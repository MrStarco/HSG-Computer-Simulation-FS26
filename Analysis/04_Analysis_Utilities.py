"""
Group 5 – Misconduct ABM | Analysis Utilities
=============================================

Helper functions shared by the Jupyter notebook.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path


# -----------------------------------------------------------------------------
# CSV loading
# -----------------------------------------------------------------------------

def load_behaviorspace_csv(path: str | Path) -> pd.DataFrame:
    """Load a NetLogo BehaviorSpace table-output CSV.

    NetLogo prepends 6 metadata rows before the real header; we skip them.
    Column names are sanitised to snake_case for convenience.
    """
    df = pd.read_csv(path, skiprows=6)
    df.columns = [
        c.strip().replace(" ", "_").replace("-", "_").replace("[", "").replace("]", "")
        for c in df.columns
    ]
    # NetLogo stores the run index under "[run number]" -> "run_number"
    if "run_number" not in df.columns and "X.run.number." in df.columns:
        df = df.rename(columns={"X.run.number.": "run_number"})
    return df


# -----------------------------------------------------------------------------
# Steady-state aggregation
# -----------------------------------------------------------------------------

def steady_state_mean(df: pd.DataFrame,
                      group_keys: list[str],
                      metric_cols: list[str],
                      tick_col: str = "step",
                      window_start: int = 300,
                      window_end: int = 500) -> pd.DataFrame:
    """Return the per-run mean of each metric over the steady-state window.

    Parameters
    ----------
    df : long-format dataframe with one row per (run, tick)
    group_keys : columns that identify an individual run
        (typically ['run_number'] plus the varied IVs).
    metric_cols : DV columns to average.
    tick_col : name of the tick column ('step' in recent NetLogo, sometimes
        't' or 'ticks').
    window_start, window_end : inclusive tick bounds of the steady-state window.
    """
    tcol = tick_col if tick_col in df.columns else (
        "ticks" if "ticks" in df.columns else "step"
    )
    mask = (df[tcol] >= window_start) & (df[tcol] <= window_end)
    sub = df.loc[mask].copy()
    agg = sub.groupby(group_keys)[metric_cols].mean().reset_index()
    return agg


def steady_state_std(df: pd.DataFrame,
                     group_keys: list[str],
                     metric_cols: list[str],
                     tick_col: str = "step",
                     window_start: int = 300,
                     window_end: int = 500) -> pd.DataFrame:
    """Per-run std over the steady-state window.  Used for volatility DVs."""
    tcol = tick_col if tick_col in df.columns else (
        "ticks" if "ticks" in df.columns else "step"
    )
    mask = (df[tcol] >= window_start) & (df[tcol] <= window_end)
    sub = df.loc[mask].copy()
    agg = sub.groupby(group_keys)[metric_cols].std().reset_index()
    return agg


def final_snapshot(df: pd.DataFrame,
                   group_keys: list[str],
                   metric_cols: list[str],
                   tick_col: str = "step") -> pd.DataFrame:
    """Return the metric values at the last tick of each run."""
    tcol = tick_col if tick_col in df.columns else (
        "ticks" if "ticks" in df.columns else "step"
    )
    idx = df.groupby(group_keys)[tcol].idxmax()
    return df.loc[idx, group_keys + metric_cols].reset_index(drop=True)


# -----------------------------------------------------------------------------
# Bootstrap confidence intervals
# -----------------------------------------------------------------------------

def bootstrap_ci(values: np.ndarray,
                 n_boot: int = 10_000,
                 alpha: float = 0.05,
                 rng: np.random.Generator | None = None) -> tuple[float, float, float]:
    """Return (mean, lower, upper) of a basic percentile bootstrap CI."""
    v = np.asarray(values, dtype=float)
    v = v[~np.isnan(v)]
    if len(v) == 0:
        return (np.nan, np.nan, np.nan)
    rng = rng or np.random.default_rng(42)
    means = np.empty(n_boot)
    n = len(v)
    for i in range(n_boot):
        sample = rng.choice(v, size=n, replace=True)
        means[i] = sample.mean()
    lo = np.quantile(means, alpha / 2)
    hi = np.quantile(means, 1 - alpha / 2)
    return (float(v.mean()), float(lo), float(hi))


def cell_means_with_ci(df: pd.DataFrame,
                       cell_keys: list[str],
                       metric: str,
                       n_boot: int = 2_000) -> pd.DataFrame:
    """Group by cell_keys and return mean + 95% bootstrap CI for *metric*."""
    rows = []
    rng = np.random.default_rng(2026)
    for key_values, sub in df.groupby(cell_keys):
        if not isinstance(key_values, tuple):
            key_values = (key_values,)
        m, lo, hi = bootstrap_ci(sub[metric].values, n_boot=n_boot, rng=rng)
        row = dict(zip(cell_keys, key_values))
        row[f"{metric}_mean"] = m
        row[f"{metric}_ci_lo"] = lo
        row[f"{metric}_ci_hi"] = hi
        row["n"] = len(sub)
        rows.append(row)
    return pd.DataFrame(rows)


# -----------------------------------------------------------------------------
# Derived DVs
# -----------------------------------------------------------------------------

def add_derived_rates(df: pd.DataFrame, n_employees_col: str = "number_employees") -> pd.DataFrame:
    """Add per-capita rate columns.

    The raw NetLogo counts are absolute per tick.  Rates make policies
    comparable across different organisation sizes (relevant for Exp B/D).
    """
    df = df.copy()
    n = df[n_employees_col] if n_employees_col in df.columns else 150
    if "true_misconduct_this_tick" in df.columns:
        df["true_misconduct_rate"] = df["true_misconduct_this_tick"] / n
    if "retaliation_events_this_tick" in df.columns:
        df["retaliation_rate"] = df["retaliation_events_this_tick"] / n
    if "sanctioned_this_tick" in df.columns:
        df["sanctioned_rate"] = df["sanctioned_this_tick"] / n
    if ("reported_events_this_tick" in df.columns
            and "true_misconduct_this_tick" in df.columns):
        df["reporting_yield"] = np.where(
            df["true_misconduct_this_tick"] > 0,
            df["reported_events_this_tick"] / df["true_misconduct_this_tick"],
            np.nan,
        )
    return df

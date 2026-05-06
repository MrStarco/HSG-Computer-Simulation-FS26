"""
analyze_all_experiments.py
--------------------------
Run this file in Spyder to produce all plots for the Group 5 misconduct ABM.

SETUP: edit the two lines in the CONFIG section below, then run the whole file
       (F5 in Spyder, or Run > Run File).

Plots are saved as PNG files in the "Sample plots" subfolder.
"""

# =============================================================================
# CONFIG  –  Paths to CSV and plot folders
# =============================================================================

import pathlib
CSV_FOLDER = pathlib.Path(__file__).parent


# PREFIX prepended to each CSV basename below. Leave empty so names match exactly,
# e.g. exp1_policy_grid-table.csv (no NetLogo model-name prefix).
#
# NetLogo BehaviorSpace (run options): enable only "Table output" / Ausgabe in Tabelle.
# The script looks for CSVs first in ./tables, then in the experiment root folder.
# Use one distinct output file path per experiment.
# Do not use Spreadsheet output for this workflow; turning off view/plot updates speeds runs.
PREFIX = ""

# =============================================================================
# END OF CONFIG  –  nothing below needs to change
# =============================================================================

from pathlib import Path
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

CSV_FOLDER = Path(CSV_FOLDER)
TABLE_FOLDER = CSV_FOLDER / "tables"
PLOT_FOLDER = CSV_FOLDER / "Sample plots"
TABLE_FOLDER.mkdir(parents=True, exist_ok=True)
PLOT_FOLDER.mkdir(parents=True, exist_ok=True)


def _resolve_csv_path(filename):
    """Resolve CSV path from ./tables first, fallback to experiment root."""
    p_tables = TABLE_FOLDER / filename
    if p_tables.exists():
        return p_tables
    return CSV_FOLDER / filename

# Derived file paths
EXP1_CSV  = _resolve_csv_path(f"{PREFIX}exp1_policy_grid-table.csv")
EXP2_CSVS = {
    "number-employees":              _resolve_csv_path(f"{PREFIX}exp2a_sens_employees-table.csv"),
    "initial-misconduct-propensity": _resolve_csv_path(f"{PREFIX}exp2b_sens_init_propensity-table.csv"),
    "initial-fear":                  _resolve_csv_path(f"{PREFIX}exp2c_sens_init_fear-table.csv"),
    "learning-rate":             _resolve_csv_path(f"{PREFIX}exp2d_sens_response_strength-table.csv"),
    "baseline-recovery-rate":                   _resolve_csv_path(f"{PREFIX}exp2e_sens_drift_speed-table.csv"),
}


# =============================================================================
# SHARED UTILITIES
# =============================================================================

def _find_header_row(path):
    """Find the real column-header row in a BehaviorSpace Table CSV."""
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if row and row[0].strip().lower().startswith("[run number]"):
                return i
    raise ValueError(f"No '[run number]' header found in {path.name}.\n"
                     "Make sure you exported as 'Table' from BehaviorSpace.")


def load_csv(path):
    """Load a BehaviorSpace Table CSV into a DataFrame."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"\nFile not found:\n  {path}\n\n"
            "Check that CSV_FOLDER and PREFIX are set correctly at the top of this file."
        )
    header_row = _find_header_row(path)
    df = pd.read_csv(path, skiprows=header_row)

    rename = {}
    for c in df.columns:
        cl = c.strip()
        if cl.lower() == "[run number]":
            rename[c] = "run"
        elif cl.lower() == "[step]":
            rename[c] = "tick"
        else:
            rename[c] = cl
    df = df.rename(columns=rename)

    for c in df.columns:
        num = pd.to_numeric(df[c], errors="coerce")
        if num.notna().any():
            df[c] = num
    # If essential policy columns are missing, this is usually Spreadsheet layout
    # being read with the Table parser. Re-parse with the spreadsheet fallback.
    required_cols = {"run", "number-employees", "punishment-severity", "reporter-protection"}
    if not required_cols.issubset(set(df.columns)):
        return load_spreadsheet_csv(path)
    return df


def load_spreadsheet_csv(path):
    """Load BehaviorSpace Spreadsheet-style CSV and convert to run-level rows.

    Supported layout: run-level parameter rows + a '[final value]' header row with
    one subsequent values row (the usual output when runMetricsEveryStep=false).
    """
    with Path(path).open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    def _cell(x):
        return (x or "").strip()

    run_row_idx = next(
        (i for i, r in enumerate(rows) if r and _cell(r[0]).lower() == "[run number]"),
        None,
    )
    if run_row_idx is None:
        raise ValueError(
            f"No '[run number]' row found in {Path(path).name}. "
            "Please export from BehaviorSpace as 'Table' or 'Spreadsheet'."
        )

    final_header_idx = next(
        (
            i for i, r in enumerate(rows[run_row_idx + 1 :], start=run_row_idx + 1)
            if r and _cell(r[0]).lower() == "[final value]"
        ),
        None,
    )
    if final_header_idx is None:
        raise ValueError(
            f"Could not find '[final value]' header row in spreadsheet export {Path(path).name}. "
            "For this script, use run-level final-value exports."
        )

    data_row_idx = next(
        (
            i for i, r in enumerate(rows[final_header_idx + 1 :], start=final_header_idx + 1)
            if any(_cell(v) for v in r[1:])
        ),
        None,
    )
    if data_row_idx is None:
        raise ValueError(f"No data row found after '[final value]' in {Path(path).name}.")

    run_vals_raw = rows[run_row_idx][1:]
    headers_raw = rows[final_header_idx][1:]
    data_raw = rows[data_row_idx][1:]

    n_cols = min(len(run_vals_raw), len(headers_raw), len(data_raw))
    run_vals_raw = run_vals_raw[:n_cols]
    headers_raw = headers_raw[:n_cols]
    data_raw = data_raw[:n_cols]

    # Parameter rows between '[run number]' and '[final value]'.
    param_rows = []
    for r in rows[run_row_idx + 1 : final_header_idx]:
        if not r:
            continue
        name = _cell(r[0])
        if not name.startswith("["):
            vals = r[1 : 1 + n_cols]
            param_rows.append((name, vals))

    def ffill(values):
        out = []
        last = ""
        for v in values:
            s = _cell(v)
            if s != "":
                last = s
            out.append(last)
        return out

    run_vals = ffill(run_vals_raw)
    headers = [h.strip() for h in headers_raw]
    param_vals = {name: ffill(vals) for name, vals in param_rows}

    records = {}
    for i in range(n_cols):
        run_id = run_vals[i]
        if run_id == "":
            continue
        rec = records.setdefault(run_id, {"run": run_id})

        # Parameters (e.g., punishment-severity, reporter-protection, number-employees)
        for pname, pvals in param_vals.items():
            pv = pvals[i]
            if pv != "":
                rec[pname] = pv

        # Final metrics
        h = headers[i]
        v = _cell(data_raw[i])
        if h.lower() == "[step]":
            if v != "":
                rec["tick"] = v
        elif h != "" and v != "":
            rec[h] = v

    if not records:
        raise ValueError(f"Failed to parse spreadsheet-style export: {Path(path).name}")

    df = pd.DataFrame(list(records.values()))
    for c in df.columns:
        num = pd.to_numeric(df[c], errors="coerce")
        if num.notna().any():
            df[c] = num

    print(f"  Parsed spreadsheet layout: {len(df)} run rows")
    return df


def add_rates(df, ticks=300):
    """Add derived stakeholder-cost columns from cumulative totals.

    true_misconduct_rate and retaliation_rate are the share of total employees
    involved on average per tick (0.12 = 12% of employees).
    This is valid because each employee can commit / experience at most one
    misconduct or retaliation event per tick, so events-per-tick / N equals
    the fraction of the workforce involved.
    """
    out = df.copy()
    n = out["number-employees"]
    t = ticks if isinstance(ticks, (int, float)) else out[ticks].clip(lower=1)
    out["true_misconduct_rate"] = out["committed-misconduct-total"] / (t * n)
    out["retaliation_rate"]     = out["retaliation-events-total"] / (t * n)
    out["reporting_rate"]       = np.where(
        out["committed-misconduct-total"] > 0,
        out["reported-events-total"] / out["committed-misconduct-total"],
        np.nan,
    )
    out["mean_fear"]       = out["mean [fear] of employees"]
    out["mean_propensity"] = out["mean [misconduct-propensity] of employees"]
    return out


def pareto_front(points):
    """Boolean mask: True = non-dominated (both axes minimised)."""
    pts = np.asarray(points, dtype=float)
    keep = np.ones(len(pts), dtype=bool)
    for i in range(len(pts)):
        if not keep[i]:
            continue
        dominated = np.all(pts <= pts[i], axis=1) & np.any(pts < pts[i], axis=1)
        if dominated.any():
            keep[i] = False
    return keep


def set_style():
    plt.rcParams.update({
        "figure.dpi": 110, "savefig.dpi": 200, "savefig.bbox": "tight",
        "font.size": 10.5, "axes.titlesize": 12, "axes.titleweight": "bold",
        "axes.labelsize": 10.5, "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.25, "grid.linewidth": 0.6,
        "legend.frameon": False, "legend.fontsize": 9,
    })


# =============================================================================
# EXPERIMENT 1  –  Policy grid: heatmaps + mechanism + Pareto + archetypes
# =============================================================================

# Single colormap used for ALL four heatmap panels.
# RdYlGn_r: green = low = good outcome, yellow = middle, red = high = bad outcome.
# Lower is always better for every metric, so the colour direction is consistent.
HEATMAP_CMAP = "RdYlGn_r"

# Four archetypal policies derived from the corners of the 0.20–0.80 grid.
# Each tuple: (punishment-severity, reporter-protection, short label, description)
ARCHETYPES = [
    (0.35, 0.35, "Status Quo",
     "P=0.35 / R=0.35\\nModerate deterrence, moderate protection"),
    (0.65, 0.35, "Iron Fist",
     "P=0.65 / R=0.35\\nHigher punishment, lower protection"),
    (0.35, 0.65, "Safe Harbor",
     "P=0.35 / R=0.65\\nHigher protection, lower deterrence"),
    (0.65, 0.65, "Rule of Law",
     "P=0.65 / R=0.65\\nStronger deterrence + stronger protection"),
]

# Colours assigned to each archetype (consistent across all plots)
ARCHETYPE_COLORS = ["#555555", "#d62728", "#1f77b4", "#2ca02c"]


def run_exp1():
    print("\n--- Experiment 1: Policy Grid ---")
    print(f"Loading {EXP1_CSV.name} ...")
    df = load_csv(EXP1_CSV)
    print(f"  {len(df):,} rows, {df['run'].nunique()} runs")

    df = add_rates(df, ticks=300)

    _plot_exp1_heatmaps(df)
    _plot_exp1_mechanism(df)
    _plot_exp1_pareto(df)
    _plot_exp1_archetypes(df)


def _plot_exp1_heatmaps(df):
    """2×2 heatmaps of policy outcomes across the punishment × protection grid."""
    # (column, panel title, colorbar label)
    DVS = [
        ("true_misconduct_rate",
         "Share of employees committing misconduct",
         "share of employees (avg per tick)"),
        ("hidden-misconduct-rate",
         "Hidden misconduct rate",
         "share of misconduct undetected"),
        ("retaliation_rate",
         "Share of employees experiencing retaliation",
         "share of employees (avg per tick)"),
        ("mean_fear",
         "Mean fear",
         "avg fear level (0\u20131)"),
    ]

    grp   = df.groupby(["punishment-severity", "reporter-protection"])
    means = grp[[d[0] for d in DVS]].mean().reset_index()
    stds  = grp[[d[0] for d in DVS]].std().reset_index()
    for col, *_ in DVS:
        means[f"{col}_std"] = stds[col]

    fig, axes = plt.subplots(2, 2, figsize=(14.5, 11.8))
    fig.suptitle(
        "Experiment 1 \u2013 Policy outcomes across the punishment \u00d7 protection grid\n"
        "(each cell = mean over 10 replications, 300 ticks; "
        "green = better outcome, red = worse outcome)",
        fontsize=13, y=0.999,
    )

    for ax, (col, title, cbar_label) in zip(axes.flat, DVS):
        pivot = means.pivot(index="reporter-protection",
                            columns="punishment-severity", values=col)
        x, y, Z = pivot.columns.values, pivot.index.values, pivot.values

        im = ax.imshow(
            Z, origin="lower", aspect="auto", cmap=HEATMAP_CMAP,
            extent=[x.min()-0.025, x.max()+0.025,
                    y.min()-0.025, y.max()+0.025],
        )
        ax.set_title(title, pad=8)
        ax.set_xlabel("punishment-severity")
        ax.set_ylabel("reporter-protection")
        ax.set_xticks(x)
        ax.set_yticks(y)
        ax.set_xticklabels([f"{v:.2f}" for v in x], fontsize=7)
        ax.set_yticklabels([f"{v:.2f}" for v in y], fontsize=7)
        ax.tick_params(labelsize=7)
        ax.grid(False)

        # Mark the four archetypes with a white square outline
        for P_val, R_val, label, _ in ARCHETYPES:
            ax.plot(P_val, R_val, marker="s", markersize=14,
                    color="none", markeredgecolor="white",
                    markeredgewidth=1.8, zorder=5)

        # Cell value annotations for all policy steps (0.20–0.80, step 0.05)
        for i, yy in enumerate(y):
            for j, xx in enumerate(x):
                v = Z[i, j]
                if not np.isnan(v):
                    ax.text(xx, yy, f"{v:.2f}", ha="center", va="center",
                            fontsize=4.6, color="black")

        cb = ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
        cb.set_label(cbar_label, fontsize=9)
        cb.ax.tick_params(labelsize=8)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    out = PLOT_FOLDER / "exp1_heatmaps.png"
    fig.savefig(out); print(f"  Saved: {out.name}")
    plt.show()


def _plot_exp1_mechanism(df):
    """Mechanism plot: how punishment interacts with protection level."""
    grp   = df.groupby(["punishment-severity", "reporter-protection"])
    means = grp[["true_misconduct_rate", "hidden-misconduct-rate",
                 "retaliation_rate"]].mean().reset_index()
    stds  = grp[["true_misconduct_rate", "hidden-misconduct-rate",
                 "retaliation_rate"]].std().reset_index()
    for col in ["true_misconduct_rate", "hidden-misconduct-rate", "retaliation_rate"]:
        means[f"{col}_std"] = stds[col]

    chosen_R = sorted(np.round(means["reporter-protection"].dropna().unique(), 2))
    sub = means[means["reporter-protection"].round(2).isin(chosen_R)].copy()
    sub["reporter-protection"] = sub["reporter-protection"].round(2)
    x_levels = sorted(np.round(means["punishment-severity"].dropna().unique(), 2))

    fig, axes = plt.subplots(1, 2, figsize=(14.8, 5.8), sharex=True)
    fig.suptitle(
        "Experiment 1 \u2013 When does punishment work? (Mechanism plot)\n"
        "Downward slope = punishment reduces misconduct.  "
        "Flat / upward = fear trap (misconduct goes underground).",
        fontsize=12, y=1.02,
    )
    cmap_mech = plt.get_cmap("viridis")
    panels = [
        ("true_misconduct_rate",
         "Share of employees committing misconduct (avg per tick)"),
        ("hidden-misconduct-rate",
         "Hidden misconduct rate (share of true misconduct undetected)"),
    ]
    legend_handles = []
    legend_labels = []
    for panel_idx, (ax, (col, ylab)) in enumerate(zip(axes, panels)):
        for k, R in enumerate(chosen_R):
            s   = sub[sub["reporter-protection"] == R].sort_values("punishment-severity")
            x   = s["punishment-severity"].values
            y   = s[col].values
            err = s[f"{col}_std"].values if f"{col}_std" in s.columns else np.zeros_like(y)
            colour = cmap_mech(k / max(len(chosen_R) - 1, 1))
            line, = ax.plot(x, y, marker="o", markersize=3.2, color=colour,
                            label=f"R = {R:.2f}", linewidth=1.6)
            ax.fill_between(x, y - err, y + err,
                            color=colour, alpha=0.08, linewidth=0)
            if panel_idx == 0:
                legend_handles.append(line)
                legend_labels.append(f"R = {R:.2f}")
        ax.set_xlabel("punishment-severity")
        ax.set_ylabel(ylab)
        ax.set_xticks(x_levels)
        ax.set_xticklabels([f"{v:.2f}" for v in x_levels], fontsize=8)

    fig.legend(
        legend_handles, legend_labels, title="reporter-protection",
        loc="lower center", ncol=7, bbox_to_anchor=(0.5, -0.03), fontsize=8
    )
    plt.tight_layout(rect=[0, 0.07, 1, 1])
    out = PLOT_FOLDER / "exp1_mechanism.png"
    fig.savefig(out); print(f"  Saved: {out.name}")
    plt.show()


def _plot_exp1_pareto(df):
    """Pareto scatter close to former exp2_pareto, now from exp1 grid data."""
    cells = (
        df.groupby(["punishment-severity", "reporter-protection"])[
            ["true_misconduct_rate", "retaliation_rate", "hidden-misconduct-rate"]
        ]
        .mean()
        .reset_index()
    )
    print(f"  Pareto aggregation: {len(cells)} policy cells")

    P = cells["punishment-severity"].values
    R = cells["reporter-protection"].values
    mgmt = cells["true_misconduct_rate"].values
    emp = cells["retaliation_rate"].values
    reg = cells["hidden-misconduct-rate"].values

    fig, axes = plt.subplots(1, 2, figsize=(14.8, 6.2))
    fig.suptitle(
        "Experiment 1 – Stakeholder trade-offs across the policy grid\n"
        "(mean over 10 reps, 300 ticks; "
        "size = punishment-severity, colour = reporter-protection; "
        "black edge = Pareto-optimal)",
        fontsize=12, y=1.02,
    )

    level_vals = np.round(np.arange(0.20, 0.801, 0.05), 2)

    def scatter_pareto(ax, x, y, xlab, ylab, title):
        sizes = 60 + 280 * P
        sc = ax.scatter(
            x, y, c=R, s=sizes, cmap="viridis", vmin=0.20, vmax=0.80,
            edgecolors="white", linewidths=0.6, alpha=0.9
        )
        # Draw one progression line per reporter-protection level.
        for r in level_vals:
            rows = cells[np.isclose(cells["reporter-protection"], r, atol=1e-6)].sort_values("punishment-severity")
            if len(rows) > 1:
                if np.array_equal(x, emp):
                    xx = rows["retaliation_rate"].values
                else:
                    xx = rows["hidden-misconduct-rate"].values
                yy = rows["true_misconduct_rate"].values
                c = plt.get_cmap("viridis")((r - 0.20) / (0.80 - 0.20))
                ax.plot(xx, yy, color=c, linewidth=0.8, alpha=0.35, zorder=1)

        mask = pareto_front(np.column_stack([x, y]))
        ax.scatter(
            x[mask], y[mask], c=R[mask], s=sizes[mask], cmap="viridis",
            vmin=0.20, vmax=0.80, edgecolors="black", linewidths=1.6,
            alpha=1.0, zorder=5
        )
        order = np.argsort(x[mask])
        ax.plot(
            x[mask][order], y[mask][order],
            color="black", linewidth=0.9, linestyle="--", alpha=0.55, zorder=4
        )
        ax.set_xlabel(xlab)
        ax.set_ylabel(ylab)
        ax.set_title(title, pad=8)
        return sc

    sc = scatter_pareto(
        axes[0], emp, mgmt,
        "Share of employees experiencing retaliation →",
        "Share of employees committing misconduct →",
        "Management vs employee stakeholders",
    )
    scatter_pareto(
        axes[1], reg, mgmt,
        "Hidden misconduct rate (share undetected) →",
        "Share of employees committing misconduct →",
        "Management vs regulator stakeholders",
    )

    cbar = fig.colorbar(sc, ax=axes, fraction=0.025, pad=0.03)
    cbar.set_label("reporter-protection")
    cbar.set_ticks(level_vals)
    cbar.set_ticklabels([f"{v:.2f}" for v in level_vals])
    size_handles = [
        Line2D(
            [0], [0], marker="o", linestyle="", markerfacecolor="lightgrey",
            markeredgecolor="grey", markersize=np.sqrt(60 + 280 * p),
            label=f"P = {p:.2f}"
        )
        for p in level_vals
    ]
    axes[0].legend(
        handles=size_handles, title="punishment-severity",
        loc="upper left", labelspacing=0.6, borderpad=0.6, ncol=2, fontsize=7.5
    )

    out = PLOT_FOLDER / "exp2_pareto.png"
    fig.savefig(out); print(f"  Saved: {out.name}")
    plt.show()


def _plot_exp1_archetypes(df):
    """Archetypal policy comparison: 3 panels × 4 archetypes (static, end-of-run).

    Uses cumulative end-of-run metrics from experiment 1 (no per-tick data needed).
    Each panel shows one outcome share; the four archetypal policies are compared
    side-by-side as horizontal bars with ±1 std error bars.
    """
    panels = [
        ("true_misconduct_rate",
         "Share of employees committing misconduct",
         "share of employees"),
        ("retaliation_rate",
         "Share of employees experiencing retaliation",
         "share of employees"),
        ("hidden-misconduct-rate",
         "Hidden misconduct rate",
         "Hidden misconduct rate"),
    ]

    # Aggregate per archetype
    archetype_data = []
    for P_val, R_val, label, desc in ARCHETYPES:
        rows = df[
            (df["punishment-severity"].sub(P_val).abs() < 0.001) &
            (df["reporter-protection"].sub(R_val).abs() < 0.001)
        ]
        if rows.empty:
            print(f"  Warning: archetype {label} has no matching rows (P={P_val}, R={R_val})")
        entry = {"label": label, "desc": desc}
        for col, *_ in panels:
            entry[col]             = rows[col].mean() if not rows.empty else np.nan
            entry[f"{col}_std"]    = rows[col].std()  if not rows.empty else np.nan
        archetype_data.append(entry)

    labels = [d["label"] for d in archetype_data]
    x      = np.arange(len(labels))

    fig, axes = plt.subplots(1, 3, figsize=(14.0, 5.5), sharey=False)
    fig.suptitle(
        "Experiment 1 \u2013 Archetypal policy comparison (end-of-run steady state)\n"
        "(mean \u00b1 1 std over 10 replications, 300 ticks; "
        "punishment \u00d7 protection grid 0.20\u20130.80)",
        fontsize=12, y=1.01,
    )

    for ax, (col, title, ylab) in zip(axes, panels):
        means = np.array([d[col]          for d in archetype_data])
        stds  = np.array([d[f"{col}_std"] for d in archetype_data])
        std_scale = np.nanmax(stds) if not np.all(np.isnan(stds)) else 0.0

        # Horizontal bar chart, one bar per archetype
        ax.barh(
            x, means, xerr=stds, color=ARCHETYPE_COLORS, alpha=0.82,
            error_kw=dict(ecolor="0.3", capsize=4, linewidth=1.2), height=0.55
        )

        # Value annotation inside / beside bar
        for i, (m, s) in enumerate(zip(means, stds)):
            if not np.isnan(m):
                offset = 0.01 if std_scale == 0 else std_scale * 0.05
                ax.text(m + offset, i, f"{m:.3f}",
                        va="center", ha="left", fontsize=9, color="0.2")

        ax.set_yticks(x)
        ax.set_yticklabels(labels, fontsize=10)
        ax.set_xlabel(ylab, fontsize=9.5)
        ax.set_title(title, pad=8)
        ax.set_xlim(left=0)
        ax.invert_yaxis()   # top = first archetype

    # Shared legend mapping colour → archetype + description
    legend_handles = [
        Line2D([0], [0], marker="s", linestyle="", markersize=10,
               color=c, label=f"{d['label']}\n{d['desc'].split(chr(10))[0]}")
        for d, c in zip(archetype_data, ARCHETYPE_COLORS)
    ]
    fig.legend(
        handles=legend_handles,
        title="Archetypal policies",
        loc="lower center",
        ncol=4,
        bbox_to_anchor=(0.5, -0.18),
        frameon=True,
        framealpha=0.9,
        fontsize=8.5,
        title_fontsize=10,
    )

    plt.tight_layout()
    out = PLOT_FOLDER / "exp1_archetypes.png"
    fig.savefig(out, bbox_inches="tight"); print(f"  Saved: {out.name}")
    plt.show()


# =============================================================================
# EXPERIMENT 2  –  Sensitivity small-multiples (OFAT), formerly Experiment 3
# =============================================================================

EXP2_PARAMS = [
    ("number-employees",              "number-employees",               300),
    ("initial-misconduct-propensity", "initial-misconduct-propensity",  0.40),
    ("initial-fear",                  "initial-fear",                   0.30),
    ("learning-rate",             "learning-rate",              0.20),
    ("baseline-recovery-rate",                   "baseline-recovery-rate",                    0.05),
]

EXP2_DVS = [
    # (column, row label, unit note)
    ("true_misconduct_rate",
     "Share of employees\ncommitting misconduct",
     "share of employees"),
    ("hidden-misconduct-rate",
     "Hidden misconduct rate",
     "share undetected"),
    ("retaliation_rate",
     "Share of employees\nexperiencing retaliation",
     "share of employees"),
    ("mean_fear",
     "Mean fear",
     "avg fear level"),
]


def run_exp2():
    print("\n--- Experiment 2: Sensitivity Analysis ---")

    agg = {}
    for col, label, baseline in EXP2_PARAMS:
        csv_path = EXP2_CSVS[col]
        print(f"  Loading {csv_path.name} ...")
        df = load_csv(csv_path)
        df = add_rates(df, ticks=300)
        df["mean_fear"] = df["mean [fear] of employees"]
        dv_cols = [d[0] for d in EXP2_DVS]
        grp   = df.groupby(col)[dv_cols]
        means = grp.mean()
        stds  = grp.std()
        out   = means.copy()
        for c in dv_cols:
            out[f"{c}_std"] = stds[c]
        agg[col] = out.reset_index().sort_values(col)
        print(f"    {len(agg[col])} parameter levels")

    n_rows, n_cols = len(EXP2_DVS), len(EXP2_PARAMS)
    fig, axes = plt.subplots(
        n_rows, n_cols,
        figsize=(3.2 * n_cols, 2.6 * n_rows),
        sharex=False, sharey="row",
    )
    fig.suptitle(
        "Experiment 2 \u2013 Sensitivity of outcomes to otherwise-fixed parameters\n"
        "(OFAT around baseline P=0.50, R=0.30; mean \u00b11 std over 10 reps, 300 ticks; "
        "dashed line = default value)",
        fontsize=13, y=0.999,
    )
    cmap_tab = plt.get_cmap("tab10")

    for r, (dv, ylab, _unit) in enumerate(EXP2_DVS):
        for c, (pcol, plab, baseline) in enumerate(EXP2_PARAMS):
            ax     = axes[r, c]
            df_p   = agg[pcol]
            x      = df_p[pcol].values
            y      = df_p[dv].values
            s      = df_p[f"{dv}_std"].values
            colour = cmap_tab(r)

            ax.plot(x, y, marker="o", color=colour, linewidth=1.8, markersize=4)
            ax.fill_between(x, y - s, y + s, color=colour, alpha=0.18, linewidth=0)
            ax.axvline(baseline, color="0.4", linestyle="--",
                       linewidth=0.9, alpha=0.8)

            if r == 0:
                ax.set_title(plab, fontsize=10)
            if r == n_rows - 1:
                ax.set_xlabel(plab, fontsize=9)
            if c == 0:
                ax.set_ylabel(ylab, fontsize=9.5)
            ax.tick_params(labelsize=8)

    plt.tight_layout(rect=[0, 0, 1, 0.962])
    out = PLOT_FOLDER / "exp2_sensitivity.png"
    fig.savefig(out); print(f"  Saved: {out.name}")
    plt.show()


# =============================================================================
# MAIN
# =============================================================================

set_style()

RUN_EXP1 = True   # set to False to skip
RUN_EXP2 = True

if RUN_EXP1:
    run_exp1()

if RUN_EXP2:
    run_exp2()

print("\nDone. All plots saved to:", PLOT_FOLDER)

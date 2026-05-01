"""
analyze_all_experiments.py
--------------------------
Run this file in Spyder to produce all plots for the Group 5 misconduct ABM.

SETUP: edit the two lines in the CONFIG section below, then run the whole file
       (F5 in Spyder, or Run > Run File).

Plots are saved as PNG files in the same folder as the CSV files.
"""

# =============================================================================
# CONFIG  –  edit these two lines, then run the file
# =============================================================================

# Folder where your NetLogo CSV exports live.
CSV_FOLDER = r"/Users/...."

# Prefix that NetLogo put in front of every filename.
# NetLogo names files like:  <PREFIX> <experiment-name>-table.csv
PREFIX = "Group5_Misconduct_ABM_EXPERIMENTS_V1 "

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

# Derived file paths
EXP1_CSV  = CSV_FOLDER / f"{PREFIX}exp1_policy_grid-table.csv"
EXP2_CSV  = CSV_FOLDER / f"{PREFIX}exp2_stakeholder_pareto-table.csv"
EXP3_CSVS = {
    "number-employees":              CSV_FOLDER / f"{PREFIX}exp3a_sens_employees-table.csv",
    "initial-misconduct-propensity": CSV_FOLDER / f"{PREFIX}exp3b_sens_init_propensity-table.csv",
    "initial-fear":                  CSV_FOLDER / f"{PREFIX}exp3c_sens_init_fear-table.csv",
    "response-strength":             CSV_FOLDER / f"{PREFIX}exp3d_sens_response_strength-table.csv",
    "drift-speed":                   CSV_FOLDER / f"{PREFIX}exp3e_sens_drift_speed-table.csv",
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
        if df[c].dtype == object:
            df[c] = pd.to_numeric(df[c], errors="ignore")
    return df


def add_rates(df, ticks=300):
    """Add derived stakeholder-cost columns.

    true_misconduct_rate and retaliation_rate are the share of total employees
    involved on average per tick (0.12 = 12% of employees).
    This is valid because each employee can commit / experience at most one
    misconduct or retaliation event per tick, so events-per-tick / N equals
    the fraction of the workforce involved.
    """
    out = df.copy()
    n = out["number-employees"]
    t = ticks if isinstance(ticks, (int, float)) else out[ticks].clip(lower=1)
    out["true_misconduct_rate"] = out["true-misconduct-total"] / (t * n)
    out["retaliation_rate"]     = out["retaliation-events-total"] / (t * n)
    out["reporting_rate"]       = np.where(
        out["true-misconduct-total"] > 0,
        out["reported-events-total"] / out["true-misconduct-total"],
        np.nan,
    )
    out["mean_fear"]       = out["mean [fear] of employees"]
    out["mean_propensity"] = out["mean [misconduct-propensity] of employees"]
    return out


def pareto_front(points):
    """Boolean mask: True = non-dominated (both axes minimised)."""
    pts  = np.asarray(points, dtype=float)
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
# EXPERIMENT 1  –  Policy grid: heatmaps + mechanism plot
# =============================================================================

# Single colormap used for ALL four heatmap panels.
# RdYlGn_r: green = low = good outcome, yellow = middle, red = high = bad outcome.
# Lower is always better for every metric, so the colour direction is consistent.
HEATMAP_CMAP = "RdYlGn_r"


def run_exp1():
    print("\n--- Experiment 1: Policy Grid ---")
    print(f"Loading {EXP1_CSV.name} ...")
    df = load_csv(EXP1_CSV)
    print(f"  {len(df):,} rows, {df['run'].nunique()} runs")

    df = add_rates(df, ticks=300)

    # (column, panel title, colorbar label)
    # true_misconduct_rate and retaliation_rate are shares of employees (0-1),
    # e.g. 0.12 means 12% of employees on average per tick.
    DVS = [
        ("true_misconduct_rate",
         "Management cost\n(share of employees committing misconduct)",
         "share of employees (avg per tick)"),
        ("hidden-misconduct-rate",
         "Regulator cost\n(hidden misconduct rate)",
         "share of misconduct undetected"),
        ("retaliation_rate",
         "Employee cost\n(share of employees experiencing retaliation)",
         "share of employees (avg per tick)"),
        ("mean_fear",
         "Organisational climate\n(mean fear)",
         "avg fear level (0\u20131)"),
    ]

    grp   = df.groupby(["punishment-value", "reporter-protection"])
    means = grp[[d[0] for d in DVS]].mean().reset_index()
    stds  = grp[[d[0] for d in DVS]].std().reset_index()
    for col, *_ in DVS:
        means[f"{col}_std"] = stds[col]

    # --- Plot 1a: 2x2 heatmaps with unified green-yellow-red colormap ---
    fig, axes = plt.subplots(2, 2, figsize=(12.5, 10.5))
    fig.suptitle(
        "Experiment 1 \u2013 Policy outcomes across the punishment \u00d7 protection grid\n"
        "(each cell = mean over 10 replications, 300 ticks; "
        "green = better outcome, red = worse outcome)",
        fontsize=13, y=0.999,
    )

    for ax, (col, title, cbar_label) in zip(axes.flat, DVS):
        pivot = means.pivot(index="reporter-protection",
                            columns="punishment-value", values=col)
        x, y, Z = pivot.columns.values, pivot.index.values, pivot.values

        im = ax.imshow(
            Z, origin="lower", aspect="auto", cmap=HEATMAP_CMAP,
            extent=[x.min()-0.05, x.max()+0.05,
                    y.min()-0.05, y.max()+0.05],
        )
        ax.set_title(title, pad=8)
        ax.set_xlabel("punishment-value")
        ax.set_ylabel("reporter-protection")
        ax.set_xticks(x); ax.set_yticks(y)
        ax.tick_params(labelsize=8); ax.grid(False)

        # Black text reads well on all shades of RdYlGn_r (green, yellow, red)
        for i, yy in enumerate(y):
            for j, xx in enumerate(x):
                v = Z[i, j]
                if not np.isnan(v):
                    ax.text(xx, yy, f"{v:.2f}", ha="center", va="center",
                            fontsize=6.5, color="black")

        cb = ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
        cb.set_label(cbar_label, fontsize=9)
        cb.ax.tick_params(labelsize=8)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    out1a = CSV_FOLDER / "exp1_heatmaps.png"
    fig.savefig(out1a); print(f"  Saved: {out1a.name}")
    plt.show()

    # --- Plot 1b: mechanism plot (answers the RQ) ---
    # chosen_R must use values that exist in the 0.0-1.0 / step-0.1 grid.
    # 0.25 and 0.75 are NOT in that grid, which is why only 3 lines appeared
    # before. Using 0.0, 0.3, 0.5, 0.7, 1.0 gives all five lines.
    chosen_R = [0.0, 0.3, 0.5, 0.7, 1.0]
    sub = means[means["reporter-protection"].round(2).isin(chosen_R)].copy()
    sub["reporter-protection"] = sub["reporter-protection"].round(2)

    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.4), sharex=True)
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
    for ax, (col, ylab) in zip(axes, panels):
        for k, R in enumerate(chosen_R):
            s   = sub[sub["reporter-protection"] == R].sort_values("punishment-value")
            x   = s["punishment-value"].values
            y   = s[col].values
            err = s[f"{col}_std"].values if f"{col}_std" in s.columns else np.zeros_like(y)
            colour = cmap_mech(k / max(len(chosen_R) - 1, 1))
            ax.plot(x, y, marker="o", color=colour,
                    label=f"R = {R:.1f}", linewidth=2)
            ax.fill_between(x, y - err, y + err,
                            color=colour, alpha=0.13, linewidth=0)
        ax.set_xlabel("punishment-value")
        ax.set_ylabel(ylab)
        ax.legend(title="reporter-protection", loc="best")

    plt.tight_layout()
    out1b = CSV_FOLDER / "exp1_mechanism.png"
    fig.savefig(out1b); print(f"  Saved: {out1b.name}")
    plt.show()


# =============================================================================
# EXPERIMENT 2  –  Pareto scatter + dynamics
# =============================================================================

STEADY_TICKS = 100   # last N ticks used for steady-state average

ARCHETYPES = [
    (0.0, 0.0, "Punishment=0.0 / Protection=0.0", "weak deterrence, exposed reporters"),
    (0.8, 0.0, "Punishment=0.8 / Protection=0.0", "harsh punishment without protection: fear trap"),
    (0.0, 0.8, "Punishment=0.0 / Protection=0.8", "safe to report but nothing to deter"),
    (0.8, 0.8, "Punishment=0.8 / Protection=0.8", "the policy sweet spot: strong & safe"),
]


def run_exp2():
    print("\n--- Experiment 2: Stakeholder Pareto + Dynamics ---")
    print(f"Loading {EXP2_CSV.name} (large file, a moment please)...")
    df = load_csv(EXP2_CSV)
    print(f"  {len(df):,} rows, {df['run'].nunique()} runs, "
          f"{df['tick'].max()} ticks/run")

    # Steady-state: average per-tick columns over the last STEADY_TICKS ticks.
    # Dividing by N gives the share of employees on that tick, then we average
    # across the steady-state window and across replications.
    tmax = df["tick"].max()
    tail = df[df["tick"] > tmax - STEADY_TICKS].copy()
    n = tail["number-employees"]
    tail["true_misconduct_rate"] = tail["true-misconduct-this-tick"] / n
    tail["retaliation_rate"]     = tail["retaliation-events-this-tick"] / n
    tail["hidden_rate"]          = tail["hidden-misconduct-rate-this-tick"]

    per_run = (
        tail.groupby(["punishment-value", "reporter-protection", "run"])
            [["true_misconduct_rate", "retaliation_rate", "hidden_rate",
              "mean [fear] of employees"]]
            .mean().reset_index()
    )
    cells = (
        per_run.groupby(["punishment-value", "reporter-protection"])
               [["true_misconduct_rate", "retaliation_rate", "hidden_rate",
                 "mean [fear] of employees"]]
               .mean().reset_index()
    )
    print(f"  Aggregated into {len(cells)} policy cells")

    P    = cells["punishment-value"].values
    R    = cells["reporter-protection"].values
    mgmt = cells["true_misconduct_rate"].values   # share of employees
    emp  = cells["retaliation_rate"].values        # share of employees
    reg  = cells["hidden_rate"].values             # share undetected (unitless)

    # --- Plot 2a: 2-panel Pareto scatter ---
    fig, axes = plt.subplots(1, 2, figsize=(14.5, 6.0))
    fig.suptitle(
        "Experiment 2 \u2013 Stakeholder trade-offs across the policy grid\n"
        "(steady-state: mean over last 100 ticks, 10 reps; "
        "size = punishment-value, colour = reporter-protection; "
        "black edge = Pareto-optimal)",
        fontsize=12, y=1.02,
    )

    def scatter_pareto(ax, x, y, xlab, ylab, title):
        sizes = 60 + 280 * P
        sc = ax.scatter(x, y, c=R, s=sizes, cmap="viridis", vmin=0, vmax=1,
                        edgecolors="white", linewidths=0.6, alpha=0.9)
        mask = pareto_front(np.column_stack([x, y]))
        ax.scatter(x[mask], y[mask], c=R[mask], s=sizes[mask],
                   cmap="viridis", vmin=0, vmax=1,
                   edgecolors="black", linewidths=1.6, alpha=1.0, zorder=5)
        order = np.argsort(x[mask])
        ax.plot(x[mask][order], y[mask][order],
                color="black", linewidth=0.9, linestyle="--", alpha=0.55, zorder=4)
        ax.set_xlabel(xlab); ax.set_ylabel(ylab); ax.set_title(title, pad=8)
        return sc

    sc = scatter_pareto(
        axes[0], emp, mgmt,
        "Share of employees experiencing retaliation \u2192",
        "Share of employees committing misconduct \u2192",
        "Management vs employee stakeholders",
    )
    scatter_pareto(
        axes[1], reg, mgmt,
        "Hidden misconduct rate (share undetected) \u2192",
        "Share of employees committing misconduct \u2192",
        "Management vs regulator stakeholders",
    )

    cbar = fig.colorbar(sc, ax=axes, fraction=0.025, pad=0.03)
    cbar.set_label("reporter-protection")
    size_handles = [
        Line2D([0], [0], marker="o", linestyle="",
               markerfacecolor="lightgrey", markeredgecolor="grey",
               markersize=np.sqrt(60 + 280 * p), label=f"P = {p:.2f}")
        for p in [0.0, 0.25, 0.5, 0.75, 1.0]
    ]
    axes[0].legend(handles=size_handles, title="punishment-value",
                   loc="upper left", labelspacing=1.1, borderpad=0.8)

    out2a = CSV_FOLDER / "exp2_pareto.png"
    fig.savefig(out2a); print(f"  Saved: {out2a.name}")
    plt.show()

    # --- Plot 2b: dynamics for four archetypal policies ---
    fig, axes = plt.subplots(2, 2, figsize=(13.5, 9.0), sharex=True)
    fig.suptitle(
        "Experiment 2 \u2013 Stakeholder cost dynamics for four archetypal policies\n"
        "(mean across 10 reps, smoothed with 20-tick rolling average)",
        fontsize=12, y=0.999,
    )

    left_cols   = ["true_misconduct_rate", "retaliation_rate"]
    right_cols  = ["hidden_rate"]
    colours = {
        "true_misconduct_rate": "#1f77b4",   # blue  – left axis
        "retaliation_rate":     "#d62728",   # red   – left axis
        "hidden_rate":          "#2ca02c",   # green – right axis
    }
    dyn_labels = {
        "true_misconduct_rate": "share committing misconduct (mgmt)",
        "retaliation_rate":     "share experiencing retaliation",
        "hidden_rate":          "hidden misconduct rate (regulators)",
    }

    for ax, (P_val, R_val, title, subtitle) in zip(axes.flat, ARCHETYPES):
        ax_r = ax.twinx()   # right y-axis for hidden_rate

        rows = df[
            (df["punishment-value"].sub(P_val).abs() < 0.01) &
            (df["reporter-protection"].sub(R_val).abs() < 0.01)
        ].copy()

        if rows.empty:
            ax.text(0.5, 0.5, f"No data for P={P_val}, R={R_val}",
                    transform=ax.transAxes, ha="center", va="center")
        else:
            n_col = rows["number-employees"]
            rows["true_misconduct_rate"] = rows["true-misconduct-this-tick"] / n_col
            rows["retaliation_rate"]     = rows["retaliation-events-this-tick"] / n_col
            rows["hidden_rate"]          = rows["hidden-misconduct-rate-this-tick"]

            all_cols = left_cols + right_cols
            mean_t = rows.groupby("tick")[all_cols].mean().sort_index()
            smooth = mean_t.rolling(20, min_periods=1, center=True).mean()

            # Left axis: employee-share metrics
            for col in left_cols:
                ax.plot(smooth.index, smooth[col],
                        color=colours[col], linewidth=2.0,
                        label=dyn_labels[col])
            ax.set_ylim(bottom=0)

            # Right axis: hidden rate
            for col in right_cols:
                ax_r.plot(smooth.index, smooth[col],
                          color=colours[col], linewidth=2.0,
                          linestyle="--", label=dyn_labels[col])
            ax_r.set_ylim(0, 1)

            ax.set_xlim(0, mean_t.index.max())

        ax.set_title(f"{title}\n{subtitle}", fontsize=10)
        ax.set_xlabel("tick")
        ax.set_ylabel("share of employees", color="black")
        ax_r.set_ylabel("hidden misconduct rate", color="#2ca02c")
        ax_r.tick_params(axis="y", labelcolor="#2ca02c")
        ax_r.spines["right"].set_visible(True)

    # Build a single figure-level legend from the last panel's two axes
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax_r.get_legend_handles_labels()
    fig.legend(h1 + h2, l1 + l2, loc="lower center", ncol=3,
               bbox_to_anchor=(0.5, -0.02), frameon=False)

    plt.tight_layout(rect=[0, 0.03, 1, 0.965])
    out2b = CSV_FOLDER / "exp2_dynamics.png"
    fig.savefig(out2b); print(f"  Saved: {out2b.name}")
    plt.show()


# =============================================================================
# EXPERIMENT 3  –  Sensitivity small-multiples (OFAT)
# =============================================================================

EXP3_PARAMS = [
    # (column name,                     x-axis label,                     baseline)
    ("number-employees",              "number-employees",               200),
    ("initial-misconduct-propensity", "initial-misconduct-propensity",  0.20),
    ("initial-fear",                  "initial-fear",                   0.20),
    ("response-strength",             "response-strength",              0.33),
    ("drift-speed",                   "drift-speed",                    0.05),
]

EXP3_DVS = [
    # (column, row label, unit note)
    ("true_misconduct_rate",
     "Share of employees\ncommitting misconduct",
     "share of employees"),
    ("hidden-misconduct-rate",
     "Hidden misconduct rate\n(regulator cost)",
     "share undetected"),
    ("retaliation_rate",
     "Share of employees\nexperiencing retaliation",
     "share of employees"),
    ("mean_fear",
     "Mean fear\n(climate)",
     "avg fear level"),
]


def run_exp3():
    print("\n--- Experiment 3: Sensitivity Analysis ---")

    agg = {}
    for col, label, baseline in EXP3_PARAMS:
        csv_path = EXP3_CSVS[col]
        print(f"  Loading {csv_path.name} ...")
        df = load_csv(csv_path)
        df = add_rates(df, ticks=300)
        df["mean_fear"] = df["mean [fear] of employees"]
        dv_cols = [d[0] for d in EXP3_DVS]
        grp   = df.groupby(col)[dv_cols]
        means = grp.mean()
        stds  = grp.std()
        out   = means.copy()
        for c in dv_cols:
            out[f"{c}_std"] = stds[c]
        agg[col] = out.reset_index().sort_values(col)
        print(f"    {len(agg[col])} parameter levels")

    n_rows, n_cols = len(EXP3_DVS), len(EXP3_PARAMS)
    fig, axes = plt.subplots(
        n_rows, n_cols,
        figsize=(3.2 * n_cols, 2.6 * n_rows),
        sharex=False, sharey="row",
    )
    fig.suptitle(
        "Experiment 3 \u2013 Sensitivity of outcomes to otherwise-fixed parameters\n"
        "(OFAT around baseline P=0.66, R=0.50; mean \u00b11 std over 10 reps, 300 ticks; "
        "dashed line = default value)",
        fontsize=13, y=0.999,
    )
    cmap_tab = plt.get_cmap("tab10")

    for r, (dv, ylab, _unit) in enumerate(EXP3_DVS):
        for c, (pcol, plab, baseline) in enumerate(EXP3_PARAMS):
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
    out3 = CSV_FOLDER / "exp3_sensitivity.png"
    fig.savefig(out3); print(f"  Saved: {out3.name}")
    plt.show()


# =============================================================================
# MAIN
# =============================================================================

set_style()

RUN_EXP1 = True   # set to False to skip
RUN_EXP2 = True
RUN_EXP3 = True

if RUN_EXP1:
    run_exp1()

if RUN_EXP2:
    run_exp2()

if RUN_EXP3:
    run_exp3()

print("\nDone. All plots saved to:", CSV_FOLDER)

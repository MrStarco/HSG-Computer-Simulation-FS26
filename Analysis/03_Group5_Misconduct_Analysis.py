# -*- coding: utf-8 -*-
"""
Group 5 - Misconduct ABM | Analysis Script (Spyder-ready)

HOW TO USE IN SPYDER:
  1. Put this file IN THE SAME FOLDER as your four CSVs and
     04_Analysis_Utilities.py.
  2. In Spyder: File > Open > select this file.
  3. Run it cell-by-cell with Ctrl+Enter (or Cmd+Enter on Mac),
     OR run the whole thing with F5.

The '# %%' markers below define cells - Spyder treats each as a
runnable block (same idea as Jupyter cells).
"""

# %% [markdown]
# # Group 5 – Misconduct ABM | Analysis Notebook
#
# **Research question.** *Under what conditions does stricter enforcement reduce true misconduct?*
#
# This notebook implements the analytical plan from `01_Experiment_Design_and_Analytics_Plan.md`. It consumes the four CSVs exported from NetLogo's BehaviorSpace (see `02_Group5_BehaviorSpace_Experiments.xml`) and produces descriptives, visualisations, regression models, and a mechanism decomposition.
#
# **Structure.**
# 1. Setup & data loading
# 2. Descriptives and convergence check
# 3. Experiment A — policy grid (headline result)
# 4. Experiment B — organisational-culture context
# 5. Experiment C — mechanism trace (time-series)
# 6. Experiment D — learning-rate robustness
# 7. Stakeholder trade-off (Pareto)
# 8. Regression models (with interaction)
# 9. Mechanism decomposition
# 10. Summary of findings
#
# Keep the four CSVs next to this notebook under the names:
#
# ```
# ExpA_PolicyGrid.csv
# ExpB_CultureContext.csv
# ExpC_MechanismTrace.csv
# ExpD_LearningRateSensitivity.csv
# ```
#

# %% [markdown]
# ## 1. Setup & data loading

# %%
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.formula.api as smf

# Local helpers
sys.path.insert(0, ".")
from importlib import reload
import importlib.util

spec = importlib.util.spec_from_file_location("utils", "04_Analysis_Utilities.py")
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)

sns.set_theme(context="notebook", style="whitegrid", palette="viridis")
plt.rcParams["figure.dpi"] = 110
pd.set_option("display.float_format", lambda x: f"{x:,.4f}")

DATA = {
    "A": "ExpA_PolicyGrid.csv",
    "B": "ExpB_CultureContext.csv",
    "C": "ExpC_MechanismTrace.csv",
    "D": "ExpD_LearningRateSensitivity.csv",
}
for k, v in DATA.items():
    print(f"Exp {k}: {v}  {'✓' if os.path.exists(v) else '✗ (not found yet)'}")

# %%
# Load what's available. The notebook degrades gracefully if not all
# CSVs are present — you can run sections as their data becomes available.
raw = {}
for k, v in DATA.items():
    if os.path.exists(v):
        df = utils.load_behaviorspace_csv(v)
        df = utils.add_derived_rates(df)
        raw[k] = df
        print(f"Loaded {k}: {df.shape[0]:,} rows × {df.shape[1]} cols")
        print("  columns:", list(df.columns)[:10], "...")
    else:
        print(f"Skipping {k}: {v} not found")


# %% [markdown]
# ## 2. Descriptive statistics & convergence check
#
# Before any inferential work we need to confirm that the last 200 ticks are genuinely steady-state (otherwise reported means are contaminated by the transient). We plot the rolling mean of `true_misconduct_rate` for a sample of runs and eyeball the curve for a plateau.

# %%
if "A" in raw:
    df = raw["A"].copy()
    # Identify the tick column robustly — recent NetLogo uses 'step'
    tick_col = "step" if "step" in df.columns else ("ticks" if "ticks" in df.columns else df.columns[-1])
    print("Using tick column:", tick_col)

    # Sample 20 runs across the corners of the policy grid
    sample_keys = (
        df.groupby(["punishment_value", "reporter_protection"])["run_number"]
          .first().reset_index()
    )
    sample_runs = sample_keys["run_number"].head(20).tolist()
    sub = df[df["run_number"].isin(sample_runs)].copy()

    # Rolling 25-tick mean per run
    sub["roll_misconduct"] = (
        sub.groupby("run_number")["true_misconduct_rate"]
           .transform(lambda s: s.rolling(25, min_periods=1).mean())
    )

    fig, ax = plt.subplots(figsize=(9, 4.5))
    for (pv, rp), g in sub.groupby(["punishment_value", "reporter_protection"]):
        for rn, gr in g.groupby("run_number"):
            ax.plot(gr[tick_col], gr["roll_misconduct"], alpha=0.4, lw=0.9,
                    label=f"P={pv}, R={rp}")
    ax.axvspan(300, 500, alpha=0.12, color="grey", label="steady-state window")
    ax.set_xlabel("tick"); ax.set_ylabel("rolling true-misconduct rate")
    ax.set_title("Convergence check — is tick 300–500 steady?")
    # dedupe legend
    h, l = ax.get_legend_handles_labels()
    ddict = dict(zip(l, h))
    ax.legend(ddict.values(), ddict.keys(), loc="upper right", fontsize=7, ncol=2)
    plt.tight_layout(); plt.show()


# %%
# Collapse Experiment A to one row per run (cell-level)
if "A" in raw:
    df = raw["A"]
    tick_col = "step" if "step" in df.columns else "ticks"
    group_keys = ["run_number", "punishment_value", "reporter_protection"]
    metric_cols = [
        "true_misconduct_rate",
        "hidden_misconduct_rate_this_tick",
        "retaliation_rate",
        "reporting_yield",
        "mean_misconduct_propensity_of_employees",
        "mean_fear_of_employees",
        "mean_utility_of_employees",
    ]
    metric_cols = [c for c in metric_cols if c in df.columns]

    ss = utils.steady_state_mean(
        df, group_keys=group_keys, metric_cols=metric_cols,
        tick_col=tick_col, window_start=300, window_end=500,
    )
    vol = utils.steady_state_std(
        df, group_keys=group_keys,
        metric_cols=["true_misconduct_rate"],
        tick_col=tick_col, window_start=300, window_end=500,
    ).rename(columns={"true_misconduct_rate": "misconduct_volatility"})
    ss = ss.merge(vol, on=group_keys)
    expA = ss
    print("Experiment A run-level table:", expA.shape)
    print(expA.describe().T)


# %% [markdown]
# ## 3. Experiment A — The policy grid
#
# ### 3.1  Headline heatmap
#
# If our central hypothesis is right, misconduct should be lowest in the upper-right (strict + protected) corner, *not* along the "strict" row alone.

# %%
if "A" in raw:
    cell = expA.groupby(["punishment_value", "reporter_protection"]).agg(
        true_misconduct=("true_misconduct_rate", "mean"),
        hidden_rate=("hidden_misconduct_rate_this_tick", "mean"),
        retaliation_rate=("retaliation_rate", "mean"),
        mean_fear=("mean_fear_of_employees", "mean"),
    ).reset_index()

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    for ax, metric, title in [
        (axes[0], "true_misconduct", "True misconduct rate (per capita, ss mean)"),
        (axes[1], "hidden_rate",     "Hidden-misconduct rate (ss mean)"),
    ]:
        piv = cell.pivot(index="reporter_protection",
                         columns="punishment_value",
                         values=metric)
        sns.heatmap(piv, ax=ax, annot=True, fmt=".3f",
                    cmap="magma_r", cbar_kws={"label": metric})
        ax.set_title(title); ax.invert_yaxis()
    plt.suptitle("Experiment A — policy grid", y=1.03)
    plt.tight_layout(); plt.show()


# %% [markdown]
# ### 3.2  Line plot with bootstrap confidence bands
#
# Arguably the clearest single visual for the interaction: true misconduct as a function of punishment, separated by protection regime.

# %%
if "A" in raw:
    ci_tbl = utils.cell_means_with_ci(
        expA,
        cell_keys=["punishment_value", "reporter_protection"],
        metric="true_misconduct_rate",
        n_boot=2000,
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    palette = sns.color_palette("viridis", n_colors=ci_tbl["reporter_protection"].nunique())
    for col, (rp, g) in zip(palette, ci_tbl.groupby("reporter_protection")):
        g = g.sort_values("punishment_value")
        ax.plot(g["punishment_value"], g["true_misconduct_rate_mean"],
                marker="o", color=col, label=f"protection={rp}")
        ax.fill_between(g["punishment_value"],
                        g["true_misconduct_rate_ci_lo"],
                        g["true_misconduct_rate_ci_hi"],
                        color=col, alpha=0.18)
    ax.set_xlabel("punishment-value (enforcement strictness)")
    ax.set_ylabel("true-misconduct rate (steady-state mean, per capita)")
    ax.set_title("Does stricter enforcement reduce misconduct?\n"
                 "It depends on reporter-protection.")
    ax.legend(title="reporter-protection", loc="best")
    plt.tight_layout(); plt.show()


# %% [markdown]
# ### 3.3  Violin plots — full distributional view
#
# Means can hide bi-modality or heavy tails, both plausible in a feedback-coupled system.

# %%
if "A" in raw:
    fig, ax = plt.subplots(figsize=(11, 5))
    plot_df = expA.copy()
    plot_df["punishment_str"] = plot_df["punishment_value"].round(2).astype(str)
    sns.violinplot(
        data=plot_df, x="punishment_str", y="true_misconduct_rate",
        hue="reporter_protection", split=False, inner="quartile",
        linewidth=0.8, cut=0, ax=ax,
    )
    ax.set_xlabel("punishment-value")
    ax.set_ylabel("true-misconduct rate (ss mean per run)")
    ax.set_title("Distribution across 20 runs per policy cell")
    plt.tight_layout(); plt.show()


# %% [markdown]
# ### 3.4  Scatter + regression lines (within-protection slopes)
#
# This is the most honest "raw data" version of the interaction test: points = individual runs, lines = within-stratum OLS fit with 95% CI.

# %%
if "A" in raw:
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.regplot_kwargs = dict(scatter_kws=dict(alpha=0.35, s=18),
                              line_kws=dict(lw=2))
    palette = sns.color_palette("viridis",
                                n_colors=expA["reporter_protection"].nunique())
    for col, (rp, g) in zip(palette, expA.groupby("reporter_protection")):
        sns.regplot(
            x="punishment_value", y="true_misconduct_rate",
            data=g, ax=ax,
            scatter_kws=dict(alpha=0.35, s=18, color=col),
            line_kws=dict(lw=2, color=col),
            label=f"protection={rp}", ci=95,
        )
    ax.set_title("Within-protection linear fits"); ax.legend()
    ax.set_xlabel("punishment-value"); ax.set_ylabel("true-misconduct rate (ss)")
    plt.tight_layout(); plt.show()


# %% [markdown]
# ## 4. Experiment B — Organisational-culture context
#
# Does the "punishment works only under high protection" finding survive when the organisation starts with a cleaner or a more corrupt culture, or with a different baseline psychological safety? We facet the headline heatmap by culture cell.

# %%
if "B" in raw:
    df = raw["B"]
    tick_col = "step" if "step" in df.columns else "ticks"
    group_keys = ["run_number", "punishment_value", "reporter_protection",
                  "initial_misconduct_propensity", "initial_fear"]
    metric_cols = [
        "true_misconduct_rate",
        "hidden_misconduct_rate_this_tick",
        "retaliation_rate",
        "mean_fear_of_employees",
        "mean_utility_of_employees",
    ]
    metric_cols = [c for c in metric_cols if c in df.columns]
    expB = utils.steady_state_mean(
        df, group_keys=group_keys, metric_cols=metric_cols,
        tick_col=tick_col, window_start=300, window_end=500,
    )
    print("Experiment B run-level:", expB.shape)


# %%
if "B" in raw:
    cellB = (expB.groupby(["punishment_value", "reporter_protection",
                           "initial_misconduct_propensity", "initial_fear"])
                   ["true_misconduct_rate"].mean().reset_index())

    g = sns.FacetGrid(cellB, row="initial_fear", col="initial_misconduct_propensity",
                      height=2.4, aspect=1.15, margin_titles=True)
    def heat(data, **kwargs):
        piv = data.pivot(index="reporter_protection",
                         columns="punishment_value",
                         values="true_misconduct_rate")
        sns.heatmap(piv, annot=True, fmt=".2f", cmap="magma_r",
                    cbar=False, ax=plt.gca())
        plt.gca().invert_yaxis()
    g.map_dataframe(heat)
    g.fig.suptitle("Exp B — true misconduct by policy, faceted by organisational culture",
                   y=1.02)
    plt.tight_layout(); plt.show()


# %% [markdown]
# ## 5. Experiment C — Mechanism trace (time-series)
#
# Here we open the black box. For each of the six regime corners we plot the mean trajectory (over 30 seeds) of propensity, fear, retaliation, and misconduct with 95% bootstrap bands. Reading left-to-right within each row tells the causal story.

# %%
if "C" in raw:
    df = raw["C"].copy()
    tick_col = "step" if "step" in df.columns else "ticks"

    # Time-series cell means + 95% CI (across seeds)
    metrics = [
        ("true_misconduct_rate", "true-misconduct rate"),
        ("mean_fear_of_employees", "mean fear"),
        ("mean_misconduct_propensity_of_employees", "mean propensity"),
        ("retaliation_rate", "retaliation rate"),
    ]
    metrics = [(m, lbl) for m, lbl in metrics if m in df.columns]

    keys = ["punishment_value", "reporter_protection", tick_col]
    agg = df.groupby(keys)[[m for m, _ in metrics]].agg(["mean", "std", "count"])
    agg.columns = [f"{m}_{s}" for m, s in agg.columns]
    agg = agg.reset_index()
    # 95% CI from normal approx (fine given N=30)
    for m, _ in metrics:
        se = agg[f"{m}_std"] / np.sqrt(agg[f"{m}_count"])
        agg[f"{m}_lo"] = agg[f"{m}_mean"] - 1.96 * se
        agg[f"{m}_hi"] = agg[f"{m}_mean"] + 1.96 * se

    fig, axes = plt.subplots(len(metrics), 2, figsize=(12, 3 * len(metrics)),
                             sharex=True)
    if len(metrics) == 1:
        axes = np.array([axes])
    palette = sns.color_palette("viridis",
                                n_colors=agg["reporter_protection"].nunique())
    pv_values = sorted(agg["punishment_value"].unique())

    for col_idx, pv in enumerate(pv_values):
        sub_pv = agg[agg["punishment_value"] == pv]
        for row_idx, (m, label) in enumerate(metrics):
            ax = axes[row_idx, col_idx]
            for c, (rp, g) in zip(palette, sub_pv.groupby("reporter_protection")):
                g = g.sort_values(tick_col)
                ax.plot(g[tick_col], g[f"{m}_mean"], color=c,
                        label=f"R={rp}")
                ax.fill_between(g[tick_col], g[f"{m}_lo"], g[f"{m}_hi"],
                                color=c, alpha=0.18)
            ax.set_ylabel(label)
            if row_idx == 0:
                ax.set_title(f"punishment-value = {pv}")
            if row_idx == len(metrics) - 1:
                ax.set_xlabel("tick")
            if row_idx == 0 and col_idx == 0:
                ax.legend(fontsize=8, loc="best")
    plt.suptitle("Experiment C — mechanism trace (mean ± 95% CI, 30 seeds)",
                 y=1.01)
    plt.tight_layout(); plt.show()


# %% [markdown]
# **How to read the mechanism figure.**
#
# * Compare the **right column** (`punishment-value = 0.7`, strict) with the **left column** (`punishment-value = 0.3`, lenient).
# * Within each column, follow the coloured lines: **yellow = high protection**, **purple = low protection**.
# * The chilling channel is visible when, under **low protection + strict punishment** (bottom-left of the right column), `mean fear` climbs, `retaliation rate` is high, propensity fails to fall, and `true misconduct` remains flat.
# * The deterrence channel dominates when, under **high protection + strict punishment** (top of the right column), fear decays, propensity slides, misconduct drops.

# %% [markdown]
# ## 6. Experiment D — Learning-rate sensitivity (robustness)
#
# Does our headline finding depend on how fast employees update their beliefs? We compare the interaction effect across three `learning-rate` settings.

# %%
if "D" in raw:
    df = raw["D"]
    tick_col = "step" if "step" in df.columns else "ticks"
    group_keys = ["run_number", "punishment_value",
                  "reporter_protection", "learning_rate"]
    metrics = ["true_misconduct_rate", "mean_fear_of_employees",
               "retaliation_rate"]
    metrics = [c for c in metrics if c in df.columns]
    expD = utils.steady_state_mean(
        df, group_keys=group_keys, metric_cols=metrics,
        tick_col=tick_col, window_start=300, window_end=500,
    )

    cellD = (expD.groupby(["punishment_value", "reporter_protection",
                            "learning_rate"])
             ["true_misconduct_rate"].agg(["mean", "std", "count"]).reset_index())
    cellD["sem"] = cellD["std"] / np.sqrt(cellD["count"])

    g = sns.FacetGrid(cellD, col="learning_rate", height=3.4, aspect=1.1)
    def lineplot(data, **kwargs):
        palette = sns.color_palette("viridis",
                                    n_colors=data["reporter_protection"].nunique())
        for c, (rp, sub) in zip(palette, data.groupby("reporter_protection")):
            sub = sub.sort_values("punishment_value")
            plt.errorbar(sub["punishment_value"], sub["mean"],
                         yerr=1.96 * sub["sem"],
                         marker="o", color=c, label=f"R={rp}", capsize=3)
        plt.xlabel("punishment-value")
        plt.ylabel("true-misconduct rate (ss)")
        plt.legend()
    g.map_dataframe(lineplot)
    g.fig.suptitle("Exp D — is the interaction robust to learning-rate?", y=1.02)
    plt.tight_layout(); plt.show()


# %% [markdown]
# ## 7. Stakeholder trade-off (Pareto view)
#
# The professor warned: different stakeholders have different outcomes. Management cares about *true misconduct*; employees care about *retaliation* and *fear*; regulators care about *hidden misconduct*. A policy may be "good" for one and "bad" for another. We visualise this explicitly.

# %%
if "A" in raw:
    trade = (expA.groupby(["punishment_value", "reporter_protection"])
             [["true_misconduct_rate", "retaliation_rate",
               "hidden_misconduct_rate_this_tick", "mean_fear_of_employees"]]
             .mean().reset_index())

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # Left: misconduct vs retaliation
    ax = axes[0]
    sc = ax.scatter(trade["retaliation_rate"], trade["true_misconduct_rate"],
                    c=trade["reporter_protection"], s=70 + 250*trade["punishment_value"],
                    cmap="viridis", edgecolor="k", alpha=0.85)
    for _, r in trade.iterrows():
        ax.annotate(f"P={r['punishment_value']:.1f}\nR={r['reporter_protection']:.2f}",
                    (r["retaliation_rate"], r["true_misconduct_rate"]),
                    fontsize=6, xytext=(4, 4), textcoords="offset points")
    ax.set_xlabel("retaliation rate (employee welfare cost) →")
    ax.set_ylabel("true misconduct rate (management cost) →")
    ax.set_title("Management vs employee stakeholders")
    plt.colorbar(sc, ax=ax, label="reporter-protection")

    # Right: misconduct vs hidden misconduct rate (regulator view)
    ax = axes[1]
    sc2 = ax.scatter(trade["hidden_misconduct_rate_this_tick"], trade["true_misconduct_rate"],
                     c=trade["reporter_protection"], s=70 + 250*trade["punishment_value"],
                     cmap="viridis", edgecolor="k", alpha=0.85)
    ax.set_xlabel("hidden-misconduct rate (regulator concern) →")
    ax.set_ylabel("true misconduct rate →")
    ax.set_title("Management vs regulator stakeholders")
    plt.colorbar(sc2, ax=ax, label="reporter-protection")

    plt.suptitle("Pareto trade-off across policy cells\n"
                 "(size ∝ punishment-value, colour = reporter-protection)")
    plt.tight_layout(); plt.show()


# %% [markdown]
# ## 8. Regression models
#
# "Graphs not enough" — the Week 6 slides explicitly call for quantitative insight. We fit three OLS models. Because the runs within a cell are independent draws, standard OLS errors are fine; for belt-and-braces we also report HC3 robust errors.

# %%
if "A" in raw:
    # Standardise IVs for clean interaction interpretation
    dfA = expA.copy()
    dfA["P"] = dfA["punishment_value"]
    dfA["R"] = dfA["reporter_protection"]
    dfA["Y"] = dfA["true_misconduct_rate"]

    m1 = smf.ols("Y ~ P + R + P:R", data=dfA).fit(cov_type="HC3")
    print("=" * 70)
    print("MODEL 1 — Primary interaction model")
    print("=" * 70)
    print(m1.summary())


# %%
if "A" in raw:
    # Mechanism models
    dfA["fear"] = dfA["mean_fear_of_employees"]
    dfA["prop"] = dfA["mean_misconduct_propensity_of_employees"]

    m2 = smf.ols("fear ~ P + R + P:R", data=dfA).fit(cov_type="HC3")
    m3 = smf.ols("prop ~ P + R + P:R", data=dfA).fit(cov_type="HC3")

    print("=" * 70)
    print("MODEL 2 — Chilling channel: fear = f(P, R, P*R)")
    print("=" * 70)
    print(m2.summary().tables[1])
    print()
    print("=" * 70)
    print("MODEL 3 — Deterrence channel: propensity = f(P, R, P*R)")
    print("=" * 70)
    print(m3.summary().tables[1])


# %%
if "B" in raw:
    dfB = expB.copy()
    dfB.rename(columns={
        "punishment_value": "P", "reporter_protection": "R",
        "initial_misconduct_propensity": "IP",
        "initial_fear": "IF",
        "true_misconduct_rate": "Y",
    }, inplace=True)
    m4 = smf.ols("Y ~ P*R + IP*P + IF*P + IP + IF", data=dfB).fit(cov_type="HC3")
    print("=" * 70)
    print("MODEL 4 — Context moderators (Experiment B)")
    print("=" * 70)
    print(m4.summary().tables[1])


# %% [markdown]
# ### 8.1  Marginal effects plot
#
# Because $\hat{\beta}_1 + \hat{\beta}_3 R$ is the slope of Y on P at protection level R, we can plot the marginal effect of punishment as a function of protection — with a CI from the covariance matrix. This is the cleanest single summary of the interaction.

# %%
if "A" in raw:
    import numpy as np
    cov = m1.cov_params()
    R_grid = np.linspace(0, 1, 101)
    beta1 = m1.params["P"]
    beta3 = m1.params["P:R"]
    # Var(beta1 + beta3*R) = Var(beta1) + R^2 Var(beta3) + 2R Cov
    me = beta1 + beta3 * R_grid
    se = np.sqrt(
        cov.loc["P", "P"]
        + R_grid**2 * cov.loc["P:R", "P:R"]
        + 2 * R_grid * cov.loc["P", "P:R"]
    )
    lo, hi = me - 1.96 * se, me + 1.96 * se

    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.plot(R_grid, me, color="C0", lw=2, label="marginal effect dY/dP")
    ax.fill_between(R_grid, lo, hi, color="C0", alpha=0.2, label="95% CI")
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xlabel("reporter-protection (R)")
    ax.set_ylabel("Marginal effect of punishment on true misconduct")
    ax.set_title("At what protection level does stricter enforcement start working?")
    ax.legend(); plt.tight_layout(); plt.show()

    # Threshold: where does the CI first exclude zero?
    signif = hi < 0
    if signif.any():
        print(f"Enforcement becomes significantly deterrent at R ≈ {R_grid[signif.argmax()]:.2f}")
    else:
        print("Enforcement is never unambiguously deterrent in this grid.")


# %% [markdown]
# ## 9. Mechanism decomposition
#
# The total effect of punishment on true misconduct splits into:
#
# * a **direct (deterrence)** component captured by Model 3 — the effect of P on `misconduct-propensity`;
# * an **indirect (chilling)** component captured by Model 2 — the effect of P on `fear`, which (via the logistic in the NetLogo code) suppresses reporting.
#
# By comparing the regression slopes we can quantify **which channel dominates at each protection level**.

# %%
if "A" in raw:
    R_grid = np.linspace(0, 1, 101)

    # Slope of propensity on P at each R (negative = deterrence working)
    b1_p = m3.params["P"]; b3_p = m3.params["P:R"]
    me_prop = b1_p + b3_p * R_grid

    # Slope of fear on P at each R (positive = chilling working)
    b1_f = m2.params["P"]; b3_f = m2.params["P:R"]
    me_fear = b1_f + b3_f * R_grid

    fig, ax = plt.subplots(figsize=(8, 4.7))
    ax.plot(R_grid, me_prop, color="C0", label="∂(mean propensity)/∂P  (deterrence channel)")
    ax.plot(R_grid, me_fear, color="C3", label="∂(mean fear)/∂P  (chilling channel)")
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xlabel("reporter-protection (R)")
    ax.set_ylabel("marginal effect of punishment")
    ax.set_title("Which channel dominates, and where?")
    ax.legend(); plt.tight_layout(); plt.show()

    print("Deterrence channel (Δ propensity per 1.0 Δ punishment):")
    for rp in [0.0, 0.25, 0.5, 0.75, 1.0]:
        print(f"  R = {rp:.2f}: {b1_p + b3_p*rp:+.3f}")
    print("\nChilling channel (Δ fear per 1.0 Δ punishment):")
    for rp in [0.0, 0.25, 0.5, 0.75, 1.0]:
        print(f"  R = {rp:.2f}: {b1_f + b3_f*rp:+.3f}")


# %% [markdown]
# ## 10. Summary of findings
#
# Tick each hypothesis from the design doc against what the data actually show.  Fill these in after running the experiments.
#
# | # | Hypothesis | Supported? | Key evidence |
# |---|---|---|---|
# | H1 | Marginal effect of P on misconduct depends on R (interaction β₃ < 0, CI excludes 0) | ☐ | Model 1 coefficient on `P:R` |
# | H1a | Heatmap (§3.1) shows diagonal minimum, not horizontal | ☐ | Fig. 3.1 |
# | H1b | Violin plots (§3.3) show sign change / slope flattening at low R | ☐ | Fig. 3.3 |
# | H2 | "P works only under high R" is robust across starting cultures (Exp B) | ☐ | Fig. 4 faceted heatmap; Model 4 |
# | H3 | Chilling channel visible: at low R, strict P raises mean fear and hidden rate while true misconduct does not fall | ☐ | Exp C time-series; Models 2 & 3 |
# | H4 | Pareto front is spanned by (any P, high R); no policy dominates on all DVs | ☐ | Fig. 7 |
# | H5 | Qualitative findings survive learning-rate ∈ {0.05, 0.2, 0.4} | ☐ | Fig. 6 |
#
# ### Managerial takeaways (to be finalised after running)
#
# 1. **Protection is a precondition, not a supplement.** Stricter sanctions without whistleblower safeguards do not reliably reduce misconduct; they displace it into the dark figure.
# 2. **Invest in the pair, not the lever.** The policy package that minimises *true* misconduct, *hidden* misconduct, and *retaliation* simultaneously lies in the top-right of the grid — both strict and protective.
# 3. **Fear is the intervening variable.** Interventions that reduce fear directly (psychological safety training, anonymous hotlines) buy headroom for sanctions to work. Sanctions alone, in a fearful climate, are counterproductive.
# 4. **Context matters — but the direction doesn't.** Starting cultures shift the *level* of equilibrium misconduct, but the *shape* of the policy landscape is preserved.
#
# ### Limitations
#
# * Steady-state defined as ticks 300–500; very low learning rates may not converge (flagged in §6).
# * Observation radius fixed at 3; denser organisations (larger `number-employees` with same radius) will have different witness availability.
# * Model is not calibrated to empirical data — conclusions are internal coherence of the simulated mechanism, not predictions of real-world rates.
#


# 04-05-Marco Experiment Documentation

## Scope

This folder contains the adapted experiment setup and analysis pipeline for the Group 5 misconduct ABM.  
It is based on `Experiments/01-05-Joel-Abend`, with a narrowed policy grid, renamed experiment structure, updated plotting, and improved CSV input handling.

## Folder Structure

- `Experiments-04-05-ABM.nlogox`  
  NetLogo model file with BehaviorSpace experiment definitions.
- `analyze_all_experiments-v3.py`  
  Python analysis script that loads BehaviorSpace CSV exports and creates plots.
- `tables/`  
  Expected location for CSV input files (preferred).
- experiment root (fallback)  
  CSV fallback location if files are not inside `tables/`.
- `Sample plots/`  
  Output folder for generated PNG plots.

## Experiments Implemented

### Experiment 1: `exp1_policy_grid`

- Purpose: policy landscape over punishment and protection combinations.
- Repetitions: `10`
- Time limit: `300` ticks
- Grid:
  - `punishment-value`: `0.20` to `0.80` in `0.05` steps
  - `reporter-protection`: `0.20` to `0.80` in `0.05` steps
- Metrics are exported at final run level (`runMetricsEveryStep=false`).

### Experiment 2: Sensitivity analysis (formerly Experiment 3)

- Implemented as:
  - `exp2a_sens_employees`
  - `exp2b_sens_init_propensity`
  - `exp2c_sens_init_fear`
  - `exp2d_sens_response_strength`
  - `exp2e_sens_drift_speed`
- Purpose: one-factor-at-a-time (OFAT) sensitivity around baseline policy.

## How To Run (Recommended Workflow)

### 1) Run NetLogo BehaviorSpace

Open `Experiments-04-05-ABM.nlogox` and run all required BehaviorSpace experiments.

Recommended run options:

- Enable only **Table output** (`Ausgabe in Tabelle`).
- Disable spreadsheet/statistics/list output for this workflow.
- Turn off view and monitor updates for speed when possible.
- Parallel runs: set according to hardware (for your setup, `24` has been used successfully).

For each experiment, write output to a dedicated CSV file:

- `exp1_policy_grid-table.csv`
- `exp2a_sens_employees-table.csv`
- `exp2b_sens_init_propensity-table.csv`
- `exp2c_sens_init_fear-table.csv`
- `exp2d_sens_response_strength-table.csv`
- `exp2e_sens_drift_speed-table.csv`

Preferred location: `./tables/`  
Fallback location: experiment root folder.

### 2) Run Python analysis

From this folder:

```powershell
python analyze_all_experiments-v3.py
```

Plots are written to:

- `Sample plots/exp1_heatmaps.png`
- `Sample plots/exp1_mechanism.png`
- `Sample plots/exp2_pareto.png`
- `Sample plots/exp1_archetypes.png`
- `Sample plots/exp2_sensitivity.png`

## Supported CSV Formats

The script supports both:

1. **BehaviorSpace Table export** (preferred)
2. **BehaviorSpace Spreadsheet-style export** (fallback parser implemented)

This was added because Spreadsheet-like files can otherwise miss expected normalized columns when read with a Table-only parser.

## Plot Design Notes

### Exp 1 heatmaps

- All policy steps from `0.20` to `0.80` are shown on both axes.
- All cells are annotated (smaller font for readability).
- Four archetype corners are highlighted.

### Exp 1 mechanism plot

- Uses all available `reporter-protection` levels in the current data.
- Uses all `punishment-value` steps on x-axis.
- Shared legend below the panels for better readability with many lines.

### Exp 2 Pareto plot (computed from Exp 1 data)

- No separate stakeholder-pareto experiment is required.
- Colorbar and size legend cover all policy steps.
- Additional thin progression lines by protection level improve readability.

## Possible Insights (from current sample outputs)

These are interpretation candidates, not final causal claims:

- Higher `reporter-protection` is associated with lower hidden misconduct and lower retaliation in most policy cells.
- Low protection (`~0.20-0.30`) shows clear risk of high hidden misconduct despite punishment changes.
- The Pareto landscape indicates visible trade-offs but also a frontier region where stronger protection improves multiple stakeholder outcomes simultaneously.
- The mechanism plot suggests punishment alone is insufficient when protection is weak.

## What Changed vs `01-05-Joel-Abend`

### BehaviorSpace setup changes

- Policy grid changed from `0.0-1.0` (step `0.1`) to `0.20-0.80` (step `0.05`).
- `exp2_stakeholder_pareto` experiment removed from NetLogo definitions.
- Former `exp3a-e` renamed to `exp2a-e`.

### Analysis script changes

- Migrated to `analyze_all_experiments-v3.py`.
- Added four explicit archetype labels:
  - `Status Quo`
  - `Iron Fist`
  - `Safe Harbor`
  - `Rule of Law`
- Reintroduced Pareto plot generation from Exp 1 data (`exp2_pareto.png`).
- Updated plots to display all policy steps clearly.
- Added robust Spreadsheet-format parser fallback.
- Added input-path logic: `tables/` first, root fallback.
- Added output-path logic: always write plots to `Sample plots/`.

## Final design decisions

- Archetype comparison is fixed as a static end-of-run comparison from final-run metrics.
- Pareto views are generated directly from Exp 1 policy-grid outcomes.
- There is no separate stakeholder-pareto BehaviorSpace run in this setup.

## Troubleshooting

- `KeyError: number-employees`  
  Usually caused by parsing Spreadsheet layout as Table layout.  
  The current script includes fallback parsing; verify CSV integrity if this still appears.

- Missing files error  
  Ensure CSV names exactly match expected filenames and exist either in:
  - `./tables/`, or
  - experiment root folder.

- Empty/partial plots  
  Confirm each BehaviorSpace run completed and CSVs were overwritten with full exports.


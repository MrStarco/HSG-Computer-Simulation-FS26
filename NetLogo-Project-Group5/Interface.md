# Interface Specification (NetLogo Interface Tab)

This document lists the currently integrated interface and experiment setup from `Group5_Misconduct_ABM.nlogox`.

## 1) Interface Widgets

### Buttons

1. `setup`
   - Command: `setup`
   - Type: Once button (`Forever = off`)

2. `go`
   - Command: `go`
   - Type: Forever button (`Forever = on`)

### Sliders

1. `number-employees`
   - Min: `20`
   - Max: `400`
   - Increment: `10`
   - Default: `200`

2. `initial-misconduct-propensity`
   - Min: `0`
   - Max: `1`
   - Increment: `0.01`
   - Default: `1.00`

3. `initial-fear`
   - Min: `0`
   - Max: `1`
   - Increment: `0.01`
   - Default: `1.00`

4. `punishment-value`
   - Min: `0`
   - Max: `1`
   - Increment: `0.01`
   - Default: `1.00`

5. `reporter-protection`
   - Min: `0`
   - Max: `1`
   - Increment: `0.01`
   - Default: `0.00`

6. `response-strength`
   - Min: `0`
   - Max: `1`
   - Increment: `0.01`
   - Default: `0.32`

7. `drift-speed`
   - Min: `0.01`
   - Max: `0.5`
   - Increment: `0.01`
   - Default: `0.05`

### Monitors

1. `True misconduct (total)` -> `true-misconduct-total`
2. `Sanctioned misconduct (total)` -> `sanctioned-misconduct-total`
3. `Hidden misconduct (total)` -> `hidden-misconduct-total`
4. `Hidden misconduct rate (total)` -> `hidden-misconduct-rate` (precision `3`)
5. `Reported events (total)` -> `reported-events-total`
6. `Retaliation events (total)` -> `retaliation-events-total`
7. `True misconduct (tick)` -> `true-misconduct-this-tick`
8. `Sanctioned misconduct (tick)` -> `sanctioned-this-tick`
9. `Reported events (tick)` -> `reported-events-this-tick`
10. `Retaliation events (tick)` -> `retaliation-events-this-tick`
11. `Hidden misconduct (tick)` -> `hidden-misconduct-this-tick`
12. `Hidden misconduct rate (tick)` -> `hidden-misconduct-rate-this-tick` (precision `3`)
13. `Relative change (%)` -> `relative-misconduct-change` (precision `1`)

### Plots

#### Plot 1: `Misconduct Dynamics (Cumulative)`

- X-axis: `ticks`
- Y-axis: `events`
- Pens:
  - `true total` -> `plot true-misconduct-total`
  - `sanctioned total` -> `plot sanctioned-misconduct-total`
  - `hidden total` -> `plot hidden-misconduct-total`

#### Plot 2: `Per Tick Misconduct`

- X-axis: `ticks`
- Y-axis: `events / tick`
- Pens:
  - `true (tick)` -> `plot true-misconduct-this-tick`
  - `sanctioned (tick)` -> `plot sanctioned-this-tick`
  - `hidden (tick)` -> `plot (true-misconduct-this-tick - sanctioned-this-tick)`

#### Plot 3: `Relative Misconduct Change (%)`

- X-axis: `ticks`
- Y-axis: `% change`
- Pens:
  - `rel. change %` -> `plot relative-misconduct-change`
  - `zero` -> `plot 0`

## 2) Hardcoded Model Constants

These values are fixed in code and not exposed as sliders:

- `BASE-REPORTING-CLIMATE = 0.1`
- `OBSERVATION-RADIUS = 3`
- `PUNISHMENT-WITNESS-RADIUS = 6`
- `RETALIATION-WITNESS-RADIUS = 3`
- `BYSTANDER-EFFECT-FACTOR = 0.3`

## 3) BehaviorSpace Experiments Included in `.nlogox`

The integrated model now contains built-in BehaviorSpace experiments:

- `exp1_policy_grid`
- `exp2_stakeholder_pareto`
- `exp3a_sens_employees`
- `exp3b_sens_init_propensity`
- `exp3c_sens_init_fear`
- `exp3d_sens_response_strength`
- `exp3e_sens_drift_speed`

### Common Experiment Settings

- `setup`: `setup`
- `go`: `go`
- `timeLimit`: `300`
- `repetitions`: `10`

`exp2_stakeholder_pareto` runs with `runMetricsEveryStep = true`; the others export end-of-run table metrics.

## 4) Experiment Analysis Assets

The repository now includes:

- Python analysis script: `NetLogo-Project-Group5/Experiments/analyze_all_experiments.py`
- Sample plot outputs: `NetLogo-Project-Group5/Experiments/Sample Output Plots/`

To use the script, update `CSV_FOLDER` and `PREFIX` at the top of the file, then run it in Python (e.g. Spyder or standard Python execution).

## 5) Manual Setup in NetLogo

1. Start NetLogo 7.x.
2. Open `NetLogo-Project-Group5/Group5_Misconduct_ABM.nlogox`.
3. For interactive checks:
   - Click `setup`
   - Start/stop `go`
   - Vary key policy sliders (`punishment-value`, `reporter-protection`)
4. For experiment exports:
   - Open `Tools -> BehaviorSpace`
   - Select one of the integrated experiments
   - Run and export results as **Table CSV**

## 6) Recommended Layout Structure

- Top left: `setup`, `go`
- Left column: all sliders
- Center: graphics window
- Right column: monitors
- Bottom/right: the three plots

# Interface Specification (NetLogo Interface Tab)

This document lists the current layout of `Group5_Misconduct_ABM.nlogox` after the latest interface refresh. The left column contains sliders with the control buttons directly underneath (including a color-mode switch), the right column hosts total monitors with the legend below them, and the bottom-right area shows the two dedicated plots.

## 1) Buttons

1. `setup`
   - Command: `setup`
   - Type: once button (`Forever = false`)

2. `go`
   - Command: `go`
   - Type: forever button (`Forever = true`)

3. `go-50`
   - Command: `go-50`
   - Type: once button (`Forever = false`)
   - Repeats `go` 50 times for a quick fixed-length run.

4. `switch color mode`
   - Command: `toggle-color-mode`
   - Type: once button (`Forever = false`)
   - Toggles between `event` view and `fear` view.

## 2) Sliders

1. `number-employees`
   - Min: `20`
   - Max: `400`
   - Increment: `10`
   - Default: `250`

2. `initial-misconduct-propensity`
   - Min: `0`
   - Max: `1`
   - Increment: `0.01`
   - Default: `0.30`

3. `initial-fear`
   - Min: `0`
   - Max: `1`
   - Increment: `0.01`
   - Default: `0.35`

4. `punishment-value`
   - Min: `0`
   - Max: `1`
   - Increment: `0.01`
   - Default: `1.00`

5. `reporter-protection`
   - Min: `0`
   - Max: `1`
   - Increment: `0.01`
   - Default: `0.30`

6. `response-strength`
   - Min: `0`
   - Max: `1`
   - Increment: `0.01`
   - Default: `0.20`

7. `drift-speed`
   - Min: `0.01`
   - Max: `0.5`
   - Increment: `0.01`
   - Default: `0.15`

## 3) Monitors

1. `True misconduct (total)` -> `true-misconduct-total`
2. `Sanctioned misconduct (total)` -> `sanctioned-misconduct-total`
3. `Hidden misconduct (total)` -> `hidden-misconduct-total`
4. `Hidden misconduct rate (total)` -> `hidden-misconduct-rate` (precision `3`)
5. `Reported events (total)` -> `reported-events-total`
6. `Retaliation events (total)` -> `retaliation-events-total`

Tick-level monitors were removed to keep the sidebar focused on cumulative totals—those per-tick values still feed the plots.

## 4) Color semantics

Color mode defaults to `event` on each `setup`. In `event` mode, agent colors are interpreted as:

- `Green / Yellow / Orange`: fear level (`low / medium / high`)
- `Red`: misconduct committed (direct)
- `Blue`: report submitted (direct)
- `Cyan`: retaliation experienced (direct)
- `Violet`: sanctioned offender (direct)
- `Brown`: no direct event in current tick

When switched to `fear` mode, all agents are colored by fear only (`green/yellow/orange`), regardless of current event flags.

The legend is rendered as a compact note widget in the right column below the total monitors, aligned to the same area previously used by the old legend block.

## 5) Plots

### Plot 1: `Relative Misconduct Change (%)`

- X-axis: `ticks`
- Y-axis: `% change`
- Pens:
  - `rel. change %` -> `plot relative-misconduct-change`
  - `zero` -> `plot 0`

### Plot 2: `Per Tick Misconduct`

- X-axis: `ticks`
- Y-axis: `events / tick`
- Pens:
  - `true (tick)` -> `plot true-misconduct-this-tick`
  - `sanctioned (tick)` -> `plot sanctioned-this-tick`
  - `hidden (tick)` -> `plot (true-misconduct-this-tick - sanctioned-this-tick)`

## 6) Hardcoded constants (not sliders)

- `BASE-REPORTING-CLIMATE = 0.1`
- `OBSERVATION-RADIUS = 3`
- `PUNISHMENT-WITNESS-RADIUS = 6`
- `RETALIATION-WITNESS-RADIUS = 3`
- `BYSTANDER-EFFECT-FACTOR = 0.3`

## 7) Embedded BehaviorSpace experiments

The integrated model now contains built-in BehaviorSpace experiments:

- `exp1_policy_grid`
- `exp2_stakeholder_pareto`
- `exp3a_sens_employees`
- `exp3b_sens_init_propensity`
- `exp3c_sens_init_fear`
- `exp3d_sens_response_strength`
- `exp3e_sens_drift_speed`

Shared settings:

- `setup`: `setup`
- `go`: `go`
- `timeLimit`: `300`
- `repetitions`: `10`

Special case:

- `exp2_stakeholder_pareto` uses `runMetricsEveryStep = true`.

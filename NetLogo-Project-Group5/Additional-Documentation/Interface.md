# Interface Specification (NetLogo Interface Tab)

This document specifies the Interface tab widgets and their settings for `Group5_Misconduct_ABM.nlogox`. The left column contains sliders with the control buttons directly underneath (including a color-mode switch), the right column hosts total monitors with the legend below them, and the bottom-right area shows the two dedicated plots.

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

4. `punishment-severity`
   - Min: `0`
   - Max: `1`
   - Increment: `0.01`
   - Default: `1.00`

5. `reporter-protection`
   - Min: `0`
   - Max: `1`
   - Increment: `0.01`
   - Default: `0.30`

6. `learning-rate`
   - Min: `0`
   - Max: `1`
   - Increment: `0.01`
   - Default: `0.20`

7. `baseline-recovery-rate`
   - Min: `0.01`
   - Max: `0.5`
   - Increment: `0.01`
   - Default: `0.15`

## 3) Monitors

1. `Committed misconduct (total)` -> `committed-misconduct-total`
2. `Punished misconduct (total)` -> `punished-misconduct-total`
3. `Hidden misconduct (total)` -> `hidden-misconduct-total`
4. `Hidden misconduct rate (total)` -> `hidden-misconduct-rate` (precision `3`)
5. `Reported events (total)` -> `reported-events-total`
6. `Retaliation events (total)` -> `retaliation-events-total`

The sidebar displays cumulative totals only; per-tick values are still computed internally and feed the plots.

## 4) Color semantics

Color mode defaults to `event` on each `setup`. In `event` mode, agent colors are interpreted as:

- `Green / Yellow / Orange`: fear level (`low / medium / high`)
- `Red`: misconduct committed (direct)
- `Blue`: report submitted (direct)
- `Cyan`: retaliation experienced (direct)
- `Violet`: sanctioned offender (direct)
- `Brown`: no direct event in current tick

When switched to `fear` mode, all agents are colored by fear only (`green/yellow/orange`), regardless of current event flags.

The legend is rendered as a compact note widget in the right column below the total monitors.

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
  - `committed (tick)` -> `plot committed-misconduct-this-tick`
  - `punished (tick)` -> `plot punished-misconduct-this-tick`
  - `hidden (tick)` -> `plot (committed-misconduct-this-tick - punished-misconduct-this-tick)`

## 6) Hardcoded constants (not sliders)

- `base-reporting-climate = 0.1`
- `observation-radius = 3`
- `punishment-witness-radius = 6`
- `retaliation-witness-radius = 3`
- `bystander-effect-factor = 0.3`

## 7) Sanction update dynamics

Sanction update formula:

- `misconduct-propensity <- clamp01(misconduct-propensity - learning-rate * punishment-severity * (reporter-protection * (1 + punishment-severity) / 2 - 0.8 * punishment-severity * (1 - reporter-protection)))`

This combines a deterrence channel (protection-weighted) and a backlash channel (high punishment under low protection), enabling nonlinear policy effects. See Code tab for full derivation.

## 8) BehaviorSpace experiments

Six experiments are embedded in the model (`Tools → BehaviorSpace`): `exp1_policy_grid` (2D policy sweep) and `exp2a`–`exp2e` (one-factor-at-a-time sensitivity). For full parameter configurations, see the comment block at the end of the Code tab.

# Group 5 Misconduct ABM - Documentation

This document describes the current model implementation in `Group5_Misconduct_ABM.nlogox`.

## What the model represents

The model simulates organizational misconduct in a fixed employee population.  
Core question: when does stronger punishment reduce true misconduct, and when does it instead increase fear, suppress reporting, and leave more misconduct hidden?

Each tick:
- employees may commit misconduct,
- coworkers may observe and report,
- every reported event is sanctioned automatically,
- retaliation may happen after reporting,
- fear and misconduct propensity are updated.

## Tick flow

1. **Movement**: employees move locally (`rt random 50`, `lt random 50`, `fd 1`).
2. **Misconduct decision**: each employee commits with probability `misconduct-propensity`.
3. **Observation**: witnesses are selected from `in-radius observation-radius`.
4. **Reporting**: one witness decides to report via logistic probability.
5. **Sanctioning**: every report triggers sanctioning.
6. **Retaliation**: retaliation happens with probability `1 - reporter-protection`.
7. **Drift**: non-shocked agents drift back toward baseline values.
8. **Metrics update**: cumulative and per-tick indicators are recalculated.

## Core equations

- `logistic(x) = 1 / (1 + exp(-5 * x))`
- `p_report = logistic(base-reporting-climate + reporter-protection - fear)`
- `p_retaliation = clamp01(1 - reporter-protection)`

On sanction (offender):

- `misconduct-propensity <- clamp01(misconduct-propensity - learning-rate * punishment-severity * (reporter-protection * (1 + punishment-severity) / 2 - 0.8 * punishment-severity * (1 - reporter-protection)))`

On sanction (punishment bystanders):

- same term multiplied by `bystander-effect-factor`

The sanction update combines two opposing channels:

- deterrence channel: `reporter-protection * (1 + punishment-severity) / 2` — punishment reduces propensity more effectively when reporters are protected
- backlash channel: `0.8 * punishment-severity * (1 - reporter-protection)` — under low protection, high punishment partially offsets the deterrence effect
- net effect: with sufficient protection, propensity decreases; with very low protection and high severity, the net change approaches zero or partially reverses (fear-trap dynamics)

On retaliation (reporter):

- `fear <- clamp01(fear + learning-rate * (0.2 + 0.8 * punishment-severity) * (1 - reporter-protection))`

On retaliation (retaliation bystanders):

- same term multiplied by `bystander-effect-factor`

Drift phase:

- if no misconduct this tick: propensity mean-reverts to `initial-misconduct-propensity`
- if no retaliation this tick: fear mean-reverts to `initial-fear`
- speed for both channels: `baseline-recovery-rate`

## Hardcoded constants

These values are fixed in code (not sliders):

| Variable | Value |
|---|---|
| `base-reporting-climate` | `0.1` |
| `observation-radius` | `3` |
| `punishment-witness-radius` | `6` |
| `retaliation-witness-radius` | `3` |
| `bystander-effect-factor` | `0.3` |

## Interface controls (active sliders)

- `number-employees` (20..400, step 10, default 250)
- `initial-misconduct-propensity` (0..1, step 0.01, default 0.30)
- `initial-fear` (0..1, step 0.01, default 0.35)
- `punishment-severity` (0..1, step 0.01, default 1.00)
- `reporter-protection` (0..1, step 0.01, default 0.30)
- `learning-rate` (0..1, step 0.01, default 0.20)
- `baseline-recovery-rate` (0.01..0.5, step 0.01, default 0.15)

## Visual cues

The model provides two color modes. `Event` mode is the default after `setup`: direct events are highlighted per tick (`red` misconduct, `blue` report, `cyan` retaliation experienced, `violet` sanctioned offender) and agents without a direct event are shown in `brown`. `Fear` mode colors all agents by fear only (`green` → `yellow` → `orange`). The `switch color mode` button under the run buttons toggles between these two views.

## Outputs and interpretation

Key cumulative metric:

- `hidden-misconduct-rate = (committed-misconduct-total - punished-misconduct-total) / committed-misconduct-total`

Because sanctioning is automatic after reporting, hidden misconduct tracks unreported cases. The monitors display cumulative totals: committed misconduct, punished misconduct, hidden misconduct, hidden misconduct rate, reported events, and retaliation events. Tick-level counts are still computed every tick to populate the two plots.

Plots:

1. `Per Tick Misconduct` — committed, punished, and hidden counts per tick
2. `Relative Misconduct Change (%)` — tick-over-tick momentum indicator

## BehaviorSpace experiments

Six experiments are embedded in the model (`Tools → BehaviorSpace`):

- `exp1_policy_grid`: sweeps `punishment-severity × reporter-protection` (0.0 to 1.0, step 0.1) to map the full policy space.
- `exp2a` – `exp2e`: one-factor-at-a-time (OFAT) sensitivity experiments for `number-employees`, `initial-misconduct-propensity`, `initial-fear`, `learning-rate`, and `baseline-recovery-rate` respectively.

All experiments: 10 repetitions, 300 ticks per run. Full parameter ranges are documented in the Code tab.

## How to run

1. Open `Group5_Misconduct_ABM.nlogox` in NetLogo 7.0.3.
2. Click `setup`, then `go` (continuous) or `go-50` (exactly 50 ticks).
3. Use `switch color mode` to toggle between event highlighting and fear visualization.
4. For experiments: `Tools → BehaviorSpace`, select an experiment, run, export CSV.

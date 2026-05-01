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
- `p_report = logistic(base-reporting-climate + 0.8 * reporter-protection - fear)`
- `p_retaliation = clamp01(1 - reporter-protection)`

On sanction (offender):

- `misconduct-propensity <- clamp01(misconduct-propensity - response-strength * (0.3 + 0.7 * punishment-value) * (1.5 * reporter-protection - 0.5))`

On sanction (punishment bystanders):

- same term multiplied by `bystander-effect-factor`

On retaliation (reporter):

- `fear <- clamp01(fear + response-strength * (0.2 + 0.8 * punishment-value) * (1 - reporter-protection))`

On retaliation (retaliation bystanders):

- same term multiplied by `bystander-effect-factor`

Drift phase:

- if no misconduct this tick: propensity mean-reverts to `initial-misconduct-propensity`
- if no retaliation this tick: fear mean-reverts to `initial-fear`
- speed for both channels: `drift-speed`

## Hardcoded constants

These values are fixed in code (not sliders):

| Constant | Value |
|---|---|
| `BASE-REPORTING-CLIMATE` | `0.1` |
| `OBSERVATION-RADIUS` | `3` |
| `PUNISHMENT-WITNESS-RADIUS` | `6` |
| `RETALIATION-WITNESS-RADIUS` | `3` |
| `BYSTANDER-EFFECT-FACTOR` | `0.3` |

## Interface controls (active sliders)

- `number-employees` (20..400, step 10, default 250)
- `initial-misconduct-propensity` (0..1, step 0.01, default 0.30)
- `initial-fear` (0..1, step 0.01, default 0.35)
- `punishment-value` (0..1, step 0.01, default 1.00)
- `reporter-protection` (0..1, step 0.01, default 0.30)
- `response-strength` (0..1, step 0.01, default 0.20)
- `drift-speed` (0.01..0.5, step 0.01, default 0.15)

## Outputs and interpretation

Key cumulative metric:

- `hidden-misconduct-rate = (true-misconduct-total - sanctioned-misconduct-total) / true-misconduct-total`

Because sanctioning is automatic after reporting, hidden misconduct is equivalent to unreported misconduct.

Plots included:

1. `Misconduct Dynamics (Cumulative)`
2. `Relative Misconduct Change (%)`
3. `Per Tick Misconduct`

## BehaviorSpace experiments included

Embedded experiments:

- `exp1_policy_grid`
- `exp2_stakeholder_pareto`
- `exp3a_sens_employees`
- `exp3b_sens_init_propensity`
- `exp3c_sens_init_fear`
- `exp3d_sens_response_strength`
- `exp3e_sens_drift_speed`

Shared setup:

- `setup`/`go`
- `timeLimit = 300`
- `repetitions = 10`

Common baseline values used across experiments:

- `number-employees = 300`
- `initial-misconduct-propensity = 0.4`
- `initial-fear = 0.3`
- `response-strength = 0.2`
- `drift-speed = 0.05`

`punishment-value` and `reporter-protection` are either stepped (policy grid / pareto) or fixed to `0.5` and `0.3` in one-factor sensitivity experiments.

## How to run

1. Open `Group5_Misconduct_ABM.nlogox` in NetLogo 7.x.
2. Click `setup`, then run `go`.
3. For experiments, open `Tools -> BehaviorSpace` and choose one integrated experiment.
4. Export tables as CSV for downstream analysis.

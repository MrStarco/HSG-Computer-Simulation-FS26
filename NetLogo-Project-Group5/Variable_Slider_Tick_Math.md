# Variables, Sliders, and Tick Mathematics

This document describes the mathematics currently implemented in `Group5_Misconduct_ABM.nlogox` and mirrored in `Code.nls`.

## 1) Variables

### 1.1 Agent variables (`employees-own`)

Each employee has:

- `misconduct-propensity` in `[0, 1]`
- `fear` in `[0, 1]`
- `committed-this-tick?`
- `was-retaliated-against-this-tick?`
- `reported-this-tick?`
- `was-punished-this-tick?`
- `retaliation-witnessed-this-tick?`
- `punishment-witnessed-this-tick?`

### 1.2 Global variables (`globals`)

- Structural constants:
  - `base-reporting-climate`
  - `observation-radius`
  - `punishment-witness-radius`
  - `retaliation-witness-radius`
  - `bystander-effect-factor`
  - `color-mode` (`"event"` or `"fear"`)
- Cumulative metrics:
  - `committed-misconduct-total`
  - `punished-misconduct-total`
  - `reported-events-total`
  - `retaliation-events-total`
  - `hidden-misconduct-total`
  - `hidden-misconduct-rate`
- Tick metrics:
  - `committed-misconduct-this-tick`
  - `punished-misconduct-this-tick`
  - `reported-events-this-tick`
  - `retaliation-events-this-tick`
  - `hidden-misconduct-this-tick`
  - `hidden-misconduct-rate-this-tick`
  - `committed-misconduct-prev-tick`
  - `relative-misconduct-change`

### 1.3 Helper reporters

- `clamp01(x) = max(0, min(1, x))`
- `logistic(x) = 1 / (1 + exp(-5 * x))`

## 2) Hardcoded constants

- `BASE-REPORTING-CLIMATE = 0.1`
- `OBSERVATION-RADIUS = 3`
- `PUNISHMENT-WITNESS-RADIUS = 6`
- `RETALIATION-WITNESS-RADIUS = 3`
- `BYSTANDER-EFFECT-FACTOR = 0.3`

## 3) Tick sequence

Each `go` tick runs:

1. Store previous misconduct level (`committed-misconduct-prev-tick`)
2. Reset per-tick counters
3. Move employees
4. Misconduct phase
5. Observation and reporting phase
6. Drift phase
7. Metrics update

## 4) Mathematical update rules

### 4.1 Misconduct decision

For each employee `i`:

- Commit if `u < misconduct-propensity_i`, with `u ~ Uniform(0,1)`

So:

- `P(commit_i) = misconduct-propensity_i`

### 4.2 Reporting

For each offender, one random witness is selected from employees in radius `3`.

Reporting input:

- `x_report = base-reporting-climate + 0.8 * reporter-protection - fear`

Reporting probability:

- `p_report = logistic(x_report) = 1 / (1 + exp(-5 * x_report))`

### 4.3 Sanctioning (automatic after each report)

Reported events are always sanctioned:

- `punished-misconduct-this-tick += 1`
- `punished-misconduct-total += 1`

Offender update:

- `misconduct-propensity <- clamp01(misconduct-propensity - learning-rate * (0.3 + 0.7 * punishment-severity) * (1.5 * reporter-protection - 0.5))`

Punishment bystander update (`radius = 6`):

- same term multiplied by `bystander-effect-factor`

### 4.4 Retaliation

Retaliation probability:

- `p_retaliation = clamp01(1 - reporter-protection)`

If retaliation occurs (on the reporting witness):

- `fear <- clamp01(fear + learning-rate * (0.2 + 0.8 * punishment-severity) * (1 - reporter-protection))`

Retaliation bystander update (`radius = 3`):

- same term multiplied by `bystander-effect-factor`

For retaliation bystanders, only fear is increased; `was-retaliated-against-this-tick?` is reserved for the directly affected reporter so that violet highlighting marks direct retaliation events.

### 4.5 Drift

If no misconduct this tick:

- `misconduct-propensity <- clamp01(misconduct-propensity + baseline-recovery-rate * (initial-misconduct-propensity - misconduct-propensity))`

If no retaliation this tick:

- `fear <- clamp01(fear + baseline-recovery-rate * (initial-fear - fear))`

## 5) Visual feedback

The `recolor-agent` helper supports two visualization modes. In `event` mode (default after `setup`), priority is direct retaliation (`cyan`) > direct report (`blue`) > direct sanction (`violet`) > direct misconduct (`red`) > neutral (`brown`). In `fear` mode, colors always follow fear (`green/yellow/orange`) regardless of event flags. The `toggle-color-mode` procedure switches the mode and immediately recolors all agents. Bystander color highlighting is currently commented out (disabled) even though bystander-effect fear dynamics remain in the model. All event flags are one-tick markers and are reset at the end of `drift-phase`, so highlights are short and interpretable.

## 6) Metric definitions

Per tick:

- `hidden-misconduct-this-tick = committed-misconduct-this-tick - punished-misconduct-this-tick`
- `hidden-misconduct-rate-this-tick = hidden-misconduct-this-tick / committed-misconduct-this-tick` if denominator > 0, else 0

Cumulative:

- `hidden-misconduct-total = committed-misconduct-total - punished-misconduct-total`
- `hidden-misconduct-rate = hidden-misconduct-total / committed-misconduct-total` if denominator > 0, else 0

Relative change:

- `relative-misconduct-change = ((committed-misconduct-this-tick - committed-misconduct-prev-tick) / committed-misconduct-prev-tick) * 100` if denominator > 0, else 0

Although the interface no longer exposes the tick-level monitors, these values continue to be calculated every tick to populate the two plots (`Per Tick Misconduct` and `Relative Misconduct Change (%)`).

## 7) Slider -> direct mathematical role

| Slider | Mathematical role |
|---|---|
| `number-employees` | Population size and event opportunity count |
| `initial-misconduct-propensity` | Initial value and drift target for propensity |
| `initial-fear` | Initial value and drift target for fear |
| `punishment-severity` | Scales sanction impact and retaliation fear impact |
| `reporter-protection` | Raises reporting input; lowers retaliation probability and retaliation fear term |
| `learning-rate` | Magnitude of sanction and retaliation shocks |
| `baseline-recovery-rate` | Mean-reversion speed toward initial values |

## 8) Embedded experiment defaults

The integrated BehaviorSpace experiments use:

- `timeLimit = 300`
- `repetitions = 10`
- common constants: `number-employees = 300`, `initial-misconduct-propensity = 0.4`, `initial-fear = 0.3`, `learning-rate = 0.2`, `baseline-recovery-rate = 0.05`

Policy parameters are either:

- stepped from `0` to `1` in increments of `0.1` (`exp1`, `exp2`), or
- fixed at `punishment-severity = 0.5`, `reporter-protection = 0.3` in one-factor sensitivity experiments (`exp3*`).

## 9) Convenience runs

The new `go-50` procedure repeats `go` exactly 50 times to quickly scan short runs without manually stopping the forever button. It simply encapsulates `repeat 50 [ go ]` and relies on the same tick-level bookkeeping and coloring logic described above.

# Variables, Sliders, and Tick Mathematics

This document describes the current model mathematics implemented in `Group5_Misconduct_ABM.nlogox` and mirrored in `Code.nls`.

## 1) Core Variables

### 1.1 Agent Variables (`employees-own`)

Each `employee` has:

- `misconduct-propensity` in `[0,1]`: probability of committing misconduct.
- `fear` in `[0,1]`: lowers reporting willingness.
- `committed-this-tick?`: whether misconduct was committed this tick.
- `retaliated-this-tick?`: whether retaliation was experienced this tick.

### 1.2 Global Counters (`globals`)

- `true-misconduct-total`
- `sanctioned-misconduct-total`
- `reported-events-total`
- `retaliation-events-total`
- `hidden-misconduct-total`
- `hidden-misconduct-rate`
- `true-misconduct-this-tick`
- `sanctioned-this-tick`
- `reported-events-this-tick`
- `retaliation-events-this-tick`
- `hidden-misconduct-this-tick`
- `hidden-misconduct-rate-this-tick`
- `true-misconduct-prev-tick`
- `relative-misconduct-change`

### 1.3 Helper Reporters

- `clamp01(x) = max(0, min(1, x))`
- `logistic(x) = 1 / (1 + exp(-5 * x))`

## 2) Hardcoded Constants

These values are fixed in code:

- `BASE-REPORTING-CLIMATE = 0.1`
- `OBSERVATION-RADIUS = 3`
- `PUNISHMENT-WITNESS-RADIUS = 6`
- `RETALIATION-WITNESS-RADIUS = 3`
- `BYSTANDER-EFFECT-FACTOR = 0.3`

## 3) Tick Sequence

Each `go` tick executes in this order:

1. Snapshot previous tick (`true-misconduct-prev-tick`)
2. Reset tick-level counters
3. Movement
4. Misconduct decision
5. Observation and reporting
6. Drift phase
7. Metric update

### 3.1 Movement

All agents move locally and randomly:

- `rt random 50`, `lt random 50`, `fd 1`

This changes local observation neighborhoods.

### 3.2 Misconduct Decision

For each agent `i`:

- Draw `u ~ Uniform(0,1)`
- Commit misconduct if `u < m_i(t)`, where `m_i(t) = misconduct-propensity_i(t)`

Therefore:

- `P(commit_i(t)=1) = m_i(t)`

On commit:

- `true-misconduct-this-tick += 1`
- `true-misconduct-total += 1`

### 3.3 Observation and Reporting

For each offender `j`:

- Witness set: `other employees in-radius 3`
- If witnesses exist: pick one random observer `k`

Reporting input:

`x_report = 0.1 + 0.8 * reporter-protection - fear_k`

Reporting probability:

`p_report = logistic(x_report) = 1 / (1 + exp(-5 * x_report))`

Compared to the previous version, reporting no longer includes an offender propensity term and now uses a steeper logistic curve.

If `u < p_report`:

- `reported-events-total += 1`
- `reported-events-this-tick += 1`

### 3.4 Sanctioning (after report)

Sanctioning is automatic for every report:

- `sanctioned-this-tick += 1`
- `sanctioned-misconduct-total += 1`

Offender update:

`misconduct-propensity_j = clamp01(misconduct-propensity_j - response-strength * (0.3 + 0.7 * punishment-value))`

Nearby bystanders (`radius = 6`) receive a smaller update:

`misconduct-propensity_w = clamp01(misconduct-propensity_w - response-strength * (0.3 + 0.7 * punishment-value) * 0.3)`

Interpretation:

- At `punishment-value = 0`: drop is `response-strength * 0.3`
- At `punishment-value = 1`: drop is `response-strength * 1.0`

### 3.5 Retaliation (after report)

Retaliation probability:

`p_ret = clamp01(1 - reporter-protection)`

If retaliation happens (observer `k`):

- `retaliation-events-total += 1`
- `retaliation-events-this-tick += 1`
- `retaliated-this-tick? = true`
- `fear_k = clamp01(fear_k + response-strength * (0.2 + 0.8 * punishment-value) * (1 - reporter-protection))`

Nearby bystanders (`radius = 3`) also receive fear increase:

`fear_w = clamp01(fear_w + response-strength * (0.2 + 0.8 * punishment-value) * (1 - reporter-protection) * 0.3)`

For these bystanders, `retaliated-this-tick?` is also set to true, preventing same-tick fear mean reversion.

### 3.6 Drift Phase

For each agent `i`:

1. **Misconduct propensity mean reversion** (if no commit this tick):

`m_i(t+1) = clamp01(m_i(t) + drift-speed * (initial-misconduct-propensity - m_i(t)))`

2. **Fear mean reversion** (if no retaliation this tick):

`fear_i(t+1) = clamp01(fear_i(t) + drift-speed * (initial-fear - fear_i(t)))`

`response-strength` controls event shocks (sanctioning/retaliation), while `drift-speed` controls recovery speed.

### 3.7 Metrics

Cumulative hidden misconduct:

`hidden-misconduct-total = true-misconduct-total - sanctioned-misconduct-total`

Rate:

- If `true-misconduct-total > 0`:
  - `hidden-misconduct-rate = hidden-misconduct-total / true-misconduct-total`
- Else:
  - `hidden-misconduct-rate = 0`

Relative tick-to-tick change:

- If `true-misconduct-prev-tick > 0`:
  - `relative-misconduct-change = ((true-misconduct-this-tick - true-misconduct-prev-tick) / true-misconduct-prev-tick) * 100`
- Else:
  - `relative-misconduct-change = 0`

Tick-level hidden misconduct metrics:

- `hidden-misconduct-this-tick = true-misconduct-this-tick - sanctioned-this-tick`
- If `true-misconduct-this-tick > 0`:
  - `hidden-misconduct-rate-this-tick = hidden-misconduct-this-tick / true-misconduct-this-tick`
- Else:
  - `hidden-misconduct-rate-this-tick = 0`

## 4) Slider -> Formula -> Effect

| Slider | Direct mathematical location | Main effect |
|---|---|---|
| `number-employees` | Population size `N` | More possible events per tick |
| `initial-misconduct-propensity` | Start value and mean-reversion target of `m_i` | Higher long-run baseline misconduct pressure |
| `initial-fear` | Start value and mean-reversion target of `fear_i` | Lower baseline reporting when higher |
| `punishment-value` | Sanction-induced propensity drop and retaliation-linked fear increase | Stronger sanctions and stronger retaliation pressure when higher |
| `reporter-protection` | Reporting input and retaliation probability/severity channel | Higher reporting and lower retaliation when higher |
| `response-strength` | Event-driven updates (sanction, retaliation) | Amplitude of single-event learning/shocks |
| `drift-speed` | Mean reversion in drift phase | Recovery speed toward baseline |

## 5) New BehaviorSpace Baseline Used by Integrated Experiments

The integrated experiments inside `.nlogox` use these common baseline constants:

- `number-employees = 200`
- `initial-misconduct-propensity = 0.4`
- `initial-fear = 0.3`
- `punishment-value = 0.66` (for OFAT baselines)
- `reporter-protection = 0.5` (for OFAT baselines)
- `response-strength = 0.2`
- `drift-speed = 0.15`
- `timeLimit = 300`
- `repetitions = 10`

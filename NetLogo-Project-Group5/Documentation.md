## WHAT IS IT?

This model simulates organisational misconduct in a fixed employee population.

The central question is:

**When does higher punishment reduce true misconduct — and when does it mainly increase fear and suppress reporting instead?**

Employees may commit misconduct, coworkers may observe and report it, every reported case is sanctioned automatically, and retaliation against reporters may follow. Retaliation feeds back into fear, which in turn suppresses future reporting. The model tracks how much misconduct stays hidden depending on the policy levers available to management.

---

## HOW IT WORKS

Each tick represents one abstract time period inside the organisation.

**1. Movement**
Employees move randomly within their local neighbourhood. This changes who can observe whom, introducing natural variation in observation opportunities.

**2. Misconduct Decision**
Each employee commits misconduct with a probability equal to their individual `misconduct-propensity`. This is a Bernoulli draw each tick.

**3. Observation**
Employees who committed misconduct are observed by coworkers within a fixed radius of 3 patches (hardcoded). A single random witness is selected per offender.

**4. Reporting Decision**
The witness decides whether to report using a logistic function:

`p_report = logistic(0.1 + 0.8 × reporter-protection − fear + 0.2 × offender-propensity)`

Higher protection and lower fear increase reporting probability. The constant 0.1 reflects a slightly positive baseline climate (hardcoded).

**5. Sanctioning — Automatic, Strength-Variable**
Every reported case is sanctioned without exception. The `punishment-value` slider controls the strength of the sanction: how much the offender's misconduct propensity drops.

`propensity_drop = response-strength × (0.3 + 0.7 × punishment-value)`

At `punishment-value = 0` the drop is `response-strength × 0.3`; at maximum it is `response-strength × 1.0`.

Punishment also has a **local bystander effect**: employees within `PUNISHMENT-WITNESS-RADIUS = 4` around the offender observe the sanction and reduce their own misconduct propensity by a smaller share:

`bystander_propensity_drop = response-strength × (0.3 + 0.7 × punishment-value) × 0.3`

**6. Retaliation**
After every report, retaliation against the reporter occurs with probability:

`p_retaliation = 1 − reporter-protection`

When retaliation happens, the reporter's fear increases:

`fear_increase = response-strength × (0.2 + 0.8 × punishment-value) × (1 − reporter-protection)`

Probability falls as protection rises. Retaliation severity rises with `punishment-value` and falls with `reporter-protection`.

Retaliation also has a **local bystander effect**: employees within `RETALIATION-WITNESS-RADIUS = 4` around the reporter observe retaliation and receive a smaller fear increase:

`bystander_fear_increase = response-strength × (0.2 + 0.8 × punishment-value) × (1 − reporter-protection) × 0.3`

Observed retaliation also sets the bystander's retaliation flag for the current tick, so this fear increase is not immediately offset by same-tick fear mean-reversion.

**7. Drift and Fear Decay**
In each tick's drift phase two things happen for every employee:

- **Misconduct propensity** mean-reverts toward its personal starting value (if no misconduct was committed this tick), at speed `drift-speed`. This prevents permanent collapse or runaway growth.
- **Fear mean-reverts** toward `initial-fear` when the employee was *not* retaliated against this tick:
  `fear_next = fear + drift-speed × (initial-fear − fear)`.
  Fear therefore moves back toward baseline in both directions, with speed controlled by `drift-speed` and current distance to baseline.

**Agent colours** reflect current fear level:
- 🟢 Green — fear below 0.33 (low)
- 🟡 Yellow — fear 0.33 – 0.65 (moderate)
- 🟠 Orange — fear 0.66 or above (high)

**Key output metric:**

`hidden-misconduct-rate = (true-misconduct-total − sanctioned-misconduct-total) / true-misconduct-total`

Because every reported case is sanctioned, hidden misconduct equals *unreported* misconduct. The rate measures how large a share of all actual misconduct management never sees.

---

## HOW TO USE IT

1. Click **setup** to initialise the population.
2. Click **go** (forever button) to run continuously.
3. Adjust the two main policy levers:
   - `punishment-value` — sanction strength and retaliation severity
   - `reporter-protection` — reduces retaliation probability and fear accumulation
4. Observe the three plots and the monitors.

**Recommended baseline settings:**

| Slider | Recommended default |
|---|---|
| number-employees | 150 |
| initial-misconduct-propensity | 0.25 |
| initial-fear | 0.35 |
| punishment-value | 0.70 |
| reporter-protection | 0.45 |
| response-strength | 0.20 |
| drift-speed | 0.05 |

---

## PLOTS AND MONITORS

Three plots are provided. All three show complementary perspectives on the same underlying dynamics and can be used in parallel for policy experiments.

**Misconduct Dynamics (Cumulative)**
Shows running totals of true, sanctioned, and hidden misconduct over all ticks. Useful for long-run comparisons across different parameter settings. The gap between the true and sanctioned curves is hidden misconduct.

**Per Tick Misconduct**
Shows the flow rate each tick: how many misconduct events, sanctions, and hidden events occurred in the most recent period. This is the most responsive plot — policy changes show up here first, before the cumulative curves react visibly.

**Relative Misconduct Change (%)**
Shows the percentage change in true misconduct from the previous tick, like a stock price chart. A value of zero means no change; positive values mean misconduct is rising; negative values mean it is falling. Oscillation around zero indicates a stable equilibrium. Useful for comparing whether punishment or protection produces a faster downward trend.

**Key monitors to watch:**

| Monitor | What it tells you |
|---|---|
| Hidden misconduct rate (total) | The core policy outcome: share of misconduct that stays invisible over the full run |
| Retaliation events (total) | Total retaliation load over the full run |
| Reported events (tick) | Real-time number of reports in the current period |
| Retaliation events (tick) | Real-time retaliation load in the current period |
| True misconduct (tick) | Real-time pulse of misconduct activity |
| Hidden misconduct (tick) | Unseen misconduct in the current period (`true - sanctioned`) |
| Hidden misconduct rate (tick) | Share of current-period misconduct that stayed hidden |
| Relative change (%) | Momentum: is misconduct currently growing or shrinking? |

---

## THINGS TO NOTICE

- Increasing `punishment-value` alone does not necessarily reduce true misconduct. Stronger punishment also intensifies retaliation severity after reporting, so low `reporter-protection` can still push fear up and suppress reporting.
- `reporter-protection` operates on two channels simultaneously: it raises reporting probability *and* reduces both the probability and severity of retaliation. It is the more powerful single lever in this model.
- Agents start mostly green or yellow (low/moderate fear). Orange agents only appear after repeated retaliation experiences. If fear is high at baseline and agents are already orange at tick 1, lower `initial-fear` or raise `reporter-protection`.
- The per-tick plot is noisy by design — it reflects the stochastic nature of individual decisions. Smooth trends are only visible over many ticks.

---

## THINGS TO TRY

**1. Protection sweep**
Set `punishment-value = 0.70` (fixed). Run three scenarios: `reporter-protection` at 0.10, 0.45, and 0.90. Compare hidden-misconduct-rate after 200 ticks. Observe how retaliation events and fear levels differ.

**2. Punishment sweep**
Set `reporter-protection = 0.45` (fixed). Run three scenarios: `punishment-value` at 0.20, 0.50, and 0.90. Notice that higher punishment does not always lower hidden-misconduct-rate.

**3. Fear trap**
Set `reporter-protection = 0.05`. Run 100 ticks until fear is high across the population. Then raise protection to 0.80. Observe the recovery lag: it takes time for fear to decay and reporting to recover, even after protection improves.

**4. Learning-rate sensitivity**
Keep all other sliders at default. Compare `response-strength = 0.05` vs `response-strength = 0.40`. Fast learners respond strongly to each sanction or retaliation; slow learners average out experience over time and are more resistant to short-term shocks.

---

## HARDCODED CONSTANTS

The following parameters are fixed in the code and not exposed as sliders:

| Constant | Value | Meaning |
|---|---|---|
| BASE-REPORTING-CLIMATE | 0.1 | Baseline logit offset for reporting — slightly positive culture |
| OBSERVATION-RADIUS | 3 patches | Fixed neighbourhood for witness selection |
| PUNISHMENT-WITNESS-RADIUS | 4 patches | Radius in which others observe punishment and adapt propensity |
| RETALIATION-WITNESS-RADIUS | 4 patches | Radius in which others observe retaliation and adapt fear |
| BYSTANDER-EFFECT-FACTOR | 0.3 | Scales indirect punishment/retaliation effects on nearby agents |

---

## EXTENDING THE MODEL

- Add explicit departments with local trust and norm variables.
- Add compliance capacity limits: finite case-processing capacity and a growing backlog.
- Add anonymity and evidence-quality trade-off in the reporting decision.
- Add heterogeneous roles: employees, managers, and dedicated compliance officers with different propensities and observation radii.
- Introduce warning stages before full sanction (progressive discipline).
- Track average fear across the population as a persistent monitor to visualise chilling effect over time.

---

## NETLOGO FEATURES

- One breed (`employees`) with evolving internal attributes.
- Local interaction via `in-radius` for witness selection.
- Logistic reporting function for nonlinear probability.
- Bernoulli misconduct events drawn each tick.
- Learning-rate-coupled fear dynamics (both rise and decay).
- Three synchronised plots for policy comparison across runs.

---

## CREDITS AND REFERENCES

Project concept and model structure:
- Group 5 presentation: *Agent-Based Simulation of Organisational Misconduct*

NetLogo references:
- [NetLogo Tutorial #1: Models](https://docs.netlogo.org/tutorial1)
- [Beginner's Interactive NetLogo Dictionary (BIND)](https://bind.netlogo.org)

## WHAT IS IT?

This model simulates organizational misconduct in a fixed employee population.  
It focuses on one central question:

**Under what conditions does stricter enforcement reduce true misconduct, and when does it mostly reduce visible misconduct only?**

The model is based on the Group 5 presentation concept:
- employees may commit misconduct,
- misconduct may be observed,
- observers may report,
- reported misconduct may be sanctioned,
- retaliation may occur and increase fear.

## HOW IT WORKS

Each tick represents one abstract time step in an organization.

1. **Movement**: employees move and mix locally.
2. **Misconduct decision**: each employee may commit misconduct with probability linked to `misconduct-propensity`.
3. **Observation**: nearby coworkers may observe misconduct.
4. **Reporting**: an observer decides to report based on fear, reporting climate, protection, and offender profile.
5. **Sanctioning**: reported cases are sanctioned with probability influenced by `enforcement-strictness`.
6. **Retaliation**: if a report occurs, retaliation can happen depending on baseline retaliation risk, protection, and enforcement.
7. **Feedback**: fear and misconduct propensity evolve over time; output metrics are updated.

The core outcome is:

`hidden-misconduct-rate = (true-misconduct-total - sanctioned-misconduct-total) / true-misconduct-total`

## HOW TO USE IT

1. Click `setup`.
2. Click `go` to run continuously.
3. Change policy sliders:
   - `enforcement-strictness`
   - `reporter-protection`
4. Observe monitors and plot trajectories:
   - true misconduct
   - sanctioned misconduct
   - hidden misconduct
   - hidden misconduct rate

Recommended baseline:
- medium-high enforcement (`~0.7`)
- medium protection (`~0.45`)
- medium fear (`~0.35`)

## THINGS TO NOTICE

- Stronger enforcement can reduce sanctioned offenders' incentives, but can also alter retaliation pressure.
- Lower protection can increase fear, which may suppress reporting.
- Hidden misconduct may increase even when visible sanctions look stable.

## THINGS TO TRY

1. **Protection sweep**: keep enforcement fixed, vary `reporter-protection` from low to high.
2. **Enforcement sweep**: keep protection fixed, vary `enforcement-strictness`.
3. **Combined policy**: vary both and compare hidden-misconduct-rate after the same number of ticks.
4. **Climate sensitivity**: test pessimistic vs optimistic `base-reporting-climate`.

## EXTENDING THE MODEL

Potential iterative extensions (also aligned with your project notes):
- Add explicit departments with local trust/norm variables.
- Add compliance backlog and finite case-processing capacity.
- Add evidence quality and anonymity trade-off.
- Introduce heterogeneous roles (employees, managers, compliance officers).
- Track warning stages before full sanction.

## NETLOGO FEATURES

- Uses one breed (`employees`) with evolving internal attributes.
- Uses local interaction via `in-radius` for observation logic.
- Uses probabilistic decision rules and logistic-style reporting decisions.
- Uses monitors and plots for policy comparison across runs.

## RELATED MODELS

- NetLogo models involving social norms and diffusion processes in organizations.
- Predator-prey style feedback models are structurally helpful for thinking about reinforcing loops.

## CREDITS AND REFERENCES

Project context and conceptual structure:
- Group 5 presentation: *Agent-Based Simulation of Organisational Misconduct*.

NetLogo references used for model structure and interface conventions:
- [NetLogo Tutorial #1: Models](https://docs.netlogo.org/tutorial1)
- [Beginner's Interactive NetLogo Dictionary (BIND)](https://bind.netlogo.org)

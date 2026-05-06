# Option F Formula Rationale (short note)

## Formula used in `Experiments-06-05-ABM-F.nlogox`

In the sanction update block (offender and punishment witnesses), misconduct propensity is updated by:

```text
Δmisconduct = - learning-rate * punishment-severity * (
  reporter-protection * (1 + punishment-severity) / 2
  - 0.8 * punishment-severity * (1 - reporter-protection)
)
```

## Why this structure?

The formula combines two opposing mechanisms:

1. **Deterrence channel (negative term)**  
   `reporter-protection * (1 + punishment-severity) / 2`  
   - Stronger protection increases credible reporting and therefore expected sanction impact.  
   - Punishment enters again as a signal-amplifier (`(1 + P)/2`), so high sanctions can have stronger marginal deterrence.

2. **Backlash / fear-trap channel (positive counterforce inside bracket)**  
   `0.8 * punishment-severity * (1 - reporter-protection)`  
   - If protection is weak, harsher punishment can increase concealment pressure, perceived unfairness, or reactance.  
   - This weakens (or can locally reverse) deterrence, creating flat or upward segments in some mechanism curves.

## Main levers and what they do

- `learning-rate`: global speed of behavioral adaptation.
- `punishment-severity`:
  - increases deterrence,
  - but also increases backlash under low protection.
- `reporter-protection`:
  - strengthens deterrence,
  - suppresses backlash via `(1 - reporter-protection)`.
- `0.8` (backlash coefficient):
  - calibration lever for nonlinearity and fear-trap strength,
  - higher values produce more flattening / upward bends at low protection.

## What this enables in plots

Compared with purely monotonic deterrence formulas, Option F can produce:

- mostly downward curves for medium/high protection,
- but flat or partially upward curves for low protection at high punishment,
- stronger nonlinearity in heatmaps (instead of near-linear gradients),
- clearer separation between "Iron Fist" and "Safe Harbor" policy archetypes.

## How to justify empirically

Use existing outputs (`exp1_heatmaps`, `exp1_mechanism`, `exp1_archetypes`, `exp2_pareto`) and report:

1. **Mechanism evidence**: Identify specific protection levels where slope changes from negative to near-zero/positive at high punishment.
2. **Fear-trap evidence**: Show policy cells with low hidden misconduct reduction but elevated fear/retaliation under low protection + high punishment.
3. **Archetype contrast**: Compare `Iron Fist (high P, low R)` vs `Safe Harbor (low P, high R)` on hidden misconduct and retaliation.
4. **Robustness**: Repeat with different seeds/replications and confirm the pattern is not noise.

## Conceptual references (for framing, not strict structural estimation)

- Near & Miceli: expected-utility logic in whistleblowing.
- Dozier & Miceli (1985): retaliation risk and reporting context.
- Mesmer-Magnus & Viswesvaran (2005): antecedents of whistleblowing/reporting behavior.
- Sherman (1993) Defiance Theory: sanctions can backfire under perceived illegitimacy/low fairness.


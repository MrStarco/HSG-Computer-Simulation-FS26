# Changelog — Changes Since Last Commit

## Overview

This document summarises all model and documentation changes made after the last Git commit (`09caf65 Analysis Stuff Joel`). The changes fall into five areas: bystander observation radii, fear dynamics, parameter separation, utility removal, and calibration.

---

## 1. Bystander Observation Radius for Punishment

**What:** When a reported offender is sanctioned, nearby agents within a radius of 4 patches around the offender also reduce their `misconduct-propensity` slightly.

**Formula:** `propensity_drop_bystander = response-strength × (0.3 + 0.7 × punishment-value) × 0.3`

**Why:** In reality, employees do not learn exclusively from their own experiences. Witnessing a colleague get sanctioned creates a deterrent effect even for those not directly involved. The 0.3 scaling factor keeps this indirect effect smaller than the direct sanction.

**New hardcoded constant:** `PUNISHMENT-WITNESS-RADIUS = 4` (slightly larger than the misconduct observation radius of 3).

---

## 2. Bystander Observation Radius for Retaliation

**What:** When retaliation occurs against a reporter, nearby agents within a radius of 4 patches around the reporter also receive a smaller fear increase. Their `retaliated-this-tick?` flag is set to `true`, preventing same-tick fear mean-reversion from immediately cancelling the effect.

**Formula:** `fear_increase_bystander = response-strength × (0.2 + 0.8 × punishment-value) × (1 − reporter-protection) × 0.3`

**Why:** Witnessing a colleague being retaliated against for reporting is a chilling signal. Bystanders rationally update their own willingness to report even without being targeted themselves. The flag ensures the fear increase persists into the next tick rather than being erased by drift in the same step.

**New hardcoded constant:** `RETALIATION-WITNESS-RADIUS = 4`.

---

## 3. Fear Decay — Changed to Mean-Reversion Toward `initial-fear`

**What:** Fear no longer uses a flat decay rate (`fear − constant`). It now mean-reverts toward `initial-fear`:

```
fear_next = fear + drift-speed × (initial-fear − fear)
```

**Why:** The old flat decay was directional only downward. The new formula is symmetric: fear above `initial-fear` decays toward it; fear below `initial-fear` recovers toward it. This mirrors exactly how `misconduct-propensity` already worked, making the model internally consistent.

---

## 4. Separation of `response-strength` and `drift-speed` — The Core Fix

**The problem:** Previously a single parameter (`learning-rate`) controlled both (a) how strongly an agent reacts to an event such as a sanction or retaliation, and (b) how quickly they recover back to baseline between events. These are conceptually different phenomena and should not be locked to the same value.

With `learning-rate = 0.2`, the model was snapping back to baseline in roughly **5 ticks** — the same speed as the initial shock. This made the simulation unrealistically volatile and difficult to interpret.

**The fix — two separate parameters:**

| Parameter | Controls | Default |
|---|---|---|
| `response-strength` | Magnitude of event-driven changes (sanction propensity drop, retaliation fear spike, bystander effects) | 0.20 |
| `drift-speed` | Speed of mean-reversion back to baseline between events | 0.05 |

**Why this matters:**

- `response-strength = 0.20` means a sanction causes a propensity drop of ~0.16 in one event — noticeable but not permanent.
- `drift-speed = 0.05` means recovery takes roughly **14 ticks** to close half the distance to baseline (half-life = ln(2) / 0.05 ≈ 14 ticks), and ~40 ticks to fully stabilise.
- This creates a realistic asymmetry: shocks are felt quickly, recovery is slow — consistent with how behavioural change and fear actually operate in organisations.

**Why `learning-rate` was renamed to `response-strength`:** With drift now handled by a separate parameter, "learning rate" was no longer accurate. The remaining parameter exclusively controls how strongly an agent responds to a single event, making `response-strength` the correct descriptor.

---

## 5. Utility Variable Removed

**What:** The `utility` agent variable and all associated update lines (`+1.4` for misconduct, `−1.2` for retaliation) have been fully removed from the model.

**Why:** `utility` was tracked but never read by any plot, monitor, or reporter. It had no effect on agent behaviour or model outputs. Keeping an unused variable adds maintenance overhead and misleads readers of the code. Removing it makes the agent state cleaner and the model easier to understand.

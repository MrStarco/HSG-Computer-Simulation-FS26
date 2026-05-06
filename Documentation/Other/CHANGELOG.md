# Temporary changelog

> **Range:** `8e2b780d8e701dc78b9dfb7a20d9d14c1c8fb2b9` (before) → `28598e56e69e05d74e564f257984e5f9de357c3a` (after)  
> **Note:** This file is temporary; delete or replace when a formal changelog is no longer needed.

## Commits

| Commit     | Message |
| ---------- | ------- |
| `28598e56` | Interface and colouring of agents changed |

**Author / date (28598e56):** MrStarco, 2026-05-04 22:40 +0200

## Files changed

| File | Change (short) |
| ---- | -------------- |
| `NetLogo-Project-Group5/Code.nls` | Color mode, per-tick event flags, `recolor-agent`, `go-50`, `toggle-color-mode` |
| `NetLogo-Project-Group5/Group5_Misconduct_ABM.nlogox` | Same model logic + interface (buttons, layout, plots, monitors) |
| `NetLogo-Project-Group5/Documentation.md` | Visual cues section, monitor/plot description updates, how-to-run |
| `NetLogo-Project-Group5/Interface.md` | Restructured spec: new buttons, color semantics, fewer monitors, two plots, deduplicated content |
| `NetLogo-Project-Group5/Variable_Slider_Tick_Math.md` | Aligned with variable/slider/tick behavior changes |

**Stats:** 5 files, +215 / −243 lines (per `git diff --stat`).

## Summary of behavior and UI

### Model / visualization

- **Global `color-mode`:** `"event"` (default after `setup`) or `"fear"`.
- **Event-mode colors:** direct events per tick — e.g. misconduct (`red`), report (`blue`), retaliation experienced (`cyan`), sanctioned offender (`violet`); agents without a direct event use `brown`. Optional bystander highlights are present in code but commented out.
- **Fear mode:** all agents colored by fear only (green → yellow → orange) via existing `recolor-from-fear`.
- **New procedures:** `recolor-agent` (dispatcher), `go-50` (repeat `go` 50 times), `toggle-color-mode`.
- **New per-agent tick flags:** `reported-this-tick?`, `sanctioned-this-tick?`, `retaliation-witnessed-this-tick?`, `sanction-witnessed-this-tick?` (latter two wired in places but witness toggles are commented in the reporting flow where applicable).
- **Drift phase:** calls `recolor-agent` then clears the new tick flags with the existing ones.

### NetLogo interface

- New buttons: **`go-50`**, **`switch color mode`** (`toggle-color-mode`).
- **Monitors:** tick-level monitors removed; sidebar focuses on **total** metrics (true, sanctioned, hidden, hidden rate, reported, retaliation totals). Per-tick values still drive plots.
- **Plots:** cumulative **Misconduct Dynamics** plot removed; **Relative Misconduct Change (%)** and **Per Tick Misconduct** remain.
- **Layout:** left column sliders + controls (including color switch); right column totals + legend note; bottom-right plot area.

### Documentation

- **Documentation.md:** “Visual cues” section, updated interpretation of hidden misconduct vs monitors, plot list and rationale, extended “How to run” with `go-50` and color toggle.
- **Interface.md:** single consolidated spec, color legend semantics, renumbered sections (hardcoded constants, BehaviorSpace), removed duplicate trailing copy and the old “Experiment analysis assets / manual setup / recommended layout” block in favor of a leaner structure.

---

*Generated from `git log` and `git diff` for the commit range above.*

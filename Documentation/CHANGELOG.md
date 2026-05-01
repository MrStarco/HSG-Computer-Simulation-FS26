# Changelog — Since `472b0a6082238d1c6aeb2d4113ece7fd43fe5447`

---

## 1) Model File Replacement and Experiment Integration

- Replaced `NetLogo-Project-Group5/Group5_Misconduct_ABM.nlogox` with the new `Group5_Misconduct_ABM_EXPERIMENTS_V1` version shared by teammates.
- Integrated built-in BehaviorSpace experiment suites directly in the `.nlogox` model:
  - `exp1_policy_grid`
  - `exp2_stakeholder_pareto`
  - `exp3a_sens_employees`
  - `exp3b_sens_init_propensity`
  - `exp3c_sens_init_fear`
  - `exp3d_sens_response_strength`
  - `exp3e_sens_drift_speed`

## 2) Model Logic and Parameters (Current Integrated Version)

- Reporting input was simplified to:
  - `0.1 + 0.8 * reporter-protection - fear`
- Logistic steepness was updated to:
  - `logistic(x) = 1 / (1 + exp(-5 * x))`
- Existing sanction/retaliation bystander effects remain part of the model:
  - punishment bystanders in radius `6`
  - retaliation bystanders in radius `3`

## 3) Analysis Pipeline Added to Repository

- Added experiment analysis script:
  - `NetLogo-Project-Group5/Experiments/analyze_all_experiments.py`
- Added sample output figures:
  - `NetLogo-Project-Group5/Experiments/Sample Output Plots/exp1_heatmaps.png`
  - `NetLogo-Project-Group5/Experiments/Sample Output Plots/exp1_mechanism.png`
  - `NetLogo-Project-Group5/Experiments/Sample Output Plots/exp2_dynamics.png`
  - `NetLogo-Project-Group5/Experiments/Sample Output Plots/exp2_pareto.png`
  - `NetLogo-Project-Group5/Experiments/Sample Output Plots/exp3_sensitivity.png`

## 4) Documentation Synchronization

Updated the following manual documentation files to reflect the integrated model and experiment workflow:

- `NetLogo-Project-Group5/Interface.md`
- `NetLogo-Project-Group5/Variable_Slider_Tick_Math.md`
- `NetLogo-Project-Group5/Documentation.md`
- `NetLogo-Project-Group5/Code.nls` (synchronized with embedded model code)

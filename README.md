# Misconduct ABM — Group 5

Agent-based model of organizational misconduct, reporting, and hidden misconduct dynamics.
Built in NetLogo 7.0.3. Submitted as part of the Computer Simulation course (FS26) at the University of St. Gallen.

## Research question

How do parameters such as punishment severity and reporter protection affect misconduct dynamics?

## Model files


| File                                                  | Purpose                                                           |
| ----------------------------------------------------- | ----------------------------------------------------------------- |
| `NetLogo-Project-Group5/Group5_Misconduct_ABM.nlogox` | Complete model — open this in NetLogo                             |
| `NetLogo-Project-Group5/data_analysis_jupyter.ipynb`  | Jupyter notebook for analyzing experiment outputs                 |
| `NetLogo-Project-Group5/data_analysis_script.py`      | Python script for reproducible data analysis and plotting         |
| `NetLogo-Project-Group5/data_sets/`                   | Input/output CSV datasets used by the analysis workflow           |
| `NetLogo-Project-Group5/Sample plots/`                | Example figures generated from experiment results                 |
| `NetLogo-Project-Group5/Additional-Documentation/`    | Supporting model documentation (code, interface, math, and notes) |


## How to run

1. Open `NetLogo-Project-Group5/Group5_Misconduct_ABM.nlogox` in NetLogo 7.0.3.
2. Click `setup` to initialize agents.
3. Click `go` to run continuously, or `go-50` to advance exactly 50 ticks.
4. Use `switch color mode` to toggle between event highlighting and fear visualization.
5. For experiments: `Tools → BehaviorSpace`, select an experiment, run, export CSV.
6. Place the exported CSV files in the same directory as `data_analysis_script.py` or a subfolder "data_sets"  before running the analysis script.

## Key sliders


| Slider                          | Range    | Default | Role                                                  |
| ------------------------------- | -------- | ------- | ----------------------------------------------------- |
| `number-employees`              | 20–400   | 250     | Population size                                       |
| `initial-misconduct-propensity` | 0–1      | 0.30    | Starting propensity and drift target                  |
| `initial-fear`                  | 0–1      | 0.35    | Starting fear and drift target                        |
| `punishment-severity`           | 0–1      | 1.00    | Scales sanction and retaliation impacts               |
| `reporter-protection`           | 0–1      | 0.30    | Raises reporting probability; lowers retaliation risk |
| `learning-rate`                 | 0–1      | 0.20    | Magnitude of per-event shocks                         |
| `baseline-recovery-rate`        | 0.01–0.5 | 0.15    | Mean-reversion speed to initial values                |


## Output monitors

- **Committed misconduct (total)** — cumulative committed events
- **Punished misconduct (total)** — cumulative punished events
- **Hidden misconduct (total)** — committed minus sanctioned (= unreported)
- **Hidden misconduct rate (total)** — hidden / committed
- **Reported events (total)**, **Retaliation events (total)**

## Plots

- **Per Tick Misconduct** — committed, punished, and hidden counts per tick
- **Relative Misconduct Change (%)** — tick-over-tick momentum indicator

## Repository structure

```
HSG-Computer-Simulation-FS26/
├── README.md
├── Context/
│   ├── Lecture-content/                          # Course lecture slides (reference)
│   ├── Presentation-Slides/                      # Group 5 presentation decks
│   └── Additional-Justification-and-Documentation/  # Parameter justification and notes
└── NetLogo-Project-Group5/
    ├── Group5_Misconduct_ABM.nlogox        # Main model file (submit this)
    ├── data_analysis_script.py             # Data analysis script (legacy)
    ├── data_analysis_jupyter.ipynb         # Data analysis notebook (legacy)
    ├── Additional-Documentation/
    │   ├── Code.nls                        # Source code reference
    │   ├── Documentation.md                # Info tab text
    │   ├── Interface.md                    # Interface specification
    │   └── Variable_Slider_Tick_Math.md    # Mathematical reference
    ├── data_sets/                          # BehaviorSpace CSV exports (final run)
    ├── Sample plots/                       # Output plots from final analysis
    └── Experiments/                        # Archived intermediate experiment runs
```

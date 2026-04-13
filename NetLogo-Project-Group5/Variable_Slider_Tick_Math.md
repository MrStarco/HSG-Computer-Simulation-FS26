# Variablen-, Slider- und Tick-Mathematik Dokumentation

Dieses Dokument beschreibt die Mathematik der aktuellen Modellimplementierung und die Wirkung der aktiven Slider.

## 1) Kernvariablen

### 1.1 Agent-Variablen (`employees-own`)

Jeder `employee` besitzt:

- `misconduct-propensity` in `[0,1]`: individuelle Wahrscheinlichkeit fuer Fehlverhalten.
- `fear` in `[0,1]`: senkt die Wahrscheinlichkeit, Fehlverhalten zu melden.
- `utility`: akkumuliert Nutzen/Kosten aus Ereignissen.
- `committed-this-tick?`: Flag, ob der Agent im aktuellen Tick Fehlverhalten begangen hat.
- `retaliated-this-tick?`: Flag, ob der Agent im aktuellen Tick Vergeltung erlebt hat.

### 1.2 Globale Zaehler (`globals`)

- `true-misconduct-total`
- `sanctioned-misconduct-total`
- `reported-events-total`
- `retaliation-events-total`
- `hidden-misconduct-total`
- `hidden-misconduct-rate`
- `true-misconduct-this-tick`
- `sanctioned-this-tick`
- `true-misconduct-prev-tick`
- `relative-misconduct-change`

### 1.3 Hilfsfunktionen

- `clamp01(x) = max(0, min(1, x))`
- `logistic(x) = 1 / (1 + exp(-x))`

## 2) Hardcoded Modellkonstanten

Diese Werte sind fest im Code hinterlegt:

- `BASE-REPORTING-CLIMATE = 0.1`
- `OBSERVATION-RADIUS = 3`
- `RETALIATION-COST = 1.2`

## 3) Tick-Ablauf (in Reihenfolge)

Pro Tick laeuft `go` in dieser Sequenz:

1. Snapshot des letzten Tick-Werts (`true-misconduct-prev-tick`)
2. Reset von Tick-Zaehlern
3. Bewegung
4. Fehlverhaltens-Entscheid
5. Beobachtung und Reporting
6. Drift-Phase
7. Metrik-Update

### 3.1 Bewegung

Alle Agenten bewegen sich lokal zufaellig:

- Drehung und Vorwaertsbewegung (`rt random 50`, `lt random 50`, `fd 1`)

Dadurch veraendert sich die lokale Nachbarschaft fuer Beobachtung.

### 3.2 Fehlverhalten

Fuer jeden Agenten `i`:

- Ziehe `u ~ Uniform(0,1)`
- Wenn `u < m_i(t)` mit `m_i(t) = misconduct-propensity_i(t)`, dann commitet Agent `i`

Also:

- `P(commit_i(t)=1) = m_i(t)`

Bei Commit:

- `true-misconduct-this-tick += 1`
- `true-misconduct-total += 1`
- `utility_i += misconduct-gain`

### 3.3 Beobachtung und Reporting

Fuer jeden Offender `j`:

- Witness-Menge: `other employees in-radius 3`
- Falls Witness vorhanden: waehle zufaellig einen Beobachter `k`

Reporting-Input:

`x_report = 0.1 + 0.8 * reporter-protection - fear_k + 0.2 * misconduct-propensity_j`

Reporting-Wahrscheinlichkeit:

`p_report = logistic(x_report)`

Wenn `u < p_report`:

- `reported-events-total += 1`

### 3.4 Sanktionierung (bei Report)

Sanktionierung erfolgt bei jedem Report automatisch:

- `sanctioned-this-tick += 1`
- `sanctioned-misconduct-total += 1`

Update fuer den Offender `j`:

`misconduct-propensity_j = clamp01(misconduct-propensity_j - learning-rate * (0.3 + 0.7 * punishment-value))`

Interpretation:

- Bei `punishment-value = 0`: Absenkung um `learning-rate * 0.3`
- Bei `punishment-value = 1`: Absenkung um `learning-rate * 1.0`

### 3.5 Retaliation (nach Report)

Retaliationswahrscheinlichkeit:

`p_ret = clamp01(1 - reporter-protection)`

Wenn Retaliation eintritt (beim Beobachter `k`):

- `retaliation-events-total += 1`
- `retaliated-this-tick? = true`
- `fear_k = clamp01(fear_k + learning-rate * 0.5 * (1 - reporter-protection))`
- `utility_k -= 1.2`

### 3.6 Drift-Phase

Fuer jeden Agenten `i`:

1. **Mean-Reversion der Fehlverhaltensneigung** (nur wenn kein Commit in diesem Tick):

`m_i(t+1) = clamp01(m_i(t) + learning-rate * (initial-misconduct-propensity - m_i(t)))`

2. **Fear-Decay** (nur wenn keine Retaliation in diesem Tick):

`fear_i(t+1) = clamp01(fear_i(t) - learning-rate * 0.03)`

Damit ist Fear eventgetrieben nach oben und ohne neues Ereignis langsam ruecklaeufig.

### 3.7 Metriken

Kumulierte Hidden-Misconduct:

`hidden-misconduct-total = true-misconduct-total - sanctioned-misconduct-total`

Rate:

- Wenn `true-misconduct-total > 0`:
  - `hidden-misconduct-rate = hidden-misconduct-total / true-misconduct-total`
- sonst:
  - `hidden-misconduct-rate = 0`

Relative Tick-zu-Tick-Aenderung:

- Wenn `true-misconduct-prev-tick > 0`:
  - `relative-misconduct-change = ((true-misconduct-this-tick - true-misconduct-prev-tick) / true-misconduct-prev-tick) * 100`
- sonst:
  - `relative-misconduct-change = 0`

## 4) Slider -> Formel -> Wirkung

| Slider | Direkter mathematischer Ort | Haupteffekt |
|---|---|---|
| `number-employees` | Populationsgroesse `N` | Mehr Agenten erzeugen mehr potenzielle Ereignisse pro Tick |
| `initial-misconduct-propensity` | Startwert von `m_i`; Zielwert der Mean-Reversion | Hoeheres langfristiges Baseline-Niveau fuer Fehlverhalten |
| `initial-fear` | Startwert von `fear_i` | Niedrigere Anfangs-Reportingbereitschaft bei hohem Wert |
| `punishment-value` | Absenkung von `misconduct-propensity` nach Sanktion | Staerkere Reduktion der Offender-Neigung bei hohem Wert |
| `reporter-protection` | Reporting-Input, `p_ret`, Fear-Anstieg bei Retaliation | Mehr Reporting und weniger Retaliation/Fear-Anstieg |
| `misconduct-gain` | `utility += misconduct-gain` bei Commit | Erhoeht unmittelbaren Nutzen aus Fehlverhalten |
| `learning-rate` | Updates von Propensity und Fear | Steuert Geschwindigkeit aller Anpassungsprozesse |

## 5) Dynamik ueber viele Ticks (Intuition)

### 5.1 Erwartete Fehlverhalten pro Tick

`E[true-misconduct-this-tick | t] = Sum_i m_i(t)`

Das ist der zentrale Input fuer Reporting, Sanktionen und Hidden-Misconduct.

### 5.2 Nichtlineares Reporting

Durch `p_report = logistic(x_report)` wirken kleine Aenderungen in `x_report` besonders stark im mittleren Bereich und schwach in den Saettigungsbereichen nahe 0 oder 1.

### 5.3 Gekoppelte Fear-Dynamik

Fear bewegt sich in beide Richtungen:

- nach oben bei Retaliation (eventbasiert),
- nach unten ohne Retaliation (langsamer Decay).

Damit entsteht eine realistischere Erholungsdynamik statt dauerhaftem Drift nach oben.

### 5.4 Hidden-Misconduct als Policy-Zielgroesse

`hidden-misconduct-rate = 1 - sanctioned-misconduct-total / true-misconduct-total`

Die Rate sinkt nur, wenn sanktionierte Faelle langfristig mit den tatsaechlichen Faellen Schritt halten.

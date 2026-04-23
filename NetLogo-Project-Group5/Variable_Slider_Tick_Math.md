# Variablen-, Slider- und Tick-Mathematik Dokumentation

Dieses Dokument beschreibt die Mathematik der aktuellen Modellimplementierung und die Wirkung der aktiven Slider.

## 1) Kernvariablen

### 1.1 Agent-Variablen (`employees-own`)

Jeder `employee` besitzt:

- `misconduct-propensity` in `[0,1]`: individuelle Wahrscheinlichkeit fuer Fehlverhalten.
- `fear` in `[0,1]`: senkt die Wahrscheinlichkeit, Fehlverhalten zu melden.
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
- `reported-events-this-tick`
- `retaliation-events-this-tick`
- `hidden-misconduct-this-tick`
- `hidden-misconduct-rate-this-tick`
- `true-misconduct-prev-tick`
- `relative-misconduct-change`

### 1.3 Hilfsfunktionen

- `clamp01(x) = max(0, min(1, x))`
- `logistic(x) = 1 / (1 + exp(-x))`

## 2) Hardcoded Modellkonstanten

Diese Werte sind fest im Code hinterlegt:

- `BASE-REPORTING-CLIMATE = 0.1`
- `OBSERVATION-RADIUS = 3`
- `PUNISHMENT-WITNESS-RADIUS = 6`
- `RETALIATION-WITNESS-RADIUS = 3`
- `BYSTANDER-EFFECT-FACTOR = 0.3`

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

`misconduct-propensity_j = clamp01(misconduct-propensity_j - response-strength * (0.3 + 0.7 * punishment-value))`

Zusatz fuer Beobachter im `PUNISHMENT-WITNESS-RADIUS` um den Offender:

`misconduct-propensity_w = clamp01(misconduct-propensity_w - response-strength * (0.3 + 0.7 * punishment-value) * 0.3)`

Interpretation:

- Bei `punishment-value = 0`: Absenkung um `response-strength * 0.3`
- Bei `punishment-value = 1`: Absenkung um `response-strength * 1.0`

### 3.5 Retaliation (nach Report)

Retaliationswahrscheinlichkeit:

`p_ret = clamp01(1 - reporter-protection)`

Wenn Retaliation eintritt (beim Beobachter `k`):

- `retaliation-events-total += 1`
- `retaliated-this-tick? = true`
- `fear_k = clamp01(fear_k + response-strength * (0.2 + 0.8 * punishment-value) * (1 - reporter-protection))`
Zusatz fuer Beobachter im `RETALIATION-WITNESS-RADIUS` um den Reporter:

`fear_w = clamp01(fear_w + response-strength * (0.2 + 0.8 * punishment-value) * (1 - reporter-protection) * 0.3)`

Dabei wird fuer diese Beobachter ebenfalls `retaliated-this-tick? = true` gesetzt, sodass in der Drift-Phase im selben Tick keine Fear-Mean-Reversion angewendet wird.

### 3.6 Drift-Phase

Fuer jeden Agenten `i`:

1. **Mean-Reversion der Fehlverhaltensneigung** (nur wenn kein Commit in diesem Tick):

`m_i(t+1) = clamp01(m_i(t) + drift-speed * (initial-misconduct-propensity - m_i(t)))`

2. **Fear-Mean-Reversion** (nur wenn keine Retaliation in diesem Tick):

`fear_i(t+1) = clamp01(fear_i(t) + drift-speed * (initial-fear - fear_i(t)))`

`drift-speed` steuert die Erholungsgeschwindigkeit unabhaengig von `response-strength`.
`response-strength` steuert nur die ereignisgetriebenen Spruenge (Sanktionen, Retaliation).
Damit kann die Erholung deutlich langsamer eingestellt werden als die Reaktion auf Ereignisse.

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

Tick-basierte Hidden-Misconduct-Kennzahlen:

- `hidden-misconduct-this-tick = true-misconduct-this-tick - sanctioned-this-tick`
- Wenn `true-misconduct-this-tick > 0`:
  - `hidden-misconduct-rate-this-tick = hidden-misconduct-this-tick / true-misconduct-this-tick`
- sonst:
  - `hidden-misconduct-rate-this-tick = 0`

## 4) Slider -> Formel -> Wirkung

| Slider | Direkter mathematischer Ort | Haupteffekt |
|---|---|---|
| `number-employees` | Populationsgroesse `N` | Mehr Agenten erzeugen mehr potenzielle Ereignisse pro Tick |
| `initial-misconduct-propensity` | Startwert von `m_i`; Zielwert der Mean-Reversion | Hoeheres langfristiges Baseline-Niveau fuer Fehlverhalten |
| `initial-fear` | Startwert von `fear_i` | Niedrigere Anfangs-Reportingbereitschaft bei hohem Wert |
| `punishment-value` | Absenkung von `misconduct-propensity` nach Sanktion und Fear-Anstieg bei Retaliation | Hoehere Sanktionsstaerke und staerkere Retaliation bei hohem Wert |
| `reporter-protection` | Reporting-Input, `p_ret`, Fear-Anstieg bei Retaliation | Mehr Reporting und weniger Retaliation/Fear-Anstieg |
| `response-strength` | Ereignisgetriebene Updates (Sanktion, Retaliation) | Steuert Staerke der Reaktion auf Einzelereignisse |
| `drift-speed` | Mean-Reversion in der Drift-Phase | Steuert Erholungsgeschwindigkeit zurueck zum Ausgangswert; unabhaengig von response-strength |

## 5) Dynamik ueber viele Ticks (Intuition)

### 5.1 Erwartete Fehlverhalten pro Tick

`E[true-misconduct-this-tick | t] = Sum_i m_i(t)`

Das ist der zentrale Input fuer Reporting, Sanktionen und Hidden-Misconduct.

### 5.2 Nichtlineares Reporting

Durch `p_report = logistic(x_report)` wirken kleine Aenderungen in `x_report` besonders stark im mittleren Bereich und schwach in den Saettigungsbereichen nahe 0 oder 1.

### 5.3 Gekoppelte Fear-Dynamik

Fear bewegt sich in beide Richtungen:

- nach oben bei Retaliation (eventbasiert; staerker bei hohem `punishment-value`),
- nach unten ohne Retaliation (langsamer Decay).

Damit entsteht eine realistischere Erholungsdynamik statt dauerhaftem Drift nach oben.

### 5.4 Hidden-Misconduct als Policy-Zielgroesse

`hidden-misconduct-rate = 1 - sanctioned-misconduct-total / true-misconduct-total`

Die Rate sinkt nur, wenn sanktionierte Faelle langfristig mit den tatsaechlichen Faellen Schritt halten.

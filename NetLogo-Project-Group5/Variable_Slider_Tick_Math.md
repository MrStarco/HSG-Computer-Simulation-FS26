# Variablen-, Slider- und Tick-Mathematik Dokumentation

Dieses Dokument erklaert, wie die Interface-Slider mit den Modellvariablen verbunden sind und was mathematisch in jedem Tick passiert.

## 1) Kernvariablen pro Agent

Jeder `employee` hat:

- `misconduct-propensity` in `[0,1]`: Wahrscheinlichkeit fuer Fehlverhalten.
- `fear` in `[0,1]`: beeinflusst Meldungsbereitschaft negativ.
- `utility`: akkumuliert Gewinne/Kosten aus Verhalten, Sanktionen und Retaliation.

Wichtige globale Zaehler:

- `true-misconduct-total`
- `sanctioned-misconduct-total`
- `reported-events-total`
- `retaliation-events-total`
- `hidden-misconduct-total`
- `hidden-misconduct-rate`

Hilfsfunktionen:

- `clamp01(x) = max(0, min(1, x))`
- `logistic(x) = 1 / (1 + exp(-x))`

## 2) Tick-Ablauf (mathematisch, in Reihenfolge)

Pro Tick laeuft `go` in dieser Logik:

1. Bewegung
2. Fehlverhaltens-Entscheid
3. Beobachtung und Reporting
4. Drift/Feedback
5. Metrik-Update

### 2.1 Bewegung

Agenten bewegen sich lokal zufaellig. Das aendert die Nachbarschaft und damit indirekt die Beobachtungswahrscheinlichkeit.

### 2.2 Fehlverhalten

Fuer jeden Agenten `i`:

- Ziehe `u ~ Uniform(0,1)`.
- Wenn `u < m_i(t)` mit `m_i(t) = misconduct-propensity_i(t)`, dann begeht Agent `i` Fehlverhalten.

Damit ist das Ereignis Bernoulli-verteilt:

- `P(commit_i(t)=1) = m_i(t)`

Wenn Fehlverhalten passiert:

- `true-misconduct-this-tick += 1`
- `true-misconduct-total += 1`
- `utility_i += misconduct-gain`

### 2.3 Beobachtung und Reporting

Fuer jeden Offender `j` mit Fehlverhalten:

- Menge der moeglichen Beobachter: Agenten in `observation-radius`.
- Falls mindestens ein Beobachter existiert, wird ein zufaelliger Beobachter `k` ausgewaehlt.

Reporting-Input:

`x_report = base-reporting-climate + 0.8 * reporter-protection - fear_k + 0.2 * misconduct-propensity_j`

Reporting-Wahrscheinlichkeit:

`p_report = logistic(x_report)`

Mit `u ~ Uniform(0,1)` gilt:

- Wenn `u < p_report`, dann wird gemeldet (`reported-events-total += 1`).

### 2.4 Sanktion bei Report

Sanktionswahrscheinlichkeit:

`p_sanction = clamp01(0.15 + 0.75 * enforcement-strictness)`

Wenn Sanktion eintritt:

- `sanctioned-this-tick += 1`
- `sanctioned-misconduct-total += 1`
- `utility_j -= sanction-cost * enforcement-strictness`
- `misconduct-propensity_j = clamp01(misconduct-propensity_j - learning-rate * 0.8)`

Wenn keine Sanktion eintritt:

- `misconduct-propensity_j = clamp01(misconduct-propensity_j + learning-rate * 0.3)`

### 2.5 Retaliation nach Report

Retaliationswahrscheinlichkeit:

`p_ret = clamp01(retaliation-base-chance * (1 - reporter-protection) * (0.5 + enforcement-strictness))`

Wenn Retaliation eintritt:

- `retaliation-events-total += 1`
- `fear_k = clamp01(fear_k + 0.15 * (1 - reporter-protection))`
- `utility_k -= retaliation-cost`

### 2.6 Drift-Phase fuer alle Agenten

Fuer jeden Agenten `i`:

1. Rueckdrift von `misconduct-propensity`, aber nur wenn in diesem Tick **kein** Fehlverhalten begangen wurde:

`m_i(t+1) = clamp01(m_i(t) + learning-rate * (initial-misconduct-propensity - m_i(t)))`

2. Genereller Fear-Drift:

`fear_i(t+1) = clamp01(fear_i(t) + 0.05 * retaliation-base-chance * (1 - reporter-protection))`

### 2.7 Metriken

- `hidden-misconduct-total = true-misconduct-total - sanctioned-misconduct-total`
- Wenn `true-misconduct-total > 0`:
  - `hidden-misconduct-rate = hidden-misconduct-total / true-misconduct-total`
  andernfalls `0`.

## 3) Verbindung Slider -> Formeln -> Wirkung

| Slider | Direkter mathematischer Ort | Haupteffekt |
|---|---|---|
| `number-employees` | Populationsgroesse `N` | Mehr Agenten -> mehr potenzielle Ereignisse pro Tick |
| `initial-misconduct-propensity` | Startwert von `m_i`, Drift-Ziel | Hoeheres langfristiges Basisniveau fuer Fehlverhalten |
| `initial-fear` | Startwert von `fear_i` | Anfangs geringere Reporting-Wahrscheinlichkeit bei hohem Wert |
| `enforcement-strictness` | `p_sanction`, Sanktionskosten, `p_ret` | Mehr Sanktionen, aber auch Retaliationsterm wird groesser |
| `reporter-protection` | Reporting-Input, `p_ret`, Fear-Zuwachs | Mehr Meldungen, weniger Retaliation, langsamerer Fear-Anstieg |
| `base-reporting-climate` | Reporting-Input `x_report` | Verschiebt Report-Logit nach oben/unten |
| `observation-radius` | Zeugenmenge in Radius | Hoeherer Radius -> eher Zeugen vorhanden |
| `retaliation-base-chance` | `p_ret` und Fear-Drift | Mehr Retaliation und systematisch steigende Angst |
| `misconduct-gain` | `utility += misconduct-gain` | Erhoeht kurzfristigen Anreiz fuer Offender |
| `sanction-cost` | `utility -= sanction-cost * enforcement-strictness` | Erhoeht erwartete Kosten bei Sanktion |
| `retaliation-cost` | `utility_observer -= retaliation-cost` | Erhoeht Kosten fuer Melder bei Retaliation |
| `learning-rate` | Updates von `misconduct-propensity` | Schnellere Anpassung nach Sanktion/Nicht-Sanktion/Drift |

## 4) Dynamik ueber viele Ticks (Intuition)

### 4.1 Erwartete Fehlverhalten pro Tick

Wenn `m_i(t)` gegeben ist:

`E[true-misconduct-this-tick | t] = Sum_i m_i(t)`

Das ist der zentrale Treiber fuer alle Folgeprozesse.

### 4.2 Reporting als Logit-Mechanik

`p_report = logistic(x_report)` macht den Prozess nichtlinear:

- kleine Aenderungen in `x_report` nahe `0` haben den groessten Effekt,
- bei sehr niedrigen/hohen Werten saettigt die Wahrscheinlichkeit gegen `0` bzw. `1`.

### 4.3 Rueckkopplung auf Fehlverhalten

Offender erhalten drei Arten von Updates:

- Sanktion: `m` sinkt stark um `learning-rate * 0.8`
- Report ohne Sanktion: `m` steigt um `learning-rate * 0.3`
- Kein Commit im Tick: `m` driftet Richtung `initial-misconduct-propensity`

Damit entsteht ueber Zeit ein Gleichgewicht aus:

- Entdeckung/Reporting/Sanktion (daempfend),
- Baseline-Drift und unsanktioniertem Lernen (anhebend).

### 4.4 Fear-Dynamik ueber Zeit

Es gibt einen systematischen Driftterm:

`Delta fear_base = 0.05 * retaliation-base-chance * (1 - reporter-protection)`

plus eventbasierte Spruenge bei Retaliation.

Ohne starke Protection oder geringe Retaliation steigt Fear daher tendenziell und senkt indirekt Reporting.

### 4.5 Hidden Misconduct als Ergebnisgroesse

`hidden-misconduct-rate` sinkt nur, wenn Sanktionen mit den True Events Schritt halten.

Formal:

`hidden-rate = 1 - sanctioned-misconduct-total / true-misconduct-total`

Folge: Sichtbar viele Sanktionen sind nicht automatisch "gut", wenn gleichzeitig True Misconduct noch schneller steigt.

## 5) Praktische Lesart fuer Policy-Experimente

- Hohe `enforcement-strictness` ohne ausreichend `reporter-protection` kann gemischte Effekte erzeugen (mehr Sanktion, aber auch mehr Retaliationsdruck).
- `reporter-protection` ist ein Hebel auf zwei Kanaelen gleichzeitig: Reporting rauf, Retaliation/Fear runter.
- `learning-rate` steuert, wie schnell sich das System nach Policy-Aenderungen neu einpendelt.

Damit laesst sich jeder Run als gekoppelte stochastische Dynamik lesen:

1. Bernoulli-Fehlverhalten
2. Logit-Reporting
3. Stochastische Sanktion/Retaliation
4. Lern- und Drift-Updates mit Clamping auf `[0,1]`

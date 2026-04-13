# Interface-Spezifikation (NetLogo Interface Tab)

Dieses Dokument beschreibt alle Widgets, die fuer das Modell benoetigt werden, plus eine manuelle Schritt-fuer-Schritt-Anleitung zum Anlegen in NetLogo.

## 1) Benoetigte Widgets

### Buttons

1. `setup`
   - Command: `setup`
   - Typ: Once button (Forever = aus)

2. `go`
   - Command: `go`
   - Typ: Forever button (Forever = an)

### Slider

1. `number-employees`
   - Min: `20`
   - Max: `400`
   - Increment: `10`
   - Default: `150`

2. `initial-misconduct-propensity`
   - Min: `0`
   - Max: `1`
   - Increment: `0.01`
   - Default: `0.25`

3. `initial-fear`
   - Min: `0`
   - Max: `1`
   - Increment: `0.01`
   - Default: `0.35`

4. `punishment-value`
   - Min: `0`
   - Max: `1`
   - Increment: `0.01`
   - Default: `0.70`

5. `reporter-protection`
   - Min: `0`
   - Max: `1`
   - Increment: `0.01`
   - Default: `0.45`

6. `misconduct-gain`
   - Min: `0`
   - Max: `5`
   - Increment: `0.1`
   - Default: `1.4`

7. `learning-rate`
   - Min: `0`
   - Max: `1`
   - Increment: `0.01`
   - Default: `0.20`

### Monitors

1. `True misconduct (total)`
   - Reporter: `true-misconduct-total`

2. `Sanctioned misconduct (total)`
   - Reporter: `sanctioned-misconduct-total`

3. `Hidden misconduct (total)`
   - Reporter: `hidden-misconduct-total`

4. `Hidden misconduct rate`
   - Reporter: `hidden-misconduct-rate`
   - Decimal places: `3`

5. `Reported events`
   - Reporter: `reported-events-total`

6. `Retaliation events`
   - Reporter: `retaliation-events-total`

7. `True misconduct (tick)`
   - Reporter: `true-misconduct-this-tick`

8. `Sanctioned (tick)`
   - Reporter: `sanctioned-this-tick`

9. `Relative change (%)`
   - Reporter: `relative-misconduct-change`
   - Decimal places: `1`

### Plots

#### Plot 1: `Misconduct Dynamics (Cumulative)`

- X-Axis: `ticks`
- Y-Axis: `events`
- Pens:
  1. `true total` -> `plot true-misconduct-total`
  2. `sanctioned total` -> `plot sanctioned-misconduct-total`
  3. `hidden total` -> `plot hidden-misconduct-total`

#### Plot 2: `Per Tick Misconduct`

- X-Axis: `ticks`
- Y-Axis: `events / tick`
- Pens:
  1. `true (tick)` -> `plot true-misconduct-this-tick`
  2. `sanctioned (tick)` -> `plot sanctioned-this-tick`
  3. `hidden (tick)` -> `plot (true-misconduct-this-tick - sanctioned-this-tick)`

#### Plot 3: `Relative Misconduct Change (%)`

- X-Axis: `ticks`
- Y-Axis: `% change`
- Pens:
  1. `rel. change %` -> `plot relative-misconduct-change`
  2. `zero` -> `plot 0`

## 2) Hardcoded Konstanten im Code

Diese Werte sind fest im Modellcode hinterlegt und erscheinen deshalb nicht als Slider:

- `BASE-REPORTING-CLIMATE = 0.1`
- `OBSERVATION-RADIUS = 3`
- `RETALIATION-COST = 1.2`

## 3) Manuelle Einrichtung in NetLogo

1. NetLogo starten.
2. Entweder:
   - `File -> Open...` und `Group5_Misconduct_ABM.nlogo` oeffnen, oder
   - neues leeres Modell erstellen (`File -> New`) und manuell befuellen.
3. Bei manueller Befuellung:
   - **Code Tab**: Inhalt aus `Code.nls` komplett einfuegen.
   - **Interface Tab**: Widgets gemaess obiger Spezifikation anlegen.
   - **Info Tab**: Inhalt aus `Documentation.md` einfuegen.
4. Reihenfolge fuer Tests:
   - `setup` klicken
   - `go` starten/stoppen
   - Parameter variieren (z. B. `punishment-value` und `reporter-protection`)
5. Modell speichern (`File -> Save`), damit Interface-Layout dauerhaft bleibt.

## 4) Empfohlene Layout-Struktur

- Links oben: `setup`, `go`
- Darunter links: alle Slider
- Rechts: Monitors
- Unten/rechts: die drei Plots
- Mitte: Graphics Window (Agentenansicht)

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

4. `enforcement-strictness`
   - Min: `0`
   - Max: `1`
   - Increment: `0.01`
   - Default: `0.70`

5. `reporter-protection`
   - Min: `0`
   - Max: `1`
   - Increment: `0.01`
   - Default: `0.45`

6. `base-reporting-climate`
   - Min: `-1`
   - Max: `1`
   - Increment: `0.01`
   - Default: `0.10`

7. `observation-radius`
   - Min: `1`
   - Max: `8`
   - Increment: `1`
   - Default: `3`

8. `retaliation-base-chance`
   - Min: `0`
   - Max: `1`
   - Increment: `0.01`
   - Default: `0.40`

9. `misconduct-gain`
   - Min: `0`
   - Max: `5`
   - Increment: `0.1`
   - Default: `1.4`

10. `sanction-cost`
    - Min: `0`
    - Max: `8`
    - Increment: `0.1`
    - Default: `2.6`

11. `retaliation-cost`
    - Min: `0`
    - Max: `5`
    - Increment: `0.1`
    - Default: `1.2`

12. `learning-rate`
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

### Plot

Plot name: `Misconduct Dynamics`

- X-Axis: `ticks`
- Y-Axis: `events`

PENS:

1. Pen `true`
   - Update command: `plot true-misconduct-total`

2. Pen `sanctioned`
   - Update command: `plot sanctioned-misconduct-total`

3. Pen `hidden`
   - Update command: `plot hidden-misconduct-total`

## 2) Manuelle Einrichtung in NetLogo

1. NetLogo starten.
2. Entweder:
   - `File -> Open...` und `Group5_Misconduct_ABM.nlogo` oeffnen, oder
   - neues leeres Modell erstellen (`File -> New`) und manuell befuellen.
3. Bei manueller Befuellung:
   - **Code Tab**: Inhalt aus `Code.nls` komplett einfuegen.
   - **Interface Tab**: Widgets gemass obiger Spezifikation anlegen.
   - **Info Tab**: Inhalt aus `Documentation.md` einfuegen.
4. Reihenfolge fuer Tests:
   - `setup` klicken
   - `go` starten/stoppen
   - Parameter variieren (z. B. `enforcement-strictness` und `reporter-protection`)
5. Modell speichern (`File -> Save`), damit Interface-Layout dauerhaft bleibt.

## 3) Empfohlene Layout-Struktur

- Links oben: `setup`, `go`
- Darunter links: alle Slider
- Rechts: Monitors
- Unten rechts: Plot `Misconduct Dynamics`
- Mitte: Graphics Window (Agentenansicht)

# NetLogo Project - Group 5

Dieses Verzeichnis enthaelt ein lauffaehiges Kernmodell fuer euer Thema **Reporting, Enforcement und Hidden Misconduct** sowie die aufgeteilten Bausteine fuer Code/Interface/Info.

## Projektstruktur

- `Group5_Misconduct_ABM.nlogo`  
  Vollstaendige NetLogo-Modelldatei (wenn ihr direkt starten wollt).

- `Code.nls`  
  Reiner NetLogo-Code fuer den **Code Tab**.

- `Interface.md`  
  Spezifikation aller Interface-Widgets inkl. manueller Schritt-fuer-Schritt-Anleitung.

- `Documentation.md`  
  Text fuer den **Info Tab** in NetLogo.

## Nutzung in NetLogo

### Option A (empfohlen): Direkt starten

1. NetLogo oeffnen.
2. `File -> Open...`
3. `Group5_Misconduct_ABM.nlogo` waehlen.
4. `setup` klicken, dann `go`.

### Option B: Manuell aus Einzeldateien aufbauen

1. In NetLogo ein neues Modell erstellen (`File -> New`).
2. Inhalt von `Code.nls` komplett in den **Code Tab** einfuegen.
3. Widgets im **Interface Tab** gemass `Interface.md` anlegen.
4. Inhalt von `Documentation.md` in den **Info Tab** einfuegen.
5. Speichern (`File -> Save`) als eigene `.nlogo`.

## Typische Team-Experimente

- `enforcement-strictness` erhoehen/senken und auf `hidden-misconduct-rate` achten.
- `reporter-protection` variieren und Effekte auf Reporting/Retaliation beobachten.
- Mehrere Runs mit gleichen Einstellungen vergleichen (stochastisches Modell).

## GitHub-Kurzanleitung fuer Einsteiger

### A) Einfach ueber GitHub.com (ohne Terminal)

1. Repository auf GitHub oeffnen.
2. Auf `main` **nicht direkt** arbeiten, sondern neuen Branch erstellen:
   - Dropdown bei Branch-Name -> neuen Namen eingeben (z. B. `feature/interface-tuning`) -> erstellen.
3. Datei oeffnen -> Stift-Symbol (`Edit this file`) klicken.
4. Aenderungen machen.
5. Unten:
   - Commit message eintragen (kurz und klar)
   - `Commit changes` auf den eigenen Branch
6. `Compare & pull request` klicken.
7. In der PR kurz schreiben:
   - Was geaendert?
   - Warum?
   - Was sollte Reviewer testen?
8. Auf Review warten, danach mergen.

### B) Lokal mit Git (Terminal) - Basisablauf

```bash
git clone <repo-url>
cd <repo-ordner>
git checkout -b feature/mein-thema
# Dateien bearbeiten
git add .
git commit -m "Add initial misconduct experiment settings"
git push -u origin feature/mein-thema
```

Danach auf GitHub Pull Request erstellen.

## Gute Team-Regeln (sehr wichtig)

- Kleine, fokussierte Commits statt grosser Sammel-Commits.
- Sprechende Commit Messages (was/warum).
- Vor PR kurz lokal testen (`setup`, `go`, Monitors/Plot pruefen).
- Konflikte frueh loesen: regelmaessig `main` in den Feature-Branch holen.
- Keine sensiblen Daten committen.

## Quellen

- [NetLogo Tutorial #1](https://docs.netlogo.org/tutorial1)
- [BIND - Beginner's Interactive NetLogo Dictionary](https://bind.netlogo.org)

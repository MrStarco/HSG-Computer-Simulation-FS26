# Changelog — Since Last Commit (`09caf65`)

---

## 1. Bystander Effect for Punishment (radius 6)
Agents within radius 6 of a sanctioned offender reduce their `misconduct-propensity` by 30% of the direct sanction effect. Radius is intentionally larger than other events because organisations signal punishment publicly to maximise deterrence.

## 2. Bystander Effect for Retaliation (radius 3)
Agents within radius 3 of the reporter receive a smaller fear increase when retaliation occurs. Radius matches the misconduct observation radius — retaliation is covert and only perceptible to those in immediate proximity, unlike public sanctions.

breed [employees employee]

globals [
  true-misconduct-total
  sanctioned-misconduct-total
  reported-events-total
  retaliation-events-total
  hidden-misconduct-rate
  hidden-misconduct-total
  true-misconduct-this-tick
  sanctioned-this-tick
]

employees-own [
  utility
  misconduct-propensity
  fear
  committed-this-tick?
]

to setup
  clear-all
  set true-misconduct-total 0
  set sanctioned-misconduct-total 0
  set reported-events-total 0
  set retaliation-events-total 0
  set hidden-misconduct-rate 0
  set hidden-misconduct-total 0
  set true-misconduct-this-tick 0
  set sanctioned-this-tick 0

  create-employees number-employees [
    setxy random-xcor random-ycor
    set shape "person"
    set size 1.1
    set utility 0
    set misconduct-propensity clamp01 (random-normal initial-misconduct-propensity 0.08)
    set fear clamp01 (random-normal initial-fear 0.08)
    set committed-this-tick? false
    recolor-from-fear
  ]
  reset-ticks
end

to go
  if not any? employees [ stop ]

  set true-misconduct-this-tick 0
  set sanctioned-this-tick 0

  move-employees
  misconduct-phase
  observation-and-reporting-phase
  drift-phase
  update-metrics
  tick
end

to move-employees
  ask employees [
    rt random 50
    lt random 50
    fd 1
  ]
end

to misconduct-phase
  ask employees [
    set committed-this-tick? false
    if random-float 1 < misconduct-propensity [
      set committed-this-tick? true
      set true-misconduct-this-tick true-misconduct-this-tick + 1
      set true-misconduct-total true-misconduct-total + 1
      set utility utility + misconduct-gain
    ]
  ]
end

to observation-and-reporting-phase
  ask employees with [committed-this-tick?] [
    let offender self
    let witnesses other employees in-radius observation-radius
    if any? witnesses [
      let observer one-of witnesses
      ask observer [ decide-report offender ]
    ]
  ]
end

to decide-report [offender]
  let reporting-input (base-reporting-climate + (0.8 * reporter-protection) - fear + (0.2 * [misconduct-propensity] of offender))
  let reporting-prob logistic reporting-input

  if random-float 1 < reporting-prob [
    set reported-events-total reported-events-total + 1

    let sanction-prob clamp01 (0.15 + (0.75 * enforcement-strictness))
    ifelse random-float 1 < sanction-prob
    [
      set sanctioned-this-tick sanctioned-this-tick + 1
      set sanctioned-misconduct-total sanctioned-misconduct-total + 1
      ask offender [
        set utility utility - (sanction-cost * enforcement-strictness)
        set misconduct-propensity clamp01 (misconduct-propensity - (learning-rate * 0.8))
      ]
    ]
    [
      ask offender [
        set misconduct-propensity clamp01 (misconduct-propensity + (learning-rate * 0.3))
      ]
    ]

    let retaliation-prob clamp01 (retaliation-base-chance * (1 - reporter-protection) * (0.5 + enforcement-strictness))
    if random-float 1 < retaliation-prob [
      set retaliation-events-total retaliation-events-total + 1
      set fear clamp01 (fear + (0.15 * (1 - reporter-protection)))
      set utility utility - retaliation-cost
      ask offender [ set color red ]
    ]
  ]
end

to drift-phase
  ask employees [
    if not committed-this-tick? [
      set misconduct-propensity clamp01 (misconduct-propensity + (learning-rate * (initial-misconduct-propensity - misconduct-propensity)))
    ]
    set fear clamp01 (fear + (0.05 * retaliation-base-chance * (1 - reporter-protection)))
    set committed-this-tick? false
    recolor-from-fear
  ]
end

to recolor-from-fear
  ifelse fear < 0.33
  [ set color green + 1 ]
  [ ifelse fear < 0.66
    [ set color yellow - 2 ]
    [ set color orange + 1 ] ]
end

to update-metrics
  set hidden-misconduct-total (true-misconduct-total - sanctioned-misconduct-total)
  ifelse true-misconduct-total > 0
  [ set hidden-misconduct-rate (hidden-misconduct-total / true-misconduct-total) ]
  [ set hidden-misconduct-rate 0 ]
end

to-report clamp01 [x]
  report max (list 0 (min (list 1 x)))
end

to-report logistic [x]
  report 1 / (1 + exp (- x))
end
@#$#@#$#@
GRAPHICS-WINDOW
240
10
760
530
-1
-1
13.0
1
10
1
1
1
0
1
1
1
-16
16
-16
16
0
0
1
ticks
30.0

BUTTON
20
20
95
53
setup
setup
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
105
20
180
53
go
go
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

SLIDER
20
80
220
113
number-employees
number-employees
20
400
150.0
10
1
NIL
HORIZONTAL

SLIDER
20
118
220
151
initial-misconduct-propensity
initial-misconduct-propensity
0
1
0.25
0.01
1
NIL
HORIZONTAL

SLIDER
20
156
220
189
initial-fear
initial-fear
0
1
0.35
0.01
1
NIL
HORIZONTAL

SLIDER
20
194
220
227
enforcement-strictness
enforcement-strictness
0
1
0.7
0.01
1
NIL
HORIZONTAL

SLIDER
20
232
220
265
reporter-protection
reporter-protection
0
1
0.45
0.01
1
NIL
HORIZONTAL

SLIDER
20
270
220
303
base-reporting-climate
base-reporting-climate
-1
1
0.1
0.01
1
NIL
HORIZONTAL

SLIDER
20
308
220
341
observation-radius
observation-radius
1
8
3.0
1
1
NIL
HORIZONTAL

SLIDER
20
346
220
379
retaliation-base-chance
retaliation-base-chance
0
1
0.4
0.01
1
NIL
HORIZONTAL

SLIDER
20
384
220
417
misconduct-gain
misconduct-gain
0
5
1.4
0.1
1
NIL
HORIZONTAL

SLIDER
20
422
220
455
sanction-cost
sanction-cost
0
8
2.6
0.1
1
NIL
HORIZONTAL

SLIDER
20
460
220
493
retaliation-cost
retaliation-cost
0
5
1.2
0.1
1
NIL
HORIZONTAL

SLIDER
20
498
220
531
learning-rate
learning-rate
0
1
0.2
0.01
1
NIL
HORIZONTAL

MONITOR
780
20
980
65
True misconduct (total)
true-misconduct-total
17
1
11

MONITOR
780
70
980
115
Sanctioned misconduct (total)
sanctioned-misconduct-total
17
1
11

MONITOR
780
120
980
165
Hidden misconduct (total)
hidden-misconduct-total
17
1
11

MONITOR
780
170
980
215
Hidden misconduct rate
hidden-misconduct-rate
17
3
11

MONITOR
780
220
980
265
Reported events
reported-events-total
17
1
11

MONITOR
780
270
980
315
Retaliation events
retaliation-events-total
17
1
11

MONITOR
780
320
980
365
True misconduct (tick)
true-misconduct-this-tick
17
1
11

MONITOR
780
370
980
415
Sanctioned (tick)
sanctioned-this-tick
17
1
11

PLOT
780
430
1180
680
Misconduct Dynamics
ticks
events
0.0
10.0
0.0
10.0
true
true
"" ""
PENS
"true" 1.0 0 -16777216 true "" "plot true-misconduct-total"
"sanctioned" 1.0 0 -7500403 true "" "plot sanctioned-misconduct-total"
"hidden" 1.0 0 -955883 true "" "plot hidden-misconduct-total"

@#$#@#$#@
## WHAT IS IT?

This model simulates organizational misconduct in a fixed employee population and examines when stronger enforcement reduces true misconduct versus mainly visible misconduct.

## HOW IT WORKS

Each tick executes this sequence:
1. Employees move.
2. Misconduct happens probabilistically.
3. Nearby coworkers may observe.
4. Observers decide whether to report (based on fear, protection, and climate).
5. Reported cases can be sanctioned (enforcement strictness).
6. Retaliation can occur and feeds back into fear.
7. Metrics are updated.

## HOW TO USE IT

1. Click `setup`.
2. Click `go` (forever button).
3. Vary `enforcement-strictness` and `reporter-protection`.
4. Compare `true-misconduct-total`, `sanctioned-misconduct-total`, and `hidden-misconduct-rate`.

## THINGS TO NOTICE

- Hidden misconduct can rise even when sanctions are stable.
- Weak protection increases fear and can suppress reporting.
- Policy effects are nonlinear because retaliation and fear create feedback loops.

## THINGS TO TRY

- Keep enforcement fixed, sweep protection from low to high.
- Keep protection fixed, sweep enforcement from low to high.
- Repeat same setting multiple times and compare run variability.

## EXTENDING THE MODEL

- Add departments and local trust/reporting norms.
- Add compliance queue/backlog and processing limits.
- Add anonymity and evidence-quality tradeoff.

## NETLOGO FEATURES

- Local interaction with `in-radius`.
- Probabilistic decision rules.
- Monitors and plot for policy comparison.

## CREDITS AND REFERENCES

Concept source: Group 5 project presentation on reporting, enforcement, retaliation, and hidden misconduct.
Reference docs:
- https://docs.netlogo.org/tutorial1
- https://bind.netlogo.org
@#$#@#$#@
default
true
0
Polygon -7500403 true true 150 5 40 250 150 205 260 250

person
false
0
Circle -7500403 true true 110 5 80
Polygon -7500403 true true 105 90 120 195 90 285 105 300 135 300 150 225 165 300 195 300 210 285 180 195 195 90
Rectangle -7500403 true true 127 79 172 94
Polygon -7500403 true true 195 90 240 150 225 180 165 105
Polygon -7500403 true true 105 90 60 150 75 180 135 105
@#$#@#$#@
NetLogo 7.0.3
@#$#@#$#@
setup
go
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
default
0.0
-0.2 0 0.0 1.0
0.0 1 1.0 0.0
0.2 0 0.0 1.0
link direction
true
0
Line -7500403 true 150 150 90 180
Line -7500403 true 150 150 210 180
@#$#@#$#@
0
@#$#@#$#@

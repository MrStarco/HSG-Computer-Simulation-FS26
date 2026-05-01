**Parameter Justification for the Misconduct Agent-Based Model**

*Group 5 — Empirical Grounding for Validity Documentation*

**Introduction**

This document maps each parameter and key mechanism of the Group 5
misconduct ABM onto a corresponding body of organisational and
behavioural research, providing both a conceptual justification and,
where possible, an empirical anchor for the chosen parameter level. The
purpose is to address the *verification, validation, and replication*
requirements outlined in Week 8 of the course (Beese et al., 2019), and
in particular to satisfy the validity prompt: *“How can you justify the
agent-level behavior based on our general experience/observations?”* The
mapping below pairs each parameter with the leading research stream from
which it derives and, where the literature provides quantitative
estimates (for example, retaliation prevalence as a percentage of
reporting cases), translates those estimates onto the model's normalised
\[0,1\] scale.

**Note on tick interpretation**

The empirical surveys cited in this document (NBES, European Barometer)
report annual rates of misconduct observation, reporting, and
retaliation. The cleanest reading of one model tick is therefore **one
annual reporting cycle**. If a tick is interpreted as a shorter period
(for example a month or a quarter), the empirical rates given below
should be divided proportionally. This interpretation choice should be
stated explicitly in the validity section of the final report, in line
with the requirement to maintain consistent terminology between the
conceptual model and the simulation model (Week 8 verification slide).

**1. initial-misconduct-propensity (default 0.4)**

***What it does***

Per-tick probability that any individual employee commits an act of
misconduct. The setup value also serves as the mean-reversion target
during the drift phase.

***Theoretical grounding***

Routine-activity and opportunity theories of workplace deviance
(Hollinger & Clark, 1983; Robinson & Bennett, 1995). These theories
treat misconduct as a probabilistic outcome of individual disposition
combined with situational opportunity, which is precisely the Bernoulli
structure implemented in the misconduct-phase.

***Empirical anchor***

The Ethics Resource Center's National Business Ethics Survey (NBES)
reports observed-misconduct prevalence in the United States workforce:
55% in 2007, 45% in 2011, and 41% in 2013 (Ethics Resource Center, 2008,
2012, 2014). Because the model already separates commission from
observation, a per-tick commission probability of approximately 0.40 is
consistent with the interpretation that one tick corresponds to one
annual cycle and that observed-misconduct prevalence is roughly equal to
commission prevalence at the population level. The default of 0.4 is
therefore well-defended.

***Suggested sensitivity range***

0.20 (strong-culture firm) to 0.60 (weak-culture firm). The National
Government Ethics Survey (Ethics Resource Center, 2008) found
observation rates of 57–63% across public-sector organisations,
supporting the upper bound.

**2. initial-fear (default 0.5)**

***What it does***

Baseline subtractive term in the reporting-decision logistic. Fear is
also the mean-reversion target after retaliation-induced spikes have
decayed.

***Theoretical grounding***

Defensive and quiescent silence (Pinder & Harlos, 2001), organisational
silence as a collective phenomenon (Morrison & Milliken, 2000), and
psychological safety as the inverse construct (Edmondson, 1999).

***Empirical anchor***

Two complementary estimates. The Ethics Resource Center (2008) reports
that 36% of non-reporters explicitly feared retaliation from at least
one source, while 54% were skeptical that reporting would make a
difference (futility). Combining these two silence pressures yields a
baseline silence-driving force in the 0.40–0.55 range. Independently,
McKinsey & Company (2021) found that 89% of employees consider
psychological safety essential, but that the leadership behaviours
producing it are uncommon, implying that baseline psychological safety
in organisations is moderate rather than high. The recommended baseline
of 0.35 noted in the model's info tab sits cleanly within this range.

***Suggested sensitivity range***

0.20 (high-psychological-safety organisations) to 0.70 (post-scandal or
climate-of-fear organisations).

**3. reporter-protection (default 0.5) — high-leverage policy lever**

***What it does***

In the model, retaliation probability equals (1 − reporter-protection);
the same parameter also raises the reporting-decision logistic via the
+0.8 × protection term. Protection therefore operates through two
channels: it directly suppresses retaliation events and it directly
raises reporting willingness.

***Theoretical grounding***

Whistleblower protection literature (Near & Miceli, 1995; Dworkin &
Baucus, 1998; Rehg, Miceli, Near, & Van Scotter, 2008). Mesmer-Magnus
and Viswesvaran's (2005) meta-analysis of 193 correlations from 26
samples (N = 18,781) found that retaliation against whistleblowers is
best predicted by contextual variables, which is precisely the type of
variable reporter-protection represents.

***Empirical anchor — direct percentage mapping***

The retaliation-probability mapping inverts cleanly to the protection
scale.

**United States baseline.** The 2011 NBES reported that 22% of US
employees who reported misconduct subsequently experienced retaliation,
up from 12% in 2007 and 15% in 2009 (Ethics Resource Center, 2012).
Mapping a retaliation probability of 0.22 onto the model implies
**reporter-protection ≈ 0.78**, a “well-protected, US-style” baseline.

**European baseline.** The Special Eurobarometer 470 on corruption found
that 81% of respondents indicated they would not blow the whistle
because of the potential of retaliation (European Commission, 2017).
Although this measures fear of retaliation rather than realised
retaliation, it justifies a substantially lower protection setting in
any scenario explicitly designed to study climate-of-fear effects:
**reporter-protection ≈ 0.20**.

**Within-firm variation.** The 2011 NBES (Ethics Resource Center, 2012)
further reports that reporting rates were 72% at companies where
employees believed retaliation was not tolerated, compared with 54% at
companies where retaliation was perceived as tolerated. Future
willingness to report dropped from 95% to 86% after experiencing
retaliation. The 18-percentage-point gap between high- and
low-protection climates is a quantitative face-validity benchmark that
the model should be able to reproduce when sweeping the protection
parameter.

***Recommended experimental sweep***

{0.20, 0.50, 0.78, 0.95}, corresponding to four meaningful policy
regimes: European-Barometer-low, model default, US-NBES-baseline, and a
best-practice ceiling.

**4. punishment-value (default 0.5)**

***What it does***

Scales (a) the propensity drop applied to the offender after sanction,
(b) the bystander deterrent effect on neighbouring agents, and (c) the
severity of any subsequent retaliation event.

***Theoretical grounding***

General deterrence theory (Becker, 1968; Nagin, 2013; Paternoster,
2010). One important conceptual nuance should be flagged in the validity
write-up: Nagin's (2013) review of the empirical deterrence literature
concludes that the certainty of apprehension, rather than the severity
of the resulting consequences, is the more effective deterrent. The
current model conflates certainty (implicitly fixed at 1.0 because every
report is sanctioned automatically) and severity (controlled by
punishment-value). This is a deliberate simplification for tractability
and should be discussed as a model limitation.

***Empirical anchor***

Hollinger and Clark (1983) found perceived sanction severity and
certainty negatively associated with employee theft. D'Arcy, Hovav, and
Galletta (2009) found perceived severity reduced information-system
misuse, with mixed effects across countermeasures. There is no single
percentage anchor that maps directly to the \[0,1\] severity scale, so
the default of 0.5 is justified narratively as “moderate sanction
strength corresponding to typical written-warning to suspension
regimes.”

***Suggested sensitivity range***

0.20 (lenient response) to 0.90 (termination plus reputational
consequences). The most policy-relevant region is the high-punishment,
low-protection corner, where the model's central hypothesis predicts the
highest hidden-misconduct rate.

**5. The reporting-decision logistic**

Although the four constants in the reporting logistic are not exposed as
sliders, they are the most consequential hidden assumptions in the model
and the natural target of any methodologically rigorous review.

***Base climate constant (+0.1)***

Justified by NBES baseline reporting rates, which have hovered between
63% and 65% across multiple survey waves (Ethics Resource Center, 2014).
With the default parameters substituted into the logistic — protection =
0.5, fear = 0.5, offender-propensity = 0.4 — the input evaluates to
0.08, yielding a reporting probability of approximately 0.52. This is
somewhat below the empirical baseline; raising the constant from 0.1 to
approximately 0.3 would land the model more precisely at 60%.

***Weight on protection (+0.8)***

Dominant positive coefficient. Justified by the 18-percentage-point gap
(72% vs 54%) between high- and low-protection reporting climates
documented in the NBES (Ethics Resource Center, 2012) and by the
meta-analytic finding that contextual variables are the strongest
predictors of whistleblowing (Mesmer-Magnus & Viswesvaran, 2005).

***Weight on fear (−1.0)***

Equal-magnitude opposite-sign mirror of the protection coefficient.
Justified by treating climate-of-fear and climate-of-voice as inverse
constructs (Morrison & Milliken, 2000).

***Weight on offender propensity (+0.2)***

Captures the seriousness-of-wrongdoing effect. Mesmer-Magnus and
Viswesvaran's (2005) meta-analysis found that wrongdoing characteristics
correlate with whistleblowing intent, but the effect is weaker than that
of contextual variables such as retaliation climate. The 0.2 vs 0.8
relative weighting in the model is consistent with this empirical
ordering.

**6. OBSERVATION-RADIUS = 3 (and the bystander mechanism)**

***What it does***

A witness must be within radius 3 patches of the offender for misconduct
to be observable. Of the available witnesses, exactly one is selected to
make the reporting decision.

***Theoretical grounding***

Latané's (1981) social impact theory and the bystander effect (Latané &
Darley, 1968, 1970).

***Empirical anchor***

Latané and Nida's (1981) meta-analysis of 56 experiments found that 75%
of lone bystanders helped, compared with 53% in groups. In the seminal
Darley and Latané (1968) study, the sole bystander always intervened,
while only 62% intervened when in a group of five. Fischer and
colleagues (2011) updated this evidence base with a meta-analysis of 105
independent effect sizes from over 7,700 participants, reporting an
overall effect size of g = −0.35 for the inhibitory effect of group size
on helping.

***Possible model refinement***

The current code selects one-of witnesses regardless of how many are
present, and the reporting probability is independent of group size. The
bystander literature would predict that more witnesses should reduce the
probability that any single one acts (diffusion of responsibility). A
defensible extension is to scale the per-witness reporting probability
by 1/n^k with k between 0.3 and 0.5. This refinement should be noted in
the discussion section even if not implemented for the current
submission.

**7. BYSTANDER-EFFECT-FACTOR = 0.3**

***What it does***

Scales the magnitude of indirect (vicarious) propensity and fear updates
for agents who witness another agent being punished or retaliated
against, relative to direct experience.

***Theoretical grounding***

Bandura's (1977) social learning theory and Latané's (1981) social
impact theory both predict that vicarious reinforcement produces effects
of smaller magnitude than direct experience. Latané's theory in
particular provides a theoretical justification for an indirect-impact
factor of approximately one-third of the direct effect, which is exactly
what the model's value of 0.3 implements.

**8. response-strength (0.33) and drift-speed (0.05)**

These are learning-rate and mean-reversion parameters, respectively, and
are best understood as numerical-stability choices supported by general
behavioural-modelling conventions rather than by direct empirical
estimation.

***response-strength***

Standard reinforcement-learning literature uses learning rates in the
0.1–0.5 range (Sutton & Barto, 2018). The default of 0.33 is a
conventional middle value.

***drift-speed***

Justified by the empirical observation that 86% of employees who
experienced retaliation said they would still report future misconduct,
compared with 95% who had not experienced retaliation — a
9-percentage-point drop suggesting that retaliation-induced fear
partially decays rather than fully persists (Ethics Resource Center,
2014). A drift-speed of 0.05 implies that approximately half of any
deviation is recovered in roughly 14 ticks, which is consistent with a
“slow but real recovery” interpretation.

***Required validation step***

Both parameters should be subject to a sensitivity analysis (sweep ±50%
from default) as explicitly required by the Week 8 validity assignment.
The qualitative pattern of results should be unchanged across this
range.

**9. Suggested baseline experimental design**

Adopting the empirically-anchored values, the proposed “realistic
baseline” run is as follows.

***Anchored baseline parameters***

initial-misconduct-propensity = 0.40 (NBES observation rate ≈ 41%).

initial-fear = 0.35 (moderate but non-crisis climate, consistent with
combined silence-pressure data).

reporter-protection = 0.78 (NBES retaliation rate ≈ 22%, mapped as 1 −
0.22).

punishment-value = 0.50 (moderate baseline; no clean empirical anchor).

response-strength = 0.33; drift-speed = 0.05 (literature-conventional).

***Experimental sweeps***

Protection sweep: {0.20, 0.50, 0.78, 0.95} — four regimes spanning
Eurobarometer-low to best-practice.

Punishment sweep: {0.20, 0.50, 0.80} — three sanction-strength regimes.

Together this yields a 4 × 3 design (12 cells), which is feasible to run
with adequate replication within the time budget the assignment slides
describe. With approximately 30 replications per cell to handle
stochastic variation, this gives 360 simulation runs in total.

**References**

Bandura, A. (1977). Social learning theory. Englewood Cliffs, NJ:
Prentice-Hall.

Becker, G. S. (1968). Crime and punishment: An economic approach.
Journal of Political Economy, 76(2), 169–217.
https://doi.org/10.1086/259394

Beese, J., Haki, M. K., Aier, S., & Winter, R. (2019). Simulation-based
research in information systems: Epistemic implications and a review of
the status quo. Business & Information Systems Engineering, 61(4),
503–521. https://doi.org/10.1007/s12599-019-00604-4

D'Arcy, J., Hovav, A., & Galletta, D. (2009). User awareness of security
countermeasures and its impact on information systems misuse: A
deterrence approach. Information Systems Research, 20(1), 79–98.
https://doi.org/10.1287/isre.1070.0160

Dworkin, T. M., & Baucus, M. S. (1998). Internal vs. external
whistleblowers: A comparison of whistleblowering processes. Journal of
Business Ethics, 17(12), 1281–1298.
https://doi.org/10.1023/A:1005916210589

Edmondson, A. (1999). Psychological safety and learning behavior in work
teams. Administrative Science Quarterly, 44(2), 350–383.
https://doi.org/10.2307/2666999

Ethics Resource Center. (2008). 2007 National Business Ethics Survey: An
inside view of private sector ethics. Arlington, VA: Author.

Ethics Resource Center. (2012). 2011 National Business Ethics Survey:
Workplace ethics in transition. Arlington, VA: Author.

Ethics Resource Center. (2014). National Business Ethics Survey of the
U.S. workforce. Arlington, VA: Author.

European Commission. (2017). Special Eurobarometer 470: Corruption.
Brussels: European Commission.
https://data.europa.eu/euodp/en/data/dataset/S2176_88_2_470_ENG

Fischer, P., Krueger, J. I., Greitemeyer, T., Vogrincic, C.,
Kastenmüller, A., Frey, D., Heene, M., Wicher, M., & Kainbacher, M.
(2011). The bystander-effect: A meta-analytic review on bystander
intervention in dangerous and non-dangerous emergencies. Psychological
Bulletin, 137(4), 517–537. https://doi.org/10.1037/a0023304

Hollinger, R. C., & Clark, J. P. (1983). Theft by employees. Lexington,
MA: Lexington Books.

Latané, B. (1981). The psychology of social impact. American
Psychologist, 36(4), 343–356. https://doi.org/10.1037/0003-066X.36.4.343

Latané, B., & Darley, J. M. (1968). Group inhibition of bystander
intervention in emergencies. Journal of Personality and Social
Psychology, 10(3), 215–221. https://doi.org/10.1037/h0026570

Latané, B., & Darley, J. M. (1970). The unresponsive bystander: Why
doesn't he help? New York: Appleton-Century-Crofts.

Latané, B., & Nida, S. (1981). Ten years of research on group size and
helping. Psychological Bulletin, 89(2), 308–324.
https://doi.org/10.1037/0033-2909.89.2.308

McKinsey & Company. (2021). Psychological safety and the critical role
of leadership development. McKinsey & Company.
https://www.mckinsey.com/business-functions/people-and-organizational-performance/our-insights/psychological-safety-and-the-critical-role-of-leadership-development

Mesmer-Magnus, J. R., & Viswesvaran, C. (2005). Whistleblowing in
organizations: An examination of correlates of whistleblowing
intentions, actions, and retaliation. Journal of Business Ethics, 62(3),
277–297. https://doi.org/10.1007/s10551-005-0849-1

Miceli, M. P., & Near, J. P. (1992). Blowing the whistle: The
organizational and legal implications for companies and employees. New
York: Lexington Books.

Morrison, E. W., & Milliken, F. J. (2000). Organizational silence: A
barrier to change and development in a pluralistic world. Academy of
Management Review, 25(4), 706–725. https://doi.org/10.2307/259200

Nagin, D. S. (2013). Deterrence in the twenty-first century. Crime and
Justice, 42(1), 199–263. https://doi.org/10.1086/670398

Near, J. P., & Miceli, M. P. (1985). Organizational dissidence: The case
of whistle-blowing. Journal of Business Ethics, 4(1), 1–16.
https://doi.org/10.1007/BF00382668

Near, J. P., & Miceli, M. P. (1995). Effective whistle-blowing. Academy
of Management Review, 20(3), 679–708. https://doi.org/10.2307/258791

Near, J. P., & Miceli, M. P. (2016). After the wrongdoing: What managers
should know about whistleblowing. Business Horizons, 59(1), 105–114.
https://doi.org/10.1016/j.bushor.2015.09.007

Paternoster, R. (2010). How much do we really know about criminal
deterrence? Journal of Criminal Law and Criminology, 100(3), 765–824.

Pinder, C. C., & Harlos, K. P. (2001). Employee silence: Quiescence and
acquiescence as responses to perceived injustice. Research in Personnel
and Human Resources Management, 20, 331–369.
https://doi.org/10.1016/S0742-7301(01)20007-3

Rehg, M. T., Miceli, M. P., Near, J. P., & Van Scotter, J. R. (2008).
Antecedents and outcomes of retaliation against whistleblowers: Gender
differences and power relationships. Organization Science, 19(2),
221–240. https://doi.org/10.1287/orsc.1070.0310

Robinson, S. L., & Bennett, R. J. (1995). A typology of deviant
workplace behaviors: A multidimensional scaling study. Academy of
Management Journal, 38(2), 555–572. https://doi.org/10.2307/256693

Sutton, R. S., & Barto, A. G. (2018). Reinforcement learning: An
introduction (2nd ed.). Cambridge, MA: MIT Press.

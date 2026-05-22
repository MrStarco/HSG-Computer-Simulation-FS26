# Parameter Renaming — Misconduct ABM

*Group 5 — proposed parameter and variable name changes for the NetLogo model.*

<table>
<colgroup>
<col style="width: 35%" />
<col style="width: 35%" />
<col style="width: 28%" />
</colgroup>
<thead>
<tr>
<th><strong>Current name</strong></th>
<th><strong>Proposed name</strong></th>
<th><strong>Scope</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="3"><strong>Adjustable sliders (Interface)</strong></td>
</tr>
<tr>
<td>number-employees</td>
<td><strong>number-employees</strong></td>
<td>Slider — unchanged</td>
</tr>
<tr>
<td>initial-misconduct-propensity</td>
<td><strong>initial-misconduct-propensity</strong></td>
<td>Slider — unchanged</td>
</tr>
<tr>
<td>initial-fear</td>
<td><strong>initial-fear</strong></td>
<td>Slider — unchanged</td>
</tr>
<tr>
<td><mark>punishment-value</mark></td>
<td><strong>punishment-severity</strong></td>
<td>Slider</td>
</tr>
<tr>
<td>reporter-protection</td>
<td><strong>reporter-protection</strong></td>
<td>Slider — unchanged</td>
</tr>
<tr>
<td><mark>response-strength</mark></td>
<td><strong>learning-rate</strong></td>
<td>Slider</td>
</tr>
<tr>
<td><mark>drift-speed</mark></td>
<td><strong>baseline-recovery-rate</strong></td>
<td>Slider</td>
</tr>
<tr>
<td colspan="3"><strong>Hardcoded constants (set in setup)</strong></td>
</tr>
<tr>
<td>base-reporting-climate</td>
<td><strong>base-reporting-climate</strong></td>
<td>Global — unchanged</td>
</tr>
<tr>
<td>observation-radius</td>
<td><strong>observation-radius</strong></td>
<td>Global — unchanged</td>
</tr>
<tr>
<td>punishment-witness-radius</td>
<td><strong>punishment-witness-radius</strong></td>
<td>Global — unchanged</td>
</tr>
<tr>
<td>retaliation-witness-radius</td>
<td><strong>retaliation-witness-radius</strong></td>
<td>Global — unchanged</td>
</tr>
<tr>
<td>bystander-effect-factor</td>
<td><strong>bystander-effect-factor</strong></td>
<td>Global — unchanged</td>
</tr>
<tr>
<td colspan="3"><strong>Output metrics — cumulative totals</strong></td>
</tr>
<tr>
<td><mark>true-misconduct-total</mark></td>
<td><strong>committed-misconduct-total</strong></td>
<td>Global</td>
</tr>
<tr>
<td><mark>sanctioned-misconduct-total</mark></td>
<td><strong>punished-misconduct-total</strong></td>
<td>Global</td>
</tr>
<tr>
<td>hidden-misconduct-total</td>
<td><strong>hidden-misconduct-total</strong></td>
<td>Global — unchanged</td>
</tr>
<tr>
<td>hidden-misconduct-rate</td>
<td><strong>hidden-misconduct-rate</strong></td>
<td>Global — unchanged</td>
</tr>
<tr>
<td>reported-events-total</td>
<td><strong>reported-events-total</strong></td>
<td>Global — unchanged</td>
</tr>
<tr>
<td>retaliation-events-total</td>
<td><strong>retaliation-events-total</strong></td>
<td>Global — unchanged</td>
</tr>
<tr>
<td colspan="3"><strong>Output metrics — per-tick flows</strong></td>
</tr>
<tr>
<td><mark>true-misconduct-this-tick</mark></td>
<td><strong>committed-misconduct-this-tick</strong></td>
<td>Global</td>
</tr>
<tr>
<td><mark>sanctioned-this-tick</mark></td>
<td><strong>punished-misconduct-this-tick</strong></td>
<td>Global</td>
</tr>
<tr>
<td>reported-events-this-tick</td>
<td><strong>reported-events-this-tick</strong></td>
<td>Global — unchanged</td>
</tr>
<tr>
<td>retaliation-events-this-tick</td>
<td><strong>retaliation-events-this-tick</strong></td>
<td>Global — unchanged</td>
</tr>
<tr>
<td>hidden-misconduct-this-tick</td>
<td><strong>hidden-misconduct-this-tick</strong></td>
<td>Global — unchanged</td>
</tr>
<tr>
<td>hidden-misconduct-rate-this-tick</td>
<td><strong>hidden-misconduct-rate-this-tick</strong></td>
<td>Global — unchanged</td>
</tr>
<tr>
<td><mark>true-misconduct-prev-tick</mark></td>
<td><strong>committed-misconduct-prev-tick</strong></td>
<td>Global</td>
</tr>
<tr>
<td>relative-misconduct-change</td>
<td><strong>relative-misconduct-change</strong></td>
<td>Global — unchanged</td>
</tr>
<tr>
<td colspan="3"><strong>Agent attributes (employees-own)</strong></td>
</tr>
<tr>
<td>misconduct-propensity</td>
<td><strong>misconduct-propensity</strong></td>
<td>Agent — unchanged</td>
</tr>
<tr>
<td>fear</td>
<td><strong>fear</strong></td>
<td>Agent — unchanged</td>
</tr>
<tr>
<td>committed-this-tick?</td>
<td><strong>committed-this-tick?</strong></td>
<td>Agent — unchanged</td>
</tr>
<tr>
<td>reported-this-tick?</td>
<td><strong>reported-this-tick?</strong></td>
<td>Agent — unchanged</td>
</tr>
<tr>
<td><mark>sanctioned-this-tick?</mark></td>
<td><strong>was-punished-this-tick?</strong></td>
<td>Agent</td>
</tr>
<tr>
<td><mark>retaliated-this-tick?</mark></td>
<td><strong>was-retaliated-against-this-tick?</strong></td>
<td>Agent</td>
</tr>
<tr>
<td><mark>sanction-witnessed-this-tick?</mark></td>
<td><strong>punishment-witnessed-this-tick?</strong></td>
<td>Agent</td>
</tr>
<tr>
<td>retaliation-witnessed-this-tick?</td>
<td><strong>retaliation-witnessed-this-tick?</strong></td>
<td>Agent — unchanged</td>
</tr>
</tbody>
</table>

# Human Anger, Friendliness and approach-related questionnaire content

Exploratory human-only analysis. [Specification](PROTOCOL.md) committed at `b308adb` after source/baseline verification and before new item/bin/nonlinear outcomes. See [decision brief](DECISION_BRIEF.md), [source gate](SOURCE_GATE.json), [source manifest](SOURCE_MANIFEST.json) and [numerical verification](VERIFICATION.json). Prior model/factor findings are not reanalyzed.

## Population, key and historical reproduction

Johnson’s307,313-record IPIP300.dat matches SHA256 `1bbb7189f5f0f2883bb4493f956cf639178c5c8ee95319fd3881f6d9d2f189a3`. All five existing external files (raw data, DAT300.doc, original item-key workbook,300-item scoring workbook and official IPIP key HTML) match their frozen AA27 hashes; all nine Git sources match pinned commits/hashes. No data download, relocation or modification occurred.

The raw file has333 content bytes per record, items1–300 at columns34–333, and already-keyed1–5 values with0 missing. We reproduce145,388 complete all-age records and117,260 complete adults aged18–80 inclusive, then remove one exact300-item duplicate pattern, retaining the first source row: **117,259**. Eligibility requires all300 items valid, not merely the three facets analyzed. No outcome-dependent, demographic, desirability or post hoc careless-response filter is added.

The read-only scoring-workbook Input sheet matches every one of the300 archived scoring-specification rows; item wording/facet/sign independently agrees with official IPIP HTML. The documented minor wording normalizations at58/78/202 are inherited and do not affect these30 N2/E1/E3 items. All148 original negative keys were already applied by Johnson’s collection process. **Stored data are never reversed again.** Primary facet score is the arithmetic mean of ten stored keyed items. Full N2/E1/E3 item inventories and original signs are exported; item public-domain wording is distinct from dataset licensing.

The original seed20260920 reference/calibration/test selections and all three26-facet transformed-matrix hashes reproduce exactly. Frozen reference-only rank-normalized N2–E1 Pearson r is−0.2804773821160381; reproduction−0.2804773821160449, error6.78e−15. This gate verifies continuity. New analysis intentionally uses the full eligible unique cohort’s **raw keyed item values/arithmetic facet means**, not the old transformed30,000-person reference. Neither historical methodology nor its reported result is replaced. Full-cohort results:

| Outcome versus N2 facet | Metric | Correlation | Simultaneous95% interval (224-endpoint family) |
| --- | --- | --- | --- |
| E1 | Pearson | -0.277509 | [-0.287735, -0.267220] |
| E1 | Spearman | -0.268662 | [-0.278697, -0.258568] |
| E3 | Pearson | -0.037709 | [-0.048566, -0.026843] |
| E3 | Spearman | -0.035524 | [-0.046178, -0.024862] |

E3 is fully measured in these humans. Its use is authorized secondary human analysis, not model-facet rescue; the four model exclusions N3/C3/E3/N5 and AA27 failed model bridge remain unchanged.

## All ten items

Every coefficient below uses **higher stored item values = higher Anger**. [− key] marks a negatively worded original statement; it does not mean that a second reversal was performed. Full exact coefficients, original-wording-oriented signs and simultaneous bounds are in item_correlations.csv.

| Item | Official wording | E1 Pearson | E1 Spearman | E3 Pearson | E3 Spearman |
| --- | --- | --- | --- | --- | --- |
| 6 | Get angry easily. | -0.157 | -0.154 | +0.049 | +0.047 |
| 36 | Get irritated easily. | -0.250 | -0.248 | -0.024 | -0.020 |
| 66 | Get upset easily. | -0.207 | -0.205 | -0.095 | -0.093 |
| 96 | Am often in a bad mood. | -0.451 | -0.444 | -0.221 | -0.220 |
| 126 | Lose my temper. | -0.165 | -0.163 | +0.039 | +0.034 |
| 156 | Rarely get irritated. [− key] | -0.214 | -0.211 | -0.016 | -0.012 |
| 186 | Seldom get mad. [− key] | -0.146 | -0.142 | +0.030 | +0.029 |
| 216 | Am not easily annoyed. [− key] | -0.228 | -0.224 | -0.028 | -0.027 |
| 246 | Keep my cool. [− key] | -0.186 | -0.181 | -0.086 | -0.096 |
| 276 | Rarely complain. [− key] | -0.109 | -0.111 | +0.037 | +0.033 |

Original-wording-oriented r is original_key_sign×Anger-keyed_r; its CI signs/order are adjusted only for reporting. Thus the original positive statement “Keep my cool” is associated with *higher* Friendliness when read in its wording orientation (+.186), while its Anger-keyed score is associated with lower Friendliness (−.186). The same distinction applies to “Rarely complain” (+.109 wording-oriented versus−.109 Anger-keyed). No synthetic raw-category data are analyzed or exported.

All ten E1 coefficients are negative for both metrics, with simultaneous intervals below0. The facet average therefore does **not** conceal a positive Anger-item/Friendliness relationship. It does conceal differences in strength. “Am often in a bad mood” is strongest negative (Pearson−.450819); “Rarely complain,” in Anger-keyed direction, is weakest (−.109266). Getting irritated (−.250441) and upset (−.207232) lie between bad mood and getting angry (−.156765)/losing temper (−.164583). These wordings span irritability, general negative affect, temper and self-control/complaint content, but no new scored subfacets or latent factor separation is demonstrated.

The shared respondent bootstrap explicitly compares correlated correlation estimates. Every45 item pair per outcome/metric is retained; there are180 contrasts. A descriptive absolute difference≥.10 benchmark is not a clinical/behavioral cutoff. Summary:

| Outcome | Metric | Contrast intervals excluding0 | All contrasts | |Δr|≥.10 |
| --- | --- | --- | --- | --- |
| E1 | Pearson | 44 | 45 | 13 |
| E1 | Spearman | 44 | 45 | 12 |
| E3 | Pearson | 40 | 45 | 17 |
| E3 | Spearman | 39 | 45 | 17 |

Bad mood versus getting angry differs by−.294054 (the exported get-angry-minus-bad-mood contrast is+.294054, CI[+.283760,+.304349]). Bad mood versus the Anger-keyed “Rarely complain” differs−.341553, CI[−.353305,−.329800]. Conversely, getting upset versus the Anger-keyed “Rarely get irritated” differs only+.006802, CI[−.002979,+.016582]; that distinction is unresolved. Getting angry versus losing temper differs+.007819, CI[+.000414,+.015223], a statistically precise but small effect. We do not equate all detectable contrasts with meaningfully distinct constructs.

## Secondary Assertiveness comparison

E3 comprises taking charge, leading/influencing others, taking control, and reverse-keyed reticence/holding back opinions. It is an approach-related self-report facet, not a direct physiological/motivational mechanism or observed behavior measure. Total N2/E3 is slightly negative (r−.037709; rho−.035524), while individual items mix signs.

Getting angry easily (+.048833) and losing temper (+.039085) are small positive Pearson associations with E3, while bad mood (−.220635), being upset (−.094623), irritability (−.024196) and the Anger-keyed loss-of-cool item (−.086311) are negative. Thus it would be wrong to infer a uniform anger/approach link. Even losing temper and not keeping cool differ in sign. Some contrast intervals include0 (e.g. losing-temper versus Anger-keyed complaining difference+.002442, CI[−.009227,+.014111]). Wording polarity/method effects and broader affect content may contribute; these are plausible explanations, not tested causal or psychometric mechanisms.

## Distribution and nonlinear associations

Eight half-unit bins and three broad score bands were fixed before new outcomes. All fine-bin counts exceed4,600, so none needs the prespecified n<50 suppression. Fine-bin E1 means decline monotonically from3.863 at the lowest to2.904 at the highest Anger bin. Group boundaries refer only to observed questionnaire scale values, not diagnoses:

| Prespecified band | n | Mean N2 | Mean E1 | Within-band E1-on-N2 slope | Simultaneous95% slope interval |
| --- | --- | --- | --- | --- | --- |
| Low [1,2.5) | 44,967 | 1.875086 | 3.701997 | -0.253555 | [-0.281982, -0.225127] |
| Moderate [2.5,3.5) | 41,599 | 2.937181 | 3.479129 | -0.199138 | [-0.237710, -0.160565] |
| High [3.5,5] | 30,693 | 3.982762 | 3.192415 | -0.375521 | [-0.411679, -0.339362] |

Moderate-minus-low E1 mean is−.222868, CI[−.238189,−.207547]; high-minus-moderate is−.286714, CI[−.304651,−.268777]. Broad within-range associations remain negative, with a descriptively steeper slope at high scores. These conditional distributions are not evidence that changing anger changes friendliness.

We fit linear, quadratic and natural cubic spline models with fixed raw-score knots1,2,3,4,5 (no data-driven search). Identical five-fold assignments use seed2026102602; all new feature centering/scaling/coefficients use training respondents only. Only aggregate metrics/coefficients and a fold-assignment hash are exported, never human-level folds or predictions. Held-out comparisons:

| Model | Held-out MSE | Pooled held-out R² | Relative MSE reduction vs linear | Simultaneous95% reduction interval |
| --- | --- | --- | --- | --- |
| linear | 0.599743412 | 0.076924 | 0.0000% | reference |
| quadratic | 0.599219016 | 0.077731 | 0.0874% | [0.0313%, 0.1435%] |
| spline | 0.598542442 | 0.078772 | 0.2002% | [0.1146%, 0.2859%] |

The spline’s0.2002% MSE reduction is statistically detectable under this exploratory family but below the prespecified1% descriptive benchmark; the quadratic reduction is smaller. The fitted relation remains decreasing and the8-bin means show no sign reversal. The largest gridwise spline-minus-linear departure is−.207935 E1 units at N2=5.0 (384 respondents at that exact score; spline fitted mean2.741935, simultaneous band[2.685860,2.798011], versus linear2.949870). At N2=4.5 the difference is−.078284 with1,179 respondents at that score. These are descriptive fitted-model contrasts, not separately estimated simultaneous intervals for the model difference. The larger tail bend coexists with a small overall prediction gain; neither establishes an optimal anger level, nonlinear behavioral mechanism or causal effect. Nonlinear-model R² remains about.079: most individual Friendliness variance is not predicted by Anger alone. We do not extrapolate beyond1–5 or select a peak for interpretation.

## Resampling and multiplicity

Two thousand ordinary nonparametric respondent draws (seed2026102601) resample eligible people jointly with replacement; categorical contingency sufficient statistics preserve their joint dependence and exactly recompute tied ranks within every draw. No independent-item resampling, repeated reversal, population-norm recoding or human imputation occurs.

The primary approximate simultaneous95% max-standardized-deviation family includes224 prespecified endpoints:40 item correlations and4 facet correlations on Fisher-z scale plus180 dependent differences on correlation scale. A separate59-endpoint exploratory family includes41 spline conditional means,8 fine-bin means,3 broad means,3 broad slopes,2 adjacent broad means differences and2 held-out MSE reductions. Each family uses its own empirical higher95th quantile; they are not jointly controlled together. MSE-reduction resampling keeps already fitted OOF predictions fixed, so it is not a fully nested refit bootstrap. All estimation/interval tables and aggregate draws are retained, including small, null and contrary results. No unadjusted p-value/significance labels are used.

Bootstrap intervals assume the selected respondent records can be treated as exchangeable; deduplicating exact patterns does not identify all repeated people or remove selection/careless-response bias. The same source/reference has been inspected before, so neither full-cohort reuse nor new technical folds are untouched confirmation. Separate families and descriptive size benchmarks do not establish clinical or behavioral significance.

## Independent checks and reproducibility

The separate verifier imports neither primary nor source-gate code. It hashes all14 pinned inputs, streams raw fixed-width lines independently, reproduces eligibility/exact-pattern deduplication, checks the historical result using rank midpoints/scalar inverse normal, and recomputes all40 item/four facet correlations with direct-row SciPy Pearson/Spearman. Unscaled direct-row QR least squares independently verifies full curves, coefficients and all15 held-out fold/model metrics against the primary exact weighted contingency solver. Independent raw-bin means/slopes/correlations and10 explicit respondent bootstrap draws (all44 correlations and59 secondary outputs each) agree. All224/59 interval estimates/bounds and all180 contrasts are checked from aggregate draws.

There are 2,805 checked scalar/array values; maximum discrepancy across verification families 5.99e-13. All18 primary output files reproduce byte-for-byte in a fresh destination, including both2000-draw aggregate tables. There are no primary numerical warnings or undefined bootstrap outcomes; verifier warnings are recorded separately. Tie, constant/undefined, sign interpretation and intentional second-reversal refusal fixtures pass. Two PNGs are inspected directly, with SVG/PDF enlargement versions and independent file reproduction. This is algorithmic/process independence, not another human or agent reviewer.

No raw respondent rows, source IDs, item/profile vectors, resampled IDs, individual fitted values or predictions enter Git. Original raw data remain unchanged at their existing ignored external path. Only aggregate coefficients/draws/counts/correlations/figures/methods and verification hashes are committed. Historical AA26 corrections/withdrawals, AA27 failed model gate, all model exclusions and prior model studies remain unchanged. CPU only: no inference, paid compute, causal intervention or viewer deployment. Commit/push the dedicated branch, no merge, and stop for review.

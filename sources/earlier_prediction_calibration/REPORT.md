# Direct-12 post-hoc prediction-strength calibration

This is an authorized exploratory diagnostic, not a revision of the frozen
experiment. Original scientific freeze 84ff3d9c and results commit
33e3cbd9a82692c84f234be2b38ff639dd5c6992 remain unchanged. The frozen plan
excluded outcome-driven scalar corrections from its primary experiment;
the user's October 15 instruction separately authorizes this diagnostic.
The [analysis plan](ANALYSIS_PLAN.md) was written before calibration results.

## Baseline and inputs

All 278 external SHA-256 values, six frozen comparison code/plan hashes,
154-member scientific seal, 18 complete formal endpoints/members and all
committed source artifacts match. Original reference/calibration/test
membership and transformed-array fingerprints reproduce exactly, with sizes
30000/10000/10000, seed20260920, first-response-pattern deduplication and ten
already-keyed items/facet. See [fresh audit](results/INPUT_BASELINE_AUDIT.json).
No input repair or content alteration was needed. Formal contrast validation
reproduces eligibility, means, exact float32 units and first scheduled stops.

Only E1,O5,C5,O2,N2,E5,A3,O1,O6 enter this comparison. N3,C3,E3 remain
preserved partial extractions outside the primary nine. A3 is Altruism;
Assertiveness is E3 and is not substituted. Scenario and survey stay separate.
New Direct-12 extraction used Qwen3-32B; saved-bank compatibility remains
CONDITIONAL_LAYER_MATCHED_SAVED_BANK, with original bank checkpoint/masks unknown.
All original per-facet R², S, Pearson/Spearman and RMSE reproduce within1e-10;
actual verification errors are recorded numerically. Original macro R² is
−.2105510335134649/−.08423479427386835; human reference+.2929856514801089.

## Estimator and held-out results

On calibration humans only, D=prediction−reference mean and Z=observed−reference
mean. The common least-squares optimum is sum(D×Z)/sum(D²), clipped to[0,1].
Every transformed-unit squared error has equal weight; this minimizes pooled
SSE rather than equal-facet macro R². No new intercept, covariance coefficient,
scale or marginal transformation is fitted. Original coefficients are held
fixed; test predictions apply mean+λ×D unchanged. Positive λ preserves tied
ranks and therefore S/Pearson/Spearman; λ=0 is a constant baseline with S=0
and undefined prediction correlation. R² retains the original **test-mean SST**;
the reference mean is the prediction anchor, not the SST denominator.
For baseline reproduction, the same original persona and human-reference
coefficients are deterministically reconstructed with the frozen Ledoit–Wolf
estimator; calibration never changes these point coefficients.

| Source | Common λ | Original R² | Calibrated R² | Gain | SSE reduction | Facet-specific R² |
| --- | --- | --- | --- | --- | --- | --- |
| Scenario | 0.372342 | -0.210551 | +0.119950 | +0.330501 | 27.27% | +0.131999 |
| Survey | 0.442744 | -0.084235 | +0.150228 | +0.234463 | 21.56% | +0.159086 |

| Facet | Scenario original | Scenario common | Scenario facet | Survey original | Survey common | Survey facet | Human benchmark |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E1 Friendliness | -0.327546 | +0.081887 | +0.084865 | -0.052875 | +0.199169 | +0.199801 | +0.477332 |
| O5 Intellect | -0.296556 | +0.141436 | +0.141509 | -0.192630 | +0.140557 | +0.142588 | +0.302304 |
| C5 Self-discipline | -0.426220 | +0.092009 | +0.097413 | -0.220260 | +0.124378 | +0.128199 | +0.220589 |
| O2 Artistic interests | -0.194282 | +0.218076 | +0.221068 | -0.088650 | +0.204847 | +0.204909 | +0.313677 |
| N2 Anger | -0.233118 | -0.015576 | +0.004021 | -0.195393 | -0.011873 | +0.009325 | +0.159219 |
| E5 Excitement-seeking | -0.053680 | +0.076236 | +0.075717 | +0.045432 | +0.086135 | +0.089669 | +0.224275 |
| A3 Altruism | +0.166378 | +0.300115 | +0.344298 | +0.209818 | +0.321995 | +0.348662 | +0.448290 |
| O1 Imagination | -0.050113 | +0.184848 | +0.192361 | +0.014785 | +0.260081 | +0.264012 | +0.343775 |
| O6 Liberalism | -0.479822 | +0.000522 | +0.026739 | -0.278339 | +0.026766 | +0.044608 | +0.147410 |

All individual ordering/error metrics, SSE numerators, SST denominators and
SSE changes are in [test_results.csv](results/test_results.csv). Macro R² is
an equal-nine-facet mean, not pooled R²; reported SSE reduction is pooled across
all90,000 target observations. Original S=.322496993/.362933845 and human
S=.518044938 remain unchanged by positive shrinkage. Original predictions,
persona scores, human measures and coefficients remain preserved.

## Calibration strengths and fixed sensitivity

Common constrained/unconstrained λ=.372341951989 scenario and .442743561005
survey. Every facet optimum also lies inside[0,1]. The table reports calibration
data fits only; exact unconstrained values and cross-product/energy sufficient
statistics appear in [multipliers.csv](results/multipliers.csv).

| Facet | Scenario facet λ | Survey facet λ |
| --- | --- | --- |
| E1 | 0.326348 | 0.479709 |
| O5 | 0.367889 | 0.403824 |
| C5 | 0.302936 | 0.376240 |
| O2 | 0.428324 | 0.464844 |
| N2 | 0.121279 | 0.181714 |
| E5 | 0.363103 | 0.500374 |
| A3 | 0.602791 | 0.629162 |
| O1 | 0.437254 | 0.488987 |
| O6 | 0.179190 | 0.263282 |

Facet-specific calibration improves test macro R² over the common fit by
.012049/.008857, small relative to the common-scalar gain. It remains an
exploratory nine-parameter diagnostic on the same already examined cohort,
not a selected replacement for the primary common fit.

| Fixed λ (illustration only) | Scenario macro R² | Survey macro R² |
| --- | --- | --- |
| 0.00 | -0.000121 | -0.000121 |
| 0.25 | +0.106466 | +0.121413 |
| 0.50 | +0.106924 | +0.147905 |
| 0.75 | +0.001251 | +0.079356 |
| 1.00 | -0.210551 | -0.084235 |

The curve uses a predeclared0–1 grid and five fixed illustrative values.
No test-set optimum is reported or used to choose the calibration. Endpoint1
reproduces the frozen result; endpoint0 reproduces the reference-mean intercept
macroR²−.000120726. A favorable point on this curve is not new validation.

![Sensitivity curve](figures/multiplier_curve.png)

## Separate uncertainty

2000 paired held-out respondent resamples reuse the original seed20261014 and
row multiplicities across sources/conditions/facets. Fitted common/facet scalars
and all coefficients remain fixed. Each draw recomputes its own test-mean SST;
calibrated-minus-original differences are taken **within** the same draw.
Per-facet and macro95% percentile intervals retain every draw.

1000 whole-observed-question draws/source reproduce the original seeds and
eligibility, including rejected zero contributors. Each draw's original R²
matches the saved frozen uncertainty table. The frozen estimator propagates
direction uncertainty through the persona covariance model; its scalar is
refitted only on the fixed calibration cohort before test evaluation. A second
column holds the point-fitted common scalar fixed across direction draws.
Zero undefined joint draws occurred; all18000 facet definedness/denominator
records are retained. No new response or activation extraction is involved.

| Source | Respondent ΔR² | Question ΔR² (refit λ) | Question ΔR² (fixed λ) | Respondent calibrated R² | Question calibrated R² |
| --- | --- | --- | --- | --- | --- |
| Scenario | [0.319487, 0.342652] | [0.264843, 0.409225] | [0.263254, 0.408163] | [0.114029, 0.125346] | [0.101786, 0.136729] |
| Survey | [0.226238, 0.243229] | [0.200201, 0.291734] | [0.199461, 0.290429] | [0.143814, 0.156318] | [0.129927, 0.164508] |

![Separate uncertainty](figures/uncertainty.png)

These are separate descriptive95% families, not combined/joint bounds or
confirmatory significance tests. Fixed-fit respondent uncertainty excludes
calibration-fitting variation. Question uncertainty conditions on observed
eligibility, adaptive endpoints, fixed humans/personas and reference fit; it
omits judge error and released-bank provenance uncertainty. It does not measure
new-population transfer. No facet or unfavorable draw is selected away.

## Structural discrepancies remain

Scaling predictions around a reference mean leaves the original persona
correlation/covariance matrices and regression coefficients unchanged.
E1–N2 remains human−.280477 versus scenario+.709784/survey+.607053;
C5–O6 remains human−.227448 versus+.662943/+.698483. Both sources still match
21/36 relationship signs. These positive multipliers also preserve the sign
of every target-excluded prediction slope; they cannot reverse a mistaken
relationship. N2 remains negative under common calibration for both sources;
scenario O6 is only barely positive (+.000522). Even with facet-specific shrinkage, no
structural geometry repair has occurred. See all72 signed pairs in
[structural_discrepancies.csv](results/structural_discrepancies.csv).

The full-human benchmark macroR²+.292986 remains superior, with the original
same-dimensional n275 human control median+.271120 preserved as context, not
rerun or recalibrated. Shrinkage recovers useful error performance in this
cohort while preserving substantial structural and validation limits.

## Verification and provenance

[Independent numerical report](INDEPENDENT_NUMERICAL_VERIFICATION.json) uses a
separate streaming parser/NormalDist human transform, independent BF16 decoder,
Ledoit–Wolf moment/covariance-block solves, scalar math.fsum statistics,
bounded numerical minimization, all test metrics, exact tied-rank invariance,
selected explicit respondent/question repeats and all question-fit arithmetic.
Sorted linear percentile calculations independently check every interval.
This is an independent numerical implementation in the same coordinating
process; no extra agent is claimed. A full rerun in a fresh ignored destination
checks byte equality of all numerical outputs and private point caches.
[Reproduction](REPRODUCE.md) documents commands and validation.

The local Apple BLAS runtime emits matmul divide/overflow/invalid warnings
also seen in the frozen study. All outputs are finite, baseline/draw identities
and the independent einsum/scalar route pass; warnings are retained in local
logs and not treated as evidence of scientific effects. Metadata records the
actual CPU environment and seeds. Figures are aggregate, reviewed at full and
narrow widths; no respondent-level table, IDs, arrays, weights, credentials,
environment or caches are added to Git.

No scientific protocol, vector, grade, eligibility threshold, score, coefficient
or historical execution record changed. The normal-shaped persona marginals
are imposed and released-bank checkpoint/masks remain unknown. The already
examined test cohort means this is exploratory, even though multiplier fitting
uses calibration humans only. No human-plausibility, causal, behavioral,
wellbeing or steering claim follows. No provider access, GPU, inference,
rescoring or paid compute. Conservative historical carry remains
**$20.396661/$25**; resources remain as previously verified deleted. Publish on
the new calibration branch only and stop for review; no automatic merge.

# Direct-30 B: prediction-strength rescaling

Post-hoc local CPU diagnostic, separate from the frozen Direct-30 B experiment. A calibration-only common multiplier substantially improves test macro R², while preserving ordering and every original pair correlation. It does not repair the underlying relationship structure or establish behavioral validity.

## Main results

| Format | Common λ | As measured R² | Common rescaled R² | Gain | Exploratory facet-specific R² |
|---|---:|---:|---:|---:|---:|
| Scenario | 0.529452 | +0.045794 | +0.254224 | +0.208430 | +0.294975 |
| Survey | 0.549380 | +0.078076 | +0.252502 | +0.174426 | +0.298105 |

Macro R² is the equal-26-facet mean, not pooled R². The untouched human-reference benchmark is **+0.584196**, with ordering S **0.747793**; reference-mean prediction gives macro R² **−0.000153**. Scenario/survey ordering S remains **0.510899/0.511972**. Common rescaling reduces pooled test SSE by **21.83%/18.86%**. These are descriptive held-out results in an already examined cohort, not independent confirmation.

The common multiplier improves **20/26 scenario** and **19/26 survey** facets; it worsens the other **6/7**. Scenario E1, O2, N2, N6, C6 and A4 worsen. Survey E1, C5, N2, N6, C6, N1 and A4 worsen. Thus the result is not uniform improvement. All 26 scenario common-rescaled point R² values are positive; survey has 24 positive, with **O6 −0.000006** and **E4 −0.106314** remaining nonpositive. Do not round the small O6 negative into an asserted positive.

Facet-specific multipliers are an exploratory 26-parameter diagnostic per format. Their macro R² is **0.294975/0.298105**, still below the human benchmark. Scenario N6/C6 and survey N2/A4 have unconstrained optima above 1, retained explicitly and clipped to 1. No facet or format is selected using its test performance.

## Method and baseline gate

The [analysis plan](ANALYSIS_PLAN.md) was committed at **3feb147098daf5b958ee184692b5b49a0d152611** before any baseline/calibration calculation, on a new branch from main **bdb8f3d00986bd1e8d5cc8d443eb756faeba4448**. The notebook branch was not modified. Frozen Direct-30 B source: **bf99d3def5b1af4ccc5831bc6659c9e40560c337**; Direct-12 estimator source: **3aa46590b2a048997b8a4b9149adf99ffe5a94e6**. [Source manifest](results/SOURCE_MANIFEST.json) binds exact Git bytes. Frozen original results remain unchanged.

The local Johnson `IPIP300.dat` matches the AA27 SHA-256 and 102,949,853-byte length. The 300-item specification hash also matches. Items are already keyed and were not reversed again. Eligibility remains complete responses, ages 18–80, first exact-pattern deduplication: 117,260 eligible records, 117,259 distinct patterns. Seed **20260920** uses original 60%/20%/20% boundaries then caps to reference **30,000**, calibration **10,000**, test **10,000**. Reference-only rank-normal transforms and all membership/transformed-array fingerprints match exactly.

Use the final 26 facets in their frozen completion order; N3, C3, E3 and N5 remain excluded. Reconstruct coefficients with exact frozen function bodies and the saved 275-persona score matrices. No activations or model outputs are newly extracted. The [baseline gate](results/BASELINE_GATE.json) reproduces all **52 model facet R² values**, S/Pearson/Spearman/RMSE, human-reference R² and all **325 unique reference-human correlations** (650 source-labeled rows). Largest baseline discrepancy: **5.15e-14**, below **1e−9**. Calibration begins only after the gate passes.

With human-reference mean μ, calibration residuals D=original prediction−μ and Z=observed−μ, fit λ_raw=Σ(DZ)/Σ(D²) per format and λ=clip(λ_raw,0,1). This weights every transformed-unit squared error equally and minimizes pooled SSE; it does not optimize equal-facet macro R². There is no new intercept, marginal transform, direction, covariance coefficient or test-set fit. Original frozen Ledoit–Wolf coefficients and intercepts remain fixed after deterministic reconstruction. Test prediction is μ+λ(original prediction−μ); R² uses the **test mean** in SST. The reference mean anchors predictions, not the denominator. Facet-specific estimates use the same rule columnwise.

## All facets

| Facet | Scenario original | Common | Facet-specific* | Survey original | Common | Facet-specific* |
|---|---:|---:|---:|---:|---:|---:|
| E1 | +0.356994 | +0.338125 | +0.381333 | +0.415895 | +0.394522 | +0.440090 |
| O5 | -0.278103 | +0.014359 | +0.052839 | -0.297242 | +0.063926 | +0.104735 |
| C5 | +0.409242 | +0.418944 | +0.458114 | +0.393482 | +0.345979 | +0.400227 |
| O2 | +0.248786 | +0.245717 | +0.272527 | +0.233053 | +0.238785 | +0.258654 |
| N2 | +0.251807 | +0.227069 | +0.262087 | +0.382069 | +0.299537 | +0.382069 |
| E5 | -0.007629 | +0.086906 | +0.086893 | +0.183619 | +0.187975 | +0.202698 |
| A3 | +0.408812 | +0.464761 | +0.494712 | +0.179618 | +0.238224 | +0.244471 |
| O1 | +0.164159 | +0.263725 | +0.268514 | -0.129854 | +0.247976 | +0.260687 |
| O6 | -0.342059 | +0.026000 | +0.071945 | -0.364444 | -0.000006 | +0.060966 |
| N6 | +0.446677 | +0.333863 | +0.446677 | +0.489978 | +0.403249 | +0.491154 |
| A1 | +0.225362 | +0.355996 | +0.363555 | +0.181652 | +0.259783 | +0.265020 |
| C2 | -0.798109 | +0.056648 | +0.164598 | -0.503149 | +0.148555 | +0.214291 |
| E6 | +0.222994 | +0.232682 | +0.253493 | +0.236016 | +0.333295 | +0.340530 |
| C4 | -0.402179 | +0.328404 | +0.360513 | -0.394063 | +0.176824 | +0.224266 |
| O4 | -1.246850 | +0.171812 | +0.327755 | -0.394666 | +0.240792 | +0.285823 |
| C6 | +0.384179 | +0.275305 | +0.384179 | +0.410637 | +0.351540 | +0.415379 |
| A5 | -0.084410 | +0.286086 | +0.291040 | -0.467668 | +0.021941 | +0.096188 |
| O3 | +0.132494 | +0.158755 | +0.167312 | +0.072108 | +0.159581 | +0.159864 |
| A2 | +0.088281 | +0.186688 | +0.187979 | +0.042187 | +0.154994 | +0.155038 |
| E2 | +0.068133 | +0.292768 | +0.292359 | +0.270003 | +0.342681 | +0.354105 |
| E4 | -0.676000 | +0.073771 | +0.160658 | -0.901046 | -0.106314 | +0.071069 |
| A6 | +0.316079 | +0.374663 | +0.396091 | +0.253850 | +0.308683 | +0.321342 |
| N1 | +0.382484 | +0.418083 | +0.449699 | +0.659303 | +0.532975 | +0.659342 |
| C1 | +0.369035 | +0.460130 | +0.482101 | +0.494256 | +0.516225 | +0.555777 |
| N4 | +0.277657 | +0.291649 | +0.317076 | +0.197337 | +0.398788 | +0.399890 |
| A4 | +0.272810 | +0.226905 | +0.275293 | +0.387041 | +0.304535 | +0.387041 |

*Exploratory facet-specific rescaling. Exact values, both multiplier versions and 95% fixed-fit respondent intervals are in [facet_comparison.csv](results/facet_comparison.csv). [test_results.csv](results/test_results.csv) preserves SSE/SST, correlations, S and benchmarks; [multipliers.csv](results/multipliers.csv) includes calibration sufficient statistics.

![Per-facet rescaling](figures/facet_rescaling.png)

Figure: every final direct Qwen facet, with scenario and survey shown separately. Horizontal coordinates are held-out test R². Grey is as measured; colored dots and bars are common rescaling with 95% fixed-fit respondent intervals; crosses are exploratory facet-specific rescaling. These are conditional questionnaire predictions from model-derived geometry, not observed model behavior or historical proxies. Intervals do not include question/extraction uncertainty.

## Separate uncertainty

| Format | Respondent calibrated R² | Respondent gain | Question calibrated R² | Question gain |
|---|---|---|---|---|
| Scenario | [+0.249420, +0.258568] | [+0.203270, +0.213521] | [+0.232485, +0.269422] | [+0.172811, +0.244662] |
| Survey | [+0.247365, +0.257162] | [+0.169590, +0.179424] | [+0.227522, +0.269177] | [+0.151066, +0.224546] |

All intervals above are descriptive **95% percentile** intervals. Required respondent uncertainty uses **2,000** paired test-row resamples, seed **20261014**, shared across all facets/formats/conditions, with all fits and multipliers fixed. Each draw recomputes its own test-mean SST. Gain intervals are paired within draws; no undefined draws occurred. These omit calibration-fit, reference-fit, extraction and population-shift uncertainty. The frozen study's 98.75% families remain historical; these 95% diagnostic intervals do not replace them.

Optional whole-observed-question resampling completed in **40.51 seconds**, under the 30-minute limit. It retains 1,000 draws per format, seeds **20261113/20261114**, original observed questions, rejected zero contributions, accepted multiplicities, formal endpoints and facet order. All 52 local endpoint seals and 275 role-tensor hashes were verified. Every draw's original R² matches the saved aggregate frozen draw table within **8.59e-14**. Scalars refit on calibration respondents only; a second result holds the point scalar fixed across direction draws. Both variants and all definedness rows are retained in [question outputs](questions/). No undefined draw occurred. Question and respondent intervals remain separate, not combined into a joint bound; adaptive endpoints, judged eligibility and the existing role bank are conditioned on.

## What calibration does not change

All fitted common and facet-specific multipliers are positive. Exact tied prediction ranks and S remain unchanged; Pearson/Spearman differences are numerical roundoff only. All **325 persona pair correlations per format** and **325 human reference correlations** are unchanged. A positive affine scaling of the persona score columns independently reproduces the same correlations. Conditional prediction-column correlations are a separate quantity and are not substituted for the original relationship geometry.

Model/human relationship signs still agree in **217/325 scenario** and **204/325 survey** pairs. In particular, original human–model disagreements remain. Positive scalar rescaling cannot reverse incorrect relationship signs or validate construct equivalence. Better squared-error performance is evidence about prediction magnitude on this cohort, not repaired human personality structure, causal control, wellbeing, safety or observed behavior. Normal-shaped persona marginals were imposed, and original released-bank checkpoint/response-mask provenance remains unresolved. AA26 corrections/withdrawals, AA27's failed original bridge gate, and C/T/F distinctions are unchanged.

## Verification and execution

[Independent verification](INDEPENDENT_VERIFICATION.json) uses a separate streaming parser/NormalDist transform, moment-based covariance/block solves, math.fsum multipliers/test R², bounded calibration minimization, exact tied-rank invariance, all relationship cells, explicit respondent draws 0/17/1999 and sorted linear percentile checks. [Question verification](QUESTION_VERIFICATION.json) expands observed questions in float64 for draws 0/17/999 per source and independently checks readouts, coefficients, calibration and test results. This is computational independence in one local coordinating process, not an independent human scientific review.

[Deterministic reproduction](DETERMINISTIC_VERIFICATION.json) compares all 11 primary aggregate files and all four question numerical/provenance files in new ignored destinations, excluding declared runtime/environment/warning metadata. [Final verification](FINAL_VERIFICATION.json) binds source/output hashes, plan preservation, syntax, links, privacy scope and actual figure review. No participant rows, IDs or individual predictions are committed. Private verification arrays and full repeated warning logs stay under ignored `data_external/`.

The local Apple numerical runtime emits the same divide/overflow/invalid matmul diagnostics documented in the frozen studies. All outputs are finite; independent scalar/einsum paths and exact baseline/draw identities pass without relaxed scientific tolerance. Primary warning records and a compact question warning count/message summary are retained; the complete duplicate question warning log is retained locally and SHA-bound. Actual CPU environment and timings are in results/RUN_METADATA.json and questions/STATUS.json.

No inference, GPU, extraction, grading, paid computation, viewer publication or main merge occurred. [REPRODUCE.md](REPRODUCE.md) documents safe reruns. Push the new branch and stop for scientific review.

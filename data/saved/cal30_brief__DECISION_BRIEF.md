# Direct-30 B rescaling — decision brief

**Prediction magnitude explains a substantial part of the squared-error deficit; rescaling improves the average without changing ordering or the original relationship geometry.**

| Format | Common λ | As measured R² | Common rescaled R² | Gain | Exploratory facet-specific R² |
|---|---:|---:|---:|---:|---:|
| Scenario | 0.529452 | +0.045794 | +0.254224 | +0.208430 | +0.294975 |
| Survey | 0.549380 | +0.078076 | +0.252502 | +0.174426 | +0.298105 |

The common multipliers are fitted only on the frozen 10,000 calibration respondents and evaluated on the untouched 10,000 test respondents. Original reference-only transforms, 26-facet membership, seed/splits, coefficients and intercepts remain fixed. All 52 original R² cells and all 325 human reference correlations passed the baseline gate before fitting.

The common method improves 20/26 scenario and 19/26 survey facets; 6/7 worsen. Survey E4 remains negative (−0.106314) and O6 is essentially zero but slightly negative (−0.000006). Facet-specific results are exploratory and do not replace the common fit. The human-reference benchmark remains higher at +0.584196.

Two thousand paired respondent resamples give common-rescaling macro R² intervals **[+0.249420, +0.258568]** / **[+0.247365, +0.257162]**. One thousand question resamples per format completed in 40.5s; their intervals are **[+0.232485, +0.269422]** / **[+0.227522, +0.269177]**. These are separate conditional 95% intervals, not population validation or joint bounds.

S stays 0.510899/0.511972. All 325 pair correlations and their disagreements remain: prediction rescaling does not repair geometry or establish behavioral, causal, wellbeing or safety outcomes. The already examined cohort makes this post-hoc diagnostic exploratory. AA26 corrections and AA27's failed bridge remain intact.

[Per-facet results and intervals](results/facet_comparison.csv) · [Full report](REPORT.md) · [Figure](figures/facet_rescaling.png) · [Independent checks](INDEPENDENT_VERIFICATION.json) · [Reproduction](REPRODUCE.md).

Local Mac CPU only; no raw respondent exports, paid compute or notebook-branch edits. Stop after branch push; no merge.

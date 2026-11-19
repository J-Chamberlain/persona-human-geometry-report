# Direct-12: excessive prediction strength explains much of the negative R²

Calibration-only shrinkage recovers **0.330501 macro R² in scenario** and
**0.234463 in survey**. Both become positive: **+0.119950 / +0.150228**, from
the original **−0.210551 / −0.084235**. Test squared error falls **27.27% /
21.56%**. This supports excessive magnitude as a substantial contributor to
the negative results; it does not repair the relationship structure.

| Source | Common λ | Original R² | Calibrated R² | Gain | SSE reduction | Facet-specific R² (exploratory) |
| --- | --- | --- | --- | --- | --- | --- |
| Scenario | 0.372342 | -0.210551 | +0.119950 | +0.330501 | 27.27% | +0.131999 |
| Survey | 0.442744 | -0.084235 | +0.150228 | +0.234463 | 21.56% | +0.159086 |

Multipliers were fitted on the existing 10,000 calibration humans only, around
the existing reference mean, with no new intercept, regression coefficient or
reference-transform fit. Both unconstrained optima lie inside [0,1] and equal
the primary constrained estimates. Test outcomes never selected a multiplier.
The human-reference benchmark stays **+0.292986**, well above both calibrated
sources. Ordering is unchanged: scenario S=.322497; survey S=.362934; human
S=.518045. Shrinkage improves magnitudes without improving rankings.

![Original, calibrated and human-reference performance](figures/facet_R2.png)

Scenario paired-respondent 95% interval for the gain: [0.319487, 0.342652]. Separate question interval: [0.264843, 0.409225].

Survey paired-respondent 95% interval for the gain: [0.226238, 0.243229]. Separate question interval: [0.200201, 0.291734].

![Illustrative sensitivity; fitted values use calibration only](figures/multiplier_curve.png)

Calibration strength varies: scenario facet λ=.121–.603; survey .182–.629.
Facet-specific calibration adds only **.012049 / .008857** macro R² beyond the
common scalar (exploratory). N2 remains negative under common calibration in
both sources; scenario O6 is only barely positive (+.000522). All adverse original facets
remain in the report. E1–N2 and C5–O6 sign reversals are unchanged; both sources
still match only 21/36 human relationship signs.

**Decision:** magnitude is a major remediable component of this particular
prediction deficit. Retain the original negative transfer result and describe
calibration as a separate post-hoc diagnostic. This already examined test cohort
cannot supply an untouched confirmatory validation. Neither positive calibrated
R² nor stable extraction establishes human plausibility, behavioral validity,
wellbeing, steering success or causal effects.

All inputs/memberships and baseline metrics reproduce. Separate numerical
verification and a full deterministic diagnostic rerun are in the linked
[report](REPORT.md). No inference, rescoring, extraction, GPU or paid compute.

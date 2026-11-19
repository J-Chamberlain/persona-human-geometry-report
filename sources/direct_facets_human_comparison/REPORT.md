# Direct-30 B: aggregate comparison and terminal closeout

N1, C1, N4 and A4 each converged under the frozen rules, bringing the measured comparison to **26/30 facets**. Historical N3, C3 and E3 partials and A's unconverged N5 remain excluded. Nothing was regenerated, rejudged or rescued. The existing controller performed the primary CPU job once, after verified pod deletion.

Across the changed set of 26 targets, model macro R² is **+0.045794 scenario / +0.078076 survey**, versus **+0.584196 human-reference**. These descriptive means must be read separately from fixed-target gains. The previous 22 targets change by −0.001908/+0.012538 when B's four predictors are added: the scenario change is negative. The larger 26-target average includes four newly measured targets and does not establish general improvement on old targets.

## Fixed target comparisons

Each target is excluded from its own predictor set. Gains compare the same targets using 26 predictors versus that target set's original predictor set. No dedicated joint uncertainty interval is claimed for these gains; the 26-target intervals cannot be borrowed.

Original 9 baseline R² -0.210551/-0.084235; Original 15 baseline R² -0.114504/-0.053389; Previous 22 baseline R² -0.003153/+0.000736 (scenario/survey, respectively). These historical baselines remain unchanged.

| Fixed targets | Scenario R² | Survey R² | Scenario gain | Survey gain |
| --- | --- | --- | --- | --- |
| Original 9 | +0.134668 | +0.110689 | +0.345219 | +0.194923 |
| Original 15 | -0.022673 | +0.040798 | +0.091831 | +0.094186 |
| Previous 22 | -0.005061 | +0.013274 | -0.001908 | +0.012538 |

The original 9 and 15 outputs reproduce at the frozen tolerance; the independent review also checks every previous 22/fixed 9/fixed 15 row and all priority-prefix changes. All negative prefix gains remain in the exported tables.

![Per-target squared-error performance](combined_human_profiles/figures/conditional_R2.png)

| Target | Scenario R² | Survey R² | Human-reference R² |
| --- | --- | --- | --- |
| E1 | +0.356994 | +0.415895 | +0.771989 |
| O5 | -0.278103 | -0.297242 | +0.521818 |
| C5 | +0.409242 | +0.393482 | +0.666693 |
| O2 | +0.248786 | +0.233053 | +0.399718 |
| N2 | +0.251807 | +0.382069 | +0.633007 |
| E5 | -0.007629 | +0.183619 | +0.613127 |
| A3 | +0.408812 | +0.179618 | +0.708409 |
| O1 | +0.164159 | -0.129854 | +0.427431 |
| O6 | -0.342059 | -0.364444 | +0.303784 |
| N6 | +0.446677 | +0.489978 | +0.783830 |
| A1 | +0.225362 | +0.181652 | +0.446000 |
| C2 | -0.798109 | -0.503149 | +0.452586 |
| E6 | +0.222994 | +0.236016 | +0.570316 |
| C4 | -0.402179 | -0.394063 | +0.653325 |
| O4 | -1.246850 | -0.394666 | +0.523417 |
| C6 | +0.384179 | +0.410637 | +0.594270 |
| A5 | -0.084410 | -0.467668 | +0.477524 |
| O3 | +0.132494 | +0.072108 | +0.548352 |
| A2 | +0.088281 | +0.042187 | +0.531270 |
| E2 | +0.068133 | +0.270003 | +0.689433 |
| E4 | -0.676000 | -0.901046 | +0.483356 |
| A6 | +0.316079 | +0.253850 | +0.563354 |
| N1 | +0.382484 | +0.659303 | +0.775251 |
| C1 | +0.369035 | +0.494256 | +0.729194 |
| N4 | +0.277657 | +0.197337 | +0.703132 |
| A4 | +0.272810 | +0.387041 | +0.618519 |

Ordering S is +0.510899/+0.511972 versus human +0.747793; human-intercept R² is -0.000153. Ordering and squared-error performance answer different questions. The original near-null/negative 15 and 22 comparisons remain historical findings, and the new negative targets and sign reversals remain visible. Constant-predictor correlations and undefined cells remain undefined; they are not replaced with zero.

## Separate uncertainty families and controls

| Family | Format | 98.75% macro R² interval | Defined / total |
| --- | --- | --- | --- |
| Respondents; fits fixed | scenario | [+0.034627, +0.057040] | 2000/2000 |
| Respondents; fits fixed | survey_style | [+0.065741, +0.090130] | 2000/2000 |
| Questions; conditional extraction | scenario | [-0.025264, +0.109686] | 1000/1000 |
| Questions; conditional extraction | survey_style | [-0.016034, +0.125594] | 1000/1000 |

There are 1,000 question draws/source, 2,000 paired respondent draws and 1,000 controls/type/source. Question resampling conditions on frozen eligibility and adaptive endpoints; respondent resampling keeps predictions/fits fixed. These are separate uncertainty families, not joint intervals or new independent human samples. Undefined joint extraction draws: {"scenario": 0, "survey_style": 0}. All multiplicities, retained/undefined counts, intervals and aggregate draw tables are preserved. Matched 275-human benchmarks, within-column shuffles, facet-label permutations and joint-row invariance controls remain in their tables; no control alters the primary estimator. Calibration slopes are diagnostics only: no multiplier or calibration was fitted/applied.

Both question-resampling R² intervals span zero (scenario −0.025264 to +0.109686; survey −0.016034 to +0.125594). Fixed-fit respondent intervals are positive (scenario +0.034627 to +0.057040; survey +0.065741 to +0.090130). This difference limits the positive 26-target point estimates: they are sensitive to which eligible extraction questions contributed, even while the saved predictions are consistently positive over respondent resamples. Neither family is a joint confidence claim.

| Format; 325 relationships | Pearson | Spearman | RMSE | Sign agreement |
| --- | --- | --- | --- | --- |
| scenario | +0.444216 | +0.436862 | +0.483722 | +0.667692 |
| survey_style | +0.424178 | +0.410574 | +0.520359 | +0.627692 |

E1–N2: human -0.280477, scenario +0.709784, survey +0.607053. C5–O6: human -0.227448, scenario +0.662943, survey +0.698483. These structural errors persist despite positive fixed 9/15 point gains.

The human reference 30,000 / calibration 10,000 / test 10,000 membership and reference-only transformations remain frozen. Previously inspected humans make this exploratory. Rank transforms impose normal-shaped marginals. Human observational associations, model geometric projections and demonstrated causal effects remain distinct; no causal behavior, wellbeing or human-plausibility claim follows. The saved 275-persona bank has unknown original checkpoint/response masks, so compatibility remains conditional. Actual extraction used pinned Qwen3-32B/tokenizer 9216db5781bf21249d130ec9da846c4624c16137, block 48 with all 64 layers retained, separate formats and unchanged scorer/eligibility/stopping rules.

## Independent review and preservation

Verification uses independent human parsing/NormalDist, ZIP BF16 decoding, scalar ranks/metrics, Ledoit–Wolf moments/block solves, every formal endpoint seal, point/prefix/fixed-target arithmetic, selected explicit uncertainty/control draws and all saved interval/count arithmetic: **11627 checks**, maximum discrepancy 1.473198746326787e-08. The preselected draws and tolerances are recorded. All saved new B stopping checkpoints additionally pass **66 explicit-row/bootstrap checks**, maximum discrepancy 2.3422643802284426e-07; frozen pass/fail/first endpoint decisions agree without threshold ambiguity. This is verification of saved outputs, not a second full primary uncertainty job or an independent person's review.

RuntimeWarnings are retained in INDEPENDENT_NUMERICAL_WARNINGS.log and the original controller record. Independent arithmetic and finite assertions support the saved results without changing math or suppressing warnings. All 39 original figures were reviewed at full and 390px phone width; dense heatmaps/persona profiles require zoom. [Readable aggregate companion](display_companions/README.md) preserves all target estimates in phone-sized panels, while the [figure gallery](FIGURES.html) links original images and captions. Original scientific figure bytes remain unchanged.

The ordering plot's legend overlaps some upper bars; FIGURE_REVIEW.json records this display limitation, and exact values remain in the original aggregate CSV. PRIMARY_RUNTIME_WARNINGS.json preserves exact warning messages/counts/source hashes; the complete warning-only extract is retained in the private CPU archive.

CPU_OUTPUT_INVENTORY.json binds every original output and marks compact Git inclusion. Full aggregate draws, warnings, verifier source, reports and metadata are sealed in a separate private CPU archive; cpu_durable contains its fresh-download/every-member receipt. Final publication is complete only when FINAL_VALIDATION.json and the verified remote records tip accompany this report. No raw human rows, individual predictions, weights, activation arrays, credentials or environments belong in this export.

The authorized study is closed after these checks, durable archive and verified records publication. Stop for scientific review; calibration, excluded-facet rescue, further extraction and another paid attempt require separate authority.

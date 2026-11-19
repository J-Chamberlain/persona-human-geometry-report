# Facet extraction convergence and block-48 persona geometry

Saved-artifact CPU audit, executed November 5, 2026 under the requested November 6 package name. Branch `codex/facet-convergence-geometry-20261106`; base main `a00af3d`. Plans were committed before results: `f8dd65f` (stopping audit) and `e769b30` (user-approved block-48 geometry amendment).

## Findings

The frozen extraction chain qualifies 26 of 30 facets in both formats. Across those 52 format endpoints, the first passing checkpoint is 16–48 accepted questions: scenario counts are 4 at 16, 17 at 24, 3 at 32 and 2 at 48; survey-style counts are 1 at 16, 12 at 24, 8 at 32 and 5 at 48. E5 stops earliest in both formats (16/16). Scenario E6/O3/C1 also stop at 16. E4 and O6 are latest in both formats (48/48); survey E2/C2/C5 also require48. No qualifying endpoint requires64.

All252 distinct saved checkpoints, all frozen phase statuses and all 55 format-level first passes are retained. N3/C3/E3/N5 remain excluded: N3 survey, C3 scenario and E3 scenario each pass at 24, while their other formats do not pass. N5 passes neither format. A format-level pass inside an excluded facet does not qualify it for the 26-facet comparison. All checkpoint statistics were available in sealed summaries:252 rows read, zero missing-statistic reconstructions. Separate independent vector recomputation verifies 75 checkpoints across 20 formats.

The familiar viewer axes use role vectors averaged across all 64 stored layers. They were not used to project block48 question contrasts. With the user's explicit approval, we instead fit **PC1-48..PC5-48** to saved role row48. PC1-48/PC2-48/PC3-48 closely match viewerPC1/PC2/PC3 across 275 personas (r=+.981878/+.967881/+.976156), satisfying the requested |r|≥.9 descriptive threshold. PC4-48 matches viewerPC4 with reversed sign (r=−.912117). PC5-48 is a **different axis** relative to all five viewer PCs (largest |r|=.240615, with viewerPC4). Sign choices are arbitrary coordinate conventions; first-three signs were aligned to same-index viewer scores, not rotated or reassigned.

## Frozen rule and estimator

At accepted-question checkpoints8/12/16/24/32/48/64, average raw paired high-minus-low contrasts at **block48, hidden-tuple index49** with equal accepted-question weight. Each accepted question is one paired sampling unit. For each checkpoint reset NumPy default_rng to seed 20260924, draw 1,000 bootstrap sets of n paired questions with replacement, and calculate cosine between each bootstrap mean and the observed mean. The first checkpoint with n ≥ 16, bootstrap cosine p05≥.95, and cosine to the previous scheduled mean≥.98 is the accepted stop. Positive norm is required. n=8 cannot pass; n=12 remains ineligible even if its numerical cosines were high.

The frozen implementation uses float32 arrays/means and bootstrap multiplicities; linear .05 quantile. Successive means follow the scheduled checkpoints, not every question. Batch overshoot can leave accepted extras: they have zero formal endpoint weight. We do not evaluate new post-stop gates simply because enough extras exist. The qualified52 means use1,464 formal question pairs;447 additional accepted pairs remain visible only as extras. Rejected pairs never enter these directions.

[Stopping histories](results/stopping_histories.csv) contain facet, format, first-evaluation run/phase, n, both cosines, pass/fail, final accepted stopping n, read/recomputed flag and summary/prefix hashes. [All occurrences](results/checkpoint_occurrences.csv) retain copied continuation histories; they are not new evaluations. [Counts](results/final_question_counts.csv) distinguish accepted availability, extras, format status and facet qualification.

## Stopping table

A dash means no accepted stopping point; it does not mean zero accepted questions.

| Facet | Scenario stopping n | Survey-style stopping n | Final facet status |
|---|---:|---:|---|
| N1 | 24 | 32 | Qualified |
| N2 | 24 | 24 | Qualified |
| N3 | — | 24 | Excluded |
| N4 | 24 | 32 | Qualified |
| N5 | — | — | Excluded |
| N6 | 24 | 24 | Qualified |
| E1 | 24 | 24 | Qualified |
| E2 | 24 | 48 | Qualified |
| E3 | 24 | — | Excluded |
| E4 | 48 | 48 | Qualified |
| E5 | 16 | 16 | Qualified |
| E6 | 16 | 24 | Qualified |
| O1 | 24 | 24 | Qualified |
| O2 | 24 | 24 | Qualified |
| O3 | 16 | 32 | Qualified |
| O4 | 24 | 32 | Qualified |
| O5 | 24 | 24 | Qualified |
| O6 | 48 | 48 | Qualified |
| A1 | 24 | 24 | Qualified |
| A2 | 24 | 24 | Qualified |
| A3 | 24 | 24 | Qualified |
| A4 | 24 | 24 | Qualified |
| A5 | 24 | 32 | Qualified |
| A6 | 32 | 32 | Qualified |
| C1 | 16 | 24 | Qualified |
| C2 | 32 | 48 | Qualified |
| C3 | 24 | — | Excluded |
| C4 | 24 | 32 | Qualified |
| C5 | 32 | 48 | Qualified |
| C6 | 24 | 32 | Qualified |

Unconverged formats exhausted the saved banks with N3 scenario11, C3 survey13, E3 survey46, N5 scenario10 and N5 survey23 accepted questions. Their last evaluated checkpoints are8/12/32/8/16 respectively. Unaccepted terminal means are labeled `excluded_partial_not_accepted` and never presented as qualified finals.

## Inputs and preservation

| Phase | Source commit | Sealed summaries | Distinct checkpoints first recorded here |
|---|---|---:|---:|
| direct12_v2 | `e06ff9a` | 37 | 97 |
| direct18_production | `a080eea` | 5 | 20 |
| direct18_continuation | `a080eea` | 14 | 32 |
| direct30_a_initial | `2a8da23` | 0 | 0 |
| direct30_a_cpu_recovery | `507dced` | 1 | 4 |
| direct30_a_continuation | `a5279e3` | 26 | 66 |
| direct30_b | `bf99d3d` | 10 | 33 |

The initial Direct-30 A run has no completed format summary (preserved attempted/incomplete ledger); its saved CPU recovery supplies C6 scenario before continuation. Continuations copy some older histories;252 is a deduplicated count, not the number of summary occurrences. [Phase coverage](results/PHASE_COVERAGE.json) verifies each available frozen ledger, including partial, not-attempted and incomplete statuses. The combined B input supplies all 52 qualified endpoints with sealed summaries and question arrays.

Original local roots are the `persona-human-geometry-v2-20261014/data_external/direct12_execution_v2_runs/` and `persona-human-geometry-direct18-execution-20261015/data_external/` trees next to the original repository. Exact run names, paths and summary hashes are in [ENDPOINTS](results/ENDPOINTS.json) and [INPUT_HASHES](results/INPUT_HASHES.json). Six excluded N3/C3/E3 format directories had summaries/seals but no delta arrays. We recovered175 accepted arrays from their existing pinned release archives into a separate local cache, without modifying source directories or opening response-text members. [Archive recovery](verification/ARCHIVE_RECOVERY.json) records full archive SHA256/length, source-spec hashes, release tag and every recovered member hash. A first verifier invocation detected the missing local arrays and stopped before numerical comparison; it passed after this recovery. No numerical failure was suppressed.

## Compatible basis and relationship to the viewer

The [original construction audit](../../outputs/extended_persona_pca/persona_pca_construction_audit.md) and its pinned implementation establish:275 released Qwen/Qwen3-32B role tensors,64×5120 BF16; original viewer inputs are float32 all-layer means cast to float64, coordinate-centered across roles, without coordinate scaling or per-role normalization, followed by ordinary SVD PCA. The new basis changes only the layer selection to row48: BF16→float32→float64, identical role ordering and coordinate-centering/preprocessing. Deterministic signs make the largest absolute loading positive, then PC1-48..PC3-48 are oriented positively to same-index viewer scores, matching the original Qwen sign convention. PC4-48/PC5-48 retain deterministic loading signs. No Procrustes rotation or matching optimization is applied.

Model/representation compatibility is supported at the nominal Qwen3-32B, block48,5120-coordinate level used by the frozen direct comparisons. Extraction revision is `9216db5781bf21249d130ec9da846c4624c16137`. The released role tensors' exact original model revision, response masks and detailed upstream pooling provenance were not released; this inherited provenance limit remains. We do not claim independently proven exact checkpoint identity. Role-file hashes match the existing pinned manifest for upstream revision `3b3b788432ad33e3a28d9ff08e88a530c0740814`. No new activation extraction is used to fill that gap.

Explained variance for PC1-48..PC5-48 is38.2918%,11.8832%,8.3557%,5.0178%,3.4845% (first3=58.5306%, first5=67.0329%). This is variance across centered role activation coordinates. The [signed5×5 table](results/pc48_viewer_correlations.csv) compares persona scores, not loading-vector cosines. Canonical correlations between the centered PC1..3 score spaces, computed by QR/SVD, are **.996751,.985301,.971731**; these summarize shared three-dimensional variation across the same275 roles, not equality of axes or causal effects. [Persona score exports](results/pc48_persona_scores.csv), [variance ratios](results/pc48_explained_variance.csv) and [canonical correlations](results/pc48_viewer_canonical_correlations.json) support reproduction.

## Historical trait axis guide

Pearson r across the 275 aligned personas between each new PC score and each of the existing240 historical trait cosine-score columns; report the three most negative/positive coefficients. This follows the notebook's pinned `phg/landscape.py` axis guide at `b03d1d7`, read without modifying its branch. Rank by signed Pearson r; no facet proxies are chosen. All720 coefficients are in [trait associations](results/pc48_trait_associations.csv), with the 18 selected labels in [trait poles](results/pc48_trait_poles.csv).

| Axis | Negative end: historical traits (r) | Positive end: historical traits (r) |
|---|---|---|
| PC1-48 | narrative (-0.988), flirty (-0.977), spontaneous (-0.977) | factual (+0.980), methodical (+0.956), transparent (+0.955) |
| PC2-48 | abstract (-0.946), conceptual (-0.937), introverted (-0.910) | practical (+0.918), experiential (+0.915), contemporary (+0.778) |
| PC3-48 | benevolent (-0.914), nurturing (-0.910), optimistic (-0.838) | callous (+0.888), pessimistic (+0.866), cynical (+0.858) |

These historical scores were produced by the existing historical all-layer readouts. Their associations with block48 PC scores are descriptive **across-persona, cross-representation correlations**. They are not newly extracted block48 traits, direct Johnson IPIP measurements or validated human meanings for the axes. This guide describes associations shared with the historical score library, not a mechanism.

## Question and running-mean projections

For a saved question contrast δq, report `cos_pcj = δq·vj / ||δq||`, where vj is unit PCj-48 in5120 coordinates. `norm` is the original block48 contrast norm. For each scheduled mean and accepted final, first average raw contrasts in float32 with the frozen equal weights, then normalize that mean and project. Averaging unit question vectors would change the estimator and is not done. Do not subtract the role centroid from a contrast: `(high−μ)−(low−μ)=high−low`.

[Question directions](results/question_directions_pc123.csv) contain2,119 accepted pairs across all 60 formats, ordered by original accepted position, not lexicographically by question ID. `checkpoint_membership` lists only actually evaluated checkpoint prefixes. `formal_endpoint_weight` is1/n for formal members and0 for extras or unaccepted partials. No response text, questions, respondents or individual human predictions are exported. [Running means](results/running_mean_pc123.csv) contain252 scheduled estimates,55 accepted format finals (including3 inside excluded facets) and5 explicitly unaccepted partial diagnostics. The table's `cos_pc1..3` always mean **PC1-48..PC3-48**, as its `basis` field states.

The projections are not normalized again within the displayed three coordinates. Their squared sum is the fraction of the full direction's squared length represented here. Across52 qualified finals this ranges1.1418%–32.2542%, median13.8678%. Thus visually smooth PC traces cannot establish full-space stability, and visibly noisy individual questions can coexist with a stable mean. The three-axis picture illustrates the recorded estimator; the frozen full-space gate determines convergence.

## Figures and captions

1. [Stopping counts](figures/stopping_counts.png) ([SVG](figures/stopping_counts.svg)): first passing accepted-question counts by facet/format at block48. Asterisks identify excluded facets, including format-level passes; blank/no-stop cells preserve bank exhaustion. Colour encodes question count, not confidence or human fit.
2. [Basis correspondence](figures/basis_correspondence.png) ([SVG](figures/basis_correspondence.svg)): left, signed Pearson correlation across 275 persona scores for new block48 and saved all-layer axes; right, activation variance explained by new PCs. These are different representation constructions; axis labels remain distinct.
3. [N1 in PC space](figures/question_space_N1.png) ([SVG](figures/question_space_N1.svg)): individual unit high-minus-low question contrasts on the three block48 cosine axes; colour gives accepted-question order including extras. Red path joins scheduled normalized raw means; star marks the frozen accepted final. Extras do not enter this path. This is a deterministic illustration using a frozen B reference facet, not an outcome-selected representative claim.
4. [N1 component traces](figures/question_paths_N1.png) ([SVG](figures/question_paths_N1.svg)): the same cosine components against accepted-question order. Faint dots are individual unit contrasts; joined circles are scheduled normalized raw means; stars are accepted finals; grey regions contain zero-weight accepted extras. Each panel labels its axis and format. Neither picture plots direct human IPIP measurements.
5. Complete traces for [N](figures/question_paths_N_all.png), [E](figures/question_paths_E_all.png), [O](figures/question_paths_O_all.png), [A](figures/question_paths_A_all.png), [C](figures/question_paths_C_all.png), each also supplied as SVG. Every facet/format is shown; excluded panels are labeled. Crosses denote unaccepted partial terminal means, while stars within excluded facets mean only format-level passes. PC1-48/PC2-48/PC3-48 colours are consistent. Within-panel limits aid readability; compare numerical cosines, not apparent slopes across panels.

## Verification and interpretation limits

[Collection verification](results/COLLECTION_VERIFICATION.json) checks all saved decisions and first stops, plus all 33 block48 rows in the frozen B `FROZEN_STOP_VERIFICATION.json` for N1/C1/N4/A4 (absolute tolerance2e−6). [Independent stopping recomputation](verification/INDEPENDENT_VERIFICATION.json) uses explicit resampled rows, float64 coordinate sums and einsum cosines, importing no primary numerical code:75 checkpoints across 20 formats, maximum p05 error1.772e−7 and successive-cosine error1.497e−7. The seed is reset at each checkpoint exactly as frozen. No missing summary statistic needed reconstruction.

[Independent geometry](verification/INDEPENDENT_GEOMETRY.json) decodes every BF16 role using independent scalar binary conversion and reconstructs the basis through a275×275 centered Gram eigendecomposition. Maximum loading error6.50e−15, persona-score error8.39e−13; all 25 viewer and720 trait correlations and three canonical correlations agree below 1e−8. Scalar recomputation of 171 question projections agrees below 1e−8;60 terminal raw-mean projections (independent float64 means versus frozen float32) agree within 2e−6, observed maximum5.15e−9. Orthonormality is below 1e−10. Frozen saved unit48 arrays also match all 52 available qualified endpoints within 2e−6. [Geometry receipt](results/GEOMETRY_VERIFICATION.json) binds source hashes and preprocessing.

[Deterministic reproduction](verification/DETERMINISTIC_VERIFICATION.json) reruns collection, PCA, projections, both independent checks and figures in a fresh cache; scientific tables/figures and stable provenance JSON match byte-for-byte. Timing and path-dependent verification metadata are excluded from the byte test. [Closeout](verification/CLOSEOUT.json) records syntax, scoped links, input-preservation hashes, exports and actual figure review. No broad unchanged migration/viewer or human-data pipeline is claimed as rerun.

These are adaptive first-pass stops. The bootstrap describes directional stability conditional on accepted questions, selection rules and the current checkpoint, not an unconditional confidence statement accounting for repeated stopping, rejected questions or unobserved responses. No new validity criterion is inferred from smoothness or p05; no changes to frozen rules, endpoints or questionnaire comparisons were made. Historical model geometry, human observational associations and demonstrated causal effects remain separate. No behavioral, safety, wellbeing or human-plausibility conclusion follows. AA26 corrections/withdrawals and AA27's failed primary bridge remain authoritative; activation PCs, AA18 C, trait PCA T and AA17 F remain distinct.

# Trait Correlation Outlier Diagnostics

## Main answer

**The strongest disagreements are reproducible, but neither extraction imprecision nor a few unusual personas explains them generally.** The frozen screen identifies13 consistent reversals and6 close-agreement pairs among325 relationships in the latest verified26-facet Direct-30 comparison. All13 reversal signs remain resolved under separate simultaneous human/model resampling bands. Style conditioning changes many of these relationships, while removing much of the measured trait variance. Some historical proxies reproduce the discrepancies; others disagree or vary across models. The evidence supports a mixed measurement/representation explanation, without identifying causes.

[Decision brief](DECISION_BRIEF.md) · [Figures](FIGURES.md) · [Frozen methods](analysis_specification.md) · [Reproduction](REPRODUCE.md)

## Authoritative input and preserved scope

Base is the latest completed Direct-30 B records **bf99d3d**, not the earlier22-facet comparison. Its final receipt reports11,627 independent arithmetic checks plus66 frozen stopping checks. Both formats have26 fully converged facets: E1,O5,C5,O2,N2,E5,A3,O1,O6,N6,A1,C2,E6,C4,O4,C6,A5,O3,A2,E2,E4,A6,N1,C1,N4,A4. N3,C3,E3,N5 remain excluded under their original gates. This is not a completed30-facet bank and does not alter the earlier22/15/9 studies or their prediction/calibration findings.

The new branch is `codex/trait-correlation-outlier-diagnostics-20261019`. Live main65da790 was inspected and predates the latest branch evidence. Prior persona-bank dependence bc82e07, historical-library diagnostic40f1654 and cross-model study e01cacb were read from immutable Git revisions. The plan, sources, metadata and baseline reproduction were committed/pushed as **0a8498b before screening and adjusted calculations**. Full revisions/SHA256 files are in [source_manifest.json](source_manifest.json).

Primary inputs are the existing275-persona, rank-normal **block48** scenario and survey measurements. No score is refitted within a subset or weighting. Actual new extraction model/tokenizer was Qwen/Qwen3-32B revision9216db5781bf21249d130ec9da846c4624c16137; exact historical saved-bank checkpoint/tokenizer/response masks remain unresolved. Hash-verified saved-bank compatibility is conditional, not proven measurement equivalence. No new persona readout or prediction model was computed.

Human primary is the same30,000 reference respondents after the existing reference-fitted empirical marginal transform; the original10,000 evaluation respondents provide a point sensitivity. Source contains307,313 rows,117,260 complete adults aged18–80 and117,259 unique complete response patterns. Scoring uses all ten items/facet with the released responses **already keyed**, without double reversal. Original seed20260920,30,000/10,000/10,000 memberships and every transformed matrix hash reproduce. All650 published model correlations and duplicated human entries reproduce within **1.12e−15**. All52 formal endpoint seals, accepted-contrast means and unit48 directions verify; accepted extras remain excluded.

## 1. Complete rankings, screens and uncertainty

All325 pairs are ranked by mean absolute model-minus-human discrepancy, with continuous errors and format differences retained. A reversal requires |human r|≥.25, both model signs opposite and both |model r|≥.30. Close agreement requires |human r|≥.25 and both model deviations≤.15. Screening is not a significance/equivalence test, and the19 selected pairs are not19 independent replications.

### Consistent reversals:13 pairs,11 unique facets

| Relationship | Human | Scenario | Survey |
|---|---:|---:|---:|
| Excitement-Seeking – Self-Consciousness | -0.324 | +0.901 | +0.735 |
| Modesty – Self-Consciousness | +0.454 | -0.570 | -0.710 |
| Anger – Cheerfulness | -0.294 | +0.876 | +0.658 |
| Gregariousness – Self-Consciousness | -0.488 | +0.552 | +0.494 |
| Vulnerability – Modesty | +0.286 | -0.569 | -0.811 |
| Friendliness – Anger | -0.280 | +0.710 | +0.607 |
| Cheerfulness – Anxiety | -0.349 | +0.693 | +0.479 |
| Modesty – Self-Efficacy | -0.320 | +0.425 | +0.683 |
| Vulnerability – Cheerfulness | -0.282 | +0.744 | +0.435 |
| Gregariousness – Anxiety | -0.256 | +0.456 | +0.672 |
| Friendliness – Vulnerability | -0.301 | +0.605 | +0.384 |
| Friendliness – Anxiety | -0.336 | +0.468 | +0.422 |
| Friendliness – Self-Discipline | +0.282 | -0.511 | -0.352 |

### Close agreement:6 pairs,10 unique facets

| Relationship | Human | Scenario | Survey |
|---|---:|---:|---:|
| Altruism – Sympathy | +0.604 | +0.557 | +0.733 |
| Cheerfulness – Adventurousness | +0.319 | +0.410 | +0.238 |
| Morality – Sympathy | +0.404 | +0.258 | +0.405 |
| Achievement-Striving – Cautiousness | +0.324 | +0.266 | +0.239 |
| Trust – Sympathy | +0.354 | +0.319 | +0.389 |
| Friendliness – Gregariousness | +0.747 | +0.760 | +0.747 |

The largest discrepancy is **Excitement-Seeking–Self-Consciousness**, −.324 human versus+.901/+.735 model. Friendliness–Anger is −.280 versus+.710/+.607. Closest agreement is Friendliness–Gregariousness, +.747 versus+.760/+.747. Unscreened does not mean unimportant: Excitement-Seeking–Anxiety is −.219 versus+.827/+.850; the earlier Self-Discipline–Liberalism reversal also misses the human-magnitude cutoff. Both remain in the complete ranking.

Threshold sensitivity is material but transparent. Raising the human cutoff to.30 reduces reversals13→7; lowering it to.20 yields16. Changing model magnitude.30→.25/.35 leaves13. Agreement tolerance.10/.15/.20 gives4/6/12 pairs. Joint stricter and relaxed settings give7/16 reversals and4/16 agreements. No threshold was optimized or promoted after outcomes; [all variants](results/threshold_counts.csv).

Uncertainty uses2,000 whole-reference-human draws and2,000 paired whole-persona draws shared across formats. This preserves dependence between pairs sharing facets. The95th-percentile maximum absolute error across325 human cells is **.02209**, and across650 model cells **.20875**. All13 selected reversals retain their signs under these separate approximate simultaneous bands. Each sample family is nominal95%; jointly the two families offer only a nominal90% union-bound statement under ideal coverage, **not a single combined95% guarantee**. Historical benchmark reuse, fixed marginal transforms and extraction uncertainty are outside those bands.

For Friendliness–Anger the ordinary95% intervals are human[−.292,−.269], scenario[.652,.760] and survey[.527,.675]. For the top E5–N4 discrepancy: human[−.334,−.314], scenario[.878,.921], survey[.685,.778]. These are not near-zero ambiguities within the studied bank/reference sample.

Magnitude-screen membership itself is less certain: reversal frequencies range.8445–1.000 across resamples; agreement frequencies.537–1.000. Friendliness–Gregariousness is screened close in all2,000 draws, whereas Morality–Sympathy is close in53.7%. Such frequencies are descriptive resampling stability, not probabilities that a population claim is true. Separate fixed-group bootstrap summaries and delete-one-facet group summaries retain shared-facet dependence. Group-error separation is partly imposed by screening; no inferential test of that separation is presented.

## 2. Extraction reliability does not supply a general explanation

| Pair-level diagnostic, group median | Reversal | Close agreement |
|---|---:|---:|
| Minimum scenario–survey persona correlation | .9232 | .8962 |
| Minimum source-direction cosine | .7882 | .8008 |
| Minimum accepted contrast count | 24 | 24 |
| Mean formal acceptance fraction | .8302 | .8934 |
| Minimum original convergence bootstrap p05 | .95299 | .95488 |
| Minimum new whole-question direction p05 | .95488 | .95493 |
| Maximum relative-direction-norm95% interval width | .1631 | .1763 |

Distributions overlap. Reversal pairs have somewhat lower acceptance, but not generally weaker source-readout agreement or directional precision. The groups share facets, so these medians are neither independent observations nor a test establishing equal reliability. C2 Orderliness has especially low scenario–survey persona agreement(.456), while C4 Achievement-Striving is.712; such unusual measurement behavior occurs beyond the reversal set too. E1 accepts24/48 scenario and24/35 survey observations yet has source-readout agreement.957, illustrating why acceptance and agreement are different diagnostics.

All52,000 new whole-observed-question direction draws are retained, with zero undefined draws. They include rejected observations as zero contributors, normalize by accepted multiplicity and exclude beyond-endpoint accepted extras. These diagnostic direction resamples condition on the observed adaptive endpoint and fixed scorer/masks; they do not reclassify historical convergence. Stable directions do not prove construct validity.

**Boundary:** this task makes no new persona projections. Therefore it does not provide pair-specific correlation uncertainty from extraction resampling. Direction precision and saved prediction-extraction intervals cannot substitute for that missing uncertainty. Strong person-resampling signs are not advertised as robust to every extraction design choice.

## 3. Composition: reversals persist, some agreements deteriorate

All275 single-persona deletions were calculated for each pair/format. No deletion changes a selected reversal's sign; maximum selected-pair correlation change is **.01742**. Pair-specific top1/top5 removal sets are ranked by average absolute influence across both formats and applied identically to both; these are adversarial stress tests, not cleaning decisions. Original full-bank results remain primary.

All five transported alternative weightings preserve both opposing signs for all13 reversals. Kish effectiveN ranges128.6–271.5, compared with275 uniform. Fourteen of15 pre-existing group exclusions retain all13; removing the Qwen consensus A pool leaves12 with both opposing signs. The groups are legacy analytical semantic/geometry assignments, not original author categories or validated psychological types. The old global top5/top10 stress sets also retain all13 signs.

The **130-persona ordinary-role subset** was frozen from definitions: previously assigned task/occupational or life-role personas, excluding explicit infant/toddler/adolescent/teenager, exceptional prodigy and clandestine spy frames. It omits the nonhuman/imaginary and disposition-only pools without using a correlation. It is a conservative operational subset, not a representative or validated typical-human sample. Ambiguity in authored categories remains visible in [classification](persona_classification.csv).

All13 reversals remain oppositely signed in this subset. Mean absolute discrepancy over the26 reversal-format cells rises **.924→.995**. Friendliness–Anger strengthens **+.710/+.607→+.833/+.804**. Removing fantastical frames therefore does not explain it. Conversely, the six close-agreement pairs' mean discrepancy rises **.060→.277**: Trust–Sympathy becomes+.093/−.078 and Morality–Sympathy−.068/−.061. Friendliness–Gregariousness and Altruism–Sympathy remain closer. Close agreement in the original bank is not automatically composition-invariant.

## 4. Style: substantial dependence with substantial variance removal

Formal, Animated, Verbose, Technical and Methodical are the same fixed historical readouts and poles as before. They are measurements of prompted language/disposition, not validated latent nuisance factors. Conditioning removes linear relationships statistically; it is not a causal intervention.

| Condition | Reversal pairs retaining both opposing signs | Mean absolute discrepancy, reversal cells |
|---|---:|---:|
| Original | 13/13 | .924 |
| Formal | 5/13 | .390 |
| Animated | 4/13 | .320 |
| Verbose | 13/13 | .991 |
| Technical | 9/13 | .667 |
| Methodical | 6/13 | .428 |
| Joint five | 2/13 | .309 |

These are sign counts, not reapplications of magnitude thresholds or independent significance results. Formal-adjusted Friendliness–Anger is **−.245/−.274**; joint-five gives **−.229/−.011**. The largest E5–N4 discrepancy persists after joint-five conditioning: **+.585/+.275** versus marginal human−.324. Other changes depend on format, including uncertain small residuals.

Joint styles remove a median **75.3%** of measured trait variance, range29.2–96.0% across26facets×2formats. Formal alone removes a median48.4%. Residual variance, control–target associations, control rank/condition numbers and correlation intervals are exported. Removing this much information can erase target content as well as a broad style component. Human style counterparts are unavailable, so comparison to the **marginal** human matrix is not a matched partial-correlation test. No better human prediction or corrected measurement is inferred from smaller discrepancy.

## 5. Cross-model proxies and construct boundaries

Every pre-frozen AA27 direct/close indicator combination for the screened pairs is retained in all three historical libraries. Signs, tiers and same-indicator overlap flags are explicit; no broad/none mapping is upgraded and no favorable indicator is selected. Historical readouts use all-layer means and unknown original model/tokenizer/rollout lineage, whereas the new direct IPIP readouts are block48. Identical labels do not establish psychological or methodological equivalence. Intervals use the same2,000 paired persona draws across models; proxy combinations and models are not independent replications.

| Fixed historical relationship, oriented | Qwen | Llama | Gemma |
|---|---:|---:|---:|
| Negative Avoidant–Hostile | +.581 | −.706 | −.245 |
| Nurturing–Hostile | −.476 | −.900 | −.810 |
| Adventurous–Avoidant | −.744 | +.244 | +.118 |
| Humble–Avoidant | +.278 | −.112 | +.414 |

The first two reproduce the prior social-approach versus care distinction. Qwen's negative-Avoidant/Hostile interval is[.488,.661], versus Llama[−.753,−.656] and Gemma[−.359,−.123]. Joint styles bring these toward small positive residuals whose intervals include zero. Nurturing–Hostile remains negative in all models under the same styles. No universal social-approach/hostility sign follows: other approach indicators and many other proxy combinations differ.

The strongest new E5–N4 reversal is **not** reproduced by historical Qwen Adventurous–Avoidant, which is strongly negative. All four mapped Qwen E5–N4 combinations are negative; Llama/Gemma are positive. But N4 has only one historical **close** indicator, Avoidant, whose definition is broad withdrawal, not the full self-consciousness scale. This observation cannot tell whether new extraction design, representation layer, old proxy inadequacy or model representations caused the discrepancy. It does show that “the model has one invariant trait relationship” is too simple.

### Grounded construct interpretation, not a new mapping

- **E1 social approach versus A3/A6 care.** E1 asks making friends, warming up, interpersonal comfort and distance, plus cheering others up. A3/A6 cover helping and sympathetic concern. A3–A6 agrees relatively well while E1–Anger reverses. The historical care versus approach split supports keeping those concepts distinct; it does not validate either proxy as the human facet.
- **N4 Self-Consciousness versus withdrawal.** Its items cover intimidation, fear of doing the wrong thing, approaching others, embarrassment, unfamiliar social situations and standing up for oneself. Avoidant's broad withdrawal definition covers only part of that content. Its cross-model result is a related-proxy sensitivity, not a direct replication.
- **E5 excitement versus expressive language.** The scale includes loud crowds/music, recklessness, danger and adventure. A response that is energetic or emotionally expressive can align with several direct directions; the strong Animated associations are compatible with that explanation, but do not demonstrate it.
- **A5 Modesty versus epistemic humility.** The human scale includes self-promotion, superiority, center-of-attention preferences and knowing answers. Historical Humble stresses acknowledging limitations/uncertainty. It is a frozen direct mapping under AA27's labels, but the wording emphasizes different behavior. We retain that classification while identifying its coverage limitation.

These are interpretations grounded in the pinned exact ten-item keys and canonical definitions, not evidence that any selected persona expresses real human feelings or behavior. [Item inventory](facet_item_inventory.csv); [all historical definitions/mapping rationales](historical_indicator_inventory.csv). No new psychological scale or outcome-tuned semantic bridge is created.

## Synthesis, limitations and verification

A general random-direction-noise explanation loses support: several high-agreement, converged measurements still reverse. A handful-of-personas or fantasy-only explanation also loses support under these fixed tests. Broad style/procedural-versus-expressive covariance gains **descriptive** support for part of the discrepancy, with heavy content removal and residual exceptions. Construct/measurement differences remain plausible, especially for N4 and Modesty, but are entangled with layer, extraction procedure, checkpoint provenance and authored-bank composition. The data do not identify their separate causal contributions.

AA27's failed historical gate, all earlier prediction/calibration/null findings and every original extraction result are unchanged. No behavioral predictor, model inference, rescoring, steering, new activation extraction or paid compute occurred. No automatic adoption of conditioned scores or preferred proxy follows.

[Independent verification](verification_report.json) passes **3446 checks**, maximum checked discrepancy **2.40e−11** (below the relevant frozen residual tolerance; basic correlations satisfy1e−12). Checks include source/52endpoint hashes, exact human split/transforms and original correlations, all325 ordinary scalar values, all30 condition matrices via independent SVD/weighted-rank arithmetic, selected explicit bootstrap draws, all275 scalar deletions for selected pairs, family-band maxima, every interval, source masks/seeds/literal question resamples, historical cross-model points and published baselines, zero/constant/tied fixtures. Arithmetic is independently written in this task, not a separate recruited rater/agent.

The [deterministic rerun](deterministic_verification.json) reproduces **22 principal files byte-for-byte** in a separate directory. During development, global ranks in subset Spearman diagnostics were corrected to weighted midranks; primary Pearson/group membership was unchanged. Published cross-model baseline arithmetic was checked during verification rather than before the first exploratory calculation; no mapping, threshold or model choice changed. These procedural details do not rewrite frozen source outputs.

Main numerical computation: **9.94 seconds wall / 9.29 seconds process CPU**, peak RSS **1,005,584,384 bytes (~0.94GiB)**. All six figures were visually reviewed, with obstructing legends/colorbars repaired. Runtime/environment/log hashes are in [resource_log.json](resource_log.json); scoped syntax/privacy/preservation/link checks and actual package size are in [publication_verification.json](publication_verification.json). New numerical runs emitted no RuntimeWarnings. Raw humans/IDs/transformed profiles/predictions and all full activation/weight files remain outside Git. Branch-only context/state/index updates; stop after verified push, with no merge or follow-on study.

# PHG-CM01 — Cross-model personality factor correspondence

## Answer

**Partly shared organization, substantial indicator-dependent differences, and an unresolved direct-IPIP comparison.** Qwen's positive social-approach/hostility relationship is not universal across historical indicators or models. Flirtatious expression and hostility co-vary positively in all three; nurturing and hostility co-vary negatively. Charisma/hostility separates Llama from Qwen and Gemma. Self-Consciousness lacks an adequate historical measurement, so a direct cross-model conclusion about Excitement-Seeking–Self-Consciousness is unavailable.

This is an exploratory study of activation-derived measurements, not generated behavior, human behavioral prediction, causal steering, a safety outcome, or evidence that anger improves assertion. [Decision brief](DECISION_BRIEF.md); [frozen protocol](PROTOCOL.md); [complete source manifest](source_manifest.json).

## Design and provenance

The protocol,60 facet-indicator rows/54 distinct traits, exact19-pair inventory and hashes were committed/pushed at **3e2b72d** before new cross-model calculations. Base: live main **cb6a91f681e6f41e36c10ce51a51151fdb7d6048**; Qwen branch-specific reference **fc764f842edc7bb04935875e2eb267e49ad45ffd**, October26. Older AA17/AA18 and previous historical cross-model findings were already known; this is not independent confirmation. The complete comparison covers all13 frozen strong reversals and6 close agreements, not a new screen. Main's older research snapshot does not supersede the branch-specific results.

**Historical measurements:** same275 exact persona identities and240 trait definitions per model, from Lu et al.'s *Assistant Axis* artifact family, processed by the saved project cosine pipeline. Average all stored decoder-layer rows for each role and trait, separately L2-normalize the means, take their cosine. Qwen64 rows, Llama80, Gemma46; actual identifiers Qwen/Qwen3-32B, meta-llama/Llama-3.3-70B-Instruct, google/gemma-2-27b-it. Native hidden coordinates are never mixed between models. Original exact checkpoint/tokenizer revisions, response-level masks, selected contrasts and weighting remain unresolved. Saved CSV hashes match AA17:

| Model | SHA256 |
|---|---|
| Qwen | 723d42415fe3a70221919fe8ae2aec2e2ebcdeae5bef89a1aeea55fdaccfe5d8 |
| Llama | 74b2cb886967159fe4580b2dc8066cfe3ba789bedde7f0f380ee95240a3ed947 |
| Gemma | 798c0618b9e468eec2e6d9083c96b2eef3d414f15f29d93180ff679614fea427 |

**Recent direct measurements:** only Qwen has26 qualified Johnson IPIP facet estimates; scenario and survey_style remain separate, rank-normalized block48 readouts. N3/C3/E3/N5 remain excluded. These are different representations from historical all-layer means. No layer-matched identity is asserted. Qwen historical/F and direct/F relationships reproduce the October26 report, not a newly refitted solution. No Llama/Gemma IPIP score is invented.

**Human context:** frozen transformed30,000-reference Johnson facet correlations; no respondent rows are read. The separate human item study51cdecc used117,259 complete deduplicated adults and found all ten keyed Anger items negatively associated with Friendliness. That finding remains distinct from these historical proxies. Already-keyed human data are never rescored here.

**Factor solutions:** original AA17 principal-axis/shrinkage/oblimin fits,5 Qwen and6 Llama/Gemma factors, same original signs and saved regression scores. No factor fitting, retention decision or rotation is repeated. AA18 provides prior evidence of shared persona-score spans but does not supply these independently fitted factor identities. The new Qwen trait-score T PCA, original activation PCs, AA18 C and AA17 F are distinct analyses; none is substituted for another.

## Indicator coverage and Qwen reference

[Selections](indicator_selection.csv) retain exact canonical definitions, aspect descriptions, original AA27 direct/close tiers and polarities. Complementary aspects were selected semantically before Llama/Gemma calculations. They are not independent measurements. All selected rows retain their Qwen direct-facet associations in [audit](results/qwen_indicator_audit.csv), including unfavorable ones; full26×240 Pearson/Spearman cells and26×5 factor correlations are exported.

| Selected construct | Qwen association with its historical indicator, scenario / survey |
|---|---|
| Friendliness with negative Avoidant | +.314 / +.131 |
| Friendliness with Charismatic | +.721 / +.578 |
| Friendliness with Nurturing | +.512 / +.653 |
| Anger with Hostile | +.854 / +.832 |
| Anger with Temperamental | +.949 / +.952 |
| Excitement-Seeking with Adventurous | +.949 / +.953 |
| Self-Consciousness with Avoidant | **−.770 / −.718** |
| Gregariousness with historical Gregarious | +.649 / +.710 |

Thus close conceptual language does not guarantee agreement. N4 is particularly underrepresented; C5 uses only close proxies. E3 assertion indicators are contextual historical measurements, not a qualified new direct IPIP facet. No sign is changed to repair an observed mismatch.

Reproduced direct relationships:

| Pair | Human reference | Qwen scenario | Qwen survey |
|---|---:|---:|---:|
| Friendliness–Anger | −.280477 | +.709784 | +.607053 |
| Excitement-Seeking–Self-Consciousness | −.324172 | +.901013 | +.734774 |
| Friendliness–Gregariousness | +.746985 | +.759970 | +.746995 |

## Historical cross-model relationships

For every frozen pair, evaluate all Cartesian combinations of its selected indicators, preserving raw and semantically oriented Pearson/Spearman values. Exclude only mechanically identical self-pairs from replication summaries, logging E1/N6 Avoidant–Avoidant and A3/A6 Benevolent–Benevolent. Result: **197 distinct within-family combinations ×3 models =591 rows** (combinations across families can still overlap). All54 selected traits'4,293 model-specific pair cells and4,080 full historical-trait/factor associations remain separately available.

### Approach, care and hostility

| Historical relationship | Qwen r [95%] | Llama r [95%] | Gemma r [95%] |
|---|---|---|---|
| −Avoidant × Hostile | +.502 [.404,.595] | −.752 [−.801,−.711] | −.311 [−.416,−.193] |
| Charismatic × Hostile | +.738 [.693,.780] | −.526 [−.616,−.406] | +.512 [.422,.593] |
| Flirty × Hostile | +.805 [.771,.837] | +.690 [.637,.743] | +.760 [.720,.799] |
| Nurturing × Hostile | −.522 [−.602,−.424] | −.944 [−.957,−.930] | −.862 [−.892,−.825] |

These are raw historical cosine-score Pearson correlations with the explicit sign adjustment on Avoidant. Earlier rank-transformed proxy analyses are different statistics, not overwritten baselines. The full pair table also retains canonical raw signs and Spearman.

The paired Qwen-minus-Llama Charismatic–Hostile difference is **+1.263**, conditional95% interval **[+1.152,+1.350]**. Qwen-minus-Gemma is **+.226 [.163,.297]**. The same authors' persona IDs are paired across models; these models are not independent random replicates.

All20 E1/N2 indicator combinations remain. Five (all Flirty with the five hostility/volatility/irritability/restraint indicators) are positive in all three; five (all Nurturing combinations) negative in all three; five Charismatic combinations are positive/negative/positive; five negative-Avoidant combinations positive/negative/negative. This coherent aspect split is more informative than calling a median proxy correlation “Friendliness–Anger.” Family medians (.662/−.701/.069) are available as indicator-choice summaries only, not facet estimates or independent evidence counts.

### Excitement and the failed N4 proxy

Adventurous × Avoidant is **−.746/+.106/+.121** (Qwen/Llama/Gemma); Risk-taking × Avoidant **−.792/+.277/+.171**; Hedonistic × Avoidant **−.461/+.792/+.595**. Llama Adventurous–Avoidant's interval includes zero. These historical comparisons differ across models, but the sole N4 indicator fails its presumed orientation within Qwen itself. They therefore do **not** establish reversed or shared IPIP E5/N4 relationships in Llama/Gemma. In particular, do not conflate historical high Avoidant with low Friendliness in one table and verified high Self-Consciousness in another.

### Human-agreeing controls and other screened pairs

Charismatic × Gregarious is positive in all three (**+.650/+.220/+.264**), Nurturing × Gregarious likewise (**+.430/+.236/+.210**). Yet only6/12 E1/E2 indicator combinations are positive in all three; the rest include negative introversion/avoidance contrasts and model-specific signs. All11 non-identical A3/A6 combinations are positive in every model. All nine E2/N1 historical combinations are positive in all three, unlike the negative human direct-facet reference; this is stronger evidence of shared historical organization but remains proxy limited. Other reversal and control families contain both signs, with complete results rather than selected favorable examples in [family summaries](results/indicator_sensitivity_summary.csv) and [all sign patterns](results/cross_model_sign_pattern_counts.csv).

## Factor correspondence and combinations

Matching uses all240 historical rows, maximum-absolute Tucker congruence and a rectangular Hungarian assignment, never factor numbers or labels. Signed congruence and every alternative remain. Primary selected matches:

| Qwen axis | Llama match / signed congruence | Gemma match / signed congruence |
|---|---|---|
| F1 | F1 / +.732 | F1 / +.790 |
| F2 | F3 / +.751 | F2 / +.771 |
| F3 | F2 / +.919 | F6 / −.930 |
| F4 | F4 / +.791 | F4 / +.791 |
| F5 | F5 / −.607 | F5 / −.734 |

The clear all-three pattern is grounded/secular versus spiritual/idealist organization (original provisional descriptions), with LlamaF2/GemmaF6 signed congruence−.915. A further cooperative pattern LlamaF1/GemmaF3 has+.896. QwenF1 also resembles GemmaF3 (+.772), almost as much as its assigned GemmaF1 (+.790): its top-match gap is just.018. These competing relationships prevent a unique one-to-one psychological interpretation.

The minimum whole-loading-subspace canonical correlations are **.818 Qwen/Llama, .777 Qwen/Gemma, .490 Llama/Gemma**, exactly reproducing AA17. Extra sixth axes and rotations matter; five matched axes do not capture all of either six-factor solution. Matched selected-trait patterns export the largest excluded sixth-axis association so this omission is visible.

**Full trait patterns show why similar overall geometry can yield different focal associations.** Empirical trait–saved-score Pearson values:

- Qwen Hostile correlates−.968 withF1, Charismatic−.807, Flirty−.895. Nurturing isF1-positive+.335, F2-positive+.674 and F5-negative−.801. Those traits do not all express the same interpersonal property.
- Llama Hostile isF1-negative−.934 andF6-negative−.717; Charismatic isF1-positive+.326 andF6-positive+.774. Flirty remainsF1-negative−.688/F6-negative−.607; Nurturing isF1-positive+.864/F6-positive+.792. F6 is individually unresolved, so these are complete-pattern descriptions, not a validated F6 mechanism.
- Gemma Hostile isF3-negative−.913, NurturingF3-positive+.855, CharismaticF3-negative−.488 and Flirty−.611. Charismatic/Flirty also have substantialF1/F6 associations. Gemma's care/cooperation dimension is not just the axis assigned to QwenF1.

Matched-axis empirical profile cosine is .976 for Flirty and .922 for Hostile between Qwen/Llama, but only .344 for Charismatic and .339 for Nurturing. These basis-dependent descriptive comparisons omit LlamaF6, whose associations with those traits are large; the unmatched-axis values remain in the table. They support different trait combinations, not a universal scalar factor-equivalence score.

These are ordinary correlations, distinct from oblique pattern coefficients (which can exceed1), implied structure loadings and latent Phi. All are separately exported. Factor scores themselves are correlated; e.g. the established QwenF1/F2 r=−.249 andF2/F5 r=−.493 remain unchanged. Multiple marginal associations cannot be summed as independent factor effects.

### Oblique accounting, not causal attribution

For sample-standardized trait scoresY and all saved standardized factor scoresZ, jointly regress Y on Z. J is projection onto the entire factor span, R=Y−J. Original correlation equals Cov(J_i,J_j)+Cov(R_i,R_j), since original trait variances are1 and J′R=0. Own projected/residual correlations have different denominators and do not add. With joint coefficientsB, projected covariance is B_i′Cov(Z)B_j; all ordered cross-factor terms are retained.

For Charismatic–Hostile, projected/residual additive terms are **+.739/−.001** Qwen, **−.519/−.007** Llama, **+.511/+.001** Gemma. Corresponding diagonal/cross-factor totals are **+.547/+.192**, **−.277/−.241**, **+.230/+.281**. Ignoring factor intercorrelations would misstate this accounting. High factor coverage is expected because factors were fitted from these same historical traits; it is descriptive compression, not independent explanation or behavioral validation.

## Robustness and uncertainty

**Persona uncertainty:**2,000 jointly paired persona resamples, seed2026967, fixed saved directions/factor solutions. Report95% percentile intervals for historical pair and selected-factor Pearson correlations, and paired between-model differences. All2,000 draws are finite; no draws discarded or replaced. Group-level draw summaries preserve shared-trait/persona dependence. No per-cell significance claim or multiplicity-unadjusted discovery claim is made. Intervals condition on this authored bank and upstream estimates; they are not human population confidence intervals and do not capture persona-selection bias, semantic uncertainty or extraction uncertainty.

**Indicator selection:** all combinations stay. Six families have no two-sided direct-only AA27 comparison: A5/N4, E1/C5, E1/N2, E2/N4, E5/N4, N2/E6. They are explicitly unavailable, not imputed. No selected trait pair reaches |r|≥.995 in any model, so the predeclared near-duplicate collapse changes no selected count. This strict-threshold result does not establish independence: many scores remain strongly correlated.

**Factor matching:** excluding all54 selected traits leaves the original matched assignments unchanged on186 remaining rows. The strong QwenF3/LlamaF2/GemmaF6 match persists (absolute.928/.933/.918). Matching instead on full240 empirical trait–factor-score fingerprints changes QwenF4's Gemma match fromF4 toF3. Under that representation the globally assigned QwenF4/GemmaF3 congruence is+.601; it is a different statistic from original pattern+.208, and assignment constraints matter. Retain both rather than choose a preferred correspondence. QwenF5/LlamaF5 also weakens to−.307 under empirical matching. Full-pattern, empirical and selected-exclusion results are all exported.

**Existing factor-estimation uncertainty:** original20 bootstraps and10 split halves are reused, not newly refitted. Qwen5/5 axes stable; LlamaF4/F5/F6 individually unresolved; GemmaF5 individually unresolved by the original rule. Original loading intervals and all cross-loadings remain. These small upstream stability studies do not provide uncertainty in original activation extraction, whose record-level contrasts are unavailable. No invented extraction bootstrap is reported.

**Broad context:** all240-trait relationship fingerprints (28,680 dependent cells) correlate **.703 Qwen/Llama, .868 Qwen/Gemma, .821 Llama/Gemma**; RMSE **.429/.291/.326**. Many shared relationships coexist with the focal disagreements. No cell-independence test is attached to those summaries, and they do not imply measurement invariance.

## Evidence limits and review decision

Supported: substantial shared historical organization; some clear model-specific historical relationships; preserved distinction between social charm and care; limited equivalence between proxy labels and direct IPIP readouts; non-unique factor correspondence. Plausible but unresolved explanations include shared prompts/personas, extraction/aggregation procedure, training/architecture differences and construct coverage. These explanations are observationally confounded here. Matching factor combinations does not establish matched psychological meaning, actual feature activation, model emotions, causal effects or behavior.

Direct Llama/Gemma IPIP extraction would materially improve construct identification, especially N4 and E1/N2. It would not itself establish psychometric equivalence. No PHG-CM02 is proposed or executed. This study ends for scientific review, with AA26 corrections, AA27's original failed gate, original human analyses and all historical negative results unchanged.

A historical proxy's failure to reproduce a relationship is not proof that the corresponding directly extracted IPIP relationship would be absent in Llama or Gemma. Those direct comparisons have not been measured here.

### Protocol completion during recovery

The recovered core results were retained unchanged. [Recovery audit](RECOVERY_REPORT.md) distinguishes completed prior work from the missing summaries added during recovery. [Projection uncertainty](completion/projection_intervals.csv) now reports 95% conditional intervals for projected/residual additive terms, their own correlations, and diagonal/cross-factor totals for all 591 screened rows. Each of the same 2,000 paired persona resamples centers traits and saved factor scores, recomputes the joint descriptive regression within the fixed original factor span, and uses the resample's original-trait SD denominator. No factor solution or direction is re-estimated; additive terms sum to the original correlation in each draw. All added draws are finite.

[Per-draw sign summaries](completion/paired_sign_bootstrap.csv) retain 6,000 group/draw rows and shared model/cell dependence. [Numerical discoveries](completion/qwen_historical_extremes.csv) identify the five most positive and negative historical associations for each direct Qwen facet/format, separately from frozen semantic selections. Neither output changes the indicator inventory or supplies new validated facets. [Independent completion checks](completion_verification.json) compare explicit sampled-row QR calculations with all combinations in five draws/model, six complete focal projection intervals and three selected trait/factor intervals; all discrepancies remain below `1e-10`.

## Verification, figures and reproduction

[Independent verification](verification_report.json) imports no primary analysis code: scalar math.fsum Pearson/score reconstruction; SciPy Spearman; full240-trait scalar Tucker matching; QR versus SVD projection; ordered covariance sums; three complete2,000-draw focal bootstrap intervals; five sampled joint draws; sign/row-order/rotation and invalid-input fixtures. Max errors remain below frozen1e−10, including the independent bootstrap intervals (<6e−13). All650 direct pair cells,260 direct/F cells,1,200 Qwen historical/F cells, original96 match cells and all saved factor scores reproduce. [Baseline record](results/baseline_reproduction.json).

Two complete numerical runs and repeated summary/figure generation must agree deterministically; receipts and actual resource use are in deterministic_verification.json and execution_status.json. Platform NumPy matrix-multiply warning emissions are retained in results/warnings.json and verifier_warnings.json. Finite assertions, independent scalar/QR calculations and no-zero-replacement rules pass; warning logs are not hidden or used to relax tolerances. A reporting-only interactive attempt lacked optional `tabulate`; no dependency was installed and no scientific computation depended on it.

Three publication PNG/SVG figures (all exact data in CSVs):

1. [Historical relationships](figures/01_historical_relationships.png): illustrative frozen semantic roles, including conflicting proxies and human-agreeing controls. Not an exhaustive forest plot; all197 combinations remain in tables.
2. [Trait/factor patterns](figures/02_trait_factor_patterns.png):20 focal historical traits and all original model-specific axes, numeric ordinary correlations; unresolved axes marked. Full54 selected and240 total traits remain in tables.
3. [Factor matching](figures/03_full_pattern_factor_matches.png): every original signed factor-pair congruence, primary assignment and changed empirical assignment; signs preserved.

See [REPRODUCE.md](REPRODUCE.md) for exact commands, environment and input recovery. Historical outputs/viewers are never written. Only this package plus additive branch-local context/state/validation documentation are changed. Dedicated branch, push and no merge.

**Cell-count correction:** the frozen protocol and preserved primary receipt say 102 factor-pair cells. The pinned AA17 source and all three matching tables actually contain 96 per representation (30+30+36). Every source cell is present; this corrects the description, without altering the frozen protocol, selections, numerical outputs or historical receipt. See [recovery correction](RECOVERY_REPORT.md#correction-to-the-frozen-cell-count-description) and the independently checked inventory in `final_verification.json`.

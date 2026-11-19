# Historical trait relationships across Qwen, Llama and Gemma

## Answer

**There is no single cross-model “social approach goes with hostility” result.** Negative Avoidant–Hostile is positive only in Qwen; Charismatic–Hostile is positive in Qwen/Gemma and negative in Llama; Flirty–Hostile is positive in all three. Nurturing and Benevolent remain negative with Hostile throughout the tested composition and style sensitivities. These are reproducible patterns of saved measurements, not established psychological equivalence or causal behavior.

[Decision brief](DECISION_BRIEF.md) · [Figures](FIGURES.md) · [Frozen specification](analysis_specification.md) · [Reproduction](REPRODUCE.md)

## Sources and comparability

Task branch `codex/cross-model-trait-relationships-20261015`, based on Qwen diagnostic `bc82e07afef7aa564c0a3962112d63d7282f5404`, preserving historical diagnostic `40f1654`, Direct-12 human comparison `33e3cbd9` and extraction `e06ff9a`. Live main `65da79049a5be4f78c4ba03cffe5cd7f6c5bb963` was checked and predates these results. The input/pair/weight/procedure freeze was pushed as **`fb673d7ce1daa4e05b02a6df43aef388c41dc061` before new Llama/Gemma correlations**. Qwen results and prior three-model reports were already known; this is exploratory replication on a previously studied bank.

All three saved historical tables have the same 275 unique persona IDs and 240 unique trait labels/definitions, finite values and nonconstant columns. Their exact hashes match the AA27 matrix-source alignment and AA17/18 audits. Preflight also rehashed **all 1,545 original trait/persona files**, matching both historical manifests and immutable first-party HF LFS hashes at dataset revision `3b3b788432ad33e3a28d9ff08e88a530c0740814`. No activation tensor was decoded, projected or rescored. Only source metadata were downloaded; no vector or model-weight downloads occurred. [Source manifest](source_manifest.json), [external-file verification](external_source_verification.json), [compatibility matrix](compatibility_matrix.csv).

| Model | Identified model family | Saved rows × coordinates | Downstream score construction |
|---|---|---:|---|
| Qwen | Qwen/Qwen3-32B | 64×5120 | Mean all unnormalized layer rows, normalize role/trait means separately, cosine |
| Llama | meta-llama/Llama-3.3-70B-Instruct | 80×8192 | Same operation within its own coordinate space |
| Gemma | google/gemma-2-27b-it | 46×4608 | Same operation within its own coordinate space |

The AA14/AA15 correction is preserved: the historical “layer48” inventory described an **all-layer** calculation. We do not mix Qwen block48 with invented matching-layer Llama/Gemma data. Upstream post-block, assistant-response-token positive-minus-negative trait extraction is supported by the retained paper/code audit, but **original model/tokenizer revisions, rollout IDs, selected contrasts, masks and exact weights remain unavailable**. A verified dataset revision is not a model revision. Identical labels do not prove measurement invariance.

Primary scores apply the inherited within-bank midrank-normal transformation to the existing cosine columns, once over all 275 personas. They remain fixed under deletion, weighting and bootstrap. Secondary analysis uses original cosines. Qwen's all-240 all-layer transformed scores reproduce the preceding diagnostic within 2.23e−16. Its 180 published historical correlations across block48/all-layer and original/Formal/five-style procedures reproduce within **1.49e−13**, below the frozen 1e−12 tolerance. Qwen block48 landmarks +.577/−.548 remain separate from all-layer values +.581/−.476. [Reproduction table](qwen_baseline_reproduction.csv).

## Primary relationships

All entries below are Pearson correlations of primary rank-normal readouts. Only Avoidant is reversed in the explicitly labeled negative-Avoidant comparisons. Unflipped Pearson and Spearman, adjusted versions and original-cosine sensitivity are all retained in [correlation_results.csv](results/correlation_results.csv); [primary table with intervals](primary_correlation_summary.csv).

| Original relationship | Qwen | Llama | Gemma |
|---|---:|---:|---:|
| Negative Avoidant–Hostile | +.5806 | −.7061 | −.2453 |
| Charismatic–Hostile | +.7384 | −.3074 | +.5391 |
| Flirty–Hostile | +.7738 | +.6738 | +.7253 |
| Nurturing–Hostile | −.4756 | −.9004 | −.8102 |
| Benevolent–Hostile | −.4761 | −.9559 | −.9393 |
| Formal–Hostile | −.6472 | −.5479 | −.3910 |
| Formal–negative Avoidant | −.3321 | +.5545 | +.6037 |
| Formal–Charismatic | −.7273 | +.2786 | −.4105 |
| Formal–Nurturing | −.1421 | +.4126 | +.0692 |

For clarity, **raw positive Avoidant–Hostile** has the opposite signs: −.5806/+.7061/+.2453. This is a polarity convention, not a data-dependent sign change. Negative Avoidant–Hostile Spearman is +.6414/−.7577/−.2993. Original-cosine Pearson is +.5022/−.7518/−.3113, retaining the same signs. All five approach/care relationship signs in the first five rows survive that scale sensitivity.

The 95% paired-persona bootstrap intervals for negative Avoidant–Hostile are Qwen [.492,.663], Llama [−.753,−.656], Gemma [−.367,−.123]. Llama minus Qwen is **−1.287 [−1.369,−1.206]**, Gemma minus Qwen **−.826 [−.940,−.713]**. Differences in correlations may exceed one; they are not correlations themselves. These are descriptive bank-conditional intervals, not population/model-family inferences or a confirmatory multiple-testing family.

![Original and conditional comparisons](figures/primary_correlations.png)

## The same controls have different covariance roles

Every model uses Formal alone and the same fixed five readouts: **Formal, Animated, Verbose, Technical, Methodical**. No control was selected separately for a model. Exact definitions and canonical poles are in the preceding pinned control specification. Partial Pearson is intercept-inclusive weighted linear residualization; partial Spearman first ranks targets and controls. Neither is a causal adjustment.

| Negative Avoidant–Hostile | Qwen | Llama | Gemma |
|---|---:|---:|---:|
| Original | +.581 | −.706 | −.245 |
| Condition Formal | +.509 [.432,.583] | −.578 [−.640,−.515] | −.013 [−.136,.116] |
| Condition five styles | +.071 [−.033,.176] | +.118 [−.018,.260] | +.112 [−.012,.239] |

Thus the strong original model differences become small and uncertain under joint conditioning. Formal alone accounts for a positive shared component in Qwen and a negative one in Llama/Gemma because its association with negative Avoidant changes sign. It is not a universal explanation with the same direction across all models.

For Charismatic–Hostile, the joint-style residuals are −.003/−.173/+.117; the Qwen/Gemma intervals include zero, while Llama remains negative descriptively. Flirty–Hostile becomes +.078/+.173/+.222, with intervals [−.034,.192]/[.066,.273]/[.071,.366]. Nurturing–Hostile remains **−.699/−.879/−.850**, and Benevolent–Hostile **−.718/−.926/−.943**. Care and flirtation/social approach are not interchangeable historical indicators.

Joint conditioning removes **82.7%/70.7%/71.4% of Hostile variance**, and 56.8%/88.6%/57.7% of Avoidant variance. It removes 89–94% of Charismatic and Flirty variance. Such residuals may lose trait content along with style; they are not validated corrected personality scores. Formal alone removes 41.9%/30.0%/15.3% of Hostile variance, quite different from the much larger removal reported for the separate Direct-12 Anger readouts. Do not transfer the Direct-12 variance percentages to these historical indicators.

The five-control covariance is full rank in every one of 2,000 uniform bootstrap draws in each model. Point condition numbers are 93.3/29.5/47.4; maximum bootstrap values 139.4/49.5/79.5. Independent SVD residualization agrees with the covariance calculation. Correlations involving Formal conditioned on itself, and Technical in the full control set, remain undefined rather than zero. [Variance/stability tables](results/conditioning_diagnostics.csv), [bootstrap stability](results/bootstrap_numerical_stability.csv).

![Variance removed](figures/variance_removed.png)

## Persona-bank composition and influence

The three models share persona definitions, not independent samples. We transported the preceding study's **exact primary block48 Qwen weight values, strata and persona-ID masks**, unchanged across all models' all-layer readouts. These Qwen-derived style strata are not claimed to balance Llama/Gemma style. Group labels distinguish newly assigned definition-only categories, legacy semantic-seed/geometry families and Qwen geometry consensus groups. None is an original author category, diagnosis or observed demographic variable.

All 15 eligible group exclusions preserve every approach/care sign in the first five rows of the primary table. For negative Avoidant–Hostile, exclusion ranges are Qwen **+.263 to+.683**, Llama **−.744 to−.665**, Gemma **−.334 to−.080**. Under the five alternative weightings, ranges are **+.452 to+.660 / −.749 to−.703 / −.300 to−.144**. No weight was optimized to improve human agreement.

Kish effective N is 275 uniform; 186.0 equal definition groups; 128.6 equal eligible legacy families; 232.3 equal Qwen consensus groups; 271.5 fixed Formal×Verbose strata; 238.4 tempered Qwen style density. All retain the 275 personas with positive weights. Six-person Other exclusion and the nine-person Formal×Animated stratum remain ineligible; thresholds were not weakened. Protected residual groups keep their original target masses.

No single persona changes the focal signs. Negative Avoidant–Hostile deletion ranges are **[.5718,.5989] / [−.7144,−.7011] / [−.2689,−.2357]**. Largest absolute changes are .0183/.0083/.0236. Authored labels with greatest influence differ—Toddler, Caregiver and Moderator respectively—but these are prompts, not inferred ages or diagnoses. Every exact deletion is retained for every selected pair and both score spaces.

The prior Direct-12 globally influential top10 set is transported as a labeled stress test, not reselected per model. Removing it yields negative Avoidant–Hostile **+.659/−.680/−.201** and Nurturing–Hostile **−.459/−.891/−.798**. Category demeaning changes the estimand more substantially: Gemma's legacy-family-demeaned negative Avoidant–Hostile is +.024, whereas ordinary exclusions/weights retain its negative sign. It is therefore essential to distinguish changing bank composition from removing between-category covariance. [All composition ranges](composition_sensitivity_summary.csv), [LOO summaries](results/leave_one_out_summary.csv), [every deletion](results/leave_one_out.csv).

![Group exclusions](figures/group_exclusion_sensitivity.png)

## Broader historical trait structure

All 240 common labels and all **28,680** unordered pairs are retained, including weak, contrary and background relationships. Original fingerprint Pearson/Spearman and correlation RMSE are:

| Model pair | Fingerprint Pearson [95% bank interval] | Fingerprint Spearman | RMSE | Same signs |
|---|---:|---:|---:|---:|
| Qwen–Llama | .733 [.709,.754] | .737 | .399 | 22,352/28,680 |
| Qwen–Gemma | .868 [.856,.878] | .872 | .286 | 24,354/28,680 |
| Llama–Gemma | .840 [.822,.852] | .842 | .305 | 23,748/28,680 |

Across all three, **11,982 pairs are positive, 8,905 negative and 7,793 mixed** on the primary scale. These are descriptive cell counts, not 28,680 independent replications. The 200 whole-persona bootstrap draws preserve their dependence and shared identities; no binomial cell-count or naive cell-wise significance test is used.

Under five-style conditioning, fingerprint Pearson is .838/.880/.868 and RMSE .229/.201/.197. The comparison uses the same 235 non-control traits in every model: 27,495 pairs. The five conditioned traits create 1,185 explicitly undefined rows in the complete table; Formal alone creates 239. No undefined value is set to zero. Shared AA27 mapped-facet pairs, no-shared-mapping background and three frozen different-content controls are labeled separately. Background is not guaranteed semantically unrelated or statistically independent. No principal component or cluster was assigned a psychological interpretation.

Agreement between a *named trait's persona readouts* is distinct from agreement between whole relationship matrices. Hostile readouts agree strongly across models (rank-normal Pearson .886/.956/.916), as do Flirty (.945/.947/.955). Avoidant readouts are much less consistent: Qwen–Llama **−.164**, Qwen–Gemma **+.312**, Llama–Gemma **+.690**. This helps locate measurement disagreement without identifying its cause or selecting a replacement proxy. The earlier AA18 raw-score corresponding-trait summaries reproduce exactly. [All readout agreement](results/trait_readout_agreement.csv), [full library results](results/library_relationships.csv), [matrix agreement](results/library_agreement.csv).

![Library agreement](figures/library_agreement.png)

The secondary C5/O6 audit preserves all **64** original mapped proxy combinations, not one preferred pair. Their original positive counts are 29/64 Qwen, 35/64 Llama and 27/64 Gemma, with wide positive and negative ranges. No common sign is a valid summary of these heterogeneous indicators. All four C5 indicators are close or broad mappings; these are not independently extracted direct Self-Discipline measurements. Tiers, individual poles and every adjusted/unflipped result remain visible. [Proxy inventory](pair_specification.csv).

## What this does and does not explain

The fixed human Friendliness–Anger reference is **−.280477**. Similar signs in some historical model indicators do not establish equivalence with the official E1/N2 scales. The original Qwen Direct-12 scenario/survey findings remain separate; no corresponding Llama/Gemma direct extractions exist in this study.

Shared elicitation language, upstream contrast procedures and persona-bank construction can contribute to shared Flirty/care patterns and broad matrix agreement. Shared training conventions or representations could also contribute. Model-specific extraction/readout properties or representations could explain Avoidant/Charismatic differences. **These possibilities remain observationally entangled.** Robustness to the tested subgroups does not establish robustness to an independently authored bank. Statistical conditioning cannot identify causal style effects, prove psychological construct validity or demonstrate behavior control.


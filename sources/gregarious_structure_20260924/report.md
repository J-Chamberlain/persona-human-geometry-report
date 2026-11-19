# Gregariousness: restricted model–human structural comparison

## Finding

The existing gregarious indicator does **not show strong or specific human structural correspondence under this frozen bridge**. The result is weak across all three models, and none exceeds either semantic-label permutation benchmark. This does not support treating a single gregarious indicator as sufficient to repair the bridge. AA27 remains failed/untestable under its original coverage rule.

This is a newly executed, exploratory CPU analysis of existing cosine tables and human IPIP data. It is separate from AA27 and from the original sample-availability audit. No model inference, extraction, behavioral evaluation, or persona plausibility classification was performed.

## Main result

A fingerprint contains 20 correlations: gregariousness with each of the 20 already covered facets. We compared the model fingerprint across 275 persona means with the human fingerprint across 23,453 previously held-out respondents. A high positive fingerprint correlation would mean that the same facets tend to accompany gregariousness in both sources. It would not imply paired individual prediction or shared scales.

| Model | Fingerprint Pearson r | Conditional bootstrap 95% interval | Spearman r | Matching correlation signs | Label permutation p | Within-domain permutation p |
|---|---:|---:|---:|---:|---:|---:|
| Qwen | 0.114 | [0.089, 0.143] | 0.134 | 10/20 | 0.322 | 0.131 |
| Llama | 0.254 | [0.161, 0.349] | 0.251 | 12/20 | 0.144 | 0.261 |
| Gemma | 0.028 | [-0.006, 0.065] | -0.044 | 12/20 | 0.461 | 0.469 |

The descriptive Fisher-z aggregate is r=0.133, with conditional bootstrap interval [0.091, 0.180]. Its common-permutation p-values are 0.282 unrestricted and 0.270 within domain. Model-specific Holm-adjusted p-values are saved in the primary table; none is below .05. The three models are not treated as independent samples.

The positive conditional intervals for Qwen and Llama do not contradict the permutation results. Resampling respondents/persona labels asks how stable the calculated weak pattern is with the fixed mappings. Shuffling facet labels asks whether the correct semantic pairing is unusually good among alternate label assignments. Neither analysis estimates missing extraction-sample uncertainty.

![Correlation fingerprints](results/correlation_fingerprints.png)

## Where the patterns disagree

The human Gregariousness–Assertiveness correlation is +.504, while the corresponding model correlations are −.355 (Qwen), −.310 (Llama), and −.602 (Gemma). Human Gregariousness correlates negatively with Anxiety (−.262); all three model readouts correlate positively with the mapped Anxiety composite (+.704, +.101, +.443). These are concrete structural disagreements under the fixed mapping, not just imprecisely estimated near-matches.

The models do share a positive link with mapped Cheerfulness, but it is much stronger in their persona geometry (+.971, +.719, +.894) than in the human data (+.537). All 20 paired entries and magnitude discrepancies are retained, including those that agree.

The models also agree fairly well with each other on which persona means score highly on gregariousness: pairwise correlations .655–.825. Thus cross-model consistency alone does not establish human correspondence.

## Specificity within Extraversion

Using the same 18 non-Extraversion anchors for every target avoids self-correlations and compares Gregariousness with the other five Extraversion facets on equal footing.

| Human comparison facet | Qwen | Llama | Gemma |
|---|---:|---:|---:|
| E1 Friendliness | -0.133 | 0.226 | -0.129 |
| E2 Gregariousness | 0.057 | 0.251 | -0.017 |
| E3 Assertiveness | -0.274 | -0.288 | -0.432 |
| E4 Activity Level | -0.549 | -0.393 | -0.602 |
| E5 Excitement-Seeking | 0.449 | 0.108 | 0.153 |
| E6 Cheerfulness | -0.026 | 0.229 | -0.092 |

Qwen and Gemma match human Excitement-Seeking more closely than human Gregariousness on these anchors. Llama has its highest point estimate for Gregariousness, but its advantages over Friendliness and Cheerfulness are small and their paired bootstrap intervals include zero. These alternatives were fixed before calculation. They are diagnostics, not a reason to relabel the vector or promote a different mapping. The full pairwise difference intervals are in specificity.csv.

## Stability and controls

| Model | Rank-transformed indicators r | Raw-cosine composite r | Leave-one-anchor-out range | Leave-one-domain-out range | Human partition range |
|---|---:|---:|---:|---:|---:|
| Qwen | 0.140 | 0.131 | -0.036 to 0.211 | 0.044 to 0.348 | 0.116 to 0.147 |
| Llama | 0.235 | 0.246 | 0.094 to 0.402 | 0.222 to 0.286 | 0.256 to 0.276 |
| Gemma | 0.024 | 0.034 | -0.158 to 0.172 | -0.017 to 0.118 | 0.028 to 0.054 |

Normalization changes and alternate human partitions do not turn the weak result into strong correspondence. Removing a single anchor can materially change the profile correlation, particularly for Llama and Gemma. Within-domain centering gives .302, .152, and .016 respectively; the frozen within-domain permutation benchmarks still do not support unusually good semantic matching. Leave-one-indicator-out results are retained without choosing a favorable deletion.

The descriptive extroverted, negative introverted, and verbose controls do not identify a consistent replacement across models. For example, Llama extroverted performs better on the primary fingerprint (.453), while Gemma verbose performs better than Gemma gregarious (.306 versus .028). These post-comparison observations do not validate either control as an IPIP indicator.

## Method, provenance, and interpretation limits

The pre-computation specification and its timestamp/hash are analysis_freeze.md and freeze_manifest.json. The source commit is b93015a64ee69801f4fc19e6378f2ad737298efd in J-Chamberlain/persona-human-geometry. All three 275×240 cosine tables exactly match the AA27 source hashes. The direct-only, alias-deduplicated mappings and signs are unchanged. Model composites average signed, within-model standardized indicators. Gregariousness is not reused in an anchor. Other cross-anchor indicator reuse is disclosed in cross_anchor_reuse.csv. No axes, rotations, weights, or signs were fitted to human agreement.

The Johnson IPIP300.dat hash is verified before use. Its values are already keyed. Complete adults aged 18–80 reproduce n=117,260; removing one duplicate complete response pattern gives 117,259. The seed-20260924 split reproduces 70,355 training, 23,451 validation, and 23,453 test rows. Human facets average all ten keyed items. An independent streaming parser reproduced all human facet scores and the test split exactly.

The test partition was used in the earlier human-only information-value analysis that motivated this follow-up. This is not a pristine confirmatory holdout or a new human cohort. The frozen semantic mapping and present comparisons were not selected using these model–human results, but earlier human results and historical model geometry were already known.

There are 1,000 bootstrap replicates, jointly resampling persona labels across models and independently resampling human test rows, and 10,000 shared permutations for each null family. Within-domain permutations preserve broad Big Five membership. Facet exchangeability is a diagnostic null assumption; facets and mappings are not random interchangeable measurements. Human respondents are an observational volunteer sample, and personas are a curated archetype collection, not matched human individuals or random draws from the same population. Their different sampling and selection can change correlation structures.

The sample-availability audit at archive commit c074c7c528c58342dd748b308ca009d333600bc2 found no original persona response distributions or trait polarity samples in the audited sources. The conditional intervals here therefore exclude uncertainty in the extracted vectors. Existing cosine tables use layer-averaged vectors; no local single-layer clouds were substituted.

Failure of this restricted comparison cannot isolate whether the gregarious vector, one or more anchor mappings, persona sampling, or the assumed correspondence between the two populations is responsible. The semantic audit supports overlap in intended meaning but also identifies warmth/rapport content and unresolved extraction lineage. This study tests the combined representation-and-bridge proposal, not an isolated causal property of gregariousness.

## What this changes

The earlier human-only ranking established that a good measurement of Gregariousness could add useful information about human profiles. This follow-up does not establish that the existing model indicator supplies that measurement. It gives no basis to relax the gate for this candidate, claim a strong human bridge, or infer that extracting more traits would necessarily solve the problem. Additional coverage remains a potential benefit whose realization depends on measurement validity.

A useful next design task would localize the largest disagreements by inspecting the gregarious and anchor extraction specifications, then specify a prospectively testable bridge. Any revised mapping must be recorded as a new exploratory specification; choosing mappings to improve these observed correlations cannot validate them on the same comparison. No additional extraction is justified solely by these results.

## Reproduction and verification

Run `python run_analysis.py --raw /path/to/IPIP300.dat`, then `python verify_analysis.py --raw /path/to/IPIP300.dat`, then `python build_report.py`. Python package versions, seeds, and source hashes are in results/run_metadata.json. Inputs are frozen aggregate model data and mapping/scoring specifications. The raw human file is external; private intermediates are ignored and excluded from the commit.

Independent verification reconstructs human scores from fixed-width bytes, builds model composites from the mapping strings, checks all fingerprint correlations with scipy.stats.pearsonr/spearmanr, verifies specificity comparisons and both permutation families, and checks stored bootstrap intervals. results/verification.json contains the actual errors and status. No full historical factor pipeline, viewer, raw model extraction, or unrelated workstream was rerun. The separate addition does not rewrite historical migration inventories. No method changes were made after viewing results.

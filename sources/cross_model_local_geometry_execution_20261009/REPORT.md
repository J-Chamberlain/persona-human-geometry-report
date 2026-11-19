# Cross-model local semantic geometry: completed late-layer study

**Llama and Gemma reproduce similar relationships among these twelve concepts in their MFA reconstructions across held-out contexts: primary Spearman rho = 0.839.** Domain-preserving and domain×valence-preserving permutation p = 0.000200 each. This supports the specified relational comparison beyond those controls, **not agreement between identified individual regions or hidden subspaces**. Raw activations give almost the same agreement (0.834); MFA superiority is not demonstrated. No component qualifies for the four planned named-region illustrations under the frozen token-support rule.

The authorized primary experiment is complete. All 640 texts/model, raw retained tokens, lineage and exact all 8K posterior summaries are preserved. Conservative total machine/storage spending is **at most $1.213**, versus the $21 ceiling; the task-filtered provider ledger remains delayed, with zero records, which does **not** mean free execution. Both task pods and attached disks are verified deleted. No early-layer analysis, extra anchors, new MFA training, paid annotation, generation, Qwen/Friendliness replay or steering occurred.

## What was tested

The [October8 protocol](../cross_model_local_geometry_20261008/protocol.md) and its bank/schedules remain byte-exact. Twelve working concepts: friendliness, warmth, intimacy, sociability, compassion, trust, gratitude, love, joy, sadness, anger, loneliness. Each has 24 authored context families and implicit/explicit lexical conditions; 64 reference texts come from the authors' synthetic labeled bank. Whole families: 12 development, 6 evaluation A, 6 evaluation B. These are curated stimulus labels, not independent psychological judgments.

Subjects are base `meta-llama/Llama-3.1-8B@d04e592bb4f6aa9cfee91e2e20afa771667e1d4b`, block 22 resid_post/D=4096, and base `google/gemma-2-2b@c5ebcd40d208330abc697524c919956e692655cf`, block 18 resid_post/D=2304. Released late MFAs at `db871d79436ddd3eebf072bdc8a1b73e3d6acbd9`: 8000 components, rank 10,shared positive diagonal noise. Full LM shard and MFA hashes verified before use. [Technical evidence](technical_results/), [parameter checks](CHECKPOINT_PARAMETER_VERIFICATION.json).

Native fast-tokenizer input, one BOS, no EOS/chat/instruction/generation/truncation. Full original text prefixes precede each target clause; character overlap identifies retained tokens. Llama processed 19,384 / retained 9,480; Gemma19,184/9,328. Inference stops immediately after the target block; later decoder blocks cannot change its residual. Technical timing/parity forwards are additional excluded repeats, not extra independent research examples. [Exact tokens](token_counts.json), [token lineage verification](RUNTIME_VERIFICATION.json).

**Documented reconstructed loader, not exact replication of the unknown original environment:** TransformerLens 2.16.1, Torch 2.8.0+cu128, Transformers 4.56.2, FP32, TF32 disabled. Inspected and installed loader source hashes match. Author-route defaults fold RMS scales; writing-weight centering is skipped for RMS/RMSPre, and Gemma unembedding centering is disabled by logit softcap. Token-list/string IDs and independent hook/cache residuals match on 8 references/model (relativeL2=0). No native-HF residual substitution or known coordinate mismatch was used. Original author LM/TL revisions/dtype and a gold activation pair remain unavailable; internal parity and fit screens support this reconstruction but do not establish original-run coordinate identity.

Exact likelihood-consistent posterior over all 8000 components, component chunk 256 / token batch 16: centroid term `c=sum(r*mu)`, local displacement `d=sum(r*W*E[z|x])`, reconstruction `xhat=c+d`. Cached shared-noise Cholesky factors; no top-component shortcut or fitting. Author-code parity on 32-component subsets and 2 complete 8K rows/model passes the frozen log-prob/D and reconstruction tolerances. Maximum full8K reconstruction difference is 1.11e-7; Gemma's small-subset responsibility difference is 1.58e-5, with reconstruction difference 5.64e-6. Priors/noise are positive and finite.

Reference/development median relative reconstruction errors: Llama 0.682/0.662, Gemma 0.728/0.696; development p95 also passes the frozen 2× reference gate. Held-out medians 0.651/0.694. These substantial errors limit fidelity; the reference bank is not original Pile validation or psychological truth. Both LMs/encoders were kept resident on one A10080 after measured memory permitted it, an operational departure from the card's proposed unload/reload route. Peak allocated VRAM 55.5 GB (51.7GiB).

## Frozen outcomes and controls

Each implicit clause is character-pooled after token MFA application; six families are equally averaged per concept/half. RSM = negative squared full-dimensional Euclidean distance/own median pair distance. Primary averages Spearman(LlamaA,GemmaB) and Spearman(LlamaB,GemmaA), using 66 dependent upper-triangle edges. No cross-model coordinate alignment is needed; translation, scalar scale and orthogonal axes do not affect these ranks.

| Prespecified comparison | Result |
|---|---:|
| Primary MFA reconstruction, cross-context rho | **0.839** (halves0.777/0.901) |
| Frozen paired-family percentile95% interval | **[0.605,0.837]** |
| Unrestricted label / within-family phrase-assignment p |0.000100 /0.000100|
| Domain / domain×valence label p |0.000200 /0.000200|
| Within-model A/B reliability: Llama / Gemma |0.877 /0.885|
| Raw / centroid / local displacement cross-context rho |0.834 /0.767 /0.718|
| Eight interpersonal concepts, descriptive rho |0.606|
| Mean top3 neighbor Jaccard |0.554|
| Word pooling / explicit cue / last-token rho |0.826 /0.832 /**0.345**|
| Descriptive rank-residual nuisance-adjusted rho |0.680|

All 10,000 draws for each null and 1000 paired whole-family bootstrap draws are retained; none is undefined. Domain×valence permutation space 241,920, of which 9804 unique permutations were sampled. The same Gemma label permutation applies in both halves; phrase assignment is separately permuted within each family and recomputed. No independent-edge null is used.

**The frozen percentile interval lies slightly below the point estimate.** Independent full-dimensional pair loops/SciPy reproduce every bootstrap draw. Bootstrap mean 0.748 versus original 0.839: resampling six families with replacement produces a downward-biased distribution in this small bank. The percentile method was not changed, recentered or clipped to include the point. Treat the nominal interval cautiously, conditional on this finite bank and fixed concepts/model fits.

Twenty fixed alternate context splits yield rho 0.801–0.861; leave-one-family-out 0.793–0.849. Same-context agreement 0.919 is higher than the cross-context primary, showing why the latter was frozen. Raw agreement 0.834 versus MFA 0.839 supplies no demonstrated method advantage. Last-token agreement/reliability is markedly weaker: **the result depends on pooling across the clause and does not establish a stable terminal-token semantic representation**.

Nuisance adjustment includes fixed domain/valence/arousal, target-word overlap, length, subword segmentation and relative token-position summaries (design rank 20 on 66 edges). Its positive 0.680 is descriptive, with no conditional p claim, and does not causally eliminate lexical/topic confounding. The bank has repeated templates/synonyms and one subject name. One authored bank, two model architectures/sizes, approximately matched depths, and one released MFA fit/model do not estimate population semantics, MFA-seed stability, psychological validity or causal control.

## Region support and figures

Illustration selection was fixed before activations: implicit development only, per-concept hard-assignment support in at least 6 families and 20 token occurrences, at most 4 components by posterior mass. Family support reaches 10–12, but the largest component's token support is only 10–12 for these concepts. Consequently friendliness/warmth/intimacy/sociability are **all unsupported in both models**. Thresholds were not relaxed and explicit duplicate clauses were not added to manufacture support. This is insufficient token coverage for the illustration, not evidence that a region is absent or unstable. No named center-neighbor graph, cross-model region map or subspace alignment is claimed; no extra anchors were extracted.

[Matched RSMs](results/matched_RSMs.png), [null/raw/reliability controls](results/controls.png), [all-concept neighbors](figures/concept_neighbors.png), [support gap](figures/region_support.png), [Llama development geometry](figures/llama_development_geometry.png), [Gemma development geometry](figures/gemma_development_geometry.png). All scientific distances use full coordinates. Development-token PCA3 retains 14.9%/19.1%; model axes are separate and display spacing is not evidence. Colored clouds are observed tokens with stimulus labels, not inferred named regions or synthetic Gaussian samples. Initial empty region placeholders remain under results/ for exact reproduction; the explanatory figures make their unsupported status explicit.

## Decision

This bounded study provides positive evidence for **cross-context relational agreement in MFA-reconstructed token geometry**, beyond the frozen label/phrase and coarse domain/valence controls. It does not show that MFA is necessary, that individual semantic regions match, or that factor axes/subspaces have cross-model correspondence. Retain the near-equal raw baseline, pooling dependence, biased bootstrap and unsupported-region outcome. A next scientific step would need an independently authored bank and sufficient per-region token support; any additional inference/anchor analysis requires a separate decision. This authorization is complete, with no active machine or paid storage left.

Source basis: [paper](https://arxiv.org/abs/2602.02464), [published paper](https://proceedings.mlr.press/v306/shafran26a.html), [inspected author code](https://github.com/ordavid-s/decomposing-activations-local-geometry/tree/ae8aa7c8f25a917256826d2d50561784942d8fed), [MFA revision](https://huggingface.co/ordavids1/decomposing-local-geometry-MFAs/tree/db871d79436ddd3eebf072bdc8a1b73e3d6acbd9), [planning package](../../planning/cross_model_local_geometry_20261008/feasibility_report.md). The published paper did not report this matched cross-model test; this is a new scoped study with a reconstructed loader.

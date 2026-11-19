# Cross-model trait relationships: decision brief

**The pattern is partly shared and strongly indicator-dependent. Qwen's positive negative-Avoidant–Hostile association does not replicate in Llama or Gemma. Flirty–Hostile is positive in all three; care–hostility is consistently negative.**

| Historical relationship, original Pearson r | Qwen | Llama | Gemma |
|---|---:|---:|---:|
| Negative Avoidant–Hostile | +.581 | −.706 | −.245 |
| Charismatic–Hostile | +.738 | −.307 | +.539 |
| Flirty–Hostile | +.774 | +.674 | +.725 |
| Nurturing–Hostile | −.476 | −.900 | −.810 |
| Benevolent–Hostile | −.476 | −.956 | −.939 |

These use the same 275 persona IDs and historical all-layer, rank-normal measurements. The signs above survive every eligible group exclusion, fixed alternative weighting and single-persona deletion. Original-cosine scoring gives the same sign pattern.

**Broad style matters across models, but Formal has different associations with social approach.** With the same five style controls, negative Avoidant–Hostile becomes +.071/+.118/+.112; all three bank-bootstrap intervals include zero. Nurturing–Hostile remains −.699/−.879/−.850. Joint conditioning removes 71–83% of Hostile variance and may remove personality content too; these are not validated corrected scores or causal effects.

The full 240-trait relationship patterns agree substantially across models (fingerprint r=.733–.868), while particular labels such as Avoidant have weak or reversed corresponding-persona agreement. Shared prompts, extraction methods and bank construction remain entangled with model-specific representations. These three models are not a random sample of model families.

The human Friendliness–Anger value −.280 is contextual: these historical indicators are not the official IPIP facets. No Llama/Gemma Direct-12 measurements were fabricated. AA27's failed gate and all prior studies remain unchanged.

[Full report](REPORT.md) · [Original/style-conditioned figure](figures/primary_correlations.png) · [Weighting](figures/weighting_sensitivity.png) · [All figures](FIGURES.md) · [Verification](verification_report.json)

# PHG-TOOL01 — Interactive trait correlation explorer

The existing publishing viewer now includes one reusable matrix below the original trait comparison tool. The Site, audience, original controls, sibling assets, and public paths are preserved. This is a saved-data tool release; no scientific study, extraction, inference, factor/PCA refit, human-data access, GPU or paid service was run.

## Comparisons

| Preset | Statistic and scope |
|---|---|
| 1. Within-model traits | Pearson r across 275 personas, all 240 historical traits, Qwen/Llama/Gemma. |
| 2. Cross-model differences | Separate within-model matrices or A minus B, fixed shared trait ordering, Δr range −2 to +2. |
| 3. Cross-model trait matching | Pearson r over exact matched persona IDs, with independent model/trait axes. No native hidden-coordinate mixing. |
| 4. Traits and factors | Pearson r with original AA17 saved factor scores, or explicitly labeled oblique pattern coefficients. |
| 5. Factor correspondence | Signed Tucker congruence across all 240 original oblique pattern rows. Cell detail distinguishes original PHG-CM01 assignments and alternatives. |
| 6. Traits and components | Pearson r with Qwen T1–T5 or model-specific AA18 C1–C5. |
| 7. Qwen IPIP | Separate scenario/survey-style 26-facet matrices; independent axes also support cross-format exploration. |
| 8. Human versus Qwen | Separate source matrices or Qwen minus human, using frozen 30,000-reference human correlations. |
| 9. IPIP and geometry | Qwen direct facets against historical traits, F, T, C; advanced manual axes include original activation PC1–PC10. |

Manual axes remain configurable after a preset. Each has model/source, representation, format, search, custom exact-name/code selections, and ordering. Historical traits support alphabetical, strongest F/T/C association, and deterministic average-linkage signed-correlation ordering. Component focus ranks the strongest absolute empirical associations within that component's model; factors remain overlapping. Fixed ordering uses A's order across comparison panels. Available filters include the frozen PHG-CM01 54 traits, IPIP domain, all 6 close-agreement or 13 reversal pairs, and custom selections. Frozen pair filters mask other cells, including self-pairs, rather than create a new screen.

Canvas rendering is restricted to the visible scroll viewport, even at maximum zoom. Labels stay pinned and thin out at small cell sizes; zoom to read every label. Cell selection, hover, tap and native X/Y selectors expose exact values; the latter and previous/next buttons provide keyboard access. Paired-score scatterplots show all 275 personas with point titles. Human respondent scores are never bundled or plotted.

## Scientific boundaries

- Historical trait/F measurements use the original all-layer-mean cosine pipeline (Qwen3-32B, Llama-3.3-70B-Instruct, Gemma-2-27b-it). Original checkpoint revisions, masks and contrast-level extraction uncertainty remain unresolved.
- Direct IPIP uses newer Qwen block-48 directions and saved rank-normalized scores. N3/C3/E3/N5 remain excluded. Direct Llama/Gemma IPIP is unavailable; historical proxies are never substituted.
- AA17 F, October 25 Qwen T, AA18 C, and original activation PCs are distinct. C uses each model's `qwen_score`/`llama_score`/`gemma_score` columns, not shared `consensus_score` or held-out columns. Original saved signs are retained.
- Tucker congruence is an uncentered pattern cosine, distinct from Pearson score correlation. Oblique pattern loadings are fitted coefficients and may exceed 1; the display clips at ±1.2 while cell detail retains the numeric value. Pearson uses a fixed −1…+1 blue/red scale, Δr a −2…+2 brown/teal scale, and congruence its own −1…+1 purple/green scale.
- AA17 Llama F4/F5/F6 and Gemma F5 remain individually unresolved. Component association and matching do not establish interchangeable psychological meanings or exclusive trait membership.
- Existing conditional PHG-CM01 2,000-persona bootstrap intervals are reused for covered selected pairs and trait/F cells. Raw-sign difference intervals explicitly undo frozen semantic polarities. The October 19 source supplies ordinary human and Qwen IPIP intervals; its separate approximate simultaneous bands are not a joint 95% guarantee. Human–Qwen difference intervals are unavailable, and marginal intervals are never subtracted. No new bootstrap is run.
- Human questionnaire respondents and authored model personas are unpaired. Mixed human–model axes return missing. Model-human differences compare marginal structures, not individuals. No wellbeing, causal, human-plausibility, measurement-invariance or behavioral-validity conclusion follows; AA26 corrections and AA27's failed primary gate remain unchanged.

## Inputs and reproduction

[Public source manifest](../public/trait_profile_geometry_explorer/correlation-v1/manifest.json) records immutable Git commits, source paths, byte sizes, SHA256 values, environment, builder/runtime hashes and output hash. PHG-CM01 is pinned to `cc4ef374b69ecd5337efa33b8dae3e25cf8e9347`; Qwen's October 26 reference to `fc764f842edc7bb04935875e2eb267e49ad45ffd`. The 15 saved model-score blocks contain only permitted model-persona measurements. Human data consist only of aggregate correlations and intervals.

Use Python with NumPy/Pandas (bundled desktop Python was used; exact versions in the manifest). In a full clone with the pinned commits available:

```sh
python3 web/build_correlation_data.py
node web/test_correlation.cjs
node --check web/correlation-explorer.js
python3 -m http.server 8766 --bind 127.0.0.1 --directory web/public
```

If a pinned commit is absent from a shallow clone, fetch the specified commit from the same repository. The builder verifies upstream hashes before use and writes only this task's public data and verification report. No raw humans or external private runtime files are required. `web/correlation-explorer.js` and `.css` are reusable source assets; copy each into the existing public explorer directory after editing. The runtime check rejects a stale JS copy. The build is deterministic within its recorded environment and seed-free; clustering is display-only ordering of fixed correlations.

## Verification

- [Data verification](data_verification.json): 4,080 trait/F associations, 4,293 selected historical pair correlations, 650 direct IPIP cells, 780 IPIP/F/T/C associations, 96 full-pattern factor correspondences, all 591 paired model-difference signs, 30 T/activation-PC1–PC6 values, and all 975 interval source point estimates match frozen outputs. Source-table errors are below 2e−12; rounding's maximum within-block correlation discrepancy is below 2e−10 (required tolerance 1e−9).
- [Runtime verification](runtime_verification.json): 216 numerical checks plus schema, missingness, zero variance, invalid source, human privacy, source hash, integration, and ordering checks.
- Browser QA covers all nine presets, independent formats/axes, models, domains/custom/research filters, F/T/C ordering/focus, zoom/scroll, canvas selection, paired scatterplots, human separation, desktop and 390/320 px mobile layouts. Original persona comparison, equalizer edit/reset, difference graphs and 2D/3D controls are exercised. Evidence is in `browser_verification.json` and screenshots.
- [Site reconciliation](site_reconciliation.json): imports 8 independently advanced Site assets, preserves all 32 pre-task assets, and identifies Cloudflare's sole live/source HTML difference. All sibling assets are byte-identical to the refreshed existing Site checkout. The original explorer changes only by the new section, stylesheet and script references.

Publish with `scripts/export_site.py` and the existing authenticated Sites source/archive/save/deploy workflow. Never run the publishing checkout's legacy preparation scripts. See [web/README.md](../README.md). Deployment receipt is recorded after successful publication; export alone is not deployment. No PHG-TOOL02 or further research is authorized by this release.

## Published release

**Version 25 deployed successfully**, public audience preserved, on the original [Trait-Profile Geometry Explorer URL](https://persona-trait-landscapes.josiah-chamberlain.chatgpt.site/trait_profile_geometry_explorer/trait_profile_geometry_explorer). [Publication receipt](publication.json) records the saved version/deployment IDs, exact Site source commit and archive hash. [Post-deployment verification](deployed_verification.json) confirms served data/code hashes, the canonical guide and both existing viewer routes; the live browser reproduces the human–Qwen example with no console errors. [Deployed screenshot](deployed.jpg). PHG-TOOL01 is complete; no further study or TOOL02 was initiated.

## Browser combination follow-up

The [combination audit](COMBINATION_AUDIT.md) exercises all241 supported source-pair/statistic configurations and all68 comparison displays through actual browser controls. Unsupported source/statistic/view/filter combinations are now disabled or synchronized before rendering. Within-source comparison views preserve matched labels; mixed manual axes retain single-matrix score correlations. Comparison B has a separate Qwen IPIP format selector, including Human→Qwen navigation. The source data are unchanged. The audit links exhaustive CPU/browser evidence and records the follow-up publication separately.

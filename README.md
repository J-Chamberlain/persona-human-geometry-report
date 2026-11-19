# Persona–Human Geometry: report and reproducibility package

[Read the published report](https://j-chamberlain.github.io/persona-human-geometry-report/). Author: Josiah Chamberlain. Personas, trait list and released model vectors: Lu et al. (2026), *The Assistant Axis*; human reference: Johnson IPIP-NEO and SAPA; GPT questionnaire comparison: Petrov et al. (2024). External papers/providers retain their original credit and links.

**Package branch: `codex/self-contained-package`. Not merged or deployed.** The published `index.html` is unchanged. This is a packaging change, not a new analysis or a scientific correction. Claude Code will later switch the report's reader-facing references using [REFERENCE_MAP.csv](REFERENCE_MAP.csv), rebuild, and audit them with Josiah.

**Offline reader package:** all report inputs are now packaged, including a [PHG-authored cited table of the50 published values](data/published/domain_correlations_petrov2024.csv) used by Figure5.1. The original Petrov CSV is not redistributed and is not a build dependency; `scripts/download_petrov.py` remains an optional route to it. See [DATA_SOURCES.md](DATA_SOURCES.md) and [HANDBACK.md](HANDBACK.md).

**Licence:** copyright 2026 Josiah Chamberlain. PHG code is MIT; PHG report text, figures, derived data and extraction materials are CC BY 4.0. [LICENSE](LICENSE) defines the folder scopes and third-party exceptions.

The source was frozen from research branch `claude/phg-report-notebook-20261101` at **`53a249656ac1b0a318424662f101838ceac36537`**, also named by the current published page, based on report-repository main `46da81aface8da4c3274a279870d1c9dcb3f31e8`. Later notebook edits belong to the editorial handoff. Runtime code no longer invokes `git show`, `git cat-file`, the research checkout, its object cache, or migration adapters.

## Trace a number or method

1. Find the reader figure/section in [REFERENCE_MAP.csv](REFERENCE_MAP.csv) or [inventory coverage](provenance/inventory_coverage.csv). The latter records both the reader's figure number and the original internal build key; they differ.
2. Open its local saved table under [data/saved/](data/saved/) and the relevant scientific evidence under [sources/](sources/). [MANIFEST.csv](MANIFEST.csv) records every payload file's SHA256, size, uses, original repository/commit/path/source hash and any transformation/subsetting.
3. Follow the corresponding function in [phg/analysis.py](phg/analysis.py) or check in [phg/checks.py](phg/checks.py); [check-source index](provenance/check_sources.csv) links the audit IDs to packaged data/report evidence. `RECOMPUTED` recalculates statistics from saved aggregate/persona results; `CHECKED` compares saved values; `HASH-ONLY` verifies bytes. A hash is not independent measurement recreation.

[provenance/evidence_registry.json](provenance/evidence_registry.json) resolves each old pinned origin to its packaged representation. Snapshot verification re-derives deterministic subsets from **packaged evidence**, not a research Git blob. Original source hashes remain provenance; redacted public copies have separate hashes. Only private absolute paths and operational/cost sections/fields were withheld; no scientific numerical field or study status was changed. Historical source reports may mention unprovided historical files that are not part of level1.

## Layout

- `index.html`: current published reading copy, preserved exactly; not the output target of this task.
- `phg/`, `report/`: analysis/rendering/check code, prose, output-free generated notebook, tests and the vendored MIT Plotly bundle/recipe. No notebook working notes, screenshots or editorial queues.
- `data/saved/`: 64 snapshot inputs plus two external aggregate/provenance files. Historical trait/factor/persona geometry is model-derived, not human respondent data.
- `sources/`: only scientific reports/result files reached from the input registry, checks, methods or reader references. Descriptive directory names explain internal study codes: `historical_trait_factors` = AA17 F; `shared_consensus_directions` = AA18 C (displayed as D in this report); `human_consensus_validation` = AA19; `human_bridge_corrections` = AA26; `human_facet_bridge_coverage` = AA27; `direct_facets_human_comparison` = final Direct-30 B.
- `extraction/`: portraits, scenario/statement banks, rubrics, item maps and criteria for all30 facets, plus frozen scientific protocol/estimator files. [Counts for all30](extraction/counts_all30.csv) preserve excluded N3/C3/E3/N5 and their format-level outcomes; [excluded-count provenance](extraction/excluded_count_provenance.json) records sealed-summary fingerprints without copying runtime journals.
- `scripts/`, `data/downloads/`: opt-in pinned public-input downloads and a deeper measurement recipe. Large binaries and raw human files remain ignored and uncommitted.
- `verification/`: baseline and package verification evidence. [EXCLUSIONS.csv](EXCLUSIONS.csv) lists explicit holds and stale operational references; [DATA_SOURCES.md](DATA_SOURCES.md) records permissions and unresolved licensing.

## Level1 — rebuild the analysis from saved results, CPU

Install the frozen Python dependencies (internet needed for environment setup, not numerical execution):

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r report/requirements-notebook.txt
pip install -e . --no-deps
python -m pytest -q report/tests
python scripts/verify_package.py
```

All81 source tests are retained; four packaging-boundary tests cover no Git fallback, hash-tampering refusal, pending-source holds and the reader input without the original Petrov file. The adapted suite has85 tests.

No data downloads are required for the standard READER build:

```sh
python scripts/rebuild.py
```

The build runs entirely offline after dependency installation, regenerates snapshots/inventory/notebook and writes `report/phg_report.html` plus the check ledger. It never writes `index.html` and does not access an original Petrov CSV, research checkout, cached research Git objects, activation vectors or raw human data. The50 published coefficients and all Figure5.1 numerical inputs/template fits agree exactly with the previous reader path; [verification](verification/PUBLISHED_VALUES.json) records the comparison.

For optional retrieval of the authors' original file only, use `python scripts/download_petrov.py`. That file is hash-verified, remains Git-ignored, and is neither required by nor substituted into the READER build. This does not assert a redistribution licence for the original file.
Baseline: **628 PASS,3 NOTE,2 SKIPPED;81 tests**. Packaged reader: **624 PASS,3 NOTE,6 SKIPPED;85 tests**. Three additional skips are the explicitly pending steering/substitution sources. One additional skip is the stale inventory pointer to a zero-response IPIP startup failure, excluded as operational history; the completed retry's null brief is packaged separately, without retargeting that source check or changing the narrative. The original two human-raw-data skips and all three notes remain. The former original-file hash check is now explicitly a hash check of the PHG cited table; it is not presented as verification of the original file. [Verification comparison](verification/REBUILD_COMPARISON.json) enumerates every changed status/observation and preserves the baseline ledger. All passing numerical observations agree with the baseline within the recorded comparison tolerance.

For validation with IP networking denied, set `PHG_KERNEL_IPC=1` to use local IPC for the notebook kernel instead of loopback TCP.

Optional browser check:

```sh
npm ci
npx playwright install chromium
node report/check_html.cjs report/phg_report.html
```

The browser checker blocks external requests and exercises desktop/phone figures and menus. Test setup/dependency downloads are separate from offline report execution. See [HAND BACK commands and results](HANDBACK.md).

## Level2 — recreate underlying measurements (not executed here)

This level was **not re-executed for packaging**. It is not implied by source hashes or level1 tests.

- Released historical persona/trait cosines can be recreated on CPU after downloading the pinned Lu role/trait tensors, e.g. `python scripts/download_vectors.py --model qwen-3-32b`, then `python scripts/recompute_released_scores.py --model qwen-3-32b --output data_external/recreated-qwen`. The optional recipe needs `torch`, loads only verified saved tensors, and uses float32 all-layer means followed by float64 normalized cosine. It does not run a model. Repeat separately for Gemma/Llama; original checkpoint/mask provenance remains unknown where the source did not release it. PCA refitting and upstream factor retention/selection are deeper analyses, not hash checks.
- Independent Johnson human-scoring checks require `python scripts/download_ipip.py --only IPIP300.dat` and `python scripts/rebuild.py --mode REPRODUCTION`. The packaged manifest/spec preserve already-keyed responses, ages18–80, complete answers, exact-pattern deduplication, seed20260920,30k/10k/10k pools and reference-fitted transforms. The mode also runs additional independent bootstrap arithmetic where implemented. It does not recreate every underlying study, model extraction, held-out prediction or uncertainty family.
- Re-extracting the30 direct facets requires model weights/access, GPU inference, the packaged author materials and frozen protocol, scoring/judging and extraction records. The original raw model responses/activation records and judging locks are not packaged. They are needed to independently recreate accepted contrasts and their exact stopping histories; absent them, new inference would be a new measurement, not a deterministic rebuild. No model weights, GPU calls, new responses or paid work were used here.
- Exact human held-out predictions and full respondent/question uncertainty cannot be recreated from aggregate tables alone; raw human data, original fitted objects and/or extraction records are additional dependencies. The report uses saved aggregates and retains their conditional/adaptive limitations. A raw-data download is not equivalent to refitting all original analyses. SAPA refits similarly require separately acquired provider data and original psychometric fits, not supplied respondent records.

Activation PCs, historical factors F, consensus directions C/D and trait-score PCA T remain distinct. Historical proxies are not directly extracted Johnson facets. AA26 corrections/withdrawals, AA27's failed bridge, excluded facets and nulls retain their status. No packaging result establishes human behavioral validity or causal control.

## Integrity and release status

Every payload file is SHA256-listed in MANIFEST.csv; the manifest cannot hash itself and is bound by the package Git commit. Generated local HTML, raw downloads, environments, caches and node_modules are excluded. PHG-authored code is MIT and the report materials are CC BY 4.0, subject to the third-party exceptions in LICENSE. No merge, deployment or scientific revision is included in this task. The fresh-clone offline reader gate is documented in verification/FRESH_CLONE.json. The inherited Figure E.6 phone-layout failure remains recorded separately and was not changed in this packaging task.

# Packaging handback for Josiah and Claude Code

## Freeze and ownership

- Report package branch: `codex/self-contained-package` in `J-Chamberlain/persona-human-geometry-report`. The final remote commit is supplied with the completion message; this document is bound by that commit.
- Frozen notebook source: **53a249656ac1b0a318424662f101838ceac36537**, research branch `claude/phg-report-notebook-20261101`.
- Report-repository baseline: **46da81aface8da4c3274a279870d1c9dcb3f31e8**. `index.html` remains byte-identical. Neither repository's main branch nor the notebook branch was edited during packaging. No merge or deployment occurred.
- Stage2 remains Claude Code's work: rewrite reader-facing references, rebuild the reading copy, and perform the reference audit with Josiah. This branch does not silently change the current page's citations or findings.

## Reference and provenance files

[REFERENCE_MAP.csv](REFERENCE_MAP.csv) contains280 reader-facing reference occurrences: printed source-table rows, Appendix G source lines, Appendix A.14 PHG method citations, the printed snapshot-manifest path, research-repository hyperlinks and original external credit/citation links. External links stay external. Old RESEARCH_STATE pointers map to scientific reports; no state/coordination file is copied. A printed source-table row remains one reference occurrence even if repeated elsewhere.

[provenance/inventory_coverage.csv](provenance/inventory_coverage.csv) accounts for all138 original inventory rows, including rows for no-longer-displayed figures. It records both the internal key and `DISPLAY_NUMBER` reader label. Every row has a packaged destination or an explicit hold/stale-pointer reason. [provenance/original_inventory.csv](provenance/original_inventory.csv) preserves the exact frozen input inventory.

[MANIFEST.csv](MANIFEST.csv) hashes every release payload file, including source reports, snapshot inputs, extraction materials, build code and this handback, and records upstream origin and transformations. It excludes only itself because a manifest cannot self-hash; the package Git commit binds its bytes. [Evidence registry](provenance/evidence_registry.json) supplies runtime origin→packaged-file resolution. [Check-source index](provenance/check_sources.csv) covers all633 baseline check records, locating check groups, candidate input tables and scientific reports; the exact operations remain in `phg/checks.py`.

## Holds, uncertainties and discrepancies

1. **Petrov published CSV: licensing hold, confirmed by Josiah.** No licence was found at the pinned upstream commit, and Josiah answered that he has no permission. The table is not committed. Its identity, SHA256, URL and opt-in local retrieval are documented in DATA_SOURCES.md and `scripts/download_petrov.py`. Consequently the strict fresh-clone, entirely offline full-reader acceptance gate is **BLOCKED**. After an explicitly documented external aggregate download, offline rebuilding is verified. This is an exception, not a passed version of the original gate; do not merge it away without review.
2. **Explicit pending studies:** E1 steering confirmation `8bf7cb6` and historical substitution `22ab297` inputs are not packaged. Their inventory/source references remain flagged in EXCLUSIONS.csv and REFERENCE_MAP.csv. Three formerly passing presence/hash checks now SKIP; their numerical results are neither invented nor republished here.
3. **Mis-targeted IPIP source pointer:** the original inventory key `ipipq_brief` names `...primary/final-review/DECISION_BRIEF.md` at `0013a4d`, an operational zero-response startup failure. The report discusses the completed retry's aggregate null. The actual `...retry01/final-review/DECISION_BRIEF.md` is packaged, and the stale operational file is excluded. The registry/check was not retargeted as though it were unchanged: its presence/hash check now SKIPS, and the reference map gives the completed scientific source for later editorial review. No study status or narrative number was fixed.
4. **Existing rounding notes retained:** `1.pc.gemma`, `5d.cm01.Charismatic × Hostile.Llama`, and `5d.cross.Nurturing – Hostile.Qwen.conditioned on five styles` retain their baseline NOTE status. The ledger comparison found no unexplained numerical observation changes at absolute tolerance1e−10.
5. **Phone browser failure retained:** the original full browser check exits1 because Figure E.6's axis title extends12.046875 pixels left of its container. The same check on the unchanged published `index.html`, in the same browser, fails identically. Desktop and phone have zero console/interaction errors and zero external requests; iPad touch interactions pass. No layout fix was made in a packaging task. Full machine-readable baseline/package browser results are supplied; the global browser verdict remains FAIL, not PASS.
6. **PHG code/report licence:** no top-level licence existed at the source freeze. This task does not invent an MIT grant for the author's work. LICENSE records that choice as unresolved. Plotly's MIT notice, Lu's MIT dataset declaration and IPIP public-domain permission are separate, documented permissions. SAPA raw-data metadata could not be rechecked (provider403); no raw SAPA assets are distributed or relicensed, only PHG-derived aggregate results.
7. **Stale source inventory prose:** inherited build registry gap text mentions skeleton sections, historical matrices not snapshotted, missing26-facet calibration and obsolete historical-branch availability. The frozen report already contains later additions contradicting those old inventory notes. They are recorded here, not rewritten as new scientific corrections. Claude should reconcile those editorial notes during stage2. Source reports also retain references to deeper historical artifacts not needed for the report build; this package does not promise archive-wide reproduction.
8. No numerical finding/source discrepancy beyond the preserved rounding notes was found by the executed ledger comparison. This is a scoped saved-result comparison, not an independent audit of every scientific claim or source paper.

## Included materials and deliberate omissions

All30 facets have high/low portraits, scenario questions, survey-style statements, rubrics, assessment schemas, item maps and criterion weights. Frozen scientific configuration/prompts/schedules and exact stopping-function bodies are included; launch/budget/coordination functions and fields are omitted with provenance. `extraction/counts_all30.csv` combines the original52 qualified-format count rows with8 excluded-format aggregates derived from sealed summaries; summary fingerprints are preserved without distributing response records or journals. Format-level passes inside excluded facets remain visible.

AA17/AA18 factors/shared directions, the AA19 human validation, AA26 corrections/withdrawals, AA27 failed coverage gate, uncertainty tables, convergence audit/calibration, and the completed questionnaire null are included where reached by the report. Human observational associations, model projections and causal claims retain their boundaries. No raw human rows, private absolute paths, credentials, activation binaries, model weights, execution receipts/cost records, agent coordination files, notebook queues/screenshots, public-viewer code or unrelated study folders are distributed.

No level2 measurements were recreated. Public vectors and Johnson raw responses are script-only external dependencies. Original direct-extraction response/activation records and judging locks are unavailable in the package; new model execution would be a new measurement. Aggregate hashes cannot independently reproduce them.

## Verification commands and status

The acceptance run uses a **fresh local clone of the package branch**, a separately installed pinned Python environment and one openly downloaded, hash-verified Petrov aggregate outside the clone. An OS sandbox denies research-checkout reads, archived notebook-data reads, Git/GitHub CLI execution and all network sockets; the kernel uses opt-in local IPC transport. Deliberate source-read and external-network probes confirm those denials.

Commands (run from the fresh clone after dependency setup):

```sh
python scripts/verify_package.py
python scripts/rebuild.py                    # expected BLOCKED with Petrov absent
python scripts/download_petrov.py --dest /tmp/phg-petrov-local.csv  # separate explicit network setup
PHG_PETROV_FILE=/tmp/phg-petrov-local.csv python scripts/rebuild.py
PHG_PETROV_FILE=/tmp/phg-petrov-local.csv python -m pytest -q report/tests
python scripts/compare_verification.py
node report/check_html.cjs report/phg_report.html
```

Only the explicit local data download and dependency installation need internet; no human raw file or vector bank is accessed. Set `PHG_KERNEL_IPC=1` for the sandboxed notebook kernel. The sandboxed rebuild, tests and comparison use only the clone plus the documented held aggregate. The absent-input run must fail clearly; no figure is silently omitted or replaced. The full reader ledger is **624 PASS,3 NOTE,6 SKIPPED**, compared with **628 PASS,3 NOTE,2 SKIPPED** at the freeze; all81 original tests plus3 packaging tests pass. Check tiers now truthfully name packaged evidence rather than research Git objects. Independent re-extraction/human refitting is not claimed.

[REBUILD_COMPARISON.json](verification/REBUILD_COMPARISON.json), [FRESH_CLONE.json](verification/FRESH_CLONE.json), [public audit](verification/PUBLIC_AUDIT.json) and browser records supply exact results, size and commands. Repository payload and packed-Git size are recorded in FRESH_CLONE.json. The research-main documentation entry requested after acceptance was **not made**, because the strict offline gate remains blocked; no scientific finding changed and the task card forbids other research-repository edits. Josiah can decide the licensed-input/acceptance exception before that closeout and any merge.

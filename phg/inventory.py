"""Planned-figure registry and INVENTORY.md / INVENTORY.csv builder."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from . import sources as S


@dataclass(frozen=True)
class Fig:
    id: str
    section: str
    title: str
    status: str  # BUILT or SKELETON
    sources: tuple[str, ...]
    tier: str
    tier_note: str = ""


FIGURES = [
    # Former headline figure, Figure 4.1 since iteration 28 (key stays "H")
    Fig("H", "4", "Headline: 325-pair scatter, human r vs Qwen r, 13 reversals highlighted", "BUILT",
        ("d30b_profiles", "d30b_relationships", "d30b_fingerprints", "od_all_pairs", "od_screened"), "RECOMPUTED",
        "Qwen r and screen RECOMPUTED; human r CHECKED"),
    # Iteration 47: Figure 1.2 is the trait map (key "tmap"); the explorer (key "1.2") is shown as Figure 1.3.
    Fig("tmap", "1", "All 240 traits at their r with PC1 and PC2 or PC3 (model and vertical-axis menus), circles at r² = 1 and .5",
        "BUILT", ("traits_qwen", "traits_gemma", "traits_llama", "persona_pcs"), "RECOMPUTED",
        "trait-PC correlations computed in this notebook (as for Figure 1.1)"),
    Fig("1.2", "1", "Persona Landscape Explorer: persona PCs (PC1–PC6) and 240-trait profiles, three models", "BUILT",
        ("persona_pcs", "role_coords", "traits_qwen", "traits_llama", "traits_gemma", "pc_trait_qwen_ext", "pca_xmodel",
         "od_persona_class"), "RECOMPUTED", "z-scores, row matching and PC cross-check RECOMPUTED; default pair CHECKED"),
    # Iteration 32: Figure 6.1 (Discussion), Big Five domain correlations: people, GPT answers (external, published), activations.
    Fig("6.1", "6", "Correlation between Big Five domain scores, ten domain pairs: people (BBC, IPIP-NEO), GPT-3.5/GPT-4 persona answers (Petrov et al. 2024), Qwen/Gemma/Llama activations",
        "BUILT", ("d30b_relationships", "bf_strict_map", "traits_qwen", "traits_gemma", "traits_llama"), "RECOMPUTED",
        "our sources computed in this notebook; Petrov et al. values from their published file, SHA-256 checked"),
    # Iteration 33: Section 3 (SAPA trait-word bridge) and the Section 4 elicitation figures. Keys are internal; reader-facing
    # numbers come from report.DISPLAY_NUMBER (sapa1 -> 3.1, sapa2 -> 3.2, conv -> 4.1, qcloud -> 4.2).
    # 1 Foundations (skeleton)
    # Iteration 21: Figure 1.2 is the axis guide (characters on PC1-PC2 coloured by a trait, table for PC1-PC5); the
    # iteration 20 factor figure moved to Appendix E.4.
    Fig("1.1", "1", "Characters on a model's PC1 and PC2/PC3 coloured by one trait (model, axis and trait menus; trait list per model and axis), with a guide to PC1-PC5 for all three models",
        "BUILT", ("traits_qwen", "traits_gemma", "traits_llama", "persona_pcs", "pca_diag"), "RECOMPUTED",
        "trait-PC correlations computed in this notebook; explained variance and stability from the saved PCA diagnostics"),
    # Iteration 31: Figure 1.3 is the historical traits grouped by Big Five domain; the planned skeletons move to 1.4-1.6.
    Fig("1.3", "3", "42 Big Five traits and the five domain scores in people (SAPA proxies) and the three models: with one another, with the domain scores and with PC1-PC5, plus differences (Rows / Columns / Show menus; shown as Figure 3.1; absorbs former 3.2, sapa1)",
        "BUILT", ("bf_strict_map", "bf_domain_corr", "bf_sapa_corr", "bf_sapa_domains", "traits_qwen", "traits_gemma", "traits_llama", "persona_pcs"), "RECOMPUTED",
        "model trait r, block averages and trait-PC r computed in this notebook; people matrix read from the AA1 audit and sign-flipped here; domain-score r CHECKED against the saved study values"),
    Fig("1.4", "1", "Data and method pipeline schematic (personas, traits, vectors; Lu et al. 2026)", "SKELETON", ("lineage",), "HASH-ONLY", "diagram; provenance text only"),
    Fig("1.5", "1", "Persona activation PCA spectrum, PC1–PC6", "SKELETON", ("pca_spectrum",), "HASH-ONLY", "planned RECOMPUTED needs released vectors"),
    Fig("1.6", "1", "Cross-model PC correspondence", "SKELETON", ("pca_xmodel",), "HASH-ONLY", "input snapshotted for 1.2"),
    # 2 Model organization (skeleton)
    # Iteration 16: the activation-axes heatmap (was G.3) is Figure 2.1; the trait-pair density figure moved to G.1.
    Fig("elbow", "2", "Share of the variation among the 275 characters carried by PC1-PC5, three models (each component / cumulative menu)",
        "BUILT", ("pca_diag",), "CHECKED", "saved PCA diagnostics; cumulative sums recomputed"),
    Fig("2.1", "2", "Signed r between Qwen PC1-5 and Gemma / Llama PC1-5 (saved; menu, Qwen–Gemma first), plane canonical correlations",
        "BUILT", ("pca_xmodel", "persona_pcs"), "RECOMPUTED", "canonical correlations computed in this notebook"),
    Fig("2.2", "2", "Per-trait agreement of the 275 character scores between models (240 traits x 3 pairs; was G.2)", "BUILT",
        ("traits_qwen", "traits_llama", "traits_gemma", "aa18_traitconv", "aa18_pairwise", "greg_xmodel"), "RECOMPUTED",
        "computed in this notebook; equals AA18 saved per-trait values"),
    Fig("2.3", "2", "r between each model's AA18 consensus scores C1-C5 and its activation PC1-5 (model menu: Qwen, Gemma, Llama)",
        "BUILT", ("aa18_scores", "persona_pcs"), "RECOMPUTED", "computed in this notebook from saved AA18 scores and persona PCs"),
    # Planned figures renumbered in iterations 11, 17 and 18 (now 2.4-2.10) for the built 2.1-2.3.
    Fig("2.4", "2", "Qwen trait PCA T1–T5: explained variance", "SKELETON", ("tpca_var",), "HASH-ONLY"),
    Fig("2.5", "2", "T1–T5 vs activation PC1–PC6", "SKELETON", ("tpca_vs_pc",), "HASH-ONLY"),
    Fig("2.6", "2", "Strongest T loadings", "SKELETON", ("tpca_load",), "HASH-ONLY"),
    Fig("2.7", "2", "Qwen F Pearson trait poles", "SKELETON", ("fpearson",), "HASH-ONLY"),
    Fig("2.8", "2", "AA18 consensus C1–C5 and alignment with AA17", "SKELETON", ("aa18_load", "aa18_align"), "HASH-ONLY"),
    Fig("2.9", "2", "Cross-model factor congruence (PHG-CM01)", "SKELETON", ("cm01_matches",), "CHECKED", "two congruences checked in Section 5"),
    # 3 Human measurements (skeleton)
    Fig("3.6", "3", "Human 26-facet correlation matrix (30,000 reference respondents)", "SKELETON", ("d30b_relationships",), "CHECKED", "two saved sources agree; RECOMPUTED only with raw OSF data"),
    # Planned figures renumbered in iteration 9 (were 3.2-3.4); the built 3.2 moved to Appendix F as F.1 in iteration 10.
    # Iteration 20: built Figure 3.1, renumbered 3.2 in iteration 29 (Qwen facets vs C1-C5 / F1-F5 / PC1-PC5); the planned human matrix skeleton is now 3.6.
    Fig("3.2", "3", "Qwen's 26 facets vs consensus directions C1-C5 and activation PC1-PC5 (menu)", "BUILT",
        ("d30b_profiles", "aa18_scores", "persona_pcs", "fexp_geo", "fexp_var"), "RECOMPUTED",
        "C values reproduce the saved Oct 25 facet correlations; PC values computed in this notebook"),
    Fig("3.3", "3", "AA19 consensus component classification", "SKELETON", ("aa19_class",), "HASH-ONLY"),
    Fig("3.4", "3", "AA27 facet bridge coverage and failed gate", "SKELETON", ("aa27_cov", "aa27_gate"), "HASH-ONLY"),
    Fig("3.5", "3", "IPIP coverage information benchmark", "SKELETON", ("ipip_cov",), "HASH-ONLY"),
    # 4 Human correspondence (built)
    Fig("4.2", "4", "26×26 human vs Qwen matrices and domain averages, scenario prompts (ordinary-role checks in Appendix D)", "BUILT",
        ("d30b_profiles", "d30b_relationships", "od_persona_class", "od_composition"), "RECOMPUTED",
        "Qwen RECOMPUTED; human CHECKED"),
    Fig("4.3", "4", "Held-out R² per facet vs human-reference benchmark, two uncertainty families; left domain band", "BUILT",
        ("d30b_facet_results", "d30b_resp_int", "d30b_extr_int", "d30b_macro_resp", "d30b_macro_extr",
         "cal30_facets", "cal30_brief", "cal30_qint"), "CHECKED",
        "predictions/humans not in Git; macro values checked against report; after-rescaling row from facet_comparison.csv"),
    # Appendix F: comparison of the two prompt methods (F.1) and survey-style results as a table (F.2, iteration 15)
    Fig("F.1", "F", "Agreement between the two elicitation methods (scenario vs survey-style prompts), per facet (was 3.2)", "BUILT",
        ("d30b_profiles", "d30b_fingerprints", "d30b_facet_results", "cal30_facets"), "RECOMPUTED",
        "per-facet and pair agreement recomputed from saved profiles; outline values checked"),
    # Iteration 15: Figures F.2-F.4 (survey-style redraws of Figures 4.1, 4.2 and 4.3) replaced by one table linking to them.
    Fig("F.2", "F", "Survey-style results alongside the main text (table; links to Figures 4.1, 4.2, 4.3; pairs and per-facet R² in details)",
        "BUILT", ("d30b_profiles", "d30b_relationships", "d30b_fingerprints", "od_all_pairs", "d30b_facet_results",
                  "d30b_resp_int", "d30b_extr_int", "cal30_facets", "cal30_qint"), "RECOMPUTED",
        "pattern r, sign share and spread ratio recomputed; R² and multipliers checked against the calibration package"),
    # Appendix G: how the models were compared (iteration 14)
    Fig("G.1", "G", "Trait correlations compared between models: 28,680 historical trait pairs, density shading (was Figure 2.1)",
        "BUILT", ("traits_qwen", "traits_llama", "traits_gemma", "pca_xmodel"), "RECOMPUTED",
        "rank-normal scoring as in e01cacb; agreement reproduces the reported .733/.868/.840"),
    Fig("G.3b", "G", "Characters on Qwen PC1 vs Gemma / Llama PC1 (Figure 2.2 candidate)", "BUILT",
        ("persona_pcs", "pca_xmodel"), "CHECKED"),
    Fig("G.4", "G", "AA17 factor-to-factor congruence per model pair, matched pairs outlined (PHG-CM01)", "BUILT",
        ("cm01_matches",), "CHECKED", "equals AA17 cross_model_factor_alignment.csv (not snapshotted)"),
    Fig("G.5", "G", "AA18 consensus directions C1-C5 with AA19 human status (table)", "BUILT",
        ("aa18_diag", "aa19_comp"), "CHECKED"),
    Fig("G.6", "G", "Beyond personas: Oct 9 local semantic geometry, Llama-3.1-8B vs Gemma-2-2B (text)", "BUILT",
        ("lgeo_results",), "CHECKED"),
    Fig("E.1", "E", "Technical exploration: calibration slider (earlier nine-facet Direct-12 experiment; illustrative, post hoc)", "BUILT",
        ("cal12_test", "cal12_mult", "cal12_curve"), "RECOMPUTED", "R²(k) recomputed exactly from saved SSE; curve checked"),
    Fig("E.2", "E", "How well each facet fits its domain (mean same-domain correlation; people, Qwen scenario, Qwen survey)", "BUILT",
        ("d30b_relationships",), "RECOMPUTED", "recomputed via an independent path; five values checked against supplied expectations"),
    Fig("E.4", "E", "Each model's AA17 factors vs its activation PC1-6 (model menu), key to Qwen's factors; tables: Qwen F vs C1-C5, Qwen facets vs F1-F5 (was Figure 1.2 in iteration 20)",
        "BUILT", ("aa17_scores", "persona_pcs", "fexp_poles", "aa18_scores", "fexp_geo", "fexp_var", "d30b_profiles"), "RECOMPUTED",
        "factor-PC and factor-C values computed in this notebook; facet-F values equal the saved Oct 26 results"),
    Fig("E.3", "E", "Facet-specific rescaling (exploratory table; one multiplier per facet)", "BUILT",
        ("cal30_facets",), "CHECKED", "table only; as-measured values checked against Direct-30 B"),
    # 5 Investigating discrepancies (built)
    Fig("5a", "5", "Friendliness–Anger leave-one-out and group-exclusion influence", "BUILT",
        ("d30b_profiles", "od_loo", "od_persona_class", "od_composition", "od_conditions"), "RECOMPUTED"),
    Fig("5b", "5", "E1 vs N2 persona scatter coloured by Formal; raw / conditioned toggle", "BUILT",
        ("d30b_profiles", "hist_styles48", "od_composition", "od_style_var"), "RECOMPUTED"),
    Fig("5c", "5", "C/T/F projected vs residual contributions, 13 reversals", "BUILT", ("ctgeo_pairs", "fexp_pairs"), "CHECKED",
        "additivity checked; Qwen r RECOMPUTED"),
    Fig("5d.1", "5", "E1 and N2 item wording", "BUILT", ("od_items",), "CHECKED"),
    Fig("5d.2", "5", "Anger items vs Friendliness and Assertiveness", "BUILT", ("ha_items", "ha_facets"), "CHECKED",
        "human aggregates; RECOMPUTED needs raw OSF data"),
    Fig("5d.3", "5", "Friendliness by Anger band", "BUILT", ("ha_bins",), "CHECKED", "internal nesting consistency checked"),
    Fig("5e.1", "5", "Cross-model historical relationships, raw and style-conditioned", "BUILT", ("cross_primary",), "CHECKED"),
    Fig("5e.2", "5", "PHG-CM01 focal relationship table", "BUILT", ("cm01_pairs",), "CHECKED"),
    Fig("5e.3", "5", "Qwen F1 vs Llama F1 / Gemma F3 trait-association patterns", "BUILT", ("cm01_all240", "cm01_matches"), "CHECKED"),
    # 6 Conclusions (skeleton)
    Fig("6.1", "6", "Direct vs historical facet agreement", "SKELETON", ("d26_agree",), "HASH-ONLY"),
    Fig("6.2", "6", "Historical substitution calibration (six targets)", "SKELETON", ("calsub_eval",), "HASH-ONLY"),
    Fig("6.3", "6", "E1 steering confirmation outcome", "SKELETON", ("steer_arms", "steer_cmp"), "HASH-ONLY"),
    Fig("6.4", "6", "IPIP questionnaire execution outcome", "SKELETON", ("ipipq_brief",), "HASH-ONLY"),
    Fig("6.5", "6", "Open-questions table", "SKELETON", ("tool01_readme",), "HASH-ONLY", "interaction-pattern reference"),
]

GAPS = [
    "Human-side values (325 human r, item analysis, band means) are CHECKED, not RECOMPUTED: OSF downloads are blocked by this session's network policy (HTTP 403 at the proxy). REPRODUCTION mode recomputes them once `research/notebooks/download_ipip.py` has fetched IPIP300.dat with a matching AA27 SHA-256; that path is unit-tested only on synthetic fixtures.",
    "Calibration slider uses Direct-12 (nine facets, 3aa4659). No saved 26-facet Direct-30 B calibration sweep exists; the historical-substitution study (22ab297) has calibrated direct R² for six targets only.",
    "Held-out R² (4.3) cannot be recomputed: individual predictions and test respondents are deliberately outside Git.",
    "No pair-specific extraction (question-resampling) uncertainty exists for facet-pair correlations; only persona and respondent bootstraps (outlier study).",
    "Five alternative weightings and global drop-5/drop-10 influence sets are saved (outlier study) but not shown or recomputed here; frozen weights live in the bank-dependence study (bc82e07) and were not snapshotted.",
    "Historical three-model trait banks were not snapshotted, so cross-model (5.d1, 5.d2) values are CHECKED against reports, not RECOMPUTED.",
    "C/T/F projections (5.0) are CHECKED for additivity; the projections themselves need factor/component scores not in the snapshot.",
    "Direct Llama/Gemma IPIP measurements do not exist; historical proxies are not substitutes.",
    "Pins not supplied for three branches (direct-vs-historical, both calibration branches); branch tips c8f661e, 3aa4659, 22ab297 were used and recorded.",
    "Style readouts come from 40f1654 (direct12 historical-library diagnostic), a dependency of the outlier study not named in the task list.",
    "Sections 1–3 and 6 are skeletons: sources inventoried and hash-checked only.",
]


def source_rows() -> pd.DataFrame:
    rows = []
    allsrc = {**S.SOURCES, **S.PLANNED}
    for f in FIGURES:
        for k in f.sources:
            src = allsrc[k]
            avail = S.evidence_available(src.commit, src.path)
            blob = S.evidence_bytes(src.commit, src.path) if avail else b""
            rows.append(dict(
                figure=f.id, section=f.section, title=f.title, status=f.status, tier=f.tier, tier_note=f.tier_note,
                source_key=k, commit=S.full_commit(src.commit) if avail else src.commit, branch=S.COMMITS[src.commit_key][1],
                path=src.path, bytes=len(blob) if avail else None, sha256=S.evidence_record(src.commit, src.path)["source_sha256"] if avail else None,
                package_path=S.evidence_record(src.commit, src.path)["package_path"] if avail else "",
                snapshot=("subset" if src.subset else "copy") if k in S.SOURCES else "not snapshotted",
            ))
    return pd.DataFrame(rows)


def write(out_dir: Path) -> pd.DataFrame:
    df = source_rows()
    df.to_csv(out_dir / "INVENTORY.csv", index=False, lineterminator="\n")
    lines = ["# PHG report notebook: figure and source inventory", "",
             "Every planned figure, the pinned commit and path it reads, the source file size and SHA-256, and the verification tier.",
             "Tiers: **RECOMPUTED** (independently recalculated here), **CHECKED** (compared with a saved result), "
             "**HASH-ONLY** (source integrity only). Machine-readable copy: [INVENTORY.csv](INVENTORY.csv). "
             "Generated by `python research/notebooks/build_inventory.py`.", ""]
    for sec, title in [("1", "The persona landscape"),
                       ("2", "The three models arrange traits in largely the same way"),
                       ("3", "Measuring 26 personality facets inside Qwen"),
                       ("4", "Qwen's personality structure: partial resemblance, systematic differences"),
                       ("5", "Case study: why do Friendliness and Anger go together in Qwen?"),
                       ("6", "Discussion (planned figures)"), ("E", "Appendix E: technical explorations"),
                       ("F", "Appendix F: survey-style prompt results"), ("G", "Appendix G: how the models were compared")]:
        lines += [f"## {sec} {title}", "", "| Figure | Status | Tier | Commit | Path | Bytes | SHA-256 (12) |", "|---|---|---|---|---|---:|---|"]
        for r in df[df.section == sec].itertuples():
            note = f" ({r.tier_note})" if r.tier_note else ""
            lines.append(f"| {r.figure} {r.title} | {r.status} | {r.tier}{note} | `{str(r.commit)[:7]}` | `{r.path}` | "
                         f"{'' if pd.isna(r.bytes) else format(int(r.bytes), ',')} | `{'' if pd.isna(r.sha256) else r.sha256[:12]}` |")
        lines.append("")
    lines += ["## Gaps", ""] + [f"- {g}" for g in GAPS] + [""]
    (out_dir / "INVENTORY.md").write_text("\n".join(lines))
    return df

"""Pinned provenance registry and hash-checked packaged input loading.

Every input retains its original research commit and path. Runtime access is
exclusively through provenance/evidence_registry.json and packaged files.
Snapshot re-derivation checks packaged evidence, not a research Git object store. Subset files keep only the
rows/columns listed in their rule; the rule and the source blob hash are kept
so the subset can be re-derived and checked.

Nothing here writes into ``research/outputs/``; frozen results stay untouched.
"""
from __future__ import annotations

import hashlib
import io
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = ROOT / "data" / "saved"
MANIFEST = SNAPSHOT_DIR / "snapshot_manifest.json"

# Pinned commits supplied with the task. Branch names are kept for provenance.
COMMITS = {
    "main_hist": ("65da790", "main"),
    "d30b": ("bf99d3d", "codex/direct30-b-gpu-records-20261016"),
    "d26hist": ("c8f661e", "codex/direct26-historical-comprehensive-20261019 (branch tip)"),
    "outlier": ("c556609", "codex/trait-correlation-outlier-diagnostics-20261019"),
    "bank": ("bc82e07", "codex/qwen-persona-bank-dependence-20261015"),
    "cross": ("e01cacb", "codex/cross-model-trait-relationships-20261015"),
    "cm01": ("cc4ef37", "codex/phg-cm01-cross-model-factors"),
    "lgeo": ("fe3a307", "codex/cross-model-local-geometry-execution-20261008"),
    "ctgeo": ("1ea36c7", "C/T geometry (ipip-consensus-geometry)"),
    "fexp": ("fc764f8", "F explanation (ipip-aa17-factor-explanation)"),
    "tpca": ("6368af7", "Qwen trait PCA T1-T5"),
    "fpearson": ("8eb8548", "AA17 Pearson F chart"),
    "anger": ("51cdecc", "codex/human-anger-friendliness-20261026"),
    "cal12": ("3aa4659", "codex/direct12-strength-calibration-20261015 (branch tip)"),
    "calsub": ("22ab297", "codex/historical-trait-substitution-calibration-20261021 (branch tip)"),
    "steer": ("8bf7cb6", "E1 steering confirmation"),
    "ipipq": ("0013a4d", "IPIP questionnaire execution"),
    "tool01": ("5fd7b95", "codex/phg-tool01-correlation-explorer"),
    # Style readouts used by the outlier study (its HISTCOM), not separately
    # listed in the task; recorded so the dependency is visible.
    "cal30": ("677d4f2", "codex/direct30-calibration-20261102"),
    "histlib": ("40f1654", "direct12 historical-library diagnostic (outlier-study dependency)"),
    # Lu et al. lineage note lives on current main only.
    "main_now": ("8b65f26", "main (current tip, documentation only)"),
    "conv": ("598857c", "codex/facet-convergence-geometry-20261106"),
}

D30 = "research/outputs/direct30_b_gpu_execution_20261016"
D30C = D30 + "/combined_human_profiles"
OD = "research/outputs/trait_correlation_outlier_diagnostics_20261019"
CAL12 = "research/outputs/direct12_strength_calibration_20261015"
HA = "research/outputs/human_anger_friendliness_20261026"
CONV = "research/outputs/facet_convergence_geometry_20261106/results"
CM01 = "research/outputs/phg_cm01_cross_model_factors_20261027"
CROSS = "research/outputs/cross_model_trait_relationships_20261015"
HIST = "research/outputs/direct12_historical_library_diagnostic_20261015"

STYLES = ["formal", "animated", "verbose", "technical", "methodical"]

def _subset_styles(df: pd.DataFrame) -> pd.DataFrame:
    return df[["persona"] + ["historical_" + s for s in STYLES]]


def _subset_screened(df: pd.DataFrame, screened: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    pairs = set(screened["pair"]) if screened is not None else None
    if pairs is None:
        raise ValueError("screened pairs required")
    return df[df["pair"].isin(pairs)]


FOCAL_HIST_PAIRS = {
    ("avoidant", "hostile"), ("charismatic", "hostile"), ("flirty", "hostile"),
    ("nurturing", "hostile"), ("adventurous", "avoidant"), ("charismatic", "gregarious"),
    ("benevolent", "hostile"),
}


def _subset_cm01_pairs(df: pd.DataFrame) -> pd.DataFrame:
    keep = [((a, b) in FOCAL_HIST_PAIRS) or ((b, a) in FOCAL_HIST_PAIRS)
            for a, b in zip(df["trait_a"], df["trait_b"])]
    return df[keep]


PC_KEEP = 6  # saved scores go to PC10; the explorer offers PC1-PC6


def persona_pcs_from_viewer_json(raw: bytes) -> pd.DataFrame:
    """Saved model-local persona PCA scores (extended_persona_pca/viewer_data.json) as a table."""
    d = json.loads(raw)
    rows = []
    for m, v in d["models"].items():
        for p in v["points"]:
            rows.append(dict(model=m, persona=p["persona"], **{f"pc{k + 1}": p["coordinates"][k] for k in range(PC_KEEP)}))
    return pd.DataFrame(rows)


def pca_diagnostics_from_viewer_json(raw: bytes) -> pd.DataFrame:
    """Saved per-component PCA diagnostics (explained variance, bootstrap loading stability), three models, PC1-PC10."""
    d = json.loads(raw)
    keep = ["component", "explained_variance_ratio", "cumulative_explained_variance", "bootstrap_median_loading_cosine",
            "bootstrap_loading_cosine_q05"]
    return pd.DataFrame([dict(model=m, **{k: r[k] for k in keep}) for m, v in d["models"].items() for r in v["diagnostics"]])


def _subset_aa18_scores(df: pd.DataFrame) -> pd.DataFrame:
    """AA18 per-persona scores, components C1-C5 only (the supported consensus axes)."""
    return df[df.component.isin(["C1", "C2", "C3", "C4", "C5"])].reset_index(drop=True)


def _subset_aa18_loadings(df: pd.DataFrame) -> pd.DataFrame:
    """AA18 consensus trait loadings, components C1-C5 only."""
    return df[df.component.isin(["C1", "C2", "C3", "C4", "C5"])].reset_index(drop=True)


def _subset_cross_primary(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["condition"].isin(["uniform", "condition_formal", "condition_core5"])]


@dataclass(frozen=True)
class Source:
    key: str
    commit_key: str
    path: str
    description: str
    subset: Optional[str] = None  # name of a subset rule in SUBSETS
    subset_rule: str = ""  # human-readable rule

    @property
    def commit(self) -> str:
        return COMMITS[self.commit_key][0]

    @property
    def local_name(self) -> str:
        name = Path(self.path).name
        if self.subset:
            stem, ext = name.rsplit(".", 1)
            ext = "csv" if self.subset in ("persona_pcs", "pca_diag") else ext  # JSON source, CSV subset
            name = f"{stem}__subset.{ext}"
        return f"{self.key}__{name}"

    @property
    def local_path(self) -> Path:
        return SNAPSHOT_DIR / self.local_name


SUBSETS: dict[str, Callable[..., pd.DataFrame]] = {
    "styles": _subset_styles,
    "screened": _subset_screened,
    "cm01_pairs": _subset_cm01_pairs,
    "cross_primary": _subset_cross_primary,
    "aa18_scores": _subset_aa18_scores,
    "aa18_loadings": _subset_aa18_loadings,
}

_S = Source
SOURCES: dict[str, Source] = {s.key: s for s in [
    # Direct-30 B (26 facets, human comparison)
    _S("d30b_profiles", "d30b", D30C + "/model_persona_profiles.csv", "Qwen 275 persona x 26 facet rank-normal scores, scenario and survey"),
    _S("d30b_relationships", "d30b", D30C + "/relationships.csv", "325 facet-pair correlations, frozen human reference and Qwen, per format"),
    _S("d30b_fingerprints", "d30b", D30C + "/relationship_fingerprints.csv", "Agreement of 325-pair fingerprints"),
    _S("d30b_facet_results", "d30b", D30C + "/facet_results.csv", "Held-out R2/S per facet, model and human-reference"),
    _S("d30b_resp_int", "d30b", D30C + "/respondent_intervals.csv", "Respondent-resampling intervals (fits fixed)"),
    _S("d30b_extr_int", "d30b", D30C + "/extraction_intervals.csv", "Question-resampling (extraction) intervals"),
    _S("d30b_macro_resp", "d30b", D30C + "/macro_respondent_family_intervals.csv", "Macro R2 respondent-family interval"),
    _S("d30b_macro_extr", "d30b", D30C + "/macro_extraction_family_intervals.csv", "Macro R2 question-family interval"),
    _S("d30b_point_stage", "d30b", D30C + "/POINT_ESTIMATE_STAGE.json", "Facet list and frozen split hashes"),
    # Outlier / reversal diagnostics
    _S("od_screened", "outlier", OD + "/screened_pair_groups.csv", "13 frozen reversals and 6 close agreements"),
    _S("od_all_pairs", "outlier", OD + "/results/all_pair_discrepancies.csv", "All 325 pairs ranked by discrepancy, with names"),
    _S("od_corr_unc", "outlier", OD + "/results/correlation_uncertainty.csv", "Marginal intervals and simultaneous bands"),
    _S("od_loo", "outlier", OD + "/results/leave_one_out_summary.csv", "Single-persona deletion extrema"),
    _S("od_conditions", "outlier", OD + "/results/condition_summary.csv", "Composition/style condition definitions"),
    _S("od_composition", "outlier", OD + "/results/composition_style_sensitivity.csv",
       "Condition results for screened pairs", subset="screened",
       subset_rule="rows whose pair is in od_screened (19 pairs)"),
    _S("od_style_var", "outlier", OD + "/results/style_variance_removed.csv", "Variance removed by style conditioning"),
    _S("od_persona_class", "outlier", OD + "/persona_classification.csv", "Authored definitions and frozen analytical groups"),
    _S("od_items", "outlier", OD + "/facet_item_inventory.csv", "IPIP-NEO-300 item wording and keys"),
    # Style readouts (historical library)
    _S("hist_styles48", "histlib", HIST + "/results/model_readouts_48.csv", "Historical Formal/Animated/Verbose/Technical/Methodical readouts",
       subset="styles", subset_rule="columns persona + historical_{formal,animated,verbose,technical,methodical}"),
    # Calibration (Direct-12, nine facets)
    _S("cal12_test", "cal12", CAL12 + "/results/test_results.csv", "Direct-12 test SSE/SST by condition"),
    _S("cal12_mult", "cal12", CAL12 + "/results/multipliers.csv", "Calibration-fitted multipliers"),
    _S("cal12_curve", "cal12", CAL12 + "/results/sensitivity_curve.csv", "Illustrative macro R2 by multiplier"),
    # Human Anger-Friendliness item study
    _S("ha_items", "anger", HA + "/results/item_correlations.csv", "Anger item correlations with E1 and E3"),
    _S("ha_bins", "anger", HA + "/results/anger_bins.csv", "Friendliness means by Anger band"),
    _S("ha_facets", "anger", HA + "/results/facet_correlations.csv", "N2-E1 and N2-E3 facet correlations"),
    # Cross-model
    _S("cross_primary", "cross", CROSS + "/primary_correlation_summary.csv", "Historical cross-model relationships, raw and style-conditioned",
       subset="cross_primary", subset_rule="condition in {uniform, condition_formal, condition_core5}"),
    _S("cm01_pairs", "cm01", CM01 + "/results/selected_trait_pair_correlations.csv", "PHG-CM01 original-cosine focal pair correlations",
       subset="cm01_pairs", subset_rule="focal historical trait pairs listed in FOCAL_HIST_PAIRS"),
    _S("cm01_all240", "cm01", CM01 + "/results/all240_factor_associations.csv", "240-trait x factor associations, three models"),
    _S("cm01_matches", "cm01", CM01 + "/results/factor_matches.csv", "Cross-model factor congruence"),
    # F / C / T decomposition
    _S("fexp_pairs", "fexp", "research/outputs/ipip_aa17_factor_explanation_20261026/results/highlighted_pair_explanation.csv", "F projected/residual contributions, screened pairs"),
    # Direct-30 B rescaling (iteration 7): aggregates only
    _S("cal30_facets", "cal30", "research/outputs/direct30_calibration_20261102/results/facet_comparison.csv",
       "Per-facet as-measured, common-rescaled and facet-specific (exploratory) R² with respondent intervals"),
    _S("cal30_brief", "cal30", "research/outputs/direct30_calibration_20261102/DECISION_BRIEF.md",
       "Direct-30 B rescaling decision brief (macro values, multipliers, intervals)"),
    _S("cal30_qint", "cal30", "research/outputs/direct30_calibration_20261102/questions/question_intervals.csv",
       "Per-facet and macro question-resampling (95%) intervals, as measured and rescaled"),
    # Persona Landscape Explorer (Section 1)
    _S("persona_pcs", "main_hist", "research/outputs/extended_persona_pca/viewer_data.json",
       "Saved model-local persona PCA scores, three models", subset="persona_pcs",
       subset_rule="JSON models.*.points -> model, persona, pc1..pc6 (of the saved PC1-PC10)"),
    _S("role_coords", "main_hist", "research/outputs/model_coverage_terrain_viewer/role_coordinates.csv",
       "Native PC1-PC3 per model (terrain viewer), cross-check for persona_pcs"),
    _S("traits_qwen", "main_hist", "research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv",
       "Qwen 275 x 240 historical trait cosine scores (AA17 audit 723d42415fe3)"),
    _S("traits_llama", "main_hist", "research/outputs/multimodel_trait_profile_pc_predictor/llama/persona_trait_similarity_matrix.csv",
       "Llama 275 x 240 historical trait cosine scores (AA17 audit 74b2cb886967)"),
    _S("traits_gemma", "main_hist", "research/outputs/multimodel_trait_profile_pc_predictor/gemma/persona_trait_similarity_matrix.csv",
       "Gemma 275 x 240 historical trait cosine scores (AA17 audit 798c0618b9e4)"),
    _S("pc_trait_qwen_ext", "main_hist", "research/outputs/extended_persona_pca/qwen_extended_pc_trait_associations.csv",
       "Saved Qwen PC4-PC13 x 240-trait Pearson associations (only saved full association table)"),
    _S("pca_xmodel", "main_hist", "research/outputs/extended_persona_pca/cross_model_pc_score_correspondence.csv",
       "Saved cross-model persona PC score correlations"),
    _S("ctgeo_pairs", "ctgeo", "research/outputs/ipip_consensus_geometry_20261025/results/screened_pair_decomposition.csv", "C and T projected/residual contributions, screened pairs"),
    # Appendix G: cross-model comparisons (iteration 14). AA17 cross_model_factor_alignment.csv is not added: its 96
    # Tucker congruences equal cm01_matches (original_pattern) to 1e-16.
    _S("aa18_diag", "main_hist", "research/outputs/aa18_three_model_consensus_trait_structure/shared_dimension_diagnostics.csv",
       "AA18 shared dimensions: projector eigenvalue (of 3 models), held-out agreement, supported consensus axes C1-C5"),
    _S("aa18_pairwise", "main_hist", "research/outputs/aa18_three_model_consensus_trait_structure/pairwise_model_agreement.csv",
       "AA18 pairwise model agreement (median per-trait and per-persona profile correlations)"),
    _S("aa18_traitconv", "main_hist", "research/outputs/aa18_three_model_consensus_trait_structure/trait_profile_convergence.csv",
       "AA18 per-trait cross-model correlation of the 275 persona scores (aggregate, one row per trait)"),
    # Iteration 18: Figure 2.3 (consensus directions C1-C5 vs each model's activation PCs).
    _S("aa18_scores", "main_hist", "research/outputs/aa18_three_model_consensus_trait_structure/shared_persona_scores.csv",
       "AA18 per-persona scores on the consensus directions (consensus and each model), C1-C5", subset="aa18_scores",
       subset_rule="component in {C1..C5}"),
    # Iteration 19: key to the consensus directions (trait poles), shown with Figure 2.3.
    _S("aa18_loadings", "main_hist", "research/outputs/aa18_three_model_consensus_trait_structure/consensus_trait_loadings.csv",
       "AA18 consensus trait loadings (240 traits), C1-C5", subset="aa18_loadings", subset_rule="component in {C1..C5}"),
    # Iteration 21: Figure 1.2 lead (explained variance and stability of the persona PCs).
    _S("pca_diag", "main_hist", "research/outputs/extended_persona_pca/viewer_data.json",
       "Saved per-component persona PCA diagnostics (explained variance, bootstrap loading stability), three models",
       subset="pca_diag", subset_rule="models.*.diagnostics: component, explained variance, bootstrap loading cosines"),
    # Iteration 20: Figure 2.4 (each model's AA17 factors vs C1-C5) and Figure 3.1 (Qwen facets vs C, F and PC).
    _S("aa17_scores", "main_hist", "research/outputs/aa17_three_model_trait_factor/persona_factor_scores.csv",
       "AA17 per-persona factor scores, three models (Qwen F1-F5; Llama, Gemma F1-F6)"),
    _S("fexp_poles", "fexp", "research/outputs/ipip_aa17_factor_explanation_20261026/results/historical_factor_poles.csv",
       "Qwen AA17 factors: top-3 historical traits at each pole (ordinary Pearson r over 275 personas)"),
    _S("fexp_geo", "fexp", "research/outputs/ipip_aa17_factor_explanation_20261026/results/facet_geometry_correlations.csv",
       "Qwen facet x C1-C5 / T1-T5 / F1-F5 Pearson r, both prompt formats (Oct 25-26 studies)"),
    _S("fexp_var", "fexp", "research/outputs/ipip_aa17_factor_explanation_20261026/results/facet_variance_explained.csv",
       "Qwen facet variance explained by C1-C5 / T1-T5 / F1-F5, both prompt formats"),
    # Iteration 31: Figure 1.3 (the historical traits grouped by Big Five domain). The mapping was frozen geometry-blind
    # at 636c5c1d (Sept 11) before any geometry analysis; the saved domain intercorrelations are the cross-check.
    _S("bf_strict_map", "main_hist", "research/outputs/externally_anchored_big_five/human_anchored_strict_trait_mapping.csv",
       "Human-anchored strict Big Five mapping: 42 historical traits, IPIP-NEO domain, facet and polarity (frozen geometry-blind)"),
    _S("bf_domain_corr", "main_hist", "research/outputs/externally_anchored_big_five/big_five_domain_intercorrelations.csv",
       "Saved Big Five domain-score intercorrelations across the 275 personas, three models, four constructions"),
    # Iteration 32 (side preview, not in the report body): human SAPA trait-proxy correlations for Figure 1.3's traits.
    _S("bf_sapa_corr", "main_hist", "research/outputs/sapa_bridge_psychometric_audit/human_trait_proxy_correlation_matrix.csv",
       "SAPA V5 pairwise-complete Pearson r between the 45 ACCEPT_DIRECT trait proxies (oriented items; AA1, retained by AA26)"),
    _S("bf_sapa_domains", "main_hist", "research/outputs/sapa_bridge_psychometric_audit/retained_traits_vs_human_big_five.csv",
       "SAPA V5: each bridge trait proxy vs official IPIP100 Big Five domain scales (part-whole corrected Pearson r)"),
    # Iteration 33: Section 4 elicitation (stopping points and question directions; Codex study 598857c).
    _S("conv_final", "conv", CONV + "/final_question_counts.csv", "Per facet and format: accepted stopping n, status, available questions"),
    _S("conv_hist", "conv", CONV + "/stopping_histories.csv", "All 252 scheduled checkpoints: bootstrap p05 cosine, cosine to previous, pass"),
    _S("conv_q", "conv", CONV + "/question_directions_pc123.csv", "2,119 saved question contrast directions: cosines with block-48 PC1-PC3 (PC1-48..)"),
    _S("conv_mean", "conv", CONV + "/running_mean_pc123.csv", "Running and final mean contrast directions on PC1-48..PC3-48"),
    _S("conv_pcv", "conv", CONV + "/pc48_viewer_correlations.csv", "Block-48 PCs vs the all-layer viewer PCs across 275 personas"),
    _S("conv_var", "conv", CONV + "/pc48_explained_variance.csv", "Block-48 persona PCA explained variance, PC1-48..PC5-48"),
    _S("aa19_comp", "main_hist", "research/outputs/aa19_human_consensus_factor_validation/component_classification.csv",
       "AA19 classification of consensus components C1-C5 against human factors"),
    _S("greg_xmodel", "main_hist", "research/outputs/gregarious_structure_20260924/results/cross_model_gregarious.csv",
       "Sept 24 Gregariousness follow-up: cross-model agreement of the gregarious indicator's persona means (.655-.825)"),
    _S("lgeo_results", "lgeo", "research/outputs/cross_model_local_geometry_execution_20261009/results/results.json",
       "Oct 9 local semantic geometry (Llama-3.1-8B vs Gemma-2-2B, 640 texts): summary results incl. primary rho"),
]}

# Sources for skeleton sections (inventoried, not snapshotted yet).
PLANNED: dict[str, Source] = {s.key: s for s in [
    _S("pca_spectrum", "main_hist", "research/outputs/extended_persona_pca/full_pca_spectrum.csv", "Persona activation PCA spectrum (PC1-PC6)"),
    _S("lineage", "main_now", "research/literature/20261026_assistant_axis_lineage.md", "Lu et al. (2026) lineage and citation guide"),
    _S("tpca_var", "tpca", "research/outputs/qwen_trait_pca_20261025/explained_variance.csv", "Qwen T1-T5 explained variance"),
    _S("tpca_vs_pc", "tpca", "research/outputs/qwen_trait_pca_20261025/trait_pcs_vs_activation_pcs.csv", "T vs activation PC correlations"),
    _S("tpca_load", "tpca", "research/outputs/qwen_trait_pca_20261025/strongest_trait_loadings.csv", "Strongest T loadings"),
    _S("aa17_load", "main_hist", "research/outputs/aa17_three_model_trait_factor/factor_loadings_rotated.csv", "AA17 rotated loadings F1-F5/F6"),
    _S("aa17_fcorr", "main_hist", "research/outputs/aa17_three_model_trait_factor/factor_correlations.csv", "AA17 factor intercorrelations"),
    _S("fpearson", "fpearson", "research/outputs/aa17_factor_pearson_poles_20261026/selected_correlations.csv", "Qwen F Pearson trait poles"),
    _S("aa18_load", "main_hist", "research/outputs/aa18_three_model_consensus_trait_structure/consensus_trait_loadings.csv", "AA18 C1-C5 loadings"),
    _S("aa18_align", "main_hist", "research/outputs/aa18_three_model_consensus_trait_structure/aa17_factor_alignment.csv", "AA18 vs AA17 alignment"),
    _S("aa19_class", "main_hist", "research/outputs/aa19_human_consensus_factor_validation/component_classification.csv", "AA19 component classification"),
    _S("aa27_cov", "main_hist", "research/outputs/aa27_ipip_neo_profile_plausibility/facet_bridge_coverage.csv", "AA27 facet bridge coverage"),
    _S("aa27_gate", "main_hist", "research/outputs/aa27_ipip_neo_profile_plausibility/bridge_validity_gate.json", "AA27 failed bridge gate"),
    _S("ipip_cov", "main_hist", "research/outputs/ipip_bridge_coverage_20260924/results/geometry_diagnostics.csv", "IPIP coverage benchmark"),
    _S("d26_agree", "d26hist", "research/outputs/direct26_historical_comprehensive_20261019/facet_agreement_summary.csv", "Direct vs historical facet agreement"),
    _S("calsub_eval", "calsub", "research/outputs/historical_trait_substitution_calibration_20261021/evaluation/evaluation_results.csv", "Historical substitution calibration results"),
    _S("steer_arms", "steer", "research/outputs/e1_steering_confirmation_execution_20261009/results/arm_summary.csv", "E1 steering confirmation arms"),
    _S("steer_cmp", "steer", "research/outputs/e1_steering_confirmation_execution_20261009/results/comparison_summary.csv", "E1 steering comparisons"),
    _S("ipipq_brief", "ipipq", "research/outputs/ipip_questionnaire_execution_20261024/run_records/ipip-qwen32b-20261024-primary/final-review/DECISION_BRIEF.md", "IPIP questionnaire decision brief"),
    _S("tool01_readme", "tool01", "web/phg-tool01/README.md", "PHG-TOOL01 interaction conventions"),
]}


# ---------------------------------------------------------------- packaged evidence access
EVIDENCE_REGISTRY = ROOT / "provenance" / "evidence_registry.json"

def evidence_record(commit: str, path: str) -> dict:
    rows = json.loads(EVIDENCE_REGISTRY.read_text())
    found = [r for r in rows if r["origin_commit"].startswith(commit) and r["origin_path"] == path]
    if len(found) != 1:
        raise FileNotFoundError(f"Packaged evidence unavailable: {commit}:{path}; see EXCLUSIONS.csv")
    return found[0]

def full_commit(short: str) -> str:
    matches = {r["origin_commit"] for r in json.loads(EVIDENCE_REGISTRY.read_text()) if r["origin_commit"].startswith(short)}
    if len(matches) != 1: raise ValueError(f"Origin commit unavailable or ambiguous: {short}")
    return matches.pop()

def evidence_bytes(commit: str, path: str) -> bytes:
    r = evidence_record(commit, path)
    data = (ROOT / r["package_path"]).read_bytes()
    if sha256(data) != r["package_sha256"]: raise ValueError(f"Packaged evidence hash mismatch: {r['package_path']}")
    return data

def evidence_available(commit: str, path: str) -> bool:
    try: evidence_bytes(commit, path); return True
    except FileNotFoundError: return False


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _derive(src: Source, raw: bytes) -> bytes:
    """Return the bytes stored locally: exact copy, or a deterministic subset."""
    if not src.subset:
        return raw
    if src.subset == "persona_pcs":
        out = persona_pcs_from_viewer_json(raw)
        return out.to_csv(index=False, lineterminator="\n").encode()  # full precision
    if src.subset == "pca_diag":
        return pca_diagnostics_from_viewer_json(raw).to_csv(index=False, lineterminator="\n").encode()
    df = pd.read_csv(io.BytesIO(raw), keep_default_na=False, dtype=str)
    kwargs = {}
    if src.subset == "screened":
        screened = pd.read_csv(io.BytesIO(evidence_bytes(SOURCES["od_screened"].commit, SOURCES["od_screened"].path)), dtype=str)
        kwargs["screened"] = screened
    out = SUBSETS[src.subset](df, **kwargs)
    return out.to_csv(index=False, lineterminator="\n").encode()


def build_snapshot(sources: Optional[dict[str, Source]] = None) -> dict:
    sources = sources or SOURCES
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for src in sources.values():
        raw = evidence_bytes(src.commit, src.path)
        local = _derive(src, raw)
        src.local_path.write_bytes(local)
        rows.append(dict(
            key=src.key, commit=full_commit(src.commit), branch=COMMITS[src.commit_key][1], path=src.path,
            source_bytes=evidence_record(src.commit, src.path).get("source_bytes", len(raw)), source_sha256=evidence_record(src.commit, src.path)["source_sha256"], local_file=src.local_name,
            packaged_source_sha256=sha256(raw),
            local_bytes=len(local), local_sha256=sha256(local), mode="subset" if src.subset else "copy",
            subset_rule=src.subset_rule, description=src.description,
        ))
    manifest = dict(note="Snapshot derived from hash-verified packaged evidence; original commit/path/SHA retained; no research Git history required.", files=rows)
    MANIFEST.write_text(json.dumps(manifest, indent=1) + "\n")
    return manifest


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text())


def verify_snapshot() -> list[dict]:
    """Check each local snapshot file against its recorded hash (HASH-ONLY tier)."""
    out = []
    for row in load_manifest()["files"]:
        p = SNAPSHOT_DIR / row["local_file"]
        ok = p.exists() and sha256(p.read_bytes()) == row["local_sha256"]
        out.append(dict(key=row["key"], ok=ok))
    return out


def verify_against_evidence() -> list[dict]:
    """Re-derive every snapshot file from Git and compare (uses packaged evidence; not an independent re-extraction)."""
    out = []
    for row in load_manifest()["files"]:
        src = SOURCES[row["key"]]
        if not evidence_available(src.commit, src.path):
            out.append(dict(key=row["key"], ok=None, note="origin deliberately not packaged; see EXCLUSIONS.csv"))
            continue
        raw = evidence_bytes(src.commit, src.path)
        ok = sha256(raw) == evidence_record(src.commit, src.path)["package_sha256"] and sha256(_derive(src, raw)) == row["local_sha256"]
        out.append(dict(key=row["key"], ok=ok))
    return out


# ---------------------------------------------------------------- loaders
def path(key: str) -> Path:
    return SOURCES[key].local_path


def csv(key: str, **kw) -> pd.DataFrame:
    return pd.read_csv(path(key), **kw)


def jsonfile(key: str) -> dict:
    return json.loads(path(key).read_text())

#!/usr/bin/env python3
"""Generate phg_report.ipynb (source of truth for structure) and EDITORIAL_TRACKER.md.

Reader-facing prose comes from prose.md; empty slots are omitted. Code cells
are hidden by default (jupyter.source_hidden + hide-input tag).
Run: python report/build_notebook.py
"""
import sys
from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
cells = []


def md(text):
    cells.append(nbf.v4.new_markdown_cell(text.strip("\n")))


def code(text, tags=()):
    meta = {"jupyter": {"source_hidden": True}, "tags": ["hide-input", *tags]}
    cells.append(nbf.v4.new_code_cell(text.strip("\n"), metadata=meta))


# ---------------------------------------------------------------- front matter
md("""
# Persona–human geometry

The 275 characters, the 240 historical traits and the released persona and trait vectors come from
Lu et al. (2026), *The Assistant Axis*. Everything not attributed to them is a PHG analysis.
""")

code("""
# ---- configuration: two flags ----------------------------------------------
import os
MODE = os.environ.get("PHG_MODE", "READER")   # "READER" or "REPRODUCTION"
DRAFT = os.environ.get("PHG_DRAFT", "1")      # "1": show draft outlines; "0": omit them (reader build)
# ---------------------------------------------------------------------------
os.environ["PHG_MODE"], os.environ["PHG_DRAFT"] = MODE, DRAFT
import sys, pathlib
ROOT = next(p for p in [pathlib.Path.cwd(), *pathlib.Path.cwd().parents] if (p / "phg").is_dir())
sys.path.insert(0, str(ROOT))
import pandas as pd
from phg import analysis as A, checks, figures as F, inventory, report as R, sources as S
REPRO = R.mode() == R.REPRODUCTION
L = R.Ledger()
INV = inventory.source_rows()

def sources_for(key):
    d = INV[INV.figure == key][["commit", "branch", "path"]].copy()
    d["commit"] = d.commit.str[:7]
    return R.details("Source commits", R.table_html(d, float_fmt="{}"), cls="sources") if len(d) else ""

def lead(key):
    R.show_html(R.lead_html(key))

def outline(key):
    R.show_html(R.outline_html(key))

# Method notes live in Appendix A; sections link to them.
METHODS = [
    ("formats", "Prompt formats",
     "Qwen's facet readouts were extracted twice: with scenario prompts and with survey-style prompts (Section 4). The main "
     "text uses the scenario-prompt extraction only; the survey-style values for Figures 4.1, 4.2 and E.6 are tabulated in Appendix F (F.2). "
     "Exception: the 13 reversals and 6 close matches keep their frozen definition, which uses both prompt formats (A.2)."),
    ("headline", "4.1 Classifying trait pairs",
     "The y axis is Qwen r from scenario prompts. "
     "Pairs are classed with the frozen screen from the outlier diagnostics, which uses both prompt formats: Qwen reverses the "
     "human pattern when the people correlation is at least .25 in size and both Qwen formats have the opposite sign with size "
     "at least .30; a close match is within .15 of the people value in both formats."),
    ("bestfit", "Trend lines",
     "Trend: standardized major axis, which treats both axes symmetrically. Its slope is the ratio of the two spreads; above "
     "1 means the vertical source links traits more strongly. A least-squares line would understate this when agreement is "
     "weak. Shown on Figures 4.1, G.1 and H.7 with the dashed perfect-agreement diagonal. Figure H.2 keeps its best-fit "
     "line on standardized scores, whose slope equals the correlation."),
    ("models", "G.1 Trait correlations compared between models",
     "The three saved 275 × 240 historical trait matrices (Lu et al. 2026 traits; same 275 characters in each model). Each "
     "trait column is put on the cross-model study's primary scale (e01cacb): the midrank-normal transform "
     "Φ⁻¹((average rank − .5)/275). Each model's 240 × 240 Pearson correlation matrix gives 28,680 trait-pair correlations; "
     "model-pair agreement is the Pearson correlation of those 28,680 values. Shading is a 2D histogram (80 × 80 cells on "
     "−1..1, log count); no individual points are drawn."),
    ("explorer", "1.3 Persona Landscape Explorer",
     "Positions are each model's saved persona PCA scores (PC1–PC6 of the saved PC1–PC10; model-local, centered). Trait scores "
     "come from the saved 275 × 240 historical cosine matrices and are shown standardized only: z-scores across that model's "
     "275 characters (population SD), i.e. standard deviations from the average character. Raw cosine values are comparable "
     "only within a model and are not shown or embedded. Axis tags list the three traits most negatively "
     "and most positively correlated with the PC, from the saved Qwen PC4–PC13 association table; no saved table exists for the "
     "other axes, so they are untagged. Embedded values are rounded to 4 decimals."),
    ("domain", "4.2 Domain averages and ordinary roles",
     "Domain averages are equal-weight means of the saved facet-pair correlations within each pair of Big Five domains "
     "(descriptive); Qwen blocks use the scenario-prompt pair correlations. The ordinary-role domain averages (130 characters "
     "in the frozen ordinary-role subset, outlier study c556609) are no longer displayed; their recomputation checks remain "
     "in Appendix D."),
    ("prediction", "E.6 Predicting real people's scores",
     "R² for predicting each held-out respondent's facet score from their other facets using Qwen's character-derived "
     "relationships, against a benchmark built the same way from people's own correlations (Human benchmark). Qwen: as "
     "measured. Qwen, calibrated: predictions multiplied by one common factor per format (0.529 for scenario prompts; 0.549 "
     "for survey-style prompts, Appendix F), fitted only on the 10,000 calibration respondents and evaluated on the 10,000 "
     "test respondents; "
     "coefficients, intercepts and splits are unchanged. Each Qwen marker carries one bar: the 95% interval from resampling "
     "the extraction questions (conditional on the frozen stopping points). The per-facet intervals for Qwen are the "
     "frozen Direct-30 B extraction intervals; the calibration package reproduces them from the same draws. Respondent "
     "(test-sample) 95% intervals are in the tables, not on the chart. Average intervals in the note are 95% from the "
     "calibration package; the frozen Direct-30 B averages (98.75%) are kept in their own table. Source for the calibrated "
     "values: codex/direct30-calibration-20261102 @ 677d4f2 (aggregates only). Facet-specific multipliers are exploratory "
     "and appear only in Appendix E.3."),
    ("influence", "H.1 Influence of characters and groups",
     "Scenario prompts. Exact leave-one-out over all 275 characters, and exclusion of each frozen analytical group (legacy assignments, not author "
     "categories), plus the definition-only ordinary-role subset of 130 characters. The ineligible six-character legacy 'other' "
     "family is not excluded, as in the frozen study."),
    ("style", "H.2 Style conditioning",
     "Scenario prompts. Colour is the historical Formal readout. The menu switches between the original relationship and the relationship "
     "conditioned on Formal, or on five styles (Formal, Animated, Verbose, Technical, Methodical). The original slope stays "
     "visible in every view. Conditioning linearly removes what the measured style readouts explain; it is not a correction and "
     "also removes much of each trait's variance."),
    ("geometry", "H.3 Geometric accounting",
     "Scenario prompts. Each Qwen correlation is split additively into the part carried by a five-dimensional projection (D, T or F) and the "
     "remainder. This accounts for Qwen's covariance; it is not a share of the people-vs-Qwen gap explained."),
    ("factors", "H.7 Trait–factor patterns",
     "Each dot is one of 240 historical traits: its correlation with Qwen F1 against its correlation with the matched factor in "
     "Llama or Gemma. Red dots meet a display rule chosen for this view (opposite signs with both at least .3 in size, or a "
     "difference of at least .6); it is not a frozen definition."),
    ("fit", "E.2 Facet fit",
     "For each facet: the mean of its saved correlations with the other facets in the same domain, for people (30,000 "
     "reference respondents) and for Qwen (275 characters, scenario and survey-style prompts)."),
    ("human", "Human data",
     "Johnson IPIP-NEO-300 (OSF): 30,000 reference, 10,000 calibration and 10,000 test respondents drawn from 117,259 unique "
     "complete adult response sets. SAPA V5 (Section 3): 23,679 respondents; each of the 42 bridged traits averages one to six "
     "SAPA items matched in a reviewed mapping fixed in September from the trait definitions, before any geometry was examined. "
     "Median reliability .72. SAPA gives each respondent a random subset of items, so each trait-pair correlation rests on the "
     "respondents who answered both item sets (median 475), and human correlations are weaker than longer scales would give. "
     "In the trait-with-domain view, people's domain scores are IPIP scales while the models' are built from the other mapped "
     "traits. Coverage is uneven: Conscientiousness has only four traits, and Extraversion has no Friendliness or Activity "
     "Level trait. Only aggregate statistics appear in this report."),
    ("extraction", "Facet extraction and the convergence rule", ""),  # iteration 54: written text in prose.md (method.extraction)
]
MNUM = {k: f"A.{i + 1}" for i, (k, _, _) in enumerate(METHODS)}

def method_link(key):
    n = MNUM[key]
    return f"<p class='phg-methodlink'>Method details: <a href='#method-{key}'>Appendix {n}</a></p>"
""")

code("R.init_page()", tags=("plotly-init",))

# ---------------------------------------------------------------- Summary
md("## Introduction")
code('R.show_html(R.body_html("summary"))')

# ---------------------------------------------------------------- Section 1
md("## 1 The persona landscape")
code("""
from phg import explorer, landscape as LS
R.show_html(R.source_tag("Data: Lu et al. (2026)", "Analysis: PHG"))
lead("section.1")
# Iteration 50: the lineage text moved into the Introduction; Section 1 opens with its own lead.
R.show_html("<h3 id='what-the-main-axes-separate'>What the main axes separate</h3>")
tpc = pd.concat([A.trait_pc_corr(m).rename_axis("Trait").reset_index().assign(Model=A.MODEL_LABEL[m]) for m in A.PC_MAP_MODELS])
tpc = tpc[["Model", "Trait"] + [f"PC{j}" for j in range(1, 6)]]
R.show(F.pc_trait_map_figure(), "1.1", post_script=F.pc_trait_map_script(),
       after=R.details("What each model's first three activation axes separate: strongest traits and characters at each end (table)",
                       F.axis_guide_html())  # iteration 47: collapsible
       + R.details("Correlation of all 240 traits with each model's PC1–PC5 (table)",
                   R.table_html(tpc, float_fmt="{:+.3f}", max_rows=800))
       + sources_for("1.1"))
R.show_html("<h3 id='characters-that-personify-the-axes'>Characters that personify the axes</h3>" + R.body_html("chars"))
checks.characters_text(L)
# Iteration 47: Figure 1.2, the 240 traits on the same axes (the explorer becomes Figure 1.3).
R.show_html("<h3 id='the-traits-on-the-axes'>The traits on the same axes</h3>")
R.show(F.trait_map_figure(), "tmap", post_script=F.trait_map_script("tmap"), after=sources_for("tmap"))
checks.figure_tmap(L)
R.show_html("<h3 id='exploring-the-persona-landscape'>Exploring the persona landscape</h3>")
a, b = LS.default_pair()
R.show_block("1.2", R.fig_label_html("1.2", "Character positions on the principal components, and each character's trait scores")
    + explorer.explorer_html()
    + R.details("How the default characters were chosen",
                f"<p>{R.html_escape(LS.DEFAULT_RULE)} With this rule A = <b>{a}</b> and B = <b>{b}</b>.</p>")
    + method_link("explorer") + sources_for("1.2"))
checks.figure_12(L)
checks.section1(L, reproduction=REPRO)
checks.snapshot_checks(L, "1", keys={"persona_pcs", "role_coords", "traits_qwen", "traits_llama", "traits_gemma",
                                     "pc_trait_qwen_ext", "pca_xmodel", "pca_diag",
                                     "bf_strict_map", "bf_domain_corr"}, reproduction=REPRO)
checks.planned_source_checks(L, "1", ["lineage", "pca_spectrum"], INV)
R.show_html(R.audit_line(L, "1"))
""")

# ---------------------------------------------------------------- Section 2
md("## 2 The three models arrange traits in largely the same way")
code("""
R.show_html(R.source_tag("Data: Lu et al. (2026)", "Analysis: PHG"))
lead("section.2")
# Iteration 53: the trait-pair comparison (key "G.1") opens Section 2 as Figure 2.1, the yardstick Section 3 reuses with people;
# the axis correspondence (key "2.1") is Figure 2.2; per-trait character-score agreement (key "2.2") moves to Appendix G.2.
mp = A.model_pair_agreement().assign(pair=lambda d: d.a.map(A.MODEL_LABEL) + "–" + d.b.map(A.MODEL_LABEL))[
    ["pair", "r", "sma", "same_sign", "n"]].rename(columns={"pair": "Models", "r": "Agreement r",
    "sma": "Trend slope (spread ratio)", "same_sign": "Pairs with the same sign", "n": "Trait pairs"})
R.show(F.model_pairs_figure(), "G.1",
       after=R.details("Model-pair agreement (table)", R.table_html(mp, float_fmt="{:+.4f}"))
       + R.details("Labelled trait pairs (table)", R.table_html(A.focal_hist_pairs().rename(columns={
           "label": "Trait pair", "qwen": "Qwen r", "llama": "Llama r", "gemma": "Gemma r"}), float_fmt="{:+.3f}"))
       + method_link("models") + method_link("bestfit") + sources_for("G.1"))
cc = pd.DataFrame([dict(Models=f"Qwen–{A.MODEL_LABEL[m]}", **{f"Canonical correlation {i + 1}": v
                       for i, v in enumerate(A.pc_plane_cca(m))}) for m in ["gemma", "llama"]])
R.show(F.pc_heatmap_figure(), "2.1",
       after=R.details("Canonical correlations of the PC1–PC2 planes (table)",
                       R.table_html(cc, float_fmt="{:.4f}")) + sources_for("2.1"))
c3 = pd.concat([pd.DataFrame(A.consensus_pc_corr(m), index=A.CONSENSUS, columns=[f"PC{j}" for j in range(1, 6)])
                .rename_axis("Consensus").reset_index().assign(Model=A.MODEL_LABEL[m]) for m in ["qwen", "gemma", "llama"]])
c3 = c3[["Model", "Consensus"] + [f"PC{j}" for j in range(1, 6)]]
# Iteration 42: second menu shows the traits that contribute most to each consensus direction (AA18 loadings).
csf, csv_ = F.consensus_combined_figure()
R.show(csf, "2.3", before=F.consensus_key_html(), post_script=F.consensus_combined_script("2.3", csv_),
       after=R.details("All values, three models (table)", R.table_html(c3.assign(Consensus=c3.Consensus.map(A.dlab)).rename(
           columns={"Consensus": "Shared direction"}), float_fmt="{:+.3f}"))
       + sources_for("2.3"))
checks.section2(L)
checks.figure_23(L)
checks.figure_23_contrib(L)
checks.consensus_key(L)
checks.planned_source_checks(L, "2", ["tpca_var", "tpca_vs_pc", "tpca_load", "fpearson", "aa18_load", "aa18_align"], INV)
checks.snapshot_checks(L, "2", keys={"cm01_matches", "aa18_scores", "aa18_loadings"}, reproduction=REPRO)
R.show_html(R.audit_line(L, "2"))
""")

# ---------------------------------------------------------------- Section 3 (iteration 33): the SAPA trait-word bridge
md("## 3 Do people arrange the traits the same way?")
code("""
R.show_html(R.source_tag("Human data: SAPA V5 (23,679 respondents)", "Analysis: PHG"))
lead("section.sapa")
# Iteration 42: the Big Five view moves to Section 3 (a human construct, introduced with the human data).
# Iteration 41: one Big Five figure (key "1.3", shown as 1.2) with three menus: Model; Show traits or domain scores;
# Columns Big Five traits or PC1-PC5. The explorer closes the section (1.3).
# Iteration 46: Figures 3.1 and 3.2 become one matrix (key "1.3", shown as 3.1) with Rows / Columns / Show menus.
bft = A.bf_traits()
bfmap = pd.DataFrame({"Domain": bft.domain.map(A.DOMAIN_NAME), "IPIP-NEO facet": bft.facet + " " + bft.facet_name,
                      "Trait": bft.label})
spc = pd.concat([A.bf_domain_blocks(s_).assign(Source=lab) for s_, lab in [("people", "People (SAPA)"), ("qwen", "Qwen"),
                 ("gemma", "Gemma"), ("llama", "Llama")]])
spc = spc[spc.row != spc.col]
dom_tab = spc.pivot_table(index=["row_name", "col_name"], columns="Source", values="mean_r", sort=False)[
    ["People (SAPA)", "Qwen", "Gemma", "Llama"]]
dsr = spc[spc.Source != "People (SAPA)"].pivot_table(index=["row_name", "col_name"], columns="Source", values="domain_r", sort=False)[
    ["Qwen", "Gemma", "Llama"]].add_suffix(" domain-score r")
dom_tab = dom_tab.join(dsr).reset_index().rename(columns={"row_name": "Domain", "col_name": "With domain"})
bfp = pd.concat([A.bf_pc_corr(m, 5).rename_axis("Trait").reset_index().assign(Model=A.MODEL_LABEL[m]) for m in ["qwen", "gemma", "llama"]])
bfp = bfp.assign(Domain=list(bft.domain.map(A.DOMAIN_NAME)) * 3)[["Model", "Domain", "Trait"] + F.BF_PCS]
tdm = A.bridge_domain_summary()
R.show(F.bigfive_matrix_figure(), "1.3", post_script=F.bigfive_matrix_script("1.3"),
       after=R.details("The 42 traits and their Big Five facets (frozen strict mapping; (−) = reverse-keyed, sign flipped)",
                       R.table_html(bfmap, float_fmt="{}", max_rows=60))
       + R.details("Does each trait belong to its assigned domain? People and the three models (table)", R.table_html(tdm, float_fmt="{:+.2f}"))
       + R.details("Domain averages (average trait-pair r) for people and the three models, and the models' domain-score r (table)",
                   R.table_html(dom_tab, float_fmt="{:+.2f}"))
       + R.details("Each trait's correlation with PC1–PC5, three models (table)", R.table_html(bfp, float_fmt="{:+.3f}", max_rows=200))
       + sources_for("1.3"))
checks.figure_bfpc(L)
checks.figure_13(L)
checks.figure_bm(L)
checks.section_sapa(L)
checks.snapshot_checks(L, "S", keys={"bf_sapa_corr", "bf_sapa_domains"}, reproduction=REPRO)
R.show_html(R.audit_line(L, "S"))
""")

# ---------------------------------------------------------------- Section 3
md("## 4 Measuring the Big Five facets directly inside Qwen")
code("""
from phg import human
R.show_html(R.source_tag("Human data: Johnson IPIP-NEO-300 (30,000 respondents)", "Analysis: PHG"))
lead("section.3")
R.show_html("<h3 id='two-ways-of-eliciting-each-facet'>How each facet was extracted</h3>")
R.show_html(R.body_html("s3.1"))
stp = A.stopping_table()
stp = stp.assign(Facet=[f"{c} {A.facet_label30(c)}" for c in stp.facet], Format=stp.format.map({"scenario": "Scenario", "survey_style": "Survey-style"}))
stp = stp[["Facet", "Format", "stopping_n", "available", "last_checkpoint", "p05", "prev", "qualified"]].rename(columns={
    "stopping_n": "Stopping n", "available": "Accepted questions available", "last_checkpoint": "Last checkpoint",
    "p05": "Bootstrap p05 cosine at stop", "prev": "Cosine to previous at stop", "qualified": "Facet kept"})
# Iteration 35: the stopping and question-direction figures were removed; the method is described in text and the full
# stopping table stays here (Codex 598857c; checks in section_conv).
R.show_html(R.details("Stopping points for all 30 facets and both prompt formats (table)", R.table_html(stp, float_fmt="{:.3f}", max_rows=80))
            + R.details("Source commits", "<p class='phg-small'>codex/facet-convergence-geometry-20261106 @ 598857c: "
                        "results/final_question_counts.csv, stopping_histories.csv, question_directions_pc123.csv</p>", cls="sources"))
checks.section_conv(L)
checks.extraction_counts(L)
R.show_html(method_link("human"))
checks.planned_source_checks(L, "3", ["aa19_class", "aa27_cov", "aa27_gate", "ipip_cov"], INV)
raw = human.raw_available()
checks.section3_formats(L)
checks.figure_31(L)
checks.snapshot_checks(L, "3", keys={"fexp_geo", "fexp_var", "conv_final", "conv_hist", "conv_q", "conv_mean", "conv_pcv", "conv_var"}, reproduction=REPRO)
L.add("3.raw_file", "HASH-ONLY", "raw IPIP300.dat present with AA27 SHA-256 (needed for human recomputation)", True,
      True if (REPRO and raw) else None, section="3",
      note="" if (REPRO and raw) else ("file absent: run download_ipip.py" if REPRO else "checked in REPRODUCTION mode only"))
""")

# ---------------------------------------------------------------- Section 4
md("### Trait pairs: Qwen links some traits as people do, and reverses others")
code("""
# Iteration 28: the former headline figure (Figure 0) moved here as Figure 4.1; its key stays "H".
R.show(F.human_vs_qwen_scatter(), "H", after=F.reversal_table_html() + method_link("headline") + method_link("formats")
       + method_link("bestfit")
       + sources_for("H"))
""")

md("### The Neuroticism–Extraversion block")
code("""
cols = {"row_name": "Domain", "col_name": "With domain", "n_pairs": "Facet pairs", "human": "People",
        "scenario": "Qwen", "diff_scenario": "Qwen r − people r"}
tbl = lambda d: R.table_html(d[list(cols)].rename(columns=cols), float_fmt="{:+.3f}")
# Iteration 36: after the trait-pair scatter (Figure 4.1), so its 13 outlined reversals are already introduced; the
# 15-row largest-differences table was dropped as redundant with them.
R.show(F.correlation_matrices(), "4.2", post_script=F.matrix_detail_script("4.2"),
       after=R.details("Domain averages (table): average of facet-pair correlations, descriptive", tbl(A.domain_blocks()))
       + method_link("domain") + sources_for("4.2"))
""")

code('R.show_html(R.body_html("4.4"))')

code("""
checks.section4(L, reproduction=REPRO)
checks.trend_checks(L)  # Figure 4.2 and the survey-style spread ratio (section 4), 5e.3 and 5b (section 5)
# Iteration 33: Appendix H (former Section 5) checks run here so Appendix D includes them.
checks.section5(L, reproduction=REPRO)
checks.snapshot_checks(L, "5", keys={"d30b_profiles", "hist_styles48", "od_loo", "od_composition", "od_style_var", "od_persona_class",
                                     "od_items", "ha_items", "ha_bins", "ha_facets", "cross_primary", "cm01_pairs", "cm01_all240",
                                     "cm01_matches", "fexp_pairs", "ctgeo_pairs", "od_conditions"}, reproduction=REPRO)
checks.appendix_f(L)  # Appendix F table (ledger section F), iteration 15
checks.appendix_g(L)  # Appendix G checks (ledger section G), run here so Appendix D includes them
checks.appendix_e(L)  # E.2 facet-fit checks (ledger section E), run here so Appendix D includes them
checks.appendix_e4(L)  # E.4 factor checks (iteration 21)
checks.snapshot_checks(L, "E", keys={"aa17_scores", "fexp_poles"}, reproduction=REPRO)
checks.snapshot_checks(L, "4", keys={"d30b_profiles", "d30b_relationships", "d30b_fingerprints", "d30b_facet_results", "d30b_resp_int",
                                     "d30b_extr_int", "d30b_macro_resp", "d30b_macro_extr", "od_all_pairs", "od_screened",
                                     "cal12_test", "cal12_mult", "cal12_curve", "od_corr_unc", "od_persona_class",
                                     "od_composition"}, reproduction=REPRO)
R.show_html(R.audit_line(L, ("3", "4")))
""")

# ---------------------------------------------------------------- 6-9 and About
md("## 5 Discussion")
code("""
# Iteration 36: the GPT comparison (Figure 5.1) opens the Discussion; it motivates D2.
# Iteration 32: Figure 6.1, Big Five domain correlations in people, in GPT answers (Petrov et al. 2024) and in activations.
R.show_html(R.body_html("discussion.0"))  # iteration 49: the central difference first, then Figure 5.1
R.show_html("<h3 id='valence-vs-intensity'>Model answers and model activations compared with people</h3>")
src_lab = {k: v[0] + (" (demographic personas)" if "silicon" in k else (" (generic personas)" if "generic" in k else ""))
           for k, v in F.SOURCE_STYLE.items()}
dct = A.domain_corr_sources()
dct.index = [f"{A.DOMAIN_NAME[a]} – {A.DOMAIN_NAME[b]}" for a, b in dct.index]
dct = dct.rename(columns=src_lab).T.reset_index().rename(columns={"index": "Source"})
tf = A.template_fit().rename(index=src_lab).reset_index().rename(columns={"index": "Source", "valence": "Match to valence pattern",
     "intensity": "Match to intensity pattern", "people_bbc": "Match to BBC people"})
R.show(F.domain_sources_figure(), "6.1", post_script=F.domain_sources_phone_script("6.1"),
       after=R.details("Domain correlations by source (table)", R.table_html(dct, float_fmt="{:+.2f}"))
       + R.details("How closely each source matches the two sign patterns (post hoc, descriptive)", R.table_html(tf, float_fmt="{:+.2f}"))
       + sources_for("6.1"))
checks.figure_61(L)
R.show_html(R.body_html("discussion"))
checks.planned_source_checks(L, "6", ["d26_agree", "calsub_eval", "steer_arms", "steer_cmp", "ipipq_brief", "tool01_readme"], INV)
R.show_html(R.audit_line(L, "6"))
""")
md("## 6 Limitations")
code('R.show_html(R.body_html("limitations"))')
md("## 7 Related work")
code('R.show_html(R.body_html("related"))')
md("## 8 Open questions and next steps")
code('R.show_html(R.body_html("open"))')
md("## About this work")
code('R.show_html(R.body_html("about"))')

# ---------------------------------------------------------------- Appendices
md("## Appendix A: Methods")
code("""
def method_body(k, body):
    if k != "extraction":
        return f"<p>{R.html_escape(body)}</p>"
    # Iteration 54: A.14 is written text with two tables (stopping points; responses against Lu et al.).
    ec = A.extraction_counts()
    st = ec.pivot_table(index="format", columns="stopping_n", values="facet", aggfunc="count", fill_value=0)
    st = st.rename(index={"scenario": "Scenario questions (26 facets)", "survey_style": "Survey-style statements (26 facets)"})
    st = st.rename_axis("Accepted pairs at stop").rename_axis(None, axis=1).reset_index()
    st.columns = [str(int(c)) if not isinstance(c, str) else c for c in st.columns]
    per = ec.groupby("facet").generated.sum()
    lo1, hi1, lo2, hi2, m = ec.generated.min(), ec.generated.max(), per.min(), per.max(), per.mean()
    L_ = A.LU_RESPONSES_PER_POLE
    eff = pd.DataFrame([
        {"Responses per pole": "One format", "This study": f"{lo1}–{hi1}", "Lu et al.": f"{L_:,}", "Fewer by": f"{L_ / hi1:g}–{L_ / lo1:g}×"},
        {"Responses per pole": "Both formats, per facet", "This study": f"{lo2}–{hi2}", "Lu et al.": f"{L_:,}", "Fewer by": f"{L_ / hi2:g}–{L_ / lo2:g}×"},
        {"Responses per pole": "Average per facet, both formats", "This study": f"{m:.1f}", "Lu et al.": f"{L_:,}", "Fewer by": f"{L_ / m:.1f}×"}])
    h = R.body_html("method.extraction")
    h = h.replace("<p class='phg-body'>[[TABLE:stops]]</p>", R.table_html(st, float_fmt="{}"))
    h = h.replace("<p class='phg-body'>[[TABLE:efficiency]]</p>", R.table_html(eff, float_fmt="{}"))
    return h
R.show_html("".join(f"<h3 id='method-{k}'>{MNUM[k]} {R.html_escape(t)}</h3>{method_body(k, body)}" for k, t, body in METHODS))
""")

md("## Appendix B: Data inheritance and provenance")
code("""
prov = INV[["figure", "commit", "branch", "path", "bytes"]].copy()
prov["commit"] = prov.commit.str[:7]
R.show_html("<p>Personas, trait list and released vectors: Lu et al. (2026), The Assistant Axis. Human data: Johnson "
            "IPIP-NEO-300 (OSF), aggregates only. Every other input is a PHG output read from a pinned Git commit into a "
            "hash-checked snapshot (research/notebooks/data/snapshot_manifest.json).</p>"
            + R.details(f"All {len(prov)} figure inputs (commit, branch, path, bytes)", R.table_html(prov, float_fmt="{:,.0f}")))
""")

md("## Appendix C: Glossary and facet key")
code("""
glossary = pd.DataFrame([
    ("Scenario prompts / survey-style prompts", "Qwen's facet readouts were extracted twice: once from scenario prompts and once from survey-style (questionnaire-like) prompts. Results are shown for each."),
    ("PC1–PC6", "Activation PCA of persona vectors."),
    ("T1–T5", "Qwen-only PCA of the 275 × 240 historical trait scores."),
    ("F1–F5 (Qwen), F1–F6 (Llama, Gemma)", "Each model's own factor analysis of its 240 trait scores."),
    ("D1–D5", "The five shared directions: found jointly in the three models' trait scores (generalized canonical correlation analysis). Not the Conscientiousness facets C1–C6."),
    ("Conditioned on X", "Correlation after linearly removing what the measured readout X explains. A descriptive view, not a correction."),
    ("Ordinary roles", "The 130 characters classed as everyday human roles in the frozen outlier study."),
], columns=["Term", "Meaning"])
key = pd.DataFrame([dict(Domain=A.DOMAIN_NAME[c[0]], Facet=A.name(c), Code=c) for c in A.ordered_codes()])
R.show_html("<h3>Glossary</h3>" + R.table_html(glossary) + "<h3>Facet key (26 facets and codes)</h3>" + R.table_html(key))
""")

md("## Appendix D: Numerical audit")
code("""
head = [c for c in L.section("5") if c.id.startswith("5.E1N2")]
summary = pd.DataFrame([dict(tier=t, **v) for t, v in L.summary().items()]).fillna(0)
intro = ("<p>" + R.html_escape(R.mode_banner_text(R.mode())) + "</p><p>Tiers: <b>RECOMPUTED</b> (independently recalculated "
         "here), <b>CHECKED</b> (compared with a saved result), <b>HASH-ONLY</b> (source integrity only). <b>NOTE</b> marks a "
         "frozen brief that rounds a value differently from its CSV, or a saved file printed at lower precision; the CSV or "
         "full-precision value is used. Every figure's sources are listed in INVENTORY.md.</p>")
R.show_html(R.details("Open the audit", intro
    + R.verification_html(head, "Required: Qwen Friendliness–Anger +.7098 / +.6071 and people −.2805")
    + R.table_html(summary, caption=f"All checks this run ({R.mode()} mode)", float_fmt="{:.0f}")
    + R.audit_appendix(L), cls="audit-root"))
_ = (ROOT / "report" / f"verification_{R.mode().lower()}.json").write_text(L.to_json() + "\\n")  # no stray byte count
""")

md("## Appendix E: Technical explorations")
code('lead("section.E")')

md("### E.1 Calibration slider (earlier nine-facet experiment)")
code("""
cal = A.calibration()[["source", "facet", "S", "R2_original", "R2_common", "R2_facet_saved", "R2_human", "k_common"]].copy()
cal["facet"] = cal.facet.map(A.name)
cal["source"] = cal.source.map(A.FORMAT_NAME)
inner = (R.lead_html("E.1") + R.figure_html(F.calibration_slider(), "E.1") + R.caption_html("E.1") + R.evidence_panel("E.1")
         + "<p class='phg-small'>Direct-12 (nine facets). Predictions are scaled toward the reference mean by k; squared error "
           "is an exact quadratic in k, recomputed from three saved conditions. Ordering is unchanged for k &gt; 0 and "
           "undefined at k = 0. The fitted λ came from calibration respondents only. Post hoc and illustrative.</p>"
         + R.details("Saved results at k = 1 and k = λ", R.table_html(cal)) + sources_for("E.1"))
R.show_html(R.details("Calibration slider: earlier nine-facet experiment", inner, cls="technical"))
""")

md("### E.2 How well each facet fits its domain")
code("""
fit = A.facet_fit()[["domain", "name", "n_pairs", "human", "scenario", "survey"]].rename(columns={
    "domain": "Domain", "name": "Facet", "n_pairs": "Same-domain facets", "human": "People", "scenario": "Qwen, scenario",
    "survey": "Qwen, survey-style"})
R.show(F.facet_fit_figure(), "E.2", after=R.details("All values (table)", R.table_html(fit, float_fmt="{:+.3f}"))
       + method_link("fit") + sources_for("E.2"))
""")

md("### E.3 Facet-specific rescaling (exploratory)")
code("""
fx = A.rescaled_table().assign(source=lambda d: d.source.map(A.FORMAT_NAME))[
    ["source", "name", "original", "rescaled", "facet_mult", "facet_R2", "facet_lo", "facet_hi"]].rename(columns={
    "source": "Format", "name": "Facet", "original": "As measured", "rescaled": "Common rescaling",
    "facet_mult": "Facet multiplier", "facet_R2": "Facet-specific R²", "facet_lo": "Respondents 95%, lower",
    "facet_hi": "Respondents 95%, upper"})
R.show_html("<p class='phg-small'>One multiplier per facet, fitted on the calibration respondents. Exploratory: it does not "
            "replace the common (one per format) rescaling shown in Figure E.6.</p>" + R.table_html(fx, float_fmt="{:+.3f}")
            + sources_for("E.3"))
""")

md("### E.4 Each model's own trait factors")
code("""
f12 = pd.concat([pd.DataFrame(A.factor_pc_corr(m), columns=[f"PC{j}" for j in range(1, 7)]).assign(
    Model=A.MODEL_LABEL[m], Factor=[f"F{i + 1}" for i in range(A.MODEL_FACTORS[m])],
    **{"PC1–PC6 R²": A.factor_pc_r2(m)}) for m in ["qwen", "gemma", "llama"]])
f12 = f12[["Model", "Factor"] + [f"PC{j}" for j in range(1, 7)] + ["PC1–PC6 R²"]]
fc = pd.DataFrame(A.factor_consensus_corr("qwen"), columns=[A.dlab(c) for c in A.CONSENSUS]).assign(Factor=[f"F{k} · {A.FACTOR_LABEL[f'F{k}']}" for k in range(1, 6)])
fc = fc[["Factor"] + [A.dlab(c) for c in A.CONSENSUS]]
z31f, r31f = A.facet_direction_matrix("F")
ff = pd.DataFrame(z31f, columns=[f"F{k}" for k in range(1, 6)]).assign(Facet=[A.name(f) for f in A.ordered_codes()], **{"F1–F5 R²": r31f})
ff = ff[["Facet"] + [f"F{k}" for k in range(1, 6)] + ["F1–F5 R²"]]
R.show(F.factor_pc_figure(), "E.4", before=F.factor_key_html(), post_script=F.phone_compact_script("E.4", 60),
       after=R.details("All values, three models (table)", R.table_html(f12, float_fmt="{:+.3f}"))
       + R.details("Qwen's factors and the shared directions D1–D5 (table)", R.table_html(fc, float_fmt="{:+.3f}"))
       + R.details("Qwen's facets and its factors F1–F5, scenario prompts (table)", R.table_html(ff, float_fmt="{:+.3f}"))
       + sources_for("E.4"))
R.show_html(R.audit_line(L, "E"))
""")

md("### E.5 Where the facets sit in Qwen's geometry")
code("""
# Iteration 35: moved from Section 4 (it describes Qwen's own axes rather than comparing with people). Checks
# (figure_31) still run in the Section 4 cell so Appendix D includes them.
z31 = []
for v, lab in [("C", "Consensus"), ("PC", "Qwen PC")]:  # Qwen factors: Appendix E.4
    Z, r2 = A.facet_direction_matrix(v)
    z31.append(pd.DataFrame(Z, columns=[f"{lab} {k}" for k in range(1, 6)]).assign(**{f"{lab} R²": r2}))
f31 = pd.concat([pd.DataFrame({"Facet": [A.name(f) for f in A.ordered_codes()]})] + z31, axis=1)
R.show(F.facets_geometry_figure(), "3.2", post_script=F.phone_compact_script("3.2", 118, short_y=False),
       after=R.details("All values (table)", R.table_html(f31, float_fmt="{:+.3f}")) + sources_for("3.2"))
""")

md("### E.6 Predicting real people's scores")
# Iteration 36: moved from Section 4; its checks (section4) still run before Appendix D.
code("""
fr43 = A.S.csv("d30b_facet_results")
hum43 = fr43[fr43.condition == "human_reference"].groupby("source").R2.mean()
rmac = A.rescaled_macro().assign(human=lambda d: d.source.map(hum43)).query("source == 'scenario'")[
    ["human", "as_measured", "am_q_lo", "am_q_hi", "rescaled", "q_lo", "q_hi", "improved", "multiplier"]].rename(columns={
    "human": "Human benchmark", "as_measured": "Qwen", "am_q_lo": "Qwen, prompts 95% lower",
    "am_q_hi": "Qwen, prompts 95% upper", "rescaled": "Qwen, calibrated", "q_lo": "Calibrated, prompts 95% lower",
    "q_hi": "Calibrated, prompts 95% upper", "improved": "Facets improved (of 26)", "multiplier": "Multiplier"})
r2t = A.r2_table().set_index("facet")
rt = A.rescaled_table().query("source == 'scenario'")
rt = rt.assign(human=r2t.loc[rt.facet, "R2_human"].to_numpy(),
               e_lo=[r2t.loc[f, f"extr_lo_{s}"] for f, s in zip(rt.facet, rt.source)],
               e_hi=[r2t.loc[f, f"extr_hi_{s}"] for f, s in zip(rt.facet, rt.source)],
               p_lo=[r2t.loc[f, f"resp_lo_{s}"] for f, s in zip(rt.facet, rt.source)],
               p_hi=[r2t.loc[f, f"resp_hi_{s}"] for f, s in zip(rt.facet, rt.source)],
               )[
    ["name", "human", "original", "e_lo", "e_hi", "p_lo", "p_hi", "rescaled", "q_lo", "q_hi", "resp_lo", "resp_hi"]].rename(columns={
    "name": "Facet", "human": "Human benchmark", "original": "Qwen", "e_lo": "Qwen, prompts 95% lower",
    "e_hi": "Qwen, prompts 95% upper", "p_lo": "Qwen, test respondents 95% lower", "p_hi": "Qwen, test respondents 95% upper",
    "rescaled": "Qwen, calibrated", "q_lo": "Calibrated, prompts 95% lower", "q_hi": "Calibrated, prompts 95% upper",
    "resp_lo": "Calibrated, test respondents 95% lower", "resp_hi": "Calibrated, test respondents 95% upper"})
mi = A.macro_intervals().query("source == 'scenario'").drop(columns="source").rename(columns={
    "family": "Family", "confidence": "Confidence", "median": "Median", "lower": "Lower", "upper": "Upper",
    "draws_defined": "Draws defined", "draws_total": "Draws"})
R.show(F.heldout_r2(), "4.3", after=R.details("Average R² with 95% intervals (table)", R.table_html(rmac, float_fmt="{:+.4f}"))
       + R.details("Per-facet R² with 95% intervals from prompts and from test respondents (table)", R.table_html(rt, float_fmt="{:+.3f}"))
       + R.details("Average R² for Qwen: frozen Direct-30 B intervals at 98.75% (respondent and question families; no 95% "
                   "respondent interval is saved)", R.table_html(mi))
       + method_link("prediction") + sources_for("4.3"))
""")

# ---------------------------------------------------------------- Appendix F
md("## Appendix F: Survey-style prompt results")
code("""
R.show_html("<p class='phg-small'>Each facet was also extracted with survey-style prompts (Section 4). F.1 compares the two "
            "methods; F.2 gives the main results for both side by side, linking to the figures that show them. The figures "
            "themselves are not repeated here.</p>")
fa = A.format_agreement()[["domain", "name", "r"]].rename(columns={"domain": "Domain", "name": "Facet",
                                                                    "r": "r between scenario and survey-style scores"})
R.show(F.format_agreement_figure(), "F.1", after=R.details("All values (table)", R.table_html(fa, float_fmt="{:.3f}"))
       + method_link("formats") + sources_for("F.1"))

R.show_html("<h3 id='f2-survey-alongside'>F.2 Survey-style results alongside the main text</h3>")
R.show_block("F.2", F.format_results_table_html() + method_link("formats")
             + R.details("Trait-pair correlations, both prompt methods (325 pairs)", R.table_html(A.pairs_by_format(), float_fmt="{:+.3f}"))
             + R.details("Prediction R² per facet, survey-style prompts", R.table_html(A.survey_r2_table(), float_fmt="{:+.3f}"))
             + sources_for("F.2"))
R.show_html(R.audit_line(L, "F"))
""")

# ---------------------------------------------------------------- Appendix G
md("## Appendix G: How the models were compared")
code("""
def gsrc(entry, branch, commit):
    return ("<p class='phg-gsource'><b>Source:</b> " + R.html_escape(entry) + "; <code>" + R.html_escape(branch) + "</code> @ <code>"
            + R.html_escape(commit) + "</code></p>")
R.show_html(R.tag("Collects every cross-model comparison; Figures 2.1 and 2.2 appear in Section 2, Figure G.2 here")
            + "<style>.phg-gsource{font-size:13px;color:#5b6b82;margin:2px 0 8px}</style>")

R.show_html("<h3 id='g1-trait-pair-correlations'>G.1 Trait-pair correlations</h3>")
R.show_html(gsrc("RESEARCH_STATE “Oct 15 — cross-model historical trait relationships”",
                 "codex/cross-model-trait-relationships-20261015", "e01cacb")
            + "<p class='phg-small'>Shown in <a href='#wrap-G.1'>Figure 2.1</a> (Section 2).</p>")

R.show_html("<h3 id='g2-persona-scores'>G.2 Persona scores</h3>")
R.show_html(gsrc("RESEARCH_STATE “AA16–19” (three-model consensus outputs)", "main", "65da790")
            + gsrc("RESEARCH_STATE “September 24 — Gregariousness structural follow-up” (.655–.825)", "main", "65da790"))
g2 = A.persona_score_agreement().assign(pair=lambda d: d.a.map(A.MODEL_LABEL) + "–" + d.b.map(A.MODEL_LABEL)).groupby(
    "pair", sort=False).r.describe()[["min", "25%", "50%", "75%", "max"]].reset_index().rename(columns={
    "pair": "Models", "min": "Lowest", "25%": "Lower quartile", "50%": "Median", "75%": "Upper quartile", "max": "Highest"})
R.show(F.persona_agreement_figure(), "2.2",
       after=R.details("Summary per model pair (table)", R.table_html(g2, float_fmt="{:+.3f}"))
       + "<p class='phg-small'>An earlier Gregariousness follow-up (September 24) reported .655–.825 for a single gregarious "
         "indicator under that study's scoring; it is not the same statistic.</p>" + sources_for("2.2"))

R.show_html("<h3 id='g3-main-activation-axes'>G.3 Main activation axes</h3>")
R.show_html(gsrc("No RESEARCH_STATE entry (extended persona PCA, snapshot pin)", "main", "65da790")
            + "<p class='phg-small'>The axis-by-axis correlations and the plane canonical correlations are shown in "
              "<a href='#wrap-2.1'>Figure 2.2</a> (Section 2). Below: how much of the variation each axis carries (Figure G.3a) "
              "and the characters on the first axes (Figure G.3b).</p>")
# Iteration 48: variance carried by each activation axis (Figure G.3a; was 2.1 in iterations 44-47).
pv = A.S.csv("pca_diag").query("component <= 5").assign(Model=lambda d: d.model.map(A.MODEL_LABEL))
pv = pv[["Model", "component", "explained_variance_ratio", "cumulative_explained_variance", "bootstrap_loading_cosine_q05"]].rename(columns={
    "component": "Axis", "explained_variance_ratio": "Share explained", "cumulative_explained_variance": "Cumulative share",
    "bootstrap_loading_cosine_q05": "Stability (5th-percentile bootstrap cosine)"})
R.show(F.variance_elbow_figure(), "elbow", after=R.details("All values, PC1–PC5, three models (saved PCA diagnostics)",
       R.table_html(pv, float_fmt="{:.3f}")) + sources_for("elbow"))
checks.figure_elbow(L)
R.show(F.pc1_scatter_figure(), "G.3b", after=sources_for("G.3b"))

R.show_html("<h3 id='g4-factor-matching'>G.4 Factor matching</h3>")
R.show(F.factor_match_figure(), "G.4",
       before=gsrc("RESEARCH_STATE “Oct 27 — PHG-CM01 factors”", "codex/phg-cm01-cross-model-factors", "cc4ef37")
       + gsrc("RESEARCH_STATE “AA16–19” (AA17 factors)", "main", "65da790"),
       after="<p class='phg-small'>Worked examples: <a href='#wrap-5e.3'>Figure H.7</a>.</p>" + sources_for("G.4"))

R.show_html("<h3 id='g5-consensus-directions'>G.5 Shared directions D1–D5</h3>")
g5 = A.consensus_table().assign(component=lambda d: d.component.map(A.dlab)).rename(columns={"component": "Direction", "projector_eigenvalue": "Shared across models (projector eigenvalue, of 3)",
    "heldout_mean_pairwise_pearson": "Held-out agreement between models (mean r)", "status": "Human status",
    "human_projection_r": "Human subspace projection r", "bridge_adequate": "Human bridge adequate"})
R.show_block("G.5", gsrc("RESEARCH_STATE “AA16–19”", "main", "65da790") + R.table_html(g5, float_fmt="{:.3f}")
             + sources_for("G.5"))

R.show_html("<h3 id='g6-beyond-personas'>G.6 Beyond personas</h3>")
R.show_block("G.6", gsrc("RESEARCH_STATE “October 9 — cross-model local semantic relationships, completed primary study”",
                         "codex/cross-model-local-geometry-execution-20261008", "fe3a307") + sources_for("G.6"))

R.show_html("<h3 id='g7-what-is-not-yet-compared'>G.7 What is not yet compared</h3>")
R.show_block("G.7", gsrc("RESEARCH_STATE “Oct 27 — PHG-CM01 factors” (direct Llama/Gemma IPIP unmeasured)",
                         "codex/phg-cm01-cross-model-factors", "cc4ef37"))
R.show_html(R.audit_line(L, "G"))
""")

# ---------------------------------------------------------------- Appendix H (was Section 5 until iteration 33)
md("""
## Appendix H: Case study: Friendliness and Anger
""")
code("""
R.show_html(R.source_tag("Analysis: PHG", "Human data: Johnson IPIP-NEO-300"))
lead("section.5")
""")

md("### Is it driven by unusual characters?")
code("""
R.show_html(R.tag("Direct measurement · Qwen IPIP facets"))
loo = A.loo_e1n2()
loo = loo[loo.source == "scenario"]
top = loo.reindex(loo.change.abs().sort_values(ascending=False).index).head(5)[["persona", "r_without", "change"]].rename(
    columns={"persona": "Character removed", "r_without": "Qwen r without it", "change": "Change"})
R.show(F.influence_figure(), "5a",
       after=R.details("Five most influential single removals", R.table_html(top, float_fmt="{:+.4f}"))
       + method_link("influence") + sources_for("5a"))
""")

md("### Is it response style?")
code("""
R.show_html(R.tag("Statistical conditioning · style-adjusted, with variance removed shown"))
ct = A.conditioning_table().query("source == 'scenario'").drop(columns="source").rename(columns={
    "condition": "Condition", "r": "Qwen r", "var_removed_E1": "Variance removed, Friendliness",
    "var_removed_N2": "Variance removed, Anger"})
R.show(F.style_scatter(), "5b",
       after=R.details("Original and conditioned correlations, with variance removed", R.table_html(ct, float_fmt="{:+.4f}"))
       + method_link("style") + sources_for("5b"))
""")

md("### Where in the geometry?")
code("""
R.show_html(R.tag("Geometric accounting · C, T and F five-dimensional projections"))
R.show(F.ctf_bars(), "5c", after=method_link("geometry") + sources_for("5c"))
""")

md("### Is it the questionnaire itself?")
code("""
R.show_html(R.tag("Human item analysis · 117,259 respondents"))
R.show_block("5d.1", "<p class='phg-listhead'>The ten questionnaire items for each facet</p>" + F.item_columns_html() + sources_for("5d.1"))
R.show(F.anger_items_figure(), "5d.2", after=sources_for("5d.2"))
R.show(F.anger_bands_figure(), "5d.3", after=sources_for("5d.3"))
""")

md("### Is it specific to Qwen?")
code("""
R.show_html(R.tag("Cross-model proxy comparison · historical traits, not IPIP facets"))
cmt = A.cross_model_table().pivot_table(index="relationship", columns=["view", "model"], values="adjusted_Pearson", sort=False)
cmt.columns = [f"{m}, {v}" for v, m in cmt.columns]
R.show(F.cross_model_figure(), "5e.1",
       after=R.details("All values (raw and conditioned, three models)", R.table_html(cmt.reset_index())) + sources_for("5e.1"))
cm = A.cm01_table().pivot_table(index="relationship", columns="model", values="r", sort=False)[["Qwen", "Llama", "Gemma"]]
R.show_block("5e.2", "<p class='phg-listhead'>PHG-CM01 focal relationships (original cosine scores, correlation r)</p>"
             + R.table_html(cm.reset_index(), float_fmt="{:+.2f}") + sources_for("5e.2"))
R.show(F.factor_pattern_figure(), "5e.3", after=method_link("factors") + sources_for("5e.3"))
""")

code("""
R.show_html(R.audit_line(L, "5"))
""")

nb = nbf.v4.new_notebook(cells=cells)
nb.metadata.update({"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"},
                    "language_info": {"name": "python"}})

if __name__ == "__main__":
    from phg import inventory, prose
    nbf.write(nb, HERE / "phg_report.ipynb")
    skel = {}
    for f in inventory.FIGURES:
        if f.status == "SKELETON":
            skel.setdefault(f.section, []).append(f"{f.id} {f.title}")
    # Packaging excludes the editorial tracker; no working notes are generated.
    print(f"wrote {len(cells)} cells (no editorial working files)")

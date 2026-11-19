"""Verification checks for each report section, labelled by tier.

Expected constants quoted from frozen reports are cited by source so a
reviewer can trace them. A FAIL is reported, never tuned away.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import analysis as A
from . import human
from . import sources as S
from . import stats
from .report import Ledger

# Quoted values (source in comment).
QWEN_E1N2 = {"scenario": 0.7098, "survey_style": 0.6071}  # task brief / Direct-30 B REPORT.md
HUMAN_E1N2 = -0.2805  # task brief; REPORT.md gives -0.280477
HUMAN_E1N2_ANGER_STUDY = -0.280477382116  # human-anger DECISION_BRIEF.md reproduction
MACRO_R2 = {"scenario": 0.045794, "survey_style": 0.078076, "human": 0.584196}  # Direct-30 B REPORT.md
MACRO_RESP = {"scenario": (0.034627, 0.057040), "survey_style": (0.065741, 0.090130)}
MACRO_QUES = {"scenario": (-0.025264, 0.109686), "survey_style": (-0.016034, 0.125594)}
CAL12_MACRO = {"scenario": 0.119950, "survey_style": 0.150228}  # Direct-12 DECISION_BRIEF.md
COND_E1N2 = {("scenario", "condition_Formal"): -0.245, ("survey_style", "condition_Formal"): -0.274,
             ("scenario", "condition_core5"): -0.229, ("survey_style", "condition_core5"): -0.011}  # outlier REPORT.md
STYLE_MEDIANS = {"condition_core5": 0.753, "condition_Formal": 0.484}  # outlier REPORT.md section 4
ANGER_BANDS = [3.702, 3.479, 3.192]  # human-anger DECISION_BRIEF.md
CM01_BRIEF = {("Negative Avoidant × Hostile", "Qwen"): 0.502, ("Negative Avoidant × Hostile", "Llama"): -0.752,
              ("Negative Avoidant × Hostile", "Gemma"): -0.311, ("Charismatic × Hostile", "Qwen"): 0.738,
              ("Charismatic × Hostile", "Llama"): -0.526, ("Charismatic × Hostile", "Gemma"): 0.512,
              ("Flirty × Hostile", "Qwen"): 0.805, ("Flirty × Hostile", "Llama"): 0.690, ("Flirty × Hostile", "Gemma"): 0.760,
              ("Nurturing × Hostile", "Qwen"): -0.522, ("Nurturing × Hostile", "Llama"): -0.944,
              ("Nurturing × Hostile", "Gemma"): -0.862, ("Adventurous × Avoidant", "Qwen"): -0.746,
              ("Adventurous × Avoidant", "Llama"): 0.106, ("Adventurous × Avoidant", "Gemma"): 0.121,
              ("Charismatic × Gregarious", "Qwen"): 0.650, ("Charismatic × Gregarious", "Llama"): 0.220,
              ("Charismatic × Gregarious", "Gemma"): 0.264}  # PHG-CM01 DECISION_BRIEF.md
CROSS_BRIEF = {("Negative Avoidant – Hostile", "Qwen", "raw"): 0.581, ("Negative Avoidant – Hostile", "Llama", "raw"): -0.706,
               ("Negative Avoidant – Hostile", "Gemma", "raw"): -0.245, ("Nurturing – Hostile", "Qwen", "raw"): -0.476,
               ("Nurturing – Hostile", "Llama", "raw"): -0.900, ("Nurturing – Hostile", "Gemma", "raw"): -0.810,
               ("Negative Avoidant – Hostile", "Qwen", "conditioned on five styles"): 0.071,
               ("Negative Avoidant – Hostile", "Llama", "conditioned on five styles"): 0.118,
               ("Negative Avoidant – Hostile", "Gemma", "conditioned on five styles"): 0.112,
               ("Nurturing – Hostile", "Qwen", "conditioned on five styles"): -0.699,
               ("Nurturing – Hostile", "Llama", "conditioned on five styles"): -0.879,
               ("Nurturing – Hostile", "Gemma", "conditioned on five styles"): -0.850}  # cross-model DECISION_BRIEF.md
CONGRUENCE = {("Qwen_F1", "Llama_F1"): None, ("Qwen_F1", "Gemma_F3"): 0.772}  # CM01 REPORT.md (+.772)


def _brief(L: Ledger, cid: str, desc: str, quoted: float, value: float, sec: str):
    """Compare a 3-decimal value quoted in a frozen brief with its CSV value.

    Within rounding (0.0005): PASS. Off by less than one unit in the third
    decimal: NOTE (the brief rounds differently; the CSV value is used).
    Anything larger stays a FAIL.
    """
    d = abs(value - quoted)
    if d <= 5e-4:
        L.add(cid, "CHECKED", desc, quoted, value, tol=5e-4, section=sec)
    elif d < 1e-3:
        L.add(cid, "CHECKED", desc, quoted, value, tol=5e-4, section=sec, status="NOTE",
              note=f"frozen brief rounds to {quoted:+.3f}; CSV value {value:+.6f} is used")
    else:
        L.add(cid, "CHECKED", desc, quoted, value, tol=5e-4, section=sec)


def snapshot_checks(L: Ledger, section: str, keys=None, reproduction=False):
    for r in S.verify_snapshot():
        if keys and r["key"] not in keys:
            continue
        L.add(f"hash:{r['key']}", "HASH-ONLY", "snapshot file matches recorded SHA-256", True, r["ok"], section=section)
    if reproduction:
        for r in S.verify_against_evidence():
            if keys and r["key"] not in keys:
                continue
            L.add(f"evidence:{r['key']}", "HASH-ONLY", "re-derived from packaged evidence (original Git provenance retained)", True, r["ok"],
                  section=section, note=r.get("note", ""))


def planned_source_checks(L: Ledger, section: str, keys, inventory: pd.DataFrame):
    inv = inventory.drop_duplicates("source_key").set_index("source_key")
    for k in keys:
        src = S.PLANNED[k]
        ok = None
        if S.evidence_available(src.commit, src.path):
            ok = S.sha256(S.evidence_bytes(src.commit, src.path)) == S.evidence_record(src.commit, src.path)["package_sha256"]
        L.add(f"planned:{k}", "HASH-ONLY", f"pinned source present ({src.commit}:{src.path.split('/')[-1]})", True, ok,
              section=section, note="" if ok is not None else "deliberately not packaged; see EXCLUSIONS.csv")


def section4(L: Ledger, reproduction: bool = False):
    sec = "4"
    p = A.pairs325()
    L.add("4.qwen650", "RECOMPUTED", "650 Qwen pair correlations from 275x26 persona scores vs saved", 0.0,
          float(max(np.abs(p.scenario - p.scenario_saved).max(), np.abs(p.survey - p.survey_saved).max())), tol=1e-12, section=sec)
    L.add("4.screen", "RECOMPUTED", "frozen screen (|h|>=.25, |q|>=.30, tol .15) reproduces frozen groups", True,
          bool((p.group_frozen == p.group_recomputed).all()), section=sec)
    L.add("4.n_reversals", "RECOMPUTED", "number of consistent reversals", 13, int((p.group_recomputed == "consistent_reversal").sum()), section=sec)
    L.add("4.n_agree", "RECOMPUTED", "number of close agreements", 6, int((p.group_recomputed == "close_agreement").sum()), section=sec)
    L.add("4.human_sources", "CHECKED", "human r: Direct-30 B relationships.csv vs outlier all_pair_discrepancies.csv (max |diff|)",
          0.0, float(np.abs(p.human - p.human_od).max()), tol=1e-12, section=sec)
    L.add("4.human_dup", "CHECKED", "human r duplicated identically in scenario and survey rows", 0.0,
          float(np.abs(p.human - p.human_survey_copy).max()), tol=0, section=sec)
    fp = S.csv("d30b_fingerprints").set_index("source")
    for fmt, col in [("scenario", "scenario"), ("survey_style", "survey")]:
        L.add(f"4.fp_pearson.{fmt}", "RECOMPUTED", f"fingerprint Pearson (325 pairs), {fmt}", float(fp.loc[fmt, "Pearson"]),
              stats.pearson(p.human, p[col]), tol=1e-12, section=sec)
        L.add(f"4.fp_sign.{fmt}", "RECOMPUTED", f"sign agreement (325 pairs), {fmt}", float(fp.loc[fmt, "sign_agreement"]),
              float((np.sign(p.human) == np.sign(p[col])).mean()), tol=1e-12, section=sec)
    fr = S.csv("d30b_facet_results")
    for fmt in A.FORMATS:
        L.add(f"4.macroR2.{fmt}", "CHECKED", f"macro R2 = mean of 26 saved facet R2 vs REPORT.md, {fmt}", MACRO_R2[fmt],
              float(fr[(fr.condition == "model") & (fr.source == fmt)].R2.mean()), tol=5e-7, section=sec)
    L.add("4.macroR2.human", "CHECKED", "human-reference macro R2 vs REPORT.md", MACRO_R2["human"],
          float(fr[(fr.condition == "human_reference") & (fr.source == "scenario")].R2.mean()), tol=5e-7, section=sec)
    mac = A.macro_intervals()
    for fam, ref in [("Respondents; fits fixed", MACRO_RESP), ("Questions; conditional extraction", MACRO_QUES)]:
        for fmt in A.FORMATS:
            row = mac[(mac.family == fam) & (mac.source == fmt)].iloc[0]
            L.add(f"4.macro_int.{fam.split(';')[0].lower()}.{fmt}", "CHECKED", f"98.75% macro interval ({fam}), {fmt}: lower",
                  ref[fmt][0], float(row.lower), tol=5e-7, section=sec)
            L.add(f"4.macro_int.{fam.split(';')[0].lower()}.{fmt}.u", "CHECKED", f"98.75% macro interval ({fam}), {fmt}: upper",
                  ref[fmt][1], float(row.upper), tol=5e-7, section=sec)
    # Calibration (Direct-12, nine facets)
    c = A.calibration()
    L.add("4.cal.quadratic", "RECOMPUTED", "SSE(k) quadratic from k=0,1,λ predicts saved facet-λ R2 (max |diff|)", 0.0,
          float((c.R2_facet_saved - c.R2_facet_predicted).abs().max()), tol=1e-9, section=sec)
    cur = S.csv("cal12_curve")
    for fmt in A.FORMATS:
        cc = c[c.source == fmt]
        ks = cur[cur.source == fmt].multiplier.to_numpy()
        mac_k = np.mean([stats.r2_curve(np.array([r.a, r.b, r.c]), r.SST, ks) for r in cc.itertuples()], axis=0)
        L.add(f"4.cal.curve.{fmt}", "RECOMPUTED", f"macro R2(k) curve vs saved sensitivity_curve.csv (max |diff|), {fmt}", 0.0,
              float(np.abs(mac_k - cur[cur.source == fmt].macro_R2.to_numpy()).max()), tol=1e-9, section=sec)
        L.add(f"4.cal.lambda.{fmt}", "RECOMPUTED", f"macro R2 at common λ vs DECISION_BRIEF.md, {fmt}", CAL12_MACRO[fmt],
              float(cc.R2_common.mean()), tol=5e-7, section=sec)
    t = S.csv("cal12_test")
    t = t[t.facet != "MACRO"]
    sd = t[t.condition.isin(["original", "common_calibrated", "facet_calibrated_exploratory"])].groupby(["source", "facet"]).S.agg(lambda s: s.max() - s.min())
    L.add("4.cal.ordering", "CHECKED", "ordering S identical across original and calibrated conditions (max spread)", 0.0,
          float(sd.max()), tol=1e-12, section=sec)
    # Human recomputation needs the raw OSF file.
    if reproduction and human.raw_available():
        out = human.reference_correlations(A.codes())
        stage = S.jsonfile("d30b_point_stage")["split"]
        L.add("4.human.partition", "RECOMPUTED", "split membership hashes match POINT_ESTIMATE_STAGE.json", True,
              out["partition_sha256"] == stage["partition_sha256"], section=sec)
        L.add("4.human.transform", "RECOMPUTED", "reference transform hash matches", stage["transformed_sha256"]["reference"],
              out["reference_transformed_sha256"], section=sec)
        cs = list(A.codes())
        R = out["R"]
        diff = max(abs(R[cs.index(a), cs.index(b)] - h) for a, b, h in zip(p.left, p.right, p.human))
        L.add("4.human.R", "RECOMPUTED", "325 human correlations recomputed from raw responses", 0.0, float(diff), tol=1e-12, section=sec)
    else:
        L.add("4.human.R", "RECOMPUTED", "325 human correlations recomputed from raw responses", 0.0, None, section=sec,
              note="raw IPIP300.dat not present (REPRODUCTION mode + download_ipip.py required)" if reproduction else "READER mode")
    _domain_block_checks(L, sec)
    _averaging_checks(L, sec)
    _rescaling_checks(L, sec)
    _ordinary_and_fit_checks(L, sec)
    if reproduction:
        _bootstrap_matrix_check(L, sec)


def _domain_block_checks(L: Ledger, sec: str):
    """Domain averages (4.2): recompute from relationships.csv through a separate matrix-mask path."""
    rel = S.csv("d30b_relationships")
    codes = list(A.ordered_codes())
    ix = {c: k for k, c in enumerate(codes)}
    mats = {}
    for src, key in [("scenario", "human_reference"), ("scenario", "model_persona"), ("survey_style", "model_persona")]:
        Mx = np.full((26, 26), np.nan)
        for r in rel[rel.source == src].itertuples():
            i, j = ix[r.left], ix[r.right]
            Mx[max(i, j), min(i, j)] = getattr(r, key)
        mats[(src, key)] = Mx
    dom = np.array([c[0] for c in codes])
    blocks = A.domain_blocks().set_index(["row", "col"])
    worst, total, count_ok = 0.0, 0, True
    for (di, dj), b in blocks.iterrows():
        mask = np.zeros((26, 26), bool)
        mask[np.ix_(dom == di, dom == dj)] = True
        mask |= mask.T
        mask &= np.tril(np.ones((26, 26), bool), -1)
        ni, nj = int((dom == di).sum()), int((dom == dj).sum())
        expect = ni * (ni - 1) // 2 if di == dj else ni * nj
        count_ok &= int(mask.sum()) == expect == int(b.n_pairs)
        total += int(mask.sum())
        for col, k in [("human", ("scenario", "human_reference")), ("scenario", ("scenario", "model_persona")),
                       ("survey", ("survey_style", "model_persona"))]:
            worst = max(worst, abs(np.nanmean(mats[k][mask]) - b[col]))
    L.add("4.domain.means", "RECOMPUTED", "4.2 domain averages: 15 blocks x 3 sources recomputed from the 325 saved pairs (max |diff|)",
          0.0, float(worst), tol=1e-12, section=sec)
    L.add("4.domain.counts", "RECOMPUTED", "4.2 domain averages: pair counts per block match domain sizes", True, bool(count_ok), section=sec)
    L.add("4.domain.total", "RECOMPUTED", "4.2 domain averages: pair counts sum to 325", 325, total, section=sec)


# Expected values supplied with iteration 5 (tolerance 0.005).
ORDINARY_BLOCKS = {("N", "N"): (0.89, 0.86), ("E", "N"): (0.56, 0.64), ("A", "N"): (-0.31, -0.58), ("A", "A"): (0.47, 0.48),
                   ("C", "A"): (0.08, 0.28)}
ORDINARY_PATTERN = (0.39, 0.33)
ORDINARY_E1N2_FROZEN = (0.833, 0.804)  # outlier REPORT.md, ordinary-role subset
FACET_FIT = {"O6": (0.23, 0.02, 0.17), "E4": (0.22, -0.06, 0.40), "A6": (0.40, 0.27, 0.41), "A5": (0.20, 0.60, 0.65),
             "C2": (0.41, 0.46, 0.00)}


def _ordinary_and_fit_checks(L: Ledger, sec: str):
    """4.2 ordinary-roles toggle and 4.3 facet fit: recomputed from snapshot persona scores and saved pairs."""
    ids, Q = A.profiles()
    keep = A.ordinary_mask()
    L.add("4.ord.n", "RECOMPUTED", "frozen ordinary-role subset size (persona_classification.csv)", 130, int(keep.sum()), section=sec)
    po = A.pairs325_ordinary()
    blocks = A.domain_blocks_ordinary().set_index(["row", "col"])
    for (di, dj), (es, ev) in ORDINARY_BLOCKS.items():
        b = blocks.loc[(di, dj)]
        L.add(f"4.ord.{di}{dj}.scenario", "RECOMPUTED", f"ordinary roles, {A.DOMAIN_NAME[di]}–{A.DOMAIN_NAME[dj]} mean r, scenario",
              es, float(b.scenario), tol=0.005, section=sec)
        L.add(f"4.ord.{di}{dj}.survey", "RECOMPUTED", f"ordinary roles, {A.DOMAIN_NAME[di]}–{A.DOMAIN_NAME[dj]} mean r, survey-style",
              ev, float(b.survey), tol=0.005, section=sec)
    for col, e in zip(["scenario", "survey"], ORDINARY_PATTERN):
        L.add(f"4.ord.pattern.{col}", "RECOMPUTED", f"ordinary roles: pattern agreement with people over 325 pairs, {col}",
              e, stats.pearson(po.human, po[col]), tol=0.005, section=sec)
    sv = A.saved_composition()
    e1n2 = po.set_index("pair").loc["E1__N2"]
    for col, fmt, e in [("scenario", "scenario", ORDINARY_E1N2_FROZEN[0]), ("survey", "survey_style", ORDINARY_E1N2_FROZEN[1])]:
        saved = float(sv[(sv.condition == "ordinary_human_roles") & (sv.source == fmt)].Pearson.iloc[0])
        L.add(f"4.ord.E1N2.{col}", "RECOMPUTED", f"ordinary roles: E1–N2 recomputed vs frozen composition_style_sensitivity, {col}",
              saved, float(e1n2[col]), tol=1e-12, section=sec)
        L.add(f"4.ord.E1N2.{col}.report", "RECOMPUTED", f"ordinary roles: E1–N2 vs frozen REPORT.md value, {col}",
              e, float(e1n2[col]), tol=5e-4, section=sec)
    _rank_checks(L, sec)


def appendix_e(L: Ledger):
    """E.2 facet fit (moved from 4.3 in iteration 5b): checks unchanged, ledger section E."""
    sec = "E"
    # Facet fit: independent path from relationships.csv (full 26 x 26 matrices).
    rel = S.csv("d30b_relationships")
    fit = A.facet_fit().set_index("facet")
    worst = 0.0
    for src, key, col in [("scenario", "human_reference", "human"), ("scenario", "model_persona", "scenario"),
                          ("survey_style", "model_persona", "survey")]:
        r = rel[rel.source == src]
        for c in A.ordered_codes():
            m = ((r.left == c) | (r.right == c)) & (r.left.str[0] == r.right.str[0])
            worst = max(worst, abs(r[m][key].mean() - fit.loc[c, col]))
    L.add("4.fit.all", "RECOMPUTED", "E.2 facet fit: 26 facets x 3 sources recomputed from relationships.csv (max |diff|)", 0.0,
          float(worst), tol=1e-12, section=sec)
    for c, (eh, es, ev) in FACET_FIT.items():
        for col, e in [("human", eh), ("scenario", es), ("survey", ev)]:
            L.add(f"4.fit.{c}.{col}", "RECOMPUTED", f"E.2 facet fit, {A.name(c)}, {col}", e, float(fit.loc[c, col]), tol=0.005,
                  section=sec)


RANK_FIT_R2 = {"scenario": 0.66, "survey": 0.57, "human": 0.84}  # supplied with iteration 5b (tolerance .01)


def _rank_checks(L: Ledger, sec: str):
    """4.4 outline: Spearman between within-domain fit (E.2) and held-out R² (4.3), per source."""
    from scipy.stats import spearmanr
    fit = A.facet_fit().set_index("facet")
    r2 = A.r2_table().set_index("facet").loc[fit.index]
    for col, r2col, label in [("scenario", "R2_scenario", "Qwen fit vs Qwen R², scenario"),
                              ("survey", "R2_survey_style", "Qwen fit vs Qwen R², survey-style"),
                              ("human", "R2_human", "people fit vs people-benchmark R²")]:
        L.add(f"4.rank.{col}", "RECOMPUTED", f"Spearman over 26 facets: {label}", RANK_FIT_R2[col],
              float(spearmanr(fit[col], r2[r2col])[0]), tol=0.01, section=sec)


def _averaging_checks(L: Ledger, sec: str):
    """Iteration 6 display: Qwen r averaged over the two prompt formats (headline, 4.2). Independent path from
    relationships.csv saved values; the frozen reversal / close-match classes are unchanged."""
    rel = S.csv("d30b_relationships")
    w = rel.pivot_table(index=["left", "right"], columns="source", values=["human_reference", "model_persona"], sort=False)
    h = w[("human_reference", "scenario")].to_numpy()
    q = (w[("model_persona", "scenario")].to_numpy() + w[("model_persona", "survey_style")].to_numpy()) / 2
    p = A.pairs325()
    L.add("4.avg.pairs", "RECOMPUTED", "Qwen averaged r, 325 pairs: displayed vs saved scenario/survey mean (max |diff|)", 0.0,
          float(np.abs(p.set_index(["left", "right"]).loc[w.index, "qwen"].to_numpy() - q).max()), tol=1e-12, section=sec)
    hc, qc = h - h.mean(), q - q.mean()
    pattern = float((hc @ qc) / np.sqrt((hc @ hc) * (qc @ qc)))
    sign = float((np.sign(h) == np.sign(q)).mean())
    pa, sa = stats.pearson(p.human, p.qwen), float((np.sign(p.human) == np.sign(p.qwen)).mean())
    L.add("4.avg.pattern", "RECOMPUTED", "headline: averaged pattern agreement over 325 pairs (recorded value +0.4485)", pattern, pa,
          tol=1e-12, section=sec)
    L.add("4.avg.sign", "RECOMPUTED", "headline: averaged same-direction share over 325 pairs (recorded value 64.6%)", sign, sa,
          tol=1e-12, section=sec)
    L.add("4.avg.frozen_groups", "RECOMPUTED", "13 reversals and 6 close matches unchanged by averaging (frozen two-format screen)", True,
          bool((p.group_frozen == p.group_recomputed).all() and (p.group_frozen == "consistent_reversal").sum() == 13), section=sec)
    b = A.domain_blocks()
    L.add("4.avg.blocks", "RECOMPUTED", "domain averages: Qwen averaged block = mean of scenario and survey blocks (max |diff|)", 0.0,
          float(np.abs(b.qwen - (b.scenario + b.survey) / 2).max()), tol=1e-12, section=sec)
    mac = A.macro_intervals().set_index(["family", "source"])
    for fmt, (lo, hi) in [("scenario", (-0.03, 0.11)), ("survey_style", (-0.02, 0.13))]:
        r = mac.loc[("Questions; conditional extraction", fmt)]
        L.add(f"4.outline.extr.{fmt}", "CHECKED", f"4.4 outline: extraction-prompt interval for average R², {fmt}, lower (2 d.p.)",
              lo, float(r.lower), tol=0.005, section=sec)
        L.add(f"4.outline.extr.{fmt}.u", "CHECKED", f"4.4 outline: extraction-prompt interval for average R², {fmt}, upper (2 d.p.)",
              hi, float(r.upper), tol=0.005, section=sec)


# Values quoted in the rescaling DECISION_BRIEF.md (677d4f2).
RESCALE_BRIEF = {"scenario": dict(rescaled=0.254224, multiplier=0.529452, q=(0.232485, 0.269422), improved=20),
                 "survey_style": dict(rescaled=0.252502, multiplier=0.549380, q=(0.227522, 0.269177), improved=19)}


def _rescaling_checks(L: Ledger, sec: str):
    """Iteration 7: Direct-30 B rescaling aggregates (codex/direct30-calibration-20261102 @ 677d4f2)."""
    fc = S.csv("cal30_facets")
    fr = S.csv("d30b_facet_results")
    brief = S.path("cal30_brief").read_text()
    worst = 0.0
    for fmt in A.FORMATS:
        a = fc[fc.source == fmt].set_index("facet").original_R2
        b = fr[(fr.condition == "model") & (fr.source == fmt)].set_index("facet").R2.loc[a.index]
        worst = max(worst, float((a - b).abs().max()))
    L.add("4.rescale.asmeasured", "CHECKED", "as-measured R² per facet in facet_comparison.csv vs saved Direct-30 B (52 cells, max |diff|)",
          0.0, worst, tol=1e-9, section=sec)
    t = A.rescaled_table()
    mac = A.rescaled_macro().set_index("source")
    for fmt, e in RESCALE_BRIEF.items():
        g = t[t.source == fmt]
        L.add(f"4.rescale.macro.{fmt}", "RECOMPUTED", f"macro mean of the 26 per-facet rescaled R² vs DECISION_BRIEF.md, {fmt}",
              e["rescaled"], float(g.rescaled.mean()), tol=5e-7, section=sec)
        L.add(f"4.rescale.improved.{fmt}", "RECOMPUTED", f"facets improved by rescaling (rescaled R² > as measured), {fmt}",
              e["improved"], int((g.rescaled > g.original).sum()), section=sec)
        mult = g.multiplier.unique()
        L.add(f"4.rescale.multiplier.{fmt}", "CHECKED", f"common multiplier (one per format) vs DECISION_BRIEF.md, {fmt}",
              e["multiplier"], float(mult[0]) if len(mult) == 1 else None, tol=5e-7, section=sec,
              note="" if len(mult) == 1 else "multiplier not unique per format")
        L.add(f"4.rescale.q_lo.{fmt}", "CHECKED", f"macro question-resampling 95% interval, lower, vs DECISION_BRIEF.md, {fmt}",
              e["q"][0], float(mac.loc[fmt, "q_lo"]), tol=5e-7, section=sec)
        L.add(f"4.rescale.q_hi.{fmt}", "CHECKED", f"macro question-resampling 95% interval, upper, vs DECISION_BRIEF.md, {fmt}",
              e["q"][1], float(mac.loc[fmt, "q_hi"]), tol=5e-7, section=sec)
    for fmt, e in RESCALE_BRIEF.items():
        quoted = all(f"{v:.6f}".lstrip("0") in brief or f"{v:.6f}" in brief for v in (e["rescaled"], e["multiplier"]) + e["q"])
        L.add(f"4.rescale.brief.{fmt}", "CHECKED", f"expected values appear verbatim in the snapshot DECISION_BRIEF.md, {fmt}", True,
              quoted, section=sec)
    e4 = t[(t.source == "survey_style") & (t.facet == "E4")].rescaled.iloc[0]
    L.add("4.rescale.E4.survey", "CHECKED", "Activity Level (survey) remains negative after rescaling (brief: −0.106314)", -0.106314,
          float(e4), tol=5e-7, section=sec)
    _interval_level_checks(L, sec)


def _interval_level_checks(L: Ledger, sec: str):
    """Iteration 8: 95% intervals in Figure E.6. The calibration package's question-resampling intervals for the
    as-measured R² must match the frozen Direct-30 B extraction intervals (same draws) before they are shown side by side."""
    qi = S.csv("cal30_qint")
    ei = S.csv("d30b_extr_int")
    worst, n = 0.0, 0
    for fmt in A.FORMATS:
        a = qi[(qi.source == fmt) & (qi.metric == "original_R2") & (qi.facet != "MACRO")].set_index("facet")
        b = ei[(ei.source == fmt) & (ei.metric == "R2")].set_index("facet").loc[a.index]
        worst = max(worst, float((a.lower - b.lower).abs().max()), float((a.upper - b.upper).abs().max()))
        n += len(a)
    L.add("4.ci95.facets", "CHECKED", f"per-facet as-measured 95% question intervals: calibration package vs frozen Direct-30 B "
          f"extraction intervals ({n} facets x 2 bounds, max |diff|)", 0.0, worst, tol=1e-9, section=sec)
    me = S.csv("d30b_macro_extr")
    for fmt in A.FORMATS:
        a = qi[(qi.source == fmt) & (qi.metric == "original_R2") & (qi.facet == "MACRO")].iloc[0]
        b = me[(me.source == fmt) & (me.metric == "R2")].iloc[0]
        L.add(f"4.ci95.macro_median.{fmt}", "CHECKED", f"as-measured average R²: median of the calibration package's 95% question "
              f"draws vs median of the frozen 98.75% extraction family (same draws), {fmt}", float(b["median"]), float(a["median"]),
              tol=1e-9, section=sec)
        L.add(f"4.ci95.level.{fmt}", "CHECKED", f"as-measured average R² interval in the 4.3 note is the 95% level, {fmt}", 0.95,
              float(a.confidence), tol=1e-12, section=sec)
    _scenario_main_checks(L, sec)


def _scenario_main_checks(L: Ledger, sec: str):
    """Iteration 9: the main text shows scenario prompts only. Recompute the values shown or quoted from the saved data."""
    p = A.pairs325()
    fp = S.csv("d30b_fingerprints").set_index("source")
    L.add("4.main.pattern", "RECOMPUTED", "Figure 4.1 note: scenario pattern agreement over 325 pairs, recomputed vs saved fingerprint",
          float(fp.loc["scenario", "Pearson"]), stats.pearson(p.human, p.scenario), tol=1e-9, section=sec)
    L.add("4.main.sign", "RECOMPUTED", "summary outline: same direction in 67% of pairs (scenario, 2 d.p.)", 0.67,
          float((np.sign(p.human) == np.sign(p.scenario)).mean()), tol=0.005, section=sec)
    L.add("4.main.outline.pattern", "CHECKED", "summary outline: pattern agreement .44 (scenario, 2 d.p.)", 0.44,
          float(fp.loc["scenario", "Pearson"]), tol=0.005, section=sec)
    m = A.rescaled_macro().set_index("source").loc["scenario"]
    L.add("4.main.outline.r2", "CHECKED", "summary outline: average R² .05 as measured (scenario, 2 d.p.)", 0.05, float(m.as_measured),
          tol=0.005, section=sec)
    L.add("4.main.outline.r2cal", "CHECKED", "summary outline: average R² .25 after rescaling (scenario, 2 d.p.)", 0.25, float(m.rescaled),
          tol=0.005, section=sec)
    # Iteration 30: Figure 4.1 outlines the 13 frozen reversals (both mirrored cells).
    from . import figures as F_
    boxes = [sh for sh in F_.correlation_matrices().layout.shapes if sh.name == "reversal"]
    oc = list(A.ordered_codes())
    want = {c for a, b_ in zip(p.left[p.group_frozen == "consistent_reversal"], p.right[p.group_frozen == "consistent_reversal"])
            for c in [(oc.index(b_), oc.index(a)), (oc.index(a), oc.index(b_))]}
    L.add("4.2.reversal_boxes", "RECOMPUTED", "Figure 4.2: outlined cells are exactly the 13 frozen reversals, both mirrored cells (26)",
          True, len(boxes) == 26 and {(round(sh.x0 + 0.5), round(sh.y0 + 0.5)) for sh in boxes} == want, section=sec)
    b = A.domain_blocks()
    L.add("4.main.blocks", "RECOMPUTED", "4.2 domain views: Qwen − People block = scenario block − people block (max |diff|)", 0.0,
          float(np.abs(b.diff_scenario - (b.scenario - b.human)).max()), tol=1e-12, section=sec)


# Section 3.1 (was 3.2) values supplied with iteration 9 (tolerance .005).
FORMAT_AGREEMENT = dict(median=0.941, minimum=0.456, E4=0.69, C4=0.71, pairs=0.872, sign=0.831, scen_higher=13)


def section3_formats(L: Ledger):
    """3.2: agreement between the scenario and survey-style extractions, recomputed from the saved 275 x 26 profiles."""
    sec = "3"
    d = A.format_agreement().set_index("facet")
    e = FORMAT_AGREEMENT
    L.add("3.fmt.median", "RECOMPUTED", "3.2: median per-facet r between methods (275 characters)", e["median"], float(d.r.median()),
          tol=0.005, section=sec)
    L.add("3.fmt.min", "RECOMPUTED", "3.2: lowest per-facet r between methods", e["minimum"], float(d.r.min()), tol=0.005, section=sec)
    L.add("3.fmt.min_facet", "RECOMPUTED", "3.2: the lowest facet is Orderliness (C2)", "C2", str(d.r.idxmin()), section=sec)
    L.add("3.fmt.E4", "RECOMPUTED", "3.2: Activity Level r between methods", e["E4"], float(d.r["E4"]), tol=0.005, section=sec)
    L.add("3.fmt.C4", "RECOMPUTED", "3.2: Achievement-Striving r between methods", e["C4"], float(d.r["C4"]), tol=0.005, section=sec)
    # Independent path for the per-facet values: numpy corrcoef on the saved profile table.
    P = S.csv("d30b_profiles")
    a = P[P.source == "scenario"].set_index("persona").sort_index()
    b = P[P.source == "survey_style"].set_index("persona").sort_index()
    alt = {c: float(np.corrcoef(a[c], b[c])[0, 1]) for c in d.index}
    L.add("3.fmt.independent", "RECOMPUTED", "3.2: per-facet r, two computation paths (max |diff|)", 0.0,
          max(abs(alt[c] - d.r[c]) for c in d.index), tol=1e-12, section=sec)
    pr, ps = A.format_pair_agreement()
    L.add("3.fmt.pairs", "RECOMPUTED", "3.2: agreement of the 325 pair correlations between methods (Pearson)", e["pairs"], pr,
          tol=0.005, section=sec)
    L.add("3.fmt.sign", "RECOMPUTED", "3.2: share of the 325 pairs with the same sign in both methods", e["sign"], ps, tol=0.005, section=sec)
    t = A.r2_table()
    L.add("3.fmt.r2_scen_higher", "RECOMPUTED", "3.2: facets with higher R² for scenario than survey-style (of 26)", e["scen_higher"],
          int((t.R2_scenario > t.R2_survey_style).sum()), section=sec)
    fp = S.csv("d30b_fingerprints").set_index("source")
    m = A.rescaled_macro().set_index("source")
    for k, v, obs in [("pattern.scenario", 0.44, fp.loc["scenario", "Pearson"]), ("pattern.survey", 0.42, fp.loc["survey_style", "Pearson"]),
                      ("r2.scenario", 0.05, m.loc["scenario", "as_measured"]), ("r2.survey", 0.08, m.loc["survey_style", "as_measured"]),
                      ("r2cal.scenario", 0.25, m.loc["scenario", "rescaled"]), ("r2cal.survey", 0.25, m.loc["survey_style", "rescaled"])]:
        L.add(f"3.fmt.outline.{k}", "CHECKED", f"3.2 outline value {v:.2f} ({k}, 2 d.p.)", v, float(obs), tol=0.005, section=sec)


def _bootstrap_matrix_check(L, sec, draws=2000, seed=20261101):
    """Independent persona bootstrap of the 19 screened Qwen pairs vs saved marginal intervals."""
    ids, Q = A.profiles()
    cs = list(A.codes())
    unc = S.csv("od_corr_unc")
    scr = S.csv("od_screened")
    rng = np.random.default_rng(seed)
    n = len(ids)
    ix = rng.integers(0, n, (draws, n))
    worst = 0.0
    for fmt, fam in [("scenario", "scenario"), ("survey_style", "survey_style")]:
        Rb = np.array([stats.corr_matrix(Q[fmt][i]) for i in ix])
        for pr in scr.pair:
            a, b = pr.split("__")
            v = Rb[:, cs.index(a), cs.index(b)]
            lo, hi = np.percentile(v, [2.5, 97.5])
            s = unc[(unc.family == fam) & (unc.pair == pr)].iloc[0]
            worst = max(worst, abs(lo - s.lower), abs(hi - s.upper))
    L.add("4.boot.intervals", "CHECKED", "independent 2,000-draw persona bootstrap: 95% bounds of 19 screened pairs vs saved (max |diff|)",
          0.0, float(worst), tol=0.03, section=sec, note="different random stream; agreement expected only to Monte Carlo error")


def section5(L: Ledger, reproduction: bool = False):
    sec = "5"
    p = A.pairs325().set_index("pair")
    for fmt, col in [("scenario", "scenario"), ("survey_style", "survey")]:
        x, y = A.e1n2(fmt)
        r = stats.pearson(x, y)
        L.add(f"5.E1N2.{fmt}", "RECOMPUTED", f"Qwen E1–N2 r, {fmt} (target from brief)", QWEN_E1N2[fmt], r, tol=5e-5, section=sec)
        L.add(f"5.E1N2.exact.{fmt}", "RECOMPUTED", f"Qwen E1–N2 r vs saved relationships.csv, {fmt}",
              float(p.loc["E1__N2", f"{col}_saved"]), r, tol=1e-12, section=sec)
    L.add("5.E1N2.human", "CHECKED", "human E1–N2 r (saved; raw data not recomputed here)", HUMAN_E1N2, float(p.loc["E1__N2", "human"]),
          tol=5e-5, section=sec, note="RECOMPUTED only with raw OSF file")
    L.add("5.E1N2.human.anger", "CHECKED", "human E1–N2 r: Direct-30 B vs human-anger reproduction", HUMAN_E1N2_ANGER_STUDY,
          float(p.loc["E1__N2", "human"]), tol=1e-11, section=sec)
    # (a) influence
    loo = A.loo_e1n2()
    od = S.csv("od_loo")
    for fmt in A.FORMATS:
        s = od[(od.pair == "E1__N2") & (od.source == fmt)].iloc[0]
        d = loo[loo.source == fmt]
        L.add(f"5a.loo.min.{fmt}", "RECOMPUTED", f"E1–N2 LOO minimum, {fmt}", float(s.minimum), float(d.r_without.min()), tol=1e-12, section=sec)
        L.add(f"5a.loo.max.{fmt}", "RECOMPUTED", f"E1–N2 LOO maximum, {fmt}", float(s.maximum), float(d.r_without.max()), tol=1e-12, section=sec)
        L.add(f"5a.loo.who.{fmt}", "RECOMPUTED", f"most influential persona, {fmt}", s.most_influential_persona,
              d.loc[d.change.abs().idxmax(), "persona"], section=sec)
    _, Q = A.profiles()
    cs = list(A.codes())
    changes = 0
    for pr in p.index[p.group_frozen == "consistent_reversal"]:
        a, b = pr.split("__")
        for fmt in A.FORMATS:
            x, y = Q[fmt][:, cs.index(a)], Q[fmt][:, cs.index(b)]
            changes += int((np.sign(stats.leave_one_out(x, y)) != np.sign(stats.pearson(x, y))).sum())
    L.add("5a.loo.signs", "RECOMPUTED", "single deletions changing a reversal's sign (13 pairs × 2 formats × 275)", 0, changes, section=sec)
    g = A.group_exclusions_e1n2()
    sv = A.saved_composition()
    m = g.merge(sv[["condition", "source", "Pearson"]], on=["condition", "source"], how="left")
    L.add("5a.groups.n", "RECOMPUTED", "group-exclusion conditions matched to saved (15 groups + ordinary subset, × 2)", 32,
          int(m.Pearson.notna().sum()), section=sec)
    L.add("5a.groups.r", "RECOMPUTED", "E1–N2 r after each exclusion vs saved (max |diff|)", 0.0,
          float((m.r - m.Pearson).abs().max()), tol=1e-12, section=sec)
    # (b) style conditioning
    St = A.styles()
    for fmt in A.FORMATS:
        x, y = A.e1n2(fmt)
        for cond, C in [("condition_Formal", St[:, :1]), ("condition_core5", St)]:
            r = stats.partial_corr(x, y, C)
            saved = sv[(sv.condition == cond) & (sv.source == fmt)].Pearson.iloc[0]
            L.add(f"5b.{cond}.{fmt}", "RECOMPUTED", f"E1–N2 {cond} vs saved composition_style_sensitivity, {fmt}", float(saved), r,
                  tol=1e-10, section=sec)
            L.add(f"5b.{cond}.{fmt}.report", "RECOMPUTED", f"E1–N2 {cond} vs REPORT.md (3 d.p.), {fmt}", COND_E1N2[(fmt, cond)], r,
                  tol=5e-4, section=sec)
    sv_var = S.csv("od_style_var")
    worst = 0.0
    meds = {}
    for cond, C in [("condition_Formal", St[:, :1]), ("condition_core5", St)]:
        vals = []
        for fmt in A.FORMATS:
            for j, code in enumerate(cs):
                v = stats.variance_removed(Q[fmt][:, j], C)
                vals.append(v)
                s = sv_var[(sv_var.condition == cond) & (sv_var.source == fmt) & (sv_var.facet == code)].variance_removed.iloc[0]
                worst = max(worst, abs(v - s))
        meds[cond] = float(np.median(vals))
    L.add("5b.var_removed", "RECOMPUTED", "variance removed, 26 facets × 2 formats × 2 conditions vs saved (max |diff|)", 0.0, worst,
          tol=1e-10, section=sec)
    for cond, v in meds.items():
        L.add(f"5b.median.{cond}", "RECOMPUTED", f"median variance removed, {cond} vs REPORT.md", STYLE_MEDIANS[cond], v, tol=5e-4, section=sec)
    # (c) questionnaire
    it = A.item_wording()
    L.add("5c.items", "CHECKED", "ten items each for E1 and N2 in the frozen inventory", 20, len(it), section=sec)
    ai = A.anger_items()
    L.add("5c.all_negative", "CHECKED", "all ten Anger-keyed items correlate negatively with Friendliness", True,
          bool((ai.anger_keyed_r_E1 < 0).all()), section=sec)
    bins = S.csv("ha_bins")
    fine, broad = bins[bins.bin_kind == "fine"], bins[bins.bin_kind == "broad"]
    worst = 0.0
    for b in broad.itertuples():
        f = fine[(fine.lower_inclusive >= b.lower_inclusive) & (fine.upper_exclusive <= b.upper_exclusive)]
        worst = max(worst, abs((f.n * f.mean_friendliness).sum() / f.n.sum() - b.mean_friendliness))
        worst_n = abs(f.n.sum() - b.n)
    L.add("5c.bands.nest", "CHECKED", "broad Anger-band means equal n-weighted means of nested half-point bins", 0.0, worst, tol=1e-9, section=sec)
    L.add("5c.bands.total_n", "CHECKED", "band sizes sum to 117,259 respondents", 117259, int(broad.n.sum()), section=sec)
    for b, v in zip(broad.itertuples(), ANGER_BANDS):
        L.add(f"5c.band{b.bin}", "CHECKED", f"band {b.bin} mean Friendliness vs DECISION_BRIEF.md", v, float(b.mean_friendliness), tol=5e-4, section=sec)
    # (d) other models
    cm = A.cm01_table().set_index(["relationship", "model"]).r
    for k, v in CM01_BRIEF.items():
        _brief(L, f"5d.cm01.{k[0]}.{k[1]}", f"PHG-CM01 {k[0]}, {k[1]} vs DECISION_BRIEF.md (3 d.p.)", v, float(cm.loc[k]), sec)
    cr = A.cross_model_table().set_index(["relationship", "model", "view"]).adjusted_Pearson
    for k, v in CROSS_BRIEF.items():
        _brief(L, f"5d.cross.{k[0]}.{k[1]}.{k[2]}", f"cross-model {k[0]}, {k[1]}, {k[2]} vs DECISION_BRIEF/REPORT (3 d.p.)",
               v, float(cr.loc[k]), sec)
    fm = S.csv("cm01_matches")
    for fa, fb in [("Qwen_F1", "Llama_F1"), ("Qwen_F1", "Gemma_F3")]:
        saved = fm[(fm.method == "original_pattern") & (fm.factor_a == fa) & (fm.factor_b == fb)].signed_congruence.iloc[0]
        L.add(f"5d.congruence.{fa}.{fb}", "CHECKED", f"Tucker congruence {fa}/{fb} from 240 pattern loadings vs factor_matches.csv",
              float(saved), A.factor_congruence(fa, fb), tol=1e-9, section=sec)
    # C/T/F decomposition
    d = A.ctf_contributions()
    L.add("5.ctf.additive", "CHECKED", "projected + residual = Qwen r for C/T/F × 13 reversals × 2 formats (max |diff|)", 0.0,
          float((d.projected_additive_contribution + d.residual_additive_contribution - d.model_marginal_r).abs().max()), tol=1e-9, section=sec)
    rq = d.apply(lambda r: p.loc[r.pair, "scenario" if r.source == "scenario" else "survey"] if r.pair in p.index else np.nan, axis=1)
    L.add("5.ctf.model_r", "RECOMPUTED", "Qwen r in decomposition files vs recomputed from persona scores (max |diff|)", 0.0,
          float((rq - d.model_marginal_r).abs().max()), tol=1e-9, section=sec)
    fx = S.csv("fexp_pairs")
    fx = fx[fx.group == "consistent_reversal"]
    L.add("5.ctf.F_share_min", "CHECKED", "F projected share of absolute contribution, minimum (DECISION_BRIEF: 87.7%)", 0.877,
          float(fx.projection_absolute_share.min()), tol=5e-4, section=sec)
    L.add("5.ctf.F_share_max", "CHECKED", "F projected share of absolute contribution, maximum (DECISION_BRIEF: 99.5%)", 0.995,
          float(fx.projection_absolute_share.max()), tol=5e-4, section=sec)
    if reproduction:
        unc = S.csv("od_corr_unc")
        for k, fmt in enumerate(A.FORMATS):
            x, y = A.e1n2(fmt)
            b = stats.bootstrap_corr(x, y, draws=2000, seed=20261101 + k)
            lo, hi = np.percentile(b, [2.5, 97.5])
            s = unc[(unc.family == fmt) & (unc.pair == "E1__N2")].iloc[0]
            L.add(f"5.boot.E1N2.{fmt}", "CHECKED", f"independent persona bootstrap 95% interval for E1–N2 vs saved, {fmt} (max |bound diff|)",
                  0.0, float(max(abs(lo - s.lower), abs(hi - s.upper))), tol=0.02, section=sec,
                  note=f"re-drawn [{lo:+.3f}, {hi:+.3f}] vs saved [{s.lower:+.3f}, {s.upper:+.3f}]")
            St5 = A.styles()
            bc = stats.bootstrap_corr(x, y, draws=1000, seed=20261201 + k, controls=St5)
            lo, hi = np.percentile(bc, [2.5, 97.5])
            s2 = sv[(sv.condition == "condition_core5") & (sv.source == fmt)].iloc[0]
            L.add(f"5.boot.core5.{fmt}", "CHECKED", f"independent bootstrap of five-style conditioned E1–N2 vs saved interval, {fmt}",
                  0.0, float(max(abs(lo - s2.lower), abs(hi - s2.upper))), tol=0.03, section=sec,
                  note=f"re-drawn [{lo:+.3f}, {hi:+.3f}] vs saved [{s2.lower:+.3f}, {s2.upper:+.3f}]")


def section1(L: Ledger, reproduction: bool = False):
    """Persona Landscape Explorer: inputs, standardization, row matching, PCs, default pair."""
    from scipy import stats as sps
    from . import landscape as LS
    sec = "1"
    pay = LS.payload()
    raws = {m: LS.traits_raw(m) for m in LS.MODELS}
    # Row order and names identical across the three trait matrices; traits identical.
    q = raws["qwen"]
    L.add("1.rows.identical", "RECOMPUTED", "persona row order and names identical across Qwen/Llama/Gemma trait matrices",
          True, all(list(r.index) == list(q.index) for r in raws.values()), section=sec)
    L.add("1.rows.n", "RECOMPUTED", "matched personas in all three trait matrices", 275,
          len(set.intersection(*[set(r.index) for r in raws.values()])), section=sec)
    L.add("1.traits.identical", "RECOMPUTED", "trait columns identical across models (240)", True,
          all(list(r.columns) == list(q.columns) for r in raws.values()) and q.shape[1] == 240, section=sec)
    L.add("1.pcs.personas", "RECOMPUTED", "saved PC scores cover the same 275 personas in every model", True,
          all(set(LS.pcs(m).index) == set(q.index) and len(LS.pcs(m)) == 275 for m in LS.MODELS), section=sec)
    # z-scores recomputed independently (scipy, population SD) vs the embedded 4-decimal values.
    for m in LS.MODELS:
        r = raws[m].loc[pay["personas"], LS.trait_order()].to_numpy()
        z = sps.zscore(r, axis=0, ddof=0)
        emb = np.asarray(pay["models"][m]["z"]) / pay["scale"]
        L.add(f"1.z.{m}", "RECOMPUTED", f"{LS.MODEL_LABEL[m]}: within-model z-scores (scipy) vs embedded values (max |diff|)",
              0.0, float(np.abs(z - emb).max()), tol=5.01e-5, section=sec)
    # PC1-PC3 from the saved PCA scores vs the terrain viewer's saved native PC1-PC3.
    rc = S.csv("role_coords")
    for m in LS.MODELS:
        a = LS.pcs(m)[["pc1", "pc2", "pc3"]]
        b = rc[rc.model == m].set_index("role").loc[a.index, ["native_pc1", "native_pc2", "native_pc3"]].to_numpy()
        d = np.abs(a.to_numpy() - b)
        rel = float((d / np.maximum(np.abs(b), 1e-300)).max())
        dmax = float(d.max())
        desc = f"{LS.MODEL_LABEL[m]}: saved PC1–PC3 vs role_coordinates.csv (max |diff|)"
        if dmax <= 1e-9:
            L.add(f"1.pc.{m}", "RECOMPUTED", desc, 0.0, dmax, tol=1e-9, section=sec)
        elif rel <= 1e-11:
            L.add(f"1.pc.{m}", "RECOMPUTED", desc, 0.0, dmax, tol=1e-9, section=sec, status="NOTE",
                  note=f"role_coordinates.csv prints 12 significant digits (values to ~{np.abs(b).max():,.0f}); "
                       f"max relative difference {rel:.1e}")
        else:
            L.add(f"1.pc.{m}", "RECOMPUTED", desc, 0.0, dmax, tol=1e-9, section=sec)
        emb = np.asarray(pay["models"][m]["pcs"])[:, :3] / pay["scale"]
        L.add(f"1.pc.embed.{m}", "RECOMPUTED", f"{LS.MODEL_LABEL[m]}: embedded PC coordinates vs saved (max |diff|)", 0.0,
              float(np.abs(LS.pcs(m).loc[pay["personas"], ["pc1", "pc2", "pc3"]].to_numpy() - emb).max()), tol=5.01e-5, section=sec)
    # Default pair: rule applied to the independent terrain-viewer PC1 and the frozen ordinary-role subset.
    cls = S.csv("od_persona_class", keep_default_na=False).set_index("persona")
    ordinary = cls.index[cls.ordinary_role_subset.astype(str).str.lower() == "true"]
    pc1 = rc[rc.model == "qwen"].set_index("role").loc[ordinary, "native_pc1"]
    L.add("1.default.pair", "CHECKED", "default A/B = lowest/highest Qwen PC1 among 130 ordinary-role characters",
          f"{pc1.idxmin()} / {pc1.idxmax()}", " / ".join(pay["default"]), section=sec)
    L.add("1.default.n", "CHECKED", "ordinary-role subset size", 130, int(len(ordinary)), section=sec)
    xm = S.csv("pca_xmodel")
    for k, v in pay["xmodel"].items():
        t = LS.XMODEL_NAME[k.split("-")[1]]
        saved = float(xm[(xm.reference_component == 1) & (xm.target_component == 1) & (xm.target_model == t)].pearson_correlation.iloc[0])
        L.add(f"1.xmodel.{k}", "CHECKED", f"PC1 cross-model correlation shown in the notice, {k}", saved, v, tol=0, section=sec)


# ------------------------------------------------------------ Iteration 11
# Reported in cross_model_trait_relationships_20261015/REPORT.md (e01cacb): fingerprint Pearson and same-sign cells.
CROSS_LIBRARY = {("qwen", "llama"): (0.733, 22352), ("qwen", "gemma"): (0.868, 24354), ("llama", "gemma"): (0.840, 23748)}


def _lstsq(x, y):
    """Independent least-squares solve (design matrix [1, x]) for the best-fit checks."""
    X = np.column_stack([np.ones(len(x)), np.asarray(x, float)])
    (b0, b1), *_ = np.linalg.lstsq(X, np.asarray(y, float), rcond=None)
    return float(b1), float(b0)


# Spread ratios supplied with iteration 13 (tolerance .02).
TREND_EXPECTED = {"4.trend.H": 2.00, "2.trend.qwen_llama": 0.94, "2.trend.qwen_gemma": 0.98, "2.trend.llama_gemma": 1.04}


def _trend_check(L: Ledger, cid: str, desc: str, x, y, sec: str):
    """Trend line (standardized major axis): displayed slope and intercept vs an independent calculation (sample SDs,
    numpy corrcoef sign), plus the supplied expected spread ratio where one was given."""
    s1, i1 = stats.sma(x, y)
    x, y = np.asarray(x, float), np.asarray(y, float)
    s2 = float(np.sign(np.corrcoef(x, y)[0, 1]) * np.std(y, ddof=1) / np.std(x, ddof=1))
    i2 = float(np.mean(y) - s2 * np.mean(x))
    L.add(f"{cid}.slope", "RECOMPUTED", f"{desc}: trend slope (spread ratio), displayed vs independent calculation", s2, s1,
          tol=1e-10, section=sec, note=f"spread ratio {s1:.4f}, intercept {i1:+.4f}")
    L.add(f"{cid}.intercept", "RECOMPUTED", f"{desc}: trend line passes through the two means", i2, i1, tol=1e-10, section=sec)
    if cid in TREND_EXPECTED:
        L.add(f"{cid}.expected", "RECOMPUTED", f"{desc}: spread ratio vs supplied value {TREND_EXPECTED[cid]:.2f}",
              TREND_EXPECTED[cid], s1, tol=0.02, section=sec)


def section2(L: Ledger):
    """Figure 2.1: model-pair agreement of the 28,680 historical trait-pair correlations, and the outline values."""
    sec = "2"
    ag = A.model_pair_agreement().set_index(["a", "b"])
    for (a, b), (rep_r, rep_sign) in CROSS_LIBRARY.items():
        r = float(ag.loc[(a, b), "r"])
        L.add(f"2.agree.{a}_{b}", "RECOMPUTED", f"Figure 2.1: {a}–{b} agreement of 28,680 pair correlations vs e01cacb REPORT.md "
              f"({rep_r:.3f})", rep_r, r, tol=5e-4, section=sec)
        L.add(f"2.sign.{a}_{b}", "RECOMPUTED", f"Figure 2.1: {a}–{b} pairs with the same sign vs e01cacb REPORT.md", rep_sign,
              int(ag.loc[(a, b), "same_sign"]), section=sec)
        L.add(f"2.n.{a}_{b}", "RECOMPUTED", f"Figure 2.1: {a}–{b} number of trait pairs", 28680, int(ag.loc[(a, b), "n"]), section=sec)
        _trend_check(L, f"2.trend.{a}_{b}", f"Figure 2.1 {a}–{b}", A.hist_pair_cells(a), A.hist_pair_cells(b), sec)
    # Independent path for one matrix: pandas rank + scipy ndtri on the raw CSV.
    from scipy.special import ndtri
    from . import landscape as LS
    raw = S.csv("traits_qwen").set_index("persona").loc[LS.persona_order(), LS.trait_order()]
    Z = ndtri((raw.rank(method="average") - 0.5) / len(raw))
    alt = Z.corr().to_numpy()
    L.add("2.matrix.qwen", "RECOMPUTED", "Figure 2.1: Qwen 240 × 240 rank-normal correlation matrix, two paths (max |diff|)", 0.0,
          float(np.abs(alt - A.hist_trait_corr("qwen")).max()), tol=1e-10, section=sec)
    lo, hi = float(ag.r.min()), float(ag.r.max())
    L.add("2.outline.range_lo", "CHECKED", "Section 2 outline: model-pair agreement from .73", 0.73, lo, tol=0.005, section=sec)
    L.add("2.outline.range_hi", "CHECKED", "Section 2 outline: model-pair agreement to .87", 0.87, hi, tol=0.005, section=sec)
    pc = LS.xmodel_pc1()
    L.add("2.outline.pc1_gemma", "CHECKED", "Section 2 outline: Qwen PC1 vs Gemma PC1 r = .95 (saved correspondence)", 0.95,
          float(pc["qwen-gemma"]), tol=0.005, section=sec)
    L.add("2.outline.pc1_llama", "CHECKED", "Section 2 outline: Qwen PC1 vs Llama PC1 r = .68 (saved correspondence)", 0.68,
          float(pc["qwen-llama"]), tol=0.005, section=sec)
    pm = A.persona_score_agreement().groupby(["a", "b"]).r.median()
    L.add("2.outline.persona_lo", "CHECKED", "Section 2 outline: median per-trait character-score agreement from .88", 0.88,
          float(pm.min()), tol=0.005, section=sec)
    L.add("2.outline.persona_hi", "CHECKED", "Section 2 outline: median per-trait character-score agreement to .94", 0.94,
          float(pm.max()), tol=0.005, section=sec)
    nh = A.focal_hist_pairs().set_index("label")
    for m, v in [("llama", -0.900), ("gemma", -0.810)]:
        L.add(f"2.focal.nh.{m}", "CHECKED", f"Figure 2.1: Nurturing–Hostile r in {m} vs the cross-model DECISION_BRIEF.md ({v:+.3f})", v,
              float(nh.loc["Nurturing–Hostile", m]), tol=5e-4, section=sec)


def trend_checks(L: Ledger):
    """Trend lines on Figure 4.1 and the survey-style spread ratio in the F.2 table (section 4 ledger) and 5e.3 (section 5); Figure H.2's best-fit line (section 5)."""
    p = A.pairs325()
    _trend_check(L, "4.trend.H", "Figure 4.1 (scenario)", p.human, p.scenario, "4")
    _trend_check(L, "4.trend.F2", "Appendix F.2 table (survey-style spread ratio)", p.human, p.survey, "4")
    w = A.factor_patterns()
    for col in ["Llama_F1", "Gemma_F3"]:
        _trend_check(L, f"5.trend.5e3.{col}", f"Figure H.7 Qwen F1 vs {col}", w["Qwen_F1"], w[col], "5")
    # 5b: the line is drawn with slope r on standardized (population SD) scores; confirm that equals the least-squares fit.
    St = A.styles()
    x0, y0 = A.e1n2("scenario")
    for cname, C in [("raw", None), ("formal", St[:, :1]), ("five", St)]:
        rx, ry = stats.residualize(x0, C), stats.residualize(y0, C)
        zx, zy = rx / rx.std(), ry / ry.std()
        s2, i2 = _lstsq(zx, zy)
        L.add(f"5.fit.5b.{cname}", "RECOMPUTED", f"Figure H.2 ({cname}): drawn slope (measured r) vs least-squares slope", s2,
              stats.pearson(rx, ry), tol=1e-10, section="5", note=f"intercept {i2:+.2e}")


# ------------------------------------------------------------ Iteration 14: Appendix G
def appendix_g(L: Ledger):
    """Cross-model comparisons. Values computed here are RECOMPUTED against an independent path; values copied from
    pinned sources are CHECKED; numbers quoted in the draft leads are CHECKED at 2 decimals."""
    sec = "G"
    from . import landscape as LS
    # G.1: values shown with Figure G.1 (was 2.1 until iteration 16).
    ag = A.model_pair_agreement().set_index(["a", "b"])
    for (a, b), (rep_r, _) in CROSS_LIBRARY.items():
        L.add(f"G.1.r.{a}_{b}", "CHECKED", f"Figure 2.1: {a}–{b} agreement vs e01cacb REPORT.md", rep_r, float(ag.loc[(a, b), "r"]),
              tol=5e-4, section=sec)
        L.add(f"G.1.sma.{a}_{b}", "CHECKED", f"Figure 2.1: {a}–{b} trend slope vs the iteration 13 supplied value",
              TREND_EXPECTED[f"2.trend.{a}_{b}"], float(ag.loc[(a, b), "sma"]), tol=0.02, section=sec)
    # Per-trait persona-score agreement: Figure 2.1 (was G.2 until iteration 17).
    d = A.persona_score_agreement()
    P, T = LS.persona_order(), LS.trait_order()
    tc = S.csv("aa18_traitconv").set_index("trait").loc[T]
    pw = S.csv("aa18_pairwise").set_index(["model_a", "model_b"])
    for a, b in A.MODEL_PAIRS:
        g = d[(d.a == a) & (d.b == b)].set_index("trait").loc[T].r
        Xa, Xb = LS.traits_raw(a).loc[P, T], LS.traits_raw(b).loc[P, T]
        alt = np.array([np.corrcoef(Xa[t], Xb[t])[0, 1] for t in T])
        L.add(f"G.2.indep.{a}_{b}", "RECOMPUTED", f"Figure G.2: 240 per-trait r, {a}–{b}, two computation paths (max |diff|)", 0.0,
              float(np.abs(alt - g.to_numpy()).max()), tol=1e-12, section=sec)
        L.add(f"G.2.aa18.{a}_{b}", "CHECKED", f"Figure G.2: per-trait r vs AA18 trait_profile_convergence.csv, {a}–{b} (max |diff|)", 0.0,
              float(np.abs(g.to_numpy() - tc[f"pearson_{a}_{b}"].to_numpy()).max()), tol=1e-12, section=sec)
        row = pw.loc[(A.MODEL_LABEL[a], A.MODEL_LABEL[b])]
        L.add(f"G.2.median.{a}_{b}", "CHECKED", f"Figure G.2: median per-trait r vs AA18 pairwise_model_agreement.csv, {a}–{b}",
              float(row.trait_profile_pearson_median), float(g.median()), tol=1e-12, section=sec)
        L.add(f"G.2.reversed.{a}_{b}", "CHECKED", f"Figure G.2: traits with negative r vs AA18, {a}–{b}", int(row.traits_reversed),
              int((g < 0).sum()), section=sec)
        L.add(f"G.2.ge05.{a}_{b}", "CHECKED", f"Figure G.2: traits with r ≥ .5 vs AA18, {a}–{b}", int(row.traits_pearson_ge_0_5),
              int((g >= 0.5).sum()), section=sec)
    med = d.groupby(["a", "b"]).r.median()
    for (a, b), v in [(("qwen", "llama"), 0.88), (("qwen", "gemma"), 0.94), (("llama", "gemma"), 0.92)]:
        L.add(f"G.2.lead.{a}_{b}", "CHECKED", f"Figure G.2 lead: median {v:.2f} ({a}–{b}, 2 d.p.)", v, float(med.loc[(a, b)]), tol=0.005,
              section=sec)
    neg = sorted(d[d.r < 0].trait)
    L.add("G.2.lead.reversed", "CHECKED", "Figure G.2 lead: the two sign changes are avoidant and generalist (Qwen–Llama)",
          "avoidant|generalist", "|".join(neg), section=sec)
    gx = S.csv("greg_xmodel")
    L.add("G.2.greg.lo", "CHECKED", "Appendix G.2 note: Sept 24 Gregariousness follow-up range starts .655 (cross_model_gregarious.csv)", 0.655,
          float(gx.pearson_r.min()), tol=5e-4, section=sec)
    L.add("G.2.greg.hi", "CHECKED", "Appendix G.2 note: Sept 24 Gregariousness follow-up range ends .825 (cross_model_gregarious.csv)", 0.825,
          float(gx.pearson_r.max()), tol=5e-4, section=sec)
    # Activation axes: Figure 2.1 (was G.3 until iteration 16).
    for m in ["llama", "gemma"]:
        cols = [f"pc{i}" for i in range(1, 7)]
        Q, M = LS.pcs("qwen").loc[P, cols].to_numpy(float), LS.pcs(m).loc[P, cols].to_numpy(float)
        R6 = np.corrcoef(Q.T, M.T)[:6, 6:]
        L.add(f"G.3.pcx.{m}", "RECOMPUTED", f"Figure 2.2: Qwen vs {m} PC1-6 correlations from saved scores vs saved correspondence table "
              "(max |diff|)", 0.0, float(np.abs(R6 - A.pc_correspondence(m)).max()), tol=1e-6, section=sec)
        X2, Y2 = Q[:, :2] - Q[:, :2].mean(0), M[:, :2] - M[:, :2].mean(0)
        Sxx, Syy, Sxy = X2.T @ X2, Y2.T @ Y2, X2.T @ Y2
        ev = np.sort(np.linalg.eigvals(np.linalg.solve(Sxx, Sxy) @ np.linalg.solve(Syy, Sxy.T)).real)[::-1]
        cc = A.pc_plane_cca(m)
        L.add(f"G.3.cca.{m}", "RECOMPUTED", f"Figure 2.2: canonical correlations of the PC1-PC2 planes, Qwen vs {m}: QR/SVD vs eigenvalue "
              "path (max |diff|)", 0.0, float(np.abs(np.sqrt(ev) - cc).max()), tol=1e-10, section=sec,
              note="canonical correlations " + ", ".join(f"{v:.4f}" for v in cc) + " (computed in this notebook)")
    cl, cg = A.pc_plane_cca("llama"), A.pc_plane_cca("gemma")
    Rl, Rg = A.pc_correspondence("llama"), A.pc_correspondence("gemma")
    for cid, desc, v, obs in [("G.3.lead.g11", "Gemma PC1 r .95", 0.95, Rg[0, 0]), ("G.3.lead.g22", "Gemma PC2 r .92", 0.92, Rg[1, 1]),
                              ("G.3.lead.l11", "Llama PC1 r +.68", 0.68, Rl[0, 0]), ("G.3.lead.l12", "Llama PC2 r −.68", -0.68, Rl[0, 1]),
                              ("G.3.lead.cc1", "canonical .97", 0.97, cl[0]), ("G.3.lead.cc2", "canonical .90", 0.90, cl[1])]:
        L.add(cid, "CHECKED", f"Figure 2.2 lead: {desc} (2 d.p.)", v, float(obs), tol=0.005, section=sec)
    L.add("G.3.rotation", "RECOMPUTED", "Figure 2.2 lead: Llama axes rotated within a shared plane (plane canonical correlations ≥ .90 "
          "while Qwen PC1 splits evenly, |r| ≥ .6 with both Llama PC1 and PC2)", True,
          bool(cl.min() >= 0.90 and abs(Rl[0, 0]) >= 0.6 and abs(Rl[0, 1]) >= 0.6), section=sec)
    # G.4: factor matching.
    rng = {("qwen", "llama"): (0.61, 0.92), ("qwen", "gemma"): (0.73, 0.93), ("llama", "gemma"): (0.52, 0.91)}
    for (a, b), (lo, hi) in rng.items():
        fa, fb, C, Mk = A.factor_match_matrix(a, b)
        L.add(f"G.4.n.{a}_{b}", "CHECKED", f"G.4: matched pairs {a}–{b} = smaller factor count", min(len(fa), len(fb)), int(Mk.sum()),
              section=sec)
        L.add(f"G.4.lo.{a}_{b}", "CHECKED", f"G.4 lead: weakest matched |congruence| {lo:.2f}, {a}–{b}", lo, float(np.abs(C[Mk]).min()),
              tol=0.005, section=sec)
        L.add(f"G.4.hi.{a}_{b}", "CHECKED", f"G.4 lead: strongest matched |congruence| {hi:.2f}, {a}–{b}", hi, float(np.abs(C[Mk]).max()),
              tol=0.005, section=sec)
    cm = S.csv("cm01_matches").query("method == 'original_pattern'").set_index(["factor_a", "factor_b"])
    for (fa_, fb_), v in [(("Qwen_F3", "Llama_F2"), 0.919), (("Qwen_F3", "Gemma_F6"), 0.930), (("Llama_F2", "Gemma_F6"), 0.915)]:
        L.add(f"G.4.strongest.{fa_}_{fb_}", "CHECKED", f"G.4 lead: strongest match {fa_}/{fb_} |congruence| vs PHG-CM01 brief ({v:.3f})",
              v, float(cm.loc[(fa_, fb_), "absolute_congruence"]), tol=5e-4, section=sec)
    for (fa_, fb_), v in [(("Qwen_F1", "Gemma_F3"), 0.77), (("Qwen_F1", "Gemma_F1"), 0.79)]:
        L.add(f"G.4.f1.{fb_}", "CHECKED", f"G.4 lead: Qwen F1 vs {fb_} congruence {v:.2f}", v, float(cm.loc[(fa_, fb_), "signed_congruence"]),
              tol=0.005, section=sec)
    # G.5: consensus directions.
    ct = A.consensus_table().set_index("component")
    exp = {"C1": "Human combination", "C2": "Partial human analogue", "C3": "Independently supported",
           "C4": "Presently untestable", "C5": "Presently untestable"}
    L.add("G.5.components", "CHECKED", "G.5: AA18 supports exactly five consensus axes (C1-C5)", "C1|C2|C3|C4|C5", "|".join(ct.index),
          section=sec)
    L.add("G.5.aa19", "CHECKED", "G.5: AA19 classes match RESEARCH_STATE (C3 supported, C2 partial, C1 combination, C4/C5 untestable)",
          True, bool(all(ct.loc[c, "status"] == v for c, v in exp.items())), section=sec)
    L.add("G.5.bridge", "CHECKED", "G.5: bridge coverage inadequate for exactly C4 and C5 (AA19)", "C4|C5",
          "|".join(ct.index[~ct.bridge_adequate.astype(bool)]), section=sec)
    # G.6: local semantic geometry (fe3a307).
    import json as _json
    res = _json.loads(S.path("lgeo_results").read_text())
    L.add("G.6.rho", "CHECKED", "G.6 lead: primary rho .839 vs fe3a307 results.json", 0.839, float(res["primary_rho"]), tol=5e-4,
          section=sec)


# ------------------------------------------------------------ Iteration 15: Appendix F.2 table (replaces Figures F.2–F.4)
CAL30_MULT = {"scenario": 0.529452, "survey_style": 0.549380}       # calibration package 677d4f2
CAL30_RESCALED = {"scenario": 0.254224, "survey_style": 0.252502}  # calibration package 677d4f2


def appendix_f(L: Ledger):
    """Each value in the F.2 table, against the saved source or an independent calculation."""
    sec = "F"
    d = A.format_results()
    p = A.pairs325()
    fp = S.csv("d30b_fingerprints").set_index("source")
    for fmt, col in [("scenario", "scenario"), ("survey_style", "survey")]:
        r = d.loc[fmt]
        L.add(f"F.2.pattern.{fmt}", "RECOMPUTED", f"F.2 table: pattern agreement r vs saved fingerprint, {fmt}",
              float(fp.loc[fmt, "Pearson"]), float(r.pattern_r), tol=1e-9, section=sec)
        L.add(f"F.2.sign.{fmt}", "RECOMPUTED", f"F.2 table: same-direction share vs saved fingerprint, {fmt}",
              float(fp.loc[fmt, "sign_agreement"]), float(r.same_sign), tol=1e-9, section=sec)
        x, y = p.human.to_numpy(float), p[col].to_numpy(float)
        s2 = float(np.sign(np.corrcoef(x, y)[0, 1]) * np.std(y, ddof=1) / np.std(x, ddof=1))
        L.add(f"F.2.spread.{fmt}", "RECOMPUTED", f"F.2 table: spread ratio vs independent calculation (sample SDs), {fmt}",
              s2, float(r.spread), tol=1e-10, section=sec)
        L.add(f"F.2.r2.{fmt}", "CHECKED", f"F.2 table: average R² as measured vs Direct-30 B REPORT.md, {fmt}",
              MACRO_R2[fmt], float(r.r2_measured), tol=5e-7, section=sec)
        L.add(f"F.2.r2cal.{fmt}", "CHECKED", f"F.2 table: average R² after common rescaling vs calibration package, {fmt}",
              CAL30_RESCALED[fmt], float(r.r2_rescaled), tol=5e-6, section=sec)
        L.add(f"F.2.mult.{fmt}", "CHECKED", f"F.2 table: common rescaling multiplier vs calibration package, {fmt}",
              CAL30_MULT[fmt], float(r.multiplier), tol=1e-6, section=sec)
        L.add(f"F.2.groups.{fmt}", "RECOMPUTED", f"F.2 table: 13 reversals and 6 close matches (frozen screen), {fmt}",
              "13/6", f"{int(r.n_reversal)}/{int(r.n_close)}", section=sec)
    L.add("F.2.spread.survey_expected", "RECOMPUTED", "F.2 table: survey-style spread ratio vs iteration 13 reported value 2.130",
          2.130, float(d.loc["survey_style", "spread"]), tol=0.0005, section=sec)
    t = A.pairs_by_format()
    L.add("F.2.pairs_table", "RECOMPUTED", "F.2 pairs table: 325 rows, Qwen columns equal the recomputed pair correlations (max |diff|)",
          0.0, float(max(np.abs(t["Qwen r, main text"].to_numpy() - p.scenario.to_numpy()).max(),
                         np.abs(t["Qwen r, survey-style"].to_numpy() - p.survey.to_numpy()).max())) if len(t) == 325 else 1.0,
          tol=0, section=sec)


# ------------------------------------------------------------ Iteration 18: Figure 2.2
def figure_23(L: Ledger):
    """Consensus directions C1-C5 vs each model's activation PCs: displayed values against an independent path (merge on
    persona names, numpy corrcoef), plus the values quoted in the lead (2 d.p.)."""
    sec = "2"
    sc = S.csv("aa18_scores")
    pcs = S.csv("persona_pcs")
    L.add("2.3.rows", "RECOMPUTED", "Figure 2.3: AA18 snapshot has 275 characters x C1-C5, all retained", (1375, True),
          (len(sc), bool(sc.retained.astype(str).eq("True").all())), section=sec)
    for m in ["qwen", "gemma", "llama"]:
        d = sc.pivot(index="persona", columns="component", values=f"{m}_score").merge(
            pcs[pcs.model == m].set_index("persona"), left_index=True, right_index=True)
        ind = np.array([[np.corrcoef(d[c].astype(float), d[f"pc{j}"].astype(float))[0, 1] for j in range(1, 6)]
                        for c in A.CONSENSUS])
        L.add(f"2.3.r.{m}", "RECOMPUTED", f"Figure 2.3: {m} C1-C5 x PC1-5 r, displayed vs independent merge + corrcoef (max |diff|)",
              0.0, float(np.abs(A.consensus_pc_corr(m) - ind).max()), tol=1e-10, section=sec, note=f"{len(d)} characters")
    for m, vals in [("qwen", (0.94, 0.98, 0.92)), ("gemma", (0.90, 0.90, 0.78))]:
        R_ = A.consensus_pc_corr(m)
        for i, v in enumerate(vals):
            L.add(f"2.3.lead.{m}.C{i + 1}", "CHECKED", f"Figure 2.3 lead: {m} C{i + 1} vs PC{i + 1}, size {v:.2f} (2 d.p.)", v,
                  abs(float(R_[i, i])), tol=0.005, section=sec)
    Rl = A.consensus_pc_corr("llama")
    for i in range(2):
        share = float(Rl[i, 0] ** 2 + Rl[i, 1] ** 2)  # PCs are uncorrelated, so this is the R² on PC1 and PC2
        L.add(f"2.3.lead.llama.C{i + 1}.plane", "CHECKED", f"Figure 2.3 lead: Llama C{i + 1} variance on PC1-PC2 about 90%",
              0.90, share, tol=0.03, section=sec, note=f"{share:.3f}")
    for m in ["qwen", "gemma", "llama"]:
        R_ = A.consensus_pc_corr(m)
        L.add(f"2.3.lead.weak.{m}", "CHECKED", f"Figure 2.3 lead: C4 and C5 weaker than C1-C3 on their strongest PC, {m}", True,
              bool(np.abs(R_[3:]).max(axis=1).max() < np.abs(R_[:2]).max(axis=1).min()), section=sec)


# ------------------------------------------------------------ Iteration 19: key to the consensus directions
# Top-5 traits at each end as quoted in the AA18 report (three_model_consensus_trait_report.md, main 65da790).
AA18_POLES = {
    "C1": (["mercurial", "spontaneous", "obsessive", "zealous", "flirty"], ["factual", "moderate", "transparent", "conciliatory", "calm"]),
    "C2": (["introverted", "ritualistic", "pensive", "abstract", "erudite"], ["experiential", "practical", "casual", "accessible", "gregarious"]),
    "C3": (["forgiving", "humanistic", "nurturing", "empathetic", "open_ended"], ["blunt", "prescriptive", "materialist", "callous", "confrontational"]),
    "C4": (["progressive", "divergent", "interdisciplinary", "systems_thinker", "holistic"], ["traditional", "literal", "concise", "fundamentalist", "understated"]),
    "C5": (["decisive", "closure_seeking", "universalist", "assertive", "confident"], ["deferential", "cautious", "introspective", "circumspect", "inquisitive"]),
}
AA18_TOP = {"C1": (0.96, -0.95), "C2": (0.97, -0.92), "C3": (0.90, -0.80), "C4": (0.77, -0.65), "C5": (0.53, -0.41)}


def consensus_key(L: Ledger):
    sec = "2"
    k = A.consensus_key().set_index("component")
    for c in A.CONSENSUS:
        hi, lo = A.consensus_poles(c)
        L.add(f"2.3.key.poles.{c}", "CHECKED", f"Consensus key: {c} top-5 traits at each end vs AA18 report", "match",
              "match" if ([t for t, _ in hi], [t for t, _ in lo]) == AA18_POLES[c] else f"{[t for t, _ in hi]} / {[t for t, _ in lo]}",
              section=sec)
        L.add(f"2.3.key.top.{c}", "CHECKED", f"Consensus key: {c} strongest loadings vs AA18 report (2 d.p.)",
              AA18_TOP[c][0] - AA18_TOP[c][1], round(hi[0][1], 2) - round(lo[0][1], 2), tol=1e-9, section=sec,
              note=f"{hi[0][1]:+.3f} / {lo[0][1]:+.3f}")
        i = A.CONSENSUS.index(c)
        for m in ["qwen", "gemma", "llama"]:
            r = A.consensus_pc_corr(m)[i]
            L.add(f"2.3.key.axis.{c}.{m}", "RECOMPUTED", f"Consensus key: {c} best-matching {m} axis equals the largest |r| in Figure 2.3",
                  (int(np.argmax(np.abs(r))) + 1, float(r[np.argmax(np.abs(r))])), (int(k.loc[c, f"{m}_pc"]), float(k.loc[c, f"{m}_r"])),
                  section=sec)
    aa19 = S.csv("aa19_comp").set_index("component")
    L.add("2.3.key.aa19", "CHECKED", "Consensus key: human status per direction vs AA19 component_classification.csv",
          [A.AA19_PLAIN[aa19.loc[c, "classification"]] for c in A.CONSENSUS], list(k.human), section=sec)


# ------------------------------------------------------------ Iteration 20: Figures 1.2 and 3.1
def figure_12(L: Ledger):
    """Figure 1.1 (Figure 1.2 in iterations 21-26): characters on Qwen's PC1-PC2 coloured by a trait, and the axis guide for PC1-PC5."""
    sec = "1"
    from . import landscape as LS
    t = S.csv("traits_qwen")
    t = t.set_index(t.columns[0]).astype(float)
    pcs = S.csv("persona_pcs")
    j = t.merge(pcs[pcs.model == "qwen"].set_index("persona")[[f"pc{k}" for k in range(1, 6)]].astype(float),
                left_index=True, right_index=True)
    ind = np.array([[np.corrcoef(j[c], j[f"pc{k}"])[0, 1] for k in range(1, 6)] for c in t.columns])
    L.add("1.2.r", "RECOMPUTED", "Figure 1.1: 240 traits x PC1-5 r, displayed vs independent merge + corrcoef (max |diff|)", 0.0,
          float(np.abs(A.trait_pc_corr("qwen").to_numpy() - ind).max()), tol=1e-10, section=sec, note=f"{len(j)} characters")
    g = A.axis_guide("qwen")
    r = pd.DataFrame(ind, index=t.columns, columns=[f"PC{k}" for k in range(1, 6)])
    for row in g.itertuples():
        s = r[row.axis].sort_values()
        L.add(f"1.2.guide.{row.axis}", "RECOMPUTED", f"Axis guide {row.axis}: top-3 traits at each end equal the independent ranking",
              (list(s.index[::-1][:3]), list(s.index[:3])), (row.high, row.low), section=sec)
        o = pcs[pcs.model == "qwen"].set_index("persona")[f"pc{row.axis[2:]}"].astype(float).sort_values()
        L.add(f"1.2.chars.{row.axis}", "RECOMPUTED", f"Axis guide {row.axis}: two characters furthest toward each end",
              (list(o.index[::-1][:2]), list(o.index[:2])), (row.high_chars, row.low_chars), section=sec)
    menu_traits = {tr for ax in ["PC2", "PC3"] for tr, _ in A.pc_map_options("qwen", ax)}
    L.add("1.2.menu.coverage", "RECOMPUTED", "Figure 1.1 trait menus (Qwen) cover the strongest trait at both ends of PC2-PC3 (independent ranking)",
          True, all(r[f"PC{k}"].idxmax() in menu_traits and r[f"PC{k}"].idxmin() in menu_traits for k in range(2, 4)), section=sec)
    # Iteration 37: Qwen PC1 uses illustrative traits; check they are strong, nearly pure PC1 and correctly signed.
    rk = r.PC1.abs().rank(ascending=False)
    L.add("1.2.menu.pc1_illustrative", "RECOMPUTED",
          "Figure 1.1 (Qwen PC1): factual and dramatic are in the top 15 of 240 by |r| (ranks 13 and 6), signs +/−, |r with PC2| < .30",
          (13, 6, True, True), (int(rk["factual"]), int(rk["dramatic"]), bool(r.loc["factual", "PC1"] > 0 and r.loc["dramatic", "PC1"] < 0),
                                bool(abs(r.loc["factual", "PC2"]) < 0.30 and abs(r.loc["dramatic", "PC2"]) < 0.30)), section=sec)
    # Iteration 25: Gemma and Llama, the per-model/axis menus, and the diagonal rule.
    for m in ["gemma", "llama"]:
        tm = S.csv(f"traits_{m}")
        tm = tm.set_index(tm.columns[0]).astype(float)
        jm = tm.merge(pcs[pcs.model == m].set_index("persona")[[f"pc{k}" for k in range(1, 6)]].astype(float),
                      left_index=True, right_index=True)
        im = pd.DataFrame([[np.corrcoef(jm[c], jm[f"pc{k}"])[0, 1] for k in range(1, 6)] for c in tm.columns],
                          index=tm.columns, columns=[f"PC{k}" for k in range(1, 6)])
        L.add(f"1.2.r.{m}", "RECOMPUTED", f"Figure 1.1: {m} 240 traits x PC1-5 r vs independent merge + corrcoef (max |diff|)", 0.0,
              float(np.abs(A.trait_pc_corr(m).to_numpy() - im.to_numpy()).max()), tol=1e-10, section=sec, note=f"{len(jm)} characters")
        gm = A.axis_guide(m)
        L.add(f"1.2.guide.{m}", "RECOMPUTED", f"Axis guide ({m}): top-3 traits at each end of PC1-PC5 equal the independent ranking",
              [(list(im[a].sort_values().index[::-1][:3]), list(im[a].sort_values().index[:3])) for a in im.columns],
              [(h, l) for h, l in zip(gm.high, gm.low)], section=sec)
    for m in A.PC_MAP_MODELS:
        rm = A.trait_pc_corr(m)
        for ax in ["PC2", "PC3"]:
            o = [t for t, _ in A.pc_map_options(m, ax)]
            dg = max(rm.index, key=lambda t: min(abs(rm.loc[t, "PC1"]), abs(rm.loc[t, ax])))
            L.add(f"1.2.menu.{m}.{ax}", "RECOMPUTED", f"Figure 1.1 trait menu ({m}, {ax}): PC1 high/low, {ax} high/low, PC1-{ax} diagonal",
                  [*A.PC1_ILLUSTRATIVE.get(m, (rm.PC1.idxmax(), rm.PC1.idxmin())), rm[ax].idxmax(), rm[ax].idxmin(), dg], o,
                  section=sec, note="Qwen PC1: illustrative traits (iteration 37)" if m in A.PC1_ILLUSTRATIVE else "")
    for tr, k, val in [("factual", "PC1", 0.95), ("dramatic", "PC1", -0.97), ("introverted", "PC2", -0.95),
                       ("conscientious", "PC1", 0.69), ("conscientious", "PC2", -0.70), ("callous", "PC3", 0.94)]:
        L.add(f"1.2.lead.{tr}.{k}", "CHECKED", f"Figure 1.1 lead: {tr} vs {k} r = {val:+.2f} (2 d.p.)", val, float(r.loc[tr, k]),
              tol=0.005, section=sec)
    for m, k, val in [("qwen", 1, 0.32), ("qwen", 2, 0.16), ("qwen", 3, 0.09), ("gemma", 1, 0.23), ("llama", 1, 0.17),
                      ("llama", 2, 0.14)]:
        L.add(f"1.2.var.{m}.PC{k}", "CHECKED", f"Figure 1.1 lead: {m} PC{k} explains {val:.0%} (saved PCA diagnostics)", val,
              float(A.pca_variance(m).loc[k]), tol=0.005, section=sec)
    d = S.csv("pca_diag").set_index(["model", "component"])
    for m, val in [("qwen", 0.98), ("gemma", 0.97), ("llama", 0.76)]:
        L.add(f"1.2.stab.{m}", "CHECKED", f"Figure 1.1 lead: {m} PC1 bootstrap loading cosine 5th percentile {val:.2f} (saved)", val,
              float(d.loc[(m, "1"), "bootstrap_loading_cosine_q05"]) if (m, "1") in d.index else float(d.loc[(m, 1), "bootstrap_loading_cosine_q05"]),
              tol=0.005, section=sec)


def appendix_e4(L: Ledger):
    """Appendix E.4 (Figure 1.2 in iteration 20): each model's AA17 factors vs its activation PCs; key to Qwen's factors;
    Qwen's factors vs C1-C5; Qwen's facets vs F1-F5 against the saved Oct 26 values."""
    sec = "E"
    from . import landscape as LS
    d = S.csv("aa17_scores")
    pcs = S.csv("persona_pcs")
    for m in ["qwen", "gemma", "llama"]:
        w = d[d.model == A.MODEL_LABEL[m]].pivot(index="persona", columns="factor", values="score")
        j = w.merge(pcs[pcs.model == m].set_index("persona"), left_index=True, right_index=True)
        fac = sorted(w.columns, key=lambda c: int(c.split("F")[-1]))
        ind = np.array([[np.corrcoef(j[f].astype(float), j[f"pc{k}"].astype(float))[0, 1] for k in range(1, 7)] for f in fac])
        L.add(f"1.2.r.{m}", "RECOMPUTED", f"Figure E.4: {m} factors x PC1-6 r, displayed vs independent merge + corrcoef (max |diff|)",
              0.0, float(np.abs(A.factor_pc_corr(m) - ind).max()), tol=1e-10, section=sec, note=f"{len(j)} characters, {len(fac)} factors")
    q = A.factor_pc_corr("qwen")
    for k, v in enumerate([0.75, -0.50, -0.42]):
        L.add(f"1.2.lead.F1.PC{k + 1}", "CHECKED", f"Figure E.4 lead: Qwen F1 vs PC{k + 1} r = {v:+.2f} (2 d.p.)", v, float(q[0, k]),
              tol=0.005, section=sec)
    r2 = A.factor_pc_r2("qwen")
    L.add("1.2.lead.r2range", "CHECKED", "Figure E.4 lead: PC1-PC6 explain 83% to 99% of each Qwen factor", "83-99",
          f"{round(min(r2) * 100)}-{round(max(r2) * 100)}", section=sec)
    fq = A.factor_scores("qwen")
    L.add("1.2.lead.F2F5", "CHECKED", "Figure E.4 limitation: Qwen F2-F5 score correlation −.49 (2 d.p.)", -0.49,
          stats.pearson(fq.F2.to_numpy(float), fq.F5.to_numpy(float)), tol=0.005, section=sec)
    L.add("1.2.nfactors", "RECOMPUTED", "Figure E.4: factor counts Qwen 5, Llama 6, Gemma 6", (5, 6, 6),
          tuple(A.factor_scores(m).shape[1] for m in ["qwen", "llama", "gemma"]), section=sec)
    k = A.factor_poles()
    L.add("1.2.key.F1", "CHECKED", "Factor key: Qwen F1 poles vs the Oct 26 DECISION_BRIEF (patient/calm/diplomatic vs edgy/bitter/passive-aggressive)",
          ("patient, calm, diplomatic", "edgy, bitter, passive aggressive"), (k.high[0], k.low[0]), section=sec)
    fc = A.factor_consensus_corr("qwen")
    L.add("1.2.F1C1", "CHECKED", "Figure E.4 lead: Qwen F1 vs C1 r = −.89 (2 d.p.)", -0.89, float(fc[0, 0]), tol=0.005, section=sec)
    g = S.csv("fexp_geo")
    g = g[(g.source == "scenario") & (g.geometry == "F")]
    v = S.csv("fexp_var")
    v = v[(v.source == "scenario") & (v.geometry == "F")].set_index("facet")
    order = list(A.ordered_codes())
    Z, r2 = A.facet_direction_matrix("F")
    sv = g.pivot(index="facet", columns="dimension", values="pearson_r").astype(float).loc[order]
    L.add("3.1.saved.F", "CHECKED", "Appendix E.4 table: Qwen facets x F1-F5 r vs saved facet_geometry_correlations.csv (max |diff|)",
          0.0, float(np.abs(Z - sv.to_numpy()).max()), tol=1e-9, section=sec)
    L.add("3.1.r2.F", "CHECKED", "Appendix E.4 table: per-facet F1-F5 R² vs saved facet_variance_explained.csv (max |diff|)",
          0.0, float(max(abs(r - float(v.loc[f, "variance_explained"])) for r, f in zip(r2, order))), tol=1e-6, section=sec)
    L.add("3.1.lead.mean.F", "CHECKED", "Figure E.5 lead: Qwen's own factors explain 83% of each facet on average", 83,
          round(100 * float(np.mean(r2))), section=sec)
    row = {f: i for i, f in enumerate(order)}
    for f, val in [("N2", -0.93), ("C6", 0.92)]:
        L.add(f"3.1.lead.{f}", "CHECKED", f"Figure E.5 lead: {A.name(f)} on Qwen F1 {val:+.2f} (2 d.p.)", val, float(Z[row[f], 0]),
              tol=0.005, section=sec)


def figure_31(L: Ledger):
    """Qwen facets vs C1-C5 and PC1-PC5: C against the saved Oct 25 values; PC independent; lead values (F checks: appendix_e4)."""
    sec = "3"
    g = S.csv("fexp_geo")
    g = g[g.source == "scenario"]
    v = S.csv("fexp_var")
    v = v[v.source == "scenario"].set_index(["geometry", "facet"])
    order = list(A.ordered_codes())
    for view in ["C"]:
        Z, r2 = A.facet_direction_matrix(view)
        sv = g[g.geometry == view].pivot(index="facet", columns="dimension", values="pearson_r").astype(float).loc[order]
        L.add(f"3.1.saved.{view}", "CHECKED", f"Figure E.5 ({view} view): 26 x 5 r vs saved facet_geometry_correlations.csv (max |diff|)",
              0.0, float(np.abs(Z - sv.to_numpy()).max()), tol=1e-9, section=sec)
        L.add(f"3.1.r2.{view}", "CHECKED", f"Figure E.5 ({view} view): per-facet R² vs saved facet_variance_explained.csv (max |diff|)",
              0.0, float(max(abs(r - float(v.loc[(view, f), "variance_explained"])) for r, f in zip(r2, order))), tol=1e-6, section=sec)
    from . import landscape as LS
    _, Q = A.profiles()
    cs = list(A.codes())
    pcs = LS.pcs("qwen").loc[LS.persona_order()]
    Zp, _ = A.facet_direction_matrix("PC")
    ind = np.array([[np.corrcoef(Q["scenario"][:, cs.index(f)], pcs[f"pc{k}"].astype(float))[0, 1] for k in range(1, 6)] for f in order])
    L.add("3.1.pc", "RECOMPUTED", "Figure E.5 (PC view): 26 x 5 r vs numpy corrcoef (max |diff|)", 0.0, float(np.abs(Zp - ind).max()),
          tol=1e-10, section=sec)
    for view, pct in [("C", 82), ("PC", 78)]:
        L.add(f"3.1.lead.mean.{view}", "CHECKED", f"Figure E.5 lead: average share explained, {view} view, {pct}%", pct,
              round(100 * float(np.mean(A.facet_direction_matrix(view)[1]))), section=sec)
    Zc, _ = A.facet_direction_matrix("C")
    row = {f: i for i, f in enumerate(order)}
    nf = [Zc[row[f], 0] for f in order if f.startswith("N")]
    L.add("3.1.lead.N", "CHECKED", "Figure E.5 lead: Neuroticism facets on C1 from +.80 to +.92", (0.80, 0.92),
          (round(min(nf), 2), round(max(nf), 2)), section=sec)
    mod = [Zc[row[f], 0] for f in ["C5", "C1", "C6", "A4"]]
    L.add("3.1.lead.moderate", "CHECKED", "Figure E.5 lead: Self-Discipline, Self-Efficacy, Cautiousness, Cooperation on C1 −.86 to −.90",
          (-0.90, -0.86), (round(min(mod), 2), round(max(mod), 2)), section=sec)
    for f, k, val, src in [("E5", 0, 0.91, Zc), ("A6", 2, 0.86, Zc), ("A3", 2, 0.74, Zc)]:
        L.add(f"3.1.lead.{f}", "CHECKED", f"Figure E.5 lead: {A.name(f)} value {val:+.2f} (2 d.p.)", val, float(src[row[f], k]),
              tol=0.005, section=sec)


def figure_13(L: Ledger):
    """Figure 3.1 (iteration 31): historical traits grouped by Big Five domain. Independent recomputation from the raw
    snapshot files, plus a CHECKED comparison of the domain scores with the source study's saved intercorrelations."""
    sec = "S"  # Section 3 since iteration 42
    m = S.csv("bf_strict_map")
    L.add("1.3.mapping.n", "RECOMPUTED", "Figure 3.1: strict mapping has 42 traits (N 9, E 8, O 8, A 13, C 4), all frozen geometry-blind",
          (42, {"neuroticism": 9, "extraversion": 8, "openness": 8, "agreeableness": 13, "conscientiousness": 4}, {"frozen_geometry_blind"}),
          (len(m), m.external_domain.value_counts().to_dict(), set(m.review_status)), section=sec)
    t = A.bf_traits()
    L.add("1.3.order", "RECOMPUTED", "Figure 3.1 rows follow the Figure 4.2 domain order (N, E, O, A, C)", A.DOMAIN_ORDER,
          list(dict.fromkeys(t.domain)), section=sec)
    sign = dict(zip(m.trait, np.where(m.polarity == "negative", -1.0, 1.0)))
    ic = S.csv("bf_domain_corr")
    ic = ic[ic.construction == "human_anchored_strict"]
    for mod in ["qwen", "gemma", "llama"]:
        raw = S.csv(f"traits_{mod}")
        raw = raw.set_index(raw.columns[0]).astype(float)
        X = np.column_stack([raw[tr].to_numpy() * sign[tr] for tr in t.trait])
        ind = np.corrcoef(X, rowvar=False)
        D = A.bf_trait_corr(mod)
        L.add(f"1.3.r.{mod}", "RECOMPUTED", f"Figure 3.1 ({mod}): 42 x 42 signed trait r vs independent corrcoef (max |diff|)", 0.0,
              float(np.abs(D - ind).max()), tol=1e-10, section=sec, note=f"{len(raw)} characters")
        # Block averages, independently.
        dom = np.array(t.domain)
        for a, b in [("E", "N"), ("C", "N"), ("C", "A")]:
            ia, ib = np.flatnonzero(dom == a), np.flatnonzero(dom == b)
            L.add(f"1.3.block.{mod}.{a}{b}", "RECOMPUTED", f"Figure 3.1 domain view ({mod}): {a}×{b} average trait-pair r",
                  float(ind[np.ix_(ia, ib)].mean()), A.bf_block(mod, a, b), tol=1e-10, section=sec)
        # Domain scores (pole means) vs the study's saved intercorrelations: all ten pairs.
        err = max(abs(A.bf_block(mod, A.BF_LETTER[r.domain_1], A.BF_LETTER[r.domain_2], "domain_r") - r.pearson_r)
                  for r in ic[ic.model == mod].itertuples())
        L.add(f"1.3.domain_r.{mod}", "CHECKED", f"Figure 3.1 ({mod}): domain-score r for 10 domain pairs vs saved big_five_domain_intercorrelations.csv (max |diff|)",
              0.0, float(err), tol=1e-6, section=sec, note="strict construction; saved values from the Sept 11 study")
    for mod, val in [("qwen", 0.53), ("gemma", 0.39), ("llama", 0.11)]:
        L.add(f"1.3.prose.EN.{mod}", "RECOMPUTED", f"Figure 3.1 prose: {mod} E×N average trait-pair r rounds to {val:+.2f}",
              val, round(A.bf_block(mod, "E", "N"), 2), tol=1e-9, section=sec)
    for mod, val in [("qwen", 0.91), ("gemma", 0.84), ("llama", 0.59)]:
        L.add(f"1.3.prose.ENdom.{mod}", "RECOMPUTED", f"Figure 3.1 prose: {mod} E–N domain-score r rounds to {val:+.2f}",
              val, round(A.bf_block(mod, "E", "N", "domain_r"), 2), tol=1e-9, section=sec)
    L.add("1.3.prose.CE.qwen", "RECOMPUTED", "Figure 3.1 prose: Qwen C×E average trait-pair r rounds to −.64", -0.64,
          round(A.bf_block("qwen", "C", "E"), 2), tol=1e-9, section=sec)
    d = A.domain_blocks()
    en = d[((d.row == "E") & (d.col == "N")) | ((d.row == "N") & (d.col == "E"))].iloc[0]
    L.add("1.3.prose.facetEN", "RECOMPUTED", "Figure 3.1 prose: Qwen facet E×N block average (scenario, Figure 4.2) rounds to +.51", 0.51,
          round(float(en.scenario), 2), tol=1e-9, section=sec)


def figure_61(L: Ledger):
    """Figure 5.1 (iteration 32): Big Five domain-score correlations across sources."""
    import hashlib
    sec = "6"  # Discussion (Figure 5.1) since iteration 36
    h = hashlib.sha256(A.PUBLISHED_DOMAIN_FILE.read_bytes()).hexdigest()
    L.add("6.1.published_values.sha256", "HASH-ONLY", "Figure 5.1: PHG cited table of published Petrov et al. values matches its packaged SHA-256",
          A.PUBLISHED_DOMAIN_SHA256, h, section=sec, note=f"PHG representation of fifty published coefficients; original credit: {A.PETROV_URL} @ {A.PETROV_COMMIT[:7]}. Original file retrieval/verification is optional via scripts/download_petrov.py.")
    p = A.petrov_intercorrs()
    L.add("6.1.petrov.n", "CHECKED", "Figure 5.1: 10 domain pairs x 5 published sources, no gaps", (10, 5, 0),
          (p.shape[0], p.shape[1], int(p.isna().sum().sum())), section=sec)
    for col, val in [("bbc", -0.33), ("generic_gpt35", -0.37), ("generic_gpt4", -0.47), ("silicon_gpt35", -0.27), ("silicon_gpt4", -0.38)]:
        L.add(f"6.1.EN.{col}", "CHECKED", f"Figure 5.1: published N-E r ({col}) as in Petrov et al. Figure 4", val,
              round(float(p.loc[[("N", "E")], col].iloc[0]), 2), tol=1e-9, section=sec)
    # Our facet-composite domain correlations, independently: build standardized-facet sums from the matrix as a covariance.
    M = A.matrices()
    cs = list(A.codes())
    for key in ["human", "scenario"]:
        R = M[key]
        w = {d: np.array([1.0 if c[0] == d else 0.0 for c in cs]) for d in A.DOMAIN_ORDER}
        ind = {(a, b): float(w[a] @ R @ w[b] / np.sqrt((w[a] @ R @ w[a]) * (w[b] @ R @ w[b]))) for a, b in A.DOMAIN_PAIRS}
        got = A.facet_domain_score_corr(key)
        L.add(f"6.1.facets.{key}", "RECOMPUTED", f"Figure 5.1: facet-composite domain r ({key}) vs quadratic-form recomputation (max |diff|)",
              0.0, max(abs(got[k] - v) for k, v in ind.items()), tol=1e-12, section=sec)
    D = A.domain_corr_sources()
    for col, val in [("people_ipip", -0.44), ("qwen_facets", 0.73), ("qwen_traits", 0.91), ("gemma_traits", 0.84), ("llama_traits", 0.59)]:
        L.add(f"6.1.EN.{col}", "RECOMPUTED", f"Figure 5.1 prose: N-E domain r ({col}) rounds to {val:+.2f}", val,
              round(float(D.loc[[("N", "E")], col].iloc[0]), 2), tol=1e-9, section=sec)
    tf = A.template_fit()
    # Prose ranges: people and GPT answers match valence .76-.95; activations match intensity .75-.98.
    ans = ["people_bbc", "people_ipip", "gpt35_generic", "gpt4_generic", "gpt35_silicon", "gpt4_silicon"]
    act = ["qwen_facets", "qwen_traits", "gemma_traits", "llama_traits"]
    L.add("6.1.template.answers", "RECOMPUTED", "Figure 5.1 prose: people and GPT answers match the valence pattern at .76-.95",
          (0.76, 0.95), (round(tf.loc[ans, "valence"].min(), 2), round(tf.loc[ans, "valence"].max(), 2)), section=sec)
    L.add("6.1.template.activations", "RECOMPUTED", "Figure 5.1 prose: activations match the intensity pattern at .75-.98",
          (0.75, 0.98), (round(tf.loc[act, "intensity"].min(), 2), round(tf.loc[act, "intensity"].max(), 2)), section=sec)
    L.add("6.1.template.act_valence", "RECOMPUTED", "Figure 5.1 prose: activations match the valence pattern at most .31",
          0.31, round(tf.loc[act, "valence"].max(), 2), tol=1e-9, section=sec)
    L.add("6.1.EA_EC.sign", "RECOMPUTED", "Figure 5.1 prose: E-A and E-C positive in all people and GPT sources, negative in all activations",
          True, bool((D.loc[[("E", "A"), ("E", "C")], ans].drop(columns=["gpt35_silicon"]) > 0).all().all()
                     and (D.loc[[("E", "A"), ("E", "C")], act] < 0).all().all()), section=sec)
    # Discussion outline numbers (D1, D6).
    iu = np.triu_indices(len(A.bf_traits()), 1)
    H = A.bf_corr("people")[iu]
    for m, val in [("qwen", 0.39), ("gemma", 0.43), ("llama", 0.58)]:
        L.add(f"6.D6.sapa_pattern.{m}", "RECOMPUTED", f"Discussion D6: {m} vs SAPA trait-pair pattern r rounds to {val:.2f}", val,
              round(float(np.corrcoef(H, A.bf_corr(m)[iu])[0, 1]), 2), tol=1e-9, section=sec)
    L.add("6.D1.sapa_EN", "RECOMPUTED", "Discussion D1: SAPA N-E average trait-pair r rounds to −.21", -0.21,
          round(A.bf_block("people", "E", "N"), 2), tol=1e-9, section=sec)
    d = A.domain_blocks()
    en = d[((d.row == "E") & (d.col == "N")) | ((d.row == "N") & (d.col == "E"))].iloc[0]
    L.add("6.D1.facet_EN", "RECOMPUTED", "Discussion D1: people facet N-E block −.27, Qwen +.51", (-0.27, 0.51),
          (round(float(en.human), 2), round(float(en.scenario), 2)), section=sec)
    p325 = A.pairs325()
    rev = p325[p325.group_frozen == "consistent_reversal"]
    ne = sum({a[0], b[0]} == {"N", "E"} for a, b in zip(rev.left, rev.right))
    L.add("6.D1.reversals_NE", "RECOMPUTED", "Discussion D1: 9 of the 13 frozen reversals are N x E pairs", (9, 13), (ne, len(rev)), section=sec)


def section_sapa(L: Ledger):
    """Section 3 (iteration 33): SAPA trait-word bridge (Figures 3.1, 3.2)."""
    sec = "S"
    t = A.bf_traits()
    h = S.csv("bf_sapa_corr")
    h = h.set_index(h.columns[0])
    L.add("S.coverage", "CHECKED", "Section 3: all 42 strict-mapping traits present in the SAPA proxy matrix", 42,
          len(set(t.trait) & set(h.index)), section=sec)
    L.add("S.symmetric", "CHECKED", "Section 3: SAPA proxy matrix symmetric (max |R - R'|)", 0.0,
          float(np.nanmax(np.abs(h.to_numpy(float) - h.to_numpy(float).T))), tol=1e-9, section=sec)
    L.add("S.orientation", "CHECKED", "Section 3: proxies point the way the trait name does (anxious-calm, extroverted-reserved r < 0)",
          True, bool(h.loc["anxious", "calm"] < 0 and h.loc["extroverted", "reserved"] < 0), section=sec)
    P = A.bf_corr("people")
    s = t.sign.to_numpy()
    ind = h.loc[list(t.trait), list(t.trait)].to_numpy(float) * np.outer(s, s)
    np.fill_diagonal(ind, 1.0)
    L.add("S.flip", "RECOMPUTED", "Section 3: sign-flipped 42 x 42 people matrix vs independent flip (max |diff|)", 0.0,
          float(np.abs(P - ind).max()), tol=1e-12, section=sec)
    dom = np.array(t.domain)
    for a, b, val in [("E", "N", -0.21), ("C", "N", -0.17), ("C", "E", 0.10)]:
        ia, ib = np.flatnonzero(dom == a), np.flatnonzero(dom == b)
        L.add(f"S.block.{a}{b}", "RECOMPUTED", f"Section 3 prose: people {a}×{b} average trait-pair r rounds to {val:+.2f}", val,
              round(float(ind[np.ix_(ia, ib)].mean()), 2), tol=1e-9, section=sec)
    iu = np.triu_indices(len(t), 1)
    for m, val, sg in [("qwen", 0.39, 0.59), ("gemma", 0.43, 0.60), ("llama", 0.58, 0.67)]:
        M = A.bf_corr(m)[iu]
        L.add(f"S.pattern.{m}", "RECOMPUTED", f"Section 3 prose: {m} vs people pattern r {val:.2f}, same sign {sg:.2f}", (val, sg),
              (round(float(np.corrcoef(P[iu], M)[0, 1]), 2), round(float(np.mean(np.sign(P[iu]) == np.sign(M))), 2)), section=sec)
    sd = S.csv("bf_sapa_domains").set_index("trait")
    D = A.bf_domains("people")
    L.add("S.domains.people", "RECOMPUTED", "Section 3 table: people trait-domain values equal the saved IPIP100 correlations, sign-flipped (max |diff|)",
          0.0, float(np.abs(D.to_numpy() - np.column_stack([sd.loc[list(t.trait), f"{A.DOMAIN_NAME[d].lower()}_pearson_r"].to_numpy(float)
                                                            * s for d in A.DOMAIN_ORDER])).max()), tol=1e-12, section=sec)
    # Leave-one-out model domain scores, independently for one model.
    sq = A.bf_scores("qwen")
    i = list(t.trait).index("playful")
    g = t[(t.domain == "N") & (t.trait != "playful")]
    sc = sq[list(g.trait[g.sign > 0])].mean(axis=1) + sq[list(g.trait[g.sign < 0])].mean(axis=1)
    L.add("S.loo.playful", "RECOMPUTED", "Section 3 table: Qwen playful with leave-one-out Neuroticism score, independent recomputation",
          float(np.corrcoef(sq["playful"], sc)[0, 1]), float(A.bf_domains("qwen").iloc[i]["N"]), tol=1e-12, section=sec)
    b = A.bridge_domain_summary().set_index("Source")
    L.add("S.summary", "RECOMPUTED", "Section 3 prose: own domain strongest in 90% of traits for people; E traits with N −.22 (people), +.65 (Qwen)",
          (0.90, -0.22, 0.65), (round(b.loc["People (SAPA)", "Own domain strongest (share)"], 2),
                                round(b.loc["People (SAPA)", "Extraversion traits with Neuroticism"], 2),
                                round(b.loc["Qwen", "Extraversion traits with Neuroticism"], 2)), section=sec)
    L.add("S.summary.N", "RECOMPUTED", "Section 3 prose: N traits with E −.28 (people), +.74 (Qwen)", (-0.28, 0.74),
          (round(b.loc["People (SAPA)", "Neuroticism traits with Extraversion"], 2), round(b.loc["Qwen", "Neuroticism traits with Extraversion"], 2)),
          section=sec)

    # Iteration 53: slimmed Section 3 prose (D1 grouping in all three models; anxious tracks Neuroticism most closely).
    for m in ["qwen", "gemma", "llama"]:
        d1 = A.bf_domain_consensus_corr(m)["C1"]
        L.add(f"S.d1.{m}", "RECOMPUTED", f"Section 3 prose: {m} Neuroticism, Extraversion, Openness toward the charged end of D1 "
              "(r > 0), Agreeableness and Conscientiousness toward the moderate end (r < 0)", True,
              bool((d1[["N", "E", "O"]] > 0).all() and (d1[["A", "C"]] < 0).all()), section=sec,
              note=" ".join(f"{k} {v:+.2f}" for k, v in d1.items()))
    pd_ = A.bf_domains("people")
    ax = [ix for ix in pd_.index if ix.split(" ")[0] == "anxious"][0]
    L.add("S.anxious", "RECOMPUTED", "Section 3 prose: in people, anxious correlates most strongly with the Neuroticism scale", "N",
          str(pd_.loc[ax].idxmax()), section=sec, note=f"r {pd_.loc[ax, 'N']:+.2f}")
    k = A.consensus_key().set_index("component")
    L.add("S.d1d3.human", "CHECKED", "Section 3 prose: D1 has no single human counterpart (combination), D3 independently supported",
          ("Human combination", "Independently supported"), (A.consensus_table().set_index("component").loc["C1", "status"],
                                                              A.consensus_table().set_index("component").loc["C3", "status"]), section=sec)


def extraction_counts(L: Ledger):
    """Iteration 54: Section 4 lead and Appendix A.14 counts (generated pairs reconstructed from the execution journals,
    reconciled with the convergence audit's final counts)."""
    sec = "3"
    ec = A.extraction_counts()
    q = ec[ec.facet_qualified.astype(str) == "True"]
    L.add("A14.rows", "CHECKED", "A.14: 26 qualified facets x 2 formats in the generated-count table, all matched to the audit", 52,
          int(q.stopping_n.notna().sum()), section=sec)
    L.add("A14.reconcile", "RECOMPUTED", "A.14: generated - rejected = accepted available; extras match; generated - rejected - extras = stopping n",
          True, bool(((q.generated - q.rejected) == q.available_accepted).all() and (q.extras == q.accepted_extras).all()
                     and ((q.generated - q.rejected - q.extras) == q.stopping_n).all()), section=sec)
    tot = (int(q.generated.sum()), int(q[q.format == "scenario"].generated.sum()), int(q[q.format == "survey_style"].generated.sum()),
           int(q.rejected.sum()), int(q.extras.sum()), int((q.generated - q.rejected - q.extras).sum()))
    L.add("A14.totals", "RECOMPUTED", "A.14: generated 2,272 (1,024 scenario, 1,248 survey-style); rejected 361; extras 447; used 1,464",
          (2272, 1024, 1248, 361, 447, 1464), tot, section=sec)
    L.add("A14.batches", "CHECKED", "A.14: every facet generated 32 or 64 question pairs per format", True,
          bool(q.generated.isin([32, 64]).all()), section=sec)
    per = q.groupby("facet").generated.sum()
    L.add("4.lead.mean", "RECOMPUTED", "Section 4: 87 responses per pole per facet on average (both formats), about 27 times fewer than 2,400",
          (87, 27), (int(round(per.mean())), int(A.LU_RESPONSES_PER_POLE / per.mean())), section=sec, note=f"mean {per.mean():.2f}")
    stops = {f: q[q.format == f].stopping_n.astype(int).value_counts().reindex([16, 24, 32, 48], fill_value=0).tolist()
             for f in ["scenario", "survey_style"]}
    L.add("A14.stops", "RECOMPUTED", "A.14 table: stops at 16/24/32/48 = scenario 4/17/3/2, survey-style 1/12/8/5",
          {"scenario": [4, 17, 3, 2], "survey_style": [1, 12, 8, 5]}, stops, section=sec)
    prog = 2 * int(q.generated.sum()) + 4 * 2 * 64 * 2
    L.add("A14.program", "RECOMPUTED", "A.14: 5,568 responses including the four unconverged facets; about 22 times fewer than 124,800",
          (5568, 22), (prog, int(26 * 2 * A.LU_RESPONSES_PER_POLE / prog)), section=sec)
    L.add("A14.calibration", "CHECKED", "A.14: September 24 calibration cosines .980 / .966 / .969 (calibration_report.md @ 2524afc)",
          (0.980, 0.966, 0.969), tuple(round(A.CALIBRATION_COS[t], 3) for t in ["flippant", "pensive", "accessible"]), section=sec)


def section_conv(L: Ledger):
    """Section 4 elicitation (iteration 33): stopping points and question directions (Codex 598857c)."""
    sec = "3"
    t = A.stopping_table()
    h = S.csv("conv_hist").drop_duplicates(["facet", "format", "checkpoint_n"])
    L.add("4e.records", "CHECKED", "Section 4 stopping table: 60 facet-format records and 252 distinct checkpoints (Codex report)", (60, 252),
          (len(t), len(h)), section=sec)
    # Independent rule application: first scheduled checkpoint with n >= 16, p05 >= .95 and cosine to previous >= .98.
    bad = 0
    for r in t.itertuples():
        g = h[(h.facet == r.facet) & (h.format == r.format)].sort_values("checkpoint_n")
        ok = g[(g.checkpoint_n >= 16) & (g.bootstrap_p05_cosine >= 0.95) & (g.cosine_to_previous_checkpoint >= 0.98)]
        first = float(ok.checkpoint_n.iloc[0]) if len(ok) else np.nan
        if not ((np.isnan(first) and pd.isna(r.stopping_n)) or first == r.stopping_n):
            bad += 1
    L.add("4e.rule", "RECOMPUTED", "Section 4 stopping table: every stopping n equals the first checkpoint meeting the frozen rule (mismatches)", 0, bad,
          section=sec, note="float32 gate values as saved; ties at the threshold would show here")
    q = t[t.qualified]
    for fmt, exp in [("scenario", {16: 4, 24: 17, 32: 3, 48: 2}), ("survey_style", {16: 1, 24: 12, 32: 8, 48: 5})]:
        got = q[q.format == fmt].stopping_n.value_counts().sort_index()
        L.add(f"4e.counts.{fmt}", "CHECKED", f"Section 4 prose: {fmt} stopping counts for the 26 kept facets (16/24/32/48)", exp,
              {int(k): int(v) for k, v in got.items()}, section=sec)
    L.add("4e.excluded", "CHECKED", "Section 4 stopping table: excluded facets are N3, N5, E3, C3", ["C3", "E3", "N3", "N5"],
          sorted(t[~t.qualified].facet.unique()), section=sec)
    qd = S.csv("conv_q")
    L.add("4e.questions", "CHECKED", "Section 4 data: 2,119 saved question directions", 2119, len(qd), section=sec)
    pv = S.csv("conv_pcv").set_index(["block48_axis", "viewer_axis"]).pearson_r
    L.add("4e.basis", "CHECKED", "Section 4 prose: PC1-48/PC2-48/PC3-48 vs viewer PC1/PC2/PC3 r = .982/.968/.976",
          (0.982, 0.968, 0.976), tuple(round(abs(float(pv[(f"PC{k}-48", f"viewer_PC{k}")])), 3) for k in (1, 2, 3)), section=sec)
    v = S.csv("conv_var")
    L.add("4e.var", "CHECKED", "Section 4 prose: PC1-48..PC3-48 explain 58.53% of block-48 persona variance", 58.53,
          round(100 * float(v.cumulative_explained_variance.iloc[2]), 2), tol=1e-9, section=sec)
    mm = S.csv("conv_mean")
    fin = mm[(mm.estimate_kind == "final_accepted") & mm.facet_qualified].fraction_squared_length_in_pc123
    L.add("4e.share123", "CHECKED", "Section 4 prose: PC1-48..PC3-48 hold a median 14% (max 32%) of each kept facet's final direction",
          (0.14, 0.32), (round(float(fin.median()), 2), round(float(fin.max()), 2)), section=sec)
    e1 = q[(q.facet == "E1") & (q.format == "scenario")].stopping_n.iloc[0]
    L.add("4e.E1", "CHECKED", "Section 4 table: Friendliness (E1) scenario stopped at 24 questions", 24, int(e1), section=sec)


def characters_text(L: Ledger):
    """Section 1 'Characters that personify the axes' (iteration 39): every number and ranking in the text, Qwen."""
    from . import landscape as LS
    sec = "1"
    P = LS.persona_order()
    pcs = LS.pcs("qwen").loc[P][["pc1", "pc2", "pc3"]].astype(float)
    t = A.trait_matrix("qwen")
    z = (t - t.mean()) / t.std()
    rank_hi = lambda col, n: int(col.rank(ascending=False, method="min")[n])
    add = lambda i, d, e, o, tol=1e-9: L.add(f"1.chars.{i}", "RECOMPUTED", "Section 1 characters text: " + d, e, o, tol=tol, section=sec)
    add("pc1.order", "lowest PC1: leviathan first, poet second", ["leviathan", "poet"], list(pcs.pc1.nsmallest(2).index))
    add("poet.traits", "poet dramatic +2.1 SD, factual −1.7 SD", (2.1, -1.7), (round(float(z.loc["poet", "dramatic"]), 1), round(float(z.loc["poet", "factual"]), 1)))
    add("secretary.traits", "secretary dramatic −1.5 SD, factual +1.5 SD", (-1.5, 1.5),
        (round(float(z.loc["secretary", "dramatic"]), 1), round(float(z.loc["secretary", "factual"]), 1)))
    sd = pcs.std()
    add("secretary.zero", "secretary within 0.25 SD of zero on PC2 and PC3", True,
        bool(abs(pcs.loc["secretary", "pc2"]) < 0.25 * sd.pc2 and abs(pcs.loc["secretary", "pc3"]) < 0.25 * sd.pc3))
    add("poet.middle", "poet within 0.75 SD of zero on PC2 and PC3", True,
        bool(abs(pcs.loc["poet", "pc2"]) < 0.75 * sd.pc2 and abs(pcs.loc["poet", "pc3"]) < 0.75 * sd.pc3))
    add("assistant.rank", "assistant 46th of 275 toward the factual end of PC1", 46, rank_hi(pcs.pc1, "assistant"))
    add("pc2.pair", "theorist and pragmatist both in the factual quarter of PC1; theorist PC2 < 0 < pragmatist PC2", True,
        bool(min(pcs.loc["theorist", "pc1"], pcs.loc["pragmatist", "pc1"]) > pcs.pc1.quantile(0.7)
             and pcs.loc["theorist", "pc2"] < 0 < pcs.loc["pragmatist", "pc2"]))
    add("theorist.traits", "theorist experiential −1.8 SD (bottom 10 of 275), theoretical in the top 15", (-1.8, True, True),
        (round(float(z.loc["theorist", "experiential"]), 1), rank_hi(z.experiential, "theorist") >= 266, rank_hi(z.theoretical, "theorist") <= 15))
    add("pc2.top", "highest PC2: teenager, adolescent, toddler", {"teenager", "adolescent", "toddler"}, set(pcs.pc2.nlargest(3).index))
    add("pc3.factual", "mediator benevolent > 0 > callous; robot among the ten least benevolent", (True, True),
        (bool(z.loc["mediator", "benevolent"] > 0 > z.loc["mediator", "callous"]), rank_hi(z.benevolent, "robot") >= 266))
    add("pc3.dramatic", "demon 5th most callous, angel 15th most benevolent", (5, 15),
        (rank_hi(z.callous, "demon"), rank_hi(z.benevolent, "angel")))
    add("pc3.gap", "angel-demon PC3 gap nearly four SD (3.5 to 4.0)", True,
        bool(3.5 <= (pcs.loc["demon", "pc3"] - pcs.loc["angel", "pc3"]) / sd.pc3 < 4.0))


def figure_bfpc(L: Ledger):
    """Figure 3.1 (iteration 40): Big Five traits and domain scores vs PC1-PC3, recomputed independently from the raw snapshot."""
    sec = "S"
    t = A.bf_traits()
    sign = dict(zip(t.trait, t.sign))
    pcs = S.csv("persona_pcs")
    for m in ["qwen", "gemma", "llama"]:
        raw = S.csv(f"traits_{m}")
        raw = raw.set_index(raw.columns[0]).astype(float)
        pm = pcs[pcs.model == m].set_index("persona")[["pc1", "pc2", "pc3"]].astype(float)
        j = raw.join(pm, how="inner")
        ind = np.array([[np.corrcoef(j[tr] * sign[tr], j[f"pc{k}"])[0, 1] for k in (1, 2, 3)] for tr in t.trait])
        L.add(f"1.bfpc.r.{m}", "RECOMPUTED", f"Figure 3.1 ({m}): 42 x 3 trait-PC r vs independent join + corrcoef (max |diff|)", 0.0,
              float(np.abs(A.bf_pc_corr(m).to_numpy() - ind).max()), tol=1e-10, section=sec, note=f"{len(j)} characters")
    D = A.bf_domain_pc_corr("qwen")
    for d, k, val in [("Neuroticism", "PC1", -0.76), ("Extraversion", "PC1", -0.82), ("Openness", "PC1", -0.70),
                      ("Agreeableness", "PC3", -0.88), ("Conscientiousness", "PC1", 0.75)]:
        L.add(f"1.bfpc.prose.{d[:4]}", "RECOMPUTED", f"Figure 3.1 prose: Qwen {d} score with {k} rounds to {val:+.2f}", val,
              round(float(D.loc[d, k]), 2), tol=1e-9, section=sec)
    Rq = A.bf_pc_corr("qwen")
    for tr, k, val in [("dominant", "PC3", 0.87), ("assertive", "PC1", -0.76), ("optimistic", "PC3", -0.86)]:
        L.add(f"1.bfpc.prose.{tr}", "RECOMPUTED", f"Figure 3.1 prose: Qwen {tr} with {k} rounds to {val:+.2f}", val,
              round(float(Rq.loc[tr, k]), 2), tol=1e-9, section=sec)
    neo = Rq[t.domain.isin(["N", "E", "O"]).values]
    L.add("1.bfpc.prose.neo_share", "RECOMPUTED", "Figure 3.1 prose: 24 of the 25 Neuroticism, Extraversion and Openness traits lean dramatic (PC1 < 0)",
          (24, 25), (int((neo.PC1 < 0).sum()), len(neo)), section=sec)
    for m, d, k, val in [("gemma", "Neuroticism", "PC2", 0.76), ("llama", "Neuroticism", "PC2", 0.96)]:
        L.add(f"1.bfpc.prose.{m}", "RECOMPUTED", f"Figure 3.1 prose: {m} {d} score with {k} rounds to {val:+.2f}", val,
              round(float(A.bf_domain_pc_corr(m).loc[d, k]), 2), tol=1e-9, section=sec)


def figure_23_contrib(L: Ledger):
    """Figure 2.2 contributing-traits view (iteration 43): for each consensus direction, the 3 traits with the largest and the
    3 with the smallest AA18 consensus loading, re-ranked independently; low-end traits flipped; values equal the signed
    trait-PC correlations recomputed from the raw snapshot."""
    from . import figures as F
    sec = "2"
    d = S.csv("aa18_loadings")
    bad = 0
    for c in A.CONSENSUS:
        x = d[d.component == c]
        v = x.consensus_loading.astype(float).to_numpy()
        o = np.argsort(-v)
        want = list(x.trait.to_numpy()[o[:3]]) + list(x.trait.to_numpy()[o[::-1][:3]])
        bad += want != list(F.consensus_contrib(c).trait)
    L.add("2.3.contrib.rank", "RECOMPUTED", "Figure 2.3 (contributing traits): top 3 and bottom 3 traits per direction equal an independent ranking (mismatches)",
          0, bad, section=sec)
    f, _ = F.consensus_combined_figure()
    rows = pd.concat([F.consensus_contrib(c) for c in A.CONSENSUS]).reset_index(drop=True)
    pcs = S.csv("persona_pcs")
    for k, m in enumerate(["qwen", "gemma", "llama"]):
        raw = S.csv(f"traits_{m}")
        raw = raw.set_index(raw.columns[0]).astype(float)
        j = raw.join(pcs[pcs.model == m].set_index("persona")[[f"pc{q}" for q in range(1, 6)]].astype(float), how="inner")
        ind = np.array([[np.corrcoef(j[t] * sg, j[f"pc{q}"])[0, 1] for q in range(1, 6)] for t, sg in zip(rows.trait, rows.sign)])
        tr = [t for t in f.data if t.name == "Traits: " + A.MODEL_LABEL[m]][0]
        L.add(f"2.3.contrib.r.{m}", "RECOMPUTED", f"Figure 2.3 (contributing traits, {m}): 30 x 5 signed trait-PC r vs independent recomputation (max |diff|)",
              0.0, float(np.abs(np.array(tr.z) - ind).max()), tol=1e-10, section=sec)


def figure_elbow(L: Ledger):
    """Figure G.3a (iteration 44): explained variance per axis from the saved PCA diagnostics; prose numbers."""
    sec = "G"
    d = S.csv("pca_diag")
    for m in ["qwen", "gemma", "llama"]:
        x = d[d.model == m].sort_values("component")
        L.add(f"G.elbow.cum.{m}", "RECOMPUTED", f"Figure G.3a ({m}): cumulative share equals the running sum of the per-axis shares (max |diff|)",
              0.0, float((x.explained_variance_ratio.cumsum() - x.cumulative_explained_variance).abs().max()), tol=1e-9, section=sec)
    g = lambda m, c, col="explained_variance_ratio": round(100 * float(d[(d.model == m) & (d.component == c)][col].iloc[0]), 1)
    L.add("G.elbow.prose.pc1", "CHECKED", "Figure G.3a prose: PC1 carries 31.6% (Qwen), 23.5% (Gemma), 17.2% (Llama); Llama PC2 14.2%",
          (31.6, 23.5, 17.2, 14.2), (g("qwen", 1), g("gemma", 1), g("llama", 1), g("llama", 2)), section=sec)
    L.add("G.elbow.prose.qwen2", "CHECKED", "Figure G.3a prose: Qwen PC2 carries 16.2%", 16.2, g("qwen", 2), section=sec)
    L.add("G.elbow.prose.cum", "CHECKED", "Figure G.3a prose: PC1-PC3 together 56.4% / 41.9% / 37.9%; PC1-PC5 64.6% / 51.1% / 46.8%",
          (56.4, 41.9, 37.9, 64.6, 51.1, 46.8),
          tuple(g(m, c, "cumulative_explained_variance") for c in (3, 5) for m in ["qwen", "gemma", "llama"]), section=sec)
    L.add("G.elbow.prose.stab", "CHECKED", "Figure G.3a prose: PC1 stability (5th-percentile bootstrap cosine) .98 / .97 / .76",
          (0.98, 0.97, 0.76), tuple(round(float(d[(d.model == m) & (d.component == 1)].bootstrap_loading_cosine_q05.iloc[0]), 2)
                                    for m in ["qwen", "gemma", "llama"]), section=sec)


def figure_bm(L: Ledger):
    """Figure 3.1 (iteration 46): the combined Big Five matrix. The menu payload must reproduce the matrices it is built from:
    trait r per source (independently recomputed for the models), domain block averages, the split view's halves and the
    symmetric difference views."""
    from . import figures as F
    sec = "S"
    P = F.bigfive_matrix_payload()
    t = A.bf_traits()
    s = t.sign.to_numpy()
    for m in ["qwen", "gemma", "llama"]:
        X = A.trait_matrix(m)[list(t.trait)].to_numpy(float) * s
        Rr = np.corrcoef(X, rowvar=False)
        np.fill_diagonal(Rr, np.nan)
        L.add(f"S.bm.T.{m}", "RECOMPUTED", f"Figure 3.1 ({m}): menu trait matrix equals an independent np.corrcoef (max |diff|)", 0.0,
              float(np.nanmax(np.abs(np.array(P["T"][m], float) - Rr))), tol=1e-3, section=sec)
    pp = A.bf_corr("people").copy()
    np.fill_diagonal(pp, np.nan)
    L.add("S.bm.T.people", "CHECKED", "Figure 3.1 (people): menu trait matrix equals the sign-flipped SAPA proxy matrix (max |diff|)", 0.0,
          float(np.nanmax(np.abs(np.array(P["T"]["people"], float) - pp))), tol=1e-3, section=sec)
    Z = F.bm_split(np.array(P["D"]["qwen"], float), np.array(P["D"]["people"], float))
    L.add("S.bm.split.lower", "RECOMPUTED", "Figure 3.1 opening view: below the diagonal, Qwen Neuroticism–Extraversion average +.53",
          0.53, round(float(Z[1, 0]), 2), tol=1e-9, section=sec)
    L.add("S.bm.split.upper", "RECOMPUTED", "Figure 3.1 opening view: above the diagonal, people Neuroticism–Extraversion average −.21",
          -0.21, round(float(Z[0, 1]), 2), tol=1e-9, section=sec)
    for lvl in ["T", "D"]:
        Dm = np.array(P[lvl]["qwen"], float) - np.array(P[lvl]["people"], float)
        L.add(f"S.bm.diff.sym.{lvl}", "RECOMPUTED", f"Figure 3.1: Qwen − people difference ({'traits' if lvl == 'T' else 'domains'}) is symmetric, so both halves can show it (max |D − Dᵀ|)",
              0.0, float(np.nanmax(np.abs(Dm - Dm.T))), tol=1e-6, section=sec)
    L.add("S.bm.shapes", "RECOMPUTED", "Figure 3.1 payload shapes: traits 42 x 42, domains 5 x 5, trait-with-domain 42 x 5, PCs 42 x 5 and 5 x 5",
          True, all(np.array(P["T"][k], float).shape == (42, 42) and np.array(P["D"][k], float).shape == (5, 5)
                    and np.array(P["TB"][k], float).shape == (42, 5) for k in F.BM_SOURCES)
          and all(np.array(P["TP"][m], float).shape == (42, 5) and np.array(P["DP"][m], float).shape == (5, 5) for m in ["qwen", "gemma", "llama"]),
          section=sec)


def figure_tmap(L: Ledger):
    """Figure 1.2 (iteration 47): the 240 traits on PC1 and PC2/PC3. The payload equals an independent recomputation, no trait
    lies outside the unit circle (the PCs are uncorrelated), and every number and placement in the text is pinned."""
    from . import figures as F
    from . import landscape as LS
    sec = "1"
    P = F.trait_map_payload()
    cnt = {}
    for m in F.TM_MODELS:
        t = A.trait_matrix(m).to_numpy(float)
        pcs = LS.pcs(m).loc[LS.persona_order()][["pc1", "pc2", "pc3"]].to_numpy(float)
        Rr = np.array([[np.corrcoef(t[:, i], pcs[:, j])[0, 1] for j in range(3)] for i in range(t.shape[1])])
        got = np.column_stack([P["models"][m]["r"][c] for c in ["PC1", "PC2", "PC3"]])
        L.add(f"1.tmap.r.{m}", "RECOMPUTED", f"Figure 1.2 ({m}): trait-axis r equals an independent np.corrcoef (max |diff|)", 0.0,
              float(np.max(np.abs(got - Rr))), tol=1e-3, section=sec)
        L.add(f"1.tmap.circle.{m}", "RECOMPUTED", f"Figure 1.2 ({m}): no trait outside the unit circle, PC1-PC3 (max r1²+r2²+r3²)",
              True, bool((Rr ** 2).sum(axis=1).max() <= 1 + 1e-9), section=sec)
        cnt[m] = (int(((Rr[:, 0] ** 2 + Rr[:, 1] ** 2) >= 0.5).sum()), int(((Rr ** 2).sum(axis=1) >= 0.5).sum()))
    for m, (a, b) in {"qwen": (180, 228), "gemma": (187, 212), "llama": (188, 213)}.items():
        L.add(f"1.tmap.prose.{m}", "RECOMPUTED", f"Figure 1.2 prose: PC1 and PC2 explain at least half of {a} {m} traits; with PC3, {b}",
              True, cnt[m] == (a, b), section=sec)
    q, l = A.trait_pc_corr("qwen"), A.trait_pc_corr("llama")
    L.add("1.tmap.prose.qwen_pc1", "RECOMPUTED", "Figure 1.2 prose: Qwen PC1 ends are transparent (highest), factual (top 3) and narrative (lowest)",
          True, q.PC1.idxmax() == "transparent" and "factual" in q.PC1.nlargest(3).index and q.PC1.idxmin() == "narrative", section=sec)
    L.add("1.tmap.prose.qwen_pc3", "RECOMPUTED", "Figure 1.2 prose: Qwen PC3 top callous, vindictive (r > .85); bottom benevolent, supportive, forgiving (r < −.8)",
          True, bool(q.PC3.idxmax() == "callous" and q.loc["vindictive", "PC3"] > 0.85 and q.PC3.idxmin() == "benevolent"
                     and (q.loc[["benevolent", "supportive", "forgiving"], "PC3"] < -0.8).all()), section=sec)
    L.add("1.tmap.prose.llama_pc2", "RECOMPUTED", "Figure 1.2 prose: Llama PC2 runs from impulsive (highest) to calm (lowest)",
          True, l.PC2.idxmax() == "impulsive" and l.PC2.idxmin() == "calm", section=sec)

"""Assemble report tables from the snapshot. Keeps notebook cells short."""
from __future__ import annotations
from pathlib import Path

from functools import lru_cache

import numpy as np
import pandas as pd

from . import sources as S
from . import stats

FORMATS = ["scenario", "survey_style"]
FORMAT_LABEL = {"scenario": "Scenario", "survey_style": "Survey"}
# Reader-facing names for the two Qwen extraction formats.
FORMAT_NAME = {"scenario": "scenario prompts", "survey_style": "survey-style prompts"}
DOMAIN_ORDER = ["N", "E", "O", "A", "C"]
DOMAIN_NAME = {"N": "Neuroticism", "E": "Extraversion", "O": "Openness", "A": "Agreeableness", "C": "Conscientiousness"}
STYLE_COLS = ["historical_" + s for s in S.STYLES]


# ------------------------------------------------------------ basics
@lru_cache(None)
def codes() -> tuple[str, ...]:
    return tuple(S.jsonfile("d30b_point_stage")["completed_facets"])


@lru_cache(None)
def facet_names() -> dict[str, str]:
    items = S.csv("od_items")
    return dict(zip(items.facet_code, items.facet))


@lru_cache(None)
def ordered_codes() -> tuple[str, ...]:
    """The 26 facets for display: Big Five domain order N, E, O, A, C, then facet number."""
    return tuple(sorted(codes(), key=lambda c: (DOMAIN_ORDER.index(c[0]), int(c[1:]))))


def name(code: str) -> str:
    return facet_names()[code]


def pair_name(a: str, b: str) -> str:
    return f"{name(a)}–{name(b)}"


@lru_cache(None)
def profiles() -> tuple[tuple[str, ...], dict[str, np.ndarray]]:
    P = S.csv("d30b_profiles")
    ids = tuple(sorted(P.persona.unique()))
    Q = {s: P[P.source == s].set_index("persona").loc[list(ids), list(codes())].to_numpy(float) for s in FORMATS}
    return ids, Q


def facet_vector(code: str, source: str) -> np.ndarray:
    ids, Q = profiles()
    return Q[source][:, codes().index(code)]


@lru_cache(None)
def styles() -> np.ndarray:
    ids, _ = profiles()
    return S.csv("hist_styles48").set_index("persona").loc[list(ids), STYLE_COLS].to_numpy(float)


# ------------------------------------------------------------ Section 4
@lru_cache(None)
def pairs325() -> pd.DataFrame:
    """325 pairs: saved human/Qwen r, recomputed Qwen r, frozen and recomputed screen."""
    rel = S.csv("d30b_relationships")
    wide = rel.pivot_table(index=["left", "right"], columns="source", values=["human_reference", "model_persona"], sort=False)
    out = pd.DataFrame({
        "left": [i[0] for i in wide.index], "right": [i[1] for i in wide.index],
        "human": wide[("human_reference", "scenario")].to_numpy(),
        "human_survey_copy": wide[("human_reference", "survey_style")].to_numpy(),
        "scenario_saved": wide[("model_persona", "scenario")].to_numpy(),
        "survey_saved": wide[("model_persona", "survey_style")].to_numpy(),
    })
    _, Q = profiles()
    cs = list(codes())
    R = {s: stats.corr_matrix(Q[s]) for s in FORMATS}
    out["scenario"] = [R["scenario"][cs.index(a), cs.index(b)] for a, b in zip(out.left, out.right)]
    out["survey"] = [R["survey_style"][cs.index(a), cs.index(b)] for a, b in zip(out.left, out.right)]
    names = facet_names()
    out["pair"] = out.left + "__" + out.right
    out["label"] = [f"{names[a]} – {names[b]}" for a, b in zip(out.left, out.right)]
    frozen = S.csv("od_all_pairs").set_index("pair")
    out["group_frozen"] = out.pair.map(frozen.group)
    out["human_od"] = out.pair.map(frozen.human)
    out["group_recomputed"] = stats.screen(out.human, out.scenario, out.survey)
    # Display summary (iteration 6): Qwen r averaged over the two prompt formats. The frozen screen above
    # still uses both formats separately.
    out["qwen"] = (out.scenario + out.survey) / 2
    return out


def matrices() -> dict[str, np.ndarray]:
    """26x26 matrices in frozen facet order: human, scenario, survey."""
    cs = list(codes())
    n = len(cs)
    p = pairs325()
    out = {}
    for key, col in [("human", "human"), ("scenario", "scenario"), ("survey_style", "survey"), ("qwen", "qwen")]:
        M = np.eye(n)
        for a, b, v in zip(p.left, p.right, p[col]):
            i, j = cs.index(a), cs.index(b)
            M[i, j] = M[j, i] = v
        out[key] = M
    return out


def r2_table() -> pd.DataFrame:
    fr = S.csv("d30b_facet_results")
    ri = S.csv("d30b_resp_int")
    ei = S.csv("d30b_extr_int")
    rows = []
    for c in codes():
        row = dict(facet=c, name=facet_names()[c])
        hr = fr[(fr.facet == c) & (fr.condition == "human_reference")]
        row["R2_human"] = float(hr.R2.iloc[0])
        for s in FORMATS:
            m = fr[(fr.facet == c) & (fr.condition == "model") & (fr.source == s)].iloc[0]
            row[f"R2_{s}"] = float(m.R2)
            row[f"S_{s}"] = float(m.S)
            r = ri[(ri.facet == c) & (ri.condition == s) & (ri.metric == "R2")].iloc[0]
            e = ei[(ei.facet == c) & (ei.source == s) & (ei.metric == "R2")].iloc[0]
            row[f"resp_lo_{s}"], row[f"resp_hi_{s}"] = float(r.lower), float(r.upper)
            row[f"extr_lo_{s}"], row[f"extr_hi_{s}"] = float(e.lower), float(e.upper)
        rows.append(row)
    return pd.DataFrame(rows)


def macro_intervals() -> pd.DataFrame:
    r = S.csv("d30b_macro_resp").rename(columns={"condition": "source"})
    e = S.csv("d30b_macro_extr")
    r["family"] = "Respondents; fits fixed"
    e["family"] = "Questions; conditional extraction"
    d = pd.concat([r, e])
    return d[d.metric == "R2"][["family", "source", "confidence", "median", "lower", "upper", "draws_defined", "draws_total"]]


def calibration() -> pd.DataFrame:
    return stats.calibration_table(S.csv("cal12_test"), S.csv("cal12_mult"))


# ------------------------------------------------------------ Section 5
def e1n2(source: str) -> tuple[np.ndarray, np.ndarray]:
    return facet_vector("E1", source), facet_vector("N2", source)


def conditioning_table() -> pd.DataFrame:
    """E1-N2 raw and conditioned correlations, plus variance removed."""
    St = styles()
    rows = []
    for s in FORMATS:
        x, y = e1n2(s)
        for cond, C in [("raw", None), ("conditioned on Formal", St[:, :1]), ("conditioned on five styles", St)]:
            rows.append(dict(
                source=s, condition=cond, r=stats.partial_corr(x, y, C),
                var_removed_E1=np.nan if C is None else stats.variance_removed(x, C),
                var_removed_N2=np.nan if C is None else stats.variance_removed(y, C)))
    return pd.DataFrame(rows)


def loo_e1n2() -> pd.DataFrame:
    ids, _ = profiles()
    rows = []
    for s in FORMATS:
        x, y = e1n2(s)
        r0 = stats.pearson(x, y)
        loo = stats.leave_one_out(x, y)
        rows.append(pd.DataFrame(dict(source=s, persona=list(ids), r_without=loo, change=loo - r0)))
    return pd.concat(rows, ignore_index=True)


GROUP_SCHEMES = {
    "new_semantic_group": "exclude_semantic__",
    "legacy_canonical_family": "exclude_legacy_canonical__",
    "legacy_consensus_family": "exclude_legacy_consensus__",
}


# The frozen study transported 15 eligible group exclusions; the 6-persona
# legacy canonical "other" family was not eligible, so it is not excluded here.
INELIGIBLE_GROUPS = {("legacy_canonical_family", "other")}


def group_exclusions_e1n2() -> pd.DataFrame:
    """Recompute E1-N2 after excluding each frozen analytical group, and the ordinary-role subset."""
    ids, _ = profiles()
    cls = S.csv("od_persona_class", keep_default_na=False).set_index("persona").loc[list(ids)]
    rows = []
    for s in FORMATS:
        x, y = e1n2(s)
        for col, prefix in GROUP_SCHEMES.items():
            g = stats.group_exclusion(x, y, cls[col].to_numpy())
            for _, r in g.iterrows():
                if (col, r.group) in INELIGIBLE_GROUPS:
                    continue
                rows.append(dict(source=s, scheme=col, condition=prefix + r.group, n=r.n, r=r.r))
        keep = cls.ordinary_role_subset.astype(str).str.lower().eq("true").to_numpy()
        rows.append(dict(source=s, scheme="ordinary_role_subset", condition="ordinary_human_roles", n=int(keep.sum()),
                         r=stats.pearson(x[keep], y[keep])))
    return pd.DataFrame(rows)


def saved_composition(pair: str = "E1__N2") -> pd.DataFrame:
    d = S.csv("od_composition")
    return d[d.pair == pair]


def item_wording(facets=("E1", "N2")) -> pd.DataFrame:
    it = S.csv("od_items")
    it = it[it.facet_code.isin(facets)][["facet_code", "facet", "item_number", "wording", "original_response_sign"]]
    it = it.copy()
    it["key"] = np.where(it.original_response_sign > 0, "+ (as worded)", "− (reverse-keyed in source)")
    return it.drop(columns="original_response_sign")


def anger_items() -> pd.DataFrame:
    d = S.csv("ha_items")
    d = d[d.metric == "Pearson"]
    wide = d.pivot_table(index=["item_number", "wording", "original_response_sign"], columns="outcome",
                         values=["anger_keyed_r", "simultaneous_95_lower", "simultaneous_95_upper"]).reset_index()
    wide.columns = ["_".join([c for c in col if c]) if isinstance(col, tuple) else col for col in wide.columns]
    return wide


def cross_model_table() -> pd.DataFrame:
    d = S.csv("cross_primary")
    d = d[d.family.isin(["social_approach_hostility", "care_hostility"])]
    lab = {"uniform": "raw", "condition_formal": "conditioned on Formal", "condition_core5": "conditioned on five styles"}
    d = d.assign(view=d.condition.map(lab), relationship=[
        ("Negative " if p < 0 else "") + f"{a.title()} – {b.title()}" for a, b, p in zip(d.left, d.right, d.polarity)])
    return d[["relationship", "model", "view", "adjusted_Pearson", "lower", "upper"]]


CM01_FOCAL = [("avoidant", "hostile", -1), ("charismatic", "hostile", 1), ("flirty", "hostile", 1),
              ("nurturing", "hostile", 1), ("adventurous", "avoidant", 1), ("charismatic", "gregarious", 1)]


def cm01_table() -> pd.DataFrame:
    d = S.csv("cm01_pairs")
    rows = []
    for a, b, pol in CM01_FOCAL:
        for m in ["Qwen", "Llama", "Gemma"]:
            r = d[(d.model == m) & (((d.trait_a == a) & (d.trait_b == b)) | ((d.trait_a == b) & (d.trait_b == a)))].iloc[0]
            rows.append(dict(relationship=("Negative " if pol < 0 else "") + f"{a.title()} × {b.title()}", model=m,
                             r=pol * r.pearson, lower=min(pol * r.ci95_low, pol * r.ci95_high),
                             upper=max(pol * r.ci95_low, pol * r.ci95_high)))
    return pd.DataFrame(rows)


def factor_patterns() -> pd.DataFrame:
    d = S.csv("cm01_all240")
    w = d.pivot_table(index="trait", columns="factor", values="empirical_pearson")
    return w


def factor_congruence(fa: str, fb: str) -> float:
    d = S.csv("cm01_all240")
    a = d[d.factor == fa].set_index("trait").pattern_loading
    b = d[d.factor == fb].set_index("trait").pattern_loading.loc[a.index]
    return float((a @ b) / np.sqrt((a @ a) * (b @ b)))


def ctf_contributions() -> pd.DataFrame:
    """Projected and residual additive contributions to Qwen r, 13 reversals, C/T/F."""
    ct = S.csv("ctgeo_pairs")
    ct = ct[ct.frozen_group == "consistent_reversal"]
    ct = ct.assign(pair=ct.left + "__" + ct.right)[["source", "geometry", "pair", "left", "right", "human_marginal_r",
                                                    "model_marginal_r", "projected_additive_contribution",
                                                    "residual_additive_contribution"]]
    f = S.csv("fexp_pairs")
    f = f[f.group == "consistent_reversal"].assign(geometry="F")
    f = f.rename(columns={"pair": "pair"})[["source", "geometry", "pair", "left", "right", "human_marginal_r",
                                             "model_marginal_r", "projected_additive_contribution",
                                             "residual_additive_contribution"]]
    out = pd.concat([ct, f], ignore_index=True)
    names = facet_names()
    out["label"] = [f"{names[a]} – {names[b]}" for a, b in zip(out.left, out.right)]
    return out


def domain_blocks() -> pd.DataFrame:
    """Equal-weight mean of saved facet-pair correlations within each Big Five domain pair.

    Descriptive only: an average of the 325 saved pair correlations (people, Qwen scenario,
    Qwen survey-style), lower triangle of the 5 x 5 domain grid including the diagonal.
    """
    p = pairs325()
    order = DOMAIN_ORDER
    rows = []
    for i, di in enumerate(order):
        for j, dj in enumerate(order[: i + 1]):
            m = ((p.left.str[0] == di) & (p.right.str[0] == dj)) | ((p.left.str[0] == dj) & (p.right.str[0] == di))
            g = p[m]
            rows.append(dict(row=di, col=dj, row_name=DOMAIN_NAME[di], col_name=DOMAIN_NAME[dj], n_pairs=int(len(g)),
                             human=g.human.mean(), scenario=g.scenario_saved.mean(), survey=g.survey_saved.mean()))
    d = pd.DataFrame(rows)
    d["diff_scenario"] = d.scenario - d.human
    d["diff_survey"] = d.survey - d.human
    d["qwen"] = (d.scenario + d.survey) / 2  # average of the two formats (equals the block mean of averaged pairs)
    d["diff_qwen"] = d.qwen - d.human
    return d


# ------------------------------------------------------------ Iteration 5 (descriptive)
@lru_cache(None)
def ordinary_mask() -> np.ndarray:
    """Frozen ordinary-role subset (outlier study c556609), aligned to the persona order."""
    ids, _ = profiles()
    cls = S.csv("od_persona_class", keep_default_na=False).set_index("persona").loc[list(ids)]
    return cls.ordinary_role_subset.astype(str).str.lower().eq("true").to_numpy()


@lru_cache(None)
def pairs325_ordinary() -> pd.DataFrame:
    """Qwen pair correlations recomputed on the 130 ordinary-role characters (people values unchanged)."""
    _, Q = profiles()
    keep = ordinary_mask()
    cs = list(codes())
    p = pairs325()[["pair", "left", "right", "label", "human"]].copy()
    for fmt, col in [("scenario", "scenario"), ("survey_style", "survey")]:
        R = stats.corr_matrix(Q[fmt][keep])
        p[col] = [R[cs.index(a), cs.index(b)] for a, b in zip(p.left, p.right)]
    return p


def domain_blocks_from(p: pd.DataFrame, cols: dict) -> pd.DataFrame:
    rows = []
    for i, di in enumerate(DOMAIN_ORDER):
        for dj in DOMAIN_ORDER[: i + 1]:
            m = ((p.left.str[0] == di) & (p.right.str[0] == dj)) | ((p.left.str[0] == dj) & (p.right.str[0] == di))
            g = p[m]
            rows.append(dict(row=di, col=dj, row_name=DOMAIN_NAME[di], col_name=DOMAIN_NAME[dj], n_pairs=int(len(g)),
                             **{k: g[v].mean() for k, v in cols.items()}))
    return pd.DataFrame(rows)


def domain_blocks_ordinary() -> pd.DataFrame:
    """Domain averages for the 130 ordinary roles (Qwen only; people from the full reference sample)."""
    d = domain_blocks_from(pairs325_ordinary(), {"human": "human", "scenario": "scenario", "survey": "survey"})
    d["diff_scenario"] = d.scenario - d.human
    d["diff_survey"] = d.survey - d.human
    return d


def facet_fit() -> pd.DataFrame:
    """For each facet: mean correlation with the other facets in its own domain (people, Qwen scenario, Qwen survey)."""
    p = pairs325()
    rows = []
    for c in ordered_codes():
        m = ((p.left == c) | (p.right == c)) & (p.left.str[0] == p.right.str[0])
        g = p[m]
        rows.append(dict(facet=c, name=name(c), domain=DOMAIN_NAME[c[0]], n_pairs=int(len(g)), human=g.human.mean(),
                         scenario=g.scenario_saved.mean(), survey=g.survey_saved.mean()))
    return pd.DataFrame(rows)


# ------------------------------------------------------------ Iteration 7: Direct-30 B rescaling (saved aggregates)
def rescaled_table() -> pd.DataFrame:
    """Per facet and format: as-measured and common-rescaled R² (respondent 95% intervals), question-resampling 95%
    intervals for the rescaled R², and the exploratory facet-specific result. From the calibration package (677d4f2)."""
    fc = S.csv("cal30_facets")
    qi = S.csv("cal30_qint")
    q = qi[qi.metric == "calibrated_R2"].set_index(["source", "facet"])
    rows = []
    for fmt in FORMATS:
        for c in ordered_codes():
            r = fc[(fc.source == fmt) & (fc.facet == c)].iloc[0]
            rows.append(dict(source=fmt, facet=c, name=name(c), original=r.original_R2,
                             rescaled=r.common_calibrated_R2, resp_lo=r.common_calibrated_ci95_low,
                             resp_hi=r.common_calibrated_ci95_high, q_lo=q.loc[(fmt, c), "lower"], q_hi=q.loc[(fmt, c), "upper"],
                             multiplier=r.common_primary, facet_mult=r.facet_exploratory,
                             facet_R2=r.facet_calibrated_exploratory_R2, facet_lo=r.facet_calibrated_exploratory_ci95_low,
                             facet_hi=r.facet_calibrated_exploratory_ci95_high))
    return pd.DataFrame(rows)


def rescaled_macro() -> pd.DataFrame:
    """Macro means per format (recomputed from the per-facet values) with the saved macro question intervals."""
    t = rescaled_table()
    qi = S.csv("cal30_qint")
    out = []
    for fmt in FORMATS:
        g = t[t.source == fmt]
        m = qi[(qi.source == fmt) & (qi.facet == "MACRO")].set_index("metric")
        out.append(dict(source=fmt, as_measured=g.original.mean(), rescaled=g.rescaled.mean(),
                        q_lo=m.loc["calibrated_R2", "lower"], q_hi=m.loc["calibrated_R2", "upper"],
                        improved=int((g.rescaled > g.original).sum()), multiplier=float(g.multiplier.iloc[0]),
                        # 95% question-resampling interval for the as-measured average (same package, same draws)
                        am_q_lo=m.loc["original_R2", "lower"], am_q_hi=m.loc["original_R2", "upper"]))
    return pd.DataFrame(out)


# ------------------------------------------------------------ Iteration 9 (3.2, descriptive)
def format_agreement() -> pd.DataFrame:
    """Per facet: Pearson r between scenario- and survey-prompt scores across the 275 characters (domain order)."""
    _, Q = profiles()
    cs = list(codes())
    rows = [dict(facet=c, name=name(c), domain=c[0], r=stats.pearson(Q["scenario"][:, cs.index(c)], Q["survey_style"][:, cs.index(c)]))
            for c in ordered_codes()]
    return pd.DataFrame(rows)


def format_pair_agreement() -> tuple[float, float]:
    """Agreement of the 325 trait-pair correlations between the two methods: Pearson r and share with the same sign."""
    p = pairs325()
    return stats.pearson(p.scenario, p.survey), float((np.sign(p.scenario) == np.sign(p.survey)).mean())


# ------------------------------------------------------------ Iteration 11 (Section 2, descriptive)
MODEL_PAIRS = [("qwen", "gemma"), ("qwen", "llama"), ("llama", "gemma")]  # iteration 27: Qwen, Gemma, Llama order
MODEL_LABEL = {"qwen": "Qwen", "llama": "Llama", "gemma": "Gemma"}
FOCAL_HIST_PAIRS = [("nurturing", "hostile"), ("flirty", "hostile"), ("avoidant", "hostile")]


@lru_cache(None)
def hist_trait_corr(model: str) -> np.ndarray:
    """240 x 240 trait correlation matrix across the 275 characters, on the cross-model study's primary scale
    (e01cacb): each saved cosine column is midrank-normal transformed, Phi^-1((average_rank - .5) / 275), then Pearson."""
    from scipy.stats import norm, rankdata
    from . import landscape as LS
    X = LS.traits_raw(model).loc[LS.persona_order(), LS.trait_order()].to_numpy(float)
    Z = norm.ppf((np.apply_along_axis(rankdata, 0, X) - 0.5) / X.shape[0])
    return np.corrcoef(Z, rowvar=False)


def hist_pair_cells(model: str) -> np.ndarray:
    """The 28,680 unordered trait-pair correlations (upper triangle, row-major)."""
    C = hist_trait_corr(model)
    return C[np.triu_indices(C.shape[0], 1)]


def model_pair_agreement() -> pd.DataFrame:
    rows = []
    for a, b in MODEL_PAIRS:
        x, y = hist_pair_cells(a), hist_pair_cells(b)
        slope, icpt = stats.ols(x, y)
        rows.append(dict(a=a, b=b, r=stats.pearson(x, y), slope=slope, intercept=icpt, sma=stats.sma(x, y)[0], n=len(x),
                         same_sign=int((np.sign(x) == np.sign(y)).sum())))
    return pd.DataFrame(rows)


def focal_hist_pairs() -> pd.DataFrame:
    from . import landscape as LS
    T = LS.trait_order()
    rows = []
    for t1, t2 in FOCAL_HIST_PAIRS:
        i, j = T.index(t1), T.index(t2)
        rows.append(dict(label=f"{t1.capitalize()}–{t2.capitalize()}",
                         **{m: float(hist_trait_corr(m)[i, j]) for m in MODEL_LABEL}))
    return pd.DataFrame(rows)


# ------------------------------------------------------------ Iteration 14 (Appendix G, descriptive)
PCAX_TARGET = {"llama": "Llama-3.3-70B", "gemma": "Gemma-2-27B"}
AA19_STATUS = {"A_independently_supported": "Independently supported", "B_partial_human_analogue": "Partial human analogue",
               "C_human_combination": "Human combination", "D_presently_untestable": "Presently untestable"}


def persona_score_agreement() -> pd.DataFrame:
    """G.2 (computed in this notebook): for each of the 240 traits, Pearson r of its 275 character scores between two
    models, from the saved cosine matrices. One row per trait and model pair."""
    from . import landscape as LS
    P, T = LS.persona_order(), LS.trait_order()
    X = {m: LS.traits_raw(m).loc[P, T].to_numpy(float) for m in MODEL_LABEL}
    rows = []
    for a, b in MODEL_PAIRS:
        xa, xb = X[a] - X[a].mean(0), X[b] - X[b].mean(0)
        r = (xa * xb).sum(0) / np.sqrt((xa * xa).sum(0) * (xb * xb).sum(0))
        rows += [dict(a=a, b=b, trait=t, r=float(v)) for t, v in zip(T, r)]
    return pd.DataFrame(rows)


def pc_correspondence(model: str, k: int = 6) -> np.ndarray:
    """G.3: saved signed Pearson r between Qwen PC i (rows) and the other model's PC j (columns), i, j = 1..k."""
    d = S.csv("pca_xmodel")
    d = d[(d.target_model == PCAX_TARGET[model]) & (d.reference_component <= k) & (d.target_component <= k)]
    return d.pivot(index="reference_component", columns="target_component", values="pearson_correlation").to_numpy()


def pc_plane_cca(model: str, k: int = 2) -> np.ndarray:
    """G.3 (computed in this notebook): canonical correlations between the Qwen PC1..PCk plane and the other model's
    PC1..PCk plane, from the saved persona PC scores (275 characters). QR + SVD of the centred score blocks."""
    from . import landscape as LS
    P = LS.persona_order()
    cols = [f"pc{i}" for i in range(1, k + 1)]
    Aq = LS.pcs("qwen").loc[P, cols].to_numpy(float)
    Bm = LS.pcs(model).loc[P, cols].to_numpy(float)
    qa, _ = np.linalg.qr(Aq - Aq.mean(0))
    qb, _ = np.linalg.qr(Bm - Bm.mean(0))
    return np.linalg.svd(qa.T @ qb, compute_uv=False)


def factor_match_matrix(a: str, b: str) -> tuple[list, list, np.ndarray, np.ndarray]:
    """G.4: AA17 factor-to-factor Tucker congruence (signed) for one model pair, from PHG-CM01 (original_pattern; equals
    AA17 cross_model_factor_alignment.csv), and the matched-pair mask."""
    d = S.csv("cm01_matches")
    d = d[(d.method == "original_pattern") & (d.model_a == MODEL_LABEL[a]) & (d.model_b == MODEL_LABEL[b])]
    fa, fb = sorted(d.factor_a.unique()), sorted(d.factor_b.unique())
    C = d.pivot(index="factor_a", columns="factor_b", values="signed_congruence").loc[fa, fb].to_numpy()
    Mk = d.pivot(index="factor_a", columns="factor_b", values="matched").loc[fa, fb].to_numpy().astype(bool)
    return fa, fb, C, Mk


def consensus_table() -> pd.DataFrame:
    """G.5: AA18 consensus components C1-C5 (saved shared-dimension diagnostics) with the AA19 human status."""
    dg = S.csv("aa18_diag")
    dg = dg[dg.supported_consensus_axis.astype(str) == "True"].copy()
    dg["component"] = "C" + dg.component.astype(str)
    cl = S.csv("aa19_comp").set_index("component")
    out = dg[["component", "projector_eigenvalue", "heldout_mean_pairwise_pearson"]].copy()
    out["status"] = out.component.map(cl.classification).map(AA19_STATUS)
    out["human_projection_r"] = out.component.map(cl.human_subspace_projection_r)
    out["bridge_adequate"] = out.component.map(cl.bridge_adequate)
    return out.reset_index(drop=True)


# ------------------------------------------------------------ Iteration 15 (Appendix F as a table)
GROUP_LABEL = {"consistent_reversal": "Reversal", "close_agreement": "Close match"}


def format_results() -> pd.DataFrame:
    """Headline results for each prompt method (Appendix F.2). Values recomputed from the saved profiles and
    calibration package; the reversal and close-match counts come from the frozen screen, which uses both methods."""
    p = pairs325()
    m = rescaled_macro().set_index("source")
    rows = []
    for fmt, col in [("scenario", "scenario"), ("survey_style", "survey")]:
        rows.append(dict(source=fmt,
                         pattern_r=stats.pearson(p.human, p[col]),
                         same_sign=float((np.sign(p.human) == np.sign(p[col])).mean()),
                         spread=stats.sma(p.human, p[col])[0],
                         r2_measured=float(m.loc[fmt, "as_measured"]),
                         r2_rescaled=float(m.loc[fmt, "rescaled"]),
                         multiplier=float(m.loc[fmt, "multiplier"]),
                         n_reversal=int((p.group_frozen == "consistent_reversal").sum()),
                         n_close=int((p.group_frozen == "close_agreement").sum())))
    return pd.DataFrame(rows).set_index("source")


def pairs_by_format() -> pd.DataFrame:
    """325 trait pairs: people r and Qwen r under both prompt methods, with the frozen class (aggregates only)."""
    p = pairs325()
    return pd.DataFrame({"Facet pair": p.label, "People r": p.human, "Qwen r, main text": p.scenario,
                         "Qwen r, survey-style": p.survey,
                         "Class (frozen screen)": p.group_frozen.map(GROUP_LABEL).fillna("")})


def survey_r2_table() -> pd.DataFrame:
    """Per-facet prediction R² for the survey-style extraction (formerly the Figure F.4 details table)."""
    r2f = r2_table().set_index("facet")
    rtf = rescaled_table().query("source == 'survey_style'")
    rtf = rtf.assign(human=r2f.loc[rtf.facet, "R2_human"].to_numpy(),
                     e_lo=r2f.loc[rtf.facet, "extr_lo_survey_style"].to_numpy(),
                     e_hi=r2f.loc[rtf.facet, "extr_hi_survey_style"].to_numpy())
    return rtf[["name", "human", "original", "e_lo", "e_hi", "rescaled", "q_lo", "q_hi", "resp_lo", "resp_hi"]].rename(columns={
        "name": "Facet", "human": "Human benchmark", "original": "Qwen", "e_lo": "Qwen, prompts 95% lower",
        "e_hi": "Qwen, prompts 95% upper", "rescaled": "Qwen, calibrated", "q_lo": "Calibrated, prompts 95% lower",
        "q_hi": "Calibrated, prompts 95% upper", "resp_lo": "Calibrated, test respondents 95% lower",
        "resp_hi": "Calibrated, test respondents 95% upper"})


# ------------------------------------------------------------ Iteration 18 (Figure 2.2)
CONSENSUS = ["C1", "C2", "C3", "C4", "C5"]
# Iteration 53: reader-facing names D1-D5 (C1-C5 also name the Conscientiousness facets); internal keys stay C1-C5.
DLAB = {c: "D" + c[1:] for c in CONSENSUS}


def dlab(c: str) -> str:
    return DLAB.get(c, c)


@lru_cache(None)
def consensus_pc_corr(model: str, k: int = 5) -> np.ndarray:  # PC1-PC5 since iteration 25
    """Figure 2.2 (computed in this notebook): Pearson r across the 275 characters between the model's own AA18 score on
    each consensus direction C1-C5 (rows) and the model's activation PC1..PCk (columns). Signs are arbitrary."""
    from . import landscape as LS
    P = LS.persona_order()
    pcs = LS.pcs(model).loc[P]
    sc = S.csv("aa18_scores")
    out = np.zeros((len(CONSENSUS), k))
    for i, c in enumerate(CONSENSUS):
        v = sc[sc.component == c].set_index("persona").loc[P, f"{model}_score"].to_numpy(float)
        for j in range(k):
            out[i, j] = stats.pearson(v, pcs[f"pc{j + 1}"].to_numpy(float))
    return out


# ------------------------------------------------------------ Iteration 19 (key to the consensus directions)
# AA18 report's post-fit candidate labels (three_model_consensus_trait_report.md, main 65da790): "candidate" readings of
# stable axes, not causal traits or demonstrated human dimensions. Short form used on the Figure 2.2 axis.
CONSENSUS_LABEL = {
    "C1": ("Charged expression vs factual moderation", "charged vs moderate"),
    "C2": ("Abstract inwardness vs situated practicality", "abstract vs practical"),
    "C3": ("Forgiving care vs blunt prescription", "caring vs blunt"),
    "C4": ("Integrative exploration vs literal tradition", "exploring vs traditional"),
    "C5": ("Decisive closure vs deferential caution", "decisive vs cautious"),
}
AA19_PLAIN = {"A_independently_supported": "Independently supported in people",
              "B_partial_human_analogue": "Partial human analogue",
              "C_human_combination": "A combination of human factors",
              "D_presently_untestable": "Not yet testable (too few human measures)"}


def consensus_poles(c: str, n: int = 5) -> tuple[list, list]:
    """Top-n traits at each end of a consensus direction, by AA18 consensus loading: [(trait, loading)], high then low."""
    d = S.csv("aa18_loadings")
    x = d[d.component == c].assign(v=lambda t: t.consensus_loading.astype(float)).sort_values("v")
    hi = list(zip(x.trait[::-1][:n], x.v[::-1][:n]))
    lo = list(zip(x.trait[:n], x.v[:n]))
    return hi, lo


def consensus_key() -> pd.DataFrame:
    """One row per consensus direction: label, trait poles, the matching activation axis in each model (largest |r| in
    Figure 2.2) and the AA19 human status."""
    aa19 = S.csv("aa19_comp").set_index("component")
    rows = []
    for i, c in enumerate(CONSENSUS):
        hi, lo = consensus_poles(c)
        row = dict(component=c, label=CONSENSUS_LABEL[c][0], short=CONSENSUS_LABEL[c][1],
                   high=", ".join(t.replace("_", " ") for t, _ in hi), low=", ".join(t.replace("_", " ") for t, _ in lo),
                   human=AA19_PLAIN[aa19.loc[c, "classification"]])
        for m in ["qwen", "gemma", "llama"]:
            r = consensus_pc_corr(m)[i]
            j = int(np.argmax(np.abs(r)))
            row[f"{m}_pc"], row[f"{m}_r"] = j + 1, float(r[j])
        rows.append(row)
    return pd.DataFrame(rows)


# ------------------------------------------------------------ Iteration 20 (Figures 2.3 and 3.1)
FACTOR_LABEL = {  # short readings of the top historical traits at each pole of Qwen's AA17 factors (fexp_poles, fc764f8)
    "F1": "calm vs edgy", "F2": "accessible vs pedantic", "F3": "grounded vs idealistic", "F4": "literal vs holistic",
    "F5": "decisive vs pluralist"}
MODEL_FACTORS = {"qwen": 5, "llama": 6, "gemma": 6}


def factor_scores(model: str) -> pd.DataFrame:
    """AA17 factor scores for one model, 275 characters (rows, persona order) x F1..Fk."""
    from . import landscape as LS
    d = S.csv("aa17_scores")
    lab = MODEL_LABEL[model]
    w = d[d.model == lab].assign(score=lambda t: t.score.astype(float)).pivot(index="persona", columns="factor", values="score")
    w.columns = [c.split("_")[-1] for c in w.columns]
    return w.loc[LS.persona_order(), [f"F{k}" for k in range(1, MODEL_FACTORS[model] + 1)]]


def consensus_scores(model: str) -> np.ndarray:
    from . import landscape as LS
    sc = S.csv("aa18_scores")
    P = LS.persona_order()
    return np.column_stack([sc[sc.component == c].set_index("persona").loc[P, f"{model}_score"].astype(float).to_numpy()
                            for c in CONSENSUS])


@lru_cache(None)
def factor_consensus_corr(model: str) -> np.ndarray:
    """Figure 2.3 (computed in this notebook): r across the 275 characters between the model's AA17 factors (rows) and its
    own scores on C1-C5 (columns)."""
    Fm = factor_scores(model).to_numpy(float)
    Cm = consensus_scores(model)
    return np.array([[stats.pearson(Fm[:, i], Cm[:, j]) for j in range(5)] for i in range(Fm.shape[1])])


def factor_poles(n: int = 3) -> pd.DataFrame:
    """Qwen F1-F5: top-n historical traits at each pole (saved, fc764f8)."""
    d = S.csv("fexp_poles")
    d = d[d["rank"].astype(int) <= n]
    out = []
    for f in [f"F{k}" for k in range(1, 6)]:
        q = d[d.factor == f]
        out.append(dict(factor=f, label=FACTOR_LABEL[f],
                        high=", ".join(q[q.pole == "positive"].sort_values("rank").trait.str.replace("_", " ")),
                        low=", ".join(q[q.pole == "negative"].sort_values("rank").trait.str.replace("_", " "))))
    return pd.DataFrame(out)


def facet_direction_matrix(view: str, source: str = "scenario") -> tuple[np.ndarray, list]:
    """Figure 3.1 (computed in this notebook): Qwen facet (rows, domain order) x five directions; view in {C, F, PC}.
    Returns (r matrix, R² of each facet on the five directions together)."""
    from . import landscape as LS
    P = LS.persona_order()
    _, Q = profiles()
    cs = list(codes())
    X = Q[source]
    if view == "C":
        M = consensus_scores("qwen")
    elif view == "F":
        M = factor_scores("qwen").to_numpy(float)
    else:
        M = LS.pcs("qwen").loc[P, [f"pc{k}" for k in range(1, 6)]].to_numpy(float)
    order = list(ordered_codes())
    Z = np.array([[stats.pearson(X[:, cs.index(f)], M[:, k]) for k in range(5)] for f in order])
    D = np.column_stack([np.ones(len(M)), M])
    r2 = []
    for f in order:
        y = X[:, cs.index(f)]
        b = np.linalg.lstsq(D, y, rcond=None)[0]
        r2.append(float(1 - ((y - D @ b) ** 2).sum() / ((y - y.mean()) ** 2).sum()))
    return Z, r2


@lru_cache(None)
def factor_pc_corr(model: str, k: int = 6) -> np.ndarray:
    """Figure 1.2 (computed in this notebook): r across the 275 characters between the model's AA17 factors (rows) and its
    own activation PC1..PCk (columns)."""
    from . import landscape as LS
    Fm = factor_scores(model).to_numpy(float)
    pcs = LS.pcs(model).loc[LS.persona_order(), [f"pc{j}" for j in range(1, k + 1)]].to_numpy(float)
    return np.array([[stats.pearson(Fm[:, i], pcs[:, j]) for j in range(k)] for i in range(Fm.shape[1])])


def factor_pc_r2(model: str, k: int = 6) -> list:
    """Share of each factor's variance explained by the model's PC1..PCk together (OLS R²)."""
    from . import landscape as LS
    Fm = factor_scores(model).to_numpy(float)
    pcs = LS.pcs(model).loc[LS.persona_order(), [f"pc{j}" for j in range(1, k + 1)]].to_numpy(float)
    D = np.column_stack([np.ones(len(pcs)), pcs])
    return [float(1 - ((f - D @ np.linalg.lstsq(D, f, rcond=None)[0]) ** 2).sum() / ((f - f.mean()) ** 2).sum()) for f in Fm.T]


# ------------------------------------------------------------ Iteration 21 (Figure 1.2: what the main axes separate)
PC_MAP_NAMES = ["auditor", "assistant", "poet", "leviathan", "teenager", "toddler", "ascetic", "eldritch",
                "caregiver", "cynic", "revolutionary", "soldier",
                # Iteration 37: angel and demon, the contrast Lu et al. (2026) call out; opposite ends of Qwen's PC3.
                "angel", "demon",
                # Iteration 38: contrasts at the factual end (theorist/pragmatist on PC2, robot/mediator on PC3) and
                # secretary, near zero on PC2 and PC3, as poet's counterpart on PC1.
                "secretary", "theorist", "pragmatist", "robot", "mediator"]


def pc_map_traits(model: str = "qwen", k: int = 3) -> list:
    """Iteration 22 (k = 3 since iteration 23): the trait menu of Figure 1.2: the strongest trait at the high and low end of
    PC1..PCk (from the axis guide), then conscientious as the diagonal PC1-PC2 example. Returns [(trait, label)]."""
    g = axis_guide(model, k)
    out = []
    for row in g.itertuples():
        out += [(row.high[0], f"{row.high[0].replace('_', ' ').capitalize()} ({row.axis} high)"),
                (row.low[0], f"{row.low[0].replace('_', ' ').capitalize()} ({row.axis} low)")]
    out.append(("conscientious", "Conscientious (PC1–PC2 diagonal)"))
    return out


def trait_matrix(model: str) -> pd.DataFrame:
    """Saved 275 x 240 trait scores for one model (rows in persona order)."""
    from . import landscape as LS
    t = S.csv(f"traits_{model}")
    t = t.set_index(t.columns[0])
    return t.loc[LS.persona_order()].astype(float)


@lru_cache(None)
def trait_pc_corr(model: str, k: int = 5) -> pd.DataFrame:
    """Figure 1.2 (computed in this notebook): Pearson r across the 275 characters between each of the 240 trait scores and
    the model's activation PC1..PCk (rows: traits, columns: PC1..PCk)."""
    from . import landscape as LS
    t = trait_matrix(model)
    pcs = LS.pcs(model).loc[LS.persona_order()]
    return pd.DataFrame({f"PC{j}": [stats.pearson(t[c].to_numpy(), pcs[f"pc{j}"].to_numpy(float)) for c in t.columns]
                         for j in range(1, k + 1)}, index=t.columns)


def axis_guide(model: str = "qwen", k: int = 5, n: int = 3, m: int = 2) -> pd.DataFrame:
    """One row per activation axis: the n traits most positively and most negatively correlated with it (with r), and the
    m characters furthest toward each end."""
    from . import landscape as LS
    r = trait_pc_corr(model, k)
    pcs = LS.pcs(model).loc[LS.persona_order()]
    out = []
    for j in range(1, k + 1):
        s = r[f"PC{j}"].sort_values()
        o = pcs[f"pc{j}"].astype(float).sort_values()
        out.append(dict(axis=f"PC{j}", high=list(s.index[::-1][:n]), high_r=list(s.values[::-1][:n]),
                        low=list(s.index[:n]), low_r=list(s.values[:n]),
                        high_chars=list(o.index[::-1][:m]), low_chars=list(o.index[:m]),
                        strongest=float(max(abs(s.values[0]), abs(s.values[-1])))))
    return pd.DataFrame(out)


def pca_variance(model: str) -> pd.Series:
    """Saved share of variation explained per persona PC (pca_diag)."""
    d = S.csv("pca_diag")
    d = d[d.model == model]
    return pd.Series(d.explained_variance_ratio.astype(float).to_numpy(), index=d.component.astype(int).to_numpy())


# ------------------------------------------------------------ Iteration 25 (Figure 1.2 with a model menu)
PC_MAP_MODELS = ["qwen", "gemma", "llama"]


def diagonal_trait(model: str, axis: str) -> str:
    """The trait that sits most evenly between PC1 and `axis` (largest min(|r with PC1|, |r with axis|))."""
    r = trait_pc_corr(model)
    return str(np.minimum(r["PC1"].abs(), r[axis].abs()).idxmax())


# Iteration 37: for Qwen's PC1 the map offers conceptually illustrative traits instead of the top-ranked ones (transparent,
# narrative): factual (+.95, 13th of 240) and dramatic (-.97, 6th), both nearly pure PC1. The axis guide keeps the empirical
# top three. Other models keep the strongest-correlation rule.
PC1_ILLUSTRATIVE = {"qwen": ("factual", "dramatic")}


def pc_map_options(model: str, axis: str) -> list:
    """Trait menu for one model and vertical axis: PC1 high, PC1 low, axis high, axis low, then the PC1-axis diagonal.
    Returns [(trait, label)]."""
    r = trait_pc_corr(model)
    lab = lambda t: t.replace("_", " ").capitalize()
    hi, lo = PC1_ILLUSTRATIVE.get(model, (r["PC1"].idxmax(), r["PC1"].idxmin()))
    out = [(hi, "PC1 high"), (lo, "PC1 low"), (r[axis].idxmax(), f"{axis} high"),
           (r[axis].idxmin(), f"{axis} low"), (diagonal_trait(model, axis), f"PC1–{axis} diagonal")]
    return [(t, f"{lab(t)} ({w})") for t, w in out]


# ------------------------------------------------------------ Iteration 31: Figure 1.3 (historical traits by Big Five domain)
BF_LETTER = {"neuroticism": "N", "extraversion": "E", "openness": "O", "agreeableness": "A", "conscientiousness": "C"}


@lru_cache(None)
def bf_traits() -> pd.DataFrame:
    """The 42 traits of the frozen human-anchored strict mapping, ordered by domain (as in Figure 4.2), then IPIP-NEO
    facet, then name. Reverse-keyed traits (polarity negative) get a "(−)" label and are sign-flipped in bf_scores."""
    m = S.csv("bf_strict_map")
    d = pd.DataFrame({"trait": m.trait, "domain": m.external_domain.map(BF_LETTER), "facet": m.external_facet_code,
                      "facet_name": m.external_facet, "sign": np.where(m.polarity == "negative", -1.0, 1.0)})
    d["label"] = [t.replace("_", " ") + (" (−)" if s < 0 else "") for t, s in zip(d.trait, d.sign)]
    d["_o"] = d.domain.map(DOMAIN_ORDER.index)
    d["_f"] = d.facet.str[1:].astype(int)
    return d.sort_values(["_o", "_f", "trait"]).drop(columns=["_o", "_f"]).reset_index(drop=True)


def bf_scores(model: str) -> pd.DataFrame:
    """275 x 42 saved trait scores, reverse-keyed traits multiplied by −1 so each points toward its domain's high pole."""
    t = bf_traits()
    return trait_matrix(model)[list(t.trait)] * t.sign.to_numpy()


@lru_cache(None)
def bf_trait_corr(model: str) -> np.ndarray:
    """42 x 42 Pearson r across the 275 characters between the signed trait scores (computed in this notebook)."""
    return stats.corr_matrix(bf_scores(model).to_numpy(float))


@lru_cache(None)
def bf_people_corr() -> np.ndarray:
    """42 x 42 SAPA trait-proxy r (people), in bf_traits order, reverse-keyed traits sign-flipped as for the models.
    Proxies are oriented toward the trait as named (anxious-calm r < 0), so the same flips apply."""
    t = bf_traits()
    h = S.csv("bf_sapa_corr")
    h = h.set_index(h.columns[0]).loc[list(t.trait), list(t.trait)].to_numpy(float)
    s = t.sign.to_numpy()
    out = h * np.outer(s, s)
    np.fill_diagonal(out, 1.0)
    return out


def bf_corr(source: str) -> np.ndarray:
    """source: 'people' or a model key."""
    return bf_people_corr() if source == "people" else bf_trait_corr(source)


def bf_composites(model: str) -> pd.DataFrame:
    """Domain scores as in the source study: mean of positive-keyed minus mean of reverse-keyed trait scores. Up to one
    constant per domain this equals the projection on the study's unit domain direction, so correlations match its
    saved big_five_domain_intercorrelations.csv (checked)."""
    t = bf_traits()
    s = bf_scores(model)  # signed, so the reverse-keyed mean enters with a minus sign already
    out = {}
    for d in DOMAIN_ORDER:
        g = t[t.domain == d]
        pos, neg = list(g.trait[g.sign > 0]), list(g.trait[g.sign < 0])
        out[d] = (s[pos].mean(axis=1) if pos else 0.0) + (s[neg].mean(axis=1) if neg else 0.0)
    return pd.DataFrame(out)


@lru_cache(None)
def bf_domain_blocks(model: str) -> pd.DataFrame:
    """Lower triangle of the 5 x 5 grid: equal-weight mean of the trait-pair correlations in each domain block (as the
    Figure 4.2 domain view does for facets; within a domain, distinct pairs only), plus the domain-score correlation."""
    t = bf_traits()
    Rm = bf_corr(model)
    C = None if model == "people" else bf_composites(model)
    rows = []
    for i, di in enumerate(DOMAIN_ORDER):
        for dj in DOMAIN_ORDER[: i + 1]:
            a = np.flatnonzero(t.domain == di)
            b = np.flatnonzero(t.domain == dj)
            vals = [Rm[p, q] for p in a for q in b if (di != dj or p > q)]
            rows.append(dict(row=di, col=dj, row_name=DOMAIN_NAME[di], col_name=DOMAIN_NAME[dj], n_pairs=len(vals),
                             mean_r=float(np.mean(vals)),
                             domain_r=(1.0 if di == dj else (float("nan") if C is None
                                                             else stats.pearson(C[di].to_numpy(), C[dj].to_numpy())))))
    return pd.DataFrame(rows)


def bf_block(model: str, a: str, b: str, col: str = "mean_r") -> float:
    d = bf_domain_blocks(model)
    m = ((d.row == a) & (d.col == b)) | ((d.row == b) & (d.col == a))
    return float(d.loc[m, col].iloc[0])


# ------------------------------------------------------------ Iteration 32 side preview: traits vs Big Five domains
def bf_people_domains() -> pd.DataFrame:
    """42 x 5 (N, E, O, A, C): SAPA proxy r with the official IPIP100 domain scales (proxy items removed from each scale;
    Neuroticism = inverse Emotional Stability), rows in bf_traits order, reverse-keyed rows sign-flipped."""
    t = bf_traits()
    h = S.csv("bf_sapa_domains").set_index("trait").loc[list(t.trait)]
    cols = {d: f"{n.lower()}_pearson_r" for d, n in DOMAIN_NAME.items()}
    return pd.DataFrame({d: h[cols[d]].to_numpy(float) * t.sign.to_numpy() for d in DOMAIN_ORDER}, index=t.label)


@lru_cache(None)
def bf_model_domains(model: str) -> pd.DataFrame:
    """42 x 5: r across the 275 characters between each signed trait score and each domain score built from the OTHER
    mapped traits (pole means as in bf_composites, the row trait left out), so no trait is compared with itself."""
    t = bf_traits()
    s = bf_scores(model)
    out = np.full((len(t), 5), np.nan)
    for i, tr in enumerate(t.trait):
        for j, d in enumerate(DOMAIN_ORDER):
            g = t[(t.domain == d) & (t.trait != tr)]
            pos, neg = list(g.trait[g.sign > 0]), list(g.trait[g.sign < 0])
            sc = (s[pos].mean(axis=1) if pos else 0.0) + (s[neg].mean(axis=1) if neg else 0.0)
            out[i, j] = stats.pearson(s[tr].to_numpy(), np.asarray(sc, float))
    return pd.DataFrame(out, index=t.label, columns=DOMAIN_ORDER)


def bf_domains(source: str) -> pd.DataFrame:
    return bf_people_domains() if source == "people" else bf_model_domains(source)


# ------------------------------------------------------------ Iteration 32: Figure 6.1 (domain correlations across sources)
PUBLISHED_DOMAIN_FILE = S.ROOT / "data" / "published" / "domain_correlations_petrov2024.csv"
PUBLISHED_DOMAIN_SHA256 = "f11440d489d4b0832025b0b17a28cc3162339ca7ef176e27840752a3a67a696f"
PETROV_URL = "https://github.com/nikbpetrov/LLMs-Simulate-Humans"
PETROV_COMMIT = "85c3c2f78d5371cf16b71b8b94006d379b4c24fd"
DOMAIN_PAIRS = [(a, b) for i, a in enumerate(DOMAIN_ORDER) for b in DOMAIN_ORDER[i + 1:]]


def petrov_intercorrs() -> pd.DataFrame:
    """Published values used by Figure5.1, from PHG's cited 10-pair table.

    This reader path never opens the original third-party file or downloads data.
    Values remain attributed to Petrov et al. (2024), Figure4.
    """
    d = pd.read_csv(PUBLISHED_DOMAIN_FILE)
    columns = ["bbc_humans", "gpt35_generic", "gpt4_generic", "gpt35_silicon", "gpt4_silicon"]
    pairs = list(zip(d.domain_a, d.domain_b))
    if pairs != DOMAIN_PAIRS or d[columns].shape != (10, 5) or not np.isfinite(d[columns].to_numpy()).all():
        raise ValueError("Published domain table must contain the ten ordered pairs and fifty finite coefficients")
    out = d.set_index(["domain_a", "domain_b"])[columns].copy()
    out.columns = ["bbc", "generic_gpt35", "generic_gpt4", "silicon_gpt35", "silicon_gpt4"]
    # Preserve the former table's index names as well as its numerical values.
    out.index.names = [None, None]
    out.columns.name = "model"
    return out


def facet_domain_score_corr(key: str) -> pd.Series:
    """Correlation between unit-weighted domain scores built from our 26 facets (standardized), derived exactly from the
    26 x 26 facet correlation matrix: r(A, B) = sum R_AB / sqrt(sum R_AA * sum R_BB). key: human | scenario | survey_style."""
    R = matrices()[key]
    cs = list(codes())
    idx = {d: [i for i, c in enumerate(cs) if c[0] == d] for d in DOMAIN_ORDER}
    return pd.Series({(a, b): float(R[np.ix_(idx[a], idx[b])].sum() /
                                    np.sqrt(R[np.ix_(idx[a], idx[a])].sum() * R[np.ix_(idx[b], idx[b])].sum()))
                      for a, b in DOMAIN_PAIRS})


def domain_corr_sources() -> pd.DataFrame:
    """Figure 6.1 table: domain-score correlations, one column per source."""
    p = petrov_intercorrs()
    q = pd.Series({(a, b): bf_block("qwen", a, b, "domain_r") for a, b in DOMAIN_PAIRS})
    return pd.DataFrame({
        "people_bbc": p.bbc, "people_ipip": facet_domain_score_corr("human"),
        "gpt35_generic": p.generic_gpt35, "gpt4_generic": p.generic_gpt4,
        "gpt35_silicon": p.silicon_gpt35, "gpt4_silicon": p.silicon_gpt4,
        "qwen_facets": facet_domain_score_corr("scenario"), "qwen_traits": q,
        "gemma_traits": pd.Series({(a, b): bf_block("gemma", a, b, "domain_r") for a, b in DOMAIN_PAIRS}),
        "llama_traits": pd.Series({(a, b): bf_block("llama", a, b, "domain_r") for a, b in DOMAIN_PAIRS}),
    })


# Post hoc sign templates for Figure 6.1 (defined after seeing the data; descriptive only).
VALENCE_SIGN = {"N": -1, "E": 1, "O": 1, "A": 1, "C": 1}     # desirable traits together, Neuroticism opposite
INTENSITY_SIGN = {"N": 1, "E": 1, "O": 1, "A": -1, "C": -1}  # expressive traits together, composed traits opposite


def template_fit() -> pd.DataFrame:
    """Pearson r between each source's ten domain correlations and the two sign templates, and with BBC people."""
    D = domain_corr_sources()
    tv = np.array([VALENCE_SIGN[a] * VALENCE_SIGN[b] for a, b in D.index], float)
    ti = np.array([INTENSITY_SIGN[a] * INTENSITY_SIGN[b] for a, b in D.index], float)
    return pd.DataFrame({c: {"valence": stats.pearson(D[c].to_numpy(), tv), "intensity": stats.pearson(D[c].to_numpy(), ti),
                             "people_bbc": stats.pearson(D[c].to_numpy(), D.people_bbc.to_numpy())} for c in D}).T


# ------------------------------------------------------------ Iteration 33: Section 4 elicitation (Codex 598857c)
CHECKPOINTS = [8, 12, 16, 24, 32, 48, 64]
EXCLUDED_NAMES = {"N3": "Depression", "N5": "Immoderation", "E3": "Assertiveness", "C3": "Dutifulness"}


def all30_codes() -> list:
    return [f"{d}{k}" for d in DOMAIN_ORDER for k in range(1, 7)]


def facet_label30(c: str) -> str:
    return EXCLUDED_NAMES.get(c) or name(c)


def stopping_table() -> pd.DataFrame:
    """One row per facet x format: stopping n (NaN if none), facet qualified, last evaluated checkpoint, available
    accepted questions, and the gate values at the stopping checkpoint."""
    f = S.csv("conv_final")
    h = S.csv("conv_hist")
    h = h.drop_duplicates(["facet", "format", "checkpoint_n"])
    rows = []
    for r in f.itertuples():
        g = h[(h.facet == r.facet) & (h.format == r.format)]
        stop = g[g.checkpoint_n == r.stopping_n] if pd.notna(r.stopping_n) else g.iloc[0:0]
        rows.append(dict(facet=r.facet, format=r.format, stopping_n=r.stopping_n, qualified=bool(r.facet_qualified),
                         status=r.status, available=int(r.available_accepted), last_checkpoint=int(r.last_evaluated_checkpoint),
                         p05=float(stop.bootstrap_p05_cosine.iloc[0]) if len(stop) else np.nan,
                         prev=float(stop.cosine_to_previous_checkpoint.iloc[0]) if len(stop) else np.nan))
    return pd.DataFrame(rows)


def question_cloud(facet: str, fmt: str = "scenario") -> tuple:
    """Question directions (cosines with PC1-48..PC3-48) and the running/final mean direction for one facet/format."""
    q = S.csv("conv_q")
    q = q[(q.facet == facet) & (q.format == fmt)]
    m = S.csv("conv_mean")
    m = m[(m.facet == facet) & (m.format == fmt)]
    return q, m[m.estimate_kind == "scheduled_checkpoint"].sort_values("n"), m[m.estimate_kind == "final_accepted"]


def bridge_domain_summary() -> pd.DataFrame:
    """Section 3 (iteration 33): per source, mean r of each trait with its own domain, share of traits whose strongest
    domain is their own, Extraversion traits with Neuroticism and Neuroticism traits with Extraversion."""
    t = bf_traits()
    rows = []
    for s_, lab in [("people", "People (SAPA)"), ("qwen", "Qwen"), ("gemma", "Gemma"), ("llama", "Llama")]:
        D = bf_domains(s_)
        own = np.array([D.iloc[i][d] for i, d in enumerate(t.domain)])
        hit = np.mean([DOMAIN_ORDER[k] == d for k, d in zip(D.to_numpy().argmax(1), t.domain)])
        rows.append({"Source": lab, "Mean r with own domain": own.mean(), "Own domain strongest (share)": hit,
                     "Extraversion traits with Neuroticism": D[t.domain.values == "E"]["N"].mean(),
                     "Neuroticism traits with Extraversion": D[t.domain.values == "N"]["E"].mean()})
    return pd.DataFrame(rows)


# ------------------------------------------------------------ Iteration 40: Figure 1.2 (Big Five traits on the axes)
@lru_cache(None)
def bf_pc_corr(model: str, k: int = 3) -> pd.DataFrame:
    """42 x k: r across the 275 characters between each signed Big Five trait score and the model's PC1..PCk."""
    from . import landscape as LS
    pcs = LS.pcs(model).loc[LS.persona_order()]
    s = bf_scores(model)
    t = bf_traits()
    return pd.DataFrame({f"PC{j}": [stats.pearson(s[tr].to_numpy(), pcs[f"pc{j}"].to_numpy(float)) for tr in t.trait]
                         for j in range(1, k + 1)}, index=list(t.label))


GEN_COUNTS_FILE = S.SNAPSHOT_DIR / "external" / "extraction_generated_counts_20261117.csv"
# Iteration 54: September 24 calibration (codex/adaptive-trait-hifwb-extraction-20260924 @ 2524afc, calibration_report.md):
# signed cosine between the adaptive-rule direction and Lu et al.'s released Qwen direction.
CALIBRATION_COS = {"flippant": 0.980466, "pensive": 0.965569, "accessible": 0.969196}
LU_RESPONSES_PER_POLE = 2400


def extraction_counts() -> pd.DataFrame:
    """Iteration 54 (Appendix A.14): generated / rejected / accepted-extra question pairs per qualified facet and format,
    reconstructed by GPT from the Direct-12, Direct-18 and Direct-30 A/B execution journals (Nov 17), merged with the
    convergence audit's final counts (stopping n, accepted available, accepted extras)."""
    g = pd.read_csv(GEN_COUNTS_FILE)
    d = S.csv("conv_final")
    return g.merge(d[["facet", "format", "stopping_n", "available_accepted", "accepted_extras", "facet_qualified"]],
                   on=["facet", "format"], how="left")


@lru_cache(None)
def bf_domain_consensus_corr(model: str) -> pd.DataFrame:
    """Iteration 53 (Section 3 prose): 5 x 5 r across the 275 characters between each Big Five domain score
    (bf_composites, rows N E O A C) and the model's own score on each shared direction (columns C1-C5 internally,
    shown as D1-D5), from the saved shared-direction scores."""
    sp = S.csv("aa18_scores")
    piv = sp.pivot(index="persona", columns="component", values=f"{model}_score")[CONSENSUS]
    c = bf_composites(model)
    piv = piv.loc[list(c.index)]
    return pd.DataFrame({k: [stats.pearson(c[d].to_numpy(float), piv[k].to_numpy(float)) for d in DOMAIN_ORDER]
                         for k in CONSENSUS}, index=DOMAIN_ORDER)


def bf_domain_pc_corr(model: str, k: int = 3) -> pd.DataFrame:
    """5 x k: r between each Big Five domain score (bf_composites) and the model's PC1..PCk."""
    from . import landscape as LS
    pcs = LS.pcs(model).loc[LS.persona_order()]
    c = bf_composites(model)
    return pd.DataFrame({f"PC{j}": [stats.pearson(c[d].to_numpy(), pcs[f"pc{j}"].to_numpy(float)) for d in DOMAIN_ORDER]
                         for j in range(1, k + 1)}, index=[DOMAIN_NAME[d] for d in DOMAIN_ORDER])

"""Snapshot integrity, frozen headline values, verification ledger and figures."""
import numpy as np
import pytest

from phg import analysis as A, checks, figures as F, report as R, sources as S

KNOWN_PROSE_ROUNDING = {
    "5d.cm01.Charismatic × Hostile.Llama",
    "5d.cross.Nurturing – Hostile.Qwen.conditioned on five styles",
}


def test_snapshot_hashes():
    assert all(r["ok"] for r in S.verify_snapshot())


def test_snapshot_rederives_from_packaged_evidence():
    res = S.verify_against_evidence()
    if any(r["ok"] is None for r in res):
        pytest.skip("source deliberately excluded from package")
    assert all(r["ok"] for r in res)


def test_headline_e1n2():
    p = A.pairs325().set_index("pair").loc["E1__N2"]
    assert round(p.scenario, 4) == 0.7098 and round(p.survey, 4) == 0.6071
    assert round(p.human, 4) == -0.2805


def test_thirteen_reversals():
    p = A.pairs325()
    assert (p.group_recomputed == "consistent_reversal").sum() == 13
    assert (p.group_recomputed == p.group_frozen).all()


def test_ledger_no_failures_and_known_notes():
    L = R.Ledger()
    checks.section4(L)
    checks.section5(L)
    assert not [c.id for c in L.checks if c.status == "FAIL"]
    notes = {c.id: c.note for c in L.checks if c.status == "NOTE"}
    assert "4.caption.respondent_width" not in notes  # iteration 9: caption corrected, NOTE removed
    assert set(notes) == KNOWN_PROSE_ROUNDING
    assert all("is used" in n for n in notes.values())


def test_brief_rounding_classification():
    L = R.Ledger()
    checks._brief(L, "a", "d", 0.500, 0.5004, "x")   # within rounding
    checks._brief(L, "b", "d", -0.526, -0.525468, "x")  # brief rounds differently
    checks._brief(L, "c", "d", 0.500, 0.510, "x")    # genuine mismatch
    assert [c.status for c in L.checks] == ["PASS", "NOTE", "FAIL"]


def test_check_evaluation():
    assert R.Check("a", "CHECKED", "d", 1.0, 1.0 + 1e-12).status == "PASS"
    assert R.Check("a", "CHECKED", "d", 1.0, 1.1, tol=0.01).status == "FAIL"
    assert R.Check("a", "CHECKED", "d", 1.0, None).status == "SKIPPED"
    with pytest.raises(ValueError):
        R.Check("a", "MAYBE", "d", 1, 1)


def test_evidence_panel_omits_empty_slots():
    assert R.evidence_panel("4.3", {}) == ""
    h = R.evidence_panel("4.3", {"4.3": {"shows": "A finding."}})
    assert "What it shows" in h and "Principal limitation" not in h and "PROSE TBD" not in h


def test_prose_file_seeds():
    from phg import prose
    p = prose.load()
    assert prose.get("H", "how_to_read", p).startswith("Each dot is one facet pair")  # iteration 49
    assert prose.get("4.2", "how_to_read", p).endswith("tap a cell to see both values.")
    assert all(k in p for k, _ in prose.ENTRIES)


def test_prose_parse_ignores_comments():
    from phg import prose
    p = prose.parse("## 4.1\n<!-- hint -->\n### lead\nHello\n### shows\n\n## 4.2\n### lead\n")
    assert p["4.1"] == {"lead": "Hello", "shows": ""} and p["4.2"]["lead"] == ""


def test_scatter_has_no_in_plot_labels_and_rings_focal_pair():
    fig = F.human_vs_qwen_scatter()
    assert not any(t.mode and "text" in t.mode for t in fig.data)
    assert any(t.name == "Friendliness–Anger" for t in fig.data)
    assert [t.name for t in fig.data if t.showlegend is not False][:3] == ["Other pairs", "Close match (6)",
                                                                          "Reversed in Qwen (13)"]


@pytest.mark.parametrize("name", ["human_vs_qwen_scatter", "correlation_matrices", "heldout_r2", "calibration_slider", "ctf_bars",
                                  "influence_figure", "style_scatter", "anger_items_figure", "anger_bands_figure",
                                  "cross_model_figure", "factor_pattern_figure"])
def test_figures_have_visible_initial_state(name):
    fig = getattr(F, name)()
    assert any(t.visible in (None, True) for t in fig.data)


def test_style_views_keep_original_slope_visible():
    fig = F.style_scatter()
    names = [t.name for t in fig.data]
    for b in fig.layout.updatemenus[0].buttons:
        vis = b.args[0]["visible"]
        shown = [n for n, v in zip(names, vis) if v]
        assert any(n.startswith("Best fit") for n in shown), b.label
        if b.label != "Raw":
            assert any(n.startswith("Original fit") for n in shown)


def test_calibration_slider_undefined_ordering_at_zero():
    fig = F.calibration_slider()
    step0 = fig.layout.sliders[0].steps[0]
    assert step0.label == "0.00"
    assert all(np.isnan(v) for v in step0.args[0]["x"][3])
    assert "undefined" in step0.args[1]["annotations"][0]["text"]


def test_domain_blocks_cover_all_pairs_once():
    d = A.domain_blocks()
    assert len(d) == 15 and d.n_pairs.sum() == 325
    within = d[d.row == d.col].set_index("row").n_pairs.to_dict()
    assert within == {"N": 6, "E": 10, "O": 15, "A": 15, "C": 10}
    assert np.allclose(d.diff_scenario, d.scenario - d.human)


def test_matrix_full_and_domain_views():
    fig = F.correlation_matrices()
    z = np.asarray(fig.data[0].z, float)
    off = ~np.eye(26, dtype=bool)
    assert np.isnan(np.diag(z)).all() and np.isfinite(z[off]).all() and np.allclose(z, z.T, equal_nan=True)
    labels = [b.label for b in fig.layout.updatemenus[0].buttons]
    assert labels == ["People", "Qwen", "Qwen − People", "Domains: People", "Domains: Qwen", "Domains: Qwen − People"]
    assert not [a for a in fig.layout.annotations if "–" in (a.text or "")]  # guided outlines removed
    assert not [t for t in fig.data if t.type == "scatter"]
    dz = np.asarray(fig.data[3].z, float)
    assert np.isfinite(dz).all() and np.allclose(dz, dz.T)
    assert sum((a.name or "").startswith("domband|facet") for a in fig.layout.annotations) == 10


def test_iteration5_expected_values():
    b = A.domain_blocks_ordinary().set_index(["row", "col"])
    for (di, dj), (es, ev) in checks.ORDINARY_BLOCKS.items():
        assert abs(b.loc[(di, dj), "scenario"] - es) < 0.005 and abs(b.loc[(di, dj), "survey"] - ev) < 0.005
    fit = A.facet_fit().set_index("facet")
    for c, vals in checks.FACET_FIT.items():
        assert np.allclose(fit.loc[c, ["human", "scenario", "survey"]].astype(float), vals, atol=0.005)
    assert A.ordinary_mask().sum() == 130


def prose_get(k, slot):
    from phg import prose
    return prose.get(k, slot)


def test_draft_outlines_toggle(monkeypatch):
    monkeypatch.setenv("PHG_DRAFT", "1")
    # Iteration 49: every former outline is written text; no draft boxes remain, and body text renders lists and subheads.
    assert R.outline_html("summary") == "" and R.outline_html("discussion") == ""
    h = R.body_html("summary")  # iteration 50: the Introduction (no findings list; the abstract is deferred)
    assert "Draft outline" not in h and h.count("<li>") == 0 and h.startswith("<p class='phg-body'>Large language models raise two complementary challenges")
    d = R.body_html("discussion")
    assert d.count("class='phg-subhead'") == 4 and R.body_html("discussion.0").startswith("<p class='phg-body'>The three models agree with one another") and "Appendix A.14" in prose_get("s3.1", "body")  # iteration 54


def test_outline_text_verbatim():
    from phg import prose
    p = prose.load()
    assert prose.get("4.4", "body", p).startswith("Outside this block, the clearest misfits")  # iteration 54
    assert prose.get("discussion", "body", p).startswith("#### Other evidence points the other way") and "#### The next step" in prose.get("discussion", "body", p)  # iteration 55
    assert "#### Why it matters" in prose.get("discussion", "body", p)
    assert prose.get("E.2", "how_to_read", p) == ("Each row is one facet, placed by how strongly it goes together, on average, "
                                                 "with the other facets in its domain. Facets far to the left sit loosely in their domain.")


def test_iteration5b_moves_and_rank_checks():
    from phg import prose
    p = prose.load()
    assert "Appendix E.6" in prose.get("4.4", "body", p)  # iteration 36: prediction moved to the appendix
    assert prose.get("E.2", "lead", p).startswith("Facets that sit loosely in their own domain")  # iteration 49
    L = R.Ledger()
    checks.section4(L)
    checks.appendix_e(L)
    rank = {c.id: c for c in L.checks if c.id.startswith("4.rank.")}
    assert set(rank) == {"4.rank.scenario", "4.rank.survey", "4.rank.human"} and all(c.status == "PASS" for c in rank.values())
    assert all(c.section == "E" for c in L.checks if c.id.startswith("4.fit."))
    f = F.heldout_r2()
    assert sum((a.name or "").startswith("domband|pred") for a in f.layout.annotations) == 5


def test_iteration6_averaging_and_captions():
    from phg import prose
    p = A.pairs325()
    assert np.allclose(p.qwen, (p.scenario + p.survey) / 2)
    assert (p.group_frozen == "consistent_reversal").sum() == 13  # frozen classes unchanged by averaging
    fig = F.human_vs_qwen_scatter()
    assert not fig.layout.updatemenus and len(fig.data) == 6
    assert any("agreement r = .44 · Qwen links 2.0x as strong as people" in (a.text or "") for a in fig.layout.annotations)
    pr = prose.load()
    assert prose.get("4.3", "how_to_read", pr).startswith("Qwen, calibrated: predictions shrunk toward the average")
    assert prose.get("4.4", "body", pr).rstrip().endswith("The comparison above does not depend on prediction.")  # iteration 49
    h = F.heldout_r2()
    assert not h.layout.updatemenus  # iteration 9: scenario only, no format menu
    assert {t.name for t in h.data} == {"Human benchmark", "Qwen, calibrated", "Qwen"}


def test_iteration7_rescaled():
    m = A.rescaled_macro().set_index("source")
    assert abs(m.loc["scenario", "rescaled"] - 0.254224) < 5e-6 and abs(m.loc["survey_style", "rescaled"] - 0.252502) < 5e-6
    assert abs(m.loc["scenario", "as_measured"] - 0.045794) < 5e-6 and abs(m.loc["survey_style", "as_measured"] - 0.078076) < 5e-6
    assert int(m.loc["scenario", "improved"]) == 20 and int(m.loc["survey_style", "improved"]) == 19
    assert abs(m.loc["scenario", "multiplier"] - 0.529452) < 1e-6 and abs(m.loc["survey_style", "multiplier"] - 0.549380) < 1e-6
    t = A.rescaled_table()
    assert len(t) == 52 and t[["resp_lo", "resp_hi", "q_lo", "q_hi"]].notna().all().all()
    assert ((t.resp_lo <= t.rescaled) & (t.rescaled <= t.resp_hi)).all()
    h = F.heldout_r2()
    assert len(h.data) == 3
    texts = " ".join(a.text or "" for a in h.layout.annotations)
    assert "Qwen, calibrated +0.254 [+0.232, +0.269]" in texts and "Qwen +0.046 [-0.009, +0.095]" in texts
    assert "Human benchmark +0.584" in texts


def test_iteration8_labels_and_figure_43():
    h = F.heldout_r2()
    # One marker and one bar per series; no hidden or helper traces; benchmark has no bar.
    assert [t.name for t in h.data] == ["Human benchmark", "Qwen", "Qwen, calibrated"]
    assert h.data[0].error_x.array is None
    assert h.data[1].marker.symbol == "circle-open" and h.data[2].marker.symbol == "circle"
    assert h.layout.legend.itemclick is False and h.layout.legend.itemdoubleclick is False
    assert all(t.visible is True for t in h.data) and not h.layout.updatemenus
    assert h.layout.meta == "How well Qwen's trait links predict real people's facet scores"
    assert h.layout.xaxis.title.text.startswith("Prediction accuracy (R²; below 0 is worse")
    H = F.human_vs_qwen_scatter()
    assert H.layout.meta == "Trait-pair correlations in people and in Qwen"
    assert H.layout.xaxis.title.text == "Correlation between the two traits in people (r)"
    assert H.layout.yaxis.title.text == "Correlation between the two traits in Qwen (r)"
    M = F.correlation_matrices()
    assert M.layout.meta == "Trait correlations (r)"
    assert all("meta" not in b.args[1] for b in M.layout.updatemenus[0].buttons)  # iteration 9: titles never change
    assert M.data[2].colorbar.title.text == "Qwen r − people r" and M.data[0].colorbar.title.text == "r"
    # Every figure: a title in meta, no in-chart title, dropdown labels of 1-3 words, short legend entries.
    for name in ["human_vs_qwen_scatter", "correlation_matrices", "heldout_r2", "calibration_slider", "ctf_bars",
                 "influence_figure", "style_scatter", "anger_items_figure", "anger_bands_figure", "cross_model_figure",
                 "factor_pattern_figure", "facet_fit_figure", "format_agreement_figure", "model_pairs_figure"]:
        fig = getattr(F, name)()
        assert isinstance(fig.layout.meta, str) and fig.layout.meta and not (fig.layout.title.text or ""), name
        assert "?" not in fig.layout.meta, name
        for m in fig.layout.updatemenus:
            for b in m.buttons:
                assert 1 <= len([w for w in b.label.replace(",", " ").replace(":", " ").split() if w not in ("+", "−")]) <= 3, (name, b.label)
        for t in fig.data:
            if t.showlegend is not False and t.name and t.type != "heatmap" and t.type != "box":
                assert len(t.name.split()) <= 5 and "<br>" not in t.name, (name, t.name)
    lab = R.fig_label_html("H", "x")
    assert "<b>Figure 4.1.</b>" in lab  # iteration 36 display numbers


MAIN_FIGURES = ["human_vs_qwen_scatter", "correlation_matrices", "heldout_r2", "ctf_bars", "influence_figure", "style_scatter",
                "anger_items_figure", "anger_bands_figure", "cross_model_figure", "factor_pattern_figure"]


def _visible_text(fig):
    out = [fig.layout.meta or "", fig.layout.xaxis.title.text or "", fig.layout.yaxis.title.text or ""]
    out += [a.text or "" for a in fig.layout.annotations]
    out += [b.label for m in fig.layout.updatemenus for b in m.buttons]
    out += [t.name or "" for t in fig.data if t.showlegend is not False]
    out += [str(t.y[0]) for t in fig.data if t.type == "box"]
    for t in fig.data:
        if t.type == "heatmap" and t.colorbar and t.colorbar.title:
            out.append(t.colorbar.title.text or "")
    for b in [m.buttons for m in fig.layout.updatemenus]:
        for x in b:
            for v in x.args[1:]:
                out += [str(w) for k, w in v.items() if k.endswith("title.text")]
                out += [a["text"] for a in v.get("annotations", []) if isinstance(a, dict) and "text" in a]
    return " ".join(out).lower()


def test_iteration9_scenario_only_and_fixed_titles():
    for name in MAIN_FIGURES:
        fig = getattr(F, name)()
        txt = _visible_text(fig)
        assert "scenario" not in txt and "survey" not in txt, (name, txt[:200])
        for m in fig.layout.updatemenus:
            for b in m.buttons:
                assert all("meta" not in a for a in b.args[1:] if isinstance(a, dict)), (name, b.label)
    assert "scenario" not in F.reversal_table_html().lower() and "survey" not in F.largest_differences_html().lower()
    p = A.pairs325()
    H = F.human_vs_qwen_scatter()
    q = np.concatenate([np.asarray(t.y, float) for t in H.data[:3]])
    assert np.allclose(np.sort(q), np.sort(p.scenario.to_numpy()))
    S2 = F.human_vs_qwen_scatter("survey_style")
    assert S2.layout.meta.endswith("survey-style prompts")
    F2 = F.correlation_matrices("survey_style", domains=False)
    assert [b.label for b in F2.layout.updatemenus[0].buttons] == ["People", "Qwen", "Qwen − People"] and len(F2.data) == 3
    F3 = F.heldout_r2("survey_style")
    assert not F3.layout.updatemenus and "+0.253" in F3.layout.annotations[0].text


def test_iteration9_format_agreement():
    d = A.format_agreement()
    assert len(d) == 26 and abs(d.r.median() - 0.941) < 0.005 and d.loc[d.r.idxmin(), "facet"] == "C2"
    pr, ps = A.format_pair_agreement()
    assert abs(pr - 0.872) < 0.005 and abs(ps - 0.831) < 0.005
    L = R.Ledger()
    checks.section3_formats(L)
    assert len(L.checks) >= 9 and all(c.status == "PASS" for c in L.checks)
    from phg import prose
    o = prose.get("s3.1", "body")
    assert o.startswith("Lu et al.'s method and ours both measure a trait by contrast") and "about 27 times fewer" in o  # iteration 54
    assert "Each facet was extracted twice" in o and "survey-style results are in Appendix F" in o
    assert "[[TABLE:stops]]" in prose.get("method.extraction", "body") and "[[TABLE:efficiency]]" in prose.get("method.extraction", "body")
    pr_ = prose.load()
    assert "is smaller; values are in the tables below." in prose.get("4.3", "how_to_read", pr_)
    summ = prose.get("summary", "body", pr_)  # iteration 50: Introduction; the .44 / 67% figures stay in the Figure 4.1 lead
    assert "pattern agreement r = .44, with the same direction in 67% of pairs" in prose.get("H", "lead", pr_) and "Qwen is our reference model" in summ


def test_iteration11_bestfit_and_models():
    from phg import prose
    ag = A.model_pair_agreement()
    assert np.allclose(ag.r, [0.868, 0.733, 0.840], atol=5e-4) and list(ag.same_sign) == [24354, 22352, 23748]  # iteration 27 order
    M = F.model_pairs_figure()
    assert M.layout.meta == "Trait correlations compared between models (r)"
    assert [b.label for b in M.layout.updatemenus[0].buttons] == ["Qwen–Gemma", "Qwen–Llama", "Llama–Gemma"]
    assert M.layout.xaxis.title.text == "Correlation between the two traits in Qwen (r)"
    assert M.layout.yaxis.title.text == "Correlation between the two traits in Gemma (r)"
    assert M.layout.annotations[0].text == "agreement r = .87 · Gemma links 0.98x as strong as Qwen"
    vis0 = [t for t in M.data if t.visible is not False]
    assert [t.name for t in vis0 if t.type == "heatmap"] == ["Trait pairs"] and len(vis0) == 4
    foc0 = [t for t in vis0 if getattr(t, "mode", None) == "markers+text"][0]
    gem = A.focal_hist_pairs()
    assert np.allclose(foc0.x, gem.qwen) and np.allclose(foc0.y, gem.gemma)
    assert sum(t.type == "heatmap" for t in M.data) == 3 and not any(t.type == "scatter" and len(t.x) > 10 for t in M.data)
    b1 = M.layout.updatemenus[0].buttons[1].args[1]
    assert b1["xaxis.title.text"] == "Correlation between the two traits in Qwen (r)"
    assert b1["yaxis.title.text"] == "Correlation between the two traits in Llama (r)" and "meta" not in b1
    focal = [t for t in M.data if getattr(t, "mode", None) == "markers+text"][0]
    assert list(focal.text) == ["Nurturing–Hostile", "Flirty–Hostile", "Avoidant–Hostile"]
    for name in ["human_vs_qwen_scatter", "factor_pattern_figure", "model_pairs_figure"]:
        names = {t.name for t in getattr(F, name)().data}
        assert {"Perfect agreement", "Trend"} <= names and "Best fit" not in names, name
    H = F.human_vs_qwen_scatter()
    bf = [t for t in H.data if t.name == "Trend"][0]
    p = A.pairs325()
    s = np.std(p.scenario) / np.std(p.human)
    assert abs(s - 2.00) < 0.02 and np.allclose(bf.y, p.scenario.mean() + s * (np.asarray(bf.x) - p.human.mean()), atol=1e-12)
    L = R.Ledger()
    checks.section2(L)
    checks.trend_checks(L)
    assert all(c.status == "PASS" for c in L.checks) and len(L.checks) >= 30
    o = prose.get("section.2", "lead")
    assert o.startswith("Before comparing the models with people") and o.endswith("differ between models (Appendix H).")  # iteration 49
    assert prose.get("G.1", "how_to_read").endswith("not the questionnaire facets, which were measured in Qwen only.")


def test_iteration14_appendix_g():
    from phg import prose
    L = R.Ledger()
    checks.appendix_g(L)
    assert len(L.checks) >= 50 and all(c.status == "PASS" for c in L.checks)
    d = A.persona_score_agreement()
    assert len(d) == 720 and sorted(d[d.r < 0].trait) == ["avoidant", "generalist"]
    cl = A.pc_plane_cca("llama")
    assert cl.min() > 0.9 and abs(A.pc_correspondence("llama")[0, 1] + 0.676) < 0.001
    for name in ["persona_agreement_figure", "pc_heatmap_figure", "pc1_scatter_figure", "factor_match_figure"]:
        fig = getattr(F, name)()
        assert isinstance(fig.layout.meta, str) and "?" not in fig.layout.meta, name
        assert fig.layout.legend.itemclick is False, name
        for m in fig.layout.updatemenus:
            assert all("meta" not in b.args[1] for b in m.buttons), name
    g3b = F.pc1_scatter_figure()
    assert [b.label for b in g3b.layout.updatemenus[0].buttons] == ["Qwen–Gemma", "Qwen–Llama"]
    assert g3b.data[0].visible is True and g3b.layout.yaxis.title.text == "Position on Gemma's PC1"
    ct = A.consensus_table()
    assert list(ct.component) == ["C1", "C2", "C3", "C4", "C5"]
    for k in ["G.4", "G.5", "G.6", "G.7"]:  # G.3 is a pointer to Figure 2.2; G.1 is Figure 2.1 since iteration 53 (no limitation box)
        assert prose.get(k, "lead") and prose.get(k, "limitation"), k
    for k in ["2.1", "2.2", "2.3"]:  # iteration 51: Section 2 limitation boxes folded into leads and captions
        assert prose.get(k, "lead") and not prose.get(k, "limitation") and "AA18" not in prose.get(k, "lead") + prose.get(k, "how_to_read"), k
    # Iteration 51: provenance wording moved out of reader captions; it stays in the source panels and table labels.
    assert "computed in this notebook" not in prose.get("2.2", "how_to_read") + prose.get("2.1", "how_to_read")
    assert "Do not infer common semantic factors from alignment alone." in prose.get("G.5", "lead")


def test_iteration15_appendix_f_table():
    d = A.format_results()
    assert abs(d.loc["scenario", "pattern_r"] - 0.444) < 0.0005 and abs(d.loc["survey_style", "pattern_r"] - 0.424) < 0.0005
    assert round(d.loc["scenario", "same_sign"], 2) == 0.67 and round(d.loc["survey_style", "same_sign"], 2) == 0.63
    assert abs(d.loc["scenario", "spread"] - 2.00) < 0.02 and abs(d.loc["survey_style", "spread"] - 2.130) < 0.0005
    assert (d.n_reversal == 13).all() and (d.n_close == 6).all()
    html = F.format_results_table_html()
    assert html.count("href='#wrap-H'") == 4 and html.count("href='#wrap-4.3'") == 3 and html.count("href='#wrap-4.2'") == 1
    assert len(A.pairs_by_format()) == 325 and len(A.survey_r2_table()) == 26
    from phg import inventory
    ids = {f.id for f in inventory.FIGURES} if hasattr(inventory, "FIGURES") else set()
    assert not ids or ({"F.3", "F.4"}.isdisjoint(ids) and "F.2" in ids)


def test_iteration16_figure_moves():
    h = F.pc_heatmap_figure()
    assert [b.label for b in h.layout.updatemenus[0].buttons] == ["Qwen–Gemma", "Qwen–Llama"]
    assert h.data[0].visible is True and h.data[1].visible is False
    assert h.layout.xaxis.title.text == "Gemma's activation axes" and h.layout.yaxis.title.text == "Qwen's activation axes"
    assert h.layout.updatemenus[0].buttons[1].args[1]["xaxis.title.text"] == "Llama's activation axes"
    assert abs(h.data[0].z[0][0] - 0.95) < 0.005 and abs(h.data[1].z[0][1] + 0.676) < 0.001
    from phg import inventory, prose
    ids = {f.id: f for f in inventory.FIGURES}
    assert "G.3" not in ids and ids["2.1"].sources == ("pca_xmodel", "persona_pcs") and "density" in ids["G.1"].title
    o = prose.get("section.2", "lead")
    assert "Appendix G.2)" in o and "(Figure 2.1)" in o and "Section 3 applies the same test" in o  # iteration 53


def test_iteration17_figure_22():
    from phg import inventory, prose
    ids = {f.id: f for f in inventory.FIGURES}
    assert "G.2" not in ids and ids["2.2"].status == "BUILT" and ids["2.9"].status == "SKELETON"
    assert "(Figure 2.3)" in prose.get("section.2", "lead") and prose.get("2.2", "lead").startswith("For each trait")
    assert prose.get("G.2", "lead") == ""


def test_iteration18_figure_23():
    f = F.consensus_pc_figure()
    assert [b.label for b in f.layout.updatemenus[0].buttons] == ["Qwen", "Gemma", "Llama"]
    assert [t.visible for t in f.data] == [True, False, False] and [y.split(" · ")[0] for y in f.data[0].y] == ["D1", "D2", "D3", "D4", "D5"]
    assert f.layout.xaxis.title.text == "Qwen's activation axes" and f.layout.legend.itemclick is False
    q = A.consensus_pc_corr("qwen")
    assert abs(abs(q[0, 0]) - 0.945) < 0.001 and abs(abs(q[1, 1]) - 0.977) < 0.001
    from phg import inventory, prose
    ids = {x.id: x for x in inventory.FIGURES}
    assert ids["2.3"].status == "BUILT" and ids["2.9"].status == "SKELETON"
    assert "(Figure 2.2)" in prose.get("section.2", "lead") and "Signs are arbitrary" in prose.get("2.3", "how_to_read")


def test_iteration19_consensus_key():
    k = A.consensus_key()
    assert list(k.component) == ["C1", "C2", "C3", "C4", "C5"]
    assert list(k.qwen_pc) == [1, 2, 3, 4, 5] and list(k.gemma_pc[:3]) == [1, 2, 3]
    assert k.high[0].startswith("mercurial") and k.low[2].startswith("blunt")
    h = F.consensus_key_html()
    assert h.count("<tr>") == 6 and "Charged expression vs factual moderation" in h and "kweak" in h
    f = F.consensus_pc_figure()
    assert list(f.data[0].y)[0] == "D1 · charged vs moderate"  # iteration 53: shown as D1-D5
    assert "forgiving care vs blunt prescription" in h.lower()  # iteration 49: the readings live in the key


def test_iteration20_factors_and_facets():
    f = F.factor_pc_figure()  # Appendix E.4 since iteration 21
    assert [b.label for b in f.layout.updatemenus[0].buttons] == ["Qwen", "Gemma", "Llama"]
    assert [len(t.y) for t in f.data] == [5, 6, 6] and f.data[0].visible is True and f.layout.legend.itemclick is False
    assert list(f.data[0].y)[0] == "F1 · calm vs edgy"
    g = F.facets_geometry_figure()
    assert [b.label for b in g.layout.updatemenus[0].buttons] == ["Shared directions D1–D5", "Qwen's activation axes PC1–PC5"]
    assert [t.visible for t in g.data] == [True, False] and len(g.data[0].y) == 26
    assert F.factor_key_html().count("<tr>") == 6 and "Closest Qwen factor" not in F.consensus_key_html()
    from phg import inventory, prose
    ids = {x.id: x for x in inventory.FIGURES}
    assert ids["E.4"].status == "BUILT" and ids["3.2"].status == "BUILT" and ids["3.6"].status == "SKELETON"
    assert "median 14%" in prose.get("3.2", "lead") and prose.get("E.4", "limitation")  # iteration 54: moved to E.5


def test_iteration21_axis_guide():
    f = F.pc_trait_map_figure()
    assert not f.layout.updatemenus and len(f.data) == 2 and f.layout.annotations[0].text == "r with PC1 +.95 · PC2 −.28 · PC3 −.03"  # iteration 37: default trait factual
    g = A.axis_guide()
    assert list(g.axis) == ["PC1", "PC2", "PC3", "PC4", "PC5"] and g.high[0][0] == "transparent" and g.low[0][0] == "narrative"
    assert g.high_chars[0] == ["auditor", "examiner"] and g.strongest[3] < 0.7 < g.strongest[2]
    h = F.axis_guide_html()
    assert h.count("<tr") == 10 and "PC4" not in h
    assert abs(A.pca_variance("qwen").loc[1] - 0.316) < 0.001
    from phg import prose
    assert "factual correlates +.95" in prose.get("1.1", "lead")  # iteration 37: illustrative PC1 traits


def test_iteration25_model_menus():
    d = F.pc_trait_map_payload()
    assert list(d["models"]) == ["qwen", "gemma", "llama"]
    for m, M in d["models"].items():
        r = A.trait_pc_corr(m)
        for ax in ["PC2", "PC3"]:
            o = [t for t, _ in M["opts"][ax]]
            hi, lo = A.PC1_ILLUSTRATIVE.get(m, (r["PC1"].idxmax(), r["PC1"].idxmin()))  # iteration 37
            assert o[:4] == [hi, lo, r[ax].idxmax(), r[ax].idxmin()] and len(o) == 5
            assert all(t in M["z"] for t in o) and M["opts"][ax][4][1].endswith(f"(PC1–{ax} diagonal)")
    assert d["models"]["qwen"]["opts"]["PC2"][4][0] == "conscientious"
    assert "pm-tr" in F.pc_trait_map_script() and len(F.pc_heatmap_figure().data[0].x) == 5
    assert F.consensus_pc_figure().data[0].z.shape[1] if hasattr(F.consensus_pc_figure().data[0].z, "shape") else len(F.consensus_pc_figure().data[0].z[0]) == 5



def test_iteration30_reversal_outlines():
    f = F.correlation_matrices()
    boxes = [sh for sh in f.layout.shapes if sh.name == "reversal"]
    assert len(boxes) == 26 and all(sh.type == "rect" for sh in boxes)
    p = A.pairs325()
    rev = p[p.group_frozen == "consistent_reversal"]
    oc = list(A.ordered_codes())
    cells = {(round(sh.x0 + 0.5), round(sh.y0 + 0.5)) for sh in boxes}
    assert cells == {c for a, b in zip(rev.left, rev.right) for c in [(oc.index(b), oc.index(a)), (oc.index(a), oc.index(b))]}
    dom = [b for b in f.layout.updatemenus[0].buttons if b.label.startswith("Domains")][0]
    assert not any((sh.get("name") == "reversal") for sh in dom.args[1]["shapes"])


def test_bigfive_trait_matrix_iteration31():
    """Figure 1.3: 42 strict-mapping traits in Figure 4.2 domain order, reverse-keyed traits flipped, domain scores
    reproducing the source study's saved intercorrelations, and the menu/phone behaviour of the figure."""
    from phg import analysis as A, figures as F, sources as S
    t = A.bf_traits()
    assert len(t) == 42 and list(dict.fromkeys(t.domain)) == A.DOMAIN_ORDER
    assert (t.sign < 0).sum() == 15 and all(l.endswith(" (−)") == (s < 0) for l, s in zip(t.label, t.sign))
    ic = S.csv("bf_domain_corr")
    ic = ic[ic.construction == "human_anchored_strict"]
    for r in ic.itertuples():
        assert abs(A.bf_block(r.model, A.BF_LETTER[r.domain_1], A.BF_LETTER[r.domain_2], "domain_r") - r.pearson_r) < 1e-6
    fig = F.bigfive_trait_matrix_figure()
    assert [b.label for b in fig.layout.updatemenus[0].buttons] == ["Qwen", "Gemma", "Llama", "Domains: Qwen",
                                                                   "Domains: Gemma", "Domains: Llama"]
    assert len(fig.data) == 6 and len(fig.data[0].y) == 42
    assert sum(s.name == "domain_block" for s in fig.layout.shapes) == 5
    assert "buttons[3]" in F.bigfive_phone_script()


def test_iteration33_restructure():
    """Reader-facing numbers follow the new section order; internal keys are unchanged."""
    from phg import report as R2, figures as F2
    assert [R2.fig_number(k) for k in ["1.3", "tmap", "1.2", "4.2", "H", "4.3", "6.1", "3.2", "5a", "1.1", "elbow", "G.1", "2.1", "2.2", "2.3"]] == \
        ["3.1", "1.2", "1.3", "4.2", "4.1", "E.6", "5.1", "E.5", "H.1", "1.1", "G.3a", "2.1", "2.2", "G.2", "2.3"]  # iteration 53
    assert "sapa1" not in R2.DISPLAY_NUMBER  # merged into Figure 3.1
    assert len(F2.bigfive_trait_matrix_figure(people=True, models=("qwen",)).layout.updatemenus[0].buttons) == 6  # iteration 34


def test_iteration37_pc1_illustrative():
    from phg import analysis as A3
    o = A3.pc_map_options("qwen", "PC2")
    assert [t for t, _ in o[:2]] == ["factual", "dramatic"]
    assert [t for t, _ in A3.pc_map_options("llama", "PC2")[:2]] == [A3.trait_pc_corr("llama").PC1.idxmax(), A3.trait_pc_corr("llama").PC1.idxmin()]


def test_iteration41_combined_bigfive():
    from phg import figures as F4
    f, v = F4.bigfive_combined_figure()
    assert len(f.data) == 12 and len(v) == 12 and not f.layout.updatemenus
    assert sum(v["qwen|domains|pc"]["visible"]) == 1 and f.data[9].z.shape == (5, 5)
    assert "bf-c" in F4.bigfive_combined_script("1.3", v)


def test_iteration42_consensus_traits():
    from phg import figures as F5
    f, v = F5.consensus_combined_figure()
    assert len(f.data) == 6 and set(v) == {f"{w}|{m}" for w in ["axes", "traits"] for m in ["qwen", "gemma", "llama"]}
    assert not f.layout.updatemenus
    d = F5.consensus_contrib("C1")  # iteration 43: 3 high + 3 low (flipped)
    assert len(d) == 6 and list(d.sign) == [1, 1, 1, -1, -1, -1] and d.label.iloc[3].endswith("(−)")
    assert (abs(f.data[3].z[:6, 0]) > 0.8).all()  # Qwen: all six C1 traits sit on PC1


def test_iteration46_bigfive_matrix():
    """Figure 3.1: one matrix, Rows / Columns / Show menus; split view puts the Rows source below the diagonal."""
    import numpy as np
    from phg import figures as F6, analysis as A6
    P = F6.bigfive_matrix_payload()
    assert set(P["T"]) == {"people", "qwen", "gemma", "llama"} and set(P["TP"]) == {"qwen", "gemma", "llama"}
    Z = F6.bm_split(np.array(P["D"]["qwen"], float), np.array(P["D"]["people"], float))
    assert round(Z[1, 0], 2) == 0.53 and round(Z[0, 1], 2) == -0.21 and np.isnan(Z[2, 2])
    f = F6.bigfive_matrix_figure()
    assert len(f.data) == 1 and f.layout.meta.startswith("Big Five traits and domains")
    s = F6.bigfive_matrix_script("1.3")
    assert all(k in s for k in ["bm-r", "bm-c", "bm-s", "Difference: traits", "Difference: domain scores", "window.BM"])


def test_iteration47_trait_map():
    """Figure 1.2: 240 traits per model inside the unit circle; labels follow the page script's rule."""
    import numpy as np
    from phg import figures as F7
    P = F7.trait_map_payload()
    for m in F7.TM_MODELS:
        x, y, z = (np.array(P["models"][m]["r"][c]) for c in ["PC1", "PC2", "PC3"])
        assert len(x) == 240 and (x ** 2 + y ** 2 + z ** 2).max() <= 1.0001
    f = F7.trait_map_figure()
    assert len(f.data) == 2 and len(f.data[0].x) == 240 and len(f.layout.shapes) == 2
    assert {"narrative", "transparent", "introverted", "experiential"} <= set(f.data[1].text)
    s = F7.trait_map_script("tmap")
    assert all(k in s for k in ["tm-m", "tm-y", "window.TM", "Vertical axis"])

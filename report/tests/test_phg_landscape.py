"""Persona Landscape Explorer: saved inputs, standardization, defaults, embedded payload."""
import numpy as np
import pytest

from phg import checks, explorer, landscape as LS, prose, report as R


def test_zscore_is_within_model_population_standardization():
    z = LS.zscore(LS.traits_raw("llama"))
    assert np.allclose(z.mean(axis=0), 0, atol=1e-12)
    assert np.allclose(z.std(axis=0, ddof=0), 1, atol=1e-12)


def test_default_pair_rule():
    a, b = LS.default_pair()
    assert (a, b) == ("poet", "auditor")
    pc1 = LS.pcs("qwen").pc1
    assert pc1[a] < pc1[b]


def test_axis_tags_only_where_saved():  # iteration 27: PC1-PC3 tagged for every model
    tags = LS.axis_tags()
    assert set(tags["qwen"]) == {1, 2, 3, 4, 5, 6}
    assert set(tags["llama"]) == {1, 2, 3} and set(tags["gemma"]) == {1, 2, 3}
    assert tags["qwen"][1].startswith("narrative, romantic, poetic ↔ transparent")
    assert all("↔" in t and "_" not in t for t in tags["qwen"].values())


def test_payload_shapes_and_rounding():
    p = LS.payload()
    assert len(p["personas"]) == 275 and len(p["traits"]) == 240 and p["scale"] == 10000
    for m in LS.MODELS:
        assert np.asarray(p["models"][m]["pcs"]).shape == (275, 6)
        assert np.asarray(p["models"][m]["z"]).shape == (275, 240)
        assert np.asarray(p["models"][m]["z"]).dtype.kind == "i" and "raw" not in p["models"][m]
    assert set(p["xmodel"]) == {"qwen-llama", "qwen-gemma"}


def test_section1_checks_pass_or_note():
    L = R.Ledger()
    checks.section1(L)
    assert not [c.id for c in L.checks if c.status == "FAIL"]
    assert [c.id for c in L.checks if c.status == "NOTE"] == ["1.pc.gemma"]


def test_explorer_html_is_offline_and_credited():
    h = explorer.explorer_html()
    assert "http://" not in h and "https://" not in h
    assert "Lu et al. (2026), The Assistant Axis" in h and "standardization and this display: PHG" in h
    assert "Each model has its own PCA." in h


def test_explorer_caption_seeded():
    assert prose.get("1.2", "lead").startswith("Figure 1.3 joins the two views") and prose.get("1.1", "how_to_read").startswith("To explore: use the menus")  # iteration 49


def test_explorer_bars_condensed_and_expanded():
    h = explorer.explorer_html()
    assert "PER_SIDE = 8" in h and "PX_PER_BAR = 22" in h
    assert "ple-list" not in h and "<table" not in h.split("<script>")[0].split("ple-scroll")[1][:200]
    assert "Show all 240" in h and "By name" in h

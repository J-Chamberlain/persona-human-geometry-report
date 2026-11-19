import numpy as np
import pandas as pd
import pytest

from phg import stats


@pytest.fixture
def xy():
    rng = np.random.default_rng(1)
    x = rng.normal(size=60)
    z = rng.normal(size=(60, 2))
    y = 0.5 * x + z @ np.array([0.7, -0.3]) + rng.normal(size=60)
    return x, y, z


def test_pearson_matches_numpy(xy):
    x, y, _ = xy
    assert stats.pearson(x, y) == pytest.approx(np.corrcoef(x, y)[0, 1], abs=1e-14)


def test_pearson_constant_is_nan():
    assert np.isnan(stats.pearson(np.ones(5), np.arange(5.0)))


def test_corr_matrix(xy):
    x, y, z = xy
    X = np.column_stack([x, y, z])
    assert np.allclose(stats.corr_matrix(X), np.corrcoef(X.T), atol=1e-14)


def test_leave_one_out_matches_brute_force(xy):
    x, y, _ = xy
    fast = stats.leave_one_out(x, y)
    slow = [np.corrcoef(np.delete(x, i), np.delete(y, i))[0, 1] for i in range(len(x))]
    assert np.allclose(fast, slow, atol=1e-12)


def test_partial_corr_single_control_formula(xy):
    x, y, z = xy
    c = z[:, 0]
    rxy, rxc, ryc = np.corrcoef(x, y)[0, 1], np.corrcoef(x, c)[0, 1], np.corrcoef(y, c)[0, 1]
    expected = (rxy - rxc * ryc) / np.sqrt((1 - rxc ** 2) * (1 - ryc ** 2))
    assert stats.partial_corr(x, y, c) == pytest.approx(expected, abs=1e-12)


def test_partial_corr_without_controls_is_pearson(xy):
    x, y, _ = xy
    assert stats.partial_corr(x, y, None) == pytest.approx(stats.pearson(x, y), abs=1e-14)


def test_variance_removed_is_r_squared(xy):
    x, _, z = xy
    Z = np.column_stack([np.ones(len(x)), z])
    beta = np.linalg.lstsq(Z, x, rcond=None)[0]
    r2 = 1 - ((x - Z @ beta) ** 2).sum() / ((x - x.mean()) ** 2).sum()
    assert stats.variance_removed(x, z) == pytest.approx(r2, abs=1e-12)


def test_group_exclusion(xy):
    x, y, _ = xy
    labels = np.array(["a"] * 20 + ["b"] * 40)
    g = stats.group_exclusion(x, y, labels).set_index("group")
    assert g.loc["a", "n"] == 40
    assert g.loc["a", "r"] == pytest.approx(np.corrcoef(x[20:], y[20:])[0, 1], abs=1e-12)


def test_screen_rules():
    h = np.array([-0.30, 0.30, 0.20, 0.40, -0.30])
    x = np.array([0.50, 0.35, -0.50, 0.30, 0.25])
    y = np.array([0.40, 0.20, -0.50, 0.60, 0.50])
    out = stats.screen(h, x, y)
    # 0 reversal; 1 close agreement; 2 human too small; 3 survey misses tolerance; 4 scenario below .30
    assert list(out) == ["consistent_reversal", "close_agreement", "other", "other", "other"]


def test_sse_quadratic_exact_recovery():
    rng = np.random.default_rng(3)
    y = rng.normal(size=200)
    p = 2.5 * (0.4 * y + rng.normal(size=200))
    m = 0.0
    sse = lambda k: ((y - (m + k * (p - m))) ** 2).sum()
    coef = stats.sse_quadratic([0, 1, 0.37], [sse(0), sse(1), sse(0.37)])
    sst = ((y - y.mean()) ** 2).sum()
    for k in [0.0, 0.2, 0.8, 1.3]:
        assert stats.r2_curve(coef, sst, np.array([k]))[0] == pytest.approx(1 - sse(k) / sst, abs=1e-10)


def test_bootstrap_reproducible(xy):
    x, y, _ = xy
    a = stats.bootstrap_corr(x, y, draws=50, seed=7)
    b = stats.bootstrap_corr(x, y, draws=50, seed=7)
    assert np.array_equal(a, b)


def test_calibration_table_predicts_held_out_condition():
    rng = np.random.default_rng(5)
    rows, mult = [], []
    for facet in ["F1", "F2"]:
        y = rng.normal(size=300)
        p = 3 * (0.3 * y + rng.normal(size=300))
        sst = ((y - y.mean()) ** 2).sum()
        sse = lambda k: ((y - k * p) ** 2).sum()
        kc, kf = 0.4, 0.33
        for cond, k in [("original", 1), ("reference_mean", 0), ("common_calibrated", kc), ("facet_calibrated_exploratory", kf),
                        ("human_reference", 1)]:
            rows.append(dict(source="s", condition=cond, facet=facet, S=0.5, SSE=sse(k), SST=sst, R2=1 - sse(k) / sst))
        mult.append(dict(source="s", facet=facet, common_primary=kc, facet_exploratory=kf))
    t = stats.calibration_table(pd.DataFrame(rows), pd.DataFrame(mult))
    assert np.allclose(t.R2_facet_saved, t.R2_facet_predicted, atol=1e-10)

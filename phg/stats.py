"""Small, dependency-light statistics used by the report.

All functions are pure: they take arrays and return arrays or plain values.
Conditioning here means linear partialling of measured controls. It is a
descriptive statistic, not a correction, and callers always show the
original value next to the conditioned one.
"""
from __future__ import annotations

from itertools import combinations
from typing import Iterable, Optional, Sequence

import numpy as np
import pandas as pd

# Frozen screen thresholds (outlier study, analysis_specification.md).
HUMAN_MIN = 0.25
MODEL_MIN = 0.30
AGREE_TOL = 0.15


def pearson(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    x = x - x.mean()
    y = y - y.mean()
    den = np.sqrt((x @ x) * (y @ y))
    return float("nan") if den <= 1e-12 else float((x @ y) / den)


def corr_matrix(X: np.ndarray) -> np.ndarray:
    X = np.asarray(X, float)
    Z = X - X.mean(0)
    sd = np.sqrt((Z * Z).sum(0))
    with np.errstate(invalid="ignore", divide="ignore"):
        R = (Z.T @ Z) / np.outer(sd, sd)
    R[~np.isfinite(R)] = np.nan
    return R


def residualize(y: np.ndarray, controls: Optional[np.ndarray]) -> np.ndarray:
    """Residual of y after OLS on an intercept plus controls."""
    y = np.asarray(y, float)
    if controls is None or np.size(controls) == 0:
        return y - y.mean()
    C = np.asarray(controls, float)
    if C.ndim == 1:
        C = C[:, None]
    Z = np.column_stack([np.ones(len(y)), C])
    beta, *_ = np.linalg.lstsq(Z, y, rcond=None)
    return y - Z @ beta


def partial_corr(x, y, controls=None) -> float:
    """Pearson correlation conditioned on controls (linear partialling)."""
    return pearson(residualize(x, controls), residualize(y, controls))


def variance_removed(y, controls) -> float:
    """Share of y's variance linearly explained by the controls (R^2)."""
    y = np.asarray(y, float)
    r = residualize(y, controls)
    c = y - y.mean()
    return float(1 - (r @ r) / (c @ c))


def leave_one_out(x, y) -> np.ndarray:
    """Exact correlation after deleting each observation in turn (O(n))."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    n = len(x)
    sx, sy = x.sum(), y.sum()
    sxx, syy, sxy = (x * x).sum(), (y * y).sum(), (x * y).sum()
    m = n - 1
    Sx, Sy = sx - x, sy - y
    Sxx, Syy, Sxy = sxx - x * x, syy - y * y, sxy - x * y
    cov = Sxy - Sx * Sy / m
    vx = Sxx - Sx * Sx / m
    vy = Syy - Sy * Sy / m
    return cov / np.sqrt(vx * vy)


def group_exclusion(x, y, labels: Sequence, controls=None) -> pd.DataFrame:
    """Correlation after excluding each group label in turn."""
    labels = np.asarray(labels)
    rows = []
    for g in sorted(set(labels.tolist())):
        keep = labels != g
        c = None if controls is None else np.asarray(controls)[keep]
        rows.append(dict(group=g, n=int(keep.sum()), r=partial_corr(np.asarray(x)[keep], np.asarray(y)[keep], c)))
    return pd.DataFrame(rows)


def screen(h, x, y, ht=HUMAN_MIN, qt=MODEL_MIN, tol=AGREE_TOL):
    """Frozen reversal/agreement screen applied to human h and two model formats."""
    h, x, y = (np.asarray(v, float) for v in (h, x, y))
    rev = (abs(h) >= ht) & (h * x < 0) & (h * y < 0) & (abs(x) >= qt) & (abs(y) >= qt)
    agree = (abs(h) >= ht) & (abs(x - h) <= tol) & (abs(y - h) <= tol)
    return np.where(rev, "consistent_reversal", np.where(agree, "close_agreement", "other"))


def pair_table(codes: Sequence[str], R: np.ndarray) -> pd.DataFrame:
    """Upper-triangle pairs (in the given facet order) with their correlation."""
    rows = [dict(left=codes[i], right=codes[j], r=R[i, j]) for i, j in combinations(range(len(codes)), 2)]
    return pd.DataFrame(rows)


def bootstrap_corr(x, y, draws=2000, seed=0, controls=None) -> np.ndarray:
    """Whole-persona bootstrap of a (partial) correlation. Independent stream."""
    rng = np.random.default_rng(seed)
    n = len(x)
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    C = None if controls is None else np.asarray(controls, float)
    out = np.empty(draws)
    for b in range(draws):
        ix = rng.integers(0, n, n)
        out[b] = partial_corr(x[ix], y[ix], None if C is None else C[ix])
    return out


# ------------------------------------------------------------ calibration
def sse_quadratic(ks: Iterable[float], sse: Iterable[float]) -> np.ndarray:
    """Fit SSE(k) = a - 2 b k + c k^2 through observed (k, SSE) points.

    Scaling predictions toward the reference mean by k makes squared error an
    exact quadratic in k, so three distinct points identify it and any extra
    point is a check. Returns (a, b, c).
    """
    ks = np.asarray(list(ks), float)
    sse = np.asarray(list(sse), float)
    A = np.column_stack([np.ones_like(ks), -2 * ks, ks ** 2])
    coef, *_ = np.linalg.lstsq(A, sse, rcond=None)
    return coef


def r2_curve(coef: np.ndarray, sst: float, ks: np.ndarray) -> np.ndarray:
    a, b, c = coef
    ks = np.asarray(ks, float)
    return 1 - (a - 2 * b * ks + c * ks ** 2) / sst


def calibration_table(test: pd.DataFrame, mult: pd.DataFrame) -> pd.DataFrame:
    """Per source/facet quadratic coefficients from saved Direct-12 conditions.

    Uses k=0 (reference_mean), k=1 (original), k=common multiplier to fit, and
    keeps k=facet multiplier as an out-of-fit check.
    """
    rows = []
    test = test[test.facet != "MACRO"]
    for (src, facet), g in test.groupby(["source", "facet"], sort=False):
        g = g.set_index("condition")
        m = mult[(mult.source == src) & (mult.facet == facet)].iloc[0]
        kc, kf = float(m.common_primary), float(m.facet_exploratory)
        coef = sse_quadratic([0.0, 1.0, kc], [g.loc["reference_mean", "SSE"], g.loc["original", "SSE"], g.loc["common_calibrated", "SSE"]])
        sst = float(g.loc["original", "SST"])
        pred_f = 1 - (coef[0] - 2 * coef[1] * kf + coef[2] * kf ** 2) / sst
        rows.append(dict(source=src, facet=facet, a=coef[0], b=coef[1], c=coef[2], SST=sst,
                         k_common=kc, k_facet=kf, S=float(g.loc["original", "S"]),
                         R2_original=float(g.loc["original", "R2"]),
                         R2_common=float(g.loc["common_calibrated", "R2"]),
                         R2_facet_saved=float(g.loc["facet_calibrated_exploratory", "R2"]),
                         R2_facet_predicted=pred_f,
                         R2_human=float(g.loc["human_reference", "R2"])))
    return pd.DataFrame(rows)


def ols(x, y) -> tuple[float, float]:
    """Least-squares line of y on x: (slope, intercept), from centred moments."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    xc = x - x.mean()
    slope = float((xc @ (y - y.mean())) / (xc @ xc))
    return slope, float(y.mean() - slope * x.mean())


def sma(x, y) -> tuple[float, float]:
    """Standardized major axis of y on x: slope = sign(r) * SD(y) / SD(x), through the two means. Symmetric in x and y
    (unlike least squares, it does not shrink toward zero when agreement is weak). Returns (slope, intercept)."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    slope = float(np.sign(pearson(x, y)) * y.std() / x.std())
    return slope, float(y.mean() - slope * x.mean())

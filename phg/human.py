"""Johnson IPIP-NEO-300 access: hash-checked download and aggregate-only scoring.

Licensing boundary: the OSF dataset has no explicit license. Nothing in this
module writes respondent rows, IDs, individual scores or profiles to disk.
Functions return aggregate statistics (correlation matrices, counts, hashes).

Scoring rules preserved from the frozen studies (AA27, Direct-30 B, outlier
diagnostics):
  * the downloaded responses are already reverse-keyed; they are never
    reversed again;
  * adults 18-80 with all 300 items answered (0 = missing);
  * exact response-pattern deduplication keeps the first occurrence;
  * seed 20260920 permutation; 60/20/20 pools truncated to
    30,000 reference / 10,000 calibration / 10,000 test;
  * facet score = mean of its ten items; reference-fitted empirical marginal
    transform to normal scores (midrank, clipped).
"""
from __future__ import annotations

import hashlib
import json
import shutil
import urllib.request
from pathlib import Path
from typing import Optional, Sequence

import numpy as np

from . import sources

RAW_DIR = sources.ROOT / "data_external" / "aa27_ipip_neo"
AA27_MANIFEST = "research/outputs/aa27_ipip_neo_profile_plausibility/source_manifest.json"
AA27_SPEC = "research/outputs/aa27_ipip_neo_profile_plausibility/ipip_facet_scoring_specification.csv"
RAW_NAME = "IPIP300.dat"
SEED = 20260920
SPLIT_SIZES = dict(reference=30000, calibration=10000, test=10000)
EXPECTED_COUNTS = dict(raw_rows=307313, complete_adults=117260, unique_adults=117259)


def aa27_sources() -> list[dict]:
    """Expected files and SHA-256 values from the frozen AA27 manifest."""
    data = json.loads(sources.evidence_bytes("65da790", AA27_MANIFEST))
    return [s for s in data["sources"] if "osf.io/download" in s["url"]]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_file(p: Path, expected: str) -> bool:
    return Path(p).exists() and sha256_file(p) == expected


def download(dest: Path = RAW_DIR, opener=urllib.request.urlopen, only: Optional[Sequence[str]] = None) -> list[dict]:
    """Download AA27 OSF files if absent, then verify every SHA-256.

    A file whose hash does not match is moved aside (``.mismatch``) and the
    function raises; it never silently accepts changed data.
    """
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    report = []
    for s in aa27_sources():
        if only and s["filename"] not in only:
            continue
        p = dest / s["filename"]
        if not p.exists():
            tmp = p.with_suffix(p.suffix + ".part")
            with opener(s["url"], timeout=120) as r, tmp.open("wb") as f:
                shutil.copyfileobj(r, f)
            tmp.rename(p)
        got = sha256_file(p)
        ok = got == s["sha256"]
        report.append(dict(filename=s["filename"], expected=s["sha256"], observed=got, ok=ok))
        if not ok:
            p.rename(p.with_suffix(p.suffix + ".mismatch"))
            raise ValueError(f"SHA-256 mismatch for {s['filename']}: {got}")
    return report


def raw_available(dest: Path = RAW_DIR) -> bool:
    exp = next(s for s in aa27_sources() if s["filename"] == RAW_NAME)["sha256"]
    return check_file(Path(dest) / RAW_NAME, exp)


def facet_items(codes: Sequence[str]) -> dict[str, np.ndarray]:
    import io
    import pandas as pd
    spec = pd.read_csv(io.BytesIO(sources.evidence_bytes("65da790", AA27_SPEC)))
    assert spec.downloaded_data_already_keyed.astype(str).str.lower().eq("true").all()
    return {c: spec[spec.facet_code == c].item_number.to_numpy(int) - 1 for c in codes}


def parse_lines(lines: list[bytes]) -> tuple[np.ndarray, np.ndarray]:
    """Fixed-width IPIP300.dat rows -> (items 0..5, age). 0 means missing."""
    X = np.array([np.frombuffer(r[33:333], np.uint8) - 48 for r in lines])
    age = np.array([int(r[7:9]) if r[7:9].strip() else -1 for r in lines])
    return X, age


def eligible_unique(X: np.ndarray, age: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    rows = np.flatnonzero((age >= 18) & (age <= 80) & (X != 0).all(1))
    _, first = np.unique(np.ascontiguousarray(X[rows]).view(np.dtype((np.void, X.shape[1]))).ravel(), return_index=True)
    return rows, rows[np.sort(first)]


def split(unique: np.ndarray, seed: int = SEED, sizes: dict = SPLIT_SIZES) -> dict[str, np.ndarray]:
    perm = np.random.default_rng(seed).permutation(unique)
    nr, nc = int(0.6 * len(perm)), int(0.2 * len(perm))
    return dict(reference=perm[:nr][: sizes["reference"]],
                calibration=perm[nr:nr + nc][: sizes["calibration"]],
                test=perm[nr + nc:][: sizes["test"]])


def facet_scores(X: np.ndarray, ix: np.ndarray, lookup: dict[str, np.ndarray], codes: Sequence[str]) -> np.ndarray:
    # Data are already keyed: plain item means, no reversal.
    return np.column_stack([X[ix[:, None], lookup[c][None, :]].astype(float).mean(1) for c in codes])


def reference_transform(A: np.ndarray, reference: np.ndarray) -> np.ndarray:
    from scipy.stats import norm
    Y = np.empty_like(A, dtype=float)
    for j in range(A.shape[1]):
        s = np.sort(reference[:, j])
        lo = np.searchsorted(s, A[:, j], side="left")
        hi = np.searchsorted(s, A[:, j], side="right")
        prob = np.clip((lo + hi) / (2 * len(s)), 0.5 / (len(s) + 1), 1 - 0.5 / (len(s) + 1))
        Y[:, j] = norm.ppf(prob)
    return Y


def reference_correlations(codes: Sequence[str], dest: Path = RAW_DIR) -> dict:
    """Recompute the frozen 30,000-reference human correlation matrix.

    Returns only aggregates: the 26x26 matrix, counts and split/transform
    hashes for comparison with POINT_ESTIMATE_STAGE.json.
    """
    from .stats import corr_matrix
    lines = (Path(dest) / RAW_NAME).read_bytes().splitlines()
    X, age = parse_lines(lines)
    n_raw = len(lines)
    del lines
    rows, unique = eligible_unique(X, age)
    sp = split(unique)
    lookup = facet_items(codes)
    ref = facet_scores(X, sp["reference"], lookup, codes)
    Y = reference_transform(ref, ref)
    R = corr_matrix(Y)
    out = dict(
        codes=list(codes), R=R, raw_rows=n_raw, complete_adults=len(rows), unique_adults=len(unique),
        partition_sha256={k: hashlib.sha256(v.tobytes()).hexdigest() for k, v in sp.items()},
        reference_transformed_sha256=hashlib.sha256(Y.tobytes()).hexdigest(),
    )
    del X, ref, Y
    return out

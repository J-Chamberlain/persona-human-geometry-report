"""Human-data code on synthetic fixtures only (no respondent data, no network)."""
import hashlib
import io
from pathlib import Path

import numpy as np
import pytest

from phg import human


def line(age, items):
    head = f"{0:07d}{age:2d}".ljust(33).encode()
    return head + bytes(48 + int(v) for v in items)


def test_parse_lines_layout():
    items = np.arange(300) % 6
    X, age = human.parse_lines([line(30, items), line(5, items)])
    assert X.shape == (2, 300) and list(age) == [30, 5]
    assert np.array_equal(X[0], items)


def test_eligible_unique_drops_minors_missing_and_duplicates():
    rng = np.random.default_rng(0)
    a = rng.integers(1, 6, 300)
    b = rng.integers(1, 6, 300)
    miss = a.copy(); miss[10] = 0
    lines = [line(30, a), line(40, a), line(12, b), line(85, b), line(25, miss), line(50, b)]
    X, age = human.parse_lines(lines)
    rows, unique = human.eligible_unique(X, age)
    assert list(rows) == [0, 1, 5]          # 12 and 85 out of range, row 4 has a missing item
    assert list(unique) == [0, 5]           # exact duplicate of row 0 removed, first kept


def test_split_is_seeded_and_disjoint():
    ids = np.arange(1000)
    s1 = human.split(ids, sizes=dict(reference=500, calibration=100, test=100))
    s2 = human.split(ids, sizes=dict(reference=500, calibration=100, test=100))
    for k in s1:
        assert np.array_equal(s1[k], s2[k])
    allv = np.concatenate(list(s1.values()))
    assert len(allv) == len(set(allv)) == 700
    assert len(s1["reference"]) == 500  # 60% pool = 600, truncated to 500


def test_facet_scores_do_not_rekey():
    X = np.array([[1, 5, 2, 4], [5, 1, 4, 2]])
    lookup = {"F": np.array([0, 1]), "G": np.array([2, 3])}
    S = human.facet_scores(X, np.array([0, 1]), lookup, ["F", "G"])
    assert np.array_equal(S, [[3.0, 3.0], [3.0, 3.0]])  # plain means; a reversal would change these


def test_reference_transform_monotone_and_centred():
    rng = np.random.default_rng(1)
    ref = rng.normal(size=(2000, 1))
    Y = human.reference_transform(ref, ref)
    order = np.argsort(ref[:, 0])
    assert np.all(np.diff(Y[order, 0]) >= 0)
    assert abs(Y.mean()) < 0.01


def test_download_verifies_hash(tmp_path, monkeypatch):
    good = b"fixture-bytes"
    sha = hashlib.sha256(good).hexdigest()
    monkeypatch.setattr(human, "aa27_sources", lambda: [dict(url="u", filename="IPIP300.dat", sha256=sha)])
    opener = lambda url, timeout: io.BytesIO(good)
    rep = human.download(tmp_path, opener=opener)
    assert rep[0]["ok"] and (tmp_path / "IPIP300.dat").read_bytes() == good


def test_download_rejects_changed_file(tmp_path, monkeypatch):
    monkeypatch.setattr(human, "aa27_sources", lambda: [dict(url="u", filename="IPIP300.dat", sha256="0" * 64)])
    with pytest.raises(ValueError):
        human.download(tmp_path, opener=lambda url, timeout: io.BytesIO(b"changed"))
    assert not (tmp_path / "IPIP300.dat").exists()
    assert (tmp_path / "IPIP300.dat.mismatch").exists()


def test_aa27_manifest_hash_is_pinned():
    srcs = {s["filename"]: s["sha256"] for s in human.aa27_sources()}
    assert srcs["IPIP300.dat"] == "1bbb7189f5f0f2883bb4493f956cf639178c5c8ee95319fd3881f6d9d2f189a3"

#!/usr/bin/env python3
"""Download the Johnson IPIP-NEO-300 files from OSF and verify AA27 SHA-256 hashes.

Files go to data_external/aa27_ipip_neo/ (git-ignored). The dataset has no
explicit license: never commit or export respondent rows, IDs or profiles.
The responses are already reverse-keyed; nothing here re-keys them.

Usage: python research/notebooks/download_ipip.py [--only IPIP300.dat]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from phg import human  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", help="limit to these filenames")
    ap.add_argument("--dest", default=str(human.RAW_DIR))
    a = ap.parse_args()
    try:
        rows = human.download(Path(a.dest), only=a.only)
    except OSError as e:  # includes urllib URLError
        sys.exit(f"Download failed ({e}). Check network access to osf.io; nothing was accepted.")
    for r in rows:
        print(f"{r['filename']}: {'OK' if r['ok'] else 'MISMATCH'} {r['observed']}")

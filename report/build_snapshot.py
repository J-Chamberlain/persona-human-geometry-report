"""Rebuild saved snapshots solely from packaged evidence; never accesses research Git."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from phg import sources  # noqa: E402

if __name__ == "__main__":
    m = sources.build_snapshot()
    bad = [r for r in sources.verify_against_evidence() if r["ok"] is not True]
    print(f"{len(m['files'])} files written; re-derivation failures: {bad or 'none'}")

#!/usr/bin/env python3
"""Write INVENTORY.md and INVENTORY.csv from the figure registry in phg/inventory.py."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from phg import inventory  # noqa: E402

if __name__ == "__main__":
    df = inventory.write(HERE)
    print(f"{df.figure.nunique()} figures, {len(df)} figure-source rows")

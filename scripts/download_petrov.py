"""Opt-in local retrieval of published aggregates; redistribution permission unresolved.

This script does not grant redistribution rights. Keep the resulting table out of Git.
"""
from pathlib import Path
import argparse,hashlib,urllib.request
URL='https://raw.githubusercontent.com/nikbpetrov/LLMs-Simulate-Humans/85c3c2f78d5371cf16b71b8b94006d379b4c24fd/data/data_for_R/intercorrs.csv'
SHA256='aa55c342bd2ee55ba111927e3f31a71ec8f702a692da4b5ec4cb46db97224e0c'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--dest',type=Path,default=Path(__file__).resolve().parents[1]/'data/saved/external/petrov2024_intercorrs.csv');a=ap.parse_args()
    if a.dest.exists():b=a.dest.read_bytes()
    else:
        with urllib.request.urlopen(URL,timeout=60) as r:b=r.read()
    if hashlib.sha256(b).hexdigest()!=SHA256:raise ValueError('Changed Petrov input rejected; no file written')
    a.dest.parent.mkdir(parents=True,exist_ok=True)
    if not a.dest.exists():a.dest.write_bytes(b)
    print('Pinned published aggregate verified locally. No redistribution licence established; do not commit this file.')
if __name__=='__main__':main()

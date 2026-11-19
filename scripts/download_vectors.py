"""Opt-in pinned Lu et al. tensor downloads; no weights, inference or extraction."""
from pathlib import Path
import argparse,hashlib,json,urllib.request,shutil
ROOT=Path(__file__).resolve().parents[1]

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--model',choices=['qwen-3-32b','llama-3.3-70b','gemma-2-27b'],required=True);ap.add_argument('--kind',choices=['role_vectors','trait_vectors','both'],default='both');ap.add_argument('--dest',type=Path,default=ROOT/'data_external/lu_vectors');a=ap.parse_args()
    m=json.loads((ROOT/'data/downloads/lu_vectors.json').read_text());selected=[r for r in m['files'] if r['path'].startswith(a.model+'/') and (a.kind=='both' or '/'+a.kind+'/' in r['path'])]
    for r in selected:
        p=a.dest/r['path'];p.parent.mkdir(parents=True,exist_ok=True)
        if not p.exists():
            tmp=p.with_suffix(p.suffix+'.part');url=f"https://huggingface.co/datasets/{m['repository']}/resolve/{m['revision']}/{r['path']}"
            with urllib.request.urlopen(url,timeout=120) as src,tmp.open('wb') as dst:shutil.copyfileobj(src,dst)
            if tmp.stat().st_size!=r['bytes'] or digest(tmp)!=r['sha256']:raise ValueError(f'Changed upstream file rejected: {r["path"]}')
            tmp.rename(p)
        if p.stat().st_size!=r['bytes'] or digest(p)!=r['sha256']:raise ValueError(f'Local hash mismatch: {r["path"]}')
    print(f'{len(selected)} pinned tensor files verified; no model execution')
if __name__=='__main__':main()

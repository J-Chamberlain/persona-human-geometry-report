"""Optional CPU recomputation from downloaded public tensor banks, not run for packaging.

This is a measurement recipe, not a claim of independently reproduced original extraction.
Requires optional torch. Never downloads weights or invokes a model.
"""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--model',choices=['qwen-3-32b','gemma-2-27b','llama-3.3-70b'],required=True);ap.add_argument('--vectors',type=Path,default=ROOT/'data_external/lu_vectors');ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    if a.output.exists():raise FileExistsError('Use a fresh output directory')
    import torch
    m=json.loads((ROOT/'data/downloads/lu_vectors.json').read_text());rows=[r for r in m['files'] if r['path'].startswith(a.model+'/')]
    def load(kind):
        names=[];vectors=[]
        for r in rows:
            if '/'+kind+'/' not in r['path']:continue
            p=a.vectors/r['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
            x=torch.load(p,map_location='cpu',weights_only=True).float()
            if x.ndim!=2:raise ValueError('Expected released layer-by-coordinate tensor')
            names.append(p.stem);vectors.append(x.mean(0).numpy().astype(np.float64))
        return names,np.stack(vectors)
    roles,r=load('role_vectors');traits,t=load('trait_vectors')
    scores=(r/np.linalg.norm(r,axis=1)[:,None])@(t/np.linalg.norm(t,axis=1)[:,None]).T
    a.output.mkdir(parents=True)
    import csv
    with (a.output/'historical_trait_cosines.csv').open('w',newline='') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(['persona']+traits);w.writerows([[name]+list(v) for name,v in zip(roles,scores)])
    (a.output/'RECIPE.json').write_text(json.dumps(dict(status='Optional measurement recipe executed by caller; not a package validation result',model=a.model,source_revision=m['revision'],preprocessing='float32 all-layer means, float64 Euclidean cosine; no persona centering for trait scores'),indent=2)+'\n')
if __name__=='__main__':main()

"""Frozen scientific function excerpt; excludes launch, budget and coordination logic.
Original source SHA/commit and excerpt rule are in MANIFEST.csv.
"""
import hashlib,json
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parents[1]

def read(p):return json.loads(Path(p).read_text())

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def cfg():return read(P/'design/frozen_config.json')

def extract_text(q):return q.get('question',q.get('text',q.get('statement')))

def portrait_text(p,pole):
 x=p.get(pole,p.get('portraits',{}).get(pole));assert x is not None
 if isinstance(x,dict):x=x.get('text',x.get('paragraphs',x.get('portrait')))
 return '\n\n'.join(x) if isinstance(x,list) else x

def rows(facet,source):
 assert facet in cfg()['priority'] and source in cfg()['source_order'];d=P.parents[1]/'facets'/facet
 bank=read(d/('extraction_scenarios.json' if source=='scenario' else 'extraction_statements.json'));bank=bank.get('questions',bank.get('items')) if isinstance(bank,dict) else bank;assert len(bank)==64
 index={q['id']:q for q in bank};order=read(P/'design/sampling_schedule.json')['order'][facet][source];assert len(order)==len(bank) and set(order)==set(index);bank=[index[k] for k in order]
 prompts=read(P/'design/common_prompts.json');portraits=read(d/'portraits.json');out=[]
 for position,q in enumerate(bank,1):
  text=extract_text(q);assert isinstance(text,str) and text.strip()
  for pole in ['high','low']:
   system=portrait_text(portraits,pole)+'\n\n'+prompts['common_wrapper']+'\n'+prompts['response_instructions'][source]
   out.append(dict(id=q['id']+'-'+pole,facet=facet,question_id=q['id'],position=position,source=source,pole=pole,theme=q['theme'],criterion=q['criterion'],system=system,user=text,messages=[dict(role='system',content=system),dict(role='user',content=text)],fresh_conversation=True,generation=cfg()['max_new_tokens']))
 return out

def finish_reason(tokens,eos_ids,cap):
 eos_ids=[eos_ids] if isinstance(eos_ids,int) else list(eos_ids);assert tokens and eos_ids and len(tokens)<=cap
 return 'eos' if tokens[-1] in eos_ids else 'max_new_tokens' if len(tokens)==cap else 'other'

def stability(x,previous=None):
 c=cfg();x=np.asarray(x,dtype=np.float32);n=len(x);assert n in c['checkpoints'] and x.ndim==2 and np.isfinite(x).all()
 m=x.mean(0,dtype=np.float32);rng=np.random.default_rng(c['bootstrap_seed']);ids=rng.integers(n,size=(c['bootstrap_replicates'],n));weights=np.stack([np.bincount(z,minlength=n) for z in ids]).astype(np.float32);boot=weights@x/n;assert np.isfinite(boot).all();den=np.linalg.norm(boot,axis=1)*np.linalg.norm(m);cos=np.divide(boot@m,den,out=np.full(len(boot),-1.,np.float32),where=den>0);assert np.isfinite(cos).all();p05=float(np.quantile(np.clip(cos,-1,1),.05));seq=None
 if previous is not None:
  denp=np.linalg.norm(m)*np.linalg.norm(previous);seq=float(np.clip(m@previous/denp,-1,1)) if denp>0 else -1.
 return dict(n=n,bootstrap_p05=p05,successive_cosine=seq,pass_gate=bool(n>=16 and p05>=.95 and seq is not None and seq>=.98 and np.linalg.norm(m)>0))

def stop(contrasts,exhausted=False):
 a=np.asarray(contrasts,dtype=np.float32);assert len(a)==0 or a.ndim==3 and a.shape[1:]==(64,5120) and np.isfinite(a).all();hist=[];prev=None;prevall=None
 for n in cfg()['checkpoints']:
  if n>len(a):break
  z=stability(a[:n,48],prev);z['all_layer_diagnostic']=stability(a[:n].mean(1,dtype=np.float32),prevall);hist.append(z);prev=a[:n,48].mean(0,dtype=np.float32);prevall=a[:n].mean(1,dtype=np.float32).mean(0,dtype=np.float32)
  if z['pass_gate']:return dict(status='CONVERGED_BLOCK48',formal_accepted=n,history=hist,accepted_extras=len(a)-n)
 return dict(status='BANK_EXHAUSTED_UNCONVERGED' if exhausted else 'CONTINUE',formal_accepted=None,accepted=len(a),history=hist)

def facet_status(scenario,survey):
 a=[scenario['status'],survey['status']];return 'FULLY_CONVERGED' if a==['CONVERGED_BLOCK48']*2 else 'PARTIAL' if 'CONVERGED_BLOCK48' in a else 'UNCONVERGED'

def analysis_eligible(status):return sum(v=='FULLY_CONVERGED' for v in status.values())>=cfg()['cpu_followup_min_fully_converged_facets']

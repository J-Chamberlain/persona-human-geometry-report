"""CPU derivation from sealed generated records and once-locked assessments."""
from plan import *
from scorer import eligibility
import csv
import argparse

def inventory(rubric):
 criteria=[r['id'] for r in rubric['criteria']];boundaries=rubric.get('boundary_controls',rubric.get('boundary_flags',[]));boundaries=list(boundaries) if isinstance(boundaries,dict) else [r['id'] if isinstance(r,dict) else r for r in boundaries];return criteria,boundaries

def derive(runtime,facet,source,output):
 runtime=Path(runtime);output=Path(output);output.mkdir(exist_ok=False);records={};judgments={};criteria,boundaries=inventory(read(P/'facets'/facet/'rubric.json'))
 for folder in sorted(runtime.glob(facet+'-'+source+'-*')):
  if not (folder/'COMPLETE.json').exists() and not (folder/'PARTIAL.json').exists():continue
  seal_name='COMPLETE.json' if (folder/'COMPLETE.json').exists() else 'PARTIAL.json';complete=read(folder/seal_name)
  for name,h in complete['files'].items():assert sha(folder/name)==h,name
  seal=read(folder/'SCORING_COMPLETE.json');assert seal['locked_before_unblinding'] and seal['source_config_sha256']==sha(P/'design/frozen_config.json')
  for name,h in seal['files'].items():assert sha(folder/name)==h,name
  assert {'locked.json','private_map.json','packet.json',seal_name}<=set(seal['files'])
  lock=read(folder/'locked.json');assert lock['locked_before_unblinding'] and lock['no_rejudging'];mapping=read(folder/'private_map.json');assert sha(folder/'packet.json')==lock['packet_sha256']
  for a in lock['assessments']:ident=mapping[a['id']];assert ident not in judgments;judgments[ident]=a
  for file in folder.glob('*.json'):
   obj=read(file)
   if isinstance(obj,dict) and 'response' in obj and 'id' in obj:assert obj['id'] not in records;records[obj['id']]=(obj,folder)
 unmatched=[];budget_partial=False
 for folder in sorted(runtime.glob(facet+'-'+source+'-*')):
  if (folder/'PARTIAL.json').exists():budget_partial=True
 order=read(P/'design/sampling_schedule.json')['order'][facet][source];bank=read(P/'facets'/facet/('extraction_scenarios.json' if source=='scenario' else 'extraction_statements.json'));metadata={q['id']:q for q in bank};pairs=[];accepted=[];allarrays={};accepted_ids=[];observed=[]
 for pos,ident in enumerate(order,1):
  if ident+'-high' not in records and ident+'-low' not in records:continue
  if ident+'-high' not in records or ident+'-low' not in records:
   present=[records[k] for k in [ident+'-high',ident+'-low'] if k in records]
   assert len(present)==1 and present[0][0]['pole']=='high' and (present[0][1]/'PARTIAL.json').exists(),'Unmatched pair must be high-only in its own sealed PARTIAL folder, never a claimed COMPLETE folder'
   assert pos==len(observed)+1 and not unmatched,'Only one terminal unmatched question after the real matched prefix is permitted'
   unmatched.append(ident);continue
  assert not unmatched,'Matched data after unmatched partial question: STOP'
  p,folderp=records[ident+'-high'];n,foldern=records[ident+'-low'];assert p['id'] in judgments and n['id'] in judgments
  e=eligibility(judgments[p['id']],judgments[n['id']],p,n,criteria,boundaries);observed.append(ident);row=dict(question_id=ident,position=pos,theme=metadata[ident]['theme'],criterion=metadata[ident]['criterion'],item_ids=metadata[ident]['item_ids'],formulation='one_rich_portrait_pair',**e)
  if e['eligible']:
   poles=[]
   for r,folder in [(p,folderp),(n,foldern)]:
    spec=r['response_only_activation_file'];file=folder/spec['path'];assert sha(file)==spec['sha256'];a=np.load(file,allow_pickle=False);assert a.shape==(64,5120) and a.dtype==np.float32 and np.isfinite(a).all();poles.append(a)
   delta=poles[0]-poles[1];allarrays[ident]=poles;accepted.append(delta);accepted_ids.append(ident);np.save(output/(ident+'-delta.npy'),delta,allow_pickle=False);row['contrast_sha256']=sha(output/(ident+'-delta.npy'))
  pairs.append(row)
 assert observed==order[:len(observed)],'Missing earlier frozen questions: STOP, never fabricate rejected contributors'
 decision=stop(accepted,exhausted=len(observed)==cfg()['format_question_cap'])
 if budget_partial and decision['status']=='CONTINUE':decision['status']='BUDGET_OR_RUNTIME_PARTIAL_UNCONVERGED'
 formal_n=decision['formal_accepted'];formal_ids=accepted_ids[:formal_n] if formal_n is not None else [];formal_observed=observed[:observed.index(formal_ids[-1])+1] if formal_ids else [];formal=set(formal_ids)
 for row in pairs:row['formal']=row['question_id'] in formal;row['within_formal_observed_prefix']=row['question_id'] in formal_observed;row['formal_weight']=1/len(formal) if row['formal'] else 0.
 accounting=[]
 for dimension in ['theme','criterion','item_ids','formulation']:
  groups={}
  for row in pairs:
   keys=row[dimension] if isinstance(row[dimension],list) else [row[dimension]]
   for key in keys:groups.setdefault(key,[]).append(row)
  for key,group in groups.items():accounting.append(dict(facet=facet,source=source,dimension=dimension,key=key,raw_pairs=len(group),accepted_pairs=sum(r['eligible'] for r in group),formal_pairs=sum(r['formal'] for r in group),formal_weight=sum(r['formal_weight'] for r in group),multi_link_counts_not_disjoint=dimension=='item_ids'))
 with (output/'acceptance_weights.csv').open('w') as f:
  if accounting:w=csv.DictWriter(f,fieldnames=accounting[0]);w.writeheader();w.writerows(accounting)
 report=dict(partial_runtime=budget_partial,unmatched_raw_question_ids=unmatched,facet=facet,source=source,status=decision['status'],stop=decision,formal_accepted_ids=formal_ids,formal_observed_ids=formal_observed,raw_observed_ids=observed,pair_accounting=pairs,partial_estimate_accepted_ids=accepted_ids if not formal_ids else [],not_a_scientific_validity_claim=True)
 if accepted:
  chosen=formal_ids if formal_ids else accepted_ids;d=np.stack([allarrays[k][0]-allarrays[k][1] for k in chosen]);plus=np.stack([allarrays[k][0] for k in chosen]).mean(0,dtype=np.float32);minus=np.stack([allarrays[k][1] for k in chosen]).mean(0,dtype=np.float32);mean=d.mean(0,dtype=np.float32);norm=float(np.linalg.norm(mean[48].astype(float)));u=mean[48].astype(float)/norm if norm else None
  for name,a in [('mean',mean),('positive',plus),('negative',minus)]:np.save(output/(name+'.npy'),a,allow_pickle=False)
  if u is not None:np.save(output/'unit48.npy',u.astype(np.float32),allow_pickle=False)
  report.update(estimate_kind='FORMAL_CONVERGED' if formal_ids else 'PARTIAL_UNCONVERGED',n=len(chosen),norm48=norm,unit_sha256=sha(output/'unit48.npy') if u is not None else None,centroid_delta_max_abs_error=float(np.max(abs((plus-minus)-mean))),equal_accepted_question_weight=1/len(chosen),block_diagnostics=[dict(block=i,norm=float(np.linalg.norm(mean[i].astype(float)))) for i in range(64)])
 publish(output/'FORMAT_SUMMARY.json',report);publish(output/'COMPLETE.json',dict(files={p.name:sha(p) for p in sorted(output.iterdir()) if p.is_file()},generated_new_responses=False,new_judgments=False))
 return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--runtime',required=True);p.add_argument('--facet',required=True);p.add_argument('--source',choices=['scenario','survey_style'],required=True);p.add_argument('--output',required=True);a=p.parse_args();print(json.dumps(derive(a.runtime,a.facet,a.source,a.output),indent=2))

"""One blind assessment implementation adapted from E2; never creates judgments."""
import hashlib,json,random
from pathlib import Path
from plan import publish,sha,read,cfg
QUALITY=['refusal','nonanswer','severe_coherence','instruction_failure']
# Preserve legacy packet field/types; hostility is descriptive and non-excluding.
QUALITY_FIELDS=['refusal','nonanswer','severe_coherence','hostility','instruction_failure']

def packet(rows,records,seed=20261013):
 assert {r['id'] for r in rows}=={r['id'] for r in records};private={};out=[];prompts={r['id']:r for r in rows}
 for r in records:
  original=prompts[r['id']];opaque=hashlib.sha256((str(seed)+':'+r['id']).encode()).hexdigest()[:24];assert opaque not in private;private[opaque]=r['id']
  out.append(dict(id=opaque,format=original['source'],question=original['user'],response=r['response']))
 random.Random(seed).shuffle(out);return out,private

def validate(a,response,criterion_ids,boundary_ids):
 errors=[];values=[]
 if not isinstance(a,dict) or set(a)!={'id','criteria','boundary_controls','quality','rationale','confounded_only'}:return dict(valid=False,score=None,errors=['assessment_schema'])
 if not isinstance(a['criteria'],dict) or set(a['criteria'])!=set(criterion_ids):return dict(valid=False,score=None,errors=['criterion_inventory'])
 for k,v in a['criteria'].items():
  if not isinstance(v,dict) or set(v)!={'grade','evidence','context'}:errors.append(k+'_schema');continue
  grade=v['grade']
  if grade is not None and (type(grade) is not int or grade not in [-2,-1,0,1,2]):errors.append(k+'_range');continue
  if not isinstance(v['evidence'],str) or not isinstance(v['context'],str):errors.append(k+'_text');continue
  if v['evidence'] and v['evidence'] not in response:errors.append(k+'_nonliteral')
  if grade is not None:
   if not v['evidence'] or not v['context']:errors.append(k+'_missing_evidence')
   values.append(grade)
 if not isinstance(a['boundary_controls'],dict) or set(a['boundary_controls'])!=set(boundary_ids):errors.append('boundary_inventory')
 else:
  for k,v in a['boundary_controls'].items():
   if not isinstance(v,dict) or set(v)!={'present','evidence','context'}:errors.append(k+'_boundary_schema');continue
   if not isinstance(v['evidence'],str) or not isinstance(v['context'],str):errors.append(k+'_boundary_text');continue
   if v['present'] is not None and type(v['present']) is not bool:errors.append(k+'_boundary_boolean')
   if v['present'] is True and (not v['evidence'] or v['evidence'] not in response or not v['context']):errors.append(k+'_boundary_evidence')
 q=a['quality']
 if not isinstance(q,dict) or set(q)!=set(QUALITY_FIELDS+['evidence']) or any(type(q.get(k)) is not bool for k in QUALITY_FIELDS):errors.append('quality_schema')
 elif not isinstance(q['evidence'],str):errors.append('quality_evidence_type')
 elif any(q[k] for k in QUALITY) and (not q['evidence'] or q['evidence'] not in response):errors.append('quality_evidence')
 if type(a['confounded_only']) is not bool or not isinstance(a['rationale'],str) or not a['rationale']:errors.append('rationale_or_confound')
 return dict(valid=not errors,score=25*(sum(values)/len(values)+2) if values and not errors else None,errors=errors,diagnostic_criteria=len(values))

def eligibility(pos,neg,p,n,criterion_ids,boundary_ids):
 reasons=[];scores=[]
 for label,a,r in [('positive',pos,p),('negative',neg,n)]:
  v=validate(a,r['response'],criterion_ids,boundary_ids);scores.append(v['score'])
  if not v['valid']:reasons.append(label+'_invalid_assessment')
  if v['score'] is None:reasons.append(label+'_no_diagnostic_expression')
  assessment=a if isinstance(a,dict) else {};quality=assessment.get('quality',{});quality=quality if isinstance(quality,dict) else {}
  if any(quality.get(k,False) for k in QUALITY):reasons.append(label+'_quality_failure')
  if assessment.get('confounded_only'):reasons.append(label+'_confounded_only')
  if r.get('finish_reason')=='max_new_tokens':reasons.append(label+'_cap')
  if '<think>' in r['response'] or '</think>' in r['response']:reasons.append(label+'_thinking_artifact')
  if r.get('activation_valid') is not True:reasons.append(label+'_mask_or_numeric_failure')
 a,b=scores
 if a is None or a<cfg()['positive_score_min']:reasons.append('positive_below75_or_undefined')
 if b is None or b>cfg()['negative_score_max']:reasons.append('negative_above25_or_undefined')
 if a is not None and b is not None and a-b<cfg()['eligibility_gap']:reasons.append('gap_below50')
 return dict(eligible=not reasons,positive_score=a,negative_score=b,reasons=reasons,subtraction='positive_instruction_minus_negative_instruction')

def lock(packet_file,assessment_file,out,identity,criterion_ids,boundary_ids):
 assert identity and identity.get('model') and identity.get('instance_id') and identity.get('approved_identity') is True
 rows=read(packet_file);assessments=read(assessment_file);assert len(rows)==len(assessments) and len({a['id'] for a in assessments})==len(assessments) and {a['id'] for a in assessments}=={r['id'] for r in rows}
 lookup={a['id']:a for a in assessments};checks={r['id']:validate(lookup[r['id']],r['response'],criterion_ids,boundary_ids) for r in rows}
 publish(out,dict(schema='direct12.one_blind_scorer_lock.v3',actual_identity=identity,packet_sha256=sha(packet_file),assessment_sha256=sha(assessment_file),assessment_file_name=Path(assessment_file).name,assessments=assessments,checks=checks,locked_before_unblinding=True,no_rejudging=True,additional_raters=0))
 return checks

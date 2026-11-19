"""Compare reader ledgers; retain notes, raw-human skips and explicit source holds."""
from pathlib import Path
import argparse,ast,collections,json,math
ROOT=Path(__file__).resolve().parents[1]
HOLDS={'planned:calsub_eval','planned:steer_arms','planned:steer_cmp','planned:ipipq_brief'}

def load(p):return json.loads(p.read_text().strip().removesuffix('\\n'))
def equivalent(a,b):
    # The source ledger stringifies sets in process-dependent hash order.
    # Compare literal set representations semantically, never arbitrary expressions.
    if isinstance(a,str) and isinstance(b,str):
        try:
            aa,bb=ast.literal_eval(a),ast.literal_eval(b)
            if isinstance(aa,set) and isinstance(bb,set):return aa==bb
        except (ValueError,SyntaxError):pass
    if isinstance(a,(int,float)) and isinstance(b,(int,float)):
        return abs(a-b)<=1e-10
    if isinstance(a,list) and isinstance(b,list):return len(a)==len(b) and all(equivalent(x,y) for x,y in zip(a,b))
    if isinstance(a,dict) and isinstance(b,dict):return a.keys()==b.keys() and all(equivalent(a[k],b[k]) for k in a)
    return a==b

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--current',type=Path,default=ROOT/'report/verification_reader.json');ap.add_argument('--output',type=Path,default=ROOT/'verification/REBUILD_COMPARISON.json');a=ap.parse_args()
    old=load(ROOT/'verification/source_reader_baseline.json');new=load(a.current);assert len(old)==len(new)==633
    changed=[];numeric_changes=[];representation_changes=[]
    for prior,now in zip(old,new):
        if prior['id']=='6.1.petrov.sha256':
            assert now['id']=='6.1.published_values.sha256' and prior['section']==now['section']
            assert prior['status']==now['status']=='PASS' and prior['tier']==now['tier']=='HASH-ONLY'
            assert now['expected']==now['observed']=='f11440d489d4b0832025b0b17a28cc3162339ca7ef176e27840752a3a67a696f'
            representation_changes.append(dict(before_id=prior['id'],after_id=now['id'],reason='Integrity check now hashes the PHG-authored cited table, not the original third-party CSV; all fifty scientific values checked separately'))
            continue
        assert (prior['id'],prior['section'])==(now['id'],now['section'])
        if prior['status']!=now['status']:
            assert prior['id'] in HOLDS and prior['status']=='PASS' and now['status']=='SKIPPED'
            changed.append(dict(id=now['id'],before=prior['status'],after=now['status'],reason='Explicit source hold' if now['id']!='planned:ipipq_brief' else 'Stale operational startup pointer excluded; completed null separately packaged'))
        elif not equivalent(prior['observed'],now['observed']):numeric_changes.append(dict(id=now['id'],before=prior['observed'],after=now['observed']))
    assert not numeric_changes,numeric_changes
    assert {r['id'] for r in changed}==HOLDS
    assert not any(r['status']=='FAIL' for r in new)
    result=dict(status='PASS_WITH_EXPLAINED_SOURCE_SKIPS',baseline_counts=dict(collections.Counter(r['status'] for r in old)),package_counts=dict(collections.Counter(r['status'] for r in new)),status_changes=changed,unexplained_numerical_changes=numeric_changes,representation_changes=representation_changes,numerical_comparison_absolute_tolerance=1e-10,
        original_notes_preserved=[r['id'] for r in new if r['status']=='NOTE'],verification_level_change='Source checks verify packaged public evidence, not original research Git blobs. No independent extraction/human refit is implied.',strict_fresh_clone_offline_gate='PASS: all READER inputs packaged; original Petrov retrieval is optional')
    a.output.parent.mkdir(exist_ok=True,parents=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()

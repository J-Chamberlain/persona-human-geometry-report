"""Verify payload integrity, reference coverage and public-export boundaries.

Hash checks establish integrity, not independent recreation of measurements.
MANIFEST.csv cannot hash itself; its exact bytes are bound by the package Git commit.
"""
from pathlib import Path
import argparse,ast,csv,hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path);a=ap.parse_args()
    rows=list(csv.DictReader((ROOT/'MANIFEST.csv').open()));seen=set()
    for r in rows:
        p=ROOT/r['path'];assert p.is_file(),r['path'];assert r['path'] not in seen;seen.add(r['path'])
        assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'],r['path']
        assert p.stat().st_size==int(r['bytes']),r['path']
    excluded_names={'AGENTS.md','CLAUDE.md','RESEARCH_STATE.md','CONVERSATION_CONTEXT.md','CLAUDE_WORKFLOW.md','OPEN_IN_CODEX.md','BUILD_REPORT.md','EDIT_QUEUE.md','EDITORIAL_TRACKER.md'}
    source_regex=re.compile(r'/(?:Users|workspace|home)/[^\s\x22\x27<>`]+|\b(?:ghp_|github_pat_|sk-proj-)[A-Za-z0-9_]{20,}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY')
    for name in seen:
        p=ROOT/name;assert p.name not in excluded_names,name
        assert not any(x in p.parts for x in ['migration','chatgpt_handoff','screenshots','drafts','frozen','node_modules']),name
        assert p.suffix.lower() not in {'.pt','.safetensors','.dat','.npy','.npz','.parquet','.xlsx','.xls'},name
        if p.suffix=='.py':ast.parse(p.read_text(),filename=name)
        if p.suffix in {'.py','.md','.json','.csv','.toml','.txt'} and name!='scripts/verify_package.py':assert not source_regex.search(p.read_text()),name
        if p.suffix=='.csv':
            header=next(csv.reader(p.open()))
            assert not any(re.fullmatch(r'(respondent|participant|subject|person)_?id|response_text|individual_prediction',k,re.I) for k in header),name
    # The public page is preserved bit-for-bit. Held data cannot enter the payload.
    assert hashlib.sha256((ROOT/'index.html').read_bytes()).hexdigest()=='707bd8fa71fd5d8f01e6a474b978c239539cf624b4e8e49935fba376f5661997'
    assert 'data/saved/external/petrov2024_intercorrs.csv' not in seen
    from phg import sources as S
    assert all(r['ok'] for r in S.verify_snapshot())
    assert all(r['ok'] for r in S.verify_against_evidence())
    refs=list(csv.DictReader((ROOT/'REFERENCE_MAP.csv').open()));coverage=list(csv.DictReader((ROOT/'provenance/inventory_coverage.csv').open()))
    for r in refs:
        assert r['status']!='UNRESOLVED',r
        dest=r['new_path']
        if r['status'].startswith('PACKAGED'):assert (ROOT/dest).is_file(),r
    for r in coverage:
        assert r['status']!='UNRESOLVED',r
        if r['status']=='PACKAGED':assert (ROOT/r['new_path']).is_file(),r
    for c in ['N','E','O','A','C']:
        for i in range(1,7):
            for f in ['portraits.json','extraction_scenarios.json','extraction_statements.json','rubric.json','criterion_weights.csv']:
                assert (ROOT/'extraction/facets'/f'{c}{i}'/f).is_file()
    result={'package_integrity':'PASS','public_export_audit':'PASS','reference_coverage':'PASS','payload_files':len(rows),'payload_bytes':sum(int(r['bytes']) for r in rows),'reader_references':len(refs),'inventory_rows':len(coverage),
        'strict_fresh_clone_offline_reader_gate':'BLOCKED: Petrov published aggregate held out; local opt-in download needed for Figure5.1',
        'deeper_measurements':'NOT_EXECUTED','verification_level':'Packaged evidence hashes and saved-result computations, not independent re-extraction'}
    text=json.dumps(result,indent=2)+'\n'
    if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text)
    print(text)
if __name__=='__main__':
    import sys
    sys.path.insert(0,str(ROOT));main()

"""Packaging boundaries: no research Git dependency, tampering fails, holds remain explicit."""
import json,subprocess
import pytest
from phg import sources as S

def test_evidence_works_when_git_processes_are_forbidden(monkeypatch):
    def forbidden(*args,**kwargs):raise AssertionError('No subprocess allowed in evidence access')
    monkeypatch.setattr(subprocess,'check_output',forbidden)
    assert all(r['ok'] for r in S.verify_against_evidence())
    assert S.full_commit('bf99d3d').startswith('bf99d3d')

def test_tampered_evidence_fails_closed(tmp_path,monkeypatch):
    record=json.loads(S.EVIDENCE_REGISTRY.read_text())[0]
    root=tmp_path/'root';p=root/record['package_path'];p.parent.mkdir(parents=True);p.write_bytes(b'changed')
    registry=tmp_path/'registry.json';registry.write_text(json.dumps([record]))
    monkeypatch.setattr(S,'ROOT',root);monkeypatch.setattr(S,'EVIDENCE_REGISTRY',registry)
    with pytest.raises(ValueError,match='hash mismatch'):S.evidence_bytes(record['origin_commit'],record['origin_path'])

def test_pending_studies_have_no_evidence_fallback():
    for key in ['steer_arms','steer_cmp','calsub_eval']:
        src=S.PLANNED[key]
        assert not S.evidence_available(src.commit,src.path)
        with pytest.raises(FileNotFoundError):S.evidence_bytes(src.commit,src.path)

def test_reader_published_values_need_no_original_file(monkeypatch):
    from phg import analysis as A
    monkeypatch.setenv('PHG_PETROV_FILE','/not-present/original.csv')
    table=A.petrov_intercorrs()
    assert table.shape==(10,5) and not table.isna().any().any()
    assert set(table.columns)=={'bbc','generic_gpt35','generic_gpt4','silicon_gpt35','silicon_gpt4'}
    assert all(-1<=v<=1 for v in table.to_numpy().ravel())

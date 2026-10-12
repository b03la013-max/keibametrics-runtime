"""Read-only real Railway receipt regression. Never sends data or adds OOS."""
import base64
import hashlib
import json
from pathlib import Path
import sys
import tarfile
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / "runtime"))
from local_aki_columns import sha


def test_real_external_source_krs_final_result_and_paper_boundary():
    root = ROOT / "evidence/local_aki_columns_20261012"
    manifest = json.loads((root / "external_acceptance_manifest.json").read_text())
    archive_path = root / "kaw_r11_external_receipts.tar.gz"
    assert hashlib.sha256(archive_path.read_bytes()).hexdigest() == manifest["archive_sha256"]
    attestation = json.loads((root / "destination_verification.json").read_text())
    key = Ed25519PublicKey.from_public_bytes(base64.b64decode(attestation["health"]["receipt_public_key_b64"]))
    prefix = "external/KM-LOCAL-KAW-20261012-R11-LIVE-R1/39f06c07ee208cf9/"
    with tarfile.open(archive_path,"r:gz") as archive:
        def load(name): return json.load(archive.extractfile(prefix + name + ".json"))
        envelopes = {p:load(n) for p,n in (("PRE_KRS","pre_krs_receipt"),("KRS_RUN","krs_receipt"),
            ("FINAL","final_receipt"),("RESULT","replay_result_receipt"))}
        envelopes["SOURCE"] = json.loads((ROOT / manifest["canonical_source_path"]).read_text())
        assert envelopes["SOURCE"]["receipt_sha256"] == manifest["canonical_source_receipt_sha256"]
        for phase, e in envelopes.items():
            raw = json.dumps(e["receipt"],ensure_ascii=False,sort_keys=True,separators=(",", ":")).encode()
            key.verify(base64.b64decode(e["signature"]),raw)
            assert sha(e["artifact"]) == e["receipt"]["artifact_sha256"]
            assert hashlib.sha256(raw).hexdigest() == e["receipt_sha256"]
            assert e["receipt"]["phase"] == phase
            assert e["receipt"]["race_id"] == manifest["source_race_id"]
        run = envelopes["KRS_RUN"]["artifact"]
        assert run["actual_run_count"] == 20000
        assert run["input_sha256"] == envelopes["PRE_KRS"]["artifact"]["input_sha256"] == sha(load("krs_input"))
        final = envelopes["FINAL"]
        fpp = final["artifact"]["final_prediction_package"]
        columns = fpp["aki_selection"]["columns"]
        for rid, roles in fpp["roles"].items():
            assert roles == [c for c in ("W","P2","P3") if rid in columns[c]["selected"]]
        assert len(fpp["paper_tickets"]) == 10
        assert final["artifact"]["final_ticket"]["tickets"] == []
        assert final["artifact"]["capital_policy_decision"]["decision"] == "PAPER"
        result = envelopes["RESULT"]["artifact"]
        assert result["frozen_refs"]["final_receipt_sha256"] == final["receipt_sha256"]
        assert result["settlement"]["investment"] == 0
        assert result["settlement"]["pfs"] is None
        assert load("paper_settlement")["investment"] == 1000
        assert load("paper_settlement")["return"] == 0
        assert load("paper_reflection")["failure_localization"]["first_material_failure"] == "PREDICTION_ROLE_P2"
        assert load("paper_learning")["production_change_authorized"] is False
        assert manifest["unknown_future_oos_count"] == 0


def test_multi_venue_real_signed_variable_counts():
    root = ROOT / 'evidence/local_aki_columns_20261012'
    manifest = json.loads((root / 'multi_venue_manifest.json').read_text())
    path = root / 'multi_venue_external_receipts.tar.gz'
    assert hashlib.sha256(path.read_bytes()).hexdigest() == manifest['archive_sha256']
    attestation = json.loads((root / 'destination_verification.json').read_text())
    key = Ed25519PublicKey.from_public_bytes(base64.b64decode(attestation['health']['receipt_public_key_b64']))
    counts = []
    with tarfile.open(path, 'r:gz') as archive:
        for case in manifest['cases']:
            def load(name):
                raw = archive.extractfile(case['prefix'] + '/' + name + '.json').read()
                assert hashlib.sha256(raw).hexdigest() == case['files'][name + '.json']
                return json.loads(raw)
            envelopes = [load(n) for n in ('pre_krs_receipt','krs_receipt','final_receipt')]
            for e in envelopes:
                raw = json.dumps(e['receipt'],ensure_ascii=False,sort_keys=True,separators=(',', ':')).encode()
                key.verify(base64.b64decode(e['signature']),raw)
                assert sha(e['artifact']) == e['receipt']['artifact_sha256']
                assert hashlib.sha256(raw).hexdigest() == e['receipt_sha256']
                assert e['receipt']['race_id'] == case['acceptance']['race_id']
            assert envelopes[1]['artifact']['actual_run_count'] == 20000
            assert envelopes[1]['artifact']['input_sha256'] == envelopes[0]['artifact']['input_sha256'] == sha(load('krs_input'))
            final = envelopes[2]
            assert final['receipt_sha256'] == case['acceptance']['final_receipt_sha256']
            assert final['artifact']['final_prediction_package']['aki_selection'] == load('selection')
            counts.append(len(final['artifact']['final_prediction_package']['paper_tickets']))
            assert final['artifact']['final_ticket']['tickets'] == []
            assert final['artifact']['capital_policy_decision']['decision'] == 'PAPER'
    assert counts == [2,341,25]
    assert manifest['unique_actual_krs_runs'] == 60000
    assert manifest['unknown_future_oos_count'] == 0


def test_fnb_real_result_only_source_raw_and_signed_postresult():
    from runtime.formal_execution_orchestrator import parse_official_result_snapshot
    root=ROOT/'evidence/local_aki_columns_20261012'
    manifest=json.loads((root/'fnb_r06_postresult_manifest.json').read_text())
    path=root/'fnb_r06_postresult_receipts.tar.gz'
    assert hashlib.sha256(path.read_bytes()).hexdigest()==manifest['archive_sha256']
    attestation=json.loads((root/'destination_verification.json').read_text())
    key=Ed25519PublicKey.from_public_bytes(base64.b64decode(attestation['health']['receipt_public_key_b64']))
    with tarfile.open(path,'r:gz') as archive:
        def load(name):
            raw=archive.extractfile(name+'.json').read()
            assert hashlib.sha256(raw).hexdigest()==manifest['files'][name+'.json']
            return json.loads(raw)
        source=load('official_result_source_receipt');result=load('replay_result_receipt')
        for e,phase in ((source,'SOURCE'),(result,'RESULT')):
            raw=json.dumps(e['receipt'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
            key.verify(base64.b64decode(e['signature']),raw)
            assert sha(e['artifact'])==e['receipt']['artifact_sha256']
            assert hashlib.sha256(raw).hexdigest()==e['receipt_sha256']
            assert e['receipt']['phase']==phase
        order,payouts=parse_official_result_snapshot(source['artifact']['sources'][0],
            source['artifact']['source_race_context'],list(range(1,13)))
        assert order[:3]==[7,12,8]
        assert payouts=={'EXACTA':370,'TRIO':8890,'TRIFECTA':13600}
        assert load('official_result_source_request')['temporal_mode']=='RESULT_ONLY_REPLAY'
        assert result['artifact']['official_result']['finish_order']==order
        assert result['artifact']['frozen_refs']['final_receipt_sha256']==manifest['acceptance']['final_receipt_sha256']
        assert result['artifact']['settlement']['investment']==0
        assert result['artifact']['settlement']['pfs'] is None
        assert load('paper_settlement')['investment']==2500
        assert load('paper_settlement')['return']==0
        assert load('paper_learning')['production_change_authorized'] is False
        assert manifest['actual_additional_krs_runs']==0


def test_same_race_worker_lock_prevents_second_external_dispatch(tmp_path,monkeypatch):
    import fcntl
    from tools import local_aki_external_acceptance as api
    request=tmp_path/'intent.json';source=tmp_path/'source.json'
    request.write_text(json.dumps({'race_id':'LOCAL-LOCK-TEST'}))
    source.write_text(json.dumps({'receipt_sha256':'signed-source-hash'}))
    token=sha({'race_id':'LOCAL-LOCK-TEST','source_receipt':'signed-source-hash'})
    locks=tmp_path/'out/worker_locks';locks.mkdir(parents=True)
    def must_not_run(*args): raise AssertionError('duplicate dispatch')
    monkeypatch.setattr(api,'_run',must_not_run)
    import pytest
    with (locks/(token+'.lock')).open('a+') as handle:
        fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
        with pytest.raises(RuntimeError,match='EXTERNAL_EXECUTION_WAIT'):
            api.run(request,source,tmp_path/'out')
    monkeypatch.setattr(api,'_run',lambda *args:{'execution_id':'existing-id','actual_run_count':20000})
    assert api.run(request,source,tmp_path/'out')['execution_id']=='existing-id'
    assert json.loads((locks/(token+'.json')).read_text())['status']=='VERIFIED_FINAL_SAVED'


def test_real_cached_source_recomputed_without_another_external_krs(tmp_path,monkeypatch):
    from tools import local_aki_external_acceptance as api
    import urllib.request
    def no_network(*args,**kwargs):raise AssertionError('cached run must not execute another external KRS')
    monkeypatch.setattr(urllib.request,'urlopen',no_network)
    race='KM-LOCAL-OHI-20261007-R04-LIVE-R1'
    directory=tmp_path/race/'7a4c90234425aee6'
    assert not directory.exists()
    accepted=api.run(ROOT/('runtime/formal_intents/'+race+'.json'),ROOT/('runtime/executions/'+race+
        '/FORMAL/runs/37582570990-formal/source_receipt_envelope.json'),tmp_path)
    assert accepted['paper_ticket_count']==2
    assert accepted['actual_run_count']==20000
    assert (directory/'signed_source_input.json').exists()


def test_all_fourteen_external_manifests_are_only_transport_evidence():
    from runtime.local_physical.nar_source_manifest import LOCAL_BABA_CODES
    root=ROOT/'evidence/local_aki_columns_20261012/venue_manifest_transport'
    assert {p.stem for p in root.glob('*.json')}==set(LOCAL_BABA_CODES)
    for p in root.glob('*.json'):
        x=json.loads(p.read_text())
        assert x['status']=='EXTERNAL_MANIFEST_CONTRACT_PASS'
        assert x['response']['venue_id']==p.stem
        assert x['source_acquired'] is False
        assert x['prestart_source_acceptance'] is False
        assert x['unknown_future_oos_count']==0

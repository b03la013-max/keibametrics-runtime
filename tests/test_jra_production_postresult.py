import hashlib
import json
import sys
from pathlib import Path
import unittest
from copy import deepcopy
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from jra_production_postresult import (
    build_result_request, build_settlement_correction, settle_final, verify_final, ProductionPostResultError, _sha,
)
from post_result_learning import build_post_result_review


def final(decision="EXECUTE_RECOMMENDATION_PORTFOLIO", receipt_ts="2026-10-11T06:30:00+00:00"):
    tickets = [
        {"bet_type": "EXACTA", "selection": [4, 2], "stake": 100},
        {"bet_type": "EXACTA", "selection": [2, 4], "stake": 100},
        {"bet_type": "TRIFECTA", "selection": [4, 2, 6], "stake": 100},
    ]
    f = {
        "race_id": "KM-JRA-TKY-20261011-R11", "family_id": "JRA",
        "temporal_mode": "FORMAL-PRE-RACE",
        "prediction_cutoff": "2026-10-11T06:20:00+00:00",
        "scheduled_post_at": "2026-10-11T06:45:00+00:00",
        "static_prediction": {"ranking": ["4", "2", "6", "1"]},
        "final_prediction_package": {"roles": {"4": ["W", "P2", "P3"], "2": ["W", "P2", "P3"], "6": ["P3"]},
                                     "validation_status": "UNVALIDATED"},
        "capital_policy_decision": {"decision": decision},
        "final_ticket": {"tickets": tickets, "total_investment": 300, "no_bet": False},
        "final_receipt": {"receipt": {"timestamp": receipt_ts}},
        "final_receipt_sha256": "f" * 64,
    }
    f["sha256"] = _sha(f)
    return f


OFFICIAL = {"top3": [4, 2, 6], "payouts": {
    "EXACTA": {"selection": [4, 2], "per_100_yen": 1230},
    "TRIO": {"selection": [2, 4, 6], "per_100_yen": 2210},
    "TRIFECTA": {"selection": [4, 2, 6], "per_100_yen": 9870}}}
EVIDENCE = {"parsed": {"runners": [{"horse_no": h, "finish": i + 1} for i, h in enumerate([4, 2, 6, 1])]},
            "url": "https://www.jra.go.jp/x", "sha256": "a" * 64, "captured_at": "2026-10-11T07:00:00+00:00"}

WITHDRAWAL_OFFICIAL={"top3":[4,2,1],"refund_runner_ids":[6],"payouts":{
    "EXACTA":{"selection":[4,2],"per_100_yen":1230},
    "TRIO":{"selection":[1,2,4],"per_100_yen":2210},
    "TRIFECTA":{"selection":[4,2,1],"per_100_yen":9870}}}


class TestProductionPostResult(unittest.TestCase):
    def test_settles_exact_frozen_tickets_and_separates_purchase(self):
        s = settle_final(final(), OFFICIAL)
        self.assertEqual(s["total_investment"], 300)
        self.assertEqual(s["total_payout"], 1230 + 9870)
        self.assertEqual(s["actual_purchase_status"], "UNVERIFIED")
        self.assertIsNone(s['actual_purchase_pfs'])
        self.assertEqual(s['capital_exposure_class'],'RECOMMENDATION')
        self.assertEqual(len(s["winning_tickets"]), 2)

    def test_request_feeds_canonical_review(self):
        f = final()
        req = build_result_request(f, OFFICIAL, EVIDENCE)
        self.assertEqual(req["official_result"]["finish_order"], [4, 2, 6, 1])
        self.assertEqual(req["frozen_prediction_ref"]["immutable_final_sha256"], f["sha256"])
        review = build_post_result_review(req, f)
        self.assertEqual(review["race_id"], f["race_id"])

    def test_tampered_or_late_final_rejected(self):
        f = final()
        f["final_ticket"]["total_investment"] = 200
        with self.assertRaisesRegex(ProductionPostResultError, "HASH_INVALID"):
            verify_final(f)
        with self.assertRaisesRegex(ProductionPostResultError, "AFTER_POST"):
            verify_final(final(receipt_ts="2026-10-11T06:46:00+00:00"))


if __name__ == "__main__":
    unittest.main()


def test_refunds_use_official_withdrawn_runner_and_net_risk_denominator():
    f=final(); before=deepcopy(f)
    official={**deepcopy(WITHDRAWAL_OFFICIAL),"non_finishers":[
        {"horse_no":6,"finish_status":"EXCLUDED"}]}
    # The affected trifecta must be returned once, never both won and returned.
    s=settle_final(f,official)
    assert s['total_investment']==300 and s['refund']==100
    assert s['effective_investment']==200 and s['total_payout']==1230
    assert s['profit_loss']==1030 and s['pfs']==615
    assert len(s['refunded_tickets'])==1 and len(s['winning_tickets'])==1
    assert f==before
    req=build_result_request(f,official,EVIDENCE)
    review=build_post_result_review(req,f)
    assert review['capital']['refund']==100 and review['capital']['effective_investment']==200
    assert review['capital']['profit_loss']==1030 and review['capital']['pfs']==615


def test_wholly_refunded_or_zero_stake_has_undefined_pfs():
    f=final();f['final_ticket'].update(tickets=[f['final_ticket']['tickets'][-1]],total_investment=100)
    s=settle_final(f,WITHDRAWAL_OFFICIAL)
    assert s['refund']==100 and s['effective_investment']==0
    assert s['total_payout']==0 and s['profit_loss']==0 and s['pfs'] is None
    f=final();f['final_ticket'].update(tickets=[],total_investment=0,no_bet=True)
    s=settle_final(f,OFFICIAL)
    assert s['pfs'] is None and s['gross_stake_pfs'] is None


@pytest.mark.parametrize('status',['DID_NOT_FINISH','DISQUALIFIED'])
def test_noncompletion_and_disqualification_are_not_withdrawal_refunds(status):
    official={**OFFICIAL,'refund_runner_ids':[6],
              'non_finishers':[{'horse_no':6,'finish_status':status}]}
    with pytest.raises(ProductionPostResultError,match='NONCANCELLATION_REFUND_FORBIDDEN'):
        settle_final(final(),official)


def test_refund_correction_is_a_separate_audit_and_keeps_original_bytes():
    f=final(); original=build_result_request(f,OFFICIAL,EVIDENCE)
    unchanged=json.dumps([f,original],ensure_ascii=False,sort_keys=True)
    corrected=WITHDRAWAL_OFFICIAL
    audit=build_settlement_correction(f,original,corrected,EVIDENCE,
                                    audited_at='2026-10-11T07:10:00+00:00')
    assert audit['corrected_settlement']['refund']==100
    assert audit['original_settlement']['refund']==0
    assert audit['signed_result_correction']=='NOT_ISSUED'
    assert audit['old_learning_unchanged'] and audit['original_frozen_prediction_unchanged']
    assert audit['sha256']==_sha({k:v for k,v in audit.items() if k!='sha256'})
    assert json.dumps([f,original],ensure_ascii=False,sort_keys=True)==unchanged
    with pytest.raises(ProductionPostResultError,match='CHRONOLOGY'):
        build_settlement_correction(f,original,corrected,EVIDENCE,
                                    audited_at='2026-10-11T06:59:59+00:00')


def test_legacy_zero_refund_review_hash_is_unchanged_by_refund_support():
    req=build_result_request(final(),OFFICIAL,EVIDENCE)
    req['settlement'].pop('effective_investment')
    review=build_post_result_review(req,final())
    assert 'refund' not in review['capital'] and 'effective_investment' not in review['capital']


def _portable_source_checkpoint(tmp_path):
    """Small synthetic crypto fixture; no private Raw or retained key files."""
    import base64
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from execution_store import persist_phase
    f = final()
    race = f['race_id']
    execution = race + '-LIVE-R1'
    active = [{'runner_id': n, 'horse_no': int(n), 'status': 'ACTIVE'}
              for n in f['static_prediction']['ranking']]
    source = {'race_id': race, 'family_id': 'JRA', 'source_freeze_at': '2026-10-11T06:00:00Z',
              'official_runner_universe': {'runners': active},
              'jra_declared_runner_universe': {'runners': active + [
                  {'runner_id': '13', 'horse_no': 13, 'status': 'CANCELLED'}]}}
    source['source_snapshot_sha256'] = _sha(source)
    receipt = {'race_id': race, 'family': 'JRA', 'phase': 'SOURCE', 'status': 'PASS',
               'errors': [], 'artifact_sha256': _sha(source)}
    key = Ed25519PrivateKey.generate()
    envelope = {'artifact': source, 'receipt': receipt, 'receipt_sha256': _sha(receipt),
                'github_repository': 'b03la013-max/keibametrics-runtime',
                'signature_alg': 'Ed25519',
                'signer_trust_class': 'GITHUB_ACTIONS_EPHEMERAL_ED25519_PLUS_GITHUB_OIDC_ATTESTATION',
                'receipt_public_key_b64': base64.b64encode(key.public_key().public_bytes(
                    serialization.Encoding.Raw, serialization.PublicFormat.Raw)).decode(),
                'signature': base64.b64encode(key.sign(json.dumps(receipt, ensure_ascii=False,
                    sort_keys=True, separators=(',', ':')).encode())).decode()}
    stage = {'execution_id': execution, 'receipt_sha256': envelope['receipt_sha256'],
             'source_snapshot_sha256': source['source_snapshot_sha256']}
    f['source_snapshot_sha256'] = source['source_snapshot_sha256']
    f['final_prediction_package']['execution_stage_manifest'] = {
        'SIGNED_SOURCE_RECEIPT_VERIFIED': stage}
    f['sha256'] = _sha({k: v for k, v in f.items() if k != 'sha256'})
    checkpoint = tmp_path / 'synthetic_input'
    checkpoint.mkdir()
    (checkpoint / 'source_receipt_envelope.json').write_text(json.dumps(envelope))
    stored = persist_phase(execution, 'SOURCE', 'synthetic-1', checkpoint,
                           root=tmp_path / 'runtime/executions')
    return f, Path(stored['path']) / 'source_receipt_envelope.json'


def test_portable_source_checkpoint_binds_crypto_declared_active_and_ticket_exposure(tmp_path, monkeypatch):
    import jra_production_postresult as module
    import jra_pedigree_corpus as trust
    f, path = _portable_source_checkpoint(tmp_path)
    calls = []
    monkeypatch.setattr(trust, '_attested', lambda p, **kw: calls.append((p, kw)) or True)
    declared, cancelled = module._source_bound_result_universe(tmp_path, f)
    assert set(declared) == {'1', '2', '4', '6', '13'} and cancelled == {'13'}
    assert calls[0][0] == path
    assert calls[0][1]['signer'] == 'km-jra-source-first-runner.yml'
    assert calls[0][1]['not_after'].isoformat() == f['prediction_cutoff']
    f['final_ticket']['tickets'][0]['selection'] = [4, 13]
    with pytest.raises(ValueError, match='FROZEN_TICKET_OUTSIDE_ACTIVE_SOURCE'):
        module._source_bound_result_universe(tmp_path, f)


def test_portable_source_oidc_failure_or_original_bytes_tamper_is_not_accepted(tmp_path, monkeypatch):
    import jra_production_postresult as module
    import jra_pedigree_corpus as trust
    f, path = _portable_source_checkpoint(tmp_path)
    monkeypatch.setattr(trust, '_attested', lambda *a, **k: False)
    with pytest.raises(ValueError, match='SOURCE_OIDC_NOT_VERIFIED'):
        module._source_bound_result_universe(tmp_path, f)
    path.write_text('{}')
    with pytest.raises(ValueError, match='EXECUTION_STORE_FILE_HASH_MISMATCH'):
        module._source_bound_result_universe(tmp_path, f)


def _portable_normal_process(tmp_path, monkeypatch, parsed):
    import jra_production_postresult as module
    import jra_candidate_postresult_closedloop as result_module
    from datetime import datetime, timezone
    f = final()
    output = tmp_path / 'runtime/final_artifacts' / (f['race_id'] + '.json')
    output.parent.mkdir(parents=True)
    output.write_text(json.dumps(f))
    monkeypatch.setattr(module, 'verify_archived_final_signature', lambda *a, **k: None)
    monkeypatch.setattr(module.subprocess, 'check_output', lambda *a, **k: '2026-10-11T06:00:00+00:00')
    monkeypatch.setattr(module, '_intent_for', lambda *a: {
        'race_date': '2026-10-11', 'race_no': 11, 'jra_source': {'jra_meeting_key': '0520260403'}})
    def source_must_not_be_called(*a):
        raise AssertionError('NORMAL_RESULT_NEW_SOURCE_GATE')
    monkeypatch.setattr(module, '_source_bound_result_universe', source_must_not_be_called)
    evidence = {'parsed': parsed,
                'text': '払戻金 単勝 4 200円 馬単 4-2 1230円 3連複 2-4-6 2210円 3連単 4-2-6 9870円',
                'url': 'https://www.jra.go.jp/JRADB/accessS.html', 'sha256': 'a' * 64,
                'captured_at': '2026-10-11T07:00:00Z'}
    monkeypatch.setattr(result_module, 'fetch_jra_result', lambda *a: evidence)
    return module.process(tmp_path, f['race_id'], now=datetime(2026, 10, 11, 8, tzinfo=timezone.utc))


def test_portable_normal_old_checkpoint_needs_no_new_source_or_oidc_gate(tmp_path, monkeypatch):
    parsed = {'official': True, 'runners': [
        {'runner_id': str(n), 'horse_no': n, 'finish': i + 1} for i, n in enumerate([4, 2, 6, 1])],
        'non_finishers': []}
    assert _portable_normal_process(tmp_path, monkeypatch, parsed) == 'RESULT_REQUEST_WRITTEN'


def test_portable_duplicate_normal_universe_uses_old_strict_path(tmp_path, monkeypatch):
    parsed = {'official': True, 'runners': [
        {'runner_id': str(n), 'horse_no': n, 'finish': i + 1} for i, n in enumerate([4, 2, 6, 1, 1])],
        'non_finishers': []}
    with pytest.raises(ValueError, match='RUNNER_UNIVERSE_MISMATCH'):
        _portable_normal_process(tmp_path, monkeypatch, parsed)

# Owner B fixtures are local test records only, never actual Owner approval.
def _owner_b_fixture(root, race='KM-JRA-TKY-20261031-R06', *, commit=True):
    import subprocess
    import jra_production_postresult as module
    source=Path(__file__).resolve().parents[1]
    root.mkdir(parents=True,exist_ok=True)
    for name in module.OWNER_B_POLICY_FILES:
        target=root/name;target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes((source/name).read_bytes())
    operation,original_ref=module.OWNER_B_RECOVERY_SCOPES[race]
    original=root/original_ref;original.parent.mkdir(parents=True,exist_ok=True)
    if not original.exists():original.write_text('{"offline_fixture":true}\n')
    subprocess.run(['git','init','-q',str(root)],check=True)
    def save():
        subprocess.run(['git','add','.'],cwd=root,check=True)
        subprocess.run(['git','-c','user.name=offline-test','-c','user.email=offline@example.invalid',
                        'commit','-qm','offline fixture only'],cwd=root,check=True)
    save()
    policy={name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in module.OWNER_B_POLICY_FILES}
    record={'decision':'AUTHORIZE_JRA_POSTRESULT_RECOVERY','race_id':race,'operation':operation,
        'original_ref':original_ref,'artifact_file_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),
        'policy_source_sha256':module._sha(policy),'current_authority_manifest':'KM-FAMILY-CURRENT-AUTHORITY-20261012-R51',
        'authorized_by':'b03la013-max','authorization_ref':'OFFLINE_TEST_NOT_REAL_OWNER_GRANT',
        'authorized_at':'2026-11-01T00:00:00+00:00'}
    path=root/f'profiles/jra_postresult_recovery_approvals/{race}.json';path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(record))
    if commit:save()
    return record,path,save


def test_owner_b_unapproved_blocks_before_request_reuse_or_consumer_io(tmp_path,monkeypatch):
    import jra_production_postresult as module
    from jra_no_bet_postresult_learning import persist_no_bet_review_state
    monkeypatch.setattr(module.subprocess,'check_output',lambda *a,**k:pytest.fail('NO_UNAPPROVED_IO'))
    race='KM-JRA-TKY-20261031-R06'
    with pytest.raises(ProductionPostResultError,match='OWNER_B_APPROVAL_REQUIRED'):
        module.process(tmp_path,race)
    with pytest.raises(ProductionPostResultError,match='OWNER_B_APPROVAL_REQUIRED'):
        module.reuse_or_submit_production_result(tmp_path,{'race_id':race},
            call=lambda *a:pytest.fail('NO_PROVIDER_CALL'),checkpoint=tmp_path/'checkpoint',run_id='OFFLINE')
    with pytest.raises(ProductionPostResultError,match='OWNER_B_APPROVAL_REQUIRED'):
        persist_no_bet_review_state(tmp_path,{'race_id':'KM-JRA-TKY-20261031-R05'},{},
            execution_id='KM-JRA-TKY-20261031-R05-LIVE-R1',effective_time='2026-11-01T03:00:00+00:00')
    assert not list(tmp_path.rglob('*'))


@pytest.mark.parametrize('mutation',[{'race_id':'KM-JRA-TKY-20261101-R06'},
    {'operation':'ANY_RESULT'}, {'artifact_file_sha256':'0'*64}, {'policy_source_sha256':'0'*64},
    {'authorized_by':'some-other-actor'}, {'authorization_ref':''},
    {'authorized_at':'2999-01-01T00:00:00+00:00'}, {'current_authority_manifest':'R52'}])
def test_owner_b_even_committed_wrong_scope_or_pins_do_not_authorize(tmp_path,mutation):
    import jra_production_postresult as module
    record,path,save=_owner_b_fixture(tmp_path)
    record.update(mutation);path.write_text(json.dumps(record));save()
    with pytest.raises(ProductionPostResultError,match='OWNER_B_APPROVAL_REQUIRED'):
        module.require_owner_b_recovery(tmp_path,'KM-JRA-TKY-20261031-R06')


def test_owner_b_workspace_record_is_not_approval_and_scope_is_not_global(tmp_path,monkeypatch):
    import jra_production_postresult as module
    _owner_b_fixture(tmp_path,commit=False)
    with pytest.raises(ProductionPostResultError,match='OWNER_B_APPROVAL_REQUIRED'):
        module.require_owner_b_recovery(tmp_path,'KM-JRA-TKY-20261031-R06')
    monkeypatch.setattr(module.subprocess,'check_output',lambda *a,**k:pytest.fail('NORMAL_RACE_NEEDS_NO_OWNER_B_IO'))
    assert module.require_owner_b_recovery(tmp_path,'KM-JRA-TKY-20261101-R06') is None
    assert module.require_owner_b_recovery(tmp_path,'KM-JRA-KYO-20261101-R06') is None


def test_owner_b_exact_committed_record_unlocks_one_race_only(tmp_path):
    import jra_production_postresult as module
    record,path,_=_owner_b_fixture(tmp_path)
    before={p:p.read_bytes() for p in tmp_path.rglob('*.json')}
    out=module.require_owner_b_recovery(tmp_path,'KM-JRA-TKY-20261031-R06')
    assert out['operation']=='FORMAL_RESULT_SETTLEMENT_REVIEW_STATE'
    assert out['authorization_record_sha256']==hashlib.sha256(path.read_bytes()).hexdigest()
    with pytest.raises(ProductionPostResultError,match='OWNER_B_APPROVAL_REQUIRED'):
        module.require_owner_b_recovery(tmp_path,'KM-JRA-TKY-20261031-R05')
    assert before=={p:p.read_bytes() for p in before}


def test_owner_b_mixed_batch_saves_normal_race_before_material_health_exit(tmp_path,monkeypatch,capsys):
    import jra_production_postresult as module
    from datetime import datetime,timedelta,timezone
    held='KM-JRA-TKY-20261031-R06';normal='KM-JRA-KYO-20261101-R06'
    now=datetime.now(timezone.utc)
    folder=tmp_path/'runtime/final_artifacts';folder.mkdir(parents=True)
    for rid in (held,normal):
        body=final();body['race_id']=rid;body['scheduled_post_at']=(now-timedelta(hours=1)).isoformat()
        (folder/(rid+'.json')).write_text(json.dumps(body))
    original_process=module.process;calls=[]
    def process(root,race_id,**kw):
        if race_id==held:return original_process(root,race_id,**kw)
        calls.append(race_id);out=root/'runtime/results'/(race_id+'.json');out.parent.mkdir(parents=True)
        out.write_text('{"offline_normal_result":true}')
        return 'RESULT_REQUEST_WRITTEN'
    monkeypatch.setattr(module,'process',process)
    assert module.main(['--repo-root',str(tmp_path),'--days','3'])==2
    report=json.loads(capsys.readouterr().out)
    assert calls==[normal] and (tmp_path/'runtime/results'/(normal+'.json')).exists()
    assert report['counts']['BLOCKED_OWNER_APPROVAL']==1 and report['material_failure_count']==1
    assert not (tmp_path/'runtime/results'/(held+'.json')).exists()
    from jra_postresult_health import aggregate_execution_health
    path=tmp_path/'health.json';path.write_text(json.dumps(report))
    aggregate=aggregate_execution_health({'production':path},{'production':'2'})
    assert aggregate['counts']['BLOCKED_OWNER_APPROVAL']==1
    assert not any(x.get('error_code','').startswith('LANE_EXIT_WITHOUT') for x in aggregate['processed'])


def test_owner_b_view_only_grant_does_not_open_result_signing(tmp_path):
    import jra_production_postresult as module
    race='KM-JRA-TKY-20261031-R05';_owner_b_fixture(tmp_path,race)
    with pytest.raises(ProductionPostResultError,match='OWNER_B_APPROVAL_REQUIRED'):
        module.process(tmp_path,race)
    with pytest.raises(ProductionPostResultError,match='OWNER_B_APPROVAL_REQUIRED'):
        module.reuse_or_submit_production_result(tmp_path,{'race_id':race},
            call=lambda *a:pytest.fail('VIEW_ONLY_MUST_NOT_SIGN'),checkpoint=tmp_path/'checkpoint',run_id='OFFLINE')


def _owner_b_no_bet_data(root):
    from test_jra_no_bet_postresult_learning import build_input
    from jra_no_bet_postresult_learning import build_no_bet_learning
    import re
    def move(value):
        if isinstance(value,dict):return {k:move(v) for k,v in value.items()}
        if isinstance(value,list):return [move(v) for v in value]
        if isinstance(value,str) and re.match(r'^KM-JRA-[A-Z]{3}-\d{8}-R\d{2}',value):return value.replace('20261010','20261031')
        if isinstance(value,str) and value.startswith('2026-10-10T'):return value.replace('2026-10-10T','2026-10-31T')
        return value
    terminal,result=build_input();terminal=move(terminal)
    terminal['sha256']=_sha({k:v for k,v in terminal.items() if k!='sha256'})
    learning=build_no_bet_learning(terminal,result,race_no=5,
        acquired_at='2026-10-31T13:00:00+09:00',result_source_snapshot_sha256='a'*64,official_capture_verified=True)
    eid=terminal['race_id']+'-LIVE-R1'
    for folder,value in [('jra_no_bet_terminals',terminal),('jra_no_bet_learning',learning)]:
        path=root/'runtime'/folder/(eid+'.json');path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(value))
    intent={'race_id':terminal['race_id'],'scheduled_post_at':'2026-10-31T12:05:00+09:00',
        'race_date':'2026-10-31','race_no':5,'prediction_cutoff':terminal.get('prediction_cutoff'),
        'jra_source':{'jra_meeting_key':'0520260501'}}
    path=root/'runtime/jra_formal_intents'/(eid+'.json');path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(intent))
    return terminal,learning,eid


def _run_owner_b_capture(root,monkeypatch):
    import yaml
    import datetime as clock
    import jra_same_day_results
    original_datetime=clock.datetime
    class OfflineClock(original_datetime):
        @classmethod
        def now(cls,tz=None):
            fixed=original_datetime(2026,11,1,3,30,tzinfo=clock.timezone.utc)
            return fixed.astimezone(tz) if tz is not None else fixed.replace(tzinfo=None)
    monkeypatch.setattr(clock,'datetime',OfflineClock)
    workflow=Path(__file__).resolve().parents[1]/'.github/workflows/km-jra-no-bet-postresult-learning.yml'
    doc=yaml.safe_load(workflow.read_text());step=next(s for s in doc['jobs']['official-result-ingest']['steps'] if s.get('id')=='capture')
    script=step['run'].split("python - <<'PY'\n",1)[1].rsplit('\nPY',1)[0]
    monkeypatch.chdir(root);monkeypatch.setenv('GITHUB_OUTPUT',str(root/'outputs'));monkeypatch.setenv('RACE_ID_FILTER','')
    monkeypatch.setattr(jra_same_day_results,'_open_day',lambda *a:pytest.fail('NO_FRESH_CAPTURE'))
    monkeypatch.setattr(jra_same_day_results,'_fetch_race',lambda *a,**k:pytest.fail('NO_FRESH_CAPTURE'))
    exec(compile(script,'<offline-owner-b-capture>','exec'),{})
    return json.loads((root/'runtime_out/owner_b_recovery_health.json').read_text())


def test_owner_b_no_bet_unapproved_is_visible_hold_without_capture_or_view(tmp_path,monkeypatch):
    terminal,learning,eid=_owner_b_no_bet_data(tmp_path)
    originals={p:p.read_bytes() for p in tmp_path.rglob('*.json')}
    report=_run_owner_b_capture(tmp_path,monkeypatch)
    assert report['counts']['BLOCKED_OWNER_APPROVAL']==1
    assert json.loads((tmp_path/'runtime_out/recorded_candidates.json').read_text())==[]
    assert originals=={p:p.read_bytes() for p in originals}
    assert not (tmp_path/'runtime/reviews_auto').exists()


def test_owner_b_approved_view_reuses_learning_and_never_opens_capture(tmp_path,monkeypatch):
    from jra_no_bet_postresult_learning import persist_no_bet_review_state
    terminal,learning,eid=_owner_b_no_bet_data(tmp_path)
    _owner_b_fixture(tmp_path,terminal['race_id'])
    learning_path=tmp_path/'runtime/jra_no_bet_learning'/(eid+'.json');original=learning_path.read_bytes()
    report=_run_owner_b_capture(tmp_path,monkeypatch)
    assert report['material_failure_count']==0
    assert json.loads((tmp_path/'runtime_out/recorded_candidates.json').read_text())==['runtime/jra_no_bet_learning/'+eid+'.json']
    out=persist_no_bet_review_state(tmp_path,terminal,learning,execution_id=eid,
        effective_time='2026-11-01T03:30:00+00:00',official_capture_verified=True)
    assert out['review']['capital']['pfs'] is None
    assert learning_path.read_bytes()==original
    bad=deepcopy(learning);bad['official_top3']=['1','2','3'];bad['sha256']=_sha({k:v for k,v in bad.items() if k!='sha256'})
    with pytest.raises(ValueError,match='CONSUMER_ORIGINAL_MISMATCH'):
        persist_no_bet_review_state(tmp_path,terminal,bad,execution_id=eid,
            effective_time='2026-11-01T03:30:00+00:00',official_capture_verified=True)


def test_owner_b_payload_cannot_hide_under_another_race_filename(tmp_path,monkeypatch):
    terminal,learning,eid=_owner_b_no_bet_data(tmp_path)
    alias='KM-JRA-KYO-20261031-R05-LIVE-R1.json'
    for folder in ('jra_no_bet_terminals','jra_formal_intents'):
        path=tmp_path/'runtime'/folder/(eid+'.json');path.rename(path.with_name(alias))
    report=_run_owner_b_capture(tmp_path,monkeypatch)
    assert report['material_failure_count']==1
    assert report['processed'][0]['error_code']=='NO_BET_FILE_PAYLOAD_IDENTITY_MISMATCH'
    assert json.loads((tmp_path/'runtime_out/recorded_candidates.json').read_text())==[]

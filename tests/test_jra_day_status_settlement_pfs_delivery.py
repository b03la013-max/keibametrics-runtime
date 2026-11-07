"""Regression: JRA Kyoto R10 2026-10-12 was a WIN but negative-PFS race.

A chat reader relying on the day-status index must see the frozen EXACTA
5>2, 360 yen return and 51.428571% virtual PFS, not a spurious 0% or
an unverified actual purchase claim.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime" / "jra_source_runtime"))
from jra_race_day_autopilot import race_status, write_status, _post_result_evidence
from jra_race_day_resolver import JST


def test_r10_signed_result_pfs_and_winning_ticket_are_not_dropped(tmp_path):
    rid = "KM-JRA-KYO-20261012-R10"
    final_file = tmp_path / "runtime" / "final_artifacts" / (rid + ".json")
    result_file = tmp_path / "runtime" / "results" / (rid + ".json")
    final_file.parent.mkdir(parents=True)
    result_file.parent.mkdir(parents=True)
    final_file.write_text(json.dumps({
        "final_receipt_sha256": "signed-final-identity",
        "sha256": "immutable-final-identity",
    }))
    result_file.write_text(json.dumps({
        "official_result": {"top3": [5, 2, 9]},
        "settlement": {
            "pfs_authority": "FROZEN-RECOMMENDATION-PFS",
            "pfs": 360 / 700 * 100,
            "total_investment": 700,
            "total_payout": 360,
            "profit_loss": -340,
            "winning_tickets": [{
                "bet_type": "EXACTA", "selection": [5, 2],
                "stake": 100, "payout_per_100": 360, "return": 360,
            }],
            "actual_purchase_status": "UNVERIFIED",
            "actual_pfs_status": "NOT_VERIFIED",
        },
    }))
    row = race_status(
        tmp_path, rid,
        {"post": "2026-10-12T15:10:00+09:00", "title": "堀川特別",
         "venue": "京都", "race_no": 10},
        {}, dt.datetime(2026, 10, 12, 17, 0, tzinfo=JST),
    )
    assert row["state"] == "SETTLED"
    assert row["official_top3"] == [5, 2, 9]
    settlement = row["settlement"]
    assert settlement["pfs"] == 360 / 700 * 100
    assert settlement["total_investment"] == 700
    assert settlement["total_payout"] == 360
    assert settlement["profit_loss"] == -340
    assert settlement["winning_tickets"] == [{
        "bet_type": "EXACTA", "selection": [5, 2],
        "stake": 100, "payout_per_100": 360, "return": 360,
    }]
    assert settlement["pfs_authority"] == "FROZEN-RECOMMENDATION-PFS"
    assert settlement["actual_purchase_status"] == "UNVERIFIED"
    assert settlement["actual_pfs_status"] == "NOT_VERIFIED"


def _save(root, relative, value, *, self_hash=False):
    from post_result_learning import _sha
    if self_hash:
        value={k:v for k,v in value.items() if k!='sha256'}
        value={**value,'sha256':_sha(value)}
    path=root/relative
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value))
    return value


def _stored_result(root):
    rid='KM-JRA-TKY-20261024-R03'
    final={'race_id':rid,'sha256':'a'*64,'final_receipt_sha256':'b'*64}
    result={'race_id':rid,'official_result':{'top3':[8,10,5]},
            'frozen_prediction_ref':{'immutable_final_sha256':final['sha256'],
                                     'final_receipt_sha256':final['final_receipt_sha256']},
            'settlement':{'total_investment':1900,'total_payout':880,'refund':0,
                          'pfs':880/1900*100,'actual_purchase_status':'UNVERIFIED'}}
    _save(root,'runtime/final_artifacts/'+rid+'.json',final)
    _save(root,'runtime/results/'+rid+'.json',result)
    _save(root,'runtime/jra_formal_intents/'+rid+'-LIVE-R1.json',{'race_id':rid})
    review=_save(root,'runtime/reviews_auto/'+rid+'-AUTO.json',{
        'race_id':rid,'immutable_final_artifact_sha256':final['sha256'],
        'final_receipt_sha256':final['final_receipt_sha256'],'official_top3':[8,10,5],
        'capital':{'investment':1900,'return':880}},self_hash=True)
    learning=_save(root,'runtime/learning_states/'+rid+'.json',{
        'race_id':rid,'state_id':rid+'-RECOVERY','source_review_sha256':review['sha256'],
        'effective_time':'2026-10-24T09:44:00+00:00'},self_hash=True)
    return rid,final,result,review,learning


def test_learning_presence_keeps_scheduler_compatibility_without_claiming_signed_closure(tmp_path):
    rid,final,result,review,learning=_stored_result(tmp_path)
    # A saved filename is deliberately insufficient evidence of a valid State.
    _save(tmp_path,'runtime/learning_states/'+rid+'.json',{})
    row=race_status(tmp_path,rid,{}, {},dt.datetime(2026,10,24,20,tzinfo=JST))
    assert row['state']=='SETTLED_SIGNED_RESULT_LEARNED'  # legacy scheduler enum
    assert row['display_state']=='RESULT_REQUEST_STORED'
    proof=row['post_result_evidence']
    assert proof['learning']['present'] is True
    assert proof['review_learning_bound'] is False
    assert proof['signature_validation_performed'] is False
    assert proof['production_closed_loop_claim']=='NOT_ESTABLISHED_BY_STORAGE_AUDIT'
    assert 'NOT_SIGNATURE_OR_CLOSED_LOOP_PROOF' in row['scheduler_state_scope']


def test_result_review_state_binding_and_actual_creation_time_are_separate_from_consumption(tmp_path):
    rid,final,result,review,learning=_stored_result(tmp_path)
    proof=_post_result_evidence(tmp_path,rid,[rid+'-LIVE-R1'],final=final,result=result)
    assert proof['storage_state']=='RESULT_REVIEW_LEARNING_STORED'
    assert proof['review_learning_bound'] is True
    assert proof['learning']['effective_time']=='2026-10-24T09:44:00+00:00'
    assert proof['learning']['consumption']=='NOT_ESTABLISHED_BY_STORAGE'
    assert proof['stored_result_receipts']==[]
    # Self-consistent but wrong lineage may not produce a bound-learning claim.
    _save(tmp_path,'runtime/learning_states/'+rid+'.json',
          {**learning,'source_review_sha256':'c'*64},self_hash=True)
    proof=_post_result_evidence(tmp_path,rid,[rid+'-LIVE-R1'],final=final,result=result)
    assert proof['learning']['self_hash_valid'] is True
    assert proof['review_learning_bound'] is False


def test_self_hashed_review_must_match_frozen_final_and_settlement(tmp_path):
    rid,final,result,review,learning=_stored_result(tmp_path)
    _save(tmp_path,'runtime/reviews_auto/'+rid+'-AUTO.json',
          {**review,'final_receipt_sha256':'c'*64},self_hash=True)
    proof=_post_result_evidence(tmp_path,rid,[rid+'-LIVE-R1'],final=final,result=result)
    assert proof['review']['self_hash_valid'] is True
    assert proof['review']['result_and_final_bound'] is False
    assert proof['review_learning_bound'] is False


def test_other_race_bodies_or_final_references_cannot_bind_a_saved_state(tmp_path):
    rid,final,result,review,learning=_stored_result(tmp_path)
    other='KM-JRA-TKY-20261024-R04'
    for candidate_final,candidate_result in [
        ({**final,'race_id':other},result),
        (final,{**result,'race_id':other}),
        (final,{**result,'frozen_prediction_ref':{**result['frozen_prediction_ref'],'immutable_final_sha256':'c'*64}}),
    ]:
        proof=_post_result_evidence(tmp_path,rid,[rid+'-LIVE-R1'],final=candidate_final,result=candidate_result)
        assert proof['review']['result_and_final_bound'] is False
        assert proof['review_learning_bound'] is False


def test_archived_receipt_storage_does_not_become_a_signature_verification(tmp_path):
    from execution_store import persist_phase
    from post_result_learning import _sha
    rid,final,result,review,learning=_stored_result(tmp_path)
    receipt={'race_id':rid,'phase':'RESULT','status':'PASS','artifact_sha256':_sha(result)}
    envelope={'receipt':receipt,'receipt_sha256':_sha(receipt),
              'signature':'presence-only-not-a-valid-signature'}
    stage=tmp_path/'archive-stage'
    _save(stage,'result_receipt_envelope.json',envelope)
    persist_phase(rid+'-LIVE-R1','RESULT','original-provider-run',stage,
                  root=tmp_path/'runtime/executions',github_sha='d'*40)
    proof=_post_result_evidence(tmp_path,rid,[rid+'-LIVE-R1'],final=final,result=result)
    stored=proof['stored_result_receipts'][0]
    assert stored['stored_manifest_verified'] and stored['request_payload_bound']
    assert stored['signature_present'] is True
    assert stored['signature_validation']=='NOT_PERFORMED_BY_STATUS_RENDERER'
    assert proof['signature_validation_performed'] is False
    assert proof['production_closed_loop_claim']=='NOT_ESTABLISHED_BY_STORAGE_AUDIT'


def test_zero_exposure_postresult_is_visible_with_null_pfs_and_no_new_capital(tmp_path):
    rid='KM-JRA-NGT-20261024-R01';eid=rid+'-LIVE-R1'
    _save(tmp_path,'runtime/jra_formal_intents/'+eid+'.json',{'race_id':rid})
    terminal=_save(tmp_path,'runtime/jra_no_bet_terminals/'+eid+'.json',{
        'race_id':rid,'profile':'KM-JRA-PRODUCTION-AKI-SELECTION-NO-BET-TERMINAL-v1-20261012',
        'lineage':'LIVE','signed_source_receipt_sha256':'a'*64},self_hash=True)
    _save(tmp_path,'runtime/jra_no_bet_learning/'+eid+'.json',{
        'race_id':rid,'status':'ZERO_EXPOSURE_RESULT_RECORDED',
        'decision_lineage_sha256':terminal['sha256'],
        'signed_pre_race_source_receipt_sha256':'a'*64,
        'investment':0,'payout':0,'pfs':None,'production_effect':'NONE',
        'official_top3':['2','8','4']},self_hash=True)
    row=race_status(tmp_path,rid,{}, {},dt.datetime(2026,10,24,20,tzinfo=JST))
    assert row['state']=='AKI_NO_BET'
    assert row['display_state']=='AKI_NO_BET / ZERO_EXPOSURE_RESULT_RECORDED'
    assert row['ticket_count']==row['total_investment']==0
    proof=row['post_result_evidence']
    assert proof['zero_exposure_result_learning_bound'] is True
    assert proof['zero_exposure_records'][0]['pfs'] is None
    assert proof['signature_validation_performed'] is False
    idx=write_status(tmp_path,'2026-10-24',dt.datetime(2026,10,24,20,tzinfo=JST),
                     {rid:{}},{},formal_runs=[],resolver_runs=[])
    assert idx['post_result_metrics']['zero_exposure_result_learning_bound']==1
    assert 'ZERO_EXPOSURE_RESULT_RECORDED' in (tmp_path/'runtime/jra_race_day_status/2026-10-24.md').read_text()


def test_saved_oct24_36_races_preserve_finals_and_separate_storage_from_signature():
    import os
    from collections import Counter
    root=Path(os.environ.get('KM_STATUS_DATA_ROOT') or Path(__file__).resolve().parents[1])
    schedule=json.loads((root/'runtime/jra_race_day_plan/2026-10-24.schedule.json').read_text())
    finals={p:p.read_bytes() for p in (root/'runtime/final_artifacts').glob('*20261024*.json')}
    rows=[race_status(root,rid,s,{},dt.datetime(2026,10,24,20,tzinfo=JST)) for rid,s in schedule.items()]
    expected_learning=int(os.environ.get('KM_STATUS_EXPECTED_LEARNING','32'))
    expected_receipts=int(os.environ.get('KM_STATUS_EXPECTED_RECEIPTS','33'))
    assert len(rows)==36 and len(finals)==33
    assert Counter(r['state'] for r in rows)=={
        'SETTLED_SIGNED_RESULT_LEARNED':expected_learning,'SETTLED':33-expected_learning,'AKI_NO_BET':3}
    proof=[r['post_result_evidence'] for r in rows]
    assert sum(p['review_learning_bound'] for p in proof)==expected_learning
    assert sum(p['zero_exposure_result_learning_bound'] for p in proof)==3
    assert sum(any(x.get('request_payload_bound') for x in p['stored_result_receipts']) for p in proof)==expected_receipts
    assert all(p['signature_validation_performed'] is False for p in proof)
    assert all(p.read_bytes()==body for p,body in finals.items())


def _original_signature_reference(root, rid='KM-JRA-KYO-20261031-R01'):
    """Copy existing archived originals; this helper never signs or calls a provider."""
    import os, shutil, hashlib, pytest
    from execution_store import resolve_phase
    from jra_presentation import digest
    source=Path(os.environ.get('KM_STATUS_VERIFICATION_DATA_ROOT') or Path(__file__).resolve().parents[1])
    paths={kind:'runtime/'+folder+'/'+rid+suffix for kind,folder,suffix in (
        ('final','final_artifacts','.json'),('result','results','.json'),
        ('review','reviews_auto','-AUTO.json'),('learning','learning_states','.json'))}
    if not all((source/p).is_file() for p in paths.values()):
        pytest.skip('Existing Oct31 signed originals are not materialized; no Live credit')
    for p in paths.values():
        target=root/p;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source/p,target)
    eid=rid+'-LIVE-R1'
    phase=resolve_phase(eid,'RESULT',root=source/'runtime/executions')
    if not phase:pytest.skip('Existing original RESULT archive is not materialized')
    shutil.copytree(source/'runtime/executions'/eid/'RESULT',root/'runtime/executions'/eid/'RESULT')
    final=json.loads((root/paths['final']).read_text());result=json.loads((root/paths['result']).read_text())
    authority=final['final_prediction_package']['execution_stage_manifest']['SIGNED_SOURCE_RECEIPT_VERIFIED']['current_authority_manifest']
    profile='profiles/'+authority.replace('-','_')+'.json'
    contract=json.loads((source/profile).read_text())['common_family_components']['family_runtime_contracts_profile']
    for p in ('evidence/jra_bvi_phase3_20261017/runtime_health.json',profile,contract):
        target=root/p;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source/p,target)
    env=json.loads((phase['run_dir']/'result_receipt_envelope.json').read_text())
    report={'profile':'UNSIGNED_REFERENCE_NOT_A_TRUST_ROOT','rows':[{
        'race_id':rid,'result_request_sha256':digest(result),
        'result_receipt_sha256':env['receipt_sha256'],
        # These flags must have no effect on actual local cryptographic checks.
        'result_signature_verified':False,'final_signature_verified':False}],
        'input_manifest':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths.values()}}
    report_path=root/'runtime/jra_race_day_status/2026-10-31.result-verification.json'
    report_path.parent.mkdir(parents=True,exist_ok=True);report_path.write_text(json.dumps(report))
    return rid,paths,report,report_path,final,result


def _referenced_original_proof(root, case):
    from jra_race_day_autopilot import _load_result_verification_report
    rid,paths,report,path,final,result=case
    return _post_result_evidence(root,rid,[rid+'-LIVE-R1'],final=final,result=result,
        verification_report=_load_result_verification_report(root,'2026-10-31'))


def test_referenced_original_receipts_verify_locally_without_trusting_audit_booleans(tmp_path):
    case=_original_signature_reference(tmp_path)
    proof=_referenced_original_proof(tmp_path,case)
    receipt=proof['signature_verification_receipt']
    assert proof['signature_validation_performed'] is True
    assert proof['signed_result_final_verified'] is True
    assert receipt['result_signature_verified'] and receipt['final_signature_verified']
    assert receipt['settlement_old_fields_exact'] and receipt['review_exact_rebuild'] and receipt['learning_state_exact_rebuild']
    assert receipt['source_report_is_trust_root'] is False
    assert receipt['envelope_reference_byte_identity']=='UNKNOWN'
    assert receipt['production_numeric_learning_consumption']=='NOT_ESTABLISHED'
    assert proof['learning']['consumption']=='NOT_ESTABLISHED_BY_STORAGE'
    assert proof['production_closed_loop_claim']=='NOT_ESTABLISHED_BY_STORAGE_AUDIT'


def test_valid_originals_still_default_to_storage_only_without_opt_in_report(tmp_path):
    case=_original_signature_reference(tmp_path)
    rid,paths,report,path,final,result=case
    path.unlink()
    proof=_post_result_evidence(tmp_path,rid,[rid+'-LIVE-R1'],final=final,result=result)
    assert proof['signature_validation_performed'] is False
    assert 'signature_verification_receipt' not in proof


def test_day_writer_verifies_complete_stored_checkpoint_without_report(tmp_path):
    import base64
    from execution_store import persist_phase, resolve_phase
    rid,paths,report,report_path,final,result=_original_signature_reference(tmp_path,'KM-JRA-FKS-20261107-R01')
    report_path.unlink()
    executions=tmp_path/'runtime/executions'
    current=resolve_phase(rid+'-LIVE-R1','RESULT',root=executions)
    inputs=[tmp_path/path for path in paths.values()]
    originals={path:path.read_bytes() for path in inputs}

    def render():
        return write_status(tmp_path,'2026-11-07',dt.datetime(2026,11,7,11,tzinfo=JST),
            {rid:{}},{},formal_runs=[],resolver_runs=[],source_runs=[])

    verified=render()
    assert verified['post_result_metrics']['signed_result_final_verified']==1
    evidence=verified['races'][0]['post_result_evidence']
    assert evidence['signature_verification_receipt']['source_report_path'].endswith('/manifest.json')
    assert evidence['signature_verification_receipt']['envelope_reference_byte_identity']=='MATCH'
    assert evidence['learning']['consumption']=='NOT_ESTABLISHED_BY_STORAGE'
    assert all(path.read_bytes()==raw for path,raw in originals.items())

    stage=tmp_path/'bad-signature'
    stage.mkdir()
    envelope=json.loads((current['run_dir']/'result_receipt_envelope.json').read_bytes())
    signature=bytearray(base64.b64decode(envelope['signature']))
    signature[0]^=1
    envelope['signature']=base64.b64encode(signature).decode()
    (stage/'result_receipt_envelope.json').write_text(json.dumps(envelope))
    (stage/'result_request.json').write_bytes((current['run_dir']/'result_request.json').read_bytes())
    persist_phase(rid+'-LIVE-R1','RESULT','tampered-test-only',stage,root=executions,github_sha='d'*40)
    rejected=render()['post_result_metrics']
    assert rejected['signature_verification_failed']==1 and rejected['signed_result_final_verified']==0
    assert rejected['signature_validation_performed'] is False


def test_referenced_tampering_cannot_be_authorized_by_unsigned_report(tmp_path):
    import base64,hashlib,pytest
    from execution_store import persist_phase,resolve_phase
    from post_result_learning import _sha
    from jra_presentation import digest
    for kind in ('signature','final','result','review','learning'):
        root=tmp_path/kind;case=_original_signature_reference(root)
        rid,paths,report,path,final,result=case
        if kind=='signature':
            phase=resolve_phase(rid+'-LIVE-R1','RESULT',root=root/'runtime/executions')
            envelope=json.loads((phase['run_dir']/'result_receipt_envelope.json').read_text())
            raw=bytearray(base64.b64decode(envelope['signature']));raw[0]^=1
            envelope['signature']=base64.b64encode(raw).decode()
            stage=root/'test-stage';stage.mkdir();(stage/'result_receipt_envelope.json').write_text(json.dumps(envelope))
            persist_phase(rid+'-LIVE-R1','RESULT','tampered-test-only',stage,
                root=root/'runtime/executions',github_sha='d'*40)
        else:
            value=json.loads((root/paths[kind]).read_text())
            if kind=='final':value['sha256']='0'*64;final=value
            elif kind=='result':value['settlement']['total_payout']+=100;result=value
            elif kind=='review':value['capital']['investment']+=100
            else:value['production_change_authorized']=True
            if kind in ('review','learning'):value['sha256']=_sha({k:v for k,v in value.items() if k!='sha256'})
            (root/paths[kind]).write_text(json.dumps(value))
            # Even a newly rehashed unsigned report cannot authorize changed data.
            report['input_manifest'][paths[kind]]=hashlib.sha256((root/paths[kind]).read_bytes()).hexdigest()
            if kind=='result':report['rows'][0]['result_request_sha256']=digest(result)
            case=(rid,paths,report,path,final,result)
        report['rows'][0].update(result_signature_verified=True,final_signature_verified=True)
        path.write_text(json.dumps(report))
        proof=_referenced_original_proof(root,case)
        verified=proof['signature_verification_receipt']
        assert proof.get('signed_result_final_verified') is False,kind
        assert verified['status']=='FAILED',(kind,verified)
        assert verified['performed'] is True,kind
        # The nested receipt preserves an attempted verification. The public
        # completion flag requires successful verification, never an attempt.
        assert proof['signature_validation_performed'] is False,kind
        assert verified['first_blocker'],kind
        assert proof['production_closed_loop_claim']=='NOT_ESTABLISHED_BY_STORAGE_AUDIT'


def test_day_metrics_include_actual_verification_scope_and_keep_unexecuted_races(tmp_path):
    rid,paths,report,path,final,result=_original_signature_reference(tmp_path)
    other='KM-JRA-TKY-20261031-R06'
    idx=write_status(tmp_path,'2026-10-31',dt.datetime(2026,11,1,9,tzinfo=JST),
                     {rid:{},other:{}},{},formal_runs=[],resolver_runs=[],source_runs=[])
    metrics=idx['post_result_metrics']
    assert metrics['race_denominator']==2 and metrics['signed_result_final_verified']==1
    assert metrics['signature_validation_performed'] is True
    assert metrics['signature_verification_failed']==metrics['signature_verification_blocked']==0
    assert metrics['verification_report']['path'].endswith('.result-verification.json')
    assert metrics['production_closed_loop_claim']=='NOT_ESTABLISHED_BY_STORAGE_AUDIT'
    assert next(r for r in idx['races'] if r['race_id']==other).get('post_result_evidence') is None


def test_missing_archived_key_or_receipt_never_promotes_reference_only_flags(tmp_path):
    case=_original_signature_reference(tmp_path)
    (tmp_path/'evidence/jra_bvi_phase3_20261017/runtime_health.json').unlink()
    proof=_referenced_original_proof(tmp_path,case)
    assert proof['signature_validation_performed'] is False
    assert proof['signature_verification_receipt']['status']=='BLOCKED'
    assert proof['signed_result_final_verified'] is False


def test_unreadable_optional_audit_does_not_interrupt_storage_status(tmp_path,monkeypatch):
    rid,final,result,review,learning=_stored_result(tmp_path)
    path=tmp_path/'runtime/jra_race_day_status/2026-10-24.result-verification.json'
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text('{}')
    original=Path.read_bytes
    def read(selected):
        if selected==path:raise PermissionError('optional proof unavailable')
        return original(selected)
    monkeypatch.setattr(Path,'read_bytes',read)
    idx=write_status(tmp_path,'2026-10-24',dt.datetime(2026,10,24,20,tzinfo=JST),
                     {rid:{}},{},formal_runs=[],resolver_runs=[],source_runs=[])
    assert idx['races'][0]['display_state']=='RESULT_REVIEW_LEARNING_STORED'
    assert idx['post_result_metrics']['signature_validation_performed'] is False
    assert idx['post_result_metrics']['signed_result_final_verified']==0
    assert 'PermissionError' in idx['post_result_metrics']['verification_report']['error']


def test_stale_parsed_bodies_and_receipt_cannot_bind_new_file_hashes(tmp_path):
    import base64,hashlib
    from execution_store import resolve_phase
    from jra_race_day_autopilot import _load_result_verification_report,_result_signature_readback
    for kind in ('final','result','review','learning','receipt'):
        root=tmp_path/kind;case=_original_signature_reference(root)
        rid,paths,report,path,final,result=case
        review=json.loads((root/paths['review']).read_text());learning=json.loads((root/paths['learning']).read_text())
        phase=resolve_phase(rid+'-LIVE-R1','RESULT',root=root/'runtime/executions')
        envelope_path=phase['run_dir']/'result_receipt_envelope.json'
        envelope=json.loads(envelope_path.read_text())
        selected=envelope_path if kind=='receipt' else root/paths[kind]
        value=json.loads(selected.read_text())
        if kind=='receipt':value['signature']='changed-after-parse'
        elif kind=='final':value['sha256']='0'*64
        elif kind=='result':value['settlement']['total_payout']+=100
        elif kind=='review':value['capital']['investment']+=100
        else:value['production_change_authorized']=True
        selected.write_text(json.dumps(value))
        if kind!='receipt':report['input_manifest'][paths[kind]]=hashlib.sha256(selected.read_bytes()).hexdigest()
        path.write_text(json.dumps(report))
        proof=_result_signature_readback(root,rid,final,result,envelope,envelope_path,
            review,learning,_load_result_verification_report(root,'2026-10-31'))
        assert proof['verified'] is False and proof['performed'] is False,kind
        assert proof['status']=='BLOCKED' and 'STALE_PARSED_BODY:'+kind in proof['first_blocker'],(kind,proof)


def test_original_bytes_changed_during_signature_verification_are_rejected(tmp_path,monkeypatch):
    import jra_delivery
    from execution_store import resolve_phase
    original_verify=jra_delivery.verify_signed_final
    for kind in ('final','result','review','learning','receipt'):
        root=tmp_path/kind;case=_original_signature_reference(root)
        rid,paths,report,path,final,result=case
        phase=resolve_phase(rid+'-LIVE-R1','RESULT',root=root/'runtime/executions')
        selected=(phase['run_dir']/'result_receipt_envelope.json') if kind=='receipt' else root/paths[kind]
        def verify_and_replace(*args,_selected=selected,**kwargs):
            checked=original_verify(*args,**kwargs)
            value=json.loads(_selected.read_text());value['changed_after_snapshot']=True
            _selected.write_text(json.dumps(value))
            return checked
        monkeypatch.setattr(jra_delivery,'verify_signed_final',verify_and_replace)
        proof=_referenced_original_proof(root,case)['signature_verification_receipt']
        assert proof['verified'] is False and proof['performed'] is True,kind
        assert proof['status']=='FAILED' and 'ORIGINAL_BYTES_CHANGED_DURING_VERIFICATION' in proof['first_blocker'],(kind,proof)


def test_declared_outer_envelope_hash_is_bound_even_when_inner_signature_is_valid(tmp_path):
    import hashlib
    from execution_store import persist_phase,resolve_phase
    from jra_presentation import archived_trust,_receipt
    case=_original_signature_reference(tmp_path)
    rid,paths,report,path,final,result=case
    phase=resolve_phase(rid+'-LIVE-R1','RESULT',root=tmp_path/'runtime/executions')
    original_path=phase['run_dir']/'result_receipt_envelope.json'
    reference_path=original_path.relative_to(tmp_path).as_posix()
    report['rows'][0]['result_receipt_path']=reference_path
    report['input_manifest'][reference_path]=hashlib.sha256(original_path.read_bytes()).hexdigest()
    path.write_text(json.dumps(report))
    proof=_referenced_original_proof(tmp_path,case)['signature_verification_receipt']
    assert proof['verified'] and proof['envelope_reference_byte_identity']=='MATCH'
    envelope=json.loads(original_path.read_text());envelope['additional_outer_metadata']='not-in-original-audit'
    # No new signature: the original inner receipt still verifies unchanged.
    health,_=archived_trust(final,root=tmp_path)
    assert _receipt(envelope,health['receipt_signer'],rid,'RESULT')['signature_verified'] is True
    stage=tmp_path/'changed-outer-stage';stage.mkdir()
    (stage/'result_receipt_envelope.json').write_text(json.dumps(envelope))
    persist_phase(rid+'-LIVE-R1','RESULT','changed-outer-test-only',stage,
        root=tmp_path/'runtime/executions',github_sha='d'*40)
    proof=_referenced_original_proof(tmp_path,case)['signature_verification_receipt']
    assert proof['verified'] is False and proof['performed'] is False
    assert 'AUDIT_ORIGINAL_RECEIPT_FILE_MISMATCH' in proof['first_blocker']

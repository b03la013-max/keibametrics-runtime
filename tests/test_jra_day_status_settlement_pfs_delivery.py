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
    expected_receipts=int(os.environ.get('KM_STATUS_EXPECTED_RECEIPTS','20'))
    assert len(rows)==36 and len(finals)==33
    assert Counter(r['state'] for r in rows)=={
        'SETTLED_SIGNED_RESULT_LEARNED':expected_learning,'SETTLED':33-expected_learning,'AKI_NO_BET':3}
    proof=[r['post_result_evidence'] for r in rows]
    assert sum(p['review_learning_bound'] for p in proof)==expected_learning
    assert sum(p['zero_exposure_result_learning_bound'] for p in proof)==3
    assert sum(any(x.get('request_payload_bound') for x in p['stored_result_receipts']) for p in proof)==expected_receipts
    assert all(p['signature_validation_performed'] is False for p in proof)
    assert all(p.read_bytes()==body for p,body in finals.items())

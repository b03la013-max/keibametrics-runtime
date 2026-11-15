"""Synthetic future permission tests; no real Owner approval or SOURCE grant."""
from copy import deepcopy
from datetime import datetime,timezone
import json

import pytest

from runtime import local_fnb_selection_study as study
from tests.test_local_fnb_semantic_closure import fixture,NOW,seal


def inputs():
    prediction=fixture()
    prediction['race_id']='KM-LOCAL-FNB-20261103-R01-SYNTHETIC-STUDY'
    seal(prediction)
    request={'race_id':prediction['race_id'],'family_id':'LOCAL','venue_id':'FNB',
        'prediction_cutoff':'2026-11-03T06:00:00+00:00',
        'scheduled_post_at':'2026-11-03T06:05:00+00:00'}
    decision={'profile':study.DECISION_PROFILE,
        'decision':'APPROVED_BOUNDED_PRIVATE_FUTURE_PAPER_STUDY','scope':study.SCOPE,
        'race_id':prediction['race_id'],'max_races':1,'max_new_krs_starts':0,
        'authorization_observed_at':'2026-11-03T03:00:00+00:00',
        'effective_from':'2026-11-03T03:00:00+00:00',
        'effective_until':request['prediction_cutoff'],'code_and_profile_pins':study.required_pins(),
        'authority_evidence':{'type':'DIRECT_USER_INSTRUCTION_IN_CURRENT_CHAT',
            'request_id':'SYNTHETIC_ONLY','approval_ref':'SYNTHETIC_NOT_REAL_APPROVAL',
            'owner_identity_confirmed_by_direct_instruction':True,'record_is_crypto_signature':False}}
    for k in ('production_adoption','original_strict_mec_changed','source_scope_changed',
        'registered_oos_authorized','actual_purchase_authorized','paid_resources_authorized'):
        decision[k]=False
    return decision,request,prediction


def test_pending_exact_decision_holds_without_creating_execution_store(tmp_path,monkeypatch):
    decision,request,prediction=inputs();decision['decision']='PENDING_OWNER_DECISION'
    d=study.private.encoded(decision);p=study.private.encoded(prediction)
    dp=tmp_path/'pending.json';pp=tmp_path/'prediction.json';dp.write_bytes(d);pp.write_bytes(p)
    root=tmp_path/'not-created'
    with pytest.raises(ValueError,match='OWNER_DECISION_PENDING'):
        study.run_study(decision_path=dp,decision_sha256=study.private.digest(d),
            prediction_path=pp,prediction_sha256=study.private.digest(p),request=request,private_root=root)
    assert not root.exists()


@pytest.mark.parametrize('mutate',[
    lambda d:d.update(max_races=2),lambda d:d.update(max_new_krs_starts=1),
    lambda d:d.update(production_adoption=True),lambda d:d.update(actual_purchase_authorized=True),
    lambda d:d['code_and_profile_pins'].update({'runtime/minimum_efficient_coverage.py':'f'*64}),
    lambda d:d['code_and_profile_pins'].update({'runtime/capital_policy.py':'f'*64}),
    lambda d:d['code_and_profile_pins'].update({'runtime/jra_ticket_tree_renderer.py':'f'*64}),
    lambda d:d['code_and_profile_pins'].update({'profiles/family_user_capital_default_20261003_R1.json':'f'*64}),
    lambda d:d.update(race_id='OTHER_RACE'),
])
def test_future_study_cannot_expand_owner_scope_or_change_exact_policy_pins(mutate,monkeypatch):
    decision,request,prediction=inputs();mutate(decision)
    monkeypatch.setattr(study,'_now',lambda:datetime.fromisoformat(NOW))
    with pytest.raises(ValueError,match='SCOPE_OR_PINS_MISMATCH'):
        study.verify_decision(decision,request=request,prediction=prediction)


def test_existing_r12_prediction_cannot_be_promoted_after_later_selection_approval(monkeypatch):
    decision,request,prediction=inputs()
    decision.update(authorization_observed_at='2026-11-03T04:30:00+00:00',
        effective_from='2026-11-03T04:30:00+00:00')
    monkeypatch.setattr(study,'_now',lambda:datetime.fromisoformat(NOW))
    with pytest.raises(ValueError,match='NO_RETROACTIVE_PROMOTION'):
        study.verify_decision(decision,request=request,prediction=prediction)


def test_one_immutable_future_study_slot_reuses_saved_original_but_rejects_new_revision(tmp_path,monkeypatch):
    decision,request,prediction=inputs()
    monkeypatch.setattr(study,'_now',lambda:datetime.fromisoformat(NOW))
    dp=tmp_path/'decision.json';pp=tmp_path/'prediction.json'
    d=study.private.encoded(decision);p=study.private.encoded(prediction)
    dp.write_bytes(d);pp.write_bytes(p)
    kwargs={'decision_path':dp,'decision_sha256':study.private.digest(d),
        'prediction_path':pp,'prediction_sha256':study.private.digest(p),
        'request':request,'private_root':tmp_path/'private'}
    out=study.run_study(**kwargs)
    assert out['new_krs_executions']==0 and out['actual_purchase'] is False
    assert out['production_policy_adopted'] is False and out['formal_final'] is False
    assert study.run_study(**kwargs)['completion_reused'] is True
    # Different whitespace is the same Owner instruction, not a fresh slot.
    reencoded=json.dumps(decision,separators=(',',':')).encode();dp.write_bytes(reencoded)
    with pytest.raises(ValueError,match='ONE_RACE_SLOT_ALREADY_USED'):
        study.run_study(**{**kwargs,'decision_sha256':study.private.digest(reencoded)})
    dp.write_bytes(d)
    changed=deepcopy(prediction);changed['freeze_at']='2026-11-03T04:00:30+00:00';seal(changed)
    p2=study.private.encoded(changed);pp.write_bytes(p2)
    with pytest.raises(ValueError,match='ONE_RACE_SLOT_ALREADY_USED'):
        study.run_study(**{**kwargs,'prediction_sha256':study.private.digest(p2)})


def test_expired_window_cannot_dispatch_study(monkeypatch):
    decision,request,prediction=inputs()
    monkeypatch.setattr(study,'_now',lambda:datetime.fromisoformat('2026-11-03T06:01:00+00:00'))
    with pytest.raises(ValueError,match='NO_RETROACTIVE_PROMOTION'):
        study.verify_decision(decision,request=request,prediction=prediction)


def test_stake_budget_and_renderer_dependencies_are_part_of_exact_owner_pins():
    assert {'runtime/capital_policy.py','runtime/jra_ticket_tree_renderer.py',
        'profiles/family_user_capital_default_20261003_R1.json',
        'runtime/local_fnb_research_runtime.py'} <= set(study.required_pins())

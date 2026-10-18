"""Actual historical URW SOURCE contract replay; never forward OOS evidence.

Original artifact10743349134 / Run35838350855. Negative mutations below are
unsigned test cases, never claimed to be new Runtime-signed observations.
"""
import base64
import copy
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import sys

# The reused numerical modules retain their existing runtime-local imports.
# Make this test independently collectable, not dependent on another test
# importing the orchestrator first or on an interactive PYTHONPATH setting.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'runtime'))

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
import pytest

from runtime.local_fullnumerical_production import materialize_production
from runtime.local_numerical_authority_gate import assess
from runtime.local_race_key_shadow_owner import (
    compile_urw_candidate, ShadowOwnerError, _sha, _urw_scenario_prediction,
    audit_urw_candidate_paper_pipeline,
)

ROOT = Path(__file__).resolve().parents[1]
PUBKEY = 'jqWqOYlmhXXmpv/nR7lx3c2n/S5shDYava/WJVxn4kE='
NOW = datetime(2026, 10, 18, 11, 20, tzinfo=timezone.utc)


@pytest.fixture(scope='module')
def original():
    raw = gzip.decompress((ROOT/'tests/fixtures/urw_20260923_r12_source.json.gz').read_bytes())
    assert hashlib.sha256(raw).hexdigest() == '5e5c91f37ec1636d36f1a497231c829bf672e53a868172b1d72c5ac7b857331c'
    source = json.loads(raw)
    req = {'family_id':'LOCAL','race_id':'URW-20260923-R12-FORMAL-R1',
           'execution_id':'URW-20260923-R12-FORMAL-R1','venue_id':'URW',
           'race_date':'2026-09-23','race_no':12,
           'prediction_cutoff':'2026-09-23T19:27:00+09:00',
           'scheduled_post_at':'2026-09-23T19:30:00+09:00'}
    numeric = materialize_production(source['artifact'], {
        **req,'runners':source['artifact']['official_runner_universe']['runners']}, assess()['required_indices'])
    return req, source, numeric


def test_real_source_crypto_and_full_29_materialization(original):
    req, s, n = original
    assert s['receipt_sha256'] == _sha(s['receipt'])
    assert s['receipt']['artifact_sha256'] == _sha(s['artifact'])
    assert s['signer_key_id'] == 'KM-LOCAL-RUNTIME-ED25519-20260922'
    # Trusted key pinned independently, not a self-asserted envelope key.
    Ed25519PublicKey.from_public_bytes(base64.b64decode(PUBKEY)).verify(
        base64.b64decode(s['signature']), json.dumps(s['receipt'],ensure_ascii=False,
            sort_keys=True,separators=(',',':')).encode())
    assert n['strict_full_numerical_ready'] is True
    cells = [c for r in n['runners'] for c in r['canonical_components'].values()]
    assert len(cells) == 348
    assert sum(c['terminal_status']=='CALCULATED' for c in cells) == 309
    assert sum(c['terminal_status']=='RULED-NEUTRAL' for c in cells) == 39
    assert not any(n['production_numerical_authority'][k] for k in (
        'prediction_consumption_authorized','krs_consumption_authorized',
        'ticket_consumption_authorized','capital_consumption_authorized'))


def test_urw_repeatable_roles_evidence_and_explicit_semantic_gaps(original):
    req, s, n = original
    before = copy.deepcopy(original)
    a = compile_urw_candidate(req,s,n,now=NOW,historical_replay=True)
    b = compile_urw_candidate(req,s,n,now=NOW,historical_replay=True)
    assert a == b and original == before
    assert len(a['ranking']) == len(set(a['ranking'])) == 12
    assert set(a['role_columns']) == set(a['ranking']) == set(a['runner_numeric_bindings'])
    assert a['numeric_cell_count'] == 348
    assert all(x['head'] != x['second'] for x in a['head_local_pairs'])
    assert all(len({x['head'],x['second'],x['third']})==3 for x in a['pair_conditioned_thirds'])
    assert all(x['interaction_effect'].startswith('UNESTABLISHED') for x in a['pair_conditioned_thirds'])
    assert all(v['past_start_count'] <= 5 and v['current_gci'].startswith('UNKNOWN')
               for v in a['urw_evidence'].values())
    assert a['frozen_at'] is None and a['compiled_at'] == NOW.isoformat()
    assert a['temporal_class'] == 'HISTORICAL_CONTRACT_REPLAY'
    assert a['forward_oos_credit'] == a['paper_ticket_count'] == a['paper_capital_yen'] == 0
    assert a['paper_tickets'] == []
    assert all(a[k] is False for k in ('formal_handoff_allowed','production_authority',
        'signed_final_claim','prediction_consumption_authorized','kaw_owner_reused',
        'krs_numeric_consumption','capital_policy_changed','actual_purchase'))
    # Request-owned ranks/results/weights/budget are not research-model inputs.
    contaminated = {**req,'ranking':['12'],'result':[12,9,7], 'weights':{'W':999},
                    'capital_policy':{'budget':1000000}}
    assert compile_urw_candidate(contaminated,s,n,now=NOW,historical_replay=True) == a


def test_current_condition_translation_has_source_binding_without_role_or_weight_promotion(original):
    req,s,n=original
    c=compile_urw_candidate(req,s,n,now=NOW,historical_replay=True)
    for evidence in c['urw_evidence'].values():
        t=evidence['current_condition_translation']
        assert t['source_id'] and t['source_snapshot_sha256'] and t['effective_time']
        if t['current_frame_no'] is None:
            assert t['current_frame_status']=='UNKNOWN_NOT_IN_PARSED_SOURCE'
        else:
            assert type(t['current_frame_no']) is int and 1<=t['current_frame_no']<=8
        assert not t['role_adjustments_applied']
        assert all(x['new_score_adjustment'] is None for x in t['observations'])
    assert c['ranking']==c['existing_local_baseline']['ranking']
    assert c['role_columns']==c['existing_local_baseline']['roles']


def test_shortening_and_place_only_never_become_automatic_winner_evidence():
    from runtime.local_race_key_shadow_owner import _urw_current_condition_translation as translate
    header={'distance':1400,'class_tokens':['C1'],'going':'良'}
    obs={'date':'2026-10-01','distance':1500,'venue':'浦和','finish':2,
         'positions':[1,1,2,2],'surface':'DIRT','class_tokens':['C1'],
         'going':'良','matched_urw_distance':False}
    t=translate({'frame_no':1},[obs],header)['observations'][0]
    assert t['distance_relation']=='SHORTENING' and t['distance_delta_m']==-100
    assert t['new_score_adjustment'] is None and t['current_survival_effect']=='UNKNOWN'
    same={**obs,'distance':1400,'matched_urw_distance':True}
    place=translate({},[same],header)['observations'][0]
    assert place['winner_evidence_class']=='PLACE_ONLY_NOT_DIRECT_WINNER'
    winner=translate({},[{**same,'finish':1}],header)['observations'][0]
    assert winner['winner_evidence_class']=='DIRECT_WIN_OBSERVATION_CURRENT_EFFECT_UNCALIBRATED'
    assert place['corner_rank_changes']==[0,-1,0]


def test_index_consumption_audit_separates_display_from_score_dependence(original):
    from scripts.urw_candidate_krs_replay import audit_index_consumption
    _,_,n=original
    small=copy.deepcopy(n);small['runners']=small['runners'][:2]
    original_bytes=_sha(small)
    audit=audit_index_consumption(small)
    assert _sha(small)==original_bytes
    assert audit['index_count']==29 and not audit['production_consumption_authorized']
    by_index={x['index']:x for x in audit['indices']}
    assert by_index['ZAI-WIN']['candidate_score_dependence']
    assert not by_index['BVIg-L']['candidate_score_dependence']
    assert len(by_index['BVIg-L']['cells'])==2 and audit['runtime_post_count']==0
    assert all(c['cell_sha256'] for x in audit['indices'] for c in x['cells'])


@pytest.mark.parametrize('target',[
    'FOREIGN_VENUE','WRONG_RACE','UNSIGNED','ARTIFACT_TAMPER','RECEIPT_TAMPER',
    'BAD_POST','MISSING_INDEX','WRONG_INDEX','BOOLEAN','NAN','INFINITY','MISSING_PROVENANCE',
    'UNKNOWN_CELL','STALE_NUMERIC_HASH','DUPLICATE_RUNNER','MISSING_ACTIVE','PROMOTED_CONSUMER',
    'DUPLICATE_DECLARED','DUPLICATE_OFFICIAL','UNEXPLAINED_STATUS','FOREIGN_CARD','BAD_RAW',
    'FOREIGN_NUMERIC_RACE','FOREIGN_NUMERIC_SOURCE',
])
def test_contract_mutations_fail_closed(original,target):
    req,s,n = copy.deepcopy(original)
    cc = n['runners'][0]['canonical_components']
    key = next(iter(cc))
    if target=='FOREIGN_VENUE': req['venue_id']='KAW'
    if target=='WRONG_RACE': req['race_id']='OTHER'
    if target=='UNSIGNED': s.pop('signature')
    if target=='ARTIFACT_TAMPER': s['artifact']['formal_ready']=False
    if target=='RECEIPT_TAMPER': s['receipt']['timestamp']='2026-09-23T10:29:00+00:00'
    if target=='BAD_POST': req['scheduled_post_at']='2026-09-23T19:26:00+09:00'
    if target=='MISSING_INDEX': cc.pop(key)
    if target=='WRONG_INDEX': n['required_indices'][0]='NOT_REGISTERED'
    if target=='BOOLEAN': cc[key]['value']=True
    if target=='NAN': cc[key]['value']=float('nan')
    if target=='INFINITY': cc[key]['value']=float('inf')
    if target=='MISSING_PROVENANCE': cc[key]['source_fact']=None
    if target=='UNKNOWN_CELL': cc[key]['terminal_status']='UNRESOLVED'
    if target=='STALE_NUMERIC_HASH': cc[key]['value'] += .01
    if target=='DUPLICATE_RUNNER': n['runners'].append(copy.deepcopy(n['runners'][0]))
    if target=='MISSING_ACTIVE': n['runners'].pop()
    if target=='PROMOTED_CONSUMER': n['production_numerical_authority']['krs_consumption_authorized']=True
    if target=='FOREIGN_NUMERIC_RACE': n['race_id']='OTHER'
    if target=='FOREIGN_NUMERIC_SOURCE': n['production_evidence_compiler']['source_snapshot_sha256']='OTHER'
    # Recompute ordinary hashes only to reach inner shape checks. Signatures are
    # deliberately not recreated; these are negative parser unit cases only.
    a=s['artifact']
    if target=='DUPLICATE_DECLARED': a['declared_runner_universe']['runners'].append(copy.deepcopy(a['declared_runner_universe']['runners'][0]))
    if target=='DUPLICATE_OFFICIAL': a['official_runner_universe']['runners'].append(copy.deepcopy(a['official_runner_universe']['runners'][0]))
    if target=='UNEXPLAINED_STATUS': a['runner_status_registry'][0]['status']='UNKNOWN'
    card=next(x for x in a['sources'] if x.get('source_class')=='OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT')
    if target=='FOREIGN_CARD': card['final_url']=card['final_url'].replace('k_babaCode=18','k_babaCode=21')
    if target=='BAD_RAW': card['raw_gzip_b64']='invalid'
    if target in {'DUPLICATE_DECLARED','DUPLICATE_OFFICIAL','UNEXPLAINED_STATUS','FOREIGN_CARD','BAD_RAW'}:
        s['receipt']['artifact_sha256']=_sha(a)
        s['receipt_sha256']=_sha(s['receipt'])
    with pytest.raises(ShadowOwnerError):
        compile_urw_candidate(req,s,n,now=NOW,historical_replay=True)


def test_expired_or_backdated_clock_never_becomes_new_prestart_freeze(original):
    req,s,n=original
    with pytest.raises(ShadowOwnerError,match='CUTOFF_EXPIRED'):
        compile_urw_candidate(req,s,n,now=NOW)
    with pytest.raises(ShadowOwnerError,match='SOURCE_TIME_BINDING'):
        compile_urw_candidate(req,s,n,now=datetime(2026,9,22,tzinfo=timezone.utc))


def test_kaw_production_owner_still_rejects_urw(original):
    from runtime.local_production_static_owner import build_formal_static, StaticOwnerError
    req,s,n=original
    policy=json.loads((ROOT/'profiles/local_production_static_owner_20261014_v1.json').read_text())
    with pytest.raises(StaticOwnerError):
        build_formal_static(req,s,n,policy=policy,now=datetime(2026,9,23,10,20,tzinfo=timezone.utc))


def test_entry_selects_urw_candidate_without_formal_or_external_request(original,monkeypatch,tmp_path):
    from runtime import local_race_entry as e
    req,s,n=copy.deepcopy(original)
    o=e.o
    monkeypatch.setattr(o,'ROOT',tmp_path)
    monkeypatch.setattr(o,'validate_request_context',lambda *a:None)
    monkeypatch.setattr(o,'resolve_phase',lambda *a:{'run_dir':tmp_path})
    monkeypatch.setattr(o,'validate_source_checkpoint',lambda *a:None)
    monkeypatch.setattr(o,'_load_checkpoint_json',lambda *a:s)
    monkeypatch.setattr(o,'check_deadline',lambda *a,**k:None)
    phases=[]
    def source_only(r,**kwargs):
        phases.append(r['execution_phase'])
        assert r['execution_phase']=='SOURCE' and r['analysis_only'] is True
        return {'status':'SOURCE_PASS'}
    monkeypatch.setattr(o,'orchestrate',source_only)
    monkeypatch.setattr(e,'assess',lambda:{'status':'READY','required_indices':n['required_indices']})
    monkeypatch.setattr(e,'materialize_production',lambda *a:n)
    monkeypatch.setattr(e,'resolve_static_input',lambda *a:(None,{'status':'NO_CANONICAL_STATIC'}))
    monkeypatch.setattr(e,'input_packet',lambda *a,**k:{})
    # Routing-only unit case: actual historical fixture remains a replay.
    monkeypatch.setattr(e,'compile_urw_candidate',lambda *a:compile_urw_candidate(*a,now=NOW,historical_replay=True))
    monkeypatch.setattr(e,'compile_shadow',lambda *a:pytest.fail('URW used generic paper tickets'))
    out=e.run(req,output=tmp_path/'out',run_id='test')
    assert out['status']=='HOLD' and out['formal_final_proven'] is False
    assert out['shadow_owner']['production_prediction_changed'] is False
    assert phases==['SOURCE']
    assert not (tmp_path/'runtime/formal_intents').exists()


def mechanism_fixture():
    """Synthetic geometry counterfactuals; NOT a signed SOURCE or accuracy test."""
    def observation(positions,finish=3):
        return {'date':'26.09.01','venue':'浦和','distance':1400,'going':'良','surface':'DIRT',
                'race_name':'Ｃ１一','class_tokens':['C1'],'field_size':8,'positions':positions,
                'finish':finish,'matched_urw_distance':True}
    paths = {'1':[observation([1,1,1,1],1),observation([2,2,2,1],1)],
             '2':[observation([2,2,2,2],1)],
             '3':[observation([2,2,2,2],2)],
             '4':[observation([3,3,3,3],2)],
             '5':[observation([4,4,4,4])],
             '6':[observation([5,5,5,5])],
             '7':[observation([3,3,3,3])],'8':[]}
    evidence = {rid:{'past_starts':obs} for rid,obs in paths.items()}
    baseline = {'ranking':list(paths),'W':['1','2'],'P2':['3','4','6'],
                'P3':['3','4','5','6','7','8'],
                'roles':{rid:[k for k,pool in [('W',['1','2']),('P2',['3','4','6']),
                    ('P3',['3','4','5','6','7','8'])] if rid in pool] for rid in paths}}
    header = {'distance':1400,'class_tokens':['C1'],'going':'良'}
    return evidence,baseline,header


def test_conditions_change_p2_and_residual_p3_evidence_not_just_exclusion():
    e,b,h=mechanism_fixture()
    q=_urw_scenario_prediction(e,b,header=h,field_size=8)
    a=q['head_local_p2']['1'];c=q['head_local_p2']['2']
    assert a['evaluations']['3']['supported_contexts']
    assert not c['evaluations']['3']['supported_contexts']  # Different HEAD geometry.
    assert ['4','3'] in a['partial_order_edges']  # No weighted sum; support inclusion.
    assert a['incomparable_groups'] != c['incomparable_groups']
    t=q['pair_conditioned_p3']
    assert t['1>3']['evaluations']['7']['supported_contexts']
    assert not t['1>4']['evaluations']['7']['supported_contexts']  # SECOND changes the residual.
    assert all(not x['hard_exclusion'] and not x['material_exact_evidence']
        for block in t.values() for x in block['evaluations'].values())
    assert q['baseline_roles_changed'] is False
    assert q['new_numerical_weights']=={} and q['calibrated_probabilities'] is False


def test_missing_evidence_is_incomparable_and_never_automatic_purchase():
    e,b,h=mechanism_fixture()
    q=_urw_scenario_prediction(e,b,header=h,field_size=8)
    for block in q['pair_conditioned_p3'].values():
        row=block['evaluations']['8']
        assert row['unknown_contexts'] and not row['hard_exclusion']
        assert '8' in block['incomparable_groups'][0]
        assert not any('8' in edge for edge in block['partial_order_edges'])
    assert q['unknown_role_alternatives']['8']==['W','P2','P3']
    assert q['unknown_role_alternatives_material'] is False


def test_stances_preserve_correlated_paths_and_acquisition_is_not_survival():
    e,b,h=mechanism_fixture()
    e['1']['past_starts']=[{**e['1']['past_starts'][0],'positions':[1,2,5,6],'finish':7},
                          {**e['1']['past_starts'][1],'positions':[4,4,2,1],'finish':1}]
    q=_urw_scenario_prediction(e,b,header=h,field_size=8)
    stances=q['runner_scenarios']['1']
    assert stances['PRESS']['projected_position_alternatives']==[{'C1':1,'C3':5,'C4':6}]
    assert stances['SIT']['projected_position_alternatives']==[{'C1':4,'C3':2,'C4':1}]
    assert {'C1':1,'C3':2,'C4':1} not in sum((s['projected_position_alternatives'] for s in stances.values()),[])
    survival=q['actor_evidence']['1']['lead_survival_observations'][0]
    assert survival['C4_lead_retained'] is False and survival['finish_lead_retained'] is False
    assert survival['straight_rank_change']==-1
    assert q['actor_evidence']['1']['current_survival_probability'] is None
    assert all(s['probability'] is None and s['new_score_adjustment'] is None for s in stances.values())


@pytest.mark.parametrize('target',['two_calls','foreign_course','different_field','different_class'])
def test_unknown_translation_never_becomes_context_matched_effect(target):
    e,b,h=mechanism_fixture()
    for row in e['3']['past_starts']:
        if target=='two_calls':row['positions']=[2,2]
        if target=='foreign_course':row.update(venue='川崎',matched_urw_distance=False)
        if target=='different_field':row['field_size']=10
        if target=='different_class':row['class_tokens']=['C2']
    q=_urw_scenario_prediction(e,b,header=h,field_size=8)
    row=q['head_local_p2']['1']['evaluations']['3']
    assert row['unknown_contexts'] and not row['matched_contexts']
    assert row['material_exact_evidence'] is False and row['hard_exclusion'] is False


def test_missing_past_win_does_not_delete_winner_hypotheses():
    e,b,h=mechanism_fixture()
    for row in e['1']['past_starts']:row['finish']=6
    q=_urw_scenario_prediction(e,b,header=h,field_size=8)
    assert q['head_local_p2']['1']['evaluations']['3']['supported_contexts']
    assert q['actor_evidence']['1']['baseline_roles_retained']==['W']


def test_pairwise_friction_has_directional_branches_and_no_invented_cost():
    e,b,h=mechanism_fixture();h['distance']=2000
    q=_urw_scenario_prediction(e,b,header=h,field_size=8)
    f=next(x for x in q['pairwise_friction'] if (x['a'],x['b'])==('1','2'))
    assert f['branches'][0]['evidence_status']=='OBSERVED_ANALOG_AVAILABLE'
    assert f['branches'][1]['evidence_status']=='UNKNOWN_NOT_IMPOSSIBLE'
    assert f['branches'][2]['duration']==f['branches'][2]['energy_cost']=='UNKNOWN'
    assert f['score_effect'].startswith('UNKNOWN') and not f['pair_exclusion_authority']


def test_real_source_candidate_krs_mec_capital_and_exact_plumbing_remain_paper(original):
    from runtime.formal_request_validator import (
        validate_numeric_input, validate_production_authority, FormalValidationError,
    )
    req,s,n=original
    frozen=compile_urw_candidate(req,s,n,now=NOW,historical_replay=True)
    before=copy.deepcopy(frozen)
    p=audit_urw_candidate_paper_pipeline(frozen,n)
    validate_numeric_input(p['candidate_krs_input'],[r['runner_id'] for r in n['runners']])
    native=p['candidate_krs_input']['race']
    assert native['prediction_id']==req['race_id']
    assert native['racecourse']=='浦和' and native['date']==req['race_date']
    assert native['race_no']==req['race_no']
    assert native['course_rule_version']==frozen['venue_canon']
    assert frozen['scheduled_post_at']==req['scheduled_post_at']
    assert p['candidate_krs_input']['keibametrics_input_authority']['production_authority'] is False
    assert p['mec_contract_result']['material_coverage_ratio']==1
    assert p['capital_contract_result']['decision']=='PAPER'
    assert p['capital_contract_result']['capital_limit']==0
    assert p['exact_materiality_inferred_from_geometry'] is False
    assert not any(t['bet_type']=='TRIFECTA' for t in p['mec_contract_result']['tickets'])
    key=next(iter(frozen['pair_conditioned_thirds']))
    triple=(key['head'],key['second'],key['third'])
    # Explicit hypothetical materiality tests Common Exact plumbing. It is NOT
    # inferred from this retrospective race, a recommendation or a signed FINAL.
    exact=audit_urw_candidate_paper_pipeline(frozen,n,research_exact_keys=[triple])
    tickets=exact['mec_contract_result']['tickets']
    assert any(t['bet_type']=='EXACTA' and tuple(map(str,t['selection']))==triple[:2] for t in tickets)
    assert any(t['bet_type']=='TRIFECTA' and tuple(map(str,t['selection']))==triple for t in tickets)
    assert exact['capital_contract_result']['decision']=='PAPER'
    assert exact['mec_contract_result']['minimum_required_capital']==p['mec_contract_result']['minimum_required_capital']+100
    assert frozen==before  # Paper/Capital/KRS never rewrite the Static freeze.
    assert not p['signed_final_claim'] and p['runtime_send_count']==0
    assert not p['prediction_quality_proven'] and p['forward_oos_credit']==0
    candidate_request={**p['semantic_request'],
        'base_index_mapping_authority':{'production_authority':True,'status':'PRODUCTION'}}
    with pytest.raises(FormalValidationError,match='NON_PRODUCTION_STATIC_PREDICTION_FORBIDDEN'):
        validate_production_authority(candidate_request)
    with pytest.raises(ShadowOwnerError,match='OUTSIDE_FROZEN_SEMANTICS'):
        audit_urw_candidate_paper_pipeline(frozen,n,research_exact_keys=[('1','1','1')])


@pytest.mark.parametrize('change',[
    {'race_date':'2026-09-24'}, {'race_date':None}, {'race_no':True},
    {'race_no':'12'}, {'race_no':0}, {'race_no':13},
])
def test_candidate_native_krs_identity_requires_official_calendar(original,change):
    req,s,n=original
    with pytest.raises(ShadowOwnerError,match='RACE_CALENDAR_IDENTITY'):
        compile_urw_candidate({**req,**change},s,n,now=NOW,historical_replay=True)


def test_krs_and_capital_inputs_cannot_backsolve_static_freeze(original):
    req,s,n=original
    a=compile_urw_candidate(req,s,n,now=NOW,historical_replay=True)
    injected={**req,'krs_output':{'SSR_W':{'12':100}},'budget':10000000,
              'scenario_weights':{'PRESS':1},'static_prediction':{'ranking':['12']}}
    b=compile_urw_candidate(injected,s,n,now=NOW,historical_replay=True)
    assert a==b
    assert a['urw_scenario_prediction']['krs_input_or_output_consumed'] is False
    assert a['urw_scenario_prediction']['krs_role_veto_allowed'] is False


def test_real_source_scenarios_and_pipeline_refuse_cross_source_numerics(original):
    req,s,n=original
    a=compile_urw_candidate(req,s,n,now=NOW,historical_replay=True)
    q=a['urw_scenario_prediction']
    assert q['header_context']['class_tokens']==['B3','C1']
    assert len(q['runner_scenarios'])==12 and len(q['pairwise_friction'])==66
    assert len(q['head_local_p2'])==6 and len(q['pair_conditioned_p3'])==48
    assert any(v['supported_contexts'] for block in q['pair_conditioned_p3'].values() for v in block['evaluations'].values())
    assert q['full_urw_model_complete'] is False
    wrong=copy.deepcopy(n);wrong['production_evidence_compiler']['source_snapshot_sha256']='other'
    with pytest.raises(ShadowOwnerError,match='NUMERICAL_BINDING'):
        audit_urw_candidate_paper_pipeline(a,wrong)


def test_injected_prestart_clock_never_claims_a_real_forward_freeze(original):
    req,s,n=original
    p=compile_urw_candidate(req,s,n,now=datetime(2026,9,23,10,20,tzinfo=timezone.utc))
    assert p['temporal_class']=='INJECTED_CLOCK_CONTRACT_TEST'
    assert p['frozen_at'] is None and p['forward_oos_credit']==0


def test_completion_crossing_cutoff_fails_even_when_started_in_time(original,monkeypatch):
    from runtime import local_race_key_shadow_owner as m
    class CrossingClock(datetime):
        calls=0
        @classmethod
        def now(cls,tz=None):
            cls.calls+=1
            return datetime(2026,9,23,10,20 if cls.calls==1 else 28,tzinfo=timezone.utc)
    monkeypatch.setattr(m,'datetime',CrossingClock)
    req,s,n=original
    with pytest.raises(ShadowOwnerError,match='COMPLETED_AFTER_CUTOFF'):
        m.compile_urw_candidate(req,s,n)


def test_real_local_freeze_uses_completion_clock_not_start(original,monkeypatch):
    from runtime import local_race_key_shadow_owner as m
    class AdvancingClock(datetime):
        calls=0
        @classmethod
        def now(cls,tz=None):
            cls.calls+=1
            return datetime(2026,9,23,10,20,cls.calls,tzinfo=timezone.utc)
    monkeypatch.setattr(m,'datetime',AdvancingClock)
    req,s,n=original
    p=m.compile_urw_candidate(req,s,n)
    assert p['compilation_started_at'].endswith('10:20:01+00:00')
    assert p['frozen_at']==p['compiled_at']=='2026-09-23T10:20:02+00:00'
    # This uses an internal monkeypatched clock only in the unit test, never
    # a persisted freeze, independently timestamped OOS record or live result.
    assert p['forward_oos_credit']==0 and p['signed_final_claim'] is False


def test_runtime_clock_regression_is_not_a_valid_freeze(original,monkeypatch):
    from runtime import local_race_key_shadow_owner as m
    class ReversingClock(datetime):
        calls=0
        @classmethod
        def now(cls,tz=None):
            cls.calls+=1
            return datetime(2026,9,23,10,20 if cls.calls==1 else 19,tzinfo=timezone.utc)
    monkeypatch.setattr(m,'datetime',ReversingClock)
    req,s,n=original
    with pytest.raises(ShadowOwnerError,match='CLOCK_REGRESSION'):
        m.compile_urw_candidate(req,s,n)

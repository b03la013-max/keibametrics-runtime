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
from runtime.local_race_key_shadow_owner import compile_urw_candidate, ShadowOwnerError, _sha

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

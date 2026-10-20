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
from urw_reference_fixture_support import fixture_root

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
    # Current UNKNOWN class handling cannot count the old implicit 52 as an
    # observed class. The original signed SOURCE bytes remain unchanged.
    assert sum(c['terminal_status']=='CALCULATED' for c in cells) == 285
    assert sum(c['terminal_status']=='RULED-NEUTRAL' for c in cells) == 63
    assert not any(n['production_numerical_authority'][k] for k in (
        'prediction_consumption_authorized','krs_consumption_authorized',
        'ticket_consumption_authorized','capital_consumption_authorized'))


def test_urw_numeric_entry_uses_real_official_distance_instead_of_zero(original):
    from runtime.local_production_static_owner import bind_urw_numerical_context
    req, source, prior = original
    before = copy.deepcopy((req, source, prior))
    bound = bind_urw_numerical_context(
        {**req, 'runners': source['artifact']['official_runner_universe']['runners']}, source['artifact'])
    assert bound['race']['distance'] == 2000
    assert bound['race']['surface'] == 'dirt'
    assert bound['race']['class'] == 'B3_C1'
    fixed = materialize_production(source['artifact'], bound, assess()['required_indices'])
    assert fixed['strict_full_numerical_ready'] is True
    assert fixed['numeric_coverage']['required_count'] == 348
    observed = [r for r in fixed['runners'] if not r['evidence_features']['same_distance']['missing']]
    assert observed, 'The actual card contains prior 2000m observations.'
    assert all('2000m' in r['evidence_features']['same_distance']['source_fact'] for r in fixed['runners'])
    for row in observed:
        starts = row['raw_candidate_evidence']['starts']
        matched = [r for r in starts if r.get('distance') == 2000 and r.get('field_size', 0) > 1]
        expected = sum(100 * (r['field_size'] - r['finish']) / (r['field_size'] - 1)
                       for r in matched) / len(matched)
        assert row['evidence_features']['same_distance']['score'] == pytest.approx(expected, abs=1e-6)
    assert bound['numerical_race_context_source']['source_snapshot_sha256'] == source['artifact']['source_snapshot_sha256']
    assert not any(fixed['production_numerical_authority'][k] for k in (
        'prediction_consumption_authorized', 'krs_consumption_authorized',
        'ticket_consumption_authorized', 'capital_consumption_authorized'))
    assert (req, source, prior) == before


def test_unresolved_urw_numeric_class_is_not_an_observed_numeric_class(original):
    from runtime.local_production_static_owner import bind_urw_numerical_context
    req, source, _ = original
    bound = bind_urw_numerical_context(
        {**req, 'runners': source['artifact']['official_runner_universe']['runners']}, source['artifact'])
    # Exercise missing input explicitly without changing the signed SOURCE.
    # The live entry above binds the real B3イC1ア header before calculation.
    bound['race']['class'] = 'UNKNOWN'
    fixed = materialize_production(source['artifact'], bound, assess()['required_indices'])
    for row in fixed['runners']:
        for name in ('current_class', 'race_set_level', 'class_change_pressure', 'transfer_class'):
            cell = row['evidence_features'][name]
            assert cell['missing'] is True and cell['coverage'] == 0
            assert cell['raw_metric'] is None


@pytest.mark.parametrize('field,value', [('distance', 1400), ('surface', 'turf'),
    ('class', 'A1'), ('venue_id', 'KAW'), ('race_date', '2026-09-24'), ('race_no', 11)])
def test_urw_source_context_cannot_be_overridden_by_request(original, field, value):
    from runtime.local_production_static_owner import bind_urw_numerical_context, StaticOwnerError
    req, source, _ = original
    with pytest.raises(StaticOwnerError, match='URW_NUMERICAL_RACE_CONTEXT_CONFLICT'):
        bind_urw_numerical_context({**req, 'race': {field: value}}, source['artifact'])


def test_urw_source_context_rejects_changed_source_without_mutating_it(original):
    from runtime.local_production_static_owner import bind_urw_numerical_context, StaticOwnerError
    req, source, _ = original
    changed = copy.deepcopy(source['artifact'])
    changed['normalized_evidence']['start_time']['value'] = '19:31'
    with pytest.raises(StaticOwnerError, match='URW_NUMERICAL_SOURCE_INVALID'):
        bind_urw_numerical_context(req, changed)
    with pytest.raises(StaticOwnerError, match='URW_NUMERICAL_SOURCE_RACE_MISMATCH'):
        bind_urw_numerical_context({**req, 'race_id': 'OTHER-RACE'}, source['artifact'])
    other = {'venue_id': 'KAW', 'race': {'distance': 1400}}
    assert bind_urw_numerical_context(other, {}) == other


@pytest.mark.parametrize('before,after', [
    ('2026年9月23日', '2026年9月24日'), ('浦 和', '川 崎'), ('第12競走', '第11競走')])
def test_urw_numeric_context_checks_card_body_beside_url(original, before, after):
    from runtime.local_production_static_owner import bind_urw_numerical_context, StaticOwnerError
    from runtime.local_physical.source_acquisition import sha_obj, verify_source_artifact
    import unicodedata
    req, envelope, _ = original
    # In-memory unsigned transport mutation, never a new signed SOURCE.
    source = copy.deepcopy(envelope['artifact'])
    card = next(s for s in source['sources']
                if s.get('source_class') == 'OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT')
    page = gzip.decompress(base64.b64decode(card['raw_gzip_b64'])).decode('utf-8')
    page = unicodedata.normalize('NFKC', page)
    assert before in page
    raw = page.replace(before, after).encode('utf-8')
    card['raw_gzip_b64'] = base64.b64encode(gzip.compress(raw, mtime=0)).decode()
    card['raw_sha256'] = hashlib.sha256(raw).hexdigest()
    card['snapshot_sha256'] = sha_obj({k:v for k,v in card.items() if k != 'snapshot_sha256'})
    source['source_snapshot_sha256'] = sha_obj({k:v for k,v in source.items() if k != 'source_snapshot_sha256'})
    assert verify_source_artifact(source) == (True, [])
    with pytest.raises(StaticOwnerError, match='URW_NUMERICAL_CARD_BODY_IDENTITY_MISMATCH'):
        bind_urw_numerical_context(req, source)


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


def test_conditional_features_never_score_ruled_neutral_as_weak(original):
    from runtime.local_race_key_shadow_owner import owner_feature_pack
    req,s,n=original;c=compile_urw_candidate(req,s,n,now=NOW,historical_replay=True)
    p=owner_feature_pack(c,n)
    for row in n['runners']:
        for name,cell in row['canonical_components'].items():
            value=p['runners'][str(row['runner_id'])]['INDEX:'+name]
            assert value==(None if cell['terminal_status']=='RULED-NEUTRAL' else cell['value'])
    changed=copy.deepcopy(n);changed['runners'][0]['canonical_components']['HPI-L']['value']+=1
    with pytest.raises(ShadowOwnerError,match='NUMERICAL_BINDING'):
        owner_feature_pack(c,changed)


def test_urw_transfer_keeps_recent_change_beside_old_direct_history(original):
    from runtime.local_race_key_shadow_owner import owner_feature_pack
    req,s,n=original;c=compile_urw_candidate(req,s,n,now=NOW,historical_replay=True)
    rid=c['ranking'][0];ev=c['urw_evidence'][rid]
    # Unsigned synthetic reproduction of the discarded-history bug. This is
    # neither an observed race nor a quality/Forward claim.
    ev['current_condition_translation'].update(current_distance_m=1400,current_frame_no=2)
    ev['past_starts']=[
        {'date':'26.09.20','distance':1600,'field_size':10,'finish':3,
         'positions':[7,6,5,4],'surface':'DIRT','matched_urw_distance':False},
        {'date':'26.09.01','distance':1400,'field_size':10,'finish':2,
         'positions':[1,1,1,2],'surface':'DIRT','matched_urw_distance':True},
    ]
    c['sha256']=_sha({k:v for k,v in c.items() if k!='sha256'})
    before=copy.deepcopy(c)
    old=owner_feature_pack(c,n);fixed=owner_feature_pack(c,n,urw_transfer=True)
    assert c==before and old['baseline']==fixed['baseline']
    assert old['runners'][rid]['STAGE:acquisition']==.1
    assert fixed['runners'][rid]['STAGE:acquisition']==pytest.approx(.4)
    assert old['runners'][rid]['STAGE:distance_delta']==0
    assert fixed['runners'][rid]['TRANSFER:latest_distance_delta']==-200
    assert fixed['runners'][rid]['STAGE:distance_delta']==-100
    # A two-call non-sprint record cannot provide the same four-corner path.
    ev['past_starts'][0]['positions']=[7,4]
    c['sha256']=_sha({k:v for k,v in c.items() if k!='sha256'})
    assert owner_feature_pack(c,n,urw_transfer=True)['runners'][rid]['STAGE:acquisition']==.1
    # 1400m acquisition is not transferable to an unobserved URW 800m start.
    ev['current_condition_translation']['current_distance_m']=800
    for start in ev['past_starts']:start['matched_urw_distance']=False
    c['sha256']=_sha({k:v for k,v in c.items() if k!='sha256'})
    assert owner_feature_pack(c,n,urw_transfer=True)['runners'][rid]['STAGE:acquisition'] is None


def test_urw_frame_recovery_uses_original_rowspan_without_changing_frozen_inputs(original):
    from runtime.local_race_key_shadow_owner import owner_feature_pack
    req,source,n=original;c=compile_urw_candidate(req,source,n,now=NOW,historical_replay=True)
    before=copy.deepcopy((c,source,n))
    old=owner_feature_pack(c,n,urw_transfer=True)
    fixed=owner_feature_pack(c,n,urw_transfer=True,source_artifact=source['artifact'])
    assert (c,source,n)==before
    expected={'6':5,'8':6,'10':7,'12':8}
    assert {rid:fixed['runners'][rid]['STAGE:frame'] for rid in expected}==expected
    assert all(old['runners'][rid]['STAGE:frame'] is None for rid in expected)
    assert sum(row['STAGE:frame'] is not None for row in fixed['runners'].values())==12
    assert fixed['source_frame_witness']['raw_sha256']=='440fabd78872b65b4d22098df66a490ed41429ffec8a0c588c1a0742d4174cdb'
    assert fixed['baseline']==old['baseline'] and fixed['production_authority'] is False
    # Existing v1 models and Production inputs keep their original semantics.
    with pytest.raises(ShadowOwnerError,match='FRAME_CANDIDATE_SOURCE_BINDING'):
        owner_feature_pack(c,n,source_artifact=source['artifact'])
    tampered=copy.deepcopy(source['artifact']);tampered['sources'][0]['raw_sha256']='0'*64
    with pytest.raises(ShadowOwnerError,match='FRAME_SOURCE_INTEGRITY'):
        owner_feature_pack(c,n,urw_transfer=True,source_artifact=tampered)


def test_public_urw_capture_is_pinned_unsigned_and_retains_partial_bytes(monkeypatch,tmp_path):
    import urllib.request
    import scripts.urw_candidate_krs_replay as replay
    from runtime import urw_reference_source_policy as policy
    from runtime.local_physical.source_acquisition import verify_source_artifact
    class Clock(datetime):
        @classmethod
        def now(cls,tz=None):return datetime(2026,10,19,2,0,tzinfo=timezone.utc)
    monkeypatch.setattr(replay,'datetime',Clock)
    tick=[0.0]
    monkeypatch.setattr(policy,'POLICY',policy.UrwReferenceSourcePolicy(tmp_path/'robots',
        clock=lambda:tick[0],sleep=lambda seconds:tick.__setitem__(0,tick[0]+seconds)))
    req={'venue_id':'URW','race_date':'2026-10-19','race_no':1,
         'race_id':'TEST-URW-PUBLIC','prediction_cutoff':'2026-10-19T12:18:00+09:00'}
    calls=[]
    class Response:
        status=200
        headers={'Content-Type':'text/html; charset=UTF-8'}
        def __init__(self,url):
            self.url=url
            if url==policy.ROBOTS_URL:self.headers={'Content-Type':'text/plain; charset=UTF-8'}
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def geturl(self):return self.url
        def read(self,limit):
            if self.url==policy.ROBOTS_URL:return b'User-agent: *\nAllow: /\nCrawl-delay: 10\n'
            return b'<table><tr><td>original official bytes</td></tr></table>'
    class Opener:
        fail_second=False
        def open(self,request,timeout):
            if request.full_url==policy.ROBOTS_URL:return Response(request.full_url)
            calls.append(request.full_url)
            assert request.method=='GET' and 'k_babaCode=18' in request.full_url
            if self.fail_second and len(calls)==2:raise OSError('TEST_SECOND_SOURCE_FAILURE')
            return Response(request.full_url)
    opener=Opener()
    def build(handler):
        with pytest.raises(ValueError,match='REDIRECT_FORBIDDEN'):
            handler.redirect_request(None,None,302,'',{},'https://evil.invalid/')
        return opener
    monkeypatch.setattr(urllib.request,'build_opener',build)
    artifact,errors=replay.capture_public_urw_sources(req)
    assert not errors and verify_source_artifact(artifact)[0]
    assert artifact['signed_source_claim'] is False and artifact['production_authority'] is False
    assert all(x['cutoff_relation']=='PRE_CUTOFF' for x in artifact['sources'])
    assert len(calls)==2 and artifact['source_fetch_execution']['redirects_allowed'] is False
    for bad in ({'venue_id':'KAW'},{'race_date':'2026-10-18'},{'race_no':True},
                {'prediction_cutoff':'2026-10-19T10:59:00+09:00'}):
        with pytest.raises(ValueError,match='SCOPE_OR_DEADLINE'):
            replay.capture_public_urw_sources({**req,**bad})
    calls.clear();opener.fail_second=True
    with pytest.raises(OSError,match='TEST_SECOND_SOURCE_FAILURE'):
        replay.capture_public_urw_sources(req,output=tmp_path/'partial')
    saved=list((tmp_path/'partial').glob('*.json'))
    assert len(saved)==1 and json.loads(saved[0].read_text())['http_status']==200


def test_reference_uses_real_raw_card_without_full29_or_production_owner(original):
    from datetime import timedelta
    from runtime.local_race_key_shadow_owner import compile_reference_prediction, render_reference_prediction
    from runtime.local_physical.source_acquisition import sha_obj
    req, envelope, _ = copy.deepcopy(original)
    # Explicit unsigned contract derivative. Original signed envelope is intact.
    source = envelope['artifact']
    source['scheduled_post_at'] = req['scheduled_post_at']
    source['source_race_context'] = {k: req[k] for k in ('venue_id', 'race_date', 'race_no')}
    source['source_snapshot_sha256'] = sha_obj({k:v for k,v in source.items() if k!='source_snapshot_sha256'})
    now = datetime.fromisoformat(req['prediction_cutoff'])-timedelta(seconds=1)
    prediction = compile_reference_prediction(req, source, now=now)
    assert len(prediction['runners']) == len(prediction['runner_display_order']) == 12
    assert set(prediction['ranking']) | set(prediction['unranked_condition_transfer']) == set(prediction['runner_display_order'])
    assert all(row['reference_rank'] is None for row in prediction['runners'] if not row['facts']['exact_races'])
    assert all(row['source_id'] and row['snapshot_sha256'] for row in prediction['runners'])
    assert prediction['formal_handoff_allowed'] is prediction['signed_final_claim'] is False
    assert prediction['numerical_prediction_consumption'] is prediction['krs_engine_executed'] is False
    assert prediction['canonical_tickets'] is prediction['stakes'] is None
    assert prediction['temporal_class'] == 'INJECTED_CLOCK_CONTRACT_TEST'
    assert 'NON-PRODUCTION / NON-FORMAL / REFERENCE ONLY' in render_reference_prediction(prediction)
    with pytest.raises(ShadowOwnerError, match='WINDOW_EXPIRED'):
        compile_reference_prediction(req, source, now=now+timedelta(seconds=2))
    source['sources'][0]['raw_sha256'] = '0'*64
    with pytest.raises(ShadowOwnerError, match='SOURCE_INTEGRITY'):
        compile_reference_prediction(req, source, now=now)


def test_reference_bootstrap_uses_actual_official_clock_and_optional_odds(monkeypatch, tmp_path):
    import urllib.request
    from scripts import urw_candidate_krs_replay as replay
    from runtime import urw_reference_source_policy as policy
    tick=[0.0]
    monkeypatch.setattr(policy,'POLICY',policy.UrwReferenceSourcePolicy(tmp_path/'robots',
        clock=lambda:tick[0],sleep=lambda seconds:tick.__setitem__(0,tick[0]+seconds)))
    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 10, 19, 4, tzinfo=timezone.utc)
    monkeypatch.setattr(replay, 'datetime', Clock)
    class Response:
        status = 200
        headers = {'Content-Type': 'text/html; charset=UTF-8'}
        def __init__(self, url):
            self.url = url
            if url==policy.ROBOTS_URL:self.headers={'Content-Type':'text/plain; charset=UTF-8'}
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def geturl(self): return self.url
        def read(self, size):
            if self.url==policy.ROBOTS_URL:return b'User-agent: *\nAllow: /\nCrawl-delay: 10\n'
            return '<h3>2026年10月19日（月）浦和第5競走14:20発走</h3><table><tr><td>official card bytes</td></tr></table>'.encode()
    class Opener:
        def open(self, req, timeout):
            assert req.method == 'GET'
            if 'OddsTanFuku' in req.full_url: raise OSError('OPTIONAL_ODDS_UNAVAILABLE')
            return Response(req.full_url)
    monkeypatch.setattr(urllib.request, 'build_opener', lambda *a: Opener())
    artifact, errors = replay.capture_public_urw_sources({'venue_id':'URW', 'race_date':'2026-10-19',
        'race_no':5, 'race_id':'UNSIGNED-TEST'}, output=tmp_path/'bytes', reference_only=True)
    assert not errors and artifact['prediction_cutoff'] == '2026-10-19T14:18:00+09:00'
    assert artifact['scheduled_post_at'] == '2026-10-19T14:20:00+09:00'
    assert len(artifact['sources']) == 1 and artifact['optional_source_errors']
    assert artifact['production_authority'] is artifact['signed_source_claim'] is False


@pytest.fixture(scope='module')
def conditional_training():
    # Synthetic optimizer/conditional-mass test only, not race-quality credit.
    from runtime.local_race_key_shadow_owner import fit_conditioned_owner
    packs=[];labels={}
    for day in (1,2,3):
        p={'race_id':f'TEST-URW-{day}','race_date':f'2026-09-0{day}','venue_id':'URW',
            'venue_canon':'TEST_ONLY','venue_canon_source_sha256':'a'*64,
            'scheduled_post_at':f'2026-09-0{day}T12:00:00+09:00','prediction_cutoff':f'2026-09-0{day}T11:58:00+09:00',
            'production_authority':False,'runners':{},'baseline':{'W':['1'],'P2':['2','3'],'P3':['2','3','4']}}
        for i in range(1,6):
            p['runners'][str(i)]={'INDEX:HPI-L':float((i*day)%6),
                **{'STAGE:'+k:float((i+day)%3) for k in ('lead','frame','progression','final_reserve')}}
        p['sha256']=_sha(p);packs.append(p);labels[p['race_id']]=list(map(str,((day%5)+1,((day+1)%5)+1,((day+2)%5)+1)))
    model=fit_conditioned_owner(packs,labels)
    return packs,labels,model


def test_conditional_joint_mass_normalization_and_no_actual_prefix_input(conditional_training):
    from runtime.local_race_key_shadow_owner import predict_conditioned_owner
    packs,_,model=conditional_training
    p=copy.deepcopy(packs[-1]);p.update(race_id='TEST-URW-VALIDATION',scheduled_post_at='2026-09-04T12:00:00+09:00',prediction_cutoff='2026-09-04T11:58:00+09:00')
    p['sha256']=_sha({k:v for k,v in p.items() if k!='sha256'})
    pred=predict_conditioned_owner(model,p,historical_replay=True)
    assert sum(x['model_mass'] for x in pred['ordered_triples'])==pytest.approx(1.)
    assert len(pred['ordered_triples'])==60 and len(pred['ordered_pairs'])==20
    assert all(len({x['head'],x['second'],x['third']})==3 for x in pred['ordered_triples'])
    assert not pred['material_exact_evidence'] and not pred['formal_handoff_allowed']
    with pytest.raises(ShadowOwnerError,match='STRICTLY_EARLIER'):
        predict_conditioned_owner(model,packs[0],historical_replay=True)
    p['venue_id']='KAW';p['sha256']=_sha({k:v for k,v in p.items() if k!='sha256'})
    with pytest.raises(ShadowOwnerError,match='TRANSFER_FORBIDDEN'):
        predict_conditioned_owner(model,p,historical_replay=True)


def test_conditional_model_training_parameters_ignore_validation_input(conditional_training):
    from runtime.local_race_key_shadow_owner import fit_conditioned_owner,predict_conditioned_owner
    packs,labels,model=conditional_training
    again=fit_conditioned_owner(packs,labels)
    assert again['fits']==model['fits']
    assert all(set(f['coefficients'])!={0.} for f in model['fits'])
    missing=copy.deepcopy(packs)
    for pack in missing:
        pack['venue_canon']=None
        pack['sha256']=_sha({k:v for k,v in pack.items() if k!='sha256'})
    with pytest.raises(ShadowOwnerError,match='TRAINING_SCOPE'):
        fit_conditioned_owner(missing,labels)
    # An injected time cannot create a forward freeze, even in a test process.
    p=copy.deepcopy(packs[-1]);p.update(race_id='TEST-URW-FUTURE',scheduled_post_at='2027-01-01T12:00:00+09:00',prediction_cutoff='2027-01-01T11:58:00+09:00')
    p['sha256']=_sha({k:v for k,v in p.items() if k!='sha256'})
    with pytest.raises(ShadowOwnerError,match='FORWARD_CLOCK'):
        predict_conditioned_owner(model,p,now=NOW)


def test_conditional_models_cannot_silently_change_feature_semantics(conditional_training):
    from runtime.local_race_key_shadow_owner import fit_conditioned_owner,predict_conditioned_owner
    packs,labels,model=conditional_training
    changed=copy.deepcopy(packs)
    changed[-1]['schema']='URW-CONDITIONAL-TRANSFER-FEATURES-v2'
    changed[-1]['sha256']=_sha({k:v for k,v in changed[-1].items() if k!='sha256'})
    with pytest.raises(ShadowOwnerError,match='TRAINING_SCOPE'):
        fit_conditioned_owner(changed,labels)
    p=changed[-1]
    p.update(race_id='TEST-URW-VALIDATION',scheduled_post_at='2026-09-04T12:00:00+09:00')
    p['sha256']=_sha({k:v for k,v in p.items() if k!='sha256'})
    with pytest.raises(ShadowOwnerError,match='FEATURE_SCHEMA_MISMATCH'):
        predict_conditioned_owner(model,p,historical_replay=True)


def test_unsigned_public_adapter_preserves_full_universe_and_never_claims_signature(original):
    from runtime.local_race_key_shadow_owner import compile_public_venue_candidate,owner_feature_pack
    req,s,n=original
    # Legacy archive has no source_race_context. Build an explicitly unsigned
    # parser derivative; do not change its original signed envelope or claim a
    # new receipt. The live public acquisition records this context itself.
    raw=copy.deepcopy(s['artifact']);raw['source_race_context']={k:req[k] for k in ('venue_id','race_date','race_no')}
    raw['source_snapshot_sha256']=_sha({k:v for k,v in raw.items() if k!='source_snapshot_sha256'})
    numeric=copy.deepcopy(n);numeric['production_evidence_compiler']['source_snapshot_sha256']=raw['source_snapshot_sha256']
    out=compile_public_venue_candidate(req,raw,numeric,historical_replay=True)
    assert out['source_receipt_sha256'] is None and out['source_signature_authority'].startswith('UNSIGNED')
    assert not out['formal_handoff_allowed'] and out['forward_oos_credit']==0
    assert len(owner_feature_pack(out,numeric)['runners'])==12
    bad=copy.deepcopy(raw);bad['runner_status_registry'][0]['status']='ACTIVE_DECLARED'
    bad['source_snapshot_sha256']=_sha({k:v for k,v in bad.items() if k!='source_snapshot_sha256'})
    changed=copy.deepcopy(n);changed['production_evidence_compiler']['source_snapshot_sha256']=bad['source_snapshot_sha256']
    with pytest.raises(ShadowOwnerError,match='ACTIVE_FULL29'):
        compile_public_venue_candidate(req,bad,changed,historical_replay=True)


def test_declared_snapshot_is_research_only_and_does_not_open_verified_active_path(monkeypatch):
    import runtime.local_race_key_shadow_owner as owner
    capsule=json.loads(gzip.decompress((fixture_root()/'declared_capsule.json.gz').read_bytes()))
    assert capsule['TEST_SYNTHETIC_ONLY'] is True
    source=capsule['source_artifact'];numeric=capsule['numerical']
    report=capsule['report'];recorded=datetime.fromisoformat(report['frozen_at'])
    class FixedClock(datetime):
        @classmethod
        def now(cls,tz=None):return recorded.astimezone(tz) if tz else recorded.replace(tzinfo=None)
    # Clock injection is confined to this unit test. Real freeze entry points
    # take their own actual clock and give no signed/Forward/OOS credit.
    monkeypatch.setattr(owner,'datetime',FixedClock)
    before=copy.deepcopy(source)
    with pytest.raises(ShadowOwnerError,match='ACTIVE_FULL29'):
        owner.compile_public_venue_candidate(numeric,source,numeric)
    research=owner.compile_public_venue_candidate(numeric,source,numeric,declared_snapshot_shadow=True)
    assert source==before and research['runner_status_registry']==source['runner_status_registry']
    assert research['runner_universe_basis']=='DECLARED_NOT_VERIFIED_ACTIVE'
    assert research['source_age_seconds']>3600 and research['freshness_claim'] is False
    assert not any(research[k] for k in ('production_authority','formal_handoff_allowed',
        'signed_final_claim','prediction_consumption_authorized','krs_consumption_authorized',
        'ticket_consumption_authorized','capital_consumption_authorized'))
    assert research['forward_oos_credit']==report['forward_oos_credit']==0
    incomplete=copy.deepcopy(numeric)
    incomplete['runners'][0]['canonical_components'].pop('HPI-L')
    with pytest.raises(ShadowOwnerError,match='ACTIVE_FULL29'):
        owner.compile_public_venue_candidate(incomplete,source,incomplete,declared_snapshot_shadow=True)
    with pytest.raises(ShadowOwnerError,match='PRESTART_ONLY'):
        owner.compile_public_venue_candidate(numeric,source,numeric,declared_snapshot_shadow=True,historical_replay=True)
    # The offline mode cannot produce a new diagnostic after the real cutoff.
    recorded=datetime.fromisoformat(report['fields']['prediction_cutoff'])
    with pytest.raises(ShadowOwnerError,match='CLOCK_OR_IDENTITY'):
        owner.compile_public_venue_candidate(numeric,source,numeric,declared_snapshot_shadow=True)


@pytest.mark.parametrize('venue',['MOR','KNZ','NGY','SON','HIM','MIZ','MON','SAG','KSM','KCH'])
def test_missing_current_venue_canon_holds_without_using_another_venue(original,venue):
    from runtime.local_race_key_shadow_owner import compile_public_venue_candidate
    req,s,n=original
    with pytest.raises(ShadowOwnerError,match='OUTSIDE_SOUTH_KANTO_SCOPE'):
        compile_public_venue_candidate({**req,'venue_id':venue},s['artifact'],n,historical_replay=True)


def test_real_ohi_source_uses_recovered_canon_and_never_equates_unverified_course_or_sand():
    from runtime.local_race_key_shadow_owner import compile_public_venue_candidate
    path=ROOT/'runtime/executions/KM-LOCAL-OHI-20261009-R04-LIVE-R2/SOURCE/runs/37898486286-source/source_receipt_envelope.json'
    raw=path.read_bytes()
    assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()=='8ffb28a43109a5af30db62fe5134eac8e189b773'
    source=json.loads(raw);artifact=source['artifact'];rid=source['receipt']['race_id']
    Ed25519PublicKey.from_public_bytes(base64.b64decode(PUBKEY)).verify(base64.b64decode(source['signature']),
        json.dumps(source['receipt'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
    assert _sha(artifact)==source['receipt']['artifact_sha256']
    # The observed official heading says17:12. Retain the original16:28
    # cutoff; this is historical source-only research, no old FINAL rewrite.
    req={'family_id':'LOCAL','venue_id':'OHI','race_date':'2026-10-09','race_no':4,'race_id':rid,'execution_id':rid,
        'scheduled_post_at':'2026-10-09T17:12:00+09:00','prediction_cutoff':artifact['prediction_cutoff']}
    n=materialize_production(artifact,{**req,'runners':artifact['official_runner_universe']['runners']},assess()['required_indices'])
    out=compile_public_venue_candidate(req,artifact,n,historical_replay=True)
    assert out['venue_canon']=='OHI-v2.1-20260903' and out['current_course_family']=='R-IN'
    assert out['numeric_provenance_sha256']==n['index_provenance_hash']
    for ev in out['venue_evidence'].values():
        assert ev['current_condition_translation']['direct_history_qualification'].startswith('HOLD_OCF')
        assert not any(s['matched_venue_distance'] for s in ev['past_starts'])
    assert not out['formal_handoff_allowed'] and out['forward_oos_credit']==0
    assert path.read_bytes()==raw


def test_public_shadow_rejects_changed_frozen_model_before_any_source_get(tmp_path,monkeypatch):
    from scripts.urw_candidate_krs_replay import public_source_shadow
    from runtime.local_physical import source_acquisition
    monkeypatch.setattr(source_acquisition,'acquire_sources',
        lambda *a,**k:pytest.fail('changed research model must fail before network'))
    model=tmp_path/'forecasts_before_evaluation.json.gz';model.write_bytes(b'changed')
    (tmp_path/'ranker_report.json').write_text(json.dumps({'forecast_artifact_sha256':'0'*64}))
    output=tmp_path/'attempt'
    public_source_shadow(output,model)
    report=json.loads((output/'public_shadow_status.json').read_text())
    assert report['first_failed_stage']=='FROZEN_RESEARCH_MODEL_BINDING'
    assert report['error']=='PUBLIC_FROZEN_MODEL_ARTIFACT_MISMATCH'
    assert report['runtime_post_count']==report['forward_oos_credit']==0


@pytest.mark.parametrize('change',['missing_plan','changed_hash','foreign_venue','race_mismatch','expired'])
def test_urw_public_research_plan_failures_stop_before_network(tmp_path,monkeypatch,change):
    from scripts import urw_candidate_krs_replay as replay
    from runtime.local_physical import source_acquisition
    class Clock(datetime):
        @classmethod
        def now(cls,tz=None):
            return datetime(2026,10,19,4 if change=='expired' else 0,0,tzinfo=timezone.utc).astimezone(tz)
    monkeypatch.setattr(replay,'datetime',Clock)
    monkeypatch.setattr(source_acquisition,'acquire_sources',lambda *a,**k:pytest.fail('NO GET FOR INVALID PLAN'))
    fields={'venue_id':'URW','race_date':'2026-10-19','race_no':2,
            'scheduled_post_at':'2026-10-19T12:50:00+09:00','prediction_cutoff':'2026-10-19T12:48:00+09:00'}
    plan={'family_id':'LOCAL','venue_id':'URW','race_date':'2026-10-19','races':[{'fields':fields}]}
    if change=='foreign_venue':plan['venue_id']='MOR'
    if change=='race_mismatch':fields['race_no']=1
    plan['plan_sha256']=_sha(plan)
    if change=='changed_hash':plan['plan_sha256']='0'*64
    path=tmp_path/'plan.json';path.write_text(json.dumps(plan))
    report=replay.public_source_shadow(tmp_path/'out',race_no=2,plan_path=None if change=='missing_plan' else path)
    assert report['status']=='HOLD_PUBLIC_SHADOW' and report['runtime_post_count']==0
    assert report['first_failed_stage'] in ('DATED_OFFICIAL_PLAN_BINDING','DATED_PUBLIC_SHADOW_WINDOW')


@pytest.mark.parametrize('change',['none','post','runner'])
def test_urw_second_race_preserves_declared_hold_and_evidence_before_prediction(original,tmp_path,monkeypatch,change):
    from scripts import urw_candidate_krs_replay as replay
    from runtime.local_physical import source_acquisition
    from runtime.local_physical.nar_runner_universe import enrich_source_artifact
    class Clock(datetime):
        @classmethod
        def now(cls,tz=None):
            return datetime(2026,10,19,0,0,tzinfo=timezone.utc).astimezone(tz)
    monkeypatch.setattr(replay,'datetime',Clock)
    # Explicitly unsigned synthetic time derivative of an actual source. It
    # exists only under tmp_path; no original receipt, status or OOS is edited.
    source=copy.deepcopy(original[1]['artifact'])
    source['normalized_evidence'].pop('odds_tables',None)
    source['normalized_evidence']['start_time'].update(value='12:50',authority='NAR_OFFICIAL')
    if change=='post':source['normalized_evidence']['start_time']['value']='12:51'
    declared=enrich_source_artifact(copy.deepcopy(source))['declared_runner_universe']
    def acquire(manifest):
        assert manifest['race_id'].endswith('R02-PUBLIC-SHADOW')
        return copy.deepcopy(source),[]
    monkeypatch.setattr(source_acquisition,'acquire_sources',acquire)
    monkeypatch.setattr(replay,'materialize_production',lambda *a,**k:pytest.fail('DECLARED MUST NOT PREDICT'))
    plan={'family_id':'LOCAL','venue_id':'URW','race_date':'2026-10-19','races':[{'fields':{
        'venue_id':'URW','race_date':'2026-10-19','race_no':2,'scheduled_post_at':'2026-10-19T12:50:00+09:00',
        'prediction_cutoff':'2026-10-19T12:48:00+09:00'},'declared_runner_universe':declared}]}
    if change=='runner':
        plan['races'][0]['declared_runner_universe']=copy.deepcopy(declared)
        plan['races'][0]['declared_runner_universe']['runners'][0]['name']='PLAN_RUNNER_CHANGED'
    plan['plan_sha256']=_sha(plan);path=tmp_path/'plan.json';path.write_text(json.dumps(plan))
    report=replay.public_source_shadow(tmp_path/'out',race_no=2,plan_path=path)
    if change!='none':
        assert report['first_failed_stage']=='FRESH_OFFICIAL_RACE_RECHECK'
        assert ('POST_CHANGED_REPLAN' if change=='post' else 'UNIVERSE_CHANGED_REPLAN') in report['error']
        assert report['observed_evidence_saved'] and not report['prediction_frozen']
        return
    assert report['error']=='PUBLIC_ACTIVE_DECLARED_IS_NOT_VERIFIED_ACTIVE'
    assert report['request_fields']['race_no']==2 and report['plan_sha256']==plan['plan_sha256']
    assert report['declared']==12 and report['observed_evidence_saved'] and not report['prediction_frozen']
    assert all(s['status']=='ACTIVE_DECLARED' for s in report['runner_status_registry'])
    assert report['signed_source_count']==report['signed_final_count']==report['forward_oos_credit']==0


def test_actual_frozen_failure_audit_preserves_models_and_traces_all_29(tmp_path,monkeypatch):
    from scripts.urw_candidate_krs_replay import failure_audit
    from runtime import local_race_key_shadow_owner as owner
    monkeypatch.setattr(owner,'fit_conditioned_owner',lambda *a,**k:pytest.fail('NO REFIT AFTER VALIDATION'))
    output=tmp_path/'audit';failure_audit(output)
    report=json.loads((output/'failure_and_transport_audit.json').read_text())
    assert len(report['indices'])==29 and len(report['validation'])==3
    assert [r['baseline_winner_rank'] for r in report['validation']]==[4,12,11]
    assert sum(r['cells'] for r in report['indices'])==1827
    assert all(r['provenance_complete']==r['cells'] for r in report['indices'])
    bvi=next(r for r in report['indices'] if r['index']=='BVIg-L')
    assert not bvi['candidate_krs_input_changed_fields'] and bvi['static_score_changes']==0
    assert report['fitted_or_selected_models']==report['new_tickets']==report['runtime_post_count']==0
    assert all(m['unknown_contribution_verified_zero'] for r in report['validation'] for m in r['models'].values())


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


def test_urw_recent_record_uses_observation_date_not_transport_row_order():
    from runtime.local_production_static_owner import _runner_facts
    past = {"surface": "DIRT", "venue": "浦和", "distance": 1400,
            "field_size": 10, "content_positions": [2, 2, 2, 2]}
    old = {**past, "date": "26.08.01", "finish": 1}
    recent = {**past, "date": "26.09.20", "finish": 10}
    row = {"starts": [old, recent], "race_card_fetched_at": "2026-09-22T10:00:00+09:00"}
    before = copy.deepcopy(row)
    kwargs = {"venue_name": "浦和", "distance": 1400,
              "race_day": datetime(2026, 9, 23, tzinfo=timezone.utc)}
    a = _runner_facts(row, **kwargs)
    b = _runner_facts({**row, "starts": [recent, old]}, **kwargs)
    assert a == b and row == before
    assert a["recent_dirt_finish_share"] == 0
    assert a["exact_wins"] == 1 and a["exact_podiums"] == 1
    assert [v["date"] for v in a["observed_runs"]] == ["2026-09-20", "2026-08-01"]


def test_urw_record_cannot_postdate_source_observation_even_before_target_day():
    from runtime.local_production_static_owner import _runner_facts, StaticOwnerError
    row = {"race_card_fetched_at": "2026-09-21T14:00:00+09:00",
           "starts": [{"date": "26.09.22", "surface": "DIRT", "venue": "浦和",
                       "distance": 1400, "field_size": 10, "finish": 1}]}
    with pytest.raises(StaticOwnerError, match="HISTORICAL_START_AFTER_SOURCE_OBSERVATION"):
        _runner_facts(row, venue_name="浦和", distance=1400,
                      race_day=datetime(2026, 9, 23, tzinfo=timezone.utc))


@pytest.mark.parametrize("before,after", [
    ("2026年9月23日", "2026年9月24日"), ("浦 和", "川 崎"), ("第12競走", "第11競走")])
def test_direct_urw_candidate_checks_printed_identity_beside_transport(original, before, after):
    import unicodedata
    req, envelope, numeric = original
    changed = copy.deepcopy(envelope)
    source = changed["artifact"]
    card = next(s for s in source["sources"]
                if s.get("source_class") == "OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT")
    text = unicodedata.normalize("NFKC", gzip.decompress(
        base64.b64decode(card["raw_gzip_b64"])).decode("utf-8"))
    assert before in text
    raw = text.replace(before, after).encode("utf-8")
    card["raw_gzip_b64"] = base64.b64encode(gzip.compress(raw, mtime=0)).decode()
    card["raw_sha256"] = hashlib.sha256(raw).hexdigest()
    card["snapshot_sha256"] = _sha({k:v for k,v in card.items() if k != "snapshot_sha256"})
    source["source_snapshot_sha256"] = _sha({k:v for k,v in source.items() if k != "source_snapshot_sha256"})
    changed["receipt"]["artifact_sha256"] = _sha(source)
    changed["receipt_sha256"] = _sha(changed["receipt"])
    # Unsigned negative mutation, not a newly signed SOURCE. A consistent
    # transport hash must not bypass the independent printed identity check.
    with pytest.raises(ValueError, match="URW_NUMERICAL_CARD_BODY_IDENTITY_MISMATCH"):
        compile_urw_candidate(req, changed, numeric, now=NOW, historical_replay=True)



def test_forward_owner_protocol_preserves_models_and_has_no_automatic_promotion(conditional_training):
    from scripts.urw_candidate_krs_replay import owner_forward_protocol
    _,_,model=conditional_training
    before=copy.deepcopy(model)
    protocol=owner_forward_protocol(model,model)
    assert model==before
    assert protocol["minimum_eligible_races"]==60 and protocol["minimum_distinct_race_dates"]==5
    assert protocol["interval"]["upper_percentile"]==95
    assert protocol["production_authority"] is False
    assert "NO_AUTOMATIC_PROMOTION" in protocol["production_promotion"]
    changed=copy.deepcopy(model);changed["fits"][0]["coefficients"][0]+=1
    with pytest.raises(ValueError,match="MODEL_HASH_OR_AUTHORITY"):
        owner_forward_protocol(changed,model)


def test_frozen_owner_evaluator_requires_result_after_post_and_retains_nonformal(conditional_training):
    from scripts.urw_candidate_krs_replay import owner_forward_protocol,evaluate_owner_forward_comparison
    from runtime.local_race_key_shadow_owner import predict_conditioned_owner
    packs,_,model=conditional_training
    pack=copy.deepcopy(packs[-1]);pack.update(race_id="TEST-URW-VALIDATION",
        race_date="2026-09-04",scheduled_post_at="2026-09-04T12:00:00+09:00",
        prediction_cutoff="2026-09-04T11:58:00+09:00")
    pack["sha256"]=_sha({k:v for k,v in pack.items() if k!="sha256"})
    pred=predict_conditioned_owner(model,pack,historical_replay=True)
    # Unsigned synthetic freeze fields for evaluator-contract tests only.
    pred.update(temporal_class="LOCAL_PRESTART_SHADOW_NOT_FORMAL",
                frozen_at="2026-09-04T11:55:00+09:00")
    pred["sha256"]=_sha({k:v for k,v in pred.items() if k!="sha256"})
    freeze={"race_id":pack["race_id"],"race_date":pack["race_date"],
        "scheduled_post_at":pack["scheduled_post_at"],"prediction_cutoff":pack["prediction_cutoff"],
        "frozen_at":"2026-09-04T11:55:00+09:00", "feature_pack":pack,
        "models":{"BASELINE":model,"CANDIDATE":model},
        "predictions":{"BASELINE":pred,"CANDIDATE":pred},
        "protocol":owner_forward_protocol(model,model),"formal_quality_eligible":False}
    freeze["sha256"]=_sha(freeze)
    label={"race_id":pack["race_id"],"official_result_verified":True,
        "source_url":"https://example.invalid/TEST-ONLY", "source_raw_sha256":"0"*64,
        "observed_at":"2026-09-04T12:10:00+09:00","finish_order":["1","2","3"]}
    actual=evaluate_owner_forward_comparison(freeze,label)
    assert actual["paired_joint_nll_delta"]==0
    assert actual["formal_quality_eligible"] is actual["production_authority"] is False
    assert actual["recommendation_pfs"]=="N/A" and actual["actual_purchase_pfs"]=="UNKNOWN"
    with pytest.raises(ValueError,match="RESULT_IDENTITY_OR_TIME"):
        evaluate_owner_forward_comparison(freeze,{**label,"observed_at":"2026-09-04T11:59:00+09:00"})
    broken=copy.deepcopy(freeze);broken["predictions"]["CANDIDATE"]["ranking"]=[]
    with pytest.raises(ValueError,match="FREEZE_OR_PROTOCOL_CHANGED"):
        evaluate_owner_forward_comparison(broken,label)

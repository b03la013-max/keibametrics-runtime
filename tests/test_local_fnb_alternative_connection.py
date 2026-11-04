"""Synthetic crypto/transport fixtures. Not real SOURCE or LIVE acceptance."""
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
import base64,json
from unittest.mock import Mock

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat

from runtime import local_fnb_alternative_connection as m
from runtime import local_fnb_r20_chat_completion as r20
from runtime import local_fnb_exact_orientation_research as exact
from runtime import local_fnb_adopted_single_owner as compute
from test_local_fnb_provider_independence_r14 import fixture_card,NOW


def fixture(monkeypatch):
    raw,capture,intent=fixture_card();key=Ed25519PrivateKey.generate()
    trust={'receipt_public_key_b64':base64.b64encode(key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)).decode(),
        'receipt_signer_key_id':'SYNTHETIC_KEY_NEVER_INSTALLED','engine_sha256':m.common.ENGINE_SHA,'parameter_map_sha256':m.common.MAP_SHA}
    # Only this mechanical fixture substitutes an ephemeral key. Production
    # code separately rejects any key differing from existing canonical trust.
    monkeypatch.setattr(m,'canonical_trust',lambda trust:None)
    def sign(*,phase,race_id,status,artifact):
        receipt={'family':'LOCAL','phase':phase,'race_id':race_id,'status':status,'errors':[],
            'engine_sha256':trust['engine_sha256'],'parameter_map_sha256':trust['parameter_map_sha256'],'artifact_sha256':m.compact(artifact)}
        return {'artifact':deepcopy(artifact),'receipt':receipt,'receipt_sha256':m.compact(receipt),'signature_alg':'Ed25519',
            'signer_key_id':trust['receipt_signer_key_id'],'signature':base64.b64encode(key.sign(json.dumps(receipt,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())).decode()}
    from runtime.local_fnb_rakuten_reference import parse_card
    parsed=parse_card(raw,capture=capture,race=intent,now=NOW)
    request={**intent,'family_id':'LOCAL','race_id':'KM-LOCAL-FNB-20261106-R01-LIVE-SYNTHETIC',
        'scheduled_post_at':'2026-11-06T14:45:00+09:00','prediction_cutoff':'2026-11-06T14:40:00+09:00'}
    rows=[{'horse_no':r['horse_no'],'name':r['name'],'status':'ACTIVE','current_jockey':r['current_jockey'],
        'current_load':r['current_load']} for r in parsed['runners']]
    permission=b'SYNTHETIC_PERMISSION_ORIGINAL';changes=b'SYNTHETIC_CURRENT_STATE_ORIGINAL'
    artifact={'schema':m.SOURCE_SCHEMA,'source_class':m.SOURCE_CLASS,'provider':'RAKUTEN_KEIBA','official':False,
        'raw_sha256':m.sha(raw),'source_url':parsed['source_url'],'parsed_card_sha256':m.compact(parsed),
        'source_snapshot_sha256':m.compact(parsed),'source_freeze_at':NOW.isoformat(),
        'active_runner_ids':['1','2'],'active_universe_sha256':m.compact(rows),
        'provider_permission':{'provider':'RAKUTEN_KEIBA','actor_id':'TEST_ONLY','original_sha256':m.sha(permission),
            'retrieval_method_authorized':True,'private_retention_authorized':True,'cloud_processing_authorized':True,
            'effective_from':'2026-11-03T00:00:00+00:00','effective_until':'2026-11-07T00:00:00+00:00'},
        'current_state':{'original_sha256':m.sha(changes),'latest_changes_verified':True,'complete_declared_universe':True,
            'request_race_id':request['race_id'],'card_raw_sha256':m.sha(raw),'observed_at':NOW.isoformat(),'runners':rows},
        'field_admission':{'profile_adoption_verified':True,'consumer_scope':'FNB_FORMAL_FULL29_STATIC_KRS_TICKET',
            'admitted_fields':['identity','scheduled_post_at','runner_number_name','frame','jockey_load','current_changes',
                'active_status','current_body_weight','weather_going','dated_history'],'decision_sha256':'a'*64,
            'effective_from':'2026-11-03T00:00:00+00:00','effective_until':'2026-11-07T00:00:00+00:00'}}
    owner={'venue_id':'FNB','family_id':'LOCAL','owner_count':1,'model_code_sha256':m.common.MODEL_SHA,
        'model_profile_sha256':m.common.MODEL_PROFILE_SHA,**{c:True for c in m.CONSUMERS},
        'selection_profile':exact.PROFILE,'selection_module_sha256':exact.MODULE_SHA,
        'selection_profile_sha256':m.sha(exact.PROFILE_PATH.read_bytes()),'alternative_source_class':m.SOURCE_CLASS,
        'races_by_date':{'2026-11-06':[1]},'effective_from':'2026-11-03T00:00:00+00:00',
        'effective_until':'2026-11-07T00:00:00+00:00','current_authority':'KM-FAMILY-CURRENT-AUTHORITY-20261012-R51',
        'source_admission_decision_sha256':'a'*64,'actual_purchase_authorized':False,'registered_OOS_increment':0,
        'numerical_registry_sha256':m.sha((m.ROOT/'mapping/local_evidence_feature_rule_registry_v0.1_candidate_20260923.json').read_bytes()),
        'numerical_mapping_sha256':m.sha((m.ROOT/'mapping/local_full_numerical_mapping_v0.1_candidate_20260923.json').read_bytes())}
    owner['connection_module_sha256']={name:m.sha((m.ROOT/name).read_bytes()) for name in m.CONNECTION_MODULES}
    captured={'raw':raw,'capture':capture,'request':request,'actor_id':'TEST_ONLY','permission_original':permission,
        'current_state_original':changes,'source_envelope':sign(phase='SOURCE',race_id=request['race_id'],status='SOURCE_FROZEN',artifact=artifact),
        'owner_adoption_envelope':sign(phase='OWNER_ADOPTION',race_id=request['race_id'],status='APPROVED',artifact=owner),'trust':trust}
    return captured,intent,trust,sign,owner


def assess(x):return m.source_assessment(x[0],intent=x[1],now=NOW,trust=x[2])


def test_alternative_class_is_honest_and_one_owner_does_not_need_BC(monkeypatch,tmp_path):
    x=fixture(monkeypatch);captured,intent,trust,sign,owner=x
    source=assess(x);assert source['source_admitted'] and source['artifact']['official'] is False
    out=m.owner_adoption(captured['owner_adoption_envelope'],request=captured['request'],source=source['artifact'],trust=trust,now=NOW)
    assert out['owner_count']==1 and all(out[k] for k in m.CONSUMERS)
    assert set(captured)-{'raw','capture','request','actor_id','permission_original','current_state_original','source_envelope','owner_adoption_envelope','trust'}==set()


def test_unsigned_callback_200_is_not_source_admission_and_stops_owner(monkeypatch,tmp_path):
    x=fixture(monkeypatch);captured=x[0];captured.pop('source_envelope');executor=Mock()
    monkeypatch.delenv('CI',raising=False);monkeypatch.delenv('GITHUB_ACTIONS',raising=False)
    result=r20.complete('2026-11-06 船橋1R',tmp_path,now=NOW,producers={'entry_mode':m.MODE,'source':lambda **kw:captured,
        'execute_single_owner':executor,'trust':x[2]})
    assert result['first_failed_stage']=='SOURCE' and result['reason']=='ALTERNATIVE_SOURCE_SIGNED_RECEIPT_MISSING'
    assert result['status']=='EXECUTION_HOLD_NOT_NO_BET' and not result['recipient_delivery_ack']
    executor.assert_not_called();assert list(tmp_path.glob('source_attempts/**/original_provider_card.html'))


@pytest.mark.parametrize('case,code',[
    ('permission','PERMISSION_ORIGINAL'),('changes','CURRENT_CHANGES'),('scope','FIELD_ADMISSION'),
    ('active','ACTIVE_SET_SHA'),('official','SIGNED_RAW_OR_CLASS'),('signature','SIGNATURE_OR_BINDING'),
    ('race','REQUEST_IDENTITY'),('raw','CAPTURE_URL_OR_HASH')])
def test_alternative_admission_counterexamples(monkeypatch,case,code):
    x=fixture(monkeypatch);c,i,t,sign,owner=x
    if case=='permission':c['permission_original']=b'wrong'
    elif case=='changes':c['current_state_original']=b'wrong'
    elif case in ('scope','active','official'):
        a=deepcopy(c['source_envelope']['artifact'])
        if case=='scope':a['field_admission']['profile_adoption_verified']=False
        elif case=='active':a['active_runner_ids']=['1']
        else:a['official']=True
        c['source_envelope']=sign(phase='SOURCE',race_id=c['request']['race_id'],status='SOURCE_FROZEN',artifact=a)
    elif case=='signature':c['source_envelope']['artifact']['provider']='NAR_OFFICIAL'
    elif case=='race':c['request']['race_no']=2
    else:c['raw']+=b'changed'
    try:r=assess(x)
    except (m.ProducerHold,ValueError) as e:assert code in str(e)
    else:assert not r['source_admitted'] and any(code in s for s in r['reasons'])


@pytest.mark.parametrize('key,value',[('owner_count',2),('venue_id','KAW'),('ticket_numeric_consumption',False),
    ('selection_module_sha256','0'*64),('effective_from','2026-11-05T00:00:00+00:00')])
def test_owner_scope_and_effective_time_are_not_granted_by_binding(monkeypatch,key,value):
    c,i,t,sign,o=fixture(monkeypatch);o[key]=value
    env=sign(phase='OWNER_ADOPTION',race_id=c['request']['race_id'],status='APPROVED',artifact=o)
    with pytest.raises(m.ProducerHold):m.owner_adoption(env,request=c['request'],source=c['source_envelope']['artifact'],trust=t,now=NOW)


def test_no_existing_signer_stops_before_any_krs(monkeypatch,tmp_path):
    x=fixture(monkeypatch);c,i,t,sign,o=x;engine=Mock();monkeypatch.setattr(m.common,'execute_krs',engine)
    with pytest.raises(m.ProducerHold,match='FINAL_SIGNER_NOT_CONNECTED'):
        compute.execute(request=c['request'],admitted_source=assess(x),adopted_owner=o,captured_source=c,
            private_root=tmp_path,now=NOW,engine=None,params=None,clock=lambda:NOW)
    engine.assert_not_called()


def test_real_default_trust_rejects_a_new_key_without_reading_secrets():
    with pytest.raises(m.ProducerHold,match='NO_NEW_KEY_ALLOWED'):m.canonical_trust({'receipt_public_key_b64':'fake'})


def mock_krs(requested, *, destination,**kwargs):
    """Synthetic Engine response: no actual trials, no empirical acceptance."""
    ids=[r['horse_no'] for r in requested['horses']]
    output={'snapshot':{'master_seed':1,'run_count':5000,'prediction_id':requested['race']['prediction_id'],'field_size':len(ids)},
        'engine':{'engine_version':'1.1.0','parameter_map_version':'0.1-provisional','parameter_status':'PROVISIONAL_UNCALIBRATED'},
        'summary':[{'horse_no':r,**{k:.5 for k in ('SSR-W','SSR-P2','SSR-P3','LSR','Z4R-W','Z4R-P2','Z4R-P3')}} for r in ids],
        'scenario_analysis':{n:{'run_count':1000,'ssr':{str(r):{k:.5 for k in ('SSR-W','SSR-P2','SSR-P3','LSR','Z4R-W','Z4R-P2','Z4R-P3')} for r in ids}} for n in exact.SCENARIOS}}
    Path(destination).mkdir(parents=True)
    for name,value in [('execution_input.json',requested),('execution_output.json',output)]:
        (Path(destination)/name).write_bytes(m.encoded(value))
    return {'synthetic_only':True,'actual_trials':0}


def test_complete_single_owner_adapter_uses_actual_fixed_arithmetic_and_tree_with_synthetic_crypto_krs(monkeypatch,tmp_path):
    x=fixture(monkeypatch);c,i,t,sign,o=x;monkeypatch.setattr(m.common,'execute_krs',mock_krs)
    result=compute.execute(request=c['request'],admitted_source=assess(x),adopted_owner=o,captured_source=c,
        private_root=tmp_path,now=NOW,engine=None,params=None,sign_final=sign,clock=lambda:NOW)
    out=m.verify_result(result,request=c['request'],source=assess(x),adoption=o,trust=t,root=tmp_path,now=NOW,captured=c)
    assert out['status']==m.READY and out['owner_count']==1 and not out['independent_BC']
    assert not out['recipient_delivery_ack'] and not out['natural_delivery_verified']
    assert len(result['numerical']['runners'])==2 and len(result['numerical']['required_indices'])==29
    assert result['KRS_receipt']['actual_trials']==0


def test_delivery_uses_original_ack_and_durable_no_resend_claim(tmp_path):
    from runtime import local_fnb_day_supervisor as day
    race={'race_id':'SYNTHETIC-RACE','prediction_cutoff':'2026-11-04T01:00:00+00:00'}
    original={'path':'body.md','sha256':m.sha(b'SYNTHETIC BODY')};(tmp_path/'body.md').write_bytes(b'SYNTHETIC BODY')
    ready={'originals':{'body':original},'final_freeze_at':NOW.isoformat(),'source_snapshot_sha256':'a'*64,
        'revision':race['race_id'],'method_ticket_sha256':{'EXACTA':'b'*64}}
    adoption={'delivery_recipient_id':'TEST_SELF','delivery_route_id':'TEST_ROUTE','delivery_authorized':True}
    activation={**adoption,'delivery_enabled':True,'delivery_approval_ref':'SYNTHETIC_APPROVAL_NOT_LIVE'}
    inspect=Mock(return_value={});send=Mock(return_value={'status':'SEND_SUCCESS_IS_NOT_ACK'})
    binding={'delivery_activation':activation,'inspect_delivery':inspect,'authorize_delivery':lambda **kw:True,'deliver':send}
    a=m.deliver_verified(ready,request=race,adoption=adoption,producers=binding,root=tmp_path,clock=lambda:NOW)
    b=m.deliver_verified(ready,request=race,adoption=adoption,producers=binding,root=tmp_path,clock=lambda:NOW)
    assert not a['recipient_delivery_ack'] and not b['recipient_delivery_ack'] and send.call_count==1
    data={**adoption,'owner_model_sha256':m.common.MODEL_SHA,'owner_profile_sha256':m.common.MODEL_PROFILE_SHA,'race_id':race['race_id'],'revision':ready['revision'],
        'source_snapshot_sha256':ready['source_snapshot_sha256'],'method_ticket_sha256':ready['method_ticket_sha256'],
        'body_sha256':original['sha256'],'recipient_ack_verified':True,
        'received_at':NOW.isoformat()}
    raw=m.encoded(data);(tmp_path/'ACK.json').write_bytes(raw)
    inspect.return_value={'recipient_ack_verified':True,'original':{'path':'ACK.json','sha256':m.sha(raw)}}
    c=m.deliver_verified(ready,request=race,adoption=adoption,producers=binding,root=tmp_path,clock=lambda:NOW)
    assert c['recipient_delivery_ack'] and send.call_count==1 and not c['natural_delivery_verified']


@pytest.mark.parametrize('case',['wrong_recipient','late_ack','altered_body'])
def test_recipient_ack_identity_cutoff_and_body_are_not_inferred(tmp_path,case):
    race={'race_id':'SYNTHETIC-RACE','prediction_cutoff':'2026-11-04T01:00:00+00:00'}
    original={'path':'body.md','sha256':m.sha(b'BODY')};(tmp_path/'body.md').write_bytes(b'BODY')
    ready={'originals':{'body':original},'final_freeze_at':NOW.isoformat(),'source_snapshot_sha256':'a'*64,
        'revision':race['race_id'],'method_ticket_sha256':{'EXACTA':'b'*64}}
    adoption={'delivery_recipient_id':'SELF','delivery_route_id':'ROUTE','delivery_authorized':True}
    data={**adoption,'owner_model_sha256':m.common.MODEL_SHA,'owner_profile_sha256':m.common.MODEL_PROFILE_SHA,'race_id':race['race_id'],'revision':ready['revision'],
        'source_snapshot_sha256':ready['source_snapshot_sha256'],'method_ticket_sha256':ready['method_ticket_sha256'],
        'body_sha256':original['sha256'],'recipient_ack_verified':True,'received_at':NOW.isoformat()}
    if case=='wrong_recipient':data['delivery_recipient_id']='OTHER'
    elif case=='late_ack':data['received_at']='2026-11-04T01:01:00+00:00'
    else:data['body_sha256']='0'*64
    raw=m.encoded(data);(tmp_path/'ACK.json').write_bytes(raw)
    binding={'delivery_activation':adoption,'inspect_delivery':lambda **kw:{'recipient_ack_verified':True,
        'original':{'path':'ACK.json','sha256':m.sha(raw)}}}
    with pytest.raises(ValueError,match='ACK_RECEIPT_IDENTITY_OR_CLOCK'):
        m.deliver_verified(ready,request=race,adoption=adoption,producers=binding,root=tmp_path,clock=lambda:NOW)


def test_existing_kaw_only_and_four_false_profile_is_untouched():
    p=json.loads((m.ROOT/'profiles/local_production_static_owner_20261014_v1.json').read_bytes())
    assert p['venues']==['KAW'] and all(p[k] is False for k in m.CONSUMERS)


def computed_fixture(monkeypatch,tmp_path):
    x=fixture(monkeypatch);c,i,t,sign,o=x
    mocked=Mock(side_effect=mock_krs);monkeypatch.setattr(m.common,'execute_krs',mocked)
    result=compute.execute(request=c['request'],admitted_source=assess(x),adopted_owner=o,captured_source=c,
        private_root=tmp_path,now=NOW,engine=None,params=None,sign_final=sign,clock=lambda:NOW)
    return x,result,mocked


@pytest.mark.parametrize('case',['numeric','static','requested_krs','selection','mec','body'])
def test_even_a_signed_callback_cannot_replace_raw_model_selection_or_ticket_proof(monkeypatch,tmp_path,case):
    x,result,_=computed_fixture(monkeypatch,tmp_path);c,i,t,sign,o=x
    artifact=result['final_envelope']['artifact']
    if case=='numeric':
        row=result['numerical']['runners'][0];next(iter(row['canonical_components'].values()))['value']=42.1234567
        artifact['numerical_sha256']=m.sha(m.encoded(result['numerical']))
    elif case=='static':result['prediction']['freeze_at']='2026-11-03T00:00:00+00:00'
    elif case=='requested_krs':result['krs_requested_input']['horses'][0]['horse_no']=999
    elif case=='selection':result['selection_review']['selected_at']='2026-11-03T00:00:00+00:00'
    elif case=='mec':result['methods']['EXACTA']['strict_MEC_plans']=[]
    else:
        result['body']='ALL_FIELDS_TRUE_IS_NOT_A_COMPLETE_BODY'
        artifact['body_sha256']=m.sha(result['body'].encode())
        result['full_body_verification']['body_sha256']=artifact['body_sha256']
    result['final_envelope']=sign(phase='FINAL',race_id=c['request']['race_id'],status='PASS',artifact=artifact)
    with pytest.raises((m.ProducerHold,ValueError,KeyError)):
        m.verify_result(result,request=c['request'],source=assess(x),adoption=o,trust=t,root=tmp_path,now=NOW,captured=c)


def test_frozen_completion_readback_does_not_call_source_or_engine_again(monkeypatch,tmp_path):
    from functools import partial
    x=fixture(monkeypatch);c,i,t,sign,o=x;source=Mock(return_value=c)
    engine=Mock(side_effect=mock_krs);monkeypatch.setattr(m.common,'execute_krs',engine)
    binding={'source':source,'trust':t,'owner_adoption_envelope':c['owner_adoption_envelope'],
        'execute_single_owner':partial(compute.execute,engine=None,params=None,sign_final=sign,clock=lambda:NOW)}
    a=m.run(i,tmp_path,binding,clock=lambda:NOW)
    source.side_effect=AssertionError('NO_SOURCE_REFETCH_FOR_SAVED_ORIGINAL')
    b=m.run(i,tmp_path,binding,clock=lambda:NOW)
    assert a['new_prediction_executed'] and b['new_prediction_executed'] is False
    assert a['body_sha256']==b['body_sha256'] and source.call_count==1 and engine.call_count==1
    assert not b['recipient_delivery_ack']
    index=json.loads((tmp_path/m._index_path(i)).read_bytes())
    original=tmp_path/index['execution_original']['path'];original.write_bytes(original.read_bytes()+b' ')
    with pytest.raises(ValueError,match='PRIVATE_ORIGINAL_BYTES_CHANGED'):
        m.run(i,tmp_path,binding,clock=lambda:NOW)


@pytest.mark.parametrize('field',['revision','source_snapshot_sha256','method_ticket_sha256'])
def test_ack_requires_revision_source_and_each_ticket_sha(tmp_path,field):
    race={'race_id':'SYNTHETIC-RACE','prediction_cutoff':'2026-11-04T01:00:00+00:00'}
    (tmp_path/'body.md').write_bytes(b'BODY')
    ready={'originals':{'body':{'path':'body.md','sha256':m.sha(b'BODY')}},'final_freeze_at':NOW.isoformat(),
        'source_snapshot_sha256':'a'*64,'revision':race['race_id'],'method_ticket_sha256':{'EXACTA':'b'*64}}
    adoption={'delivery_recipient_id':'SELF','delivery_route_id':'ROUTE','delivery_authorized':True}
    data={**adoption,'owner_model_sha256':m.common.MODEL_SHA,'owner_profile_sha256':m.common.MODEL_PROFILE_SHA,'race_id':race['race_id'],'body_sha256':m.sha(b'BODY'),'recipient_ack_verified':True,
        'received_at':NOW.isoformat(),**{k:ready[k] for k in ('revision','source_snapshot_sha256','method_ticket_sha256')}}
    data[field]='WRONG';raw=m.encoded(data);(tmp_path/'ACK.json').write_bytes(raw)
    binding={'delivery_activation':adoption,'inspect_delivery':lambda **kw:{'recipient_ack_verified':True,
        'original':{'path':'ACK.json','sha256':m.sha(raw)}}}
    with pytest.raises(m.ProducerHold,match='ACK_REVISION_SOURCE_OR_TICKET_SHA_MISMATCH'):
        m.deliver_verified(ready,request=race,adoption=adoption,producers=binding,root=tmp_path,clock=lambda:NOW)



def test_provider_denial_stops_next_attempt_without_retry_or_redirect(monkeypatch,tmp_path):
    import urllib.error
    from runtime.local_fnb_bounded_rakuten_producer import BoundedCardProducer
    monkeypatch.delenv('CI',raising=False);monkeypatch.delenv('GITHUB_ACTIONS',raising=False)
    c,i,_,_,_=fixture(monkeypatch)
    robots=tmp_path/'robots.txt';robots.write_bytes(b'SYNTHETIC_ROBOTS')
    from runtime import local_fnb_bounded_rakuten_producer as provider
    monkeypatch.setattr(provider,'ROBOTS_SHA',m.sha(robots.read_bytes()))
    cards={'2026-11-06-R01':{'url':c['source_envelope']['artifact']['source_url'],'observed_program_raw_sha256':'a'*64}}
    transport=Mock();transport.open.side_effect=urllib.error.HTTPError(c['source_envelope']['artifact']['source_url'],403,'denied',{},None)
    monkeypatch.setattr(provider.urllib.request,'build_opener',Mock(return_value=transport))
    producer=BoundedCardProducer(root=tmp_path/'http',observed_cards=cards,robots_path=robots,actor_id='SYNTHETIC')
    with pytest.raises(m.ProducerHold,match='HTTP_FAILURE_STOP_NO_RETRY'):producer(intent=i,private_root=tmp_path,now=NOW)
    with pytest.raises(m.ProducerHold,match='REFUSAL_STOP_NO_RETRY'):producer(intent=i,private_root=tmp_path,now=NOW)
    assert transport.open.call_count==1


def test_public_ci_cannot_start_the_bounded_provider(monkeypatch,tmp_path):
    from runtime.local_fnb_bounded_rakuten_producer import BoundedCardProducer
    monkeypatch.setenv('CI','true')
    with pytest.raises(m.ProducerHold,match='PUBLIC_CI_FORBIDDEN'):
        BoundedCardProducer(root=tmp_path,observed_cards={},robots_path=tmp_path/'none',actor_id='SYNTHETIC')



def test_same_single_owner_original_is_verified_by_existing_day_supervisor(monkeypatch,tmp_path):
    from runtime import local_fnb_day_supervisor as day
    x,result,_=computed_fixture(monkeypatch,tmp_path);c,i,t,sign,o=x
    m.save_completion(tmp_path,i,c,result)
    race={**c['request']};race.pop('race_date');producers={'trust':t}
    completion=m.supervisor_completion(tmp_path,race,producers,NOW)
    assert day.verify_prediction(tmp_path,race,completion,NOW)
    assert completion['owner_count']==1 and completion['horse_count']==2 and completion['index_cells']==58
    completion['method_ticket_sha256']['EXACTA']='0'*64
    with pytest.raises(m.ProducerHold,match='SUPERVISOR_COMPLETION_MISMATCH'):
        day.verify_prediction(tmp_path,race,completion,NOW)


def test_day_callbacks_do_not_dispatch_without_real_adopted_source(monkeypatch,tmp_path):
    c,i,t,_,_=fixture(monkeypatch);c['source_envelope']=None
    producers={'source':lambda **kw:c,'trust':t}
    binding=m.day_callbacks(producers,discover_day=lambda **kw:{},verify_discovery=lambda **kw:False,
        authorize_race=lambda **kw:False,clock=lambda:NOW)
    result=binding['execute_race'](race=c['request'],private_root=tmp_path,now=NOW)
    assert result['status']=='EXECUTION_HOLD_NOT_NO_BET' and result['reason']=='ALTERNATIVE_SOURCE_SIGNED_RECEIPT_MISSING'
    assert binding['inspect_race'](race=c['request'],private_root=tmp_path,now=NOW)['status']=='NO_FORMAL_ORIGINAL'

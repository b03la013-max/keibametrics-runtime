"""Optional alternative-SOURCE/single-Owner transport for the existing R20.

No provider permission, Owner adoption, key, worker or send is created here.
The installed private producer must supply actual signed SOURCE/adoption and
an existing single-Owner executor. Legacy NAR/two-Owner execution is separate.
"""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import base64,hashlib,json,re,math

from runtime.local_fnb_r20_chat_completion import ProducerHold
from runtime import local_fnb_research_runtime as common

MODE='FNB_ALTERNATIVE_PROVIDER_SINGLE_OWNER_V1'
SOURCE_CLASS='ADMITTED_ALTERNATIVE_PROVIDER_HTTP_CARD'
SOURCE_SCHEMA='KM-FNB-ADMITTED-ALTERNATIVE-SOURCE-v1'
READY='VERIFIED_FORMAL_SINGLE_OWNER_BODY_READY_TO_RENDER'
CONSUMERS=('numerical_prediction_consumption','krs_numeric_consumption',
           'ticket_numeric_consumption','capital_numeric_consumption')
ROOT=Path(__file__).resolve().parents[1]
CONNECTION_MODULES=(
    'runtime/local_fnb_alternative_connection.py','runtime/local_fnb_adopted_single_owner.py',
    'runtime/local_fnb_bounded_rakuten_producer.py','runtime/local_fnb_r20_chat_completion.py',
    'runtime/local_race_entry.py','runtime/local_fnb_day_supervisor.py','runtime/local_fnb_finite_actor.py')


def encoded(x):return common.encoded(x)
def sha(b):return hashlib.sha256(b).hexdigest()
def compact(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def require(ok,stage,code):
    if not ok:raise ProducerHold(stage,code)
def stamp(s):return common._stamp(s)


def signed(envelope, *, phase,status,race_id,trust):
    """Use the existing LOCAL receipt verifier, with independently pinned trust."""
    require(isinstance(envelope,dict),'SOURCE' if phase=='SOURCE' else 'OWNER' if phase=='OWNER_ADOPTION' else 'FINAL',
            'ALTERNATIVE_SOURCE_SIGNED_RECEIPT_MISSING' if phase=='SOURCE' else 'FNB_OWNER_ADOPTION_RECEIPT_MISSING' if phase=='OWNER_ADOPTION' else 'SIGNED_FINAL_MISSING')
    canonical_trust(trust)
    from runtime.local_fnb_r12_historical_krs_witness import verify_envelope
    try:
        return verify_envelope(envelope,race_id=race_id,phase=phase,status=status,
            public=base64.b64decode(trust['receipt_public_key_b64'],validate=True),cfg=trust)
    except Exception as e:
        raise ProducerHold(phase,'EXISTING_LOCAL_RECEIPT_SIGNATURE_OR_BINDING_INVALID') from e


def canonical_trust(trust):
    gateway=json.loads((ROOT/'profiles/current_execution_gateway.json').read_bytes())['families']['LOCAL']
    observed=json.loads((ROOT/'evidence/family_audit_20261016/runtime_health.json').read_bytes())
    require(isinstance(trust,dict) and all(trust.get(k)==gateway[k]==observed[k]
        for k in ('receipt_signer_key_id','engine_sha256','parameter_map_sha256'))
        and trust.get('receipt_public_key_b64')==observed['receipt_public_key_b64'],
        'SOURCE','EXISTING_LOCAL_PUBLIC_TRUST_MISMATCH_NO_NEW_KEY_ALLOWED')


def source_assessment(captured, *, intent,now,trust=None):
    """Reparse real Rakuten bytes; qualifications are independently signed facts.

    Reference parsing NEVER infers ACTIVE or permission from a listed row.
    A signed receipt alone is also insufficient: its admitted exact raw,
    parser, rights original, field scope and current change/Active proof bind.
    """
    from runtime.local_fnb_rakuten_reference import parse_card
    raw=captured.get('raw');capture=captured.get('capture') or {};request=captured.get('request') or {}
    require(isinstance(raw,bytes) and bool(raw),'SOURCE','ALTERNATIVE_PROVIDER_RAW_MISSING')
    require(all(request.get(k)==intent.get(k) for k in ('venue_id','race_date','race_no'))
        and request.get('family_id')=='LOCAL','SOURCE','ALTERNATIVE_PROVIDER_REQUEST_IDENTITY_MISMATCH')
    prefix='KM-LOCAL-FNB-'+intent['race_date'].replace('-','')+'-R'+str(intent['race_no']).zfill(2)
    require(re.fullmatch(re.escape(prefix)+r'(?:-[A-Za-z0-9_]+)*',str(request.get('race_id'))),
        'SOURCE','ALTERNATIVE_PROVIDER_REQUEST_RACE_ID_INVALID')
    parsed=parse_card(raw,capture=capture,race=intent,now=now)
    cutoff=stamp(request['prediction_cutoff']);post=stamp(request['scheduled_post_at']);observed=stamp(now)
    require(stamp(capture.get('completed_at') or capture.get('captured_at'))<=observed<cutoff<post,
            'TIME','PRESTART_CUTOFF_EXPIRED_DIAGNOSTIC_REQUIRED')
    require((post-cutoff).total_seconds()==300,'TIME','ADOPTED_300_SECOND_CUTOFF_REQUIRED')
    require(stamp(parsed['race_identity']['scheduled_post_at'])==post,'SOURCE','ALTERNATIVE_PROVIDER_POST_CONFLICT')
    reasons=[]
    env=captured.get('source_envelope');artifact=None
    if not isinstance(env,dict):reasons.append('ALTERNATIVE_SOURCE_SIGNED_RECEIPT_MISSING')
    elif not trust:reasons.append('EXISTING_LOCAL_SOURCE_TRUST_NOT_CONNECTED')
    else:artifact=signed(env,phase='SOURCE',status='SOURCE_FROZEN',race_id=request['race_id'],trust=trust)
    if artifact is not None:
        require(artifact.get('schema')==SOURCE_SCHEMA and artifact.get('source_class')==SOURCE_CLASS
            and artifact.get('provider')=='RAKUTEN_KEIBA' and artifact.get('official') is False
            and artifact.get('raw_sha256')==sha(raw) and artifact.get('source_url')==parsed['source_url']
            and artifact.get('parsed_card_sha256')==compact(parsed)
            and artifact.get('source_snapshot_sha256')==compact(parsed),
            'SOURCE','ALTERNATIVE_PROVIDER_SIGNED_RAW_OR_CLASS_MISMATCH')
        rights=captured.get('permission_original');permission=artifact.get('provider_permission') or {}
        if not (isinstance(rights,bytes) and rights and sha(rights)==permission.get('original_sha256')
                and permission.get('provider')=='RAKUTEN_KEIBA' and permission.get('actor_id')==captured.get('actor_id')
                and all(permission.get(k) is True for k in ('retrieval_method_authorized','private_retention_authorized','cloud_processing_authorized'))
                and stamp(permission['effective_from'])<=stamp(parsed['captured_at'])<=observed<stamp(permission['effective_until'])):
            reasons.append('ALTERNATIVE_PROVIDER_PERMISSION_ORIGINAL_UNVERIFIED')
        changes=captured.get('current_state_original');state=artifact.get('current_state') or {}
        if not (isinstance(changes,bytes) and changes and sha(changes)==state.get('original_sha256')
                and state.get('latest_changes_verified') is True and state.get('complete_declared_universe') is True
                and state.get('request_race_id')==request['race_id'] and state.get('card_raw_sha256')==sha(raw)
                and stamp(parsed['captured_at'])<=stamp(state['observed_at'])<=stamp(artifact['source_freeze_at'])<=observed):
            reasons.append('ALTERNATIVE_PROVIDER_CURRENT_CHANGES_AND_ACTIVE_UNVERIFIED')
        else:
            rows=state.get('runners') or [];by={str(r.get('horse_no')):r for r in rows}
            card={r['runner_id']:r for r in parsed['runners']}
            require(len(by)==len(rows) and set(by)==set(card),'SOURCE','ALTERNATIVE_PROVIDER_DECLARED_UNIVERSE_CONFLICT')
            for rid,row in by.items():
                require(row.get('name')==card[rid]['name'] and row.get('status') in ('ACTIVE','CANCELLED','EXCLUDED')
                    and row.get('current_jockey')==card[rid]['current_jockey']
                    and row.get('current_load')==card[rid]['current_load'],'SOURCE','ALTERNATIVE_PROVIDER_CURRENT_RUNNER_CONFLICT')
            active=sorted((r for r in by if by[r]['status']=='ACTIVE'),key=int)
            require(len(active)>=2 and artifact.get('active_runner_ids')==active
                and artifact.get('active_universe_sha256')==compact([by[r] for r in active]),
                'SOURCE','ALTERNATIVE_PROVIDER_ACTIVE_SET_SHA_MISMATCH')
        admission=artifact.get('field_admission') or {}
        expected=('identity','scheduled_post_at','runner_number_name','frame','jockey_load',
                  'current_changes','active_status','current_body_weight','weather_going','dated_history')
        if not (admission.get('profile_adoption_verified') is True and admission.get('consumer_scope')=='FNB_FORMAL_FULL29_STATIC_KRS_TICKET'
                and set(admission.get('admitted_fields') or [])==set(expected)
                and re.fullmatch('[a-f0-9]{64}',str(admission.get('decision_sha256')))
                and stamp(admission['effective_from'])<=stamp(artifact['source_freeze_at'])<=observed<stamp(admission['effective_until'])):
            reasons.append('ALTERNATIVE_PROVIDER_FIELD_ADMISSION_NOT_ADOPTED')
        require(0<=(observed-stamp(artifact['source_freeze_at'])).total_seconds()<=600
            and stamp(parsed['captured_at'])<=stamp(artifact['source_freeze_at'])<cutoff,
            'SOURCE','ALTERNATIVE_PROVIDER_SOURCE_FRESHNESS_NOT_PROVEN')
    else:
        reasons+=['ALTERNATIVE_PROVIDER_PERMISSION_ORIGINAL_UNVERIFIED',
            'ALTERNATIVE_PROVIDER_CURRENT_CHANGES_AND_ACTIVE_UNVERIFIED','ALTERNATIVE_PROVIDER_FIELD_ADMISSION_NOT_ADOPTED']
    return {'status':'ADMITTED_ALTERNATIVE_PROVIDER_SOURCE' if not reasons else 'SOURCE_HOLD_NOT_NO_BET',
        'source_admitted':not reasons,'first_error':reasons[0] if reasons else None,'reasons':reasons,
        'race_id':request['race_id'],'request':deepcopy(request),'parsed':parsed,'raw_sha256':sha(raw),
        'source_envelope':deepcopy(env),'artifact':deepcopy(artifact),'raw_reparsed':True,'provider':'RAKUTEN_KEIBA',
        'raw_qualification_is_not_inferred_from_HTTP':True,'new_KRS':0,'formal_final':False,'recipient_ACK':False}


def owner_adoption(envelope, *, request,source,trust,now):
    from runtime import local_fnb_exact_orientation_research as exact
    common._pinned(ROOT/'runtime/local_fnb_context_static_candidate.py',common.MODEL_SHA)
    common._pinned(ROOT/'profiles/local_fnb_context_static_candidate_v0.1_20261103.json',common.MODEL_PROFILE_SHA)
    out=signed(envelope,phase='OWNER_ADOPTION',status='APPROVED',race_id=request['race_id'],trust=trust)
    require(out.get('connection_module_sha256')=={name:sha((ROOT/name).read_bytes()) for name in CONNECTION_MODULES},
        'OWNER','FNB_ADOPTED_CONNECTION_CODE_DRIFT')
    require(out.get('venue_id')=='FNB' and out.get('family_id')=='LOCAL' and out.get('owner_count')==1
        and out.get('model_code_sha256')==common.MODEL_SHA and out.get('model_profile_sha256')==common.MODEL_PROFILE_SHA
        and all(out.get(k) is True for k in CONSUMERS),'OWNER','FNB_OWNER_AND_FOUR_CONSUMER_SCOPE_NOT_ADOPTED')
    require(out.get('selection_profile')==exact.PROFILE and out.get('selection_module_sha256')==exact.MODULE_SHA
        and out.get('selection_profile_sha256')==sha(exact.PROFILE_PATH.read_bytes())
        and out.get('alternative_source_class')==SOURCE_CLASS,'SELECTION','FNB_EXACT_SELECTION_OR_SOURCE_SCOPE_NOT_ADOPTED')
    require(request['race_no'] in (out.get('races_by_date') or {}).get(request['race_date'],[])
        and stamp(out['effective_from'])<=stamp(now)<stamp(out['effective_until'])
        and stamp(out['effective_from'])<stamp(request['prediction_cutoff']),
        'OWNER','FNB_OWNER_DATED_EFFECTIVE_SCOPE_MISMATCH')
    require(out.get('current_authority')=='KM-FAMILY-CURRENT-AUTHORITY-20261012-R51'
        and out.get('source_admission_decision_sha256')==source['field_admission']['decision_sha256']
        and out.get('actual_purchase_authorized') is False and out.get('registered_OOS_increment')==0,
        'OWNER','FNB_OWNER_CURRENT_AUTHORITY_OR_ADMISSION_MISMATCH')
    return out


def _original(root,path,raw):
    p=Path(root)/path;common._immutable(p,raw)
    require(p.read_bytes()==raw,'SAVE','PRIVATE_ORIGINAL_READBACK_SHA_MISMATCH')
    return {'path':path,'sha256':sha(raw),'bytes':len(raw)}


def _index_path(intent):
    return 'formal_single_owner_intents/'+intent['race_date']+'-R'+str(intent['race_no']).zfill(2)+'/completion.json'


def save_completion(root,intent,captured,result):
    serial=deepcopy(captured)
    for key in ('raw','permission_original','current_state_original'):
        serial[key]={'base64':base64.b64encode(serial[key]).decode()}
    folder='formal_single_owner/'+captured['request']['race_id']+'/'
    index={'captured_original':_original(root,folder+'captured_source.json',encoded(serial)),
        'execution_original':_original(root,folder+'complete_execution.json',encoded(result))}
    _original(root,_index_path(intent),encoded(index))


def read_completion(root,intent,trust,now):
    from runtime.local_fnb_day_supervisor import original
    path=Path(root)/_index_path(intent)
    if not path.exists():return None
    require(not path.is_symlink(),'READBACK','SINGLE_OWNER_COMPLETION_INDEX_SYMLINK_REJECTED')
    index=json.loads(path.read_bytes())
    captured=json.loads(original(Path(root),index['captured_original']))
    for key in ('raw','permission_original','current_state_original'):
        captured[key]=base64.b64decode(captured[key]['base64'],validate=True)
    result=json.loads(original(Path(root),index['execution_original']))
    # Revalidate signed prestart chronology at the actual signed freeze; the
    # new readback/send clock stays current and can never extend the cutoff.
    frozen=result['final_envelope']['artifact']['final_freeze_at']
    require(stamp(frozen)<=stamp(now),'TIME','SINGLE_OWNER_SAVED_FINAL_IN_FUTURE')
    source=source_assessment(captured,intent=intent,now=stamp(frozen),trust=trust)
    require(source['source_admitted'],'SOURCE',source['first_error'])
    request=source['request']
    require(not intent.get('race_id') or request['race_id']==intent['race_id'],
        'REVISION','SINGLE_OWNER_DISCOVERY_REVISION_DIFFERS_FROM_FROZEN_ORIGINAL')
    adoption=owner_adoption(captured['owner_adoption_envelope'],request=request,source=source['artifact'],trust=trust,now=stamp(frozen))
    verified=verify_result(result,request=request,source=source,adoption=adoption,trust=trust,root=root,
        now=stamp(frozen),captured=captured)
    verified.update(new_prediction_executed=False,source='EXISTING_FORMAL_FROZEN_ORIGINAL_READBACK',readback_at=stamp(now).isoformat())
    return verified,request,adoption


def run(intent,root,producers, *, clock):
    """Connect a single real Owner without changing the legacy B/C contract."""
    observed=clock()
    previous=read_completion(root,intent,producers.get('trust'),observed)
    if previous:
        verified,request,adoption=previous
        return deliver_verified(verified,request=request,adoption=adoption,producers=producers,root=root,clock=clock)
    require(callable(producers.get('source')),'SOURCE_PRODUCER','SOURCE_PRODUCER_NOT_CONNECTED')
    captured=producers['source'](intent=deepcopy(intent),private_root=root,now=observed)
    trust=producers.get('trust');assessment=source_assessment(captured,intent=intent,now=clock(),trust=trust)
    request=assessment['request'];race_id=request['race_id']
    # Preserve lawful Raw and exact admission diagnosis before a failed gate.
    assessment_copy={k:v for k,v in assessment.items() if k not in ('source_envelope','artifact')}
    prefix='source_attempts/'+race_id+'/'+sha(encoded(captured['capture']))+'/'
    _original(root,prefix+'original_provider_card.html',captured['raw'])
    _original(root,prefix+'assessment.json',encoded(assessment_copy))
    require(assessment['source_admitted'],'SOURCE',assessment['first_error'])
    adoption=owner_adoption(producers.get('owner_adoption_envelope'),request=request,
        source=assessment['artifact'],trust=trust,now=clock())
    require(callable(producers.get('execute_single_owner')),'OWNER','ADOPTED_SINGLE_OWNER_EXECUTOR_NOT_CONNECTED')
    require(clock()<stamp(request['prediction_cutoff']),'TIME','PRESTART_CUTOFF_EXPIRED_DIAGNOSTIC_REQUIRED')
    # The claim persists before invoking an Engine-capable executor. A partial
    # or ambiguous run is reconciled by real originals, never blindly rerun.
    claim=Path(root)/'single_owner_claims'/race_id/'claim.json'
    require(not claim.exists(),'EXECUTION','SINGLE_OWNER_CLAIM_EXISTS_READBACK_REQUIRED')
    _original(root,str(claim.relative_to(root)),encoded({'race_id':race_id,'source_receipt_sha256':captured['source_envelope']['receipt_sha256'],
        'owner_adoption_sha256':producers['owner_adoption_envelope']['receipt_sha256'],'claimed_at':clock().isoformat()}))
    execution_source=deepcopy(captured)
    execution_source.update(trust=deepcopy(trust),owner_adoption_envelope=deepcopy(producers['owner_adoption_envelope']))
    result=producers['execute_single_owner'](request=deepcopy(request),admitted_source=deepcopy(assessment),
        adopted_owner=deepcopy(adoption),captured_source=execution_source,private_root=root,now=clock())
    verified=verify_result(result,request=request,source=assessment,adoption=adoption,trust=trust,root=root,now=clock(),captured=execution_source)
    save_completion(root,intent,execution_source,result)
    verified['new_prediction_executed']=True
    return deliver_verified(verified,request=request,adoption=adoption,producers=producers,root=root,clock=clock)


def deliver_verified(verified, *, request,adoption,producers,root,clock,allow_mutation=True):
    """Reuse the existing supervisor's actual-original/recipient ACK check.

    A returned send status is deliberately ignored. An immutable delivery claim
    survives an ambiguous send so a retry inspects the original, never resends.
    """
    from runtime import local_fnb_day_supervisor as day
    activation=producers.get('delivery_activation')
    if not activation:
        return {**verified,'delivery_status':'RECIPIENT_TRANSPORT_ACTIVATION_NOT_CONNECTED'}
    require(adoption.get('delivery_recipient_id')==activation.get('delivery_recipient_id')
        and adoption.get('delivery_route_id')==activation.get('delivery_route_id')
        and adoption.get('delivery_authorized') is True,'DELIVERY','FNB_RECIPIENT_ROUTE_NOT_IN_ADOPTED_SCOPE')
    path=Path(root)/'single_owner_delivery'/request['race_id']/'checkpoint.json'
    if path.exists():cell=json.loads(path.read_bytes())
    else:cell={}
    cell['completion']={'body_original':verified['originals']['body'],
        'prediction_freeze_at':verified['final_freeze_at'],'source_snapshot_sha256':verified['source_snapshot_sha256']}
    save=lambda:day.put(path,cell)
    binding=dict(producers)
    inspect=producers.get('inspect_delivery')
    if callable(inspect):
        def inspect_bound(**kw):
            receipt=inspect(**kw)
            if receipt.get('recipient_ack_verified') is True:
                data=json.loads(day.original(Path(root),receipt['original']))
                require(data.get('revision')==verified['revision']
                    and data.get('source_snapshot_sha256')==verified['source_snapshot_sha256']
                    and data.get('method_ticket_sha256')==verified['method_ticket_sha256']
                    and data.get('owner_model_sha256')==common.MODEL_SHA
                    and data.get('owner_profile_sha256')==common.MODEL_PROFILE_SHA,
                    'DELIVERY','RECIPIENT_ACK_REVISION_SOURCE_OR_TICKET_SHA_MISMATCH')
            return receipt
        binding['inspect_delivery']=inspect_bound
    day._deliver(binding,activation,Path(root),request,cell,clock,save,allow_mutation=allow_mutation)
    # Re-read after send. _deliver itself validates recipient/original SHA/time.
    day._deliver(binding,activation,Path(root),request,cell,clock,save,allow_mutation=False)
    save();ack=cell.get('status')=='DELIVERED_PRESTART'
    return {**verified,'recipient_delivery_ack':ack,'delivery_status':'DELIVERED_PRESTART' if ack else 'DELIVERY_PENDING_OR_ACK_UNVERIFIED',
        'delivery_checkpoint':str(path.relative_to(root)),'natural_delivery_verified':False}


def verify_result(result, *, request,source,adoption,trust,root,now,captured):
    """A callback return cannot assert Formal/Delivery without real originals."""
    from runtime.minimum_efficient_coverage import validate_mec_plan
    from runtime.jra_ticket_tree_renderer import render_ticket_tree
    final=signed(result.get('final_envelope'),phase='FINAL',status='PASS',race_id=request['race_id'],trust=trust)
    require(final.get('race_id')==request['race_id'] and final.get('owner_count')==1
        and final.get('actual_purchase') is False and final.get('registered_OOS_increment')==0
        and final.get('model_code_sha256')==common.MODEL_SHA
        and final.get('source_receipt_sha256')==source['source_envelope']['receipt_sha256']
        and final.get('active_universe_sha256')==source['artifact']['active_universe_sha256'],
        'FINAL','SINGLE_OWNER_FINAL_SOURCE_MODEL_BINDING_MISMATCH')
    require(stamp(source['artifact']['source_freeze_at'])<=stamp(final['static_freeze_at'])
        <=stamp(final['final_freeze_at'])<=stamp(now)<stamp(request['prediction_cutoff'])
        and stamp(adoption['effective_from'])<=stamp(final['static_freeze_at']),
        'TIME','SINGLE_OWNER_FORMAL_FREEZE_NOT_PRESTART')
    num=result.get('numerical') or {};ids=set(source['artifact']['active_runner_ids'])
    require({str(r['runner_id']) for r in num.get('runners',[])}==ids
        and len(num.get('runners',[]))==len(ids) and num.get('strict_full_numerical_ready') is True
        and len(num.get('required_indices',[]))==29,'NUMERICAL','SINGLE_OWNER_FULL29_ACTIVE_NOT_PROVEN')
    for row in num['runners']:
        require(set(row.get('canonical_components',{}))==set(num['required_indices'])
            and all(c.get('terminal_status') in ('CALCULATED','RULED-NEUTRAL')
                and isinstance(c.get('value'),(float,int)) and math.isfinite(c['value'])
                for c in row['canonical_components'].values()),
            'NUMERICAL','SINGLE_OWNER_FULL29_TERMINAL_INCOMPLETE')
    requested=result.get('krs_requested_input');executed=result.get('krs_execution_input');output=result.get('krs_output')
    require(isinstance(requested,dict) and isinstance(executed,dict) and isinstance(output,dict)
        and common.engine_input_projection(requested)==common.engine_input_projection(executed),
        'KRS','SINGLE_OWNER_KRS_INPUT_REVISION_MISMATCH')
    common._verify_output(output,requested)
    require({str(r['horse_no']) for r in requested['horses']}==ids
        and requested['race']['date'].replace('/','-')==request['race_date']
        and requested['race']['race_no']==request['race_no'],
        'KRS','SINGLE_OWNER_KRS_SOURCE_ACTIVE_RACE_MISMATCH')
    for k,v in [('KRS_input_sha256',sha(encoded(executed))),('KRS_output_sha256',sha(encoded(output))),
                ('numerical_sha256',sha(encoded(num)))]:
        require(final.get(k)==v,'FINAL','SINGLE_OWNER_FINAL_NUMERICAL_KRS_SHA_MISMATCH')
    # Recompute only deterministic arithmetic/Static/Selection from the exact
    # signed Raw and existing KRS output. Never rerun the Engine on readback.
    from runtime.local_fnb_adopted_single_owner import materialize_inputs,render_body
    from runtime.local_fnb_context_static_candidate import build_context,predict
    from runtime.local_fnb_csv_research_runtime import _bridge_aliases
    from runtime import local_fnb_semantic_closure as semantic
    from runtime import local_fnb_exact_orientation_research as exact
    loaded,expected_num,packet=materialize_inputs(captured,request,source,generated_at=result['materialized_at'])
    require(expected_num==num and packet==result.get('observations'),
        'NUMERICAL','SINGLE_OWNER_RAW_TO_FULL29_REPLAY_MISMATCH')
    context=build_context(packet,generated_at=result['context']['generated_at'])
    upstream,_=common.build_upstream(_bridge_aliases(num),numerical_sha256=sha(encoded(num)))
    prediction=predict(context,frozen_at=final['static_freeze_at'],upstream_krs_input=upstream)
    require(prediction['source_snapshot_sha256']==source['artifact']['source_snapshot_sha256'],
        'SOURCE','SINGLE_OWNER_STATIC_SOURCE_SNAPSHOT_MISMATCH')
    require(context==result['context'] and prediction==result['prediction'] and requested==prediction['PRE_KRS_input'],
        'OWNER','SINGLE_OWNER_FROZEN_STATIC_OR_PRE_KRS_REPLAY_MISMATCH')
    selected_at=result['selection_review']['selected_at']
    require(stamp(final['static_freeze_at'])<=stamp(selected_at)<=stamp(final['final_freeze_at']),
        'TIME','SINGLE_OWNER_SELECTION_NOT_WITHIN_FREEZE')
    freeze={'profile':exact.PROFILE,'module_sha256':exact.MODULE_SHA,'profile_sha256':sha(exact.PROFILE_PATH.read_bytes()),
        'frozen_at':adoption['effective_from'],'formal_adoption_receipt_sha256':captured['owner_adoption_envelope']['receipt_sha256']}
    s2=semantic.research_unknown_path_protection(prediction,evaluated_at=selected_at)
    review=exact.evaluate(prediction,context,output,s2,freeze=freeze,evaluated_at=selected_at)
    full=exact.construct(prediction,context,output,review,s2,freeze=freeze,evaluated_at=selected_at)
    require(freeze==result['selection_freeze'] and s2==result['base_S2'] and review==result['selection_review']
        and full==result['full_semantic_portfolio'] and final.get('selection_decision_sha256')==sha(encoded(review)),
        'SELECTION','SINGLE_OWNER_EXACT_SELECTION_REPLAY_MISMATCH')
    methods=result.get('methods') or {};require(set(methods)=={'EXACTA','TRIO','TRIFECTA'},'TICKET','SINGLE_OWNER_THREE_METHODS_MISSING')
    for method,row in methods.items():
        tickets=row['tickets'];plans=row.get('strict_MEC_plans') or []
        proposed=full['methods'][method]['tickets']
        exact_plans=([r['strict_plan'] for r in full['strict_MEC_exact_pair_plans']] if method=='TRIFECTA' else
            [r['canonical_plan'] for r in s2['known_pair_scoped_subplans']])
        require(row.get('full_semantic_tickets')==proposed and plans==exact_plans,
            'MEC','SINGLE_OWNER_MATERIAL_MEC_REQUEST_REPLAY_MISMATCH')
        require(bool(plans) or not tickets,'MEC','SINGLE_OWNER_MEC_RECEIPT_MISSING')
        expected={}
        for plan in plans:
            validate_mec_plan(plan)
            require(plan.get('material_coverage_ratio')==1 and not plan.get('uncovered_active_w_heads')
                and not plan.get('orphan_thirds'),'MEC','SINGLE_OWNER_STRICT_MEC_NOT_CLOSED')
            for ticket in plan['tickets']:
                if ticket['bet_type']==method:expected[tuple(ticket['selection'])]=ticket['stake']
        from runtime.capital_policy import resolve_capital_policy
        capital=resolve_capital_policy(semantic.original_request(prediction), {'minimum_required_capital':sum(expected.values()),
            'profile':exact.PROFILE,'sha256':sha(encoded(proposed)),'material_coverage_ratio':1.0})
        require(capital==row['capital_policy'],'CAPITAL','SINGLE_OWNER_EXISTING_CAPITAL_DECISION_CHANGED')
        selected=expected if capital['decision']=='EXECUTE_FULL_MEC' else {}
        require(len(tickets)==len({tuple(t['selection']) for t in tickets})
            and {tuple(t['selection']):t['stake'] for t in tickets}==selected,
            'TICKET','SINGLE_OWNER_CANONICAL_ARRAY_DIFFERS_FROM_STRICT_MEC')
        require(all(t['bet_type']==method and t['stake']%100==0 and t['stake']>0 for t in tickets),
            'TICKET','SINGLE_OWNER_TICKET_TYPE_STAKE_INVALID')
        tree=render_ticket_tree({'final_ticket':{'tickets':tickets,'no_bet':not tickets},
            'capital_policy_decision':row['capital_policy'],'final_prediction_package':{'validation_status':'UNVALIDATED'}})
        require(tree['canonical_roundtrip_verified'] and tree['text']==row['canonical_tree'],
            'TICKET','SINGLE_OWNER_CANONICAL_TREE_MISMATCH')
        require(final.get('method_ticket_sha256',{}).get(method)==sha(encoded(tickets)),
            'FINAL','SINGLE_OWNER_SIGNED_TICKET_SHA_MISMATCH')
    require(render_body(num,request,prediction,output,executed,review,methods,loaded,captured)==result.get('body'),
        'DELIVERY_BODY','SINGLE_OWNER_FULL_BODY_CANONICAL_CONTENT_MISMATCH')
    body=result.get('body');require(isinstance(body,str) and body and final.get('body_sha256')==sha(body.encode()),
        'FINAL','SINGLE_OWNER_SIGNED_FULL_BODY_SHA_MISMATCH')
    # Exact signed body identity is necessary; the installed executor must also
    # provide the canonical existing full-body/29/Role content verifier receipt.
    content=result.get('full_body_verification') or {}
    require(content.get('all29_cells')==len(ids)*29 and content.get('all_roles_included') is True
        and content.get('all_selected_tickets_included') is True and content.get('body_sha256')==sha(body.encode()),
        'DELIVERY_BODY','SINGLE_OWNER_COMPLETE_BODY_VERIFICATION_MISSING')
    for row in num['runners']:
        require(str(row['runner_id']) in body and all(index in body and str(c['value']) in body
            for index,c in row['canonical_components'].items()),'DELIVERY_BODY','SINGLE_OWNER_ALL29_TEXT_MISSING')
    require(all(row['canonical_tree'] in body for row in methods.values()),
        'DELIVERY_BODY','SINGLE_OWNER_CANONICAL_TREE_BODY_MISSING')
    folder='formal_single_owner/'+request['race_id']+'/'
    proofs={'body':_original(root,folder+'complete_body.md',body.encode()),
        'final_envelope':_original(root,folder+'final_receipt_envelope.json',encoded(result['final_envelope']))}
    return {'status':READY,'profile':MODE,'race_id':request['race_id'],'owner_count':1,
        'independent_BC':False,'formal_final_proven':True,'body':body,'body_sha256':sha(body.encode()),
        'originals':proofs,'recipient_delivery_ack':False,'natural_delivery_verified':False,
        'final_freeze_at':final['final_freeze_at'],
        'revision':request['race_id'],'method_ticket_sha256':final['method_ticket_sha256'],
        'selection_decision_sha256':final['selection_decision_sha256'],
        'source_snapshot_sha256':source['artifact']['source_snapshot_sha256'],'registered_oos_increment':0,
        'actual_purchase':False,'delivery_status':'FORMAL_ORIGINAL_READY_TRANSPORT_AND_ACK_SEPARATE'}



def race_intent(race):
    # Existing discovery rows carry their dated identity in Race ID; a
    # redundant race_date field is optional in the unchanged day contract.
    match=re.fullmatch(r'KM-LOCAL-FNB-(\d{8})-R(\d{2})(?:-[A-Za-z0-9_]+)*',str(race.get('race_id')))
    require(match is not None and int(match[2])==race.get('race_no'),
        'REVISION','SINGLE_OWNER_DISCOVERY_RACE_IDENTITY_INVALID')
    value=match[1];date=value[:4]+'-'+value[4:6]+'-'+value[6:]
    require(not race.get('race_date') or race['race_date']==date,'REVISION','SINGLE_OWNER_DISCOVERY_DATE_CONFLICT')
    return {'venue_id':'FNB','race_date':date,'race_no':race['race_no'],'race_id':race['race_id']}


def supervisor_completion(root,race,producers,now):
    """Read the real signed single-Owner original for the existing Actor."""
    intent=race_intent(race)
    loaded=read_completion(root,intent,producers.get('trust'),now)
    if not loaded:return {'status':'NO_FORMAL_ORIGINAL'}
    verified,request,adoption=loaded
    require(request['race_id']==race['race_id'] and stamp(request['prediction_cutoff'])==stamp(race['prediction_cutoff']),
        'REVISION','SINGLE_OWNER_DISCOVERY_SOURCE_CUTOFF_MISMATCH')
    from runtime import local_fnb_day_supervisor as day
    index=json.loads((Path(root)/_index_path(intent)).read_bytes())
    computed=json.loads(day.original(Path(root),index['execution_original']))
    stages={k:{'status':'VERIFIED'} for k in day.STAGES[:8]}
    stages['SOURCE']['source_snapshot_sha256']=verified['source_snapshot_sha256']
    stages['KRS'].update(engine_sha256=common.ENGINE_SHA,map_sha256=common.MAP_SHA,run_count=5000,seed=1)
    selected=sum(len(m['tickets']) for m in computed['methods'].values())
    # Separate alternatives remain separate; this is only an integrity count.
    stages['TICKET'].update(ticket_count=selected,alternatives_not_combined=True)
    return {**verified,'status':READY,'classification':'FORMAL_FNB_SINGLE_OWNER_PRESTART',
        'prediction_cutoff':request['prediction_cutoff'],'prediction_freeze_at':verified['final_freeze_at'],
        'source_freeze_at':computed['prediction']['source_freeze_at'],'model_code_sha256':common.MODEL_SHA,
        'horse_count':len(computed['numerical']['runners']),'index_cells':29*len(computed['numerical']['runners']),
        'computed_no_bet':selected==0,'stages':stages,'body_original':verified['originals']['body'],
        'method_ticket_sha256':verified['method_ticket_sha256'],'trust':deepcopy(producers.get('trust'))}


def verify_supervisor_result(root,race,result,now):
    actual=supervisor_completion(root,race,{'trust':result.get('trust')},now)
    require({k:v for k,v in actual.items() if k!='readback_at'}=={k:v for k,v in result.items() if k!='readback_at'}
        and stamp(result['readback_at'])<=stamp(now),'READBACK','SINGLE_OWNER_SUPERVISOR_COMPLETION_MISMATCH')
    return True


def day_callbacks(producers, *, discover_day,verify_discovery,authorize_race,clock):
    """Connect real existing callbacks. Creates no activation, lease or Worker.

    Caller must supply independently qualified discovery/authorization and a
    pinned dated activation under the unchanged existing finite-Actor rules.
    """
    require(all(callable(c) for c in (discover_day,verify_discovery,authorize_race)),
        'ACTOR','QUALIFIED_DAY_DISCOVERY_AND_AUTHORIZATION_NOT_CONNECTED')
    def inspect_race(*,race,private_root,now):return supervisor_completion(private_root,race,producers,now)
    def execute_race(*,race,private_root,now):
        intent=race_intent(race)
        try:
            result=run(intent,private_root,producers,clock=clock)
            return {'status':result['status'],'run_id':race['race_id']}
        except ProducerHold as error:
            return {'status':'EXECUTION_HOLD_NOT_NO_BET','first_failed_stage':error.stage,'reason':error.code}
    def inspect_delivery(*,race,completion,private_root,now):
        intent=race_intent(race)
        previous=read_completion(private_root,intent,producers.get('trust'),now)
        if not previous:return {}
        verified,request,adoption=previous
        status=deliver_verified(verified,request=request,adoption=adoption,producers=producers,
            root=private_root,clock=lambda:now,allow_mutation=False)
        if not status.get('recipient_delivery_ack'):return {}
        path=Path(private_root)/status['delivery_checkpoint']
        return json.loads(path.read_bytes())['delivery']
    # Delivery stays in run()/deliver_verified(), where the stronger new
    # Revision/Source/Ticket ACK checks reuse the existing supervisor primitive.
    return {'discover_day':discover_day,'verify_discovery':verify_discovery,'authorize_race':authorize_race,
        'inspect_race':inspect_race,'execute_race':execute_race,'inspect_delivery':inspect_delivery}

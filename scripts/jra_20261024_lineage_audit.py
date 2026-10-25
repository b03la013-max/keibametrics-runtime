"""Retrospective saved-input SOURCE/Feature/BVI/OOS audit, never a new prediction."""
from __future__ import annotations

import argparse
import base64
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile

CODE_ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(CODE_ROOT/'runtime'),str(CODE_ROOT/'runtime/jra_source_runtime')]
from jra_horse_history import parse_horse_history
from jra_source_runtime.jra_race_card_detail import parse_race_card_detail
from jra_krs_input_builder_production import build_krs_input
from jra_official_fact_evaluator_production import _jra_official_class_strength, official_production_observations
from jra_registered_common import parse_workout


def sha(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def raw(snapshot):
    content=gzip.decompress(base64.b64decode(snapshot['raw_gzip_b64']))
    if hashlib.sha256(content).hexdigest()!=snapshot['raw_sha256']:
        raise ValueError('ARCHIVED_RAW_HASH_MISMATCH')
    return content


def load_race(root,rid):
    formal=root/'runtime/requests'/(rid+'-LIVE-R1-FORMAL.json')
    if formal.exists():
        data=formal.read_bytes();req=json.loads(data)
        return formal,data,req,req['source_snapshot'],'FORMAL_REQUEST'
    path=root/'runtime/jra_no_bet_terminals'/(rid+'-LIVE-R1.json')
    data=path.read_bytes();terminal=json.loads(data)
    req=terminal['failure_report']['prepared_numerical_request']
    envs=list((root/'runtime/executions'/(rid+'-LIVE-R1')/'SOURCE/runs').glob('*/source_receipt_envelope.json'))
    matched=[json.loads(x.read_text())['artifact'] for x in envs]
    source=next(x for x in matched if x['source_snapshot_sha256']==terminal['source_snapshot_sha256'])
    return path,data,req,source,'AKI_NO_BET'


def audit(root):
    counts=Counter();by_venue={};races=[];all_bvi=[];oos=[]
    protected={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
               for p in (root/'runtime/final_artifacts').glob('KM-JRA-*-20261024-R*.json')}
    plan=json.loads((root/'runtime/jra_race_day_plan/2026-10-24.json').read_text())['forward_oos_preregistration']
    for venue in ['TKY','KYO','NGT']:
        venue_counts=Counter()
        for number in range(1,13):
            rid=f'KM-JRA-{venue}-20261024-R{number:02d}'
            input_path,input_bytes,req,source,kind=load_race(root,rid)
            snapshots={x['snapshot_sha256']:x for x in source['sources']}
            detail=source['jra_official_race_card_detail'];snapshot=snapshots[detail['source_snapshot_sha256']]
            parsed=parse_race_card_detail(raw(snapshot),snapshot['content_type'])
            old_rows={str(x['runner_id']):x for x in detail['runners']}
            new_rows={str(x['runner_id']):x for x in parsed['runners']}
            if set(old_rows)!=set(new_rows):raise ValueError('REPARSED_UNIVERSE_CHANGED:'+rid)
            source_sha=source.get('source_snapshot_sha256') or sha(source)
            # A derived parser view for retrospective diagnosis only. Never save
            # this as a SOURCE or assign it a historical Freeze/signature.
            parser_view=deepcopy(source);parser_view['source_snapshot_sha256']=source_sha
            registry=json.loads((CODE_ROOT/'mapping/jra_evidence_feature_rule_registry_v1.3_20261010.json').read_text())
            before_observations=official_production_observations(parser_view,registry)
            row_counts=Counter();grade_recoveries=[];runners=[]
            for r in req['runners']:
                runner=str(r['runner_id']);old=old_rows[runner];new=new_rows[runner]
                row_counts['runners']+=1
                row_counts['index_cells']+=len(r['canonical_components'])
                row_counts['frame_recovered']+=old.get('frame_no') is None and new.get('frame_no') is not None
                row_counts['rider_label_corrected']+=old.get('jockey')!=new.get('jockey')
                history=(source.get('jra_official_horse_history') or {}).get('runners',{}).get(runner,{})
                hs=snapshots.get(history.get('source_snapshot_sha256'))
                grade_count=0
                if hs:
                    reparsed=parse_horse_history(raw(hs),hs['content_type'])
                    if len(history.get('runs',[]))!=len(reparsed['runs']):raise ValueError('HISTORY_ROW_COUNT_CHANGED')
                    for before,after in zip(history.get('runs',[]),reparsed['runs']):
                        if {k:v for k,v in before.items() if k!='race_name'}!={k:v for k,v in after.items() if k!='race_name'}:
                            raise ValueError('HISTORY_NON_GRADE_FACT_CHANGED')
                        if _jra_official_class_strength(before.get('race_name')) is None and _jra_official_class_strength(after.get('race_name')) is not None:
                            grade_count+=1
                            if number==11 and venue=='KYO' and len(grade_recoveries)<30:
                                grade_recoveries.append({'runner_id':runner,'date':before['date'],'before':before['race_name'],'after':after['race_name'],'raw_sha256':hs['raw_sha256']})
                    parser_view['jra_official_horse_history']['runners'][runner]['runs']=reparsed['runs']
                row_counts['history_grade_recovered']+=grade_count
                cc=r['canonical_components'];bvi=cc['BVI'];parts=bvi.get('components') or []
                status=('MEASURED_PLUS_DCR' if bvi.get('adjustments') else 'MEASURED') if parts else 'DCR_ONLY'
                venue_counts['bvi_'+status]+=1
                features=r.get('evidence_features') or {}
                refs=sorted({ref for p in parts for ref in p.get('evidence_refs',[])})
                components=[]
                for p in parts:
                    fact=p.get('source_fact','');offspring=re.search(r'offspring=(\d+)',fact);runs=re.search(r'runs=(\d+)',fact)
                    components.append({'feature':p.get('feature'),'rule_id':features.get(p.get('feature'),{}).get('rule_id'),
                        'reported_offspring_count':int(offspring[1]) if offspring else None,
                        'run_count':int(runs[1]) if runs else None,
                        'denominator_identity_kind':'NAME_SIRE_DAM_SURROGATE_NOT_ACCEPTED_PERMANENT_ID',
                        'independence_qualification':'NOT_PROVEN_BY_PERMANENT_HORSE_AND_RACE_IDS',
                        'source_authority':features.get(p.get('feature'),{}).get('source_authority'),
                        'rule_authority':features.get(p.get('feature'),{}).get('rule_authority'),
                        'source_fact':fact,'category':p.get('category'),'weight':p.get('weight')})
                target_distance=(source.get('jra_race_context') or {}).get('distance_m')
                target_surface=(source.get('jra_race_context') or {}).get('surface')
                target_going=(source.get('jra_race_context') or {}).get('going')
                runs=history.get('runs') or old.get('recent_runs') or []
                trace={f:{'feature_present':f in features,'source_fact':features.get(f,{}).get('source_fact'),
                           'observation_count':features.get(f,{}).get('observation_count'),
                           'indices_using':sorted(k for k,c in cc.items() if any(p.get('feature')==f for p in c.get('components',[])))}
                       for f in ['same_distance_fit','distance_fit','surface_fit','going_fit','class_performance','opponent_strength','weight_load_fit','jockey_quality']}
                runner_row={'race_id':rid,'venue':venue,'runner_id':runner,'name':r.get('name'),'bvi_class':status,'bvi_value':bvi['value'],
                    'bvi_sha256':sha(bvi),'bvi_observed_weight':bvi.get('coverage_weight'),'bvi_components':components,
                    'bvi_evidence_refs':refs,'horse_registry_id':r.get('official_horse_id'),
                    'official_profile_token_present':bool(new.get('horse_profile_token')),
                    'permanent_registry_acceptance':'UNKNOWN_NO_ACCEPTED_REGISTRY_LINEAGE',
                    'pedigree':{k:new.get(k) for k in ['sire','dam','damsire']},
                    'history_count':len(runs),'same_distance_history_count':sum(x.get('distance_m')==target_distance for x in runs),
                    'same_surface_history_count':sum(x.get('surface')==target_surface for x in runs),
                    'same_going_history_count':sum(x.get('going')==target_going for x in runs),'feature_index_lineage':trace}
                runners.append(runner_row);all_bvi.append(runner_row)
            after_observations=official_production_observations(parser_view,registry)
            class_feature_changes=[]
            for runner in before_observations:
                old_feature=before_observations[runner].get('class_performance')
                new_feature=after_observations[runner].get('class_performance')
                if old_feature!=new_feature:
                    class_feature_changes.append({'runner_id':runner,'before':old_feature,'after':new_feature})
            row_counts['class_feature_recovered']=sum(x['before'] is None and x['after'] is not None for x in class_feature_changes)
            workout=(source.get('jra_registered_common') or {}).get('workout') or {}
            workout_repair={}
            if workout.get('source_snapshot_sha256') in snapshots:
                ws=snapshots[workout['source_snapshot_sha256']]
                new_workout=parse_workout(raw(ws),ws['content_type'],source['jra_official_runner_universe'])
                old_workout={str(x['runner_id']):x for x in workout['runners']}
                workout_repair={'schema':new_workout['schema'],
                    'runner_count':len(new_workout['runners']),
                    'gait_misbound_to_name':sum(old_workout[str(x['runner_id'])].get('gait')==x.get('horse_name') and x.get('gait')=='' for x in new_workout['runners']),
                    'comment_observed':sum(bool(x.get('assessment')) for x in new_workout['runners']),
                    'timed_lap_observed':sum(x.get('final1f') is not None for x in new_workout['runners']),
                    'course_observed':sum(bool(x.get('course')) for x in new_workout['runners']),
                    'raw_sha256':ws['raw_sha256'],
                    'numerical_assessment_input_changed':False}
                for x in new_workout['runners']:
                    if {k:v for k,v in x.items() if k!='gait'}!={k:v for k,v in old_workout[str(x['runner_id'])].items() if k!='gait'}:
                        raise ValueError('WORKOUT_NON_GAIT_INPUT_CHANGED')
                row_counts['workout_gait_corrected']=workout_repair['gait_misbound_to_name']
            counts.update(row_counts);venue_counts.update(row_counts)
            context={k:source.get('jra_race_context',{}).get(k) for k in ['weather','going','race_class','distance_m','surface']}
            old_krs=req.get('krs_input_data') or {}
            replay_input=deepcopy(req);replay_input['source_snapshot']=source
            replay_input['source_snapshot_sha256']=source_sha;replay_input['prediction_cutoff']=source['prediction_cutoff']
            replay_input.setdefault('race_id',rid)
            repaired=build_krs_input(replay_input)['krs_input_data']
            changes={k:{'before':old_krs.get(section,{}).get(field),'after':repaired[section][field]}
                     for k,section,field in [('weather','environment','weather'),('going','race','going'),('class','race','class')]
                     if old_krs.get(section,{}).get(field)!=repaired[section][field]}
            if old_krs:
                if repaired['horses']!=old_krs['horses'] or repaired['simulation']!=old_krs['simulation']:
                    raise ValueError('HSV_OR_PHYSICS_CHANGED:'+rid)
                counts['krs_context_recovered_races']+=bool(changes)
            shadow_path=root/'runtime/role_rescue_shadow'/(rid+'.json')
            if shadow_path.exists():
                shadow=json.loads(shadow_path.read_text());result_path=root/'runtime/role_rescue_shadow_results'/(rid+'.json')
                shadow_result=json.loads(result_path.read_text()) if result_path.exists() else {}
                witness=shadow_result.get('persistence_witness') or {}
                rank=shadow.get('conditional_rank_comparison') or {}
                bindings={'sidecar':shadow['code_sha256']==plan['sidecar_code_sha256'],
                    'rank_code':rank.get('code_sha256')==plan['rank_code_sha256'],
                    'model':rank.get('model_sha256')==plan['model_sha256'],
                    'model_policy':rank.get('model_policy_sha256')==plan['model_policy_sha256']}
                oos.append({'race_id':rid,'runtime_claimed_eligible':shadow_result.get('oos_eligible',False),
                    'archived_witness_recorded_verified':witness.get('verified',False),
                    'witness':witness,'preregistered_bindings':bindings,
                    'strict_preregistered_oos_accepted':bool(witness.get('verified') and all(bindings.values())),
                    'standalone_shadow_signature':False,'signature_scope':shadow.get('signature_trust'),
                    'learning_binding_count':len(shadow.get('learning_state_bindings') or []),
                    'prediction_input_sha256':shadow.get('prediction_input_sha256')})
            if input_path.read_bytes()!=input_bytes:raise ValueError('ORIGINAL_INPUT_CHANGED:'+rid)
            races.append({'race_id':rid,'input_kind':kind,'input_file_sha256':hashlib.sha256(input_bytes).hexdigest(),
                'source_sha256':source_sha,'detail_raw_sha256':snapshot['raw_sha256'],
                'counts':dict(row_counts),'source_context':context,'krs_context_changes':changes,
                'grade_recoveries':grade_recoveries,'class_feature_changes':class_feature_changes,
                'workout_audit':workout_repair,'runners':runners})
        by_venue[venue]=dict(venue_counts)
    for path,value in protected.items():
        if hashlib.sha256((root/path).read_bytes()).hexdigest()!=value:raise ValueError('FROZEN_FINAL_CHANGED:'+path)
    out={'classification':'RETROSPECTIVE_SAVED_SOURCE_CORRECTNESS_AND_LINEAGE_NOT_FORWARD_OOS',
        'observed_at':datetime.now(timezone.utc).isoformat(),'baseline_main':'1e72d0d01bc41918fa5f460d49c85235f87a486b',
        'counts':dict(counts),'by_venue':by_venue,'races':races,'oos':oos,
        'oos_summary':{'shadow_saved':len(oos),'runtime_claimed_eligible':sum(x['runtime_claimed_eligible'] for x in oos),
            'archive_verified_records':sum(x['archived_witness_recorded_verified'] for x in oos),
            'strict_preregistered_accepted':sum(x['strict_preregistered_oos_accepted'] for x in oos),
            'minimum_races':60,'minimum_days':3,'minimum_venues':2,'automatic_promotion':False},
        'bvi_summary':{'classes':dict(Counter(x['bvi_class'] for x in all_bvi)),
            'accepted_permanent_id_recovered':0,'new_corpus_admissions':0,'unaccepted_408_runs_consumed':False,
            'hierarchical_bayes_fit':'BLOCKED_NO_ACCEPTED_ID_AND_INDEPENDENT_LABEL_LINEAGE'},
        'diagnoses':{'distance_fit_alias':'Legacy diagnostic feature distance_fit has no Production index binding; same_distance_fit is the registered measured feature. No policy alias is silently promoted.',
            'weather':'Printed pre-cutoff SOURCE facts omitted by sparse request race metadata; future input connection corrected, old inputs retained.',
            'grade':'Official image alt grades lost by plain text extraction; opt-in grade retention only, existing numerical class weights unchanged.',
            'identity':'Official profile tokens are navigation references, not accepted permanent Registry IDs.'},
        'frozen_final_file_sha256':protected,'production_policy_changed':False,'old_artifacts_modified':False}
    out['sha256']=sha(out);return out


def audit_archives(root, metadata_path, code_path, archive_root):
    """Reuse the existing provider verifier; never change OOS qualification rules."""
    from jra_role_learning_shadow import build_shadow, verify_actions_artifact, instant, ticket_key
    from jra_conditional_rank_shadow import compare, policy_sha
    from jra_shadow_checkpoint import learning_effect
    metadata=json.loads(metadata_path.read_text())['races']
    code={x['race_id']:x for x in json.loads(code_path.read_text())}
    plan=json.loads((root/'runtime/jra_race_day_plan/2026-10-24.json').read_text())['forward_oos_preregistration']
    authority_path=CODE_ROOT/'profiles/KM_FAMILY_CURRENT_AUTHORITY_20261012_R51.json'
    authority=json.loads(authority_path.read_text())
    source_contract=authority['family_scoped_authority']['JRA']['source_candidate_forward_oos']
    rows=[];first_state_archive={};archive_inputs=[]
    for item in metadata:
        rid=item['race_id'];provider=code[rid]
        artifact=next(a for a in item['metadata']['artifacts'] if a['name']=='krs-utility-'+str(item['run_id']))
        archive=(archive_root/(str(artifact['id'])+'.zip')).read_bytes()
        if 'sha256:'+hashlib.sha256(archive).hexdigest()!=artifact['digest']:
            raise ValueError('PROVIDER_ARCHIVE_DIGEST_MISMATCH:'+rid)
        with zipfile.ZipFile(__import__('io').BytesIO(archive)) as z:
            shadow_raw=z.read(rid+'/role_learning_shadow.json')
            shadow=json.loads(shadow_raw)
            checkpoint=json.loads(z.read(rid+'/shadow_input.json'))
        archive_inputs.append((item,artifact,archive,shadow_raw,shadow,checkpoint,provider))
        for state in checkpoint['learning_states']:
            sid=state.get('sha256')
            if state.get('race_id','').startswith('KM-JRA-') and '20261024' in state['race_id']:
                entry={'provider_created_at':artifact['created_at'],'artifact_id':artifact['id'],'archive_digest':artifact['digest'],'target_race':rid}
                if sid not in first_state_archive or instant(entry['provider_created_at'])<instant(first_state_archive[sid]['provider_created_at']):first_state_archive[sid]=entry
    for item,artifact,archive,shadow_raw,shadow,c,provider in archive_inputs:
        rid=item['race_id'];q=c['request'];f=c['final'];errors=[]
        files={path:base64.b64decode(obj['content']) if obj.get('encoding')=='base64' else obj['content'].encode()
               for path,obj in provider['code'].items()}
        hashes={path:hashlib.sha256(raw).hexdigest() for path,raw in files.items()}
        model=json.loads(files['research/jra_conditional_rank/model.json'])
        independent=False;witness={}
        try:
            witness=verify_actions_artifact(shadow,provider['run'],artifact,archive,files['runtime/jra_role_learning_shadow.py'])
            rank=shadow['conditional_rank_comparison']
            if hashes['runtime/jra_conditional_rank_shadow.py']!=rank['code_sha256']:raise ValueError('PROVIDER_RANK_CODE_MISMATCH')
            if model['sha256']!=sha({k:v for k,v in model.items() if k!='sha256'}) or model['sha256']!=rank['model_sha256']:raise ValueError('PROVIDER_MODEL_MISMATCH')
            if policy_sha(model)!=rank['model_policy_sha256']:raise ValueError('PROVIDER_MODEL_POLICY_MISMATCH')
            independent=True
        except (KeyError,ValueError,TypeError) as exc:errors.append(str(exc))
        source=q['source_snapshot'];source_sha=sha({k:v for k,v in source.items() if k!='source_snapshot_sha256'})
        bindings={'source':shadow['source_sha256']==q['source_snapshot_sha256']==f['source_snapshot_sha256']==source_sha,
            'source_payload':shadow['source_payload_sha256']==sha(source),
            'universe':shadow['runner_universe_sha256']==sha(sorted(str(r['runner_id']) for r in q['runners'])),
            'cutoff':shadow['prediction_cutoff']==q['prediction_cutoff']==f['prediction_cutoff'],
            'final':shadow['baseline_final_sha256']==f['sha256']==sha({k:v for k,v in f.items() if k!='sha256'}),
            'checkpoint':c['sha256']==sha({k:v for k,v in c.items() if k!='sha256'}),
            'request':c['request_sha256']==sha(q),
            'learning':c['learning_input_sha256']==sha(c['learning_states'])==shadow['checkpoint_learning_input_sha256'],
            'prediction_input':shadow['prediction_input_sha256']==sha({'request_sha256':sha(q),'learning_states':c['learning_states']})}
        if not all(bindings.values()):errors.append('SAVED_INPUT_BINDING_MISMATCH')
        prereg={'sidecar_code':hashes['runtime/jra_role_learning_shadow.py']==plan['sidecar_code_sha256'],
            'rank_code':hashes['runtime/jra_conditional_rank_shadow.py']==plan['rank_code_sha256'],
            'model':model['sha256']==plan['model_sha256'],
            'model_policy':policy_sha(model)==plan['model_policy_sha256'],
            'portfolio_policy':shadow['conditional_rank_portfolio']['policy_sha256']==plan['portfolio_policy_sha256']}
        # All original state bodies come from the provider archive, including
        # excluded/legacy states. No reconstructed/backdated effective_time.
        on=build_shadow(q,f,states=c['learning_states'],observed_at=shadow['observed_at'])
        off=build_shadow(q,f,states=[],observed_at=shadow['observed_at'])
        if on['arms']!=shadow['arms'] or on['learning_state_bindings']!=shadow['learning_state_bindings']:
            raise ValueError('ORIGINAL_SHADOW_REPLAY_MISMATCH:'+rid)
        rank_on=compare(q,model);rank_off=compare(deepcopy(q),model)
        if rank_on!=rank_off or rank_on!=shadow['conditional_rank_comparison']:raise ValueError('FIXED_RANK_REPLAY_MISMATCH:'+rid)
        loaded={s['sha256']:s for s in c['learning_states'] if isinstance(s,dict) and s.get('sha256')}
        learning=[]
        for b in on['learning_state_bindings']:
            state=loaded[b['state_sha256']];existence=first_state_archive.get(state['sha256'])
            learning.append({**b,'state_body_sha_valid':state['sha256']==sha({k:v for k,v in state.items() if k!='sha256'}),
                'state_body_in_archived_input':True,'learning_validity':state.get('learning_validity'),
                'source_freeze_boundary':source['source_freeze_at'],
                'effective_before_source_freeze':instant(state['effective_time'])<instant(source['source_freeze_at']),
                'earliest_observed_provider_archive':existence,
                'provider_existence_before_source_freeze':bool(existence and instant(existence['provider_created_at'])<instant(source['source_freeze_at']))})
        arm_effects={}
        for arm in on['arms']:
            keys_on={ticket_key(t) for t in on['arms'][arm]['tickets']};keys_off={ticket_key(t) for t in off['arms'][arm]['tickets']}
            arm_effects[arm]={'added':len(keys_on-keys_off),'removed':len(keys_off-keys_on),
                'capital_delta':on['arms'][arm]['required_capital']-off['arms'][arm]['required_capital']}
        rows.append({'race_id':rid,'provider_verification':witness,'provider_verified':independent,
            'provider_run_url':provider['run']['html_url'],'archive':artifact,'archive_sha256':hashlib.sha256(archive).hexdigest(),
            'shadow_file_sha256':hashlib.sha256(shadow_raw).hexdigest(),'shadow_sha256':shadow['sha256'],
            'source_sha256':source_sha,'runner_universe_sha256':shadow['runner_universe_sha256'],
            'prediction_input_sha256':shadow['prediction_input_sha256'],'prediction_cutoff':shadow['prediction_cutoff'],
            'production_prediction_request_sha256':c['request_sha256'],
            'production_learning_binding_fields':{k:v for k,v in q.items() if 'learning' in k.lower()},
            'actual_code_sha256':hashes,'model_sha256':model['sha256'],'model_policy_sha256':policy_sha(model),
            'bindings':bindings,'preregistered_bindings':prereg,
            'strict_preregistered_oos_accepted':independent and all(bindings.values()) and all(prereg.values()),
            'errors':errors,'loaded_state_count':len(c['learning_states']),
            'state_bindings':learning,'excluded_states':on['learning_intake']['excluded'],
            'learning_input_sha256':c['learning_input_sha256'],
            'input_without_learning_sha256':sha({'request_sha256':sha(q),'learning_states':[]}),
            'arm_effects_vs_no_learning':arm_effects,'learning_effect':learning_effect(shadow),
            'static_roles_changed':False,'fixed_rank_scores_changed':False,'fixed_rank_order_changed':False,
            'production_tickets_changed':on['arms']['PRODUCTION']!=off['arms']['PRODUCTION']})
    accepted=[b for r in rows for b in r['state_bindings']]
    output={'classification':'SAVED_PRE_CUTOFF_PROVIDER_ARTIFACT_AUDIT_AND_RETROSPECTIVE_ON_OFF_REPLAY',
        'observed_at':datetime.now(timezone.utc).isoformat(),'provider_archives_verified':sum(r['provider_verified'] for r in rows),
        'strict_preregistered_oos_accepted':sum(r['strict_preregistered_oos_accepted'] for r in rows),
        'source_candidate_signature_contract':source_contract,
        'conditional_rank_signature_scope':plan['signature_scope'],
        'standalone_shadow_signatures_found':0,'signature_contract_resolution':'Separate signed Candidate FINAL is required by the SOURCE_CANDIDATE cohort. The registered ROLE/CONDITIONAL_RANK sidecar inherits verified Production SOURCE/KRS/FINAL and requires exact independent provider archive content; no standalone Shadow signature is claimed. Cohorts are not conflated.',
        'learning':{'targets_with_loaded_accepted_bindings':sum(bool(r['state_bindings']) for r in rows),
            'scope':'ACTUAL_SAVED_SHADOW_INPUT_CONSUMPTION_ONLY; ON_OFF_REPLAY_IS_RETROSPECTIVE_INFLUENCE_VERIFICATION',
            'production_numeric_learning_consumption':0,
            'accepted_binding_occurrences':len(accepted),'distinct_source_states':len({b['state_sha256'] for b in accepted}),
            'provider_existence_before_source_binding_occurrences':sum(b['provider_existence_before_source_freeze'] for b in accepted),
            'targets_with_provider_proven_accepted_state':sum(any(b['provider_existence_before_source_freeze'] for b in r['state_bindings']) for r in rows),
            'distinct_source_states_with_provider_existence_before_a_target_source':len({b['state_sha256'] for b in accepted if b['provider_existence_before_source_freeze']}),
            'loaded_but_independent_source_boundary_time_unproven_occurrences':sum(not b['provider_existence_before_source_freeze'] for b in accepted),
            'ticket_changed_targets':sum(any(e['added'] or e['removed'] for e in r['arm_effects_vs_no_learning'].values()) for r in rows),
            'production_ticket_changed_targets':sum(r['production_tickets_changed'] for r in rows),
            'rank_model_numeric_learning_inputs':False,'rank_scores_changed_targets':0,
            'shadow_added_tickets':sum(r['arm_effects_vs_no_learning']['LEARNING_ON']['added'] for r in rows),
            'shadow_added_virtual_capital':sum(r['arm_effects_vs_no_learning']['LEARNING_ON']['capital_delta'] for r in rows),
            'excluded_counts':dict(Counter(e['reason'] for r in rows for e in r['excluded_states'])),
            'effect_limit':'State bindings alter provenance/input hashes. LEARNING_ON can activate pre-existing rescue proposals through a W-failure flag. The fixed conditional rank model reads only Full20 and fixed coefficients; it does not use Learning states as numerical inputs.',
            'new_original_lost_state_bodies_recovered':0,'fresh_recovery_state_live_consumption':0},
        'minimum_races':60,'minimum_days':3,'minimum_venues':2,'automatic_promotion':False,
        'races':rows,'production_effect':'NONE','new_historical_source_or_freeze_created':False}
    output['sha256']=sha(output);return output


def main():
    p=argparse.ArgumentParser();p.add_argument('--data-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--provider-metadata',type=Path);p.add_argument('--provider-code',type=Path);p.add_argument('--archive-root',type=Path);a=p.parse_args()
    if a.provider_metadata:
        if not a.provider_code or not a.archive_root:p.error('provider audit requires code cache and downloaded archives')
        result=audit_archives(a.data_root,a.provider_metadata,a.provider_code,a.archive_root)
    else:result=audit(a.data_root)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['counts','by_venue','oos_summary','bvi_summary','provider_archives_verified','strict_preregistered_oos_accepted','learning','sha256'] if k in result},ensure_ascii=False))


if __name__=='__main__':main()

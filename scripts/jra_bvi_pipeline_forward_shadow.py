"""Reuse Single Entry artifacts for immutable, current-policy A/B/C forward OOS.

Never acquires extra race information or emits a Production FINAL. Late/partial
runs fail closed and cannot become eligible samples. Result evaluation uses the
existing official Production result lane; no optimizing on observed outcomes.
"""
from datetime import datetime, timezone, timedelta
from pathlib import Path
import argparse, copy, hashlib, json, re, subprocess, sys, urllib.request
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'runtime/jra_source_runtime')]
from jra_static_owner_forward_oos import sha, time, fingerprint, save_immutable
from jra_pedigree_corpus import _verified_source, _attested, build_corpus
from jra_owner_authorized_feature_rules import owner_authorized_observations
from jra_bvi_shadow_comparison import compare, execute_diagnostic_downstream
from family_authority_guard import resolve_current_authority
PROFILE='KM-JRA-BVI-CURRENT-POLICY-THREE-ARM-FORWARD-SHADOW-v1'
ENV_PROFILE='KM-JRA-BVI-ENV-FOUR-ARM-FORWARD-SHADOW-v1'
ENV_ARM='D_BVI_ENV_SHADOW'
ENV_MODEL_PUBLICATION='KM-JRA-BVI-ENV-MODEL-PUBLICATION-v1'
ENV_CODE_FILES=('runtime/jra_bvi_environment.py','runtime/jra_bvi_env_shadow.py',
    'runtime/jra_bvi_shadow_comparison.py','runtime/jra_bvi_oos_metrics.py',
    'scripts/jra_bvi_pipeline_forward_shadow.py')


def environment_model_publication(model, *, root=ROOT, frozen_at=None, code_git_sha=None):
    """Publish deterministic model bytes with an ACTUAL clock, never a label date.

    This is not a race prediction or OOS sample. The later prospective loader
    additionally requires these exact bytes to have been committed before the
    target cutoff; an uncommitted diagnostic file cannot be a publication.
    """
    from jra_bvi_env_shadow import verify_model
    verify_model(model)
    stamp=frozen_at or datetime.now(timezone.utc).isoformat()
    if time(model['acquisition_cutoff'])>time(stamp):
        raise ValueError('BVI_ENV_MODEL_PUBLICATION_BEFORE_ACQUISITION')
    checkout=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    code_sha=code_git_sha or checkout
    if not re.fullmatch(r'[0-9a-f]{40}',str(code_sha)):
        raise ValueError('BVI_ENV_MODEL_CODE_BINDING_INVALID')
    hashes={name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in ENV_CODE_FILES}
    for name,digest in hashes.items():
        committed=subprocess.check_output(['git','show',code_sha+':'+name],cwd=root)
        if hashlib.sha256(committed).hexdigest()!=digest:
            raise ValueError('BVI_ENV_MODEL_CODE_NOT_COMMITTED')
    out={'profile':ENV_MODEL_PUBLICATION,'model':copy.deepcopy(model),
        'frozen_at':stamp,
        'code_git_sha':code_sha,'producer_checkout_sha':checkout,
        'code_file_sha256':hashes,
        'candidate_only':True,'production_authority':False,'purchase_authority':False}
    out['sha256']=sha(out)
    return out


def load_environment_model_publication(path, req, *, root=ROOT, now=None):
    """Fail closed on unpublished, revised, post-cutoff or future-label models."""
    from jra_bvi_env_shadow import verify_model
    now=now or datetime.now(timezone.utc)
    relative=Path(path).resolve().relative_to(root.resolve())
    raw=Path(path).read_bytes();publication=json.loads(raw)
    if (publication.get('profile')!=ENV_MODEL_PUBLICATION
            or publication.get('sha256')!=sha({k:v for k,v in publication.items() if k!='sha256'})
            or publication.get('candidate_only') is not True
            or publication.get('production_authority') is not False
            or publication.get('purchase_authority') is not False):
        raise ValueError('BVI_ENV_MODEL_PUBLICATION_INVALID')
    model=publication['model'];verify_model(model)
    if any(not re.fullmatch(r'[0-9a-f]{64}',str(model.get(key) or ''))
           for key in ('model_sha256','dataset_sha256','corpus_manifest_sha256')):
        raise ValueError('BVI_ENV_MODEL_DATASET_BINDING_REQUIRED')
    if (time(model['acquisition_cutoff'])>time(publication['frozen_at'])
            or time(publication['frozen_at'])>now
            or not now<=time(req['prediction_cutoff'])
            or str(model['train_before'])>str(req['race_date'])
            or (model.get('training_label_max') and str(model['training_label_max'])>=str(req['race_date']))
            or (model.get('maximum_training_acquisition_at')
                and time(model['maximum_training_acquisition_at'])>time(publication['frozen_at']))):
        raise ValueError('BVI_ENV_MODEL_TEMPORAL_LEAKAGE')
    expected={name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in ENV_CODE_FILES}
    if (publication.get('code_file_sha256')!=expected
            or model.get('model_code_sha256')!=expected['runtime/jra_bvi_env_shadow.py']):
        raise ValueError('BVI_ENV_MODEL_CODE_BINDING_INVALID')
    code_sha=publication.get('code_git_sha')
    if not isinstance(code_sha,str) or len(code_sha)!=40:
        raise ValueError('BVI_ENV_MODEL_CODE_BINDING_INVALID')
    # Both the claimed model code commit and the publication must be durable.
    for name,digest in expected.items():
        committed=subprocess.check_output(['git','show',code_sha+':'+name],cwd=root)
        if hashlib.sha256(committed).hexdigest()!=digest:
            raise ValueError('BVI_ENV_MODEL_CODE_NOT_COMMITTED')
    committed=subprocess.check_output(['git','show','HEAD:'+relative.as_posix()],cwd=root)
    if committed!=raw:raise ValueError('BVI_ENV_MODEL_PUBLICATION_NOT_COMMITTED')
    witnessed=subprocess.check_output(['git','log','-1','--format=%cI','--',relative.as_posix()],cwd=root,text=True).strip()
    if not witnessed or not time(publication['frozen_at'])<=time(witnessed)<=now:
        raise ValueError('BVI_ENV_MODEL_PUBLICATION_TIME_INVALID')
    return publication,{'path':relative.as_posix(),'file_sha256':hashlib.sha256(raw).hexdigest(),
        'published_at':witnessed,'publication_sha256':publication['sha256'],
        'model_sha256':model['model_sha256'],'model_corpus_manifest_sha256':model['corpus_manifest_sha256'],
        'model_dataset_sha256':model['dataset_sha256'],'code_git_sha':code_sha,
        'code_file_sha256':expected,'frozen_at':publication['frozen_at']}


def environment_predictions_for_source(model, source):
    """Only exact target SOURCE context; never infer going from weather."""
    from jra_bvi_env_shadow import predict
    detail=source.get('jra_official_race_card_detail') or {}
    contexts=[x for x in (source.get('jra_race_context'),detail.get('race_context')) if x]
    if not contexts or any(not isinstance(x,dict) or x.get('official') is not True
            or x.get('production_fact_authority') is not True for x in contexts):
        raise ValueError('BVI_ENV_OFFICIAL_TARGET_ENVIRONMENT_REQUIRED')
    context={}
    for candidate in contexts:
        for key,value in candidate.items():
            if value in (None,''):continue
            if key in ('venue_name','surface','distance_m','going','weather','race_date','course_variant'):
                if context.get(key) not in (None,'') and str(context[key])!=str(value):
                    raise ValueError('BVI_ENV_TARGET_ENVIRONMENT_CONFLICT:'+key)
            context.setdefault(key,value)
    observed=detail.get('race_environment') or {}
    if observed.get('going_surface') and context.get('surface')!=observed['going_surface']:
        raise ValueError('BVI_ENV_TARGET_ENVIRONMENT_CONFLICT:going_surface')
    for key in ('going','weather'):
        value=observed.get(key)
        if value not in (None,''):
            if context.get(key) not in (None,'') and str(context[key])!=str(value):
                raise ValueError('BVI_ENV_TARGET_ENVIRONMENT_CONFLICT:'+key)
            context[key]=value
    expected_day=(source.get('source_race_context') or {}).get('race_date')
    identity_day=re.search(r'-(20\d{6})-R\d{2}$',str(source.get('race_id') or ''))
    if identity_day:
        day=identity_day[1]
        from_id=day[:4]+'-'+day[4:6]+'-'+day[6:]
        if expected_day and expected_day!=from_id:
            raise ValueError('BVI_ENV_TARGET_ENVIRONMENT_RACE_DATE_MISMATCH')
        expected_day=from_id
    if expected_day and context.get('race_date')!=expected_day:
        raise ValueError('BVI_ENV_TARGET_ENVIRONMENT_RACE_DATE_MISMATCH')
    if not context.get('race_date') or context.get('surface') not in ('芝','ダ'):
        raise ValueError('BVI_ENV_TARGET_ENVIRONMENT_IDENTITY_REQUIRED')
    try:
        length=int(context['distance_m'])
        if isinstance(context['distance_m'],bool) or not 800<=length<=4500:raise ValueError
    except (KeyError,TypeError,ValueError):
        raise ValueError('BVI_ENV_TARGET_ENVIRONMENT_DISTANCE_REQUIRED') from None
    card=detail.get('runners') or []
    ids=[str(r.get('runner_id') or r.get('horse_no') or '') for r in card]
    if not all(ids) or len(set(ids))!=len(ids):
        raise ValueError('BVI_ENV_TARGET_RUNNER_UNIVERSE_INVALID')
    environment={'venue':context.get('venue_name'),'surface':context['surface'],
        'distance_m':length,'going':context.get('going'),
        'course_variant':context.get('course_variant'),'weather':context.get('weather'),
        'race_date':context['race_date'],'prediction_cutoff':source.get('prediction_cutoff'),
        'field_size':len(card),'race_name':context.get('race_class') or context.get('raw_race_context')}
    histories=(source.get('jra_official_horse_history') or {}).get('runners') or {}
    predictions={}
    for original,rid in zip(card,ids):
        runner=copy.deepcopy(original)
        history=histories.get(rid) or {}
        if history.get('horse_name') and history['horse_name']!=runner.get('horse_name'):
            raise ValueError('BVI_ENV_TARGET_HISTORY_NAME_CONFLICT:'+rid)
        pedigree=history.get('pedigree') or {}
        for key in ('sire','dam','damsire'):
            a,b=runner.get(key),pedigree.get(key)
            if a and b and a!=b:raise ValueError('BVI_ENV_TARGET_HISTORY_PARENT_CONFLICT:'+rid+':'+key)
            if not a and b:runner[key]=b
        # The model reads `runs`, not card `recent_runs`. Retain ONLY history
        # from this exact signed runner; never substitute a corpus namesake.
        raw_runs=history.get('runs') or runner.get('recent_runs') or []
        if not isinstance(raw_runs,list):raise ValueError('BVI_ENV_TARGET_HISTORY_INVALID:'+rid)
        runner['runs']=copy.deepcopy(raw_runs)
        predictions[rid]=predict(model,runner,environment)
    return predictions,environment


def environment_cohort_fingerprint(base_policy, binding, protocol):
    # Per-race ticket hashes/counts belong to the prediction, NOT the model
    # cohort. Including them here would make every race a one-sample cohort.
    return sha({'profile':ENV_PROFILE,'base_policy':base_policy,
        'model_sha256':binding['model_sha256'],'model_code_sha256':binding['code_file_sha256'],
        'comparison_protocol':{k:protocol[k] for k in ('profile','equal_budget','equal_ticket_rule')}})


def verify_environment_preregistration(pre, *, root=ROOT):
    """Validate frozen ENV publication without substituting today's model."""
    from jra_bvi_env_shadow import verify_model
    binding=pre.get('environment_candidate') or {}
    if (pre.get('profile')!=ENV_PROFILE or set(pre['comparison']['arms'])!=
            {'A_CURRENT','B_PEDIGREE_ENHANCED_SHADOW','C_BLOODLINE_ABLATION',ENV_ARM}
            or pre.get('policy_fingerprint')!=environment_cohort_fingerprint(
                pre['base_policy_fingerprint'],binding,pre['comparison_protocol'])):
        raise ValueError('BVI_ENV_FROZEN_COHORT_BINDING_INVALID')
    path=Path(binding['path'])
    if path.is_absolute() or '..' in path.parts:
        raise ValueError('BVI_ENV_MODEL_PUBLICATION_PATH_INVALID')
    raw=subprocess.check_output(['git','show',pre['code_git_sha']+':'+path.as_posix()],cwd=root)
    publication=json.loads(raw)
    if (hashlib.sha256(raw).hexdigest()!=binding['file_sha256']
            or publication.get('sha256')!=sha({k:v for k,v in publication.items() if k!='sha256'})
            or publication.get('sha256')!=binding['publication_sha256']
            or publication.get('profile')!=ENV_MODEL_PUBLICATION):
        raise ValueError('BVI_ENV_FROZEN_MODEL_PUBLICATION_INVALID')
    model=publication['model'];verify_model(model)
    if (model['model_sha256']!=binding['model_sha256']
            or model['corpus_manifest_sha256']!=binding['model_corpus_manifest_sha256']
            or model['dataset_sha256']!=binding['model_dataset_sha256']
            or time(model['acquisition_cutoff'])>time(publication['frozen_at'])
            or not time(publication['frozen_at'])<=time(binding['published_at'])<=time(pre['computation_started_at'])
            or not time(pre['computation_started_at'])<=time(pre['frozen_at'])<=time(pre['prediction_cutoff'])
            or str(model['train_before'])>str(pre['race_date'])
            or str(model['training_label_max'])>=str(pre['race_date'])):
        raise ValueError('BVI_ENV_FROZEN_MODEL_TEMPORAL_LEAKAGE')
    if publication['code_file_sha256']!=binding['code_file_sha256']:
        raise ValueError('BVI_ENV_FROZEN_MODEL_CODE_INVALID')
    if (set(binding['code_file_sha256'])!=set(ENV_CODE_FILES)
            or model.get('model_code_sha256')!=binding['code_file_sha256']['runtime/jra_bvi_env_shadow.py']):
        raise ValueError('BVI_ENV_FROZEN_MODEL_CODE_INVALID')
    for name,digest in binding['code_file_sha256'].items():
        if name not in ENV_CODE_FILES:
            raise ValueError('BVI_ENV_FROZEN_MODEL_CODE_INVALID')
        frozen_code=subprocess.check_output(['git','show',pre['code_git_sha']+':'+name],cwd=root)
        if hashlib.sha256(frozen_code).hexdigest()!=digest:
            raise ValueError('BVI_ENV_FROZEN_MODEL_CODE_INVALID')
    if binding.get('target_environment_sha256')!=sha(binding['target_environment']):
        raise ValueError('BVI_ENV_FROZEN_ENVIRONMENT_INVALID')
    predictions=pre['comparison']['arms'][ENV_ARM]['environment_predictions']
    if binding['prediction_input_sha256']!={rid:p['input_sha256'] for rid,p in predictions.items()}:
        raise ValueError('BVI_ENV_FROZEN_PREDICTION_INPUT_INVALID')
    return True


def require_open_window(req, now=None):
    now=now or datetime.now(timezone.utc)
    if not now <= time(req['prediction_cutoff']) < time(req['scheduled_post_at']):
        raise ValueError('BVI_FORWARD_CUTOFF_EXPIRED')
    if req.get('acceptance_only') is True or req.get('temporal_mode')!='FORMAL-PRE-RACE':
        raise ValueError('BVI_FORWARD_REPLAY_FORBIDDEN')
    if req.get('family_id')!='JRA' or req.get('candidate_only') is True:
        raise ValueError('BVI_FORWARD_CURRENT_PRODUCTION_REQUEST_REQUIRED')
    return now



def production_priority_window(req, *, root=ROOT, now=None, signed_final_ids=()):
    """Operational admission only; no prediction or OOS rule changes."""
    now=now or datetime.now(timezone.utc)
    day=req.get('race_date')
    if day!='2026-10-18' and (not isinstance(day,str) or day<'2026-10-25'):
        return None
    plan_path=root/f'runtime/jra_race_day_plan/{day}.json'
    if not plan_path.is_file():raise ValueError('BVI_SHADOW_DEFER_OFFICIAL_DAY_PLAN_MISSING')
    plan=json.loads(plan_path.read_text())
    if plan.get('race_date')!=day or plan.get('family_id')!='JRA':
        raise ValueError('BVI_SHADOW_PRIORITY_PLAN_IDENTITY_INVALID')
    schedule_path=root/f'runtime/jra_race_day_plan/{day}.schedule.json'
    schedule=json.loads(schedule_path.read_text()) if schedule_path.exists() else {}
    cohort=plan.get('cohort')
    if cohort:
        ids=cohort['race_ids']
    elif plan.get('all_races') is True:
        # Normal Autopilot plans do not require cohort registrations. Reuse
        # its saved official day rows, never provisional program post times.
        if not schedule:raise ValueError('BVI_SHADOW_DEFER_OFFICIAL_SCHEDULE_MISSING')
        prereg=plan.get('forward_oos_preregistration') or {}
        targets=prereg.get('targets') or []
        if not isinstance(targets,list) or any(not isinstance(r,dict) or not isinstance(r.get('race_id'),str) for r in targets):
            raise ValueError('BVI_SHADOW_DEFER_ALL_RACES_SCOPE_UNVERIFIED')
        ids=[r.get('race_id') for r in targets]
        if (plan.get('plan_sha256')!=sha({k:v for k,v in plan.items() if k!='plan_sha256'})
                or prereg.get('target_race_count')!=len(ids) or set(schedule)!=set(ids)):
            raise ValueError('BVI_SHADOW_DEFER_ALL_RACES_SCOPE_UNVERIFIED')
        # Target IDs are only a completeness bound. They are NOT a new cohort
        # or the authority for any time, Runner Universe or OOS qualification.
        from jra_source_runtime.jra_race_day_autopilot import race_id_for
        window=plan.get('dispatch_window_minutes_before_post') or [55,30]
        if not (len(window)==2 and window[0]>window[1]>5):
            raise ValueError('BVI_SHADOW_PRIORITY_DISPATCH_WINDOW_INVALID')
        for rid,row in schedule.items():
            try:
                post=time(row['post'])
                if (post.astimezone(timezone(timedelta(hours=9))).date().isoformat()!=day
                        or type(row.get('race_no')) is not int or not 1<=row['race_no']<=12
                        or race_id_for(day,row['venue'],row['race_no'])!=rid
                        or not isinstance(row.get('official_day_row'),str) or not row['official_day_row'].strip()
                        or row.get('status')
                        or time(row['dispatch_window_open'])!=post-timedelta(minutes=window[0])
                        or time(row['dispatch_window_close'])!=post-timedelta(minutes=window[1])):
                    raise ValueError('OFFICIAL_SCHEDULE_ROW_INVALID')
            except (ValueError,KeyError,TypeError) as exc:
                raise ValueError('BVI_SHADOW_DEFER_OFFICIAL_SCHEDULE_UNVERIFIED:'+str(rid)) from exc
        if req['race_id'] not in schedule or time(req['scheduled_post_at'])!=time(schedule[req['race_id']]['post']):
            raise ValueError('BVI_SHADOW_DEFER_CURRENT_POST_MISMATCH')
    else:
        raise ValueError('BVI_SHADOW_DEFER_DAY_PLAN_UNSUPPORTED')
    if len(ids) not in (12,24,36) or len(set(ids))!=len(ids) or req['race_id'] not in ids:
        raise ValueError('BVI_SHADOW_PRIORITY_COHORT_UNVERIFIED')
    stop=min(time(req['prediction_cutoff'])-timedelta(seconds=120),now+timedelta(seconds=600))
    pending=[]
    for rid in ids:
        if rid==req['race_id'] or rid in signed_final_ids:
            continue
        if cohort:
            registration=json.loads((root/f'runtime/jra_race_registrations/{day}'/f'{rid}.json').read_text())
            from jra_race_day_registration import verify_registration
            post=time(registration['intake_intent']['scheduled_post_at'])
            verify_registration(registration,plan,race_id=rid,official_post=post)
        else:post=time(schedule[rid]['post'])
        # Prefer the existing current-day schedule when the official post changes.
        if rid in schedule:post=time(schedule[rid]['post'])
        cutoff=post-timedelta(minutes=5)
        opening=post-timedelta(minutes=55) if cohort else time(schedule[rid]['dispatch_window_open'])
        if now>=cutoff:
            continue
        if opening<=now:
            pending.append(rid)
        else:
            stop=min(stop,opening-timedelta(seconds=120))
    if pending:
        raise ValueError('BVI_SHADOW_DEFER_PRODUCTION_PENDING:'+','.join(pending))
    if (stop-now).total_seconds()<180:
        raise ValueError('BVI_SHADOW_DEFER_INSUFFICIENT_SAFE_WINDOW')
    return stop


def call(path,payload,timeout):
    req=urllib.request.Request('https://quorumprobe-production.up.railway.app'+path,
        data=json.dumps(payload,ensure_ascii=False).encode(),headers={'Content-Type':'application/json'},method='POST')
    with urllib.request.urlopen(req,timeout=timeout) as response:return json.loads(response.read())


def policy_fingerprint():
    names=('runtime/jra_bvi_failure_attribution.py','runtime/jra_bvi_static_proof.py','runtime/jra_bvi_oos_metrics.py','runtime/jra_aki_v21.py','runtime/jra_aki_v21_features.py',
        'runtime/jra_krs_input_builder_production.py','runtime/jra_candidate_krs_plan.py',
        'runtime/krs_prediction_utility.py','runtime/minimum_efficient_coverage.py','runtime/capital_policy.py',
        'scripts/jra_bvi_pipeline_forward_shadow.py',
        'profiles/jra_aki_v21_components_20261011_v1.json','profiles/jra_aki_v21_columns_20261011_v1.json')
    authority_path,authority=resolve_current_authority(ROOT)
    return sha({'authority_manifest':authority['manifest_id'],
        'authority_sha256':hashlib.sha256(authority_path.read_bytes()).hexdigest(),
        'static_owner_fingerprint':fingerprint(),
        'files':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in names}})


def bind_production_reference(comparison, req, final, *, require_match=True):
    """Compare the A replay to the actual canonical Production recommendation.

    The caller separately verifies the signed FINAL with the current trust anchor.
    Ticket annotations may differ; selections, direction and stakes may not.
    """
    from jra_production_postresult import verify_final
    verify_final(final)
    if any(final.get(k)!=req.get(k) for k in
           ('race_id','source_snapshot_sha256','prediction_cutoff','scheduled_post_at')):
        raise ValueError('BVI_FORWARD_CANONICAL_FINAL_BINDING_MISMATCH')
    if time(final['final_receipt']['receipt']['timestamp'])>time(req['prediction_cutoff']):
        raise ValueError('BVI_FORWARD_CANONICAL_FINAL_AFTER_CUTOFF')
    arm=comparison['arms']['A_CURRENT']
    matches={'ranking':arm['owner']['static_prediction']['ranking']==final['static_prediction']['ranking']}
    for field,keys in [('role_registry',('runner_id','column','status')),
            ('pair_dispositions',('head','second','status')),
            ('third_dispositions',('head','second','third','status'))]:
        project=lambda rows:sorted(tuple(str(row[k]) for k in keys) for row in rows)
        matches[field]=project(arm['owner'][field])==project(final[field])
    def tickets(rows):
        return sorted((x['bet_type'],tuple(sorted(x['selection']) if x['bet_type']=='TRIO' else x['selection']),x['stake']) for x in rows)
    actual=final['final_ticket']
    matches['tickets']=tickets(arm['diagnostic_tickets'])==tickets(actual['tickets'])
    matches['investment']=sum(x['stake'] for x in arm['diagnostic_tickets'])==actual['total_investment']
    if require_match and not all(matches.values()):
        raise ValueError('BVI_FORWARD_CANONICAL_TICKET_REPLAY_MISMATCH:'+','.join(k for k,v in matches.items() if not v))
    return {'status':'MATCHED_CANONICAL_PRODUCTION_RECOMMENDATION' if all(matches.values()) else 'HISTORICAL_CURRENT_POLICY_REPLAY_DIFFERS_FROM_ORIGINAL_PRODUCTION',
        'replay_matches':matches,'forward_eligible_baseline':all(matches.values()),
        'final_sha256':final['sha256'],'final_receipt_sha256':final['final_receipt_sha256'],
        'source_snapshot_sha256':final['source_snapshot_sha256'],
        'production_krs_receipt_sha256':final['krs_run_receipt']['receipt_sha256'],
        'production_krs_input_sha256':final['krs_run_receipt']['receipt']['input_sha256'],
        'ticket_sha256':sha(actual),'capital_sha256':sha(final['capital_policy_decision']),
        'ticket_count':len(actual['tickets']),'total_investment':actual['total_investment'],
        'comparison_krs_lane':'SEPARATE_CANDIDATE_REPLAY; NOT_PRODUCTION_EXECUTION',
        'pfs_basis':'FROZEN_RECOMMENDATION; ACTUAL_PURCHASE_UNVERIFIED'}


def arm_consumption(comparison, req, source, mapping, authority, *, execution_class='FORWARD_SHADOW_ACTUAL_COMPUTATION_NOT_PRODUCTION_FINAL'):
    from jra_bvi_consumption import build_bvi_consumption
    from jra_bvi_static_proof import build_static_proof,SOURCE_ANNOTATIONS
    from jra_static_owner_executable import compile_static_owner
    out={}
    for name,arm in comparison['arms'].items():
        if name==ENV_ARM:
            # A research score must NEVER be laundered through the Production
            # BVI proof/Mapping. Preserve its own model -> Full20 -> KRS trace.
            lineage=arm.get('environment_shadow_proof') or {}
            if (arm.get('production_authority') is not False or arm.get('candidate_only') is not True
                    or not lineage.get('model_sha256') or not arm.get('numerical_provenance_sha256')
                    or any(cell.get('candidate_only') is not True or cell.get('production_authority') is not False
                        for row in arm['numerical_runners'] for cell in row['canonical_components'].values())):
                raise ValueError('BVI_ENV_RESEARCH_LINEAGE_INVALID')
            receipt=arm.get('krs_signed_run_receipt') or {}
            proof={'profile':'KM-JRA-BVI-ENV-RESEARCH-CONSUMPTION-v1',
                'status':'RESEARCH_BOUND_NOT_PRODUCTION_PROOF','execution_class':execution_class,
                'source_snapshot_sha256':source['source_snapshot_sha256'],
                'environment_shadow_proof':copy.deepcopy(lineage),
                'numerical_provenance_sha256':arm['numerical_provenance_sha256'],
                'static_prediction_sha256':sha(arm['owner']),
                'krs_input_sha256':sha(arm['krs_input']),
                'signed_run_receipt_sha256':receipt.get('receipt_sha256'),
                'executed_input_sha256':(receipt.get('receipt') or {}).get('input_sha256'),
                'executed_output_sha256':(receipt.get('receipt') or {}).get('output_sha256'),
                'receipt_verified':arm.get('krs_receipt_verified') is True,
                'mec_sha256':sha(arm.get('mec')),'capital_sha256':sha(arm.get('capital_policy_decision')),
                'ticket_sha256':sha(arm.get('diagnostic_tickets')),
                'candidate_only':True,'production_authority':False,'purchase_authority':False,
                'production_numerical_closure':False}
            proof['sha256']=sha(proof);out[name]=proof
            continue
        prepared=copy.deepcopy(req)
        prepared.pop('bvi_static_consumption_proof',None)
        prepared['runners']=copy.deepcopy(arm['numerical_runners'])
        prepared['numerical_calculated_at']=arm.get('numerical_calculated_at')
        owner=arm['owner']
        raw=compile_static_owner(prepared,source_snapshot_sha256=owner['source_snapshot_sha256'],
            source_receipt_sha256=owner['source_receipt_sha256'],frozen_at=owner['frozen_at'],
            prediction_cutoff=req['prediction_cutoff'])
        formal=copy.deepcopy(prepared)
        formal.update({k:copy.deepcopy(owner[k]) for k in
            ('static_prediction','role_registry','pair_dispositions','third_dispositions','purchased_heads')})
        # Fresh Static outputs omit transport-only SOURCE annotations. Keep
        # their original binding; the existing verifier checks every value.
        formal['static_prediction'].update({k:req['static_prediction'][k] for k in SOURCE_ANNOTATIONS
                                           if k in req['static_prediction']})
        formal['krs_input_data']=copy.deepcopy(arm['krs_input'])
        formal['bvi_static_consumption_proof']=build_static_proof(prepared,raw,formal,authority,
            execution_class=execution_class)
        proof=build_bvi_consumption(formal,mapping,source_artifact=source)
        receipt=arm.get('krs_signed_run_receipt') or {}
        proof['comparison_execution']={'krs_lane':'SEPARATE_CANDIDATE_EXECUTION',
            'signed_run_receipt_sha256':receipt.get('receipt_sha256'),
            'executed_input_sha256':(receipt.get('receipt') or {}).get('input_sha256'),
            'executed_output_sha256':(receipt.get('receipt') or {}).get('output_sha256'),
            'actual_run_count':(receipt.get('receipt') or {}).get('actual_run_count'),
            'mec_sha256':sha(arm.get('mec')),'capital_sha256':sha(arm.get('capital_policy_decision')),
            'ticket_sha256':sha(arm.get('diagnostic_tickets')),
            'receipt_verified':arm.get('krs_receipt_verified') is True}
        proof['sha256']=sha({k:v for k,v in proof.items() if k!='sha256'})
        out[name]=proof
    return out


def freeze(request, source_path, output, *, environment_model_path=None):
    req=json.loads(request.read_text());now=require_open_window(req)
    environment_publication=environment_binding=None
    if environment_model_path is not None:
        expected=ROOT/'runtime/jra_static_owner_forward_oos'/req['race_id']/'pedigree_env_pre_result.json'
        if Path(output).resolve()!=expected.resolve():
            raise ValueError('BVI_ENV_SEPARATE_IMMUTABLE_OUTPUT_REQUIRED')
        environment_publication,environment_binding=load_environment_model_publication(
            environment_model_path,req,now=now)
    shadow_stop=None
    day=req.get('race_date')
    if day=='2026-10-18' or (isinstance(day,str) and day>='2026-10-25'):
        # Read-only trust check before any research KRS use. Production is untouched.
        from jra_delivery import verify_signed_final
        _,priority_authority=resolve_current_authority(ROOT,now=now)
        contracts=json.loads((ROOT/priority_authority['common_family_components']['family_runtime_contracts_profile']).read_text())
        contract=contracts['families']['JRA']
        with urllib.request.urlopen(contract['external_endpoint'].rstrip('/')+'/health',timeout=20) as response:
            priority_health=json.load(response)
        completed_ids=[]
        for path in (ROOT/'runtime/final_artifacts').glob(f'KM-JRA-*-{day.replace("-","")}-R*.json'):
            try:
                final=json.loads(path.read_text());verify_signed_final(final,priority_health,contract)
                if time(final['final_receipt']['receipt']['timestamp'])<=now:
                    completed_ids.append(final['race_id'])
            except Exception:
                continue  # invalid/unknown is pending, never permission to run research
        shadow_stop=production_priority_window(req,now=now,signed_final_ids=completed_ids)
    checked=_verified_source(source_path)
    if checked is None or not _attested(source_path,not_after=time(req['prediction_cutoff'])):
        raise ValueError('BVI_FORWARD_SOURCE_OIDC_OR_SIGNATURE_INVALID')
    env=json.loads(source_path.read_text());source=env['artifact']
    from jra_execution_maturity_bridge import verify_formal_request_binding
    binding=verify_formal_request_binding(req,env)
    if binding.get('status')!='PASS':raise ValueError('BVI_FORWARD_FORMAL_SOURCE_BINDING_REQUIRED')
    if (source['race_id']!=req['race_id'] or source['prediction_cutoff']!=req['prediction_cutoff']
            or checked['source_snapshot_sha256']!=req['source_snapshot_sha256']):
        raise ValueError('BVI_FORWARD_SOURCE_BINDING_MISMATCH')
    authority_path, authority=resolve_current_authority(ROOT,now=now)
    if time(authority['effective_at'])>time(req['prediction_cutoff']):
        raise ValueError('BVI_FORWARD_AUTHORITY_NOT_EFFECTIVE_AT_CUTOFF')
    mapping=json.loads((ROOT/'mapping/jra_base_index_evidence_mapping_v1.0_20260921.json').read_text())
    card=source['jra_official_race_card_detail']['runners']
    registry=json.loads((ROOT/'mapping/jra_evidence_feature_rule_registry_v1.3_20261010.json').read_text())
    corpus=build_corpus(ROOT,prediction_cutoff=now.isoformat(),race_date=req['race_date'],
        exclude_race_id=req['race_id'],required_sires={r['sire'] for r in card if r.get('sire')},
        required_damsires={r['damsire'] for r in card if r.get('damsire')})
    enriched=owner_authorized_observations(source,registry,corpus=corpus)
    # Do not stamp a later-read corpus observation with the earlier card time.
    from jra_bvi_shadow_comparison import PEDIGREE_FEATURES
    comparison_time=require_open_window(req)
    for features in enriched.values():
        for key,spec in features.items():
            if key in PEDIGREE_FEATURES:spec['observed_at']=comparison_time.isoformat()
    environment_options={}
    if environment_publication is not None:
        predictions,target_environment=environment_predictions_for_source(environment_publication['model'],source)
        environment_options={'environment_predictions':predictions,
            'environment_model_sha':environment_publication['model']['model_sha256']}
    comparison=compare(req,mapping,source_sha=source['source_snapshot_sha256'],receipt_sha=env['receipt_sha256'],
        algorithm_freeze_at=comparison_time.isoformat(),cutoff=req['prediction_cutoff'],
        source_artifact=source,current_authority=authority,root=ROOT,enhanced_features=enriched,
        **environment_options)
    actual=comparison['arms']['A_CURRENT']['owner']
    numerical={str(r['runner_id']):r for r in comparison['arms']['A_CURRENT']['numerical_runners']}
    for runner in req['runners']:
        for key,cell in runner['canonical_components'].items():
            if abs(cell['value']-numerical[str(runner['runner_id'])]['canonical_components'][key]['value'])>1e-6:
                raise ValueError('BVI_FORWARD_A_CURRENT_NUMERICAL_REPLAY_MISMATCH:'+key)
    for field in ('role_registry','pair_dispositions','third_dispositions'):
        columns=('runner_id','column','status') if field=='role_registry' else ('head','second','status') if field=='pair_dispositions' else ('head','second','third','status')
        def semantics(rows):return sorted(tuple(str(r[k]) for k in columns) for r in rows)
        if semantics(actual[field])!=semantics(req[field]):raise ValueError('BVI_FORWARD_A_CURRENT_POLICY_REPLAY_MISMATCH:'+field)
    def priority_call(path,payload,timeout):
        observed=require_open_window(req)
        if shadow_stop is not None:
            remaining=(shadow_stop-observed).total_seconds()
            # Keep the existing maximum single KRS request (420s) inside the
            # reserved window; do not launch work that would rely on cancellation.
            if remaining<timeout+30:
                raise ValueError('BVI_SHADOW_DEFER_REQUEST_EXCEEDS_SAFE_WINDOW')
        return call(path,payload,timeout)
    execute_diagnostic_downstream(comparison,req,None,priority_call)
    final_path=ROOT/'runtime/final_artifacts'/f"{req['race_id']}.json"
    final=json.loads(final_path.read_text())
    contracts=json.loads((ROOT/authority['common_family_components']['family_runtime_contracts_profile']).read_text())
    contract=contracts['families']['JRA']
    from jra_delivery import verify_signed_final
    with urllib.request.urlopen(contract['external_endpoint'].rstrip('/')+'/health',timeout=20) as response:
        health=json.load(response)
    verify_signed_final(final,health,contract)
    production_reference=bind_production_reference(comparison,req,final)
    consumption=arm_consumption(comparison,req,source,mapping,authority)
    completed=require_open_window(req)
    if shadow_stop is not None and completed>=shadow_stop:
        raise ValueError('BVI_SHADOW_SAFE_WINDOW_EXPIRED')
    for arm in comparison['arms'].values():
        executed=time(arm['krs_signed_run_receipt']['receipt']['timestamp'])
        if not now<=executed<=completed:
            raise ValueError('BVI_FORWARD_KRS_TIME_OUTSIDE_PRE_CUTOFF_FREEZE')
    from jra_bvi_oos_metrics import preregister
    record={'operational_shadow_stop_at':shadow_stop.isoformat() if shadow_stop else None,
        'code_git_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'model_sha256':sha({'mapping':mapping,'static_owner_fingerprint':fingerprint(),
            'engine_sha256':contract['engine_sha256'],'parameter_map_sha256':contract['parameter_map_sha256']}),
        'comparison_protocol':preregister(comparison),
        'production_baseline':production_reference,'arm_bvi_consumption':consumption,
        'profile':PROFILE,'race_id':req['race_id'],'frozen_at':completed.isoformat(),
        'computation_started_at':now.isoformat(),'prediction_cutoff':req['prediction_cutoff'],
        'scheduled_post_at':req['scheduled_post_at'],'policy_fingerprint':policy_fingerprint(),
        'authority_manifest':authority['manifest_id'],'authority_file_sha256':hashlib.sha256(authority_path.read_bytes()).hexdigest(),
        'mapping_sha256':sha(mapping),'source_snapshot_sha256':source['source_snapshot_sha256'],
        'source_receipt_sha256':env['receipt_sha256'],
        'source_file_sha256':hashlib.sha256(source_path.read_bytes()).hexdigest(),
        'formal_request_file_sha256':hashlib.sha256(request.read_bytes()).hexdigest(),
        'formal_source_binding':binding,'comparison':comparison,
        'market_ranking':(sorted({str(x.get('runner_id') or x.get('horse_no')):x.get('popularity_rank')
            for x in source['jra_official_race_card_detail']['runners']},key=lambda rid:
            next(x['popularity_rank'] for x in source['jra_official_race_card_detail']['runners']
                 if str(x.get('runner_id') or x.get('horse_no'))==rid))
            if {x.get('popularity_rank') for x in source['jra_official_race_card_detail']['runners']}
               ==set(range(1,len(req['runners'])+1)) else None),
        'corpus_availability_cutoff':now.isoformat(),'enhanced_observed_at':comparison_time.isoformat(),
        'corpus':{k:corpus.get(k) for k in ('manifest_sha256','horse_count','run_count','snapshot_count','identity_collision_count','run_conflict_count')},
        'candidate_only':True,'production_authority':False,'purchase_authority':False,
        'oos_status':'PRE_RESULT_FROZEN / REQUIRES_PRE_CUTOFF_GIT_WITNESS_AND_OFFICIAL_RESULT'}
    if environment_publication is not None:
        # The ABC-only cohort and files are not overwritten or counted as D.
        record['profile']=ENV_PROFILE
        record['race_date']=req['race_date']
        record['environment_candidate']={**environment_binding,
            'target_environment':target_environment,'target_environment_sha256':sha(target_environment),
            'prediction_input_sha256':{rid:p['input_sha256'] for rid,p in predictions.items()}}
        record['base_policy_fingerprint']=record['policy_fingerprint']
        record['policy_fingerprint']=environment_cohort_fingerprint(record['base_policy_fingerprint'],
            environment_binding,record['comparison_protocol'])
    record['sha256']=sha(record);save_immutable(output,record)
    return record


def persist_result_receipt(result_request, receipt, root=ROOT):
    """Called only after canonical Result Runner /verify succeeds.

    Preserve its unchanged signed response in the existing forward cohort;
    never create, resubmit or modify a historical RESULT or learning event.
    """
    if result_request.get('result_lane')!='PRODUCTION':return
    directory=root/'runtime/jra_static_owner_forward_oos'/result_request['race_id']
    if not any((directory/name).exists() for name in ('pedigree_pipeline_pre_result.json','pedigree_env_pre_result.json')):return
    target=directory/'production_result_receipt.json'
    record={'race_id':result_request['race_id'],'result_request_sha256':sha(result_request),
        'signed_result_envelope':receipt,'verified_by_canonical_result_runner':True}
    record['sha256']=sha(record)
    if target.exists():
        prior=json.loads(target.read_text())
        if prior.get('result_request_sha256')!=record['result_request_sha256']:
            raise ValueError('BVI_FORWARD_SIGNED_RESULT_REQUEST_CHANGED')
        return
    save_immutable(target,record)


def _settle_record(path, root):
    from mec_r4_shadow import settle_ticket_list
    from krs_prediction_utility import evaluate_against_result
    pre=json.loads(path.read_text())
    environment=pre.get('profile')==ENV_PROFILE
    target=path.with_name('pedigree_env_result.json' if environment else 'pedigree_pipeline_result.json')
    if pre.get('profile') not in (PROFILE,ENV_PROFILE) or pre.get('sha256')!=sha({k:v for k,v in pre.items() if k!='sha256'}):
        raise ValueError('BVI_FORWARD_FROZEN_HASH_INVALID')
    if environment:
        if path.name!='pedigree_env_pre_result.json':raise ValueError('BVI_ENV_SEPARATE_IMMUTABLE_OUTPUT_REQUIRED')
        verify_environment_preregistration(pre,root=root)
    witness=subprocess.check_output(['git','log','-1','--format=%cI','--',str(path.relative_to(root))],cwd=root,text=True).strip()
    if not witness or not time(pre['frozen_at'])<=time(witness)<=time(pre['prediction_cutoff']):
        raise ValueError('BVI_FORWARD_NOT_PRE_CUTOFF_COMMITTED')
    result_path=root/'runtime/results'/f"{pre['race_id']}.json"
    if not result_path.exists():return None
    result=json.loads(result_path.read_text());official=result['official_result']
    receipt_path=path.with_name('production_result_receipt.json')
    if not receipt_path.exists():return None
    bound=json.loads(receipt_path.read_text());envelope=bound['signed_result_envelope'];receipt=envelope['receipt']
    if (bound.get('sha256')!=sha({k:v for k,v in bound.items() if k!='sha256'})
            or bound.get('result_request_sha256')!=sha(result)
            or receipt.get('phase')!='RESULT' or receipt.get('status')!='PASS'
            or bound.get('race_id')!=pre['race_id']
            or not str(result.get('race_id','')).startswith('KM-JRA-')
            or result.get('family_id','JRA')!='JRA'
            or receipt.get('race_id')!=pre['race_id']
            or receipt.get('artifact_sha256')!=sha(result)
            or call('/verify',envelope,30).get('valid') is not True):
        raise ValueError('BVI_FORWARD_SIGNED_RESULT_BINDING_INVALID')
    # RESULT signs the unchanged request hash; it does not embed an artifact.
    signed_official=result['official_result']
    signed_top3=signed_official.get('top3') or signed_official.get('finish_order',[])[:3]
    if [str(x) for x in signed_top3]!=[str(x) for x in official['top3']]:
        raise ValueError('BVI_FORWARD_SIGNED_RESULT_ORDER_MISMATCH')
    if (result.get('race_id')!=pre['race_id'] or result.get('result_lane')!='PRODUCTION'
            or official.get('status')!='OFFICIAL'
            or (result.get('frozen_prediction_ref') or {}).get('source_cutoff')!=pre['prediction_cutoff']
            or not str(official.get('source_url','')).startswith('https://www.jra.go.jp/')
            or len(str(official.get('raw_sha256','')))!=64):
        raise ValueError('BVI_FORWARD_OFFICIAL_RESULT_LANE_REQUIRED')
    if not time(pre['scheduled_post_at'])<time(official['captured_at']):
        raise ValueError('BVI_FORWARD_RESULT_NOT_POST_RACE')
    payout={'official_result':{'top3':official['top3'],'payouts':{k:v['per_100_yen'] for k,v in official['payouts'].items()}}}
    if len(official['top3'])!=3 or len(set(official['top3']))!=3:
        raise ValueError('BVI_FORWARD_RESULT_UNIVERSE_INVALID')
    arms={}
    for name,arm in pre['comparison']['arms'].items():
        settlement=settle_ticket_list(arm['diagnostic_tickets'],payout)
        if settlement['status']!='SETTLED':raise ValueError('BVI_FORWARD_PAYOUT_INCOMPLETE')
        ranking=arm['owner']['static_prediction']['ranking'];top3=[str(x) for x in official['top3']];cols=arm['owner']['active_columns']
        arms[name]={'settlement':settlement,'winner_rank':ranking.index(top3[0])+1,
            'winner_discovery_recall':int(top3[0] in cols['W']),'p2_capture':top3[1] in cols['P2'],
            'p3_capture':top3[2] in cols['P3'],
            'ordered_pair_semantic_capture':any(str(x['head'])==top3[0] and str(x['second'])==top3[1] and x['status']!='EXCLUDE' for x in arm['owner']['pair_dispositions']),
            'exact_semantic_capture':any((str(x['head']),str(x['second']),str(x['third']))==tuple(top3) and x['status']!='EXCLUDE' for x in arm['owner']['third_dispositions']),
            'top3_mean_rank':sum(ranking.index(x)+1 for x in top3)/3,
            'market_winner_rank':pre['market_ranking'].index(top3[0])+1 if pre.get('market_ranking') else None,
            'market_top3_mean_rank':sum(pre['market_ranking'].index(x)+1 for x in top3)/3 if pre.get('market_ranking') else None,
            'candidate_width':len(set().union(*(set(v) for v in cols.values()))),
            'role_widths':{k:len(v) for k,v in cols.items()},
            'ticket_count':len(arm['diagnostic_tickets']),'capital_required':arm['capital_required'],
            'low_popularity_top3_discovered':([rid for rid in top3 if pre['market_ranking'].index(rid)+1>=6
                and rid in set().union(*(set(v) for v in cols.values()))] if pre.get('market_ranking') else None),
            'false_positive_candidates':len(set().union(*(set(v) for v in cols.values()))-set(top3)),
            'ordered_pair_capture':'EXACTA' in settlement['hit_types'],
            'exact_capture':'TRIFECTA' in settlement['hit_types'],
            'krs_utility':evaluate_against_result(arm['krs_utility'],official['top3'],static_ranking=ranking)}
    record={'profile':pre['profile'],'race_id':pre['race_id'],'policy_fingerprint':pre['policy_fingerprint'],
        'frozen_sha256':pre['sha256'],'git_commit_at':witness,'official_result_file_sha256':hashlib.sha256(result_path.read_bytes()).hexdigest(),
        'production_result_receipt_file_sha256':hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
        'signed_result_receipt_sha256':envelope['receipt_sha256'],'signed_result_verified':True,
        'official_result_raw_sha256':official['raw_sha256'],'result_captured_at':official['captured_at'],
        'arms':arms,'oos_eligible':True,'production_effect':'NONE','actual_purchase_inferred':False}
    if environment:
        record['environment_candidate']=pre['environment_candidate']
        record['base_policy_fingerprint']=pre['base_policy_fingerprint']
    record['sha256']=sha(record);save_immutable(target,record);return record


def cohort_metrics(eligible, *, include_environment=False):
    from pfs_grand_review import _aggregate, _robustness
    metrics={}
    names=('A_CURRENT','B_PEDIGREE_ENHANCED_SHADOW','C_BLOODLINE_ABLATION')
    if include_environment:names=names+(ENV_ARM,)
    for name in names:
        rows=[]
        for r in eligible:
            s=r['arms'][name]['settlement'];rows.append({'race_id':r['race_id'],'date':r['result_captured_at'],
                'investment':s['investment'],'return':s['return'],'profit_loss':s['profit_loss'],
                'hit_but_loss':bool(s['return'] and s['profit_loss']<0)})
        arm_records=[r['arms'][name] for r in eligible]
        fields=('winner_rank','winner_discovery_recall','p2_capture','p3_capture','top3_mean_rank',
            'ordered_pair_capture','exact_capture','candidate_width','false_positive_candidates',
            'market_winner_rank','market_top3_mean_rank')
        accuracy={}
        for field in fields:
            observed=[float(x[field]) for x in arm_records if x.get(field) is not None]
            accuracy[field]={'n':len(observed),'mean':sum(observed)/len(observed) if observed else None}
        rows.sort(key=lambda row:(row['date'],row['race_id']))
        metrics[name]={'aggregate':_aggregate(rows),'robustness':_robustness(rows),'prediction':accuracy}
    return metrics


def environment_scorecard(records, evaluations):
    """Never pool distinct fitted models, code or Production policy cohorts."""
    from jra_bvi_oos_metrics import aggregate
    cohorts={}
    for record in records:cohorts.setdefault(record['policy_fingerprint'],[]).append(record)
    current=policy_fingerprint()
    groups={}
    for key,rows in cohorts.items():
        selected=[e for e in evaluations if e['policy_fingerprint']==key]
        strata={}
        for field in ('venue','surface','distance_m','going'):
            buckets={}
            for row in rows:
                value=row['environment_candidate']['target_environment'].get(field)
                buckets.setdefault(str(value) if value is not None else 'MISSING',[]).append(row)
            strata[field]={value:cohort_metrics(part,include_environment=True) for value,part in buckets.items()}
        is_current=all(r.get('base_policy_fingerprint')==current for r in rows)
        groups[key]={'eligible_settled_races':len(rows),'race_ids':sorted(r['race_id'] for r in rows),
            'current_base_policy':is_current,'model_sha256':rows[0]['environment_candidate']['model_sha256'],
            'status':'INDEPENDENT_REVIEW_REQUIRED' if is_current and len(rows)>=30 else 'FORWARD OOS PENDING',
            'arms':cohort_metrics(rows,include_environment=True),
            'profile_metrics':aggregate(selected,include_environment=True),
            'controlled_pfs':environment_controlled_pfs(rows,selected),
            'environment_stability':strata,'automatic_promotion':False}
    largest=max((g['eligible_settled_races'] for g in groups.values() if g['current_base_policy']),default=0)
    return {'profile':ENV_PROFILE,'eligible_settled_races':largest,
        'eligible_count_basis':'LARGEST_SINGLE_MODEL_CODE_AND_CURRENT_POLICY_COHORT; NEVER_POOLED',
        'unpooled_race_count':len(records),'cohorts':groups,
        'arms':cohort_metrics([],include_environment=True),'required_forward_races':30,
        'status':'INDEPENDENT_REVIEW_REQUIRED' if largest>=30 else 'FORWARD OOS PENDING',
        'automatic_promotion':False,'production_effect':'NONE','predictive_improvement_demonstrated':False}


def environment_controlled_pfs(records, evaluations):
    """Same-race budget/count diagnostics; fractional units are never wagers."""
    from pfs_grand_review import _aggregate, _robustness
    names=('A_CURRENT','B_PEDIGREE_ENHANCED_SHADOW','C_BLOODLINE_ABLATION',ENV_ARM)
    by_id={r['race_id']:r for r in records}
    budgets={name:[] for name in names};counts={name:[] for name in names}
    for e in evaluations:
        rid=e['race_id'];record=by_id[rid]
        values={name:e['arms'][name]['equal_budget_return_per_yen'] for name in names}
        if all(v is not None for v in values.values()):
            for name,value in values.items():
                budgets[name].append({'race_id':rid,'date':record['result_captured_at'],
                    'investment':1.0,'return':value,'profit_loss':value-1.0,
                    'hit_but_loss':bool(0<value<1)})
        equal=e.get('equal_ticket') or {}
        if equal.get('status')=='FROZEN_PREFIX_DIAGNOSTIC':
            for name in names:
                s=equal['arms'][name]
                counts[name].append({'race_id':rid,'date':record['result_captured_at'],
                    'investment':s['investment'],'return':s['return'],'profit_loss':s['profit_loss'],
                    'hit_but_loss':bool(s['return'] and s['profit_loss']<0)})
    def measured(groups):
        return {name:{'aggregate':_aggregate(sorted(rows,key=lambda r:(r['date'],r['race_id']))),
            'robustness':_robustness(sorted(rows,key=lambda r:(r['date'],r['race_id'])))} for name,rows in groups.items()}
    return {'equal_budget':measured(budgets),'equal_ticket_count':measured(counts),
        'equal_budget_basis':'ONE_COMMON_VIRTUAL_UNIT_PER_SAME_RACE; ALL_FOUR_NONZERO_STAKES_REQUIRED',
        'equal_ticket_basis':'PREREGISTERED_FROZEN_PREFIX_MINIMUM_COUNT; NO_RESULT_SELECTION',
        'fractional_diagnostic_only':True,'actual_purchase_inferred':False,'production_effect':'NONE'}


def settle(root=ROOT, *, include_environment=False):
    records=[]
    evaluations=[]
    evaluation_refs=[]
    failures=[]
    from jra_bvi_oos_metrics import evaluate, aggregate
    paths=list((root/'runtime/jra_static_owner_forward_oos').glob('*/pedigree_pipeline_pre_result.json'))
    if include_environment:
        paths+=list((root/'runtime/jra_static_owner_forward_oos').glob('*/pedigree_env_pre_result.json'))
    for path in sorted(paths):
        try:
            record=_settle_record(path,root)
            if record is not None:
                pre=json.loads(path.read_text())
                result_path=root/'runtime/results'/f"{pre['race_id']}.json"
                raw=result_path.read_bytes()
                if hashlib.sha256(raw).hexdigest()!=record['official_result_file_sha256']:
                    raise ValueError('BVI_OOS_RESULT_CHANGED_AFTER_VERIFICATION')
                evaluation=evaluate(pre,json.loads(raw)['official_result'],record)
                evaluation['policy_fingerprint']=record['policy_fingerprint']
                evaluation['frozen_sha256']=pre['sha256']
                evaluation['official_result_file_sha256']=record['official_result_file_sha256']
                evaluation['sha256']=sha(evaluation)
                metric_code_sha=hashlib.sha256((ROOT/'runtime/jra_bvi_oos_metrics.py').read_bytes()).hexdigest()
                prefix='pedigree_env_evaluation_' if pre['profile']==ENV_PROFILE else 'pedigree_evaluation_'
                metric_path=path.with_name(prefix+metric_code_sha[:16]+'.json')
                save_immutable(metric_path,evaluation)
                evaluation_refs.append({'race_id':pre['race_id'],'policy_fingerprint':record['policy_fingerprint'],
                    'metrics_path':str(metric_path.relative_to(root)),'sha256':evaluation['sha256']})
                evaluations.append(evaluation);records.append(record)
        except (ValueError, KeyError, OSError, subprocess.SubprocessError) as exc:
            failures.append({'race_id':path.parent.name,'status':'HOLD','reason':str(exc)})
    environment_records=[r for r in records if r['profile']==ENV_PROFILE]
    environment_fingerprints={r['policy_fingerprint'] for r in environment_records}
    environment_evaluations=[e for e in evaluations if e['policy_fingerprint'] in environment_fingerprints]
    records=[r for r in records if r['profile']==PROFILE]
    evaluations=[e for e in evaluations if e['policy_fingerprint'] not in environment_fingerprints]
    if include_environment:
        env_score=environment_scorecard(environment_records,environment_evaluations)
        env_out=root/'runtime/jra_static_owner_forward_oos/pedigree_env_current.json'
        env_out.parent.mkdir(parents=True,exist_ok=True)
        env_out.write_text(json.dumps(env_score,ensure_ascii=False,indent=2)+'\n')
    eligible=[x for x in records if x['policy_fingerprint']==policy_fingerprint()]
    metrics=cohort_metrics(eligible)
    cohorts={}
    for record in records:
        cohorts.setdefault(record['policy_fingerprint'], []).append(record['race_id'])
    current_profiles=aggregate([e for e in evaluations if e['policy_fingerprint']==policy_fingerprint()])
    scorecard={'profile_capital_by_policy':{key:{profile:cohort_metrics([r for r in records if r['policy_fingerprint']==key and
            any(e['race_id']==r['race_id'] and e['race_profile']==profile for e in evaluations)])
            for profile in ('NEWCOMER','LOW_CAREER','ESTABLISHED','MIXED')} for key in cohorts},
        'profile_metrics':current_profiles, 'controlled_comparison_races':evaluation_refs,
        'historical_profile_cohorts':{key:aggregate([e for e in evaluations if e['policy_fingerprint']==key]) for key in cohorts},
        'race_failures':failures,'policy_cohorts':{key:{'eligible_settled_races':len(ids), 'race_ids':sorted(ids), 'current_policy':key==policy_fingerprint(), 'arms':cohort_metrics([r for r in records if r['policy_fingerprint']==key])} for key,ids in cohorts.items()},
        'profile':PROFILE,'eligible_settled_races':len(eligible),'arms':metrics,
        'status':'FORWARD OOS PENDING' if len(eligible)<30 else 'INDEPENDENT_REVIEW_REQUIRED',
        'required_forward_races':30,'automatic_promotion':False,'production_effect':'NONE',
        'predictive_improvement_demonstrated':False}
    if include_environment:scorecard['environment_candidate']=env_score
    out=root/'runtime/jra_static_owner_forward_oos/pedigree_pipeline_current.json';out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(scorecard,ensure_ascii=False,indent=2)+'\n');return scorecard


if __name__=='__main__':
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='action',required=True)
    f=sub.add_parser('freeze');f.add_argument('--request',type=Path,required=True);f.add_argument('--source',type=Path,required=True);f.add_argument('--output',type=Path,required=True)
    f.add_argument('--environment-model',type=Path)
    s=sub.add_parser('settle');s.add_argument('--environment',action='store_true');args=parser.parse_args()
    if args.action=='freeze':
        try:
            r=freeze(args.request,args.source,args.output,environment_model_path=args.environment_model)
        except Exception as exc:
            failure={'profile':PROFILE,'status':'NOT_FROZEN','first_failed_operation':'FORWARD_COMPARISON_FREEZE',
                'reason':type(exc).__name__+':'+str(exc),'recorded_at':datetime.now(timezone.utc).isoformat(),
                'request_path':str(args.request),'production_effect':'NONE','forward_oos_increment':0}
            p=ROOT/'runtime_out/jra_bvi_forward_freeze_failure.json';p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text(json.dumps(failure,ensure_ascii=False,indent=2)+'\n')
            raise
        print('BVI_FORWARD_PIPELINE_FROZEN',r['race_id'],r['sha256'])
    else:print(json.dumps(settle(include_environment=args.environment),ensure_ascii=False))

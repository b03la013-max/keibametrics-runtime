"""Reuse Single Entry artifacts for immutable, current-policy A/B/C forward OOS.

Never acquires extra race information or emits a Production FINAL. Late/partial
runs fail closed and cannot become eligible samples. Result evaluation uses the
existing official Production result lane; no optimizing on observed outcomes.
"""
from datetime import datetime, timezone, timedelta
from pathlib import Path
import argparse, copy, hashlib, json, subprocess, sys, urllib.request
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from jra_static_owner_forward_oos import sha, time, fingerprint, save_immutable
from jra_pedigree_corpus import _verified_source, _attested, build_corpus
from jra_owner_authorized_feature_rules import owner_authorized_observations
from jra_bvi_shadow_comparison import compare, execute_diagnostic_downstream
from family_authority_guard import resolve_current_authority
PROFILE='KM-JRA-BVI-CURRENT-POLICY-THREE-ARM-FORWARD-SHADOW-v1'


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
    ids=plan['cohort']['race_ids']
    if len(ids) not in (12,24,36) or len(set(ids))!=len(ids) or req['race_id'] not in ids:
        raise ValueError('BVI_SHADOW_PRIORITY_COHORT_UNVERIFIED')
    stop=min(time(req['prediction_cutoff'])-timedelta(seconds=120),now+timedelta(seconds=600))
    pending=[]
    schedule_path=root/f'runtime/jra_race_day_plan/{day}.schedule.json'
    schedule=json.loads(schedule_path.read_text()) if schedule_path.exists() else {}
    for rid in ids:
        if rid==req['race_id'] or rid in signed_final_ids:
            continue
        registration=json.loads((root/f'runtime/jra_race_registrations/{day}'/f'{rid}.json').read_text())
        from jra_race_day_registration import verify_registration
        post=time(registration['intake_intent']['scheduled_post_at'])
        verify_registration(registration,plan,race_id=rid,official_post=post)
        # Prefer the existing current-day schedule when the official post changes.
        if rid in schedule:post=time(schedule[rid]['post'])
        cutoff=post-timedelta(minutes=5)
        opening=post-timedelta(minutes=55)
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


def freeze(request, source_path, output):
    req=json.loads(request.read_text());now=require_open_window(req)
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
    comparison=compare(req,mapping,source_sha=source['source_snapshot_sha256'],receipt_sha=env['receipt_sha256'],
        algorithm_freeze_at=comparison_time.isoformat(),cutoff=req['prediction_cutoff'],
        source_artifact=source,current_authority=authority,root=ROOT,enhanced_features=enriched)
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
    record['sha256']=sha(record);save_immutable(output,record)
    return record


def persist_result_receipt(result_request, receipt, root=ROOT):
    """Called only after canonical Result Runner /verify succeeds.

    Preserve its unchanged signed response in the existing forward cohort;
    never create, resubmit or modify a historical RESULT or learning event.
    """
    if result_request.get('result_lane')!='PRODUCTION':return
    directory=root/'runtime/jra_static_owner_forward_oos'/result_request['race_id']
    if not (directory/'pedigree_pipeline_pre_result.json').exists():return
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
    pre=json.loads(path.read_text());target=path.with_name('pedigree_pipeline_result.json')
    if pre.get('profile')!=PROFILE or pre.get('sha256')!=sha({k:v for k,v in pre.items() if k!='sha256'}):
        raise ValueError('BVI_FORWARD_FROZEN_HASH_INVALID')
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
    record={'profile':PROFILE,'race_id':pre['race_id'],'policy_fingerprint':pre['policy_fingerprint'],
        'frozen_sha256':pre['sha256'],'git_commit_at':witness,'official_result_file_sha256':hashlib.sha256(result_path.read_bytes()).hexdigest(),
        'production_result_receipt_file_sha256':hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
        'signed_result_receipt_sha256':envelope['receipt_sha256'],'signed_result_verified':True,
        'official_result_raw_sha256':official['raw_sha256'],'result_captured_at':official['captured_at'],
        'arms':arms,'oos_eligible':True,'production_effect':'NONE','actual_purchase_inferred':False}
    record['sha256']=sha(record);save_immutable(target,record);return record


def cohort_metrics(eligible):
    from pfs_grand_review import _aggregate, _robustness
    metrics={}
    for name in ('A_CURRENT','B_PEDIGREE_ENHANCED_SHADOW','C_BLOODLINE_ABLATION'):
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


def settle(root=ROOT):
    records=[]
    evaluations=[]
    evaluation_refs=[]
    failures=[]
    from jra_bvi_oos_metrics import evaluate, aggregate
    for path in sorted((root/'runtime/jra_static_owner_forward_oos').glob('*/pedigree_pipeline_pre_result.json')):
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
                metric_path=path.with_name('pedigree_evaluation_'+metric_code_sha[:16]+'.json')
                save_immutable(metric_path,evaluation)
                evaluation_refs.append({'race_id':pre['race_id'],'policy_fingerprint':record['policy_fingerprint'],
                    'metrics_path':str(metric_path.relative_to(root)),'sha256':evaluation['sha256']})
                evaluations.append(evaluation);records.append(record)
        except (ValueError, KeyError, OSError, subprocess.SubprocessError) as exc:
            failures.append({'race_id':path.parent.name,'status':'HOLD','reason':str(exc)})
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
    out=root/'runtime/jra_static_owner_forward_oos/pedigree_pipeline_current.json';out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(scorecard,ensure_ascii=False,indent=2)+'\n');return scorecard


if __name__=='__main__':
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='action',required=True)
    f=sub.add_parser('freeze');f.add_argument('--request',type=Path,required=True);f.add_argument('--source',type=Path,required=True);f.add_argument('--output',type=Path,required=True)
    sub.add_parser('settle');args=parser.parse_args()
    if args.action=='freeze':
        try:
            r=freeze(args.request,args.source,args.output)
        except Exception as exc:
            failure={'profile':PROFILE,'status':'NOT_FROZEN','first_failed_operation':'FORWARD_COMPARISON_FREEZE',
                'reason':type(exc).__name__+':'+str(exc),'recorded_at':datetime.now(timezone.utc).isoformat(),
                'request_path':str(args.request),'production_effect':'NONE','forward_oos_increment':0}
            p=ROOT/'runtime_out/jra_bvi_forward_freeze_failure.json';p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text(json.dumps(failure,ensure_ascii=False,indent=2)+'\n')
            raise
        print('BVI_FORWARD_PIPELINE_FROZEN',r['race_id'],r['sha256'])
    else:print(json.dumps(settle(),ensure_ascii=False))

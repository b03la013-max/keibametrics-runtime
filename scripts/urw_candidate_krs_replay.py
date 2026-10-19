"""URW contract/conditional-model research, never a Production dispatcher.

Requires the original seven Actions archives and the independently pinned Engine
reference. Archive/fit modes make no network calls, signatures or Runtime
requests. Conditional fitting is explicitly NON-PRODUCTION. Forecast/Engine
outputs are persisted before the separate validation-label pass.
"""
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from zipfile import ZipFile
import argparse
import base64
import gzip
import hashlib
import json
import subprocess
import sys
import time
import copy

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'runtime')]
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from runtime.local_fullnumerical_production import materialize_production
from runtime.local_numerical_authority_gate import assess
from runtime.local_race_key_shadow_owner import compile_urw_candidate, audit_urw_candidate_paper_pipeline, _sha
from runtime.krs_prediction_utility import build_krs_prediction_utility, evaluate_against_result
from runtime.mec_r4_shadow import settle_ticket_list

ENGINE = '9929df994aa7964173edef9af7e9a705628ce377babf22df3af4e280fc275421'
PARAMETERS = 'd8c027ee5bcc8fd3d2c248e8059b341776be38910e833d7589f09ab817c161f5'
KEY = 'jqWqOYlmhXXmpv/nR7lx3c2n/S5shDYava/WJVxn4kE='
ARCHIVES = {
    35831609334: '65c7b3b61f1034ee7744a074014e7343f2f681416630aa9d7a783da818693c9d',
    35840245134: '57fbecf198a2093ab350c0a504d1996c6935ee5db66be554d37b97a17fba2c56',
    35845291112: 'b95ac312dc2658e1ba264eb293f71a2e3aa1f20da9d1002c9c51199024962bcc',
    35847691817: '3729ecbd26afbf3e8437804a23242940b4d25383484f3c236ba1336ec5d152ab',
    35961138259: 'ed759ed1086c72f6c5a16c07cedc76c5a35a2f52a7857062b7796d4a9d4bc04c',
    35978840734: '848612bed0b2d79bb191ee40a24318ff0af3b2d56349b5b66795acb084cb3dce',
    35984798580: '557b93a09b31f59dd1db364f3124d2a28df4c222c8dd1296f9e24aec92512e8a',
}


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n')


def audit_index_consumption(numerical):
    """Result-blind finite interventions on the existing Candidate baseline.

    These unsigned 0/100 counterfactuals measure code dependence, not plausible
    feature changes, predictive value, calibration or Production authority.
    Preserve RULED-NEUTRAL state and provenance; never save as materialized
    SOURCE or feed these synthetic values to the Runtime/Engine.
    """
    from runtime.local_krs_bridge_candidate import build_candidate_prediction_structure_derived as predict
    rows=numerical['runners']
    base=predict({'runners':copy.deepcopy(rows)})['candidate_static_prediction']
    scores={x['runner_id']:x for x in base['runner_scores']}
    indices=[]
    for name in numerical.get('required_indices') or numerical['candidate_full_numerical_summary']['required_indices']:
        cells=[]
        for offset,row in enumerate(rows):
            rid=str(row['runner_id']);cell=row['canonical_components'][name]
            interventions=[]
            for value in (0,100):
                changed=copy.deepcopy(rows)
                changed[offset]['canonical_components'][name]['value']=value
                observed=predict({'runners':changed})['candidate_static_prediction']
                score=next(x for x in observed['runner_scores'] if x['runner_id']==rid)
                interventions.append({'unsigned_synthetic_value':value,
                    'role_score_deltas':{k:score[k]-scores[rid][k] for k in ('w_score','p2_score','p3_score')},
                    'ranking_changed':observed['ranking']!=base['ranking'],
                    'roles_changed':observed['roles']!=base['roles']})
            cells.append({'runner_id':rid,'value':cell['value'],'terminal_status':cell['terminal_status'],
                'rule_id':cell['rule_id'],'mapping_version':cell['mapping_version'],
                'evidence_refs':cell['evidence_refs'],'source_fact':cell['source_fact'],
                'cell_sha256':_sha(cell),'interventions':interventions,
                'production_consumption_authorized':False})
        indices.append({'index':name,'cells':cells,
            'candidate_score_dependence':any(any(v!=0 for v in q['role_score_deltas'].values()) for c in cells for q in c['interventions']),
            'ranking_changed_cases':sum(q['ranking_changed'] for c in cells for q in c['interventions']),
            'role_changed_cases':sum(q['roles_changed'] for c in cells for q in c['interventions'])})
    out={'classification':'UNSIGNED_SYNTHETIC_CODE_SENSITIVITY_NOT_PREDICTIVE_VALUE_NOT_OOS',
        'race_id':numerical['race_id'],'source_snapshot_sha256':(numerical.get('production_evidence_compiler') or numerical['candidate_evidence_compiler'])['source_snapshot_sha256'],
        'original_numeric_provenance_sha256':numerical.get('index_provenance_hash') or numerical['candidate_index_provenance_sha256'],
        'candidate_baseline':base,'indices':indices,'index_count':len(indices),
        'score_consumed_indices':[x['index'] for x in indices if x['candidate_score_dependence']],
        'production_consumption_authorized':False,'runtime_post_count':0,
        'prediction_value_increment':'UNKNOWN_REQUIRES_FROZEN_FORWARD_COMPARISON'}
    out['sha256']=_sha(out)
    return out


def frozen_feature_packs(path, *, urw_transfer=False):
    """Reuse the immutable signed-SOURCE-derived feature audit, not labels."""
    from runtime.local_race_key_shadow_owner import owner_feature_pack
    raw=path.read_bytes()
    original=json.loads(gzip.decompress(raw));packs=[]
    for f in original['forecasts'].values():
        c=f['candidate'];audit=f['index_consumption_audit']
        rows={rid:{'runner_id':rid,'canonical_components':{}} for rid in c['ranking']}
        # Reconstitute exactly the ORIGINAL cells from the stored audit. The
        # unsigned0/100 interventions are deliberately not read here.
        for index in audit['indices']:
            for cell in index['cells']:
                cc={k:cell[k] for k in ('value','terminal_status','rule_id','mapping_version','evidence_refs','source_fact')}
                # Some original cells have additional provenance; retain exact
                # hash by recovering the production cell from the bound SOURCE
                # materializer when available, or use the audit's separate hash.
                rows[cell['runner_id']]['canonical_components'][index['index']]=cc
        n={'race_id':c['race_id'],'runners':list(rows.values()),
            'production_evidence_compiler':{'source_snapshot_sha256':c['source_snapshot_sha256']}}
        # Audit cells expose a subset of the original provenance. Bind this
        # explicit derived representation, never pass it as Production material.
        derived=copy.deepcopy(c)
        derived['numeric_provenance_sha256']=_sha([r['canonical_components'] for r in n['runners']])
        derived['sha256']=_sha({k:v for k,v in derived.items() if k!='sha256'})
        pack=owner_feature_pack(derived,n,urw_transfer=urw_transfer)
        pack['original_candidate_sha256']=c['sha256'];pack['source_audit_sha256']=hashlib.sha256(raw).hexdigest()
        pack['original_cell_sha256']={index['index']:{cell['runner_id']:cell['cell_sha256'] for cell in index['cells']}
                                     for index in audit['indices']}
        pack['sha256']=_sha({k:v for k,v in pack.items() if k!='sha256'});packs.append(pack)
    return sorted(packs,key=lambda p:p['scheduled_post_at'])


def ranker_audit(output, *, urw_transfer=False):
    """Chronological retrospective comparison; validation labels read last."""
    from runtime.local_race_key_shadow_owner import fit_conditioned_owner,predict_conditioned_owner
    protocol_path=ROOT/'research/urw_owner/20261019_conditional_model/protocol.json'
    protocol=json.loads(protocol_path.read_text())
    packs=frozen_feature_packs(ROOT/'research/urw_owner/20261019_condition_consumption/evidence_audit.json.gz',urw_transfer=urw_transfer)
    training=[p for p in packs if p['race_date']<=protocol['training_through']]
    validation=[p for p in packs if p['race_date']>=protocol['validation_from']]
    assert len(training)==3 and len(validation)==3
    def labels_for(p):
        paths=sorted((ROOT/'runtime/family_result_requests').glob(p['race_id'].replace('-FORMAL-R1','')+'-RESULT-R*.json'))
        record=json.loads(paths[-1].read_text())
        assert record['race_id']==p['race_id']
        return list(map(str,record['finish_order'][:3])),{'path':str(paths[-1].relative_to(ROOT)),
            'sha256':hashlib.sha256(paths[-1].read_bytes()).hexdigest(),
            'official_verified_recorded':record.get('official_result_verified') is True,
            'label_time_available_before_historical_target':'UNKNOWN_NOT_PREQUENTIAL_CREDIT'}
    train_labels={p['race_id']:labels_for(p)[0] for p in training}
    models={};forecasts={}
    arms={'URW_TRANSFER_V2':{'stage_evidence':True,'interactions':True}} if urw_transfer else protocol['arms']
    if urw_transfer:
        # Keep the rejected v1 fits and their forecasts immutable. Only the
        # diagnosed transfer-input repair is fitted, using the same train set.
        frozen_path=ROOT/'research/urw_owner/20261019_conditional_model/forecasts_before_evaluation.json.gz'
        old=json.loads(gzip.decompress(frozen_path.read_bytes()))
        old_report=json.loads((frozen_path.parent/'ranker_report.json').read_text())
        if hashlib.sha256(frozen_path.read_bytes()).hexdigest()!=old_report['forecast_artifact_sha256']:
            raise ValueError('URW_PRIOR_FROZEN_MODEL_HASH_MISMATCH')
        forecasts=copy.deepcopy(old['forecasts'])
    for arm,spec in arms.items():
        model=fit_conditioned_owner(training,train_labels,**spec);models[arm]=model
        forecasts[arm]={p['race_id']:predict_conditioned_owner(model,p,historical_replay=True) for p in validation}
    output.mkdir(parents=True,exist_ok=False)
    frozen={'protocol_sha256':hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
        'compiled_at':datetime.now(timezone.utc).isoformat(),'models':models,'forecasts':forecasts,
        'training_features':[p['sha256'] for p in training],'validation_features':[p['sha256'] for p in validation],
        'classification':'RETROSPECTIVE_CHRONOLOGICAL_HOLDOUT_NOT_UNSEEN_RESEARCHER_NOT_FORWARD',
        'limits':'Historical validation labels have appeared in earlier repository reports. No researcher-blind validation or calibrated quality is claimed. Neither scaling, penalty selection nor fitting receives validation inputs or labels.'}
    if urw_transfer:
        frozen['prior_frozen_forecasts_sha256']=hashlib.sha256(frozen_path.read_bytes()).hexdigest()
        frozen['input_repair']='Retain newer dirt transfers beside direct history; distance-specific position paths; latest distance delta and distance/draw interaction. No fixed new scores.'
    packed=gzip.compress(json.dumps(frozen,ensure_ascii=False,sort_keys=True).encode(),mtime=0)
    (output/'forecasts_before_evaluation.json.gz').write_bytes(packed)
    # Only after the immutable forecast artifact exists does evaluation read
    # validation labels. No best-arm selection or coefficient adjustment follows.
    import math
    rows=[];sums={arm:{'races':0,'winner_top1':0,'winner_top3':0,'W':0,'P2':0,'P3':0,
        'ordered_pair_top1':0,'exact_top1':0,'exact_top5':0,'top3_joint_nll':0.} for arm in ['BASELINE',*forecasts]}
    for key in ('ordered_pair_top1','exact_top1','exact_top5','top3_joint_nll'):sums['BASELINE'][key]=None
    uniform_nll=0.
    for p in validation:
        actual,ref=labels_for(p);rid=p['race_id'];base=p['baseline']
        n=len(p['runners']);uniform_nll+=math.log(n*(n-1)*(n-2))
        b=sums['BASELINE'];b['races']+=1;b['winner_top1']+=base['ranking'][0]==actual[0];b['winner_top3']+=actual[0] in base['ranking'][:3]
        for role,horse in zip(('W','P2','P3'),actual):b[role]+=horse in base[role]
        row={'race_id':rid,'label_provenance':ref,'actual_top3':actual,'arms':{}}
        for arm,predictions in forecasts.items():
            pred=predictions[rid];score=sums[arm];score['races']+=1
            score['winner_top1']+=pred['ranking'][0]==actual[0];score['winner_top3']+=actual[0] in pred['ranking'][:3]
            for role,horse in zip(('W','P2','P3'),actual):score[role]+=role in pred['role_columns'][horse]
            pair=pred['ordered_pairs'][0];triple=pred['ordered_triples'][0]
            score['ordered_pair_top1']+=[pair['head'],pair['second']]==actual[:2]
            score['exact_top1']+=[triple['head'],triple['second'],triple['third']]==actual
            score['exact_top5']+=any([t['head'],t['second'],t['third']]==actual for t in pred['ordered_triples'][:5])
            mass=next(t['model_mass'] for t in pred['ordered_triples'] if [t['head'],t['second'],t['third']]==actual)
            score['top3_joint_nll']-=math.log(max(mass,1e-300))
            def conditional_changes(distributions):
                # Excluding a different head/pair changes the list even for an
                # independent model. Compare only COMMON alternatives: odds
                # changes and order reversals expose actual conditioning.
                from itertools import combinations
                max_shift=0.;reversals=0;comparisons=0
                for a,b in combinations(distributions.values(),2):
                    for x,y in combinations(sorted(set(a)&set(b)),2):
                        first=math.log(max(a[x],1e-300)/max(a[y],1e-300))
                        second=math.log(max(b[x],1e-300)/max(b[y],1e-300))
                        max_shift=max(max_shift,abs(first-second));comparisons+=1
                        reversals+=first*second<0 and min(abs(first),abs(second))>1e-10
                return {'common_alternative_comparisons':comparisons,'order_reversals':reversals,'max_logodds_shift':max_shift}
            row['arms'][arm]={'prediction_sha256':pred['sha256'],'actual_exact_model_rank':next(i+1 for i,t in enumerate(pred['ordered_triples']) if [t['head'],t['second'],t['third']]==actual),
                'actual_winner_model_rank':pred['ranking'].index(actual[0])+1,
                'head_conditioning':conditional_changes(pred['p2_model_mass_given_head']),
                'pair_conditioning':conditional_changes(pred['p3_model_mass_given_pair']),
                'material_exact_evidence':False}
        rows.append(row)
    report={'protocol':protocol,'forecast_artifact_sha256':hashlib.sha256(packed).hexdigest(),
        'training_races':[p['race_id'] for p in training],'validation_races':[p['race_id'] for p in validation],
        'original_selected_denominator':7,'training_completed':3,'validation_completed':3,'input_hold_retained':1,
        'metrics':sums,'validation_rows':rows,'production_changes':False,'runtime_post_count':0,'genuine_forward_oos':0,
        'uniform_ordered_top3_reference_nll':uniform_nll,
        'adoption':'REJECTED_FOR_PRODUCTION_NO_WINNER_ROLE_CAPTURE_GAIN',
        'training_label_limit':'Sep23 stored labels were unverified in historical metadata; fresh official refetch required for empirical acceptance. Diagnostic fitting is not proof of true outcome or Publication Time.'}
    report['sha256']=_sha(report);dump(output/'ranker_report.json',report)
    print(json.dumps({'metrics':sums,'disposition':report['adoption']}))



def refetch_historical_labels(output):
    """Official GET checks after forecasts are frozen; no fitting or settlement.

    Preserve the old records. A mismatch invalidates the retrospective quality
    claim rather than changing labels, forecasts or a Production/OOS ledger.
    """
    sys.path.insert(0,str(ROOT/'runtime/local_physical'))
    from runtime.local_physical.nar_source_manifest import _result_source,LOCAL_BABA_CODES
    from runtime.local_physical.source_acquisition import fetch_source
    from runtime.formal_execution_orchestrator import parse_official_result_snapshot
    frozen=ROOT/'research/urw_owner/20261019_conditional_model/forecasts_before_evaluation.json.gz'
    report_path=ROOT/'research/urw_owner/20261019_conditional_model/ranker_report.json'
    forecast_sha=hashlib.sha256(frozen.read_bytes()).hexdigest()
    evaluation=json.loads(report_path.read_text())
    assert evaluation['forecast_artifact_sha256']==forecast_sha
    packs=frozen_feature_packs(ROOT/'research/urw_owner/20261019_condition_consumption/evidence_audit.json.gz')
    output.mkdir(parents=True,exist_ok=False)
    def check(p):
        import re
        rid=p['race_id'];race_no=int(re.search(r'-R(\d+)-FORMAL',rid).group(1))
        row={'race_id':rid,'role':'TRAINING' if p['race_date']=='2026-09-23' else 'VALIDATION'}
        paths=sorted((ROOT/'runtime/family_result_requests').glob(rid.replace('-FORMAL-R1','')+'-RESULT-R*.json'))
        record=json.loads(paths[-1].read_text());stored=list(map(str,record['finish_order'][:3]))
        row.update(stored_top3=stored,stored_path=str(paths[-1].relative_to(ROOT)),
                   stored_sha256=hashlib.sha256(paths[-1].read_bytes()).hexdigest())
        try:
            spec=_result_source('URW',LOCAL_BABA_CODES['URW'],p['race_date'].replace('-','/'),race_no)
            snapshot,errors=fetch_source(spec,'')
            dump(output/(rid+'.official_snapshot.json'),snapshot)
            if errors:raise ValueError('OFFICIAL_RESULT_SOURCE_ERRORS:'+','.join(errors))
            order,payouts=parse_official_result_snapshot(snapshot,
                {'venue_id':'URW','race_date':p['race_date'],'race_no':race_no},list(p['runners']))
            actual=list(map(str,order[:3]));matches=actual==stored
            row.update(status='VERIFIED_CURRENT_OFFICIAL_LABEL' if matches else 'HOLD_STORED_LABEL_MISMATCH',
                official_top3=actual,stored_matches_official=matches,
                official_raw_sha256=snapshot['raw_sha256'],fetched_at=snapshot['fetched_at'],
                official_payouts=payouts)
        except (ValueError,KeyError,TypeError,OSError,RuntimeError) as exc:
            row.update(status='HOLD_OFFICIAL_LABEL_UNVERIFIED',error=str(exc))
        return row
    with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(check,packs))
    result={'classification':'READ_ONLY_FRESH_OFFICIAL_RESULT_CHECK_NOT_SETTLEMENT_NOT_OOS',
        'forecast_artifact_sha256':forecast_sha,'selected_denominator':7,'complete_feature_races':len(packs),
        'retained_input_hold':1,'rows':rows,'verified_labels':sum(x.get('stored_matches_official') is True for x in rows),
        'historical_publication_times':'UNKNOWN_NOT_PREQUENTIAL_CREDIT',
        'runtime_post_count':0,'existing_record_changes':False,'refit_performed':False,
        'compiled_at':datetime.now(timezone.utc).isoformat()}
    result['status']='VERIFIED_CURRENT_OFFICIAL_LABELS' if result['verified_labels']==len(packs) else 'HOLD_LABEL_PROVENANCE'
    result['sha256']=_sha(result);dump(output/'official_label_verification.json',result)
    print(json.dumps(result,ensure_ascii=False))


def declared_snapshot_shadow(output, source_path, plan_path, *, race_no=1):
    """Offline Oct19 URW diagnostic from original public snapshot bytes.

    This cannot acquire SOURCE, upgrade a status, sign, dispatch or publish
    tickets. Old source times remain old; the real prediction clock is used.
    The strict verified-active public-shadow path remains separate.
    """
    from runtime.local_physical.source_acquisition import verify_source_artifact
    from runtime.local_physical.nar_runner_universe import enrich_source_artifact
    from runtime.local_nar_evidence_candidate import compile_candidate_evidence
    from runtime.local_fullnumerical_candidate import materialize_candidate
    from runtime.local_production_static_owner import _card_heading
    from runtime.local_race_key_shadow_owner import compile_public_venue_candidate,owner_feature_pack,predict_conditioned_owner
    from runtime.local_krs_bridge_candidate import build_candidate_prediction_structure_derived,build_candidate_krs
    started=datetime.now(timezone.utc)
    plan=json.loads(plan_path.read_text())
    if (plan.get('family_id')!='LOCAL' or plan.get('venue_id')!='URW' or plan.get('race_date')!='2026-10-19'
            or plan.get('plan_sha256')!=_sha({k:v for k,v in plan.items() if k!='plan_sha256'})):
        raise ValueError('DECLARED_SHADOW_PLAN_HASH_OR_SCOPE')
    chosen=[r for r in plan['races'] if r['fields']['race_no']==race_no]
    if len(chosen)!=1:raise ValueError('DECLARED_SHADOW_PLAN_RACE')
    fields=chosen[0]['fields']
    from datetime import timedelta
    if (fields.get('venue_id')!='URW' or fields.get('race_date')!='2026-10-19'
            or fields.get('race_no')!=race_no or datetime.fromisoformat(fields['prediction_cutoff'])<=started
            or datetime.fromisoformat(fields['scheduled_post_at'])-datetime.fromisoformat(fields['prediction_cutoff'])!=timedelta(seconds=120)):
        raise ValueError('DECLARED_SHADOW_SCOPE_OR_CUTOFF')
    raw=source_path.read_bytes();source=json.loads(raw)
    valid,errors=verify_source_artifact(source)
    if not valid:raise ValueError('DECLARED_SHADOW_ORIGINAL_HASH:'+','.join(errors))
    original_sha=source['source_snapshot_sha256']
    source['source_race_context']={k:fields[k] for k in ('venue_id','race_date','race_no')}
    source=enrich_source_artifact(source)
    source['source_snapshot_sha256']=_sha({k:v for k,v in source.items() if k!='source_snapshot_sha256'})
    identity=lambda rows:sorted((str(r['runner_id']),r['name']) for r in rows)
    declared=source['declared_runner_universe']['runners']
    if identity(declared)!=identity(chosen[0]['declared_runner_universe']['runners']):
        raise ValueError('DECLARED_SHADOW_UNIVERSE_CHANGED')
    header=_card_heading(source)
    req={**fields,'family_id':'LOCAL','race_id':source['race_id'],'execution_id':source['race_id'],
        'runners':declared,'race':{'racecourse':'浦和','date':fields['race_date'],
            'race_no':race_no,'prediction_id':source['race_id'],
            'distance':header['distance'],'surface':'DIRT','class':header['class']}}
    n=materialize_candidate(compile_candidate_evidence(source,req))
    n=build_candidate_prediction_structure_derived(n)
    c=compile_public_venue_candidate(req,source,n,declared_snapshot_shadow=True)
    p=owner_feature_pack(c,n)
    bridge=build_candidate_krs(n)
    # Reuse byte-bound pre-existing v1 fits, never the rejected transfer refit.
    old_path=ROOT/'research/urw_owner/20261019_conditional_model/forecasts_before_evaluation.json.gz'
    old_bytes=old_path.read_bytes()
    expected=json.loads((old_path.parent/'ranker_report.json').read_text())['forecast_artifact_sha256']
    if hashlib.sha256(old_bytes).hexdigest()!=expected:raise ValueError('DECLARED_SHADOW_FROZEN_MODEL_HASH')
    model=json.loads(gzip.decompress(old_bytes))['models']['CONDITIONAL_STAGE']
    prediction=predict_conditioned_owner(model,p)
    prediction.update(temporal_class='UNSIGNED_FROZEN_DECLARED_SNAPSHOT_SHADOW',
        source_signature_eligibility='HOLD_UNSIGNED_AND_NOT_VERIFIED_ACTIVE',
        model_disposition='PRE_EXISTING_REJECTED_MODEL_DIAGNOSTIC_ONLY_NO_PROMOTION',forward_oos_credit=0)
    prediction['sha256']=_sha({k:v for k,v in prediction.items() if k!='sha256'})
    completed=datetime.now(timezone.utc)
    if completed>=datetime.fromisoformat(fields['prediction_cutoff']):raise ValueError('DECLARED_SHADOW_COMPLETED_AFTER_CUTOFF')
    report={'classification':'UNSIGNED_FROZEN_DECLARED_SNAPSHOT_SHADOW_NOT_LIVE_NOT_OOS',
        'race_id':source['race_id'],'fields':fields,'started_at':started.isoformat(),'frozen_at':completed.isoformat(),
        'plan_sha256':plan['plan_sha256'],'plan_is_activation_authority':False,
        'original_input_file_sha256':hashlib.sha256(raw).hexdigest(),'original_source_artifact_sha256':original_sha,
        'source_freeze_at':source['source_freeze_at'],'source_age_seconds':c['source_age_seconds'],
        'runner_universe_basis':'DECLARED_NOT_VERIFIED_ACTIVE','runner_count':len(declared),
        'runner_status_registry':source['runner_status_registry'],'summary':n['candidate_full_numerical_summary'],
        'candidate_sha256':c['sha256'],'prediction_sha256':prediction['sha256'],
        'krs_input_sha256':bridge['candidate_krs_input_sha256'],'prediction_frozen':True,
        'krs_engine_executed':False,'krs_stop':'PINNED_ENGINE_FILE_UNAVAILABLE_LOCALLY_RUNTIME_POST_NOT_AUTHORIZED',
        'formal_first_stop':'URW_PRODUCTION_OWNER_QUALITY_AND_SCOPE_NOT_ESTABLISHED',
        'source_freshness_claim':False,'production_authority':False,'formal_registration_count':0,
        'signed_source_count':0,'signed_final_count':0,'delivery_verified':False,'tickets':[],
        'runtime_post_count':0,'forward_oos_credit':0,'new_paid_api_requests':0,'new_model_fits':0}
    report['sha256']=_sha(report)
    bundle={'source_artifact':source,'numerical':n,'candidate':c,'features':p,
        'prediction':prediction,'krs_input':bridge['candidate_krs_input_data'],'report':report}
    output.mkdir(parents=True,exist_ok=False)
    (output/'snapshot_prediction.json.gz').write_bytes(gzip.compress(json.dumps(bundle,ensure_ascii=False,sort_keys=True).encode(),mtime=0))
    dump(output/'snapshot_shadow_status.json',report)
    print(json.dumps({'status':report['classification'],'race_id':report['race_id'],'frozen_at':report['frozen_at'],
        'runners':len(declared),'numerical_cells':report['summary']['terminalized_count'],'formal_final':0,'forward_oos_credit':0}))
    return report


def freeze_public_research_handoff(output, source, numerical, candidate):
    """Preserve an unsigned baseline, uniform reference and KRS INPUT only."""
    from runtime.local_krs_bridge_candidate import build_candidate_krs
    from runtime.local_production_static_owner import _card_heading
    if (candidate.get('venue_id')!='URW' or candidate.get('production_authority') is not False
            or candidate.get('source_snapshot_sha256')!=source.get('source_snapshot_sha256')
            or candidate.get('race_id')!=numerical.get('race_id')
            or datetime.now(timezone.utc)>=datetime.fromisoformat(candidate['prediction_cutoff'])):
        raise ValueError('PUBLIC_URW_HANDOFF_BINDING_OR_CUTOFF')
    base=candidate['existing_local_baseline'];rows=copy.deepcopy(numerical['runners'])
    for row in rows:row['candidate_static_roles']=list(base['roles'][str(row['runner_id'])])
    header=_card_heading(source)
    bridge=build_candidate_krs({'race':{'prediction_id':candidate['race_id'],'racecourse':'浦和',
        'date':candidate['race_date'],'race_no':candidate['race_no'],'venue':'URW',
        'course_rule_version':candidate['venue_canon'],'distance':header['distance'],'surface':'dirt','course':'left'},
        'runners':rows,'candidate_full_numerical_summary':{'numeric_transport_complete':True,
            'mapping_id':numerical['production_numerical_authority']['mapping_id'],
            'sha256':numerical['production_numerical_summary']['sha256']},
        'candidate_current_state':copy.deepcopy(numerical.get('numerical_current_state') or {}),
        'candidate_environment':copy.deepcopy(numerical.get('numerical_environment') or {})})
    count=len(rows)
    uniform={'model':'UNIFORM_WITHOUT_REPLACEMENT','feature_count':0,'fitted_parameters':0,
        'winner_mass':1/count,'p2_given_head_mass':1/(count-1),'p3_given_pair_mass':1/(count-2),
        'ranked_discrimination':'NONE_ALL_TIES','production_authority':False}
    uniform['sha256']=_sha(uniform)
    pairs=[[h,s] for h in base['W'] for s in base['P2'] if h!=s]
    triples=[[h,s,t] for h,s in pairs for t in base['P3'] if t not in (h,s)]
    handoff={'classification':'UNSIGNED_PRESTART_RESEARCH_INPUTS_NOT_FORMAL_TICKETS_NOT_FORWARD',
        'frozen_at':datetime.now(timezone.utc).isoformat(),'original_candidate_frozen_at':candidate['frozen_at'],
        'race_id':candidate['race_id'],'source_sha256':source['source_snapshot_sha256'],
        'candidate_sha256':candidate['sha256'],'baseline':base,
        'baseline_implementation_sha256':hashlib.sha256((ROOT/'runtime/local_krs_bridge_candidate.py').read_bytes()).hexdigest(),
        'uniform_reference':uniform,'candidate_ordered_pairs':pairs,'candidate_ordered_triples':triples,
        'candidate_stakes':None,'capital_yen':None,'material_exact_evidence':False,
        'candidate_krs_input':bridge['candidate_krs_input_data'],
        'candidate_krs_input_sha256':bridge['candidate_krs_input_sha256'],
        'krs_engine_executed':False,'runtime_post_count':0,'signed_source_count':0,
        'signed_final_count':0,'formal_ticket_count':0,'production_authority':False,'forward_oos_credit':0}
    if datetime.fromisoformat(handoff['frozen_at'])>=datetime.fromisoformat(candidate['prediction_cutoff']):
        raise ValueError('PUBLIC_URW_HANDOFF_COMPLETED_AFTER_CUTOFF')
    handoff['sha256']=_sha(handoff)
    path=output/'public_research_handoff.json.gz'
    if path.exists():raise ValueError('PUBLIC_URW_HANDOFF_ALREADY_FROZEN')
    path.write_bytes(gzip.compress(json.dumps(handoff,ensure_ascii=False,sort_keys=True).encode(),mtime=0))
    return handoff


def fetch_public_urw_reference(spec, prediction_cutoff=''):
    """Official URW GET for unsigned reference/planning, never Production SOURCE.

    Reuse snapshot extraction while keeping this proxy transport separate from
    the Production DNS/SSRF verifier. No credentials, redirects or Runtime POST.
    Robots permission and per-origin pacing are required before the target GET.
    """
    import urllib.request
    import re
    from urllib.parse import urlparse, parse_qs
    from runtime.local_physical.source_acquisition import snapshot_from_bytes
    from runtime.urw_reference_source_policy import open_public_urw_source, USER_AGENT
    from runtime.local_race_key_intake import JST
    from datetime import date
    url=urlparse(spec['url']); q=parse_qs(url.query)
    day=(q.get('k_raceDate') or [''])[0].replace('/','-')
    try:
        selected=date.fromisoformat(day)
    except ValueError as exc:
        raise ValueError('PUBLIC_URW_REFERENCE_URL_SCOPE') from exc
    if (url.scheme!='https' or url.netloc!='www.keiba.go.jp'
            or url.path not in {'/KeibaWeb/TodayRaceInfo/DebaTable',
                '/KeibaWeb/TodayRaceInfo/OddsTanFuku','/KeibaWeb/TodayRaceInfo/RaceList'}
            or url.fragment or q.get('k_babaCode')!=['18'] or len(q.get('k_raceDate',[]))!=1
            or len(q.get('k_raceNo',[]))!=1 or not re.fullmatch(r'(?:[1-9]|1[0-2])',q['k_raceNo'][0])
            or selected < datetime.now(timezone.utc).astimezone(JST).date()
            or spec.get('official') is not True or spec.get('authority')!='NAR_OFFICIAL'):
        raise ValueError('PUBLIC_URW_REFERENCE_URL_SCOPE')
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,*args,**kwargs):
            raise ValueError('PUBLIC_URW_CAPTURE_REDIRECT_FORBIDDEN')
    opener=urllib.request.build_opener(NoRedirect())
    req=urllib.request.Request(spec['url'],headers={
        'User-Agent':USER_AGENT,'Accept':'text/html','Accept-Language':'ja'},method='GET')
    with open_public_urw_source(opener,req,timeout=15) as response:
        if response.geturl()!=spec['url'] or response.status!=200:
            raise ValueError('PUBLIC_URW_CAPTURE_RESPONSE_IDENTITY')
        headers={k.lower():v for k,v in response.headers.items()}
        if not headers.get('content-type','').lower().startswith('text/html'):
            raise ValueError('PUBLIC_URW_CAPTURE_CONTENT_TYPE')
        raw=response.read(spec['max_bytes']+1)
        if len(raw)>spec['max_bytes']:raise ValueError('PUBLIC_URW_CAPTURE_MAX_BYTES')
        if headers.get('content-encoding','').lower()=='gzip':
            raw=gzip.decompress(raw)
            if len(raw)>spec['max_bytes']:raise ValueError('PUBLIC_URW_CAPTURE_MAX_BYTES')
    completed=datetime.now(timezone.utc)
    if prediction_cutoff and completed>=datetime.fromisoformat(prediction_cutoff):
        raise ValueError('PUBLIC_URW_CAPTURE_COMPLETED_AFTER_CUTOFF')
    return snapshot_from_bytes(spec,raw,final_url=spec['url'],status_code=200,
        headers=headers,fetched_at=completed.isoformat(),prediction_cutoff=prediction_cutoff)


def capture_public_urw_sources(request, *, output=None, reference_only=False):
    """Unsigned URW research bytes through the environment's normal HTTPS proxy.

    This does not replace Production fetch_source or its DNS/SSRF guard. Only
    generated NAR URW card/odds URLs are accepted, redirects are refused, TLS
    verification remains enabled, and no Runtime request/signature is made.
    Existing snapshot extraction and evidence merge preserve the actual bytes
    and completion time. A structurally complete artifact is still unsigned.
    """
    from runtime.local_physical.nar_source_manifest import _race_card_source,_odds_source
    from runtime.local_physical.source_acquisition import _merge_evidence,sha_obj,SOURCE_SCHEMA,SOURCE_PROFILE
    from datetime import timedelta
    from runtime.local_race_key_intake import JST
    import re
    day=request.get('race_date');number=request.get('race_no')
    cutoff=None if reference_only else datetime.fromisoformat(request['prediction_cutoff'])
    now=datetime.now(timezone.utc)
    today=now.astimezone(JST).date().isoformat()
    if (request.get('venue_id')!='URW' or not isinstance(day,str)
            or (day<today if reference_only else day!=today)
            or type(number) is not int or not 1<=number<=12
            or (cutoff is not None and (cutoff.tzinfo is None or now>=cutoff
                or now.astimezone(JST).date().isoformat()!=day))):
        raise ValueError('PUBLIC_URW_CAPTURE_SCOPE_OR_DEADLINE')
    specs=[_race_card_source('URW','18',day.replace('-','/'),number),
           _odds_source('URW','18',day.replace('-','/'),number,required=not reference_only)]
    if output is not None:output.mkdir(parents=True,exist_ok=False)
    snapshots=[];errors=[];optional_errors=[]
    for spec in specs:
        if cutoff is not None and datetime.now(timezone.utc)>=cutoff:raise ValueError('PUBLIC_URW_CAPTURE_CUTOFF')
        try:
            snapshot,serr=fetch_public_urw_reference(spec,request.get('prediction_cutoff','') if cutoff else '')
        except (OSError,ValueError) as exc:
            if spec['required']:raise
            optional_errors.append({'source_id':spec['source_id'],'error':str(exc)});continue
        completed=datetime.fromisoformat(snapshot['fetched_at'])
        if reference_only and cutoff is None:
            from runtime.local_physical.source_acquisition import _html_text
            from runtime.local_race_day_dispatcher import raw_html
            heading=re.sub(r'\s+','',_html_text(raw_html(snapshot))).split('競走馬')[0]
            y,m,d=map(int,day.split('-'))
            match=re.search(rf'{y}年{m}月{d}日.*?浦和第{number}競走(\d{{1,2}}:\d{{2}})発走',heading)
            if not match:raise ValueError('REFERENCE_OFFICIAL_IDENTITY_OR_POST_REQUIRED')
            post=datetime.fromisoformat(day+'T'+match[1]+':00+09:00')
            cutoff=post-timedelta(seconds=120)
            request={**request,'scheduled_post_at':post.isoformat(),'prediction_cutoff':cutoff.isoformat()}
        if completed>=cutoff:raise ValueError('PUBLIC_URW_CAPTURE_COMPLETED_AFTER_CUTOFF')
        snapshot['cutoff_relation']='PRE_CUTOFF'
        snapshot['snapshot_sha256']=sha_obj({k:v for k,v in snapshot.items() if k!='snapshot_sha256'})
        snapshots.append(snapshot)
        if spec['required']:
            errors.extend(serr)
        elif serr:
            optional_errors.append({'source_id':spec['source_id'],'errors':serr})
        if output is not None:dump(output/(spec['source_id']+'.json'),snapshot)
    normalized,conflicts,merge_errors=_merge_evidence(snapshots);errors.extend(merge_errors)
    manifest=[{k:s[k] for k in ('source_id','url','source_class','authority','priority','official','required','extract')} for s in specs]
    raw_bundle=[{k:s[k] for k in ('source_id','raw_sha256','snapshot_sha256','fetched_at','final_url')} for s in snapshots]
    artifact={'schema':SOURCE_SCHEMA,'profile':SOURCE_PROFILE,'race_id':request['race_id'],
        'prediction_cutoff':request['prediction_cutoff'],'source_freeze_at':datetime.now(timezone.utc).isoformat(),
        'source_fetch_execution':{'mode':'ENVIRONMENT_DEFAULT_HTTPS_PROXY_URW_PUBLIC_RESEARCH',
            'source_count':len(snapshots),'prediction_authority':False,'production_transport_changed':False,
            'redirects_allowed':False,'local_dns_proof':'UNAVAILABLE_NOT_ASSERTED','tls_verification':True},
        'required_source_manifest':manifest,'required_source_manifest_sha256':sha_obj(manifest),
        'sources':snapshots,'raw_source_bundle_sha256':sha_obj(raw_bundle),
        'normalized_evidence':normalized,'normalized_evidence_sha256':sha_obj(normalized),'conflicts':conflicts,
        'missing_required_sources':[],'stale_sources':[],'post_cutoff_sources':[],
        'formal_ready':not errors,'errors':list(dict.fromkeys(errors)),
        'research_only':True,'signed_source_claim':False,'production_authority':False}
    if reference_only:
        artifact.update(source_race_context={k:request[k] for k in ('venue_id','race_date','race_no')},
            scheduled_post_at=request['scheduled_post_at'],optional_source_errors=optional_errors)
    artifact['source_snapshot_sha256']=sha_obj(artifact)
    return artifact,artifact['errors']


def public_source_shadow(output, models_path=None, *, race_no=1, plan_path=None,
                         environment_public_capture=False, quiet=False):
    """Public official GET only; never Runtime POST, receipt mint or LIVE.

    Date/venue scope is this user's Oct19 URW research preparation. It cannot
    silently roll to another date or obtain an OOS/Production signature. The
    ordinary full SOURCE acquisition/evidence/materializer code is reused.
    """
    sys.path.insert(0,str(ROOT/'runtime/local_physical'))
    from runtime.local_physical.nar_source_manifest import build_local_nar_manifest
    from runtime.local_physical.source_acquisition import acquire_sources,sha_obj,verify_source_artifact
    from runtime.local_physical.nar_runner_universe import enrich_source_artifact
    from runtime.local_physical.nar_auxiliary_evidence import enrich_with_auxiliary_evidence
    from runtime.local_physical.local_population_ledger import enrich_with_population_seed
    from runtime.local_race_key_shadow_owner import compile_public_venue_candidate,owner_feature_pack,predict_conditioned_owner
    from runtime.local_race_key_intake import JST
    output.mkdir(parents=True,exist_ok=False)
    req={'family_id':'LOCAL','venue_id':'URW','race_date':'2026-10-19','race_no':race_no,
        'race_id':f'KM-LOCAL-URW-20261019-R{race_no:02d}-PUBLIC-SHADOW','execution_id':f'KM-LOCAL-URW-20261019-R{race_no:02d}-PUBLIC-SHADOW',
        'scheduled_post_at':'2026-10-19T12:20:00+09:00','prediction_cutoff':'2026-10-19T12:18:00+09:00',
        'require_active_runner_universe':True,'include_odds':True}
    report={'classification':'PUBLIC_OFFICIAL_RESEARCH_NOT_FORMAL_NOT_SIGNED_SOURCE',
        'race_id':req['race_id'],'started_at':datetime.now(timezone.utc).isoformat(),
        'runtime_post_count':0,'signed_source_count':0,'signed_final_count':0,'formal_registration':False,
        'delivery_verified':False,'forward_oos_credit':0,'production_changes':False,'new_paid_api_requests':0}
    try:
        stage='FROZEN_RESEARCH_MODEL_BINDING'
        frozen=None
        if models_path is not None:
            packed=models_path.read_bytes()
            expected=json.loads((models_path.parent/'ranker_report.json').read_text())['forecast_artifact_sha256']
            if hashlib.sha256(packed).hexdigest()!=expected:
                raise ValueError('PUBLIC_FROZEN_MODEL_ARTIFACT_MISMATCH')
            frozen=json.loads(gzip.decompress(packed))
            report['frozen_model_artifact_sha256']=expected
        stage='DATED_OFFICIAL_PLAN_BINDING'
        if type(race_no) is not int or not 1<=race_no<=12:
            raise ValueError('PUBLIC_URW_RACE_NUMBER_INVALID')
        if plan_path is None and race_no!=1:
            raise ValueError('PUBLIC_URW_DATED_OFFICIAL_PLAN_REQUIRED')
        plan_race=None
        if plan_path is not None:
            plan=json.loads(plan_path.read_text())
            if (plan.get('family_id')!='LOCAL'
                    or plan.get('plan_sha256')!=_sha({k:v for k,v in plan.items() if k!='plan_sha256'})
                    or plan.get('venue_id')!='URW' or plan.get('race_date')!='2026-10-19'):
                raise ValueError('PUBLIC_URW_OFFICIAL_PLAN_HASH_OR_SCOPE')
            selected=[r for r in plan['races'] if r['fields']['race_no']==race_no]
            if len(selected)!=1:
                raise ValueError('PUBLIC_URW_PLAN_RACE_IDENTITY')
            plan_race=selected[0];fields=plan_race['fields']
            if (fields.get('venue_id')!='URW' or fields.get('race_date')!='2026-10-19'
                    or fields.get('race_no')!=race_no):
                raise ValueError('PUBLIC_URW_PLAN_RACE_IDENTITY')
            from datetime import timedelta
            post=datetime.fromisoformat(fields['scheduled_post_at'])
            cutoff=datetime.fromisoformat(fields['prediction_cutoff'])
            if (post.tzinfo is None or cutoff.tzinfo is None
                    or post.astimezone(JST).date().isoformat()!='2026-10-19'
                    or post-cutoff!=timedelta(seconds=120)):
                raise ValueError('PUBLIC_URW_PLAN_CLOCK_INVALID')
            req.update(scheduled_post_at=post.isoformat(),prediction_cutoff=cutoff.isoformat())
            report['plan_sha256']=plan['plan_sha256']
        report['plan_binding_is_activation_authority']=False
        report['request_fields']={k:req[k] for k in ('venue_id','race_date','race_no','scheduled_post_at','prediction_cutoff')}
        stage='DATED_PUBLIC_SHADOW_WINDOW'
        now=datetime.now(JST)
        if now.date().isoformat()!=req['race_date'] or now>=datetime.fromisoformat(req['prediction_cutoff']):
            raise ValueError('DATED_PUBLIC_SHADOW_WINDOW_CLOSED')
        manifest=build_local_nar_manifest(req)
        stage='OFFICIAL_SOURCE_GET'
        artifact,errors=(capture_public_urw_sources(req,output=output/'public_capture')
                         if environment_public_capture else acquire_sources(manifest))
        report['environment_public_capture']=environment_public_capture
        dump(output/'public_source_attempt.json',artifact)
        if errors:
            report['source_errors']=errors
            report['first_failed_stage']='OFFICIAL_SOURCE_GET'
            raise ValueError('PUBLIC_REQUIRED_SOURCE_HOLD:'+','.join(errors))
        artifact['source_manifest_profile']=manifest['manifest_profile']
        artifact['source_race_context']={k:req[k] for k in ('venue_id','race_date','race_no')}
        artifact=enrich_source_artifact(artifact)
        # Preserve the original observed statuses even on HOLD. Never upgrade
        # ACTIVE_DECLARED or replace these bytes with a research assumption.
        artifact['source_snapshot_sha256']=sha_obj({k:v for k,v in artifact.items() if k!='source_snapshot_sha256'})
        dump(output/'public_source_universe_observation.json',artifact)
        report.update(source_snapshot_sha256=artifact['source_snapshot_sha256'],
            source_freeze_at=artifact['source_freeze_at'],
            declared=len((artifact.get('declared_runner_universe') or {}).get('runners') or []),
            runner_status_registry=artifact.get('runner_status_registry') or [],
            observed_evidence_saved=True, prediction_frozen=False)
        stage='FRESH_OFFICIAL_RACE_RECHECK'
        start=(artifact.get('normalized_evidence') or {}).get('start_time') or {}
        if (start.get('authority')!='NAR_OFFICIAL'
                or start.get('value')!=datetime.fromisoformat(req['scheduled_post_at']).astimezone(JST).strftime('%H:%M')):
            raise ValueError('PUBLIC_URW_FRESH_OFFICIAL_POST_CHANGED_REPLAN_REQUIRED')
        if plan_race is not None:
            def identity(rows):
                return sorted((str(r['runner_id']),r['name']) for r in rows)
            if identity(artifact['declared_runner_universe']['runners'])!=identity(plan_race['declared_runner_universe']['runners']):
                raise ValueError('PUBLIC_URW_DECLARED_UNIVERSE_CHANGED_REPLAN_REQUIRED')
        stage='ACTIVE_RUNNER_UNIVERSE'
        if errors or artifact.get('formal_ready') is not True:
            raise ValueError('PUBLIC_REQUIRED_SOURCE_HOLD:'+','.join(errors))
        if not (artifact.get('active_runner_universe') or {}).get('runners'):
            raise ValueError('PUBLIC_FRESH_ACTIVE_RUNNER_UNIVERSE_UNPROVEN')
        if any(r.get('status')=='ACTIVE_DECLARED' for r in artifact.get('runner_status_registry') or []):
            report['first_failed_stage']='ACTIVE_RUNNER_UNIVERSE'
            raise ValueError('PUBLIC_ACTIVE_DECLARED_IS_NOT_VERIFIED_ACTIVE')
        stage='AUXILIARY_SOURCE_GET'
        artifact,aux_errors=enrich_with_auxiliary_evidence(artifact,req['prediction_cutoff'],require_profiles=False)
        if aux_errors:raise ValueError('PUBLIC_AUXILIARY_SOURCE_HOLD:'+','.join(aux_errors))
        artifact=enrich_with_population_seed(artifact)
        artifact['source_snapshot_sha256']=sha_obj({k:v for k,v in artifact.items() if k!='source_snapshot_sha256'})
        valid,errors=verify_source_artifact(artifact)
        if not valid:raise ValueError('PUBLIC_SOURCE_REVERIFY_HOLD:'+','.join(errors))
        stage='FULL29_MATERIALIZATION'
        n=materialize_production(artifact,{**req,'runners':artifact['official_runner_universe']['runners']},assess()['required_indices'])
        stage='VENUE_CANDIDATE_STATIC'
        c=compile_public_venue_candidate(req,artifact,n)
        p=owner_feature_pack(c,n)
        dump(output/'public_source_artifact.json',artifact)
        dump(output/'public_full29.json',n);dump(output/'public_candidate.json',c);dump(output/'public_feature_pack.json',p)
        handoff=freeze_public_research_handoff(output,artifact,n,c)
        report.update(research_handoff_sha256=handoff['sha256'],
            candidate_krs_input_sha256=handoff['candidate_krs_input_sha256'],krs_engine_executed=False)
        if frozen is not None:
            stage='FROZEN_CONDITIONAL_RESEARCH_PREDICTION'
            for arm,model in frozen['models'].items():
                prediction=predict_conditioned_owner(model,p)
                prediction['source_signature_eligibility']='HOLD_UNSIGNED_PUBLIC_SOURCE; not formal Signed SOURCE OOS'
                prediction['sha256']=_sha({k:v for k,v in prediction.items() if k!='sha256'})
                dump(output/(arm+'.prestart_shadow.json'),prediction)
        report.update(status='PUBLIC_PRESTART_SHADOW_SAVED_NOT_FORMAL_NOT_SIGNED',
            source_snapshot_sha256=artifact['source_snapshot_sha256'],source_freeze_at=artifact['source_freeze_at'],
            declared=len(artifact['declared_runner_universe']['runners']),active=len(artifact['active_runner_universe']['runners']),
            numerical_cells=len(n['runners'])*29,candidate_sha256=c['sha256'],feature_sha256=p['sha256'],
            prediction_frozen=True, frozen_at=c['frozen_at'])
    except (ValueError,KeyError,TypeError,OSError) as exc:
        report.update(status='HOLD_PUBLIC_SHADOW',error=str(exc))
        report.setdefault('first_failed_stage',stage)
    report['completed_at']=datetime.now(timezone.utc).isoformat();report['sha256']=_sha(report)
    dump(output/'public_shadow_status.json',report)
    if not quiet:print(json.dumps(report))
    return report


def failure_audit(output):
    """Explain frozen failures and transport dependence; never refit or reselect.

    Outcome-aware attribution is retrospective diagnostic evidence only. Index
    interventions are unsigned synthetic CODE tests, never proposed forecasts.
    KRS output sensitivity is not inferred from an input-field dependency.
    """
    import math
    from runtime.local_krs_bridge_candidate import build_candidate_prediction_structure_derived, build_runner_bridge
    from runtime.local_race_key_shadow_owner import _choice_features
    audit_path=ROOT/'research/urw_owner/20261019_condition_consumption/evidence_audit.json.gz'
    model_path=ROOT/'research/urw_owner/20261019_conditional_model/forecasts_before_evaluation.json.gz'
    report_path=model_path.parent/'ranker_report.json'
    audit=json.loads(gzip.decompress(audit_path.read_bytes()))
    frozen=json.loads(gzip.decompress(model_path.read_bytes()))
    expected=json.loads(report_path.read_text())['forecast_artifact_sha256']
    if hashlib.sha256(model_path.read_bytes()).hexdigest()!=expected:
        raise ValueError('FROZEN_DIAGNOSTIC_MODEL_HASH')
    before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (audit_path,model_path,report_path)}
    packs={p['race_id']:p for p in frozen_feature_packs(audit_path)}
    indices=next(iter(audit['forecasts'].values()))['candidate']['required_indices']
    dependence={name:{'index':name,'cells':0,'calculated':0,'ruled_neutral':0,'provenance_complete':0,
        'static_score_changes':0,'ranking_changes':0,'role_changes':0,'pair_changes':0,'third_changes':0} for name in indices}
    def sets(pred):
        pairs={(h,s) for h in pred['W'] for s in pred['P2'] if h!=s}
        triples={(h,s,t) for h,s in pairs for t in pred['P3'] if t not in (h,s)}
        return pairs,triples
    validation=[]
    for rid,f in audit['forecasts'].items():
        c,a=f['candidate'],f['index_consumption_audit']
        for v in (c,a):
            if v['sha256']!=_sha({k:z for k,z in v.items() if k!='sha256'}):raise ValueError('DIAGNOSTIC_INPUT_HASH')
        if _sha(f['paper']['candidate_krs_input'])!=f['paper']['candidate_krs_input_sha256']:
            raise ValueError('DIAGNOSTIC_KRS_INPUT_BINDING')
        rows={r:{'runner_id':r,'canonical_components':{}} for r in c['ranking']}
        for item in a['indices']:
            for cell in item['cells']:
                rows[cell['runner_id']]['canonical_components'][item['index']]={k:cell[k] for k in ('value','terminal_status','rule_id','mapping_version','evidence_refs','source_fact')}
        rows=list(rows.values())
        predict=lambda rr:build_candidate_prediction_structure_derived({'runners':rr})['candidate_static_prediction']
        base=predict(copy.deepcopy(rows));pairs,thirds=sets(base)
        assert base['ranking']==c['ranking'] and base['roles']==c['role_columns']
        assert pairs=={(p['head'],p['second']) for p in c['head_local_pairs']}
        assert thirds=={(p['head'],p['second'],p['third']) for p in c['pair_conditioned_thirds']}
        scores={r['runner_id']:r for r in base['runner_scores']}
        for pos,row in enumerate(rows):
            for name,cell in row['canonical_components'].items():
                d=dependence[name];d['cells']+=1;d['calculated']+=cell['terminal_status']=='CALCULATED'
                d['ruled_neutral']+=cell['terminal_status']=='RULED-NEUTRAL'
                d['provenance_complete']+=all(cell.get(k) for k in ('rule_id','mapping_version','evidence_refs','source_fact'))
                for value in (0.,100.):
                    changed=copy.deepcopy(rows);changed[pos]['canonical_components'][name]['value']=value
                    p=predict(changed);ps,ts=sets(p);s=next(r for r in p['runner_scores'] if r['runner_id']==row['runner_id'])
                    d['static_score_changes']+=any(s[k]!=scores[row['runner_id']][k] for k in ('w_score','p2_score','p3_score'))
                    d['ranking_changes']+=p['ranking']!=base['ranking'];d['role_changes']+=p['roles']!=base['roles']
                    d['pair_changes']+=ps!=pairs;d['third_changes']+=ts!=thirds
        if c['race_date']<'2026-09-24':continue
        # Labels enter only AFTER result-blind code interventions. They never
        # modify a model, numeric cell, Role, ticket or archived ledger.
        record=sorted((ROOT/'runtime/family_result_requests').glob(rid.replace('-FORMAL-R1','')+'-RESULT-R*.json'))[-1]
        actual=list(map(str,json.loads(record.read_text())['finish_order'][:3]));winner=actual[0]
        pack=packs[rid];model_details={}
        for arm,model in frozen['models'].items():
            pred=frozen['forecasts'][arm][rid];top=pred['ranking'][0];fit=model['fits'][0]
            def contributions(h):
                row=_choice_features(pack,h,[],stage_evidence=model['stage_evidence'],interactions=model['interactions'])
                return {k:w*(row[k]-m)/s if row.get(k) is not None and s else 0.
                    for k,m,s,w in zip(fit['feature_names'],fit['training_means'],fit['training_scales'],fit['coefficients'])}
            wc,tc=contributions(winner),contributions(top)
            gap={k:wc[k]-tc[k] for k in wc}
            observed=math.log(pred['winner_model_mass'][winner]/pred['winner_model_mass'][top])
            assert abs(sum(gap.values())-observed)<1e-8
            model_details[arm]={'winner_rank':pred['ranking'].index(winner)+1,'top1':top,
                'winner_model_mass':pred['winner_model_mass'][winner],'uniform_winner_mass':1/len(rows),
                'winner_vs_top_logit_gap':observed,'feature_gap':gap,
                'missing_features_of_winner':pred['missingness'][winner],
                'unknown_contribution_verified_zero':all(wc.get(k,0.)==0. for k in pred['missingness'][winner]),
                'ridge_penalty':fit['ridge_penalty'],'trained_races':len(model['training_races'])}
        validation.append({'race_id':rid,'actual_top3':actual,'baseline_winner_rank':base['ranking'].index(winner)+1,
            'baseline_W':base['W'],'winner_role_scores':scores[winner],
            'winner_cells':{name:next(z for z in item['cells'] if z['runner_id']==winner) for name,item in ((i['index'],i) for i in a['indices'])},
            'winner_prestart_history':c['urw_evidence'][winner],
            'models':model_details,'input_sha256':f['paper']['candidate_krs_input_sha256'],
            'label_provenance':str(record.relative_to(ROOT))})
    # An explicit synthetic fixture traces the existing bridge implementation.
    # No observed SOURCE values or Engine outputs are invented for this test.
    probe={'runner_id':'1','canonical_components':{n:{'value':52.,'evidence_refs':['SYNTHETIC_CODE_TEST']} for n in indices},
        'evidence_features':{n:{'score':52.,'evidence_refs':['SYNTHETIC_CODE_TEST']} for n in ('position_acquisition','leadership_stalk_acceptance','draw_style_fit','third_corner_progression','position_maintenance','kickback_traffic_tolerance')}}
    bridge=build_runner_bridge(probe)
    for name in indices:
        paths=set()
        for value in (0.,100.):
            q=copy.deepcopy(probe);q['canonical_components'][name]['value']=value;b=build_runner_bridge(q)
            paths|={group+'.'+k for group in ('hsv','static') for k in bridge[group] if bridge[group][k]!=b[group][k]}
            if b['uncertainty_scale']!=bridge['uncertainty_scale']:paths.add('uncertainty_scale')
        dependence[name]['candidate_krs_input_changed_fields']=sorted(paths)
        dependence[name]['krs_output_or_predictive_increment']='NOT_TESTED_NOT_INFERRED_FROM_TRANSPORT'
    assert before=={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (audit_path,model_path,report_path)}
    out={'classification':'RETROSPECTIVE_FAILURE_ATTRIBUTION_AND_SYNTHETIC_CODE_SENSITIVITY_NOT_MODEL_RESEARCH_RESTART',
        'frozen_input_hashes':before,'validation':validation,'indices':list(dependence.values()),
        'fitted_or_selected_models':0,'new_tickets':0,'production_changes':False,'runtime_post_count':0,'forward_oos_credit':0,
        'interpretation':'Score gaps localize frozen failures; they do not prove causal importance or authorize a new coefficient. No improvement or expected return estimate is claimed.'}
    out['sha256']=_sha(out);output.mkdir(parents=True,exist_ok=False);dump(output/'failure_and_transport_audit.json',out)
    print(json.dumps({'validation_races':len(validation),'indices':len(dependence),'refits':0,'model_adoption':'REJECTED_UNCHANGED'}))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--archives', type=Path)
    ap.add_argument('--ranker-audit', action='store_true')
    ap.add_argument('--urw-transfer-audit', action='store_true')
    ap.add_argument('--public-shadow', action='store_true')
    ap.add_argument('--environment-public-capture', action='store_true',
        help='Unsigned URW card/odds GET through the existing environment HTTPS proxy; no Production transport change')
    ap.add_argument('--declared-snapshot', type=Path)
    ap.add_argument('--race-no', type=int, default=1, choices=range(1,13))
    ap.add_argument('--dated-plan', type=Path)
    ap.add_argument('--official-label-refetch', action='store_true')
    ap.add_argument('--failure-audit', action='store_true')
    ap.add_argument('--frozen-models', type=Path)
    ap.add_argument('--engine', type=Path)
    ap.add_argument('--baseline-outputs', type=Path)
    ap.add_argument('--evidence-audit-only', action='store_true')
    ap.add_argument('--prior-predictions', type=Path)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    if args.declared_snapshot is not None:
        if args.dated_plan is None:ap.error('--dated-plan required for declared snapshot diagnostics')
        declared_snapshot_shadow(args.output,args.declared_snapshot,args.dated_plan,race_no=args.race_no)
        return
    if args.official_label_refetch:
        refetch_historical_labels(args.output)
        return
    if args.failure_audit:
        failure_audit(args.output)
        return
    if args.public_shadow:
        public_source_shadow(args.output,args.frozen_models,race_no=args.race_no,plan_path=args.dated_plan,
            environment_public_capture=args.environment_public_capture)
        return
    if args.ranker_audit or args.urw_transfer_audit:
        ranker_audit(args.output,urw_transfer=args.urw_transfer_audit)
        return
    if args.archives is None:ap.error('--archives required for archive replay')
    params = ROOT / 'runtime/local_physical/parameter_map_v0.1-provisional.json'
    if not args.evidence_audit_only:
        if args.engine is None or args.baseline_outputs is None:
            ap.error('--engine and --baseline-outputs required for Engine replay')
        assert hashlib.sha256(args.engine.read_bytes()).hexdigest() == ENGINE
    assert hashlib.sha256(params.read_bytes()).hexdigest() == PARAMETERS
    args.output.mkdir(parents=True, exist_ok=False)
    key = Ed25519PublicKey.from_public_bytes(base64.b64decode(KEY))
    rows, forecasts = [], {}
    started = datetime.now(timezone.utc).isoformat()
    for run, digest in ARCHIVES.items():
        archive = args.archives / f'urw-history-{run}.zip'
        assert hashlib.sha256(archive.read_bytes()).hexdigest() == digest
        with ZipFile(archive) as z:
            source = json.loads(z.read('source_receipt_envelope.json'))
        assert source['signer_key_id'] == 'KM-LOCAL-RUNTIME-ED25519-20260922'
        assert source['receipt_sha256'] == _sha(source['receipt'])
        assert source['receipt']['artifact_sha256'] == _sha(source['artifact'])
        key.verify(base64.b64decode(source['signature']), json.dumps(
            source['receipt'], ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())
        rid = source['receipt']['race_id']
        stored = json.loads((ROOT / 'runtime/family_requests' / f'{rid}.json').read_text())
        request = {k: stored[k] for k in ('race_id', 'race_date', 'race_no', 'venue_id',
                                        'scheduled_post_at', 'prediction_cutoff')}
        request.update(family_id='LOCAL', execution_id=rid)
        row = {'race_id': rid, 'archive_run_id': run, 'archive_sha256': digest,
               'source_receipt_sha256': source['receipt_sha256']}
        rows.append(row)
        try:
            numerical = materialize_production(source['artifact'], {
                **request, 'runners': source['artifact']['official_runner_universe']['runners']},
                assess()['required_indices'])
            row['numerical_cells'] = 29 * len(numerical['runners'])
            candidate = compile_urw_candidate(request, source, numerical, historical_replay=True)
            paper = audit_urw_candidate_paper_pipeline(candidate, numerical)
            forecasts[rid] = {'candidate': candidate, 'paper': paper}
            if args.evidence_audit_only:
                forecasts[rid]['index_consumption_audit']=audit_index_consumption(numerical)
            row.update(status='CANDIDATE_REPLAY', candidate_sha256=candidate['sha256'],
                       candidate_krs_input_sha256=paper['candidate_krs_input_sha256'])
            dump(args.output / f'{rid}.input.json', paper['candidate_krs_input'])
        except ValueError as exc:
            row.update(status='HOLD', first_failed_stage='URW_STATIC_CANDIDATE', error=str(exc))

    if args.evidence_audit_only:
        prior=json.loads(gzip.decompress(args.prior_predictions.read_bytes()))['forecasts'] if args.prior_predictions else {}
        for row in rows:
            rid=row['race_id']
            if rid not in forecasts:
                continue
            f=forecasts[rid];candidate=f['candidate'];scenario=candidate['urw_scenario_prediction']
            if prior:
                old=prior[rid]
                row['same_ranking_and_roles_as_prior_identity_replay']=(candidate['ranking']==old['candidate']['ranking'] and candidate['role_columns']==old['candidate']['role_columns'])
                row['same_engine_input_as_prior_identity_replay']=f['paper']['candidate_krs_input_sha256']==old['paper']['candidate_krs_input_sha256']
                assert row['same_ranking_and_roles_as_prior_identity_replay'] and row['same_engine_input_as_prior_identity_replay']
            row.update(score_consumed_indices=f['index_consumption_audit']['score_consumed_indices'],
                strict_p2_order_edges=sum(len(x['partial_order_edges']) for x in scenario['head_local_p2'].values()),
                strict_p3_order_edges=sum(len(x['partial_order_edges']) for x in scenario['pair_conditioned_p3'].values()),
                material_exact_count=sum(e['material_exact_evidence'] for x in scenario['pair_conditioned_p3'].values() for e in x['evaluations'].values()),
                source_bound_condition_translations=len(candidate['urw_evidence']))
        artifact={'classification':'HISTORICAL_EVIDENCE_AND_UNSIGNED_CODE_SENSITIVITY_NOT_FORWARD',
                  'forecasts':forecasts,'created_at':datetime.now(timezone.utc).isoformat()}
        packed=gzip.compress(json.dumps(artifact,ensure_ascii=False,sort_keys=True).encode(),mtime=0)
        (args.output/'evidence_audit.json.gz').write_bytes(packed)
        report={'classification':artifact['classification'],'selected_denominator':len(rows),
            'candidate_completed':len(forecasts),'held':len(rows)-len(forecasts),
            'races':rows,'artifact_sha256':hashlib.sha256(packed).hexdigest(),
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'genuine_forward_oos':0,'new_engine_runs':0,'runtime_post_count':0,
            'prediction_quality_improvement':'NOT_PROVEN','production_changes':False,
            'limits':'0/100 unsigned interventions measure Candidate code dependence only, not feature plausibility or incremental prediction value. Neutral states preserved. Existing six-race Engine evidence reusable only where exact Engine input SHA and roles match; no new quality claim.'}
        report['sha256']=_sha(report)
        dump(args.output/'report.json',report)
        print(json.dumps({k:v for k,v in report.items() if k!='races'}))
        return

    def simulate(rid):
        wall = time.perf_counter()
        with (args.output / f'{rid}.log').open('w') as log:
            subprocess.run([sys.executable, str(args.engine.resolve()),
                str(args.output / f'{rid}.input.json'), '--output', str(args.output / f'{rid}.output.json'),
                '--csv', str(args.output / f'{rid}.csv'), '--params', str(params),
                '--runs', '5000', '--seed', '1', '--short'], stdout=log, stderr=subprocess.STDOUT,
                timeout=180, check=True)
        raw = json.loads((args.output / f'{rid}.output.json').read_text())
        snap = raw['snapshot']
        assert snap['prediction_id'] == rid and snap['racecourse'] == '浦和'
        assert snap['date'] == forecasts[rid]['candidate']['race_date']
        assert snap['race_no'] == forecasts[rid]['candidate']['race_no']
        assert snap['run_count'] == 5000
        return rid, raw, time.perf_counter() - wall

    with ThreadPoolExecutor(max_workers=3) as pool:
        for rid, raw, seconds in pool.map(simulate, forecasts):
            forecasts[rid]['engine_output'] = raw
            forecasts[rid]['utility'] = build_krs_prediction_utility(
                forecasts[rid]['paper']['semantic_request'], {'status': 'EXECUTED', 'output': raw})
            forecasts[rid]['offline_wall_seconds'] = seconds
    snapshots = [x['engine_output']['snapshot']['simulation_snapshot_id'] for x in forecasts.values()]
    assert len(snapshots) == len(set(snapshots))
    before_labels = {'classification': 'RETROSPECTIVE_CANDIDATE_NOT_FORWARD_OOS',
                     'completed_at': datetime.now(timezone.utc).isoformat(), 'forecasts': forecasts}
    frozen_bytes = json.dumps(before_labels, ensure_ascii=False, sort_keys=True).encode()
    (args.output / 'predictions_before_labels.json.gz').write_bytes(gzip.compress(frozen_bytes, mtime=0))

    # Labels cannot influence compilation, simulation, role proposals or tickets.
    for row in rows:
        rid = row['race_id']
        matches = sorted((ROOT / 'runtime/family_result_requests').glob(
            rid.replace('-FORMAL-R1', '') + '-RESULT-R*.json'))
        labels = json.loads(matches[-1].read_text())
        assert labels['race_id'] == rid
        row['label'] = {'path': str(matches[-1].relative_to(ROOT)),
            'file_sha256': hashlib.sha256(matches[-1].read_bytes()).hexdigest(),
            'official_result_verified_recorded': labels.get('official_result_verified') is True,
            'fresh_official_refetch_verified': False, 'top3': labels['finish_order'][:3]}
        if rid not in forecasts:
            row['recommended_pfs'] = 'N/A'
            continue
        f = forecasts[rid]
        actual = list(map(int, labels['finish_order'][:3]))
        row.update(snapshot=f['engine_output']['snapshot'], offline_wall_seconds=f['offline_wall_seconds'],
            evaluation=evaluate_against_result(f['utility'], actual, static_ranking=f['candidate']['ranking']),
            semantic_virtual_settlement=settle_ticket_list(f['paper']['mec_contract_result']['tickets'],
                {'official_result': {'top3': labels['finish_order'][:3], 'payouts': labels['payouts']}}))
        old = json.loads((args.baseline_outputs / f'{rid}.output.json').read_text())
        old_utility = build_krs_prediction_utility(f['paper']['semantic_request'], {'status': 'EXECUTED', 'output': old})
        row['anonymous_baseline_snapshot'] = old['snapshot']
        row['anonymous_baseline_evaluation'] = evaluate_against_result(
            old_utility, actual, static_ranking=f['candidate']['ranking'])
        row['nonveto_shadow_role_hits'] = {role: role in f['utility']['shadow_role_registry'][str(horse)]
                                         for role, horse in zip(('W', 'P2', 'P3'), actual)}
        row['false_shadow_additions'] = {k: row['evaluation'][k] for k in
            ('false_pair_addition_count', 'false_exact_addition_count', 'proposal_width')}
    completed = [r for r in rows if r['status'] != 'HOLD']
    report = {'classification': 'HISTORICAL_DIAGNOSTIC_NOT_PRODUCTION_NOT_OOS',
        'started_at': started, 'prediction_pass_completed_before_labels_at': before_labels['completed_at'],
        'prediction_pass_sha256': hashlib.sha256(frozen_bytes).hexdigest(),
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'engine_sha256': ENGINE, 'parameter_map_sha256': PARAMETERS,
        'selected_denominator': len(rows), 'candidate_completed': len(completed), 'held': len(rows)-len(completed),
        'requested_runs_per_completed_race': 5000, 'master_seed': 1,
        'unique_race_bound_snapshot_count': len(set(snapshots)),
        'anonymous_baseline_snapshot_count': len({r['anonymous_baseline_snapshot']['simulation_snapshot_id'] for r in completed}),
        'static_role_hits': {role: sum(next(x for x in r['evaluation']['rank_comparison'] if x['role']==role)['static_role_hit'] for r in completed) for role in ('W','P2','P3')},
        'nonveto_shadow_role_hits': {role: sum(r['nonveto_shadow_role_hits'][role] for r in completed) for role in ('W','P2','P3')},
        'quality_disposition': 'HOLD_UNCALIBRATED_ROLE_EXPANSION_NOT_PURCHASE_AUTHORITY',
        'races': rows, 'genuine_forward_oos': 0, 'runtime_post_count': 0,
        'new_paid_api_requests': 0, 'signed_final_count': 0, 'actual_purchase_pfs': 'UNKNOWN',
        'production_changes': False, 'physics_or_parameters_changed': False,
        'limits': 'Seven retrievable historical archives, one retained HOLD; mixed stored-label provenance, no fresh official refetch. Seed namespace repair changes simulation draws. Role unions widen coverage and do not establish discrimination, calibration, incremental PFS or material Exact. No ticket additions or numeric effects are fitted from results.'}
    report['sha256'] = _sha(report)
    dump(args.output / 'report.json', report)
    print(json.dumps({k:v for k,v in report.items() if k!='races'}, ensure_ascii=False))


if __name__ == '__main__':
    main()

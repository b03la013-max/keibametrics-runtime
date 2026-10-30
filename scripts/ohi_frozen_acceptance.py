"""Read-only OHI acceptance from existing canonical checkpoints.

No SOURCE acquisition, Runtime POST, signature, ledger update or policy choice.
Reuses LOCAL accounting, full29, frozen R4/R5 arms and the existing venue-local
conditional owner. New computations are explicitly retrospective research.
"""
from __future__ import annotations
import argparse
import base64
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'runtime')]
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature
from runtime.execution_store import resolve_phase
from runtime.execution_gateway import load_gateway, family_config, request_json, assess_runtime_health
from runtime.local_result_settlement import settle_frozen_tickets
from runtime.local_fullnumerical_production import materialize_production
from runtime.local_race_key_shadow_owner import (
    compile_public_venue_candidate, owner_feature_pack,
    fit_conditioned_owner, predict_conditioned_owner,
)
from runtime.mec_r4_shadow import settle_ticket_list
from runtime.local_mec_r4_bridge import verify_signed_final_binding as verify_r4
from runtime.local_mec_r5_shadow import verify_signed_final_binding as verify_r5


def sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)+'\n',encoding='utf-8')


def verify(path, eid, phase, key):
    raw = path.read_bytes(); env = json.loads(raw); r = env['receipt']
    if (r.get('family')!='LOCAL' or r.get('phase')!=phase or r.get('race_id')!=eid
            or env.get('signature_alg')!='Ed25519'
            or env.get('signer_key_id')!='KM-LOCAL-RUNTIME-ED25519-20260922'
            or r.get('schema')!='KM-LOCAL-SIGNED-RECEIPT-v1'
            or r.get('status') != {'SOURCE':'SOURCE_FROZEN','KRS_RUN':'EXECUTED'}.get(phase,'PASS')
            or r.get('errors') or sha(r)!=env['receipt_sha256']
            or sha(env['artifact'])!=r['artifact_sha256']):
        raise ValueError('HISTORICAL_RECEIPT_BINDING:'+str(path))
    key.verify(base64.b64decode(env['signature'], validate=True),
               json.dumps(r,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
    return env, {'path':str(path.relative_to(ROOT)), 'sha256':hashlib.sha256(raw).hexdigest(),
                 'receipt_sha256':env['receipt_sha256'], 'crypto_verified':True}


def aggregate(rows):
    """No missing payout becomes zero; keep chronological drawdown and cash."""
    complete=[r for r in rows if r.get('return') is not None]
    missing=len(rows)-len(complete)
    unknown_investment=sum(r.get('investment') is None for r in rows)
    known_inv=sum(r['investment'] for r in rows if r.get('investment') is not None)
    inv=None if unknown_investment else known_inv
    settled_inv=sum(r['investment'] for r in complete if r.get('investment') is not None)
    ret=sum(r['return'] for r in complete)
    eq=peak=dd=0
    for r in complete:
        if r.get('investment') is None: continue
        eq+=r['return']-r['investment']; peak=max(peak,eq); dd=max(dd,peak-eq)
    largest=max((r['return'] for r in complete),default=0)
    largest_ticket=max((r.get('maximum_ticket_return',0) for r in complete),default=0)
    return {'fixed_denominator':len(rows),'settled':len(complete),'unsettled':missing,
        'investment':inv,'known_investment':known_inv,'unknown_investment_races':unknown_investment,
        'settled_investment':settled_inv,'return':ret if not missing else None,
        'pfs':100*ret/inv if inv and not missing else None,
        'profit_loss':ret-inv if not missing and inv is not None else None,
        'max_drawdown':dd if not missing and not unknown_investment else None,
        'observed_complete_subsequence_drawdown':dd,
        'drawdown_scope':'INCOMPLETE_FULL_COHORT_UNKNOWN' if missing or unknown_investment else 'COMPLETE_FIXED_COHORT',
        'maximum_race_return':largest,
        'maximum_ticket_return':largest_ticket,
        'pfs_excluding_maximum_ticket':100*(ret-largest_ticket)/inv if inv and not missing else None,
        'largest_race_share':largest/ret if ret else None,
        'pfs_excluding_maximum_return':100*(ret-largest)/inv if inv and not missing else None,
        'participating_races':sum((r.get('investment') or 0)>0 for r in rows),
        'hit_races':sum(r['return']>0 for r in complete),
        'hit_but_loss':sum(r.get('investment') is not None and 0<r['return']<r['investment'] for r in complete),
        'profitable_races':sum(r.get('investment') is not None and r['return']>r['investment'] for r in complete),
        'actual_purchase':False,'new_forward_oos_credit':0}


def ticket_difference(baseline, candidate, official):
    """Separate actual shared, extra and displaced stake; never C count-B count."""
    def index(rows):
        return {(t['bet_type'],tuple(sorted(t['selection'])) if t['bet_type']=='TRIO'
                 else tuple(t['selection'])):t['stake'] for t in rows}
    a,b=index(baseline),index(candidate)
    shared=[];added=[];removed=[]
    for (bt,sel) in sorted(set(a)|set(b)):
        old,new=a.get((bt,sel),0),b.get((bt,sel),0)
        for dest,stake in ((shared,min(old,new)),(added,max(0,new-old)),(removed,max(0,old-new))):
            if stake:dest.append({'bet_type':bt,'selection':list(sel),'stake':stake})
    def settled(rows):
        s=settle_frozen_tickets({'tickets':rows},official)
        return {'ticket_count':len(rows),'investment':s['investment'],'return':s['return'],
                'profit_loss':s['return']-s['investment'],'winning_tickets':s['winning_tickets']}
    return {'shared':settled(shared),'candidate_extra_stake':settled(added),
            'baseline_displaced_stake':settled(removed),
            'candidate_only_selection_count':len(set(b)-set(a)),
            'baseline_only_selection_count':len(set(a)-set(b))}


def audit(output, *, health, retrain=True):
    if assess_runtime_health(health,'LOCAL',load_gateway(),ROOT)['status']!='PASS':
        raise ValueError('CURRENT_GATEWAY_HEALTH_REQUIRED')
    key=Ed25519PublicKey.from_public_bytes(base64.b64decode(health['receipt_public_key_b64'],validate=True))
    expected={'20261007':[f'KM-LOCAL-OHI-20261007-R{i:02d}-LIVE-R1' for i in range(1,13)]}
    for day,manifest in (
        ('20261008','research/common/KM-FAMILY-OHI-20261008-DAY-REGRESSION-R1.json'),
        ('20261009','research/common/KM-FAMILY-OHI-20261009-DAY-R43-REGRESSION-R1.json')):
        expected[day]=[r['race_id'] for r in load(ROOT/manifest)['verified_result_records']]
    rows=[]; train=[]; labels={}; heldout=[]; failures=[]; files=[]
    for execution in sorted((ROOT/'runtime/executions').glob('KM-LOCAL-OHI-202610*-R*-LIVE-R*')):
        eid=execution.name; day=eid.split('-')[3]
        if day not in ('20261005','20261006','20261007','20261008','20261009'): continue
        if eid=='KM-LOCAL-OHI-20261008-R08-LIVE-R1': continue  # superseded declared revision; retain bytes
        try:
            formal=resolve_phase(eid,'FORMAL'); result=resolve_phase(eid,'RESULT')
            if not formal or not result: raise ValueError('CANONICAL_PHASE_INCOMPLETE')
            fd,rd=formal['run_dir'],result['run_dir']
            fin,fp=verify(fd/'final_receipt_envelope.json',eid,'FINAL',key)
            res,rp=verify(rd/'result_receipt_envelope.json',eid,'RESULT',key)
            src,sp=verify(fd/'source_receipt_envelope.json',eid,'SOURCE',key)
            krs,kp=verify(fd/'krs_receipt_envelope.json',eid,'KRS_RUN',key)
            if (fin['artifact'].get('source_receipt_sha256')!=src['receipt_sha256']
                or fin['artifact'].get('krs_receipt_sha256')!=krs['receipt_sha256']
                or (res['artifact'].get('frozen_refs') or {}).get('final_receipt_sha256')!=fin['receipt_sha256']):
                raise ValueError('HISTORICAL_SOURCE_FINAL_RESULT_LINEAGE')
            files.extend([fp,rp,sp,kp]); official=res['artifact']['official_result']
            settled=settle_frozen_tickets(fin['artifact']['final_ticket'],official)
            old=res['artifact']['settlement']
            if (settled['investment'],settled['return'])!=(old['investment'],old['return']):
                raise ValueError('HISTORICAL_FINANCE_MISMATCH')
            req=load(ROOT/'runtime/formal_intents'/f'{eid}.json')
            prediction=fin['artifact']['final_prediction_package']; ranking=list(map(int,prediction.get('ranking') or []))
            roles=prediction.get('roles') or {}; top3=official['finish_order'][:3]
            orig_tickets=fin['artifact']['final_ticket']['tickets']
            keys={(t['bet_type'],tuple(sorted(t['selection'])) if t['bet_type']=='TRIO' else tuple(t['selection'])) for t in orig_tickets}
            row={'race_id':eid,'day':day,'post':req['scheduled_post_at'],
                'classification':'REAL_HISTORICAL_SIGNED_ORIGINAL',
                'investment':settled['investment'],'return':settled['return'],'ticket_count':len(orig_tickets),
                'maximum_ticket_return':max((w['return'] for w in settled['winning_tickets']),default=0),
                'by_type':settled['by_type'],'top3':top3,'winner_rank':ranking.index(top3[0])+1 if top3[0] in ranking else None,
                'role_capture':{col:col in roles.get(str(h),[]) for col,h in zip(('W','P2','P3'),top3)},
                'ordered_pair_ticket':('EXACTA',tuple(top3[:2])) in keys,
                'trio_ticket':('TRIO',tuple(sorted(top3))) in keys,
                'trifecta_ticket':('TRIFECTA',tuple(top3)) in keys,
                'first_failure':((res['artifact'].get('automatic_post_result_review') or {})
                    .get('failure_localization') or {}).get('first_material_failure') or 'UNKNOWN',
                'original_numerical':prediction.get('actual_numerical_calculation'),
                'final_receipt_sha256':fin['receipt_sha256'],'result_receipt_sha256':res['receipt_sha256'],
                'source_receipt_sha256':src['receipt_sha256'],'final_git_revision':fin['receipt'].get('github_revision'),
                'original_krs':{k:krs['artifact'].get(k) for k in
                    ('actual_run_count','seed','input_sha256','output_sha256','engine_sha256','parameter_map_sha256','started_at','completed_at')},
                'shadows':{}, 'new_forward_oos_credit':0}
            for kind,name,checker in [('R4','mec_r4_shadow_pre_result.json',verify_r4),
                                       ('R5','local_mec_r5_shadow_pre_result.json',verify_r5)]:
                p=fd/name
                if not p.exists(): continue
                shadow=load(p); checker(fin,shadow)
                if shadow['sha256']!=sha({k:v for k,v in shadow.items() if k!='sha256'}):
                    raise ValueError('FROZEN_SHADOW_HASH_MISMATCH')
                for arm,spec in shadow['arms'].items():
                    outcome=settle_ticket_list(spec['tickets'],{'official_result':{**official,'top3':top3}})
                    checked=settle_frozen_tickets({'tickets':spec['tickets']},official)
                    if (outcome['investment'],outcome['return']) != (checked['investment'],checked['return']):
                        raise ValueError('FROZEN_SHADOW_FINANCE_MISMATCH')
                    row['shadows'][kind+':'+arm]={**outcome,'source_shadow_sha256':shadow['sha256'],
                        'maximum_ticket_return':max((w['return'] for w in checked['winning_tickets']),default=0),
                        'stake_set_difference':ticket_difference(orig_tickets,spec['tickets'],official),
                        'same_information':True,'realizable_frozen_tickets':True,
                        'same_budget_as_production':outcome['investment']==row['investment'],
                        'same_points_as_production':len(spec['tickets'])==len(orig_tickets)}
                if kind=='R4' and 'CORE_PROTECTION' in shadow['arms']:
                    for arm,spec in shadow['arms'].items():
                        if arm.startswith('CPSS_'):
                            row['shadows'][kind+':'+arm]['krs_vs_fixed_core_protection'] = ticket_difference(
                                shadow['arms']['CORE_PROTECTION']['tickets'],spec['tickets'],official)
            try:
                numerical=materialize_production(src['artifact'],req,req['required_indices'])
                row['diagnostic_full29']=numerical['numeric_coverage']
                write(output/'numerical'/f'{eid}.json',numerical)
                candidate=compile_public_venue_candidate(req,src['artifact'],numerical,historical_replay=True)
                pack=owner_feature_pack(candidate,numerical)
                write(output/'features'/f'{eid}.json',pack)
                if day<'20261007':train.append(pack);labels[eid]=list(map(str,top3))
                else:heldout.append((pack,list(map(str,top3))))
            except (ValueError,KeyError,TypeError) as exc:
                row['feature_replay_failure']=str(exc)
            rows.append(row)
        except (ValueError,KeyError,TypeError,OSError,AssertionError,InvalidSignature) as exc:
            failures.append({'race_id':eid,'first_failed_stage':type(exc).__name__+':'+str(exc),'new_forward_oos_credit':0})
    rows.sort(key=lambda r:r['post'])
    cohorts={}
    for day in ('20261007','20261008','20261009'):
        completed={r['race_id']:r for r in rows if r['day']==day}
        failed={r['race_id']:r['first_failed_stage'] for r in failures}
        selected=[completed.get(eid,{'race_id':eid,'day':day,'investment':None,'return':None,
            'shadows':{},'first_failure':failed.get(eid,'EXPECTED_ORIGINAL_NOT_FOUND'),
            'classification':'UNSETTLED_EXPECTED_ORIGINAL_FAILURE'}) for eid in expected[day]]
        arms=sorted({a for r in selected for a in r['shadows']})
        cohorts[day]={'production':aggregate(selected),'races':selected,
            'first_failures':dict(Counter(r.get('first_failure') or 'UNKNOWN' for r in selected)),
            'frozen_shadow_comparisons':{a:{**aggregate([{'investment':r['shadows'][a]['investment'],
                'return':r['shadows'][a]['return'],
                'maximum_ticket_return':r['shadows'][a]['maximum_ticket_return']} if a in r['shadows'] else
                {'investment':None,'return':None} for r in selected]),
                'missing_arm_races':len(selected)-sum(a in r['shadows'] for r in selected),
                'equal_budget_and_points_races':sum(r['shadows'].get(a,{}).get('same_budget_as_production') is True
                    and r['shadows'].get(a,{}).get('same_points_as_production') is True for r in selected),
                'normalization':'DIFFERENT_FROZEN_CAPITAL_NOT_A_MATCHED_BUDGET_PERFORMANCE_PROOF'} for a in arms}}
    training={'status':'NOT_EXECUTED','production_authority':False,'new_forward_oos_credit':0}
    if retrain and len(train)>=2:
        model=fit_conditioned_owner(train,labels)  # existing algorithm, train-only CV; no new model family
        write(output/'existing_conditioned_owner_retrained.json',model)
        predictions=[]
        for pack,label in heldout:
            pred=predict_conditioned_owner(model,pack,historical_replay=True)
            write(output/'conditioned_predictions'/f"{pack['race_id']}.json",pred)
            predictions.append({'race_id':pack['race_id'],'prediction_sha256':pred['sha256'],
                'winner_rank':pred['ranking'].index(label[0])+1,
                'role_capture':{c:c in pred['role_columns'].get(h,[]) for c,h in zip(('W','P2','P3'),label)}})
        training={'status':'EXISTING_ALGORITHM_RETRAINED_RETROSPECTIVE_ONLY','training_races':len(train),
            'training_max_post_at':model['training_max_post_at'],'model_sha256':model['sha256'],
            'chronological_holdout_races':len(predictions),'predictions':predictions,
            'calibration':'UNVALIDATED_SMALL_SAMPLE','performance_improvement_claim':False,
            'production_authority':False,'new_forward_oos_credit':0}
    output_data={'profile':'OHI-FROZEN-READONLY-ACCEPTANCE-20261026-v1','cohorts':cohorts,
        'source_files':files,'first_failures':failures,'retraining':training,
        'no_original_modified':all(hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in files),
        'runtime_post_count':0,'original_krs_reexecuted':False,'production_effect':'NONE','new_forward_oos_credit':0,
        'code_dependencies_sha256':{rel:hashlib.sha256((ROOT/rel).read_bytes()).hexdigest() for rel in (
            'scripts/ohi_frozen_acceptance.py','runtime/local_result_settlement.py',
            'runtime/local_fullnumerical_production.py','runtime/local_nar_evidence_candidate.py',
            'runtime/local_race_key_shadow_owner.py','runtime/local_mec_r4_bridge.py','runtime/local_mec_r5_shadow.py',
            'mapping/local_full_numerical_mapping_v1.0_production_20261008.json',
            'mapping/local_evidence_feature_rule_registry_v1.1_production_numerical_20261008.json')},
        'runtime_health_sha256':sha(health)}
    output_data['sha256']=sha(output_data);write(output/'acceptance.json',output_data)
    return output_data


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--no-retrain',action='store_true')
    args=p.parse_args();output=Path(args.output).resolve()
    if output==ROOT or ROOT in output.parents: raise ValueError('USE_SEPARATE_PRIVATE_DIAGNOSTIC_OUTPUT')
    gateway=load_gateway();cfg=family_config('LOCAL',gateway)
    status,health=request_json(cfg['external_endpoint'].rstrip('/')+'/health',method='GET',attempts=1,timeout=20)
    if status!=200:raise ValueError('CURRENT_LOCAL_RUNTIME_HEALTH_UNAVAILABLE')
    write(output/'runtime_health.json',health)
    data=audit(output,health=health,retrain=not args.no_retrain)
    print(json.dumps({'sha256':data['sha256'],'cohorts':{d:v['production'] for d,v in data['cohorts'].items()},
                      'failures':len(data['first_failures']),'retraining':{k:v for k,v in data['retraining'].items() if k!='predictions'}},ensure_ascii=False))


if __name__=='__main__':main()

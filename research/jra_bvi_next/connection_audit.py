"""Read-only BVI scalar sensitivity and bounded role-audit regression.

All outputs are post-capture research. Real request/source files are never
changed; no external service, KRS, MEC, Capital or ticket purchase is invoked.
"""
from __future__ import annotations

import argparse
from collections import Counter
import copy
import hashlib
import json
import math
from pathlib import Path

from candidate import load_fixed_module, predict, role_audit_proposal, is_explicit_jump, sha, PROFILE


def restore_model(record):
    return {**{k:v for k,v in record.items() if k != 'stages'},
            'stages':[{'factor':s['factor'],'terms':{tuple(t['key']):{k:v for k,v in t.items() if k!='key'} for t in s['terms']}} for s in record['stages']]}


def role_columns(req):
    by_id = req['static_prediction']['roles']
    return {role:[rid for rid,roles in by_id.items() if role in roles] for role in ('W','P2','P3')}


def environment_band(interaction):
    effect=sum(c['effect'] for c in interaction)
    qualified=bool(interaction) and all(type(c.get('standard_error_proxy')) in (int,float)
                                       and math.isfinite(c['standard_error_proxy'])
                                       and c['standard_error_proxy']>=0 for c in interaction)
    se_upper=sum(c['standard_error_proxy'] for c in interaction) if qualified else None
    return effect,se_upper,effect-1.96*se_upper if se_upper is not None else None


def summarize_outcomes(outcomes):
    qualified=[r for r in outcomes if r['status']=='ARCHIVED_OFFICIAL_LABEL_READ; NOT_INDEPENDENTLY_REVERIFIED_HERE']
    return {'qualified_archived_result_races':len(qualified),'unknown_archived_result_races':len(outcomes)-len(qualified),
            'unevaluated_rescues':sum(r.get('unevaluated_rescues',0) for r in outcomes),
            'correct_P3_rescues':sum(r['P3_correct_rescue'] for r in qualified) if qualified else None,
            'false_P3_rescues':sum(r['false_P3_rescue'] for r in qualified) if qualified else None,
            'false_top3_additions':sum(r['false_top3_candidate_additions'] for r in qualified) if qualified else None}


def run(repository, models_path, output_dir):
    fixed=load_fixed_module(repository)
    from jra_index_provenance_builder import materialize_index_provenance
    publication=json.loads(models_path.read_text())
    if publication['sha256'] != sha({k:v for k,v in publication.items() if k!='sha256'}):
        raise ValueError('CANDIDATE_MODEL_HASH_MISMATCH')
    model=restore_model(publication['models']['HIERARCHICAL_ENV'])
    records=[];scalar_counts=Counter()
    for path in sorted((repository/'runtime/requests').glob('*20261025*FORMAL.json')):
        req=json.loads(path.read_text());source=req['source_snapshot']
        if sha(source)!=req['source_snapshot_sha256']:
            raise ValueError('ARCHIVED_SOURCE_BINDING_MISMATCH:'+req['race_id'])
        context=source.get('jra_race_context') or {}
        detail=source.get('jra_official_race_card_detail') or {}
        observed=detail.get('race_environment') or {}
        histories=(source.get('jra_official_horse_history') or {}).get('runners') or {}
        card=detail.get('runners') or []
        cards={str(r.get('runner_id') or r.get('horse_no')):r for r in card}
        environment={'venue':req['race']['venue'],'surface':req['race']['surface'],
                     'distance_m':req['race']['distance'],'race_date':req['race_date'],
                     'race_name':req['race']['race_name'],'field_size':len(req['runners']),
                     'going':context.get('going') or observed.get('going')}
        predictions=[]
        for runner in req['runners']:
            rid=str(runner['runner_id']);raw=copy.deepcopy(cards[rid]);history=histories.get(rid) or {}
            ped=history.get('pedigree') or {}
            if history.get('horse_name') and history['horse_name']!=raw.get('horse_name'):
                raise ValueError('ARCHIVED_HISTORY_IDENTITY_CONFLICT')
            for key in ('sire','dam','damsire'):
                if raw.get(key) and ped.get(key) and raw[key]!=ped[key]:
                    raise ValueError('ARCHIVED_PARENT_IDENTITY_CONFLICT')
                raw[key]=raw.get(key) or ped.get(key)
            runs=history.get('runs') or raw.get('recent_runs') or []
            raw['runs']=[r for r in runs if not is_explicit_jump(r)]
            row=fixed._prediction_row(raw,environment)
            score,components=predict(model,row,fixed)
            general=[c for c in components if c['factor'] in ('sire','damsire','sire_damsire_pair')]
            interaction=[c for c in components if c['factor'] not in ('sire','damsire','sire_damsire_pair','season')]
            # Same horse and parent participates in multiple terms: do not
            # assume their uncertainty estimates are independent.
            effect,se_upper,lower=environment_band(interaction)
            predictions.append({'runner_id':rid,'name':runner.get('name'),'research_score':round(score*100,6),
                                'environment_effect':effect,'environment_lower_proxy':lower,
                                'uncertainty':'SUM_OF_TERM_CLUSTER_SE_CONSERVATIVE_PROXY; NOT_CALIBRATED_CI',
                                'uncertainty_status':'AVAILABLE_UNCALIBRATED_PROXY' if lower is not None else 'UNKNOWN_TERM_CLUSTER_SE_OR_NO_ENVIRONMENT_SUPPORT',
                                'minimum_general_offspring':min((c['composite_offspring'] for c in general),default=0),
                                'minimum_environment_offspring':min((c['composite_offspring'] for c in interaction),default=0),
                                'general_components':general,'environment_components':interaction})
        proposal=role_audit_proposal(role_columns(req),predictions)
        # Pure scalar perturbation of each original BVI. Only this research
        # copy is recalculated through the existing canonical formulas.
        before=materialize_index_provenance(req)
        perturb=copy.deepcopy(req)
        for rid,spec in perturb['index_provenance_ledger']['runners'].items():
            spec['base_indices']['BVI']['value']=min(100.,spec['base_indices']['BVI']['value']+1.)
        after=materialize_index_provenance(perturb)
        by_before={str(r['runner_id']):r for r in before['runners']}
        by_after={str(r['runner_id']):r for r in after['runners']}
        delta={key:sum(abs(by_before[rid]['canonical_components'][key]['value']-by_after[rid]['canonical_components'][key]['value'])>1e-6 for rid in by_before)
               for key in ('BVI','TPI','ZAI_WIN','ZAI_PLACE','SRI','F3S','T3I')}
        scalar_counts.update(delta)
        pairs={(str(p['head']),str(p['second'])) for p in req['pair_dispositions'] if p['status']!='EXCLUDE'}
        hypothetical_thirds={(a,b,h) for h in proposal['p3_rescue'] for a,b in pairs if h not in (a,b)}
        records.append({'race_id':req['race_id'],'classification':'KNOWN_20261025_POST_CAPTURE_REGRESSION; NO_FORWARD_OOS',
                        'source_sha256':req['source_snapshot_sha256'],'original_prediction_cutoff':req['prediction_cutoff'],
                        'request_raw_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                        'candidate_model_record_sha256':publication['sha256'],
                        'candidate_dataset_sha256':publication['dataset_sha256'],
                        'original_roles':role_columns(req),'proposal':proposal,'predictions':predictions,
                        'scalar_plus_one_changed_cells':delta,
                        'hypothetical_semantic_third_orientation_upper_bound':len(hypothetical_thirds),
                        'hypothetical_100yen_trifecta_stake_upper_bound':100*len(hypothetical_thirds),
                        'cost_status':'UPPER_BOUND_ONLY; NO_MEC_KRS_TICKETS_OR_CAPITAL_EXECUTED',
                        'results_used_in_proposal':False})
    output_dir.mkdir(parents=True,exist_ok=True)
    # Persist every proposed role before any result label is opened. The clock
    # is post-capture, never marketed as a historical pre-result witness.
    frozen={'profile':PROFILE+'-CONNECTION-AUDIT','classification':'POST_CAPTURE; NOT_FORWARD_OOS',
            'records':records,'scalar_total_changed_cells':dict(scalar_counts),
            'production_effect':'NONE','purchase_authority':False,'forward_oos_increment':0}
    frozen['sha256']=sha(frozen)
    proposal_path=output_dir/'connection_proposals.json'
    if proposal_path.exists():
        raise ValueError('IMMUTABLE_RESEARCH_PROPOSALS_ALREADY_EXIST')
    proposal_path.write_text(json.dumps(frozen,ensure_ascii=False,indent=2)+'\n')
    outcomes=[]
    for record in records:
        path=repository/'runtime/results'/(record['race_id']+'.json')
        if not path.exists():
            outcomes.append({'race_id':record['race_id'],'status':'ARCHIVED_RESULT_MISSING',
                             'unevaluated_rescues':len(record['proposal']['p3_rescue']),
                             'P3_correct_rescue':None,'false_P3_rescue':None,'false_top3_candidate_additions':None})
            continue
        result=json.loads(path.read_text());official=result.get('official_result') or {}
        if official.get('status')!='OFFICIAL' or len(official.get('top3') or [])!=3:
            outcomes.append({'race_id':record['race_id'],'status':'ARCHIVED_RESULT_UNQUALIFIED',
                             'unevaluated_rescues':len(record['proposal']['p3_rescue']),
                             'P3_correct_rescue':None,'false_P3_rescue':None,'false_top3_candidate_additions':None})
            continue
        top=list(map(str,official['top3']));proposal=record['proposal'];original=record['original_roles']
        rescued=proposal['p3_rescue']
        outcomes.append({'race_id':record['race_id'],'status':'ARCHIVED_OFFICIAL_LABEL_READ; NOT_INDEPENDENTLY_REVERIFIED_HERE',
                         'result_file_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'top3':top,
                         'P3_correct_rescue':sum(h==top[2] for h in rescued),
                         'false_P3_rescue':sum(h!=top[2] for h in rescued),
                         'added_top3_horse':sum(h in top for h in rescued),
                         'false_top3_candidate_additions':sum(h not in top for h in rescued),
                         'before_capture':{role:top[i] in original[role] for i,role in enumerate(('W','P2','P3'))},
                         'after_capture':{role:top[i] in proposal['roles'][role] for i,role in enumerate(('W','P2','P3'))},
                         'candidate_width_increment':proposal['candidate_width_increment'],
                         'PFS':None,'KRS_unique_rescue_harm':None,'ticket_cost_measured':False})
    settled={'profile':PROFILE+'-CONNECTION-REGRESSION','proposal_sha256':frozen['sha256'],'outcomes':outcomes,
             'race_count':len(records),'runner_count':sum(len(r['predictions']) for r in records),
             'proposed_rescues':sum(len(r['proposal']['p3_rescue']) for r in records),
             **summarize_outcomes(outcomes),
             'scalar_total_changed_cells':dict(scalar_counts),'forward_oos_increment':0,
             'decision':'HOLD_UNVALIDATED; MODEL_INCREMENT_REJECTED; NO_PRODUCTION_CONNECTION',
             'PFS':None,'actual_or_virtual_ticket_cost':None,'production_effect':'NONE','purchase_authority':False}
    (output_dir/'connection_evaluation.json').write_text(json.dumps(settled,ensure_ascii=False,indent=2)+'\n')
    return settled


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',type=Path,required=True);p.add_argument('--models',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();out=run(a.repository,a.models,a.output)
    print(json.dumps({k:v for k,v in out.items() if k!='outcomes'},ensure_ascii=False))

"""Explain the actual Oct25 frozen inputs without reconstructing a prediction.

Reuses the enacted role replay. Missing conditions are not low suitability and
generic SOURCE hashes do not establish independent evidence observations.
"""
import argparse
from collections import Counter
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime')]
from jra_role_exclusion_audit import build_role_exclusion_audit
from jra_official_fact_evaluator_production import _observed_runs
from jra_source_runtime.jra_observed_context import resolve_observed_context
from jra_aki_v21 import sha


def raw_sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def bvi_kind(cell):
    if cell.get('components'):
        return 'MEASURED_PLUS_DCR' if cell.get('adjustments') else 'MEASURED'
    return 'DCR_ONLY' if cell.get('adjustments') else 'UNMEASURED_NO_COMPONENT_OR_DCR_PROOF'


def runner_lineage(runner,source):
    rid=str(runner['runner_id']);history=(source.get('jra_official_horse_history',{}).get('runners') or {}).get(rid,{})
    detail=next((r for r in source.get('jra_official_race_card_detail',{}).get('runners',[]) if str(r['runner_id'])==rid),{})
    context=resolve_observed_context(source)
    race_day=date.fromisoformat(source['source_race_context']['race_date'])
    runs=_observed_runs(history,detail,race_day)
    surface=context.get('surface');going=context.get('going')
    selected=[r for r in runs if r.get('surface')==surface and r.get('going')==going]
    features=runner.get('evidence_features') or {};present='going_fit' in features
    if present:going_status='OBSERVED_FEATURE'
    elif not surface or not going:going_status='TARGET_CONTEXT_MISSING'
    elif not runs:going_status='NO_ADMISSIBLE_PRIOR_RUNS'
    elif not selected:going_status='NO_PRIOR_MATCHING_SURFACE_GOING'
    elif len(selected)==1:going_status='ONE_PRIOR_MATCHING_SURFACE_GOING_NOT_EMITTED'
    else:going_status='MATCHING_PRIOR_OBSERVATIONS_NOT_EMITTED_REQUIRES_COMPILER_REVIEW'
    uses={}
    for index,cell in runner['canonical_components'].items():
        for component in cell.get('components') or []:
            if component.get('feature'):uses.setdefault(component['feature'],set()).add(index)
    return {'runner_id':rid,'name':runner.get('name'),
        'identity_namespace':'RACE_BOUND_HORSE_NUMBER_NOT_PERMANENT_REGISTRY_ID',
        'official_profile_token_sha256':history.get('profile_token_sha256'),
        'permanent_registry_id':None,'history_raw_sha256':history.get('raw_sha256'),
        'source_available_at':None,'source_freeze_at':source.get('source_freeze_at'),
        'stored_fetch_times':sorted({str(s['fetched_at']) for s in source.get('sources',[]) if s.get('fetched_at')}),
        'source_available_at_semantics':'First official availability is not established by a freeze or self-recorded fetch time.',
        'parsed_history_count':len(history.get('runs') or []),
        'admissible_prior_runs':len(runs),'prior_runs':runs,
        'going':{'target_surface':surface,'target_going':going,
            'feature_present':present,'matching_prior_runs':len(selected),'status':going_status,
            'missing_is_low_suitability':False},
        'bvi':{'value':runner['canonical_components']['BVI']['value'],
            'class':bvi_kind(runner['canonical_components']['BVI']),
            'components':runner['canonical_components']['BVI'].get('components') or [],
            'adjustments':runner['canonical_components']['BVI'].get('adjustments') or [],
            'permanent_identity_and_independent_label_qualification':'NOT_ESTABLISHED_BY_INDEX_COMPONENTS'},
        'features_present':sorted(features),'feature_rules':{n:f.get('rule_id') for n,f in features.items()},
        'feature_index_uses':{n:sorted(indices) for n,indices in sorted(uses.items())},
        'features_present_not_used_by_frozen_index':sorted(set(features)-set(uses)),
        'shared_feature_index_dependencies':{n:sorted(indices) for n,indices in sorted(uses.items()) if len(indices)>1},
        'numerical_component_count':len(runner['canonical_components']),
        'numerical_components_sha256':sha(runner['canonical_components']),
        'new_numeric_calculations':0}


def audit(data_root):
    root=Path(data_root);authority=json.loads((root/'profiles/KM_FAMILY_CURRENT_AUTHORITY_20261012_R51.json').read_text())
    originals={};races=[];coverage=[];terminals=[]
    for venue in ('TKY','KYO','NGT'):
        for no in range(1,13):
            rid=f'KM-JRA-{venue}-20261025-R{no:02d}'
            qp=root/'runtime/requests'/(rid+'-LIVE-R1-FORMAL.json');fp=root/'runtime/final_artifacts'/(rid+'.json')
            if not qp.exists() or not fp.exists():
                terminal=root/'runtime/jra_no_bet_terminals'/(rid+'-LIVE-R1.json')
                coverage.append({'race_id':rid,'state':'AKI_NO_BET' if terminal.exists() else 'NO_FINAL',
                    'role_prediction_not_reconstructed':True,'new_forward_oos_credit':0})
                if terminal.exists():
                    t=json.loads(terminal.read_text());prepared=t['failure_report']['prepared_numerical_request']
                    originals[str(terminal.relative_to(root))]=raw_sha(terminal)
                    if t['sha256']!=sha({k:v for k,v in t.items() if k!='sha256'}):raise ValueError('LINEAGE_TERMINAL_HASH:'+rid)
                    envelopes=sorted((root/'runtime/executions'/t['source_execution_id']/'SOURCE/runs').glob('*/source_receipt_envelope.json'))
                    bound=[]
                    for path in envelopes:
                        envelope=json.loads(path.read_text())
                        if envelope.get('receipt_sha256')==t['signed_source_receipt_sha256']:
                            source=envelope['artifact']
                            if source.get('race_id')!=rid or source.get('source_snapshot_sha256')!=t['source_snapshot_sha256']:
                                raise ValueError('LINEAGE_TERMINAL_SOURCE_BINDING:'+rid)
                            originals[str(path.relative_to(root))]=raw_sha(path);bound.append(source)
                    if len(bound)!=1:raise ValueError('LINEAGE_TERMINAL_SOURCE_MISSING_OR_DUPLICATE:'+rid)
                    raw_context=str(resolve_observed_context(bound[0]).get('raw_race_context') or '')
                    scope='JRA_JUMP_EXCLUDED_FROM_FLAT_EVALUATION' if '障害' in raw_context else 'JRA_FLAT'
                    terminals.append({'race_id':rid,'venue':venue,'decision_reason':t['decision_reason'],
                        'evaluation_scope':scope,'source_context_raw':raw_context,
                        'production_full20_ready_recorded':t['production_full20_ready'],
                        'recorded_calculated_cells':t['base_calculated_count']+t['derived_calculated_count'],
                        'source_sha256':t['source_snapshot_sha256'],'signed_source_receipt_sha256':t['signed_source_receipt_sha256'],
                        'runner_count':len(prepared['runners']),'runners':[runner_lineage(r,bound[0]) for r in prepared['runners']],
                        'existing_aki_diagnostic':t['failure_report']['aki_selection_failure']['diagnostic'],
                        'formal_role_adoption_reconstructed':False,'krs_executed':False,'signed_final_created':False})
                continue
            q=json.loads(qp.read_text());f=json.loads(fp.read_text())
            if q['race_id']!=rid or f['race_id']!=rid or q['source_snapshot_sha256']!=f['source_snapshot_sha256']:
                raise ValueError('LINEAGE_RACE_SOURCE_FINAL_BINDING:'+rid)
            for path in (qp,fp):originals[str(path.relative_to(root))]=raw_sha(path)
            explanation=build_role_exclusion_audit(q,authority,root)
            runners=[runner_lineage(r,q['source_snapshot']) for r in q['runners']]
            rp=root/'runtime/results'/(rid+'.json');labels=None
            if rp.exists():
                result=json.loads(rp.read_text())
                if result['race_id']!=rid or result['frozen_prediction_ref']['immutable_final_sha256']!=f['sha256']:
                    raise ValueError('LINEAGE_RESULT_BINDING:'+rid)
                originals[str(rp.relative_to(root))]=raw_sha(rp)
                labels=result['official_result']['top3']
            by_id={r['runner_id']:r for r in runners}
            outcome=[]
            if labels is not None:
                for role,h in zip(('W','P2','P3'),map(str,labels)):
                    role_row=next(x for x in explanation['rows'] if x['column']==role and x['runner_id']==h)
                    outcome.append({'role':role,'runner_id':h,'static_rank':q['static_prediction']['ranking'].index(h)+1,
                        'bvi_class':by_id[h]['bvi']['class'],'bvi_value':by_id[h]['bvi']['value'],
                        'saved_status':role_row['saved_status'],'role_captured':role_row['eligible_under_registered_rules'],
                        'unmet_criteria':role_row['unmet_criteria'],'going':by_id[h]['going']})
            coverage.append({'race_id':rid,'state':'FINAL','runners':len(runners),'result_label_available':labels is not None})
            races.append({'race_id':rid,'venue':venue,'source_sha256':q['source_snapshot_sha256'],
                'final_sha256':f['sha256'],'source_freeze_at':q['source_snapshot']['source_freeze_at'],
                'prediction_cutoff':q['prediction_cutoff'],'runners':runners,'role_explanation':explanation,
                'outcome_diagnostics':outcome,'outcome_used_to_form_roles':False})
    by_venue={}
    for venue in ('TKY','KYO','NGT'):
        rows=[r for r in races if r['venue']==venue];runners=[x for r in rows for x in r['runners']]
        by_venue[venue]={'finals':len(rows),'runners':len(runners),'role_cells':sum(r['role_explanation']['role_cell_count'] for r in rows),
            'terminal_runners':sum(t['runner_count'] for t in terminals if t['venue']==venue),
            'flat_terminal_runners':sum(t['runner_count'] for t in terminals if t['venue']==venue and t['evaluation_scope']=='JRA_FLAT'),
            'all_saved_numerical_runners':len(runners)+sum(t['runner_count'] for t in terminals if t['venue']==venue),
            'going_feature_present':sum(r['going']['feature_present'] for r in runners),
            'going_feature_missing':sum(not r['going']['feature_present'] for r in runners),
            'going_status':dict(Counter(r['going']['status'] for r in runners)),
            'bvi_classes':dict(Counter(r['bvi']['class'] for r in runners)),
            'labelled_races':sum(bool(r['outcome_diagnostics']) for r in rows),
            'role_capture':{role:sum(x['role_captured'] for r in rows for x in r['outcome_diagnostics'] if x['role']==role) for role in ('W','P2','P3')}}
    if any(raw_sha(root/p)!=h for p,h in originals.items()):raise ValueError('LINEAGE_ORIGINAL_MUTATION')
    out={'profile':'KM-JRA-20261025-EXISTING-PREDICTION-LINEAGE-v1',
        'classification':'POST_RESULT_EXPLANATION_NOT_NEW_PREDICTION_NOT_FORWARD_OOS',
        'created_at':datetime.now(timezone.utc).isoformat(),'denominator_races':36,'coverage':coverage,
        'by_venue':by_venue,'races':races,'no_bet_terminal_lineage':terminals,'input_raw_sha256':originals,
        'production_numeric_change':False,'new_candidates':0,'new_forward_oos_credit':0,
        'source_final_result_rewritten':0,'runtime_posts':0,
        'independent_signature_reverification':'NOT_PERFORMED_BY_THIS_EXPLANATION',
        'limits':['Missing historical conditions are not measured zero or low suitability.',
            'Horse number / navigation SHA is not a recovered permanent registry ID.',
            'Shared feature dependencies do not prove bias or justify changing Production weights.',
            'Race without canonical RESULT labels remains outcome UNKNOWN; no result reconstructed from predictions.',
            'Existing Kyoto candidate comparison remains the original research cohort and hashes.']}
    out['sha256']=sha(out);return out


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--data-root',type=Path,default=ROOT)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();out=audit(args.data_root)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'by_venue':out['by_venue'],'sha256':out['sha256'],'new_candidates':0,'new_oos_credit':0},ensure_ascii=False))


if __name__=='__main__':main()

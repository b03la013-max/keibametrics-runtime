"""Saved-input replay and failure attribution.  Outcome access is evaluation-only."""
from __future__ import annotations

from collections import Counter,defaultdict
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import statistics
import sys

from candidates import ROOT, ROLES, ROLE_INDEX, digest, predict, POLICY, order, instant
from input_audit import race_input_audit, migration_summary

sys.path.insert(0,str(ROOT/'runtime'))
from jra_production_postresult import verify_final

def load(path):return json.loads(path.read_text())


def archived_shadow_lineage(data_root, race_id, final):
    path=Path(data_root)/'runtime/role_rescue_shadow'/(race_id+'.json')
    if not path.exists():return {'status':'ORIGINAL_SHADOW_UNAVAILABLE'}
    shadow=load(path)
    if shadow.get('sha256')!=digest({k:v for k,v in shadow.items() if k!='sha256'}):raise ValueError('REPLAY_ORIGINAL_SHADOW_HASH')
    if (shadow.get('race_id')!=race_id or shadow.get('baseline_final_sha256')!=final['sha256'] or shadow.get('source_sha256')!=final['source_snapshot_sha256']):raise ValueError('REPLAY_ORIGINAL_SHADOW_BINDING')
    return {
        'path':str(path.relative_to(data_root)),
        'original_shadow_sha256':shadow['sha256'],
        'original_prediction_input_sha256':shadow.get('prediction_input_sha256'),
        'original_checkpoint_learning_input_sha256':shadow.get('checkpoint_learning_input_sha256'),
        'original_learning_state_bindings':shadow.get('learning_state_bindings'),
        'original_learning_applied_to_arm':shadow.get('learning_applied_to_arm'),
        'original_shadow_code_sha256':shadow.get('code_sha256'),
        'original_shadow_policy_fingerprint':shadow.get('policy_fingerprint'),
        'does_not_witness_new_research_candidate_freeze':True,
        'new_candidate_reads_learning_states_numerically':False,
        'fresh_states_read':0,
    }

def source_for_terminal(data_root,terminal):
    paths=sorted((data_root/'runtime/executions'/terminal['source_execution_id']/'SOURCE/runs').glob('*/source_receipt_envelope.json'))
    for path in paths:
        env=load(path)
        if env.get('receipt_sha256')==terminal['signed_source_receipt_sha256']:
            if env['artifact']['source_snapshot_sha256']!=terminal['source_snapshot_sha256']:raise ValueError('REPLAY_SOURCE_TERMINAL_BINDING')
            return env['artifact'],str(path.relative_to(data_root))
    raise ValueError('REPLAY_ORIGINAL_SOURCE_MISSING')

def load_race(data_root,race_id):
    data_root=Path(data_root);fp=data_root/'runtime/final_artifacts'/(race_id+'.json')
    if fp.exists():
        f=load(fp);verify_final(f);qp=data_root/'runtime/requests'/(race_id+'-LIVE-R1-FORMAL.json');q=load(qp);rp=data_root/'runtime/results'/(race_id+'.json');r=load(rp)
        if (q['race_id']!=race_id or q['source_snapshot_sha256']!=f['source_snapshot_sha256'] or r['frozen_prediction_ref']['immutable_final_sha256']!=f['sha256']):raise ValueError('REPLAY_FINAL_RESULT_SOURCE_BINDING')
        official=r['official_result'];kind='PAPER' if f.get('capital_policy_decision',{}).get('decision')=='PAPER' else 'FORMAL_FINAL'
        return {'race_id':race_id,'venue':race_id.split('-')[2],'q':q,'f':f,'result':r,'official':official,'top3':list(map(str,official['top3'])),'kind':kind,'baseline_roles':f['static_prediction']['roles'],'provenance':{'request_path':str(qp.relative_to(data_root)),'request_file_sha256':sha256(qp.read_bytes()).hexdigest(),'request_payload_sha256':digest(q),'final_sha256':f['sha256'],'result_sha256':digest(r),'original_archived_shadow_lineage':archived_shadow_lineage(data_root,race_id,f),'signature_independently_reverified_by_this_replay':False,'label_trust':'CANONICAL_OFFICIAL_RESULT_BOUND_TO_FROZEN_FINAL'}}
    tp=data_root/'runtime/jra_no_bet_terminals'/(race_id+'-LIVE-R1.json');t=load(tp)
    if t['sha256']!=digest({k:v for k,v in t.items() if k!='sha256'}):raise ValueError('REPLAY_TERMINAL_HASH')
    source,sp=source_for_terminal(data_root,t);q=deepcopy(t['failure_report']['prepared_numerical_request']);q.update(source_snapshot=source,source_snapshot_sha256=t['source_snapshot_sha256'],prediction_cutoff=t['prediction_cutoff'],scheduled_post_at=t['scheduled_post_at'])
    static=deepcopy(t['failure_report'].get('static_owner_executable_diagnostic',{}).get('static_prediction',{}));cols=t['failure_report'].get('aki_selection_failure',{}).get('diagnostic',{}).get('columns',{})
    roles={str(r['runner_id']):[role for role in ROLES if str(r['runner_id']) in cols.get(role,[])] for r in q['runners']};static['roles']=roles;q['static_prediction']=static
    op=data_root/'runtime/source_candidate_oos'/race_id/'official_result_observation.json';o=load(op)
    if o['race_id']!=race_id or o['status']!='OFFICIAL_POST_RESULT_SNAPSHOT' or not o.get('raw_sha256'):raise ValueError('REPLAY_OFFICIAL_OBSERVATION_BINDING')
    official={'top3':o['result_top3'],'payouts':o['payouts'],'captured_at':o['captured_at']}
    return {'race_id':race_id,'venue':race_id.split('-')[2],'q':q,'f':None,'terminal':t,'official':official,'top3':list(map(str,o['result_top3'])),'kind':'AKI_NO_BET','baseline_roles':roles,'provenance':{'prepared_input_path':str(tp.relative_to(data_root))+'#/failure_report/prepared_numerical_request','original_prepared_input_sha256':digest(t['failure_report']['prepared_numerical_request']),'original_terminal_sha256':t['sha256'],'source_path':sp,'official_result_observation_path':str(op.relative_to(data_root)),'official_result_observation_sha256':digest(o),'research_view_augmented_with_original_source_and_failed_columns':True,'label_trust':'OFFICIAL_POST_RESULT_SNAPSHOT_NOT_SIGNED_RESULT','does_not_complete_production_result_learning':True}}

def race_ids(day='20261024'):
    return [f'KM-JRA-{v}-{day}-R{n:02d}' for v in ['TKY','KYO','NGT'] for n in range(1,13)]

def role_evaluation(rank,row):
    actual=row['top3'];width={r:sum(r in roles for roles in row['baseline_roles'].values()) for r in ROLES}
    selected={r:rank['ranking'][r][:width[r]] for r in ROLES};h=rank['ranking']['W'][0];s=rank['head_local_p2'][h][0];t=rank['pair_conditioned_third'][h+'>'+s][0]
    captured={r:a in selected[r] for r,a in zip(ROLES,actual)}
    baseline={r:r in row['baseline_roles'].get(a,[]) for r,a in zip(ROLES,actual)}
    pair=captured['W'] and actual[1] in rank['head_local_p2'][actual[0]][:width['P2']]
    exact=pair and actual[2] in rank['pair_conditioned_third'][actual[0]+'>'+actual[1]][:width['P3']]
    return {'actual_role_rank':{r:rank['ranking'][r].index(a)+1 for r,a in zip(ROLES,actual)},'matched_width':width,'matched_width_role_capture':captured,'baseline_role_capture':baseline,'unique_role_rescue':{r:captured[r] and not baseline[r] for r in ROLES},'unique_role_harm':{r:baseline[r] and not captured[r] for r in ROLES},'predicted_chain':[h,s,t],'top1_ordered_pair':[h,s]==actual[:2],'top1_ordered_exact':[h,s,t]==actual,'matched_width_conditional_pair':pair,'matched_width_conditional_exact':exact,'matched_width_conditional_is_set_capture_not_top1_prediction':True,'selected_roles':selected}

def failure_matrix(row,diagnostics):
    actual=row['top3'];q=row['q'];runners={str(r['runner_id']):r for r in q['runners']};f=row['f'];roles=row['baseline_roles'];role_rows={}
    for role,h in zip(ROLES,actual):
        values={rid:x['canonical_components'][ROLE_INDEX[role]]['value'] for rid,x in runners.items()};ranking=order(values);runner=runners[h];bvi=runner['canonical_components']['BVI']
        role_rows[role]={'runner_id':h,'name':runner.get('name'),'role_selected':role in roles.get(h,[]),'role_index':ROLE_INDEX[role],'role_index_value':values[h],'role_index_rank':ranking.index(h)+1,'static_rank':list(map(str,(f or {}).get('static_prediction',q.get('static_prediction',{})).get('ranking',[]))).index(h)+1 if h in list(map(str,(f or {}).get('static_prediction',q.get('static_prediction',{})).get('ranking',[]))) else None,'bvi_class':'DCR_ONLY' if not bvi.get('components') else 'MEASURED_PLUS_DCR' if bvi.get('adjustments') else 'MEASURED','input_evidence':diagnostics[h],'selected_role_list':roles.get(h,[]),'all20':{i:runner['canonical_components'][i]['value'] for i in runner['canonical_components']}}
    pair=next((x for x in (f or {}).get('pair_dispositions',[]) if str(x.get('head'))==actual[0] and str(x.get('second'))==actual[1]),None)
    third=next((x for x in (f or {}).get('third_dispositions',[]) if [str(x.get(k)) for k in ['head','second','third']]==actual),None)
    tickets=(f or {}).get('final_ticket',{}).get('tickets',[]);exacta=any(t['bet_type']=='EXACTA' and list(map(str,t['selection']))==actual[:2] for t in tickets);exact=any(t['bet_type']=='TRIFECTA' and list(map(str,t['selection']))==actual for t in tickets);trio=any(t['bet_type']=='TRIO' and set(map(str,t['selection']))==set(actual) for t in tickets)
    missing=[role for role in ROLES if not role_rows[role]['role_selected']]
    if missing:first=missing[0]+'_ROLE_SELECTION'
    elif not pair or pair.get('status') not in {'PURCHASE','PROTECT'}:first='HEAD_LOCAL_PAIR_DISPOSITION'
    elif not third or third.get('status') not in {'PURCHASE','PROTECT'}:first='PAIR_CONDITIONED_THIRD_DISPOSITION'
    elif not exact:first='PROTECTED_EXACT_NOT_CONVERTED' if pair.get('status')=='PROTECT' or third.get('status')=='PROTECT' else 'MEC_CAPITAL_OR_TICKET_CONVERSION'
    else:first='ORDERED_EXACT_CAPTURED'
    if row['kind']=='AKI_NO_BET':terminal_reason=row['terminal']['decision_reason']
    elif row['kind']=='PAPER':terminal_reason=(f.get('capital_policy_decision') or {}).get('reason')
    else:terminal_reason=None
    utility=(f or {}).get('krs_prediction_utility') or {}
    rescue={role:[{k:p.get(k) for k in ['horse_no','proposal','actionable','tier','reason','krs_rank']} for p in utility.get('role_proposals',[]) if str(p.get('horse_no'))==h and p.get('proposal')=='ADD_'+role+'_SHADOW'] for role,h in zip(ROLES,actual)}
    return {'race_id':row['race_id'],'venue':row['venue'],'kind':row['kind'],'actual_top3':actual,'roles':role_rows,'first_prediction_failure':first,'purchase_terminal_reason':terminal_reason,'correct_pair_disposition':pair,'correct_third_disposition':third,'correct_ticket_present':{'EXACTA':exacta,'TRIFECTA':exact,'TRIO':trio},'krs_correct_role_proposals':rescue,'krs_actionable_is_not_purchase_authority':True,'provenance':row['provenance']}

def summary(items):
    if not items:return {'races':0}
    return {'races':len(items),'role_capture':{r:sum(x['matched_width_role_capture'][r] for x in items) for r in ROLES},'mean_actual_role_rank':{r:statistics.mean(x['actual_role_rank'][r] for x in items) for r in ROLES},'role_unique_rescue':{r:sum(x['unique_role_rescue'][r] for x in items) for r in ROLES},'role_unique_harm':{r:sum(x['unique_role_harm'][r] for x in items) for r in ROLES},'top1_ordered_pair':sum(x['top1_ordered_pair'] for x in items),'top1_ordered_exact':sum(x['top1_ordered_exact'] for x in items),'matched_width_conditional_pair':sum(x['matched_width_conditional_pair'] for x in items),'matched_width_conditional_exact':sum(x['matched_width_conditional_exact'] for x in items)}


def paired_control_metrics(rows, arm_name, control='STATIC_INDEX'):
    paired=[(row['evaluations'][arm_name],row['evaluations'][control])
            for row in rows if arm_name in row['evaluations']]
    return {
        'control':control,'paired_races':len(paired),
        'role_capture_delta':{
            role:sum(int(a['matched_width_role_capture'][role])-int(b['matched_width_role_capture'][role]) for a,b in paired)
            for role in ROLES},
        'mean_actual_role_rank_delta':{
            role:statistics.mean(a['actual_role_rank'][role]-b['actual_role_rank'][role] for a,b in paired)
            for role in ROLES},
        'not_a_bvi_gain_against_production_role_rules':arm_name=='BVI_NEUTRAL_SENSITIVITY',
    }

def run(data_root):
    output=[];matrix=[];allrunner=[];input_audits=[];venue_mechanism=defaultdict(list);duplicate=Counter();feature_seen=Counter();calibration=[];baseline_counts={v:Counter() for v in ['ALL','TKY','KYO','NGT']};baseline_formal_counts={v:Counter() for v in ['ALL','TKY','KYO','NGT']}
    sys.path.insert(0,str(ROOT/'research/jra_conditional_rank'))
    from probability_shadow import scores,distribution,measures,ece
    old_probability=load(ROOT/'research/jra_conditional_rank/probability_candidate.json')
    for rid in race_ids():
        row=load_race(data_root,rid);projection=predict(row['q'],row['f']);evaluations={name:role_evaluation(arm,row) for name,arm in projection['arms'].items()}
        for venue in ['ALL',row['venue']]:
            for i,role in enumerate(ROLES):
                baseline_counts[venue][role]+=role in row['baseline_roles'].get(row['top3'][i],[])
                if row['kind']!='AKI_NO_BET':baseline_formal_counts[venue][role]+=role in row['baseline_roles'].get(row['top3'][i],[])
        matrix.append(failure_matrix(row,projection['all_runner_diagnostics']))
        input_audits.append(race_input_audit(row['q'],row['f'],projection,row['baseline_roles']))
        output.append({'race_id':rid,'venue':row['venue'],'kind':row['kind'],'runners':len(row['q']['runners']),'evaluations':evaluations,'unavailable_arms':projection['unavailable_arms'],'input_provenance':row['provenance'],'arms':{name:{k:v for k,v in arm.items() if k!='ticket_candidates'} for name,arm in projection['arms'].items()}})
        context=row['q']['source_snapshot'].get('jra_race_context') or {};key=f'{row["venue"]}|{context.get("surface")}|{context.get("distance_m")}'
        for runner in row['q']['runners']:
            h=str(runner['runner_id']);d=projection['all_runner_diagnostics'][h];features=runner.get('evidence_features') or {}
            bvi=runner['canonical_components']['BVI'];bvi_class='DCR_ONLY' if not bvi.get('components') else 'MEASURED_PLUS_DCR' if bvi.get('adjustments') else 'MEASURED'
            entry={'race_id':rid,'venue':row['venue'],'runner_id':h,'name':runner.get('name'),'context':{k:context.get(k) for k in ['surface','distance_m','going','course_variant','weight_rule']},'observed_features':{k:{p:v.get(p) for p in ['category','observation_count','source_fact','rule_id','evidence_refs','result_derived']} for k,v in features.items()},'bvi_class':bvi_class,'diagnostics':d}
            allrunner.append(entry);venue_mechanism[key].append(entry)
            for feature,indices in d['duplicate_feature_indices'].items():duplicate[feature+'|'+','.join(indices)]+=1
            for feature in features:feature_seen[feature]+=1
        dist=distribution(scores(row['q']['runners'],old_probability['rank_model']),old_probability['temperatures'])
        calibration.append({'race_id':rid,'kind':row['kind'],'metrics':{role:measures(dist['marginals'][role],h) for role,h in zip(ROLES,row['top3'])}})
    arms=sorted({name for r in output for name in r['evaluations']})
    result={'classification':POLICY['classification'],'production_effect':'NONE','genuine_oos_credit':0,'minimum_forward_distinct_races':60,'minimum_forward_days':3,'minimum_forward_venues':2,'policy':POLICY,'policy_sha256':digest(POLICY),'races':output,'failure_matrix':matrix,'all_runner_audit':allrunner,'candidate_metrics':{name:{venue:summary([r['evaluations'][name] for r in output if name in r['evaluations'] and (venue=='ALL' or r['venue']==venue)]) for venue in ['ALL','TKY','KYO','NGT']} for name in arms},'formal_only_candidate_metrics':{name:{venue:summary([r['evaluations'][name] for r in output if name in r['evaluations'] and r['kind']!='AKI_NO_BET' and (venue=='ALL' or r['venue']==venue)]) for venue in ['ALL','TKY','KYO','NGT']} for name in arms},'baseline_capture':{v:dict(c) for v,c in baseline_counts.items()},'baseline_formal_only_capture':{v:dict(c) for v,c in baseline_formal_counts.items()},'shared_feature_dependencies':dict(duplicate),'observed_feature_counts':dict(feature_seen),'venue_mechanisms':{key:{'runner_observations':len(items),'races':len({x['race_id'] for x in items}),'feature_counts':{f:sum(f in x['observed_features'] for x in items) for f in ['position_quality','dash_quality','pace_resilience','closing_quality','course_geometry_fit','distance_fit','going_fit','same_day_track_fit']},'missing_specific_mechanism_measurements':['independent speed trajectory','course segment timestamps','independent tactical labels'],'causal_mechanism_validation':'UNKNOWN; observed coarse feature association does not validate hills/rail/straight dynamics','local_rules_imported':False} for key,items in venue_mechanism.items()},'probability_readiness':{'reference_model_sha256':old_probability['sha256'],'reference_model_created_at':old_probability['created_at'],'training_races':len(old_probability['rank_model']['training_manifest']),'calibration_races':len(old_probability['calibration_manifest']),'evaluation_races':len(calibration),'split':'existing pre-October24 frozen model/temperature; October24 replay evaluation only','metrics':{role:{'mean_log_loss':statistics.mean(r['metrics'][role]['log_loss'] for r in calibration),'mean_brier_sum':statistics.mean(r['metrics'][role]['brier_sum'] for r in calibration),'top1_ece_5bins':ece([r['metrics'][role] for r in calibration])} for role in ROLES},'calibration_accepted':False,'ev_kelly_authority':False,'future_oos_required':True,'races':calibration},'positive_controls':{'policy':'all baseline-correct roles/races retained in denominator; worsening reported, no cherry-picking','role_harm_counts_in_candidate_metrics':True},'unaccepted_research_runs_imported':0,'actual_purchase':'UNVERIFIED'}
    result['frozen_input_audits']=input_audits
    result['role_migration_counts']=migration_summary(input_audits)
    result['paired_static_index_control']={name:paired_control_metrics(output,name) for name in arms}
    result['history_observation_summary']={
        venue:{
            'runners':sum(venue=='ALL' or x['venue']==venue for x in allrunner),
            'runners_with_admitted_prior_history':sum((venue=='ALL' or x['venue']==venue) and x['diagnostics']['history']['observations']>0 for x in allrunner),
            'admitted_prior_runs':sum(x['diagnostics']['history']['observations'] for x in allrunner if venue=='ALL' or x['venue']==venue),
            'status_counts':dict(Counter(x['diagnostics']['history']['status'] for x in allrunner if venue=='ALL' or x['venue']==venue)),
        } for venue in ['ALL','TKY','KYO','NGT']}
    result['newcomer_input_coverage']=[{'race_id':x['race_id'],**x['newcomer_workout_coverage']} for x in input_audits if '新馬' in str(x['context'].get('race_class'))]
    result['sha256']=digest(result);return result

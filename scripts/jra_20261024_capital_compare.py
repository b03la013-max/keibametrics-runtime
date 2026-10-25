"""Replay frozen 24 October originals and result-blind research allocations.

Outputs only research evidence. Does not change original FINAL/RESULT/Learning,
dispatch a workflow, or grant purchase authority. All new variants are post-result
exploration and must start a separate future OOS cohort.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import gzip
import importlib.util
import json
import statistics
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'runtime')]
from research.jra_20261024_capital.comparison import (
    POLICY, digest, key, ranked_tickets, matched_exposure, concentration,
    evaluate_portfolio, settle, cash_metrics)
from jra_production_postresult import settle_final

ROLES=('W','P2','P3')
ROLE_INDEX={'W':'ZAI_WIN','P2':'ZAI_PLACE','P3':'T3I'}

def load(path):return json.loads(path.read_text())

def rank(values):return sorted(values,key=lambda h:(-values[h],int(h)))

def static_ranks(request):
    return {role:rank({str(r['runner_id']):r['canonical_components'][index]['value'] for r in request['runners']}) for role,index in ROLE_INDEX.items()}

def native_candidates(final,request):
    roles=final.get('krs_prediction_utility') or {};rankings={}
    static=static_ranks(request)
    summary=roles.get('summary') or []
    for role,metric in [('W','SSR-W'),('P2','SSR-P2'),('P3','SSR-T3')]:
        kr=rank({str(r['horse_no']):r[metric] for r in summary})
        rankings[role]=sorted(static[role],key=lambda h:(static[role].index(h)+kr.index(h),int(h)))
    return ranked_tickets(rankings)

def protected_candidates(final,request):
    rr=static_ranks(request);pool=[]
    for t in final['minimum_efficient_coverage'].get('tickets') or []:
        pool.append({**t,'priority_score':-1e6})
    for p in final.get('pair_dispositions') or []:
        if p.get('status') not in {'PURCHASE','PROTECT'}:continue
        h,s=str(p['head']),str(p['second'])
        pool.append({'bet_type':'EXACTA','selection':[int(h),int(s)],
            'priority_score':(1e6 if p['status']=='PROTECT' else 0)-rr['W'].index(h)-rr['P2'].index(s)})
    for p in final.get('third_dispositions') or []:
        if p.get('status') not in {'PURCHASE','PROTECT'}:continue
        h,s,t=map(str,(p['head'],p['second'],p['third']))
        score=(1e6 if p['status']=='PROTECT' else 0)-rr['W'].index(h)-rr['P2'].index(s)-rr['P3'].index(t)
        for kind,sel in [('TRIFECTA',[int(h),int(s),int(t)]),('TRIO',sorted(map(int,(h,s,t))))]:
            pool.append({'bet_type':kind,'selection':sel,'priority_score':score})
    return pool

def cash(row,settled):
    return {'race_id':row['race_id'],'venue':row['venue'],'post_at':row['post_at'],
        'investment':settled['total_investment'],'return':settled['total_payout'],
        'refund':settled.get('refund',0),
        'effective_investment':settled.get('effective_investment',settled['total_investment'])}

def krs_audit(final,official):
    roles=final['static_prediction']['roles'];actual=list(map(str,official['top3']));utility=final['krs_prediction_utility']
    proposals=[p for p in utility.get('role_proposals') or [] if p.get('actionable') is True]
    additions={role:{str(p['horse_no']) for p in proposals if p['proposal']=='ADD_'+role+'_SHADOW'} for role in ROLES}
    baseline={role:role in roles.get(h,[]) for role,h in zip(ROLES,actual)}
    rescue={role:not baseline[role] and h in additions[role] for role,h in zip(ROLES,actual)}
    false_add={role:sorted(additions[role]-{h},key=int) for role,h in zip(ROLES,actual)}
    pair_proposals=utility.get('actionable_ordered_pair_proposals') or []
    third_proposals=utility.get('actionable_pair_third_proposals') or []
    pair={(str(p['head']),str(p['second'])) for p in pair_proposals}
    exact={(str(p['head']),str(p['second']),str(p['third'])) for p in third_proposals}
    return {'actionable_is_purchase_authority':False,'baseline_role_capture':baseline,
        'unique_additive_role_rescue':rescue,'unique_additive_role_harm':{r:False for r in ROLES},
        'harm_definition':'Add-only proposals cannot remove a Production Role; ticket replacement harm is evaluated separately.',
        'false_actionable_role_additions':false_add,'actionable_role_proposal_count':len(proposals),
        'actionable_pair_count':len(pair),'actionable_exact_count':len(exact),
        'correct_actionable_ordered_pair':tuple(actual[:2]) in pair,
        'correct_actionable_ordered_exact':tuple(actual) in exact,
        'false_actionable_pairs':len(pair-{tuple(actual[:2])}),
        'false_actionable_exacts':len(exact-{tuple(actual)})}

def records(data):
    out=[]
    for venue in ['TKY','KYO','NGT']:
        for no in range(1,13):
            rid=f'KM-JRA-{venue}-20261024-R{no:02d}'
            fp=data/'runtime/final_artifacts'/(rid+'.json');rp=data/'runtime/results'/(rid+'.json')
            if fp.exists():
                f=load(fp);q=load(data/'runtime/requests'/(rid+'-LIVE-R1-FORMAL.json'));r=load(rp)
                if (f.get('sha256')!=digest({k:v for k,v in f.items() if k!='sha256'})
                        or r['frozen_prediction_ref']['immutable_final_sha256']!=f['sha256']
                        or q['source_snapshot_sha256']!=f['source_snapshot_sha256']):
                    raise ValueError('CAPITAL_FROZEN_INPUT_BINDING:'+rid)
                out.append({'race_id':rid,'venue':venue,'no':no,'final':f,'request':q,
                    'result':r,'official':r['official_result'],'post_at':f['scheduled_post_at'],
                    'original_paths':{'final':str(fp.relative_to(data)),'request':str((data/'runtime/requests'/(rid+'-LIVE-R1-FORMAL.json')).relative_to(data)),'result':str(rp.relative_to(data))}})
            else:
                terminal=load(data/'runtime/jra_no_bet_terminals'/(rid+'-LIVE-R1.json'))
                obs_path=data/'runtime/source_candidate_oos'/rid/'official_result_observation.json';observation=load(obs_path)
                out.append({'race_id':rid,'venue':venue,'no':no,'terminal':terminal,
                    'request':terminal['failure_report']['prepared_numerical_request'],
                    'official':{'top3':observation['result_top3'],'payouts':observation['payouts']},
                    'post_at':terminal['scheduled_post_at'],'label_status':'OFFICIAL_SAVED_OBSERVATION_NOT_PRODUCTION_SIGNED_RESULT',
                    'original_paths':{'terminal':str((data/'runtime/jra_no_bet_terminals'/(rid+'-LIVE-R1.json')).relative_to(data)),'official_observation':str(obs_path.relative_to(data))}})
    return out

def run(args):
    data=args.data_root;rows=records(data);experiments=[];base_cash=[];arm_cash=defaultdict(list);native_cash=defaultdict(list);no_bet=[];baseline_by_type=defaultdict(list);corrected_by_type=defaultdict(list)
    code_sha=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    comparison_sha=hashlib.sha256((ROOT/'research/jra_20261024_capital/comparison.py').read_bytes()).hexdigest()
    settlement_sha=hashlib.sha256(args.settlement_code.read_bytes()).hexdigest() if args.settlement_code else None
    prediction_sha=None
    settlement_fn=settle_final
    if args.settlement_code:
        spec=importlib.util.spec_from_file_location('jra_20261024_corrected_settlement',args.settlement_code);settlement_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(settlement_module);settlement_fn=settlement_module.settle_final
    module=None
    if args.prediction_root:
        path=args.prediction_root/'research/jra_20261024_prediction/candidates.py'
        prediction_sha=hashlib.sha256(path.read_bytes()).hexdigest()
        spec=importlib.util.spec_from_file_location('jra_20261024_prediction_candidate',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    corrections={}
    if args.correction_evidence:
        correction=load(args.correction_evidence)
        corrections[correction['correction']['race_id']]=correction
    corrected_cash=[]
    for row in rows:
        rid=row['race_id'];q=row['request'];official=row['official'];paths=row['original_paths']
        manifest={p:hashlib.sha256((data/p).read_bytes()).hexdigest() for p in paths.values()}
        if 'final' not in row:
            no_bet.append({'race_id':rid,'state':'AKI_NO_BET','investment':0,'pfs':None,
                'opportunity_cost':'UNKNOWN_NO_FROZEN_PRODUCTION_TICKETS',
                'official_top3':official['top3'],'label_status':row['label_status'],'source_paths':paths,'raw_file_sha256':manifest})
            zero={'race_id':rid,'venue':row['venue'],'post_at':row['post_at'],'investment':0,'return':0,'refund':0,'effective_investment':0}
            base_cash.append(zero);corrected_cash.append(zero)
            continue
        f=row['final'];original=f['final_ticket']['tickets'];stored=row['result']['settlement'];baseline_original=settle(original,official,settlement_fn=settle_final)
        if any(baseline_original[k]!=stored[k] for k in ['total_investment','total_payout','profit_loss','pfs']):
            raise ValueError('FROZEN_BASELINE_REPLAY_DIVERGES:'+rid)
        if rid in corrections:
            audit=corrections[rid];c=audit['correction']
            if (c['sha256']!=digest({k:v for k,v in c.items() if k!='sha256'})
                    or c['immutable_final_sha256']!=f['sha256']
                    or c['original_result_sha256']!=digest(row['result'])
                    or audit['official']['payouts']!=official['payouts']
                    or audit['official']['top3']!=official['top3']):
                raise ValueError('RESEARCH_CORRECTION_LINEAGE:'+rid)
            official={**deepcopy(official),**deepcopy(audit['official'])}
        baseline=settle(original,official,settlement_fn=settlement_fn)
        base_cash.append(cash(row,baseline_original));corrected_cash.append(cash(row,baseline))
        for kind in ['EXACTA','TRIO','TRIFECTA']:
            subset=[t for t in original if t['bet_type']==kind]
            baseline_by_type[row['venue']+'|'+kind].append(cash(row,settle(subset,row['official'],settlement_fn=settle_final)))
            corrected_by_type[row['venue']+'|'+kind].append(cash(row,settle(subset,official,settlement_fn=settlement_fn)))
        if not original:
            mec=f['minimum_efficient_coverage']['tickets'];counter=settle(mec,official,settlement_fn=settlement_fn)
            no_bet.append({'race_id':rid,'state':f['capital_policy_decision']['decision'],'investment':0,'pfs':None,
                'frozen_mec_counterfactual':counter,'hypothetical_point_count':len(mec),
                'minimum_capital':f['capital_policy_decision'].get('required_capital'),
                'classification':'UNPURCHASED_PAPER_COUNTERFACTUAL_NEVER_PRODUCTION_PFS'})
        rr=static_ranks(q);pools={'STATIC_ONLY':ranked_tickets(rr),
            'STATIC_PLUS_KRS_ORDINAL_MEAN':native_candidates(f,q),
            'PROTECTION_FIRST':protected_candidates(f,q)}
        sp=data/'runtime/role_rescue_shadow'/(rid+'.json')
        native=load(sp) if sp.exists() else None
        native_evaluations={}
        if native:
            if native['baseline_final_sha256']!=f['sha256'] or native['source_sha256']!=q['source_snapshot_sha256']:
                raise ValueError('FROZEN_SHADOW_BINDING:'+rid)
            for name in ['KRS_ACTIONABLE','LEARNING_ON','CORE_PROTECTION','WINNER_REAUDIT','HEAD_LOCAL_P2','PAIR_THIRD']:
                ts=native['arms'][name]['tickets'];old={key(t) for t in original}
                pools['FROZEN_'+name]=[{**t,'priority_score':1e6 if key(t) not in old else -1e6} for t in ts]
                if original:
                    z=settle(ts,official,settlement_fn=settlement_fn);native_cash[name].append(cash(row,z))
                    native_evaluations[name]=evaluate_portfolio(f,{'tickets':ts},official,settlement_fn=settlement_fn)
            if native.get('conditional_rank_portfolio'):
                pools['FROZEN_OCT18_EQUAL_EXPOSURE']=[{**t,'priority_score':-i} for i,t in enumerate(native['conditional_rank_portfolio']['tickets'])]
        prediction=module.predict(q,f) if module else None
        metadata={}
        if prediction:
            for name,arm in prediction['arms'].items():
                pools['PREDICTION_'+name]=arm['ticket_candidates'];metadata['PREDICTION_'+name]=arm['metadata']
        race={'race_id':rid,'venue':row['venue'],'state':'PAPER' if f['capital_policy_decision'].get('paper_only') else 'FORMAL_FINAL',
            'post_at':row['post_at'],'baseline':baseline,'original_settlement':stored,'frozen_final_sha256':f['sha256'],
            'correction_applied_to_research_evaluation_only':rid in corrections,
            'source_sha256':q['source_snapshot_sha256'],'feature_input_sha256':digest(q['runners']),
            'baseline_concentration':concentration(original),'krs':krs_audit(f,official),
            'source_paths':paths,'raw_file_sha256':manifest,'portfolios':{},
            'unmatched_native_controls':native_evaluations}
        for name,pool in pools.items():
            portfolio=matched_exposure(f,q,pool,candidate_id='JRA-20261024-'+name,metadata=metadata.get(name))
            evaluation=evaluate_portfolio(f,portfolio,official,settlement_fn=settlement_fn)
            race['portfolios'][name]={'portfolio':portfolio,'evaluation':evaluation,'concentration':concentration(portfolio['tickets'])}
            arm_cash[name].append(cash(row,evaluation['candidate']))
        for name,options in [('PROTECTED_HEAD_PAIR_DIVERSITY',{'diversity':True}),('BET_TYPE_ROUND_ROBIN',{'bet_type_mix':True})]:
            portfolio=matched_exposure(f,q,pools['PROTECTION_FIRST'],candidate_id='JRA-20261024-'+name,**options)
            evaluation=evaluate_portfolio(f,portfolio,official,settlement_fn=settlement_fn)
            race['portfolios'][name]={'portfolio':portfolio,'evaluation':evaluation,'concentration':concentration(portfolio['tickets'])}
            arm_cash[name].append(cash(row,evaluation['candidate']))
        # A deliberately separate zero-exposure structural gate, not equal-budget.
        conc=race['baseline_concentration'];abstain=conc['max_head_share_of_ordered']==1
        guard=settle([] if abstain else original,official,settlement_fn=settlement_fn)
        native_cash['SINGLE_HEAD_PAPER_RESEARCH'].append(cash(row,guard))
        race['single_head_paper_guard']={'triggered':abstain,'same_budget':not abstain,
            'avoided_investment':baseline['total_investment']-guard['total_investment'],
            'foregone_return':baseline['total_payout']-guard['total_payout'],'settlement':guard,
            'production_effect':'NONE','classification':'POST_RESULT_EXPLORATORY_GATE_NOT_MATCHED_EXPOSURE'}
        actual=tuple(official['top3']);exact={'bet_type':'TRIFECTA','selection':list(actual)}
        race['actual_exact_path']={'selection':list(actual),
            'registered_PROTECT':any(str(p.get('status'))=='PROTECT' and tuple(map(int,(p['head'],p['second'],p['third'])))==actual for p in f.get('third_dispositions') or []),
            'in_mec':key(exact) in {key(t) for t in f['minimum_efficient_coverage']['tickets']},
            'in_final':key(exact) in {key(t) for t in original},
            'in_protection_priority':key(exact) in {key(t) for t in race['portfolios']['PROTECTION_FIRST']['portfolio']['tickets']},
            'post_result_label_used_only_for_diagnostic':True}
        experiments.append(race)
    # The three AKI terminals remain zero allocation in every matched arm.
    # They are included only as zero-exposure rows, never supplied invented tickets.
    aki_zeros=[r for r in base_cash if r['race_id'] not in {x['race_id'] for x in experiments}]
    for cashes in arm_cash.values():cashes.extend(deepcopy(aki_zeros))
    def grouped(cashes):return {v:cash_metrics([x for x in cashes if x['venue']==v]) for v in ['TKY','KYO','NGT']}
    def width(counts):return {'total_points':sum(counts),'median_race_points':statistics.median(counts) if counts else None,'maximum_race_points':max(counts,default=0)}
    dependencies=[(Path(__file__),code_sha),(ROOT/'research/jra_20261024_capital/comparison.py',comparison_sha)]
    if args.settlement_code:dependencies.append((args.settlement_code,settlement_sha))
    if args.prediction_root:dependencies.append((args.prediction_root/'research/jra_20261024_prediction/candidates.py',prediction_sha))
    if any(hashlib.sha256(path.read_bytes()).hexdigest()!=expected for path,expected in dependencies):
        raise ValueError('RESEARCH_CODE_CHANGED_DURING_REPLAY')
    report={'profile':POLICY['candidate_id'],'classification':POLICY['classification'],
        'observed_at':datetime.now(timezone.utc).isoformat(),'baseline_main':'1e72d0d01bc41918fa5f460d49c85235f87a486b',
        'source_races':36,'frozen_finals':len(experiments),'zero_bet_terminals':len([r for r in no_bet if r['state']=='AKI_NO_BET']),
        'policy':POLICY,'policy_sha256':digest(POLICY),'code_sha256':code_sha,
        'comparison_code_sha256':comparison_sha,'prediction_code_sha256':prediction_sha,
        'baseline_original_settlement':{'all':cash_metrics(base_cash),'by_venue':grouped(base_cash),
            'by_venue_and_bet_type':{k:cash_metrics(v) for k,v in baseline_by_type.items()},
            'ticket_width':width([len(row.get('final',{}).get('final_ticket',{}).get('tickets',[])) for row in rows])},
        'baseline_refund_corrected_research':{'all':cash_metrics(corrected_cash),'by_venue':grouped(corrected_cash),
            'by_venue_and_bet_type':{k:cash_metrics(v) for k,v in corrected_by_type.items()},
            'evidence_path':str(args.correction_evidence) if args.correction_evidence else None,
            'settlement_code_sha256':settlement_sha,
            'new_signed_RESULT_issued':False},
        'matched_budget_point_comparisons':{name:{'all':cash_metrics(cash),'by_venue':grouped(cash),
            'ticket_width':width([r['portfolios'][name]['portfolio']['ticket_count'] for r in experiments]+[0]*len(aki_zeros)),
            'unique_ticket_rescue':sum(r['portfolios'][name]['evaluation']['unique_ticket_rescue'] for r in experiments),
            'unique_ticket_harm':sum(r['portfolios'][name]['evaluation']['unique_ticket_harm'] for r in experiments),
            'false_positive_redeployed_stake':sum(r['portfolios'][name]['evaluation']['false_positive_redeployed_stake'] for r in experiments),
            'removed_winning_return':sum(r['portfolios'][name]['evaluation']['removed_return'] for r in experiments),
            'exposure':'SAME_BUDGET_AND_TOTAL_POINTS; bet-type counts also exact except BET_TYPE_ROUND_ROBIN'} for name,cash in arm_cash.items()},
        'unmatched_addition_or_abstention_controls':{name:{'all':cash_metrics(cash),'by_venue':grouped(cash),
            'unique_ticket_rescue':sum(r['unmatched_native_controls'].get(name,{}).get('unique_ticket_rescue',0) for r in experiments),
            'unique_ticket_harm':sum(r['unmatched_native_controls'].get(name,{}).get('unique_ticket_harm',0) for r in experiments),
            'false_positive_added_stake':sum(r['unmatched_native_controls'].get(name,{}).get('false_positive_redeployed_stake',0) for r in experiments),
            'added_return':sum(r['unmatched_native_controls'].get(name,{}).get('added_return',0) for r in experiments),
            'removed_return':sum(r['unmatched_native_controls'].get(name,{}).get('removed_return',0) for r in experiments),
            'same_budget_comparison':False,'must_not_mix_with_matched_exposure':True} for name,cash in native_cash.items()},
        'no_bet_opportunity_cost_separate':no_bet,'races':experiments,
        'kyo_refund_correction':'SEPARATE_OFFICIAL_EVIDENCE_CORRECTION_SERIES; original signed records unchanged' if corrections else 'PENDING_COMMON_P0_CORRECTION_INTEGRATION',
        'unknown_future_oos_credit':0,'actual_purchase':'UNVERIFIED','automatic_promotion':False,
        'long_run_robust_pfs':'PENDING_FORWARD_OOS; one observed date cannot satisfy 3 dates or establish R100',
        'positive_controls':[{'race_id':r['race_id'],'baseline':r['baseline'],'candidate_changes':{name:{'net_return_delta':p['evaluation']['net_return_delta'],'unique_ticket_harm':p['evaluation']['unique_ticket_harm']} for name,p in r['portfolios'].items()}} for r in experiments if r['baseline']['profit_loss']>0],
        'required_unknowns':{'ev_kelly':'NOT_ADMITTED_UNCALIBRATED','live_next_race_learning_numeric_consumption':'MEASURE_BY_ROOT_LINEAGE_AUDIT'}}
    report['sha256']=digest(report)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    if args.output.suffix=='.gz':
        args.output.write_bytes(gzip.compress(json.dumps(report,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
    else:args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    summary={k:v for k,v in report.items() if k not in {'races','positive_controls'}}
    summary['replay_semantic_sha256']=report['sha256']
    summary['replay_path']=str(args.output.name);summary['replay_file_sha256']=hashlib.sha256(args.output.read_bytes()).hexdigest()
    summary['race_diagnostics']=[{k:r[k] for k in ['race_id','state','baseline','baseline_concentration','krs','actual_exact_path','single_head_paper_guard']} for r in experiments]
    summary['sha256']=digest({k:v for k,v in summary.items() if k!='sha256'})
    summary_path=args.output.with_name('summary.json');summary_path.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'output':str(args.output),'original_pfs':{k:v['pfs'] for k,v in report['baseline_original_settlement']['by_venue'].items()},'corrected_pfs':{k:v['pfs'] for k,v in report['baseline_refund_corrected_research']['by_venue'].items()},'matched_pfs':{k:v['all']['pfs'] for k,v in report['matched_budget_point_comparisons'].items()},'sha256':report['sha256']},ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data-root',type=Path,default=ROOT);p.add_argument('--prediction-root',type=Path);p.add_argument('--correction-evidence',type=Path);p.add_argument('--settlement-code',type=Path);p.add_argument('--output',type=Path,default=ROOT/'research/jra_20261024_capital/replay.json.gz');run(p.parse_args())

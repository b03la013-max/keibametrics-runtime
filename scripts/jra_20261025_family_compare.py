"""Extend the existing fixed Oct24 comparisons to Oct25, without refitting.

Only frozen request/FINAL data enter construction. Official labels enter after
all portfolios exist. Missing canonical RESULT is never synthesized or marked
closed-loop complete; separately supplied official labels are research only.
"""
import argparse
from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timezone
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import statistics
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'runtime'),str(ROOT/'research/jra_20261024_prediction')]
from candidates import predict,digest,ROLES
from replay import role_evaluation,summary
from scripts.jra_20261024_capital_compare import static_ranks,native_candidates,protected_candidates
from research.jra_20261024_capital.comparison import (
    matched_exposure,evaluate_portfolio,cash_metrics,concentration,ranked_tickets,key)
from jra_production_postresult import verify_final,settle_final
from krs_prediction_utility import evaluate_against_result


def orders(official):
    rows=official.get('top3_orders') or [official['top3']]
    out={tuple(map(str,r)) for r in rows}
    if not out or len(out)!=len(rows) or any(len(r)!=3 or len(set(r))!=3 for r in out):
        raise ValueError('RESEARCH_OFFICIAL_VALID_ORDERS')
    return sorted(out,key=lambda r:tuple(map(int,r)))


def role_score(arm,final,official):
    valid=orders(official)
    rows=[role_evaluation(arm,{'top3':list(r),'baseline_roles':final['static_prediction']['roles']}) for r in valid]
    out=deepcopy(rows[0])
    for name in ['matched_width_role_capture','baseline_role_capture']:
        out[name]={role:any(r[name][role] for r in rows) for role in ROLES}
    out['actual_role_rank']={role:statistics.mean(r['actual_role_rank'][role] for r in rows) for role in ROLES}
    out['unique_role_rescue']={r:out['matched_width_role_capture'][r] and not out['baseline_role_capture'][r] for r in ROLES}
    out['unique_role_harm']={r:out['baseline_role_capture'][r] and not out['matched_width_role_capture'][r] for r in ROLES}
    for name in ['top1_ordered_pair','top1_ordered_exact','matched_width_conditional_pair','matched_width_conditional_exact']:
        out[name]=any(r[name] for r in rows)
    out['official_valid_orders']=[list(r) for r in valid]
    out['tie_semantics']='race-level any-valid-order capture; mean rank over tied valid outcomes'
    return out


def cash(rid,final,settled):
    return {'race_id':rid,'venue':rid.split('-')[2],'post_at':final['scheduled_post_at'],
        'investment':settled['total_investment'],'return':settled['total_payout'],
        'refund':settled.get('refund',0),
        'effective_investment':settled.get('effective_investment',settled['total_investment'])}


def portfolio_pools(request,final,shadow=None):
    # Reuse exactly the pre-existing PR332 eight arms and Capital controls.
    prediction=predict(request,final)
    pools={name:(arm['ticket_candidates'],arm['metadata'],{}) for name,arm in prediction['arms'].items()}
    pools.update(STATIC_ONLY=(ranked_tickets(static_ranks(request)),None,{}),
        STATIC_PLUS_KRS_ORDINAL_MEAN=(native_candidates(final,request),None,{}),
        PROTECTION_FIRST=(protected_candidates(final,request),None,{}))
    pools['PROTECTED_HEAD_PAIR_DIVERSITY']=(pools['PROTECTION_FIRST'][0],None,{'diversity':True})
    pools['BET_TYPE_ROUND_ROBIN']=(pools['PROTECTION_FIRST'][0],None,{'bet_type_mix':True})
    if shadow:
        if (shadow.get('sha256')!=digest({k:v for k,v in shadow.items() if k!='sha256'})
                or shadow['baseline_final_sha256']!=final['sha256']
                or shadow['source_sha256']!=request['source_snapshot_sha256']
                or shadow['race_id']!=request['race_id']
                or shadow['prediction_cutoff']!=request['prediction_cutoff']
                or shadow['runner_universe_sha256']!=digest(sorted(str(r['runner_id']) for r in request['runners']))
                or shadow['source_payload_sha256']!=digest(request['source_snapshot'])):
            raise ValueError('RESEARCH_FROZEN_SHADOW_BINDING')
        old={key(t) for t in final['final_ticket']['tickets']}
        for name in ['KRS_ACTIONABLE','LEARNING_ON','CORE_PROTECTION','WINNER_REAUDIT','HEAD_LOCAL_P2','PAIR_THIRD']:
            pool=[{**t,'priority_score':1e6 if key(t) not in old else -1e6} for t in shadow['arms'][name]['tickets']]
            pools['FROZEN_'+name]=(pool,None,{})
        if shadow.get('conditional_rank_portfolio'):
            pools['FROZEN_OCT18_EQUAL_EXPOSURE']=([{**t,'priority_score':-i} for i,t in enumerate(shadow['conditional_rank_portfolio']['tickets'])],None,{})
    return prediction,pools


def krs_metrics(final,official):
    valid=orders(official);utility=final['krs_prediction_utility'];roles=final['static_prediction']['roles']
    target={role:{r[i] for r in valid} for i,role in enumerate(ROLES)}
    props=utility.get('actionable_role_proposals') or []
    additions={role:{str(p['horse_no']) for p in props if p['proposal']=='ADD_'+role+'_SHADOW'} for role in ROLES}
    pairs={(str(p['head']),str(p['second'])) for p in utility.get('actionable_ordered_pair_proposals') or []}
    exacts={(str(p['head']),str(p['second']),str(p['third'])) for p in utility.get('actionable_pair_third_proposals') or []}
    baseline={r:any(r in roles.get(h,[]) for h in target[r]) for r in ROLES}
    return {'baseline_role_capture':baseline,
        'classification':'DEAD_HEAT_MULTIPLE_VALID_ORDERS' if len(valid)>1 else 'SINGLE_VALID_ORDER',
        'by_valid_order':[{'order':list(r),'incremental_utility':evaluate_against_result(utility,list(map(int,r)),
            static_ranking=final['static_prediction']['ranking'])} for r in valid],
        'unique_role_rescue':{r:not baseline[r] and bool(target[r]&additions[r]) for r in ROLES},
        'role_proposals':sum(map(len,additions.values())),
        'false_role_proposals':sum(len(additions[r]-target[r]) for r in ROLES),
        'false_role_additions':{r:sorted(additions[r]-target[r],key=int) for r in ROLES},
        'ordered_pair_rescue':bool(pairs&{r[:2] for r in valid}),
        'exact_rescue':bool(exacts&set(valid)),
        'false_pair_proposals':len(pairs-{r[:2] for r in valid}),
        'false_exact_proposals':len(exacts-set(valid)),
        'proposal_has_purchase_authority':False}


def economic_metrics(rows,races,arm=None):
    m=cash_metrics(rows)
    settlements=[r['evaluations'][arm]['comparison']['candidate'] if arm else r['baseline']
                 for r in races if arm is None or arm in r['evaluations']]
    portfolios=[r['evaluations'][arm]['portfolio'] if arm else {'tickets':r['baseline_frozen_tickets']}
                for r in races if arm is None or arm in r['evaluations']]
    points=sum(len(p['tickets']) for p in portfolios)
    positive=sorted((r['return']+r.get('refund',0)-r['investment'] for r in rows
                     if r['return']+r.get('refund',0)>r['investment']),reverse=True)
    total_positive=sum(positive)
    m.update(total_points=points,winning_ticket_rows=sum(len(s['winning_tickets']) for s in settlements),
        ticket_hit_coverage=(sum(len(s['winning_tickets']) for s in settlements)/points if points else None),
        profit_dependency={f'top{n}':sum(positive[:n])/total_positive if total_positive else None for n in (1,2)},
        scenario_exposure='UNKNOWN_NO_DISJOINT_FROZEN_SCENARIO_BUDGET_MAP; ordered head/pair exposure is reported separately')
    return m


def compare(data_root,*,day='20261025',venues=('TKY','KYO','NGT'),official_labels=None,
            settlement_fn=settle_final,shadow_root=None):
    data_root=Path(data_root);shadow_root=Path(shadow_root or data_root);official_labels=official_labels or {}
    if len(set(venues))!=len(venues):raise ValueError('RESEARCH_DUPLICATE_VENUE')
    races=[];coverage=[];baseline=[];formal_known=[];arms=defaultdict(list);roles=defaultdict(list)
    hashes={};nominal_investment=0;missing_formal=[]
    for venue in venues:
        for no in range(1,13):
            rid=f'KM-JRA-{venue}-{day}-R{no:02d}';fp=data_root/'runtime/final_artifacts'/(rid+'.json')
            if not fp.exists():
                tp=data_root/'runtime/jra_no_bet_terminals'/(rid+'-LIVE-R1.json')
                state='AKI_NO_BET' if tp.exists() else 'NO_FINAL_UNEVALUABLE'
                coverage.append({'race_id':rid,'state':state,'investment':0,'pfs':None,
                    'opportunity_cost':'UNKNOWN_NO_FROZEN_PRODUCTION_TICKETS','prediction_invented':False})
                continue
            qp=data_root/'runtime/requests'/(rid+'-LIVE-R1-FORMAL.json')
            f=json.loads(fp.read_text());q=json.loads(qp.read_text());verify_final(f)
            if (q['race_id']!=rid or f['race_id']!=rid or q['source_snapshot_sha256']!=f['source_snapshot_sha256']
                    or q['prediction_cutoff']!=f['prediction_cutoff']):raise ValueError('RESEARCH_ORIGINAL_BINDING:'+rid)
            nominal_investment+=f['final_ticket']['total_investment']
            rp=data_root/'runtime/results'/(rid+'.json');stored=json.loads(rp.read_text()) if rp.exists() else None
            if stored and stored['frozen_prediction_ref']['immutable_final_sha256']!=f['sha256']:
                raise ValueError('RESEARCH_RESULT_BINDING:'+rid)
            if stored and rid in official_labels and digest(stored['official_result'])!=digest(official_labels[rid]):
                raise ValueError('RESEARCH_CANONICAL_RESULT_OVERRIDE_FORBIDDEN:'+rid)
            if not stored:missing_formal.append(rid)
            official=(stored or {}).get('official_result') or official_labels.get(rid)
            if official is None:
                coverage.append({'race_id':rid,'state':'FROZEN_FINAL_RESULT_PENDING','investment':f['final_ticket']['total_investment'],'pfs':None})
                continue
            old=digest((q,f,stored,official));sp=shadow_root/'runtime/role_rescue_shadow'/(rid+'.json')
            shadow=json.loads(sp.read_text()) if sp.exists() else None
            prediction,pools=portfolio_pools(q,f,shadow)
            # Every portfolio is constructed before official labels are used.
            portfolios={name:matched_exposure(f,q,pool,candidate_id='JRA-FIXED-COMPARISON-'+name,metadata=metadata,**options)
                        for name,(pool,metadata,options) in pools.items()}
            settled=settlement_fn(f,official)
            if stored:
                if any(settled[k]!=stored['settlement'][k] for k in ('total_investment','total_payout','profit_loss')):
                    raise ValueError('RESEARCH_ORIGINAL_SETTLEMENT_DIVERGED:'+rid)
                formal_known.append(cash(rid,f,settled))
            baseline.append(cash(rid,f,settled));evaluations={}
            for name,portfolio in portfolios.items():
                ev=evaluate_portfolio(f,portfolio,official,settlement_fn=settlement_fn)
                evaluations[name]={'portfolio':portfolio,'comparison':ev,'concentration':concentration(portfolio['tickets'])}
                arms[name].append(cash(rid,f,ev['candidate']))
                if name in prediction['arms']:
                    role=role_score(prediction['arms'][name],f,official);roles[name].append(role);evaluations[name]['role']=role
            if digest((q,f,stored,official))!=old:raise ValueError('RESEARCH_ORIGINAL_MUTATED:'+rid)
            for p in [fp,qp]+([rp] if stored else []):hashes[str(p.relative_to(data_root))]=hashlib.sha256(p.read_bytes()).hexdigest()
            if shadow:hashes[str(sp.relative_to(shadow_root))]=hashlib.sha256(sp.read_bytes()).hexdigest()
            state='PAPER' if f['capital_policy_decision'].get('paper_only') else 'FORMAL_FINAL'
            coverage.append({'race_id':rid,'state':state,'investment':settled['total_investment'],'return':settled['total_payout'],'pfs':settled['pfs'],
                'label_status':'CANONICAL_RESULT_REQUEST_SIGNATURE_NOT_REVERIFIED' if stored else 'UNSIGNED_OFFICIAL_LABEL_RESEARCH_ONLY','production_closed_loop_completed':False})
            races.append({'race_id':rid,'kind':state,'runner_count':len(q['runners']),'baseline':settled,'baseline_concentration':concentration(f['final_ticket']['tickets']),
                'baseline_frozen_tickets':deepcopy(f['final_ticket']['tickets']),
                'krs':krs_metrics(f,official),'official_valid_orders':[list(r) for r in orders(official)],'formal_result_request_present':bool(stored),
                'final_sha256':f['sha256'],'source_sha256':q['source_snapshot_sha256'],'evaluations':evaluations})
    def grouped(rows):return {v:cash_metrics([r for r in rows if r['venue']==v]) for v in venues}
    metrics={name:{'cash':economic_metrics(values,races,name),'by_venue':grouped(values),'roles':summary(roles[name]) if roles[name] else None,
        'roles_formal_only':summary([r['evaluations'][name]['role'] for r in races
            if r['kind']=='FORMAL_FINAL' and name in r['evaluations'] and 'role' in r['evaluations'][name]])
            if any(r['kind']=='FORMAL_FINAL' and name in r['evaluations'] and 'role' in r['evaluations'][name] for r in races) else None,
        'unique_ticket_rescue':sum(r['evaluations'][name]['comparison']['unique_ticket_rescue'] for r in races if name in r['evaluations']),
        'unique_ticket_harm':sum(r['evaluations'][name]['comparison']['unique_ticket_harm'] for r in races if name in r['evaluations']),
        'false_positive_redeployed_stake':sum(r['evaluations'][name]['comparison']['false_positive_redeployed_stake'] for r in races if name in r['evaluations']),
        'same_budget_and_points_per_race':True,
        'positive_controls':{r['race_id']:{'return_delta':r['evaluations'][name]['comparison']['net_return_delta'],'lost_hit':r['evaluations'][name]['comparison']['unique_ticket_harm']}
            for r in races if r['race_id'] in {'KM-JRA-TKY-20261025-R02','KM-JRA-KYO-20261025-R07','KM-JRA-KYO-20261025-R08'} and name in r['evaluations']}}
        for name,values in arms.items()}
    for record in metrics.values():
        record['research_disposition']='HOLD_POSITIVE_CONTROL_RETURN_HARM' if any(
            p['return_delta']<0 for p in record['positive_controls'].values()) else 'FORWARD_OOS_PENDING_NO_PROMOTION'
    baseline_metrics=economic_metrics(baseline,races)
    frontier=[]
    for name,record in metrics.items():
        point=(record['cash']['return'],record['cash']['winning_ticket_rows'],-record['cash']['maximum_drawdown'])
        dominates=lambda other: all(a>=b for a,b in zip(other,point)) and any(a>b for a,b in zip(other,point))
        if not any(dominates((r['cash']['return'],r['cash']['winning_ticket_rows'],-r['cash']['maximum_drawdown']))
                   for n,r in metrics.items() if n!=name):frontier.append(name)
    result={'profile':'KM-JRA-EXISTING-CANDIDATE-FAMILY-COMPARISON-20261025-R1','classification':'POST_RESULT_EXPLORATION_NOT_FORWARD_OOS',
        'observed_at':datetime.now(timezone.utc).isoformat(),'baseline_main':'ae0a8de00bf4709cf8c6e5445a59515174348e10',
        'denominator_races':12*len(venues),'coverage':coverage,'evaluated_finals':len(races),'runner_observations':sum(r['runner_count'] for r in races),
        'formal_series':{'status':'INCOMPLETE_MISSING_CANONICAL_RESULT_REQUEST' if missing_formal else 'CANONICAL_STORED_REQUEST_REPLAY',
            'result_signature_verification':'NOT_PERFORMED_BY_COMPARISON; closed-loop acceptance is separate',
            'unprocessed_races':missing_formal,'full_population_pfs':None if missing_formal else baseline_metrics['pfs'],
            'nominal_frozen_investment':nominal_investment,'known_result_subset':cash_metrics(formal_known)},
        'baseline_offline_research':{'all':baseline_metrics,'by_venue':grouped(baseline),'not_a_new_signed_result':True},
        'candidate_metrics':metrics,'input_raw_sha256':hashes,'races':races,
        'baseline_role_capture':{kind:{v:{'races':len([r for r in races if r['kind']==kind and r['race_id'].split('-')[2]==v]),
            'capture':{role:sum(r['krs']['baseline_role_capture'][role] for r in races if r['kind']==kind and r['race_id'].split('-')[2]==v) for role in ROLES}}
            for v in venues} for kind in ('FORMAL_FINAL','PAPER')},
        'pfs_coverage_frontier':{'arms':frontier,'axes':['return','winning_ticket_rows','negative_maximum_drawdown'],
            'same_budget_only':True,'post_result_diagnostic_only_not_candidate_selection':True},
        'dependency_raw_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in (
            'research/jra_20261024_prediction/candidates.py','research/jra_20261024_capital/comparison.py',
            'scripts/jra_20261024_capital_compare.py')},
        'matched_comparison_count':sum(len(r['evaluations']) for r in races),
        'candidate_models_or_policies_added':0,'production_changes':0,'new_signatures':0,'runtime_posts':0,'actual_purchase':'UNVERIFIED','forward_oos_increment':0,
        'limitations':['Missing FINAL is unevaluable, never 0% recommendation PFS','PAPER receives zero research budget',
            'Canonical RESULT request presence is not an independently verified RESULT signature',
            'Unsigned tie labels only complete offline research, not Production RESULT/Learning','No EV/Kelly or capital turnover without calibrated probability/initial bankroll',
            'Exploratory comparison does not select a future winning arm or grant promotion']}
    result['sha256']=digest(result);return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--data-root',type=Path,required=True);p.add_argument('--shadow-root',type=Path)
    p.add_argument('--day',default='20261025');p.add_argument('--venues',default='TKY,KYO,NGT');p.add_argument('--official-labels',type=Path)
    p.add_argument('--settlement-code',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    fn=settle_final;settlement_dependencies={}
    if a.settlement_code:
        # A supplied repair must not silently import the baseline cached helper.
        helper=a.settlement_code.parent/'jra_candidate_postresult_closedloop.py'
        for path,name in [(helper,'jra_candidate_postresult_closedloop'),(a.settlement_code,'explicit_research_settlement')]:
            settlement_dependencies[str(path.resolve())]=hashlib.sha256(path.read_bytes()).hexdigest()
            spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
            sys.modules[name]=module;spec.loader.exec_module(module)
        fn=module.settle_final
    labels=json.loads(a.official_labels.read_text()) if a.official_labels else {}
    r=compare(a.data_root,day=a.day,venues=tuple(a.venues.split(',')),official_labels=labels,settlement_fn=fn,shadow_root=a.shadow_root)
    if any(hashlib.sha256(Path(path).read_bytes()).hexdigest()!=sha for path,sha in settlement_dependencies.items()):
        raise ValueError('EXPLICIT_SETTLEMENT_CODE_CHANGED_DURING_COMPARISON')
    r['settlement_dependency_raw_sha256']=settlement_dependencies
    if a.official_labels:r['offline_official_labels_file_sha256']=hashlib.sha256(a.official_labels.read_bytes()).hexdigest()
    r['comparison_code_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();r['sha256']=digest({k:v for k,v in r.items() if k!='sha256'})
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_bytes(gzip.compress(json.dumps(r,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode(),mtime=0))
    short={k:v for k,v in r.items() if k!='races'};a.output.with_name('summary.json').write_text(json.dumps(short,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'finals':r['evaluated_finals'],'comparisons':r['matched_comparison_count'],'formal_status':r['formal_series']['status'],
        'research_pfs':{k:v['pfs'] for k,v in r['baseline_offline_research']['by_venue'].items()},'sha256':r['sha256']}))


if __name__=='__main__':main()

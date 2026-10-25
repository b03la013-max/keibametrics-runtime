"""Apply existing PR332 candidates to all nine saved Kyoto FINALs, offline.

No refit, new thresholds, simulation calls, result-dependent ticket selection,
or OOS credit. PAPER remains zero exposure; its internal plan is diagnostic.
"""
import argparse
from collections import defaultdict
import copy
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'runtime'),str(ROOT/'research/jra_20261024_prediction')]
from candidates import predict,digest,ROLES
from replay import load_race,role_evaluation,summary
from input_audit import race_input_audit
from research.jra_20261024_capital.comparison import matched_exposure,evaluate_portfolio,cash_metrics
from jra_production_postresult import settle_final


def cash(rid,final,settlement):
    return {'race_id':rid,'post_at':final['scheduled_post_at'],
        'investment':settlement['total_investment'],'return':settlement['total_payout'],
        'refund':settlement.get('refund',0),
        'effective_investment':settlement.get('effective_investment',settlement['total_investment'])}


def compare(data_root):
    races=[];baseline=[];arm_cash=defaultdict(list);role_scores=defaultdict(list)
    coverage=[];input_hashes={};input_audits=[]
    for no in range(1,13):
        rid=f'KM-JRA-KYO-20261025-R{no:02d}'
        fp=data_root/'runtime/final_artifacts'/(rid+'.json')
        if not fp.exists():
            terminal=data_root/'runtime/jra_no_bet_terminals'/(rid+'-LIVE-R1.json')
            if terminal.exists():
                t=json.loads(terminal.read_text())
                if t['sha256']!=digest({k:v for k,v in t.items() if k!='sha256'}):
                    raise ValueError('KYOTO_TERMINAL_HASH:'+rid)
                coverage.append({'race_id':rid,'state':'AKI_NO_BET','pfs':None,
                    'decision_reason':t['decision_reason'],'terminal_sha256':t['sha256']})
            else:
                coverage.append({'race_id':rid,'state':'NO_FINAL_UNEVALUABLE','pfs':None,
                    'prediction_not_invented':True})
            continue
        row=load_race(data_root,rid);q,f,r=row['q'],row['f'],row['result']
        raw_before=digest((q,f,r))
        # Predictions accept only the frozen request/FINAL. Labels enter only
        # role_evaluation and settlement below, after all arm rankings exist.
        projection=predict(q,f)
        input_audits.append(race_input_audit(q,f,projection,row['baseline_roles']))
        frozen=settle_final(f,r['official_result'])
        if any(frozen[k]!=r['settlement'][k] for k in ('total_investment','total_payout','profit_loss')):
            raise ValueError('KYOTO_ORIGINAL_SETTLEMENT_MISMATCH:'+rid)
        baseline.append(cash(rid,f,frozen));evaluations={}
        for name,arm in projection['arms'].items():
            role=role_evaluation(arm,row);role_scores[name].append(role)
            portfolio=matched_exposure(f,q,arm['ticket_candidates'],candidate_id=arm['metadata']['candidate_id'],metadata=arm['metadata'])
            evaluation=evaluate_portfolio(f,portfolio,row['official'],settlement_fn=settle_final)
            if evaluation['candidate']['total_investment']!=frozen['total_investment']:
                raise ValueError('KYOTO_BUDGET_CHANGED:'+rid+':'+name)
            arm_cash[name].append(cash(rid,f,evaluation['candidate']))
            evaluations[name]={'role':role,'portfolio':portfolio,'comparison':evaluation}
        if digest((q,f,r))!=raw_before:
            raise ValueError('KYOTO_ORIGINAL_MUTATED:'+rid)
        for relative in (row['provenance']['request_path'],
                         'runtime/final_artifacts/'+rid+'.json','runtime/results/'+rid+'.json'):
            input_hashes[relative]=hashlib.sha256((data_root/relative).read_bytes()).hexdigest()
        coverage.append({'race_id':rid,'state':row['kind'],'pfs':frozen['pfs'],
            'investment':frozen['total_investment'],'return':frozen['total_payout']})
        races.append({'race_id':rid,'kind':row['kind'],'runner_count':len(q['runners']),
            'official_top3':row['top3'],'baseline':frozen,
            'baseline_role_capture':{role:role in row['baseline_roles'].get(h,[])
                                     for role,h in zip(ROLES,row['top3'])},
            'input_provenance':row['provenance'],'evaluations':evaluations})
    result={'profile':'KM-JRA-KYOTO-20261025-EXISTING-CANDIDATE-COMPARISON-v1',
        'classification':'POST_RESULT_EXPLORATION_NOT_FORWARD_OOS',
        'production_effect':'NONE','genuine_forward_oos_credit':0,
        'refitted_models':0,'external_krs_calls':0,'new_policy_weights':0,
        'comparison_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'candidate_code_raw_sha256':{path:hashlib.sha256((ROOT/path).read_bytes()).hexdigest() for path in (
            'research/jra_20261024_prediction/candidates.py',
            'research/jra_20261024_capital/comparison.py',
            'research/jra_20261024_prediction/replay.py')},
        'purchase_authority':False,'automatic_promotion':False,
        'production_change_recommended':False,
        'denominator_races':12,'coverage':coverage,'evaluated_finals':len(races),
        'runner_observations':sum(r['runner_count'] for r in races),
        'baseline_metrics':cash_metrics(baseline),
        'candidate_metrics':{name:{'cash':cash_metrics(rows),'roles':summary(role_scores[name]),
            'new_ticket_rescues':sum(r['evaluations'][name]['comparison']['unique_ticket_rescue'] for r in races),
            'lost_baseline_hits':sum(r['evaluations'][name]['comparison']['unique_ticket_harm'] for r in races),
            'false_positive_redeployed_stake':sum(r['evaluations'][name]['comparison']['false_positive_redeployed_stake'] for r in races)}
            for name,rows in arm_cash.items()},
        'positive_controls':['KM-JRA-KYO-20261025-R07','KM-JRA-KYO-20261025-R08'],
        'input_raw_sha256':input_hashes,'frozen_input_audits':input_audits,'races':races,
        'limits':['No new observation for absent workout load/paired-response data',
                  'No causal Kyoto downhill or long-distance mechanism inferred',
                  'No reproduction of missing Kyoto3 pre-race prediction',
                  'No admission to fixed ENV 30-race cohort or PR332 prospective cohort']}
    result['sha256']=digest(result)
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--data-root',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();report=compare(args.data_root)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_bytes(gzip.compress(json.dumps(report,ensure_ascii=False,sort_keys=True,
        separators=(',',':'),allow_nan=False).encode(),mtime=0))
    short={k:v for k,v in report.items() if k not in ('races','frozen_input_audits','sha256')}
    short['full_report_sha256']=report['sha256'];short['sha256']=digest(short)
    args.output.with_name('summary.json').write_text(json.dumps(short,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'finals':report['evaluated_finals'],'runners':report['runner_observations'],
        'baseline':report['baseline_metrics'],'arms':{name:x['cash']['pfs'] for name,x in report['candidate_metrics'].items()},
        'sha256':report['sha256']},ensure_ascii=False))


if __name__=='__main__':
    main()

"""Blocked-date historical evaluation; never labels newly fitted rules as OOS."""
import argparse, collections, json, math, pathlib, statistics, sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[2]/'runtime'))
from selector import calibrate, select, hit, risk_coupled_select
from build_ledger import ROOT, build, read

def summary(records):
    n=len(records);points=[x['points'] for x in records]
    return {'races':n,'total_points':sum(points),'mean_points':sum(points)/n if n else None,
            'median_points':statistics.median(points) if n else None,
            'min_points':min(points) if n else None,'max_points':max(points) if n else None,
            'any_hit':sum(x['any_hit'] for x in records),'top3_ticket_hit':sum(x['top3_hit'] for x in records),
            'return_yen_known_complete_payouts':sum(x['return_yen'] for x in records if x['complete_payouts']),
            'complete_payout_races':sum(x['complete_payouts'] for x in records)}

def measure(row,ts):
    h=hit(ts,row['outcome']['top3']);pay=row['outcome']['payouts'];ret=0
    for t in ts:
        if hit([t],row['outcome']['top3'])[t['bet_type']]:ret+=pay.get(t['bet_type'],0)*t.get('stake',100)/100
    return {'race_key':row['race_key'],'lane':row['lane'],'points':len(ts),'any_hit':any(h.values()),
            'top3_hit':h['TRIO'] or h['TRIFECTA'],'hits':h,'return_yen':ret,
            'complete_payouts':all(b in pay for b in {t['bet_type'] for t in ts})}

def box(rank,width):
    from itertools import combinations,permutations
    hs=rank[:width]
    return [{'bet_type':'EXACTA','selection':list(s),'stake':100} for s in permutations(hs,2)]+[{'bet_type':'TRIO','selection':sorted(s),'stake':100} for s in combinations(hs,3)]

def evaluate(ledger):
    eligible=[r for r in ledger['rows'] if r['analysis_eligible']]
    report={'status':'HISTORICAL_RESEARCH / NO_NEW_UNKNOWN_FORWARD_OOS / NO_PRODUCTION_PROMOTION',
            'rule_created_after_all_outcomes':True,'actual_purchase_status':'NOT_VERIFIED',
            'baseline':{},'score_available':{},'blocked_date_folds':[],'next_race_models':{},'r50_mechanical_replays':[]}
    for lane in sorted({r['lane'] for r in eligible}):
        rows=[r for r in eligible if r['lane']==lane]
        report['baseline'][lane]=summary([measure(r,r['tickets']) for r in rows])
        report['score_available'][lane]=sum(bool(r['frozen_scores']) for r in rows)
    candidate=[r for r in eligible if r['lane']=='JRA_CANDIDATE' and r['frozen_scores']]
    for profile in sorted({r['numerical_profile'] for r in candidate}):
        rs=[r for r in candidate if r['numerical_profile']==profile]
        for day in sorted({r['date'] for r in rs}):
            train=[r for r in rs if r['date']<day];test=[r for r in rs if r['date']==day]
            if not train:continue
            fold={'test_day':day,'numerical_profile':profile,'train_n':len(train),'test_n':len(test),
                  'classification':'DATE_BLOCKED_HISTORICAL_HOLDOUT / RESEARCH_DESIGN_AFTER_RESULTS','arms':{}}
            for name,func in [('FROZEN_BASELINE',lambda r:r['tickets']),('FIXED_TOP3',lambda r:box(r['ranking'],3)),('FIXED_TOP6',lambda r:box(r['ranking'],6))]:
                records=[measure(r,func(r)) for r in test];fold['arms'][name]={'summary':summary(records),'races':records}
            for target in [.8,.9,.95]:
                model=calibrate(train,target)
                if model['q'] is None:fold['arms'][f'ADAPTIVE_{target}']={'status':'INSUFFICIENT_CALIBRATION','model':model};continue
                records=[]
                for row in test:
                    s=select(row['frozen_scores'],model,lane=row['lane'],numerical_profile=profile,race_date=day)
                    records.append({**measure(row,s['tickets']),'column_widths':{c:len(v) for c,v in s['columns'].items()},'aki':s['features']['aki'], 'capital_decision':s['decision']})
                old=fold['arms']['FROZEN_BASELINE']['races']
                harms=[r['race_key'] for r,b in zip(records,old) if b['any_hit'] and not r['any_hit']]
                rescues=[r['race_key'] for r,b in zip(records,old) if r['any_hit'] and not b['any_hit']]
                fold['arms'][f'ADAPTIVE_{target}']={'model':model,'summary':summary(records),'races':records,
                    'lost_baseline_hits':harms,'new_historical_hits':rescues,'promotion':'NOT_AUTHORIZED_BY_EVIDENCE'}
            report['blocked_date_folds'].append(fold)
        report['next_race_models'][profile]=calibrate(rs,.9)
    report['risk_coupled_discovery']={}
    for lane in ['JRA_PRODUCTION','JRA_CANDIDATE']:
        records=[]
        for row in eligible:
            if row['lane']!=lane or not row['frozen_scores']:continue
            s=risk_coupled_select(row['frozen_scores']);records.append({'old':measure(row,row['tickets']),
                'candidate':measure(row,s['tickets']),'column_widths':{c:len(v) for c,v in s['columns'].items()},
                'features':s['features'],'limits':s['limits'],'status':s['status']})
        report['risk_coupled_discovery'][lane]={'classification':'POSTHOC_DISCOVERY / NOT_HOLDOUT / NOT_OOS',
            'baseline':summary([x['old'] for x in records]),'candidate':summary([x['candidate'] for x in records]),
            'lost_baseline_hits':[x['old']['race_key'] for x in records if x['old']['any_hit'] and not x['candidate']['any_hit']],
            'new_historical_hits':[x['old']['race_key'] for x in records if not x['old']['any_hit'] and x['candidate']['any_hit']],
            'races':records,'production_promotion':False}
    # R50 is an enacted mechanical comparator, not a calibrated model.
    from jra_aki_v21 import apply_authorized_v21
    from minimum_efficient_coverage import build_mec_plan
    authority=read(ROOT/'profiles/KM_FAMILY_CURRENT_AUTHORITY_20261011_R50.json')
    for row in eligible:
        if row['lane']!='JRA_PRODUCTION' or not row['frozen_scores']:continue
        request=read(ROOT/row['feature_path']);source={**request['source_snapshot'],'source_snapshot_sha256':request['source_snapshot_sha256']}
        selected=apply_authorized_v21(request,source,authority,root=ROOT);mec=build_mec_plan(selected)
        report['r50_mechanical_replays'].append({'old':measure(row,row['tickets']),'r50':measure(row,mec['tickets']),
           'calculation':selected['static_prediction']['aki_jra_v21'],'selection':selected['aki_column_selection'],
           'classification':'UNSIGNED_POSTRESULT_MECHANICAL_REPLAY_NOT_OOS','information_gate':selected['aki_compiler_receipt']['information_gate']})
    return report

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--ledger',required=True);args=ap.parse_args()
    report=evaluate(read(pathlib.Path(args.ledger)));pathlib.Path(args.output).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'baseline':report['baseline'],'scores':report['score_available'],'folds':[{k:v for k,v in f.items() if k!='arms'}|{'arms':{k:v.get('summary',v.get('status')) for k,v in f['arms'].items()}} for f in report['blocked_date_folds']]},ensure_ascii=False))

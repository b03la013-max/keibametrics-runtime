"""Additional lane/bet/index comparisons from the verified day ledger; read-only inputs."""
import json,statistics,sys
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from jra_full_day_postrace_review import read,write,BASE,DERIVED

def build():
    out=ROOT/'runtime/daily_reviews/JRA-2026-10-17';ledger=read(out/'audit_ledger.json');races=ledger['races']
    alternatives=read(out/'alternative_lane_settlements.json');index=read(out/'numerical_discrimination.json')
    grouped=defaultdict(list)
    for r in alternatives:
        for t in r['tickets']:grouped[(r['lane'],t['bet_type'])].append({'race_id':r['race_id'],**t})
    bet=[]
    for (lane,kind),tickets in sorted(grouped.items()):
        inv=sum(t['investment'] for t in tickets);ret=sum(t['return'] for t in tickets)
        race_totals=defaultdict(lambda:[0,0])
        for t in tickets:race_totals[t['race_id']][0]+=t['investment'];race_totals[t['race_id']][1]+=t['return']
        bet.append({'lane':lane,'bet_type':kind,'ticket_count':len(tickets),'investment':inv,'return':ret,
            'profit_loss':ret-inv,'pfs':ret/inv*100 if inv else None,'hit_ticket_count':sum(t['hit'] for t in tickets),
            'hit_but_loss_race_count':sum(0<r<i for i,r in race_totals.values()),
            'paper_reference_is_not_executable_exposure':lane=='CANDIDATE_PAPER_REFERENCE'})
    winner=[];capital=[]
    for r in races:
        pr=r['prediction'];st=r['settlement']
        if not pr:continue
        rows=[x for x in index if x['race_id']==r['race_id']]
        winner.append({'race_id':r['race_id'],'lane':'PAPER' if r['formal_grade'].endswith('PAPER') else 'PRODUCTION',
            'static_winner_rank':pr['winner_rank'],'winner_in_W':pr['W'],
            'indices':{x['index']:{'value':x['winner_value'],'rank':x['winner_rank'],'runner_count':x['runner_count']} for x in rows},
            'interpretation':'Observed frozen per-index ranks only; low/high ranks are not a causal weight attribution, and no index is rescored.'})
        heads=Counter();unordered=0
        for t in (st or {}).get('tickets',[]):
            if t['bet_type'] in ('EXACTA','TRIFECTA'):heads[str(t['selection'][0])]+=t['investment']
            else:unordered+=t['investment']
        if st and 'investment' in st:
            assert sum(heads.values())+unordered==st['investment']
            capital.append({'race_id':r['race_id'],'lane':'PAPER' if r['formal_grade'].endswith('PAPER') else 'PRODUCTION',
                'ordered_head_investment':dict(heads),'unordered_ticket_investment':unordered,'total_investment':st['investment'],
                'return':st['return'],'hit_but_loss':st['hit_but_loss'],'pfs':st['pfs'],
                'no_arbitrary_head_assignment_to_trio':True,'dominant_causal_loss_owner':'UNDETERMINED'})
    krs={};prediction={}
    for lane in ['PRODUCTION','PAPER']:
        rows=[r for r in races if r['prediction'] and (r['formal_grade'].endswith('PAPER') if lane=='PAPER' else not r['formal_grade'].endswith('PAPER'))]
        semantic=[r for r in rows if r['krs'] and r['krs'].get('semantic_evaluation_eligible')]
        krs[lane]={'executed_races':sum(bool(r['krs']) for r in rows),'semantic_evaluable_races':len(semantic),
            'actionable_rescue_events':dict(Counter(event for r in semantic for event in r['krs']['utility'].get('rescues',[]))),
            'unique_actionable_role_rescues':sum(len(r['krs']['unique_actionable_role_rescues']) for r in semantic),
            'false_role_proposals':sum(len(r['krs']['false_positive_actionable_role_proposals']) for r in semantic),
            'production_added_ticket_count':0,'production_added_capital':0,'actual_production_harm':0}
        prediction[lane]={'race_count':len(rows),'winner_mean_rank':statistics.mean(r['prediction']['winner_rank'] for r in rows),
            'market_relative_winner_rank_gain':statistics.mean(r['prediction']['market_relative_winner_rank_gain'] for r in rows),
            'market_basis':'Same Signed SOURCE pre-cutoff official popularity; higher gain is better'}
    result={'source_snapshot':ledger['summary']['git_snapshot'],'audit_generated_at':ledger['summary']['generated_at'],
        'alternative_lane_bet_type_pfs':bet,'winner_index_review':winner,'head_capital_review':capital,
        'krs_by_lane':krs,'prediction_by_lane':prediction,'no_production_policy_change':True}
    write(out/'supplemental_metrics.json',result)
    print(json.dumps({'bet_type_lane_rows':len(bet),'winner_index_races':len(winner),'krs_by_lane':krs},ensure_ascii=False))

if __name__=='__main__':build()

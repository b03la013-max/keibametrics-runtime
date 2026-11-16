"""Integer 100-yen matched retrospective benchmarks; never changes prediction.

The experiment namespace is fixed and outcome-independent. Equal-count sampled
subsets are COUNTERFACTUAL comparison portfolios, never replacement predictions.
Full-coverage equal-budget portfolios preserve every original ticket.
"""
import hashlib
import base64
import json
from copy import deepcopy
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT / 'runtime'))
from mec_r4_shadow import settle_ticket_list
from tools.local_aki_comparison import metrics
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
NAMESPACE = 'LOCAL-AKI-MATCHED-REPLAY-20261013-R1'


def ticket_key(t):
    bt=t['bet_type'].upper(); sel=tuple(map(int,t['selection']))
    return bt, tuple(sorted(sel)) if bt == 'TRIO' else sel


def portfolio(tickets, identity, units, count=None):
    unique={}
    for t in tickets:
        k=ticket_key(t)
        if k in unique: raise ValueError('DUPLICATE_FROZEN_TICKET')
        unique[k]=deepcopy(t)
    ranked=sorted(unique.items(),key=lambda kv: hashlib.sha256(json.dumps(
        [NAMESPACE,list(identity),kv[0]],sort_keys=True).encode()).hexdigest())
    n=len(ranked) if count is None else count
    if n <= 0 or n > len(ranked) or units < n: raise ValueError('MATCHED_PORTFOLIO_NOT_FEASIBLE')
    # No results, odds, payouts, AKI or candidate scores enter this ordering.
    quotient,remainder=divmod(units,n)
    out=[]
    for i,(_,t) in enumerate(ranked[:n]):
        t['stake']=100*(quotient+(i<remainder)); out.append(t)
    return out


def compare(corpus):
    attestation=json.loads((ROOT/'evidence/local_aki_columns_20261012/destination_verification.json').read_text())
    key=Ed25519PublicKey.from_public_bytes(base64.b64decode(attestation['health']['receipt_public_key_b64']))
    def verified(e,race_id,phase):
        raw=json.dumps(e['receipt'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
        key.verify(base64.b64decode(e['signature']),raw)
        artifact_raw=json.dumps(e['artifact'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
        if (hashlib.sha256(raw).hexdigest()!=e['receipt_sha256'] or
            hashlib.sha256(artifact_raw).hexdigest()!=e['receipt']['artifact_sha256'] or
            e['receipt']['race_id']!=race_id or e['receipt']['phase']!=phase or e['receipt']['status']!='PASS'):
            raise ValueError('MATCHED_COMPARISON_SIGNED_LINEAGE_INVALID')
    unique={}
    for r in corpus['races']:
        if r.get('acceptance_only') or 'candidate_settlement' not in r: continue
        if any(r[a+'_settlement']['status'] != 'SETTLED' for a in ('candidate','production')): continue
        k=tuple(r['identity'])
        if k not in unique or r['latest']['signed_at'] > unique[k]['latest']['signed_at']: unique[k]=r
    rows=sorted(unique.values(),key=lambda r:(r['race_date'],r['venue'],r['identity'][2]))
    matched={mode:[] for mode in ('equal_budget_full_coverage','equal_budget_equal_count')}; excluded=[]
    for r in rows:
        final=json.loads((ROOT/r['latest']['path']/'final_receipt_envelope.json').read_text())
        result_envelope=json.loads((ROOT/r['result_path']).read_text())
        verified(final,r['race_id'],'FINAL');verified(result_envelope,r['race_id'],'RESULT')
        result=result_envelope['artifact']
        if result['frozen_refs']['final_receipt_sha256']!=final['receipt_sha256']:
            raise ValueError('MATCHED_COMPARISON_RESULT_FINAL_MISMATCH')
        result=deepcopy(result);result['official_result']['top3']=result['official_result']['finish_order'][:3]
        original={'candidate':r['paper_tickets'],'production':final['artifact']['final_ticket']['tickets']}
        sizes={a:len(v) for a,v in original.items()}
        if not all(sizes.values()):
            excluded.append({'identity':r['identity'],'reason':'EMPTY_ORIGINAL_PORTFOLIO','counts':sizes});continue
        for mode in matched:
            units=(max if mode=='equal_budget_full_coverage' else min)(sizes.values())
            rr={'identity':r['identity'],'venue':r['venue'],'class':r['class'],'distance':r['distance'],
                'runner_count':r['runner_count'],'race_date':r['race_date'],'budget_yen':units*100,
                'scope':'COUNTERFACTUAL_REPLAY_ONLY / NOT_PURCHASE / NOT_PREDICTION_PRUNING'}
            for arm,ts in original.items():
                portfolio_tickets=portfolio(ts,r['identity'],units,
                    count=units if mode=='equal_budget_equal_count' else None)
                rr[arm+'_tickets']=portfolio_tickets
                rr[arm+'_settlement']=settle_ticket_list(portfolio_tickets,result)
            matched[mode].append(rr)
    def summarize(rr):
        arms={a:metrics(rr,a) for a in ('candidate','production')}
        for a in arms:
            ss=[r[a+'_settlement'] for r in rr]
            losses=[max(0,-s['profit_loss']) for s in ss];gross=sum(losses)
            arms[a]['worst_five_loss_share']=sum(sorted(losses,reverse=True)[:5])/gross if gross else None
            top=sorted(ss,key=lambda s:s['return'],reverse=True)[:3]
            arms[a]['pfs_excluding_top_three_races']=((arms[a]['return']-sum(s['return'] for s in top))/
                (arms[a]['investment']-sum(s['investment'] for s in top))*100
                if arms[a]['investment']>sum(s['investment'] for s in top) else None)
            arms[a]['by_bet_type']={}
            for bt in ('EXACTA','TRIO','TRIFECTA'):
                bs=[s['by_bet_type'][bt] for s in ss];investment=sum(s['investment'] for s in bs);returned=sum(s['return'] for s in bs)
                arms[a]['by_bet_type'][bt]={'investment':investment,'return':returned,
                    'pfs':returned/investment*100 if investment else None,'ticket_count':sum(s['ticket_count'] for s in bs)}
        return arms
    report={'status':'RETROSPECTIVE_MATCHED_REPLAY / UNCALIBRATED / NOT_OOS','namespace':NAMESPACE,
        'prediction_portfolios_modified':False,'automatic_promotion':False,'unknown_future_oos_count':0,
        'outcome_independent_ordering':True,'integer_stake_unit_yen':100,'excluded':excluded,'modes':{}}
    for mode,rr in matched.items():
        report['modes'][mode]={'races':len(rr),'all':summarize(rr),'by_venue':{v:summarize([r for r in rr if r['venue']==v]) for v in sorted({r['venue'] for r in rr})},
            'by_field_size':{str(n):summarize([r for r in rr if r['runner_count']==n]) for n in sorted({r['runner_count'] for r in rr})},
            'by_class':{str(c):summarize([r for r in rr if r['class']==c]) for c in sorted({r['class'] for r in rr},key=str)},
            'by_distance':{str(d):summarize([r for r in rr if r['distance']==d]) for d in sorted({r['distance'] for r in rr},key=str)},
            'chronological_split':{p:summarize([r for r in rr if (r['race_date']<'2026-10-09')==early]) for p,early in [('before_20261009',True),('from_20261009',False)]},
            'portfolios':rr}
    return report

if __name__=='__main__':
    root=ROOT/'research/local_aki_columns_20261012'
    report=compare(json.loads((root/'corpus_audit.json').read_text()))
    (root/'matched_comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({m:x['all'] for m,x in report['modes'].items()},ensure_ascii=False))


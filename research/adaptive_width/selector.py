"""Research-only joint residual calibration and independent AKI columns.

No outcomes, payouts, or ranking targets are accepted by select(). Scores are
index scores, never probabilities. Historical calibration is not future OOS.
"""
import math
from itertools import permutations
from statistics import pstdev

BASE = {'W':.35,'P2':.8,'P3':1.2}
METRIC = {'W':'ZAI_WIN','P2':'ZAI_PLACE','P3':'T3I'}
REQUIRED = {'ZAI_WIN','ZAI_PLACE','T3I','RFI','BWI','CFI','GCI','PRI','TPI','DCR'}

def features(scores):
    if len(scores)<3 or any(not REQUIRED<=set(v) for v in scores.values()):
        raise ValueError('INCOMPLETE_FROZEN_INDICES')
    if any(isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v) or not 0<=v<=100 for r in scores.values() for v in r.values()):
        raise ValueError('INVALID_INDEX')
    scores={str(h):v for h,v in scores.items()}
    ranks={c:sorted(scores,key=lambda h:(-scores[h][k],str(h))) for c,k in METRIC.items()}
    scales={c:max(1.,pstdev([scores[h][k] for h in ranks[c][:(len(scores)+1)//2]])) for c,k in METRIC.items()}
    h=ranks['W'][0];s=next(x for x in ranks['P2'] if x!=h);t=next(x for x in ranks['P3'] if x not in {h,s})
    anchors={'W':h,'P2':s,'P3':t}
    gaps={c:{x:max(0.,(scores[anchors[c]][k]-scores[x][k])/scales[c]) for x in scores} for c,k in METRIC.items()}
    def quality(v,weights): return weights[0] if v<60 else weights[1] if v<75 else weights[2]
    axes={};sep={};density={}
    for c,k in METRIC.items():
        top=ranks[c][0];d=(scores[top][k]-scores[ranks[c][1]][k])/scales[c]
        sep[c]=40 if d<.25 else 20 if d<.75 else 0
        near=sum((scores[top][k]-scores[x][k])/scales[c]<=.5 for x in ranks[c][1:])
        density[c]=0 if near<2 else 15 if near<5 else 30
        if c=='W': extra=sum(quality(min(scores[h][k] for k in group),(10,5,0)) for group in [('RFI','BWI'),('CFI','GCI'),('PRI','TPI')])
        else:
            group=('RFI','CFI','TPI') if c=='P2' else ('RFI','CFI','F3S')
            threats=sum((scores[ranks[c][0]][k]-scores[x][k])/scales[c]<=1.5 and (scores[h]['ZAI_WIN']-scores[x]['ZAI_WIN'])/scales['W']>.5 and sum(scores[x].get(k,0)>=65 for k in group)>=2 for x in scores)
            extra=0 if threats<1 else 15 if threats<3 else 30
        axes[c]=sep[c]+density[c]+extra
    orderW={h:i for i,h in enumerate(ranks['W'])};orderP={h:i for i,h in enumerate(ranks['P3'])}
    inv=sum((orderW[a]-orderW[b])*(orderP[a]-orderP[b])<0 for i,a in enumerate(ranks['W']) for b in ranks['W'][i+1:])/(len(scores)*(len(scores)-1)/2)
    rsi=(0 if inv<.1 else 25 if inv<.3 else 50)+density['W']
    risk=sep['W']+quality(scores[h]['DCR'],(20,10,0))+quality(min(scores[h]['RFI'],scores[h]['BWI']),(15,7.5,0))+quality(min(scores[h]['CFI'],scores[h]['GCI']),(15,7.5,0))+quality(min(scores[h]['PRI'],scores[h]['TPI']),(10,5,0))
    # Directional multipliers are preregistered hypotheses, not fitted AKI weights.
    radii={c:BASE[c]*(1+axes[c]/100+(risk/200 if c=='W' else rsi/400)) for c in METRIC}
    return {'ranks':ranks,'anchors':anchors,'gaps':gaps,'radii':radii,
            'aki':axes,'axis_failure_risk':risk,'rsi':rsi,
            'external_variation':'UNOBSERVABLE','solid_correction':0,
            'information_gate':'PAPER_NO_AUTHORIZED_EXTERNAL_SERIES'}

def residual(scores,top3):
    f=features(scores)
    return max(f['gaps'][c][str(h)]/f['radii'][c] for c,h in zip(METRIC,top3))

def calibrate(rows,target=.9):
    if not 0<target<1: raise ValueError('INVALID_TARGET')
    if not rows: raise ValueError('EMPTY_CALIBRATION')
    strata={(r['lane'],r['numerical_profile']) for r in rows}
    if len(strata)!=1: raise ValueError('MIXED_LANE_OR_NUMERICAL_AUTHORITY')
    if len({r['race_key'] for r in rows})!=len(rows): raise ValueError('DUPLICATE_RACE')
    if any(not r['analysis_eligible'] or not r['frozen_scores'] for r in rows): raise ValueError('INELIGIBLE_CALIBRATION')
    values=sorted(residual(r['frozen_scores'],r['outcome']['top3']) for r in rows)
    k=math.ceil((len(rows)+1)*target-1e-12)
    q=values[k-1] if k<=len(values) else None
    lane,profile=next(iter(strata))
    return {'schema':'KM-AKI-JOINT-COVERAGE-CANDIDATE-v1','lane':lane,'numerical_profile':profile,
            'target_joint_coverage':target,'n':len(rows),'quantile_order':k,'q':q,
            'calibration_last_date':max(r['date'] for r in rows),
            'calibration_races':sorted(r['race_key'] for r in rows),
            'calibration_days':len({r['date'] for r in rows}),
            'authority':'RESEARCH_ONLY / HISTORICAL_CALIBRATION / NOT_FORWARD_VALIDATED',
            'production_change':False,'prediction_probability_claim':False}

def select(scores,model,*,lane,numerical_profile,race_date,budget=None):
    if lane!=model['lane'] or numerical_profile!=model['numerical_profile']: raise ValueError('AUTHORITY_MISMATCH')
    if race_date<=model['calibration_last_date']: raise ValueError('RESULT_LEAKAGE_DATE_BOUNDARY')
    if budget is not None and (isinstance(budget,bool) or not isinstance(budget,int) or budget<0): raise ValueError('INVALID_BUDGET')
    f=features(scores)
    if model['q'] is None: return {'status':'INSUFFICIENT_CALIBRATION','tickets':[], 'decision':'PAPER','features':f,'reason':'FINITE_SAMPLE_QUANTILE_UNAVAILABLE'}
    cols={c:[h for h in f['ranks'][c] if f['gaps'][c][h]<=model['q']*f['radii'][c]+1e-12] for c in METRIC}
    core={c:[h for h in cols[c] if f['gaps'][c][h]<=BASE[c]+1e-12] for c in METRIC}
    out={};represented=0
    def add(b,selection,reason):
        s=tuple(sorted(map(int,selection))) if b=='TRIO' else tuple(map(int,selection))
        out[(b,s)]={'bet_type':b,'selection':list(s),'stake':100,'reason':reason}
    for h in cols['W']:
        for s in cols['P2']:
            if h==s: continue
            if h in core['W'] and s in core['P2']: add('EXACTA',(h,s),'ORDERED_CORE_PAIR')
            for t in cols['P3']:
                if t in {h,s}:continue
                represented+=1
                add('TRIO',(h,s,t),'CALIBRATED_JOINT_SET_PROTECTION')
                if h in core['W'] and s in core['P2'] and t in core['P3']: add('TRIFECTA',(h,s,t),'ORDERED_CORE_THIRD')
    ts=[out[k] for k in sorted(out)];capital=100*len(ts)
    return {'status':'RESEARCH_CANDIDATE','decision':'PAPER','features':f,'columns':cols,'core_columns':core,
            'tickets':ts,'ticket_count':len(ts),'capital_yen':capital,'represented_ordered_structures':represented,
            'budget_compatible':budget is not None and capital<=budget,
            'budget_excess_action':'PAPER_KEEP_FULL_SEMANTICS','reason':'FUTURE_VALIDATION_AND_EXTERNAL_OBSERVATIONS_REQUIRED',
            'fixed_ticket_cap':None,'calibrated_probability_claim':False}

def hit(tickets,top3):
    pair=list(map(int,top3[:2]));triple=list(map(int,top3));unordered=sorted(triple)
    return {b:any(t['bet_type']==b and t['selection']==(pair if b=='EXACTA' else unordered if b=='TRIO' else triple) for t in tickets) for b in ['EXACTA','TRIFECTA','TRIO']}

def risk_coupled_select(scores,*,budget=None):
    """Discovery hypothesis: axis uncertainty propagates into place protection.

    Developed after inspecting historical failures. These constants have NOT
    been validated prospectively. Original R50 semantics and signed FINALs are
    not rewritten. Ordered core stays narrow; extensions become unordered sets.
    """
    if budget is not None and (isinstance(budget,bool) or not isinstance(budget,int) or budget<0): raise ValueError('INVALID_BUDGET')
    f=features(scores);a=f['aki'];risk=f['axis_failure_risk'];rsi=f['rsi']
    limits={'W':.35+.65*a['W']/100+.5*risk/100,
            'P2':.8+1.2*a['P2']/100+risk/100,
            'P3':1.2+.8*a['P3']/100+.5*rsi/100+2*risk/100}
    groups={'W':('RFI','CFI','PRI'),'P2':('RFI','CFI','TPI'),'P3':('RFI','CFI','F3S')}
    qualified={c:[h for h in f['ranks'][c] if scores[h][METRIC[c]]>=60 and sum(scores[h].get(k,0)>=65 for k in groups[c])>=2] for c in METRIC}
    columns={c:[h for h in qualified[c] if f['gaps'][c][h]<=limits[c]+1e-12] for c in METRIC}
    core={c:[h for h in columns[c] if f['gaps'][c][h]<=BASE[c]+1e-12] for c in METRIC}
    if (a['W']>=60 or risk>35) and len(columns['W'])<2:
        return {'status':'AXIS_EVIDENCE_INSUFFICIENT','decision':'PAPER','features':f,'columns':columns,'tickets':[],
                'ticket_count':0,'capital_yen':0,'reason':'NO_FORCED_HEAD_FILL','limits':limits}
    out={}
    def add(b,parts,reason):
        parts=tuple(sorted(map(int,parts))) if b=='TRIO' else tuple(map(int,parts))
        out[(b,parts)]={'bet_type':b,'selection':list(parts),'stake':100,'reason':reason}
    for h in columns['W']:
        for s in columns['P2']:
            if h==s:continue
            if h in core['W'] and s in core['P2']:add('EXACTA',(h,s),'ORDERED_CORE_PAIR')
            for t in columns['P3']:
                if t in {h,s}:continue
                if h in core['W'] and s in core['P2'] and t in core['P3']:
                    add('TRIFECTA',(h,s,t),'ORDERED_CORE_THIRD')
                else:add('TRIO',(h,s,t),'AXIS_COUPLED_SET_PROTECTION')
    ts=[out[k] for k in sorted(out)];capital=100*len(ts)
    return {'status':'DISCOVERY_HYPOTHESIS_AFTER_RESULTS','decision':'PAPER','features':f,'columns':columns,'core_columns':core,
            'limits':limits,'tickets':ts,'ticket_count':len(ts),'capital_yen':capital,
            'budget_compatible':budget is not None and capital<=budget,
            'budget_excess_action':'PAPER_KEEP_FULL_SEMANTICS','fixed_ticket_cap':None,
            'production_change':False,'reason':'POSTHOC_DISCOVERY_NOT_FORWARD_VALIDATED'}

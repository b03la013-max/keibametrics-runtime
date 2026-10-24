"""Outcome-blind research projections over frozen JRA inputs.

These candidates were specified after 2026-10-24 results.  Their replay is
exploration, never a historical freeze or Production/EV/purchase authority.
No Result, finish order or payout is accepted by the prediction interface.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from hashlib import sha256
from itertools import permutations
import json
import math
from pathlib import Path
import re
import statistics
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'runtime'))
from jra_conditional_rank_shadow import FEATURES, vectors, policy_sha

ROLES = ('W', 'P2', 'P3')
ROLE_INDEX = {'W': 'ZAI_WIN', 'P2': 'ZAI_PLACE', 'P3': 'T3I'}
POLICY = {
    'candidate_family': 'JRA-FACTOR-RESEARCH-20261024-R1',
    'classification': 'POST_RESULT_EXPLORATION_NOT_FORWARD_OOS',
    'new_factor_mix': .25,
    'history_half_life_days': 180.,
    'history_distance_scale_m': 400.,
    'history_prior_pseudocount': 3.,
    'history_prior_normalized_finish': .5,
    'history_surface': 'exact only; absent or different surface not evidence',
    'history_venue_weight': {'same': 1., 'different': .5},
    'history_going_weight': {'same': 1., 'different_or_unknown': .5},
    'history_class_weight': '1/(1+absolute ordinal class distance), unknown=1 with explicit missing flag',
    'history_order': 'all observed prior races, fixed exponential recency and context similarity',
    'history_concordance': '1-(finish-1)/(field_size-1), finite valid finishes only',
    'information': 'observation counts remain separate; no DCR removal; unavailable factor leaves baseline unchanged',
    'dedup': 'each unique observed feature once, category score mean; diagnostic shared dependency is not automatically a bug',
    'pair_conditioning': 'head exclusion/P2 and pair exclusion/P3 except existing frozen head-P2 interaction control',
    'bvi_ablation': 'in-memory Base13 BVI scalar 50 through existing registered derived calculator; DCR unchanged',
    'krs': 'reuse frozen SSR-W/SSR-P2/SSR-T3 and archived worlds; no simulation/physics/seed change',
    'numeric_tie_break': True,
    'production_effect': 'NONE',
    'purchase_authority': False,
    'ev_kelly_authority': False,
    'automatic_promotion': False,
    'minimum_forward_distinct_races': 60,
    'minimum_forward_days': 3,
    'minimum_forward_venues': 2,
}

ABILITY_FEATURES = {
    'W': ('recent_performance','same_distance_fit','distance_fit','same_course_fit','class_performance','position_quality','pace_resilience','closing_quality'),
    'P2': ('recent_consistency','surface_fit','going_fit','distance_fit','pace_resilience','closing_quality'),
    'P3': ('recent_consistency','surface_fit','going_fit','closing_quality','position_quality'),
}

def digest(value):
    return sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def instant(value):
    t=datetime.fromisoformat(value.replace('Z','+00:00'))
    if t.tzinfo is None: raise ValueError('RESEARCH_TIMEZONE_REQUIRED')
    return t

def zscores(values):
    if not values:return {}
    mean=statistics.mean(values.values());scale=max(1.,statistics.pstdev(values.values()))
    return {h:(v-mean)/scale for h,v in values.items()}

def order(values):
    return sorted(values,key=lambda h:(-values[h],int(h)))

def class_ordinal(name):
    s=unicodedata.normalize('NFKC',str(name or ''))
    for pat,value in [(r'G\s*(?:1|I)(?![I\d])',6),(r'G\s*(?:2|II)(?![I\d])',5),(r'G\s*(?:3|III)(?![I\d])',4),(r'3勝|1600万',3),(r'2勝|1000万',2),(r'1勝|500万',1),(r'未勝利|新馬',0),(r'オープン|OPEN|OP\b|リステッド|\bL\b',3.5)]:
        if re.search(pat,s,re.I):return value
    return None

def valid_feature(item, scale):
    return (isinstance(item,dict) and item.get('result_derived') is False and bool(item.get('evidence_refs'))
            and item.get('source_authority')=='JRA_OFFICIAL' and item.get('category') in scale
            and item.get('production_authority') is not False)

def history_measure(request, runner):
    source=request['source_snapshot'];context=source.get('jra_race_context') or request.get('race') or {}
    runner_id=str(runner['runner_id']);record=(source.get('jra_official_horse_history',{}).get('runners') or {}).get(runner_id,{})
    target_day=instant(source['source_freeze_at']).date();surface=context.get('surface');distance=context.get('distance_m') or context.get('distance');venue=context.get('venue_name') or context.get('venue')
    target_class=class_ordinal(context.get('race_class') or context.get('raw_race_context') or context.get('race_name'))
    admitted=[];excluded=[]
    if record.get('official') is not True:return {'value':None,'observations':0,'status':'OFFICIAL_HISTORY_UNAVAILABLE','runs':[]}
    for run in record.get('runs') or []:
        reason=None
        try:day=datetime.fromisoformat(str(run['date'])).date();finish=int(run['finish']);field=int(run['field_size']);dist=int(run['distance_m'])
        except (KeyError,ValueError,TypeError):reason='MISSING_FINISH_FIELD_OR_DISTANCE'
        if reason is None and day>=target_day:reason='CURRENT_OR_FUTURE_DAY_RUN_NOT_TIME_PROVEN'
        if reason is None and not (1<=finish<=field and field>=2 and dist>0):reason='NOT_NUMERIC_FINISH'
        if reason is None and (not surface or run.get('surface')!=surface):reason='DIFFERENT_OR_UNKNOWN_SURFACE'
        if reason:
            excluded.append({'date':run.get('date'),'reason':reason});continue
        recency=2**(-(target_day-day).days/POLICY['history_half_life_days'])
        distance_weight=math.exp(-abs(dist-distance)/POLICY['history_distance_scale_m']) if type(distance) in (int,float) else 1.
        venue_weight=1. if run.get('venue')==venue else .5
        going_weight=1. if run.get('going')==context.get('going') and context.get('going') else .5
        grade=class_ordinal(run.get('race_name'));class_weight=1/(1+abs(grade-target_class)) if grade is not None and target_class is not None else 1.
        weight=recency*distance_weight*venue_weight*going_weight*class_weight
        value=1-(finish-1)/(field-1)
        admitted.append({'date':run['date'],'race_name':run.get('race_name'),'normalized_finish':value,'weight':weight,'class_known':grade is not None,'same_venue':run.get('venue')==venue,'same_distance':dist==distance,'same_going':run.get('going')==context.get('going')})
    mass=sum(r['weight'] for r in admitted);prior=POLICY['history_prior_pseudocount']
    value=100*(sum(r['weight']*r['normalized_finish'] for r in admitted)+prior*.5)/(mass+prior) if admitted else None
    return {'value':value,'observations':len(admitted),'effective_weight':mass,'target_class_known':target_class is not None,'status':'OBSERVED_CONTEXT_SHRUNK' if admitted else 'NO_ADMISSIBLE_PRIOR_RUN','runs':admitted,'excluded':excluded}

def factor_scores(request, raw_baseline):
    scale=json.loads((ROOT/'mapping/jra_base_index_evidence_mapping_v1.0_20260921.json').read_text())['category_scale']
    diagnostics={};history={};ability={r:{} for r in ROLES};dedup={};duplicate_counts={}
    for runner in request['runners']:
        h=str(runner['runner_id']);features=runner.get('evidence_features') or {};hist=history_measure(request,runner);history[h]=hist['value']
        observed={k:scale[v['category']] for k,v in features.items() if valid_feature(v,scale)}
        role_obs={}
        for role in ROLES:
            vals=[observed[k] for k in ABILITY_FEATURES[role] if k in observed];n=len(vals)
            ability[role][h]=50+(statistics.mean(vals)-50)*n/(n+3) if vals else None
            role_obs[role]=n
        dedup[h]=statistics.mean(observed.values()) if observed else None
        uses={}
        for index,cell in runner['canonical_components'].items():
            for item in cell.get('components') or []:
                uses.setdefault(item.get('feature'),set()).add(index)
        duplicates={k:sorted(v) for k,v in uses.items() if k and len(v)>1};duplicate_counts[h]=len(duplicates)
        diagnostics[h]={'history':hist,'observed_feature_count':len(observed),'role_observation_counts':role_obs,'information_does_not_equal_ability':True,'cfi':runner['canonical_components']['CFI']['value'],'jti':runner['canonical_components']['JTI']['value'],'dcr':runner['canonical_components']['DCR']['value'],'duplicate_feature_indices':duplicates,'dedup_score':dedup[h]}
    def mix(factors):
        out={}
        for role in ROLES:
            observed={h:v for h,v in factors[role].items() if v is not None};zs=zscores(observed)
            out[role]={h:raw_baseline[role][h] if h not in zs else (1-POLICY['new_factor_mix'])*raw_baseline[role][h]+POLICY['new_factor_mix']*zs[h] for h in raw_baseline[role]}
        return out
    return {'CONTEXT_HISTORY':mix({r:history for r in ROLES}),'OBSERVED_ABILITY':mix(ability),'UNIQUE_EVIDENCE':mix({r:dedup for r in ROLES})},diagnostics

def research_rank(scores,request,arm_id,*,head_local=None,pair_third=None,ticket_scores=None):
    rankings={r:order(scores[r]) for r in ROLES};universe=set(rankings['W'])
    head_local=head_local or {h:[s for s in rankings['P2'] if s!=h] for h in universe}
    pair_third=pair_third or {h+'>'+s:[t for t in rankings['P3'] if t not in (h,s)] for h in universe for s in universe if s!=h}
    candidates=[];trio={}
    for wr,h in enumerate(rankings['W'],1):
        for sr,s in enumerate(head_local[h],1):
            value=ticket_scores['EXACTA'][h+'>'+s] if ticket_scores else -float(wr+sr)
            candidates.append({'bet_type':'EXACTA','selection':[int(h),int(s)],'priority_score':value})
            for tr,t in enumerate(pair_third[h+'>'+s],1):
                key=h+'>'+s+'>'+t;value=ticket_scores['TRIFECTA'][key] if ticket_scores else -float(wr+sr+tr)
                candidates.append({'bet_type':'TRIFECTA','selection':[int(h),int(s),int(t)],'priority_score':value})
                triple=tuple(sorted(map(int,(h,s,t))))
                if ticket_scores:trio[triple]=trio.get(triple,0.)+value
                else:trio[triple]=max(value,trio.get(triple,-math.inf))
    candidates += [{'bet_type':'TRIO','selection':list(t),'priority_score':v} for t,v in trio.items()]
    metadata={'candidate_id':'JRA-20261024-'+arm_id+'-R1','classification':POLICY['classification'],'designed_after_20261024_results':True,'source_sha256':request['source_snapshot_sha256'],'runner_universe_sha256':digest(sorted(universe)),'feature_input_sha256':digest(request['runners']),'prediction_cutoff':request['prediction_cutoff'],'source_freeze_at':request['source_snapshot']['source_freeze_at'],'code_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),'policy_sha256':digest(POLICY),'production_effect':'NONE','purchase_authority':False,'ev_kelly_authority':False,'genuine_forward_oos_credit':0,'minimum_forward_days':3,'minimum_forward_distinct_races':60,'minimum_forward_venues':2}
    return {'ranking':rankings,'head_local_p2':head_local,'pair_conditioned_third':pair_third,'ticket_candidates':candidates,'metadata':metadata}

def bvi_scores(request):
    from jra_index_provenance_builder import materialize_index_provenance
    ledger=deepcopy(request['index_provenance_ledger'])
    for item in ledger['runners'].values():item['base_indices']['BVI']['value']=50.
    q={'runners':[{'runner_id':str(r['runner_id'])} for r in request['runners']],'index_provenance_ledger':ledger}
    changed=materialize_index_provenance(q)['runners']
    return {role:zscores({str(r['runner_id']):r['canonical_components'][idx]['value'] for r in changed}) for role,idx in ROLE_INDEX.items()}

def predict(request,final=None):
    """No labels/payouts. All factors use only the supplied frozen pre-race view."""
    if request.get('family_id')!='JRA':raise ValueError('RESEARCH_JRA_ONLY')
    source=request['source_snapshot'];freeze=instant(source['source_freeze_at']);cutoff=instant(request['prediction_cutoff'])
    if freeze>cutoff or source.get('race_id')!=request['race_id']:raise ValueError('RESEARCH_SOURCE_TIME_OR_ID')
    if final and (final['race_id']!=request['race_id'] or final['source_snapshot_sha256']!=request['source_snapshot_sha256'] or final['prediction_cutoff']!=request['prediction_cutoff']):raise ValueError('RESEARCH_FINAL_INPUT_BINDING')
    x=vectors(request['runners'])
    original_universe=source.get('official_runner_universe',{}).get('runners')
    if original_universe is not None and {str(r['runner_id']) for r in original_universe}!=set(x):raise ValueError('RESEARCH_SOURCE_RUNNER_UNIVERSE')
    if final and set(map(str,final.get('static_prediction',{}).get('ranking',[])))!=set(x):raise ValueError('RESEARCH_FINAL_RUNNER_UNIVERSE')
    raw={role:zscores({str(r['runner_id']):r['canonical_components'][idx]['value'] for r in request['runners']}) for role,idx in ROLE_INDEX.items()}
    arms={'STATIC_INDEX':research_rank(raw,request,'STATIC-INDEX')}
    model=json.loads((ROOT/'research/jra_conditional_rank/model.json').read_text())
    if model['sha256']!=digest({k:v for k,v in model.items() if k!='sha256'}):raise ValueError('RESEARCH_EXISTING_MODEL_HASH')
    frozen={role:{h:sum(a*b for a,b in zip(v,model['coefficients'][role])) for h,v in x.items()} for role in ROLES}
    arms['FROZEN_OCT18_RANK']=research_rank(frozen,request,'FROZEN-OCT18-RANK')
    arms['FROZEN_OCT18_RANK']['metadata'].update(reference_model_sha256=model['sha256'],reference_model_created_at=model['created_at'],reference_model_policy_sha256=policy_sha(model))
    factors,diagnostics=factor_scores(request,raw)
    for name,sc in factors.items():arms[name]=research_rank(sc,request,name.replace('_','-'))
    arms['BVI_NEUTRAL_SENSITIVITY']=research_rank(bvi_scores(request),request,'BVI-NEUTRAL-SENSITIVITY')
    unavailable={}
    summary=(final or {}).get('krs_prediction_utility',{}).get('summary') or []
    if {str(r.get('horse_no')) for r in summary}==set(x):
        krs={role:zscores({str(r['horse_no']):float(r[idx]) for r in summary}) for role,idx in [('W','SSR-W'),('P2','SSR-P2'),('P3','SSR-T3')]}
        arms['FROZEN_KRS_ROLE']=research_rank(krs,request,'FROZEN-KRS-ROLE')
    else:unavailable['FROZEN_KRS_ROLE']='NO_PRODUCTION_KRS_RECEIPT_OR_COMPLETE_SAVED_SUMMARY'
    sys.path.insert(0,str(ROOT/'research/jra_conditional_rank'))
    from head_p2_shadow import predict as head_predict
    base=json.loads((ROOT/'research/jra_conditional_rank/probability_candidate.json').read_text());interaction=json.loads((ROOT/'research/jra_conditional_rank/head_p2_candidate.json').read_text())
    dist=head_predict(request['runners'],base,interaction)
    head={h:order(values) for h,values in dist['head_p2'].items()};third={key:order(values) for key,values in dist['pair_third'].items()}
    pairs={h+'>'+s:dist['marginals']['W'][h]*mass for h,values in dist['head_p2'].items() for s,mass in values.items()}
    arms['FROZEN_HEAD_P2']=research_rank(dist['marginals'],request,'FROZEN-HEAD-P2',head_local=head,pair_third=third,ticket_scores={'EXACTA':pairs,'TRIFECTA':dist['ordered_joint']})
    arms['FROZEN_HEAD_P2']['metadata'].update(reference_model_sha256=interaction['sha256'],reference_model_created_at=interaction['created_at'],calibration_status='UNVALIDATED_RESEARCH_PROBABILITIES_NO_EV_KELLY')
    return {'race_id':request['race_id'],'arms':arms,'unavailable_arms':unavailable,'all_runner_diagnostics':diagnostics,'policy_sha256':digest(POLICY),'classification':POLICY['classification']}

"""Read frozen Candidate; join independent later official SOURCE results.
Never refit, mutate a frozen artifact, or increment forward trackers.
"""
from pathlib import Path
import sys,json,hashlib,collections,re
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'runtime/local_physical')]
from nar_auxiliary_evidence import _result_rows_from_table
from local_nar_evidence_candidate import compile_candidate_evidence
from local_fullnumerical_candidate import materialize_candidate
from local_candidate_postresult import failure_axes

def load(p):return json.loads(Path(p).read_text())
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def metrics(pred,actual):
    rank=[str(x) for x in pred.get('ranking') or []];roles=pred.get('roles') or {}
    def role(r):return set(str(x) for x in pred.get(r) or []) or {str(k) for k,v in roles.items() if any(str(x).startswith(r) for x in v)}
    ranks=[rank.index(str(x))+1 if str(x) in rank else len(rank)+1 for x in actual]
    w,p2,p3=role('W'),role('P2'),role('P3')
    return {'winner_rank':ranks[0],'winner_reciprocal_rank':1/ranks[0] if str(actual[0]) in rank else 0,
            'top3_contained_count':sum(str(x) in rank[:3] for x in actual),'top3_role_contained_count':sum(str(x) in p3 for x in actual),'mean_actual_top3_rank':sum(ranks)/3,
            'W_hit':str(actual[0]) in w,'P2_hit':str(actual[1]) in p2,'P3_hit':str(actual[2]) in p3,
            'W_universe':sorted(w),'missing_actual_count':sum(str(x) not in rank for x in actual)}

def run():
    folders=[];seen=set();hash_before={};results={};component_rows=[];report=[]
    for intent in sorted((ROOT/'runtime/formal_intents').glob('*FNB-20260930*.json')):
        req=load(intent);eid=req['execution_id'];store=ROOT/'runtime/executions'/eid/'FORMAL';latest=store/'LATEST.json'
        if not latest.exists():continue
        folder=store/'runs'/load(latest)['run_id']
        if folder in seen:continue
        seen.add(folder);folders.append((req,folder))
        source=load(folder/'source_receipt_envelope.json')['artifact']
        for field,wrapped in source['normalized_evidence'].items():
            match=re.fullmatch('same_day_r(\\d+)_result_tables',field)
            if not match:continue
            rows=next((r for table in wrapped['value'] if (r:=_result_rows_from_table(table))),[])
            top=sorted(rows,key=lambda r:r['finish'])[:3]
            if len(top)!=3:continue
            no=int(match[1]);results[no]={'top3':[r['horse_no'] for r in top],'independent_later_source':str(folder/'source_receipt_envelope.json'),
                'source_snapshot_sha256':source['source_snapshot_sha256'],'official_field':field,'available_at':source['source_freeze_at']}
    for req,folder in folders:
        rid=req['race_id'];no=req['race_no'];frozen=folder/'candidate_numerical_shadow_summary.json'
        hash_before[str(frozen)]=digest(frozen)
        original=load(frozen);fin=load(folder/'final_receipt_envelope.json')['artifact'];source=load(folder/'source_receipt_envelope.json')['artifact']
        # Diagnostics re-evaluate input missingness only; scored ranking always comes from OLD frozen Candidate.
        compiled=compile_candidate_evidence(source,req);diag=materialize_candidate(compiled)
        for runner in compiled['runners']:
            for name,feature in runner['evidence_features'].items():component_rows.append({'runner':runner['runner_id'],'race_id':rid,'component':name,'missing':bool(feature.get('missing'))})
        row={'race_id':rid,'grade':'KNOWN-DEVELOPMENT','cluster':'FNB-20260930','future_oos_eligible':False,
             'frozen_candidate_sha256':hash_before[str(frozen)],'candidate_profile':original['candidate_static_prediction']['profile'],
             'missingness_saturation':{r['runner_id']:r['candidate_missingness_saturation'] for r in diag['runners']},
             'rank_displacement_neutral_heavy':{'status':'CAUSAL_ATTRIBUTION_UNIDENTIFIED','reason':'Frozen v01 includes neutral values; removing indices would construct a different hypothesis. No result-fit ablation.'}}
        if no not in results:row.update(status='HOLD_OFFICIAL_RESULT_UNAVAILABLE',failure_axes=failure_axes(['NUMERICAL_AUTHORITY_NOT_READY']));report.append(row);continue
        result=results[no];actual=result['top3'];base=req['static_prediction'];cand=original['candidate_static_prediction']
        b,c=metrics(base,actual),metrics(cand,actual);correct_w={str(actual[0])}
        added=set(c['W_universe'])-set(b['W_universe']);removed=set(b['W_universe'])-set(c['W_universe'])
        pair=any(int(x['head'])==actual[0] and int(x['second'])==actual[1] and x.get('status')!='EXCLUDE' for x in req.get('pair_dispositions') or [])
        third=any([int(x[k]) for k in ['head','second','third']]==actual and x.get('status')!='EXCLUDE' for x in req.get('third_dispositions') or [])
        tickets=(fin.get('final_ticket') or {}).get('tickets') or []
        exact=any(t['bet_type']=='TRIFECTA' and [int(x) for x in t['selection']]==actual for t in tickets)
        # Reproduce an observed failure from frozen role/order/ticket facts; do not replace pre-existing diagnosis.
        first='ROLE' if not (b['W_hit'] and b['P2_hit'] and b['P3_hit']) else 'PAIR' if not pair else 'THIRD' if not third else 'EXACT' if not exact else 'UNDIAGNOSED'
        existing=ROOT/'runtime/performance_ledger'/(rid+'.json');diagnosis=load(existing) if existing.exists() else {'first_material_failure':first}
        row.update(status='DEVELOPMENT_EVALUATED',official_result=result,actual_top3=actual,baseline=b,candidate=c,
            false_W_promotion=len(added-correct_w),false_W_demotion=len(removed&correct_w),
            pair_preservation={'baseline':pair,'candidate':None,'reason':'Candidate static artifact has no pair decision authority'},
            third_preservation={'baseline':third,'candidate':None,'reason':'Candidate static artifact does not emit frozen pair-local third disposition'},
            exact_semantic_presence={'baseline':third,'candidate':None,'candidate_status':'NOT_EMITTED; no posthoc Cartesian universe invented'},
            purchased_exact=exact,failure_axes=failure_axes(['NUMERICAL_AUTHORITY_NOT_READY'],diagnosis))
        report.append(row)
    groups=collections.defaultdict(list)
    for x in component_rows:groups[x['component']].append(x)
    component_map=[]
    for name,items in sorted(groups.items()):
        neutral=sum(x['missing'] for x in items);ratio=neutral/len(items)
        classification='UNIDENTIFIABLE_WITH_CURRENT_SOURCE' if ratio==1 else 'NEUTRAL-DOMINANT' if neutral>len(items)-neutral else 'INFORMATIVE'
        action='REMOVE/MERGE-CANDIDATE' if name in ['age_growth','transport_season','stable_combo','weight_change_reason_rate'] and ratio==1 else 'OPTIONAL-CANDIDATE' if ratio==1 else 'KEEP_FOR_VALIDATION'
        component_map.append({'component':name,'classification':classification,'action':action,'calculated':len(items)-neutral,'neutral':neutral,'missingness_ratio':ratio,'note':'INFORMATIVE describes observed content, not proven predictive increment.'})
    assert all(digest(p)==h for p,h in hash_before.items())
    out={'grade':'DEVELOPMENT; ONE DAY/VENUE CLUSTER','independent_oos_count':0,'races':report,'component_map':component_map,
         'frozen_candidate_unchanged':True,'held_count':sum(x['status']!='DEVELOPMENT_EVALUATED' for x in report),
         'limitations':['R12 official result inaccessible during reconnaissance; held, not fabricated','No existing FNB9/30 day diagnosis file in checkout; inferred role/order gaps labelled, capital cause not invented']}
    (ROOT/'research/utility/development_evaluation.json').write_text(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2))
    compact={**out,'races':[{k:v for k,v in r.items() if k!='missingness_saturation'} for r in report]}
    (ROOT/'research/utility/development_summary.json').write_text(json.dumps(compact,ensure_ascii=False,sort_keys=True,indent=2))
    print(json.dumps({'evaluated':len(report)-out['held_count'],'held':out['held_count'],'components':len(component_map),'frozen_unchanged':True}))
if __name__=='__main__':run()

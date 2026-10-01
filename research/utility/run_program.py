"""Reuse current evaluators; offline reports and explicit pre-race Capital SHADOW.
No network, purchases, Production mutation, or OOS admission side effects.
"""
from pathlib import Path
import sys,json,hashlib,datetime,copy,collections,subprocess
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'runtime'))
sys.path.insert(0,str(ROOT/'runtime/local_physical'))
from local_numerical_authority_gate import assess as production_authority
from local_nar_evidence_candidate import compile_candidate_evidence
from local_fullnumerical_candidate import materialize_candidate
from local_krs_bridge_candidate import build_candidate_prediction
from krs_prediction_utility import evaluate_against_result
from pfs_grand_review import build_report
from common_exact_continuity_oos_tracker import build_status as common_status
from mec_r4_oos_tracker import build_status as r4_status
from local_mec_r5_oos_tracker import build_status as r5_status
from local_physical.nar_auxiliary_evidence import build_same_day_bias

def load(p):return json.loads(Path(p).read_text())
def sha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def dt(x):return datetime.datetime.fromisoformat(str(x).replace('Z','+00:00'))
def capital_arms(final,budget,*,request,generated_at,scheduled_post_at):
    """Tier ablation with equal ACTUAL spend; no ranking, AKI or odds weights."""
    if dt(generated_at)>=dt(scheduled_post_at):raise ValueError('NOT_PRE_RACE')
    if isinstance(budget,bool) or not isinstance(budget,int) or budget<100 or budget%100:raise ValueError('BUDGET_UNIT_INVALID')
    art=final.get('artifact') or final
    if not request.get('race_id') or dt(request['scheduled_post_at'])!=dt(scheduled_post_at):raise ValueError('RACE_SCHEDULE_BINDING_REQUIRED')
    universe={int(x['runner_id']) for x in request.get('runners') or [] if not x.get('scratched') and not x.get('excluded')}
    if not universe:raise ValueError('RUNNER_UNIVERSE_REQUIRED')
    freeze=art.get('final_freeze_timestamp')
    if not freeze or dt(freeze)>dt(generated_at) or dt(freeze)>=dt(scheduled_post_at):raise ValueError('FINAL_NOT_PRE_RACE_FROZEN')
    tickets=copy.deepcopy((art.get('final_ticket') or {}).get('tickets') or [])
    keys=[]
    for t in tickets:
        bt=t['bet_type'];sel=[int(x) for x in t['selection']]
        if bt not in {'EXACTA','TRIO','TRIFECTA'} or len(sel)!=(2 if bt=='EXACTA' else 3) or len(sel)!=len(set(sel)):raise ValueError('INVALID_TICKET')
        if not set(sel)<=universe:raise ValueError('RUNNER_UNIVERSE_VIOLATION')
        k=(bt,tuple(sorted(sel) if bt=='TRIO' else sel))
        if k in keys:raise ValueError('DUPLICATE_TICKET')
        keys.append(k)
        if isinstance(t.get('stake'),bool) or not isinstance(t.get('stake'),int) or t['stake']<=0 or t['stake']%100:raise ValueError('INVALID_STAKE')
    arms={'PRODUCTION':{'tickets':tickets,'investment':sum(t['stake'] for t in tickets)}}
    for name,tiers in [('CONSERVATIVE',{'CORE'}),('BALANCED',{'CORE','PROTECTION'}),('WIDE',{'CORE','PROTECTION','TAIL'})]:
        subset=[copy.deepcopy(t) for t in tickets if str(t.get('mec_tier') or t.get('tier')).upper() in tiers]
        if not subset or len(subset)>budget//100 or any(str(t.get('mec_tier') or t.get('tier')).upper() not in {'CORE','PROTECTION','TAIL'} for t in tickets):
            arms[name]={'status':'HOLD_SHADOW','reason':'MISSING_TIER_OR_INSUFFICIENT_MINIMUM_BUDGET'};continue
        # Existing nominal stakes are allocation ratios, not likelihoods.
        remainder=budget//100-len(subset);den=sum(t['stake'] for t in subset)
        units=[1+(remainder*t['stake']//den) for t in subset]
        left=budget//100-sum(units)
        order=sorted(range(len(subset)),key=lambda i:(-(remainder*subset[i]['stake']%den),keys[tickets.index(subset[i])]))
        for i in order[:left]:units[i]+=1
        for t,n in zip(subset,units):t['stake']=n*100
        arms[name]={'status':'FROZEN_SHADOW','tickets':subset,'investment':sum(t['stake'] for t in subset)}
    return {'status':'PRE-RACE-CAPITAL-SHADOW','generated_at':generated_at,'scheduled_post_at':scheduled_post_at,
            'race_id':request['race_id'],'input_sha256':sha(final),'request_sha256':sha(request),'budget':budget,'arms':arms,'production_effect':'NONE',
            'production_comparable_equal_spend':arms['PRODUCTION']['investment']==budget,
            'notice':'Tier ablation, not an AKI/distribution-adaptive policy. No new ticket added.'}


def run():
    out=ROOT/'research/utility';out.mkdir(exist_ok=True)
    # Explicitly known, correlated Development cohort; outputs never enter runtime trackers.
    reg=load(ROOT/'mapping/local_evidence_feature_rule_registry_v0.1_candidate_20260923.json')
    comparisons=[];feature_rows=[];evidence=[];mec=[];current=[];errors=[];seen_runs=set()
    for intent in sorted((ROOT/'runtime/formal_intents').glob('*FNB-20260930*')):
        req=load(intent);eid=req.get('execution_id');store=ROOT/'runtime/executions'/str(eid)/'FORMAL'
        pointer=store/'LATEST.json'
        if not pointer.exists():continue
        ptr=load(pointer);rid=req['race_id']
        # Resolve same canonical latest run, never choose favorable historical revision.
        folder=store/'runs'/str(ptr.get('run_id'))
        if str(folder) in seen_runs:continue
        seen_runs.add(str(folder))
        if not folder.exists():errors.append({'race_id':rid,'reason':'LATEST_RUN_MISSING'});continue
        try:
            src=load(folder/'source_receipt_envelope.json')['artifact']
            compiled=compile_candidate_evidence(src,req)
            num=materialize_candidate(compiled);pred=build_candidate_prediction(num)
            comparisons.append({'race_id':rid,'grade':'KNOWN-CORRELATED-DEVELOPMENT','source_snapshot_sha256':src.get('source_snapshot_sha256'),
                                'source_path':str(folder/'source_receipt_envelope.json'),
                                'production_ranking':req['static_prediction']['ranking'],'candidate_ranking':pred['candidate_static_prediction']['ranking'],
                                'candidate_numerical':num['candidate_full_numerical_summary'],
                                'production_numerical':load(folder/'numerical_authority_preflight.json'),
                                'same_source':True,'oos_eligible':False,'outcome_metrics':'PENDING_VERIFIED_RESULT'} )
            for runner in compiled['runners']:
                for idx,comps in reg['common_component_sets'].items():
                    for comp in comps:
                        f=runner['evidence_features'][comp]
                        feature_rows.append({'race_id':rid,'runner_id':runner['runner_id'],'index':idx,'component':comp,
                                             'terminal':'RULED-NEUTRAL' if f.get('missing') else 'CALCULATED',
                                             'output':f['score'],'rule_id':f['rule_id'],'provenance':f['evidence_refs'],'source_fact':f['source_fact']})
                raw=runner.get('raw_candidate_evidence') or {}
                current.append({'race_id':rid,'runner_id':runner['runner_id'],'status':'SHADOW-ONLY',
                                'body_weight':{'status':'OBSERVED' if raw.get('current_body_weight') else 'MISSING','value':raw.get('current_body_weight')},
                                'training':{'status':'MISSING'},'comment':{'status':'MISSING'},'paddock':{'status':'MISSING'},
                                'history':{'status':'OBSERVED' if raw.get('starts') else 'MISSING','value':raw.get('starts')},
                                'source_snapshot_sha256':src.get('source_snapshot_sha256')})
            bias=build_same_day_bias(src)
            evidence.append({'race_id':rid,'source_snapshot_sha256':src.get('source_snapshot_sha256'),
                             'normalized_fields':list(src.get('normalized_evidence') or {}),
                             'auxiliary':src.get('auxiliary_evidence'), 'same_day_corner_measurement':bias,
                             'feature_missing_counts':dict(collections.Counter(x['component'] for x in feature_rows if x['race_id']==rid and x['terminal']=='RULED-NEUTRAL'))})
            fin=load(folder/'final_receipt_envelope.json')['artifact'];plan=load(folder/'mec_plan.json')
            mec.append({'race_id':rid,'grade':'KNOWN-CORRELATED-DEVELOPMENT','frozen_ticket_count':len(fin['final_ticket']['tickets']),
                        'investment':sum(t['stake'] for t in fin['final_ticket']['tickets']),
                        'tier_counts':dict(collections.Counter(t.get('mec_tier','UNKNOWN') for t in fin['final_ticket']['tickets'])),
                        'semantic_conversion':load(folder/'role_pair_third_closure.json'),
                        'mec_profile':plan.get('profile'),'outcome_metrics':'PENDING_VERIFIED_RESULT'})
        except Exception as e:errors.append({'race_id':rid,'reason':str(e)})
    closure=[]
    for idx,comps in reg['common_component_sets'].items():
        for comp in comps:
            rule=reg['component_score_rules'][idx][comp]
            rows=[x for x in feature_rows if x['index']==idx and x['component']==comp]
            closure.append({'index':idx,'component':comp,'evidence_input':'Frozen official SOURCE via existing compiler',
                            'semantic_feature':comp,'numerical_rule':rule['transform'],'rule_id':rule['rule_id'],
                            'missing_rule':rule.get('missing_rule'),'neutral_rule':'EXISTING RULE; no new constant',
                            'hold_rule':'invalid/nonfinite score, provenance absent, temporal/universe mismatch',
                            'output':'0..100 UNCALIBRATED ordinal; not probability',
                            'production_state':'UNBOUND','candidate_state':'BOUND_NON_PRODUCTION',
                            'calculated':sum(x['terminal']=='CALCULATED' for x in rows),
                            'ruled_neutral':sum(x['terminal']=='RULED-NEUTRAL' for x in rows),
                            'provenance':'runner_rule_terminalization.json','calibration':'OOS_PENDING'})
    programs={'COMMON_EXACT':common_status(),'MEC_R4':r4_status(),'MEC_R5':r5_status()}
    for label,file in [('KRS','krs_oos_status.json'),('LOCAL_NUMERICAL_DUAL','local_candidate_dual_oos_status.json'),('LOCAL_NUMERICAL_V03','local_candidate_v03_oos_status.json')]:
        programs[label]=load(ROOT/'runtime'/file)
    from krs_oos_promotion_gate import evaluate_r30
    from local_candidate_dual_oos_tracker import evaluate_measurements as dual_eval,read_measurements as dual_read
    from local_candidate_v03_oos_tracker import evaluate_measurements as v03_eval,read_measurements as v03_read
    programs['KRS']=evaluate_r30([load(p) for p in sorted((ROOT/'runtime/krs_oos_measurements').glob('*.json'))])
    programs['LOCAL_NUMERICAL_DUAL']=dual_eval(dual_read(ROOT/'runtime/local_candidate_dual_oos_measurements'))
    programs['LOCAL_NUMERICAL_V03']=v03_eval(v03_read(ROOT/'runtime/local_candidate_v03_oos_measurements'))
    pfs=build_report()
    artifacts={'numerical_rule_closure':closure,'runner_rule_terminalization':feature_rows,'numerical_comparison':comparisons,
               'evidence_details':evidence,'mec_conversion':mec,'current_state_shadow':current,'program_status':programs,
               'pfs_report':pfs,'program_errors':errors}
    for name,data in artifacts.items():(out/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2))
    (out/'hashes.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.glob('*.json')) if p.name!='hashes.json'},indent=2))
    print(json.dumps({'rules':len(closure),'races':len(comparisons),'runner_rules':len(feature_rows),'errors':len(errors),'actual_verified':pfs['actual_pfs']['verified_race_count']}))

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--freeze-final');ap.add_argument('--intent');ap.add_argument('--budget',type=int);ap.add_argument('--post');ap.add_argument('--output');a=ap.parse_args()
    if a.freeze_final:
        obj=capital_arms(load(a.freeze_final),a.budget,request=load(a.intent),generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),scheduled_post_at=a.post)
        obj['sha256']=sha(obj);dest=Path(a.output)
        with dest.open('x') as f:json.dump(obj,f,ensure_ascii=False,sort_keys=True,indent=2)
    else:run()

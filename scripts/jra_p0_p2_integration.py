"""Reuse frozen P0-P2 evidence and evaluate existing P2 interaction at equal exposure.

No model fitting, future activation, source collection or Production writes.
"""
import json,sys,hashlib,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'scripts'),str(ROOT/'research/jra_conditional_rank')]
from jra_prediction_quality_audit import records
from jra_20261018_formal_review import metrics
from probability_shadow import scores,distribution,sha
from head_p2_shadow import predict,matched_exposure,EXPOSURE_POLICY
from jra_production_postresult import settle_final
from family_authority_guard import resolve_current_authority
import gzip


def capital_summary(rows):
    # Reuse the canonical capital/drawdown metric implementation; role labels from
    # the Production review are deliberately not returned as Candidate role metrics.
    out=metrics(rows)
    keys=('registered_races','formal_finals','invested_races','zero_investment_final_races',
          'investment','return','profit_loss','weighted_pfs','median_race_pfs',
          'largest_returns_excluded','max_drawdown_yen','max_losing_streak',
          'hit_but_loss','largest_return_share','largest_race_exposure_share')
    return {k:out[k] for k in keys}


def run():
    evidence=ROOT/'evidence/jra_p0_20261018'
    _,authority=resolve_current_authority(root=ROOT)
    prior=json.loads(gzip.decompress((evidence/'JRA_20261018_36R_FORMAL_REVIEW.json.gz').read_bytes()))
    original={r['race_id']:r for r in prior['races']}
    base=json.loads((ROOT/'research/jra_conditional_rank/probability_candidate.json').read_text())
    head=json.loads((ROOT/'research/jra_conditional_rank/head_p2_candidate.json').read_text())
    groups={k:[] for k in ('PRODUCTION','UNIT_19_EXCLUSION','HEAD_P2_19_INTERACTION')}
    rows=[]
    data=records()
    for row in data:
        if row['day']!='20261018' or row['no_bet']:continue
        q,f,result=row['q'],row['f'],row['r'];rid=row['race_id'];official=result['official_result']
        arm_distributions={'UNIT_19_EXCLUSION':distribution(scores(q['runners'],base['rank_model']),dict(W=1.,P2=1.,P3=1.)),
                           'HEAD_P2_19_INTERACTION':predict(q['runners'],base,head)}
        portfolios={'PRODUCTION':f['final_ticket']}
        portfolios.update({k:{'tickets':out['tickets'],'total_investment':out['required_capital']}
                           for k,d in arm_distributions.items() for out in [matched_exposure(d,f)]})
        results={k:settle_final({'final_ticket':p},official) for k,p in portfolios.items()}
        for k,settled in results.items():
            item=dict(original[rid]);item.update(investment=settled['total_investment'],**{'return':settled['total_payout']})
            groups[k].append(item)
        unit=results['UNIT_19_EXCLUSION'];new=results['HEAD_P2_19_INTERACTION']
        def allocation(s):return {(t['bet_type'],tuple(t['selection'])):t['return'] for t in s['winning_tickets']}
        before,after=allocation(unit),allocation(new)
        rows.append({'race_id':rid,'venue':row['venue'],'source_sha256':q['source_snapshot_sha256'],
                     'request_sha256':sha(q),'final_sha256':f['sha256'],'result_sha256':sha(result),
                     'post_at':f['scheduled_post_at'],'budget':f['final_ticket']['total_investment'],
                     'ticket_count':len(f['final_ticket']['tickets']),
                     'returns':{k:s['total_payout'] for k,s in results.items()},
                     'interaction_removed_winning_return':sum(before[k] for k in before.keys()-after.keys()),
                     'interaction_new_winning_return':sum(after[k] for k in after.keys()-before.keys()),
                     'interaction_net_return':new['total_payout']-unit['total_payout'],
                     'changed_stake_on_shared_wins':sum(after[k]-before[k] for k in before.keys()&after.keys()),
                     'false_positive_cost':{k:sum(t['stake'] for t in portfolios[k]['tickets'])-sum(t['stake'] for t in results[k]['winning_tickets']) for k in portfolios}})
    rows.sort(key=lambda r:(r['post_at'],r['race_id']))
    controls={'KM-JRA-TKY-20261018-R11','KM-JRA-KYO-20261018-R02','KM-JRA-KYO-20261018-R04','KM-JRA-KYO-20261018-R10'}
    refs={}
    for name in ('JRA_20261018_36R_FORMAL_REVIEW.json.gz','PREDICTION_QUALITY_SUMMARY.json','CONDITIONAL_FAILURE_ANALYSIS.json','PREDICTIVE_STRUCTURE_AUDIT.json','CONDITIONAL_P2_RECHECK.json','DELIVERY_SHADOW_ISOLATION.json'):
        path=evidence/name;refs[name]=hashlib.sha256(path.read_bytes()).hexdigest()
    recheck=json.loads((evidence/'CONDITIONAL_P2_RECHECK.json').read_text())
    counts=recheck['bvi_corpus']['counts']
    feature_ids=('position_quality','pace_resilience','closing_quality','course_geometry_fit',
                 'same_course_distance_quality','opponent_strength','downhill_control','reacceleration')
    venue_mechanisms={}
    for venue in ('TKY','KYO','NGT'):
        runners=[h for row in data if row['day']=='20261018' and row['venue']==venue for h in row['runners']]
        coverage={key:sum(bool((h.get('evidence_features',{}).get(key) or {}).get('evidence_refs'))
                   and (h.get('evidence_features',{}).get(key) or {}).get('result_derived') is False
                   and (h.get('evidence_features',{}).get(key) or {}).get('source_authority')=='JRA_OFFICIAL'
                   for h in runners) for key in feature_ids}
        venue_mechanisms[venue]={'canon_promotion':'HOLD','status':'EXISTING_OBSERVED_FEATURE_REAUDIT_ONLY',
            'runner_count':len(runners),'observed_official_pre_result_feature_counts':coverage,
            'count_is_not_mechanistic_or_causal_validation':True,
            'limit':'No measured geometry/position/pace evidence synthesized and no venue coefficient fitted from Oct18'}
    report={'profile':'JRA-P0-P2-INTEGRATION-20261018','observed_at':datetime.now(timezone.utc).isoformat(),
            'classification':'EXPLORATION_AND_MECHANICAL_NOT_FORWARD_OOS','production_effect':'NONE',
            'base_main_sha':'56c7fca7f377b8261f22b4aee40e1c002e0404f8',
            'current_authority_id':authority.get('manifest_id') or authority.get('authority_id'),
            'model_sha256':{'unit_19':base['sha256'],'head_p2':head['sha256']},
            'comparison_policy':EXPOSURE_POLICY,'comparison_policy_sha256':sha(EXPOSURE_POLICY),
            'reference_artifact_file_sha256':refs,'formal_races':len(rows),'no_final_no_bet_excluded':2,
            'capital':{k:capital_summary(v) for k,v in groups.items()},
            'venue_capital':{v:{k:capital_summary([r for r in items if r['venue']==v]) for k,items in groups.items()} for v in ('TKY','KYO','NGT')},
            'positive_controls':[r for r in rows if r['race_id'] in controls],
            'races':rows,'actual_purchase':'UNVERIFIED_RECOMMENDATION_OR_RESEARCH_VIRTUAL',
            'comparison_limit':'unit19 vs interaction19 only; original rank41/equal-ordinal portfolio is a distinct existing baseline',
            'new_learning_live_consumption':0,'genuine_forward_oos':0,
            'inventory':{
                'delivery_first_independent_shadow':'IMPLEMENTED / NOT LIVE-VERIFIED',
                'research_fit_label_feature_binding':'CORRECTNESS DEFECT REPAIRED / MECHANICAL VERIFIED',
                'same_filesystem_checkpoint_resume':'IMPLEMENTED / VERIFIED',
                'fresh_runner_automatic_checkpoint_retrieval':'NOT IMPLEMENTED; original-witness manual restore only',
                'winner_conditioned_p2_utility':'PREDICTIVE MODEL LIMITATION; interaction worsened equal-exposure utility',
                'pair_third_interaction':'PREDICTIVE MODEL LIMITATION; exclusion-only baseline retained',
                'probability_calibration':'PREDICTIVE MODEL LIMITATION / UNVALIDATED',
                'bvi_hierarchical_model':'DATA DEFICIENCY',
                'railway_isolated_startup_rollback':'AUTHORITY / APPROVAL BLOCKED; no rejected operation retried',
                'new_learning_live_consumption':'FORWARD OOS PENDING',
                'future_72_official_intake_and_freeze':'FORWARD OOS PENDING'},
            'research_candidate_disposition':'HOLD; no model refit/runner auto-connection/promotion; future registration needs separate frozen evidence',
            'bvi':{'verified_identity_complete_samples':0,'inherited_counts':counts,
                   'hierarchical_fit':'BLOCKED_MISSING_PERMANENT_HORSE_SIRE_DAMSIRE_AND_OFFICIAL_RACE_IDS',
                   'minimum_recovery':'resolve IDs and conflicting labels, verify raw provenance and PIT/OIDC, count independent offspring and condition cells before choosing sample-size requirements',
                   'unaccepted_408_imported':False,'new_sources_collected':False},
            'venue_mechanisms':venue_mechanisms,
            'calibration':'UNVALIDATED; preserve unit model research baseline; no EV/Kelly authority',
            'p0':'IMPLEMENTED_NOT_LIVE_VERIFIED; independent archive witness/cutoff/Delivery ACK remain per-race requirements',
            'code_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
                ('scripts/jra_p0_p2_integration.py','research/jra_conditional_rank/head_p2_shadow.py','runtime/jra_shadow_checkpoint.py')}}
    report['sha256']=sha(report)
    (evidence/'P0_P2_INTEGRATION.json').write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('formal_races','capital','positive_controls','research_candidate_disposition')},ensure_ascii=False))


if __name__=='__main__':run()

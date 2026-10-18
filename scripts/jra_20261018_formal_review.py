"""Reproducible 36-race audit and exploratory sidecars; never edits frozen inputs."""
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime, timezone
import hashlib, json, statistics, sys
from itertools import permutations
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from jra_production_postresult import settle_final, verify_final
from post_result_learning import build_post_result_review
from jra_role_learning_shadow import build_shadow, digest, ticket_key, POLICY
from family_authority_guard import resolve_current_authority
from jra_delivery import verify_signed_final


def load(path):
    return json.loads(Path(path).read_text())


def metrics(rows):
    exposed=[r for r in rows if r.get('investment',0)>0 and r.get('return') is not None]
    formal=[r for r in rows if r.get('formal_final')]
    inv=sum(r['investment'] for r in exposed);ret=sum(r['return'] for r in exposed)
    ordered=sorted(exposed,key=lambda r:(r['post_at'],r['race_id']))
    equity=peak=drawdown=streak=maxstreak=0
    for r in ordered:
        equity+=r['return']-r['investment'];peak=max(peak,equity);drawdown=max(drawdown,peak-equity)
        streak=streak+1 if r['return']==0 else 0;maxstreak=max(maxstreak,streak)
    best=sorted(exposed,key=lambda r:(-r['return'],r['race_id']))
    trimmed={}
    for k in (1,2,3):
        subset=best[k:];i=sum(r['investment'] for r in subset);p=sum(r['return'] for r in subset)
        trimmed[str(k)]={'removed_race_ids':[r['race_id'] for r in best[:k]],'investment':i,'return':p,'pfs':100*p/i if i else None}
    return {'registered_races':len(rows),'formal_finals':len(formal),'invested_races':len(exposed),
        'no_final_races':len(rows)-len(formal),'zero_investment_final_races':sum(r.get('formal_final') and r['investment']==0 for r in rows),
        'investment':inv,'return':ret,'profit_loss':ret-inv,'weighted_pfs':100*ret/inv if inv else None,
        'median_race_pfs':statistics.median(100*r['return']/r['investment'] for r in exposed) if exposed else None,
        'largest_returns_excluded':trimmed,'max_drawdown_yen':drawdown,'max_losing_streak':maxstreak,
        'drawdown_order':'official post_at then race_id; same-time ordering is descriptive, not actual purchase ledger',
        'hit_but_loss':sum(0<r['return']<r['investment'] for r in exposed),
        'largest_return_share':max((r['return'] for r in exposed),default=0)/ret if ret else None,
        'largest_race_exposure_share':max((r['investment'] for r in exposed),default=0)/inv if inv else None,
        'role_capture':{role:{'captured':sum(r['capture'][role] for r in formal),'denominator':len(formal),
            'rate':sum(r['capture'][role] for r in formal)/len(formal) if formal else None} for role in ('W','P2','P3','ORDERED_PAIR','EXACT')},
        'first_material_failure':dict(Counter(r['first_material_failure'] for r in rows)),
        'dominant_loss_owner':dict(Counter(r.get('dominant_pfs_loss_owner','UNKNOWN') for r in rows)),
        'actual_purchase_status':'UNVERIFIED','forward_prediction_improvement':'PENDING'}


def run(root=ROOT):
    _,authority=resolve_current_authority(root=root)
    health=load(root/'evidence/jra_p0_20261018/RUNTIME_READINESS.json')['health']
    contract=load(root/authority['common_family_components']['family_runtime_contracts_profile'])['families']['JRA']
    rows=[];arms=defaultdict(list);bet=defaultdict(lambda:{'investment':0,'return':0});tiers=defaultdict(lambda:{'investment':0,'return':0})
    states=[load(p) for p in (root/'runtime/learning_states').glob('*20261018*')]
    for venue in ('TKY','KYO','NGT'):
      for no in range(1,13):
        rid=f'KM-JRA-{venue}-20261018-R{no:02d}'; fp=root/'runtime/final_artifacts'/f'{rid}.json'
        row={'race_id':rid,'venue':venue,'race_no':no,'formal_final':fp.exists()}
        if not fp.exists():
            terminal=next((root/'runtime/jra_no_bet_terminals').glob(rid+'*'))
            t=load(terminal);op=root/'runtime/source_candidate_oos'/rid/'official_result_observation.json';o=load(op) if op.exists() else {}
            row.update(first_material_failure=t.get('first_blocked_stage','AKI_SELECTION'),
              decision=t.get('decision_reason'),investment=0,**{'return':0},pfs=None,
              official_top3=o.get('result_top3'),official_observation_path=str(op.relative_to(root)),
              production_result_path=None,production_learning_path=None,
              result_status='OFFICIAL_OBSERVATION_ONLY_NO_PRODUCTION_SIGNED_RESULT',
              no_bet_learning_status='MISSING_CANONICAL_NO_BET_LEARNING',
              dominant_pfs_loss_owner='NO_CAPITAL_EXPOSURE',capture=None)
            rows.append(row);continue
        f=load(fp);verify_final(f);verify_signed_final(f,health,contract)
        result=load(root/'runtime/results'/f'{rid}.json');official=result['official_result']
        settled=settle_final(f,official)
        if any(settled[k]!=result['settlement'][k] for k in ('total_investment','total_payout','profit_loss')):
            raise ValueError('SETTLEMENT_REPLAY_MISMATCH:'+rid)
        if result['frozen_prediction_ref']['immutable_final_sha256']!=f['sha256']:
            raise ValueError('RESULT_FINAL_SHA_MISMATCH:'+rid)
        old=load(root/'runtime/reviews_auto'/f'{rid}-AUTO.json');new=build_post_result_review(result,f)
        q=load(root/'runtime/requests'/f'{rid}-LIVE-R1-FORMAL.json')
        actual=list(map(str,official['top3']));roles=f['static_prediction']['roles'];ranking=list(map(str,f['static_prediction']['ranking']))
        pair=tuple(actual[:2]);triple=tuple(actual)
        pset={(str(x['head']),str(x['second'])) for x in f['pair_dispositions'] if x.get('status') in ('PURCHASE','PROTECT')}
        tset={(str(x['head']),str(x['second']),str(x['third'])) for x in f['third_dispositions'] if x.get('status') in ('PURCHASE','PROTECT')}
        rolecap={r:r in roles.get(h,[]) for r,h in zip(('W','P2','P3'),actual)}
        cap={**rolecap,'ORDERED_PAIR':pair in pset,'EXACT':triple in tset}
        winner_rank=ranking.index(actual[0])+1
        if not rolecap['W']:
            first='WINNER_MIGRATION_FAILURE' if set(roles.get(actual[0],[])) & {'P2','P3'} else 'HORSE_DISCOVERY_OR_WINNER_ROLE_FAILURE'
        elif not rolecap['P2']:first='P2_ROLE_FAILURE'
        elif pair not in pset:first='HEAD_LOCAL_ORDERED_PAIR_FAILURE'
        elif not rolecap['P3']:first='P3_ROLE_FAILURE'
        elif triple not in tset:first='PAIR_CONDITIONED_THIRD_FAILURE'
        else:first=new['failure_localization']['first_material_failure']
        runner_audit=[]
        for r in q['runners']:
            h=str(r['runner_id']);features=r.get('evidence_features') or {};values={k:v['value'] for k,v in r['canonical_components'].items()}
            feature_refs=defaultdict(list)
            for idx,c in r['canonical_components'].items():
                for component in c.get('components',[]):feature_refs[component.get('feature')].append(idx)
            runner_audit.append({'runner_id':h,'name':r.get('name'),'static_rank':ranking.index(h)+1,
              'official_finish':official.get('finish_order',[]).index(int(h))+1 if int(h) in official.get('finish_order',[]) else None,
              'roles':roles.get(h,[]),'indices':values,'feature_ids':sorted(features),
              'shared_feature_dependencies':{k:v for k,v in feature_refs.items() if len(v)>1},
              'repeated_dependency_is_not_automatically_a_bug':True,
              'bvi_status':r['canonical_components']['BVI'].get('information_status','OBSERVED_OR_MIXED'),
              'bvi_components':[{k:c.get(k) for k in ('feature','feature_rule_id','weight','weighted_contribution','source_fact')} for c in r['canonical_components']['BVI'].get('components',[])],
              'aki_ledger':[x for x in q['role_registry'] if str(x['runner_id'])==h]})
        shadow=build_shadow(q,f,historical=True,observed_at=datetime.now(timezone.utc).isoformat())
        market=q['source_snapshot'].get('jra_official_market_observation') or {}
        market_rows=sorted([r for r in market.get('runners',[]) if type(r.get('popularity_rank')) is int],key=lambda r:(r['popularity_rank'],int(r['runner_id'])))
        for name,top in [('STATIC_TOP3_BOX',list(map(int,ranking[:3]))),('MARKET_TOP3_BOX',[int(r['runner_id']) for r in market_rows[:3]])]:
            tickets=[{'bet_type':'EXACTA','selection':list(p),'stake':100} for p in permutations(top,2)]
            tickets += [{'bet_type':'TRIFECTA','selection':list(p),'stake':100} for p in permutations(top,3)]
            if len(top)==3:tickets += [{'bet_type':'TRIO','selection':sorted(top),'stake':100}]
            shadow['arms'][name]={'tickets':tickets,'ticket_count':len(tickets),'required_capital':sum(t['stake'] for t in tickets),
                'added_ticket_count':len(tickets),'removed_ticket_count':len(f['final_ticket']['tickets']),'added_capital':sum(t['stake'] for t in tickets)}
        for name,arm in shadow['arms'].items():
            ff=deepcopy(f);ff['final_ticket']['tickets']=arm['tickets'];ff['final_ticket']['total_investment']=arm['required_capital']
            s=settle_final(ff,official)
            budget=f['final_ticket']['total_investment'];keys={ticket_key(t) for t in f['final_ticket']['tickets']}
            hits=sum(t['stake']//100*official['payouts'][t['bet_type']]['per_100_yen'] for t in arm['tickets']
                     if tuple(sorted(t['selection']))==tuple(sorted(official['payouts'][t['bet_type']]['selection'])) and t['bet_type']=='TRIO')
            arms[name].append({'race_id':rid,'investment':s['total_investment'],'return':s['total_payout'],
                'added_capital':arm['added_capital'],'added_ticket_count':arm['added_ticket_count'],
                'removed_ticket_count':arm['removed_ticket_count'],
                'equal_budget_scaled_return':s['total_payout']*budget/s['total_investment'] if s['total_investment'] else None,
                'equal_ticket_prefix_return':_prefix_return(arm['tickets'],len(f['final_ticket']['tickets']),official),
                'equal_budget_semantics':'Fractional diagnostic only, not legal stake recommendation',
                'equal_ticket_semantics':'Frozen baseline-first arm order, not outcome-selected subset',
                'baseline_semantic_preserved':keys.issubset({ticket_key(t) for t in arm['tickets']}),
                'exploration_only':True,'oos_eligible':False})
        for t in f['final_ticket']['tickets']:
            k=t['bet_type'];pay=official['payouts'][k];sel=sorted(t['selection']) if k=='TRIO' else t['selection'];win=sorted(pay['selection']) if k=='TRIO' else pay['selection'];rr=t['stake']//100*pay['per_100_yen'] if sel==win else 0
            bet[k]['investment']+=t['stake'];bet[k]['return']+=rr
            tier=str(t.get('mec_tier') or t.get('tier') or 'UNSPECIFIED');tiers[tier]['investment']+=t['stake'];tiers[tier]['return']+=rr
        l=load(root/'runtime/learning_states'/f'{rid}.json');droot=root/'runtime/jra_delivery'/rid
        row.update(authority=q['current_authority_manifest'],source_sha256=q['source_snapshot_sha256'],
          source_freeze=q['source_snapshot']['source_freeze_at'],post_at=f['scheduled_post_at'],cutoff=f['prediction_cutoff'],
          static_computed_at=q.get('static_computed_at'),static_declared_freeze=q['static_freeze_timestamp'],
          final_signed_at=f['final_receipt']['receipt']['timestamp'],final_sha256=f['sha256'],
          final_receipt_sha256=f['final_receipt_sha256'],final_signature_independently_verified=True,investment=settled['total_investment'],**{'return':settled['total_payout']},
          pfs=settled['pfs'],capital_decision=settled['capital_policy_decision'],
          decision_population='ZERO_STAKE_FINAL' if not settled['total_investment'] else 'FROZEN_RECOMMENDATION',
          official_top3=official['top3'],official_payouts=official['payouts'],official_raw_sha256=official['raw_sha256'],
          official_result_captured_at=official['captured_at'],official_special_finish_handling='Accepted by existing official parser; duplicate top3 ranks are held, not coerced',
          capture=cap,ticket_capture=new['conversion'],first_material_failure=first,
          static_first_material_failure=old['failure_localization']['first_material_failure'],
          winner_static_rank=winner_rank,role_correct_static_top3_aki_excluded=winner_rank<=3 and not rolecap['W'],
          dominant_pfs_loss_owner=l['reference_metrics'].get('dominant_pfs_loss_owner','UNKNOWN'),
          aki=q['static_prediction'].get('aki_jra_v21'),runner_audit=runner_audit,
          model_market_disagreement=shadow['model_market_disagreement'],
          krs_receipt_sha256=f['krs_run_receipt']['receipt_sha256'],krs_run_count=f['krs_prediction_utility']['snapshot']['run_count'],
          krs_before=old['krs']['post_result_evaluation'],krs_recomputed=new['krs']['post_result_evaluation'],
          learning_state_id=l['state_id'],learning_sha256=l['sha256'],learning_effective_time=l.get('effective_time'),
          learning_consumption='UNVERIFIED_NO_EFFECTIVE_TIME_OR_FROZEN_INPUT_BINDING',
          notification_record=(droot/'notification.json').exists(),recipient_ack_record=(droot/'recipient_ack.json').exists(),
          canonical_readback_record=(droot/'availability_receipt.json').exists(),signed_result_independently_verified='UNKNOWN_NOT_PERSISTED_WITH_CANONICAL_RESULT',
          evidence_paths={'final':str(fp.relative_to(root)),'request':str((root/'runtime/requests'/f'{rid}-LIVE-R1-FORMAL.json').relative_to(root))})
        rows.append(row)
    summary=metrics(rows)
    return {'profile':'JRA_20261018_36R_FORMAL_REVIEW','authority':authority['manifest_id'],
      'race_date':'2026-10-18','observed_at':datetime.now(timezone.utc).isoformat(),
      'summary':summary,'venues':{v:metrics([r for r in rows if r['venue']==v]) for v in ('TKY','KYO','NGT')},
      'races':rows,'bet_type_pfs':dict(bet),'tier_pfs':dict(tiers),
      'shadow_comparison':{name:{'races':data,'investment':sum(x['investment'] for x in data),'return':sum(x['return'] for x in data),
          'added_capital':sum(x['added_capital'] for x in data),'equal_budget_return':sum(x['equal_budget_scaled_return'] or 0 for x in data),
          'equal_ticket_return':sum(x['equal_ticket_prefix_return'] for x in data),
          'classification':'EXPLORATION_REGRESSION_ONLY_NOT_FORWARD_OOS'} for name,data in arms.items()},
      'learning':{'states':len(states),'missing_effective_time':sum(not s.get('effective_time') for s in states),
          'verified_actual_next_input_consumptions':0,'retroactive_timestamp_invented':False,
          'production_consumption_authorized':False},
      'venue_canon':{v:{'CANON_REVISION_REQUIRED':'NO','PROMOTION':'HOLD','reason':'Current evidence does not isolate a venue-specific numeric effect from Common role/discovery failures; prospective shadow required.'} for v in ('TKY','KYO','NGT')},
      'positive_controls':['TKY-R11','KYO-R02','KYO-R04','KYO-R10'],
      'negative_controls':['TKY-R08','TKY-R12','NGT-ALL'],
      'production_policy_changed':False,'historical_artifacts_modified':False,
      'candidate_policy':POLICY,'forward_oos_status':'PREPARED_NOT_ACTIVATED_REQUIRES_REVIEW_AND_MERGE',
      'remaining_baselines':{'simple_box':'STATIC_TOP3_BOX, descriptive comparator only, not a proposed Production remedy',
          'market':'MARKET_TOP3_BOX from same Signed SOURCE observations, not a selection rule',
          'static_only':'NOT_IDENTIFIABLE_FROM_POST_KRS_FINAL_WITHOUT_INDEPENDENT_PRE_KRS_TICKET_FREEZE'},
      'quality_claim':'NO UNKNOWN_FUTURE_IMPROVEMENT_CLAIM'}


def _prefix_return(tickets,k,official):
    total=0
    for t in tickets[:k]:
        kind=t['bet_type'];p=official['payouts'][kind]
        a=sorted(t['selection']) if kind=='TRIO' else t['selection'];b=sorted(p['selection']) if kind=='TRIO' else p['selection']
        if a==b:total+=t['stake']//100*p['per_100_yen']
    return total

if __name__=='__main__':
    report=run();report['sha256']=digest(report)
    out=ROOT/'evidence/jra_p0_20261018/JRA_20261018_36R_FORMAL_REVIEW.json'
    out.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'summary':report['summary'],'venues':report['venues']},ensure_ascii=False,indent=2))

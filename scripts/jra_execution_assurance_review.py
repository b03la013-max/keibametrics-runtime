"""Extend the existing day review; all new historical comparisons are REPLAY.

Never issues receipts, sends notifications, runs an Engine, or changes policy.
"""
from pathlib import Path
from datetime import datetime,timezone
from itertools import permutations
from collections import Counter,defaultdict
import json,sys,hashlib

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'runtime')]
from jra_full_day_postrace_review import settle_tickets,robust,sha
from jra_production_krs_contract import production_krs_payload,assert_production_krs_receipt
from jra_role_rescue_shadow import build_role_rescue_shadow
from family_authority_guard import resolve_current_authority

D=ROOT/'runtime/daily_reviews/JRA-2026-10-17'
E=ROOT/'evidence/jra_day_review_20261017'

def load(p,default=None):
    p=Path(p);return json.loads(p.read_text()) if p.exists() else default

def save(name,obj):
    (D/name).write_text(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+'\n')

def comparison_tickets(final,request,market):
    original=final['final_ticket']['tickets']
    core=[t for t in original if t.get('mec_tier')=='CORE']
    # The ledger carries tiers while the FINAL ticket may not; the caller
    # enriches only a copy, never the frozen original.
    review='REVIEW' in request.get('aki_column_selection',{}).get('triggers',{}).values()
    arms={'A_CURRENT_PRODUCTION':original,'B_SELECTIVE_CORE_ONLY':core,
          'C_AKI_TRIGGER_SELECTIVE':core if review else original}
    allowed=final['final_ticket'].get('available_bet_types',[])
    for name,rank in [('D_STATIC_TOP3_BOX',final['static_prediction']['ranking']),('E_SOURCE_MARKET_TOP3_BOX',market)]:
        if 'TRIFECTA' in allowed and len(rank)>=3:
            arms[name]=[{'bet_type':'TRIFECTA','selection':list(p),'stake':100}
                        for p in permutations([int(h) for h in rank[:3]])]
    return arms

def main():
    ledger=load(D/'audit_ledger.json');rows=ledger['races'];now=datetime.now(timezone.utc).isoformat()
    tickets=load(D/'ticket_settlement.json');byrace=defaultdict(dict)
    for t in tickets:
        key=(t['bet_type'],tuple(map(str,t['selection'])))
        byrace[t['race_id']][key]=t.get('mec_tier','UNKNOWN')
    matrix=[];replays=[];aki=[];checked=[];consumption=[];role_shadows=[]
    result_envelopes={}
    for p in (E/'result_checkpoints').glob('*/result_receipt_envelope.json'):
        envelope=load(p);result_envelopes[envelope['receipt']['race_id']]=envelope
    for row in rows:
        rid=row['race_id'];pred=row['prediction'];req=load(ROOT/(row['artifact_refs']['request'] or '__missing__'),{})
        final=load(ROOT/(row['artifact_refs']['final'] or '__missing__'),{})
        classification=row['first_material_failure'];settlement=row.get('settlement') or {}
        matrix.append({'race_id':rid,'venue':row['venue'],'status':row['observed_status']['state'],
            'formal_grade':row['formal_grade'],'temporal_eligibility':row['temporal_eligibility'],
            'capture':{k:pred[k] for k in ['W','P2','P3','ordered_pair','ordered_exact','winner_rank']} if pred else 'NOT EXECUTED',
            'first_material_failure':classification,'secondary_failures':row['secondary_failures'],
            'dominant_pfs_loss_owner':row['dominant_pfs_loss_owner'],
            'observed_recommendation_profit_loss':settlement.get('profit_loss'),
            'capital_overexpansion':'HYPOTHESIS; wide tickets alone do not establish avoidable loss',
            'aki_overcompression':'UNDETERMINED unless exact pre-AKI Production semantics recovered',
            'actual_purchase':'NOT VERIFIED'})
        learning=load(ROOT/(row['artifact_refs']['learning'] or '__missing__'),{})
        context=req.get('learning_intake') or req.get('prequential_learning_context')
        next_row=next((r for r in rows if r['venue']==row['venue'] and r['race_no']==row['race_no']+1),None)
        signed_at=result_envelopes.get(rid,{}).get('receipt',{}).get('timestamp')
        next_cutoff=(next_row or {}).get('temporal',{}).get('prediction_cutoff')
        timing='UNKNOWN'
        if signed_at and next_cutoff:
            timing=('SIGNED_RESULT_AFTER_NEXT_CUTOFF / SIGNED_LEARNING_DELIVERY_MISS' if datetime.fromisoformat(signed_at.replace('Z','+00:00'))>=datetime.fromisoformat(next_cutoff.replace('Z','+00:00'))
                    else 'SIGNED_RESULT_BEFORE_NEXT_CUTOFF; INTAKE STILL UNVERIFIED')
        consumption.append({'race_id':rid,'learning_state_recorded':bool(learning),
            'event_recorded':bool(load(ROOT/(row['artifact_refs']['result'] or '__missing__'),{}).get('learning_event')),
            'next_race_consumption':'NOT VERIFIED','target_prediction_learning_binding':context or 'NOT PRESENT',
            'effective_time':learning.get('effective_time','UNKNOWN'),
            'next_same_venue_race':next_row['race_id'] if next_row else 'PENDING NEXT MEETING',
            'signed_result_timestamp':signed_at or 'UNKNOWN','next_cutoff':next_cutoff or 'UNKNOWN',
            'timing':timing,'delivery_miss':'OBSERVED' if 'DELIVERY_MISS' in timing else 'UNDETERMINED: generation before cutoff does not prove intake'})
        if not final:continue
        raw=load(ROOT/row['krs']['raw_output_ref']);payload=production_krs_payload(req)
        assert_production_krs_receipt(payload,raw,expected_engine_sha256=req['engine_sha256'])
        checked.append({'race_id':rid,'output_receipt_binding':'PASS',
            'input_hash_contract':'UNVERIFIED_LEGACY_HASH_SCOPE','historical_receipt_modified':False})
        role_shadow=build_role_rescue_shadow(final)
        role_shadow['lane']='RESEARCH-REPLAY; NOT FORWARD OOS'
        role_shadows.append(role_shadow)
        pre=load(ROOT/(row['artifact_refs']['candidate_pre_result'] or '__missing__'),{})
        basis=(pre.get('source_snapshot_sha256')==req.get('source_snapshot_sha256') and
               pre.get('numeric_provenance_hash')==req.get('index_provenance_hash') and
               pre.get('ranking')==final['static_prediction']['ranking'])
        before=(pre.get('owner') or {}).get('active_columns',{})
        after=req.get('aki_column_selection',{}).get('columns',{})
        actual=row['official_result']['top3']
        changes={}
        for role,horse in zip(['W','P2','P3'],actual):
            b=set(map(str,before.get(role,[])));a=set(map(str,after.get(role,[])))
            changes[role]={'before':sorted(b),'after':sorted(a),'added':sorted(a-b),'removed':sorted(b-a),
                'candidate_baseline_hit_lost':str(horse) in b-a if basis and not row['official_result']['top3_display_order_is_not_unique'] else None,
                'candidate_baseline_capture_added':str(horse) in a-b if basis and not row['official_result']['top3_display_order_is_not_unique'] else None}
        aki.append({'race_id':rid,'basis_match':basis,'comparison_lane':'FROZEN CANDIDATE OWNER vs FORMAL AKI',
            'production_pre_aki_identity':'UNVERIFIED: candidate envelope raw-owner hash differs; do not infer production bug',
            'axes':row['aki']['axes'],'axis_failure_risk':row['aki']['axis_failure_risk'],'columns':changes})
        if not settlement.get('investment'):continue
        # Only existing Production exposure enters this research population.
        copyfinal=json.loads(json.dumps(final))
        for t in copyfinal['final_ticket']['tickets']:
            t['mec_tier']=byrace[rid].get((t['bet_type'],tuple(map(str,t['selection']))),'UNKNOWN')
        source=load(ROOT/row['artifact_refs']['source'])['artifact']
        # Use exactly the market order frozen with the same SOURCE, never closing odds.
        market_obs=source.get('jra_official_market_observation') or {}
        market_rows=market_obs.get('runners',[])
        market=[str(x['horse_no']) for x in sorted(market_rows,key=lambda x:(x.get('popularity_rank') or 999,int(x['horse_no']))) if x.get('popularity_rank')]
        for arm,ts in comparison_tickets(copyfinal,req,market).items():
            s=settle_tickets(ts,row['official_result'])
            replays.append({'race_id':rid,'post':row['post'],'arm':arm,'lane':'RESEARCH-REPLAY; NOT FORWARD OOS',
                'source_snapshot_sha256':req['source_snapshot_sha256'],'ticket_count':len(ts),
                **{k:s[k] for k in ['investment','return','profit_loss','pfs','hit_but_loss']}})
    save('prediction_failure_matrix.json',{'population':36,'rows':matrix,'failure_counts':dict(Counter(x['first_material_failure']['classification'] for x in matrix)),
        'causal_loss_decomposition':'UNDETERMINED; first observed miss is not a causal yen allocation'})
    save('execution_assurance_closure.json',{'generated_at':now,'inherited_head':'470bb61b9beb2e397079e2925d2ceb9905d0c9fb',
        'source_oidc':load(E/'source_oidc/summary.json'),'krs':checked,'runtime':load(E/'runtime_followup.json'),
        'delivery':{'signed_final':23,'canonical_availability_before_post':23,'verified_user_delivery':0,
            'chatgpt_automatic_push':'NOT IMPLEMENTED IN OBSERVED ROUTE','actual_notifications_sent_by_this_review':0},
        'learning':consumption,'confirmed_next_prediction_consumption':0,
        'closed_loop_status':'PARTIAL: persistence/readiness do not prove delivery/application',
        'production_activation':'NONE','merge':'PENDING OWNER EXACT-HEAD APPROVAL AND INDEPENDENT REVIEW'})
    save('aki_incremental_comparison.json',{'rows':aki,'notice':'Pre-AKI comparator is an existing frozen Candidate; hash mismatch prevents causal Production overcompression claim.'})
    save('krs_unique_role_shadow_replay.json',{'rows':role_shadows,'production_ticket_conversion':0,
        'warning':'Retrospective design screen only; no historical Production hit or unknown-future OOS credit.'})
    save('capital_research_comparison.json',{'population':'19 positive-exposure Frozen Production FINAL; 4 PAPER excluded, 13 no FINAL excluded',
        'lane':'RESEARCH-REPLAY','rows':replays,
        'arms':{arm:robust([r for r in replays if r['arm']==arm]) for arm in sorted({r['arm'] for r in replays})},
        'matched_budget':'D/E are 6 tickets x100 yen when both available. A/B/C have unequal exposure; no equal-budget superiority claim.',
        'historical_selection':'Deterministic frozen input only; definitions made after Oct17 results, so never count as unknown-future OOS.'})
    authority_path,authority=resolve_current_authority(root=ROOT,now=datetime.now(timezone.utc))
    files=['runtime/jra_production_krs_contract.py','runtime/jra_learning_intake.py','runtime/jra_role_rescue_shadow.py',
        'runtime/race_day_fast_reflection.py','scripts/jra_execution_assurance_review.py',
        str(authority_path),authority['common_family_components']['family_runtime_contracts_profile'],
        'runtime/jra_static_owner_executable.py','runtime/jra_aki_dispatch.py','runtime/jra_aki_v21.py',
        'profiles/jra_aki_v21_columns_20261011_v1.json','profiles/jra_aki_v21_components_20261011_v1.json',
        'runtime/minimum_efficient_coverage.py','runtime/capital_policy.py']
    fixed={'A_CURRENT_PRODUCTION':'Exact existing FINAL tickets; policy unchanged',
        'B_SELECTIVE_CORE_ONLY':'Existing R3 CORE tickets only; no added combinations',
        'C_AKI_TRIGGER_SELECTIVE':'If any official AKI column trigger is REVIEW use CORE_ONLY, otherwise existing FINAL tickets; never repair missing Pair',
        'D_STATIC_TOP3_BOX':'All 6 TRIFECTA permutations of frozen Static top3; 100 yen each; skip unavailable bet type',
        'E_SOURCE_MARKET_TOP3_BOX':'All 6 TRIFECTA permutations of same Signed SOURCE popularity top3; 100 yen each; skip incomplete market'}
    protocol={'candidate_id':'JRA-POST-OCT17-PAIRED-SHADOW-20261017-R1','registered_at':now,
        'status':'PREREGISTERED FOR OWNER REVIEW / NOT ACTIVATED','family':'JRA','venues':['TKY','KYO','NGT'],
        'eligible':'Unknown future races after this commit and Owner activation; freeze same SOURCE/universe/cutoff before result',
        'required_sample':{'distinct_races':60,'minimum_meeting_days':3,'minimum_venues':2,
            'precision':'Design pilot only, not a power claim; preserve all abstentions/failures'},
        'arms':fixed,'definition_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files},
        'baseline':'A Current Production; D/E matched budget comparator separately',
        'baseline_authority':authority['manifest_id'],
        'primary_prediction_metric':'Ordered Exact capture at fixed candidate width; separately Winner/P2/P3 capture',
        'primary_capital_metric':'Paired recommendation profit/loss; weighted PFS plus largest-return-excluded PFS',
        'secondary_metrics':['Candidate/false-positive width','KRS unique rescue/harm','Role/Pair/Third retention','Investment','Drawdown','Hit-but-loss'],
        'negative_control':'Unchanged Production arm exactly reproduces frozen tickets; same-input duplicate must have zero delta',
        'false_positive_cost':'Track additional losing tickets and yen separately; no win-probability interpretation of KRS frequency',
        'capital_impact':'0 actual yen; hypothetical exposure per arm only; no purchase',
        'stop_reject':['Any post-cutoff freeze or target-result leakage','Source/universe mismatch','Changed fingerprint',
            'Missing signed FINAL for Production comparator','Nonpositive paired primary gain or positive-control loss at fixed review point'],
        'promotion_authority':'Current Authority + explicit Owner decision; no auto promotion at 30/60',
        'production_policy_change':False,'historical_oct17_count_in_forward_sample':0,
        'bvi_abc':'Existing admitted same-race pre-frozen distinct A/B/C only; A=B is not added-information evidence',
        'learning':'runtime/jra_learning_intake.py validates Shadow context only; no automatic numerical application'}
    protocol['per_candidate']=[{
        'candidate_id':key+'-JRA-20261017-R1','algorithm':algorithm,'family':'JRA','venues':['TKY','KYO','NGT'],
        'baseline':'A_CURRENT_PRODUCTION','same_source_cutoff_universe_required':True,
        'primary_metric':'Paired profit/loss and robust PFS','secondary_metric':'Lost baseline hits; ticket width; drawdown',
        'negative_control':'A frozen tickets reproduce exactly','false_positive_cost':'Hypothetical losing ticket yen',
        'required_sample':protocol['required_sample'],'capital_impact':'0 actual yen',
        'stop_reject':protocol['stop_reject'],'promotion_authority':protocol['promotion_authority'],
        'historical_screen':('REJECTED FOR PROMOTION: loses KYO11 positive-control protection hit; negative-control research only'
            if key.startswith(('B_','C_')) else 'CONTROL/BASELINE; NOT AN APPROVED NEW POLICY')
        } for key,algorithm in fixed.items()]
    protocol['per_candidate'].append({'candidate_id':'JRA-KRS-UNIQUE-ROLE-REVIEW-ONE-PER-COLUMN-v1',
        'algorithm':'runtime/jra_role_rescue_shadow.py; at most one already-observed unique actionable KRS proposal per column; no Pair/Third/ticket creation',
        'family':'JRA','venues':['TKY','KYO','NGT'],'baseline':'Frozen Static roles',
        'primary_metric':'Incremental Winner/P2/P3 capture per added role; fixed one-per-column width',
        'secondary_metric':'False-positive additions; distinct Pair feasibility; Unique Harm',
        'negative_control':'Already-held Static roles must never become unique rescues',
        'false_positive_cost':'Added false role count; no actual stake','capital_impact':'0 actual yen',
        'required_sample':protocol['required_sample'],'stop_reject':protocol['stop_reject'],
        'promotion_authority':protocol['promotion_authority'],'status':'SHADOW ONLY / OWNER ACTIVATION PENDING'})
    for candidate in protocol['per_candidate']:
        candidate['policy_fingerprint']=sha({'candidate':candidate,'definitions':protocol['definition_sha256']})
    previous=load(D/'preregistered_shadow_comparison.json')
    if previous:
        if previous.get('definition_sha256')!=protocol['definition_sha256'] or previous.get('arms')!=protocol['arms']:
            raise ValueError('PREREGISTRATION_CHANGED: create a new candidate revision; never overwrite an active cohort')
        protocol=previous
    protocol['policy_fingerprint']=sha({k:v for k,v in protocol.items() if k!='policy_fingerprint'})
    save('preregistered_shadow_comparison.json',protocol)
    save('venue_canon_verdict.json',{'TKY':'HOLD','KYO':'HOLD','NGT':'HOLD',
        'reason':'One dependent day; no multi-day frozen venue-specific causal mechanism. Runtime/AKI/MEC/Capital stay Common.',
        'candidate_attachments':'Tokyo/Kyoto v1.0 are NON-PRODUCTION compatibility sources, not race-time Production Authority',
        'required_oos':'Pre-race pace/position/corner/closing mechanism, positive-control preservation, venue/day paired comparison'})
    print(json.dumps({'rows':len(matrix),'krs_output_bindings':len(checked),'replay_arm_counts':dict(Counter(r['arm'] for r in replays)),
        'fingerprint':protocol['policy_fingerprint']}))

if __name__=='__main__':main()

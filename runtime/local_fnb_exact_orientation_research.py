"""Optional fixed-Owner Exact Selection experiment; no Production promotion.

Static eligibility + historical World compatibility + scenario ordinal
stability are explicit NEW research hypotheses. The original S1/S2 arrays
and all numerical/KRS/MEC/Capital policy bytes remain unchanged.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from itertools import product, permutations
import hashlib
import json
import math
import re
from pathlib import Path

from runtime import local_fnb_semantic_closure as semantic
from runtime.minimum_efficient_coverage import build_mec_plan, validate_mec_plan
from runtime.capital_policy import resolve_capital_policy
from runtime.jra_ticket_tree_renderer import render_ticket_tree

PROFILE = 'KM-FNB-EXACT-SCENARIO-ORDINAL-RESEARCH-v0.1-20261104'
VERSION = '0.1'
SCENARIOS = ('natural','low_friction','high_friction','leader_success','leader_failure')
PROFILE_PATH = Path(__file__).resolve().parents[1]/'profiles/local_fnb_exact_scenario_ordinal_research_v0.1_20261104.json'
MODULE_BYTES = Path(__file__).read_bytes()
MODULE_SHA = hashlib.sha256(MODULE_BYTES).hexdigest()


def encoded(x):
    return (json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def require(condition, code):
    if not condition:raise ValueError('FNB_EXACT_RESEARCH_' + code)


def stamp(value):
    dt=datetime.fromisoformat(str(value).replace('Z','+00:00'))
    require(dt.tzinfo is not None,'AWARE_CLOCK_REQUIRED')
    return dt


def validate_freeze(freeze, evaluated_at):
    require(sha(Path(__file__).read_bytes())==MODULE_SHA,'MODULE_CHANGED_AFTER_IMPORT')
    p=PROFILE_PATH.read_bytes();profile=json.loads(p)
    require(freeze.get('profile')==PROFILE and freeze.get('module_sha256')==MODULE_SHA
        and freeze.get('profile_sha256')==sha(p) and profile.get('profile')==PROFILE
        and profile.get('version')==VERSION and profile.get('scenarios')==list(SCENARIOS)
        and profile.get('production_adopted') is False,'EXACT_PROFILE_CODE_FREEZE_MISMATCH')
    require(stamp(freeze['frozen_at'])<=stamp(evaluated_at),'PROFILE_FREEZE_IN_FUTURE')
    return profile


def scenario_order(krs, active):
    out={}
    for name in SCENARIOS:
        scenario=(krs.get('scenario_analysis') or {}).get(name)
        require(isinstance(scenario,dict) and type(scenario.get('run_count')) is int
            and scenario['run_count']>0,'SCENARIO_NOT_EXECUTED:' + name)
        rows=scenario.get('ssr') or {}
        require(set(rows)==set(active),'SCENARIO_UNIVERSE_MISMATCH:' + name)
        out[name]={}
        for rid in active:
            row=rows[rid]
            require(all(type(row.get(k)) in (int,float) and math.isfinite(row[k])
                and 0<=row[k]<=1 for k in ('SSR-W','SSR-P2','SSR-P3','Z4R-W','Z4R-P2','Z4R-P3','LSR')),
                'SCENARIO_SUPPORT_INVALID')
            out[name][rid]=deepcopy(row)
    return out


def dominates(scenarios, a, b, column):
    comparisons=[{'scenario':n,'left':scenarios[n][a][column],'right':scenarios[n][b][column]}
                 for n in SCENARIOS]
    return {'left':a,'right':b,'column':column,'comparisons':comparisons,
        'weak_every_scenario':all(x['left']>=x['right'] for x in comparisons),
        'strict_some_scenario':any(x['left']>x['right'] for x in comparisons),
        'dominates':all(x['left']>=x['right'] for x in comparisons)
            and any(x['left']>x['right'] for x in comparisons)}


def world_review(context_rows, triple):
    paths=[context_rows[r].get('paths') or [] for r in triple]
    require(all(paths),'KNOWN_CONTEXT_WITHOUT_HISTORICAL_PATH')
    witness=None;total=0;conflicts=0
    for indices in product(*(range(len(p)) for p in paths)):
        total+=1
        chosen=[p[i] for p,i in zip(paths,indices)]
        exclusive=sum(p['world_hypothesis']=='LEAD_HOLD' for p in chosen)
        if exclusive>1:conflicts+=1
        elif witness is None:
            witness=[{'runner_id':rid,'context_path_index':i,'world':p['world_hypothesis'],
                'source_event_date':p['source_event_date'],'source_raw_sha256':p['source_raw_sha256'],
                'stage_cost_hypotheses':deepcopy(p['stage_cost_hypotheses'])}
                for rid,i,p in zip(triple,indices,chosen)]
    return {'compatible_hypothesis_exists':witness is not None,'path_combinations_reviewed':total,
        'multiple_exclusive_leader_combinations':conflicts,'compatibility_witness':witness,
        'interpretation':'HISTORICAL_PROJECTED_WORLD_ASSUMPTION_NOT_OBSERVED_JOINT_TACTICS',
        'measured_current_tactics_or_joint_causal_support':False}


def evaluate(prediction, context, krs, s2, *, freeze, evaluated_at):
    """Evaluate every N³ slot; only duplicates are structural exclusions."""
    profile=validate_freeze(freeze,evaluated_at)
    scope=re.match(r'^KM-LOCAL-FNB-(\d{8})-R(\d{2})(?:-|$)',prediction.get('race_id',''))
    require(scope is not None and scope[1] in ('20261104','20261105','20261106')
        and 1<=int(scope[2])<=12,'RACE_OUTSIDE_FROZEN_RESEARCH_SCOPE')
    active=semantic._validate(prediction)
    require(stamp(prediction['freeze_at'])<=stamp(evaluated_at),'EVALUATION_BEFORE_STATIC_FREEZE')
    require(context.get('sha256')==semantic._sha({k:v for k,v in context.items() if k!='sha256'})
        and prediction['input_context_sha256']==context['sha256']
        and prediction['source_snapshot_sha256']==context.get('source_snapshot_sha256')
        and prediction['race_id']==context.get('race_id'),'CONTEXT_SOURCE_STATIC_BINDING_MISMATCH')
    require(s2.get('profile')==semantic.UNKNOWN_RESEARCH_POLICY and s2.get('race_id')==prediction['race_id']
        and s2.get('source_snapshot_sha256')==prediction['source_snapshot_sha256']
        and s2.get('model_prediction_sha256')==semantic._sha(prediction),'S2_SOURCE_STATIC_BINDING_MISMATCH')
    require(all(r['status']==semantic.PROPOSAL_STATUS for r in prediction['pair_dispositions']+prediction['third_dispositions']),
        'ORIGINAL_PROPOSAL_MUTATED_OR_UNJUSTIFIED_PURCHASE')
    snap=krs.get('snapshot') or {}
    require(snap.get('run_count')==5000 and snap.get('master_seed')==1
        and snap.get('prediction_id')==prediction['PRE_KRS_input']['race']['prediction_id'],
        'KRS_EXECUTION_OR_REVISION_MISMATCH')
    orders=scenario_order(krs,active)
    unknown=semantic._unknown(prediction)
    ctx={r['runner_id']:r for r in context['runners']}
    require(set(ctx)==set(active),'CONTEXT_FULL_UNIVERSE_MISMATCH')
    pair_allowed,third_allowed=semantic._proposal_qualification(prediction)
    p2={r['head']:r['ranking'] for r in prediction['head_local_P2']}
    third_ranks={(r['head'],r['second']):r['ranking'] for r in prediction['pair_conditioned_Third']}
    s2_pairs={tuple(p['pair_id'].split('>')):p for p in s2['known_pair_scoped_subplans']}
    joint={tuple(str(r[k]) for k in ('W','P2','P3')):r for r in krs.get('top_trifecta_occurrence',[])}
    ledger=[];candidates=[]
    row_by={}
    for h,s,t in product(active,repeat=3):
        triple=(h,s,t);key='>'.join(triple)
        row={'path_id':key,'head':h,'second':s,'third':t,'rule_id':PROFILE,'version':VERSION,
            'source_snapshot_sha256':prediction['source_snapshot_sha256'],
            'static_prediction_sha256':prediction['sha256'],'static_model_sha256':prediction['model_code_sha256'],
            'static_freeze_at':prediction['freeze_at'],'selection_freeze_at':evaluated_at,
            'unknown_participants':sorted(set(triple)&unknown,key=int),'formal_terminal':'POLICY_NOT_ADOPTED',
            'production_adopted':False,'global_P3':t in prediction['column_rankings']['P3']['front'],
            'material_pair_in_S2':(h,s) in s2_pairs,'head_local_P2_front':bool(pair_allowed.get((h,s))),
            'pair_conditioned_Third_front':bool(third_allowed.get(triple)),
            'evidence_refs':['research_prediction.json','context.json','krs/execution_output.json'],
            'joint_occurrence':deepcopy(joint.get(triple)),
            'joint_support_status':'OBSERVED_IN_TRUNCATED_TOP20' if triple in joint else 'CENSORED_NOT_ZERO_NOT_PROVEN_UNOBSERVED',
            'joint_marginal_occurrence_is_not_probability_or_EV':True}
        if len(set(triple))<3:
            terminal,reason='STRUCTURAL_INELIGIBLE','SAME_RUNNER_MULTIPLE_FINISH_POSITIONS'
        elif set(triple)&unknown:
            terminal,reason='UNKNOWN_UNRESOLVED','NO_KNOWN_STATIC_CONDITIONAL_PATH_UNKNOWN_PROTECTED_BY_S2'
        elif not pair_allowed.get((h,s)) or not third_allowed.get(triple):
            protected=(h,s) in s2_pairs and t in s2_pairs[(h,s)]['effective_pair_scoped_p3']
            terminal='EXACT_PROTECT_ONLY' if protected else 'EVIDENCE_RANKED_LOWER'
            reason='NOT_ORIGINAL_KNOWN_HEAD_LOCAL_AND_PAIR_THIRD_FRONT_NO_STRUCTURAL_EXCLUSION'
        else:
            stage=world_review(ctx,triple)
            tests=[dominates(orders,h,s,'SSR-W'),dominates(orders,h,t,'SSR-W'),dominates(orders,s,t,'SSR-P2')]
            positive=all(orders[n][rid][col]>0 for n in SCENARIOS
                for rid,col in ((h,'SSR-W'),(s,'SSR-P2'),(t,'SSR-P3')))
            row.update(winner_path=deepcopy(prediction['runner_world_stage_basis'][h]),
                head_local_P2_assessment=deepcopy(next(x for x in p2[h]['rows'] if x['runner_id']==s)),
                pair_Third_assessment=deepcopy(next(x for x in third_ranks[(h,s)]['rows'] if x['runner_id']==t)),
                stage_world_review=stage,ordinal_comparisons=tests,assigned_roles_positive_in_every_scenario=positive,
                historical_six_stage_hypotheses={r:deepcopy(ctx[r]['stage_cost_topology']) for r in triple},
                hypothetical_position_ranges={r:deepcopy(ctx[r]['reachable_position_range']) for r in triple},
                scenario_stage_support={n:{r:{'marginals':orders[n][r],
                    'simulated_positions':deepcopy((krs['scenario_analysis'][n].get('positions') or {}).get(r))}
                    for r in triple} for n in SCENARIOS},
                quality={'known_historical_context_runners':3,'unknown_context_runners':0,
                    'stage_historical_proxy_runners':3,'measured_current_tactics_runners':0,
                    'unconsumed_unknown_fields':deepcopy(prediction.get('unconsumed_unknown_fields',[]))})
            if not stage['compatible_hypothesis_exists']:
                terminal,reason='EXACT_PROTECT_ONLY','SCENARIO_CONFLICT_MULTIPLE_EXCLUSIVE_LEAD_HOLD_PATHS'
            elif not positive:
                terminal,reason='EXACT_PROTECT_ONLY','NO_ASSIGNED_ROLE_OCCURRENCE_IN_AT_LEAST_ONE_SCENARIO'
            elif not all(x['dominates'] for x in tests):
                terminal,reason='EXACT_PROTECT_ONLY','SAME_SET_ORIENTATION_TIE_OR_SCENARIO_ORDER_CROSSING'
            else:
                terminal,reason='EXACT_PURCHASE','NEW_PAPER_HYPOTHESIS_KNOWN_CONDITIONAL_PATH_AND_SCENARIO_ORDINAL_STABILITY'
                candidates.append(triple)
        row.update(terminal=terminal,reason=reason)
        ledger.append(row);row_by[triple]=row
    sets={tuple(sorted(x,key=int)) for x in permutations(active,3)}
    comparison=[]
    for group in sorted(sets,key=lambda x:tuple(map(int,x))):
        orientations=[tuple(x) for x in permutations(group)]
        chosen=[x for x in orientations if row_by[x]['terminal']=='EXACT_PURCHASE']
        require(len(chosen)<=1,'CONTRADICTORY_EXACT_DIRECTIONS_FOR_SAME_SET')
        comparison.append({'three_horse_set':list(group),'all_six_orientations':[
            {'orientation':list(x),'terminal':row_by[x]['terminal'],'reason':row_by[x]['reason']}
            for x in orientations],'exact_chosen':list(chosen[0]) if chosen else None,
            'not_indiscriminate_six_way_purchase':True})
    return {'profile':PROFILE,'version':VERSION,'race_id':prediction['race_id'],
        'profile_sha256':sha(PROFILE_PATH.read_bytes()),'module_sha256':MODULE_SHA,
        'policy_freeze':deepcopy(freeze),'selected_at':evaluated_at,
        'source_snapshot_sha256':prediction['source_snapshot_sha256'],'static_prediction_sha256':prediction['sha256'],
        'evaluated_slots':len(ledger),'distinct_ordered_triples':len(active)*(len(active)-1)*(len(active)-2),
        'ledger':ledger,'same_set_six_orientation_comparisons':comparison,
        'exact_selected':sorted([list(x) for x in candidates],key=lambda x:tuple(map(int,x))),
        'material_exact_count':len(candidates),'original_S1_S2_unchanged':True,
        'joint_probability_or_EV_claim':False,'formal_selection_adopted':False,'registered_OOS_increment':0}


def construct(prediction, context, krs, review, s2, *, freeze, evaluated_at):
    """Preserve S2 Set floors while adding only independently reviewed Exact."""
    validate_freeze(freeze,evaluated_at)
    # A caller cannot manufacture PURCHASE by changing both summary and ledger.
    # Re-derive the complete decision from the bound, unchanged real inputs.
    verified=evaluate(prediction,context,krs,s2,freeze=freeze,evaluated_at=evaluated_at)
    require(encoded(verified)==encoded(review),'REVIEW_NOT_REPRODUCIBLE_FROM_INPUTS')
    require(review.get('profile')==PROFILE and review.get('module_sha256')==MODULE_SHA
        and review.get('profile_sha256')==sha(PROFILE_PATH.read_bytes())
        and review.get('static_prediction_sha256')==prediction['sha256']
        and review.get('source_snapshot_sha256')==prediction['source_snapshot_sha256']
        and review.get('selected_at')==evaluated_at,'REVIEW_SOURCE_PROFILE_FREEZE_MISMATCH')
    selected={tuple(t) for t in review['exact_selected']}
    terminal_set={(r['head'],r['second'],r['third']) for r in review['ledger'] if r['terminal']=='EXACT_PURCHASE'}
    require(selected==terminal_set and all(len(set(t))==3 for t in selected),'EXACT_PURCHASE_NOT_REVIEWED')
    plans=[];exact={}
    for sub in s2['known_pair_scoped_subplans']:
        h,s=sub['pair_id'].split('>');thirds={t for a,b,t in selected if (a,b)==(h,s)}
        if not thirds:continue
        request=deepcopy(sub['request']);found=set()
        for row in request['third_dispositions']:
            if row['third'] in thirds:
                row.update(status='PURCHASE',reason='EXPLICIT_UNADOPTED_EXACT_SCENARIO_ORDINAL_PAPER_SELECTION',
                    exact_rule_id=PROFILE,exact_selection_id=PROFILE+':'+h+'>'+s+'>'+row['third'])
                found.add(row['third'])
        require(found==thirds,'PAIR_LOCAL_EXACT_THIRD_LOST_IN_TRANSPORT')
        request.update(classification='NEW_UNADOPTED_EXACT_SELECTION_PAPER_NOT_FORMAL_NOT_OOS',
            exact_selection_profile=PROFILE,exact_selection_profile_sha256=review['profile_sha256'])
        plan=build_mec_plan(request,strict_head_closure=True,min_stake=100)
        proof=validate_mec_plan(plan)
        require(not plan['uncovered_active_w_heads'] and not plan['orphan_thirds'],'STRICT_MEC_CLOSURE_FAILURE')
        for row in plan['tickets']:
            if row['bet_type']=='TRIFECTA':exact[tuple(map(str,row['selection']))]=deepcopy(row)
        plans.append({'pair_id':sub['pair_id'],'strict_request':request,'strict_plan':plan,'validation':proof})
    require(set(exact)==selected,'STRICT_MEC_EXACT_TICKET_LOSS_OR_EXTRA')
    methods={}
    for method in ('EXACTA','TRIO','TRIFECTA'):
        tickets=deepcopy(s2['methods'][method]['tickets']) if method!='TRIFECTA' else [exact[t] for t in sorted(exact,key=lambda t:tuple(map(int,t)))]
        for ticket in tickets:
            ticket['canonical_ticket_id']=sha(encoded({'race_id':prediction['race_id'],'owner':prediction['model_id'],
                'revision':PROFILE,'method':method,'selection':ticket['selection'],'stake':ticket['stake']}))
        required=sum(t['stake'] for t in tickets)
        decision=resolve_capital_policy(semantic.original_request(prediction),{'minimum_required_capital':required,
            'profile':PROFILE,'sha256':sha(encoded(tickets)),'material_coverage_ratio':1.0})
        tree=render_ticket_tree({'final_ticket':{'tickets':tickets,'no_bet':not tickets},
            'capital_policy_decision':{'decision':'AKI_REFERENCE_ONLY'},'final_prediction_package':{'validation_status':'UNVALIDATED'}})
        cap=decision['capital_limit'];require(type(cap) is int,'EXISTING_HARD_BUDGET_REQUIRED')
        methods[method]={'tickets':tickets,'point_count':len(tickets),'required_MEC':required,
            'capital_policy':decision,'capital_limit':cap,'paper_notional_investment':required,
            'hypothetical_unused':max(0,cap-required),'budget_shortfall':max(0,required-cap),
            'within_existing_cap_eligible_paper_amount':required if required<=cap else 0,
            'capital_nonselected_full_paper_amount':required if required>cap else 0,
            'actual_purchase':0,'formal_selected_amount':0,'cash_unused':cap,
            'zero_reason':'NO_EXACT_ORIENTATION_PASSES_FROZEN_RULE' if not tickets and method=='TRIFECTA' else None,
            'computed_whole_race_NO_BET':False,'canonical_tree':tree['text'],
            'reflattened_tickets':tree['reflattened_tickets'],'canonical_roundtrip_verified':tree['canonical_roundtrip_verified'],
            'ticket_sha256':sha(encoded(tickets)),'tree_sha256':sha(tree['text'].encode()),
            'independent_alternative_not_pooled_purchase':True}
    simple=lambda ts:[(t['bet_type'],t['selection'],t['stake']) for t in ts]
    require(all(simple(methods[m]['tickets'])==simple(s2['methods'][m]['tickets']) for m in ('EXACTA','TRIO')),
        'S2_EXACTA_OR_TRIO_CHANGED')
    return {'profile':PROFILE,'race_id':prediction['race_id'],'methods':methods,
        'strict_MEC_exact_pair_plans':plans,'exact_selection_count':len(selected),
        'base_S2_pair_requests_SHA':sha(encoded(s2['known_pair_scoped_subplans'])),
        'all_original_S2_ordered_pairs_and_sets_preserved':True,
        'full_semantic_portfolio_required_capital':sum(x['required_MEC'] for x in methods.values()),
        'full_portfolio_is_not_pooled_purchase':True,'formal_final':False,'recipient_ACK':False,
        'new_KRS':0,'registered_OOS_increment':0,'PFS':None}

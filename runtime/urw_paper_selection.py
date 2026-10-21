"""Outcome-blind, non-Production selection experiment outside immutable MEC.

Joint *model masses* are not calibrated probabilities, prices or EV. Budget
numbers below are experimental ceilings, never a user's purchase budget.
No Runtime, signing, fitting, HTTP, settlement or Production imports here.
"""
from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
from itertools import permutations
import json
import math


POLICY = {
    'id': 'URW-PAPER-P0S1-CONDITIONAL-COVERAGE-20261021-v1',
    'classification': 'UNAPPROVED_NON_PRODUCTION_POLICY_EXPERIMENT',
    'race_cap_yen': 2000, 'day_cap_yen': 24000,
    'protection_cap_yen': 500, 'unit_yen': 100,
    'initial_research_cash_yen': 150000,
    'minimum_joint_lift_over_uniform': 1.10,
    'minimum_protection_model_lift': 1.00,
    'minimum_krs_joint_lift': 1.10,
    'minimum_marginal_fraction_of_first_gain': 0.25,
    'budget_fill_required': False,
    'price_or_ev_used': False, 'stake_optimization': False,
    'development_date_excluded_from_future_quality': '2026-10-21',
    'p1': {'history_min_mean_finish_fraction': 0.5,
           'maximum_distance_change_fraction': 0.25,
           'minimum_progression': 0.05, 'minimum_final_reserve': 0.10},
}


def sha(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def _sealed(obj):
    return {**obj, 'sha256': sha(obj)}


def _check_sha(obj):
    if obj.get('sha256') != sha({k: v for k, v in obj.items() if k != 'sha256'}):
        raise ValueError('RESEARCH_INPUT_SHA_MISMATCH')


def _key(ticket):
    bt = str(ticket['bet_type']).upper()
    ids = tuple(int(x) for x in ticket['selection'])
    return bt, tuple(sorted(ids)) if bt == 'TRIO' else ids


def canonical_tickets(tickets):
    for t in tickets:
        bt=t.get('bet_type');xs=t.get('selection');stake=t.get('stake')
        if (not isinstance(bt,str) or bt.upper() not in ('EXACTA','TRIO','TRIFECTA')
                or not isinstance(xs,(list,tuple)) or len(xs)!=(2 if bt.upper()=='EXACTA' else 3)
                or any(type(x) not in (int,str) or not str(x).isdigit() or int(x)<=0 for x in xs)
                or len(set(map(int,xs)))!=len(xs) or type(stake) is not int or stake<=0 or stake%100):
            raise ValueError('RESEARCH_SOURCE_TICKET_INVALID')
    return [{'bet_type': bt, 'selection': list(ids), 'stake': stake}
            for bt, ids, stake in sorted((*_key(t), t['stake']) for t in tickets)]


def _joint(pred):
    """Consume the existing conditional models; reject inconsistent adapters."""
    _check_sha(pred)
    ids = set(map(str, pred['ranking']))
    if len(ids) < 3 or len(ids) != len(pred['ranking']) or ids != set(pred['role_columns']):
        raise ValueError('RESEARCH_RUNNER_UNIVERSE')
    pairs = {}; triples = {}
    for rows, fields, dest in ((pred['ordered_pairs'], ('head', 'second'), pairs),
                               (pred['ordered_triples'], ('head', 'second', 'third'), triples)):
        for row in rows:
            key = tuple(str(row[k]) for k in fields); mass = row['model_mass']
            if (len(set(key)) != len(key) or not set(key) <= ids or key in dest
                    or type(mass) not in (int, float) or not math.isfinite(mass) or mass < 0):
                raise ValueError('RESEARCH_CONDITIONAL_ROW_INVALID')
            expected = pred['winner_model_mass'][key[0]] * pred['p2_model_mass_given_head'][key[0]][key[1]]
            if len(key) == 3:
                expected *= pred['p3_model_mass_given_pair']['>'.join(key[:2])][key[2]]
            if not math.isclose(expected, mass, rel_tol=1e-8, abs_tol=1e-12):
                raise ValueError('RESEARCH_CONDITIONAL_ADAPTER_DISAGREES')
            dest[key] = mass
        if not math.isclose(sum(dest.values()), 1.0, abs_tol=1e-8):
            raise ValueError('RESEARCH_JOINT_MASS_NOT_NORMALIZED')
    n = len(ids)
    if len(pairs) != n*(n-1) or len(triples) != n*(n-1)*(n-2):
        raise ValueError('RESEARCH_CONDITIONAL_UNIVERSE_INCOMPLETE')
    return ids, pairs, triples


def _validate_policy(policy):
    if policy != POLICY:
        raise ValueError('UNREGISTERED_RESEARCH_POLICY')


def _krs_support(utility, ids, prediction, source_ref):
    """Observed joint occurrence only; omitted top-list entries stay UNKNOWN."""
    out = {}; n = len(ids)
    if not utility or utility.get('krs_status') != 'EXECUTED':
        return out
    _check_sha(utility)
    if (utility.get('race_id')!=prediction['race_id'] or
            source_ref.get('krs_utility_sha256')!=utility['sha256'] or
            source_ref.get('krs_snapshot_sha256')!=sha(utility.get('snapshot')) or
            source_ref.get('krs_master_seed')!=utility.get('snapshot',{}).get('master_seed') or
            source_ref.get('krs_master_seed') is None or
            not source_ref.get('krs_input_sha256') or not source_ref.get('krs_output_file_sha256')):
        raise ValueError('RESEARCH_KRS_FROZEN_RACE_SEED_BINDING')
    for field, bt, labels in (('top_exacta_occurrence', 'EXACTA', ('W', 'P2')),
                              ('top_trifecta_occurrence', 'TRIO', ('W', 'P2', 'P3'))):
        seen = set();total_frequency=0.0
        for row in utility.get(field, []):
            order = tuple(str(row[k]) for k in labels)
            value = row['frequency']
            if (order in seen or len(set(order)) != len(order) or not set(order) <= ids
                    or type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 1):
                raise ValueError('RESEARCH_KRS_JOINT_INVALID')
            seen.add(order)
            total_frequency+=value
            if total_frequency>1+1e-9:raise ValueError('RESEARCH_KRS_JOINT_TOTAL_INVALID')
            key = _key({'bet_type': bt, 'selection': order})
            # TRIO aggregates the observed distinct permutations, without
            # inventing frequencies for orders omitted from the Engine top list.
            out[key] = out.get(key, 0.0) + value
            if bt=='TRIO':
                out[('TRIFECTA',tuple(map(int,order)))]=value
    return {k: {'observed_joint_frequency_lower_bound': v,
                'uniform_lift_lower_bound': v * (n*(n-1) if k[0] == 'EXACTA' else n*(n-1)*(n-2)/(6 if k[0]=='TRIO' else 1)),
                'omitted_orders': 'UNKNOWN_NOT_ZERO', 'probability_or_ev': False}
            for k, v in out.items()}


def select_portfolio(prediction, source_tickets, *, source_ref, policy=POLICY,
                     krs_utility=None, excluded_runner_ids=(), day_remaining_yen=None):
    """P0S1: predictions/roles/KRS fixed; select, never rewrite their semantics.

    Greedy marginal coverage of the *same ordered-triple scenario atoms*
    penalizes redundant cross-bet coverage. All six TRIO permutations are summed.
    Absolute lift and relative marginal-gain floors prevent budget backfilling.
    Protection is separately capped, needs static AND observed joint KRS support.
    """
    _validate_policy(policy)
    ids, pairs, triples = _joint(prediction)
    excluded = set(map(str, excluded_runner_ids))
    if not excluded <= ids:raise ValueError('RESEARCH_EXCLUSION_UNIVERSE')
    remaining = policy['day_cap_yen'] if day_remaining_yen is None else day_remaining_yen
    if type(remaining) is not int or remaining < 0 or remaining % 100:
        raise ValueError('RESEARCH_DAY_BUDGET_INVALID')
    budget = min(policy['race_cap_yen'], remaining)
    core_budget = min(budget, policy['race_cap_yen']-policy['protection_cap_yen'])
    n = len(ids); support = _krs_support(krs_utility, ids, prediction, source_ref)
    candidates = []; seen = set()
    for ticket in canonical_tickets(source_tickets):
        key = _key(ticket); bt, numbers = key; order = tuple(map(str, numbers))
        if (key in seen or bt not in ('EXACTA','TRIO','TRIFECTA')
                or len(order)!=(2 if bt=='EXACTA' else 3) or len(set(order))!=len(order)
                or not set(order)<=ids or type(ticket['stake']) is not int
                or ticket['stake']<=0 or ticket['stake']%100):
            raise ValueError('RESEARCH_SOURCE_TICKET_INVALID')
        seen.add(key)
        atoms = ({k for k in triples if k[:2]==order} if bt=='EXACTA' else
                 set(permutations(order)) if bt=='TRIO' else {order})
        mass = sum(triples[k] for k in atoms)
        uniform = (1/(n*(n-1)) if bt=='EXACTA' else (6 if bt=='TRIO' else 1)/(n*(n-1)*(n-2)))
        candidates.append({'ticket':ticket,'atoms':atoms,'model_mass':mass,'lift':mass/uniform,
                           'krs':support.get(key),'excluded':bool(set(order)&excluded)})
    chosen = {}; covered = set(); first_gain = None
    for tier, cap in (('CORE',core_budget),('PROTECTION',min(policy['protection_cap_yen'],budget-core_budget))):
        spent = 0
        while spent + policy['unit_yen'] <= cap:
            options = []
            for row in candidates:
                key = _key(row['ticket'])
                if key in chosen or row['excluded']:continue
                eligible = (row['lift'] >= policy['minimum_joint_lift_over_uniform'] if tier=='CORE' else
                            row['lift'] >= policy['minimum_protection_model_lift'] and row['krs'] is not None
                            and row['krs']['uniform_lift_lower_bound'] >= policy['minimum_krs_joint_lift'])
                if not eligible:continue
                gain = sum(triples[a] for a in row['atoms']-covered)
                if gain<=0 or (first_gain is not None and gain < first_gain*policy['minimum_marginal_fraction_of_first_gain']):
                    continue
                options.append((gain, key, row))
            if not options:break
            gain, key, row = sorted(options,key=lambda x:(-x[0],x[1]))[0]
            if first_gain is None:first_gain=gain
            chosen[key]={'tier':tier,'marginal_model_coverage':gain,
                         'reason':'CONDITIONAL_JOINT_MARGINAL_COVERAGE' if tier=='CORE' else 'STATIC_AND_JOINT_KRS_SUPPORT',
                         'stake':policy['unit_yen']}
            covered |= row['atoms'];spent += policy['unit_yen']
    ledger=[]; selected=[]
    for row in candidates:
        key=_key(row['ticket']);pick=chosen.get(key)
        if pick:
            selected.append({**row['ticket'],'stake':policy['unit_yen']})
            reason=pick['reason']
        else:
            reason=('EXPLICIT_SCRATCH_OR_EXCLUSION' if row['excluded'] else
                    'BELOW_STATIC_LIFT_AND_NO_CORROBORATED_PROTECTION' if row['lift']<policy['minimum_joint_lift_over_uniform']
                    and not (row['krs'] and row['lift']>=policy['minimum_protection_model_lift']
                             and row['krs']['uniform_lift_lower_bound']>=policy['minimum_krs_joint_lift']) else
                    'REDUNDANT_LOW_MARGINAL_GAIN_OR_FIXED_TIER_BUDGET')
        ledger.append({'original_ticket':row['ticket'],'selected':bool(pick),'reason':reason,
                       'selection_detail':pick,'conditional_model_mass':row['model_mass'],
                       'joint_lift_over_uniform_not_ev':row['lift'],'krs_joint_support':row['krs'],
                       'ordered_scenario_count':len(row['atoms']),
                       'input_ref':source_ref})
    source_atoms=set().union(*(r['atoms'] for r in candidates)) if candidates else set()
    spent=len(selected)*policy['unit_yen']
    created=datetime.now(timezone.utc)
    temporal=('POSTHOC_DEVELOPMENT_NOT_PRESTART' if created>=datetime.fromisoformat(prediction['prediction_cutoff']) else
              'FORWARD_RESEARCH_PENDING_INDEPENDENT_ANCHOR')
    return _sealed({'classification':temporal,'created_at':created.isoformat(),'forward_oos_credit':0,
        'race_id':prediction['race_id'],'prediction_sha256':prediction['sha256'],
        'source_candidates_ref':copy.deepcopy(source_ref),'source_candidates_sha256':sha(canonical_tickets(source_tickets)),
        'policy':copy.deepcopy(policy),'policy_sha256':sha(policy),
        'input_sha256':sha({'prediction':prediction,'source_tickets':canonical_tickets(source_tickets),
                            'source_ref':source_ref,'krs':krs_utility,'excluded':sorted(excluded),
                            'day_remaining_yen':remaining}),
        'consumed':{'ordered_pair_mass':True,'conditional_third_mass':True,
                    'trio_distinct_permutations_summed':6,'ranking_only_does_not_force_ticket_change':True,
                    'krs':bool(support),'krs_input_sha256':sha(krs_utility) if krs_utility else None,
                    'krs_incremental_value':'UNMEASURED_REQUIRES_SEPARATE_RESULT_PASS'},
        'selected_tickets':canonical_tickets(selected),'candidate_ledger':ledger,
        'race_budget_yen':budget,'used_budget_yen':spent,'unused_budget_yen':budget-spent,
        'day_budget_remaining_yen':remaining-spent,
        'tier_spend_yen':{tier:sum(x['stake'] for x in chosen.values() if x['tier']==tier) for tier in ('CORE','PROTECTION')},
        'coverage':{'source_ordered_scenarios':len(source_atoms),'protected_ordered_scenarios':len(covered),
                    'lost_ordered_scenarios':len(source_atoms-covered),
                    'source_model_mass':sum(triples[x] for x in source_atoms),
                    'protected_model_mass':sum(triples[x] for x in covered),
                    'lost_model_mass':sum(triples[x] for x in source_atoms-covered),
                    'is_material_coverage_100_percent':False,'original_mec_unchanged':True},
        'no_bet':not selected,'no_bet_reason':'NO_QUALIFIED_NONREDUNDANT_TICKET_WITHIN_RESEARCH_CAP' if not selected else None,
        'calibrated_probability':False,'ev_claim':False,'production_authority':False,
        'signed_final_claim':False,'actual_purchase':False,
        'private_storage_required':True,'public_redistribution_authorized':False})


def p1_role_hypotheses(prediction, feature_pack, observation, *, policy=POLICY):
    """Limited, pre-evidence-conditioned Role experiment, not a fitted model.

    Keep ranking and conditional values unchanged. Unknown is neither a penalty
    nor a sufficient reason for admission. Every runner gets the same review.
    Context-qualified history AND observed path support are both required.
    Class/venue translation remains UNKNOWN unless already witnessed.
    """
    _validate_policy(policy);_joint(prediction);_check_sha(feature_pack)
    if (prediction['feature_sha256']!=feature_pack['sha256'] or
            observation['source']['raw_sha256']!=feature_pack['source_snapshot_sha256']):
        raise ValueError('RESEARCH_P1_SOURCE_FEATURE_BINDING')
    from runtime.urw_nankan_reference_source import verify_history_asof
    observed=observation['source'].get('fetched_at')
    if (not observed or datetime.fromisoformat(observed)!=datetime.fromisoformat(feature_pack['source_observed_at'])):
        raise ValueError('RESEARCH_P1_SOURCE_OBSERVATION_TIME_BINDING')
    verify_history_asof(observation['facts'],observed)
    pred=copy.deepcopy(prediction);original_roles=copy.deepcopy(pred['role_columns']);review=[]
    facts={str(x['runner_id']):x for x in observation['facts']}
    if set(facts)!=set(original_roles):raise ValueError('RESEARCH_P1_FULL_UNIVERSE')
    def ranks(values):return sorted(values,key=lambda x:(-values[x],int(x)))
    initial_w=[x for x,rs in original_roles.items() if 'W' in rs]
    initial_pairs=[(h,s) for h in initial_w for s,rs in original_roles.items() if 'P2' in rs and h!=s]
    for rid in sorted(facts,key=int):
        row=feature_pack['runners'][rid];fact=facts[rid];evidence=[];compatible=[]
        for start in fact.get('starts',[]):
            dt=str(start.get('date',''))
            try:past=datetime.strptime(dt,'%y.%m.%d').date()
            except ValueError:raise ValueError('RESEARCH_P1_HISTORY_DATE')
            if past>=datetime.fromisoformat(feature_pack['race_date']).date():
                raise ValueError('RESEARCH_P1_POST_RESULT_HISTORY_FORBIDDEN')
            distance=start.get('distance');finish=start.get('finish');field=start.get('field_size')
            if (start.get('surface')=='DIRT' and type(distance) is int
                    and abs(distance-observation['race']['distance'])/observation['race']['distance']<=policy['p1']['maximum_distance_change_fraction']
                    and type(finish) is int and type(field) is int and 1<=finish<=field and field>1):
                compatible.append(start)
        fractions=[(s['field_size']-s['finish'])/(s['field_size']-1) for s in compatible]
        history=bool(fractions and sum(fractions)/len(fractions)>=policy['p1']['history_min_mean_finish_fraction']
                     and any(s['finish']<=3 for s in compatible))
        progression=row.get('STAGE:progression');reserve=row.get('STAGE:final_reserve')
        path=((progression is not None and progression>=policy['p1']['minimum_progression'])
              or (reserve is not None and reserve>=policy['p1']['minimum_final_reserve']))
        if history:evidence.append({'family':'CONTEXT_QUALIFIED_FINISH_HISTORY',
                                    'provider_race_ids':[s.get('provider_race_id') for s in compatible]})
        if path:evidence.append({'family':'OBSERVED_PATH_PROGRESSION_OR_RESERVE',
                                'progression':progression,'final_reserve':reserve})
        eligible=history and path and fact.get('status')=='ACTIVE_DECLARED'
        roles=[]
        if eligible:
            if (set(original_roles[rid])&{'P2','P3'} and pred['winner_model_mass'][rid]>=1/len(facts)):
                roles.append('W')
            if any(rid!=h and ranks(pred['p2_model_mass_given_head'][h]).index(rid)<pred['role_widths']['P2'] for h in initial_w):
                roles.append('P2')
            if any(rid not in (h,s) and ranks(pred['p3_model_mass_given_pair'][h+'>'+s]).index(rid)<pred['role_widths']['P3'] for h,s in initial_pairs):
                roles.append('P3')
        added=[r for r in roles if r not in original_roles[rid]]
        pred['role_columns'][rid]=[r for r in ('W','P2','P3') if r in set(original_roles[rid]+added)]
        review.append({'runner_id':rid,'original_roles':original_roles[rid],'added_roles':added,
                       'evidence_families':evidence,'source_raw_sha256':feature_pack['source_snapshot_sha256'],
                       'feature_pack_sha256':feature_pack['sha256'],'eligible':eligible,
                       'reason':'MULTI_EVIDENCE_AND_CONDITIONAL_SUPPORT' if added else
                                'NO_NEW_ROLE_QUALIFIED_OR_ALREADY_PRESENT',
                       'unknown_only_effect':'NONE','class_translation':'NO_NEW_COEFFICIENT_UNSUPPORTED_CONTEXT_REMAINS_UNKNOWN'})
    pred['role_widths']={r:sum(r in rs for rs in pred['role_columns'].values()) for r in ('W','P2','P3')}
    pred['research_parent_prediction_sha256']=prediction['sha256']
    pred['research_role_policy_sha256']=sha(policy['p1'])
    created=datetime.now(timezone.utc)
    pred['frozen_at']=pred['compiled_at']=created.isoformat()
    pred['temporal_class']='POSTHOC_ROLE_HYPOTHESIS_NOT_PRESTART' if created>=datetime.fromisoformat(pred['prediction_cutoff']) else 'FORWARD_RESEARCH_ROLE_HYPOTHESIS'
    pred.pop('sha256');pred=_sealed(pred)
    return _sealed({'prediction':pred,'all_runner_review':review,'ranking_changed':False,
                    'model_refitted':False,'role_policy_changed':True,'production_authority':False,
                    'private_storage_required':True,'public_redistribution_authorized':False})

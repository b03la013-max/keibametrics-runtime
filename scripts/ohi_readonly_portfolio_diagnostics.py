"""Outcome-blind OHI portfolio frontiers from immutable private originals.

This is a retrospective diagnostic, not a new selector or a buy instruction.
Every prefix is retained; no result-dependent prefix/model is chosen. The
Candidate's existing conditional masses are used directly, never SSR products.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import copy
import hashlib
from itertools import combinations, permutations
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'runtime')]
from runtime.ohi_single_race_research import readback, private_root

SCHEMA = 'OHI-READONLY-PORTFOLIO-DIAGNOSTICS-v1-20261026'


def sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


def key(ticket):
    kind = ticket['bet_type'].upper()
    ids = tuple(str(x) for x in ticket['selection'])
    if kind not in ('EXACTA', 'TRIO', 'TRIFECTA') or len(ids) != (2 if kind == 'EXACTA' else 3):
        raise ValueError('DIAGNOSTIC_TICKET_SHAPE')
    if len(set(ids)) != len(ids):
        raise ValueError('DIAGNOSTIC_SELF_COMBINATION')
    if kind == 'TRIO':
        ids = tuple(sorted(ids, key=int))
    return kind + ':' + '>'.join(ids)


def validate_tickets(tickets, universe):
    seen = set()
    for t in tickets:
        k = key(t)
        if k in seen or any(str(i) not in universe for i in t['selection']):
            raise ValueError('DIAGNOSTIC_DUPLICATE_OR_UNKNOWN_RUNNER')
        if type(t['stake']) is not int or t['stake'] != 100:
            raise ValueError('DIAGNOSTIC_REQUIRES_FROZEN_100_YEN_UNIT')
        seen.add(k)
    return seen


def conditional_scores(prediction):
    """Sum existing ordered permutations for TRIO; no marginal independence."""
    if 'ordered_pairs' not in prediction or 'ordered_triples' not in prediction:
        return None
    values = defaultdict(float)
    for row in prediction['ordered_pairs']:
        value = row['model_mass']
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            raise ValueError('DIAGNOSTIC_MODEL_MASS_INVALID')
        values[key({'bet_type':'EXACTA','selection':[row['head'],row['second']]})] = value
    for row in prediction['ordered_triples']:
        value = row['model_mass']
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            raise ValueError('DIAGNOSTIC_MODEL_MASS_INVALID')
        ids = [row['head'], row['second'], row['third']]
        values[key({'bet_type':'TRIFECTA','selection':ids})] = value
        values[key({'bet_type':'TRIO','selection':ids})] += value
    return dict(values)


def prefix_orders(original, owner):
    """Result-independent orderings; the full source semantic remains intact."""
    portfolio = original['portfolios'][owner]
    tickets = copy.deepcopy(portfolio['mec']['tickets'])
    universe = {str(x['runner_id']) for x in original['all_runners']}
    validate_tickets(tickets, universe)
    orders = {'EXISTING_MEC_ORDER_PREFIX_DIAGNOSTIC': [key(t) for t in tickets]}
    scores = conditional_scores(original['owners'][owner])
    if scores is not None:
        # These are uncalibrated event model masses, NOT EV or odds-aware value.
        # Cross-bet-type value comparability remains unknown without prices.
        missing = [key(t) for t in tickets if key(t) not in scores]
        if missing:
            raise ValueError('DIAGNOSTIC_CONDITIONAL_MASS_MISSING')
        orders['EXISTING_CONDITIONAL_MODEL_MASS_PREFIX_DIAGNOSTIC'] = sorted(
            orders['EXISTING_MEC_ORDER_PREFIX_DIAGNOSTIC'], key=lambda k:(-scores[k], k))
    return tickets, orders, scores


def top4_reference(original, owner):
    ids = [str(x) for x in original['owners'][owner]['ranking'][:4]]
    return ([{'bet_type':'EXACTA','selection':list(pair),'stake':100,
              'research_additional_reason':'EXPLICIT_TOP4_DIAGNOSTIC_REFERENCE_NOT_OWNER_POLICY'}
             for pair in permutations(ids, 2)] +
            [{'bet_type':'TRIO','selection':list(trio),'stake':100,
              'research_additional_reason':'EXPLICIT_TOP4_DIAGNOSTIC_REFERENCE_NOT_OWNER_POLICY'}
             for trio in combinations(ids, 3)])


def outcome(tickets, result):
    """Read-only payout labels only; formal Settlement stays in existing code.

    Required input: winning_selections[bet_type] list of selection and positive
    integer payout_per_100. Special refunds/voids require the existing admitted
    settlement and are deliberately NOT zero-filled here.
    """
    investment = sum(t['stake'] for t in tickets)
    empty = {'investment':investment,'return':None,'profit_loss':None,'pfs':None,
             'winning_ticket_keys':None,'maximum_ticket_return':None}
    if result is None:
        return {**empty,'status':'RESULT_NOT_PROVIDED'}
    if result.get('void') or result.get('refund_runner_ids') or result.get('refunds'):
        return {**empty,'status':'SPECIAL_RESULT_REQUIRES_EXISTING_SETTLEMENT'}
    payouts = result.get('winning_selections')
    if not isinstance(payouts, dict) or result.get('payouts_complete') is not True:
        return {**empty,'status':'PAYOUTS_INCOMPLETE_NOT_ZERO'}
    winning = {}
    for kind, rows in payouts.items():
        for row in rows:
            k = key({'bet_type':kind,'selection':row['selection']})
            amount = row['payout_per_100']
            if type(amount) is not int or amount <= 0 or k in winning:
                raise ValueError('DIAGNOSTIC_WINNING_PAYOUT_INVALID_OR_DUPLICATE')
            winning[k] = amount
    for kind in {t['bet_type'] for t in tickets}:
        if kind not in payouts or not payouts[kind]:
            return {**empty,'status':'WINNING_PAYOUT_TYPE_MISSING'}
    returns = {key(t):winning[key(t)] * (t['stake']//100)
               for t in tickets if key(t) in winning}
    returned = sum(returns.values())
    return {'status':'RESEARCH_LABEL_EVALUATED_NOT_SIGNED_SETTLEMENT',
            'result_evidence_status':result.get('verification_status','UNVERIFIED'),
            'investment':investment,'return':returned,'profit_loss':returned-investment,
            'pfs':returned/investment*100 if investment else None,
            'winning_ticket_keys':sorted(returns),'maximum_ticket_return':max(returns.values(),default=0)}


def frontier(tickets, order, budget, result=None, *, frozen_winning_keys=None):
    by_key = {key(t):t for t in tickets}
    if len(order) != len(by_key) or set(order) != set(by_key):
        raise ValueError('DIAGNOSTIC_ORDER_UNIVERSE_MISMATCH')
    all_units = {u for t in tickets for u in t.get('coverage_ids', [])}
    counts = list(range(0, min(len(order), budget//100)+1))
    if len(order) not in counts:
        counts.append(len(order))
    points = []
    for n in counts:
        selected = [by_key[k] for k in order[:n]]
        covered = {u for t in selected for u in t.get('coverage_ids', [])}
        evaluated = outcome(selected,result)
        winning = evaluated['winning_ticket_keys']
        points.append({'prefix_length':n,'selected_ticket_count':n,
            'nonselected_ticket_count':len(order)-n,
            'selected_keys_sha256':sha(order[:n]),
            'source_candidate_coverage_ratio':n/len(order) if order else None,
            'covered_material_unit_count':len(covered),
            'lost_material_unit_count':len(all_units-covered),
            'lost_material_unit_ids_sha256':sha(sorted(all_units-covered)),
            'material_unit_coverage_ratio':len(covered)/len(all_units) if all_units else None,
            'used_budget':n*100,'unused_budget':max(0,budget-n*100),
            'within_fixed_10000_yen_cap':n*100<=budget,
            'no_forced_fill':True,
            'selection_reason':'EXACT_PREFIX_OF_DISCLOSED_RESULT_BLIND_ORDER',
            'nonselection_reason':'AFTER_PREFIX_END_NOT_DELETED_FROM_SEMANTIC',
            'preserved_frozen_winning_keys':sorted(set(winning)&set(frozen_winning_keys))
                if winning is not None and frozen_winning_keys is not None else None,
            'lost_frozen_winning_keys':sorted(set(frozen_winning_keys)-set(winning))
                if winning is not None and frozen_winning_keys is not None else None,
            'evaluation':evaluated})
    return {'full_ordered_source_candidate_keys':order,'all_source_material_unit_ids':sorted(all_units),
            'all_prefixes_retained':True,
            'chosen_prefix':None,'purchase_policy':False,'frontier':points}


def prestart_evidence_diagnostics(original, feature_pack):
    features = (feature_pack or {}).get('runners', {})
    rows = []
    for horse in original['all_runners']:
        rid = str(horse['runner_id']);cells = original['numerical_cells'][rid]
        values = features.get(rid, {})
        rows.append({'runner_id':rid,'provider_horse_id':horse['provider_horse_id'],
            'name':horse['name'],'source_snapshot_sha256':original['source_sha256'],
            'history_count':len(horse['starts']),
            'observed_sire_dam_damsire':{k:horse.get(k) for k in ('sire','dam','damsire')},
            'terminal_status_by_index':{k:v['terminal_status'] for k,v in cells.items()},
            'neutral_reason_by_index':{k:{'fallback_value':v['value'],
                'missing_components':[{'component':c.get('component'),'rule_id':c.get('rule_id'),
                    'score':c.get('score'),'evidence_refs':c.get('evidence_refs',[]),
                    'native_component_record':copy.deepcopy(c)}
                    for c in v.get('components',[]) if c.get('missing')],
                'all_components_unknown':v.get('all_components_unknown')}
                for k,v in cells.items() if v['terminal_status']=='RULED-NEUTRAL'},
            'observed_feature_values':{k:v for k,v in values.items() if v is not None},
            'unknown_feature_names':[k for k,v in values.items() if v is None],
            'current_condition_observation':{k:horse.get(k) for k in
                ('current_load','current_body_weight','current_body_weight_change','frame_no')},
            'victory_path_classification':'INSUFFICIENT_EVIDENCE',
            'classification_basis':'NO_REGISTERED_IDENTIFIABLE_ABILITY_VS_ENVIRONMENT_MODEL_OR_CAUSAL_LABEL; NO_POSTRESULT_CAUSE_INFERRED',
            'unknown_is_weak':False})
    return rows


def summarize_evaluations(rows, initial_capital=120000):
    complete = [r for r in rows if r['return'] is not None]
    all_complete = len(rows)==len(complete)
    stake = sum(r['investment'] for r in rows)
    returned = sum(r['return'] for r in complete)
    balance = peak = initial_capital; dd = 0
    for row in complete:
        balance += row['return']-row['investment'];peak=max(peak,balance);dd=max(dd,peak-balance)
    largest = max((r['return'] for r in complete),default=0)
    largest_ticket = max((r['maximum_ticket_return'] for r in complete),default=0)
    return {'fixed_denominator':len(rows),'settled_label_count':len(complete),
        'investment':stake,'return':returned if all_complete else None,
        'profit_loss':returned-stake if all_complete else None,
        'pfs':100*returned/stake if stake and all_complete else None,
        'max_drawdown':dd if all_complete else None,
        'initial_capital_reference':initial_capital,
        'initial_capital_is_research_accounting_reference_not_owner_budget':True,
        'final_balance':balance if all_complete else None,
        'maximum_race_return':largest if all_complete else None,
        'largest_race_share_of_return':largest/returned if returned and all_complete else None,
        'pfs_with_largest_race_return_zeroed_stake_retained':100*(returned-largest)/stake if stake and all_complete else None,
        'pfs_with_largest_ticket_return_zeroed_stake_retained':100*(returned-largest_ticket)/stake if stake and all_complete else None,
        'participation':sum(r['investment']>0 for r in rows),
        'hit_but_loss':sum(0<r['return']<r['investment'] for r in complete),
        'no_bet':sum(r['investment']==0 for r in rows)}


def diagnose(original, feature_pack=None, result=None):
    before = sha(original)
    if original.get('production_authority') is not False or original.get('registered_oos_credit') != 0:
        raise ValueError('DIAGNOSTIC_NONPRODUCTION_ORIGINAL_REQUIRED')
    if result is not None and result.get('provider_race_id') != original['race']['provider_race_id']:
        raise ValueError('DIAGNOSTIC_OTHER_RACE_RESULT')
    output = {'race':copy.deepcopy(original['race']),'input_prediction_sha256':original['sha256'],
        'input_source_sha256':original['source_sha256'],'freeze_at':original['freeze_at'],
        'victory_path_evidence':prestart_evidence_diagnostics(original,feature_pack),
        'owners':{},'positive_control':original['race']['race_no'] in (8,11,12)}
    for owner, pred in original['owners'].items():
        port = original['portfolios'][owner];tickets, orders, scores = prefix_orders(original,owner)
        top = top4_reference(original,owner)
        validate_tickets(top,{str(x['runner_id']) for x in original['all_runners']})
        conditional = {'available':scores is not None,
            'actually_consumed_by_frozen_selection':False,
            'frozen_selection_basis':port['selection_semantics'],
            'head_conditioned_p2':pred.get('p2_model_mass_given_head'),
            'pair_conditioned_p3':pred.get('p3_model_mass_given_pair'),
            'score_meaning':'EXISTING_UNCALIBRATED_CONDITIONAL_MODEL_MASS_NOT_EV',
            'ticket_model_mass':scores,
            'trio_method':'SUM_EXISTING_ORDERED_TRIPLE_MASSES_OF_ALL_MATCHING_PERMUTATIONS',
            'probability_calibration':'UNPROVEN','market_value':'UNKNOWN'}
        frozen_evaluation=outcome(port['tickets'],result)
        output['owners'][owner] = {
            'source_semantic_sha256':sha(port['semantic_request']),
            'source_mec_sha256':port['mec']['sha256'],
            'source_candidate_tickets':tickets,
            'minimum_required_capital':port['mec']['minimum_required_capital'],
            'capital_limit':port['capital']['capital_limit'],
            'capital_excess':max(0,port['mec']['minimum_required_capital']-port['capital']['capital_limit']),
            'frozen_selected_ticket_keys':[key(t) for t in port['tickets']],
            'frozen_selected_evaluation':frozen_evaluation,
            'all_mec_candidate_evaluation':outcome(tickets,result),
            'conditional_information':conditional,
            'prefix_comparisons':{name:frontier(tickets,order,10000,result,
                frozen_winning_keys=frozen_evaluation['winning_ticket_keys']) for name,order in orders.items()},
            'top4_reference':{'tickets':top,'evaluation':outcome(top,result),
                'explicit_research_addition_keys':sorted({key(t) for t in top}-{key(t) for t in tickets}),
                'selected_as_best_method':False},
            'ev':'UNKNOWN_NOT_CALIBRATED_NO_DECISION_TIME_BET_TYPE_PRICES',
            'krs_purchase_effect':{'actual_consumption':False,'incremental_selected_tickets':0,
                'incremental_stake':0,'counterfactual_utility':'NOT_IDENTIFIED_BY_UNUSED_AUDIT_OUTPUT'},
        }
    if before != sha(original):
        raise ValueError('DIAGNOSTIC_MUTATED_ORIGINAL')
    return output


def run(root, results=None):
    root=Path(root);races=[];file_proofs=[]
    for number in range(1,13):
        folder=root/('live-r01-v1' if number==1 else f'live-r{number:02d}-v2')
        original,_=readback(folder)
        feature=json.loads((folder/'features.json').read_text())
        result=(results or {}).get('races',{}).get(str(number))
        races.append(diagnose(original,feature,result))
        file_proofs.append({'race_no':number,'prediction_sha256':original['sha256'],
            'source_sha256':original['source_sha256'],
            'original_file_sha256':hashlib.sha256((folder/'prediction-original.json').read_bytes()).hexdigest()})
    owners={}
    for owner in races[0]['owners']:
        owners[owner]=summarize_evaluations([r['owners'][owner]['frozen_selected_evaluation'] for r in races])
    common=min(o['investment'] for o in owners.values())
    analytical={}
    for owner, row in owners.items():
        factor=common/row['investment'] if row['investment'] else None
        analytical[owner]={'common_budget':common,'factor':factor,
            'analytical_return':row['return']*factor if factor is not None and row['return'] is not None else None,
            'actual_100_yen_reconstructible':factor is not None and float(factor).is_integer(),
            'reselection':False,'interpretation':'LINEAR_NORMALIZATION_OF_FROZEN_ARMS_NOT_CONSTRUCTED_TICKETS'}
    neutral=Counter(index for r in races for horse in r['victory_path_evidence']
                    for index,status in horse['terminal_status_by_index'].items() if status=='RULED-NEUTRAL')
    return {'schema':SCHEMA,'classification':'POSTRESULT_READONLY_DIAGNOSTIC_NOT_FORWARD',
        'production_authority':False,'actual_purchase':False,'new_oos_credit':0,
        'new_model_or_selection_policy':False,'chosen_prefix_or_winning_method':None,
        'source_originals':file_proofs,'races':races,'frozen_arm_summary':owners,
        'equal_budget_analytical_only':analytical,'neutral_counts_by_index':dict(neutral),
        'victory_path_classification_counts':{'INSUFFICIENT_EVIDENCE':sum(len(r['victory_path_evidence']) for r in races)},
        'all_final_evaluation_uses_same_fixed_12_races':True,
        'p1_p2_boundaries':{'P1_01_05':'EVIDENCE_REPORTED_CAUSAL_WIN_PATH_UNIDENTIFIED_NO_THRESHOLD_ADDED',
            'P1_06':'ZERO_HISTORY_AND_MISSINGNESS_STRATIFIED_NO_UNKNOWN_PENALTY_ADDED',
            'P1_07_12':'ROLE_AND_CONDITIONAL_MODEL_MASS_AUDIT_ONLY_NO_ROLE_WIDTH_CHANGE',
            'P1_13_18':'FULL_RESULT_BLIND_PREFIX_FRONTIERS_NOT_NEW_PURCHASE_POLICY',
            'P2_01_06':'FROZEN_EVIDENCE_ONLY_NO_LATER_WEIGHT_TRACK_OR_BLOODLINE_COHORT_BACKFILL',
            'P2_07_10':'KRS_NOT_CONSUMED_BY_FROZEN_SELECTION_EV_AND_CALIBRATION_UNPROVEN',
            'P2_11_12':'FIXED_COHORT_COST_AND_OPPORTUNITY_DIAGNOSTICS_NO_CORRECT_ONE_TICKET_REPLAY',
            'P2_13_15':'NO_OOS_REGISTRATION_OR_PRODUCTION_PROMOTION_BY_THIS_SCRIPT'}}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--original-root',required=True)
    p.add_argument('--results-json')
    p.add_argument('--output',required=True)
    a=p.parse_args();output=private_root(a.output)
    if output.exists():raise ValueError('DIAGNOSTIC_REVISION_ALREADY_EXISTS')
    results=json.loads(Path(a.results_json).read_text()) if a.results_json else None
    report=run(a.original_root,results)
    output.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    output.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'output':str(output),'sha256':sha(report),'races':len(report['races']),
                      'frozen_arms':report['frozen_arm_summary']},ensure_ascii=False))


if __name__=='__main__':main()

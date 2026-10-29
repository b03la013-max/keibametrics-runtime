"""Read-only payable-order sensitivity; never resolves a canonical RESULT hold.

Official paid TRIFECTA orders are scenarios, not unique finish assignments.
Keep their metrics separate from the original unique-order daily cohort.
"""
from copy import deepcopy
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'runtime')]
from jra_full_day_postrace_review import parse_official, prediction, settle_tickets
from jra_krs_utility_measurement import evaluate_against_result


def review(final, official):
    if not official.get('top3_display_order_is_not_unique'):
        raise ValueError('DEAD_HEAT_REQUIRED')
    orders = [p['selection'] for p in official['payouts']['TRIFECTA']]
    if not orders or any(len(o) != 3 or len(set(o)) != 3 for o in orders):
        raise ValueError('PAYABLE_ORDERS_INVALID')
    scenarios = []
    for order in orders:
        local = deepcopy(official)
        local['top3'] = order
        local['top3_display_order_is_not_unique'] = False
        p = prediction(final, local)
        k = evaluate_against_result(
            final['krs_prediction_utility'], order,
            static_ranking=final['static_prediction']['ranking'],
            static_roles=final['static_prediction']['roles'])
        scenarios.append({'payable_order': order, 'prediction': p, 'krs': k})
    keys = ['W', 'P2', 'P3', 'ordered_pair', 'pair_conditioned_third', 'ordered_exact']
    bounds = {k: {'any_payable_order': any(s['prediction'][k] for s in scenarios),
                  'all_payable_orders': all(s['prediction'][k] for s in scenarios)} for k in keys}
    return {'race_id': final.get('race_id'), 'status': 'ANALYSIS ONLY',
            'canonical_result_status': 'PENDING EXISTING MANUAL ADJUDICATION',
            'cohort_effect': 'NONE; daily unique-order denominator unchanged',
            'definition': 'Each official paid TRIFECTA selection is evaluated separately. '
                          'Any/all bounds are sensitivity diagnostics, not a unique P2/P3 result.',
            'scenarios': scenarios, 'capture_bounds': bounds,
            'settlement': settle_tickets(final['final_ticket']['tickets'], official),
            'production_effect': 'NONE'}


def main():
    rid = 'KM-JRA-KYO-20261017-R12'
    fp = ROOT / 'runtime/final_artifacts' / (rid + '.json')
    hp = ROOT / 'evidence/jra_day_review_20261017/official/082026040612.html'
    final = json.loads(fp.read_text())
    official = parse_official(hp.read_text(), '2026-10-17', 'KYO', 12)
    report = review(final, official)
    report['inputs'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in [fp, hp]}
    out = ROOT / 'runtime/daily_reviews/JRA-2026-10-17/dead_heat_review.json'
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()

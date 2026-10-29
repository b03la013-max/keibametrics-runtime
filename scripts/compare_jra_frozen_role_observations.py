"""Five measurement lanes on the same 19 frozen races; no ticket invention.

The full KRS-proposal union is a new POST-RESULT diagnostic comparator only.
It has no forward registration or activation. The one-per-column candidate and
all frozen definitions are imported without modification. Pair/Exact/PFS are
undefined when a lane has no frozen decision/tickets for those metrics.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
from jra_role_rescue_shadow import build_role_rescue_shadow
D = ROOT / 'runtime/daily_reviews/JRA-2026-10-17'


def load(p):
    return json.loads((ROOT / p).read_text())


def columns(static):
    return {c: {str(h) for h, roles in static['roles'].items() if c in roles} for c in ('W', 'P2', 'P3')}


def added(base, proposals):
    out = {c: set(h) for c, h in base.items()}
    for p in proposals:
        for c in out:
            if p['proposal'] == 'ADD_' + c + '_SHADOW':
                out[c].add(str(p['horse_no']))
    return out


def main():
    audit = load(D / 'audit_ledger.json')
    capital = load(D / 'capital_research_comparison.json')
    rows = []
    for r in audit['races']:
        if (r.get('settlement') or {}).get('investment', 0) <= 0:
            continue
        f = load(r['artifact_refs']['final']); req = load(r['artifact_refs']['request'])
        src = load(r['artifact_refs']['source'])['artifact']
        base = columns(f['static_prediction'])
        role_shadow = build_role_rescue_shadow(f)
        proposals = f['krs_prediction_utility']['actionable_role_proposals']
        market = sorted(src['jra_official_market_observation']['runners'], key=lambda h: (h.get('popularity_rank') or 999, int(h['horse_no'])))
        top = {str(h['horse_no']) for h in market[:3] if h.get('popularity_rank')}
        assert len(top) == 3
        arms = {'STATIC_ONLY_FROZEN_ROLES': base,
                'STATIC_PLUS_KRS_OBSERVATIONAL_UNION': added(base, proposals),
                'PRODUCTION_AKI': {c: set(map(str, req['aki_column_selection']['columns'][c])) for c in base},
                'REGISTERED_ONE_PER_COLUMN_ROLE_RESCUE': added(base, role_shadow['selected_proposals']),
                'MARKET_TOP3_BOX_ROLE_UNIVERSE': {c: top for c in base}}
        actual = list(map(str, r['official_result']['top3']))
        for name, cols in arms.items():
            capture = {c: actual[i] in cols[c] for i, c in enumerate(base)}
            ambiguous = r['official_result']['top3_display_order_is_not_unique']
            if ambiguous:
                capture['P2'] = capture['P3'] = 'PENDING_CANONICAL_DEAD_HEAT_RESULT'
            downstream = name in ('STATIC_ONLY_FROZEN_ROLES', 'PRODUCTION_AKI')
            cash_arm = 'A_CURRENT_PRODUCTION' if name == 'PRODUCTION_AKI' else 'E_SOURCE_MARKET_TOP3_BOX' if name == 'MARKET_TOP3_BOX_ROLE_UNIVERSE' else None
            cash = next((x for x in capital['rows'] if x['race_id'] == r['race_id'] and x['arm'] == cash_arm), None)
            rows.append({'race_id': r['race_id'], 'arm': name, 'source_snapshot_sha256': req['source_snapshot_sha256'],
                'prediction_cutoff': req['prediction_cutoff'], 'columns': {c: sorted(h, key=int) for c, h in cols.items()},
                'capture': capture, 'W_width': len(cols['W']), 'W_false_positive_width': len(cols['W']) - int(capture['W']),
                'ordered_pair': (r['prediction']['ordered_pair'] if downstream else all(h in top for h in actual[:2]) if cash_arm == 'E_SOURCE_MARKET_TOP3_BOX' else 'NOT_EVALUABLE_AS_FROZEN_DECISION') if not ambiguous else 'PENDING_CANONICAL_DEAD_HEAT_RESULT',
                'ordered_exact': (r['prediction']['ordered_exact'] if downstream else set(actual) == top if cash_arm == 'E_SOURCE_MARKET_TOP3_BOX' else 'NOT_EVALUABLE_AS_FROZEN_DECISION') if not ambiguous else 'PENDING_CANONICAL_DEAD_HEAT_RESULT',
                'capital': {k: cash[k] for k in ('investment', 'return', 'pfs', 'ticket_count')} if cash else 'NOT_DEFINED: no frozen tickets for this arm',
                'lane': 'POST_RESULT_DIAGNOSTIC / NOT_FORWARD_OOS', 'production_effect': 'NONE'})
    summary = {}
    for name in sorted({r['arm'] for r in rows}):
        arm = [r for r in rows if r['arm'] == name]
        summary[name] = {'races': len(arm), 'winner_capture': sum(r['capture']['W'] for r in arm),
            'W_candidate_slots': sum(r['W_width'] for r in arm), 'W_false_positive_slots': sum(r['W_false_positive_width'] for r in arm),
            'P2_capture': sum(r['capture']['P2'] is True for r in arm), 'P2_denominator': sum(isinstance(r['capture']['P2'], bool) for r in arm),
            'P3_capture': sum(r['capture']['P3'] is True for r in arm), 'P3_denominator': sum(isinstance(r['capture']['P3'], bool) for r in arm)}
    out = {'rows': rows, 'summary': summary, 'robust_pfs': {k: capital['arms'][k] for k in ('A_CURRENT_PRODUCTION', 'E_SOURCE_MARKET_TOP3_BOX')},
        'caveats': ['Frozen Static roles already include enacted AKI; these are duplicate baselines, not a causal AKI ablation.',
                    'All-actionable union is a new retrospective measurement only; NOT REGISTERED FOR FORWARD USE.',
                    'Additional roles do not authorize compatible pairs, thirds, stakes or tickets. Undefined downstream metrics are not zero.',
                    'Market top3 BOX is the existing research baseline, not an admitted Production policy.',
                    'Winner-only includes KYO12 unique first place; P2/P3/Order preserve its manual hold.'],
        'registration_fingerprint': load(D / 'preregistered_shadow_comparison.json')['policy_fingerprint'],
        'candidate_definition_sha256_unchanged': hashlib.sha256((ROOT / 'runtime/jra_role_rescue_shadow.py').read_bytes()).hexdigest(),
        'historical_forward_oos_credit': 0, 'activation_performed': False}
    assert len(rows) == 95
    (D / 'five_lane_role_observation_review.json').write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=2) + '\n')
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()

"""FULL29 SHADOW: feed the Rakuten-parsed card into the EXISTING formal LOCAL
29-index arithmetic, unchanged, and build (not run) the KRS input.

Classification: FULL29_SHADOW_PAPER / provider=RAKUTEN_PUBLIC_CARD.
  * Formal SOURCE is NOT established (no official signed SOURCE receipt).
  * Uses the Production evidence registry ids and the regression-tested
    implementation mapping exactly as local_fullnumerical_production does,
    via the provider-neutral compile_parsed_candidate_evidence() entry.
  * prediction/KRS/ticket/capital consumption stay False. Nothing here is
    read by the paper engine's marks or tickets.
  * KRS: the external Engine v1.1.0 is behind the signed formal gateway; this
    module only builds the 5,000-run / seed-1 input. krs_trials = 0.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

RUNTIME = Path(__file__).resolve().parents[1]
REPO = RUNTIME.parent
if str(RUNTIME) not in sys.path:
    sys.path.insert(0, str(RUNTIME))

GOING = {'稍': '稍重', '不': '不良'}


def build(race, runners, html_sha, fetched_at):
    raw = {}
    for r in runners:
        rid = str(r['horse_no'])
        raw[rid] = {
            'runner_id': rid, 'horse_no': r['horse_no'], 'name': r['name'],
            'starts': [dict(s, going=GOING.get(s.get('going'), s.get('going'))) for s in r['starts']],
            'current_jockey': r.get('current_jockey'), 'current_load': r.get('current_load'),
            'current_body_weight': r.get('current_body_weight'),
            'current_body_weight_change': r.get('current_body_weight_change'),
            'sex_age': r.get('sex_age'), 'age': r.get('age'), 'sire': r.get('sire'),
            'damsire': r.get('damsire'), 'trainer': r.get('trainer'),
            # same per-runner market fields the formal NAR card parser supplies
            'odds': r.get('win_odds'), 'popularity': r.get('popularity'),
            'race_card_fetched_at': fetched_at, 'race_card_source_id': 'RAKUTEN-' + race['rid'],
            'race_card_snapshot_sha256': html_sha}
    src = {'normalized_evidence': {'track_condition': {'value': race.get('going') or ''}},
           'source_freeze_at': fetched_at, 'source_snapshot_sha256': html_sha}
    req = {'race': {'venue_id': race['venue_id'], 'race_date': race['race_date'], 'distance': race.get('distance') or 0,
                    'surface': (race.get('surface') or 'DIRT').lower(), 'going': race.get('going'),
                    'class': race.get('race_name'), 'race_no': race['race_no']},
           'venue_id': race['venue_id'], 'race_date': race['race_date'], 'race_no': race['race_no'],
           'runners': [{'runner_id': str(r['horse_no']), 'name': r['name']} for r in runners],
           'run_count': 5000, 'seed': 1}
    return src, req, raw


def run(race, runners, html_text, fetched_at):
    import local_fullnumerical_production as prod
    from local_nar_evidence_candidate import compile_parsed_candidate_evidence
    from local_fullnumerical_candidate import materialize_candidate, REQUIRED
    from local_bvi_bloodline_research import attach_research
    from local_krs_bridge_candidate import build_candidate_krs

    html_sha = hashlib.sha256(html_text.encode()).hexdigest()
    src, req, raw = build(race, runners, html_sha, fetched_at)
    comp = compile_parsed_candidate_evidence(src, req, raw, REPO / prod.PRODUCTION_EVIDENCE_REGISTRY)
    attach_research(comp, src)
    out = materialize_candidate(comp, REPO / prod.IMPLEMENTATION_EVIDENCE_REGISTRY, REPO / prod.IMPLEMENTATION_MAPPING)
    counts = {'CALCULATED': 0, 'RULED-NEUTRAL': 0, 'RULED-HOLD': 0, 'NOT-APPLICABLE': 0, 'UNRESOLVED': 0}
    neutral_by_index = {}
    table = []
    for ru in out['runners']:
        cc = ru.get('canonical_components') or {}
        vals = {}
        for idx in REQUIRED:
            spec = cc.get(idx)
            st = (spec or {}).get('terminal_status', 'UNRESOLVED')
            counts[st if st in counts else 'UNRESOLVED'] += 1
            if st != 'CALCULATED':
                neutral_by_index[idx] = neutral_by_index.get(idx, 0) + 1
            vals[idx] = None if not spec or spec.get('value') is None else round(float(spec['value']), 2)
        table.append({'no': int(ru['runner_id']), 'name': ru.get('name'), 'indices': vals})
    krs_input_sha, krs_error = None, None
    try:
        krs = build_candidate_krs(out)
        krs_input_sha = krs['candidate_krs_input_sha256']
    except Exception as exc:  # readiness evidence only
        krs_error = f'{type(exc).__name__}:{str(exc)[:160]}'
    order = sorted(table, key=lambda x: -(x['indices'].get('F3S-L') or 0))
    return {'classification': 'FULL29_SHADOW_PAPER', 'provider': 'RAKUTEN_PUBLIC_CARD',
            'formal_source_established': False, 'production_numerical_authority': False,
            'prediction_consumption_authorized': False, 'krs_consumption_authorized': False,
            'ticket_consumption_authorized': False, 'capital_consumption_authorized': False,
            'evidence_registry_id': prod.PROD_REGISTRY_ID, 'mapping_id': prod.PROD_MAPPING_ID,
            'source_snapshot_sha256': html_sha, 'source_fetched_at': fetched_at,
            'required_indices': list(REQUIRED), 'runner_count': len(table),
            'cells': len(table) * len(REQUIRED), 'terminal_counts': counts,
            'non_calculated_by_index': neutral_by_index,
            'f3s_order': [x['no'] for x in order], 'runners': table,
            'krs': {'engine': 'EXTERNAL_v1.1.0_NOT_CALLED', 'trials': 0, 'run_count_planned': 5000, 'seed': 1,
                    'input_built': krs_input_sha is not None, 'input_sha256': krs_input_sha, 'error': krs_error}}

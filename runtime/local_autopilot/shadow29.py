"""FULL29 SHADOW: feed the Rakuten-parsed card into the EXISTING formal LOCAL
29-index arithmetic, unchanged, and build (not run) the KRS input.

Classification: FULL29_SHADOW_CANDIDATE_ARITHMETIC / provider=RAKUTEN_PUBLIC_CARD.
  * Arithmetic = materialize_candidate(); the production consumer
    (materialize_production) is NOT executed. Its per-cell gates are
    re-applied and reported as production_gates for comparison only.
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
    # Same per-cell gates materialize_production() applies before it rebinds to
    # Production authority (registry equivalence + finite value + provenance).
    try:
        prod._assert_registry_equivalence()
        equivalence = 'PASS'
    except Exception as exc:
        equivalence = f'FAIL:{type(exc).__name__}:{str(exc)[:120]}'
    prod_gate = {'pass': 0, 'PROVENANCE_INCOMPLETE': 0, 'FINITE_VALUE_REQUIRED': 0, 'TERMINAL_MISSING': 0, 'STATUS_INVALID': 0}
    neutral_by_index = {}
    table = []
    for ru in out['runners']:
        cc = ru.get('canonical_components') or {}
        vals = {}
        for idx in REQUIRED:
            spec = cc.get(idx)
            st = (spec or {}).get('terminal_status', 'UNRESOLVED')
            counts[st if st in counts else 'UNRESOLVED'] += 1
            if not isinstance(spec, dict):
                prod_gate['TERMINAL_MISSING'] += 1
            elif str(st).upper() not in ('CALCULATED', 'RULED-NEUTRAL', 'RULED-HOLD', 'NOT-APPLICABLE'):
                prod_gate['STATUS_INVALID'] += 1
            elif str(st).upper() in ('CALCULATED', 'RULED-NEUTRAL') and not prod._finite_numeric(spec.get('value')):
                prod_gate['FINITE_VALUE_REQUIRED'] += 1
            elif not spec.get('rule_id') or not spec.get('evidence_refs') or not spec.get('source_fact'):
                prod_gate['PROVENANCE_INCOMPLETE'] += 1
            else:
                prod_gate['pass'] += 1
            if st != 'CALCULATED':
                neutral_by_index[idx] = neutral_by_index.get(idx, 0) + 1
            vals[idx] = None if not spec or spec.get('value') is None else round(float(spec['value']), 2)
        table.append({'no': int(ru['runner_id']), 'name': ru.get('name'), 'indices': vals})
    krs_input_sha, krs_error, krs_input = None, None, None
    try:
        krs = build_candidate_krs(out)
        krs_input_sha = krs['candidate_krs_input_sha256']
        krs_input = krs['candidate_krs_input_data']
    except Exception as exc:  # readiness evidence only
        krs_error = f'{type(exc).__name__}:{str(exc)[:160]}'
    order = sorted(table, key=lambda x: -(x['indices'].get('F3S-L') or 0))
    return {'classification': 'FULL29_SHADOW_CANDIDATE_ARITHMETIC', 'provider': 'RAKUTEN_PUBLIC_CARD',
            'implementation': 'local_fullnumerical_candidate.materialize_candidate (NOT the production consumer)',
            'production_gates': {'registry_equivalence': equivalence, 'cells': prod_gate},
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
                    'input_built': krs_input_sha is not None, 'input_sha256': krs_input_sha, 'error': krs_error},
            '_krs_input': krs_input}


def resolve_endpoint():
    """LOCAL external KRS Engine endpoint + engine/parameter_map SHA from the canonical contract."""
    from family_runtime_contract import load_contracts, resolve_family_runtime
    r = resolve_family_runtime({'family_id': 'LOCAL'}, load_contracts())
    c = r['contract']
    return r['external_endpoint'], {k: c.get(k) for k in ('engine_sha256', 'parameter_map_sha256', 'runtime',
                                                          'signed_receipt_authority')}


def research_krs(krs_input, race_id, run_count=5000, seed=1, timeout=300):
    """NON-PRODUCTION research KRS: real external Engine run on the SOURCE-derived
    (Rakuten public card) candidate input. Returns (stages, envelope). Never a formal KRS."""
    import copy
    import json
    import time
    import urllib.error
    import urllib.request
    from datetime import datetime, timezone
    now = lambda: datetime.now(timezone.utc).isoformat()
    stages = {'REQUESTED': now()}
    endpoint, contract = resolve_endpoint()

    def call(path, payload, t):
        body = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode()
        rq = urllib.request.Request(endpoint + path, data=body, headers={'content-type': 'application/json'}, method='POST')
        try:
            with urllib.request.urlopen(rq, timeout=t) as x:
                raw = x.read().decode()
                return x.status, (json.loads(raw) if raw else {})
        except urllib.error.HTTPError as e:
            raw = e.read().decode(errors='replace')
            try:
                return e.code, json.loads(raw)
            except ValueError:
                return e.code, {'raw': raw[:500]}

    inp = copy.deepcopy(krs_input)
    inp.setdefault('race', {})['race_id'] = race_id
    inp.setdefault('simulation', {})['run_count'] = run_count
    inp['simulation']['master_seed'] = seed
    stages['ATTEMPTED'] = now()
    t0 = time.monotonic()
    code, res = call('/krs/execute', {'family_id': 'LOCAL', 'race_id': race_id, 'krs_input_data': inp,
                                      'run_count': run_count, 'seed': seed}, timeout)
    art = res.get('artifact') or {}
    summary = {'classification': 'LOCAL_RESEARCH_KRS_NON_PRODUCTION (SOURCE=RAKUTEN_PUBLIC_CARD, unsigned)',
               'endpoint': endpoint, 'contract': contract, 'race_id': race_id, 'run_count_requested': run_count,
               'seed': seed, 'http_status': code, 'elapsed_s': round(time.monotonic() - t0, 1),
               'receipt_status': (res.get('receipt') or {}).get('status'),
               'actual_run_count': art.get('actual_run_count'), 'input_sha256': art.get('input_sha256'),
               'output_sha256': art.get('output_sha256'), 'receipt_sha256': res.get('receipt_sha256'),
               'engine_sha256_reported': art.get('engine_sha256') or (res.get('receipt') or {}).get('engine_sha256'),
               'calibrated': False}
    if code < 300 and summary['receipt_status'] == 'EXECUTED':
        stages['COMPLETED'] = now()
        if summary['output_sha256']:
            stages['OUTPUT_CAPTURED'] = now()
        if summary['receipt_sha256']:
            stages['RECEIPT_ISSUED'] = now()
            vc, v = call('/verify', res, 60)
            summary['verify'] = {'http_status': vc, 'valid': v.get('valid')}
            if vc < 300 and v.get('valid') is True:
                stages['RECEIPT_VERIFIED'] = now()
    else:
        summary['error'] = str(res)[:300]
    summary['stages'] = stages
    return summary, res


def run_production(race, runners, html_text, fetched_at):
    """FORMAL Full29: the Production numerical consumer
    local_fullnumerical_production.materialize_production() on the
    Runtime-signed Rakuten card (provider-parsed facts, same Production
    registries and closure gate). Consumption flags stay exactly as the
    Production module sets them (prediction/KRS/ticket/capital = False, R52).
    The KRS input is still the SOURCE-derived technical proxy built from the
    same compiled evidence (KRS-input consumption is not authorised)."""
    import os
    import local_fullnumerical_production as prod
    from local_nar_evidence_candidate import compile_parsed_candidate_evidence
    from local_fullnumerical_candidate import materialize_candidate, REQUIRED
    from local_bvi_bloodline_research import attach_research
    from local_krs_bridge_candidate import build_candidate_krs

    html_sha = hashlib.sha256(html_text.encode()).hexdigest()
    src, req, raw = build(race, runners, html_sha, fetched_at)
    cwd = os.getcwd()
    os.chdir(REPO)   # Production module resolves its registries relative to the repo root
    try:
        prod_out = prod.materialize_production(src, req, REQUIRED, raw_field=raw)   # raises on closure failure
        comp = compile_parsed_candidate_evidence(src, req, raw, REPO / prod.PRODUCTION_EVIDENCE_REGISTRY)
        attach_research(comp, src)
        cand = materialize_candidate(comp, REPO / prod.IMPLEMENTATION_EVIDENCE_REGISTRY, REPO / prod.IMPLEMENTATION_MAPPING)
        krs = build_candidate_krs(cand)
    finally:
        os.chdir(cwd)
    cov = prod_out['numeric_coverage']
    # identical arithmetic check: Production values == implementation values cell by cell
    pv = {(str(r['runner_id']), i): (r.get('canonical_components') or {}).get(i, {}).get('value')
          for r in prod_out['runners'] for i in REQUIRED}
    cv = {(str(r['runner_id']), i): (r.get('canonical_components') or {}).get(i, {}).get('value')
          for r in cand['runners'] for i in REQUIRED}
    table = [{'no': int(r['runner_id']), 'name': r.get('name'),
              'indices': {i: (None if (r.get('canonical_components') or {}).get(i, {}).get('value') is None
                              else round(float(r['canonical_components'][i]['value']), 2)) for i in REQUIRED}}
             for r in prod_out['runners']]
    return {'classification': 'FULL29_PRODUCTION_NUMERICAL_MATERIALIZATION', 'provider': 'RAKUTEN_PUBLIC_CARD',
            'implementation': 'local_fullnumerical_production.materialize_production (Production consumer)',
            'materializer_profile': prod.PROFILE,
            'production_numerical_authority': prod_out['production_numerical_authority'],
            'production_numerical_summary': prod_out['production_numerical_summary'],
            'numeric_coverage': {k: v for k, v in cov.items() if k != 'unresolved'},
            'full_terminalization': prod_out['full_terminalization'],
            'full_numerical_closure': prod_out['full_numerical_closure'],
            'strict_full_numerical_ready': prod_out['strict_full_numerical_ready'],
            'index_terminalization_hash': prod_out['index_terminalization_hash'],
            'index_provenance_hash': prod_out['index_provenance_hash'],
            'implementation_value_equivalence': 'PASS' if pv == cv else 'MISMATCH',
            'evidence_registry_id': prod.PROD_REGISTRY_ID, 'mapping_id': prod.PROD_MAPPING_ID,
            'source_snapshot_sha256': html_sha, 'source_fetched_at': fetched_at,
            'required_indices': list(REQUIRED), 'runner_count': len(table),
            'cells': len(table) * len(REQUIRED), 'runners': table,
            'krs': {'input_mode': 'TECHNICAL_PROXY_DIAGNOSTIC', 'input_sha256': krs['candidate_krs_input_sha256']},
            '_krs_input': krs['candidate_krs_input_data']}

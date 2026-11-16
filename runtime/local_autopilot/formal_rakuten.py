"""LOCAL formal Production on the Runtime-signed Rakuten race card.

Owner instructions 2026-11-16 (16:26 楽天競馬をソースに / 16:32 地方平地14場すべて /
17:19 完成させなさい). One call per race, before cutoff:

  SOURCE (Runtime fetch + freeze + sign, Rakuten profile, signature verified here)
  -> Full29 (production registry on the signed card bytes; numeric consumers stay false)
  -> Static (Owner policy v1.1: ordinal past-start heuristic, no 29-index numbers / odds)
  -> PRE_KRS (SOURCE-derived technical-proxy KRS input; R52 boundary unchanged)
  -> KRS (5,000 runs) -> Role/Pair/Third closure -> MEC -> Capital (RECOMMENDATION_ONLY)
  -> Signed FINAL (Runtime), signature verified here.

Everything is kept; nothing is purchased. A failure records the first failed stage.
"""
from __future__ import annotations

import base64
import copy
import gzip
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / 'runtime'):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from runtime.local_autopilot import rakuten  # noqa: E402

POLICY_PATH = REPO / 'profiles' / 'local_production_static_owner_20261116_v1_1.json'
RAKUTEN_PROFILE = 'KM-LOCAL-RAKUTEN-SOURCE-MANIFEST-v1.0-20261116'
JST = timezone(timedelta(hours=9))
STAGES = ['SOURCE_FREEZE', 'RUNNER_UNIVERSE', 'NUMERICAL_MATERIALIZATION', 'INDEX_PROVENANCE', 'STATIC_FREEZE',
          'PRE_KRS', 'KRS', 'KRS_UTILITY', 'MEC', 'CAPITAL', 'FINAL_TICKET_FREEZE']


class FormalStop(RuntimeError):
    def __init__(self, stage, detail):
        super().__init__(f'{stage}:{detail}')
        self.stage, self.detail = stage, detail


def _sha(x):
    return hashlib.sha256(json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def _now():
    return datetime.now(timezone.utc)


_V16 = {'checked': 0.0, 'ready': False}


def runtime_v16_ready():
    """True once the Runtime serves /health16 with the Rakuten profile (probed <= every 5 min)."""
    if time.monotonic() - _V16['checked'] < 300:
        return _V16['ready']
    _V16['checked'] = time.monotonic()
    try:
        c, h = _call(_endpoint(), '/health16', None, 20)
        # REV.1 is known to reject the Rakuten host (SOURCE_HOST_NOT_ALLOWED); do not
        # spend formal attempts on it.
        _V16['ready'] = (c < 300 and RAKUTEN_PROFILE in (h.get('approved_source_profiles') or [])
                         and 'v1.6-REV.1-' not in str(h.get('runtime_revision') or ''))
    except Exception:
        _V16['ready'] = False
    return _V16['ready']


def _endpoint():
    from runtime.local_autopilot.shadow29 import resolve_endpoint
    return resolve_endpoint()[0]


def _call(base, path, payload=None, timeout=240):
    data = None if payload is None else json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode()
    rq = urllib.request.Request(base + path, data=data, method='GET' if payload is None else 'POST',
                                headers={'content-type': 'application/json'})
    try:
        with urllib.request.urlopen(rq, timeout=timeout) as x:
            raw = x.read().decode()
            return x.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        raw = e.read().decode(errors='replace')
        try:
            return e.code, json.loads(raw)
        except ValueError:
            return e.code, {'detail': raw[:400]}


def _verify_sig(env, public_b64):
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    key = Ed25519PublicKey.from_public_bytes(base64.b64decode(public_b64, validate=True))
    msg = json.dumps(env['receipt'], ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    key.verify(base64.b64decode(env['signature'], validate=True), msg)   # raises on failure
    return hashlib.sha256(msg).hexdigest() == env.get('receipt_sha256')


# ---------------------------------------------------------------- Static Owner v1.1
def build_static(race, source_env, rows, numerical, policy, now):
    """Port of local_production_static_owner.build_formal_static (same ordinal rule set)
    onto the Runtime-signed Rakuten card. No 29-index numbers, odds or results."""
    from runtime.local_production_static_owner import _runner_facts
    if (policy.get('enabled') is not True or policy.get('owner_authorization') != 'EXPLICIT_USER_INSTRUCTION_20261116'
            or policy.get('numerical_prediction_consumption') is not False):
        raise FormalStop('STATIC_FREEZE', 'STATIC_OWNER_AUTHORIZATION_MISSING')
    if race['venue_id'] not in policy['venues']:
        raise FormalStop('STATIC_FREEZE', 'VENUE_OWNER_NOT_AUTHORIZED')
    art = source_env['artifact']
    ids = [str(r['runner_id']) for r in art['official_runner_universe']['runners']]
    if set(ids) != {str(r['horse_no']) for r in rows}:
        raise FormalStop('RUNNER_UNIVERSE', 'STATIC_UNIVERSE_MISMATCH')
    by = {str(r['horse_no']): r for r in rows}
    for r in art['official_runner_universe']['runners']:
        if rakuten.nfkc(by[str(r['runner_id'])]['name']) != rakuten.nfkc(r['name']):
            raise FormalStop('RUNNER_UNIVERSE', 'CARD_NAME_MISMATCH:' + str(r['runner_id']))
    head = art['rakuten_card_header']
    if head.get('surface') != 'DIRT' or not 800 <= int(head.get('distance') or 0) <= 2600:
        raise FormalStop('STATIC_FREEZE', 'LOCAL_DIRT_DISTANCE_OUT_OF_SCOPE')
    day = datetime.fromisoformat(race['post_current']).astimezone(JST).replace(hour=0, minute=0, second=0, microsecond=0)
    facts = {rid: _runner_facts(by[rid], venue_name=race['venue_name'], distance=head['distance'], race_day=day)
             for rid in ids}

    def rank_key(rid):
        f = facts[rid]
        vals = (f['exact_wins'], f['exact_podiums'], f['exact_best_finish_share'], f['venue_best_finish_share'],
                f['recent_dirt_finish_share'], f['dirt_best_finish_share'])
        return tuple(-float(v) if v is not None else 0 for v in vals) + (int(rid),)
    ranked = sorted(ids, key=rank_key)
    n = len(ranked)
    heads, seconds, thirds = ranked[:min(n, 3)], ranked[:min(n, 6)], ranked[:min(n, 9)]
    unknown = [rid for rid in ranked if facts[rid]['unknown_exact_course']]
    if unknown and not any(x in thirds for x in unknown) and n > len(thirds):
        thirds = thirds[:-1] + [unknown[0]]
    roles = {rid: [c for c, pool in (('W', heads), ('P2', seconds)) if rid in pool] + ['P3'] for rid in ranked}
    role_registry = [{'runner_id': rid, 'column': c, 'status': 'CORE' if rid in heads else 'PROTECTED'}
                     for rid in ranked for c in ('W', 'P2', 'P3') if c in roles[rid]]
    pairs, third_rows = [], []
    for h in heads:
        for p in seconds:
            if h == p:
                continue
            pairs.append({'head': h, 'second': p, 'status': 'PURCHASE',
                          'reason': 'OFFICIAL_PRESTART_ORDINAL_HEAD_LOCAL_PAIR / SAME_CARD_SOURCE'})
            for t in thirds:
                if t not in (h, p):
                    third_rows.append({'head': h, 'second': p, 'third': t, 'status': 'PURCHASE',
                                       'reason': 'OFFICIAL_PRESTART_THIRD_ROW / UNKNOWN_PROTECTED'})
    for h in heads:
        for p in ids:
            if h != p and p not in seconds:
                pairs.append({'head': h, 'second': p, 'status': 'SEMANTIC_ONLY',
                              'reason': 'FULL_P2_UNIVERSE_AUDIT / NOT_PURCHASED'})
    marks = {rid: '◎' if i == 0 else '○' if i == 1 else '▲' if i == 2 else '△' for i, rid in enumerate(ranked)}
    runners = [{'runner_id': rid, 'name': by[rid]['name'], 'jockey': by[rid].get('current_jockey'),
                'assigned_weight': by[rid].get('current_load'), 'static_roles': roles[rid]} for rid in ranked]
    req = {
        'family_id': 'LOCAL', 'race_id': race['formal_race_id'], 'execution_phase': 'AUTO',
        'race': {'race_id': race['formal_race_id'], 'venue': race['venue_id'], 'venue_id': race['venue_id'],
                 'race_date': race['race_date'], 'race_no': race['race_no'], 'surface': 'dirt',
                 'distance': head['distance'], 'class': race.get('class_text') or 'UNKNOWN'},
        'runners': runners, 'required_indices': numerical['required_indices'], 'run_count': 5000,
        'seed': int(race['race_date'].replace('-', '') + str(race['race_no']).zfill(2)),
        'static_prediction_frozen': True,
        'static_prediction': {
            'status': 'FROZEN / OWNER-AUTHORIZED / RULE-BASED-UNVALIDATED / RESULT-BLIND',
            'ranking': ranked, 'marks': marks, 'roles': roles,
            'uncertainty': {rid: ('EXACT_COURSE_UNKNOWN / PROTECTED_NOT_WEAK' if facts[rid]['unknown_exact_course']
                                  else 'EXACT_COURSE_OBSERVED') for rid in ranked},
            'source_basis_receipt_sha256': source_env['receipt_sha256'],
            'source_basis_snapshot_sha256': art['source_snapshot_sha256']},
        'venue_canon': policy['venue_canons'][race['venue_id']],
        'role_registry': role_registry, 'pair_dispositions': pairs, 'third_dispositions': third_rows,
        'capital_policy': {'mode': 'RECOMMENDATION_ONLY'},
        'source_policy': 'RUNTIME_SIGNED_RAKUTEN_RACE_CARD (OWNER_INSTRUCTION_20261116)',
        'source_snapshot_sha256': art['source_snapshot_sha256'],
    }
    ledger = {'profile': policy['profile'], 'status': 'OWNER_AUTHORIZED_UNVALIDATED_PRESTART_STATIC',
              'frozen_at': now.isoformat(), 'source_receipt_sha256': source_env['receipt_sha256'],
              'full_universe': ranked, 'observed_facts': facts, 'uncalibrated': True,
              'numerical_prediction_consumption': False, 'odds_consumed': False, 'result_consumed': False}
    ledger['sha256'] = _sha(ledger)
    return req, ledger


# ---------------------------------------------------------------- orchestrator
def run_formal(r, out_dir, deadline):
    """r: autopilot queue race. Returns (summary, artifacts). Never raises."""
    from runtime.local_autopilot import shadow29
    from minimum_efficient_coverage import (MEC_PROFILE, build_mec_plan, canonicalize_role_pair_third_closure,
                                            validate_mec_plan)
    from capital_policy import resolve_capital_policy
    t0 = time.monotonic()
    key = f"{r['venue_id']}_{r['race_no']:02d}"
    race = dict(r, formal_race_id=f"KM-LOCAL-{r['venue_id']}-{r['race_date'].replace('-', '')}-R{r['race_no']:02d}-RKT")
    stages, arts, manifest = {}, {}, []
    summary = {'classification': 'LOCAL_FORMAL_PRODUCTION_RAKUTEN_SIGNED_SOURCE', 'race_id': race['formal_race_id'],
               'stages': stages, 'first_failed_stage': None, 'actual_purchase': False}

    def mark(stage, **kw):
        stages[stage] = _now().isoformat()
        manifest.append({'stage': stage, 'at': stages[stage], **kw})

    def guard(stage):
        if _now() >= deadline:
            raise FormalStop(stage, 'PRESTART_DEADLINE_PASSED')
    try:
        base = _endpoint()
        hc, health = _call(base, '/health', None, 30)
        if hc >= 300 or health.get('status') != 'READY':
            raise FormalStop('SOURCE_FREEZE', f'RUNTIME_NOT_READY:{hc}')
        pub = health['receipt_public_key_b64']
        policy = json.loads(POLICY_PATH.read_text())
        guard('SOURCE_FREEZE')
        sc, src = _call(base, '/source/acquire', {
            'family_id': 'LOCAL', 'race_id': race['formal_race_id'], 'manifest_profile': RAKUTEN_PROFILE,
            'venue_id': r['venue_id'], 'race_date': r['race_date'], 'race_no': r['race_no'],
            'rakuten_race_id': r['rid'], 'prediction_cutoff': deadline.isoformat()}, 200)
        arts['source_receipt'] = src
        if sc >= 300 or (src.get('receipt') or {}).get('status') != 'SOURCE_FROZEN':
            raise FormalStop('SOURCE_FREEZE', f"HTTP_{sc}:{(src.get('receipt') or {}).get('errors') or src.get('detail')}")
        if not _verify_sig(src, pub):
            raise FormalStop('SOURCE_FREEZE', 'SOURCE_RECEIPT_SHA_MISMATCH')
        vc, sv = _call(base, '/source/verify', src, 60)
        if vc >= 300 or sv.get('valid') is not True:
            raise FormalStop('SOURCE_FREEZE', 'SOURCE_VERIFY_FAILED')
        art = src['artifact']
        mark('SOURCE_FREEZE', receipt_sha256=src['receipt_sha256'], snapshot_sha256=art['source_snapshot_sha256'])
        snap = next(s for s in art['sources'] if s['source_id'] == 'RAKUTEN_RACE_CARD')
        raw = gzip.decompress(base64.b64decode(snap['raw_gzip_b64']))
        if hashlib.sha256(raw).hexdigest() != snap['raw_sha256']:
            raise FormalStop('SOURCE_FREEZE', 'RAW_SHA_MISMATCH')
        html = raw.decode('utf-8', errors='replace')
        active, cancelled = rakuten.parse_card(html)
        mark('RUNNER_UNIVERSE', active=len(active), cancelled=len(cancelled),
             universe_sha256=art['official_runner_universe_sha256'])
        guard('NUMERICAL_MATERIALIZATION')
        head = art['rakuten_card_header']
        sh = shadow29.run({'venue_id': r['venue_id'], 'venue_name': r['venue_name'], 'race_no': r['race_no'],
                           'race_date': r['race_date'], 'distance': head.get('distance'), 'surface': head.get('surface'),
                           'going': head.get('going'), 'race_name': head.get('race_name'), 'post_current': r['post_current'],
                           'rid': r['rid']}, active, html, snap['fetched_at'])
        krs_input = sh.pop('_krs_input', None)
        arts['full29'] = sh
        tc = sh.get('terminal_counts') or {}
        full_term = (sh.get('production_gates') or {}).get('registry_equivalence') == 'PASS' and not tc.get('UNRESOLVED')
        numerical = {'required_indices': sh.get('required_indices') or [], 'strict_full_numerical_ready': full_term,
                     'production_numerical_authority': {'prediction_consumption_authorized': False}}
        if len(numerical['required_indices']) != 29 or not full_term or krs_input is None:
            raise FormalStop('NUMERICAL_MATERIALIZATION', f"FULL29_NOT_TERMINAL:{tc}:{(sh.get('krs') or {}).get('error')}")
        mark('NUMERICAL_MATERIALIZATION', cells=sh.get('cells'), terminal_counts=tc)
        mark('INDEX_PROVENANCE', registry_equivalence=sh['production_gates']['registry_equivalence'],
             cell_gate_pass=sh['production_gates']['cells'].get('pass'))
        guard('STATIC_FREEZE')
        req, ledger = build_static(race, src, active, numerical, policy, _now())
        arts['static_ledger'] = ledger
        mark('STATIC_FREEZE', ledger_sha256=ledger['sha256'], ranking=req['static_prediction']['ranking'])
        roles = req['static_prediction']['roles']
        kin = copy.deepcopy(krs_input)
        for h in kin['horses']:
            h['static_roles'] = roles.get(str(h['horse_no']), [])
        kin.setdefault('keibametrics_input_authority', {}).update({
            'input_mode': 'TECHNICAL_PROXY_DIAGNOSTIC', 'full_numerical_calculation': False, 'full_terminalization': True,
            'proxy_reason': 'R52 LOCAL numerical KRS-input consumer false; SOURCE-derived technical proxy on the signed card'})
        kin.setdefault('race', {})['race_id'] = race['formal_race_id']
        kin.setdefault('simulation', {}).update({'run_count': 5000, 'master_seed': req['seed']})
        guard('PRE_KRS')
        pc, pre = _call(base, '/pre-krs', {'family_id': 'LOCAL', 'race_id': race['formal_race_id'], 'source_receipt': src,
                                          'krs_input_data': kin, 'full_terminalization': True,
                                          'full_numerical_calculation': False,
                                          'krs_input_mode': 'TECHNICAL_PROXY_DIAGNOSTIC',
                                          'static_prediction_frozen': True}, 120)
        arts['pre_krs_receipt'] = pre
        if pc >= 300 or (pre.get('receipt') or {}).get('status') != 'PASS' or not _verify_sig(pre, pub):
            raise FormalStop('PRE_KRS', f"HTTP_{pc}:{(pre.get('receipt') or {}).get('errors') or pre.get('detail')}")
        mark('PRE_KRS', receipt_sha256=pre['receipt_sha256'])
        guard('KRS')
        kc, run = _call(base, '/krs/execute', {'family_id': 'LOCAL', 'race_id': race['formal_race_id'],
                                              'krs_input_data': kin, 'run_count': 5000, 'seed': req['seed']}, 300)
        arts['krs_run_receipt'] = run
        if kc >= 300 or (run.get('receipt') or {}).get('status') != 'EXECUTED' or not _verify_sig(run, pub):
            raise FormalStop('KRS', f"HTTP_{kc}:{(run.get('receipt') or {}).get('errors') or run.get('detail')}")
        ka = run['artifact']
        mark('KRS', actual_run_count=ka['actual_run_count'], input_sha256=ka['input_sha256'], output_sha256=ka['output_sha256'])
        mark('KRS_UTILITY', status='NOT_CONSUMED (uncalibrated; R52)', production_effect='NONE')
        guard('MEC')
        req, closure = canonicalize_role_pair_third_closure(req)
        mec = build_mec_plan(req, None, strict_head_closure=True, min_stake=100)
        chk = validate_mec_plan(mec)
        if chk.get('mec_verified') is not True or mec.get('profile') != MEC_PROFILE:
            raise FormalStop('MEC', 'MEC_VERIFY_FAILED')
        mark('MEC', mec_sha256=mec['sha256'], ticket_count=mec['ticket_count'],
             minimum_required_capital=mec['minimum_required_capital'])
        capital = resolve_capital_policy(req, mec)
        mark('CAPITAL', decision=capital['decision'], mode=capital['mode'], required_capital=capital['required_capital'])
        no_bet = bool(capital['no_bet'])
        tickets = [] if no_bet else copy.deepcopy(mec['tickets'])
        total = 0 if no_bet else int(mec['minimum_required_capital'])
        guard('FINAL_TICKET_FREEZE')
        freeze = _now().isoformat()
        mark('FINAL_TICKET_FREEZE', ticket_count=len(tickets), total_investment=total)
        fpp = {'ranking': req['static_prediction']['ranking'], 'roles': roles, 'marks': req['static_prediction']['marks'],
               'source_snapshot_sha256': art['source_snapshot_sha256'], 'static_ledger_sha256': ledger['sha256'],
               'local_krs_input_sha256': _sha(kin), 'minimum_efficient_coverage': mec,
               'krs_prediction_utility_shadow': None, 'owner_policy': policy['profile']}
        trace = {'fpp_sha256': _sha(fpp), 'mec_sha256': mec['sha256'], 'candidate_count': mec.get('candidate_count', len(tickets)),
                 'selected_count': len(tickets), 'capital_decision_sha256': capital['sha256'],
                 'role_pair_third_closure_sha256': closure.get('sha256')}
        fc, fin = _call(base, '/final', {
            'family_id': 'LOCAL', 'race_id': race['formal_race_id'], 'source_receipt': src, 'krs_run_receipt': run,
            'final_prediction_package': fpp,
            'final_ticket': {'finalized': True, 'no_bet': no_bet, 'total_investment': total, 'tickets': tickets,
                             'frozen_at': freeze},
            'minimum_efficient_coverage': mec, 'capital_policy_decision': capital, 'ticket_transport_trace': trace,
            'execution_stage_manifest': manifest, 'final_freeze_timestamp': freeze}, 180)
        arts['final_receipt'] = fin
        if fc >= 300 or (fin.get('receipt') or {}).get('status') != 'PASS' or not _verify_sig(fin, pub):
            raise FormalStop('FINAL', f"HTTP_{fc}:{(fin.get('receipt') or {}).get('errors') or fin.get('detail')}")
        vfc, vf = _call(base, '/verify', fin, 60)
        summary.update(status='SIGNED_FINAL', final_receipt_sha256=fin['receipt_sha256'],
                       final_verified_remote=vfc < 300 and vf.get('valid') is True, final_verified_local=True,
                       ticket_count=len(tickets), total_investment=total, no_bet=no_bet,
                       ranking=fpp['ranking'], marks=fpp['marks'],
                       roles={k: v for k, v in roles.items()}, krs_actual_run_count=ka['actual_run_count'],
                       before_cutoff=_now() < deadline, tickets=tickets)
        stages['SIGNED_FINAL'] = _now().isoformat()
    except FormalStop as e:
        summary.update(status='HOLD', first_failed_stage=e.stage, error=str(e.detail)[:400])
    except Exception as e:  # never break the autopilot
        summary.update(status='HOLD', first_failed_stage=summary['first_failed_stage'] or 'INTERNAL',
                       error=f'{type(e).__name__}:{str(e)[:300]}')
    summary['elapsed_s'] = round(time.monotonic() - t0, 1)
    return summary, arts


def run_for_key(out, key):
    """CLI/worker entry: formal run for one queued race; files under out/formal/."""
    from runtime.local_autopilot.run import cutoff, dump
    q = json.loads((out / 'queue.json').read_text())
    r = q['races'][key]
    deadline = cutoff(r)
    summary, arts = run_formal(r, out, deadline)
    fd = out / 'formal'
    fd.mkdir(exist_ok=True)
    for name, obj in arts.items():
        dump(fd / f'{key}.{name}.json', obj)
    dump(fd / f'{key}.summary.json', summary)
    return summary


if __name__ == '__main__':
    import argparse
    import os
    ap = argparse.ArgumentParser()
    ap.add_argument('--date', required=True)
    ap.add_argument('--key', required=True)
    a = ap.parse_args()
    root = Path(os.environ.get('KM_LOCAL_AUTOPILOT_OUT') or (REPO / 'runtime' / 'local_autopilot' / 'output'))
    s = run_for_key(root / a.date, a.key)
    print(json.dumps({k: v for k, v in s.items() if k != 'tickets'}, ensure_ascii=False, default=str)[:3000])

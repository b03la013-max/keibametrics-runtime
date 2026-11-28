"""LOCAL formal Production on the Runtime-signed Rakuten race card.

Owner instructions 2026-11-16 (16:26 楽天競馬をソースに / 16:32 地方平地14場すべて /
17:19 完成させなさい). One call per race, before cutoff:

  SOURCE (Runtime fetch + freeze + sign, Rakuten profile, signature verified here)
  -> Full29 (production registry on the signed card bytes; numeric consumers stay false)
  -> Static (Owner policy v1.1: ordinal past-start heuristic, no 29-index numbers / odds)
  -> PRE_KRS (KRS input mode from the authority resolved per race: R53 LOCAL consumption
     authorised -> FORMAL_NUMERICAL from the Production Full29; otherwise technical proxy)
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
FORMAL_VENUE = {'KOC': 'KCH', 'HMJ': 'HIM'}   # autopilot (Rakuten page) code -> Runtime / Static / Full29 code
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


def resolve_authority(now):
    """Current family authority at this instant (canonical resolver) and the LOCAL consumption flags."""
    from family_authority_guard import resolve_current_authority
    path, a = resolve_current_authority(REPO, now=now)
    L = (a.get('family_scoped_authority') or {}).get('LOCAL') or {}
    b = L.get('numerical_consumption_boundary') or {}
    return {'manifest_id': a.get('manifest_id'), 'path': str(path.relative_to(REPO)),
            'file_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'effective_at': a.get('effective_at'),
            'resolved_at': now.isoformat(),
            'consumption': {k: b.get(k) is True for k in ('prediction_authority', 'krs_input_authority',
                                                          'ticket_authority', 'capital_authority')},
            'numerical_prediction_consumer': _active(L.get('numerical_prediction_consumer')),
            'local_ticket_cap': _active(L.get('local_ticket_cap'))}


def _active(x):
    return x if isinstance(x, dict) and x.get('status') == 'ACTIVE' else None


def numerical_ranking(full29):
    """R54 numerical prediction consumer: existing candidate arithmetic
    (local_krs_bridge_candidate.build_candidate_prediction) on the Production Full29 values."""
    from local_krs_bridge_candidate import build_candidate_prediction
    req = {'runners': [{'runner_id': str(x['no']), 'name': x.get('name'),
                        'canonical_components': {i: {'value': v} for i, v in x['indices'].items()}}
                       for x in full29['runners']]}
    cp = build_candidate_prediction(req)['candidate_static_prediction']
    return cp['ranking'], {k: cp[k] for k in ('profile', 'ranking', 'runner_scores')}


def cap_tickets(tickets, ranking, cap):
    """R54 LOCAL ticket cap: keep <= cap tickets of the MEC set by tier, numerical rank sum, MEC order."""
    tier = {'CORE': 0, 'PROTECTION': 1, 'TAIL': 2}
    pos = {str(h): i for i, h in enumerate(ranking)}
    order = sorted(range(len(tickets)), key=lambda i: (tier.get(str(tickets[i].get('mec_tier')), 3),
                                                        sum(pos.get(str(x), 99) for x in tickets[i]['selection']), i))
    keep = sorted(order[:cap])
    kept = [copy.deepcopy(tickets[i]) for i in keep]
    dropped = [tickets[i] for i in order[cap:]]
    rec = {'max_tickets': cap, 'mec_ticket_count': len(tickets), 'kept_count': len(kept),
           'kept_investment': sum(int(t.get('stake') or 100) for t in kept),
           'dropped_count': len(dropped), 'dropped_coverage_ids': sorted({c for t in dropped for c in t.get('coverage_ids') or []}),
           'tickets': kept}
    rec['sha256'] = _sha(rec)
    return rec


def prior_learning_states(out_dir, race_id, source_freeze, pub=None):
    """Verified LOCAL RESULT learning states available strictly before this race's SOURCE freeze.
    With `pub`, the RESULT receipt's Ed25519 signature must verify (unsigned/forged states are ignored)."""
    states = []
    if out_dir is None:
        return states
    for f in sorted(Path(out_dir).parent.glob('*/formal/*.result_receipt.json')):
        try:
            rec = json.loads(f.read_text())
        except (OSError, ValueError):
            continue
        art = rec.get('artifact') or {}
        st = art.get('automatic_next_race_learning_state')
        if (rec.get('receipt') or {}).get('status') != 'PASS' or not isinstance(st, dict) or st.get('race_id') == race_id:
            continue
        if pub is not None:
            try:
                if not _verify_sig(rec, pub):
                    continue
            except Exception:
                continue
        states.append(dict(st, effective_time=art.get('review_completed_at'),
                           result_receipt_sha256=rec.get('receipt_sha256')))
    eligible = []
    for st in states:
        try:
            t = datetime.fromisoformat(str(st['effective_time']).replace('Z', '+00:00'))
        except (KeyError, ValueError):
            continue
        if t < source_freeze:
            eligible.append(st)
    return eligible


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
def build_static(race, source_env, rows, numerical, policy, now, ranked_override=None, consumer=None):
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
    static_ranked = sorted(ids, key=rank_key)
    if ranked_override is not None:
        if sorted(ranked_override) != sorted(ids):
            raise FormalStop('STATIC_FREEZE', 'NUMERICAL_RANKING_UNIVERSE_MISMATCH')
        ranked = list(ranked_override)
    else:
        ranked = static_ranked
    n = len(ranked)
    heads, seconds, thirds = ranked[:min(n, 3)], ranked[:min(n, 6)], ranked[:min(n, 9)]
    unknown = [rid for rid in ranked if facts[rid]['unknown_exact_course']]
    if ranked_override is None and unknown and not any(x in thirds for x in unknown) and n > len(thirds):
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
        'seed': 1,   # 実行契約: KRS 5,000回・固定seed 1（研究KRSと同一）
        'static_prediction_frozen': True,
        'static_prediction': {
            'status': ('FROZEN / OWNER-AUTHORIZED R54 NUMERICAL CONSUMER (candidate ranking, Static widths 3/6/9) / RESULT-BLIND'
                       if ranked_override is not None else 'FROZEN / OWNER-AUTHORIZED / RULE-BASED-UNVALIDATED / RESULT-BLIND'),
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
              'numerical_prediction_consumption': ranked_override is not None, 'odds_consumed': False, 'result_consumed': False,
              'static_owner_v1_1_shadow_ranking': static_ranked,
              'numerical_prediction_consumer': (consumer or {}).get('profile') if ranked_override is not None else None}
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
    # The Runtime, the Static owner policy and the Full29 compiler use 高知 = KCH / 姫路 = HIM; the autopilot
    # queue uses the Rakuten-page codes KOC / HMJ. Translate for every formal-side call (fixes
    # HTTP_422 RAKUTEN_VENUE_NOT_IN_SCOPE, 2026-11-21); files, keys, 水分ボンバー and NAR tables keep KOC / HMJ.
    fv = FORMAL_VENUE.get(r['venue_id'], r['venue_id'])
    race = dict(r, venue_id=fv,
                formal_race_id=f"KM-LOCAL-{fv}-{r['race_date'].replace('-', '')}-R{r['race_no']:02d}-RKT")
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
        authority = resolve_authority(_now())
        summary['authority'] = authority
        numeric_krs = authority['consumption']['krs_input_authority']
        base = _endpoint()
        hc, health = _call(base, '/health', None, 30)
        if hc >= 300 or health.get('status') != 'READY':
            raise FormalStop('SOURCE_FREEZE', f'RUNTIME_NOT_READY:{hc}')
        pub = health['receipt_public_key_b64']
        policy = json.loads(POLICY_PATH.read_text())
        guard('SOURCE_FREEZE')
        sc, src = _call(base, '/source/acquire', {
            'family_id': 'LOCAL', 'race_id': race['formal_race_id'], 'manifest_profile': RAKUTEN_PROFILE,
            'venue_id': fv, 'race_date': r['race_date'], 'race_no': r['race_no'],
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
        # Owner 2026-11-21 13:09 / 13:32「全てを指数に接続し常に改善」: measured NAR / 競馬ブック / 水分ボンバー values,
        # attached to the card rows BEFORE Full29 (neutral slots get evidence) and kept for the ranking layer.
        from runtime.local_autopilot import ext_connect
        ext_pre, ext_pre_error = None, None
        if ext_connect.enabled(r['race_date']):
            try:
                def _sbo_fetch():
                    from runtime.local_autopilot import sbo
                    snap = sbo.snapshot(sbo.Client(Path(out_dir).parent / 'sbo_state.json'), r['race_date'], r['venue_id'], r['race_no'])
                    return snap, _now().astimezone(JST).isoformat()
                ext_pre = ext_connect.prepare(r, head, active, out_dir, deadline, _sbo_fetch, _now())
            except Exception as exc:
                ext_pre_error = f'PREPARE:{type(exc).__name__}:{str(exc)[:200]}'
                for x in active:
                    x.pop('external_evidence', None)
        guard('NUMERICAL_MATERIALIZATION')
        try:
            sh = shadow29.run_production({'venue_id': fv, 'venue_name': r['venue_name'], 'race_no': r['race_no'],
                                          'race_date': r['race_date'], 'distance': head.get('distance'),
                                          'surface': head.get('surface'), 'going': head.get('going'),
                                          'race_name': head.get('race_name'), 'post_current': r['post_current'],
                                          'rid': r['rid']}, active, html, snap['fetched_at'])
        except Exception as exc:
            raise FormalStop('NUMERICAL_MATERIALIZATION', f'PRODUCTION_MATERIALIZER:{type(exc).__name__}:{str(exc)[:200]}')
        krs_input = sh.pop('_krs_input', None)
        arts['full29'] = sh
        cov = sh['numeric_coverage']
        numerical = {'required_indices': sh['required_indices'], 'strict_full_numerical_ready': sh['strict_full_numerical_ready'],
                     'production_numerical_authority': sh['production_numerical_authority']}
        if (len(numerical['required_indices']) != 29 or not sh['full_numerical_closure'] or krs_input is None
                or sh['implementation_value_equivalence'] != 'PASS'):
            raise FormalStop('NUMERICAL_MATERIALIZATION', f"FULL29_NOT_CLOSED:{cov}:{sh['implementation_value_equivalence']}")
        mark('NUMERICAL_MATERIALIZATION', materializer=sh['materializer_profile'], cells=sh['cells'],
             calculated=cov['calculated_count'], ruled_neutral=cov['ruled_neutral_count'],
             full_numerical_closure=True, terminalization_hash=sh['index_terminalization_hash'])
        mark('INDEX_PROVENANCE', provenance_hash=sh['index_provenance_hash'],
             evidence_registry=sh['evidence_registry_id'], mapping=sh['mapping_id'],
             implementation_value_equivalence=sh['implementation_value_equivalence'])
        guard('STATIC_FREEZE')
        consumer = authority.get('numerical_prediction_consumer')
        num_rank, num_pred = (numerical_ranking(sh) if consumer else (None, None))
        if num_pred:
            arts['numerical_prediction'] = num_pred
        num_rank_base = num_rank
        if num_pred and ext_pre is not None:
            try:
                conn = ext_connect.connect(ext_pre, num_pred)
                arts['ext_connection'] = conn
                num_rank = conn['ranking']
                mark('EXT_CONNECTION', profile=conn['profile'], sbo=conn['sbo'].get('status'),
                     keibabook=conn['keibabook'].get('status'), nar_tables=conn['status']['tables'],
                     full29_slots=conn['status']['full29_slots'], changed_top3=conn['changed_top3'],
                     ranking_base=conn['ranking_base'], ranking=conn['ranking'])
            except Exception as exc:   # the connection must never block the formal prediction
                arts['ext_connection'] = {'status': 'ERROR', 'error': f'{type(exc).__name__}:{str(exc)[:200]}'}
                mark('EXT_CONNECTION', status='ERROR_BASE_RANKING_USED')
        elif ext_pre_error:
            arts['ext_connection'] = {'status': 'ERROR', 'error': ext_pre_error}
        req, ledger = build_static(race, src, active, numerical, policy, _now(), ranked_override=num_rank, consumer=consumer)
        arts['static_ledger'] = ledger
        mark('STATIC_FREEZE', ledger_sha256=ledger['sha256'], ranking=req['static_prediction']['ranking'])
        roles = req['static_prediction']['roles']
        kin = copy.deepcopy(krs_input)
        for h in kin['horses']:
            h['static_roles'] = roles.get(str(h['horse_no']), [])
        if numeric_krs:
            kin.setdefault('keibametrics_input_authority', {}).update({
                'input_mode': 'FORMAL_NUMERICAL', 'full_numerical_calculation': True, 'full_terminalization': True,
                'proxy_reason': None, 'bridge_id': 'local_krs_bridge_candidate/PRODUCTION_FULL29',
                'authority_manifest': authority['manifest_id']})
        else:
            kin.setdefault('keibametrics_input_authority', {}).update({
                'input_mode': 'TECHNICAL_PROXY_DIAGNOSTIC', 'full_numerical_calculation': False, 'full_terminalization': True,
                'proxy_reason': f"{authority['manifest_id']}: LOCAL numerical KRS-input consumer false; SOURCE-derived technical proxy"})
        kin.setdefault('race', {})['race_id'] = race['formal_race_id']
        kin.setdefault('simulation', {}).update({'run_count': 5000, 'master_seed': req['seed']})
        arts['krs_input'] = copy.deepcopy(kin)   # kept for the KRS calibration re-runs (KCP 2026-11-26; derived values only)
        try:   # automatic KRS input variant (auto_policy, Owner 2026-11-28 「改善は承認無しで」); base input kept above
            from runtime.local_autopilot import auto_policy
            kin2, kvar = auto_policy.krs_input_for(kin, Path(out_dir).parent, r['race_date'])
            if kvar:
                kin = kin2
                arts['krs_input_variant'] = kvar
                mark('AUTO_POLICY_KRS', variant=kvar)
        except Exception as exc:
            mark('AUTO_POLICY_KRS', status=f'ERROR_BASE_INPUT_KEPT:{type(exc).__name__}:{str(exc)[:120]}')
        guard('PRE_KRS')
        pc, pre = _call(base, '/pre-krs', {'family_id': 'LOCAL', 'race_id': race['formal_race_id'], 'source_receipt': src,
                                          'krs_input_data': kin, 'full_terminalization': True,
                                          'full_numerical_calculation': bool(numeric_krs),
                                          'krs_input_mode': kin['keibametrics_input_authority']['input_mode'],
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
        from krs_prediction_utility import build_krs_prediction_utility
        try:
            utility = build_krs_prediction_utility(req, {'status': 'EXECUTED', 'output': copy.deepcopy(ka.get('raw_output') or {})})
        except Exception as exc:
            utility = None
            arts['krs_utility_error'] = {'error': f'{type(exc).__name__}:{str(exc)[:200]}'}
        if utility is not None:
            arts['krs_prediction_utility'] = utility
        mark('KRS_UTILITY', utility_class=(utility or {}).get('utility_class'), utility_sha256=(utility or {}).get('sha256'),
             production_effect='MEC_SHADOW_ONLY (existing MEC R3 keeps KRS proposals non-capitalised; no new selection policy)')
        guard('MEC')
        req, closure = canonicalize_role_pair_third_closure(req)
        mec = build_mec_plan(req, utility, strict_head_closure=True, min_stake=100)
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
        freeze_at = datetime.fromisoformat(stages['SOURCE_FREEZE'])
        states = prior_learning_states(out_dir, race['formal_race_id'], freeze_at, pub)
        bindings, enforced = [], []
        for st in states:
            for item in st.get('immediate_correctness') or []:
                if item == 'MEC_PRECOMPRESSION_SEMANTIC_UNIVERSE_REQUIRED':
                    if mec.get('precompression_semantic_universe') is not True:
                        raise FormalStop('MEC', 'LEARNING_IMMEDIATE_CORRECTNESS_FAILED:' + item)
                    enforced.append({'state_id': st['state_id'], 'item': item, 'status': 'SATISFIED'})
                else:
                    raise FormalStop('MEC', 'LEARNING_IMMEDIATE_CORRECTNESS_UNKNOWN:' + item)
            bindings.append({'state_id': st['state_id'], 'state_sha256': st['sha256'],
                             'result_receipt_sha256': st.get('result_receipt_sha256'),
                             'effective_time': st['effective_time'],
                             'immediate_correctness': st.get('immediate_correctness') or [],
                             'shadow_candidates': st.get('shadow_candidates') or [],
                             'use': 'IMMEDIATE_CORRECTNESS_ENFORCED + SHADOW_RECORDED (production_change_authorized=false)'})
        cap_cfg = authority.get('local_ticket_cap')
        capped = cap_tickets(tickets, req['static_prediction']['ranking'], int(cap_cfg['max_tickets'])) \
            if cap_cfg and not no_bet else None
        promo = None
        if capped and not no_bet:   # Owner 2026-11-21 20:00: pre-registered same-budget variant promoted automatically
            try:
                from runtime.local_autopilot import auto_promote, formal_mix
                promo = auto_promote.active_variant(Path(out_dir).parent, r['race_date'])
                if promo:
                    capped = auto_promote.apply_to_cap(capped, req['static_prediction']['ranking'], roles, tickets,
                                                       formal_mix._market_order(Path(out_dir), key), promo,
                                                       krs=arts.get('krs_prediction_utility'),
                                                       abl_src={'full29': arts.get('full29'),
                                                                'ext': (arts.get('ext_connection') or {}).get('runners') or {}})
                    capped['sha256'] = _sha(capped)
                    mark('AUTO_PROMOTION', candidate=promo['candidate'], variant=promo['variant'],
                         tickets=len(capped['tickets']), investment=capped['kept_investment'])
            except Exception as exc:   # never block the formal prediction: keep the R54_60 cap
                promo = None
                mark('AUTO_PROMOTION', status=f'ERROR_R54_60_KEPT:{type(exc).__name__}:{str(exc)[:120]}')
        budget = None
        if capped and not no_bet:   # automatic point-reducing series (auto_policy, Owner 2026-11-28); never adds points
            try:
                from runtime.local_autopilot import auto_policy
                capped2, budget = auto_policy.apply_budget(capped, req['static_prediction']['ranking'],
                                                           arts.get('numerical_prediction'), arts.get('krs_prediction_utility'),
                                                           Path(out_dir).parent, r['race_date'])
                if capped2 is not capped:
                    capped = capped2
                    capped['sha256'] = _sha(capped)
                if budget:
                    mark('AUTO_POLICY_BUDGET', **{k: budget.get(k) for k in ('series', 'applied')}, tickets=len(capped['tickets']))
            except Exception as exc:
                budget = None
                mark('AUTO_POLICY_BUDGET', status=f'ERROR_TICKETS_KEPT:{type(exc).__name__}:{str(exc)[:120]}')
        if capped:
            mark('LOCAL_TICKET_CAP', max_tickets=capped['max_tickets'], mec_ticket_count=capped['mec_ticket_count'],
                 kept=capped['kept_count'], kept_investment=capped['kept_investment'], sha256=capped['sha256'])
        fpp = {'ranking': req['static_prediction']['ranking'], 'roles': roles, 'marks': req['static_prediction']['marks'],
               'local_ticket_cap': capped, 'prediction_consumer': (consumer or {}).get('profile'),
               'source_snapshot_sha256': art['source_snapshot_sha256'], 'static_ledger_sha256': ledger['sha256'],
               'local_krs_input_sha256': _sha(kin), 'krs_input_mode': kin['keibametrics_input_authority']['input_mode'],
               'minimum_efficient_coverage': mec,
               'krs_prediction_utility_shadow': utility, 'owner_policy': policy['profile'],
               'current_authority': {k: authority[k] for k in ('manifest_id', 'file_sha256', 'resolved_at')},
               'learning_state_bindings': bindings, 'learning_immediate_correctness': enforced}
        try:
            from jra_next_race_learning_binding_audit import audit_learning_consumption
            arts['learning_binding_audit'] = audit_learning_consumption(
                race_id=race['formal_race_id'], source_freeze=stages['SOURCE_FREEZE'], prediction_cutoff=deadline.isoformat(),
                learning_states=states, prediction_input=fpp, family_id='LOCAL')
        except Exception as exc:
            arts['learning_binding_audit'] = {'error': f'{type(exc).__name__}:{str(exc)[:200]}'}
        mark('LEARNING_BINDING', eligible_states=len(states), bound=len(bindings), enforced=len(enforced))
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
        full_numeric_pre = (pre.get('artifact') or {}).get('full_numerical_calculation') is True
        summary.update(status='SIGNED_FINAL', final_receipt_sha256=fin['receipt_sha256'],
                       formal_status='FULL_FORMAL_E2E_PASS' if full_numeric_pre else 'FORMAL_E2E_TERMINALIZED_PROXY_KRS_PASS',
                       final_verified_remote=vfc < 300 and vf.get('valid') is True, final_verified_local=True,
                       ticket_count=len(capped['tickets']) if capped else len(tickets),
                       total_investment=capped['kept_investment'] if capped else total, no_bet=no_bet,
                       signed_final_ticket_count=len(tickets), signed_final_total_investment=total,
                       signed_final_tickets=tickets, local_ticket_cap_sha256=(capped or {}).get('sha256'),
                       prediction_consumer=(consumer or {}).get('profile'),
                       ranking=fpp['ranking'], marks=fpp['marks'], ranking_base=num_rank_base,
                       auto_promotion=(capped or {}).get('auto_promotion'),
                       tickets_r54_60=(capped or {}).get('champion_r54_60_tickets'),
                       tickets_before_budget=(capped or {}).get('tickets_before_budget'), budget_policy=budget,
                       krs_input_variant=arts.get('krs_input_variant'),
                       ext_connection=(None if 'ext_connection' not in arts else
                                       {k: arts['ext_connection'].get(k) for k in ('profile', 'status', 'sbo', 'keibabook',
                                                                                   'changed_top3', 'changed_top6', 'error')}),
                       roles={k: v for k, v in roles.items()}, krs_actual_run_count=ka['actual_run_count'],
                       before_cutoff=_now() < deadline, tickets=capped['tickets'] if capped else tickets,
                       krs_input_mode=kin['keibametrics_input_authority']['input_mode'],
                       learning_state_bindings=[b['state_id'] for b in bindings])
        stages['SIGNED_FINAL'] = _now().isoformat()
        if ext_pre is not None:   # C26 comparison base: the same card WITHOUT any external evidence (record only)
            try:
                plain = [{k: v for k, v in x.items() if k != 'external_evidence'} for x in active]
                sh0 = shadow29.run_production({'venue_id': fv, 'venue_name': r['venue_name'], 'race_no': r['race_no'],
                                               'race_date': r['race_date'], 'distance': head.get('distance'),
                                               'surface': head.get('surface'), 'going': head.get('going'),
                                               'race_name': head.get('race_name'), 'post_current': r['post_current'],
                                               'rid': r['rid']}, plain, html, snap['fetched_at'])
                summary['ranking_no_external'] = numerical_ranking(sh0)[0]
            except Exception as exc:
                summary['ranking_no_external_error'] = f'{type(exc).__name__}:{str(exc)[:160]}'
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

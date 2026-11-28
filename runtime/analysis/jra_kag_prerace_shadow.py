"""KAG-JRA v1 pre-start governance Shadow (research only, never a FINAL gate).

The old BLUE/RED/PURPLE v1.0-CANDIDATE is not Production Authority.
This module only reads immutable FINAL prediction files for a future race.
It MUST NOT load result, settlement, learning, or post-result audit to form
pre-start challenges. No pre-start fix, ticket rewrite, owner approval, or
independent LEVEL-3 AI audit is implied. Persisted Git commit chronology must
be verified separately before any future-OOS claim.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
PROFILE = 'KM-JRA-KAG-PRERACE-SHADOW-v1.0'
FAMILY = 'JRA'
RACE_KEY = re.compile(r'^KM-JRA-[A-Z]{3}-20\d{6}-R\d{2}$')
LAYERS = ('RED-1', 'RED-2', 'RED-3', 'RED-4', 'RED-5')


def _read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def _parse_timestamp(raw):
    if not isinstance(raw, str) or not raw:
        raise ValueError('TIMESTAMP_REQUIRED')
    value = datetime.fromisoformat(raw.replace('Z', '+00:00'))
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError('TIMEZONE_REQUIRED')
    return value


def _hash(raw):
    return hashlib.sha256(raw).hexdigest()


def analyze_final(final, *, race_id, now, artifact_sha256):
    """Analyze only signed-FINAL-shaped data; no RESULT object in the API."""
    if not RACE_KEY.fullmatch(race_id) or final.get('race_id') != race_id:
        raise ValueError('RACE_KEY_MISMATCH')
    if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
        raise ValueError('AWARE_CLOCK_REQUIRED')
    post = _parse_timestamp(final.get('scheduled_post_at'))
    freeze = _parse_timestamp(final.get('final_freeze_timestamp'))
    if not freeze < post or not freeze <= now < post:
        raise ValueError('NOT_PRESTART_ELIGIBLE')
    frozen = (final.get('final_prediction_package') or {})
    tickets = (final.get('final_ticket') or {})
    roles = frozen.get('roles') or {}
    ranking = [str(h) for h in (frozen.get('ranking') or [])]
    role_names = {str(k): set(v) for k, v in roles.items() if isinstance(v, list)}
    selections = tickets.get('tickets') or []
    ticket_count = len(selections)
    bet = Counter(str(t.get('bet_type', '')).upper() for t in selections if isinstance(t, dict))
    full_rank = set(ranking)
    wagered = not tickets.get('no_bet') and ticket_count > 0

    checks = []
    challenges = []
    def record(layer, code, status, severity, evidence, response='UNKNOWN', disposition='NO-CHANGE', basis=''):
        row = {'layer': layer, 'code': code, 'status': status,
               'severity': severity, 'evidence': evidence,
               'blue_response': {'response': response, 'basis': basis,
                                 'execution': 'RULE_BOUND_MACHINE_REVIEW'},
               'purple': {'disposition': disposition,
                          'authority': 'RESEARCH_ONLY; OWNER_APPROVAL_REQUIRED_FOR_PRODUCTION'},
               'independence': 'LEVEL-1'}
        checks.append(row)
        if status == 'CHALLENGE':
            challenges.append(row)

    # RED-1: audit only frozen-file fields. Never claim independent SOURCE verification.
    if not ranking or len(ranking) != len(full_rank) or any(not x.isdigit() for x in ranking):
        record('RED-1', 'FROZEN_RANKING_INVALID', 'CHALLENGE', 'P0',
               {'runner_count': len(ranking), 'unique_count': len(full_rank)},
               'ACCEPT', 'REGRESSION-ONLY', 'frozen ranking contract')
    else:
        record('RED-1', 'FROZEN_RANKING_UNIQUE', 'PASS', 'INFO',
               {'runner_count': len(ranking)}, 'EXISTING', 'NO-CHANGE', 'frozen FINAL')
    invalid = [i for i, t in enumerate(selections) if not isinstance(t, dict) or
               not isinstance(t.get('selection'), list) or
               len(t['selection']) != len(set(str(v) for v in t['selection'])) or
               any(str(v) not in full_rank for v in t['selection'])]
    if invalid:
        record('RED-1', 'TICKET_RUNNER_UNIVERSE_MISMATCH', 'CHALLENGE', 'P0',
               {'ticket_indices': invalid}, 'ACCEPT', 'REGRESSION-ONLY', 'frozen ticket vs ranking')
    else:
        record('RED-1', 'TICKET_RUNNER_UNIVERSE', 'PASS', 'INFO',
               {'tickets_checked': ticket_count}, 'EXISTING', 'NO-CHANGE', 'frozen ticket vs ranking')
    record('RED-1', 'OFFICIAL_SOURCE_REVERIFY', 'UNKNOWN', 'INFO',
           {'source_signature_independently_verified': False,
            'reason': 'pre-start Shadow does not re-fetch JRA official SOURCE'},
           'UNKNOWN', 'NO-CHANGE', 'existing Production source gate is independent')

    # RED-2: possible winner alternatives WITHOUT asserting the eventual winner.
    w_candidates = [h for h in ranking if 'W' in role_names.get(h, set())]
    top3_not_w = [h for h in ranking[:3] if h not in w_candidates]
    record('RED-2', 'STATIC_TOP3_NOT_W', 'CHALLENGE' if top3_not_w else 'PASS', 'P2',
           {'static_top3_not_w': top3_not_w, 'w_count': len(w_candidates)},
           'PARTIAL' if top3_not_w else 'EXISTING',
           'SHADOW' if top3_not_w else 'NO-CHANGE',
           'role-selection research is not Production authority')

    # RED-3: material W/P2 relationships; Pair-local Third is explicitly UNKNOWN.
    p2 = {h for h, rr in role_names.items() if 'P2' in rr}
    uncovered = [h for h in w_candidates if not (p2 - {h})]
    record('RED-3', 'GLOBAL_P2_CANDIDATE_GAP',
           'CHALLENGE' if uncovered and wagered else 'UNKNOWN', 'P1',
           {'uncovered_w': uncovered if wagered else [], 'w_count': len(w_candidates),
            'note': 'global P2 membership does not establish head-local Pair closure'},
           'PARTIAL' if uncovered and wagered else 'UNKNOWN',
           'SHADOW' if uncovered and wagered else 'NO-CHANGE',
           'requires independently bound head-local P2 evidence')
    record('RED-3', 'PAIR_THIRD_SOURCE', 'UNKNOWN', 'INFO',
           {'reason': 'final headline roles alone cannot prove Pair-local Third closure'},
           'UNKNOWN', 'NO-CHANGE', 'require verified semantic graph readback')

    # RED-4: Owner's multi-primary preference, without adding any real ticket.
    ordered = bet['EXACTA'] + bet['TRIFECTA']
    multi = sum(bet[b] for b in ('TRIO', 'QUINELLA', 'WIDE', 'PLACE'))
    if wagered and ordered and multi == 0:
        record('RED-4', 'MULTI_PRIMARY_ABSENT', 'CHALLENGE', 'P1',
               {'ordered_ticket_count': ordered, 'multi_ticket_count': multi,
                'bet_type_counts': dict(bet)}, 'PARTIAL', 'SHADOW',
               'Owner multi-primary policy; MP-A/MP-B are Shadow only')
    else:
        record('RED-4', 'MULTI_PRIMARY_ABSENT', 'PASS', 'INFO',
               {'ordered_ticket_count': ordered, 'multi_ticket_count': multi,
                'no_bet': not wagered}, 'EXISTING', 'NO-CHANGE',
               'no assertion of multi-primary sufficiency')
    if wagered and len(w_candidates) > 1 and ordered:
        ordered_heads = {str(t['selection'][0]) for t in selections if isinstance(t, dict)
                         and t.get('bet_type') in ('EXACTA', 'TRIFECTA') and t.get('selection')}
        missing = sorted(set(w_candidates) - ordered_heads, key=lambda h: ranking.index(h) if h in ranking else 999)
        if missing:
            record('RED-4', 'W_HEAD_NOT_IN_ORDERED_TICKETS', 'CHALLENGE', 'P1',
                   {'missing_w': missing, 'ordered_heads': sorted(ordered_heads)},
                   'PARTIAL', 'SHADOW', 'final Role-to-Ticket closure')
    if wagered:
        ordered_stake = sum(int(t.get('stake') or 0) for t in selections if isinstance(t, dict)
                            and t.get('bet_type') in ('EXACTA', 'TRIFECTA'))
        multi_stake = sum(int(t.get('stake') or 0) for t in selections if isinstance(t, dict)
                          and t.get('bet_type') in ('TRIO', 'QUINELLA', 'WIDE', 'PLACE'))
        if ordered_stake > multi_stake:
            record('RED-4', 'ORDERED_STAKE_EXCEEDS_MULTI', 'CHALLENGE', 'P1',
                   {'ordered_stake': ordered_stake, 'multi_stake': multi_stake},
                   'PARTIAL', 'SHADOW', 'same-budget MP-A/MP-B comparison required')

    # RED-5: missing independent registry inspection is UNKNOWN, never PASS.
    record('RED-5', 'RESEARCH_META_INDEPENDENCE', 'UNKNOWN', 'INFO',
           {'reason': 'candidate overlap, multiplicity and OOS lineage not audited by this pre-start reader'},
           'UNKNOWN', 'NO-CHANGE', 'requires independent research registry audit')

    return {'profile': PROFILE, 'race_id': race_id, 'scope': FAMILY,
            'production_effect': 'NONE', 'governance_authority': 'CANDIDATE / SHADOW',
            'independence': 'LEVEL-1', 'blue': {
                'formal_prediction_sha256': final.get('sha256'),
                'source_artifact_sha256': artifact_sha256,
                'scheduled_post_at': post.isoformat(),
                'production_final_frozen_at': freeze.isoformat(),
                'source_signature_reverified': False},
            'shadow_frozen_at': now.isoformat(),
            'prestart_time_check': 'PASSED',
            'git_first_commit_prestart_verified': False,
            'true_forward_oos': 'PENDING_INDEPENDENT_COMMIT_TIME_CHECK',
            'checks': checks,
            'summary': {'challenges': len(challenges),
                        'by_layer': dict(Counter(c['layer'] for c in challenges)),
                        'unknown_checks': sum(c['status'] == 'UNKNOWN' for c in checks),
                        'layer_coverage': {layer: sum(c['layer'] == layer for c in checks) for layer in LAYERS}}}


def freeze_day(root, date, *, now=None):
    if not re.fullmatch(r'20\d{2}-\d{2}-\d{2}', date):
        raise ValueError('DATE_FORMAT_REQUIRED')
    root = Path(root)
    now = now or datetime.now(timezone.utc)
    target = root / 'runtime/jra_governance/prerace'
    created, skipped = [], []
    for path in sorted((root / 'runtime/final_artifacts').glob('KM-JRA-*-'+date.replace('-', '')+'-R??.json')):
        rid = path.stem
        output = target / (rid+'.json')
        if output.exists():
            skipped.append({'race_id': rid, 'reason': 'IMMUTABLE_SHADOW_ALREADY_EXISTS'})
            continue
        try:
            raw = path.read_bytes()
            record = analyze_final(json.loads(raw), race_id=rid, now=now, artifact_sha256=_hash(raw))
        except (ValueError, OSError, TypeError, KeyError) as exc:
            skipped.append({'race_id': rid, 'reason': str(exc)[:120]})
            continue
        target.mkdir(parents=True, exist_ok=True)
        with output.open('x', encoding='utf-8') as out:
            json.dump(record, out, ensure_ascii=False, sort_keys=True, indent=2)
            out.write('\n')
        created.append(rid)
    return {'profile': PROFILE, 'date': date, 'created_count': len(created),
            'created_race_ids': created, 'skipped': skipped,
            'production_effect': 'NONE', 'true_forward_claim': False}


def audit_day(root, date):
    """Post-start linkage only: never rewrites a pre-start challenge."""
    root = Path(root)
    pre = root / 'runtime/jra_governance/prerace'
    post = root / 'runtime/jra_governance' / (date+'.json')
    jpost = _read(post) if post.exists() else None
    known = {r.get('race_id'): r for r in (jpost or {}).get('races', [])}
    rows = []
    for path in sorted(pre.glob('KM-JRA-*-'+date.replace('-', '')+'-R??.json')) if pre.exists() else []:
        record = _read(path)
        rows.append({'race_id': record.get('race_id'),
                     'prestart_shadow_sha256': _hash(path.read_bytes()),
                     'first_git_commit_prepost_verified': False,
                     'post_result_challenge_count': len(known.get(record.get('race_id'), {}).get('challenges', [])) if record.get('race_id') in known else None,
                     'status': 'POST_LINKED_RESEARCH_ONLY' if record.get('race_id') in known else 'POST_RESULT_PENDING'})
    result = {'profile': PROFILE+'-AUDIT', 'date': date, 'production_effect': 'NONE',
              'independence': 'LEVEL-1', 'forward_oos_performance_claim': False,
              'prestart_shadow_count': len(rows),
              'post_result_join_count': sum(x['status'] == 'POST_LINKED_RESEARCH_ONLY' for x in rows),
              'missing_independent_commit_proof': True, 'races': rows}
    out = root / 'runtime/jra_governance/pre_audit' / (date+'.json')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2)+'\n', encoding='utf-8')
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument('command', choices=('freeze', 'audit'))
    p.add_argument('date')
    args = p.parse_args()
    print(json.dumps(freeze_day(ROOT, args.date) if args.command == 'freeze' else audit_day(ROOT, args.date), ensure_ascii=False))


if __name__ == '__main__':
    main()

"""Single-factor role candidate replay on settled JRA races (NON-PRODUCTION, known-result replay).

Each candidate changes ONE role decision on top of the frozen FINAL, then rebuilds
tickets with the Production MEC (build_mec_plan) and settles them with the
Production settle_final at official JRA payouts. Static ranking, indices, AKI
rules, MEC and capital code are untouched. Results are regression evidence only,
never forward OOS, and never alter a signed FINAL.

Candidates
- W_PLUS_STATIC2: when the formal W set has exactly one head, add the Static rank-2
  runner to W as PROTECTED (REVIEW). Tests the single-axis width limit.
- P2_KRS_HEAD_LOCAL: for every formal W head, add the most frequent KRS exacta
  second for that head (if not already a P2) as PROTECTED P2. Tests head-local P2.
"""
import argparse, copy, glob, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'runtime'), str(ROOT / 'runtime/jra_source_runtime')]
from minimum_efficient_coverage import build_mec_plan  # noqa: E402
from jra_production_postresult import settle_final  # noqa: E402

LIVE = ('CORE', 'PROTECTED')


def _live(f, col):
    return [str(x['runner_id']) for x in f['role_registry'] if x['column'] == col and x['status'] in LIVE]


def _promote(f, col, rid, tag):
    for x in f['role_registry']:
        if x['column'] == col and str(x['runner_id']) == str(rid):
            if x['status'] in LIVE:
                return False
            x.update(status='PROTECTED', review_mode='REVIEW', reason=f'SHADOW_CANDIDATE:{tag}')
            return True
    return False


def _mirror_pairs(f, new_head=None, new_second=None, tag=''):
    """Give an added head/second the same pair/third structure as the formal roles.

    Production AKI derives these from compiled pair facts that the FINAL does not
    store, so the replay marks them PROTECT with reason SHADOW_MIRRORED_STRUCTURE
    (no registered pair evidence evaluated)."""
    W, P2, P3 = _live(f, 'W'), _live(f, 'P2'), _live(f, 'P3')
    pairs, thirds = f.setdefault('pair_dispositions', []), f.setdefault('third_dispositions', [])
    have = {(str(x['head']), str(x['second'])) for x in pairs}
    added = []
    for h in W:
        for s in P2:
            if h == s or (h, s) in have or (new_head and h != new_head and s != new_second and new_second is None) :
                continue
            if new_head and h != new_head:
                continue
            if new_second and s != new_second:
                continue
            pairs.append({'head': h, 'second': s, 'status': 'PROTECT', 'reason': 'SHADOW_MIRRORED_STRUCTURE:' + tag,
                          'rule_matches': []})
            added.append((h, s))
    for h, s in added:
        for t in P3:
            if t not in {h, s}:
                thirds.append({'head': h, 'second': s, 'third': t, 'status': 'PROTECT',
                               'reason': 'SHADOW_MIRRORED_STRUCTURE:' + tag, 'rule_matches': []})
    if new_head and new_head not in [str(x) for x in f.get('purchased_heads') or []]:
        f['purchased_heads'] = list(f.get('purchased_heads') or []) + [new_head]


def w_plus_static2(f):
    W = _live(f, 'W')
    rank = [str(r) for r in f['static_prediction']['ranking']]
    if len(W) != 1 or len(rank) < 2:
        return False
    nxt = next((r for r in rank if r not in W), None)
    if not (nxt and _promote(f, 'W', nxt, 'W_PLUS_STATIC2')):
        return False
    _mirror_pairs(f, new_head=nxt, tag='W_PLUS_STATIC2')
    return True


def p2_krs_head_local(f):
    occ = (f.get('krs_prediction_utility') or {}).get('top_exacta_occurrence') or []
    changed = False
    P2 = set(_live(f, 'P2'))
    for head in _live(f, 'W'):
        seconds = [str(o['P2']) for o in occ if str(o['W']) == head and str(o['P2']) != head]
        pick = next((s for s in seconds if s not in P2), None)
        if pick and _promote(f, 'P2', pick, 'P2_KRS_HEAD_LOCAL'):
            P2.add(pick); changed = True
            _mirror_pairs(f, new_head=head, new_second=pick, tag='P2_KRS_HEAD_LOCAL')
    return changed


def p2_static_next_control(f):
    """Control for P2_KRS_HEAD_LOCAL: same number of added P2 per head, chosen by Static rank."""
    rank = [str(r) for r in f['static_prediction']['ranking']]
    P2 = set(_live(f, 'P2'))
    changed = False
    for head in _live(f, 'W'):
        pick = next((r for r in rank if r != head and r not in P2), None)
        if pick and _promote(f, 'P2', pick, 'P2_STATIC_NEXT_CONTROL'):
            P2.add(pick); changed = True
            _mirror_pairs(f, new_head=head, new_second=pick, tag='P2_STATIC_NEXT_CONTROL')
    return changed


CANDIDATES = {'W_PLUS_STATIC2': w_plus_static2, 'P2_KRS_HEAD_LOCAL': p2_krs_head_local,
              'P2_STATIC_NEXT_CONTROL': p2_static_next_control}


def _settle(f, official):
    s = settle_final(f, official)
    return s.get('effective_investment', s.get('total_investment', 0)) or 0, s.get('total_payout', 0) or 0


def run(dates, root=ROOT):
    rows = []
    for d in dates:
        for p in sorted(glob.glob(str(root / f'runtime/final_artifacts/KM-JRA-*-{d}-R*.json'))):
            rid = Path(p).stem
            rp = root / 'runtime/results' / f'{rid}.json'
            if not rp.exists():
                continue
            final = json.loads(Path(p).read_text())
            if not (final.get('final_ticket') or {}).get('tickets'):
                continue  # PAPER / NO-BET: not in the paid denominator
            official = json.loads(rp.read_text())['official_result']
            top3 = [str(x) for x in official['finish_order'][:3]]
            base_inv, base_pay = _settle(final, official)
            row = {'race_id': rid, 'top3': top3, 'baseline': {'investment': base_inv, 'payout': base_pay,
                   'W_hit': top3[0] in _live(final, 'W'), 'P2_hit': top3[1] in _live(final, 'P2')}}
            for name, fn in CANDIDATES.items():
                f = copy.deepcopy(final)
                if not fn(f):
                    row[name] = None
                    continue
                try:
                    mec = build_mec_plan(f)
                except Exception as exc:  # MEC refusal is itself a result
                    row[name] = {'mec_refused': str(exc)[:160], 'investment': row['baseline']['investment'],
                                 'payout': row['baseline']['payout'], 'W_hit': row['baseline']['W_hit'],
                                 'P2_hit': row['baseline']['P2_hit']}
                    continue
                f['final_ticket'] = {**f['final_ticket'], 'tickets': mec['tickets'],
                                     'total_investment': mec['minimum_required_capital']}
                inv, pay = _settle(f, official)
                row[name] = {'investment': inv, 'payout': pay, 'W_hit': top3[0] in _live(f, 'W'),
                             'P2_hit': top3[1] in _live(f, 'P2'), 'tickets': mec['ticket_count']}
            rows.append(row)
    return rows


def summarize(rows):
    out = {}
    for name in ['baseline', *CANDIDATES]:
        changed = [r for r in rows if r.get(name)] if name != 'baseline' else rows
        tot = lambda key, rs, side: sum((r[side] if r.get(side) else r['baseline'])[key] for r in rs)
        if name == 'baseline':
            inv, pay = tot('investment', rows, 'baseline'), tot('payout', rows, 'baseline')
            wh = sum(r['baseline']['W_hit'] for r in rows); p2 = sum(r['baseline']['P2_hit'] for r in rows)
        else:
            inv = sum((r[name] or r['baseline'])['investment'] for r in rows)
            pay = sum((r[name] or r['baseline'])['payout'] for r in rows)
            wh = sum((r[name] or r['baseline'])['W_hit'] for r in rows)
            p2 = sum((r[name] or r['baseline'])['P2_hit'] for r in rows)
        pays = sorted(((r[name] or r['baseline']) if name != 'baseline' else r['baseline'])['payout'] for r in rows)
        out[name] = {'races': len(rows), 'changed_races': len(changed) if name != 'baseline' else 0,
                     'investment': inv, 'payout': pay, 'pfs': round(pay / inv * 100, 2) if inv else None,
                     'pfs_excl_max_payout': round((pay - pays[-1]) / inv * 100, 2) if inv and pays else None,
                     'W_hit': wh, 'P2_hit': p2,
                     'hit_races': sum(1 for r in rows if ((r[name] or r['baseline']) if name != 'baseline' else r['baseline'])['payout'] > 0)}
    return out


# ---- Forward OOS: freeze candidate tickets before post, evaluate after RESULT ----
FWD = 'runtime/jra_role_candidate_forward'


def _sha(obj):
    import hashlib
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def freeze_forward(date8, root=ROOT, now=None):
    """Freeze every candidate's role set and tickets for FINALs whose post time is still ahead.

    Never freezes after the scheduled post (or for races already resulted); existing
    freezes are immutable."""
    import datetime as dt
    now = now or dt.datetime.now(dt.timezone.utc)
    made = []
    for p in sorted(glob.glob(str(root / f'runtime/final_artifacts/KM-JRA-*-{date8}-R*.json'))):
        rid = Path(p).stem
        out = root / FWD / rid / 'pre_result.json'
        if out.exists() or (root / 'runtime/results' / f'{rid}.json').exists():
            continue
        final = json.loads(Path(p).read_text())
        post = dt.datetime.fromisoformat(final['scheduled_post_at'])
        if now >= post:
            continue
        body = {'profile': 'KM-JRA-ROLE-CANDIDATE-FORWARD-v1', 'race_id': rid, 'final_sha256': final.get('sha256'),
                'scheduled_post_at': final['scheduled_post_at'], 'frozen_at': now.isoformat(),
                'code_sha256': _sha(Path(__file__).read_text()), 'production_effect': 'NONE', 'arms': {}}
        for name, fn in CANDIDATES.items():
            f = copy.deepcopy(final)
            if not (final.get('final_ticket') or {}).get('tickets') or not fn(f):
                body['arms'][name] = None
                continue
            try:
                mec = build_mec_plan(f)
            except Exception as exc:
                body['arms'][name] = {'mec_refused': str(exc)[:160]}
                continue
            body['arms'][name] = {'W': _live(f, 'W'), 'P2': _live(f, 'P2'), 'P3': _live(f, 'P3'),
                                  'tickets': mec['tickets'], 'investment': mec['minimum_required_capital']}
        body['sha256'] = _sha(body)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(body, ensure_ascii=False, indent=1) + '\n')
        made.append(rid)
    return made


def evaluate_forward(root=ROOT):
    rows = []
    for p in sorted(glob.glob(str(root / FWD / '*' / 'pre_result.json'))):
        pre = json.loads(Path(p).read_text())
        rid = pre['race_id']
        rp = root / 'runtime/results' / f'{rid}.json'
        if not rp.exists():
            continue
        official = json.loads(rp.read_text())['official_result']
        if not official.get('captured_at') or pre['frozen_at'] >= official['captured_at']:
            continue  # only freezes made before the result count as forward OOS
        final = json.loads((root / 'runtime/final_artifacts' / f'{rid}.json').read_text())
        if not (final.get('final_ticket') or {}).get('tickets'):
            continue
        base_inv, base_pay = _settle(final, official)
        row = {'race_id': rid, 'baseline': {'investment': base_inv, 'payout': base_pay}}
        for name, arm in pre['arms'].items():
            if not arm or 'tickets' not in arm:
                row[name] = None
                continue
            f = copy.deepcopy(final)
            f['final_ticket'] = {**f['final_ticket'], 'tickets': arm['tickets'], 'total_investment': arm['investment']}
            inv, pay = _settle(f, official)
            row[name] = {'investment': inv, 'payout': pay}
        rows.append(row)
    agg = {}
    for name in ['baseline', *CANDIDATES]:
        inv = sum((r.get(name) or r['baseline'])['investment'] for r in rows)
        pay = sum((r.get(name) or r['baseline'])['payout'] for r in rows)
        agg[name] = {'races': len(rows), 'investment': inv, 'payout': pay,
                     'pfs': round(pay / inv * 100, 2) if inv else None}
    return {'classification': 'FORWARD_OOS (frozen before result)', 'note': 'no significance claim below 100 races',
            'summary': agg}


if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] in ('freeze', 'evaluate'):
    if sys.argv[1] == 'freeze':
        print(json.dumps({'frozen': freeze_forward(sys.argv[2].replace('-', ''))}))
    else:
        print(json.dumps(evaluate_forward(), ensure_ascii=False, indent=1))
    sys.exit(0)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--dates', nargs='+', required=True); ap.add_argument('--out')
    a = ap.parse_args()
    rows = run([d.replace('-', '') for d in a.dates])
    rep = {'profile': 'KM-JRA-ROLE-CANDIDATE-REPLAY-v1', 'classification': 'KNOWN_RESULT_REPLAY / NOT_FORWARD_OOS / NON_PRODUCTION',
           'summary': summarize(rows), 'races': rows}
    if a.out:
        Path(a.out).write_text(json.dumps(rep, ensure_ascii=False, indent=1) + '\n')
    print(json.dumps(rep['summary'], ensure_ascii=False, indent=1))

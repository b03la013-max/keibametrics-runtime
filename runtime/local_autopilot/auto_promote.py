"""Automatic promotion / demotion of pre-registered same-budget ticket variants (Owner 2026-11-21 20:00 JST
「作って下さい」 for the proposal of 19:59: reflections -> improvements applied automatically, with safeguards).

Rules (fixed before any decision; changing them needs the Owner; 2026-11-22 21:31 Owner: generated candidates
from auto_candidates.py join the list, and challengers keep being judged while a variant is promoted):
  * Only PRE-REGISTERED candidates that are complete same-budget ticket sets built from the signed formal
    summary are eligible (formal_mix variants: C13 MIX_P2BOX20, C15 MIX_WAXIS_TRIO, C22 KEEP_MEC_TRIO20,
    C24 W_PLUS_TOP2POP_60, C28 CORE_LAYER_60 from 2026-11-22). Same races, same 60 points, official payouts.
  * PROMOTE when, on >= 100 races after the candidate's first eligible post (and after any earlier demotion):
      candidate PFS > champion PFS, candidate PFS without the single largest payout > champion's,
      candidate hit races >= champion's, and in >= 2 venues with >= 12 races each the candidate PFS is higher
      while no venue with >= 12 races is worse by more than 30 points.
    Several qualify -> the one with the highest PFS without the largest payout.
  * The promoted variant becomes the delivered (and signed) recommendation from the NEXT race day.
  * PROBATION: after >= 100 races under the promoted variant, if its PFS AND its PFS without the largest
    payout are both below the signed R54_60 cap (the original champion) on those races -> automatic DEMOTION
    to R54_60 from the next race day; the candidate may qualify again only on races after the demotion.
  * Every decision is appended to output/auto_promotion.json and sent with the daily report.
The 29 indices, KRS, MEC, the 60-ticket cap size and the purchase policy (recommendation only) are untouched.
"""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path

PROFILE = 'KM-LOCAL-AUTO-PROMOTION-v1.0-20261121'
CHAMPION = 'R54_60'
MIN_RACES = 100
MIN_VENUE_RACES = 12
MIN_VENUES = 2
VENUE_WORSE_LIMIT = 30.0
REPO = Path(__file__).resolve().parents[2]
CANDIDATES = {   # id -> (formal_mix variant, prereg file)
    'C13-FORMAL-MIX-P2BOX20': ('MIX_P2BOX20', 'KM_LOCAL_FORWARD_OOS_PREREG_20261118_R5.json'),
    'C15-FORMAL-MIX-WAXIS-TRIO': ('MIX_WAXIS_TRIO', 'KM_LOCAL_FORWARD_OOS_PREREG_20261118_R5.json'),
    'C22-KEEP-MEC-TRIO20': ('KEEP_MEC_TRIO20', 'KM_LOCAL_FORWARD_OOS_PREREG_20261120_R8.json'),
    'C24-W-PLUS-TOP2POP-SAME-BUDGET': ('W_PLUS_TOP2POP_60', 'KM_LOCAL_FORWARD_OOS_PREREG_20261120_R9.json'),
    'C28-CORE-LAYER-60': ('CORE_LAYER_60', 'KM_LOCAL_FORWARD_OOS_PREREG_20261122_R12.json'),
    'C29-KRS-CAP-60': ('GEN:KRSCAP:mode=1', 'KM_LOCAL_FORWARD_OOS_PREREG_20261125_R13.json'),
    'C30-KRS-CAP-TEMPERED-60': ('GEN:KRSCAP:mode=1:t=165', 'KM_LOCAL_FORWARD_OOS_PREREG_20261127_R14.json'),
    'C31-W-PLUS-KRS-TOP1-60': ('GEN:KRSW:n=1', 'KM_LOCAL_FORWARD_OOS_PREREG_20261128_R15.json'),
    'C32-SCTP-TRIO10-60': ('GEN:TRIOPROT:k=6', 'KM_LOCAL_FORWARD_OOS_PREREG_20261129_R16.json'),
    'C33-SCTP-TRIO20-60': ('GEN:TRIOPROT:k=12', 'KM_LOCAL_FORWARD_OOS_PREREG_20261129_R16.json'),
    'C34-SCTP-TRIO30-60': ('GEN:TRIOPROT:k=18', 'KM_LOCAL_FORWARD_OOS_PREREG_20261129_R16.json'),
}
# Owner-decided promotions (not automatic). Applied once into the state: the variant becomes the delivered one from
# effective_from, replacing whatever is active. Probation uses the pre-registered revert rule of the candidate.
# Rollback: delete the entry (or set 'withdrawn': True) and set output/auto_promotion.json 'active' back.
OWNER_PROMOTIONS = [
    {'candidate': 'C24-W-PLUS-TOP2POP-SAME-BUDGET', 'variant': 'W_PLUS_TOP2POP_60', 'effective_from': '2026-11-27',
     'decided_at': '2026-11-26T23:00:00+09:00', 'owner_words': 'Aでよろしく／それでもC24に切替',
     'decision_profile': 'KM_LOCAL_FORWARD_OOS_DECISION_20261126_C24.json',
     # prereg R9: revert if PFS excluding top-1 falls below the R54_60 replay over the next 100 races
     'revert_rule': 'PFS_EX_TOP1'},
]


def _apply_owner(st, owner=None):
    owner = OWNER_PROMOTIONS if owner is None else owner
    done = st.setdefault('owner_applied', [])
    for o in owner:
        tag = f"{o['candidate']}@{o['effective_from']}"
        if o.get('withdrawn') or tag in done:
            continue
        prev_a = st.get('active')
        prev = (prev_a or {}).get('candidate')
        st['active'] = {'previous': {k: v for k, v in prev_a.items() if k != 'previous'} if prev_a else None,
                        'candidate': o['candidate'], 'variant': o['variant'], 'effective_from': o['effective_from'],
                        'promoted_on': o['decided_at'][:10], 'by': 'OWNER', 'revert_rule': o.get('revert_rule')}
        st.setdefault('blocked_until', {}).pop(o['candidate'], None)
        st['history'] = (st.get('history') or [])[-100:] + [{
            'decided_at': o['decided_at'], 'day': o['decided_at'][:10], 'action': 'OWNER_PROMOTE',
            'candidate': o['candidate'], 'variant': o['variant'], 'effective_from': o['effective_from'],
            'replaced': prev, 'owner_words': o.get('owner_words')}]
        done.append(tag)
    return st


def candidates(root):
    """-> {id: (variant, first_eligible_day)}: the fixed pre-registered candidates + the generated ones still
    being evaluated (auto_candidates.json in the data root, registered before their first eligible day)."""
    out = {}
    for cid, (variant, prereg) in CANDIDATES.items():
        try:
            p = json.loads((REPO / 'profiles' / prereg).read_text())
        except (OSError, ValueError):
            continue
        out[cid] = (variant, p['first_eligible_post'][:10])
    try:
        g = json.loads((Path(root) / 'auto_candidates.json').read_text())
        for cid, c in (g.get('candidates') or {}).items():
            if c.get('status') == 'EVALUATING':
                out[cid] = (c['variant'], c['first_eligible_post'][:10])
    except (OSError, ValueError, KeyError):
        pass
    return out


def state_path(root):
    return Path(root) / 'auto_promotion.json'


def load_state(root):
    try:
        st = json.loads(state_path(root).read_text())
    except (OSError, ValueError):
        st = {'profile': PROFILE, 'active': None, 'history': [], 'blocked_until': {}}
    return _apply_owner(st)


def active_variant(root, race_date):
    """-> {'candidate', 'variant', 'effective_from'} applied on race_date, or None (R54_60)."""
    a = load_state(root).get('active')
    if a and str(race_date) >= a['effective_from']:
        return a
    p = (a or {}).get('previous')   # races before an Owner switch keep the variant that was active then
    if p and str(race_date) >= p['effective_from']:
        return p
    return None


def _agg(rows, name):
    v = [r[name] for r in rows]
    inv, pay = sum(x[0] for x in v), sum(x[1] for x in v)
    vs = sorted(v, key=lambda x: -x[1])
    inv_x, pay_x = sum(x[0] for x in vs[1:]), sum(x[1] for x in vs[1:])
    return {'races': len(v), 'invest': inv, 'payout': pay, 'pfs': round(100 * pay / inv, 2) if inv else 0.0,
            'pfs_ex_top1': round(100 * pay_x / inv_x, 2) if inv_x else 0.0,
            'hit_races': sum(1 for x in v if x[2]), 'points_per_race': round(sum(x[3] for x in v) / len(v), 1) if v else 0}


def compare(rows, cand, champ):
    c, h = _agg(rows, cand), _agg(rows, champ)
    venues = {}
    for v in sorted({r['key'].split('_')[0] for r in rows}):
        rs = [r for r in rows if r['key'].split('_')[0] == v]
        if len(rs) >= MIN_VENUE_RACES:
            a, b = _agg(rs, cand), _agg(rs, champ)
            venues[v] = {'races': len(rs), 'candidate_pfs': a['pfs'], 'champion_pfs': b['pfs']}
    better = [v for v, x in venues.items() if x['candidate_pfs'] > x['champion_pfs']]
    much_worse = [v for v, x in venues.items() if x['candidate_pfs'] < x['champion_pfs'] - VENUE_WORSE_LIMIT]
    ok = {'races': len(rows) >= MIN_RACES,
          'same_budget': abs(c['points_per_race'] - h['points_per_race']) <= 0.5,
          'pfs': c['pfs'] > h['pfs'], 'pfs_ex_top1': c['pfs_ex_top1'] > h['pfs_ex_top1'],
          'hits': c['hit_races'] >= h['hit_races'], 'venues_better': len(better) >= MIN_VENUES,
          'no_venue_much_worse': not much_worse}
    return {'candidate': c, 'champion': h, 'venues': venues, 'venues_better': better, 'venues_much_worse': much_worse,
            'checks': ok, 'passes': all(ok.values())}


def _rows(root, since):
    from runtime.local_autopilot import formal_mix
    return formal_mix.races(root, since=since)


def decide(root, today, rows_fn=None):
    """Run after the day's settlement. Returns the decision record (also appended to the state)."""
    rows_fn = rows_fn or _rows
    st = load_state(root)
    nxt = (date.fromisoformat(today) + timedelta(days=1)).isoformat()
    rec = {'decided_at': datetime.now().astimezone().isoformat(), 'day': today}
    a = st.get('active')
    champ_variant = CHAMPION
    if a:   # probation of the promoted variant against the original champion on its own races
        since = datetime.fromisoformat(a['effective_from'] + 'T00:00:00+09:00')
        rows = [r for r in rows_fn(root, since) if a['variant'] in r]
        cmpd = compare(rows, a['variant'], CHAMPION)
        rec.update(action='PROBATION', candidate=a['candidate'], races=len(rows), detail=cmpd)
        ex_worse = cmpd['candidate']['pfs_ex_top1'] < cmpd['champion']['pfs_ex_top1']
        if len(rows) >= MIN_RACES and (ex_worse if a.get('revert_rule') == 'PFS_EX_TOP1'
                                       else cmpd['candidate']['pfs'] < cmpd['champion']['pfs'] and ex_worse):
            st['active'] = None
            st.setdefault('blocked_until', {})[a['candidate']] = nxt
            rec.update(action='DEMOTE', effective_from=nxt)
            a = None
        else:
            champ_variant = a['variant']
    if rec.get('action') != 'DEMOTE':
        # challengers are compared with what is delivered now (the promoted variant, or R54_60), on races after
        # both their first eligible day and the current variant's start (Owner 2026-11-22 21:31)
        best = None
        for cid, (variant, first_day) in candidates(root).items():
            if a and cid == a['candidate']:
                continue
            start = max(first_day, st.get('blocked_until', {}).get(cid, '0000-00-00'), a['effective_from'] if a else '')
            rows = [r for r in rows_fn(root, datetime.fromisoformat(start + 'T00:00:00+09:00'))
                    if variant in r and champ_variant in r]
            cmpd = compare(rows, variant, champ_variant)
            rec.setdefault('evaluated', {})[cid] = {'races': len(rows), 'passes': cmpd['passes'], 'checks': cmpd['checks'],
                                                    'candidate': cmpd['candidate'], 'champion': cmpd['champion'],
                                                    'venues': cmpd['venues'], 'against': champ_variant}
            if cmpd['passes'] and (best is None or cmpd['candidate']['pfs_ex_top1'] > best[2]['candidate']['pfs_ex_top1']):
                best = (cid, variant, cmpd)
        if best:
            if a:
                rec['replaced'] = a['candidate']
            st['active'] = {'candidate': best[0], 'variant': best[1], 'effective_from': nxt, 'promoted_on': today}
            rec.update(action='PROMOTE', candidate=best[0], variant=best[1], effective_from=nxt)
        elif not a:
            rec.update(action='KEEP_CHAMPION')
    st['profile'] = PROFILE
    st['last_decision'] = rec
    if rec['action'] in ('PROMOTE', 'DEMOTE'):
        st['history'] = (st.get('history') or [])[-100:] + [{k: rec[k] for k in rec if k not in ('evaluated', 'detail')}]
    state_path(root).write_text(json.dumps(st, ensure_ascii=False, indent=1) + '\n')
    return rec


def apply_to_cap(capped, ranking, roles, signed_tickets, market_order, promo, krs=None, abl_src=None):
    """Replace the capped recommendation by the promoted variant (BEFORE /final, so it is signed)."""
    from runtime.local_autopilot import formal_mix
    summ = {'ranking': [str(x) for x in ranking], 'roles': {str(k): v for k, v in roles.items()},
            'tickets': capped['tickets'], 'signed_final_tickets': signed_tickets, '_market_order': market_order,
            '_krs': formal_mix.krs_view(krs), '_abl_src': abl_src}
    vt = formal_mix.variant_of(summ, promo['variant'])
    by_key = {(str(t.get('bet_type')), tuple(str(x) for x in t['selection'])): t for t in signed_tickets}
    out = []
    for bt, sel in vt:
        t = by_key.get((bt, tuple(str(x) for x in sel)))
        out.append(dict(t, stake=100) if t else {'bet_type': bt, 'selection': [str(x) for x in sel], 'stake': 100,
                                                 'source': f"AUTO_PROMOTED:{promo['candidate']}"})
    new = dict(capped, tickets=out, kept_count=len(out), kept_investment=100 * len(out),
               auto_promotion={'profile': PROFILE, **promo}, champion_r54_60_tickets=capped['tickets'])
    new.pop('sha256', None)
    return new


def md(rec):
    a = rec.get('action')
    head = {'PROMOTE': f"自動昇格：{rec.get('candidate')}（{rec.get('effective_from')}から配信券面に採用"
                       + (f"、{rec['replaced']} と交代" if rec.get('replaced') else '') + '）',
            'DEMOTE': f"自動降格：{rec.get('candidate')} → 元の60点（{rec.get('effective_from')}から）",
            'PROBATION': f"昇格中の {rec.get('candidate')} を監視中（{rec.get('races')}R）",
            'KEEP_CHAMPION': '昇格条件を満たす候補なし（現行の60点を継続）'}.get(a, a)
    L = [f'## 自動改善の判定（{rec.get("day")}）', '', head, '']
    for cid, e in (rec.get('evaluated') or {}).items():
        c, h = e['candidate'], e['champion']
        L.append(f"- {cid}：{e['races']}R／PFS {c['pfs']}% 対 {'現行' if e.get('against', CHAMPION) == CHAMPION else e['against']} {h['pfs']}%／最大払戻除く {c['pfs_ex_top1']}% 対 "
                 f"{h['pfs_ex_top1']}%／的中 {c['hit_races']} 対 {h['hit_races']}／"
                 + ('条件をすべて満たす' if e['passes'] else '未達：' + '・'.join(k for k, v in e['checks'].items() if not v)))
    return '\n'.join(L) + '\n'

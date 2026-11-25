"""LOCAL same-day track trend from races already settled at the same venue (evidence only).

Only races whose official result was settled BEFORE the current race's freeze time are used, so no later
information leaks into an earlier prediction. Few observations keep a wide uncertainty label; nothing is
converted into a numeric correction (no approved rule exists).
"""
import json
from datetime import datetime
from pathlib import Path

PROFILE = 'KM-LOCAL-DAY-TREND-EVIDENCE-v1.0-20261118'
# B3 n287（2026-11-25 登録）：1〜3番人気で決まったレースは能力で決まっただけかもしれないので偏りの根拠にしない。
# 6番人気以下（単勝オッズ順）で3着以内に来た馬だけの前/後・内/外の占有率を、3着以内全体と並べて記録する（証拠のみ）。
LONGSHOT_POP = 6


def _style(prior):
    """Front-runner proxy from the horse's own last 3 starts (first corner position / field size)."""
    rel = [s['content_positions'][0] / s['field_size'] for s in (prior or [])[:3]
           if s.get('content_positions') and s.get('field_size')]
    return None if not rel else ('FRONT' if sum(rel) / len(rel) <= 0.34 else 'CLOSER' if sum(rel) / len(rel) > 0.6 else 'MID')


def build(day_dir, venue_id, freeze_at):
    day_dir = Path(day_dir)
    rows = []
    try:
        q = json.loads((day_dir / 'queue.json').read_text())
    except (OSError, ValueError):
        return {'profile': PROFILE, 'status': 'NO_QUEUE'}
    for key, r in sorted(q['races'].items()):
        st = r.get('settlement') or {}
        if r.get('venue_id') != venue_id or not st.get('order') or not st.get('settled_at'):
            continue
        if datetime.fromisoformat(st['settled_at']) >= freeze_at:
            continue
        try:
            pred = json.loads((day_dir / 'rev' / f"{st['revision']}.json").read_text())['prediction']
        except (OSError, ValueError, KeyError):
            continue
        rk = {x['no']: x for x in pred.get('ranking') or []}
        w = int(st['order'][0])
        odds = {n: x.get('win') for n, x in rk.items() if x.get('win')}
        pop = {n: i for i, n in enumerate(sorted(odds, key=odds.get), 1)}
        prior = pred.get('prior_runs') or {}
        top3 = []
        for no in st['order'][:3]:
            no = int(no)
            top3.append({'no': no, 'pop': pop.get(no), 'style': _style(prior.get(str(no))),
                         'frame': (rk.get(no) or {}).get('frame')})
        rows.append({'top3': top3, 'race': key, 'winner_style': _style((pred.get('prior_runs') or {}).get(str(w))),
                     'winner_frame': (rk.get(w) or {}).get('frame'),
                     'winner_was_favorite': bool(odds) and w == min(odds, key=odds.get),
                     'winner_paper_rank': list(rk).index(w) + 1 if w in rk else None})
    n = len(rows)
    share = lambda f: round(sum(1 for x in rows if f(x)) / n, 2) if n else None
    allt = [h for x in rows for h in x['top3']]
    lng = [h for h in allt if (h['pop'] or 0) >= LONGSHOT_POP]

    def occ(hs, f):
        known = [h for h in hs if f(h) is not None]
        return round(sum(1 for h in known if f(h)) / len(known), 2) if known else None
    sty = lambda k: (lambda h: None if h['style'] is None else h['style'] == k)
    inner = lambda h: None if h['frame'] is None else h['frame'] <= 4
    longshot = {'pop_threshold': LONGSHOT_POP, 'n_top3': len(allt), 'n_longshot_top3': len(lng),
                'top3_front_share': occ(allt, sty('FRONT')), 'top3_closer_share': occ(allt, sty('CLOSER')),
                'top3_inner_frame_share': occ(allt, inner),
                'longshot_front_share': occ(lng, sty('FRONT')), 'longshot_closer_share': occ(lng, sty('CLOSER')),
                'longshot_inner_frame_share': occ(lng, inner),
                'uncertainty': 'HIGH' if len(lng) < 4 else 'MEDIUM' if len(lng) < 8 else 'LOW',
                'note': '人気薄3着内の通り道（B3 n287、証拠のみ・予測力は未検証）'}
    return {'profile': PROFILE, 'status': 'OK' if n else 'NO_PRIOR_RACE', 'venue_id': venue_id,
            'freeze_at': freeze_at.isoformat(), 'races_used': [x['race'] for x in rows], 'n': n,
            'uncertainty': 'HIGH' if n < 4 else 'MEDIUM' if n < 8 else 'LOW',
            'winner_front_share': share(lambda x: x['winner_style'] == 'FRONT'),
            'winner_closer_share': share(lambda x: x['winner_style'] == 'CLOSER'),
            'winner_inner_frame_share': share(lambda x: (x['winner_frame'] or 9) <= 4),
            'favorite_win_share': share(lambda x: x['winner_was_favorite']),
            'longshot_top3': longshot,
            'production_effect': 'NONE (no approved numeric rule; research evidence)'}

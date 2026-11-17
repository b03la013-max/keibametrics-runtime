"""LOCAL same-day track trend from races already settled at the same venue (evidence only).

Only races whose official result was settled BEFORE the current race's freeze time are used, so no later
information leaks into an earlier prediction. Few observations keep a wide uncertainty label; nothing is
converted into a numeric correction (no approved rule exists).
"""
import json
from datetime import datetime
from pathlib import Path

PROFILE = 'KM-LOCAL-DAY-TREND-EVIDENCE-v1.0-20261118'


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
        rows.append({'race': key, 'winner_style': _style((pred.get('prior_runs') or {}).get(str(w))),
                     'winner_frame': (rk.get(w) or {}).get('frame'),
                     'winner_was_favorite': bool(odds) and w == min(odds, key=odds.get),
                     'winner_paper_rank': list(rk).index(w) + 1 if w in rk else None})
    n = len(rows)
    share = lambda f: round(sum(1 for x in rows if f(x)) / n, 2) if n else None
    return {'profile': PROFILE, 'status': 'OK' if n else 'NO_PRIOR_RACE', 'venue_id': venue_id,
            'freeze_at': freeze_at.isoformat(), 'races_used': [x['race'] for x in rows], 'n': n,
            'uncertainty': 'HIGH' if n < 4 else 'MEDIUM' if n < 8 else 'LOW',
            'winner_front_share': share(lambda x: x['winner_style'] == 'FRONT'),
            'winner_closer_share': share(lambda x: x['winner_style'] == 'CLOSER'),
            'winner_inner_frame_share': share(lambda x: (x['winner_frame'] or 9) <= 4),
            'favorite_win_share': share(lambda x: x['winner_was_favorite']),
            'production_effect': 'NONE (no approved numeric rule; research evidence)'}

"""LOCAL T-10 final-prediction checkpoint (P0-B: 前夜 -> 45分前 -> 10分前).

At post-10 min for a race whose formal Signed FINAL (Revision 1) exists, the Rakuten card is fetched once
more and compared with the card frozen in Revision 1:
  * identity changes: active runner set, jockeys, official going, post time;
  * prediction dependency: the Production Full29 numerical consumer is recomputed locally on the new card
    (no Runtime call, no KRS) and its W/P2/P3 sets (top 3 / 6 / 9) are compared with Revision 1.
Material = any identity change or any W/P2/P3 set change. Odds or body-weight movement alone is material
only through that dependency (it must change the consumer's role sets). Nothing here changes a numeric
policy; a material change triggers the existing formal pipeline again (Revision 2) only when it can
finish before the cutoff, and Revision 1 stays valid and stored whatever happens.
"""
import base64
import gzip
import hashlib
import json
from pathlib import Path

PROFILE = 'KM-LOCAL-CHECKPOINT10-v1.0-20261117'
CHECK_MIN = 10          # start of the final check (minutes before the post)
REV2_BUDGET_S = 150     # Rakuten 61 s crawl delay (Runtime side) + Full29 + KRS 5000 + MEC + FINAL, measured ~70 s


def _rev1_card(fdir, key):
    src = json.loads((Path(fdir) / f'{key}.source_receipt.json').read_text())
    snap = next(s for s in src['artifact']['sources'] if s['source_id'] == 'RAKUTEN_RACE_CARD')
    raw = gzip.decompress(base64.b64decode(snap['raw_gzip_b64']))
    return raw.decode('utf-8', errors='replace'), snap['raw_sha256'], src['artifact'].get('rakuten_card_header') or {}


def _roles_from_ranking(rank):
    rank = [str(x) for x in rank]
    return {'W': set(rank[:3]), 'P2': set(rank[:6]), 'P3': set(rank[:9])}


def _consumer_ranking(r, head, active, html, fetched_at):
    from runtime.local_autopilot import shadow29, formal_rakuten as fr
    sh = shadow29.run_production({'venue_id': r['venue_id'], 'venue_name': r['venue_name'], 'race_no': r['race_no'],
                                  'race_date': r['race_date'], 'distance': head.get('distance'),
                                  'surface': head.get('surface'), 'going': head.get('going'),
                                  'race_name': head.get('race_name'), 'post_current': r['post_current'],
                                  'rid': r['rid']}, active, html, fetched_at)
    sh.pop('_krs_input', None)
    rank, _ = fr.numerical_ranking(sh)
    return [str(x) for x in rank], sh.get('index_terminalization_hash')


def compare(r, fdir, key, new_html, fetched_at, rev1_ranking):
    from runtime.local_autopilot import rakuten as rk
    old_html, old_sha, _ = _rev1_card(fdir, key)
    old_head, new_head = rk.parse_header(old_html), rk.parse_header(new_html)
    a_old, _ = rk.parse_card(old_html)
    a_new, x_new = rk.parse_card(new_html)
    jo = {x['horse_no']: x.get('current_jockey') for x in a_old}
    jn = {x['horse_no']: x.get('current_jockey') for x in a_new}
    bo = {x['horse_no']: x.get('current_body_weight') for x in a_old}
    bn = {x['horse_no']: x.get('current_body_weight') for x in a_new}
    identity = {
        'active_removed': sorted(set(jo) - set(jn)), 'active_added': sorted(set(jn) - set(jo)),
        'jockey_changed': sorted(n for n in set(jo) & set(jn) if jo[n] != jn[n]),
        'going': None if (old_head.get('going') or None) == (new_head.get('going') or None)
        else [old_head.get('going'), new_head.get('going')],
        'post': [old_head.get('post'), new_head.get('post')]
        if old_head.get('post') and new_head.get('post') and old_head['post'] != new_head['post'] else None,
    }
    observed = {'body_weight_new': sorted(n for n in bn if bn[n] and not bo.get(n)),
                'body_weight_changed': sorted(n for n in bn if bn[n] and bo.get(n) and bn[n] != bo[n])}
    new_rank, new_hash = _consumer_ranking(r, new_head, a_new, new_html, fetched_at)
    ro, rn = _roles_from_ranking(rev1_ranking), _roles_from_ranking(new_rank)
    role_diff = {k: {'in': sorted(rn[k] - ro[k], key=int), 'out': sorted(ro[k] - rn[k], key=int)}
                 for k in ro if ro[k] != rn[k]}
    reasons = [k for k, v in identity.items() if v] + (['ROLE_SET_CHANGE'] if role_diff else [])
    up = [x for x in new_rank if x in rev1_ranking and new_rank.index(x) < rev1_ranking.index(x)]
    down = [x for x in new_rank if x in rev1_ranking and new_rank.index(x) > rev1_ranking.index(x)]
    return {'profile': PROFILE, 'checked_at': fetched_at, 'rev1_source_raw_sha256': old_sha,
            'new_source_raw_sha256': hashlib.sha256(new_html.encode()).hexdigest(),
            'identity': identity, 'observed': observed, 'role_diff': role_diff,
            'rank_up': up[:6], 'rank_down': down[:6], 'new_numeric_ranking': new_rank[:9],
            'new_index_terminalization_hash': new_hash, 'material': bool(reasons), 'reasons': reasons,
            'scratched_now': [x.get('horse_no') for x in x_new]}


def ticket_diff(old, new):
    k = lambda t: (t['bet_type'], '-'.join(map(str, t['selection'])))
    a, b = {k(t) for t in old}, {k(t) for t in new}
    return {'added': sorted(b - a)[:30], 'removed': sorted(a - b)[:30], 'added_count': len(b - a),
            'removed_count': len(a - b)}


def effective_dir(day_dir, key):
    """Formal files of the latest effective revision (Revision 2 lives in formal/rev2/, Revision 1 stays)."""
    d = Path(day_dir) / 'formal'
    return d / 'rev2' if (d / 'rev2' / f'{key}.summary.json').exists() and \
        json.loads((d / 'rev2' / f'{key}.summary.json').read_text()).get('status') == 'SIGNED_FINAL' else d

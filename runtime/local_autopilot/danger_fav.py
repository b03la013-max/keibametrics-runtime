"""LOCAL 危険な1番人気 evidence (shadow only; never consumed by ranking, tickets, KRS or capital).

Source rules: Drive 情報源「地方競馬版・危険な1番人気の見抜き方」 (第9章 危険度ランク / 第10章 チェックリスト).
Inputs already fetched for the prediction: the Rakuten card (runners with up to 5 prior starts) and, for
南関東 only, the Keibabook bands (tri / cci / tm / pace). Every flag is a mechanical reading of those
inputs; a flag that cannot be read is reported as None (unknown), never guessed.

Also returns a compact per-runner 前走内容 record (public Rakuten facts only) so results can be joined
later (前走内容をできるだけ収集).
"""
from datetime import date

PROFILE = 'KM-LOCAL-DANGER-FAV-EVIDENCE-v1.0-20261117'
JRA_VENUES = ('札幌', '函館', '福島', '新潟', '東京', '中山', '中京', '京都', '阪神', '小倉')
SMALL_TRACK = ('浦和', '川崎', '園田', '笠松', '水沢')   # 第6章 小回り内枠有利
RANK_A = ('first_course', 'first_distance', 'transfer_first', 'outer_frame_small_track', 'many_front_runners',
          'jockey_change', 'pace_against')
RANK_B = ('closer_style', 'layoff', 'last_lost', 'workout_or_stable_caution')
RANK_C = ('not_dominant_odds',)


def _d(s):
    try:
        y, m, d = (int(x) for x in s.split('.'))
        return date(2000 + y, m, d)
    except (AttributeError, ValueError):
        return None


def _first_pos(s):
    p = s.get('content_positions') or []
    return p[0] if p else None


def prior_record(runner, limit=5):
    out = []
    for s in (runner.get('starts') or [])[:limit]:
        out.append({k: s.get(k) for k in ('date', 'venue', 'race_name', 'distance', 'surface', 'going', 'field_size',
                                          'finish', 'finish_text', 'margin', 'content_positions', 'content_final3f',
                                          'ride_body_weight', 'ride_jockey', 'ride_popularity')})
    return out


def _front(r):
    st = [s for s in (r.get('starts') or [])[:3] if _first_pos(s)]
    return bool(st) and sum(1 for s in st if _first_pos(s) == 1) >= 2


def flags(race, runners, kb=None):
    """race: venue_name, distance, race_date (YYYY-MM-DD); runners: Rakuten parse_card rows (active)."""
    act = [r for r in runners if r.get('win_odds')]
    if len(act) < 3:
        return {'profile': PROFILE, 'status': 'NO_ODDS'}
    act.sort(key=lambda r: r['win_odds'])
    fav, second = act[0], act[1]
    st = fav.get('starts') or []
    venue, dist = race.get('venue_name') or '', race.get('distance')
    today = date.fromisoformat(race['race_date']) if race.get('race_date') else None
    kbf = ((kb or {}).get(fav['horse_no']) or {}) if kb else None
    f = {}
    if not st:
        f.update(first_course=None, first_distance=None, transfer_first=None, jockey_change=None, layoff=None,
                 last_lost=None, closer_style=None, no_same_course_distance=None)
    else:
        f['first_course'] = not any(venue and venue in (s.get('venue') or '') for s in st)
        f['first_distance'] = not any(s.get('distance') == dist for s in st) if dist else None
        f['no_same_course_distance'] = not any(venue in (s.get('venue') or '') and s.get('distance') == dist
                                               for s in st) if dist and venue else None
        f['transfer_first'] = all(any(j in (s.get('venue') or '') for j in JRA_VENUES) for s in st)
        lj, cj = (st[0].get('ride_jockey') or ''), (fav.get('current_jockey') or '')
        f['jockey_change'] = (not (lj[:2] and cj.startswith(lj[:2]))) if lj and cj else None
        ld = _d(st[0].get('date'))
        f['layoff'] = (today - ld).days >= 60 if ld and today else None
        f['last_lost'] = (st[0].get('finish') or 99) > 1 if st[0].get('finish_text') else None
        rel = [_first_pos(s) / s['field_size'] for s in st[:3] if _first_pos(s) and s.get('field_size')]
        f['closer_style'] = (sum(rel) / len(rel) > 0.5) if rel else None
    fronts = sum(1 for r in act if _front(r))
    f['many_front_runners'] = _front(fav) and fronts >= 3
    f['outer_frame_small_track'] = (venue in SMALL_TRACK and (fav.get('frame_no') or 0) >= 7) if venue else None
    f['body_weight_swing'] = abs(fav['current_body_weight_change']) >= 10 \
        if fav.get('current_body_weight_change') is not None else None
    f['not_dominant_odds'] = fav['win_odds'] >= 2.5 and second['win_odds'] / fav['win_odds'] < 1.6
    if kbf and kbf.get('course_first') is not None:   # 能力表 当該場成績 (all venues) beats the 5-run window
        f['first_course'] = kbf['course_first']
    if kbf and kbf.get('style'):
        f['closer_style'] = kbf['style'] in ('差し', '追込')
    if kbf and set(kbf) & {'tri', 'cci', 'tm', 'pace'}:
        f['workout_or_stable_caution'] = 'CAUTION' in (kbf.get('tri'), kbf.get('cci'))
        f['pace_against'] = kbf.get('pace') in ('中位', '後方') and venue in SMALL_TRACK + ('大井', '船橋')
        tms = [((kb.get(r['horse_no']) or {}).get('tm')) for r in act]
        tms = [t for t in tms if t is not None]
        f['press_not_top'] = (kbf.get('tm') is not None and tms and kbf['tm'] < max(tms))
    else:
        f['workout_or_stable_caution'] = f['pace_against'] = f['press_not_top'] = None
    count = lambda keys: sum(1 for k in keys if f.get(k) is True)
    rank = 'A' if count(RANK_A) else 'B' if count(RANK_B) else 'C' if count(RANK_C) else 'NONE'
    return {'profile': PROFILE, 'status': 'OK', 'favorite_no': fav['horse_no'], 'favorite_win_odds': fav['win_odds'],
            'second_no': second['horse_no'], 'second_win_odds': second['win_odds'], 'flags': f,
            'count_a': count(RANK_A), 'count_b': count(RANK_B), 'danger_rank': rank,
            'unknown': sorted(k for k, v in f.items() if v is None),
            'keibabook_coverage': sorted(kbf) if kbf else []}

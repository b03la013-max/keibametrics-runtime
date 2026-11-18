"""LOCAL 南関東 class-move evidence (shadow only; never consumed by ranking, tickets, KRS or capital).

Source: Owner Drive library, YouTube transcript「南関東のクラス分けを完全解説します【川崎競馬】」
(番組ポイント制 2024-01, 1着 x 0.40/0.25/0.15/0.10 for 2nd-5th, 1月・7月 再編成). The author's own
2-year tallies (period and filters not published; UNVERIFIED, never used as numbers here):
  promoted after a win 複勝率 50.9% / promoted without a win 31.4% / promoted after a 2nd 41.3%
  -> the 消し candidate is "promoted after a 3rd or worse";
  demoted after a 掲示板 (<=5th) in the upper class 39.4% / demoted without one 18.6% / after a 3rd 46.4%.
This module only labels each runner mechanically from the card it already has (current race name and
the up-to-5 prior starts) so the claims can be tested on our own settled races (shadow_measure).
A label that cannot be read is UNKNOWN, never guessed.
"""
from runtime.local_autopilot.engine import class_level

PROFILE = 'KM-LOCAL-CLASS-MOVE-EVIDENCE-v1.0-20261118'
NANKAN = ('URW', 'FNB', 'OHI', 'KAW')
JRA_VENUES = ('札幌', '函館', '福島', '新潟', '東京', '中山', '中京', '京都', '阪神', '小倉')
STEP = 0.5   # a class step on engine.class_level is >= 0.8; group (一)(二) differences (0.08) are SAME


def classify(current_race_name, prior_runs):
    """-> (label, detail). prior_runs: newest first, dicts with race_name / finish / venue."""
    cur = class_level(current_race_name or '')
    runs = [s for s in (prior_runs or []) if s]
    if not runs:
        return 'NO_PRIOR', {}
    last = runs[0]
    if any(v in str(last.get('venue') or '') for v in JRA_VENUES):
        return 'JRA_TRANSFER_FIRST', {'prev_venue': last.get('venue')}
    prev = class_level(last.get('race_name') or '')
    if cur is None or prev is None:
        return 'UNKNOWN', {'cur': cur, 'prev': prev}
    fin = last.get('finish')
    d = {'cur': round(cur, 2), 'prev': round(prev, 2), 'prev_finish': fin}
    if prev < cur - STEP:
        if fin is None:
            return 'PROMOTED_UNKNOWN_FINISH', d
        return ('PROMOTED_AFTER_WIN' if fin == 1 else 'PROMOTED_AFTER_2ND' if fin == 2
                else 'PROMOTED_AFTER_3RD_OR_WORSE'), d
    if prev > cur + STEP:
        upper = [s for s in runs if (class_level(s.get('race_name') or '') or -9) > cur + STEP]
        board = [s for s in upper if isinstance(s.get('finish'), int) and s['finish'] <= 5]
        d['upper_starts'] = len(upper)
        if fin == 3:
            return 'DEMOTED_AFTER_3RD', d
        return ('DEMOTED_BOARD_IN_UPPER' if board else 'DEMOTED_NO_BOARD_IN_UPPER'), d
    return 'SAME_CLASS', d


def race_evidence(race, runners):
    """race: venue_id, race_name; runners: Rakuten parse_card rows (active, with starts)."""
    by = {}
    for r in runners:
        label, d = classify(race.get('race_name'), r.get('starts'))
        by[str(r['horse_no'])] = dict(d, label=label)
    return {'profile': PROFILE, 'status': 'OK', 'nankan': race.get('venue_id') in NANKAN,
            'race_class': class_level(race.get('race_name') or ''), 'by_horse': by}

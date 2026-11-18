"""LOCAL going x distance-rotation x early-position evidence (shadow only; never consumed by ranking,
tickets, KRS, MEC or capital).

Source: Owner Drive library「地方競馬向け・複勝軸選定と穴馬激走パターン」(Owner-added 2026-11-18, §12/§13/§20/§17-9,10):
  良（乾いた）ダート -> 距離短縮・同距離組を評価 / 重・不良 -> 距離延長の先行馬を評価、後方からの延長馬は届きにくい.
The document cites the NAR 出馬表解説 (水分が多いほど時計が速い) but publishes no tallies: the claims are UNVERIFIED.
This module only labels each runner mechanically from what the card already has (today's going and distance,
the last prior start's distance and first passing position) so shadow_measure can test the claims on our own
settled races. Anything that cannot be read is UNKNOWN, never guessed.
"""
PROFILE = 'KM-LOCAL-GOING-ROTATION-EVIDENCE-v1.0-20261119'
STEP_M = 100     # |distance change| < 100 m counts as the same distance
FRONT_POS = 3    # first passing position <= 3 in the last start counts as 先行


def going_class(going):
    g = str(going or '')
    if '不良' in g or (g.startswith('重') or g == '重'):
        return 'WET'
    if '稍' in g:
        return 'DAMP'
    if '良' in g:
        return 'DRY'
    return 'UNKNOWN'


def classify(cur_going, cur_distance, prior_runs):
    """-> (label, detail). label = <going>:<rotation>:<position>; claim group in detail['claim']."""
    g = going_class(cur_going)
    runs = [s for s in (prior_runs or []) if s]
    if not runs:
        return f'{g}:NO_PRIOR:NA', {'claim': 'NO_PRIOR'}
    last = runs[0]
    d0 = last.get('distance')
    if not cur_distance or not d0:
        rot = 'UNKNOWN'
    else:
        diff = cur_distance - d0
        rot = 'EXTEND' if diff >= STEP_M else 'SHORTEN' if diff <= -STEP_M else 'SAME'
    pos = (last.get('content_positions') or [None])[0]
    p = 'UNKNOWN' if not isinstance(pos, int) else 'FRONT' if pos <= FRONT_POS else 'BACK'
    claim = 'OTHER'
    if g == 'WET' and rot == 'EXTEND':
        claim = 'CLAIM_WET_EXTEND_FRONT' if p == 'FRONT' else 'COUNTER_WET_EXTEND_BACK' if p == 'BACK' else 'OTHER'
    elif g == 'DRY' and rot in ('SHORTEN', 'SAME'):
        claim = 'CLAIM_DRY_SHORTEN_OR_SAME'
    elif g == 'DRY' and rot == 'EXTEND':
        claim = 'DRY_EXTEND'
    return f'{g}:{rot}:{p}', {'claim': claim, 'cur_distance': cur_distance, 'prev_distance': d0, 'prev_first_pos': pos}


def race_labels(race_going, race_distance, prior_runs_by_no):
    out = {}
    for no, runs in (prior_runs_by_no or {}).items():
        label, d = classify(race_going, race_distance, runs)
        out[str(no)] = dict(d, label=label)
    return {'profile': PROFILE, 'status': 'OK', 'going_class': going_class(race_going), 'by_horse': out}

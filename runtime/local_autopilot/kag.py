"""KAG-LOCAL: Blue / Red / Purple governance made executable (Owner 2026-11-27 22:49 「永続的に実施してください」, ChatGPT
KAG v1.0, restoring "Adversarial Governance BLUE / RED / PURPLE v1.0-CANDIDATE" 2026-09). Daily, after settlement.

BLUE   = the production formal prediction and the existing reflection (review/*.review.json, formal_eval, rev_audit).
RED    = fixed, deterministic counter-checks (independence LEVEL-1) over the five layers, per race:
         RED-1 evidence, RED-2 prediction, RED-3 role/semantic, RED-4 decision/capital, RED-5 meta (per day).
         The checks and thresholds below are frozen here; a change is a new profile version.
BLUE RESPONSE = a fixed mapping from each challenge type to the existing mechanism that already answers it
         (EXISTING / PARTIAL) or ACCEPT when none does.
PURPLE = fixed disposition rules (EXISTING-RULE-ABSORBED / REGRESSION-ONLY / SHADOW / NO-CHANGE). Purple never changes
         production: SHADOW means "research request for the Owner", formulas / KRS / capital need the Owner.
PRE-RACE RED SHADOW (RED-2, uses only pre-race frozen values): horses that >= 3 of the main indices rank #1 while the
         formal ranking puts them outside the top 3 ("independent winner signal"). Its precision is measured after
         the result (win / top-3 rate of flagged horses vs. all horses at the same formal ranks) — never fed back into
         that race. ChatGPT's daily report is an external LEVEL-3 Red; it is noted, not executed here.
"""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

PROFILE = 'KM-LOCAL-KAG-v1.0-20261127'
MAIN = ['HPI-L', 'TPI-L', 'SRI-L', 'F3S-L', 'T3I-L', 'ZAI-WIN', 'CFIg-L', 'WCI']
WINDOW_DAYS = 7
SHADOW_MIN = 8          # a PARTIAL type seen in >= 8 races over 7 days becomes a SHADOW research request
RESPONSE = {            # challenge type -> (Blue response, existing mechanism, Purple when frequent)
    'R1_REV2_NOT_EFFECTIVE': ('EXISTING', 'check10 の1回再試行・rev_audit は Rev1 有効として除外（11/27 修正）', 'REGRESSION-ONLY'),
    'R1_NEUTRAL_HEAVY': ('EXISTING', 'index_health の全馬同値率・KIEP の除去実験', 'EXISTING-RULE-ABSORBED'),
    'R2_INDEX_CONFLICT': ('PARTIAL', 'KIEP（指数→正式順位の実計算）・EXT 週次再学習。EXT 30% 接続そのものの比較は未実施', 'SHADOW'),
    'R2_MARKET_WINNER_LOW': ('EXISTING', 'C24（W＋人気上位2・配信中）・WPLUS・MKTP2', 'EXISTING-RULE-ABSORBED'),
    'R3_KRS_NOT_CONNECTED': ('PARTIAL', '券面は KRSCAP（C29/C30/G007）で比較中。役割（W）への KRS 接続は未比較', 'SHADOW'),
    'R3_P2_MISS_WITH_W': ('EXISTING', 'MKTP2・P2PLUS・role_shadow（勝ち馬別2着）', 'EXISTING-RULE-ABSORBED'),
    'R4_CAP_DROPPED_HIT': ('EXISTING', 'auto_candidates CAP_LOST_HIT → PAIRFULL・CORE・KRSCAP', 'EXISTING-RULE-ABSORBED'),
    'R4_HIT_BUT_LOSS': ('EXISTING', 'KSP 予算系列（B1〜B6）・robustness の的中赤字', 'EXISTING-RULE-ABSORBED'),
}
LAYER = {'R1': 'RED-1 Evidence', 'R2': 'RED-2 Prediction', 'R3': 'RED-3 Role/Semantic', 'R4': 'RED-4 Decision/Capital'}


def _j(p):
    try:
        return json.loads(Path(p).read_text())
    except (OSError, ValueError):
        return None


def pre_race_flags(full29, ranking):
    """RED-2 pre-race shadow: horses ranked #1 by >= 3 MAIN indices but outside the formal top 3."""
    runners = (full29 or {}).get('runners') or []
    top = {}
    for idx in MAIN:
        vals = [(x['indices'].get(idx), int(x['no'])) for x in runners if isinstance(x.get('indices', {}).get(idx), (int, float))]
        if vals:
            m = max(v for v, _ in vals)
            for v, h in vals:
                if v == m:
                    top[h] = top.get(h, 0) + 1
    rank = [int(x) for x in ranking or []]
    return sorted(h for h, n in top.items() if n >= 3 and h in rank and rank.index(h) >= 3)


def race_challenges(rv, fe, ra):
    """rv: review json, fe: formal_eval race row, ra: revision_audit race row -> [(type, evidence)]"""
    ch = []
    L = rv.get('layers') or {}
    ev = lambda k: (lambda v: v if isinstance(v, dict) else {})((L.get(k) or {}).get('evidence'))
    role, idx = ev('ROLE'), ev('INDEX')
    if (ra or {}).get('revision2_not_effective'):
        ch.append(('R1_REV2_NOT_EFFECTIVE', ra['revision2_not_effective']))
    if (idx.get('ruled_neutral_share') or 0) >= 0.3:
        ch.append(('R1_NEUTRAL_HEAVY', {'ruled_neutral_share': idx.get('ruled_neutral_share')}))
    wr = role.get('winner_pre_rank')
    n1 = [k for k, v in (idx.get('winner_rank_by_index') or {}).items() if v == 1]
    if wr and wr > 3 and len(n1) >= 3:
        ch.append(('R2_INDEX_CONFLICT', {'winner_pre_rank': wr, 'indices_ranking_winner_first': n1}))
    wm = (ra or {}).get('w_miss') or {}
    if wr and wr > 5 and (wm.get('winner_market_rank') or 99) <= 3:
        ch.append(('R2_MARKET_WINNER_LOW', {'winner_pre_rank': wr, 'winner_market_rank': wm.get('winner_market_rank')}))
    krs = (fe or {}).get('krs') or {}
    if krs.get('winner_rank_krs_ssr_w') == 1 and role.get('winner_in_W') is False:
        ch.append(('R3_KRS_NOT_CONNECTED', {'static': krs.get('winner_rank_static'), 'krs': 1}))
    if role.get('winner_in_W') and role.get('second_in_P2') is False:
        ch.append(('R3_P2_MISS_WITH_W', {'second_pre_rank': role.get('second_pre_rank')}))
    cap = (fe or {}).get('cap') or {}
    if cap.get('hits_lost'):
        ch.append(('R4_CAP_DROPPED_HIT', {'hits_lost': cap['hits_lost'][:3], 'payout_lost': cap.get('payout_lost')}))
    capl = ev('CAPITAL')
    if capl.get('hit_but_loss'):
        ch.append(('R4_HIT_BUT_LOSS', {'pfs': capl.get('pfs')}))
    return ch


def day(root, day_s):
    dd = Path(root) / day_s
    fe = {r['race']: r for r in (_j(dd / 'review' / 'formal_eval.json') or {}).get('races') or []}
    ra = {r['race']: r for r in (_j(dd / 'review' / 'revision_audit.json') or {}).get('races') or []}
    races, pre = [], []
    for p in sorted((dd / 'review').glob('*.review.json')):
        rv = _j(p) or {}
        key = rv.get('race_key') or p.name.split('.')[0]
        chs = race_challenges(rv, fe.get(key), ra.get(key))
        cp = ((rv.get('layers') or {}).get('CAPITAL') or {}).get('evidence')
        races.append({'race': key, 'blue': {'first_material_failure': rv.get('first_material_failure'),
                                             'pfs': cp.get('pfs') if isinstance(cp, dict) else None},
                      'red': [{'type': t, 'layer': LAYER[t[:2]], 'evidence': e} for t, e in chs]})
        sm = _j(dd / 'formal' / f'{key}.summary.json') or {}
        fu = _j(dd / 'formal' / f'{key}.full29.json')
        order = ((rv.get('official_result') or {}).get('order') or [])
        rank = [int(x) for x in sm.get('ranking') or []]
        if fu and rank and order:
            fl = pre_race_flags(fu, rank)
            pre.append({'race': key, 'flagged': fl, 'winner': int(order[0]), 'top3': [int(x) for x in order[:3]],
                        'peer': {int(h): rank.index(int(h)) + 1 for h in fl}, 'rank': rank})
    return {'profile': PROFILE, 'day': day_s, 'races': races, 'pre_race_red': pre}


def _window(root, today):
    d0 = date.fromisoformat(today)
    out = []
    for i in range(WINDOW_DAYS):
        x = _j(Path(root) / (d0 - timedelta(days=i)).isoformat() / 'review' / 'kag.json')
        if x:
            out.append(x)
    return out


def adjudicate(root, today, cur):
    win = [cur] + [x for x in _window(root, today) if x.get('day') != today]
    cnt = {}
    for d in win:
        for r in d['races']:
            for c in r['red']:
                cnt[c['type']] = cnt.get(c['type'], 0) + 1
    dec = {}
    for t, n in sorted(cnt.items(), key=lambda kv: -kv[1]):
        resp, mech, when_freq = RESPONSE[t]
        disp = (when_freq if (resp != 'PARTIAL' or n >= SHADOW_MIN) else 'EXISTING-RULE-ABSORBED') if resp != 'ACCEPT' else 'SHADOW'
        dec[t] = {'races_7d': n, 'blue_response': resp, 'existing_mechanism': mech, 'purple': disp,
                  'owner_needed': False, 'auto_candidate': disp == 'SHADOW'}   # Owner 2026-11-28 23:32: no approval
    # pre-race RED-2 shadow precision over the window (flagged horse vs. same formal rank horses)
    fw = ft3 = fn = bw = bt3 = bn = 0
    for d in win:
        for r in d.get('pre_race_red') or []:
            for h in r['flagged']:
                fn += 1
                fw += h == r['winner']
                ft3 += h in r['top3']
                pos = r['rank'].index(h) if h in r['rank'] else 3
                for j in range(max(3, pos - 1), min(len(r['rank']), pos + 2)):
                    bn += 1
                    bw += r['rank'][j] == r['winner']
                    bt3 += r['rank'][j] in r['top3']
    prec = {'flagged_horses': fn, 'win_rate': round(fw / fn, 3) if fn else None, 'top3_rate': round(ft3 / fn, 3) if fn else None,
            'same_rank_peers': bn, 'peer_win_rate': round(bw / bn, 3) if bn else None,
            'peer_top3_rate': round(bt3 / bn, 3) if bn else None}
    meta = _meta(root)
    return {'window_days': len(win), 'purple': dec, 'pre_race_red_precision': prec, 'red5_meta': meta}


def _meta(root):
    ac = _j(Path(root) / 'auto_candidates.json') or {}
    C = ac.get('candidates') or {}
    ev = [c for c in C.values() if c.get('status') == 'EVALUATING']
    fam = {}
    for c in ev:
        fam[c.get('family')] = fam.get(c.get('family'), 0) + 1
    ap = _j(Path(root) / 'auto_promotion.json') or {}
    return {'evaluating': len(ev), 'retired': sum(c.get('status') == 'RETIRED' for c in C.values()),
            'same_family_evaluating': {k: v for k, v in fam.items() if v > 1},
            'active': (ap.get('active') or {}).get('candidate'),
            'flags': (['MANY_SAME_FAMILY'] if any(v > 2 for v in fam.values()) else []) +
                     (['SLOTS_FULL'] if len(ev) >= 6 else [])}


def _prec_word(p):
    if p['win_rate'] is None or p['peer_win_rate'] is None:
        return '指摘の精度はまだ測れない'
    w, t = p['win_rate'] > p['peer_win_rate'], p['top3_rate'] > p['peer_top3_rate']
    return ('**勝率・3着内とも同順位帯より上（指摘が当たっている）**' if w and t else
            '勝率は上・3着内は下（まだ判断しない）' if w else '3着内は上・勝率は下（まだ判断しない）' if t else
            '同順位帯より下（指摘は当たっていない）')


def md(cur, adj):
    J = {'EXISTING-RULE-ABSORBED': '既存の仕組みで吸収', 'REGRESSION-ONLY': '再発防止の記録', 'SHADOW': '**自動で研究候補化（承認不要・同予算100Rで自動採否）**',
         'NO-CHANGE': '変更なし'}
    nm = {'R1_REV2_NOT_EFFECTIVE': '直前修正版が署名されず Rev1 のまま', 'R1_NEUTRAL_HEAVY': '勝ち馬の指数の3割以上が中立',
          'R2_INDEX_CONFLICT': '主要指数3つ以上で1位の勝ち馬を正式4位以下', 'R2_MARKET_WINNER_LOW': '人気3位内の勝ち馬を正式6位以下',
          'R3_KRS_NOT_CONNECTED': 'KRS で勝ち馬1位なのに W 外', 'R3_P2_MISS_WITH_W': '勝ち馬は W 内なのに2着が P2 外',
          'R4_CAP_DROPPED_HIT': '全MECにあった的中券を60点で落とした', 'R4_HIT_BUT_LOSS': '的中したのに赤字'}
    tot = sum(len(r['red']) for r in cur['races'])
    L = [f"### 三チーム統治（Blue／Red／Purple）{cur['day']}・{len(cur['races'])}R", '',
         'Red は固定の機械検査（独立性 LEVEL-1）。ChatGPT の日次総括は外部の Red（LEVEL-3）として扱う。Purple は本番を変えない。', '',
         f"- Red の指摘：本日 {tot} 件", '', '| Red の指摘（層） | 本日 | 直近7日 | Blue の応答 | 既存の仕組み | Purple 裁定 |', '|---|---|---|---|---|---|']
    today = {}
    for r in cur['races']:
        for c in r['red']:
            today[c['type']] = today.get(c['type'], 0) + 1
    for t, x in adj['purple'].items():
        L.append(f"| {nm[t]}（{LAYER[t[:2]]}） | {today.get(t, 0)} | {x['races_7d']} | {x['blue_response']} | {x['existing_mechanism']} | {J[x['purple']]} |")
    p = adj['pre_race_red_precision']
    L += ['', f"- 発走前 Red（主要指数3つ以上で1位なのに正式4位以下の馬・{adj['window_days']}日分）：{p['flagged_horses']}頭、勝率 {p['win_rate']}・3着内 {p['top3_rate']}"
              f"（同じ正式順位帯の馬は勝率 {p['peer_win_rate']}・3着内 {p['peer_top3_rate']}）→ "
              f"{_prec_word(p)}"]
    m = adj['red5_meta']
    L.append(f"- RED-5（自己点検）：比較中の自動候補 {m['evaluating']}／6、引退 {m['retired']}、同じ型の重複 {m['same_family_evaluating'] or 'なし'}"
             f"{'、注意：' + '・'.join(m['flags']) if m['flags'] else ''}")
    sh = [nm[t] for t, x in adj['purple'].items() if x['purple'] == 'SHADOW']
    if sh:
        L.append(f"- Purple が自動の研究候補に回したもの（承認不要。auto_candidates が翌日から同予算で比較し、auto_promote が自動で採否）：{'、'.join(sh)}")
    return '\n'.join(L) + '\n'


def write_daily(root, day_s):
    cur = day(root, day_s)
    adj = adjudicate(root, day_s, cur)
    cur['adjudication'] = adj
    out = Path(root) / day_s / 'review'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'kag.json').write_text(json.dumps(cur, ensure_ascii=False, indent=1) + '\n')
    text = md(cur, adj)
    (out / 'kag.md').write_text(text)
    return text

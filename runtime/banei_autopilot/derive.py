"""Derived engine inputs (Owner 2026-11-21 13:23: 集めた情報は全て指数に接続し、指数に必要な情報は渡す).

Every derivation follows the definition in ばんえい攻略条項 (2026-08-03) / v4.0-BAN spec 3-2. Where the 条項
names a condition but no cut-off (e.g. 「先行馬多数」, 「障害巧者騎手」), the cut-off used here is marked
PROVISIONAL in CUTS and reported in the record; it is reviewed at R30 with the Owner, never on a single day.
"""
import re
from datetime import datetime

CUTS = {   # PROVISIONAL cut-offs (no number in the 条項) -> review at R30
    'front_grade': ('A',),                 # キンタロー先行力: 逃げ・先行型
    'fade_grade': ('D', 'E'),              # キンタロー末脚: 障害後に甘くなる
    'pace_H_front_min': 2,                 # 7節 Hペース: 逃げ馬複数 (>=2)
    'pace_H_forward_share': 0.5,           # 7節 Hペース: 先行馬多数 (先行力A/B が半数以上)
    'jockey_min_rides': 100,               # JBR-B 障害巧者騎手: NAR台帳で騎乗100回以上
    'jockey_top_share': 0.25,              # JBR-B 障害巧者騎手: 3着内率の上位25%
    'consecutive_loss_finish': 4,          # BWL-B 状態悪化根拠: 近2走とも4着以下
    'heavy_load': 690,                     # ADF-B / 5-2 重斤量 (ADF-Bの690kgと同じ)
    'body_drop': -15,                      # 5-2 馬体重-15kg以上
}
FRONT_WORDS = ('逃げ', '先行', '好位')
FADE_WORDS = ('伸欠', '甘', '止ま', '失速', '粘り欠')


def _jk(name):
    return re.sub(r'[\s☆▲△◇★]', '', name or '')[:3]


def jockey_stats(hist):
    """{jockey3: {'rides', 'top3', 'rate'}} from the NAR ledger, plus the 障害巧者 set (PROVISIONAL cut)."""
    st = {}
    for runs in hist.values():
        for z in runs:
            j = _jk(z.get('jockey'))
            if not j:
                continue
            s = st.setdefault(j, {'rides': 0, 'top3': 0})
            s['rides'] += 1
            s['top3'] += 1 if z.get('finish') and z['finish'] <= 3 else 0
    elig = sorted((v['top3'] / v['rides'], j) for j, v in st.items() if v['rides'] >= CUTS['jockey_min_rides'])
    k = max(1, int(len(elig) * CUTS['jockey_top_share'])) if elig else 0
    skilled = {j for _, j in elig[-k:]} if k else set()
    return st, skilled


def _md(date_yy):                         # '26.11.14' -> '11/14'
    try:
        d = datetime.strptime('20' + date_yy, '%Y.%m.%d')
        return f'{d.month}/{d.day}'
    except (TypeError, ValueError):
        return None


def horse_inputs(r, kin, kbh, nar, skilled, today_name, band):
    """Per-horse flags for JBR-B / ADF-B / BWL-B / CPU-B / POF-B / PHV-B and the moisture fill."""
    from source import race_class
    past = kin.get('past') or []
    g = kin.get('grades') or {}
    notes = [p.get('note') or '' for p in past[:3]]
    starts = r.get('starts') or []
    fins = [s.get('finish') for s in starts if s.get('finish')]
    front_type = (g.get('front') in CUTS['front_grade']) or sum(any(w in n for w in FRONT_WORDS[:2]) for n in notes) >= 2
    fades = (g.get('kick') in CUTS['fade_grade']) or sum(any(w in n for w in FADE_WORDS) for n in notes) >= 2
    # 同馬で好走 (JBR-B): today's jockey rode this horse to 1-3着 (楽天 card starts or NAR ledger)
    jk = _jk(r.get('jockey'))
    same = jk and any(_jk(s.get('jockey')) == jk and (s.get('finish') or 9) <= 3 for s in starts)
    # 4-2: the rescue needs a 障害巧者騎手; the other conditions only count on top of it (軽度 / 複数該当)
    jbr_hits = []
    if jk and jk in skilled:
        jbr_hits.append('BARRIER_JOCKEY')
        if same:
            jbr_hits.append('SAME_HORSE_GOOD')
        if kin.get('front_ok'):
            jbr_hits.append('CAN_GO_FORWARD')
    # CPU-B: 昇級初戦 / 連勝中
    order = ['C3', 'C2', 'C1', 'B4', 'B3', 'B2', 'B1', 'A2', 'A1', 'OP']
    now_c = race_class(today_name or '')
    # 前走クラス: キンタローの近走欄（例 C2-1）→ 楽天近走のレース名 → NAR台帳 の順（楽天の近走名にはクラスが無いことが多い）
    kc = next((p.get('race_class') for p in past if p.get('race_class')), None)
    last_c = race_class(kc) if kc else (race_class(starts[0]['race_name']) if starts else 'OTHER')
    if last_c == 'OTHER' and nar:
        last_c = race_class(max(nar, key=lambda z: z['date']).get('race_name') or '')
    promoted = now_c in order and last_c in order and order.index(now_c) > order.index(last_c)
    demoted = now_c in order and last_c in order and order.index(now_c) < order.index(last_c)
    win_streak = len(fins) >= 2 and fins[0] == 1 and fins[1] == 1
    # BWL-B 状態悪化根拠 (4-16 手順4): 連続減 / 弱気コメント / 連敗
    bws = [s.get('body_weight') for s in starts[:2]]
    cont_drop = (r.get('body_delta') or 0) < 0 and len(bws) == 2 and None not in bws and bws[0] < bws[1]
    consecutive_loss = len(fins) >= 2 and all(f >= CUTS['consecutive_loss_finish'] for f in fins[:2])
    # 前走復調 (5-1): last finish better than the one before
    recovered = len(fins) >= 2 and fins[0] < fins[1]
    # 馬場水分の補完: card starts get the past-race moisture from キンタロー (same date)
    km = {p.get('date'): p.get('moisture') for p in past if p.get('moisture') is not None}
    for s in starts:
        if s.get('moisture') is None:
            s['moisture'] = km.get(_md(s.get('date')))
    fit = g.get('heavy') if band == 'DRY' else g.get('light') if band == 'WET' else None
    return {'front_type': bool(front_type), 'fades_after_barrier': bool(fades),
            'jbr_hits': jbr_hits, 'jockey_barrier': bool(jbr_hits),
            'promoted': promoted, 'demoted': demoted, 'last_class': last_c, 'win_streak': win_streak,
            'kintaro_picks': kin.get('picks'), 'kintaro_comment': kin.get('comment'),
            'state_bad': cont_drop, 'consecutive_loss': consecutive_loss,
            'comment_weak': kbh.get('cci') == 'CAUTION' if kbh.get('cci') else None,
            'recovered': recovered, 'track_fit_grade': fit,
            'kintaro_grades': g, 'kintaro_notes': notes, 'tm_marks': kbh.get('tm_marks') or ''}


def race_pace(horses):
    """7節: H = 逃げ馬複数 and 先行馬多数; S = no 逃げ・先行型; else M (PROVISIONAL cuts)."""
    H = [h for h in horses if not h.get('scratched')]
    if not H:
        return None
    fr = sum(1 for h in H if h.get('front_type'))
    fwd = sum(1 for h in H if h.get('front_ok'))
    if fr >= CUTS['pace_H_front_min'] and fwd >= CUTS['pace_H_forward_share'] * len(H):
        return 'H'
    return 'S' if fr == 0 else 'M'

"""KeibaMetrics LOCAL v4.3 autopilot engine (deterministic, stdlib only).

Implements the v4.3 chain on the data a public South-Kanto card provides:
base indices (0-100, unknown = 52 RULED-NEUTRAL) -> TPI-L (linear, final
min-penalty) -> SRI-L / T3I-L / F3S-L -> WCI / 本命不安 -> AKI-v2 (W/P/ASI/RSI)
-> race type (地力/環境/混合) -> two-axis quadrant -> formation tickets.

Everything is PAPER / uncalibrated: p(win) is a softmax of TPI-L final blended
with the market, labelled 暫定. No purchase is ever made.
"""
from __future__ import annotations

import itertools
import math
import re
import statistics
import unicodedata
from datetime import date

NEUTRAL = 52.0

# §3.5 / §23-§26 jockey notes (surname prefixes). Higher = stronger at venue.
JOCKEYS = {
    'ALL': {'笹川': 70, '矢野': 70, '御神本': 68, '本田正': 66, '町田': 66, '野畑': 66, '和田譲': 62,
            '吉原': 68, '山崎誠': 64, '森泰': 68, '本橋': 62, '張田': 60, '西啓': 62, '今野': 60,
            '岡部': 60, '藤本現': 58, '山口達': 58, '佐藤友': 60, '石川倭': 58, '桑村': 58},
    'KAW': {'町田': 70, '山崎誠': 68, '野畑': 70, '山林堂': 60},
    'OHI': {'矢野': 72, '笹川': 72, '御神本': 70},
    'FNB': {'本橋': 66, '山口達': 62},
    'URW': {'笹川': 72, '本橋': 66},
}
TRAINERS = {
    'URW': {'小久保': 72, '國保': 66, '平山': 64, '繁田': 64, '小澤': 60, '宇野木': 60},
    'KAW': {'小久保': 68, '内田勝': 62, '佐々木仁': 62},
    'FNB': {'新井清': 66, '林正': 62},
    'OHI': {'荒山': 62, '藤田輝': 62, '渡邉和': 60},
}
SIRES = {
    'KAW': {'ヘニーヒューズ', 'エンパイアメーカー', 'ホッコータルマエ', 'エスポワールシチー', 'コパノリッキー',
            'ダノンレジェンド', 'アジアエクスプレス', 'マジェスティックウォリアー', 'パイロ', 'モーニン',
            'シニスターミニスター', 'フリオーソ'},
    'OHI': {'シニスターミニスター', 'パイロ', 'エスポワールシチー', 'ホッコータルマエ', 'ヘニーヒューズ'},
    'URW': {'ヘニーヒューズ', 'ホッコータルマエ', 'シニスターミニスター', 'パイロ', 'サウスヴィグラス'},
    'FNB': {'ホッコータルマエ', 'パイロ', 'ヘニーヒューズ', 'キングカメハメハ', 'ルーラーシップ'},
}
# EVI weight on early position vs late speed, by venue (§23-§26).
FRONT_WEIGHT = {'URW': 0.85, 'KAW': 0.75, 'FNB': 0.55, 'OHI': 0.55}
CLASS_LEVEL = {'A1': 8, 'A2': 7, 'B1': 6, 'B2': 5, 'B3': 4, 'C1': 3, 'C2': 2, 'C3': 1}
KANJI = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}


def clamp(x, lo=0.0, hi=100.0):
    return max(lo, min(hi, x))


def norm(text):
    return unicodedata.normalize('NFKC', str(text or ''))


def class_level(text):
    t = norm(text)
    m = re.search(r'([ABC])\s*([123])', t)
    if not m:
        return None
    level = CLASS_LEVEL[m[1] + m[2]]
    g = re.search(r'[\(（]([一二三四五六七八九十])[\)）]', t)
    return level - 0.08 * ((KANJI[g[1]] - 1) if g else 0)


def lookup(table, name, default=NEUTRAL):
    name = norm(name).replace(' ', '')
    best = None
    for key, score in table.items():
        if name.startswith(key) and (best is None or len(key) > len(best[0])):
            best = (key, score)
    return best[1] if best else default


def start_date(s):
    try:
        y, m, d = s['date'].split('.')
        return date(2000 + int(y), int(m), int(d))
    except (KeyError, ValueError, AttributeError):
        return None


def rel_finish(s):
    if s.get('finish') and s.get('field_size') and s['field_size'] > 1:
        return 1 - (s['finish'] - 1) / (s['field_size'] - 1)
    return None


def early_norm(s):
    p = s.get('content_positions') or []
    if p and s.get('field_size') and s['field_size'] > 1:
        return (p[0] - 1) / (s['field_size'] - 1)
    return None


def wmean(values, weights):
    pairs = [(v, w) for v, w in zip(values, weights) if v is not None]
    if not pairs:
        return None
    return sum(v * w for v, w in pairs) / sum(w for _, w in pairs)


RECENCY = [0.30, 0.25, 0.20, 0.15, 0.10]


def base_indices(r, race, today):
    venue = race['venue_id']
    starts = [s for s in r['starts'] if s.get('surface') != 'TURF'][:5] or r['starts'][:5]
    flags = []
    # --- HPI-L: finish quality + margin + position (通過順>着順) -------------
    fin = wmean([rel_finish(s) for s in starts], RECENCY)
    mar = wmean([None if s.get('margin') is None else clamp(1 - s['margin'] / 2.0, 0, 1) for s in starts], RECENCY)
    pos = wmean([None if early_norm(s) is None else 1 - early_norm(s) for s in starts], RECENCY)
    parts = [(fin, 0.45), (mar, 0.30), (pos, 0.25)]
    known = [(v, w) for v, w in parts if v is not None]
    hpi = 35 + 60 * sum(v * w for v, w in known) / sum(w for _, w in known) if known else NEUTRAL
    if not known:
        flags.append('HPI:RULED-NEUTRAL(過去走なし)')
    # --- CFIg-L: same venue / distance-decay / frame ---------------------
    dist = race.get('distance')
    dw = [math.exp(-abs((s.get('distance') or dist or 0) - (dist or 0)) / 400) if dist else 1 for s in starts]
    dist_perf = wmean([rel_finish(s) for s in starts], dw)
    same = [rel_finish(s) for s in starts if race['venue_name'] in norm(s.get('venue')) and rel_finish(s) is not None]
    cfi = NEUTRAL
    if dist_perf is not None:
        cfi = 40 + 45 * dist_perf
    if same:
        cfi += 10 * (statistics.mean(same) - 0.5)
    frame = r.get('frame_no')
    if frame and venue in ('URW', 'KAW'):
        cfi += {1: 4, 2: 4, 3: 3, 4: 1, 7: -2, 8: -3}.get(frame, 0)
    if dist and venue == 'URW' and dist in (1500, 1600) and frame and frame >= 7:
        cfi -= 4
    # --- RFIg-L: repeatability of early position + finish stability ------
    eps = [early_norm(s) for s in starts if early_norm(s) is not None]
    fins = [rel_finish(s) for s in starts if rel_finish(s) is not None]
    rfi = NEUTRAL
    if len(eps) >= 2:
        rfi = 80 - 60 * statistics.pstdev(eps) - (25 * statistics.pstdev(fins) if len(fins) >= 2 else 0)
        rfi += 8 * (1 - statistics.mean(eps)) - 4
    # --- EVI (UEV/KEV/FEV/OEV): early position expectation ---------------
    ep3 = wmean([early_norm(s) for s in starts[:3]], [0.5, 0.3, 0.2])
    f3 = [s.get('content_final3f') for s in starts[:3] if s.get('content_final3f')]
    fw = FRONT_WEIGHT.get(venue, 0.7)
    leads = sum(1 for s in starts[:3] if (s.get('content_positions') or [99])[0] == 1)
    if ep3 is None:
        evi = NEUTRAL
        flags.append('EVI:RULED-NEUTRAL(通過順なし)')
    else:
        evi = 40 + 50 * fw * (1 - ep3) + 6 * leads + (50 * (1 - fw) * 0.5)
    # --- NCI: class effective value (§22) --------------------------------
    cur = class_level(race.get('race_name', '') + ' ' + race.get('class_text', ''))
    past = [(class_level(s.get('race_name')), rel_finish(s)) for s in starts]
    past = [(c, f) for c, f in past if c is not None]
    nci = NEUTRAL
    if cur is not None and past:
        diffs = [(c - cur) + (f - 0.5) for c, f in past if f is not None]
        if diffs:
            nci = clamp(55 + 14 * statistics.mean(diffs))
            if past[0][0] < cur - 0.5:
                flags.append('URP:昇級初戦')
            elif past[0][0] > cur + 0.5:
                flags.append('DRS:降級')
    # --- JTI-L / CSI-L / BVIg-L -----------------------------------------
    jti = max(lookup(JOCKEYS.get(venue, {}), r.get('current_jockey'), 0),
              lookup(JOCKEYS['ALL'], r.get('current_jockey'), NEUTRAL))
    prev_j = starts[0].get('ride_jockey') if starts else None
    if prev_j and norm(prev_j)[:2] != norm(r.get('current_jockey'))[:2]:
        jti += 3 if jti >= 64 else -1
    csi = lookup(TRAINERS.get(venue, {}), r.get('trainer'))
    bvi = 62 if norm(r.get('sire')) in SIRES.get(venue, set()) else NEUTRAL
    # --- BWI-L: §34 good-run body-weight range + age/interval ------------
    bwi = NEUTRAL
    bw = r.get('current_body_weight')
    good = [s['ride_body_weight'] for s in starts if s.get('ride_body_weight') and (rel_finish(s) or 0) >= 0.6]
    if bw and good:
        gap = abs(bw - statistics.median(good))
        bwi = 70 - 2.2 * max(0, gap - 4)
    elif bw:
        bwi = 55 - (6 if r.get('current_body_weight_change') is not None and abs(r['current_body_weight_change']) >= 16 else 0)
    last = start_date(starts[0]) if starts else None
    interval = (today - last).days if last else None
    age = r.get('age')
    if age and age >= 7 and interval is not None and interval <= 6:
        bwi -= 10
        flags.append('BWI:高齢×中5日以内')
    if age and age <= 4:
        bwi += 3
    if interval is not None and interval >= 180:
        bwi -= 5
        flags.append('BWI:長期休養明け')
    return {'HPI': clamp(hpi), 'CFI': clamp(cfi), 'RFI': clamp(rfi), 'EVI': clamp(evi), 'NCI': clamp(nci),
            'JTI': clamp(jti), 'CSI': clamp(csi), 'BVI': clamp(bvi), 'BWI': clamp(bwi),
            'CCI': NEUTRAL, 'interval': interval, 'early': ep3, 'leads': leads, 'flags': flags,
            'n_starts': len(starts)}


def softmax(xs, tau):
    m = max(xs)
    e = [math.exp((x - m) / tau) for x in xs]
    s = sum(e)
    return [v / s for v in e]


def predict(race, runners, odds, today):
    active = [r for r in runners if r.get('status') != 'CANCELLED'
              and not (odds.get(r['horse_no'], {}).get('cancelled'))]
    rows = []
    for r in active:
        b = base_indices(r, race, today)
        tpi = (0.18 * b['HPI'] + 0.16 * b['CFI'] + 0.14 * b['RFI'] + 0.08 * b['BVI'] + 0.08 * b['JTI']
               + 0.08 * b['CSI'] + 0.08 * b['BWI'] + 0.10 * b['NCI'] + 0.10 * b['EVI'])
        low = min(b['HPI'], b['CFI'], b['RFI'], b['NCI'], b['EVI'], b['BWI'])
        tpif = tpi - max(0, (60 - low) * 0.5)
        o = odds.get(r['horse_no'], {})
        rows.append({'no': r['horse_no'], 'frame': r.get('frame_no'), 'name': r['name'],
                     'jockey': r.get('current_jockey'), 'trainer': r.get('trainer'), 'load': r.get('current_load'),
                     'bw': r.get('current_body_weight'), 'bw_change': r.get('current_body_weight_change'),
                     'win': o.get('win'), 'place_low': o.get('place_low'), **b,
                     'TPI': clamp(tpi), 'TPIF': clamp(tpif)})
    n = len(rows)
    if n == 0:
        raise ValueError('NO_ACTIVE_RUNNERS')
    # pace: leaders (early <= 0.15 or recent leads)
    leaders = [x for x in rows if (x['early'] is not None and x['early'] <= 0.15) or x['leads'] >= 2]
    for x in rows:
        if x in leaders and len(leaders) >= 3:
            x['EVI'] = clamp(x['EVI'] - 6)
            x['flags'].append('EVI:同型多数')
    # popularity from odds
    with_odds = sorted([x for x in rows if x['win']], key=lambda x: x['win'])
    for i, x in enumerate(with_odds):
        x['pop'] = i + 1
    model_rank = sorted(rows, key=lambda x: -x['TPIF'])
    for i, x in enumerate(model_rank):
        x['model_rank'] = i + 1
    for x in rows:
        pop = x.get('pop')
        x['OPI'] = clamp(NEUTRAL + (6 * (pop - x['model_rank']) if pop else 0))
        x['SRI'] = clamp(0.20 * x['TPIF'] + 0.18 * x['RFI'] + 0.18 * x['EVI'] + 0.15 * x['CFI'] + 0.12 * x['NCI']
                         + 0.10 * x['BWI'] + 0.05 * x['JTI'] + 0.02 * x['CSI'] - 3 * sum('URP' in f or 'BWI:' in f for f in x['flags']))
        t3 = 0.35 * x['TPIF'] + 0.20 * x['EVI'] + 0.15 * x['RFI'] + 0.15 * x['OPI'] + 0.15 * x['CFI']
        if pop and pop >= 6 and x['early'] is not None and x['early'] <= 0.3:
            t3 += 6
        x['T3I'] = clamp(t3)
        x['F3S'] = clamp(0.25 * x['SRI'] + 0.20 * x['TPIF'] + 0.18 * x['EVI'] + 0.14 * x['RFI'] + 0.12 * x['CFI']
                         + 0.06 * x['NCI'] + 0.05 * x['T3I'])
    # probabilities (uncalibrated)
    pm = softmax([x['F3S'] for x in rows], 4.5)
    imp = [1 / x['win'] if x['win'] else None for x in rows]
    tot = sum(v for v in imp if v)
    for x, a, m in zip(rows, pm, imp):
        x['p_model'] = a
        x['p_market'] = m / tot if (m and tot) else None
        x['p_win'] = 0.5 * a + 0.5 * x['p_market'] if x['p_market'] else a
    order = sorted(rows, key=lambda x: -x['F3S'])
    marks = ['◎', '○', '▲', '△', '△']
    for x in rows:
        x['mark'] = ''
    for x, mk in zip(order, marks):
        x['mark'] = mk
    rest = [x for x in order[5:]]
    ana = max(rest, key=lambda x: (x['T3I'] + x['OPI'] / 2)) if rest else None
    if ana:
        ana['mark'] = '☆'
    for x in order:
        x['role'] = '×'
    for x in order[:2]:
        x['role'] = '1着候補'
    for x in order[2:4]:
        x['role'] = '2着候補'
    for x in order[4:6]:
        x['role'] = '3着候補'
    if ana:
        ana['role'] = '3着候補'
    return judge(race, rows, order, ana, leaders)


def judge(race, rows, order, ana, leaders):
    n = len(rows)
    h = order[0]
    gap = h['F3S'] - order[1]['F3S'] if n > 1 else 20
    # 本命不安指数 (§10)
    fuan = 0
    reasons = []
    for f in h['flags']:
        if 'URP' in f:
            fuan -= 8; reasons.append('昇級初戦')
        if '高齢' in f:
            fuan -= 8; reasons.append('高齢×短間隔')
        if '同型' in f:
            fuan -= 7; reasons.append('同型多数')
        if '休養' in f:
            fuan -= 5; reasons.append('休み明け')
    if h['EVI'] < 55:
        fuan -= 6; reasons.append('前に行けない恐れ')
    if h.get('pop') and h['pop'] >= 4:
        fuan -= 4; reasons.append('市場評価が低い')
    if h['n_starts'] == 0:
        fuan -= 6; reasons.append('過去走データなし')
    reversal = sum(1 for x in order[1:] if h['F3S'] - x['F3S'] < 4)
    wci = clamp(50 + 3.2 * gap + 0.25 * (h['EVI'] - 60) + 0.25 * (h['CFI'] - 60) + fuan * 1.2
                + (8 if h.get('pop') == 1 else 0) - 5 * reversal)
    # AKI-v2 (§19)
    w = 30 + (8 if len(leaders) >= 3 and h in leaders else 0) + (10 if any('URP' in f for f in h['flags']) else 0)
    w += 8 if (h.get('pop') or 1) >= 3 else 0
    w += 8 if (h.get('p_market') or 0.4) < 0.30 else 0
    w -= 6 if h.get('pop') == 1 else 0
    w -= 6 if gap >= 6 else 0
    w += 5 * max(0, reversal - 1)
    longshots = [x for x in rows if (x.get('pop') or 0) >= 6 and x['T3I'] >= order[min(3, n - 1)]['T3I'] - 3]
    p = 30 + 10 * min(2, len(longshots)) + (6 if n >= 12 else 0) - (8 if n <= 8 else 0)
    top3m = sorted([x['p_market'] for x in rows if x['p_market']], reverse=True)[:3]
    p -= 8 if sum(top3m) > 0.72 else 0
    p += 6 if len(leaders) >= 3 else 0
    asi = clamp(100 + fuan * 1.6 - (8 if len(leaders) >= 3 and h in leaders else 0) - 6 * max(0, reversal - 1)
                - (10 if h['SRI'] < 62 else 0))
    col2 = order[1:3]
    col3 = order[3:8]
    ls = lambda x: 0.30 * x['SRI'] + 0.25 * x['T3I'] + 0.20 * x['EVI'] + 0.15 * x['CFI'] + 0.10 * x['OPI']
    promote = [x for x in col3 if col2 and ls(x) > min(ls(c) for c in col2)]
    rsi = clamp(25 + 12 * len(promote) + (10 if ana and ana in promote else 0))
    katai = (8 if gap >= 6 else 0) + (8 if sum(top3m) > 0.72 else 0) + (8 if n <= 8 else 0)
    ext = 0
    total = clamp(0.35 * clamp(w) + 0.35 * clamp(p) + 0.20 * rsi + 0.10 * ext - katai)
    if total < 35:
        aki_type, form = 'A', '1-2-4'
    elif total < 50:
        aki_type, form = ('B', '1-3-6') if asi >= 65 else ('C', '2-2-6')
    elif total < 65:
        aki_type, form = ('B', '1-3-7') if asi >= 65 else ('C', '2-3-7')
    else:
        aki_type, form = 'D', '2-4-8'
    if katai >= 16 and total >= 35:
        aki_type, form = 'E', '1-2-5'
    # race type (§30)
    evi_top = max(rows, key=lambda x: x['EVI'])
    if gap >= 6 and h['HPI'] >= max(x['HPI'] for x in rows) - 2:
        rtype = '地力決着型'
    elif evi_top is not h and (len(leaders) >= 3 or len(leaders) == 1):
        rtype = '環境適合型'
    else:
        rtype = '混合型'
    # two-axis quadrant (§12)
    gate = wci >= 90 and fuan > -10 and reversal <= 1 and asi >= 65
    tan_ev = h['p_win'] * h['win'] - 1 if h['win'] else None
    value = tan_ev is not None and tan_ev >= 0.10
    quad = 1 if gate and value else 2 if gate else 3 if value else 4
    tickets = build_tickets(rows, order, ana, quad, form, total, asi, clamp(w), clamp(p), rsi, promote)
    pace = ('ハイペース想定（逃げ候補%d頭）' % len(leaders) if len(leaders) >= 3 else
            '単騎逃げ濃厚（%s）' % leaders[0]['name'] if len(leaders) == 1 else
            '逃げ候補%d頭・平均ペース' % len(leaders))
    return {'rows': rows, 'order': order, 'ana': ana, 'pace': pace, 'race_type': rtype,
            'wci': round(wci), 'fuan': fuan, 'fuan_reasons': reasons, 'reversal': reversal,
            'gate': '絶対的' if gate else '不安あり', 'tan_ev': tan_ev, 'quad': quad,
            'aki': {'W': round(clamp(w)), 'P': round(clamp(p)), 'ASI': round(asi), 'RSI': round(rsi),
                    'katai': katai, 'total': round(total), 'type': aki_type, 'form': form},
            'checks': {'軸抜けライン': clamp(w) >= 50 or asi < 65, '穴同士ライン': clamp(p) >= 60,
                       '3列目昇格': rsi >= 60 and bool(promote), '堅決着補正': katai > 0},
            'promote': [x['no'] for x in promote], 'tickets': tickets}


CAP = lambda total: 5 if total < 50 else 7 if total < 65 else 8


def trio(cols, cap, must=()):
    a, b, c = cols
    seen, out = set(), []
    for x in a:
        for y in b:
            for z in c:
                k = frozenset((x, y, z))
                if len(k) == 3 and k not in seen:
                    seen.add(k)
                    out.append(tuple(sorted(k)))
    must = [tuple(sorted(m)) for m in must if len(set(m)) == 3]
    keep = [m for m in must if m not in out] + out
    return keep[:cap]


def build_tickets(rows, order, ana, quad, form, total, asi, w, p, rsi, promote):
    n = [x['no'] for x in order]
    h, o = n[0], n[1] if len(n) > 1 else None
    rest = n[2:]
    t = []
    if len(n) < 3:
        return [{'k': '単勝', 'b': str(h), 'pt': 1, 'st': '最小', 'note': '頭数不足'}]
    hx = order[0]
    ana_no = ana['no'] if ana else None
    second = [o] + rest[:1]
    if rsi >= 60 and promote:
        second = list(dict.fromkeys(second + [promote[0]['no'] if isinstance(promote[0], dict) else promote[0]]))
    third_size = {'1-2-4': 4, '1-3-6': 6, '1-3-7': 7, '2-2-6': 6, '2-3-7': 7, '2-4-8': 8, '1-2-5': 5}.get(form, 5)
    pool = [x for x in n[1:] if x != ana_no][:third_size - (1 if ana_no else 0)] + ([ana_no] if ana_no else [])
    cap = CAP(total)
    if quad == 1:
        t.append({'k': '単勝', 'b': f'{h}', 'pt': 1, 'st': '厚', 'note': '二段ゲート通過'})
        t.append({'k': '馬単', 'b': f'{h}→{",".join(map(str, n[1:3]))}', 'pt': 2, 'st': '中'})
    elif quad == 2:
        t.append({'k': '馬単', 'b': f'{h}→{",".join(map(str, n[1:4]))}', 'pt': 3, 'st': '中',
                  'note': '絶対的だが単勝配当不足→1着固定で配当化'})
        tri = [(h, y, z) for y in n[1:3] for z in n[1:5] + ([ana_no] if ana_no else []) if y != z]
        t.append({'k': '三連単', 'b': f'{h}→{",".join(map(str, n[1:3]))}→{",".join(map(str, dict.fromkeys(n[1:5] + ([ana_no] if ana_no else []))))}',
                  'pt': len(set(tri)), 'st': '小'})
    else:
        pl = hx.get('place_low')
        if quad == 3 and pl and pl >= 1.3:
            t.append({'k': '複勝', 'b': f'{h}', 'pt': 1, 'st': '中', 'note': f'複勝下限{pl:.1f}倍≥1.3'})
        else:
            wide = [o] + ([ana_no] if ana_no and ana_no != o else [])
            t.append({'k': 'ワイド', 'b': ' / '.join(f'{h}-{x}' for x in wide), 'pt': len(wide),
                      'st': '中' if quad == 3 else '小', 'note': '複勝下限割れ/不明→ワイドへルーティング' if quad == 3 else '本命は軸、相手に妙味'})
    # 三連複 formation (§20), always (全レース購入)
    if form.startswith('1-'):
        cols = ([h], second, pool)
    else:
        cols = ([h, o], [h, o] + rest[:1], pool)
    must = []
    if (w >= 50 or asi < 65) and len(n) >= 4:
        must.append((o, n[2], n[3]))           # ◎抜けライン
    if p >= 60 and ana_no:
        must.append((h, ana_no, next(x for x in n[1:] if x != ana_no)))  # 軸+穴+α
    combos = trio(cols, cap, must)
    t.append({'k': '三連複', 'b': ' / '.join('-'.join(map(str, c)) for c in combos), 'pt': len(combos),
              'st': '最小' if quad == 4 else '小', 'note': f'{form}型（上限{cap}点）'})
    return t

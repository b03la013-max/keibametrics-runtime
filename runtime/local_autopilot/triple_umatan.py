"""SPAT4 LOTO トリプル馬単 (三重勝馬番号二連勝単式) recommendation for the Southern Kanto meetings.

Regulation (sources in the module docstring of the delivery / Owner report):
  - target races: the last three races of the day at the venue (12R day: R10-R12)
  - sales close 5 minutes before the scheduled post of the FIRST target race; SPAT4 internet only
  - 1 combination >= 50 yen, 10-yen steps; payout rate 70 %; cap 60,000,000 yen per 10 yen; carry-over exists
  - a combination containing a horse scratched / excluded after sales is refunded in full
The pick is built from the existing PAPER win probabilities of each leg's latest pre-start revision (plain
Harville for the 2nd place), as a per-leg FORMATION (1着 A → 2着 B) so it can be entered with SPAT4 セレクト.
Probabilities are uncalibrated: the hit estimate is a model figure, never an EV / Kelly input. No purchase.
"""
import hashlib
import json
from datetime import datetime, timedelta
from itertools import product
from pathlib import Path

PROFILE = 'KM-LOCAL-TRIPLE-UMATAN-PAPER-v1.0-20261118'
VENUES = ('URW', 'FNB', 'OHI', 'KAW')          # 南関東4場 (門別も発売するが Owner 指示の範囲外)
CLOSE_BEFORE_MIN = 5
BUILD_WINDOW_MIN = (7, 20)                      # build when the first leg is 7-20 minutes from post
UNIT_YEN = 50                                   # 1組 50円 (minimum)
TIERS = (('S', 8), ('M', 36), ('L', 120))      # point caps; SPAT4 accepts at most 120 combinations per vote
A_MAX, B_MAX = 3, 6


def legs(q, venue_id):
    rs = sorted(((r['race_no'], k) for k, r in q['races'].items() if r['venue_id'] == venue_id), reverse=True)
    return [k for _, k in sorted(rs[:3])] if len(rs) >= 3 else []


def deadline(q, leg_keys):
    return datetime.fromisoformat(q['races'][leg_keys[0]]['post_current']) - timedelta(minutes=CLOSE_BEFORE_MIN)


def leg_probs(pred, scratched):
    rows = [x for x in pred['ranking'] if x['no'] not in scratched]
    src = 'PAPER_p_win'
    vals = {x['no']: float(x['p_win']) for x in rows if x.get('p_win')}
    if len(vals) < len(rows) or not vals:
        vals, src = {x['no']: 1 / x['win'] for x in rows if x.get('win')}, 'MARKET_1/odds'
    t = sum(vals.values())
    return {k: v / t for k, v in vals.items()}, src


def exacta(p, i, j):
    return p[i] * p[j] / (1 - p[i]) if p[i] < 1 else 0.0


def leg_options(p):
    order = sorted(p, key=p.get, reverse=True)
    out = []
    for a in range(1, A_MAX + 1):
        for b in range(2, B_MAX + 1):
            A, B = order[:a], order[:b]
            pairs = [(i, j) for i in A for j in B if i != j]
            if pairs:
                out.append({'first': A, 'second': B, 'points': len(pairs),
                            'cover': round(sum(exacta(p, i, j) for i, j in pairs), 4)})
    return out


def build(q, venue_id, root_day, now):
    ks = legs(q, venue_id)
    if not ks:
        return None
    rec = {'profile': PROFILE, 'venue_id': venue_id, 'venue_name': q['races'][ks[0]]['venue_name'],
           'legs': [], 'deadline': deadline(q, ks).isoformat(), 'built_at': now.isoformat(),
           'production_effect': 'PAPER recommendation only; no purchase; probabilities uncalibrated'}
    opts = []
    for k in ks:
        r = q['races'][k]
        pre = [e for e in r['editions'] if e.get('rev')]
        if not pre:
            rec['status'] = f'NO_PREDICTION:{k}'
            return rec
        e = pre[-1]
        pred = json.loads((Path(root_day) / 'rev' / f"{e['rev']}.json").read_text())
        scratched = set(pred.get('scratched_nos') or [])
        p, src = leg_probs(pred['prediction'], scratched)
        rec['legs'].append({'race': k, 'race_no': r['race_no'], 'post': r['post_current'], 'edition': e['edition'],
                            'revision': e['rev'], 'prob_source': src,
                            'top': [[n, round(p[n], 3)] for n in sorted(p, key=p.get, reverse=True)[:6]]})
        opts.append(leg_options(p))
    rec['tiers'] = {}
    for name, cap in TIERS:
        best = None
        for combo in product(*opts):
            pts = combo[0]['points'] * combo[1]['points'] * combo[2]['points']
            if pts > cap:
                continue
            hit = combo[0]['cover'] * combo[1]['cover'] * combo[2]['cover']
            if best is None or hit > best[0] or (hit == best[0] and pts < best[1]):
                best = (hit, pts, combo)
        hit, pts, combo = best
        rec['tiers'][name] = {'cap': cap, 'points': pts, 'stake_yen': pts * UNIT_YEN,
                              'model_hit_prob': round(hit, 5),
                              'legs': [{'first': c['first'], 'second': c['second'], 'points': c['points'],
                                        'leg_cover': c['cover']} for c in combo]}
    # Owner library「トリプル馬単攻略法」§22: skip when no leg can be narrowed to 1-3 points
    m = rec['tiers']['M']['legs']
    rec['skip_advice'] = None if min(l['points'] for l in m) <= 3 else 'NO_NARROW_LEG'
    rec['status'] = 'BUILT' if now < deadline(q, ks) else 'BUILT_AFTER_DEADLINE'
    rec['sha256'] = hashlib.sha256(json.dumps(rec['tiers'], sort_keys=True).encode()).hexdigest()
    return rec


def md(rec):
    L = [f"### 【地方版PAPER トリプル馬単】{rec['venue_name']} "
         + '・'.join(f"{x['race_no']}R" for x in rec['legs'])
         + f"（SPAT4締切 {rec['deadline'][11:16]}＝{rec['legs'][0]['race_no']}R発走5分前）", '']
    for x in rec['legs']:
        L.append(f"- {x['race_no']}R {x['post'][11:16]}（{x['edition']}）上位確率 "
                 + ' '.join(f"{n}:{int(v * 100)}%" for n, v in x['top'][:4]))
    L += ['', '| 案 | 1レース目 | 2レース目 | 3レース目 | 組数 | 50円/組 | モデル的中確率 |', '|---|---|---|---|---|---|---|']
    for name, t in rec['tiers'].items():
        cell = lambda l: (f"1着{','.join(map(str, l['first']))}→2着"
                          f"{','.join(str(x) for x in l['second'] if len(l['first']) > 1 or x not in l['first'])}（{l['points']}組）")
        L.append(f"| {name} | {cell(t['legs'][0])} | {cell(t['legs'][1])} | {cell(t['legs'][2])} | {t['points']} | "
                 f"{t['stake_yen']:,}円 | {t['model_hit_prob'] * 100:.2f}% |")
    if rec.get('skip_advice'):
        L += ['', '**見送り検討**：どのレースも1〜3点に絞れません（M案で最少の脚でも4点以上）。']
    L += ['', '<sub>入力：SPAT4 LOTO「セレクト」で各レース 1着→2着 のフォーメーション（同じ馬は1着・2着同時不可）。'
          '払戻率70%・1組50円（10円×5口）以上10円単位・1回最大120組・発売後の取消/除外馬を含む組は全額返還。確率はPAPERの未較正値（期待値・資金配分には使わない）。'
          f"2・3レース目は締切時点で最新の版（朝版の場合あり）。実購入なし。SHA `{rec['sha256'][:12]}`</sub>"]
    return '\n'.join(L)


def settle(rec, q):
    """Hit / refund after all legs settled. The トリプル馬単 dividend is not on the race result page:
    payout stays None (hit rate vs model probability is what is measured)."""
    res = []
    for x in rec['legs']:
        st = q['races'][x['race']].get('settlement')
        if not st or not st.get('order'):
            return None
        res.append([int(v) for v in st['order'][:2]])
    out = {}
    for name, t in rec['tiers'].items():
        hit = all(o[0] in l['first'] and o[1] in l['second'] and o[0] != o[1] for o, l in zip(res, t['legs']))
        out[name] = {'hit': hit, 'stake_yen': t['stake_yen'], 'model_hit_prob': t['model_hit_prob'], 'payout': None}
    return {'orders': res, 'tiers': out}

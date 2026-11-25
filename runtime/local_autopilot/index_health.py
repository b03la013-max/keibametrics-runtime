"""Weekly health check of the 29 formal indices (Owner 2026-11-25 21:54 「進めて」 for the 21:53 proposal).

Diagnosis only: the production weights, the ranking, KRS, MEC and the tickets are untouched. A change suggested by
this report goes through the same automatic Forward OOS (100R, same budget) as every other candidate.

Data: every settled formal race in the data root, <day>/formal/<KEY>.full29.json (the frozen index values that the
formal prediction used) + <day>/<KEY>.result.json (official order) + <day>/formal/<KEY>.summary.json (ranking) +
<day>/<KEY>.shadow29.json (cells that were RULED-NEUTRAL, per index).

Per index:
  - AUC-W / AUC-T3: within-race pairwise probability that the winner (a top-3 horse) has the higher value than a
    horse that did not (ties = 1/2); pooled over races; SE from the per-race spread. 0.5 = no information.
  - tercile rates: within-race top / middle / bottom third by the index -> win and top-3 rates (monotone?).
  - by venue AUC-T3 (venues with >= MIN_VENUE races).
  - no-information share: races where the index has one value for every runner (no separation at all).
  - drop-one: AUC-T3 of an equal-weight z-sum of the ability indices vs. the same sum without this index
    (a proxy of the production combination, said so in the report).
Flags (ability indices): REVERSED (AUC-T3 < 0.5 by > 2 SE), WEAK (|AUC-T3 - 0.5| <= 2 SE), DRAG (dropping it
raises the proxy AUC). Risk indices: REVERSED when AUC-T3 > 0.5 by > 2 SE. Diagnostics: no direction flag.
"""
from __future__ import annotations

import json
import statistics as st
from datetime import date
from pathlib import Path

PROFILE = 'KM-LOCAL-INDEX-HEALTH-v1.0-20261125'
MIN_VENUE = 20
# direction (from local_fullnumerical_candidate): RISK = higher is riskier (expected AUC < 0.5);
# DIAG = a diagnostic whose direction is not an ability (market gap, data confidence, ...): shown, never "reversed"
RISK = {'RSI', 'W-AKI', 'P2-AKI', 'P3-AKI'}
DIAG = {'DCR', 'OPI-V', 'PRI', 'DRS', 'URP'}
VENUE_JA = {'OHI': '大井', 'KAW': '川崎', 'FNB': '船橋', 'URW': '浦和', 'MON': '門別', 'MIZ': '水沢', 'MRO': '盛岡',
            'KNZ': '金沢', 'KSM': '笠松', 'NGY': '名古屋', 'SON': '園田', 'HMJ': '姫路', 'KOC': '高知', 'SAG': '佐賀'}


def _load(p):
    try:
        return json.loads(Path(p).read_text())
    except (OSError, ValueError):
        return None


def races(root):
    """[(day, key, {no: {index: value}}, order, ranking, neutral_by_index, n_runners)]"""
    out = []
    for dd in sorted(Path(root).glob('20??-??-??')):
        for f in sorted((dd / 'formal').glob('*.full29.json')):
            key = f.name.split('.')[0]
            res = _load(dd / f'{key}.result.json')
            fu = _load(f)
            if not res or not fu or not res.get('order'):
                continue
            vals = {int(r['no']): {k: v for k, v in (r.get('indices') or {}).items() if isinstance(v, (int, float))}
                    for r in fu.get('runners') or []}
            order = [int(x) for x in res['order'] if int(x) in vals]
            if len(order) < 5:
                continue
            sm = _load(dd / 'formal' / f'{key}.summary.json') or {}
            sh = _load(dd / f'{key}.shadow29.json') or {}
            out.append((dd.name, key, vals, order, [int(x) for x in sm.get('ranking') or []],
                        sh.get('non_calculated_by_index') or {}, len(vals)))
    return out


def _auc(score, order, top):
    pos = set(order[:top])
    P = [score[h] for h in order if h in pos and h in score]
    N = [score[h] for h in order if h not in pos and h in score]
    if not P or not N:
        return None
    s = sum(1.0 if p > n else 0.5 if p == n else 0.0 for p in P for n in N)
    return s / (len(P) * len(N))


def _pool(xs):
    xs = [x for x in xs if x is not None]
    if len(xs) < 2:
        return None, None, len(xs)
    return st.mean(xs), st.stdev(xs) / len(xs) ** 0.5, len(xs)


def _terciles(score, order):
    hs = sorted(score, key=lambda h: -score[h])
    n = len(hs)
    groups = [hs[:n // 3], hs[n // 3: n - n // 3], hs[n - n // 3:]]
    win, top3 = order[0], set(order[:3])
    return [(sum(h == win for h in g), sum(h in top3 for h in g), len(g)) for g in groups]


def _z(vals, idx):
    xs = [v[idx] for v in vals.values() if idx in v]
    if len(xs) < 2:
        return {h: 0.0 for h in vals}
    m, s = st.mean(xs), st.pstdev(xs) or 1.0
    return {h: (v[idx] - m) / s if idx in v else 0.0 for h, v in vals.items()}


def evaluate(root):
    R = races(root)
    idxs = sorted({k for r in R for v in r[2].values() for k in v})
    rep = {'profile': PROFILE, 'races': len(R), 'days': sorted({r[0] for r in R}), 'indices': {}}
    if not R:
        return rep
    zc = [{i: _z(r[2], i) for i in idxs} for r in R]
    abil = [i for i in idxs if i not in RISK | DIAG]
    full = [{h: sum(z[i][h] for i in abil) for h in r[2]} for r, z in zip(R, zc)]
    proxy_t3 = _pool([_auc(f, r[3], 3) for r, f in zip(R, full)])
    rank_t3 = _pool([_auc({h: -i for i, h in enumerate(r[4])}, r[3], 3) for r in R if r[4]])
    rep['reference'] = {'formal_ranking_auc_t3': _r(rank_t3[0]), 'equal_weight_proxy_auc_t3': _r(proxy_t3[0])}
    for i in idxs:
        sc = [{h: v[i] for h, v in r[2].items() if i in v} for r in R]
        aw, sew, n = _pool([_auc(s, r[3], 1) for s, r in zip(sc, R)])
        a3, se3, _ = _pool([_auc(s, r[3], 3) for s, r in zip(sc, R)])
        terc = [[0, 0, 0] for _ in range(3)]
        for s, r in zip(sc, R):
            if len(s) >= 6:
                for g, (w, t, c) in enumerate(_terciles(s, r[3])):
                    terc[g][0] += w
                    terc[g][1] += t
                    terc[g][2] += c
        ven = {}
        for s, r in zip(sc, R):
            ven.setdefault(r[1].split('_')[0], []).append(_auc(s, r[3], 3))
        by_venue = {VENUE_JA.get(v, v): round(_pool(x)[0], 3) for v, x in ven.items()
                    if _pool(x)[0] is not None and len(x) >= MIN_VENUE}
        neutral = sum(len(set(s.values())) <= 1 for s in sc) / len(R)
        kind = 'RISK' if i in RISK else 'DIAG' if i in DIAG else 'ABILITY'
        drop = (_pool([_auc({h: f[h] - z[i][h] for h in f}, r[3], 3) for r, f, z in zip(R, full, zc)])[0]
                if kind == 'ABILITY' else None)
        flag = []
        if a3 is not None and se3 is not None and kind != 'DIAG':
            bad = a3 < 0.5 - 2 * se3 if kind == 'ABILITY' else a3 > 0.5 + 2 * se3
            if bad:
                flag.append('REVERSED')
            elif abs(a3 - 0.5) <= 2 * se3:
                flag.append('WEAK')
        if drop is not None and proxy_t3[0] is not None and drop > proxy_t3[0] + 0.002:
            flag.append('DRAG')
        rep['indices'][i] = {
            'kind': kind, 'races': n, 'auc_win': _r(aw), 'auc_win_se': _r(sew), 'auc_top3': _r(a3), 'auc_top3_se': _r(se3),
            'terciles': [{'win_rate': _r(w / c if c else None), 'top3_rate': _r(t / c if c else None)} for w, t, c in terc],
            'by_venue_auc_top3': by_venue, 'neutral_share': _r(neutral), 'drop_one_proxy_auc_top3': _r(drop),
            'flags': flag}
    return rep


def _r(x, d=3):
    return None if x is None else round(x, d)


def md(rep):
    L = [f"### 29指数の健康診断（{rep['days'][0] if rep.get('days') else ''}〜{rep['days'][-1] if rep.get('days') else ''}・"
         f"確定{rep['races']}R）", '',
         '診断のみ。本番の重み・順位・KRS・買い目は変更していません。0.5＝情報なし、高いほど好走馬を上に置けている。', '']
    ref = rep.get('reference') or {}
    if ref:
        L.append(f"- 正式順位の3着内AUC {ref.get('formal_ranking_auc_t3') or 0:.3f}／能力指数を等しく足した参考値 "
                 f"{ref.get('equal_weight_proxy_auc_t3') or 0:.3f}")
    ix = rep.get('indices') or {}
    order = sorted(ix, key=lambda k: -(ix[k]['auc_top3'] or 0))
    rev = [k for k in order if 'REVERSED' in ix[k]['flags']]
    drag = [k for k in order if 'DRAG' in ix[k]['flags']]
    weak = [k for k in order if 'WEAK' in ix[k]['flags']]
    if rev:
        L.append('- **逆に働いている指数**（能力指数なのに高いほど3着内に来ない／危険度指数なのに高いほど来る）：' + '、'.join(f"{k}（{ix[k]['auc_top3']:.3f}）" for k in rev))
    if drag:
        L.append('- **外すと参考順位が良くなる指数**：' + '、'.join(drag))
    if weak:
        L.append(f"- 効きが確認できない指数：{len(weak)}個（{'、'.join(weak)}）")
    L += ['', '| 指数 | 種別 | 勝ちAUC | 3着内AUC | 上位1/3→下位1/3の3着内率 | 全馬同値 | 判定 |', '|---|---|---|---|---|---|---|']
    KJ = {'ABILITY': '能力', 'RISK': '危険度', 'DIAG': '診断'}
    for k in order:
        x = ix[k]
        t = x['terciles']
        tt = '→'.join(f"{(g['top3_rate'] or 0) * 100:.0f}%" for g in t)
        L.append(f"| {k} | {KJ[x['kind']]} | {x['auc_win'] or 0:.3f} | {x['auc_top3'] or 0:.3f}±{x['auc_top3_se'] or 0:.3f} | {tt} | "
                 f"{(x['neutral_share'] or 0) * 100:.0f}% | {'・'.join(x['flags']) or ('有効' if x['kind'] == 'ABILITY' else '想定どおり' if x['kind'] == 'RISK' else '—')} |")
    vv = {k: ix[k]['by_venue_auc_top3'] for k in rev + drag if ix[k]['by_venue_auc_top3']}
    if vv:
        L += ['', '競馬場別（3着内AUC、20R以上の場）：']
        for k, d in vv.items():
            L.append(f"- {k}：" + '、'.join(f"{v} {a:.3f}" for v, a in d.items()))
    L += ['', '「外すと良くなる」は能力指数を等しく足した近似での判定で、本番の組み合わせ方そのものではありません。'
          '「全馬同値」はそのレースで全頭が同じ値（情報なし）だった割合。危険度指数は3着内AUCが0.5未満なら想定どおり。']
    return '\n'.join(L) + '\n'


def weekly(root, today):
    """Once per ISO week (first settled day of the week): write <root>/index_health/<day>.json/.md; returns the md
    text when a new report was made, else None."""
    d = Path(root) / 'index_health'
    d.mkdir(exist_ok=True)
    wk = date.fromisoformat(today).isocalendar()[:2]
    for f in d.glob('20??-??-??.json'):
        if date.fromisoformat(f.stem).isocalendar()[:2] == wk:
            return None
    rep = evaluate(root)
    rep['day'] = today
    (d / f'{today}.json').write_text(json.dumps(rep, ensure_ascii=False, indent=1) + '\n')
    text = md(rep)
    (d / f'{today}.md').write_text(text)
    return text

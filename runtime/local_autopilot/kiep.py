"""KIEP-LOCAL: index evolution research with the ACTUAL formal consumer (Owner 2026-11-26 21:43 「永続的に実施してください」,
ChatGPT KIEP v1.0 for LOCAL).

index_health.py ranks the 29 indices with an equal-weight proxy. This module re-runs the real formal ranking path on
the frozen values of every settled formal race:
    Full29 values -> formal_rakuten.numerical_ranking (local_krs_bridge_candidate, the Production numerical consumer)
                  -> ext_connect.apply (0.7 x overall + 0.3 x EXT, with the EXT that was frozen for that race)
and checks first that it reproduces the stored formal ranking (REPRODUCED share). Then, one index at a time, the index
is set to its race mean for every runner (no information, same level) and the ranking is recomputed: the change in
winner rank / top-3 AUC on the earlier and the later race days (time split by day) is the Actual Consumer Ablation.

The production formula, the registry, the weights and the tickets are not changed. When neutralising an index improves
the top-3 AUC on BOTH halves by >= MIN_GAIN, auto_candidates registers GEN:IDXABL:drop=<n> (n = position in
INDEX_IDS): the same signed MEC capped to the same 60 points, ordered with the ablated ranking. The auto_promote rules
(100R, PFS, PFS without the largest payout, hits, venues) decide; a formula change itself stays an Owner decision.
"""
from __future__ import annotations

import json
import statistics as st
from datetime import date
from pathlib import Path

PROFILE = 'KM-LOCAL-KIEP-ACTUAL-CONSUMER-ABLATION-v1.0-20261126'
INDEX_IDS = ['HPI-L', 'CFIg-L', 'RFIg-L', 'BVIg-L', 'JTI-L', 'CSI-L', 'BWI-L', 'DCR', 'NCI', 'TPI-L', 'EVI/CEV', 'CCI',
             'TRI', 'PRI', 'OPI-V', 'DRS', 'URP', 'HCS', 'ZAI-WIN', 'ZAI-PLACE', 'SRI-L', 'T3I-L', 'F3S-L', 'WCI',
             'W-AKI', 'P2-AKI', 'P3-AKI', 'ASI', 'RSI']   # = full29 required_indices order (frozen 2026-11-26)
MIN_GAIN = 0.004
SCALE = 1.5   # weight-up test: the index's deviation from the race mean x 1.5
TRAIN_SHARE = 0.6


def _load(p):
    try:
        return json.loads(Path(p).read_text())
    except (OSError, ValueError):
        return None


# LOCAL canon coefficients of the derived indices (local_fullnumerical_candidate.materialize_candidate, read
# 2026-11-26). Base indices reach the formal consumer only through these, so a base-index ablation is propagated
# through them: derived' = derived + sum coef x (input' - input). Linear parts exactly; the TPI min-major penalty is
# recomputed; observed-only re-normalisation of missing inputs is not reproduced (stated in the report).
TPI_W = {'HPI-L': .18, 'CFIg-L': .16, 'RFIg-L': .14, 'BVIg-L': .08, 'JTI-L': .08, 'CSI-L': .08, 'BWI-L': .08, 'NCI': .10, 'EVI/CEV': .10}
TPI_MAJOR = ['HPI-L', 'CFIg-L', 'RFIg-L', 'NCI', 'EVI/CEV', 'BWI-L']
SRI_W = {'TPI-L': .20, 'RFIg-L': .18, 'EVI/CEV': .18, 'CFIg-L': .15, 'NCI': .12, 'BWI-L': .10, 'JTI-L': .05, 'CSI-L': .02}
F3S_W = {'SRI-L': .25, 'TPI-L': .20, 'EVI/CEV': .18, 'RFIg-L': .14, 'CFIg-L': .12, 'NCI': .06, 'T3I-L': .05}
ZW = ['TPI-L', 'SRI-L', 'EVI/CEV', 'CFIg-L', 'NCI', 'DCR']
ZP = ['TPI-L', 'SRI-L', 'EVI/CEV', 'CFIg-L', 'RFIg-L', 'DCR']
BASE = ['HPI-L', 'CFIg-L', 'RFIg-L', 'BVIg-L', 'JTI-L', 'CSI-L', 'BWI-L', 'NCI', 'EVI/CEV']


def propagate(old, new):
    """old/new: one runner's index dicts where only base indices differ -> new with the derived indices updated."""
    v = dict(new)
    d = lambda k: v[k] - old[k]
    pen = lambda x: max(0.0, (60.0 - min(x[k] for k in TPI_MAJOR)) * 0.5)
    v['TPI-L'] = old['TPI-L'] + sum(w * d(k) for k, w in TPI_W.items()) + pen(old) - pen(v)
    v['SRI-L'] = old['SRI-L'] + sum(w * d(k) for k, w in SRI_W.items())
    v['F3S-L'] = old['F3S-L'] + sum(w * d(k) for k, w in F3S_W.items())
    v['ZAI-WIN'] = old['ZAI-WIN'] + sum(d(k) for k in ZW) / len(ZW)
    v['ZAI-PLACE'] = old['ZAI-PLACE'] + sum(d(k) for k in ZP) / len(ZP)
    v['WCI'] = old['WCI'] + (d('ZAI-WIN') + d('SRI-L')) / 4
    return v


def ranking(full29, ext_runners, neutral=None, factor=0.0):
    """The formal ranking path on frozen values; `neutral` = an index id set to its race mean (a base index is
    propagated through the derived indices that use it)."""
    from runtime.local_autopilot import ext_connect
    from runtime.local_autopilot.formal_rakuten import numerical_ranking
    f = full29
    if neutral:
        vals = [x['indices'][neutral] for x in full29['runners'] if isinstance(x['indices'].get(neutral), (int, float))]
        m = st.mean(vals) if vals else None
        rows = []
        for x in full29['runners']:
            ov = x['indices'].get(neutral)
            nv = (m + factor * (ov - m)) if (m is not None and isinstance(ov, (int, float))) else m
            iv = dict(x['indices'], **({neutral: nv} if nv is not None else {}))
            if neutral in BASE and m is not None:
                try:
                    iv = propagate(x['indices'], iv)
                except (KeyError, TypeError, ValueError):
                    pass
            rows.append(dict(x, indices=iv))
        f = {'runners': rows}
    _, num = numerical_ranking(f)
    ext = {int(k): v for k, v in (ext_runners or {}).items()}
    r, _ = ext_connect.apply(num['runner_scores'], ext)
    return [int(x) for x in r]


def races(root):
    out = []
    for sp in sorted(Path(root).glob('20??-??-??/formal/*.summary.json')):
        key = sp.name.split('.')[0]
        dd = sp.parent.parent
        eff = sp.parent / 'rev2'
        d = eff if (eff / f'{key}.result.json').exists() and (eff / f'{key}.full29.json').exists() else sp.parent
        res = _load(d / f'{key}.result.json') or _load(dd / f'{key}.result.json')
        fu, ec, sm = _load(d / f'{key}.full29.json'), _load(d / f'{key}.ext_connection.json'), _load(d / f'{key}.summary.json')
        if not res or not fu or not sm or not res.get('order') or sm.get('no_bet'):
            continue
        gone = set(res.get('non_starters') or [])
        order = [int(x) for x in res['order'] if int(x) not in gone]
        if len(order) < 5:
            continue
        out.append({'day': dd.name, 'key': key, 'full29': fu, 'ext': (ec or {}).get('runners') or {},
                    'stored': [int(x) for x in (ec or {}).get('ranking') or sm.get('ranking') or []], 'order': order})
    return out


def _auc_t3(rank, order):
    top = set(order[:3])
    pos = {h: i for i, h in enumerate(rank)}
    P = [pos[h] for h in rank if h in top]
    N = [pos[h] for h in rank if h not in top and h in set(order)]
    if not P or not N:
        return None
    return sum(1.0 if p < n else 0.5 if p == n else 0.0 for p in P for n in N) / (len(P) * len(N))


def _metrics(pairs):
    aucs = [_auc_t3(r, o) for r, o in pairs]
    aucs = [a for a in aucs if a is not None]
    wr = [r.index(o[0]) + 1 for r, o in pairs if o[0] in r]
    return {'races': len(pairs), 'auc_top3': round(st.mean(aucs), 4) if aucs else None,
            'winner_rank_mean': round(st.mean(wr), 3) if wr else None,
            'winner_top1': sum(x == 1 for x in wr), 'winner_top3': sum(x <= 3 for x in wr)}


def evaluate(root):
    R = races(root)
    rep = {'profile': PROFILE, 'races': len(R), 'days': sorted({r['day'] for r in R}), 'index_ids': INDEX_IDS}
    if not R:
        return rep
    base = []
    rep_ok = 0
    for r in R:
        try:
            b = ranking(r['full29'], r['ext'])
        except Exception:
            b = None
        r['base'] = b
        rep_ok += int(b is not None and b == r['stored'])
        base.append(b)
    R = [r for r in R if r['base']]
    rep['reproduced'] = {'races': len(R), 'identical_to_stored_formal_ranking': rep_ok}
    days = sorted({r['day'] for r in R})
    cut = days[max(1, int(len(days) * TRAIN_SHARE)) - 1] if len(days) > 1 else days[-1]
    halves = {'train': [r for r in R if r['day'] <= cut], 'test': [r for r in R if r['day'] > cut]}
    rep['split'] = {'train': f"{days[0]}〜{cut}", 'test': f"{min((r['day'] for r in halves['test']), default='-')}〜{days[-1]}"}
    rep['baseline'] = {h: _metrics([(r['base'], r['order']) for r in rows]) for h, rows in halves.items()}
    abl = {}
    for n, idx in enumerate(INDEX_IDS):
        row = {'n': n}
        for h, rows in halves.items():
            pairs = []
            for r in rows:
                try:
                    pairs.append((ranking(r['full29'], r['ext'], idx), r['order']))
                except Exception:
                    continue
            m = _metrics(pairs)
            b = rep['baseline'][h]
            m['auc_gain'] = round((m['auc_top3'] or 0) - (b['auc_top3'] or 0), 4) if m['auc_top3'] is not None else None
            row[h] = m
        g1, g2 = row['train'].get('auc_gain'), row['test'].get('auc_gain')
        row['verdict'] = ('DROP_HELPS' if g1 is not None and g2 is not None and g1 >= MIN_GAIN and g2 >= MIN_GAIN else
                          'NEEDED' if g1 is not None and g2 is not None and g1 <= -MIN_GAIN and g2 <= -MIN_GAIN else
                          'NO_EFFECT' if g1 is not None and g2 is not None and abs(g1) < MIN_GAIN and abs(g2) < MIN_GAIN else 'MIXED')
        abl[idx] = row
    rep['ablation'] = abl
    scl = {}
    for n, idx in enumerate(INDEX_IDS):   # KIEP-04 weight: the index's spread x SCALE (its weight up), same path
        if abl[idx]['verdict'] not in ('NEEDED', 'MIXED') and not any(abs(abl[idx][h].get('auc_gain') or 0) >= MIN_GAIN / 2 for h in halves):
            continue
        row = {'n': n}
        for h, rows in halves.items():
            pairs = []
            for r in rows:
                try:
                    pairs.append((ranking(r['full29'], r['ext'], idx, SCALE), r['order']))
                except Exception:
                    continue
            m = _metrics(pairs)
            m['auc_gain'] = round((m['auc_top3'] or 0) - (rep['baseline'][h]['auc_top3'] or 0), 4) if m['auc_top3'] is not None else None
            row[h] = m
        g1, g2 = row['train'].get('auc_gain'), row['test'].get('auc_gain')
        row['verdict'] = 'UP_HELPS' if g1 is not None and g2 is not None and g1 >= MIN_GAIN and g2 >= MIN_GAIN else 'NO'
        scl[idx] = row
    rep['scale'] = {'factor': SCALE, 'rows': scl}
    return rep


def md(rep):
    if not rep.get('races'):
        return '### KIEP 指数の実計算での除去実験\n\n対象レースなし\n'
    rp, b = rep['reproduced'], rep['baseline']
    L = [f"### KIEP：指数を1つずつ無効にして正式の計算で順位を出し直す（確定{rep['races']}R）", '',
         '研究のみ。正式の算式・重み・順位・買い目は変更していません。無効化＝そのレースの全馬をその指数の平均値にする。',
         '基礎指数（HPI・CFI・RFI・BVI・JTI・CSI・BWI・NCI・EVI）は、それを使う総合系の指数（TPI・SRI・F3S・ZAI・WCI）へ'
         '正典の係数で波及させて計算（欠損時の重みの付け直しは再現しない近似）。', '',
         f"- 正式の計算を再現できたレース：{rp['identical_to_stored_formal_ranking']}／{rp['races']}（順位が保存値と完全一致）",
         f"- 学習 {rep['split']['train']}（3着内AUC {b['train']['auc_top3']}）／試験 {rep['split']['test']}（{b['test']['auc_top3']}）", '',
         '| 指数 | 学習 AUC の変化 | 試験 AUC の変化 | 判定 |', '|---|---|---|---|']
    J = {'DROP_HELPS': '**外すと良くなる**', 'NEEDED': '効いている', 'NO_EFFECT': 'ほぼ影響なし', 'MIXED': '期間で逆'}
    ab = rep['ablation']
    for idx in sorted(ab, key=lambda k: -((ab[k]['test'].get('auc_gain') or 0) + (ab[k]['train'].get('auc_gain') or 0))):
        x = ab[idx]
        L.append(f"| {idx} | {x['train'].get('auc_gain'):+.4f} | {x['test'].get('auc_gain'):+.4f} | {J[x['verdict']]} |")
    sc = (rep.get('scale') or {}).get('rows') or {}
    if sc:
        L += ['', f"重みを上げる試験（その指数の平均からの差を ×{rep['scale']['factor']}）：", '',
              '| 指数 | 学習 AUC の変化 | 試験 AUC の変化 | 判定 |', '|---|---|---|---|']
        for idx, x in sorted(sc.items(), key=lambda kv: -((kv[1]['test'].get('auc_gain') or 0))):
            L.append(f"| {idx} | {x['train'].get('auc_gain'):+.4f} | {x['test'].get('auc_gain'):+.4f} | "
                     f"{'**上げると良くなる**' if x['verdict'] == 'UP_HELPS' else '—'} |")
    helps = [k for k, x in ab.items() if x['verdict'] == 'DROP_HELPS']
    helps += [f"{k}↑" for k, x in sc.items() if x['verdict'] == 'UP_HELPS']
    L += ['', f"- 学習・試験の両方で {MIN_GAIN} 以上良くなった指数は自動で比較候補（外す＝GEN:IDXABL、上げる＝GEN:IDXSCL）になります：{'、'.join(helps) or 'なし'}"]
    return '\n'.join(L) + '\n'


def weekly(root, today):
    d = Path(root) / 'kiep'
    d.mkdir(exist_ok=True)
    wk = date.fromisoformat(today).isocalendar()[:2]
    for f in d.glob('20??-??-??.json'):
        if date.fromisoformat(f.stem).isocalendar()[:2] == wk:
            return None
    rep = evaluate(root)
    rep['day'] = today
    (d / f'{today}.json').write_text(json.dumps({k: v for k, v in rep.items()}, ensure_ascii=False, indent=1) + '\n')
    text = md(rep)
    (d / f'{today}.md').write_text(text)
    return text

"""KRS calibration baseline for LOCAL (Owner 2026-11-26 19:53 「進めて」 for Claude's 19:4x proposal on ChatGPT KCP v1.0).

Measurement only (Phase 2 "現行誤差測定"): KRS-Engine, parameter_map, the formal ranking, MEC and tickets are untouched;
SSR stays an uncalibrated simulation frequency (no EV / Kelly). Any change found here goes in as a new candidate through
the automatic Forward OOS like every other one.

Per settled formal race (<day>/formal/<KEY>.krs_prediction_utility.json + <day>/<KEY>.result.json + the PAPER record
<day>/<KEY>.json for the market odds and the PAPER win rate, + <day>/formal/<KEY>.summary.json for the formal ranking):
  CAL-05 probability: winner log loss / Brier (one-of-N) and top-3 Brier for
         KRS  = SSR-W normalised over the field (SSR-T3 / 3 for top 3),
         PAPER = the PAPER model's p_win (uncalibrated),
         MKT  = 1/odds normalised (the market, with the take removed by normalising);
         reliability (10 bins) and ECE; a one-parameter temperature T fitted on the earlier 60 % of race days and
         tested on the later 40 % (grid; time split by day, all horses and revisions of a race stay together).
  CAL-03 stage: predicted 1角 / 4角 median vs the official passing order when the result page gave it
         (result.json 'corners', recorded from 2026-11-26): MAE in positions, share of actual positions inside the
         p25-p75 band (nominal 50 %), predicted leader actually 1st at 1角, front 3 at 1角 still front 3 at 4角
         (predicted vs actual rate). Races without passing order are counted, not guessed.
  CAL-06 increment: winner's rank under SSR-W vs under the formal ranking (better / same / worse), top-3 AUC.
"""
from __future__ import annotations

import json
import math
from datetime import date
from pathlib import Path

PROFILE = 'KM-LOCAL-KRS-CALIB-BASELINE-v1.0-20261126'
EPS = 1e-6
TRAIN_SHARE = 0.6
T_GRID = [round(0.4 + 0.05 * i, 2) for i in range(53)]   # 0.40 .. 3.00


def _load(p):
    try:
        return json.loads(Path(p).read_text())
    except (OSError, ValueError):
        return None


def _norm(d):
    s = sum(v for v in d.values() if v and v > 0)
    return {h: (v / s if s and v and v > 0 else 0.0) for h, v in d.items()}


def _corners(res):
    from runtime.local_autopilot import hist_stats
    cs = [v for name, v in (res.get('corners') or []) if 'コーナー' in str(name)]
    if not cs:
        return None, None
    return hist_stats.corner_positions(cs[0]), hist_stats.corner_positions(cs[-1])


def _hist_corners(root):
    """Official passing order for races settled before result.json kept it: NAR monthly CSVs (the Owner's ZIPs) and
    the Rakuten result backfill, via hist_stats.load_sources. {VEN_YYYYMMDD_Rnn: (first, last)}; {} if none."""
    import os
    try:
        from runtime.local_autopilot import hist_stats
        races, _ = hist_stats.load_sources(Path(root), os.environ.get('KM_LOCAL_NAR_ROOT'))
    except Exception:
        return {}
    return {rid: (r.get('first_corner') or None, r.get('last_corner') or None) for rid, r in races.items()
            if r.get('first_corner') and r.get('last_corner')}


def races(root, research=None):
    """research=None: the formal KRS; research='HOLD15' etc.: the after-result research re-run of the same race
    (krs_research.py), only for races that have one."""
    out = []
    hist = None
    for dd in sorted(Path(root).glob('20??-??-??')):
        pat = f'*.krs_research_{research}.json' if research else '*.krs_prediction_utility.json'
        for f in sorted((dd / 'formal').glob(pat)):
            key = f.name.split('.')[0]
            res = _load(dd / f'{key}.result.json')
            ku = _load(f)
            if not res or not ku or not res.get('order') or len(res['order']) < 5:
                continue
            gone = set(res.get('non_starters') or [])
            summ = {int(s['horse_no']): s for s in ku.get('summary') or [] if int(s['horse_no']) not in gone}
            if len(summ) < 5:
                continue
            pap = _load(dd / f'{key}.json') or {}
            rk = {int(r['no']): r for r in (pap.get('prediction') or {}).get('ranking') or []}
            fs = _load(dd / 'formal' / f'{key}.summary.json') or {}
            fc, lc = _corners(res)
            if not fc:
                if hist is None:
                    hist = _hist_corners(root)
                v, rn = key.split('_')[0], int(key.split('_')[1])
                fc, lc = hist.get(f"{v}_{dd.name.replace('-', '')}_R{rn:02d}", (None, None))
            out.append({'day': dd.name, 'key': key, 'venue': key.split('_')[0], 'order': [int(x) for x in res['order']],
                        'krs_w': _norm({h: s.get('SSR-W') or 0 for h, s in summ.items()}),
                        'krs_t3': {h: min(1.0, (s.get('SSR-T3') or 0)) for h, s in summ.items()},
                        'pos': {h: s.get('positions') or {} for h, s in summ.items()},
                        'paper_w': _norm({h: (rk.get(h) or {}).get('p_win') or 0 for h in summ}),
                        'mkt_w': _norm({h: 1 / (rk.get(h) or {}).get('win') if (rk.get(h) or {}).get('win') else 0 for h in summ}),
                        'formal_rank': [int(x) for x in fs.get('ranking') or [] if int(x) in summ],
                        'first_corner': fc, 'last_corner': lc})
    return out


def _temper(p, t):
    w = {h: math.exp(math.log(max(v, EPS)) / t) for h, v in p.items()}
    return _norm(w)


def _win_scores(rows, src, t=1.0):
    ll, br, n, zero = 0.0, 0.0, 0, 0
    bins = [[0, 0.0, 0] for _ in range(10)]
    for r in rows:
        p = r[src]
        if not any(p.values()):
            continue
        if t != 1.0:
            p = _temper(p, t)
        w = r['order'][0]
        zero += p.get(w, 0) <= 0
        ll += -math.log(max(p.get(w, 0), EPS))
        br += sum((v - (h == w)) ** 2 for h, v in p.items())
        n += 1
        for h, v in p.items():
            b = min(9, int(v * 10))
            bins[b][0] += 1
            bins[b][1] += v
            bins[b][2] += int(h == w)
    if not n:
        return None
    tot = sum(b[0] for b in bins)
    ece = sum(abs(b[1] / b[0] - b[2] / b[0]) * b[0] / tot for b in bins if b[0])
    return {'races': n, 'winner_at_zero': zero, 'log_loss': round(ll / n, 4), 'brier': round(br / n, 4), 'ece': round(ece, 4),
            'reliability': [{'bin': f'{i / 10:.1f}-{(i + 1) / 10:.1f}', 'n': b[0],
                             'mean_pred': round(b[1] / b[0], 3) if b[0] else None,
                             'actual': round(b[2] / b[0], 3) if b[0] else None} for i, b in enumerate(bins)]}


def _t3_brier(rows):
    s, n = 0.0, 0
    for r in rows:
        top = set(r['order'][:3])
        s += sum((v - (h in top)) ** 2 for h, v in r['krs_t3'].items()) / len(r['krs_t3'])
        n += 1
    return round(s / n, 4) if n else None


def _fit_t(rows, src):
    best = None
    for t in T_GRID:
        sc = _win_scores(rows, src, t)
        if sc and (best is None or sc['log_loss'] < best[1]):
            best = (t, sc['log_loss'])
    return best[0] if best else 1.0


def _stage(rows):
    have = [r for r in rows if r['first_corner'] and r['last_corner']]
    st = {'races_with_passing_order': len(have), 'races_without': len(rows) - len(have)}
    for cn, key in (('1角', 'first_corner'), ('4角', 'last_corner')):
        err, inside, n = 0.0, 0, 0
        for r in have:
            for h, p in r['pos'].items():
                q = p.get(cn) or (p.get('3角') if cn == '4角' and not p.get('4角') else None)
                a = r[key].get(h)
                if not q or a is None or q.get('median') is None:
                    continue
                err += abs(q['median'] - a)
                inside += int((q.get('p25') or q['median']) <= a <= (q.get('p75') or q['median']))
                n += 1
        st[cn] = {'horses': n, 'mae_positions': round(err / n, 2) if n else None,
                  'inside_p25_p75': round(inside / n, 3) if n else None, 'nominal': 0.5}
    lead_ok = lead_n = keep_pred = keep_act = keep_n = 0
    for r in have:
        med = {h: (p.get('1角') or {}).get('median') for h, p in r['pos'].items() if (p.get('1角') or {}).get('median') is not None}
        if not med:
            continue
        lead = min(med, key=lambda h: med[h])
        lead_n += 1
        lead_ok += int(r['first_corner'].get(lead) == 1)
        front_act = {h for h, v in r['first_corner'].items() if v <= 3}
        for h in front_act:
            keep_n += 1
            keep_act += int((r['last_corner'].get(h) or 99) <= 3)
            q4 = (r['pos'].get(h) or {}).get('4角') or {}
            keep_pred += int((q4.get('median') or 99) <= 3)
    st['predicted_leader_led_1角'] = round(lead_ok / lead_n, 3) if lead_n else None
    st['front3_stays_front3'] = {'horses': keep_n, 'predicted': round(keep_pred / keep_n, 3) if keep_n else None,
                                 'actual': round(keep_act / keep_n, 3) if keep_n else None}
    return st


def _auc_t3(score, order):
    top = set(order[:3])
    P = [score[h] for h in score if h in top]
    N = [score[h] for h in score if h not in top]
    if not P or not N:
        return None
    return sum(1.0 if p > n else 0.5 if p == n else 0.0 for p in P for n in N) / (len(P) * len(N))


def _increment(rows):
    better = same = worse = 0
    ak, af = [], []
    for r in rows:
        if not r['formal_rank']:
            continue
        w = r['order'][0]
        kr = sorted(r['krs_w'], key=lambda h: -r['krs_w'][h])
        a, b = (kr.index(w) if w in kr else 99), (r['formal_rank'].index(w) if w in r['formal_rank'] else 99)
        better += a < b
        same += a == b
        worse += a > b
        ak.append(_auc_t3(r['krs_t3'], r['order']))
        n = len(r['formal_rank'])
        af.append(_auc_t3({h: n - i for i, h in enumerate(r['formal_rank'])}, r['order']))
    m = lambda xs: round(sum(x for x in xs if x is not None) / max(1, sum(x is not None for x in xs)), 3)
    return {'winner_rank_krs_better': better, 'same': same, 'worse': worse,
            'auc_top3_krs': m(ak), 'auc_top3_formal_ranking': m(af)}


def evaluate(root):
    R = races(root)
    rep = {'profile': PROFILE, 'races': len(R), 'days': sorted({r['day'] for r in R}),
           'notice': 'SSR は未較正のシミュレーション頻度。補正値は研究のみで EV・Kelly・購入方針に使わない'}
    if not R:
        return rep
    days = rep['days']
    cut = days[max(1, int(len(days) * TRAIN_SHARE)) - 1] if len(days) > 1 else days[-1]
    tr = [r for r in R if r['day'] <= cut]
    te = [r for r in R if r['day'] > cut] or tr
    prob = {s: _win_scores(R, s) for s in ('krs_w', 'paper_w', 'mkt_w')}
    temp = {}
    for s in ('krs_w', 'paper_w'):
        t = _fit_t(tr, s)
        temp[s] = {'T_fitted_on_train': t, 'train_days': f'{tr[0]["day"]}〜{cut}', 'test_days': f'{te[0]["day"]}〜{te[-1]["day"]}',
                   'test_log_loss_identity': (_win_scores(te, s) or {}).get('log_loss'),
                   'test_log_loss_tempered': (_win_scores(te, s, t) or {}).get('log_loss'),
                   'test_log_loss_market': (_win_scores(te, 'mkt_w') or {}).get('log_loss')}
    ven = {}
    for r in R:
        ven.setdefault(r['venue'], []).append(r)
    try:
        rep['variants'] = compare_variants(root)
    except Exception as exc:
        rep['variants_error'] = f'{type(exc).__name__}:{str(exc)[:120]}'
    rep.update(probability=prob, krs_top3_brier=_t3_brier(R), temperature=temp, stage=_stage(R),
               increment=_increment(R),
               by_venue={v: {'races': len(x), 'krs_log_loss': (_win_scores(x, 'krs_w') or {}).get('log_loss'),
                             'mkt_log_loss': (_win_scores(x, 'mkt_w') or {}).get('log_loss'),
                             **{k: v2 for k, v2 in _increment(x).items() if k in ('winner_rank_krs_better', 'same', 'worse')}}
                         for v, x in sorted(ven.items()) if len(x) >= 20})
    return rep


def compare_variants(root):
    """Formal KRS vs each research variant on exactly the same races (CAL-01/02 shadow comparison)."""
    from runtime.local_autopilot import krs_research
    out = {}
    for name in list(krs_research.VARIANTS) + ['BASE']:
        V = races(root, name)
        if not V:
            continue
        keys = {(r['day'], r['key']) for r in V}
        B = [r for r in races(root) if (r['day'], r['key']) in keys]
        row = {}
        for lab, R in (('formal', B), (name, V)):
            st = _stage(R)
            ws = _win_scores(R, 'krs_w') or {}
            row[lab] = {'races': len(R), 'log_loss': ws.get('log_loss'), 'ece': ws.get('ece'),
                        'front3_stays_front3': st['front3_stays_front3'], '1角_mae': st['1角']['mae_positions'],
                        '4角_mae': st['4角']['mae_positions'], 'auc_top3': _increment(R)['auc_top3_krs']}
        out[name] = row
    return out


def md(rep):
    from runtime.local_autopilot.index_health import VENUE_JA
    if not rep.get('races'):
        return '### KRS の較正測定\n\n対象レースなし\n'
    p, t, s, inc = rep['probability'], rep['temperature'], rep['stage'], rep['increment']
    L = [f"### KRS の較正測定（{rep['days'][0]}〜{rep['days'][-1]}・確定{rep['races']}R）", '',
         '測定のみ。KRS・係数・正式順位・買い目は変更していません。SSR は未較正の頻度で、補正値も研究用です。', '',
         '**勝ち馬の確率（小さいほど良い）**', '', '| 確率の出どころ | 対数損失 | Brier | ECE |', '|---|---|---|---|']
    for k, nm in (('krs_w', 'KRS（SSR-W）'), ('paper_w', 'PAPER の勝率'), ('mkt_w', '市場（単勝オッズ）')):
        x = p.get(k) or {}
        L.append(f"| {nm} | {x.get('log_loss')} | {x.get('brier')} | {x.get('ece')} |")
    z = (p.get('krs_w') or {}).get('winner_at_zero')
    if z:
        L.append(f"- KRS が勝ち頻度0（5,000回で一度も勝たない）とした馬が勝ったレース：{z}R（対数損失を大きく悪化させる主因）")
    k = t.get('krs_w') or {}
    T = k.get('T_fitted_on_train') or 1
    L += ['', f"- 温度補正（{k.get('train_days')} で T を決め、{k.get('test_days')} で試験）：KRS の T={T}"
              f"（{'1より大＝KRSは自信過剰、ならす方向' if T > 1 else '1より小＝KRSは控えめ、尖らせる方向' if T < 1 else '補正不要'}）、"
              f"試験の対数損失 {k.get('test_log_loss_identity')} → {k.get('test_log_loss_tempered')}（市場 {k.get('test_log_loss_market')}）"]
    rel = [b for b in (p.get('krs_w') or {}).get('reliability') or [] if b['n']]
    if rel:
        L.append('- KRS の信頼度（予測の帯→実際の勝率）：' + '、'.join(f"{b['bin']} {b['mean_pred']:.2f}→{b['actual']:.2f}（{b['n']}頭）" for b in rel))
    L.append(f"- 3着内（SSR-T3）の Brier：{rep.get('krs_top3_brier')}")
    L += ['', '**位置の再現（1角・4角）**', '']
    if s['races_with_passing_order']:
        for cn in ('1角', '4角'):
            x = s[cn]
            L.append(f"- {cn}：平均ずれ {x['mae_positions']} 頭分、予測の幅（p25〜p75）に入った割合 {x['inside_p25_p75']}（名目 0.5）・{x['horses']}頭")
        f3 = s['front3_stays_front3']
        L.append(f"- 予測の先頭馬が実際に1角先頭：{s['predicted_leader_led_1角']}／1角3番手内の馬が4角も3番手内：予測 {f3['predicted']}・実際 {f3['actual']}（{f3['horses']}頭）")
    L.append(f"- 通過順あり {s['races_with_passing_order']}R・なし {s['races_without']}R（結果ページの通過順は 11/26 から記録、それ以前は NAR 月次 CSV・結果ページの過去分で補完）")
    L += ['', '**KRS を使う価値（29指数の正式順位との比較）**', '',
          f"- 勝ち馬の順位：KRS が上 {inc['winner_rank_krs_better']}R・同じ {inc['same']}R・下 {inc['worse']}R",
          f"- 3着内 AUC：KRS {inc['auc_top3_krs']}／正式順位 {inc['auc_top3_formal_ranking']}"]
    cv = rep.get('variants') or {}
    if cv:
        L += ['', '**係数を変えた再計算（研究・結果確定後に同じ入力・同じ乱数で再実行）**', '',
              '| 比較 | R | 勝ち 対数損失 | 3着内 AUC | 1角3番手内→4角3番手内（予測/実際） | 4角ずれ |', '|---|---|---|---|---|---|']
        for name, row in cv.items():
            for lab, x in row.items():
                f3 = x['front3_stays_front3']
                L.append(f"| {'正式 KRS' if lab == 'formal' else lab} | {x['races']} | {x['log_loss']} | {x['auc_top3']} | "
                         f"{f3['predicted']}/{f3['actual']} | {x['4角_mae']} |")
    bv = rep.get('by_venue') or {}
    if bv:
        L += ['', '| 競馬場 | R | KRS 対数損失 | 市場 | 勝ち馬順位 KRS上/同/下 |', '|---|---|---|---|---|']
        for v, x in bv.items():
            L.append(f"| {VENUE_JA.get(v, v)} | {x['races']} | {x['krs_log_loss']} | {x['mkt_log_loss']} | "
                     f"{x['winner_rank_krs_better']}/{x['same']}/{x['worse']} |")
    return '\n'.join(L) + '\n'


def weekly(root, today):
    d = Path(root) / 'krs_calib'
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

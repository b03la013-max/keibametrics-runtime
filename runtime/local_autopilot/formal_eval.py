"""LOCAL formal post-result evaluation (evidence only; never changes MEC, cap, KRS or capital).

Per settled formal race:
  * KRS vs Static: winner rank and top-3 capture under the frozen Static ranking vs the KRS SSR ranks
    (IMPROVED / WORSENED / NEUTRAL) - P0-B 3.4.
  * 60-point cap: tickets before / after the cap, dropped tickets and coverage, investment saved,
    hits lost, loss avoided, PFS change - P1-B 5.2. LIVE_R54 when the signed race carried the cap;
    REPLAY_CAP_ONLY (known-result replay, not OOS) when it predates R54.
"""
import json
from pathlib import Path

PROFILE = 'KM-LOCAL-FORMAL-EVAL-v1.0-20261117'
ORDERED = ('EXACTA', 'TRIFECTA', 'BRACKET_EXACTA')
CAP = 60


def _key(t):
    sel = [int(x) for x in t['selection']]
    return '-'.join(map(str, sel if t['bet_type'] in ORDERED else sorted(sel)))


def settle(tickets, res):
    ns = set(res.get('non_starters') or []) | set(res.get('non_starters_inferred') or [])
    inv = pay = 0
    hits = []
    for t in tickets:
        if any(int(x) in ns for x in t['selection']):
            continue
        stake = int(t.get('stake') or 100)
        inv += stake
        p = (res['payouts'].get(t['bet_type']) or {}).get(_key(t))
        if p:
            pay += p * stake // 100
            hits.append(f"{t['bet_type']}:{_key(t)}")
    return {'invest': inv, 'payout': pay, 'pfs': round(100 * pay / inv, 1) if inv else None, 'hits': hits}


def cap_eval(sm, res, full29=None):
    if sm.get('signed_final_tickets'):
        full, kept, mode = sm['signed_final_tickets'], sm['tickets'], 'LIVE_R54'
    else:
        from runtime.local_autopilot import formal_rakuten as fr
        full = sm.get('tickets') or []
        ranking = sm.get('ranking') or []
        if full29:
            try:
                ranking = [str(x) for x in fr.numerical_ranking(full29)[0]]
            except Exception:
                pass
        kept, mode = fr.cap_tickets(full, ranking, CAP)['tickets'], 'REPLAY_CAP_ONLY'
    a, b = settle(full, res), settle(kept, res)
    kept_ids = {(t['bet_type'], _key(t)) for t in kept}
    dropped = [t for t in full if (t['bet_type'], _key(t)) not in kept_ids]
    return {'mode': mode, 'mec_tickets': len(full), 'kept_tickets': len(kept), 'dropped_tickets': len(dropped),
            'dropped_coverage_ids': sorted({c for t in dropped for c in t.get('coverage_ids') or []})[:40],
            'invest_full': a['invest'], 'invest_capped': b['invest'], 'invest_saved': a['invest'] - b['invest'],
            'payout_full': a['payout'], 'payout_capped': b['payout'],
            'hits_lost': sorted(set(a['hits']) - set(b['hits'])),
            'loss_avoided': max(0, (a['invest'] - a['payout']) - (b['invest'] - b['payout'])),
            'pfs_full': a['pfs'], 'pfs_capped': b['pfs']}


def krs_eval(sm, util, res):
    order = [int(x) for x in res['order']]
    top3 = set(order[:3])
    static = [int(x) for x in sm.get('ranking') or []]
    rows = (util or {}).get('summary') or []
    krs_w = [int(r['horse_no']) for r in sorted(rows, key=lambda r: (r.get('ranks') or {}).get('SSR-W', 99))]
    krs_t3 = [int(r['horse_no']) for r in sorted(rows, key=lambda r: (r.get('ranks') or {}).get('SSR-T3', 99))]
    if not static or not krs_w:
        return {'verdict': 'NOT_AVAILABLE'}
    rk = lambda lst, h: lst.index(h) + 1 if h in lst else None
    s_w, k_w = rk(static, order[0]), rk(krs_w, order[0])
    s_c, k_c = len(set(static[:3]) & top3), len(set(krs_t3[:3]) & top3)
    score = (s_w - k_w if s_w and k_w else 0) + 2 * (k_c - s_c)
    return {'winner_rank_static': s_w, 'winner_rank_krs_ssr_w': k_w, 'top3_capture_static': s_c,
            'top3_capture_krs_ssr_t3': k_c,
            'verdict': 'IMPROVED' if score > 0 else 'WORSENED' if score < 0 else 'NEUTRAL',
            'utility_class': (util or {}).get('utility_class')}


def evaluate_day(day_dir):
    fdir = Path(day_dir) / 'formal'
    rows = []
    for sp in sorted(fdir.glob('*.summary.json')) if fdir.exists() else []:
        key = sp.name.split('.')[0]
        rp = fdir / f'{key}.result.json'
        if not rp.exists():
            continue
        sm, res = json.loads(sp.read_text()), json.loads(rp.read_text())
        if sm.get('status') != 'SIGNED_FINAL' or not res.get('payouts'):
            continue
        ld = lambda n: json.loads((fdir / f'{key}.{n}.json').read_text()) if (fdir / f'{key}.{n}.json').exists() else None
        rows.append({'race': key, 'krs': krs_eval(sm, ld('krs_prediction_utility'), res),
                     'cap': cap_eval(sm, res, ld('full29'))})
    agg = {'races': len(rows),
           'krs_verdicts': {v: sum(1 for r in rows if r['krs']['verdict'] == v)
                            for v in ('IMPROVED', 'NEUTRAL', 'WORSENED', 'NOT_AVAILABLE')}}
    for mode in ('LIVE_R54', 'REPLAY_CAP_ONLY'):
        c = [r['cap'] for r in rows if r['cap']['mode'] == mode]
        if c:
            s = lambda k: sum(x[k] for x in c)
            agg[mode] = {'races': len(c), 'invest_full': s('invest_full'), 'invest_capped': s('invest_capped'),
                         'payout_full': s('payout_full'), 'payout_capped': s('payout_capped'),
                         'pfs_full': round(100 * s('payout_full') / s('invest_full'), 1) if s('invest_full') else None,
                         'pfs_capped': round(100 * s('payout_capped') / s('invest_capped'), 1) if s('invest_capped') else None,
                         'races_with_lost_hits': sum(1 for x in c if x['hits_lost']), 'loss_avoided': s('loss_avoided')}
    return {'profile': PROFILE, 'race_date': Path(day_dir).name,
            'note': 'REPLAY_CAP_ONLY applies the R54 cap to a pre-R54 MEC set on known results: research, not OOS.',
            'aggregate': agg, 'races': rows}


def md(o):
    a = o['aggregate']
    L = [f"# 地方版 正式評価 {o['race_date']}（KRS改善/悪化・60点上限）", '', f"- 対象 {a['races']}R／KRS判定 {a['krs_verdicts']}"]
    for mode, label in (('LIVE_R54', '実運用（R54）'), ('REPLAY_CAP_ONLY', '上限のみ再生（既知結果・OOSではない）')):
        if mode in a:
            m = a[mode]
            L.append(f"- {label} {m['races']}R：全MEC {m['invest_full']:,}円→{m['payout_full']:,}円（{m['pfs_full']}%）／"
                     f"上限後 {m['invest_capped']:,}円→{m['payout_capped']:,}円（{m['pfs_capped']}%）／"
                     f"的中を失ったRace {m['races_with_lost_hits']}／回避損失 {m['loss_avoided']:,}円")
    L += ['', '| Race | KRS判定 | 1着順位 Static→KRS | Top3捕捉 Static→KRS | 方式 | 券数 全→上限後 | 回収 全→上限後 | 失った的中 |',
          '|---|---|---|---|---|---|---|---|']
    for r in o['races']:
        k, c = r['krs'], r['cap']
        L.append(f"| {r['race']} | {k['verdict']} | {k.get('winner_rank_static')}→{k.get('winner_rank_krs_ssr_w')} | "
                 f"{k.get('top3_capture_static')}→{k.get('top3_capture_krs_ssr_t3')} | {c['mode']} | "
                 f"{c['mec_tickets']}→{c['kept_tickets']} | {c['pfs_full']}%→{c['pfs_capped']}% | {', '.join(c['hits_lost']) or '-'} |")
    L += ['', f"<sub>{o['note']}</sub>", '']
    return '\n'.join(L)


def write_daily(day_dir):
    o = evaluate_day(day_dir)
    if not o['races']:
        return None
    d = Path(day_dir) / 'review'
    d.mkdir(parents=True, exist_ok=True)
    (d / 'formal_eval.json').write_text(json.dumps(o, ensure_ascii=False, indent=1) + '\n')
    (d / 'formal_eval.md').write_text(md(o))
    return o

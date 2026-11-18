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


SMALL = (5, 10, 20, 30)   # research caps (C05/C10/C20/C30); Control = R54 60 (Production unchanged)


def small_eval(sm, res):
    """Same frozen prediction, same KRS/MEC output, same selection order as the R54 cap (tier, rank sum, MEC
    order); only the point limit differs. 100-yen flat stakes, so equal points = equal budget."""
    from runtime.local_autopilot import formal_rakuten as fr
    full = sm.get('signed_final_tickets') or sm.get('tickets') or []
    ranking = [str(x) for x in sm.get('ranking') or []]
    out = {}
    for n in SMALL:
        kept = fr.cap_tickets(full, ranking, n)['tickets'] if len(full) > n else full
        s = settle(kept, res)
        out[f'C{n:02d}'] = {'tickets': len(kept), **{k: s[k] for k in ('invest', 'payout', 'pfs')},
                            'hit': bool(s['hits'])}
    return out


def mec_composition(sm):
    """Why tickets multiply: role sizes, the P3 label spread vs material thirds, MEC bet-type mix."""
    roles = sm.get('roles') or {}
    cnt = lambda r: sum(1 for v in roles.values() if r in v)
    full = sm.get('signed_final_tickets') or sm.get('tickets') or []
    mix = {}
    for t in full:
        mix[t['bet_type']] = mix.get(t['bet_type'], 0) + 1
    thirds = {str(t['selection'][-1]) for t in full if t['bet_type'] in ('TRIFECTA',)}
    return {'W': cnt('W'), 'P2': cnt('P2'), 'P3_label': cnt('P3'), 'active': len(roles),
            'material_third_in_trifecta': len(thirds), 'mec_tickets': len(full), 'bet_mix': mix,
            'recommended_tickets': len(sm.get('tickets') or [])}


def concentration(pairs):
    """Per-race (invest, payout) -> hit / profit / hit-but-loss races, largest single-race payout share and the
    PFS without that race (Drive 2026-11-18 全場反省 §3.4/§11: 的中赤字率・最大払戻依存). Descriptive only."""
    py = sum(b for _, b in pairs)
    hit = [(a, b) for a, b in pairs if b > 0]
    out = {'hit_races': len(hit), 'profit_races': sum(1 for a, b in hit if b > a),
           'hit_but_loss_races': sum(1 for a, b in hit if b <= a), 'top1_payout_share': None, 'pfs_ex_top1': None}
    if py:
        i = max(range(len(pairs)), key=lambda j: pairs[j][1])
        rest = pairs[:i] + pairs[i + 1:]
        ri, rp = sum(a for a, _ in rest), sum(b for _, b in rest)
        out['top1_payout_share'] = round(100 * pairs[i][1] / py, 1)
        out['pfs_ex_top1'] = round(100 * rp / ri, 1) if ri else None
    return out


def evaluate_day(day_dir):
    from runtime.local_autopilot.checkpoint10 import effective_dir
    base = Path(day_dir) / 'formal'
    rows = []
    for sp in sorted(base.glob('*.summary.json')) if base.exists() else []:
        key = sp.name.split('.')[0]
        fdir = effective_dir(day_dir, key)
        sp = fdir / f'{key}.summary.json'
        rp = fdir / f'{key}.result.json'
        if not rp.exists():
            continue
        sm, res = json.loads(sp.read_text()), json.loads(rp.read_text())
        if sm.get('status') != 'SIGNED_FINAL' or not res.get('payouts'):
            continue
        ld = lambda n: json.loads((fdir / f'{key}.{n}.json').read_text()) if (fdir / f'{key}.{n}.json').exists() else None
        rev1 = None
        if sm.get('revision') == 2:   # T-10 effect: the superseded Revision 1 tickets on the same result
            sm1 = json.loads((base / f'{key}.summary.json').read_text())
            s1, s2 = settle(sm1.get('tickets') or [], res), settle(sm.get('tickets') or [], res)
            rev1 = {'rev1': {k: s1[k] for k in ('invest', 'payout', 'pfs')}, 'rev2': {k: s2[k] for k in ('invest', 'payout', 'pfs')},
                    'winner_rank_rev1': ([str(x) for x in sm1.get('ranking') or []].index(str(res['order'][0])) + 1
                                         if str(res['order'][0]) in [str(x) for x in sm1.get('ranking') or []] else None),
                    'winner_rank_rev2': ([str(x) for x in sm.get('ranking') or []].index(str(res['order'][0])) + 1
                                         if str(res['order'][0]) in [str(x) for x in sm.get('ranking') or []] else None)}
        rows.append({'race': key, 'revision': sm.get('revision', 1), 'check10_vs_rev1': rev1,
                     'krs': krs_eval(sm, ld('krs_prediction_utility'), res),
                     'cap': cap_eval(sm, res, ld('full29')), 'small': small_eval(sm, res),
                     'mec': mec_composition(sm)})
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
    if rows:
        sm_ = {}
        for c in [f'C{n:02d}' for n in SMALL]:
            xs = [r['small'][c] for r in rows]
            iv, py = sum(x['invest'] for x in xs), sum(x['payout'] for x in xs)
            sm_[c] = {'invest': iv, 'payout': py, 'pfs': round(100 * py / iv, 1) if iv else None,
                      'hit_races': sum(1 for x in xs if x['hit']),
                      'top1_payout_share': round(100 * max(x['payout'] for x in xs) / py, 1) if py else None}
        live = [r['cap'] for r in rows]
        sm_['R54_60'] = {'invest': sum(x['invest_capped'] for x in live), 'payout': sum(x['payout_capped'] for x in live)}
        sm_['MEC_FULL'] = {'invest': sum(x['invest_full'] for x in live), 'payout': sum(x['payout_full'] for x in live)}
        for k in ('R54_60', 'MEC_FULL'):
            v = sm_[k]
            v['pfs'] = round(100 * v['payout'] / v['invest'], 1) if v['invest'] else None
        sm_['R54_60'].update(concentration([(x['invest_capped'], x['payout_capped']) for x in live]))
        sm_['MEC_FULL'].update(concentration([(x['invest_full'], x['payout_full']) for x in live]))
        agg['small_point_comparison'] = sm_
        m = [r['mec'] for r in rows]
        agg['mec_composition_mean'] = {k: round(sum(x[k] for x in m) / len(m), 1)
                                       for k in ('W', 'P2', 'P3_label', 'active', 'material_third_in_trifecta',
                                                 'mec_tickets', 'recommended_tickets')}
        agg['revisions'] = sum(1 for r in rows if r['revision'] == 2)
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
    sc = a.get('small_point_comparison')
    if sc:
        L += ['', '## 少点数Candidate比較（研究・同一予測/KRS/MEC、選択順はR54上限と同じ、100円均等）', '',
              '| 方式 | 投資 | 払戻 | 回収率 | 的中Race | 最大1R依存 |', '|---|---|---|---|---|---|']
        for k in ('C05', 'C10', 'C20', 'C30', 'R54_60', 'MEC_FULL'):
            v = sc[k]
            L.append(f"| {k} | {v['invest']:,} | {v['payout']:,} | {v['pfs']}% | {v.get('hit_races', '-')} | "
                     f"{v.get('top1_payout_share', '-')} |")
        for k in ('R54_60', 'MEC_FULL'):
            v = sc[k]
            if 'hit_but_loss_races' in v:
                L.append(f"- {k}：的中{v['hit_races']}R（黒字{v['profit_races']}R・的中赤字{v['hit_but_loss_races']}R）"
                         f"／最大1R依存 {v['top1_payout_share']}%／最大1R除外の回収率 {v['pfs_ex_top1']}%（記述統計）")
        mc = a['mec_composition_mean']
        L += ['', f"- MEC構成の平均：W {mc['W']}頭・P2 {mc['P2']}頭・P3ラベル {mc['P3_label']}頭（出走 {mc['active']}頭）"
                  f"・三連単の3着候補 {mc['material_third_in_trifecta']}頭・MEC {mc['mec_tickets']}点→推薦 {mc['recommended_tickets']}点"]
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

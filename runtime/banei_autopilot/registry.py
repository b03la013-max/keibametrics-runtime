"""ばんえい版 改善の仕組み（Owner 2026-11-21 22:43「絶えず改善しなさい／改善する仕組みを作りなさい」、自動昇格を承認）。

情報→点数の変換、指数の式、合成、券面の規則を「設定（config）」として持ち、本番（production）と影の候補式（candidates）を
同じ未知のレースで並べて比べ続ける。状態は KM_BAN_OUT/challenger_registry.json（データブランチ）に保存し、毎日の反省会の後に
step() が次を行う。

1. 昇格: 候補が本番より良いと「事前に決めた条件」（PROMOTE）を満たしたら、自動で本番に切り替える（版を1つ上げる）。
   切り替えた直前の本番は 'PREV' として影で走らせ続ける。
2. 戻す: 昇格後、PREV が新しい本番に同じ条件で勝ったら、自動で元に戻す。
3. 引退: RETIRE_AT レースを過ぎても昇格条件を満たさない候補は RETIRED（記録は残す）。
4. 新しい候補: 影の候補が MAX_ACTIVE 未満になったら、本番の設定の「近傍」（NEIGHBORS）から未試行のものを自動登録する。
   P1仮説から作る候補は毎晩の作業が add() で登録する。
統計: 勝ち馬の評価順位の差（候補−本番、小さいほど良い）を対にして、ブートストラップ（seed固定）の片側信頼区間で判定。
同時に走る候補数で有意水準を割る（Bonferroni）。結果を見てから条件を変えない（PROMOTE は登録日つきで固定）。
"""
import copy
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import mean

import challengers

JST = timezone(timedelta(hours=9))
PROMOTE = {'registered_at': '2026-11-21T22:50+09:00',
           'min_races': 100,                 # 少なくともこのレース数（同じ本番のもとで）
           'alpha': 0.05,                    # 片側・候補数で割る
           'rank_metric': 'winner_win_rank',  # 勝ち馬の評価順位（小さいほど良い）
           'top3_tol': 0.05,                 # 3着内馬の複順位5位内の平均が本番より 0.05 以上悪くない
           'pfs_ex_top1_tol': 5.0,           # 最高1本を除いた回収率が本番より 5 ポイント以上悪くない
           'boot': 2000}
RETIRE_AT = 300
MAX_ACTIVE = 16
# 本番の数値設定の近傍（新しい候補の自動生成）。キー: (設定の場所, 名前) -> 候補を作る関数
NEIGHBORS = [
    ('patch', 'SBO_SHARE', lambda v: [round(min(1.0, (v if v is not None else 0.30) + d), 2) for d in (-0.15, 0.15)]),
    ('patch', 'MARKET_W', lambda v: [round(min(0.8, max(0.0, (v or 0.0) + d)), 2) for d in (-0.15, 0.15)]),
    ('patch', 'PICKS_W', lambda v: [round(max(0.0, (v or 0.0) + d), 2) for d in (-0.75, 0.75)]),
    ('tpatch', 'FORCE_TRIO_AXIS', lambda v: [None if v else 2]),
    # 合成式の係数（根拠が最も薄い所: PROVENANCE 弱点2）
    ('patch', 'SCORE', lambda v: [_score(v, win_brs=x) for x in (0.0, 1.0)] + [_score(v, win_bta=x) for x in (0.0, 1.0)]),
    # BSI の重み（近走/馬場/平均）
    ('patch', 'BSI_W', lambda v: [_bsi(v, d) for d in (('recent', 'track'), ('track', 'recent'), ('avg', 'recent'))]),
]


def _score(v, **kw):
    import engine
    base = copy.deepcopy(v or engine.SCORE)
    base.update(kw)
    return base


def _bsi(v, d):
    import engine
    w = dict(v or engine.BSI_W)
    up, down = d
    step = 0.05 if w[down] >= 0.1 else 0.0
    w[up] = round(w[up] + step, 2)
    w[down] = round(w[down] - step, 2)
    return w


def _now():
    return datetime.now(JST).isoformat(timespec='minutes')


def path(root):
    return Path(root) / 'challenger_registry.json'


QUEUE = Path(__file__).with_name('candidates_queue.json')     # 毎晩の作業が P1 仮説から追加する候補（main に PR で）


def _merge_queue(reg):
    """candidates_queue.json の候補を registry に取り込む（同じIDや同じ設定は取り込まない）。"""
    try:
        q = json.loads(QUEUE.read_text()) if QUEUE.exists() else {}
    except ValueError:
        q = {}
    for cid, c in (q.get('candidates') or {}).items():
        add(reg, cid, c.get('what', ''), c.get('config') or {}, c.get('why', 'queue'))
    return reg


# Owner の採否（registry の自動規則の外で Owner が決めたもの）。記録は消さず status だけを変える（試して落とした候補も残す）。
OWNER_DECISIONS = {
    'EXACT_BY_W': {'status': 'REJECTED', 'at': '2026-11-28T23:10+09:00',
                   'reason': 'Owner 2026-11-28「不採用とします」。W3頭以上で三連単を外したあと三連複を足さず 2〜7点しか買わない'
                             '（24R中22R）ため同じ30点の比較になっていない（KAG-BAN Purple REJECT-WITH-REASON）。狙いどおりの版は EXACT_BY_W_FILL'},
    'AXIS2_EXACT_BY_W': {'status': 'REJECTED', 'at': '2026-11-28T23:10+09:00',
                         'reason': 'Owner 2026-11-28「不採用とします」。EXACT_BY_W と同じ欠陥で 11〜24点しか買わず同じ30点の比較になっていない'},
}


def _apply_owner_decisions(reg):
    for cid, d in OWNER_DECISIONS.items():
        c = reg['candidates'].get(cid)
        if c and c.get('status') == 'SHADOW':
            c.update(status=d['status'], decided_at=d['at'], decision_reason=d['reason'])
            reg.setdefault('history', []).append({'at': d['at'], 'event': 'OWNER_' + d['status'], 'candidate': cid,
                                                  'evidence': {'reason': d['reason']}})
    return reg


def load(root):
    p = path(root)
    if p.exists():
        return _apply_owner_decisions(_merge_queue(json.loads(p.read_text())))
    cands = {cid: {'what': c['what'], 'config': challengers.config_of(c), 'status': c['status'],
                   'registered': c.get('registered', challengers.PREREG['registered_at'])}
             for cid, c in challengers.PREREG['candidates'].items()}
    return _apply_owner_decisions(_merge_queue({'production': {'id': 'BASE', 'version': 'KM-BAN-v4.0-static-r1', 'config': {}, 'since': None},
                                                'candidates': cands, 'history': [], 'promote_rule': PROMOTE}))


def save(root, reg):
    p = path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(reg, ensure_ascii=False, indent=1, default=str))


def add(reg, cid, what, config, why):
    """新しい候補を登録（毎晩の作業・自動生成）。同じ設定の候補が既にあれば登録しない。"""
    if cid in reg['candidates'] or any(c.get('config') == config for c in reg['candidates'].values()):
        return False
    reg['candidates'][cid] = {'what': what, 'config': config, 'status': 'SHADOW', 'registered': _now(), 'why': why}
    return True


def _pairs(revs, cid, since):
    out = []
    for x in revs:
        sh = x.get('shadow') or {}
        b, c = sh.get('BASE'), sh.get(cid)
        if not b or not c or 'error' in b or 'error' in c:
            continue
        if since and (x.get('day') or '') < since:
            continue
        if b.get('winner_win_rank') is None or c.get('winner_win_rank') is None:
            continue
        out.append((b, c))
    return out


def compare(revs, cid, since, n_active):
    """BASE（今の本番）と候補 cid の対比較。昇格条件を満たしたかと、その数字を返す。"""
    P = _pairs(revs, cid, since)
    n = len(P)
    res = {'n': n}
    if n == 0:
        return res
    d = [c['winner_win_rank'] - b['winner_win_rank'] for b, c in P]
    rng = random.Random(0)
    boots = sorted(mean(rng.choice(d) for _ in d) for _ in range(PROMOTE['boot']))
    a = PROMOTE['alpha'] / max(1, n_active)
    upper = boots[min(len(boots) - 1, int((1 - a) * len(boots)))]
    t3 = mean(c['top3_in_place5'] - b['top3_in_place5'] for b, c in P)

    def pfs_ex(side):
        st = sum(p[side]['stake'] for p in P)
        rt = sorted((p[side]['return'] for p in P), reverse=True)
        top_stake = next((p[side]['stake'] for p in P if p[side]['return'] == rt[0]), 0) if rt else 0
        return 100 * (sum(rt) - (rt[0] if rt else 0)) / (st - top_stake) if st - top_stake > 0 else None
    pb, pc = pfs_ex(0), pfs_ex(1)
    res.update(mean_rank_diff=round(mean(d), 3), upper=round(upper, 3), alpha=round(a, 4), top3_diff=round(t3, 3),
               pfs_ex_top1_base=round(pb, 1) if pb is not None else None,
               pfs_ex_top1_cand=round(pc, 1) if pc is not None else None)
    res['promote'] = bool(n >= PROMOTE['min_races'] and upper < 0 and t3 >= -PROMOTE['top3_tol']
                          and (pb is None or pc is None or pc >= pb - PROMOTE['pfs_ex_top1_tol']))
    return res


# KCP-BAN（Owner 2026-11-26 21:25「KCP は永続的に実施」）: 指数の成分の識別力（review.component_auc）を毎晩集計し、
# 事前に固定した条件を満たした成分について「その成分の重みを0にする」影の候補を自動で登録する。比較・昇格・戻す・
# 引退はほかの候補と同じ PROMOTE の条件で行う（本番の数値は手で変えない）。
KCP = {'registered_at': '2026-11-26T21:40:00+09:00', 'min_races': 100, 'auc_top3_below': 0.55, 'max_active': 3,
       'components': {'bta': 'bta', 'mpa': 'mpa', 'brs': 'brs', 'wda': 'wda', 'front_bonus': 'front', 'jbr': 'jbr',
                      'adf': 'adf', 'bwl': 'bwl', 'cci': 'cci', 'cpu': 'cpu'}}


def kcp_candidates(revs, prod_cfg):
    """条件を満たした成分 → 影の候補 {cid: (what, config)}。成分の AUC は全期間の発走前凍結の記録から。"""
    import review, engine
    s = review.component_auc_summary(revs) or {}
    out = {}
    base_w = dict(engine.COMP_W, **(((prod_cfg or {}).get('patch') or {}).get('COMP_W') or {}))
    for comp, knob in KCP['components'].items():
        d = s.get(comp) or {}
        if (d.get('races') or 0) < KCP['min_races'] or d.get('auc_top3') is None or d['auc_top3'] >= KCP['auc_top3_below']:
            continue
        if base_w.get(knob) == 0.0:
            continue
        cfg = copy.deepcopy(prod_cfg or {})
        cfg.setdefault('patch', {})['COMP_W'] = dict(base_w, **{knob: 0.0})
        out[f'KCP_ABLATE_{knob}'] = (f"KCP-BAN: 成分 {comp} の重みを0（{d['races']}R で 3着内 AUC {d['auc_top3']}）", cfg)
    return out


def kcp_table(revs):
    import review
    return review.component_auc_summary(revs) or {}


def _all_reviews(root):
    revs = []
    for d in sorted(p for p in Path(root).iterdir() if (p / 'review').is_dir()):
        for f in sorted((d / 'review').glob('R*.review.json')):
            try:
                x = json.loads(f.read_text())
            except ValueError:
                continue
            x['day'] = d.name
            revs.append(x)
    return revs


# Owner 2026-11-28 23:33「改善は承認無しで進めて欲しい」：Owner の承認による止めは無し。
# ただし本番でまだ扱えない券種を使う候補は、本番の対応（オッズ・券面・精算・FORMAL）が入るまで昇格を待つ。
# 待っている間は NEEDS_PRODUCTION_SUPPORT を1回記録し、毎晩の反省会がその対応を実装して旗を True にする。
PRODUCTION_SUPPORT = (('tpatch', 'SINGLE_MODE', 'EXACTA_PRODUCTION_READY'),)


def needs_support(cfg):
    """本番でまだ扱えない設定を使う候補なら、足りない旗の名前を返す（無ければ None）。"""
    import tickets as T
    for where, key, flag in PRODUCTION_SUPPORT:
        if (cfg or {}).get(where, {}).get(key) is not None and not getattr(T, flag, False):
            return flag
    return None


def step(root, log=lambda *a: None):
    """毎日の反省会の後に呼ぶ。昇格・戻す・引退・新候補の生成を行い、registry と improvement_status.md を書く。"""
    reg = load(root)
    revs = _all_reviews(root)
    since = reg['production'].get('since')
    active = {k: v for k, v in reg['candidates'].items() if v['status'] == 'SHADOW' and k != 'BASE'}
    table = {cid: compare(revs, cid, max(since or '', (c.get('registered') or '')[:10]), len(active))
             for cid, c in active.items()}
    events = []
    for cid, t in table.items():                                  # 本番の対応待ち（承認待ちではない）
        c = reg['candidates'][cid]
        flag = needs_support(c.get('config'))
        if t.get('promote') and flag and not c.get('support_needed_at'):
            c['support_needed_at'] = _now()
            events.append(('NEEDS_PRODUCTION_SUPPORT', cid, dict(t, flag=flag)))
    winners = sorted([(t['mean_rank_diff'], cid) for cid, t in table.items()
                      if t.get('promote') and not needs_support(reg['candidates'][cid].get('config'))])
    if winners:
        cid = winners[0][1]
        prev = reg['production']
        c = reg['candidates'][cid]
        ver = prev['version'].split('+')[0] + f"+{cid}@{datetime.now(JST):%Y%m%d}"
        reg['candidates']['PREV'] = {'what': f"昇格前の本番（{prev['version']}）", 'config': prev.get('config') or {},
                                     'status': 'SHADOW', 'registered': _now(), 'guard_of': cid}
        reg['production'] = {'id': cid, 'version': ver, 'config': c['config'], 'since': datetime.now(JST).strftime('%Y-%m-%d'),
                             'promoted_from': prev['version'], 'evidence': table[cid]}
        c['status'] = 'PRODUCTION'
        if cid == 'PREV':                                         # 戻す（ロールバック）
            events.append(('ROLLBACK', cid, table[cid]))
        else:
            events.append(('PROMOTED', cid, table[cid]))
        for k, v in reg['candidates'].items():                    # 新しい本番のもとで比べ直す
            if v['status'] == 'SHADOW' and k not in ('PREV',):
                v['registered'] = _now()
    for cid, t in table.items():                                  # 引退
        if reg['candidates'][cid]['status'] == 'SHADOW' and t.get('n', 0) >= RETIRE_AT and not t.get('promote'):
            reg['candidates'][cid]['status'] = 'RETIRED'
            events.append(('RETIRED', cid, t))
    # 新しい候補（本番の近傍）
    prod_cfg = reg['production'].get('config') or {}
    n_active = sum(1 for v in reg['candidates'].values() if v['status'] == 'SHADOW')
    for where, name, gen in NEIGHBORS:
        if n_active >= MAX_ACTIVE:
            break
        cur = (prod_cfg.get(where) or {}).get(name)
        mod = __import__('engine' if where == 'patch' else 'tickets')
        eff = cur if cur is not None else getattr(mod, name, None)          # 本番で実際に効いている値
        for v in gen(cur):
            if v == cur or v == eff:
                continue
            cfg = copy.deepcopy(prod_cfg)
            if v is None:
                (cfg.get(where) or {}).pop(name, None)
            else:
                cfg.setdefault(where, {})[name] = v
            tag = v if not isinstance(v, dict) else '_'.join(f"{k}{x}" for k, x in v.items()
                                                             if not isinstance(x, dict) and x != (getattr(__import__('engine'), name).get(k)
                                                                                                    if isinstance(getattr(__import__('engine'), name), dict) else None))
            cid = f"AUTO_{name}_{tag}"
            if add(reg, cid, f"本番の近傍: {name}={json.dumps(v, ensure_ascii=False)}", cfg, 'auto-neighbor'):
                events.append(('REGISTERED', cid, {}))
                n_active += 1
                if n_active >= MAX_ACTIVE:
                    break
    # KCP-BAN: 識別力の低い成分を外す候補（近傍とは別枠で最大 KCP['max_active'] 本）
    try:
        kcp_active = sum(1 for k, v in reg['candidates'].items() if k.startswith('KCP_') and v['status'] == 'SHADOW')
        for cid, (what, cfg) in kcp_candidates(revs, reg['production'].get('config') or {}).items():
            if kcp_active >= KCP['max_active']:
                break
            if add(reg, cid, what, cfg, 'kcp-ban'):
                events.append(('REGISTERED', cid, {}))
                kcp_active += 1
        reg['kcp'] = {'at': _now(), 'rule': KCP, 'component_auc': kcp_table(revs)}
        import review as _rv
        reg['kiep'] = {'at': _now(), **_rv.kiep_summary(revs)}
        import governance
        reg['kag'] = {'at': _now(), 'summary': governance.summary(revs), 'meta': governance.meta(reg, revs)}
        import intel
        reg['kdp_ksp_kap'] = {'at': _now(), 'structure': intel.structure_summary(revs), 'risk': intel.risk_summary(revs),
                              'drift': intel.drift_summary(revs),
                              'rules': {'structure': intel.STRUCTURE, 'risk': intel.RISK, 'drift': intel.DRIFT}}
    except Exception as e:                                        # 較正の集計は本処理を止めない
        reg['kcp'] = {'at': _now(), 'error': f'{type(e).__name__}:{str(e)[:120]}'}
    # KIEP-BAN P0: Formula Ledger を毎晩書き、算式の SHA が変わった日を履歴に残す
    try:
        import formula_ledger
        led = formula_ledger.build()
        (Path(root) / 'formula_ledger.json').write_text(json.dumps(led, ensure_ascii=False, indent=1) + '\n')
        fh = reg.setdefault('formula_history', [])
        if not fh or fh[-1]['formula_sha'] != led['formula_sha']:
            fh.append({'at': _now(), 'formula_sha': led['formula_sha'], 'production': reg['production']['version'],
                       'implementation_sha16': led['implementation_sha16']})
    except Exception as e:
        reg['formula_ledger_error'] = f'{type(e).__name__}:{str(e)[:120]}'
    reg['history'] += [{'at': _now(), 'event': e, 'candidate': c, 'evidence': t} for e, c, t in events]
    reg['last_step'] = {'at': _now(), 'table': table}
    save(root, reg)
    _status_md(root, reg, table)
    for e, c, t in events:
        log('IMPROVE', e, c, json.dumps(t, ensure_ascii=False)[:200])
    return events


def _status_md(root, reg, table):
    p = reg['production']
    L = ['# ばんえい 改善の状況（自動）', '',
         f"- 本番: {p['version']}（{p['id']}、{p.get('since') or '初版'}から）",
         f"- 昇格条件（{PROMOTE['registered_at']} 登録・固定）: 同じ本番のもとで {PROMOTE['min_races']}R 以上、勝ち馬の評価順位が"
         f"片側{int(PROMOTE['alpha'] * 100)}%（候補数で割る）で本番より良い、3着内馬の捕捉が {PROMOTE['top3_tol']} 以上悪くない、"
         f"最高1本を除いた回収率が {PROMOTE['pfs_ex_top1_tol']} ポイント以上悪くない。満たせば自動昇格、PREV が勝てば自動で戻す。"
         f"{RETIRE_AT}R で昇格しない候補は引退。", '',
         '| 候補 | 内容 | R | 順位差(平均) | 上側 | 3着内捕捉差 | 回収率(最高1本除く) 本番→候補 | 昇格条件 |',
         '|---|---|---|---|---|---|---|---|']
    for cid, t in sorted(table.items()):
        c = reg['candidates'].get(cid, {})
        L.append(f"| {cid} | {c.get('what', '')} | {t.get('n', 0)} | {t.get('mean_rank_diff', '')} | {t.get('upper', '')} | "
                 f"{t.get('top3_diff', '')} | {t.get('pfs_ex_top1_base', '')}→{t.get('pfs_ex_top1_cand', '')} | "
                 f"{'満たす' if t.get('promote') else ''} |")
    k = reg.get('kcp') or {}
    if k.get('component_auc'):
        L += ['', '## KCP-BAN 指数の成分の識別力（毎晩更新）', '',
              f"0.5＝識別なし。{KCP['min_races']}R 以上で 3着内 AUC が {KCP['auc_top3_below']} 未満の成分は、"
              f"重みを0にする影の候補（KCP_ABLATE_*）を自動登録（同時に最大{KCP['max_active']}本）。pop は人気の基準線。", '',
              '| 成分 | R | 3着内 AUC | 1着 AUC |', '|---|---|---|---|']
        L += [f"| {c} | {d['races']} | {d['auc_top3']} | {d['auc_win']} |"
              for c, d in sorted(k['component_auc'].items(), key=lambda kv: -(kv[1].get('auc_top3') or 0))]
    kp = reg.get('kiep') or {}
    if kp.get('components'):
        L += ['', '## KIEP-BAN 成分の健康診断（毎晩更新）', '',
              f"{kp['races']}R。単調性＝レース内で上位・中位・下位の3群に分けた3着内率（上位≥中位≥下位なら単調）。"
              "欠損率＝値の無い馬の割合。", '',
              '| 成分 | 判定R | 欠損率 | 上位 | 中位 | 下位 | 単調 |', '|---|---|---|---|---|---|---|']
        L += [f"| {c} | {d['races']} | {d['missing_rate']} | {d['top3_rate_high']} | {d['top3_rate_mid']} | {d['top3_rate_low']} | "
              f"{'○' if d['monotonic'] else '×' if d['monotonic'] is False else ''} |"
              for c, d in sorted(kp['components'].items()) if d['races']]
        rp = kp.get('redundant_pairs') or {}
        L += ['', f"- 重複（平均順位相関 |0.6| 以上）: {('、'.join(f'{p} {r}' for p, r in rp.items())) or 'なし'}",
              f"- 情報源の取得率: {('、'.join(f'{f} {r}' for f, r in (kp.get('feed_rate') or {}).items())) or '—'}"]
    x = reg.get('kdp_ksp_kap') or {}
    if x:
        L += ['', '## KDP・KSP・KAP（毎晩更新、証拠のみ）', '']
        st = x.get('structure') or {}
        if st:
            nm = {'ONE': '一強', 'TWO': '二強', 'THREE': '三強', 'MIXED': '混戦'}
            L += ['KDP レースの型（1着の点の上位差 4 以上で区切る、11/26 事前固定）', '',
                  '| 型 | R | 勝ち馬W内 | ◎1着 | 三連複 | 三連単 | 回収率 |', '|---|---|---|---|---|---|---|']
            L += [f"| {nm.get(k, k)} | {d['races']} | {d['winner_in_W']} | {d['honmei_win']} | {d['trio_hit']} | {d['exact_hit']} | {d['pfs']}% |"
                  for k, d in sorted(st.items())]
        r = x.get('risk') or {}
        if r:
            L += ['', f"KSP 仮想精算（{r['races']}R・{r['days']}開催日）: 回収率 {r['pfs']}%（最高1本除く {r['pfs_ex_top1']}%・3本除く {r['pfs_ex_top3']}%）、"
                  f"純損益 {r['net']:,}円、最大ドローダウン {r['max_drawdown']:,}円（{r['max_drawdown_races']}R）、連続不的中 最長 {r['longest_losing_streak']}R、"
                  f"的中赤字 {r['hit_but_loss']}/{r['hit_races']}R"]
            if 'var' in r:
                L += [f"- {r['note']}：仮想資金 {r['bankroll']:,}円で {r['boot_horizon_days']}開催日 → 損益の中央値 {r['median_net']:,}円、"
                      f"5% VaR {r['var']:,}円、CVaR {r['cvar']:,}円、途中で資金が尽きる割合 {r['ruin_rate']}"]
        d = x.get('drift') or {}
        if d:
            fl = '、'.join(f"{f['kind']}:{f['what']} {f['prior']}→{f['recent']}" for f in d.get('flags') or []) or 'なし'
            L += ['', f"KAP 環境変化の検知: {d['status']}"
                  + (f"（直近{d['recent_races']}R 対 それ以前{d['prior_races']}R、回収率 {d['pfs_prior']}%→{d['pfs_recent']}%、検知: {fl}）"
                     if d['status'] != 'WAITING' else f"（{d['races']}/{d['need']}R、窓がたまるまで待機）")]
    g = reg.get('kag') or {}
    if g:
        sm, mt = g.get('summary') or {}, g.get('meta') or {}
        L += ['', '## KAG-BAN 三チーム統治（Blue・Red・Purple、毎晩更新）', '',
              '発走前に凍結した記録だけで Red が機械反証（LEVEL-1、規則は 11/27 事前固定）。結果後に、その指摘が実際の最初の断線と'
              '同じ層だったか（当たり）を数える。本番は変えない。ChatGPT による独立反証（LEVEL-3）は Drive の記録を使い、応答と Owner 判断は改善の記録に残す。', '']
        if sm.get('challenges'):
            L += ['| 指摘 | 層 | 件数 | 当たり | 当たり率 | 基準率 | 倍率 |', '|---|---|---|---|---|---|---|']
            L += [f"| {cid} | {d['layer']} | {d['n']} | {d['confirmed']} | {d['precision']} | {d.get('base_rate')} | {d.get('lift')} |"
                  for cid, d in sm['challenges'].items()]
            L += ['', '倍率＝当たり率÷基準率（指摘の有無に関係なく、その層で断線したレースの割合）。1前後の指摘は見分ける力が無く、'
                      '100R 以上でそうなら RED-5 で REJECT-WITH-REASON の候補（規則を変えるときは新しい版として登録）。']
            L += ['', f"- 指摘のあったレースの断線率 {sm['fail_rate_with_challenge']}（{sm['races_with_challenge']}R）"
                      f" 対 指摘の無いレース {sm['fail_rate_without_challenge']}（{sm['races_without_challenge']}R）"]
        else:
            L += ['- まだ発走前の指摘の記録がありません（11/28 から）']
        L += [f"- RED-5 Meta: 影の候補 {mt.get('active')}本、30R 以上本番と同じ券面のままの候補 {mt.get('inert_after_30R') or 'なし'}、"
              f"同じ設定の重複 {mt.get('duplicate_configs') or 'なし'}"]
    fh = reg.get('formula_history') or []
    if fh:
        L += [f"- 算式の版（formula_ledger.json）: {fh[-1]['formula_sha'][:12]}（{fh[-1]['at'][:10]} から、記録 {len(fh)} 版）"]
    L += ['', '## 履歴', ''] + [f"- {h['at']} {h['event']} {h['candidate']}" for h in reg['history'][-30:]]
    L += ['', '引退・不採用の候補も registry に残す。新しい候補は本番の近傍から自動で、P1仮説からは毎晩の作業で登録する。']
    (Path(root) / 'improvement_status.md').write_text('\n'.join(L) + '\n')

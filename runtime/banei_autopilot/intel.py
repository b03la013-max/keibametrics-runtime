"""KDP・KSP・KAP（ばんえい版）— Owner 2026-11-26 22:03「永続的に実施」（ChatGPT 五大知能計画のうち ばんえい分）。

既存の仕組み（不確実性＝DCR・info_coverage・C0-INFO、市場＝NOMKT/MKT 影・market_drift・人気の AUC、条件付き役割＝
failure_chain・EXACT_* 影、変換＝funnel・compression_loss、反実仮想＝層ごとの影の候補 patch/tpatch/cuts）はそのまま使い、
足りないものだけをここに置く。どれも証拠のみで、本番の予想・券面・購入方針（毎レース・30点）は変えない。

- KDP-02 race_structure: レースの型（一強・二強・三強・混戦）。定義は下の STRUCTURE に事前固定し、結果を見て変えない。
- KSP-01/02 risk: 凍結券面の仮想精算で、最大ドローダウン・その期間・連続不的中・的中赤字率・最高1本/3本を除いた回収率・
  開催日単位のブロック・ブートストラップによる VaR/CVaR と仮想資金の枯渇率。確率の予測ではなく、過去の損失の形の要約。
- KAP-03 drift: 直近の窓とそれ以前で、成分の識別力・欠損率・情報源の取得率・回収率がどれだけ動いたか。検知だけで本番は変えない。
"""
import random

# KDP-02（2026-11-26 22:10 事前固定）: 1着の点（win_score）の上位差でレースを分ける
STRUCTURE = {'registered_at': '2026-11-26T22:10:00+09:00', 'key': 'win_score',
             'one_strong_gap': 4.0,      # 1位−2位 ≥ 4 → 一強
             'two_strong_gap': 4.0,      # 2位−3位 ≥ 4（一強でない）→ 二強
             'three_strong_gap': 4.0}    # 3位−4位 ≥ 4（上の2つでない）→ 三強、どれでもない → 混戦

# KSP（2026-11-26 22:10 事前固定）
RISK = {'registered_at': '2026-11-26T22:10:00+09:00', 'bankroll': 100000, 'horizon_days': 30, 'boot': 2000,
        'alpha': 0.05, 'seed': 20261126}

# KAP-03（2026-11-26 22:10 事前固定）
DRIFT = {'registered_at': '2026-11-26T22:10:00+09:00', 'window': 36, 'min_prior': 36, 'auc_shift': 0.08,
         'rate_shift': 0.15}


def race_structure(rows):
    sc = sorted((x.get(STRUCTURE['key']) for x in rows or [] if x.get(STRUCTURE['key']) is not None), reverse=True)
    if len(sc) < 4:
        return None
    g1, g2, g3 = sc[0] - sc[1], sc[1] - sc[2], sc[2] - sc[3]
    if g1 >= STRUCTURE['one_strong_gap']:
        return 'ONE'
    if g2 >= STRUCTURE['two_strong_gap']:
        return 'TWO'
    if g3 >= STRUCTURE['three_strong_gap']:
        return 'THREE'
    return 'MIXED'


def structure_summary(revs):
    """型ごとの R数・勝ち馬が W 内・◎1着・三連複/三連単的中・投資・払戻・回収率。"""
    out = {}
    for x in revs:
        st = x.get('structure')
        if not st:
            continue
        d = out.setdefault(st, {'races': 0, 'winner_in_W': 0, 'honmei_win': 0, 'trio_hit': 0, 'exact_hit': 0,
                                'stake': 0, 'return': 0})
        d['races'] += 1
        d['winner_in_W'] += int(bool(((x.get('finishers') or {}).get('1') or {}).get('in_role')))
        d['honmei_win'] += int(x.get('honmei_finish') == 1)
        d['trio_hit'] += int(bool(x.get('trio_hit')))
        d['exact_hit'] += int(bool(x.get('exact_hit')))
        d['stake'] += x.get('stake') or 0
        d['return'] += x.get('return') or 0
    for d in out.values():
        d['pfs'] = round(d['return'] / d['stake'] * 100, 1) if d['stake'] else None
    return out


def _ordered(revs):
    return sorted((x for x in revs if (x.get('stake') or 0) > 0), key=lambda x: (x.get('day') or '', x.get('key') or ''))


def risk_summary(revs, cfg=RISK):
    rs = _ordered(revs)
    if not rs:
        return None
    nets = [(x.get('return') or 0) - (x.get('stake') or 0) for x in rs]
    stake, ret = sum(x['stake'] for x in rs), sum(x.get('return') or 0 for x in rs)
    pays = sorted((x.get('return') or 0 for x in rs), reverse=True)
    cum, peak, mdd, dd_len, dd_max_len, start = 0, 0, 0, 0, 0, 0
    for n in nets:
        cum += n
        if cum >= peak:
            peak, dd_len = cum, 0
        else:
            dd_len += 1
            mdd = max(mdd, peak - cum)
            dd_max_len = max(dd_max_len, dd_len)
    streak = best = 0
    for x in rs:
        streak = 0 if (x.get('return') or 0) > 0 else streak + 1
        best = max(best, streak)
    hits = [x for x in rs if (x.get('return') or 0) > 0]
    hit_loss = sum(1 for x in hits if x['return'] < x['stake'])
    days = {}
    for x in rs:
        days.setdefault(x.get('day'), 0)
        days[x.get('day')] += (x.get('return') or 0) - x['stake']
    dnet = list(days.values())
    out = {'races': len(rs), 'days': len(dnet), 'stake': stake, 'return': ret, 'net': ret - stake,
           'pfs': round(ret / stake * 100, 1),
           'pfs_ex_top1': round((ret - sum(pays[:1])) / stake * 100, 1),
           'pfs_ex_top3': round((ret - sum(pays[:3])) / stake * 100, 1),
           'top1_share': round(pays[0] / ret, 3) if ret else None,
           'max_drawdown': mdd, 'max_drawdown_races': dd_max_len, 'longest_losing_streak': best,
           'hit_races': len(hits), 'hit_but_loss': hit_loss,
           'hit_but_loss_rate': round(hit_loss / len(hits), 3) if hits else None}
    if len(dnet) >= 3:                                   # 開催日単位のブロック・ブートストラップ（同じ日のレースの依存を保つ）
        rnd = random.Random(cfg['seed'])
        sums, ruin = [], 0
        for _ in range(cfg['boot']):
            bank, lo = cfg['bankroll'], cfg['bankroll']
            for _d in range(cfg['horizon_days']):
                bank += rnd.choice(dnet)
                lo = min(lo, bank)
            sums.append(bank - cfg['bankroll'])
            ruin += int(lo <= 0)
        sums.sort()
        k = max(1, int(cfg['alpha'] * len(sums)))
        out.update({'boot_horizon_days': cfg['horizon_days'], 'bankroll': cfg['bankroll'],
                    'var': -sums[k - 1], 'cvar': -round(sum(sums[:k]) / k),
                    'median_net': sums[len(sums) // 2], 'ruin_rate': round(ruin / cfg['boot'], 3),
                    'note': f"過去{len(dnet)}開催日の日次損益を復元抽出した仮想の分布（予測ではない）"})
    return out


def _window_stats(revs):
    import review
    auc = review.component_auc_summary(revs) or {}
    kp = review.kiep_summary(revs)
    st = sum(x.get('stake') or 0 for x in revs)
    rt = sum(x.get('return') or 0 for x in revs)
    return {'auc': {k: v.get('auc_top3') for k, v in auc.items()},
            'missing': {k: v.get('missing_rate') for k, v in (kp.get('components') or {}).items()},
            'feed': kp.get('feed_rate') or {}, 'pfs': round(rt / st * 100, 1) if st else None, 'races': len(revs)}


def drift_summary(revs, cfg=DRIFT):
    rs = sorted(revs, key=lambda x: (x.get('day') or '', x.get('key') or ''))
    if len(rs) < cfg['window'] + cfg['min_prior']:
        return {'status': 'WAITING', 'races': len(rs), 'need': cfg['window'] + cfg['min_prior']}
    recent, prior = _window_stats(rs[-cfg['window']:]), _window_stats(rs[:-cfg['window']])
    flags = []
    for k, v in recent['auc'].items():
        p = prior['auc'].get(k)
        if v is not None and p is not None and abs(v - p) >= cfg['auc_shift']:
            flags.append({'kind': 'CONCEPT', 'what': k, 'prior': p, 'recent': v})
    for k, v in recent['missing'].items():
        p = prior['missing'].get(k)
        if v is not None and p is not None and abs(v - p) >= cfg['rate_shift']:
            flags.append({'kind': 'DATA', 'what': k, 'prior': p, 'recent': v})
    for k in set(recent['feed']) | set(prior['feed']):
        v, p = recent['feed'].get(k, 0), prior['feed'].get(k, 0)
        if abs(v - p) >= cfg['rate_shift']:
            flags.append({'kind': 'SOURCE', 'what': k, 'prior': p, 'recent': v})
    return {'status': 'FLAGGED' if flags else 'STABLE', 'window': cfg['window'], 'recent_races': recent['races'],
            'prior_races': prior['races'], 'pfs_recent': recent['pfs'], 'pfs_prior': prior['pfs'], 'flags': flags}

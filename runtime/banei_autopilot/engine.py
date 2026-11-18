"""KeibaMetrics BAN (ばんえい・帯広) Static engine — v4.0-BAN implementation spec (Owner-approved 2026-11-19).

Implements the executable core of ばんえい攻略条項 (2026-08-03) + v2.3-BAN as one deterministic pass:
base indices (水分ボンバー first, own fallback) -> ISV/LIS -> BTA/MPA/BRS (キンタロー 区間実測) ->
WDA/FLA (no double count) -> JBR/ADF/BWL/CPU/POF/MOP/PCH/CCI -> DCR -> TPI ->
three rankings (1着 / 3着以内 / 穴複勝) -> roles W/P2/P3 -> marks, F3S, S3H, AKI, ASI.

Owner decisions applied: BSI weights 0.40/0.35/0.25 (provisional), TPI adjustments = midpoint of each
条項 range, 水分ボンバー weight 0.30 inside BSI source blend. Nothing here is a probability or EV
(全版共通: 未較正値の確率・EV表示禁止). Unknown values stay None -> neutral, never 0 (v2.3 第8条).
"""
from statistics import mean

BSI_W = {'recent': 0.40, 'track': 0.35, 'avg': 0.25}          # Owner 2026-11-19: provisional
SBO_SHARE = 0.30                                              # Owner 2026-11-18: 水分ボンバー 30% start
MID = lambda lo, hi: (lo + hi) / 2.0                          # Owner 2026-11-19: midpoint of ranges

RULESET = 'KM-BAN-v4.0-static-r1'


def _f(x):
    try:
        return None if x is None or x == '' else float(x)
    except (TypeError, ValueError):
        return None


def moisture_band(m):
    """攻略条項 第6節: 乾燥 ~1.5%, 中間, 湿った軽い馬場. Value alone never fixes 時計 (第21-5)."""
    m = _f(m)
    if m is None:
        return 'UNKNOWN'
    if m <= 1.5:
        return 'DRY'
    if m < 2.6:
        return 'MID'
    return 'WET'


# ---------------------------------------------------------------- base indices (spec 3-1)
def base_indices(h, moisture):
    """近走 / 馬場 / 平均 from 水分ボンバー speed indices (h['sbo_past'] = [{'idx','moisture'}...], newest
    first); fallback h['own_past'] (same shape, own time-based index). Provenance kept per value."""
    band = moisture_band(moisture)
    out = {}
    for src_key, src in (('sbo_past', 'SBO'), ('own_past', 'OWN')):
        past = [p for p in (h.get(src_key) or []) if _f(p.get('idx')) is not None]
        if not past:
            continue
        rec = _f(past[0]['idx'])
        same = [_f(p['idx']) for p in past if moisture_band(p.get('moisture')) == band and band != 'UNKNOWN']
        trk = mean(same) if same else None
        avg = mean(_f(p['idx']) for p in past[:5])
        for k, v in (('recent', rec), ('track', trk), ('avg', avg)):
            if v is not None and k not in out:
                out[k] = (round(v, 2), src)
    return {k: (out[k][0] if k in out else None) for k in BSI_W}, {k: out[k][1] for k in out}


def bsi(idx):
    have = {k: v for k, v in idx.items() if v is not None}
    if not have:
        return None
    w = sum(BSI_W[k] for k in have)
    return round(sum(BSI_W[k] * v for k, v in have.items()) / w, 2)


def isv(idx):
    v = [x for x in idx.values() if x is not None]
    if len(v) < 2:
        return None, 'UNKNOWN'
    d = max(v) - min(v)
    lab = 'VERY_STABLE' if d <= 2 else 'STABLE' if d <= 5 else 'STANDARD' if d <= 9 else 'UNSTABLE'
    return round(d, 2), lab


# ---------------------------------------------------------------- barrier / stage (spec 3-2, 3-4)
def bta(past):
    """BTA-B on the newest up-to-5 measured 第2障害 times (sec). Midpoint adjustments (TPI-equivalent)."""
    t = [_f(p.get('barrier_sec')) for p in (past or [])[:5]]
    t = [x for x in t if x is not None]
    if not t:
        return None, 'UNCONFIRMED', None
    m = mean(t)
    adj = 6.0 if m <= 18 else 3.0 if m <= 22 else 0.0 if m <= 27 else -3.0 if m <= 34 else -6.0
    spread = max(t) - min(t) if len(t) >= 2 else None
    ev = ('STABLE' if len(t) >= 3 and spread is not None and spread <= 6 else
          'CONDITIONAL' if len(t) >= 2 else 'PROVISIONAL')       # v2.7 BAN-BRES: 1回成功≠Stable
    return adj, ev, round(m, 1)


def mpa(past):
    g = []
    for p in (past or [])[:5]:
        a, b = _f(p.get('pos_first')), _f(p.get('pos_barrier'))
        if a is not None and b is not None:
            g.append(a - b)
    if not g:
        return None
    m = mean(g)
    return 5.0 if m >= 5 else 3.0 if m >= 3 else 1.5 if m >= 1 else -2.0 if m < 0 else 0.0


def brs(past):
    g = []
    for p in (past or [])[:5]:
        b, f = _f(p.get('pos_barrier')), _f(p.get('pos_finish'))
        if b is not None and f is not None:
            g.append(b - f)
    if not g:
        return None
    m = mean(g)
    return 4.0 if m >= 2 else 2.0 if m >= 1 else 0.0 if m >= 0 else -2.0


# ---------------------------------------------------------------- weight (spec 3-2, no double count)
def weight_terms(h, field, special, front_ok):
    """WDA-B vs FLA-B: the '軽量＋先行' bonus is taken once (max of the two), per v4.0 spec 3-2."""
    loads = [_f(x.get('load')) for x in field if _f(x.get('load')) is not None]
    me = _f(h.get('load'))
    if me is None or len(loads) < 2:
        return 0.0, 0.0, 'UNKNOWN'
    top = sorted(loads, reverse=True)[:3]
    diff = mean(top) - me                         # lighter than the heavy top group
    if diff >= 30:
        wda = MID(8, 12)
    elif diff >= 20:
        wda = MID(5, 8)
    elif diff >= 10:
        wda = MID(2, 4)
    else:
        wda = 0.0
    if not special and wda:                       # v2.3 第81条: 規定戦以外は逆転主因にしない
        wda *= 0.5
    front_bonus_wda = MID(2, 4) if wda and front_ok else 0.0
    fla_ok = diff >= 10 and front_ok and h.get('barrier_stable') and h.get('body_stable')
    front_bonus_fla = MID(2, 4) if fla_ok else 0.0
    return wda, max(front_bonus_wda, front_bonus_fla), ('FLA' if fla_ok else 'WDA' if wda else 'NONE')


def bwl(h):
    """BWL-B / BAN-BWR: only outside the good-run range with >=2 worsening signals."""
    bw, d = _f(h.get('body_weight')), _f(h.get('body_delta'))
    rng = h.get('good_bw_range')                  # (lo, hi) from 1-3着 runs
    if bw is None or d is None:
        return 0.0, 'UNKNOWN'
    if not rng:
        return 0.0, 'HOLD'                        # レンジ未取得: 保留 (21-4)
    lo, hi = rng
    if lo - 10 <= bw <= hi + 10:
        return 0.0, 'IN_RANGE'
    bad = sum(1 for k in ('state_bad', 'comment_weak', 'consecutive_loss') if h.get(k))
    return (-3.0, 'OUT_BAD') if bad >= 2 else (0.0, 'OUT_UNCONFIRMED')


def adf(h, race):
    c = sum([(_f(h.get('age')) or 0) >= 8, (_f(h.get('load')) or 0) >= 690, race.get('pace') == 'H',
             (_f(h.get('body_delta')) or 0) < 0, bool(h.get('front_type')), moisture_band(race.get('moisture')) == 'DRY',
             bool(h.get('fades_after_barrier'))])
    return (-MID(4, 8), c) if c >= 3 else (0.0, c)


def dcr(h, idx, bta_ev):
    pts = [any(v is not None for v in idx.values()), bta_ev != 'UNCONFIRMED',
           bool(h.get('kintaro_past')), h.get('mpa') is not None, h.get('brs') is not None,
           bool(h.get('good_bw_range')), h.get('cci') is not None, h.get('body_weight') is not None,
           h.get('odds') is not None, h.get('moisture_known', True)]
    return round(100 * sum(1 for p in pts if p) / len(pts))


# ---------------------------------------------------------------- main
def evaluate(race):
    """race = {'moisture', 'special', 'young'(2歳), 'pace'('H'|'M'|'S'|None), 'horses':[...]}.
    Each horse: no, name, age, load, body_weight, body_delta, odds, pop, jockey_barrier(bool),
    cci ('VERY_STRONG'|'STRONG'|'NEUTRAL'|'CAUTION'|None), front_ok, promoted, kintaro_past=[...],
    sbo_past=[...], own_past=[...], good_bw_range, barrier_stable, body_stable.
    Returns a ledger dict (rows per horse + race-level marks / F3S / S3H / AKI / ASI)."""
    H = [h for h in race['horses'] if not h.get('scratched')]
    rows = []
    for h in H:
        idx, prov = base_indices(h, race.get('moisture'))
        b = bsi(idx)
        d, isv_lab = isv(idx)
        kp = h.get('kintaro_past') or []
        bta_adj, bta_ev, bta_mean = bta(kp)
        h = dict(h, mpa=mpa(kp), brs=brs(kp))
        wda, front_bonus, wsrc = weight_terms(h, H, race.get('special'), h.get('front_ok'))
        jbr = MID(2, 3) if h.get('jockey_barrier') else 0.0
        adf_adj, adf_n = adf(h, race)
        bwl_adj, bwl_lab = bwl(h)
        cci = {'VERY_STRONG': 3.0, 'STRONG': 1.5, 'NEUTRAL': 0.0, 'CAUTION': -1.5}.get(h.get('cci'), 0.0)
        cpu = -1.5 if h.get('promoted') and not h.get('win_streak') else 0.0
        lis = (2.0 if d is not None and d <= 1 else 1.0 if d is not None and d <= 3 else 0.0)
        tpi = None if b is None else round(b + (bta_adj or 0) + (h['mpa'] or 0) + (h['brs'] or 0) + wda
                                           + front_bonus + jbr + adf_adj + bwl_adj + cci + cpu, 2)
        rows.append({'no': h['no'], 'name': h.get('name'), 'pop': h.get('pop'), 'odds': h.get('odds'),
                     'idx': idx, 'idx_src': prov, 'bsi': b, 'isv': d, 'isv_label': isv_lab, 'lis': lis,
                     'bta': bta_adj, 'bta_evidence': bta_ev, 'barrier_mean_sec': bta_mean,
                     'mpa': h['mpa'], 'brs': h['brs'], 'wda': wda, 'front_bonus': front_bonus,
                     'weight_source': wsrc, 'jbr': jbr, 'adf': adf_adj, 'adf_hits': adf_n,
                     'bwl': bwl_adj, 'bwl_label': bwl_lab, 'cci': cci, 'cpu': cpu, 'tpi': tpi,
                     'dcr': dcr(h, idx, bta_ev), 'age': h.get('age'), 'load': h.get('load')})
    _rank(rows, race)
    return {'ruleset': RULESET, 'moisture_band': moisture_band(race.get('moisture')), 'rows': rows,
            **_race_level(rows, race), 'probability_status': 'NOT-PROBABILITY / NOT-EV'}


def _neutral(rows, key):
    vals = [r[key] for r in rows if r[key] is not None]
    return mean(vals) if vals else 0.0


def _rank(rows, race):
    nt = _neutral(rows, 'tpi')
    for r in rows:
        t = r['tpi'] if r['tpi'] is not None else nt            # unknown -> neutral, flagged
        r['tpi_eff'] = t
        r['win_score'] = round(t + (r['brs'] or 0) * 0.5 + (r['bta'] or 0) * 0.5 - (2.0 if r['bta_evidence'] == 'UNCONFIRMED' else 0), 2)
        stab = {'VERY_STABLE': 4, 'STABLE': 2, 'STANDARD': 0, 'UNSTABLE': -2, 'UNKNOWN': 0}[r['isv_label']]
        r['place_score'] = round(t + stab + r['lis'] + (2 if r['bta_evidence'] == 'STABLE' else 0), 2)
        longshot = (r['pop'] or 0) >= 7
        r['hole_score'] = round(r['place_score'] + (3 if longshot else 0) + r['lis'], 2)
    for key, name in (('win_score', 'win_rank'), ('place_score', 'place_rank'), ('hole_score', 'hole_rank')):
        for i, r in enumerate(sorted(rows, key=lambda x: -x[key])):
            r[name] = i + 1
    n = len(rows)
    for r in rows:
        # roles (spec 3-3). Hard EXCL only with explicit evidence flag, never from rank alone.
        r['role_w'] = ('STRONG' if r['win_rank'] <= 2 else 'CONDITIONAL' if r['win_rank'] <= 4
                       else 'RESIDUAL' if r['place_rank'] <= 3 else None)
        r['role_p2'] = 'BUY' if r['place_rank'] <= 4 else 'MONITOR' if r['place_rank'] <= 6 else None
        r['role_p3'] = 'BUY' if r['place_rank'] <= min(6, n) else 'MONITOR' if r['hole_rank'] <= 6 else None
        # 強制降格 (5-2): 3項目以上で本命禁止
        r['no_honmei'] = r['adf_hits'] >= 3 or (r['bta_evidence'] == 'UNCONFIRMED' and race.get('young'))


def _race_level(rows, race):
    by_win = sorted(rows, key=lambda r: r['win_rank'])
    by_place = sorted(rows, key=lambda r: r['place_rank'])
    honmei = next((r for r in by_win if not r['no_honmei']), by_win[0])
    marks = {honmei['no']: '◎'}
    for r in by_win:
        if r['no'] not in marks and len(marks) < 2:
            marks[r['no']] = '○'
    for r in by_place:
        if r['no'] not in marks and len([m for m in marks.values() if m == '▲']) < 1:
            marks[r['no']] = '▲'
    f3s = [honmei['no']]
    for r in by_place:
        if r['no'] not in f3s and len(f3s) < 3:
            f3s.append(r['no'])
    s3h = [r['no'] for r in sorted(rows, key=lambda r: r['hole_rank'])
           if (r['pop'] or 0) >= 6 and r['no'] not in f3s][:3]
    for n_ in s3h:
        marks.setdefault(n_, '穴')
    for r in by_place:
        if r['no'] not in marks and r['role_p3'] == 'BUY':
            marks[r['no']] = '△'
    # AKI (13節): 加点要素の数から 0-100 の目安。確率ではない。
    t = sorted([r['tpi_eff'] for r in rows], reverse=True)
    close = 1 if len(t) >= 3 and t[0] - t[2] <= 4 else 0
    pops = sorted([r['odds'] for r in rows if r['odds']])
    split = 1 if len(pops) >= 2 and pops[0] >= 2.5 else 0
    unsure = sum(1 for r in rows if r['bta_evidence'] in ('UNCONFIRMED', 'PROVISIONAL')) >= len(rows) / 2
    old = sum(1 for r in rows if (r['age'] or 0) >= 8) >= 3
    big_w = sum(1 for r in rows if r['wda']) >= 2
    aki = min(100, 30 + 12 * close + 12 * split + 10 * unsure + 6 * old + 8 * big_w + (10 if race.get('young') else 0))
    # ASI (v2.3 第39条) for ◎: separation of place_score to the 4th horse, minus data gaps
    ps = sorted([r['place_score'] for r in rows], reverse=True)
    gap = (honmei['place_score'] - ps[3]) if len(ps) >= 4 else 10
    asi = max(0, min(100, round(55 + 4 * gap + (honmei['dcr'] - 70) * 0.3 - (10 if honmei['no_honmei'] else 0))))
    return {'marks': marks, 'f3s': f3s, 's3h': s3h, 'aki': aki, 'asi': asi, 'honmei': honmei['no']}

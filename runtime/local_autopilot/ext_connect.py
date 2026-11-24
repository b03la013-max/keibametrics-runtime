"""External-information connection for the LOCAL formal prediction (Owner orders 2026-11-21 13:09
「水分ボンバーオンラインもNARの資料もGoogleドライブの精読も接続しなさい」 and 13:32「１２３全て始めなさい／
…全てを指数に接続させ常に改善させなさい」).

Two outlets, both from the formal race card at SOURCE time, before cutoff:
 1. Full29: measured NAR / 競馬ブック evidence fills the components that were canonical-neutral for lack of a
    source (ext_model.full29_evidence -> local_nar_evidence_candidate external_evidence): BVIg-L (7 parts),
    JTI-L stable_combo, CSI-L stable/comment/training, BWI-L weight-change/age/season, DCR training coverage,
    NCI class_relative_time (own NAR speed figure). The 29 values, the numerical ranking and the KRS input move.
 2. Ranking layer: overall' = (1 - EXT_SHARE) overall + EXT_SHARE EXT,
      EXT = 52 + sum_fixed W_k (s_k - 52) + sum_measured beta_k (s_k - 52)
    fixed (no history to measure): VMI 水分ボンバー 4 columns, TMI / KBA / PACE 競馬ブック; measured: SPD (own NAR speed
    figure, half weight when 水分ボンバー is present), JKY, FRM, HRS, PAT (every pattern label: Drive reading, class move,
    day trend, weather, 危険な1番人気, 亀谷, YouTube sire rules ...). beta is refit weekly on NAR (ext_model.fit_weights)
    and adopted only when the hold-out weeks improve ("常に改善").
Production 29 registry/mapping, KRS Engine, MEC, the 60-ticket cap and the purchase policy are unchanged.
Raw 水分ボンバー numbers, NAR tables and histories stay in the private cache on the runner (never in Git).
"""
from __future__ import annotations

import json
import os
import time
from datetime import date, datetime, timedelta
from pathlib import Path

from runtime.local_autopilot import ext_model as em

PROFILE = 'KM-LOCAL-EXT-CONNECTION-v2.1-20261121'
EXT_FROM = '2026-11-22'
EXT_SHARE = 0.30
NEUTRAL = 52.0
FIXED_W = {'VMI': 0.25, 'TMI': 0.06, 'KBA': 0.06, 'PACE': 0.03}
MEASURED = ['JKY', 'FRM', 'HRS', 'PAT', 'SPD', 'KM3', 'ITV', 'BWS', 'BWP', 'SHF', 'FRS']
# first fit 2026-11-21 (tables < 2026-08-09, fit 08-09..10-03, hold-out 10-04..10-31 log-loss 0.45268 market ->
# 0.44788); refit weekly by ensure(refit=True)
DEFAULT_BETA = {'JKY': 0.35, 'FRM': 0.3, 'HRS': 0.0, 'PAT': 0.3, 'SPD': 0.8,
                'KM3': 0.0,   # 亀谷 v3 (B4 2026-11-24): starts at 0, only the weekly hold-out refit can move it
                # B3 pattern labels (b3_labels, 2026-11-25): same rule, weight 0 until the hold-out refit adopts one
                'ITV': 0.0, 'BWS': 0.0, 'BWP': 0.0, 'SHF': 0.0, 'FRS': 0.0}
SPD_WITH_SBO = 0.5          # 水分ボンバー present: the own speed figure counts half (same past races, 条項 6.1)
FIT_NAMES = list(MEASURED)
REFIT_DAYS = 7
SBO_COLS = {'recent': 0.40, 'dist': 0.20, 'going': 0.15, 'avg': 0.25}
PACE_TARGET = {'逃げ': 82.0, '好位': 66.0, '中位': 52.0, '後方': 38.0}
W = dict(FIXED_W, **{k: DEFAULT_BETA[k] for k in MEASURED})    # kept for reporting


def private_dir():
    return Path(os.environ.get('KM_PRIVATE_CACHE') or (Path.home() / '.km_private_cache'))


def enabled(race_date):
    return str(race_date) >= EXT_FROM and os.environ.get('KM_EXT_CONNECTION', '1') != '0'


# ---------------------------------------------------------------- tables / weights (once per race day)
def _paths(day):
    d = private_dir() / 'ext'
    return d / f'tables_v{em.TABLE_VERSION}_{day}.json', d / f'history_v{em.TABLE_VERSION}_{day}.json', d / 'weights.json'


def weights():
    try:
        w = json.loads(_paths('x')[2].read_text())
        return dict(DEFAULT_BETA, **w['current'])
    except (OSError, ValueError, KeyError):
        return dict(DEFAULT_BETA)


def ensure(root, day, refit=True):
    """Build the NAR + backfill tables for `day` (data strictly before it) and, weekly, refit beta."""
    from runtime.local_autopilot import hist_stats as hs
    tp, hp, wp = _paths(day)
    if tp.exists() and hp.exists() and not refit:
        return tp
    races = None
    if not (tp.exists() and hp.exists()):
        t0 = time.time()
        races, src = hs.load_sources(root, os.environ.get('KM_NAR_ROOT'))
        if not races:
            return None
        t, hist = em.build(races, day)
        t.update(source=src, build_seconds=round(time.time() - t0, 1))
        tp.parent.mkdir(parents=True, exist_ok=True)
        hp.write_text(json.dumps(hist, ensure_ascii=False, separators=(',', ':')))
        tp.write_text(json.dumps(t, ensure_ascii=False, separators=(',', ':')))
        for old in tp.parent.glob('*_20*.json'):          # keep the last 3 days
            if old.stem.split('_')[-1] < (date.fromisoformat(day) - timedelta(days=3)).isoformat():
                old.unlink()
    if refit:
        try:
            wdoc = json.loads(wp.read_text())
        except (OSError, ValueError):
            wdoc = {'current': dict(DEFAULT_BETA), 'history': []}
        last = (wdoc.get('history') or [{}])[-1].get('day') if wdoc.get('history') else None
        if not last or (date.fromisoformat(day) - date.fromisoformat(last)).days >= REFIT_DAYS:
            if races is None:
                races, _ = hs.load_sources(root, os.environ.get('KM_NAR_ROOT'))
            r = em.fit_weights(races, day, FIT_NAMES, dict(DEFAULT_BETA, **wdoc['current']))
            r['day'] = day
            wdoc['current'] = {k: round(v, 4) for k, v in r['weights'].items()}
            wdoc['history'] = (wdoc.get('history') or [])[-50:] + [{k: v for k, v in r.items() if k != 'weights'}]
            wp.parent.mkdir(parents=True, exist_ok=True)
            wp.write_text(json.dumps(wdoc, ensure_ascii=False, indent=1))
            try:   # public summary (weights and hold-out log-loss only) for the Owner / review
                (Path(root) / 'ext_weights.json').write_text(json.dumps(wdoc, ensure_ascii=False, indent=1) + '\n')
            except OSError:
                pass
    return tp


_LOADED = {}


def load(day):
    if day in _LOADED:
        return _LOADED[day]
    tp, hp, _ = _paths(day)
    if not (tp.exists() and hp.exists()):
        return None
    t = json.loads(tp.read_text())
    cells = {tuple(json.loads(k)): v for k, v in t.pop('cells').items()}
    t.pop('standards', None)
    _LOADED.clear()
    _LOADED[day] = (t, cells, json.loads(hp.read_text()))
    return _LOADED[day]


# ---------------------------------------------------------------- current race
def card_history(r, race_day):
    out = []
    for s in r.get('starts') or []:
        try:
            y, m_, d = s['date'].split('.')
            dt = date(2000 + int(y), int(m_), int(d)).isoformat()
        except (KeyError, ValueError, AttributeError):
            continue
        v = next((c for n, c in em.VENUE_NAME.items() if n in str(s.get('venue') or '')), None)
        if not v or dt >= race_day:
            continue
        pos = s.get('content_positions') or []
        fs = s.get('field_size')
        out.append({'date': dt, 'venue': v, 'distance': s.get('distance'), 'finish': s.get('finish'),
                    'early': (pos[0] - 1) / (fs - 1) if pos and fs and fs > 1 else None,
                    'late': (pos[-1] - 1) / (fs - 1) if pos and fs and fs > 1 else None,
                    'cls': em.class_code(s.get('race_name')), 'jockey': s.get('ride_jockey'),
                    'field': fs, 'pos': pos[0] if pos else None, 'bw': s.get('ride_body_weight')})
    return sorted(out, key=lambda x: x['date'])


def merged_history(nar_hist, card_hist):
    by = {(h['date'], h['venue']): dict(h) for h in nar_hist}
    for h in card_hist:
        k = (h['date'], h['venue'])
        if k in by:
            by[k].update({a: b for a, b in h.items() if b is not None})
        else:
            by[k] = dict(h, fig=None, f3best=None)
    return sorted(by.values(), key=lambda x: x['date'])


def sbo_vmi(table, active):
    comp = {}
    for no in active:
        row = (table or {}).get(no) or (table or {}).get(str(no))
        if not row:
            continue
        parts = [(row.get(c), w) for c, w in SBO_COLS.items() if isinstance(row.get(c), (int, float))]
        if parts:
            comp[no] = sum(v * w for v, w in parts) / sum(w for _, w in parts)
    if len(comp) < 2:
        return {}, {}
    mu = sum(comp.values()) / len(comp)
    return {no: max(0.0, min(100.0, NEUTRAL + 2.0 * (v - mu))) for no, v in comp.items()}, comp


def day_bias(day_dir, venue_id, at):
    try:
        from runtime.local_autopilot import day_trend
        t = day_trend.build(day_dir, venue_id, at)
        if t.get('n', 0) >= 3 and t.get('winner_front_share') is not None:
            s = t['winner_front_share']
            return 'FRONT' if s >= 0.6 else 'BACK' if s <= 0.15 else 'NEUTRAL'
    except Exception:
        pass
    return None


def race_ext(race, runners, day, sbo_table=None, kb=None, daybias=None, weather=None, beta=None):
    """race: venue_id, distance, going, race_name; runners: parsed card rows. -> (per runner, status)."""
    loaded = load(day)
    t, cells, hist = loaded if loaded else (None, {}, {})
    beta = beta or weights()
    active = [x['horse_no'] for x in runners]
    vmi, _ = sbo_vmi(sbo_table, active)
    kb = kb or {}
    v, d = race['venue_id'], race.get('distance')
    from runtime.local_autopilot import hist_stats as hs
    field = len(runners)
    odds_rank = {x['horse_no']: i + 1 for i, x in enumerate(sorted((x for x in runners if x.get('win_odds')), key=lambda x: x['win_odds']))}
    rows = {}
    for x in runners:
        hk = em.key(x.get('name'))
        hh = merged_history(hist.get(hk) or [], card_history(x, day))
        pop = x.get('popularity') or odds_rank.get(x['horse_no'])
        cur = {'date': day, 'venue': v, 'distance': d, 'going': race.get('going'), 'age': x.get('age'),
               'sex': (x.get('sex_age') or '')[:1] or None, 'pop': pop, 'frame_no': x.get('frame_no'),
               'jockey': x.get('current_jockey'), 'cls': hs.class_code(race.get('race_name')), 'weather': weather,
               'bw': x.get('current_body_weight'),
               'special': hs.special_flag(v, race.get('race_name')), 'daybias': daybias,
               'sire': x.get('sire'), 'damsire': x.get('damsire')}
        rows[x['horse_no']] = {'venue': v, 'band': em.dist_band(d), 'going': em.going_class(race.get('going')),
                               'distance': d, 'fband': em.field_band(field), 'sire': em.key(x.get('sire')),
                               'damsire': em.key(x.get('damsire')), 'jockey': em.key(x.get('current_jockey')),
                               'trainer': em.key(x.get('trainer')), 'frame': em.frame_band(x.get('frame_no')), 'horse': hk,
                               'sex': cur['sex'], 'age': x.get('age'), 'bwchg': em.chg_band(x.get('current_body_weight_change')),
                               'season': em.season(day), 'spd': em.spd_of(hh), 'labels': em.labels(cur, hh),
                               'cand_labels': em.cand_labels(cur, hh),
                               'pop': pop or 99, 'style': em.style(hh), 'early_now': None}
    sp = [r['spd'] for r in rows.values() if r['spd'] is not None]
    mu = sum(sp) / len(sp) if len(sp) >= 2 else None
    out = {}
    for no, r in rows.items():
        r['spd_band'] = em.spd_band(None if mu is None or r['spd'] is None else r['spd'] - mu)
        comp = em.components(cells, r) if cells else {}
        kbx = kb.get(no) or kb.get(str(no)) or {}
        fixed = {}
        if no in vmi:
            fixed['VMI'] = (vmi[no], '水分ボンバー')
        if kbx.get('tm') is not None:
            fixed['TMI'] = (float(kbx['tm']), '競馬ブック TM印')
        ab = [y for y in (kbx.get('rt'), kbx.get('cpu')) if y is not None]
        if ab:
            fixed['KBA'] = (sum(ab) / len(ab), '競馬ブック 能力表')
        if kbx.get('pace') in PACE_TARGET:
            fixed['PACE'] = (PACE_TARGET[kbx['pace']], '競馬ブック 展開')
        ext = NEUTRAL + sum(FIXED_W[k] * (s - NEUTRAL) for k, (s, _) in fixed.items()) \
            + sum(beta.get(k, 0.0) * (SPD_WITH_SBO if k == 'SPD' and 'VMI' in fixed else 1.0) * (comp[k][0] - NEUTRAL)
                  for k in MEASURED if k in comp)
        evidence = em.full29_evidence(comp, kbx, comp['SPD'][0] if 'SPD' in comp and r['spd'] is not None else None)
        out[no] = {'EXT': round(max(0.0, min(100.0, ext)), 2),
                   'ranking_components': {k: round(s, 1) for k, (s, _) in fixed.items()}
                   | {k: round(comp[k][0], 1) for k in MEASURED if k in comp},
                   'labels': [f'{a}={b}' for a, b in r['labels']],
                   'cand_labels': [f'{a}={b}' for a, b in r.get('cand_labels') or []],
                   'pattern_detail': comp.get('PAT', (None, []))[1],
                   'full29_evidence': evidence}
    status = {'tables': bool(cells), 'tables_period': (t or {}).get('period'), 'tables_starts': (t or {}).get('starts'),
              'sbo_horses': len(vmi), 'kb_horses': sum(1 for x in runners if kb.get(x['horse_no']) or kb.get(str(x['horse_no']))),
              'spd_horses': sum(1 for r in rows.values() if r['spd'] is not None), 'daybias': daybias, 'weather': weather,
              'beta': beta, 'full29_slots': sum(len(o['full29_evidence']) for o in out.values())}
    return out, status


def apply(ranking_scores, ext):
    rows = []
    for r in ranking_scores:
        no = int(r['runner_id'])
        e = (ext.get(no) or {}).get('EXT', NEUTRAL)
        rows.append({'runner_id': str(no), 'overall_base': round(r['overall'], 3), 'EXT': e,
                     'overall_connected': round((1 - EXT_SHARE) * r['overall'] + EXT_SHARE * e, 3)})
    ranking = [x['runner_id'] for x in sorted(rows, key=lambda x: (-x['overall_connected'], int(x['runner_id'])))]
    return ranking, rows


# ---------------------------------------------------------------- formal hook
def sbo_cache_path(race_date, venue_id, race_no):
    return private_dir() / 'sbo' / race_date / f'{venue_id}_{int(race_no):02d}.json'


def save_sbo(race_date, venue_id, race_no, snap, fetched_at):
    """PAPER-side fetch -> private cache (the raw 水分ボンバー numbers never enter Git)."""
    if not snap or snap.get('status') != 'OK':
        return
    p = sbo_cache_path(race_date, venue_id, race_no)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({'fetched_at': fetched_at, 'sha256': snap.get('sha256'),
                             'table': {str(k): v for k, v in snap['table'].items()}}, ensure_ascii=False))


def sbo_for(r, deadline, fetch=None):
    """Cached snapshot fetched before the cutoff, else one fresh fetch (same access policy as the PAPER side)."""
    from datetime import datetime
    p = sbo_cache_path(r['race_date'], r['venue_id'], r['race_no'])
    try:
        c = json.loads(p.read_text())
        if datetime.fromisoformat(c['fetched_at']) < deadline:
            return {int(k): v for k, v in c['table'].items()}, {'status': 'USED_CACHE', 'fetched_at': c['fetched_at'], 'sha256': c['sha256']}
    except (OSError, ValueError, KeyError):
        pass
    if fetch is None:
        return None, {'status': 'NOT_FETCHED'}
    try:
        snap, at = fetch()
        if snap.get('status') != 'OK':
            return None, {'status': snap.get('status')}
        if datetime.fromisoformat(at) >= deadline:
            return None, {'status': 'FETCHED_AFTER_CUTOFF'}
        save_sbo(r['race_date'], r['venue_id'], r['race_no'], snap, at)
        return snap['table'], {'status': 'USED_FRESH', 'fetched_at': at, 'sha256': snap.get('sha256')}
    except Exception as exc:
        return None, {'status': 'UNAVAILABLE', 'error': f'{type(exc).__name__}:{str(exc)[:120]}'}


def kb_for(day_dir, r, deadline):
    from datetime import datetime
    p = Path(day_dir) / 'external' / 'keibabook_bands.json'
    try:
        doc = json.loads(p.read_text())
    except (OSError, ValueError):
        return None, {'status': 'NOT_CAPTURED'}
    cap = datetime.fromisoformat(str(doc.get('captured_at')).replace('Z', '+00:00'))
    if cap >= deadline:
        return None, {'status': 'CAPTURED_AFTER_CUTOFF', 'captured_at': doc.get('captured_at')}
    race = next((x for x in doc.get('races', []) if x.get('venue') == r['venue_name'] and x.get('race_no') == r['race_no']), None)
    if not race:
        return None, {'status': 'NOT_PROVIDED', 'captured_at': doc.get('captured_at')}
    kb = {int(k): v for k, v in (race.get('horses') or {}).items() if v}
    return kb, {'status': 'USED' if kb else 'NOT_PROVIDED', 'captured_at': doc.get('captured_at'), 'horses': len(kb)}


def weather_now(venue_id, at):
    try:
        from runtime.local_autopilot import weather
        w = weather.observe(venue_id, at, Path(os.environ.get('RUNNER_TEMP') or '/tmp') / 'km_weather_cache')
        p = (w.get('observation') or {}).get('precipitation_1h_mm')
        return None if p is None else ('雨' if p >= 0.5 else '晴')
    except Exception:
        return None


def prepare(r, head, active, day_dir, deadline, sbo_fetch=None, now=None):
    """Before Full29: compute every external value and attach Full29 evidence to the card rows (in place)."""
    day = r['race_date']
    now = now or datetime.now(deadline.tzinfo)
    sbo_t, sbo_m = sbo_for(r, deadline, sbo_fetch)
    kb, kb_m = kb_for(day_dir, r, deadline)
    db = day_bias(day_dir, r['venue_id'], min(now, deadline))
    wx = weather_now(r['venue_id'], min(now, deadline))
    race = {'venue_id': r['venue_id'], 'distance': head.get('distance'), 'going': head.get('going'),
            'race_name': head.get('race_name')}
    ext, st = race_ext(race, active, day, sbo_t, kb, db, wx)
    for x in active:
        ev = (ext.get(x['horse_no']) or {}).get('full29_evidence')
        if ev:
            x['external_evidence'] = ev
    return {'ext': ext, 'status': st, 'sbo': sbo_m, 'keibabook': kb_m}


def connect(pre, num_pred):
    """-> connection record with the connected ranking. Never changes num_pred."""
    ranking, rows = apply(num_pred['runner_scores'], pre['ext'])
    return {'profile': PROFILE, 'owner_order': '2026-11-21 13:09 / 13:32 JST 全てを指数に接続し常に改善',
            'ext_share': EXT_SHARE, 'fixed_weights': FIXED_W, 'beta': pre['status']['beta'], 'sbo_columns': SBO_COLS,
            'status': pre['status'], 'sbo': pre['sbo'], 'keibabook': pre['keibabook'],
            'ranking_base': list(num_pred['ranking']), 'ranking': ranking, 'rows': rows,
            'runners': {str(k): v for k, v in pre['ext'].items()},
            'changed_top3': list(num_pred['ranking'][:3]) != ranking[:3],
            'changed_top6': sorted(num_pred['ranking'][:6]) != sorted(ranking[:6])}


# ---------------------------------------------------------------- C26 comparison (connected vs base, same races)
def audit(root, days):
    """Effective formal revision per race: connected ranking vs the base ranking it replaced."""
    rows = []
    for day in sorted(days):
        dd = Path(root) / day
        for s1 in sorted((dd / 'formal').glob('*.summary.json')):
            k = s1.name.split('.')[0]
            s2 = dd / 'formal' / 'rev2' / s1.name
            try:
                sm = json.loads((s2 if s2.exists() else s1).read_text())
                res = json.loads(((dd / 'formal' / 'rev2' / f'{k}.result.json') if (dd / 'formal' / 'rev2' / f'{k}.result.json').exists()
                                  else (dd / 'formal' / f'{k}.result.json')).read_text())
            except (OSError, ValueError):
                continue
            if sm.get('status') != 'SIGNED_FINAL' or not sm.get('ranking_base') or not (sm.get('ext_connection') or {}).get('profile'):
                continue
            order = [str(x) for x in (res.get('order') or [])[:3]]
            if len(order) < 3:
                continue
            rows.append({'day': day, 'race': k, 'venue': k.split('_')[0], 'order': order,
                         'base': [str(x) for x in (sm.get('ranking_no_external') or sm['ranking_base'])],
                         'conn': [str(x) for x in sm['ranking']]})

    def m(rs, col):
        n = len(rs)
        if not n:
            return {'races': 0}
        win3 = sum(r['order'][0] in r[col][:3] for r in rs)
        sec6 = sum(r['order'][1] in r[col][:6] for r in rs)
        all9 = sum(all(x in r[col][:9] for x in r['order']) for r in rs)
        rk = [r[col].index(r['order'][0]) + 1 for r in rs if r['order'][0] in r[col]]
        return {'races': n, 'winner_in_W3': win3, 'winner_in_W3_rate': round(100 * win3 / n, 1),
                'second_in_P2_6': sec6, 'top3_in_P3_9': all9, 'winner_mean_rank': round(sum(rk) / len(rk), 2) if rk else None}
    by = {}
    for v in sorted({r['venue'] for r in rows}):
        rs = [r for r in rows if r['venue'] == v]
        by[v] = {'base': m(rs, 'base'), 'connected': m(rs, 'conn')}
    return {'races': len(rows), 'base': m(rows, 'base'), 'connected': m(rows, 'conn'), 'by_venue': by,
            'changed_W3': sum(sorted(r['base'][:3]) != sorted(r['conn'][:3]) for r in rows),
            'gained': [r['race'] for r in rows if r['order'][0] in r['conn'][:3] and r['order'][0] not in r['base'][:3]],
            'lost': [r['race'] for r in rows if r['order'][0] in r['base'][:3] and r['order'][0] not in r['conn'][:3]]}


def main():
    """python -m runtime.local_autopilot.ext_connect --refit [--day D]: weekly beta refit (night, no race work due)."""
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--refit', action='store_true')
    ap.add_argument('--day')
    a = ap.parse_args()
    from runtime.local_autopilot.run import ROOT
    day = a.day or (datetime.now().astimezone() + timedelta(hours=0)).date().isoformat()
    p = ensure(ROOT, day, refit=a.refit)
    try:
        h = json.loads(_paths(day)[2].read_text())['history'][-1]
    except (OSError, ValueError, KeyError, IndexError):
        h = None
    print('EXT_ENSURE', day, bool(p), json.dumps(h, ensure_ascii=False)[:400] if h else '')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

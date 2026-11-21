"""影の候補式（Shadow challengers）— Owner 2026-11-21 20:24 承認「仮説→比較→未知のレースで検証→採用」。

本番の予想（BASE）と同じ入力・同じ時刻で、事前登録した候補式でも予想して保存する（買わない・配信しない）。
結果確定後に review.py が、同じ物差しで BASE と比べる。採用は R30/R100 の節目で Owner が判断し、
試して落とした候補も消さずに残す（PREREG の status を REJECTED にするだけ）。
"""
import contextlib
import copy

import derive
import engine
import tickets

PREREG = {
    'registered_at': '2026-11-21T20:30+09:00',
    'baseline': 'BASE',
    'metrics': ['winner_win_rank', 'winner_top1', 'winner_top3', 'top3_in_place5', 'honmei_top3',
                'trio_hit', 'exact_hit', 'stake', 'return', 'pfs', 'pfs_ex_top1', 'by_moisture_band'],
    'decision': 'R30: 順位の物差し（勝ち馬の評価順位・捕捉率）で方向を見る。R100以上: 回収率も併せて Owner が採否。'
                '単日・少数での採用はしない。候補を増やすときは新しい登録日で追加し、既存の候補は書き換えない。',
    'candidates': {
        'BASE':     {'what': '本番（現行式）', 'status': 'PRODUCTION'},
        'SBO0':     {'what': '水分ボンバー比率 0%（自前指数のみ）', 'patch': {'SBO_SHARE': 0.0}, 'status': 'SHADOW'},
        'SBO60':    {'what': '水分ボンバー比率 60%', 'patch': {'SBO_SHARE': 0.6}, 'status': 'SHADOW'},
        'BSI_EQ':   {'what': 'BSI 3指数を等重み（1/3ずつ）', 'patch': {'BSI_W': {'recent': 1/3, 'track': 1/3, 'avg': 1/3}}, 'status': 'SHADOW'},
        'BSI_REC':  {'what': 'BSI 近走重視 0.50/0.30/0.20', 'patch': {'BSI_W': {'recent': 0.5, 'track': 0.3, 'avg': 0.2}}, 'status': 'SHADOW'},
        'NOPOS':    {'what': 'キンタロー丸数字（仮の読み方）を使わない＝MPA/BRSなし', 'nopos': True, 'status': 'SHADOW'},
        'CUTS_ALT': {'what': '仮の基準の別案（Hペース=逃げ3頭以上、障害巧者=上位15%）',
                     'cuts': {'pace_H_front_min': 3, 'jockey_top_share': 0.15}, 'status': 'SHADOW'},
        'MKT30':    {'what': '人気を順位に30%混ぜる', 'patch': {'MARKET_W': 0.3}, 'status': 'SHADOW'},
        'MKT50':    {'what': '人気を順位に50%混ぜる', 'patch': {'MARKET_W': 0.5}, 'status': 'SHADOW'},
    },
}


@contextlib.contextmanager
def _patched(mod, attrs):
    old = {k: getattr(mod, k) for k in attrs}
    try:
        for k, v in attrs.items():
            setattr(mod, k, v)
        yield
    finally:
        for k, v in old.items():
            setattr(mod, k, v)


def _summary(ev, tk):
    rows = ev['rows']
    return {'win_order': [r['no'] for r in sorted(rows, key=lambda r: r['win_rank'])],
            'place_order': [r['no'] for r in sorted(rows, key=lambda r: r['place_rank'])],
            'honmei': ev.get('honmei'), 'marks': ev.get('marks'),
            'trio': tk['trio'], 'exact': tk['exact'], 'points': tk['points'], 'shape': tk.get('shape')}


def run_all(race, rebuild):
    """race: the production race dict (horses already built). rebuild(cuts) -> horses rebuilt with other
    derive.CUTS (only for candidates that change a cut). Returns {candidate: summary}; never raises."""
    out = {}
    for cid, c in PREREG['candidates'].items():
        if c['status'] == 'REJECTED':
            continue
        try:
            rc = dict(race, horses=copy.deepcopy(race['horses']))
            if c.get('cuts'):
                with _patched(derive, {'CUTS': dict(derive.CUTS, **c['cuts'])}):
                    rc['horses'] = rebuild()
                    rc['pace'] = derive.race_pace(rc['horses'])
            mods = {}
            if c.get('nopos'):
                mods.update(mpa=lambda past: None, brs=lambda past: None)
            with _patched(engine, dict(c.get('patch') or {}, **mods)):
                ev = engine.evaluate(rc)
            out[cid] = _summary(ev, tickets.compile_race(ev))
        except Exception as e:                                   # a challenger never stops production
            out[cid] = {'error': f'{type(e).__name__}:{str(e)[:120]}'}
    return out

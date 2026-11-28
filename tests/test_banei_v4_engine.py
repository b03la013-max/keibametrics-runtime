import os
import sys
from itertools import product

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'runtime', 'banei_autopilot'))
import engine  # noqa: E402
import tickets  # noqa: E402
import render  # noqa: E402


def _race(n=10, young=False):
    horses = []
    for i in range(1, n + 1):
        base = 92 - i * 1.5
        horses.append({
            'no': i, 'name': f'H{i}', 'age': 4 + i % 6, 'load': 700 - (20 if i == 7 else 0),
            'body_weight': 1050, 'body_delta': (-16 if i == 3 else 4), 'odds': 1.8 + i * 1.7, 'pop': i,
            'cci': 'STRONG' if i in (2, 7) else 'NEUTRAL', 'front_ok': i in (1, 7),
            'barrier_stable': i in (1, 2, 7), 'body_stable': True, 'jockey_barrier': i == 4,
            'good_bw_range': (1030, 1060),
            'sbo_past': [{'idx': base + d, 'moisture': m} for d, m in ((1, 1.2), (-1, 2.2), (0, 1.3), (2, 1.1), (-2, 2.0))],
            'kintaro_past': [{'barrier_sec': 17 + i, 'pos_first': 5, 'pos_barrier': 4, 'pos_finish': 3}] * 3,
        })
    return {'moisture': 1.3, 'special': False, 'young': young, 'pace': 'M', 'horses': horses}


def test_indices_and_isv():
    idx, prov = engine.base_indices(_race()['horses'][0], 1.3)
    assert idx['recent'] == 91.5 and prov['recent'] == 'SBO'
    assert idx['track'] is not None and idx['avg'] is not None
    d, lab = engine.isv(idx)
    assert lab in ('VERY_STABLE', 'STABLE')


def test_bta_bands_and_evidence():
    assert engine.bta([{'barrier_sec': 16}] * 3)[:2] == (6.0, 'STABLE')
    assert engine.bta([{'barrier_sec': 36}])[:2] == (-6.0, 'PROVISIONAL')    # 1回 != Stable
    assert engine.bta([])[1] == 'UNCONFIRMED'


def test_weight_bonus_not_double_counted():
    r = _race()
    h = dict(r['horses'][6], mpa=None, brs=None)
    wda, front, src = engine.weight_terms(h, r['horses'], special=True, front_ok=True)
    assert wda == 6.5 and front == 3.0              # 20kg軽: mid(5,8); 軽量+先行 once (mid 2-4)


def test_missing_is_neutral_not_zero():
    r = _race()
    r['horses'][4]['sbo_past'] = []
    ev = engine.evaluate(r)
    row = [x for x in ev['rows'] if x['no'] == 5][0]
    assert row['tpi'] is None and row['tpi_eff'] > 0


def test_compile_cap_closure_and_render():
    ev = engine.evaluate(_race())
    tk = tickets.compile_race(ev)
    assert tk['points'] <= 30
    assert all(tuple(sorted(e)) in tk['trio'] for e in tk['exact'])       # Exact -> Trio closure
    assert all(v.startswith('HEAD-') for v in tk['terminal'].values())   # no silent W zero
    assert all(tk['hole_link'].values()) and tk['gates']['G-HOLE'] == 'PASS'   # BAN-HAC
    text, total = render.render('帯広 1R', ev, tk)
    assert total == tk['points'] and '①' not in text and '三連複' in text


def test_two_axis_keeps_o_lines_without_honmei():
    ev = engine.evaluate(_race())
    ev = dict(ev, asi=55, aki=70)                     # force UPSET-GUARD (2-3-7)
    tk = tickets.compile_race(ev)
    o = tk['axis'][1]
    assert any(o in t and ev['honmei'] not in t for t in tk['trio'])


def test_low_confidence_no_exact():
    ev = dict(engine.evaluate(_race(young=True)), asi=40)
    tk = tickets.compile_race(ev)
    assert tk['exact'] == [] and tk['points'] <= 30


def test_exposure_trace_counts_roles():
    from runtime.banei_autopilot import tickets as T
    ex = T._exposure([(1, 2, 3), (1, 2, 4)], [(1, 2, 3), (2, 1, 3)])
    assert ex['1'] == {'head': 1, 'p2': 1, 'p3': 0, 'trio': 2}
    assert ex['3'] == {'head': 0, 'p2': 0, 'p3': 2, 'trio': 1}
    assert ex['4']['trio'] == 1


def test_exact_rule_by_w_follows_ban_tag():
    import tickets as T
    ev = engine.evaluate(_race())
    W = [r['no'] for r in ev['rows'] if r['role_w'] in ('STRONG', 'CONDITIONAL')]
    old = T.EXACT_RULE
    try:
        T.EXACT_RULE = 'BY_W'
        tk = T.compile_race(ev)
        heads = {e[0] for e in tk['exact']}
        if len(W) >= 3:
            assert tk['exact'] == []
        elif len(W) == 2:
            assert len(heads) <= 2
        T.EXACT_RULE = '2HEAD'
        tk2 = T.compile_race(ev)
        assert len({e[0] for e in tk2['exact']}) in (0, 2) and tk2['points'] <= 30
    finally:
        T.EXACT_RULE = old


def test_shadow_switches_default_off():
    import engine, tickets
    assert engine.MARKET_FREE is False and tickets.EXACT_PICK is None


def test_single_mode_shadow_keeps_cap_and_production_identity():
    import json, glob, tickets
    from pathlib import Path
    files = sorted(glob.glob('tests/fixtures/banei/*.json'))
    rows = {i: {'no': i, 'win_rank': i, 'place_rank': i, 'hole_rank': i, 'role_w': 'STRONG' if i <= 2 else None,
                'role_p2': 'BUY' if i <= 4 else None, 'role_p3': 'BUY' if i <= 6 else None} for i in range(1, 9)}
    import intel
    assert tickets.SINGLE_MODE is None
    tickets.SINGLE_MODE = 'B'
    try:
        tri, ex, exa, single = tickets._single_alloc({'honmei': 1}, rows, [[1, 2, 3], [1, 2, 4]], [])
    finally:
        tickets.SINGLE_MODE = None
    assert len(tri) + len(ex) + len(exa) <= tickets.CAP_TOTAL
    assert {e[0] for e in ex} == {1, 2} and {e[0] for e in exa} == {1, 2}        # ◎だけを1着に固定しない
    assert all(len(set(e)) == 3 for e in ex) and all(e[0] != e[1] for e in exa)
    assert sorted(ex[0]) in [sorted(t) for t in tri]                               # 三連単の組は三連複で保護


def test_single_mode_is_owner_gated():
    import registry
    assert registry.owner_gated({'tpatch': {'SINGLE_MODE': 'A'}}) and not registry.owner_gated({'tpatch': {'EXACT_PICK': 'UNIVERSE'}})

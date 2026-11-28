"""TRIO_FILL（影の候補 EXACT_BY_W_FILL だけ）: 三連単を外した余りを役割の組の三連複で同じ上限30点まで埋める。本番は不変。"""
import json
import os
import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'runtime', 'banei_autopilot'))
import engine  # noqa: E402
import tickets  # noqa: E402
from test_banei_v4_engine import _race  # noqa: E402


def _ev():
    return engine.evaluate(_race())


def test_production_default_off_and_unchanged():
    assert tickets.TRIO_FILL is None and tickets.EXACT_RULE is None
    ev = _ev()
    assert tickets.compile_race(ev) == tickets.compile_race(ev)


def test_fill_reaches_cap_or_exhausts_role_combos():
    ev = _ev()
    old = (tickets.EXACT_RULE, tickets.TRIO_FILL)
    try:
        tickets.EXACT_RULE = 'BY_W'
        plain = tickets.compile_race(ev)
        tickets.TRIO_FILL = True
        filled = tickets.compile_race(ev)
    finally:
        tickets.EXACT_RULE, tickets.TRIO_FILL = old
    assert filled['points'] <= tickets.CAP_TOTAL
    assert filled['points'] >= plain['points']
    assert {tuple(sorted(t)) for t in plain['trio']} <= {tuple(sorted(t)) for t in filled['trio']}
    assert filled['exact'] == plain['exact']
    rows = {r['no']: r for r in ev['rows']}
    roled = {n for n, r in rows.items() if r['role_w'] or r['role_p2'] or r['role_p3']} or set(rows)
    pool = {tuple(sorted(t)) for t in plain['trio']} | set(combinations(sorted(roled), 3))
    if filled['points'] < tickets.CAP_TOTAL:                       # 役割馬の組が尽きたときだけ30点未満
        assert {tuple(sorted(t)) for t in filled['trio']} == pool
    assert all(len(set(t)) == 3 for t in filled['trio'])
    assert filled['gates']['G-CAPITAL'] == 'PASS'


def test_queue_registers_exact_by_w_fill():
    q = json.loads((Path(tickets.__file__).with_name('candidates_queue.json')).read_text())
    c = q['candidates']['EXACT_BY_W_FILL']
    assert c['config'] == {'tpatch': {'EXACT_RULE': 'BY_W', 'TRIO_FILL': True}}
    assert 'EXACT_BY_W' in q['candidates']                         # 既存の候補は残す（書き換えない）

import json

from runtime.local_autopilot import rev_audit as ra


def _w(p, o):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(o, ensure_ascii=False))


def _receipt(odds):
    return {'artifact': {'active_runner_universe': {'runners': [{'horse_no': h, 'win_odds': o} for h, o in odds.items()]}}}


def test_rev2_audit_and_w_miss(tmp_path):
    d = tmp_path / '2026-11-20'
    _w(d / 'queue.json', {'races': {'SON_09': {}}})
    s1 = {'ranking': ['1', '2', '3'], 'roles': {'1': ['W'], '2': ['W', 'P2'], '3': ['P2']}, 'tickets': [{'bet_type': 'EXACTA', 'selection': [2, 1]}]}
    s2 = {'ranking': ['1', '3', '2'], 'roles': {'1': ['W'], '3': ['W', 'P2'], '2': ['P2']}, 'revision_reasons': ['ROLE_SET_CHANGE'],
          'tickets': [{'bet_type': 'EXACTA', 'selection': [3, 1]}]}
    _w(d / 'formal' / 'SON_09.summary.json', s1)
    _w(d / 'formal' / 'rev2' / 'SON_09.summary.json', s2)
    _w(d / 'formal' / 'rev2' / 'SON_09.result.json', {'order': [2, 1, 3], 'payouts': {'EXACTA': {'2-1': 900}}})
    _w(d / 'formal' / 'SON_09.source_receipt.json', _receipt({1: 3.0, 2: 8.0, 3: 5.0}))
    _w(d / 'formal' / 'rev2' / 'SON_09.source_receipt.json', _receipt({1: 3.2, 2: 5.0, 3: 6.0}))
    _w(d / 'formal' / 'SON_09.full29.json', {'runners': [{'no': '2', 'indices': {'PRI': 90.0}}]})
    _w(d / 'formal' / 'rev2' / 'SON_09.full29.json', {'runners': [{'no': '2', 'indices': {'PRI': 60.0}}, {'no': '1', 'indices': {'PRI': 70.0}}, {'no': '3', 'indices': {'PRI': 50.0}}]})
    out = ra.write_daily(d)
    r = out['races'][0]
    assert (r['winner_rank_r1'], r['winner_rank_r2'], r['winner_in_W_r1'], r['winner_in_W_r2']) == (2, 3, True, False)
    assert r['shortened'] == [2] and r['winner_indices_moved'] == {'PRI': [90.0, 60.0]}
    assert r['replay_payout_r1_r2'] == [900, 0]
    assert r['w_miss']['winner_market_rank'] == 2
    assert out['summary']['w_lost_by_rev2'] == 1
    assert (d / 'review' / 'revision_audit.md').read_text().startswith('# 修正版')

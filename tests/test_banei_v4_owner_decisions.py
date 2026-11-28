"""Owner の採否（registry.OWNER_DECISIONS）: 不採用の候補は記録を残したまま影の比較から外れる。"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'runtime', 'banei_autopilot'))
import registry  # noqa: E402


def test_owner_rejects_exact_by_w_once_and_keeps_record(tmp_path):
    reg = registry.load(tmp_path)
    reg['candidates']['EXACT_BY_W']['status'] = 'SHADOW'
    reg['candidates']['AXIS2_EXACT_BY_W']['status'] = 'SHADOW'
    registry.save(tmp_path, reg)
    r = registry.load(tmp_path)
    for cid in ('EXACT_BY_W', 'AXIS2_EXACT_BY_W'):
        assert r['candidates'][cid]['status'] == 'REJECTED' and r['candidates'][cid]['decision_reason']
        assert r['candidates'][cid]['config']                        # 記録は残す
    assert r['candidates']['EXACT_BY_W_FILL']['status'] == 'SHADOW'
    n = sum(1 for h in r['history'] if h['event'] == 'OWNER_REJECTED')
    registry.save(tmp_path, r)
    assert sum(1 for h in registry.load(tmp_path)['history'] if h['event'] == 'OWNER_REJECTED') == n   # 二重に記録しない


def test_rejected_not_run_as_shadow():
    import challengers
    out = challengers.run_all({}, lambda: [], {'X': {'status': 'REJECTED', 'config': {}}}, {})
    assert 'X' not in out

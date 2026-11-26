import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'runtime', 'banei_autopilot'))
import registry  # noqa: E402


def _write(root, day, n, better):
    d = root / day / 'review'
    d.mkdir(parents=True)
    for i in range(n):
        base = {'winner_win_rank': 3, 'top3_in_place5': 2, 'honmei_top3': False, 'trio_hit': False, 'exact_hit': False,
                'stake': 2800, 'return': 1000 if i % 3 == 0 else 0}
        cand = dict(base, winner_win_rank=1 if better else 3)
        (d / f'R{i:03d}.review.json').write_text(json.dumps({'shadow': {'BASE': base, better: cand} if better else {'BASE': base}}))


def test_step_promotes_clear_winner_and_registers_guard(tmp_path):
    _write(tmp_path, '2026-11-22', 120, 'MKT30')
    ev = registry.step(tmp_path)
    reg = registry.load(tmp_path)
    assert ('PROMOTED' in [e[0] for e in ev]) and reg['production']['id'] == 'MKT30'
    assert reg['production']['config'] == {'patch': {'MARKET_W': 0.3}} and 'PREV' in reg['candidates']
    assert '+MKT30@' in reg['production']['version'] and (tmp_path / 'improvement_status.md').exists()


def test_step_does_not_promote_below_min_races_and_adds_neighbors(tmp_path):
    _write(tmp_path, '2026-11-22', 40, 'MKT30')
    ev = registry.step(tmp_path)
    reg = registry.load(tmp_path)
    assert reg['production']['id'] == 'BASE' and 'PROMOTED' not in [e[0] for e in ev]
    # 自動の近傍候補は MAX_ACTIVE まで。毎晩の反省が積む候補（candidates_queue.json）はその上に乗る（多重比較の補正に含まれる）
    n_queue = len(json.loads(registry.QUEUE.read_text())['candidates'])
    assert sum(1 for v in reg['candidates'].values() if v['status'] == 'SHADOW') <= registry.MAX_ACTIVE + n_queue


def test_compare_needs_significance():
    revs = [{'day': '2026-11-22', 'shadow': {'BASE': {'winner_win_rank': 2, 'top3_in_place5': 2, 'stake': 100, 'return': 0},
                                             'X': {'winner_win_rank': 1 if i % 2 else 3, 'top3_in_place5': 2, 'stake': 100, 'return': 0}}}
            for i in range(200)]
    t = registry.compare(revs, 'X', '2026-11-21', 5)
    assert t['n'] == 200 and not t['promote']                   # same mean, noise only


def test_add_rejects_duplicate_config():
    reg = registry.load('/nonexistent-dir-for-test')
    assert not registry.add(reg, 'DUP', 'x', {'patch': {'MARKET_W': 0.3}}, 'test')
    assert registry.add(reg, 'NEW', 'x', {'patch': {'MARKET_W': 0.45}}, 'test')


def test_kcp_ablation_candidate_only_after_min_races():
    import copy as _c
    revs = [{'component_auc': {'wda': {'top3': 0.45, 'win': 0.5}, 'bta': {'top3': 0.7, 'win': 0.7}}}]
    assert registry.kcp_candidates(revs * (registry.KCP['min_races'] - 1), {}) == {}
    got = registry.kcp_candidates(revs * registry.KCP['min_races'], {})
    assert set(got) == {'KCP_ABLATE_wda'}
    cfg = got['KCP_ABLATE_wda'][1]['patch']['COMP_W']
    assert cfg['wda'] == 0.0 and all(v == 1.0 for k, v in cfg.items() if k != 'wda')


def test_comp_w_production_is_identity():
    import engine
    assert set(engine.COMP_W.values()) == {1.0}


def test_formula_ledger_covers_tpi_components_and_is_stable():
    import formula_ledger, engine
    a, b = formula_ledger.build(), formula_ledger.build()
    assert a['formula_sha'] == b['formula_sha'] and len(a['formula_sha']) == 64
    assert {'bsi', 'bta', 'mpa', 'brs', 'wda', 'jbr', 'adf', 'bwl', 'cci', 'cpu', 'tpi'} <= set(a['components'])
    assert a['constants']['engine.COMP_W'] == engine.COMP_W


def test_kiep_health_and_redundancy():
    import review
    rows = [{'no': i, 'tpi': 20 - i, 'bta': 20 - i, 'wda': (i % 2) * 1.0, 'pop': i} for i in range(1, 10)]
    h = review.component_health(rows, [1, 2, 3])
    assert h['tpi']['high'][0] == 3 and h['tpi']['low'][0] == 0
    c = review.component_corr(rows)
    assert c['bta~pop'] == 1.0                                     # 人気は小さいほど良いので向きをそろえる
    s = review.kiep_summary([{'component_health': h, 'component_corr': c, 'feeds_present': ['kintaro']}] * 5)
    assert s['components']['tpi']['monotonic'] is True and 'bta~pop' in s['redundant_pairs']
    assert s['feed_rate'] == {'kintaro': 1.0}

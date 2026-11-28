import json
from runtime.local_autopilot import auto_policy as ap


def _rows(n, good=True):
    rows = []
    for i in range(n):
        v = ['URA', 'FUN', 'OOI'][i % 3]
        b0 = (6000, 3000)
        b2 = (3000, 2500) if good else (3000, 500)
        rows.append({'day': '2026-12-%02d' % (1 + i % 28), 'key': f'{v}_{i:02d}', 'phase': 'forward',
                     'B0_DELIVERED': b0, 'B2_GAP_HALF': b2, 'B4_ANY_HALF': b0, 'B5_ALL20': b0, 'B6_ALL30': b0})
    return rows


def test_budget_adopt_then_revert(tmp_path):
    rec = ap.decide_budget(tmp_path, '2026-12-28', _rows(120))
    assert rec['action'] == 'ADOPT' and rec['series'] == 'B2_GAP_HALF'
    st = ap.load(tmp_path)
    assert st['budget']['effective_from'] == '2026-12-29'
    bad = [dict(r, day='2027-01-%02d' % (1 + i % 28)) for i, r in enumerate(_rows(120, good=False))]
    rec = ap.decide_budget(tmp_path, '2027-01-28', bad)
    assert rec['action'] == 'REVERT' and ap.load(tmp_path)['budget'] is None


def test_budget_needs_100_races(tmp_path):
    assert ap.decide_budget(tmp_path, '2026-12-10', _rows(50))['action'] == 'KEEP'


def test_skip_series_never_adopted():
    assert 'B1_GAP_SKIP' not in ap.BUDGET_SERIES and 'B3_KRSD_SKIP' not in ap.BUDGET_SERIES


def test_apply_budget_only_reduces(tmp_path):
    ap._save(tmp_path, {'budget': {'series': 'B5_ALL20', 'effective_from': '2026-12-01'}, 'krs': None})
    tk = [{'bet_type': 'TRIFECTA', 'selection': [str(a), str(b), str(c)], 'mec_tier': 'CORE'}
          for a in range(1, 5) for b in range(1, 5) for c in range(1, 6) if len({a, b, c}) == 3][:40]
    capped = {'tickets': tk, 'kept_count': 40, 'kept_investment': 4000, 'sha256': 'x'}
    new, info = ap.apply_budget(capped, [1, 2, 3, 4, 5], {'runner_scores': [{'overall': 3}, {'overall': 1}]}, {}, tmp_path, '2026-12-02')
    assert len(new['tickets']) == 20 and new['tickets_before_budget'] == tk and info['applied']
    same, info = ap.apply_budget(capped, [1, 2, 3], None, None, tmp_path, '2026-11-30')
    assert same is capped and info is None


def test_krs_adopt_and_input(tmp_path):
    cmp = {'HOLD15': {'formal': {'races': 120, 'log_loss': 2.1, 'auc_top3': 0.70},
                      'HOLD15': {'races': 120, 'log_loss': 2.0, 'auc_top3': 0.71}}}
    rec = ap.decide_krs(tmp_path, '2026-12-20', cmp)
    assert rec['action'] == 'ADOPT'
    kin = {'horses': [{'hsv': {'early_position_hold': 50, 'midrace_hold': 50, 'front_friction_tolerance': 50}}]}
    new, var = ap.krs_input_for(kin, tmp_path, '2026-12-21')
    assert var == 'HOLD15' and new['horses'][0]['hsv']['early_position_hold'] == 65
    assert kin['horses'][0]['hsv']['early_position_hold'] == 50
    rev = ap.decide_krs(tmp_path, '2027-01-20', {'BASE': {'formal': {'races': 110, 'log_loss': 2.2}, 'BASE': {'races': 110, 'log_loss': 2.1}}})
    assert rev['action'] == 'REVERT' and ap.load(tmp_path)['krs'] is None
    again = ap.decide_krs(tmp_path, '2027-01-21', cmp)
    assert again['action'] == 'KEEP'
    assert '自動の改善採否' in ap.md([rec, rev])

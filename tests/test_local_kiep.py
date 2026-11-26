import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'runtime'))
from runtime.local_autopilot import auto_candidates as ac, formal_mix as fm, kiep  # noqa: E402

DATA = Path('/tmp/claude-0/-home-claude/0d2af595-a9df-594c-a0fa-fb83f226e379/scratchpad/data/output')


def test_ranking_reproduces_formal_consumer_when_data_available():
    rs = kiep.races(DATA) if DATA.exists() else []
    if not rs:
        return
    sample = rs[::10]
    ok = sum(kiep.ranking(r['full29'], r['ext']) == r['stored'] for r in sample)
    assert ok >= 0.9 * len(sample)


def test_kiep_report_registers_idxabl_once(tmp_path):
    d = tmp_path / 'kiep'
    d.mkdir()
    ab = {i: {'train': {'auc_gain': 0.0}, 'test': {'auc_gain': 0.0}, 'verdict': 'NO_EFFECT'} for i in kiep.INDEX_IDS}
    ab['ASI'] = {'train': {'auc_gain': 0.013}, 'test': {'auc_gain': 0.008}, 'verdict': 'DROP_HELPS'}
    (d / '2026-11-30.json').write_text(json.dumps({'ablation': ab}))
    res = ac.daily(tmp_path, '2026-11-30')
    st = ac.load(tmp_path)
    k = [c for c in res['new'] if 'IDXABL' in c]
    assert k and st['candidates'][k[0]]['variant'] == f"GEN:IDXABL:drop={kiep.INDEX_IDS.index('ASI')}"
    assert not [c for c in ac.daily(tmp_path, '2026-12-01')['new'] if 'IDXABL' in c]
    assert 'ASI' in ac.md(tmp_path, res)


def test_idxabl_without_source_keeps_base():
    s = {'ranking': ['1', '2', '3'], 'roles': {'1': ['W'], '2': ['P2'], '3': ['P2']},
         'tickets': [{'bet_type': 'EXACTA', 'selection': [1, 2]}], 'signed_final_tickets': [{'bet_type': 'EXACTA', 'selection': [1, 2]}]}
    assert fm.variant_of(s, 'GEN:IDXABL:drop=27') == fm.signed(s)


def test_propagate_is_identity_without_change_and_linear():
    old = {k: 50.0 for k in kiep.INDEX_IDS}
    assert kiep.propagate(old, dict(old)) == old
    new = dict(old, **{'HPI-L': 60.0})
    v = kiep.propagate(old, new)
    assert abs(v['TPI-L'] - (50 + 0.18 * 10)) < 1e-9          # min major unchanged (50), penalty unchanged
    assert abs(v['SRI-L'] - (50 + 0.20 * 1.8)) < 1e-9
    assert abs(v['ZAI-WIN'] - (50 + (1.8 + 0.36) / 6)) < 1e-9


def test_kiep_scale_registers_idxscl(tmp_path):
    d = tmp_path / 'kiep'
    d.mkdir()
    ab = {i: {'train': {'auc_gain': 0.0}, 'test': {'auc_gain': 0.0}, 'verdict': 'NO_EFFECT'} for i in kiep.INDEX_IDS}
    sc = {'factor': 1.5, 'rows': {'CFIg-L': {'train': {'auc_gain': 0.006}, 'test': {'auc_gain': 0.005}, 'verdict': 'UP_HELPS'}}}
    (d / '2026-11-30.json').write_text(json.dumps({'ablation': ab, 'scale': sc}))
    res = ac.daily(tmp_path, '2026-11-30')
    st = ac.load(tmp_path)
    k = [c for c in res['new'] if 'IDXSCL' in c]
    assert k and st['candidates'][k[0]]['variant'] == f"GEN:IDXSCL:i={kiep.INDEX_IDS.index('CFIg-L')}:s=150"

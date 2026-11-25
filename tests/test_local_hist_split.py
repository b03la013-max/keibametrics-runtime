"""Discovery / validation split of the hist_stats A/E tables (Drive 精読 q273, B3, 2026-11-25). Evidence only."""
import json

from runtime.local_autopilot import hist_stats as hs


def _synthetic():
    from tests.test_local_hist_stats import races
    return races()


def test_build_date_range_keeps_history_and_cuts_cells():
    r = _synthetic()
    full = hs.build(r, 'T')
    a = hs.build(r, 'T', (None, '2026-10-10'))
    b = hs.build(r, 'T', ('2026-10-10', None))
    assert a['starts'] + b['starts'] == full['starts']
    assert a['period'] == ['2026-10-01', '2026-10-01'] and b['period'] == ['2026-10-15', '2026-10-15']
    # validation start still sees its discovery-period previous start (distance change table exists)
    assert any(c['conditions'].get('change') == 'LONGER' or 'LONGER' in json.dumps(c['conditions'])
               for c in b['tables'].get('T5_DIST_CHANGE', []))


def test_build_without_range_is_unchanged():
    r = _synthetic()
    assert json.dumps(hs.build(r, 'T'), sort_keys=True) == json.dumps(hs.build(r, 'T', None), sort_keys=True)


def test_split_check_verdicts(monkeypatch):
    def fake_build(races, source, date_range=None):
        lo = date_range[0] if date_range else None
        mk = lambda cond, n, ae: {'conditions': cond, 'starts': n, 'top3': 0.3, 'ae_top3': ae, 'small_sample': n < hs.MIN_N,
                                  'expected_top3': n * 0.3 / ae, 'n1': int(n * 0.3), 'n2': 0, 'n3': 0}
        if lo is None:   # discovery
            cs = [mk({'k': 'strong'}, 400, 1.6), mk({'k': 'flip'}, 400, 1.6), mk({'k': 'gone'}, 400, 1.6),
                  mk({'k': 'flat'}, 400, 1.0), mk({'k': 'tiny'}, 10, 3.0)]
        else:
            cs = [mk({'k': 'strong'}, 200, 1.3), mk({'k': 'flip'}, 200, 0.8), mk({'k': 'gone'}, 5, 1.5)]
        return {'period': ['x', 'y'], 'starts': 1, 'tables': {'T5_INTERVAL': cs}}
    monkeypatch.setattr(hs, 'build', fake_build)
    sp = hs.split_check({}, 'T')
    v = {c['conditions']['k']: c['verdict'] for c in sp['cells']}
    assert v == {'strong': 'HOLDS', 'flip': 'FAILS', 'gone': 'UNTESTED', 'flat': 'NOT_A_LEAD', 'tiny': 'NOT_A_LEAD'}
    s = sp['summary']['T5_INTERVAL']
    assert s['leads'] == 3 and s['HOLDS'] == 1 and s['FAILS'] == 1 and s['UNTESTED'] == 1
    assert sp['cut'] == hs.SPLIT_CUT == '2025-07-01'
    md = hs.split_md(sp)
    assert 'HOLDS' in md and 'k=strong' in md and 'k=flip' not in md.split('## 検証期間')[1]


def test_split_q_only_from_discovery(monkeypatch):
    calls = []
    real = hs.bh_qvalues
    monkeypatch.setattr(hs, 'bh_qvalues', lambda cs, key='ae_top3': calls.append(len(cs)) or real(cs, key))
    hs.split_check(_synthetic(), 'T', cut='2026-10-10')
    # one BH call per discovery table that has A/E cells; validation cells are never passed in
    disc = hs.build(_synthetic(), 'T', (None, '2026-10-10'))
    n = [len([c for c in cs if c.get('ae_top3') is not None]) for cs in disc['tables'].values()]
    assert sorted(calls) == sorted(x for x in n if x)


def test_write_emits_split_files(tmp_path, monkeypatch):
    monkeypatch.delenv("KM_NAR_ROOT", raising=False)
    monkeypatch.setattr(hs, 'load_sources', lambda root, nar_root=None: (_synthetic(), 'T'))
    st = hs.write(tmp_path)
    assert st and (tmp_path / 'hist_stats_split.json').exists() and (tmp_path / 'hist_stats_split.md').exists()
    sp = json.loads((tmp_path / 'hist_stats_split.json').read_text())
    assert sp['profile'].endswith('+SPLIT') and 'summary' in sp


def test_write_split_throttle_and_nar_root(tmp_path, monkeypatch):
    seen = []
    monkeypatch.setattr(hs, 'load_sources', lambda root, nar_root=None: seen.append(nar_root) or (_synthetic(), 'T'))
    monkeypatch.setenv('KM_NAR_ROOT', '/x/km_nar')
    assert hs.write_split(tmp_path) is not None and seen == ['/x/km_nar']
    assert hs.write_split(tmp_path) is None and seen == ['/x/km_nar']        # rebuilt at most once per 20 h
    assert hs.write_split(tmp_path, min_age_h=0) is not None


def test_write_split_never_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(hs, 'split_check', lambda *a, **k: 1 / 0)
    assert hs.write_split(tmp_path, races=_synthetic(), src='T') is None

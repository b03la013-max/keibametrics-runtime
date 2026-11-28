import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'runtime', 'banei_autopilot'))
import review  # noqa: E402


def test_flat_components_detects_constant():
    rows = [{'tpi': 50.0, 'cci': 0, 'jbr': 1.5, 'dcr': 80}, {'tpi': 55.0, 'cci': 0, 'jbr': 1.5, 'dcr': 90},
            {'tpi': 60.0, 'cci': 0, 'jbr': None, 'dcr': 70}, {'tpi': 52.0, 'cci': 0, 'dcr': 85}]
    fc = review.flat_components(rows)
    assert 'cci' in fc['flat'] and 'tpi' not in fc['flat'] and 'dcr' not in fc['flat']
    assert 'jbr' in fc['unjudged'] and 'jbr' not in fc['flat']   # only 2 horses carry jbr
    assert fc['field'] == 4
    assert review.flat_components([]) is None
    assert review.flat_components([{'cci': True}, {'cci': True}, {'cci': True}])['flat'] == []


def test_flat_summary_and_markdown():
    revs = [{'flat_components': {'flat': ['cci'], 'unjudged': ['jbr'], 'field': 8}},
            {'flat_components': {'flat': [], 'unjudged': [], 'field': 8}}, {'flat_components': None}]
    s = review.flat_components_summary(revs)
    assert s['cci'] == {'flat': 1, 'unjudged': 0, 'judged': 2}
    assert s['jbr'] == {'flat': 0, 'unjudged': 1, 'judged': 1}
    assert 'tpi' not in s
    assert review.flat_components_summary([]) is None
    base = {'races': 2, 'missed': 0, 'stake': 6000, 'return': 9000, 'pfs': 150.0,
            'pfs_without_top1': None, 'trio_hit': 1, 'trio_pfs': None, 'exact_hit': 0, 'exact_pfs': None, 'honmei_win': 1,
            'honmei_top3': 1, 'winner_in_W': 1, 'second_in_P2': 2, 'third_in_P3': 0, 'ffl': {}, 'cause': {},
            'funnel': {k: 0 for k in ('winner_in_W', 'pair_in_tickets', 'trio_bought', 'exact_bought', 'profit')},
            'hit_but_loss': 0, 'extreme_hub': 0, 'hub_failed': 0, 'p0p1': {}, 'rev_audit': None}
    md = review._md('t', dict(base, flat_components=s))
    assert 'cci 1/2・0' in md


def test_flat_components_full_uses_private_cache(tmp_path, monkeypatch):
    import json
    out = tmp_path / 'output_ban' / '2026-11-28'
    out.mkdir(parents=True)
    public = [{'no': i, 'tpi': 50.0 + i, 'dcr': 90} for i in range(1, 6)]   # bsi/idx/isv redacted in public rows
    assert {'idx', 'bsi', 'isv'} <= set(review.flat_components(public)['unjudged'])
    cache = tmp_path / 'cache' / '2026-11-28'
    cache.mkdir(parents=True)
    full = [dict(r, bsi=40.0 + r['no'], idx=55.0, isv=1.0 + r['no']) for r in public]
    (cache / 'R01.full.json').write_text(json.dumps({'evaluation': {'rows': full}}))
    monkeypatch.setenv('KM_BAN_CACHE', str(tmp_path / 'cache'))
    fc = review.flat_components_full(out, '01', '', public)
    assert fc['unjudged'] == [k for k in review.FLAT_KEYS if k not in ('idx', 'bsi', 'isv', 'tpi', 'dcr')]
    assert 'idx' in fc['flat'] and 'dcr' in fc['flat'] and 'bsi' not in fc['flat'] and 'isv' not in fc['flat']
    assert '40.0' not in json.dumps(fc)                                    # names only, no raw values
    monkeypatch.setenv('KM_BAN_CACHE', str(tmp_path / 'nocache'))
    assert review.flat_components_full(out, '01', '', public) == review.flat_components(public)   # falls back

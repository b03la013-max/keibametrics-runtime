import json

from runtime.local_autopilot import auto_candidates as ac, auto_promote as ap, formal_mix as fm


def _summary(tmp, day='2026-11-22', pr=None):
    d = tmp / day / 'review'
    d.mkdir(parents=True)
    pr = pr or [{'id': 'P1:HIT_BUT_LOSS', 'tier': 'P1', 'count': 13, 'impact_yen': 44450},
                {'id': 'P1:ROLE_P2_MISS', 'tier': 'P1', 'count': 10, 'impact_yen': 60000},
                {'id': 'P2:CALIBRATION_BACKLOG', 'tier': 'P2', 'count': 34, 'impact_yen': 134450}]
    (d / 'daily_summary.json').write_text(json.dumps({'improvement_priority': pr}))


def test_generate_from_priorities_next_day(tmp_path):
    _summary(tmp_path)
    res = ac.daily(tmp_path, '2026-11-22')
    st = ac.load(tmp_path)
    assert len(res['new']) == 2
    first = st['candidates'][res['new'][0]]
    assert first['origin']['priority'] == 'P1:ROLE_P2_MISS'           # highest impact first
    assert first['first_eligible_post'].startswith('2026-11-23')     # registered before its first eligible day
    assert st['candidates'][res['new'][1]]['origin']['priority'] == 'P1:HIT_BUT_LOSS'


def test_no_duplicates_and_slot_limit(tmp_path):
    _summary(tmp_path)
    for d in range(10):
        day = f'2026-11-{22 + d:02d}'
        if d:
            _summary(tmp_path, day)
        ac.daily(tmp_path, day)
    st = ac.load(tmp_path)
    names = [c['variant'] for c in st['candidates'].values()]
    assert len(names) == len(set(names))
    assert sum(c['status'] == 'EVALUATING' for c in st['candidates'].values()) <= ac.MAX_EVALUATING
    assert not set(names) & {v for v, _ in ap.CANDIDATES.values()}


def test_retire_when_worse_after_100(tmp_path):
    _summary(tmp_path)
    res = ac.daily(tmp_path, '2026-11-22')
    cid = res['new'][0]
    dec = {'evaluated': {cid: {'races': 100, 'candidate': {'pfs': 40, 'pfs_ex_top1': 30},
                               'champion': {'pfs': 50, 'pfs_ex_top1': 35}}}}
    _summary(tmp_path, '2026-12-20')
    out = ac.daily(tmp_path, '2026-12-20', dec)
    assert cid in out['retired'] and ac.load(tmp_path)['candidates'][cid]['status'] == 'RETIRED'


def _s():
    mec = [{'bet_type': 'TRIFECTA', 'selection': [1, 2, 3]}, {'bet_type': 'TRIFECTA', 'selection': [1, 3, 2]},
           {'bet_type': 'EXACTA', 'selection': [1, 2]}, {'bet_type': 'TRIFECTA', 'selection': [4, 2, 1]}]
    return {'ranking': [str(i) for i in range(1, 9)],
            'roles': {'1': ['W'], '4': ['W'], '2': ['P2'], '3': ['P2'], '5': ['P2'], '6': ['P2'], '7': ['P2']},
            'tickets': mec, 'signed_final_tickets': mec, '_market_order': [8, 1, 2]}


def test_generated_families_same_budget():
    s = _s()
    base = fm.signed(s)
    for fam, grid in ac.FAMILY_GRID.items():
        for p in grid:
            v = fm.variant_of(s, fm.gen_name(fam, **p))
            assert len(v) <= fm.CAP
            if fam not in ('THIRDK',):
                assert len(v) == min(fm.CAP, max(len(base), len(v)))


def test_challenger_vs_active(tmp_path, monkeypatch):
    st = {'profile': ap.PROFILE, 'active': {'candidate': 'C13-FORMAL-MIX-P2BOX20', 'variant': 'MIX_P2BOX20',
                                            'effective_from': '2026-11-22', 'promoted_on': '2026-11-21'},
          'history': [], 'blocked_until': {}}
    ap.state_path(tmp_path).write_text(json.dumps(st))
    (tmp_path / 'auto_candidates.json').write_text(json.dumps({'candidates': {'G001-X': {
        'variant': 'GEN:CORE:n=2', 'status': 'EVALUATING', 'first_eligible_post': '2026-11-23T00:00:00+09:00'}}}))
    rows = []
    for i in range(120):
        v = ['OHI', 'KAW', 'FNB'][i % 3]
        rows.append({'key': f'{v}_{i:02d}', 'R54_60': (6000, 3000, 1, 60), 'MIX_P2BOX20': (6000, 3500, 1, 60),
                     'GEN:CORE:n=2': (6000, 5000 + i, 1, 60)})
    monkeypatch.setattr(ap, 'CANDIDATES', {})
    rec = ap.decide(tmp_path, '2026-12-30', rows_fn=lambda root, since: rows)
    assert rec['action'] == 'PROMOTE' and rec['candidate'] == 'G001-X' and rec['replaced'] == 'C13-FORMAL-MIX-P2BOX20'
    assert rec['evaluated']['G001-X']['against'] == 'MIX_P2BOX20'


def test_pairfull_keeps_longshot_third():
    s = _s()
    v = fm.variant_of(s, 'GEN:PAIRFULL:pairs=6')
    assert ('TRIFECTA', [1, 2, 8]) in v and len(v) <= fm.CAP


def test_cap_lost_hit_priority(tmp_path):
    _summary(tmp_path, pr=[{'id': 'P1:HIT_BUT_LOSS', 'tier': 'P1', 'count': 13, 'impact_yen': 44450}])
    (tmp_path / '2026-11-22' / 'review' / 'formal_eval.json').write_text(json.dumps(
        {'aggregate': {'LIVE_R54': {'races_with_lost_hits': 13, 'payout_lost': 514150}}}))
    res = ac.daily(tmp_path, '2026-11-22')
    st = ac.load(tmp_path)
    assert st['candidates'][res['new'][0]]['origin']['priority'] == 'P1:CAP_LOST_HIT'
    assert st['candidates'][res['new'][0]]['family'] == 'PAIRFULL'


def test_mktp2_reforms_second_set_with_market():
    s = _s()
    s['_market_order'] = [8, 1, 7, 2]
    v = fm.variant_of(s, 'GEN:MKTP2:blend=75')
    assert len(v) <= fm.CAP and any(t[0] == 'EXACTA' and t[1] == [1, 8] for t in v)
    s['_market_order'] = []
    assert fm.variant_of(s, 'GEN:MKTP2:blend=50') == fm.signed(s)


def test_krscap_orders_mec_by_simulation():
    s = _s()
    mec = [{'bet_type': 'TRIFECTA', 'selection': [1, 2, 3], 'mec_tier': 'CORE'},
           {'bet_type': 'TRIFECTA', 'selection': [4, 2, 1], 'mec_tier': 'CORE'},
           {'bet_type': 'EXACTA', 'selection': [1, 2], 'mec_tier': 'TAIL'}]
    s['signed_final_tickets'] = mec
    util = {'top_trifecta_occurrence': [{'W': 4, 'P2': 2, 'P3': 1, 'frequency': 0.2}],
            'top_exacta_occurrence': [{'W': 1, 'P2': 2, 'frequency': 0.3}],
            'summary': [{'horse_no': h, 'SSR-W': 0.1, 'SSR-P2': 0.1, 'SSR-P3': 0.1} for h in range(1, 9)]}
    s['_krs'] = fm.krs_view(util)
    v1 = fm.variant_of(s, 'GEN:KRSCAP:mode=1')
    assert v1[0] == ('EXACTA', [1, 2]) and v1[1] == ('TRIFECTA', [4, 2, 1])
    v2 = fm.variant_of(s, 'GEN:KRSCAP:mode=2')
    assert v2[0] == ('TRIFECTA', [4, 2, 1]) and v2[-1] == ('EXACTA', [1, 2])
    s['_krs'] = None
    assert fm.variant_of(s, 'GEN:KRSCAP:mode=1') == fm.signed(s)

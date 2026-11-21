import json

from runtime.local_autopilot import auto_promote as ap


def _row(key, champ, cand, others=(0, 0, False, 60)):
    r = {'day': '2026-11-22', 'key': key, 'R54_60': champ}
    for name in ('MIX_P2BOX20', 'MIX_WAXIS_TRIO', 'KEEP_MEC_TRIO20', 'W_PLUS_TOP2POP_60'):
        r[name] = others
    r['MIX_P2BOX20'] = cand
    return r


def _rows(n, champ_pay, cand_pay, venues=('OHI', 'KSM')):
    out = []
    for i in range(n):
        v = venues[i % len(venues)]
        out.append(_row(f'{v}_{i % 12 + 1:02d}', (6000, champ_pay[i % len(champ_pay)], champ_pay[i % len(champ_pay)] > 0, 60),
                        (6000, cand_pay[i % len(cand_pay)], cand_pay[i % len(cand_pay)] > 0, 60)))
    return out


def test_promotes_only_with_every_check(tmp_path):
    good = _rows(120, [0, 3000, 9000], [0, 4000, 9500])
    rec = ap.decide(tmp_path, '2026-11-21', rows_fn=lambda root, since: good)
    assert rec['action'] == 'PROMOTE' and rec['candidate'] == 'C13-FORMAL-MIX-P2BOX20'
    assert rec['effective_from'] == '2026-11-22'
    assert ap.active_variant(tmp_path, '2026-11-21') is None
    assert ap.active_variant(tmp_path, '2026-11-22')['variant'] == 'MIX_P2BOX20'
    st = json.loads(ap.state_path(tmp_path).read_text())
    assert st['history'][-1]['action'] == 'PROMOTE'


def test_too_few_races_or_one_venue_keeps_champion(tmp_path):
    few = _rows(99, [0, 3000], [0, 9000])
    assert ap.decide(tmp_path, '2026-11-21', rows_fn=lambda r, s: few)['action'] == 'KEEP_CHAMPION'
    one = _rows(120, [0, 3000], [0, 9000], venues=('OHI',))
    p = tmp_path / 'b'
    p.mkdir()
    rec = ap.decide(p, '2026-11-21', rows_fn=lambda r, s: one)
    assert rec['action'] == 'KEEP_CHAMPION'
    assert not rec['evaluated']['C13-FORMAL-MIX-P2BOX20']['checks']['venues_better']


def test_jackpot_only_win_is_not_enough(tmp_path):
    rows = _rows(120, [3000], [2900])
    rows[0]['MIX_P2BOX20'] = (6000, 900000, True, 60)        # one big payout makes the total PFS higher
    rec = ap.decide(tmp_path, '2026-11-21', rows_fn=lambda r, s: rows)
    e = rec['evaluated']['C13-FORMAL-MIX-P2BOX20']
    assert e['checks']['pfs'] and not e['checks']['pfs_ex_top1'] and rec['action'] == 'KEEP_CHAMPION'


def test_probation_demotes_after_100_worse_races(tmp_path):
    good = _rows(120, [0, 3000, 9000], [0, 4000, 9500])
    ap.decide(tmp_path, '2026-11-21', rows_fn=lambda r, s: good)
    bad = _rows(100, [0, 5000, 9000], [0, 3000, 7000])
    rec = ap.decide(tmp_path, '2026-12-10', rows_fn=lambda r, s: bad)
    assert rec['action'] == 'DEMOTE' and rec['effective_from'] == '2026-12-11'
    assert ap.active_variant(tmp_path, '2026-12-11') is None
    st = ap.load_state(tmp_path)
    assert st['blocked_until']['C13-FORMAL-MIX-P2BOX20'] == '2026-12-11'
    early = _rows(50, [0, 5000], [0, 3000])
    p = tmp_path / 'c'
    p.mkdir()
    ap.decide(p, '2026-11-21', rows_fn=lambda r, s: good)
    assert ap.decide(p, '2026-11-25', rows_fn=lambda r, s: early)['action'] == 'PROBATION'


def test_apply_to_cap_keeps_budget_and_records_champion():
    signed = [{'bet_type': 'TRIFECTA', 'selection': [str(a), str(b), str(c)], 'stake': 100, 'mec_tier': 'CORE'}
              for a in (1, 2) for b in (1, 2, 3, 4) for c in (1, 2, 3, 4, 5, 6) if len({a, b, c}) == 3]
    capped = {'max_tickets': 60, 'tickets': signed[:30], 'kept_count': 30, 'kept_investment': 3000, 'sha256': 'x'}
    roles = {'1': ['W', 'P2'], '2': ['W', 'P2'], '3': ['P2'], '4': ['P2'], '5': ['P3'], '6': ['P3']}
    new = ap.apply_to_cap(capped, ['1', '2', '3', '4', '5', '6'], roles, signed, [],
                          {'candidate': 'C13-FORMAL-MIX-P2BOX20', 'variant': 'MIX_P2BOX20', 'effective_from': '2026-11-22'})
    assert new['champion_r54_60_tickets'] == capped['tickets'] and 'sha256' not in new
    trio = [t for t in new['tickets'] if t['bet_type'] == 'TRIO']
    assert len(trio) == 4 and all(t['source'].startswith('AUTO_PROMOTED') for t in trio)
    assert new['kept_investment'] == 100 * len(new['tickets']) and len(new['tickets']) <= 60


def test_formal_mix_uses_champion_when_promoted():
    from runtime.local_autopilot import formal_mix
    sm = {'tickets': [{'bet_type': 'TRIO', 'selection': ['1', '2', '3']}],
          'tickets_r54_60': [{'bet_type': 'TRIFECTA', 'selection': ['1', '2', '3']}]}
    assert formal_mix.signed(sm) == [('TRIFECTA', [1, 2, 3])]
    assert formal_mix.signed({'tickets': sm['tickets']}) == [('TRIO', [1, 2, 3])]

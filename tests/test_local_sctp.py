from runtime.local_autopilot import formal_mix, sctp, auto_promote


def test_trio_protect_same_budget_and_drops_lowest_trifecta():
    rank = list(range(1, 11))
    main = [('TRIFECTA', [1, 2, 3])] * 0 + [('TRIFECTA', [a, b, c]) for a in (1, 2) for b in (1, 2, 3, 4) for c in (3, 4, 5, 9) if len({a, b, c}) == 3]
    main += [('EXACTA', [1, 2])]
    out = formal_mix.trio_protect(main, rank, [1, 2], [1, 2, 3, 4], 4)
    assert len(out) == len(main)
    trios = [t for t in out if t[0] == 'TRIO']
    assert len(trios) == 4 and trios[0][1] == [1, 2, 3]
    assert all(set(t[1]) <= {1, 2, 3, 4} for t in trios)
    assert ('EXACTA', [1, 2]) in out
    dropped = [t for t in main if t not in out]
    assert all(9 in t[1] for t in dropped)


def test_trio_protect_no_trifecta_keeps_main():
    main = [('EXACTA', [1, 2])]
    assert formal_mix.trio_protect(main, [1, 2, 3, 4], [1], [1, 2, 3], 6) == main


def test_candidates_registered():
    assert auto_promote.CANDIDATES['C33-SCTP-TRIO20-60'][0] == 'GEN:TRIOPROT:k=12'


def test_compare_rescue_and_opp_cost():
    rows = [{'day': 'd', 'key': 'URA_01', 'W_PLUS_TOP2POP_60': (6000, 0, False, 60), 'X': (6000, 900, True, 60)},
            {'day': 'd', 'key': 'URA_02', 'W_PLUS_TOP2POP_60': (6000, 5000, True, 60), 'X': (6000, 1000, True, 60)}]
    c = sctp.compare(rows, 'X')
    assert c['rescue'] == 1 and c['rescue_pay'] == 900 and c['opp_cost'] == 1 and c['opp_cost_pay'] == 4000
    assert c['net'] == -3100 and c['by_venue']['URA']['races'] == 2
    assert 'SCTP' in sctp.md({'prereg': 'p', 'first_eligible_day': 'x', 'forward': {'a': c}, 'reference': {}})

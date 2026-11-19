import random

from runtime.local_autopilot import ticket_tree as tt


def _rt(tickets):
    return tt.roundtrip(tickets)


def test_known_layouts_round_trip():
    cases = [
        [('単勝', [(4,)], None), ('複勝', [(4,), (7,)], None)],
        [('ワイド', tt.parse('ワイド', '10-6 / 10-9'), None)],
        [('馬連', [(1, 2), (1, 3), (2, 3)], None)],
        [('馬単', tt.parse('馬単', '4→2,6,10'), None)],
        [('馬単', [(1, 6), (6, 1), (1, 7), (6, 7)], None)],
        [('三連複', tt.parse('三連複', '1-6-9 / 1-8-9 / 1-4-9 / 1-6-8 / 1-4-6'), None)],
        [('三連単', [(1, 10, 4), (1, 10, 6), (1, 4, 10), (6, 1, 10)], None)],
        [('三連単', tt.parse('三連単', '4→2,6→1,2,7'), None)],
        [('三連複', [], None)],
    ]
    for c in cases:
        r = _rt(c)
        assert r['ok'], (c, r)


def test_random_sets_round_trip():
    rnd = random.Random(20261120)
    kinds = ['単勝', '複勝', 'ワイド', '馬連', '馬単', '三連複', '三連単']
    for _ in range(400):
        tickets = []
        for kind in rnd.sample(kinds, rnd.randint(1, 4)):
            n = tt.SIZE[kind]
            horses = rnd.sample(range(1, 17), rnd.randint(n, 7))
            pool = [tuple(rnd.sample(horses, n)) for _ in range(rnd.randint(1, 12))]
            tickets.append((kind, pool, None))
        r = _rt(tickets)
        assert r['ok'], (tickets, r)


def test_mismatch_is_reported_not_repaired():
    text, _ = tt.block([('馬単', [(1, 2), (1, 3)], None)], paper=False)
    back, total = tt.reflatten(text.replace('└─ 3', '└─ 5'))
    assert back == [('馬単', {(1, 2), (1, 5)})] and total == 2

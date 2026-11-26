from runtime.local_autopilot import head_p2 as hp

RANK = [1, 2, 3, 4, 5, 6, 7, 8]
ROLES = {1: ['W'], 2: ['W'], 3: ['P2'], 4: ['P2'], 5: ['P3'], 6: ['P3']}


def F(pace, win):
    return {'PACE': pace, 'EVI': None, 'win': win}


FEATS = {1: F('逃げ', 2.0), 2: F('後方', 3.0), 3: F('後方', 4.0), 4: F('中位', 5.0),
         5: F('好位', 30.0), 6: F('後方', 8.0), 7: F('逃げ', 6.0), 8: F('後方', 50.0)}


def test_w_miss_is_counted_not_ranked():
    r = hp.race(RANK, ROLES, [5, 1, 2], feats=FEATS)
    assert r['status'] == 'W_MISS' and r['k'] == 2 and 'arms' not in r


def test_static_style_market_ranks_same_budget():
    # winner 1 (FRONT), second 5 (好位 = FRONT): static rank of 5 among rest [2..8] is 4
    r = hp.race(RANK, ROLES, [1, 5, 3], feats=FEATS)
    assert r['status'] == 'W_HIT' and r['k'] == 2 and r['head_style'] == 'FRONT'
    a = r['arms']
    assert a['STATIC']['rank'] == 4 and not a['STATIC']['in_k']
    # FRONT horses (5, 7) move up STYLE_SHIFT=2 places: keys 2:0,3:1,4:2,5:1,6:4,7:3,8:6 -> [2,3,5,4,7,6,8]
    assert a['STYLE_COND']['top_k'] == [2, 3] and a['STYLE_COND']['rank'] == 3
    # market order without the head: 2(3.0),3(4.0),4(5.0),7(6.0),6(8.0),5(30),8(50)
    assert a['MARKET_COND']['rank'] == 6
    assert r['second_in_role_P2'] is False


def test_untested_when_features_missing():
    r = hp.race(RANK, ROLES, [1, 3, 2], feats={})
    assert r['arms']['STYLE_COND'] == {'status': 'UNTESTED'}
    assert r['arms']['MARKET_COND'] == {'status': 'UNTESTED'}
    assert r['arms']['STATIC']['rank'] == 2 and r['arms']['STATIC']['in_k']


def test_aggregate_rescued_and_lost_and_line():
    items = [hp.race(RANK, ROLES, [1, 5, 3], feats=FEATS),   # STYLE: 3 (out), STATIC 4 (out)
             hp.race(RANK, ROLES, [2, 3, 1], feats=FEATS),   # head CLOSER; STATIC rank of 3 among [1,3,..] = 2 in_k
             hp.race(RANK, ROLES, [7, 1, 2], feats=FEATS),   # W_MISS
             {'error': 'x'}, None]
    a = hp.aggregate(items)
    assert a['races'] == 3 and a['w_hit'] == 2 and a['w_miss'] == 1
    assert a['arms']['STATIC']['tested'] == 2 and a['arms']['STATIC']['in_k'] == 1
    assert set(a['arms']['STYLE_COND']) >= {'rescued', 'lost', 'paired'}
    assert 'rescued' not in a['arms']['STATIC']
    ln = hp.line(a)
    assert ln.startswith('頭別P2') and 'STATIC 1/2' in ln
    assert hp.line(hp.aggregate([])) is None


def test_prereg_fixed_and_roles_untouched():
    roles = {k: list(v) for k, v in ROLES.items()}
    hp.race(RANK, roles, [1, 5, 3], feats=FEATS)
    assert roles == ROLES
    assert hp.PREREG['control'] == 'STATIC' and hp.PREREG['arms'] == ['STATIC', 'STYLE_COND', 'MARKET_COND']

import json

from runtime.local_autopilot import pop_structures as ps


def rec(order, pops, tri, venue='KNZ', no=1, trainers=None, gone=()):
    rows = [{'number': str(n), 'rank': str(p), 'horse': f'H{n}', 'tamer': (trainers or {}).get(n, f'T{n}'),
             'state': '牡4 /鹿毛', 'weight': '450 +2', 'jockey': 'J'} for n, p in pops.items()]
    return {'venue_id': venue, 'race_date': '2026-11-13', 'race_no': no, 'header': {'distance': 1400, 'going': '良'},
            'rows': rows, 'result': {'order': order, 'non_starters': list(gone),
                                     'payouts': {'TRIFECTA': tri, 'WIN': {str(order[0]): 210}}}}


def test_fav_head_tri2_hit_and_miss():
    r, why = ps.fav_tri2(rec([4, 2, 7, 1], {4: 1, 7: 2, 2: 3, 1: 4}, {'4-2-7': 2730}))
    assert why is None and r['hit'] and r['return'] == 2730 and r['invest'] == 200 and r['fav_won']
    r, _ = ps.fav_tri2(rec([7, 4, 2, 1], {4: 1, 7: 2, 2: 3, 1: 4}, {'7-4-2': 5000}))
    assert not r['hit'] and r['return'] == 0 and r['top3_is_pop123'] and not r['fav_won']


def test_unreadable_is_skipped_not_guessed():
    assert ps.fav_tri2(rec([1, 2, 3], {1: 1, 2: 1, 3: 3}, {'1-2-3': 900}))[1] == 'TIED_POPULARITY'
    assert ps.fav_tri2(rec([1, 2, 3], {1: 1, 2: 2, 4: 4}, {'1-2-3': 900}))[1] == 'POPULARITY_MISSING'
    assert ps.fav_tri2(rec([1, 2, 3], {1: 1, 2: 2, 3: 3}, {}))[1] == 'NO_TRIFECTA_TABLE'


def test_stable_labels_best_is_lowest_popularity():
    from runtime.local_autopilot import hist_stats as hs
    race = next(iter(hs.from_rakuten_backfill(rec([1, 2, 3], {1: 2, 2: 1, 3: 3}, {'1-2-3': 900},
                                                   trainers={1: 'A', 2: 'A', 3: 'B'})).values()))
    assert ps.stable_labels(race) == {1: 'MULTI_OTHER', 2: 'MULTI_BEST', 3: 'SINGLE'}


def test_write_per_venue_never_pooled_and_banei_excluded(tmp_path):
    d = tmp_path / 'backfill' / 'results' / '2026-11-13'
    d.mkdir(parents=True)
    (d / 'KNZ_01.json').write_text(json.dumps(rec([4, 2, 7], {4: 1, 7: 2, 2: 3}, {'4-2-7': 2730})))
    (d / 'OHI_01.json').write_text(json.dumps(rec([1, 2, 3], {1: 1, 2: 2, 3: 3}, {'1-2-3': 600}, venue='OHI')))
    (d / 'OBI_01.json').write_text(json.dumps(rec([1, 2, 3], {1: 1, 2: 2, 3: 3}, {'1-2-3': 600}, venue='OBI')))
    st = ps.write(tmp_path)
    t = st['fav_head_tri2']
    assert set(t['by_venue']) == {'KNZ', 'OHI'} and st['skipped'] == {'BANEI_EXCLUDED': 1}
    assert t['NANKAN']['races'] == 1 and t['NANKAN']['roi'] == 3.0 and t['OTHER_LOCAL']['return'] == 2730
    assert st['class'].startswith('HISTORICAL_BACKFILL_LEARNING')
    assert (tmp_path / 'pop_structures.md').read_text().startswith('# Popularity-structure evidence')

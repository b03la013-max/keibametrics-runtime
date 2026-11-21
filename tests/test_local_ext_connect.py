import json
import random
from datetime import datetime, timedelta, timezone

import pytest

from runtime.local_autopilot import ext_connect as ec


def _race(i, day, venue='OHI', dist=1200, going='良', strong_jockey='強騎', n=8):
    """Synthetic race: horse 1 always ridden by strong_jockey and wins; popularity = horse number."""
    runners = []
    for no in range(1, n + 1):
        runners.append({'no': no, 'frame': (no + 1) // 2, 'name': f'馬{i}_{no}', 'horse_key': f'馬{i}_{no}|x',
                        'sire': '父強' if no == 1 else f'父{no}', 'damsire': f'母父{no}',
                        'jockey': strong_jockey if no == 1 else f'騎{no}', 'trainer': f'厩{no}', 'age': 4,
                        'finish': 8 if no == 8 else (no + 6 if no <= 2 else no - 2) if no < 8 else 8,
                        'status': 'RAN', 'pop': 8 - no + 1})
    # horse 1 (pop 8, the outsider) finishes 1st: jockey / sire A/E far above 1
    for x in runners:
        x['finish'] = {1: 1, 2: 4, 3: 2, 4: 3}.get(x['no'], x['no'])
    if i % 2:   # odd races: the outsider is ridden by someone else and finishes last -> pop-8 expectation 0.5
        runners[0].update(jockey='騎X', sire='父X', finish=n)
        runners[-1]['finish'] = 1
    return {'race_id': f'{venue}_{day.replace("-", "")}_R{i % 12 + 1:02d}', 'date': day, 'venue': venue,
            'race_no': i % 12 + 1, 'surface': 'DIRT', 'distance': dist, 'going': going, 'cond': 'C2',
            'field': n, 'first_corner': {x['no']: x['no'] for x in runners}, 'last_corner': {}, 'runners': runners,
            'payouts': {}}


def _races(k=60, start='2026-09-01'):
    d0 = datetime.fromisoformat(start)
    return {r['race_id']: r for r in (_race(i, (d0 + timedelta(days=i)).date().isoformat()) for i in range(k))}


def test_score_and_bands():
    assert ec.score(1.0) == 52.0
    assert ec.score(2.0) == 72.0 and ec.score(100) == 75.0 and ec.score(0.01) == 30.0
    assert ec.frame_band(1) == 'IN' and ec.frame_band(8) == 'OUT' and ec.frame_band(5) == 'MID'
    assert ec.key(' ☆矢野貴 ') == '矢野貴'


def test_weights_sum_to_one_and_ext_share():
    assert abs(sum(ec.W.values()) - 1.0) < 1e-9
    assert ec.EXT_SHARE == 0.30 and ec.EXT_FROM == '2026-11-22'
    assert not ec.enabled('2026-11-21') and ec.enabled('2026-11-22')


def test_labels_drive_patterns():
    h = [{'date': '2026-01-01', 'venue': 'OHI', 'distance': 1200, 'finish': 1, 'early': 0.0},
         {'date': '2026-06-01', 'venue': 'KNZ', 'distance': 1400, 'finish': 9, 'early': 0.0}]
    labs = dict(ec.labels({'date': '2026-12-20', 'venue': 'KAW', 'distance': 1200, 'going': '重', 'age': 8}, h))
    assert labs['MOVE'] == 'RETURN|7+'            # 南関 circuit before, last start elsewhere, last finish 7+
    assert labs['DIRECT'] == 'N|7+'               # won at OHI 1200, not at KAW 1200
    assert labs['LEAD'] == 'REPEAT'
    assert labs['GOROT'] == 'WET|SHORT|FRONT'
    assert labs['LAYOFF'] == 'LONG' and 'AGED' not in labs
    assert ec.labels({'date': '2026-12-20', 'venue': 'KAW'}, []) == [('DEBUT', 'Y')]


def test_tables_use_only_days_before_and_measure_ae():
    races = _races()
    t = ec.build_tables(races, '2026-10-31')
    assert t['period'][1] < '2026-10-31' and t['starts'] == 8 * 60
    cells = {tuple(json.loads(k)): v for k, v in t['cells'].items()}
    n, a, e = cells[('J', '強騎', 'OHI')]
    assert n == 30 and a == 30 and e < 18             # wins only with 強騎 -> A/E about 2
    s, k, nn, ae = ec.ae_of(cells, [('J', '強騎', 'OHI'), ('J', '強騎')])
    assert s > 60 and k == ('J', '強騎', 'OHI') and ae > 1.8
    assert ec.ae_of(cells, [('J', '無名', 'OHI')])[0] is None


def test_race_ext_and_apply_with_sbo_kb(tmp_path, monkeypatch):
    monkeypatch.setenv('KM_PRIVATE_CACHE', str(tmp_path / 'pc'))
    ec._LOADED.clear()
    races = _races()
    t, hist = ec.build_tables(races, '2026-11-22', with_history=True)
    (tmp_path / 'pc' / 'ext').mkdir(parents=True)
    (tmp_path / 'pc' / 'ext' / 'tables_2026-11-22.json').write_text(json.dumps(t, ensure_ascii=False))
    (tmp_path / 'pc' / 'ext' / 'history_2026-11-22.json').write_text(json.dumps(hist, ensure_ascii=False))
    runners = [{'horse_no': no, 'name': f'新{no}', 'sire': '父強' if no == 1 else '父2', 'damsire': None,
                'current_jockey': '強騎' if no == 1 else '騎2', 'trainer': '厩2', 'frame_no': no, 'age': 4, 'starts': []}
               for no in (1, 2, 3)]
    sbo = {1: {'recent': 70.0, 'dist': None, 'going': 60.0, 'avg': 65.0}, 2: {'recent': 50.0, 'avg': 50.0}}
    kb = {3: {'cci': 'VERY_STRONG', 'tri': 'STRONG', 'pace': '逃げ'}}
    ext, st = ec.race_ext({'venue_id': 'OHI', 'distance': 1200, 'going': '良'}, runners, '2026-11-22', sbo, kb)
    assert st['tables'] and st['sbo_horses'] == 2 and st['kb_horses'] == 1
    assert ext[1]['components']['VMI'] > 52 > ext[2]['components']['VMI']
    assert ext[1]['components']['JKY'] > 60 and ext[1]['components']['BVI'] > 55
    assert ext[3]['components']['CCI'] == 66 and ext[3]['components']['PACE'] == 82 and 'VMI' not in ext[3]['components']
    assert ext[1]['components']['PAT'] is not None          # DEBUT label measured on NAR
    assert ext[1]['EXT'] > ext[2]['EXT']
    base = [{'runner_id': '1', 'overall': 50.0}, {'runner_id': '2', 'overall': 51.0}, {'runner_id': '3', 'overall': 50.5}]
    ranking, rows = ec.apply(base, ext)
    assert ranking[0] == '1' and len(rows) == 3
    assert all(abs(r['overall_connected'] - (0.7 * r['overall_base'] + 0.3 * r['EXT'])) < 1e-6 for r in rows)


def test_missing_everything_is_neutral(tmp_path, monkeypatch):
    monkeypatch.setenv('KM_PRIVATE_CACHE', str(tmp_path / 'none'))
    ec._LOADED.clear()
    runners = [{'horse_no': 1, 'name': 'a'}, {'horse_no': 2, 'name': 'b'}]
    ext, st = ec.race_ext({'venue_id': 'OHI', 'distance': 1200}, runners, '2026-11-23')
    assert not st['tables'] and all(v['EXT'] == 52.0 for v in ext.values())
    ranking, _ = ec.apply([{'runner_id': '2', 'overall': 60.0}, {'runner_id': '1', 'overall': 50.0}], ext)
    assert ranking == ['2', '1']                              # base order kept


def test_sbo_cache_cutoff_and_kb_cutoff(tmp_path, monkeypatch):
    monkeypatch.setenv('KM_PRIVATE_CACHE', str(tmp_path / 'pc'))
    jst = timezone(timedelta(hours=9))
    r = {'race_date': '2026-11-22', 'venue_id': 'OHI', 'venue_name': '大井', 'race_no': 3}
    dl = datetime(2026, 11, 22, 15, 0, tzinfo=jst)
    ec.save_sbo('2026-11-22', 'OHI', 3, {'status': 'OK', 'sha256': 'x', 'table': {1: {'avg': 60.0}}},
                datetime(2026, 11, 22, 14, 0, tzinfo=jst).isoformat())
    t, m = ec.sbo_for(r, dl)
    assert m['status'] == 'USED_CACHE' and t == {1: {'avg': 60.0}}
    t, m = ec.sbo_for(r, datetime(2026, 11, 22, 13, 0, tzinfo=jst))      # cache newer than cutoff, no fetch
    assert t is None and m['status'] == 'NOT_FETCHED'
    day = tmp_path / 'day'
    (day / 'external').mkdir(parents=True)
    (day / 'external' / 'keibabook_bands.json').write_text(json.dumps(
        {'captured_at': '2026-11-22T05:00:00+00:00', 'races': [{'venue': '大井', 'race_no': 3, 'horses': {'1': {'cci': 'STRONG'}}}]},
        ensure_ascii=False))
    kb, km = ec.kb_for(day, r, dl)
    assert km['status'] == 'USED' and kb == {1: {'cci': 'STRONG'}}
    kb, km = ec.kb_for(day, r, datetime(2026, 11, 22, 13, 0, tzinfo=jst))
    assert kb is None and km['status'] == 'CAPTURED_AFTER_CUTOFF'


def test_connect_record_keeps_base_ranking(tmp_path, monkeypatch):
    monkeypatch.setenv('KM_PRIVATE_CACHE', str(tmp_path / 'pc'))
    ec._LOADED.clear()
    num = {'ranking': ['2', '1'], 'runner_scores': [{'runner_id': '2', 'overall': 52.5}, {'runner_id': '1', 'overall': 52.0}]}
    r = {'race_date': '2026-11-22', 'venue_id': 'OHI', 'venue_name': '大井', 'race_no': 1}
    snap = {'status': 'OK', 'sha256': 'abc', 'table': {1: {'recent': 80.0, 'avg': 80.0}, 2: {'recent': 40.0, 'avg': 40.0}}}
    dl = datetime(2026, 11, 22, 15, 0, tzinfo=timezone.utc)
    rec = ec.connect(r, {'distance': 1200, 'going': '良'}, [{'horse_no': 1, 'name': 'a'}, {'horse_no': 2, 'name': 'b'}],
                     num, tmp_path, dl, lambda: (snap, '2026-11-22T10:00:00+00:00'))
    assert rec['ranking_base'] == ['2', '1'] and rec['ranking'] == ['1', '2'] and rec['changed_top3']
    assert rec['sbo']['status'] == 'USED_FRESH' and num['ranking'] == ['2', '1']
    assert ec.sbo_cache_path('2026-11-22', 'OHI', 1).exists()


def test_c26_audit_counts_connected_vs_base(tmp_path):
    f = tmp_path / '2026-11-22' / 'formal'
    f.mkdir(parents=True)
    sm = {'status': 'SIGNED_FINAL', 'ranking_base': ['1', '2', '3', '4'], 'ranking': ['4', '1', '2', '3'],
          'ext_connection': {'profile': ec.PROFILE}}
    (f / 'OHI_01.summary.json').write_text(json.dumps(sm))
    (f / 'OHI_01.result.json').write_text(json.dumps({'order': [4, 1, 2]}))
    (f / 'OHI_02.summary.json').write_text(json.dumps(dict(sm, ext_connection=None)))   # not connected -> excluded
    (f / 'OHI_02.result.json').write_text(json.dumps({'order': [4, 1, 2]}))
    a = ec.audit(tmp_path, {'2026-11-22'})
    assert a['races'] == 1 and a['gained'] == ['OHI_01'] and not a['lost']
    assert a['base']['winner_in_W3'] == 0 and a['connected']['winner_in_W3'] == 1
    assert a['connected']['winner_mean_rank'] == 1 and a['by_venue']['OHI']['base']['winner_mean_rank'] == 4

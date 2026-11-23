"""亀谷 sire rules v3 (B4 2026-11-24): corrected rules as the EXT label KAME3, own component KM3 at weight 0."""
import json

from research.kametani import build_rules_v3 as b3
from runtime.local_autopilot import bloodline_kametani as bk
from runtime.local_autopilot import ext_connect as ec
from runtime.local_autopilot import ext_model as em
from runtime.local_autopilot import kametani_v3 as k3

RACE = {'surface': 'DIRT', 'distance': 1600, 'going': '良', 'race_date': '2026-11-24', 'venue_id': 'OHI'}


def H(sire, damsire, age=4, sex='牡', pop=5, finish=7, date='26.10.20'):
    return {'sire': sire, 'damsire': damsire, 'sex_age': f'{sex}{age}', 'age': age, 'popularity': pop, 'frame_no': 4,
            'starts': [{'finish': finish, 'distance': 1600, 'surface': 'DIRT', 'content_positions': [8],
                        'field_size': 12, 'date': date}]}


def R(**kw):
    return {**RACE, **kw}


def test_committed_json_is_the_build_output_and_v2_is_untouched():
    built = b3.build()
    on_disk = json.loads(k3.RULES_V3.read_text())
    assert json.dumps(built, ensure_ascii=False, sort_keys=True) == json.dumps(on_disk, ensure_ascii=False, sort_keys=True)
    v2 = json.loads(bk.RULES_V2.read_text())
    assert v2['profile'].startswith('KM-KAMETANI-SIRE-RULES-STRUCTURED-v2')
    assert len(on_disk['entries']) == len(v2['entries'])
    for no in ('022', '023', '034', '039', '041', '052', '075', '076'):
        assert no in on_disk['patched_entries']
    for no in ('003', '014', '015', '016', '071', '088', '091'):
        assert no in on_disk['omitted']


def test_023_ss_damsire_caution_turf_only_in_v3():
    assert k3.label(H('タワーオブロンドン', 'キズナ'), R(distance=1400)) in ('NONE', 'BUY')
    assert bk.evaluate(H('タワーオブロンドン', 'キズナ'), R(distance=1400))['caution_match'] is True    # v2 unchanged


def test_039_born_year():
    assert k3.label(H('キズナ', 'ヘニーヒューズ', age=6), R(distance=1800)) in ('BUY', 'BOTH')
    assert k3.label(H('キズナ', 'ヘニーヒューズ', age=5), R(distance=1800)) not in ('BUY', 'BOTH')


def test_022_dirt_buy_needs_short_distance():
    assert k3.label(H('シスキン', 'ヘニーヒューズ'), R(distance=1200)) in ('BUY', 'BOTH')
    assert k3.label(H('シスキン', 'ヘニーヒューズ'), R(distance=1800)) not in ('BUY', 'BOTH')


def test_072_damsire_deep_short_dirt_old_favourite():
    ev = k3.evaluate(H('存在しない種牡馬', 'ディープインパクト', age=5, pop=1), R(distance=1200))
    assert ev and ev['caution'] is True and ev['entries'][0]['kind'] == 'DAMSIRE'
    assert k3.label(H('存在しない種牡馬', 'ディープインパクト', age=3, pop=1), R(distance=1200)) == 'NONE'


def test_type_rules_follow_sire_country():
    us = next(n for n, t in bk._load()['types'].items() if (bk.sire_type(n) or {}).get('country') == '米国型')
    ev = k3.evaluate(H(us, None, age=2), R(distance=1200))
    assert any(r['kind'] == 'TYPE' and r['no'] == '089' for r in ev['entries'])
    jp = next(n for n, t in bk._load()['types'].items() if (bk.sire_type(n) or {}).get('country') == '日本型')
    ev = k3.evaluate(H(jp, None), R())
    assert any(r['kind'] == 'TYPE' and r['no'] == '090' and r['caution'] for r in ev['entries'])


def test_unknown_sire_and_damsire_no_label():
    assert k3.label(H('存在しない種牡馬', '存在しない母父'), R()) is None
    assert em.cand_labels({'sire': None, 'damsire': None}, []) == []


def test_ext_label_is_separate_from_pat_and_starts_at_zero():
    cur = {'date': '2026-11-24', 'venue': 'OHI', 'distance': 1800, 'going': '良', 'age': 6, 'sex': '牡', 'pop': 5,
           'frame_no': 4, 'sire': 'キズナ', 'damsire': 'ヘニーヒューズ'}
    hist = [{'date': '2026-10-20', 'venue': 'OHI', 'distance': 1800, 'finish': 7, 'pos': 8, 'field': 12, 'bw': 480}]
    assert ('KAME3', 'BUY') in em.cand_labels(cur, hist) or ('KAME3', 'BOTH') in em.cand_labels(cur, hist)
    assert all(n != 'KAME3' for n, _ in em.labels(cur, hist))           # PAT inputs unchanged
    assert 'KM3' in ec.MEASURED and ec.DEFAULT_BETA['KM3'] == 0.0 and 'KM3' in ec.FIT_NAMES
    assert all(ec.DEFAULT_BETA[k] == v for k, v in {'JKY': 0.35, 'FRM': 0.3, 'HRS': 0.0, 'PAT': 0.3, 'SPD': 0.8}.items())


def test_km3_component_measured_from_cells_only():
    r = {'venue': 'OHI', 'band': 'MID', 'going': 'DRY', 'distance': 1800, 'sire': None, 'damsire': None, 'jockey': None,
         'trainer': None, 'frame': None, 'horse': None, 'bwchg': None, 'age': None, 'season': 'AUT', 'sex': '牡',
         'spd_band': 'NA', 'labels': [], 'cand_labels': [('KAME3', 'BUY')], 'pop': 5, 'fband': 'MID'}
    assert ('P', 'KAME3', 'BUY', 'NANKAN') in em.cell_keys(r)
    cells = {('P', 'KAME3', 'BUY'): [200, 80, 50.0]}
    comp = em.components(cells, r)
    assert 'KM3' in comp and comp['KM3'][0] > em.NEUTRAL and 'PAT' not in comp
    assert 'KM3' not in em.components({}, r)

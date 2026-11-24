"""B3 candidate pattern labels (2026-11-25): INTV / BWSZ / BWPCT / SHFR / FAVRST as own EXT components at weight 0."""
from runtime.local_autopilot import b3_labels as b3
from runtime.local_autopilot import ext_connect as ec
from runtime.local_autopilot import ext_model as em

CUR = {'date': '2026-11-25', 'venue': 'URW', 'distance': 1400, 'going': '良', 'age': 5, 'sex': '牝', 'pop': 1,
       'frame_no': 3, 'bw': 452, 'sire': None, 'damsire': None}


def H(d, dist=1500, early=0.2, bw=470, finish=4):
    return {'date': d, 'venue': 'URW', 'distance': dist, 'finish': finish, 'early': early, 'bw': bw}


HIST = [H('2026-08-01'), H('2026-08-22'), H('2026-09-12'), H('2026-10-03', early=0.8, bw=462)]


def test_bands():
    assert [b3.interval_band(x) for x in (7, 14, 15, 35, 36, 90, 91, None, -1)] == \
        ['<=14', '<=14', '15-35', '15-35', '36-90', '36-90', '91+', None, None]
    assert [b3.bw_size_band(x) for x in (439, 440, 479, 480, 539, 540, None)] == \
        ['<440', '440-479', '440-479', '480-539', '480-539', '540+', None]
    assert b3.bw_pct_band(480, 500) == '<=-4' and b3.bw_pct_band(489, 500) == '-4..-2'
    assert b3.bw_pct_band(500, 500) == '-2..2' and b3.bw_pct_band(515, 500) == '2..4' and b3.bw_pct_band(520, 500) == '>=4'
    assert b3.bw_pct_band(None, 500) is None
    assert b3.sex_group('牝') == 'F' and b3.sex_group('牡') == 'MG' and b3.sex_group('セ') == 'MG' and b3.sex_group('') is None


def test_labels_for_a_runner():
    lab = dict(b3.labels(CUR, HIST))
    assert lab['INTV'] == '36-90'                  # 10/03 -> 11/25 = 53 days
    assert lab['BWSZ'] == '440-479|F'
    assert lab['BWPCT'] == '-4..-2'                # 452 vs 462 = -2.2 %
    assert lab['SHFR'] == 'FRONT'                  # 1500 -> 1400, one of the last 3 starts early <= 0.33
    assert lab['FAVRST'] == 'LONGER'               # usual 21 days, now 53


def test_shfr_only_when_shorter_and_favrst_only_for_top2():
    assert 'SHFR' not in dict(b3.labels(dict(CUR, distance=1500), HIST))
    hist = [dict(h, early=0.7) for h in HIST]
    assert dict(b3.labels(CUR, hist))['SHFR'] == 'NOFRONT'
    assert 'FAVRST' not in dict(b3.labels(dict(CUR, pop=3), HIST))
    assert dict(b3.labels(dict(CUR, date='2026-10-24'), HIST))['FAVRST'] == 'USUAL'
    assert dict(b3.labels(dict(CUR, date='2026-10-12'), HIST))['FAVRST'] == 'SHORTER'
    assert b3.labels(CUR, []) == []


def test_candidate_labels_are_outside_pat_and_start_at_zero():
    cl = dict(em.cand_labels(CUR, HIST))
    assert {'INTV', 'BWSZ', 'BWPCT', 'SHFR', 'FAVRST'} <= set(cl)
    names = {n for n, _ in em.labels(CUR, HIST)}
    assert not names & set(b3.COMPONENTS)          # PAT inputs unchanged
    for lab, comp in b3.COMPONENTS.items():
        assert em.CAND_COMPONENTS[lab] == comp
        assert comp in ec.MEASURED and comp in ec.FIT_NAMES and ec.DEFAULT_BETA[comp] == 0.0
    assert all(ec.DEFAULT_BETA[k] == v for k, v in {'JKY': 0.35, 'FRM': 0.3, 'HRS': 0.0, 'PAT': 0.3, 'SPD': 0.8,
                                                     'KM3': 0.0}.items())


def test_components_measured_from_cells_and_zero_weight_leaves_ext_unchanged():
    r = {'venue': 'URW', 'band': 'SHORT', 'going': 'DRY', 'distance': 1400, 'sire': None, 'damsire': None,
         'jockey': None, 'trainer': None, 'frame': None, 'horse': None, 'bwchg': None, 'age': None, 'season': 'AUT',
         'sex': '牝', 'spd_band': 'NA', 'labels': [], 'cand_labels': [('INTV', '<=14'), ('BWSZ', '540+|MG')],
         'pop': 5, 'fband': 'MID'}
    assert ('P', 'INTV', '<=14', 'NANKAN') in em.cell_keys(r)
    cells = {('P', 'INTV', '<=14'): [400, 60, 90.0], ('P', 'BWSZ', '540+|MG'): [300, 120, 80.0]}
    comp = em.components(cells, r)
    assert comp['ITV'][0] < em.NEUTRAL and comp['BWS'][0] > em.NEUTRAL and 'PAT' not in comp
    contrib = sum(ec.DEFAULT_BETA.get(k, 0.0) * (comp[k][0] - em.NEUTRAL) for k in ec.MEASURED if k in comp)
    assert contrib == 0.0


def test_prereg_is_fixed():
    assert b3.PREREG['registered'] == '2026-11-25' and b3.PREREG['labels'] == list(b3.COMPONENTS)

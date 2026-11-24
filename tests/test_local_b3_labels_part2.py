"""B3 second part (2026-11-25): LEADX / SEASEX / REST2 / FAVSLOW / DEBUTX as own EXT components at weight 0."""
from runtime.local_autopilot import b3_labels as b3
from runtime.local_autopilot import ext_connect as ec
from runtime.local_autopilot import ext_model as em

CUR = {'date': '2026-11-25', 'venue': 'URW', 'distance': 800, 'going': '良', 'age': 4, 'sex': '牡', 'pop': 2,
       'frame_no': 3, 'bw': 470, 'sire': None, 'damsire': None}


def H(d, early=0.5, bw=460, finish=5):
    return {'date': d, 'venue': 'URW', 'distance': 900, 'finish': finish, 'early': early, 'bw': bw}


def test_season_and_pop_bands():
    assert [b3.season_of(d) for d in ('2026-12-01', '2026-02-28', '2026-04-01', '2026-07-01', '2026-10-01', None)] == \
        ['WIN', 'WIN', 'SPR', 'SUM', 'AUT', None]
    assert [b3.pop_band(p) for p in (1, 2, 3, 5, 6, None)] == ['1-2', '1-2', '3-5', '3-5', '6+', None]


def test_debut_gets_seasex_and_debutx_only():
    lab = dict(b3.labels2(dict(CUR, sex='牝', pop=7), []))
    assert lab == {'SEASEX': 'AUT|F', 'DEBUTX': 'F|6+'}


def test_rest2_leadx_favslow():
    hist = [H('2026-05-01', early=0.8), H('2026-10-01', early=0.7), H('2026-10-25', early=0.0, bw=460, finish=2)]
    # 10/25 - 10/01 = 24 days: not a second start after a rest
    lab = dict(b3.labels2(CUR, hist))
    assert 'REST2' not in lab
    assert lab['LEADX'] == 'ONCE|1-3'               # mean early (0.8+0.7+0)/3 > 0.25
    assert lab['FAVSLOW'] == 'SPRINT|2+'           # 800m, two of the last 3 starts early >= 0.6
    hist2 = [H('2026-05-01', early=0.0), H('2026-10-25', early=0.0, bw=460, finish=8)]
    lab2 = dict(b3.labels2(dict(CUR, distance=1400, pop=4), hist2))
    assert lab2['REST2'] == 'UP|7+'                # gap 177 days before last, 31 days now, +2.2 %
    assert lab2['LEADX'] == 'HABIT|7+'
    assert 'FAVSLOW' not in lab2                    # 4th favourite
    assert dict(b3.labels2(dict(CUR, distance=1400), hist2))['FAVSLOW'] == 'OTHER|0'


def test_part2_is_outside_pat_and_starts_at_zero():
    hist = [H('2026-05-01', early=0.0), H('2026-10-25', early=0.0)]
    cl = dict(em.cand_labels(CUR, hist))
    assert {'LEADX', 'SEASEX', 'REST2', 'FAVSLOW'} <= set(cl)
    assert {'INTV', 'BWPCT'} <= set(cl)                         # first part still there
    names = {n for n, _ in em.labels(CUR, hist)}
    assert not names & set(b3.COMPONENTS2)
    for lab, comp in b3.COMPONENTS2.items():
        assert em.CAND_COMPONENTS[lab] == comp
        assert comp in ec.MEASURED and comp in ec.FIT_NAMES and ec.DEFAULT_BETA[comp] == 0.0
    assert not set(b3.COMPONENTS2.values()) & set(b3.COMPONENTS.values())
    assert all(ec.DEFAULT_BETA[k] == v for k, v in {'JKY': 0.35, 'FRM': 0.3, 'HRS': 0.0, 'PAT': 0.3, 'SPD': 0.8}.items())


def test_part2_components_measured_and_zero_weight():
    r = {'venue': 'URW', 'band': 'SHORT', 'going': 'DRY', 'distance': 800, 'sire': None, 'damsire': None,
         'jockey': None, 'trainer': None, 'frame': None, 'horse': None, 'bwchg': None, 'age': None, 'season': 'AUT',
         'sex': '牡', 'spd_band': 'NA', 'labels': [], 'cand_labels': [('FAVSLOW', 'SPRINT|2+'), ('SEASEX', 'AUT|MG')],
         'pop': 2, 'fband': 'MID'}
    cells = {('P', 'FAVSLOW', 'SPRINT|2+'): [300, 60, 100.0], ('P', 'SEASEX', 'AUT|MG'): [900, 300, 250.0]}
    comp = em.components(cells, r)
    assert comp['FSL'][0] < em.NEUTRAL and comp['SSX'][0] > em.NEUTRAL
    assert sum(ec.DEFAULT_BETA.get(k, 0.0) * (comp[k][0] - em.NEUTRAL) for k in ec.MEASURED if k in comp) == 0.0


def test_prereg2_is_fixed():
    assert b3.PREREG2['registered'] == '2026-11-25T03' and b3.PREREG2['labels'] == list(b3.COMPONENTS2)

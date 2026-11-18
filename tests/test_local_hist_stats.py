from runtime.local_autopilot import hist_stats as hs

RL = ('競馬場,競走年月日,レース番号,芝ダート区分,距離,天候,馬場,頭数,条件,コーナー通過順1,コーナー通過順2\n'
      '大井,2026/10/01,1,ダ,1200,晴,良,4,C2三,"1,(2,3)4","1,2,3,4"\n'
      '大井,2026/10/15,1,ダ,1400,曇,重,4,C2三,"1,2,3,4","2,1,3,4"\n')
HL = ('競馬場,競走年月日,レース番号,枠番,馬番,馬名,性,齢,生年月日,父馬名,母父馬名,騎手名,馬体重,馬体重増減,着順,タイム,人気\n'
      '大井,2026/10/01,1,1,1,アオ,牡,3,2023/03/01,父A,母父A,騎1,450,0,1,1:13.5,1\n'
      '大井,2026/10/01,1,2,2,アカ,牝,3,2023/04/01,父B,母父B,騎2,440,2,2,1:13.8,2\n'
      '大井,2026/10/01,1,3,3,キイ,牡,4,2022/05/01,父A,母父C,騎3,460,-2,3,1:14.0,3\n'
      '大井,2026/10/01,1,4,4,ミド,牡,5,2021/05/01,父C,母父A,騎4,470,0,4,1:14.2,4\n'
      '大井,2026/10/15,1,1,1,アオ,牡,3,2023/03/01,父A,母父A,騎1,452,2,2,1:28.0,1\n'
      '大井,2026/10/15,1,2,2,アカ,牝,3,2023/04/01,父B,母父B,騎2,440,0,1,1:27.9,3\n'
      '大井,2026/10/15,1,3,3,キイ,牡,4,2022/05/01,父A,母父C,騎3,460,0,取消,,\n'
      '大井,2026/10/15,1,4,4,ミド,牡,5,2021/05/01,父C,母父A,騎4,470,0,3,1:28.5,2\n')
PB = ('競馬場,競走年月日,レース番号,単勝組番,単勝払戻金（円）,複勝組番1,複勝払戻金1（円）,複勝組番2,複勝払戻金2（円）\n'
      '大井,2026/10/01,1,1,150,1,110,2,130\n'
      '大井,2026/10/15,1,2,560,2,180,1,110\n')


def races():
    return hs.from_nar_csv(RL.encode('cp932'), HL.encode('cp932'), PB)


def test_nar_adapter_and_corners():
    r = races()
    a = r['OHI_20261001_R01']
    assert a['distance'] == 1200 and a['going'] == '良' and len(a['runners']) == 4
    assert a['first_corner'] == {1: 1, 2: 2, 3: 2, 4: 4}
    b = r['OHI_20261015_R01']
    assert [x['status'] for x in b['runners']].count('SCRATCH') == 1
    assert b['payouts']['WIN'] == {'2': 560}


def test_starts_use_only_earlier_history():
    rows = hs.starts(races())
    first = [x for x in rows if x['date'] == '2026-10-01']
    assert all(x['prev_dist'] is None and x['days_since'] is None for x in first)
    ao = [x for x in rows if x['date'] == '2026-10-15' and x['no'] == 1][0]
    assert ao['prev_dist'] == 1200 and ao['days_since'] == 14
    assert all(x['no'] != 3 for x in rows if x['date'] == '2026-10-15')     # scratched horse is not a start


def test_tables_have_counts_rates_roi_and_flags():
    st = hs.build(races(), 'TEST')
    pop1 = [c for c in st['tables']['T2_POP'] if c['conditions']['pop'] == '1']
    assert sum(c['starts'] for c in pop1) == 2
    c = [c for c in pop1 if c['conditions']['band'] == 'S'][0]
    assert (c['n1'], c['starts'], c['roi_win'], c['roi_place']) == (1, 1, 1.5, 1.1)
    assert c['small_sample'] and c['win_ci95'][0] < 1
    base = st['tables']['T1_BASE'][0]
    assert base['fav_win'] is not None and base['conditions']['class'] == 'C2'
    assert st['leakage_note'].startswith('popularity')
    assert 'SHORTER' not in str(st['tables']['T5_DIST_CHANGE']) and 'LONGER' in str(st['tables']['T5_DIST_CHANGE'])
    assert hs.md(st).startswith('# 地方 統計表')


def test_runner_cells_unknown_and_class_codes():
    st = hs.build(races(), 'TEST')
    cells = hs.runner_cells(st, 'KNZ', 1400, '良', 10, 3, 2)
    assert all(c.get('status') == 'UNKNOWN_NO_CELL' for c in cells)
    assert hs.class_code('C2三') == 'C2' and hs.class_code('2歳') == '2YO' and hs.going_class('稍重') == 'DAMP'


def test_bh_and_time_split():
    cells = [{'expected_top3': 10.0, 'starts': 40, 'n1': 10, 'n2': 6, 'n3': 4}, {'expected_top3': 10.0, 'starts': 40, 'n1': 4, 'n2': 3, 'n3': 3}]
    q = hs.bh_qvalues(cells)
    assert q[0] < q[1] or q[0] < 0.05
    a, b = hs.time_split(races(), '2026-10-10')
    assert list(a) == ['OHI_20261001_R01'] and list(b) == ['OHI_20261015_R01']

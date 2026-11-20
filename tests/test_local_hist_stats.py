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


def test_youtube_claim_tables_jockey_last3f_lead_repeat_special():
    rl = ('競馬場,競走年月日,レース番号,芝ダート区分,距離,天候,馬場,頭数,条件,コーナー通過順1,コーナー通過順2\n'
          '高知,2026/10/01,12,ダ,1300,晴,重,3,一発逆転ファイナルレース,"1,2,3","1,2,3"\n'
          '高知,2026/10/08,12,ダ,1300,晴,良,3,C3,"2,1,3","3,1,2"\n')
    hl = ('競馬場,競走年月日,レース番号,枠番,馬番,馬名,性,齢,生年月日,父馬名,母父馬名,騎手名,馬体重,馬体重増減,着順,タイム,人気,上がり3F\n'
          '高知,2026/10/01,12,1,1,アオ,牡,3,2023/03/01,父A,母父A,宮川,450,0,1,1:23.5,2,40.1\n'
          '高知,2026/10/01,12,2,2,アカ,牝,3,2023/04/01,父B,母父B,永森,440,2,2,1:23.8,1,39.8\n'
          '高知,2026/10/01,12,3,3,キイ,牡,4,2022/05/01,父A,母父C,赤岡,460,-2,3,1:24.0,3,40.5\n'
          '高知,2026/10/08,12,1,1,アオ,牡,3,2023/03/01,父A,母父A,宮川,452,2,2,1:23.0,1,39.9\n'
          '高知,2026/10/08,12,2,2,アカ,牝,3,2023/04/01,父B,母父B,永森,440,0,1,1:22.9,2,39.5\n'
          '高知,2026/10/08,12,3,3,キイ,牡,4,2022/05/01,父A,母父C,赤岡,460,0,3,1:23.5,3,40.0\n')
    pb = '競馬場,競走年月日,レース番号,単勝組番,単勝払戻金（円）\n高知,2026/10/01,12,1,420\n高知,2026/10/08,12,2,330\n'
    st = hs.build(hs.from_nar_csv(rl, hl, pb), 'TEST')
    t = st['tables']
    j = [c for c in t['T6_JOCKEY'] if c['conditions']['jockey'] == '宮川'][0]
    assert (j['starts'], j['n1']) == (2, 1)
    f = [c for c in t['T7_LAST3F'] if c['conditions']['fastest_last3f'] is True]
    assert sum(c['starts'] for c in f) == 2 and all(c['conditions']['last_corner_band'] == '1-3' for c in f)
    lr = t['T8_LEAD_REPEAT']                       # アオ led 10/01, did not lead 10/08
    assert len(lr) == 1 and (lr[0]['starts'], lr[0]['led_again']) == (1, 0) and lr[0]['conditions']['special'] == 'NORMAL'
    sp = {c['conditions']['special'] for c in t['T9_SPECIAL']}
    assert sp == {'KOC_FINAL', 'NORMAL'}
    assert hs.special_flag('OHI', '一発逆転') == 'NORMAL' and hs._f3('99.9') is None


def test_ohi_course_change_table():
    st = hs.build(races(), 'TEST')                 # fixture: OHI 1200 (OUTER) then 1400 (OUTER)
    c = st['tables']['T5_OHI_COURSE']
    assert c and all(x['conditions'] == {'venue': 'OHI', 'course': 'OUTER', 'previous_course': 'OUTER'} for x in c)
    assert hs.ohi_course(1600) == 'INNER' and hs.ohi_course(1650) == 'LEFT' and hs.ohi_course(None) is None


def test_mon_course_family():
    assert hs.mon_course(1600) == 'INNER' and hs.mon_course(1500) == 'INNER'
    assert hs.mon_course(1700) == 'OUTER' and hs.mon_course(1200) == 'OUTER' and hs.mon_course(None) is None
    st = hs.build(races(), 'TEST')                 # fixture has no MON starts -> empty table, no crash
    assert st['tables'].get('T5_MON_COURSE', []) == []


def test_crz_mpa_direct_tables():
    st = hs.build(races(), 'TEST')
    t = st['tables']
    crz = {(c['conditions']['band'], c['conditions']['class'], c['conditions']['last_corner_pos(6=6+)']): c for c in t['T10_CRZ']}
    assert crz[('S', 'C2', 1)]['n1'] == 1 and crz[('M', 'C2', 2)]['n2'] == 1 and crz[('M', 'C2', 4)]['n3'] == 1
    mpa = t['T11_MPA']
    assert [c['conditions']['max_gain_prev5'] for c in mpa] == ['GAIN<=0'] and mpa[0]['starts'] == 3
    d = {(c['conditions']['same_venue_distance_win_before'], c['conditions']['last_finish']): c['starts'] for c in t['T12_DIRECT']}
    assert d == {(False, '1-3'): 2, (False, '4-6'): 1}      # first starts (no history) are excluded
    rows = hs.starts(races())
    ao2 = [x for x in rows if x['date'] == '2026-10-15' and x['no'] == 1][0]
    assert ao2['mpa_gain'] == 0 and ao2['last_finish'] == 1 and ao2['direct_win'] is False
    assert hs.mpa_band(6) == 'GAIN6+' and hs.finish_band(7) == '7+' and hs.finish_band(None) is None


def test_pop_going_order_shuffle_and_returnee_tables():
    import copy
    st = hs.build(races(), 'TEST')
    t = st['tables']
    g = {(c['conditions']['going'], c['conditions']['pop']) for c in t['T13_POP_GOING']}
    assert {c['conditions']['going'] for c in t['T13_POP_GOING']} == {'良', '重'} or len(g) >= 2
    sh = t['T14_ORDER_SHUFFLE']
    assert sum(c['races'] for c in sh) == 2 and sum(c['top3_all_pop123'] for c in sh) == 2
    assert sum(c['order_not_popularity_given_pop123'] for c in sh) == 1     # 10/15: pop3 -> pop1 -> pop2
    assert sum(c['pop1_win_given_pop123'] for c in sh) == 1
    # 出戻り: OHI -> KSM -> OHI is RETURN; OHI -> KSM is NEW_MOVE; 南関 rotation is SAME
    r = races()
    a, b = r['OHI_20261001_R01'], r['OHI_20261015_R01']
    k = copy.deepcopy(a)
    k.update(race_id='KAW_20261008_R01', date='2026-10-08', venue='KAW')
    rows = hs.starts({'a': a, 'k': k, 'b': b})
    mv = {(x['venue'], x['date']): x['move'] for x in rows if x['no'] == 1}
    assert mv[('OHI', '2026-10-01')] is None
    k2 = copy.deepcopy(k)
    k2.update(venue='KSM', race_id='KSM_20261008_R01')
    rows = hs.starts({'a': a, 'k': k2, 'b': b})
    mv = {(x['venue'], x['date']): x['move'] for x in rows if x['no'] == 1}
    assert mv[('KSM', '2026-10-08')] == 'NEW_MOVE' and mv[('OHI', '2026-10-15')] == 'RETURN'
    assert {c['conditions']['move'] for c in hs.build({'a': a, 'k': k2, 'b': b}, 'T')['tables']['T15_RETURNEE']} == {'NEW_MOVE', 'RETURN'}
    # 南関 rotation (OHI -> KAW -> OHI) is the same circuit, not a move
    assert {x['move'] for x in hs.starts({'a': a, 'k': k, 'b': b}) if x['no'] == 1} == {None, 'SAME'}


def test_urw_v16_claim_tables_fnb_aged_fav_frame():
    import copy
    r = races()
    a, b = r['OHI_20261001_R01'], r['OHI_20261015_R01']
    f = copy.deepcopy(a)
    f.update(race_id='FNB_20261001_R01', venue='FNB', distance=1500)
    u = copy.deepcopy(b)
    u.update(race_id='URW_20261015_R01', venue='URW', distance=1400)
    for x in u['runners']:
        if x['no'] == 1:
            x['age'] = 8
    st = hs.build({'f': f, 'u': u}, 'T')
    t = st['tables']
    fn = t['T16_URW_FROM_FNB']
    assert {c['conditions']['previous_fnb_distance'] for c in fn} == {'FNB1500/1800'}
    assert {c['conditions']['distance_change'] for c in fn} == {'SHORTER'}
    assert sum(c['starts'] for c in fn) == 3                                 # scratched horse 3 is not a start
    front = [c for c in fn if c['conditions']['previous_last_corner'] == 'LC<=3']
    assert sum(c['starts'] for c in front) == 2                              # last corner 1,2,3,4 at FNB: 1 and 2 ran
    ag = t.get('T17_AGED_FRONT_FAV', [])
    # URW 1400m < 1500m -> not in T17
    assert ag == []
    u2 = copy.deepcopy(u)
    u2['distance'] = 1500
    ag = hs.build({'f': f, 'u': u2}, 'T')['tables']['T17_AGED_FRONT_FAV']
    keys = {(c['conditions']['age'], c['conditions']['previous_start'], c['conditions']['days_since_last']) for c in ag}
    # horse 1: age 8, pop 1, prev 1角1番手 1着 -> OTHER; horse 4: pop 2, age 5, prev 1角4番手 -> OTHER
    assert keys == {('7+', 'OTHER', '8-14d'), ('<=6', 'OTHER', '8-14d')}
    fr = t['T18_FAV_FRAME']
    assert all(c['conditions']['venue'] in ('FNB', 'URW') for c in fr)
    assert sum(c['starts'] for c in fr) == 4                                 # pop1-2 in two races
    assert hs.md(st).startswith('# 地方 統計表')

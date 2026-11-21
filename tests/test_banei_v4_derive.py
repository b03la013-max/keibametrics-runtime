import sys

sys.path.insert(0, 'runtime/banei_autopilot')
import derive  # noqa: E402
import engine  # noqa: E402


def _r(**k):
    base = {'no': 1, 'name': 'A', 'jockey': '阿部武臣', 'body_delta': -4, 'body_weight': 1000,
            'starts': [{'finish': 5, 'jockey': '阿部武', 'race_name': 'C2-1', 'body_weight': 1004, 'date': '26.11.14'},
                       {'finish': 6, 'jockey': '阿部武', 'race_name': 'C2-1', 'body_weight': 1010, 'date': '26.10.31'}]}
    base.update(k)
    return base


def test_jbr_needs_barrier_jockey_and_counts_support():
    kin = {'front_ok': True, 'grades': {'front': 'B', 'kick': 'C'}, 'past': [{'date': '11/14', 'moisture': 1.3}]}
    f = derive.horse_inputs(_r(), kin, {}, [], set(), 'C2-1', 'DRY')
    assert f['jbr_hits'] == []                                   # 障害巧者でなければ加点なし
    f = derive.horse_inputs(_r(starts=[{'finish': 2, 'jockey': '阿部武', 'race_name': 'C2-1', 'date': '26.11.14'}]),
                            kin, {}, [], {'阿部武'}, 'C2-1', 'DRY')
    assert f['jbr_hits'] == ['BARRIER_JOCKEY', 'SAME_HORSE_GOOD', 'CAN_GO_FORWARD']


def test_bwl_signals_cpu_and_moisture_fill():
    r = _r()
    kin = {'grades': {'front': 'A', 'kick': 'D'}, 'past': [{'date': '11/14', 'moisture': 1.3}]}
    f = derive.horse_inputs(r, kin, {'cci': 'CAUTION'}, [], set(), 'B4-1', 'DRY')
    assert f['state_bad'] and f['consecutive_loss'] and f['comment_weak']
    assert f['promoted'] and not f['win_streak'] and f['front_type'] and f['fades_after_barrier']
    assert r['starts'][0]['moisture'] == 1.3 and r['starts'][1]['moisture'] is None


def test_pace_and_adf_dry_premise():
    hs = [{'front_type': True, 'front_ok': True}, {'front_type': True, 'front_ok': True},
          {'front_type': False, 'front_ok': False}]
    assert derive.race_pace(hs) == 'H'
    assert derive.race_pace([{'front_type': False, 'front_ok': True}]) == 'S'
    h = {'age': 9, 'load': 700, 'body_delta': -5, 'front_type': True}
    assert engine.adf(h, {'moisture': 1.2, 'pace': 'H'})[1] == 5
    assert engine.adf(h, {'moisture': 3.0, 'pace': 'H'}) == (0.0, 0)          # 乾燥馬場が前提


def test_bwl_pct_neutral():
    h = {'body_weight': 1000, 'body_delta': 5, 'body_delta_pct': 0.5, 'good_bw_range': (900, 950)}
    assert engine.bwl(h) == (0.0, 'NEUTRAL_PCT')


def test_promoted_from_kintaro_class_and_picks_comment_pass_through():
    kin = {'grades': {}, 'past': [{'date': '11/14', 'race_class': 'C2-1'}], 'picks': 2, 'comment': '障害修正できれば'}
    f = derive.horse_inputs(_r(starts=[]), kin, {}, [], set(), 'C1-3', 'WET')
    assert f['promoted'] and not f['demoted'] and f['last_class'] == 'C2'
    assert f['kintaro_picks'] == 2 and f['kintaro_comment'] == '障害修正できれば'
    f = derive.horse_inputs(_r(starts=[]), dict(kin, past=[{'date': '11/14', 'race_class': 'C1-4'}]), {}, [], set(), 'C2-1', 'WET')
    assert f['demoted'] and not f['promoted']

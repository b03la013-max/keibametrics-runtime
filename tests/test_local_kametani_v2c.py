"""SHADOW 亀谷 v2 corrections (Drive 精読 2026-11-21): v2 untouched, corrected copy reports changes only."""
import json

from runtime.local_autopilot import bloodline_kametani as bk
from runtime.local_autopilot import kametani_v2c as kc

RACE = {'surface': 'DIRT', 'distance': 1600, 'going': '良', 'race_date': '2026-11-21', 'venue_id': 'OHI'}


def H(no, sire, damsire, age=4, sex='牡', pop=5, starts=None):
    return {'horse_no': no, 'sire': sire, 'damsire': damsire, 'sex_age': f'{sex}{age}', 'age': age,
            'popularity': pop, 'frame_no': 4, 'starts': starts if starts is not None else
            [{'finish': 7, 'distance': 1600, 'surface': 'DIRT', 'content_positions': [8], 'field_size': 12,
              'date': '26.10.20'}]}


def R(**kw):
    return {**RACE, **kw}


def test_v2_table_not_modified():
    before = json.dumps(bk.table(), ensure_ascii=False, sort_keys=True)
    for e in list(bk.table().values()):
        kc.corrected_entry(e)
    assert json.dumps(bk.table(), ensure_ascii=False, sort_keys=True) == before


def test_023_ss_caution_is_turf_only():
    ev = kc.evaluate(H(1, 'タワーオブロンドン', 'キズナ'), R(distance=1400))
    assert ev['sire']['base_caution'] is True and ev['sire']['corr_caution'] is False and ev['changed']


def test_039_born_year_from_age():
    old = kc.evaluate(H(1, 'キズナ', 'ヘニーヒューズ', age=6), R(distance=1800))
    young = kc.evaluate(H(2, 'キズナ', 'ヘニーヒューズ', age=5), R(distance=1800))
    assert old['sire']['base_buy'] is False and old['sire']['corr_buy'] is True
    assert young['sire']['corr_buy'] is False


def test_052_needs_last_turf_or_top3():
    lost = kc.evaluate(H(1, 'モーリス', 'ハービンジャー', pop=2), R())
    assert lost['sire']['base_caution'] is True and lost['sire']['corr_caution'] is False
    top = H(2, 'モーリス', 'ハービンジャー', pop=2)
    top['starts'][0]['finish'] = 2
    assert kc.evaluate(top, R())['sire']['corr_caution'] is True


def test_094_short_gap_placed_favourite():
    h = H(1, 'ヨハネスブルグ', 'ヘニーヒューズ', age=5, pop=1)
    h['starts'][0].update(finish=3, date='26.11.07')
    assert kc.evaluate(h, R(distance=1400))['sire']['corr_caution'] is True
    h['starts'][0].update(date='26.10.01')          # 51 days: not 中3週以内 (but 1400 old fav caution still holds)
    ev = kc.evaluate(h, R(distance=1500))
    assert ev['sire']['corr_caution'] is False


def test_075_us_or_mipro_damsire():
    us = kc.evaluate(H(1, 'ドレフォン', 'ヘニーヒューズ'), R())
    eu = kc.evaluate(H(2, 'ドレフォン', 'ノヴェリスト'), R())
    assert us['sire']['corr_buy'] is True
    assert eu['sire']['corr_buy'] is False and 0 in eu['sire']['corr_unknown_buy']   # ミスプロ系か読めない


def test_072_damsire_deep_old_short_favourite():
    ev = kc.evaluate(H(1, 'ノーエントリー', 'ディープインパクト', age=5, pop=2), R(distance=1200))
    assert ev['damsire']['caution'] is True and ev['changed'] and 'sire' not in ev
    assert kc.evaluate(H(2, 'ノーエントリー', 'ディープインパクト', age=3, pop=2), R(distance=1200))['damsire']['caution'] is False


def test_race_evidence_shape_and_no_production_effect():
    out = kc.race_evidence(R(distance=1400), [H(1, 'タワーオブロンドン', 'キズナ'), H(2, 'ノーエントリー', 'X')])
    assert out['production_effect'].startswith('NONE') and out['changed'] == ['1'] and out['evaluated'] == 1
    assert set(out['patches']) >= {'C1', 'C7', 'C9'}


def test_unpatched_sire_returns_none():
    assert kc.evaluate(H(1, 'シニスターミニスター', 'ヘニーヒューズ'), R()) is None

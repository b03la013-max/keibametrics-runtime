"""Article raw-unit arithmetic, without a new Component scoring policy."""
from datetime import date
from decimal import Decimal

from runtime.local_base63_source_witness import defined_raw_formula_witness


def horse(current=449, change=-1, previous=450):
    return {'1': {'body_weight': current, 'body_weight_change': change,
        'history': [{'date': date(2026, 9, 1), 'body_weight': previous,
                     'finish': 2, 'field_size': 12}]}}


def test_exact_weight_percentage_and_points_do_not_create_scores():
    result = defined_raw_formula_witness(horse(), '2026-10-02')
    metric = result['bodyweight_rows'][0]
    assert abs(Decimal(metric['weight_change_percentage']) - Decimal(-2)/9) < Decimal('1e-27')
    assert result['history_point_rows'][0]['article67_finish_points'] == 3
    assert metric['component_score'] is None and metric['weight_change_reason'] is None
    assert result['new_component_scores'] == result['missing15_closed'] == 0
    assert result['prediction_consumption_authorized'] is False


def test_unknown_weight_is_not_zero_and_conflict_stays_hold():
    assert defined_raw_formula_witness(horse(current=None), '2026-10-02')['bodyweight_unknown'] == 1
    assert defined_raw_formula_witness(horse(current=0, change=-450), '2026-10-02')['bodyweight_unknown'] == 1
    out = defined_raw_formula_witness(horse(previous=444), '2026-10-02')
    assert out['bodyweight_hold'] == 1
    assert out['bodyweight_rows'][0]['weight_change_percentage'] is None


def test_latest_prior_race_not_input_order_or_future_row():
    h = horse()
    h['1']['history'].append({'date': date(2026, 10, 1), 'body_weight': 450,
                             'finish': 1, 'field_size': 12})
    h['1']['history'].insert(0, {'date': date(2026, 10, 3), 'body_weight': 900,
                               'finish': 1, 'field_size': 12})
    out = defined_raw_formula_witness(h, '2026-10-02')
    assert out['bodyweight_rows'][0]['previous_race_date'] == '2026-10-01'
    assert len(out['history_point_rows']) == 2


def test_invalid_finish_does_not_become_zero_observation():
    h = horse()
    h['1']['history'][0]['finish'] = 0
    row = defined_raw_formula_witness(h, '2026-10-02')['history_point_rows'][0]
    assert row['status'] == 'UNKNOWN' and row['article67_finish_points'] is None


def test_points_follow_explicit_5_3_2_without_invented_other_finish_points():
    for rank, expected in [(1, 5), (2, 3), (3, 2), (4, None), (12, None)]:
        h = horse()
        h['1']['history'][0]['finish'] = rank
        assert defined_raw_formula_witness(h, '2026-10-02')['history_point_rows'][0]['article67_finish_points'] == expected

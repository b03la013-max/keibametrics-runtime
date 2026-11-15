from datetime import date, timedelta

import pytest

from research.local_bvi.distance_diagnostic import evaluate_distance


def race(day, distance, finish, **updates):
    row = {
        "venue": "川崎", "race_date": day, "race_no": distance,
        "surface": "DIRT", "going": "良", "race_kind": "普通",
        "conditions": "サラブレッド系 一般 定量", "distance": distance,
        "has_payback": True, "observed_at": "2025-12-01T00:00:00+09:00",
        "scheduled_at": day + "T14:00:00+09:00",
        "runners": [{"sire": "父Ａ", "finish": finish}]
        + [{"sire": "父Ｂ", "finish": rank} for rank in range(1, 5) if rank != finish],
    }
    return row | updates


def card(**updates):
    return race("2026-11-16", 900, 4, **({"has_payback": False, "runners": [{"sire": "父Ａ"}]} | updates))


def test_distance_estimate_uses_only_comparable_prior_results():
    start = date(2025, 8, 1)
    history = []
    for offset in range(30):
        day = (start + timedelta(days=offset)).isoformat()
        history += [race(day, 900, 1), race(day, 1400, 4)]
    history += [race("2025-10-01", 900, 4, going="重"),
                race("2026-11-15", 900, 4),
                race("2025-10-02", 900, 4, observed_at="2026-11-16T00:00:00+09:00"),
                race("2025-10-03", 900, 4, has_payback=False)]
    target = card()
    result, = evaluate_distance(history, [target], as_of="2026-11-15T22:30:00+09:00")
    candidate = result["sires"]["父A"]
    assert candidate["same_distance_races"] == 30
    assert candidate["other_distance_races"] == 30
    assert candidate["effect_pp"] == 100
    assert candidate["approximate_95_interval_pp"] == [100, 100]
    assert result["formal_bvi"] == 52
    assert not result["prediction_authority"]


def test_missing_going_and_small_sample_do_not_infer_distance_effect():
    target = card(going=None)
    result, = evaluate_distance([race("2025-08-01", 900, 1)], [target],
                                as_of="2026-11-15T22:30:00+09:00")
    assert result["sires"]["父A"]["status"] == "INSUFFICIENT_COMPARABLE_RACES"
    assert result["sires"]["父A"]["effect_pp"] is None
    with pytest.raises(ValueError, match="AS_OF_REQUIRED"):
        list(evaluate_distance([], [target], as_of="2026-11-15"))


@pytest.mark.parametrize("target", [card(race_date="2026-11-14", scheduled_at="2026-11-14T14:00:00+09:00"),
                                    card(observed_at="2026-11-16T00:00:00+09:00"),
                                    card(has_payback=True), card(runners=[{"sire": "父Ａ", "finish": 1}])])
def test_does_not_score_past_targets_future_revisions_or_results(target):
    with pytest.raises(ValueError, match="PRESTART_TARGET_REQUIRED"):
        list(evaluate_distance([target], [target], as_of="2026-11-15T22:30:00+09:00"))

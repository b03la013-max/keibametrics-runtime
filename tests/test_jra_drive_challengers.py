"""DRIVE01 recorded challengers (Drive 精読 2026-11-22). NON-PRODUCTION shadow candidates only."""
import copy, json, sys
from pathlib import Path
sys.path.insert(0, "runtime/analysis")
import jra_role_candidate_replay as rc

RID = "KM-JRA-TKY-20261115-R11"
DRIVE = ["P3_SHORTEN_SPRINT_FRONT", "P3_SHORTEN_SAME_COUNT_CONTROL", "P3_FIRST_DIRT_BIG_OUTER_FRONT",
         "P3_FIRST_DIRT_SAME_COUNT_CONTROL", "W_WIND8_MARKET_TOP3", "W_WIND8_STATIC_SAME_COUNT_CONTROL"]


def _final():
    return json.loads(Path(f"runtime/final_artifacts/{RID}.json").read_text())


def test_drive_candidates_registered_with_controls():
    assert all(k in rc.CANDIDATES for k in DRIVE)
    prereg = json.loads(Path("profiles/KM_JRA_FORWARD_OOS_PREREG_20261128_DRIVE01.json").read_text())
    assert prereg["production_effect"] == "NONE"
    assert {a["id"] for a in prereg["arms"]} == set(DRIVE)


def test_shorten_sprint_front_rule():
    ctx = {"distance_m": 1200, "surface": "芝"}
    r = {"recent_runs": [{"distance_m": 1600, "field_size": 16, "passing_positions": [5, 6]},
                         {"distance_m": 1800, "field_size": 12, "passing_positions": [9, 9]}]}
    assert rc.shorten_sprint_front(ctx, r)
    assert not rc.shorten_sprint_front({"distance_m": 1600}, r)            # not a sprint today
    r2 = copy.deepcopy(r); r2["recent_runs"].append({"distance_m": 1400, "field_size": 16, "passing_positions": [1]})
    assert not rc.shorten_sprint_front(ctx, r2)                           # already ran <= 1400m
    r3 = copy.deepcopy(r); r3["recent_runs"][0]["passing_positions"] = [12, 12]
    assert not rc.shorten_sprint_front(ctx, r3)                           # was not forward last time


def test_first_dirt_big_outer_front_rule():
    ctx = {"surface": "ダ"}
    r = {"horse_no": 12, "current_body_weight": 470,
         "recent_runs": [{"surface": "芝", "field_size": 16, "passing_positions": [3, 4]}]}
    assert rc.first_dirt_big_outer_front(ctx, r, 16)
    assert not rc.first_dirt_big_outer_front({"surface": "芝"}, r, 16)
    assert not rc.first_dirt_big_outer_front(ctx, {**r, "horse_no": 4}, 16)          # inner half
    assert not rc.first_dirt_big_outer_front(ctx, {**r, "current_body_weight": 450}, 16)
    r2 = copy.deepcopy(r); r2["recent_runs"].append({"surface": "ダ", "field_size": 16, "passing_positions": [1]})
    assert not rc.first_dirt_big_outer_front(ctx, r2, 16)                 # not first dirt


def test_card_and_wind_only_before_cutoff(tmp_path):
    final = _final()
    assert rc.race_card(final) is not None
    rq = json.loads(Path(f"runtime/requests/{RID}-LIVE-R1-FORMAL.json").read_text())
    rq["source_snapshot"]["source_freeze_at"] = "2099-01-01T00:00:00+00:00"
    (tmp_path / "runtime/requests").mkdir(parents=True)
    (tmp_path / f"runtime/requests/{RID}-LIVE-R1-FORMAL.json").write_text(json.dumps(rq))
    assert rc.race_card(final, root=tmp_path) is None and rc.jma_wind(final, root=tmp_path) is None


def test_wind_candidate_and_control_fire_in_same_races_with_same_count():
    final = _final()
    w = rc.jma_wind(final)
    a, b = copy.deepcopy(final), copy.deepcopy(final)
    fa, fb = rc.w_wind8_market_top3(a), rc.w_wind8_static_same_count_control(b)
    assert fa == fb
    if w is None or w < rc.WIND_MS:
        assert not fa
    assert len(rc._live(a, "W")) == len(rc._live(b, "W"))


def test_p3_candidates_and_controls_add_same_count():
    final = _final()
    for cand, ctrl in [("P3_SHORTEN_SPRINT_FRONT", "P3_SHORTEN_SAME_COUNT_CONTROL"),
                       ("P3_FIRST_DIRT_BIG_OUTER_FRONT", "P3_FIRST_DIRT_SAME_COUNT_CONTROL")]:
        a, b = copy.deepcopy(final), copy.deepcopy(final)
        fa, fb = rc.CANDIDATES[cand](a), rc.CANDIDATES[ctrl](b)
        assert fa == fb
        assert len(rc._live(a, "P3")) == len(rc._live(b, "P3"))

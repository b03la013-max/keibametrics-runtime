import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime/analysis")); sys.path.insert(0, str(ROOT / "runtime"))
import jra_rev2_shadow as R2

JST = dt.timezone(dt.timedelta(hours=9))
FINAL = {"sha256": "x", "scheduled_post_at": "2026-11-28T10:05:00+09:00",
         "final_prediction_package": {"ranking": ["3", "1", "2", "4"],
                                      "roles": {"3": ["W", "P2", "P3"], "1": ["P2", "P3"], "2": ["P3"], "4": []}},
         "final_ticket": {"frozen_at": "t", "no_bet": False, "tickets": [
             {"bet_type": "EXACTA", "selection": [3, 1], "stake": 100},
             {"bet_type": "EXACTA", "selection": [3, 2], "stake": 100}]}}


def test_withdrawal_makes_rev2_without_touching_rev1():
    import copy
    f = copy.deepcopy(FINAL)
    rec = R2.build("KM-JRA-TKY-20261128-R01", f, "obs", [{"type": "競走除外", "horse_no": 2}], dt.datetime(2026, 11, 28, 9, 55, tzinfo=JST))
    assert rec["material"] and rec["withdrawn"] == [2]
    assert rec["rev2"]["ranking"] == ["3", "1", "4"] and "2" not in rec["rev2"]["roles"]
    assert rec["rev2"]["removed_tickets"] == 1 and rec["rev2"]["investment"] == 100
    assert f == FINAL and rec["production_effect"] == "NONE"


def test_jockey_change_is_recorded_but_not_material():
    rec = R2.build("KM-JRA-TKY-20261128-R01", FINAL, "obs", [{"type": "騎手変更", "horse_no": 1}], dt.datetime(2026, 11, 28, 9, 55, tzinfo=JST))
    assert not rec["material"] and "rev2" not in rec and rec["other_changes"]
    assert rec["body_weight_odds"] == "NOT_OBSERVED_BY_V1"


def test_notice_lookup_maps_meeting_name_to_venue(tmp_path, monkeypatch):
    monkeypatch.setattr(R2, "ROOT", tmp_path)
    d = tmp_path / "runtime/jra_official_daily"; d.mkdir(parents=True)
    (d / "2026-11-28.json").write_text(json.dumps({"observations": [{"observed_at": "a", "last_seen_at": "b", "notices": {
        "meetings": [{"meeting": "5回東京7日", "races": {"1": [{"type": "出走取消", "horse_no": 4}]}},
                     {"meeting": "5回京都7日", "races": {"1": []}}]}}]}, ensure_ascii=False))
    at, n = R2.notices_for("2026-11-28", "KM-JRA-TKY-20261128-R01")
    assert at == "b" and n[0]["horse_no"] == 4
    assert R2.notices_for("2026-11-28", "KM-JRA-KYO-20261128-R01")[1] == []


def test_check_writes_once_inside_the_window_only(tmp_path, monkeypatch):
    monkeypatch.setattr(R2, "ROOT", tmp_path); monkeypatch.setattr(R2, "OUT", tmp_path / "runtime/jra_rev2_shadow")
    rid = "KM-JRA-TKY-20261128-R01"
    (tmp_path / "runtime/jra_race_day_status").mkdir(parents=True)
    (tmp_path / "runtime/jra_race_day_status/2026-11-28.json").write_text(json.dumps({"races": [{"race_id": rid, "post": "2026-11-28T10:05:00+09:00"}]}))
    (tmp_path / "runtime/final_artifacts").mkdir(parents=True)
    (tmp_path / f"runtime/final_artifacts/{rid}.json").write_text(json.dumps(FINAL))
    (tmp_path / "runtime/jra_official_daily").mkdir(parents=True)
    (tmp_path / "runtime/jra_official_daily/2026-11-28.json").write_text(json.dumps({"observations": [{"observed_at": "a", "notices": {"meetings": [{"meeting": "5回東京7日", "races": {"1": []}}]}}]}, ensure_ascii=False))
    assert R2.check("2026-11-28", dt.datetime(2026, 11, 28, 9, 40, tzinfo=JST)) == []
    assert R2.check("2026-11-28", dt.datetime(2026, 11, 28, 9, 56, tzinfo=JST)) == [{"race_id": rid, "material": False}]
    assert R2.check("2026-11-28", dt.datetime(2026, 11, 28, 9, 58, tzinfo=JST)) == []
    assert R2.check("2026-11-28", dt.datetime(2026, 11, 28, 10, 6, tzinfo=JST)) == []

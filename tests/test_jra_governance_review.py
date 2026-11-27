import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime/analysis"))
import jra_governance_review as G  # noqa: E402


def _race(tmp, rid, roles, ranking, tickets, top3, inv, pay, krs=None, no_bet=False, freeze="2026-11-28T00:00:00+00:00"):
    (tmp / "runtime/final_artifacts").mkdir(parents=True, exist_ok=True)
    (tmp / "runtime/results").mkdir(parents=True, exist_ok=True)
    (tmp / f"runtime/final_artifacts/{rid}.json").write_text(json.dumps({
        "sha256": "s", "scheduled_post_at": "2026-11-28T10:05:00+09:00", "final_freeze_timestamp": freeze,
        "final_prediction_package": {"ranking": ranking, "roles": roles},
        "final_ticket": {"no_bet": no_bet, "tickets": tickets},
        "krs_prediction_utility": {"summary": [{"horse_no": int(h), "ranks": {"SSR-W": r}} for h, r in (krs or {}).items()]}}))
    (tmp / f"runtime/results/{rid}.json").write_text(json.dumps({
        "official_result": {"top3": top3}, "settlement": {"effective_investment": inv, "total_payout": pay}}))


def test_challenges_cover_role_krs_and_decision_layers(tmp_path):
    rid = "KM-JRA-TKY-20261128-R01"
    roles = {"1": ["W", "P2", "P3"], "2": ["P2", "P3"], "3": ["P3"], "4": []}
    _race(tmp_path, rid, roles, ["1", "2", "3", "4"], [{"bet_type": "EXACTA", "selection": [1, 3], "stake": 100}],
          ["2", "4", "3"], 100, 0, krs={"2": 1})
    c = {x["code"] for x in G.challenges(tmp_path, rid)["challenges"]}
    assert {"TOP3_WINNER_NOT_W", "KRS_SIGNAL_NOT_IN_ROLE", "SECOND_NOT_P2"} <= c
    assert "THIRD_NOT_P3" not in c and "W_CORRECT_NO_WINNING_TICKET" not in c


def test_w_correct_but_no_winning_ticket_and_hit_but_loss(tmp_path):
    roles = {"1": ["W", "P2", "P3"], "2": ["P2", "P3"], "3": ["P3"]}
    _race(tmp_path, "KM-JRA-TKY-20261128-R02", roles, ["1", "2", "3"],
          [{"bet_type": "EXACTA", "selection": [1, 3], "stake": 100}], ["1", "2", "3"], 100, 0)
    assert "W_CORRECT_NO_WINNING_TICKET" in {x["code"] for x in G.challenges(tmp_path, "KM-JRA-TKY-20261128-R02")["challenges"]}
    _race(tmp_path, "KM-JRA-TKY-20261128-R03", roles, ["1", "2", "3"],
          [{"bet_type": "EXACTA", "selection": [1, 2], "stake": 100}] * 5, ["1", "2", "3"], 500, 300)
    codes = {x["code"] for x in G.challenges(tmp_path, "KM-JRA-TKY-20261128-R03")["challenges"]}
    assert "HIT_BUT_LOSS" in codes and "W_CORRECT_NO_WINNING_TICKET" not in codes


def test_freeze_after_post_is_p0_and_regression_only(tmp_path):
    _race(tmp_path, "KM-JRA-TKY-20261128-R04", {"1": ["W"]}, ["1"], [], ["1", "2", "3"], 0, 0, no_bet=True,
          freeze="2026-11-28T01:10:00+00:00")
    out = G.day(tmp_path, "2026-11-28")
    c = [x for r in out["races"] for x in r["challenges"] if x["code"] == "FREEZE_AFTER_POST"][0]
    assert c["severity"] == "P0" and c["purple"]["disposition"] == "REGRESSION-ONLY"
    assert out["independence"] == "LEVEL-1" and out["production_effect"] == "NONE"


def test_recurring_p1_without_candidate_becomes_shadow(tmp_path):
    for i in range(3):
        _race(tmp_path, f"KM-JRA-TKY-20261128-R1{i}", {"1": ["W", "P2", "P3"], "2": []}, ["1", "2"], [],
              ["2", "1", "3"], 0, 0, no_bet=True)
    out = G.day(tmp_path, "2026-11-28")
    disp = {x["purple"]["disposition"] for r in out["races"] for x in r["challenges"] if x["code"] == "TOP3_WINNER_NOT_W"}
    assert disp == {"SHADOW"} and "TOP3_WINNER_NOT_W" in out["summary"]["shadow_proposals"]

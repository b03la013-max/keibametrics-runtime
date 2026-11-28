import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime/analysis"))
import jra_multi_primary_shadow as M  # noqa: E402

H = [str(i) for i in (7, 3, 12, 1, 9, 5, 14, 2, 8, 4, 6, 10)]
TEXT = ("払戻金 単勝 9 2,120 円 8 番人気 複勝 9 290 円 6 番人気 11 140 円 2 番人気 10 530 円 12 番人気 "
        "14 110 円 1 番人気 枠連 5-6 2,420 円 9 番人気 馬連 9-11 4,970 円 16 番人気 馬単 9-11 12,810 円 42 番人気 "
        "ワイド 9-11 870 円 15 番人気 9-10 3,260 円 58 番人気 9-14 580 円 8 番人気 10-11 1,470 円 26 番人気 "
        "11-14 230 円 2 番人気 3連複 9-10-11 18,620 円 110 番人気 9-11-14 1,920 円 7 番人気 "
        "3連単 9-11-10 146,590 円 694 番人気 9-11-14 22,070 円 121 番人気 ページトップへ戻る")


def test_point_counts_match_spec_v11():
    want = {"1-2-4": 5, "1-2-6": 9, "1-3-7": 15, "1-4-8": 22, "2-3-6": 10, "2-4-7": 19, "BOX5": 10, "BOX6": 20}
    for k, n in want.items():
        assert len(M.trio_combos(M.trio_columns(k, H))) == n, k


def test_axis_table():
    assert M.trio_type(90, 10) == "1-2-4" and M.trio_type(90, 70) == "1-4-8"
    assert M.trio_type(70, 40) == "2-3-6" and M.trio_type(70, 55) == "1-3-7"
    assert M.trio_type(55, 20) == "2-3-6" and M.trio_type(55, 60) == "2-4-7"
    assert M.trio_type(40, 20) == "BOX5" and M.trio_type(40, 60) == "BOX6"


def test_same_budget_and_allocation():
    a = M.build_arm("MP-A", H, 90, 10, 0, 2000)
    assert a["investment"] == 2000
    assert a["units"] == {"TRIO": 10, "QUINELLA": 5, "WIDE": 3, "PLACE": 2}
    assert {t["bet_type"] for t in a["tickets"]} == {"TRIO", "QUINELLA", "WIDE", "PLACE"}
    assert all(t["stake"] % 100 == 0 and t["stake"] >= 100 for t in a["tickets"])
    small = M.build_arm("MP-A", H, 90, 10, 0, 300)
    assert small["investment"] == 300


def test_mp_b_order_only_with_absolute_stable_head():
    b = M.build_arm("MP-B", H, 90, 10, 20, 3000)
    assert b["exacta_order_rule_fired"] and b["investment"] == 3000
    assert all(t["selection"][0] == 7 for t in b["tickets"] if t["bet_type"] == "EXACTA")
    assert not M.build_arm("MP-B", H, 70, 10, 20, 3000)["exacta_order_rule_fired"]
    assert not M.build_arm("MP-B", H, 90, 10, 40, 3000)["exacta_order_rule_fired"]


def test_parse_all_payouts_dead_heat():
    p = M.parse_all_payouts(TEXT)
    assert len(p["PLACE"]) == 4 and len(p["WIDE"]) == 5 and len(p["TRIO"]) == 2
    assert p["QUINELLA"] == [{"selection": [9, 11], "per_100_yen": 4970}]
    assert p["TRIFECTA"][0]["per_100_yen"] == 146590


def test_settle_wide_place_and_refund():
    p = M.parse_all_payouts(TEXT)
    t = [{"bet_type": "WIDE", "selection": [11, 9], "stake": 200}, {"bet_type": "PLACE", "selection": [14], "stake": 100},
         {"bet_type": "TRIO", "selection": [1, 2, 3], "stake": 100}, {"bet_type": "QUINELLA", "selection": [9, 5], "stake": 100}]
    s = M.settle_tickets(t, p, [5])
    assert s["investment"] == 400 and s["refund"] == 100 and s["payout"] == 2 * 870 + 110
    assert s["by_type"]["WIDE"]["payout"] == 1740


def _final(tmp, rid, post, no_bet=False):
    f = {"race_id": rid, "scheduled_post_at": post, "sha256": "x",
         "final_prediction_package": {"ranking": H, "official_aki_verification": {"calculation": {
             "axes": {"ASI": 67.5, "W-AKI": 30.0}, "P-AKI_compatibility_only": 35.0, "version": "AKI-JRA v2.1"}}},
         "final_ticket": {"no_bet": no_bet, "tickets": [] if no_bet else [
             {"bet_type": "EXACTA", "selection": [7, 3], "stake": 500}, {"bet_type": "TRIFECTA", "selection": [7, 3, 12], "stake": 700}]}}
    d = tmp / "runtime/final_artifacts"; d.mkdir(parents=True, exist_ok=True)
    (d / f"{rid}.json").write_text(json.dumps(f))


def test_freeze_before_post_only_once(tmp_path, monkeypatch):
    monkeypatch.setattr(M, "ROOT", tmp_path); monkeypatch.setattr(M, "OUT", tmp_path / "runtime/jra_multi_primary")
    _final(tmp_path, "KM-JRA-TKY-20261129-R01", "2026-11-29T10:05:00+09:00")
    _final(tmp_path, "KM-JRA-TKY-20261129-R02", "2026-11-29T10:35:00+09:00", no_bet=True)
    jst = dt.timezone(dt.timedelta(hours=9))
    assert M.freeze("2026-11-29", dt.datetime(2026, 11, 29, 10, 4, 30, tzinfo=jst)) == [
        {"race_id": "KM-JRA-TKY-20261129-R02", "status": "PRODUCTION_NO_BET_SAME_BUDGET_ZERO"}]
    got = M.freeze("2026-11-29", dt.datetime(2026, 11, 29, 9, 30, tzinfo=jst))
    assert got == [{"race_id": "KM-JRA-TKY-20261129-R01", "status": "FROZEN"}]
    rec = json.loads((tmp_path / "runtime/jra_multi_primary/2026-11-29/KM-JRA-TKY-20261129-R01.json").read_text())
    assert rec["production_effect"] == "NONE" and rec["budget"] == 1200
    assert rec["arms"]["MP-A"]["investment"] == 1200 and rec["arms"]["MP-A"]["trio_type"] == "2-3-6"
    assert M.freeze("2026-11-29", dt.datetime(2026, 11, 29, 9, 40, tzinfo=jst)) == []


def test_payout_page_must_agree_with_production():
    p = {"payouts": M.parse_all_payouts(TEXT)}
    res = {"official_result": {"payouts": {"EXACTA": {"selection": [9, 11], "per_100_yen": 12810}}}}
    assert M._check_against_production(p, res)
    res["official_result"]["payouts"]["EXACTA"]["per_100_yen"] = 12000
    assert not M._check_against_production(p, res)

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "runtime"), str(ROOT / "runtime/jra_source_runtime"), str(ROOT / "runtime/analysis")]
import jra_nobet_shadow as N


def test_reference_shape_fills_empty_columns_from_static_order():
    roles, tk = N.reference_tickets({"W": [], "P2": [], "P3": ["6", "8"]}, ["3", "1", "6", "8", "2", "5", "4"])
    assert roles["W"] == ["3", "1"] and len(roles["P2"]) == 4 and len(roles["P3"]) == 6
    ex = [t for t in tk if t["bet_type"] == "EXACTA"]
    assert len(ex) == 2 * 3 and all(t["selection"][0] != t["selection"][1] for t in ex)
    trios = [tuple(t["selection"]) for t in tk if t["bet_type"] == "TRIO"]
    assert len(trios) == len(set(trios)) and all(len(set(x)) == 3 for x in trios)


def test_classes_and_metrics():
    races = [{"race_id": "KM-JRA-TKY-20991231-R01", "state": "AKI_NO_BET", "decision_reason": "AKI_SINGLE_HEAD_FORBIDDEN"},
             {"race_id": "KM-JRA-TKY-20991231-R02", "state": "SOURCE_FAILED", "first_blocked_stage": "SOURCE"},
             {"race_id": "KM-JRA-TKY-20991231-R03", "state": "WAITING"}]
    cl = [N.classify_race(r) for r in races]
    assert [c["class"] for c in cl] == ["SELECTIVE_RULE", "TECHNICAL", "PENDING"]
    m = N.metrics(cl)
    assert m["technical_no_bet_pct"] == 33.3 and m["selective_no_bet_pct"] == 33.3 and m["prediction_completion_pct"] == 33.3

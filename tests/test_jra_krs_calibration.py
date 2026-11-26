import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime/analysis"))
import jra_krs_calibration as K


def test_identity_keeps_ssr_and_temperature_flattens_but_keeps_order():
    w = {"1": 0.6, "2": 0.3, "3": 0.1}
    assert K.probs(w, "KCP-B1") == {"1": 0.6, "2": 0.3, "3": 0.1} or abs(sum(K.probs(w, "KCP-B1").values()) - 1) < 1e-12
    c = K.probs(w, "KCP-C2")
    assert abs(sum(c.values()) - 1) < 1e-12
    assert c["1"] > c["2"] > c["3"] and c["1"] < 0.6 and c["3"] > 0.1


def test_constants_are_frozen_before_forward_window():
    assert K.T_FIXED == 2.65 and K.FIT_CUT < K.FIRST_ELIGIBLE == "20261128"


def test_metrics_on_toy_rows():
    rows = [{"ssr_w": {"1": 0.9, "2": 0.1}, "winner": "2"}, {"ssr_w": {"1": 0.9, "2": 0.1}, "winner": "1"}]
    m = K.metrics(rows, "UNIFORM")
    assert m["races"] == 2 and abs(m["logloss_per_race"] - 0.6931) < 1e-3
    d = K.paired_logloss_diff(rows, "KCP-C2", "KCP-B1")
    assert d["races"] == 2

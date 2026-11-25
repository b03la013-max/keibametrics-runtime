import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime/analysis")); sys.path.insert(0, str(ROOT / "runtime"))
import jra_conversion_challenger as CC


def test_scale_monotone_and_same_range():
    order = ["VERY_WEAK", "WEAK", "CAUTION", "MIXED", "NEUTRAL", "POSITIVE", "STRONG", "VERY_STRONG", "EXCEPTIONAL"]
    vals = [CC.CV2_SCALE[k] for k in order]
    assert vals == sorted(vals) and vals[0] == 24.0 and vals[-1] == 94.0


def test_prod_arm_reproduces_frozen_ranking():
    import json
    rid = "KM-JRA-KYO-20261122-R11"
    p = ROOT / f"runtime/requests/{rid}-LIVE-R1-FORMAL.json"
    if not p.exists():
        return
    r = CC.race(rid, CC.FC._mapping())
    assert r["prod_replay_matches_frozen"] is True
    assert set(r["rankings"]) == set(CC.ARMS + CC.BASELINES)


def test_market_blind_weights_drop_vmi_and_keep_ratios():
    w = CC._market_blind_weights("v1.1")
    base = CC.B.ZAI_WIN_WEIGHTS["v1.1"]
    assert "VMI" not in w and abs(sum(w.values()) - sum(base.values()) / (1 - base["VMI"]) + base["VMI"] / (1 - base["VMI"])) < 1e-9
    assert abs(w["BVI"] / w["HPI"] - base["BVI"] / base["HPI"]) < 1e-12
    assert CC._market_blind_weights("v1.0") == dict(CC.B.ZAI_WIN_WEIGHTS["v1.0"])


def test_market_baseline_is_recorded_but_not_an_arm():
    assert "MARKET_BLIND" in CC.ARMS and "MARKET_VMI" not in CC.ARMS and CC.BASELINES == ["MARKET_VMI"]

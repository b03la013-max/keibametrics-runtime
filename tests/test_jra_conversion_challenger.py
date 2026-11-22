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
    assert set(r["rankings"]) == set(CC.ARMS)

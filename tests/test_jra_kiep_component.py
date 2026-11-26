import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime/analysis"))
import jra_kiep_component as K


def test_rank_and_score():
    vals = {"1": {"A": 1.0}, "2": {"A": 3.0}, "3": {"A": 2.0}}
    rk = K._rank(vals, {"A": 1.0})
    assert rk == ["2", "3", "1"]
    assert K._score(rk, ["3", "2", "1"]) == (2.0, 2)


def test_ci_sign_convention():
    c = K._ci([-1.0, -1.0, -1.0, -1.2])
    assert c["n"] == 4 and c["mean"] < 0 and c["ci95"][1] < 0
    assert K._ci([0.5]) == {"n": 1}

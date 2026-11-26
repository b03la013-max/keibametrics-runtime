import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime/analysis"))
import jra_ksp_risk as K


def _r(d, n, inv, pay):
    return {"race_id": f"KM-JRA-TKY-{d}-R{n:02d}", "venue": "TKY", "date": d, "race_no": n,
            "investment": inv, "payout": pay, "no_bet": inv == 0}


def test_drawdown_streak_and_hit_but_loss():
    rs = [_r("20261128", 1, 1000, 0), _r("20261128", 2, 1000, 0), _r("20261128", 3, 1000, 500),
          _r("20261129", 1, 1000, 5000), _r("20261129", 2, 0, 0)]
    m = K.metrics(rs)
    assert m["bet_races"] == 4 and m["no_bet_races"] == 1
    assert m["max_drawdown_yen"] == 2500 and m["longest_losing_streak"] == 2
    assert m["hit_but_loss"] == 1 and m["pfs"] == 137.5 and m["pfs_ex_top1"] == 12.5


def test_no_bet_only_has_no_pfs():
    assert K.metrics([_r("20261128", 1, 0, 0)]) == {"races": 1, "bet_races": 0}


def test_bootstrap_resamples_whole_days():
    rs = [_r("20261128", 1, 1000, 0), _r("20261129", 1, 1000, 3000)]
    b = K.block_bootstrap(rs, n=200)
    assert b["unit"] == "race_day" and 0 <= b["pfs_p2_5"] <= b["pfs_p97_5"] <= 300

"""DRIVE02 recorded challengers (Owner 追加 Drive 2026-11-26). NON-PRODUCTION shadow candidates only."""
import copy, glob, json, sys
from pathlib import Path
sys.path.insert(0, "runtime/analysis")
import jra_role_candidate_replay as rc

ARMS = ["W_FOREIGN_JOCKEY_MKT_TOP3", "W_FOREIGN_JOCKEY_STATIC_SAME_COUNT_CONTROL", "W_FOREIGN_PREV23_MKT_TOP3",
        "W_FOREIGN_PREV23_STATIC_SAME_COUNT_CONTROL", "W_FOREIGN_SWITCH_MKT_TOP3", "W_FOREIGN_SWITCH_STATIC_SAME_COUNT_CONTROL"]


def test_registered_with_controls_and_no_production_effect():
    assert all(k in rc.CANDIDATES for k in ARMS)
    p = json.loads(Path("profiles/KM_JRA_FORWARD_OOS_PREREG_20261128_DRIVE02.json").read_text())
    assert p["production_effect"] == "NONE" and {a["id"] for a in p["arms"]} == set(ARMS)


def test_foreign_jockey_pattern():
    assert rc.is_foreign_jockey("C.ルメール") and rc.is_foreign_jockey("M.デムーロ") and rc.is_foreign_jockey("Ｒ．ムーア")
    assert not rc.is_foreign_jockey("武 豊") and not rc.is_foreign_jockey(None) and not rc.is_foreign_jockey("")


def test_rules():
    r = {"jockey": "R.ムーア", "recent_runs": [{"finish": 2, "jockey": "戸崎 圭太"}]}
    assert rc.foreign_rule(r, "ALL") and rc.foreign_rule(r, "PREV23") and rc.foreign_rule(r, "SWITCH")
    r2 = {"jockey": "R.ムーア", "recent_runs": [{"finish": 1, "jockey": "R.ムーア"}]}
    assert rc.foreign_rule(r2, "ALL") and not rc.foreign_rule(r2, "PREV23") and not rc.foreign_rule(r2, "SWITCH")
    assert not rc.foreign_rule({"jockey": "川田 将雅", "recent_runs": [{"finish": 2}]}, "PREV23")


def _graded_finals():
    out = []
    for p in sorted(glob.glob("runtime/final_artifacts/KM-JRA-*-2026*-R*.json")):
        f = json.loads(Path(p).read_text())
        if "static_prediction" in f and rc.race_grade(f):
            out.append(f)
    return out


def test_candidate_and_control_fire_in_same_races_with_same_count():
    fired = 0
    for f in _graded_finals():
        for rule in ("JOCKEY", "PREV23", "SWITCH"):
            cand, ctl = f"W_FOREIGN_{rule}_MKT_TOP3", f"W_FOREIGN_{rule}_STATIC_SAME_COUNT_CONTROL"
            a, b = copy.deepcopy(f), copy.deepcopy(f)
            w0 = len(rc._live(f, "W"))
            fa, fb = rc.CANDIDATES[cand](a), rc.CANDIDATES[ctl](b)
            assert fa == fb
            if fa:
                fired += 1
                assert len(rc._live(a, "W")) - w0 == len(rc._live(b, "W")) - w0 > 0
    assert fired > 0


def test_ungraded_races_never_fire():
    for p in sorted(glob.glob("runtime/final_artifacts/KM-JRA-*-2026112*-R0[1-5].json"))[:10]:
        f = json.loads(Path(p).read_text())
        if "static_prediction" in f and rc.race_grade(f) is None:
            assert all(not rc.CANDIDATES[k](copy.deepcopy(f)) for k in ARMS)

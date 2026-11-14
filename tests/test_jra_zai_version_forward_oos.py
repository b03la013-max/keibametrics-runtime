import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
sys.path.insert(0, str(ROOT / "runtime/analysis"))
import jra_zai_version_forward_oos as z  # noqa: E402
from jra_index_provenance_builder import zai_win_value  # noqa: E402

SRC = ROOT / "runtime/final_artifacts/KM-JRA-TKY-20261114-R11.json"


def _final_as_1115(tmp, fix_formula=True):
    d = json.loads(SRC.read_text())
    d["race_id"] = d["race_id"].replace("20261114", "20261115")
    if fix_formula:
        for r in d["final_prediction_package"]["index_provenance_replay"]["runners"].values():
            r["zai_win"] = zai_win_value(r["base_final_values"], "v1.1")
    p = tmp / "runtime/final_artifacts" / (d["race_id"] + ".json")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d))
    return p, d


def test_skips_v10_dated_finals(tmp_path):
    assert z.freeze_one(SRC, tmp_path) is None


def test_freeze_is_bound_and_immutable(tmp_path):
    p, d = _final_as_1115(tmp_path)
    a = z.freeze_one(p, tmp_path)
    assert a["production_formula_check"] == "PRODUCTION_IS_V1_1"
    assert set(a["shadow_v1_0_ranking"]) == set(a["production_v1_1_ranking"])
    b = z.freeze_one(p, tmp_path)
    assert a["sha256"] == b["sha256"] and a["frozen_at"] == b["frozen_at"]


def test_formula_mismatch_is_flagged(tmp_path):
    p, _ = _final_as_1115(tmp_path, fix_formula=False)
    assert z.freeze_one(p, tmp_path)["production_formula_check"] == "PRODUCTION_FORMULA_MISMATCH"


def test_evaluate_and_summary(tmp_path):
    p, d = _final_as_1115(tmp_path)
    pre = z.freeze_one(p, tmp_path)
    top3 = pre["shadow_v1_0_ranking"][:3]
    ev = tmp_path / "runtime/jra_static_owner_forward_oos" / d["race_id"] / "result_evaluation.json"
    ev.parent.mkdir(parents=True)
    ev.write_text(json.dumps({"top3": top3, "observed_at": "2099-01-01T00:00:00+00:00",
                              "official_result_sha256": "x"}))
    r = z.evaluate_one(tmp_path / z.OUT / d["race_id"], tmp_path)
    assert r["freeze_before_result"] is True
    assert r["shadow_v1_0"]["exact_triple_top3"] is True
    s = z.summary(tmp_path)
    assert s["races"] == 1 and s["checkpoint"] == "PRE_30"
    assert s["paired_top3_mean_rank_diff"] >= 0

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
sys.path.insert(0, str(ROOT / "runtime/analysis"))
import jra_index_research as R  # noqa: E402
import jra_index_provenance_builder as B  # noqa: E402

FINAL = ROOT / "runtime/final_artifacts/KM-JRA-TKY-20261114-R11.json"


def _root(tmp, top3=None, rid=None):
    d = json.loads(FINAL.read_text())
    if rid:
        d["race_id"] = rid
    rid = d["race_id"]
    (tmp / "runtime/final_artifacts").mkdir(parents=True, exist_ok=True)
    fp = tmp / "runtime/final_artifacts" / f"{rid}.json"
    fp.write_text(json.dumps(d))
    runners = list(d["final_prediction_package"]["index_provenance_replay"]["runners"])
    ev = tmp / "runtime/jra_static_owner_forward_oos" / rid / "result_evaluation.json"
    ev.parent.mkdir(parents=True, exist_ok=True)
    ev.write_text(json.dumps({"top3": top3 or runners[:3], "observed_at": "2026-11-14T07:00:00+00:00"}))
    for sub in ("mapping", "runtime/jra_index_provenance_builder.py"):
        dst = tmp / sub
        if not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            (shutil.copytree if (ROOT / sub).is_dir() else shutil.copy)(ROOT / sub, dst)
    return fp, d


def test_manifest_reads_code_weights(tmp_path):
    _root(tmp_path)
    m = R.manifest(tmp_path)
    assert m["derived7"]["ZAI_WIN"]["v1.1"] == B.ZAI_WIN_WEIGHTS["v1.1"]
    assert set(m["base13_feature_weights_by_profile"]) == set(B.BASE)
    assert "HPI" in m["derived7"]["TPI_base"]


def test_reflection_is_immutable_and_covers_20_indices(tmp_path):
    fp, _ = _root(tmp_path)
    a = R.reflect_one(tmp_path, fp)
    assert set(a["per_index"]) == set(R.ALL20)
    assert a["production_effect"] == "NONE"
    b = R.reflect_one(tmp_path, fp)
    assert a["sha256"] == b["sha256"] and a["reflected_at"] == b["reflected_at"]


def test_candidates_have_ids_parent_and_rejection_rule(tmp_path):
    fp, _ = _root(tmp_path)
    row = R.reflect_one(tmp_path, fp)
    cands = R.generate_candidates([row] * R.MIN_TRAIN_RACES, ["20261101", "20261114"])
    assert {c["change"]["type"] for c in cands} >= {"ABLATE", "DISCRIMINATION_REWEIGHT"}
    for c in cands:
        assert c["candidate_id"].startswith("CAND-ZAIW-") and c["parent_formula"] == "JRA-ZAI-WIN-v1.1"
        assert c["rejection"] and c["pre_registered"]["primary"]
        w = c.get("weights") or next(iter(c["weights_by_surface"].values()))
        assert abs(sum(w.values()) - 1) < 1e-4


def test_forward_freeze_requires_registration_before_race_freeze(tmp_path):
    fp, d = _root(tmp_path, rid="KM-JRA-TKY-20261115-R11")
    row = R.reflect_one(tmp_path, fp)
    c = R.generate_candidates([row] * R.MIN_TRAIN_RACES, ["20261101", "20261114"])[0]
    c.update(status="SHADOW", forward_from_race_date="20261115")
    reg = {"candidates": [dict(c, registered_at="2099-01-01T00:00:00+00:00")]}
    R.registry_path(tmp_path).parent.mkdir(parents=True, exist_ok=True)
    R.registry_path(tmp_path).write_text(json.dumps(reg))
    assert R.freeze(tmp_path, "20261115")["frozen"] == 0  # registered after the race froze
    reg["candidates"][0]["registered_at"] = "2000-01-01T00:00:00+00:00"
    R.registry_path(tmp_path).write_text(json.dumps(reg))
    assert R.freeze(tmp_path, "20261115")["frozen"] == 1
    rep = R.evaluate_forward(tmp_path)
    assert rep[c["candidate_id"]]["eligible_races"] == 1
    assert rep[c["candidate_id"]]["status"] == "OOS_EVALUATING"


def test_walkforward_trains_only_on_earlier_dates(tmp_path):
    fp, _ = _root(tmp_path)
    row = R.reflect_one(tmp_path, fp)
    rows = []
    for i, day in enumerate(["20261101"] * R.MIN_TRAIN_RACES + ["20261102"] * 3):
        r = dict(row, race_id=f"KM-JRA-TKY-{day}-R{(i % 12) + 1:02d}")
        rows.append(r)
    wf = R.walkforward(rows)
    assert [f["test_date"] for f in wf["folds"]] == ["20261102"]
    assert wf["folds"][0]["train_races"] == R.MIN_TRAIN_RACES

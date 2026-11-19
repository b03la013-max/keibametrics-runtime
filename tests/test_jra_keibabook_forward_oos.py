import datetime as dt, json, shutil, sys
from pathlib import Path
sys.path.insert(0, "runtime/analysis")
import jra_keibabook_forward_oos as kb

RID = "KM-JRA-FKS-20261115-R03"


def test_strip_only_keibabook_features():
    runners = [{"runner_id": "1", "evidence_features": {
        "workout_speed": {"evidence_refs": ["SUPP:KEIBABOOK-202603060403"]},
        "sire_track_signal": {"evidence_refs": ["SUPP:BLOODB-2026111503030403"]}}}]
    out, n = kb._strip_keibabook(runners)
    assert n == 1 and list(out[0]["evidence_features"]) == ["sire_track_signal"]


def test_freeze_before_post_and_reproduce(tmp_path):
    src = Path(".").resolve()
    for d in ("runtime/final_artifacts", "runtime/requests", "mapping"):
        (tmp_path / d).mkdir(parents=True, exist_ok=True)
    shutil.copy(src / f"runtime/final_artifacts/{RID}.json", tmp_path / f"runtime/final_artifacts/{RID}.json")
    shutil.copy(src / f"runtime/requests/{RID}-LIVE-R1-FORMAL.json", tmp_path / f"runtime/requests/{RID}-LIVE-R1-FORMAL.json")
    shutil.copy(src / kb.MAPPING, tmp_path / kb.MAPPING)
    post = dt.datetime.fromisoformat(json.loads((tmp_path / f"runtime/final_artifacts/{RID}.json").read_text())["scheduled_post_at"])
    assert kb.freeze("20261115", root=tmp_path, now=post) == []
    assert kb.freeze("20261115", root=tmp_path, now=post - dt.timedelta(minutes=30)) == [RID]
    body = json.loads((tmp_path / kb.OUT / RID / "pre_result.json").read_text())
    assert body["recompute_reproduces_production"] is True  # 11/15 had no Keibabook: arms identical
    assert body["keibabook_features_removed"] == 0

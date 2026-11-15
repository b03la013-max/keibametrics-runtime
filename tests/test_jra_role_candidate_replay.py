import datetime as dt, json, shutil, sys
from pathlib import Path
sys.path.insert(0, "runtime/analysis")
import jra_role_candidate_replay as rc

RID = "KM-JRA-TKY-20261115-R11"


def _root(tmp_path):
    src = Path(".").resolve()
    (tmp_path / "runtime/final_artifacts").mkdir(parents=True)
    shutil.copy(src / f"runtime/final_artifacts/{RID}.json", tmp_path / f"runtime/final_artifacts/{RID}.json")
    return tmp_path


def test_baseline_replay_reproduces_official_settlement():
    rows = rc.run(["20261115"])
    s = rc.summarize(rows)["baseline"]
    assert (s["investment"], s["payout"]) == (49900, 14520)


def test_forward_freeze_only_before_post(tmp_path):
    root = _root(tmp_path)
    post = dt.datetime.fromisoformat(json.loads((root / f"runtime/final_artifacts/{RID}.json").read_text())["scheduled_post_at"])
    assert rc.freeze_forward("20261115", root=root, now=post) == []
    assert rc.freeze_forward("20261115", root=root, now=post - dt.timedelta(minutes=30)) == [RID]
    body = json.loads((root / rc.FWD / RID / "pre_result.json").read_text())
    assert body["production_effect"] == "NONE" and set(body["arms"]) == set(rc.CANDIDATES)
    # immutable: a second freeze does not overwrite
    assert rc.freeze_forward("20261115", root=root, now=post - dt.timedelta(minutes=10)) == []

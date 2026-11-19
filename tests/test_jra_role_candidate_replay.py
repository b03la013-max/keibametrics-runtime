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


def test_market_ranking_uses_only_pre_cutoff_official_observation(tmp_path):
    final = json.loads(Path(f"runtime/final_artifacts/{RID}.json").read_text())
    mk = rc.market_ranking(final)
    assert mk and len(set(mk)) == len(mk)
    rq = json.loads(Path(f"runtime/requests/{RID}-LIVE-R1-FORMAL.json").read_text())
    rq["source_snapshot"]["jra_official_market_observation"]["captured_at"] = "2099-01-01T00:00:00+00:00"
    (tmp_path / "runtime/requests").mkdir(parents=True)
    (tmp_path / f"runtime/requests/{RID}-LIVE-R1-FORMAL.json").write_text(json.dumps(rq))
    assert rc.market_ranking(final, root=tmp_path) is None  # observed after cutoff: never used


def test_market_top3_adds_only_missing_favourites():
    import copy
    final = json.loads(Path(f"runtime/final_artifacts/{RID}.json").read_text())
    f = copy.deepcopy(final)
    before = set(rc._live(f, "W"))
    top3 = rc.market_ranking(final)[:3]
    changed = rc.w_plus_market_top3(f)
    assert set(rc._live(f, "W")) == before | set(top3)
    assert changed == bool(set(top3) - before)

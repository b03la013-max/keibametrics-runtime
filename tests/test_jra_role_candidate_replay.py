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


def test_p3_market_top5_adds_missing_thirds_under_every_pair():
    import copy
    final = json.loads(Path(f"runtime/final_artifacts/{RID}.json").read_text())
    f = copy.deepcopy(final)
    before = set(rc._live(f, "P3"))
    top5 = rc.market_ranking(final)[:5]
    miss = [r for r in top5 if r not in before]
    assert rc.p3_market_top5(f) == bool(miss)
    assert set(rc._live(f, "P3")) == before | set(top5)
    pairs = {(str(p["head"]), str(p["second"])) for p in f["pair_dispositions"]}
    got = {(str(t["head"]), str(t["second"]), str(t["third"])) for t in f["third_dispositions"]}
    for h, s in pairs:
        for t in miss:
            if t not in (h, s):
                assert (h, s, t) in got
    c = copy.deepcopy(final)
    if miss:
        assert rc.p3_static_same_count_control(c)
        assert len(set(rc._live(c, "P3")) - before) == len(miss)   # same width, Static choice


def test_skip_heavy_going_uses_pre_cutoff_official_going_only(tmp_path):
    import copy
    final = json.loads(Path(f"runtime/final_artifacts/{RID}.json").read_text())
    rq = json.loads(Path(f"runtime/requests/{RID}-LIVE-R1-FORMAL.json").read_text())
    obs = rq["source_snapshot"].setdefault("aki_external_observations", [])
    cut = dt.datetime.fromisoformat(final["prediction_cutoff"])
    obs[:] = [{"going": "良", "source_authority": "JRA_OFFICIAL", "observed_at": (cut - dt.timedelta(hours=2)).isoformat()},
              {"going": "重", "source_authority": "JRA_OFFICIAL", "observed_at": (cut + dt.timedelta(minutes=1)).isoformat()}]
    (tmp_path / "runtime/requests").mkdir(parents=True)
    (tmp_path / f"runtime/requests/{RID}-LIVE-R1-FORMAL.json").write_text(json.dumps(rq))
    assert rc.official_going(final, root=tmp_path) == "良"          # after-cutoff 重 is never used
    obs[1]["observed_at"] = (cut - dt.timedelta(minutes=5)).isoformat()
    (tmp_path / f"runtime/requests/{RID}-LIVE-R1-FORMAL.json").write_text(json.dumps(rq))
    assert rc.official_going(final, root=tmp_path) == "重"


def test_p2_market_top3_adds_missing_seconds_under_every_head():
    import copy
    final = json.loads(Path(f"runtime/final_artifacts/{RID}.json").read_text())
    f = copy.deepcopy(final)
    before = set(rc._live(f, "P2"))
    top3 = rc.market_ranking(final)[:3]
    miss = [r for r in top3 if r not in before]
    assert rc.p2_market_top3(f) == bool(miss)
    assert set(rc._live(f, "P2")) == before | set(top3)
    pairs = {(str(p["head"]), str(p["second"])) for p in f["pair_dispositions"]}
    for h in rc._live(f, "W"):
        for s in miss:
            if s != h:
                assert (h, s) in pairs
    c = copy.deepcopy(final)
    if miss:
        assert rc.p2_static_same_count_control(c)
        assert len(set(rc._live(c, "P2")) - before) == len(miss)

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


def test_drop_trifecta_keeps_production_exacta_and_trio_without_mec_rebuild(tmp_path):
    import copy
    final = json.loads(Path(f"runtime/final_artifacts/{RID}.json").read_text())
    base = final["final_ticket"]["tickets"]
    f = copy.deepcopy(final)
    assert rc.drop_trifecta(f) == any(t["bet_type"] == "TRIFECTA" for t in base)
    tk, inv = rc._filtered_tickets(f)
    assert tk == [t for t in base if t["bet_type"] != "TRIFECTA"]
    assert inv == sum(t["stake"] for t in tk)
    assert f["final_ticket"]["tickets"] == base  # the frozen FINAL copy is not rewritten by the arm itself


def test_exacta_only_keeps_only_production_exacta():
    import copy
    final = json.loads(Path(f"runtime/final_artifacts/{RID}.json").read_text())
    f = copy.deepcopy(final)
    rc.exacta_only(f)
    tk, _ = rc._filtered_tickets(f)
    assert tk and all(t["bet_type"] == "EXACTA" for t in tk)
    assert len(tk) == sum(1 for t in final["final_ticket"]["tickets"] if t["bet_type"] == "EXACTA")


def test_ticket_shape_arms_replay_settles_subset_of_production():
    rows = rc.run(["20261115"])
    for r in rows:
        for arm in ("DROP_TRIFECTA", "EXACTA_ONLY"):
            a = r.get(arm)
            if a:
                assert a["investment"] <= r["baseline"]["investment"]
                assert a["payout"] <= r["baseline"]["payout"]


def test_ticket_shape_arms_frozen_with_tickets(tmp_path):
    root = _root(tmp_path)
    post = dt.datetime.fromisoformat(json.loads((root / f"runtime/final_artifacts/{RID}.json").read_text())["scheduled_post_at"])
    rc.freeze_forward("20261115", root=root, now=post - dt.timedelta(minutes=30))
    body = json.loads((root / rc.FWD / RID / "pre_result.json").read_text())
    for arm, dropped in (("DROP_TRIFECTA", {"TRIFECTA"}), ("EXACTA_ONLY", {"TRIFECTA", "TRIO"})):
        a = body["arms"][arm]
        if a:
            assert set(a["dropped_bet_types"]) == dropped
            assert all(t["bet_type"] not in dropped for t in a["tickets"])
            assert a["investment"] == sum(t["stake"] for t in a["tickets"])


def test_w_static_top3_single_head_adds_static_top3_only_for_single_head():
    """11/23 review P1: single-head W gets the missing Static top-3 runners as heads (at most two)."""
    import copy
    rid = "KM-JRA-FKS-20261123-R08"  # single head 14 (Static 1); winner 11 was Static 3
    final = json.loads(Path(f"runtime/final_artifacts/{rid}.json").read_text())
    rank = [str(r) for r in final["static_prediction"]["ranking"]]
    f = copy.deepcopy(final)
    before = rc._live(f, "W")
    assert len(before) == 1
    assert rc.w_static_top3_single_head(f)
    after = set(rc._live(f, "W"))
    assert after == set(before) | set(rank[:3]) and len(after - set(before)) <= 2
    # a multi-head W is untouched
    g = copy.deepcopy(f)
    assert not rc.w_static_top3_single_head(g)
    assert rc.w_static_top3_single_head in rc.CANDIDATES.values()


def test_w_static_top3_single_head_never_more_than_two_heads_added():
    import copy
    final = json.loads(Path(f"runtime/final_artifacts/{RID}.json").read_text())
    f = copy.deepcopy(final)
    W = rc._live(f, "W")
    if len(W) != 1:
        return
    rc.w_static_top3_single_head(f)
    assert len(set(rc._live(f, "W")) - set(W)) <= 2

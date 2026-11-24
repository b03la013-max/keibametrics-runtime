import json, sys
sys.path.insert(0, "runtime/analysis")
import jra_delivery_ledger as L


def _fetch(comments):
    return lambda since: comments


def test_ledger_separates_final_post_and_assisted(tmp_path, monkeypatch):
    monkeypatch.setattr(L, "OUT", tmp_path)
    rid = "KM-JRA-FKS-20261123-R01"
    comments = [{"created_at": "2026-11-23T00:07:11Z", "user": {"login": "github-actions[bot]", "type": "Bot"},
                 "body": f"【福島1R】 ... `{rid}`"},
                {"created_at": "2026-11-23T00:08:00Z", "user": {"login": "someone", "type": "User"},
                 "body": "`KM-JRA-TKY-20261123-R01`"}]
    L.add_assisted("2026-11-23", rid, "2026-11-23T00:30:00+00:00")
    L.add_assisted("2026-11-23", rid, "2026-11-23T05:00:00+00:00")  # idempotent
    out = L.build("2026-11-23", fetch=_fetch(comments))
    row = {r["race_id"]: r for r in out["races"]}
    a = row[rid]
    assert a["final_saved"]["status"] == "PRE_POST"
    assert a["issue_posted"]["status"] == "PRE_POST" and a["issue_post_count"] == 1
    assert a["assisted_sent"]["status"] == "PRE_POST" and a["assisted_sent"]["at"].startswith("2026-11-23T00:30")
    assert a["device_receipt"] == "UNVERIFIED"
    # a non-bot comment never counts as a delivery post
    assert row["KM-JRA-TKY-20261123-R01"]["issue_posted"]["status"] == "NO"
    assert out["summary"]["device_receipt_verified"] == 0
    assert (tmp_path / "2026-11-23.md").exists()

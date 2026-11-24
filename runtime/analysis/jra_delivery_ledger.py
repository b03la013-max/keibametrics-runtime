"""JRA delivery ledger: separate what was saved, what was posted, and what reached the owner.

Owner approval 2026-11-24 13:54 (ChatGPT audit 11/24 P0: delivery acceptance). Record only;
no prediction, ticket or capital effect.

Per race of a card it records three independent facts, each with its own timestamp:
  FINAL_SAVED      signed FINAL artifact exists and was frozen before the official post time
  ISSUE_POSTED     a bot comment carrying the race_id was posted on the approved JRA owner
                   delivery issue (#421) before the post time
  ASSISTED_SENT    the race was sent to the owner in the Claude session (ASSISTED delivery),
                   from runtime/jra_delivery_ledger/<date>_assisted.json
Device receipt (the owner's phone actually showing it) is not observable here and is
always recorded as UNVERIFIED; it is never inferred from a post or a send.

  python3 runtime/analysis/jra_delivery_ledger.py build 2026-11-23
  python3 runtime/analysis/jra_delivery_ledger.py assisted 2026-11-23 KM-JRA-TKY-20261123-R11 [--at ISO]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runtime/jra_delivery_ledger"
REPO = "b03la013-max/keibametrics-runtime"
ISSUE = 421
PROFILE = "KM-JRA-DELIVERY-LEDGER-v1"


def _ts(s):
    if not s:
        return None
    return dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))


def issue_comments(since: str, fetch=None) -> list[dict]:
    """All comments on the delivery issue since `since` (ISO). `fetch` is injectable for tests."""
    if fetch:
        return fetch(since)
    out, page = [], 1
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    while True:
        path = f"repos/{REPO}/issues/{ISSUE}/comments?since={since}&per_page=100&page={page}"
        if token:
            req = urllib.request.Request("https://api.github.com/" + path,
                                         headers={"Authorization": "Bearer " + token,
                                                  "Accept": "application/vnd.github+json"})
            batch = json.loads(urllib.request.urlopen(req, timeout=30).read())
        else:
            batch = json.loads(subprocess.check_output(["gh", "api", path]))
        out += batch
        if len(batch) < 100:
            return out
        page += 1


def _assisted(date: str) -> dict:
    p = OUT / f"{date}_assisted.json"
    if not p.exists():
        return {}
    return {r["race_id"]: r for r in json.loads(p.read_text()).get("sent", [])}


def build(date: str, fetch=None) -> dict:
    status = json.loads((ROOT / f"runtime/jra_race_day_status/{date}.json").read_text())
    races = status["races"] if isinstance(status["races"], list) else list(status["races"].values())
    day0 = (dt.date.fromisoformat(date) - dt.timedelta(days=1)).isoformat() + "T15:00:00Z"
    comments = [c for c in issue_comments(day0, fetch) if (c.get("user") or {}).get("type") == "Bot"
                or (c.get("user") or {}).get("login") == "github-actions[bot]"]
    assisted = _assisted(date)
    rows = []
    for r in races:
        rid, post = r["race_id"], _ts(r.get("post"))
        fp = ROOT / f"runtime/final_artifacts/{rid}.json"
        final_at = None
        if fp.exists():
            final_at = _ts(json.loads(fp.read_text()).get("final_freeze_timestamp"))
        posts = sorted(_ts(c["created_at"]) for c in comments if f"`{rid}`" in (c.get("body") or ""))
        a = assisted.get(rid) or {}
        a_at = _ts(a.get("sent_at"))

        def fact(at, present):
            if not present:
                return {"status": "NO"}
            if at is None:
                return {"status": "YES_TIME_UNRECORDED"}
            return {"status": "PRE_POST" if post and at < post else "AFTER_POST", "at": at.isoformat()}

        rows.append({"race_id": rid, "venue": r.get("venue"), "race_no": r.get("race_no"),
                     "post": r.get("post"), "state": r.get("state"),
                     "final_saved": fact(final_at, fp.exists()),
                     "issue_posted": fact(posts[0] if posts else None, bool(posts)),
                     "issue_post_count": len(posts),
                     "assisted_sent": fact(a_at, bool(a)),
                     "device_receipt": "UNVERIFIED"})

    def n(key, *ok):
        return sum(1 for x in rows if x[key]["status"] in ok)

    finals = [x for x in rows if x["final_saved"]["status"] != "NO"]
    summary = {"races": len(rows), "final_saved_pre_post": n("final_saved", "PRE_POST"),
               "issue_posted_pre_post": n("issue_posted", "PRE_POST"),
               "issue_posted_after_post": n("issue_posted", "AFTER_POST"),
               "assisted_sent": n("assisted_sent", "PRE_POST", "AFTER_POST", "YES_TIME_UNRECORDED"),
               "assisted_sent_pre_post": n("assisted_sent", "PRE_POST"),
               "final_without_issue_post": sum(1 for x in finals if x["issue_posted"]["status"] == "NO"),
               "final_without_any_send": sum(1 for x in finals if x["issue_posted"]["status"] == "NO"
                                             and x["assisted_sent"]["status"] == "NO"),
               "device_receipt_verified": 0}
    out = {"profile": PROFILE, "race_date": date, "record_only": True, "production_effect": "NONE",
           "issue": f"{REPO}#{ISSUE}", "summary": summary, "races": rows,
           "note": "device_receipt is never inferred from a post or a send"}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{date}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    lines = [f"# JRA 配信台帳 {date}", "",
             "| R | 発走 | FINAL保存 | Issue#421投稿 | 本人配信(ASSISTED) | 端末到達 |", "|---|---|---|---|---|---|"]
    lab = {"PRE_POST": "発走前", "AFTER_POST": "発走後", "YES_TIME_UNRECORDED": "済（時刻未記録）", "NO": "—"}
    for x in rows:
        lines.append(f"| {x['venue']}{x['race_no']}R | {(x['post'] or '')[11:16]} | {lab[x['final_saved']['status']]} | "
                     f"{lab[x['issue_posted']['status']]} | {lab[x['assisted_sent']['status']]} | 未確認 |")
    lines += ["", "集計: " + json.dumps(summary, ensure_ascii=False)]
    (OUT / f"{date}.md").write_text("\n".join(lines) + "\n")
    return out


def add_assisted(date: str, race_id: str, at: str | None) -> None:
    p = OUT / f"{date}_assisted.json"
    d = json.loads(p.read_text()) if p.exists() else {"profile": PROFILE + "-ASSISTED", "race_date": date, "sent": []}
    if any(r["race_id"] == race_id for r in d["sent"]):
        return
    d["sent"].append({"race_id": race_id, "sent_at": at, "channel": "CLAUDE_SESSION_ASSISTED"})
    OUT.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("build"); s.add_argument("date")
    s = sub.add_parser("assisted"); s.add_argument("date"); s.add_argument("race_id"); s.add_argument("--at")
    a = ap.parse_args()
    if a.cmd == "build":
        print(json.dumps(build(a.date)["summary"], ensure_ascii=False))
    else:
        add_assisted(a.date, a.race_id, a.at or dt.datetime.now(dt.timezone.utc).isoformat())


if __name__ == "__main__":
    main()

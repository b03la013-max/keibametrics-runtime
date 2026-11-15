"""Pre-start Owner delivery of a FINAL (or NO-BET) as a GitHub issue comment.

Owner approval 2026-11-15 19:50 JST: the ticket tree of every Production FINAL is
posted to the Owner delivery issue before the scheduled post; the Owner's GitHub
notification carries it to the phone. Never posts at or after post time, never
alters the FINAL, and records only that the comment was ACCEPTED by GitHub
(user ACK stays ACK_UNVERIFIED).
"""
from __future__ import annotations
import argparse, datetime as dt, json, os, urllib.request
from pathlib import Path

CHANNEL = Path(__file__).resolve().parents[1] / "runtime/jra_owner_delivery_channel.json"
VENUE = {"TKY": "東京", "KYO": "京都", "FKS": "福島", "NKY": "中山", "HSN": "阪神", "CKY": "中京",
         "KKR": "小倉", "NGT": "新潟", "SPP": "札幌", "HKD": "函館"}


def compose(race_id: str, post_at: str, tree: str | None, no_bet_reason: str | None = None) -> str:
    _, _, v, date, r = race_id.split("-")
    head = f"**【{VENUE.get(v, v)}{int(r[1:])}R】** {date[4:6]}/{date[6:]} 発走 {post_at[11:16]}"
    if tree is None:
        return f"{head} — **見送り**（{no_bet_reason or 'NO-BET'}）\n\n`{race_id}`"
    return f"{head}\n\n```\n{tree.rstrip()}\n```\n確率は未較正です。 `{race_id}`"


def deliver(race_id, post_at, body, *, now=None, post=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    if now >= dt.datetime.fromisoformat(post_at):
        return {"status": "SKIPPED_POST_TIME_PASSED", "race_id": race_id}
    issue = json.loads(CHANNEL.read_text())["issue_number"]
    post = post or _post_comment
    resp = post(issue, body)
    return {"status": "DELIVERY_ACCEPTED", "race_id": race_id, "issue": issue,
            "comment_url": resp.get("html_url"), "accepted_at": now.isoformat(), "user_ack": "ACK_UNVERIFIED"}


def _post_comment(issue, body):
    repo, token = os.environ["GITHUB_REPOSITORY"], os.environ["GITHUB_TOKEN"]
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/issues/{issue}/comments",
                                 data=json.dumps({"body": body}).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--race-id", required=True); ap.add_argument("--post-at", required=True)
    ap.add_argument("--tree"); ap.add_argument("--no-bet-reason"); ap.add_argument("--receipt")
    a = ap.parse_args()
    tree = Path(a.tree).read_text() if a.tree else None
    out = deliver(a.race_id, a.post_at, compose(a.race_id, a.post_at, tree, a.no_bet_reason))
    if a.receipt:
        Path(a.receipt).write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps(out, ensure_ascii=False))

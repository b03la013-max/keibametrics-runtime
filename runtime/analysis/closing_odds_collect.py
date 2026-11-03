"""Owner-triggered research collector. Default is a read-only local plan, no HTTP.

Never imported by Production. --execute requires explicit Owner/preflight
attestations; these attestations are not a substitute for Owner authorization.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import http.cookiejar
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from datetime import date, datetime, timezone
from pathlib import Path

import closing_odds_reader as reader

BASE = "https://www.jra.go.jp"
AGENT = "KeibaMetricsOfflineResearch/0.6"
ACTION = re.compile(r"doAction\(\s*['\"](/JRADB/access[DSO]\.html)['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*\)")


def actions(html):
    return sorted(set(ACTION.findall(html)))


def select_action(html, *, prefix, path=None):
    selected = [(p, t) for p, t in actions(html) if t.startswith(prefix) and (path is None or p == path)]
    if len(selected) != 1:
        raise ValueError("OFFICIAL_NAVIGATION_NOT_UNIQUE:" + prefix)
    return selected[0]


def closing_action(html, meeting_key, date8, race_no):
    prefix = "pw151ouS3" + meeting_key + f"{race_no:02d}" + date8 + "Z/"
    action = select_action(html, prefix=prefix, path="/JRADB/accessO.html")
    if not re.fullmatch(re.escape(prefix) + r"[0-9A-Fa-f]{2}", action[1]):
        raise ValueError("CLOSING_NAVIGATION_TOKEN_INVALID")
    return action


def require_approval(approval_ref, robots_reviewed, terms_reviewed):
    if not approval_ref or not approval_ref.strip() or not robots_reviewed or not terms_reviewed:
        raise ValueError("OWNER_APPROVAL_AND_ROBOTS_TERMS_REVIEW_REQUIRED")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("AUTOMATIC_REDIRECT_FORBIDDEN")


class OfficialClient:
    def __init__(self, *, approval_ref, robots_reviewed, terms_reviewed, interval=5.0, max_requests=300):
        require_approval(approval_ref, robots_reviewed, terms_reviewed)
        if interval < 5 or not 1 <= max_requests <= 500:
            raise ValueError("REQUEST_LIMITS_INVALID")
        self.interval, self.max_requests = float(interval), int(max_requests)
        self.last, self.count, self.robots = None, 0, None
        jar = http.cookiejar.CookieJar()  # Anonymous session only; never persisted or printed.
        self.opener = urllib.request.build_opener(NoRedirect(), urllib.request.HTTPCookieProcessor(jar))

    def _request(self, url, data=None, referer=None, *, robots_bootstrap=False):
        parsed = urllib.parse.urlparse(url)
        valid = parsed.scheme == "https" and parsed.netloc == "www.jra.go.jp" and not parsed.query and not parsed.fragment
        valid = valid and (parsed.path in {"/robots.txt", "/JRADB/accessS.html", "/JRADB/accessD.html", "/JRADB/accessO.html"}
                           or re.fullmatch(r"/keiba/calendar\d{4}/\d{4}/\d{1,2}/\d{4}\.html", parsed.path))
        if not valid:
            raise ValueError("OFFICIAL_REQUEST_URL_NOT_ALLOWLISTED")
        if not robots_bootstrap and (self.robots is None or not self.robots.can_fetch(AGENT, url)):
            raise ValueError("ROBOTS_PERMISSION_NOT_ESTABLISHED")
        if self.count >= self.max_requests:
            raise ValueError("MANUAL_REQUEST_BUDGET_EXCEEDED")
        if self.last is not None:
            time.sleep(max(0, self.interval - (time.monotonic() - self.last)))
        self.last = time.monotonic()
        self.count += 1
        headers = {"User-Agent": AGENT, "Accept": "text/html,text/plain;q=0.9"}
        if referer:
            headers["Referer"] = referer
        req = urllib.request.Request(url, data=data, headers=headers)
        with self.opener.open(req, timeout=30) as response:
            if response.status != 200 or response.geturl() != url:
                raise ValueError("OFFICIAL_RESPONSE_NOT_DIRECT_200")
            raw = response.read(4_000_001)
            if len(raw) > 4_000_000:
                raise ValueError("OFFICIAL_RESPONSE_TOO_LARGE")
            content_type = response.headers.get("Content-Type", "")
        return raw, content_type, datetime.now(timezone.utc).isoformat()

    def load_robots(self):
        raw, _, _ = self._request(BASE + "/robots.txt", robots_bootstrap=True)
        robots = urllib.robotparser.RobotFileParser(BASE + "/robots.txt")
        robots.parse(raw.decode("utf-8", errors="strict").splitlines())
        self.robots = robots
        delay = robots.crawl_delay(AGENT) or robots.crawl_delay("*") or 0
        self.interval = max(self.interval, delay)
        rate = robots.request_rate(AGENT) or robots.request_rate("*")
        if rate:
            self.interval = max(self.interval, rate.seconds / rate.requests)
        if not robots.can_fetch(AGENT, BASE + "/JRADB/accessO.html"):
            raise ValueError("ROBOTS_DENIES_CLOSING_ENDPOINT")

    def get(self, url):
        return self._request(url)

    def post(self, action, referer):
        path, token = action
        reader.official_url(BASE + path)
        return self._request(BASE + path, urllib.parse.urlencode({"cname": token}).encode("ascii"), referer)


def collection_plan(root, start, end, asof):
    # Reuse the analysis cohort/identity rules, never Production source code.
    import benter_second_stage as b
    inputs = b.Inputs(root)
    series, _, audit = inputs.load(start, end, asof)
    observations = {r["race_id"]: r for r in audit["observation_selection"]}
    plan, rejected = [], []
    for race in series["pre_signature"]:
        selected = observations[race.race_id]["selected_pre_signature_path"]
        source = inputs.read(Path(root) / selected)["artifact"]
        key = str(source.get("jra_meeting_key_discovered", ""))
        if not re.fullmatch(r"\d{10}", key):
            rejected.append({"race_id": race.race_id, "reason": "SAVED_MEETING_KEY_MISSING"})
            continue
        result = inputs.read(Path(root) / "runtime/results" / (race.race_id + ".json"))["official_result"]
        _, nonstarters, _ = b.result_outcome(result)
        plan.append({"race_id": race.race_id, "race_date": race.race_date, "post_at": race.post_at,
                     "meeting_key": key, "active_runner_ids": list(race.ids), "nonstarters": nonstarters})
    return plan, rejected, inputs.manifest


def rejected_capture(directory, context, raw, content_type, url, error):
    out = {"classification": "REJECTED_RESEARCH_CAPTURE_NOT_ELIGIBLE_ODDS", "race_id": context["race_id"],
           "captured_at": datetime.now(timezone.utc).isoformat(), "url": url, "content_type": content_type,
           "raw_html_base64": base64.b64encode(raw).decode("ascii"),
           "raw_sha256": hashlib.sha256(raw).hexdigest(), "reason": str(error)}
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / (context["race_id"] + "-" + out["raw_sha256"] + ".json")
    with target.open("x", encoding="utf-8") as f:
        f.write(reader.canonical(out) + "\n")


def collect(root, plan, client):
    root = Path(root)
    directory = root / "runtime/closing_odds"
    pending = [p for p in plan if not (directory / (p["race_id"] + ".json")).exists()]
    if not pending:
        return {"saved": 0, "skipped_existing": len(plan), "failures": [], "requests": 0}
    if any(reader.timestamp(p["post_at"]) >= datetime.now(timezone.utc) for p in pending):
        raise ValueError("CLOSING_COLLECTION_REQUIRES_COMPLETED_RACE_TIME")
    client.load_robots()
    days, failures, saved = {}, [], 0
    rejected_dir = root / "runtime/closing_odds_rejected" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    for context in pending:
        rid, key, day = context["race_id"], context["meeting_key"], context["race_date"]
        raw, content_type, url = None, "", None
        try:
            day8 = day.replace("-", "")
            if (key, day) not in days:
                calendar = f"{BASE}/keiba/calendar{day[:4]}/{day[:4]}/{int(day[5:7])}/{day8[4:]}.html"
                r0, ct, _ = client.get(calendar)
                entry = select_action(reader.decode_html(r0, ct)[0], prefix="pw01sli00")
                r1, ct, _ = client.post(entry, calendar)
                action = select_action(reader.decode_html(r1, ct)[0], prefix="pw01srl00" + key + day8 + "/")
                r2, ct, _ = client.post(action, BASE + entry[0])
                days[key, day] = (reader.decode_html(r2, ct)[0], BASE + action[0])
            day_html, referer = days[key, day]
            race_no = int(reader.identity(rid)[5])
            action = select_action(day_html, prefix="pw01sde01" + key + f"{race_no:02d}" + day8 + "/")
            raw, content_type, captured = client.post(action, referer)
            url = BASE + action[0]
            kwargs = dict(race_id=rid, expected_active=context["active_runner_ids"], expected_nonstarters=context["nonstarters"])
            try:
                capture = reader.build_capture(raw, url=url, captured_at=captured, content_type=content_type,
                                               request_cname=action[1], **kwargs)
            except ValueError as exc:
                # A result page containing only popularity is not an odds source.
                # Identity failure stays fatal, even when another odds link exists.
                if "HEADER" in str(exc):
                    raise
                closing = closing_action(reader.decode_html(raw, content_type)[0], key, day8, race_no)
                raw, content_type, captured = client.post(closing, url)
                url = BASE + closing[0]
                capture = reader.build_capture(raw, url=url, captured_at=captured, content_type=content_type,
                                               request_cname=closing[1], **kwargs)
            reader.save_capture(directory, capture)
            saved += 1
        except Exception as exc:
            if raw is not None:
                rejected_capture(rejected_dir, context, raw, content_type, url, exc)
            failures.append({"race_id": rid, "reason": type(exc).__name__ + ":" + str(exc)})
    return {"saved": saved, "skipped_existing": len(plan) - len(pending), "failures": failures, "requests": client.count}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from", dest="start", type=date.fromisoformat, required=True)
    parser.add_argument("--to", dest="end", type=date.fromisoformat, required=True)
    parser.add_argument("--asof", type=date.fromisoformat, required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--owner-approval-ref")
    parser.add_argument("--robots-reviewed", action="store_true")
    parser.add_argument("--terms-reviewed", action="store_true")
    parser.add_argument("--interval", type=float, default=5)
    parser.add_argument("--max-requests", type=int, default=300)
    args = parser.parse_args(argv)
    if not args.start <= args.end <= args.asof:
        parser.error("Require from <= to <= asof")
    if args.execute:
        require_approval(args.owner_approval_ref, args.robots_reviewed, args.terms_reviewed)
    plan, excluded, manifest = collection_plan(args.root, args.start, args.end, args.asof)
    if not args.execute:
        print(reader.canonical({"mode": "LOCAL_PLAN_NO_REQUESTS", "plan": plan, "excluded": excluded,
                                "input_files_sha256": manifest}))
        return
    client = OfficialClient(approval_ref=args.owner_approval_ref, robots_reviewed=args.robots_reviewed,
                            terms_reviewed=args.terms_reviewed, interval=args.interval, max_requests=args.max_requests)
    result = collect(args.root, plan, client)
    for path, expected in manifest.items():
        if hashlib.sha256((args.root / path).read_bytes()).hexdigest() != expected:
            raise ValueError("ORIGINAL_INPUT_CHANGED_DURING_COLLECTION:" + path)
    print(reader.canonical(result))
    if result["failures"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

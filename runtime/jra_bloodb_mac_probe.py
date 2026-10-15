"""Permission-gated subscriber DOM schema probe bound to a signed JRA SOURCE.

The report includes page structure and table *column labels*, never paid
horse-level ratings, row values, raw member HTML, cookies or login details.
It is intentionally diagnostic: does not save any purchased data or change BVI.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from bs4 import BeautifulSoup
from jra_bloodb_mac_collector import (
    BloodBError, HOME, PROFILE, ROOT, namekey, allowed_page, official_universe,
    private_dir, parse_rendered, utc_time, playwright_sync,
)
from jra_bloodb_mac_automation import discover_links, load_official
from jra_bloodb_mac_acceptance import queue_spec

PROFILE_ID = "BLOODB-MAC-LIVE-STRUCTURAL-PROBE-v0.1"


def safe_structure(html: str, official: list[dict]) -> dict:
    """Bounded, redacted DOM metadata; no body texts or subscriber table rows.

    Header texts are column schema only. An official horse name appearing in a
    header is explicitly redacted to avoid accidentally printing horse rows.
    """
    if not isinstance(html, str) or len(html.encode("utf-8")) > 2_500_000:
        raise BloodBError("BLOODB_PROBE_HTML_SIZE_INVALID")
    soup = BeautifulSoup(html, "html.parser")
    official_names = set(official_universe(official))
    tables = soup.select("table")
    shapes = []
    for table in tables[:12]:
        rows = table.select("tr")
        header = next((r for r in rows[:3] if len(r.find_all("th", recursive=False)) >= 2), None)
        fields = []
        if header is not None:
            for th in header.find_all("th", recursive=False)[:24]:
                raw = th.get_text(" ", strip=True)
                label = namekey(raw)
                if len(raw) > 40 or any(name in label for name in official_names):
                    fields.append("[REDACTED_OR_NOT_COLUMN]")
                else:
                    fields.append(raw[:40])
        shapes.append({
            "row_count": len(rows),
            "thead_count": len(table.select("thead")),
            "th_count": len(table.select("th")),
            "td_count": len(table.select("td")),
            "column_headers": fields,
        })
    # Only bounded counts and schema headings leave this function.
    return {
        "html_bytes_bucket": "SMALL" if len(html) < 25_000 else
                             ("MEDIUM" if len(html) < 250_000 else "LARGE"),
        "tables_total": len(tables),
        "table_shapes": shapes,
        "forms": len(soup.select("form")),
        "password_inputs": len(soup.select("input[type=password]")),
        "iframes": len(soup.select("iframe")),
        "scripts": len(soup.select("script")),
        "links": len(soup.select("a[href]")),
        "selects": len(soup.select("select")),
        "options": len(soup.select("option")),
        "tr": len(soup.select("tr")),
        "td": len(soup.select("td")),
        "div": len(soup.select("div")),
        "spans": len(soup.select("span")),
    }


def probe_context(context, spec: dict, *, clock=None) -> dict:
    """Inspect the exact listed JRA race without saving proprietary page rows.

    Incomplete live DOM, missing/ambiguous venue link, expired login, and
    unsupported markup are reported explicitly, not treated as valid capture.
    """
    clock = clock or (lambda: datetime.now(timezone.utc))
    cutoff = utc_time(spec["prediction_cutoff"])
    if clock() >= cutoff:
        raise BloodBError("BLOODB_PROBE_PREDICTION_CUTOFF_EXPIRED")
    official, source = load_official(spec)
    if source["level"] != "SOURCE_ED25519_ONLY_NOT_INDEPENDENT_OIDC_ATTESTED_HERE":
        raise BloodBError("BLOODB_PROBE_SIGNED_SOURCE_REQUIRED")
    if spec.get("jra_signed_source_artifact_sha256") != source["source_artifact_sha256"]:
        raise BloodBError("BLOODB_PROBE_QUEUE_SOURCE_HASH_MISMATCH")

    report = {
        "profile": PROFILE_ID,
        "race_id": spec["race_id"],
        "official_runner_count": len(official),
        "status": "BLOCKED",
        "index": None, "detail": None,
        "observed_race_link_count": 0,
        "matched_runner_count": None,
        "parser_status": "NOT_RUN",
        "block_reason": None,
        "provider_permission": "OPERATOR_ASSERTION_NOT_PROVIDER_ATTESTATION",
        "jra_source_verification": source["level"],
        "independent_oidc_verified_here": False,
        "paid_content_persisted": False,
        "paid_rows_emitted": False,
        "production_authority": False, "bvi_authority": False,
        "krs_authority": False, "final_authority": False,
        "oos_increment": 0,
    }

    page = context.new_page()
    try:
        response = page.goto(ROOT + "/allsel", wait_until="domcontentloaded", timeout=30000)
        if response is None or response.status != 200 or page.url.rstrip("/") != ROOT + "/allsel":
            report["block_reason"] = "BLOODB_INDEX_LOGIN_OR_REDIRECT"
            return report
        if clock() >= cutoff:
            raise BloodBError("BLOODB_PROBE_PREDICTION_CUTOFF_EXPIRED")
        index_html = page.content()
        report["index"] = safe_structure(index_html, official)
        if report["index"]["password_inputs"]:
            report["block_reason"] = "BLOODB_LOGIN_REQUIRED"
            return report

        try:
            options = discover_links(index_html, date_text=spec["race_date"],
                                     race_no=int(spec["race_no"]),
                                     venue=spec.get("venue"))
        except BloodBError as exc:
            report["block_reason"] = str(exc).split(":")[0]
            return report
        report["observed_race_link_count"] = len(options)
        if len(options) != 1:
            report["block_reason"] = "BLOODB_RACE_LINK_MISSING_OR_AMBIGUOUS"
            return report
        if options[0]["observed_venue"] != spec.get("venue"):
            report["block_reason"] = "BLOODB_VENUE_NOT_INDEPENDENTLY_LABELED"
            return report
        target = allowed_page(options[0]["url"])
        response = page.goto(target, wait_until="domcontentloaded", timeout=30000)
        if response is None or response.status != 200 or page.url != target:
            report["block_reason"] = "BLOODB_DETAIL_LOGIN_OR_REDIRECT"
            return report
        if clock() >= cutoff:
            raise BloodBError("BLOODB_PROBE_PREDICTION_CUTOFF_EXPIRED")
        detail_html = page.content()
        report["detail"] = safe_structure(detail_html, official)
        if report["detail"]["password_inputs"]:
            report["block_reason"] = "BLOODB_DETAIL_LOGIN_REQUIRED"
            return report
        try:
            parsed = parse_rendered(detail_html, official)
        except BloodBError as exc:
            report["parser_status"] = "UNSUPPORTED_OR_INCOMPLETE"
            report["block_reason"] = str(exc).split(":")[0]
            return report
        if clock() >= cutoff:
            raise BloodBError("BLOODB_PROBE_PREDICTION_CUTOFF_EXPIRED")
        report["parser_status"] = "FULL_RUNNER_SCHEMA_MATCH"
        report["matched_runner_count"] = parsed["horse_count"]
        report["status"] = "LOCAL_MEMBER_DOM_SCHEMA_COMPATIBLE"
        return report
    finally:
        page.close()


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Inspect member DOM structure without paid horse data export")
    p.add_argument("--race-id", required=True, help="Exact JRA race ID from private signed-SOURCE queue")
    p.add_argument("--queue", type=Path, default=HOME / "bloodb_queue.json")
    p.add_argument("--profile", type=Path, default=PROFILE)
    p.add_argument("--provider-permission-confirmed", action="store_true")
    args = p.parse_args(argv)
    if not args.provider_permission_confirmed:
        raise BloodBError("PROVIDER_AUTOMATED_ACCESS_PERMISSION_MUST_BE_CONFIRMED")
    spec = queue_spec(args.queue, args.race_id)
    profile = args.profile.expanduser()
    if not profile.is_dir():
        raise BloodBError("BLOODB_LOCAL_SUBSCRIBER_LOGIN_PROFILE_REQUIRED")
    with playwright_sync()() as pl:
        context = pl.chromium.launch_persistent_context(
            str(private_dir(profile)), headless=True, accept_downloads=False)
        try:
            report = probe_context(context, spec)
        finally:
            context.close()
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["status"] == "LOCAL_MEMBER_DOM_SCHEMA_COMPATIBLE" else 2


if __name__ == "__main__":
    raise SystemExit(main())

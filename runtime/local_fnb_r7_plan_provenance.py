"""R7 offline FNB day-plan provenance validator.

Checks persisted official observations against the actual bundled NAR card bytes.
Never fetches an external URL or grants SOURCE licensing, Owner, numeric consumer
permission, signed-source recognition, OOS registration or Delivery authority.
An internally consistent plan is still DISCOVERY-ONLY and needs a fresh,
appropriately licensed Signed SOURCE for every formal race.
"""
from __future__ import annotations

import base64
from datetime import datetime, date, timedelta, timezone
import gzip
import hashlib
import json
import re
import io
from urllib.parse import urlsplit, parse_qs

from runtime.local_race_day_dispatcher import sha
from runtime.local_physical.nar_runner_universe import (
    canonical_name, extract_runner_universe_from_tables,
)
from runtime.local_physical.source_acquisition import _decode, _html_tables, _html_text

JST = timezone(timedelta(hours=9))
PROFILE = "KM-FNB-R7-FROZEN-DISCOVERY-PLAN-PROVENANCE-v1"
MAX_CARD_BYTES = 900000


def _date_time(value):
    t = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if t.tzinfo is None:
        raise ValueError("FNB_PLAN_TIMEZONE_REQUIRED")
    return t.astimezone(JST)


def _parse_raw(snapshot):
    if (snapshot.get("source_class") != "OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT"
            or snapshot.get("authority") != "NAR_OFFICIAL"
            or snapshot.get("official") is not True
            or type(snapshot.get("http_status")) is not int
            or snapshot["http_status"] != 200):
        raise ValueError("OFFICIAL_CARD_AUTHORITY_OR_STATUS_INVALID")
    actual_snapshot_hash = sha({k: v for k, v in snapshot.items()
                                if k != "snapshot_sha256"})
    if actual_snapshot_hash != snapshot.get("snapshot_sha256"):
        raise ValueError("OFFICIAL_CARD_SNAPSHOT_HASH_MISMATCH")
    encoded = snapshot.get("raw_gzip_b64")
    if not isinstance(encoded, str) or len(encoded) > 2 * MAX_CARD_BYTES:
        raise ValueError("OFFICIAL_CARD_RAW_MISSING_OR_OVERSIZE")
    try:
        packed = base64.b64decode(encoded, validate=True)
        with gzip.GzipFile(fileobj=io.BytesIO(packed), mode="rb") as f:
            raw = f.read(MAX_CARD_BYTES + 1)
    except (ValueError, OSError, EOFError) as exc:
        raise ValueError("OFFICIAL_CARD_RAW_DECODE_FAILED") from exc
    if len(raw) > MAX_CARD_BYTES:
        raise ValueError("OFFICIAL_CARD_RAW_TOO_LARGE")
    if (hashlib.sha256(raw).hexdigest() != snapshot.get("raw_sha256")
            or snapshot.get("byte_count") != len(raw)):
        raise ValueError("OFFICIAL_CARD_RAW_HASH_OR_LENGTH_MISMATCH")
    html = _decode(raw, str(snapshot.get("content_type") or ""))
    header = re.sub(r"\s+", "", _html_text(html)).split("競走馬", 1)[0]
    runners = extract_runner_universe_from_tables(_html_tables(html))
    fetched = _date_time(snapshot.get("fetched_at"))
    return header, runners, fetched


def verify_fnb_plan(plan: dict, race_date: str) -> dict:
    """Verify stored raw evidence; do not certify current official availability."""
    failures = []
    observations = []
    def fail(s):
        failures.append(str(s))

    if not isinstance(plan, dict):
        return {"profile": PROFILE, "status": "PLAN_RAW_INTEGRITY_FAILED",
                "raw_integrity_verified": False, "issues": ["PLAN_NOT_OBJECT"],
                "races": [], "source_license": "NOT_VERIFIED",
                "signed_source": "NOT_VERIFIED", "formal_authority_granted": False}
    try:
        if date.fromisoformat(race_date).isoformat() != race_date:
            raise ValueError("FNB_DATE_INVALID")
        if (plan.get("family_id"), plan.get("venue_id"), plan.get("race_date")) != (
                "LOCAL", "FNB", race_date):
            fail("PLAN_DAY_OR_VENUE_MISMATCH")
        if plan.get("plan_sha256") != sha({k: v for k, v in plan.items()
                                           if k != "plan_sha256"}):
            fail("PLAN_SHA_MISMATCH")
        if (plan.get("status") != "DISCOVERY_ONLY_NOT_REGISTERED_NOT_SIGNED_SOURCE"
                or plan.get("prediction_freeze") is not False):
            fail("PLAN_SCOPE_NOT_DISCOVERY_ONLY")
        saved = plan.get("official_snapshots")
        if not isinstance(saved, list):
            saved = []
            fail("PLAN_OFFICIAL_SNAPSHOTS_MISSING")
        # The official daily RaceList must independently link exactly the
        # same 12 races. A collection of 12 individual cards alone does not
        # prove a coherent official meeting.
        menus = [x for x in saved if isinstance(x, dict)
                 and x.get("source_class") == "OFFICIAL_DAY_MENU"]
        if len(menus) != 1:
            fail("PLAN_DAY_MENU_COUNT_NOT_ONE")
        else:
            menu = menus[0]
            try:
                from runtime.local_race_day_dispatcher import CardLinks
                u = urlsplit(str(menu.get("final_url") or ""))
                q = parse_qs(u.query)
                if ((u.scheme, u.hostname, u.path) != (
                        "https", "www.keiba.go.jp", "/KeibaWeb/TodayRaceInfo/RaceList")
                        or q.get("k_babaCode") != ["19"]
                        or q.get("k_raceDate") != [race_date.replace("-", "/")]):
                    raise ValueError("DAY_MENU_URL_IDENTITY_INVALID")
                if (menu.get("official") is not True
                        or menu.get("authority") != "NAR_OFFICIAL"
                        or menu.get("http_status") != 200
                        or menu.get("snapshot_sha256") !=
                           sha({k: v for k, v in menu.items()
                                if k != "snapshot_sha256"})):
                    raise ValueError("DAY_MENU_AUTHORITY_OR_HASH_INVALID")
                packed = base64.b64decode(menu["raw_gzip_b64"], validate=True)
                with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
                    raw = stream.read(MAX_CARD_BYTES + 1)
                if (len(raw) > MAX_CARD_BYTES
                        or hashlib.sha256(raw).hexdigest() != menu.get("raw_sha256")
                        or len(raw) != menu.get("byte_count")):
                    raise ValueError("DAY_MENU_RAW_HASH_INVALID")
                links = CardLinks("FNB", race_date)
                links.feed(_decode(raw, str(menu.get("content_type") or "")))
                if sorted(links.races) != list(range(1, 13)):
                    raise ValueError("DAY_MENU_NOT_ALL_12_RACES")
            except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
                fail("PLAN_DAY_MENU_NOT_VERIFIED:" + str(exc))
        cards = {}
        for snapshot in saved:
            if not isinstance(snapshot, dict):
                fail("PLAN_SNAPSHOT_NOT_OBJECT")
                continue
            if snapshot.get("source_class") != "OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT":
                continue
            source_id = snapshot.get("source_id")
            if not isinstance(source_id, str):
                fail("PLAN_CARD_SOURCE_ID_INVALID")
                continue
            if source_id in cards:
                fail("PLAN_DUPLICATE_OFFICIAL_CARD:" + source_id)
            cards[source_id] = snapshot
        rows = plan.get("races")
        if not isinstance(rows, list):
            rows = []
            fail("PLAN_RACES_MISSING")
        numbers = []
        posts = []
        for row in rows:
            if not isinstance(row, dict):
                fail("PLAN_RACE_ROW_NOT_OBJECT")
                continue
            fields = row.get("fields")
            if not isinstance(fields, dict):
                fail("PLAN_RACE_FIELDS_MISSING")
                continue
            number = fields.get("race_no")
            if type(number) is not int or not 1 <= number <= 12:
                fail("PLAN_RACE_NUMBER_INVALID")
                continue
            numbers.append(number)
            prefix = f"R{number:02d}"
            if (fields.get("venue_id") != "FNB"
                    or fields.get("race_date") != race_date
                    or row.get("race_key") !=
                       f"FNB-{race_date.replace('-', '')}-{prefix}-LIVE-R1"
                    or row.get("intent_status") !=
                       "DRAFT_NOT_FORMAL_STATIC_NOT_DISPATCHED"):
                fail(prefix + ":RACE_IDENTITY_OR_DRAFT_SCOPE_INVALID")
            try:
                post = _date_time(fields.get("scheduled_post_at"))
                cutoff = _date_time(fields.get("prediction_cutoff"))
                if (post.date().isoformat() != race_date
                        or not 120 <= (post-cutoff).total_seconds() <= 3600):
                    raise ValueError("POST_OR_CUTOFF_INVALID")
                posts.append((number, post))
            except (ValueError, TypeError):
                fail(prefix + ":POST_OR_CUTOFF_INVALID")
                continue
            expected_id = (
                f"NAR-FNB-{race_date.replace('-', '')}-{prefix}-RACE-CARD")
            card = cards.get(expected_id)
            if card is None:
                fail(prefix + ":OFFICIAL_RAW_CARD_MISSING")
                continue
            url = urlsplit(str(card.get("final_url") or ""))
            params = parse_qs(url.query)
            if ((url.scheme, url.hostname, url.path) != (
                    "https", "www.keiba.go.jp", "/KeibaWeb/TodayRaceInfo/DebaTable")
                    or params.get("k_babaCode") != ["19"]
                    or params.get("k_raceDate") != [race_date.replace("-", "/")]
                    or params.get("k_raceNo") != [str(number)]):
                fail(prefix + ":OFFICIAL_CARD_URL_IDENTITY_INVALID")
                continue
            try:
                header, parsed, fetched = _parse_raw(card)
                d = date.fromisoformat(race_date)
                wanted = rf"{d.year}年{d.month}月{d.day}日.*?船橋第{number}競走(\d{{1,2}}:\d{{2}})発走"
                match = re.search(wanted, header)
                if not match or match.group(1) != post.strftime("%H:%M"):
                    raise ValueError("OFFICIAL_CARD_PRINTED_CLOCK_MISMATCH")
                if row.get("source_basis_sha256") != card.get("snapshot_sha256"):
                    raise ValueError("SOURCE_BASIS_SNAPSHOT_MISMATCH")
                universe = row.get("declared_runner_universe")
                if not isinstance(universe, dict):
                    raise ValueError("DECLARED_RUNNER_UNIVERSE_MISSING")
                runners = universe.get("runners")
                if not isinstance(runners, list):
                    raise ValueError("DECLARED_RUNNERS_MISSING")
                if (universe.get("source_id") != expected_id
                        or universe.get("source_snapshot_sha256") != card.get("snapshot_sha256")
                        or universe.get("runner_count") != len(runners)
                        or universe.get("runner_universe_sha256") !=
                           sha({k: v for k, v in universe.items()
                                if k != "runner_universe_sha256"})):
                    raise ValueError("DECLARED_UNIVERSE_LINEAGE_OR_COUNT_MISMATCH")
                comparable = lambda xs: sorted(
                    (int(r["horse_no"]), canonical_name(r["name"])) for r in xs)
                if comparable(parsed) != comparable(runners):
                    raise ValueError("DECLARED_RUNNERS_DISAGREE_WITH_OFFICIAL_RAW")
                observations.append({
                    "race_no": number,
                    "official_post_at": post.isoformat(),
                    "raw_sha256": card["raw_sha256"],
                    "card_snapshot_sha256": card["snapshot_sha256"],
                    "runner_count": len(parsed),
                    "planned_required_cells": 29 * len(parsed),
                    "observation_relation_to_cutoff":
                        "BEFORE_CUTOFF" if fetched < cutoff else
                        "AT_OR_AFTER_CUTOFF_DIAGNOSTIC_ONLY",
                })
            except (ValueError, OSError, TypeError, KeyError, AttributeError) as exc:
                fail(prefix + ":" + str(exc))
        if sorted(numbers) != list(range(1, 13)):
            fail("PLAN_12_RACE_SET_MISSING_OR_DUPLICATE")
        if sorted(posts, key=lambda x: x[0]) != sorted(posts, key=lambda x: x[1]):
            fail("PLAN_POST_TIMES_NOT_ASCENDING")
        if len(observations) != 12:
            fail("PLAN_OFFICIAL_RAW_COVERAGE_NOT_12_OF_12")
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        fail("PLAN_VERIFICATION_INTERNAL_HOLD:" + type(exc).__name__)
    good = not failures
    return {"profile": PROFILE,
            "status": "DISCOVERY_RAW_INTEGRITY_VERIFIED_ONLY" if good
                      else "PLAN_RAW_INTEGRITY_FAILED",
            "raw_integrity_verified": good,
            "official_raw_reparsed_race_count": len(observations),
            "total_declared_runners": sum(x["runner_count"] for x in observations),
            "planned_required_cells": sum(x["planned_required_cells"] for x in observations),
            "races": observations, "issues": failures[:50],
            "additional_issue_count": max(0, len(failures)-50),
            "source_license": "NOT_VERIFIED",
            "signed_source": "NOT_VERIFIED",
            "formal_authority_granted": False,
            "prestart_delivery_proven": False,
            "independent_issuer_trust": "NOT_VERIFIED",
            "not_live_snapshot": True}

"""Kawasaki SOURCE using South Kanto's provider IDs and official observations."""
from __future__ import annotations

import base64
import gzip
import hashlib
import io
import re
from datetime import date, datetime, timezone

from runtime import urw_nankan_reference_source as nankan
from runtime.local_physical.source_acquisition import (
    SOURCE_PROFILE, SOURCE_SCHEMA, sha_obj, snapshot_from_bytes, verify_source_artifact,
)

PROFILE = "KM-LOCAL-NANKAN-KAW-SOURCE-MANIFEST-v1"
PROVIDER = nankan.PROVIDER
CHANGES = nankan.ORIGIN + "/henko_info/00000000000000.do"
BUNDLE_KEYS = ("source_id", "raw_sha256", "snapshot_sha256", "fetched_at", "final_url")
SOURCE_CLASSES = (
    "OFFICIAL_VENUE_CALENDAR",
    "OFFICIAL_RACE_PROGRAM",
    "OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT",
    "OFFICIAL_ACTIVE_BETTING_UNIVERSE",
    "OFFICIAL_RACE_CHANGES",
)


def _require(condition, code):
    if not condition:
        raise nankan.NankanError(code)


def _time(value):
    stamp = datetime.fromisoformat(value)
    _require(stamp.utcoffset() is not None, "NANKAN_KAW_TIMEZONE_REQUIRED")
    return stamp


def validate_request(request):
    day = date.fromisoformat(request["race_date"])
    number = request["race_no"]
    _require(request.get("family_id") == "LOCAL" and request.get("venue_id") == "KAW"
             and type(number) is int and 1 <= number <= 12, "NANKAN_KAW_RACE_SCOPE")
    race_prefix = f"KM-LOCAL-KAW-{day:%Y%m%d}-R{number:02d}-LIVE-R"
    _require(re.fullmatch(race_prefix + r"[1-9][0-9]*", request["race_id"]),
             "NANKAN_KAW_EXECUTION_ID")
    cutoff = _time(request["prediction_cutoff"])
    _require(cutoff.astimezone(nankan.JST).date() == day, "NANKAN_KAW_CUTOFF_DAY")
    return day.isoformat(), number, cutoff


def _race(request, calendar, program):
    day, number, cutoff = validate_request(request)
    program_url = nankan.program_link(calendar, day, venue_id="KAW")
    races = nankan.parse_program(program, program_url, day, venue_id="KAW")
    _require(number <= len(races), "NANKAN_KAW_RACE_NOT_ON_PROGRAM")
    race = races[number - 1]
    post = _time(race["scheduled_post_at"])
    _require(cutoff < post, "NANKAN_KAW_CUTOFF_NOT_BEFORE_POST")
    if request.get("scheduled_post_at"):
        _require(_time(request["scheduled_post_at"]) == post, "NANKAN_KAW_OFFICIAL_POST_CHANGED")
    return {**race, "prediction_cutoff": request["prediction_cutoff"]}, program_url


def _manifest(race, program_url):
    race_id = race["provider_race_id"]
    urls = (nankan.CALENDAR, program_url, nankan.ORIGIN + f"/uma_shosai/{race_id}.do",
            nankan.ORIGIN + f"/odds/{race_id}01.do", CHANGES)
    return [
        {"source_id": f"NANKAN-{race_id}-{kind}", "source_class": kind, "url": url,
         "authority": PROVIDER, "priority": 100, "official": True, "required": True, "extract": []}
        for kind, url in zip(SOURCE_CLASSES, urls, strict=True)
    ]


def _derive(request, observations, freeze_at, *, original_snapshots=None):
    day, _, cutoff = validate_request(request)
    frozen = _time(freeze_at)
    _require(len(observations) == len(SOURCE_CLASSES) and frozen < cutoff,
             "NANKAN_KAW_SOURCE_COUNT_OR_CUTOFF")
    race, program_url = _race(request, observations[0][1], observations[1][1])
    manifest = _manifest(race, program_url)
    snapshots = []
    previous_fetch = None
    for index, (spec, (meta, raw)) in enumerate(zip(manifest, observations, strict=True)):
        _require(meta.get("url") == spec["url"] and meta.get("http_status") == 200
                 and 0 < len(raw) <= nankan.MAX_BYTES
                 and hashlib.sha256(raw).hexdigest() == meta.get("raw_sha256"),
                 "NANKAN_KAW_RAW_IDENTITY")
        fetched = _time(meta["fetched_at"])
        _require(fetched.astimezone(nankan.JST).date().isoformat() == day and fetched <= frozen
                 and (previous_fetch is None or fetched >= previous_fetch),
                 "NANKAN_KAW_CAPTURE_TIME")
        previous_fetch = fetched
        snapshot, errors = snapshot_from_bytes(
            spec, raw, final_url=meta["url"], status_code=200, fetched_at=meta["fetched_at"],
            prediction_cutoff=request["prediction_cutoff"], headers={"content-type": "text/html"},
            gzip_mtime=0,
        )
        _require(not errors, "NANKAN_KAW_SNAPSHOT_FAILED")
        policy = meta.get("source_policy")
        _require(isinstance(policy, dict) and policy.get("robots_url") == nankan.ROBOTS
                 and policy.get("terms_url") == nankan.TERMS
                 and policy.get("status") in {200, 404}
                 and (policy.get("status") == 200 and re.fullmatch(r"[0-9a-f]{64}", policy.get("robots_sha256") or "")
                      or policy.get("status") == 404 and policy.get("robots_sha256") is None)
                 and _time(policy["checked_at"]) <= fetched, "NANKAN_KAW_ROBOTS_EVIDENCE_REQUIRED")
        snapshot["source_access_policy"] = policy
        snapshot["snapshot_sha256"] = sha_obj({k: v for k, v in snapshot.items() if k != "snapshot_sha256"})
        if original_snapshots is not None:
            original = original_snapshots[index]
            # Encoders can pack identical raw bytes differently across zlib versions.
            keys = {"raw_gzip_b64", "snapshot_sha256"}
            _require({k: v for k, v in snapshot.items() if k not in keys}
                     == {k: v for k, v in original.items() if k not in keys},
                     "NANKAN_KAW_SNAPSHOT_CHANGED")
            snapshot = original
        snapshots.append(snapshot)

    card, odds, changes = snapshots[2:]
    card_meta, card_raw = observations[2]
    exclusions = []
    parsed = nankan.parse_card(card_raw, race, card_meta["url"], excluded_rows=exclusions)
    _require(not exclusions, "NANKAN_KAW_EXCLUSION_IDENTITY_UNRESOLVED")
    nankan.verify_history_asof(parsed, card_meta["fetched_at"])
    odds_meta, odds_raw = observations[3]
    change_meta, change_raw = observations[4]
    current_odds = nankan.parse_current_odds(odds_raw, race, odds_meta, parsed)
    current_changes = nankan.parse_current_changes(change_raw, race, change_meta, parsed)
    _require(current_odds["provider_display_at"], "NANKAN_KAW_ODDS_TIME_UNKNOWN")
    _require(current_changes["target_race_change_status"] != "UNKNOWN",
             "NANKAN_KAW_TARGET_CHANGES_UNKNOWN")
    if current_changes["items"]:
        _require(current_changes["provider_display_at"], "NANKAN_KAW_CHANGES_TIME_UNKNOWN")
    odds_by_id = {row["runner_id"]: row for row in current_odds["runners"]}
    changes_by_id = {}
    for item in current_changes["items"]:
        changes_by_id.setdefault(item["runner_id"], []).append(item)

    declared, active, statuses, facts = [], [], [], {}
    for row in sorted(parsed, key=lambda row: row["horse_no"]):
        rid = row["runner_id"]
        betting = odds_by_id[rid]
        items = changes_by_id.get(rid, [])
        cancelled = any(item["status"] == "CANCELLED" for item in items)
        _require(cancelled == (row["status"] == "CANCELLED") == (betting["status"] == "CANCELLED"),
                 "NANKAN_KAW_CANCELLATION_CONFLICT")
        for item in items:
            if item["status"] == "CANCELLED":
                continue
            jockeys = item["jockey_names_observed"]
            _require(item["change_type"] == "騎手変更" and len(jockeys) == 2
                     and jockeys[-1] == row["current_jockey"], "NANKAN_KAW_CHANGE_NOT_RECONCILED")
        runner = {"runner_id": rid, "horse_no": row["horse_no"], "frame_no": row["frame_no"],
                  "name": row["name"]}
        declared.append(runner)
        statuses.append({
            "runner_id": rid, "name": row["name"], "status": "CANCELLED" if cancelled else "ACTIVE",
            "reason": "EXPLICIT_OFFICIAL_ODDS_CANCELLATION" if cancelled else "OFFICIAL_ODDS_ACTIVE",
            "evidence_sources": [item["source_id"] for item in (card, odds, changes)],
        })
        if not cancelled:
            _require(betting["betting_membership_observed"], "NANKAN_KAW_BETTING_MEMBERSHIP_UNKNOWN")
            _require(row["frame_no"] and row["current_body_weight"] is not None
                     and row["current_load"] is not None and row["current_jockey"] != "UNKNOWN",
                     "NANKAN_KAW_CURRENT_CARD_FACTS_MISSING")
            active.append(runner)
        facts[rid] = {**row, "odds": betting["win_odds"], "current_odds": betting["win_odds"],
                      "status": statuses[-1]["status"], "active_verified": not cancelled,
                      "missingness": [entry for entry in row["missingness"] if entry not in
                                      {"CURRENT_ACTIVE_NOT_VERIFIED", "CURRENT_ODDS_UNKNOWN"}],
                      "race_card_source_id": card["source_id"],
                      "race_card_fetched_at": card["fetched_at"],
                      "race_card_snapshot_sha256": card["snapshot_sha256"]}
    _require(len(active) >= 2, "NANKAN_KAW_ACTIVE_UNIVERSE_INCOMPLETE")
    dom = nankan.DOM(nankan.decode(card_raw)).root
    header = nankan._verify_race_header(dom, race)
    subtitle = nankan.one(dom.all("p", "nk23_c-tab1__subtitle"), "NANKAN_CARD_HEADER_UNKNOWN")
    witness = subtitle.parent.text() if subtitle.parent is not dom else header
    conditions = set(re.findall(r"馬場\s*[:：]\s*(?:ダート|ダ)?\s*(不良|稍重|良|重|不|稍)(?![\w])", witness))
    _require(len(conditions) == 1, "NANKAN_KAW_TRACK_CONDITION_UNKNOWN")
    condition = next(iter(conditions))
    condition = {"不": "不良", "稍": "稍重"}.get(condition, condition)
    classes = re.findall(r"(?<![A-Z0-9])[ABC][1-3](?![A-Z0-9])", race["race_name"])
    heading = {"distance": race["distance"], "surface": "dirt",
               "class": "_".join(dict.fromkeys(classes)) or "UNKNOWN",
               "header_witness": header, "header_sha256": hashlib.sha256(header.encode()).hexdigest()}
    normalized = {
        name: {"value": value, "authority": PROVIDER, "official": True, "cutoff_relation": "PRE_CUTOFF",
               "source_id": card["source_id"], "snapshot_sha256": card["snapshot_sha256"]}
        for name, value in (("start_time", race["scheduled_post_at"][11:16]),
                            ("track_condition", condition))
    }
    def universe(kind, runners):
        result = {"profile": PROFILE, "universe_type": kind, "source_id": card["source_id"],
                  "source_snapshot_sha256": card["snapshot_sha256"], "runners": runners,
                  "runner_count": len(runners)}
        if kind == "ACTIVE":
            result["status_registry_sha256"] = sha_obj(statuses)
        result["runner_universe_sha256"] = sha_obj(result)
        return result

    declared_universe = universe("DECLARED", declared)
    active_universe = universe("ACTIVE", active)
    artifact = {
        "schema": SOURCE_SCHEMA, "profile": SOURCE_PROFILE, "source_manifest_profile": PROFILE,
        "provider": PROVIDER, "race_id": request["race_id"],
        "source_race_context": {k: race[k] for k in ("venue_id", "race_date", "race_no")},
        "provider_race_id": race["provider_race_id"], "provider_day_id": race["provider_day_id"],
        "prediction_cutoff": request["prediction_cutoff"], "scheduled_post_at": race["scheduled_post_at"],
        "source_freeze_at": freeze_at, "required_source_manifest": manifest,
        "required_source_manifest_sha256": sha_obj(manifest), "sources": snapshots,
        "raw_source_bundle_sha256": sha_obj([{k: s[k] for k in BUNDLE_KEYS} for s in snapshots]),
        "normalized_evidence": normalized, "normalized_evidence_sha256": sha_obj(normalized),
        "race_heading": heading, "parsed_nankan_facts": facts,
        "odds_provider_display_at": current_odds["provider_display_at"],
        "changes_provider_display_at": current_changes["provider_display_at"],
        "declared_runner_universe": declared_universe, "active_runner_universe": active_universe,
        "official_runner_universe": active_universe,
        "official_runner_universe_sha256": active_universe["runner_universe_sha256"],
        "official_declared_runner_universe_sha256": declared_universe["runner_universe_sha256"],
        "runner_status_registry": statuses, "runner_status_registry_sha256": sha_obj(statuses),
        "conflicts": [], "missing_required_sources": [], "stale_sources": [], "post_cutoff_sources": [],
        "formal_ready": True, "errors": [], "public_redistribution_authorized": False,
    }
    artifact["source_snapshot_sha256"] = sha_obj(artifact)
    return artifact


def acquire(request, get, *, now=lambda: datetime.now(timezone.utc)):
    """Call only with a provider-scoped, permission-checked fetcher."""
    day, number, cutoff = validate_request(request)
    _require(now() < cutoff, "NANKAN_KAW_CUTOFF_PASSED")
    calendar = get(nankan.CALENDAR)
    program_url = nankan.program_link(calendar[1], day, venue_id="KAW")
    program = get(program_url)
    race, _ = _race(request, calendar[1], program[1])
    _require(race["race_no"] == number, "NANKAN_KAW_RACE_SCOPE")
    snapshots = [calendar, program]
    for spec in _manifest(race, program_url)[2:]:
        _require(now() < cutoff, "NANKAN_KAW_CUTOFF_PASSED")
        snapshots.append(get(spec["url"]))
    return _derive(request, snapshots, now().isoformat())


def verify(artifact):
    """Re-derive all observations from retained bytes. Verify the envelope separately."""
    _require(artifact.get("source_manifest_profile") == PROFILE, "NANKAN_KAW_PROFILE_REQUIRED")
    snapshots = artifact["sources"]
    _require(len(snapshots) == len(SOURCE_CLASSES), "NANKAN_KAW_SOURCE_COUNT_OR_CUTOFF")
    observations = []
    for snapshot in snapshots:
        encoded = snapshot["raw_gzip_b64"]
        _require(len(encoded) <= 2 * nankan.MAX_BYTES, "NANKAN_KAW_RAW_SIZE")
        with gzip.GzipFile(fileobj=io.BytesIO(base64.b64decode(encoded, validate=True))) as stream:
            raw = stream.read(nankan.MAX_BYTES + 1)
        _require(len(raw) <= nankan.MAX_BYTES, "NANKAN_KAW_RAW_SIZE")
        observations.append(({"url": snapshot["final_url"], "http_status": snapshot["http_status"],
                              "fetched_at": snapshot["fetched_at"], "raw_sha256": snapshot["raw_sha256"],
                              "source_policy": snapshot["source_access_policy"]}, raw))
    _require(verify_source_artifact(artifact)[0], "NANKAN_KAW_SOURCE_HASH_INVALID")
    request = {"family_id": "LOCAL", **artifact["source_race_context"],
               "race_id": artifact["race_id"], "prediction_cutoff": artifact["prediction_cutoff"],
               "scheduled_post_at": artifact["scheduled_post_at"]}
    expected = _derive(request, observations, artifact["source_freeze_at"],
                       original_snapshots=snapshots)
    _require(expected == artifact, "NANKAN_KAW_DERIVED_SOURCE_CHANGED")
    return expected["parsed_nankan_facts"]

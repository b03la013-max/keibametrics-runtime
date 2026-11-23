#!/usr/bin/env python3
"""Atomic LOCAL development claims for automatic and on-demand Work sessions.

Shared source: coordination/local_work_claims.json on coord/local-edit-claims.
GitHub Contents SHA compare-and-swap serializes claim updates. This governs
development writes only; it grants NO SOURCE, numerical, Merge or Deploy authority.

Usage (existing GitHub token, no new credential):
  python tools/local_change_claim.py reserve --owner manual --id UUID --workstream BASE9 --paths runtime/local_fullnumerical_production.py --branch manual/work
  python tools/local_change_claim.py acquire --owner manual --id UUID --workstream BASE9 --paths runtime/local_fullnumerical_production.py --branch manual/work
  python tools/local_change_claim.py verify --id UUID
  python tools/local_change_claim.py release --id UUID

A manual reservation can queue behind an active auto claim. The auto claimant
must verify before EACH Git write and release when a manual reservation appears.
Manual Work must acquire before writing; it cannot seize an in-flight claim.
"""
from __future__ import annotations

import argparse
import base64
import copy
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import PurePosixPath
import urllib.error
import urllib.parse
import urllib.request
import uuid

REPO = "b03la013-max/keibametrics-runtime"
BRANCH = "coord/local-edit-claims"
FILE = "coordination/local_work_claims.json"
SCHEMA = "KM-LOCAL-EDIT-CLAIMS-v1"
WORKSTREAMS = {"SOURCE", "BASE9", "CONSUMER", "KRS", "DELIVERY", "RESULT", "COMMON"}
OWNERS = {"auto", "manual"}


class ClaimError(RuntimeError):
    """Claim collision, invalid state, unavailable GitHub, or expired right."""


def _stamp(value: str) -> datetime:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError) as exc:
        raise ClaimError("CLAIM_EXPIRY_INVALID") from exc
    if dt.tzinfo is None:
        raise ClaimError("CLAIM_EXPIRY_NAIVE")
    return dt.astimezone(timezone.utc)


def _path(raw: str) -> str:
    if not isinstance(raw, str) or not raw or raw.startswith("/") or "\\" in raw:
        raise ClaimError("CLAIM_PATH_INVALID")
    directory = raw.endswith("/")
    parts = raw.rstrip("/").split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ClaimError("CLAIM_PATH_INVALID")
    normalized = str(PurePosixPath(*parts))
    if normalized == ".":
        raise ClaimError("CLAIM_PATH_INVALID")
    return normalized + ("/" if directory else "")


def _paths(values) -> list[str]:
    result = sorted({_path(v) for v in values})
    if not result:
        raise ClaimError("CLAIM_PATHS_REQUIRED")
    return result


def collision(a: dict, b: dict) -> bool:
    """Same workstream, COMMON or overlapping concrete files/directories."""
    if "COMMON" in (a["workstream"], b["workstream"]):
        return True
    if a["workstream"] == b["workstream"]:
        return True
    for x in a["paths"]:
        for y in b["paths"]:
            if x == y or (x.endswith("/") and y.startswith(x)) or (y.endswith("/") and x.startswith(y)):
                return True
    return False


def _live(entries: list[dict], now: datetime) -> list[dict]:
    return [entry for entry in entries if _stamp(entry["expires_at"]) > now]


def transition(state: dict, action: str, *, claim_id: str = "", owner: str = "",
               workstream: str = "", paths=(), branch: str = "",
               ttl_minutes: int = 45, now: datetime | None = None):
    """Pure transition. Caller must CAS the returned state before claiming success."""
    now = now or datetime.now(timezone.utc)
    if state.get("schema") != SCHEMA or state.get("family") != "LOCAL":
        raise ClaimError("CLAIM_MANIFEST_SCHEMA_OR_FAMILY_INVALID")
    next_state = copy.deepcopy(state)
    next_state["claims"] = _live(next_state.get("claims", []), now)
    next_state["reservations"] = _live(next_state.get("reservations", []), now)
    claims = next_state["claims"]
    reservations = next_state["reservations"]
    if action == "status":
        return next_state, {"status": "READ_ONLY", "claims": claims, "reservations": reservations}, False
    try:
        uuid.UUID(claim_id)
    except (ValueError, AttributeError) as exc:
        raise ClaimError("CLAIM_UUID_REQUIRED") from exc
    existing = next((c for c in claims if c["id"] == claim_id), None)
    reserved = next((c for c in reservations if c["id"] == claim_id), None)
    if action == "verify":
        if not existing:
            raise ClaimError("CLAIM_NOT_ACTIVE")
        if existing["owner"] == "auto" and any(collision(existing, r) for r in reservations):
            raise ClaimError("MANUAL_PRIORITY_RESERVATION")
        return next_state, {"status": "VERIFIED", "claim": existing}, False
    if action == "release":
        if existing is None and reserved is None:
            raise ClaimError("CLAIM_NOT_OWNED_OR_EXPIRED")
        next_state["claims"] = [c for c in claims if c["id"] != claim_id]
        next_state["reservations"] = [r for r in reservations if r["id"] != claim_id]
        return next_state, {"status": "RELEASED", "id": claim_id}, True
    if action not in {"acquire", "reserve", "renew"}:
        raise ClaimError("CLAIM_ACTION_UNSUPPORTED")
    if action == "renew":
        if existing is None:
            raise ClaimError("CLAIM_NOT_ACTIVE")
        if existing["owner"] == "auto" and any(collision(existing, r) for r in reservations):
            raise ClaimError("MANUAL_PRIORITY_RESERVATION")
        if ttl_minutes < 1 or ttl_minutes > 120:
            raise ClaimError("CLAIM_TTL_OUT_OF_RANGE")
        existing["expires_at"] = (now + timedelta(minutes=ttl_minutes)).isoformat()
        return next_state, {"status": "RENEWED", "claim": existing}, True
    if owner not in OWNERS or workstream not in WORKSTREAMS:
        raise ClaimError("CLAIM_OWNER_OR_WORKSTREAM_INVALID")
    if not branch or branch == "main" or branch == BRANCH or branch.startswith("refs/"):
        raise ClaimError("CLAIM_ISOLATED_BRANCH_REQUIRED")
    normalized = _paths(paths)
    if ttl_minutes < 1 or ttl_minutes > 120:
        raise ClaimError("CLAIM_TTL_OUT_OF_RANGE")
    sought = {
        "id": claim_id, "owner": owner, "workstream": workstream,
        "branch": branch, "paths": normalized,
        "expires_at": (now + timedelta(minutes=ttl_minutes)).isoformat(),
    }
    if existing:
        if action == "acquire" and all(existing[k] == sought[k] for k in ("id", "owner", "workstream", "branch", "paths")):
            return next_state, {"status": "ALREADY_HELD", "claim": existing}, False
        raise ClaimError("CLAIM_ID_ALREADY_USED")
    if reserved and any(reserved[k] != sought[k] for k in ("owner", "workstream", "branch", "paths")):
        raise ClaimError("RESERVATION_SCOPE_MISMATCH")
    if action == "reserve":
        if owner != "manual":
            raise ClaimError("RESERVATION_MANUAL_ONLY")
        if reserved:
            return next_state, {"status": "ALREADY_RESERVED", "reservation": reserved}, False
        if any(collision(sought, r) for r in reservations):
            raise ClaimError("MANUAL_RESERVATION_CONFLICT")
        if any(c["owner"] == "manual" and collision(sought, c) for c in claims):
            raise ClaimError("MANUAL_ACTIVE_CLAIM_CONFLICT")
        reservations.append(sought)
        return next_state, {"status": "RESERVED", "reservation": sought}, True
    if owner == "auto" and any(collision(sought, r) for r in reservations):
        raise ClaimError("MANUAL_PRIORITY_RESERVATION")
    if any(collision(sought, r) for r in reservations if r["id"] != claim_id):
        raise ClaimError("OTHER_MANUAL_RESERVATION")
    if any(collision(sought, c) for c in claims):
        raise ClaimError("ACTIVE_CLAIM_CONFLICT")
    claims.append(sought)
    if reserved:
        next_state["reservations"] = [r for r in reservations if r["id"] != claim_id]
    return next_state, {"status": "ACQUIRED", "claim": sought}, True


def _api(method: str, *, payload=None):
    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    if method == "PUT" and not token:
        raise ClaimError("EXISTING_GITHUB_TOKEN_REQUIRED")
    url = ("https://api.github.com/repos/" + REPO + "/contents/" + FILE
           + ("?ref=" + urllib.parse.quote(BRANCH, safe="") if method == "GET" else ""))
    headers = {"Accept": "application/vnd.github+json",
               "User-Agent": "KeibaMetrics-LOCAL-Dev-Coordination",
               "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(
        url, headers=headers, method=method,
        data=None if payload is None else json.dumps(payload, separators=(",", ":")).encode(),
    )
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code in {409, 422} and method == "PUT":
            raise ClaimError("CLAIM_CAS_CONFLICT") from exc
        raise ClaimError(f"CLAIM_GITHUB_HTTP_{exc.code}") from exc
    except (TimeoutError, OSError) as exc:
        raise ClaimError("CLAIM_GITHUB_UNAVAILABLE") from exc


def remote_action(action: str, **options) -> dict:
    for attempt in range(4):
        item = _api("GET")
        try:
            state = json.loads(base64.b64decode(item["content"]).decode())
        except (ValueError, KeyError, TypeError) as exc:
            raise ClaimError("CLAIM_MANIFEST_READ_INVALID") from exc
        updated, outcome, changed = transition(state, action, **options)
        if not changed:
            # An unchanged read verifies only the state observed at that instant.
            return outcome
        payload = {
            "message": "coord(local): " + action + " dev claim",
            "content": base64.b64encode((json.dumps(updated, indent=2, sort_keys=True) + "\n").encode()).decode(),
            "sha": item["sha"], "branch": BRANCH,
        }
        try:
            _api("PUT", payload=payload)
            return outcome
        except ClaimError as exc:
            if str(exc) != "CLAIM_CAS_CONFLICT" or attempt == 3:
                raise
    raise ClaimError("CLAIM_CAS_RETRIES_EXHAUSTED")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", choices=("status", "reserve", "acquire", "verify", "renew", "release"))
    p.add_argument("--id", dest="claim_id", default="")
    p.add_argument("--owner", default="")
    p.add_argument("--workstream", default="")
    p.add_argument("--paths", nargs="*", default=[])
    p.add_argument("--branch", default="")
    p.add_argument("--ttl-minutes", type=int, default=45)
    args = p.parse_args()
    try:
        outcome = remote_action(args.action, claim_id=args.claim_id, owner=args.owner,
                                workstream=args.workstream, paths=args.paths,
                                branch=args.branch, ttl_minutes=args.ttl_minutes)
    except ClaimError as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(outcome, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Owner-operated primary submission for an existing LOCAL Formal intent.

This program does not generate predictions, tickets, stake choices or policy,
and does not retry a request blocked by a ChatGPT tool safety decision.
An authorized GitHub CLI session writes one immutable intent to the canonical
Single Entry path; the existing GitHub Actions workflow performs the runtime.
"""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Callable

DEFAULT_REPO = "b03la013-max/keibametrics-runtime"
INTENT_ROOT = "runtime/formal_intents"
IDENTIFIER = re.compile(r"KM-LOCAL-[A-Z0-9][A-Z0-9-]{8,145}")


class EntryError(ValueError):
    pass


def _datetime(value: str) -> datetime:
    try:
        t = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError, AttributeError) as exc:
        raise EntryError("FORMAL_DATETIME_INVALID") from exc
    if t.tzinfo is None:
        raise EntryError("FORMAL_DATETIME_TZ_REQUIRED")
    return t.astimezone(timezone.utc)


def validate(intent: dict[str, Any], *, now: datetime | None = None) -> tuple[str, str]:
    """Transport preflight; existing Family Authority Guard remains canonical."""
    if not isinstance(intent, dict) or intent.get("family_id") != "LOCAL":
        raise EntryError("LOCAL_FAMILY_REQUIRED")
    if intent.get("execution_phase") not in ("AUTO", None):
        raise EntryError("SINGLE_ENTRY_AUTO_REQUIRED")
    if intent.get("temporal_mode") != "FORMAL-PRE-RACE":
        raise EntryError("PRE_RACE_MODE_REQUIRED")
    eid = intent.get("execution_id")
    if not isinstance(eid, str) or not IDENTIFIER.fullmatch(eid):
        raise EntryError("EXECUTION_ID_INVALID")
    if intent.get("race_id") != eid:
        raise EntryError("RACE_EXECUTION_ID_MISMATCH")
    race = intent.get("race")
    if not isinstance(race, dict) or race.get("race_id") != eid:
        raise EntryError("NESTED_RACE_ID_MISMATCH")
    for key in ("venue_id", "race_date", "race_no"):
        if intent.get(key) != race.get(key):
            raise EntryError(f"RACE_IDENTITY_{key.upper()}_MISMATCH")
    if not intent.get("venue_id") or not intent.get("race_date") or not isinstance(intent.get("race_no"), int):
        raise EntryError("RACE_IDENTITY_INCOMPLETE")
    runners = intent.get("runners")
    if not isinstance(runners, list) or not runners:
        raise EntryError("RUNNER_UNIVERSE_MISSING")
    numbers = [str(r.get("runner_id") or "") for r in runners if isinstance(r, dict)]
    if len(numbers) != len(runners) or len(set(numbers)) != len(numbers) or any(not n.isdigit() for n in numbers):
        raise EntryError("RUNNER_UNIVERSE_DUPLICATE_OR_INVALID")
    for runner in runners:
        if str(runner.get("horse_no")) != str(runner.get("runner_id")):
            raise EntryError("RUNNER_NUMBER_MISMATCH")
        if not str(runner.get("name") or "").strip():
            raise EntryError("RUNNER_NAME_MISSING")
    required = intent.get("required_indices")
    if not isinstance(required, list) or len(required) != 29 or len(set(required)) != 29:
        raise EntryError("FULL_29_INDEX_MANIFEST_REQUIRED")
    if intent.get("static_prediction_frozen") is not True:
        raise EntryError("FROZEN_STATIC_REQUIRED")
    static = intent.get("static_prediction")
    if not isinstance(static, dict) or not static.get("ranking") or not isinstance(static.get("roles"), dict):
        raise EntryError("STATIC_PREDICTION_INCOMPLETE")
    if set(map(str, static.get("ranking", []))) != set(numbers):
        raise EntryError("STATIC_RANKING_UNIVERSE_MISMATCH")
    if set(map(str, static["roles"])) != set(numbers):
        raise EntryError("STATIC_ROLE_UNIVERSE_MISMATCH")
    if not isinstance(intent.get("pair_dispositions"), list) or not isinstance(intent.get("third_dispositions"), list):
        raise EntryError("PAIR_THIRD_MISSING")
    if not isinstance(intent.get("run_count"), int) or intent["run_count"] < 5000:
        raise EntryError("KRS_RUN_COUNT_BELOW_STANDARD")
    if not intent.get("current_authority_manifest") or not intent.get("venue_canon"):
        raise EntryError("AUTHORITY_DECLARATION_REQUIRED")
    cutoff = _datetime(intent.get("prediction_cutoff"))
    post = _datetime(intent.get("scheduled_post_at"))
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        raise EntryError("CURRENT_TIME_TZ_REQUIRED")
    if cutoff >= post:
        raise EntryError("CUTOFF_NOT_BEFORE_POST")
    if current.astimezone(timezone.utc) >= cutoff:
        raise EntryError("FORMAL_CUTOFF_ALREADY_PASSED")
    path = f"{INTENT_ROOT}/{eid}.json"
    digest = hashlib.sha256(json.dumps(intent, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return path, digest


def _gh(args: list[str], *, input_text: str | None = None, executor: Callable[..., Any] = subprocess.run) -> Any:
    return executor(["gh", "api", *args], input=input_text, text=True, capture_output=True, check=False)


def submit(intent: dict[str, Any], *, repo: str, ref: str = "main", dry_run: bool = False,
           now: datetime | None = None, executor: Callable[..., Any] = subprocess.run) -> dict[str, Any]:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise EntryError("REPOSITORY_INVALID")
    if ref != "main":
        raise EntryError("PRODUCTION_BRANCH_MAIN_ONLY")
    path, digest = validate(intent, now=now)
    base = {"status": "VALIDATED", "execution_id": intent["execution_id"], "repo": repo,
            "path": path, "intent_sha256": digest, "production_effect": "UNVERIFIED_UNTIL_SIGNED_FINAL"}
    if dry_run:
        return {**base, "status": "DRY_RUN_ONLY"}
    uri = f"repos/{repo}/contents/{path}"
    old = _gh([f"{uri}?ref={ref}"], executor=executor)
    if old.returncode == 0:
        try:
            found = json.loads(old.stdout)
            former = json.loads(base64.b64decode(found["content"]).decode("utf-8"))
        except (ValueError, KeyError, TypeError) as exc:
            raise EntryError("EXISTING_INTENT_UNVERIFIABLE") from exc
        old_sha = hashlib.sha256(json.dumps(former, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        if old_sha != digest:
            raise EntryError("IMMUTABLE_INTENT_CONFLICT_NEW_EXECUTION_ID_REQUIRED")
        return {**base, "status": "ALREADY_SUBMITTED_IDENTICAL", "file_url": found.get("html_url")}
    if "404" not in (old.stderr or ""):
        raise EntryError("GITHUB_READ_OR_AUTHORIZATION_FAILURE")
    body = {"message": f"formal: LOCAL owner-authorized intent {intent['execution_id']}",
            "content": base64.b64encode((json.dumps(intent, ensure_ascii=False, indent=2) + "\n").encode()).decode(),
            "branch": ref}
    result = _gh(["-X", "PUT", uri, "--input", "-"], input_text=json.dumps(body), executor=executor)
    if result.returncode != 0:
        raise EntryError("GITHUB_INTENT_COMMIT_FAILED")
    try:
        receipt = json.loads(result.stdout)
        commit_sha = receipt["commit"]["sha"]
    except (KeyError, ValueError, TypeError) as exc:
        raise EntryError("GITHUB_COMMIT_RECEIPT_INVALID") from exc
    return {**base, "status": "SUBMITTED_PUSH_TRIGGER_PENDING", "commit_sha": commit_sha,
            "file_url": receipt.get("content", {}).get("html_url")}


def main() -> int:
    parser = argparse.ArgumentParser(description="Owner-operated canonical LOCAL Formal Single Entry")
    parser.add_argument("--intent", type=Path, required=True)
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        payload = json.loads(args.intent.read_text(encoding="utf-8"))
        result = submit(payload, repo=args.repo, dry_run=args.dry_run)
    except (OSError, ValueError, EntryError) as exc:
        print(json.dumps({"status": "HOLD", "failure": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

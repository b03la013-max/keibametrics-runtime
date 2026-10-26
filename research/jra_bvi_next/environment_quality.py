"""Read-only environment evidence audit of retained JRA harvest snapshots.

This is NOT the full signed-SOURCE/Reader corpus. A harvest self-hash and a
recorded raw-page digest do not independently verify GitHub OIDC, race IDs or
outcome labels. This tool never grants training/Forward-OOS eligibility, never
reacquires a URL, and never imputes going from weather or other races.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import date, datetime
import hashlib
import json
from pathlib import Path
import re

from candidate import is_explicit_jump, VENUES, GOINGS

PROFILE = "KM-JRA-BVI-ENV-RETAINED-HARVEST-QUALITY-v0.1-20261027"
HARVEST_PROFILE = "KM-JRA-OFFICIAL-PEDIGREE-HARVEST-v1.0-20261010"
GOING_ALIASES = {"稍": "稍重", "不": "不良"}
HEX_SHA = re.compile(r"^[0-9a-f]{64}$")


def canonical_sha(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def harvest_sha(value: dict) -> str:
    """Match the existing verified-backfill producer's JSON serialization."""
    body = {k: v for k, v in value.items() if k != "sha256"}
    return hashlib.sha256(
        json.dumps(body, ensure_ascii=False, sort_keys=True).encode()
    ).hexdigest()


def load_claimed_harvest(path: Path) -> tuple[dict, str]:
    if path.is_symlink() or not path.is_file():
        raise ValueError("ENV_SOURCE_NOT_REGULAR_FILE")
    raw = path.read_bytes()
    try:
        source = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError("ENV_SOURCE_INVALID_JSON") from exc
    if not isinstance(source, dict):
        raise ValueError("ENV_SOURCE_NOT_OBJECT")
    if (source.get("profile") != HARVEST_PROFILE
            or source.get("source") != "www.jra.go.jp"
            or source.get("official") is not True):
        raise ValueError("ENV_UNRECOGNIZED_HARVEST_PROVENANCE")
    if source.get("sha256") != harvest_sha(source):
        raise ValueError("ENV_HARVEST_SELF_HASH_MISMATCH")
    horses = source.get("horses")
    if (not isinstance(horses, list) or source.get("horse_count") != len(horses)
            or not isinstance(source.get("race_date"), str)):
        raise ValueError("ENV_HARVEST_CARDINALITY_MISMATCH")
    try:
        date.fromisoformat(source["race_date"])
    except ValueError as exc:
        raise ValueError("ENV_HARVEST_RACE_DATE_INVALID") from exc
    for horse in horses:
        if not isinstance(horse, dict) or not HEX_SHA.fullmatch(str(horse.get("raw_sha256") or "")):
            raise ValueError("ENV_PROFILE_RAW_DIGEST_MISSING")
        if not isinstance(horse.get("runs"), list):
            raise ValueError("ENV_PROFILE_RUNS_INVALID")
    return source, hashlib.sha256(raw).hexdigest()


def observation(horse: dict, run: dict, capture_race_day: str) -> tuple[tuple, dict] | None:
    if not isinstance(run, dict):
        return None
    horse_parts = tuple(str(horse.get(k) or "").strip() for k in
                        ("horse_name", "sire", "dam"))
    if not all(horse_parts):
        return None
    try:
        when = date.fromisoformat(str(run["date"]))
        target = date.fromisoformat(capture_race_day)
        finish, field = int(run["finish"]), int(run["field_size"])
        distance = int(run["distance_m"])
        if (when >= target or not 2 <= field <= 30 or not 1 <= finish <= field
                or not 800 <= distance <= 4500):
            return None
    except (ValueError, TypeError, KeyError):
        return None
    venue = str(run.get("venue") or "").strip()
    race_name = str(run.get("race_name") or run.get("race_class_text") or "").strip()
    surface = str(run.get("surface") or "").strip()
    going_raw = str(run.get("going") or "").strip()
    going = GOING_ALIASES.get(going_raw, going_raw)
    # Race key is PROVISIONAL: same composite horse/date/course/race label,
    # never an official JRA horse ID or a race-bound independent result.
    horse_id = hashlib.sha256("\x1f".join(horse_parts).encode()).hexdigest()
    key = (horse_id, when.isoformat(), venue, race_name, distance)
    return key, {
        "surface": surface, "venue": venue,
        "label": (finish, field),
        "jump": is_explicit_jump({"race_name": race_name, "surface": surface}),
        "going": going if going in GOINGS else None,
        "going_missing": going_raw == "",
        "going_invalid": bool(going_raw and going not in GOINGS),
        "damsire_missing": not bool(str(horse.get("damsire") or "").strip()),
    }


def audit_snapshots(paths: list[Path]) -> dict:
    """Classify original observations, not admitted unique training records."""
    observations = defaultdict(list)
    counts = Counter()
    manifest = []
    for path in sorted(paths, key=lambda p: str(p)):
        source, raw_sha = load_claimed_harvest(path)
        manifest.append((path.name, raw_sha))
        counts["source_files"] += 1
        if not source.get("collection_started_at"):
            counts["missing_source_collection_clock"] += 1
        for horse in source["horses"]:
            counts["source_horse_observations"] += 1
            for run in horse["runs"]:
                counts["source_run_observations"] += 1
                item = observation(horse, run, source["race_date"])
                if item is None:
                    counts["invalid_or_current_run_observations"] += 1
                    continue
                key, obj = item
                observations[key].append(obj)
                counts["valid_provisional_observations"] += 1

    goings = Counter()
    for witnessed in observations.values():
        counts["deduplicated_provisional_runs"] += 1
        counts["repeated_provisional_observations"] += len(witnessed) - 1
        surfaces = {w["surface"] for w in witnessed}
        labels = {w["label"] for w in witnessed}
        if len(surfaces) != 1 or len(labels) != 1:
            counts["conflicting_surface_or_label_runs"] += 1
            continue
        if any(w["jump"] for w in witnessed):
            counts["explicit_obstacle_or_mixed_surface_runs"] += 1
            continue
        w = witnessed[0]
        if w["venue"] not in VENUES or w["surface"] not in ("芝", "ダ"):
            counts["non_jra_or_unsupported_surface_runs"] += 1
            continue
        if any(x["damsire_missing"] for x in witnessed):
            counts["flat_runs_with_missing_damsire"] += 1
        values = {x["going"] for x in witnessed if x["going"]}
        if len(values) > 1:
            counts["conflicting_direct_going_runs"] += 1
        elif any(x["going_invalid"] for x in witnessed):
            counts["invalid_direct_going_runs"] += 1
        elif values:
            counts["flat_direct_going_observed"] += 1
            goings[next(iter(values))] += 1
            if any(x["going_missing"] for x in witnessed):
                counts["observed_with_missing_duplicate"] += 1
        else:
            counts["flat_original_going_missing"] += 1

    buckets = (
        "conflicting_surface_or_label_runs", "explicit_obstacle_or_mixed_surface_runs",
        "non_jra_or_unsupported_surface_runs", "conflicting_direct_going_runs",
        "invalid_direct_going_runs", "flat_direct_going_observed",
        "flat_original_going_missing",
    )
    if sum(counts[b] for b in buckets) != counts["deduplicated_provisional_runs"]:
        raise ValueError("ENV_BUCKETS_DO_NOT_PARTITION_PROVISIONAL_RUNS")
    report = {
        "profile": PROFILE,
        "classification": "POST_CAPTURE_RETAINED_HARVEST_SUBSET_ONLY; NOT_FULL_SIGNED_SOURCE_CORPUS",
        "source_original_manifest_sha256": canonical_sha(manifest),
        "source_self_hashes_checked": counts["source_files"],
        "github_oidc_reverified_by_this_audit": False,
        "official_horse_id_confirmed": 0,
        "independent_race_bound_labels_confirmed": 0,
        "strict_training_eligible": 0,
        "forward_oos_increment": 0,
        "production_effect": "NONE",
        "weather_imputation": False,
        "counts": dict(sorted(counts.items())),
        "observed_direct_goings": dict(sorted(goings.items())),
    }
    report["sha256"] = canonical_sha(report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, help="Optional unpromoted report; prefer CI temp directory")
    args = parser.parse_args()
    files = sorted((args.repository / "runtime/pedigree_corpus").glob("*.json"))
    if not files:
        raise SystemExit("ENV_NO_RETAINED_HARVEST_SNAPSHOTS")
    report = audit_snapshots(files)
    rendered = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.output:
        if args.output.resolve().is_relative_to(args.repository.resolve()):
            raise SystemExit("ENV_REPORT_MUST_NOT_WRITE_PRODUCTION_REPOSITORY")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()

"""Research-only environment projection of the existing admitted BVI corpus.

No collector, numeric mapping, Production reader default, or signed artifact is
changed here.  A row exists only when the ordinary reader already admitted the
same exact pedigree identity and historical result.  Environment observations
are recovered from those immutable inputs, not inferred from weather or joined
to a different race with the same date/venue.  Composite identities remain
provisional; they are never advertised as independent official registry IDs.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date
import hashlib
import json
from pathlib import Path
import re

from jra_pedigree_corpus import (
    _ATTEST_CACHE, _clean_runs, _dt, _horse_identity, _sha,
    _source_horses_from_verified_artifact, _verified_harvest, _verified_source, build_corpus,
)

PROFILE = "KM-JRA-BVI-ENV-DATASET-v1-SHADOW"
JRA_VENUES = frozenset(("札幌", "函館", "福島", "新潟", "東京", "中山", "中京", "京都", "阪神", "小倉"))
ENVIRONMENT_FIELDS = ("venue", "surface", "distance_m", "going", "inner_outer",
                      "course_shape", "straight_m", "weather", "rainfall_mm",
                      "moisture_pct", "cushion_value")
_BASE_FIELDS = ("date", "venue", "surface", "distance_m", "race_name", "finish", "field_size", "body_weight")


def _run_key(run):
    return tuple(run[k] for k in ("date", "venue", "surface", "distance_m", "race_name"))


def _surface(raw):
    # The Production legacy parser collapses 芝ダ to 芝.  Keep that Production
    # behavior unchanged, but do not use a mixed surface as research evidence.
    if raw in ("芝", "TURF"):
        return "芝"
    if raw in ("ダ", "ダート", "DIRT"):
        return "ダ"
    if raw in ("障", "障害"):
        return "障"
    return None


def _harvest_available_at(path, captured, cutoff):
    """Use witnessed timestamp when exposed by the mandatory OIDC verifier.

    A test-injected verifier cannot create a historical availability timestamp.
    If the verifier only exposes a boolean, the already-checked cutoff is a
    conservative upper bound, never the old actual race date.
    """
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    times = []
    for signer in ("km-jra-pedigree-verified-backfill.yml", "km-jra-pedigree-corpus-harvest.yml"):
        valid, witnessed = _ATTEST_CACHE.get((digest, signer), (False, []))
        if valid:
            times.extend(t for t in witnessed if captured <= t <= cutoff)
    return min(times) if times else cutoff


def _bound_profile_raw_hashes(path, frozen, *, include_conflicts=False):
    """Recover only a horse profile's exact, already-signed snapshot binding."""
    artifact = json.loads(path.read_text(encoding="utf-8"))["artifact"]
    history = (artifact.get("jra_official_horse_history") or {}).get("runners") or {}
    snapshots = {s.get("snapshot_sha256"): s for s in artifact.get("sources") or [] if isinstance(s, dict)}
    out = {}
    conflicts = {}
    for card in (artifact.get("jra_official_race_card_detail") or {}).get("runners") or []:
        rid = str(card.get("runner_id") or card.get("horse_no") or "")
        past = history.get(rid) or {}
        snap = snapshots.get(past.get("source_snapshot_sha256")) or {}
        raw_hash = past.get("raw_sha256")
        fetched = _dt(snap.get("fetched_at"))
        matched = _source_horses_from_verified_artifact({
            "jra_official_race_card_detail": {"runners": [card]},
            "jra_official_horse_history": {"runners": {rid: past}},
        })
        if not matched:
            continue
        identity = _horse_identity(matched[0])
        if fetched is not None and fetched > frozen:
            conflicts[identity] = "PROFILE_RAW_FETCH_AFTER_SIGNED_FREEZE"
            continue
        if raw_hash and snap and raw_hash != snap.get("raw_sha256"):
            conflicts[identity] = "PROFILE_RAW_HASH_BINDING_CONFLICT"
            continue
        if (re.fullmatch(r"[0-9a-f]{64}", str(raw_hash or ""))
                and raw_hash == snap.get("raw_sha256") and fetched is not None
                and snap.get("official") is True
                and snap.get("source_id") == "JRA-OFFICIAL-HORSE-HISTORY"):
            out[identity] = raw_hash
    return (out, conflicts) if include_conflicts else out


def _coverage(rows):
    n = len(rows)
    return {
        field: {
            "observed": sum(r.get(field) is not None and r.get(field) != "" for r in rows),
            "missing": sum(r.get(field) is None or r.get(field) == "" for r in rows),
            "conflict": sum("CONFLICT_QUARANTINED" in r["environment_status"].get(field, "") for r in rows),
            "denominator": n,
            "coverage_rate": (sum(r.get(field) is not None and r.get(field) != "" for r in rows) / n if n else None),
        } for field in ENVIRONMENT_FIELDS
    }


def _parent_distributions(rows):
    out = {}
    for parent_type in ("sire", "damsire"):
        groups = defaultdict(list)
        for row in rows:
            if row.get(parent_type):
                groups[row[parent_type]].append(row)
        out[parent_type] = [{
            "parent": parent, "runs": len(group),
            "composite_offspring": len({r["horse_id"] for r in group}),
            "independent_official_offspring": None,
            "going_counts": dict(sorted(Counter(r["going"] or "MISSING" for r in group).items())),
            "venue_counts": dict(sorted(Counter(r["venue"] or "MISSING" for r in group).items())),
            "surface_counts": dict(sorted(Counter(r["surface"] or "MISSING" for r in group).items())),
            "distance_counts": dict(sorted(Counter(str(r["distance_m"]) if r["distance_m"] else "MISSING" for r in group).items())),
        } for parent, group in sorted(groups.items())]
    return out


def build_environment_dataset(root, *, prediction_cutoff, race_date,
                              exclude_race_id=None, attestation_verifier=None,
                              source_attestation_verifier=None):
    """Project recovered facts through the SAME reader acceptance gates.

    ``race_date`` is the target event-day exclusion boundary, while
    ``prediction_cutoff`` is the actual acquisition/verification boundary.
    Earlier historical result labels are NOT proof of pre-race availability.
    Explicit injected verifiers are intended for synthetic unit tests only,
    exactly as in the existing reader; real acceptance supplies no substitute.
    """
    root = Path(root)
    corpus = build_corpus(root, prediction_cutoff=prediction_cutoff, race_date=race_date,
                          exclude_race_id=exclude_race_id,
                          attestation_verifier=attestation_verifier,
                          source_attestation_verifier=source_attestation_verifier)
    cutoff = _dt(prediction_cutoff)
    try:
        day = date.fromisoformat(race_date)
    except (TypeError, ValueError):
        day = None
    if cutoff is None or day is None:
        raise ValueError("BVI_ENV_INVALID_TARGET_TIME")
    snapshots = set(corpus["snapshots"])
    targets = {(hid, key): run for hid, horse in corpus["horses"].items()
               for key, run in horse["runs"].items()}
    observations = defaultdict(list)
    sources = {}
    file_digests = {}
    source_counts = Counter()

    def observe(horse, *, source_key, source_path, captured_at, available_at, trust,
                environment_rejection_reason=None):
        identity = _horse_identity(horse)
        if identity not in corpus["horses"]:
            return
        if source_path not in file_digests:
            file_digests[source_path] = hashlib.sha256(source_path.read_bytes()).hexdigest()
        digest = file_digests[source_path]
        reference = _sha([source_key, str(source_path.relative_to(root)), horse.get("raw_sha256")])
        sources[reference] = {
            "source_key": source_key, "file": str(source_path.relative_to(root)),
            "file_sha256": digest, "raw_source_sha256": horse.get("raw_sha256"),
            "captured_at": captured_at.isoformat(),
            "available_at_upper_bound": available_at.isoformat(), "trust": trust,
            "raw_hash_status": ("OBSERVED_OFFICIAL_PROFILE_RAW_SHA256" if horse.get("raw_sha256")
                                else "BOUND_BY_SIGNED_SOURCE_SNAPSHOT_NOT_SEPARATELY_MAPPED"),
            "environment_rejection_reason": environment_rejection_reason,
        }
        for run in _clean_runs(horse.get("runs") or [], day, include_environment=True):
            base = {k: run[k] for k in _BASE_FIELDS}
            key = (identity, _run_key(base))
            if targets.get(key) != base:
                continue
            observations[key].append({
                "reference": reference,
                "available_at": available_at.isoformat(),
                "going": None if environment_rejection_reason else run["going"],
                "going_raw": run["going_raw"],
                "surface": None if environment_rejection_reason else _surface(run["surface_raw"]),
                "environment_eligible": environment_rejection_reason is None,
            })

    # Reuse the exact signed SOURCE extractor and immutable-byte verification.
    # Only snapshot IDs admitted by the ordinary Reader can be projected.
    for path in sorted(root.glob("runtime/executions/*/SOURCE/runs/*/source_receipt_envelope.json")):
        source = _verified_source(path)
        if not source or source.get("source_snapshot_sha256") not in snapshots:
            continue
        captured = _dt(source.get("source_freeze_at"))
        if captured is None or captured > cutoff or source.get("race_id") == exclude_race_id:
            continue
        # build_corpus already performed the optional independent SOURCE
        # attestation check. Do not reinterpret legacy ingress as fresh OIDC.
        trust = ("ED25519_AND_INDEPENDENT_OIDC_AT_CUTOFF" if source_attestation_verifier is not None
                 else "ED25519 / LEGACY_OIDC_AT_INGRESS_NOT_REVERIFIED_HERE")
        available = cutoff if source_attestation_verifier is not None else captured
        raw_hashes, profile_conflicts = _bound_profile_raw_hashes(path, captured, include_conflicts=True)
        for horse in source["horses"]:
            horse = {**horse, "raw_sha256": raw_hashes.get(_horse_identity(horse))}
            observe(horse, source_key=source["source_snapshot_sha256"], source_path=path,
                    captured_at=captured, available_at=available, trust=trust,
                    environment_rejection_reason=profile_conflicts.get(_horse_identity(horse)))
        source_counts["signed_sources"] += 1

    for path in sorted(root.glob("runtime/pedigree_corpus/*.json")):
        harvest = _verified_harvest(path, not_after=cutoff, attestation_verifier=attestation_verifier)
        if not harvest or "ATTESTED_HARVEST:" + harvest["sha256"] not in snapshots:
            continue
        captured = _dt(harvest.get("harvested_at"))
        if captured is None or captured > cutoff:
            continue
        available = _harvest_available_at(path, captured, cutoff)
        for horse in harvest["horses"]:
            observe(horse, source_key="ATTESTED_HARVEST:" + harvest["sha256"], source_path=path,
                    captured_at=captured, available_at=available,
                    trust=("UNIT_TEST_INJECTED_VERIFIER / NOT_REAL_OIDC" if attestation_verifier is not None
                           else "GITHUB_OIDC_VERIFIED_AT_CUTOFF / ORIGINAL_HASH_PRESERVED"))
        source_counts["oidc_harvests"] += 1

    rows = []
    for (identity, key), run in sorted(targets.items(), key=lambda item: (item[0][0], str(item[0][1]))):
        horse = corpus["horses"][identity]
        seen = observations[(identity, key)]
        if not seen:
            # An unexplained missing join cannot produce a model observation.
            raise ValueError("BVI_ENV_ADMITTED_RUN_PROJECTION_MISSING")
        values = {}
        statuses = {}
        field_refs = {}
        qualified = [o for o in seen if o["environment_eligible"]]
        first_base = min((_dt(o["available_at"]) for o in qualified), default=cutoff)
        available = first_base
        for field in ("surface", "going"):
            known = {o[field] for o in seen if o[field] is not None}
            if len(known) == 1:
                values[field] = next(iter(known))
                support = [o for o in seen if o[field] == values[field]]
                first = min(support, key=lambda o: o["available_at"])
                available = max(available, _dt(first["available_at"]))
                statuses[field] = "OBSERVED_IN_ACCEPTED_ORIGINAL"
                field_refs[field] = first["reference"]
            else:
                values[field] = None
                statuses[field] = ("CONFLICT_QUARANTINED" if known
                                   else "SOURCE_TIME_OR_BINDING_CONFLICT_QUARANTINED" if not qualified
                                   else "MISSING")
        for field in ENVIRONMENT_FIELDS:
            if field not in ("venue", "surface", "distance_m", "going"):
                values[field] = None
                statuses[field] = "NO_EXACT_OFFICIAL_RACE_BINDING / NOT_INFERRED"
        for field in ("venue", "distance_m"):
            values[field] = run.get(field) if qualified else None
            statuses[field] = ("OBSERVED_IN_ACCEPTED_ORIGINAL" if qualified and run.get(field)
                               else "SOURCE_TIME_OR_BINDING_CONFLICT_QUARANTINED" if not qualified
                               else "MISSING")
        refs = sorted({o["reference"] for o in seen})
        rows.append({
            **run, **values, "horse_id": identity, "horse_name": horse["horse_name"],
            "baseline_venue": run["venue"], "baseline_surface": run["surface"],
            "sire": horse["sire"], "dam": horse["dam"], "damsire": horse["damsire"],
            "horse_identity_status": "NAME_SIRE_DAM_COMPOSITE_NOT_OFFICIAL_HORSE_ID",
            "row_id": _sha([identity, key]), "race_key": list(key),
            "race_identity_status": "COMPOSITE_PROVISIONAL_NOT_OFFICIAL_RACE_ID",
            "official_race_id": None, "official_horse_id": None,
            "official_race_navigation_reference": None,
            "available_at": available.isoformat(),
            "availability_status": "CONSERVATIVE_VERIFIED_INPUT_UPPER_BOUND_NOT_RACE_DATE",
            "environment_status": statuses, "field_provenance": field_refs,
            "provenance": refs, "going_raw_values": sorted({o["going_raw"] for o in seen if o["going_raw"]}),
            "observation_count": len(seen),
            "research_label_eligible": bool(qualified),
            "model_training_eligibility": False,
        })
    assert len(rows) == corpus["run_count"]
    central = [r for r in rows if r["baseline_venue"] in JRA_VENUES]
    result = {
        "profile": PROFILE, "prediction_cutoff": prediction_cutoff, "race_date": race_date,
        "classification": "POST_CAPTURE_RESEARCH_DATASET / NON_PRODUCTION / NOT_FORWARD_OOS",
        "rows": rows, "sources": dict(sorted(sources.items())),
        "source_counts": dict(source_counts),
        "verification_mode": ("UNIT_TEST_INJECTED_HARVEST_VERIFIER" if attestation_verifier is not None
                              else "REAL_DEFAULT_HARVEST_VERIFIERS"),
        "baseline_corpus": {k: v for k, v in corpus.items() if k != "horses"},
        "manifest_sha256": corpus["manifest_sha256"],
        "coverage": _coverage(rows), "jra_10_venue_coverage": _coverage(central),
        "jra_10_venue_runs": len(central),
        "going_recovered_runs": sum(r["going"] is not None for r in rows),
        "environment_quarantined_rows": sum(not r["research_label_eligible"] for r in rows),
        "parent_distributions": _parent_distributions(rows),
        "duplicate_observations_excluded": sum(max(r["observation_count"] - 1, 0) for r in rows),
        "official_permanent_horse_ids": 0, "official_race_ids": 0,
        "model_training_eligibility": False,
        "model_training_blockers": ["OFFICIAL_PERMANENT_HORSE_IDS_UNRESOLVED", "INDEPENDENT_OFFICIAL_RACE_IDS_UNRESOLVED"],
        "environment_join_policy": "DIRECT_ORIGINAL_ROW_ONLY; NO_WEATHER_TO_GOING_INFERENCE; NO_DAY_VENUE_ONLY_ENVIRONMENT_JOIN",
        "production_effect": "NONE", "historical_frozen_prediction_rewritten": False,
        "forward_oos_increment": 0,
    }
    result["dataset_sha256"] = _sha(result)
    return result

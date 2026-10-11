"""Bounded JRA official horse-profile backfill for scarce sire BVI cohorts.

Owner-curated *public JRA horse tokens* are only discovery hints. Every horse is
independently fetched from www.jra.go.jp, parsed for its actual sire/dam/damsire,
rejected if outside the requested parent groups, and committed only after the
existing OIDC/Sigstore corpus signer verifies the generated immutable bytes.

NEVER backdate a harvest for a historical or already-frozen prediction.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import quote

from jra_pedigree_harvest import _Client, PROFILE, _decode, _sha, parse_horse_pedigree
from jra_horse_history import parse_horse_history

TOKEN_PATTERN = re.compile(r"^pw01dud[0-9A-Za-z/]{10,45}$")
COHORT_PATTERN = re.compile(r"^[a-z0-9-]{8,64}$")
MAX_PROFILES = 20


def acquire(manifest: dict, *, client=None, now=None) -> dict:
    if manifest.get("source") != "JRA_OFFICIAL" or not COHORT_PATTERN.fullmatch(
            str(manifest.get("cohort_id") or "")):
        raise ValueError("JRA_TARGETED_COHORT_MANIFEST_INVALID")
    parents = manifest.get("target_sires", [])
    maternal_parents = manifest.get("target_damsires", [])
    tokens = manifest.get("official_horse_profile_tokens")
    def valid_scope(xs):
        return (isinstance(xs, list) and len(xs) <= 10
                and all(isinstance(p, str) and p.strip() and len(p) <= 90 for p in xs)
                and len(set(xs)) == len(xs))
    if not valid_scope(parents) or not valid_scope(maternal_parents) or not (parents or maternal_parents):
        raise ValueError("JRA_TARGETED_PARENT_SCOPE_INVALID")
    if not isinstance(tokens, list) or not 1 <= len(tokens) <= MAX_PROFILES or any(
            not isinstance(t, str) or not TOKEN_PATTERN.fullmatch(t) for t in tokens
    ) or len(set(tokens)) != len(tokens):
        raise ValueError("JRA_TARGETED_PUBLIC_TOKEN_SCOPE_INVALID")
    if client is None:
        client = _Client(delay=1.3)
    cohort_date = str(manifest.get("cohort_date") or "")
    if not re.fullmatch(r"20\d{2}-\d{2}-\d{2}", cohort_date):
        raise ValueError("JRA_TARGETED_COHORT_DATE_INVALID")
    # Acquisition date is recorded at collection time, not claimed as observed
    # before the target race's already frozen prediction cutoff.
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None or current.astimezone(timezone.utc).date().isoformat() < cohort_date:
        raise ValueError("JRA_TARGETED_FUTURE_COHORT_FORBIDDEN")
    parent_set = set(parents)
    damsire_set = set(maternal_parents)
    horses, errors = [], []
    for tok in tokens:
        try:
            raw, content_type = client.raw_get(
                "/JRADB/accessU.html?CNAME=" + quote(tok, safe=""))
            page = _decode(raw, content_type)
            ped = parse_horse_pedigree(page)
            if not ped.get("horse_name") or not ped.get("sire") or not ped.get("dam"):
                raise ValueError("JRA_TARGETED_PARENT_IDENTITY_MISSING")
            # An independently verified official sire OR damsire cohort may
            # satisfy the EXISTING Production BVI maternal/distance/class
            # fallback rules. No change to those rules or sample thresholds.
            if not (ped["sire"] in parent_set or ped.get("damsire") in damsire_set):
                raise ValueError("JRA_TARGETED_PARENT_NOT_MATCHED")
            parsed = parse_horse_history(raw, content_type)
            horses.append({**ped, "runs": parsed.get("runs") or [],
                           "raw_sha256": _sha(raw),
                           "profile_token_sha256": hashlib.sha256(tok.encode()).hexdigest()})
        except Exception as exc:
            errors.append(type(exc).__name__ + ":" + str(exc).split(":")[0])
    out = {
        "profile": PROFILE, "official": True, "source": "www.jra.go.jp",
        "race_date": cohort_date, "mode": "targeted_official_horse_profiles",
        "cohort_id": manifest["cohort_id"], "target_sires": sorted(parent_set),
        "target_damsires": sorted(damsire_set),
        # A cohort's usable time is after the LAST horse fetch, never the
        # initial queue dispatch time. This prevents late page data being
        # treated as available before an earlier race cutoff.
        "harvested_at": max(current, datetime.now(timezone.utc)).astimezone(timezone.utc).isoformat(),
        "horse_token_count": len(tokens), "selected_token_count": len(tokens),
        "horse_count": len(horses), "horses": horses,
        "errors": errors,
        "coverage_class": "FULL" if not errors else "PARTIAL_WITH_EXPLICIT_MISSINGNESS",
        "discovery_complete": False,
    }
    out["sha256"] = hashlib.sha256(json.dumps(
        out, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    result = acquire(manifest)
    if (result["horse_count"] < 3
            or result["horse_count"] / result["horse_token_count"] < 0.90):
        raise SystemExit("JRA_TARGETED_COHORT_INCOMPLETE_NO_PUBLICATION")
    if args.output.exists():
        raise SystemExit("JRA_TARGETED_COHORT_IMMUTABLE_ALREADY_EXISTS")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"cohort_id": result["cohort_id"],
                      "observed_horses": result["horse_count"],
                      "observed_prior_runs": sum(len(x["runs"]) for x in result["horses"]),
                      "mode": result["mode"],
                      "production_evidence_available_only_after_attestation": True,
                      "historical_oos_increment": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

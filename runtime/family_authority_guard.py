from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

ROOT = Path(__file__).resolve().parents[1]
SUPPORTED_FAMILIES = {"JRA", "LOCAL", "BAN"}
OWNER_CLASSES = {"COMMON_FAMILY", "FAMILY_SPECIFIC", "VENUE_SPECIFIC", "CANDIDATE_SHADOW"}

FAMILY_MARKERS = {
    "JRA": ("KM-JRA", "JRA-", "JRA_", "/JRA/", " JRA "),
    "LOCAL": ("KM-LOCAL", "LOCAL-", "LOCAL_", "/LOCAL/", " LOCAL "),
    "BAN": ("KM-BAN", "BAN-", "BAN_", "/BAN/", " BAN ", "PARAMETER_MAP-BAN"),
}

SENSITIVE_KEY_TOKENS = (
    "parameter_map",
    "source_adapter",
    "source_runtime",
    "information_source_registry",
    "evidence_rule_registry",
    "evidence_compiler",
    "numerical_mapping",
    "production_mapping",
    "mapping_authority",
    "numerical_materializer",
    "krs_input_adapter",
    "krs_input_builder",
)

PRODUCTION_AUTHORITY_KEY_TOKENS = (
    "parameter_map",
    "source_adapter",
    "evidence_rule_registry",
    "numerical_mapping",
    "production_mapping",
    "mapping_authority",
    "numerical_materializer",
    "krs_input_adapter",
    "krs_input_builder",
)

NONPRODUCTION_MARKERS = ("CANDIDATE", "SHADOW", "NON-PRODUCTION", "NON_PRODUCTION")


class FamilyAuthorityError(ValueError):
    pass


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def resolve_current_authority(root: Path = ROOT, now: datetime | None = None) -> Tuple[Path, Dict[str, Any]]:
    now = now or datetime.now(timezone.utc)
    candidates = []
    for path in sorted((root / "profiles").glob("KM_FAMILY_CURRENT_AUTHORITY_*.json")):
        try:
            obj = _load_json(path)
            if "CURRENT-AUTHORITY" not in str(obj.get("status") or ""):
                continue
            effective = _parse_dt(obj["effective_at"]).astimezone(timezone.utc)
            if effective <= now.astimezone(timezone.utc):
                candidates.append((effective, str(obj.get("manifest_id") or ""), path, obj))
        except Exception:
            continue
    if not candidates:
        raise FamilyAuthorityError("CURRENT_AUTHORITY_RESOLUTION_EMPTY")
    _, _, path, obj = max(candidates, key=lambda x: (x[0], x[1]))
    return path, obj


def load_authority(path: str | Path | None = None) -> Tuple[Path, Dict[str, Any]]:
    if path:
        p = Path(path)
        if not p.is_absolute():
            p = ROOT / p
        return p, _load_json(p)
    return resolve_current_authority()


def _contract_path(authority: Dict[str, Any], key: str) -> Path:
    common = authority.get("common_family_components") or {}
    value = str(common.get(key) or "").strip()
    if not value:
        raise FamilyAuthorityError(f"CURRENT_AUTHORITY_CONTRACT_PATH_MISSING:{key}")
    path = ROOT / value
    if not path.exists():
        raise FamilyAuthorityError(f"CURRENT_AUTHORITY_CONTRACT_FILE_MISSING:{key}:{value}")
    return path


def load_scope_contract(authority: Dict[str, Any]) -> Dict[str, Any]:
    return _load_json(_contract_path(authority, "scope_ownership_profile"))


def load_lifecycle_contract(authority: Dict[str, Any]) -> Dict[str, Any]:
    return _load_json(_contract_path(authority, "formal_lifecycle_profile"))


def validate_scope_contract(scope: Dict[str, Any]) -> Dict[str, Any]:
    scopes = scope.get("scopes")
    if not isinstance(scopes, dict) or not scopes:
        raise FamilyAuthorityError("SCOPE_OWNERSHIP_SCOPES_MISSING")
    for name, spec in scopes.items():
        if not isinstance(spec, dict):
            raise FamilyAuthorityError(f"SCOPE_SPEC_INVALID:{name}")
        owner = str(spec.get("owner") or "")
        if owner not in OWNER_CLASSES:
            raise FamilyAuthorityError(f"SCOPE_OWNER_INVALID:{name}:{owner}")

    for name in scope.get("common_reserved_scopes") or []:
        owner = str((scopes.get(name) or {}).get("owner") or "")
        if owner != "COMMON_FAMILY":
            raise FamilyAuthorityError(f"COMMON_RESERVED_SCOPE_OWNER_MISMATCH:{name}:{owner}")

    for name in scope.get("family_isolated_scopes") or []:
        owner = str((scopes.get(name) or {}).get("owner") or "")
        if owner != "FAMILY_SPECIFIC":
            raise FamilyAuthorityError(f"FAMILY_ISOLATED_SCOPE_OWNER_MISMATCH:{name}:{owner}")

    for name in scope.get("venue_allowed_scopes") or []:
        owner = str((scopes.get(name) or {}).get("owner") or "")
        if owner != "VENUE_SPECIFIC":
            raise FamilyAuthorityError(f"VENUE_SCOPE_OWNER_MISMATCH:{name}:{owner}")

    return {
        "scope_count": len(scopes),
        "common_reserved_count": len(scope.get("common_reserved_scopes") or []),
        "family_isolated_count": len(scope.get("family_isolated_scopes") or []),
        "venue_scope_count": len(scope.get("venue_allowed_scopes") or []),
    }


def validate_lifecycle_contract(lifecycle: Dict[str, Any]) -> Dict[str, Any]:
    stages = lifecycle.get("stages")
    if not isinstance(stages, list) or not stages:
        raise FamilyAuthorityError("FORMAL_LIFECYCLE_STAGES_MISSING")
    ids = []
    for row in stages:
        sid = str((row or {}).get("stage_id") or "")
        owner = str((row or {}).get("owner_class") or "")
        if not sid:
            raise FamilyAuthorityError("FORMAL_LIFECYCLE_STAGE_ID_MISSING")
        if owner not in OWNER_CLASSES:
            raise FamilyAuthorityError(f"FORMAL_LIFECYCLE_OWNER_INVALID:{sid}:{owner}")
        ids.append(sid)
    if len(ids) != len(set(ids)):
        raise FamilyAuthorityError("FORMAL_LIFECYCLE_DUPLICATE_STAGE")
    required = {
        "CANON_RESOLVE", "SCOPE_OWNERSHIP_RESOLVE", "SIGNED_SOURCE_RECEIPT",
        "FULL_RUNNER_UNIVERSE", "REQUIRED_INDEX_MANIFEST",
        "ACTUAL_NUMERICAL_MATERIALIZATION", "INDEX_PROVENANCE",
        "STATIC_PREDICTION_FREEZE", "PRE_KRS", "KRS_EXECUTE",
        "PRECOMPRESSION_SEMANTIC_UNIVERSE", "MEC", "CAPITAL_POLICY",
        "CANONICAL_TICKET", "SIGNED_FINAL", "SIGNED_RESULT",
        "SETTLEMENT", "PREDICTION_UTILITY_MEASUREMENT", "PFS_MEASUREMENT",
        "FIRST_MATERIAL_FAILURE_LOCALIZATION", "LEARNING_STATE_N_PLUS_1"
    }
    missing = sorted(required - set(ids))
    if missing:
        raise FamilyAuthorityError(f"FORMAL_LIFECYCLE_REQUIRED_STAGE_MISSING:{missing}")
    return {"stage_count": len(ids), "required_stage_count": len(required)}


def infer_family(req: Dict[str, Any], request_path: str | None = None) -> str:
    explicit = str(req.get("family_id") or "").upper().strip()
    if explicit:
        if explicit not in SUPPORTED_FAMILIES:
            raise FamilyAuthorityError(f"UNSUPPORTED_FAMILY:{explicit}")
        return explicit
    normalized = str(request_path or "").replace("\\", "/")
    if "/runtime/requests/" in "/" + normalized or normalized.startswith("runtime/requests/"):
        return "JRA"
    raise FamilyAuthorityError("FAMILY_ID_MISSING")


def _walk(obj: Any, path: Tuple[str, ...] = ()) -> Iterable[Tuple[Tuple[str, ...], str, Any]]:
    if isinstance(obj, dict):
        for key, value in obj.items():
            k = str(key)
            yield path + (k,), k, value
            yield from _walk(value, path + (k,))
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            yield from _walk(value, path + (str(i),))


def _marker_families(value: Any) -> set[str]:
    if not isinstance(value, str):
        return set()
    upper = " " + value.upper().replace("\\", "/") + " "
    found = set()
    for family, markers in FAMILY_MARKERS.items():
        if any(marker in upper for marker in markers):
            found.add(family)
    return found


def _is_sensitive_key(key: str) -> bool:
    low = key.lower()
    return any(token in low for token in SENSITIVE_KEY_TOKENS)


def _is_production_authority_key(key: str) -> bool:
    low = key.lower()
    return any(token in low for token in PRODUCTION_AUTHORITY_KEY_TOKENS)


def validate_explicit_scope_bindings(req: Dict[str, Any], scope: Dict[str, Any]) -> int:
    bindings = req.get("authority_scope_bindings")
    if bindings is None:
        return 0
    if not isinstance(bindings, dict):
        raise FamilyAuthorityError("AUTHORITY_SCOPE_BINDINGS_INVALID")
    specs = scope["scopes"]
    for scope_name, declared_owner in bindings.items():
        if scope_name not in specs:
            raise FamilyAuthorityError(f"AUTHORITY_SCOPE_UNKNOWN:{scope_name}")
        expected = str(specs[scope_name]["owner"])
        actual = str(declared_owner)
        if actual != expected:
            raise FamilyAuthorityError(f"AUTHORITY_SCOPE_OWNER_MISMATCH:{scope_name}:{actual}!={expected}")
    return len(bindings)


def validate_cross_family_isolation(req: Dict[str, Any], family: str, production_formal: bool) -> Dict[str, Any]:
    checked = 0
    for path, key, value in _walk(req):
        if not _is_sensitive_key(key):
            continue
        checked += 1
        values = value if isinstance(value, list) else [value]
        for v in values:
            if not isinstance(v, (str, int, float, bool)) and v is not None:
                continue
            text = str(v)
            other = _marker_families(text) - {family}
            if other:
                raise FamilyAuthorityError(
                    "CROSS_FAMILY_AUTHORITY_REUSE:"
                    + family + ":" + ".".join(path) + ":" + ",".join(sorted(other)) + ":" + text
                )
            if production_formal and _is_production_authority_key(key):
                up = text.upper()
                if any(marker in up for marker in NONPRODUCTION_MARKERS):
                    raise FamilyAuthorityError(
                        "NON_PRODUCTION_AUTHORITY_IN_PRODUCTION_SCOPE:"
                        + ".".join(path) + ":" + text
                    )
    return {"sensitive_authority_fields_checked": checked}


def validate_runtime_readiness(authority: Dict[str, Any], family: str, production_formal: bool) -> None:
    if not production_formal:
        return
    fam = ((authority.get("family_scoped_authority") or {}).get(family) or {})
    status = " ".join(str(fam.get(k) or "") for k in ("status", "execution_status", "runtime_status"))
    if "BLOCKED-PHYSICAL-RUNTIME-UNVERIFIED" in status.upper():
        raise FamilyAuthorityError(f"FAMILY_RUNTIME_BLOCKED:{family}:PHYSICAL_RUNTIME_UNVERIFIED")


def validate_request_context(
    req: Dict[str, Any],
    *,
    request_path: str | None = None,
    authority_path: str | Path | None = None,
) -> Dict[str, Any]:
    authority_file, authority = load_authority(authority_path)
    scope = load_scope_contract(authority)
    lifecycle = load_lifecycle_contract(authority)

    scope_check = validate_scope_contract(scope)
    lifecycle_check = validate_lifecycle_contract(lifecycle)

    family = infer_family(req, request_path)
    temporal_mode = str(req.get("temporal_mode") or "FORMAL-PRE-RACE")
    acceptance_only = bool(req.get("acceptance_only"))
    production_formal = temporal_mode == "FORMAL-PRE-RACE" and not acceptance_only

    declared = str(req.get("current_authority_manifest") or "").strip()
    if production_formal and declared and declared != str(authority.get("manifest_id")):
        raise FamilyAuthorityError(
            f"STALE_CURRENT_AUTHORITY:{declared}!={authority.get('manifest_id')}"
        )

    resolved = str(req.get("resolved_current_authority_manifest") or "").strip()
    if resolved and resolved != str(authority.get("manifest_id")):
        raise FamilyAuthorityError(
            f"RESOLVED_CURRENT_AUTHORITY_MISMATCH:{resolved}!={authority.get('manifest_id')}"
        )

    binding_count = validate_explicit_scope_bindings(req, scope)
    isolation = validate_cross_family_isolation(req, family, production_formal)
    validate_runtime_readiness(authority, family, production_formal)

    return {
        "status": "PASS",
        "family_id": family,
        "temporal_mode": temporal_mode,
        "production_formal": production_formal,
        "current_authority_manifest": authority.get("manifest_id"),
        "current_authority_path": str(authority_file.relative_to(ROOT)),
        "scope_ownership_contract": scope.get("profile_id"),
        "formal_lifecycle_contract": lifecycle.get("profile_id"),
        "explicit_scope_binding_count": binding_count,
        **scope_check,
        **lifecycle_check,
        **isolation,
    }


def _expect_fail(fn, code: str) -> None:
    try:
        fn()
    except FamilyAuthorityError as exc:
        if code not in str(exc):
            raise AssertionError(f"EXPECTED_{code}_GOT:{exc}") from exc
        return
    raise AssertionError(f"EXPECTED_FAILURE_NOT_RAISED:{code}")


def selftest(authority_path: str | Path | None = None) -> Dict[str, Any]:
    authority_file, authority = load_authority(authority_path)
    manifest = str(authority.get("manifest_id"))
    base = {
        "temporal_mode": "FORMAL-PRE-RACE",
        "current_authority_manifest": manifest,
    }

    jra = validate_request_context({**base, "family_id": "JRA"}, authority_path=authority_file)
    local = validate_request_context({**base, "family_id": "LOCAL"}, authority_path=authority_file)

    _expect_fail(
        lambda: validate_request_context(
            {**base, "family_id": "JRA", "parameter_map_authority": "parameter_map-BAN Rev.13"},
            authority_path=authority_file,
        ),
        "CROSS_FAMILY_AUTHORITY_REUSE",
    )
    _expect_fail(
        lambda: validate_request_context(
            {**base, "family_id": "LOCAL", "production_mapping": "KM-JRA-MAPPING-CANDIDATE"},
            authority_path=authority_file,
        ),
        "CROSS_FAMILY_AUTHORITY_REUSE",
    )
    _expect_fail(
        lambda: validate_request_context(
            {**base, "family_id": "JRA", "authority_scope_bindings": {"MEC": "VENUE_SPECIFIC"}},
            authority_path=authority_file,
        ),
        "AUTHORITY_SCOPE_OWNER_MISMATCH",
    )

    ban_state = "NOT_TESTED"
    try:
        validate_request_context({**base, "family_id": "BAN"}, authority_path=authority_file)
        ban_state = "PASS"
    except FamilyAuthorityError as exc:
        if "FAMILY_RUNTIME_BLOCKED" in str(exc):
            ban_state = "EXPECTED_BLOCKED"
        else:
            raise

    return {
        "status": "PASS",
        "authority": manifest,
        "jra": jra["status"],
        "local": local["status"],
        "ban": ban_state,
        "negative_cross_family": "PASS",
        "negative_scope_override": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request")
    parser.add_argument("--authority-path")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()

    try:
        if args.selftest:
            print(json.dumps(selftest(args.authority_path), ensure_ascii=False, sort_keys=True))
            return 0
        if not args.request:
            parser.error("--request or --selftest is required")
        path = Path(args.request)
        req = _load_json(path)
        report = validate_request_context(
            req,
            request_path=str(path),
            authority_path=args.authority_path,
        )
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
        return 0
    except FamilyAuthorityError as exc:
        print("FAMILY_AUTHORITY_GUARD_FAIL:" + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

"""Point-in-time JRA pedigree corpus built only from stored, signed JRA SOURCEs.

Every stored JRA SOURCE envelope carries the official race card (sire / dam /
damsire for each runner) and the runner's official race history. Pooling them
gives sire- and damsire-level performance facts without any third-party source.

Temporal purity: only envelopes whose ``source_freeze_at`` is strictly before
the target prediction cutoff are read, only runs dated strictly before the
target race day are counted, and the target race's own SOURCE is excluded.
The corpus is a growing sample of horses this runtime has observed; it is not a
complete national population and every feature records its sample size.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

PROFILE = "KM-JRA-POINT-IN-TIME-PEDIGREE-CORPUS-v1.1-20261010-TRUSTED-IDENTITY"
HARVEST_PROFILE = "KM-JRA-OFFICIAL-PEDIGREE-HARVEST-v1.0-20261010"
REPO = "b03la013-max/keibametrics-runtime"
_CACHE: dict[str, dict] = {}
_ATTEST_CACHE: dict[tuple, tuple[bool, list[datetime]]] = {}


def _sha(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def _dt(v: Any):
    try:
        d = datetime.fromisoformat(str(v).replace("Z", "+00:00"))
        return d.astimezone(timezone.utc) if d.tzinfo else None
    except (TypeError, ValueError):
        return None


def _norm_surface(v: Any) -> str:
    s = str(v or "")
    return "ダ" if s.startswith("ダ") else "芝" if s.startswith("芝") else "障" if s.startswith("障") else s


def _horse_identity(h: dict) -> str | None:
    """Same Japanese name is not a globally unique horse identifier.

    Require independent sire AND dam on all records and use the immutable
    pedigree triple (a profile-id alias can be introduced after verification).
    """
    name = str(h.get("horse_name") or "").strip()
    sire = str(h.get("sire") or "").strip()
    dam = str(h.get("dam") or "").strip()
    if not (name and sire and dam):
        return None
    return hashlib.sha256(("\x1f".join([name, sire, dam])).encode("utf-8")).hexdigest()


def _attested(path: Path, *, signer: str | None = None,
              not_after: datetime | None = None) -> bool:
    """Verify artifact bytes against GitHub OIDC / Sigstore, not an in-file flag."""
    if not (os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")):
        return False
    # Always key attestation cache by the actual artifact bytes. A same-size
    # modification that restores mtime must never reuse signed provenance.
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    cache_key = (digest, signer)
    if cache_key in _ATTEST_CACHE:
        verified, witnessed = _ATTEST_CACHE[cache_key]
        return bool(verified and (not_after is None or any(t <= not_after for t in witnessed)))
    cmd = ["gh", "attestation", "verify", str(path), "--repo", REPO,
           "--format", "json"]
    if signer:
        cmd += ["--signer-workflow", REPO + "/.github/workflows/" + signer]
    try:
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           text=True, timeout=20, check=False)
        if r.returncode != 0:
            _ATTEST_CACHE[cache_key] = (False, [])
            return False
        data = json.loads(r.stdout)
        witnessed = []
        for item in data:
            result = item.get("verificationResult") or {}
            for stamp in result.get("verifiedTimestamps") or []:
                t = _dt(stamp.get("timestamp") or stamp.get("time"))
                if t is not None:
                    witnessed.append(t)
        _ATTEST_CACHE[cache_key] = (True, witnessed)
        return bool(not_after is None or any(t <= not_after for t in witnessed))
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired, ValueError, TypeError):
        return False


def _clean_runs(runs: list[dict], race_day: date) -> list[dict]:
    out = []
    for r in runs:
        if not isinstance(r, dict):
            continue
        try:
            d = date.fromisoformat(str(r["date"]))
            finish, field = int(r["finish"]), int(r["field_size"])
            if d >= race_day or not (2 <= field <= 30 and 1 <= finish <= field):
                continue
            length = r.get("distance_m")
            if length is not None and not (800 <= int(length) <= 4500):
                continue
        except (KeyError, TypeError, ValueError):
            continue
        # Preserve an actually observed JRA race-day body weight. Dropping it
        # made the existing physical_pedigree_fit rule unconditionally MISSING,
        # even when the signed JRA history supplied genuine weight evidence.
        weight = r.get("body_weight")
        try:
            weight = int(weight) if weight is not None else None
        except (TypeError, ValueError):
            weight = None
        if weight is not None and not 250 <= weight <= 850:
            weight = None
        out.append({
            "date": d.isoformat(), "venue": str(r.get("venue") or ""),
            "surface": _norm_surface(r.get("surface")),
            "distance_m": int(r["distance_m"]) if r.get("distance_m") is not None else None,
            "race_name": str(r.get("race_name") or r.get("race_class_text") or ""),
            "finish": finish, "field_size": field,
            "body_weight": weight,
        })
    return out


def _source_horses_from_verified_artifact(art: dict) -> list[dict]:
    """Derive pedigree-identified horses from one already verified JRA SOURCE.

    The race card and per-runner official history may each contain pedigree
    fields. Accept complementary values only for the same horse number. A
    contradictory parent (or horse name) excludes the horse, not just the
    conflicting field: pooling a false sire/dam creates contaminated offspring
    statistics and misleading Production BVI coverage.
    """
    detail = (art.get("jra_official_race_card_detail") or {}).get("runners") or []
    history = (art.get("jra_official_horse_history") or {}).get("runners") or {}
    out = []
    for x in detail:
        if not isinstance(x, dict):
            continue
        rid = str(x.get("runner_id") or x.get("horse_no") or "")
        if not rid:
            continue
        past = history.get(rid) or {}
        hped = past.get("pedigree") or {}
        name = str(x.get("horse_name") or "").strip()
        official_history_name = str(past.get("horse_name") or "").strip()
        if official_history_name and official_history_name != name:
            continue
        parents = {}
        conflict = False
        for key in ("sire", "dam", "damsire"):
            card = str(x.get(key) or "").strip()
            profile = str(hped.get(key) or "").strip()
            if card and profile and card != profile:
                conflict = True
                break
            parents[key] = card or profile
        if conflict:
            continue
        h = {"horse_name": name, **parents}
        if not _horse_identity(h):
            continue
        h["runs"] = past.get("runs") or x.get("recent_runs") or []
        out.append(h)
    return out


def _verified_source(path: Path) -> dict | None:
    """Ed25519 signed SOURCE + nested snapshot binding. NOT independent OIDC.

    The external Formal runner already checks GitHub OIDC; this local reader
    checks the original receipt bytes. An untrusted unsigned JSON fixture
    cannot participate in Production BVI.
    """
    key = f"{path}:{hashlib.sha256(path.read_bytes()).hexdigest()}"
    if key in _CACHE:
        return _CACHE[key]
    try:
        from jra_source_runtime.verify_source_envelope import verify, sha_obj
        checked = verify(str(path))
        envelope = json.loads(path.read_text(encoding="utf-8"))
        art = envelope["artifact"]
        if checked.get("valid") is not True or checked.get("github_repository") != REPO:
            return None
        if art.get("family_id") != "JRA":
            return None
        snap = str(art.get("source_snapshot_sha256") or "")
        if not re.fullmatch(r"[0-9a-f]{64}", snap):
            return None
        if snap != sha_obj({k:v for k,v in art.items() if k != "source_snapshot_sha256"}):
            return None
        if art.get("race_id") != checked.get("race_id"):
            return None
        summary = {
            "race_id": art.get("race_id"),
            "source_freeze_at": art.get("source_freeze_at"),
            "source_snapshot_sha256": snap,
            "horses": [],
            "signed_source_crypto_verified": True,
        }
        # This helper may consult the *same verified signed SOURCE* horse
        # history for parents missing on the race card; no external or
        # unattested parent identity is introduced.
        summary["horses"] = _source_horses_from_verified_artifact(art)
        _CACHE[key] = summary
        return summary
    except (OSError, ValueError, TypeError, KeyError, ImportError):
        return None


def _verified_harvest(path: Path, *, not_after: datetime,
                      attestation_verifier=None) -> dict | None:
    """A self-declared 'official' flag or sha256 is NEVER trust authority.

    Confirm content integrity, actual JRA site, identity/raw checks, and
    GitHub Actions OIDC attestation issued by the harvest workflow. Historical
    harvests cannot be backdated: the observable attestation is tied to the
    captured bytes. Offline mode fails closed unless the caller injects a
    verifier (reserved for isolated unit tests).
    """
    try:
        data = path.read_bytes()
        obj = json.loads(data)
        digest = obj.get("sha256")
        if (obj.get("profile") != HARVEST_PROFILE or obj.get("official") is not True
                or obj.get("source") != "www.jra.go.jp"
                or not re.fullmatch(r"[0-9a-f]{64}", str(digest or ""))):
            return None
        unsigned = {k:v for k,v in obj.items() if k != "sha256"}
        # Preserve the v1 producer canonical hash serialization exactly.
        actual = hashlib.sha256(json.dumps(unsigned, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        if digest != actual:
            return None
        trusted = (attestation_verifier or
                   (lambda p: (
                       _attested(p, signer="km-jra-pedigree-verified-backfill.yml",
                                 not_after=not_after)
                       or _attested(p, signer="km-jra-pedigree-corpus-harvest.yml",
                                    not_after=not_after)
                   )))(path)
        if not trusted:
            return None
        if (obj.get("horse_count") != len(obj.get("horses") or [])
                or obj.get("horse_token_count", -1) < obj["horse_count"]):
            return None
        if any(not (_horse_identity(h) and re.fullmatch(r"[0-9a-f]{64}", str(h.get("raw_sha256") or "")))
               for h in obj["horses"]):
            return None
        return obj
    except (OSError, ValueError, TypeError, KeyError):
        return None


def _signed_source_might_match_target(path: Path, *,
                                      required_sires: set[str] | None,
                                      required_damsires: set[str] | None) -> bool:
    """Negative-only relevance filter for archived signed JRA SOURCE envelopes.

    A matching or incomplete/malformed file ALWAYS enters the existing
    cryptographic _verified_source gate; prefilter JSON is never admitted as
    evidence. Non-matching fully-identified official runner cards need not
    incur expensive Ed25519/SHA verification on every future race.
    """
    if required_sires is None and required_damsires is None:
        return True
    try:
        root = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(root, dict):
            return True
        art = root.get("artifact")
        if not isinstance(art, dict):
            return True
        detail = (art.get("jra_official_race_card_detail") or {}).get("runners")
        history = (art.get("jra_official_horse_history") or {}).get("runners") or {}
        if not isinstance(detail, list) or not detail or not isinstance(history, dict):
            return True
        sires = required_sires or set()
        damsires = required_damsires or set()
        for x in detail:
            if not isinstance(x, dict):
                return True
            rid = str(x.get("runner_id") or x.get("horse_no") or "")
            if not rid:
                return True
            past = history.get(rid) or {}
            if not isinstance(past, dict):
                return True
            ped = past.get("pedigree") or {}
            if not isinstance(ped, dict):
                return True
            sire = str(x.get("sire") or ped.get("sire") or "").strip()
            damsire = str(x.get("damsire") or ped.get("damsire") or "").strip()
            # An absent parent may have further evidence in verified upstream
            # ingestion; do not silently discard uncertain source files.
            if (not sire or not damsire or sire in sires or damsire in damsires):
                return True
        return False
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        return True


def _harvest_might_match_target(path: Path, *, required_sires: set[str] | None,
                                required_damsires: set[str] | None) -> bool:
    """Cheap *negative-only* relevance hint before costly GitHub OIDC verification.

    Never use this JSON to create pedigree evidence: any potentially relevant
    file still passes _verified_harvest's content hash, workflow identity and
    timestamp attestation. Malformed input is sent to the verifier for
    fail-closed rejection, not silently treated as a valid sample.
    """
    if required_sires is None and required_damsires is None:
        return True
    try:
        blob = json.loads(path.read_text(encoding="utf-8"))
        horses = blob.get("horses")
        if not isinstance(horses, list):
            return True
        sires = required_sires or set()
        damsires = required_damsires or set()
        for h in horses:
            if not isinstance(h, dict):
                return True
            if (str(h.get("sire") or "").strip() in sires
                    or str(h.get("damsire") or "").strip() in damsires):
                return True
        return False
    except (OSError, ValueError, TypeError):
        return True


def build_corpus(root: str | Path, *, prediction_cutoff: str, race_date: str,
                 exclude_race_id: str | None = None,
                 attestation_verifier=None,
                 source_attestation_verifier=None,
                 required_sires: set[str] | None = None,
                 required_damsires: set[str] | None = None) -> dict:
    cutoff = _dt(prediction_cutoff)
    try:
        day = date.fromisoformat(str(race_date))
    except ValueError:
        day = None
    empty = {"profile": PROFILE, "horses": {}, "snapshots": [],
             "snapshot_count": 0, "horse_count": 0, "run_count": 0,
             "manifest_sha256": _sha([]), "identity_collision_count": 0,
             "run_conflict_count": 0, "rejected_untrusted_inputs": 0}
    if cutoff is None or day is None:
        return empty
    horses: dict[str, dict] = {}
    snaps = set()
    rejected = 0
    conflicts = set()
    names: dict[str, set[str]] = {}
    maternal_conflicts = set()

    def add(h: dict, source_key: str):
        identity = _horse_identity(h)
        if not identity:
            return
        name = str(h["horse_name"]).strip()
        names.setdefault(name, set()).add(identity)
        row = horses.setdefault(identity, {
            "horse_id": identity, "horse_name": name,
            "sire": h["sire"], "dam": h["dam"],
            "damsire": h.get("damsire") or "", "runs": {},
        })
        row.setdefault("identity_kind", "NAME_SIRE_DAM_COMPOSITE_NOT_OFFICIAL_HORSE_ID")
        row.setdefault("source_references", [])
        if source_key not in row["source_references"]:
            row["source_references"].append(source_key)
        incoming = str(h.get("damsire") or "").strip()
        if identity not in maternal_conflicts:
            if incoming and row["damsire"] and incoming != row["damsire"]:
                maternal_conflicts.add(identity)
                row["damsire"] = ""
                row["maternal_identity_status"] = "CONFLICT_QUARANTINED"
            elif incoming:
                row["damsire"] = incoming
                row["maternal_identity_status"] = "OBSERVED"
        for run in _clean_runs(h.get("runs") or [], day):
            # A date + course alone is not a unique race identity. Do not
            # silently overwrite contradictory same-key historical results.
            key = (run["date"], run["venue"], run["surface"],
                   run["distance_m"], run["race_name"])
            if (identity, key) in conflicts:
                continue
            prev = row["runs"].get(key)
            if prev is not None and prev != run:
                conflicts.add((identity, key))
                row["runs"].pop(key, None)
            else:
                row["runs"][key] = run

    for path in sorted(Path(root).glob("runtime/executions/*/SOURCE/runs/*/source_receipt_envelope.json")):
        # Signed SOURCE envelopes can be multi-megabyte. Filter only files
        # proven irrelevant by the untrusted negative hint; every potentially
        # useful source still passes full Ed25519 and snapshot hash verification.
        if not _signed_source_might_match_target(
                path, required_sires=required_sires,
                required_damsires=required_damsires):
            continue
        summary = _verified_source(path)
        if not summary:
            rejected += 1
            continue
        if summary.get("race_id") == exclude_race_id:
            continue
        if required_sires is not None or required_damsires is not None:
            if not any(h.get("sire") in (required_sires or set())
                       or h.get("damsire") in (required_damsires or set())
                       for h in summary["horses"]):
                continue
        frozen = _dt(summary.get("source_freeze_at"))
        if frozen is None or frozen > cutoff:
            continue
        # Legacy signed SOURCE already passed GitHub OIDC at its original
        # acquisition handoff. Here cryptographic content/hash are reverified.
        # Rechecking GitHub OIDC per file is optional but supported: the
        # canonical Formal SOURCE gate remains the mandatory independent
        # verifier of the CURRENT race. Do not call this legacy offline
        # receipt check independent identity verification.
        if source_attestation_verifier is not None and source_attestation_verifier(path) is not True:
            rejected += 1
            continue
        snaps.add(str(summary["source_snapshot_sha256"]))
        for h in summary["horses"]:
            add(h, str(summary["source_snapshot_sha256"]))

    harvest_paths = [p for p in sorted(Path(root).glob("runtime/pedigree_corpus/*.json"))
                     if _harvest_might_match_target(p, required_sires=required_sires,
                                                  required_damsires=required_damsires)]
    # Verification is independent per immutable artifact. Parallelize only
    # verification; merge in canonical path order so collision semantics and
    # every sample/threshold/hash remain identical to the sequential path.
    import time, sys
    from concurrent.futures import ThreadPoolExecutor
    started = time.monotonic()
    workers = 4 if (attestation_verifier is None and len(harvest_paths) > 1
                    and (os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN'))) else 1
    print(f'PEDIGREE_VERIFY_START artifacts={len(harvest_paths)} workers={workers}', file=sys.stderr, flush=True)
    def verify_harvest(path):
        return _verified_harvest(path, not_after=cutoff, attestation_verifier=attestation_verifier)
    pool = ThreadPoolExecutor(max_workers=workers)
    try:
        verified_harvests = list(pool.map(verify_harvest, harvest_paths))
    finally:
        pool.shutdown(wait=True)
    print(f'PEDIGREE_VERIFY_DONE artifacts={len(harvest_paths)} seconds={time.monotonic()-started:.3f}',
          file=sys.stderr, flush=True)
    for path, hv in zip(harvest_paths, verified_harvests):
        # Most archive batches have no offspring of the specific target sire
        # or damsire. Do not perform a networked GitHub OIDC verification for
        # those files; a negative hint never contributes to the corpus.
        # Potentially relevant files must still pass full _verified_harvest.
        if not _harvest_might_match_target(
                path, required_sires=required_sires,
                required_damsires=required_damsires):
            continue
        if not hv:
            rejected += 1
            continue
        captured = _dt(hv.get("harvested_at"))
        if captured is None or captured > cutoff:
            continue
        snaps.add("ATTESTED_HARVEST:" + hv["sha256"])
        for h in hv.get("horses") or []:
            if required_sires is not None or required_damsires is not None:
                if h.get("sire") not in (required_sires or set()) and h.get("damsire") not in (required_damsires or set()):
                    continue
            add(h, "ATTESTED_HARVEST:" + hv["sha256"])
    manifest = sorted(snaps)
    return {
        "profile": PROFILE, "horses": horses,
        "snapshots": manifest, "snapshot_count": len(manifest),
        "horse_count": len(horses),
        "run_count": sum(len(h["runs"]) for h in horses.values()),
        "manifest_sha256": _sha(manifest),
        "identity_collision_count": sum(len(ids)-1 for ids in names.values() if len(ids)>1),
        "run_conflict_count": len(conflicts),
        "maternal_identity_conflict_count": len(maternal_conflicts),
        "rejected_untrusted_inputs": rejected,
        "production_harvest_rule": "OIDC_ATTESTED_JRA_HARVEST_OR_SIGNED_SOURCE_ONLY",
        "source_signature_level": "ENVELOPE_ED25519_VERIFIED / LEGACY_SOURCE_OIDC_AT_INGRESS_NOT_REVERIFIED_HERE",
        "valid_for_historical_OOS_recompute": False,
    }

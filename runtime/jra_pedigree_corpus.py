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
    cmd = ["gh", "attestation", "verify", str(path), "--repo", REPO,
           "--format", "json"]
    if signer:
        cmd += ["--signer-workflow", REPO + "/.github/workflows/" + signer]
    try:
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           text=True, timeout=60, check=False)
        if r.returncode != 0:
            return False
        if not_after is None:
            return True
        data = json.loads(r.stdout)
        # A stored harvest timestamp is never an authority. Use signed
        # Sigstore transparency / TSA witness time to reject retrospective use.
        for item in data:
            result = item.get("verificationResult") or {}
            for stamp in result.get("verifiedTimestamps") or []:
                t = _dt(stamp.get("timestamp") or stamp.get("time"))
                if t is not None and t <= not_after:
                    return True
        return False
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
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
        out.append({
            "date": d.isoformat(), "venue": str(r.get("venue") or ""),
            "surface": _norm_surface(r.get("surface")),
            "distance_m": int(r["distance_m"]) if r.get("distance_m") is not None else None,
            "race_name": str(r.get("race_name") or r.get("race_class_text") or ""),
            "finish": finish, "field_size": field,
        })
    return out


def _verified_source(path: Path) -> dict | None:
    """Ed25519 signed SOURCE + nested snapshot binding. NOT independent OIDC.

    The external Formal runner already checks GitHub OIDC; this local reader
    checks the original receipt bytes. An untrusted unsigned JSON fixture
    cannot participate in Production BVI.
    """
    key = f"{path}:{path.stat().st_mtime_ns}"
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
        detail = (art.get("jra_official_race_card_detail") or {}).get("runners") or []
        history = (art.get("jra_official_horse_history") or {}).get("runners") or {}
        for x in detail:
            if not isinstance(x, dict):
                continue
            rid = str(x.get("runner_id") or x.get("horse_no") or "")
            h = {
                "horse_name": str(x.get("horse_name") or "").strip(),
                "sire": str(x.get("sire") or "").strip(),
                "dam": str(x.get("dam") or "").strip(),
                "damsire": str(x.get("damsire") or "").strip(),
            }
            if not _horse_identity(h):
                continue
            h["runs"] = (history.get(rid) or {}).get("runs") or x.get("recent_runs") or []
            summary["horses"].append(h)
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
                   (lambda p: _attested(p, signer="km-jra-pedigree-corpus-harvest.yml",
                                        not_after=not_after)))(path)
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


def build_corpus(root: str | Path, *, prediction_cutoff: str, race_date: str,
                 exclude_race_id: str | None = None,
                 attestation_verifier=None,
                 source_attestation_verifier=None) -> dict:
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
        summary = _verified_source(path)
        if not summary:
            rejected += 1
            continue
        if summary.get("race_id") == exclude_race_id:
            continue
        frozen = _dt(summary.get("source_freeze_at"))
        if frozen is None or frozen > cutoff:
            continue
        # Receipt public keys are embedded in envelopes; independent OIDC
        # signer verification and timestamp are required for BVI Production.
        verified = (source_attestation_verifier or
                    (lambda p: _attested(p, not_after=cutoff)))(path)
        if verified is not True:
            rejected += 1
            continue
        snaps.add(str(summary["source_snapshot_sha256"]))
        for h in summary["horses"]:
            add(h, "SIGNED_SOURCE")

    for path in sorted(Path(root).glob("runtime/pedigree_corpus/*.json")):
        hv = _verified_harvest(path, not_after=cutoff,
                               attestation_verifier=attestation_verifier)
        if not hv:
            rejected += 1
            continue
        captured = _dt(hv.get("harvested_at"))
        if captured is None or captured > cutoff:
            continue
        snaps.add("ATTESTED_HARVEST:" + hv["sha256"])
        for h in hv.get("horses") or []:
            add(h, "ATTESTED_HARVEST")
    manifest = sorted(snaps)
    return {
        "profile": PROFILE, "horses": horses,
        "snapshots": manifest, "snapshot_count": len(manifest),
        "horse_count": len(horses),
        "run_count": sum(len(h["runs"]) for h in horses.values()),
        "manifest_sha256": _sha(manifest),
        "identity_collision_count": sum(len(ids)-1 for ids in names.values() if len(ids)>1),
        "run_conflict_count": len(conflicts),
        "rejected_untrusted_inputs": rejected,
        "production_harvest_rule": "OIDC_ATTESTED_JRA_HARVEST_OR_SIGNED_SOURCE_ONLY",
        "source_signature_level": "ENVELOPE_ED25519_PLUS_GITHUB_OIDC_ATTESTATION_BEFORE_CUTOFF",
        "valid_for_historical_OOS_recompute": False,
    }

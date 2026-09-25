from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import shutil
from typing import Any, Dict, Optional

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_ROOT = REPO_ROOT / "runtime" / "executions"


class ExecutionStoreError(ValueError):
    pass


def _safe(value: str) -> str:
    x = re.sub(r"[^A-Za-z0-9._-]+", "-", str(value or "").strip())
    x = re.sub(r"-+", "-", x).strip("-")
    if not x:
        raise ExecutionStoreError("EXECUTION_STORE_ID_EMPTY")
    return x[:180]


def _sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def phase_root(execution_id: str, phase: str, root: pathlib.Path | None = None) -> pathlib.Path:
    base = root or DEFAULT_ROOT
    return base / _safe(execution_id) / _safe(str(phase).upper())


def persist_phase(
    execution_id: str,
    phase: str,
    run_id: str,
    source_dir: str | pathlib.Path,
    *,
    root: pathlib.Path | None = None,
    github_sha: str | None = None,
) -> Dict[str, Any]:
    src = pathlib.Path(source_dir)
    if not src.exists() or not src.is_dir():
        raise ExecutionStoreError(f"EXECUTION_STORE_SOURCE_DIR_MISSING:{src}")
    files = sorted(p for p in src.iterdir() if p.is_file() and p.suffix == ".json")
    if not files:
        raise ExecutionStoreError("EXECUTION_STORE_NO_JSON_FILES")

    proot = phase_root(execution_id, phase, root)
    run_key = _safe(str(run_id))
    dest = proot / "runs" / run_key
    dest.mkdir(parents=True, exist_ok=True)

    inventory = {}
    for p in files:
        target = dest / p.name
        shutil.copy2(p, target)
        inventory[p.name] = {"sha256": _sha256(target), "bytes": target.stat().st_size}

    manifest = {
        "schema": "KM-EXECUTION-STORE-v1",
        "execution_id": _safe(execution_id),
        "phase": _safe(str(phase).upper()),
        "run_id": run_key,
        "github_sha": github_sha,
        "stored_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "files": inventory,
    }
    manifest_path = dest / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2),
        encoding="utf-8",
    )
    manifest["manifest_sha256"] = _sha256(manifest_path)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2),
        encoding="utf-8",
    )

    latest = {
        "schema": "KM-EXECUTION-STORE-POINTER-v1",
        "execution_id": manifest["execution_id"],
        "phase": manifest["phase"],
        "run_id": run_key,
        "run_path": str(dest.relative_to(root or DEFAULT_ROOT)),
        "manifest_sha256": _sha256(manifest_path),
        "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    proot.mkdir(parents=True, exist_ok=True)
    (proot / "LATEST.json").write_text(
        json.dumps(latest, ensure_ascii=False, sort_keys=True, indent=2),
        encoding="utf-8",
    )
    return {"manifest": manifest, "latest": latest, "path": str(dest)}


def resolve_phase(
    execution_id: str,
    phase: str,
    *,
    root: pathlib.Path | None = None,
) -> Optional[Dict[str, Any]]:
    base = root or DEFAULT_ROOT
    proot = phase_root(execution_id, phase, base)
    latest_path = proot / "LATEST.json"
    if not latest_path.exists():
        return None
    latest = json.loads(latest_path.read_text(encoding="utf-8"))
    run_path = latest.get("run_path")
    if not run_path:
        raise ExecutionStoreError("EXECUTION_STORE_LATEST_RUN_PATH_MISSING")
    run_dir = base / str(run_path)
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        raise ExecutionStoreError("EXECUTION_STORE_MANIFEST_MISSING")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = str(latest.get("manifest_sha256") or "")
    actual = _sha256(manifest_path)
    if expected and expected != actual:
        raise ExecutionStoreError("EXECUTION_STORE_MANIFEST_HASH_MISMATCH")
    for name, meta in (manifest.get("files") or {}).items():
        p = run_dir / name
        if not p.exists() or _sha256(p) != str(meta.get("sha256") or ""):
            raise ExecutionStoreError(f"EXECUTION_STORE_FILE_HASH_MISMATCH:{name}")
    return {"latest": latest, "manifest": manifest, "run_dir": run_dir}


def materialize_phase(
    execution_id: str,
    phase: str,
    destination: str | pathlib.Path,
    *,
    root: pathlib.Path | None = None,
) -> Optional[Dict[str, Any]]:
    resolved = resolve_phase(execution_id, phase, root=root)
    if resolved is None:
        return None
    dest = pathlib.Path(destination)
    dest.mkdir(parents=True, exist_ok=True)
    for p in resolved["run_dir"].iterdir():
        if p.is_file() and p.name != "manifest.json":
            shutil.copy2(p, dest / p.name)
    return resolved


def _cli() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    pp = sub.add_parser("persist")
    pp.add_argument("--execution-id", required=True)
    pp.add_argument("--phase", required=True)
    pp.add_argument("--run-id", required=True)
    pp.add_argument("--source-dir", default="runtime_out")
    pp.add_argument("--github-sha")

    rp = sub.add_parser("resolve")
    rp.add_argument("--execution-id", required=True)
    rp.add_argument("--phase", required=True)
    rp.add_argument("--destination")

    args = ap.parse_args()
    if args.cmd == "persist":
        result = persist_phase(
            args.execution_id,
            args.phase,
            args.run_id,
            args.source_dir,
            github_sha=args.github_sha,
        )
    else:
        result = (
            materialize_phase(args.execution_id, args.phase, args.destination)
            if args.destination
            else resolve_phase(args.execution_id, args.phase)
        )
        if result is None:
            return 3
        if isinstance(result.get("run_dir"), pathlib.Path):
            result = {**result, "run_dir": str(result["run_dir"])}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())

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
from pathlib import Path
from typing import Any

PROFILE = "KM-JRA-POINT-IN-TIME-PEDIGREE-CORPUS-v1.0-20261010"
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


def _summarize(path: Path) -> dict | None:
    key = f"{path}:{path.stat().st_mtime_ns}"
    if key in _CACHE:
        return _CACHE[key]
    try:
        art = json.loads(path.read_text(encoding="utf-8")).get("artifact") or {}
    except (OSError, ValueError):
        return None
    if art.get("family_id") != "JRA":
        return None
    detail = (art.get("jra_official_race_card_detail") or {}).get("runners") or []
    hist = (art.get("jra_official_horse_history") or {}).get("runners") or {}
    horses = []
    for x in detail:
        name = str(x.get("horse_name") or "").strip()
        sire = str(x.get("sire") or "").strip()
        if not name or not sire:
            continue
        rid = str(x.get("runner_id") or x.get("horse_no") or "")
        runs = (hist.get(rid) or {}).get("runs") or x.get("recent_runs") or []
        clean = []
        for r in runs:
            try:
                fin, field = int(r["finish"]), int(r["field_size"])
            except (KeyError, TypeError, ValueError):
                continue
            if field < 2 or not 1 <= fin <= field or not r.get("date"):
                continue
            clean.append({"date": str(r["date"]), "venue": str(r.get("venue") or ""),
                          "surface": _norm_surface(r.get("surface")),
                          "distance_m": r.get("distance_m"),
                          "race_name": str(r.get("race_name") or r.get("race_class_text") or ""),
                          "finish": fin, "field_size": field})
        horses.append({"horse_name": name, "sire": sire,
                       "damsire": str(x.get("damsire") or "").strip(), "runs": clean})
    out = {"race_id": art.get("race_id"), "source_freeze_at": art.get("source_freeze_at"),
           "source_snapshot_sha256": art.get("source_snapshot_sha256"), "horses": horses}
    _CACHE[key] = out
    return out


def build_corpus(root: str | Path, *, prediction_cutoff: str, race_date: str,
                 exclude_race_id: str | None = None) -> dict:
    cutoff = _dt(prediction_cutoff)
    try:
        day = date.fromisoformat(str(race_date))
    except ValueError:
        day = None
    if cutoff is None or day is None:
        return {"profile": PROFILE, "horses": {}, "snapshots": [], "manifest_sha256": _sha([])}
    horses: dict[str, dict] = {}
    snaps = set()
    for path in sorted(Path(root).glob("runtime/executions/*/SOURCE/runs/*/source_receipt_envelope.json")):
        s = _summarize(path)
        if not s:
            continue
        frozen = _dt(s.get("source_freeze_at"))
        # Any SOURCE frozen no later than this cutoff is admissible: only runs
        # dated before the race day are counted, so the current race card's
        # other runners contribute strictly pre-race history.
        if frozen is None or frozen > cutoff:
            continue
        snaps.add(str(s.get("source_snapshot_sha256") or ""))
        for h in s["horses"]:
            row = horses.setdefault(h["horse_name"], {"sire": h["sire"], "damsire": h["damsire"], "runs": {}})
            for r in h["runs"]:
                if date.fromisoformat(r["date"]) < day:
                    row["runs"][(r["date"], r["venue"])] = r
    # Official JRA pedigree harvest files (jra_pedigree_harvest.py). Admissible
    # only when harvested no later than the cutoff; runs still filtered by day.
    for path in sorted(Path(root).glob("runtime/pedigree_corpus/*.json")):
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        harvested = _dt(obj.get("harvested_at"))
        if obj.get("official") is not True or harvested is None or harvested > cutoff:
            continue
        snaps.add("HARVEST:" + str(obj.get("sha256") or ""))
        for h in obj.get("horses") or []:
            name, sire = str(h.get("horse_name") or "").strip(), str(h.get("sire") or "").strip()
            if not name or not sire:
                continue
            row = horses.setdefault(name, {"sire": sire, "damsire": str(h.get("damsire") or "").strip(), "runs": {}})
            for r in h.get("runs") or []:
                try:
                    fin, field = int(r["finish"]), int(r["field_size"])
                    day_r = date.fromisoformat(str(r["date"]))
                except (KeyError, TypeError, ValueError):
                    continue
                if field < 2 or not 1 <= fin <= field or day_r >= day:
                    continue
                row["runs"][(str(r["date"]), str(r.get("venue") or ""))] = {
                    "date": str(r["date"]), "venue": str(r.get("venue") or ""),
                    "surface": _norm_surface(r.get("surface")), "distance_m": r.get("distance_m"),
                    "race_name": str(r.get("race_name") or ""), "finish": fin, "field_size": field}
    snaps.discard("")
    snaps.discard("HARVEST:")
    manifest = sorted(snaps)
    return {"profile": PROFILE, "horses": horses, "snapshots": manifest,
            "snapshot_count": len(manifest), "horse_count": len(horses),
            "run_count": sum(len(h["runs"]) for h in horses.values()),
            "manifest_sha256": _sha(manifest)}

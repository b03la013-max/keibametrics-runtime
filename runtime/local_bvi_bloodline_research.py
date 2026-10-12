"""Connect collected pedigree references without promoting them to official BVI.

BVI-R is an uncalibrated, all-NAR prize/AEI research score, not venue fit.
The official same-condition 5/3/2 race-statistic BVI remains ruled neutral.
"""
from __future__ import annotations

import hashlib
import json
import math
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "research/local_bvi/manifest.json"
VENUES = dict(URW="浦和", FNB="船橋", OHI="大井", KAW="川崎", MOR="盛岡",
              MIZ="水沢", KSM="笠松", NGY="名古屋", SON="園田", HIM="姫路",
              KCH="高知", SAG="佐賀", MON="門別", KNZ="金沢", OBI="帯広")


def _name(value):
    return "".join(unicodedata.normalize("NFKC", str(value or "")).split())


def _timestamp(value):
    try:
        result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return result.astimezone(timezone.utc) if result.tzinfo else None
    except (TypeError, ValueError):
        return None


def load_dataset(manifest_path=DEFAULT_MANIFEST):
    path = Path(manifest_path)
    manifest = json.loads(path.read_text(encoding="utf-8"))
    data = (path.parent / manifest["data_file"]).read_bytes()
    if hashlib.sha256(data).hexdigest() != manifest["sha256"]:
        raise ValueError("LOCAL_BVI_DATASET_HASH_MISMATCH")
    if not _timestamp(manifest.get("available_at")):
        raise ValueError("LOCAL_BVI_DATASET_AVAILABLE_AT_REQUIRED")
    return manifest, json.loads(data)


def _annual_score(rows):
    if not rows:
        return {"score": 52.0, "status": "UNKNOWN", "year_count": 0, "rows": []}
    # Missing top-50 years are unknown and never inserted as zero AEI.
    scores, total = [], 0
    for row in rows:
        aei = float(row["AEI"])
        n = int(row["出走頭数"])
        if not math.isfinite(aei) or aei < 0 or n <= 0:
            raise ValueError("LOCAL_BVI_INVALID_ANNUAL_STATISTIC")
        scores.append(n * (52 + 48 * (aei - 1) / (aei + 1)))
        total += n
    return {"score": round(sum(scores) / total, 6), "status": "RESEARCH_AEI",
            "year_count": len(rows), "rows": rows}


def evaluate(raw, race, as_of, dataset=None):
    manifest, data = dataset if dataset is not None else load_dataset()
    cutoff, available = _timestamp(as_of), _timestamp(manifest["available_at"])
    eligible = cutoff is not None and cutoff >= available
    venue = VENUES.get(str(race.get("venue") or race.get("venue_id") or "").upper(),
                       str(race.get("venue") or race.get("venue_id") or ""))
    result = {
        "dataset_id": manifest["dataset_id"], "dataset_sha256": manifest["sha256"],
        "available_at": manifest["available_at"], "as_of": as_of,
        "connection_status": "CONNECTED" if eligible else "TEMPORAL_BLOCKED",
        "formal_index": "BVIg-L", "formal_value": 52.0,
        "formal_status": "RULED-NEUTRAL", "formal_population_fit_available": False,
        "formal_missing": manifest["formal_missing"], "prediction_authority": False,
        "scope": "ALL_NAR_AEI_RESEARCH_ONLY", "venue": venue,
        "sire": raw.get("sire"), "damsire": raw.get("damsire"),
    }
    annual = [r for r in data["annual"] if eligible and r["終了日"] < cutoff.date().isoformat()]
    components = {}
    for field, category in (("sire", "父"), ("damsire", "母父")):
        name = _name(raw.get(field))
        matched = [r for r in annual if name and r["区分"] == category and _name(r["血統名"]) == name]
        components[field] = _annual_score(matched)
    result["research_components"] = components
    result["research_index"] = "BVI-L-R-v0.1"
    result["research_value"] = round((30 * components["sire"]["score"] +
                                      20 * components["damsire"]["score"] + 50 * 52) / 100, 6) if eligible else None
    result["research_observed_weight"] = sum(w for k, w in (("sire", 30), ("damsire", 20))
                                             if components[k]["year_count"])
    result["research_status"] = ("UNCALIBRATED_PARTIAL" if result["research_observed_weight"]
                                  else "UNKNOWN") if eligible else "TEMPORAL_BLOCKED"
    # Preserve overlapping publications as references. Never pool them, nor infer
    # current sand/distance/going suitability from a broad, mixed-era table.
    result["venue_reference_rows"] = [r for r in data["supplement"] if eligible and
                                      r["競馬場"] == venue and _name(r["血統名"]) == _name(raw.get("sire"))
                                      and r["終了日"] < cutoff.date().isoformat()]
    result["venue_reference_policy"] = "REFERENCE_ONLY_NO_POOLING_NO_ERA_OR_SURFACE_INFERENCE"
    result["source_refs"] = sorted({r["出典URL"] for c in components.values() for r in c["rows"]} |
                                    {r["出典URL"] for r in result["venue_reference_rows"]})
    return result


def attach_research(compiled, source_artifact):
    """Use the source freeze, never the wall clock, for replay availability."""
    dataset = load_dataset()
    as_of = source_artifact.get("source_freeze_at")
    race = dict(compiled.get("race") or {})
    race.setdefault("venue", compiled.get("venue_id"))
    for runner in compiled["runners"]:
        runner["bloodline_bvi_research"] = evaluate(runner.get("raw_candidate_evidence") or {}, race, as_of, dataset)
    compiled["bloodline_bvi_connection"] = {
        "dataset_id": dataset[0]["dataset_id"], "sha256": dataset[0]["sha256"],
        "available_at": dataset[0]["available_at"], "source_freeze_at": as_of,
        "connected_runners": sum(r["bloodline_bvi_research"]["connection_status"] == "CONNECTED"
                                 for r in compiled["runners"]),
        "runner_count": len(compiled["runners"]), "prediction_authority": False,
        "formal_bvi_policy": "EXISTING_CANONICAL_NEUTRAL_UNTIL_OFFICIAL_POPULATION_AVAILABLE",
    }

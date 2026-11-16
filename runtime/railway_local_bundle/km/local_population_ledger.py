from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List

from source_acquisition import sha_obj

PROFILE = "KM-LOCAL-POINT-IN-TIME-POPULATION-LEDGER-v1.0-20260924"


def _going_group(value: Any) -> str:
    s = str(value or "")
    if "不良" in s or s.strip() == "重":
        return "WET"
    if "稍" in s:
        return "INTERMEDIATE"
    if "良" in s:
        return "DRY"
    return "UNKNOWN"


def _distance_bucket(value: Any) -> str:
    try:
        d = int(value)
    except Exception:
        return "UNKNOWN"
    return str((d // 100) * 100)


def build_population_seed(artifact: Dict[str, Any]) -> Dict[str, Any]:
    aux = artifact.get("auxiliary_evidence") or {}
    profiles = aux.get("profiles") or {}
    horses = profiles.get("horses") or {}
    pedigree = aux.get("pedigree_population_seed") or {}
    seeds = {str(x.get("runner_id")): x for x in (pedigree.get("seeds") or [])}

    observations: List[Dict[str, Any]] = []
    for runner_id, horse in sorted(horses.items(), key=lambda x: int(x[0]) if str(x[0]).isdigit() else str(x[0])):
        ped = seeds.get(str(runner_id)) or {}
        for h in horse.get("history") or []:
            finish = h.get("finish")
            observations.append({
                "runner_id": str(runner_id),
                "horse_name": ped.get("horse_name"),
                "sire": ped.get("sire"),
                "dam": ped.get("dam"),
                "damsire": ped.get("damsire"),
                "race_date": h.get("date"),
                "venue": h.get("venue"),
                "distance": h.get("distance"),
                "distance_bucket": _distance_bucket(h.get("distance")),
                "going": h.get("going"),
                "going_group": _going_group(h.get("going")),
                "race_class": h.get("class"),
                "popularity": h.get("popularity"),
                "finish": finish,
                "win": bool(finish == 1),
                "top3": bool(isinstance(finish, int) and finish <= 3),
                "source_id": horse.get("source_id"),
                "source_snapshot_sha256": horse.get("source_snapshot_sha256"),
            })

    def aggregate(key_name: str) -> List[Dict[str, Any]]:
        groups: Dict[tuple, List[Dict[str, Any]]] = defaultdict(list)
        for o in observations:
            name = str(o.get(key_name) or "").strip()
            if not name:
                continue
            k = (name, o.get("venue"), o.get("distance_bucket"), o.get("going_group"))
            groups[k].append(o)
        rows: List[Dict[str, Any]] = []
        for (name, venue, distance_bucket, going_group), obs in groups.items():
            n = len(obs)
            wins = sum(1 for x in obs if x.get("win"))
            top3 = sum(1 for x in obs if x.get("top3"))
            rows.append({
                key_name: name,
                "venue": venue,
                "distance_bucket": distance_bucket,
                "going_group": going_group,
                "starts": n,
                "wins": wins,
                "top3": top3,
                "win_rate": round(wins / n, 6) if n else None,
                "top3_rate": round(top3 / n, 6) if n else None,
                "sample_status": "INSUFFICIENT" if n < 20 else "DESCRIPTIVE_ONLY",
            })
        return sorted(rows, key=lambda x: (str(x.get(key_name)), str(x.get("venue")), str(x.get("distance_bucket")), str(x.get("going_group"))))

    out = {
        "profile": PROFILE,
        "production_authority": False,
        "status": "FIELD-CONDITIONED-SEED / POINT-IN-TIME / SELECTION-BIASED / SHADOW",
        "observation_count": len(observations),
        "observations": observations,
        "sire_cohorts": aggregate("sire"),
        "damsire_cohorts": aggregate("damsire"),
        "limitations": [
            "Current-field horse histories only; this is not yet an unbiased all-horse population.",
            "No cohort may become BVI Production authority from this seed alone.",
            "All history rows are inherited from pre-target-date NAR horse profiles.",
        ],
    }
    out["sha256"] = sha_obj({k: v for k, v in out.items() if k != "sha256"})
    return out


def enrich_with_population_seed(artifact: Dict[str, Any]) -> Dict[str, Any]:
    out = build_population_seed(artifact)
    artifact["point_in_time_population_ledger"] = out
    artifact["point_in_time_population_ledger_sha256"] = sha_obj(out)
    artifact["point_in_time_population_profile"] = PROFILE
    return artifact

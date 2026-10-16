"""JRA official-fact-only closure and static-owner *candidate*.

This module executes real, reproducible calculations from pre-race observations.
Neither an existing rule name nor a runnable algorithm confers Production
prediction authority. Promotion requires the independent Family governance gate.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
from datetime import date
from typing import Any

from jra_evidence_feature_normalizer_production import percentile_band, rate_band
from jra_index_provenance_builder import BASE, DERIVED, FORMULA_REGISTRY
from jra_source_candidate_semantics import build_candidate_semantics

PROFILE = "KM-JRA-SOURCE-ONLY-EVIDENCE-STATIC-OWNER-CANDIDATE-20261010-R1"
PRODUCTION_MAPPING = "JRA-EVIDENCE-TO-BASE-MAPPING-v1.0-PRODUCTION-20260921"
RULE_IDS = {
    "recent_performance": "JRA-EVIDENCE-PERCENTILE-RECENT-PERFORMANCE-v1",
    "recent_consistency": "JRA-RECENT-CONSISTENCY-RATE-v1",
    "same_course_fit": "KM-JRA-SAME-COURSE-FIT-v1",
    "same_distance_fit": "KM-JRA-SAME-DISTANCE-FIT-v1",
    "surface_fit": "KM-JRA-SURFACE-FIT-v1",
    "going_fit": "KM-JRA-GOING-FIT-v1",
    "same_course_distance_quality": "KM-JRA-SAME-COURSE-DISTANCE-QUALITY-v1",
    "jockey_quality": "KM-JRA-JOCKEY-QUALITY-v1",
    "trainer_quality": "KM-JRA-TRAINER-QUALITY-v1",
}


class CandidateClosureError(ValueError):
    pass


def _sha(obj: Any) -> str:
    return hashlib.sha256(
        json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _official_runners(source: dict) -> list[dict]:
    official = source.get("jra_official_runner_universe") or {}
    rows = official.get("runners") or []
    ids = [str(x.get("runner_id") or x.get("horse_no") or "") for x in rows]
    if len(ids) < 2 or not all(ids) or len(set(ids)) != len(ids):
        raise CandidateClosureError("OFFICIAL_PDF_UNIVERSE_REQUIRED_UNIQUE")
    return rows


def _runner_map(rows: list[dict]) -> dict[str, dict]:
    out = {}
    for row in rows:
        rid = str(row.get("runner_id") or row.get("horse_no") or "")
        if rid and rid not in out:
            out[rid] = row
    return out


def _recent_rows(detail: dict, history: dict, race_date: str) -> list[dict]:
    # Official historical records can be partial: never infer career_starts from them.
    rows = list(history.get("runs") or detail.get("recent_runs") or [])
    selected = []
    for row in rows:
        observed_at = str(row.get("date") or "")
        if not observed_at:
            continue
        try:
            if date.fromisoformat(observed_at) >= date.fromisoformat(race_date):
                continue
        except ValueError:
            continue
        if row.get("finish") is None or row.get("field_size") is None:
            continue
        try:
            finish, field = int(row["finish"]), int(row["field_size"])
        except (ValueError, TypeError):
            continue
        if field < 2 or not 1 <= finish <= field:
            continue
        selected.append({**row, "finish": finish, "field_size": field})
    return selected


def propose_official_observed_features(source: dict) -> dict:
    """Evaluate observed history only; never invent a missing feature or rating.

    This is an explicit NON-PRODUCTION promotion candidate. Exactly the same
    facts may be useful to an authorized evaluator in a later separately
    approved Production release.
    """
    if str(source.get("family_id") or "") != "JRA":
        raise CandidateClosureError("JRA_ONLY")
    source_sha = str(source.get("source_snapshot_sha256") or "")
    race_date = str((source.get("source_race_context") or {}).get("race_date") or "")
    if not source_sha or not race_date:
        raise CandidateClosureError("SOURCE_BASIS_OR_DATE_MISSING")
    try:
        date.fromisoformat(race_date)
    except ValueError as exc:
        raise CandidateClosureError("RACE_DATE_INVALID") from exc
    official = _official_runners(source)
    detail = _runner_map((source.get("jra_official_race_card_detail") or {}).get("runners") or [])
    history = ((source.get("jra_official_horse_history") or {}).get("runners") or {})
    context = source.get("jra_race_context") or {}
    venue, target_dist, surface = (
        str(context.get("venue_name") or ""),
        context.get("distance_m"),
        str(context.get("surface") or ""),
    )
    person = ((source.get("jra_official_person_stats") or {}).get("runners") or {})
    person_source_sha = str(source.get("jra_official_person_stats_sha256") or "")
    detail_environment = ((source.get("jra_official_race_card_detail") or {}).get("race_environment") or {})
    # Calendar context does not carry track going; JRA's detailed official
    # race-card does. Only use it when its surface agrees with the target race.
    official_going = str(detail_environment.get("going") or "")
    official_going_surface = str(detail_environment.get("going_surface") or "")
    if official_going_surface and official_going_surface != surface:
        official_going = ""
    going = str(context.get("going") or context.get("track_condition") or official_going or "")
    observed = {}
    required = sorted(RULE_IDS)
    for runner in official:
        rid = str(runner.get("runner_id") or runner.get("horse_no"))
        rows = _recent_rows(detail.get(rid) or {}, history.get(rid) or {}, race_date)
        facts = {}
        def add(name: str, selected: list[dict], method: str) -> None:
            if len(selected) < 2:
                return
            if method == "finish_normalized":
                normalized = [
                    (x["field_size"] - x["finish"]) / (x["field_size"] - 1)
                    for x in selected
                ]
                raw = sum(normalized) / len(normalized)
                category = percentile_band(raw)
            else:
                raw = sum(x["finish"] <= 3 for x in selected) / len(selected)
                category = rate_band(raw)
            spec = {
                "category": category,
                "rule_id": RULE_IDS[name],
                "evidence_refs": [source_sha] + [
                    f"JRA_OFFICIAL_HISTORY:{rid}:{x['date']}:{x['finish']}:{x['field_size']}"
                    for x in selected
                ],
                "source_fact": (
                    f"{name}: observed={len(selected)}; raw_rate_or_normalized={raw:.6f}; "
                    f"source_dates={[x['date'] for x in selected]}; all before {race_date}"
                ),
                "sample_count": len(selected),
                "numeric_observation": round(raw, 6),
                "candidate_only": True,
                "production_authority": False,
            }
            facts[name] = spec
        add("recent_performance", rows[:4], "finish_normalized")
        add("recent_consistency", rows[:4], "top3_rate")
        if venue:
            add("same_course_fit", [x for x in rows if str(x.get("venue") or "") == venue], "top3_rate")
        if target_dist is not None:
            add("same_distance_fit", [x for x in rows if str(x.get("distance_m") or "") == str(target_dist)], "top3_rate")
        if surface:
            add("surface_fit", [x for x in rows if str(x.get("surface") or "") == surface], "top3_rate")
        if going and surface:
            add("going_fit", [x for x in rows
                              if str(x.get("surface") or "") == surface
                              and str(x.get("going") or "") == going], "top3_rate")
        if venue and target_dist is not None and surface:
            add("same_course_distance_quality", [x for x in rows
                 if str(x.get("venue") or "") == venue
                 and str(x.get("distance_m") or "") == str(target_dist)
                 and str(x.get("surface") or "") == surface], "top3_rate")

        # JRA person statistics are observed facts. Transformations below are
        # NON-PRODUCTION candidates and require an exact current-name/token
        # match performed by the official Source Adapter.
        by_person = person.get(rid) or {}
        for kind, feature in (("jockey", "jockey_quality"),
                              ("trainer", "trainer_quality")):
            if by_person.get(f"{kind}_matched") is not True:
                continue
            profile = by_person.get(kind) or {}
            flat = profile.get("current_year_flat") or {}
            try:
                starts = int(flat.get("starts"))
                win_rate = float(flat.get("win_rate"))
            except (ValueError, TypeError):
                continue
            # Official pages may express ratios as 0..1 or percentages as
            # 0..100. Exact value 1.0 is ambiguous and cannot be guessed.
            if starts < 30 or not math.isfinite(win_rate) or win_rate < 0:
                continue
            if win_rate == 1.0:
                continue
            rate = win_rate / 100.0 if win_rate > 1.0 else win_rate
            if not 0.0 <= rate <= 1.0:
                continue
            fact = {
                "category": rate_band(rate),
                "rule_id": RULE_IDS[feature],
                "evidence_refs": [x for x in [
                    source_sha, person_source_sha,
                    str(profile.get("sha256") or ""),
                    f"JRA_OFFICIAL_PERSON_STATS:{rid}:{kind}"
                ] if x],
                "source_fact": (
                    f"Current-year official {kind} stats: starts={starts}, "
                    f"win_rate_raw={win_rate}, normalized_ratio={rate:.6f}; "
                    f"current runner/person identity matched before cutoff."
                ),
                "sample_count": starts,
                "numeric_observation": round(rate, 6),
                "candidate_only": True,
                "production_authority": False,
            }
            facts[feature] = fact
        observed[rid] = {
            "features": facts,
            "observed_count": len(facts),
            "unresolved": [x for x in required if x not in facts],
            "pre_start_facts_only": True,
        }
    report = {
        "profile": PROFILE,
        "status": "CANDIDATE / NON-PRODUCTION / FACT-BOUND / NO-MISSING-IMPUTATION",
        "source_snapshot_sha256": source_sha,
        "race_id": source.get("race_id"),
        "runners": observed,
        "official_runner_ids": sorted(observed),
        "production_evaluator_authority": False,
        "production_feature_merge_allowed": False,
        "required_promotion": "INDEPENDENT_RULE_SEMANTICS_REVIEW_AND_FROZEN_OOS",
    }
    report["sha256"] = _sha(report)
    return report


def evaluate_static_owner_candidate(request: dict, *, source_snapshot_sha256: str) -> dict:
    """Run a real rank/role/pair/third candidate against FULL Production-index values.

    The input may be numerically Production-authored; the derived rank/role
    *policy* remains a Candidate and cannot be reported as Production STATIC.
    """
    if request.get("family_id") != "JRA" or not source_snapshot_sha256:
        raise CandidateClosureError("JRA_SOURCE_BASIS_REQUIRED")
    runners = request.get("runners") or []
    if len(runners) < 2:
        raise CandidateClosureError("AT_LEAST_TWO_OFFICIAL_RUNNERS_REQUIRED")
    ids = [str(r.get("runner_id") or "") for r in runners]
    if not all(ids) or len(set(ids)) != len(ids):
        raise CandidateClosureError("RUNNER_UNIVERSE_INVALID")
    for runner in runners:
        rid = str(runner["runner_id"])
        cells = runner.get("canonical_components") or {}
        if set(cells) != set(BASE) | set(DERIVED):
            raise CandidateClosureError(f"FULL20_REQUIRED:{rid}")
        for index, spec in cells.items():
            value = spec.get("value")
            if (not isinstance(value, (int, float)) or isinstance(value, bool)
                    or not math.isfinite(value) or not 0 <= value <= 100):
                raise CandidateClosureError(f"BAD_NUMERICAL:{rid}:{index}")
            if spec.get("candidate_only") or spec.get("production_authority") is False:
                raise CandidateClosureError(f"CANDIDATE_NUMERICAL_REJECTED:{rid}:{index}")
            expected = PRODUCTION_MAPPING if index in BASE else FORMULA_REGISTRY
            if spec.get("mapping_version") != expected:
                raise CandidateClosureError(f"NON_PRODUCTION_MAPPING:{rid}:{index}")
            if not spec.get("rule_id") or not spec.get("evidence_refs") or not spec.get("source_fact"):
                raise CandidateClosureError(f"INDEX_PROVENANCE_REQUIRED:{rid}:{index}")
    # Reuse the already-shipped structure-derived Candidate algorithm. Do NOT
    # copy its rules and silently promote them to a new Production owner.
    derived = build_candidate_semantics(copy.deepcopy(request))
    result = {
        "profile": PROFILE,
        "status": "STATIC_OWNER_EXECUTED / CANDIDATE / NON-PRODUCTION",
        "source_snapshot_sha256": source_snapshot_sha256,
        "race_id": request.get("race_id"),
        "runner_ids": ids,
        "production_index_inputs_validated": True,
        "ranking": derived["static_prediction"]["ranking"],
        "roles": derived["static_prediction"]["roles"],
        "role_registry": derived["role_registry"],
        "pair_dispositions": derived["pair_dispositions"],
        "third_dispositions": derived["third_dispositions"],
        "future_multiplicity": derived["future_multiplicity"],
        "candidate_semantic_freeze_sha256": derived["candidate_semantic_freeze"]["sha256"],
        "static_prediction_production_authority": False,
        "signed_static_freeze_verified": False,
        "production_promotion_required": True,
        "ticket_or_capital_authority": False,
    }
    result["sha256"] = _sha(result)
    return result

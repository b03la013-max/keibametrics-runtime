from __future__ import annotations

import argparse
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

PROFILE = "KM-JRA-LOCAL-MATURITY-IMPORT-20261003-R1"

NONSEMANTIC_KEYS = {
    "execution_attempt","retry_reason","retry_repair_sha","execution_mode",
    "single_entry","execution_phase","phase","jra_single_entry",
    "jra_maturity_bridge","entry_transport_fallback","transport_metadata",
    "formal_semantic_basis_sha256",
    # Annotations the canonical Formal Runner adds from the resolved Current
    # Authority BEFORE it re-verifies this binding; they are not request
    # semantics, and treating them as such failed every bridged request.
    "resolved_current_authority_manifest",
    "resolved_current_authority_profile_path",
    "resolved_jra_source_runtime_profile",
    "resolved_family_prediction_utility_contract",
}

SOURCE_REQUIRED = (
    "family_id","race_id","venue_id","race_date","race_no",
    "prediction_cutoff","scheduled_post_at",
)

class JRAMaturityBridgeError(ValueError):
    pass

def _canon(obj: Any) -> bytes:
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")

def _sha(obj: Any) -> str:
    return hashlib.sha256(_canon(obj)).hexdigest()

def _load(path: str | Path) -> Dict[str,Any]:
    obj=json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(obj,dict):
        raise JRAMaturityBridgeError("OBJECT_REQUIRED")
    return obj

def _family(req: Dict[str,Any]) -> str:
    return str(req.get("family_id") or "").upper()

def resolve_current_authority(profile_root: str | Path="profiles") -> str:
    rows=[]
    now=datetime.now(timezone.utc)
    for p in Path(profile_root).glob("KM_FAMILY_CURRENT_AUTHORITY_*.json"):
        try:
            x=_load(p)
            if "CURRENT-AUTHORITY" not in str(x.get("status") or ""):
                continue
            raw=str(x.get("effective_at") or "")
            if not raw:
                continue
            dt=datetime.fromisoformat(raw.replace("Z","+00:00")).astimezone(timezone.utc)
            if dt<=now:
                rows.append((dt,str(x.get("manifest_id") or "")))
        except Exception:
            continue
    if not rows:
        raise JRAMaturityBridgeError("JRA_SINGLE_ENTRY_CURRENT_AUTHORITY_EMPTY")
    return max(rows,key=lambda z:(z[0],z[1]))[1]

def load_current_authority(profile_root: str | Path="profiles") -> Dict[str,Any]:
    """Return the single resolved Current Authority manifest object (read-only)."""
    authority_id=resolve_current_authority(profile_root)
    for p in Path(profile_root).glob("KM_FAMILY_CURRENT_AUTHORITY_*.json"):
        try:
            row=_load(p)
        except Exception:
            continue
        if row.get("manifest_id")==authority_id:
            return row
    raise JRAMaturityBridgeError("JRA_CURRENT_AUTHORITY_FILE_UNAVAILABLE")

def _execution_id(intent: Dict[str,Any]) -> str:
    explicit=str(intent.get("execution_id") or "").strip()
    if explicit:
        return explicit
    race_id=str(intent.get("race_id") or "").strip()
    if not race_id:
        raise JRAMaturityBridgeError("JRA_SINGLE_ENTRY_RACE_ID_REQUIRED")
    return race_id+"-SINGLE-R1"

def _require_jra(intent: Dict[str,Any]) -> None:
    if _family(intent)!="JRA":
        raise JRAMaturityBridgeError("JRA_SINGLE_ENTRY_JRA_ONLY")
    missing=[k for k in SOURCE_REQUIRED if intent.get(k) in (None,"")]
    if missing:
        raise JRAMaturityBridgeError("JRA_SINGLE_ENTRY_REQUIRED_MISSING:"+",".join(missing))

def semantic_payload(req: Dict[str,Any]) -> Dict[str,Any]:
    return {
        k:copy.deepcopy(v) for k,v in req.items()
        if k not in NONSEMANTIC_KEYS
    }

def semantic_sha256(req: Dict[str,Any]) -> str:
    return _sha(semantic_payload(req))

def build_source_request(intent: Dict[str,Any]) -> Dict[str,Any]:
    _require_jra(intent)
    cfg=intent.get("jra_source") if isinstance(intent.get("jra_source"),dict) else {}
    meeting_key=str(cfg.get("jra_meeting_key") or intent.get("jra_meeting_key") or "").strip()
    if not meeting_key:
        raise JRAMaturityBridgeError("JRA_SINGLE_ENTRY_MEETING_KEY_REQUIRED")
    out={
        "family_id":"JRA",
        "race_id":intent["race_id"],
        "execution_id":_execution_id(intent),
        "venue_id":intent["venue_id"],
        "race_date":intent["race_date"],
        "race_no":intent["race_no"],
        "jra_meeting_key":meeting_key,
        "temporal_mode":str(intent.get("temporal_mode") or "FORMAL-PRE-RACE"),
        "prediction_cutoff":intent["prediction_cutoff"],
        "scheduled_post_at":intent["scheduled_post_at"],
        "external_dispatch_deadline_at":(
            intent.get("external_dispatch_deadline_at")
            or intent.get("release_deadline_at")
        ),
        # Current Source Manifest formal core is the official runner universe.
        # These enrichments are still attempted by the Source Runtime, but are
        # optional by default so an unavailable fact remains UNKNOWN and flows
        # into Source→Feature→Index Exact Gap instead of blocking Signed SOURCE.
        # Callers may explicitly set any require_* flag true for acceptance/tests.
        "require_jra_race_card_detail":bool(cfg.get("require_jra_race_card_detail",False)),
        "require_jra_horse_history":bool(cfg.get("require_jra_horse_history",False)),
        "require_jra_person_stats":bool(cfg.get("require_jra_person_stats",False)),
        "require_registered_common_workout":bool(cfg.get("require_registered_common_workout",False)),
        "require_jma_weather":bool(cfg.get("require_jma_weather",False)),
        "require_tsl_shadow":bool(cfg.get("require_tsl_shadow",False)),
        "jra_single_entry_profile":PROFILE,
    }
    if not out["external_dispatch_deadline_at"]:
        raise JRAMaturityBridgeError("JRA_SINGLE_ENTRY_DISPATCH_DEADLINE_REQUIRED")
    return out

def source_checkpoint_manifest(source_env: Dict[str,Any], source_execution_id: str) -> Dict[str,Any]:
    artifact=source_env.get("artifact") if isinstance(source_env.get("artifact"),dict) else {}
    receipt=source_env.get("receipt") if isinstance(source_env.get("receipt"),dict) else {}
    manifest={
        "source_execution_id":str(source_execution_id),
        "receipt_sha256":str(source_env.get("receipt_sha256") or ""),
        "source_snapshot_sha256":str(artifact.get("source_snapshot_sha256") or ""),
        "race_id":str(artifact.get("race_id") or ""),
        "prediction_cutoff":str(artifact.get("prediction_cutoff") or ""),
        "source_freeze_at":str(artifact.get("source_freeze_at") or ""),
        "runtime_revision":str(receipt.get("runtime_revision") or ""),
    }
    missing=[k for k,v in manifest.items() if not str(v).strip()]
    if missing:
        raise JRAMaturityBridgeError("JRA_SOURCE_CHECKPOINT_INCOMPLETE:"+",".join(missing))
    manifest["sha256"]=_sha(manifest)
    return manifest

def _production_gap_summary(gaps: list[dict]) -> dict:
    """Aggregate the exact Production closure gap without inventing readiness."""
    by_owner: dict[str,int] = {}
    by_feature: dict[str,int] = {}
    by_source_family: dict[str,int] = {}
    by_index: dict[str,int] = {}
    classes = {"SOURCE_FACT_UNAVAILABLE":0, "EVALUATOR_OR_AUTHORITY_GAP":0}
    for row in gaps:
        owner=str(row.get("correct_owner") or "UNKNOWN")
        feature=str(row.get("feature") or "UNKNOWN")
        sf=str(row.get("source_family") or "UNKNOWN")
        by_owner[owner]=by_owner.get(owner,0)+1
        by_feature[feature]=by_feature.get(feature,0)+1
        by_source_family[sf]=by_source_family.get(sf,0)+1
        for idx in row.get("index_binding") or []:
            key=str(idx)
            by_index[key]=by_index.get(key,0)+1
        if row.get("source_fact_available") is False:
            classes["SOURCE_FACT_UNAVAILABLE"]+=1
        else:
            classes["EVALUATOR_OR_AUTHORITY_GAP"]+=1

    def top(d: dict[str,int], n:int=20) -> list[dict]:
        return [
            {"key":k,"count":v}
            for k,v in sorted(d.items(), key=lambda kv:(-kv[1], kv[0]))[:n]
        ]

    return {
        "schema":"KM-JRA-PRODUCTION-CLOSURE-EXACT-GAP-SUMMARY-v1",
        "exact_gap_count":len(gaps),
        "gap_class_counts":classes,
        "owner_counts":by_owner,
        "source_family_counts":by_source_family,
        "index_binding_counts":by_index,
        "top_features":top(by_feature),
        "first_repair_priority":(
            "SOURCE_FACT_ACQUISITION" if classes["SOURCE_FACT_UNAVAILABLE"]>classes["EVALUATOR_OR_AUTHORITY_GAP"]
            else "PRODUCTION_EVALUATOR_OR_AUTHORITY_CLOSURE"
        ) if gaps else "NONE",
        "production_ready":len(gaps)==0,
        "candidate_parallel_is_not_production_repair":True,
        "no_neutral_fill":True,
        "no_candidate_to_production_substitution":True,
    }

def _production_index_coverage_diagnostic(runners: list[dict], mapping: dict) -> dict:
    """Explain every runner x Base13 gap using the *existing* authorized weights.

    Diagnostic only. Never materialize a missing feature or change a score.
    """
    base = ("HPI","SSI","CFI","RFI","BVI","JTI","CSI",
            "TRI","BWI","GCI","PRI","KGI","VMI")
    try:
        from .jra_evidence_to_base_production import _feature_score, ProductionMappingError
    except ImportError:
        from jra_evidence_to_base_production import _feature_score, ProductionMappingError
    rows = []
    for runner in runners:
        rid = str(runner.get("runner_id") or "")
        career = runner.get("career_starts")
        if career is None:
            profile = "NEWCOMER" if runner.get("newcomer") is True else None
        else:
            starts = int(career)
            profile = "NEWCOMER" if starts <= 0 else ("LOW_CAREER" if starts <= 3 else "ESTABLISHED")
        if profile is None:
            for index in base:
                rows.append({"runner_id":rid, "index_id":index,
                             "profile":"UNRESOLVED", "status":"BLOCKED",
                             "reason":"CAREER_STARTS_MISSING",
                             "required_features":[], "missing_features":[]})
            continue
        spec = mapping["index_profiles"][profile]
        minimum = float(mapping["profiles"][profile]["minimum_index_coverage_weight"])
        evidence = runner.get("evidence_features") or {}
        for index in base:
            weights = spec[index]
            available = []
            missing = []
            covered = 0.0
            for name, weight in weights.items():
                try:
                    # Use the *same* Production authority firewall as the actual
                    # numerical evaluator. A syntactically complete Shadow or
                    # result-derived fact must not close an index gap.
                    evaluated = _feature_score(name, evidence, mapping)
                    if evaluated is None:
                        raise ProductionMappingError("FEATURE_MISSING")
                    covered += float(weight)
                    available.append(name)
                except (ProductionMappingError, ValueError, TypeError) as exc:
                    missing.append({
                        "feature": name,
                        "weight": float(weight),
                        "validation_reason": str(exc),
                    })
            rows.append({"runner_id":rid,"index_id":index,"profile":profile,
                         "status":"COVERAGE_THRESHOLD_MET" if covered + 1e-12 >= minimum else "BLOCKED",
                         "coverage_weight":round(covered,6),"required_weight":minimum,
                         "required_features":list(weights),
                         "available_features":available,
                         "missing_features":missing,
                         "reason":None if covered + 1e-12 >= minimum else "INDEX_EVIDENCE_COVERAGE_LOW"})
    blocked = [row for row in rows if row["status"]=="BLOCKED"]
    return {"schema":"KM-JRA-PRODUCTION-BASE13-INDEX-COVERAGE-DIAGNOSTIC-v1",
            "rows":rows, "required":len(rows), "blocked":len(blocked),
            "all_base_index_coverage_met":not blocked,
            "authority":"DIAGNOSTIC_ONLY / PRODUCTION_MAPPING_UNCHANGED",
            "no_missing_value_imputation":True}



def _source_only_coverage_repair_plan(index_coverage: dict, features: dict) -> dict:
    """Identify the smallest *candidate* missing-feature set per blocked Base13 index.

    The plan is advisory: factual availability does not authorize an evaluator,
    and the plan must never generate Evidence or Production scores.
    """
    trace_by_runner = (features.get("runners") or {})
    rows = []
    feature_frequency: dict[str, int] = {}
    for index_row in index_coverage.get("rows") or []:
        if index_row.get("status") != "BLOCKED":
            continue
        rid = str(index_row.get("runner_id") or "")
        missing = index_row.get("missing_features") or []
        deficit = max(
            0.0,
            float(index_row.get("required_weight") or 0.0)
            - float(index_row.get("coverage_weight") or 0.0),
        )
        feature_trace = ((trace_by_runner.get(rid) or {}).get("source_feature_trace") or {}).get("features") or {}
        options = []
        for item in missing:
            name = str(item["feature"])
            trace = feature_trace.get(name) or {}
            fact_available = trace.get("fact_available")
            options.append({
                "feature": name,
                "weight": float(item["weight"]),
                "fact_available": fact_available if isinstance(fact_available, bool) else None,
                "source_family": trace.get("source_family"),
                "correct_owner": (
                    "JRA_PRODUCTION_FEATURE_EVALUATOR_OR_AUTHORITY"
                    if fact_available is True else "JRA_SOURCE_ADAPTER_OR_FACT_ACQUISITION"
                    if fact_available is False else "UNRESOLVED_EVIDENCE_PROVENANCE"
                ),
            })
        # The fewest components needed to clear a coverage threshold can be
        # found greedily by weight. Factual availability breaks ties, but NEVER
        # authorizes use. This is not a proposed Production feature selection.
        options.sort(key=lambda x: (
            -x["weight"],
            0 if x["fact_available"] is True else 1 if x["fact_available"] is None else 2,
            x["feature"],
        ))
        chosen = []
        restored = 0.0
        for option in options:
            if restored + 1e-12 >= deficit:
                break
            chosen.append(option)
            restored += option["weight"]
            feature_frequency[option["feature"]] = feature_frequency.get(option["feature"], 0) + 1
        rows.append({
            "runner_id": rid,
            "index_id": index_row["index_id"],
            "profile": index_row.get("profile"),
            "missing_coverage_weight": round(deficit, 6),
            "additional_weight_if_all_chosen_authorized": round(restored, 6),
            "conditional_minimum_missing_feature_count": len(chosen),
            "conditional_repair_features": chosen,
            "authorized_evaluators_required": True,
            "closure_proven": False,
            "closure_feasible_with_available_facts_only": (
                bool(chosen) and restored + 1e-12 >= deficit
                and all(x["fact_available"] is True for x in chosen)
            ),
        })
    return {
        "schema": "KM-JRA-SOURCE-ONLY-BASE13-CLOSURE-PLAN-v1",
        "status": "DIAGNOSTIC_ONLY / NO_FEATURE_PROMOTION / NO_PREDICTION_POLICY_CHANGE",
        "blocked_index_count": len(rows),
        "conditional_repair_rows": rows,
        "highest_coverage_impact_features": [
            {"feature": name, "blocked_indices_affected": count}
            for name, count in sorted(feature_frequency.items(), key=lambda z: (-z[1], z[0]))
        ],
        "static_owner_independent_blocker": "NO_AUTHORIZED_SOURCE_ONLY_STATIC_RANK_ROLE_DECISION_RULE_CONNECTED",
        "production_authority_granted": False,
    }


def prepare_production_numerical(intent: Dict[str,Any], source_env: Dict[str,Any], *, source_execution_id: str | None = None,
                                 current_authority: Dict[str,Any] | None = None) -> Dict[str,Any]:
    """Expose the existing JRA numerical boundary; never manufacture Static roles.

    This is a preparation report, not signature verification or a FINAL receipt.
    SOURCE authentication remains owned by the existing signed-receipt loader.
    """
    try:
        from .jra_zero_touch_source_index_orchestrator import build_source_runner_stubs
        from .jra_source_to_evidence_features import compile_source_to_features
        from .jra_evidence_to_base_production import load_mapping, build_production_ledger, evaluate_partial_production_base_indices
        from .jra_index_provenance_builder import materialize_index_provenance
        from .jra_supplemental_evidence_pack import apply_supplemental_evidence_pack
    except ImportError:
        from jra_zero_touch_source_index_orchestrator import build_source_runner_stubs
        from jra_source_to_evidence_features import compile_source_to_features
        from jra_evidence_to_base_production import load_mapping, build_production_ledger, evaluate_partial_production_base_indices
        from jra_index_provenance_builder import materialize_index_provenance
        from jra_supplemental_evidence_pack import apply_supplemental_evidence_pack

    _require_jra(intent)
    source = source_env.get("artifact") or {}
    checkpoint = source_checkpoint_manifest(source_env, source_execution_id or _execution_id(intent))
    if source.get("race_id") != intent["race_id"] or source.get("prediction_cutoff") != intent["prediction_cutoff"]:
        raise JRAMaturityBridgeError("JRA_PRODUCTION_PREPARATION_SOURCE_IDENTITY_MISMATCH")
    official = source.get("jra_official_runner_universe") or source.get("official_runner_universe") or {}
    ids = [str(r.get("runner_id") or r.get("horse_no") or "") for r in official.get("runners") or []]
    if len(ids) < 2 or "" in ids or len(set(ids)) != len(ids):
        raise JRAMaturityBridgeError("JRA_PRODUCTION_PREPARATION_OFFICIAL_UNIVERSE_INVALID")
    # Detail cards may enrich an official runner, never add a new runner.
    runners = [r for r in build_source_runner_stubs(source) if r["runner_id"] in set(ids)]
    mapping = load_mapping("mapping/jra_base_index_evidence_mapping_v1.0_20260921.json")
    req = {"family_id":"JRA", "race_id":intent["race_id"],
           "prediction_cutoff":intent["prediction_cutoff"],
           "acceptance_only":bool(intent.get("acceptance_only")), "runners":runners}
    if intent.get("supplemental_evidence_pack") is not None:
        req, _ = apply_supplemental_evidence_pack(req, intent["supplemental_evidence_pack"], mapping)
    features = compile_source_to_features(source, req["runners"], mapping)
    gaps = []
    for runner in req["runners"]:
        rid = runner["runner_id"]
        rr = features["runners"][rid]
        runner.update(rr["factual_runner_updates"])
        for name, value in rr["generated_production_features"].items():
            runner["evidence_features"].setdefault(name, copy.deepcopy(value))
        for name, row in rr["source_feature_trace"]["features"].items():
            if row["production_feature_state"] != "MISSING":
                continue
            gaps.append({"runner_id":rid, "feature":name,
                         "source_fact_available":row["fact_available"],
                         "production_evaluator_available":None,
                         "evaluator_implementation_status":"NOT_ESTABLISHED_BY_PRODUCTION_FEATURE_TRACE",
                         "rule_id":row["rule_id"], "authority":row["source_authority"],
                         "source_family":row["source_family"],
                         "automation_class":row["automation_class"],
                         "index_binding":row["target_bindings"],
                         "evidence_refs":row["evidence_refs"],
                         "missing_reason":row["missing_reason"],
                         "correct_owner":"JRA_SOURCE_ADAPTER" if row["fact_available"] is False else "JRA_PRODUCTION_FEATURE_EVALUATOR_OR_AUTHORITY"})
    numeric_error = None
    try:
        req["index_provenance_ledger"] = build_production_ledger(intent["race_id"], req["runners"], mapping)
        # Bind authority to the real Production ledger only after the existing
        # evidence-based evaluator has succeeded for every index.
        req["base_index_mapping_authority"] = {
            "mapping_id": mapping["mapping_id"],
            "status": mapping["status"],
            "production_authority": True,
            "calibration_status": mapping.get("calibration_status"),
        }
        req = materialize_index_provenance(req)
        numerical_ready = all(len(r.get("canonical_components") or {}) == 20 for r in req["runners"])
    except ValueError as exc:
        numerical_ready = False
        numeric_error = str(exc)
    partial_base = evaluate_partial_production_base_indices(intent["race_id"], req["runners"], mapping)
    index_coverage = _production_index_coverage_diagnostic(req["runners"], mapping)
    gap_summary = _production_gap_summary(gaps)
    closure_plan = _source_only_coverage_repair_plan(index_coverage, features)
    supplemental_supplied = intent.get("supplemental_evidence_pack") is not None
    source_only_ready = (numerical_ready and not supplemental_supplied
                         and bool(features.get("source_only_formal_base_ready")))
    # Both observational feature proposals and numerical->Static conversion
    # execute in a strictly separate CANDIDATE lane. Neither satisfies a
    # Production evaluator or Production Static Owner acceptance gate.
    candidate_fact_evaluation = None
    candidate_fact_evaluation_error = None
    static_owner_candidate = None
    static_owner_candidate_error = None
    try:
        from .jra_source_only_closure_candidate import (
            propose_official_observed_features, evaluate_static_owner_candidate,
        )
    except ImportError:
        from jra_source_only_closure_candidate import (
            propose_official_observed_features, evaluate_static_owner_candidate,
        )
    try:
        candidate_fact_evaluation = propose_official_observed_features(source)
    except ValueError as exc:
        candidate_fact_evaluation_error = str(exc)
    if numerical_ready:
        try:
            static_owner_candidate = evaluate_static_owner_candidate(
                req, source_snapshot_sha256=str(source.get("source_snapshot_sha256") or "")
            )
        except ValueError as exc:
            static_owner_candidate_error = str(exc)
    # Executable deterministic Static Owner runs independently of the old
    # Candidate semantics but is not promoted by a successful computation.
    static_executable = None
    static_executable_error = None
    if numerical_ready:
        try:
            try:
                from .jra_static_owner_executable import compile_static_owner
            except ImportError:
                from jra_static_owner_executable import compile_static_owner
            static_executable = compile_static_owner(
                req,
                source_snapshot_sha256=checkpoint["source_snapshot_sha256"],
                source_receipt_sha256=checkpoint["receipt_sha256"],
                frozen_at=(checkpoint["source_freeze_at"] if intent.get("acceptance_only") is True else datetime.now(timezone.utc).isoformat()),
                prediction_cutoff=intent["prediction_cutoff"],
            )
        except ValueError as exc:
            static_executable_error = str(exc)
    # Read-only Static Owner activation state. It is reported (never granted)
    # so the readiness flags agree with the auto-handoff gate.
    try:
        from .jra_production_blocker_classifier import (
            owner_activation_status, structural_closure_feasibility,
        )
    except ImportError:
        from jra_production_blocker_classifier import (
            owner_activation_status, structural_closure_feasibility,
        )
    if current_authority is None:
        try:
            current_authority = load_current_authority()
        except JRAMaturityBridgeError:
            current_authority = None
    authority_id = str((current_authority or {}).get("manifest_id") or resolve_current_authority())
    owner_status = owner_activation_status(current_authority)
    owner_activation_error = None if owner_status["authorized"] else owner_status["reason"]
    static_ready = bool(numerical_ready and owner_status["authorized"]
                        and isinstance(static_executable, dict)
                        and static_executable.get("static_prediction"))
    blockers = []
    if not numerical_ready:
        blockers.append({"stage":"PRODUCTION_FEATURE_INDEX_CLOSURE", "reason":numeric_error})
    if owner_activation_error:
        blockers.append({"stage":"PRODUCTION_STATIC_PREDICTION_OWNER", "reason":owner_activation_error})
    elif static_executable_error:
        blockers.append({"stage":"PRODUCTION_STATIC_PREDICTION_OWNER", "reason":static_executable_error})
    report = {"profile":PROFILE, "family_id":"JRA", "race_id":intent["race_id"],
              "evidence_class":"NUMERICAL_PREPARATION_ONLY / NOT_SIGNATURE_VERIFICATION / NOT_FINAL / NOT_OOS",
              "current_authority_manifest":authority_id,
              "mapping_id":mapping["mapping_id"],
              "mapping_sha256":hashlib.sha256(Path("mapping/jra_base_index_evidence_mapping_v1.0_20260921.json").read_bytes()).hexdigest(),
              "source_checkpoint_manifest":checkpoint,
              "runner_universe":ids, "source_feature_trace_schema":features["trace_schema"],
              "source_feature_report":features, "exact_gaps":gaps,
              "exact_gap_count":len(gaps),
              "production_closure_summary":gap_summary,
              "base_index_coverage_diagnostic":index_coverage,
              "partial_production_base_calculation":partial_base,
              "partial_base_calculated_count":partial_base["calculated_base_cells"],
              "partial_base_blocked_count":partial_base["blocked_base_cells"],
              "source_only_coverage_repair_plan":closure_plan,
              "required_index_count":len(ids)*20,
              "verified_full_index_count":len(ids)*20 if numerical_ready else 0,
              "source_only_full_numerical_ready":source_only_ready,
              "numerical_closure_mode":("SOURCE_ONLY" if source_only_ready else
                  "WITH_SUPPLEMENTAL_EVIDENCE" if numerical_ready and supplemental_supplied else
                  "BLOCKED"),
              "candidate_official_observed_feature_report":candidate_fact_evaluation,
              "candidate_official_observed_feature_error":candidate_fact_evaluation_error,
              "static_owner_candidate_diagnostic":static_owner_candidate,
              "static_owner_candidate_error":static_owner_candidate_error,
              "static_owner_executable_diagnostic":static_executable,
              "static_owner_executable_error":static_executable_error,
              "production_full_numerical_ready":numerical_ready,
              "production_numerical_error":numeric_error,
              "prepared_numerical_request":req if numerical_ready else None,
              "first_blocked_stage":blockers[0]["stage"] if blockers else None,
              "independent_blockers":blockers,
              "static_owner_activation_error":owner_activation_error,
              "static_owner_activation_status":owner_status,
              "static_generation_ready":static_ready,
              "static_generation_missing_reason":owner_activation_error or static_executable_error,
              "production_auto_handoff_ready":static_ready,
              # Local readiness to hand a PRE_KRS request to the canonical
              # Formal Runner. External KRS / MEC / Capital / Signed FINAL are
              # never implied by this flag.
              "production_full_pipeline_ready":static_ready,
              "production_full_pipeline_ready_scope":"LOCAL_PRE_KRS_HANDOFF_ONLY",
              "completion_next_owner":(
                  "JRA_PRODUCTION_FEATURE_EVALUATOR_OR_SOURCE_ADAPTER"
                  if not numerical_ready else
                  "JRA_PRODUCTION_STATIC_PREDICTION_OWNER" if not static_ready else
                  "CANONICAL_FORMAL_RUNNER"
              ),
              "candidate_parallel_required":True,
              "candidate_parallel_reason":"Preserve all-stage execution without mislabeling Candidate as Production.",
              "status":"PARTIAL_EXACT_GAP_IDENTIFIED", "production_prediction_change":False,
              "production_numerical_change":False, "candidate_numerics_used":False}
    try:
        from .jra_production_blocker_classifier import classify_production_blockers
    except ImportError:
        from jra_production_blocker_classifier import classify_production_blockers
    feasibility = structural_closure_feasibility(report, mapping)
    report["structural_closure_feasibility"] = feasibility
    # Temporal state is evaluated by the live caller, not by a reproducible
    # preparation report (historical recomputation must stay deterministic).
    report["production_blocker_classification"] = classify_production_blockers(
        report, owner_status=owner_status, intent=None, feasibility=feasibility)
    report["sha256"] = _sha(report)
    return report

def build_formal_request(
    intent: Dict[str,Any],
    source_env: Dict[str,Any],
    *,
    source_execution_id: str|None=None,
) -> Dict[str,Any]:
    _require_jra(intent)
    source_execution_id=str(source_execution_id or _execution_id(intent)).strip()
    checkpoint=source_checkpoint_manifest(source_env,source_execution_id)
    artifact=source_env.get("artifact") or {}
    if str(artifact.get("race_id") or "")!=str(intent.get("race_id") or ""):
        raise JRAMaturityBridgeError("JRA_SINGLE_ENTRY_SOURCE_RACE_MISMATCH")
    if str(artifact.get("prediction_cutoff") or "")!=str(intent.get("prediction_cutoff") or ""):
        raise JRAMaturityBridgeError("JRA_SINGLE_ENTRY_SOURCE_CUTOFF_MISMATCH")

    out=copy.deepcopy(intent)
    out.pop("jra_source",None)
    out["family_id"]="JRA"
    resolved_authority=resolve_current_authority()
    declared_authority=str(out.get("current_authority_manifest") or "").strip()
    if declared_authority and declared_authority!=resolved_authority:
        raise JRAMaturityBridgeError(
            "JRA_SINGLE_ENTRY_STALE_CURRENT_AUTHORITY:"
            +declared_authority+"!="+resolved_authority
        )
    out["current_authority_manifest"]=resolved_authority
    out["execution_id"]=_execution_id(intent)
    out["source_execution_id"]=source_execution_id
    out["temporal_mode"]=str(out.get("temporal_mode") or "FORMAL-PRE-RACE")
    out["static_prediction_frozen"]=bool(out.get("static_prediction_frozen"))
    static=out.get("static_prediction")
    if not isinstance(static,dict):
        raise JRAMaturityBridgeError("JRA_SINGLE_ENTRY_STATIC_PREDICTION_REQUIRED")
    if out["static_prediction_frozen"] is not True:
        raise JRAMaturityBridgeError("JRA_SINGLE_ENTRY_STATIC_FREEZE_REQUIRED")
    static=copy.deepcopy(static)
    static["source_basis_receipt_sha256"]=checkpoint["receipt_sha256"]
    static["source_basis_snapshot_sha256"]=checkpoint["source_snapshot_sha256"]
    static["source_checkpoint_manifest_sha256"]=checkpoint["sha256"]
    out["static_prediction"]=static
    out["source_checkpoint_manifest"]=checkpoint
    out["jra_maturity_bridge"]={
        "profile":PROFILE,
        "origin_family":"LOCAL",
        "target_family":"JRA",
        "promotion_class":"C0_SCHEMA_INTERFACE + C1_EXECUTION_CORRECTNESS",
        "imported_mechanisms":[
            "SINGLE_ENTRY_CONTINUATION",
            "STABLE_EXECUTION_ID",
            "DURABLE_SOURCE_CHECKPOINT_REUSE",
            "STATIC_SIGNED_SOURCE_BINDING",
            "FORMAL_SEMANTIC_BASIS",
            "FAIL_CLOSED_RESUME_DIAGNOSTICS",
            "ENTRY_TRANSPORT_SEMANTIC_HASH",
            "FAST_POSTRESULT_REFLECTION",
        ],
        "excluded_cross_family_material":[
            "LOCAL_SOURCE_ADAPTER",
            "LOCAL_EVIDENCE_RULES",
            "LOCAL_NUMERICAL_MAPPING",
            "LOCAL_PARAMETER_MAP",
            "LOCAL_PREDICTION_COEFFICIENTS",
            "LOCAL_VENUE_MECHANISMS",
            "LOCAL_MEC_R5_PRODUCTION_AUTHORITY",
        ],
        "production_prediction_change":False,
        "production_numerical_change":False,
        "krs_physics_change":False,
        "mec_r3_change":False,
        "capital_policy_change":False,
        "automatic_promotion":False,
        "resolved_current_authority_manifest":resolved_authority,
    }
    out["formal_semantic_basis_sha256"]=semantic_sha256(out)
    return out

def verify_formal_request_binding(req: Dict[str,Any], source_env: Dict[str,Any]) -> Dict[str,Any]:
    _require_jra(req)
    meta=req.get("jra_maturity_bridge")
    if not isinstance(meta,dict):
        return {"profile":PROFILE,"status":"NOT_APPLICABLE"}
    if meta.get("profile")!=PROFILE:
        raise JRAMaturityBridgeError("JRA_MATURITY_PROFILE_MISMATCH")
    source_execution_id=str(req.get("source_execution_id") or "").strip()
    if not source_execution_id:
        raise JRAMaturityBridgeError("JRA_MATURITY_SOURCE_EXECUTION_ID_REQUIRED")
    checkpoint=source_checkpoint_manifest(source_env,source_execution_id)
    static=req.get("static_prediction")
    if not isinstance(static,dict):
        raise JRAMaturityBridgeError("JRA_MATURITY_STATIC_REQUIRED")
    expected={
        "source_basis_receipt_sha256":checkpoint["receipt_sha256"],
        "source_basis_snapshot_sha256":checkpoint["source_snapshot_sha256"],
        "source_checkpoint_manifest_sha256":checkpoint["sha256"],
    }
    for k,v in expected.items():
        if str(static.get(k) or "")!=str(v):
            raise JRAMaturityBridgeError(f"JRA_MATURITY_STATIC_SOURCE_BINDING_MISMATCH:{k}")
    declared=str(req.get("formal_semantic_basis_sha256") or "")
    actual=semantic_sha256(req)
    if not declared or declared!=actual:
        raise JRAMaturityBridgeError(
            f"JRA_MATURITY_FORMAL_SEMANTIC_HASH_MISMATCH:{declared}!={actual}"
        )
    if meta.get("production_prediction_change") is not False:
        raise JRAMaturityBridgeError("JRA_MATURITY_PREDICTION_CHANGE_FORBIDDEN")
    if meta.get("production_numerical_change") is not False:
        raise JRAMaturityBridgeError("JRA_MATURITY_NUMERICAL_CHANGE_FORBIDDEN")
    return {
        "profile":PROFILE,
        "status":"PASS",
        "source_execution_id":source_execution_id,
        "source_checkpoint_manifest_sha256":checkpoint["sha256"],
        "formal_semantic_basis_sha256":actual,
        "production_effect":"NONE",
    }

def require_manual_static_parity(intent: Dict[str,Any], report: Dict[str,Any]) -> Dict[str,Any]:
    """Apply the SAME numerical/source/authority boundary to an explicit Static.

    An explicit (manual) Static is an existing Production entry, but it may not
    be used to bypass the automatic Owner gate: Full20 must be Actual from the
    same signed SOURCE, and no unapproved Candidate Owner output may be
    relabelled as an explicit Static.
    """
    blockers=[]
    supplemental=intent.get("supplemental_evidence_pack")
    verified_supplement=(report.get("numerical_closure_mode")=="WITH_SUPPLEMENTAL_EVIDENCE"
                         and intent.get("acceptance_only") is not True
                         and isinstance(supplemental,dict))
    if (report.get("production_full_numerical_ready") is not True
            or report.get("verified_full_index_count")!=report.get("required_index_count")
            or not (report.get("source_only_full_numerical_ready") is True or verified_supplement)):
        blockers.append("JRA_AUTHORIZED_FULL20_INCOMPLETE")
    try:
        from .jra_static_owner_executable import PROFILE as OWNER_PROFILE
    except ImportError:
        from jra_static_owner_executable import PROFILE as OWNER_PROFILE
    def tainted(row: Any) -> bool:
        if not isinstance(row,dict):
            return False
        marks=" ".join(str(row.get(k) or "") for k in ("authority","profile","status","policy_id")).upper()
        return (row.get("production_authority") is False or row.get("candidate_only") is True
                or row.get("candidate_policy") is True or OWNER_PROFILE.upper() in marks
                or "CANDIDATE" in marks or "SHADOW" in marks)
    static=intent.get("static_prediction")
    if tainted(static) or any(tainted(r) for k in ("role_registry","pair_dispositions","third_dispositions")
                              for r in (intent.get(k) or [])):
        blockers.append("JRA_MANUAL_STATIC_CANDIDATE_OR_SHADOW_AUTHORITY_FORBIDDEN")
    owner=report.get("static_owner_executable_diagnostic") or {}
    owner_authorized=((report.get("static_owner_activation_status") or {}).get("authorized") is True)
    if (isinstance(static,dict) and not owner_authorized and isinstance(owner.get("static_prediction"),dict)
            and [str(x) for x in static.get("ranking") or []]==[str(x) for x in owner["static_prediction"].get("ranking") or []]
            and {str(k):sorted(v) for k,v in (static.get("roles") or {}).items() if v}
                =={str(k):sorted(v) for k,v in (owner["static_prediction"].get("roles") or {}).items() if v}):
        blockers.append("JRA_MANUAL_STATIC_EQUALS_UNAUTHORIZED_CANDIDATE_OWNER")
    if blockers:
        raise JRAMaturityBridgeError("JRA_SINGLE_ENTRY_MANUAL_STATIC_BLOCKED:"+",".join(blockers))
    return {"status":"PASS","numerical_closure_mode":report.get("numerical_closure_mode"),
            "verified_full_index_count":report.get("verified_full_index_count")}


def main() -> int:
    p=argparse.ArgumentParser()
    sp=p.add_subparsers(dest="cmd",required=True)

    s=sp.add_parser("build-source")
    s.add_argument("--intent",required=True)
    s.add_argument("--output",required=True)

    f=sp.add_parser("build-formal")
    f.add_argument("--intent",required=True)
    f.add_argument("--source-envelope",required=True)
    f.add_argument("--source-execution-id")
    f.add_argument("--output",required=True)
    f.add_argument("--gap-output")

    v=sp.add_parser("verify-formal")
    v.add_argument("--request",required=True)
    v.add_argument("--source-envelope",required=True)
    v.add_argument("--output")

    args=p.parse_args()
    if args.cmd=="build-source":
        out=build_source_request(_load(args.intent))
    elif args.cmd=="build-formal":
        intent = _load(args.intent)
        source_env = _load(args.source_envelope)
        # Both the automatic and the explicit-Static entry compute the SAME
        # Production numerical report from the SAME signed SOURCE and persist
        # it, so every stop is diagnosable and neither entry skips the gate.
        report = prepare_production_numerical(intent, source_env, source_execution_id=args.source_execution_id)
        gap_path = Path(args.gap_output or (args.output + ".exact-gap.json"))
        gap_path.parent.mkdir(parents=True, exist_ok=True)
        gap_path.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
        classification = report.get("production_blocker_classification") or {}
        diag = ("FIRST=" + str(classification.get("first_actual_blocked_stage"))
                + ":INDEPENDENT=" + ",".join(classification.get("independent_blocker_stages") or [])
                + ":ROUTE=" + str(classification.get("terminal_route")))
        if not isinstance(intent.get("static_prediction"), dict):
            try:
                # The existing External Single-Entry workflow owns signed
                # SOURCE acquisition. No Static Owner is self-approved here.
                from jra_production_auto_handoff import compile_production_auto_handoff
                authority_obj = load_current_authority()
                auto = compile_production_auto_handoff(
                    intent, source_env, report,
                    current_authority=authority_obj,
                    frozen_at=datetime.now(timezone.utc).isoformat(),
                )
                out = build_formal_request(
                    auto, source_env, source_execution_id=args.source_execution_id
                )
            except (ValueError, KeyError, TypeError) as exc:
                # Persist the actual failure before raising. An unapproved
                # Static owner or invalid transport is not missing evidence.
                report["auto_handoff_error"] = str(exc)
                from jra_single_entry_outcome import evidence_terminal_eligible
                report["evidence_no_bet_eligible"] = evidence_terminal_eligible(report)
                report["sha256"] = _sha({k: v for k, v in report.items() if k != "sha256"})
                gap_path.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
                raise JRAMaturityBridgeError(
                    "JRA_SINGLE_ENTRY_AUTO_FORMAL_BLOCKED:"
                    + str(exc) + ":" + str(report["first_blocked_stage"]) + ":" + diag + ":" + str(gap_path)
                ) from exc
        else:
            try:
                require_manual_static_parity(intent, report)
            except JRAMaturityBridgeError as exc:
                raise JRAMaturityBridgeError(
                    str(exc) + ":" + str(report["first_blocked_stage"]) + ":" + diag + ":" + str(gap_path)
                ) from exc
            out=build_formal_request(
                intent,source_env,
                source_execution_id=args.source_execution_id
            )
    else:
        out=verify_formal_request_binding(_load(args.request),_load(args.source_envelope))
    if getattr(args,"output",None):
        q=Path(args.output); q.parent.mkdir(parents=True,exist_ok=True)
        q.write_text(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,ensure_ascii=False,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())

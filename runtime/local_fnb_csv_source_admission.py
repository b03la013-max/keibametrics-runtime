"""Research CSV SOURCE candidate, never a fabricated HTML card or admission.

Reparse the exact original ZIP with the existing NAR parser. Independent,
trusted gates must attest Provider rights and official latest changes. A
normalized candidate uses the shared parsed-evidence schema; existing R13/R20
HTML admission is deliberately unchanged. CSV Profile adoption and the existing
SOURCE signature verifier are separate prerequisites, never caller flags.
No network, signer, Production consumer, or permanent-ID inference is present.
"""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
import base64
import hashlib
import json
import re

from runtime.local_nar_csv_reference import inspect_zip, _norm, _dt

PROFILE = "KM-FNB-NAR-CSV-SOURCE-CANDIDATE-v0.1-20261103"
SOURCE_CLASS = "OFFICIAL_NAR_CSV_ZIP_RESEARCH_CANDIDATE"
SHA = re.compile(r"[0-9a-f]{64}")


class CsvAdmissionHold(ValueError):
    pass


def sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def _same_race(left, right):
    keys = ("venue_id", "race_date", "race_no")
    return all(left.get(k) == right.get(k) for k in keys)


def _number(value, integer=False):
    """Absent/unparseable measurements stay UNKNOWN; no default neutral."""
    text = str(value or "").strip()
    if not re.fullmatch(r"[+-]?\d+(?:\.\d+)?", text):
        return None
    number = float(text)
    if integer and not number.is_integer():
        return None
    return int(number) if integer else number


def _decision(verifier, **kwargs):
    if not callable(verifier):
        return {}
    # Only an independently configured gate may return this decision. Payload
    # booleans are not gates and are never interpreted as Provider permission.
    result = verifier(**deepcopy(kwargs))
    return result if isinstance(result, dict) else {}


def assess(*, raw, capture, request, encoding, header_mode, freeze_at, actor_id,
           qualification_verifier=None, official_change_packet=None,
           official_change_verifier=None, source_receipt=None,
           source_receipt_verifier=None, now=None):
    """Return all explicit terminals and an unsigned, format-honest candidate.

    Gate interfaces are trusted code dependencies, not values from ``capture``.
    Qualification binds Provider/raw/URL/method/Actor/permission/validity.
    The official-change gate must reverify its original raw and signed/external
    receipt, returning complete declared runners, ACTIVE/CANCELLED/EXCLUDED
    status, official Race ID and current jockey facts. This module never infers
    those facts from CSV headcount or names. Missing gates produce HOLD.
    """
    now = _dt(now or datetime.now(timezone.utc)); freeze = _dt(freeze_at)
    race = {"venue_id": request.get("venue_id"), "race_date": request.get("race_date"),
            "race_no": request.get("race_no")}
    for field in ("scheduled_post_at",):
        race[field] = request[field]
    requested = request.get("race") or {}
    if requested.get("distance_m") is not None: race["distance_m"] = requested["distance_m"]
    if requested.get("surface") is not None: race["surface"] = requested["surface"]
    if requested.get("direction") is not None: race["turn"] = requested["direction"]
    parsed = inspect_zip(raw, capture=capture, race=race, encoding=encoding,
                         header_mode=header_mode, now=now)
    captured = _dt(capture["captured_at"])
    cutoff = _dt(request["prediction_cutoff"]); post = _dt(request["scheduled_post_at"])
    reasons = []
    if not captured <= freeze <= now < cutoff < post:
        reasons.append("CSV_FETCH_FREEZE_NOW_CUTOFF_POST_ORDER_INVALID")
    if parsed["target_outcome_fields_present"]:
        reasons.append("CSV_TARGET_OUTCOME_FIELDS_PRESENT_NOT_PRESTART")
    if not parsed["race_identity"].get("surface") or not parsed["race_identity"].get("turn"):
        reasons.append("CSV_RACE_SURFACE_OR_DIRECTION_UNRESOLVED")
    if (not isinstance(request.get("race_id"), str)
            or not re.fullmatch(r"KM-LOCAL-FNB-"+race["race_date"].replace("-", "")
                               +rf"-R{race['race_no']:02d}(?:-[A-Za-z0-9_]+)*", request["race_id"])):
        reasons.append("CSV_INTENT_RACE_ID_MISMATCH")
    rights = _decision(qualification_verifier, capture=capture, raw_sha256=capture["raw_sha256"],
                       actor_id=actor_id, freeze_at=freeze_at, now=now.isoformat())
    try:
        rights_ok = (rights.get("passed") is True and rights.get("provider_id") == "NAR_OFFICIAL_CSV"
            and rights.get("raw_sha256") == capture["raw_sha256"]
            and rights.get("source_url") == capture["source_url"]
            and rights.get("retrieval_method") == capture["retrieval_method"]
            and rights.get("actor_id") == actor_id and bool(rights.get("permission_ref"))
            and bool(SHA.fullmatch(str(rights.get("permission_sha256", ""))))
            and rights.get("private_retention_authorized") is True
            and rights.get("cloud_processing_authorized") is True
            and rights.get("retrieval_method_authorized") is True
            and _dt(rights["effective_from"]) <= captured
            and now < _dt(rights["effective_until"]))
    except (KeyError, ValueError, TypeError):
        rights_ok = False
    if not rights_ok: reasons.append("CSV_PROVIDER_QUALIFICATION_UNVERIFIED")

    packet = official_change_packet or {}
    changes_raw = packet.get("raw")
    change_digest = hashlib.sha256(changes_raw).hexdigest() if isinstance(changes_raw, bytes) and changes_raw else None
    changes = _decision(official_change_verifier, packet=packet, request=request,
                        csv_raw_sha256=capture["raw_sha256"], freeze_at=freeze_at)
    try:
        changes_ok = (bool(change_digest) and changes.get("passed") is True
            and changes.get("raw_sha256") == change_digest
            and changes.get("csv_raw_sha256") == capture["raw_sha256"]
            and changes.get("request_race_id") == request["race_id"]
            and _dt(changes["freeze_at"]) == freeze
            and _dt(changes["cutoff_at"]) == cutoff
            and _dt(changes["csv_captured_at"]) == captured
            and changes.get("authority") in {"NAR_OFFICIAL", "NANKAN_OFFICIAL", "FKEIBA_OFFICIAL"}
            and changes.get("original_raw_reparsed") is True
            and changes.get("external_receipt_verified") is True
            and bool(SHA.fullmatch(str(changes.get("receipt_sha256", ""))))
            and _same_race(changes.get("race_identity") or {}, race)
            and bool(changes.get("official_race_id"))
            and changes.get("complete_declared_universe") is True
            and changes.get("latest_changes_verified") is True
            and captured <= _dt(changes["observed_at"]) <= freeze
            and _dt(changes["source_updated_at"]) <= _dt(changes["observed_at"]))
    except (KeyError, ValueError, TypeError):
        changes_ok = False
    if not changes_ok: reasons.append("CSV_INDEPENDENT_OFFICIAL_CHANGES_UNVERIFIED")
    if changes_ok:
        conditions = changes.get("race_identity") or {}
        required_conditions = ("scheduled_post_at", "distance_m", "surface", "turn")
        if any(conditions.get(k) is None for k in required_conditions):
            reasons.append("CSV_OFFICIAL_RACE_CONDITIONS_UNVERIFIED")
        else:
            for field in required_conditions:
                left, right = conditions[field], parsed["race_identity"][field]
                if field == "scheduled_post_at": left, right = _dt(left), _dt(right)
                if left != right: reasons.append("CSV_OFFICIAL_RACE_CONDITION_CONFLICT:"+field)
        for event in changes.get("events") or []:
            if event.get("field") not in {"jockey", "status"}:
                reasons.append("CSV_OFFICIAL_CHANGE_FIELD_NOT_IMPLEMENTED:"+str(event.get("field")))
    candidate = None; parsed_rows = None; reconciliation = []
    if changes_ok:
        csv_rows = {str(r["runner_number"]): r for r in parsed["runners"]}
        official = {}; events = changes.get("events") or []
        for row in changes.get("runners") or []:
            rid = str(row.get("horse_no"))
            if (not rid.isdigit() or int(rid) < 1 or rid in official or not row.get("name")
                    or row.get("status") not in {"ACTIVE", "CANCELLED", "EXCLUDED"}):
                reasons.append("CSV_OFFICIAL_RUNNER_STATUS_OR_ID_INVALID"); continue
            official[rid] = row
        active = {rid: r for rid, r in official.items() if r["status"] == "ACTIVE"}
        if not official or not active or set(csv_rows)-set(official) or set(active)-set(csv_rows):
            reasons.append("CSV_OFFICIAL_DECLARED_OR_ACTIVE_UNIVERSE_MISMATCH")
        for rid in set(csv_rows) & set(official):
            if _norm(csv_rows[rid]["horse_name"]) != _norm(official[rid]["name"]):
                reasons.append("CSV_OFFICIAL_HORSE_NUMBER_NAME_CONFLICT:"+rid)
        expected = {str(r.get("runner_id")): r for r in request.get("runners") or []}
        if len(expected) != len(request.get("runners") or []) or set(expected) != set(active):
            reasons.append("CSV_REQUEST_ACTIVE_UNIVERSE_MISMATCH")
        elif any(_norm(expected[rid].get("name", "")) != _norm(active[rid]["name"]) for rid in active):
            reasons.append("CSV_REQUEST_ACTIVE_NAME_CONFLICT")
        parsed_rows = {}
        for rid, current in active.items():
            if rid not in csv_rows: continue
            row = csv_rows[rid]; fields = row["prestart_reference_fields"]
            jockey = fields["騎手名"]
            if not current.get("jockey"):
                reasons.append("CSV_CURRENT_OFFICIAL_JOCKEY_UNOBSERVED:"+rid)
            elif _norm(jockey) != _norm(current["jockey"]):
                matching = [e for e in events if str(e.get("horse_no")) == rid
                    and e.get("field") == "jockey" and _norm(e.get("from", "")) == _norm(jockey)
                    and _norm(e.get("to", "")) == _norm(current["jockey"])]
                if not matching:
                    reasons.append("CSV_JOCKEY_CONFLICT_WITHOUT_VERIFIED_CHANGE:"+rid)
                else:
                    reconciliation.append({"runner_id":rid,"field":"jockey","csv_value":jockey,
                        "official_current_value":current["jockey"],"official_change_raw_sha256":change_digest})
                    jockey = current["jockey"]
            parsed_rows[rid] = {"runner_id":rid,"horse_no":int(rid),"frame_no":_number(fields["枠番"],True),
                "name":row["horse_name"],"current_jockey":jockey,"current_load":_number(fields["負担重量"]),
                "age":_number(fields["齢"],True),"sex_age":fields["性"]+fields["齢"],
                "current_body_weight":_number(fields["馬体重"],True),
                "current_body_weight_change":_number(fields["馬体重増減"],True),
                "sire":fields["父馬名"],"dam":fields["母馬名"],"damsire":fields["母父馬名"],
                "trainer":fields["調教師"],"starts":[],"odds":None,"popularity":None,
                "horse_id":None,"sire_id":None,"damsire_id":None,"jockey_id":None,"stable_id":None,
                "race_card_source_id":"NAR-CSV-"+capture["raw_sha256"],
                "race_card_snapshot_sha256":parsed["sha256"],"race_card_fetched_at":capture["captured_at"],
                "csv_aggregate_reference_fields":{k:fields[k] for k in ("全成績","ダート左成績","ダート右成績","当競馬場成績","うち当距離成績")},
                "field_provenance":deepcopy(row["field_provenance"]),
                "current_jockey_provenance":({"raw_sha256":change_digest,"receipt_sha256":changes["receipt_sha256"]}
                    if jockey != fields["騎手名"] else deepcopy(row["field_provenance"]["騎手名"]))}
        if not reasons:
            card = {"source_id":"NAR-CSV-"+capture["raw_sha256"],"source_class":SOURCE_CLASS,
                "authority":"NAR_OFFICIAL","official":False,"format":"application/zip",
                "requested_url":capture["source_url"],"final_url":capture["source_url"],
                "fetched_at":capture["captured_at"],"http_status":200,"byte_count":len(raw),
                "raw_sha256":capture["raw_sha256"],"raw_encoding":"base64-original-zip",
                "raw_b64":base64.b64encode(raw).decode(),"parsed_csv_sha256":parsed["sha256"]}
            card["snapshot_sha256"] = sha(card)
            for row in parsed_rows.values():
                row["race_card_snapshot_sha256"] = card["snapshot_sha256"]
            candidate = {"schema":PROFILE,"classification":"UNADOPTED_CSV_SOURCE_CANDIDATE_NOT_ADMITTED",
                "race_id":request["race_id"],"source_race_context":deepcopy(parsed["race_identity"]),
                "official_race_id":changes["official_race_id"],"source_freeze_at":freeze_at,
                "prediction_cutoff":request["prediction_cutoff"],"scheduled_post_at":request["scheduled_post_at"],
                "sources":[card],"source_snapshot_sha256":card["snapshot_sha256"],
                "declared_runner_universe":{"runners":[{"runner_id":rid,"horse_no":int(rid),"name":r["name"],"status":r["status"]} for rid,r in official.items()]},
                "active_runner_universe":{"runners":[{"runner_id":rid,"horse_no":int(rid),"name":r["name"]} for rid,r in active.items()]},
                "parsed_runner_evidence":parsed_rows,"normalized_evidence":{
                    "track_condition":{"value":parsed["race_reference_fields"]["馬場"] or None,
                        "source_id":card["source_id"],"snapshot_sha256":card["snapshot_sha256"],
                        "fetched_at":capture["captured_at"],"provenance":deepcopy(parsed["race_field_provenance"]["馬場"])},
                    "weather":{"value":parsed["race_reference_fields"]["天候"] or None,
                        "source_id":card["source_id"],"snapshot_sha256":card["snapshot_sha256"],
                        "fetched_at":capture["captured_at"],"provenance":deepcopy(parsed["race_field_provenance"]["天候"])}},
                "official_change_evidence":{"raw_sha256":change_digest,"raw_b64":base64.b64encode(changes_raw).decode(),
                    "byte_count":len(changes_raw),"receipt_sha256":changes["receipt_sha256"],
                    "observed_at":changes["observed_at"],"source_updated_at":changes["source_updated_at"]},
                "permission_evidence":{"permission_ref":rights["permission_ref"],"permission_sha256":rights["permission_sha256"],
                    "actor_id":actor_id,"effective_from":rights["effective_from"],"effective_until":rights["effective_until"]},
                "formal_source_admitted":False,"production_numeric_consumers_authorized":False,
                "permanent_ids_inferred":False,"dated_individual_history_available":False,"csv_publisher_updated_at":None,
                "csv_publisher_updated_at_status":"NOT_PROVIDED_NOT_INFERRED_FROM_FETCH"}
            candidate["official_runner_universe_sha256"] = sha(candidate["active_runner_universe"])
            candidate["declared_runner_universe"]["runner_universe_sha256"] = sha(candidate["declared_runner_universe"]["runners"])
            candidate["active_runner_universe"]["runner_universe_sha256"] = candidate["official_runner_universe_sha256"]
            candidate["sha256"] = sha(candidate)
    signature = _decision(source_receipt_verifier, receipt=source_receipt,
        source_candidate=deepcopy(candidate), request=request) if candidate is not None and source_receipt is not None else {}
    signature_ok = (candidate is not None and signature.get("passed") is True
        and signature.get("source_candidate_sha256") == candidate["sha256"]
        and signature.get("raw_sha256") == capture["raw_sha256"]
        and signature.get("profile_id") == PROFILE and signature.get("signature_verified") is True
        and bool(SHA.fullmatch(str(signature.get("receipt_sha256", "")))))
    terminals = list(dict.fromkeys(reasons))
    if not signature_ok: terminals.append("CSV_SOURCE_EXTERNAL_SIGNATURE_UNVERIFIED")
    terminals.append("CSV_FORMAL_PROFILE_NOT_ADOPTED_R13_R20_HTML_GATES_UNCHANGED")
    result = {"profile":PROFILE,"request_sha256":sha(request),"status":("CSV_SOURCE_CANDIDATE_READY_REQUIRES_ADOPTION" if candidate else "CSV_SOURCE_CANDIDATE_HOLD"),
        "parsed_reference":parsed,"source_candidate":candidate,"qualification_verified_by_external_gate":bool(rights_ok),
        "official_changes_verified_by_external_gate":bool(changes_ok),"external_signature_verified_by_supplied_gate":bool(signature_ok),
        "ready_for_private_research_parsed_numeric":candidate is not None,"formal_source_admitted":False,
        "r13_r20_existing_admission_passed":False,"new_OOS":0,"terminals":terminals,
        "reconciled_official_changes":reconciliation,"new_numeric_policy":False}
    result["sha256"] = sha(result)
    return result


@dataclass(frozen=True)
class CsvConsumerBinding:
    """Private fixed configuration; JSON input cannot supply these callables.

    The Profile file remains disabled until an exact Owner-approved adoption.
    Its document verifier and SOURCE verifier must be the existing trusted
    authority/signature gates, not a parser or a purpose declaration.
    """
    profile_sha256: str
    adapter_code_sha256: str
    scope: str
    profile_approval_verifier: object
    source_receipt_verifier: object
    actor_id: str = ""


def _bound_request(assessment, request):
    if (assessment.get("profile") != PROFILE
            or assessment.get("sha256") != sha({k:v for k,v in assessment.items() if k!="sha256"})
            or assessment.get("request_sha256") != sha(request)):
        raise CsvAdmissionHold("CSV_ASSESSED_REQUEST_OR_HASH_MISMATCH")


def compile_research_numeric(assessment, request, *, repo_root=None):
    """Consume CSV facts through existing 63/29 arithmetic, research only.

    This does not call or bypass R13 admission and does not make the candidate
    a signed SOURCE. Missing histories and IDs remain missing. Current CSV
    aggregates are retained as references, never fabricated individual starts.
    """
    _bound_request(assessment,request)
    if assessment.get("ready_for_private_research_parsed_numeric") is not True:
        raise CsvAdmissionHold("CSV_RESEARCH_NUMERICAL_VALIDATED_CANDIDATE_REQUIRED")
    source = assessment.get("source_candidate") or {}
    if (source.get("sha256") != sha({k:v for k,v in source.items() if k!="sha256"})
            or source.get("race_id") != request.get("race_id")
            or source.get("formal_source_admitted") is not False
            or source.get("production_numeric_consumers_authorized") is not False):
        raise CsvAdmissionHold("CSV_RESEARCH_CANDIDATE_HASH_ID_OR_SCOPE_INVALID")
    # Existing engine modules use their established import convention.
    import sys
    root = Path(repo_root or Path(__file__).resolve().parents[1]).resolve()
    if str(root/"runtime") not in sys.path: sys.path.insert(0,str(root/"runtime"))
    from runtime.local_nar_evidence_candidate import compile_parsed_candidate_evidence
    from runtime.local_fullnumerical_candidate import materialize_candidate
    registry = root/"mapping/local_evidence_feature_rule_registry_v0.1_candidate_20260923.json"
    mapping = root/"mapping/local_full_numerical_mapping_v0.1_candidate_20260923.json"
    intent = deepcopy(request)
    if not (intent.get("race") or {}).get("class"):
        intent.setdefault("race", {})["class"] = assessment["parsed_reference"]["race_reference_fields"]["条件"]
    compiled = compile_parsed_candidate_evidence(source, intent,
                        source["parsed_runner_evidence"], registry)
    numeric = materialize_candidate(compiled, registry, mapping)
    numeric["csv_research_consumer"] = {"profile":PROFILE,
        "classification":"PRIVATE_CSV_RESEARCH_NOT_FORMAL_NOT_REGISTERED_OOS",
        "actual_generated_at":datetime.now(timezone.utc).isoformat(),"prestart_prediction_claim":False,
        "source_candidate_sha256":source["sha256"],"assessment_sha256":assessment["sha256"],
        "zip_raw_sha256":source["sources"][0]["raw_sha256"],
        "official_change_raw_sha256":source["official_change_evidence"]["raw_sha256"],
        "formal_source_admitted":False,"r13_r20_admission_bypassed":False,
        "production_numeric_consumers_authorized":False,"registered_OOS_increment":0}
    return numeric


def consume_with_approved_profile(assessment, request, *, binding, source_receipt,
                                  repo_root=None, now=None):
    """Dormant signed-Profile hook for the private entry, disabled by default.

    Approval changes the exact Profile and private binding, not SOURCE/Owner
    authority by inference. Even an approved hook uses existing candidate
    arithmetic and never enables Production numerical Consumers or R13/R20.
    """
    _bound_request(assessment,request)
    root = Path(repo_root or Path(__file__).resolve().parents[1]).resolve()
    path = root/"profiles/local_fnb_nar_csv_source_candidate_v0.1_20261103.json"
    raw = path.read_bytes(); profile = json.loads(raw)
    if (profile.get("profile_id") != PROFILE or profile.get("enabled") is not True
            or profile.get("status") != "APPROVED_PRIVATE_NONPRODUCTION_CSV_PROFILE"):
        raise CsvAdmissionHold("CSV_PROFILE_NOT_ADOPTED")
    verified_now = _dt(now or datetime.now(timezone.utc))
    if verified_now >= _dt(request["prediction_cutoff"]):
        raise CsvAdmissionHold("CSV_PRIVATE_PRESTART_CUTOFF_EXPIRED")
    if (not isinstance(binding,CsvConsumerBinding)
            or binding.profile_sha256 != hashlib.sha256(raw).hexdigest()
            or binding.adapter_code_sha256 != hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
            or binding.scope != "SINGLE_RACE_PRESTART_NONPRODUCTION_NOT_REGISTERED_OOS"):
        raise CsvAdmissionHold("CSV_PRIVATE_CONSUMER_BINDING_MISMATCH")
    adoption = _decision(binding.profile_approval_verifier, profile=profile,
        profile_sha256=binding.profile_sha256,scope=binding.scope,request=request)
    source = assessment.get("source_candidate") or {}
    rights = source.get("permission_evidence") or {}
    if (binding.actor_id != rights.get("actor_id") or not binding.actor_id
            or not _dt(rights["effective_from"]) <= verified_now < _dt(rights["effective_until"])):
        raise CsvAdmissionHold("CSV_PROVIDER_QUALIFICATION_EXPIRED_OR_ACTOR_MISMATCH")
    if (adoption.get("passed") is not True or adoption.get("profile_sha256") != binding.profile_sha256
            or adoption.get("scope") != binding.scope or not adoption.get("approval_ref")
            or not SHA.fullmatch(str(adoption.get("approval_sha256", "")))):
        raise CsvAdmissionHold("CSV_PROFILE_APPROVAL_GATE_UNVERIFIED")
    try:
        approval_current = _dt(adoption["effective_from"]) <= verified_now < _dt(adoption["effective_until"])
    except (KeyError,ValueError,TypeError):
        approval_current = False
    if not approval_current: raise CsvAdmissionHold("CSV_PROFILE_APPROVAL_NOT_EFFECTIVE_NOW")
    signature = _decision(binding.source_receipt_verifier, receipt=source_receipt,
        source_candidate=source,request=request,profile=profile)
    if (signature.get("passed") is not True or signature.get("signature_verified") is not True
            or signature.get("source_candidate_sha256") != source.get("sha256")
            or signature.get("profile_id") != PROFILE or signature.get("scope") != binding.scope
            or signature.get("race_id") != request.get("race_id")
            or signature.get("cutoff_at") != request.get("prediction_cutoff")
            or signature.get("freeze_at") != source.get("source_freeze_at")
            or not SHA.fullmatch(str(signature.get("receipt_sha256", "")))):
        raise CsvAdmissionHold("CSV_EXISTING_SOURCE_SIGNATURE_GATE_UNVERIFIED")
    return {"source_candidate":deepcopy(source),"request":deepcopy(request),
        "numerical":compile_research_numeric(assessment,request,repo_root=root),
        "csv_private_profile_admission":{"status":"APPROVED_CSV_PRIVATE_RESEARCH_CONSUMED",
            "scope":binding.scope,"approval_ref":adoption["approval_ref"],
            "approval_sha256":adoption["approval_sha256"],"source_receipt_sha256":signature["receipt_sha256"],
            "profile_sha256":binding.profile_sha256,"adapter_code_sha256":binding.adapter_code_sha256,
            "formal_R13_R20_admission":False,"production_numeric_consumers_authorized":False,
            "owner_scope_granted":False,"registered_OOS_increment":0}}

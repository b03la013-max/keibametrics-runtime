"""Responses API prediction owner, SHADOW only; no Production authorization.

Credentials are supplied exclusively by the calling runtime's environment.
The existing Production prompt/canon must be supplied as digest-pinned files.
This adapter never substitutes Candidate indices, market order or KRS order.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import urllib.request


class CandidateHold(ValueError):
    pass


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest()


def timestamp(value):
    parsed = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise CandidateHold("TIMEZONE_REQUIRED")
    return parsed


def pinned_text(root, spec):
    path = (root / spec["path"]).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise CandidateHold("PINNED_INPUT_PATH_INVALID")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != spec["sha256"]:
        raise CandidateHold("PINNED_INPUT_DIGEST_MISMATCH")
    return raw.decode("utf-8")


def ensure_clean(value):
    """No outcome state, substitute ranks or credentials in API input/artifacts."""
    forbidden = {"official_result", "finish_order", "payouts", "settlement",
                 "api_key", "openai_api_key", "authorization", "candidate_indices",
                 "krs_ranking", "popularity_ranking", "odds_ranking"}
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in forbidden:
                raise CandidateHold("FORBIDDEN_INPUT_OR_OUTPUT_FIELD")
            ensure_clean(child)
    elif isinstance(value, list):
        for child in value:
            ensure_clean(child)
    elif isinstance(value, str):
        secret = os.environ.get("OPENAI_API_KEY")
        if re.search(r"sk-[A-Za-z0-9_-]{16,}", value) or (secret and secret in value):
            raise CandidateHold("SECRET_IN_INPUT_OR_OUTPUT")


def obj(properties):
    return {"type": "object", "properties": properties,
            "required": list(properties), "additionalProperties": False}


def arr(items):
    return {"type": "array", "items": items}


def prediction_schema(ids):
    runner = {"type": "string", "enum": ids}
    text = {"type": "string"}
    return obj({
        "ranking": arr(runner),
        "roles": arr(obj({"runner_id": runner,
                          "columns": arr({"type": "string", "enum": ["W", "P2", "P3"]})})),
        "role_registry": arr(obj({"runner_id": runner,
                                  "column": {"type": "string", "enum": ["W", "P2", "P3"]},
                                  "status": text})),
        "pair_dispositions": arr(obj({"head": runner, "second": runner,
                                      "status": text, "reason": text})),
        "third_dispositions": arr(obj({"head": runner, "second": runner, "third": runner,
                                       "status": text, "reason": text})),
        "uncertainty": obj({"level": text, "reasons": arr(text)}),
        # These are disclosure fields, not new ranking rules. Unsupported
        # Production concepts must remain UNKNOWN/unresolved in SHADOW.
        "alternative_winner": {"type": "string", "enum": ids + ["UNKNOWN"]},
        "partial_order": arr(arr(runner)),
        "ties": arr(arr(runner)),
        "unresolved": arr(text),
        "evidence_conflict": text,
        "market_conflict": text,
        "venue_prediction_context": obj({"interpretation": text, "evidence_refs": arr(text)}),
    })


def validate_schema(value, schema):
    kind = schema["type"]
    if kind == "object":
        if not isinstance(value, dict) or set(value) != set(schema["properties"]):
            raise CandidateHold("OUTPUT_SCHEMA_INVALID")
        for key, item in value.items():
            validate_schema(item, schema["properties"][key])
    elif kind == "array":
        if not isinstance(value, list):
            raise CandidateHold("OUTPUT_SCHEMA_INVALID")
        for item in value:
            validate_schema(item, schema["items"])
    elif kind == "string":
        if not isinstance(value, str) or ("enum" in schema and value not in schema["enum"]):
            raise CandidateHold("OUTPUT_SCHEMA_INVALID")
    else:
        raise CandidateHold("UNSUPPORTED_SCHEMA_TYPE")


def responses_call(payload, *, timeout):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise CandidateHold("SERVICE_ACCOUNT_RUNTIME_SECRET_MISSING")
    req = urllib.request.Request("https://api.openai.com/v1/responses",
                                 data=json.dumps(payload).encode(),
                                 headers={"Authorization": "Bearer " + key,
                                          "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.load(response)
    except Exception:
        # Never retain provider error bodies/headers or credentials in diagnostics.
        raise CandidateHold("OPENAI_API_TRANSPORT_OR_PROVIDER_HOLD") from None


def execute(context, config, *, root, call=responses_call, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    if config.get("mode") != "SHADOW" or config.get("production_authorized") is not False:
        raise CandidateHold("CANDIDATE_PROMOTION_FORBIDDEN")
    if config.get("credential_owner_type") != "service_account" or not config.get("project_id"):
        raise CandidateHold("SERVICE_ACCOUNT_PROJECT_METADATA_REQUIRED")
    # Metadata is not evidence of credential ownership. Provisioning must verify
    # this externally before enabling live API calls.
    if call is responses_call and config.get("credential_attestation_verified") is not True:
        raise CandidateHold("SERVICE_ACCOUNT_ATTESTATION_REQUIRED")
    envelope = context["signed_source"]
    artifact = envelope["artifact"]
    receipt = envelope["receipt"]
    if context["source_verification"].get("verified") is not True or artifact.get("formal_ready") is not True:
        raise CandidateHold("SOURCE_NOT_VERIFIED_OR_PARTIAL")
    if receipt.get("race_id") != context["race_id"] or receipt.get("phase") != "SOURCE":
        raise CandidateHold("SOURCE_RACE_LINEAGE_MISMATCH")
    cutoff = timestamp(context["prediction_cutoff"])
    deadline = timestamp(context["release_deadline_at"])
    if timestamp(artifact["source_freeze_at"]) > cutoff or now >= deadline:
        raise CandidateHold("DEADLINE_OR_POST_CUTOFF_SOURCE_HOLD")
    if artifact.get("post_cutoff_sources"):
        raise CandidateHold("POST_CUTOFF_SOURCE_HOLD")
    universe = artifact["active_runner_universe"]
    ids = [str(row["runner_id"]) for row in universe["runners"]]
    if not ids or len(set(ids)) != len(ids) or len(ids) != universe["runner_count"]:
        raise CandidateHold("RUNNER_UNIVERSE_INVALID")
    instruction = pinned_text(root, config["instruction"])
    canon = pinned_text(root, config["venue_canon"])
    policy = pinned_text(root, config["policy"])
    if not all(isinstance(config.get(key), str) and config[key].strip()
               for key in ("prompt_id", "prompt_version", "venue_canon_id", "policy_id")):
        raise CandidateHold("VERSIONED_PROMPT_POLICY_METADATA_REQUIRED")
    # Never send the baseline Prediction, intent-derived scores, KRS or RESULT.
    data = {"race_id": context["race_id"], "signed_source": envelope,
            "current_authority": context["current_authority"], "venue_canon": canon,
            "policy": policy, "runner_universe": universe,
            "numerical_authority": context["production_numerical_authority"],
            "current_state_evidence": artifact.get("normalized_evidence", {}),
            "missingness": {"required_sources": artifact.get("missing_required_sources", []),
                            "stale_sources": artifact.get("stale_sources", []),
                            "conflicts": artifact.get("conflicts", []),
                            "policy": "UNKNOWN_NO_PROXY"},
            "prediction_cutoff": context["prediction_cutoff"]}
    ensure_clean(data)
    ensure_clean(instruction)
    schema = prediction_schema(ids)
    input_schema = obj({key: {"type": "object"} if isinstance(value, dict) else {"type": "string"}
                        for key, value in data.items()})
    model = config.get("model_identifier")
    if not isinstance(model, str) or not model:
        raise CandidateHold("PINNED_MODEL_REQUIRED")
    payload = {"model": model, "instructions": instruction,
               "input": json.dumps(data, ensure_ascii=False), "store": False,
               "max_output_tokens": int(config.get("max_output_tokens", 8000)),
               "text": {"format": {"type": "json_schema", "name": "km_static_prediction",
                                    "strict": True, "schema": schema}}}
    remaining = (deadline - now).total_seconds()
    reserve = max(120, int(config.get("production_reserve_seconds", 120)))
    if remaining <= reserve:
        raise CandidateHold("SHADOW_DEFERRED_TO_PROTECT_PRODUCTION_DEADLINE")
    result = call(payload, timeout=min(int(config.get("timeout_seconds", 90)), remaining - reserve))
    ensure_clean(result)
    if result.get("status") != "completed" or result.get("model") != model or not result.get("id"):
        raise CandidateHold("INCOMPLETE_OR_MODEL_MISMATCH")
    blocks = [part for item in result.get("output", []) for part in item.get("content", [])]
    if any(part.get("type") == "refusal" for part in blocks):
        raise CandidateHold("MODEL_REFUSAL")
    texts = [part["text"] for part in blocks if part.get("type") == "output_text"]
    if len(texts) != 1:
        raise CandidateHold("OUTPUT_TEXT_CARDINALITY_INVALID")
    try:
        prediction = json.loads(texts[0])
    except (ValueError, TypeError):
        raise CandidateHold("OUTPUT_JSON_INVALID") from None
    ensure_clean(prediction)
    validate_schema(prediction, schema)
    if len(prediction["ranking"]) != len(ids) or set(prediction["ranking"]) != set(ids):
        raise CandidateHold("RANKING_UNIVERSE_INVALID")
    role_ids = [row["runner_id"] for row in prediction["roles"]]
    if len(role_ids) != len(ids) or set(role_ids) != set(ids):
        raise CandidateHold("ROLES_UNIVERSE_INVALID")
    assigned = {(row["runner_id"], column) for row in prediction["roles"] for column in row["columns"]}
    registered = {(row["runner_id"], row["column"]) for row in prediction["role_registry"]}
    if assigned != registered or len(registered) != len(prediction["role_registry"]):
        raise CandidateHold("ROLE_REGISTRY_INCONSISTENT")
    for key in ("pair_dispositions", "third_dispositions"):
        fields = ["head", "second"] + (["third"] if key == "third_dispositions" else [])
        selections = [tuple(row[f] for f in fields) for row in prediction[key]]
        if len(set(selections)) != len(selections) or any(len(set(s)) != len(s) for s in selections):
            raise CandidateHold("DUPLICATE_OR_SELF_SELECTION")
    for key in ("ties", "partial_order"):
        if any(len(group) < 2 or len(group) != len(set(group)) for group in prediction[key]):
            raise CandidateHold("INVALID_PARTIAL_ORDER_OR_TIE_GROUP")
    frozen = dt.datetime.now(dt.timezone.utc) if now is None else now
    # Check wall clock after an actual call; test-injected clocks are deterministic.
    if call is responses_call:
        frozen = dt.datetime.now(dt.timezone.utc)
    if frozen >= deadline:
        raise CandidateHold("DEADLINE_HOLD_AFTER_RESPONSE")
    lineage = {"execution_id": context["execution_id"], "race_id": context["race_id"],
               "source_binding": context["source_binding"], "source_sha256": digest(envelope),
               "venue_canon_sha256": config["venue_canon"]["sha256"],
               "venue_canon_id": config["venue_canon_id"],
               "policy_id": config["policy_id"], "policy_sha256": config["policy"]["sha256"],
               "prompt_id": config["prompt_id"], "prompt_version": config["prompt_version"],
               "authority_id": context["current_authority"]["manifest_id"],
               "input_schema_sha256": digest(input_schema), "output_schema_sha256": digest(schema),
               "current_authority_sha256": digest(context["current_authority"]),
               "instruction_sha256": config["instruction"]["sha256"], "schema_sha256": digest(schema),
               "model_identifier": model, "api_response_identifier": result["id"],
               "prediction_output_sha256": digest(prediction), "freeze_timestamp": frozen.isoformat(),
               "input_sha256": digest(data), "candidate_config_sha256": digest(config)}
    static = {"ranking": prediction["ranking"],
              "roles": {row["runner_id"]: row["columns"] for row in prediction["roles"] if row["columns"]},
              "uncertainty": prediction["uncertainty"], "venue_state": prediction["venue_prediction_context"],
              "status": "FROZEN / SHADOW / API-OWNER-CANDIDATE / NOT-PRODUCTION",
              "frozen_at": frozen.isoformat()}
    semantics = {"static_prediction": static,
                 **{key: prediction[key] for key in ("role_registry", "pair_dispositions",
                                                     "third_dispositions", "venue_prediction_context")},
                 "final_prediction_package": {key: static[key] for key in (
                     "ranking", "roles", "uncertainty", "venue_state")}}
    lineage["prediction_semantics_sha256"] = digest(semantics)
    return {"status": "SHADOW_FROZEN", "production_effect": "NONE",
            "production_authorized": False, "promotion": "HOLD",
            "prediction": prediction, "prediction_semantics": semantics, "lineage": lineage}


def compare(candidate, baseline, baseline_source_binding):
    if candidate["lineage"]["source_binding"] != baseline_source_binding:
        raise CandidateHold("COMPARISON_SOURCE_BASIS_MISMATCH")
    prediction = candidate["prediction"]
    static = baseline.get("static_prediction") or {}
    roles = {row["runner_id"]: row["columns"] for row in prediction["roles"] if row["columns"]}
    checks = {"ranking": prediction["ranking"] == static.get("ranking"),
              "roles": roles == static.get("roles"),
              "role_registry": prediction["role_registry"] == baseline.get("role_registry"),
              "pair_dispositions": prediction["pair_dispositions"] == baseline.get("pair_dispositions"),
              "third_dispositions": prediction["third_dispositions"] == baseline.get("third_dispositions"),
              "uncertainty": prediction["uncertainty"] == static.get("uncertainty"),
              "venue_prediction_context": prediction["venue_prediction_context"] == baseline.get("venue_prediction_context")}
    return {"status": "STRUCTURAL_MATCH" if all(checks.values()) else "SEMANTIC_DIFFERENCE",
            "checks": checks, "baseline_sha256": digest(baseline),
            "difference_classification": "UNRESOLVED_REQUIRES_PROVENANCE_REVIEW" if not all(checks.values()) else "NONE",
            "unverified_concepts": ["alternative_winner", "partial_order", "ties", "unresolved",
                                    "evidence_conflict", "market_conflict"],
            "candidate_sha256": digest(candidate), "production_equivalence": "UNPROVEN",
            "promotion": "HOLD", "production_effect": "NONE"}

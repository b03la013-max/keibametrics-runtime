"""Responses API prediction owner, SHADOW only; no Production authorization.

Credentials are supplied exclusively by the calling runtime's environment.
The NEW C2 Candidate prompt/canon are supplied as digest-pinned files.
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
import urllib.error

INPUT_CONTRACT_VERSION = "KM-OPENAI-OWNER-PRE-RACE-INPUT-v3-C2"
CANDIDATE_ID = "KM-LOCAL-OPENAI-PREDICTION-OWNER-CANDIDATE-v1"


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


def prediction_authority_input(authority, cutoff):
    """Expose normative pre-race authority, never acceptance/research ledgers.

    The full immutable manifest remains digest-bound in lineage. Its operational
    and measurement snapshots are not Prediction evidence. Historical comparison
    must supply the authority effective at that historical prediction cutoff.
    """
    effective = authority.get("effective_at")
    if not effective:
        raise CandidateHold("AUTHORITY_EFFECTIVE_AT_REQUIRED")
    if timestamp(effective) > cutoff:
        raise CandidateHold("POST_CUTOFF_AUTHORITY_HOLD")
    common = authority.get("common_family_components", {})
    local = authority.get("family_scoped_authority", {}).get("LOCAL", {})
    common_keys = ("prediction_utility_contract", "scope_ownership_contract",
                   "formal_lifecycle_contract", "fnb_venue_canon")
    local_keys = ("production_suite", "production_numeric_status", "common_canon",
                  "common_canon_profile", "common_canon_compiled_sha256",
                  "information_source_registry", "base_index_registry",
                  "evidence_rule_registry", "numerical_authority_status",
                  "current_venue_canons", "production_prediction_owner")
    return {"manifest_id": authority["manifest_id"], "effective_at": effective,
            "common_family_components": {k: common[k] for k in common_keys if k in common},
            "family_scoped_authority": {"LOCAL": {k: local[k] for k in local_keys if k in local}}}


def prediction_source_input(envelope):
    """Preserve signed SOURCE references and factual inputs, exclude shadow state."""
    artifact = envelope["artifact"]
    # Validate before projection so an injected target outcome cannot be silently
    # discarded and the corrupt source treated as clean.
    ensure_clean(envelope)
    keys = ("race_id", "formal_ready", "source_freeze_at", "prediction_cutoff",
            "source_snapshot_sha256", "raw_source_bundle_sha256",
            "active_runner_universe", "source_race_context", "normalized_evidence",
            "normalized_evidence_sha256", "auxiliary_evidence", "auxiliary_evidence_sha256",
            "jma_weather_evidence", "jma_weather_evidence_sha256",
            "point_in_time_population_ledger", "point_in_time_population_ledger_sha256",
            "sources", "missing_required_sources", "stale_sources", "conflicts")
    return {"receipt": envelope["receipt"], "signed_envelope_sha256": digest(envelope),
            "source_receipt_sha256": envelope.get("receipt_sha256"),
            "source_snapshot_sha256": artifact.get("source_snapshot_sha256"),
            "artifact_projection": {k: artifact[k] for k in keys if k in artifact},
            "projection_is_signed_artifact": False}


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


def responses_call(payload, *, timeout, project_id=None):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise CandidateHold("SERVICE_ACCOUNT_RUNTIME_SECRET_MISSING")
    headers = {"Authorization": "Bearer " + key, "Content-Type": "application/json"}
    if project_id:
        headers["OpenAI-Project"] = project_id
    req = urllib.request.Request("https://api.openai.com/v1/responses",
                                 data=json.dumps(payload).encode(),
                                 headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        # HTTP status is non-secret; provider bodies, headers and error messages
        # are not preserved. Distinguish request/account/rate failures from
        # transport failures without exposing credentials or changing policy.
        if exc.code in (401, 403):
            code = "OPENAI_API_AUTHENTICATION_HOLD"
        elif exc.code in (400, 404, 408, 409, 422, 429):
            code = f"OPENAI_API_HTTP_{exc.code}_HOLD"
        elif 500 <= exc.code < 600:
            code = "OPENAI_API_HTTP_5XX_HOLD"
        else:
            code = "OPENAI_API_HTTP_UNCLASSIFIED_HOLD"
        raise CandidateHold(code) from None
    except (TimeoutError,):
        raise CandidateHold("OPENAI_API_TIMEOUT_HOLD") from None
    except urllib.error.URLError:
        raise CandidateHold("OPENAI_API_NETWORK_HOLD") from None
    except (ValueError, UnicodeDecodeError):
        raise CandidateHold("OPENAI_API_RESPONSE_DECODE_HOLD") from None
    except Exception:
        # Never retain provider response bodies/headers or credentials.
        raise CandidateHold("OPENAI_API_CLIENT_RUNTIME_HOLD") from None


def execute(context, config, *, root, call=responses_call, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    ensure_clean(config)
    if config.get("mode") != "SHADOW" or config.get("production_authorized") is not False:
        raise CandidateHold("CANDIDATE_PROMOTION_FORBIDDEN")
    if call is responses_call and not os.environ.get("OPENAI_API_KEY"):
        raise CandidateHold("SERVICE_ACCOUNT_RUNTIME_SECRET_MISSING")
    if config.get("credential_owner_type") != "service_account" or not config.get("project_id"):
        raise CandidateHold("SERVICE_ACCOUNT_PROJECT_METADATA_REQUIRED")
    # Metadata is not evidence of credential ownership. Provisioning must verify
    # this externally before enabling live API calls.
    if call is responses_call and config.get("credential_attestation_verified") is not True:
        raise CandidateHold("SERVICE_ACCOUNT_ATTESTATION_REQUIRED")
    if call is responses_call:
        if (config.get("credential_environment") != "keibametrics-staging"
                or os.environ.get("KM_CREDENTIAL_ENVIRONMENT") != "keibametrics-staging"
                or os.environ.get("GITHUB_ACTIONS") != "true"):
            raise CandidateHold("STAGING_ENVIRONMENT_REQUIRED")
        if not config.get("service_account_id"):
            raise CandidateHold("SERVICE_ACCOUNT_ID_REQUIRED")
    envelope = context["signed_source"]
    artifact = envelope["artifact"]
    receipt = envelope["receipt"]
    if context["source_verification"].get("verified") is not True or artifact.get("formal_ready") is not True:
        raise CandidateHold("SOURCE_NOT_VERIFIED_OR_PARTIAL")
    if receipt.get("race_id") != context["race_id"] or receipt.get("phase") != "SOURCE":
        raise CandidateHold("SOURCE_RACE_LINEAGE_MISMATCH")
    cutoff = timestamp(context["prediction_cutoff"])
    authority_input = prediction_authority_input(context["current_authority"], cutoff)
    deadline = timestamp(context["release_deadline_at"])
    historical = context.get("execution_class") == "HISTORICAL_BEHAVIORAL_COMPARISON"
    if timestamp(artifact["source_freeze_at"]) > cutoff or (not historical and now >= deadline):
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
    if config.get("owner_entrypoint"):
        pinned_text(root, config["owner_entrypoint"])
    normative_sources = {spec["path"]: pinned_text(root, spec)
                         for spec in config.get("normative_sources", [])}
    if not all(isinstance(config.get(key), str) and config[key].strip()
               for key in ("prompt_id", "prompt_version", "venue_canon_id", "policy_id")):
        raise CandidateHold("VERSIONED_PROMPT_POLICY_METADATA_REQUIRED")
    # Never send the baseline Prediction, intent-derived scores, KRS or RESULT.
    source_input = prediction_source_input(envelope)
    data = {"race_id": context["race_id"], "signed_source": source_input,
            "current_authority": authority_input, "venue_canon": canon,
            "policy": policy, "normative_sources": normative_sources, "runner_universe": universe,
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
    reserve = max(120, int(config.get("production_reserve_seconds", 120)))
    remaining = (reserve + int(config.get("timeout_seconds", 90))
                 if historical else (deadline - now).total_seconds())
    if remaining <= reserve:
        raise CandidateHold("SHADOW_DEFERRED_TO_PROTECT_PRODUCTION_DEADLINE")
    timeout = min(int(config.get("timeout_seconds", 90)), remaining - reserve)
    authentication_response_id = None
    if call is responses_call:
        # Authenticate the exact project/model before sending race evidence.
        # No models.read scope, alternate model or factual input is required.
        probe = responses_call({"model": model, "store": False, "max_output_tokens": 32,
                                "input": "Return OK for credential authentication only."},
                               timeout=min(15, timeout), project_id=config["project_id"])
        ensure_clean(probe)
        if probe.get("status") != "completed" or probe.get("model") != model or not probe.get("id"):
            raise CandidateHold("API_AUTHENTICATION_PREFLIGHT_HOLD")
        authentication_response_id = probe["id"]
        if not historical:
            available = (deadline - dt.datetime.now(dt.timezone.utc)).total_seconds() - reserve
            if available <= 0:
                raise CandidateHold("SHADOW_DEFERRED_TO_PROTECT_PRODUCTION_DEADLINE")
            timeout = min(timeout, available)
    result = (responses_call(payload, timeout=timeout, project_id=config["project_id"])
              if call is responses_call else call(payload, timeout=timeout))
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
    if not historical and frozen >= deadline:
        raise CandidateHold("DEADLINE_HOLD_AFTER_RESPONSE")
    lineage = {"execution_id": context["execution_id"], "race_id": context["race_id"],
               "candidate_id": config.get("candidate_id", CANDIDATE_ID),
               "owner_entrypoint_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
               "execution_class": "HISTORICAL_BEHAVIORAL_COMPARISON" if historical else "PRE_RACE_SHADOW",
               "prediction_cutoff": context["prediction_cutoff"],
               "release_deadline_at": context["release_deadline_at"],
               "historical_oos_eligible": False,
               "change_class": "C2 DECISION POLICY FORMALIZATION",
               "normative_source_digests": config.get("normative_sources", []),
               "credential_attestation": {
                   "expected_project_id": config["project_id"],
                   "owner_type": config["credential_owner_type"],
                   "service_account_id": config.get("service_account_id"),
                   "expected_environment": config.get("credential_environment"),
                   "secret_presence": True if call is responses_call else "NOT_TESTED",
                   "api_authentication": "SUCCESS" if call is responses_call else "NOT_TESTED",
                   "api_authentication_response_identifier": authentication_response_id,
                   "identity_attestation": "EXTERNAL_PROVISIONING_ATTESTATION" if call is responses_call else "NOT_TESTED"},
               "input_contract_version": INPUT_CONTRACT_VERSION,
               "source_binding": context["source_binding"], "source_sha256": digest(envelope),
               "venue_canon_sha256": config["venue_canon"]["sha256"],
               "venue_canon_id": config["venue_canon_id"],
               "policy_id": config["policy_id"], "policy_sha256": config["policy"]["sha256"],
               "prompt_id": config["prompt_id"], "prompt_version": config["prompt_version"],
               "authority_id": context["current_authority"]["manifest_id"],
               "input_schema_sha256": digest(input_schema), "output_schema_sha256": digest(schema),
               "current_authority_sha256": digest(context["current_authority"]),
               "prediction_authority_input_sha256": digest(authority_input),
               "prediction_source_input_sha256": digest(source_input),
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
    return {"status": "HISTORICAL_COMPARISON_FROZEN" if historical else "SHADOW_FROZEN", "production_effect": "NONE",
            "production_authorized": False, "automatic_promotion": False, "promotion": "HOLD",
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
    def metric(left, right):
        unknown = left is None or right is None or left == "UNKNOWN" or right == "UNKNOWN"
        return {"status": "UNKNOWN" if unknown else ("MATCH" if left == right else "DIFFERENCE")}
    metrics = {key: metric(prediction.get(key), baseline.get(key, static.get(key)))
               for key in ("alternative_winner", "unresolved", "uncertainty")}
    metrics["ranking"] = metric(prediction["ranking"], static.get("ranking"))
    if static.get("ranking") and set(static["ranking"]) == set(prediction["ranking"]):
        metrics["ranking"]["position_agreement"] = sum(
            a == b for a, b in zip(prediction["ranking"], static["ranking"])) / len(prediction["ranking"])
    for column in ("W", "P2", "P3"):
        left = sorted(k for k, v in roles.items() if column in v)
        baseline_roles = static.get("roles")
        right = sorted(str(k) for k, v in baseline_roles.items() if column in v) if isinstance(baseline_roles, dict) else None
        metrics[column] = metric(left, right)
        if right is not None:
            metrics[column]["intersection"] = len(set(left) & set(right))
            metrics[column]["union"] = len(set(left) | set(right))
    for key, name in (("pair_dispositions", "Pair"), ("third_dispositions", "Third"),
                      ("venue_prediction_context", "venue_interpretation")):
        metrics[name] = metric(prediction.get(key), baseline.get(key))
    statuses = [m["status"] for m in metrics.values()]
    status = "DIFFERENCE" if "DIFFERENCE" in statuses else ("UNKNOWN" if "UNKNOWN" in statuses else "MATCH")
    return {"status": status, "comparison_class": "HISTORICAL_BEHAVIORAL_COMPARISON",
            "metrics": metrics,
            "checks": checks, "baseline_sha256": digest(baseline),
            "difference_classification": "NOT_AUTOMATICALLY_A_BUG",
            "unverified_concepts": ["alternative_winner", "partial_order", "ties", "unresolved",
                                    "evidence_conflict", "market_conflict"],
            "candidate_sha256": digest(candidate), "production_equivalence": "NOT_CLAIMED",
            "promotion": "HOLD", "production_effect": "NONE"}


def post_result_prediction_utility(candidate, baseline, source_binding, final, result, verification,
                                   *, expected_execution_id=None):
    """Prediction-only measurement; verified RESULT stays outside Owner inputs.

    This function does not settle money, create a new counter or authorize OOS.
    Existing Family governance and human review own any later promotion.
    """
    lineage = candidate["lineage"]
    if (verification.get("verified") is not True
            or result.get("receipt", {}).get("phase") != "RESULT"
            or result.get("receipt", {}).get("status") != "PASS"):
        raise CandidateHold("RESULT_UTILITY_VERIFICATION_REQUIRED")
    if (lineage["source_binding"] != source_binding
            or final["artifact"].get("source_receipt_sha256") != source_binding.get("source_receipt_sha256")
            or final["artifact"].get("source_snapshot_sha256") != source_binding.get("source_snapshot_sha256")
            or result["artifact"].get("frozen_refs", {}).get("final_receipt_sha256") != final.get("receipt_sha256")):
        raise CandidateHold("RESULT_UTILITY_FROZEN_LINEAGE_MISMATCH")
    if (result["receipt"]["race_id"] != lineage["race_id"]
            or final["receipt"]["race_id"] != lineage["race_id"]
            or (expected_execution_id or source_binding.get("execution_id")) != lineage["execution_id"]
            or digest(candidate["prediction"]) != lineage["prediction_output_sha256"]):
        raise CandidateHold("RESULT_UTILITY_RACE_OR_PREDICTION_MISMATCH")
    if lineage["execution_class"] == "PRE_RACE_SHADOW":
        if timestamp(lineage["freeze_timestamp"]) >= timestamp(lineage["release_deadline_at"]):
            raise CandidateHold("RESULT_UTILITY_POST_DEADLINE_FREEZE")
    order = [str(r) for r in result["artifact"]["official_result"]["finish_order"][:3]]
    if len(order) != 3 or len(set(order)) != 3:
        raise CandidateHold("RESULT_UTILITY_TOP3_REQUIRED")
    prediction = candidate["prediction"]
    legacy = baseline["static_prediction"]
    def metrics(rank, roles, pairs, thirds, alternative):
        if any(r not in rank for r in order):
            raise CandidateHold("RESULT_UTILITY_UNIVERSE_MISMATCH")
        ranks = [rank.index(r) + 1 for r in order]
        def supported(rows, fields, selection):
            statuses = [p.get("status") for p in (rows or []) if [str(p[k]) for k in fields] == selection]
            if any(s in ("PURCHASE", "PROTECT") for s in statuses):
                return True
            return "UNKNOWN" if any(s not in ("EXCLUDE", "REJECT", "REMOVED_JUSTIFIED") for s in statuses) else False
        return {"Winner_rank": ranks[0], "P2_rank": ranks[1], "P3_rank": ranks[2],
                "Top3_mean_rank": sum(ranks) / 3,
                "role_capture": {c: order[i] in roles.get(c, []) for i, c in enumerate(("W", "P2", "P3"))},
                "width": {c: len(roles.get(c, [])) for c in ("W", "P2", "P3")},
                "Alternative_Winner": "UNKNOWN" if alternative in (None, "UNKNOWN") else alternative == order[0],
                "Ordered_Pair": supported(pairs, ("head", "second"), order[:2]),
                "Pair_conditioned_Third": supported(thirds, ("head", "second", "third"), order)}
    candidate_roles = {c: [r["runner_id"] for r in prediction["roles"] if c in r["columns"]] for c in ("W", "P2", "P3")}
    legacy_roles = {c: [str(k) for k, v in legacy["roles"].items() if c in v] for c in ("W", "P2", "P3")}
    changes = {}
    for i, c in enumerate(("W", "P2", "P3")):
        added = set(candidate_roles[c]) - set(legacy_roles[c])
        removed = set(legacy_roles[c]) - set(candidate_roles[c])
        changes[c] = {"promotions": sorted(added), "demotions": sorted(removed),
                      "false_promotions": sorted(added - {order[i]}),
                      "false_demotions": sorted(removed & {order[i]})}
    return {"status": "PREDICTION_UTILITY_MEASURED", "candidate_id": lineage["candidate_id"],
            "race_id": lineage["race_id"], "execution_id": lineage["execution_id"],
            "execution_class": lineage["execution_class"], "source_binding": source_binding,
            "final_receipt_sha256": final["receipt_sha256"], "result_receipt_sha256": result.get("receipt_sha256"),
            "candidate_prediction_sha256": lineage["prediction_output_sha256"],
            "candidate": metrics(prediction["ranking"], candidate_roles, prediction["pair_dispositions"], prediction["third_dispositions"], prediction["alternative_winner"]),
            "legacy": metrics([str(r) for r in legacy["ranking"]], legacy_roles, baseline.get("pair_dispositions"), baseline.get("third_dispositions"), legacy.get("alternative_winner")),
            "role_changes": changes, "uncertainty_quality": "UNKNOWN / NO_CALIBRATED_QUALITY_MAPPING",
            "economic_evaluation": "SEPARATE / MEC_TICKET_CAPITAL_PFS_NOT_OWNER_EQUIVALENCE",
            "actual_purchase_pfs": "UNKNOWN", "count_increment": 0,
            "oos_authorization": "EXISTING_FORWARD_GOVERNANCE_REQUIRED",
            "maturity_promotion_contract": "KM-FAMILY-CROSS-FAMILY-MATURITY-PROMOTION-20260928-R1",
            "promotion": "HOLD", "automatic_promotion": False, "production_effect": "NONE"}


def historical_behavioral_comparison(config, *, root, verify=None, call=responses_call):
    """Read only audited frozen SOURCE/intent; never open RESULT artifacts."""
    if call is responses_call and not os.environ.get("OPENAI_API_KEY"):
        raise CandidateHold("SERVICE_ACCOUNT_RUNTIME_SECRET_MISSING")
    if verify is None:
        from execution_gateway import family_config, request_json
        endpoint = family_config("LOCAL")["external_endpoint"].rstrip("/")
        def verify(envelope):
            status, result = request_json(endpoint + "/verify", method="POST", payload=envelope)
            if status != 200 or result.get("verified") is not True:
                raise CandidateHold("SOURCE_FRESH_VERIFICATION_HOLD")
            return result
    audit = json.loads((root / "research/execution/OWNER_REALITY_AUDIT_20261002.json").read_text())
    reports = []
    for record in audit["findings"]:
        evidence = record["evidence"]
        source_spec = evidence["SOURCE/source_receipt_envelope.json"]
        envelope = json.loads(pinned_text(root, {"path": source_spec["path"], "sha256": source_spec["file_sha256"]}))
        baseline = json.loads(pinned_text(root, {"path": record["intent_path"], "sha256": record["intent_file_sha256"]}))
        authority_paths = [p for p in (root / "profiles").glob("KM_FAMILY_CURRENT_AUTHORITY_*.json")
                           if json.loads(p.read_text()).get("manifest_id") == record["declared_authority"]]
        if len(authority_paths) != 1:
            raise CandidateHold("HISTORICAL_AUTHORITY_UNRESOLVED")
        authority = json.loads(authority_paths[0].read_text())
        binding_spec = evidence["FORMAL/static_source_basis_binding.json"]
        binding = json.loads(pinned_text(root, {"path": binding_spec["path"], "sha256": binding_spec["file_sha256"]}))
        if (binding.get("source_receipt_sha256") != envelope.get("receipt_sha256")
                or binding.get("source_snapshot_sha256") != envelope["artifact"].get("source_snapshot_sha256")
                or binding.get("execution_id") != record["execution_id"]):
            raise CandidateHold("COMPARISON_SOURCE_BASIS_MISMATCH")
        from local_numerical_authority_gate import assess
        context = {"execution_id": record["execution_id"], "race_id": record["race_id"],
                   "signed_source": envelope, "source_verification": verify(envelope),
                   "source_binding": binding, "current_authority": authority,
                   "production_numerical_authority": assess(),
                   "prediction_cutoff": envelope["artifact"]["prediction_cutoff"],
                   "release_deadline_at": baseline.get("scheduled_post_at") or envelope["artifact"]["prediction_cutoff"],
                   "execution_class": "HISTORICAL_BEHAVIORAL_COMPARISON"}
        candidate = execute(context, config, root=root, call=call)
        reports.append({"race_id": record["race_id"], "candidate": candidate,
                        "behavioral_comparison": compare(candidate, baseline, binding)})
    return {"status": "HISTORICAL_BEHAVIORAL_COMPARISON_RECORDED", "candidate_id": CANDIDATE_ID,
            "oos_eligible": False, "count_increment": 0, "production_effect": "NONE",
            "automatic_promotion": False, "promotion": "HOLD", "comparisons": reports}


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--historical-comparison", action="store_true", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    root = pathlib.Path(__file__).resolve().parents[1]
    try:
        path = (root / args.config).resolve()
        if not path.is_relative_to(root):
            raise CandidateHold("PINNED_INPUT_PATH_INVALID")
        config = json.loads(path.read_text())
        ensure_clean(config)
        report = historical_behavioral_comparison(config, root=root)
        code = 0
    except Exception as exc:
        report = {"status": "HOLD", "code": str(exc) if isinstance(exc, CandidateHold) else "SHADOW_RUNTIME_HOLD",
                  "production_effect": "NONE", "promotion": "HOLD", "count_increment": 0}
        code = 2
    dest = pathlib.Path(args.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "code": report.get("code"), "production_effect": "NONE"}))
    return code


if __name__ == "__main__":
    raise SystemExit(main())

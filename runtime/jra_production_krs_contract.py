"""Formal JRA Production KRS exact-execution and receipt contract.

Prevents a 20,000-run Formal request from reaching Railway as SIM-STD
(default 5,000), or from claiming KRS complete with a mismatched receipt.
All KRS physics, parameter_map and existing signed /verify stay unchanged.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

MODE_FOR_RUNS = {5000: "SIM-STD", 20000: "SIM-HIGH"}


class JRAProductionKRSContractError(ValueError):
    pass


def serialize_krs_payload(payload):
    """Exact existing HTTP serialization, captured before transport."""
    return json.dumps(payload, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def checkpoint_krs_request(payload, directory):
    body=serialize_krs_payload(payload)
    canonical=json.dumps(payload['input_data'],ensure_ascii=False,sort_keys=True,
                         separators=(',',':'),allow_nan=False).encode('utf-8')
    record={'race_id':payload['race_id'], 'wire_sha256':hashlib.sha256(body).hexdigest(),
            'input_data_canonical_sha256':hashlib.sha256(canonical).hexdigest(),
            'wire_serialization':'UTF-8; insertion field order; compact JSON; no newline',
            'input_data_serialization':'UTF-8; sorted keys; compact JSON; no newline',
            'receipt_input_hash_scope':'UNVERIFIED until runtime declares a supported contract',
            'production_policy_effect':'NONE'}
    root=Path(directory);root.mkdir(parents=True,exist_ok=True)
    files={'krs_request_wire.json':body,
           'krs_request_hashes.json':(json.dumps(record,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()}
    for name,raw in files.items():
        path=root/name
        if path.exists() and path.read_bytes()!=raw:
            raise JRAProductionKRSContractError('KRS_REQUEST_CHECKPOINT_CONFLICT:'+name)
        if not path.exists():path.write_bytes(raw)
    return body,record


def production_krs_payload(request: Mapping[str, Any]) -> dict[str, Any]:
    if request.get("family_id") != "JRA":
        raise JRAProductionKRSContractError("JRA_ONLY")
    if request.get("candidate_only") is True or request.get("production_authority") is False:
        raise JRAProductionKRSContractError("CANDIDATE_NOT_PRODUCTION")
    count = request.get("run_count", 5000)
    if type(count) is not int or count not in MODE_FOR_RUNS:
        raise JRAProductionKRSContractError("FORMAL_KRS_RUN_COUNT_UNSUPPORTED")
    mode = MODE_FOR_RUNS[count]
    explicit_mode = request.get("mode")
    if explicit_mode is not None and explicit_mode != mode:
        raise JRAProductionKRSContractError(
            f"FORMAL_KRS_MODE_COUNT_CONFLICT:{explicit_mode}!={mode}"
        )
    race_id = str(request.get("race_id") or "").strip()
    if not race_id:
        raise JRAProductionKRSContractError("FORMAL_RACE_ID_REQUIRED")
    seed = request.get("seed")
    if type(seed) is not int or seed < 0:
        raise JRAProductionKRSContractError("FORMAL_KRS_SEED_INVALID")
    adapter_mode = request.get("jra_adapter_mode") or "EXPLICIT_ENGINE_HSV"
    if adapter_mode != "EXPLICIT_ENGINE_HSV":
        raise JRAProductionKRSContractError("FORMAL_KRS_ADAPTER_NOT_PRODUCTION")
    original = request.get("krs_input_data")
    if not isinstance(original, dict) or not isinstance(original.get("simulation"), dict):
        raise JRAProductionKRSContractError("FORMAL_KRS_INPUT_MISSING")
    kinput = deepcopy(original)
    kinput["simulation"]["run_count"] = count
    kinput["simulation"]["master_seed"] = seed
    return {
        "race_id": race_id,
        "input_data": kinput,
        "mode": mode,
        "seed": seed,
        "input_class": "FORMAL-LIVE-" + adapter_mode,
    }


def assert_production_krs_receipt(
    payload: Mapping[str, Any],
    response: Mapping[str, Any],
    *,
    expected_engine_sha256: str,
) -> dict[str, Any]:
    run = response.get("run_receipt")
    receipt = run.get("receipt") if isinstance(run, dict) else None
    if not isinstance(receipt, dict) or receipt.get("status") != "EXECUTED":
        raise JRAProductionKRSContractError("FORMAL_KRS_NOT_EXECUTED")
    count = payload["input_data"]["simulation"]["run_count"]
    required = {
        "race_id": payload["race_id"],
        "mode": payload["mode"],
        "seed": payload["seed"],
        "requested_run_count": count,
        "actual_run_count": count,
        "engine_sha256": expected_engine_sha256,
        "input_class": payload["input_class"],
    }
    for name, expected in required.items():
        if receipt.get(name) != expected:
            raise JRAProductionKRSContractError(
                f"FORMAL_KRS_RECEIPT_{name.upper()}_MISMATCH:"
                f"{receipt.get(name)!r}!={expected!r}"
            )
    for name in ("input_sha256", "output_sha256"):
        value = receipt.get(name)
        if not isinstance(value, str) or len(value) != 64 or any(
            c not in "0123456789abcdef" for c in value
        ):
            raise JRAProductionKRSContractError(f"FORMAL_KRS_RECEIPT_{name.upper()}_INVALID")
    if not run.get("receipt_sha256"):
        raise JRAProductionKRSContractError("FORMAL_KRS_RECEIPT_HASH_MISSING")
    # The signed output digest must bind the exact structured output consumed
    # downstream. A genuine receipt alone cannot authenticate a different body.
    raw=response.get('output_canonical_json')
    if not isinstance(raw,str) or not isinstance(response.get('output'),dict):
        raise JRAProductionKRSContractError('FORMAL_KRS_STRUCTURED_OUTPUT_MISSING')
    if hashlib.sha256(raw.encode('utf-8')).hexdigest()!=receipt['output_sha256']:
        raise JRAProductionKRSContractError('FORMAL_KRS_OUTPUT_HASH_MISMATCH')
    try:decoded=json.loads(raw)
    except (TypeError,ValueError) as exc:
        raise JRAProductionKRSContractError('FORMAL_KRS_OUTPUT_JSON_INVALID') from exc
    if json.dumps(decoded,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)!=json.dumps(
            response['output'],sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False):
        raise JRAProductionKRSContractError('FORMAL_KRS_STRUCTURED_OUTPUT_MISMATCH')
    declared=receipt.get('input_hash_contract')
    if declared is not None:
        if declared!='KM-KRS-INPUT-DATA-SORTED-UTF8-v1':
            raise JRAProductionKRSContractError('FORMAL_KRS_INPUT_HASH_CONTRACT_UNSUPPORTED')
        expected=hashlib.sha256(json.dumps(payload['input_data'],ensure_ascii=False,
            sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')).hexdigest()
        if receipt['input_sha256']!=expected:
            raise JRAProductionKRSContractError('FORMAL_KRS_INPUT_HASH_MISMATCH')
    # The independent /verify call must still verify the signed envelope.
    return receipt

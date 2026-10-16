"""Formal JRA Production KRS exact-execution and receipt contract.

Prevents a 20,000-run Formal request from reaching Railway as SIM-STD
(default 5,000), or from claiming KRS complete with a mismatched receipt.
All KRS physics, parameter_map and existing signed /verify stay unchanged.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

MODE_FOR_RUNS = {5000: "SIM-STD", 20000: "SIM-HIGH"}


class JRAProductionKRSContractError(ValueError):
    pass


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
    # The independent /verify call must still verify the signed envelope.
    return receipt

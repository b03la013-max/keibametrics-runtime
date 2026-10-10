"""JRA Candidate KRS runtime-mode and receipt conformance.

Operational correctness only. No numerical formula, KRS physics, purchase
policy, or Production authority is introduced by this module.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

ENGINE_SHA256 = "9929df994aa7964173edef9af7e9a705628ce377babf22df3af4e280fc275421"
INPUT_CLASS = "FORWARD-OOS-CANDIDATE-SOURCE-DERIVED-NON-PRODUCTION"
ACCEPTANCE_INPUT_CLASS = "CANDIDATE-SOURCE-DERIVED-NON-PRODUCTION"
MODE_BY_COUNT = {5000: "SIM-STD", 20000: "SIM-HIGH"}


class CandidateKRSConformanceError(ValueError):
    pass


def build_candidate_krs_payload(\n    request: Mapping[str, Any], *, input_class: str = INPUT_CLASS\n) -> dict[str, Any]:
    """Make mode and actual simulation count impossible to disagree silently."""
    if input_class not in {INPUT_CLASS, ACCEPTANCE_INPUT_CLASS}:\n        raise CandidateKRSConformanceError("KRS_INPUT_CLASS_NOT_AUTHORIZED")\n    if request.get("family_id") != "JRA":
        raise CandidateKRSConformanceError("JRA_ONLY")
    race_id = str(request.get("race_id") or "").strip()
    if not race_id:
        raise CandidateKRSConformanceError("KRS_RACE_ID_REQUIRED")
    count = request.get("run_count")
    if type(count) is not int or count not in MODE_BY_COUNT:
        raise CandidateKRSConformanceError("KRS_RUN_COUNT_UNSUPPORTED_BY_RUNTIME")
    seed = request.get("seed")
    if type(seed) is not int or seed < 0:
        raise CandidateKRSConformanceError("KRS_SEED_INVALID")
    source = request.get("krs_input_data")
    if not isinstance(source, dict) or not isinstance(source.get("simulation"), dict):
        raise CandidateKRSConformanceError("KRS_SIMULATION_INPUT_MISSING")
    kinput = deepcopy(source)
    kinput["simulation"]["run_count"] = count
    kinput["simulation"]["master_seed"] = seed
    return {
        "race_id": race_id,
        "input_data": kinput,
        "mode": MODE_BY_COUNT[count],
        "seed": seed,
        "input_class": input_class,
    }


def verify_candidate_krs_execution(
    payload: Mapping[str, Any],
    response: Mapping[str, Any],
    *,
    engine_sha256: str = ENGINE_SHA256,
) -> dict[str, Any]:
    """Check the external execution *before* allowing MEC, Capital or FINAL.

    This does not verify the cryptographic receipt: the separate /verify
    call remains mandatory after this structural check.
    """
    run = response.get("run_receipt")
    receipt = run.get("receipt") if isinstance(run, dict) else None
    if not isinstance(receipt, dict) or receipt.get("status") != "EXECUTED":
        raise CandidateKRSConformanceError("KRS_EXECUTION_NOT_ATTESTED")
    expected_count = payload["input_data"]["simulation"]["run_count"]
    checks = (
        ("engine_sha256", engine_sha256),
        ("mode", payload["mode"]),
        ("race_id", payload["race_id"]),
        ("seed", payload["seed"]),
        ("requested_run_count", expected_count),
        ("actual_run_count", expected_count),
        ("input_class", payload["input_class"]),
    )
    for field, expected in checks:
        if receipt.get(field) != expected:
            raise CandidateKRSConformanceError(
                f"KRS_RECEIPT_{field.upper()}_MISMATCH:"
                f"{receipt.get(field)!r}!={expected!r}"
            )
    if not isinstance(receipt.get("input_sha256"), str) or not receipt["input_sha256"]:
        raise CandidateKRSConformanceError("KRS_INPUT_SHA_MISSING")
    if not isinstance(receipt.get("output_sha256"), str) or not receipt["output_sha256"]:
        raise CandidateKRSConformanceError("KRS_OUTPUT_SHA_MISSING")
    return receipt

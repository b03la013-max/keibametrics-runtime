"""Read-only archived BVI +1 -> registered AKI role/Pair/Third sensitivity.

This is a 2026-10-25 post-capture counterfactual, NOT a pre-race prediction,
official outcome test, signed SOURCE replay, or Forward OOS. The plus-one BVI
perturbation is hypothetical and is not an ENV feature or Production model.
No KRS / MEC / ticket / Capital execution occurs. Do not infer their outputs.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime"))

from jra_index_provenance_builder import BASE, materialize_index_provenance

PROFILE = "KM-JRA-BVI-REGISTERED-AKI-ROLE-BOUNDARY-AUDIT-20261029"
AUTHORITY = "KM-FAMILY-CURRENT-AUTHORITY-20261012-R51"
D_SHA256 = "a969cc518da73b4795932f02d8f3cbc6d0ac47a1a7904907055e46958d9f0fc1"
D_PATH = "runtime/jra_static_owner_forward_oos/models/bvi_env_20261024_5e7f3b31cebd.json"
METRICS = ("BVI", "TPI", "SRI", "F3S", "T3I", "ZAI_WIN", "ZAI_PLACE")
ROLES = ("W", "P2", "P3")


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")).encode("utf-8")).hexdigest()


def guard_authority(authority, root):
    if authority.get("manifest_id") != AUTHORITY:
        raise ValueError("RESEARCH_AUTHORITY_R51_REQUIRED")
    actual = hashlib.sha256((root / D_PATH).read_bytes()).hexdigest()
    if actual != D_SHA256:
        raise ValueError("FIXED_D_RAW_SHA_MISMATCH")
    return actual


def state(request):
    """Normalize only stage identities; do not copy executable/purchase flags."""
    sp = request["static_prediction"]
    by_id = sp["roles"]
    roles = {c: frozenset(str(rid) for rid, names in by_id.items() if c in names)
             for c in ROLES}
    pairs = frozenset((str(x["head"]), str(x["second"]), str(x["status"]))
                      for x in request["pair_dispositions"])
    thirds = frozenset((str(x["head"]), str(x["second"]), str(x["third"]), str(x["status"]))
                       for x in request["third_dispositions"])
    return {"ranking": tuple(str(x) for x in sp["ranking"]),
            "roles": roles, "pairs": pairs, "thirds": thirds}


def stage_delta(before, after):
    return {
        "static_ranking_changed": before["ranking"] != after["ranking"],
        "role_membership_symmetric_difference": {
            role: len(before["roles"][role] ^ after["roles"][role]) for role in ROLES},
        "pair_decision_symmetric_difference": len(before["pairs"] ^ after["pairs"]),
        "third_decision_symmetric_difference": len(before["thirds"] ^ after["thirds"]),
    }


def _validate_source(req):
    if req.get("family_id") != "JRA" or req.get("current_authority_manifest") != AUTHORITY:
        raise ValueError("ARCHIVED_RACE_SCOPE_OR_AUTHORITY_MISMATCH")
    if req.get("temporal_mode") != "FORMAL-PRE-RACE":
        raise ValueError("NOT_ARCHIVED_FORMAL_PRE_RACE")
    source = req.get("source_snapshot")
    if not isinstance(source, dict) or canonical_sha(source) != req.get("source_snapshot_sha256"):
        raise ValueError("ARCHIVED_SOURCE_HASH_MISMATCH")
    if not isinstance(req.get("index_provenance_ledger", {}).get("runners"), dict):
        raise ValueError("ARCHIVED_FULL20_LEDGER_MISSING")
    return {**source, "source_snapshot_sha256": req["source_snapshot_sha256"]}


def probe(request, authority, root):
    """Two independent in-memory replays under the *same* unchanged R51 AKI."""
    from jra_aki_dispatch import apply_authorized_v21
    source = _validate_source(request)
    base = materialize_index_provenance(request)
    candidate = deepcopy(request)
    changed = 0
    for rid, spec in candidate["index_provenance_ledger"]["runners"].items():
        old = spec["base_indices"]["BVI"]["value"]
        if type(old) not in (int, float) or not math.isfinite(old) or not 0 <= old <= 100:
            raise ValueError("BVI_VALUE_INVALID:" + rid)
        new = min(100.0, float(old) + 1.0)
        spec["base_indices"]["BVI"]["value"] = new
        changed += new != old
    comparison = materialize_index_provenance(candidate)
    b = {str(x["runner_id"]): x["canonical_components"] for x in base["runners"]}
    c = {str(x["runner_id"]): x["canonical_components"] for x in comparison["runners"]}
    if set(b) != set(c):
        raise ValueError("SCALAR_COUNTERFACTUAL_RUNNER_MISMATCH")
    metric_counts = Counter()
    for rid in b:
        for key in BASE:
            if key != "BVI" and b[rid][key]["value"] != c[rid][key]["value"]:
                raise ValueError("SCALAR_COUNTERFACTUAL_NON_BVI_BASE_MUTATION:" + rid + ":" + key)
        for key in METRICS:
            metric_counts[key] += abs(b[rid][key]["value"] - c[rid][key]["value"]) > 1e-6
        if b[rid]["DCR"]["value"] != c[rid]["DCR"]["value"]:
            raise ValueError("DCR_CHANGED_BY_BVI_ONLY")
    baseline = apply_authorized_v21(deepcopy(base), source, authority, root=root)
    varied = apply_authorized_v21(deepcopy(comparison), source, authority, root=root)
    saved = state(request)
    replayed = state(baseline)
    delta = stage_delta(replayed, state(varied))
    return {
        "race_id": request["race_id"],
        "status": "RECOMPUTED_REGISTERED_AKI_IN_MEMORY",
        "archived_replay_match": stage_delta(saved, replayed) == {
            "static_ranking_changed": False,
            "role_membership_symmetric_difference": {r: 0 for r in ROLES},
            "pair_decision_symmetric_difference": 0, "third_decision_symmetric_difference": 0},
        "runner_count": len(b), "bvi_changed_runners": changed,
        "recomputed_index_changed_runners": dict(metric_counts),
        "registered_aki_stage_delta": delta,
        "downstream": {
            "krs_executed": False, "krs_changed": None,
            "mec_executed": False, "mec_changed": None,
            "ticket_changed": None, "same_budget_cost_delta": None,
            "capital_changed": None, "pfs": None},
    }


def run(root=ROOT):
    root = Path(root).resolve()
    authority = json.loads((root / "profiles/KM_FAMILY_CURRENT_AUTHORITY_20261012_R51.json").read_text())
    d_sha = guard_authority(authority, root)
    paths = sorted((root / "runtime/requests").glob("*20261025*FORMAL.json"))
    if not paths:
        raise ValueError("NO_ARCHIVED_20261025_FORMAL_REQUESTS")
    outcomes = []
    totals = Counter()
    for path in paths:
        raw = path.read_bytes()
        file_sha = hashlib.sha256(raw).hexdigest()
        race_id = path.name.split("-LIVE-")[0]
        try:
            req = json.loads(raw)
            result = probe(req, authority, root)
            if result["race_id"] != race_id:
                raise ValueError("REQUEST_FILE_RACE_ID_MISMATCH")
            totals["recomputed_races"] += 1
            totals["runners"] += result["runner_count"]
            totals["bvi_perturbed_runners"] += result["bvi_changed_runners"]
            totals["archived_exact_replay_races"] += result["archived_replay_match"] is True
            for key, count in result["recomputed_index_changed_runners"].items():
                totals["numeric_" + key] += count
            for key, count in result["registered_aki_stage_delta"]["role_membership_symmetric_difference"].items():
                totals["role_membership_changed_" + key] += count
            totals["pair_decision_changes"] += result["registered_aki_stage_delta"]["pair_decision_symmetric_difference"]
            totals["third_decision_changes"] += result["registered_aki_stage_delta"]["third_decision_symmetric_difference"]
            totals["ranking_changed_races"] += result["registered_aki_stage_delta"]["static_ranking_changed"]
            outcomes.append({**result, "original_request_raw_sha256": file_sha})
        except Exception as exc:
            totals["blocked_races"] += 1
            outcomes.append({"race_id": race_id, "original_request_raw_sha256": file_sha,
                             "status": "BLOCKED_INDEPENDENT_REPLAY",
                             "reason": type(exc).__name__ + ":" + str(exc)[:320],
                             "krs_changed": None, "ticket_changed": None, "pfs": None})
        if hashlib.sha256(path.read_bytes()).hexdigest() != file_sha:
            raise ValueError("ARCHIVED_REQUEST_MUTATED_BY_RESEARCH")
    report = {
        "profile": PROFILE,
        "classification": "POSTCAPTURE_20261025_READ_ONLY_SCALAR_ABLATION; NOT_FORWARD_OOS",
        "current_authority": AUTHORITY, "fixed_d_raw_sha256": d_sha,
        "archived_request_count": len(paths), "totals": dict(totals),
        "outcomes": outcomes, "source_result_labels_read": False,
        "scalar_intervention": "MIN_100_BVI_PLUS_ONE_ONLY; NOT_A_SHARED_PEDIGREE_FEATURE_CHANGE",
        "shared_pedigree_value_effect": None,
        "registered_role_policy": "UNCHANGED_R51_REGISTERED_AKI; IN_MEMORY_REPLAY_ONLY",
        "KRS_MEC_TICKET_CAPITAL_ACTUAL_DIFF": None,
        "unknown_downstream_is_zero": False,
        "production_effect": "NONE", "purchase_authority": False,
        "forward_oos_increment": 0, "model_selection": "REJECT_HISTORICAL_INCREMENT",
        "automatic_promotion": False,
    }
    report["sha256"] = canonical_sha(report)
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repository", type=Path, default=ROOT)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    report = run(args.repository)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise ValueError("RESEARCH_REPORT_ALREADY_EXISTS")
    args.output.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"profile": PROFILE, "classification": report["classification"],
                      "totals": report["totals"], "report_sha256": report["sha256"],
                      "unresolved_downstream": report["KRS_MEC_TICKET_CAPITAL_ACTUAL_DIFF"]},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()

"""FNB frozen FINAL presentation completeness, NOT recipient Delivery evidence.

All owners/methods remain alternatives; a structural check of self-contained
metadata is not an independent signature, numeric calculation, KRS execution
or actual recipient acknowledgement.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from runtime.local_fnb_r9_method_audit import audit_methods

OWNER_NAMES = ("BASELINE", "CANDIDATE")
ROLES = ("W", "P2", "P3")
PROD_INDEX_MAPPING = (Path(__file__).resolve().parents[1] /
    "mapping/local_full_numerical_mapping_v1.0_production_20261008.json")


def _indices():
    try:
        data=json.loads(PROD_INDEX_MAPPING.read_text(encoding="utf-8"))
        keys=data.get("required_indices")
        return keys if isinstance(keys,list) and len(keys)==29 and len(set(keys))==29 else None
    except (OSError,ValueError,TypeError):
        return None


def audit_presentation(artifact, runner_ids):
    missing=[]
    pkg=artifact.get("final_prediction_package") if isinstance(artifact,dict) else None
    pkg=pkg if isinstance(pkg,dict) else {}
    ids=[str(x) for x in runner_ids] if isinstance(runner_ids,list) else []
    wanted=set(ids)
    if not wanted or len(ids)!=len(wanted) or any(not x.isdigit() for x in ids):
        missing.append("OFFICIAL_RUNNER_UNIVERSE_NOT_PROVEN")
    rank=pkg.get("ranking")
    if not isinstance(rank,list) or len(rank)!=len(wanted) or set(map(str,rank))!=wanted:
        missing.append("ALL_RUNNER_RANKING_MISSING")
    roles=pkg.get("roles")
    if (not isinstance(roles,dict) or set(roles)!=wanted or any(
            not isinstance(v,list) or not set(v)<=set(ROLES) or
            len(v)!=len(set(v)) for v in roles.values())):
        missing.append("ALL_RUNNER_ROLE_MATRIX_MISSING")
    unknown=pkg.get("unknown_by_runner")
    if not isinstance(unknown,dict) or set(unknown)!=wanted or any(
            not isinstance(v,(dict,list)) for v in unknown.values()):
        missing.append("ALL_RUNNER_UNKNOWN_NOT_EXPLICIT")

    required=_indices()
    if required is None:
        missing.append("PRODUCTION_29_INDEX_MANIFEST_NOT_RESOLVED")
    cells=pkg.get("numerical_cells_by_runner")
    numerical_good=(required is not None and isinstance(cells,dict) and
                    set(cells)==wanted and all(
                    isinstance(specs,dict) and set(specs)==set(required)
                    for specs in cells.values()))
    if numerical_good:
        for rid in ids:
            for index in required:
                cell=cells[rid][index]
                value=cell.get("value") if isinstance(cell,dict) else None
                if (not isinstance(cell,dict)
                        or cell.get("terminal_status") not in ("CALCULATED","RULED-NEUTRAL")
                        or type(value) not in (int,float)
                        or not math.isfinite(value) or not 0<=value<=100
                        or not cell.get("rule_id") or not cell.get("evidence_refs")
                        or not cell.get("source_fact")):
                    numerical_good=False
                    break
            if not numerical_good:
                break
    if not numerical_good:
        missing.append("ALL_RUNNERS_29_INDICES_NOT_MATERIALIZED")

    owner_rankings=pkg.get("owner_rankings")
    if (not isinstance(owner_rankings,dict) or set(owner_rankings)!=set(OWNER_NAMES)
            or any(not isinstance(r,list) or len(r)!=len(wanted)
                   or set(map(str,r))!=wanted for r in owner_rankings.values())):
        missing.append("DUAL_OWNER_RANKINGS_INCOMPLETE")
    owner_roles=pkg.get("owner_roles")
    if not isinstance(owner_roles,dict) or set(owner_roles)!=set(OWNER_NAMES):
        missing.append("DUAL_OWNER_ROLE_COLUMNS_INCOMPLETE")
    else:
        for owner in OWNER_NAMES:
            columns=owner_roles[owner]
            if (not isinstance(columns,dict) or set(columns)!=set(ROLES)
                    or any(not isinstance(v,list) or not v
                           or len(v)!=len(set(map(str,v)))
                           or not set(map(str,v))<=wanted
                           for v in columns.values())):
                missing.append("DUAL_OWNER_ROLE_COLUMNS_INCOMPLETE:"+owner)
    krs=pkg.get("krs_owner_receipts")
    if not isinstance(krs,dict) or set(krs)!=set(OWNER_NAMES) or any(
            not isinstance(x,dict) or
            type(x.get("run_count")) is not int or x["run_count"]!=5000 or
            type(x.get("seed")) is not int or x["seed"]!=1 or
            not isinstance(x.get("receipt_sha256"),str) or
            len(x["receipt_sha256"])!=64 for x in krs.values()):
        missing.append("DUAL_OWNER_KRS_5000_RECEIPT_FIELDS_MISSING")
    method=audit_methods(pkg.get("owner_method_portfolios"))
    if not method["complete"]:
        missing.extend(method["failures"])
    result={
        "status":"DISPLAY_FIELDS_OBSERVED_DELIVERY_UNPROVEN" if not missing
                 else "DELIVERY_PRESENTATION_INCOMPLETE",
        "missing":list(dict.fromkeys(missing)),
        "method_audit":method,
        "all_horses_numerically_displayed":numerical_good,
        "six_alternative_methods_structurally_validated":method["complete"],
        "dual_owner_krs_signatures_independently_verified":False,
        "source_to_index_independently_verified":False,
        "prestart_delivery_pass":False,
        "recipient_ack":False, "user_received_at":None,
        "signed_source_or_calculation_verified_here":False,
        "full_content_not_a_delivery_receipt":True}
    return result

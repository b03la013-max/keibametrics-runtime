"""AKI reference trees for FINALs frozen BEFORE the AKI width policy (R49).

A Production FINAL is immutable, so races frozen under the earlier fixed-cluster
widths keep their signed tickets. For those races this computes, from the SAME
frozen pre-race Full20 inputs (the canonical FORMAL request), what the current
AKI-JRA v2 Static Owner would select, and publishes it as a clearly labelled
REFERENCE: not signed, not a FINAL, not a purchase basis, computed after the
freeze (timestamp recorded). The signed FINAL is never modified.
"""
from __future__ import annotations

import copy
import glob
import json
from datetime import datetime, timezone
from pathlib import Path

from jra_static_owner_executable import PROFILE as AKI_PROFILE, compile_static_owner
from jra_ticket_tree_renderer import render_ticket_tree

LABEL = "AKI再計算・参考（正式FINALではない／署名なし／購入根拠にしない）"


def _formal_request(root: Path, race_id: str):
    paths = sorted(glob.glob(str(root / "runtime" / "requests" / f"{race_id}-LIVE-R*-FORMAL.json")))
    return json.loads(Path(paths[-1]).read_text(encoding="utf-8")) if paths else None


def aki_reference(root: Path, race_id: str) -> dict | None:
    fpath = root / "runtime" / "final_artifacts" / f"{race_id}.json"
    if not fpath.exists():
        return None
    final = json.loads(fpath.read_text(encoding="utf-8"))
    if ((final.get("static_prediction") or {}).get("aki_jra_v2")
            or (final.get("static_prediction") or {}).get("aki_jra_v21")):
        return None  # already decided by AKI in the signed FINAL
    req = _formal_request(root, race_id)
    if not req:
        return {"status": "FORMAL_REQUEST_MISSING"}
    # Prefer the newly enacted official route for references when activated.
    candidates=[]
    for path in (root / "profiles").glob("KM_FAMILY_CURRENT_AUTHORITY_*.json"):
        authority=json.loads(path.read_text(encoding="utf-8"))
        if ((authority.get("family_scoped_authority") or {}).get("JRA") or {}).get("aki_v21_activation"):
            candidates.append((authority.get("effective_at", ""),authority))
    if candidates:
        from jra_aki_v21 import apply_authorized_v21, PROFILE
        from jra_aki_capital_preflight import verify_aki_ticket_binding
        from minimum_efficient_coverage import build_mec_plan
        from capital_policy import resolve_capital_policy
        authority=max(candidates,key=lambda row:row[0])[1]
        source={**req["source_snapshot"],"source_snapshot_sha256":req["source_snapshot_sha256"]}
        selected=apply_authorized_v21(req,source,authority,root=root)
        mec=build_mec_plan(selected)
        binding=verify_aki_ticket_binding(selected,mec,source=source,current_authority=authority,root=root)
        capital=resolve_capital_policy(selected,mec)
        tree=render_ticket_tree({"static_prediction":selected["static_prediction"],
                "capital_policy_decision":capital,"aki_information_gate":selected.get("aki_information_gate"),"final_prediction_package":{"validation_status":"UNVALIDATED"},
                "final_ticket":{"tickets":mec["tickets"],"no_bet":capital["no_bet"]}})
        return {"status":"AKI_REFERENCE_ONLY","label":LABEL,"policy_profile":PROFILE,
                "computed_at":datetime.now(timezone.utc).isoformat(),
                "inputs":"same frozen pre-race Full20; unsigned mechanical replay, no OOS",
                "signed_final_ticket_count":len((final.get("final_ticket") or {}).get("tickets") or []),
                "reference_ticket_count":mec["ticket_count"],"reference_total_investment":mec["minimum_required_capital"],
                "aki_jra_v21":selected["static_prediction"]["aki_jra_v21"],
                "capital_policy_decision":capital,"binding":binding,"tree":LABEL+"\n"+tree["text"]}
    owner = compile_static_owner(
        copy.deepcopy(req), source_snapshot_sha256=req["source_snapshot_sha256"],
        source_receipt_sha256=str(req.get("source_snapshot_sha256")),
        frozen_at=req["prediction_cutoff"], prediction_cutoff=req["prediction_cutoff"])
    tickets = [{"bet_type": "EXACTA", "selection": [int(p["head"]), int(p["second"])], "stake": 100}
               for p in owner["pair_dispositions"] if p["status"] == "PURCHASE"]
    tickets += [{"bet_type": "TRIFECTA", "selection": [int(t["head"]), int(t["second"]), int(t["third"])], "stake": 100}
                for t in owner["third_dispositions"] if t["status"] == "PURCHASE"]
    pseudo = {"static_prediction": {"ranking": owner["static_prediction"]["ranking"],
                                    "aki_jra_v2": owner["aki_jra_v2"]},
              "capital_policy_decision": {"decision": "AKI_REFERENCE_ONLY"},
              "final_prediction_package": {"validation_status": "UNVALIDATED"},
              "final_ticket": {"tickets": tickets, "no_bet": False}}
    tree = render_ticket_tree(pseudo)
    signed = len((final.get("final_ticket") or {}).get("tickets") or [])
    return {"status": "AKI_REFERENCE_ONLY", "label": LABEL, "policy_profile": AKI_PROFILE,
            "computed_at": datetime.now(timezone.utc).isoformat(),
            "inputs": "same frozen pre-race Full20 as the signed FINAL (canonical FORMAL request)",
            "signed_final_ticket_count": signed, "reference_ticket_count": tree["ticket_count"],
            "reference_total_investment": tree["total_investment"],
            "aki_jra_v2": owner["aki_jra_v2"], "tree": LABEL + "\n" + tree["text"]}

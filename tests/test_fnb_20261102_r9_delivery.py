"""R9 prevents synthetic six-method metadata from masquerading as Delivery.

These small positive fixtures test STRUCTURE ONLY; even complete-looking
fields cannot prove signed KRS or recipient acknowledgment.
"""
from __future__ import annotations
from copy import deepcopy

from runtime.local_fnb_r8_delivery_completeness import (
    audit_presentation, audit_venue_presentation, _indices)
from runtime.local_fnb_r9_method_audit import audit_methods
from runtime.jra_ticket_tree_renderer import render_ticket_tree
from runtime import formal_execution_orchestrator as o

IDS=["1","2","3"]


def _tickets(method):
    selection={"EXACTA":[1,2], "TRIO":[1,2,3],
               "TRIFECTA":[1,2,3]}[method]
    return [{"bet_type":method, "selection":selection, "stake":100}]


def _method(method):
    tickets=_tickets(method)
    tree=render_ticket_tree({
        "final_ticket":{"tickets":tickets,"no_bet":False},
        "capital_policy_decision":{"decision":"RECOMMENDATION_ONLY"}})
    return {"tickets":tickets,"point_count":1,"total_investment":100,
            "capital_limit":500,"unused_capital":400,
            "no_bet":False,"canonical_tree":tree["text"]}


def _synthetic():
    indices=_indices()
    assert len(indices)==29
    cells={rid:{idx:{"terminal_status":"RULED-NEUTRAL","value":52.0,
                      "rule_id":"SYNTHETIC_NOT_AUTHORIZED",
                      "evidence_refs":["FAKE"],"source_fact":"test_only"}
                for idx in indices} for rid in IDS}
    methods={method:_method(method)
             for method in ("EXACTA","TRIO","TRIFECTA")}
    pkg={"ranking":list(IDS),
         "roles":{"1":["W"],"2":["P2"],"3":["P3"]},
         "unknown_by_runner":{rid:[] for rid in IDS},
         "numerical_cells_by_runner":cells,
         "owner_rankings":{"BASELINE":list(IDS),"CANDIDATE":list(reversed(IDS))},
         "owner_roles":{owner:{"W":["1"],"P2":["2"],"P3":["3"]}
                        for owner in ("BASELINE","CANDIDATE")},
         "krs_owner_receipts":{owner:{"run_count":5000,"seed":1,
                                      "receipt_sha256":"a"*64}
                              for owner in ("BASELINE","CANDIDATE")},
         "owner_method_portfolios":{
            owner:deepcopy(methods) for owner in ("BASELINE","CANDIDATE")}}
    return {"final_prediction_package":pkg,
            "final_ticket":{"tickets":_tickets("EXACTA"),"no_bet":False}}


def test_r9_structurally_complete_synthetic_portfolios_never_imply_delivery():
    grade=audit_presentation(_synthetic(),IDS)
    assert grade["status"]=="DISPLAY_FIELDS_OBSERVED_DELIVERY_UNPROVEN",grade
    assert grade["method_audit"]["complete"] is True
    assert len(grade["method_audit"]["methods"])==6
    assert grade["six_alternative_methods_structurally_validated"] is True
    assert grade["prestart_delivery_pass"] is False
    assert grade["recipient_ack"] is False
    assert grade["dual_owner_krs_signatures_independently_verified"] is False


def test_r9_rejects_all_six_empty_method_dicts_false_positive():
    obj=_synthetic()
    obj["final_prediction_package"]["owner_method_portfolios"]={
        owner:{method:{} for method in ("EXACTA","TRIO","TRIFECTA")}
        for owner in ("BASELINE","CANDIDATE")}
    grade=audit_presentation(obj,IDS)
    assert grade["status"]=="DELIVERY_PRESENTATION_INCOMPLETE"
    assert len(grade["method_audit"]["failures"])==6


def test_r9_rejects_stake_tree_budget_duplicate_and_method_swaps():
    for problem in ("wrong_stake","wrong_tree","wrong_budget",
                    "duplicate_ticket","wrong_bet"):
        obj=_synthetic()
        m=obj["final_prediction_package"]["owner_method_portfolios"]["BASELINE"]["EXACTA"]
        if problem=="wrong_stake":
            m["tickets"][0]["stake"]=200
        if problem=="wrong_tree":
            m["canonical_tree"]="FAKE"
        if problem=="wrong_budget":
            m["unused_capital"]=500
        if problem=="duplicate_ticket":
            m["tickets"].append(deepcopy(m["tickets"][0]))
            m["point_count"]=2
            m["total_investment"]=200
            m["unused_capital"]=300
        if problem=="wrong_bet":
            m["tickets"][0]["bet_type"]="TRIO"
        audit=audit_presentation(obj,IDS)
        assert audit["status"]=="DELIVERY_PRESENTATION_INCOMPLETE",(problem,audit)
        assert audit["method_audit"]["complete"] is False


def test_r9_rejects_forged_index_scalar_and_missing_provenance():
    obj=_synthetic()
    k=_indices()[0]
    obj["final_prediction_package"]["numerical_cells_by_runner"]["1"][k]=52
    assert "ALL_RUNNERS_29_INDICES_NOT_MATERIALIZED" in (
        audit_presentation(obj,IDS)["missing"])
    obj=_synthetic()
    obj["final_prediction_package"]["numerical_cells_by_runner"]["1"][k]["rule_id"]=""
    assert "ALL_RUNNERS_29_INDICES_NOT_MATERIALIZED" in (
        audit_presentation(obj,IDS)["missing"])


def test_r9_other_local_venues_not_subject_to_fnb_specialized_six_method_gate():
    assert audit_venue_presentation({},["1","2"],"KAW")["status"]=="NOT_APPLICABLE_NON_FNB"
    assert audit_venue_presentation({},["1","2"],"OHI")["status"]=="NOT_APPLICABLE_NON_FNB"
    assert audit_venue_presentation({},["1","2"],"FNB")["status"]=="DELIVERY_PRESENTATION_INCOMPLETE"


def test_r9_historical_fnb_single_portfolio_remains_not_dual_owner_delivery():
    eid="LOCAL-KM-LOCAL-FNB-20261002-R04-LIVE-R1-EXEC"
    phase=o.resolve_phase(eid,"FORMAL")
    assert phase is not None
    artifact=o._load_checkpoint_json(phase,"final_receipt_envelope.json")["artifact"]
    grade=audit_venue_presentation(artifact,[str(i) for i in range(1,13)],"FNB")
    assert grade["status"]=="DELIVERY_PRESENTATION_INCOMPLETE"
    assert "DUAL_OWNER_SIX_METHODS_MISSING" in grade["missing"]
    assert grade["prestart_delivery_pass"] is False

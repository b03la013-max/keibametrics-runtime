"""R7 ticket disposition acceptance from the actual frozen FNB 2026-10-02 R04.

No actual purchase or PFS is created; verified FINAL flag is supplied only
after the caller has already completed external signer verification.
"""
from __future__ import annotations

import copy
import inspect

from runtime import formal_execution_orchestrator as o
from runtime.local_fnb_r7_ticket_disposition import attest_ticket_decision

EID="LOCAL-KM-LOCAL-FNB-20261002-R04-LIVE-R1-EXEC"


def _artifact():
    phase=o.resolve_phase(EID,"FORMAL")
    assert phase is not None
    envelope=o._load_checkpoint_json(phase,"final_receipt_envelope.json")
    assert envelope["receipt"]["status"]=="PASS"
    return envelope["artifact"]


def test_r7_actual_fnb_canonical_is_selected_not_actually_purchased():
    frozen=_artifact()
    grade=attest_ticket_decision(frozen,final_verified=True)
    assert grade["status"]=="VERIFIED_FROZEN_RECOMMENDATION_TICKETS"
    assert grade["ticket_count"]==80
    assert grade["recommendation_investment"]==8000
    assert grade["actual_purchase"]=="NOT_VERIFIED"
    assert grade["no_bet_calculated"] is False
    assert grade["pfs"] is None
    assert grade["recipient_delivery_ack"]=="NOT_VERIFIED"


def test_r7_zero_tickets_without_capital_no_bet_must_not_be_no_bet():
    frozen=_artifact()
    fake=copy.deepcopy(frozen)
    fake["final_ticket"]["tickets"]=[]
    fake["final_ticket"]["total_investment"]=0
    grade=attest_ticket_decision(fake,final_verified=True)
    assert grade["status"]=="ZERO_TICKETS_WITHOUT_CONFIRMED_CAPITAL_NO_BET"
    assert grade["no_bet_calculated"] is False
    assert grade["pfs"] is None


def test_r7_calculated_no_bet_requires_capital_and_zero_stake():
    frozen=_artifact()
    no_bet=copy.deepcopy(frozen)
    no_bet["final_ticket"]["tickets"]=[]
    no_bet["final_ticket"]["total_investment"]=0
    no_bet["final_ticket"]["no_bet"]=True
    no_bet["capital_policy_decision"]["no_bet"]=True
    no_bet["capital_policy_decision"]["reason"]="Budget is smaller than minimum MEC coverage."
    grade=attest_ticket_decision(no_bet,final_verified=True)
    assert grade["status"]=="VERIFIED_FROZEN_RECOMMENDATION_NO_BET"
    assert grade["no_bet_calculated"] is True
    assert grade["recommendation_investment"]==0
    assert grade["pfs"] is None
    assert grade["pfs_reason"]=="NO_BET_ZERO_INVESTMENT_PFS_NULL"
    fake=copy.deepcopy(no_bet)
    fake["capital_policy_decision"]["reason"]=""
    assert attest_ticket_decision(fake,final_verified=True)["no_bet_calculated"] is False


def test_r7_unverified_final_never_implies_no_bet_or_actual_purchase():
    frozen=_artifact()
    frozen["final_ticket"]["tickets"]=[]
    frozen["final_ticket"]["total_investment"]=0
    frozen["final_ticket"]["no_bet"]=True
    frozen["capital_policy_decision"]["no_bet"]=True
    grade=attest_ticket_decision(frozen,final_verified=False)
    assert grade["status"]=="UNVERIFIED_FINAL_NOT_A_CALCULATED_NO_BET"
    assert grade["no_bet_calculated"] is False
    assert grade["ticket_count"] is None
    assert grade["pfs"] is None


def test_r7_stake_tamper_and_no_bet_conflict_are_rejected():
    frozen=_artifact()
    fake=copy.deepcopy(frozen)
    fake["final_ticket"]["tickets"][0]["stake"]+=100
    assert attest_ticket_decision(fake,final_verified=True)["status"]=="TICKET_TOTAL_STAKE_MISMATCH"
    fake=copy.deepcopy(frozen)
    fake["capital_policy_decision"]["no_bet"]=True
    assert attest_ticket_decision(fake,final_verified=True)["status"]=="TICKETS_PRESENT_BUT_CAPITAL_NO_BET_CONFLICT"


def test_r7_existing_signed_readback_and_summary_expose_no_bet_truth():
    from runtime.local_race_key_gate import readback_final,main
    src=inspect.getsource(readback_final)
    assert "attest_ticket_decision(artifact, final_verified=True)" in src
    assert "'ticket_disposition':ticket_disposition" in src
    summary=inspect.getsource(main)
    assert "Ticket disposition:" in summary
    assert "actual purchase UNKNOWN" in summary

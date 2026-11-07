"""Read-only FNB R7 ticket/no-bet terminal attestation.

This helper may be called ONLY after the existing external signature and
temporal check of FINAL. It never issues a purchase, settlement, PFS, Owner,
Consumer, OOS or Delivery authorization. An empty array is not a NO-BET until
Capital and canonical ticket semantics independently agree.
"""
from __future__ import annotations

PROFILE="KM-FNB-R7-FINAL-TICKET-NOBET-DISPOSITION-v1"


def attest_ticket_decision(artifact: dict | None, *, final_verified: bool) -> dict:
    base={"profile":PROFILE,"pfs":None, "actual_purchase_pfs":None,
          "pfs_reason":"NO_VERIFIED_RESULT_SETTLEMENT_OR_ACTUAL_PURCHASE",
          "recipient_delivery_ack":"NOT_VERIFIED",
          "actual_purchase":"NOT_VERIFIED",
          "no_bet_calculated":False,
          "prediction_or_ticket_reexecution":False}
    if final_verified is not True:
        return {**base, "status":"UNVERIFIED_FINAL_NOT_A_CALCULATED_NO_BET",
                "ticket_count":None,"recommendation_investment":None}
    if not isinstance(artifact,dict):
        return {**base, "status":"FINAL_ARTIFACT_MISSING",
                "ticket_count":None,"recommendation_investment":None}
    ticket=artifact.get("final_ticket")
    capital=artifact.get("capital_policy_decision")
    if not isinstance(ticket,dict) or not isinstance(capital,dict):
        return {**base,"status":"CANONICAL_TICKET_OR_CAPITAL_MISSING",
                "ticket_count":None,"recommendation_investment":None}
    rows=ticket.get("tickets")
    if not isinstance(rows,list) or ticket.get("finalized") is not True:
        return {**base,"status":"CANONICAL_FINAL_TICKETS_NOT_VERIFIED",
                "ticket_count":None,"recommendation_investment":None}
    stakes=[]
    for row in rows:
        if (not isinstance(row,dict) or type(row.get("stake")) is not int
                or row["stake"]<=0 or not isinstance(row.get("selection"),list)
                or len(set(map(str,row["selection"]))) != len(row["selection"])):
            return {**base,"status":"INVALID_CANONICAL_TICKET_CELLS",
                    "ticket_count":len(rows),"recommendation_investment":None}
        stakes.append(row["stake"])
    total=sum(stakes)
    if type(ticket.get("total_investment")) is not int or ticket["total_investment"]!=total:
        return {**base,"status":"TICKET_TOTAL_STAKE_MISMATCH",
                "ticket_count":len(rows),"recommendation_investment":total}
    nb_ticket=ticket.get("no_bet") is True
    nb_capital=capital.get("no_bet") is True
    if len(rows)==0:
        if (nb_ticket and nb_capital and total==0
                and isinstance(capital.get("reason"),str) and capital["reason"].strip()):
            return {**base,"status":"VERIFIED_FROZEN_RECOMMENDATION_NO_BET",
                    "no_bet_calculated":True, "ticket_count":0,
                    "recommendation_investment":0,
                    "no_bet_reason":capital["reason"],
                    "pfs_reason":"NO_BET_ZERO_INVESTMENT_PFS_NULL"}
        return {**base,"status":"ZERO_TICKETS_WITHOUT_CONFIRMED_CAPITAL_NO_BET",
                "ticket_count":0,"recommendation_investment":0}
    if nb_ticket or nb_capital:
        return {**base,"status":"TICKETS_PRESENT_BUT_CAPITAL_NO_BET_CONFLICT",
                "ticket_count":len(rows),"recommendation_investment":total}
    return {**base,"status":"VERIFIED_FROZEN_RECOMMENDATION_TICKETS",
            "ticket_count":len(rows),"recommendation_investment":total,
            "paper_only":capital.get("mode")=="RECOMMENDATION_ONLY"}

"""FNB dual-owner display verifier, read-only and never an ACK."""
def audit_presentation(artifact, runner_ids):
    pkg=artifact.get("final_prediction_package") or {}
    rank=pkg.get("ranking")
    roles=pkg.get("roles")
    required=set(str(x) for x in runner_ids)
    missing=[]
    if not isinstance(rank,list) or set(map(str,rank))!=required or len(rank)!=len(required):
        missing.append("ALL_RUNNER_RANKING_MISSING")
    if not isinstance(roles,dict) or set(roles)!=required or any(
            not isinstance(v,list) or not set(v)<=set(("W","P2","P3"))
            for v in roles.values()):
        missing.append("ALL_RUNNER_ROLE_MATRIX_MISSING")
    if not required:
        missing.append("OFFICIAL_RUNNER_UNIVERSE_NOT_PROVEN")
    numerical=pkg.get("numerical_cells_by_runner")
    if (not isinstance(numerical,dict) or set(numerical)!=required
            or any(not isinstance(v,dict) or len(v)!=29
                   for v in numerical.values())):
        missing.append("ALL_RUNNERS_29_INDICES_NOT_MATERIALIZED")
    ticket=artifact.get("final_ticket") or {}
    rows=ticket.get("tickets")
    if not isinstance(rows,list):
        missing.append("CANONICAL_TICKET_ARRAY_MISSING")
        rows=[]
    types={t.get("bet_type") for t in rows if isinstance(t,dict)}
    for name in ("EXACTA","TRIO","TRIFECTA"):
        if name not in types and ticket.get("no_bet") is not True:
            missing.append("BET_TYPE_NOT_PRESENT:"+name)
    owners=pkg.get("owner_method_portfolios")
    if not isinstance(owners,dict) or set(owners)!={"BASELINE","CANDIDATE"}:
        missing.append("DUAL_OWNER_SIX_METHODS_MISSING")
    elif any(not isinstance(v,dict) or
             set(v)!={"EXACTA","TRIO","TRIFECTA"} for v in owners.values()):
        missing.append("DUAL_OWNER_METHODS_INCOMPLETE")
    return {"status":"DISPLAY_FIELDS_OBSERVED_DELIVERY_UNPROVEN" if not missing
            else "DELIVERY_PRESENTATION_INCOMPLETE",
            "missing":missing,"prestart_delivery_pass":False,
            "recipient_ack":False,"user_received_at":None,
            "signed_source_or_calculation_verified_here":False}

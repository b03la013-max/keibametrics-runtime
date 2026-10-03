from __future__ import annotations
import hashlib, json, pathlib

PROFILE="KM-FAMILY-CAPITAL-COMPATIBILITY-v1.0-20260921"
DEFAULT_PROFILE_ID="KM-FAMILY-USER-CAPITAL-DEFAULT-20261003-R1"
DEFAULT_PROFILE_PATH=pathlib.Path(__file__).resolve().parents[1] / "profiles" / "family_user_capital_default_20261003_R1.json"

class CapitalPolicyError(ValueError):
    pass

def _sha(x):
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def _load_family_default()->dict:
    try:
        obj=json.loads(DEFAULT_PROFILE_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        raise CapitalPolicyError(f"FAMILY_CAPITAL_DEFAULT_LOAD_FAILED:{e}")
    if str(obj.get("profile") or "")!=DEFAULT_PROFILE_ID:
        raise CapitalPolicyError("FAMILY_CAPITAL_DEFAULT_PROFILE_MISMATCH")
    p=obj.get("default_capital_policy")
    if not isinstance(p,dict):
        raise CapitalPolicyError("FAMILY_CAPITAL_DEFAULT_POLICY_MISSING")
    return dict(p)

def resolve_capital_policy(request:dict, mec:dict)->dict:
    required=int(mec.get("minimum_required_capital") or 0)
    if required<0:
        raise CapitalPolicyError("BAD_MEC_REQUIRED_CAPITAL")

    p=request.get("capital_policy")
    budget_source="REQUEST_EXPLICIT"
    if p is None:
        p=_load_family_default()
        budget_source="FAMILY_USER_DEFAULT"
    if not isinstance(p,dict):
        raise CapitalPolicyError("CAPITAL_POLICY_NOT_OBJECT")
    mode=str(p.get("mode") or "").upper()

    if mode=="RECOMMENDATION_ONLY":
        out={
          "profile":PROFILE,
          "mode":mode,
          "required_capital":required,
          "capital_limit":None,
          "compatibility":"NOT_EVALUATED_NO_BANKROLL_ASSUMPTION",
          "decision":"EXECUTE_RECOMMENDATION_PORTFOLIO",
          "no_bet":False,
          "paper_only":False,
          "reason":"Recommendation-only mode was explicitly requested; no race-budget compatibility decision is made.",
          "budget_source":budget_source,
          "budget_fill_required":False,
          "final_ticket_stake_unit_yen":100,
          "internal_allocation_precision":"DECIMAL_ALLOWED",
          "ticket_count_limit":None,
          "unused_budget_must_not_expand_tickets":True,
        }
    elif mode=="HARD_RACE_BUDGET":
        cap=p.get("max_race_capital")
        if not isinstance(cap,int) or cap<0 or cap%100:
            raise CapitalPolicyError("MAX_RACE_CAPITAL_MUST_BE_NONNEGATIVE_100_YEN_INCREMENT")
        action=str(p.get("insufficient_action") or "NO_BET").upper()
        if action not in {"NO_BET","PAPER"}:
            raise CapitalPolicyError("INSUFFICIENT_ACTION_MUST_BE_NO_BET_OR_PAPER")
        unit=p.get("final_ticket_stake_unit_yen",100)
        if not isinstance(unit,int) or unit<=0 or unit%100:
            raise CapitalPolicyError("FINAL_TICKET_STAKE_UNIT_MUST_BE_POSITIVE_100_YEN_INCREMENT")
        budget_fill_required=bool(p.get("budget_fill_required",False))
        if budget_fill_required:
            raise CapitalPolicyError("BUDGET_FILL_REQUIRED_FORBIDDEN_BY_FAMILY_DEFAULT_SEMANTICS")
        ticket_limit=cap//unit if unit else None
        common={
          "profile":PROFILE,
          "mode":mode,
          "required_capital":required,
          "capital_limit":cap,
          "budget_source":budget_source,
          "budget_fill_required":False,
          "final_ticket_stake_unit_yen":unit,
          "internal_allocation_precision":str(p.get("internal_allocation_precision") or "DECIMAL_ALLOWED"),
          "ticket_count_limit":ticket_limit,
          "unused_budget_must_not_expand_tickets":True,
          "unused_budget":max(0,cap-required),
        }
        if required<=cap:
            out={
              **common,
              "compatibility":"COMPATIBLE",
              "decision":"EXECUTE_FULL_MEC",
              "no_bet":False,
              "paper_only":False,
              "reason":"MEC minimum required capital is within the race budget. Unused budget is not spent merely to fill the cap.",
            }
        else:
            out={
              **common,
              "compatibility":"INCOMPATIBLE",
              "decision":action,
              "no_bet":True,
              "paper_only":action=="PAPER",
              "reason":"MEC minimum capital exceeds the race budget; semantic coverage is not compressed to fit budget.",
              "unused_budget":0,
            }
    else:
        raise CapitalPolicyError(f"UNSUPPORTED_CAPITAL_POLICY_MODE:{mode}")

    out["default_profile"]=DEFAULT_PROFILE_ID if budget_source=="FAMILY_USER_DEFAULT" else None
    out["mec_profile"]=mec.get("profile")
    out["mec_sha256"]=mec.get("sha256")
    out["material_coverage_ratio"]=mec.get("material_coverage_ratio")
    out["sha256"]=_sha(out)
    return out

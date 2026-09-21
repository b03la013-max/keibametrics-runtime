from __future__ import annotations
import hashlib, json

PROFILE="KM-FAMILY-CAPITAL-COMPATIBILITY-v1.0-20260921"

class CapitalPolicyError(ValueError):
    pass

def _sha(x):
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def resolve_capital_policy(request:dict, mec:dict)->dict:
    required=int(mec.get("minimum_required_capital") or 0)
    if required<0:
        raise CapitalPolicyError("BAD_MEC_REQUIRED_CAPITAL")
    p=request.get("capital_policy")
    if p is None:
        p={"mode":"RECOMMENDATION_ONLY"}
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
          "reason":"No bankroll/race budget supplied; MEC is treated as recommendation capital, not affordability proof.",
        }
    elif mode=="HARD_RACE_BUDGET":
        cap=p.get("max_race_capital")
        if not isinstance(cap,int) or cap<0 or cap%100:
            raise CapitalPolicyError("MAX_RACE_CAPITAL_MUST_BE_NONNEGATIVE_100_YEN_INCREMENT")
        action=str(p.get("insufficient_action") or "NO_BET").upper()
        if action not in {"NO_BET","PAPER"}:
            raise CapitalPolicyError("INSUFFICIENT_ACTION_MUST_BE_NO_BET_OR_PAPER")
        if required<=cap:
            out={
              "profile":PROFILE,"mode":mode,"required_capital":required,"capital_limit":cap,
              "compatibility":"COMPATIBLE","decision":"EXECUTE_FULL_MEC","no_bet":False,"paper_only":False,
              "reason":"MEC minimum required capital is within the explicit race budget.",
            }
        else:
            out={
              "profile":PROFILE,"mode":mode,"required_capital":required,"capital_limit":cap,
              "compatibility":"INCOMPATIBLE","decision":action,
              "no_bet":True,"paper_only":action=="PAPER",
              "reason":"MEC minimum capital exceeds explicit budget; semantic coverage is not compressed to fit budget.",
            }
    else:
        raise CapitalPolicyError(f"UNSUPPORTED_CAPITAL_POLICY_MODE:{mode}")

    out["mec_profile"]=mec.get("profile")
    out["mec_sha256"]=mec.get("sha256")
    out["material_coverage_ratio"]=mec.get("material_coverage_ratio")
    out["sha256"]=_sha(out)
    return out

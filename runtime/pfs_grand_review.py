from __future__ import annotations
import json, os, re, hashlib
from collections import defaultdict
from mec_r4_shadow import settle_ticket_list

PROFILE="KM-PFS-GRAND-REVIEW-v1.0-20260922"
SOURCE_PRIORITY={
    "runtime/performance_ledger": 400,
    "runtime/reviews": 300,
    "runtime/reviews_auto": 250,
    "runtime/results": 200,
}
EXCLUDE_RACE_MARKERS=("KM-ACCEPT-","TEST","T0","T1","T2","T3","T4","T5","T6","T7","T8","T9")

def _sha(x):
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def _num(v):
    try:
        return float(v)
    except Exception:
        return None

def _venue(race_id):
    u=str(race_id).upper()
    for v in ("NKY","HSN","TKY","KYO","CHK","SPP","NGT","KKR","FKS","HKD"):
        if ("-"+v+"-" in u) or (u.startswith(v+"-")):
            return v
    return "UNKNOWN"

def _date(race_id):
    m=re.search(r"(20\d{6})",str(race_id))
    return m.group(1) if m else None

def _grade_class(grade):
    u=str(grade or "").upper()
    if "POST-START" in u or "POSTSTART" in u:
        return "POST_START_REPLAY"
    if "FORMAL-PRE-RACE" in u or "FORMAL PRE-RACE" in u:
        return "FORMAL_PRE_RACE"
    if "FROZEN-OOS" in u or "LIVE-INTENT" in u:
        return "FROZEN_OOS_NONCONFORMANT"
    if "BLOCK" in u:
        return "BLOCKED"
    return "OTHER"

def _extract(path,obj):
    rid=str(obj.get("race_id") or "")
    if not rid or any(m in rid.upper() for m in EXCLUDE_RACE_MARKERS):
        return None

    inv=ret=pfs=None
    authority=None
    grade=obj.get("formal_grade")
    model_elig=obj.get("model_comparison_eligibility")
    actual="UNKNOWN"
    bet_types={}

    if path.startswith("runtime/performance_ledger/"):
        inv=_num(obj.get("investment"))
        ret=_num(obj.get("return"))
        pfs=_num(obj.get("pfs"))
        authority=obj.get("pfs_authority")
        grade=obj.get("formal_grade")
        model_elig=obj.get("model_comparison_eligibility")
    elif path.startswith("runtime/reviews"):
        measurement=obj.get("measurement") or {}
        completeness=str(measurement.get("settlement_completeness") or "").upper()
        if completeness in {"PENDING","UNKNOWN","INCOMPLETE"}:
            return None
        capital=obj.get("capital") or obj.get("settlement") or {}
        inv=_num(measurement.get("investment"))
        if inv is None: inv=_num(capital.get("total_investment") or capital.get("investment"))
        ret=_num(measurement.get("return"))
        if ret is None: ret=_num(capital.get("return") or capital.get("provisional_return"))
        pfs=_num(measurement.get("pfs"))
        if pfs is None: pfs=_num(capital.get("pfs") or capital.get("provisional_pfs"))
        authority=measurement.get("pfs_authority") or capital.get("pfs_authority")
        grade=grade or (obj.get("formal_eligibility") or {}).get("formal_grade") or (obj.get("frozen_artifact") or {}).get("formal_grade")
        model_elig=model_elig or (obj.get("formal_eligibility") or {}).get("model_comparison_eligibility")
        bt=(obj.get("settlement") or {}).get("by_bet_type") or capital.get("ticket_type_settlement") or {}
        if isinstance(bt,dict):
            for k,v in bt.items():
                if isinstance(v,dict):
                    bi=_num(v.get("investment")); br=_num(v.get("return") or v.get("payout"))
                    if bi is not None and br is not None: bet_types[str(k).upper()]={"investment":bi,"return":br}
    elif path.startswith("runtime/results/"):
        s=obj.get("settlement") or {}
        if str(s.get("status") or "").upper()!="SETTLED":
            return None
        inv=_num(s.get("total_investment"))
        ret=_num(s.get("total_payout"))
        pfs=_num(s.get("pfs"))
        if pfs is None: pfs=_num(s.get("pfs_percent"))
        authority=s.get("pfs_authority")
        fr=obj.get("frozen_prediction_ref") or {}
        grade=grade or fr.get("final_status") or fr.get("formal_grade") or fr.get("temporal_formality")
        le=obj.get("learning_event") or {}
        model_elig=model_elig or le.get("model_comparison_eligibility")
        for row in s.get("bet_type_summary") or s.get("by_bet_type") or []:
            if isinstance(row,dict):
                k=str(row.get("bet_type") or "").upper()
                bi=_num(row.get("investment")); br=_num(row.get("payout") or row.get("return"))
                if k and bi is not None and br is not None: bet_types[k]={"investment":bi,"return":br}
        note=str(s.get("note") or "").upper()
        actual="UNVERIFIED" if "ACTUAL" in note and ("UNVERIFIED" in note or "NOT VERIFIED" in note) else "UNKNOWN"

    if inv is None or ret is None:
        return None
    if inv<0 or ret<0:
        return None
    if pfs is None and inv>0:
        pfs=ret/inv*100.0

    return {
        "race_id":rid,
        "date":_date(rid),
        "venue":_venue(rid),
        "source_path":path,
        "source_priority":max((v for k,v in SOURCE_PRIORITY.items() if path.startswith(k)),default=0),
        "formal_grade":grade,
        "formal_class":_grade_class(grade),
        "model_comparison_eligibility":model_elig,
        "pfs_authority":authority,
        "actual_ticket_status":actual,
        "investment":inv,
        "return":ret,
        "profit_loss":ret-inv,
        "pfs":pfs,
        "no_bet":inv==0,
        "hit":ret>0,
        "hit_but_loss":ret>0 and ret<inv,
        "bet_types":bet_types,
    }

def _json_files(root):
    for base in SOURCE_PRIORITY:
        if not os.path.isdir(base): continue
        for fn in sorted(os.listdir(base)):
            if fn.endswith(".json"):
                yield os.path.join(base,fn)

def canonical_records():
    chosen={}
    supplements=defaultdict(list)
    for path in _json_files("."):
        try:
            with open(path,encoding="utf-8") as f: obj=json.load(f)
        except Exception:
            continue
        rec=_extract(path,obj)
        if not rec: continue
        rid=rec["race_id"]
        supplements[rid].append(rec)
        if rid not in chosen or rec["source_priority"]>chosen[rid]["source_priority"]:
            chosen[rid]=rec
    # Merge bet-type detail from lower-priority reviews/results without changing canonical money totals.
    for rid,rec in chosen.items():
        merged={}
        if any(str(x.get("actual_ticket_status") or "").upper()=="UNVERIFIED" for x in supplements[rid]):
            rec["actual_ticket_status"]="UNVERIFIED"
        for x in sorted(supplements[rid],key=lambda z:z["source_priority"],reverse=True):
            for bt,v in (x.get("bet_types") or {}).items():
                merged.setdefault(bt,v)
        rec["bet_types"]=merged
    return sorted(chosen.values(),key=lambda x:(x.get("date") or "",x["race_id"]))

def _aggregate(rows):
    bet=[r for r in rows if r["investment"]>0]
    inv=sum(r["investment"] for r in bet)
    ret=sum(r["return"] for r in bet)
    return {
        "race_count":len(rows),
        "bet_race_count":len(bet),
        "no_bet_count":sum(r["investment"]==0 for r in rows),
        "investment":round(inv,2),
        "return":round(ret,2),
        "profit_loss":round(ret-inv,2),
        "investment_weighted_pfs":round(ret/inv*100.0,9) if inv else None,
        "hit_race_count":sum(r["return"]>0 for r in bet),
        "hit_rate":round(sum(r["return"]>0 for r in bet)/len(bet)*100.0,6) if bet else None,
        "hit_but_loss_count":sum(r["hit_but_loss"] for r in bet),
        "hit_but_loss_rate":round(sum(r["hit_but_loss"] for r in bet)/len(bet)*100.0,6) if bet else None,
    }

def _max_drawdown(rows):
    equity=0.0
    peak=0.0
    max_dd=0.0
    losing_streak=max_losing=0
    for r in sorted(rows,key=lambda x:(x.get("date") or "",x.get("race_id") or "")):
        pl=float(r.get("profit_loss") or 0)
        equity += pl
        peak=max(peak,equity)
        max_dd=max(max_dd,peak-equity)
        if pl<0:
            losing_streak+=1
            max_losing=max(max_losing,losing_streak)
        else:
            losing_streak=0
    return round(max_dd,2),max_losing

def _robustness(rows):
    bet=sorted([r for r in rows if r["investment"]>0],key=lambda x:x["return"],reverse=True)
    def ex(k):
        return _aggregate(bet[k:]) if len(bet)>k else _aggregate([])
    total_return=sum(r["return"] for r in bet)
    dd,streak=_max_drawdown(rows)
    return {
        "largest_return_race":bet[0]["race_id"] if bet else None,
        "largest_return":bet[0]["return"] if bet else None,
        "largest_return_share_pct":round((bet[0]["return"]/total_return*100.0),6) if bet and total_return else None,
        "excluding_largest_return":ex(1),
        "excluding_top3_returns":ex(3),
        "max_drawdown":dd,
        "max_losing_streak":streak,
    }
def _by(rows,key):
    groups=defaultdict(list)
    for r in rows: groups[str(r.get(key) or "UNKNOWN")].append(r)
    return {k:_aggregate(v) for k,v in sorted(groups.items())}

def _bet_type(rows):
    sums=defaultdict(lambda:[0.0,0.0,0])
    for r in rows:
        for bt,x in (r.get("bet_types") or {}).items():
            sums[bt][0]+=float(x["investment"])
            sums[bt][1]+=float(x["return"])
            sums[bt][2]+=1
    out={}
    for bt,(inv,ret,n) in sorted(sums.items()):
        out[bt]={
            "race_observation_count":n,
            "investment":round(inv,2),
            "return":round(ret,2),
            "profit_loss":round(ret-inv,2),
            "pfs":round(ret/inv*100.0,9) if inv else None,
        }
    return out

def _tier_pfs():
    """Prospective/structured MEC tier economics where immutable FINAL has tier metadata.

    Historical races without frozen tier metadata are deliberately omitted rather than inferred.
    """
    root="runtime/final_artifacts"
    rows=defaultdict(list)
    races=[]
    if not os.path.isdir(root):
        return {"status":"NO_STRUCTURED_TIER_DATA","races":[],"tiers":{}}
    for fn in sorted(os.listdir(root)):
        if not fn.endswith(".json"): continue
        path=os.path.join(root,fn)
        try:
            final=json.load(open(path,encoding="utf-8"))
        except Exception:
            continue
        rid=str(final.get("race_id") or "")
        result_path=os.path.join("runtime","results",rid+".json")
        if not rid or not os.path.exists(result_path):
            continue
        tickets=(final.get("final_ticket") or {}).get("tickets") or []
        tiers=sorted({str(x.get("mec_tier") or x.get("tier") or "").upper() for x in tickets if x.get("mec_tier") or x.get("tier")})
        if not tiers:
            continue
        try:
            result=json.load(open(result_path,encoding="utf-8"))
        except Exception:
            continue
        if str((result.get("settlement") or {}).get("status") or "").upper()!="SETTLED":
            continue
        race={"race_id":rid,"tiers":{}}
        for tier in tiers:
            subset=[x for x in tickets if str(x.get("mec_tier") or x.get("tier") or "").upper()==tier]
            if not subset: continue
            try:
                s=settle_ticket_list(subset,result)
            except Exception:
                continue
            if s.get("status")!="SETTLED":
                continue
            row={"race_id":rid,**{k:s.get(k) for k in ("investment","return","profit_loss","pfs","ticket_count")}}
            rows[tier].append(row)
            race["tiers"][tier]=row
        if race["tiers"]:
            races.append(race)
    agg={}
    for tier,xs in sorted(rows.items()):
        inv=sum(float(x.get("investment") or 0) for x in xs)
        ret=sum(float(x.get("return") or 0) for x in xs)
        agg[tier]={
            "race_count":len(xs),
            "investment":round(inv,2),
            "return":round(ret,2),
            "profit_loss":round(ret-inv,2),
            "pfs":round(ret/inv*100.0,9) if inv else None,
        }
    return {
        "status":"PARTIAL_STRUCTURED_HISTORY_ONLY",
        "note":"Only immutable FINAL races with explicit frozen mec_tier metadata are included; missing historical tiers are not inferred.",
        "races":races,
        "tiers":agg,
    }

def build_report():
    rows=canonical_records()
    formal=[r for r in rows if r["formal_class"]=="FORMAL_PRE_RACE"]
    eligible=[r for r in formal if str(r.get("model_comparison_eligibility") or "").upper()=="ELIGIBLE"]
    all_frozen=[r for r in rows if str(r.get("pfs_authority") or "").upper().startswith("FROZEN")]
    report={
        "profile":PROFILE,
        "status":"MEASUREMENT-BASELINE / NON-AUTHORITY / NO-PRODUCTION-CHANGE",
        "method":"Canonical race_id dedupe; Performance Ledger > Formal Review > Auto Review > Result. Investment-weighted PFS.",
        "production_effect":"NONE",
        "records":rows,
        "cohorts":{
            "ALL_FROZEN_RECOMMENDATION":_aggregate(all_frozen),
            "FORMAL_PRE_RACE":_aggregate(formal),
            "MODEL_COMPARISON_ELIGIBLE":_aggregate(eligible),
        },
        "robustness":{
            "ALL_FROZEN_RECOMMENDATION":_robustness(all_frozen),
            "FORMAL_PRE_RACE":_robustness(formal),
            "MODEL_COMPARISON_ELIGIBLE":_robustness(eligible),
        },
        "formal_pre_race_by_venue":_by(formal,"venue"),
        "all_by_formal_class":_by(rows,"formal_class"),
        "formal_pre_race_bet_type":_bet_type(formal),
        "actual_pfs":{
            "status":"NOT_AGGREGATED_UNLESS_PURCHASE_VERIFIED",
            "verified_race_count":sum(str(r.get("actual_ticket_status")).upper()=="VERIFIED" for r in rows),
        },
        "tier_pfs":_tier_pfs(),
        "limitations":[
            "Repository contains structured individual-race records only for part of historical KeibaMetrics operation.",
            "Legacy day aggregates are not mixed into race-level totals to avoid double counting.",
            "Actual purchase is generally unverified; primary authority is Frozen Recommendation PFS.",
            "Post-start replay and nonconformant frozen races are excluded from FORMAL_PRE_RACE cohort but retained in ALL_FROZEN_RECOMMENDATION where settlement exists."
        ]
    }
    report["sha256"]=_sha(report)
    return report

def write_report(path="runtime/pfs_grand_review/current.json"):
    report=build_report()
    os.makedirs(os.path.dirname(path),exist_ok=True)
    with open(path,"w",encoding="utf-8") as f:
        json.dump(report,f,ensure_ascii=False,sort_keys=True,indent=2)
    return report

if __name__=="__main__":
    r=write_report()
    print(json.dumps({"status":"PASS","profile":r["profile"],"sha256":r["sha256"],"cohorts":r["cohorts"]},ensure_ascii=False,separators=(",",":")))

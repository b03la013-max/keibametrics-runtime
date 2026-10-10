from __future__ import annotations
import json, os, re, hashlib, glob, copy
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
    for v in ("FNB","KAW","URW","OHI","SON","KOC","SAG","MOR","MON","NGY","KSM","NKY","HSN","TKY","KYO","CHK","SPP","NGT","KKR","FKS","HKD"):
        if ("-"+v+"-" in u) or (u.startswith(v+"-")):
            return v
    return "UNKNOWN"

def _family(race_id):
    venue=_venue(race_id)
    if venue in {"FNB","KAW","URW","OHI","SON","KOC","SAG","MOR","MON","NGY","KSM"}:return "LOCAL"
    if "BAN" in str(race_id) or "OBI" in str(race_id):return "BAN"
    return "JRA" if venue!="UNKNOWN" else "UNKNOWN"

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
        authority=measurement.get("pfs_authority") or capital.get("pfs_authority") or capital.get("authority")
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
        "median_race_pfs":__import__("statistics").median([r["return"]/r["investment"]*100 for r in bet]) if bet else None,
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
        "excluding_top2_returns":ex(2),
        "excluding_top3_returns":ex(3),
        "largest_return_zeroed_keep_stakes_pfs":(total_return-(bet[0]["return"] if bet else 0))/sum(r["investment"] for r in bet)*100 if bet else None,
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
        try:
            if settle_ticket_list(tickets,result).get("status")!="SETTLED":continue
        except Exception:continue
        race={"race_id":rid,"family_id":_family(rid),"venue":_venue(rid),"tiers":{}}
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
            steps=[];previous_i=previous_r=0
            for label,selected in [("CORE",{"CORE"}),("CORE+PROTECTION",{"CORE","PROTECTION"}),("FULL",{"CORE","PROTECTION","TAIL"})]:
                inv=sum(float(v["investment"]) for k,v in race["tiers"].items() if k in selected)
                ret=sum(float(v["return"]) for k,v in race["tiers"].items() if k in selected)
                di,dr=inv-previous_i,ret-previous_r
                steps.append({"stage":label,"investment":inv,"return":ret,"added_investment":di,"added_return":dr,"marginal_pfs":dr/di*100 if di else None,"profit_loss_delta":dr-di})
                previous_i,previous_r=inv,ret
            race["marginal_capital"]=steps
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

def _candidate_ticket_key(bt,sel):
    bt=str(bt or "").upper()
    vals=[int(x) for x in (sel or [])]
    if bt=="TRIO":
        vals=sorted(vals)
    return (bt,tuple(vals))


def _candidate_automatic_settlements():
    """Read new immutable JRA RESULT→PFS ledgers without implying Actual purchase.

    Legacy source_candidate_results is a separate input path. Both sources are
    reconciled by race_id and never included in FORMAL_PRE_RACE/Production PFS.
    """
    rows=[]
    for path in sorted(glob.glob("runtime/source_candidate_oos/KM-JRA-*/settlement.json")):
        d=os.path.dirname(path)
        try:
            settlement=json.load(open(path,encoding="utf-8"))
            pre=json.load(open(os.path.join(d,"pre_result.json"),encoding="utf-8"))
            final=json.load(open(os.path.join(d,"candidate_final.json"),encoding="utf-8"))
            evaluated=json.load(open(os.path.join(d,"result_evaluation.json"),encoding="utf-8"))
        except (OSError,ValueError) as exc:
            raise ValueError("CANDIDATE_PFS_LEDGER_INCOMPLETE:"+path) from exc
        rid=str(settlement.get("race_id") or "")
        if (not rid or rid != os.path.basename(d) or rid != pre.get("race_id")
                or rid != final.get("race_id") or rid != evaluated.get("race_id")):
            raise ValueError("CANDIDATE_PFS_RACE_ID_MISMATCH:"+path)
        for obj,label in ((pre,"PRE_RESULT"),(final,"FINAL"),(settlement,"SETTLEMENT"),
                          (evaluated,"EVALUATION")):
            if str(obj.get("sha256") or "")!=_sha({k:v for k,v in obj.items() if k!="sha256"}):
                raise ValueError("CANDIDATE_PFS_"+label+"_HASH_INVALID:"+rid)
        if (pre.get("oos_eligible") is not True or
                evaluated.get("oos_eligible") is not True or
                pre.get("candidate_final_verified") is not True):
            raise ValueError("CANDIDATE_PFS_PRE_START_ELIGIBILITY_FAIL:"+rid)
        if (str(settlement.get("status"))!="SETTLED_FROZEN_CANDIDATE_RECOMMENDATION"
                or settlement.get("production_effect")!="NONE"
                or settlement.get("automatic_promotion") is not False
                or str(settlement.get("actual_purchase_status"))!="UNVERIFIED"
                or settlement.get("frozen_pre_result_sha256")!=pre["sha256"]
                or settlement.get("frozen_candidate_final_sha256")!=final["sha256"]
                or evaluated.get("settlement_sha256")!=settlement["sha256"]):
            raise ValueError("CANDIDATE_PFS_SETTLEMENT_AUTHORITY_OR_LINEAGE_MISMATCH:"+rid)
        inv=_num(settlement.get("recommended_stake_yen"))
        ret=_num(settlement.get("recommended_return_yen"))
        tickets=settlement.get("frozen_tickets") or []
        if (inv is None or ret is None or inv<=0 or ret<0 or
                round(sum(float(t.get("stake") or 0) for t in tickets),2)!=inv or
                int(settlement.get("purchased_ticket_count") or 0)!=len(tickets)):
            raise ValueError("CANDIDATE_PFS_STAKE_OR_RETURN_MISMATCH:"+rid)
        return_sum=sum(float(t.get("recommended_return") or 0) for t in tickets)
        if round(return_sum,2)!=ret:
            raise ValueError("CANDIDATE_PFS_TICKET_RETURN_MISMATCH:"+rid)
        types=defaultdict(lambda:{"investment":0.0,"return":0.0})
        for t in tickets:
            kind=str(t.get("bet_type") or "").upper()
            if kind not in {"EXACTA","TRIO","TRIFECTA"}:
                raise ValueError("CANDIDATE_PFS_TICKET_TYPE_INVALID:"+rid)
            types[kind]["investment"]+=float(t["stake"])
            types[kind]["return"]+=float(t.get("recommended_return") or 0)
        rows.append({
            "race_id":rid,"date":_date(rid),"venue":_venue(rid),"source_path":path,
            "source_priority":0,"formal_grade":"FROZEN-OOS / SOURCE-DERIVED-CANDIDATE",
            "formal_class":"FROZEN_OOS_CANDIDATE",
            "model_comparison_eligibility":"CANDIDATE_OOS_ELIGIBLE",
            "pfs_authority":"CANDIDATE-FROZEN-RECOMMENDATION-PFS",
            "actual_ticket_status":"UNVERIFIED","investment":inv,"return":ret,
            "profit_loss":ret-inv,"pfs":ret/inv*100.0,
            "no_bet":False,"hit":ret>0,"hit_but_loss":0<ret<inv,
            "bet_types":dict(types),
        })
    return rows


def _candidate_forward_records():
    root="runtime/source_candidate_results"
    rows=[]
    if not os.path.isdir(root):
        return rows
    for path in sorted(glob.glob(os.path.join(root,"*.json"))):
        try:
            obj=json.load(open(path,encoding="utf-8"))
        except Exception:
            continue
        rid=str(obj.get("race_id") or "")
        if not rid:
            continue
        oos_path=os.path.join("runtime","source_candidate_oos",rid,"result_evaluation.json")
        if not os.path.exists(oos_path):
            continue
        try:
            oos=json.load(open(oos_path,encoding="utf-8"))
        except Exception:
            continue
        if not bool(oos.get("oos_eligible")):
            continue
        s=obj.get("settlement") or {}
        if str(s.get("status") or "").upper()!="SETTLED":
            continue
        inv=_num(s.get("total_investment"))
        ret=_num(s.get("total_payout"))
        pfs=_num(s.get("pfs"))
        if inv is None or ret is None:
            continue
        if pfs is None and inv>0:
            pfs=ret/inv*100.0
        bet_types={}
        for row in s.get("bet_type_summary") or []:
            if not isinstance(row,dict):
                continue
            bt=str(row.get("bet_type") or "").upper()
            bi=_num(row.get("investment")); br=_num(row.get("payout"))
            if bt and bi is not None and br is not None:
                bet_types[bt]={"investment":bi,"return":br}
        rows.append({
            "race_id":rid,
            "date":_date(rid),
            "venue":_venue(rid),
            "source_path":path,
            "source_priority":0,
            "formal_grade":"FROZEN-OOS / SOURCE-DERIVED-CANDIDATE",
            "formal_class":"FROZEN_OOS_CANDIDATE",
            "model_comparison_eligibility":"CANDIDATE_OOS_ELIGIBLE",
            "pfs_authority":s.get("pfs_authority"),
            "actual_ticket_status":s.get("actual_ticket_status") or "UNVERIFIED",
            "investment":inv,
            "return":ret,
            "profit_loss":ret-inv,
            "pfs":pfs,
            "no_bet":inv==0,
            "hit":ret>0,
            "hit_but_loss":ret>0 and ret<inv,
            "bet_types":bet_types,
        })
    # New postresult automation writes per-race settlement.json instead of the
    # legacy source_candidate_results path. Without merging both lanes here,
    # headline and robust PFS remain stale while the OOS tracker advances.
    by_id={x["race_id"]:x for x in rows}
    for row in _candidate_automatic_settlements():
        previous=by_id.get(row["race_id"])
        if previous is not None:
            if (round(previous["investment"],2)!=round(row["investment"],2)
                    or round(previous["return"],2)!=round(row["return"],2)):
                raise ValueError("CANDIDATE_PFS_DOUBLE_SOURCE_CONFLICT:"+row["race_id"])
            continue
        by_id[row["race_id"]]=row
    return [by_id[k] for k in sorted(by_id)]

def _candidate_mec_capital_density():
    root="runtime/source_candidate_oos"
    tiers=defaultdict(lambda:{"ticket_count":0,"capital":0.0})
    bet_types=defaultdict(lambda:{"ticket_count":0,"capital":0.0})
    races=[]
    eligible=0
    if not os.path.isdir(root):
        return {"status":"NO_CANDIDATE_OOS_DATA","eligible_race_count":0,"tiers":{},"bet_types":{},"races":[]}
    for d in sorted(glob.glob(os.path.join(root,"*"))):
        if not os.path.isdir(d):
            continue
        eval_path=os.path.join(d,"result_evaluation.json")
        final_path=os.path.join(d,"candidate_final.json")
        if not (os.path.exists(eval_path) and os.path.exists(final_path)):
            continue
        try:
            ev=json.load(open(eval_path,encoding="utf-8"))
            final=json.load(open(final_path,encoding="utf-8"))
        except Exception:
            continue
        if not bool(ev.get("oos_eligible")):
            continue
        eligible+=1
        rid=str(final.get("race_id") or os.path.basename(d))
        race={"race_id":rid,"tiers":{},"bet_types":{}}
        for t in ((final.get("mec") or {}).get("tickets") or []):
            tier=str(t.get("mec_tier") or t.get("tier") or "UNKNOWN").upper()
            bt=str(t.get("bet_type") or "UNKNOWN").upper()
            stake=float(t.get("stake") or 0)
            tiers[tier]["ticket_count"]+=1; tiers[tier]["capital"]+=stake
            bet_types[bt]["ticket_count"]+=1; bet_types[bt]["capital"]+=stake
            race["tiers"].setdefault(tier,{"ticket_count":0,"capital":0.0})
            race["tiers"][tier]["ticket_count"]+=1; race["tiers"][tier]["capital"]+=stake
            race["bet_types"].setdefault(bt,{"ticket_count":0,"capital":0.0})
            race["bet_types"][bt]["ticket_count"]+=1; race["bet_types"][bt]["capital"]+=stake
        races.append(race)
    total=sum(x["capital"] for x in tiers.values())
    tout={}
    for k,v in sorted(tiers.items()):
        tout[k]={
            "ticket_count":int(v["ticket_count"]),
            "capital":round(v["capital"],2),
            "capital_share_pct":round(v["capital"]/total*100.0,6) if total else None,
        }
    bout={k:{"ticket_count":int(v["ticket_count"]),"capital":round(v["capital"],2)}
          for k,v in sorted(bet_types.items())}
    return {
        "status":"CANDIDATE-OOS-MEASUREMENT / NON-PRODUCTION",
        "eligible_race_count":eligible,
        "total_capital":round(total,2),
        "tiers":tout,
        "bet_types":bout,
        "races":races,
    }

def _candidate_tier_pfs(candidate_rows):
    tiers=defaultdict(lambda:{"investment":0.0,"return":0.0,"ticket_count":0})
    races=[]
    for rec in candidate_rows:
        rid=rec["race_id"]
        final_path=os.path.join("runtime","source_candidate_oos",rid,"candidate_final.json")
        result_path=os.path.join("runtime","source_candidate_results",rid+".json")
        if not (os.path.exists(final_path) and os.path.exists(result_path)):
            continue
        try:
            final=json.load(open(final_path,encoding="utf-8"))
            result=json.load(open(result_path,encoding="utf-8"))
        except Exception:
            continue
        ticket_tier={}
        race_tiers=defaultdict(lambda:{"investment":0.0,"return":0.0,"ticket_count":0})
        for t in ((final.get("mec") or {}).get("tickets") or []):
            tier=str(t.get("mec_tier") or t.get("tier") or "UNKNOWN").upper()
            k=_candidate_ticket_key(t.get("bet_type"),t.get("selection"))
            stake=float(t.get("stake") or 0)
            ticket_tier[k]=tier
            tiers[tier]["investment"]+=stake; tiers[tier]["ticket_count"]+=1
            race_tiers[tier]["investment"]+=stake; race_tiers[tier]["ticket_count"]+=1
        for w in ((result.get("settlement") or {}).get("winning_tickets") or []):
            k=_candidate_ticket_key(w.get("bet_type"),w.get("selection"))
            tier=ticket_tier.get(k)
            if not tier:
                continue
            payout=float(w.get("payout") or 0)
            tiers[tier]["return"]+=payout
            race_tiers[tier]["return"]+=payout
        race_out={}
        for tier,x in sorted(race_tiers.items()):
            inv=x["investment"]; ret=x["return"]
            race_out[tier]={
                "investment":round(inv,2),
                "return":round(ret,2),
                "profit_loss":round(ret-inv,2),
                "pfs":round(ret/inv*100.0,9) if inv else None,
                "ticket_count":int(x["ticket_count"]),
            }
        races.append({"race_id":rid,"tiers":race_out})
    out={}
    for tier,x in sorted(tiers.items()):
        inv=x["investment"]; ret=x["return"]
        out[tier]={
            "investment":round(inv,2),
            "return":round(ret,2),
            "profit_loss":round(ret-inv,2),
            "pfs":round(ret/inv*100.0,9) if inv else None,
            "ticket_count":int(x["ticket_count"]),
        }
    return {
        "status":"CANDIDATE-FROZEN-RECOMMENDATION-TIER-PFS / NON-PRODUCTION",
        "note":"Uses only OOS-eligible Source-Derived Candidate settlements and the frozen Candidate MEC tier on the exact recommended ticket. Actual purchase remains separate.",
        "tiers":out,
        "races":races,
    }

def build_report():
    rows=canonical_records()
    actual_rows,actual_held=actual_purchase_records()
    candidate_rows=_candidate_forward_records()
    candidate_density=_candidate_mec_capital_density()
    formal=[r for r in rows if r["formal_class"]=="FORMAL_PRE_RACE"]
    eligible=[r for r in formal if str(r.get("model_comparison_eligibility") or "").upper()=="ELIGIBLE"]
    all_frozen=[r for r in rows if str(r.get("pfs_authority") or "").upper().startswith("FROZEN")]
    for row in all_frozen:row["family_id"]=_family(row["race_id"])
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
        "frozen_by_family":{f:{"aggregate":_aggregate([r for r in all_frozen if r["family_id"]==f]),"robustness":_robustness([r for r in all_frozen if r["family_id"]==f]),"by_venue":_by([r for r in all_frozen if r["family_id"]==f],"venue"),"by_formal_class":_by([r for r in all_frozen if r["family_id"]==f],"formal_class"),"by_bet_type":_bet_type([r for r in all_frozen if r["family_id"]==f])} for f in ["JRA","LOCAL","BAN","UNKNOWN"]},
        "actual_pfs":{
            "status":"MEASURED" if actual_rows else "NO_VERIFIED_SETTLED_PURCHASES",
            "verified_race_count":len(actual_rows),"status":"VERIFIED_DATA" if actual_rows else "UNKNOWN / NO VERIFIED PURCHASE","records":actual_rows,"held":actual_held,
            "aggregate":_aggregate(actual_rows),"robustness":_robustness(actual_rows),
            "by_venue":_by(actual_rows,"venue"),"bet_type":_bet_type(actual_rows),
        },
        "tier_pfs":_tier_pfs(),
        "candidate_forward_oos":{
            "status":"MEASUREMENT-ONLY / NON-PRODUCTION / NO-AUTO-PROMOTION",
            "production_effect":"NONE",
            "eligible_race_count":candidate_density.get("eligible_race_count"),
            "settled_race_count":len(candidate_rows),
            "settlement_coverage_pct":round(len(candidate_rows)/candidate_density.get("eligible_race_count")*100.0,6) if candidate_density.get("eligible_race_count") else None,
            "aggregate":_aggregate(candidate_rows),
            "robustness":_robustness(candidate_rows),
            "by_venue":_by(candidate_rows,"venue"),
            "bet_type":_bet_type(candidate_rows),
            "mec_capital_density":candidate_density,
            "tier_pfs":_candidate_tier_pfs(candidate_rows),
        },
        "limitations":[
            "Repository contains structured individual-race records only for part of historical KeibaMetrics operation.",
            "Legacy day aggregates are not mixed into race-level totals to avoid double counting.",
            "Actual purchase is generally unverified; primary authority is Frozen Recommendation PFS.",
            "Post-start replay and nonconformant frozen races are excluded from FORMAL_PRE_RACE cohort but retained in ALL_FROZEN_RECOMMENDATION where settlement exists.",
            "Source-Derived Candidate OOS is reported in a separate candidate_forward_oos block and is never merged into Production/Formal PFS cohorts.",
            "Candidate tier PFS is Frozen Recommendation PFS, not verified Actual Purchase PFS."
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


def actual_purchase_records(root="runtime/actual_purchases", *, result_overrides=None):
    """Explicit receipt/user-confirmed purchases only; never infer from FINAL.

    Reads complete race purchase ledgers. Incomplete/error ledgers remain visible
    as held records; pending settlement is not a zero return.
    """
    from datetime import datetime
    records=[];held=[]
    seen=set()
    paths=sorted(glob.glob(os.path.join(root,"*.json")))
    race_counts={}
    for candidate in paths:
        try:
            race=str(json.load(open(candidate,encoding="utf-8")).get("race_id") or "")
            race_counts[race]=race_counts.get(race,0)+1
        except Exception:pass
    for path in paths:
        rid=None
        try:
            obj=json.load(open(path,encoding="utf-8"));rid=str(obj.get("race_id") or "")
            if not rid or rid in seen or race_counts.get(rid,0)>1:raise ValueError("DUPLICATE_OR_MISSING_RACE_ID")
            if obj.get("purchase_verified") is not True or obj.get("ledger_complete") is not True or not obj.get("verification_ref"):
                raise ValueError("PURCHASE_PROOF_OR_COMPLETE_LEDGER_REQUIRED")
            post=datetime.fromisoformat(obj["scheduled_post_at"].replace("Z","+00:00"))
            tickets=[];refs=set();refund=0;failed=0
            for event in obj.get("purchases") or []:
                pid=event.get("purchase_id")
                if not pid or pid in refs:raise ValueError("DUPLICATE_OR_MISSING_PURCHASE_ID")
                refs.add(pid)
                ts=datetime.fromisoformat(event["timestamp"].replace("Z","+00:00"))
                if ts>=post:raise ValueError("PURCHASE_NOT_PRE_RACE")
                if event.get("success") is False:failed+=1;continue
                if event.get("success") is not True or not event.get("proof_ref"):raise ValueError("PURCHASE_SUCCESS_PROOF_REQUIRED")
                t=event["ticket"];stake=t.get("stake")
                if isinstance(stake,bool) or not isinstance(stake,int) or stake<=0 or stake%100:raise ValueError("INVALID_PURCHASE_STAKE")
                bt=str(t.get("bet_type") or "").upper();sel=t.get("selection") or []
                if bt not in {"EXACTA","TRIO","TRIFECTA"} or len(sel)!=(2 if bt=="EXACTA" else 3) or len(set(sel))!=len(sel):raise ValueError("INVALID_PURCHASE_TICKET")
                if any(isinstance(x,bool) or not isinstance(x,int) or x<=0 for x in sel):raise ValueError("INVALID_HORSE_ID")
                rf=event.get("refund",0)
                if isinstance(rf,bool) or not isinstance(rf,int) or rf<0 or rf>stake or rf%100 or (rf and not event.get("refund_proof_ref")):raise ValueError("INVALID_REFUND")
                refund+=rf
                if stake-rf:tickets.append({**t,"stake":stake-rf})
            seen.add(rid)
            rp=os.path.join("runtime","results",rid+".json")
            if rid in (result_overrides or {}):
                result=result_overrides[rid]
            elif os.path.isfile(rp):
                result=json.load(open(rp,encoding="utf-8"))
            else:raise ValueError("PURCHASE_CONFIRMED_SETTLEMENT_PENDING")
            if result.get("race_id")!=rid:raise ValueError("RESULT_RACE_MISMATCH")
            if str((result.get("settlement") or {}).get("status")).upper() not in {"SETTLED","COMPLETE"}:raise ValueError("OFFICIAL_SETTLEMENT_PENDING")
            settled=settle_ticket_list(tickets,result)
            if settled.get("status")!="SETTLED":raise ValueError("ACTUAL_PAYOUT_MISSING")
            inv=settled["investment"];ret=settled["return"]
            records.append({"race_id":rid,"date":_date(rid),"venue":_venue(rid),
                            "pfs_authority":"ACTUAL-PFS","actual_ticket_status":"VERIFIED",
                            "verification_ref":obj["verification_ref"],"purchase_count":len(refs),
                            "failed_purchase_count":failed,"refund":refund,"investment":inv,"return":ret,
                            "profit_loss":ret-inv,"pfs":ret/inv*100 if inv else None,
                            "hit_but_loss":0<ret<inv,"bet_types":settled.get("by_bet_type") or {},
                            "source_path":path})
        except Exception as e:
            held.append({"race_id":rid,"source_path":path,"status":"HOLD_ACTUAL_PFS","reason":str(e)})
    return records,held




def _capital_dt(x):
    from datetime import datetime
    return datetime.fromisoformat(str(x).replace("Z","+00:00"))

def capital_arms(final,budget,*,request,generated_at,scheduled_post_at):
    """Tier ablation with equal ACTUAL spend; no ranking, AKI or odds weights."""
    if _capital_dt(generated_at)>=_capital_dt(scheduled_post_at):raise ValueError('NOT_PRE_RACE')
    if isinstance(budget,bool) or not isinstance(budget,int) or budget<100 or budget%100:raise ValueError('BUDGET_UNIT_INVALID')
    art=final.get('artifact') or final
    if not request.get('race_id') or _capital_dt(request['scheduled_post_at'])!=_capital_dt(scheduled_post_at):raise ValueError('RACE_SCHEDULE_BINDING_REQUIRED')
    universe={int(x['runner_id']) for x in request.get('runners') or [] if not x.get('scratched') and not x.get('excluded')}
    if not universe:raise ValueError('RUNNER_UNIVERSE_REQUIRED')
    freeze=art.get('final_freeze_timestamp')
    if not freeze or _capital_dt(freeze)>_capital_dt(generated_at) or _capital_dt(freeze)>=_capital_dt(scheduled_post_at):raise ValueError('FINAL_NOT_PRE_RACE_FROZEN')
    tickets=copy.deepcopy((art.get('final_ticket') or {}).get('tickets') or [])
    keys=[]
    for t in tickets:
        bt=t['bet_type'];sel=[int(x) for x in t['selection']]
        if bt not in {'EXACTA','TRIO','TRIFECTA'} or len(sel)!=(2 if bt=='EXACTA' else 3) or len(sel)!=len(set(sel)):raise ValueError('INVALID_TICKET')
        if not set(sel)<=universe:raise ValueError('RUNNER_UNIVERSE_VIOLATION')
        k=(bt,tuple(sorted(sel) if bt=='TRIO' else sel))
        if k in keys:raise ValueError('DUPLICATE_TICKET')
        keys.append(k)
        if isinstance(t.get('stake'),bool) or not isinstance(t.get('stake'),int) or t['stake']<=0 or t['stake']%100:raise ValueError('INVALID_STAKE')
    arms={'PRODUCTION':{'tickets':tickets,'investment':sum(t['stake'] for t in tickets)}}
    for name,tiers in [('CONSERVATIVE',{'CORE'}),('BALANCED',{'CORE','PROTECTION'}),('WIDE',{'CORE','PROTECTION','TAIL'})]:
        subset=[copy.deepcopy(t) for t in tickets if str(t.get('mec_tier') or t.get('tier')).upper() in tiers]
        if not subset or len(subset)>budget//100 or any(str(t.get('mec_tier') or t.get('tier')).upper() not in {'CORE','PROTECTION','TAIL'} for t in tickets):
            arms[name]={'status':'HOLD_SHADOW','reason':'MISSING_TIER_OR_INSUFFICIENT_MINIMUM_BUDGET'};continue
        # Existing nominal stakes are allocation ratios, not likelihoods.
        remainder=budget//100-len(subset);den=sum(t['stake'] for t in subset)
        units=[1+(remainder*t['stake']//den) for t in subset]
        left=budget//100-sum(units)
        order=sorted(range(len(subset)),key=lambda i:(-(remainder*subset[i]['stake']%den),keys[tickets.index(subset[i])]))
        for i in order[:left]:units[i]+=1
        for t,n in zip(subset,units):t['stake']=n*100
        arms[name]={'status':'FROZEN_SHADOW','tickets':subset,'investment':sum(t['stake'] for t in subset)}
    return {'status':'PRE-RACE-CAPITAL-SHADOW','generated_at':generated_at,'scheduled_post_at':scheduled_post_at,
            'race_id':request['race_id'],'input_sha256':_sha(final),'request_sha256':_sha(request),'budget':budget,'arms':arms,'production_effect':'NONE',
            'production_comparable_equal_spend':arms['PRODUCTION']['investment']==budget,
            'notice':'Tier ablation, not an AKI/distribution-adaptive policy. No new ticket added.'}


if __name__=="__main__":
    r=write_report()
    print(json.dumps({"status":"PASS","profile":r["profile"],"sha256":r["sha256"],"cohorts":r["cohorts"]},ensure_ascii=False,separators=(",",":")))

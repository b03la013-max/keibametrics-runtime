"""Append-only bridge: official JRA Candidate postresult -> preregistered PFS ledger.

Do NOT edit runtime/pfs_grand_review.py: its definition is frozen as part of
the LOCAL forward protocol. This adapter uses the legacy supported
source_candidate_results format, with source hashes and no Actual claim.
"""
from __future__ import annotations
import hashlib
import json
from collections import defaultdict
from pathlib import Path

PROFILE="KM-JRA-CANDIDATE-POSTRESULT-PFS-BRIDGE-20261010-R1"


def _hash(obj):
    return hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,
        separators=(",",":")).encode("utf-8")).hexdigest()


def _read_checked(path:Path):
    x=json.loads(path.read_text(encoding="utf-8"))
    if x.get("sha256")!=_hash({k:v for k,v in x.items() if k!="sha256"}):
        raise ValueError("IMMUTABLE_INPUT_HASH_MISMATCH:"+str(path))
    return x


def bridge_race(root:Path,race_id:str)->dict:
    d=root/"runtime"/"source_candidate_oos"/race_id
    pre=_read_checked(d/"pre_result.json")
    final=_read_checked(d/"candidate_final.json")
    result=_read_checked(d/"result_evaluation.json")
    settlement=_read_checked(d/"settlement.json")
    if any(x.get("race_id")!=race_id for x in (pre,final,result,settlement)):
        raise ValueError("BRIDGE_RACE_ID_MISMATCH:"+race_id)
    if (pre.get("oos_eligible") is not True or pre.get("candidate_final_verified") is not True
        or result.get("oos_eligible") is not True
        or final.get("candidate_only") is not True
        or result.get("settlement_sha256")!=settlement["sha256"]
        or settlement.get("frozen_pre_result_sha256")!=pre["sha256"]
        or settlement.get("frozen_candidate_final_sha256")!=final["sha256"]
        or settlement.get("status")!="SETTLED_FROZEN_CANDIDATE_RECOMMENDATION"
        or settlement.get("actual_purchase_status")!="UNVERIFIED"
        or settlement.get("production_effect")!="NONE"
        or settlement.get("automatic_promotion") is not False):
        raise ValueError("BRIDGE_TEMPORAL_OR_AUTHORITY_MISMATCH:"+race_id)
    frozen=(final.get("mec") or {}).get("tickets") or []
    settled=settlement.get("frozen_tickets") or []
    if not frozen or len(settled)!=len(frozen):
        raise ValueError("BRIDGE_TICKET_UNIVERSE_MISMATCH:"+race_id)
    def ticket_key(row):
        kind=str(row.get("bet_type") or "").upper()
        if kind not in {"EXACTA","TRIO","TRIFECTA"}:
            raise ValueError("BRIDGE_TICKET_TYPE_INVALID:"+race_id)
        selection=[int(x) for x in row.get("selection") or []]
        if len(selection)!=(2 if kind=="EXACTA" else 3) or len(set(selection))!=len(selection):
            raise ValueError("BRIDGE_SELECTION_INVALID:"+race_id)
        if kind=="TRIO":selection=sorted(selection)
        return (kind,tuple(selection))
    f={ticket_key(row):row for row in frozen}
    r={ticket_key(row):row for row in settled}
    if len(f)!=len(frozen) or len(r)!=len(settled) or set(f)!=set(r):
        raise ValueError("BRIDGE_TICKET_KEYS_MISMATCH:"+race_id)
    inv=ret=0
    by_type=defaultdict(lambda:{"investment":0,"payout":0})
    winning=[]
    for key,row in r.items():
        stake=int(row["stake"]); pay=int(row["recommended_return"])
        frozen_stake=int(f[key]["stake"])
        if stake!=frozen_stake or stake<100 or stake%100 or pay<0:
            raise ValueError("BRIDGE_TICKET_STAKE_OR_RETURN_INVALID:"+race_id)
        inv+=stake;ret+=pay
        by_type[key[0]]["investment"]+=stake
        by_type[key[0]]["payout"]+=pay
        if pay:
            winning.append({"bet_type":key[0],"selection":list(key[1]),
                            "stake":stake,"payout":pay,
                            "payout_per_100":pay*100/stake})
    if (inv!=int(settlement["recommended_stake_yen"])
        or ret!=int(settlement["recommended_return_yen"])
        or len(frozen)!=int(settlement["purchased_ticket_count"])
        or inv<=0):
        raise ValueError("BRIDGE_CANONICAL_CAPITAL_MISMATCH:"+race_id)
    doc={
        "race_id":race_id,
        "profile":PROFILE,
        "source_result_settlement_sha256":settlement["sha256"],
        "source_pre_result_sha256":pre["sha256"],
        "source_candidate_final_sha256":final["sha256"],
        "production_effect":"NONE","automatic_promotion":False,
        "settlement":{
            "status":"SETTLED",
            "pfs_authority":"CANDIDATE-FROZEN-RECOMMENDATION-PFS",
            "actual_ticket_status":"UNVERIFIED",
            "total_investment":inv,"total_payout":ret,
            "pfs":round(ret/inv*100,9),
            "winning_tickets":winning,
            "bet_type_summary":[{"bet_type":bt,**values} for bt,values in sorted(by_type.items())],
            "immutable_source_sha256":settlement["sha256"],
        }
    }
    doc["sha256"]=_hash(doc)
    return doc


def bridge_all(root:Path=Path("."))->dict:
    root=root.resolve()
    source=root/"runtime"/"source_candidate_oos"
    target=root/"runtime"/"source_candidate_results"
    target.mkdir(parents=True,exist_ok=True)
    written=[];unchanged=[]
    for path in sorted(source.glob("KM-JRA-*/settlement.json")):
        rid=path.parent.name
        doc=bridge_race(root,rid)
        dest=target/(rid+".json")
        if dest.exists():
            previous=json.loads(dest.read_text(encoding="utf-8"))
            old=previous.get("settlement") or {}
            new=doc["settlement"]
            if (int(old.get("total_investment") or -1)!=new["total_investment"]
                or int(old.get("total_payout") or -1)!=new["total_payout"]):
                raise ValueError("CANDIDATE_LEGACY_PFS_CONFLICT:"+rid)
            if previous.get("source_result_settlement_sha256") not in (None,doc["source_result_settlement_sha256"]):
                raise ValueError("CANDIDATE_LEGACY_SOURCE_HASH_CONFLICT:"+rid)
            unchanged.append(rid)
            continue
        try:
            with dest.open("x",encoding="utf-8") as fh:
                json.dump(doc,fh,ensure_ascii=False,sort_keys=True,indent=2)
                fh.write("\n")
        except FileExistsError:
            raise ValueError("CANDIDATE_LEGACY_APPEND_RACE:"+rid)
        written.append(rid)
    return {"profile":PROFILE,"written":written,"unchanged":unchanged,"production_effect":"NONE"}


if __name__=="__main__":
    print(json.dumps(bridge_all(),ensure_ascii=False,sort_keys=True))

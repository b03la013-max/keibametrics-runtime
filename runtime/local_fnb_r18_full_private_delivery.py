"""FNB R18: nontruncating 2 Owner × 3 methods private DELIVERY BODY gate.

This module RENDERS only already verified source/29 index, frozen role rankings,
actual KRS two 5000-run seed1 output, and the six separately generated Common
MEC/Capital trees. It cannot fabricate missing selections or promote a
document presentation to a signed FINAL or actual recipient ACK.
"""
from __future__ import annotations

import hashlib,json,math
from pathlib import Path
from runtime.local_fnb_r9_method_audit import audit_methods
from runtime.local_fnb_r13_private_single_numeric import _atomic_private_write
from runtime.local_fnb_r17_method_constructor import METHODS, OWNERS

PROFILE="KM-FNB-R18-ALL-HORSE-DUAL-OWNER-SIX-METHOD-FULL-DELIVERY-v1"

def text(v):
    return str(v).replace("\n"," ").replace("\r"," ").replace("|","／")

def verified_full_delivery(*,race_id,private_root,semantics,portfolios,diagnostic_only=False):
    path=Path(private_root).resolve()/race_id
    num_file=path/"numerical_materialization.json"
    if not num_file.is_file():
        raise ValueError("FNB_R18_MISSING_ACTUAL_ALL29_NUMERICAL_ORIGINAL")
    num=json.loads(num_file.read_text(encoding="utf-8"))
    mapping=json.loads((Path(__file__).resolve().parents[1]/
        "mapping/local_full_numerical_mapping_v1.0_production_20261008.json").read_text())
    required=mapping["required_indices"]
    if not isinstance(required,list) or len(required)!=29:
        raise ValueError("FNB_R18_CURRENT_29_INDEX_MANIFEST_MISSING")
    runners=num.get("runners")
    if not isinstance(runners,list) or len(runners)<2:
        raise ValueError("FNB_R18_ACTIVE_UNIVERSE_OR_NUMERICS_MISSING")
    ids=[str(r.get("runner_id")) for r in runners]
    if len(set(ids))!=len(ids):
        raise ValueError("FNB_R18_DUPLICATE_HORSE_NUMBERS")
    if not isinstance(semantics,dict) or set(semantics)!=set(OWNERS):
        raise ValueError("FNB_R18_TWO_FROZEN_OWNER_RANKINGS_MISSING")
    audit=audit_methods(portfolios)
    if not audit["complete"]:
        raise ValueError("FNB_R18_NOT_ALL_SIX_METHODS_VERIFIED")
    lines=["# 船橋｜ケイバメトリクス全馬・両Owner・全6方式 完全私有表示原本",
        "Race "+text(race_id),
        "分類："+("POSTCUTOFF_DIAGNOSTIC_NOT_PRESTART" if diagnostic_only
                else "SINGLE_RACE_PRESTART_NONPRODUCTION_NOT_REGISTERED_OOS"),
        "全券面は所有者間で合算しない独立代替案です。",
        "SSR/LSR/Z4Rは未較正のシミュレーション出現率で、実勝率やEVではありません。",
        "本表示は実購入・正式署名・本人への到達ACKを示しません。",""]
    for owner in OWNERS:
        frozen=semantics[owner]
        order=frozen.get("rankings_by_column")
        if not isinstance(order,dict) or set(order)!={"W","P2","P3"}:
            raise ValueError("FNB_R18_"+owner+"_W_P2_P3_FULL_RANKING_MISSING")
        for col in ("W","P2","P3"):
            ranks=order[col]
            if not isinstance(ranks,list) or [str(v) for v in ranks] is None or (
                    len(ranks)!=len(ids) or set(map(str,ranks))!=set(ids)):
                raise ValueError("FNB_R18_"+owner+"_"+col+"_RANKING_NOT_ALL_ACTIVE")
            if len(set(map(str,ranks)))!=len(ranks):
                raise ValueError("FNB_R18_DUPLICATE_COLUMN_RANK")
        roles=frozen.get("role_registry")
        if not isinstance(roles,list):
            raise ValueError("FNB_R18_FROZEN_OWNER_ROLE_REGISTRY_REQUIRED")
        krs_file=path/(owner+"_krs_output.json")
        if not krs_file.is_file():
            raise ValueError("FNB_R18_"+owner+"_ACTUAL_KRS_OUTPUT_MISSING")
        krs=json.loads(krs_file.read_text())
        snap=krs.get("snapshot") or {}
        engine=krs.get("engine") or {}
        krs_rows=krs.get("summary")
        if (snap.get("run_count")!=5000 or snap.get("master_seed")!=1 or
                snap.get("prediction_id")!=race_id+"-"+owner or
                engine.get("engine_version")!="1.1.0" or
                engine.get("parameter_map_version")!="0.1-provisional" or
                not isinstance(krs_rows,list) or len(krs_rows)!=len(ids)):
            raise ValueError("FNB_R18_"+owner+"_REAL_KRS_5000_SEED1_NOT_VERIFIED")
        krs_by={str(x.get("horse_no")):x for x in krs_rows if isinstance(x,dict)}
        if set(krs_by)!=set(ids):
            raise ValueError("FNB_R18_"+owner+"_KRS_HORSE_UNIVERSE_MISMATCH")
        lines+=["## "+owner+"｜全馬W/P2/P3・役割・KRS","",
           "|馬番|馬名|W順位|P2順位|P3順位|採用Role|SSR-W|SSR-P2|SSR-P3|LSR|Z4R-W|",
           "|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|"]
        role_by={rid:set() for rid in ids}
        for row in roles:
            k=str(row.get("runner_id"))
            if k not in role_by:
                raise ValueError("FNB_R18_ROLE_NOT_AN_ACTIVE_RUNNER")
            if row.get("status") in ("CORE","PROTECTED","CONDITIONAL","RESIDUAL"):
                if row.get("column") not in ("W","P2","P3"):
                    raise ValueError("FNB_R18_ACTIVE_ROLE_COLUMN_INVALID")
                role_by[k].add(row["column"])
        for horse in runners:
            rid=str(horse["runner_id"])
            rr=krs_by[rid]
            metrics=[]
            for key in ("SSR-W","SSR-P2","SSR-P3","LSR","Z4R-W"):
                value=rr.get(key)
                if type(value) not in (float,int) or not math.isfinite(float(value)) or not 0<=float(value)<=1:
                    raise ValueError("FNB_R18_KRS_METRIC_NOT_AN_OBSERVED_FINITE_OCCURRENCE:"+key)
                metrics.append(f"{float(value):.4f}")
            name=text(horse.get("name") or horse.get("horse_name") or "馬名UNKNOWN")
            ranks=[str(order[col].index(int(rid))+1 if int(rid) in order[col]
                   else [str(x) for x in order[col]].index(rid)+1)
                   for col in ("W","P2","P3")]
            lines.append("|"+"|".join([rid,name,*ranks,
              "/".join(c for c in ("W","P2","P3") if c in role_by[rid]) or "非採用",
              *metrics])+"|")
        lines+=["","### "+owner+"｜3方式（各方式は独立した別案）"]
        for method in METHODS:
            t=portfolios[owner][method]
            if t["point_count"]!=len(t["tickets"]) or (
                    sum(x["stake"] for x in t["tickets"])!=t["total_investment"]):
                raise ValueError("FNB_R18_RENDERED_TICKET_TOTAL_MISMATCH")
            lines+=["",f"#### {method}",
              f"点数：{t['point_count']}点／Stake合計：{t['total_investment']}円"
              f"／必要MEC額：{t['required_method_mec_capital']}円"
              f"／予算：{t['capital_limit']}円／未使用：{t['unused_capital']}円",
              ("計算済みNO-BET："+t["reason"] if t["no_bet"]
               else "元券面を以下に一切省略せず表示します。"),
              t["canonical_tree"]]
        lines.append("")
    lines+=["## 全馬29指数・各セル状態・欠測来歴", ""]
    cell_count=0
    for horse in runners:
        rid=str(horse["runner_id"])
        cells=horse.get("canonical_components")
        if not isinstance(cells,dict) or set(cells)!=set(required):
            raise ValueError("FNB_R18_HORSE_FULL29_INCOMPLETE:"+rid)
        lines+=["### "+rid+"番 "+text(horse.get("name") or "UNKNOWN"),
                "|指数|値|状態|Rule ID|根拠|","|---|---:|---|---|---|"]
        for idx in required:
            c=cells[idx]
            v=c.get("value")
            status=c.get("terminal_status")
            if (status not in ("CALCULATED","RULED-NEUTRAL") or
                    type(v) not in (int,float) or not math.isfinite(float(v))):
                raise ValueError("FNB_R18_UNRESOLVED_OR_NONFINITE_CELL:"+idx+":"+rid)
            refs=c.get("evidence_refs")
            if not isinstance(refs,list) or not refs:
                raise ValueError("FNB_R18_PROVENANCE_MISSING:"+idx+":"+rid)
            lines.append("|"+"|".join([idx,f"{float(v):.6f}",status,
                text(c.get("rule_id") or "UNKNOWN"),
                text(",".join(map(str,refs)))])+"|")
            cell_count+=1
        missing=horse.get("numerical_missing_components") or []
        lines.append("欠測構成要素："+(", ".join(map(str,missing)) if missing else "なし")+"")
        lines.append("")
    if cell_count!=len(runners)*29:
        raise ValueError("FNB_R18_ALL_ACTIVE_29_CELLS_NOT_RENDERED")
    body="\n".join(lines)+"\n"
    digest=_atomic_private_write(path/"FULL_ALL_HORSES_BC_SIX_METHODS.md",body.encode("utf-8"))
    if hashlib.sha256((path/"FULL_ALL_HORSES_BC_SIX_METHODS.md").read_bytes()).hexdigest()!=digest:
        raise ValueError("FNB_R18_PRIVATE_DELIVERY_DOCUMENT_READBACK_FAIL")
    return {"status":"FULL_PRESENTATION_READY_RECIPIENT_ACK_UNVERIFIED",
            "race_id":race_id,
            "all_horses":len(runners),"all_29_index_cells":cell_count,
            "two_owners":list(OWNERS),"six_alternative_methods":True,
            "full_body_sha256":digest,
            "body_filename":"FULL_ALL_HORSES_BC_SIX_METHODS.md",
            "private_body_roundtrip_verified":True,
            "prestart_time_verified_by_document":False,
            "signed_final_verified_by_document":False,
            "recipient_delivery_ack":False,
            "registered_oos_increment":0}

from __future__ import annotations

import copy
import datetime as dt
import hashlib
import json
from typing import Any, Dict

PROFILE="KM-FAMILY-CONVERSION-DIAGNOSTICS-SHADOW-20261005-R1"
ACTIVATION_AT="2026-10-06T00:00:00+09:00"
HARD_MARKERS=("STRUCTURAL_HARD","HARD_EXCLUSION","HARD-EXCLUSION","IMPOSSIBLE","INELIGIBLE")


def _sha(obj:Any)->str:
    return hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def _roles(req:Dict[str,Any], final_package:Dict[str,Any])->Dict[str,list]:
    return (final_package or {}).get("roles") or (req.get("static_prediction") or {}).get("roles") or {}


def _role_rows(req:Dict[str,Any])->Dict[int,Dict[str,Dict[str,Any]]]:
    out={}
    for row in req.get("role_registry") or []:
        try:
            runner=int(row["runner_id"])
        except Exception:
            continue
        col=str(row.get("column") or "").upper()
        if col:
            out.setdefault(runner,{})[col]=dict(row)
    return out


def _hard(reason:Any)->bool:
    text=str(reason or "").upper()
    return any(x in text for x in HARD_MARKERS)


def _material_pairs(req:Dict[str,Any])->Dict[tuple[int,int],Dict[str,Any]]:
    out={}
    for row in req.get("pair_dispositions") or []:
        status=str(row.get("status") or "").upper()
        if status not in {"PURCHASE","PROTECT","MATERIAL"}:
            continue
        try:
            out[(int(row["head"]),int(row["second"]))]=dict(row)
        except Exception:
            continue
    return out


def _hard_pairs(req:Dict[str,Any])->set[tuple[int,int]]:
    out=set()
    for row in req.get("pair_dispositions") or []:
        if str(row.get("status") or "").upper()!="EXCLUDE" or not _hard(row.get("reason")):
            continue
        try:
            out.add((int(row["head"]),int(row["second"])))
        except Exception:
            continue
    return out


def _explicit_thirds(req:Dict[str,Any])->Dict[tuple[int,int,int],Dict[str,Any]]:
    out={}
    for row in req.get("third_dispositions") or []:
        try:
            out[(int(row["head"]),int(row["second"]),int(row["third"]))]=dict(row)
        except Exception:
            continue
    return out


def _krs_p3_ranks(utility:Dict[str,Any])->Dict[int,int]:
    out={}
    for row in (utility or {}).get("summary") or []:
        try:
            runner=int(row.get("horse_no") if row.get("horse_no") is not None else row.get("runner_id"))
        except Exception:
            continue
        ranks=row.get("ranks") or {}
        raw=ranks.get("SSR-P3")
        try:
            out[runner]=int(raw)
        except Exception:
            continue
    return out


def _purchased_exact(final_ticket:Dict[str,Any])->set[tuple[int,int,int]]:
    out=set()
    for row in (final_ticket or {}).get("tickets") or []:
        if str(row.get("bet_type") or "").upper()!="TRIFECTA":
            continue
        sel=row.get("selection") or []
        if len(sel)!=3:
            continue
        try:
            out.add(tuple(int(x) for x in sel))
        except Exception:
            continue
    return out


def build_diagnostics(req:Dict[str,Any], final_ticket:Dict[str,Any],
                      final_package:Dict[str,Any], krs_utility:Dict[str,Any],
                      generated_at:str, basis_sha256:str)->Dict[str,Any]:
    roles=_roles(req,final_package)
    registry=_role_rows(req)
    material_pairs=_material_pairs(req)
    hard_pairs=_hard_pairs(req)
    explicit_thirds=_explicit_thirds(req)
    p3_ranks=_krs_p3_ranks(krs_utility)
    purchased_exact=_purchased_exact(final_ticket)

    active_w=sorted(int(r) for r,vals in roles.items()
                    if any(str(v).upper().startswith("W") for v in (vals or [])))
    active_p3=sorted(int(r) for r,vals in roles.items()
                     if any(str(v).upper().startswith("P3") for v in (vals or [])))

    winner_migration=[]
    for runner,vals in roles.items():
        rid=int(runner)
        role_set={str(v).upper() for v in (vals or [])}
        if any(v.startswith("W") for v in role_set):
            continue
        wrow=(registry.get(rid) or {}).get("W") or {}
        if _hard(wrow.get("reason")):
            continue
        lower={}
        for col in ("P2","P3"):
            row=(registry.get(rid) or {}).get(col) or {}
            status=str(row.get("status") or "").upper()
            if status in {"CORE","PROTECTED"}:
                lower[col]=status
        if lower:
            winner_migration.append({
                "runner_id":rid,
                "lower_role_status":lower,
                "diagnostic":"LOWER_ROLE_RETAINED_W_ABSENT",
                "structural_hard_w_negative_observed":False,
                "automatic_w_promotion":False,
                "purchase_authority":False,
            })

    protected_p2=[]
    for rid,cols in registry.items():
        status=str((cols.get("P2") or {}).get("status") or "").upper()
        if status in {"CORE","PROTECTED"}:
            protected_p2.append((rid,status))

    pair_residual=[]
    for head in active_w:
        for second,p2_status in protected_p2:
            if head==second or (head,second) in material_pairs or (head,second) in hard_pairs:
                continue
            pair_residual.append({
                "head":head,
                "second":second,
                "p2_status":p2_status,
                "terminal":"PAIR-RESIDUAL",
                "diagnostic":"ACTIVE_W_X_CORE_OR_PROTECTED_P2_NO_MATERIAL_PAIR",
                "automatic_purchase":False,
                "purchase_authority":False,
            })

    selective_exact=[]
    for (head,second),pair in sorted(material_pairs.items()):
        for third in active_p3:
            if third in {head,second}:
                continue
            exact=(head,second,third)
            if exact in purchased_exact:
                continue
            reasons=[]
            p3row=(registry.get(third) or {}).get("P3") or {}
            p3_status=str(p3row.get("status") or "").upper()
            if p3_status in {"CORE","PROTECTED"}:
                reasons.append("STATIC_P3_"+p3_status)
            if any(x in str(p3row.get("reason") or "").upper()
                   for x in ("DIRECT","PROTECT","CURRENT_STATE","STAGE")):
                reasons.append("STATIC_P3_INDEPENDENT_REASON")
            explicit=explicit_thirds.get(exact) or {}
            explicit_status=str(explicit.get("status") or "").upper()
            if explicit_status in {"PURCHASE","PROTECT","MATERIAL"}:
                reasons.append("PAIR_LOCAL_THIRD_"+explicit_status)
            rank=p3_ranks.get(third)
            if rank is not None and rank<=3:
                reasons.append("KRS_P3_TOP3_REAUDIT")
            if not reasons:
                continue
            selective_exact.append({
                "exact":[head,second,third],
                "pair_status":str(pair.get("status") or "").upper(),
                "p3_role_status":p3_status or None,
                "krs_p3_rank":rank,
                "independent_protection_reasons":sorted(set(reasons)),
                "diagnostic":"MATERIAL_PAIR_X_INDEPENDENTLY_PROTECTED_P3",
                "automatic_purchase":False,
                "purchase_authority":False,
            })

    out={
        "profile":PROFILE,
        "status":"SHADOW-DIAGNOSTIC / NON-PRODUCTION / NO-AUTO-PROMOTION",
        "activation_at":ACTIVATION_AT,
        "race_id":req.get("race_id"),
        "generated_at":generated_at,
        "scheduled_post_at":req.get("scheduled_post_at"),
        "temporal_mode":req.get("temporal_mode"),
        "source_basis_sha256":basis_sha256,
        "winner_role_migration_candidates":winner_migration,
        "pair_residual_candidates":pair_residual,
        "selective_exact_candidates":selective_exact,
        "production_effect":"NONE",
        "automatic_purchase":False,
        "existing_common_exact_oos_arms_changed":False,
        "existing_local_mec_r5_arms_changed":False,
    }
    out["sha256"]=_sha({k:v for k,v in out.items() if k!="sha256"})
    return out


def bind_to_trace(trace:Dict[str,Any], diagnostic:Dict[str,Any])->Dict[str,Any]:
    out=copy.deepcopy(trace or {})
    out["family_conversion_diagnostics_binding"]={
        "profile":PROFILE,
        "sha256":diagnostic.get("sha256"),
        "basis_sha256":diagnostic.get("source_basis_sha256"),
        "generated_at":diagnostic.get("generated_at"),
        "scheduled_post_at":diagnostic.get("scheduled_post_at"),
        "production_effect":"NONE",
    }
    return out


def verify_signed_final_binding(final_envelope:Dict[str,Any], diagnostic:Dict[str,Any])->Dict[str,Any]:
    expected=_sha({k:v for k,v in diagnostic.items() if k!="sha256"})
    if diagnostic.get("sha256")!=expected:
        raise AssertionError("FAMILY_CONVERSION_DIAGNOSTIC_CONTENT_HASH_MISMATCH")
    rec=final_envelope.get("receipt") or {}
    art=final_envelope.get("artifact") or {}
    if rec.get("phase")!="FINAL" or rec.get("status")!="PASS":
        raise AssertionError("FAMILY_CONVERSION_DIAGNOSTIC_FINAL_NOT_PASS")
    binding=(art.get("ticket_transport_trace") or {}).get("family_conversion_diagnostics_binding") or {}
    if binding.get("sha256")!=diagnostic.get("sha256"):
        raise AssertionError("FAMILY_CONVERSION_DIAGNOSTIC_SHA_NOT_BOUND")
    if binding.get("basis_sha256")!=diagnostic.get("source_basis_sha256"):
        raise AssertionError("FAMILY_CONVERSION_DIAGNOSTIC_BASIS_SHA_NOT_BOUND")
    if str(binding.get("production_effect"))!="NONE":
        raise AssertionError("FAMILY_CONVERSION_DIAGNOSTIC_PRODUCTION_EFFECT_FORBIDDEN")
    return {
        "valid":True,
        "profile":PROFILE,
        "diagnostic_sha256":diagnostic.get("sha256"),
        "basis_sha256":diagnostic.get("source_basis_sha256"),
        "final_receipt_sha256":final_envelope.get("receipt_sha256"),
        "production_effect":"NONE",
    }

"""FNB R13: perform independent private 29-index numerical diagnostic.

This runs the EXISTING LOCAL 29-index production numerical materializer on
one properly identified official source artifact, WITHOUT promoting any of
its four downstream Prediction/KRS/Ticket/Capital consumer permissions.

All full horse materialization is stored ONLY under caller's private path,
outside this public GitHub repository. Read-back bytes and SHA are checked.
This lane cannot masquerade as user-delivered or as v2 registered OOS.

No autonomous provider GET, signing, KRS, purchase or network POST occurs.
The private Work actor must supply the permitted official SOURCE bytes.
"""
from __future__ import annotations

from datetime import datetime,timezone
import hashlib,json,os,tempfile
from pathlib import Path

from runtime.local_fnb_r13_private_source_admission import (
    SCOPE,PURPOSE,admit)

def _encoded(obj):
    return (json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2,
                       allow_nan=False)+"\n").encode("utf-8")

def _sha(data):
    return hashlib.sha256(data).hexdigest()

def _atomic_private_write(path,payload):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent,delete=False) as f:
        temp=Path(f.name)
        f.write(payload)
        f.flush()
        os.fsync(f.fileno())
    try:
        os.chmod(temp,0o600)
        os.replace(temp,path)
    finally:
        temp.unlink(missing_ok=True)
    actual=path.read_bytes()
    if actual!=payload:
        raise ValueError("PRIVATE_NUMERICAL_PERSISTED_BYTES_DIFFER")
    return _sha(actual)

def execute(*,source_artifact,request,private_root,
            repo_root=None,now=None,diagnostic_only=False):
    now=now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("FNB_PRIVATE_ASOF_TIMEZONE_REQUIRED")
    cutoff=datetime.fromisoformat(request["prediction_cutoff"].replace("Z","+00:00"))
    if cutoff.tzinfo is None:
        raise ValueError("FNB_PRIVATE_CUTOFF_TIMEZONE_REQUIRED")
    if now>=cutoff and not diagnostic_only:
        raise ValueError("FNB_PRESTART_CUTOFF_EXPIRED_NO_RETROACTIVE_PREDICTION")
    root=Path(repo_root or Path(__file__).resolve().parents[1])
    private_root=Path(private_root).resolve()
    admission=admit(source=source_artifact,request=request,purpose=PURPOSE,
                    classification=SCOPE,
                    destination=private_root,public_repo_root=root)
    import sys
    runtime_dir=str(root/"runtime")
    if runtime_dir not in sys.path:
        sys.path.insert(0,runtime_dir)
    from local_fullnumerical_production import materialize_production
    from runtime.local_fnb_r8_arithmetic_29 import verify_29
    from runtime.local_fnb_r8_missingness_census import census
    from runtime.local_fnb_r9_evidence_63 import audit_63
    required=request["required_indices"]
    result=materialize_production(source_artifact,request,required)
    registry=json.loads((root/"mapping/local_evidence_feature_rule_registry_v1.1_production_numerical_20261008.json").read_text(encoding="utf-8"))
    mapping=json.loads((root/"mapping/local_full_numerical_mapping_v1.0_production_20261008.json").read_text(encoding="utf-8"))
    arithmetic=verify_29(result,registry,mapping)
    missingness=census(result)
    components=audit_63(result,registry,request,source_artifact)
    if (arithmetic["status"]!="29_OF_29_RECORDED_FEATURE_ARITHMETIC_PASS"
            or components["status"]!="ALL_63_COMPONENT_RECORDS_LINEAGE_VERIFIED"
            or result["numeric_coverage"]["unresolved_count"]!=0):
        raise ValueError("PRIVATE_FULL_29_ARITHMETIC_OR_FEATURE_LINEAGE_HOLD")
    race_key=request["race_id"]
    if not isinstance(race_key,str) or not race_key or "/" in race_key or ".." in race_key:
        raise ValueError("FNB_PRIVATE_RACE_KEY_INVALID")
    path=private_root/race_key
    path.mkdir(parents=True,exist_ok=True)
    frozen=_encoded(result)
    frozen_sha=_atomic_private_write(path/"numerical_materialization.json",frozen)
    package={
        "classification":SCOPE if not diagnostic_only else
          "HISTORICAL_DIAGNOSTIC_ONLY_NOT_PRESTART_NOT_REGISTERED_OOS",
        "private_use_scope":PURPOSE,
        "source_admission":admission,
        "race_id":race_key,
        "as_of_observed_at":now.isoformat(),
        "official_cutoff":request["prediction_cutoff"],
        "prestart_source_acquired_and_calculated_proven":(not diagnostic_only and now<cutoff),
        "numerical_materialization_file":"numerical_materialization.json",
        "numerical_materialization_sha256":frozen_sha,
        "runner_count":len(result["runners"]),
        "required_29_index_cells":len(result["runners"])*29,
        "numeric_coverage":result["numeric_coverage"],
        "independent_recorded_feature_29_index_arithmetic":arithmetic,
        "recorded_63_component_lineage":components,
        "missingness_census":missingness,
        "source_to_all_63_feature_transforms_independent":False,
        "formal_signed_source_attested_here":False,
        "production_numerical_consumers_authorized":False,
        "fixed_two_owners_krs_5000_seed1_verified":False,
        "six_method_ticket_trees_verified":False,
        "recipient_delivery_ack_verified":False,
        "actual_purchase":False,
        "registered_oos_increment":0,
        "new_github_commits":0,
        "prediction_status":"NOT_CALCULATED_IN_THIS_NUMERIC_ONLY_LANE",
        "pfs":None
    }
    receipt=_encoded(package)
    receipt_sha=_atomic_private_write(path/"private_numerical_receipt.json",receipt)
    if ((path/"private_numerical_receipt.json").read_bytes()!=receipt or
            _sha((path/"numerical_materialization.json").read_bytes())!=frozen_sha):
        raise ValueError("FNB_PRIVATE_NUMERIC_READBACK_VERIFICATION_FAILED")
    return {"status":"PRIVATE_NUMERIC_DIAGNOSTIC_COMPLETE_NOT_FORMAL",
            "classification":package["classification"],
            "race_id":race_key,
            "runner_count":package["runner_count"],
            "29_index_cells":package["required_29_index_cells"],
            "calculated":result["numeric_coverage"]["calculated_count"],
            "neutral":result["numeric_coverage"]["ruled_neutral_count"],
            "unknown_components":components["missing_component_records"],
            "private_receipt_sha256":receipt_sha,
            "private_materialization_sha256":frozen_sha,
            "full_private_readback_verified":True,
            "private_root":str(path),
            "signed_final_or_delivery_claim":False,
            "registered_oos_increment":0}

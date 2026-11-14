"""Non-Production index audit: regression for leakage/neutral/identity guards."""
import pytest

from research import local_index_outcome_audit as audit


def artifacts(n=5):
    names=[f"I{i:02d}" for i in range(29)]
    rows=[]
    for k in range(n):
        rows.append({
            "runner_id":str(k+1),
            "canonical_components":{
                name:{"terminal_status":"CALCULATED","value":float(100-k*5)}
                for name in names
            }
        })
    return ({"race_id":"KM-LOCAL-KAW-20261111-R01-LIVE-R1","required_indices":names,"runners":rows},
            {"race_id":"KM-LOCAL-KAW-20261111-R01-LIVE-R1","finish_order":[str(k+1) for k in range(n)]})


def kwargs():
    return {"frozen_at":"2026-11-11T05:40:00+09:00",
            "scheduled_post_at":"2026-11-11T14:45:00+09:00"}


def test_actual_full29_rows_have_29_measured_correlations_no_claim_of_causality():
    num,res=artifacts()
    out=audit.audit(num,res,**kwargs())
    assert len(out["indices"])==29
    assert out["indices"]["I00"]["higher_score_better_finish_spearman"]==1.0
    assert out["indices"]["I28"]["calculated_runner_count"]==5
    assert out["prediction_consumption_authorized"] is False
    assert out["external_signature_verification"]=="NOT_PERFORMED"
    assert out["classification"]=="NONPRODUCTION_RETROSPECTIVE_DIAGNOSTIC_NOT_OOS"
    assert out["sha256"]==audit._digest({k:v for k,v in out.items() if k!="sha256"})


def test_neutral_is_not_a_calculated_observation():
    num,res=artifacts()
    for row in num["runners"]:
        if row["runner_id"] in ("1","2","3"):
            row["canonical_components"]["I00"]={"terminal_status":"RULED-NEUTRAL","value":52.0}
    out=audit.audit(num,res,**kwargs())
    x=out["indices"]["I00"]
    assert x["calculated_runner_count"]==2
    assert x["ruled_neutral_runner_count"]==3
    assert x["higher_score_better_finish_spearman"] is None
    assert out["indices"]["I01"]["higher_score_better_finish_spearman"]==1.0


def test_duplicate_runner_prevents_false_index_success():
    num,res=artifacts()
    num["runners"][1]["runner_id"]="1"
    with pytest.raises(audit.IndexAuditError,match="NUMERICAL_RUNNER_IDENTITY_INVALID"):
        audit.audit(num,res,**kwargs())


def test_missing_runner_or_undocumented_scratches_require_official_reconciliation():
    num,res=artifacts()
    res["finish_order"]=res["finish_order"][:-1]
    with pytest.raises(audit.IndexAuditError,match="FINISH_UNIVERSE_MISMATCH"):
        audit.audit(num,res,**kwargs())


def test_poststart_numerical_cannot_claim_predated_prediction():
    num,res=artifacts()
    with pytest.raises(audit.IndexAuditError,match="POSTSTART_NUMERICAL"):
        audit.audit(num,res,frozen_at="2026-11-11T14:46:00+09:00",
                    scheduled_post_at=kwargs()["scheduled_post_at"])


def test_result_for_different_race_is_rejected():
    num,res=artifacts()
    res["race_id"]="KM-LOCAL-KAW-20261111-R02-LIVE-R1"
    with pytest.raises(audit.IndexAuditError,match="RACE_IDENTITY_MISMATCH"):
        audit.audit(num,res,**kwargs())


def test_29_index_manifest_required_and_nonfinite_input_rejected():
    num,res=artifacts()
    num["required_indices"]=num["required_indices"][:-1]
    with pytest.raises(audit.IndexAuditError,match="FULL29_MANIFEST_REQUIRED"):
        audit.audit(num,res,**kwargs())
    num,res=artifacts()
    num["runners"][0]["canonical_components"]["I00"]["value"]=float("nan")
    with pytest.raises(audit.IndexAuditError,match="INDEX_CALCULATED_VALUE_INVALID"):
        audit.audit(num,res,**kwargs())


def test_tied_scores_report_insufficient_variation_without_fabricated_ability():
    num,res=artifacts()
    for row in num["runners"]:
        row["canonical_components"]["I00"]["value"]=20
    out=audit.audit(num,res,**kwargs())
    assert out["indices"]["I00"]["higher_score_better_finish_spearman"] is None


def test_signer_claim_is_only_caller_attestation():
    num,res=artifacts()
    out=audit.audit(num,res,source_prestart_attested=True,result_official_attested=True,**kwargs())
    assert out["source_prestart_attested_unverified"] is True
    assert out["result_official_attested_unverified"] is True
    assert out["external_signature_verification"]=="NOT_PERFORMED"

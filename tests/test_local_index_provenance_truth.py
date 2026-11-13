import pytest
from runtime.local_index_provenance_builder import build, LocalProvenanceError


def sample():
    return {
        "race_id":"KM-LOCAL-KAW-SYNTHETIC",
        "runners":[{
            "runner_id":"1",
            "canonical_components":{
                "HPI-L":{
                    "terminal_status":"CALCULATED",
                    "rule_id":"SYNTHETIC",
                    "mapping_version":"TEST",
                    "evidence_refs":["TEST"],
                    "source_fact":"synthetic value",
                    "value":54.0,
                }
            },
        }],
        "full_terminalization":True,
        "full_numerical_calculation":True,
        "numeric_coverage":{"required_count":1},
    }


def test_valid_numeric_terminal_preserves_calculated_value_and_ledger_flags():
    x=build(sample())
    assert x["index_provenance_ledger"]["rows"][0]["value"]==54.0
    assert x["index_provenance_ledger"]["full_numerical_calculation"] is True
    assert len(x["index_provenance_hash"])==64


@pytest.mark.parametrize("invalid",[True,"52",float("nan"),float("inf"),-0.01,100.01])
def test_invalid_numeric_terminal_not_certified(invalid):
    q=sample()
    q["runners"][0]["canonical_components"]["HPI-L"]["value"]=invalid
    with pytest.raises(LocalProvenanceError,match="NUMERIC_TERMINAL_VALUE_INVALID"):
        build(q)


def test_ruled_neutral_must_have_finite_numeric_value():
    q=sample()
    q["runners"][0]["canonical_components"]["HPI-L"]["terminal_status"]="RULED-NEUTRAL"
    q["runners"][0]["canonical_components"]["HPI-L"]["value"]=float("nan")
    with pytest.raises(LocalProvenanceError,match="NUMERIC_TERMINAL_VALUE_INVALID"):
        build(q)


@pytest.mark.parametrize("name",["full_terminalization","full_numerical_calculation"])
@pytest.mark.parametrize("wrong",["false","true",1,0])
def test_numerical_ledger_flags_must_be_true_booleans(name,wrong):
    q=sample()
    q[name]=wrong
    with pytest.raises(LocalProvenanceError,match="NUMERICAL_LEDGER_FLAG_INVALID"):
        build(q)


def test_missing_ledger_flags_default_false_without_claiming_numeric_completion():
    q=sample()
    q.pop("full_numerical_calculation")
    q.pop("full_terminalization")
    x=build(q)
    assert x["index_provenance_ledger"]["full_terminalization"] is False
    assert x["index_provenance_ledger"]["full_numerical_calculation"] is False

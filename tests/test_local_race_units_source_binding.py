"""Existing LOCAL units and real archived SOURCE; no live forecast or KRS."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest

from runtime.local_nar_evidence_candidate import (
    LocalCandidateEvidenceError, compile_candidate_evidence, resolve_race_units)
from runtime.execution_store import resolve_phase

ROOT=Path(__file__).resolve().parents[1]
RID="KM-LOCAL-FNB-20261002-R04-LIVE-R1"

def archive():
    checkpoint=resolve_phase("LOCAL-"+RID+"-EXEC","SOURCE")
    assert checkpoint
    data=(checkpoint["run_dir"]/"source_receipt_envelope.json").read_bytes()
    assert hashlib.sha256(data).hexdigest()=="eb5c3b5ea22848ccde7cc16a3bc2073bd3d7bca520826031a6196394015a6710"
    return json.loads(data)["artifact"],json.loads((ROOT/"runtime/formal_intents"/(RID+".json")).read_text())

@pytest.mark.parametrize("venue,name",[("URW","浦和"),("FNB","船橋"),("OHI","大井"),("KAW","川崎"),("MOR","盛岡")])
def test_canonical_meters_and_japanese_venue_keep_explicit_direction(venue,name):
    q={"venue_id":venue,"race":{"venue":name,"distance_m":1500,"direction":"LEFT"}}
    assert resolve_race_units(q)=={"venue_id":venue,"venue_name":name,"distance_m":1500,"direction":"LEFT"}

@pytest.mark.parametrize("race,venue,code",[
    ({"venue":"浦和","distance_m":1500},"FNB","VENUE_FIELDS_CONFLICT"),
    ({"venue":"船橋","distance_m":1500},"FNB_typo","VENUE_ID_UNRESOLVED"),
    ({"venue":"船橋_typo","distance_m":1500},"FNB","VENUE_ID_UNRESOLVED"),
    ({"venue":"船橋","distance_m":1500,"distance":1200},"FNB","DISTANCE_FIELDS_CONFLICT"),
    ({"venue":"船橋","distance_m":True},"FNB","DISTANCE_UNIT_INVALID"),
    ({"venue":"船橋","distance_m":"1500m"},"FNB","DISTANCE_UNIT_INVALID"),
    ({"venue":"船橋","distance_m":1500,"direction":"UNKNOWN"},"FNB","DIRECTION_INVALID"),
])
def test_ambiguous_explicit_fields_hold_instead_of_silent_substitution(race,venue,code):
    with pytest.raises(LocalCandidateEvidenceError,match=code):
        resolve_race_units({"venue_id":venue,"race":race})

def test_real_archived_canonical_and_legacy_units_produce_identical_features():
    source,request=archive()
    old_source=deepcopy(source);old_request=deepcopy(request)
    legacy=deepcopy(request)
    legacy["race"]["distance"]=legacy["race"].pop("distance_m")
    legacy["race"]["venue"]="FNB"
    reg=ROOT/"mapping/local_evidence_feature_rule_registry_v1.1_production_numerical_20261008.json"
    a=compile_candidate_evidence(source,request,reg)
    b=compile_candidate_evidence(source,legacy,reg)
    assert source==old_source and request==old_request
    assert len(a["runners"])==12
    assert [r["evidence_features"] for r in a["runners"]]==[r["evidence_features"] for r in b["runners"]]
    missing=sum(f["missing"] for r in a["runners"] for f in r["evidence_features"].values())
    assert missing==212
    for row in a["runners"]:
        assert not row["evidence_features"]["course_geometry"]["missing"]
        assert not row["evidence_features"]["turn_direction"]["missing"]
        assert row["evidence_features"]["sire_fit"]["missing"]

def test_real_source_independent_raw_witness_covers_the_756_components():
    from runtime.local_base63_source_witness import verify
    from runtime.local_fullnumerical_production import materialize_production
    source,request=archive()
    registry=json.loads((ROOT/"mapping/local_evidence_feature_rule_registry_v1.1_production_numerical_20261008.json").read_text())
    numeric=materialize_production(source,request,request["required_indices"])
    witness=verify(source,request,registry,numeric)
    assert witness["component_match_counts"]=={"MATCH":756}
    assert witness["index_match_counts"]=={"MATCH":108}
    assert witness["production_input_provenance_gaps"]==0
    assert witness["nonmissing_arithmetic_match_count"]==544
    assert witness["missing_terminal_match_count"]==212
    assert witness["distinct_observed_rules_exercised"]==48
    assert witness["all_63_rules_empirical_measurement_complete"] is False
    assert witness["model_consumers_authorized"] is False
    assert witness["new_independent_raw_acquired"]==0
    assert numeric["numeric_coverage"]["calculated_count"]==312
    assert numeric["numeric_coverage"]["ruled_neutral_count"]==36

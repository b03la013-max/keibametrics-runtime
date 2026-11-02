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


def test_existing_v03_overrides_consume_canonical_units_from_the_same_archive():
    from runtime.local_evidence_routing_candidate_v03 import compile_candidate_evidence_v03
    source,request=archive()
    old_source=deepcopy(source);old_request=deepcopy(request)
    legacy=deepcopy(request)
    legacy["race"]["distance"]=legacy["race"].pop("distance_m")
    legacy["race"]["venue"]="FNB"
    reg=ROOT/"mapping/local_evidence_feature_rule_registry_v0.3_candidate_20260925_evidence_routing.json"
    a=compile_candidate_evidence_v03(source,request,reg)
    b=compile_candidate_evidence_v03(source,legacy,reg)
    assert source==old_source and request==old_request
    assert a["candidate_evidence_compiler"]["resolved_race_units"]["distance_m"]==1500
    assert [r["evidence_features"] for r in a["runners"]]==[r["evidence_features"] for r in b["runners"]]
    assert sum(not r["evidence_features"]["same_distance"]["missing"] for r in a["runners"])==11
    assert a["candidate_v03_policy"]["production_effect"]=="NONE"
    assert a["candidate_v03_policy"]["weight_change_from_v01"] is False


def young_race_archive():
    rid="KM-LOCAL-FNB-20261002-R01-LIVE-R1"
    checkpoint=resolve_phase("LOCAL-"+rid+"-EXEC","SOURCE")
    assert checkpoint
    data=(checkpoint["run_dir"]/"source_receipt_envelope.json").read_bytes()
    assert hashlib.sha256(data).hexdigest()=="24abc7e8d3d43381a8d4eb0bb2dae93b21e1cb746df50b907bc014f626340a35"
    return json.loads(data)["artifact"],json.loads((ROOT/"runtime/formal_intents"/(rid+".json")).read_text())


def test_real_fnb_unresolved_age_class_stays_unknown_in_nci_and_witness():
    from runtime.local_base63_source_witness import verify
    from runtime.local_fullnumerical_production import materialize_production
    source,request=young_race_archive()
    old_source=deepcopy(source);old_request=deepcopy(request)
    assert request["race"]["name"]=="3歳七" and request["race"]["class"]=="3歳"
    numeric=materialize_production(source,request,request["required_indices"])
    registry=json.loads((ROOT/"mapping/local_evidence_feature_rule_registry_v1.1_production_numerical_20261008.json").read_text())
    witness=verify(source,request,registry,numeric)
    assert source==old_source and request==old_request
    assert witness["component_match_counts"]=={"MATCH":693}
    assert witness["index_match_counts"]=={"MATCH":99}
    assert witness["missing_count"]==404
    assert witness["independent_official_race_context"]["class_score_status"]=="CLASS_UNRESOLVED_CANONICAL_NEUTRAL"
    for runner in numeric["runners"]:
        for name in ("current_class","race_set_level","class_change_pressure","transfer_class"):
            feature=runner["evidence_features"][name]
            assert feature["score"]==52 and feature["missing"] is True and feature["coverage"]==0
    assert witness["model_consumers_authorized"] is False
    assert witness["all_63_rules_empirical_measurement_complete"] is False


@pytest.mark.parametrize("change",[
    {"name":"3歳八"}, {"name":""}, {"class":"4歳"}, {"class":"未知"}, {"class":"C3"},
    {"name":"オッズ","class":"オッズ"},
])
def test_unknown_class_score_equality_never_replaces_raw_name_or_class_identity(change):
    from runtime.local_base63_source_witness import verify
    source,request=young_race_archive()
    request=deepcopy(request);request["race"].update(change)
    registry=json.loads((ROOT/"mapping/local_evidence_feature_rule_registry_v1.1_production_numerical_20261008.json").read_text())
    with pytest.raises(ValueError,match="OFFICIAL_REQUEST_CLASS_CONFLICT"):
        verify(source,request,registry)


def test_known_c3_ordinal52_remains_observed_while_unparsed_class_is_unknown():
    source,request=archive()
    reg=ROOT/"mapping/local_evidence_feature_rule_registry_v1.1_production_numerical_20261008.json"
    compiled=compile_candidate_evidence(source,request,reg)
    for runner in compiled["runners"]:
        feature=runner["evidence_features"]["current_class"]
        assert feature["score"]==52 and feature["missing"] is False and feature["coverage"]==1


@pytest.mark.parametrize("label",["C4","A9","A10","Ａ９","B3_C4","3歳"])
def test_unregistered_class_labels_do_not_become_observed_neutral_ordinals(label):
    from runtime.local_nar_evidence_candidate import _class_score
    from runtime.local_base63_source_witness import grade
    assert _class_score(label)==(52.0,"CLASS_UNRESOLVED_CANONICAL_NEUTRAL")
    assert grade(label)==(52,"CLASS_UNRESOLVED_CANONICAL_NEUTRAL")


def classless_intent_archive():
    rid="KM-LOCAL-FNB-20260930-R12-LIVE-R1"
    checkpoint=resolve_phase("LOCAL-"+rid+"-EXEC","SOURCE")
    assert checkpoint
    data=(checkpoint["run_dir"]/"source_receipt_envelope.json").read_bytes()
    assert hashlib.sha256(data).hexdigest()=="b814605111d667118afd50c6eff63f625e36594df8f692d59cd443154bfd85a5"
    return json.loads(data)["artifact"],json.loads((ROOT/"runtime/formal_intents"/(rid+".json")).read_text())


def test_missing_intent_class_uses_actual_frozen_official_title_without_new_ordinal():
    from runtime.local_nar_evidence_candidate import _current_class_label
    from runtime.local_fullnumerical_production import materialize_production
    from runtime.local_base63_source_witness import verify
    source,request=classless_intent_archive()
    original_source=deepcopy(source);original_request=deepcopy(request)
    assert not request["race"].get("class")
    label,basis=_current_class_label(request,source)
    assert label=="長月特別Ｂ２二Ｂ３一"
    assert basis=="HASH_VERIFIED_FROZEN_OFFICIAL_FNB_RACE_TITLE"
    numeric=materialize_production(source,request,request["required_indices"])
    for runner in numeric["runners"]:
        current=runner["evidence_features"]["current_class"]
        assert current["score"]==74 and current["missing"] is False
    registry=json.loads((ROOT/"mapping/local_evidence_feature_rule_registry_v1.1_production_numerical_20261008.json").read_text())
    witness=verify(source,request,registry,numeric)
    assert witness["component_match_counts"]=={"MATCH":756}
    assert witness["index_match_counts"]=={"MATCH":108}
    assert witness["missing_count"]==245
    assert source==original_source and request==original_request


@pytest.mark.parametrize("mutation",["raw_hash","snapshot_hash","url_identity","future_fetch","foreign_final_url","wrong_final_race","post_cutoff_flag","after_cutoff"])
def test_missing_class_header_extraction_does_not_accept_unqualified_raw(mutation):
    from runtime.local_nar_evidence_candidate import _current_class_label
    source,request=classless_intent_archive();source=deepcopy(source)
    card=next(s for s in source["sources"] if s["source_class"]=="OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT")
    if mutation=="raw_hash":card["raw_sha256"]="0"*64
    elif mutation=="snapshot_hash":card["snapshot_sha256"]="0"*64
    elif mutation=="url_identity":card["requested_url"]=card["requested_url"].replace("k_raceNo=12","k_raceNo=11")
    elif mutation=="future_fetch":card["fetched_at"]="2026-09-30T11:42:29+00:00"
    elif mutation=="foreign_final_url":card["final_url"]="https://example.org/card"
    elif mutation=="wrong_final_race":card["final_url"]=card["final_url"].replace("k_raceNo=12","k_raceNo=11")
    elif mutation=="post_cutoff_flag":card["cutoff_relation"]="POST_CUTOFF"
    else:card["fetched_at"]="2026-09-30T11:44:01+00:00"
    if mutation!="snapshot_hash":
        value={k:v for k,v in card.items() if k!="snapshot_sha256"}
        card["snapshot_sha256"]=hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    if mutation=="future_fetch":
        assert _current_class_label(request,source)==("","OFFICIAL_CURRENT_CLASS_NOT_IN_ORIGINAL_FREEZE")
    else:
        with pytest.raises(LocalCandidateEvidenceError,match="CURRENT_CLASS_"):
            _current_class_label(request,source)

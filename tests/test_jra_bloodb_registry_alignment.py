"""Regression for the 2026-11-15 1R/2R stop (UNREGISTERED_RULE_ID).

The three Owner-approved BLOOD BIAS feature/rule pairs must compile through the
real Evidence Compiler with the Production registry (v1.3, fixed in 82da3a2df)
and must still fail against the pre-fix registry bytes. Provenance checks
(evidence_refs, source_fact, unknown rule ids) stay enforced.
"""
import copy, json, subprocess, sys
sys.path.insert(0, "runtime")
import pytest
from evidence_feature_compiler import (compile_evidence_feature_ledger, EvidenceCompilerError,
                                       _load_rule_registry, RULE_REGISTRY_PATH)
from jra_evidence_to_base_production import load_mapping

PAIRS = [
    ("pedigree_class", "KM-JRA-BLOODB-SIRE-GENERATION-RANK-BAND-v1"),
    ("pedigree_distance", "KM-JRA-BLOODB-SIRE-DISTANCE-TYPE-RANK-BAND-v1"),
    ("expert_support", "KM-JRA-BLOODB-PEDIGREE-EVALUATION-MARK-v1"),
]
PRE_FIX = "f2a8e5807147d5abcb5b1572fb32879318873d21"  # FKS 11/15 R02 failing checkout


def _fixture(feature, rule):
    req = json.load(open("runtime/requests/KM-JRA-HSN-20260921-R12.json", encoding="utf-8"))
    runners = copy.deepcopy(req["runners"])
    feats = runners[0]["evidence_features"]
    x = feats.setdefault(feature, copy.deepcopy(next(iter(feats.values()))))
    x["rule_id"] = rule
    x["source_fact"] = "BLOOD BIAS band=STRONG (regression fixture)"
    x["evidence_refs"] = ["external:bloodb:regression"]
    return req, runners


def _pre_fix_registry():
    try:
        raw = subprocess.run(["git", "show", f"{PRE_FIX}:{RULE_REGISTRY_PATH}"],
                             capture_output=True, check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("pre-fix commit not available in this checkout")
    return json.loads(raw)


@pytest.mark.parametrize("feature,rule", PAIRS)
def test_production_registry_accepts_owner_bloodb_rule(feature, rule):
    mp = load_mapping("mapping/jra_base_index_evidence_mapping_v1.0_20260921.json")
    req, runners = _fixture(feature, rule)
    out = compile_evidence_feature_ledger(req["race_id"], req["source_snapshot_sha256"], runners, mp)
    rid = str(runners[0]["runner_id"])
    assert out["runners"][rid]["features"][feature]["rule_id"] == rule if "features" in out["runners"][rid] \
        else out["runners"][rid][feature]["rule_id"] == rule


@pytest.mark.parametrize("feature,rule", PAIRS)
def test_pre_fix_registry_rejects_same_pair(feature, rule):
    mp = load_mapping("mapping/jra_base_index_evidence_mapping_v1.0_20260921.json")
    req, runners = _fixture(feature, rule)
    with pytest.raises(EvidenceCompilerError, match="UNREGISTERED_RULE_ID"):
        compile_evidence_feature_ledger(req["race_id"], req["source_snapshot_sha256"], runners, mp,
                                        rule_registry=_pre_fix_registry())


def test_provenance_still_enforced():
    mp = load_mapping("mapping/jra_base_index_evidence_mapping_v1.0_20260921.json")
    req, runners = _fixture(*PAIRS[0])
    runners[0]["evidence_features"]["pedigree_class"]["evidence_refs"] = []
    with pytest.raises(EvidenceCompilerError, match="EVIDENCE_REFS_MISSING"):
        compile_evidence_feature_ledger(req["race_id"], req["source_snapshot_sha256"], runners, mp)
    req, runners = _fixture("pedigree_class", "KM-JRA-BLOODB-UNKNOWN-v1")
    with pytest.raises(EvidenceCompilerError, match="UNREGISTERED_RULE_ID"):
        compile_evidence_feature_ledger(req["race_id"], req["source_snapshot_sha256"], runners, mp)

import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
sys.path.insert(0, str(ROOT / "runtime" / "jra_source_runtime"))

import jra_index_provenance_builder as B  # noqa: E402
from jra_external_pack_builder import (bloodb_from_compact, build_packs, distance_type,  # noqa: E402
                                       rank_band, race_id_from_rcode, race_id_from_tsl)
from jra_supplemental_evidence_pack import (SupplementalEvidenceError,  # noqa: E402
                                            apply_supplemental_evidence_pack)


VALS = {k: 50.0 + i for i, k in enumerate(B.BASE)}


def test_zai_v10_unchanged_and_v11_weights():
    v10 = (VALS["HPI"]*.20 + VALS["SSI"]*.17 + VALS["CFI"]*.10 + VALS["RFI"]*.08 + VALS["JTI"]*.05
           + VALS["CSI"]*.05 + VALS["TRI"]*.05 + VALS["BWI"]*.05 + VALS["GCI"]*.08 + VALS["PRI"]*.12
           + VALS["KGI"]*.05)
    assert B.zai_win_value(VALS, "v1.0") == v10
    for table in (B.ZAI_WIN_WEIGHTS, B.ZAI_PLACE_WEIGHTS):
        assert abs(sum(table["v1.0"].values()) - 1) < 1e-9
        assert abs(sum(table["v1.1"].values()) - 1) < 1e-9
        assert table["v1.1"]["BVI"] == 0.15 and table["v1.1"]["VMI"] == 0.05
        assert table["v1.1"]["HPI"] == round(table["v1.0"]["HPI"] * .8, 6)


def test_zai_version_gate_by_race_date():
    assert B.zai_formula_version("KM-JRA-TKY-20261114-R11") == "v1.0"
    assert B.zai_formula_version("KM-JRA-TKY-20261115-R01") == "v1.1"
    assert B.zai_formula_version(None) == "v1.0"


def test_rank_and_distance_bands():
    assert rank_band("1") == "EXCEPTIONAL" and rank_band("10") == "VERY_STRONG"
    assert rank_band("20") == "STRONG" and rank_band("35") == "POSITIVE"
    assert rank_band("55") == "NEUTRAL" and rank_band("75") == "MIXED" and rank_band("99") == "CAUTION"
    assert rank_band("") is None and rank_band("注") is None
    assert distance_type("芝", 1400) == "P" and distance_type("芝", 1800) == "S" and distance_type("芝", 2200) == "T"
    assert distance_type("ダ", 1150) == "P" and distance_type("ダ", 1700) == "S" and distance_type("ダ", 1800) == "T"


def test_race_ids():
    assert race_id_from_rcode("2026111505050411") == "KM-JRA-TKY-20261115-R11"
    assert race_id_from_rcode("2026111503030401") == "KM-JRA-FKS-20261115-R01"
    assert race_id_from_rcode("2026111508050412") == "KM-JRA-KYO-20261115-R12"
    assert race_id_from_tsl("20261115", "/20261115/0520260504/11/first.html") == "KM-JRA-TKY-20261115-R11"


def _compact():
    return {"captured_at": "2026-11-14T06:10:09Z", "races": [
        ["2026111505050411", "芝1400", "1:21:9::67:53:79:,4:3:6:5:1:3:21:血,9::19:35:49:29:28:"],
        ["2026111503030404", "障2750", "1:::::::"]]}


def _tsl():
    return {"date8": "20261115", "kind": "first", "captured_at": "2026-11-15T00:10:00Z", "races": [
        {"url": "/20261115/0520260504/11/first.html",
         "horses": [{"no": 1, "mark": "◎"}, {"no": 4, "mark": ""}, {"no": 9, "mark": "×"}]}]}


def test_build_packs_bands_and_no_raw_values():
    packs = build_packs(bloodb_from_compact(_compact()), _tsl(), ingested_at="2026-11-15T00:20:00Z")
    assert set(packs) == {"KM-JRA-TKY-20261115-R11"}  # jump race excluded
    p = packs["KM-JRA-TKY-20261115-R11"]
    f = p["runner_features"]
    assert f["4"]["sire_track_signal"]["category"] == "EXCEPTIONAL"   # CR 3
    assert f["4"]["pedigree_class"]["category"] == "VERY_STRONG"      # GR 6
    assert f["4"]["pedigree_distance"]["category"] == "EXCEPTIONAL"   # p (芝1400) = 1
    assert f["4"]["expert_support"]["category"] == "VERY_STRONG"      # 血
    assert "sire_track_signal" not in f["9"]                         # blank CR
    assert f["1"]["external_index_support"]["category"] == "VERY_STRONG"
    assert f["4"]["external_index_support"]["category"] == "CAUTION"
    assert f["9"]["external_index_support"]["category"] == "MIXED"
    text = json.dumps(p, ensure_ascii=False)
    assert "CR=" not in text and ":21:9:" not in text
    assert p["captured_at"] == "2026-11-15T00:10:00Z"
    material = {k: v for k, v in p.items() if k != "pack_sha256"}
    from jra_external_pack_builder import sha
    assert sha(material) == p["pack_sha256"]


def _request(rids, cutoff="2026-11-15T15:15:00+09:00"):
    return {"race_id": "KM-JRA-TKY-20261115-R11", "prediction_cutoff": cutoff,
            "runners": [{"runner_id": r, "evidence_features": {}} for r in rids]}


def _mapping():
    return json.loads((ROOT / "mapping/jra_base_index_evidence_mapping_v1.0_20260921.json").read_text())


def test_apply_pack_registered_rules_and_scratch_filter(monkeypatch):
    monkeypatch.chdir(ROOT)
    pack = build_packs(bloodb_from_compact(_compact()), _tsl(),
                       ingested_at="2026-11-15T00:20:00Z")["KM-JRA-TKY-20261115-R11"]
    req, att = apply_supplemental_evidence_pack(_request(["1", "4"]), pack, _mapping())
    assert att["dropped_runners_not_in_official_universe"] == ["9"]
    feats = {r["runner_id"]: r["evidence_features"] for r in req["runners"]}
    assert feats["4"]["sire_track_signal"]["rule_id"] == "KM-JRA-BLOODB-SIRE-COURSE-RANK-BAND-v1"
    assert feats["1"]["external_index_support"]["category"] == "VERY_STRONG"


def test_apply_pack_rejects_capture_after_cutoff(monkeypatch):
    monkeypatch.chdir(ROOT)
    pack = build_packs(bloodb_from_compact(_compact()), _tsl(),
                       ingested_at="2026-11-15T00:20:00Z")["KM-JRA-TKY-20261115-R11"]
    with pytest.raises(SupplementalEvidenceError):
        apply_supplemental_evidence_pack(_request(["1", "4", "9"], cutoff="2026-11-15T09:00:00+09:00"),
                                         pack, _mapping())


def test_legacy_pack_universe_mismatch_still_fails(monkeypatch):
    monkeypatch.chdir(ROOT)
    pack = build_packs(bloodb_from_compact(_compact()), _tsl(),
                       ingested_at="2026-11-15T00:20:00Z")["KM-JRA-TKY-20261115-R11"]
    legacy = copy.deepcopy(pack)
    legacy.pop("owner_decision")
    from jra_external_pack_builder import sha
    legacy["pack_sha256"] = sha({k: v for k, v in legacy.items() if k != "pack_sha256"})
    with pytest.raises(SupplementalEvidenceError, match="UNIVERSE_MISMATCH"):
        apply_supplemental_evidence_pack(_request(["1", "4"]), legacy, _mapping())


def test_resolver_attaches_pack(tmp_path):
    from jra_race_day_resolver import attach_supplemental_pack
    d = tmp_path / "runtime/jra_supplemental_packs"
    d.mkdir(parents=True)
    (d / "KM-JRA-TKY-20261115-R11.json").write_text(json.dumps({"race_id": "KM-JRA-TKY-20261115-R11"}))
    intent = attach_supplemental_pack({"race_id": "KM-JRA-TKY-20261115-R11"}, tmp_path)
    assert intent["supplemental_evidence_pack"]["race_id"] == "KM-JRA-TKY-20261115-R11"
    assert "supplemental_evidence_pack" not in attach_supplemental_pack({"race_id": "KM-JRA-TKY-20261115-R10"}, tmp_path)
    (d / "KM-JRA-TKY-20261115-R12.json").write_text(json.dumps({"race_id": "OTHER"}))
    i = attach_supplemental_pack({"race_id": "KM-JRA-TKY-20261115-R12"}, tmp_path)
    assert i["supplemental_evidence_pack_skipped"] == "PACK_RACE_ID_MISMATCH"

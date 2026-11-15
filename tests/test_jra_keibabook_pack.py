"""Owner decision 2026-11-15: Keibabook workout / stable-comment bands in Production packs."""
import json, sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "runtime"), str(ROOT / "runtime" / "jra_source_runtime")]
from jra_external_pack_builder import KEIBABOOK_RULES, build_packs, keibabook_races  # noqa: E402
from jra_supplemental_evidence_pack import apply_supplemental_evidence_pack  # noqa: E402
from evidence_feature_compiler import _load_rule_registry  # noqa: E402

BANDS = {"date": "2026-11-15", "captured_at": "2026-11-14T22:34:06.425Z",
         "res": {"04": [["202605040411", "1NVS,4NXN,9N-N"]], "00": [["202605000401", "1NSN"]],
                 "06": [["202603060412", "16NVN"]]}}


def test_race_id_mapping_matches_official_venues():
    ids = {rid for rid, _, _ in keibabook_races(BANDS)}
    assert ids == {"KM-JRA-TKY-20261115-R11", "KM-JRA-KYO-20261115-R01", "KM-JRA-FKS-20261115-R12"}


def test_bands_to_registered_features_and_no_raw_text():
    p = build_packs(None, None, ingested_at="2026-11-14T22:40:00Z", keibabook=BANDS)["KM-JRA-TKY-20261115-R11"]
    f = p["runner_features"]
    assert f["1"]["workout_speed"]["category"] == "VERY_STRONG"
    assert f["1"]["stable_comment_state"]["category"] == "STRONG"
    assert f["4"]["workout_speed"]["category"] == "EXCEPTIONAL"
    assert "workout_speed" not in f["9"]  # '-' = no in-window workout: left UNKNOWN, never filled
    assert p["owner_decision_keibabook"] == "OWNER-2026-11-15-KEIBABOOK-WORKOUT-STABLE-PRODUCTION"
    assert "【" not in json.dumps(p, ensure_ascii=False)  # trainer comment text never enters the pack


@pytest.mark.parametrize("feature", sorted(KEIBABOOK_RULES))
def test_rule_ids_registered_in_production_registry(feature):
    # the 11/15 BLOODB lesson: the registry the compiler actually reads must hold the pair
    reg = _load_rule_registry()
    assert KEIBABOOK_RULES[feature] in reg["feature_rules"][feature]


def test_pack_applies_through_supplemental_guard(monkeypatch):
    monkeypatch.chdir(ROOT)
    pack = build_packs(None, None, ingested_at="2026-11-14T22:40:00Z", keibabook=BANDS)["KM-JRA-TKY-20261115-R11"]
    req = {"race_id": "KM-JRA-TKY-20261115-R11", "prediction_cutoff": "2026-11-15T14:25:00+09:00",
           "runners": [{"runner_id": r, "evidence_features": {}} for r in ["1", "4", "9"]]}
    mapping = json.loads((ROOT / "mapping/jra_base_index_evidence_mapping_v1.0_20260921.json").read_text())
    out, att = apply_supplemental_evidence_pack(req, pack, mapping)
    feats = {r["runner_id"]: r["evidence_features"] for r in out["runners"]}
    assert feats["4"]["workout_speed"]["rule_id"] == "JRA-WORKOUT-FINAL1F-BAND-v1"


def test_owner_pack_keeps_official_precedence(monkeypatch):
    monkeypatch.chdir(ROOT)
    pack = build_packs(None, None, ingested_at="2026-11-14T22:40:00Z", keibabook=BANDS)["KM-JRA-TKY-20261115-R11"]
    official = {"category": "NEUTRAL", "rule_id": "JRA-WORKOUT-CAPABILITY-COMMENT-v1", "evidence_refs": ["OFFICIAL:1"],
                "source_fact": "official workout assessment", "result_derived": False}
    req = {"race_id": "KM-JRA-TKY-20261115-R11", "prediction_cutoff": "2026-11-15T14:25:00+09:00",
           "runners": [{"runner_id": "1", "evidence_features": {"workout_capability": dict(official)}},
                       {"runner_id": "4", "evidence_features": {}}, {"runner_id": "9", "evidence_features": {}}]}
    mapping = json.loads((ROOT / "mapping/jra_base_index_evidence_mapping_v1.0_20260921.json").read_text())
    out, att = apply_supplemental_evidence_pack(req, pack, mapping)
    f1 = out["runners"][0]["evidence_features"]
    assert f1["workout_capability"] == official                # official kept, not merged
    assert f1["workout_speed"]["category"] == "VERY_STRONG"    # gap filled
    assert att["official_precedence_skipped"] == ["1:workout_capability"]


def test_u13_newcomer_signal_registered_and_emitted():
    from jra_external_pack_builder import bloodb_from_compact
    bb = bloodb_from_compact({"captured_at": "2026-11-20T21:00:00Z",
                              "races": [["2026112105050405", "芝1600", "3:4:21::31:29:36:注"]]})
    f = build_packs(bb, None, ingested_at="2026-11-20T21:10:00Z")["KM-JRA-TKY-20261121-R05"]["runner_features"]["3"]
    assert f["sire_newcomer_signal"]["category"] == f["sire_track_signal"]["category"] == "VERY_STRONG"  # CR 4
    reg = _load_rule_registry()
    assert f["sire_newcomer_signal"]["rule_id"] in reg["feature_rules"]["sire_newcomer_signal"]

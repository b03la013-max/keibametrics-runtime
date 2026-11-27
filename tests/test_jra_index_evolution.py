import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime")); sys.path.insert(0, str(ROOT / "runtime/analysis"))
import jra_index_evolution as E  # noqa: E402


def test_pava_is_non_decreasing():
    fit = E._pava([(0.1, 10), (0.3, 10), (0.2, 10), (0.5, 10)])
    assert fit == sorted(fit) and abs(fit[1] - 0.25) < 1e-9


def _rows(n, d, w_c=True, w_p=True, surface="芝", venue="TKY"):
    return [{"race_id": f"r{i}", "d": d, "w_c": w_c, "w_p": w_p, "surface": surface, "venue": venue} for i in range(n)]


def test_decide_rejects_interim_degradation_and_waits_below_100():
    c = {"candidate_id": "x", "status": "OOS_EVALUATING", "stage": "S1_CONVERSION", "type": "T"}
    assert E.decide(c, {"eligible_races": 30, "paired_diff_mean": .5, "ci95": [.2, .8]}, _rows(30, .5))[0] == "REJECTED"
    assert E.decide(c, {"eligible_races": 60, "paired_diff_mean": -.5, "ci95": [-.8, -.2]}, _rows(60, -.5))[0] == "OOS_EVALUATING"


def test_decide_eligible_only_without_worse_strata_or_winner_drop():
    c = {"candidate_id": "x", "status": "OOS_EVALUATING", "stage": "S2_INDEX_FORMULA", "type": "T"}
    ok = E.decide(c, {"eligible_races": 100, "paired_diff_mean": -.3, "ci95": [-.5, -.1]}, _rows(100, -.3))
    assert ok[0] == "PROMOTION_ELIGIBLE" and ok[1]["eligible"] and "rollback" in ok[1]["adoption"]
    rows = _rows(60, -.8) + _rows(40, .5, surface="ダ")
    bad = E.decide(c, {"eligible_races": 100, "paired_diff_mean": -.28, "ci95": [-.5, -.05]}, rows)
    assert bad[0] == "OOS_EVALUATING" and bad[1]["worse_strata"]
    drop = _rows(100, -.3, w_c=False, w_p=True)
    assert E.decide(c, {"eligible_races": 100, "paired_diff_mean": -.3, "ci95": [-.5, -.1]}, drop)[0] == "OOS_EVALUATING"


def test_apply_changes_only_the_candidate_part():
    m = E._mapping(ROOT)
    s1 = E.apply(m, {"stage": "S1_CONVERSION", "category_scale": {**m["category_scale"], "WEAK": 40}})
    assert s1["category_scale"]["WEAK"] == 40 and m["category_scale"]["WEAK"] != 40
    s2 = E.apply(m, {"stage": "S2_INDEX_FORMULA", "profile": "ESTABLISHED", "index": "BWI", "feature_weights": {"weight_load_fit": 1.0}})
    assert s2["index_profiles"]["ESTABLISHED"]["BWI"] == {"weight_load_fit": 1.0}
    assert s2["index_profiles"]["ESTABLISHED"]["HPI"] == m["index_profiles"]["ESTABLISHED"]["HPI"]


def test_sidecar_is_frozen_once_and_reproduces_production_values(tmp_path):
    rid = "KM-JRA-TKY-20261123-R11"
    (tmp_path / "runtime/requests").mkdir(parents=True)
    src = ROOT / f"runtime/requests/{rid}-LIVE-R1-FORMAL.json"
    (tmp_path / f"runtime/requests/{rid}-LIVE-R1-FORMAL.json").write_text(src.read_text())
    (tmp_path / "mapping").mkdir()
    (tmp_path / "mapping/jra_base_index_evidence_mapping_v1.0_20260921.json").write_text((ROOT / "mapping/jra_base_index_evidence_mapping_v1.0_20260921.json").read_text())
    a = E.features_sidecar(tmp_path, rid)
    b = E.features_sidecar(tmp_path, rid)
    assert a["sha256"] == b["sha256"] and a["frozen_at"] == b["frozen_at"]
    vals = E.base_values(a, E._mapping(ROOT))
    final = json.loads((ROOT / f"runtime/final_artifacts/{rid}.json").read_text())
    rep = final["final_prediction_package"]["index_provenance_replay"]["runners"]
    h = next(iter(vals))
    assert abs(vals[h]["HPI"] - rep[h]["base_final_values"]["HPI"]) < 0.05


def test_register_respects_stage_cap_and_records_tried(tmp_path, monkeypatch):
    monkeypatch.setattr(E, "_train_rows", lambda root, rows: [(r, None) for r in rows])
    monkeypatch.setattr(E, "gen_s1", lambda train, m: [{"stage": "S1_CONVERSION", "type": f"T{i}", "category_scale": {"X": i}} for i in range(5)])
    monkeypatch.setattr(E, "gen_s2", lambda train, m: [])
    (tmp_path / "mapping").mkdir()
    (tmp_path / "mapping/jra_base_index_evidence_mapping_v1.0_20260921.json").write_text(
        (ROOT / "mapping/jra_base_index_evidence_mapping_v1.0_20260921.json").read_text())
    monkeypatch.setattr(E, "_mapping", lambda root: {})
    rows = [{"race_id": f"KM-JRA-TKY-202611{10 + i // 30:02d}-R{i % 12 + 1:02d}"} for i in range(60)]
    reg, out = E.register(tmp_path, rows, {})
    assert out["registered"] == E.MAX_ACTIVE
    tried = json.loads((tmp_path / E.OUT / "tried_ledger.json").read_text())["entries"]
    assert len(tried) == 5 and sum(e["outcome"].startswith("NOT_REGISTERED:STAGE_CAP") for e in tried) == 2
    reg2, out2 = E.register(tmp_path, rows, {})
    assert out2["registered"] == 0  # same training window: no new generation

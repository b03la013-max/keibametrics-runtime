import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime/analysis"))
import jra_production_consumer_chain_audit as a  # noqa: E402

FINAL = ROOT / "runtime/final_artifacts/KM-JRA-TKY-20261108-R11.json"
MAPPING = json.loads((ROOT / "mapping/jra_base_index_evidence_mapping_v1.0_20260921.json").read_text())["index_profiles"]


def _audit(tmp_path, mutate=None):
    d = json.loads(FINAL.read_text())
    if mutate:
        mutate(d)
    p = tmp_path / "runtime/final_artifacts" / FINAL.name
    p.parent.mkdir(parents=True)
    p.write_text(json.dumps(d))
    # reuse the real signed SOURCE checkpoint for the Active universe
    src = ROOT / "runtime/executions"
    (tmp_path / "runtime/executions").symlink_to(src)
    return a.audit_final(p, tmp_path, MAPPING)


def test_stored_signed_final_passes_every_chain_check(tmp_path):
    r = _audit(tmp_path)
    assert r["pass"], r["checks"]
    assert r["full20_cells"] == r["full20_required"] == 20 * r["active_count"]
    assert r["observation"]["present_components"] < r["observation"]["required_components"]


def test_tampered_base_value_breaks_arithmetic_or_static(tmp_path):
    def m(d):
        rs = d["final_prediction_package"]["index_provenance_replay"]["runners"]
        k = next(iter(rs))
        rs[k]["base_final_values"]["HPI"] += 10
    r = _audit(tmp_path, m)
    assert not r["checks"]["C3_full20_arithmetic"]


def test_static_ranking_not_from_zai_win_fails(tmp_path):
    def m(d):
        sp = d["static_prediction"]
        sp["ranking"] = list(reversed(sp["ranking"]))
    r = _audit(tmp_path, m)
    assert not r["checks"]["C4_static_consumed"]


def test_krs_short_run_or_wrong_parameter_map_fails(tmp_path):
    def m(d):
        d["krs_run_receipt"]["receipt"]["actual_run_count"] = 1000
    assert not _audit(tmp_path, m)["checks"]["C5_krs_actual"]


def test_source_snapshot_mismatch_fails(tmp_path):
    def m(d):
        d["static_prediction"]["source_basis_snapshot_sha256"] = "0" * 64
    assert not _audit(tmp_path, m)["checks"]["C1_source_binding"]


def test_final_after_post_fails(tmp_path):
    def m(d):
        d["final_freeze_timestamp"] = d["scheduled_post_at"]
    assert not _audit(tmp_path, m)["checks"]["C6_final_prestart"]

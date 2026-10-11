"""Art.3 DCR information policy (owner-authorized 2026-10-11, R48)."""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
import jra_evidence_to_base_production as m


def mapping():
    return {"mapping_id": "JRA-EVIDENCE-TO-BASE-MAPPING-v1.0-PRODUCTION-20260921",
            "category_scale": {"STRONG": 80.0, "NEUTRAL": 50.0, "WEAK": 25.0},
            "profiles": {"ESTABLISHED": {"minimum_index_coverage_weight": 0.42}},
            "index_profiles": {"ESTABLISHED": {"TRI": {"a": 0.3, "b": 0.7}}}}


def feat(cat):
    return {"category": cat, "evidence_refs": ["x"], "source_fact": "f", "rule_id": "r"}


def test_unpublished_information_is_neutral_scaled_by_dcr(monkeypatch):
    monkeypatch.setattr(m, "DCR_INFORMATION_POLICY_ENABLED", True)
    none = m._weighted_index("TRI", "ESTABLISHED", {}, mapping())
    assert none["value"] == 50.0 and none["dcr"] == 0.0
    assert none["information_status"] == "INFORMATION_INSUFFICIENT_DCR_ART3"
    assert any("OFFICIALLY_UNPUBLISHED:a,b" in r for r in none["evidence_refs"])
    part = m._weighted_index("TRI", "ESTABLISHED", {"a": feat("STRONG")}, mapping())
    assert part["value"] == pytest.approx(50 + (80 - 50) * 0.3)   # 59.0, never 80
    full = m._weighted_index("TRI", "ESTABLISHED", {"a": feat("STRONG"), "b": feat("WEAK")}, mapping())
    assert "information_status" not in full


def test_invalid_or_non_production_feature_still_fails_closed(monkeypatch):
    monkeypatch.setattr(m, "DCR_INFORMATION_POLICY_ENABLED", True)
    bad = dict(feat("STRONG"), production_authority=False)
    with pytest.raises(m.ProductionMappingError, match="NON_PRODUCTION"):
        m._weighted_index("TRI", "ESTABLISHED", {"a": bad}, mapping())
    with pytest.raises(m.ProductionMappingError, match="CATEGORY_INVALID"):
        m._weighted_index("TRI", "ESTABLISHED", {"a": feat("MADE_UP")}, mapping())


def test_strict_mode_still_blocks(monkeypatch):
    monkeypatch.setattr(m, "DCR_INFORMATION_POLICY_ENABLED", False)
    with pytest.raises(m.ProductionMappingError, match="INDEX_EVIDENCE_COVERAGE_LOW"):
        m._weighted_index("TRI", "ESTABLISHED", {"a": feat("STRONG")}, mapping())

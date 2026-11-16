import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))

import family_authority_guard as g  # noqa: E402

R52 = json.loads((ROOT / "profiles/KM_FAMILY_CURRENT_AUTHORITY_20261115_R52.json").read_text())
R53 = json.loads((ROOT / "profiles/KM_FAMILY_CURRENT_AUTHORITY_20261116_R53.json").read_text())


def test_r53_resolves_from_2026_11_17_jst():
    _, a = g.resolve_current_authority(ROOT, now=datetime(2026, 11, 17, tzinfo=timezone.utc))
    assert a["manifest_id"] == R53["manifest_id"]
    assert a["predecessor"] == R52["manifest_id"]


def test_r53_changes_only_local():
    changed = {k for k in R53 if R52.get(k) != R53.get(k)}
    assert changed == {"manifest_id", "status", "effective_at", "predecessor", "precedence",
                       "family_scoped_authority", "r53_change_declaration"}
    assert R53["common_family_components"] == R52["common_family_components"]
    for fam in R52["family_scoped_authority"]:
        if fam != "LOCAL":
            assert R53["family_scoped_authority"][fam] == R52["family_scoped_authority"][fam]
    l52, l53 = R52["family_scoped_authority"]["LOCAL"], R53["family_scoped_authority"]["LOCAL"]
    assert {k for k in l53 if l52.get(k) != l53.get(k)} == {
        "status", "numerical_consumption_boundary", "formal_source_amendment", "production_static_owner",
        "formal_runner", "learning_binding"}


def test_r53_local_consumption_owner_authorized_without_new_numerics():
    b = R53["family_scoped_authority"]["LOCAL"]["numerical_consumption_boundary"]
    assert all(b[k] is True for k in ("prediction_authority", "krs_input_authority", "ticket_authority", "capital_authority"))
    assert b["owner_authorization"]["statements"] == ["数式コンシューマは承認します", "品質受入も承認します"]
    assert R53["r53_change_declaration"]["new_numerics"] is False
    assert R53["r53_change_declaration"]["new_selection_policy"] is False
    assert "RECOMMENDATION_ONLY" in b["policy"]


def test_r53_contracts_still_validate():
    for load, check in ((g.load_scope_contract, g.validate_scope_contract),
                        (g.load_lifecycle_contract, g.validate_lifecycle_contract),
                        (g.load_maturity_contract, g.validate_maturity_contract)):
        check(load(R53))

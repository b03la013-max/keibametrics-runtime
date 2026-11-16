import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))

import family_authority_guard as g  # noqa: E402

R53 = json.loads((ROOT / "profiles/KM_FAMILY_CURRENT_AUTHORITY_20261116_R53.json").read_text())
R54 = json.loads((ROOT / "profiles/KM_FAMILY_CURRENT_AUTHORITY_20261116_R54.json").read_text())


def test_r54_resolves_from_2026_11_17_jst():
    _, a = g.resolve_current_authority(ROOT, now=datetime(2026, 11, 17, tzinfo=timezone.utc))
    assert a["manifest_id"] == R54["manifest_id"]
    assert a["predecessor"] == R53["manifest_id"]


def test_r54_changes_only_local():
    assert R54["common_family_components"] == R53["common_family_components"]
    for fam in R53["family_scoped_authority"]:
        if fam != "LOCAL":
            assert R54["family_scoped_authority"][fam] == R53["family_scoped_authority"][fam]
    l53, l54 = R53["family_scoped_authority"]["LOCAL"], R54["family_scoped_authority"]["LOCAL"]
    assert {k for k in l54 if l53.get(k) != l54.get(k)} == {
        "status", "numerical_prediction_consumer", "local_ticket_cap", "improvement_proposal_adoption",
        "research_bc_six_methods"}


def test_r54_owner_decisions_recorded():
    L = R54["family_scoped_authority"]["LOCAL"]
    assert L["numerical_prediction_consumer"]["role_widths"]["W"] == "top 3"
    assert L["local_ticket_cap"]["max_tickets"] == 60
    assert L["research_bc_six_methods"]["status"] == "ABOLISHED"
    assert R54["r54_change_declaration"]["new_numerics"] is False


def test_r54_contracts_still_validate():
    for load, check in ((g.load_scope_contract, g.validate_scope_contract),
                        (g.load_lifecycle_contract, g.validate_lifecycle_contract),
                        (g.load_maturity_contract, g.validate_maturity_contract)):
        check(load(R54))

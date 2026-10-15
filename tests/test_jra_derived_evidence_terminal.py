import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from jra_single_entry_outcome import evidence_terminal_eligible


def base(**kw):
    r = {"auto_handoff_error": "JRA_AUTHORIZED_FULL20_INCOMPLETE", "production_full_numerical_ready": False,
         "first_blocked_stage": "PRODUCTION_FEATURE_INDEX_CLOSURE", "partial_base_blocked_count": 0}
    r.update(kw)
    return r


def test_derived_dcr_gap_is_an_evidence_terminal():
    assert evidence_terminal_eligible(base(production_numerical_error="DCR_COMPONENT_UNRESOLVED:6:bodyweight_range"))


def test_base_gap_still_eligible_and_other_errors_not():
    assert evidence_terminal_eligible(base(partial_base_blocked_count=3))
    assert not evidence_terminal_eligible(base(production_numerical_error="SOMETHING_ELSE"))
    assert not evidence_terminal_eligible(base(production_full_numerical_ready=True,
                                               production_numerical_error="DCR_COMPONENT_UNRESOLVED:1:x"))

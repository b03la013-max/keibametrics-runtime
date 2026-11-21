"""ChatGPT 11/21 P0-3: the raw RESULT diagnosis is ranking-only and must say so."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from runtime.local_autopilot.settle import diagnose


def test_diagnosis_declares_rank_only_scope():
    d = diagnose([3, 1, 2, 4], [1, 3, 2], pay_hit=True)
    assert d['scope'] == 'RANK_ONLY_NOT_TICKET_FACE'
    assert d['first_failure'] == 'W_WIDTH_OR_ROLE'   # unchanged classification

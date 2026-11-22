"""11/22 ばんえい反省（ChatGPT）P0-4：直前見直しの変更台帳（騎手・馬体重・人気・オッズ・出走の有無の before/after）。証拠のみ。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'runtime', 'banei_autopilot'))
import run  # noqa: E402


def rec(rows, at):
    return {'frozen_at': at, 'evaluation': {'rows': rows}}


def test_change_ledger_records_jockey_and_weight_before_after():
    r1 = rec([{'no': 1, 'jockey': 'A', 'body_weight': None, 'pop': 2, 'odds': 4.1},
              {'no': 4, 'jockey': 'B', 'body_weight': None, 'pop': 1, 'odds': 2.0},
              {'no': 5, 'jockey': 'C', 'body_weight': None, 'pop': 3, 'odds': 6.0}], '2026-11-22T19:00:00+09:00')
    r2 = rec([{'no': 1, 'jockey': 'A', 'body_weight': 1010, 'pop': 2, 'odds': 4.1},
              {'no': 4, 'jockey': 'D', 'body_weight': 980, 'pop': 1, 'odds': 2.0}], '2026-11-22T19:20:00+09:00')
    c = run.change_ledger(r1, r2)
    assert c['changed'] == ['body_weight', 'jockey', 'runner']
    assert c['jockey_changes'] == [{'no': 4, 'field': 'jockey', 'before': 'B', 'after': 'D'}]
    assert {'no': 5, 'field': 'runner', 'before': True, 'after': False} in c['diffs']
    assert c['rev1_frozen_at'].endswith('19:00:00+09:00') and c['rev2_received_at'].endswith('19:20:00+09:00')
    assert c['evidence_only'] is True


def test_change_ledger_empty_when_nothing_changed_and_old_rows_without_fields():
    rows = [{'no': 1, 'pop': 1, 'odds': 1.5}]
    c = run.change_ledger(rec(rows, 'a'), rec([dict(x) for x in rows], 'b'))
    assert c['changed'] == [] and c['diffs'] == []

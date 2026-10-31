"""Only explicit markers in the current number cell are retained as facts."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'runtime/jra_source_runtime'), str(ROOT / 'runtime')]
import jra_race_card_detail as candidate

def parse_cells(markup):
    parser = candidate._DetailTableExtractor()
    parser.feed(markup)
    row = parser.tables[0][0]
    return parser.equipment_cells.get(id(row), {})

class TestEquipmentRetention(unittest.TestCase):
    def test_full_card_retains_current_observation_and_all_prior_fields(self):
        def card(number, history=''):
            return ('''<table><tr><th>枠</th><th>馬番</th><th>馬名</th>
                <th>性齢/負担重量/騎手</th><th>前走</th></tr>
                <tr><td>1</td><td>''' + number + '''</td><td>SYNTHETIC HORSE</td>
                <td>牡3/鹿 57.0kg 騎手名</td><td>''' + history + '''</td></tr></table>''').encode()
        old = candidate.parse_race_card_detail(card('2'), 'text/html;charset=utf-8')
        current = candidate.parse_race_card_detail(card('2<img alt="ブリンカー着用">'),
                                                   'text/html;charset=utf-8')
        observed = current['runners'][0].pop('observed_current_equipment')
        self.assertEqual(observed, {'blinkers_worn': True,
                         'evidence_type': 'JRA_OFFICIAL_CURRENT_HORSE_NUMBER_CELL_MARKER',
                         'marker_alt': 'ブリンカー着用'})
        # The normalized-document digest changes with the newly retained fact;
        # every pre-existing semantic field remains equal.
        self.assertNotEqual(current.pop('sha256'), old.pop('sha256'))
        self.assertEqual(current, old)
        self.assertNotIn('equipment_effect', current['runners'][0])

    def test_full_card_history_marker_is_never_promoted_to_current_equipment(self):
        raw = '''<img alt="ブリンカー着用"><table><tr><th>枠</th><th>馬番</th><th>馬名</th>
                 <th>性齢/負担重量/騎手</th><th>前走</th></tr><tr><td>1</td><td>2</td>
                 <td>SYNTHETIC HORSE</td><td>牡3/鹿 57.0kg 騎手名</td>
                 <td><img alt="ブリンカー着用"></td></tr></table>'''.encode()
        row = candidate.parse_race_card_detail(raw, 'text/html;charset=utf-8')['runners'][0]
        self.assertNotIn('observed_current_equipment', row)
        self.assertNotIn('equipment_effect', row)

    def test_explicit_marker_is_bound_to_own_cell(self):
        cells = parse_cells('<table><tr><td>1</td><td>2<img alt="ブリンカー着用"></td><td>HORSE</td></tr></table>')
        self.assertEqual(cells.get(1), {'BLINKERS'})
        self.assertNotIn(0, cells)

    def test_historical_cell_marker_is_not_current_number_cell(self):
        cells = parse_cells('<table><tr><td>1</td><td>2</td><td>HORSE</td><td>HISTORY<img alt="ブリンカー着用"></td></tr></table>')
        self.assertIsNone(cells.get(1))
        self.assertEqual(cells.get(3), {'BLINKERS'})

    def test_absent_or_nonexact_or_legend_marker_does_not_invent_equipment(self):
        for markup in ('<table><tr><td>1</td><td>2</td></tr></table>',
                       '<table><tr><td>1</td><td>2<img alt="初ブリンカー"></td></tr></table>',
                       '<img alt="ブリンカー着用"><table><tr><td>1</td><td>2</td></tr></table>'):
            with self.subTest(markup=markup):
                self.assertIsNone(parse_cells(markup).get(1))

if __name__ == '__main__':
    unittest.main()

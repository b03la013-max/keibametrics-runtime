import copy
import hashlib
import unittest
from runtime.local_nankan_card_identity_evidence import extract_card_identities


def fixture(main_jockey='031253', detail_jockey='031253'):
    ma = f'<a href="/kis_info/{main_jockey}.do">藤本現暉</a>' if main_jockey else ''
    de = f'<a href="/kis_info/{detail_jockey}.do">藤本現</a>' if detail_jockey else ''
    cells = ['1', '1', '<a href="/uma_info/2023104097.do">レモンクォーツ</a>',
             '牡3', '-', '-', '56', ma, '父 母', '-', '-', '-']
    raw = ('''<html><meta charset="utf-8">
<input id="gamenKirikaeMenu_programId" value="2026102620110101">
<input id="_cc_proId" value="2026102620110101">
<p class="nk23_c-tab1__subtitle">1R 2026年10月26日 大井競馬 ダ1,600m 発走14:30</p>
<table class="nk23_c-table23__table"><tbody><tr>'''
        + ''.join('<td>' + c + '</td>' for c in cells)
        + '</tr></tbody></table><table class="tb-shousai"><tbody><tr><td class="umaban">1</td>'
        + '<td><a href="/uma_info/2023104097.do">レモンクォーツ</a></td><td>' + de
        + '</td></tr></tbody></table></html>').encode()
    receipt = {'url': 'https://www.nankankeiba.com/uma_shosai/2026102620110101.do',
               'http_status': 200, 'provider': 'NANKAN_OFFICIAL',
               'raw_sha256': hashlib.sha256(raw).hexdigest(),
               'fetched_at': '2026-10-26T00:50:40+00:00', 'source_policy': {
                   'usage_scope': 'USER_PERSONAL_NONCOMMERCIAL_PRIVATE_ONLY_NOT_PUBLIC_REDISTRIBUTION'}}
    race = {'provider': 'NANKAN_OFFICIAL', 'provider_race_id': '2026102620110101',
            'race_date': '2026-10-26', 'venue_id': 'OHI', 'race_no': 1, 'distance': 1600,
            'scheduled_post_at': '2026-10-26T14:30:00+09:00',
            'prediction_cutoff': '2026-10-26T14:25:00+09:00', 'program_runner_count': 1}
    runners = [{'horse_no': 1, 'runner_id': '1', 'provider_horse_id': '2023104097',
                'name': 'レモンクォーツ', 'current_jockey': '藤本現'}]
    return raw, receipt, race, runners


def run_case(parts):
    return extract_card_identities(*parts, freeze_at='2026-10-26T00:50:56+00:00')


def replace_raw(parts, old, new):
    raw, receipt, race, runners = copy.deepcopy(parts)
    raw = raw.replace(old.encode(), new.encode())
    receipt['raw_sha256'] = hashlib.sha256(raw).hexdigest()
    return raw, receipt, race, runners


class CardIdentityEvidenceTests(unittest.TestCase):
    def test_exact_same_provider_link_survives_label_abbreviation(self):
        parts = fixture(); before = copy.deepcopy(parts)
        out = run_case(parts); row = out['rows'][0]
        self.assertEqual(row['jockey']['provider_id'], '031253')
        self.assertEqual(row['jockey']['name_observed'], '藤本現暉')
        self.assertEqual(row['detail_jockey_label'], '藤本現')
        self.assertTrue(row['main_detail_id_match'])
        self.assertIsNone(row['nar_license_id'])
        self.assertFalse(out['numerical_consumer_enabled'])
        self.assertEqual(out['independent_raw_source_count'], 1)
        self.assertEqual(parts, before)

    def test_missing_rider_links_are_unknown(self):
        out = run_case(fixture(None, None))
        self.assertEqual(out['exact_jockey_id_count'], 0)
        self.assertEqual(out['rows'][0]['jockey_identity_state'], 'UNKNOWN_LINK_ABSENT')

    def test_conflicting_main_detail_rider_id_rejected(self):
        with self.assertRaisesRegex(ValueError, 'RIDER_CONTRADICTION'):
            run_case(fixture('031253', '031241'))

    def test_name_alone_cannot_join_swapped_horse(self):
        parts = fixture(); parts[3][0]['provider_horse_id'] = '2023106204'
        with self.assertRaisesRegex(ValueError, 'UNIVERSE_MISMATCH'):
            run_case(parts)

    def test_body_race_id_contradiction_rejected(self):
        parts = replace_raw(fixture(), 'id="_cc_proId" value="2026102620110101"',
                            'id="_cc_proId" value="2026102720110201"')
        with self.assertRaisesRegex(ValueError, 'BODY_RACE_ID'):
            run_case(parts)

    def test_postfreeze_receipt_rejected(self):
        parts = fixture(); parts[1]['fetched_at'] = '2026-10-26T00:51:00+00:00'
        with self.assertRaisesRegex(ValueError, 'POSTFREEZE'):
            run_case(parts)

    def test_missing_timezone_rejected(self):
        parts = fixture(); parts[1]['fetched_at'] = '2026-10-26T00:50:40'
        with self.assertRaisesRegex(ValueError, 'TIMESTAMP_UNKNOWN'):
            run_case(parts)

    def test_raw_byte_tamper_rejected(self):
        raw, receipt, race, runners = fixture()
        with self.assertRaisesRegex(ValueError, 'RAW_RECEIPT'):
            run_case((raw + b'X', receipt, race, runners))

    def test_unapproved_endpoint_cannot_impersonate_card(self):
        parts = fixture(); parts[1]['url'] = 'https://www.nankankeiba.com/topics_comparison/2026102620110101.do'
        with self.assertRaisesRegex(ValueError, 'RAW_RECEIPT'):
            run_case(parts)

    def test_missing_frame_cell_requires_observed_rowspan(self):
        parts = replace_raw(fixture(), '<td>1</td><td>1</td>', '<td>1</td>')
        with self.assertRaisesRegex(ValueError, 'DECLARATION_ROW'):
            run_case(parts)

    def test_shared_frame_rowspan_expands_without_shifting_identity_cells(self):
        raw, receipt, race, runners = fixture()
        text = raw.decode()
        main_row = text.split('<table class="nk23_c-table23__table"><tbody><tr>', 1)[1].split('</tr>', 1)[0]
        second = main_row.removeprefix('<td>1</td>')
        second = second.replace('<td>1</td>', '<td>2</td>', 1)
        second = second.replace('2023104097', '2023106204').replace('レモンクォーツ', 'ゴールドレジーナ')
        second = second.replace('031253', '031241').replace('藤本現暉', '西啓太')
        text = text.replace(main_row, main_row.replace('<td>1</td>', '<td rowspan="2">1</td>', 1) + '</tr><tr>' + second, 1)
        detail_end = '</td></tr></tbody></table></html>'
        text = text.replace(detail_end, '</td></tr><tr><td class="umaban">2</td><td>'
            '<a href="/uma_info/2023106204.do">ゴールドレジーナ</a></td><td>'
            '<a href="/kis_info/031241.do">西啓太</a></td></tr></tbody></table></html>')
        raw = text.encode(); receipt['raw_sha256'] = hashlib.sha256(raw).hexdigest()
        race['program_runner_count'] = 2
        runners.append({'horse_no': 2, 'frame_no': 1, 'runner_id': '2', 'provider_horse_id': '2023106204',
                        'name': 'ゴールドレジーナ', 'current_jockey': '西啓太'})
        out = run_case((raw, receipt, race, runners))
        self.assertEqual(out['runner_count'], 2)
        self.assertEqual(out['rows'][1]['jockey']['provider_id'], '031241')

    def test_schedule_requires_zoned_same_day_header_clock(self):
        for bad in ('2026-10-27T14:30:00+09:00', '2026-10-26T14:30:00',
                    '2026-10-26T14:30:00+00:00'):
            with self.subTest(scheduled_post_at=bad):
                parts = fixture(); parts[2]['scheduled_post_at'] = bad
                with self.assertRaises(ValueError):
                    run_case(parts)
        parts = fixture(); parts[2]['scheduled_post_at'] = '2026-10-26T05:30:00+00:00'
        self.assertEqual(run_case(parts)['runner_count'], 1)

    def test_cutoff_after_scheduled_post_is_contradiction(self):
        parts = fixture(); parts[2]['prediction_cutoff'] = '2026-10-26T14:31:00+09:00'
        with self.assertRaisesRegex(ValueError, 'SCHEDULE_CONTEXT'):
            run_case(parts)

    def test_receipt_authority_claims_are_rejected_not_downgraded(self):
        for key in ('formal_source_claim', 'signed_source_claim', 'production_authority',
                    'public_redistribution_authorized'):
            with self.subTest(flag=key):
                parts = fixture(); parts[1][key] = True
                with self.assertRaisesRegex(ValueError, 'PROVIDER_OR_AUTHORITY_HOLD'):
                    run_case(parts)
        parts = fixture(); parts[1]['source_authority'] = 'NAR_OFFICIAL'
        with self.assertRaisesRegex(ValueError, 'PROVIDER_OR_AUTHORITY_HOLD'):
            run_case(parts)

    def test_runner_id_requires_nonempty_string_or_integer(self):
        for invalid in (None, '', '  ', True, False, 1.5, ['1'], {'id': '1'}):
            with self.subTest(runner_id=invalid):
                parts = fixture(); parts[3][0]['runner_id'] = invalid
                with self.assertRaisesRegex(ValueError, 'FROZEN_RUNNER_ID'):
                    run_case(parts)
        parts = fixture(); del parts[3][0]['runner_id']
        with self.assertRaisesRegex(ValueError, 'FROZEN_RUNNER_ID'):
            run_case(parts)

    def test_runner_id_canonical_string_must_be_unique(self):
        for duplicate in (1, ' 1 '):
            with self.subTest(duplicate=duplicate):
                parts = fixture(); parts[3].append({'horse_no': 2, 'runner_id': duplicate,
                    'provider_horse_id': '2023106204', 'name': 'ゴールドレジーナ', 'current_jockey': '西啓太'})
                with self.assertRaisesRegex(ValueError, 'FROZEN_RUNNER_ID_DUPLICATE'):
                    run_case(parts)

    def test_runner_id_remains_arbitrary_not_restricted_to_horse_number(self):
        for observed, expected in ((' HORSE:03 ', 'HORSE:03'), (17, '17')):
            with self.subTest(runner_id=observed):
                parts = fixture(); parts[3][0]['runner_id'] = observed
                self.assertEqual(run_case(parts)['rows'][0]['runner_id'], expected)

    def test_duplicate_frozen_runner_rejected(self):
        parts = fixture(); parts[3].append(copy.deepcopy(parts[3][0]))
        with self.assertRaisesRegex(ValueError, 'FROZEN_UNIVERSE'):
            run_case(parts)


if __name__ == '__main__':
    unittest.main()

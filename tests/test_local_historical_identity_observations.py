import base64
import gzip
import hashlib
import unittest

from runtime.local_historical_identity_observations import extract_result_row_identities


def snapshot(body=None):
    body = body or '''<h4>2026年10月1日（木） 船 橋 第1競走</h4><section class="raceTitle"><h3>Ｃ３四</h3><li>ダート 1200ｍ 天候：晴 馬場：良</li></section><table><tr><th>着順</th><th>枠</th><th>馬番</th><th>馬名</th><th>所属</th><th>性齢</th><th>負担重量</th><th>騎手</th><th>調教師</th><th>馬体重</th><th>タイム</th><th>着差</th><th>上がり</th><th>通過</th><th>人気</th><th>オッズ</th></tr>
    <tr><td>1</td><td>1</td><td>1</td><td><a href="/KeibaWeb/DataRoom/HorseMarkInfo?k_lineageLoginCode=123">Synthetic</a></td><td>船橋</td><td>牡4</td><td>56.0</td><td><a href="/KeibaWeb/DataRoom/RiderMark?k_riderLicenseNo=456">SyntheticJ</a></td><td><a href="/KeibaWeb/DataRoom/TrainerMark?k_trainerLicenseNo=789">SyntheticT</a></td><td>480(-4)</td><td>1:12.0</td><td></td><td>37.0</td><td></td><td>1</td><td>1.5</td></tr></table>'''
    raw = body.encode()
    url = 'https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/RaceMarkTable?k_babaCode=19&k_raceDate=2026%2F10%2F01&k_raceNo=1'
    return {'official': True, 'authority': 'NAR_OFFICIAL', 'http_status': 200,
            'source_id': 'SYNTHETIC_CORRECTNESS_ONLY', 'requested_url': url, 'final_url': url,
            'fetched_at': '2026-10-01T05:00:00+00:00', 'content_type': 'text/html; charset=UTF-8',
            'raw_gzip_b64': base64.b64encode(gzip.compress(raw)).decode(),
            'raw_sha256': hashlib.sha256(raw).hexdigest(), 'byte_count': len(raw)}


class ResultIdentityTests(unittest.TestCase):
    def parse(self, s):
        return extract_result_row_identities(s, as_of='2026-11-03T04:00:00+00:00', target_race_date='2026-11-03')

    def test_actual_fields_are_cell_link_bound_not_name_join(self):
        result = self.parse(snapshot()); row = result['records'][0]
        self.assertEqual((row['horse_id'], row['jockey_id'], row['trainer_id']), ('NAR:123','NAR:456','NAR:789'))
        self.assertIsNone(row['stable_id'])
        self.assertEqual((row['body_weight_kg'], row['body_weight_delta_kg']), (480,-4))
        self.assertEqual((row['distance_m'],row['surface'],row['going']), (1200,'DIRT','良'))
        self.assertIsNone(row['event_at']); self.assertIsNone(row['field_size'])
        self.assertFalse(result['production_admission']); self.assertFalse(result['whole_population_complete'])

    def test_raw_hash_mismatch_rejected(self):
        s=snapshot();s['raw_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'RAW_HASH'): self.parse(s)

    def test_source_at_decision_cutoff_rejected(self):
        s=snapshot();s['fetched_at']='2026-11-03T04:00:00+00:00'
        with self.assertRaisesRegex(ValueError,'SOURCE_AT_OR_AFTER'):self.parse(s)

    def test_redirect_to_other_race_rejected(self):
        s=snapshot();s['final_url']=s['final_url'].replace('k_raceNo=1','k_raceNo=2')
        with self.assertRaisesRegex(ValueError,'REDIRECT_RACE'):self.parse(s)

    def test_external_host_identity_rejected(self):
        s=snapshot();raw=gzip.decompress(base64.b64decode(s['raw_gzip_b64'])).decode().replace('/KeibaWeb/DataRoom/RiderMark?', 'https://example.invalid/KeibaWeb/DataRoom/RiderMark?')
        with self.assertRaisesRegex(ValueError,'URL_SCOPE'):self.parse(snapshot(raw))

    def test_missing_identity_stays_missing(self):
        s=snapshot();raw=gzip.decompress(base64.b64decode(s['raw_gzip_b64'])).decode().replace('/KeibaWeb/DataRoom/RiderMark?k_riderLicenseNo=456','/no-permanent-identity')
        r=self.parse(snapshot(raw));self.assertIsNone(r['records'][0]['jockey_id']);self.assertFalse(r['all_printed_row_identities_recovered'])

    def test_same_day_result_never_backfilled(self):
        with self.assertRaisesRegex(ValueError,'SAME_OR_AFTER_TARGET'):extract_result_row_identities(snapshot(),as_of='2026-11-03T04:00:00+00:00',target_race_date='2026-10-01')

    def test_cancelled_finish_not_zero_ability(self):
        s=snapshot();raw=gzip.decompress(base64.b64decode(s['raw_gzip_b64'])).decode().replace('<td>1</td><td>1</td><td>1</td>', '<td>取消</td><td>1</td><td>1</td>')
        self.assertIsNone(self.parse(snapshot(raw))['records'][0]['finish'])

    def test_raw_other_race_header_rejected_even_when_snapshot_hash_valid(self):
        s=snapshot();raw=gzip.decompress(base64.b64decode(s['raw_gzip_b64'])).decode().replace('第1競走','第2競走')
        with self.assertRaisesRegex(ValueError,'PRINTED_RACE_HEADER'):self.parse(snapshot(raw))

    def test_no_result_page_is_explicit_terminal(self):
        with self.assertRaisesRegex(ValueError,'RESULT_INFORMATION_NOT_AVAILABLE'):self.parse(snapshot('ご指定のレース成績の情報がありません'))

    def test_official_short_distance_table_without_corner_column(self):
        s=snapshot();raw=gzip.decompress(base64.b64decode(s['raw_gzip_b64'])).decode().replace('<th>通過</th>','').replace('<td>37.0</td><td></td>','<td>37.0</td>')
        r=self.parse(snapshot(raw))
        self.assertEqual(r['records'][0]['jockey_id'],'NAR:456')


if __name__ == '__main__': unittest.main()

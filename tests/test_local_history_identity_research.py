import copy
import unittest
from runtime.local_history_identity_research import classify_start, transfer_facts, JRA_NAMES


class HistoryIdentityTests(unittest.TestCase):
    def test_all_ten_jra_names_exact_with_provider_collector(self):
        for name in JRA_NAMES:
            for value in (name, 'J'+name, 'JRA'+name+'競馬場'):
                with self.subTest(value=value):
                    self.assertTrue(classify_start({'venue':value,'provider':'NANKAN_OFFICIAL'})['is_jra'])

    def test_all_ten_scoped_jv_codes_and_jra_race_ids(self):
        for i,name in enumerate(JRA_NAMES,1):
            with self.subTest(code=i):
                a=classify_start({'venue_code':f'{i:02d}','provider':'JRA_OFFICIAL'})
                b=classify_start({'provider':'JRA_OFFICIAL','provider_race_id':f'2026{i:02d}010101'})
                self.assertEqual(name,a['canonical_venue']);self.assertTrue(a['is_jra'])
                self.assertEqual(name,b['canonical_venue']);self.assertTrue(b['is_jra'])

    def test_publisher_alone_unscoped_code_and_j_prefix_not_authority(self):
        for row in ({'provider':'JRA_OFFICIAL'}, {'venue_code':'05'}, {'venue':'Junk'},
                    {'venue':'J浦和'}, {'venue':'J交流京都'},
                    {'provider':'NANKAN_OFFICIAL','venue_code':'05'},
                    {'venue':'東京湾'}, {'venue':'新潟県'}, {'venue':'札幌観光'}):
            with self.subTest(row=row):self.assertIsNone(classify_start(row)['is_jra'])

    def test_local_names_and_namespaced_codes_not_jra(self):
        for name in ('大井','浦和','門別','盛岡','名古屋','金沢','札幌(地方)','函館（地方）','地方札幌','新潟競馬場（地方競馬）'):
            with self.subTest(name=name):self.assertFalse(classify_start({'venue':name})['is_jra'])
        self.assertFalse(classify_start({'venue_code':'20','provider':'NANKAN_OFFICIAL'})['is_jra'])
        self.assertFalse(classify_start({'venue_code':'44','venue_code_namespace':'JV_DATA'})['is_jra'])
        self.assertFalse(classify_start({'venue_code':'58','venue_code_namespace':'JV_DATA'})['is_jra'])
        for code in ('30','49','50','51','52','53','54','55','56','57','58','59','60','61'):
            with self.subTest(jv_local_code=code):
                self.assertFalse(classify_start({'venue_code':code,'venue_code_namespace':'JV_DATA'})['is_jra'])
        self.assertIsNone(classify_start({'venue_code':'58','provider':'NANKAN_OFFICIAL'})['is_jra'])
        self.assertIsNone(classify_start({'venue':'札幌','venue_code':'58','provider':'NANKAN_OFFICIAL'})['is_jra'])

    def test_conflicting_name_namespace_and_race_identity_unknown(self):
        for row in ({'venue':'大井','provider':'JRA_OFFICIAL','venue_code':'05'},
                    {'venue':'札幌','provider':'JRA_OFFICIAL','venue_code':'58'},
                    {'venue':'東京','provider':'JRA_OFFICIAL','provider_race_id':'202606010101'},
                    {'venue':'東京','provider':'NANKAN_OFFICIAL','provider_race_id':'2026102620110101'}):
            with self.subTest(row=row):
                self.assertEqual('CONFLICT',classify_start(row)['family'])
                self.assertIsNone(classify_start(row)['is_jra'])

    def test_observed_history_not_registration_transfer_first_race(self):
        starts=[{'venue':'大井'},{'venue':'札幌'},{'venue':'函館'}];before=copy.deepcopy(starts)
        facts=transfer_facts(starts)
        self.assertTrue(facts['observed_jra_history']);self.assertFalse(facts['latest_observed_start_is_jra'])
        self.assertEqual(1,facts['observed_local_starts_since_most_recent_jra'])
        self.assertIsNone(facts['actual_registration_transfer_first_start'])
        self.assertIsNone(facts['actual_registration_transfer_date']);self.assertEqual(before,starts)

    def test_latest_jra_and_unknown_history_are_separate(self):
        facts=transfer_facts([{'venue':'新潟'},{'venue':'大井'}])
        self.assertTrue(facts['latest_observed_start_is_jra']);self.assertEqual(0,facts['observed_local_starts_since_most_recent_jra'])
        self.assertIsNone(transfer_facts([{'venue':'UNKNOWN'}])['latest_observed_start_is_jra'])
        facts=transfer_facts([{'venue':'大井'}]);self.assertFalse(facts['observed_jra_history']);self.assertIsNone(facts['lifetime_jra_history'])
        self.assertIsNone(transfer_facts([])['observed_jra_history'])


if __name__=='__main__':unittest.main()

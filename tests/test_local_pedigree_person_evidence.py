import copy
import json
import hashlib
import os
from pathlib import Path
import unittest
from runtime import local_pedigree_person_evidence as m

class EvidenceBoundaryTests(unittest.TestCase):
    def original(self):
        v={'production_authority':False,'race':{'provider_race_id':'2026102620110101','prediction_cutoff':'2026-10-26T05:25:00+00:00'},
           'source_fetched_at':'2026-10-26T00:45:00+00:00','source_sha256':'a'*64,
           'all_runners':[{'provider_horse_id':'1','runner_id':'1','name':'馬A','sire':'父A','damsire':'母父A','current_jockey':'騎手A',
                 'starts':[{'date':'26.10.05','venue':'大井','provider_race_id':'2026100520100207','finish':1,'distance':1400,'going':'良','surface':'DIRT','ride_jockey':'騎手A','ride_popularity':1}]}]}
        return self.seal(v)
    def seal(self,x):return {**{k:v for k,v in x.items() if k!='sha256'},'sha256':m.sha({k:v for k,v in x.items() if k!='sha256'})}
    def test_same_field_subset_has_no_bvi_or_skill_authority(self):
        o=self.original();r=m.selected_history_cohort([o]);self.assertFalse(r['formal_bvi_eligible']);self.assertFalse(r['score_consumption']);self.assertEqual(1,len(r['records']));self.assertEqual(1,r['groups'][0]['wins']);self.assertEqual(1,r['groups'][0]['unique_horses']);self.assertFalse(r['groups'][0]['score_eligible'])
    def test_duplicate_history_deduplicated_conflict_rejected(self):
        o=self.original();r=m.selected_history_cohort([o,o]);self.assertEqual(1,len(r['records']))
        b=copy.deepcopy(o);b['all_runners'][0]['starts'][0]['finish']=2;b=self.seal(b)
        with self.assertRaisesRegex(ValueError,'DUPLICATE_CONFLICT'):m.selected_history_cohort([o,b])
    def test_same_number_other_race_date_or_venue_is_rejected(self):
        for change in ({'provider_race_id':'2026100620100207'},{'provider_race_id':'2026100518100207'}):
            o=self.original();o['all_runners'][0]['starts'][0].update(change);o=self.seal(o)
            with self.subTest(change=change),self.assertRaisesRegex(ValueError,'IDENTITY'):m.selected_history_cohort([o])
    def test_unknown_finish_not_zero_and_jra_not_local(self):
        for change,label in [({'finish':None},'FINISH_UNKNOWN_NOT_ZERO'),({'venue':'京都'},'NONLOCAL_OR_UNKNOWN_VENUE'),({'date':'26.10.26'},'TARGET_OR_FUTURE_DATE')]:
            o=self.original();o['all_runners'][0]['starts'][0].update(change);r=m.selected_history_cohort([self.seal(o)]);self.assertEqual([],r['records']);self.assertEqual(1,r['excluded'][label])
    def test_wrong_original_hash_or_source_time_cannot_enter_cohort(self):
        o=self.original();o['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'HASH'):m.selected_history_cohort([o])
        o=self.original();o['source_fetched_at']='2026-10-26T06:25:00+00:00'
        with self.assertRaisesRegex(ValueError,'POST_CUTOFF'):m.selected_history_cohort([self.seal(o)])
    def test_annual_reference_does_not_become_official_population(self):
        raw=json.dumps({'annual':[{'終了日':'2025-12-31','出典URL':'https://example.test'}],'supplement':[]}).encode();man={'data_file':'x','dataset_id':'test','available_at':'2026-10-01T00:00:00Z','sha256':hashlib.sha256(raw).hexdigest(),'annual_rows':1,'supplement_rows':0}
        r=m.audit_reference_dataset(man,raw,'2026-10-26T00:00:00Z');self.assertFalse(r['formal_bvi_eligible']);self.assertEqual(1,r['missing_required_statistic_rows']['三着回数'])
        with self.assertRaisesRegex(ValueError,'POST_CUTOFF'):m.audit_reference_dataset(man,raw,'2026-09-26T00:00:00Z')
        with self.assertRaisesRegex(ValueError,'SHA'):m.audit_reference_dataset(man,raw+b' ','2026-10-26T00:00:00Z')
    def test_name_only_not_license_verified_and_ambiguous_not_filled(self):
        o=self.original();a={'profiles':[{'license_no':'123','name':'騎手A'}]};r=m.current_rider_links([o],a);self.assertEqual('NAME_ONLY_NOT_CROSS_PROVIDER_VERIFIED',r[0]['connection']);self.assertFalse(r[0]['strict_index_consumption'])
        a['profiles'].append({'license_no':'456','name':'騎手A'});r=m.current_rider_links([o],a);self.assertEqual('UNKNOWN_OR_AMBIGUOUS',r[0]['connection'])
    def test_arbitrary_key_cannot_impersonate_existing_signer(self):
        with self.assertRaisesRegex(ValueError,'TRUSTED_AUTHORITY'):m.audit_signed_riders({'receipt':{},'artifact':{}},'other-key','2026-10-26T00:00:00Z',lambda s:{})

if __name__=='__main__':unittest.main()

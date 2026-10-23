"""Preserve already printed JRA facts without changing admission or policies."""
import copy
import base64
import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime/jra_source_runtime'),str(ROOT/'runtime')]
from jra_race_card_detail import parse_race_card_detail
from jra_official_pdf import apply_official_detail_status


class ObservedFactRetention(unittest.TestCase):
    def test_frame_image_alt_is_a_fact_not_a_guessed_horse_number(self):
        raw='''<table><tr><th>枠</th><th>馬番</th><th>馬名</th>
          <th>性齢/負担重量/騎手</th><th>前走</th></tr>
          <tr><td><img alt="枠8桃" src="/JRADB/img/waku/8.png"></td><td>16</td>
          <td>サンプルホース</td><td>牡3/鹿 57.5kg 騎手名</td><td></td></tr>
          <tr><td><img src="/JRADB/img/waku/1.png"></td><td>1</td>
          <td>別のホース</td><td>牡3/鹿 57.0kg 騎手名</td><td></td></tr></table>'''.encode()
        rows=parse_race_card_detail(raw,'text/html; charset=utf-8')['runners']
        self.assertEqual(rows[0]['frame_no'],8)
        self.assertEqual(rows[0]['horse_no'],16)
        self.assertIsNone(rows[1]['frame_no'])
        self.assertEqual(rows[0]['assigned_weight'],57.5)

    def test_unrecognised_or_non_alt_frame_labels_remain_missing(self):
        for image in ('<img alt="枠18桃">','<img data-alt="枠8桃">',
                      '<img title=" alt=\'枠8桃\'">','<img alt="枠8桃" alt="枠1白">'):
            with self.subTest(image=image):
                raw=('''<table><tr><th>枠</th><th>馬番</th><th>馬名</th>
                <th>性齢/負担重量/騎手</th><th>前走</th></tr><tr><td>'''+image+
                '''</td><td>16</td><td>サンプルホース</td><td>牡3/鹿 57.5kg 騎手名</td>
                <td></td></tr></table>''').encode()
                row=parse_race_card_detail(raw,'text/html; charset=utf-8')['runners'][0]
                self.assertIsNone(row['frame_no'])

    def test_current_rider_link_owns_identity_while_rating_stays_in_raw(self):
        for link in ('''<a href="/JRADB/accessK.html?CNAME=pw04kmk001140%2F24">横山 和生</a>''',
                     '''<a href="#" onclick="return doAction('/JRADB/accessK.html', 'pw04kmk001140/24');">横山 和生</a>'''):
            with self.subTest(link=link):
                raw=('''<table><tr><th>枠</th><th>馬番</th><th>馬名</th>
                <th>性齢/負担重量/騎手</th><th>前走</th></tr><tr><td>1</td><td>1</td>
                <td>サンプルホース</td><td>牝3/鹿 55.0kg '''+link+
                '''<div class="rating"><span>110</span> <span>M</span></div></td>
                <td></td></tr></table>''').encode()
                row=parse_race_card_detail(raw,'text/html; charset=utf-8')['runners'][0]
                self.assertEqual(row['jockey'],'横山 和生')
                self.assertEqual(row['jockey_profile_token'],'pw04kmk001140/24')
                self.assertIn('110 M',row['raw'])

    def example(self):
        rows=[{'horse_no':3,'runner_id':'3','name':'ホース A','status':'ACTIVE',
               'assigned_weight':None,'frame_no':None},
              {'horse_no':6,'runner_id':'6','name':'ホース B','status':'ACTIVE',
               'assigned_weight':56.0,'frame_no':4}]
        pdf={'runner_count':2,'runners':copy.deepcopy(rows)}
        artifact={'jra_official_runner_universe':pdf,
                  'jra_official_pdf_runner_universe':copy.deepcopy(pdf)}
        detail=copy.deepcopy(rows)
        detail[0].update(assigned_weight=57.5,frame_no=2)
        detail[1].update(assigned_weight=57.5,frame_no=4)
        declared={'runners':detail,'source_id':'JRA-OFFICIAL-RACE-CARD-DETAIL',
                  'source_snapshot_sha256':'verified-detail-sha'}
        return artifact,declared,copy.deepcopy(declared)

    def test_missing_facts_are_completed_only_after_exact_identity_binding(self):
        artifact,declared,active=self.example()
        original=copy.deepcopy(artifact['jra_official_pdf_runner_universe'])
        result=apply_official_detail_status(artifact,declared,active)
        rows=result['jra_official_runner_universe']['runners']
        self.assertEqual(rows[0]['assigned_weight'],57.5)
        self.assertEqual(rows[0]['frame_no'],2)
        self.assertEqual(rows[0]['detail_fact_sources']['assigned_weight'],{
            'source_id':'JRA-OFFICIAL-RACE-CARD-DETAIL',
            'source_snapshot_sha256':'verified-detail-sha'})
        self.assertEqual(rows[1]['assigned_weight'],56.0)
        self.assertEqual(result['jra_official_pdf_runner_universe'],original)
        diag=result['official_runner_universe_reconciliation']
        self.assertEqual(len(diag['completed_detail_facts']),2)
        self.assertEqual(diag['detail_fact_conflicts'],[
            {'horse_no':6,'field':'assigned_weight','pdf_value':56.0,'detail_value':57.5}])

    def test_identity_mismatch_cannot_complete_facts(self):
        artifact,declared,active=self.example()
        declared['runners'][0]['name']='別馬'
        before=copy.deepcopy(artifact)
        with self.assertRaisesRegex(ValueError,'JRA_DECLARED_PDF_DETAIL_IDENTITY_MISMATCH'):
            apply_official_detail_status(artifact,declared,active)
        self.assertEqual(artifact,before)

    def test_cancelled_runner_is_not_restored_by_fact_completion(self):
        artifact,declared,active=self.example()
        declared['runners'][0]['status']='CANCELLED'
        active['runners']=active['runners'][1:]
        result=apply_official_detail_status(artifact,declared,active)
        self.assertEqual([r['horse_no'] for r in result['jra_official_runner_universe']['runners']],[6])
        self.assertEqual(result['jra_declared_runner_universe']['runners'][0]['status'],'CANCELLED')

    def test_saved_oct18_cards_retain_frames_and_current_rider_identity(self):
        paths=sorted((ROOT/'runtime/requests').glob('KM-JRA-*-20261018-*-FORMAL.json'))
        if not paths:self.skipTest('stored official cards missing')
        runners=0;rider_recoveries=0
        for path in paths:
            request=json.loads(path.read_text())
            source=request['source_snapshot']; old=source['jra_official_race_card_detail']
            snapshot=next(s for s in source['sources']
                          if s.get('snapshot_sha256')==old['source_snapshot_sha256'])
            raw=gzip.decompress(base64.b64decode(snapshot['raw_gzip_b64']))
            self.assertEqual(hashlib.sha256(raw).hexdigest(),snapshot['raw_sha256'])
            parsed=parse_race_card_detail(raw,snapshot['content_type'])
            self.assertEqual(len(old['runners']),len(parsed['runners']))
            for before,after in zip(old['runners'],parsed['runners']):
                with self.subTest(race=request['race_id'],runner=before['runner_id']):
                    self.assertIsNone(before['frame_no'])
                    self.assertIn(after['frame_no'],range(1,9))
                    if before['jockey']!=after['jockey']:
                        self.assertRegex(before['jockey'],r'\s+[0-9]{2,3}\s+[A-Z]')
                        self.assertTrue(before['jockey'].startswith(after['jockey']))
                        self.assertIsNone(before['jockey_profile_token'])
                        self.assertRegex(after['jockey_profile_token'],r'^pw04kmk[0-9]{6}/[0-9A-Fa-f]{2}$')
                        rider_recoveries+=1
                    unchanged=set(before)|set(after)
                    unchanged-={'frame_no','jockey','jockey_profile_token'}
                    self.assertEqual({k:before.get(k) for k in unchanged},
                                     {k:after.get(k) for k in unchanged})
                    runners+=1
        self.assertEqual((len(paths),runners),(34,437))
        self.assertEqual(rider_recoveries,10)

    def test_saved_tokyo11_omitted_weights_reach_existing_feature_rule(self):
        from jra_race_card_detail import runner_universes_from_detail
        from jra_owner_authorized_feature_rules import owner_authorized_observations
        path=ROOT/'runtime/requests/KM-JRA-TKY-20261018-R11-LIVE-R1-FORMAL.json'
        if not path.exists():self.skipTest('stored official Tokyo11 SOURCE missing')
        original=path.read_bytes(); request=json.loads(original); source=request['source_snapshot']
        source['source_snapshot_sha256']=request['source_snapshot_sha256']
        before=copy.deepcopy(source['jra_official_pdf_runner_universe'])
        declared,active=runner_universes_from_detail(source['jra_official_race_card_detail'])
        registry=json.loads((ROOT/'mapping/jra_evidence_feature_rule_registry_v1.3_20261010.json').read_text())
        prior=owner_authorized_observations(source,registry)
        self.assertTrue(all('weight_load_fit' not in features for features in prior.values()))
        repaired=apply_official_detail_status(copy.deepcopy(source),declared,active)
        after=owner_authorized_observations(repaired,registry)
        self.assertEqual(len(after),13)
        self.assertTrue(all('weight_load_fit' in features for features in after.values()))
        rows={str(r['runner_id']):r for r in repaired['jra_official_runner_universe']['runners']}
        self.assertEqual([rows[r]['assigned_weight'] for r in ('3','6')],[57.5,57.5])
        self.assertEqual(repaired['jra_official_pdf_runner_universe'],before)
        self.assertEqual(path.read_bytes(),original)
        for rid in prior:
            self.assertEqual(prior[rid],{k:v for k,v in after[rid].items() if k!='weight_load_fit'})


if __name__=='__main__':
    unittest.main()

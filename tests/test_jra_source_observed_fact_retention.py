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
                    unchanged-={'frame_no','jockey','jockey_profile_token','recent_runs'}
                    self.assertEqual({k:before.get(k) for k in unchanged},
                                     {k:after.get(k) for k in unchanged})
                    self.assertEqual(len(before['recent_runs']),len(after['recent_runs']))
                    for old_run,new_run in zip(before['recent_runs'],after['recent_runs']):
                        keys=(set(old_run)|set(new_run))-{'raw','race_class_text'}
                        self.assertEqual({k:old_run.get(k) for k in keys},
                                         {k:new_run.get(k) for k in keys})
                        if old_run.get('race_class_text')!=new_run.get('race_class_text'):
                            self.assertTrue(new_run['race_class_text'].startswith(old_run['race_class_text']))
                            self.assertRegex(new_run['race_class_text'][len(old_run['race_class_text']):],r'^ (?:G[ⅠⅡⅢ123]|Jpn[ⅠⅡⅢ123]|リステッド)$')
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


class CancelledNumberRetention(unittest.TestCase):
    FIXTURE=ROOT/'tests/fixtures/jra_cancelled_20261025'

    def raw(self):
        raw=(self.FIXTURE/'current_rows.html').read_bytes()
        self.assertEqual(len(raw),12499)
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         '177cf1380ffdac6a0bbb2ece9062acd4950bc59d5e830a473e59654cb958d278')
        return raw

    def test_actual_cancelled_identity_survives_without_guessed_number(self):
        detail=parse_race_card_detail(self.raw(),'text/html;charset=utf-8')
        self.assertEqual(detail['runner_count'],9)
        row=next(r for r in detail['runners'] if r['horse_name']=='シュプレヒコール')
        self.assertEqual(row['status'],'CANCELLED')
        self.assertIsNone(row['horse_no'])
        self.assertIsNone(row['runner_id'])
        self.assertEqual(row['horse_profile_token'],'pw01dud002024105437/B2')
        self.assertEqual([r['horse_no'] for r in detail['runners'] if r['status']=='ACTIVE'],
                         [1,2,3,4,6,7,8,9])

    def context_raw(self):
        # Synthetic context harness around unchanged extracted real current rows.
        return ('<h1>2026年10月25日（日曜）4回京都9日 3レース</h1>'
                '<p>発走時刻：11時00分 天候 小雨 芝 重 2歳 未勝利 '
                'コース：1,600メートル（芝・右）</p>').encode()+self.raw()

    def artifact(self):
        fixture=json.loads((self.FIXTURE/'evidence.json').read_text())
        pdf=fixture['pdf_universe']
        from source_acquisition import sha_obj
        self.assertEqual(sha_obj({k:v for k,v in pdf.items() if k!='runner_universe_sha256'}),
                         pdf['runner_universe_sha256'])
        detail=parse_race_card_detail(self.context_raw(),'text/html;charset=utf-8')
        snap=fixture['detail_source_metadata']
        snap.update(raw_gzip_b64=base64.b64encode(gzip.compress(self.context_raw())).decode(),
                    raw_sha256=hashlib.sha256(self.context_raw()).hexdigest(),
                    byte_count=len(self.context_raw()),content_type='text/html;charset=utf-8')
        snap['snapshot_sha256']=sha_obj({k:v for k,v in snap.items() if k!='snapshot_sha256'})
        detail['source_snapshot_sha256']=snap['snapshot_sha256']
        return {'source_race_context':{'race_date':'2026-10-25','venue_id':'KYO','race_no':3},
                'jra_official_race_card_detail':detail,
                'jra_official_pdf_runner_universe':pdf,
                'jra_official_runner_universe':copy.deepcopy(pdf),
                'sources':[fixture['pdf_source_metadata'],snap]}

    def resolve(self,artifact):
        from jra_race_card_detail import resolve_cancelled_runner_numbers
        return resolve_cancelled_runner_numbers(artifact,meeting_key='0820260409')

    def test_actual_identity_binding_yields_declared9_cancelled1_active8(self):
        from jra_race_card_detail import runner_universes_from_detail
        artifact=self.artifact(); original=copy.deepcopy(artifact['jra_official_pdf_runner_universe'])
        result=self.resolve(artifact)
        detail=result['jra_official_race_card_detail']
        row=next(r for r in detail['runners'] if r['status']=='CANCELLED')
        self.assertEqual(row['horse_no'],5)
        self.assertEqual(row['runner_id'],'5')
        self.assertEqual(row['horse_number_binding']['pdf_source_snapshot_sha256'],original['source_snapshot_sha256'])
        declared,active=runner_universes_from_detail(detail)
        result=apply_official_detail_status(result,declared,active)
        self.assertEqual(result['jra_declared_runner_universe']['runner_count'],9)
        self.assertEqual([r['horse_no'] for r in result['jra_official_runner_universe']['runners']],
                         [1,2,3,4,6,7,8,9])
        self.assertEqual(result['jra_official_pdf_runner_universe'],original)

    def test_row_order_and_frame_are_not_number_evidence(self):
        artifact=self.artifact()
        rows=artifact['jra_official_race_card_detail']['runners']
        rows.reverse()
        next(r for r in rows if r['horse_no'] is None)['frame_no']=8
        result=self.resolve(artifact)
        self.assertEqual(next(r for r in result['jra_official_race_card_detail']['runners']
                              if r['status']=='CANCELLED')['horse_no'],5)

    def test_missing_number_cannot_be_used_as_detail_only_fallback(self):
        from jra_race_card_detail import runner_universes_from_detail
        with self.assertRaisesRegex(ValueError,'UNRESOLVED'):
            runner_universes_from_detail(self.artifact()['jra_official_race_card_detail'])
        artifact=self.artifact();artifact.pop('jra_official_pdf_runner_universe')
        with self.assertRaises(ValueError):self.resolve(artifact)

    def test_ambiguous_or_conflicting_identity_fails_without_mutation(self):
        mutations={
            'duplicate_pdf_name':lambda a:a['jra_official_pdf_runner_universe']['runners'][0].update(name='シュプレヒコール'),
            'duplicate_pdf_number':lambda a:a['jra_official_pdf_runner_universe']['runners'][0].update(horse_no=5),
            'wrong_name':lambda a:a['jra_official_race_card_detail']['runners'][4].update(horse_name='別馬'),
            'missing_profile':lambda a:a['jra_official_race_card_detail']['runners'][4].update(horse_profile_token=None),
            'duplicate_profile':lambda a:a['jra_official_race_card_detail']['runners'][4].update(horse_profile_token=a['jra_official_race_card_detail']['runners'][0]['horse_profile_token']),
            'active_without_number':lambda a:a['jra_official_race_card_detail']['runners'][4].update(status='ACTIVE'),
            'duplicate_detail_name':lambda a:a['jra_official_race_card_detail']['runners'][0].update(horse_name='シュプレヒコール'),
            'conflicting_numeric_row':lambda a:a['jra_official_race_card_detail']['runners'][0].update(horse_no=5),
            'missing_row':lambda a:a['jra_official_race_card_detail']['runners'].pop(),
        }
        for label,mutate in mutations.items():
            with self.subTest(label=label):
                artifact=self.artifact();mutate(artifact);before=copy.deepcopy(artifact)
                with self.assertRaises(ValueError):self.resolve(artifact)
                self.assertEqual(artifact,before)

    def test_mismatched_race_or_unbound_evidence_fails(self):
        mutations={
            'race':lambda a:a['source_race_context'].update(race_no=4),
            'date':lambda a:a['source_race_context'].update(race_date='2026-10-24'),
            'venue':lambda a:a['source_race_context'].update(venue_id='TKY'),
            'pdf_race':lambda a:a['jra_official_pdf_runner_universe'].update(race_no=4),
            'pdf_url':lambda a:a['jra_official_pdf_runner_universe'].update(official_pdf_url='https://www.jra.go.jp/keiba/rpdf/pdf/20261024-04kyoto08.pdf'),
            'pdf_snapshot':lambda a:a['jra_official_pdf_runner_universe'].update(source_snapshot_sha256='missing'),
            'pdf_raw_hash':lambda a:a['sources'][0].update(raw_sha256='wrong'),
            'pdf_post_cutoff':lambda a:a['sources'][0].update(cutoff_relation='POST_CUTOFF'),
            'pdf_unofficial':lambda a:a['sources'][0].update(official=False),
            'detail_post_cutoff':lambda a:a['sources'][1].update(cutoff_relation='POST_CUTOFF'),
            'detail_raw_hash':lambda a:a['sources'][1].update(raw_sha256='wrong'),
            'detail_snapshot':lambda a:a['sources'][1].update(snapshot_sha256='missing'),
        }
        for label,mutate in mutations.items():
            with self.subTest(label=label):
                artifact=self.artifact();mutate(artifact);before=copy.deepcopy(artifact)
                with self.assertRaises(ValueError):self.resolve(artifact)
                self.assertEqual(artifact,before)

    def card(self,number='1',history='出走取消',name='テスト',extra=''):
        return (f'''<table><tr><th>枠</th><th>馬番</th><th>馬名</th>
        <th>性齢/負担重量/騎手</th><th>前走</th></tr><tr><td>8</td><td>{number}</td>
        <td><a href="/JRADB/accessU.html?CNAME=pw01dud002024105437/B2">{name}</a>{extra}</td>
        <td>牡2/鹿 56.0kg 騎手</td><td>{history}</td></tr></table>''').encode()

    def test_normal_numeric_and_historical_cancellation_remain_active(self):
        row=parse_race_card_detail(self.card(),'text/html;charset=utf-8')['runners'][0]
        self.assertEqual((row['horse_no'],row['status']),(1,'ACTIVE'))

    def test_unnumbered_without_current_cancellation_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'NUMBER'):
            parse_race_card_detail(self.card(number=''), 'text/html;charset=utf-8')

    def test_explicit_exclusion_is_retained_and_ambiguous_status_rejected(self):
        row=parse_race_card_detail(self.card(number='除外'), 'text/html;charset=utf-8')['runners'][0]
        self.assertEqual(row['status'],'EXCLUDED');self.assertIsNone(row['horse_no'])
        with self.assertRaisesRegex(ValueError,'STATUS_AMBIGUOUS'):
            parse_race_card_detail(self.card(number='出走取消 競走除外'),'text/html;charset=utf-8')

    def test_unnumbered_profile_must_belong_to_exact_current_row(self):
        for extra in ('<a href="/JRADB/accessU.html?CNAME=pw01dud002024999999/AA">テスト</a>',
                      '<a href="/JRADB/accessU.html?CNAME=pw01dud002024999999/AA">別馬</a>'):
            with self.subTest(extra=extra),self.assertRaisesRegex(ValueError,'IDENTITY'):
                parse_race_card_detail(self.card(number='取消',extra=extra),'text/html;charset=utf-8')
        raw=self.card(number='取消').replace(b'accessU.html',b'other.html')
        with self.assertRaisesRegex(ValueError,'IDENTITY'):
            parse_race_card_detail(raw,'text/html;charset=utf-8')

    def test_new_source_fetch_resolves_before_universe_construction(self):
        from unittest.mock import patch
        import jra_race_card_detail as module
        from jra_race_card_detail import runner_universes_from_detail
        artifact=self.artifact();artifact.pop('jra_official_race_card_detail');artifact['sources'].pop()
        with patch.object(module,'_discover_and_fetch',return_value=(self.context_raw(),{'content-type':'text/html;charset=utf-8'},
                          'https://www.jra.go.jp/JRADB/accessD.html',{})), \
             patch.object(module,'utcnow',return_value='2026-10-25T01:10:10.651485+00:00'):
            result=module.fetch_and_enrich_race_card_detail(artifact,'2026-10-25T10:55:00+09:00',
                   race_date='2026-10-25',meeting_key='0820260409',race_no=3)
        declared,active=runner_universes_from_detail(result['jra_official_race_card_detail'])
        self.assertEqual((declared['runner_count'],active['runner_count']),(9,8))


def test_entire_failed_original_cp932_yields_declared9_cancelled1_active8():
    from jra_race_card_detail import resolve_cancelled_runner_numbers,runner_universes_from_detail
    fixture=json.loads((ROOT/'tests/fixtures/jra_cancelled_20261025/original_cp932.json').read_text())
    original=copy.deepcopy(fixture)
    snapshot=next(s for s in fixture['sources'] if s['snapshot_sha256']==fixture['detail_snapshot_sha256'])
    raw=gzip.decompress(base64.b64decode(snapshot['raw_gzip_b64']))
    assert len(raw)==136226
    assert hashlib.sha256(raw).hexdigest()==snapshot['raw_sha256']=='c896c6468a98a490307755982f29bb0c04e41f34dc3edfd222df40823fa71a1e'
    assert b'charset=Shift_JIS' in raw or 'シュプレヒコール' in raw.decode('cp932')
    detail=parse_race_card_detail(raw,snapshot['content_type'])
    assert detail['runner_count']==9
    cancelled=next(r for r in detail['runners'] if r['status']=='CANCELLED')
    assert cancelled['horse_no'] is None and cancelled['horse_name']=='シュプレヒコール'
    detail['source_snapshot_sha256']=snapshot['snapshot_sha256']
    artifact={**fixture,'jra_official_race_card_detail':detail,
              'jra_official_runner_universe':copy.deepcopy(fixture['jra_official_pdf_runner_universe'])}
    bound=resolve_cancelled_runner_numbers(artifact,meeting_key='0820260409')
    declared,active=runner_universes_from_detail(bound['jra_official_race_card_detail'])
    repaired=apply_official_detail_status(bound,declared,active)
    assert declared['runner_count']==9 and active['runner_count']==8
    assert [(r['horse_no'],r['name']) for r in declared['runners'] if r['status']=='CANCELLED']==[(5,'シュプレヒコール')]
    assert [r['horse_no'] for r in repaired['jra_official_runner_universe']['runners']]==[1,2,3,4,6,7,8,9]
    assert repaired['jra_official_pdf_runner_universe']==original['jra_official_pdf_runner_universe']
    assert fixture==original


if __name__=='__main__':
    unittest.main()

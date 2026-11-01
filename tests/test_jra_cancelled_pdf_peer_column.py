"""Synthetic PDFs only: printed cancellation number survives peer-column fallback."""
import base64
import copy
import gzip
import hashlib
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import fitz

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime/jra_source_runtime'),str(ROOT/'runtime')]
from source_acquisition import sha_obj
from jra_race_card_detail import parse_detail_race_context,resolve_cancelled_runner_numbers,runner_universes_from_detail
from jra_official_pdf import official_pdf_url,fetch_and_enrich_official_pdf,apply_official_detail_status


def artifact(printed=True):
    """Nine fictitious horses; number9/frame8 independently proves the column."""
    names=['テストイチ','テストニ','テストサン','テストヨン','テストゴ',
           'テストロク','テストナナ','テストハチ','テストキュウ']
    with fitz.open() as doc:
        page=doc.new_page()
        page.insert_text((20,40),'1R',fontsize=14)
        page.insert_text((320,40),'4R',fontsize=14)
        for i,name in enumerate(names,1):
            y=60+i*55
            page.insert_text((350,y),name,fontname='japan',fontsize=12)
            page.insert_text((455,y),'（JPN）',fontname='japan',fontsize=10)
            if i!=2 or printed:page.insert_text((326,y+2),str(i),fontsize=16)
        raw=doc.tobytes()
    pdf_snap={'source_id':'JRA-OFFICIAL-RACE-PDF','official':True,'authority':'JRA_OFFICIAL',
              'cutoff_relation':'PRE_CUTOFF','raw_sha256':hashlib.sha256(raw).hexdigest(),
              'fetched_at':'2026-11-01T11:00:00+09:00',
              'raw_gzip_b64':base64.b64encode(gzip.compress(raw)).decode(),
              'final_url':official_pdf_url('2026-11-01','TKY','0520260411')}
    pdf_snap['snapshot_sha256']=sha_obj(pdf_snap)
    raw_detail=('<h1>2026年11月1日（日曜）4回東京11日 4レース</h1>'
                '<p>発走時刻：11時30分 天候 晴 芝 良 2歳 新馬 '
                'コース：1,600メートル（芝・左）</p>').encode()
    detail_snap={'source_id':'JRA-OFFICIAL-RACE-CARD-DETAIL','official':True,'authority':'JRA_OFFICIAL',
                 'cutoff_relation':'PRE_CUTOFF','content_type':'text/html;charset=utf-8',
                 'raw_sha256':hashlib.sha256(raw_detail).hexdigest(),
                 'raw_gzip_b64':base64.b64encode(gzip.compress(raw_detail)).decode()}
    detail_snap['snapshot_sha256']=sha_obj(detail_snap)
    rows=[{'horse_name':name,'horse_no':None if i==2 else i,'runner_id':None if i==2 else str(i),
           'frame_no':min(i,8),'horse_profile_token':f'pw01dud{i:010d}/BE',
           'status':'CANCELLED' if i==2 else 'ACTIVE'}
          for i,name in enumerate(names,1)]
    # Tokens are unique identities, never decoded to infer a horse number.
    detail={'runners':rows,'runner_count':9,'source_snapshot_sha256':detail_snap['snapshot_sha256'],
            'race_context':parse_detail_race_context(raw_detail,'text/html;charset=utf-8')}
    detail['sha256']=sha_obj(detail)
    pdf={'source_id':'JRA-OFFICIAL-RACE-PDF','source_snapshot_sha256':pdf_snap['snapshot_sha256'],
         'raw_sha256':pdf_snap['raw_sha256'],'official_pdf_url':pdf_snap['final_url'],'race_no':4,
         'runner_count':9,'declared_runner_count':9,
         'runners':[{'name':f'ベツテスト{i}','horse_no':i} for i in range(1,10)]}
    pdf['runner_universe_sha256']=sha_obj(pdf)
    return {'prediction_cutoff':'2026-11-01T11:25:00+09:00',
            'source_race_context':{'race_date':'2026-11-01','venue_id':'TKY','race_no':4},
            'jra_official_pdf_runner_universe':pdf,'jra_official_race_card_detail':detail,
            'sources':[pdf_snap,detail_snap]}


class CancelledPeerColumn(unittest.TestCase):
    @staticmethod
    def replace_pdf(a,raw):
        snapshot=a['sources'][0]
        snapshot.update(raw_gzip_b64=base64.b64encode(gzip.compress(raw)).decode(),
                        raw_sha256=hashlib.sha256(raw).hexdigest())
        snapshot['snapshot_sha256']=sha_obj({k:v for k,v in snapshot.items() if k!='snapshot_sha256'})
        pdf=a['jra_official_pdf_runner_universe']
        pdf.update(raw_sha256=snapshot['raw_sha256'],source_snapshot_sha256=snapshot['snapshot_sha256'])
        pdf['runner_universe_sha256']=sha_obj({k:v for k,v in pdf.items() if k!='runner_universe_sha256'})

    def test_printed_number_and_all_names_bind_without_raw_mutation(self):
        a=artifact();old=copy.deepcopy(a)
        resolve_cancelled_runner_numbers(a,meeting_key='0520260411')
        cancelled=next(r for r in a['jra_official_race_card_detail']['runners'] if r['status']=='CANCELLED')
        self.assertEqual(cancelled['horse_no'],2)
        self.assertEqual(cancelled['horse_number_binding']['method'],'EXPLICIT_SAME_RACE_PDF_PRINTED_NUMBER')
        declared,active=runner_universes_from_detail(a['jra_official_race_card_detail'])
        self.assertEqual((declared['runner_count'],active['runner_count']),(9,8))
        self.assertEqual(a['sources'],old['sources'])
        self.assertEqual(a['jra_official_pdf_runner_universe'],old['jra_official_pdf_runner_universe'])

    def test_missing_printed_number_is_not_inferred_from_order_or_gap(self):
        a=artifact(printed=False);old=copy.deepcopy(a)
        with self.assertRaisesRegex(ValueError,'PRINTED_NUMBER_AMBIGUOUS'):
            resolve_cancelled_runner_numbers(a,meeting_key='0520260411')
        self.assertEqual(a,old)

    def test_frame_only_glyph_cannot_replace_missing_horse_number(self):
        a=artifact(printed=False)
        raw=gzip.decompress(base64.b64decode(a['sources'][0]['raw_gzip_b64']))
        with fitz.open(stream=raw,filetype='pdf') as doc:
            doc[0].insert_text((305,172),'2',fontsize=16)
            self.replace_pdf(a,doc.tobytes())
        old=copy.deepcopy(a)
        with self.assertRaisesRegex(ValueError,'PRINTED_NUMBER_AMBIGUOUS'):
            resolve_cancelled_runner_numbers(a,meeting_key='0520260411')
        self.assertEqual(a,old)

    def test_competing_pdf_revision_is_not_consumed_after_verifying_another(self):
        a=artifact();other_artifact=copy.deepcopy(a)
        raw=gzip.decompress(base64.b64decode(a['sources'][0]['raw_gzip_b64']))
        with fitz.open(stream=raw,filetype='pdf') as doc:
            doc[0].insert_text((450,700),'OTHER_REVISION',fontsize=10)
            self.replace_pdf(other_artifact,doc.tobytes())
        other=other_artifact['sources'][0]
        other.update(cutoff_relation='POST_CUTOFF')
        other['snapshot_sha256']=sha_obj({k:v for k,v in other.items() if k!='snapshot_sha256'})
        a['sources'].insert(0,other);old=copy.deepcopy(a)
        with self.assertRaisesRegex(ValueError,'PDF_SNAPSHOT_REQUIRED'):
            resolve_cancelled_runner_numbers(a,meeting_key='0520260411')
        self.assertEqual(a,old)

    def test_retained_raw_can_recover_only_a_missing_legacy_view_after_full_proof(self):
        a=artifact();a.pop('jra_official_pdf_runner_universe');raw_sources=copy.deepcopy(a['sources'])
        resolve_cancelled_runner_numbers(a,meeting_key='0520260411')
        declared,active=runner_universes_from_detail(a['jra_official_race_card_detail'])
        apply_official_detail_status(a,declared,active)
        self.assertEqual((declared['runner_count'],active['runner_count']),(9,8))
        self.assertEqual(a['jra_official_runner_universe']['runner_count'],8)
        self.assertEqual(a['sources'],raw_sources)
        self.assertTrue(a['jra_official_pdf_runner_universe']['independent_pdf_name_presence_verified'])
        self.assertIsNot(a.get('formal_ready'),True)

    def test_absent_pdf_view_and_absent_raw_remain_rejected(self):
        a=artifact();a.pop('jra_official_pdf_runner_universe');a['sources']=a['sources'][1:]
        old=copy.deepcopy(a)
        with self.assertRaises(ValueError):resolve_cancelled_runner_numbers(a,meeting_key='0520260411')
        self.assertEqual(a,old)

    def test_missing_view_requires_actual_target_clock_not_only_pre_flag(self):
        for observed in (None,'2026-11-01T11:00:00','2026-11-01T12:00:00+09:00'):
            with self.subTest(fetched_at=observed):
                a=artifact();a.pop('jra_official_pdf_runner_universe');snap=a['sources'][0]
                snap['fetched_at']=observed
                snap['snapshot_sha256']=sha_obj({k:v for k,v in snap.items() if k!='snapshot_sha256'})
                old=copy.deepcopy(a)
                with self.assertRaisesRegex(ValueError,'TARGET_TEMPORAL_BINDING_REQUIRED'):
                    resolve_cancelled_runner_numbers(a,meeting_key='0520260411')
                self.assertEqual(a,old)

    def test_pdf_parse_failure_retains_valid_raw_without_admitting_universe(self):
        original=artifact();raw=gzip.decompress(base64.b64decode(original['sources'][0]['raw_gzip_b64']))
        url=original['sources'][0]['final_url']
        class Response:
            status=200
            headers={'content-type':'application/pdf'}
            def geturl(self):return url
            def read(self,limit):return raw[:limit]
            def __enter__(self):return self
            def __exit__(self,*args):pass
        class Opener:
            def open(self,*args,**kwargs):return Response()
        a={}
        with patch('jra_official_pdf.urllib.request.build_opener',return_value=Opener()), \
                patch('jra_official_pdf.utcnow',return_value='2026-11-01T02:00:00+00:00'), \
                patch('jra_official_pdf.validate_public_url'):
            with self.assertRaises(ValueError):
                fetch_and_enrich_official_pdf(a,'2026-11-01T11:25:00+09:00',
                    race_date='2026-11-01',venue_id='TKY',race_no=4,meeting_key='0520260411')
        self.assertEqual(len(a['sources']),1)
        self.assertEqual(a['sources'][0]['raw_sha256'],hashlib.sha256(raw).hexdigest())
        self.assertNotIn('jra_official_runner_universe',a)


if __name__=='__main__':unittest.main()

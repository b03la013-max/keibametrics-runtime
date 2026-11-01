"""Synthetic PDFs only: printed cancellation number survives peer-column fallback."""
import base64
import copy
import gzip
import hashlib
import sys
import unittest
from pathlib import Path

import fitz

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime/jra_source_runtime'),str(ROOT/'runtime')]
from source_acquisition import sha_obj
from jra_race_card_detail import parse_detail_race_context,resolve_cancelled_runner_numbers,runner_universes_from_detail
from jra_official_pdf import official_pdf_url


def artifact(printed=True):
    """Fictitious three-horse fixture; no retained JRA source bytes or identities."""
    names=['テストイチ','テストニ','テストサン']
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
           'horse_profile_token':'pw01dud0000000000/BE','status':'CANCELLED' if i==2 else 'ACTIVE'}
          for i,name in enumerate(names,1)]
    # Unique profile tokens are independently required; they never encode horse numbers.
    for row,token in zip(rows,['pw01dud0000000049/BE','pw01dud0000000101/BE','pw01dud0000000251/BE']):
        row['horse_profile_token']=token
    detail={'runners':rows,'runner_count':3,'source_snapshot_sha256':detail_snap['snapshot_sha256'],
            'race_context':parse_detail_race_context(raw_detail,'text/html;charset=utf-8')}
    detail['sha256']=sha_obj(detail)
    pdf={'source_id':'JRA-OFFICIAL-RACE-PDF','source_snapshot_sha256':pdf_snap['snapshot_sha256'],
         'raw_sha256':pdf_snap['raw_sha256'],'official_pdf_url':pdf_snap['final_url'],'race_no':4,
         'runner_count':3,'declared_runner_count':3,
         'runners':[{'name':name,'horse_no':i} for i,name in enumerate(['ベツイチ','ベツニ','ベツサン'],1)]}
    pdf['runner_universe_sha256']=sha_obj(pdf)
    return {'source_race_context':{'race_date':'2026-11-01','venue_id':'TKY','race_no':4},
            'jra_official_pdf_runner_universe':pdf,'jra_official_race_card_detail':detail,
            'sources':[pdf_snap,detail_snap]}


class CancelledPeerColumn(unittest.TestCase):
    def test_printed_number_and_all_names_bind_without_raw_mutation(self):
        a=artifact();old=copy.deepcopy(a)
        resolve_cancelled_runner_numbers(a,meeting_key='0520260411')
        cancelled=next(r for r in a['jra_official_race_card_detail']['runners'] if r['status']=='CANCELLED')
        self.assertEqual(cancelled['horse_no'],2)
        self.assertEqual(cancelled['horse_number_binding']['method'],'EXPLICIT_SAME_RACE_PDF_PRINTED_NUMBER')
        declared,active=runner_universes_from_detail(a['jra_official_race_card_detail'])
        self.assertEqual((declared['runner_count'],active['runner_count']),(3,2))
        self.assertEqual(a['sources'],old['sources'])
        self.assertEqual(a['jra_official_pdf_runner_universe'],old['jra_official_pdf_runner_universe'])

    def test_missing_printed_number_is_not_inferred_from_order_or_gap(self):
        a=artifact(printed=False);old=copy.deepcopy(a)
        with self.assertRaisesRegex(ValueError,'PRINTED_NUMBER_AMBIGUOUS'):
            resolve_cancelled_runner_numbers(a,meeting_key='0520260411')
        self.assertEqual(a,old)


if __name__=='__main__':unittest.main()

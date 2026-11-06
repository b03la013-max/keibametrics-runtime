"""SOURCE candidate boundaries; genuine private fixtures never enter GitHub."""
import copy
import hashlib
import json
import os
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import patch

from runtime.ohi_source_admission_candidate import review_terms, build_candidate, _policy, main
from runtime.urw_nankan_reference_source import sha, TERMS, DOM, decode
from runtime.local_physical.source_acquisition import verify_source_artifact


class PurposeBoundaries(unittest.TestCase):
    def setUp(self):
        self.raw = ('<html><div id="contents730"><p>南関東4競馬場WWWサーバ '
            '非営利の目的でかつユーザー自身で利用する場合に限り '
            '文書を複製、使用、ダウンロードすることができます '
            '個別に利用条件が付されている場合 配布、転載は認められません'
            '</p></div></html>').encode('utf-8')
        digest=hashlib.sha256(DOM(decode(self.raw)).root.all('div')[0].text().encode()).hexdigest()
        self.approved=patch('runtime.ohi_source_admission_candidate._reviewed_terms_text_sha256',return_value=digest)
        self.approved.start();self.addCleanup(self.approved.stop)
        self.now = datetime.now(timezone.utc)
        self.meta = {'url': TERMS, 'http_status': 200,
            'fetched_at': self.now.isoformat(), 'raw_sha256': hashlib.sha256(self.raw).hexdigest(),
            'source_policy': {'robots_url': 'https://www.nankankeiba.com/robots.txt',
                'status': 404, 'classification': 'ROBOTS_ABSENT_HTTP_404_NOT_DENIAL',
                'terms_url': TERMS, 'checked_at': self.now.isoformat(),
                'usage_scope': 'USER_PERSONAL_NONCOMMERCIAL_PRIVATE_ONLY_NOT_PUBLIC_REDISTRIBUTION'}}

    def test_personal_use_does_not_require_commercial_contract_or_grant_cloud(self):
        r = review_terms(self.raw, self.meta, now=self.now)
        self.assertFalse(r['commercial_contract_required_for_personal_document_use'])
        self.assertFalse(r['blanket_license_granted'])
        for k in ('automated_acquisition', 'ai_analysis', 'cloud_processing_storage'):
            self.assertIn('NOT_EXPRESSLY_DETERMINED', r[k])
        self.assertFalse(r['provider_privacy_outsourcing_clause_is_user_cloud_permission'])

    def test_terms_raw_url_time_and_changed_clauses_reject(self):
        for key, value in [('url', TERMS+'?x=1'), ('http_status', 403),
                           ('raw_sha256', '0'*64),
                           ('fetched_at', (self.now+timedelta(seconds=1)).isoformat())]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                review_terms(self.raw, {**self.meta, key:value}, now=self.now)
        raw = self.raw.replace('配布、転載は認められません'.encode(), b'changed')
        with self.assertRaisesRegex(ValueError, 'FRESH_REVIEW'):
            review_terms(raw, {**self.meta, 'raw_sha256':hashlib.sha256(raw).hexdigest()}, now=self.now)

    def test_new_restriction_cannot_reuse_previous_legal_review(self):
        raw=self.raw.replace(b'</div>', '<p>上記の利用許諾は撤回されます。</p></div>'.encode())
        with self.assertRaisesRegex(ValueError,'FRESH_REVIEW'):
            review_terms(raw,{**self.meta,'raw_sha256':hashlib.sha256(raw).hexdigest()},now=self.now)

    def test_network_unknown_and_robots_denial_are_not_accepted(self):
        for status, rule in [(403,'SOURCE_POLICY_ROBOTS_UNKNOWN'),
                             (200,'Disallow: /'), (404,'Allow: /')]:
            bad = copy.deepcopy(self.meta)
            bad['source_policy'].update(status=status, classification=rule)
            with self.subTest(status=status, rule=rule), self.assertRaises(ValueError):
                _policy(bad)

    def test_registry_is_candidate_only_no_existing_authorization_is_changed(self):
        root=Path(__file__).resolve().parents[1]
        r=json.loads((root/'profiles/local_information_source_registry_v1.10_20260924.json').read_text())['nankan_official_admission']
        self.assertFalse(r['formal_source_enabled']); self.assertFalse(r['source_consumer_enabled'])
        self.assertFalse(r['contract_scope_verified']); self.assertTrue(r['reported_permissions']['cloud_processing'])
        self.assertFalse(r['personal_use_review_candidate']['commercial_contract_required_for_that_purpose'])

    def test_cli_rejects_public_code_output_before_reading_raw(self):
        root=Path(__file__).resolve().parents[1]
        args=['candidate','--source-dir','/missing','--terms-dir','/missing',
              '--output',str(root/'candidate-must-not-be-written.json')]
        with patch('sys.argv',args),self.assertRaisesRegex(ValueError,'OUTSIDE_CODE'):
            main()


@unittest.skipUnless(os.environ.get('KM_OHI_ADMISSION_FIXTURE'), 'private genuine source required')
class GenuineSource(unittest.TestCase):
    def setUp(self):
        self.root=Path(os.environ['KM_OHI_ADMISSION_FIXTURE'])
        self.src=self.root/'fresh-r02.source'
        self.o=json.loads((self.src/'observation.json').read_text())
        self.raw=(self.root/'terms.raw.html').read_bytes()
        self.meta=json.loads((self.root/'terms.receipt.json').read_text())

    def build(self, observation=None):
        return build_candidate(observation or self.o,self.src,self.raw,self.meta,diagnostic=True)

    def test_real_raw_schema_roundtrip_is_unsigned_and_rejected_by_formal_verifier(self):
        before=copy.deepcopy(self.o); r=self.build()
        self.assertEqual(before,self.o); self.assertEqual(14,len(r['parsed_nankan_facts']))
        self.assertEqual(5,len(r['sources'])); self.assertFalse(r['active_verified'])
        self.assertFalse(r['formal_ready']); self.assertFalse(r['consumer_authorization'])
        self.assertEqual((False,['SOURCE_NOT_FORMAL_READY']),verify_source_artifact(r))

    def test_changed_raw_snapshot_and_source_receipt_rejected(self):
        r=self.build();r['sources'][0]['raw_sha256']='0'*64
        self.assertIn('SOURCE_RAW_HASH_MISMATCH',str(verify_source_artifact(r)))
        o=copy.deepcopy(self.o);o['source']['raw_sha256']='0'*64;o['sha256']=sha({k:v for k,v in o.items() if k!='sha256'})
        with self.assertRaises(ValueError):self.build(o)

    def test_other_venue_or_authority_cannot_be_converted(self):
        for change in ({'active_verified':True},{'production_authority':True},
                       {'race':{**self.o['race'],'venue_id':'KAW'}}):
            o={**copy.deepcopy(self.o),**change};o['sha256']=sha({k:v for k,v in o.items() if k!='sha256'})
            with self.subTest(change=change),self.assertRaises(ValueError):self.build(o)

    def test_resealed_other_race_and_stale_source_reject(self):
        o=copy.deepcopy(self.o);o['race']['race_no']=3;o['sha256']=sha({k:v for k,v in o.items() if k!='sha256'})
        with self.assertRaises(ValueError):self.build(o)
        with patch('runtime.ohi_single_race_research.utcnow',return_value=datetime.fromisoformat(self.o['race']['prediction_cutoff'])):
            with self.assertRaisesRegex(ValueError,'EXPIRED'):
                build_candidate(self.o,self.src,self.raw,self.meta)


if __name__=='__main__': unittest.main()

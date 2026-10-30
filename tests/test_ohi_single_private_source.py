"""Private genuine Raw conformance; no provider Raw is committed to Git."""
import copy,hashlib,json,os,unittest
from datetime import datetime,timedelta,timezone
from pathlib import Path
from runtime.ohi_single_race_research import (
    parse_program,dated_changes,parse_single_card,observe,numerical,seal,
    decode,NankanError,check_source_time,build_candidate_prediction_structure_derived,
    selection,PROFILE,
)

@unittest.skipUnless(os.environ.get('KM_OHI_PRIVATE_FIXTURE'),'requires genuine private fixture; not synthetic Live')
class GenuineOHISource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=Path(os.environ['KM_OHI_PRIVATE_FIXTURE'])
        cls.program=(cls.p/'program.raw.html').read_bytes();cls.card=(cls.p/'r01.card.raw.html').read_bytes();cls.changes=(cls.p/'changes.raw.html').read_bytes()
        cls.pm=json.loads((cls.p/'program.receipt.json').read_text());cls.cm=json.loads((cls.p/'r01.card.receipt.json').read_text());cls.chm=json.loads((cls.p/'changes.receipt.json').read_text())
        cls.races=parse_program(cls.program,cls.pm['url'],'2026-10-26');cls.race=cls.races[0]
    def observation(self):return observe(self.race,self.card,self.cm,self.changes,self.chm,[self.pm,self.cm,self.chm],program_races=self.races)
    def test_real_identity_and_all_declared(self):
        rows=parse_single_card(self.card,self.race,self.cm['url']);self.assertEqual([str(x) for x in range(1,9)],[r['runner_id'] for r in rows]);self.assertEqual(8,len({r['provider_horse_id'] for r in rows}));self.assertTrue(all(not r['active_verified'] for r in rows))
    def test_explicit_dated_no_changes_not_absence(self):self.assertEqual('EXPLICIT_NO_CHANGES_TODAY',dated_changes(self.changes,self.chm,self.race)['status'])
    def test_complete_document_required(self):
        s=decode(self.changes);s=s[:s.index('本日開催に変更情報がありません')+len('本日開催に変更情報がありません</p>')];raw=s.encode('cp932');m={**self.chm,'raw_sha256':hashlib.sha256(raw).hexdigest()}
        with self.assertRaisesRegex(NankanError,'INCOMPLETE'):dated_changes(raw,m,self.race)
    def test_wrong_header_date_not_rescued_by_aside(self):
        for kind,raw,meta in [('program',self.program,self.pm),('changes',self.changes,self.chm)]:
            with self.subTest(kind=kind):
                b=(decode(raw).replace('2026年10月26日','2026年10月25日',1)).encode('cp932');m={**meta,'raw_sha256':hashlib.sha256(b).hexdigest()}
                with self.assertRaisesRegex(NankanError,'HEADER_DATE'):
                    parse_program(b,m['url'],'2026-10-26') if kind=='program' else dated_changes(b,m,self.race)
    def test_notice_missing_is_unknown(self):
        b=decode(self.changes).replace('本日開催に変更情報がありません','変更情報の状態は未確認').encode('cp932');m={**self.chm,'raw_sha256':hashlib.sha256(b).hexdigest()}
        with self.assertRaises(NankanError):dated_changes(b,m,self.race)
    def test_other_venue_not_accepted(self):
        b=decode(self.card).replace('大井競馬','浦和競馬').encode('cp932')
        with self.assertRaisesRegex(NankanError,'BODY|MISMATCH'):parse_single_card(b,self.race,self.cm['url'])
    def test_stale_source_rejected_without_fabricated_no_bet(self):
        o=self.observation();old=(datetime.now(timezone.utc)-timedelta(seconds=601)).isoformat();o['receipts']=[{**r,'fetched_at':old} for r in o['receipts']]
        with self.assertRaisesRegex(ValueError,'EXPIRED'):check_source_time(o,'TEST')
    def test_full29_provenance_and_common_mec_roundtrip(self):
        o=self.observation();before=json.dumps(o,sort_keys=True);n=numerical(o,'OHI-2026102620110101-PRIVATE-TEST');s=n['candidate_full_numerical_summary'];self.assertEqual(232,s['terminalized_count']);self.assertEqual(0,s['unresolved_count']);self.assertFalse(s['production_authority'])
        self.assertEqual(o['sha256'],n['candidate_evidence_compiler']['source_snapshot_sha256'])
        for r in n['runners']:
            for c in r['canonical_components'].values():
                self.assertTrue(c['evidence_refs']);self.assertTrue(any(ref in c['evidence_refs'] for ref in (self.cm['raw_sha256'],'NANKAN-CARD:'+self.race['provider_race_id'])))
        p=build_candidate_prediction_structure_derived(n)['candidate_static_prediction'];x=selection(o,p,n['race_id']);tickets=x['tickets'];self.assertEqual(len(tickets),len(x['tree']['reflattened_tickets']));self.assertTrue(all(t['stake']==100 for t in tickets));self.assertEqual(sum(t['stake'] for t in tickets),x['tree']['total_investment']);self.assertLessEqual(x['tree']['total_investment'],10000);self.assertEqual(0,x['actual_investment_reserved']);self.assertEqual(before,json.dumps(o,sort_keys=True))

if __name__=='__main__':unittest.main()

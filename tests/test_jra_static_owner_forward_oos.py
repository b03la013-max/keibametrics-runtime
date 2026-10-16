from copy import deepcopy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'runtime'))
from jra_static_owner_forward_oos import freeze,evaluate,scorecard,sha,fingerprint
from test_jra_production_auto_handoff import fixture,ROOT


def prepared():
    intent,env,report,_=fixture()
    intent.update(race_date='2026-10-10',race_no=5,jra_source={'jra_meeting_key':'0520260403'})
    source=env['artifact'];source['jra_official_runner_universe']={'runners':[{'runner_id':str(i)} for i in range(1,4)]}
    source['jra_official_race_card_detail']={'runners':[{'runner_id':str(i),'popularity_rank':4-i} for i in range(1,4)]}
    source['source_snapshot_sha256']=sha({k:v for k,v in source.items() if k!='source_snapshot_sha256'})
    report.update(race_id=intent['race_id'],family_id='JRA')
    return intent,env,report

class ForwardTests(unittest.TestCase):
    def frozen(self):
        intent,env,report=prepared()
        return freeze(intent,env,report,source_verified=True,created_at='2026-10-10T12:10:00+09:00',root=ROOT)

    def test_forward_record_is_shadow_not_a_production_approval(self):
        pre=self.frozen()
        self.assertEqual(pre['full_index_count'],60)
        self.assertEqual(pre['market_ranking'],['3','2','1'])
        self.assertFalse(pre['production_authority'])
        self.assertFalse(pre['signed_final_issued'])
        result=evaluate(pre,['1','2','3'],result_sha256='f'*64,observed_at='2026-10-10T12:30:00+09:00',git_commit_at='2026-10-10T12:11:00+09:00')
        score=scorecard([result,result],policy_fingerprint=pre['policy_fingerprint'])
        self.assertEqual(score['eligible_settled_races'],1)
        self.assertEqual(score['remaining_forward_races'],29)
        self.assertFalse(score['production_activation_authorized'])
        self.assertFalse(score['market_baseline_superiority_proven'])

    def test_partial_candidate_unverified_late_and_replay_cannot_freeze(self):
        for case in ('late','partial','candidate','signature','replay','market','identity'):
            intent,env,report=prepared();now='2026-10-10T12:10:00+09:00';verified=True
            if case=='late':now='2026-10-10T12:19:00+09:00'
            if case=='partial':report['production_full_numerical_ready']=False
            if case=='candidate':report['prepared_numerical_request']['runners'][0]['canonical_components']['HPI']['candidate_only']=True
            if case=='signature':verified=False
            if case=='replay':intent['acceptance_only']=True
            if case=='market':env['artifact']['jra_official_race_card_detail']['runners'][0]['popularity_rank']=None
            if case=='identity':report['prepared_numerical_request']['race_id']='OTHER'
            with self.subTest(case=case),self.assertRaises(ValueError):
                freeze(intent,env,report,source_verified=verified,created_at=now,root=ROOT)

    def test_postcutoff_commit_witness_and_wrong_result_rejected(self):
        pre=self.frozen()
        with self.assertRaisesRegex(ValueError,'NOT_PROSPECTIVE'):
            evaluate(pre,['1','2','3'],result_sha256='f'*64,observed_at='2026-10-10T12:30:00+09:00',git_commit_at='2026-10-10T12:20:00+09:00')
        with self.assertRaises(ValueError):
            evaluate(pre,['1','1','3'],result_sha256='f'*64,observed_at='2026-10-10T12:30:00+09:00',git_commit_at='2026-10-10T12:11:00+09:00')

    def test_existing_candidate_and_changed_policy_records_do_not_count(self):
        pre=self.frozen()
        result=evaluate(pre,['1','2','3'],result_sha256='f'*64,observed_at='2026-10-10T12:30:00+09:00',git_commit_at='2026-10-10T12:11:00+09:00')
        old=deepcopy(result);old['profile']='JRA-SOURCE-DERIVED-CANDIDATE';old['sha256']=sha({k:v for k,v in old.items() if k!='sha256'})
        score=scorecard([old,result],policy_fingerprint='different')
        self.assertEqual(score['eligible_settled_races'],0)
        self.assertFalse(score['automatic_promotion'])

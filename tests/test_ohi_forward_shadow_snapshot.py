"""Forward fixtures are unit tests, never genuine future evidence."""
import copy
from datetime import datetime, timezone, timedelta
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
P=Path(__file__).resolve().parents[1]/'scripts/ohi_forward_shadow_snapshot.py'
spec=importlib.util.spec_from_file_location('forward_shadow',P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class ForwardShadowTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,10,27,3,tzinfo=timezone.utc)
        self.contract=m.make_contract(now=self.now-timedelta(hours=1))
        self.race={'venue_id':'OHI','race_date':'2026-10-27','race_no':1,'provider_race_id':'2026102720110201','prediction_cutoff':(self.now+timedelta(hours=2)).isoformat()}
        self.obs={'race':self.race,'source_profile':m.SOURCE_PROFILE,'receipts':[{'fetched_at':(self.now-timedelta(seconds=50)).isoformat()}],'sha256':'a'*64}
        self.manifest=m.seal({'source_sha256':self.obs['sha256'],'model_sha256':m.research.MODEL,'engine_sha256':m.research.ENGINE,'parameters_sha256':m.research.PARAM,'dependency_sha256':copy.deepcopy(self.contract['prediction_dependency_sha256'])})
        self.original={'race':self.race,'freeze_at':(self.now-timedelta(seconds=20)).isoformat(),'classification':m.research.CLASS,'production_authority':False,'registered_oos_credit':0,'signed_final':False,'actual_purchase':False,'formal_source':False,'source_sha256':self.obs['sha256'],'execution_manifest_sha256':self.manifest['sha256'],'numerical_summary':{'required_count':29,'unresolved_count':0,'terminalized_count':29},'all_runners':[{'runner_id':'1'}],'sha256':'b'*64,'owners':{o:{'roles':{'1':['W']}} for o in m.OWNERS},'portfolios':{o:{'capital':{'capital_limit':10000},'tickets':[]} for o in m.OWNERS},'krs':{}}
        for owner in m.OWNERS:
            output={'summary':[]}
            receipt=m.seal({'engine_sha256':m.research.ENGINE,'parameter_map_sha256':m.research.PARAM,'runs':5000,'seed':1,'actual_engine_executed':True,'output_sha256':m.sha(output),'input_sha256':m.sha({'horses':[]})})
            self.original['krs'][owner]={'output':output,'receipt':receipt}
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.folder=Path(self.temp.name)/'original';self.folder.mkdir()
        self.patchers=[patch.object(m.research,'readback',return_value=(self.original,'body')),patch.object(m.research,'verify_observation',return_value=True),patch.object(m.research,'check_source_time',return_value={'stage':'FORWARD_SHADOW_SNAPSHOT'}),patch.object(m,'load',side_effect=self.loader),patch.object(m,'diagnose',return_value={'outcome':None})]
        for p in self.patchers:p.start();self.addCleanup(p.stop)
    def loader(self,path):return {'observation.json':self.obs,'execution-manifest.json':self.manifest,'features.json':{},'input.json':{'horses':[]}}[Path(path).name]
    def snap(self):return m.capture_snapshot(self.folder,self.contract,now=self.now)
    def reseal_manifest(self):
        self.manifest=m.seal({k:v for k,v in self.manifest.items() if k!='sha256'});self.original['execution_manifest_sha256']=self.manifest['sha256']
    def test_contract_does_not_claim_model_purchase_or_oos(self):
        c=self.contract
        self.assertFalse(c['A']['implemented']);self.assertFalse(c['B']['implemented']);self.assertIsNone(c['D']['chosen_prefix']);self.assertFalse(c['D']['purchase_policy']);self.assertEqual(0,c['registered_oos_credit']);self.assertEqual(10000,c['owner_cap_yen']);self.assertEqual(5000,c['krs_runs_per_owner']);self.assertEqual(1,c['krs_seed'])
        self.assertEqual(list(range(1,13)),c['target_race_numbers']);self.assertEqual('R1',c['first_acceptance_priority'])
    def test_valid_snapshot_readonly_never_evaluates_results(self):
        before=copy.deepcopy(self.original);r=self.snap();self.assertEqual(before,self.original);self.assertFalse(r['outcome_received']);self.assertFalse(r['performance_evaluated']);self.assertFalse(r['owner_ack']);self.assertEqual(0,r['registered_oos_credit']);m.diagnose.assert_called_once_with(self.original,{},None);m.research.verify_observation.assert_called_once();m.research.check_source_time.assert_called_once_with(self.obs,'FORWARD_SHADOW_SNAPSHOT');self.assertEqual([],r['selected_frozen_tickets']['BASELINE'])
    def test_contract_after_prediction_and_snapshot_at_cutoff_rejected(self):
        self.contract=m.make_contract(now=self.now-timedelta(seconds=10))
        with self.assertRaisesRegex(ValueError,'FREEZE_CUTOFF'):self.snap()
        self.contract=m.make_contract(now=self.now-timedelta(hours=1));self.now=datetime.fromisoformat(self.race['prediction_cutoff'])
        with self.assertRaisesRegex(ValueError,'FREEZE_CUTOFF'):self.snap()
    def test_other_day_venue_race_or_provider_rejected(self):
        for change in ({'race_date':'2026-10-26'},{'venue_id':'URW'},{'race_no':13},{'provider_race_id':'2026102820110201'}):
            old=copy.deepcopy(self.original['race']);self.original['race']={**old,**change}
            with self.subTest(change=change),self.assertRaisesRegex(ValueError,'TARGET_RACE_SCOPE'):self.snap()
            self.original['race']=old
    def test_resealed_contract_cannot_change_cap_seed_model_or_scope(self):
        for change in ({'owner_cap_yen':20000},{'krs_seed':2},{'model_sha256':'f'*64},{'target_race_numbers':[1]},{'production_authority':True}):
            altered=m.seal({**{k:v for k,v in self.contract.items() if k!='sha256'},**change})
            with self.subTest(change=change),self.assertRaisesRegex(ValueError,'DEFINITION'):m.capture_snapshot(self.folder,altered,now=self.now)
    def test_mutated_owner_numerical_capital_and_missing_dependency_rejected(self):
        initial=copy.deepcopy(self.manifest['dependency_sha256'])
        for key in m.PREDICTION_PATHS:
            self.manifest['dependency_sha256']=copy.deepcopy(initial)
            self.manifest['dependency_sha256'][key]='0'*64
            self.reseal_manifest()
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,'DEPENDENCY_CODE'):self.snap()
        self.manifest['dependency_sha256']=copy.deepcopy(initial)
        self.manifest['dependency_sha256'].pop('runtime/local_fullnumerical_candidate.py')
        self.reseal_manifest()
        with self.assertRaisesRegex(ValueError,'DEPENDENCY_KEYS'):self.snap()

    def test_only_two_known_capital_transports_are_compatible(self):
        for value in m.CAPITAL_TRANSPORT_HASHES:
            self.manifest['dependency_sha256'][m.CAPITAL_PATH]=value
            self.reseal_manifest();self.snap()
        self.manifest['dependency_sha256']['runtime/capital_policy.py']=m.CAPITAL_TRANSPORT_HASHES[0]
        self.reseal_manifest()
        with self.assertRaisesRegex(ValueError,'DEPENDENCY_CODE'):self.snap()

    def test_contract_portable_between_both_known_capital_byte_roots(self):
        read_bytes=Path.read_bytes
        capital=(m.ROOT/m.CAPITAL_PATH).resolve()
        actual=capital.read_bytes()
        variants={m.hashlib.sha256(b).hexdigest():b for b in (actual,actual.rstrip(b'\n'),actual.rstrip(b'\n')+b'\n',actual.rstrip(b'\n')+b'\n\n')}
        self.assertTrue(set(m.CAPITAL_TRANSPORT_HASHES)<=set(variants))
        for created_hash in m.CAPITAL_TRANSPORT_HASHES:
            def created_read(path):
                return variants[created_hash] if path.resolve()==capital else read_bytes(path)
            with patch.object(Path,'read_bytes',created_read):
                contract=m.make_contract(now=self.now-timedelta(hours=1))
                self.assertEqual(m.CAPITAL_TRANSPORT_HASHES[1],contract['prediction_dependency_sha256'][m.CAPITAL_PATH])
                self.assertEqual(created_hash,contract['contract_creation_transport_evidence'][m.CAPITAL_PATH])
            for consumed_hash in m.CAPITAL_TRANSPORT_HASHES:
                def consumed_read(path):
                    return variants[consumed_hash] if path.resolve()==capital else read_bytes(path)
                with self.subTest(created=created_hash,consumed=consumed_hash),patch.object(Path,'read_bytes',consumed_read):
                    m.verify_contract(contract,self.now)
        with patch.object(Path,'read_bytes',lambda path: b'{}\n' if path.resolve()==capital else read_bytes(path)):
            with self.assertRaisesRegex(ValueError,'LOCAL_CAPITAL_TRANSPORT_UNKNOWN'):m.make_contract(now=self.now)

    def test_krs_input_must_match_receipt_canonical_sha(self):
        receipt=self.original['krs']['BASELINE']['receipt']
        receipt['input_sha256']='0'*64
        self.original['krs']['BASELINE']['receipt']=m.seal({k:v for k,v in receipt.items() if k!='sha256'})
        with self.assertRaisesRegex(ValueError,'KRS_INPUT_BINDING'):self.snap()
    def test_stale_future_and_missing_receipt_rejected(self):
        for seconds in (600,-1):
            self.obs['receipts']=[{'fetched_at':(self.now-timedelta(seconds=seconds)).isoformat()}]
            with self.subTest(seconds=seconds),self.assertRaisesRegex(ValueError,'SOURCE_AGE'):self.snap()
        self.obs['receipts']=[]
        with self.assertRaisesRegex(ValueError,'SOURCE_AGE'):self.snap()
    def test_diagnostic_original_and_incomplete_numerical_rejected(self):
        self.original['classification']='POSTCUTOFF_OR_OFFLINE_DIAGNOSTIC'
        with self.assertRaisesRegex(ValueError,'CLASSIFICATION'):self.snap()
        self.original['classification']=m.research.CLASS;self.original['numerical_summary']['unresolved_count']=1
        with self.assertRaisesRegex(ValueError,'29_TERMINAL'):self.snap()
    def test_bad_krs_receipt_and_noninteger_stake_rejected(self):
        receipt=self.original['krs']['BASELINE']['receipt'];receipt['seed']=2
        with self.assertRaisesRegex(ValueError,'KRS_RECEIPT'):self.snap()
        receipt['seed']=1;self.original['portfolios']['BASELINE']['tickets']=[{'stake':100.0}]
        with self.assertRaisesRegex(ValueError,'CAP_OR_STAKE'):self.snap()
    def test_naive_clock_and_bad_contract_hash_rejected(self):
        with self.assertRaisesRegex(ValueError,'UTC_AWARE'):m.make_contract(now=datetime(2026,10,26))
        self.contract['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'SELF_HASH'):self.snap()
    def test_immutable_write_rejects_existing_output(self):
        p=Path(self.temp.name)/'contract.json';m.research.write(p,self.contract);before=p.read_bytes()
        with self.assertRaisesRegex(ValueError,'IMMUTABLE'):m.research.write(p,self.contract)
        self.assertEqual(before,p.read_bytes())
if __name__=='__main__':unittest.main()

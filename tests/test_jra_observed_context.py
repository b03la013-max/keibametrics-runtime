from copy import deepcopy
import base64,gzip,hashlib,json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"runtime"))
from jra_source_runtime.jra_race_card_detail import parse_detail_race_context
from jra_source_runtime.jra_observed_context import resolve_observed_context,bind_observed_context
from jra_execution_maturity_bridge import prepare_production_numerical

RAW='''<html>出馬表 2026年10月10日（土曜）4回京都3日 9レース
ここから本文です 2026年10月10日（土曜）4回京都3日 発走時刻：14時15分
天候 晴 ダート 良 3歳以上1勝クラス [指定] 定量 コース：1,400 メートル （ダート・右）</html>'''.encode()

def source():
    return {"source_race_context":{"race_date":"2026-10-10","venue_id":"KYO","race_no":9},
            "jra_race_context":{"surface":"芝","distance_m":2000,"race_class":"1勝クラス"},
            "jra_official_race_card_detail":{"source_snapshot_sha256":"a"*64},
            "sources":[{"source_id":"JRA-OFFICIAL-RACE-CARD-DETAIL","snapshot_sha256":"a"*64,
                        "raw_sha256":hashlib.sha256(RAW).hexdigest(),"official":True,"authority":"JRA_OFFICIAL",
                        "cutoff_relation":"PRE_CUTOFF","raw_gzip_b64":base64.b64encode(gzip.compress(RAW)).decode(),
                        "content_type":"text/html;charset=utf-8"}]}

class ContextTests(unittest.TestCase):
    def test_printed_conditions_override_calendar_without_editing_input(self):
        obj=source();before=deepcopy(obj)
        context=resolve_observed_context(obj)
        self.assertEqual(obj,before)
        self.assertEqual((context['surface'],context['distance_m']),("ダ",1400))
        self.assertEqual(context['going'],"良")
        bind_observed_context(obj)
        self.assertEqual(obj['jra_calendar_race_context'],before['jra_race_context'])
        self.assertEqual(obj['jra_race_context_reconciliation']['differences']['distance_m'],{"planned":2000,"observed":1400})

    def test_invalid_hash_identity_and_postcutoff_fail_closed(self):
        changes=(lambda x:x['sources'][0].update(raw_sha256='b'*64),
                 lambda x:x['source_race_context'].update(race_no=8),
                 lambda x:x['sources'][0].update(cutoff_relation='POST_CUTOFF'),
                 lambda x:x['sources'][0].update(official=False),
                 lambda x:x['jra_official_race_card_detail'].update(race_context={'surface':'芝'}))
        for change in changes:
            obj=source();change(obj)
            with self.assertRaises(ValueError):resolve_observed_context(obj)

    def test_unbound_printed_assertion_is_not_authority(self):
        obj=source();obj['sources']=[]
        obj['jra_official_race_card_detail']['race_context']=parse_detail_race_context(RAW)
        with self.assertRaisesRegex(ValueError,'SOURCE_BINDING'):resolve_observed_context(obj)

    def test_real_kyoto9_signed_source_remains_immutable_and_improves_coverage(self):
        root=Path(__file__).resolve().parents[1];eid='KM-JRA-KYO-20261010-R09-LIVE-R1'
        env=json.loads(next((root/'runtime/executions'/eid/'SOURCE/runs').glob('*/source_receipt_envelope.json')).read_text())
        intent=json.loads((root/'runtime/jra_formal_intents'/(eid+'.json')).read_text());before=deepcopy(env)
        report=prepare_production_numerical(intent,env)
        self.assertEqual(env,before)
        self.assertEqual(resolve_observed_context(env['artifact'])['distance_m'],1400)
        self.assertGreaterEqual(report['partial_base_calculated_count'],90)
        self.assertFalse(report['production_full_numerical_ready'])

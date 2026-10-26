import copy
from datetime import datetime,timezone
import unittest
from runtime.local_evidence_quality_audit import (
    BASE9, audit_runner, component_quality, history_course_observation, passing_path_observation,
)


class EvidenceQualityAuditTests(unittest.TestCase):
    def runner(self):
        features={};indices={}
        for i,index in enumerate(BASE9):
            name=f'component_{i}'
            features[name]={'missing':True,'coverage':0,'source_timestamp':'2026-10-26T01:00:00+00:00','source_fact':'not observed','evidence_refs':['card-hash']}
            indices[index]={'terminal_status':'RULED-NEUTRAL','value':52,'observed_weight_fraction':1,
                'components':[{'component':name,'missing':True,'coverage':0,'weight':100,'score':52}]}
        indices['TPI-L']={'terminal_status':'CALCULATED','value':52,'missingness_fraction':0.5,'source_fact':'original formula','evidence_refs':['card-hash']}
        indices['EVI/CEV']={'terminal_status':'CALCULATED','value':52,'source_fact':'original formula','evidence_refs':['card-hash']}
        for name in ('position_acquisition','position_maintenance','third_corner_progression','leadership_stalk_acceptance','kickback_traffic_tolerance','going_adaptation','course_geometry','going_fit'):
            features[name]={'missing':True,'source_timestamp':'2026-10-26T01:00:00+00:00','evidence_refs':[]}
        return {'runner_id':'1','name':'Test','candidate_indices':indices,'evidence_features':features,
                'raw_candidate_evidence':{'starts':[]}}

    def test_inner_outer_marker_does_not_invent_turn_or_sand(self):
        x=history_course_observation({'going_observed':'不外ダ 1200','venue':'大井','direction':'UNKNOWN','going':'不良','surface':'DIRT'})
        self.assertEqual('OUTER',x['course_family_observed']);self.assertIsNone(x['direction_explicit'])
        self.assertTrue(x['sand_regime'].startswith('UNKNOWN'))
        y=history_course_observation({'going_observed':'良左ダ 1400','direction':'UNKNOWN'})
        self.assertEqual('LEFT',y['direction_explicit'])

    def test_four_unlabelled_calls_do_not_become_named_corner_track(self):
        x=passing_path_observation({'content_positions':[8,7,4,2]})
        self.assertEqual(4,x['call_count']);self.assertFalse(x['complete_2_3_4_corner_path'])
        y=passing_path_observation({'content_positions':[8,7,4,2],'named_corner_positions':{'2':7,'3':4,'4':2}})
        self.assertTrue(y['complete_2_3_4_corner_path'])

    def test_known_proxy_is_not_promoted_into_direct_measurement(self):
        c={'component':'opponent_strength','missing':False,'coverage':1,'weight':25,'score':70}
        r=component_quality('HPI-L',c,{'source_fact':'class and field','source_timestamp':'2026-10-26T01:00:00+00:00'})
        self.assertEqual('C',r['evidence_class']);self.assertFalse(r['score_is_measurement'])
        c['missing']=True;self.assertEqual('D',component_quality('HPI-L',c,{})['evidence_class'])

    def test_neutral_denominator_is_not_observed_information_and_score_unchanged(self):
        runner=self.runner();before=copy.deepcopy(runner)
        result=audit_runner(runner,{'provider_race_id':'2026102620110101'},'2026-10-26T14:25:00+09:00')
        b=result['base9']['BVIg-L'];self.assertEqual(1,b['legacy_observed_weight_fraction'])
        self.assertEqual(0,b['weighted_observed_share']);self.assertEqual(0,b['coverage_adjusted_weighted_share'])
        self.assertEqual(52,b['value']);self.assertEqual(before,runner)
        self.assertIn('BVIg-L',result['derived20']['TPI-L']['direct_neutral_index_inputs'])

    def test_post_cutoff_source_is_rejected(self):
        runner=self.runner();runner['evidence_features']['component_0']['source_timestamp']='2026-10-26T06:00:00+00:00'
        with self.assertRaisesRegex(ValueError,'POSTCUTOFF'):audit_runner(runner,{'provider_race_id':'x'},'2026-10-26T14:25:00+09:00')

    def test_market_diagnostic_retains_cross_runner_ability_rank_inputs(self):
        runner=self.runner();runner['raw_candidate_evidence']['popularity']=3
        runner['candidate_indices']['SRI-L']={'terminal_status':'CALCULATED','value':52,
            'source_fact':'existing SRI formula','evidence_refs':['card-hash']}
        for name in ('PRI','OPI-V'):
            runner['candidate_indices'][name]={'terminal_status':'CALCULATED','value':52,
                'source_fact':'ability rank versus official market rank','evidence_refs':['card-hash']}
        before=copy.deepcopy(runner)
        result=audit_runner(runner,{'provider_race_id':'2026102620110101'},'2026-10-26T14:25:00+09:00')
        for name in ('PRI','OPI-V'):
            row=result['derived20'][name]
            self.assertEqual(['TPI-L','SRI-L','HPI-L','CFIg-L','RFIg-L'],row['direct_index_inputs'])
            self.assertEqual('ALL_RUNNERS_IN_SAME_FROZEN_RACE',row['cross_runner_population_inputs']['scope'])
            self.assertEqual(3,row['cross_runner_population_inputs']['this_runner_official_market_rank'])
        self.assertEqual(before,runner)

    def test_naive_timestamp_cannot_establish_cutoff_purity(self):
        runner=self.runner();runner['evidence_features']['component_0']['source_timestamp']='2026-10-26T01:00:00'
        with self.assertRaisesRegex(ValueError,'WITHOUT_ZONE'):audit_runner(runner,{'provider_race_id':'x'},'2026-10-26T14:25:00+09:00')


if __name__=='__main__':unittest.main()

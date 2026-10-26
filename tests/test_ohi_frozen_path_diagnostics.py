"""Outcome evaluation boundaries; no model or purchase policy tests."""
import copy
import importlib.util
from pathlib import Path
import unittest

p=Path(__file__).resolve().parents[1]/'scripts/ohi_frozen_path_diagnostics.py'
spec=importlib.util.spec_from_file_location('ohi_path_diagnostics',p)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def ticket(kind,selection):return {'bet_type':kind,'selection':selection,'stake':100}


def portfolio(roles,no_bet=False):
    ids=list(roles)
    pairs=[{'head':h,'second':s} for h in ids for s in ids if h!=s and 'W' in roles[h] and 'P2' in roles[s]]
    thirds=[{**p,'third':t} for p in pairs for t in ids if t not in (p['head'],p['second']) and 'P3' in roles[t]]
    ticks=[ticket('EXACTA',[p['head'],p['second']]) for p in pairs]
    return {'semantic_request':{'pair_dispositions':pairs,'third_dispositions':thirds},
            'mec':{'tickets':ticks},'capital':{'no_bet':no_bet},'tickets':[] if no_bet else ticks}


class FrozenPathEvaluation(unittest.TestCase):
    def test_other_day_same_runner_numbers_cannot_supply_result(self):
        race={'provider_race_id':'2026102620110101','race_no':1,'race_date':'2026-10-26','venue_id':'OHI'}
        label={'provider_race_id':race['provider_race_id'],'rank_groups':[['4'],['7'],['5']]}
        m.verify_label_identity(label,race)
        for change in ({'provider_race_id':'2026102720110201'}, {'provider_race_id':None},
                       {'race_date':'2026-10-27'}, {'venue_id':'URW'}, {'race_no':2},
                       {'source_url':'https://www.nankankeiba.com/result/2026102720110201.do'}):
            with self.subTest(change=change),self.assertRaises(ValueError):
                m.verify_label_identity({**label,**change},race)

    def test_duplicate_race_labels_do_not_silently_replace_evidence(self):
        for rows in ([{'race_no':1},{'race_no':1}], {'1':{'finish_groups':[]},'01':{'finish_groups':[]}}):
            with self.subTest(rows=rows),self.assertRaisesRegex(ValueError,'DUPLICATE_RACE'):
                m.top3_labels({'races':rows})

    def test_unordered_hit_does_not_mean_ordered_role_success(self):
        groups=[['4'],['7'],['5']]
        tickets=[ticket('TRIO',[4,5,7]),ticket('EXACTA',[4,5])]
        hit=m.matching_tickets(tickets,groups)
        self.assertEqual(1,len(hit['TRIO']));self.assertEqual([],hit['EXACTA'])

    def test_second_place_tie_has_two_pairs_one_trio_no_invented_third(self):
        groups=m.top3_labels({'races':{'11':{'finish_groups':[['9'],['2','4'],['7'],['6']]}}})[11]['rank_groups']
        self.assertEqual([['9'],['2','4']],groups)
        hits=m.matching_tickets([ticket('EXACTA',[9,2]),ticket('EXACTA',[9,4]),
            ticket('TRIO',[2,4,9]),ticket('TRIFECTA',[9,2,4])],groups)
        self.assertEqual([2,1,0],[len(hits[k]) for k in ('EXACTA','TRIO','TRIFECTA')])

    def test_missing_winner_is_first_loss_even_when_capital_also_rejects(self):
        roles={'1':[],'2':['W','P2'],'3':['P3']}
        self.assertEqual('W_ROLE_BOUNDARY',m.first_path_loss({'ranking':['2','3','1'],'roles':roles},portfolio(roles,True),[['1'],['2'],['3']]))

    def test_retained_roles_with_no_bet_is_capital_loss_not_prediction_loss(self):
        roles={'1':['W'],'2':['P2'],'3':['P3']}
        self.assertEqual('CAPITAL_FULL_MEC_REJECTED',m.first_path_loss({'ranking':['1','2','3'],'roles':roles},portfolio(roles,True),[['1'],['2'],['3']]))

    def test_diff_does_not_remove_a_changed_physics_value(self):
        a={'horses':[{'hsv':{'ability':50},'static_roles':['W']}]}
        b=copy.deepcopy(a);b['horses'][0]['hsv']['ability']=51
        self.assertEqual(['/horses/0/hsv/ability'],m.diff_paths(a,b))

    def test_cluster_parity_cliff_is_detected_not_silently_changed(self):
        rows=[{'runner_id':str(i),'w_score':52.0} for i in (1,2,3)]
        changes=m.cluster_sensitivity(rows,'w_score',1)
        self.assertTrue(any(v['original_width']==3 and v['perturbed_width']==1 for v in changes))
        self.assertTrue(all(v['w_score']==52.0 for v in rows))


if __name__=='__main__':unittest.main()

"""Real frozen-input checks for explanation, never a new prediction policy."""
from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'scripts')]
from jra_role_exclusion_audit import build_role_exclusion_audit,support_lineage
from jra_20261025_prediction_lineage import audit,bvi_kind


@pytest.fixture(scope='module')
def report():return audit(ROOT)


def test_all_saved_finals_and_role_cells_are_replayed_without_new_scores(report):
    assert len(report['coverage'])==36 and len(report['races'])==30
    assert sum(v['runners'] for v in report['by_venue'].values())==400
    assert sum(v['role_cells'] for v in report['by_venue'].values())==1200
    assert all(r['role_explanation']['status']=='REPLAY_MATCHED' for r in report['races'])
    assert report['source_final_result_rewritten']==report['new_forward_oos_credit']==report['new_candidates']==0


def test_niigata_missing_going_is_not_low_suitability_or_measured_zero(report):
    s=report['by_venue']['NGT']
    assert s['runners']==153 and s['going_feature_missing']==144
    assert s['terminal_runners']==13 and s['all_saved_numerical_runners']==166
    assert s['bvi_classes']=={'MEASURED':143,'MEASURED_PLUS_DCR':3,'DCR_ONLY':7}
    rows=[x for r in report['races'] if r['venue']=='NGT' for x in r['runners']]
    missing=[x for x in rows if not x['going']['feature_present']]
    assert sum(x['going']['matching_prior_runs']==0 for x in missing)==120
    assert sum(x['going']['matching_prior_runs']==1 for x in missing)==24
    assert not any(x['going']['matching_prior_runs']>=2 for x in missing)
    assert all(x['going']['missing_is_low_suitability'] is False for x in missing)
    assert bvi_kind({'value':50,'components':[],'adjustments':[]})=='UNMEASURED_NO_COMPONENT_OR_DCR_PROOF'
    terminal=next(t for t in report['no_bet_terminal_lineage'] if t['race_id']=='KM-JRA-NGT-20261025-R01')
    assert terminal['runner_count']==13 and not terminal['formal_role_adoption_reconstructed']
    assert not terminal['krs_executed'] and not terminal['signed_final_created']


def test_shared_snapshot_hash_is_not_independent_or_shared_event_proof():
    cells={k:{'value':80,'components':[{'feature':'f','evidence_refs':['f'*64]}]} for k in ('CFI','PRI','RFI')}
    row={'runner_id':'7','canonical_components':cells,'evidence_features':{'f':{}}}
    policy={'support_groups':{'W':['CFI','PRI','RFI']},'support_floor':65}
    assert support_lineage(row,'W',policy)['shared_horse_date_dependencies']==[]
    for k in ('CFI','RFI'):
        cells[k]['components'][0]['evidence_refs'] += [
            'SOURCE_FETCHED_AT:2026-10-01T12:00:00Z',
            'JRA_PERSON_STATS:2026-10-01',
            'JRA_OFFICIAL_HISTORY:8:2026-10-01:3:10',
            'JRA_OFFICIAL_HISTORY:7:2026-99-01:3:10']
    assert support_lineage(row,'W',policy)['shared_horse_date_dependencies']==[]
    for k in ('CFI','RFI'):
        cells[k]['components'][0]['evidence_refs'].append('JRA_OFFICIAL_HISTORY:7:2026-10-01:3:10')
    before=deepcopy(row);out=support_lineage(row,'W',policy)
    assert out['shared_horse_date_dependencies']==[{'runner_id':'7','prior_date':'2026-10-01','index_groups':['CFI','RFI']}]
    assert out['independent_event_identity_proven'] is False and row==before


def test_wrong_race_source_cannot_be_labeled_as_a_valid_role_explanation():
    q=json.loads((ROOT/'runtime/requests/KM-JRA-TKY-20261025-R02-LIVE-R1-FORMAL.json').read_text())
    authority=json.loads((ROOT/'profiles/KM_FAMILY_CURRENT_AUTHORITY_20261012_R51.json').read_text())
    q['race_id']='KM-JRA-KYO-20261025-R02'
    with pytest.raises(ValueError,match='ROLE_AUDIT_SOURCE_RACE_MISMATCH'):
        build_role_exclusion_audit(q,authority,ROOT)


def test_success_controls_and_unmeasured_time_are_preserved(report):
    rows={r['race_id']:r for r in report['races']}
    for rid in ('KM-JRA-TKY-20261025-R02','KM-JRA-KYO-20261025-R07','KM-JRA-KYO-20261025-R08'):
        assert all(r['role_captured'] for r in rows[rid]['outcome_diagnostics'])
        assert rows[rid]['outcome_used_to_form_roles'] is False
    for race in rows.values():
        for runner in race['runners']:
            assert runner['source_available_at'] is None
            assert runner['source_freeze_at']==race['source_freeze_at']
            assert runner['numerical_component_count']==20 and runner['new_numeric_calculations']==0


def test_initial_condition_winner_remains_unknown_instead_of_a_backfilled_feature(report):
    r=next(x for x in report['races'] if x['race_id']=='KM-JRA-NGT-20261025-R03')
    winner=next(x for x in r['outcome_diagnostics'] if x['role']=='W')
    assert winner['runner_id']=='18' and winner['static_rank']==17 and not winner['role_captured']
    detail=next(x for x in r['runners'] if x['runner_id']=='18')
    assert detail['admissible_prior_runs']==1
    assert detail['prior_runs'][0]['surface']=='ダ' and detail['going']['target_surface']=='芝'
    assert detail['going']['matching_prior_runs']==0 and 'going_fit' not in detail['features_present']
    assert all(row['unmet_criteria'] for row in r['role_explanation']['rows'] if row['runner_id']=='18')

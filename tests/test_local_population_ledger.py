import sys
import copy
import json
import hashlib
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"/"local_physical"))

from local_population_ledger import PROFILE, build_population_seed


def test_population_seed_from_pre_race_history():
    art={"auxiliary_evidence":{
      "profiles":{"horses":{"1":{
        "source_id":"H1","source_snapshot_sha256":"abc",
        "history":[
          {"date":"2026/09/01","venue":"浦和","distance":1400,"going":"不良","class":"C1","popularity":3,"finish":1},
          {"date":"2026/08/01","venue":"浦和","distance":1400,"going":"良","class":"C1","popularity":2,"finish":4},
        ]
      }}},
      "pedigree_population_seed":{"seeds":[{"runner_id":"1","horse_name":"A","sire":"父A","dam":"母A","damsire":"母父A"}]}
    }}
    out=build_population_seed(art)
    assert out["profile"]==PROFILE
    assert out["production_authority"] is False
    assert out["observation_count"]==2
    assert out["observations"][0]["sire"]=="父A"
    assert any(x["going_group"]=="WET" for x in out["sire_cohorts"])
    assert all(x["sample_status"]=="INSUFFICIENT" for x in out["sire_cohorts"])


def _artifact(finishes):
    return {"auxiliary_evidence":{
        "profiles":{"horses":{"1":{"history":[
            {"finish":f,"venue":"大井","distance":1200,"going":"良"} for f in finishes]}}},
        "pedigree_population_seed":{"seeds":[{"runner_id":"1","sire":"父","damsire":"母父"}]}}}


@pytest.mark.parametrize('unknown',[None,0,-1,True,'1','取消'])
def test_unobserved_finish_is_not_a_loss_or_top3(unknown):
    source=_artifact([1,4,unknown]);before=copy.deepcopy(source)
    result=build_population_seed(source)
    assert source==before
    assert result['observation_count']==3
    assert result['known_finish_observation_count']==2
    assert result['unknown_finish_observation_count']==1
    row=result['observations'][-1]
    assert row['win'] is row['top3'] is None and row['finish_observed'] is False
    for kind in ['sire_cohorts','damsire_cohorts']:
        cohort=result[kind][0]
        assert cohort['starts']==2 and cohort['unknown_finish_observations']==1
        assert cohort['win_rate']==cohort['top3_rate']==0.5
    assert result['production_authority'] is False


def test_all_unknown_rates_remain_null_and_do_not_create_twenty_start_sample():
    result=build_population_seed(_artifact([None]*20))
    cohort=result['sire_cohorts'][0]
    assert cohort['starts']==0 and cohort['unknown_finish_observations']==20
    assert cohort['win_rate'] is cohort['top3_rate'] is None
    result=build_population_seed(_artifact([1]*19+[None]))
    assert result['sire_cohorts'][0]['sample_status']=='INSUFFICIENT'


def test_actual_ohi_ten_source_ledgers_are_readonly_and_unknown_rows_are_isolated():
    # Historical diagnostic only; never regenerate or overwrite a signed SOURCE.
    manifest=json.loads((ROOT/'research/common/KM-FAMILY-OHI-20261008-DAY-REGRESSION-R1.json').read_text())
    total_unknown=0
    for record in manifest['verified_result_records']:
        root=ROOT/'runtime/executions'/record['race_id']
        path=sorted(root.glob('SOURCE/runs/*/source_receipt_envelope.json'))[-1]
        original=path.read_bytes();envelope=json.loads(original);source=envelope['artifact']
        before=copy.deepcopy(source)
        candidate=build_population_seed(source)
        assert candidate['profile']!=source['point_in_time_population_ledger']['profile']
        assert candidate['observation_count']==source['point_in_time_population_ledger']['observation_count']
        total_unknown+=candidate['unknown_finish_observation_count']
        assert candidate['production_authority'] is False
        assert source==before and hashlib.sha256(path.read_bytes()).digest()==hashlib.sha256(original).digest()
    assert total_unknown==33

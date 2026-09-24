import sys
from pathlib import Path

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

"""R14 two-owner private real-process transport with a TEST-ONLY fake engine.

The real fixed KRS Engine and parameter_map are *not* checked into this PUBLIC
repository. Real local Engine/Map SHA and seed1 execution are accepted
separately in the user's private execution container; CI stub tests transport.
"""
from __future__ import annotations
from datetime import datetime,timezone
from hashlib import sha256
import json,os
from pathlib import Path
import pytest

from runtime import local_fnb_r14_private_dual_krs as dual
RID="KM-LOCAL-FNB-20261102-R01-LIVE-R1"
UTC=timezone.utc
CUTOFF="2026-11-02T14:40:00+09:00"


def _inputs():
    base={"race_id":RID,"classification":"PRIVATE_NONPRODUCTION_FIXED_OWNER",
          "race":{"date":"2026-11-02","racecourse":"FNB",
                  "race_no":1,"distance_m":1200,"surface":"DIRT","direction":"LEFT"},
          "horses":[{"horse_no":1,"hsv":{"base_competitive_ability":55},
                     "static":{"tpi":50}},
                    {"horse_no":2,"hsv":{"base_competitive_ability":44},
                     "static":{"tpi":50}}]}
    out={}
    for name in dual.OWNERS:
        x=json.loads(json.dumps(base))
        x["owner"]=name
        x["race"]["prediction_id"]=RID+"-"+name
        x["original_prediction_sha256"]=(("a" if name=="BASELINE" else "b")*64)
        x["simulation"]={"run_count":5000,"master_seed":1}
        out[name]=x
    return out


def _fake_engine_fixture(tmp_path,monkeypatch):
    engine=tmp_path/"FAKE_ONLY_NOT_KRS.py"
    code="""import argparse,json
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('source')
p.add_argument('--params')
p.add_argument('--runs',type=int)
p.add_argument('--seed',type=int)
p.add_argument('--output')
a=p.parse_args()
x=json.loads(Path(a.source).read_text())
result={'engine':{'engine_version':'1.1.0','parameter_map_version':'0.1-provisional',
                  'parameter_status':'PROVISIONAL_UNCALIBRATED'},
        'snapshot':{'prediction_id':x['race']['prediction_id'],
                    'run_count':a.runs,'master_seed':a.seed,
                    'race_no':x['race']['race_no'],
                    'field_size':len(x['horses']),
                    'simulation_snapshot_id':'TEST_ONLY-'+x['owner']},
        'summary':[{'horse_no':h['horse_no'],'SSR-W':0.5}
                   for h in x['horses']],
        'warnings':['TEST_ONLY_FAKE_NO_REAL_SIMULATION']}
Path(a.output).write_text(json.dumps(result))
"""
    engine.write_text(code)
    params=tmp_path/"FAKE_PARAMS.json"
    params.write_text('{"test_only":true}')
    monkeypatch.setattr(dual,"ENGINE_SHA",sha256(engine.read_bytes()).hexdigest())
    monkeypatch.setattr(dual,"MAP_SHA",sha256(params.read_bytes()).hexdigest())
    return engine,params


def _execute(tmp_path,engine,params,inputs=None,diagnostic=False):
    return dual.execute(inputs=inputs or _inputs(),engine=engine,params=params,
             private_output=tmp_path/"private",public_repo=Path(__file__).resolve().parents[1],
             race_id=RID,cutoff_at=CUTOFF,
             diagnostic_only=diagnostic,
             now=datetime(2026,11,2,4,0,tzinfo=UTC))


def test_r14_two_separate_inputs_run_once_each_and_private_sha_roundtrip(tmp_path,monkeypatch):
    engine,params=_fake_engine_fixture(tmp_path,monkeypatch)
    output=_execute(tmp_path,engine,params)
    assert output["status"]=="DUAL_OWNER_REAL_LOCAL_ENGINE_EXECUTED_PRIVATE"
    assert output["owner_count"]==2
    assert output["registered_oos_increment"]==0
    assert output["formal_final_or_delivery_verified"] is False
    private=tmp_path/"private"/RID
    assert (private.stat().st_mode & 0o777)==0o700
    report=json.loads((private/"private_dual_krs_receipt.json").read_text())
    assert set(report["owners"])==set(dual.OWNERS)
    assert all(r["actual_krs_runs"]==5000 and r["actual_master_seed"]==1
               for r in report["owners"].values())
    assert all(not r["frozen_owner_sha_claim_independently_signed_verified"]
               for r in report["owners"].values())
    assert all((private/(name+"_krs_input.json")).is_file() and
               (private/(name+"_krs_output.json")).is_file()
               for name in dual.OWNERS)
    assert report["owner_source_sha_independently_frozen_here"] is False


def test_r14_wrong_parameter_map_cannot_simulate(tmp_path):
    engine=tmp_path/"bad_engine.py"; engine.write_text("print('NO')")
    params=tmp_path/"bad.json";params.write_text("{}")
    with pytest.raises(ValueError,match="FNB_KRS_IMMUTABLE_ENGINE_OR_PARAMETER_MAP_SHA_MISMATCH"):
        _execute(tmp_path,engine,params)


def test_r14_missing_candidate_or_duplicate_owner_source_disallowed(tmp_path,monkeypatch):
    engine,params=_fake_engine_fixture(tmp_path,monkeypatch)
    data=_inputs()
    data.pop("CANDIDATE")
    with pytest.raises(ValueError,match="FNB_KRS_BOTH_FIXED_OWNERS_REQUIRED"):
        _execute(tmp_path,engine,params,data)
    data=_inputs()
    data["CANDIDATE"]["original_prediction_sha256"]=data["BASELINE"]["original_prediction_sha256"]
    with pytest.raises(ValueError,match="FNB_KRS_TWO_DISTINCT_FROZEN_OWNER_PREDICTIONS_REQUIRED"):
        _execute(tmp_path,engine,params,data)


def test_r14_cross_universe_and_wrong_owner_input_forbidden(tmp_path,monkeypatch):
    engine,params=_fake_engine_fixture(tmp_path,monkeypatch)
    data=_inputs()
    data["CANDIDATE"]["horses"][1]["horse_no"]=3
    with pytest.raises(ValueError,match="FNB_KRS_OWNERS_DIFFERENT_ACTIVE_UNIVERSES"):
        _execute(tmp_path,engine,params,data)
    data=_inputs()
    data["CANDIDATE"]["owner"]="BASELINE"
    with pytest.raises(ValueError,match="FNB_KRS_WRONG_OWNER_OR_RACE"):
        _execute(tmp_path,engine,params,data)


def test_r14_cutoff_and_public_repo_boundaries_are_not_relaxed(tmp_path,monkeypatch):
    engine,params=_fake_engine_fixture(tmp_path,monkeypatch)
    with pytest.raises(ValueError,match="FNB_KRS_PRESTART_CUTOFF_MISSED"):
        dual.execute(inputs=_inputs(),engine=engine,params=params,
            private_output=tmp_path/"private",public_repo=Path(__file__).resolve().parents[1],
            race_id=RID,cutoff_at=CUTOFF,
            now=datetime(2026,11,2,9,0,tzinfo=UTC))
    with pytest.raises(ValueError,match="FNB_KRS_PRIVATE_OUTPUT_INSIDE_PUBLIC_GIT_REPO"):
        dual.execute(inputs=_inputs(),engine=engine,params=params,
            private_output=Path(__file__).resolve().parents[1]/"test_bad_private",
            public_repo=Path(__file__).resolve().parents[1],
            race_id=RID,cutoff_at=CUTOFF,
            now=datetime(2026,11,2,4,0,tzinfo=UTC))

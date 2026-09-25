from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"/"jra_source_runtime"))
from jra_market_observation import build_market_observation

def test_single_market_observation_never_claims_stability():
    art={"jra_official_race_card_detail_sha256":"D","jra_official_race_card_detail":{"runners":[
      {"runner_id":"1","horse_no":1,"horse_name":"A","win_odds":3.2,"popularity_rank":1},
      {"runner_id":"2","horse_no":2,"horse_name":"B","win_odds":8.1,"popularity_rank":4}
    ]}}
    r=build_market_observation(art)
    assert r["status"]=="PASS"
    assert r["production_fact_authority"] is True
    assert r["stability_authority"] is False
    assert r["observed_runner_count"]==2

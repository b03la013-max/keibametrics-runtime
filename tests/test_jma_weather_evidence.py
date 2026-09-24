import datetime
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"/"local_physical"))

from jma_weather_evidence import PROFILE, choose_nearest_station, _candidate_times


def test_choose_nearest_station():
    stations={
      "A":{"type":"A","lat":[35,50.0],"lon":[139,40.0],"alt":10,"kjName":"近い"},
      "B":{"type":"A","lat":[34,0.0],"lon":[135,0.0],"alt":5,"kjName":"遠い"},
    }
    out=choose_nearest_station(stations,"URW")
    assert out["station_id"]=="A"
    assert out["distance_km"] < 20


def test_candidate_times_are_ten_minute_jst():
    xs=_candidate_times("2099-01-01T00:00:00+00:00")
    assert len(xs)==13
    assert all(x.utcoffset()==datetime.timedelta(hours=9) for x in xs)
    assert all(x.minute % 10 == 0 for x in xs)
    assert all((xs[i]-xs[i+1]).total_seconds()==600 for i in range(len(xs)-1))


def test_profile_is_shadow_only():
    assert PROFILE=="KM-LOCAL-JMA-WEATHER-EVIDENCE-v1.0-20260924"

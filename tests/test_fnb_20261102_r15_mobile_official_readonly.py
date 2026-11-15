"""R15 alternative official mobile GET preserves default robots/ACL, no bypass."""
from datetime import datetime,timezone
from runtime.local_fnb_r15_mobile_official_readonly import spec,probe
import pytest

def test_r15_source_is_only_original_nar_official_mobile_url():
    url=spec(2)["url"]
    assert url.startswith("https://sp.keiba.go.jp/KeibaWebSP/TodayRaceInfo/S_DebaTable?")
    assert "k_babaCode=19" in url and "k_raceNo=2" in url
    assert spec(2)["official"] is True
    assert spec(2)["source_class"]=="OFFICIAL_MOBILE_CARD_RESEARCH_ONLY"

def test_r15_blocked_request_no_live_flag_and_no_public_raw():
    def fail(s,cutoff):
        raise ValueError("SOURCE_POLICY_ROBOTS_DISALLOWED")
    result=probe(2,fetch=fail,now=datetime(2026,11,2,5,30,tzinfo=timezone.utc))
    assert result["status"]=="NAR_MOBILE_OBSERVATION_HOLD"
    assert result["source_error_code"]=="SOURCE_POLICY_ROBOTS_DISALLOWED"
    assert result["robots_bypass"] is False
    assert result["production_source_registry_changed"] is False
    assert result["raw_exported_to_public_github"] is False

def test_r15_no_counterfeit_success_on_mismatched_body():
    def empty(s,cutoff):
        return {"http_status":200,"extracted_evidence":{"html_text":"not a card"}},[]
    result=probe(2,fetch=empty)
    assert result["status"]=="NAR_MOBILE_OBSERVATION_HOLD"
    assert result["signed_source_verified"] is False

@pytest.mark.parametrize("value",[0,13,True,"2"])
def test_r15_invalid_race_number_hold(value):
    with pytest.raises(ValueError):
        spec(value)

"""R14 verifies live source diagnostic cannot invent a signed prestart source."""
from datetime import datetime,timezone
from runtime.local_fnb_r14_live_source_probe import probe_one,_card_spec
import pytest

def test_r14_exact_official_11_02_race_card_spec():
    card=_card_spec(1)
    assert card["source_id"]=="NAR-FNB-20261102-R01-RACE-CARD"
    assert card["url"].startswith("https://www.keiba.go.jp/")
    assert card["source_class"]=="OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT"
    assert card["required"] is True

def test_r14_official_fetch_error_does_not_become_no_changes_or_signed_source():
    def fetched(spec,cutoff):
        return {"http_status":200},["EXTRACT_REQUIRED_FAILED:race_card_tables"]
    grade=probe_one(1,fetch=fetched,now=datetime(2026,11,2,5,30,tzinfo=timezone.utc))
    assert grade["status"]=="OFFICIAL_LIVE_SOURCE_FETCH_HOLD"
    assert grade["race_no"]==1
    assert grade["raw_published"] is False
    assert grade["signed_source"] is False

def test_r14_official_dns_error_redacted_and_no_dynamic_source_approval():
    def bad(spec,cutoff):
        raise ValueError("SOURCE_DNS_RESOLUTION_FAILED:private-example.invalid")
    grade=probe_one(1,fetch=bad)
    assert grade["status"]=="OFFICIAL_LIVE_SOURCE_FETCH_HOLD"
    assert grade["failure_code"]=="SOURCE_DNS_RESOLUTION_FAILED"
    assert "private-example.invalid" not in str(grade)
    assert grade["signed_source"] is False

@pytest.mark.parametrize("bad_no",[0,13,True,"1"])
def test_r14_race_number_must_be_exact_int(bad_no):
    with pytest.raises(ValueError,match="R14_RACE_NUMBER_1_TO_12_REQUIRED"):
        probe_one(bad_no)

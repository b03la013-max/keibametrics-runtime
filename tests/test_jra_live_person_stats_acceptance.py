from datetime import datetime
import sys
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime/jra_source_runtime'),str(ROOT/'tools')]
from jra_live_person_stats_acceptance import select_current_card


def test_current_card_selection_never_reuses_a_retired_historical_date():
    seen=[]
    def meetings(day):
        seen.append(day)
        return ['東京'] if day=='2026-10-18' else []
    out=select_current_card(datetime.fromisoformat('2026-10-17T00:00:00+09:00'),meetings=meetings,
                            resolve=lambda day,venue:('0520260407',[{'race_no':1,'field_size':13}]))
    assert out[:3]==('2026-10-18','東京','0520260407')
    assert seen==['2026-10-17','2026-10-18']


def test_current_card_unavailable_is_bounded_and_not_a_false_pass():
    calls=[]
    def meetings(day):calls.append(day);return []
    with pytest.raises(ValueError,match='CURRENT_CARD_UNAVAILABLE'):
        select_current_card(datetime.fromisoformat('2026-10-17T00:00:00+09:00'),meetings=meetings)
    assert len(calls)==8 and min(calls)=='2026-10-17'

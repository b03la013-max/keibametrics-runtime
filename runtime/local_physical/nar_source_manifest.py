from __future__ import annotations

import datetime
import urllib.parse
from typing import Any, Dict, List

PROFILE = "KM-LOCAL-NAR-SOURCE-MANIFEST-v1.0-20260923"

# NAR racecourse codes used by KeibaWeb (same two-digit family as the published
# local-racing telephone betting codes). Keep LOCAL and BAN ownership separate.
LOCAL_BABA_CODES = {
    "MOR": "10",  # 盛岡
    "MIZ": "11",  # 水沢
    "URW": "18",  # 浦和
    "FNB": "19",  # 船橋
    "OHI": "20",  # 大井
    "KAW": "21",  # 川崎
    "KNZ": "22",  # 金沢
    "KSM": "23",  # 笠松
    "NGY": "24",  # 名古屋
    "SON": "27",  # 園田
    "HIM": "28",  # 姫路
    "KCH": "31",  # 高知
    "SAG": "32",  # 佐賀
    "MON": "36",  # 門別
}

VENUE_NAMES = {
    "MOR":"盛岡","MIZ":"水沢","URW":"浦和","FNB":"船橋","OHI":"大井","KAW":"川崎",
    "KNZ":"金沢","KSM":"笠松","NGY":"名古屋","SON":"園田","HIM":"姫路","KCH":"高知",
    "SAG":"佐賀","MON":"門別",
}


def _date(v: Any) -> str:
    s = str(v or "").strip().replace("/", "-")
    try:
        d = datetime.date.fromisoformat(s)
    except Exception as e:
        raise ValueError("NAR_RACE_DATE_INVALID") from e
    return d.strftime("%Y/%m/%d")


def _race_no(v: Any) -> int:
    try:
        n = int(v)
    except Exception as e:
        raise ValueError("NAR_RACE_NO_INVALID") from e
    if n < 1 or n > 12:
        raise ValueError("NAR_RACE_NO_OUT_OF_RANGE")
    return n


def _url(page: str, baba: str, race_date: str, race_no: int) -> str:
    q = urllib.parse.urlencode({
        "k_babaCode": baba,
        "k_raceDate": race_date,
        "k_raceNo": race_no,
    })
    return f"https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/{page}?{q}"


def _race_card_source(venue_id: str, baba: str, race_date: str, race_no: int) -> Dict[str, Any]:
    return {
        "source_id": f"NAR-{venue_id}-{race_date.replace('/','')}-R{race_no:02d}-RACE-CARD",
        "source_class": "OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT",
        "authority": "NAR_OFFICIAL",
        "priority": 100,
        "official": True,
        "required": True,
        "url": _url("DebaTable", baba, race_date, race_no),
        "max_bytes": 900000,
        "extract": [
            {"field":"race_card_tables","type":"html_tables","required":True},
            {"field":"weather","type":"regex","scope":"html_text","pattern":r"天候[:：]\s*([^\s]+)","group":1,"cast":"str","required":False},
            {"field":"track_condition","type":"regex","scope":"html_text","pattern":r"馬場[:：]\s*([^\s]+)","group":1,"cast":"str","required":False},
            {"field":"start_time","type":"regex","scope":"html_text","pattern":r"(\d{1,2}:\d{2})\s*発走","group":1,"cast":"str","required":False},
        ],
    }


def _odds_source(venue_id: str, baba: str, race_date: str, race_no: int, required: bool=False) -> Dict[str, Any]:
    return {
        "source_id": f"NAR-{venue_id}-{race_date.replace('/','')}-R{race_no:02d}-ODDS-TANFUKU",
        "source_class": "OFFICIAL_ACTIVE_BETTING_UNIVERSE",
        "authority": "NAR_OFFICIAL",
        "priority": 100,
        "official": True,
        "required": bool(required),
        "url": _url("OddsTanFuku", baba, race_date, race_no),
        "max_bytes": 600000,
        "extract": [
            {"field":"odds_tables","type":"html_tables","required":False},
        ],
    }


def _result_source(venue_id: str, baba: str, race_date: str, race_no: int) -> Dict[str, Any]:
    scope = f"same_day_r{race_no:02d}"
    return {
        "source_id": f"NAR-{venue_id}-{race_date.replace('/','')}-R{race_no:02d}-RESULT",
        "source_class": "OFFICIAL_SAME_DAY_RACE_RESULT_PASSING_ORDER",
        "authority": "NAR_OFFICIAL",
        "priority": 100,
        "official": True,
        "required": False,
        "url": _url("RaceMarkTable", baba, race_date, race_no),
        "max_bytes": 750000,
        "extract": [
            {"field":f"{scope}_result_tables","type":"html_tables","required":False},
            {"field":f"{scope}_weather","type":"regex","scope":"html_text","pattern":r"天候[:：]\s*([^\s]+)","group":1,"cast":"str","required":False},
            {"field":f"{scope}_track_condition","type":"regex","scope":"html_text","pattern":r"馬場[:：]\s*([^\s]+)","group":1,"cast":"str","required":False},
        ],
    }


def build_local_nar_manifest(payload: Dict[str, Any]) -> Dict[str, Any]:
    race = payload.get("race") if isinstance(payload.get("race"), dict) else {}
    venue_id = str(payload.get("venue_id") or race.get("venue_id") or "").upper().strip()
    if venue_id not in LOCAL_BABA_CODES:
        raise ValueError("LOCAL_NAR_VENUE_ID_UNSUPPORTED:" + venue_id)
    race_date = _date(payload.get("race_date") or race.get("race_date") or race.get("date"))
    race_no = _race_no(payload.get("race_no") or race.get("race_no"))
    race_id = str(payload.get("race_id") or race.get("race_id") or f"{venue_id}-{race_date.replace('/','')}-R{race_no:02d}")
    cutoff = str(payload.get("prediction_cutoff") or race.get("prediction_cutoff") or "").strip()
    if not cutoff:
        raise ValueError("PREDICTION_CUTOFF_REQUIRED")

    baba = LOCAL_BABA_CODES[venue_id]
    sources: List[Dict[str, Any]] = [_race_card_source(venue_id, baba, race_date, race_no)]

    require_active=bool(payload.get("require_active_runner_universe", False))
    include_odds=bool(payload.get("include_odds", False)) or require_active
    if include_odds:
        sources.append(_odds_source(venue_id, baba, race_date, race_no, required=require_active))

    if bool(payload.get("include_same_day_results", True)):
        start = max(1, int(payload.get("same_day_result_start_race") or 1))
        for n in range(start, race_no):
            sources.append(_result_source(venue_id, baba, race_date, n))

    return {
        "manifest_profile": PROFILE,
        "family_id": "LOCAL",
        "race_id": race_id,
        "venue_id": venue_id,
        "venue_name": VENUE_NAMES[venue_id],
        "nar_baba_code": baba,
        "race_date": race_date,
        "race_no": race_no,
        "prediction_cutoff": cutoff,
        "sources": sources,
        "source_policy": {
            "race_card_required": True,
            "same_day_results": "OPTIONAL_AVAILABLE_PREVIOUS_RACES",
            "odds": "REQUIRED_FOR_ACTIVE_RUNNER_UNIVERSE" if require_active else "OPTIONAL_UNLESS_REQUESTED_BY_CALLER",
            "runner_universe_model": "DECLARED_RACE_CARD_PLUS_ACTIVE_OFFICIAL_BETTING_UNIVERSE",
            "body_weight_and_change_info": "CAPTURED_IN_RACE_CARD_RAW_AND_TABLES",
            "track_weather_current_state": "CAPTURED_FROM_RACE_CARD_WHEN_PUBLISHED",
        },
    }

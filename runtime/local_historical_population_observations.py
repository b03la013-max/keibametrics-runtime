"""Offline NAR history observations for private unadopted research.

Consumes actual saved HorseMarkInfo bytes, preserving the official per-row
RaceMarkTable identity which the legacy table-only parser drops. This is not
Provider admission, a complete population, a permanent parent/person join,
or a score/model producer. No network or Production registry is used.
"""
from __future__ import annotations

import base64
from datetime import date, datetime, timedelta, timezone
import gzip
import hashlib
from html.parser import HTMLParser
import json
import re
import unicodedata
from urllib.parse import parse_qs, urljoin, urlsplit

PROFILE = "KM-LOCAL-HISTORICAL-POPULATION-OBSERVATIONS-RESEARCH-v0.1-20261103"
CLASSIFICATION = "PRIVATE_RESEARCH_UNADOPTED_NOT_OOS_NOT_PRODUCTION"
# Existing LOCAL official manifest identity table; no predictive rule or
# cross-family mapping. Unknown/retired codes remain explicitly unverified.
VENUE_NAMES_BY_CODE = {10:"盛岡",11:"水沢",18:"浦和",19:"船橋",20:"大井",21:"川崎",
    22:"金沢",23:"笠松",24:"名古屋",27:"園田",28:"姫路",31:"高知",32:"佐賀",36:"門別"}
VENUE_MAP_ORIGIN = "runtime/local_physical/nar_source_manifest.py:LOCAL_BABA_CODES+VENUE_NAMES"


def _aware(value):
    result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("POPULATION_AWARE_TIME_REQUIRED")
    return result


def _one(query, name):
    values = query.get(name) or []
    if len(values) != 1 or not values[0]:
        raise ValueError("POPULATION_OFFICIAL_IDENTITY_AMBIGUOUS:" + name)
    return values[0]


def _nar_url(value, path):
    parsed = urlsplit(value)
    if (parsed.scheme != "https" or parsed.hostname not in {"www.keiba.go.jp", "keiba.go.jp"}
            or parsed.username or parsed.password or parsed.port not in (None, 443)
            or parsed.path != path):
        raise ValueError("POPULATION_OFFICIAL_URL_SCOPE_MISMATCH")
    return parse_qs(parsed.query)


class _HistoryRows(HTMLParser):
    """Keep the cell text and links from the same printed row."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows = []
        self.cells = None
        self.text = None
        self.links = None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.cells, self.links = [], []
        elif tag in {"td", "th"} and self.cells is not None:
            self.text = []
        elif tag == "a" and self.cells is not None:
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)

    def handle_data(self, data):
        if self.text is not None:
            self.text.append(data)

    def handle_endtag(self, tag):
        if tag in {"td", "th"} and self.text is not None:
            self.cells.append(re.sub(r"\s+", " ", "".join(self.text)).strip())
            self.text = None
        elif tag == "tr" and self.cells is not None:
            self.rows.append((self.cells, self.links))
            self.cells = self.links = self.text = None


def _integer(text):
    normalized = str(text).replace(",", "").strip()
    return int(normalized) if re.fullmatch(r"[0-9]+", normalized) else None


def extract_horse_history(snapshot, *, as_of, target_race_date=None):
    """Extract byte-bound observations without changing their qualification.

    ``as_of`` is a real research cutoff. Historical replay callers must pass
    the original freeze, not today's date. Same-day target/future rows are
    excluded when target_race_date is supplied. Source/Provider permission
    and envelope cryptographic verification remain separate caller duties.
    """
    freeze = _aware(as_of)
    fetched = _aware(snapshot["fetched_at"])
    if fetched >= freeze:
        raise ValueError("POPULATION_SOURCE_AT_OR_AFTER_ASOF")
    if (snapshot.get("official") is not True or snapshot.get("authority") != "NAR_OFFICIAL"
            or snapshot.get("source_class") != "OFFICIAL_HORSE_HISTORY_PROFILE"
            or snapshot.get("http_status") != 200):
        raise ValueError("POPULATION_OFFICIAL_HISTORY_SNAPSHOT_REQUIRED")
    requested = _nar_url(snapshot["requested_url"], "/KeibaWeb/DataRoom/HorseMarkInfo")
    final = _nar_url(snapshot["final_url"], "/KeibaWeb/DataRoom/HorseMarkInfo")
    horse = _one(requested, "k_lineageLoginCode")
    if not re.fullmatch(r"[0-9]+", horse) or _one(final, "k_lineageLoginCode") != horse:
        raise ValueError("POPULATION_PERMANENT_HORSE_IDENTITY_MISMATCH")
    raw = gzip.decompress(base64.b64decode(snapshot["raw_gzip_b64"], validate=True))
    digest = hashlib.sha256(raw).hexdigest()
    if digest != snapshot.get("raw_sha256") or len(raw) != snapshot.get("byte_count"):
        raise ValueError("POPULATION_RAW_HASH_OR_SIZE_MISMATCH")
    match = re.search(r"charset\s*=\s*([A-Za-z0-9_-]+)", snapshot.get("content_type", ""), re.I)
    if not match:
        raise ValueError("POPULATION_EXPLICIT_CHARSET_REQUIRED")
    parser = _HistoryRows()
    parser.feed(raw.decode(match.group(1), errors="strict"))
    target = str(target_race_date or "").replace("-", "/")
    if target:
        date.fromisoformat(target.replace("/", "-"))
    records, excluded, missing_links = [], 0, 0
    for row_no, (cells, links) in enumerate(parser.rows):
        if len(cells) < 23 or not re.fullmatch(r"\d{4}/\d{2}/\d{2}", cells[0]):
            continue
        try:
            date.fromisoformat(cells[0].replace("/", "-"))
        except ValueError as exc:
            raise ValueError("POPULATION_PRINTED_EVENT_DATE_INVALID") from exc
        # A dated result cannot be observable before its date. Intraday event
        # time is absent: never invent midnight as the actual result time.
        if cells[0] > fetched.astimezone(timezone(timedelta(hours=9))).date().strftime("%Y/%m/%d") or (target and cells[0] >= target):
            excluded += 1
            continue
        official_links = []
        for href in links:
            url = urljoin(snapshot["final_url"], href)
            if urlsplit(url).path != "/KeibaWeb/TodayRaceInfo/RaceMarkTable":
                continue
            query = _nar_url(url, "/KeibaWeb/TodayRaceInfo/RaceMarkTable")
            day = _one(query, "k_raceDate")
            race = _one(query, "k_raceNo")
            venue = _one(query, "k_babaCode")
            if day != cells[0] or _integer(race) != _integer(cells[2]) or not re.fullmatch(r"[0-9]+", venue):
                raise ValueError("POPULATION_PRINTED_ROW_OFFICIAL_RACE_LINK_CONFLICT")
            official_links.append((day, int(venue), int(race), url))
        identities = {(d, v, n) for d, v, n, _ in official_links}
        if not identities:
            missing_links += 1
            continue
        if len(identities) != 1:
            raise ValueError("POPULATION_MULTIPLE_RACE_IDENTITIES_IN_ROW")
        day, venue, number = next(iter(identities))
        if not 1 <= number <= 12:
            raise ValueError("POPULATION_OFFICIAL_RACE_NUMBER_OUT_OF_RANGE")
        known_venue = VENUE_NAMES_BY_CODE.get(venue)
        printed_venue = re.sub(r"\s+", "", unicodedata.normalize("NFKC", cells[1]))
        if known_venue is not None and printed_venue != known_venue:
            raise ValueError("POPULATION_PRINTED_ROW_OFFICIAL_VENUE_CONFLICT")
        field, finish = _integer(cells[9]), _integer(cells[13])
        if field is None or field < 1 or finish is None or not 1 <= finish <= field:
            # Cancelled/withdrawn/abnormal result text is not a rank number.
            excluded += 1
            continue
        distance = re.fullmatch(r"(芝|ダート|ダ|直)?\s*(\d+)", cells[5])
        explicit_surface = ({"芝": "TURF", "ダ": "DIRT", "ダート": "DIRT"}.get(distance.group(1))
                            if distance else None)
        records.append({
            "horse_id": "NAR:" + horse,
            "race_id": f"NAR:{day.replace('/', '')}:{venue:02d}:R{number:02d}",
            "official_race_url": official_links[0][3],
            "identity_method": "OFFICIAL_ROW_LINK_DATE_VENUE_RACENO_NOT_NAME_JOIN",
            "event_date": day, "event_at": None,
            "event_time_limit": "date-only result history; intraday event timestamp absent",
            "venue_code": venue, "venue_label": cells[1], "race_no": number,
            "printed_venue_identity_status": "VERIFIED_EXISTING_LOCAL_MAP" if known_venue else "UNKNOWN_CODE_NOT_IN_EXISTING_LOCAL_MAP",
            "venue_map_origin": VENUE_MAP_ORIGIN,
            "race_name": cells[3], "class_label": cells[4],
            "distance_display": cells[5],
            "distance_m": int(distance.group(2)) if distance else None,
            "weather": cells[6], "going": cells[7],
            "field_size": field, "horse_no": _integer(cells[11]), "finish": finish,
            "body_weight_kg": _integer(cells[17]),
            "jockey_label": cells[18], "jockey_id": None,
            "trainer_label": cells[20], "stable_id": None,
            "surface": explicit_surface, "sand_era": None,
            "sire_id": None, "damsire_id": None, "parent_id": None,
            "source_id": snapshot.get("source_id"), "source_raw_sha256": digest,
            "source_snapshot_sha256": snapshot.get("snapshot_sha256"),
            "source_fetched_at": snapshot["fetched_at"],
            "field_provenance": {"row_ordinal": row_no, "identity": "same-row official link",
                "printed_cells": {k: i for k, i in [("date", 0), ("venue", 1), ("race_no", 2),
                  ("class_label", 4), ("distance_m", 5), ("going", 7), ("field_size", 9),
                  ("finish", 13), ("body_weight_kg", 17), ("jockey_label", 18), ("trainer_label", 20)]}},
            "qualification": "BYTE_VERIFIED_ARCHIVED_OBSERVATION_NOT_PROVIDER_ADMISSION",
        })
    result = {"profile": PROFILE, "classification": CLASSIFICATION,
        "source_raw_sha256": digest, "as_of": as_of, "horse_id": "NAR:" + horse,
        "records": records, "excluded_rows": excluded, "rows_without_official_race_link": missing_links,
        "comparison_population_complete": False, "production_authority": False,
        "permanent_parent_identity_inferred": False, "person_identity_inferred": False,
        "new_raw_acquisition": False, "score_generated": False,
        "limitations": ["current-field selected horse histories, not a complete sampling frame",
            "printed names do not establish permanent historical jockey/stable/parent IDs",
            "date-only result rows do not establish intraday event_at",
            "historical weight is not current target bodyweight",
            "no Provider permission or SOURCE signature issued by this extractor"]}
    result["sha256"] = hashlib.sha256(json.dumps(result, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    return result

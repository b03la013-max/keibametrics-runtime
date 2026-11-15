"""Offline, byte-bound identities from saved official LOCAL result rows.

The HorseMarkInfo history table omits person identity links.  A saved
RaceMarkTable retains horse, jockey and trainer links in each result row.
This extractor recovers those observed identities, never joins printed names
and never grants Provider admission, a complete comparison frame, or a score.
"""
from __future__ import annotations

import base64
from datetime import date, datetime, timedelta, timezone
import gzip
import hashlib
import html
from html.parser import HTMLParser
import json
import re
import unicodedata
from urllib.parse import parse_qs, urljoin, urlsplit

from runtime.local_historical_population_observations import VENUE_NAMES_BY_CODE

PROFILE = "KM-LOCAL-RESULT-ROW-IDENTITY-OBSERVATIONS-RESEARCH-v0.1-20261103"
CLASSIFICATION = "PRIVATE_RESEARCH_UNADOPTED_NOT_OOS_NOT_PRODUCTION"
RESULT_PATH = "/KeibaWeb/TodayRaceInfo/RaceMarkTable"
IDENTITIES = {
    "horse_id": (3, "/KeibaWeb/DataRoom/HorseMarkInfo", "k_lineageLoginCode"),
    "jockey_id": (7, "/KeibaWeb/DataRoom/RiderMark", "k_riderLicenseNo"),
    "trainer_id": (8, "/KeibaWeb/DataRoom/TrainerMark", "k_trainerLicenseNo"),
}


def _aware(value):
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("IDENTITY_AWARE_TIMESTAMP_REQUIRED")
    return parsed


def _query(url, path):
    p = urlsplit(url)
    if (p.scheme != "https" or p.hostname not in {"www.keiba.go.jp", "keiba.go.jp"}
            or p.username or p.password or p.port not in (None, 443) or p.path != path):
        raise ValueError("IDENTITY_OFFICIAL_URL_SCOPE_MISMATCH")
    return parse_qs(p.query)


def _one(query, field):
    values = query.get(field, [])
    if len(values) != 1 or not values[0]:
        raise ValueError("IDENTITY_OFFICIAL_PARAMETER_AMBIGUOUS:" + field)
    return values[0]


class _Rows(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows = []
        self.cells = self.cell = None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.cells = []
        elif tag in {"td", "th"} and self.cells is not None:
            self.cell = {"text": [], "links": []}
        elif tag == "a" and self.cell is not None:
            href = dict(attrs).get("href")
            if href:
                self.cell["links"].append(href)

    def handle_data(self, text):
        if self.cell is not None:
            self.cell["text"].append(text)

    def handle_endtag(self, tag):
        if tag in {"td", "th"} and self.cell is not None:
            self.cell["text"] = re.sub(r"\s+", " ", "".join(self.cell["text"])).strip()
            self.cells.append(self.cell)
            self.cell = None
        elif tag == "tr" and self.cells is not None:
            self.rows.append(self.cells)
            self.cells = self.cell = None


def _identity(cell, base_url, path, parameter):
    found, links = set(), []
    for href in cell["links"]:
        url = urljoin(base_url, href)
        if urlsplit(url).path != path:
            continue
        raw_id = _one(_query(url, path), parameter)
        if not re.fullmatch(r"[0-9]+", raw_id):
            raise ValueError("IDENTITY_OFFICIAL_ID_NOT_NUMERIC")
        found.add(raw_id)
        links.append(url)
    if len(found) > 1:
        raise ValueError("IDENTITY_MULTIPLE_IDS_IN_SAME_CELL")
    return ("NAR:" + next(iter(found)), links[0]) if found else (None, None)


def extract_result_row_identities(snapshot, *, as_of, target_race_date=None):
    """Recover explicit row identities without inventing event times/parents.

    ``as_of`` is the future research decision time. Observations fetched at or
    after that point fail closed. A date-only race date is retained as such;
    an actual event_at is never synthesized from midnight or scheduled post.
    """
    cutoff, fetched = _aware(as_of), _aware(snapshot["fetched_at"])
    if fetched >= cutoff:
        raise ValueError("IDENTITY_SOURCE_AT_OR_AFTER_ASOF")
    if (snapshot.get("official") is not True or snapshot.get("authority") != "NAR_OFFICIAL"
            or snapshot.get("http_status") != 200):
        raise ValueError("IDENTITY_OFFICIAL_HTTP200_SNAPSHOT_REQUIRED")
    identities = []
    for name in ("requested_url", "final_url"):
        q = _query(snapshot[name], RESULT_PATH)
        day = _one(q, "k_raceDate").replace("/", "-")
        date.fromisoformat(day)
        venue, race = _one(q, "k_babaCode"), _one(q, "k_raceNo")
        if not venue.isdigit() or not race.isdigit() or not 1 <= int(race) <= 12:
            raise ValueError("IDENTITY_RACE_PARAMETERS_INVALID")
        identities.append((day, int(venue), int(race)))
    if identities[0] != identities[1]:
        raise ValueError("IDENTITY_RESULT_REDIRECT_RACE_MISMATCH")
    day, venue, number = identities[0]
    if day > fetched.astimezone(timezone(timedelta(hours=9))).date().isoformat():
        raise ValueError("IDENTITY_RESULT_EVENT_DATE_AFTER_CAPTURE")
    if target_race_date and day >= date.fromisoformat(str(target_race_date)).isoformat():
        raise ValueError("IDENTITY_SAME_OR_AFTER_TARGET_DATE")
    raw = gzip.decompress(base64.b64decode(snapshot["raw_gzip_b64"], validate=True))
    digest = hashlib.sha256(raw).hexdigest()
    if digest != snapshot.get("raw_sha256") or len(raw) != snapshot.get("byte_count"):
        raise ValueError("IDENTITY_RAW_HASH_OR_SIZE_MISMATCH")
    encoding = re.search(r"charset\s*=\s*([A-Za-z0-9_-]+)", snapshot.get("content_type", ""), re.I)
    if not encoding:
        raise ValueError("IDENTITY_EXPLICIT_CHARSET_REQUIRED")
    text = raw.decode(encoding.group(1), errors="strict")
    if "ご指定のレース成績の情報がありません" in text:
        raise ValueError("IDENTITY_RESULT_INFORMATION_NOT_AVAILABLE")
    headings = [html.unescape(re.sub(r"<[^>]+>", "", h))
                for h in re.findall(r"<h4\b[^>]*>(.*?)</h4>", text, re.S | re.I)]
    printed = []
    for heading in headings:
        h = re.sub(r"\s+", "", unicodedata.normalize("NFKC", heading))
        match = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日.*?([一-龯]+)第(\d+)競走", h)
        if match:
            printed.append((date(int(match[1]), int(match[2]), int(match[3])).isoformat(), match[4], int(match[5])))
    if printed != [(day, VENUE_NAMES_BY_CODE.get(venue), number)]:
        raise ValueError("IDENTITY_PRINTED_RACE_HEADER_URL_CONFLICT")
    def clean(value):
        return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", value))).strip()
    titles = re.findall(r'<section\b[^>]*class=["\']raceTitle["\'][^>]*>(.*?)</section>', text, re.S | re.I)
    race_name = distance_m = surface = going = None
    if len(titles) == 1:
        title = re.search(r"<h3\b[^>]*>(.*?)</h3>", titles[0], re.S | re.I)
        race_name = clean(title[1]) if title else None
        conditions = clean(titles[0])
        distance = re.search(r"(ダート|芝)\s*([0-9]+)[ｍm]", unicodedata.normalize("NFKC", conditions))
        if distance:
            surface = {"ダート": "DIRT", "芝": "TURF"}[distance[1]]
            distance_m = int(distance[2])
        g = re.search(r"馬場[：:]\s*(不良|稍重|良|重)", conditions)
        going = g[1] if g else None
    parsed = _Rows()
    parsed.feed(text)
    headers = [i for i, cells in enumerate(parsed.rows) if len(cells) in (15, 16) and
               [c["text"].replace(" ", "") for c in cells[:4]] == ["着順", "枠", "馬番", "馬名"]]
    if len(headers) != 1:
        raise ValueError("IDENTITY_UNIQUE_OFFICIAL_RESULT_TABLE_REQUIRED")
    expected_columns = len(parsed.rows[headers[0]])
    result_rows = []
    for ordinal, cells in enumerate(parsed.rows[headers[0] + 1:], headers[0] + 1):
        if len(cells) != expected_columns or not re.fullmatch(r"[0-9]+", cells[2]["text"]):
            break
        result_rows.append((ordinal, cells))
    if not result_rows:
        raise ValueError("IDENTITY_NO_RESULT_ROWS")
    seen, records = set(), []
    for ordinal, cells in result_rows:
        horse_no = int(cells[2]["text"])
        if horse_no < 1 or horse_no in seen:
            raise ValueError("IDENTITY_DUPLICATE_OR_INVALID_HORSE_NUMBER")
        seen.add(horse_no)
        row = {"race_id": f"NAR:{day.replace('-', '')}:{venue:02d}:R{number:02d}",
               "event_date": day, "event_at": None, "venue_code": venue, "race_no": number,
               "race_name": race_name, "class": None, "class_label_raw": race_name,
               "distance_m": distance_m, "surface": surface, "going": going,
               "horse_no": horse_no, "horse_label": cells[3]["text"],
               "jockey_label": cells[7]["text"], "stable_label": cells[8]["text"],
               "stable_id": None,
               "trainer_identity_semantics": "OFFICIAL_TRAINER_LICENSE_NOT_SEPARATELY_VERIFIED_STABLE_ORGANIZATION",
               "finish_display": cells[0]["text"],
               "finish": int(cells[0]["text"]) if cells[0]["text"].isdigit() else None,
               "source_raw_sha256": digest, "source_fetched_at": snapshot["fetched_at"],
               "source_id": snapshot.get("source_id"), "field_size": None,
               "sire_id": None, "damsire_id": None,
               "qualification": "BYTE_VERIFIED_ARCHIVED_OFFICIAL_ROW_NOT_PROVIDER_ADMISSION",
               "field_provenance": {"row_ordinal": ordinal, "identity_links": {}}}
        for field, (column, path, parameter) in IDENTITIES.items():
            row[field], link = _identity(cells[column], snapshot["final_url"], path, parameter)
            row["field_provenance"]["identity_links"][field] = {"column": column, "url": link}
        weight = re.fullmatch(r"([0-9]+)\(([+-]?[0-9]+)\)", cells[9]["text"])
        row["body_weight_kg"] = int(weight.group(1)) if weight else None
        row["body_weight_delta_kg"] = int(weight.group(2)) if weight else None
        row["carried_weight_kg"] = float(cells[6]["text"]) if re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", cells[6]["text"]) else None
        records.append(row)
    complete = all(all(r.get(k) for k in IDENTITIES) for r in records)
    out = {"profile": PROFILE, "classification": CLASSIFICATION, "race_id": records[0]["race_id"],
           "as_of": as_of, "source_raw_sha256": digest, "records": records,
           "result_row_count": len(records), "all_printed_row_identities_recovered": complete,
           "field_size_not_inferred_from_rows": True, "whole_population_complete": False,
           "actual_event_at_available": False, "new_raw_acquisition": False,
           "production_admission": False, "score_generated": False,
           "future_pre_asof_capture": True}
    out["sha256"] = hashlib.sha256(json.dumps(out, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()).hexdigest()
    return out

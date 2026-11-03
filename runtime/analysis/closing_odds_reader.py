"""Pure, fail-closed reader for unsigned OFFLINE JRA closing-price captures.

No network or Production imports. A post-race capture timestamp, popularity,
or a winner's payout does not establish an all-runner closing-price table.
"""
from __future__ import annotations

import base64
import hashlib
import json
import math
import os
import re
import tempfile
import unicodedata
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

SCHEMA = "JRA_CLOSING_ODDS_RESEARCH_V1"
RACE = re.compile(r"KM-JRA-([A-Z]{3})-(\d{4})(\d{2})(\d{2})-R(\d{2})")
VENUES = {"SAP":"札幌", "HKD":"函館", "FKS":"福島", "NGT":"新潟", "TKY":"東京",
          "NKY":"中山", "CKY":"中京", "KYO":"京都", "HSN":"阪神", "KOK":"小倉"}
NONSTARTERS = {"取消":"CANCELLED", "除外":"EXCLUDED"}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def norm(value):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", value)).strip()


def timestamp(value):
    result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("CAPTURE_TIMEZONE_REQUIRED")
    return result


def identity(race_id):
    match = RACE.fullmatch(race_id)
    if not match or match[1] not in VENUES or not 1 <= int(match[5]) <= 12:
        raise ValueError("JRA_RACE_ID_INVALID")
    datetime(int(match[2]), int(match[3]), int(match[4]))
    return match


def official_url(url):
    parsed = urlparse(url)
    if (parsed.scheme != "https" or parsed.netloc != "www.jra.go.jp" or
            parsed.path not in {"/JRADB/accessD.html", "/JRADB/accessS.html", "/JRADB/accessO.html"}):
        raise ValueError("CLOSING_SOURCE_URL_NOT_OFFICIAL")
    return url


class Tables(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text, self.tables, self.table, self.row, self.cell = [], [], None, None, None
        self.suppressed = 0
        self.nested = 0
        self.headings, self.heading = [], None
        self.link_depth = self.nav_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.suppressed += 1
        if self.suppressed:
            return
        if tag == "a":
            self.link_depth += 1
        if tag == "nav":
            self.nav_depth += 1
        if tag in {"h1", "h2", "h3", "h4", "caption", "title"}:
            self.heading = []
        if tag == "table":
            if self.table is not None:
                self.nested += 1
            else:
                self.table = []
        elif tag == "tr" and self.table is not None:
            self.row = []
        elif tag in {"td", "th"} and self.row is not None:
            self.cell = []
        elif tag == "br" and self.cell is not None:
            self.cell.append(" ")

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.suppressed = max(0, self.suppressed - 1)
            return
        if self.suppressed:
            return
        if tag in {"h1", "h2", "h3", "h4", "caption", "title"} and self.heading is not None:
            self.headings.append(norm("".join(self.heading)))
            self.heading = None
        if tag == "a":
            self.link_depth = max(0, self.link_depth - 1)
        if tag == "nav":
            self.nav_depth = max(0, self.nav_depth - 1)
        if tag in {"td", "th"} and self.cell is not None:
            self.row.append(norm("".join(self.cell)))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.table.append(self.row)
            self.row = None
        elif tag == "table":
            if self.nested:
                self.nested -= 1
            elif self.table is not None:
                self.tables.append(self.table)
                self.table = None
        if tag in {"p", "div", "h1", "h2", "h3", "tr", "br"}:
            self.text.append(" ")

    def handle_data(self, data):
        if not self.suppressed:
            self.text.append(data)
            if self.heading is not None and not self.link_depth and not self.nav_depth:
                self.heading.append(data)
            if self.cell is not None:
                self.cell.append(data)


def parse_closing_html(html, race_id, *, expected_active=None, expected_nonstarters=None):
    """Return all active prices; never derive odds from ranks or payout amounts.

    This parser supports explicit odds columns, not arbitrary combined racecard
    cells. A previously unseen official layout stays blocked until verified.
    """
    match = identity(race_id)
    parser = Tables()
    parser.feed(html)
    text = norm(" ".join(parser.text))
    headers = re.findall(r"(\d{4})年\s*(\d{1,2})月\s*(\d{1,2})日.{0,100}?"
                         r"(札幌|函館|福島|新潟|東京|中山|中京|京都|阪神|小倉).{0,30}?"
                         r"(?<!\d)(\d{1,2})\s*レース", text)
    expected_header = (int(match[2]), int(match[3]), int(match[4]), VENUES[match[1]], int(match[5]))
    actual = {(int(y), int(m), int(d), v, int(r)) for y, m, d, v, r in headers}
    if actual != {expected_header}:
        raise ValueError("CLOSING_RACE_HEADER_AMBIGUOUS_OR_MISMATCH")
    # Menu links to a final/result page are not evidence that this table is final.
    marker = re.search(r"(?:最終|確定)(?:単勝)?オッズ|レース結果|競走成績", " ".join(parser.headings))
    if marker is None:
        raise ValueError("CLOSING_STATUS_NOT_EXPLICIT")
    candidates = []
    for table in parser.tables:
        for i, row in enumerate(table[:4]):
            head = [re.sub(r"\s+", "", c) for c in row]
            if any("払戻" in h for h in head):
                continue
            ni = [j for j, h in enumerate(head) if h == "馬番"]
            oi = [j for j, h in enumerate(head) if h in {"単勝", "単勝オッズ", "確定単勝オッズ", "最終単勝オッズ"}]
            if len(ni) == len(oi) == 1:
                candidates.append((head, table[i + 1:], ni[0], oi[0]))
                break
    if len(candidates) != 1:
        raise ValueError("CLOSING_ALL_RUNNER_ODDS_TABLE_NOT_UNIQUE")
    head, body, ni, oi = candidates[0]
    name_i = next((i for i, h in enumerate(head) if h == "馬名"), None)
    pop_i = next((i for i, h in enumerate(head) if h in {"人気", "単勝人気"}), None)
    status_i = next((i for i, h in enumerate(head) if h in {"着順", "状態"}), None)
    runners, seen = [], set()
    for row in body:
        if len(row) <= ni or not re.fullmatch(r"\d{1,2}", row[ni]):
            continue
        no = int(row[ni])
        if not 1 <= no <= 18 or no in seen or len(row) != len(head):
            raise ValueError("CLOSING_RUNNER_ROW_AMBIGUOUS")
        seen.add(no)
        state = row[status_i] if status_i is not None else ""
        name = row[name_i] if name_i is not None else None
        status = NONSTARTERS.get(state, "ACTIVE")
        price = row[oi].replace(",", "")
        if status == "ACTIVE":
            if not re.fullmatch(r"\d+(?:\.\d+)?", price):
                raise ValueError("CLOSING_ACTIVE_PRICE_MISSING")
            odds = float(price)
            if not math.isfinite(odds) or not 1 <= odds <= 999.9:
                raise ValueError("CLOSING_PRICE_INVALID")
        else:
            odds = None
        popularity = None
        if pop_i is not None and status == "ACTIVE":
            token = re.fullmatch(r"(\d{1,2})(?:番人気)?", row[pop_i])
            if token is not None:
                popularity = int(token[1])
                if not 1 <= popularity <= 18:
                    raise ValueError("CLOSING_POPULARITY_INVALID")
        runners.append({"runner_id": str(no), "horse_no": no, "horse_name": name,
                        "status": status, "win_odds": odds, "popularity_rank": popularity,
                        "display_capped_999_9": odds == 999.9})
    if len([r for r in runners if r["status"] == "ACTIVE"]) < 2:
        raise ValueError("CLOSING_ACTIVE_UNIVERSE_EMPTY")
    active = {r["runner_id"] for r in runners if r["status"] == "ACTIVE"}
    if expected_active is not None and active != {str(int(x)) for x in expected_active}:
        raise ValueError("CLOSING_ACTIVE_UNIVERSE_MISMATCH")
    if expected_nonstarters is not None:
        for row in runners:
            if row["status"] != "ACTIVE" and expected_nonstarters.get(row["runner_id"]) != row["status"]:
                raise ValueError("CLOSING_NONSTARTER_UNIVERSE_MISMATCH")
    runners.sort(key=lambda r: r["horse_no"])
    return {"race_id": race_id, "closing_marker": marker[0], "runners": runners,
            "n_active": len(active), "popularity_missing": sum(r["status"] == "ACTIVE" and r["popularity_rank"] is None for r in runners),
            "interpretation": "Explicit official closing odds; unsigned research evidence, not a RESULT receipt"}


def decode_html(raw, content_type=""):
    declared = re.search(r"charset=[\"']?([\w-]+)", content_type, re.I)
    meta = re.search(br"charset=[\"']?([\w-]+)", raw[:8192], re.I)
    encoding = declared[1] if declared else meta[1].decode("ascii") if meta else "utf-8"
    if encoding.lower() not in {"utf-8", "utf8", "shift_jis", "shift-jis", "cp932", "euc-jp"}:
        raise ValueError("CLOSING_HTML_ENCODING_UNSUPPORTED")
    return raw.decode(encoding, errors="strict"), encoding


def build_capture(raw, *, race_id, url, captured_at, content_type="text/html; charset=utf-8",
                  request_cname=None, expected_active=None, expected_nonstarters=None):
    official_url(url)
    timestamp(captured_at)
    html, encoding = decode_html(raw, content_type)
    parsed = parse_closing_html(html, race_id, expected_active=expected_active, expected_nonstarters=expected_nonstarters)
    out = {"schema": SCHEMA, "classification": "OFFLINE_RESEARCH_ONLY_UNSIGNED", "race_id": race_id,
           "captured_at": captured_at, "url": url, "request_cname": request_cname,
           "content_type": content_type, "encoding": encoding, "raw_html_base64": base64.b64encode(raw).decode("ascii"),
           "raw_sha256": hashlib.sha256(raw).hexdigest(), "parsed": parsed, "parsed_sha256": digest(parsed)}
    return {**out, "capture_sha256": digest(out)}


def validate_capture(capture, *, race_id, expected_active=None, expected_nonstarters=None):
    if capture.get("schema") != SCHEMA or capture.get("race_id") != race_id:
        raise ValueError("CLOSING_CAPTURE_IDENTITY_INVALID")
    if capture.get("capture_sha256") != digest({k: v for k, v in capture.items() if k != "capture_sha256"}):
        raise ValueError("CLOSING_CAPTURE_SHA_MISMATCH")
    raw = base64.b64decode(capture["raw_html_base64"], validate=True)
    rebuilt = build_capture(raw, race_id=race_id, url=capture["url"], captured_at=capture["captured_at"],
                            content_type=capture["content_type"], request_cname=capture.get("request_cname"),
                            expected_active=expected_active, expected_nonstarters=expected_nonstarters)
    if rebuilt != capture:
        raise ValueError("CLOSING_RAW_OR_PARSED_SHA_MISMATCH")
    return rebuilt


def save_capture(directory, capture):
    """Atomically publish once; no overwrite, including concurrent writers."""
    validate_capture(capture, race_id=capture["race_id"])
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / (capture["race_id"] + ".json")
    fd, temporary = tempfile.mkstemp(prefix=".closing-", dir=directory)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write((canonical(capture) + "\n").encode("utf-8"))
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, target)  # Fails atomically if another capture already exists.
    finally:
        os.unlink(temporary)
    return target

"""Ingest previously acquired NAR race-information ZIPs for LOCAL BVI research."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from contextlib import closing
import csv
from datetime import date, datetime, timezone
from hashlib import sha256
import io
import json
import os
from pathlib import Path
import re
import sqlite3
import unicodedata
from zipfile import ZipFile
from zoneinfo import ZoneInfo


PROVIDER = "NAR_OFFICIAL_RACE_CSV"
JST = ZoneInfo("Asia/Tokyo")
RACE_KEY = ("競馬場", "競走年月日", "レース番号")
RACE_FIELDS = (*RACE_KEY, "発走時刻", "競走種類名称", "レース名", "芝ダート区分", "回り",
               "距離", "天候", "馬場", "頭数", "条件")
HORSE_FIELDS = (*RACE_KEY, "馬番", "馬名", "性", "齢", "生年月日", "父馬名", "母馬名",
                "母父馬名", "調教師所属", "着順", "着差")
PAYBACK_FIELDS = (*RACE_KEY, "単勝組番", "単勝払戻金(円)")
NONFINISH = {
    "出走取消": "CANCELLED", "取消": "CANCELLED", "競走除外": "EXCLUDED", "除外": "EXCLUDED",
    "競走中止": "DID_NOT_FINISH", "中止": "DID_NOT_FINISH", "失格": "DISQUALIFIED",
    "競走取止め": "RACE_CANCELLED", "取止め": "RACE_CANCELLED",
}


def _text(value: str) -> str:
    return unicodedata.normalize("NFKC", value).strip()


def _optional(value: str) -> str | None:
    return _text(value) or None


def _integer(value: str) -> int | None:
    normalized = _text(value)
    return int(normalized) if re.fullmatch(r"\d+", normalized) else None


def _date(value: str) -> str | None:
    value = _text(value)
    if not re.fullmatch(r"[0-9]{8}", value):
        return None
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError:
        return None


def _instant(value: str) -> str:
    result = datetime.fromisoformat(value)
    if result.utcoffset() is None:
        raise ValueError("Timezone required for observations and cutoffs")
    return result.astimezone(timezone.utc).isoformat(timespec="microseconds")


def _post(day: str, time: str) -> str | None:
    hm = _text(time)
    if not re.fullmatch(r"[0-9]{3,4}", hm):
        return None
    hm = hm.zfill(4)
    try:
        return datetime.fromisoformat(f"{day}T{hm[:2]}:{hm[2:]}").replace(tzinfo=JST).isoformat()
    except ValueError:
        return None


def _race_key(row: dict) -> tuple[str, str, int]:
    venue, day, number = _text(row["競馬場"]), _date(row["競走年月日"]), _integer(row["レース番号"])
    if not venue or not day or not number:
        raise ValueError("Invalid NAR race identity")
    return venue, day, number


def _json(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _rows(zipped: ZipFile, member: str, fields: tuple[str, ...]):
    data = zipped.read(member)
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = data.decode("cp932")
    input_rows = csv.reader(io.StringIO(text, newline=""), strict=True)
    header = [_text(column) for column in next(input_rows, [])]
    if len(header) != len(set(header)) or not set(fields).issubset(header):
        raise ValueError(f"Unexpected NAR CSV header: {member}")
    for row in input_rows:
        if len(row) != len(header):
            raise ValueError(f"Unexpected NAR CSV row width: {member}:{input_rows.line_num}")
        yield dict(zip(header, row))


def _members(zipped: ZipFile) -> dict[str, str]:
    members, periods = {}, set()
    for name in zipped.namelist():
        match = re.fullmatch(r"([0-9]{6}(?:[0-9]{2})?)_(racelist|horselist|payback)\.csv", name)
        if match:
            period, kind = match.groups()
            if kind in members:
                raise ValueError(f"Duplicate NAR CSV member: {kind}")
            members[kind] = name
            periods.add(period)
    if set(members) != {"racelist", "horselist", "payback"} or len(periods) != 1:
        raise ValueError("Expected a single NAR race-information ZIP with three CSV files")
    return members


def _runner(row: dict) -> dict:
    no = _integer(row["馬番"])
    if not no:
        raise ValueError("Invalid NAR horse number")
    name, birth_date = _optional(row["馬名"]), _date(row["生年月日"])
    sire, dam, damsire = (_optional(row[field]) for field in ("父馬名", "母馬名", "母父馬名"))
    identity = (name, birth_date, sire, dam, damsire)
    key = sha256(_json(identity).encode()).hexdigest() if all(identity) else None
    rank = _integer(row["着順"]) or None
    finish_status = "FINISHED" if rank else NONFINISH.get(
        _text(row["着順"]) or _text(row["着差"]), "UNKNOWN"
    )
    return {
        "horse_no": no, "name": name, "birth_date": birth_date, "sex": _optional(row["性"]),
        "age": _integer(row["齢"]), "sire": sire, "dam": dam, "damsire": damsire,
        "horse_key": f"nar-composite:{key}" if key else None, "stable_id_confirmed": False,
        "trainer_region": _optional(row["調教師所属"]), "finish": rank, "finish_status": finish_status,
    }


def _read_archive(raw: bytes) -> tuple[dict, int]:
    races, duplicate_rows = {}, 0
    with ZipFile(io.BytesIO(raw)) as zipped:
        members = _members(zipped)
        for row in _rows(zipped, members["racelist"], RACE_FIELDS):
            key = _race_key(row)
            venue, day, number = key
            surface = {"ダート": "DIRT", "芝": "TURF"}.get(_text(row["芝ダート区分"]))
            race = {
                "venue": venue, "race_date": day, "race_no": number,
                "scheduled_at": _post(day, row["発走時刻"]), "race_kind": _optional(row["競走種類名称"]),
                "race_name": _optional(row["レース名"]), "surface": surface,
                "direction": _optional(row["回り"]), "distance": _integer(row["距離"]),
                "weather": _optional(row["天候"]), "going": _optional(row["馬場"]),
                "conditions": _optional(row["条件"]), "field_size": _integer(row["頭数"]),
                "has_payback": False,
            }
            if key in races:
                if races[key] != race:
                    raise ValueError("Conflicting NAR race rows")
                duplicate_rows += 1
            else:
                races[key] = race
        runners = defaultdict(dict)
        for row in _rows(zipped, members["horselist"], HORSE_FIELDS):
            key = _race_key(row)
            if key not in races:
                raise ValueError("NAR horse row without matching race")
            runner = _runner(row)
            no = runner["horse_no"]
            if no in runners[key]:
                if runners[key][no] != runner:
                    raise ValueError("Conflicting NAR runner rows")
                duplicate_rows += 1
            else:
                runners[key][no] = runner
        for row in _rows(zipped, members["payback"], PAYBACK_FIELDS):
            key = _race_key(row)
            if key not in races:
                raise ValueError("NAR payback row without matching race")
            winner = runners[key].get(_integer(row["単勝組番"]))
            # Cancelled races can have placeholders/refunds in the payback file.
            if winner and winner["finish"] == 1 and (_integer(row["単勝払戻金(円)"]) or 0) > 0:
                races[key]["has_payback"] = True
    for key, race in races.items():
        race["runners"] = sorted(runners[key].values(), key=lambda runner: runner["horse_no"])
    return races, duplicate_rows


_SCHEMA = """
CREATE TABLE IF NOT EXISTS archives (
    sha256 TEXT PRIMARY KEY, observed_at TEXT NOT NULL, source_ref TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS payloads (sha256 TEXT PRIMARY KEY, payload TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS observations (
    venue TEXT NOT NULL, race_date TEXT NOT NULL, race_no INTEGER NOT NULL,
    observed_at TEXT NOT NULL, payload_sha256 TEXT NOT NULL, archive_sha256 TEXT NOT NULL,
    PRIMARY KEY (venue, race_date, race_no, observed_at)
);
"""


def _private_database(path: Path) -> None:
    if path.parent.stat().st_mode & 0o077:
        raise ValueError("Use a private directory for the research database")
    if not path.exists():
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            pass
        else:
            os.close(fd)
    if path.is_symlink() or not path.is_file() or path.stat().st_mode & 0o077:
        raise ValueError("Use a private database file (0600)")


def ingest_archive(archive: Path, database: Path, *, observed_at: str, source_ref: str) -> dict:
    """Store immutable timestamped snapshots with each archive's byte-level SHA."""
    stamp = _instant(observed_at)
    if not source_ref.strip():
        raise ValueError("Source reference required")
    raw = Path(archive).read_bytes()
    archive_sha = sha256(raw).hexdigest()
    path = Path(database)
    _private_database(path)
    with closing(sqlite3.connect(path)) as conn, conn:
        conn.executescript(_SCHEMA)
        conn.execute("BEGIN IMMEDIATE")
        if conn.execute("SELECT 1 FROM archives WHERE sha256 = ?", (archive_sha,)).fetchone():
            return {"status": "DUPLICATE_ARCHIVE", "archive_sha256": archive_sha}
        races, duplicate_rows = _read_archive(raw)
        changes, statuses, venues = Counter(), Counter(), Counter()
        identified, payback_races = 0, 0
        conn.execute("INSERT INTO archives VALUES (?, ?, ?)", (archive_sha, stamp, source_ref))
        for key, race in races.items():
            body = _json(race)
            digest = sha256(body.encode()).hexdigest()
            previous = conn.execute(
                """SELECT observed_at, payload_sha256 FROM observations
                   WHERE venue = ? AND race_date = ? AND race_no = ? AND observed_at <= ?
                   ORDER BY observed_at DESC LIMIT 1""",
                (*key, stamp),
            ).fetchone()
            if previous is None:
                changes["new"] += 1
            elif previous[1] == digest:
                changes["unchanged"] += 1
            elif previous[0] == stamp:
                raise ValueError("Conflicting NAR evidence for the same observation instant")
            else:
                changes["changed"] += 1
            conn.execute("INSERT OR IGNORE INTO payloads VALUES (?, ?)", (digest, body))
            conn.execute("INSERT OR IGNORE INTO observations VALUES (?, ?, ?, ?, ?, ?)",
                         (*key, stamp, digest, archive_sha))
            statuses.update(row["finish_status"] for row in race["runners"])
            identified += sum(row["horse_key"] is not None for row in race["runners"])
            payback_races += int(race["has_payback"])
            venues[race["venue"]] += 1
        return {
            "status": "INGESTED", "provider": PROVIDER, "archive_sha256": archive_sha,
            "observed_at": stamp, "races": len(races), "runners": sum(statuses.values()),
            "runners_with_composite_identity": identified, "payback_races": payback_races,
            "duplicate_rows": duplicate_rows, "finish_status_counts": dict(statuses), "venues": dict(venues),
            **{kind: changes[kind] for kind in ("new", "changed", "unchanged")},
        }


def iter_races(database: Path, *, as_of: str):
    """Yield the last snapshot visible at the cutoff, with acquisition provenance."""
    stamp = _instant(as_of)
    uri = Path(database).resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as conn:
        rows = conn.execute(
            """SELECT p.payload, o.payload_sha256, o.archive_sha256, o.observed_at, a.source_ref
               FROM observations o JOIN payloads p ON p.sha256 = o.payload_sha256
               JOIN archives a ON a.sha256 = o.archive_sha256
               JOIN (SELECT venue, race_date, race_no, MAX(observed_at) AS observed_at
                     FROM observations WHERE observed_at <= ? GROUP BY venue, race_date, race_no) latest
               USING (venue, race_date, race_no, observed_at)
               ORDER BY o.race_date, o.venue, o.race_no""", (stamp,),
        )
        for body, digest, archive_sha, observed_at, source_ref in rows:
            if sha256(body.encode()).hexdigest() != digest:
                raise ValueError("NAR research corpus payload hash mismatch")
            yield dict(json.loads(body), archive_sha256=archive_sha, observed_at=observed_at,
                       provider=PROVIDER, source_ref=source_ref)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("database", type=Path)
    parser.add_argument("--observed-at", required=True, help="Actual acquisition time with timezone")
    parser.add_argument("--source-ref", required=True, help="Reference to the authorized download")
    args = parser.parse_args()
    receipt = ingest_archive(args.archive, args.database, observed_at=args.observed_at, source_ref=args.source_ref)
    print(_json(receipt))


if __name__ == "__main__":
    main()

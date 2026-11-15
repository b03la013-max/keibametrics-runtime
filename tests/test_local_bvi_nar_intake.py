import csv
import io
import sqlite3
from zipfile import ZipFile

import pytest

from runtime.local_bvi_nar_intake import ingest_archive, iter_races


SOURCE = "https://www.keiba.go.jp/KeibaWeb/MonthlyConveneInfo/MonthlyConveneInfoTop"
EARLY = "2026-11-15T12:00:00+09:00"
LATE = "2026-11-15T14:00:00+09:00"


def _zip(path, *, final, encoding="utf-8-sig", conflicting_runner=False):
    key = ("川崎", "20261115", 1)
    race = (*key, "1300", "普通", "試験", "ダート", "左", 1400, "晴", "良", 4, "サラブレッド系")
    horses = (
        (*key, 1, "同名", "牡", 3, "20230218", "父Ａ", "母Ａ", "母父Ａ", "川崎", 1 if final else "", ""),
        (*key, 2, "同名", "牡", 4, "20220218", "父Ａ", "母Ｂ", "母父Ａ", "浦和", 1 if final else "", ""),
        (*key, 3, "取消馬", "牝", 4, "", "父Ａ", "母Ｃ", "", "川崎", "", "出走取消"),
        (*key, 4, "中止馬", "牡", 5, "20210228", "父Ａ", "母Ｄ", "母父Ｄ", "大井", "", "競走中止" if final else ""),
    )
    duplicate = (*horses[0][:-2], 2, "") if conflicting_runner else horses[0]
    files = {
        "racelist": [
            ("競馬場", "競走年月日", "レース番号", "発走時刻", "競走種類名称", "レース名", "芝ダート区分",
             "回り", "距離", "天候", "馬場", "頭数", "条件"), race,
        ],
        "horselist": [
            ("競馬場", "競走年月日", "レース番号", "馬番", "馬名", "性", "齢", "生年月日", "父馬名",
             "母馬名", "母父馬名", "調教師所属", "着順", "着差"), *horses, duplicate,
        ],
        "payback": [
            ("競馬場", "競走年月日", "レース番号", "単勝組番", "単勝払戻金（円）"),
            *(((*key, 1, 220), (*key, 2, 1000)) if final else ((*key, "", 100),)),
        ],
    }
    with ZipFile(path, "w") as zipped:
        for file, rows in files.items():
            buf = io.StringIO(newline="")
            csv.writer(buf).writerows(rows)
            zipped.writestr(f"20261115_{file}.csv", buf.getvalue().encode(encoding))
    return path


def test_cutoff_replay_distinguishes_payout_placeholder_and_preserves_tied_ranks(tmp_path):
    path = tmp_path / "private.db"
    early = _zip(tmp_path / "early.zip", final=False)
    late = _zip(tmp_path / "late.zip", final=True, encoding="cp932")
    assert ingest_archive(early, path, observed_at=EARLY, source_ref=SOURCE)["duplicate_rows"] == 1
    receipt = ingest_archive(late, path, observed_at=LATE, source_ref=SOURCE)
    assert receipt["races"] == receipt["changed"] == receipt["payback_races"] == 1
    assert receipt["runners"] == 4
    prior, = iter_races(path, as_of="2026-11-15T03:30:00+00:00")
    result, = iter_races(path, as_of=LATE)
    assert not prior["has_payback"] and prior["runners"][0]["finish"] is None
    assert result["archive_sha256"] == receipt["archive_sha256"]
    assert result["has_payback"] and [r["finish"] for r in result["runners"]] == [1, 1, None, None]
    assert [r["finish_status"] for r in result["runners"]] == ["FINISHED", "FINISHED", "CANCELLED", "DID_NOT_FINISH"]
    assert result["runners"][0]["horse_key"] != result["runners"][1]["horse_key"]
    assert result["runners"][2]["horse_key"] is None
    assert not any(r["stable_id_confirmed"] for r in result["runners"])
    assert path.stat().st_mode & 0o777 == 0o600
    assert ingest_archive(late, path, observed_at="2026-11-16T12:00:00+09:00", source_ref=SOURCE)["status"] == "DUPLICATE_ARCHIVE"


def test_conflicts_leave_existing_snapshot_available(tmp_path):
    path = tmp_path / "private.db"
    early = _zip(tmp_path / "early.zip", final=False)
    late = _zip(tmp_path / "late.zip", final=True)
    broken = _zip(tmp_path / "broken.zip", final=True, conflicting_runner=True)
    ingest_archive(early, path, observed_at=EARLY, source_ref=SOURCE)
    with pytest.raises(ValueError, match="Conflicting NAR runner rows"):
        ingest_archive(broken, path, observed_at=LATE, source_ref=SOURCE)
    with pytest.raises(ValueError, match="same observation instant"):
        ingest_archive(late, path, observed_at=EARLY, source_ref=SOURCE)
    assert ingest_archive(late, path, observed_at=LATE, source_ref=SOURCE)["changed"] == 1
    assert len(list(iter_races(path, as_of=LATE))) == 1


def test_readback_rejects_changed_payload(tmp_path):
    path = tmp_path / "private.db"
    archive = _zip(tmp_path / "early.zip", final=False)
    ingest_archive(archive, path, observed_at=EARLY, source_ref=SOURCE)
    with sqlite3.connect(path) as db:
        db.execute("UPDATE payloads SET payload = '{}' ")
    with pytest.raises(ValueError, match="payload hash mismatch"):
        list(iter_races(path, as_of=EARLY))

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime/capture"))
import keibabook_jra_bands_from_pages as K  # noqa: E402


def test_workouts_parse_nbsp_and_final_furlong():
    t = ("(前回)9/16 栗坂 重一杯に追う1回56.941.027.114.1助手11/15 栗ＣＷ 稍一杯に追う"
         "84.369.053.839.212.1［８］助手11/18 栗坂 重一杯に追う1回56.741.626.913.2")
    assert K.workouts(t) == [["9/16 栗坂", 14.1], ["11/15 栗ＣＷ", 12.1], ["11/18 栗坂", 13.2]]


def test_compact_reads_header_table_and_comments():
    pages = {"date": "20261129", "races": [{"kb_id": "202605040812", "title": "t", "pages": {
        "調教": {"tables": [{"rows": [["枠番", "馬番", "馬名", "短評", ""], ["1", "1", "A", "上向く", "→"],
                                       ["11/26 栗坂 稍強め1回56.141.126.712.9"]]}]},
        "厩舎の話": {"tables": [{"rows": [["枠番", "馬番", "馬 名厩舎の話"], ["1", "1", "A"], ["○【師】順調です。"], [""]]}]}}}]}
    c = K.compact(pages)
    assert c["races"][0]["w"] == [[1, "A", "上向く", [["11/26 栗坂", 12.9]]]]
    assert c["races"][0]["s"] == [[1, "○【師】順調です。"]]

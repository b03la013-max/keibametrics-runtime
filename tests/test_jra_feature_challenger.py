import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime/analysis")); sys.path.insert(0, str(ROOT / "runtime"))
import jra_feature_challenger as FC


def test_tsl_result_annotation_is_a4_error(tmp_path, monkeypatch):
    import gzip
    d = tmp_path / "jra/2026-11-29/tsl_full"; d.mkdir(parents=True)
    rec = {"races": [{"key": "0520261105/11", "horses": [{"no": 1}],
                      "rec": {"axis": "7 [縦]", "main": "5(2着), 6", "second": "1", "cover": "2", "raw": "本線: 5(2着)"}}]}
    with gzip.open(d / "1400_last.json.gz", "wt") as f:
        json.dump(rec, f)
    monkeypatch.setattr(FC, "PRIVATE", tmp_path)
    a4 = FC.A4()
    out = FC.build_tsl_bands("2026-11-29", {"KM-JRA-TKY-20261129-R11": "15:40"}, a4)
    assert out == {} and a4.errors[0]["reason"] == "RESULT_ANNOTATION_IN_PRE_RACE_CAPTURE"


def test_tsl_post_time_strict_and_bands(tmp_path, monkeypatch):
    import gzip
    d = tmp_path / "jra/2026-11-29/tsl_full"; d.mkdir(parents=True)
    rec = {"races": [{"key": "0520261105/11", "rec": {"axis": "7 [縦]", "main": "5, 6", "second": "1", "cover": "2, 9", "raw": "x"}}]}
    for hhmm in ("1500", "1540"):
        with gzip.open(d / f"{hhmm}_last.json.gz", "wt") as f:
            json.dump(rec, f)
    monkeypatch.setattr(FC, "PRIVATE", tmp_path)
    a4 = FC.A4()
    out = FC.build_tsl_bands("2026-11-29", {"KM-JRA-TKY-20261129-R11": "15:40"}, a4)
    r = out["KM-JRA-TKY-20261129-R11"]
    assert r["capture"] == "1500"           # 15:40 capture is not strictly before post
    assert r["bands"] == {"1": "NEUTRAL", "2": "NEUTRAL", "5": "POSITIVE", "6": "POSITIVE", "7": "STRONG", "9": "NEUTRAL"}
    assert not a4.errors


def test_challenger_fills_only_unobserved_and_prod_matches_frozen():
    rid = "KM-JRA-KYO-20261122-R11"
    p = ROOT / f"runtime/requests/{rid}-LIVE-R1-FORMAL.json"
    if not p.exists():
        return
    req = json.loads(p.read_text())
    mapping = FC._mapping()
    a4 = FC.A4()
    order, filled = FC.rank_arm(req, mapping, {}, a4, "PROD")
    frozen = [str(x) for x in req["static_prediction"]["ranking"]]
    assert order == frozen and filled == 0 and not a4.errors
    no = str(req["runners"][0]["runner_id"])
    observed = next(k for k, v in req["runners"][0]["evidence_features"].items() if isinstance(v, dict) and v.get("category"))
    add = {no: {observed: FC._spec("WEAK", "x", "x", "x"), "workout_load": FC._spec("STRONG", "x", "x", "x")}}
    _, filled = FC.rank_arm(req, mapping, add, a4, "CH")
    assert filled == 1                      # the observed Production feature is never overwritten

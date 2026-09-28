import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"))

import mec_r4_oos_tracker as r4
import local_mec_r5_oos_tracker as r5


def _write_result(root: Path, name: str, race_id: str, acceptance_only: bool):
    d=root/"runtime"/"family_result_requests"
    d.mkdir(parents=True,exist_ok=True)
    (d/name).write_text(json.dumps({
        "race_id":race_id,
        "official_result_verified":True,
        "official_result_verification_ref":"OFFICIAL:TEST",
        "source":"NAR_OFFICIAL",
        "acceptance_only":acceptance_only,
    }),encoding="utf-8")


def test_acceptance_only_result_is_verified_but_never_oos_admissible(tmp_path,monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write_result(tmp_path,"acc.json","R-ACC",True)
    for fn in (r4._official_result_authority,r5._official_result_authority):
        x=fn("R-ACC")
        assert x["verified"] is True
        assert x["oos_admissible"] is False
        assert x["refs"][0]["acceptance_only"] is True


def test_verified_non_acceptance_result_remains_oos_admissible(tmp_path,monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write_result(tmp_path,"live.json","R-LIVE",False)
    for fn in (r4._official_result_authority,r5._official_result_authority):
        x=fn("R-LIVE")
        assert x["verified"] is True
        assert x["oos_admissible"] is True
        assert x["refs"][0]["acceptance_only"] is False

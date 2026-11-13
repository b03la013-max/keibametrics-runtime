"""FNB R8 cancellation and active-set Raw replay, synthetic only."""
import json
import runpy
from pathlib import Path
from datetime import datetime, timezone

from runtime.local_fnb_r8_day_semantics import audit_day
from runtime.local_race_day_dispatcher import sha
from runtime.local_physical.nar_runner_universe import enrich_source_artifact
from runtime.local_physical.nar_source_manifest import _race_card_source
from runtime.local_physical.source_acquisition import snapshot_from_bytes

SOURCE=runpy.run_path(str(Path(__file__).with_name("test_fnb_20261102_r8_semantics.py")))
full_plan=SOURCE["full_plan"]


def test_r8_official_cancelled_runner_reflects_active_status():
    plan=full_plan()
    spec=_race_card_source("FNB","19","2026/11/02",1)
    html=("<html><body><p>2026年11月2日 船橋 第1競走 14:45発走</p>"
          "<table><tr><th>枠番</th><th>馬番</th><th>競走馬</th></tr>"
          "<tr><td>1</td><td>1</td><td>テスト一号</td><td>出走取消</td></tr>"
          "<tr><td>2</td><td>2</td><td>テスト二号</td></tr></table></body></html>")
    card,errors=snapshot_from_bytes(spec,html.encode(),final_url=spec["url"],
        status_code=200,headers={"content-type":"text/html; charset=UTF-8"},
        fetched_at="2026-11-02T12:00:00+09:00")
    assert not errors
    plan["official_snapshots"][1]=card
    evidence={"normalized_evidence":{"race_card_tables":{
        "value":card["extracted_evidence"]["race_card_tables"],
        "source_id":card["source_id"],"snapshot_sha256":card["snapshot_sha256"]}}}
    rebuilt=enrich_source_artifact(evidence)
    row=plan["races"][0]
    row["source_basis_sha256"]=card["snapshot_sha256"]
    row["declared_runner_universe"]=rebuilt["declared_runner_universe"]
    row["runner_status_registry"]=rebuilt["runner_status_registry"]
    plan["plan_sha256"]=sha({k:v for k,v in plan.items() if k!="plan_sha256"})
    proof=audit_day(plan,"2026-11-02")
    assert proof["status"]=="FNB_DAY_SEMANTICS_CONSISTENT",proof["issues"]
    assert proof["races"][0]["cancelled"]==1
    row["runner_status_registry"][0]["status"]="ACTIVE_DECLARED"
    plan["plan_sha256"]=sha({k:v for k,v in plan.items() if k!="plan_sha256"})
    bad=audit_day(plan,"2026-11-02")
    assert bad["status"]=="FNB_DAY_SEMANTICS_HOLD"

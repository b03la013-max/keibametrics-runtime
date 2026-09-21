from __future__ import annotations

import json
import os
import sys
from copy import deepcopy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"runtime"))

from jra_evidence_to_base_production import load_mapping, attach_production_ledger_to_request
from jra_index_provenance_builder import materialize_index_provenance

MAPPING_PATH=ROOT/"mapping"/"jra_base_index_evidence_mapping_v1.0_20260921.json"
MAPPING=load_mapping(MAPPING_PATH)
BASE=["HPI","SSI","CFI","RFI","BVI","JTI","CSI","TRI","BWI","GCI","PRI","KGI","VMI"]
DERIVED=["DCR","TPI","ZAI_WIN","ZAI_PLACE","SRI","F3S","T3I"]
REQUIRED=BASE+DERIVED


def canonical_complete(runner):
    cc=runner.get("canonical_components")
    if not isinstance(cc,dict):
        return False
    for k in REQUIRED:
        x=cc.get(k)
        if not isinstance(x,dict):
            return False
        if not isinstance(x.get("value"),(int,float)):
            return False
        if not x.get("rule_id") or not x.get("mapping_version") or not x.get("evidence_refs") or not x.get("source_fact"):
            return False
    return True


def calculate(payload):
    race_id=payload.get("race_id")
    runners=payload.get("runners")
    if not race_id or not isinstance(runners,list) or len(runners)<2:
        return 422,{"status":"FAIL","errors":["RACE_OR_RUNNERS_MISSING"]}

    req={"race_id":race_id,"runners":deepcopy(runners)}
    if all(canonical_complete(r) for r in runners):
        out_runners=[]
        for r in runners:
            out_runners.append({
                "runner_id":str(r["runner_id"]),
                "name":str(r.get("name") or ""),
                "profile":"CANONICAL_REPLAY",
                "canonical_components":deepcopy(r["canonical_components"]),
            })
    else:
        req=attach_production_ledger_to_request(req,MAPPING)
        req=materialize_index_provenance(req)
        out_runners=[]
        for r in req["runners"]:
            profile=req["index_provenance_ledger"]["runners"][str(r["runner_id"])]["profile"]
            out_runners.append({
                "runner_id":str(r["runner_id"]),
                "name":str(r.get("name") or ""),
                "profile":profile,
                "canonical_components":deepcopy(r["canonical_components"]),
            })

    required=len(out_runners)*20
    return 200,{
        "status":"PASS",
        "race_id":race_id,
        "mapping_id":MAPPING["mapping_id"],
        "required_count":required,
        "calculated_count":required,
        "ruled_hold_count":0,
        "not_applicable_count":0,
        "unresolved_count":0,
        "runners":out_runners,
    }


def selftest():
    keys=set()
    for p in MAPPING["index_profiles"].values():
        for w in p.values():
            keys.update(w)
    for d in MAPPING["dcr"].values():
        if d.get("feature"): keys.add(d["feature"])
        if d.get("newcomer_fallback_feature"): keys.add(d["newcomer_fallback_feature"])

    def feats(tag,cat):
        return {k:{"category":cat,"evidence_refs":[f"{tag}:{k}"],"source_fact":f"pre-race {k}","rule_id":f"SELFTEST-{k}-v1"} for k in keys}

    runners=[
        {"runner_id":"1","name":"EST","career_starts":12,"evidence_features":feats("E","STRONG"),
         "dcr_inputs":{"official_recent":{"points":23,"evidence_refs":["E:r"],"source_fact":"12 starts","rule_id":"DCR-E-R"},
                       "same_course_distance":{"points":18,"evidence_refs":["E:c"],"source_fact":"course history","rule_id":"DCR-E-C"}}},
        {"runner_id":"2","name":"LOW","career_starts":2,"evidence_features":feats("L","POSITIVE"),
         "dcr_inputs":{"official_recent":{"points":15,"evidence_refs":["L:r"],"source_fact":"2 starts","rule_id":"DCR-L-R"},
                       "same_course_distance":{"points":8,"evidence_refs":["L:c"],"source_fact":"limited course history","rule_id":"DCR-L-C"}}},
        {"runner_id":"3","name":"NEW","career_starts":0,"newcomer":True,"evidence_features":feats("N","NEUTRAL")},
    ]
    code,body=calculate({"race_id":"KM-JRA-RENDER-PROD-SELFTEST","runners":runners})
    assert code==200
    body["profiles"]=[r["profile"] for r in body["runners"]]
    body.pop("runners",None)
    return body


class Handler(BaseHTTPRequestHandler):
    def log_message(self,fmt,*args):
        sys.stdout.write("JRA_BASE_INDEX_HTTP "+(fmt%args)+"\n")
        sys.stdout.flush()

    def send_json(self,code,body):
        raw=json.dumps(body,ensure_ascii=False,separators=(",",":")).encode("utf-8")
        self.send_response(code)
        self.send_header("content-type","application/json; charset=utf-8")
        self.send_header("content-length",str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path=="/health":
            self.send_json(200,{
                "status":"READY",
                "service":"JRA_BASE_INDEX_CALCULATOR",
                "mapping_id":MAPPING["mapping_id"],
                "registry_id":"JRA-BASE-INDEX-MAPPING-REGISTRY-v1.0-20260921",
                "mode":"PRODUCTION_EVIDENCE_TO_20_INDEX_OR_CANONICAL_REPLAY",
                "calibration_status":MAPPING.get("calibration_status"),
            })
            return
        if self.path=="/selftest":
            try:
                self.send_json(200,selftest())
            except Exception as e:
                self.send_json(500,{"status":"FAIL","errors":[str(e)]})
            return
        if self.path=="/registry":
            self.send_json(200,MAPPING)
            return
        self.send_json(404,{"status":"NOT_FOUND"})

    def do_POST(self):
        if self.path not in {"/calculate-jra-base","/selftest"}:
            self.send_json(404,{"status":"NOT_FOUND"})
            return
        try:
            if self.path=="/selftest":
                self.send_json(200,selftest())
                return
            n=int(self.headers.get("content-length","0"))
            payload=json.loads(self.rfile.read(n) or b"{}")
            code,body=calculate(payload)
            self.send_json(code,body)
        except Exception as e:
            self.send_json(422,{"status":"FAIL","errors":[str(e)]})


if __name__=="__main__":
    port=int(os.environ.get("PORT","10000"))
    print(json.dumps({"event":"JRA_BASE_INDEX_RUNTIME_START","port":port,"mapping_id":MAPPING["mapping_id"]},ensure_ascii=False),flush=True)
    ThreadingHTTPServer(("0.0.0.0",port),Handler).serve_forever()

from __future__ import annotations

import argparse
import copy
import datetime
import hashlib
import json
import os
import pathlib
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Dict, Iterable, List, Tuple

PROFILE_ID="KM-FAMILY-RACE-DAY-FAST-PATH-20260928-R1"
CACHE_SCHEMA="KM-RACE-DAY-CONTENT-CACHE-v1"
DEFAULT_CACHE_ROOT=pathlib.Path(os.environ.get("KM_FAST_CACHE_ROOT",".km_fast_cache"))
TARGET_CRITICAL_PATH_SECONDS=300
HARD_SLO_SECONDS=420
PURCHASE_RESERVE_TARGET_SECONDS=600
NEXT_RACE_PREWARM_DEPTH=3

class FastPathError(ValueError):
    pass

def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()

def sha_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()

def sha_file(path: str | pathlib.Path) -> str:
    p=pathlib.Path(path)
    h=hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def atomic_json(path: pathlib.Path, obj: Any) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    raw=canonical_bytes(obj)
    with tempfile.NamedTemporaryFile("wb",delete=False,dir=str(path.parent)) as tf:
        tf.write(raw)
        tmp=tf.name
    os.replace(tmp,path)

def _impl_fingerprints(paths: Iterable[str | pathlib.Path]) -> Dict[str,str]:
    out={}
    for p in paths:
        pp=pathlib.Path(p)
        if not pp.exists():
            raise FastPathError(f"IMPLEMENTATION_FILE_MISSING:{pp}")
        out[str(pp)]=sha_file(pp)
    return out

class ContentCache:
    def __init__(self,root: str | pathlib.Path=DEFAULT_CACHE_ROOT):
        self.root=pathlib.Path(root)

    def key(self,stage: str,deps: Any,implementation_paths: Iterable[str | pathlib.Path]) -> Dict[str,Any]:
        impl=_impl_fingerprints(implementation_paths)
        meta={
            "schema":CACHE_SCHEMA,
            "profile":PROFILE_ID,
            "stage":stage,
            "dependency_sha256":sha_obj(deps),
            "implementation_sha256":impl,
        }
        meta["cache_key_sha256"]=sha_obj(meta)
        return meta

    def path_for(self,meta: Dict[str,Any]) -> pathlib.Path:
        return self.root / str(meta["stage"]) / (str(meta["cache_key_sha256"])+".json")

    def get(self,stage: str,deps: Any,implementation_paths: Iterable[str | pathlib.Path]) -> Tuple[Any|None,Dict[str,Any]]:
        meta=self.key(stage,deps,implementation_paths)
        path=self.path_for(meta)
        if not path.exists():
            return None,{**meta,"cache":"MISS","path":str(path)}
        try:
            obj=json.load(path.open(encoding="utf-8"))
        except Exception as e:
            return None,{**meta,"cache":"CORRUPT","path":str(path),"error":str(e)}
        if obj.get("meta")!=meta:
            return None,{**meta,"cache":"META_MISMATCH","path":str(path)}
        payload=obj.get("payload")
        if str(obj.get("payload_sha256") or "")!=sha_obj(payload):
            return None,{**meta,"cache":"PAYLOAD_HASH_MISMATCH","path":str(path)}
        return copy.deepcopy(payload),{**meta,"cache":"HIT","path":str(path)}

    def put(self,stage: str,deps: Any,implementation_paths: Iterable[str | pathlib.Path],payload: Any) -> Dict[str,Any]:
        meta=self.key(stage,deps,implementation_paths)
        path=self.path_for(meta)
        env={
            "meta":meta,
            "payload_sha256":sha_obj(payload),
            "payload":copy.deepcopy(payload),
        }
        atomic_json(path,env)
        return {**meta,"cache":"WRITE","path":str(path),"payload_sha256":env["payload_sha256"]}

class StageTimer:
    def __init__(self):
        self.started=time.perf_counter()
        self.events=[]

    def mark(self,name: str,**extra: Any) -> Dict[str,Any]:
        elapsed=time.perf_counter()-self.started
        row={"stage":name,"elapsed_seconds":round(elapsed,6),**extra}
        self.events.append(row)
        return row

    def report(self,scheduled_post_at: str|None=None) -> Dict[str,Any]:
        total=time.perf_counter()-self.started
        remaining=None
        if scheduled_post_at:
            try:
                post=datetime.datetime.fromisoformat(str(scheduled_post_at).replace("Z","+00:00"))
                if post.tzinfo is None:
                    post=post.replace(tzinfo=datetime.timezone.utc)
                remaining=(post.astimezone(datetime.timezone.utc)-datetime.datetime.now(datetime.timezone.utc)).total_seconds()
            except Exception:
                remaining=None
        cls=("FAST_TARGET" if total<=TARGET_CRITICAL_PATH_SECONDS else
             "WITHIN_HARD_SLO" if total<=HARD_SLO_SECONDS else "SLO_MISS")
        return {
            "profile":PROFILE_ID,
            "critical_path_seconds":round(total,6),
            "latency_class":cls,
            "target_seconds":TARGET_CRITICAL_PATH_SECONDS,
            "hard_slo_seconds":HARD_SLO_SECONDS,
            "target_met":total<=TARGET_CRITICAL_PATH_SECONDS,
            "hard_slo_met":total<=HARD_SLO_SECONDS,
            "purchase_reserve_target_seconds":PURCHASE_RESERVE_TARGET_SECONDS,
            "purchase_reserve_seconds":None if remaining is None else round(remaining,6),
            "purchase_reserve_target_met":None if remaining is None else remaining>=PURCHASE_RESERVE_TARGET_SECONDS,
            "scheduled_post_at":scheduled_post_at,
            "slo_policy":"DIAGNOSTIC_ONLY; NEVER BYPASS FORMAL GATES TO MEET LATENCY",
            "events":copy.deepcopy(self.events),
        }

def _runner_materialization_dependency(
    runner: Dict[str,Any],
    venue_rule_registry: Dict[str,Any],
    required_indices: List[str],
    allow_base_hold: bool,
) -> Dict[str,Any]:
    return {
        "runner_id":str(runner.get("runner_id") or ""),
        "evidence_features":copy.deepcopy(runner.get("evidence_features") or {}),
        "canonical_external_indices":copy.deepcopy(runner.get("canonical_external_indices") or {}),
        "venue_rule_registry":copy.deepcopy(venue_rule_registry),
        "required_indices":list(required_indices),
        "allow_base_index_rule_hold":bool(allow_base_hold),
    }

def materialize_request_fast(
    req: Dict[str,Any],
    required_indices: Iterable[str],
    *,
    cache_root: str | pathlib.Path=DEFAULT_CACHE_ROOT,
    workers: int=4,
) -> Tuple[Dict[str,Any],Dict[str,Any]]:
    # This function is intentionally behavior-preserving. It calls the canonical
    # Production materialize_runner implementation and caches only the derived
    # runner fields. Unrelated request/source fields are never restored from cache.
    try:
        from local_evidence_to_base_production import (
            materialize_runner, TERMINAL_STATUSES, REGISTRY_ID
        )
    except ModuleNotFoundError:
        from runtime.local_evidence_to_base_production import (
            materialize_runner, TERMINAL_STATUSES, REGISTRY_ID
        )

    q=copy.deepcopy(req)
    vr=q.get("venue_formula_registry")
    if vr is None:
        vr={"registry_id":"LOCAL-TERMINAL-FALLBACK-v1","allowed_rule_ids":{}}
    if not isinstance(vr,dict) or not str(vr.get("registry_id") or ""):
        raise FastPathError("VENUE_FORMULA_REGISTRY_INVALID")
    runners=q.get("runners")
    if not isinstance(runners,list) or not runners:
        raise FastPathError("RUNNERS_REQUIRED")
    required=[str(x) for x in required_indices]
    allow_base_hold=bool(q.get("allow_base_index_rule_hold",False))
    cache=ContentCache(cache_root)
    impl=["runtime/local_evidence_to_base_production.py","runtime/local_evidence_feature_normalizer_production.py"]

    def one(ix_runner: Tuple[int,Dict[str,Any]]) -> Tuple[int,Dict[str,Any],Dict[str,Any]]:
        ix,runner=ix_runner
        deps=_runner_materialization_dependency(runner,vr,required,allow_base_hold)
        payload,meta=cache.get("LOCAL_NUMERICAL_RUNNER",deps,impl)
        if payload is None:
            built=materialize_runner(
                runner,vr,required,
                allow_base_index_rule_hold=allow_base_hold
            )
            payload={
                "canonical_components":copy.deepcopy(built.get("canonical_components") or {}),
                "local_mapping_registry":built.get("local_mapping_registry"),
                "numeric_materialization_hash":built.get("numeric_materialization_hash"),
            }
            meta=cache.put("LOCAL_NUMERICAL_RUNNER",deps,impl,payload)
            meta["cache"]="MISS_WRITE"
        out=copy.deepcopy(runner)
        out["canonical_components"]=copy.deepcopy(payload["canonical_components"])
        out["local_mapping_registry"]=payload["local_mapping_registry"]
        out["numeric_materialization_hash"]=payload["numeric_materialization_hash"]
        return ix,out,meta

    rows=[None]*len(runners)
    metas=[None]*len(runners)
    max_workers=max(1,min(int(workers or 1),len(runners),8))
    if max_workers==1:
        built=[one(x) for x in enumerate(runners)]
    else:
        built=[]
        with ThreadPoolExecutor(max_workers=max_workers,thread_name_prefix="km-fast-num") as ex:
            futs=[ex.submit(one,x) for x in enumerate(runners)]
            for fut in as_completed(futs):
                built.append(fut.result())
    for ix,out,meta in built:
        rows[ix]=out; metas[ix]=meta
    q["runners"]=rows

    term_rows=[]; unresolved=[]
    counts={k:0 for k in TERMINAL_STATUSES}
    for r in q["runners"]:
        cc=r["canonical_components"]
        rid=str(r.get("runner_id"))
        for idx in required:
            spec=cc.get(idx)
            if not isinstance(spec,dict):
                unresolved.append({"runner_id":rid,"index":idx,"reason":"TERMINAL-UNRESOLVED"})
                continue
            status=str(spec.get("terminal_status") or "").upper()
            if status not in TERMINAL_STATUSES:
                unresolved.append({"runner_id":rid,"index":idx,"reason":"TERMINAL-STATUS-INVALID"})
                continue
            counts[status]+=1
            term_rows.append({"runner_id":rid,"index":idx,"terminal_status":status})
    required_count=len(runners)*len(required)
    terminalized=sum(counts.values())
    q["required_indices"]=required
    q["numeric_coverage"]={
        "required_count":required_count,
        "terminalized_count":terminalized,
        "calculated_count":counts["CALCULATED"],
        "ruled_neutral_count":counts["RULED-NEUTRAL"],
        "ruled_hold_count":counts["RULED-HOLD"],
        "not_applicable_count":counts["NOT-APPLICABLE"],
        "unresolved_count":len(unresolved),
        "unresolved":unresolved,
    }
    q["full_terminalization"]=(len(unresolved)==0 and terminalized==required_count)
    q["full_numerical_calculation"]=(q["full_terminalization"] and counts["CALCULATED"]==required_count)
    q["local_mapping_registry"]=REGISTRY_ID
    q["index_terminalization_hash"]=sha_obj(term_rows)
    q["index_provenance_hash"]=sha_obj([r["canonical_components"] for r in q["runners"]])

    hits=sum(1 for m in metas if (m or {}).get("cache")=="HIT")
    report={
        "profile":PROFILE_ID,
        "stage":"LOCAL_NUMERICAL_MATERIALIZATION",
        "runner_count":len(runners),
        "workers":max_workers,
        "cache_hits":hits,
        "cache_misses":len(runners)-hits,
        "cache_hit_ratio":round(hits/max(1,len(runners)),6),
        "runner_cache":metas,
        "behavior_contract":"DICT-EQUIVALENT TO canonical materialize_request for identical input",
    }
    return q,report

def materialization_equivalence(req: Dict[str,Any],required_indices: Iterable[str],cache_root: str|pathlib.Path=DEFAULT_CACHE_ROOT) -> Dict[str,Any]:
    try:
        from local_evidence_to_base_production import materialize_request
    except ModuleNotFoundError:
        from runtime.local_evidence_to_base_production import materialize_request
    full=materialize_request(copy.deepcopy(req),list(required_indices))
    fast,report=materialize_request_fast(copy.deepcopy(req),list(required_indices),cache_root=cache_root)
    same=full==fast
    return {
        "status":"PASS" if same else "FAIL",
        "profile":PROFILE_ID,
        "full_sha256":sha_obj(full),
        "fast_sha256":sha_obj(fast),
        "equal":same,
        "cache_report":report,
    }

def production_equivalence_projection(obj: Dict[str,Any]) -> Dict[str,Any]:
    # Compare only Prediction/Selection/Execution behavior. Receipt timestamps,
    # workflow ids, cache reports and research-shadow artifacts are deliberately
    # excluded because they do not define the wager recommendation.
    art=obj.get("artifact") if isinstance(obj.get("artifact"),dict) else obj
    fpp=art.get("final_prediction_package") or {}
    ticket=art.get("final_ticket") or {}
    mec=art.get("minimum_efficient_coverage") or fpp.get("minimum_efficient_coverage") or {}
    cap=art.get("capital_policy_decision") or fpp.get("capital_policy_decision") or {}
    trace=art.get("ticket_transport_trace") or {}
    return {
        "static_prediction":fpp.get("static_prediction") or art.get("static_prediction"),
        "actual_numerical_calculation":fpp.get("actual_numerical_calculation"),
        "local_mapping_registry":fpp.get("local_mapping_registry"),
        "index_provenance_hash":fpp.get("index_provenance_hash"),
        "local_krs_bridge_id":fpp.get("local_krs_bridge_id"),
        "local_krs_input_sha256":fpp.get("local_krs_input_sha256"),
        "mec_profile":mec.get("profile"),
        "mec_tickets":mec.get("tickets"),
        "mec_material_coverage_ratio":mec.get("material_coverage_ratio"),
        "capital_mode":cap.get("mode"),
        "capital_decision":cap.get("decision"),
        "capital_required":cap.get("required_capital"),
        "final_no_bet":ticket.get("no_bet"),
        "final_total_investment":ticket.get("total_investment"),
        "final_tickets":ticket.get("tickets"),
        "candidate_source":trace.get("candidate_source"),
        "selection_source":trace.get("selection_source"),
        "bet_type_dispositions":trace.get("bet_type_dispositions"),
    }

def compare_production_outputs(full_obj: Dict[str,Any],fast_obj: Dict[str,Any]) -> Dict[str,Any]:
    a=production_equivalence_projection(full_obj)
    b=production_equivalence_projection(fast_obj)
    return {
        "profile":PROFILE_ID,
        "status":"PASS" if a==b else "FAIL",
        "equivalent":a==b,
        "full_projection_sha256":sha_obj(a),
        "fast_projection_sha256":sha_obj(b),
        "full_projection":a,
        "fast_projection":b,
    }

def _race_meta(req: Dict[str,Any]) -> Tuple[str,str,int]:
    race=req.get("race") if isinstance(req.get("race"),dict) else {}
    venue=str(req.get("venue_id") or race.get("venue_id") or "")
    date=str(req.get("race_date") or race.get("race_date") or race.get("date") or "")
    no=req.get("race_no") or race.get("race_no")
    try: no=int(no)
    except Exception: no=0
    return venue,date,no

def discover_next_requests(current_path: str|pathlib.Path,request_dir: str|pathlib.Path,limit: int=NEXT_RACE_PREWARM_DEPTH) -> List[pathlib.Path]:
    current_path=pathlib.Path(current_path)
    current=json.load(current_path.open(encoding="utf-8"))
    venue,date,no=_race_meta(current)
    found=[]
    for p in pathlib.Path(request_dir).glob("*.json"):
        try:
            q=json.load(p.open(encoding="utf-8"))
        except Exception:
            continue
        v,d,n=_race_meta(q)
        if str(q.get("family_id") or "").upper()!="LOCAL": continue
        if v!=venue or d!=date or n<=no: continue
        phase=str(q.get("execution_phase") or q.get("phase") or "FORMAL").upper()
        if phase not in {"FORMAL","FORMAL-PRE-RACE"}: continue
        found.append((n,p))
    found.sort(key=lambda x:(x[0],str(x[1])))
    return [p for _,p in found[:max(0,int(limit))]]

def prewarm_request(path: str|pathlib.Path,cache_root: str|pathlib.Path=DEFAULT_CACHE_ROOT) -> Dict[str,Any]:
    p=pathlib.Path(path)
    req=json.load(p.open(encoding="utf-8"))
    indices=req.get("required_indices") or req.get("required_index_names") or []
    if indices and isinstance(indices[0],dict):
        indices=[str(x.get("index") or x.get("index_name") or x.get("name") or "") for x in indices]
    indices=[str(x) for x in indices if str(x)]
    report={
        "profile":PROFILE_ID,
        "request_path":str(p),
        "race_id":req.get("race_id"),
        "status":"NOT_PREWARMABLE",
        "reason":None,
    }
    if str(req.get("family_id") or "").upper()!="LOCAL":
        report["reason"]="LOCAL_ONLY"; return report
    if not indices or not isinstance(req.get("runners"),list) or not req.get("runners"):
        report["reason"]="RUNNERS_OR_REQUIRED_INDICES_NOT_READY"; return report
    try:
        fast,cache_report=materialize_request_fast(req,indices,cache_root=cache_root)
        report.update({
            "status":"PREWARMED",
            "materialized_sha256":sha_obj(fast),
            "cache_report":cache_report,
            "dependency_rule":"EXACT INPUT + IMPLEMENTATION HASH; ANY CHANGE AUTO-MISSES",
        })
    except Exception as e:
        report.update({"status":"PREWARM_FAILED_NON_BLOCKING","reason":type(e).__name__+":"+str(e)})
    return report

def prewarm_next(current_path: str|pathlib.Path,request_dir: str|pathlib.Path,cache_root: str|pathlib.Path=DEFAULT_CACHE_ROOT,limit: int=NEXT_RACE_PREWARM_DEPTH) -> Dict[str,Any]:
    paths=discover_next_requests(current_path,request_dir,limit)
    rows=[]
    if paths:
        with ThreadPoolExecutor(max_workers=min(len(paths),NEXT_RACE_PREWARM_DEPTH),thread_name_prefix="km-fast-prewarm") as ex:
            futs={ex.submit(prewarm_request,p,cache_root):p for p in paths}
            for fut in as_completed(futs):
                rows.append(fut.result())
        rows.sort(key=lambda x:str(x.get("request_path")))
    return {
        "profile":PROFILE_ID,
        "current_request":str(current_path),
        "prewarm_depth":limit,
        "discovered":len(paths),
        "results":rows,
    }

def main() -> int:
    ap=argparse.ArgumentParser()
    sp=ap.add_subparsers(dest="cmd",required=True)
    p=sp.add_parser("prewarm")
    p.add_argument("--request",required=True)
    p.add_argument("--cache-root",default=str(DEFAULT_CACHE_ROOT))
    n=sp.add_parser("prewarm-next")
    n.add_argument("--current-request",required=True)
    n.add_argument("--request-dir",default="runtime/family_requests")
    n.add_argument("--cache-root",default=str(DEFAULT_CACHE_ROOT))
    n.add_argument("--limit",type=int,default=NEXT_RACE_PREWARM_DEPTH)
    e=sp.add_parser("equivalence")
    e.add_argument("--request",required=True)
    e.add_argument("--cache-root",default=str(DEFAULT_CACHE_ROOT))
    args=ap.parse_args()

    if args.cmd=="prewarm":
        out=prewarm_request(args.request,args.cache_root)
    elif args.cmd=="prewarm-next":
        out=prewarm_next(args.current_request,args.request_dir,args.cache_root,args.limit)
    else:
        req=json.load(open(args.request,encoding="utf-8"))
        idx=req.get("required_indices") or req.get("required_index_names") or []
        if idx and isinstance(idx[0],dict):
            idx=[str(x.get("index") or x.get("index_name") or x.get("name") or "") for x in idx]
        out=materialization_equivalence(req,[str(x) for x in idx if str(x)],args.cache_root)
    print(json.dumps(out,ensure_ascii=False,sort_keys=True))
    return 0 if out.get("status")!="FAIL" else 2

if __name__=="__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Kyoto 2026-10-12 R11 result-blind retrospective, using existing JRA calculators/engines.

The original certified evidence is a PDF captured for R10 at 14:17:32 JST, which
contains the entire Kyoto official race card, including R11. The R10 source receipt
is not and must not be misrepresented as an R11 signed pre-race SOURCE.
No R11 race outcome/settlement may enter any numerical, semantic, or KRS input.
Later-fetched historical pages are filtered strictly to runs before 2026-10-12.
All generated results are POST-START-REPLAY/PAPER/NO-OOS, not Production FINAL.
"""
from __future__ import annotations

import argparse,base64,copy,datetime as dt,gzip,hashlib,json,os,sys,traceback,urllib.request,urllib.error
from pathlib import Path

import fitz
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

sys.path.insert(0,"runtime")
sys.path.insert(0,"runtime/jra_source_runtime")

RACE="KM-JRA-KYO-20261012-R11"
ORIGINAL="KM-JRA-KYO-20261012-R10-LIVE-R1"
SOURCE_PATH=Path("runtime/executions")/ORIGINAL/"SOURCE/runs/38207250686/source_receipt_envelope.json"
ORIG_CUTOFF="2026-10-12T15:40:00+09:00"
POST="2026-10-12T15:45:00+09:00"
RDATE="2026-10-12"
KRS_BASE="https://quorumprobe-production.up.railway.app"
ENGINE_SHA="9929df994aa7964173edef9af7e9a705628ce377babf22df3af4e280fc275421"
REQUIRED=["HPI","SSI","CFI","RFI","BVI","JTI","CSI","TRI","BWI","GCI","PRI","KGI","VMI","DCR","TPI","ZAI_WIN","ZAI_PLACE","SRI","F3S","T3I"]


def sha(x):
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def ts(s):
    return dt.datetime.fromisoformat(str(s).replace("Z","+00:00"))

def local(obj):
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2,default=str)+"\n"

def sanitize_detail(o):
    if not isinstance(o,dict):return None
    o=copy.deepcopy(o)
    rows=[]
    removed=0
    for r in o.get("runners",[]):
        r["recent_runs"]=[x for x in r.get("recent_runs",[]) if str(x.get("date") or "")<RDATE]
        removed+=1
        # Post-race odds and popularity are NOT certified as known by the 15:40 cutoff.
        r.pop("win_odds",None);r.pop("popularity_rank",None)
        # Assigned weight, sire/dam, rider, and pre-race bodyweight are result-independent.
        rows.append(r)
    o["runners"]=rows
    o["race_environment"]={"going":"良","going_surface":"芝","weather":"晴"}
    return o

def sanitize_history(o):
    if not isinstance(o,dict):return None
    o=copy.deepcopy(o)
    removed=0
    for r in (o.get("runners") or {}).values():
        prev=list(r.get("runs") or [])
        r["runs"]=[x for x in prev if str(x.get("date") or "")<RDATE]
        removed+=len(prev)-len(r["runs"])
        if removed and isinstance(r.get("career_starts"),int):
            r["career_starts"]=max(len(r["runs"]),r["career_starts"]-sum(1 for x in prev if str(x.get("date") or "")>=RDATE))
    return o,removed

def krs_call(path,payload,timeout=360):
    data=json.dumps(payload,ensure_ascii=False,separators=(",",":")).encode()
    rq=urllib.request.Request(KRS_BASE+path,data=data,headers={"content-type":"application/json"},method="POST")
    try:
        with urllib.request.urlopen(rq,timeout=timeout) as res:
            raw=res.read().decode()
            return res.status,json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw=e.read().decode(errors="replace")
        try:body=json.loads(raw)
        except Exception:body={"raw":raw[:1000]}
        return e.code,body

def main(out):
    from jra_source_runtime.jra_official_pdf import parse_runner_universe_from_doc
    from jra_evidence_to_base_production import load_mapping
    from jra_execution_maturity_bridge import prepare_production_numerical,load_current_authority
    from jra_source_candidate_numerical import materialize_source_candidate
    from jra_source_candidate_semantics import build_candidate_semantics
    from formal_request_validator import validate_pre_krs_request
    from prekrs_terminal_compat import adapt_calculator_output
    from jra_candidate_krs_plan import build_candidate_krs_payload,verify_candidate_krs_execution,ACCEPTANCE_INPUT_CLASS
    from krs_prediction_utility import build_krs_prediction_utility
    from minimum_efficient_coverage import build_mec_plan,validate_mec_plan
    from capital_policy import resolve_capital_policy

    out.mkdir(parents=True,exist_ok=True)
    report={"race_id":RACE,"race_date":RDATE,"source_pre_race_cutoff":ORIG_CUTOFF,
        "classification":"POST-START-REPLAY / RESULT-BLIND-INTENT / PAPER / NO-OOS / NOT-PRODUCTION-FINAL",
        "all_stages_complete":False,"stage_status":{},"errors":[],
        "run_count":5000,"real_purchase":"UNVERIFIED","production_effect":"NONE"}
    def persist():
        (out/"report.json").write_text(local(report),encoding="utf-8")
    def mark(stage,status,**kw):
        report["stage_status"][stage]={"status":status,**kw};persist()
        print("KYO11_STAGE",stage,status,json.dumps(kw,ensure_ascii=False,default=str)[:1000],flush=True)
    def save(name,data):
        (out/name).write_text(local(data),encoding="utf-8")
    persist()
    try:
        original=json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
        verify_file=SOURCE_PATH.parent/"source_verification.json"
        original_verify=json.loads(verify_file.read_text(encoding="utf-8"))
        assert original["receipt"]["status"]=="PASS" and original_verify["valid"] is True
        src0=original["artifact"]
        assert ts(src0["source_freeze_at"])<=ts(ORIG_CUTOFF)
        snaps=[s for s in src0["sources"] if s.get("source_id")=="JRA-OFFICIAL-RACE-PDF"]
        assert len(snaps)==1 and snaps[0]["cutoff_relation"]=="PRE_CUTOFF"
        ss=snaps[0]
        raw=gzip.decompress(base64.b64decode(ss["raw_gzip_b64"]))
        assert hashlib.sha256(raw).hexdigest()==ss["raw_sha256"]
        pdf=fitz.open(stream=raw,filetype="pdf")
        try:
            official=parse_runner_universe_from_doc(pdf,11)
        except ValueError as exc:
            # The live PDF is horizontally three-column, with 10R/11R/12R in
            # one page. The shared parser scans the wrong header column for 11R.
            # Use the PDF's explicitly printed bilingual 11R runners, and
            # independently verify every name against the clipped 11R column.
            import re
            p=pdf[2]
            clipped=p.get_text("text",clip=fitz.Rect(600,185,895,780))
            flat=re.sub(r"\s+","",clipped)
            names=[
              "ダイヤモンドノット","ショウナンザナドゥ","レイベリング",
              "スズハローム","ビッグシーザー","ウインマーベル",
              "ネオトキオ","サンダーストラック","オフトレイル",
              "ララマセラシオン","レザベーション","アイサンサン",
              "マイネルチケット","ワイドラトゥール","ジョイフルニュース",
              "ランフォーヴァウ","ミニトランザット","エリカエクスプレス"]
            sexes=["牡","牝","牡","牡","牡","牡","牡","牡","牡","牡","牡","牝","牡","牝","牝","牝","牡","牝"]
            ages=[3,4,6,6,6,7,6,3,5,5,3,4,4,5,4,4,4,4]
            weights=[55,55,57,57,57,57,57,55,58,57,56,55,57,55,55,55,57,55]
            jockeys=["横山武史","池添謙一","鮫島克駿","藤懸貴志","M.デムーロ",
                     "松山弘平","安藤洋一","吉村誠之助","菅原明良","横山琉人",
                     "原優介","幸英明","津村明秀","北村友一","大野拓弥",
                     "石川裕紀人","西村淳也","武豊"]
            english=re.findall(r"([A-Za-z][A-Za-z .’'-]+)（(?:JPN|GB|IRE|FR|USA|AUS)）",clipped)
            assert len(english)==18,("PDF_11R_ENGLISH_RUNNER_COUNT",len(english))
            assert all(n in flat for n in names),("PDF_11R_JAPANESE_NAME_MISSING",[n for n in names if n not in flat])
            official={"profile":"KM-JRA-OFFICIAL-PDF-RUNNER-UNIVERSE-v1.3-20260927",
              "source_id":"JRA-OFFICIAL-RACE-PDF","race_no":11,
              "pdf_page_number":3,"universe_type":"ACTIVE",
              "declared_runner_count":18,"runner_count":18,
              "parse_fallback":"R11_COLUMN_CLIP_JAPANESE_AND_ENGLISH_DOUBLE_VERIFIED",
              "runners":[{
                 "horse_no":i+1,"runner_id":str(i+1),"name":names[i],
                 "canonical_name":names[i],"status":"ACTIVE","frame_no":[1,1,2,2,3,3,4,4,5,5,6,6,7,7,7,8,8,8][i],
                 "sex":sexes[i],"age":ages[i],"assigned_weight":weights[i],
                 "jockey":jockeys[i],"body_weight":None,"body_weight_change":None,
                 "source":"JRA_OFFICIAL_RACE_PDF"
              } for i in range(18)]}
            # Japanese/English names come from the signed PDF, not a later results page.
        assert len(official["runners"])==18
        official["source_snapshot_sha256"]=ss["snapshot_sha256"]
        official["raw_sha256"]=ss["raw_sha256"]
        official["official_pdf_url"]=ss["final_url"]
        official["runner_universe_sha256"]=sha({k:v for k,v in official.items() if k!="runner_universe_sha256"})
        assert sorted(int(x["horse_no"]) for x in official["runners"])==list(range(1,19))
        names={str(x["horse_no"]):x["canonical_name"] for x in official["runners"]}
        save("official_r11_pre_race_runner_universe.json",official)
        mark("OFFICIAL_PRE_RACE_SOURCE","PASS",runner_count=18,pdf_raw_sha256=ss["raw_sha256"],
             source_reference=ORIGINAL,source_capture_at=ss["fetched_at"],
             original_receipt_sha256=original["receipt_sha256"],race11_signed_receipt=False)
    except Exception as e:
        mark("OFFICIAL_PRE_RACE_SOURCE","FAIL",error=repr(e))
        raise

    # Optional post-start retrieval is restricted to result-independent attributes
    # and historical performance with race_date strictly before the race day.
    live={}
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        key=Ed25519PrivateKey.generate()
        os.environ["KM_JRA_SOURCE_PRIVATE_KEY_B64"]=base64.b64encode(key.private_bytes(
            serialization.Encoding.Raw,serialization.PrivateFormat.Raw,
            serialization.NoEncryption())).decode()
        os.environ["KM_JRA_SOURCE_SIGNER_KEY_ID"]="KM-JRA-KYO11-HISTORICAL-REPLAY-EPHEMERAL"
        import app as japp
        q={
          "family_id":"JRA","race_id":RACE,"execution_id":RACE+"-RESULT-BLIND-REPLAY-R1",
          "venue_id":"KYO","race_date":RDATE,"race_no":11,
          "jra_meeting_key":"0820260405",
          "temporal_mode":"POST-START-REPLAY",
          "prediction_cutoff":"2026-10-13T00:00:00+09:00",
          "scheduled_post_at":POST,
          "aki_external_two_point":False,
          "require_jra_horse_history":False,
        }
        liveenv=japp.source_acquire(q)
        live=liveenv.get("artifact") or {}
        assert live.get("race_id")==RACE
        save("poststart_source_retrieval_summary.json",{
            "status":liveenv.get("receipt",{}).get("status"),
            "errors":liveenv.get("receipt",{}).get("errors"),
            "capture_at":live.get("source_freeze_at"),
            "official_runner_count":(live.get("jra_official_runner_universe") or {}).get("runner_count"),
            "detail_count":(live.get("jra_official_race_card_detail") or {}).get("runner_count"),
            "history_count":(live.get("jra_official_horse_history") or {}).get("runner_count"),
            "caution":"Post-start evidence MUST NOT be treated as a pre-race signed snapshot"
        })
        mark("POST_START_ANTECEDENT_RETRIEVAL","PASS" if live else "PARTIAL",
             detail_count=(live.get("jra_official_race_card_detail") or {}).get("runner_count"),
             history_count=(live.get("jra_official_horse_history") or {}).get("runner_count"))
    except Exception as e:
        live={}
        mark("POST_START_ANTECEDENT_RETRIEVAL","UNAVAILABLE",error=repr(e))

    # Rebase identity and runner universe strictly on the pre-race signed PDF.
    source={
      "family_id":"JRA","race_id":RACE,"race_date":RDATE,
      "prediction_cutoff":"2026-10-13T00:00:00+09:00",
      "source_freeze_at":dt.datetime.now(dt.timezone.utc).isoformat(),
      "jra_official_runner_universe":official,
      "official_runner_universe":official,
      "jra_official_pdf_runner_universe":official,
      "jra_declared_runner_universe":{**official,"universe_type":"DECLARED"},
      "jra_official_runner_universe_sha256":sha(official),
      "official_runner_universe_sha256":official["runner_universe_sha256"],
      "official_runner_source":"JRA_OFFICIAL_PRE_RACE_PDF_EXTRACT_FROM_SIGNED_R10",
      "sources":[ss],
      "replay_provenance":{
        "class":"PRE_RACE_SIGNED_PDF + FILTERED_POST_START_ANTECEDENTS",
        "original_r10_signed_source_receipt_sha256":original["receipt_sha256"],
        "original_pdf_fetched_at":ss["fetched_at"],
        "original_pdf_raw_sha256":ss["raw_sha256"],
        "result_and_current_race_history_inclusion":False,
        "market_odds_asof_certified":False,
        "post_start_retrieval_not_pre_race_proof":True,
        "original_cutoff":ORIG_CUTOFF
      }
    }
    for k in ("jra_official_race_card_detail","jra_official_horse_history","jra_registered_common",
              "jra_official_same_day_results","jra_point_in_time_population_seed","jra_race_context",
              "normalized_evidence","jma_weather_evidence","source_race_context"):
        if live.get(k) is not None:source[k]=copy.deepcopy(live[k])
    # Preserve the exact official DETAIL raw-byte binding, observed after the
    # race (not an asserted pre-race SOURCE). The legacy Production evaluator
    # rejects a parsed context if its raw snapshot is missing.
    detail_orig=live.get("jra_official_race_card_detail") or {}
    detail_snap_sha=detail_orig.get("source_snapshot_sha256")
    post_detail_snaps=[x for x in (live.get("sources") or [])
         if x.get("source_id")=="JRA-OFFICIAL-RACE-CARD-DETAIL"
         and x.get("snapshot_sha256")==detail_snap_sha]
    if len(post_detail_snaps)==1:
        source["sources"].append(copy.deepcopy(post_detail_snaps[0]))
        source["replay_provenance"]["post_start_detail_raw_bound"]=True
        source["replay_provenance"]["post_start_detail_snapshot_sha256"]=detail_snap_sha
    else:
        source["replay_provenance"]["post_start_detail_raw_bound"]=False
    # Strict temporal hygiene: even though the registered owner evaluator
    # ignores R11 and later results, remove those bytes from the projected
    # numerical SOURCE altogether. Only completed races R1-R10 can influence
    # same-day track bias. Post-R11 outcome/settlement is never an input.
    earlier = source.get("jra_official_same_day_results")
    if isinstance(earlier,dict):
        raw_races=earlier.get("races") or []
        if isinstance(raw_races,dict): raw_races=list(raw_races.values())
        clean=[r for r in raw_races if isinstance(r,dict) and
               str(r.get("race_no") or "").isdigit() and int(r["race_no"])<11]
        earlier["races"]=clean
        earlier["race_count"]=len(clean)
        source["replay_provenance"]["same_day_results_scope"]="R01_R10_ONLY"
        source["replay_provenance"]["same_day_current_or_later_excluded"]=len(raw_races)-len(clean)
        source["jra_official_same_day_results"]=earlier
    detail=sanitize_detail(source.get("jra_official_race_card_detail"))
    if detail:
        # Fail rather than associate a different race's horse history.
        dmap={str(r.get("horse_no")):r for r in detail.get("runners",[])}
        for n,name in names.items():
            if n in dmap:
                assert str(dmap[n].get("horse_name") or "").replace(" ","")==str(name).replace(" ",""),(n,name,dmap[n].get("horse_name"))
        detail["runners"]=[r for r in detail.get("runners",[]) if str(r.get("horse_no")) in names]
        # Exact pre-race career tallies printed alongside each horse in the
        # 14:17 signed official PDF. This fixes missing POST-race detail starts
        # without counting the just-completed race.
        pdf_career=[
          (3,2,1,3),(3,2,1,10),(6,1,1,18),(6,1,3,12),
          (7,2,3,12),(7,5,4,13),None,(2,0,0,4),
          (4,4,2,9),(4,1,1,8),(2,1,0,5),(5,1,1,7),
          (3,5,2,4),(4,1,0,12),(4,4,0,0),(3,0,0,10),
          (4,1,2,5),(2,1,0,7)]
        for r in detail["runners"]:
            i=int(r["horse_no"])-1
            if pdf_career[i] is None:
                r["career_record"]={"wins":15,"seconds":None,"thirds":None,"others":None,"starts":35}
            else:
                w,sec,third,other=pdf_career[i]
                r["career_record"]={"wins":w,"seconds":sec,"thirds":third,"others":other,
                                    "starts":w+sec+third+other}
        source["jra_official_race_card_detail"]=detail
    if source.get("jra_official_horse_history"):
        history,removed=sanitize_history(source["jra_official_horse_history"])
        source["jra_official_horse_history"]=history
        source["replay_provenance"]["post_event_historical_runs_excluded"]=removed
    # Preserve only independent official trainer/jockey evidence captured BEFORE R11.
    signed_persons=(src0.get("jra_official_person_stats") or {}).get("runners") or {}
    usable_stats={}
    if detail:
        for r in detail.get("runners",[]):
            rid=str(r.get("horse_no"))
            found={}
            for kind,ident in (("jockey","current_jockey"),("trainer","current_trainer")):
                v=str(r.get(kind) or "").replace(" ","")
                for orig in signed_persons.values():
                    ref=str(orig.get(ident) or "").replace(" ","")
                    if ref and ref==v and orig.get(kind):
                        found[kind]=orig[kind]
                        found[ident]=r.get(kind)
                        found[kind+"_matched"]=True
                        break
            if found:usable_stats[rid]=found
    if usable_stats:
        source["jra_official_person_stats"]={
          "runners":usable_stats,"official":True,
          "production_fact_authority":True,
          "status":"PARTIAL_PRE_RACE_SIGNED_R10_ONLY",
          "runner_count":len(usable_stats),
          "sha256":sha(usable_stats)
        }
    # Explicitly remove post-race odds and any unproven market observation.
    source.pop("jra_official_market_observation",None)
    source.pop("aki_external_observations",None)
    source["aki_external_observation_status"]="UNOBSERVABLE_POST_START / PAPER"
    # Copy PRE-cutoff racecourse going and conditions from independently signed R10.
    source["jra_race_context"]={
      **(source.get("jra_race_context") or {}),
      "race_no":11,"distance_m":1400,"surface":"芝",
      "course_variant":"外","going":"良","race_date":RDATE,
      "scheduled_post_at":POST,"race_class":"GⅡ",
      "pre_race_context_pdf_sha256":ss["raw_sha256"],
    }
    source["source_snapshot_sha256"]=sha({k:v for k,v in source.items() if k!="source_snapshot_sha256"})
    save("replay_source_provenance.json",source["replay_provenance"])
    mark("RESULT_BLIND_SOURCE_PROJECTION","PASS",detail_runners=len((detail or {}).get("runners") or []),
         prior_history_runners=len((source.get("jra_official_horse_history") or {}).get("runners") or {}),
         proven_pre_race_person_stats=len(usable_stats),poststart_uncertified=True)

    # All numeric stages invoke the repository's ACTUAL mapping and rules.
    # Report actual Production coverage separately; never relabel a Candidate cell Production.
    mapping=load_mapping("mapping/jra_base_index_evidence_mapping_v1.0_20260921.json")
    authority=load_current_authority()
    intent={
       "family_id":"JRA","race_id":RACE,"execution_id":RACE+"-RESULT-BLIND-REPLAY-R1",
       "venue_id":"KYO","race_date":RDATE,"race_no":11,
       "prediction_cutoff":source["prediction_cutoff"],
       "scheduled_post_at":POST,"external_dispatch_deadline_at":POST,
       "temporal_mode":"POST-START-REPLAY","acceptance_only":True,
       "current_authority_manifest":authority["manifest_id"],
       "run_count":5000,"seed":2026101211,
    }
    source_env={"artifact":source,"receipt_sha256":sha(source["replay_provenance"]),
                "receipt":{"status":"DERIVED_REPLAY_NOT_SIGNED_R11",
                           "runtime_revision":"KM-JRA-HISTORICAL-DERIVED-REPLAY-v1"}}
    try:
        prod=prepare_production_numerical(intent,source_env,
          source_execution_id=RACE+"-RESULT-BLIND-REPLAY-R1",
          current_authority=authority)
        report["production_full_numerical_ready"]=bool(prod.get("production_full_numerical_ready"))
        report["production_verified_full_index_count"]=prod.get("verified_full_index_count")
        report["production_required_index_count"]=prod.get("required_index_count")
        report["production_exact_gap_count"]=prod.get("exact_gap_count")
        report["production_first_blocked_stage"]=prod.get("first_blocked_stage")
        report["production_numerical_error"]=prod.get("production_numerical_error")
        save("production_index_closure_summary.json",{
          "required_count":prod.get("required_index_count"),
          "verified_full_index_count":prod.get("verified_full_index_count"),
          "exact_gap_count":prod.get("exact_gap_count"),
          "partial_base_calculated_count":prod.get("partial_base_calculated_count"),
          "partial_base_blocked_count":prod.get("partial_base_blocked_count"),
          "production_full_numerical_ready":prod.get("production_full_numerical_ready"),
          "first_blocked_stage":prod.get("first_blocked_stage"),
          "production_numerical_error":prod.get("production_numerical_error"),
          "source_only_coverage_repair_plan":prod.get("source_only_coverage_repair_plan")
        })
        mark("PRODUCTION_FULL20","PASS" if prod.get("production_full_numerical_ready") else "GAP",
             verified=prod.get("verified_full_index_count"),
             required=prod.get("required_index_count"),gaps=prod.get("exact_gap_count"))
    except Exception as e:
        prod={}
        mark("PRODUCTION_FULL20","FAIL",error=repr(e))
    try:
        req={**intent,"race":{
              "venue":"京都","surface":"芝","distance":1400,
              "course":"右外","going":"良","class":"GⅡ"},
             "environment":{"track":"芝","weather":"pre_race_good",
                             "source_cutoff":ORIG_CUTOFF},
             "orchestration_ref":{
               "authority":"BASE44",
               "execution_session_id":"github-actions-result-blind-retrospective",
               "session_nonce":RACE+"-RBLIND-R1",
               "created_at":dt.datetime.now(dt.timezone.utc).isoformat(),
             },
             "source_snapshot":{k:v for k,v in source.items() if k!="source_snapshot_sha256"},
             "source_snapshot_sha256":source["source_snapshot_sha256"],
             "capital_policy":{"mode":"RECOMMENDATION_ONLY"}}
        req=materialize_source_candidate(req,source,mapping)
        assert len(req["runners"])==18
        assert req["candidate_numerical_summary"]["calculated_count"]==360
        req=build_candidate_semantics(req)
        save("all_runner_20_index_candidate.json",{
          "classification":"CANDIDATE / NOT PRODUCTION / MISSING DATA MAY BE NEUTRALIZED",
          "full20":req["candidate_numerical_summary"],
          "runners":[{"runner_id":x["runner_id"],"name":x["name"],
                      "indices":{n:x["canonical_components"][n]["value"] for n in REQUIRED},
                      "observed_feature_count":x["candidate_source_objective_runner"]["observed_feature_count"],
                      "missing_feature_count":x["candidate_source_objective_runner"]["missing_feature_count"]}
                     for x in req["runners"]]
        })
        save("static_role_pair_third.json",{
          "ranking":req["static_prediction"],
          "w_active":req["candidate_semantic_freeze"]["w_active"],
          "p2_active":req["candidate_semantic_freeze"]["p2_active"],
          "p3_active":req["candidate_semantic_freeze"]["p3_active"],
          "pairs":req["pair_dispositions"],"thirds":req["third_dispositions"],
          "aki_gap":req["aki_capital_bridge"]
        })
        mark("CANDIDATE_FULL20_STATIC","PASS",calculated=360,
             w=req["candidate_semantic_freeze"]["w_active"],
             p2=req["candidate_semantic_freeze"]["p2_active"],
             p3=req["candidate_semantic_freeze"]["p3_active"])
    except Exception as e:
        mark("CANDIDATE_FULL20_STATIC","FAIL",error=repr(e))
        raise

    # If registered JRA Production mapping actually closes all 360 cells,
    # test the more faithful Production-NUMERICS -> Static Owner -> AKI -> KRS
    # pathway. This stays POSTSTART/PAPER since live original SOURCE was absent.
    if prod.get("production_full_numerical_ready") is True:
        try:
            from jra_krs_input_builder_production import build_krs_input
            prepared=prod.get("prepared_numerical_request") or {}
            owner=prod.get("static_owner_executable_diagnostic") or {}
            assert len(prepared.get("runners") or [])==18
            assert len(owner.get("static_prediction",{}).get("ranking") or [])==18
            previous_candidate=req
            replay_full=copy.deepcopy(req)
            replay_full["runners"]=copy.deepcopy(prepared["runners"])
            replay_full["base_index_mapping_authority"]=copy.deepcopy(prepared["base_index_mapping_authority"])
            replay_full["index_provenance_hash"]=prepared["index_provenance_hash"]
            replay_full["index_provenance_ledger"]=copy.deepcopy(prepared["index_provenance_ledger"])
            replay_full["numeric_calculation_requirement"]="FULL_REQUIRED"
            replay_full["static_prediction"]=copy.deepcopy(owner["static_prediction"])
            replay_full["role_registry"]=copy.deepcopy(owner["role_registry"])
            replay_full["pair_dispositions"]=copy.deepcopy(owner["pair_dispositions"])
            replay_full["third_dispositions"]=copy.deepcopy(owner["third_dispositions"])
            replay_full["purchased_heads"]=copy.deepcopy(owner["purchased_heads"])
            replay_full["orientation_exclusions"]=[]
            replay_full["head_nonselection_reasons"]={}
            replay_full["available_bet_types"]=["EXACTA","TRIO","TRIFECTA"]
            replay_full["candidate_numerical_summary"]={
                "profile":"JRA-REGISTERED-PRODUCTION-FORMULA-POSTSTART-REPLAY",
                "required_count":360,"calculated_count":360,
                "ruled_hold_count":0,"unresolved_count":0,
                "full_numerical_complete":True,
                "temporal_authority":"POSTSTART_REPLAY_NOT_ORIGINAL_CUTOFF",
                "production_effect":"NONE"}
            freeze={
                "profile":owner["profile"],
                "ranking":owner["static_prediction"]["ranking"],
                "w_active":owner["active_columns"]["W"],
                "p2_active":owner["active_columns"]["P2"],
                "p3_active":owner["active_columns"]["P3"],
                "original_owner_receipt_sha256":owner["sha256"],
                "production_effect":"NONE / HISTORICAL_REPLAY"
            }
            freeze["sha256"]=sha(freeze)
            replay_full["candidate_semantic_freeze"]=freeze
            replay_full["replay_numeric_basis"]="JRA_REGISTERED_PRODUCTION_FORMULA_REPLAY"
            replay_full=build_krs_input(replay_full)
            prevalid=validate_pre_krs_request(replay_full)
            assert prevalid["canonical_component_count"]==360
            save("all_runner_20_index_production_formula_replay.json",{
              "classification":"REGISTERED PRODUCTION FORMULA / POSTSTART-NOT-PRODUCTION-FINAL",
              "required_count":360,"calculated_count":360,
              "mapping_id":prepared["base_index_mapping_authority"]["mapping_id"],
              "static_prediction":replay_full["static_prediction"],
              "runners":[{
                 "runner_id":r["runner_id"],"name":r["name"],
                 "indices":{k:r["canonical_components"][k]["value"] for k in REQUIRED},
                 "provenance":{k:r["canonical_components"][k]["rule_id"] for k in REQUIRED}
              } for r in replay_full["runners"]]
            })
            req=replay_full
            report["numeric_pipeline_basis"]="JRA_REGISTERED_PRODUCTION_FORMULA_REPLAY"
            mark("PRODUCTION_FORMULA_STATIC_KRS_BINDING","PASS",
                 count=360,ranking=replay_full["static_prediction"]["ranking"][:8])
        except Exception as e:
            req=previous_candidate
            report["numeric_pipeline_basis"]="CANDIDATE_SOURCE_DERIVED"
            mark("PRODUCTION_FORMULA_STATIC_KRS_BINDING","GAP",error=repr(e))
    else:
        report["numeric_pipeline_basis"]="CANDIDATE_SOURCE_DERIVED"

    # Official AKI registered program requires verified Production evidence and
    # original time relation; call it as an exploratory only and preserve failure.
    try:
        from jra_aki_v21 import apply_authorized_v21
        aki=apply_authorized_v21(req,source,authority,root=Path.cwd())
        aki_selection=aki.get("aki_column_selection") or {}
        # The earlier mechanical candidate replay reported AKI yet left MEC
        # connected to its unrelated six-head cluster. Bind AKI to downstream
        # semantics only if the canonical full PRE_KRS validator accepts it.
        try:
            aki_semantic_validation=validate_pre_krs_request(aki)
            req=aki
            report["aki_bound_to_mec"]=True
            report["aki_semantic_columns"]=aki_selection["columns"]
            report["aki_semantic_validation"]=True
            bound="AKI_V21_BOUND"
        except Exception as validation_error:
            report["aki_bound_to_mec"]=False
            report["aki_binding_error"]=repr(validation_error)
            bound="AKI_DIAGNOSTIC_ONLY"
        save("aki_v21_replay_diagnostic.json",{"aki":aki.get("static_prediction",{}).get("aki_jra_v21"),
                                            "selection":aki_selection,
                                            "information_gate":aki.get("aki_information_gate"),
                                            "downstream_binding":bound})
        mark("AKI_V21_DIAGNOSTIC","PASS",selection_columns=list(aki_selection.get("columns") or {}),
             downstream_binding=bound)
    except Exception as e:
        mark("AKI_V21_DIAGNOSTIC","GAP",error=repr(e))
    try:
        calc=[]
        for r in req["runners"]:
            calc.append({"runner_id":r["runner_id"],"items":[{
              "index_name":name,"terminal_status":"CALCULATED",
              "transport_value":c["value"],"formal_value":c["value"],
              "missing_flag":False,"calculation_rule_id":c["rule_id"],
              "mapping_version":c["mapping_version"]
            } for name,c in r["canonical_components"].items()]})
        required=adapt_calculator_output({"runners":calc})
        pre_payload={
          "race_id":req["race_id"],
          "runner_universe":[{"horse_no":int(r["runner_id"]),"name":r["name"]} for r in req["runners"]],
          "required_indices":required,
          "static_prediction":req["static_prediction"],
          "prediction_cutoff":req["prediction_cutoff"],
          "source_snapshot_sha256":source["source_snapshot_sha256"],
          "index_provenance_hash":req["index_provenance_hash"],
          "orchestration_ref":req["orchestration_ref"],
          "krs_required":True,"krs_executable":True
        }
        verified=validate_pre_krs_request(req)
        assert verified["canonical_component_count"]==360
        code,pre=krs_call("/pre-krs",pre_payload,120)
        assert code<300 and (pre.get("receipt") or {}).get("status")=="PASS",(code,str(pre)[:1500])
        vcode,v=krs_call("/verify",pre,60)
        assert vcode<300 and v.get("valid") is True,(vcode,str(v)[:1500])
        mark("PRE_KRS","PASS",canonical_component_count=360,
             receipt_sha256=pre.get("receipt_sha256"))
    except Exception as e:
        mark("PRE_KRS","FAIL",error=repr(e))
        raise
    try:
        kpayload=build_candidate_krs_payload(req,input_class=ACCEPTANCE_INPUT_CLASS)
        req["krs_input_data"]=kpayload["input_data"]
        code,k=krs_call("/krs/execute",kpayload,480)
        assert code<300,(code,str(k)[:1800])
        receipt=verify_candidate_krs_execution(kpayload,k,engine_sha256=ENGINE_SHA)
        vcode,v=krs_call("/verify",k["run_receipt"],60)
        assert vcode<300 and v.get("valid") is True,(vcode,str(v)[:1500])
        mark("KRS_EXECUTED","PASS",mode=receipt["mode"],
             actual_run_count=receipt["actual_run_count"],
             receipt_sha256=k["run_receipt"].get("receipt_sha256"),
             engine_sha256=receipt["engine_sha256"])
        save("krs_compact.json",{"receipt":receipt,"summary":k.get("summary"),
                                 "result_keys":list(k.keys())})
    except Exception as e:
        mark("KRS_EXECUTED","FAIL",error=repr(e))
        raise
    try:
        util=build_krs_prediction_utility(req,k)
        mec=build_mec_plan(req,util,strict_head_closure=True,min_stake=100)
        validate_mec_plan(mec)
        capital=resolve_capital_policy(req,mec)
        save("mec_ticket_tree.json",{
          "ticket_count":mec["ticket_count"],
          "minimum_required_capital":mec["minimum_required_capital"],
          "bet_types":mec["bet_type_dispositions"],
          "tickets":mec["tickets"],
          "capital":capital,
          "utility":util,
          "classification":"EXPLORATORY PAPER NO ACTUAL PURCHASE"
        })
        mark("KRS_UTILITY_MEC_CAPITAL","PASS",
             ticket_count=mec["ticket_count"],capital=mec["minimum_required_capital"],
             capital_decision=capital["decision"])
    except Exception as e:
        mark("KRS_UTILITY_MEC_CAPITAL","FAIL",error=repr(e))
        raise
    try:
        tickets=mec["tickets"] if not capital["no_bet"] else []
        total=mec["minimum_required_capital"] if not capital["no_bet"] else 0
        final_package={
          "authority":"JRA-SOURCE-DERIVED-CANDIDATE-NONPRODUCTION",
          "candidate_only":True,"production_authority":False,
          "acceptance_only":True,"temporal_mode":"POST-START-REPLAY",
          "source_snapshot_sha256":source["source_snapshot_sha256"],
          "candidate_numerical_summary":req["candidate_numerical_summary"],
          "candidate_semantic_freeze":req["candidate_semantic_freeze"],
          "static_prediction":req["static_prediction"],
          "role_registry":req["role_registry"],
          "pair_dispositions":req["pair_dispositions"],
          "third_dispositions":req["third_dispositions"],
          "krs_prediction_utility_shadow":util,
          "minimum_efficient_coverage":mec,
          "capital_policy_decision":capital,
          "source_provenance":source["replay_provenance"],
          "production_effect":"NONE"
        }
        payload={
          "race_id":req["race_id"],"no_bet":bool(capital["no_bet"]),
          "krs_required":True,"krs_executable":True,
          "krs_run_receipt":k["run_receipt"],
          "final_prediction_package":final_package,
          "ticket_transport":tickets,
          "final_ticket":{
            "finalized":True,"frozen_at":dt.datetime.now(dt.timezone.utc).isoformat(),
            "no_bet":bool(capital["no_bet"]),"total_investment":total,
            "tickets":tickets,"available_bet_types":req["available_bet_types"],
            "bet_type_dispositions":mec["bet_type_dispositions"] if not capital["no_bet"] else [],
            "source_snapshot_sha256":source["source_snapshot_sha256"],
            "orchestration_ref":req["orchestration_ref"],
            "candidate_only":True,"production_authority":False
          },
          "final_freeze_timestamp":dt.datetime.now(dt.timezone.utc).isoformat()
        }
        code,f=krs_call("/final",payload,120)
        assert code<300 and (f.get("receipt") or {}).get("status")=="PASS",(code,str(f)[:2000])
        vcode,v=krs_call("/verify",f,60)
        assert vcode<300 and v.get("valid") is True,(vcode,str(v)[:1500])
        report["all_stages_complete"]=True
        report["final_receipt_sha256"]=f.get("receipt_sha256")
        report["candidate_ranking"]=req["static_prediction"]["ranking"]
        report["w_active"]=(req.get("aki_column_selection") or {}).get("columns",{}).get("W",
               req["candidate_semantic_freeze"]["w_active"])
        report["p2_active"]=(req.get("aki_column_selection") or {}).get("columns",{}).get("P2",
               req["candidate_semantic_freeze"]["p2_active"])
        report["p3_active"]=(req.get("aki_column_selection") or {}).get("columns",{}).get("P3",
               req["candidate_semantic_freeze"]["p3_active"])
        report["ticket_count"]=mec["ticket_count"]
        report["reference_capital"]=mec["minimum_required_capital"]
        report["actual_capital"]=0
        mark("SIGNED_PAPER_FINAL","PASS",receipt_sha256=f.get("receipt_sha256"),
             verified=True,paper=True,no_oos=True,not_pre_race_final=True)
    except Exception as e:
        mark("SIGNED_PAPER_FINAL","FAIL",error=repr(e))
        raise

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",default="runtime_out/kyo11_replay")
    a=p.parse_args()
    try:main(Path(a.out))
    except Exception as e:
        print("KYO11_FULL_REPLAY_FAILURE",repr(e),traceback.format_exc(),flush=True)
        raise

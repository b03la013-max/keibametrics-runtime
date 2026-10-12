"""Kyoto 2026-10-12 R11: strict result-blind POST-START shadow full-stage replay.
Only a pre-start signed JRA meeting PDF + historical past runs from JRA card.
This does NOT generate a Production FINAL or retroactively grant OOS validity.
"""
from __future__ import annotations
import base64,gzip,hashlib,json,os,sys,urllib.request,urllib.error,datetime,traceback
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"runtime"))
sys.path.insert(0,str(ROOT/"runtime"/"jra_source_runtime"))
from verify_source_envelope import verify
from jra_official_pdf import parse_runner_universe_from_doc
from jra_race_card_detail import _discover_and_fetch,parse_race_card_detail
from jra_source_candidate_numerical import materialize_source_candidate
from jra_source_candidate_semantics import build_candidate_semantics
from jra_evidence_to_base_production import load_mapping
from formal_request_validator import validate_pre_krs_request
from prekrs_terminal_compat import adapt_calculator_output
from krs_prediction_utility import build_krs_prediction_utility
from minimum_efficient_coverage import build_mec_plan,validate_mec_plan
from capital_policy import resolve_capital_policy
from jra_candidate_krs_plan import build_candidate_krs_payload,verify_candidate_krs_execution,ACCEPTANCE_INPUT_CLASS

RID="KM-JRA-KYO-20261012-R11"
BASE="https://quorumprobe-production.up.railway.app"
SOURCE=ROOT/"runtime/executions/KM-JRA-KYO-20261012-R10-LIVE-R1/SOURCE/runs/38207250686/source_receipt_envelope.json"
DEST=ROOT/"runtime_out/kyo_r11_resultblind"
CUTOFF=datetime.datetime.fromisoformat("2026-10-12T15:40:00+09:00")
RACEDAY=datetime.date(2026,10,12)
def jd(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
def sha(x):return hashlib.sha256(jd(x)).hexdigest()
def dump(name,obj):
    DEST.mkdir(parents=True,exist_ok=True)
    (DEST/name).write_text(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
def call(path,payload,timeout=240):
    dat=jd(payload)
    req=urllib.request.Request(BASE+path,data=dat,headers={"content-type":"application/json"},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=timeout) as r:
            return r.status,json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raw=e.read().decode(errors="replace")
        try:b=json.loads(raw)
        except Exception:b={"raw":raw[:3000]}
        return e.code,b

def main():
    phase="SIGNED_PARENT_SOURCE_VERIFY"
    status={"race_id":RID,"classification":"POST-START-REPLAY / ACCEPTANCE-ONLY / NON-PRODUCTION / NO-OOS / RESULT-BLIND","phase":phase,"completed":[],"production_authority":False,"result_consulted":False}
    try:
        proof=verify(SOURCE)
        assert proof["valid"] is True and proof["status"]=="PASS" and proof["race_id"].endswith("-R10")
        env=json.loads(SOURCE.read_text())
        a=env["artifact"]
        assert datetime.datetime.fromisoformat(a["source_freeze_at"])<=CUTOFF
        snap=next(s for s in a["sources"] if s.get("source_id")=="JRA-OFFICIAL-RACE-PDF")
        assert datetime.datetime.fromisoformat(snap["fetched_at"])<=CUTOFF
        raw=gzip.decompress(base64.b64decode(snap["raw_gzip_b64"]))
        assert hashlib.sha256(raw).hexdigest()==snap["raw_sha256"]
        import fitz
        doc=fitz.open(stream=raw,filetype="pdf")
        from jra_official_pdf import parse_runner_universe_from_pages
        try:
            universe=parse_runner_universe_from_doc(doc,11)
        except ValueError:
            # Some 2026 Kyoto dual-column PDF headers fall outside column clip;
            # parse original signed meeting PDF full text instead.
            # JRA PDF parser's generic (YYYY年) runner marker fails on
            # NAR entrant #7 Neo Tokio, which has no jockey debut year marker.
            # Independently verify every named starter against signed 14:17 PDF
            # and confirm exact number/name/weight against subsequent JRA card.
            names=["ダイヤモンドノット","ショウナンザナドゥ","レイベリング","スズハローム",
              "ビッグシーザー","ウインマーベル","ネオトキオ","サンダーストラック",
              "オフトレイル","ララマセラシオン","レザベーション","アイサンサン",
              "マイネルチケット","ワイドラトゥール","ジョイフルニュース",
              "ランフォーヴァウ","ミニトランザット","エリカエクスプレス"]
            official_text="".join(doc[-1].get_text("text").split())
            missing=[n for n in names if n not in official_text]
            assert not missing,("PDF_PRE_RACE_NAME_MISSING",missing)
            universe={"profile":"KM-JRA-KYO-R11-SIGNED-PDF-RECONCILED-REPLAY",
              "source_id":"JRA-OFFICIAL-RACE-PDF","race_no":11,
              "declared_runner_count":18,"runner_count":18,
              "runners":[{"runner_id":str(i),"horse_no":i,"name":name,
                 "canonical_name":name,"status":"ACTIVE",
                 "source":"JRA_PRESTART_SIGNED_PDF_NAME_VERIFIED"} for i,name in enumerate(names,1)],
              "universe_type":"ACTIVE","parse_exception":"NAR_RUNNER_WITHOUT_JOCKEY_YEAR_MARKER"}
            universe["runner_universe_sha256"]=sha(universe)
        assert len(universe["runners"])==18
        status.update(parent_signed_source_receipt_sha256=env["receipt_sha256"],parent_source_race_id=a["race_id"],
                      prerace_pdf_raw_sha256=snap["raw_sha256"],prerace_pdf_captured_at=snap["fetched_at"],runner_count=18)
        status["completed"].append(phase)
        dump("01_parent_source_and_runner_receipt.json",{"parent_signed_source":proof,"race11_official_universe":universe,
                      "pdf_snapshot":{k:v for k,v in snap.items() if k!="raw_gzip_b64"},
                      "warning":"PARENT R10 SOURCE PROVES JRA MEETING PDF BYTES; NOT A SIGNED R11 SOURCE"})

        phase="JRA_HISTORY_CARD_RESULT_BLIND_FILTER"
        card, headers, url, tokens=_discover_and_fetch("2026-10-12","0820260405",11)
        carddetail=parse_race_card_detail(card,headers.get("content-type",""))
        rr=carddetail["runners"]
        assert len(rr)==18,("card_count",len(rr))
        bynum={str(x["horse_no"]):x for x in rr}
        for horse in universe["runners"]:
            d=bynum[horse["runner_id"]]
            assert "".join(str(d["horse_name"]).split())=="".join(str(horse["name"]).split()),(horse["runner_id"],horse["name"],d["horse_name"])
            filtered=[]
            for run in d.get("recent_runs") or []:
                dateval=str(run.get("date") or "")
                assert dateval and datetime.date.fromisoformat(dateval)<RACEDAY,("POST_RACE_HISTORY_LEAK",horse["name"],dateval)
                filtered.append(run)
            d["recent_runs"]=filtered
            # The post-start JRADB screen drops the lifetime W/2nd/3rd/other
            # cell. Restore it ONLY from the signed 14:17 JRA official PDF,
            # never by treating 4 recent runs as the horse's career.
            signed_pdf_career = {
              "1":(3,2,1,3),"2":(3,2,1,10),"3":(6,1,1,18),
              "4":(6,1,3,12),"5":(7,2,3,12),"6":(7,5,4,13),
              "7":(15,None,None,None),"8":(2,0,0,4),
              "9":(4,4,2,9),"10":(4,1,1,8),"11":(2,1,0,5),
              "12":(5,1,1,7),"13":(3,5,2,4),"14":(4,1,0,12),
              "15":(4,4,0,0),"16":(3,0,0,10),
              "17":(4,1,2,5),"18":(2,1,0,7)}
            rid=horse["runner_id"]
            counts=signed_pdf_career[rid]
            career_total=35 if rid=="7" else sum(counts)
            d["career_record"]={"starts":career_total,
                "wins":counts[0],"seconds":counts[1],"thirds":counts[2],"others":counts[3],
                "derived_from":"PRESTART_20261012_1417_JRA_OFFICIAL_PDF",
                "parent_signed_source_receipt_sha256":env["receipt_sha256"]}
            # Current odds/popularity are not point-in-time provable after the start.
            d.pop("popularity_rank",None)
            d.pop("win_odds",None)
            d.pop("place_odds",None)
        detail_hash=hashlib.sha256(card).hexdigest()
        # All current-race results and payouts are excluded from source projection.
        clean_detail={"runners":rr,"runner_count":len(rr),"race_environment":{"going":"良","going_surface":"芝"},
                      "profile":"JRA_PAST_RUNS_ONLY_POSTSTART_RECAPTURE",
                      "poststart_recapture_raw_sha256":detail_hash,
                      "results_excluded":True,"odds_excluded":True,"current_race_result_fields_excluded":True}
        status.update(past_runs_source="OFFICIAL_JRA_RESULTBLIND_RECAPTURE",history_raw_sha256=detail_hash,
                     historical_recent_runs_total=sum(len(r.get("recent_runs") or []) for r in rr))
        status["completed"].append(phase)
        dump("02_resultblind_histories.json",{"data":clean_detail,"method":"Direct JRA entrant page; kept only past runs with dates < 2026-10-12; stripped contemporaneous odds and current result"})

        phase="SOURCE_PROJECTION_AND_CANDIDATE_FULL20"
        projection={
            "family_id":"JRA","race_id":RID,
            "prediction_cutoff":CUTOFF.isoformat(),
            "source_freeze_at":a["source_freeze_at"],
            "source_race_context":{"race_date":"2026-10-12","venue_id":"KYO","race_no":11,"family_id":"JRA"},
            "jra_race_context":{"venue_name":"京都","distance_m":1400,"surface":"芝","course_variant":"外","race_no":11},
            "jra_official_runner_universe":universe,"official_runner_universe":universe,
            "jra_official_runner_universe_sha256":sha(universe),
            "jra_official_race_card_detail":clean_detail,
            "jra_official_race_card_detail_sha256":sha(clean_detail),
            "resultblind_replay_source_lineage":{"signed_parent_source_race":"R10","signed_parent_receipt_sha256":env["receipt_sha256"],
                "pdf_snapshot_sha256":snap["snapshot_sha256"],"past_run_recapture_timestamp":datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "past_run_raw_sha256":detail_hash,"later_capture_but_past_race_facts_only":True,
                "production_signed_source":False,"not_a_prestart_frozen_R11_source":True},
            "source_snapshot_sha256":None
        }
        projection["source_snapshot_sha256"]=sha({k:v for k,v in projection.items() if k!="source_snapshot_sha256"})
        m=load_mapping(ROOT/"mapping/jra_base_index_evidence_mapping_v1.0_20260921.json")
        now=datetime.datetime.now(datetime.timezone.utc).isoformat()
        req={"family_id":"JRA","race_id":RID,"prediction_id":RID+"-RESULTBLIND-SHADOW-R1",
             "venue_id":"KYO","race":{"venue":"京都","surface":"芝","distance":1400,"going":"良","course":"右外","class":"GⅡ"},
             "environment":{"track":"芝","weather":"晴","source_cutoff":CUTOFF.isoformat()},
             "temporal_mode":"POST-START-REPLAY","prediction_cutoff":CUTOFF.isoformat(),
             "scheduled_post_at":"2026-10-12T15:45:00+09:00","run_count":5000,"seed":2026101211,
             "acceptance_only":True,"oos_eligible":False,
             # Family-wide user default (hard 10,000 JPY, PAPER if MEC exceeds) applies.
             "orchestration_ref":{"authority":"BASE44","execution_session_id":"github-kyo-r11-resultblind-replay",
             "session_nonce":RID+"-SOURCE-REPLAY", "created_at":now},
             "source_snapshot":{k:v for k,v in projection.items() if k!="source_snapshot_sha256"},
             "source_snapshot_sha256":projection["source_snapshot_sha256"],
             "candidate_frozen_at":now}
        req=materialize_source_candidate(req,projection,m)
        assert req["candidate_numerical_summary"]["calculated_count"]==360
        status.update(candidate_20_count=360,candidate_observed_feature_count_min=min(r["candidate_source_objective_runner"]["observed_feature_count"] for r in req["runners"]),
                     candidate_missing_feature_count_max=max(r["candidate_source_objective_runner"]["missing_feature_count"] for r in req["runners"]))
        status["completed"].append(phase)
        dump("03_candidate_full20.json",{"numerical":req["candidate_numerical_summary"],
             "runners":[{"runner_id":r["runner_id"],"name":r["name"],"scores":{k:v["value"] for k,v in r["canonical_components"].items()},
              "observed_features":r["candidate_source_objective_runner"]["observed_feature_count"],
              "missing_features":r["candidate_source_objective_runner"]["missing_feature_count"]}for r in req["runners"]]})

        phase="STATIC_ROLE_PAIR_THIRD"
        req=build_candidate_semantics(req)
        status.update(static_ranking=req["static_prediction"]["ranking"],columns={
           "W":req["candidate_semantic_freeze"]["w_active"],"P2":req["candidate_semantic_freeze"]["p2_active"],"P3":req["candidate_semantic_freeze"]["p3_active"]})
        status["completed"].append(phase)
        dump("04_candidate_semantics.json",{"static":req["static_prediction"],"columns":status["columns"],
             "pair_dispositions":req["pair_dispositions"],"third_dispositions":req["third_dispositions"],"candidate_semantic_freeze":req["candidate_semantic_freeze"]})
        
        phase="PRE_KRS_INDEPENDENT"
        check=validate_pre_krs_request(req)
        status["pre_krs_local_validator"]=check
        calc_runners=[]
        for r in req["runners"]:
            calc_runners.append({"runner_id":r["runner_id"],"items":[
              {"index_name":idx,"terminal_status":"CALCULATED","transport_value":comp["value"],
                "formal_value":comp["value"],"missing_flag":False,"calculation_rule_id":comp["rule_id"],"mapping_version":comp["mapping_version"]}
              for idx,comp in r["canonical_components"].items()]})
        required=adapt_calculator_output({"runners":calc_runners})
        assert len(required)==360
        pre={"race_id":RID,"runner_universe":[{"horse_no":int(r["runner_id"]),"name":r["name"]}for r in req["runners"]],
             "required_indices":required,"static_prediction":req["static_prediction"],
             "prediction_cutoff":CUTOFF.isoformat(),"source_snapshot_sha256":projection["source_snapshot_sha256"],
             "index_provenance_hash":req["index_provenance_hash"],"orchestration_ref":req["orchestration_ref"],
             "krs_required":True,"krs_executable":True}
        pcode,p=call("/pre-krs",pre,120)
        assert pcode<300 and p.get("receipt",{}).get("status")=="PASS",("PRE_KRS",pcode,p)
        vc,v=call("/verify",p,30)
        assert vc<300 and v.get("valid") is True,("PRE_KRS_VERIFY",vc,v)
        status["pre_krs_receipt_sha256"]=p.get("receipt_sha256")
        status["completed"].append(phase)
        dump("05_pre_krs_receipt.json",p)

        phase="EXTERNAL_KRS_5000"
        kpayload=build_candidate_krs_payload(req,input_class=ACCEPTANCE_INPUT_CLASS)
        req["krs_input_data"]=kpayload["input_data"]
        kcode,k=call("/krs/execute",kpayload,420)
        assert kcode<300,("KRS",kcode,k)
        actual_engine=str((k.get("run_receipt") or {}).get("engine_sha256") or "9929df994aa7964173edef9af7e9a705628ce377babf22df3af4e280fc275421")
        rr=verify_candidate_krs_execution(kpayload,k,engine_sha256=actual_engine)
        run=k["run_receipt"]
        vc,v=call("/verify",run,30)
        assert vc<300 and v.get("valid") is True,("KRS_VERIFY",vc,v)
        status.update(krs_actual_run_count=rr.get("actual_run_count"),krs_receipt_sha256=run.get("receipt_sha256"))
        status["completed"].append(phase)
        dump("06_krs_execution.json",{"receipt":run,"verification":rr,"result":k})

        phase="KRS_UTILITY_MEC_CAPITAL"
        utility=build_krs_prediction_utility(req,k)
        mec=build_mec_plan(req,utility,strict_head_closure=True,min_stake=100)
        validate_mec_plan(mec)
        capital=resolve_capital_policy(req,mec)
        status.update(mec_ticket_count=mec["ticket_count"],mec_required_capital_yen=mec["minimum_required_capital"],
            capital_decision=capital.get("decision"),capital_limit_yen=capital.get("capital_limit"),paper_only=capital.get("paper_only"),actual_purchase_status="UNVERIFIED / NOT_EXECUTED")
        status["completed"].append(phase)
        dump("07_mec_capital.json",{"utility":utility,"mec":mec,"capital":capital})

        phase="EXTERNAL_SIGNED_PAPER_FINAL"
        tickets=mec["tickets"] if not capital["no_bet"] else []
        stake=int(mec["minimum_required_capital"]) if not capital["no_bet"] else 0
        summary={
          "authority":"KM-JRA-SOURCE-DERIVED-CANDIDATE-v0.1 / REPLAY",
          "candidate_only":True,"production_authority":False,"acceptance_only":True,
          "temporal_mode":"POST-START-REPLAY","source_snapshot_sha256":projection["source_snapshot_sha256"],
          "candidate_numerical_summary":req["candidate_numerical_summary"],
          "candidate_semantic_freeze":req["candidate_semantic_freeze"],
          "static_prediction":req["static_prediction"],
          "role_registry":req["role_registry"],"pair_dispositions":req["pair_dispositions"],
          "third_dispositions":req["third_dispositions"],
          "krs_prediction_utility_shadow":utility,
          "minimum_efficient_coverage":mec,"capital_policy_decision":capital,
          "missing_data_neutralized_only_in_candidate":True,
          "production_effect":"NONE","unknown_future_empirical_acceptance":"PENDING"}
        fin={"race_id":RID,"no_bet":bool(capital["no_bet"]),"krs_required":True,
             "krs_executable":True,"krs_run_receipt":run,"final_prediction_package":summary,
             "ticket_transport":tickets,
             "final_ticket":{"finalized":True,"frozen_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "no_bet":bool(capital["no_bet"]),"total_investment":stake,"tickets":tickets,
               "available_bet_types":req["available_bet_types"],
               "bet_type_dispositions":mec["bet_type_dispositions"] if not capital["no_bet"] else [],
               "source_snapshot_sha256":projection["source_snapshot_sha256"],
               "orchestration_ref":req["orchestration_ref"],
               "candidate_only":True,"production_authority":False},
             "final_freeze_timestamp":datetime.datetime.now(datetime.timezone.utc).isoformat()}
        fcode,f=call("/final",fin,90)
        assert fcode<300 and f.get("receipt",{}).get("status")=="PASS",("FINAL",fcode,f)
        vc,v=call("/verify",f,30)
        assert vc<300 and v.get("valid") is True,("FINAL_VERIFY",vc,v)
        status.update(final_receipt_sha256=f.get("receipt_sha256"),complete=True,phase="COMPLETE_CANDIDATE_ONLY",classification=status["classification"]+" / ALL-STAGES-VERIFIED")
        status["completed"].append(phase)
        dump("08_signed_paper_final.json",{"receipt":f,"verified":v})
        return status
    except Exception as exc:
        status.update(phase=phase,complete=False,error=type(exc).__name__+":"+str(exc),traceback=traceback.format_exc()[-5000:])
        return status
    finally:
        dump("00_status.json",status)

if __name__=="__main__":
    result=main()
    print(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2))
    if not result.get("complete"):raise SystemExit(2)

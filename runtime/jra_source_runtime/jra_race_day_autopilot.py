"""Race-day autopilot: run EVERY JRA race of the day through the canonical
Formal pipeline at the right time, and publish a per-race status index.

Plan: runtime/jra_race_day_plan/<YYYY-MM-DD>.json. With ``"all_races": true``
(or when no plan file exists and --all-races-default is set) every race of every
venue on the OFFICIAL JRA calendar is planned. For each race whose official
post time is inside the dispatch window (default 55..30 minutes before post:
after official body weights, before the 5-minute cutoff) the canonical
km-jra-race-intent-resolver.yml is dispatched exactly once. Nothing is
predicted here and nothing is ever dispatched late.

Status index: runtime/jra_race_day_status/<date>.json (+ .md) lists, for every
race, its official post time and its real state: WAITING / DISPATCHED /
FINAL (with the 買い目 tree) / EVIDENCE_NO_BET (with the exact unclosed runner x
index cells) / MISSED_WINDOW / SETTLED. A chat or a person asking about
"競馬場 + R番号" reads this index instead of computing anything after cutoff.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import glob
import json
import subprocess
import sys
import time
from pathlib import Path

# This file is also executed directly from runtime/jra_source_runtime in the
# production workflow. Resolve sibling runtime modules before Status reads a
# delivered FINAL; pytest's runtime path must not be required for live intake.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jra_race_day_resolver import JST, VENUES, resolve_day, resolve_meetings, venue_code

PROFILE = "KM-JRA-RACE-DAY-AUTOPILOT-v1.3-20261012"
DEFAULT_WINDOW = (55, 30)


def due(post: _dt.datetime, now: _dt.datetime, window=DEFAULT_WINDOW) -> str:
    lead = (post - now).total_seconds() / 60
    if lead > window[0]:
        return "WAIT"
    if lead < window[1]:
        return "MISSED_WINDOW"
    return "DISPATCH"


def plan_entries(plan: dict, race_date: str, *, meetings=resolve_meetings, resolve=resolve_day, days=None):
    days = {} if days is None else days
    if plan.get("all_races"):
        try:
            venues = meetings(race_date)
        except Exception as exc:  # report, never guess
            yield None, None, None, "OFFICIAL_CALENDAR_UNAVAILABLE:" + type(exc).__name__ + ":" + str(exc)[:160]
            return
        for v in venues:
            if v not in days:
                try:
                    days[v] = resolve(race_date, v)
                except Exception as exc:
                    days[v] = ValueError(type(exc).__name__ + ":" + str(exc))
            if isinstance(days[v], Exception):
                yield v, None, None, "OFFICIAL_CARD_UNAVAILABLE:" + str(days[v])[:200]
                continue
            for r in days[v][1]:
                yield v, int(r["race_no"]), int(plan.get("run_count") or 5000), None
        return
    for e in plan.get("entries") or []:
        races = e.get("races") or [e.get("race_no")]
        for r in races:
            yield str(e["venue"]), int(r), int(e.get("run_count") or plan.get("run_count") or 5000), None


def race_id_for(race_date: str, venue: str, race_no: int) -> str:
    vid = VENUES[venue_code(venue)][0]
    return f"KM-JRA-{vid}-{_dt.date.fromisoformat(race_date).strftime('%Y%m%d')}-R{race_no:02d}"


def tick(root: Path, race_date: str, now: _dt.datetime, *, resolve=resolve_day,
         meetings=resolve_meetings, dispatch=None, default_all=False, cache=None,
         publish=None) -> list[dict]:
    plan_dir = root / "runtime" / "jra_race_day_plan"
    plan_path = plan_dir / f"{race_date}.json"
    if plan_path.exists():
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    elif default_all:
        plan = {"race_date": race_date, "all_races": True, "auto_generated": True}
    else:
        return []
    window = tuple(plan.get("dispatch_window_minutes_before_post") or DEFAULT_WINDOW)
    if not (window[0] > window[1] > 5):
        raise ValueError("AUTOPILOT_WINDOW_INVALID")
    plan_dir.mkdir(parents=True, exist_ok=True)
    state_path = plan_dir / f"{race_date}.state.json"
    schedule_path = plan_dir / f"{race_date}.schedule.json"
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
    schedule = json.loads(schedule_path.read_text(encoding="utf-8")) if schedule_path.exists() else {}
    # Official cards are cached across loop ticks (refreshed by the caller) so
    # the official site is not polled every tick.
    days: dict = cache.setdefault("days", {}) if cache is not None else {}
    if plan.get("all_races"):
        memo = cache if cache is not None else {}
        if "meetings" not in memo:
            try:
                memo["meetings"] = meetings(race_date)
            except Exception as exc:
                memo["meetings"] = exc
        cached = memo["meetings"]
        if isinstance(cached, (list, tuple)) and not cached:
            # Official calendar answered: no JRA meeting on this date. Nothing
            # to plan, dispatch or publish (no empty state/status files).
            return [{"race_id": race_date, "status": "NO_OFFICIAL_MEETINGS"}]
        def meetings(_d, _c=cached):
            if isinstance(_c, Exception):
                raise _c
            return _c
    out = []
    for venue, race_no, run_count, err in plan_entries(plan, race_date, meetings=meetings,
                                                       resolve=resolve, days=days):
        if err:
            key = f"{race_date}:{venue or 'ALL'}"
            schedule[key] = {"status": err}
            out.append({"race_id": key, "status": err})
            continue
        rid = race_id_for(race_date, venue, race_no)
        if venue not in days:
            try:
                days[venue] = resolve(race_date, venue)
            except Exception as exc:  # official card not available: report, never guess
                days[venue] = ValueError(type(exc).__name__ + ":" + str(exc))
        if isinstance(days[venue], Exception):
            out.append({"race_id": rid, "status": "OFFICIAL_CARD_UNAVAILABLE:" + str(days[venue])[:200]})
            schedule[rid] = {"status": out[-1]["status"]}
            continue
        race = next((r for r in days[venue][1] if r["race_no"] == race_no), None)
        if race is None:
            out.append({"race_id": rid, "status": "NOT_ON_OFFICIAL_CARD"})
            schedule[rid] = {"status": "NOT_ON_OFFICIAL_CARD"}
            continue
        hh, mm = map(int, race["post_time"].split(":"))
        d = _dt.date.fromisoformat(race_date)
        post = _dt.datetime(d.year, d.month, d.day, hh, mm, tzinfo=JST)
        schedule[rid] = {"post": post.isoformat(), "title": race.get("title"), "venue": venue,
                         "race_no": race_no, "official_day_row": race.get("raw"),
                         "dispatch_window_open": (post - _dt.timedelta(minutes=window[0])).isoformat(),
                         "dispatch_window_close": (post - _dt.timedelta(minutes=window[1])).isoformat()}
        if plan.get('cohort'):
            try:
                sys.path.insert(0,str(root/'runtime'))
                from jra_race_day_registration import verify_registration
                record=json.loads((root/'runtime/jra_race_registrations'/race_date/(rid+'.json')).read_text())
                schedule[rid]['registration_reconciliation']=verify_registration(record,plan,race_id=rid,official_post=post)
                schedule[rid]['registered_intake']=True
            except (ValueError,OSError,KeyError,TypeError) as exc:
                schedule[rid]['status']='HOLD_PREREGISTRATION_INTEGRITY'
                out.append({'race_id':rid,'status':'HOLD_PREREGISTRATION_INTEGRITY','error':str(exc)[:300]})
                continue
        # Only a failure known to precede the dispatch call may be retried.
        # An ambiguous acknowledgement retains the existing no-resend hold.
        known_no_send = (state.get(rid) or {}).get('dispatch_state') == 'CLAIM_PUBLISH_FAILED_NO_SEND'
        if (rid in state and not known_no_send) or list((root / "runtime" / "jra_formal_intents").glob(rid + "-LIVE-*.json")):
            out.append({"race_id": rid, "status": "ALREADY_DISPATCHED"})
            continue
        decision = due(post, now, window)
        if decision == "DISPATCH":
            if dispatch is None and publish is None:
                raise ValueError('DURABLE_DISPATCH_PUBLISH_REQUIRED')
            if publish is not None:
                state[rid]={**state.get(rid,{}),'claimed_at':now.isoformat(),'post':post.isoformat(),
                            'profile':PROFILE,'dispatch_state':'CLAIMED_NOT_ACKNOWLEDGED',
                            'cohort_sha256':(plan.get('cohort') or {}).get('sha256')}
                schedule_path.write_text(json.dumps(schedule,ensure_ascii=False,sort_keys=True,indent=1)+'\n')
                state_path.write_text(json.dumps(state,ensure_ascii=False,sort_keys=True,indent=1)+'\n')
                try:
                    write_status(root,race_date,now,schedule,state)
                    publish()  # The claim must exist on main BEFORE the API call.
                    merged=json.loads(state_path.read_text())
                    state.clear();state.update(merged)
                except Exception as exc:
                    state[rid]['dispatch_state']='CLAIM_PUBLISH_FAILED_NO_SEND'
                    state[rid]['first_failure']={'stage':'CLAIM_PUBLICATION','error':str(exc)[:300]}
                    out.append({'race_id':rid,'status':'CLAIM_PUBLISH_FAILED_NO_SEND'})
                    continue
            try:
                acknowledgement=(dispatch or _gh_dispatch)(venue, race_no, race_date, run_count)
            except Exception as exc:
                # One resolver/API failure must not prevent other due races.
                out.append({"race_id":rid,"status":"DISPATCH_FAILED",
                            "error":type(exc).__name__+":"+str(exc)[:200]})
                if publish is not None:
                    state[rid]['dispatch_state']='HOLD_AMBIGUOUS_DISPATCH_NO_AUTOMATIC_RETRY'
                    state[rid]['first_failure']={'stage':'INTENT_WORKFLOW_DISPATCH',
                        'observed_at':now.isoformat(),'error':str(exc)[:300],
                        'returncode':getattr(exc,'returncode',None),
                        'response':str(getattr(exc,'stderr','') or '')[:500]}
                continue
            state[rid] = {**state.get(rid,{}),"dispatched_at": now.isoformat(), "post": post.isoformat(),
                          "profile": PROFILE,'dispatch_state':'DISPATCH_ACKNOWLEDGED',
                          'acknowledgement':acknowledgement}
        out.append({"race_id": rid, "post": post.isoformat(), "status": decision, "title": race.get("title")})
    schedule_path.write_text(json.dumps(schedule, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    write_status(root, race_date, now, schedule, state)
    return out


# --------------------------------------------------------------- status index
def _blocked_cells(gap: dict) -> list[str]:
    rows = ((gap.get("base_index_coverage_diagnostic") or {}).get("rows") or [])
    per: dict[str, list[str]] = {}
    for x in rows:
        if x.get("status") == "BLOCKED":
            per.setdefault(str(x.get("runner_id")), []).append(f"{x.get('index_id')}({x.get('profile')})")
    return [f"{rid}番:{'/'.join(v)}" for rid, v in sorted(per.items(), key=lambda z: int(z[0]) if z[0].isdigit() else 99)]


def race_status(root: Path, rid: str, sched: dict, state: dict, now: _dt.datetime) -> dict:
    row = {"race_id": rid, "post": sched.get("post"), "title": sched.get("title"),
           "venue": sched.get("venue"), "race_no": sched.get("race_no")}
    row["registered_intake"]=sched.get("registered_intake",False)
    if sched.get("status"):
        row["state"] = sched["status"]
        return row
    intents = sorted(glob.glob(str(root / "runtime" / "jra_formal_intents" / (rid + "-LIVE-*.json"))))
    final_p = root / "runtime" / "final_artifacts" / (rid + ".json")
    result_p = root / "runtime" / "results" / (rid + ".json")
    eids = [Path(p).stem for p in intents]
    no_bet = [p for e in eids for p in glob.glob(str(root / "runtime" / "jra_no_bet_terminals" / (e + ".json")))]
    gaps = [p for e in eids for p in glob.glob(str(root / "runtime" / "exact_gaps" / (e + ".json")))]
    if final_p.exists():
        final = json.loads(final_p.read_text(encoding="utf-8"))
        row["state"] = "FINAL"
        row["final_receipt_sha256"] = final.get("final_receipt_sha256")
        row["immutable_final_sha256"] = final.get("sha256")
        row["actual_numerical_calculation"]=(final.get("final_prediction_package") or {}).get("actual_numerical_calculation")
        row["krs_actual_run_count"]=((final.get("krs_run_receipt") or {}).get("receipt") or {}).get("actual_run_count")
        delivery=root/"runtime/jra_delivery"/rid/"availability_receipt.json"
        row["canonical_availability_verified_before_post"]=False
        row["user_delivery_verified"]=False
        if delivery.exists():
            proof=json.loads(delivery.read_text())
            from jra_production_postresult import _sha
            if (proof.get("sha256")!=_sha({k:v for k,v in proof.items() if k!="sha256"})
                    or proof.get("final_sha256")!=final.get("sha256")):
                raise ValueError("JRA_DELIVERY_STATUS_PROOF_INVALID")
            row["canonical_availability_verified_before_post"]=proof.get("availability_verified_before_post") is True
            row["availability_receipt"]=delivery.relative_to(root).as_posix()
            # Canonical publication never proves that a human received the tickets.
            row["user_received_at"]=None
        try:
            from jra_ticket_tree_renderer import render_ticket_tree
            tree = render_ticket_tree(final)
            row["ticket_tree"] = tree["text"]
            row["ticket_count"] = tree["ticket_count"]
            row["total_investment"] = tree["total_investment"]
        except Exception as exc:
            row["ticket_tree_error"] = type(exc).__name__ + ":" + str(exc)
        try:
            sys.path.insert(0, str(root / "runtime"))
            from jra_aki_reference import aki_reference
            ref = aki_reference(root, rid)
            if ref:
                row["aki_reference"] = ref
        except Exception as exc:
            row["aki_reference_error"] = type(exc).__name__ + ":" + str(exc)
        if result_p.exists():
            res = json.loads(result_p.read_text(encoding="utf-8"))
            st = res.get("settlement") or {}
            row["state"] = ("SETTLED_SIGNED_RESULT_LEARNED"
                            if (root / "runtime" / "learning_states" / (rid + ".json")).exists() else "SETTLED")
            row["official_top3"] = (res.get("official_result") or {}).get("top3")
            # Display exactly the RESULT-owned virtual PFS and winning tickets.
            # Do not silently recompute, drop the winning selection, or imply an actual bet.
            row["settlement"] = {k: st.get(k) for k in (
                "pfs_authority", "pfs", "total_investment", "total_payout",
                "profit_loss", "winning_tickets", "actual_purchase_status",
                "actual_pfs_status",
            )}
    elif no_bet:
        row["state"] = "EVIDENCE_NO_BET"
        row["no_bet_terminal"] = Path(no_bet[-1]).relative_to(root).as_posix()
        terminal = json.loads(Path(no_bet[-1]).read_text(encoding="utf-8"))
        if terminal.get("profile") == "KM-JRA-PRODUCTION-AKI-SELECTION-NO-BET-TERMINAL-v1-20261012":
            row["state"] = ("AKI_NO_BET" if terminal.get("lineage") == "LIVE"
                            else "AKI_NO_BET_HISTORICAL")
            row["first_blocked_stage"] = terminal.get("first_blocked_stage")
            row["decision_reason"] = terminal.get("decision_reason")
            diagnostic = ((terminal.get("failure_report") or {}).get("aki_selection_failure") or {}).get("diagnostic") or {}
            row["aki_selection_failure"] = {k: diagnostic.get(k) for k in
                                              ("code", "empty_columns", "columns", "triggers", "selection_ledger")}
            row["ticket_count"] = 0
            row["total_investment"] = 0
        if gaps:
            gap = json.loads(Path(gaps[-1]).read_text(encoding="utf-8"))
            row["full20"] = f"{gap.get('verified_full_index_count')}/{gap.get('required_index_count')}"
            row["unclosed_cells"] = _blocked_cells(gap)
    elif gaps:
        gap = json.loads(Path(gaps[-1]).read_text(encoding="utf-8"))
        failure = gap.get('formal_execution_failure')
        if failure:
            row.update(state='FORMAL_FAILED', first_blocked_stage=failure['first_failed_stage'],
                       execution_error=failure.get('error'), formal_run_id=failure['run_id'],
                       formal_run_url=failure.get('run_url'),
                       formal_conclusion=failure.get('conclusion'),
                       formal_exit_code=failure.get('exit_code'))
            return row
        row["state"] = "PRODUCTION_BLOCKED"
        error=gap.get("auto_handoff_error")
        stage=gap.get("first_blocked_stage") or (gap.get("production_blocker_classification") or {}).get("first_actual_blocked_stage")
        if error:
            stage=stage or ("PRODUCTION_AKI_COLUMN_SELECTION" if str(error).startswith("AKI_") else "PRODUCTION_AUTO_HANDOFF")
            row["execution_error"]=error
        elif gap.get("production_full_pipeline_ready") is True:
            row["state"]="DISPATCHED_RUNNING"
            row["awaiting_stage"]="EXTERNAL_FORMAL_FINAL"
        row["first_blocked_stage"] = stage
        row["full20"] = f"{gap.get('verified_full_index_count')}/{gap.get('required_index_count')}"
        row["unclosed_cells"] = _blocked_cells(gap)
    elif eids or rid in state:
        row["state"] = "DISPATCHED_RUNNING"
        row["dispatched_at"] = (state.get(rid) or {}).get("dispatched_at")
        cell=state.get(rid) or {}
        if cell.get('claimed_at') and not cell.get('dispatched_at'):
            row['state']=cell.get('dispatch_state','CLAIMED_NOT_ACKNOWLEDGED')
            row['first_failure']=cell.get('first_failure')
    else:
        post = _dt.datetime.fromisoformat(sched["post"]) if sched.get("post") else None
        close = _dt.datetime.fromisoformat(sched["dispatch_window_close"]) if sched.get("dispatch_window_close") else None
        row["state"] = ("MISSED_WINDOW" if close and now > close else "WAITING")
        row["dispatch_window_open"] = sched.get("dispatch_window_open")
    return row


def observed_formal_runs(root):
    """One bounded read per status refresh, including hard-killed Formal jobs."""
    import os
    if not os.environ.get('GH_TOKEN') and not os.environ.get('GITHUB_TOKEN'):
        return []
    try:
        result=subprocess.run(['gh','run','list','--workflow','km-formal-request-runner.yml',
            '--limit','100','--json','databaseId,displayTitle,status,conclusion,url,headSha'],
            cwd=root,check=True,capture_output=True,text=True,timeout=15)
        return json.loads(result.stdout)
    except (OSError,subprocess.SubprocessError,ValueError):
        return []  # Missing observation never becomes a fabricated failure.


def reconcile_formal_run_status(root, row, runs):
    if row.get('state')!='DISPATCHED_RUNNING':
        return
    matches=[]
    for run in runs:
        title=str(run.get('displayTitle') or '')
        path=title.removeprefix('JRA Formal ')
        if not path.startswith('runtime/requests/') or not path.endswith('.json'):
            continue
        target=(root/path).resolve()
        if not target.is_relative_to((root/'runtime/requests').resolve()) or not target.is_file():
            continue
        try:
            request=json.loads(target.read_text())
        except (OSError,ValueError):
            continue
        if request.get('family_id')=='JRA' and request.get('race_id')==row['race_id']:
            matches.append(run)
    if not matches:return
    latest=max(matches,key=lambda x:int(x['databaseId']))
    if latest.get('status')=='completed' and latest.get('conclusion') in ('failure','cancelled','timed_out'):
        row.update(state='FORMAL_FAILED',first_blocked_stage='EXTERNAL_FORMAL_WORKFLOW',
                   formal_run_id=str(latest['databaseId']),formal_run_url=latest.get('url'),
                   formal_conclusion=latest['conclusion'],formal_workflow_head_sha=latest.get('headSha'),
                   execution_error='CANONICAL_FORMAL_RUN_'+latest['conclusion'].upper(),
                   detailed_failure_stage_verified=False)


def write_status(root: Path, race_date: str, now: _dt.datetime, schedule: dict, state: dict, *, formal_runs=None) -> dict:
    rows=[]
    for rid,s in schedule.items():
        try:rows.append(race_status(root,rid,s,state,now))
        except (OSError,ValueError,KeyError,TypeError,ImportError) as exc:
            rows.append({'race_id':rid,'post':s.get('post'),'state':'HOLD_CHECKPOINT_INTEGRITY',
                         'first_blocked_stage':'CHECKPOINT_READBACK','execution_error':str(exc)[:300]})
    runs=(observed_formal_runs(root) if any(r.get('state')=='DISPATCHED_RUNNING' for r in rows) else []) if formal_runs is None else formal_runs
    for row in rows:
        reconcile_formal_run_status(root,row,runs)
    rows.sort(key=lambda r: (r.get("post") or "", r["race_id"]))
    idx = {"profile": PROFILE, "race_date": race_date, "generated_at":now.isoformat(), "races": rows,
           "how_to_read": "Each race is run automatically 55-30 min before its official post. FINAL = signed pre-race "
                          "Production FINAL with the 買い目 tree; EVIDENCE_NO_BET = verified zero-exposure terminal "
                          "because some runner x index cells could not be closed from official evidence; "
                          "AKI_NO_BET = actual Full20 closed, registered AKI positive-evidence selection cannot close; "
                          "MISSED_WINDOW = never predicted (no late or backdated FINAL)."}
    plan_path=root/'runtime/jra_race_day_plan'/f'{race_date}.json'
    plan=json.loads(plan_path.read_text()) if plan_path.exists() else {}
    cohort=(plan.get('cohort') or {})
    if cohort:
        indexed={r['race_id']:r for r in rows}
        # Missing races remain in the denominator; never count only successes.
        cohort_rows=[indexed.get(rid,{}) for rid in cohort['race_ids']]
        idx['cohort_metrics']={'denominator':cohort['race_count'],'cohort_sha256':cohort['sha256'],
            'registered_intakes':sum(r.get('registered_intake') is True for r in cohort_rows),
            'dispatch_acknowledged':sum(bool((state.get(rid) or {}).get('dispatched_at')) for rid in cohort['race_ids']),
            'final_artifacts_present':sum(bool(r.get('immutable_final_sha256')) for r in cohort_rows),
            'canonical_available_before_post':sum(r.get('canonical_availability_verified_before_post') is True for r in cohort_rows),
            'user_delivery_verified':sum(r.get('user_delivery_verified') is True for r in cohort_rows),
            'full20_calculated_cells':sum((r.get('actual_numerical_calculation') or {}).get('calculated_count',0) for r in cohort_rows),
            'external_krs_recorded':sum((r.get('krs_actual_run_count') or 0)>=5000 for r in cohort_rows),
            'learning_records_present':sum((root/'runtime/learning_states'/(rid+'.json')).exists() for rid in cohort['race_ids']),
            'actual_purchase_status':'UNVERIFIED','prediction_quality':'FORWARD_OOS_PENDING'}
    d = root / "runtime" / "jra_race_day_status"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{race_date}.json").write_text(json.dumps(idx, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    md = [f"# JRA {race_date} 全レース状況", ""]
    for r in rows:
        head = f"## {r.get('venue') or ''}{r.get('race_no') or ''}R {r.get('title') or ''} ({(r.get('post') or '')[11:16]}) — {r.get('state')}"
        md.append(head)
        if r.get('formal_run_id'):
            md.append(f"Formal Run {r['formal_run_id']} / {r.get('formal_conclusion')} / "
                      f"最初の停止工程 {r.get('first_blocked_stage')} / {r.get('execution_error')}")
        if r.get("ticket_tree"):
            md += ["```", r["ticket_tree"], "```"]
        if (r.get("aki_reference") or {}).get("tree"):
            md += ["```", r["aki_reference"]["tree"], "```"]
        if r.get("unclosed_cells"):
            md.append(f"Full20 {r.get('full20')} 未成立: " + "、".join(r["unclosed_cells"]))
        if r.get("aki_selection_failure"):
            md.append(f"Full20 {r.get('full20')} 計算済み。AKI選定停止: {r.get('decision_reason')}。"
                      + "空列: " + "、".join(r["aki_selection_failure"].get("empty_columns") or [])
                      + "。投資0円・買い目なし。正式FINALとは別の見送り決定。")
        if r.get("settlement"):
            md.append(f"結果 {r.get('official_top3')} 精算 {r['settlement']}")
        md.append("")
    (d / f"{race_date}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return idx


def _gh_dispatch(venue, race_no, race_date, run_count):
    result=subprocess.run(["gh", "workflow", "run", "km-jra-race-intent-resolver.yml", "--ref", "main",
                    "-f", f"venue={venue}", "-f", f"race_no={race_no}", "-f", f"race_date={race_date}",
                    "-f", f"run_count={run_count}"], check=True, timeout=30,capture_output=True,text=True)
    return {'transport':'GITHUB_CLI_WORKFLOW_DISPATCH','returncode':result.returncode,
            'observed_at':_dt.datetime.now(_dt.timezone.utc).isoformat(),
            'response':result.stdout.strip()[:500],'http_status':None}


def _post_result_closed_loop(root: Path, race_date: str) -> None:
    """Settle due Production FINALs (official result) and hand each RESULT
    request to the canonical Result Runner exactly once, only after the request
    is published on main. Scheduled cron alone proved unreliable, so the day
    loop drives it; idempotent per race (state: <date>.state.json)."""
    run = lambda *a: subprocess.run(list(a), cwd=root, text=True, capture_output=True, timeout=30)
    r = subprocess.run([sys.executable, "runtime/jra_production_postresult.py", "--days", "1"],
                       cwd=root, text=True, capture_output=True, timeout=180)
    print(r.stdout.strip()[-2000:], flush=True)
    d8 = _dt.date.fromisoformat(race_date).strftime("%Y%m%d")
    new = [x for x in run("git", "ls-files", "--others", "--exclude-standard",
                          "runtime/results").stdout.split() if x.startswith("runtime/results/KM-JRA-")]
    if new:
        run("git", "add", *new)
        run("git", "commit", "-m", "result: JRA Production official result request [skip ci]")
    pushed = False
    for i in range(5):
        if _rebase_generated(root, race_date) and \
                run("git", "push", "origin", "HEAD:main").returncode == 0:
            pushed = True
            break
        run("git", "rebase", "--abort")
        time.sleep(3 * (i + 1))
    if not pushed:
        return  # retried next tick; never dispatch an unpublished request
    state_path = root / "runtime" / "jra_race_day_plan" / f"{race_date}.state.json"
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
    done = set(state.get("_result_runner_dispatched") or [])
    published = sorted(Path(p).relative_to(root).as_posix() for p in
                       glob.glob(str(root / "runtime" / "results" / f"KM-JRA-*-{d8}-R*.json")))
    for path in published:
        rid = Path(path).stem
        if path in done or (root / "runtime" / "learning_states" / f"{rid}.json").exists():
            done.add(path)  # Result Runner already completed (learning state persisted)
            continue
        if run("gh", "workflow", "run", "km-formal-result-runner.yml", "--ref", "main",
               "-f", f"request_path={path}").returncode == 0:
            done.add(path)
    state["_result_runner_dispatched"] = sorted(done)
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def request_postresult_worker(root, race_date, now, *, publish, send=None):
    """Hand results to the existing independent workflow, never wait for RESULT."""
    path=root/'runtime/jra_race_day_plan'/f'{race_date}.state.json'
    state=json.loads(path.read_text()) if path.exists() else {}
    previous=state.get('_postresult_worker') or {}
    if previous.get('requested_at') and (now-_dt.datetime.fromisoformat(previous['requested_at'])).total_seconds()<1800:
        return 'RECENT_RESULT_WORKER_REQUEST'
    d8=_dt.date.fromisoformat(race_date).strftime('%Y%m%d')
    finals=list((root/'runtime/final_artifacts').glob(f'KM-JRA-*-{d8}-R*.json'))
    due_final=False
    for final_path in finals:
        if (root/'runtime/learning_states'/final_path.name).exists():continue
        try:
            due_final |= _dt.datetime.fromisoformat(json.loads(final_path.read_text())['scheduled_post_at'])<now
        except (OSError,ValueError,KeyError,TypeError):
            continue  # Status index owns this race's checkpoint integrity failure.
    if not due_final:
        return 'NO_DUE_FINAL'
    state['_postresult_worker']={'requested_at':now.isoformat(),'state':'CLAIMED_NOT_ACKNOWLEDGED'}
    path.write_text(json.dumps(state,ensure_ascii=False,sort_keys=True,indent=1)+'\n')
    publish()
    try:
        if send is None:
            subprocess.run(['gh','workflow','run','km-jra-production-postresult.yml','--ref','main'],
                           check=True,cwd=root,capture_output=True,text=True,timeout=30)
        else:send()
        result='ACKNOWLEDGED'
    except (subprocess.SubprocessError,OSError):
        result='UNKNOWN_NO_IMMEDIATE_RETRY'
    state=json.loads(path.read_text());state['_postresult_worker']['state']=result
    path.write_text(json.dumps(state,ensure_ascii=False,sort_keys=True,indent=1)+'\n')
    return result


def merge_dispatch_state(remote: dict, local: dict) -> dict:
    """Monotonic union: never lose an acknowledged dispatch or result handoff."""
    out = dict(remote)
    for key, value in local.items():
        if key == "_result_runner_dispatched":
            out[key] = sorted(set(remote.get(key) or []) | set(value or []))
        elif key=='_postresult_worker' and key in out:
            out[key]=max([out[key],value],key=lambda x:x.get('requested_at',''))
        elif key not in out:
            out[key] = value
        elif isinstance(value, dict) and isinstance(out[key], dict):
            a, b = out[key], value
            merged={**a,**b}
            for stamp in ('claimed_at','dispatched_at'):
                observed=[x[stamp] for x in (a,b) if x.get(stamp)]
                if observed:merged[stamp]=min(observed)
            if a.get('first_failure'):merged['first_failure']=a['first_failure']
            if merged.get('dispatched_at'):
                merged['dispatch_state']='DISPATCH_ACKNOWLEDGED'
                acknowledged=next((x for x in (a,b) if x.get('dispatched_at')),merged)
                if acknowledged.get('acknowledgement'):merged['acknowledgement']=acknowledged['acknowledgement']
            out[key]=merged
    return out


def _rebase_generated(root: Path, race_date: str) -> bool:
    """Resolve ONLY derived race-day files; other conflicts remain failures."""
    def run(*args):
        return subprocess.run(list(args),cwd=root,text=True,capture_output=True,timeout=30)
    r=run("git","pull","--rebase","--autostash","origin","main")
    if r.returncode == 0:
        return True
    conflicts=run("git","diff","--name-only","--diff-filter=U").stdout.splitlines()
    state_path=f"runtime/jra_race_day_plan/{race_date}.state.json"
    schedule_path=f"runtime/jra_race_day_plan/{race_date}.schedule.json"
    index_paths={f"runtime/jra_race_day_status/{race_date}.json",f"runtime/jra_race_day_status/{race_date}.md"}
    allowed={state_path,schedule_path}|index_paths
    if not conflicts or not set(conflicts)<=allowed:
        return False
    for path in conflicts:
        if path in index_paths:
            continue  # Rebuild from merged truth below, never pick a stale index.
        remote=json.loads(run("git","show",f":2:{path}").stdout)
        local=json.loads(run("git","show",f":3:{path}").stdout)
        value=merge_dispatch_state(remote,local) if path==state_path else {**remote,**local}
        (root/path).write_text(json.dumps(value,ensure_ascii=False,indent=1,sort_keys=True)+"\n")
    state=json.loads((root/state_path).read_text())
    schedule=json.loads((root/schedule_path).read_text())
    write_status(root,race_date,_dt.datetime.now(JST),schedule,state)
    run("git","add",*sorted(allowed))
    r=run("git","-c","core.editor=true","rebase","--continue")
    return r.returncode==0


def _commit(root: Path, race_date: str) -> None:
    paths = [f"runtime/jra_race_day_plan/{race_date}.state.json", f"runtime/jra_race_day_plan/{race_date}.schedule.json",
             f"runtime/jra_race_day_status/{race_date}.json", f"runtime/jra_race_day_status/{race_date}.md"]
    run = lambda *a: subprocess.run(list(a), cwd=root, text=True, capture_output=True, timeout=30)
    run("git", "add", *paths)
    if run("git", "diff", "--cached", "--quiet").returncode != 0:
        run("git", "commit", "-m", f"autopilot: race-day state and status {race_date} [skip ci]")
    elif not run("git","rev-list","origin/main..HEAD").stdout.strip():
        return
    for i in range(5):
        if _rebase_generated(root, race_date) and \
                run("git", "push", "origin", "HEAD:main").returncode == 0:
            return
        run("git", "rebase", "--abort")
        time.sleep(3 * (i + 1))
    raise RuntimeError("AUTOPILOT_STATE_PUBLISH_RETRIES_EXHAUSTED")


def loop_finished(now, until, started, maximum_seconds):
    hh,mm=map(int,until.split(":"))
    return (now>=now.replace(hour=hh,minute=mm,second=0,microsecond=0)
            or time.monotonic()-started>=maximum_seconds)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default="../..")
    ap.add_argument("--date", default=_dt.datetime.now(JST).date().isoformat())
    ap.add_argument("--all-races-default", action="store_true",
                    help="plan every official race when no plan file exists for the date")
    ap.add_argument("--loop-until", help="HH:MM JST; tick every --interval seconds until then, committing state")
    ap.add_argument("--interval", type=int, default=120)
    ap.add_argument("--max-loop-seconds", type=int, default=1800)
    ap.add_argument("--publish-only", action="store_true")
    a = ap.parse_args()
    root = Path(a.repo_root).resolve()
    if a.publish_only:
        if not _rebase_generated(root,a.date):
            raise RuntimeError('AUTOPILOT_STATUS_REFRESH_PULL_FAILED')
        schedule=json.loads((root/'runtime/jra_race_day_plan'/f'{a.date}.schedule.json').read_text())
        state_path=root/'runtime/jra_race_day_plan'/f'{a.date}.state.json'
        state=json.loads(state_path.read_text()) if state_path.exists() else {}
        write_status(root,a.date,_dt.datetime.now(JST),schedule,state)
        _commit(root,a.date)
        raise SystemExit(0)
    started=time.monotonic()
    cache: dict = {}
    cache_at = None
    while True:
        now = _dt.datetime.now(JST)
        if a.loop_until:
            try:
                if not _rebase_generated(root,a.date):
                    subprocess.run(["git","rebase","--abort"],cwd=root,capture_output=True,timeout=30)
                    print("AUTOPILOT_PULL_RETRY_NEXT_TICK",flush=True)
            except (subprocess.SubprocessError,OSError,ValueError) as exc:
                print("AUTOPILOT_PULL_ERROR:"+str(exc)[:200],flush=True)
        if cache_at is None or (now - cache_at).total_seconds() > 1800 or any(
                isinstance(v, Exception) for v in list(cache.get("days", {}).values()) + [cache.get("meetings")]):
            cache, cache_at = {}, now
        try:
            res = tick(root, a.date, now, default_all=a.all_races_default, cache=cache,
                       publish=lambda:_commit(root,a.date))
            print(json.dumps({"profile": PROFILE, "date": a.date, "at": now.isoformat(), "races": res}, ensure_ascii=False), flush=True)
            if [r.get("status") for r in res] == ["NO_OFFICIAL_MEETINGS"]:
                break  # non-race day: stop at once instead of idling until the loop end
        except Exception as exc:  # keep the day running; the index shows the last good state
            print(json.dumps({"profile": PROFILE, "error": type(exc).__name__ + ":" + str(exc)}, ensure_ascii=False), flush=True)
        if a.loop_until:
            try:
                request_postresult_worker(root,a.date,_dt.datetime.now(JST),
                                         publish=lambda:_commit(root,a.date))
            except (subprocess.SubprocessError, OSError, RuntimeError, ValueError, KeyError, TypeError) as exc:
                print(json.dumps({"stage":"POSTRESULT","error":str(exc)[:300]}),flush=True)
        if not a.loop_until:
            break
        try:
            _commit(root, a.date)
        except (subprocess.SubprocessError, OSError, RuntimeError) as exc:
            print(json.dumps({"stage":"PUBLISH","error":str(exc)[:300]}),flush=True)
        hh, mm = map(int, a.loop_until.split(":"))
        if loop_finished(_dt.datetime.now(JST),a.loop_until,started,a.max_loop_seconds):
            break
        time.sleep(max(30, a.interval))

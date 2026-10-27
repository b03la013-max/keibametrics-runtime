"""JRA Candidate closed-loop: verified official result -> frozen-ticket settlement -> learning.

This module never changes or backdates PRE_RESULT/FINAL. It does not confer
Production prediction, actual purchase, or signed RESULT authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "jra_source_runtime"))

from jra_source_candidate_oos import evaluate_result
from jra_source_candidate_promotion_gate import bind_result
from jra_same_day_results import (_open_day, _result_post, parse_result_detail,
    finish_groups_and_top3_orders, validate_result_identity, OfficialResultNavigationError)
from jra_race_card_detail import _date8
from jra_source_runtime.source_acquisition import _decode, _html_text, utcnow

PROFILE = "KM-JRA-CANDIDATE-AUTOMATIC-POSTRESULT-CLOSEDLOOP-20261010-R1"
BET_KINDS = {"EXACTA": ("馬単", 2), "TRIO": ("3連複", 3), "TRIFECTA": ("3連単", 3)}


class PendingOfficialResult(ValueError):
    pass


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def validate_result_target(race_id, race_date, meeting_key, race_no):
    """Bind existing execution identity before any official RESULT request.

    This checks observed date/key/number only; it supplies no missing time,
    SOURCE, registration, permission, or formal result authority.
    """
    from jra_race_day_resolver import VENUES
    day=_date8(race_date)
    key=str(meeting_key or '')
    if (type(race_no) is not int or not 1<=race_no<=12 or
            not re.fullmatch(r'\d{10}',key) or key[:2] not in VENUES or
            key[2:6]!=day[:4] or int(key[6:8])<1 or int(key[8:10])<1):
        raise ValueError('RESULT_TARGET_REFERENCE_INVALID')
    venue_id,venue=VENUES[key[:2]]
    expected=f'KM-JRA-{venue_id}-{day}-R{race_no:02d}'
    if race_id!=expected:
        raise ValueError('RESULT_TARGET_RACE_ID_MISMATCH')
    return {'race_id':expected,'race_date':f'{day[:4]}-{day[4:6]}-{day[6:]}',
            'meeting_key':key,'venue_id':venue_id,'venue':venue,'race_no':race_no,
            'meeting_no':int(key[6:8]),'meeting_day':int(key[8:10])}


def _verified_pre_frozen(pre: dict, final: dict, race_id: str) -> None:
    if pre.get("race_id") != race_id or final.get("race_id") != race_id:
        raise ValueError("RACE_ID_BINDING_MISMATCH")
    if pre.get("oos_eligible") is not True or pre.get("candidate_final_verified") is not True:
        raise ValueError("PRE_START_CANDIDATE_FINAL_NOT_VERIFIED")
    if pre.get("source_snapshot_sha256") != final.get("source_snapshot_sha256"):
        raise ValueError("SOURCE_BASIS_MISMATCH")
    if pre.get("sha256") != canonical_sha({k:v for k,v in pre.items() if k != "sha256"}):
        raise ValueError("PRE_RESULT_HASH_INVALID")
    if final.get("sha256") != canonical_sha({k:v for k,v in final.items() if k != "sha256"}):
        raise ValueError("CANDIDATE_FINAL_HASH_INVALID")
    if pre.get("candidate_final_receipt_sha256") != (final.get("final_receipt") or {}).get("receipt_sha256"):
        raise ValueError("FINAL_RECEIPT_BINDING_MISMATCH")
    post = datetime.fromisoformat(str(pre["scheduled_post_at"]).replace("Z","+00:00"))
    ft = datetime.fromisoformat(str(pre["candidate_final_receipt_timestamp"]).replace("Z","+00:00"))
    if ft >= post:
        raise ValueError("FINAL_AFTER_SCHEDULED_POST")
    if final.get("candidate_only") is not True or final.get("production_effect") not in ("NONE", None):
        raise ValueError("CANDIDATE_AUTHORITY_LEAK")


def parse_official_payouts(text: str) -> dict:
    """Extract each distinct official winning combination per 100 yen.

    One payout retains the historic dict shape; a dead heat may yield a list.
    Repeating the same canonical combination is never an extra payout.
    The result verifier separately reconciles the complete winning set.
    """
    if "払戻金" not in text:
        raise PendingOfficialResult("JRA_OFFICIAL_PAYOUT_SECTION_NOT_PUBLISHED")
    # JRA footer also contains 払戻金 (e.g., 払戻金の支払を受けた方へ).
    # Anchor the actual payout table by the adjacent first bet-type label.
    anchors = list(re.finditer(r"払戻金\s+単勝\s+", text))
    if len(anchors) != 1:
        raise (ValueError if len(anchors)>1 else PendingOfficialResult)("JRA_OFFICIAL_PAYOUT_TABLE_NOT_UNIQUE")
    tail = "単勝 " + text[anchors[0].end():].split("勝馬の紹介",1)[0]
    out = {}
    for kind, (label, count) in BET_KINDS.items():
        labels=list(re.finditer(r"(?<!\S)"+re.escape(label)+r"\s+",tail))
        if len(labels)!=1:
            raise (ValueError if len(labels)>1 else PendingOfficialResult)("JRA_PAYOUT_MISSING_OR_AMBIGUOUS:" + kind)
        block=tail[labels[0].end():]
        stop=re.search(r"(?<!\S)(?:単勝|複勝|枠連|馬連|ワイド|馬単|3連複|3連単)\s+",block)
        if stop:block=block[:stop.start()]
        pattern = r"((?:\d{1,2}\s*-\s*){"+str(count-1)+r"}\d{1,2})\s+([\d,]+)\s*円"
        matches=re.findall(pattern,block)
        if not matches:
            raise PendingOfficialResult("JRA_PAYOUT_MISSING_OR_AMBIGUOUS:"+kind)
        entries=[];seen=set()
        for selection,yen in matches:
            nums=[int(x) for x in re.findall(r"\d+",selection)]
            amount=int(yen.replace(",",""))
            if len(nums)!=count or len(set(nums))!=count or any(not 1<=x<=18 for x in nums) or amount<=0:
                raise ValueError("JRA_PAYOUT_FORMAT_INVALID:"+kind)
            key=tuple(sorted(nums)) if kind=="TRIO" else tuple(nums)
            if key in seen:
                raise ValueError("JRA_PAYOUT_DUPLICATE_COMBINATION:"+kind)
            seen.add(key);entries.append({"selection":nums,"per_100_yen":amount})
        out[kind]=entries[0] if len(entries)==1 else entries
    return out


def official_top3_orders(official:dict)->list[list[int]]:
    """Return every permissible order without silently truncating a dead heat."""
    supplied=official.get("top3_orders")
    if supplied is None and (official.get("dead_heat") is True or official.get("finish_groups") is not None):
        raise ValueError("OFFICIAL_TOP3_ORDERS_REQUIRED")
    orders=supplied if supplied is not None else [official.get("top3")]
    if not isinstance(orders,list) or not orders:
        raise ValueError("OFFICIAL_TOP3_ORDERS_REQUIRED")
    seen=set();out=[]
    for order in orders:
        if (not isinstance(order,list) or len(order)!=3 or
                any(type(x) is not int or not 1<=x<=18 for x in order) or len(set(order))!=3):
            raise ValueError("OFFICIAL_TOP3_ORDER_INVALID")
        key=tuple(order)
        if key in seen:raise ValueError("OFFICIAL_TOP3_ORDER_DUPLICATE")
        seen.add(key);out.append(order[:])
    groups=official.get("finish_groups")
    if supplied is not None:
        if not isinstance(groups,list) or not groups:
            raise ValueError("OFFICIAL_FINISH_GROUPS_REQUIRED")
        if (any(not isinstance(g,dict) or type(g.get("finish")) is not int or g["finish"]<1
                or not isinstance(g.get("horse_numbers"),list) or not g["horse_numbers"] for g in groups)
                or len({g["finish"] for g in groups})!=len(groups)):
            raise ValueError("OFFICIAL_FINISH_GROUPS_INVALID")
        rows=[{"finish":g["finish"],"horse_no":n} for g in groups for n in g["horse_numbers"]]
        expected=finish_groups_and_top3_orders(rows)["top3_orders"]
        if sorted(out)!=expected:
            raise ValueError("OFFICIAL_TOP3_GROUP_BINDING_MISMATCH")
        if official.get("top3")!=expected[0]:
            raise ValueError("OFFICIAL_LEGACY_TOP3_BINDING_MISMATCH")
    return sorted(out)


def official_payout_entries(official:dict,kind:str)->list[dict]:
    """Validate all payable combinations, and each canonical ticket pays once."""
    value=official.get("payouts",{}).get(kind)
    entries=value if isinstance(value,list) else [value]
    count=BET_KINDS[kind][1];seen=set();out=[]
    for pay in entries:
        if not isinstance(pay,dict):raise ValueError("OFFICIAL_PAYOUT_INVALID")
        selection=pay.get("selection");price=pay.get("per_100_yen")
        if (not isinstance(selection,list) or len(selection)!=count or
                any(type(x) is not int or not 1<=x<=18 for x in selection) or
                len(set(selection))!=count or type(price) is not int or price<=0):
            raise ValueError("OFFICIAL_PAYOUT_INVALID")
        key=tuple(sorted(selection)) if kind=="TRIO" else tuple(selection)
        if key in seen:raise ValueError("OFFICIAL_PAYOUT_DUPLICATE_COMBINATION")
        seen.add(key);out.append(pay)
    expected={tuple(sorted(o)) if kind=="TRIO" else tuple(o[:count])
              for o in official_top3_orders(official)}
    if seen!=expected:
        raise ValueError("OFFICIAL_PAYOUT_TOP3_COMBINATIONS_MISMATCH:"+kind)
    return out


def verify_official_result(parsed: dict, payout_text: str, frozen_runner_ids: list[str]) -> dict:
    rows = list(parsed.get("runners") or [])
    if parsed.get("official") is not True or not rows:
        raise PendingOfficialResult("JRA_OFFICIAL_RESULT_TABLE_MISSING")
    non_finishers=list(parsed.get("non_finishers") or [])
    ids = [str(r.get("runner_id")) for r in rows+non_finishers]
    if len(set(ids)) != len(ids) or set(ids) != set(map(str,frozen_runner_ids)):
        raise ValueError("OFFICIAL_RESULT_RUNNER_UNIVERSE_MISMATCH")
    try:
        grouped=finish_groups_and_top3_orders(rows)
    except ValueError as exc:
        raise PendingOfficialResult("JRA_TOP3_NOT_CONFIRMED:"+str(exc)) from exc
    actual=grouped["top3_orders"][0]
    payouts = parse_official_payouts(payout_text)
    checked={"top3":actual,"payouts":payouts}
    if grouped["dead_heat"]:checked.update(grouped)
    for kind in BET_KINDS:
        try:official_payout_entries(checked,kind)
        except ValueError as exc:
            raise ValueError("OFFICIAL_PAYOUT_TOP3_MISMATCH:"+kind+":"+str(exc)) from exc
    # Only the explicit official refund horse-number declaration authorizes
    # refunds. A non-finish, fall or disqualification is not a cancellation.
    # Keep the returned numeric finishers compatible with same-day features.
    match=re.search(r"返還馬番\s*((?:\d{1,2}\s*番(?:\s*[、・,]\s*)?\s*)+)",payout_text)
    refunded=[int(x) for x in re.findall(r"(\d{1,2})\s*番",match.group(1))] if match else []
    if len(refunded)!=len(set(refunded)) or not set(map(str,refunded))<=set(frozen_runner_ids):
        raise ValueError("OFFICIAL_REFUND_RUNNER_UNIVERSE_MISMATCH")
    withdrawn={int(r["horse_no"]) for r in non_finishers if r.get("finish_status") in {"CANCELLED","EXCLUDED"}}
    not_refundable={int(r["horse_no"]) for r in non_finishers if r.get("finish_status") in {"DID_NOT_FINISH","DISQUALIFIED"}}
    if not withdrawn<=set(refunded):
        raise PendingOfficialResult("OFFICIAL_REFUND_DECLARATION_REQUIRED")
    if not_refundable & set(refunded):
        raise ValueError("OFFICIAL_REFUND_NONCANCELLATION_STATUS")
    return {**checked, "refund_runner_ids":refunded,
            "non_finishers":non_finishers,
            "refund_declaration":match.group(0) if match else None}


def evaluate_official_candidate_result(pre:dict,official:dict)->dict:
    """Keep joint dead-heat outcomes; do not select the most flattering rank."""
    orders=official_top3_orders(official)
    measurements=[evaluate_result(pre,order) for order in orders]
    if len(orders)==1:return measurements[0]
    out=dict(measurements[0])
    for key,value in out.items():
        if type(value) is bool and key.endswith("capture"):
            out[key]=any(row[key] for row in measurements)
    for key in ("winner_static_rank","second_static_rank","third_static_rank","top3_mean_static_rank"):
        if any(row.get(key)!=out.get(key) for row in measurements):out[key]=None
    for key in ("winner_capture_efficiency","p2_capture_efficiency","p3_capture_efficiency"):
        out[key]=max(row[key] for row in measurements)
    for section in ("market_baseline","candidate_vs_market"):
        out[section]=dict(out.get(section) or {})
        for key,value in out[section].items():
            if any((row.get(section) or {}).get(key)!=value for row in measurements):
                out[section][key]=None
    out.update(actual_top3_orders=orders,official_finish_groups=official["finish_groups"],
               actual_top3_is_legacy_representative=True,
               dead_heat_order_evaluations=measurements,
               dead_heat_aggregation="ANY_VALID_ORDER_CAPTURE; VARYING_SCALAR_RANKS_ARE_NULL")
    out["krs_incremental_utility"]={"classification":"DEAD_HEAT_MULTIPLE_VALID_ORDERS",
        "by_valid_order":[{"top3":order,"evaluation":row.get("krs_incremental_utility")}
                           for order,row in zip(orders,measurements)]}
    out["sha256"]=canonical_sha({k:v for k,v in out.items() if k!="sha256"})
    return out


def settle_frozen_candidate(pre: dict, final: dict, official: dict, *, source_sha256: str, source_url: str) -> dict:
    race_id = str(pre.get("race_id") or "")
    _verified_pre_frozen(pre, final, race_id)
    actual = [int(x) for x in official["top3"]]
    prices = official["payouts"]
    orders=official_top3_orders(official)
    tickets = list(((final.get("mec") or {}).get("tickets") or []))
    if not tickets:
        raise ValueError("FROZEN_MEC_TICKETS_MISSING")
    required = int((final.get("capital") or {}).get("required_capital") or 0)
    # Reuse the Production arithmetic without asserting that this synthetic
    # carrier is a signed FINAL or a purchased Production portfolio.
    from jra_production_postresult import settle_final
    settled=settle_final({"final_ticket":{"tickets":tickets,"total_investment":required}},official)
    if int((final.get("mec") or {}).get("ticket_count") or 0)!=len(tickets):
        raise ValueError("FROZEN_CAPITAL_CANONICAL_MISMATCH")
    def key(ticket):
        selection=ticket["selection"]
        return ticket["bet_type"],tuple(sorted(selection) if ticket["bet_type"]=="TRIO" else selection)
    paid={key(t):t["return"] for t in settled["winning_tickets"]}
    purchases=[{"bet_type":t["bet_type"],"selection":t["selection"],"stake":t["stake"],
                "recommended_return":paid.get(key(t),0),"win":paid.get(key(t),0)>0} for t in tickets]
    stake_total=settled["total_investment"];return_total=settled["total_payout"]
    effective_stake=settled["effective_investment"]
    evaluated = evaluate_official_candidate_result(pre,official)
    bound = bind_result(pre, evaluated)
    if not evaluated["winner_capture"]: first = "W_HEAD_ZERO"
    elif not evaluated["p2_capture"]: first = "P2_SECOND_ZERO"
    elif not evaluated["p3_capture"]: first = "P3_THIRD_ZERO"
    elif not evaluated["ordered_pair_capture"]: first = "ORDERED_PAIR_MISSING"
    elif not evaluated["exact_capture"]: first = "PAIR_CONDITIONED_THIRD_MISSING"
    elif not any(x["win"] for x in purchases): first = "TICKET_CONVERSION_UNREACHABLE"
    elif return_total < effective_stake: first = "CAPITAL_EFFICIENCY_LOSS"
    else: first = "NONE"
    owner = "NONE" if return_total >= effective_stake else (
        "CAPITAL_EFFICIENCY" if any(x["win"] for x in purchases) else
        "PREDICTION_ROLE_ORDER" if first in {"W_HEAD_ZERO","P2_SECOND_ZERO","P3_THIRD_ZERO","ORDERED_PAIR_MISSING","PAIR_CONDITIONED_THIRD_MISSING"} else
        "TICKET_CONVERSION")
    report = {
        "profile": PROFILE, "race_id": race_id, "status":"SETTLED_FROZEN_CANDIDATE_RECOMMENDATION",
        "authority":"CANDIDATE / NON-PRODUCTION / NO-AUTO-PROMOTION",
        "official_result_source_sha256":source_sha256,
        "official_result_source_url":source_url,
        "frozen_pre_result_sha256":pre["sha256"],"frozen_candidate_final_sha256":final["sha256"],
        "actual_top3": actual, "official_payouts": prices, "purchased_ticket_count":len(purchases),
        "frozen_tickets":purchases, "recommended_stake_yen":stake_total,
        "recommended_return_yen":return_total,
        "recommended_profit_yen":settled["profit_loss"],
        "frozen_recommendation_pfs_percent":round(settled["pfs"],2) if settled["pfs"] is not None else None,
        "actual_purchase_status":"UNVERIFIED","actual_pfs_status":"NOT_VERIFIED",
        "first_material_failure":first,"dominant_pfs_loss_owner":owner,
        "prediction_measurement":evaluated, "oos_eligible":pre["oos_eligible"],
        "result_receipt_status":"OFFICIAL_HTTP_SNAPSHOT_HASH_BOUND / SIGNED_RESULT_NOT_VERIFIED",
        "production_effect":"NONE","automatic_promotion":False,
    }
    if len(orders)>1:
        report.update(actual_top3_orders=orders,official_finish_groups=official["finish_groups"],
                      actual_top3_is_legacy_representative=True)
    if settled["refund"]:
        report.update(recommended_refund_yen=settled["refund"],
                      recommended_effective_stake_yen=settled["effective_investment"],
                      refunded_tickets=settled["refunded_tickets"])
    report["sha256"] = canonical_sha(report)
    bound["settlement_sha256"] = report["sha256"]
    bound["official_result_source_sha256"] = source_sha256
    bound["sha256"] = canonical_sha({k:v for k,v in bound.items() if k!="sha256"})
    learning = {
        "profile":PROFILE,"race_id":race_id,"status":"LEARNING_OBSERVATION_RECORDED / NO_POLICY_AUTO_CHANGE",
        "previous_state_sha256":pre["sha256"],"settlement_sha256":report["sha256"],
        "first_material_failure":first,"dominant_pfs_loss_owner":owner,
        "next_action":("KEEP" if first=="NONE" else "TEST_NEXT"),
        "promotion_authority":False,"new_model_weights_applied":False,"learning_state":"N_PLUS_1_OBSERVATION",
    }
    learning["sha256"]=canonical_sha(learning)
    return {"result_evaluation":bound,"settlement":report,"learning":learning}


def fetch_jra_result(race_date: str, meeting_key: str, race_no: int, *, session=None) -> dict:
    import base64
    if type(race_no) is not int or not 1 <= race_no <= 12:
        raise OfficialResultNavigationError('JRA_RESULT_RACE_NUMBER_INVALID','RESULT_INPUT')
    client, referer, day_html, key, d = session if session is not None else _open_day(race_date, meeting_key)
    if key != meeting_key or d != _date8(race_date):
        raise OfficialResultNavigationError('JRA_RESULT_SESSION_TARGET_MISMATCH','RESULT_INPUT')
    needle=r'pw01sde\d{2}'+re.escape(key+f'{race_no:02d}'+d)+r'/[0-9A-Fa-f]{2}'
    tokens=sorted(set(re.findall(needle,day_html)))
    if not tokens:
        exc=PendingOfficialResult('JRA_OFFICIAL_RESULT_RACE_NOT_PUBLISHED')
        exc.first_failed_stage='RESULT_RACE_SELECTION'
        exc.official_navigation=list(getattr(client,'result_navigation',[]))
        exc.diagnostic={'navigation':[{k:v for k,v in row.items() if k!='fetched_at'}
                                      for row in exc.official_navigation]}
        raise exc
    if len(tokens)!=1:
        raise OfficialResultNavigationError('JRA_RESULT_RACE_TOKEN_NOT_UNIQUE','RESULT_RACE_SELECTION',client=client)
    url,raw,headers=_result_post(client,tokens[0],referer)
    fetched=client.last_response.get("fetched_at") or utcnow()
    try:
        identity=validate_result_identity(raw,headers.get('content-type',''),key,d,race_no)
        parsed=parse_result_detail(raw,headers.get('content-type',''))
    except Exception as exc:
        if not hasattr(exc,'first_failed_stage'):exc.first_failed_stage='RESULT_DETAIL_TABLE'
        exc.diagnostic={'navigation':[{k:v for k,v in row.items() if k!='fetched_at'}
                                      for row in getattr(client,'result_navigation',[])]}
        raise
    return {'parsed':parsed,'text':_html_text(_decode(raw,headers.get('content-type',''))),
            'sha256':hashlib.sha256(raw).hexdigest(),'captured_at':fetched,
            'url':url,'source_authority':'JRA_OFFICIAL_POST_RESULT',
            'identity':identity,'navigation':list(getattr(client,'result_navigation',[])),
            'raw_base64':base64.b64encode(raw).decode('ascii'),'content_type':headers.get('content-type','')}


def build_official_result_observation(race_id:str,evidence:dict,*,official=None):
    """Retain original raw capture at an existing caller-owned artifact path.

    A repeated capture of identical bytes reuses its first recorded time.
    No signature, pre-result freeze, learning admission or OOS is conferred.
    """
    import base64
    raw=evidence.get('raw_base64')
    identity=evidence.get('identity') or {}
    if raw is None:raise ValueError('OFFICIAL_RESULT_RAW_CAPTURE_REQUIRED')
    try:decoded=base64.b64decode(raw,validate=True)
    except (ValueError,TypeError) as exc:raise ValueError('OFFICIAL_RESULT_RAW_CAPTURE_INVALID') from exc
    if hashlib.sha256(decoded).hexdigest()!=evidence.get('sha256'):
        raise ValueError('OFFICIAL_RESULT_RAW_SHA_MISMATCH')
    key=identity.get('meeting_key') or '';date=str(identity.get('race_date') or '')
    try:validate_result_target(race_id,date,key,identity.get('race_no'))
    except (ValueError,TypeError) as exc:raise ValueError('OFFICIAL_RESULT_CAPTURE_RACE_MISMATCH') from exc
    bound=validate_result_identity(decoded,evidence.get('content_type',''),key,_date8(date),identity['race_no'])
    if bound!=identity:raise ValueError('OFFICIAL_RESULT_RAW_IDENTITY_BINDING_MISMATCH')
    source_url=urllib.parse.urlsplit(evidence.get('url') or '')
    if (source_url.scheme!='https' or source_url.hostname!='www.jra.go.jp' or
            source_url.path!='/JRADB/accessS.html'):
        raise ValueError('OFFICIAL_RESULT_CAPTURE_ENDPOINT_INVALID')
    record={'profile':PROFILE,'race_id':race_id,'status':'OFFICIAL_POST_RESULT_SNAPSHOT',
            'raw_sha256':evidence['sha256'],'raw_base64':raw,'captured_at':evidence['captured_at'],
            'url':evidence['url'],'identity':identity,'navigation':evidence.get('navigation') or [],
            'signed_result_receipt_verified':False}
    if official is not None:record.update(result_top3=official['top3'],payouts=official['payouts'])
    record['sha256']=canonical_sha(record)
    return record


def persist_official_result_observation(path:Path,race_id:str,evidence:dict,*,official=None):
    record=build_official_result_observation(race_id,evidence,official=official)
    raw=record['raw_base64'];identity=record['identity']
    path=Path(path)
    if path.exists():
        old=json.loads(path.read_text())
        if (old.get('sha256')!=canonical_sha({k:v for k,v in old.items() if k!='sha256'}) or
                old.get('race_id')!=race_id or old.get('identity')!=identity or
                old.get('raw_sha256')!=record['raw_sha256'] or old.get('raw_base64')!=raw):
            raise ValueError('OFFICIAL_RESULT_OBSERVATION_IMMUTABILITY_VIOLATION')
        return old
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as out:
        out.write(json.dumps(record,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    return record


def process(root:Path, race_id:str)->str:
    race_dir=root/"runtime"/"source_candidate_oos"/race_id
    result_path=race_dir/"result_evaluation.json"
    if result_path.exists():
        saved={}
        for name in ('result_evaluation','settlement','learning','official_result_observation'):
            path=race_dir/(name+'.json')
            if not path.exists():raise ValueError('CANDIDATE_RESULT_BUNDLE_INCOMPLETE:'+name)
            value=json.loads(path.read_text())
            if value.get('race_id')!=race_id:raise ValueError('CANDIDATE_RESULT_BUNDLE_RACE_MISMATCH')
            # Legacy observation metadata did not have a self hash. Existing
            # immutable originals are not upgraded or rewritten retrospectively.
            if (name!='official_result_observation' or 'sha256' in value) and value.get('sha256')!=canonical_sha(
                    {k:v for k,v in value.items() if k!='sha256'}):
                raise ValueError('CANDIDATE_RESULT_BUNDLE_SHA_MISMATCH:'+name)
            saved[name]=value
        if (saved['learning'].get('settlement_sha256')!=saved['settlement']['sha256'] or
                saved['result_evaluation'].get('settlement_sha256')!=saved['settlement']['sha256'] or
                saved['official_result_observation'].get('raw_sha256')!=
                saved['settlement'].get('official_result_source_sha256')):
            raise ValueError('CANDIDATE_RESULT_BUNDLE_BINDING_MISMATCH')
        return "ALREADY_SETTLED"
    pre_path=race_dir/"pre_result.json"; final_path=race_dir/"candidate_final.json"
    if not pre_path.exists() or not final_path.exists(): return "PRE_RESULT_NOT_FROZEN"
    pre=json.loads(pre_path.read_text(encoding="utf-8"))
    final=json.loads(final_path.read_text(encoding="utf-8"))
    _verified_pre_frozen(pre,final,race_id)
    post=datetime.fromisoformat(str(pre["scheduled_post_at"]).replace("Z","+00:00"))
    if datetime.now(timezone.utc)<=post+timedelta(minutes=1): return "RESULT_NOT_YET_DUE"
    # Repo commit identity is independent of in-file timestamps.
    import subprocess
    rel=pre_path.relative_to(root).as_posix()
    commit_time=subprocess.check_output(["git","log","-1","--format=%cI","--",rel],
                                       cwd=root,text=True).strip()
    if not commit_time or datetime.fromisoformat(commit_time)>=post:
        raise ValueError("NO_PRE_START_GIT_COMMIT_WITNESS")
    intent_path=root/"runtime"/"jra_formal_intents"/(race_id+"-LIVE-R1.json")
    if not intent_path.exists(): return "JRA_FORMAL_INTENT_MISSING"
    intent=json.loads(intent_path.read_text(encoding="utf-8"))
    if intent.get("race_id")!=race_id or intent.get("venue_id") not in {"KYO","TKY","NKY","HSN","CKY","NGT","FKU","KOK","SAP","HAK"}:
        raise ValueError("INTENT_RACE_OR_VENUE_MISMATCH")
    meeting_key=(intent.get("jra_source") or {}).get("jra_meeting_key")
    validate_result_target(race_id,intent["race_date"],meeting_key,intent["race_no"])
    evidence=fetch_jra_result(intent["race_date"],meeting_key,int(intent["race_no"]))
    outcome=verify_official_result(evidence["parsed"],evidence["text"],pre["ranking"])
    artifacts=settle_frozen_candidate(pre,final,outcome,source_sha256=evidence["sha256"],source_url=evidence["url"])
    source_meta=build_official_result_observation(race_id,evidence,official=outcome)
    artifacts["official_result_observation"]=source_meta
    for key,obj in artifacts.items():
        p=race_dir/(key+".json")
        if p.exists():raise ValueError("RESULT_IMMUTABILITY_VIOLATION:"+key)
        p.write_text(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    return "SETTLED_RECOMMENDATION"


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",default=".")
    p.add_argument("--race-id")
    p.add_argument("--days",type=int,default=3)
    p.add_argument('--health-out')
    args=p.parse_args(argv)
    if args.days < 1 or args.days>14:raise SystemExit("INVALID_DAYS_RANGE")
    root=Path(args.repo_root).resolve()
    dirs=[root/"runtime"/"source_candidate_oos"/args.race_id] if args.race_id else sorted(
        (root/"runtime"/"source_candidate_oos").glob("KM-JRA-*-R??"))
    today=datetime.now(timezone.utc)
    results=[]
    from jra_postresult_health import build_execution_health,write_execution_health,health_exit_code,failure_row
    for d in dirs:
        pre=d/"pre_result.json"
        if not pre.exists():
            if args.race_id:
                results.append({'race_id':d.name,'status':'PRE_RESULT_NOT_FROZEN','persisted':False})
            continue
        stage='READ_FROZEN_PRE_RESULT'
        refs={'pre_result_ref':pre.relative_to(root).as_posix(),
              'frozen_pre_result_sha256':None,'final_ref':(d/'candidate_final.json').relative_to(root).as_posix()}
        try:
            x=json.loads(pre.read_text(encoding="utf-8"))
            refs.update(frozen_pre_result_sha256=x.get('sha256'),source_ref=x.get('source_snapshot_sha256'))
            stage='CHECK_RESULT_DUE_TIME'
            post=datetime.fromisoformat(str(x["scheduled_post_at"]).replace("Z","+00:00"))
            if not args.race_id and not (0 <= (today-post).total_seconds() <= args.days*86400):
                continue
            stage='PROCESS_CANDIDATE_RESULT'
            status=process(root,d.name)
            row=dict(refs,race_id=d.name,status=status,
                persisted=status in ('SETTLED_RECOMMENDATION','ALREADY_SETTLED'))
        except PendingOfficialResult as exc:
            row=dict(refs,race_id=d.name,status='PENDING:'+str(exc),persisted=False,
                first_failed_stage=getattr(exc,'first_failed_stage',None) or stage,
                error_code=str(exc),exception_class=type(exc).__name__,recommendation_pfs=None)
        except Exception as exc:
            row=failure_row(d.name,exc,stage,**refs)
        results.append(row)
    report=build_execution_health('CANDIDATE',results)
    report['profile']=PROFILE
    report=write_execution_health(args.health_out or root/'runtime/source_candidate_oos/settlement_health.json',report)
    print(json.dumps(report,ensure_ascii=False))
    return health_exit_code(report)


if __name__=="__main__":
    raise SystemExit(main())

"""JRA Candidate closed-loop: verified official result -> frozen-ticket settlement -> learning.

This module never changes or backdates PRE_RESULT/FINAL. It does not confer
Production prediction, actual purchase, or signed RESULT authority.
"""
from __future__ import annotations

import argparse
import base64
import http.client
import http.cookiejar
import hashlib
import json
import re
import sys
import time as clock
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "jra_source_runtime"))

from jra_source_candidate_oos import evaluate_result
from jra_source_candidate_promotion_gate import bind_result
from jra_same_day_results import parse_result_detail
from source_acquisition import _decode, _html_text, utcnow

PROFILE = "KM-JRA-CANDIDATE-AUTOMATIC-POSTRESULT-CLOSEDLOOP-20261010-R1"
BET_KINDS = {"EXACTA": ("馬単", 2), "TRIO": ("3連複", 3), "TRIFECTA": ("3連単", 3)}


class PendingOfficialResult(ValueError):
    pass


class OfficialResultAcquisitionError(ValueError):
    """Typed unresolved official observation; absence is never a race result."""
    def __init__(self, reason, *, category, retryable=False, **evidence):
        super().__init__(reason)
        self.category = category
        self.retryable = retryable
        self.evidence = evidence


def result_failure(exc):
    """Public failure metadata, with no cookie/token/credential output."""
    if isinstance(exc, OfficialResultAcquisitionError):
        return {"status": "PENDING" if exc.retryable else "BLOCKED",
                "category": exc.category, "retryable": exc.retryable,
                "reason": str(exc), **exc.evidence}
    if isinstance(exc, urllib.error.HTTPError):
        denied = exc.code in (401, 403, 429)
        retryable = 500 <= exc.code <= 599
        return {"status": "PENDING" if retryable else "BLOCKED",
                "category": "OFFICIAL_ACCESS_DENIED" if denied else "OFFICIAL_HTTP_UNAVAILABLE"
                    if retryable else "OFFICIAL_REQUEST_REJECTED",
                "retryable": retryable, "http_status": exc.code,
                "reason": type(exc).__name__ + ":" + str(exc)}
    if isinstance(exc, PendingOfficialResult):
        manual = any(x in str(exc) for x in ("AMBIGUOUS", "NOT_UNIQUE", "DEAD_HEAT", "FORMAT_INVALID", "MISMATCH"))
        return {"status": "BLOCKED" if manual else "PENDING",
                "category": "OFFICIAL_RESULT_ADJUDICATION_REQUIRED" if manual else "RESULT_NOT_FINAL",
                "retryable": not manual, "reason": str(exc)}
    from jra_pedigree_harvest import retryable_official_error
    transient = retryable_official_error(exc)
    return {"status": "PENDING" if transient else "BLOCKED",
            "category": "OFFICIAL_ACQUISITION_UNAVAILABLE" if transient else "RESULT_INTEGRITY_OR_PARSER_ERROR",
            "retryable": transient, "reason": type(exc).__name__ + ":" + str(exc)}


class _ResultNavigationClient:
    """Existing official result navigation, retaining the actual response bytes.

    Uses the Collector's already observed archive-form parser; it never guesses
    a checksum or tries another authority after access denial. Transient reads
    use the same URL, opener and POST token, with at most three attempts.
    """
    def __init__(self):
        class OfficialRedirectOnly(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                target = urllib.parse.urlsplit(newurl)
                if target.scheme != "https" or target.netloc != "www.jra.go.jp":
                    raise ValueError("JRA_RESULT_REDIRECT_AUTHORITY_FORBIDDEN")
                return super().redirect_request(req, fp, code, msg, headers, newurl)
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()), OfficialRedirectOnly())
        self.last_url = "https://www.jra.go.jp/"
        self.last_raw = b""
        self.last_headers = {}
        self.retry_count = 0

    def _request(self, path, token=None):
        from jra_race_card_detail import _fetch
        from jra_pedigree_harvest import retryable_official_error
        if token is None:
            if not re.fullmatch(r"/keiba/calendar\d{4}/\d{4}/\d{1,2}/\d{4}\.html", path):
                raise ValueError("JRA_RESULT_CALENDAR_PATH_INVALID")
        elif path != "/JRADB/accessS.html":
            raise ValueError("JRA_RESULT_NAVIGATION_ENDPOINT_INVALID")
        data = None if token is None else urllib.parse.urlencode({"cname": token}).encode()
        for attempt in range(3):
            clock.sleep(0.7 if attempt == 0 else 3 * 2 ** (attempt - 1))
            try:
                result = _fetch(self.opener, "https://www.jra.go.jp" + path,
                                data=data, referer=self.last_url)
                self.last_url, self.last_raw, self.last_headers = result
                target = urllib.parse.urlsplit(self.last_url)
                if (target.scheme != "https" or target.netloc != "www.jra.go.jp"
                        or target.path != path):
                    raise ValueError("JRA_RESULT_RESPONSE_AUTHORITY_OR_PATH_INVALID")
                return _decode(self.last_raw, self.last_headers.get("content-type", ""))
            except (OSError, http.client.HTTPException) as exc:
                if (isinstance(exc, urllib.error.HTTPError) and exc.code in (401, 403, 429)):
                    raise  # no retries, alternate origin, identity or token probing
                if not retryable_official_error(exc) or attempt == 2:
                    raise
                self.retry_count += 1

    def get(self, path):
        return self._request(path)

    def post(self, path, token):
        return self._request(path, token)


def verify_result_context(raw, content_type, race_date, meeting_key, race_no):
    """Bind the original result heading, independently of its navigation token."""
    from bs4 import BeautifulSoup
    from jra_race_day_resolver import VENUES
    soup = BeautifulSoup(_decode(raw, content_type), "html.parser")
    head = soup.find("h1")
    text = head.get_text(" ", strip=True) if head is not None else ""
    match = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日[（(][^）)]*[）)]\s*(\d+)回"
                      r"(札幌|函館|福島|新潟|東京|中山|中京|京都|阪神|小倉)(\d+)日\s*(\d+)レース", text)
    if not match:
        raise OfficialResultAcquisitionError("JRA_RESULT_ORIGINAL_HEADING_UNREADABLE", category="RESULT_PARSER_ERROR")
    year, month, day, meeting, venue, meeting_day, number = match.groups()
    identity = (f"{int(year):04d}-{int(month):02d}-{int(day):02d}", venue,
                int(meeting), int(meeting_day), int(number))
    expected = (race_date, VENUES[meeting_key[:2]][1], int(meeting_key[6:8]),
                int(meeting_key[8:]), int(race_no))
    if identity != expected:
        raise OfficialResultAcquisitionError("JRA_RESULT_ORIGINAL_RACE_CONTEXT_MISMATCH", category="RESULT_IDENTITY_CONFLICT")
    return {"race_date": identity[0], "venue": identity[1], "meeting_no": identity[2],
            "meeting_day": identity[3], "race_no": identity[4], "heading_verified": True}


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


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
    """Extract only unambiguous JRA payouts per 100 yen after the LAST 払戻金.

    All three issued bet types must be present. Duplicate, ambiguous, or
    malformed official payout entries fail closed, not silently marked zero.
    """
    if "払戻金" not in text:
        raise PendingOfficialResult("JRA_OFFICIAL_PAYOUT_SECTION_NOT_PUBLISHED")
    # JRA footer also contains 払戻金 (e.g., 払戻金の支払を受けた方へ).
    # Anchor the actual payout table by the adjacent first bet-type label.
    anchors = list(re.finditer(r"払戻金\s+単勝\s+", text))
    if len(anchors) != 1:
        raise PendingOfficialResult("JRA_OFFICIAL_PAYOUT_TABLE_NOT_UNIQUE")
    tail = "単勝 " + text[anchors[0].end():].split("勝馬の紹介",1)[0]
    out = {}
    for kind, (label, count) in BET_KINDS.items():
        pattern = re.escape(label) + r"\s+((?:\d{1,2}\s*-\s*){" + str(count - 1) + r"}\d{1,2})\s+([\d,]+)\s*円"
        matches = re.findall(pattern, tail)
        if len(matches) != 1:
            raise PendingOfficialResult("JRA_PAYOUT_MISSING_OR_AMBIGUOUS:" + kind)
        selection, yen = matches[0]
        nums = [int(x) for x in re.findall(r"\d+", selection)]
        amount = int(yen.replace(",", ""))
        if len(nums) != count or len(set(nums)) != count or amount <= 0:
            raise PendingOfficialResult("JRA_PAYOUT_FORMAT_INVALID:" + kind)
        out[kind] = {"selection": nums, "per_100_yen": amount}
    return out


def verify_official_result(parsed: dict, payout_text: str, frozen_runner_ids: list[str]) -> dict:
    rows = list(parsed.get("runners") or [])
    if parsed.get("official") is not True or not rows:
        raise PendingOfficialResult("JRA_OFFICIAL_RESULT_TABLE_MISSING")
    non_finishers=list(parsed.get("non_finishers") or [])
    ids = [str(r.get("runner_id")) for r in rows+non_finishers]
    if len(set(ids)) != len(ids) or not set(ids).issubset(set(frozen_runner_ids)):
        raise ValueError("OFFICIAL_RESULT_RUNNER_UNIVERSE_MISMATCH")
    top = {}
    for r in rows:
        rank = r.get("finish")
        if rank in (1,2,3):
            if rank in top:
                raise PendingOfficialResult("JRA_DEAD_HEAT_MANUAL_ADJUDICATION_REQUIRED")
            top[rank] = int(r["horse_no"])
    if set(top) != {1,2,3}:
        raise PendingOfficialResult("JRA_TOP3_NOT_CONFIRMED")
    actual = [top[1], top[2], top[3]]
    payouts = parse_official_payouts(payout_text)
    for kind, spec in payouts.items():
        expected = actual[:2] if kind == "EXACTA" else sorted(actual) if kind == "TRIO" else actual
        found = sorted(spec["selection"]) if kind == "TRIO" else spec["selection"]
        if found != expected:
            raise PendingOfficialResult("OFFICIAL_PAYOUT_TOP3_MISMATCH:" + kind)
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
    return {"top3": actual, "payouts": payouts, "refund_runner_ids":refunded,
            "non_finishers":non_finishers,
            "refund_declaration":match.group(0) if match else None}


def settle_frozen_candidate(pre: dict, final: dict, official: dict, *, source_sha256: str, source_url: str) -> dict:
    race_id = str(pre.get("race_id") or "")
    _verified_pre_frozen(pre, final, race_id)
    actual = [int(x) for x in official["top3"]]
    prices = official["payouts"]
    tickets = list(((final.get("mec") or {}).get("tickets") or []))
    if not tickets:
        raise ValueError("FROZEN_MEC_TICKETS_MISSING")
    purchases = []
    refunded = {int(x) for x in official.get("refund_runner_ids") or []}
    if not refunded <= {int(x) for x in pre["ranking"]} or refunded.intersection(actual):
        raise ValueError("OFFICIAL_REFUND_RUNNER_UNIVERSE_OR_FINISH_CONFLICT")
    seen = set()
    stake_total = 0
    return_total = 0
    for ticket in tickets:
        kind = str(ticket.get("bet_type") or "")
        if kind not in BET_KINDS:
            raise ValueError("UNKNOWN_BET_TYPE:" + kind)
        n = BET_KINDS[kind][1]
        sel = [int(x) for x in ticket.get("selection") or []]
        stake = ticket.get("stake")
        if len(sel) != n or len(set(sel)) != n or not isinstance(stake,int) or isinstance(stake,bool) or stake <= 0 or stake % 100:
            raise ValueError("FROZEN_TICKET_INVALID")
        key = (kind, tuple(sorted(sel)) if kind == "TRIO" else tuple(sel))
        if key in seen:
            raise ValueError("DUPLICATE_FROZEN_TICKET")
        seen.add(key)
        pay = prices[kind]
        winner = sorted(pay["selection"]) if kind == "TRIO" else pay["selection"]
        observed = sorted(sel) if kind == "TRIO" else sel
        refund = bool(refunded.intersection(sel))
        amount = stake if refund else (stake // 100) * pay["per_100_yen"] if observed == winner else 0
        purchase = {"bet_type":kind,"selection":sel,"stake":stake,"recommended_return":amount,
                    "win":amount>0 and not refund}
        if refund:
            purchase["official_refund"] = True
        purchases.append(purchase)
        stake_total += stake
        return_total += amount
    required = int((final.get("capital") or {}).get("required_capital") or 0)
    if required != stake_total or int((final.get("mec") or {}).get("ticket_count") or 0) != len(purchases):
        raise ValueError("FROZEN_CAPITAL_CANONICAL_MISMATCH")
    evaluated = evaluate_result(pre, actual)
    bound = bind_result(pre, evaluated)
    if not evaluated["winner_capture"]: first = "W_HEAD_ZERO"
    elif not evaluated["p2_capture"]: first = "P2_SECOND_ZERO"
    elif not evaluated["p3_capture"]: first = "P3_THIRD_ZERO"
    elif not evaluated["ordered_pair_capture"]: first = "ORDERED_PAIR_MISSING"
    elif not evaluated["exact_capture"]: first = "PAIR_CONDITIONED_THIRD_MISSING"
    elif not any(x["win"] for x in purchases): first = "TICKET_CONVERSION_UNREACHABLE"
    elif return_total < stake_total: first = "CAPITAL_EFFICIENCY_LOSS"
    else: first = "NONE"
    owner = "NONE" if return_total >= stake_total else (
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
        "recommended_profit_yen":return_total-stake_total,
        "frozen_recommendation_pfs_percent":round(100*return_total/stake_total,2),
        "actual_purchase_status":"UNVERIFIED","actual_pfs_status":"NOT_VERIFIED",
        "first_material_failure":first,"dominant_pfs_loss_owner":owner,
        "prediction_measurement":evaluated, "oos_eligible":pre["oos_eligible"],
        "result_receipt_status":"OFFICIAL_HTTP_SNAPSHOT_HASH_BOUND / SIGNED_RESULT_NOT_VERIFIED",
        "production_effect":"NONE","automatic_promotion":False,
    }
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


def fetch_jra_result(race_date: str, meeting_key: str, race_no: int, *, client=None) -> dict:
    """Resolve a historical date through the already approved archive reader.

    The old first-menu-only reader could not find older frozen dates once the
    live menu advanced. Never substitute today's race, derive a token checksum,
    or call missing navigation proof a non-existent race.
    """
    from jra_pedigree_harvest import _day_navigation
    from jra_race_day_resolver import VENUES
    date = datetime.fromisoformat(str(race_date)).date().isoformat()
    key = str(meeting_key or "")
    if (not re.fullmatch(r"\d{10}", key) or key[:2] not in VENUES
            or key[2:6] != date[:4] or type(race_no) is not int or not 1 <= race_no <= 12):
        raise OfficialResultAcquisitionError("JRA_RESULT_REQUEST_IDENTITY_INVALID",
                                             category="RACE_REQUEST_NOT_VALID")
    client = client or _ResultNavigationClient()
    try:
        page, entry, days, pattern = _day_navigation(client, date, "results")
    except ValueError as exc:
        # The Collector parser itself verifies the observed official archive
        # form. Unexpected markup is BLOCKED, not an infinite pending result.
        if isinstance(exc, OfficialResultAcquisitionError):
            raise
        raise OfficialResultAcquisitionError(str(exc), category="RESULT_DAY_RESOLUTION_FAILED") from exc
    matches = [token for token in days if re.fullmatch(
        r"pw01srl\d{2}" + re.escape(key + date.replace("-", "")) + r"/[0-9A-Fa-f]{2}", token)]
    if not matches:
        raise OfficialResultAcquisitionError("JRA_RESULT_REQUESTED_DAY_NOT_OBSERVED",
                                             category="RESULT_DAY_NOT_OBSERVED", retryable=True)
    if len(matches) != 1:
        raise OfficialResultAcquisitionError("JRA_RESULT_DAY_NAVIGATION_AMBIGUOUS", category="RESULT_DAY_RESOLUTION_FAILED")
    day_html = client.post(page, matches[0])
    tokens = sorted(set(re.findall(pattern, day_html)))
    candidates = [token for token in tokens if re.fullmatch(
        r"pw01sde\d{2}" + re.escape(key + f"{race_no:02d}" + date.replace("-", "")) + r"/[0-9A-Fa-f]{2}", token)]
    if not candidates:
        # Missing navigation is not independent proof that a race never existed.
        raise OfficialResultAcquisitionError("JRA_OFFICIAL_RESULT_RACE_NOT_OBSERVED",
                                             category="RACE_NOT_OBSERVED", retryable=True)
    if len(candidates) != 1:
        raise OfficialResultAcquisitionError("JRA_RESULT_RACE_NAVIGATION_AMBIGUOUS", category="RESULT_DAY_RESOLUTION_FAILED")
    client.post(page, candidates[0])
    raw, headers = client.last_raw, client.last_headers
    plain = _html_text(_decode(raw, headers.get("content-type", "")))
    if any(label in plain for label in ("該当するレースはありません", "該当する競走はありません")):
        raise OfficialResultAcquisitionError("JRA_OFFICIAL_RACE_DOES_NOT_EXIST",
                                             category="RACE_NOT_FOUND", retryable=False)
    context = verify_result_context(raw, headers.get("content-type", ""), date, key, race_no)
    try:
        parsed = parse_result_detail(raw, headers.get("content-type", ""))
    except ValueError as exc:
        text = _html_text(_decode(raw, headers.get("content-type", "")))
        if any(label in text for label in ("成績未確定", "結果未確定", "レース前")):
            raise PendingOfficialResult("JRA_OFFICIAL_RESULT_NOT_FINAL") from exc
        raise OfficialResultAcquisitionError(str(exc), category="RESULT_PARSER_ERROR") from exc
    return {"parsed": parsed, "text": _html_text(_decode(raw, headers.get("content-type", ""))),
            "sha256": hashlib.sha256(raw).hexdigest(), "captured_at": utcnow(),
            "url": client.last_url, "source_authority": "JRA_OFFICIAL_POST_RESULT",
            "raw_base64": base64.b64encode(raw).decode(), "content_type": headers.get("content-type", ""),
            "context_verification": context, "retry_count": getattr(client, "retry_count", 0)}


def process(root:Path, race_id:str)->str:
    race_dir=root/"runtime"/"source_candidate_oos"/race_id
    result_path=race_dir/"result_evaluation.json"
    required = ["result_evaluation", "settlement", "learning", "official_result_observation"]
    has_output = any((race_dir / (key + ".json")).exists() for key in required)
    pre_path=race_dir/"pre_result.json"; final_path=race_dir/"candidate_final.json"
    if not pre_path.exists() or not final_path.exists():
        if has_output:
            raise ValueError("CANDIDATE_EXISTING_SETTLEMENT_FROZEN_INPUT_MISSING")
        return "PRE_RESULT_NOT_FROZEN"
    pre=json.loads(pre_path.read_text(encoding="utf-8"))
    final=json.loads(final_path.read_text(encoding="utf-8"))
    _verified_pre_frozen(pre,final,race_id)
    if has_output:
        existing = {key: json.loads((race_dir / (key + ".json")).read_text()) for key in required
                    if (race_dir / (key + ".json")).exists()}
        original = existing.get("official_result_observation")
        if original is not None:
            if (original.get("race_id") != race_id or original.get("status") != "OFFICIAL_POST_RESULT_SNAPSHOT"
                    or not re.fullmatch(r"[0-9a-f]{64}", str(original.get("raw_sha256", "")))
                    or not str(original.get("url", "")).startswith("https://www.jra.go.jp/")
                    or datetime.fromisoformat(original["captured_at"]) <= datetime.fromisoformat(pre["scheduled_post_at"])):
                raise ValueError("CANDIDATE_EXISTING_RESULT_OBSERVATION_INVALID")
            expected = settle_frozen_candidate(pre, final,
                {"top3": original["result_top3"], "payouts": original["payouts"],
                 "refund_runner_ids": original.get("refund_runner_ids", [])},
                source_sha256=original["raw_sha256"], source_url=original["url"])
            if any(existing[key] != value for key, value in expected.items() if key in existing):
                raise ValueError("CANDIDATE_EXISTING_SETTLEMENT_ARTIFACT_CONFLICT")
            for key, value in expected.items():
                target = race_dir / (key + ".json")
                if key not in existing:
                    with target.open("x", encoding="utf-8") as stream:
                        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
            return "ALREADY_SETTLED" if len(existing) == len(required) else "SETTLED_RECOMMENDATION"
        # A crash before persisting the observation requires a new official
        # read, then exact comparison of all previously written output bytes.
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
    evidence=fetch_jra_result(intent["race_date"],meeting_key,int(intent["race_no"]))
    outcome=verify_official_result(evidence["parsed"],evidence["text"],pre["ranking"])
    artifacts=settle_frozen_candidate(pre,final,outcome,source_sha256=evidence["sha256"],source_url=evidence["url"])
    source_meta={"profile":PROFILE,"race_id":race_id,"status":"OFFICIAL_POST_RESULT_SNAPSHOT",
                 "raw_sha256":evidence["sha256"],"captured_at":evidence["captured_at"],
                 "url":evidence["url"],"result_top3":outcome["top3"],
                 "payouts":outcome["payouts"],"signed_result_receipt_verified":False}
    if outcome.get("non_finishers") or outcome.get("refund_runner_ids"):
        source_meta.update(non_finishers=outcome["non_finishers"], refund_runner_ids=outcome["refund_runner_ids"],
                           refund_declaration=outcome["refund_declaration"])
    artifacts["official_result_observation"]=source_meta
    for key in ("official_result_observation", "result_evaluation", "settlement", "learning"):
        obj = artifacts[key]
        p=race_dir/(key+".json")
        if p.exists():
            if json.loads(p.read_text()) != obj:
                raise ValueError("RESULT_IMMUTABILITY_VIOLATION:"+key)
            continue
        with p.open("x", encoding="utf-8") as stream:
            json.dump(obj, stream, ensure_ascii=False, sort_keys=True, indent=2)
    return "SETTLED_RECOMMENDATION"


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",default=".")
    p.add_argument("--race-id")
    p.add_argument("--days",type=int,default=3)
    args=p.parse_args()
    if args.days < 1 or args.days>14:raise SystemExit("INVALID_DAYS_RANGE")
    root=Path(args.repo_root).resolve()
    dirs=[root/"runtime"/"source_candidate_oos"/args.race_id] if args.race_id else sorted(
        (root/"runtime"/"source_candidate_oos").glob("KM-JRA-*-R??"))
    today=datetime.now(timezone.utc)
    from jra_research_settlement_manifest import summarize_races
    results=[]
    access_suspended = False
    for d in dirs:
        pre=d/"pre_result.json"
        if not pre.exists():continue
        try:
            x=json.loads(pre.read_text(encoding="utf-8"))
            post=datetime.fromisoformat(str(x["scheduled_post_at"]).replace("Z","+00:00"))
            if not args.race_id and not (0 <= (today-post).total_seconds() <= args.days*86400):
                continue
            if access_suspended and not (d / "result_evaluation.json").exists():
                results.append({"race_id": d.name, "status": "BLOCKED", "retryable": False,
                                "category": "OFFICIAL_ACCESS_SUSPENDED"})
                continue
            status=process(root,d.name)
        except Exception as exc:
            failure = result_failure(exc)
            if failure.get("category") == "OFFICIAL_ACCESS_DENIED":
                access_suspended = True
            results.append({"race_id": d.name, **failure})
            continue
        results.append({"race_id":d.name,"status":status})
    manifest = summarize_races(results)
    print(json.dumps({"profile":PROFILE,"processed":results,"processing_manifest": manifest},ensure_ascii=False))
    if manifest["status"] in {"PARTIAL", "BLOCKED", "PENDING"}:
        raise SystemExit(2)


if __name__=="__main__":
    main()

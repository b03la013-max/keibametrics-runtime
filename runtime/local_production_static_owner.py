"""Owner-requested LOCAL automatic Production Static: signed NAR evidence only.

No 29-index numeric values, AKI Shadow ranks, betting odds or results enter
this owner. The transparent ordinal racing heuristic is unvalidated; its
predictive value must be measured prospectively. Existing Production R3 MEC,
KRS, Capital, source signer, parameter_map, numeric mapping stay unchanged.
This owner may make a Formal Static only through the explicit enabled owner
contract and complete signed SOURCE/Full29 transport gates.
"""
from __future__ import annotations

import base64
import copy
from datetime import datetime, timedelta, timezone
import gzip
import hashlib
from html import unescape
from html.parser import HTMLParser
import json
import re
import unicodedata
from typing import Any

from runtime.local_nar_evidence_candidate import parse_race_card
from runtime.local_physical.nar_source_manifest import VENUE_NAMES

PROFILE = "KM-LOCAL-PRODUCTION-STATIC-EVIDENCE-OWNER-v1.0-20261014"
JST = timezone(timedelta(hours=9))


class StaticOwnerError(ValueError):
    pass


def _sha(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _dt(s: str) -> datetime:
    try:
        out = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise StaticOwnerError("STATIC_OWNER_CLOCK_INVALID") from exc
    if out.tzinfo is None:
        raise StaticOwnerError("STATIC_OWNER_NAIVE_TIME_FORBIDDEN")
    return out.astimezone(timezone.utc)


class _VisibleText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.fragments = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.hidden += 1
        elif tag in {"div", "p", "h1", "h2", "h3", "td", "th", "li", "dt", "dd", "tr"}:
            self.fragments.append(" ")

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.hidden = max(0, self.hidden - 1)
        else:
            self.fragments.append(" ")

    def handle_data(self, data):
        if not self.hidden:
            self.fragments.append(data)


def _card_heading(source_artifact: dict, *, expected_race: dict | None = None) -> dict:
    sources = source_artifact.get("sources") or []
    main = next((x for x in sources if x.get("source_class") == "OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT"
                 and x.get("official") is True and x.get("cutoff_relation") == "PRE_CUTOFF"), None)
    if not main or not main.get("raw_gzip_b64"):
        raise StaticOwnerError("SIGNED_OFFICIAL_RACE_CARD_RAW_REQUIRED")
    try:
        raw = gzip.decompress(base64.b64decode(main["raw_gzip_b64"], validate=True))
        try:
            page = raw.decode("utf-8")
        except UnicodeError:
            page = raw.decode("cp932")
    except (ValueError, OSError, UnicodeError) as exc:
        raise StaticOwnerError("OFFICIAL_RACE_CARD_DECODE_FAILED") from exc
    parser = _VisibleText()
    parser.feed(page)
    visible = re.sub(r"\s+", " ", unicodedata.normalize("NFKC", unescape("".join(parser.fragments))))
    # Important: use only race HEADER, never historical starts that follow
    # the official 競走馬 table. A requested course/distance is never guessed.
    head = re.split(r"競走馬|枠番", visible, maxsplit=1)[0]
    if expected_race is not None:
        # URL/context labels originate in the request. Verify the independent
        # printed race header before its distance/class can feed calculation.
        y, m, d = map(int, str(expected_race["race_date"]).split("-"))
        printed = re.sub(r"\s+", "", head)
        pattern = (rf"{y}年{m}月{d}日.{{0,30}}浦和.{{0,12}}"
                   rf"第{int(expected_race['race_no'])}競走")
        if not re.search(pattern, printed):
            raise StaticOwnerError("URW_NUMERICAL_CARD_BODY_IDENTITY_MISMATCH")
    candidates = []
    for match in re.finditer(r"(?:ダート|芝)[^0-9]{0,24}(\d{3,4})\s*[mｍ]|(\d{3,4})\s*[mｍ][^0-9]{0,24}(?:ダート|芝)", head):
        candidates.append((int(match.group(1) or match.group(2)), match.group(0)))
    if len({x[0] for x in candidates}) != 1:
        raise StaticOwnerError("OFFICIAL_RACE_DISTANCE_NOT_UNAMBIGUOUS")
    dist, witness = candidates[0]
    surface = "turf" if "芝" in witness and "ダート" not in witness else "dirt"
    if surface != "dirt" or not 800 <= dist <= 2600:
        raise StaticOwnerError("LOCAL_DIRT_DISTANCE_OUT_OF_SCOPE")
    classes = re.findall(r"(?<![A-Z0-9])([ABC][1-3])(?:選定馬|[一二三四五六七八九十 ]|$)", head.upper())
    class_label = classes[0] if classes else "UNKNOWN"
    # URW headers also use B3イC1ア / C2選抜馬. Preserve each explicitly
    # printed class token for the existing class transform; never invent one.
    from urllib.parse import parse_qs, urlsplit
    if parse_qs(urlsplit(main.get("final_url", "")).query).get("k_babaCode") == ["18"]:
        classes = re.findall(r"(?<![A-Z0-9])([ABC][1-3])(?=[^A-Z0-9]|$)", head.upper())
        class_label = "_".join(dict.fromkeys(classes)) if classes else "UNKNOWN"
    return {"distance": dist, "surface": surface, "class": class_label,
            "header_witness": witness, "header_sha256": hashlib.sha256(head.encode()).hexdigest()}


def _start_date(raw: str) -> datetime | None:
    match = re.fullmatch(r"(\d{2})\.(\d{2})\.(\d{2})", str(raw))
    if not match:
        return None
    try:
        return datetime(2000 + int(match.group(1)), int(match.group(2)), int(match.group(3)), tzinfo=JST)
    except ValueError:
        return None


def bind_urw_numerical_context(request: dict, source: dict) -> dict:
    """Bind the existing URW materializer to the verified card, not distance 0.

    SOURCE signature/Authority verification belongs to the existing caller.
    This supplies observed inputs only; it grants no predictive consumer scope.
    Frozen numerical artifacts are never passed through this function on readback.
    """
    out = copy.deepcopy(request)
    if request.get("venue_id") != "URW":
        return out
    from runtime.local_physical.source_acquisition import verify_source_artifact
    valid, errors = verify_source_artifact(source)
    if not valid:
        raise StaticOwnerError("URW_NUMERICAL_SOURCE_INVALID:" + ",".join(errors))
    context = source.get("source_race_context")
    if (source.get("race_id") != request.get("race_id")
            or (context is not None and any(
                str(context.get(k)).replace("/", "-") != str(request.get(k))
                for k in ("venue_id", "race_date", "race_no")))):
        raise StaticOwnerError("URW_NUMERICAL_SOURCE_RACE_MISMATCH")
    header = _card_heading(source, expected_race=request)
    observed = {"venue_id": "URW", "race_date": request["race_date"],
                "race_no": request["race_no"], "distance": header["distance"],
                "surface": header["surface"], "class": header["class"]}
    race = out.get("race") or {}
    if not isinstance(race, dict):
        raise StaticOwnerError("URW_NUMERICAL_RACE_CONTEXT_INVALID")
    for key, value in observed.items():
        if key in race and race[key] not in (None, "", "UNKNOWN", value):
            raise StaticOwnerError("URW_NUMERICAL_RACE_CONTEXT_CONFLICT:" + key)
    if race.get("venue") not in (None, "", "URW", "浦和"):
        raise StaticOwnerError("URW_NUMERICAL_RACE_CONTEXT_CONFLICT:venue")
    out["race"] = {**race, **observed}
    card = next(s for s in source["sources"]
                if s.get("source_class") == "OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT"
                and s.get("official") is True and s.get("cutoff_relation") == "PRE_CUTOFF")
    from urllib.parse import urlsplit, parse_qs
    url = urlsplit(card["final_url"])
    query = parse_qs(url.query)
    if (url.scheme != "https" or url.hostname != "www.keiba.go.jp"
            or url.path != "/KeibaWeb/TodayRaceInfo/DebaTable"
            or any(query.get(k) != [v] for k, v in {
                "k_babaCode": "18", "k_raceDate": request["race_date"].replace("-", "/"),
                "k_raceNo": str(request["race_no"])}.items())):
        raise StaticOwnerError("URW_NUMERICAL_CARD_IDENTITY_MISMATCH")
    out["numerical_race_context_source"] = {
        "source_id": card["source_id"], "raw_sha256": card["raw_sha256"],
        "snapshot_sha256": card["snapshot_sha256"],
        "source_snapshot_sha256": source["source_snapshot_sha256"],
        "fetched_at": card["fetched_at"], "header_sha256": header["header_sha256"],
        "observed_fields": observed,
        "signature_verification": "EXISTING_SOURCE_CALLER_REQUIRED_NOT_GRANTED_HERE",
    }
    return out


def _runner_facts(row: dict, *, venue_name: str, distance: int, race_day: datetime) -> dict:
    obs = []
    observed_day = None
    if venue_name == "浦和" and row.get("race_card_fetched_at"):
        observed_day = _dt(row["race_card_fetched_at"]).astimezone(JST).date()
    for start in row.get("starts") or []:
        past = _start_date(start.get("date"))
        if past is None or past >= race_day:
            # Future-dated historical data must be a hard failure, not discarded
            if past is not None and past >= race_day:
                raise StaticOwnerError("NON_PRESTART_HISTORICAL_START")
            continue
        if observed_day is not None and past.date() > observed_day:
            raise StaticOwnerError("HISTORICAL_START_AFTER_SOURCE_OBSERVATION")
        if start.get("surface") != "DIRT":
            continue
        field = int(start.get("field_size") or 0)
        finish = int(start.get("finish") or 0)
        if field < 2 or finish < 1 or finish > field:
            continue
        same_venue = str(start.get("venue") or "").replace("ナ", "") == venue_name
        same_distance = start.get("distance") == distance
        exact = same_venue and same_distance
        pos = start.get("content_positions") or []
        obs.append({"date": past.date().isoformat(), "place": start.get("venue"),
                    "distance": start.get("distance"), "finish": finish, "field": field,
                    "exact": exact, "same_venue": same_venue,
                    "podium": finish <= 3, "win": finish == 1,
                    "finish_share": (field - finish) / (field - 1),
                    "last_turn": pos[-1] if pos else None,
                    "race_name": start.get("race_name"),
                    "raw_reference": start.get("raw")})
    if venue_name == "浦和":
        # Provider tables and resumed observations need not retain newest-first
        # order. "Recent" is the latest observed date, never the first row.
        # This corrects source ordering only; the existing ordinal keys stay.
        obs.sort(key=lambda x: x["date"], reverse=True)
    exact_rows = [x for x in obs if x["exact"]]
    venue_rows = [x for x in obs if x["same_venue"]]
    # Strict ordinal hierarchy over known observed records (not calibrated
    # numeric predictions): matched win, matched podium, matched placement,
    # local fallback, then other dirt; UNKNOWNs retain third-column protection.
    def best(group):
        return max((x["finish_share"] for x in group), default=None)
    return {
        "exact_races": len(exact_rows),
        "exact_wins": sum(x["win"] for x in exact_rows),
        "exact_podiums": sum(x["podium"] for x in exact_rows),
        "exact_best_finish_share": best(exact_rows),
        "venue_best_finish_share": best(venue_rows),
        "dirt_best_finish_share": best(obs),
        "recent_dirt_finish_share": obs[0]["finish_share"] if obs else None,
        "observed_runs": obs,
        "unknown_exact_course": not exact_rows,
    }


def build_formal_static(request: dict, envelope: dict, numerical: dict, *,
                        policy: dict, now: datetime | None = None) -> tuple[dict, dict]:
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise StaticOwnerError("STATIC_FREEZE_NAIVE")
    now = now.astimezone(timezone.utc)
    if (policy.get("profile") != PROFILE or policy.get("enabled") is not True
            or policy.get("owner_authorization") != "EXPLICIT_USER_INSTRUCTION_20261014"
            or policy.get("numerical_prediction_consumption") is not False):
        raise StaticOwnerError("STATIC_OWNER_AUTHORIZATION_MISSING")
    if request.get("family_id") != "LOCAL":
        raise StaticOwnerError("LOCAL_ONLY")
    venue = str(request.get("venue_id") or "")
    if venue not in set(policy.get("venues") or []) or venue not in VENUE_NAMES:
        raise StaticOwnerError("VENUE_OWNER_NOT_AUTHORIZED")
    cutoff = _dt(request.get("prediction_cutoff"))
    release = _dt(request.get("release_deadline_at"))
    if now >= cutoff or now >= release:
        raise StaticOwnerError("PRESTART_STATIC_OWNER_DEADLINE_HOLD")
    if not isinstance(envelope, dict) or not envelope.get("signature") or not envelope.get("receipt_sha256"):
        raise StaticOwnerError("SOURCE_SIGNATURE_REQUIRED")
    receipt = envelope.get("receipt") or {}
    if (receipt.get("phase") != "SOURCE" or receipt.get("status") != "SOURCE_FROZEN"
            or receipt.get("race_id") != request.get("race_id")):
        raise StaticOwnerError("SIGNED_SOURCE_RACE_MISMATCH")
    source = envelope.get("artifact") or {}
    if source.get("formal_ready") is not True or _dt(source.get("source_freeze_at")) >= cutoff:
        raise StaticOwnerError("OFFICIAL_SOURCE_NOT_PRESTART_FROZEN")
    official = source.get("source_race_context") or {}
    if (official.get("venue_id") != venue
            or str(official.get("race_date") or "").replace("/", "-") != request.get("race_date")
            or int(official.get("race_no") or 0) != int(request.get("race_no") or 0)):
        raise StaticOwnerError("OFFICIAL_SOURCE_IDENTITY_MISMATCH")
    official_post = (source.get("normalized_evidence") or {}).get("start_time") or {}
    if (official_post.get("authority") != "NAR_OFFICIAL"
            or official_post.get("cutoff_relation") != "PRE_CUTOFF"
            or official_post.get("value") != _dt(request.get("scheduled_post_at")).astimezone(JST).strftime("%H:%M")):
        raise StaticOwnerError("OFFICIAL_SOURCE_POST_MISMATCH")
    if (numerical.get("strict_full_numerical_ready") is not True
            or (numerical.get("production_numerical_authority") or {}).get("prediction_consumption_authorized") is not False
            or len(numerical.get("required_indices") or []) != 29):
        raise StaticOwnerError("NUMERICAL_CLOSURE_ONLY_NOT_PREDICTIVE")
    pool = (source.get("active_runner_universe") or source.get("official_runner_universe") or {}).get("runners") or []
    ids = [str(r.get("runner_id")) for r in pool]
    if len(pool) < 2 or len(ids) != len(set(ids)) or set(ids) != {str(r.get("runner_id")) for r in numerical.get("runners") or []}:
        raise StaticOwnerError("FULL_RUNNER_UNIVERSE_MISMATCH")
    parsed = parse_race_card(source)
    declared = (source.get("declared_runner_universe") or {}).get("runners") or []
    declared_ids = [str(x.get("runner_id")) for x in declared]
    status_rows = source.get("runner_status_registry") or []
    registered = {str(x.get("runner_id")): x for x in status_rows}
    if (len(registered) != len(status_rows) or len(declared_ids) != len(set(declared_ids))
            or set(declared_ids) != set(parsed) or set(declared_ids) != set(registered)
            or not set(ids).issubset(set(declared_ids))):
        raise StaticOwnerError("OFFICIAL_DECLARED_UNIVERSE_STATUS_MISMATCH")
    if {rid for rid, v in registered.items() if v.get("status") == "ACTIVE"} != set(ids):
        raise StaticOwnerError("OFFICIAL_ACTIVE_STATUS_UNIVERSE_MISMATCH")
    official_ids = {str(s.get("source_id")) for s in source.get("sources") or []
                    if s.get("official") is True and s.get("cutoff_relation") == "PRE_CUTOFF"}
    for rid in set(declared_ids) - set(ids):
        entry = registered[rid]
        if (entry.get("status") != "CANCELLED"
                or entry.get("reason") != "EXPLICIT_OFFICIAL_ODDS_CANCELLATION"):
            raise StaticOwnerError("OFFICIAL_CANCELLATION_NOT_VERIFIED:" + rid)
        if (not entry.get("evidence_sources")
                or not set(entry["evidence_sources"]).issubset(official_ids)):
            raise StaticOwnerError("OFFICIAL_CARD_RUNNER_MISMATCH")
    # NAR race-card HTML may still include withdrawn runners. Only the
    # official signed ACTIVE universe receives Production prediction roles.
    parsed = {rid: row for rid, row in parsed.items() if rid in set(ids)}
    if set(ids) != set(parsed):
        raise StaticOwnerError("OFFICIAL_CARD_RUNNER_MISMATCH")
    for row in pool:
        rid = str(row["runner_id"])
        if str(parsed[rid]["name"]) != str(row["name"]):
            raise StaticOwnerError("OFFICIAL_CARD_NAME_MISMATCH")
    header = _card_heading(source, expected_race=request if venue == "URW" else None)
    day = _dt(request["scheduled_post_at"]).astimezone(JST).replace(hour=0, minute=0, second=0, microsecond=0)
    facts = {rid: _runner_facts(parsed[rid], venue_name=VENUE_NAMES[venue],
                                distance=header["distance"], race_day=day) for rid in ids}
    # Known observations always outrank a guessed value, but UNKNOWN is not an
    # inference of weak ability and is protected in P3. This ordering is an
    # owner-authorized ordinal baseline awaiting genuine future OOS testing.
    def rank_key(rid):
        f = facts[rid]
        values = (f["exact_wins"], f["exact_podiums"],
                  f["exact_best_finish_share"], f["venue_best_finish_share"],
                  f["recent_dirt_finish_share"], f["dirt_best_finish_share"])
        return tuple(-float(v) if v is not None else 0 for v in values) + (int(rid),)
    ranked = sorted(ids, key=rank_key)
    n = len(ranked)
    heads = ranked[:min(n, 3)]
    seconds = ranked[:min(n, 6)]
    thirds = ranked[:min(n, 9)]
    unknown = [rid for rid in ranked if facts[rid]["unknown_exact_course"]]
    if unknown and not any(x in thirds for x in unknown) and n > len(thirds):
        thirds = thirds[:-1] + [unknown[0]]
    # Maintain complete 3rd-role information; no horse is discarded from
    # analysis because it lacks exact venue/distance experience.
    roles = {rid: [col for col, pool_ in (("W", heads), ("P2", seconds))
                    if rid in pool_] + ["P3"] for rid in ranked}
    role_registry = [
        {"runner_id": rid, "column": col, "status": ("CORE" if rid in heads else "PROTECTED")}
        for rid in ranked for col in ("W", "P2", "P3")
        if col in roles[rid]
    ]
    pairs, thirds_matrix = [], []
    for h in heads:
        for p in seconds:
            if h == p:
                continue
            pairs.append({"head": h, "second": p, "status": "PURCHASE",
                          "reason": "OFFICIAL_PRESTART_ORDINAL_HEAD_LOCAL_PAIR / SAME_CARD_SOURCE"})
            for third in thirds:
                if third in {h, p}:
                    continue
                thirds_matrix.append({"head": h, "second": p, "third": third,
                                      "status": "PURCHASE",
                                      "reason": "OFFICIAL_PRESTART_THIRD_ROW / UNKNOWN_PROTECTED"})
    for h in heads:
        for p in ids:
            if h == p or p in seconds:
                continue
            pairs.append({"head": h, "second": p, "status": "SEMANTIC_ONLY",
                          "reason": "FULL_P2_UNIVERSE_AUDIT / NOT_PURCHASED"})
    marks = {rid: "◎" if i == 0 else "○" if i == 1 else "▲" if i == 2 else "△"
             for i, rid in enumerate(ranked)}
    enriched = []
    for row in pool:
        x = copy.deepcopy(row)
        d = parsed[str(row["runner_id"])]
        x["jockey"] = d["current_jockey"]
        x["assigned_weight"] = d["current_load"]
        enriched.append(x)
    request_ = copy.deepcopy(request)
    request_.pop("execution_phase", None)
    request_.pop("analysis_only", None)
    request_.update({
        "execution_phase": "AUTO",
        "race": {"race_id": request["race_id"], "venue": venue,
                 "venue_id": venue, "race_date": request["race_date"],
                 "race_no": request["race_no"], "surface": header["surface"],
                 "course": "left" if venue in {"KAW", "FNB", "MOR", "URW"} else "right",
                 "distance": header["distance"], "class": header["class"]},
        "runners": enriched,
        "required_indices": numerical["required_indices"],
        "run_count": 5000,
        "seed": int(str(request["race_date"]).replace("-", "") + str(request["race_no"]).zfill(2)),
        "static_prediction_frozen": True,
        "static_prediction": {
            "status": "FROZEN / OWNER-AUTHORIZED / RULE-BASED-UNVALIDATED / RESULT-BLIND",
            "ranking": ranked, "marks": marks, "roles": roles,
            "uncertainty": {rid: ("EXACT_COURSE_UNKNOWN / PROTECTED_NOT_WEAK" if facts[rid]["unknown_exact_course"]
                                  else "EXACT_COURSE_OBSERVED") for rid in ranked},
            "source_basis_receipt_sha256": envelope["receipt_sha256"],
            "source_basis_snapshot_sha256": source["source_snapshot_sha256"],
        },
        "venue_canon": policy["venue_canons"][venue],
        "venue_prediction_context": {
            "canon": policy["venue_canons"][venue],
            "course": f"{venue}_DIRT_{header['distance']}",
            "current_track_state": str((source.get("normalized_evidence") or {}).get("track_condition", {}).get("value")),
            "prediction_mechanisms": ["OFFICIAL_EXACT_COURSE_OBSERVATIONS",
                                      "PRESTART_SOURCE_BASIS", "MISSINGNESS_THIRD_PROTECTION"],
            "race_specific_context": {"official_runner_count": n,
                                      "source_receipt_sha256": envelope["receipt_sha256"],
                                      "owner_profile": PROFILE, "header_witness": header["header_witness"]},
            "temporal_status": "PRESTART_FROZEN_NO_RESULT"},
        "role_registry": role_registry,
        "pair_dispositions": pairs,
        "third_dispositions": thirds_matrix,
        "capital_policy": {"mode": "RECOMMENDATION_ONLY"},
        "require_full_numerical_authority": True,
        "production_numerical_claim": True,
        "degraded_execution": False,
        "source_policy": "CURRENT_LOCAL_OFFICIAL_NAR",
    })
    ledger = {"profile": PROFILE, "status": "OWNER_AUTHORIZED_UNVALIDATED_PRESTART_STATIC",
              "execution_id": request["execution_id"], "frozen_at": now.isoformat(),
              "source_receipt_sha256": envelope["receipt_sha256"],
              "source_snapshot_sha256": source["source_snapshot_sha256"],
              "raw_header_sha256": header["header_sha256"], "official_distance": header["distance"],
              "full_universe": ranked, "observed_facts": facts,
              "uncalibrated": True, "numerical_prediction_consumption": False,
              "odds_consumed": False, "result_consumed": False, "empirical_oos_validated": False,
              "canonical_production_suite_changed": False,
              "formal_intent_sha256": _sha(request_)}
    ledger["sha256"] = _sha(ledger)
    return request_, ledger

"""KM LOCAL Physical Runtime v1.6 — Rakuten keiba race card as an approved formal SOURCE.

Owner instructions 2026-11-16 16:26 / 16:32 JST: use 楽天競馬 as the formal SOURCE
(keiba.go.jp /KeibaWeb/TodayRaceInfo/ is disallowed for crawlers by its robots.txt),
and extend the formal Static Owner to all 14 NAR flat venues.

Additive wrapper over app_v15 (unchanged): the NAR profile behaves exactly as before.
For the Rakuten profile the runtime itself fetches the public race card
(robots.txt checked, Crawl-delay honoured by source_acquisition), freezes the raw
bytes, extracts the declared/active runner universe from that card and signs the
SOURCE receipt. PRE_KRS / FINAL / FORMAL accept either approved profile and apply the
same runner-universe checks to both.
"""
from __future__ import annotations

import re
from typing import Any, Dict

from fastapi import HTTPException

import app_v15 as v15
from app_v15 import app, legacy, NAR_MANIFEST_PROFILE  # noqa: F401  (app is served)
from nar_runner_universe import validate_krs_horses, _sha
import source_acquisition as _sa
from source_acquisition import acquire_sources, sha_obj, verify_source_artifact
import rakuten

APP_VERSION = "KM-LOCAL-PHYSICAL-RUNTIME-v1.6-REV.2-20261116-RAKUTEN-SOURCE"
RAKUTEN_PROFILE = "KM-LOCAL-RAKUTEN-SOURCE-MANIFEST-v1.0-20261116"
APPROVED_PROFILES = {NAR_MANIFEST_PROFILE, RAKUTEN_PROFILE}
RAKUTEN_BABA = {"MOR": "10", "MIZ": "11", "URW": "18", "FNB": "19", "OHI": "20", "KAW": "21",
                "KNZ": "22", "KSM": "23", "NGY": "24", "SON": "27", "HIM": "28", "KCH": "31",
                "SAG": "32", "MON": "36"}
VENUE_NAMES = {"MOR": "盛岡", "MIZ": "水沢", "URW": "浦和", "FNB": "船橋", "OHI": "大井", "KAW": "川崎",
               "KNZ": "金沢", "KSM": "笠松", "NGY": "名古屋", "SON": "園田", "HIM": "姫路", "KCH": "高知",
               "SAG": "佐賀", "MON": "門別"}
# /health and receipt runtime_revision stay v1.5 REV.8 (existing gateway checks); the
# extension is identified by source_manifest_profile + runtime_extension and /health16.


_V15_ROBOTS_POLICY = _sa._literal_robots_policy


def _rfc9309_robots_policy(text: str, robots_url: str) -> Dict[str, Any]:
    """RFC 9309 2.2.1: several groups for the same user-agent are combined.
    The pinned v1.5 parser refuses a repeated '*' group (Rakuten publishes two).
    Merging only ever adds rules / delay; every other refusal is kept."""
    try:
        return _V15_ROBOTS_POLICY(text, robots_url)
    except ValueError as e:
        if str(e) != "ROBOTS_REPEATED_DEFAULT_GROUP_UNSUPPORTED":
            raise
    blocks, cur = [], None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        key = line.split(":", 1)[0].strip().lower() if ":" in line else ""
        if key == "user-agent" and (cur is None or cur["directives"]):
            cur = {"agents": [], "lines": [], "directives": False}
            blocks.append(cur)
        if cur is None or not line:
            continue
        if key == "user-agent":
            cur["agents"].append(line.split(":", 1)[1].strip())
        elif key in ("allow", "disallow", "crawl-delay", "request-rate"):
            cur["lines"].append(line)
            cur["directives"] = True
    star = [b for b in blocks if "*" in b["agents"]]
    others = [b for b in blocks if "*" not in b["agents"]]
    merged = []
    for b in others:
        merged += ["User-agent: " + a for a in b["agents"]] + b["lines"] + [""]
    merged += ["User-agent: *"] + [ln for b in star for ln in b["lines"]]
    return _V15_ROBOTS_POLICY("\n".join(merged) + "\n", robots_url)


_sa._literal_robots_policy = _rfc9309_robots_policy
# Honour a published Crawl-delay (Rakuten: 60 s) instead of refusing after 30 s; NAR (10 s) unaffected.
_sa._POLICY_MAX_WAIT = 75.0
# The Owner-approved Rakuten formal SOURCE host (exact host only, no wildcard).
if "keiba.rakuten.co.jp" not in _sa.DEFAULT_ALLOWED_HOSTS:
    _sa.DEFAULT_ALLOWED_HOSTS.append("keiba.rakuten.co.jp")


def _drop_routes(*paths):
    app.router.routes[:] = [r for r in app.router.routes
                            if not (getattr(r, "path", None) in paths and "POST" in (getattr(r, "methods", None) or set()))]


def rakuten_manifest(payload: Dict[str, Any]) -> Dict[str, Any]:
    venue = str(payload.get("venue_id") or "")
    rid = str(payload.get("rakuten_race_id") or "")
    date8 = str(payload.get("race_date") or "").replace("-", "")
    race_no = int(payload.get("race_no") or 0)
    if venue not in RAKUTEN_BABA:
        raise ValueError("RAKUTEN_VENUE_NOT_IN_SCOPE")
    if not re.fullmatch(r"\d{18}", rid):
        raise ValueError("RAKUTEN_RACE_ID_INVALID")
    if rid[:8] != date8 or rid[8:10] != RAKUTEN_BABA[venue] or int(rid[-2:]) != race_no:
        raise ValueError("RAKUTEN_RACE_ID_CONTEXT_MISMATCH")
    return {"profile": RAKUTEN_PROFILE, "sources": [{
        "source_id": "RAKUTEN_RACE_CARD", "url": "https://keiba.rakuten.co.jp/race_card/list/RACEID/" + rid,
        "source_class": "RAKUTEN_RACE_CARD_CURRENT_STATE", "authority": "RAKUTEN_KEIBA_PUBLIC_CARD",
        "priority": 90, "official": False, "required": True, "extract": []}]}


def _rakuten_universe(artifact: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
    import base64
    import gzip
    snap = next(s for s in artifact.get("sources") or [] if s.get("source_id") == "RAKUTEN_RACE_CARD")
    html = gzip.decompress(base64.b64decode(snap["raw_gzip_b64"])).decode("utf-8", errors="replace")
    head = rakuten.parse_header(html)
    if head.get("race_no") != int(ctx["race_no"]):
        raise ValueError("RAKUTEN_CARD_RACE_NO_MISMATCH")
    if VENUE_NAMES[ctx["venue_id"]] not in rakuten.nfkc(head.get("venue_name_page") or ""):
        raise ValueError("RAKUTEN_CARD_VENUE_MISMATCH")
    active_rows, cancelled_rows = rakuten.parse_card(html)
    declared = [{"runner_id": str(r["horse_no"]), "horse_no": r["horse_no"], "name": r["name"],
                 "frame_no": r["frame_no"], "jockey": r.get("current_jockey"), "load": r.get("current_load"),
                 "body_weight": r.get("current_body_weight"), "win_odds": r.get("win_odds")}
                for r in sorted(active_rows + cancelled_rows, key=lambda x: x["horse_no"])]
    if len({d["horse_no"] for d in declared}) != len(declared):
        raise ValueError("RAKUTEN_CARD_DUPLICATE_HORSE_NO")
    cancelled = {r["horse_no"] for r in cancelled_rows}
    statuses = [{"runner_id": d["runner_id"], "name": d["name"],
                 "status": "CANCELLED" if d["horse_no"] in cancelled else "ACTIVE_DECLARED",
                 "reason": "EXPLICIT_RACE_CARD_CANCELLATION" if d["horse_no"] in cancelled else "PRESENT_ON_CURRENT_RACE_CARD",
                 "evidence_sources": ["RAKUTEN_RACE_CARD"]} for d in declared]
    active = [d for d in declared if d["horse_no"] not in cancelled]
    if len(active) < 2:
        raise ValueError("RAKUTEN_ACTIVE_RUNNERS_LT_2")

    def universe(kind, rows, extra=None):
        u = {"profile": RAKUTEN_PROFILE, "universe_type": kind, "source_id": "RAKUTEN_RACE_CARD",
             "source_snapshot_sha256": snap.get("snapshot_sha256"), "runner_count": len(rows), "runners": rows}
        u.update(extra or {})
        u["runner_universe_sha256"] = _sha(u)
        return u
    dec = universe("DECLARED", declared)
    act = universe("ACTIVE", active, {"status_registry_sha256": _sha(statuses)})
    artifact.update({
        "rakuten_card_header": head,
        "declared_runner_universe": dec, "active_runner_universe": act,
        "runner_status_registry": statuses, "runner_status_registry_sha256": _sha(statuses),
        "official_runner_universe": act, "official_runner_universe_sha256": act["runner_universe_sha256"],
        "official_declared_runner_universe_sha256": dec["runner_universe_sha256"],
        "source_authority_basis": "OWNER_INSTRUCTION_20261116_RAKUTEN_FORMAL_SOURCE",
        "runtime_extension": APP_VERSION,
    })
    return artifact


def _require_source_receipt(payload: Dict[str, Any], race_id: str) -> Dict[str, Any]:
    env = payload.get("source_receipt")
    if not isinstance(env, dict):
        raise HTTPException(422, "SOURCE_RECEIPT_REQUIRED")
    if not legacy.verify_envelope(env):
        raise HTTPException(422, "SOURCE_RECEIPT_SIGNATURE_INVALID")
    rec = env.get("receipt") or {}
    if rec.get("phase") != "SOURCE":
        raise HTTPException(422, "SOURCE_RECEIPT_PHASE_INVALID")
    if rec.get("status") != "SOURCE_FROZEN":
        raise HTTPException(422, "SOURCE_RECEIPT_NOT_FROZEN")
    if str(rec.get("race_id") or "") != str(race_id):
        raise HTTPException(422, "SOURCE_RECEIPT_RACE_ID_MISMATCH")
    valid, errors = verify_source_artifact(env.get("artifact") or {})
    if not valid:
        raise HTTPException(422, "SOURCE_ARTIFACT_INVALID:" + ",".join(errors))
    if (env.get("artifact") or {}).get("source_manifest_profile") not in APPROVED_PROFILES:
        raise HTTPException(422, "SOURCE_CONSUMER_NOT_AUTHORIZED")
    return env


_V15_SOURCE_ACQUIRE = v15.source_acquire   # original NAR path (kept unchanged)
v15._require_source_receipt = _require_source_receipt   # used by v15 routes we keep (none below)
_drop_routes("/source/manifest/local", "/source/acquire", "/pre-krs", "/final", "/formal")


@app.post("/source/manifest/local")
def source_manifest_local(payload: Dict[str, Any]):
    legacy.validate_family(payload)
    try:
        if payload.get("manifest_profile") == RAKUTEN_PROFILE:
            return rakuten_manifest(payload)
        return v15.build_local_nar_manifest(payload)
    except ValueError as e:
        raise HTTPException(422, str(e))


@app.post("/source/acquire")
def source_acquire(payload: Dict[str, Any]):
    if payload.get("manifest_profile") != RAKUTEN_PROFILE:
        return _V15_SOURCE_ACQUIRE(payload)
    legacy.validate_family(payload)
    race_id = str(payload.get("race_id") or "")
    if not race_id:
        raise HTTPException(422, "RACE_ID_REQUIRED")
    try:
        manifest = rakuten_manifest(payload)
    except ValueError as e:
        raise HTTPException(422, str(e))
    req = dict(payload, sources=manifest["sources"])     # caller-supplied URLs are never used
    artifact, errors = acquire_sources(req)
    ctx = {"venue_id": payload.get("venue_id"), "race_date": payload.get("race_date"), "race_no": payload.get("race_no"),
           "rakuten_race_id": payload.get("rakuten_race_id")}
    artifact["source_manifest_profile"] = RAKUTEN_PROFILE
    artifact["source_race_context"] = ctx
    if not errors:
        try:
            artifact = _rakuten_universe(artifact, ctx)
        except Exception as e:
            errors = list(errors) + ["RAKUTEN_RUNNER_UNIVERSE_EXTRACTION_FAILED:" + str(e)]
    artifact["formal_ready"] = not errors
    artifact["errors"] = list(dict.fromkeys(errors))
    artifact["source_snapshot_sha256"] = sha_obj({k: v for k, v in artifact.items() if k != "source_snapshot_sha256"})
    status = "SOURCE_FROZEN" if not artifact["errors"] else "FAIL"
    return legacy.signed_receipt("SOURCE", race_id, status, artifact, artifact["errors"])


@app.post("/pre-krs")
def pre_krs(payload: Dict[str, Any]):
    legacy.validate_family(payload)
    race_id = str(payload.get("race_id") or "")
    source = _require_source_receipt(payload, race_id)
    ok, errs = validate_krs_horses(source.get("artifact") or {}, payload.get("krs_input_data"))
    if not ok:
        raise HTTPException(422, "SOURCE_RUNNER_UNIVERSE_MISMATCH:" + ",".join(errs))
    out = legacy.pre_krs(payload)
    if (out.get("receipt") or {}).get("status") == "PASS":
        art = dict(out.get("artifact") or {})
        art["source_receipt_sha256"] = source.get("receipt_sha256")
        art["source_snapshot_sha256"] = (source.get("artifact") or {}).get("source_snapshot_sha256")
        art["source_manifest_profile"] = (source.get("artifact") or {}).get("source_manifest_profile")
        out = legacy.signed_receipt("PRE_KRS", race_id, "PASS", art, [])
    return out


@app.post("/final")
def final(payload: Dict[str, Any]):
    legacy.validate_family(payload)
    race_id = str(payload.get("race_id") or "")
    source = _require_source_receipt(payload, race_id)
    sa = source.get("artifact") or {}
    allowed = {str(r.get("runner_id") or r.get("horse_no")) for r in
               (sa.get("official_runner_universe") or {}).get("runners") or []}
    fpp = payload.get("final_prediction_package") or {}
    if (not isinstance(fpp, dict) or not isinstance(fpp.get("ranking") or [], list)
            or not isinstance(fpp.get("roles") or {}, dict)):
        raise HTTPException(422, "SOURCE_FINAL_RUNNER_UNIVERSE_MISMATCH")
    refs = set(map(str, fpp.get("ranking") or [])) | set(map(str, fpp.get("roles") or {}))  # same as v1.5
    for part in (payload.get("final_ticket") or {}, payload.get("minimum_efficient_coverage") or {},
                 fpp.get("minimum_efficient_coverage") or {}):
        if not isinstance(part, dict) or not isinstance(part.get("tickets") or [], list):
            raise HTTPException(422, "SOURCE_FINAL_RUNNER_UNIVERSE_MISMATCH")
        for t in part.get("tickets") or []:
            if not isinstance(t, dict) or not isinstance(t.get("selection"), list):
                raise HTTPException(422, "SOURCE_FINAL_RUNNER_UNIVERSE_MISMATCH")
            refs.update(map(str, t["selection"]))
    if not allowed or refs - allowed:
        raise HTTPException(422, "SOURCE_FINAL_RUNNER_UNIVERSE_MISMATCH")
    out = legacy.final(payload)
    if (out.get("receipt") or {}).get("status") == "PASS":
        art = dict(out.get("artifact") or {})
        art["source_receipt_sha256"] = source.get("receipt_sha256")
        art["source_snapshot_sha256"] = sa.get("source_snapshot_sha256")
        art["source_manifest_profile"] = sa.get("source_manifest_profile")
        out = legacy.signed_receipt("FINAL", race_id, "PASS", art, [])
    return out


v15.source_acquire, v15.pre_krs, v15.final = source_acquire, pre_krs, final  # v15.formal resolves these globals


@app.post("/formal")
def formal(payload: Dict[str, Any]):
    return v15.formal(payload)


@app.get("/health16")
def health16():
    h = dict(v15.health())
    h["runtime_revision"] = APP_VERSION
    h["runtime_app_v16_sha256"] = legacy.sha_file(__file__)
    h["rakuten_source_profile"] = RAKUTEN_PROFILE
    h["rakuten_parser_sha256"] = legacy.sha_file("/opt/km/rakuten.py")
    h["approved_source_profiles"] = sorted(APPROVED_PROFILES)
    return h

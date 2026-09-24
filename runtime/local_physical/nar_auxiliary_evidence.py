from __future__ import annotations

import base64
import concurrent.futures
import gzip
import html
import re
import unicodedata
import urllib.parse
from html.parser import HTMLParser
from typing import Any, Dict, List, Tuple

from source_acquisition import _decode, _html_tables, fetch_source, sha_obj, utcnow

PROFILE = "KM-LOCAL-NAR-AUXILIARY-EVIDENCE-v1.0-20260924"
MAX_PROFILE_WORKERS = 6


def _norm(value: Any) -> str:
    s = unicodedata.normalize("NFKC", str(value or ""))
    return re.sub(r"\s+", "", s).strip()


def _as_int(value: Any) -> int | None:
    m = re.search(r"-?\d+", unicodedata.normalize("NFKC", str(value or "")).replace(",", ""))
    return int(m.group()) if m else None


def _as_float(value: Any) -> float | None:
    s = unicodedata.normalize("NFKC", str(value or "")).replace(",", "").replace("%", "")
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    return float(m.group()) if m else None


def _raw_bytes(snapshot: Dict[str, Any]) -> bytes:
    try:
        return gzip.decompress(base64.b64decode(str(snapshot["raw_gzip_b64"])))
    except Exception as e:
        raise ValueError("AUXILIARY_SOURCE_RAW_DECODE_FAILED:" + str(snapshot.get("source_id"))) from e


def _race_card_snapshot(artifact: Dict[str, Any]) -> Dict[str, Any]:
    for s in artifact.get("sources") or []:
        if not isinstance(s, dict):
            continue
        cls = str(s.get("source_class") or "")
        if cls.startswith("OFFICIAL_RACE_CARD") and s.get("raw_gzip_b64"):
            return s
    raise ValueError("AUXILIARY_RACE_CARD_RAW_SOURCE_MISSING")


class _AnchorParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.items: List[Dict[str, str]] = []
        self._href: str | None = None
        self._parts: List[str] = []

    def handle_starttag(self, tag: str, attrs):
        if tag.lower() != "a":
            return
        d = dict(attrs)
        self._href = str(d.get("href") or "")
        self._parts = []

    def handle_data(self, data: str):
        if self._href is not None and data:
            self._parts.append(data)

    def handle_endtag(self, tag: str):
        if tag.lower() == "a" and self._href is not None:
            self.items.append({
                "href": html.unescape(self._href),
                "text": re.sub(r"\s+", " ", "".join(self._parts)).strip(),
            })
            self._href = None
            self._parts = []


def _id_from_url(url: str | None, key: str) -> str | None:
    if not url:
        return None
    q = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
    v = q.get(key)
    return str(v[0]).strip() if v and str(v[0]).strip() else None


def discover_entity_registry(artifact: Dict[str, Any]) -> List[Dict[str, Any]]:
    race_card = _race_card_snapshot(artifact)
    decoded = _decode(_raw_bytes(race_card), str(race_card.get("content_type") or ""))
    parser = _AnchorParser()
    parser.feed(decoded)
    anchors = parser.items

    declared = (artifact.get("declared_runner_universe") or artifact.get("official_runner_universe") or {}).get("runners") or []
    if not declared:
        raise ValueError("AUXILIARY_DECLARED_RUNNER_UNIVERSE_MISSING")
    by_name = {_norm(r.get("name")): r for r in declared if _norm(r.get("name"))}
    base_url = str(race_card.get("final_url") or race_card.get("requested_url") or "https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/DebaTable")

    horse_positions = []
    for i, a in enumerate(anchors):
        if "HorseMarkInfo" not in a["href"]:
            continue
        name = _norm(a["text"])
        if name in by_name:
            horse_positions.append((i, name))

    records: List[Dict[str, Any]] = []
    for pos_idx, (anchor_index, cname) in enumerate(horse_positions):
        runner = by_name[cname]
        next_index = horse_positions[pos_idx + 1][0] if pos_idx + 1 < len(horse_positions) else len(anchors)
        segment = anchors[anchor_index:next_index]
        horse_anchor = next((a for a in segment if "HorseMarkInfo" in a["href"]), None)
        rider_anchor = next((a for a in segment if "RiderMark" in a["href"]), None)
        trainer_anchor = next((a for a in segment if "TrainerMark" in a["href"]), None)
        if not horse_anchor:
            continue
        horse_url = urllib.parse.urljoin(base_url, horse_anchor["href"])
        rider_url = urllib.parse.urljoin(base_url, rider_anchor["href"]) if rider_anchor else None
        trainer_url = urllib.parse.urljoin(base_url, trainer_anchor["href"]) if trainer_anchor else None
        records.append({
            "runner_id": str(runner.get("runner_id") or runner.get("horse_no")),
            "horse_no": int(runner.get("horse_no") or runner.get("runner_id")),
            "horse_name": str(runner.get("name") or ""),
            "horse_lineage_login_code": _id_from_url(horse_url, "k_lineageLoginCode"),
            "horse_profile_url": horse_url,
            "rider_name": str((rider_anchor or {}).get("text") or ""),
            "rider_license_no": _id_from_url(rider_url, "k_riderLicenseNo"),
            "rider_profile_url": rider_url,
            "trainer_name": str((trainer_anchor or {}).get("text") or ""),
            "trainer_license_no": _id_from_url(trainer_url, "k_trainerLicenseNo"),
            "trainer_profile_url": trainer_url,
        })

    expected_ids = {str(r.get("runner_id") or r.get("horse_no")) for r in declared}
    actual_ids = {r["runner_id"] for r in records}
    if actual_ids != expected_ids:
        raise ValueError("AUXILIARY_ENTITY_REGISTRY_INCOMPLETE:" + ",".join(sorted(expected_ids - actual_ids)))
    return sorted(records, key=lambda x: int(x["horse_no"]))


def _profile_specs(registry: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    specs: List[Dict[str, Any]] = []
    seen = set()
    for rec in registry:
        rid = rec["runner_id"]
        entries = [
            (f"NAR-HORSE-{rec.get('horse_lineage_login_code') or rid}", "OFFICIAL_HORSE_HISTORY_PROFILE", rec.get("horse_profile_url"), f"horse:{rid}"),
            (f"NAR-RIDER-{rec.get('rider_license_no') or rid}", "OFFICIAL_RIDER_PROFILE", rec.get("rider_profile_url"), f"rider:{rec.get('rider_license_no') or rid}"),
            (f"NAR-TRAINER-{rec.get('trainer_license_no') or rid}", "OFFICIAL_TRAINER_PROFILE", rec.get("trainer_profile_url"), f"trainer:{rec.get('trainer_license_no') or rid}"),
        ]
        for source_id, source_class, url, entity_key in entries:
            if not url or source_id in seen:
                continue
            seen.add(source_id)
            specs.append({
                "source_id": source_id,
                "source_class": source_class,
                "authority": "NAR_OFFICIAL",
                "priority": 100,
                "official": True,
                "required": False,
                "url": url,
                "max_bytes": 700000,
                "timeout_seconds": 20,
                "entity_key": entity_key,
                "extract": [],
            })
    return specs


def _fetch_profiles(specs: List[Dict[str, Any]], cutoff: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    snapshots: List[Dict[str, Any]] = []
    warnings: List[str] = []

    def one(spec: Dict[str, Any]):
        try:
            snap, errs = fetch_source(spec, cutoff)
            return snap, errs
        except Exception as e:
            return {
                "source_id": spec.get("source_id"),
                "source_class": spec.get("source_class"),
                "authority": spec.get("authority"),
                "official": True,
                "required": False,
                "requested_url": spec.get("url"),
                "status": "FETCH_FAILED",
                "error": str(e),
                "fetched_at": utcnow(),
            }, []

    workers = max(1, min(MAX_PROFILE_WORKERS, len(specs) or 1))
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        for snap, errs in (f.result() for f in [ex.submit(one, s) for s in specs]):
            snapshots.append(snap)
            warnings.extend(errs)
            if snap.get("status") == "FETCH_FAILED":
                warnings.append("AUXILIARY_OPTIONAL_FETCH_FAILED:" + str(snap.get("source_id")))
            elif not (200 <= int(snap.get("http_status") or 0) < 300):
                warnings.append("AUXILIARY_OPTIONAL_HTTP_STATUS:" + str(snap.get("source_id")))

    snapshots.sort(key=lambda s: str(s.get("source_id") or ""))
    return snapshots, list(dict.fromkeys(warnings))


def _tables_from_snapshot(snapshot: Dict[str, Any]) -> List[List[List[str]]]:
    if not snapshot.get("raw_gzip_b64"):
        return []
    return _html_tables(_decode(_raw_bytes(snapshot), str(snapshot.get("content_type") or "")))


def _stat_row(row: List[str]) -> Dict[str, Any] | None:
    if len(row) != 10:
        return None
    total = _as_int(row[7])
    if total is None:
        return None
    return {
        "label": row[0], "first": _as_int(row[1]), "second": _as_int(row[2]),
        "third": _as_int(row[3]), "fourth": _as_int(row[4]), "fifth": _as_int(row[5]),
        "unplaced": _as_int(row[6]), "total": total, "win_rate_pct": _as_float(row[8]),
        "quinella_rate_pct": _as_float(row[9]),
    }


def parse_person_profile(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    profile: Dict[str, Any] = {"source_id": snapshot.get("source_id"), "source_snapshot_sha256": snapshot.get("snapshot_sha256"), "identity": {}, "performance_rows": []}
    for table in _tables_from_snapshot(snapshot):
        for row in table:
            if len(row) == 2 and row[0] in {"所属", "所属厩舎", "生年月日", "初騎乗日", "初出走日", "初勝利日"}:
                profile["identity"][row[0]] = row[1]
            stat = _stat_row(row)
            if stat:
                profile["performance_rows"].append(stat)
    profile["lifetime_local"] = next((x for x in profile["performance_rows"] if x["label"] == "地方競馬"), None)
    profile["latest_year"] = next((x for x in profile["performance_rows"] if re.fullmatch(r"20\d{2}年", x["label"])), None)
    profile["summary_sha256"] = sha_obj({"identity": profile["identity"], "performance_rows": profile["performance_rows"]})
    return profile


def parse_horse_profile(snapshot: Dict[str, Any], race_context: Dict[str, Any] | None = None) -> Dict[str, Any]:
    history_rows: List[Dict[str, Any]] = []
    filtered_target_or_future = 0
    race_context = race_context or {}
    target_date = str(race_context.get("race_date") or "").replace("-", "/")
    for table in _tables_from_snapshot(snapshot):
        if not table or "年月日" not in table[0] or "競馬場" not in table[0]:
            continue
        for row in table[1:]:
            if len(row) >= 23 and re.fullmatch(r"\d{4}/\d{2}/\d{2}", row[0]):
                if target_date and row[0] >= target_date:
                    filtered_target_or_future += 1
                    continue
                history_rows.append({
                    "date": row[0], "venue": row[1], "race_no": _as_int(row[2]), "race_name": row[3],
                    "class": row[4], "distance": _as_int(row[5]), "weather": row[6], "going": row[7],
                    "field_size": _as_int(row[9]), "frame_no": _as_int(row[10]), "horse_no": _as_int(row[11]),
                    "popularity": _as_int(row[12]), "finish": _as_int(row[13]), "time": row[14], "margin": row[15],
                    "final_3f": _as_float(row[16]), "body_weight": _as_int(row[17]), "jockey": row[18],
                    "carried_weight": _as_float(row[19]), "trainer": row[20], "earnings": _as_int(row[21]),
                    "reference_horse": row[22],
                })
    return {
        "source_id": snapshot.get("source_id"),
        "source_snapshot_sha256": snapshot.get("snapshot_sha256"),
        "history_count": len(history_rows),
        "history": history_rows,
        "history_sha256": sha_obj(history_rows),
        "filtered_target_or_future_rows": filtered_target_or_future,
        "temporal_filter": "STRICTLY_BEFORE_TARGET_RACE_DATE" if target_date else "SOURCE_CUTOFF_ONLY",
    }


def _positions(value: str) -> List[int]:
    return [int(x) for x in re.findall(r"\d+", str(value or ""))]


def _result_rows_from_table(table: List[List[str]]) -> List[Dict[str, Any]]:
    if not table:
        return []
    head = table[0]
    if not {"着順", "馬番", "馬名"}.issubset(set(head)):
        return []
    idx = {name: head.index(name) for name in head}
    pidx = next((i for i, h in enumerate(head) if _norm(h) == _norm("コーナー通過順")), None)
    frame_idx = next((i for i, h in enumerate(head) if _norm(h) == "枠"), None)
    out = []
    for row in table[1:]:
        if len(row) < len(head):
            continue
        finish = _as_int(row[idx["着順"]]); horse_no = _as_int(row[idx["馬番"]])
        if finish is None or horse_no is None:
            continue
        out.append({"finish": finish, "frame_no": _as_int(row[frame_idx]) if frame_idx is not None else None, "horse_no": horse_no, "horse_name": row[idx["馬名"]], "passing_positions": _positions(row[pidx]) if pidx is not None else []})
    return out


def build_same_day_bias(artifact: Dict[str, Any]) -> Dict[str, Any]:
    races = []
    for field, wrapped in sorted((artifact.get("normalized_evidence") or {}).items()):
        if not re.fullmatch(r"same_day_r\d{2}_result_tables", field):
            continue
        tables = (wrapped or {}).get("value") if isinstance(wrapped, dict) else None
        if not isinstance(tables, list):
            continue
        result_rows = []
        for table in tables:
            result_rows = _result_rows_from_table(table)
            if result_rows: break
        if not result_rows: continue
        top3 = [x for x in result_rows if x["finish"] <= 3]
        winner = next((x for x in result_rows if x["finish"] == 1), None)
        races.append({"field": field, "field_size": len(result_rows), "winner_frame_no": (winner or {}).get("frame_no"), "winner_last_corner": ((winner or {}).get("passing_positions") or [None])[-1], "top3": top3, "source_id": (wrapped or {}).get("source_id"), "snapshot_sha256": (wrapped or {}).get("snapshot_sha256")})
    top3_rows = [x for r in races for x in r["top3"]]
    front_top3 = sum(1 for x in top3_rows if x.get("passing_positions") and x["passing_positions"][-1] <= 3)
    leader_wins = sum(1 for r in races if r.get("winner_last_corner") == 1)
    frames = [x.get("frame_no") for x in top3_rows if x.get("frame_no") is not None]
    summary = {
        "profile": "KM-LOCAL-SAME-DAY-POSITION-BIAS-v1.0-20260924-SHADOW", "production_authority": False,
        "races_observed": len(races), "top3_observations": len(top3_rows),
        "front_at_last_corner_top3_rate": round(front_top3 / len(top3_rows), 6) if top3_rows else None,
        "leader_at_last_corner_win_rate": round(leader_wins / len(races), 6) if races else None,
        "inner_frame_top3_rate": round(sum(1 for x in frames if x <= 3) / len(frames), 6) if frames else None,
        "outer_frame_top3_rate": round(sum(1 for x in frames if x >= 6) / len(frames), 6) if frames else None,
        "races": races,
    }
    summary["sha256"] = sha_obj({k: v for k, v in summary.items() if k != "sha256"})
    return summary


def build_pedigree_seed(artifact: Dict[str, Any]) -> Dict[str, Any]:
    """Capture pre-race pedigree identities as a population-ledger seed.

    This is deliberately not a BVI score. It preserves sire/dam/damsire lineage
    so a point-in-time population database can be accumulated without inventing
    a pedigree fit statistic from the current field alone.
    """
    ev = artifact.get("normalized_evidence") or {}
    rc = ev.get("race_card_tables") or {}
    tables = rc.get("value") if isinstance(rc, dict) else None
    rows = None
    if isinstance(tables, list):
        for table in tables:
            if isinstance(table, list) and any(isinstance(r, list) and "競走馬" in r for r in table):
                if rows is None or len(table) > len(rows):
                    rows = table
    seeds = []
    if rows:
        def primary(row):
            if len(row) < 2 or not re.fullmatch(r"\\d{1,2}", str(row[0]).strip()):
                return False
            if len(row) >= 3 and re.fullmatch(r"\\d{1,2}", str(row[1]).strip()):
                return _norm(row[2]) not in {"", "競走馬", "馬名"}
            return _norm(row[1]) not in {"", "競走馬", "馬名", "前走回"}
        indices=[i for i,row in enumerate(rows) if isinstance(row,list) and primary(row)]
        for n,i in enumerate(indices):
            stop=indices[n+1] if n+1<len(indices) else len(rows)
            group=rows[i:stop]
            if len(group)<5:
                continue
            p,meta,blood,content,marginrow=group[:5]
            if len(p)>=3 and re.fullmatch(r"\\d{1,2}",str(p[1]).strip()):
                horse_no=int(p[1]); name=str(p[2]).strip()
            else:
                horse_no=int(p[0]); name=str(p[1]).strip()
            seeds.append({
                "runner_id":str(horse_no),
                "horse_name":name,
                "sire":str(blood[0]).strip() if blood else "",
                "dam":str(content[0]).strip() if content else "",
                "damsire":re.sub(r"^[（(]|[）)]$","",str(marginrow[0]).strip()) if marginrow else "",
                "race_card_source_id":rc.get("source_id"),
                "race_card_snapshot_sha256":rc.get("snapshot_sha256"),
            })
    out={
        "profile":"KM-LOCAL-PEDIGREE-POPULATION-SEED-v1.0-20260924",
        "production_authority":False,
        "population_fit_ready":False,
        "runner_count":len(seeds),
        "seeds":sorted(seeds,key=lambda x:int(x["runner_id"])),
        "rule":"Identity/history seed only. Do not convert current-field lineage frequencies into BVI population fit.",
    }
    out["sha256"]=sha_obj({k:v for k,v in out.items() if k!="sha256"})
    return out


def build_profile_summaries(snapshots: List[Dict[str, Any]], registry: List[Dict[str, Any]], race_context: Dict[str, Any] | None = None) -> Dict[str, Any]:
    by_source = {
        str(s.get("source_id")): s for s in snapshots
        if isinstance(s, dict)
        and s.get("cutoff_relation") != "POST_CUTOFF"
        and s.get("raw_gzip_b64")
    }
    horses: Dict[str, Any] = {}; riders: Dict[str, Any] = {}; trainers: Dict[str, Any] = {}
    for rec in registry:
        rid = rec["runner_id"]
        hs = by_source.get(f"NAR-HORSE-{rec.get('horse_lineage_login_code') or rid}")
        if hs and hs.get("raw_gzip_b64"): horses[rid] = parse_horse_profile(hs, race_context)
        rider_id = str(rec.get("rider_license_no") or rid)
        rs = by_source.get(f"NAR-RIDER-{rider_id}")
        if rs and rs.get("raw_gzip_b64") and rider_id not in riders: riders[rider_id] = parse_person_profile(rs)
        trainer_id = str(rec.get("trainer_license_no") or rid)
        ts = by_source.get(f"NAR-TRAINER-{trainer_id}")
        if ts and ts.get("raw_gzip_b64") and trainer_id not in trainers: trainers[trainer_id] = parse_person_profile(ts)
    out = {"horses": horses, "riders": riders, "trainers": trainers, "runner_entity_registry": registry}
    out["sha256"] = sha_obj({k: v for k, v in out.items() if k != "sha256"})
    return out


def _manifest_canonical(specs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [{"source_id": str(s.get("source_id") or ""), "url": str(s.get("url") or ""), "source_class": str(s.get("source_class") or ""), "authority": str(s.get("authority") or ""), "priority": int(s.get("priority") or 0), "official": bool(s.get("official", False)), "required": bool(s.get("required", False)), "entity_key": s.get("entity_key")} for s in specs]


def enrich_with_auxiliary_evidence(artifact: Dict[str, Any], prediction_cutoff: str, *, require_profiles: bool = False) -> Tuple[Dict[str, Any], List[str]]:
    registry = discover_entity_registry(artifact)
    specs = _profile_specs(registry)
    snapshots, warnings = _fetch_profiles(specs, prediction_cutoff)
    successful = [s for s in snapshots if s.get("raw_gzip_b64") and 200 <= int(s.get("http_status") or 0) < 300]
    temporal_eligible = [s for s in successful if s.get("cutoff_relation") != "POST_CUTOFF"]
    required_errors: List[str] = []
    if require_profiles and len(successful) != len(specs):
        missing = sorted(set(s["source_id"] for s in specs) - set(str(s.get("source_id")) for s in successful))
        required_errors.append("AUXILIARY_REQUIRED_PROFILES_MISSING:" + ",".join(missing))

    artifact["sources"] = list(artifact.get("sources") or []) + snapshots
    manifest = _manifest_canonical(specs)
    artifact["discovered_auxiliary_source_manifest"] = manifest
    artifact["discovered_auxiliary_source_manifest_sha256"] = sha_obj(manifest)
    artifact["nar_entity_registry"] = registry
    artifact["nar_entity_registry_sha256"] = sha_obj(registry)
    auxiliary = {
        "profile": PROFILE, "production_authority": False,
        "mode": "OFFICIAL-SOURCE / AUXILIARY-SHADOW / NO-PRODUCTION-NUMERICAL-CHANGE",
        "profile_source_count": len(specs), "profile_source_success_count": len(successful),
        "profile_source_temporal_eligible_count": len(temporal_eligible),
        "profile_source_warning_count": len(warnings), "profile_warnings": warnings,
        "profiles": build_profile_summaries(snapshots, registry, artifact.get("source_race_context") or {}),
        "same_day_position_bias": build_same_day_bias(artifact),
        "pedigree_population_seed": build_pedigree_seed(artifact),
        "population_pedigree_status": "SEED-HISTORY-CAPTURED / POPULATION-AGGREGATION-NOT-YET-PRODUCTION",
        "training_comment_paddock_status": "NO-UNIVERSAL-NAR-OFFICIAL-SOURCE-CONNECTED",
        "jma_weather_status": "NOT-ACTIVATED-UNTIL-VENUE-STATION-LINEAGE-VERIFIED",
    }
    artifact["auxiliary_evidence"] = auxiliary
    artifact["auxiliary_evidence_sha256"] = sha_obj(auxiliary)
    raw_bundle = [{"source_id": s.get("source_id"), "raw_sha256": s.get("raw_sha256"), "snapshot_sha256": s.get("snapshot_sha256"), "fetched_at": s.get("fetched_at"), "final_url": s.get("final_url")} for s in artifact["sources"]]
    artifact["raw_source_bundle_sha256"] = sha_obj(raw_bundle)
    artifact["post_cutoff_sources"] = [
        s.get("source_id") for s in artifact["sources"] if s.get("cutoff_relation") == "POST_CUTOFF"
    ]
    artifact["stale_sources"] = [
        s.get("source_id") for s in artifact["sources"] if s.get("stale")
    ]
    artifact["auxiliary_source_profile"] = PROFILE
    artifact["auxiliary_source_required"] = bool(require_profiles)
    artifact["errors"] = list(dict.fromkeys(list(artifact.get("errors") or []) + required_errors))
    artifact["formal_ready"] = bool(artifact.get("formal_ready") is True and not required_errors)
    return artifact, required_errors

from __future__ import annotations

import base64
import datetime
import gzip
import json
import math
from typing import Any, Dict, List, Tuple

from source_acquisition import fetch_source, sha_obj, utcnow

PROFILE = "KM-JRA-JMA-WEATHER-EVIDENCE-v1.0-20260925"
STATION_TABLE_URL = "https://www.jma.go.jp/bosai/amedas/const/amedastable.json"

# Approximate racecourse centroids are used only to select the nearest official
# JMA AMeDAS station. They are NOT a racing/prediction feature themselves.
VENUE_COORDS = {
    "SPP": (43.076, 141.323),
    "HKD": (41.770, 140.773),
    "FKS": (37.760, 140.480),
    "NGT": (37.948, 139.187),
    "TKY": (35.663, 139.485),
    "NKY": (35.725, 139.962),
    "CHK": (35.067, 136.989),
    "KYO": (34.907, 135.725),
    "HSN": (34.779, 135.363),
    "KKR": (33.842, 130.890),
}


def _parse_dt(value: Any) -> datetime.datetime:
    s = str(value or "").strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.astimezone(datetime.timezone.utc)


def _raw_json(snapshot: Dict[str, Any]) -> Any:
    raw = gzip.decompress(base64.b64decode(str(snapshot["raw_gzip_b64"])))
    return json.loads(raw.decode("utf-8"))


def _deg(pair: Any) -> float | None:
    if not isinstance(pair, list) or len(pair) < 2:
        return None
    try:
        return float(pair[0]) + float(pair[1]) / 60.0
    except Exception:
        return None


def _haversine_km(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    r = 6371.0088
    lat1, lon1, lat2, lon2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def choose_nearest_station(stations: Dict[str, Any], venue_id: str) -> Dict[str, Any]:
    venue_id = str(venue_id or "").upper()
    if venue_id not in VENUE_COORDS:
        raise ValueError("JMA_VENUE_COORDS_UNSUPPORTED:" + venue_id)
    target = VENUE_COORDS[venue_id]
    rows: List[Dict[str, Any]] = []
    for station_id, meta in (stations or {}).items():
        if not isinstance(meta, dict):
            continue
        lat = _deg(meta.get("lat"))
        lon = _deg(meta.get("lon"))
        if lat is None or lon is None:
            continue
        distance = _haversine_km(target, (lat, lon))
        # A/B stations generally expose a broader observation set. A small
        # preference is applied only for tie-breaking; distance remains primary.
        station_type = str(meta.get("type") or "")
        type_penalty = {"A": 0.0, "B": 0.25, "C": 0.5}.get(station_type, 0.75)
        rows.append({
            "station_id": str(station_id),
            "station_name": meta.get("kjName"),
            "station_type": station_type,
            "elems": meta.get("elems"),
            "latitude": lat,
            "longitude": lon,
            "altitude_m": meta.get("alt"),
            "distance_km": round(distance, 3),
            "_rank": distance + type_penalty,
        })
    if not rows:
        raise ValueError("JMA_STATION_TABLE_EMPTY")
    winner = min(rows, key=lambda x: (x["_rank"], x["distance_km"], x["station_id"]))
    winner.pop("_rank", None)
    if float(winner["distance_km"]) > 80.0:
        raise ValueError("JMA_NEAREST_STATION_TOO_FAR")
    return winner


def _value(row: Dict[str, Any], key: str) -> Any:
    v = row.get(key)
    if isinstance(v, list) and v:
        return v[0]
    return v


def _observation_url(ts_jst: datetime.datetime) -> str:
    return "https://www.jma.go.jp/bosai/amedas/data/map/" + ts_jst.strftime("%Y%m%d%H%M00") + ".json"


def _candidate_times(cutoff: str) -> List[datetime.datetime]:
    now = datetime.datetime.now(datetime.timezone.utc)
    try:
        c = _parse_dt(cutoff)
    except Exception:
        c = now
    anchor = min(c, now)
    jst = datetime.timezone(datetime.timedelta(hours=9))
    t = anchor.astimezone(jst).replace(second=0, microsecond=0)
    t = t.replace(minute=(t.minute // 10) * 10)
    # JMA map publication can lag a few minutes, so walk backward.
    return [t - datetime.timedelta(minutes=10 * i) for i in range(0, 13)]


def _fetch_station_table(cutoff: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    spec = {
        "source_id": "JMA-AMEDAS-STATION-TABLE",
        "source_class": "OFFICIAL_JMA_AMEDAS_STATION_METADATA",
        "authority": "JMA_OFFICIAL",
        "priority": 100,
        "official": True,
        "required": False,
        "url": STATION_TABLE_URL,
        "max_bytes": 1000000,
        "timeout_seconds": 20,
        "extract": [],
    }
    snap, _ = fetch_source(spec, cutoff)
    if not (200 <= int(snap.get("http_status") or 0) < 300):
        raise ValueError("JMA_STATION_TABLE_HTTP_FAILED")
    return snap, _raw_json(snap)


def _fetch_observation(station_id: str, cutoff: str) -> Tuple[Dict[str, Any], Dict[str, Any], str]:
    last_error = "JMA_OBSERVATION_NOT_FOUND"
    for t in _candidate_times(cutoff):
        url = _observation_url(t)
        spec = {
            "source_id": "JMA-AMEDAS-MAP-" + t.strftime("%Y%m%d%H%M"),
            "source_class": "OFFICIAL_JMA_AMEDAS_OBSERVATION",
            "authority": "JMA_OFFICIAL",
            "priority": 100,
            "official": True,
            "required": False,
            "url": url,
            "max_bytes": 1200000,
            "timeout_seconds": 15,
            "extract": [],
        }
        try:
            snap, _ = fetch_source(spec, cutoff)
            if not (200 <= int(snap.get("http_status") or 0) < 300):
                last_error = "JMA_OBSERVATION_HTTP_" + str(snap.get("http_status"))
                continue
            body = _raw_json(snap)
            row = body.get(str(station_id)) if isinstance(body, dict) else None
            if isinstance(row, dict):
                return snap, row, t.isoformat()
            last_error = "JMA_STATION_NOT_IN_MAP:" + str(station_id)
        except Exception as e:
            last_error = type(e).__name__ + ":" + str(e)
    raise ValueError(last_error)


def build_jma_weather_evidence(
    artifact: Dict[str, Any],
    prediction_cutoff: str,
    *,
    require_weather: bool = False,
) -> Tuple[Dict[str, Any], List[str]]:
    context = artifact.get("source_race_context") or {}
    venue_id = str(context.get("venue_id") or "").upper()
    errors: List[str] = []
    warnings: List[str] = []
    snapshots: List[Dict[str, Any]] = []

    evidence: Dict[str, Any] = {
        "profile": PROFILE,
        "production_authority": False,
        "mode": "OFFICIAL-JMA / CURRENT-STATE-SHADOW / NO-PRODUCTION-NUMERICAL-CHANGE",
        "venue_id": venue_id,
        "status": "NOT_AVAILABLE",
        "station": None,
        "observation": None,
        "warnings": warnings,
    }

    try:
        station_snap, station_table = _fetch_station_table(prediction_cutoff)
        snapshots.append(station_snap)
        station = choose_nearest_station(station_table, venue_id)
        evidence["station"] = station
        obs_snap, row, observed_at = _fetch_observation(station["station_id"], prediction_cutoff)
        snapshots.append(obs_snap)
        evidence["observation"] = {
            "observed_at_jst": observed_at,
            "temperature_c": _value(row, "temp"),
            "precipitation_10m_mm": _value(row, "precipitation10m"),
            "precipitation_1h_mm": _value(row, "precipitation1h"),
            "precipitation_3h_mm": _value(row, "precipitation3h"),
            "precipitation_24h_mm": _value(row, "precipitation24h"),
            "wind_speed_ms": _value(row, "wind"),
            "wind_direction_code": _value(row, "windDirection"),
            "humidity_pct": _value(row, "humidity"),
            "sun_10m_min": _value(row, "sun10m"),
            "snow_depth_cm": _value(row, "snow"),
        }
        evidence["status"] = "CAPTURED"
    except Exception as e:
        warnings.append("JMA_OPTIONAL_WEATHER_UNAVAILABLE:" + type(e).__name__ + ":" + str(e))
        if require_weather:
            errors.append("JMA_REQUIRED_WEATHER_FAILED:" + str(e))

    evidence["warnings"] = list(dict.fromkeys(warnings))
    evidence["sha256"] = sha_obj({k: v for k, v in evidence.items() if k != "sha256"})
    artifact["sources"] = list(artifact.get("sources") or []) + snapshots
    artifact["jma_weather_evidence"] = evidence
    artifact["jma_weather_evidence_sha256"] = sha_obj(evidence)
    artifact["jma_weather_profile"] = PROFILE
    artifact["jma_weather_required"] = bool(require_weather)

    raw_bundle = [
        {
            "source_id": s.get("source_id"),
            "raw_sha256": s.get("raw_sha256"),
            "snapshot_sha256": s.get("snapshot_sha256"),
            "fetched_at": s.get("fetched_at"),
            "final_url": s.get("final_url"),
        }
        for s in artifact.get("sources") or []
    ]
    artifact["raw_source_bundle_sha256"] = sha_obj(raw_bundle)
    artifact["errors"] = list(dict.fromkeys(list(artifact.get("errors") or []) + errors))
    artifact["formal_ready"] = bool(artifact.get("formal_ready") is True and not errors)
    return artifact, errors

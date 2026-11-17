"""LOCAL weather evidence from JMA AMeDAS (evidence only; never changes the official going or any index).

Terms: JMA website content may be reused with the source stated ("出典：気象庁ホームページ"), edited data
must say it was edited (data.jma.go.jp/developer/ryuui.pdf). Load: one station table per day (cached) and
one 10-minute map per call, newest slot at or before the freeze time; no retries beyond a short walk back.
Station choice reuses the Runtime bundle's racecourse centroids (nearest station, A/B type preferred).
"""
import hashlib
import json
import math
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROFILE = 'KM-LOCAL-WEATHER-EVIDENCE-v1.0-20261118'
ATTRIBUTION = '出典：気象庁ホームページ（アメダス）'
JST = timezone(timedelta(hours=9))
TABLE_URL = 'https://www.jma.go.jp/bosai/amedas/const/amedastable.json'
MAP_URL = 'https://www.jma.go.jp/bosai/amedas/data/map/{}00.json'
UA = 'KeibaMetrics-LOCAL-evidence/1.0 (+github.com/b03la013-max)'
VENUE_COORDS = {   # same centroids as runtime/railway_local_bundle/km/jma_weather_evidence.py
    'MOR': (39.700, 141.185), 'MIZ': (39.139, 141.139), 'URW': (35.861, 139.667), 'FNB': (35.694, 139.991),
    'OHI': (35.596, 139.743), 'KAW': (35.535, 139.707), 'KNZ': (36.612, 136.692), 'KSM': (35.369, 136.756),
    'NGY': (35.074, 136.807), 'SON': (34.768, 135.442), 'HIM': (34.843, 134.690), 'KCH': (33.548, 133.507),
    'SAG': (33.287, 130.454), 'MON': (42.557, 142.018)}


def _get(url, timeout=15):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _deg(p):
    return float(p[0]) + float(p[1]) / 60.0 if isinstance(p, list) and len(p) >= 2 else None


def _km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371.0088 * math.asin(math.sqrt(h))


def nearest_station(table, venue_id):
    if venue_id not in VENUE_COORDS:
        return None
    rows = []
    for sid, m in table.items():
        lat, lon = _deg(m.get('lat')), _deg(m.get('lon'))
        if lat is None or lon is None:
            continue
        d = _km(VENUE_COORDS[venue_id], (lat, lon))
        rows.append((d + {'A': 0.0, 'B': 0.25, 'C': 0.5}.get(str(m.get('type')), 0.75), d, sid, m))
    if not rows:
        return None
    _, d, sid, m = min(rows)
    return {'station_id': sid, 'station_name': m.get('kjName'), 'type': m.get('type'), 'distance_km': round(d, 2),
            'altitude_m': m.get('alt')} if d <= 80 else None


def _table(cache_dir):
    p = Path(cache_dir) / 'amedastable.json'
    if p.exists() and datetime.fromtimestamp(p.stat().st_mtime, JST).date() == datetime.now(JST).date():
        return json.loads(p.read_text())
    raw = _get(TABLE_URL)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(raw)
    return json.loads(raw)


def observe(venue_id, freeze_at, cache_dir, fetch=_get, now=None):
    """Newest 10-minute AMeDAS map row at or before freeze_at for the venue's station."""
    fetched_at = now or datetime.now(JST)
    out = {'profile': PROFILE, 'attribution': ATTRIBUTION, 'venue_id': venue_id, 'status': 'NOT_AVAILABLE',
           'production_effect': 'NONE (official going unchanged; no numeric consumer)'}
    try:
        st = nearest_station(_table(cache_dir), venue_id)
        if not st:
            out['status'] = 'NO_STATION'
            return out
        out['station'] = st
        t = min(freeze_at, fetched_at).astimezone(JST).replace(second=0, microsecond=0)
        t = t.replace(minute=t.minute // 10 * 10)
        for i in range(4):
            slot = t - timedelta(minutes=10 * i)
            try:
                raw = fetch(MAP_URL.format(slot.strftime('%Y%m%d%H%M')))
            except Exception:
                continue
            row = json.loads(raw).get(st['station_id'])
            if not isinstance(row, dict):
                continue
            v = lambda k: (row.get(k) or [None, None])[0] if isinstance(row.get(k), list) else row.get(k)
            q = lambda k: (row.get(k) or [None, None])[1] if isinstance(row.get(k), list) and len(row[k]) > 1 else None
            out.update(status='CAPTURED', observed_at=slot.isoformat(), fetched_at=fetched_at.isoformat(),
                       source_id='JMA_AMEDAS_MAP', raw_sha256=hashlib.sha256(raw).hexdigest(),
                       available_before_cutoff=slot <= freeze_at,
                       observation={'temperature_c': v('temp'), 'precipitation_10m_mm': v('precipitation10m'),
                                    'precipitation_1h_mm': v('precipitation1h'), 'precipitation_24h_mm': v('precipitation24h'),
                                    'wind_speed_ms': v('wind'), 'wind_direction_code': v('windDirection'),
                                    'gust_ms': v('gust'), 'humidity_pct': v('humidity')},
                       quality_flags={k: q(k) for k in ('temp', 'precipitation10m', 'wind', 'humidity')})
            return out
        out['status'] = 'NO_OBSERVATION'
    except Exception as exc:
        out['error'] = f'{type(exc).__name__}:{str(exc)[:120]}'
    return out


def diff(a, b):
    """Observation change between two captures (T-45 vs T-10) for the checkpoint record."""
    if not (a and b and a.get('status') == b.get('status') == 'CAPTURED'):
        return None
    oa, ob = a['observation'], b['observation']
    return {k: [oa.get(k), ob.get(k)] for k in oa if oa.get(k) != ob.get(k)}

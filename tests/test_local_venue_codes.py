import json
import re
from pathlib import Path

from runtime.local_autopilot import formal_rakuten as fr, rakuten as rk

REPO = Path(__file__).resolve().parents[1]


def test_every_rakuten_venue_reaches_runtime_static_and_full29():
    """P0-2 (11/21 高知 KOC/KCH): every venue the autopilot can discover must be accepted by the Runtime
    /source/acquire, the Static owner policy and the Full29 compiler after the formal-side translation."""
    app = (REPO / 'runtime/railway_local_bundle/km/app_v16.py').read_text()
    baba = dict(re.findall(r'"([A-Z]{3})": "(\d{2})"', app.split('RAKUTEN_BABA =')[1].split('}')[0]))
    policy = json.loads((REPO / 'profiles/local_production_static_owner_20261116_v1_1.json').read_text())
    comp = (REPO / 'runtime/local_nar_evidence_candidate.py').read_text()
    for code, (vid, name) in rk.VENUES.items():
        fv = fr.FORMAL_VENUE.get(vid, vid)
        assert baba.get(fv) == code, (vid, fv)
        assert fv in policy['venues'] and fv in policy['venue_canons'], fv
        assert f'"{fv}": "{name}"' in comp, fv

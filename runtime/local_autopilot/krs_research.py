"""KCP CAL-01/02 research re-runs of KRS on settled formal races (Owner 2026-11-26 21:35 「進めて」).

The weekly KRS calibration baseline (krs_calib) found that KRS under-predicts how often the horses in the front 3 at
the first corner are still in the front 3 at the last corner (predicted 0.42, actual 0.71, 173R). The engine's
parameter_map is pinned inside the Production service, so this does NOT change it. Instead, after a race is settled,
the frozen KRS input of that formal race (formal/<KEY>.krs_input.json, kept from 2026-11-27) is re-run through the
same external KRS-Engine with a pre-registered input variant (position-holding features raised for every runner),
same seed and 5,000 runs, as NON-PRODUCTION research. krs_calib compares the variants with the formal KRS on the
same races. Nothing here reaches the formal prediction, the tickets or the delivery.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

PROFILE = 'KM-LOCAL-KRS-RESEARCH-RERUN-v1.0-20261126'
VARIANTS = {   # pre-registered 2026-11-26 21:40 JST; a new variant = a new name, never an edit of these
    'HOLD15': {'early_position_hold': 15, 'midrace_hold': 15, 'front_friction_tolerance': 15},
}
MAX_PER_NIGHT = 40


def variant_input(kin, name):
    if name == 'BASE':   # the unmodified input: re-run while auto_policy has adopted a variant (probation)
        return copy.deepcopy(kin)
    add = VARIANTS[name]
    out = copy.deepcopy(kin)
    for h in out.get('horses') or []:
        hsv = h.get('hsv') or {}
        for k, d in add.items():
            if k in hsv:
                hsv[k] = round(min(100.0, max(0.0, float(hsv[k]) + d)), 6)
    return out


def nightly(root, day, runner=None, limit=MAX_PER_NIGHT):
    """Re-run every settled formal race of `day` that has a kept KRS input and no research file yet."""
    if runner is None:
        from runtime.local_autopilot.shadow29 import research_krs as runner
    dd = Path(root) / day
    done = 0
    names = list(VARIANTS)
    try:
        from runtime.local_autopilot import auto_policy
        if auto_policy.active(auto_policy.load(root), 'krs', day):
            names.append('BASE')
    except Exception:
        pass
    for kp in sorted((dd / 'formal').glob('*.krs_input.json')):
        key = kp.name.split('.')[0]
        if not (dd / f'{key}.result.json').exists():
            continue
        kin = json.loads(kp.read_text())
        seed = int((kin.get('simulation') or {}).get('master_seed') or 1)
        rid = str((kin.get('race') or {}).get('race_id') or key)
        for name in names:
            outp = dd / 'formal' / f'{key}.krs_research_{name}.json'
            if outp.exists() or done >= limit:
                continue
            meta, res = runner(variant_input(kin, name), f'{rid}-RESEARCH-{name}', 5000, seed)
            raw = ((res or {}).get('artifact') or {}).get('raw_output') or {}
            outp.write_text(json.dumps({'profile': PROFILE, 'variant': name, 'add': VARIANTS.get(name, {}),
                                        'classification': 'NON_PRODUCTION_RESEARCH_RERUN_AFTER_RESULT',
                                        'run': {k: meta.get(k) for k in ('http_status', 'receipt_status', 'actual_run_count',
                                                                         'input_sha256', 'output_sha256', 'elapsed_s')},
                                        'summary': raw.get('summary') or []}, ensure_ascii=False) + '\n')
            done += 1
    return done

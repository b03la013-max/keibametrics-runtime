"""Verify the frozen R1 registration from any checkout without rewriting it.

One historical definition key contains the author's absolute checkout path.
Map only that recorded prefix to this checkout, retain the original key and
hash, and reject traversal, changed bytes or changed registration fingerprints.
This read-only verifier never activates a candidate or rebuilds its definition.
"""
import argparse
import hashlib
import json
from pathlib import Path

RECORDED_PREFIX = '/workspace/scratch/ab7e656e13a3/km-day-review/'
PLAN = 'runtime/daily_reviews/JRA-2026-10-17/preregistered_shadow_comparison.json'


def sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def verify(root):
    root = Path(root).resolve()
    plan = json.loads((root / PLAN).read_text())
    if sha({k: v for k, v in plan.items() if k != 'policy_fingerprint'}) != plan['policy_fingerprint']:
        raise ValueError('REGISTRATION_FINGERPRINT_MISMATCH')
    for candidate in plan['per_candidate']:
        value = {k: v for k, v in candidate.items() if k != 'policy_fingerprint'}
        if sha({'candidate': value, 'definitions': plan['definition_sha256']}) != candidate['policy_fingerprint']:
            raise ValueError('CANDIDATE_FINGERPRINT_MISMATCH:' + candidate['candidate_id'])
    verified = []
    for original, expected in plan['definition_sha256'].items():
        relative = original[len(RECORDED_PREFIX):] if original.startswith(RECORDED_PREFIX) else original
        path = (root / relative).resolve()
        if Path(relative).is_absolute() or not path.is_relative_to(root):
            raise ValueError('DEFINITION_PATH_OUTSIDE_CHECKOUT:' + original)
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('FROZEN_DEFINITION_CHANGED:' + original)
        verified.append({'original_definition_key': original, 'checkout_path': relative, 'sha256': expected})
    return {'registration_fingerprint': plan['policy_fingerprint'], 'definition_count': len(verified),
            'candidate_count': len(plan['per_candidate']), 'verified_definitions': verified,
            'registration_bytes_rewritten': False, 'activation_performed': False,
            'registration_status': plan['status'], 'production_effect': 'NONE'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--root', default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    print(json.dumps(verify(args.root), ensure_ascii=False, indent=2))

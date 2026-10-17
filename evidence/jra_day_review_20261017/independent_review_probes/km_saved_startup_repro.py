"""Reproduce only the reviewed saved Railway diagnostic command, locally.

No Railway API, production environment, credentials, signing, or server startup.
This is a failure reproduction, never a KRS restart acceptance result.
"""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile

EXPECTED_COMMAND_SHA256 = '7e0a88dae4037bb1b8c9bbcde56d8116ac5fbfe493690bdf0a6ba753e84f0778'


def reproduce(command):
    digest = hashlib.sha256(command.encode('utf-8')).hexdigest()
    if digest != EXPECTED_COMMAND_SHA256:
        raise ValueError('UNREVIEWED_COMMAND: refusal to execute')
    argv = shlex.split(command)
    results = []
    with tempfile.TemporaryDirectory(prefix='km-saved-startup-repro-') as tmp:
        # Do not inherit any Production blob, signing key, network/proxy setting.
        base = {'PATH': str(Path(sys.executable).parent) + os.pathsep + os.defpath,
                'PYTHONUNBUFFERED': '1'}
        probe = base64.b64encode(b'LOCAL_SYNTHETIC_PROBE_NOT_RUNTIME_CODE').decode()
        for name, additions, expected in [
            ('no_blobs', {}, 9),
            ('synthetic_blobs', {k: probe for k in (
                'KM_LOCAL_COMBINED_B64', 'KM_LOCAL_BOOTSTRAP_B64',
                'KM_LOCAL_BOOTSTRAP_B64_V4')}, 9),
            ('malformed_blob', {'KM_LOCAL_COMBINED_B64': 'a'}, 1),
        ]:
            result = subprocess.run(argv, cwd=tmp, env={**base, **additions},
                                    capture_output=True, text=True, timeout=5)
            results.append({'case': name, 'returncode': result.returncode,
                            'expected_returncode': expected,
                            'stdout': result.stdout, 'stderr': result.stderr,
                            'pass': result.returncode == expected})
    return {'classification': 'LOCAL DIAGNOSTIC FAILURE REPRODUCTION / NOT LIVE ACCEPTANCE',
            'command_sha256': digest, 'production_mutations': 0,
            'production_credentials_used': False, 'cases': results,
            'runtime_cold_start': 'NOT EXECUTED', 'runtime_restart': 'NOT EXECUTED',
            'runtime_rollback': 'NOT EXECUTED'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command_json', type=Path,
                        help='JSON string containing the captured saved command')
    args = parser.parse_args()
    report = reproduce(json.loads(args.command_json.read_text()))
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if all(x['pass'] for x in report['cases']) else 1)

"""Execute the runner's actual KRS block against a frozen response.

Faults must still stop the runner while leaving the observed body available
to the existing always-upload step. No network or new signature is used.
"""
import copy
import json
import os
from pathlib import Path
import sys
import textwrap

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
from jra_production_krs_contract import production_krs_payload, assert_production_krs_receipt, JRAProductionKRSContractError


@pytest.mark.parametrize('fault', ['output_hash', 'signature', 'http', 'none'])
def test_observed_krs_response_survives_failure(tmp_path, fault):
    rid = 'KM-JRA-KYO-20261017-R11'
    req = json.loads((ROOT / 'runtime/requests' / (rid + '-LIVE-R1-FORMAL.json')).read_text())
    original = json.loads((ROOT / 'evidence/jra_day_review_20261017/krs_checkpoints/39007251004' / rid / 'krs_response.json').read_text())
    response = copy.deepcopy(original)
    if fault == 'output_hash':
        response['output_canonical_json'] += ' '
    if fault == 'http':
        response = {'error': 'upstream temporary failure'}
    calls, stages = [], []
    def call(base, path, payload, **kwargs):
        calls.append(path)
        return ((503 if fault == 'http' else 200), response) if path == '/krs/execute' else (200, {'valid': fault != 'signature'})
    workflow = (ROOT / '.github/workflows/km-formal-request-runner.yml').read_text()
    block = workflow[workflow.index('          kcode,k=call(KRS,"/krs/execute"'):workflow.index('          # Persist the actual structured KRS output')]
    env = dict(call=call, KRS='unused', kpayload=production_krs_payload(req), kbody=b'fixture',
               artifact_dir=str(tmp_path), os=os, json=json, assert_production_krs_receipt=assert_production_krs_receipt,
               ENGINE_SHA=req['engine_sha256'], khashes={'wire_sha256': 'fixture'}, stage=lambda *a, **kw: stages.append(a))
    if fault == 'none':
        exec(compile(textwrap.dedent(block), '<actual-workflow-krs-block>', 'exec'), env)
        assert stages == [('KRS_EXECUTION_VERIFIED',)]
    else:
        error = JRAProductionKRSContractError if fault == 'output_hash' else AssertionError
        with pytest.raises(error):
            exec(compile(textwrap.dedent(block), '<actual-workflow-krs-block>', 'exec'), env)
        assert not stages
    assert json.loads((tmp_path / 'krs_response.json').read_text()) == response
    assert ('/verify' in calls) == (fault in ('signature', 'none'))
    assert original == json.loads((ROOT / 'evidence/jra_day_review_20261017/krs_checkpoints/39007251004' / rid / 'krs_response.json').read_text())

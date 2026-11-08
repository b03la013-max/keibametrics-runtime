"""Durable intent and returned envelope for the existing JRA RESULT signer.

These records are transport evidence. Only the formal RESULT verifier admits
an envelope into the verified RESULT phase.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
from uuid import uuid4

from execution_store import phase_root, require_public_json_files


class ResultSubmissionError(ValueError):
    pass


def _binding(execution_id, request):
    race_id = request['race_id']
    if not isinstance(race_id, str) or not re.fullmatch(r'KM-JRA-[A-Z]{3}-\d{8}-R\d{2}', race_id):
        raise ResultSubmissionError('RESULT_SUBMISSION_RACE_IDENTITY_INVALID')
    if not isinstance(execution_id, str) or not re.fullmatch(re.escape(race_id) + r'-LIVE-R[1-9]\d*', execution_id):
        raise ResultSubmissionError('RESULT_SUBMISSION_EXECUTION_IDENTITY_INVALID')
    raw = json.dumps(request, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    refs = request['frozen_prediction_ref']
    return {'profile': 'KM-JRA-RESULT-SUBMISSION-v1', 'race_id': race_id,
            'execution_id': execution_id, 'request_sha256': hashlib.sha256(raw).hexdigest(),
            'immutable_final_sha256': refs['immutable_final_sha256'],
            'final_receipt_sha256': refs['final_receipt_sha256']}


def _record(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n'
    with path.open('x', encoding='utf-8') as stream:
        stream.write(raw)
    return path


def _read(path):
    if path.is_symlink():
        raise ResultSubmissionError('RESULT_SUBMISSION_PATH_INVALID')
    try:
        record = json.loads(path.read_text(encoding='utf-8'))
    except FileNotFoundError:
        return None
    if not isinstance(record, dict):
        raise ResultSubmissionError('RESULT_SUBMISSION_RECORD_INVALID')
    return record


class ResultSubmission:
    def __init__(self, root, execution_id, request):
        self.binding = _binding(execution_id, request)
        self.path = phase_root(execution_id, 'RESULT_SUBMISSION', Path(root) / 'runtime/executions')
        self._claim = None

    def enroll(self):
        """Publish enrollment in the same commit as the newly created request."""
        return _record(self.path / 'ENROLLED.json', self.binding)

    def state(self):
        enrollment = _read(self.path / 'ENROLLED.json')
        claim = _read(self.path / 'CLAIM.json')
        returned = _read(self.path / 'RESPONSE.json')
        if enrollment is None and claim is None and returned is None:
            return 'LEGACY_UNRESOLVED', None
        if enrollment != self.binding:
            raise ResultSubmissionError('RESULT_SUBMISSION_ENROLLMENT_BINDING_MISMATCH')
        if claim is None and returned is None:
            return 'READY', None
        run = (claim or {}).get('runner_attempt')
        nonce = (claim or {}).get('claim_nonce')
        if (not isinstance(run, str) or not re.fullmatch(r'[1-9]\d*-[1-9]\d*', run)
                or not isinstance(nonce, str) or not re.fullmatch(r'[a-f0-9]{32}', nonce)
                or claim != {**self.binding, 'runner_attempt': run, 'claim_nonce': nonce}):
            raise ResultSubmissionError('RESULT_SUBMISSION_CLAIM_BINDING_MISMATCH')
        if returned is None:
            return 'SIGNER_OUTCOME_UNKNOWN', None
        envelope = returned.get('envelope') if isinstance(returned, dict) else None
        if not isinstance(envelope, dict) or returned != {**claim, 'envelope': envelope}:
            raise ResultSubmissionError('RESULT_SUBMISSION_RESPONSE_BINDING_MISMATCH')
        return 'RESPONSE_RECORDED', envelope

    def claim(self, run_id, publish):
        if self.state()[0] != 'READY' or not re.fullmatch(r'[1-9]\d*-[1-9]\d*', run_id):
            raise ResultSubmissionError('RESULT_SUBMISSION_CLAIM_UNAVAILABLE')
        claim = {**self.binding, 'runner_attempt': run_id, 'claim_nonce': uuid4().hex}
        publish(_record(self.path / 'CLAIM.json', claim))
        self._claim = claim

    def save_response(self, envelope, publish):
        if (self.state()[0] != 'SIGNER_OUTCOME_UNKNOWN' or self._claim is None or
                _read(self.path / 'CLAIM.json') != self._claim):
            raise ResultSubmissionError('RESULT_SUBMISSION_RESPONSE_CLAIM_MISMATCH')
        path = _record(self.path / 'RESPONSE.json', {**self._claim, 'envelope': envelope})
        require_public_json_files([path])
        publish(path)


def publish_to_main(root, path):
    """Publish one immutable record. A concurrent conflicting claim loses."""
    root = Path(root).resolve()
    name = path.resolve().relative_to(root).as_posix()

    def git(*args):
        return subprocess.run(['git', '-c', 'user.name=keibametrics-runtime', '-c',
                               'user.email=actions@users.noreply.github.com', *args],
                              cwd=root, check=False, timeout=30,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode

    if git('add', '--', name) or git('commit', '--only', '-m',
            'result: persist JRA signer transport evidence [skip ci]', '--', name):
        raise ResultSubmissionError('RESULT_SUBMISSION_COMMIT_FAILED')
    for attempt in range(3):
        if not git('push', 'origin', 'HEAD:main'):
            return
        if attempt == 2 or git('fetch', 'origin', 'main'):
            break
        if git('rebase', 'FETCH_HEAD'):
            git('rebase', '--abort')
            break
    raise ResultSubmissionError('RESULT_SUBMISSION_PUBLICATION_UNCONFIRMED')

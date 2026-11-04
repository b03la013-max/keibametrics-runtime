"""Portable one-Race FNB private research execution, never a Production grant.

Supply an already permitted signed SOURCE, exact Race Intent, pinned trust file
and canonical Engine. Acquisition, model adoption, signing, deployment and
recipient delivery are independent authorities and are not issued by this CLI.
All originals/results stay outside git. Existing immutable KRS executions may
be reused only after exact byte and canonical Engine-input equivalence checks.
"""
from __future__ import annotations

import argparse
import base64
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

from runtime.local_fnb_r14_private_dual_krs import ENGINE_SHA, MAP_SHA

PROFILE = 'KM-FNB-PRIVATE-SINGLE-RACE-RESEARCH-RUNTIME-v1-20261103'
CLASSIFICATION = 'UNADOPTED_PRIVATE_RESEARCH_DIAGNOSTIC_NOT_FORMAL_NOT_REGISTERED_OOS'
MODEL_SHA = '8fbee4eafada822ddb28185eb7233a96626e9ce93c8ff9a705fc3516faf9eed4'
MODEL_PROFILE_SHA = 'ba2e04aa9ca36f9adb2813d2376c81c15b857f15bebc320a408c5877c9240735'
PRESTART_CLASSIFICATION = 'SINGLE_RACE_PRESTART_NONPRODUCTION_NOT_REGISTERED_OOS'
REPO = Path(__file__).resolve().parents[1]


class ResearchHold(ValueError):
    pass


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       indent=2, allow_nan=False) + '\n').encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def _stamp(value):
    out = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    if out.tzinfo is None:
        raise ResearchHold('RESEARCH_AWARE_CLOCK_REQUIRED')
    return out.astimezone(timezone.utc)


def _pinned(path, expected):
    path = Path(path)
    if path.is_symlink() or not re.fullmatch('[a-f0-9]{64}', str(expected)):
        raise ResearchHold('PINNED_ORIGINAL_SHA_REQUIRED')
    data = path.read_bytes()
    if digest(data) != expected:
        raise ResearchHold('PINNED_ORIGINAL_BYTES_MISMATCH')
    return data


def _actual_clock():
    return datetime.now(timezone.utc)


def _prestart_clock(request, *, not_before):
    """Use the process clock, never an intent-provided historical as-of."""
    observed = _stamp(_actual_clock())
    if observed < _stamp(not_before):
        raise ResearchHold('PRIVATE_PRESTART_CLOCK_REGRESSION')
    if not observed < _stamp(request['prediction_cutoff']) < _stamp(request['scheduled_post_at']):
        raise ResearchHold('PRIVATE_PRESTART_CUTOFF_EXPIRED_NOT_NO_BET')
    return observed


def verify_private_owner_decision(path, pin, *, request, source, check_prestart=True):
    """Verify a supplied immutable decision; do not issue adoption or rights.

    The caller pins the actual Owner instruction record, separately from the
    already verified SOURCE. This is not a cryptographic Owner signature or a
    Provider permission. The fixed model and profile themselves stay unchanged.
    """
    data = _pinned(path, pin)
    decision = json.loads(data)
    scope = decision.get('permitted_scope') or {}
    authority = decision.get('authority_evidence') or {}
    profile_path = REPO / 'profiles/local_fnb_context_static_candidate_v0.1_20261103.json'
    _pinned(REPO / 'runtime/local_fnb_context_static_candidate.py', MODEL_SHA)
    _pinned(profile_path, MODEL_PROFILE_SHA)
    if (decision.get('profile') != 'KM-FNB-FIXED-CONTEXT-PRIVATE-OWNER-EXECUTION-DECISION-20261103-R1'
            or decision.get('decision') != 'APPROVED_FIXED_MODEL_PRIVATE_NONPRODUCTION_RESEARCH_USE'
            or decision.get('model_id') != 'KM-FNB-CONTEXT-PARETO-STATIC-RESEARCH-v0.1-20261103'
            or decision.get('model_version') != '0.1'
            or decision.get('model_code_sha256') != MODEL_SHA
            or decision.get('model_profile_sha256') != MODEL_PROFILE_SHA
            or authority.get('type') != 'DIRECT_USER_INSTRUCTION_IN_CURRENT_CHAT'
            or authority.get('owner_identity_confirmed_by_direct_instruction') is not True
            or authority.get('record_is_crypto_signature') is not False
            or not authority.get('request_id')
            or scope.get('classification') != PRESTART_CLASSIFICATION
            or scope.get('family_id') != 'LOCAL' or scope.get('venue_id') != 'FNB'
            or scope.get('purpose') != 'WHOLLY_PRIVATE_NONCOMMERCIAL_RESEARCH'
            or request.get('family_id') != 'LOCAL' or request.get('venue_id') != 'FNB'
            or type(request.get('race_no')) is not int
            or request['race_no'] not in (scope.get('races_by_date') or {}).get(request.get('race_date'), [])
            or decision.get('selection_policy') != 'EXISTING_ORIGINAL_STRICT_MEC_ONLY_NEW_PROTECTION_POLICY_NOT_ADOPTED'
            or any(decision.get(key) is not False for key in ('production_owner_adoption',
                'production_scope_changed', 'numerical_policy_changed', 'signing_key_created_or_changed',
                'independent_BC_authorized_by_this_record', 'actual_purchase_authorized'))):
        raise ResearchHold('PRIVATE_OWNER_DECISION_SCOPE_OR_MODEL_MISMATCH')
    if (_stamp(request['scheduled_post_at']) - _stamp(request['prediction_cutoff'])).total_seconds() != 300:
        raise ResearchHold('PRIVATE_PRESTART_APPROVED_CUTOFF_300_SECONDS_REQUIRED')
    approved = _stamp(decision['authorization_observed_at'])
    freeze = _stamp(source['source_freeze_at'])
    # Lawfully obtained current SOURCE may predate the model-use decision.
    # The decision must precede execution, not the independent data capture.
    observed = (_prestart_clock(request, not_before=freeze) if check_prestart
                else _stamp(_actual_clock()))
    if observed < freeze:
        raise ResearchHold('PRIVATE_PRESTART_CLOCK_REGRESSION')
    if approved > observed:
        raise ResearchHold('PRIVATE_OWNER_DECISION_NOT_YET_EFFECTIVE')
    return {'decision_sha256': pin, 'decision_bytes': len(data),
            'owner_request_id': authority['request_id'],
            'approved_at': approved.isoformat(), 'verified_at': observed.isoformat(),
            'classification': PRESTART_CLASSIFICATION,
            'model_code_sha256': MODEL_SHA, 'model_profile_sha256': MODEL_PROFILE_SHA,
            'owner_signature_claimed': False, 'provider_rights_granted': False,
            'production_scope_changed': False}, data


def _private_root(path):
    raw = Path(path).absolute()
    for ancestor in (raw, *raw.parents):
        if ancestor.is_symlink():
            raise ResearchHold('PRIVATE_STORE_SYMLINK_FORBIDDEN')
        marker = ancestor / '.git'
        if marker.exists():
            # A literally empty bootstrap directory is not a Git repository.
            # Any real or damaged Git metadata, including fresh git-init, bars Raw.
            if marker.is_file() or any(marker.iterdir()):
                raise ResearchHold('PRIVATE_SOURCE_IN_GIT_WORKTREE_FORBIDDEN')
    root = raw.resolve()
    if root == REPO or REPO in root.parents:
        raise ResearchHold('PRIVATE_SOURCE_IN_GIT_WORKTREE_FORBIDDEN')
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    return root


def _immutable(path, data):
    path = Path(path)
    _private_root(path.parent)
    if path.is_symlink():
        raise ResearchHold('PRIVATE_STORE_SYMLINK_FORBIDDEN')
    try:
        with path.open('xb') as f:
            f.write(data)
        path.chmod(0o600)
    except FileExistsError:
        if path.read_bytes() != data:
            raise ResearchHold('IMMUTABLE_RESEARCH_ORIGINAL_REVISION_CONFLICT')
    if path.read_bytes() != data:
        raise ResearchHold('PRIVATE_RESEARCH_READBACK_FAILED')
    return {'path': str(path), 'sha256': digest(data), 'bytes': len(data)}


@contextmanager
def _repo_cwd():
    # Existing materializer registry paths are repo-relative. The CLI is one
    # process per Race; restore the caller's cwd even when a component holds.
    previous = Path.cwd()
    os.chdir(REPO)
    try:
        yield
    finally:
        os.chdir(previous)


def verify_source(envelope, request, trust):
    # Legacy receipt helpers import their sibling modules by bare name. Bind
    # them to this checkout explicitly rather than depending on the caller cwd.
    runtime_path = str(REPO / 'runtime')
    if runtime_path not in sys.path:
        sys.path.insert(0, runtime_path)
    from runtime.local_fnb_r12_historical_krs_witness import verify_envelope
    from runtime.local_fnb_r20_chat_completion import _verify_captured_source
    from runtime.local_fnb_r13_private_source_admission import admit, PURPOSE, SCOPE
    if (request.get('family_id') != 'LOCAL' or request.get('venue_id') != 'FNB'
            or not re.fullmatch(r'KM-LOCAL-FNB-\d{8}-R\d{2}(?:-[A-Za-z0-9_]+)*', str(request.get('race_id')))
            or trust.get('engine_sha256') != ENGINE_SHA
            or trust.get('parameter_map_sha256') != MAP_SHA):
        raise ResearchHold('SOURCE_INTENT_OR_PINNED_TRUST_MISMATCH')
    day = str(request.get('race_date') or '')
    number = request.get('race_no')
    try:
        datetime.strptime(day, '%Y-%m-%d')
    except ValueError as error:
        raise ResearchHold('SOURCE_INTENT_RACE_DATE_INVALID') from error
    if type(number) is not int or not 1 <= number <= 12:
        raise ResearchHold('SOURCE_INTENT_RACE_NUMBER_INVALID')
    expected_prefix = 'KM-LOCAL-FNB-' + day.replace('-', '') + '-R' + str(number).zfill(2)
    if not re.fullmatch(re.escape(expected_prefix) + r'(?:-[A-Za-z0-9_]+)*', request['race_id']):
        raise ResearchHold('SOURCE_INTENT_RACE_IDENTITY_MISMATCH')
    artifact = verify_envelope(envelope, race_id=request['race_id'], phase='SOURCE',
        status='SOURCE_FROZEN', public=base64.b64decode(trust['receipt_public_key_b64'], validate=True), cfg=trust)
    # Metadata admission and real Raw replay both remain mandatory. Signature
    # verification with caller-supplied trust does not establish provider scope.
    admit(source=artifact, request=request, purpose=PURPOSE, classification=SCOPE,
          destination=Path(tempfile.gettempdir()) / 'km-private-research-admission', public_repo_root=REPO)
    _verify_captured_source(artifact, request, datetime.now(timezone.utc))
    return artifact


def build_upstream(numerical, *, numerical_sha256):
    """Reuse the existing HSV mapping; no new score, coefficient or physics."""
    from runtime.local_krs_bridge_candidate import build_runner_bridge, PROFILE as BRIDGE
    race = deepcopy(numerical['race'])
    state = numerical['numerical_current_state']
    race.update(date=numerical['race_date'], racecourse='船橋',
                distance=race.get('distance_m', race.get('distance')),
                prediction_id=numerical['race_id'] + '-CURRENT29-CONTEXT-DIAGNOSTIC',
                going=state.get('official_going'), weather=state.get('official_weather'))
    environment = deepcopy(numerical['numerical_environment'])
    environment.pop('production_numerical_authority', None)
    environment['candidate_only'] = True
    horses, provenance = [], []
    for row in numerical['runners']:
        bridge = build_runner_bridge(row)
        horses.append({'horse_no': int(row['runner_id']), 'name': row['name'],
            'hsv': bridge['hsv'], 'static': bridge['static'],
            'static_roles': [], 'uncertainty_scale': bridge['uncertainty_scale'],
            'evidence': bridge['evidence']})
        provenance.append({'runner_id': row['runner_id'], 'mapping': bridge['provenance']})
    return {'race': race, 'environment': environment, 'horses': horses,
            'simulation': {'run_count': 5000, 'master_seed': 1},
            'keibametrics_input_authority': {'classification': CLASSIFICATION,
                'bridge_profile': BRIDGE, 'numerical_materialization_sha256': numerical_sha256,
                'production_authority': False}}, provenance


def engine_input_projection(value):
    """Exactly the four top-level objects read by the pinned Engine constructor.

    Keep entire race/environment/horse/simulation objects, including roles and
    RNG identity. Only external tracing metadata is excluded; nothing inside
    the Engine inputs is omitted or normalized to permit a cache hit.
    """
    return {key: deepcopy(value[key]) for key in ('race', 'environment', 'horses', 'simulation')}


def _verify_output(output, requested):
    snap, engine = output['snapshot'], output['engine']
    active = [int(row['horse_no']) for row in requested['horses']]
    if (snap.get('master_seed') != 1 or snap.get('run_count') != 5000
            or snap.get('prediction_id') != requested['race']['prediction_id']
            or snap.get('field_size') != len(active)
            or sorted(int(row['horse_no']) for row in output['summary']) != sorted(active)
            or engine.get('engine_version') != '1.1.0'
            or engine.get('parameter_map_version') != '0.1-provisional'
            or engine.get('parameter_status') != 'PROVISIONAL_UNCALIBRATED'):
        raise ResearchHold('KRS_OUTPUT_IDENTITY_COUNT_OR_CALIBRATION_MISMATCH')


def reuse_krs(cache, requested, destination, *, receipt_sha256):
    """Copy verified old execution originals; never claim a new Engine run.

    Cache manifest paths are relative to the supplied directory. The cache is
    an explicit user-selected immutable execution, not a model qualification.
    Its execution input may have different non-Engine tracing metadata; both
    full input SHA values and the exact Engine-input equality proof are kept.
    """
    cache = Path(cache).resolve()
    receipt_path = cache / 'context_receipt.json'
    receipt_bytes = _pinned(receipt_path, receipt_sha256)
    receipt = json.loads(receipt_bytes)
    source_input = _pinned(cache / 'context_input.json', receipt['input_sha256'])
    source_output = _pinned(cache / 'context_output.json', receipt['output_sha256'])
    original = json.loads(source_input)
    if (receipt.get('status') != 'EXECUTED' or receipt.get('process_returncode') != 0
            or receipt.get('engine_sha256') != ENGINE_SHA or receipt.get('parameter_map_sha256') != MAP_SHA
            or receipt.get('actual_base_run_count') != 5000 or receipt.get('actual_seed') != 1
            or receipt.get('model_code_sha256') != MODEL_SHA
            or engine_input_projection(original) != engine_input_projection(requested)):
        raise ResearchHold('KRS_CACHE_NOT_IDENTICAL_ENGINE_INPUT')
    output = json.loads(source_output)
    _verify_output(output, requested)
    saved = {name: _immutable(Path(destination) / name, data) for name, data in (
        ('execution_input.json', source_input), ('execution_output.json', source_output),
        ('execution_original_receipt.json', receipt_bytes))}
    return {'status': 'REUSED_IMMUTABLE_CANONICAL_KRS', 'new_engine_execution': False,
        'execution_input_sha256': digest(source_input), 'requested_input_sha256': digest(encoded(requested)),
        'engine_input_projection_sha256': digest(encoded(engine_input_projection(requested))),
        'full_input_bytes_equal': source_input == encoded(requested),
        'exact_engine_input_equal': True, 'source_originals': saved,
        'output_sha256': digest(source_output), 'engine_sha256': ENGINE_SHA,
        'parameter_map_sha256': MAP_SHA, 'run_count': 5000, 'seed': 1,
        'uncalibrated_occurrences_not_win_probability_or_EV': True}


def execute_krs(requested, *, engine, params, destination, cache=None, cache_receipt_sha256=None):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True, mode=0o700)
    _immutable(destination / 'requested_input.json', encoded(requested))
    if engine is not None:
        _pinned(engine, ENGINE_SHA)
    if params is not None:
        _pinned(params, MAP_SHA)
    if cache is not None:
        return reuse_krs(cache, requested, destination, receipt_sha256=cache_receipt_sha256)
    if engine is None or params is None:
        raise ResearchHold('PINNED_CANONICAL_ENGINE_AND_MAP_REQUIRED_WITHOUT_CACHE')
    _pinned(engine, ENGINE_SHA)
    _pinned(params, MAP_SHA)
    with tempfile.TemporaryDirectory(dir=destination) as temporary:
        path = Path(temporary) / 'output.json'
        command = [sys.executable, str(Path(engine).resolve()), str(destination / 'requested_input.json'),
                   '--params', str(Path(params).resolve()), '--runs', '5000', '--seed', '1', '--output', str(path), '--short']
        started_at = datetime.now(timezone.utc).isoformat()
        run = subprocess.run(command, capture_output=True, text=True, timeout=240)
        completed_at = datetime.now(timezone.utc).isoformat()
        if run.returncode != 0 or not path.is_file():
            raise ResearchHold('CANONICAL_KRS_PROCESS_FAILED')
        data = path.read_bytes()
        _verify_output(json.loads(data), requested)
    saved_input = _immutable(destination / 'execution_input.json', encoded(requested))
    saved_output = _immutable(destination / 'execution_output.json', data)
    return {'status': 'EXECUTED_CANONICAL_KRS', 'new_engine_execution': True,
        'execution_input_sha256': saved_input['sha256'], 'requested_input_sha256': saved_input['sha256'],
        'exact_engine_input_equal': True, 'output_sha256': saved_output['sha256'],
        'engine_sha256': ENGINE_SHA, 'parameter_map_sha256': MAP_SHA, 'run_count': 5000, 'seed': 1,
        'process_returncode': 0, 'started_at': started_at, 'completed_at': completed_at,
        'uncalibrated_occurrences_not_win_probability_or_EV': True}


def _verify_saved_manifest(path, *, recipe=None, race_id=None):
    manifest = json.loads(path.read_bytes())
    root = path.parent
    if manifest.get('classification') == PRESTART_CLASSIFICATION:
        if (root / 'prestart_finalization_failure.json').exists():
            raise ResearchHold('PRIVATE_PRESTART_FINAL_SAVE_EXPIRED')
        finalization = json.loads((root / 'prestart_finalization_receipt.json').read_bytes())
        if (finalization.get('status') != 'PRIVATE_PRESTART_SAVE_READBACK_VERIFIED'
                or finalization.get('manifest_sha256') != digest(path.read_bytes())
                or finalization.get('prediction_cutoff') != manifest.get('prediction_cutoff')
                or not _stamp(manifest['prestart_computation_completed_at'])
                    <= _stamp(finalization['save_readback_verified_at']) < _stamp(manifest['prediction_cutoff'])):
            raise ResearchHold('PRIVATE_PRESTART_FINAL_SAVE_PROOF_UNVERIFIED')
    if recipe is not None:
        if (manifest.get('profile') != PROFILE or manifest.get('classification') != recipe.get('execution_classification', CLASSIFICATION)
                or manifest.get('race_id') != race_id or manifest.get('input_recipe') != recipe
                or manifest.get('source_sha256') != recipe['source_sha256']
                or manifest.get('code_pins') != recipe['code_pins']
                or manifest.get('unadopted_paper_policy_choice') != recipe['paper_policy']
                or manifest.get('output_directory') != str(root)
                or type(manifest.get('registered_OOS_increment')) is not int
                or manifest['registered_OOS_increment'] != 0
                or any(manifest.get(key) is not False for key in ('provider_usage_authority_granted',
                    'model_adopted', 'formal_OWNER_scope_changed', 'numerical_consumers_changed',
                    'independent_BC', 'actual_purchase', 'formal_final', 'recipient_delivery_proven'))):
            raise ResearchHold('COMPLETED_RESEARCH_MANIFEST_IDENTITY_OR_SCOPE_CHANGED')
        if recipe.get('execution_classification') == PRESTART_CLASSIFICATION:
            approval = manifest.get('private_owner_decision') or {}
            decision_bytes = _pinned(root / 'owner_decision_original.json', recipe['owner_decision_sha256'])
            decision_original = json.loads(decision_bytes)
            if (approval.get('decision_sha256') != recipe.get('owner_decision_sha256')
                    or approval.get('decision_bytes') != len(decision_bytes)
                    or approval.get('approved_at') != _stamp(decision_original['authorization_observed_at']).isoformat()
                    or approval.get('owner_request_id') != decision_original['authority_evidence']['request_id']
                    or approval.get('model_code_sha256') != MODEL_SHA
                    or approval.get('model_profile_sha256') != MODEL_PROFILE_SHA
                    or approval.get('owner_signature_claimed') is not False
                    or approval.get('provider_rights_granted') is not False
                    or approval.get('production_scope_changed') is not False
                    or manifest.get('fixed_model_private_use_verified') is not True
                    or manifest.get('completion_before_cutoff') is not True
                    or not _stamp(manifest['prestart_computation_completed_at']) < _stamp(manifest['prediction_cutoff'])
                    or not _stamp(approval['approved_at']) <= _stamp(manifest['actual_observed_at'])
                        <= _stamp(manifest['static_freeze_at']) <= _stamp(manifest['prestart_computation_completed_at'])
                    or not _stamp(manifest['source_freeze_at']) <= _stamp(manifest['actual_observed_at'])):
                raise ResearchHold('COMPLETED_PRIVATE_PRESTART_PROOF_CHANGED')
    for item in manifest['private_artifacts']:
        target = root / item['path']
        if target.is_symlink() or root not in target.resolve().parents or digest(target.read_bytes()) != item['sha256']:
            raise ResearchHold('COMPLETED_RESEARCH_ORIGINAL_BYTES_CHANGED')
    return manifest


def _render_private_body(folder, prediction, krs, strict, paper_result, *, private_owner_decision=None, request=None,
                         static_original_saved_at=None, computational_field_label='Active'):
    approved = private_owner_decision is not None
    lines = ['# FNB・単一Race事前研究' if approved else '# FNB・単一Race研究Diagnostic', '',
        ('本人承認の固定モデルによる非Production事前研究です。正式FINAL、独立B/C、真正Forward OOS、実購入の認定はありません。本人表示の実績は別途検収します。'
         if approved else '未採用研究です。正式FINAL、発走前本人Delivery、独立B/C、真正Forward OOS、実購入の認定はありません。'),
        '旧KRSを再利用した場合、新規KRS実行数は0です。SSRは未較正頻度であり実勝率・EVではありません。', '',
        (folder / 'numerical/all_horse_29_index_report.md').read_text(), '',
        '## 全'+computational_field_label+' W/P2/P3・Role', '',
        '|馬番|W順位／区間|P2順位／区間|P3順位／区間|Role|',
        '|---:|---|---|---|---|']
    for runner in prediction['active_runners']:
        cells = []
        for column in ('W', 'P2', 'P3'):
            row = next(row for row in prediction['column_rankings'][column]['rows'] if row['runner_id'] == runner)
            cells.append(str(row['rank'] if row['rank'] is not None else 'UNKNOWN') + ' / ' +
                str(row['rank_interval']['min']) + '–' + str(row['rank_interval']['max']))
        lines.append('|' + runner + '|' + '|'.join(cells) + '|' + ','.join(prediction['roles'][runner]) + '|')
    if approved:
        lines += ['', '## 実行分類・時刻', '', '```json',
            encoded({'classification': PRESTART_CLASSIFICATION,
                'scheduled_post_at': request['scheduled_post_at'],
                'prediction_cutoff': request['prediction_cutoff'],
                'source_freeze_at': prediction['source_freeze_at'],
                'model_input_asof': prediction['freeze_at'],
                'static_original_saved_at': static_original_saved_at,
                'private_owner_decision': private_owner_decision,
                'recipient_delivery_proven': False}).decode().rstrip(), '```']
    output = json.loads((folder / 'krs/execution_output.json').read_bytes())
    lines += ['', '## 全'+computational_field_label+' KRS', '', '|馬番|馬名|SSR-W|SSR-P2|SSR-P3|SSR-T3|',
              '|---:|---|---:|---:|---:|---:|']
    for row in output['summary']:
        lines.append('|' + str(row['horse_no']) + '|' + row['name'] + '|' +
            '|'.join(str(row[key]) for key in ('SSR-W', 'SSR-P2', 'SSR-P3', 'SSR-T3')) + '|')
    lines += ['', '## 元モデルの厳格MEC', '', '```json', encoded(strict).decode().rstrip(), '```', '',
              '## 全Head-local P2・Pair-conditioned Third・UNKNOWN', '', '```json',
              encoded({key: prediction[key] for key in ('head_local_P2', 'pair_conditioned_Third',
                  'unresolved_semantic_paths')}).decode().rstrip(), '```']
    if paper_result is not None:
        lines += ['', '## 明示指定された別の未採用紙上仮説', '',
            '元の厳格MECのHOLDを解除した結果ではありません。券種ごとの独立代替案です。', '']
        for method, detail in paper_result['methods'].items():
            lines += ['### ' + method, '', '```json',
                encoded({key: value for key, value in detail.items() if key not in ('tickets', 'canonical_tree')}).decode().rstrip(),
                '```', '', '```text', detail['canonical_tree'], '```', '']
    lines += ['', '## KRS実行・再利用の系譜', '', '```json', encoded(krs).decode().rstrip(), '```', '']
    return ('\n'.join(lines) + '\n').encode()


def run(*, source_path, source_sha256, request_path, request_sha256,
        trust_path, trust_sha256, private_root, engine=None, params=None,
        krs_cache=None, krs_cache_receipt_sha256=None, paper=False, paper_policy=None, now=None,
        owner_decision_path=None, owner_decision_sha256=None):
    """Diagnostic by default; a pinned dated decision enables private prestart.

    SOURCE admission, fixed model bytes, physics, MEC and Production authority
    are unchanged. Completing this computation never proves recipient display.
    """
    from runtime.local_fnb_r13_private_single_numeric import execute as numerical_execute
    from runtime.local_fnb_observation_context import build_observation_packet
    from runtime.local_fnb_context_static_candidate import build_context, predict
    observed = now or datetime.now(timezone.utc)
    observed = _stamp(observed)
    source_bytes = _pinned(source_path, source_sha256)
    request_bytes = _pinned(request_path, request_sha256)
    trust_bytes = _pinned(trust_path, trust_sha256)
    envelope, request, trust = map(json.loads, (source_bytes, request_bytes, trust_bytes))
    source = verify_source(envelope, request, trust)
    owner_decision = owner_decision_bytes = None
    if owner_decision_path is not None or owner_decision_sha256 is not None:
        if owner_decision_path is None or owner_decision_sha256 is None:
            raise ResearchHold('PRIVATE_OWNER_DECISION_PATH_AND_PIN_REQUIRED')
        if now is not None:
            raise ResearchHold('PRIVATE_PRESTART_INTENT_ASOF_OVERRIDE_FORBIDDEN')
        if paper or paper_policy is not None:
            raise ResearchHold('PRIVATE_PRESTART_ONLY_EXISTING_STRICT_MEC_AUTHORIZED')
        owner_decision, owner_decision_bytes = verify_private_owner_decision(
            owner_decision_path, owner_decision_sha256, request=request, source=source, check_prestart=False)
        observed = _stamp(owner_decision['verified_at'])
    approved = owner_decision is not None
    classification = PRESTART_CLASSIFICATION if approved else CLASSIFICATION
    if engine is not None:
        _pinned(engine, ENGINE_SHA)
    if params is not None:
        _pinned(params, MAP_SHA)
    if krs_cache is not None:
        _pinned(Path(krs_cache) / 'context_receipt.json', krs_cache_receipt_sha256)
    elif engine is None or params is None:
        raise ResearchHold('PINNED_CANONICAL_ENGINE_AND_MAP_REQUIRED_WITHOUT_CACHE')
    root = _private_root(private_root)
    code_paths = ('runtime/local_fnb_research_runtime.py', 'runtime/local_fnb_context_static_candidate.py',
                  'runtime/local_fnb_observation_context.py', 'runtime/local_fullnumerical_production.py',
                  'runtime/local_krs_bridge_candidate.py', 'runtime/local_fnb_semantic_closure.py',
                  'runtime/local_nar_evidence_candidate.py', 'runtime/local_fullnumerical_candidate.py',
                  'runtime/local_physical/source_acquisition.py',
                  'runtime/local_fnb_r13_private_single_numeric.py',
                  'runtime/local_fnb_r13_private_source_admission.py',
                  'runtime/local_fnb_r12_historical_krs_witness.py',
                  'runtime/local_fnb_r20_chat_completion.py',
                  'runtime/local_fnb_r8_card_raw_check.py',
                  'runtime/local_fnb_r8_arithmetic_29.py',
                  'runtime/local_fnb_r8_missingness_census.py',
                  'runtime/local_fnb_r9_evidence_63.py',
                  'runtime/local_fnb_r9_history_asof.py',
                  'runtime/local_fnb_r11_venue_temporal.py',
                  'runtime/local_fnb_r12_official_change_scope.py',
                  'runtime/local_fnb_r13_private_numeric_document.py',
                  'runtime/local_production_static_owner.py',
                  'runtime/local_bvi_bloodline_research.py',
                  'runtime/minimum_efficient_coverage.py',
                  'runtime/capital_policy.py',
                  'runtime/jra_ticket_tree_renderer.py',
                  'profiles/family_user_capital_default_20261003_R1.json',
                  'mapping/local_evidence_feature_rule_registry_v1.1_production_numerical_20261008.json',
                  'mapping/local_full_numerical_mapping_v1.0_production_20261008.json',
                  'mapping/local_evidence_feature_rule_registry_v0.1_candidate_20260923.json',
                  'mapping/local_full_numerical_mapping_v0.1_candidate_20260923.json')
    if approved:
        code_paths += ('profiles/local_fnb_context_static_candidate_v0.1_20261103.json',)
    code_pins = {name: digest((REPO / name).read_bytes()) for name in code_paths}
    if code_pins['runtime/local_fnb_context_static_candidate.py'] != MODEL_SHA:
        raise ResearchHold('RESEARCH_MODEL_VERSION_SHA_CHANGED')
    if approved and code_pins['profiles/local_fnb_context_static_candidate_v0.1_20261103.json'] != MODEL_PROFILE_SHA:
        raise ResearchHold('PRIVATE_OWNER_MODEL_PROFILE_SHA_CHANGED')
    if paper_policy not in (None, 'pair-local-known', 'unknown-path-protection'):
        raise ResearchHold('EXPLICIT_PAPER_POLICY_NOT_SUPPORTED')
    paper_policy = paper_policy or ('pair-local-known' if paper else None)
    paper = paper_policy is not None
    recipe = {'source_sha256': source_sha256, 'request_sha256': request_sha256,
              'trust_sha256': trust_sha256, 'code_pins': code_pins,
              'engine_sha256': ENGINE_SHA, 'parameter_map_sha256': MAP_SHA, 'paper_policy': paper_policy}
    if approved:
        recipe.update(owner_decision_sha256=owner_decision_sha256,
                      execution_classification=PRESTART_CLASSIFICATION)
    folder = _private_root(root / request['race_id'] / digest(encoded(recipe)))
    lock = folder / '.execution.lock'
    if lock.is_symlink():
        raise ResearchHold('PRIVATE_STORE_SYMLINK_FORBIDDEN')
    with lock.open('a') as handle:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        final = folder / 'research_execution_manifest.json'
        if final.exists():
            result = _verify_saved_manifest(final, recipe=recipe, race_id=request['race_id'])
            return {**result, 'completion_reused': True, 'new_engine_executions_this_call': 0}
        # Existing immutable originals remain readable after cutoff; only a
        # new calculation must pass the actual-clock prestart guard.
        if approved:
            observed = _prestart_clock(request, not_before=observed)
        started = folder / 'run_started.json'
        if started.exists():
            asof = _stamp(json.loads(started.read_bytes())['research_asof'])
        else:
            asof = observed
            _immutable(started, encoded({'research_asof': asof.isoformat(), 'recipe': recipe}))
        if asof > observed or asof < _stamp(source['source_freeze_at']):
            raise ResearchHold('RESEARCH_ASOF_NOT_OBSERVED')
        _immutable(folder / 'source_envelope.json', source_bytes)
        _immutable(folder / 'race_intent.json', request_bytes)
        if approved:
            _immutable(folder / 'owner_decision_original.json', owner_decision_bytes)
            numerical_asof = _prestart_clock(request, not_before=observed)
        else:
            numerical_asof = asof
        with tempfile.TemporaryDirectory(dir=folder) as temporary:
            with _repo_cwd():
                num = numerical_execute(source_artifact=source, request=request, private_root=Path(temporary),
                    repo_root=REPO, now=numerical_asof, diagnostic_only=not approved)
            numeric_bytes = (Path(num['private_root']) / 'numerical_materialization.json').read_bytes()
            for file in Path(num['private_root']).iterdir():
                if file.is_file():
                    _immutable(folder / 'numerical' / file.name, file.read_bytes())
        numerical = json.loads(numeric_bytes)
        context_asof = _prestart_clock(request, not_before=numerical_asof) if approved else asof
        packet = build_observation_packet(request, envelope, generated_at=context_asof.isoformat())
        context = build_context(packet, generated_at=context_asof.isoformat())
        upstream, provenance = build_upstream(numerical, numerical_sha256=digest(numeric_bytes))
        static_input_asof = _prestart_clock(request, not_before=context_asof) if approved else asof
        prediction = predict(context, frozen_at=static_input_asof.isoformat(), upstream_krs_input=upstream)
        active = {str(row['runner_id']) for row in numerical['runners']}
        if set(prediction['active_runners']) != active:
            raise ResearchHold('FULL_ACTIVE_RESEARCH_CHAIN_MISMATCH')
        for name, value in (('observations.json', packet), ('context.json', context),
                            ('existing_hsv_bridge.json', upstream), ('hsv_provenance.json', provenance),
                            ('research_prediction.json', prediction)):
            _immutable(folder / name, encoded(value))
        # The fixed model's supplied as-of remains in its original bytes. The
        # wrapper records actual immutable-output completion separately.
        static_asof = _prestart_clock(request, not_before=static_input_asof) if approved else asof
        krs = execute_krs(prediction['PRE_KRS_input'], engine=engine, params=params,
                          destination=folder / 'krs', cache=krs_cache, cache_receipt_sha256=krs_cache_receipt_sha256)
        _immutable(folder / 'krs' / 'research_krs_receipt.json', encoded(krs))
        semantic_asof = _prestart_clock(request, not_before=static_asof) if approved else asof
        from runtime.local_fnb_semantic_closure import assess_semantics, execute_strict_mec, research_pair_local_protection
        semantics = assess_semantics(prediction, evaluated_at=semantic_asof.isoformat())
        strict = execute_strict_mec(prediction, evaluated_at=semantic_asof.isoformat())
        _immutable(folder / 'semantic_inventory.json', encoded(semantics))
        _immutable(folder / 'original_strict_mec.json', encoded(strict))
        paper_result = None
        if paper:
            if paper_policy == 'unknown-path-protection':
                from runtime.local_fnb_semantic_closure import research_unknown_path_protection
                paper_result = research_unknown_path_protection(prediction, evaluated_at=asof.isoformat())
            else:
                paper_result = research_pair_local_protection(prediction, evaluated_at=asof.isoformat())
            _immutable(folder / 'separate_unadopted_paper_hypothesis.json', encoded(paper_result))
        body = _render_private_body(folder, prediction, krs, strict, paper_result,
            private_owner_decision=owner_decision, request=request,
            static_original_saved_at=static_asof.isoformat() if approved else None)
        body_receipt = _immutable(folder / 'complete_research_body.md', body)
        if code_pins != {name: digest((REPO / name).read_bytes()) for name in code_paths}:
            raise ResearchHold('RESEARCH_IMPLEMENTATION_CHANGED_DURING_EXECUTION')
        inventory = [{'path': str(path.relative_to(folder)), 'bytes': path.stat().st_size,
                      'sha256': digest(path.read_bytes())} for path in sorted(folder.rglob('*'))
                     if path.is_file() and path.name != '.execution.lock']
        completed_asof = _prestart_clock(request, not_before=semantic_asof) if approved else None
        result = {'profile': PROFILE, 'classification': classification, 'race_id': request['race_id'],
            'actual_observed_at': observed.isoformat(), 'research_asof': asof.isoformat(),
            'input_recipe': recipe,
            'source_signature_verified_with_supplied_pinned_trust': True,
            'provider_usage_authority_granted': False, 'model_adopted': False,
            'formal_OWNER_scope_changed': False, 'numerical_consumers_changed': False,
            'independent_BC': False, 'registered_OOS_increment': 0, 'actual_purchase': False,
            'source_sha256': source_sha256, 'source_snapshot_sha256': source['source_snapshot_sha256'],
            'source_freeze_at': source['source_freeze_at'], 'numerical_sha256': digest(numeric_bytes),
            'active_runners': sorted(active, key=int), 'index_cells': len(active) * 29,
            'model_id': prediction['model_id'], 'model_version': prediction['model_version'],
            'model_code_sha256': MODEL_SHA, 'model_prediction_sha256': prediction['sha256'],
            'Context_changes_KRS_physical_arrays': False, 'KRS': krs,
            'original_strict_MEC': strict, 'paper_hypothesis_executed_separately': paper,
            'unadopted_paper_policy_choice': paper_policy,
            'paper_hypothesis_is_not_original_strict_MEC_completion': True,
            'formal_final': False, 'recipient_delivery_proven': False, 'PFS': None,
            'code_pins': code_pins, 'private_artifacts': inventory,
            'complete_private_body': body_receipt, 'output_directory': str(folder)}
        if approved:
            result.update(private_owner_decision=owner_decision,
                fixed_model_private_use_verified=True, model_output_classification=prediction['classification'],
                prediction_cutoff=request['prediction_cutoff'], scheduled_post_at=request['scheduled_post_at'],
                model_input_asof=static_input_asof.isoformat(), static_freeze_at=static_asof.isoformat(),
                prestart_computation_completed_at=completed_asof.isoformat(), completion_before_cutoff=True)
        _immutable(final, encoded(result))
        if approved:
            try:
                saved_at = _prestart_clock(request, not_before=completed_asof)
                _immutable(folder / 'prestart_finalization_receipt.json', encoded({
                    'status': 'PRIVATE_PRESTART_SAVE_READBACK_VERIFIED',
                    'manifest_sha256': digest(final.read_bytes()),
                    'prediction_cutoff': request['prediction_cutoff'],
                    'save_readback_verified_at': saved_at.isoformat(),
                    'recipient_delivery_proven': False}))
                _prestart_clock(request, not_before=saved_at)
            except ResearchHold:
                _immutable(folder / 'prestart_finalization_failure.json', encoded({
                    'status': 'PRIVATE_PRESTART_FINALIZATION_FAILED_NOT_NO_BET',
                    'observed_at': _stamp(_actual_clock()).isoformat(),
                    'prediction_cutoff': request['prediction_cutoff'],
                    'prestart_delivery_proven': False}))
                raise
        return {**result, 'completion_reused': False,
                'new_engine_executions_this_call': int(krs['new_engine_execution'])}


def run_intent(path):
    """Resolve one explicitly selected private descriptor; never execute code from it."""
    path = Path(path).resolve()
    intent = json.loads(path.read_bytes())
    if intent.get('profile') != 'KM-FNB-PRIVATE-RESEARCH-INTENT-v1':
        raise ResearchHold('PRIVATE_RESEARCH_INTENT_PROFILE_REQUIRED')
    fields = {'source_path', 'source_sha256', 'request_path', 'request_sha256',
        'trust_path', 'trust_sha256', 'private_root', 'engine', 'params',
        'krs_cache', 'krs_cache_receipt_sha256', 'paper_policy',
        'owner_decision_path', 'owner_decision_sha256'}
    if set(intent) - fields - {'profile'}:
        raise ResearchHold('PRIVATE_RESEARCH_INTENT_UNKNOWN_FIELD')
    kwargs = {k: v for k, v in intent.items() if k != 'profile'}
    for key in ('source_path', 'request_path', 'trust_path', 'private_root', 'engine', 'params', 'krs_cache', 'owner_decision_path'):
        if kwargs.get(key) is not None:
            candidate = Path(kwargs[key])
            kwargs[key] = candidate if candidate.is_absolute() else path.parent / candidate
    required = {'source_path', 'source_sha256', 'request_path', 'request_sha256',
                'trust_path', 'trust_sha256', 'private_root'}
    if not required <= kwargs.keys():
        raise ResearchHold('PRIVATE_RESEARCH_INTENT_ASSETS_REQUIRED')
    return run(**kwargs)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'source-sha256', 'request', 'request-sha256', 'trust', 'trust-sha256', 'private-root'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--engine')
    parser.add_argument('--params')
    parser.add_argument('--owner-decision', help='Optional existing immutable dated private-use decision; no Production grant')
    parser.add_argument('--owner-decision-sha256', help='Exact SHA of that existing Owner decision original')
    parser.add_argument('--krs-cache-receipt-sha256', help='Exact SHA of the selected immutable original execution receipt.')
    parser.add_argument('--reuse-krs-cache', help='Verified prior execution directory; never rerun Engine for a cache hit.')
    parser.add_argument('--experimental-paper-pair-local-protection', action='store_true',
                        help='Explicit separate unadopted partial paper hypothesis; never clears original strict MEC HOLD.')
    parser.add_argument('--experimental-paper-policy', choices=('pair-local-known', 'unknown-path-protection'),
                        help='Explicit NEW unadopted research selection policy; original strict status stays separate.')
    args = parser.parse_args(argv)
    try:
        result = run(source_path=args.source, source_sha256=args.source_sha256,
            request_path=args.request, request_sha256=args.request_sha256,
            trust_path=args.trust, trust_sha256=args.trust_sha256, private_root=args.private_root,
            engine=args.engine, params=args.params, krs_cache=args.reuse_krs_cache,
            krs_cache_receipt_sha256=args.krs_cache_receipt_sha256,
            paper=args.experimental_paper_pair_local_protection, paper_policy=args.experimental_paper_policy,
            owner_decision_path=args.owner_decision, owner_decision_sha256=args.owner_decision_sha256)
    except (ValueError, OSError, KeyError) as error:
        # Do not expose Raw, credentials or callback exception text in logs.
        print(json.dumps({'profile': PROFILE, 'status': 'RESEARCH_EXECUTION_HOLD_NOT_NO_BET',
                          'exception_type': type(error).__name__,
                          'reason': str(error).partition(':')[0] if re.fullmatch('[A-Z][A-Z0-9_]{0,119}', str(error).partition(':')[0]) else 'RESEARCH_INPUT_OR_COMPONENT_UNVERIFIED',
                          'formal_final': False, 'actual_purchase': False}))
        return 2
    print(json.dumps({key: result[key] for key in ('profile', 'classification', 'race_id', 'index_cells',
        'completion_reused', 'new_engine_executions_this_call', 'output_directory',
        'formal_final', 'recipient_delivery_proven', 'registered_OOS_increment')}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

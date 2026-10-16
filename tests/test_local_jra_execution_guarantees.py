from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import subprocess

import pytest
from runtime.local_prestart_gate import validate_window, PrestartError
from runtime import formal_execution_orchestrator as o

ROOT = Path(__file__).resolve().parents[1]

def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'tools' / (name + '.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def request():
    return {'temporal_mode': 'FORMAL-PRE-RACE', 'prediction_cutoff': '2026-10-12T12:00:00+09:00',
            'scheduled_post_at': '2026-10-12T12:10:00+09:00'}


def now(hour, minute, second=0):
    return datetime.fromisoformat(f'2026-10-12T{hour:02}:{minute:02}:{second:02}+09:00')


def test_source_cutoff_and_formal_release_are_distinct():
    r = request()
    validate_window(r, phase='SOURCE', now=now(11, 59, 59))
    with pytest.raises(PrestartError, match='SOURCE_INCOMPLETE'):
        validate_window(r, phase='SOURCE', now=now(12, 0))
    validate_window(r, phase='FORMAL', now=now(12, 0))
    with pytest.raises(PrestartError, match='FORMAL_INCOMPLETE'):
        validate_window(r, now=now(12, 8))


@pytest.mark.parametrize('value', [0, -1, True, 'nan', 'inf', 'bad'])
def test_invalid_buffer_never_extends_prestart(value):
    r = {**request(), 'release_buffer_seconds': value}
    with pytest.raises(PrestartError, match='RELEASE_BUFFER_INVALID'):
        validate_window(r, now=now(11, 0))


@pytest.mark.parametrize('deadline', ['2026-10-12T12:10:00+09:00', '2026-10-12T12:11:00+09:00'])
def test_explicit_deadline_cannot_authorize_poststart(deadline):
    with pytest.raises(PrestartError, match='NOT_BEFORE_POST'):
        validate_window({**request(), 'release_deadline_at': deadline}, now=now(11, 0))


def test_timezone_and_cutoff_order_are_required():
    with pytest.raises(PrestartError, match='TZ_REQUIRED'):
        validate_window({**request(), 'scheduled_post_at': '2026-10-12T12:10:00'}, now=now(11, 0))
    with pytest.raises(PrestartError, match='CUTOFF_NOT_BEFORE_POST'):
        validate_window({**request(), 'prediction_cutoff': '2026-10-12T12:10:00+09:00'}, now=now(11, 0))


def test_replay_not_promoted_or_timeblocked():
    assert validate_window({'temporal_mode': 'POST-START-REPLAY'}) is None


def test_real_orchestrator_uses_source_gate_before_acquisition(monkeypatch, tmp_path):
    from tests.test_formal_execution_orchestrator import base_intent
    r = base_intent()
    r['static_prediction'] = {'ranking': ['1'], 'roles': {'1': ['W']}, 'status': 'FROZEN'}
    r['static_prediction_frozen'] = True
    monkeypatch.setattr(o, 'validate_request_context', lambda *a: None)
    monkeypatch.setattr(o, 'resume_plan', lambda *a: {'action': 'RUN_SOURCE_THEN_FORMAL', 'resume_from': 'SOURCE', 'checkpoints': {}})
    calls = []
    def gate(req, *, phase):
        calls.append(phase)
        raise o.PrestartError('DEADLINE_HOLD:SOURCE_INCOMPLETE')
    monkeypatch.setattr(o, 'validate_window', gate)
    monkeypatch.setattr(o, 'run_phase', lambda *a, **k: pytest.fail('expired SOURCE must not run'))
    out = o.orchestrate(r, run_id='test', github_sha='test', runtime_out=tmp_path/'out', tmp_root=tmp_path/'tmp')
    assert calls == ['SOURCE']
    assert out['status'] == 'DEADLINE_HOLD'
    assert out['first_failed_phase'] == 'SOURCE'


def put_intent(root, venue, race):
    eid = f'KM-LOCAL-{venue}-20261012-R{race:02}-LIVE-R1'
    path = root / 'runtime/formal_intents' / (eid + '.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({'family_id': 'LOCAL', 'execution_id': eid, 'race_id': eid}))
    return str(path.relative_to(root))


def test_batch_keeps_every_race_and_rejects_traversal(tmp_path):
    m = module('local_intent_matrix')
    paths = [put_intent(tmp_path, 'OHI', i) for i in range(1, 13)]
    rows = m.resolve(paths + paths, root=tmp_path)['include']
    assert len(rows) == 12
    assert len({r['execution_id'] for r in rows}) == 12
    with pytest.raises(ValueError, match='PATH_INVALID'):
        m.resolve(['runtime/formal_intents/../../profiles/authority.json'], root=tmp_path)


def run(cwd, *args):
    p = subprocess.run(['git', *args], cwd=cwd, capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    return p.stdout


def fixture_repos(tmp_path):
    remote = tmp_path/'remote.git'; remote.mkdir()
    run(remote, 'init', '--bare')
    seed = tmp_path/'seed'; run(tmp_path, 'clone', str(remote), str(seed))
    for config in [('user.name','test'), ('user.email','test@example.invalid')]:
        run(seed,'config',*config)
    run(seed,'checkout','-b','main')
    path = seed/'runtime/aki_adaptive_oos_status.json'; path.parent.mkdir(parents=True)
    path.write_text('{"n":0}\n')
    (seed/'receipt.json').write_text('original\n')
    run(seed,'add','.'); run(seed,'commit','-m','seed'); run(seed,'push','-u','origin','main')
    worker = tmp_path/'worker'; run(tmp_path,'clone','--branch','main',str(remote),str(worker))
    run(worker,'config','user.name','test'); run(worker,'config','user.email','test@example.invalid')
    return seed, worker


def test_real_rebase_merges_race_records_rebuilds_view_preserves_scratch(tmp_path):
    m = module('persist_local_checkpoints'); seed, worker = fixture_repos(tmp_path)
    for repo, n in [(seed,1),(worker,2)]:
        (repo/f'race{n}.json').write_text(str(n))
        (repo/'runtime/aki_adaptive_oos_status.json').write_text(json.dumps({'n':n}))
        run(repo,'add','.'); run(repo,'commit','-m',f'race{n}')
    run(seed,'push','origin','main')
    (worker/'scratch.json').write_text('scratch')
    def refresh(paths):
        assert paths == {'runtime/aki_adaptive_oos_status.json'}
        assert (worker/'race1.json').exists() and (worker/'race2.json').exists()
        (worker/'runtime/aki_adaptive_oos_status.json').write_text('{"n":3}')
    m.persist(cwd=worker,branch='main',refresh=refresh,attempts=1)
    assert (worker/'scratch.json').read_text() == 'scratch'
    run(seed,'pull','--ff-only')
    assert (seed/'race2.json').exists()
    assert json.loads((seed/'runtime/aki_adaptive_oos_status.json').read_text()) == {'n':3}


def test_real_receipt_conflict_holds_without_overwrite(tmp_path):
    m = module('persist_local_checkpoints'); seed, worker = fixture_repos(tmp_path)
    for repo, text in [(seed,'remote receipt'),(worker,'local receipt')]:
        (repo/'receipt.json').write_text(text)
        run(repo,'add','.'); run(repo,'commit','-m','receipt')
    run(seed,'push','origin','main')
    with pytest.raises(RuntimeError,match='IMMUTABLE_OR_UNKNOWN_CONFLICT'):
        m.persist(cwd=worker,branch='main',refresh=lambda paths: pytest.fail('must hold'),attempts=1)
    assert (seed/'receipt.json').read_text() == 'remote receipt'
    assert (worker/'receipt.json').read_text() == 'local receipt'


def test_workflow_batch_is_bounded_and_independent():
    import yaml
    workflow = yaml.safe_load((ROOT/'.github/workflows/km-formal-single-entry.yml').read_text())
    job = workflow['jobs']['orchestrate']
    assert job['strategy']['fail-fast'] is False
    assert job['strategy']['max-parallel'] == 4
    assert 'matrix.execution_id' in job['concurrency']['group']
    assert 'persist_local_checkpoints.py' in str(job['steps'])
    assert 'result-wait-seconds' not in str(job['steps'])
    continuation = workflow['jobs']['result']
    assert 'result-wait-seconds' in str(continuation['steps'])
    assert 'always()' in continuation['if']
    assert 'orchestrate' in continuation['needs']


def test_historical_canonical_execution_id_is_preserved(tmp_path):
    m = module('local_intent_matrix')
    path = put_intent(tmp_path, 'OHI', 1)
    p = tmp_path/path
    req = json.loads(p.read_text())
    req['execution_id'] = 'LOCAL-' + req['race_id'] + '-EXEC'
    p.write_text(json.dumps(req))
    assert m.resolve([path], root=tmp_path)['include'][0]['execution_id'] == req['execution_id']
    req['execution_id'] = 'KM-LOCAL-OHI-20261012-R99-LIVE-R1'
    p.write_text(json.dumps(req))
    with pytest.raises(ValueError, match='IDENTITY_CONFLICT'):
        m.resolve([path], root=tmp_path)


def test_rebuild_actual_tracker_views_in_isolated_output_store(tmp_path, monkeypatch):
    m = module('persist_local_checkpoints')
    monkeypatch.chdir(tmp_path)
    (tmp_path/'runtime').mkdir()
    (tmp_path/'research').symlink_to(ROOT/'research', target_is_directory=True)
    # These are research views, never acceptance evidence for a real race.
    m.rebuild(m.SNAPSHOTS)
    for path in m.SNAPSHOTS:
        assert isinstance(json.loads((tmp_path/path).read_text()), dict)

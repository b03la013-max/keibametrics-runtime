"""Queued reference jobs resume an earlier run's published forecast verbatim."""
from datetime import datetime
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))

from runtime import local_reference_day as reference
from tools import persist_local_checkpoints as store
from urw_reference_fixture_support import fixture_root


def git(cwd, *args):
    return subprocess.check_output(['git', *args], cwd=cwd, text=True).strip()


def commit(cwd, message):
    git(cwd, 'add', '.')
    git(cwd, 'commit', '-qm', message)
    return git(cwd, 'rev-parse', 'HEAD')


def queued_checkouts(tmp_path):
    remote = tmp_path / 'remote.git'
    first = tmp_path / 'first'
    queued = tmp_path / 'queued'
    git(tmp_path, 'init', '--bare', '--initial-branch=main', str(remote))
    first.mkdir()
    git(first, 'init', '--initial-branch=main')
    git(first, 'config', 'user.name', 'Reference Test')
    git(first, 'config', 'user.email', 'reference-test@example.invalid')
    (first / 'authority.txt').write_text('PRODUCTION-FROZEN\n')
    before = commit(first, 'existing frozen authority')
    request = first / 'runtime/local_reference_start_requests/2026-10-20.json'
    request.parent.mkdir(parents=True)
    request.write_text('{"reference_only":true}\n')
    event_sha = commit(first, 'dated reference-only request')
    git(first, 'remote', 'add', 'origin', str(remote))
    git(first, 'push', '-q', 'origin', 'HEAD:main')
    git(tmp_path, 'clone', '-q', str(remote), str(queued))
    git(queued, 'checkout', '-q', '--detach', event_sha)
    return remote, first, queued, before, event_sha


def test_queued_worker_reads_preceding_publication_without_regeneration(tmp_path):
    remote, first, queued, before, event_sha = queued_checkouts(tmp_path)
    relative = Path('runtime/local_reference/2026-10-20/R01')
    assert not (queued / relative).exists()
    shutil.copytree(fixture_root() / relative, first / relative,
                    ignore=shutil.ignore_patterns('worker.lock'))
    published_sha = commit(first, 'first worker frozen reference')
    # Exercise the same existing normal-FF persistence used by Actions.
    store.persist(cwd=first, branch='main', attempts=1, refresh=lambda _: None)
    originals = {p.relative_to(first): p.read_bytes()
                 for p in (first / relative).rglob('*') if p.is_file()}
    receipt = store.sync_before_generation(cwd=queued, branch='main', event_sha=event_sha)
    assert receipt == {'event_sha': event_sha, 'generation_base_sha': published_sha,
                       'fast_forwarded': True, 'remote_write_count': 0}
    # Advancing the worktree must not replace the original push event range.
    assert git(queued, 'diff', '--name-only', before, event_sha) == (
        'runtime/local_reference_start_requests/2026-10-20.json')
    store.verify_event_files(cwd=queued, event_sha=event_sha,
                             paths=['runtime/local_reference_start_requests/2026-10-20.json'])

    def forbidden(*args, **kwargs):
        pytest.fail('queued run must not fetch, rank, re-freeze or POST this race')

    pub, body = reference.one_race(queued / relative, '2026-10-20', 1,
                                 generate=forbidden,
                                 clock=lambda: datetime.fromisoformat('2026-10-20T20:00:00+09:00'))
    assert pub['reference_runner_count'] == 11 and '最終結論' in body
    assert all((queued / path).read_bytes() == raw for path, raw in originals.items())
    assert (queued / 'authority.txt').read_text() == 'PRODUCTION-FROZEN\n'
    assert git(queued, 'diff', '--name-only') == ''
    assert git(remote, 'rev-parse', 'refs/heads/main') == published_sha


@pytest.mark.parametrize('dirty_path', ['authority.txt', 'runtime/local_reference/new.json'])
def test_generation_sync_holds_dirty_checkout_without_overwriting(tmp_path, dirty_path):
    remote, first, queued, _, event_sha = queued_checkouts(tmp_path)
    target = queued / dirty_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b'local bytes must survive\n')
    (first / 'upstream.txt').write_text('new main\n')
    advanced = commit(first, 'later main')
    git(first, 'push', '-q', 'origin', 'HEAD:main')
    with pytest.raises(RuntimeError, match='DIRTY_CHECKOUT_HOLD'):
        store.sync_before_generation(cwd=queued, branch='main', event_sha=event_sha)
    assert target.read_bytes() == b'local bytes must survive\n'
    assert git(queued, 'rev-parse', 'HEAD') == event_sha
    assert not (queued / 'upstream.txt').exists()
    assert git(remote, 'rev-parse', 'refs/heads/main') == advanced


def test_generation_sync_rejects_divergent_main_without_reset_or_merge(tmp_path):
    remote, first, queued, before, event_sha = queued_checkouts(tmp_path)
    # Simulate a remote history replacement after the queued event. The helper
    # must reject it; it has no force/reset/rebase or conflict-resolution path.
    git(first, 'checkout', '-q', '-b', 'replacement', before)
    (first / 'authority.txt').write_text('different remote authority\n')
    replacement = commit(first, 'replacement history')
    git(first, 'push', '-q', '--force', 'origin', 'HEAD:main')
    with pytest.raises(RuntimeError, match='NOT_FAST_FORWARD_HOLD'):
        store.sync_before_generation(cwd=queued, branch='main', event_sha=event_sha)
    assert git(queued, 'rev-parse', 'HEAD') == event_sha
    assert (queued / 'authority.txt').read_text() == 'PRODUCTION-FROZEN\n'
    assert git(remote, 'rev-parse', 'refs/heads/main') == replacement


def test_only_reference_job_syncs_and_immutable_event_selection_is_preserved():
    workflow = (ROOT / '.github/workflows/km-local-race-key-entry.yml').read_text()
    reference_job = workflow.split('  reference-day:', 1)[1].split('  resolve:', 1)[0]
    assert reference_job.index('--sync-before-generation') < reference_job.index(
        'Complete or resume every frozen URW reference')
    assert '--event-sha "$GITHUB_SHA"' in reference_job
    assert "before,after=event.get('before',''),event.get('after','')" in reference_job
    assert "['git','diff','--name-only','--diff-filter=AMR',before,after]" in reference_job
    assert 'verify_event_files(cwd=Path.cwd(),event_sha=after,paths=requests)' in reference_job
    assert workflow.count('--sync-before-generation') == 1
    assert 'formal_execution_orchestrator' not in reference_job


@pytest.mark.parametrize('updated', [True, False])
def test_later_same_path_request_update_or_delete_is_held(tmp_path, updated):
    _, first, queued, _, event_sha = queued_checkouts(tmp_path)
    path = 'runtime/local_reference_start_requests/2026-10-20.json'
    if updated:
        (first / path).write_text('{"reference_only":true,"changed":true}\n')
    else:
        (first / path).unlink()
    commit(first, 'later request amendment')
    git(first, 'push', '-q', 'origin', 'HEAD:main')
    store.sync_before_generation(cwd=queued, branch='main', event_sha=event_sha)
    with pytest.raises(RuntimeError, match='REQUEST_CHANGED_AFTER_EVENT'):
        store.verify_event_files(cwd=queued, event_sha=event_sha, paths=[path])

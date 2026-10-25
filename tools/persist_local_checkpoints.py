"""Rebase race records strictly; rebuild disposable aggregate views on conflict.

Run after committing only the workflow's approved paths. Never select a side for
conflicting receipts, per-race measurements, authority, or configuration.
"""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOTS = {
    'runtime/local_candidate_forward_status.json',
    'runtime/local_candidate_dual_oos_status.json',
    'runtime/local_candidate_v03_oos_status.json',
    'runtime/mec_r4_oos_status.json',
    'runtime/local_mec_r5_oos_status.json',
    'runtime/aki_adaptive_oos_status.json',
    'runtime/common_exact_continuity_oos_status.json',
}
JRA_RESULT_SNAPSHOTS = {
    'runtime/krs_oos_status.json',
    'runtime/source_candidate_oos_status.json',
    'runtime/role_rescue_shadow_status.json',
    'runtime/pfs_grand_review/current.json',
    'runtime/family_prediction_utility/current.json',
}


def git(*args, cwd):
    return subprocess.run(['git', *args], cwd=cwd, text=True, capture_output=True,
                          env={**os.environ, 'GIT_EDITOR': 'true'})


def sync_before_generation(*, cwd, branch, event_sha):
    """Read earlier workers' durable records before producing any new ones.

    A queued Actions checkout is pinned to the event SHA. Only fast-forward it
    to the fetched branch; never rebase unpublished forecasts, reset local
    files, or resolve an immutable-record conflict. The caller must keep the
    original event before/after SHAs for ingress selection.
    """
    if (not re.fullmatch(r'[0-9a-f]{40}', event_sha or '') or not branch
            or branch.startswith('-')
            or git('check-ref-format', 'refs/heads/' + branch, cwd=cwd).returncode):
        raise RuntimeError('REFERENCE_SYNC_EVENT_OR_BRANCH_INVALID')
    head = git('rev-parse', 'HEAD', cwd=cwd)
    if head.returncode or head.stdout.strip() != event_sha:
        raise RuntimeError('REFERENCE_SYNC_EVENT_CHECKOUT_MISMATCH')
    status = git('status', '--porcelain', '--untracked-files=all', cwd=cwd)
    if status.returncode or status.stdout.strip():
        raise RuntimeError('REFERENCE_SYNC_DIRTY_CHECKOUT_HOLD')
    if git('fetch', '--no-tags', 'origin', 'refs/heads/' + branch, cwd=cwd).returncode:
        raise RuntimeError('REFERENCE_SYNC_FETCH_FAILED')
    fetched = git('rev-parse', 'FETCH_HEAD', cwd=cwd)
    if fetched.returncode:
        raise RuntimeError('REFERENCE_SYNC_FETCHED_HEAD_INVALID')
    current = fetched.stdout.strip()
    if git('merge-base', '--is-ancestor', event_sha, current, cwd=cwd).returncode:
        raise RuntimeError('REFERENCE_SYNC_NOT_FAST_FORWARD_HOLD')
    if git('merge', '--ff-only', '--no-edit', current, cwd=cwd).returncode:
        raise RuntimeError('REFERENCE_SYNC_FAST_FORWARD_FAILED')
    if git('rev-parse', 'HEAD', cwd=cwd).stdout.strip() != current:
        raise RuntimeError('REFERENCE_SYNC_HEAD_MISMATCH')
    return {'event_sha': event_sha, 'generation_base_sha': current,
            'fast_forwarded': current != event_sha, 'remote_write_count': 0}


def verify_event_files(*, cwd, event_sha, paths):
    """Do not consume a newer request body for an older queued push event."""
    if not re.fullmatch(r'[0-9a-f]{40}', event_sha or ''):
        raise RuntimeError('REFERENCE_PUSH_EVENT_SHA_INVALID')
    for name in paths:
        path = Path(name)
        if path.is_absolute() or '..' in path.parts:
            raise RuntimeError('REFERENCE_PUSH_EVENT_PATH_INVALID')
        original = subprocess.run(['git', 'show', event_sha + ':' + name], cwd=cwd,
                                  capture_output=True)
        current = Path(cwd) / path
        if (original.returncode or not current.is_file() or current.is_symlink()
                or not current.resolve().is_relative_to(Path(cwd).resolve())
                or current.read_bytes() != original.stdout):
            raise RuntimeError('REFERENCE_PUSH_REQUEST_CHANGED_AFTER_EVENT:' + name)


def rebuild(paths):
    sys.path.insert(0, str(ROOT / 'runtime'))
    # The utility snapshot consumes the other merged views, so it is last.
    for path in sorted(paths, key=lambda p: (p == 'runtime/family_prediction_utility/current.json', p)):
        if path == 'runtime/krs_oos_status.json':
            from krs_oos_promotion_gate import evaluate_r30
            obj = evaluate_r30([json.loads(p.read_text()) for p in
                               sorted(Path('runtime/krs_oos_measurements').glob('*.json'))])
        elif path == 'runtime/source_candidate_oos_status.json':
            from jra_source_candidate_promotion_gate import evaluate
            obj = evaluate([json.loads(p.read_text()) for p in
                            sorted(Path('runtime/source_candidate_oos').glob('*/result_evaluation.json'))])
        elif path == 'runtime/role_rescue_shadow_status.json':
            from jra_role_learning_shadow import write_status
            write_status(path)
            continue
        elif path == 'runtime/pfs_grand_review/current.json':
            from pfs_grand_review import write_report
            write_report(path)
            continue
        elif path == 'runtime/family_prediction_utility/current.json':
            from family_prediction_utility import write_snapshot
            write_snapshot(path)
            continue
        elif path == 'runtime/local_candidate_forward_status.json':
            from local_candidate_postresult import forward_status
            obj = forward_status()
        elif path == 'runtime/aki_adaptive_oos_status.json':
            from aki_adaptive_oos_tracker import scan_execution_store
            obj = scan_execution_store(Path('runtime/executions'))
        elif path.endswith('local_candidate_dual_oos_status.json'):
            from local_candidate_dual_oos_tracker import write_status
            write_status('runtime/local_candidate_dual_oos_measurements', path)
            continue
        elif path.endswith('local_candidate_v03_oos_status.json'):
            from local_candidate_v03_oos_tracker import write_status
            write_status('runtime/local_candidate_v03_oos_measurements', path)
            continue
        else:
            import importlib
            name = Path(path).stem.replace('_status', '_tracker')
            importlib.import_module(name).write_status(path)
            continue
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + '\n')


def persist(*, cwd, branch, refresh=rebuild, attempts=5, snapshots=SNAPSHOTS):
    # Noncommitted runtime scratch must not obstruct the durable record commit.
    dirty = git('status', '--porcelain', cwd=cwd).stdout.strip()
    stashed = bool(dirty)
    if stashed and git('stash', 'push', '--include-untracked', '-m', 'km-local-persist-scratch', cwd=cwd).returncode:
        raise RuntimeError('PERSIST_SCRATCH_STASH_FAILED')
    touched = set(git('diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD', cwd=cwd).stdout.splitlines()) & snapshots
    pushed = False
    try:
        for attempt in range(attempts):
            if git('fetch', 'origin', branch, cwd=cwd).returncode:
                raise RuntimeError('PERSIST_FETCH_FAILED')
            result = git('rebase', 'FETCH_HEAD', cwd=cwd)
            while result.returncode:
                conflicts = set(git('diff', '--name-only', '--diff-filter=U', cwd=cwd).stdout.splitlines())
                if not conflicts or not conflicts <= snapshots:
                    git('rebase', '--abort', cwd=cwd)
                    raise RuntimeError('PERSIST_IMMUTABLE_OR_UNKNOWN_CONFLICT')
                touched |= conflicts
                # Upstream view is only temporary; every touched view is rebuilt
                # from the merged race records before any push.
                for path in sorted(conflicts):
                    if git('checkout', '--ours', '--', path, cwd=cwd).returncode:
                        raise RuntimeError('PERSIST_VIEW_RESOLUTION_FAILED')
                    git('add', '--', path, cwd=cwd)
                result = git('rebase', '--continue', cwd=cwd)
            refresh(touched)
            if touched:
                if git('add', '--', *sorted(touched), cwd=cwd).returncode:
                    raise RuntimeError('PERSIST_VIEW_STAGE_FAILED')
                if git('diff', '--cached', '--quiet', cwd=cwd).returncode:
                    if git('commit', '-m', 'measurement: rebuild merged measurement views [skip ci]', cwd=cwd).returncode:
                        raise RuntimeError('PERSIST_VIEW_COMMIT_FAILED')
            if git('push', 'origin', 'HEAD:' + branch, cwd=cwd).returncode == 0:
                pushed = True
                return
            time.sleep(min(2 * (attempt + 1), 10))
        raise RuntimeError('PERSIST_PUSH_RETRY_EXHAUSTED')
    finally:
        # Always retain pending records in commits/stash; fail visibly if scratch
        # restoration conflicts. Never force push or drop a conflicting stash.
        if stashed:
            restore = git('stash', 'pop', cwd=cwd)
            if restore.returncode:
                # Once the verified RESULT commit is durably pushed, local
                # scratch cannot retroactively invalidate that receipt. Git
                # retains a conflicting stash for inspection; state the hold
                # explicitly instead of reporting a false failed lifecycle.
                if pushed:
                    print('PERSIST_SCRATCH_RESTORE_WARNING_STASH_PRESERVED:'
                          'SIGNED_RECORDS_ALREADY_PUSHED',
                          file=sys.stderr)
                else:
                    raise RuntimeError('PERSIST_SCRATCH_RESTORE_HOLD_STASH_PRESERVED')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--branch', required=True)
    parser.add_argument('--jra-result', action='store_true')
    parser.add_argument('--sync-before-generation', action='store_true')
    parser.add_argument('--event-sha')
    args = parser.parse_args()
    if args.sync_before_generation:
        if args.jra_result or not args.event_sha:
            parser.error('--sync-before-generation requires --event-sha and excludes --jra-result')
        print(json.dumps(sync_before_generation(cwd=Path.cwd(), branch=args.branch,
                                               event_sha=args.event_sha), sort_keys=True))
    else:
        if args.event_sha:
            parser.error('--event-sha requires --sync-before-generation')
        persist(cwd=Path.cwd(), branch=args.branch,
                snapshots=SNAPSHOTS | JRA_RESULT_SNAPSHOTS if args.jra_result else SNAPSHOTS)

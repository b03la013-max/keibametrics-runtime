"""Rebase LOCAL race records strictly; rebuild disposable aggregate views on conflict.

Run after committing only the workflow's approved paths. Never select a side for
conflicting receipts, per-race measurements, authority, or configuration.
"""
import argparse
import json
import os
from pathlib import Path
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


def git(*args, cwd):
    return subprocess.run(['git', *args], cwd=cwd, text=True, capture_output=True,
                          env={**os.environ, 'GIT_EDITOR': 'true'})


def rebuild(paths):
    sys.path.insert(0, str(ROOT / 'runtime'))
    for path in sorted(paths):
        if path == 'runtime/local_candidate_forward_status.json':
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
        Path(path).write_text(json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + '\n')


def persist(*, cwd, branch, refresh=rebuild, attempts=5):
    # Noncommitted runtime scratch must not obstruct the durable record commit.
    dirty = git('status', '--porcelain', cwd=cwd).stdout.strip()
    stashed = bool(dirty)
    if stashed and git('stash', 'push', '--include-untracked', '-m', 'km-local-persist-scratch', cwd=cwd).returncode:
        raise RuntimeError('PERSIST_SCRATCH_STASH_FAILED')
    touched = set(git('diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD', cwd=cwd).stdout.splitlines()) & SNAPSHOTS
    pushed = False
    try:
        for attempt in range(attempts):
            if git('fetch', 'origin', branch, cwd=cwd).returncode:
                raise RuntimeError('PERSIST_FETCH_FAILED')
            result = git('rebase', 'FETCH_HEAD', cwd=cwd)
            while result.returncode:
                conflicts = set(git('diff', '--name-only', '--diff-filter=U', cwd=cwd).stdout.splitlines())
                if not conflicts or not conflicts <= SNAPSHOTS:
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
                    if git('commit', '-m', 'measurement: rebuild merged LOCAL views [skip ci]', cwd=cwd).returncode:
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
    args = parser.parse_args()
    persist(cwd=Path.cwd(), branch=args.branch)

"""Process contention and interruption tests for the actual checkpoint writer."""
import fcntl
import json
import multiprocessing
import os
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
import jra_krs_request_checkpoint as checkpoint
from jra_production_krs_contract import JRAProductionKRSContractError


def payload(marker=1):
    return {'race_id': 'KM-JRA-TKY-20261018-R01', 'input_data': {'marker': marker}}


def worker(directory, marker, barrier, queue):
    barrier.wait(timeout=5)
    try:
        body, record = checkpoint.checkpoint_krs_request(payload(marker), directory)
        queue.put(('OK', body, record))
    except JRAProductionKRSContractError as exc:
        queue.put(('CONFLICT', str(exc)))


@pytest.mark.parametrize('markers', [(1, 2), (1, 1)])
def test_independent_processes_cannot_publish_different_immutable_requests(tmp_path, markers):
    ctx = multiprocessing.get_context('fork')
    barrier, queue = ctx.Barrier(2), ctx.Queue()
    processes = [ctx.Process(target=worker, args=(str(tmp_path), n, barrier, queue)) for n in markers]
    for process in processes: process.start()
    results = [queue.get(timeout=10) for _ in processes]
    for process in processes:
        process.join(timeout=5)
        assert process.exitcode == 0
    successes = [r for r in results if r[0] == 'OK']
    assert len(successes) == (1 if markers[0] != markers[1] else 2)
    wire = (tmp_path / 'krs_request_wire.json').read_bytes()
    record = json.loads((tmp_path / 'krs_request_hashes.json').read_text())
    assert all(r[1] == wire and r[2] == record for r in successes)


def test_interrupted_pair_resumes_only_with_identical_bytes(tmp_path, monkeypatch):
    original = checkpoint._publish
    def interrupt(path, raw):
        if path.name == 'krs_request_hashes.json': raise OSError('simulated interruption')
        return original(path, raw)
    with monkeypatch.context() as patch:
        patch.setattr(checkpoint, '_publish', interrupt)
        with pytest.raises(OSError, match='interruption'):
            checkpoint.checkpoint_krs_request(payload(), tmp_path)
    wire = (tmp_path / 'krs_request_wire.json').read_bytes()
    assert not (tmp_path / 'krs_request_hashes.json').exists()
    with pytest.raises(JRAProductionKRSContractError, match='CONFLICT'):
        checkpoint.checkpoint_krs_request(payload(2), tmp_path)
    assert not (tmp_path / 'krs_request_hashes.json').exists()
    body, _ = checkpoint.checkpoint_krs_request(payload(), tmp_path)
    assert body == wire


def test_pair_conflict_never_overwrites_and_other_race_is_independent(tmp_path):
    root = tmp_path / 'first'
    checkpoint.checkpoint_krs_request(payload(), root)
    record = root / 'krs_request_hashes.json'
    record.write_bytes(b'corrupt')
    with pytest.raises(JRAProductionKRSContractError, match='CONFLICT'):
        checkpoint.checkpoint_krs_request(payload(), root)
    assert record.read_bytes() == b'corrupt'
    assert checkpoint.checkpoint_krs_request(payload(2), tmp_path / 'second')[0]


def test_lock_wait_is_bounded_and_does_not_block_another_race(tmp_path):
    root = tmp_path / 'busy'; root.mkdir()
    fd = os.open(root / '.krs-request.lock', os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        with pytest.raises(JRAProductionKRSContractError, match='LOCK_TIMEOUT'):
            checkpoint.checkpoint_krs_request(payload(), root, lock_timeout=.02)
        assert not (root / 'krs_request_wire.json').exists()
        assert checkpoint.checkpoint_krs_request(payload(), tmp_path / 'other')[0]
    finally:
        os.close(fd)


def test_existing_symlink_cannot_redirect_checkpoint(tmp_path):
    target = tmp_path / 'outside'; target.write_bytes(b'preserve')
    root = tmp_path / 'race'; root.mkdir()
    (root / 'krs_request_wire.json').symlink_to(target)
    with pytest.raises(JRAProductionKRSContractError, match='SYMLINK'):
        checkpoint.checkpoint_krs_request(payload(), root)
    assert target.read_bytes() == b'preserve'

"""Durable, race-local publication of the existing two-file KRS checkpoint.

The preregistered serializer/record format remains frozen. A bounded advisory
lock serializes cooperating writers, and fsynced temporary files are published
with atomic no-replace links. A crash between publications is resumable only
when every existing byte agrees with the requested immutable checkpoint.
"""
import fcntl
import os
from pathlib import Path
import tempfile
import time

from jra_production_krs_contract import (
    checkpoint_krs_request as _frozen_checkpoint,
    JRAProductionKRSContractError,
)


def _existing(path, expected):
    if path.is_symlink():
        raise JRAProductionKRSContractError('KRS_REQUEST_CHECKPOINT_SYMLINK_FORBIDDEN')
    if path.exists() and path.read_bytes() != expected:
        raise JRAProductionKRSContractError('KRS_REQUEST_CHECKPOINT_CONFLICT:' + path.name)


def _publish(path, raw):
    fd, name = tempfile.mkstemp(prefix='.krs-publish-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(name, path)  # atomic; never replaces an existing checkpoint
        except FileExistsError:
            _existing(path, raw)
    finally:
        os.unlink(name)


def checkpoint_krs_request(payload, directory, *, lock_timeout=1.0):
    root = Path(directory)
    if root.is_symlink():
        raise JRAProductionKRSContractError('KRS_REQUEST_CHECKPOINT_SYMLINK_FORBIDDEN')
    root.mkdir(parents=True, exist_ok=True)
    fd = os.open(root / '.krs-request.lock', os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        deadline = time.monotonic() + lock_timeout
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise JRAProductionKRSContractError('KRS_REQUEST_CHECKPOINT_LOCK_TIMEOUT')
                time.sleep(min(.01, max(0, deadline - time.monotonic())))
        with tempfile.TemporaryDirectory(prefix='.krs-staging-', dir=root) as staging:
            body, record = _frozen_checkpoint(payload, staging)
            files = [(root / name, (Path(staging) / name).read_bytes())
                     for name in ('krs_request_wire.json', 'krs_request_hashes.json')]
            # Check the complete pair before publishing either missing file.
            for path, raw in files:
                _existing(path, raw)
            for path, raw in files:
                _publish(path, raw)
            directory_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
            return body, record
    finally:
        os.close(fd)  # releases the lock even on interruption/error

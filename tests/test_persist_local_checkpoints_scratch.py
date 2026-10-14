"""Signed durable RESULT must not be misclassified as failed after git push."""
from pathlib import Path
from types import SimpleNamespace

import pytest

from tools import persist_local_checkpoints as persist


def _mock_git(*, allow_push: bool):
    called = []

    def call(*args, cwd):
        called.append(tuple(args))
        name = args[0]
        if name == "status":
            return SimpleNamespace(returncode=0, stdout="?? runtime_out/diagnostic.txt\n")
        if name == "diff-tree":
            return SimpleNamespace(returncode=0, stdout="")
        if name == "stash" and args[1] == "push":
            return SimpleNamespace(returncode=0, stdout="")
        if name == "stash" and args[1] == "pop":
            return SimpleNamespace(returncode=1, stdout="", stderr="CONFLICT scratch")
        if name == "push":
            return SimpleNamespace(returncode=0 if allow_push else 1, stdout="")
        return SimpleNamespace(returncode=0, stdout="")
    return call, called


def test_signed_push_survives_post_push_scratch_restore_conflict(monkeypatch, tmp_path, capsys):
    mock, called = _mock_git(allow_push=True)
    monkeypatch.setattr(persist, "git", mock)
    persist.persist(cwd=tmp_path, branch="main", attempts=1, refresh=lambda _: None)
    err = capsys.readouterr().err
    assert "PERSIST_SCRATCH_RESTORE_WARNING_STASH_PRESERVED" in err
    assert ("push", "origin", "HEAD:main") in called
    assert ("stash", "pop") in called


def test_no_successful_push_still_fails_closed(monkeypatch, tmp_path):
    mock, called = _mock_git(allow_push=False)
    monkeypatch.setattr(persist, "git", mock)
    monkeypatch.setattr(persist.time, "sleep", lambda _: None)
    with pytest.raises(RuntimeError, match="PERSIST_SCRATCH_RESTORE_HOLD_STASH_PRESERVED"):
        persist.persist(cwd=tmp_path, branch="main", attempts=1, refresh=lambda _: None)
    assert ("push", "origin", "HEAD:main") in called

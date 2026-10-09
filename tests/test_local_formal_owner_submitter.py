from __future__ import annotations

from datetime import datetime, timezone
import base64
import json
from pathlib import Path
from types import SimpleNamespace
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from submit_local_formal_intent import submit, EntryError

NOW = datetime(2026, 10, 9, 5, 0, tzinfo=timezone.utc)
ID = "KM-LOCAL-OHI-20261009-R01-LIVE-R1"


def intent():
    numbers = ["1", "2"]
    return {
        "family_id": "LOCAL", "execution_phase": "AUTO", "temporal_mode": "FORMAL-PRE-RACE",
        "execution_id": ID, "race_id": ID, "venue_id": "OHI", "race_date": "2026-10-09", "race_no": 1,
        "race": {"race_id": ID, "venue_id": "OHI", "race_date": "2026-10-09", "race_no": 1},
        "prediction_cutoff": "2026-10-09T15:00:00+09:00", "scheduled_post_at": "2026-10-09T15:35:00+09:00",
        "runners": [{"runner_id": n, "horse_no": int(n), "name": f"Test{n}"} for n in numbers],
        "required_indices": [f"INDEX_{n}" for n in range(29)],
        "static_prediction_frozen": True,
        "static_prediction": {"ranking": numbers, "roles": {n: ["W", "P2", "P3"] for n in numbers}},
        "pair_dispositions": [], "third_dispositions": [], "run_count": 5000,
        "current_authority_manifest": "KM-FAMILY-CURRENT-AUTHORITY-20261008-R44",
        "venue_canon": "OHI-PRODUCTION",
    }


def test_dry_run_has_no_network():
    def fail(*a, **kw):
        raise AssertionError("unexpected external call")
    output = submit(intent(), repo="owner/repo", dry_run=True, now=NOW, executor=fail)
    assert output["status"] == "DRY_RUN_ONLY"


def test_expired_formal_is_rejected():
    with pytest.raises(EntryError, match="FORMAL_CUTOFF_ALREADY_PASSED"):
        submit(intent(), repo="owner/repo", dry_run=True,
               now=datetime(2026, 10, 9, 7, 0, tzinfo=timezone.utc))


def test_runner_mismatch_is_rejected():
    data = intent()
    data["runners"][1]["horse_no"] = 99
    with pytest.raises(EntryError, match="RUNNER_NUMBER_MISMATCH"):
        submit(data, repo="owner/repo", dry_run=True, now=NOW)


def test_idempotent_same_intent_requires_no_write():
    data = intent()
    content = base64.b64encode(json.dumps(data).encode()).decode()
    calls = []
    def fake(cmd, **kw):
        calls.append(cmd)
        return SimpleNamespace(returncode=0, stdout=json.dumps({"content": content}), stderr="")
    out = submit(data, repo="owner/repo", now=NOW, executor=fake)
    assert out["status"] == "ALREADY_SUBMITTED_IDENTICAL"
    assert len(calls) == 1


def test_same_id_with_changed_semantics_conflicts():
    old, new = intent(), intent()
    new["run_count"] = 20000
    content = base64.b64encode(json.dumps(new).encode()).decode()
    def fake(cmd, **kw):
        return SimpleNamespace(returncode=0, stdout=json.dumps({"content": content}), stderr="")
    with pytest.raises(EntryError, match="IMMUTABLE_INTENT_CONFLICT"):
        submit(old, repo="owner/repo", now=NOW, executor=fake)


def test_submits_only_one_official_canonical_path():
    calls = []
    def fake(cmd, **kw):
        calls.append((cmd, kw.get("input")))
        if len(calls) == 1:
            return SimpleNamespace(returncode=1, stdout="", stderr="HTTP 404 Not Found")
        return SimpleNamespace(returncode=0, stdout=json.dumps({
            "commit": {"sha": "abc123"}, "content": {"html_url": "https://github.com/example"}}), stderr="")
    out = submit(intent(), repo="owner/repo", now=NOW, executor=fake)
    assert out["status"] == "SUBMITTED_PUSH_TRIGGER_PENDING"
    assert len(calls) == 2
    assert calls[1][0][2:4] == ["-X", "PUT"]
    data = json.loads(calls[1][1])
    assert json.loads(base64.b64decode(data["content"]))["execution_id"] == ID
    assert data["branch"] == "main"


def test_unauthorized_github_error_is_not_retried_as_create():
    def fake(cmd, **kw):
        return SimpleNamespace(returncode=1, stdout="", stderr="HTTP 403 Forbidden")
    with pytest.raises(EntryError, match="GITHUB_READ_OR_AUTHORIZATION_FAILURE"):
        submit(intent(), repo="owner/repo", now=NOW, executor=fake)

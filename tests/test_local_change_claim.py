"""Offline guarantees for LOCAL auto/manual edits; no live credentials needed."""
from datetime import datetime, timedelta, timezone
import copy
import uuid

import pytest

from tools import local_change_claim as lease


NOW = datetime(2026, 11, 10, 2, 0, tzinfo=timezone.utc)
AUTO_ID = "11111111-1111-4111-8111-111111111111"
MANUAL_ID = "22222222-2222-4222-8222-222222222222"
OTHER_ID = "33333333-3333-4333-8333-333333333333"


def empty():
    return {"schema": lease.SCHEMA, "family": "LOCAL", "claims": [], "reservations": []}


def apply(state, action, claim_id, *, owner="auto", stream="SOURCE",
          paths=("runtime/local_race_entry.py",), branch="auto/local-source", ttl=45, now=NOW):
    return lease.transition(
        state, action, claim_id=claim_id, owner=owner, workstream=stream,
        paths=paths, branch=branch, ttl_minutes=ttl, now=now,
    )


def test_auto_acquire_verify_and_release_round_trip():
    state, result, changed = apply(empty(), "acquire", AUTO_ID)
    assert changed and result["status"] == "ACQUIRED"
    state2, verified, changed = apply(state, "verify", AUTO_ID)
    assert not changed and verified["claim"]["id"] == AUTO_ID
    state3, released, changed = apply(state2, "release", AUTO_ID)
    assert changed and released["status"] == "RELEASED"
    assert state3["claims"] == []


def test_manual_reservation_preempts_next_auto_write_but_not_in_flight_claim():
    state, _, _ = apply(empty(), "acquire", AUTO_ID)
    state, reserved, _ = apply(
        state, "reserve", MANUAL_ID, owner="manual",
        stream="CONSUMER", paths=("runtime/local_race_entry.py",), branch="manual/consumer",
    )
    assert reserved["status"] == "RESERVED"
    with pytest.raises(lease.ClaimError, match="MANUAL_PRIORITY_RESERVATION"):
        apply(state, "verify", AUTO_ID)
    with pytest.raises(lease.ClaimError, match="ACTIVE_CLAIM_CONFLICT"):
        apply(state, "acquire", MANUAL_ID, owner="manual",
              stream="CONSUMER", paths=("runtime/local_race_entry.py",), branch="manual/consumer")
    state, _, _ = apply(state, "release", AUTO_ID)
    state, granted, _ = apply(state, "acquire", MANUAL_ID, owner="manual",
                              stream="CONSUMER", paths=("runtime/local_race_entry.py",),
                              branch="manual/consumer")
    assert granted["status"] == "ACQUIRED"
    assert state["reservations"] == []
    with pytest.raises(lease.ClaimError, match="ACTIVE_CLAIM_CONFLICT"):
        apply(state, "acquire", AUTO_ID)


def test_disjoint_workstreams_and_paths_can_coexist():
    state, _, _ = apply(empty(), "acquire", AUTO_ID)
    state, second, _ = apply(state, "acquire", OTHER_ID, owner="manual",
                             stream="BASE9", paths=("runtime/local_fullnumerical_production.py",),
                             branch="manual/base9")
    assert second["status"] == "ACQUIRED"
    assert len(state["claims"]) == 2


def test_same_workstream_different_paths_still_conflict():
    state, _, _ = apply(empty(), "acquire", AUTO_ID)
    with pytest.raises(lease.ClaimError, match="ACTIVE_CLAIM_CONFLICT"):
        apply(state, "acquire", OTHER_ID, stream="SOURCE",
              paths=("tests/test_nar_source_manifest.py",), branch="auto/source-other")


def test_directory_parent_collision_prevents_other_workstream():
    state, _, _ = apply(empty(), "acquire", AUTO_ID,
                        stream="COMMON", paths=("runtime/",))
    with pytest.raises(lease.ClaimError, match="ACTIVE_CLAIM_CONFLICT"):
        apply(state, "acquire", OTHER_ID, stream="BASE9",
              paths=("runtime/local_fullnumerical_production.py",))


def test_manual_only_reservations_and_no_main_or_unsafe_path():
    with pytest.raises(lease.ClaimError, match="RESERVATION_MANUAL_ONLY"):
        apply(empty(), "reserve", AUTO_ID)
    with pytest.raises(lease.ClaimError, match="CLAIM_ISOLATED_BRANCH_REQUIRED"):
        apply(empty(), "acquire", AUTO_ID, branch="main")
    for bad in ("../secret", "/absolute", r"a\b", "some//bad"):
        with pytest.raises(lease.ClaimError, match="CLAIM_PATH_INVALID"):
            apply(empty(), "acquire", AUTO_ID, paths=(bad,))


def test_claim_idempotent_when_same_id_and_scope():
    state, _, _ = apply(empty(), "acquire", AUTO_ID)
    again, result, changed = apply(state, "acquire", AUTO_ID)
    assert not changed and result["status"] == "ALREADY_HELD" and again == state
    with pytest.raises(lease.ClaimError, match="CLAIM_ID_ALREADY_USED"):
        apply(state, "acquire", AUTO_ID, paths=("another/file.py",))


def test_expired_claim_not_ever_verified_or_kept_as_blocker():
    state, _, _ = apply(empty(), "acquire", AUTO_ID, ttl=1)
    late = NOW + timedelta(minutes=2)
    with pytest.raises(lease.ClaimError, match="CLAIM_NOT_ACTIVE"):
        apply(state, "verify", AUTO_ID, now=late)
    state, result, _ = apply(state, "acquire", MANUAL_ID, owner="manual", now=late,
                             branch="manual/safe")
    assert result["status"] == "ACQUIRED"
    assert len(state["claims"]) == 1


def test_renew_cannot_ignore_manual_reservation():
    state, _, _ = apply(empty(), "acquire", AUTO_ID)
    state, _, _ = apply(state, "reserve", MANUAL_ID, owner="manual",
                         branch="manual/source")
    with pytest.raises(lease.ClaimError, match="MANUAL_PRIORITY_RESERVATION"):
        apply(state, "renew", AUTO_ID)


def test_release_requires_own_active_id():
    with pytest.raises(lease.ClaimError, match="CLAIM_NOT_OWNED_OR_EXPIRED"):
        apply(empty(), "release", OTHER_ID)


def test_invalid_manifest_rejected_without_mutation():
    state = empty()
    state["schema"] = "INVALID"
    with pytest.raises(lease.ClaimError, match="SCHEMA"):
        apply(state, "acquire", AUTO_ID)


def test_remote_cas_conflict_must_recheck_and_reject_colliding_new_owner(monkeypatch):
    stored = empty()
    sha = 0
    puts = []

    def fake_api(method, *, payload=None):
        nonlocal stored, sha
        if method == "GET":
            import base64
            import json
            return {"sha": str(sha), "content": base64.b64encode(json.dumps(stored).encode()).decode()}
        assert payload["sha"] == str(sha)
        puts.append(payload)
        # Another writer wins the first attempted PUT.
        if len(puts) == 1:
            stored, _, _ = apply(stored, "acquire", MANUAL_ID, owner="manual",
                                  branch="manual/real")
            sha += 1
            raise lease.ClaimError("CLAIM_CAS_CONFLICT")
        raise AssertionError("losing actor must not commit after observing conflict")

    monkeypatch.setattr(lease, "_api", fake_api)
    with pytest.raises(lease.ClaimError, match="ACTIVE_CLAIM_CONFLICT"):
        lease.remote_action("acquire", claim_id=AUTO_ID, owner="auto",
                            workstream="SOURCE", paths=("runtime/local_race_entry.py",),
                            branch="auto/source")
    assert len(puts) == 1


def test_remote_success_is_only_reported_after_server_put(monkeypatch):
    stored = empty()
    sha = 0

    def fake_api(method, *, payload=None):
        nonlocal stored, sha
        import base64
        import json
        if method == "GET":
            return {"sha": str(sha), "content": base64.b64encode(json.dumps(stored).encode()).decode()}
        assert payload["sha"] == str(sha)
        assert payload["branch"] == lease.BRANCH
        stored = json.loads(base64.b64decode(payload["content"]))
        sha += 1
        return {"commit": {"sha": "committed"}}

    monkeypatch.setattr(lease, "_api", fake_api)
    result = lease.remote_action("acquire", claim_id=AUTO_ID, owner="auto",
                                 workstream="SOURCE", paths=("runtime/local_race_entry.py",),
                                 branch="auto/source")
    assert result["status"] == "ACQUIRED"
    assert len(stored["claims"]) == 1

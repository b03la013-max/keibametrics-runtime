"""Private SOURCE transport tests. All runners, permission proof, and signer are fixtures."""
import base64
import copy
from datetime import datetime, timedelta, timezone
import gzip
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import pytest

from runtime import execution_store as store
from runtime import formal_execution_orchestrator as orchestrator
from runtime import local_private_checkpoint as transport
from runtime import local_race_entry
from runtime.local_race_key_intake import JST, build
from runtime.local_physical.nar_source_manifest import LOCAL_BABA_CODES, PROFILE as NAR_PROFILE, _result_source, build_local_nar_manifest
from runtime.local_physical.source_acquisition import SOURCE_PROFILE

MARK = b"PRIVATE_SIGNED_FIXTURE_NEVER_PUBLISH"


def digest(value):
    return transport._sha(transport._json(value))


def write(path, data):
    path.write_bytes(data)
    path.chmod(0o600)
    return path


@pytest.fixture
def signed_case(monkeypatch, request):
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    with tempfile.TemporaryDirectory(prefix="km-private-test-", dir=Path.home()) as directory:
        root = Path(directory)
        post_race = getattr(request, "param", None) == "RESULT"
        now = datetime.now(timezone.utc) - (timedelta(minutes=30) if post_race else timedelta())
        cutoff = (now + timedelta(minutes=15)).astimezone(JST).replace(second=0, microsecond=0)
        post = cutoff + timedelta(minutes=2)
        if post.date() != cutoff.date():
            cutoff, post = cutoff + timedelta(minutes=2), post + timedelta(minutes=2)
        intent = build({"venue_id": "KAW", "race_date": post.date().isoformat(), "race_no": 1,
                        "scheduled_post_at": post.isoformat(), "prediction_cutoff": cutoff.isoformat()}, now=now)
        basis = orchestrator.source_checkpoint_basis(intent)
        # This fixture represents a historical NAR checkpoint, which has no
        # new provider-profile field and remains readable by digest.
        basis.pop("source_manifest_profile")
        basis.pop("scheduled_post_at")
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key().public_bytes_raw()
        cfg = transport.gateway.family_config("LOCAL")
        health = {
            **cfg["active_bundle_sha256"],
            "family": "LOCAL", "status": "READY", "runtime_revision": cfg["runtime_profile"],
            "github_revision": cfg["runtime_git_revision"], "receipt_signer_key_id": cfg["receipt_signer_key_id"],
            "receipt_public_key_b64": base64.b64encode(public_key).decode(),
            "capabilities": cfg["required_capabilities"], "engine_sha256": cfg["engine_sha256"],
            "parameter_map_sha256": cfg["parameter_map_sha256"],
        }
        assert transport.gateway.assess_runtime_health(health, "LOCAL")["status"] == "PASS"
        calls = []
        write(root / "fixture-health.json", transport._json(health))

        def health_only(url, *, method, **kwargs):
            assert method == "GET" and url == cfg["external_endpoint"] + "/health"
            assert "payload" not in kwargs
            calls.append(method)
            return 200, health

        monkeypatch.setattr(transport.gateway, "request_json", health_only)
        authority, _ = transport.resolve_current_authority()
        proof = write(root / "permission-fixture.txt", b"ISOLATED TEST FIXTURE PERMISSION ONLY")
        approval = write(root / "runtime-fixture.txt", b"ISOLATED TEST RUNTIME APPROVAL ONLY")
        binding = {
            "schema": "KM-LOCAL-PRIVATE-CHECKPOINT-BINDING-v1", "venue_id": "KAW",
            "code_sha256": transport.code_sha256(), "policy_sha256": transport._sha(authority.read_bytes()),
            "gateway_endpoint": cfg["external_endpoint"], "gateway_sha256": transport._sha(
                (transport.ROOT / "profiles/current_execution_gateway.json").read_bytes()),
            "signer_runtime_revision": cfg["runtime_git_revision"],
            "signer_public_key_sha256": transport._sha(public_key),
            "permission_file": proof.name, "permission_sha256": transport._sha(proof.read_bytes()),
            "private_storage_and_authorized_runtime_processing": True,
            "source_url_prefixes": {"NAR_OFFICIAL": ["https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/"]},
            "valid_from": (now - timedelta(minutes=5)).isoformat(),
            "valid_until": (post + timedelta(hours=1)).isoformat(),
            "retain_until": (post + timedelta(days=1)).isoformat(),
            "formal_runtime_approval_file": approval.name,
            "formal_runtime_approval_sha256": transport._sha(approval.read_bytes()),
            "formal_execution_ids": [intent["execution_id"]], "cost_control_ref": "FIXTURE_ONLY",
        }
        binding_path = write(root / "binding.json", transport._json(binding))
        binding_sha = transport._sha(binding_path.read_bytes())
        runtime_hashes = {k: health[k] for k in ("legacy_runtime_app_sha256", "source_acquisition_sha256",
                                                  "nar_source_manifest_sha256", "nar_runner_universe_sha256")}
        runtime_hashes["runtime_wrapper_sha256"] = health["runtime_app_sha256"]

        def signed(artifact, phase="SOURCE", status="SOURCE_FROZEN", timestamp=None):
            if phase == "SOURCE":
                artifact = copy.deepcopy(artifact)
                artifact["source_snapshot_sha256"] = digest(
                    {k: v for k, v in artifact.items() if k != "source_snapshot_sha256"})
            receipt = {
                "race_id": intent["race_id"], "family": "LOCAL", "phase": phase, "status": status,
                "artifact_sha256": digest(artifact), "github_revision": cfg["runtime_git_revision"],
                "engine_sha256": cfg["engine_sha256"], "parameter_map_sha256": cfg["parameter_map_sha256"],
                "timestamp": timestamp or (now - timedelta(seconds=1)).isoformat(), "runtime_hashes": runtime_hashes,
            }
            return {"artifact": artifact, "receipt": receipt, "receipt_sha256": digest(receipt),
                    "signature": base64.b64encode(private_key.sign(transport._json(receipt))).decode(),
                    "signature_alg": "Ed25519", "signer_key_id": cfg["receipt_signer_key_id"]}

        runners = [{"runner_id": str(n), "horse_no": n, "name": f"Fixture-{n}"}
                   for n in range(1, 4 if post_race else 3)]
        card_spec, odds_spec = build_local_nar_manifest({
            **basis, "require_active_runner_universe": True,
        })["sources"]
        url, odds_url = card_spec["url"], odds_spec["url"]
        card_id, odds_id = card_spec["source_id"], odds_spec["source_id"]
        snapshot = {"source_id": card_id, "official": True, "authority": "NAR_OFFICIAL",
                    "fetched_at": (now - timedelta(seconds=5)).isoformat(), "requested_url": url, "final_url": url,
                    "source_class": "OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT",
                    "raw_sha256": transport._sha(MARK),
                    "raw_gzip_b64": base64.b64encode(gzip.compress(MARK, mtime=0)).decode()}
        snapshot["snapshot_sha256"] = digest(snapshot)
        odds = {**snapshot, "source_id": odds_id, "requested_url": odds_url, "final_url": odds_url,
                "source_class": "OFFICIAL_ACTIVE_BETTING_UNIVERSE"}
        odds["snapshot_sha256"] = digest({k: v for k, v in odds.items() if k != "snapshot_sha256"})
        statuses = [{"runner_id": r["runner_id"], "status": "ACTIVE", "evidence_sources": [card_id, odds_id]}
                    for r in runners]
        active = {"universe_type": "ACTIVE", "runners": runners, "runner_count": len(runners), "source_id": card_id,
                  "source_snapshot_sha256": snapshot["snapshot_sha256"], "status_registry_sha256": digest(statuses)}
        active["runner_universe_sha256"] = digest(active)
        snapshots = [snapshot, odds]
        bundle = [{k: snap[k] for k in ("source_id", "raw_sha256", "snapshot_sha256", "fetched_at", "final_url")}
                  for snap in snapshots]
        manifest = [{k: spec[k] for k in ("source_id", "url", "source_class", "authority", "required")}
                    for spec in (card_spec, odds_spec)]
        table = [["枠番", "馬番", "競走馬"]]
        for r in runners:
            number = str(r["horse_no"])
            table.extend([
                [number, number, r["name"], "試験騎手", "3.5 (1人気)"] + [""] * 5,
                ["牡3", "", "", "56.0"] + [""] * 5,
                ["試験父", "試験厩舎", "480 (+0)"] + [""] * 5,
                ["試験母"] + [""] * 5,
                ["(試験母父)"] + [""] * 5,
            ])
        numerical_evidence = {"race_card_tables": {
            "value": [table], "source_id": card_id, "fetched_at": snapshot["fetched_at"],
            "snapshot_sha256": snapshot["snapshot_sha256"]},
            "start_time": {"value": post.strftime("%H:%M"), "source_id": card_id}}
        artifact = {
            "profile": SOURCE_PROFILE, "source_manifest_profile": NAR_PROFILE, "formal_ready": True, "errors": [],
            "race_id": intent["race_id"], "source_race_context": {"venue_id": "KAW", "race_date": intent["race_date"],
                                                                 "race_no": 1},
            "prediction_cutoff": intent["prediction_cutoff"], "source_freeze_at": (now - timedelta(seconds=2)).isoformat(),
            "sources": snapshots, "raw_source_bundle_sha256": digest(bundle),
            "required_source_manifest": manifest, "required_source_manifest_sha256": digest(manifest),
            "normalized_evidence": numerical_evidence, "normalized_evidence_sha256": digest(numerical_evidence),
            "official_runner_universe": active, "active_runner_universe": active,
            "declared_runner_universe": {"runners": runners},
            "official_runner_universe_sha256": active["runner_universe_sha256"],
            "runner_status_registry": statuses, "runner_status_registry_sha256": digest(statuses),
            "public_redistribution_authorized": False,
        }
        envelope = signed(artifact)
        envelope_path = write(root / "signed-source.json", json.dumps(envelope, indent=2).encode())
        yield root, binding_path, binding_sha, intent, basis, signed, envelope_path, envelope, calls


def test_private_checkpoint_separates_public_and_recovers_exact_bytes(signed_case):
    root, binding, pin, intent, basis, signed, path, envelope, calls = signed_case
    eid = intent["execution_id"]
    public_input = root / "public-input"
    public_input.mkdir()
    write(public_input / "source_receipt_envelope.json", path.read_bytes())
    with pytest.raises(store.ExecutionStoreError, match="PRIVATE_SOURCE_PUBLIC_STORAGE_FORBIDDEN"):
        store.persist_phase(eid, "SOURCE", "1", public_input, root=root / "public-store")
    assert not (root / "public-store").exists()
    first = transport.PrivateCheckpoint(binding, pin)
    saved = first.import_source(path, basis, github_sha="FIXTURE")
    second = transport.PrivateCheckpoint(binding, pin)
    resolved = second.resolve(eid, "SOURCE")
    assert len(calls) == 2
    stored = resolved["run_dir"] / "source_receipt_envelope.json"
    assert stored.read_bytes() == path.read_bytes()
    assert gzip.decompress(base64.b64decode(envelope["artifact"]["sources"][0]["raw_gzip_b64"])) == MARK
    assert saved["latest"]["manifest_sha256"] == resolved["latest"]["manifest_sha256"]
    assert second.import_source(path, basis, github_sha="FIXTURE")["latest"] == saved["latest"]
    with pytest.raises(store.ExecutionStoreError, match="PRIVATE_SOURCE_PUBLIC_STORAGE_FORBIDDEN"):
        store.materialize_phase(eid, "SOURCE", root / "public-materialized", root=second.store_root)
    with pytest.raises(store.ExecutionStoreError, match="PRIVATE_SOURCE_PUBLIC_STORAGE_FORBIDDEN"):
        store.require_public_artifact_paths([stored])
    assert not (root / "public-materialized").exists()

    # Crash after durable run publication but before atomic LATEST publication.
    pointer = resolved["run_dir"].parents[1] / "LATEST.json"
    pointer.unlink()
    restored = transport.PrivateCheckpoint(binding, pin).import_source(path, basis, github_sha="FIXTURE")
    assert restored["latest"]["manifest_sha256"] == saved["latest"]["manifest_sha256"]

    artifact = copy.deepcopy(envelope["artifact"])
    odds = artifact["sources"][1]
    revised_raw = b"DIFFERENT_SIGNED_FIXTURE_BYTES"
    odds["raw_sha256"] = transport._sha(revised_raw)
    odds["raw_gzip_b64"] = base64.b64encode(gzip.compress(revised_raw, mtime=0)).decode()
    odds["snapshot_sha256"] = digest({k: v for k, v in odds.items() if k != "snapshot_sha256"})
    artifact["raw_source_bundle_sha256"] = digest(
        [{k: snap[k] for k in ("source_id", "raw_sha256", "snapshot_sha256", "fetched_at", "final_url")}
         for snap in artifact["sources"]])
    altered = write(root / "altered.json", transport._json(signed(artifact)))
    with pytest.raises(store.ExecutionStoreError, match="IMMUTABLE_REVISION_CONFLICT"):
        second.import_source(altered, basis, github_sha="FIXTURE")
    assert stored.read_bytes() == path.read_bytes()


@pytest.mark.parametrize("defect, reason", [
    ("signature", "SIGNATURE_INVALID"),
    ("raw", "RAW_OR_SNAPSHOT_HASH_INVALID"),
    ("scope", "ENDPOINT_OUTSIDE_PERMISSION"),
    ("authority", "CONSUMER_NOT_AUTHORIZED"),
    ("active", "ACTIVE_UNIVERSE_INVALID"),
    ("race", "RACE_CONTEXT_MISMATCH"),
])
def test_signed_private_input_fails_closed(signed_case, defect, reason):
    root, binding, pin, intent, basis, signed, path, envelope, calls = signed_case
    artifact = copy.deepcopy(envelope["artifact"])
    if defect == "raw":
        artifact["sources"][0]["raw_gzip_b64"] = base64.b64encode(gzip.compress(b"tamper")).decode()
    if defect == "scope":
        snapshot = artifact["sources"][0]
        snapshot["final_url"] = "https://unapproved.invalid/KeibaWeb/TodayRaceInfo/DebaTable"
        snapshot["snapshot_sha256"] = digest({k: v for k, v in snapshot.items() if k != "snapshot_sha256"})
        artifact["official_runner_universe"]["source_snapshot_sha256"] = snapshot["snapshot_sha256"]
        universe = artifact["official_runner_universe"]
        universe["runner_universe_sha256"] = digest({k: v for k, v in universe.items() if k != "runner_universe_sha256"})
        artifact["official_runner_universe_sha256"] = universe["runner_universe_sha256"]
        artifact["raw_source_bundle_sha256"] = digest(
            [{k: snap[k] for k in ("source_id", "raw_sha256", "snapshot_sha256", "fetched_at", "final_url")}
             for snap in artifact["sources"]])
    if defect == "authority":
        artifact["source_manifest_profile"] = "UNAPPROVED_NANKAN"
    if defect == "active":
        artifact["runner_status_registry"][0]["status"] = "ACTIVE_DECLARED"
    if defect == "race":
        basis = {**basis, "race_no": 2}
    changed = signed(artifact)
    if defect == "signature":
        changed["signature"] = base64.b64encode(b"x" * 64).decode()
    write(path, transport._json(changed))
    private = transport.PrivateCheckpoint(binding, pin)
    with pytest.raises(store.ExecutionStoreError, match=reason):
        private.import_source(path, basis, github_sha="FIXTURE")
    assert private.resolve(intent["execution_id"], "SOURCE") is None


def test_normal_kaw_entry_consumes_private_readback(signed_case):
    root, binding, pin, intent, basis, signed, path, envelope, calls = signed_case
    first = transport.PrivateCheckpoint(binding, pin)
    first.import_source(path, basis, github_sha="FIXTURE")
    second = transport.PrivateCheckpoint(binding, pin)
    output = second.work_root / intent["execution_id"] / "entry"
    token = orchestrator.PRIVATE_CHECKPOINT.set(second)
    try:
        report = local_race_entry.run({**intent, "analysis_only": True}, output=output, run_id="fixture")
    finally:
        orchestrator.PRIVATE_CHECKPOINT.reset(token)
    assert report["source"]["signed_source_verified"] is True
    assert report["source_receipt_sha256"] == envelope["receipt_sha256"]
    computed = json.loads((output / "numerical_materialization.json").read_bytes())
    assert computed["numeric_coverage"]["numeric_value_count"] == 2 * 29
    assert not (orchestrator.ROOT / "runtime/executions" / intent["execution_id"]).exists()
    assert len(calls) == 2


def test_kaw_live_source_never_falls_back_to_nar(signed_case, monkeypatch):
    _, binding, pin, intent, _, _, _, _, calls = signed_case
    private = transport.PrivateCheckpoint(binding, pin)
    basis = orchestrator.source_checkpoint_basis(intent)
    assert basis["source_manifest_profile"] == transport.nankan_kaw_source.PROFILE

    def no_network(*args, **kwargs):
        pytest.fail("Fresh KAW requests may not use the legacy SOURCE transport")

    monkeypatch.setattr(transport.gateway, "request_json", no_network)
    with pytest.raises(store.ExecutionStoreError, match="PRIVATE_NANKAN_SIGNED_SOURCE_IMPORT_REQUIRED"):
        private.acquire_source(basis, github_sha="FIXTURE")
    with pytest.raises(store.ExecutionStoreError, match="PRIVATE_SOURCE_NANKAN_EXCLUSIVE_PERMISSION_REQUIRED"):
        private.produce_nankan_source(basis, no_network, github_sha="FIXTURE")
    private.binding["formal_execution_ids"] = []
    with pytest.raises(store.ExecutionStoreError, match="PRIVATE_SOURCE_EXECUTION_APPROVAL_REQUIRED"):
        private.acquire_source(basis, github_sha="FIXTURE")
    assert calls == []


def test_kaw_nankan_signed_private_roundtrip(signed_case, monkeypatch, tmp_path, capsys):
    from test_nankan_kaw_source import KAW_DAY_ID, fixture_access_policy, pages
    from runtime import urw_nankan_reference_source as nankan
    from runtime import local_race_day_dispatcher as dispatcher
    from runtime import family_authority_guard
    from runtime import kaw_research_startup as startup

    _, binding_path, _, intent, _, sign, _, _, calls = signed_case
    binding = json.loads(binding_path.read_bytes())
    binding["source_url_prefixes"] = {"NANKAN_OFFICIAL": [nankan.ORIGIN + "/"]}
    binding["source_only_execution_ids"] = binding.pop("formal_execution_ids")
    binding_bytes = transport._json(binding)
    write(binding_path, binding_bytes)
    monkeypatch.setenv(transport.BINDING_ENV, str(binding_path))
    monkeypatch.setenv(transport.BINDING_SHA_ENV, transport._sha(binding_bytes))
    checkpoint = transport.PrivateCheckpoint.from_env()

    new_day = datetime.fromisoformat(intent["scheduled_post_at"])
    date_text = f"{new_day.year}年{new_day.month}月{new_day.day}日"
    new_provider_id = new_day.strftime("%Y%m%d") + KAW_DAY_ID[8:]
    fetched = datetime.now(JST) - timedelta(seconds=2)
    raw_by_url = {}
    for url, raw in pages().items():
        raw_by_url[url.replace(KAW_DAY_ID, new_provider_id)] = (
            raw.decode().replace(KAW_DAY_ID, new_provider_id)
            .replace("2026年10月22日", date_text)
            .replace("12:20", new_day.strftime("%H:%M")).replace("12:09", fetched.strftime("%H:%M")).encode()
        )
    requested = []

    def capture(_, url):
        assert url.startswith(nankan.ORIGIN + "/")
        requested.append(url)
        raw = raw_by_url[url]
        return {"url": url, "fetched_at": fetched.isoformat(),
                "http_status": 200, "raw_sha256": transport._sha(raw),
                "source_policy": fixture_access_policy(fetched.isoformat())}, raw

    monkeypatch.setattr(nankan.Client, "get", capture)
    basis = orchestrator.source_checkpoint_basis(intent)

    def sign_fixture(phase, race_id, status, artifact, errors):
        assert phase == "SOURCE" and race_id == basis["race_id"] and not errors
        return sign(artifact, phase=phase, status=status, timestamp=datetime.now(timezone.utc).isoformat())

    with pytest.raises(store.ExecutionStoreError, match="NANKAN_LIVE_ACQUISITION_PERMISSION_REQUIRED"):
        checkpoint.produce_nankan_source(basis, sign_fixture, github_sha="FIXTURE")
    assert requested == calls == []
    binding["nankan_live_acquisition_authorized"] = True
    write(binding_path, transport._json(binding))
    monkeypatch.setenv(transport.BINDING_SHA_ENV, transport._sha(binding_path.read_bytes()))
    checkpoint = transport.PrivateCheckpoint.from_env()
    expired_basis = {**basis, "prediction_cutoff": (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()}
    with pytest.raises(store.ExecutionStoreError, match="NANKAN_CUTOFF_PASSED"):
        checkpoint.produce_nankan_source(expired_basis, sign_fixture, github_sha="FIXTURE")
    assert requested == calls == []
    result = checkpoint.produce_nankan_source(basis, sign_fixture, github_sha="FIXTURE")
    assert result["status"] == "PASS" and requested == list(raw_by_url)
    resolved = transport.PrivateCheckpoint.from_env().resolve(basis["race_id"], "SOURCE")
    envelope_path = resolved["run_dir"] / "source_receipt_envelope.json"
    envelope = json.loads(envelope_path.read_bytes())
    assert envelope["receipt_sha256"] == result["receipt_sha256"]
    assert envelope["artifact"]["provider"] == "NANKAN_OFFICIAL"
    assert envelope_path.stat().st_mode & 0o777 == 0o600
    assert checkpoint.produce_nankan_source(basis, sign_fixture, github_sha="FIXTURE")["status"] == "REUSED"
    assert requested == list(raw_by_url)
    assert set(calls) == {"GET"}

    # The approved signer can hand the original bytes to a separate private
    # Runner whose SOURCE permission does not authorize fetching or prediction.
    day, eid = intent['race_date'], intent['execution_id']
    consumer_root = checkpoint.root / "consumer"
    consumer_root.mkdir(mode=0o700)
    for field in ("permission_file", "formal_runtime_approval_file"):
        name = binding[field]
        write(consumer_root / name, (checkpoint.root / name).read_bytes())
    consumer_pin = {**binding, "nankan_live_acquisition_authorized": False}
    consumer_binding = write(consumer_root / "binding.json", transport._json(consumer_pin))
    consumer = transport.PrivateCheckpoint(consumer_binding, transport._sha(consumer_binding.read_bytes()))
    transferred = write(consumer_root / "signed-source.json", envelope_path.read_bytes())
    output = consumer.work_root / eid / "source-intake"
    with pytest.raises(store.ExecutionStoreError, match="SOURCE_EXECUTION_APPROVAL_REQUIRED"):
        consumer.import_source(transferred, {**basis, "race_id": eid.replace("-R01-", "-R02-")},
                               github_sha="FIXTURE")
    token = orchestrator.PRIVATE_CHECKPOINT.set(consumer)
    try:
        accepted = local_race_entry.run(intent, output=output, run_id="fixture", github_sha="FIXTURE",
                                        private_source=transferred, source_only=True)
        assert accepted["status"] == "SOURCE_PASS"
        with pytest.raises(store.ExecutionStoreError, match="FORMAL_EXECUTION_APPROVAL_REQUIRED"):
            local_race_entry.run(intent, output=output, run_id="fixture")
    finally:
        orchestrator.PRIVATE_CHECKPOINT.reset(token)
    assert not (output / "numerical_materialization.json").exists()
    imported = consumer.resolve(eid, "SOURCE")
    imported_path = imported["run_dir"] / "source_receipt_envelope.json"
    assert imported_path.read_bytes() == transferred.read_bytes()
    report = dispatcher.private_kaw_day(tmp_path, day, 120, now=datetime.now(JST), private=consumer)
    assert report["races"][eid]["status"] == "SIGNED_NANKAN_SOURCE_VERIFIED"
    assert report["dispatch_count"] == 0

    # A newly approved formal scope can read back the same immutable SOURCE.
    # No provider refetch or change of the original storage manifest is needed.
    binding["formal_execution_ids"] = [eid]
    binding["nankan_live_acquisition_authorized"] = False
    write(binding_path, transport._json(binding))
    monkeypatch.setenv(transport.BINDING_SHA_ENV, transport._sha(binding_path.read_bytes()))
    checkpoint = transport.PrivateCheckpoint.from_env()
    assert checkpoint.resolve(eid, "SOURCE")["latest"] == resolved["latest"]
    assert checkpoint.import_source(envelope_path, basis, github_sha="NEW_FIXTURE")["latest"] == resolved["latest"]
    assert checkpoint.produce_nankan_source(basis, sign_fixture, github_sha="FIXTURE")["status"] == "REUSED"
    assert requested == list(raw_by_url)

    # The actual verifier and private store supply the program, including R2.
    # Only R1 has signed runners and Binding scope.
    now = datetime.now(JST)
    day_report = dispatcher.private_kaw_day(tmp_path, day, 120, now=now, private=checkpoint)
    race2 = eid.replace('-R01-', '-R02-')
    assert day_report['races'][eid]['active_runner_count'] == 2
    assert day_report['races'][race2]['status'] == 'HOLD_SIGNED_NANKAN_SOURCE_REQUIRED'

    monkeypatch.setenv('KM_LOCAL_AUTONOMOUS_ENABLED', 'true')
    options = dict(now=now, execute=True, private=checkpoint, clock=lambda: now)
    missing = dispatcher.private_kaw_day(tmp_path, day, 120, **options)
    assert missing['status'] == 'HOLD_PRIVATE_NANKAN_DAY_APPROVAL' and missing['dispatch_count'] == 0

    profiles = tmp_path / 'profiles'
    approvals = profiles / 'local_autonomous_approvals'
    approvals.mkdir(parents=True)
    owner = profiles / 'local_production_static_owner_20261014_v1.json'
    owner.write_bytes((transport.ROOT / 'profiles' / owner.name).read_bytes())
    original_resolver = family_authority_guard.resolve_current_authority
    monkeypatch.setattr(family_authority_guard, 'resolve_current_authority',
                        lambda *, root=None, now=None: original_resolver(now=now))
    approval = approvals / f'{day}-KAW.json'
    approval.write_text(json.dumps({
        'family_id': 'LOCAL', 'venue_id': 'KAW', 'race_date': day,
        'current_authority_manifest': intent['current_authority_manifest'],
        'destination': checkpoint.config['external_endpoint'].rstrip('/'),
        'plan_sha256': day_report['plan_sha256'], 'enabled': True, 'owner_approval_ref': 'FIXTURE_ONLY',
        'scheduled_execution_authorized': True, 'existing_runtime_usage_cost_authorized': True,
        'data_scope': 'INTENT_SOURCE_STATIC_PRE_KRS_KRS_FINAL_RESULT_SETTLEMENT',
        'race_numbers': [1], 'activation_phase': 'B', 'max_dispatches': 1, 'cost_control_ref': 'FIXTURE_ONLY',
        'start_lead_seconds': 1800, 'minimum_remaining_seconds': 300,
    }))
    scoped = dispatcher.private_kaw_day(tmp_path, day, 120, **{**options, 'private': consumer})
    assert scoped['dispatch_count'] == 0 and not scoped['races'][eid]['execution_approved']
    assert not (consumer.work_root / 'day-dispatch' / day / f'{eid}.json').exists()

    day_approval = approval.read_bytes()
    write(checkpoint.root / binding['formal_runtime_approval_file'], day_approval)
    binding['formal_runtime_approval_sha256'] = transport._sha(day_approval)
    write(binding_path, transport._json(binding))
    monkeypatch.setenv(transport.BINDING_SHA_ENV, transport._sha(binding_path.read_bytes()))
    checkpoint = transport.PrivateCheckpoint.from_env()
    approval.unlink()
    assert checkpoint.resolve(eid, "SOURCE")["latest"] == resolved["latest"]
    sent = []

    def held(request, **kwargs):
        assert orchestrator.PRIVATE_CHECKPOINT.get().binding_sha == checkpoint.binding_sha
        claim = checkpoint.work_root / 'day-dispatch' / day / f'{eid}.json'
        assert json.loads(claim.read_bytes())['source_receipt_sha256'] == envelope['receipt_sha256']
        assert claim.stat().st_mode & 0o777 == 0o600
        sent.append(request['execution_id'])
        return {'status': 'HOLD', 'first_failed_phase': 'STATIC_FREEZE'}

    monkeypatch.setattr(local_race_entry, 'run', held)
    monkeypatch.setattr(startup, 'ROOT', tmp_path)
    monkeypatch.setattr(startup, 'MOUNT_ROOT', checkpoint.root)
    write(checkpoint.root / 'bootstrap_probe.json', transport._json({
        'nonce': 'fixture', 'sha256': transport._sha(b'fixture'),
    }))
    monkeypatch.delenv('KM_LOCAL_AUTONOMOUS_ENABLED')
    assert startup.main(['--dispatch-once']) == 2
    assert 'KAW_RUNNER_DISPATCH_NOT_ACTIVATED' in capsys.readouterr().out
    monkeypatch.setenv('KM_LOCAL_AUTONOMOUS_ENABLED', 'true')
    assert startup.main([]) == 0 and not sent
    capsys.readouterr()
    assert startup.main(['--dispatch-once']) == 0
    log = capsys.readouterr().out.splitlines()
    assert 'KAW_RUNNER_BINDING_VALIDATED' in log
    assert json.loads(log[-1])['dispatch_count'] == 1
    assert envelope['receipt_sha256'] not in '\n'.join(log)
    status_path = checkpoint.work_root / 'day-dispatch' / day / 'day-status.json'
    launched = json.loads(status_path.read_bytes())
    assert launched['dispatch_count'] == 1 and launched['races'][eid]['first_failed_phase'] == 'STATIC_FREEZE'
    assert launched['races'][race2]['execution_approved'] is False
    assert startup.main(['--dispatch-once']) == 0
    repeated = json.loads(status_path.read_bytes())
    assert repeated['races'][eid]['status'] == 'HOLD_PRIOR_CLAIM_NO_AUTOMATIC_RETRY'
    assert repeated['dispatch_count'] == 0 and sent == [eid]
    assert requested == list(raw_by_url)


def test_startup_health_does_not_load_formal_binding(signed_case, monkeypatch, capsys):
    from runtime import kaw_research_startup as startup

    root, binding, _, *_ = signed_case
    monkeypatch.setattr(startup, "MOUNT_ROOT", root)
    write(root / "bootstrap_probe.json", transport._json({
        "nonce": "fixture", "sha256": transport._sha(b"fixture"),
    }))
    monkeypatch.delenv(transport.BINDING_ENV, raising=False)
    monkeypatch.delenv(transport.BINDING_SHA_ENV, raising=False)
    assert startup.main([]) == 0
    assert "KAW_RUNNER_WAITING_FOR_BINDING" in capsys.readouterr().out
    assert startup.main(["--check-binding"]) == 2
    monkeypatch.setenv(transport.BINDING_ENV, str(binding))
    monkeypatch.setenv(transport.BINDING_SHA_ENV, "0" * 64)
    assert startup.main([]) == 0
    assert "KAW_RUNNER_BINDING_NOT_CHECKED" in capsys.readouterr().out
    with pytest.raises(store.ExecutionStoreError, match="BINDING_SHA_MISMATCH"):
        startup.main(["--check-binding"])


def test_private_binding_and_publication_boundaries(signed_case, monkeypatch):
    root, binding, pin, intent, basis, signed, path, envelope, calls = signed_case
    with pytest.raises(store.ExecutionStoreError, match="BINDING_SHA_MISMATCH"):
        transport.PrivateCheckpoint(binding, "0" * 64)
    wrong_code = {**json.loads(binding.read_bytes()), "code_sha256": "0" * 64}
    wrong_binding = write(root / "wrong-code.json", transport._json(wrong_code))
    with pytest.raises(store.ExecutionStoreError, match="BINDING_SCOPE_OR_CODE_INVALID"):
        transport.PrivateCheckpoint(wrong_binding, transport._sha(wrong_binding.read_bytes()))
    private = transport.PrivateCheckpoint(binding, pin)
    link = root / "link"
    link.symlink_to(transport.ROOT, target_is_directory=True)
    with pytest.raises(store.ExecutionStoreError, match="PATH_FORBIDDEN"):
        private.directory(link)
    with pytest.raises(store.ExecutionStoreError, match="OUTPUT_MUST_BE_IN_WORK_ROOT"):
        private.output_directory(private.store_root)
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    with pytest.raises(store.ExecutionStoreError, match="CI_FORBIDDEN"):
        transport.PrivateCheckpoint(binding, pin)
    assert calls == []


@pytest.mark.parametrize("defect, code", [
    ("expired", "SOURCE_PROCESSING_PERMISSION_EXPIRED"),
    ("approval", "SOURCE_EXECUTION_APPROVAL_REQUIRED"),
    ("cost", "SOURCE_EXECUTION_APPROVAL_REQUIRED"),
])
def test_source_only_proof_fails_before_acquisition(signed_case, defect, code):
    root, binding_path, _, intent, *_ = signed_case
    binding = json.loads(binding_path.read_bytes())
    binding["source_only_execution_ids"] = binding.pop("formal_execution_ids")
    if defect == "expired":
        binding["valid_until"] = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
    elif defect == "approval":
        write(root / binding["formal_runtime_approval_file"], b"CHANGED TEST PROOF")
    else:
        binding["cost_control_ref"] = ""
    write(binding_path, transport._json(binding))
    private = transport.PrivateCheckpoint(binding_path, transport._sha(binding_path.read_bytes()))
    with pytest.raises(store.ExecutionStoreError, match=code):
        private.acquire_source(orchestrator.source_checkpoint_basis(intent), github_sha="FIXTURE")


def test_new_process_reuses_checkpoint_via_normal_cli(signed_case):
    root, binding, pin, intent, basis, signed, path, envelope, calls = signed_case
    first = transport.PrivateCheckpoint(binding, pin)
    first.import_source(path, basis, github_sha="FIXTURE")
    request = write(root / "fixture-request.json", transport._json(intent))
    output = first.work_root / intent["execution_id"] / "restart"
    cmd = """
import json, sys
from pathlib import Path
from runtime import execution_gateway, local_race_entry
health = json.loads(Path(sys.argv.pop(1)).read_bytes())
def fixture_health(url, *, method, **kwargs):
    assert method == 'GET' and url.endswith('/health') and 'payload' not in kwargs
    return 200, health
execution_gateway.request_json = fixture_health
raise SystemExit(local_race_entry.main())
"""
    env = {**os.environ, transport.BINDING_ENV: str(binding), transport.BINDING_SHA_ENV: pin}
    proc = subprocess.run([sys.executable, "-c", cmd, str(root / "fixture-health.json"), "--request", str(request),
                           "--output", str(output), "--run-id", "restart", "--private-source-only"],
                          cwd=transport.ROOT, env=env, capture_output=True, check=True)
    summary = json.loads(proc.stdout)
    assert summary == {"status": "SOURCE_PASS", "execution_id": intent["execution_id"], "private_report_saved": True}
    assert not proc.stderr
    assert MARK not in proc.stdout
    assert json.loads((output / "entry_report.json").read_bytes())["signed_source_verified"] is True


def test_formal_orchestrator_routes_fixture_final_without_public_output(signed_case, monkeypatch):
    root, binding, pin, intent, basis, signed, path, envelope, calls = signed_case
    private = transport.PrivateCheckpoint(binding, pin)
    private.import_source(path, basis, github_sha="FIXTURE")
    eid = intent["execution_id"]
    output = private.work_root / eid / "formal"
    temporary = private.work_root / eid / "tmp"
    final = signed({
        "source_receipt_sha256": envelope["receipt_sha256"],
        "source_snapshot_sha256": envelope["artifact"]["source_snapshot_sha256"],
        "final_freeze_timestamp": envelope["receipt"]["timestamp"],
    }, phase="FINAL", status="PASS")

    def formal_fixture(command, *, cwd, env, capture_output, text):
        assert command[-1] == "runtime.non_jra_formal_runner"
        assert env["KM_LOCAL_PRIVATE_CHECKPOINT_RUNNER"] == "1"
        assert env[transport.BINDING_SHA_ENV] == pin and capture_output and text
        request = Path(env["REQUEST_FILE"])
        assert request.is_relative_to(temporary)
        assert json.loads(request.read_bytes())["source_receipt"] == envelope
        assert Path(env["KM_RUNTIME_OUT"]) == output
        write(output / "final_receipt_envelope.json", transport._json(final))
        return subprocess.CompletedProcess(command, 0, MARK.decode(), "")

    monkeypatch.setattr(orchestrator.subprocess, "run", formal_fixture)
    token = orchestrator.PRIVATE_CHECKPOINT.set(private)
    try:
        request = orchestrator.build_phase_request(intent, "FORMAL")
        result = orchestrator.run_phase(request, "FORMAL", run_id="fixture",
                                        github_sha="FIXTURE", runtime_out=output, tmp_root=temporary)
    finally:
        orchestrator.PRIVATE_CHECKPOINT.reset(token)
    assert result["status"] == "PASS" and result["stdout_tail"] is None
    recovered = transport.PrivateCheckpoint(binding, pin).resolve(eid, "FORMAL")
    assert (recovered["run_dir"] / "final_receipt_envelope.json").read_bytes() == transport._json(final)
    assert store.resolve_phase(eid, "FORMAL") is None


@pytest.mark.parametrize("signed_case", ["RESULT"], indirect=True)
@pytest.mark.parametrize("interrupted", [False, True])
def test_private_result_reads_frozen_final_and_submits_at_most_once(signed_case, monkeypatch, interrupted):
    from runtime.local_physical.source_acquisition import snapshot_from_bytes

    _, binding, pin, intent, basis, signed, path, source, calls = signed_case
    private = transport.PrivateCheckpoint(binding, pin)
    eid = intent["execution_id"]
    result_output = private.work_root / eid / "entry-result"
    saved = private.import_source(path, basis, github_sha="FIXTURE")
    signed_final = signed({
        "source_receipt_sha256": source["receipt_sha256"],
        "source_snapshot_sha256": source["artifact"]["source_snapshot_sha256"],
        "final_freeze_timestamp": source["receipt"]["timestamp"],
        "final_ticket": {"tickets": [
            {"bet_type": "EXACTA", "selection": [1, 2], "stake": 100},
            {"bet_type": "TRIO", "selection": [1, 2, 3], "stake": 200},
            {"bet_type": "TRIFECTA", "selection": [2, 1, 3], "stake": 100},
        ]},
    }, phase="FINAL", status="PASS")
    formal_out = private.output_directory(private.work_root / eid / "formal", create=True)
    private.write(formal_out / "final_receipt_envelope.json", signed_final)
    source_resolved = private.resolve(eid, "SOURCE")
    assert saved["latest"] == source_resolved["latest"]
    private.write(formal_out / "formal_checkpoint_basis.json",
                  orchestrator.formal_checkpoint_basis(intent, source_resolved))
    private.persist(eid, "FORMAL", "fixture-formal", formal_out, github_sha="FIXTURE")
    health_only = transport.gateway.request_json

    def gateway_fixture(url, *, method, **kwargs):
        if method == "GET":
            return health_only(url, method=method, **kwargs)
        assert url == private.config["external_endpoint"] + "/result" and kwargs["attempts"] == 1
        calls.append("RESULT")
        if interrupted:
            raise TimeoutError("fixture after submit")
        payload = kwargs["payload"]
        assert payload["final_receipt"] == signed_final
        assert payload["settlement"]["return"] == 2300
        return 200, signed({
            "official_result": payload["official_result"],
            "settlement": {**payload["settlement"], "pfs_authority": payload["pfs_authority"]},
            "frozen_refs": {"final_receipt_sha256": signed_final["receipt_sha256"],
                            "final_ticket_sha256": digest(signed_final["artifact"]["final_ticket"])},
            "learning_event": {"state_id": "fixture-state", "production_change_authorized": False},
            "automatic_next_race_learning_state": {"state_id": "fixture-next-race"},
        }, phase="RESULT", status="PASS", timestamp=datetime.now(timezone.utc).isoformat())

    def result_page(spec, _):
        day = datetime.fromisoformat(intent["scheduled_post_at"])
        html = f"<h2>{day.year}年{day.month}月{day.day}日 川崎第1競走競走成績</h2>"
        html += "<table><tr><th>着順</th><th>馬番</th><th>馬名</th></tr>"
        html += "".join(f"<tr><td>{i}</td><td>{i}</td><td>Fixture-{i}</td></tr>" for i in (1, 2, 3))
        html += "</table><table>"
        for name, selection, amount in (("馬連単", "1-2", 500), ("三連複", "1-2-3", 900), ("三連単", "1-2-3", 1600)):
            html += f"<tr><td>{name}</td><td>{selection}</td><td>{amount}円</td><td>1人気</td></tr>"
        calls.append("OFFICIAL")
        return snapshot_from_bytes(spec, (html + "</table>").encode(), final_url=spec["url"],
                                   status_code=200, headers={"content-type": "text/html; charset=utf-8"})

    monkeypatch.setattr(transport.gateway, "request_json", gateway_fixture)
    token = orchestrator.PRIVATE_CHECKPOINT.set(private)
    try:
        with pytest.raises(orchestrator.FormalOrchestrationError,
                           match="PRIVATE_NANKAN_OFFICIAL_RESULT_ADAPTER_REQUIRED"):
            orchestrator.acquire_official_result_request(
                intent, run_id="fixture", github_sha="FIXTURE", tmp_root=result_output, fetch=result_page)
        assert "OFFICIAL" not in calls

        # Seed an already persisted legacy result fixture. Settlement and
        # idempotent recovery still work without a new NAR request.
        ctx = source["artifact"]["source_race_context"]
        spec = _result_source("KAW", LOCAL_BABA_CODES["KAW"],
                                        ctx["race_date"].replace("-", "/"), ctx["race_no"])
        snapshot, errors = result_page(spec, None)
        assert not errors
        order, payouts = orchestrator.parse_official_result_snapshot(snapshot, ctx, ["1", "2", "3"])
        official = {
            "family_id": "LOCAL", "execution_id": eid, "race_id": eid, "phase": "RESULT",
            "execution_phase": "RESULT", "temporal_mode": "RESULT", "finish_order": order, "payouts": payouts,
            "result_available_at": snapshot["fetched_at"],
            "result_timestamp_authority": "OBSERVED_AT_OFFICIAL_RETRIEVAL_PUBLICATION_TIME_UNKNOWN",
            "source": spec["url"], "official_result_verified": True,
            "official_result_verification_ref": spec["url"] + "#sha256=" + snapshot["raw_sha256"],
            "frozen_final_sha256": digest(signed_final), "official_snapshot_sha256": snapshot["snapshot_sha256"],
            "source_binding": orchestrator._source_binding_from_resolved(source_resolved),
            "pfs_authority": "FROZEN-RECOMMENDATION",
        }
        out = private.output_directory(private.work_root / eid / "official-archived", create=True)
        private.write(out / "official_result_request.json", official)
        private.write(out / "official_result_snapshot.json", snapshot)
        private.persist(eid, "OFFICIAL_RESULT", snapshot["snapshot_sha256"], out, github_sha="FIXTURE")
    finally:
        orchestrator.PRIVATE_CHECKPOINT.reset(token)
    for index in (1, 2):
        private = transport.PrivateCheckpoint(binding, pin)
        token = orchestrator.PRIVATE_CHECKPOINT.set(private)
        try:
            report = local_race_entry.run({**intent, "execution_phase": "OFFICIAL_RESULT"},
                                          output=result_output, run_id=f"result-{index}", github_sha="FIXTURE")
        finally:
            orchestrator.PRIVATE_CHECKPOINT.reset(token)
        assert report["phase"] == "RESULT"
        if interrupted:
            assert not report["completion"]["complete"]
        else:
            assert report["completion"]["complete"], report["completion"]
            summary = json.loads((result_output / "result" / "result_summary.json").read_bytes())
            assert (summary["investment"], summary["return"], summary["pfs"]) == (400, 2300, 575.0)
            learning = json.loads((result_output / "result" / "learning_state.json").read_bytes())
            assert learning["automatic_next_race_learning_state"] == {"state_id": "fixture-next-race"}
    assert calls.count("OFFICIAL") == calls.count("RESULT") == 1
    assert store.resolve_phase(eid, "OFFICIAL_RESULT") is None and store.resolve_phase(eid, "RESULT") is None
    assert (private.resolve(eid, "RESULT") is None) == interrupted

"""Owner-only checkpoint transport for already authorized, signed LOCAL KAW data."""
from __future__ import annotations

import base64
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile
from urllib.parse import urlsplit

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from runtime import execution_gateway as gateway
from runtime import execution_store as store
from runtime.family_authority_guard import resolve_current_authority
from runtime.local_physical.nar_source_manifest import (
    LOCAL_BABA_CODES, PROFILE as NAR_PROFILE, _result_source,
)
from runtime.local_physical import nankan_kaw_source
from runtime.local_physical.source_acquisition import verify_source_artifact

ROOT = Path(__file__).resolve().parents[1]
BINDING_ENV = "KM_LOCAL_PRIVATE_CHECKPOINT_BINDING"
BINDING_SHA_ENV = "KM_LOCAL_PRIVATE_CHECKPOINT_BINDING_SHA256"
PRIVATE_PHASES = {"SOURCE", "FORMAL", "OFFICIAL_RESULT", "RESULT"}


def _require(condition, code):
    if not condition:
        raise store.ExecutionStoreError(code)


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def _time(value):
    try:
        stamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if stamp.utcoffset() is not None:
            return stamp
    except ValueError:
        pass
    raise store.ExecutionStoreError("PRIVATE_SOURCE_TIMESTAMP_INVALID")


def private_directory(path, *, create=False):
    path = Path(path)
    chain = (path, *path.parents)
    _require(path.is_absolute() and ".." not in path.parts and
             not any(p.is_symlink() or (p / ".git").exists() for p in chain) and
             not any(part in {".github", "public", "dist"} for part in path.parts),
             "PRIVATE_CHECKPOINT_PATH_FORBIDDEN")
    if create:
        path.mkdir(mode=0o700, exist_ok=True)
    info = path.stat()
    _require(stat.S_ISDIR(info.st_mode) and info.st_uid == os.geteuid() and
             stat.S_IMODE(info.st_mode) == 0o700, "PRIVATE_CHECKPOINT_DIRECTORY_NOT_OWNER_ONLY")
    return path


def private_file(path):
    info = path.lstat()
    _require(stat.S_ISREG(info.st_mode) and info.st_uid == os.geteuid() and
             stat.S_IMODE(info.st_mode) == 0o600 and info.st_nlink == 1,
             "PRIVATE_CHECKPOINT_FILE_NOT_OWNER_ONLY")
    return path


def code_sha256():
    files = ("execution_gateway.py", "execution_store.py", "family_authority_guard.py",
             "formal_execution_orchestrator.py", "local_prestart_gate.py", "local_private_checkpoint.py",
             "local_race_entry.py", "local_race_key_gate.py", "local_static_input_resolver.py",
             "non_jra_formal_runner.py", "local_physical/nankan_kaw_source.py",
             "local_physical/source_acquisition.py", "urw_nankan_reference_source.py",
             "urw_reference_source_policy.py", "local_nar_evidence_candidate.py",
             "local_production_static_owner.py")
    return _sha(_json({name: _sha((ROOT / "runtime" / name).read_bytes()) for name in files}))


class PrivateCheckpoint:
    def __init__(self, binding_path, expected_sha):
        _require(not os.environ.get("GITHUB_ACTIONS") and not os.environ.get("CI"),
                 "PRIVATE_CHECKPOINT_CI_FORBIDDEN")
        path = Path(binding_path)
        self.root = private_directory(path.parent)
        _require(not any(self.root.is_relative_to(Path(p)) for p in ("/tmp", "/var/tmp", "/dev/shm")),
                 "PRIVATE_CHECKPOINT_PERSISTENT_ROOT_REQUIRED")
        raw = private_file(path).read_bytes()
        _require(_sha(raw) == expected_sha, "PRIVATE_CHECKPOINT_BINDING_SHA_MISMATCH")
        self.binding_path = path
        self.binding_sha = expected_sha
        self.binding = json.loads(raw)
        b = self.binding
        _require(isinstance(b, dict), "PRIVATE_CHECKPOINT_BINDING_INVALID")
        _require(b.get("schema") == "KM-LOCAL-PRIVATE-CHECKPOINT-BINDING-v1" and b.get("venue_id") == "KAW" and
                 b.get("code_sha256") == code_sha256(), "PRIVATE_CHECKPOINT_BINDING_SCOPE_OR_CODE_INVALID")
        authority_path, _ = resolve_current_authority()
        _require(_sha(authority_path.read_bytes()) == b.get("policy_sha256"),
                 "PRIVATE_CHECKPOINT_AUTHORITY_SHA_MISMATCH")
        self.gateway = gateway.load_gateway()
        self.config = gateway.family_config("LOCAL", self.gateway)
        _require(b.get("gateway_endpoint") == self.config["external_endpoint"] and
                 b.get("gateway_sha256") == _sha((ROOT / "profiles/current_execution_gateway.json").read_bytes()),
                 "PRIVATE_CHECKPOINT_GATEWAY_BINDING_MISMATCH")
        _require(_time(b.get("valid_from")) <= datetime.now(timezone.utc) < _time(b.get("retain_until")) and
                 _time(b.get("valid_from")) < _time(b.get("valid_until")) <= _time(b.get("retain_until")),
                 "PRIVATE_CHECKPOINT_BINDING_OUTSIDE_RETENTION")
        proof = str(b.get("permission_file") or "")
        _require(proof not in {"", ".", "..", path.name, store.PRIVATE_MARKER} and Path(proof).name == proof and
                 _sha(private_file(self.root / proof).read_bytes()) == b.get("permission_sha256") and
                 b.get("private_storage_and_authorized_runtime_processing") is True and
                 isinstance(b.get("source_url_prefixes"), dict) and bool(b["source_url_prefixes"]),
                 "PRIVATE_CHECKPOINT_PROVIDER_RIGHTS_REQUIRED")
        self.store_root = private_directory(self.root / "checkpoints", create=True)
        self.work_root = private_directory(self.root / "work", create=True)
        self._key = None
        self._runtime_hashes = None
        marker = self.root / store.PRIVATE_MARKER
        try:
            fd = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            private_file(marker)
        else:
            os.close(fd)

    @classmethod
    def from_env(cls):
        path = os.environ.get(BINDING_ENV)
        pin = os.environ.get(BINDING_SHA_ENV)
        if not path and not pin:
            return None
        _require(path and pin, "PRIVATE_CHECKPOINT_BINDING_REQUIRED")
        return cls(path, pin)

    def directory(self, path, *, create=False):
        path = Path(path)
        _require(path.is_relative_to(self.root) and path != self.root and ".." not in path.parts,
                 "PRIVATE_CHECKPOINT_PATH_OUTSIDE_ROOT")
        for parent in reversed(path.parents):
            if parent != self.root and parent.is_relative_to(self.root):
                private_directory(parent, create=create)
        return private_directory(path, create=create)

    def output_directory(self, path, *, create=False):
        path = Path(path)
        _require(path.is_relative_to(self.work_root) and path != self.work_root,
                 "PRIVATE_CHECKPOINT_OUTPUT_MUST_BE_IN_WORK_ROOT")
        return self.directory(path, create=create)

    def write(self, path, value):
        self.directory(path.parent, create=True)
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temp:
            pending = Path(temp.name)
            try:
                temp.write(_json(value))
                temp.flush()
                os.fsync(temp.fileno())
                temp.close()
                os.replace(pending, path)
                store._sync_directory(path.parent)
            finally:
                pending.unlink(missing_ok=True)

    def _identity(self, execution_id):
        _require(re.fullmatch(r"KM-LOCAL-KAW-\d{8}-R(?:0[1-9]|1[0-2])-LIVE-R[1-9]\d*", execution_id),
                 "PRIVATE_CHECKPOINT_EXECUTION_ID_INVALID")

    @contextmanager
    def race_lock(self, execution_id):
        self._identity(execution_id)
        directory = self.directory(self.store_root / execution_id, create=True)
        fd = os.open(directory / ".race.lock", os.O_CREAT | os.O_NOFOLLOW | os.O_RDWR, 0o600)
        with os.fdopen(fd, "rb") as lock:
            private_file(directory / ".race.lock")
            fcntl.flock(lock, fcntl.LOCK_EX)
            yield

    def _signer(self):
        if self._key is None:
            endpoint = self.config["external_endpoint"].rstrip("/")
            http, health = gateway.request_json(endpoint + "/health", method="GET", timeout=20, attempts=1)
            _require(http < 300 and gateway.assess_runtime_health(health, "LOCAL", self.gateway)["status"] == "PASS" and
                     health.get("github_revision") == self.binding.get("signer_runtime_revision"),
                     "PRIVATE_CHECKPOINT_GATEWAY_HEALTH_REQUIRED")
            key = base64.b64decode(health["receipt_public_key_b64"], validate=True)
            _require(_sha(key) == self.binding.get("signer_public_key_sha256"),
                     "PRIVATE_CHECKPOINT_SIGNER_KEY_PIN_MISMATCH")
            self._key = Ed25519PublicKey.from_public_bytes(key)
            self._runtime_hashes = {name: health[name] for name in
                                    ("legacy_runtime_app_sha256", "source_acquisition_sha256",
                                     "nar_source_manifest_sha256", "nar_runner_universe_sha256")}
            self._runtime_hashes["runtime_wrapper_sha256"] = health["runtime_app_sha256"]
        return self._key

    def _verify_signature(self, envelope, execution_id, phase, status):
        receipt = envelope["receipt"]
        artifact = envelope["artifact"]
        _require(receipt.get("race_id") == execution_id and receipt.get("family") == "LOCAL" and
                 receipt.get("phase") == phase and receipt.get("status") == status and not receipt.get("errors") and
                 receipt.get("github_revision") == self.binding.get("signer_runtime_revision") and
                 receipt.get("engine_sha256") == self.config["engine_sha256"] and
                 receipt.get("parameter_map_sha256") == self.config["parameter_map_sha256"] and
                 envelope.get("signature_alg") == "Ed25519" and
                 envelope.get("signer_key_id") == self.config["receipt_signer_key_id"] and
                 _sha(_json(receipt)) == envelope.get("receipt_sha256") and
                 _sha(_json(artifact)) == receipt.get("artifact_sha256"),
                 "PRIVATE_CHECKPOINT_RECEIPT_BINDING_INVALID")
        try:
            self._signer().verify(base64.b64decode(envelope["signature"], validate=True), _json(receipt))
        except (InvalidSignature, ValueError) as exc:
            if isinstance(exc, store.ExecutionStoreError):
                raise
            raise store.ExecutionStoreError("PRIVATE_CHECKPOINT_SIGNATURE_INVALID") from None
        _require(all((receipt.get("runtime_hashes") or {}).get(k) == v for k, v in self._runtime_hashes.items()),
                 "PRIVATE_CHECKPOINT_RECEIPT_RUNTIME_HASH_MISMATCH")

    def _verify_source(self, envelope, basis):
        execution_id = basis["race_id"]
        self._identity(execution_id)
        artifact = envelope["artifact"]
        context = artifact["source_race_context"]
        _require(basis.get("family_id") == "LOCAL" and basis.get("venue_id") == context.get("venue_id") == "KAW" and
                 basis.get("race_date") == str(context.get("race_date")).replace("/", "-") and
                 basis.get("race_no") == context.get("race_no") and
                 artifact.get("race_id") == execution_id and
                 execution_id.split("-")[3:5] == [basis["race_date"].replace("-", ""), f'R{basis["race_no"]:02d}'],
                 "PRIVATE_SOURCE_RACE_CONTEXT_MISMATCH")
        profile = artifact.get("source_manifest_profile")
        expected_profile = basis.get("source_manifest_profile")
        _require((profile == NAR_PROFILE and expected_profile is None)
                 or profile == expected_profile == nankan_kaw_source.PROFILE,
                 "PRIVATE_SOURCE_CONSUMER_NOT_AUTHORIZED")
        official_authority = "NAR_OFFICIAL"
        if profile == nankan_kaw_source.PROFILE:
            official_authority = nankan_kaw_source.PROVIDER
            _require(set(self.binding["source_url_prefixes"]) == {official_authority},
                     "PRIVATE_SOURCE_NANKAN_EXCLUSIVE_PERMISSION_REQUIRED")
            _require(_time(artifact.get("scheduled_post_at")) == _time(basis.get("scheduled_post_at")),
                     "PRIVATE_SOURCE_NANKAN_SCHEDULE_MISMATCH")
            try:
                nankan_kaw_source.verify(artifact)
            except (KeyError, TypeError, ValueError, OSError) as exc:
                raise store.ExecutionStoreError("PRIVATE_SOURCE_NANKAN_ARTIFACT_INVALID") from exc
        now = datetime.now(timezone.utc)
        frozen, signed, cutoff = (_time(artifact["source_freeze_at"]), _time(envelope["receipt"]["timestamp"]),
                                  _time(artifact["prediction_cutoff"]))
        start, end = _time(self.binding["valid_from"]), _time(self.binding["valid_until"])
        _require(cutoff == _time(basis["prediction_cutoff"]) and start <= frozen <= signed <= now and
                 signed < min(end, cutoff) and
                 basis.get("explicit_source_manifest_sha256") in (None, artifact.get("required_source_manifest_sha256")),
                 "PRIVATE_SOURCE_TIMING_OR_MANIFEST_INVALID")
        bundle = [{k: s.get(k) for k in ("source_id", "raw_sha256", "snapshot_sha256", "fetched_at", "final_url")}
                  for s in artifact["sources"]]
        _require(verify_source_artifact(artifact)[0] and artifact.get("formal_ready") is True
                 and not artifact.get("errors") and
                 _sha(_json(bundle)) == artifact.get("raw_source_bundle_sha256") and
                 _sha(_json(artifact["required_source_manifest"])) == artifact.get("required_source_manifest_sha256"),
                 "PRIVATE_SOURCE_RAW_OR_SNAPSHOT_HASH_INVALID")
        active = artifact["official_runner_universe"]
        statuses = artifact["runner_status_registry"]
        active_ids = [str(r["runner_id"]) for r in active["runners"]]
        status_ids = [str(r["runner_id"]) for r in statuses]
        declared_ids = [str(r["runner_id"]) for r in artifact["declared_runner_universe"]["runners"]]
        _require(active == artifact.get("active_runner_universe") and active["universe_type"] == "ACTIVE" and
                 active_ids and len(set(active_ids)) == len(active_ids) == active["runner_count"] and
                 len(set(status_ids)) == len(status_ids) == len(declared_ids) and
                 set(status_ids) == set(declared_ids) and
                 all(r["status"] in {"ACTIVE", "CANCELLED", "INACTIVE"} for r in statuses) and
                 set(active_ids) == {str(r["runner_id"]) for r in statuses if r["status"] == "ACTIVE"} and
                 active["status_registry_sha256"] == artifact["runner_status_registry_sha256"] == _sha(_json(statuses)) and
                 active["runner_universe_sha256"] == artifact["official_runner_universe_sha256"] ==
                 _sha(_json({k: v for k, v in active.items() if k != "runner_universe_sha256"})),
                 "PRIVATE_SOURCE_ACTIVE_UNIVERSE_INVALID")
        snapshots = [s for s in artifact["sources"] if "raw_gzip_b64" in s]
        card = [s for s in snapshots if s.get("source_class") == "OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT"]
        odds = [s for s in snapshots if s.get("source_class") == "OFFICIAL_ACTIVE_BETTING_UNIVERSE"]
        required = {s["source_id"] for s in artifact["required_source_manifest"] if s.get("required") is True}
        _require(len(card) == len(odds) == 1 and
                 all(s.get("authority") == official_authority and s.get("official") is True and
                     s["source_id"] in required for s in (*card, *odds)) and
                 card[0].get("source_id") == active.get("source_id") and
                 card[0].get("snapshot_sha256") == active.get("source_snapshot_sha256"),
                 "PRIVATE_SOURCE_OFFICIAL_CARD_OR_ODDS_BINDING_INVALID")
        source_ids = {s["source_id"] for s in snapshots}
        _require(required <= source_ids and len(source_ids) == len(snapshots) and
                 all(r["evidence_sources"] and set(r["evidence_sources"]) <= source_ids for r in statuses) and
                 all(odds[0]["source_id"] in r["evidence_sources"] for r in statuses if r["status"] == "ACTIVE"),
                 "PRIVATE_SOURCE_ACTIVE_EVIDENCE_MISSING")
        for source in snapshots:
            self._check_snapshot_scope(source, start, frozen)
        self._verify_signature(envelope, execution_id, "SOURCE", "SOURCE_FROZEN")

    def _check_snapshot_scope(self, source, start, frozen):
        _require(source.get("source_id") and
                 start <= _time(source.get("fetched_at")) <= frozen, "PRIVATE_SOURCE_PROVIDER_SCOPE_INVALID")
        for label in ("requested_url", "final_url"):
            _require(self.allows_source_endpoint(source.get("authority"), source[label]),
                     "PRIVATE_SOURCE_ENDPOINT_OUTSIDE_PERMISSION")

    def allows_source_endpoint(self, authority, address):
        prefixes = self.binding["source_url_prefixes"].get(authority)
        if not isinstance(prefixes, list) or not prefixes:
            return False
        url = urlsplit(address)
        return (url.scheme == "https" and not url.username and not url.password and not url.fragment
                and not any(c in url.path for c in ("%", "\\", "/../", "/./"))
                and not url.path.endswith(("/..", "/."))
                and any(url.netloc == p.netloc and url.path.startswith(p.path)
                        for p in map(urlsplit, prefixes) if p.scheme == "https" and p.path.endswith("/")
                        and not p.query and not p.fragment))

    def resolve(self, execution_id, phase):
        self._identity(execution_id)
        _require(phase in PRIVATE_PHASES, "PRIVATE_CHECKPOINT_PHASE_UNSUPPORTED")
        phase_path = self.store_root / execution_id / phase
        if not phase_path.exists() and not phase_path.is_symlink():
            return None
        self.directory(phase_path)
        pointer = phase_path / "LATEST.json"
        if not pointer.exists() and not pointer.is_symlink():
            return None
        run_id = json.loads(private_file(pointer).read_bytes())["run_id"]
        _require(re.fullmatch(r"[A-Za-z0-9_-][A-Za-z0-9_.-]{0,179}", run_id),
                 "PRIVATE_CHECKPOINT_RUN_ID_INVALID")
        candidate = self.directory(phase_path / "runs" / run_id)
        inventory = json.loads(private_file(candidate / "manifest.json").read_bytes())["files"]
        for name in inventory:
            _require(Path(name).name == name and name not in {"", ".", ".."},
                     "PRIVATE_CHECKPOINT_INVENTORY_PATH_INVALID")
            private_file(candidate / name)
        run_path = json.loads(pointer.read_bytes()).get("run_path")
        _require(run_path == str(candidate.relative_to(self.store_root)), "PRIVATE_CHECKPOINT_POINTER_PATH_INVALID")
        result = store.resolve_phase(execution_id, phase, root=self.store_root)
        _require(result is not None and result["run_dir"] == candidate,
                 "PRIVATE_CHECKPOINT_POINTER_CHANGED")
        path = self.directory(result["run_dir"])
        _require(result["manifest"].get("storage_scope") == "PRIVATE" and
                 json.loads(private_file(path / "private_checkpoint_binding.json").read_bytes()) ==
                 {"binding_sha256": self.binding_sha}, "PRIVATE_CHECKPOINT_STORED_BINDING_MISMATCH")
        self._verify_phase(path, phase, execution_id)
        return result

    def _verify_phase(self, path, phase, execution_id):
        def read(name):
            return json.loads(private_file(path / name).read_bytes())

        if phase == "SOURCE":
            basis = read("source_checkpoint_basis.json")
            _require(basis["race_id"] == execution_id, "PRIVATE_SOURCE_EXECUTION_ID_MISMATCH")
            self._verify_source(read("source_receipt_envelope.json"), basis)
        elif phase == "FORMAL":
            self._verify_final(read("final_receipt_envelope.json"), execution_id)
        elif phase == "OFFICIAL_RESULT":
            self._verify_official_result(read("official_result_request.json"),
                                         read("official_result_snapshot.json"), execution_id)
        else:
            request, final = self._result_inputs(execution_id)
            expected, _ = store.build_local_result_payload(request, final)
            _require(read("result_checkpoint_basis.json") == {"request_sha256": _sha(_json(request))},
                     "PRIVATE_RESULT_REQUEST_CHANGED")
            self._verify_result(read("result_receipt_envelope.json"), final, expected)

    def _verify_final(self, final, execution_id):
        self._verify_signature(final, execution_id, "FINAL", "PASS")
        source = self.resolve(execution_id, "SOURCE")
        _require(source is not None, "PRIVATE_FINAL_SIGNED_SOURCE_REQUIRED")
        envelope = json.loads((source["run_dir"] / "source_receipt_envelope.json").read_bytes())
        artifact = final["artifact"]
        source_artifact = envelope["artifact"]
        _require(artifact.get("source_receipt_sha256") == envelope["receipt_sha256"] and
                 artifact.get("source_snapshot_sha256") == source_artifact["source_snapshot_sha256"] and
                 _time(envelope["receipt"]["timestamp"]) <= _time(artifact["final_freeze_timestamp"]) <=
                 _time(final["receipt"]["timestamp"]) < _time(source_artifact["prediction_cutoff"]) and
                 _time(final["receipt"]["timestamp"]) <= datetime.now(timezone.utc),
                 "PRIVATE_FINAL_SOURCE_OR_TIME_BINDING_MISMATCH")

    def _verify_official_result(self, request, snapshot, execution_id):
        from runtime.formal_execution_orchestrator import (
            _official_post_from_source, _source_binding_from_resolved, parse_official_result_snapshot,
        )

        source = self.resolve(execution_id, "SOURCE")
        final = self.resolve(execution_id, "FORMAL")
        _require(source is not None and final is not None, "PRIVATE_RESULT_FROZEN_FINAL_REQUIRED")
        source_artifact = json.loads(private_file(source["run_dir"] /
                                                  "source_receipt_envelope.json").read_bytes())["artifact"]
        final_envelope = json.loads(private_file(final["run_dir"] / "final_receipt_envelope.json").read_bytes())
        context = source_artifact["source_race_context"]
        source_basis = _source_binding_from_resolved(source)
        post = _official_post_from_source({}, source)
        spec = _result_source("KAW", LOCAL_BABA_CODES["KAW"], context["race_date"].replace("-", "/"),
                              context["race_no"])
        observed = _time(snapshot["fetched_at"])
        self._check_snapshot_scope(snapshot, _time(self.binding["valid_from"]), datetime.now(timezone.utc))
        _require(request.get("race_id") == request.get("execution_id") == execution_id and
                 request.get("family_id") == "LOCAL" and request.get("execution_phase") == "RESULT" and
                 request.get("official_result_verified") is True and request.get("pfs_authority") == "FROZEN-RECOMMENDATION" and
                 request.get("source_binding") == source_basis and
                 request.get("frozen_final_sha256") == _sha(_json(final_envelope)) and
                 snapshot["requested_url"] == snapshot["final_url"] == request.get("source") == spec["url"] and
                 snapshot.get("authority") == spec["authority"] and snapshot.get("source_id") == spec["source_id"] and
                 post is not None and post <= observed < _time(self.binding["valid_until"]) and
                 request.get("result_available_at") == snapshot["fetched_at"] and
                 request.get("official_snapshot_sha256") == snapshot.get("snapshot_sha256") ==
                 _sha(_json({k: v for k, v in snapshot.items() if k != "snapshot_sha256"})),
                 "PRIVATE_RESULT_OFFICIAL_SNAPSHOT_BINDING_INVALID")
        active = [r["runner_id"] for r in source_artifact["active_runner_universe"]["runners"]]
        order, payouts = parse_official_result_snapshot(snapshot, context, active)
        _require(request.get("finish_order") == order and request.get("payouts") == payouts,
                 "PRIVATE_RESULT_OFFICIAL_OUTCOME_CHANGED")

    def _result_inputs(self, execution_id):
        official = self.resolve(execution_id, "OFFICIAL_RESULT")
        final = self.resolve(execution_id, "FORMAL")
        _require(official is not None and final is not None, "PRIVATE_RESULT_OFFICIAL_OR_FINAL_REQUIRED")
        return (json.loads(private_file(official["run_dir"] / "official_result_request.json").read_bytes()),
                json.loads(private_file(final["run_dir"] / "final_receipt_envelope.json").read_bytes()))

    def _verify_result(self, envelope, final, expected):
        self._verify_signature(envelope, expected["race_id"], "RESULT", "PASS")
        _require(_time(expected["result_available_at"]) <= _time(envelope["receipt"]["timestamp"])
                 <= datetime.now(timezone.utc), "PRIVATE_RESULT_RECEIPT_TIMESTAMP_INVALID")
        frozen_ticket = final["artifact"].get("final_ticket") or {}
        _require((envelope["artifact"].get("frozen_refs") or {}).get("final_ticket_sha256")
                 == _sha(_json(frozen_ticket)), "PRIVATE_RESULT_FINAL_TICKET_CHANGED")
        return store.verify_result_reuse(envelope, final, expected, {"verified": True})

    def settle_result(self, request, directory, *, github_sha):
        from runtime.race_day_fast_reflection import build_fast_reflection

        execution_id = request["execution_id"]
        self._identity(execution_id)
        self.require_formal_execution(execution_id)
        official, final = self._result_inputs(execution_id)
        _require(request == official, "PRIVATE_RESULT_REQUEST_CHANGED")
        payload, by_type = store.build_local_result_payload(official, final)
        exchange = self.output_directory(self.work_root / execution_id / "result_exchange", create=True)
        claim = exchange / "request.sha256"
        saved = exchange / "receipt.json"
        payload_sha = _sha(_json(payload))
        try:
            fd = os.open(claim, os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_WRONLY, 0o600)
        except FileExistsError:
            _require(private_file(claim).read_text() == payload_sha, "PRIVATE_RESULT_REQUEST_CHANGED")
            _require(saved.exists() or saved.is_symlink(), "PRIVATE_RESULT_SUBMISSION_OUTCOME_UNCONFIRMED")
            envelope = json.loads(private_file(saved).read_bytes())
        else:
            with os.fdopen(fd, "w") as record:
                record.write(payload_sha)
                record.flush()
                os.fsync(record.fileno())
            store._sync_directory(exchange)
            _require(not saved.exists() and not saved.is_symlink(), "PRIVATE_RESULT_UNEXPECTED_RECEIPT")
            endpoint = self.config["external_endpoint"].rstrip("/")
            http, envelope = gateway.request_json(endpoint + "/result", method="POST", payload=payload,
                                                  timeout=180, attempts=1)
            _require(http < 300, "PRIVATE_RESULT_SUBMISSION_OUTCOME_UNCONFIRMED")
            self.write(saved, envelope)
        self._verify_result(envelope, final, payload)
        artifact = envelope["artifact"]
        settlement = artifact["settlement"]
        investment, total_return = settlement["investment"], settlement["return"]
        reflection = build_fast_reflection(artifact, race_id=execution_id)
        identity = {"race_id": execution_id, "execution_id": execution_id}
        self.write(directory / "result_receipt_envelope.json", envelope)
        self.write(directory / "receipt_verifications.json", {"FINAL": True, "RESULT": True})
        self.write(directory / "result_checkpoint_basis.json", {"request_sha256": _sha(_json(request))})
        self.write(directory / "race_day_fast_reflection.json", reflection)
        self.write(directory / "result_summary.json", {
            **identity, "verified": True, "result_receipt": envelope["receipt_sha256"],
            "investment": investment, "return": total_return, "profit_loss": total_return - investment,
            "pfs": None if investment == 0 else round(total_return / investment * 100, 6),
            "pfs_authority": payload["pfs_authority"], "by_type": by_type,
            "winning_tickets": payload["settlement"]["winning_tickets"],
        })
        self.write(directory / "learning_state.json", {
            **identity, "final_receipt_sha256": final["receipt_sha256"],
            "result_receipt_sha256": envelope["receipt_sha256"], "learning_event": artifact.get("learning_event"),
            "automatic_next_race_learning_state": artifact.get("automatic_next_race_learning_state"),
            "failure_localization": artifact.get("failure_localization"),
            "automatic_post_result_review": artifact.get("automatic_post_result_review"),
            "production_policy_change": False, "actual_purchase_pfs": "UNKNOWN_UNLESS_VERIFIED",
        })
        self.write(directory / "forward_tracker_terminal.json", {
            **identity, "status": "HOLD", "reason": "PRIVATE_FORWARD_TRACKER_NOT_REGISTERED",
            "research_failure_nonblocking": True, "production_effect": "NONE",
        })
        return self.persist(execution_id, "RESULT", envelope["receipt_sha256"], directory, github_sha=github_sha)

    def require_current_processing(self):
        _require(datetime.now(timezone.utc) < _time(self.binding["valid_until"]),
                 "PRIVATE_SOURCE_PROCESSING_PERMISSION_EXPIRED")

    def require_formal_execution(self, execution_id):
        self.require_current_processing()
        approved = self.binding.get("formal_execution_ids")
        proof = self.binding.get("formal_runtime_approval_file") or ""
        _require(isinstance(approved, list) and execution_id in approved and
                 proof not in {"", ".", "..", self.binding_path.name, store.PRIVATE_MARKER} and
                 Path(proof).name == proof and
                 _sha(private_file(self.root / proof).read_bytes()) ==
                 self.binding.get("formal_runtime_approval_sha256") and self.binding.get("cost_control_ref"),
                 "PRIVATE_FORMAL_EXECUTION_APPROVAL_REQUIRED")

    def import_source(self, path, basis, *, github_sha):
        if basis.get("source_manifest_profile") == nankan_kaw_source.PROFILE:
            self.require_nankan_source_approval(basis["race_id"])
        else:
            self.require_current_processing()
        if path.parent == self.root:
            private_directory(self.root)
        else:
            self.directory(path.parent)
        payload = private_file(path).read_bytes()
        return self._persist_source_bytes(payload, basis, github_sha=github_sha)

    def require_nankan_source_approval(self, execution_id):
        self._identity(execution_id)
        self.require_formal_execution(execution_id)
        _require(set(self.binding["source_url_prefixes"]) == {nankan_kaw_source.PROVIDER},
                 "PRIVATE_SOURCE_NANKAN_EXCLUSIVE_PERMISSION_REQUIRED")

    def produce_nankan_source(self, basis, sign, *, github_sha):
        """Operator entry on the authorized signer host, with no public signing route."""
        execution_id = basis["race_id"]
        self.require_nankan_source_approval(execution_id)
        _require(basis.get("source_manifest_profile") == nankan_kaw_source.PROFILE
                 and basis.get("explicit_source_manifest_sha256") is None,
                 "PRIVATE_SOURCE_NANKAN_AUTODISCOVERY_BASIS_REQUIRED")
        from runtime.urw_nankan_reference_source import Client, url_scope

        with self.race_lock(execution_id):
            prior = self.resolve(execution_id, "SOURCE")
            if prior:
                _require(json.loads(private_file(prior["run_dir"] /
                                                "source_checkpoint_basis.json").read_bytes()) == basis,
                         "PRIVATE_SOURCE_ACQUISITION_BASIS_INVALID")
                return {"status": "REUSED", "receipt_sha256": prior["manifest"]["run_id"]}
            client = Client(cache=self.directory(self.work_root / "nankan-source-policy", create=True))

            def get(url):
                url_scope(url)
                _require(self.allows_source_endpoint(nankan_kaw_source.PROVIDER, url),
                         "PRIVATE_SOURCE_ENDPOINT_OUTSIDE_PERMISSION")
                return client.get(url)

            # Verify the existing gateway/key pin before contacting the provider.
            self._signer()
            artifact = nankan_kaw_source.acquire(basis, get)
            with tempfile.TemporaryDirectory(dir=self.work_root) as staging:
                path = Path(staging) / "nankan-source.json"
                self.write(path, artifact)
                saved_bytes = private_file(path).read_bytes()
                _require(saved_bytes == _json(artifact), "PRIVATE_SOURCE_NANKAN_READBACK_CHANGED")
                stored = json.loads(saved_bytes)
                nankan_kaw_source.verify(stored)
                _require(datetime.now(timezone.utc) < _time(basis["prediction_cutoff"]),
                         "PRIVATE_SOURCE_NANKAN_CUTOFF_PASSED")
                envelope = sign("SOURCE", execution_id, "SOURCE_FROZEN", stored, [])
                self._persist_source_bytes(_json(envelope), basis, github_sha=github_sha)
            return {"status": "PASS", "receipt_sha256": envelope["receipt_sha256"]}

    def acquire_source(self, basis, *, github_sha):
        execution_id = basis["race_id"]
        self._identity(execution_id)
        self.require_formal_execution(execution_id)
        _require(basis.get("family_id") == "LOCAL" and basis.get("venue_id") == "KAW" and
                 execution_id.split("-")[3:5] ==
                 [basis["race_date"].replace("-", ""), f'R{basis["race_no"]:02d}'] and
                 datetime.now(timezone.utc) < _time(basis["prediction_cutoff"]) and
                 basis.get("explicit_source_manifest_sha256") is None,
                 "PRIVATE_SOURCE_ACQUISITION_BASIS_INVALID")
        # Live NANKAN bytes enter through the owner-bound signed private import.
        # The current public signer has no permission-scoped NANKAN acquisition API.
        raise store.ExecutionStoreError("PRIVATE_NANKAN_SIGNED_SOURCE_IMPORT_REQUIRED")

    def _persist_source_bytes(self, payload, basis, *, github_sha):
        envelope = json.loads(payload)
        self._verify_source(envelope, basis)
        with tempfile.TemporaryDirectory(dir=self.work_root) as staging:
            staging = Path(staging)
            self.write(staging / "source_checkpoint_basis.json", basis)
            self.write(staging / "source_verification.json", {
                "valid": True, "verified": True, "signature_valid": True, "artifact_valid": True,
                "method": "CANONICAL_GATEWAY_HEALTH_ED25519",
            })
            envelope_path = staging / "source_receipt_envelope.json"
            envelope_path.write_bytes(payload)
            envelope_path.chmod(0o600)
            return self.persist(basis["race_id"], "SOURCE", envelope["receipt_sha256"], staging, github_sha=github_sha)

    def persist(self, execution_id, phase, run_id, directory, *, github_sha):
        self._identity(execution_id)
        _require(phase in PRIVATE_PHASES, "PRIVATE_CHECKPOINT_PHASE_UNSUPPORTED")
        _require(re.fullmatch(r"[A-Za-z0-9_-][A-Za-z0-9_.-]{0,179}", run_id),
                 "PRIVATE_CHECKPOINT_RUN_ID_INVALID")
        self.output_directory(directory)
        self._verify_phase(directory, phase, execution_id)
        self.write(directory / "private_checkpoint_binding.json", {"binding_sha256": self.binding_sha})
        files = sorted(private_file(p) for p in directory.glob("*.json") if p.name != "manifest.json")
        phase_path = self.directory(self.store_root / execution_id / phase, create=True)
        runs = self.directory(phase_path / "runs", create=True)
        target = runs / run_id
        if target.exists() or target.is_symlink():
            self.directory(target)
            for path in target.iterdir():
                private_file(path)
        for path in (phase_path / ".write.lock", phase_path / "LATEST.json"):
            if path.exists() or path.is_symlink():
                private_file(path)
        with_lock = phase_path / ".write.lock"
        fd = os.open(with_lock, os.O_CREAT | os.O_NOFOLLOW | os.O_RDWR, 0o600)
        os.close(fd)
        result = store._persist_files(execution_id, phase, run_id, files, self.store_root, github_sha, private=True)
        reopened = self.resolve(execution_id, phase)
        _require(reopened is not None and reopened["run_dir"] == Path(result["path"]),
                 "PRIVATE_CHECKPOINT_INDEPENDENT_READBACK_FAILED")
        return result

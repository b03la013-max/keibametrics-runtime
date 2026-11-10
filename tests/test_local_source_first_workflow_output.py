"""Regression: SOURCE-first entry must write a GitHub Actions output line."""

import json
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_source_first_entry_emits_parseable_execution_id(tmp_path, monkeypatch):
    workflow = yaml.safe_load(
        (ROOT / ".github/workflows/km-local-source-first-entry.yml").read_text(encoding="utf-8")
    )
    steps = workflow["jobs"]["entry"]["steps"]
    step = next(
        step for step in steps
        if step.get("name") == "Execute SOURCE-first entry with explicit hold reporting"
    )
    # Exercise only the workflow's actual intent-to-GITHUB_OUTPUT Python block.
    # Do not invoke the next step, which attempts a real SOURCE request.
    match = re.search(r"python - <<'PY'\n(.*?)\nPY", step["run"], re.S)
    assert match, "SOURCE_FIRST_INTENT_OUTPUT_BLOCK_MISSING"

    execution_id = "KM-LOCAL-KAW-20261110-R01"
    request = {
        "family_id": "LOCAL",
        "execution_phase": "SOURCE",
        "execution_id": execution_id,
    }
    output = tmp_path / "github_output"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GITHUB_EVENT_NAME", "workflow_dispatch")
    monkeypatch.setenv("RACE_REQUEST_JSON", json.dumps(request))
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))

    exec(compile(match.group(1), "<actual-source-first-workflow>", "exec"), {})
    assert output.read_text(encoding="utf-8") == f"execution_id={execution_id}\n"
    assert json.loads((tmp_path / "race-request.json").read_text()) == {**request, "analysis_only": True}


def _git(root, *args):
    import subprocess
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def _source_python():
    workflow = yaml.safe_load(
        (ROOT / ".github/workflows/km-local-source-first-entry.yml").read_text(encoding="utf-8")
    )
    step = next(s for s in workflow["jobs"]["entry"]["steps"]
                if s.get("name") == "Execute SOURCE-first entry with explicit hold reporting")
    match = re.search(r"python - <<'PY'\n(.*?)\nPY", step["run"], re.S)
    assert match
    return compile(match.group(1), "<actual-source-first-push-workflow>", "exec")


def test_source_push_uses_complete_range_not_only_tip_commit(tmp_path, monkeypatch):
    """GitHub's path filter sees every commit; ingress must do the same."""
    import subprocess

    subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, check=True, capture_output=True)
    for key, value in (("user.email", "test@example.invalid"), ("user.name", "LOCAL Test")):
        subprocess.run(["git", "config", key, value], cwd=tmp_path, check=True)

    (tmp_path / "README.md").write_text("base\n")
    subprocess.run(["git", "add", "README.md"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "base"], cwd=tmp_path, check=True, capture_output=True)
    before = _git(tmp_path, "rev-parse", "HEAD")

    execution_id = "KM-LOCAL-KAW-20261110-R01"
    request = {"family_id": "LOCAL", "execution_phase": "SOURCE", "execution_id": execution_id}
    intent = tmp_path / "runtime/source_intents" / (execution_id + ".json")
    intent.parent.mkdir(parents=True)
    intent.write_text(json.dumps(request), encoding="utf-8")
    subprocess.run(["git", "add", str(intent.relative_to(tmp_path))], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "add SOURCE intent"], cwd=tmp_path,
                   check=True, capture_output=True)

    # Regression: the last commit changes only the README. diff-tree HEAD
    # sees no SOURCE intent, although the full push range does.
    (tmp_path / "README.md").write_text("base\nadditional metadata\n")
    subprocess.run(["git", "add", "README.md"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "metadata after intent"], cwd=tmp_path,
                   check=True, capture_output=True)
    after = _git(tmp_path, "rev-parse", "HEAD")
    event = tmp_path / "event.json"
    event.write_text(json.dumps({"before": before, "after": after, "deleted": False}))
    output = tmp_path / "github_output"

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GITHUB_EVENT_NAME", "push")
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(event))
    monkeypatch.setenv("GITHUB_SHA", after)
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    exec(_source_python(), {})
    assert output.read_text() == f"execution_id={execution_id}\n"
    assert json.loads((tmp_path / "race-request.json").read_text()) == {**request, "analysis_only": True}


def test_source_push_rejects_changed_checkout_bytes(tmp_path, monkeypatch):
    """A push event must not execute a request altered after its commit."""
    import subprocess
    import pytest

    subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, check=True, capture_output=True)
    for key, value in (("user.email", "test@example.invalid"), ("user.name", "LOCAL Test")):
        subprocess.run(["git", "config", key, value], cwd=tmp_path, check=True)

    (tmp_path / "README.md").write_text("base\n")
    subprocess.run(["git", "add", "README.md"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "base"], cwd=tmp_path, check=True, capture_output=True)
    before = _git(tmp_path, "rev-parse", "HEAD")

    path = tmp_path / "runtime/source_intents/KM-LOCAL-KAW-20261110-R02.json"
    path.parent.mkdir(parents=True)
    request = {"family_id": "LOCAL", "execution_phase": "SOURCE", "execution_id": path.stem}
    path.write_text(json.dumps(request))
    subprocess.run(["git", "add", str(path.relative_to(tmp_path))], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "add SOURCE intent"], cwd=tmp_path,
                   check=True, capture_output=True)
    after = _git(tmp_path, "rev-parse", "HEAD")

    # The committed request is still intact in Git. Workspace alteration is rejected.
    path.write_text(json.dumps({**request, "execution_id": "KM-LOCAL-KAW-20261110-R03"}))
    event = tmp_path / "event.json"
    event.write_text(json.dumps({"before": before, "after": after, "deleted": False}))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GITHUB_EVENT_NAME", "push")
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(event))
    monkeypatch.setenv("GITHUB_SHA", after)
    monkeypatch.setenv("GITHUB_OUTPUT", str(tmp_path / "github_output"))
    with pytest.raises(RuntimeError, match="REFERENCE_PUSH_REQUEST_CHANGED_AFTER_EVENT"):
        exec(_source_python(), {})
    assert not (tmp_path / "race-request.json").exists()


def test_source_push_fetches_only_missing_before_tree_from_shallow_checkout(tmp_path, monkeypatch):
    """Deep push ranges work with bounded checkout history, even in large repos."""
    import subprocess

    origin = tmp_path / "origin"
    origin.mkdir()
    subprocess.run(["git", "init", "-b", "main"], cwd=origin, check=True, capture_output=True)
    for key, value in (("user.email", "test@example.invalid"), ("user.name", "LOCAL Test")):
        subprocess.run(["git", "config", key, value], cwd=origin, check=True)

    (origin / "README.md").write_text("first\n")
    subprocess.run(["git", "add", "."], cwd=origin, check=True)
    subprocess.run(["git", "commit", "-m", "base"], cwd=origin, check=True, capture_output=True)
    before = _git(origin, "rev-parse", "HEAD")

    execution_id = "KM-LOCAL-KAW-20261110-R05"
    req = {"family_id": "LOCAL", "execution_phase": "SOURCE", "execution_id": execution_id}
    intent = origin / "runtime/source_intents" / (execution_id + ".json")
    intent.parent.mkdir(parents=True)
    intent.write_text(json.dumps(req))
    subprocess.run(["git", "add", "."], cwd=origin, check=True)
    subprocess.run(["git", "commit", "-m", "SOURCE intent"], cwd=origin,
                   check=True, capture_output=True)
    for number in (1, 2):
        (origin / "README.md").write_text("first\n" + "x\n" * number)
        subprocess.run(["git", "add", "."], cwd=origin, check=True)
        subprocess.run(["git", "commit", "-m", f"metadata {number}"], cwd=origin,
                       check=True, capture_output=True)
    after = _git(origin, "rev-parse", "HEAD")

    checkout = tmp_path / "checkout"
    subprocess.run(["git", "clone", "--depth=2", "--branch", "main", origin.as_uri(),
                    str(checkout)], check=True, capture_output=True)
    missing = subprocess.run(["git", "cat-file", "-e", before + "^{tree}"],
                             cwd=checkout, capture_output=True)
    assert missing.returncode != 0, "Test must exercise the missing-before fetch"

    event = checkout / "event.json"
    event.write_text(json.dumps({"before": before, "after": after, "deleted": False}))
    output = checkout / "github_output"
    monkeypatch.chdir(checkout)
    monkeypatch.setenv("GITHUB_EVENT_NAME", "push")
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(event))
    monkeypatch.setenv("GITHUB_SHA", after)
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))

    exec(_source_python(), {})
    assert output.read_text() == f"execution_id={execution_id}\n"
    assert json.loads((checkout / "race-request.json").read_text()) == {**req, "analysis_only": True}
    assert subprocess.run(["git", "cat-file", "-e", before + "^{tree}"],
                          cwd=checkout, capture_output=True).returncode == 0


def test_source_first_rejects_mismatched_race_execution_ids(tmp_path, monkeypatch):
    """Do not materialize a SOURCE request with contradictory race identities."""
    import pytest

    request = {
        "family_id": "LOCAL",
        "execution_phase": "SOURCE",
        "execution_id": "KM-LOCAL-KAW-20261110-R01",
        "race_id": "KM-LOCAL-KAW-20261110-R02",
    }
    output = tmp_path / "github_output"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GITHUB_EVENT_NAME", "workflow_dispatch")
    monkeypatch.setenv("RACE_REQUEST_JSON", json.dumps(request))
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))

    with pytest.raises(SystemExit, match="SOURCE_INTENT_RACE_EXECUTION_ID_MISMATCH"):
        exec(_source_python(), {})
    assert not output.exists()
    assert not (tmp_path / "race-request.json").exists()


def test_source_push_rejects_filename_identity_mismatch(tmp_path, monkeypatch):
    """The immutable intent path and payload must refer to the same race."""
    import subprocess
    import pytest

    subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, check=True,
                   capture_output=True)
    for key, value in (("user.email", "test@example.invalid"),
                       ("user.name", "LOCAL Test")):
        subprocess.run(["git", "config", key, value], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("base\n")
    subprocess.run(["git", "add", "README.md"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "base"], cwd=tmp_path,
                   check=True, capture_output=True)
    before = _git(tmp_path, "rev-parse", "HEAD")

    path = tmp_path / "runtime/source_intents/KM-LOCAL-KAW-20261110-R01.json"
    path.parent.mkdir(parents=True)
    # Committed bytes are authentic, and race_id matches execution_id, but
    # the *committed filename* names a different race.
    request = {"family_id": "LOCAL", "execution_phase": "SOURCE",
               "execution_id": "KM-LOCAL-KAW-20261110-R02",
               "race_id": "KM-LOCAL-KAW-20261110-R02"}
    path.write_text(json.dumps(request))
    subprocess.run(["git", "add", str(path.relative_to(tmp_path))],
                   cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "SOURCE intent"], cwd=tmp_path,
                   check=True, capture_output=True)
    after = _git(tmp_path, "rev-parse", "HEAD")
    event = tmp_path / "event.json"
    event.write_text(json.dumps({"before": before, "after": after,
                                 "deleted": False}))
    output = tmp_path / "github_output"

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GITHUB_EVENT_NAME", "push")
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(event))
    monkeypatch.setenv("GITHUB_SHA", after)
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    with pytest.raises(SystemExit, match="SOURCE_INTENT_FILENAME_EXECUTION_ID_MISMATCH"):
        exec(_source_python(), {})
    assert not output.exists()
    assert not (tmp_path / "race-request.json").exists()

def test_source_first_with_static_cannot_enter_formal_prediction(tmp_path, monkeypatch):
    """SOURCE-only ingress must never pass a FORMAL-capable request to Runtime."""
    request = {
        "family_id": "LOCAL",
        "execution_phase": "SOURCE",
        "execution_id": "KM-LOCAL-KAW-20261110-R04",
        "static_prediction": {"provenance": "synthetic-approved-frozen"},
    }
    output = tmp_path / "github_output"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GITHUB_EVENT_NAME", "workflow_dispatch")
    monkeypatch.setenv("RACE_REQUEST_JSON", json.dumps(request))
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))

    exec(_source_python(), {})
    forwarded = json.loads((tmp_path / "race-request.json").read_text())
    assert forwarded["execution_id"] == request["execution_id"]
    assert forwarded["static_prediction"] == request["static_prediction"]
    # The downstream local_race_entry.run() only stays at SOURCE + numerical
    # when analysis_only is explicitly True; otherwise it can enter FORMAL.
    assert forwarded["analysis_only"] is True


def test_source_first_rejects_non_source_prediction_modes_before_runtime(tmp_path, monkeypatch):
    """SOURCE-only workflow must not dispatch to AUTO or REFERENCE Runtime paths."""
    import pytest

    for mode in ("REFERENCE", "AUTO"):
        execution_id = "KM-LOCAL-KAW-20261110-R06"
        request = {
            "family_id": "LOCAL",
            "execution_phase": "SOURCE",
            "execution_id": execution_id,
            "prediction_mode": mode,
        }
        out = tmp_path / "github_output"
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("GITHUB_EVENT_NAME", "workflow_dispatch")
        monkeypatch.setenv("RACE_REQUEST_JSON", json.dumps(request))
        monkeypatch.setenv("GITHUB_OUTPUT", str(out))
        # Actual runtime.local_race_entry.run() dispatches on prediction_mode
        # before consulting analysis_only. Prevent those routes at ingress.
        with pytest.raises(SystemExit, match="SOURCE_INTENT_PREDICTION_MODE_MISMATCH"):
            exec(_source_python(), {})
        assert not out.exists()
        assert not (tmp_path / "race-request.json").exists()


def test_source_first_post_run_accepts_verified_reused_checkpoint(tmp_path, monkeypatch):
    """A verified SOURCE checkpoint readback has no newly executed phases."""
    import pytest

    workflow = yaml.safe_load(
        (ROOT / ".github/workflows/km-local-source-first-entry.yml").read_text(encoding="utf-8")
    )
    step = next(s for s in workflow["jobs"]["entry"]["steps"]
                if s.get("name") == "Execute SOURCE-first entry with explicit hold reporting")
    blocks = re.findall(r"python - <<'PY'\n(.*?)\nPY", step["run"], re.S)
    assert len(blocks) == 2
    verify = compile(blocks[1], "<source-first-actual-postrun-verifier>", "exec")

    reports = tmp_path / "entry-out"
    reports.mkdir()
    report_file = reports / "entry_report.json"
    cached = {
        "status": "HOLD",
        "code": "STATIC_PREDICTION_FREEZE_REQUIRED",
        "formal_final_proven": False,
        "source": {
            "status": "SOURCE_PASS",
            "phase": "SOURCE",
            "execution_class": "SOURCE_ONLY",
            "signed_source_verified": True,
            "completion": False,
            # Existing verified SOURCE reuse does not run a new phase.
        },
    }
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SOURCE_ENTRY_RC", "1")
    report_file.write_text(json.dumps(cached))
    exec(verify, {})  # Signed SOURCE cache is a valid SOURCE-only outcome.

    # A fabricated SOURCE_PASS label without verified signature must still fail.
    cached["source"]["signed_source_verified"] = False
    report_file.write_text(json.dumps(cached))
    with pytest.raises(SystemExit, match="SIGNED_SOURCE_STAGE_NOT_VERIFIED"):
        exec(verify, {})


def test_source_only_does_not_lose_signed_checkpoint_on_numerical_hold(tmp_path, monkeypatch):
    """SOURCE is verified independently of unfinished Full29 numerical coverage."""
    import pytest

    workflow = yaml.safe_load(
        (ROOT / ".github/workflows/km-local-source-first-entry.yml").read_text(encoding="utf-8")
    )
    step = next(s for s in workflow["jobs"]["entry"]["steps"]
                if s.get("name") == "Execute SOURCE-first entry with explicit hold reporting")
    blocks = re.findall(r"python - <<'PY'\n(.*?)\nPY", step["run"], re.S)
    assert len(blocks) == 2
    verify = compile(blocks[1], "<source-first-actual-postrun-verifier>", "exec")

    reports = tmp_path / "entry-out"
    reports.mkdir()
    report = {
        "status": "HOLD",
        "first_failed_phase": "NUMERICAL",
        "code": "FULL_NUMERICAL_CLOSURE_REQUIRED",
        "formal_final_proven": False,
        "source": {
            "status": "SOURCE_PASS",
            "signed_source_verified": True,
            "execution_class": "SOURCE_ONLY",
        },
    }
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SOURCE_ENTRY_RC", "1")
    (reports / "entry_report.json").write_text(json.dumps(report))
    # It must be possible to retain a valid SOURCE-only diagnostic even if
    # actual numerical coverage is incomplete. No FORMAL success is inferred.
    exec(verify, {})

    # A valid SOURCE label cannot launder an unrelated execution failure.
    report["code"] = "UNEXPECTED_RUNTIME_FAILURE"
    (reports / "entry_report.json").write_text(json.dumps(report))
    with pytest.raises(SystemExit, match="UNEXPECTED_SOURCE_FIRST_FAILURE"):
        exec(verify, {})

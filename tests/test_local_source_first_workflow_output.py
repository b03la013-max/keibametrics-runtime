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
    assert json.loads((tmp_path / "race-request.json").read_text()) == request


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
    assert json.loads((tmp_path / "race-request.json").read_text()) == request


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

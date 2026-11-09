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

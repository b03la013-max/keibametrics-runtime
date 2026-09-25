from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
FORMAL = ROOT / ".github/workflows/km-family-non-jra-formal-runner.yml"
RESULT = ROOT / ".github/workflows/km-local-result-from-signed-final.yml"
FORMAL_RUNNER = ROOT / "runtime/non_jra_formal_runner.py"
RESULT_RUNNER = ROOT / "runtime/local_result_from_signed_final.py"


def _extract_python_heredocs(text: str):
    lines = text.splitlines()
    blocks = []
    i = 0
    while i < len(lines):
        if re.search(r"python(?:\s+-[^\s]+|\s+[^<]+)?\s+<<'PY'\s*$", lines[i]):
            base_indent = len(lines[i]) - len(lines[i].lstrip())
            i += 1
            body = []
            while i < len(lines):
                line = lines[i]
                if line.strip() == "PY" and (len(line) - len(line.lstrip())) == base_indent:
                    break
                body.append(line[base_indent:] if len(line) >= base_indent else line)
                i += 1
            blocks.append("\n".join(body) + "\n")
        i += 1
    return blocks


def test_metadata_heredocs_and_extracted_runners_compile():
    for path in (FORMAL, RESULT):
        blocks = _extract_python_heredocs(path.read_text(encoding="utf-8"))
        assert blocks, f"no metadata Python heredoc found in {path}"
        for n, block in enumerate(blocks, 1):
            compile(block, f"{path.name}:heredoc:{n}", "exec")
    for path in (FORMAL_RUNNER, RESULT_RUNNER):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")


def test_formal_gateway_contract_is_in_extracted_runner():
    workflow = FORMAL.read_text(encoding="utf-8")
    runner = FORMAL_RUNNER.read_text(encoding="utf-8")
    assert "assess_runtime_health" in runner
    assert "RUNTIME_GATEWAY_COMPATIBILITY_FAILED" in runner
    assert 'gateway_artifact_name(execution_id,"SOURCE",gateway,"LOCAL")' in runner
    assert "REQUEST_RUNTIME_REVISION_STALE" not in runner
    assert 'fail_closed("RUNTIME_REVISION_MISMATCH"' not in runner
    assert "python -m runtime.non_jra_formal_runner" in workflow
    assert "steps.execution_meta.outputs.artifact_name" in workflow
    assert "km-local-execution-failure-" in workflow
    assert len(workflow) < 21000


def test_result_gateway_contract_is_in_extracted_runner():
    workflow = RESULT.read_text(encoding="utf-8")
    runner = RESULT_RUNNER.read_text(encoding="utf-8")
    assert 'gateway_artifact_name(execution_id,"FORMAL",gateway,"LOCAL")' in runner
    assert 'family_config("LOCAL",gateway)' in runner
    assert 'endpoint=req.get("external_endpoint")' not in runner
    assert "python -m runtime.local_result_from_signed_final" in workflow
    assert "steps.execution_meta.outputs.artifact_name" in workflow
    assert "km-local-result-failure-" in workflow
    assert len(workflow) < 21000

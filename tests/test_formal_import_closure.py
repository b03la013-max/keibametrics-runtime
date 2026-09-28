from pathlib import Path

from runtime.formal_import_closure import build_closure


def test_formal_import_closure_compiles_all_local_dependencies():
    report = build_closure("runtime/non_jra_formal_runner.py")
    assert report["status"] == "PASS"
    files = set(report["files"])
    assert "runtime/non_jra_formal_runner.py" in files
    assert "runtime/local_evidence_acquisition_roundtrip.py" in files
    assert "runtime/execution_gateway.py" in files
    assert report["file_count"] >= 10


def test_roundtrip_source_contains_real_import_newlines():
    text = Path("runtime/local_evidence_acquisition_roundtrip.py").read_text(encoding="utf-8")
    assert "\\nimport " not in text
    assert "\\nfrom " not in text

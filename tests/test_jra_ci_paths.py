"""JRA acceptance workflows that do not push commits carry derived path filters (LOCAL A2 port)."""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATED = sorted(p for p in (ROOT / ".github/workflows").glob("*jra*.yml")
                   if "ci_paths:begin" in p.read_text(encoding="utf-8"))


def test_jra_generated_workflows_exist():
    assert len(GENERATED) >= 29


def test_jra_path_filters_cover_every_dependency():
    r = subprocess.run([sys.executable, str(ROOT / "tools/ci_paths.py"), "--check", *map(str, GENERATED)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout

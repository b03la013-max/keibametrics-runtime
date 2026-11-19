"""The three acceptance workflows run only when a file they check changes; their path lists must cover the
import / data-file closure of everything they run (tools/ci_paths.py). Fails when a test starts reading a new
file that is not in the trigger list -> rerun `python tools/ci_paths.py --write <workflow>`."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WFS = ['.github/workflows/km-family-owner-utility-pfs-r43-acceptance.yml',
       '.github/workflows/aki-adaptive-purchase-shadow-acceptance.yml',
       '.github/workflows/km-local-production-numerical-v1-acceptance.yml']


def test_acceptance_trigger_paths_cover_closure():
    r = subprocess.run([sys.executable, 'tools/ci_paths.py', '--check', *WFS], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_manual_dispatch_kept():
    for wf in WFS:
        assert 'workflow_dispatch:' in (ROOT / wf).read_text()

"""Offline snapshot audit; private output only, no paid content on stdout."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from jra_bloodb_browser_bridge import evaluate_snapshot
from jra_bloodb_mac_collector import private_dir, private_write, json_bytes

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--snapshot", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    report = evaluate_snapshot(json.loads(args.snapshot.read_text(encoding="utf-8")), root=ROOT)
    private_dir(args.output.parent)
    private_write(args.output, json_bytes(report))
    print(json.dumps({k: report[k] for k in ("profile", "race_count", "runner_count",
                                            "calculated_bvi_count", "blocked_bvi_count", "bvi_authority")}))

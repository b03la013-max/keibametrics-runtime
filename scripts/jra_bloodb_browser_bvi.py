"""Offline snapshot audit; private output only, no paid content on stdout."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from jra_bloodb_browser_bridge import evaluate_snapshot, snapshot_from_collection
from jra_bloodb_mac_collector import private_dir, private_write, json_bytes

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    inputs = p.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--snapshot", type=Path)
    inputs.add_argument("--collection-jsonl", type=Path)
    p.add_argument("--source-index", type=Path,
                   help="Private JSON: observed rcode -> selected signed SOURCE envelope path")
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    snapshot = (snapshot_from_collection([json.loads(line) for line in
                args.collection_jsonl.read_text(encoding="utf-8").splitlines() if line.strip()])
                if args.collection_jsonl else json.loads(args.snapshot.read_text(encoding="utf-8")))
    index = json.loads(args.source_index.read_text(encoding="utf-8")) if args.source_index else None
    report = evaluate_snapshot(snapshot, root=ROOT, source_index=index)
    private_dir(args.output.parent)
    private_write(args.output, json_bytes(report))
    print(json.dumps({k: report[k] for k in ("profile", "race_count", "runner_count",
                                            "calculated_bvi_count", "blocked_bvi_count", "bvi_authority")}))

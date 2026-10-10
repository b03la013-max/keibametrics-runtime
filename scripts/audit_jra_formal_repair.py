"""Recompute stored SOURCE; no dispatch, signing, FINAL, purchase or OOS increment."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "runtime"), str(ROOT / "runtime/jra_source_runtime")]
from jra_execution_maturity_bridge import prepare_production_numerical, resolve_current_authority
from verify_source_envelope import verify


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output); output.mkdir(parents=True, exist_ok=True)
    rows = []
    for eid in ("KM-JRA-KYO-20261010-R08-LIVE-R1", "KM-JRA-KYO-20261010-R09-LIVE-R1",
                "KM-JRA-TKY-20261010-R03-LIVE-R1", "KM-JRA-TKY-20261010-R05-LIVE-R1",
                "KM-JRA-TKY-20261010-R11-INTEGRATION-LIVE-R1"):
        # Durable store checks the stored inventory and hashes, not signer identity.
        from execution_store import resolve_phase
        checkpoint = resolve_phase(eid, "SOURCE", root=ROOT/"runtime/executions")
        if checkpoint is None:
            raise ValueError("STORED_SOURCE_REQUIRED:" + eid)
        path = checkpoint["run_dir"] / "source_receipt_envelope.json"
        signature = verify(str(path))
        intent = json.loads((ROOT/"runtime/jra_formal_intents"/(eid+".json")).read_text())
        source = json.loads(path.read_text())
        report = prepare_production_numerical(intent, source, source_execution_id=eid)
        # Historical diagnostics must never emit backdated Static/KRS/FINAL.
        (output/(eid+".json")).write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
        rows.append({"execution_id":eid,
                     "source_file":str(path.relative_to(ROOT)),
                     "source_file_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
                     "envelope_ed25519_and_hash_check":signature["valid"],
                     "independent_oidc_verification_performed_by_this_script":False,
                     **{k:report[k] for k in ("required_index_count","verified_full_index_count",
                            "partial_base_calculated_count","partial_base_blocked_count",
                            "production_numerical_error","first_blocked_stage","independent_blockers")}})
    absent = [str(p.relative_to(ROOT)) for folder in ("jra_formal_intents","requests","executions","exact_gaps")
              for p in (ROOT/"runtime"/folder).glob("*KYO-20261010-R10*")]
    summary = {"classification":"HISTORICAL_LOCAL_DIAGNOSTIC / NO_OOS / NOT_FORMAL_FINAL",
               "base_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
               "authority":resolve_current_authority(), "races":rows,
               "kyoto_r10_matching_records_in_checked_directories":absent,
               "external_krs_executed":False,"signed_final_issued":False,"oos_increment":0}
    (output/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()

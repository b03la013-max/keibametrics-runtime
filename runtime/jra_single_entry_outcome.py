"""Single Entry outcome accounting; never a signature verifier or promotion."""
from __future__ import annotations

from datetime import datetime


def evidence_terminal_eligible(report):
    """Only a demonstrated missing Base evidence failure can use this terminal."""
    return (
        # The numerical gate is evaluated first; an unapproved Owner may be
        # appended as an independent blocker ("|INDEPENDENT_BLOCKERS:...").
        str(report.get("auto_handoff_error") or "").split("|", 1)[0] == "JRA_AUTHORIZED_FULL20_INCOMPLETE"
        and report.get("production_full_numerical_ready") is False
        and report.get("first_blocked_stage") == "PRODUCTION_FEATURE_INDEX_CLOSURE"
        and (report.get("partial_base_blocked_count", 0) > 0
             # Base13 closed but a Derived DCR component lacks its evidence.
             or str(report.get("production_numerical_error") or "").startswith("DCR_COMPONENT_UNRESOLVED:"))
    )


def verify_formal_completion_summary(summary, request):
    """Validate the canonical external worker's verification summary.

    The caller must obtain this artifact from the trusted canonical Production
    job. Independent optional Shadow jobs may still be running.
    This content check does not independently verify cryptographic signatures.
    Replay and acceptance success cannot become Production pre-race success.
    """
    def require(ok, reason):
        if not ok:
            raise ValueError("JRA_SINGLE_ENTRY_COMPLETION_" + reason)

    require(summary.get("status") == "FULL_FORMAL_E2E_PASS", "STATUS")
    require(summary.get("race_id") == request.get("race_id")
            and summary.get("family_id") == "JRA"
            and request.get("family_id") == "JRA", "IDENTITY")
    require(summary.get("temporal_formality") == "FORMAL-PRE-RACE"
            and summary.get("acceptance_only") is False
            and request.get("temporal_mode", "FORMAL-PRE-RACE") == "FORMAL-PRE-RACE"
            and request.get("acceptance_only") is not True, "REPLAY_OR_ACCEPTANCE")
    require(summary.get("source_snapshot_sha256") == request.get("source_snapshot_sha256")
            and bool(request.get("source_snapshot_sha256")), "SOURCE_BINDING")
    stages = summary.get("execution_stage_manifest") or {}
    require(bool(stages) and all(x.get("status") == "PASS" for x in stages.values())
            and summary.get("all_mandatory_stages_verified") is True
            and summary.get("all_mandatory_pre_race_stages_verified") is True, "STAGES")
    manifest = summary.get("manifest") or {}
    required = len(request.get("runners") or []) * 20
    require(required > 0 and manifest.get("required_count") == required
            and manifest.get("calculated_count") == required
            and all(manifest.get(k) == 0 for k in (
                "ruled_hold_count", "not_applicable_count", "unresolved_count")), "FULL20")
    for phase in ("pre_krs", "krs", "final"):
        receipt = summary.get(phase) or {}
        require(receipt.get("verified") is True
                and len(str(receipt.get("receipt_sha256") or "")) == 64,
                phase.upper() + "_VERIFICATION")
    krs = summary["krs"]
    count = request.get("run_count", 5000)
    require(krs.get("requested_run_count") == count
            and krs.get("actual_run_count") == count
            and type(count) is int and count in (5000, 20000), "KRS_COUNT")
    try:
        final_time = datetime.fromisoformat(str(summary["final"].get("receipt_timestamp")).replace("Z", "+00:00"))
        post = datetime.fromisoformat(str(request.get("scheduled_post_at")).replace("Z", "+00:00"))
        require(final_time.tzinfo is not None and post.tzinfo is not None
                and final_time < post, "FINAL_AFTER_POST")
    except (TypeError, ValueError) as exc:
        raise ValueError("JRA_SINGLE_ENTRY_COMPLETION_FINAL_TIME_INVALID") from exc
    require(len(str(summary["final"].get("immutable_artifact_sha256") or "")) == 64,
            "IMMUTABLE_FINAL")
    return {"production_full_prediction_completed": True,
            "status": "FORMAL_COMPLETE", "race_id": summary["race_id"],
            "signed_final_receipt_sha256": summary["final"]["receipt_sha256"],
            "verification_owner": "CANONICAL_EXTERNAL_FORMAL_RUNNER",
            "independent_signature_verification_by_this_function": False}


class FormalFailureCheckpoint:
    """Keep the first Python failure even before KRS artifacts exist."""
    def __init__(self, request_path, artifact_dir="krs-artifacts"):
        import pathlib, sys
        self.path = pathlib.Path(artifact_dir)
        self.path.mkdir(parents=True, exist_ok=True)
        self.request_path = str(request_path)
        self.current_stage = "FORMAL_PREPARATION"
        self.previous_hook = sys.excepthook
        sys.excepthook = self.capture
        self.mark(self.current_stage)

    def mark(self, stage):
        import json
        self.current_stage = stage
        (self.path / "formal_progress.json").write_text(json.dumps({
            "first_pending_stage":stage,"request_path":self.request_path}) + "\n")

    def capture(self, kind, error, tb):
        import json, traceback
        record = {"first_failed_stage":self.current_stage,
                  "exception_type":kind.__name__,"error":str(error)[:2000],
                  "traceback":"".join(traceback.format_exception(kind,error,tb))[-12000:],
                  "exit_code":1,"request_path":self.request_path}
        (self.path / "formal_failure.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n")
        self.previous_hook(kind,error,tb)


def record_formal_failure(root, request, failure):
    """Derived failure index only; never edits SOURCE, FINAL, or a request."""
    import json, re
    from pathlib import Path
    root = Path(root)
    rid = str(request.get('race_id') or '')
    eid = str(request.get('execution_id') or request.get('source_execution_id') or '')
    if (request.get('family_id') != 'JRA' or not re.fullmatch(r'KM-JRA-[A-Z]+-\d{8}-R\d{2}',rid)
            or not eid.startswith(rid+'-') or not re.fullmatch(r'[A-Za-z0-9._-]+',eid)
            or not str(failure.get('run_id') or '').isdigit()):
        raise ValueError('JRA_FORMAL_FAILURE_IDENTITY_INVALID')
    path = root/'runtime/exact_gaps'/(eid+'.json')
    previous = json.loads(path.read_text()) if path.exists() else {}
    failure = {**failure,'race_id':rid,'execution_id':eid,
               'signed_final':False,'production_prediction_change':False}
    history = previous.setdefault('formal_execution_failures',{})
    key = str(failure['run_id'])
    existing = history.get(key)
    if existing and failure.get('first_failed_stage') == 'EXTERNAL_FORMAL_WORKFLOW':
        failure = existing  # Do not replace a precise traceback with a coarse poll.
    history[key] = failure
    latest = max(history.values(),key=lambda x:int(x['run_id']))
    previous['formal_execution_failure'] = latest
    previous.setdefault('race_id',rid)
    previous.setdefault('first_blocked_stage',latest['first_failed_stage'])
    # Older still-running day workers also understand this fail-closed field.
    previous.setdefault('auto_handoff_error','FORMAL_WORKFLOW_FAILED:'+str(latest.get('error') or latest.get('conclusion')))
    previous.setdefault('required_index_count',len(request.get('runners') or [])*20)
    previous.setdefault('verified_full_index_count',None)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(previous,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    return path


if __name__ == '__main__':
    import argparse, json, os
    from pathlib import Path
    from datetime import timezone
    parser=argparse.ArgumentParser()
    parser.add_argument('--request',required=True)
    parser.add_argument('--failure',default='krs-artifacts/formal_failure.json')
    args=parser.parse_args()
    path=Path(args.failure)
    if path.exists():
        record=json.loads(path.read_text())
    else:
        progress=Path('krs-artifacts/formal_progress.json')
        record={'first_failed_stage':json.loads(progress.read_text())['first_pending_stage'] if progress.exists() else 'EXTERNAL_FORMAL_WORKFLOW',
                'error':'FORMAL_WORKFLOW_FAILED_WITHOUT_PYTHON_TRACEBACK','exit_code':None}
    record.update(run_id=os.environ['GITHUB_RUN_ID'],run_attempt=os.environ.get('GITHUB_RUN_ATTEMPT'),
                  workflow_head_sha=os.environ['GITHUB_SHA'],conclusion='failure',
                  observed_at=datetime.now(timezone.utc).isoformat(),
                  run_url='https://github.com/'+os.environ['GITHUB_REPOSITORY']+'/actions/runs/'+os.environ['GITHUB_RUN_ID'])
    print(record_formal_failure(Path('.'),json.loads(Path(args.request).read_text()),record))

"""Race-key ingress transport regression; no fabricated Static or historical FINAL."""
from datetime import datetime, timezone
from pathlib import Path

import pytest

from runtime import local_race_key_intake as intake
from runtime import local_race_key_gate as gate


def authority(*, now):
    return Path("profiles/authority.json"), {
        "manifest_id": "KM-FAMILY-CURRENT-AUTHORITY-20990101-R100",
        "status": "ACTIVE / FAMILY-CURRENT-AUTHORITY / FROZEN",
    }


def future_fields():
    return {
        "venue_id": "KAW",
        "race_date": "2099-01-01",
        "race_no": "6",
        "scheduled_post_at": "2099-01-01T17:15:00+09:00",
        "prediction_cutoff": "2099-01-01T17:10:00+09:00",
    }


def valid_build(fields=None, now=None, resolver=authority):
    return intake.build(
        fields or future_fields(), now=now or datetime(2099, 1, 1, 7, tzinfo=timezone.utc),
        authority_resolver=resolver,
    )


def test_minimal_race_key_derives_identity_current_authority_and_no_static():
    x = valid_build()
    assert x["execution_id"] == x["race_id"] == "KM-LOCAL-KAW-20990101-R06-LIVE-R1"
    assert x["current_authority_manifest"].endswith("R100")
    assert x["scheduled_post_at"] == "2099-01-01T17:15:00+09:00"
    assert x["release_deadline_at"] == "2099-01-01T17:13:00+09:00"
    assert x["analysis_only"] is False
    assert x["execution_phase"] == "SOURCE"
    assert x["require_full_numerical_authority"] is True
    assert "static_prediction" not in x
    assert "runners" not in x
    assert "final_prediction_package" not in x
    assert "capital_policy" not in x


@pytest.mark.parametrize("field,replacement,code", [
    ("venue_id", "JRA", "LOCAL_VENUE_NOT_SUPPORTED"),
    ("venue_id", "KAW/../", "LOCAL_VENUE_NOT_SUPPORTED"),
    ("race_date", "2099/01/01", "RACE_DATE_INVALID"),
    ("race_no", "0", "RACE_NO_INVALID"),
    ("race_no", "13", "RACE_NO_INVALID"),
    ("race_no", "6;echo hacked", "RACE_NO_INVALID"),
    ("scheduled_post_at", "2099-01-01T17:15:00", "SCHEDULED_POST_TIMEZONE_REQUIRED"),
    ("scheduled_post_at", "2099-01-01T08:15:00+00:00", "SCHEDULED_POST_JST_REQUIRED"),
    ("scheduled_post_at", "2099-01-02T17:15:00+09:00", "RACE_DATE_AND_POST_MISMATCH"),
    ("prediction_cutoff", "2099-01-01T17:16:00+09:00", "CUTOFF_NOT_BEFORE_POST"),
])
def test_malformed_key_fail_closed(field, replacement, code):
    d = future_fields()
    d[field] = replacement
    with pytest.raises(intake.IntakeError, match=code):
        valid_build(d)


def test_cutoff_expired_never_backdates_race():
    with pytest.raises(intake.IntakeError, match="SOURCE_CUTOFF_EXPIRED"):
        valid_build(now=datetime(2099, 1, 1, 8, 11, tzinfo=timezone.utc))


def test_authority_unavailable_holds():
    def unavailable(*, now):
        return Path("none"), {"manifest_id": "test", "status": "CANDIDATE"}
    with pytest.raises(intake.IntakeError, match="CURRENT_AUTHORITY_NOT_ACTIVE"):
        valid_build(resolver=unavailable)


def signed_request():
    return {
        "execution_id": "RACE", "race_id": "RACE",
        "venue_id": "KAW", "race_date": "2099-01-01", "race_no": 6,
        "scheduled_post_at": "2099-01-01T17:15:00+09:00",
        "prediction_cutoff": "2099-01-01T17:10:00+09:00",
    }


def patch_source(monkeypatch):
    from runtime import formal_execution_orchestrator as o
    monkeypatch.setattr(o, "resolve_phase", lambda eid, phase: {"run_dir": Path("/source")}
                        if phase == "SOURCE" else {"run_dir": Path("/formal")})
    monkeypatch.setattr(o, "validate_source_checkpoint", lambda p, request: None)
    def load(resolved, key):
        if key == "source_receipt_envelope.json":
            return {
                "receipt_sha256": "signed_source",
                "artifact": {
                    "source_freeze_at": "2099-01-01T08:00:00+00:00",
                    "source_race_context": {"venue_id": "KAW", "race_date": "2099/01/01", "race_no": 6},
                    "normalized_evidence": {"start_time": {
                        "value": "17:15", "authority": "NAR_OFFICIAL",
                        "cutoff_relation": "PRE_CUTOFF"}},
                },
            }
        if key == "receipt_verifications.json":
            return {"SOURCE": True, "PRE_KRS": True, "KRS_RUN": True, "FINAL": True}
        if key == "final_before_post_verification.json":
            return {"verified": True, "execution_id": "RACE", "race_id": "RACE"}
        if key == "final_receipt_envelope.json":
            return {"receipt_sha256": "signed_final", "receipt": {"status": "PASS"}}
        raise AssertionError(key)
    monkeypatch.setattr(o, "_load_checkpoint_json", load)


def test_signed_source_without_static_is_not_formal_completion(monkeypatch):
    patch_source(monkeypatch)
    result = gate.certify(signed_request(),
                          {"status": "HOLD", "code": "STATIC_PREDICTION_FREEZE_REQUIRED",
                           "formal_final_proven": False, "completion": False})
    assert result["source_verified"] is True
    assert result["formal_final_proven"] is False
    assert result["status"] == "SOURCE_VERIFIED_STATIC_PENDING"


def test_signed_source_with_frozen_formal_verification(monkeypatch):
    patch_source(monkeypatch)
    result = gate.certify(signed_request(),
                          {"status": "FULL_LIFECYCLE_EXECUTION_PASS",
                           "completion": {"complete": True}})
    assert result["formal_final_proven"] is True
    assert result["final_receipt_sha256"] == "signed_final"


def test_invalid_formal_checkpoint_or_blocked_pipeline_cannot_pass(monkeypatch):
    from runtime import formal_execution_orchestrator as o
    patch_source(monkeypatch)
    with pytest.raises(gate.RaceKeyGateError, match="FORMAL_EXECUTION_NOT_COMPLETE"):
        gate.certify(signed_request(),
                     {"status": "BLOCKED", "completion": False})
    original = o._load_checkpoint_json
    monkeypatch.setattr(o, "_load_checkpoint_json",
                        lambda resolved, key: original(resolved, key)
                        if key == "source_receipt_envelope.json" else {"FINAL": False})
    with pytest.raises(gate.RaceKeyGateError, match="SIGNED_FINAL_VERIFICATION_REQUIRED"):
        gate.certify(signed_request(),
                     {"status": "FULL_LIFECYCLE_EXECUTION_PASS", "completion": {"complete": True}})


def test_source_verification_missing_blocks(monkeypatch):
    from runtime import formal_execution_orchestrator as o
    monkeypatch.setattr(o, "resolve_phase", lambda *args: None)
    with pytest.raises(gate.RaceKeyGateError, match="SIGNED_SOURCE_CHECKPOINT_MISSING"):
        gate.certify({"execution_id": "RACE"}, {"status": "HOLD", "code": "STATIC_PREDICTION_FREEZE_REQUIRED"})


def test_signed_source_disagrees_with_official_post_time(monkeypatch):
    patch_source(monkeypatch)
    req = signed_request()
    req["scheduled_post_at"] = "2099-01-01T17:20:00+09:00"
    with pytest.raises(gate.RaceKeyGateError, match="SIGNED_SOURCE_OFFICIAL_POST_TIME_MISMATCH"):
        gate.certify(req, {"status": "HOLD", "code": "STATIC_PREDICTION_FREEZE_REQUIRED"})


def test_signed_source_after_cutoff_does_not_retroactively_pass(monkeypatch):
    from runtime import formal_execution_orchestrator as o
    patch_source(monkeypatch)
    original = o._load_checkpoint_json
    def altered(resolved, key):
        value = original(resolved, key)
        if key == "source_receipt_envelope.json":
            value = {**value, "artifact": {**value["artifact"],
                     "source_freeze_at": "2099-01-01T08:11:00+00:00"}}
        return value
    monkeypatch.setattr(o, "_load_checkpoint_json", altered)
    with pytest.raises(gate.RaceKeyGateError, match="SIGNED_SOURCE_FROZEN_AFTER_CUTOFF"):
        gate.certify(signed_request(), {
            "status": "HOLD", "code": "STATIC_PREDICTION_FREEZE_REQUIRED"})



def test_signed_source_survives_formal_release_deadline(monkeypatch):
    patch_source(monkeypatch)
    result = gate.certify(
        signed_request(),
        {"status": "HOLD", "code": "DEADLINE_HOLD:FORMAL_INCOMPLETE",
         "prestart_deadline_expired": True,
         "formal_final_proven": False, "completion": False},
    )
    assert result["source_verified"] is True
    assert result["formal_final_proven"] is False
    assert result["completion"] is False
    assert result["status"] == "SOURCE_VERIFIED_FORMAL_DEADLINE_HOLD"


def test_forged_deadline_hold_without_actual_expiry_rejected(monkeypatch):
    patch_source(monkeypatch)
    with pytest.raises(gate.RaceKeyGateError, match="UNEXPECTED_FORMAL_HOLD"):
        gate.certify(signed_request(), {
            "status": "HOLD", "code": "DEADLINE_HOLD:FORMAL_INCOMPLETE",
            "prestart_deadline_expired": False,
            "formal_final_proven": False, "completion": False})


def test_workflow_supplies_python_roots_and_result_dependencies():
    wf = (Path(__file__).resolve().parents[1] /
          ".github/workflows/km-local-race-key-entry.yml").read_text(encoding="utf-8")
    assert "PYTHONPATH:" in wf
    assert "github.workspace }}/runtime" in wf
    assert "name: Install RESULT runtime dependencies" in wf
    assert "python -m runtime.local_race_entry" in wf


def test_dispatch_is_minimal_and_requires_signed_final_for_result():
    workflow = (Path(__file__).resolve().parents[1] /
                ".github/workflows/km-local-race-key-entry.yml").read_text(encoding="utf-8")
    for name in ("workflow_dispatch:", "repository_dispatch:", "km_local_race_key",
                 "--scheduled-post-at", "--prediction-cutoff",
                 "runtime.local_race_entry", "runtime.local_race_key_gate",
                 "steps.gate.outputs.formal_ready", "FORMAL/LATEST.json",
                 "persist_local_checkpoints.py", "--resume-official-result"):
        assert name in workflow
    assert "source_verified" in workflow
    assert "contents: write" in workflow


def test_push_concurrency_independent_of_result_wait():
    """A previous race's live RESULT cannot hold the next push race's SOURCE."""
    wf = (Path(__file__).resolve().parents[1] /
          ".github/workflows/km-local-race-key-entry.yml").read_text(encoding="utf-8")
    assert "ref: ${{ github.sha }}" in wf
    assert "group: km-formal-${{ matrix.execution_id }}" in wf
    assert "cancel-in-progress: false" in wf
    assert wf.count("group: km-formal-${{ matrix.execution_id }}")==2


def test_saved_r12_event_survives_main_moving_to_measurement_commit(tmp_path):
    """Historical R12 request in synthetic Git history; no remote history needed."""
    import subprocess
    root=Path(__file__).resolve().parents[1]
    def git(*args):
        return subprocess.check_output(['git',*args],cwd=tmp_path,text=True).strip()
    git('init');git('config','user.email','test@example.invalid');git('config','user.name','test')
    (tmp_path/'initial').write_text('initial');git('add','.');git('commit','-m','initial')
    before=git('rev-parse','HEAD')
    name='runtime/race_key_requests/KAW-20261014-R12-LIVE-R1.json'
    request=tmp_path/name;request.parent.mkdir(parents=True)
    request.write_bytes((root/name).read_bytes())
    git('add','.');git('commit','-m','saved R12 request');after=git('rev-parse','HEAD')
    (tmp_path/'measurement').write_text('later unrelated state');git('add','.');git('commit','-m','measurement')
    old=git('diff-tree','--no-commit-id','--name-only','-r','HEAD')
    assert not any(x.startswith('runtime/race_key_requests/') for x in old.splitlines())
    new=intake.resolve_event({'before':before,'after':after},'push',cwd=tmp_path)
    assert len(new['requests'])==1 and int(new['requests'][0]['race_no'])==12
    assert not new['errors']


def test_multi_race_event_has_independent_cells_and_bad_cell_is_preserved(tmp_path):
    import json,subprocess
    def git(*args):return subprocess.check_output(['git',*args],cwd=tmp_path,text=True).strip()
    git('init');git('config','user.email','test@example.invalid');git('config','user.name','test')
    (tmp_path/'initial').write_text('first');git('add','.');git('commit','-m','initial');before=git('rev-parse','HEAD')
    folder=tmp_path/'runtime/race_key_requests';folder.mkdir(parents=True)
    for number in [1,2]:
        d=future_fields();d['race_no']=number;(folder/f'R{number}.json').write_text(json.dumps(d))
    (folder/'bad.json').write_text('{"extra":"invalid"}')
    git('add','.');git('commit','-m','two keys and bad cell');after=git('rev-parse','HEAD')
    (tmp_path/'later').write_text('moving head');git('add','.');git('commit','-m','unrelated later')
    r=intake.resolve_event({'before':before,'after':after},'push',cwd=tmp_path)
    assert len(r['requests'])==2 and len(r['errors'])==1 and r['status']=='PARTIAL'
    assert len({x['execution_id'] for x in r['requests']})==2


def test_no_signed_final_or_delivery_inferred_from_successful_job(monkeypatch):
    from runtime import local_race_key_gate as gate
    monkeypatch.setattr(gate.o,'resolve_phase',lambda *args:None)
    state=gate.terminal_state('MISSING','success')
    assert state['status']=='NO_SIGNED_FINAL'
    assert not state['signed_final_pass'] and not state['prestart_delivery_pass']


def test_saved_final_flags_cannot_override_fresh_signature_failure(monkeypatch):
    from runtime import local_race_key_gate as gate
    from runtime import execution_gateway as gateway
    monkeypatch.setattr(gate.o, 'resolve_phase', lambda *a: {'run_dir': 'unused'})
    values = {'final_receipt_envelope.json': {'receipt': {'status': 'PASS', 'race_id': 'race'}},
              'receipt_verifications.json': {'FINAL': True},
              'final_before_post_verification.json': {'verified': True}}
    monkeypatch.setattr(gate.o, '_load_checkpoint_json', lambda p, name: values[name])
    monkeypatch.setattr(gateway, 'request_json', lambda *a, **k: (200, {'valid': False}))
    result = gate.terminal_state('race', 'success')
    assert result['status'] == 'HOLD'
    assert result['signed_final_pass'] is False
    assert result['render_available'] is False
    assert result['prestart_delivery_pass'] is False


def test_terminal_summary_does_not_publish_stale_tree_on_verify_hold(monkeypatch,tmp_path):
    from runtime import local_race_key_gate as gate
    import sys,json
    stale=tmp_path/'runtime/execution_reports/race/delivery/canonical_tree.txt'
    stale.parent.mkdir(parents=True);stale.write_text('STALE TICKETS')
    source_report=tmp_path/'entry_report.json'
    source_report.write_text(json.dumps({'status':'HOLD','first_failed_phase':'SOURCE',
                                       'first_failed_code':'HTTP_503','code':'HTTP_503'}))
    monkeypatch.setattr(gate.o,'ROOT',tmp_path)
    monkeypatch.setattr(gate,'terminal_state',lambda *a:{'execution_id':'race','status':'HOLD',
        'reason':'FINAL_FRESH_SIGNATURE_OR_IDENTITY_REQUIRED','render_available':False,'prestart_delivery_pass':False})
    output=tmp_path/'terminal.json';summary=tmp_path/'summary.md'
    monkeypatch.setattr(sys,'argv',['gate','--terminal-only','--execution-id','race','--job-status','failure',
        '--report',str(source_report),'--output',str(output),'--github-summary',str(summary)])
    assert gate.main()==0
    assert 'STALE TICKETS' not in summary.read_text()
    result=json.loads(output.read_text())
    assert result['execution_failure']['first_failed_code']=='HTTP_503'
    assert result['execution_failure']['first_failed_phase']=='SOURCE'
    assert result['github_summary']['canonical_final_included'] is False
    assert result['prestart_delivery_pass'] is False


def test_terminal_summary_binds_exact_content_and_final_without_receipt_claim(monkeypatch,tmp_path):
    from runtime import local_race_key_gate as gate
    import sys,json,hashlib
    tree='CANONICAL TICKETS\n'
    monkeypatch.setattr(gate,'terminal_state',lambda *a:{'execution_id':'race','status':'SIGNED_FINAL_RENDER_AVAILABLE_DELIVERY_UNPROVEN',
        'signed_final_pass':True,'prestart_final_pass':True,'render_available':True,
        'prestart_delivery_pass':False,'user_received_at':None,'canonical_tree':tree,
        'final_receipt_sha256':'receipt-sha','original_final_artifact_sha256':'artifact-sha'})
    output=tmp_path/'terminal.json';summary=tmp_path/'summary.md'
    monkeypatch.setattr(sys,'argv',['gate','--terminal-only','--execution-id','race','--job-status','success',
        '--output',str(output),'--github-summary',str(summary)])
    assert gate.main()==0
    result=json.loads(output.read_text());record=result['github_summary']
    assert tree in summary.read_text()
    assert record['content_sha256']==hashlib.sha256(summary.read_bytes()).hexdigest()
    assert record['final_receipt_sha256']=='receipt-sha'
    assert record['final_artifact_sha256']=='artifact-sha'
    assert record['written_at'] and record['canonical_final_included'] is True
    assert result['prestart_delivery_pass'] is False and result['user_received_at'] is None

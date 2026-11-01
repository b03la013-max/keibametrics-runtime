"""Official-navigation, original-result recovery and honest OOS admission.

No test dispatches a workflow, signs a RESULT or contacts JRA/GitHub.
"""
import copy
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import urllib.error
import zipfile

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
import jra_candidate_postresult_closedloop as c
import jra_static_owner_forward_oos as s
from test_jra_candidate_postresult_closedloop import frozen, official


class ArchiveOfficial:
    """Only the published archive selector advertises the older frozen date."""
    def __init__(self, heading="2026年10月4日（日曜）4回東京3日 2レース"):
        self.calls = []
        self.day = "pw01srl00052026040320261004/AF"
        self.race = "pw01sde0105202604030220261004/BC"
        self.heading = heading
        self.last_url = "https://www.jra.go.jp/JRADB/accessS.html"
        self.last_headers = {"content-type": "text/html; charset=UTF-8"}

    def get(self, path):
        self.calls.append(("GET", path))
        return "doAction('/JRADB/accessS.html','CURRENT') doAction('/JRADB/accessS.html','pw01sklROOT')"

    def post(self, path, token):
        self.calls.append(("POST", token))
        if token == "CURRENT":
            return "pw01srl00052026040520261011/AA"  # deliberately not requested day
        if token == "pw01sklROOT":
            return ('var yearMonth = "202611"; objParam["2610"]="CD"; '
                    'pw01skl00 pw01skl10 Number(arg) >= yearMonth '
                    'objParam[String(arg).substring(2,6)] '
                    '<select name="kaisaiY_list"><option value="2026"></option></select>'
                    '<select name="kaisaiM_list"><option value="10"></option></select>')
        if token == "pw01skl10202610/CD":
            return self.day
        if token == self.day:
            return self.race
        assert token == self.race
        text = '<h1>' + self.heading + '</h1><table><tr><th>着順</th><th>馬番</th><th>馬名</th><th>コーナー通過順位</th></tr>'
        text += ''.join(f'<tr><td>{i}</td><td>{i}</td><td>馬{i}</td><td>1 2</td></tr>' for i in range(1, 4))
        self.last_raw = (text + '</table>').encode()
        return text


def test_older_frozen_date_uses_observed_archive_tokens_and_original_heading():
    client = ArchiveOfficial()
    out = c.fetch_jra_result("2026-10-04", "0520260403", 2, client=client)
    assert ("POST", "pw01skl10202610/CD") in client.calls
    assert ("POST", client.race) in client.calls
    assert out["context_verification"]["heading_verified"] is True
    assert out["parsed"]["runner_count"] == 3
    assert out["sha256"] == hashlib.sha256(client.last_raw).hexdigest()
    assert not any("accessD" in call[1] for call in client.calls)


@pytest.mark.parametrize("heading", ["2026年10月5日（月曜）4回東京3日 2レース",
    "2026年10月4日（日曜）4回京都3日 2レース", "2026年10月4日（日曜）4回東京3日 3レース"])
def test_wrong_day_venue_or_race_heading_is_blocked(heading):
    with pytest.raises(c.OfficialResultAcquisitionError, match="CONTEXT_MISMATCH") as error:
        c.fetch_jra_result("2026-10-04", "0520260403", 2, client=ArchiveOfficial(heading))
    assert c.result_failure(error.value)["category"] == "RESULT_IDENTITY_CONFLICT"


def test_missing_archive_form_is_resolution_block_not_nonexistent_race():
    client = ArchiveOfficial()
    client.get = lambda path: "doAction('/JRADB/accessS.html','CURRENT')"
    with pytest.raises(c.OfficialResultAcquisitionError) as error:
        c.fetch_jra_result("2026-10-04", "0520260403", 2, client=client)
    failure = c.result_failure(error.value)
    assert failure["status"] == "BLOCKED"
    assert failure["category"] == "RESULT_DAY_RESOLUTION_FAILED"


def test_transient_read_retries_same_request_but_access_denial_stops(monkeypatch):
    import jra_race_card_detail
    monkeypatch.setattr(c.clock, "sleep", lambda seconds: None)
    calls = []
    def transient(opener, url, **kwargs):
        calls.append((id(opener), url, kwargs))
        if len(calls) == 1:
            raise TimeoutError("temporary read timeout")
        return url, b"observed", {"content-type": "text/html"}
    monkeypatch.setattr(jra_race_card_detail, "_fetch", transient)
    client = c._ResultNavigationClient()
    assert client.post("/JRADB/accessS.html", "OBSERVED_TOKEN") == "observed"
    assert calls[0] == calls[1] and client.retry_count == 1
    calls.clear()
    def denied(opener, url, **kwargs):
        calls.append(url)
        raise urllib.error.HTTPError(url, 403, "Forbidden", {}, None)
    monkeypatch.setattr(jra_race_card_detail, "_fetch", denied)
    with pytest.raises(urllib.error.HTTPError) as error:
        client.post("/JRADB/accessS.html", "OBSERVED_TOKEN")
    assert len(calls) == 1
    assert c.result_failure(error.value)["retryable"] is False
    assert c.result_failure(urllib.error.HTTPError("https://www.jra.go.jp/", 404, "Missing", {}, None))["status"] == "BLOCKED"


def pre_record(race):
    pre = {"profile": s.PROFILE, "owner_profile": s.OWNER_PROFILE, "race_id": race,
        "policy_fingerprint": "fixed-policy", "frozen_at": "2026-10-04T00:50:00+00:00",
        "prediction_cutoff": "2026-10-04T01:00:00+00:00", "scheduled_post_at": "2026-10-04T01:10:00+00:00",
        "race_date": "2026-10-04", "race_no": int(race[-2:]), "meeting_key": "0520260403",
        "ranking": ["1", "2", "3"], "market_ranking": ["3", "2", "1"],
        "production_authority": False, "candidate_only": True}
    pre["sha256"] = s.sha(pre)
    return pre


def write_pre(tmp_path, pre):
    path = tmp_path / "runtime/jra_static_owner_forward_oos" / pre["race_id"] / "pre_result.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(pre))
    return path


def result_evidence():
    return {"sha256": "a" * 64, "top3": ["1", "2", "3"], "captured_at": "2026-10-04T02:00:00+00:00",
            "source": "SAVED_ED25519_VERIFIED_PRODUCTION_RESULT"}


def test_one_race_resolution_failure_does_not_abort_an_independent_result_join(tmp_path, monkeypatch):
    first = pre_record("KM-JRA-TKY-20261004-R01")
    second = pre_record("KM-JRA-TKY-20261004-R02")
    write_pre(tmp_path, first); path = write_pre(tmp_path, second)
    original = path.read_bytes()
    monkeypatch.setattr(s, "fingerprint", lambda root: "fixed-policy")
    def saved(root, pre, **kwargs):
        if pre["race_id"] == first["race_id"]:
            raise c.OfficialResultAcquisitionError("DAY_SELECTOR_CHANGED", category="RESULT_DAY_RESOLUTION_FAILED")
        return result_evidence()
    monkeypatch.setattr(s, "saved_result_evidence", saved)
    out = s.settle(tmp_path)
    manifest = out["processing_manifest"]
    assert manifest["status"] == "PARTIAL"
    assert (manifest["success_count"], manifest["failure_count"], manifest["unresolved_count"]) == (1, 1, 1)
    assert out["eligible_settled_races"] == 0
    assert path.read_bytes() == original and not path.with_name("result_evaluation.json").exists()
    diagnostics = list(path.parent.glob("result_match_diagnostic_*.json"))
    assert json.loads(diagnostics[0].read_text())["forward_oos_increment"] == 0
    before = diagnostics[0].read_bytes()
    out = s.settle(tmp_path)
    assert out["processing_manifest"]["already_complete_count"] == 1
    assert diagnostics[0].read_bytes() == before and out["eligible_settled_races"] == 0


def test_existing_corrupt_evaluation_is_blocked_instead_of_false_complete(tmp_path, monkeypatch):
    pre = pre_record("KM-JRA-TKY-20261004-R01")
    path = write_pre(tmp_path, pre)
    record = s.evaluate(pre, ["1", "2", "3"], result_sha256="a" * 64,
        observed_at="2026-10-04T02:00:00+00:00", git_commit_at="2026-10-04T00:55:00+00:00")
    record["sha256"] = "INVALID"
    path.with_name("result_evaluation.json").write_text(json.dumps(record))
    monkeypatch.setattr(s, "fingerprint", lambda root: "fixed-policy")
    out = s.settle(tmp_path, witness_verifier=lambda *a, **k: {"status": "PASS"})
    assert out["processing_manifest"]["status"] == "BLOCKED"
    assert out["processing_manifest"]["failure_count"] == 1
    assert out["processing_manifest"]["already_complete_count"] == 0
    assert out["eligible_settled_races"] == 0


@pytest.mark.parametrize("invalid", ["late", "bytes", "oidc"])
def test_external_provider_witness_requires_exact_bytes_time_and_oidc(tmp_path, monkeypatch, invalid):
    pre = pre_record("KM-JRA-TKY-20261004-R01"); path = write_pre(tmp_path, pre)
    raw = path.read_bytes(); path.with_name("prediction_witness_ref.json").write_text('{"artifact_id":123}')
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as stream:
        stream.writestr("pre_result.json", b"different" if invalid == "bytes" else raw)
    blob = archive.getvalue()
    meta = {"id": 123, "expired": False, "size_in_bytes": len(blob),
        "created_at": "2026-10-04T01:01:00Z" if invalid == "late" else "2026-10-04T00:55:00Z",
        "digest": "sha256:" + hashlib.sha256(blob).hexdigest()}
    def gh(args, **kwargs):
        if args[1] == "attestation":
            return json.dumps([] if invalid == "oidc" else [{"verificationResult": {
                "verifiedTimestamps": [{"timestamp": "2026-10-04T00:56:00Z"}]}}])
        return blob if args[-1].endswith("/zip") else json.dumps(meta)
    monkeypatch.setattr(s.subprocess, "check_output", gh)
    with pytest.raises(ValueError):
        s.verify_independent_prediction_witness(path, pre, root=tmp_path)
    assert path.read_bytes() == raw


def test_git_only_prediction_has_no_independent_admission(tmp_path):
    pre = pre_record("KM-JRA-TKY-20261004-R01"); path = write_pre(tmp_path, pre)
    assert s.verify_independent_prediction_witness(path, pre, root=tmp_path)["status"] == "UNKNOWN"


def copy_real_originals(tmp_path):
    race = "KM-JRA-TKY-20261031-R12"
    paths = [f"runtime/jra_static_owner_forward_oos/{race}/pre_result.json",
             f"runtime/results/{race}.json", f"runtime/final_artifacts/{race}.json"]
    paths += [str(p.relative_to(ROOT)) for p in (ROOT / "runtime/executions" / (race + "-LIVE-R1") /
              "RESULT/runs/41191875119").glob("*.json")]
    for name in paths:
        target = tmp_path / name; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    pre = json.loads((tmp_path / paths[0]).read_text())
    from family_authority_guard import resolve_current_authority
    _, authority = resolve_current_authority(ROOT)
    contract = json.loads((ROOT / authority["common_family_components"]["family_runtime_contracts_profile"]).read_text())["families"]["JRA"]
    health = json.loads((ROOT / "tests/fixtures/jra_result_public_trust_20261101.json").read_text())
    return pre, lambda: (health, contract)


def test_retained_real_signed_result_completes_original_static_diagnostic_not_new_oos(tmp_path, monkeypatch):
    pre, health = copy_real_originals(tmp_path)
    monkeypatch.setattr(s, "fingerprint", lambda root: s.sha({"test_policy_root": "unchanged"}))
    path = tmp_path / "runtime/jra_static_owner_forward_oos" / pre["race_id"] / "pre_result.json"
    original = path.read_bytes()
    out = s.settle(tmp_path, health_loader=health,
        fetch_result=lambda *a: pytest.fail("retained signed RESULT must not cause another official HTTP read"))
    assert out["processing_manifest"]["status"] == "VERIFIED_COMPLETE"
    assert out["processing_manifest"]["diagnostic_settled_count"] == 1
    assert out["eligible_settled_races"] == 0
    diagnostic = json.loads(next(path.parent.glob("result_match_diagnostic_*.json")).read_text())
    assert diagnostic["top3"] == ["7", "10", "8"]
    assert diagnostic["result_evidence"]["result_request_sha256"] == "fddb5ac238d0e9d5a655c81d2fc5919b93491e6d9fbf350eca270e2d505c7dce"
    assert diagnostic["oos_eligible"] is False and path.read_bytes() == original
    target = next(path.parent.glob("result_match_diagnostic_*.json"))
    diagnostic["winner_rank"] = 999
    diagnostic["sha256"] = s.sha({k: v for k, v in diagnostic.items() if k != "sha256"})
    target.write_text(json.dumps(diagnostic))
    invalid = s.settle(tmp_path, health_loader=health)
    assert invalid["processing_manifest"]["status"] == "BLOCKED"
    assert invalid["processing_manifest"]["failure_count"] == 1
    request_path = tmp_path / "runtime/results" / (pre["race_id"] + ".json")
    corrupted = json.loads(request_path.read_text()); corrupted["official_result"]["top3"] = [10, 7, 8]
    request_path.write_text(json.dumps(corrupted))
    with pytest.raises(ValueError, match="PAYLOAD_UNBOUND"):
        s.saved_result_evidence(tmp_path, pre, health_loader=health)


@pytest.mark.parametrize("written", [(), ("result_evaluation",), ("result_evaluation", "settlement"),
                                    ("result_evaluation", "settlement", "learning")])
def test_partial_candidate_write_recovers_only_from_original_observation_and_rejects_conflict(tmp_path, written):
    pre, final = frozen(); race = pre["race_id"]
    folder = tmp_path / "runtime/source_candidate_oos" / race; folder.mkdir(parents=True)
    for name, value in (("pre_result", pre), ("candidate_final", final)):
        (folder / (name + ".json")).write_text(json.dumps(value))
    outcome = official(); rawsha = "a" * 64; url = "https://www.jra.go.jp/JRADB/accessS.html"
    expected = c.settle_frozen_candidate(pre, final, outcome, source_sha256=rawsha, source_url=url)
    for key in written:
        (folder / (key + ".json")).write_text(json.dumps(expected[key]))
    original = {"profile": c.PROFILE, "race_id": race, "status": "OFFICIAL_POST_RESULT_SNAPSHOT",
        "raw_sha256": rawsha, "captured_at": "2026-10-10T02:30:00+00:00", "url": url,
        "result_top3": outcome["top3"], "payouts": outcome["payouts"]}
    (folder / "official_result_observation.json").write_text(json.dumps(original))
    assert c.process(tmp_path, race) == ("ALREADY_SETTLED" if len(written) == 3 else "SETTLED_RECOMMENDATION")
    assert c.process(tmp_path, race) == "ALREADY_SETTLED"
    assert json.loads((folder / "learning.json").read_text()) == expected["learning"]
    broken = expected["learning"].copy(); broken["next_action"] = "PROMOTE"
    (folder / "learning.json").write_text(json.dumps(broken))
    with pytest.raises(ValueError, match="ARTIFACT_CONFLICT"):
        c.process(tmp_path, race)

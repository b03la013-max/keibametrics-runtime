"""Independent Static Owner forward evidence; never issues Production approval.

Only actual Production-formula Full20 enters this shadow. Existing
source-derived Candidate cohorts cannot be counted for this policy.
"""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import urllib.request
import zipfile

from jra_static_owner_executable import compile_static_owner, PROFILE as OWNER_PROFILE

ROOT = Path(__file__).resolve().parents[1]
PROFILE = "JRA-STATIC-OWNER-INDEPENDENT-FORWARD-OOS"


def sha(obj):
    return hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def time(value):
    result=datetime.fromisoformat(str(value).replace("Z","+00:00"))
    if result.tzinfo is None: raise ValueError("OOS_TIMEZONE_REQUIRED")
    return result


def fingerprint(root=ROOT):
    paths=("runtime/jra_bvi_failure_attribution.py","runtime/jra_static_owner_executable.py","runtime/jra_bvi_shadow_comparison.py",
           "runtime/jra_owner_authorized_feature_rules.py","runtime/jra_pedigree_corpus.py",
           "mapping/jra_evidence_feature_rule_registry_v1.3_20261010.json",
           "runtime/jra_official_fact_evaluator_production.py",
           "runtime/jra_source_to_evidence_features.py","runtime/jra_source_runtime/jra_observed_context.py",
           "runtime/jra_source_runtime/jra_current_environment.py",
           "runtime/jra_source_runtime/jra_race_card_detail.py",
           "runtime/jra_evidence_to_base_production.py","runtime/jra_index_provenance_builder.py",
           "runtime/jra_evidence_feature_normalizer_production.py",
           "mapping/jra_base_index_evidence_mapping_v1.0_20260921.json")
    return sha({p:hashlib.sha256((Path(root)/p).read_bytes()).hexdigest() for p in paths})


def freeze(intent, envelope, report, *, source_verified, created_at=None, root=ROOT):
    now=time(created_at or datetime.now(timezone.utc).isoformat())
    cutoff=time(intent["prediction_cutoff"]); post=time(intent["scheduled_post_at"])
    if not now <= cutoff < post: raise ValueError("STATIC_OWNER_FORWARD_CUTOFF_EXPIRED")
    if intent.get("acceptance_only") is True or intent.get("temporal_mode","FORMAL-PRE-RACE") != "FORMAL-PRE-RACE":
        raise ValueError("STATIC_OWNER_REPLAY_OR_ACCEPTANCE_FORBIDDEN")
    if source_verified is not True: raise ValueError("STATIC_OWNER_SIGNED_SOURCE_REQUIRED")
    if report.get("production_full_numerical_ready") is not True or report.get("source_only_full_numerical_ready") is not True:
        raise ValueError("STATIC_OWNER_SOURCE_ONLY_PRODUCTION_FULL20_REQUIRED")
    meeting_key=(intent.get("jra_source") or {}).get("jra_meeting_key")
    if not isinstance(meeting_key,str) or len(meeting_key)!=10 or not meeting_key.isdigit():
        raise ValueError("STATIC_OWNER_OFFICIAL_MEETING_KEY_REQUIRED")
    source=envelope["artifact"]
    if (source.get("race_id") != intent["race_id"] or source.get("prediction_cutoff") != intent["prediction_cutoff"]
            or source.get("source_snapshot_sha256") != sha({k:v for k,v in source.items() if k!="source_snapshot_sha256"})):
        raise ValueError("STATIC_OWNER_SOURCE_BINDING_INVALID")
    if report.get("race_id") != intent["race_id"] or report.get("family_id") != "JRA":
        raise ValueError("STATIC_OWNER_REPORT_IDENTITY_MISMATCH")
    prepared=report["prepared_numerical_request"]
    if prepared.get("race_id") != intent["race_id"] or prepared.get("family_id") != "JRA":
        raise ValueError("STATIC_OWNER_NUMERIC_IDENTITY_MISMATCH")
    official=source.get("jra_official_runner_universe") or {}
    ids=[str(x.get("runner_id") or x.get("horse_no")) for x in official.get("runners") or []]
    if set(ids) != {str(x["runner_id"]) for x in prepared["runners"]}:
        raise ValueError("STATIC_OWNER_OFFICIAL_RUNNER_UNIVERSE_MISMATCH")
    if report.get("verified_full_index_count") != len(ids)*20 or report.get("required_index_count") != len(ids)*20:
        raise ValueError("STATIC_OWNER_FULL20_COUNT_MISMATCH")
    owner=compile_static_owner(prepared,source_snapshot_sha256=source["source_snapshot_sha256"],
                               source_receipt_sha256=envelope["receipt_sha256"],
                               frozen_at=now.isoformat(),prediction_cutoff=intent["prediction_cutoff"])
    # Use published popularity only, never odds-derived synthetic probabilities.
    market={str(x.get("runner_id") or x.get("horse_no")):x.get("popularity_rank")
            for x in (source.get("jra_official_race_card_detail") or {}).get("runners") or []}
    if set(market) != set(ids) or {v for v in market.values() if type(v) is int} != set(range(1,len(ids)+1)):
        raise ValueError("STATIC_OWNER_MARKET_BASELINE_INCOMPLETE")
    market_order=sorted(ids,key=lambda rid:market[rid])
    result={"profile":PROFILE,"owner_profile":OWNER_PROFILE,"race_id":intent["race_id"],
            "policy_fingerprint":fingerprint(root),"frozen_at":now.isoformat(),
            "prediction_cutoff":intent["prediction_cutoff"],"scheduled_post_at":intent["scheduled_post_at"],
            "race_date":intent["race_date"],"race_no":intent["race_no"],
            "meeting_key":(intent.get("jra_source") or {}).get("jra_meeting_key"),
            "source_snapshot_sha256":source["source_snapshot_sha256"],"source_receipt_sha256":envelope["receipt_sha256"],
            "owner":owner,"ranking":owner["static_prediction"]["ranking"],"market_ranking":market_order,
            "numeric_provenance_hash":prepared["index_provenance_hash"],
            "full_index_count":owner["full_index_count"],"candidate_only":True,
            "production_authority":False,"purchase_authority":False,"signed_final_issued":False}
    if all(isinstance(r.get("evidence_features"),dict) and r.get("career_starts") is not None
           for r in prepared["runners"]):
        from jra_bvi_shadow_comparison import compare
        mapping=json.loads((Path(root)/"mapping/jra_base_index_evidence_mapping_v1.0_20260921.json").read_text())
        comparison_request = dict(intent)
        comparison_request.update(prepared)
        result["pedigree_comparison"] = compare(comparison_request, mapping,
            source_sha=source["source_snapshot_sha256"], receipt_sha=envelope["receipt_sha256"],
            algorithm_freeze_at=now.isoformat(), cutoff=intent["prediction_cutoff"])
        result["pedigree_comparison"]["status"] = "FROZEN_UNKNOWN_FUTURE_SHADOW / B_EQUALS_A_UNTIL_DISTINCT_INPUT"
    else:
        result["pedigree_comparison"] = {"status":"BLOCKED_FEATURE_LEDGER_UNAVAILABLE",
            "production_effect":"NONE", "oos_eligible":False}
    result["sha256"]=sha(result)
    return result


def evaluate(pre, top3, *, result_sha256, observed_at, git_commit_at):
    if pre.get("profile") != PROFILE or pre.get("owner_profile") != OWNER_PROFILE:
        raise ValueError("STATIC_OWNER_WRONG_POLICY_COHORT")
    if pre.get("sha256") != sha({k:v for k,v in pre.items() if k!="sha256"}):
        raise ValueError("STATIC_OWNER_FROZEN_HASH_INVALID")
    if not time(pre["frozen_at"]) <= time(git_commit_at) <= time(pre["prediction_cutoff"]) < time(pre["scheduled_post_at"]) < time(observed_at):
        raise ValueError("STATIC_OWNER_NOT_PROSPECTIVE")
    actual=[str(x) for x in top3]
    if len(actual)!=3 or len(set(actual))!=3 or not set(actual).issubset(pre["ranking"]):
        raise ValueError("STATIC_OWNER_RESULT_UNIVERSE_INVALID")
    if pre.get("production_authority") is not False or pre.get("candidate_only") is not True:
        raise ValueError("STATIC_OWNER_AUTHORITY_LEAK")
    if len(result_sha256)!=64: raise ValueError("STATIC_OWNER_RESULT_HASH_REQUIRED")
    static=[pre["ranking"].index(x)+1 for x in actual]
    market=[pre["market_ranking"].index(x)+1 for x in actual]
    out={"profile":PROFILE,"race_id":pre["race_id"],"policy_fingerprint":pre["policy_fingerprint"],
         "frozen_sha256":pre["sha256"],"official_result_sha256":result_sha256,
         "observed_at":observed_at,"git_commit_at":git_commit_at,"top3":actual,
         "winner_rank_gain":market[0]-static[0],
         "top3_mean_rank_gain":sum(m-s for m,s in zip(market,static))/3,
         "oos_eligible":True,"production_effect":"NONE"}
    comparison = pre.get("pedigree_comparison") or {}
    arms = comparison.get("arms") or {}
    if arms:
        measured = {}
        for name, arm in arms.items():
            owner = arm["owner"]
            ranking = owner["static_prediction"]["ranking"]
            columns = owner["active_columns"]
            candidates = set().union(*(set(x) for x in columns.values()))
            measured[name] = {
                "winner_rank": ranking.index(actual[0]) + 1,
                "winner_discovery_recall": int(actual[0] in columns["W"]),
                "p2_capture": actual[1] in columns["P2"],
                "p3_capture": actual[2] in columns["P3"],
                "top3_mean_rank": sum(ranking.index(x)+1 for x in actual)/3,
                "ordered_pair_capture": any((x["head"],x["second"]) == tuple(actual[:2])
                    for x in owner["pair_dispositions"]),
                "exact_semantic_capture": any((x["head"],x["second"],x["third"]) == tuple(actual)
                    for x in owner["third_dispositions"]),
                "candidate_width": len(candidates),
                "false_positive_candidates": len(candidates-set(actual)),
                "low_popularity_top3_discovered": [x for x in actual if x in candidates
                    and pre["market_ranking"].index(x)+1 >= 6],
                "krs_input_changed_vs_current": arm["krs_input"] != arms["A_CURRENT"]["krs_input"],
                "krs_result_utility": None, "ticket_count": None, "capital_required": None,
                "investment_weighted_pfs": None, "robust_pfs": None,
                "downstream_blocker": "SHADOW_KRS_MEC_SETTLEMENT_NOT_EXECUTED",
            }
        out["pedigree_arm_metrics"] = measured
        out["pedigree_enhanced_input_distinct"] = comparison["enhanced_input_distinct"]
    out["sha256"]=sha(out); return out


def scorecard(records, *, policy_fingerprint, independent_admissions=()):
    # A self-hashed evaluation or a Git timestamp alone is not independent
    # prediction storage evidence. The orchestrator re-verifies admissions.
    admitted = set(independent_admissions)
    accepted={}; rejected=[]
    for row in records:
        if (row.get("profile")!=PROFILE or row.get("policy_fingerprint")!=policy_fingerprint
                or row.get("oos_eligible") is not True
                or row.get("sha256")!=sha({k:v for k,v in row.items() if k!="sha256"})
                or row.get("frozen_sha256") not in admitted):
            rejected.append(row.get("race_id")); continue
        rid=row["race_id"]
        if rid in accepted and accepted[rid] != row: raise ValueError("STATIC_OWNER_DUPLICATE_RESULT_CONFLICT")
        accepted[rid]=row
    count=len(accepted)
    return {"profile":PROFILE,"policy_fingerprint":policy_fingerprint,"eligible_settled_races":count,
            "required_forward_races":30,"remaining_forward_races":max(0,30-count),
            "mean_winner_rank_gain":sum(x["winner_rank_gain"] for x in accepted.values())/count if count else None,
            "mean_top3_rank_gain":sum(x["top3_mean_rank_gain"] for x in accepted.values())/count if count else None,
            "rejected_records":rejected,"market_baseline_superiority_proven":False,
            "independent_review_required":True,"production_activation_authorized":False,
            "automatic_promotion":False,"status":"WAITING_FORWARD_OOS" if count<30 else "INDEPENDENT_REVIEW_REQUIRED"}


def verify_independent_prediction_witness(path, pre, *, root=ROOT):
    """Read provider evidence; never accept a declaration next to a prediction.

    Legacy Git-only records remain UNKNOWN. No field is backfilled into them.
    A separate reference may identify an existing independent artifact, whose bytes,
    provider creation time and OIDC verified timestamp must all bind this file.
    """
    reference_path = Path(path).with_name("prediction_witness_ref.json")
    reference = json.loads(reference_path.read_text()) if reference_path.exists() else {}
    artifact_id = reference.get("artifact_id")
    if type(artifact_id) is not int or artifact_id <= 0:
        return {"status": "UNKNOWN", "reason": "INDEPENDENT_PREDICTION_WITNESS_NOT_RECORDED"}
    repo = "b03la013-max/keibametrics-runtime"
    raw = Path(path).read_bytes()
    metadata = json.loads(subprocess.check_output(
        ["gh", "api", f"repos/{repo}/actions/artifacts/{artifact_id}"], cwd=root, text=True, timeout=30))
    created = time(metadata["created_at"])
    if (metadata.get("id") != artifact_id or metadata.get("expired") is True
            or not time(pre["frozen_at"]) <= created <= time(pre["prediction_cutoff"])):
        raise ValueError("STATIC_OWNER_PROVIDER_WITNESS_ID_OR_TIME_INVALID")
    if not 0 < int(metadata.get("size_in_bytes", 0)) <= 64 * 1024 * 1024:
        raise ValueError("STATIC_OWNER_PROVIDER_WITNESS_TOO_LARGE")
    archive = subprocess.check_output(["gh", "api", f"repos/{repo}/actions/artifacts/{artifact_id}/zip"], cwd=root, timeout=60)
    if metadata.get("digest") != "sha256:" + hashlib.sha256(archive).hexdigest():
        raise ValueError("STATIC_OWNER_PROVIDER_WITNESS_DIGEST_INVALID")
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        if sum(i.file_size for i in z.infolist()) > 64 * 1024 * 1024:
            raise ValueError("STATIC_OWNER_PROVIDER_WITNESS_TOO_LARGE")
        matches = [i for i in z.infolist() if not i.is_dir() and z.read(i) == raw]
        if len(matches) != 1 or z.testzip() is not None:
            raise ValueError("STATIC_OWNER_PROVIDER_WITNESS_PREDICTION_BYTES_INVALID")
    verified = json.loads(subprocess.check_output(["gh", "attestation", "verify", str(path),
        "--repo", repo, "--signer-workflow", repo + "/.github/workflows/km-jra-formal-single-entry.yml",
        "--format", "json"], cwd=root, text=True, timeout=60))
    stamps = [time(x.get("timestamp") or x.get("time")) for proof in verified
              for x in (proof.get("verificationResult") or {}).get("verifiedTimestamps", [])]
    if not any(time(pre["frozen_at"]) <= t <= time(pre["prediction_cutoff"]) for t in stamps):
        raise ValueError("STATIC_OWNER_INDEPENDENT_TIMESTAMP_NOT_PRE_CUTOFF")
    return {"status": "PASS", "artifact_id": artifact_id,
            "provider_created_at": metadata["created_at"], "artifact_digest": metadata["digest"],
            "prediction_file_sha256": hashlib.sha256(raw).hexdigest()}


def saved_result_evidence(root, pre, *, health_loader):
    """Verify the existing signed RESULT; never submits or re-signs a request."""
    from jra_presentation import _receipt
    from jra_delivery import verify_signed_final
    rid = pre["race_id"]
    request_path = root / "runtime/results" / (rid + ".json")
    if not request_path.exists():
        return None
    request = json.loads(request_path.read_text())
    candidates = sorted((root / "runtime/executions").glob(rid + "*/RESULT/runs/*/result_receipt_envelope.json"))
    if not candidates:
        return None  # retained observation alone is not a signed RESULT
    matches = []
    for candidate in candidates:
        envelope = json.loads(candidate.read_text())
        if (envelope.get("receipt") or {}).get("artifact_sha256") == sha(request):
            matches.append((candidate, envelope))
    if not matches:
        raise ValueError("STATIC_OWNER_SAVED_RESULT_PAYLOAD_UNBOUND")
    if len({sha(envelope) for _, envelope in matches}) != 1:
        raise ValueError("STATIC_OWNER_SAVED_RESULT_RECEIPT_CONFLICT")
    health, contract = health_loader()
    candidate, envelope = matches[0]
    receipt = _receipt(envelope, health["receipt_signer"], rid, "RESULT")
    final = json.loads((root / "runtime/final_artifacts" / (rid + ".json")).read_text())
    verify_signed_final(final, health, contract)
    reference = request.get("frozen_prediction_ref") or {}
    if (request.get("race_id") != rid or request.get("result_lane") != "PRODUCTION"
            or reference.get("source_cutoff") != pre["prediction_cutoff"]
            or reference.get("final_receipt_sha256") != final["final_receipt_sha256"]):
        raise ValueError("STATIC_OWNER_SAVED_RESULT_FINAL_BINDING_INVALID")
    official = request.get("official_result") or {}
    if (official.get("status") != "OFFICIAL" or official.get("result_use") != "POST-RACE"
            or not str(official.get("source_url", "")).startswith("https://www.jra.go.jp/")
            or len(str(official.get("raw_sha256", ""))) != 64
            or not time(pre["scheduled_post_at"]) < time(official["captured_at"]) <= time(receipt["timestamp"])):
        raise ValueError("STATIC_OWNER_SAVED_RESULT_OFFICIAL_TIME_INVALID")
    top3 = [str(x) for x in official.get("top3") or []]
    if len(top3) != 3 or len(set(top3)) != 3 or not set(top3) <= set(pre["ranking"]):
        raise ValueError("STATIC_OWNER_SAVED_RESULT_UNIVERSE_INVALID")
    return {"top3": top3, "sha256": sha(request), "captured_at": official["captured_at"],
            "source": "SAVED_ED25519_VERIFIED_PRODUCTION_RESULT", "result_request_sha256": sha(request),
            "result_receipt_sha256": envelope["receipt_sha256"],
            "receipt_file": str(candidate.relative_to(root)), "official_raw_sha256": official["raw_sha256"]}


def _runtime_health(root):
    from family_authority_guard import resolve_current_authority
    _, authority = resolve_current_authority(root)
    contracts = json.loads((root / authority["common_family_components"]["family_runtime_contracts_profile"]).read_text())
    contract = contracts["families"]["JRA"]
    with urllib.request.urlopen(contract["external_endpoint"].rstrip("/") + "/health", timeout=20) as response:
        health = json.load(response)
    if (health.get("status") != "READY"
            or (health.get("engine") or {}).get("sha256") != contract["engine_sha256"]
            or (health.get("parameter_map") or {}).get("sha256") != contract["parameter_map_sha256"]):
        raise ValueError("STATIC_OWNER_RESULT_TRUST_RUNTIME_MISMATCH")
    return health, contract


def settle(root=ROOT, *, now=None, fetch_result=None, health_loader=None,
           witness_verifier=verify_independent_prediction_witness):
    """Per-race recovery with a complete manifest; immutable originals stay intact."""
    from jra_candidate_postresult_closedloop import fetch_jra_result, verify_official_result, result_failure
    from jra_research_settlement_manifest import summarize_races
    root = Path(root); base = root / "runtime/jra_static_owner_forward_oos"
    now = now or datetime.now(timezone.utc)
    fetch_result = fetch_result or fetch_jra_result
    cached_health = []
    def health():
        if not cached_health:
            cached_health.append((health_loader or (lambda: _runtime_health(root)))())
        return cached_health[0]
    rows, records, admissions = [], [], set()
    access_suspended = False
    for path in sorted(base.glob("*/pre_result.json")):
        row = {"race_id": path.parent.name}
        try:
            pre = json.loads(path.read_text())
            if pre.get("sha256") != sha({k: v for k, v in pre.items() if k != "sha256"}):
                raise ValueError("STATIC_OWNER_FROZEN_HASH_INVALID")
            if pre.get("race_id") != path.parent.name:
                raise ValueError("STATIC_OWNER_FROZEN_RACE_IDENTITY_INVALID")
            if pre.get("profile") != PROFILE or pre.get("owner_profile") != OWNER_PROFILE:
                row.update(status="OUTSIDE_CURRENT_COHORT", retryable=False)
                rows.append(row); continue
            if now <= time(pre["scheduled_post_at"]):
                row.update(status="RESULT_NOT_YET_DUE", retryable=True)
                rows.append(row); continue
            # No synthetic or shallow-clone Git time is substituted for evidence.
            admission = witness_verifier(path, pre, root=root)
            result_path = path.with_name("result_evaluation.json")
            if result_path.exists() and admission["status"] == "PASS":
                record = json.loads(result_path.read_text())
                if (record.get("sha256") != sha({k: v for k, v in record.items() if k != "sha256"})
                        or record.get("profile") != PROFILE or record.get("race_id") != pre["race_id"]
                        or record.get("policy_fingerprint") != pre["policy_fingerprint"]
                        or record.get("frozen_sha256") != pre["sha256"] or record.get("oos_eligible") is not True):
                    raise ValueError("STATIC_OWNER_EXISTING_RESULT_RECORD_INVALID")
            if admission["status"] != "PASS":
                # Reuse the original diagnostic observation without refetching or
                # replacing its capture time. The immutable prediction is untouched.
                prior = sorted(path.parent.glob("result_match_diagnostic_*.json"))
                if prior:
                    for diagnostic_path in prior:
                        diagnostic = json.loads(diagnostic_path.read_text())
                        if (diagnostic.get("sha256") != sha({k: v for k, v in diagnostic.items() if k != "sha256"})
                                or diagnostic.get("frozen_sha256") != pre["sha256"]
                                or diagnostic.get("race_id") != pre["race_id"]
                                or diagnostic.get("oos_eligible") is not False):
                            raise ValueError("STATIC_OWNER_DIAGNOSTIC_BINDING_INVALID")
                        evidence = diagnostic["result_evidence"]
                        actual = evidence["top3"]
                        if (diagnostic.get("result_sha256") != evidence["sha256"]
                                or diagnostic.get("top3") != actual or len(actual) != 3 or len(set(actual)) != 3
                                or not set(actual) <= set(pre["ranking"])
                                or not time(pre["scheduled_post_at"]) < time(evidence["captured_at"])
                                or diagnostic.get("winner_rank") != pre["ranking"].index(actual[0]) + 1
                                or diagnostic.get("top3_mean_rank") != sum(pre["ranking"].index(x) + 1 for x in actual) / 3
                                or diagnostic.get("forward_oos_increment") != 0):
                            raise ValueError("STATIC_OWNER_DIAGNOSTIC_RESULT_OR_METRICS_INVALID")
                        if evidence.get("source") == "SAVED_ED25519_VERIFIED_PRODUCTION_RESULT":
                            if evidence != saved_result_evidence(root, pre, health_loader=health):
                                raise ValueError("STATIC_OWNER_DIAGNOSTIC_SAVED_RESULT_CHANGED")
                        else:
                            from jra_candidate_postresult_closedloop import verify_result_context
                            from jra_same_day_results import parse_result_detail
                            from source_acquisition import _decode, _html_text
                            raw = base64.b64decode(evidence["raw_base64"], validate=True)
                            if hashlib.sha256(raw).hexdigest() != evidence["sha256"]:
                                raise ValueError("STATIC_OWNER_DIAGNOSTIC_ORIGINAL_BYTES_INVALID")
                            verify_result_context(raw, evidence["content_type"], pre["race_date"], pre["meeting_key"], pre["race_no"])
                            parsed = parse_result_detail(raw, evidence["content_type"])
                            original_text = _html_text(_decode(raw, evidence["content_type"]))
                            if (original_text != evidence["text"] or
                                    [str(x) for x in verify_official_result(parsed, original_text, pre["ranking"])["top3"]] != actual):
                                raise ValueError("STATIC_OWNER_DIAGNOSTIC_ORIGINAL_RESULT_INVALID")
                    row.update(status="ALREADY_SETTLED_DIAGNOSTIC_NOT_OOS", retryable=False,
                               oos_eligible=False, admission=admission)
                    rows.append(row); continue
            evidence = saved_result_evidence(root, pre, health_loader=health)
            if evidence is None:
                if access_suspended:
                    row.update(status="BLOCKED", category="OFFICIAL_ACCESS_SUSPENDED", retryable=False)
                    rows.append(row); continue
                evidence = fetch_result(pre["race_date"], pre["meeting_key"], pre["race_no"])
                evidence["top3"] = [str(x) for x in verify_official_result(
                    evidence["parsed"], evidence["text"], pre["ranking"])["top3"]]
            observed = time(evidence["captured_at"])
            if not time(pre["scheduled_post_at"]) < observed:
                raise ValueError("STATIC_OWNER_RESULT_NOT_POST_RACE")
            if result_path.exists() and admission["status"] == "PASS":
                if (record.get("official_result_sha256") != evidence["sha256"]
                        or record.get("top3") != evidence["top3"]):
                    raise ValueError("STATIC_OWNER_EXISTING_RESULT_OFFICIAL_BINDING_INVALID")
                # Recompute from its original times, rather than trusting saved metrics.
                expected = evaluate(pre, evidence["top3"], result_sha256=evidence["sha256"],
                    observed_at=record["observed_at"], git_commit_at=record["git_commit_at"])
                if record != expected:
                    raise ValueError("STATIC_OWNER_EXISTING_RESULT_METRICS_INVALID")
                records.append(record); admissions.add(pre["sha256"])
                row.update(status="ALREADY_SETTLED", retryable=False)
                rows.append(row); continue
            if admission["status"] != "PASS":
                # A real result match is useful recovery evidence, not Forward OOS.
                diagnostic = {"profile": PROFILE + "-RESULT-MATCH-DIAGNOSTIC", "race_id": pre["race_id"],
                    "frozen_sha256": pre["sha256"], "result_sha256": evidence["sha256"],
                    "top3": evidence["top3"], "winner_rank": pre["ranking"].index(evidence["top3"][0]) + 1,
                    "top3_mean_rank": sum(pre["ranking"].index(x) + 1 for x in evidence["top3"]) / 3,
                    "result_evidence": evidence, "independent_admission": admission,
                    "oos_eligible": False, "forward_oos_increment": 0, "production_effect": "NONE"}
                diagnostic["sha256"] = sha(diagnostic)
                diagnostic_path = path.with_name("result_match_diagnostic_" + evidence["sha256"][:16] + ".json")
                save_immutable(diagnostic_path, diagnostic)
                row.update(status="DIAGNOSTIC_SETTLED_NOT_OOS", retryable=False,
                           oos_eligible=False, admission=admission)
            else:
                witness = subprocess.check_output(["git", "log", "-1", "--format=%cI", "--", str(path.relative_to(root))], cwd=root, text=True).strip()
                if not witness:
                    raise ValueError("STATIC_OWNER_COMMIT_WITNESS_REQUIRED")
                record = evaluate(pre, evidence["top3"], result_sha256=evidence["sha256"],
                    observed_at=evidence["captured_at"], git_commit_at=witness)
                save_immutable(result_path, record)
                records.append(record); admissions.add(pre["sha256"])
                row.update(status="SETTLED", retryable=False, oos_eligible=True)
        except Exception as exc:
            row.update(result_failure(exc))
            if row.get("category") == "OFFICIAL_ACCESS_DENIED":
                access_suspended = True
        rows.append(row)
    out = scorecard(records, policy_fingerprint=fingerprint(root), independent_admissions=admissions)
    for row in rows:
        if row["race_id"] in out["rejected_records"] and row["status"] in {"ALREADY_SETTLED", "SETTLED"}:
            row.update(status="BLOCKED", retryable=False, reason="STATIC_OWNER_SCORECARD_RECORD_REJECTED")
    out["processing_manifest"] = summarize_races(rows)
    out["processing_manifest"]["cohort"] = PROFILE
    base.mkdir(parents=True, exist_ok=True)
    (base / "current.json").write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    return out


def save_immutable(path, obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        if json.loads(path.read_text()) != obj: raise ValueError("STATIC_OWNER_IMMUTABLE_RECORD_CONFLICT")
        return
    with path.open("x",encoding="utf-8") as stream:
        json.dump(obj,stream,ensure_ascii=False,sort_keys=True,indent=2)


def main():
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest="command",required=True)
    p=sub.add_parser("freeze")
    for name in ("intent","source-envelope","report","output"):p.add_argument("--"+name,required=True)
    sub.add_parser("settle")
    args=parser.parse_args()
    if args.command=="freeze":
        report=json.loads(Path(args.report).read_text())
        if report.get("source_only_full_numerical_ready") is not True:
            print("STATIC_OWNER_FORWARD_NOT_READY_NUMERICAL_EVIDENCE_MISSING");return
        sys.path.insert(0,str(ROOT/"runtime/jra_source_runtime"))
        from verify_source_envelope import verify
        # Independent GitHub OIDC verification is performed by the caller.
        verified=verify(args.source_envelope)
        out=freeze(json.loads(Path(args.intent).read_text()),json.loads(Path(args.source_envelope).read_text()),
                   report,source_verified=verified["valid"])
        save_immutable(args.output,out)
    else:
        out = settle()
        print(json.dumps(out, ensure_ascii=False))
        if out["processing_manifest"]["status"] in {"PARTIAL", "BLOCKED", "PENDING"}:
            raise SystemExit(2)


if __name__=="__main__":main()

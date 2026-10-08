import copy
import datetime as dt
import hashlib
import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "runtime"))
import openai_prediction_owner_candidate as owner
import formal_execution_orchestrator as orchestrator


@pytest.fixture
def sample(tmp_path):
    config = {"mode": "SHADOW", "production_authorized": False,
              "credential_owner_type": "service_account", "project_id": "project-test",
              "model_identifier": "test-model-snapshot", "prompt_id": "TEST-ONLY",
              "prompt_version": "1", "venue_canon_id": "TEST-ONLY", "policy_id": "TEST-ONLY"}
    for key in ("instruction", "venue_canon", "policy"):
        raw = ("existing frozen " + key).encode()
        (tmp_path / (key + ".txt")).write_bytes(raw)
        config[key] = {"path": key + ".txt", "sha256": hashlib.sha256(raw).hexdigest()}
    context = {"execution_id": "A-EXEC", "race_id": "A", "source_binding": {"source": "a"},
               "current_authority": {"manifest_id": "frozen-authority",
                                     "effective_at": "2030-01-01T00:00:00+00:00"},
               "production_numerical_authority": {"status": "NOT_READY", "full_numerical_authority": False},
               "source_verification": {"verified": True},
               "prediction_cutoff": "2030-01-01T01:00:00+00:00",
               "release_deadline_at": "2030-01-01T01:10:00+00:00",
               "signed_source": {"receipt": {"race_id": "A", "phase": "SOURCE"},
                                 "artifact": {"formal_ready": True,
                                              "source_freeze_at": "2030-01-01T00:59:00+00:00",
                                              "active_runner_universe": {"runner_count": 2,
                                                                         "runners": [{"runner_id": "1"}, {"runner_id": "2"}]}}}}
    prediction = {"ranking": ["1", "2"], "roles": [{"runner_id": "1", "columns": ["W"]},
                                                        {"runner_id": "2", "columns": ["P2"]}],
                  "role_registry": [{"runner_id": "1", "column": "W", "status": "CORE"},
                                    {"runner_id": "2", "column": "P2", "status": "CORE"}],
                  "pair_dispositions": [{"head": "1", "second": "2", "status": "PURCHASE", "reason": "evidence"}],
                  "third_dispositions": [], "uncertainty": {"level": "UNKNOWN", "reasons": ["missing"]},
                  "alternative_winner": "UNKNOWN", "partial_order": [], "ties": [],
                  "unresolved": ["unsupported concepts"], "evidence_conflict": "UNKNOWN", "market_conflict": "UNKNOWN",
                  "venue_prediction_context": {"interpretation": "frozen", "evidence_refs": ["SOURCE"]}}
    now = dt.datetime(2030, 1, 1, 1, 1, tzinfo=dt.timezone.utc)
    def call(payload, timeout):
        assert payload["store"] is False
        assert payload["text"]["format"]["strict"] is True
        assert "static_prediction" not in payload["input"]
        data = json.loads(payload["input"])
        assert data["numerical_authority"]["status"] == "NOT_READY"
        assert data["missingness"]["policy"] == "UNKNOWN_NO_PROXY"
        return {"id": "resp_test", "model": config["model_identifier"], "status": "completed",
                "output": [{"content": [{"type": "output_text", "text": json.dumps(prediction)}]}]}
    return context, config, prediction, call, now


def run(sample, tmp_path):
    context, config, _, call, now = sample
    return owner.execute(context, config, root=tmp_path, call=call, now=now)


def test_structured_owner_freezes_lineage_without_production_effect(sample, tmp_path):
    result = run(sample, tmp_path)
    assert result["promotion"] == "HOLD"
    assert result["production_authorized"] is False
    assert result["lineage"]["prediction_output_sha256"] == owner.digest(result["prediction"])
    for key in ("source_sha256", "venue_canon_sha256", "current_authority_sha256",
                "instruction_sha256", "schema_sha256", "model_identifier",
                "api_response_identifier", "freeze_timestamp", "prompt_id", "prompt_version",
                "input_schema_sha256", "output_schema_sha256", "policy_sha256", "authority_id"):
        assert result["lineage"][key]


@pytest.mark.parametrize("key", ["prompt_id", "prompt_version", "venue_canon_id", "policy_id"])
def test_unversioned_prompt_or_policy_is_hold(sample, tmp_path, key):
    sample[1].pop(key)
    with pytest.raises(owner.CandidateHold, match="VERSIONED_PROMPT_POLICY"):
        run(sample, tmp_path)


def test_changed_policy_cannot_reuse_pinned_owner(sample, tmp_path):
    (tmp_path / "policy.txt").write_text("changed policy")
    with pytest.raises(owner.CandidateHold, match="PINNED_INPUT_DIGEST_MISMATCH"):
        run(sample, tmp_path)


@pytest.mark.parametrize("key", ["ties", "partial_order"])
def test_self_partial_order_or_tie_rejected(sample, tmp_path, key):
    sample[2][key] = [["1", "1"]]
    with pytest.raises(owner.CandidateHold, match="INVALID_PARTIAL_ORDER"):
        run(sample, tmp_path)


@pytest.mark.parametrize("key,value", [("mode", "PRODUCTION"), ("production_authorized", True),
                                      ("credential_owner_type", "user"), ("project_id", "")])
def test_rejects_personal_key_metadata_and_promotion(sample, tmp_path, key, value):
    sample[1][key] = value
    with pytest.raises(owner.CandidateHold):
        run(sample, tmp_path)


@pytest.mark.parametrize("key", ["official_result", "finish_order", "payouts", "settlement",
                               "candidate_indices", "krs_ranking", "odds_ranking", "popularity_ranking"])
def test_outcome_or_substitute_ranking_never_enters_api(sample, tmp_path, key):
    sample[0]["signed_source"]["artifact"][key] = [1, 2]
    with pytest.raises(owner.CandidateHold, match="FORBIDDEN"):
        run(sample, tmp_path)


@pytest.mark.parametrize("case", ["source_partial", "verification", "race", "cutoff", "deadline", "canon_hash"])
def test_invalid_authority_temporal_and_source_hold(sample, tmp_path, case):
    context, config, _, _, _ = sample
    if case == "source_partial": context["signed_source"]["artifact"]["formal_ready"] = False
    if case == "verification": context["source_verification"]["verified"] = False
    if case == "race": context["signed_source"]["receipt"]["race_id"] = "OTHER"
    if case == "cutoff": context["signed_source"]["artifact"]["source_freeze_at"] = "2030-01-01T01:02:00+00:00"
    if case == "deadline": context["release_deadline_at"] = "2030-01-01T01:00:00+00:00"
    if case == "canon_hash": config["venue_canon"]["sha256"] = "bad"
    with pytest.raises(owner.CandidateHold): run(sample, tmp_path)


@pytest.mark.parametrize("case", ["duplicate_rank", "outside_universe", "schema_extra", "roles", "self_pair", "secret"])
def test_invalid_response_rejected_before_artifact(sample, tmp_path, case, monkeypatch):
    prediction = sample[2]
    if case == "duplicate_rank": prediction["ranking"] = ["1", "1"]
    if case == "outside_universe": prediction["ranking"] = ["1", "3"]
    if case == "schema_extra": prediction["candidate_score"] = 100
    if case == "roles": prediction["role_registry"] = []
    if case == "self_pair": prediction["pair_dispositions"][0]["second"] = "1"
    if case == "secret":
        monkeypatch.setenv("OPENAI_API_KEY", "test-private-value")
        prediction["uncertainty"]["reasons"] = ["test-private-value"]
    with pytest.raises(owner.CandidateHold): run(sample, tmp_path)


def test_comparison_requires_identical_source_and_never_promotes(sample, tmp_path):
    result = run(sample, tmp_path)
    p = sample[2]
    baseline = {"static_prediction": {"ranking": p["ranking"], "roles": {"1": ["W"], "2": ["P2"]},
                                      "uncertainty": p["uncertainty"]},
                **{key: p[key] for key in ("role_registry", "pair_dispositions", "third_dispositions", "venue_prediction_context")}}
    comparison = owner.compare(result, baseline, sample[0]["source_binding"])
    assert comparison["status"] == "UNKNOWN"
    assert comparison["metrics"]["ranking"]["status"] == "MATCH"
    assert comparison["metrics"]["alternative_winner"]["status"] == "UNKNOWN"
    assert comparison["production_equivalence"] == "NOT_CLAIMED"
    with pytest.raises(owner.CandidateHold, match="SOURCE_BASIS"):
        owner.compare(result, baseline, {"source": "changed"})
    baseline["static_prediction"]["ranking"] = ["2", "1"]
    assert owner.compare(result, baseline, sample[0]["source_binding"])["status"] == "DIFFERENCE"


def test_runtime_secret_absent_does_not_create_personal_key_or_leak(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(owner.CandidateHold, match="SERVICE_ACCOUNT_RUNTIME_SECRET_MISSING"):
        owner.responses_call({}, timeout=1)


def test_shadow_hold_is_nonblocking_and_diagnostic_is_sanitized(tmp_path, monkeypatch):
    monkeypatch.setattr(orchestrator, "ROOT", tmp_path)
    def fail(*args, **kwargs):
        raise RuntimeError("SECRET MUST NOT BE SAVED")
    monkeypatch.setattr(owner, "pinned_text", fail)
    report = orchestrator.execute_prediction_owner_shadow(
        {"openai_prediction_owner_candidate_config": {}}, run_id="test", github_sha="sha", tmp_root=tmp_path)
    assert report == {"status": "HOLD", "code": "SHADOW_RUNTIME_HOLD", "production_effect": "NONE", "promotion": "HOLD"}


@pytest.mark.parametrize("case", ["refusal", "incomplete", "model", "missing_id"])
def test_provider_response_integrity(sample, tmp_path, case):
    context, config, _, original, now = sample
    def altered(payload, timeout):
        response = original(payload, timeout)
        if case == "refusal": response["output"][0]["content"] = [{"type": "refusal", "refusal": "no"}]
        if case == "incomplete": response["status"] = "incomplete"
        if case == "model": response["model"] = "different-model"
        if case == "missing_id": response.pop("id")
        return response
    with pytest.raises(owner.CandidateHold):
        owner.execute(context, config, root=tmp_path, call=altered, now=now)


def test_shadow_reserves_production_deadline_budget(sample, tmp_path):
    sample[0]["release_deadline_at"] = "2030-01-01T01:02:00+00:00"
    with pytest.raises(owner.CandidateHold, match="PROTECT_PRODUCTION"):
        run(sample, tmp_path)


@pytest.mark.parametrize("effective,code", [
    (None, "AUTHORITY_EFFECTIVE_AT_REQUIRED"),
    ("2030-01-01T01:00:01+00:00", "POST_CUTOFF_AUTHORITY_HOLD"),
])
def test_authority_temporal_purity_before_api(sample, tmp_path, effective, code):
    sample[0]["current_authority"]["effective_at"] = effective
    with pytest.raises(owner.CandidateHold, match=code):
        run(sample, tmp_path)


def test_real_fnb_frozen_source_owner_input_excludes_research_and_acceptance():
    root = pathlib.Path(__file__).resolve().parents[1]
    store = root / "runtime/executions/LOCAL-KM-LOCAL-FNB-20261001-R08-LIVE-R1-EXEC/SOURCE/runs/36840937924"
    envelope = json.loads((store / "source_receipt_envelope.json").read_text())
    authority = json.loads((root / "profiles/KM_FAMILY_CURRENT_AUTHORITY_20260929_R35.json").read_text())
    cutoff = owner.timestamp(envelope["artifact"]["prediction_cutoff"])
    original_source_sha = owner.digest(envelope)
    original_authority_sha = owner.digest(authority)
    projected_authority = owner.prediction_authority_input(authority, cutoff)
    assert projected_authority["family_scoped_authority"]["LOCAL"]["numerical_authority_status"].startswith("NOT_READY")
    for key in ("local_acceptance_evidence", "single_entry_r2_acceptance", "dynamic_measurement_state"):
        assert key not in projected_authority
    assert "mec_measurement" not in projected_authority["family_scoped_authority"]["LOCAL"]
    projected_source = owner.prediction_source_input(envelope)
    assert projected_source["signed_envelope_sha256"] == original_source_sha
    assert projected_source["source_receipt_sha256"] == envelope["receipt_sha256"]
    assert projected_source["source_snapshot_sha256"] == envelope["artifact"]["source_snapshot_sha256"]
    assert projected_source["projection_is_signed_artifact"] is False
    assert "sbo_public_shadow_evidence" not in projected_source["artifact_projection"]
    assert projected_source["artifact_projection"]["active_runner_universe"]["runner_count"] == 10
    # Earlier official races observed in the frozen pre-cutoff source are legal
    # Current-State evidence. Do not erase these together with research metrics.
    assert "same_day_r07_result_tables" in projected_source["artifact_projection"]["normalized_evidence"]
    assert owner.digest(envelope) == original_source_sha
    assert owner.digest(authority) == original_authority_sha
    current = json.loads((root / "profiles/KM_FAMILY_CURRENT_AUTHORITY_20261001_R36.json").read_text())
    with pytest.raises(owner.CandidateHold, match="POST_CUTOFF_AUTHORITY_HOLD"):
        owner.prediction_authority_input(current, cutoff)


def test_projected_input_not_full_authority_or_shadow_source(sample, tmp_path):
    context, config, _, call, now = sample
    context["current_authority"].update({
        "dynamic_measurement_state": {"opaque": "private-research-marker"},
        "family_scoped_authority": {"LOCAL": {
            "numerical_authority_status": "NOT_READY",
            "mec_measurement": {"opaque": "private-measurement-marker"}}}})
    context["signed_source"]["artifact"]["sbo_public_shadow_evidence"] = "private-shadow-marker"
    def inspect(payload, timeout):
        assert all(marker not in payload["input"] for marker in (
            "private-research-marker", "private-measurement-marker", "private-shadow-marker"))
        return call(payload, timeout)
    result = owner.execute(context, config, root=tmp_path, call=inspect, now=now)
    assert result["lineage"]["input_contract_version"] == owner.INPUT_CONTRACT_VERSION
    assert result["lineage"]["current_authority_sha256"] == owner.digest(context["current_authority"])
    assert result["lineage"]["source_sha256"] == owner.digest(context["signed_source"])


def test_new_c2_prompt_pins_and_legacy_provenance_terminalization():
    root = pathlib.Path(__file__).resolve().parents[1]
    config = json.loads((root/'research/owner_candidate/KM_LOCAL_OPENAI_OWNER_CANDIDATE_v1.json').read_text())
    assert config['candidate_id'] == owner.CANDIDATE_ID
    assert config['production_authorized'] is False
    assert isinstance(config['credential_attestation_verified'], bool)
    if config['credential_attestation_verified']:
        assert config['project_id'] and config['service_account_id']
        assert config['credential_owner_type'] == 'service_account'
    assert config['automatic_promotion'] is False
    assert config['production_effect'] == 'NONE'
    assert config['credential_environment'] == 'keibametrics-staging'
    for spec in [config['instruction'],config['policy'],config['venue_canon'],config['maturity_promotion'],*config['normative_sources']]:
        owner.pinned_text(root,spec)
    policy=json.loads(owner.pinned_text(root,config['policy']))
    assert policy['legacy_provenance_is_permanent_merge_gate'] is False
    audit=json.loads((root/'research/execution/OWNER_REALITY_AUDIT_20261002.json').read_text())
    assert all(r['classification']=='LEGACY EXTERNAL PREDICTION OWNER / PROVENANCE INCOMPLETE' for r in audit['findings'])
    assert audit['historical_provenance_terminal']=='UNKNOWN / NOT_FAIL / NOT_PROVEN'


def test_live_secret_absent_precedes_metadata_and_no_api(sample,tmp_path,monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    sample[1]['project_id']=None
    with pytest.raises(owner.CandidateHold,match='SERVICE_ACCOUNT_RUNTIME_SECRET_MISSING'):
        owner.execute(sample[0],sample[1],root=tmp_path,now=sample[4])


def test_historical_comparison_cannot_become_forward_oos(sample,tmp_path):
    context,config,_,call,now=sample
    context['release_deadline_at']='2029-12-31T23:59:00+00:00'
    context['execution_class']='HISTORICAL_BEHAVIORAL_COMPARISON'
    report=owner.execute(context,config,root=tmp_path,call=call,now=now)
    assert report['status']=='HISTORICAL_COMPARISON_FROZEN'
    assert report['lineage']['historical_oos_eligible'] is False
    assert report['lineage']['credential_attestation']['api_authentication']=='NOT_TESTED'
    assert report['automatic_promotion'] is False


@pytest.mark.parametrize('case,code',[('attestation','SERVICE_ACCOUNT_ATTESTATION_REQUIRED'),('environment','STAGING_ENVIRONMENT_REQUIRED'),('identity','SERVICE_ACCOUNT_ID_REQUIRED')])
def test_real_api_activation_requires_staging_identity(sample,tmp_path,monkeypatch,case,code):
    monkeypatch.setenv('OPENAI_API_KEY','credential-not-printed')
    monkeypatch.setenv('GITHUB_ACTIONS','true')
    monkeypatch.setenv('KM_CREDENTIAL_ENVIRONMENT','keibametrics-staging')
    config=sample[1]
    config.update(credential_attestation_verified=True,credential_environment='keibametrics-staging',service_account_id='service-test')
    if case=='attestation': config['credential_attestation_verified']=False
    if case=='environment': monkeypatch.setenv('KM_CREDENTIAL_ENVIRONMENT','production')
    if case=='identity':config['service_account_id']=None
    with pytest.raises(owner.CandidateHold,match=code):
        owner.execute(sample[0],config,root=tmp_path,now=sample[4])


def test_behavioral_comparison_all_requested_metrics_no_bug_claim(sample,tmp_path):
    report=run(sample,tmp_path)
    prediction=sample[2]
    baseline={'static_prediction':{'ranking':prediction['ranking'],'roles':{'1':['W'],'2':['P2']},'uncertainty':prediction['uncertainty']},
              **{key:prediction[key] for key in ('pair_dispositions','third_dispositions','venue_prediction_context','unresolved')}}
    measured=owner.compare(report,baseline,sample[0]['source_binding'])
    assert set(measured['metrics'])=={'ranking','W','P2','P3','alternative_winner','Pair','Third','uncertainty','unresolved','venue_interpretation'}
    assert measured['metrics']['ranking']['position_agreement']==1
    assert measured['metrics']['W']['intersection']==1
    assert measured['difference_classification']=='NOT_AUTOMATICALLY_A_BUG'
    assert measured['promotion']=='HOLD'


def test_historical_three_races_read_only_frozen_basis_not_result(tmp_path):
    root=pathlib.Path(__file__).resolve().parents[1]
    config=json.loads((root/'research/owner_candidate/KM_LOCAL_OPENAI_OWNER_CANDIDATE_v1.json').read_text())
    config['project_id']='TEST-ONLY-NOT-A-CREDENTIAL'
    inputs=[]
    def call(payload,timeout):
        data=json.loads(payload['input']); inputs.append(data)
        ids=[str(r['runner_id']) for r in data['runner_universe']['runners']]
        p={'ranking':ids,'roles':[{'runner_id':i,'columns':[]} for i in ids],
           'role_registry':[],'pair_dispositions':[],'third_dispositions':[],
           'uncertainty':{'level':'UNKNOWN','reasons':['TEST TRANSPORT ONLY']},
           'alternative_winner':'UNKNOWN','partial_order':[],'ties':[],'unresolved':['TEST TRANSPORT ONLY'],
           'evidence_conflict':'UNKNOWN','market_conflict':'UNKNOWN',
           'venue_prediction_context':{'interpretation':'TEST TRANSPORT ONLY','evidence_refs':[]}}
        return {'id':'resp_test_not_real','model':config['model_identifier'],'status':'completed',
                'output':[{'content':[{'type':'output_text','text':json.dumps(p)}]}]}
    report=owner.historical_behavioral_comparison(config,root=root,verify=lambda e:{'verified':True},call=call)
    assert len(report['comparisons'])==3 and report['count_increment']==0
    assert report['oos_eligible'] is False
    for data in inputs:
        assert 'static_prediction' not in data
        assert 'official_result' not in data
        assert 'mec_measurement' not in data['current_authority']['family_scoped_authority']['LOCAL']
    assert all(r['candidate']['lineage']['credential_attestation']['api_authentication']=='NOT_TESTED' for r in report['comparisons'])


def test_post_result_utility_separates_pfs_and_rejects_lineage_or_tamper(sample,tmp_path):
    context,_,p,_,_=sample
    context['source_binding']={'execution_id':'A-EXEC','source_receipt_sha256':'source','source_snapshot_sha256':'snapshot'}
    context['signed_source']['artifact']['active_runner_universe']={'runner_count':3,'runners':[{'runner_id':str(i)} for i in (1,2,3)]}
    p['ranking']=['1','2','3'];p['roles'].append({'runner_id':'3','columns':[]})
    candidate=run(sample,tmp_path)
    baseline={'static_prediction':{'ranking':['2','1','3'],'roles':{'2':['W'],'1':['P2'],'3':['P3']}}}
    final={'receipt_sha256':'final','receipt':{'race_id':'A'},'artifact':{'source_receipt_sha256':'source','source_snapshot_sha256':'snapshot'}}
    result={'receipt_sha256':'result','receipt':{'race_id':'A','phase':'RESULT','status':'PASS'},
            'artifact':{'frozen_refs':{'final_receipt_sha256':'final'},'official_result':{'finish_order':[2,1,3]}}}
    report=owner.post_result_prediction_utility(candidate,baseline,context['source_binding'],final,result,{'verified':True})
    assert report['candidate']['Winner_rank']==2 and report['legacy']['Winner_rank']==1
    assert report['role_changes']['W']['false_promotions']==['1']
    assert report['role_changes']['W']['false_demotions']==['2']
    assert report['count_increment']==0 and report['actual_purchase_pfs']=='UNKNOWN'
    assert report['uncertainty_quality'].startswith('UNKNOWN')
    with pytest.raises(owner.CandidateHold,match='VERIFICATION_REQUIRED'):
        owner.post_result_prediction_utility(candidate,baseline,context['source_binding'],final,result,{'verified':False})
    candidate['prediction']['ranking']=['3','2','1']
    with pytest.raises(owner.CandidateHold,match='RACE_OR_PREDICTION_MISMATCH'):
        owner.post_result_prediction_utility(candidate,baseline,context['source_binding'],final,result,{'verified':True})


def test_owner_measurement_failure_does_not_block_production(tmp_path,monkeypatch):
    monkeypatch.setattr(orchestrator,'resolve_phase',lambda *a,**k:{'bad':'checkpoint'})
    report=orchestrator.measure_prediction_owner_shadow('A',run_id='test',github_sha='test',runtime_out=tmp_path,tmp_root=tmp_path)
    assert report['status']=='HOLD' and report['production_effect']=='NONE'


def test_project_scoped_auth_request_never_logs_provider_body(monkeypatch):
    import urllib.error
    monkeypatch.setenv('OPENAI_API_KEY','test-credential-do-not-print')
    observed=[]
    def forbidden(req,timeout):
        observed.append(req.get_header('Openai-project'))
        raise urllib.error.HTTPError(req.full_url,401,'SECRET BODY MUST NOT APPEAR',{},None)
    monkeypatch.setattr(owner.urllib.request,'urlopen',forbidden)
    with pytest.raises(owner.CandidateHold) as exc:
        owner.responses_call({},timeout=1,project_id='proj-test')
    assert str(exc.value)=='OPENAI_API_AUTHENTICATION_HOLD'
    assert observed==['proj-test']
    # Existing credential boundary test also covers the formerly opaque HTTP
    # failure family; retain status codes only, never provider body/headers.
    for status, expected in [(400, 'OPENAI_API_HTTP_400_HOLD'),
                             (404, 'OPENAI_API_HTTP_404_HOLD'),
                             (429, 'OPENAI_API_HTTP_429_HOLD'),
                             (503, 'OPENAI_API_HTTP_5XX_HOLD')]:
        def reject(request, timeout):
            raise urllib.error.HTTPError(request.full_url, status, 'SECRET BODY', {}, None)
        monkeypatch.setattr(owner.urllib.request, 'urlopen', reject)
        with pytest.raises(owner.CandidateHold) as e:
            owner.responses_call({}, timeout=1, project_id='proj-test')
        assert str(e.value) == expected
        assert 'SECRET' not in str(e.value)

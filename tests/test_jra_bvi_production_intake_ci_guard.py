"""Existing acceptance workflow: automatic CI must never execute live research."""
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import types
import urllib.request

import pytest
import yaml

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
WORKFLOW=ROOT/'.github/workflows/km-jra-pedigree-production-intake-acceptance.yml'


def steps():
    return yaml.load(WORKFLOW.read_text(),Loader=yaml.BaseLoader)['jobs']['prove']['steps']


def python_body(step):
    return step['run'].split("python - <<'PY'\n",1)[1].rsplit('\nPY',1)[0]


def live_steps():
    markers=('--official-audit','scripts/jra_bvi_postcapture_real_closure.py',
             'python scripts/jra_bvi_pipeline_forward_shadow.py settle',
             'python scripts/jra_bvi_env_acceptance.py','gh attestation verify')
    return [s for s in steps() if any(marker in s.get('run','') for marker in markers)
            or s.get('uses','').startswith('actions/attest-')]


@pytest.mark.parametrize('event',['pull_request','push','workflow_dispatch'])
@pytest.mark.parametrize('day',['2026-10-17','2026-10-18','2026-10-25','2026-10-28'])
def test_actual_execution_guard_requires_manual_event_and_preserves_freeze_dates(tmp_path,monkeypatch,event,day):
    selected=next(s for s in steps() if s.get('id')=='external_window')
    class Clock(datetime):
        @classmethod
        def now(cls,tz=None):
            return datetime.fromisoformat(day+'T12:00:00+09:00').astimezone(tz)
    monkeypatch.setitem(sys.modules,'datetime',types.SimpleNamespace(datetime=Clock,timedelta=timedelta,timezone=timezone))
    monkeypatch.chdir(tmp_path);output=tmp_path/'outputs'
    monkeypatch.setenv('GITHUB_OUTPUT',str(output));monkeypatch.setenv('GITHUB_EVENT_NAME',event)
    exec(compile(python_body(selected),'<actual-external-guard>','exec'),{})
    allowed=event=='workflow_dispatch' and day=='2026-10-28'
    assert output.read_text()=='allowed='+str(allowed).lower()+'\n'
    deferred=tmp_path/'runtime_out/jra_bvi_external_acceptance_deferred.json'
    if not allowed:
        report=json.loads(deferred.read_text())
        assert report['status']==('DEFERRED_PRODUCTION_FREEZE' if event=='workflow_dispatch' else 'OFFLINE_CI_ONLY')
        assert report['external_diagnostics_executed'] is False
        assert report['model_training_executed'] is False and report['model_publication_executed'] is False
        assert report['oidc_verification_executed'] is False
        assert report['full_real_acceptance_pass_claimed'] is False


def test_every_external_oidc_training_publication_step_is_individually_guarded():
    selected=live_steps();assert len(selected)==6
    for step in selected:
        condition=step.get('if','')
        assert "github.event_name == 'workflow_dispatch'" in condition
        assert "steps.external_window.outputs.allowed == 'true'" in condition
    model=next(s for s in selected if s.get('id')=='env_model')
    # The no-flag/default CLI also trains: an else fallback must never exist.
    assert 'else' not in model['run']
    assert model['run'].strip()=='python scripts/jra_bvi_env_acceptance.py --abc-artifact runtime_out/jra_bvi_pipeline_real_acceptance.json --run-external'
    attest=next(s for s in selected if s.get('id')=='env_model_attest')
    assert "steps.env_model.outcome == 'success'" in attest['if']
    verify=next(s for s in selected if 'gh attestation verify' in s.get('run',''))
    assert "steps.env_model_attest.outcome == 'success'" in verify['if']


def test_automatic_ci_retains_offline_regressions_and_inventory_without_claiming_acceptance(tmp_path,monkeypatch):
    selected=next(s for s in steps() if s.get('name')=='Inventory tracked corpus and fixed publication evidence offline')
    assert not selected.get('if')
    def forbidden(*args,**kwargs):raise AssertionError('OFFLINE_CI_EXTERNAL_CALL')
    monkeypatch.setattr(urllib.request,'urlopen',forbidden)
    monkeypatch.setattr(subprocess,'run',forbidden)
    monkeypatch.chdir(tmp_path)
    exec(compile(python_body(selected),'<actual-offline-inventory>','exec'),{})
    report=json.loads((tmp_path/'runtime_out/jra_bvi_offline_inventory.json').read_text())
    assert report['classification']=='OFFLINE_INVENTORY_NOT_SOURCE_OR_READER_READMISSION'
    assert report['external_runtime_calls']==0 and report['oidc_reverification_executed'] is False
    assert report['new_source_acceptance']==report['new_model_publication']==report['new_forward_oos_credit']==0
    assert report['fixed_publication_verification']['fixed_model_and_bound_implementation_changed'] is False
    assert not list(tmp_path.rglob('*model_publication*'))
    assert any(s.get('name')=='Numerical lineage and temporal regression' for s in steps())
    assert any(s.get('run')=='python -m pytest -q tests/test_jra_bvi_env_acceptance.py' for s in steps())


@pytest.mark.parametrize('filename,job', [
    ('km-jra-production-krs-20000-external-acceptance.yml', 'mechanical-krs-high'),
    ('km-jra-pedigree-live-smoke.yml', 'official-read-only'),
    ('km-jra-hsn12-v17-adapter-coverage.yml', 'diagnostic'),
])
def test_external_mechanical_and_source_jobs_require_manual_event(filename, job):
    workflow = yaml.load((ROOT / '.github/workflows' / filename).read_text(), Loader=yaml.BaseLoader)
    assert 'workflow_dispatch' in workflow['on']
    # These jobs perform real HTTP work. PR/push must skip the entire job,
    # including dependency setup and any diagnostic persistence step.
    assert workflow['jobs'][job]['if'] == "github.event_name == 'workflow_dispatch'"


def test_bound_evidence_regressions_run_in_existing_offline_ci():
    workflow = yaml.load((ROOT / '.github/workflows/km-jra-single-entry-repair-regression.yml').read_text(),
                         Loader=yaml.BaseLoader)
    paths = workflow['on']['pull_request']['paths']
    commands = '\n'.join(step.get('run', '') for step in workflow['jobs']['repair']['steps'])
    for path in ('tests/test_jra_class_zero_corpus.py', 'tests/test_jra_precalculated_trace_reuse.py',
                 'tests/test_jra_bvi_production_intake_ci_guard.py',
                 'tests/test_jra_registered_common_cancelled.py',
                 'tests/test_jra_current_equipment_observation.py'):
        assert path in paths and path in commands
    for path in ('km-jra-pedigree-production-intake-acceptance.yml',
                 'km-jra-production-krs-20000-external-acceptance.yml',
                 'km-jra-pedigree-live-smoke.yml', 'km-jra-hsn12-v17-adapter-coverage.yml',
                 'km-jra-production-source-closure-real.yml',
                 'km-jra-person-stats-v11-acceptance.yml'):
        assert '.github/workflows/' + path in paths


def test_historical_offline_audits_cannot_launch_oidc_without_credentials(monkeypatch):
    targets = {
        'km-jra-production-source-closure-real.yml': ('source-closure', (
            'Execute Production numerical preparation on immutable Tokyo R05 JRA SOURCE',
            'Recompute source-verified real Kyoto R09 Production evidence after new evaluators')),
        'km-jra-single-entry-repair-regression.yml': ('repair', (
            'Recompute immutable real SOURCE as historical diagnostics',)),
    }
    for filename, (job_name, names) in targets.items():
        workflow = yaml.load((ROOT / '.github/workflows' / filename).read_text(), Loader=yaml.BaseLoader)
        job = workflow['jobs'][job_name]
        steps_by_name = {step.get('name'): step for step in job['steps']}
        for name in names:
            supplied = {**(workflow.get('env') or {}), **(job.get('env') or {}),
                        **(steps_by_name[name].get('env') or {})}
            if {'GH_TOKEN', 'GITHUB_TOKEN'} & supplied.keys():
                assert steps_by_name[name].get('if') == "github.event_name == 'workflow_dispatch'"
            else:
                assert not {'GH_TOKEN', 'GITHUB_TOKEN'} & supplied.keys()
    monkeypatch.delenv('GH_TOKEN', raising=False)
    monkeypatch.delenv('GITHUB_TOKEN', raising=False)
    def forbidden(*args, **kwargs):
        raise AssertionError('OFFLINE_CORPUS_MUST_NOT_LAUNCH_GH')
    monkeypatch.setattr(subprocess, 'run', forbidden)
    sys.path.insert(0, str(ROOT / 'runtime'))
    from jra_pedigree_corpus import _attested
    assert _attested(Path('no-file-is-read-without-a-token.json')) is False


def test_current_person_live_lane_and_persistence_are_manual_but_unit_test_remains_automatic():
    workflow = yaml.load((ROOT / '.github/workflows/km-jra-person-stats-v11-acceptance.yml').read_text(),
                         Loader=yaml.BaseLoader)
    assert 'workflow_dispatch' in workflow['on']
    steps = workflow['jobs']['acceptance']['steps']
    unit = next(step for step in steps if step.get('name') == 'Bounded current-card selection regression')
    assert not unit.get('if') and unit['run'] == 'python -m pytest -q tests/test_jra_live_person_stats_acceptance.py'
    live = next(step for step in steps if step.get('name') == 'Current-card token and person-stat mechanical acceptance')
    persisted = next(step for step in steps if step.get('name') == 'Persist')
    assert live['if'] == persisted['if'] == "github.event_name == 'workflow_dispatch'"
    artifact = next(step for step in steps if step.get('uses', '').startswith('actions/upload-artifact@'))
    assert artifact['if'] == "always() && github.event_name == 'workflow_dispatch'"

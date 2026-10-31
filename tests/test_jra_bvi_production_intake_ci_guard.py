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


def test_existing_pedigree_live_smoke_is_manual_only_without_changing_schedule():
    workflow=ROOT/'.github/workflows/km-jra-pedigree-live-smoke.yml'
    doc=yaml.load(workflow.read_text(),Loader=yaml.BaseLoader)
    assert 'workflow_dispatch' in doc['on']
    assert 'schedule' not in doc['on']
    job=doc['jobs']['official-read-only']
    assert job['if']=="github.event_name == 'workflow_dispatch'"
    assert any('--date 2026-10-04' in step.get('run','') for step in job['steps'])
    assert any('--date 2022-01-05' in step.get('run','') for step in job['steps'])


def test_existing_learning_binding_automatic_checks_stay_offline():
    workflow=ROOT/'.github/workflows/km-jra-learning-binding-audit.yml'
    doc=yaml.load(workflow.read_text(),Loader=yaml.BaseLoader)
    assert {'pull_request','push','workflow_dispatch'}<=set(doc['on'])
    expected={'Recover exact stored official locators and reverify existing OIDC intake',
              'Read authenticated Workflow states after rate reset',
              'Snapshot existing Owner scope approval through read-only provider API'}
    selected=[]
    for job in doc['jobs'].values():
        assert not job.get('if')
        for step in job['steps']:
            if step.get('name') in expected:
                assert step['if']=="github.event_name == 'workflow_dispatch'"
                selected.append(step['name'])
            elif 'python -m pytest' in step.get('run','') or 'python -m unittest' in step.get('run',''):
                assert not step.get('if')
    assert set(selected)==expected


@pytest.mark.parametrize('event', ['pull_request', 'push', 'workflow_dispatch'])
def test_existing_source_closure_oidc_recomputations_require_manual_event(event):
    workflow=ROOT/'.github/workflows/km-jra-production-source-closure-real.yml'
    doc=yaml.load(workflow.read_text(),Loader=yaml.BaseLoader)
    assert {'pull_request','push','workflow_dispatch'}<=set(doc['on'])
    job=doc['jobs']['source-closure']
    assert not job.get('if')  # Normal offline regression stays automatic.
    names={'Execute Production numerical preparation on immutable Tokyo R05 JRA SOURCE',
           'Recompute source-verified real Kyoto R09 Production evidence after new evaluators'}
    selected=[]
    for step in job['steps']:
        if step.get('name') in names:
            condition=step['if']
            assert condition=="github.event_name == 'workflow_dispatch'"
            assert 'GH_TOKEN' in (step.get('env') or {})
            enabled=eval(condition.replace('github.event_name',repr(event)),{'__builtins__':{}},{})
            assert enabled is (event=='workflow_dispatch')
            selected.append(step['name'])
        elif 'python -m pytest' in step.get('run',''):
            assert not step.get('if')
        else:
            assert not {'GH_TOKEN','GITHUB_TOKEN'} & set(step.get('env') or {})
    assert set(selected)==names
    assert any('python -m pytest' in step.get('run','') and not step.get('if') for step in job['steps'])

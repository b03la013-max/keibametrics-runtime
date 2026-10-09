from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / '.github/workflows/km-local-c2-staging-real-api-manual.yml'
RUNBOOK = ROOT / 'tools/LOCAL_FORMAL_RESTART.md'


def test_staging_acceptance_is_manual_and_unprivileged():
    s = WORKFLOW.read_text(encoding='utf-8')
    assert '\n  workflow_dispatch:' in s
    assert '\n  push:' not in s
    assert '\n  schedule:' not in s
    assert '  contents: read' in s
    assert '  contents: write' not in s
    assert 'environment: keibametrics-staging' in s
    assert 'persist-credentials: false' in s
    assert 'ref: 1033c818bf2451ccb9496ae017c7aea0c35ad13e' in s
    assert 'git rev-parse HEAD' in s
    assert "spec['production_authorized'] is False" in s
    assert "spec['automatic_promotion'] is False" in s
    assert 'secrets.OPENAI_API_KEY' in s
    assert 'git push' not in s
    assert '--historical-comparison' in s
    assert 'runtime/aki_adaptive_purchase_shadow.py' not in s


def test_restart_runbook_does_not_claim_autonomous_activation():
    s = RUNBOOK.read_text(encoding='utf-8')
    assert 'OPENAI_API_429_CREDIT_BALANCE_EXHAUSTED_HOLD' in s
    assert 'submit_local_formal_intent.py --intent' in s
    assert 'Autonomous one-trigger end-to-end is still NO' in s
    assert 'not FINAL-PASS' in s

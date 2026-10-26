"""Collector failure evidence; synthetic HTTP/clock data grants no authority."""
from __future__ import annotations

from contextlib import redirect_stdout
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import sys
import textwrap
from urllib.error import HTTPError

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'runtime'), str(ROOT / 'runtime/jra_source_runtime')]
import scripts.jra_weekend_bvi_intake as intake

WORKFLOW = '.github/workflows/km-jra-pedigree-corpus-harvest.yml'


def plan_script(text=None):
    text = text if text is not None else (ROOT / WORKFLOW).read_text()
    return textwrap.dedent(text.split("          python - <<'PY'\n", 1)[1]
                          .split('          PY\n', 1)[0])


def execute_plan(tmp_path, monkeypatch, *, code=None, event='workflow_dispatch'):
    monkeypatch.chdir(tmp_path)
    for key, value in {'EVENT': event, 'DATES': '2026-10-24', 'MODE': 'results',
                       'GITHUB_OUTPUT': str(tmp_path / 'outputs')}.items():
        monkeypatch.setenv(key, value)
    import urllib.request
    monkeypatch.setattr(urllib.request, 'urlopen', lambda *a, **k:
                        io.BytesIO(b'User-agent: *\nAllow: /\n'))
    output = io.StringIO()
    with redirect_stdout(output):
        exec(compile(code if code is not None else plan_script(), WORKFLOW, 'exec'), {})
    return output.getvalue()


class DeniedCalendar:
    def __init__(self, code):
        self.calls = []
        self.code = code

    def get(self, path):
        self.calls.append(path)
        exc = HTTPError('https://www.jra.go.jp' + path, self.code, 'Forbidden',
                        {'Retry-After': '600'}, None)
        exc.official_request = {'url': exc.url, 'method': 'GET',
                                'phase': 'CONNECT_TLS_OR_RESPONSE_HEADERS', 'attempt': 1}
        raise exc

    def post(self, *args):
        pytest.fail('A refused Calendar must not trigger a navigation POST')


@pytest.mark.parametrize('code', [403, 429])
def test_t10_plan_refusal_saves_diagnostic_and_does_not_report_zero_success(tmp_path, monkeypatch, code):
    calendar = DeniedCalendar(code)
    existing = intake.day_plan
    monkeypatch.setattr(intake, 'day_plan', lambda day, mode:
                        existing(day, mode, client=calendar))
    with pytest.raises(HTTPError) as caught:
        execute_plan(tmp_path, monkeypatch)
    assert caught.value.code == code
    assert len(calendar.calls) == 1
    assert not (tmp_path / 'outputs').exists()
    assert not (tmp_path / 'runtime_out/pedigree_day_plan.json').exists()
    failure = json.loads((tmp_path / 'runtime_out/pedigree_day_plan_failure.json').read_text())
    assert failure['status'] == 'PLAN_FAILED'
    assert failure['stage'] == 'OFFICIAL_DAY_DISCOVERY'
    assert failure['error']['http_status'] == code
    assert failure['error']['url'].endswith('/1024.html')
    assert failure['error']['method'] == 'GET' and failure['error']['attempt'] == 1
    assert failure['error']['response_headers'] == {'Retry-After': '600'}
    assert failure['access_refused'] is True
    assert failure['official_target_races'] is None and failure['bounded_batches'] is None
    for name in ('Harvest', 'OIDC', 'Reader'):
        assert failure['downstream'][name] == {'status': 'NOT_EXECUTED_PLAN_FAILED', 'success_count': None}
    assert failure['forward_oos_increment'] == 0 and failure['production_effect'] == 'NONE'
    assert datetime.fromisoformat(failure['failed_at']).tzinfo is not None


def test_t10_workflow_uploads_failure_but_never_attests_or_harvests_failed_plan():
    jobs = yaml.safe_load((ROOT / WORKFLOW).read_text())['jobs']
    steps = jobs['plan']['steps']
    upload = next(s for s in steps if s.get('uses', '').startswith('actions/upload-artifact@'))
    attest = next(s for s in steps if s.get('uses', '').startswith('actions/attest@'))
    assert upload['if'] == 'always()'
    assert 'runtime_out/pedigree_day_plan_failure.json' in upload['with']['path']
    assert upload['with']['if-no-files-found'] == 'error'
    assert "steps.plan.outcome == 'success'" in attest['if']
    assert "needs.plan.result == 'success'" in jobs['harvest']['if']
    assert 'needs.plan.outputs.matrix' in jobs['harvest']['if']
    assert "needs.plan.result == 'success'" in jobs['summarize']['if']


def test_t10_original_failure_diagnostic_is_immutable(tmp_path):
    path = tmp_path / 'failure.json'
    timestamp = datetime(2026, 10, 26, tzinfo=timezone.utc)
    intake.write_plan_failure(path, ValueError('original'), stage='OFFICIAL_DAY_DISCOVERY',
                              planned_at=timestamp, failed_at=timestamp)
    before = path.read_bytes()
    with pytest.raises(FileExistsError):
        intake.write_plan_failure(path, ValueError('later'), stage='OTHER')
    assert path.read_bytes() == before


def test_t10_cli_day_plan_keeps_failure_separate_from_an_official_plan(tmp_path, monkeypatch):
    def refused(*args, **kwargs):
        raise HTTPError('https://www.jra.go.jp/keiba/calendar2026/2026/10/1024.html',
                        403, 'Forbidden', {}, None)
    monkeypatch.setattr(intake, 'day_plan', refused)
    plan = tmp_path / 'plan.json'
    monkeypatch.setattr(sys, 'argv', ['intake', 'day-plan', '--date', '2026-10-24',
                                     '--mode', 'results', '--plan', str(plan)])
    with pytest.raises(HTTPError):
        intake.main()
    assert not plan.exists()
    assert json.loads(plan.with_suffix('.failure.json').read_text())['status'] == 'PLAN_FAILED'


class OfficialDay:
    def __init__(self):
        self.calls = []
        self.days = [f'pw01srl00{c}2026040320261024/AB' for c in ('04', '05', '08')]

    def get(self, path):
        self.calls.append(path)
        return "doAction('/JRADB/accessS.html','ROOT')"

    def post(self, path, token):
        self.calls.append(token)
        if token == 'ROOT':
            return ' '.join(self.days)
        for code, day in zip(('04', '05', '08'), self.days):
            if token == day:
                return ' '.join(f'pw01sde01{code}20260403{n:02d}20261024/AB' for n in range(1, 13))
        pytest.fail('The Planner must not request a race/horse Source')


def test_t11_normal_12_batch_plan_bytes_and_matrix_are_preserved(tmp_path, monkeypatch):
    # The same observed day and same clock produce the exact previous plan SHA.
    import datetime as dt
    original_datetime = dt.datetime

    class FixedDatetime(original_datetime):
        @classmethod
        def now(cls, tz=None):
            now = original_datetime(2026, 10, 25, 16, 28, tzinfo=timezone.utc)
            return now.astimezone(tz) if tz else now.replace(tzinfo=None)

    monkeypatch.setattr(dt, 'datetime', FixedDatetime)
    actual_plan = intake.day_plan
    clients = []

    def observed_plan(day, mode):
        client = OfficialDay();clients.append(client)
        return actual_plan(day, mode, client=client)

    monkeypatch.setattr(intake, 'day_plan', observed_plan)
    new_dir = tmp_path / 'new';new_dir.mkdir()
    execute_plan(new_dir, monkeypatch)
    new = (new_dir / 'runtime_out/pedigree_day_plan.json').read_bytes()
    # Pinned from the preceding successful planner at the same fixture clock.
    # No git history/network is needed in a shallow CI checkout.
    assert hashlib.sha256(new).hexdigest() == 'c30d0e828d6742b2d5953ba5f2a3337672c8cbd833c88032da0d69eea868ff03'
    expected_matrix = {'include': [{'index': i} for i in range(12)]}
    assert (new_dir / 'outputs').read_text() == 'matrix=' + json.dumps(expected_matrix, separators=(',', ':')) + '\n'
    assert len(json.loads(new)['include']) == 12
    assert sum(len(w['race_ids']) for w in json.loads(new)['include']) == 36
    assert all(len(c.calls) == 8 for c in clients)
    assert not (new_dir / 'runtime_out/pedigree_day_plan_failure.json').exists()


def test_failure_after_successful_plan_save_preserves_its_original_bytes(tmp_path, monkeypatch):
    monkeypatch.setattr(intake, 'day_plan', lambda day, mode: [])
    (tmp_path / 'outputs').mkdir()  # An output-channel failure is not an empty-day assertion.
    with pytest.raises(IsADirectoryError):
        execute_plan(tmp_path, monkeypatch)
    plan = tmp_path / 'runtime_out/pedigree_day_plan.json'
    before = plan.read_bytes()
    failure = json.loads((tmp_path / 'runtime_out/pedigree_day_plan_failure.json').read_text())
    assert failure['stage'] == 'MATRIX_OUTPUT'
    assert failure['bounded_batches'] is None
    assert plan.read_bytes() == before


def test_existing_offline_corpus_reader_does_not_require_live_calendar(tmp_path, monkeypatch):
    """Isolated fixture verifier is not an actual OIDC/Production acceptance."""
    import jra_pedigree_corpus as corpus
    import jra_pedigree_harvest
    monkeypatch.setattr(jra_pedigree_harvest._Client, '_open',
                        lambda *a, **k: pytest.fail('Stored Corpus must not acquire Calendar/Source'))
    path = tmp_path / 'runtime/pedigree_corpus/synthetic.json';path.parent.mkdir(parents=True)
    obj = {'profile': corpus.HARVEST_PROFILE, 'official': True, 'source': 'www.jra.go.jp',
           'harvested_at': '2026-10-24T00:00:00Z', 'race_date': '2026-10-23', 'mode': 'results',
           'horse_count': 1, 'horse_token_count': 1, 'horses': [{
               'horse_name': 'UNIT', 'sire': 'UNIT-SIRE', 'dam': 'UNIT-DAM', 'damsire': 'UNIT-DS',
               'raw_sha256': 'a' * 64, 'runs': [{'date': '2026-09-03', 'venue': '京都', 'surface': '芝',
                   'distance_m': 1600, 'race_name': '2勝クラス', 'finish': 2, 'field_size': 12}]}]}
    obj['sha256'] = hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    path.write_text(json.dumps(obj));before = path.read_bytes()
    out = corpus.build_corpus(tmp_path, prediction_cutoff='2026-10-26T10:00:00Z',
                              race_date='2026-10-27', attestation_verifier=lambda p: True)
    assert out['horse_count'] == out['run_count'] == out['snapshot_count'] == 1
    assert out['valid_for_historical_OOS_recompute'] is False
    assert path.read_bytes() == before
    # No credentials or independent verifier means the same unsigned fixture is rejected.
    monkeypatch.delenv('GH_TOKEN', raising=False);monkeypatch.delenv('GITHUB_TOKEN', raising=False)
    rejected = corpus.build_corpus(tmp_path, prediction_cutoff='2026-10-26T10:00:00Z', race_date='2026-10-27')
    assert rejected['horse_count'] == 0 and rejected['rejected_untrusted_inputs'] == 1

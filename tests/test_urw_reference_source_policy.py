"""Robots decisions/rate limits without any external official card request."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import shutil
import sys
import urllib.error
import urllib.request

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
from runtime import urw_reference_source_policy as policy
from urw_reference_fixture_support import fixture_root


class Clock:
    def __init__(self): self.now = 1000.0
    def __call__(self): return self.now
    def sleep(self, seconds): self.now += seconds


class Response:
    status = 200
    def __init__(self, url, raw, content_type='text/plain; charset=UTF-8'):
        self.url = url; self.raw = raw; self.headers = {'Content-Type': content_type}
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def geturl(self): return self.url
    def read(self, count): return self.raw[:count]


class Opener:
    def __init__(self, clock, robots, *, failure=None, target_failure=None):
        self.clock = clock; self.robots = robots; self.failure = failure
        self.target_failure = target_failure; self.calls = []
    def open(self, request, timeout):
        self.calls.append((self.clock(), request.full_url, request.get_header('User-agent')))
        assert request.get_method() == 'GET' and timeout <= 15
        if request.full_url == policy.ROBOTS_URL:
            if self.failure: raise self.failure
            return Response(policy.ROBOTS_URL, self.robots)
        if self.target_failure: raise self.target_failure
        return Response(request.full_url, b'<h3>official mock bytes</h3>', 'text/html; charset=UTF-8')


def target(path='DebaTable'):
    return policy.ORIGIN + '/KeibaWeb/TodayRaceInfo/' + path + '?k_babaCode=18'


@pytest.mark.parametrize('path', ['DebaTable', 'OddsTanFuku', 'RaceList'])
def test_official_disallow_blocks_target_get_and_reports_url_and_rule(tmp_path, path):
    clock = Clock(); client = policy.UrwReferenceSourcePolicy(tmp_path, clock=clock, sleep=clock.sleep)
    opener = Opener(clock, b'User-agent: *\nDisallow: /KeibaWeb/TodayRaceInfo/\nCrawl-delay: 10\n')
    for _ in range(2):
        with pytest.raises(policy.SourcePolicyError, match='SOURCE_POLICY_ROBOTS_DISALLOWED') as caught:
            with client.open(opener, urllib.request.Request(target(path))): pytest.fail('target forbidden')
        assert caught.value.receipt['target_url'] == target(path)
        assert caught.value.receipt['reason'] == 'Disallow: /KeibaWeb/TodayRaceInfo/'
        assert caught.value.receipt['robots_url'] == policy.ROBOTS_URL
    assert [url for _, url, _ in opener.calls] == [policy.ROBOTS_URL]
    assert opener.calls[0][2] == policy.USER_AGENT and 'Googlebot' not in policy.USER_AGENT


@pytest.mark.parametrize('failure', [OSError('network unavailable'),
    urllib.error.HTTPError(policy.ROBOTS_URL, 404, 'not found', {}, None),
    urllib.error.HTTPError(policy.ROBOTS_URL, 403, 'forbidden', {}, None)])
def test_unknown_or_missing_robots_fails_closed_without_target_get(tmp_path, failure):
    clock = Clock(); client = policy.UrwReferenceSourcePolicy(tmp_path, clock=clock, sleep=clock.sleep)
    opener = Opener(clock, b'', failure=failure)
    with pytest.raises(policy.SourcePolicyError, match='SOURCE_POLICY_ROBOTS_UNKNOWN'):
        with client.open(opener, urllib.request.Request(target())): pytest.fail('target forbidden')
    assert [url for _, url, _ in opener.calls] == [policy.ROBOTS_URL]


@pytest.mark.parametrize('raw', [b'', b'<html>not policy</html>', b'User-agent: *\nCrawl-delay: nope\n', b'\xff'])
def test_unreadable_or_invalid_robots_is_not_assumed_allow(tmp_path, raw):
    clock = Clock(); client = policy.UrwReferenceSourcePolicy(tmp_path, clock=clock, sleep=clock.sleep)
    opener = Opener(clock, raw)
    with pytest.raises(policy.SourcePolicyError, match='SOURCE_POLICY_ROBOTS_UNKNOWN'):
        with client.open(opener, urllib.request.Request(target())): pytest.fail('target forbidden')
    assert len(opener.calls) == 1


@pytest.mark.parametrize('damage', ['status', 'type', 'identity'])
def test_robots_http_identity_and_type_are_required(tmp_path, damage):
    clock = Clock(); client = policy.UrwReferenceSourcePolicy(tmp_path, clock=clock, sleep=clock.sleep)
    class UnknownResponseOpener(Opener):
        def open(self, request, timeout):
            response = super().open(request, timeout)
            if damage == 'status': response.status = 204
            if damage == 'type': response.headers['Content-Type'] = 'text/plain-not-valid'
            if damage == 'identity': response.url = 'https://elsewhere.invalid/robots.txt'
            return response
    opener = UnknownResponseOpener(clock, b'User-agent: *\nAllow: /\n')
    with pytest.raises(policy.SourcePolicyError, match='SOURCE_POLICY_ROBOTS_UNKNOWN'):
        with client.open(opener, urllib.request.Request(target())): pytest.fail('unknown HTTP policy')
    assert [url for _, url, _ in opener.calls] == [policy.ROBOTS_URL]


def test_allowed_parallel_calls_share_cache_and_honor_crawl_delay(tmp_path):
    clock = Clock()
    clients = [policy.UrwReferenceSourcePolicy(tmp_path, clock=clock, sleep=clock.sleep) for _ in range(2)]
    opener = Opener(clock, b'User-agent: *\nAllow: /\nCrawl-delay: 12.5\n')
    def fetch(number):
        with clients[number % 2].open(opener, urllib.request.Request(target() + str(number))) as response:
            return response.read(100)
    with ThreadPoolExecutor(max_workers=3) as pool:
        assert list(pool.map(fetch, range(3))) == [b'<h3>official mock bytes</h3>'] * 3
    assert sum(url == policy.ROBOTS_URL for _, url, _ in opener.calls) == 1
    assert all(right[0] - left[0] >= 12.5 for left, right in zip(opener.calls, opener.calls[1:]))
    assert all(ua == policy.USER_AGENT for _, _, ua in opener.calls)


def test_retry_after_blocks_later_call_without_immediate_retry(tmp_path):
    clock = Clock(); client = policy.UrwReferenceSourcePolicy(tmp_path, clock=clock, sleep=clock.sleep)
    opener = Opener(clock, b'User-agent: *\nAllow: /\nCrawl-delay: 10\n',
        target_failure=urllib.error.HTTPError(target(), 429, 'slow down', {'Retry-After': '120'}, None))
    with pytest.raises(urllib.error.HTTPError):
        with client.open(opener, urllib.request.Request(target())): pytest.fail('429')
    with pytest.raises(policy.SourcePolicyError, match='SOURCE_POLICY_RETRY_NOT_READY'):
        with client.open(opener, urllib.request.Request(target())): pytest.fail('no retry yet')
    assert len(opener.calls) == 2
    assert json.loads((tmp_path / 'robots.json').read_text())['next_request_at'] == clock() + 120


def test_corrupt_cached_policy_never_grants_permission(tmp_path):
    clock = Clock(); client = policy.UrwReferenceSourcePolicy(tmp_path, clock=clock, sleep=clock.sleep)
    opener = Opener(clock, b'User-agent: *\nDisallow: /\n')
    with pytest.raises(policy.SourcePolicyError, match='ROBOTS_DISALLOWED'):
        with client.open(opener, urllib.request.Request(target())): pytest.fail('disallowed')
    path = tmp_path / 'robots.json'; cached = json.loads(path.read_text())
    cached['text'] = 'User-agent: *\nAllow: /\n'
    path.write_text(json.dumps(cached))
    with pytest.raises(policy.SourcePolicyError, match='ROBOTS_UNKNOWN'):
        with client.open(opener, urllib.request.Request(target())): pytest.fail('tampered policy')
    assert len(opener.calls) == 1


def test_longest_matching_allow_and_wildcard_deny_have_rfc_precedence():
    text = 'User-agent: *\nDisallow: /KeibaWeb/*\nAllow: /KeibaWeb/TodayRaceInfo/DebaTable\n'
    assert policy.robots_decision(text, target())['allowed']
    assert not policy.robots_decision(text, target('OddsTanFuku'))['allowed']
    text += 'User-agent: KeibaMetrics-URW-PublicResearch\nDisallow: /\n'
    assert not policy.robots_decision(text, target())['allowed']


def test_unsigned_transport_applies_policy_before_snapshot_or_target_get(tmp_path, monkeypatch):
    from scripts import urw_candidate_krs_replay as replay
    from runtime.local_physical.nar_source_manifest import _race_card_source
    clock = Clock()
    monkeypatch.setattr(policy, 'POLICY', policy.UrwReferenceSourcePolicy(tmp_path, clock=clock, sleep=clock.sleep))
    opener = Opener(clock, b'User-agent: *\nDisallow: /KeibaWeb/TodayRaceInfo/\nCrawl-delay: 10\n')
    monkeypatch.setattr(urllib.request, 'build_opener', lambda *handlers: opener)
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).strftime('%Y/%m/%d')
    with pytest.raises(policy.SourcePolicyError, match='SOURCE_POLICY_ROBOTS_DISALLOWED'):
        replay.fetch_public_urw_reference(_race_card_source('URW', '18', tomorrow, 1))
    assert [url for _, url, _ in opener.calls] == [policy.ROBOTS_URL]


def test_frozen_reference_readback_never_needs_network_or_robots(tmp_path, monkeypatch):
    from runtime import local_reference_day as reference
    original = fixture_root() / 'runtime/local_reference/2026-10-20/R01'
    folder = tmp_path / 'R01'; shutil.copytree(original, folder)
    def forbidden(*args, **kwargs): pytest.fail('frozen readback must remain offline')
    monkeypatch.setattr(urllib.request, 'build_opener', forbidden)
    monkeypatch.setattr(policy, 'open_public_urw_source', forbidden)
    publication, body = reference.one_race(folder, '2026-10-20', 1, generate=forbidden)
    assert publication['reference_runner_count'] == 11 and '最終結論' in body
    assert (folder / 'answer.txt').read_bytes() == (original / 'answer.txt').read_bytes()


@pytest.mark.parametrize('code', ['SOURCE_POLICY_ROBOTS_DISALLOWED',
    'SOURCE_POLICY_ROBOTS_UNKNOWN', 'SOURCE_POLICY_RETRY_NOT_READY'])
def test_source_policy_stop_survives_day_discovery_and_cli_wrappers(tmp_path, monkeypatch, capsys, code):
    import gzip
    from runtime import local_reference_day as reference
    day='2026-10-20'; now=datetime.fromisoformat('2026-10-19T18:30:00+09:00')
    saved=fixture_root()/'runtime/local_reference'/day
    shutil.copytree(saved,tmp_path/'runtime/local_reference'/day)
    shutil.rmtree(tmp_path/'runtime/local_reference'/day/'R01')
    plan=json.loads(gzip.decompress((saved/'official_plan.json.gz').read_bytes()))
    error=policy.SourcePolicyError(code,target(),'Disallow: /KeibaWeb/TodayRaceInfo/',
        robots_sha256='a'*64,raw_body='DO_NOT_LOG_RAW_BODY_OR_CREDENTIALS')
    def blocked(*args,**kwargs):
        raise ValueError('REFERENCE_OFFICIAL_SOURCE_HOLD:'+str(error))
    report=reference.run_day(tmp_path,day,plan=plan,generate=blocked,clock=lambda:now)
    assert report['reference_complete_count']==11
    assert report['first_failed_stage']=='DATA_SOURCE_POLICY'
    assert report['code']==report['races'][0]['code']==code
    assert report['source_policy']['target_url']==target()
    assert report['source_policy']['robots_sha256']=='a'*64
    assert 'DO_NOT_LOG' not in json.dumps(report)

    monkeypatch.setattr(reference,'prepare_plan',blocked)
    window=reference.run_discovery_window(tmp_path,now=now)
    assert all(row['first_failed_stage']=='DATA_SOURCE_POLICY' and row['code']==code for row in window['days'])
    monkeypatch.setattr(sys,'argv',['reference','--date',day,'--repo-root',str(tmp_path/'cli')])
    assert reference.main()==2
    cli=json.loads(capsys.readouterr().out)
    assert cli['first_failed_stage']=='DATA_SOURCE_POLICY' and cli['code']==code
    assert cli['source_policy']['robots_sha256']=='a'*64
    assert 'DO_NOT_LOG' not in json.dumps(cli)


@pytest.mark.parametrize('wrapped', [False, True])
def test_normal_chat_keeps_formal_hold_separate_from_source_policy_stop(tmp_path, monkeypatch, wrapped):
    from runtime import local_race_entry as entry
    monkeypatch.setattr(entry,'_chat_final',lambda *args:(None,[]))
    formal={'status':'BLOCKED','first_failed_stage':'AUTHORIZATION','code':'VENUE_OWNER_NOT_AUTHORIZED'}
    monkeypatch.setattr(entry,'chat_formal_status',lambda *args:dict(formal))
    error=policy.SourcePolicyError('SOURCE_POLICY_ROBOTS_DISALLOWED',target(),
        'Disallow: /KeibaWeb/TodayRaceInfo/',robots_sha256='b'*64,raw_body='DO_NOT_LOG_RAW_BODY_OR_CREDENTIALS')
    def blocked(*args,**kwargs):
        if wrapped:raise ValueError('REFERENCE_OFFICIAL_SOURCE_HOLD:'+str(error))
        raise error
    monkeypatch.setattr(entry,'_chat_reference',blocked)
    report=entry.run_chat(entry.resolve_chat_intent('2026-10-20 浦和1R'),output=tmp_path,run_id='policy-stop')
    assert report['formal']==formal
    assert report['reference']['first_failed_stage']=='DATA_SOURCE_POLICY'
    assert report['reference']['code']=='SOURCE_POLICY_ROBOTS_DISALLOWED'
    assert report['reference']['source_policy']['robots_sha256']=='b'*64
    assert 'FORMAL：AUTHORIZATION／VENUE_OWNER_NOT_AUTHORIZED' in report['message']
    assert 'REFERENCE：DATA_SOURCE_POLICY／SOURCE_POLICY_ROBOTS_DISALLOWED' in report['message']
    assert '取得対象Raceの全出走馬と各馬評価は未確認です。' in report['message']
    assert '最終結論：正式予測は未成立。参考全馬評価も未完成。' in report['message']
    assert report['completion'] is False
    assert target() in report['message'] and 'DO_NOT_LOG' not in json.dumps(report)

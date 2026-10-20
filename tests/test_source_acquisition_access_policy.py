"""Existing SOURCE fetcher policy tests; no live HTTP or Runtime calls."""
import io
import urllib.error
import urllib.parse
import urllib.request

import pytest
from runtime.local_physical import source_acquisition as s

URL = 'https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/DebaTable?k_raceNo=4'
ROBOTS = 'https://www.keiba.go.jp/robots.txt'


class Response:
    def __init__(self, url, raw, *, status=200, content_type='text/plain', headers=None):
        self.url, self.raw, self.status = url, raw, status
        self.headers = {'content-type': content_type, **(headers or {})}
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def geturl(self): return self.url
    def read(self, size=-1): return self.raw if size < 0 else self.raw[:size]


@pytest.fixture
def transport(monkeypatch):
    s._ROBOTS_CACHE.clear()
    monkeypatch.setattr(s, 'validate_public_url', lambda url: urllib.parse.urlsplit(url))
    calls = []
    config = {'robots': b'User-agent: *\nDisallow: /KeibaWeb/TodayRaceInfo/\n', 'robots_status':200,
              'target_status':200, 'target_headers':{}, 'robots_headers':{}}
    class Opener:
        def open(self, request, *, timeout):
            url = request.full_url
            calls.append((url, request.get_header('User-agent')))
            if url == ROBOTS:
                if config['robots_status'] != 200:
                    raise urllib.error.HTTPError(url, config['robots_status'], 'test', config['robots_headers'], io.BytesIO(b''))
                return Response(url, config['robots'])
            if config['target_status'] != 200:
                raise urllib.error.HTTPError(url, config['target_status'], 'test', config['target_headers'], io.BytesIO(b'limited'))
            return Response(url, b'<html>body weight 480</html>', content_type='text/html')
    monkeypatch.setattr(s.urllib.request, 'build_opener', lambda *args: Opener())
    return calls, config


def fetch():
    return s.fetch_source({'url': URL, 'source_id':'test', 'required':True}, '')


def test_nar_disallow_stops_before_source_get(transport):
    calls, _ = transport
    with pytest.raises(ValueError, match='SOURCE_POLICY_ROBOTS_DISALLOWED'):
        fetch()
    assert calls == [(ROBOTS, s.SOURCE_USER_AGENT)]


@pytest.mark.parametrize('status', [301, 401, 403, 429, 500, 503])
def test_unknown_robots_is_cached_and_never_fetches_target(transport, status):
    calls, config = transport
    config['robots_status'] = status
    for _ in range(2):
        with pytest.raises(ValueError, match='SOURCE_POLICY_ROBOTS_UNKNOWN'):
            fetch()
    assert [url for url, _ in calls] == [ROBOTS]


@pytest.mark.parametrize('body', [b'<html>not a robots policy</html>', b'login required', b'\x00', b'\xff'])
def test_invalid_robots_never_fetches_target(transport, body):
    calls, config = transport
    config['robots'] = body
    with pytest.raises(ValueError, match='SOURCE_POLICY_ROBOTS_UNKNOWN'):
        fetch()
    assert [url for url, _ in calls] == [ROBOTS]


@pytest.mark.parametrize('status', [404, 410])
def test_absent_robots_is_not_a_data_licence(transport, status):
    calls, config = transport
    config['robots_status'] = status
    snapshot, errors = fetch()
    assert errors == []
    access = snapshot['source_access_policy']
    assert access['robots_status'] == 'ABSENT_HTTP_' + str(status)
    assert access['automatic_access_allowed'] and not access['data_licence_granted']
    assert [url for url, _ in calls] == [ROBOTS, URL]
    assert all(ua == s.SOURCE_USER_AGENT for _, ua in calls)
    assert snapshot['snapshot_sha256'] == s.sha_obj({k:v for k,v in snapshot.items() if k != 'snapshot_sha256'})


def test_allowed_policy_reuses_cache_and_binds_snapshot(transport):
    calls, config = transport
    config['robots'] = b'User-agent: *\nDisallow: /private/\n'
    first, _ = fetch()
    second, _ = fetch()
    assert [url for url, _ in calls] == [ROBOTS, URL, URL]
    assert first['source_access_policy'] == second['source_access_policy']
    assert first['source_access_policy']['robots_sha256']


def test_server_retry_after_blocks_later_source_get(transport):
    calls, config = transport
    config.update(robots_status=404, target_status=429, target_headers={'Retry-After':'120'})
    snapshot, errors = fetch()
    assert errors == ['SOURCE_HTTP_STATUS:429']
    assert snapshot['http_status'] == 429
    with pytest.raises(ValueError, match='SOURCE_POLICY_RETRY_NOT_READY'):
        fetch()
    assert [url for url, _ in calls] == [ROBOTS, URL]


def test_large_provider_crawl_delay_is_bounded_not_ignored(transport):
    calls, config = transport
    config['robots'] = b'User-agent: *\nAllow: /\nCrawl-delay: 120\n'
    with pytest.raises(ValueError, match='SOURCE_POLICY_RETRY_NOT_READY'):
        fetch()
    assert [url for url, _ in calls] == [ROBOTS]


def test_redirect_cannot_enter_disallowed_path(transport):
    calls, config = transport
    config['robots'] = b'User-agent: *\nDisallow: /private/\n'
    handler = s._SafeRedirect()
    with pytest.raises(ValueError, match='SOURCE_POLICY_ROBOTS_DISALLOWED'):
        handler.redirect_request(urllib.request.Request(URL), None, 302, 'redirect', {}, 'https://www.keiba.go.jp/private/card')
    assert [url for url, _ in calls] == [ROBOTS]


def test_url_validation_precedes_even_robots_get(transport, monkeypatch):
    calls, _ = transport
    def deny(url): raise ValueError('SOURCE_HOST_NOT_ALLOWED:private')
    monkeypatch.setattr(s, 'validate_public_url', deny)
    with pytest.raises(ValueError, match='SOURCE_HOST_NOT_ALLOWED'):
        fetch()
    assert calls == []


@pytest.mark.parametrize('rule', ['/KeibaWeb/TodayRaceInfo/*', '/*.do', '/private$', '/private%2Fcard'])
def test_unsupported_robots_pattern_is_unknown_never_an_allow(transport, rule):
    calls, config = transport
    config['robots'] = ('User-agent: *\nDisallow: ' + rule + '\n').encode()
    with pytest.raises(ValueError, match='SOURCE_POLICY_ROBOTS_UNKNOWN'):
        fetch()
    assert [url for url, _ in calls] == [ROBOTS]


def test_longest_literal_disallow_overrides_earlier_broad_allow(transport):
    calls, config = transport
    config['robots'] = b'User-agent: *\nAllow: /\nDisallow: /KeibaWeb/\n'
    with pytest.raises(ValueError, match='SOURCE_POLICY_ROBOTS_DISALLOWED'):
        fetch()
    assert [url for url, _ in calls] == [ROBOTS]


def test_longest_literal_allow_and_equal_length_allow_are_honored(transport):
    calls, config = transport
    config['robots'] = b'User-agent: *\nDisallow: /KeibaWeb/\nAllow: /KeibaWeb/TodayRaceInfo/\nDisallow: /KeibaWeb/TodayRaceInfo/\n'
    fetch()
    assert [url for url, _ in calls] == [ROBOTS, URL]


@pytest.mark.parametrize('value', ['0.5', '-1', 'abc'])
def test_unhandled_crawl_delay_never_becomes_unthrottled(transport, value):
    calls, config = transport
    config['robots'] = ('User-agent: *\nAllow: /\nCrawl-delay: '+value+'\n').encode()
    with pytest.raises(ValueError, match='SOURCE_POLICY_ROBOTS_UNKNOWN'):
        fetch()
    assert [url for url, _ in calls] == [ROBOTS]


def test_robots_retry_after_prevents_early_robots_retry(transport, monkeypatch):
    calls, config = transport
    clock = [1000.0]
    monkeypatch.setattr(s.time, 'monotonic', lambda: clock[0])
    config.update(robots_status=429, robots_headers={'Retry-After':'120'})
    with pytest.raises(ValueError, match='SOURCE_POLICY_ROBOTS_UNKNOWN'):
        fetch()
    clock[0] += 31
    with pytest.raises(ValueError, match='SOURCE_POLICY_ROBOTS_UNKNOWN'):
        fetch()
    assert [url for url, _ in calls] == [ROBOTS]


def test_robots_directive_before_agent_fails_closed(transport):
    calls, config = transport
    config['robots'] = b'Disallow: /KeibaWeb/\nUser-agent: *\nAllow: /\n'
    with pytest.raises(ValueError, match='SOURCE_POLICY_ROBOTS_UNKNOWN'):
        fetch()
    assert [url for url, _ in calls] == [ROBOTS]


def test_provider_gap_is_observed_after_robots_and_between_targets(transport, monkeypatch):
    calls, config = transport
    clock, waits = [1000.0], []
    monkeypatch.setattr(s.time, 'monotonic', lambda: clock[0])
    def sleep(seconds):
        waits.append(seconds)
        clock[0] += seconds
    monkeypatch.setattr(s.time, 'sleep', sleep)
    config['robots'] = b'User-agent: *\nAllow: /\nCrawl-delay: 2\n'
    fetch()
    fetch()
    assert waits == [2.0, 2.0]
    assert [url for url, _ in calls] == [ROBOTS, URL, URL]


def test_expired_robots_cache_never_bypasses_target_retry_after(transport, monkeypatch):
    calls, config = transport
    clock = [1000.0]
    monkeypatch.setattr(s.time, 'monotonic', lambda: clock[0])
    config.update(robots_status=404, target_status=429, target_headers={'Retry-After':'1000'})
    fetch()
    clock[0] += 301
    with pytest.raises(ValueError, match='SOURCE_POLICY_RETRY_NOT_READY'):
        fetch()
    assert [url for url, _ in calls] == [ROBOTS, URL]


def test_literal_group_parser_keeps_default_without_stdlib_internal_state():
    policy = s._literal_robots_policy('User-agent: *\nDisallow: /KeibaWeb/\nCrawl-delay: 12\n', ROBOTS)
    assert policy == {'rules':[('/KeibaWeb/', False)], 'delay':12}


def test_literal_group_parser_combines_equal_specificity_groups():
    product = s.SOURCE_USER_AGENT.split('/', 1)[0]
    policy = s._literal_robots_policy(
        'User-agent: *\nAllow: /\n\nUser-agent: '+product+'\nDisallow: /KeibaWeb/\n'
        '\nUser-agent: '+product+'\nAllow: /public/\nRequest-rate: 2/10\n', ROBOTS)
    assert policy == {'rules':[('/KeibaWeb/', False),('/public/', True)], 'delay':5}


def test_comment_between_agent_aliases_does_not_drop_applicable_restriction():
    product = s.SOURCE_USER_AGENT.split('/', 1)[0]
    policy = s._literal_robots_policy('User-agent: '+product+'\n# comment\nUser-agent: second-agent\nDisallow: /\n', ROBOTS)
    assert policy['rules'] == [('/', False)]

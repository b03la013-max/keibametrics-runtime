"""Fail-closed robots/rate policy for unsigned URW official research GETs only.

No Production SOURCE transport, alternate host/path, credentials or crawler
impersonation. A shared local lock/cache spaces processes on the same worker.
HTTP failures are never automatically retried; Retry-After gates later calls.
"""
from contextlib import contextmanager
from email.utils import parsedate_to_datetime
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import tempfile
import time
import urllib.error
from urllib.parse import parse_qsl, urlsplit
import urllib.request

ORIGIN = 'https://www.keiba.go.jp'
ROBOTS_URL = ORIGIN + '/robots.txt'
PRODUCT = 'KeibaMetrics-URW-PublicResearch'
USER_AGENT = PRODUCT + '/1.0 (+https://github.com/b03la013-max/keibametrics-runtime)'
MIN_INTERVAL = 10.0
MAX_WAIT = 30.0
CACHE_TTL = 300.0
FAILURE_TTL = 30.0
MAX_ROBOTS_BYTES = 131072


class SourcePolicyError(ValueError):
    def __init__(self, code, target, reason, **evidence):
        self.receipt = {'code': code, 'target_url': target, 'robots_url': ROBOTS_URL,
                        'reason': reason, **evidence}
        super().__init__(code + ':' + json.dumps(self.receipt, sort_keys=True))


def source_policy_failure(error):
    """Preserve policy stops through ValueError wrappers without raw body logs."""
    code = None; original = {}; seen = set(); current = error
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        receipt = getattr(current, 'receipt', None)
        if isinstance(receipt, dict) and re.fullmatch(r'SOURCE_POLICY_[A-Z_]+', str(receipt.get('code', ''))):
            code = receipt['code']; original = receipt; break
        text = str(current)
        match = re.search(r'\bSOURCE_POLICY_[A-Z_]+\b', text)
        if match:
            code = code or match[0]
            suffix = text[match.end():].lstrip(': ')
            if suffix.startswith('{'):
                try:
                    parsed, _ = json.JSONDecoder().raw_decode(suffix)
                    if isinstance(parsed, dict): original = parsed; break
                except ValueError:
                    pass
        current = current.__cause__ or current.__context__
    if code is None: return None
    safe = {'code': code, 'robots_url': ROBOTS_URL}
    target = original.get('target_url')
    if isinstance(target, str):
        url = urlsplit(target); fields = parse_qsl(url.query, keep_blank_values=True)
        validators = {'k_babaCode': r'18', 'k_raceNo': r'(?:[1-9]|1[0-2])',
                      'k_raceDate': r'\d{4}/\d{2}/\d{2}'}
        if (url.scheme == 'https' and url.netloc == 'www.keiba.go.jp' and not url.fragment
                and url.path in ('/robots.txt', '/KeibaWeb/TodayRaceInfo/DebaTable',
                    '/KeibaWeb/TodayRaceInfo/OddsTanFuku', '/KeibaWeb/TodayRaceInfo/RaceList')
                and all(key in validators and re.fullmatch(validators[key], value) for key, value in fields)):
            safe['target_url'] = target
    digest = original.get('robots_sha256')
    if isinstance(digest, str) and re.fullmatch('[0-9a-f]{64}', digest): safe['robots_sha256'] = digest
    reason = original.get('reason', '')
    if isinstance(reason, str) and (re.fullmatch(r'[A-Z][A-Z0-9_]{0,100}', reason)
            or re.fullmatch(r'(?:Disallow|Allow): /[^\s\"<>]{0,160}', reason)):
        safe['reason'] = reason
    else:
        http = re.search(r'HTTP Error ([1-5][0-9]{2})', str(reason))
        safe['reason'] = 'ROBOTS_HTTP_' + http[1] if http else 'ROBOTS_POLICY_UNRESOLVED'
    delay = original.get('retry_after_seconds')
    if type(delay) in (int, float) and math.isfinite(delay) and delay >= 0:
        safe['retry_after_seconds'] = delay
    return {'first_failed_stage': 'DATA_SOURCE_POLICY', 'code': code,
            'source_policy': safe, 'error': code}


def _pattern(value):
    """Normalize RFC 9309 octets; retain encoded reserved characters."""
    out = ''; offset = 0
    unreserved = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~'
    while offset < len(value):
        ch = value[offset]
        if ch == '%':
            pair = value[offset + 1:offset + 3]
            if len(pair) != 2 or not re.fullmatch('[0-9a-fA-F]{2}', pair):
                raise ValueError('MALFORMED_PERCENT_ENCODING')
            octet = int(pair, 16)
            out += chr(octet) if chr(octet) in unreserved else '%' + pair.upper()
            offset += 3
        elif ord(ch) > 127:
            out += ''.join(f'%{byte:02X}' for byte in ch.encode('utf-8'))
            offset += 1
        else:
            out += ch; offset += 1
    return out


def robots_decision(text, target):
    """Return the applicable longest-match rule plus conservative request gap."""
    if not text.strip() or '\x00' in text or '<html' in text.lower() or '<!doctype' in text.lower():
        raise ValueError('ROBOTS_BODY_NOT_POLICY')
    groups = []; group = None; directives = False
    for raw in text.lstrip('\ufeff').splitlines():
        line = raw.split('#', 1)[0].strip()
        if not line: continue
        if ':' not in line: raise ValueError('ROBOTS_MALFORMED_LINE')
        key, value = line.split(':', 1); key = key.strip().lower(); value = value.strip()
        if key == 'user-agent':
            if not value or (value != '*' and not re.fullmatch(r'[A-Za-z0-9_.-]+', value)):
                raise ValueError('ROBOTS_AGENT_INVALID')
            if group is None or directives:
                group = {'agents': [], 'rules': [], 'delay': MIN_INTERVAL}; groups.append(group)
            group['agents'].append(value.lower()); directives = False
        elif key in {'allow', 'disallow', 'crawl-delay', 'request-rate'}:
            if group is None: raise ValueError('ROBOTS_DIRECTIVE_WITHOUT_AGENT')
            directives = True
            if key in {'allow', 'disallow'}:
                if value:
                    if not value.startswith('/'): raise ValueError('ROBOTS_RULE_PATH_INVALID')
                    group['rules'].append((key == 'allow', _pattern(value)))
            elif key == 'crawl-delay':
                delay = float(value)
                if not math.isfinite(delay) or delay < 0: raise ValueError('ROBOTS_DELAY_INVALID')
                group['delay'] = max(group['delay'], delay)
            else:
                if not re.fullmatch(r'[1-9][0-9]*/[1-9][0-9]*', value):
                    raise ValueError('ROBOTS_REQUEST_RATE_INVALID')
                requests, seconds = map(int, value.split('/'))
                group['delay'] = max(group['delay'], seconds / requests)
    if not groups: raise ValueError('ROBOTS_AGENT_GROUP_REQUIRED')
    matches = [(len(agent), group) for group in groups for agent in group['agents']
               if agent != '*' and agent in PRODUCT.lower()]
    selected = ([group for length, group in matches if length == max(n for n, _ in matches)]
                if matches else [group for group in groups if '*' in group['agents']])
    url = urlsplit(target)
    path = _pattern(url.path + ('?' + url.query if url.query else ''))
    applicable = []
    for group in selected:
        for allowed, pattern in group['rules']:
            anchored = pattern.endswith('$')
            body = pattern[:-1] if anchored else pattern
            regex = '^' + re.escape(body).replace(r'\*', '.*') + ('$' if anchored else '')
            if re.match(regex, path):
                applicable.append((len(body.replace('*', '').encode()), allowed, pattern))
    winner = max(applicable, default=(0, True, ''), key=lambda rule: (rule[0], rule[1]))
    return {'allowed': winner[1], 'matched_rule': ('Allow: ' if winner[1] else 'Disallow: ') + winner[2],
            'crawl_delay_seconds': max([MIN_INTERVAL] + [group['delay'] for group in selected]),
            'user_agent': USER_AGENT}


def _retry_at(headers, now):
    headers = headers or {}
    value = headers.get('Retry-After') or headers.get('retry-after')
    if not value: return now
    try:
        if value.strip().isdigit(): return now + max(0, int(value))
        parsed = parsedate_to_datetime(value)
        if parsed.tzinfo is None: raise ValueError('RETRY_AFTER_TIMEZONE_REQUIRED')
        return max(now, parsed.timestamp())
    except (TypeError, ValueError, OverflowError):
        # Unknown server backoff is a visible hold, never an immediate retry.
        return now + 60.0


class UrwReferenceSourcePolicy:
    def __init__(self, cache_dir=None, *, clock=time.time, sleep=time.sleep):
        self.cache_dir = Path(cache_dir or (Path(tempfile.gettempdir()) /
            f'keibametrics-urw-source-policy-{os.getuid()}'))
        self.clock = clock; self.sleep = sleep

    def _wait(self, state, target):
        wait = max(0.0, state.get('next_request_at', 0) - self.clock())
        if wait > MAX_WAIT:
            raise SourcePolicyError('SOURCE_POLICY_RETRY_NOT_READY', target,
                                    'SERVER_OR_CRAWL_DELAY_PENDING', retry_after_seconds=wait)
        if wait:
            self.sleep(wait)
            if self.clock() + 0.001 < state['next_request_at']:
                raise SourcePolicyError('SOURCE_POLICY_RETRY_NOT_READY', target, 'CLOCK_DID_NOT_ADVANCE')

    @contextmanager
    def open(self, opener, request, *, timeout=15):
        target = request.full_url; url = urlsplit(target)
        if (url.scheme != 'https' or url.netloc != 'www.keiba.go.jp' or url.fragment
                or request.get_method() != 'GET'):
            raise SourcePolicyError('SOURCE_POLICY_ORIGIN_INVALID', target, 'OFFICIAL_ORIGIN_REQUIRED')
        self.cache_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        with (self.cache_dir / 'robots.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            path = self.cache_dir / 'robots.json'
            try:
                state = json.loads(path.read_text()) if path.exists() else {}
                if not isinstance(state, dict): raise ValueError('CACHE_NOT_OBJECT')
                if any(not isinstance(state[key], (int, float)) or not math.isfinite(state[key])
                       for key in ('expires_at', 'next_request_at', 'fetched_at') if key in state):
                    raise ValueError('CACHE_CLOCK_INVALID')
                if state.get('text') is not None and (not isinstance(state['text'], str)
                        or hashlib.sha256(state['text'].encode()).hexdigest() != state.get('text_sha256')):
                    raise ValueError('CACHE_BODY_HASH_INVALID')
            except (OSError, ValueError) as exc:
                raise SourcePolicyError('SOURCE_POLICY_ROBOTS_UNKNOWN', target, 'CACHE_INVALID') from exc

            def save():
                path.write_text(json.dumps(state, sort_keys=True) + '\n')

            if self.clock() >= state.get('expires_at', 0):
                self._wait(state, target)
                state['next_request_at'] = self.clock() + MIN_INTERVAL
                try:
                    robots = urllib.request.Request(ROBOTS_URL, headers={
                        'User-Agent': USER_AGENT, 'Accept': 'text/plain', 'Accept-Encoding': 'identity'}, method='GET')
                    with opener.open(robots, timeout=timeout) as response:
                        headers = {k.lower(): v for k, v in response.headers.items()}
                        if (response.status != 200 or response.geturl() != ROBOTS_URL
                                or headers.get('content-type', '').split(';', 1)[0].strip().lower() != 'text/plain'
                                or headers.get('content-encoding', 'identity').lower() not in ('', 'identity')):
                            raise ValueError('ROBOTS_HTTP_IDENTITY_OR_CONTENT_TYPE')
                        raw = response.read(MAX_ROBOTS_BYTES + 1)
                        if len(raw) > MAX_ROBOTS_BYTES: raise ValueError('ROBOTS_MAX_BYTES')
                        text = raw.decode('utf-8-sig', errors='strict')
                        robots_decision(text, target)
                    state.update(text=text, robots_sha256=hashlib.sha256(raw).hexdigest(),
                                 text_sha256=hashlib.sha256(text.encode()).hexdigest(),
                                 fetched_at=self.clock(), expires_at=self.clock() + CACHE_TTL)
                    state.pop('failure', None)
                except (OSError, ValueError, UnicodeError, TypeError, AttributeError) as exc:
                    if isinstance(exc, urllib.error.HTTPError):
                        state['next_request_at'] = max(state['next_request_at'], _retry_at(exc.headers, self.clock()))
                    state.update(failure=type(exc).__name__ + ':' + str(exc),
                                 expires_at=max(self.clock() + FAILURE_TTL, state['next_request_at']))
                    save()
                    raise SourcePolicyError('SOURCE_POLICY_ROBOTS_UNKNOWN', target, state['failure']) from exc
                save()
            if state.get('failure'):
                raise SourcePolicyError('SOURCE_POLICY_ROBOTS_UNKNOWN', target, state['failure'])
            try:
                if not all(key in state for key in ('text', 'robots_sha256', 'fetched_at')):
                    raise ValueError('CACHED_POLICY_INCOMPLETE')
                if not re.fullmatch('[0-9a-f]{64}', state['robots_sha256']):
                    raise ValueError('CACHED_POLICY_HASH_INVALID')
                decision = robots_decision(state['text'], target)
            except (KeyError, TypeError, ValueError) as exc:
                raise SourcePolicyError('SOURCE_POLICY_ROBOTS_UNKNOWN', target, 'CACHED_POLICY_INVALID') from exc
            if not decision['allowed']:
                raise SourcePolicyError('SOURCE_POLICY_ROBOTS_DISALLOWED', target,
                    decision['matched_rule'], robots_sha256=state['robots_sha256'], user_agent=USER_AGENT)
            interval = decision['crawl_delay_seconds']
            state['next_request_at'] = max(state.get('next_request_at', 0), state['fetched_at'] + interval)
            self._wait(state, target)
            state['next_request_at'] = self.clock() + interval
            save()
            # Lock includes body consumption, not merely response headers.
            request.add_header('User-Agent', USER_AGENT)
            try:
                with opener.open(request, timeout=timeout) as response:
                    yield response
            except urllib.error.HTTPError as exc:
                state['next_request_at'] = max(state['next_request_at'], _retry_at(exc.headers, self.clock()))
                save()
                raise


POLICY = UrwReferenceSourcePolicy()


def open_public_urw_source(opener, request, *, timeout=15):
    return POLICY.open(opener, request, timeout=timeout)

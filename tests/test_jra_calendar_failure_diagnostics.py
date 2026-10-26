"""Public HTTP diagnostics are not SOURCE, licence or non-meeting evidence."""
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from email.message import Message

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'runtime/jra_source_runtime'))
from jra_race_day_resolver import official_navigation_failure


def test_403_preserves_public_request_without_cookie_or_false_success():
    h=Message()
    for k,v in {'Date':'Mon, 26 Oct 2026 08:17:00 GMT','Content-Type':'text/html',
                'Retry-After':'3600','Set-Cookie':'private','Authorization':'secret'}.items():
        h[k]=v
    e=HTTPError('https://www.jra.go.jp/keiba/calendar2026/2026/10/1026.html',403,'Forbidden',h,None)
    e.official_request={'url':e.url,'method':'GET','phase':'CONNECT_TLS_OR_RESPONSE_HEADERS','attempt':1}
    d=official_navigation_failure(e)
    assert d['http_status']==403 and d['access_denied'] and not d['retryable']
    assert d['url']==e.url and d['attempt']==1
    assert set(d['response_headers'])=={'Date','Content-Type','Retry-After'}
    assert not d['source_accepted'] and not d['official_non_meeting_proven']
    assert d['access_denial_cause']=='UNDETERMINED'


def test_changed_http_failure_is_material_and_unknown_is_not_no_meetings():
    a=official_navigation_failure(HTTPError('https://www.jra.go.jp/',403,'Forbidden',{},None))
    b=official_navigation_failure(HTTPError('https://www.jra.go.jp/',500,'Server error',{},None))
    assert a['http_status']!=b['http_status'] and b['retryable']
    d=official_navigation_failure(URLError('DNS unavailable'),race_date='2026-10-31')
    assert d['http_status'] is None and not d['official_non_meeting_proven']
    assert d['url'].endswith('/1031.html')

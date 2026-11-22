import urllib.error

from runtime.local_autopilot import run


class SourceStop(Exception):
    pass


def test_transient_network_error_is_retried_class():
    assert run._transient(SourceStop('NETWORK:URLError:https://keiba.rakuten.co.jp/race_card/list/RACEID/1'))
    try:
        try:
            raise urllib.error.URLError('reset')
        except Exception as e:
            raise SourceStop('x') from e
    except Exception as e:
        assert run._transient(e)


def test_http_status_is_final():
    assert not run._transient(urllib.error.HTTPError('u', 429, 'Too Many', {}, None))
    assert not run._transient(urllib.error.HTTPError('u', 403, 'Forbidden', {}, None))
    assert not run._transient(SourceStop('NETWORK:HTTPError:403'))
    assert not run._transient(ValueError('parse'))

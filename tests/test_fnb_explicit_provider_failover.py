"""Independent transport failures only; every response/permission is synthetic.

No fixture is a real SOURCE, licence, Actor activation or LIVE completion.
"""
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from runtime import local_fnb_multisource as m
from runtime import local_fnb_day_supervisor as s


NOW = datetime(2026, 11, 4, 3, 0, tzinfo=timezone.utc)
INTENT = {'venue_id':'FNB', 'race_date':'2026-11-04', 'race_no':1,
          'prediction_cutoff':(NOW + timedelta(minutes=5)).isoformat()}
URLS = {'NAR_OFFICIAL':'https://www.keiba.go.jp/synthetic-format',
        'NANKAN_OFFICIAL':'https://www.nankankeiba.com/synthetic-format'}


def provider(name, *, clock=lambda:NOW):
    url = URLS[name]
    return m.ProviderBinding(provider=name, exact_urls=(url,), code_sha256='a'*64,
        permission_ref='SYNTHETIC_NOT_PERMISSION', permission_sha256='b'*64,
        effective_from=(NOW-timedelta(hours=1)).isoformat(),
        effective_until=(NOW+timedelta(hours=1)).isoformat(), actor_id='SYNTHETIC',
        automated_get_admitted=True, private_retention_admitted=True,
        cloud_processing_admitted=True, qualified_field_rules={},
        fetch=Mock(side_effect=lambda **kw:{'raw':('SYNTHETIC_'+name).encode(),
            'retrieval_method':'HTTPS_GET_ORIGINAL_RESPONSE', 'http_status':200,
            'final_url':url, 'access_policy':{'decision':'ALLOW'},
            'captured_at':clock().isoformat(), 'content_type':'text/plain'}),
        parse=Mock(return_value={'identity':deepcopy(INTENT), 'fields':[]}))


def acquire_all(root, bindings, *, clock=lambda:NOW):
    return m.acquire_available([{'provider':p,'url':URLS[p]} for p in bindings],
        bindings, intent=INTENT, actor_id='SYNTHETIC', now=NOW,
        private_root=root, clock=clock)


@pytest.mark.parametrize('error',[KeyError('private token'), TypeError('private token'),
                                RuntimeError('private token')])
def test_format_exception_keeps_raw_and_continues_independent_provider(tmp_path,error):
    first, second = provider('NAR_OFFICIAL'), provider('NANKAN_OFFICIAL')
    first.parse.side_effect = error
    result = acquire_all(tmp_path, {'NAR_OFFICIAL':first,'NANKAN_OFFICIAL':second})
    assert len(result['packets']) == 1
    assert result['packets'][0]['provider'] == 'NANKAN_OFFICIAL'
    assert len(list(tmp_path.glob('*.raw'))) == 2
    captures = [json.loads(p.read_bytes()) for p in tmp_path.glob('*.capture.json')]
    assert {c['provider'] for c in captures} == {'NAR_OFFICIAL','NANKAN_OFFICIAL'}
    assert all((tmp_path/(c['raw_sha256']+'.raw')).is_file() for c in captures)
    assert all(c['format_verified'] is False and c['formal_source_admitted'] is False for c in captures)
    assert 'private token' not in json.dumps(result)
    assert result['formal_source_admitted'] is False
    assert result['registered_oos_increment'] == 0
    assert list(tmp_path.glob('MULTISOURCE_ATTEMPTS_*.json'))


def test_slow_failed_first_provider_cannot_start_next_after_cutoff(tmp_path):
    current = [NOW]
    first, second = provider('NAR_OFFICIAL'), provider('NANKAN_OFFICIAL')
    def slow_failure(**kw):
        current[0] = NOW + timedelta(minutes=6)
        raise RuntimeError('SYNTHETIC_TRANSPORT_FAILURE')
    first.fetch.side_effect = slow_failure
    result = acquire_all(tmp_path, {'NAR_OFFICIAL':first,'NANKAN_OFFICIAL':second}, clock=lambda:current[0])
    second.fetch.assert_not_called()
    assert result['provider_receipts'][1]['reason'] == 'MULTISOURCE_CUTOFF_EXPIRED_DIAGNOSTIC_REQUIRED'
    assert not result['packets']


def test_missing_rights_never_uses_first_transport_or_lends_rights_from_next(tmp_path):
    first = replace(provider('NAR_OFFICIAL'), automated_get_admitted=False)
    second = provider('NANKAN_OFFICIAL')
    result = acquire_all(tmp_path, {'NAR_OFFICIAL':first,'NANKAN_OFFICIAL':second})
    first.fetch.assert_not_called()
    second.fetch.assert_called_once()
    assert result['provider_receipts'][0]['reason'] == 'MULTISOURCE_PROVIDER_QUALIFICATION_REQUIRED'


def test_parser_crossing_cutoff_retains_raw_but_cannot_admit_packet(tmp_path):
    current = [NOW]
    first = provider('NAR_OFFICIAL')
    def slow_parser(**kw):
        current[0] = NOW + timedelta(minutes=6)
        return {'identity':deepcopy(INTENT),'fields':[]}
    first.parse.side_effect = slow_parser
    result = acquire_all(tmp_path,{'NAR_OFFICIAL':first},clock=lambda:current[0])
    assert result['packets'] == []
    assert result['provider_receipts'][0]['reason'] == 'MULTISOURCE_CUTOFF_EXPIRED_DIAGNOSTIC_REQUIRED'
    assert len(list(tmp_path.glob('*.raw'))) == 1


def capture():
    return {'request':deepcopy(INTENT), 'source':{'fixture':'SYNTHETIC_NOT_SIGNED_SOURCE'}}


def verify(**kw):
    return {'passed':True, 'source_artifact_sha256':m.sha(kw['captured']['source'])}


def test_existing_official_verifier_failure_can_use_independent_official_binding(tmp_path):
    first = Mock(return_value=capture()); second = Mock(return_value=capture())
    produce = m.r20_source_frontend(first, official_provider='NAR_OFFICIAL',
        official_verifier=lambda **kw:{'passed':False},
        official_fallbacks=[{'provider':'NANKAN_OFFICIAL','produce':second,'verify':verify}], clock=lambda:NOW)
    result = produce(intent=INTENT, private_root=tmp_path, now=NOW)
    assert result == capture()
    second.assert_called_once()
    saved = json.loads(next(tmp_path.glob('MULTISOURCE_*.json')).read_bytes())
    assert [r['status'] for r in saved['official_attempts']] == ['HOLD','EXISTING_OFFICIAL_VERIFIER_PASSED']
    assert saved['formal_scope_granted_here'] is False


def test_reference_provider_cannot_be_used_as_official_fallback(tmp_path):
    reference = Mock(return_value=capture())
    produce = m.r20_source_frontend(None, official_verifier=None,
        official_fallbacks=[{'provider':'SBO_NAR','produce':reference,'verify':verify}], clock=lambda:NOW)
    with pytest.raises(m.MultisourceHold,match='EXPLICIT_OFFICIAL_BINDING_REQUIRED'):
        produce(intent=INTENT, private_root=tmp_path, now=NOW)
    reference.assert_not_called()


def test_duplicate_failed_origin_is_not_retried_and_optional_supplement_failure_is_recorded(tmp_path):
    first = Mock(side_effect=OSError('private detail'))
    duplicate = Mock(return_value=capture())
    second = Mock(return_value=capture())
    produce = m.r20_source_frontend(first, official_provider='NAR_OFFICIAL', official_verifier=verify,
        official_fallbacks=[{'provider':'NAR_OFFICIAL','produce':duplicate,'verify':verify},
            {'provider':'NANKAN_OFFICIAL','produce':second,'verify':verify}],
        supplemental_producers=[Mock(side_effect=RuntimeError('private supplemental detail'))], clock=lambda:NOW)
    assert produce(intent=INTENT, private_root=tmp_path, now=NOW) == capture()
    duplicate.assert_not_called()
    saved = json.loads(next(tmp_path.glob('MULTISOURCE_*.json')).read_bytes())
    assert saved['supplemental_attempts'] == [{'status':'HOLD','reason':'MULTISOURCE_PRIVATE_TRANSPORT_FAILED'}]
    assert 'private detail' not in json.dumps(saved)


def test_expired_official_attempt_does_not_start_fallback(tmp_path):
    current = [NOW]
    def late(**kw):
        current[0] += timedelta(minutes=6)
        return capture()
    second = Mock(return_value=capture())
    produce = m.r20_source_frontend(late, official_provider='NAR_OFFICIAL',official_verifier=verify,
        official_fallbacks=[{'provider':'NANKAN_OFFICIAL','produce':second,'verify':verify}],clock=lambda:current[0])
    with pytest.raises(m.MultisourceHold,match='CUTOFF_EXPIRED'):
        produce(intent=INTENT, private_root=tmp_path, now=NOW)
    second.assert_not_called()


def discovery_plan():
    return {'profile':s.PLAN_PROFILE,'race_date':'2026-11-04','venue_id':'FNB',
        'observed_at':NOW.isoformat(),'races':[{'race_no':1,'race_id':'KM-LOCAL-FNB-20261104-R01',
            'scheduled_post_at':(NOW+timedelta(minutes=10)).isoformat(),
            'prediction_cutoff':INTENT['prediction_cutoff'],'start_at':NOW.isoformat()}]}


def test_failed_discovery_origin_is_not_retried_in_same_lease_and_plan_stays_exact(tmp_path):
    first = Mock(side_effect=RuntimeError('private discovery detail'))
    plan = discovery_plan(); original = deepcopy(plan)
    second = Mock(return_value=plan); checker = Mock(return_value=True)
    bound = {'_binding_sha256':'b'*64,'discovery_routes':[
        {'provider':'NAR_OFFICIAL','discover_day':first,'verify_discovery':lambda **kw:True},
        {'provider':'NANKAN_OFFICIAL','discover_day':second,'verify_discovery':checker}]}
    failed = set()
    for _ in range(2):
        returned, active = s.discover_available(bound,day='2026-11-04',private_root=tmp_path,
                                               clock=lambda:NOW,failed_routes=failed)
        assert returned is plan and returned == original
        assert active['verify_discovery'] is checker
        assert active['_binding_sha256'] == 'b'*64
    first.assert_called_once()
    assert failed == {'NAR_OFFICIAL'}
    assert second.call_count == 2
    history = [p for p in tmp_path.glob('FNB_2026-11-04_DISCOVERY_ROUTE_*.json')
               if not p.name.endswith('_RECEIPT.json')]
    assert len(history) == 2
    assert any(json.loads(p.read_bytes())['attempts'][0]['status'] == 'HOLD' for p in history)


def test_discovery_malformed_plan_cannot_prevent_later_independent_route(tmp_path):
    second = Mock(return_value=discovery_plan())
    bound = {'discovery_routes':[
        {'provider':'NAR_OFFICIAL','discover_day':lambda **kw:{'race_date':'2026-11-04'},'verify_discovery':lambda **kw:True},
        {'provider':'NANKAN_OFFICIAL','discover_day':second,'verify_discovery':lambda **kw:True}]}
    plan, _ = s.discover_available(bound, day='2026-11-04', private_root=tmp_path,clock=lambda:NOW)
    assert plan == discovery_plan()
    saved = json.loads((tmp_path/'FNB_2026-11-04_DISCOVERY_ROUTE_RECEIPT.json').read_bytes())
    assert saved['attempts'][0]['status'] == 'HOLD'
    assert saved['selected_provider'] == 'NANKAN_OFFICIAL'


def test_all_discovery_routes_fail_without_dispatch_or_no_bet_claim(tmp_path,monkeypatch):
    monkeypatch.delenv('GITHUB_ACTIONS',raising=False)
    execute = Mock()
    bound = {'execute_race':execute,'discovery_routes':[
        {'provider':'NAR_OFFICIAL','discover_day':Mock(side_effect=OSError('private endpoint')),'verify_discovery':lambda **kw:True},
        {'provider':'NANKAN_OFFICIAL','discover_day':Mock(side_effect=KeyError('private body')),'verify_discovery':lambda **kw:True}]}
    state = s.supervise(day='2026-11-04',private_root=tmp_path,binding=bound,activation={},clock=lambda:NOW)
    execute.assert_not_called()
    assert state['counts']['dispatched'] == state['counts']['no_bet_races'] == 0
    assert state['status'] == 'DISCOVERY_HOLD_NOT_NO_BET'
    assert state['code'] == 'ALL_EXPLICIT_OFFICIAL_DISCOVERY_ROUTES_UNAVAILABLE'


def test_process_interruptions_are_never_swallowed_by_provider_fallback(tmp_path):
    first = provider('NAR_OFFICIAL'); first.fetch.side_effect = SystemExit('synthetic shutdown')
    second = provider('NANKAN_OFFICIAL')
    with pytest.raises(SystemExit):
        acquire_all(tmp_path,{'NAR_OFFICIAL':first,'NANKAN_OFFICIAL':second})
    second.fetch.assert_not_called()


def test_routes_only_binding_is_resolved_for_one_shot_cli(tmp_path,monkeypatch):
    monkeypatch.delenv('GITHUB_ACTIONS',raising=False)
    now = datetime.now(timezone.utc)
    day = now.astimezone(s.JST).date().isoformat()
    plan = {'profile':s.PLAN_PROFILE,'race_date':day,'venue_id':'FNB','observed_at':now.isoformat(),
        'races':[{'race_no':1,'race_id':'KM-LOCAL-FNB-'+day.replace('-','')+'-R01',
                  'scheduled_post_at':(now+timedelta(minutes=10)).isoformat(),
                  'prediction_cutoff':(now+timedelta(minutes=5)).isoformat()}]}
    checker = Mock(return_value=True)
    bound = {'discovery_routes':[{'provider':'NANKAN_OFFICIAL',
        'discover_day':lambda **kw:plan,'verify_discovery':checker}]}
    monkeypatch.setattr(s,'load_binding',lambda *args:bound)
    calls = []
    def tick(plan,root,**kw):
        calls.append(kw['binding'])
        return {'profile':s.PROFILE,'race_date':day,'counts':{'dispatched':0}}
    monkeypatch.setattr(s,'tick',tick)
    discovery = tmp_path/'plan.json'; discovery.write_bytes(s.encoded(plan))
    activation = tmp_path/'activation.json'; activation.write_bytes(b'{}')
    assert s.main(['--discovery-json',str(discovery),'--private-root',str(tmp_path/'private'),
                   '--execute','--binding',str(tmp_path/'SYNTHETIC.py'),'--binding-sha256','a'*64,
                   '--activation',str(activation),'--activation-sha256',hashlib.sha256(b'{}').hexdigest()]) == 0
    assert calls[0]['verify_discovery'] is checker
    checker.assert_called_once()

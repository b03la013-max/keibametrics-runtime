"""FNB input-guard tests; no adoption, real Owner prediction or KRS execution."""
import base64
from copy import deepcopy
from datetime import datetime
import gzip
import hashlib

import pytest

from runtime import local_production_static_owner as owner


def fixture():
    request = {'venue_id': 'FNB', 'race_date': '2026-11-03', 'race_no': 1,
        'scheduled_post_at': '2026-11-03T12:10:00+09:00',
        'prediction_cutoff': '2026-11-03T12:00:00+09:00'}
    body = ('<h4>2026年11月3日 船橋 第1競走 12:10発走</h4>'
            '<h3>C2一</h3><p>ダート 1500m (左)</p><table><tr><td>競走馬</td></tr></table>').encode()
    url = ('https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/DebaTable?'
           'k_raceDate=2026%2F11%2F03&k_babaCode=19&k_raceNo=1')
    card = {'source_class': 'OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT',
        'official': True, 'cutoff_relation': 'PRE_CUTOFF', 'authority': 'NAR_OFFICIAL',
        'http_status': 200, 'raw_gzip_b64': base64.b64encode(gzip.compress(body)).decode(),
        'raw_sha256': hashlib.sha256(body).hexdigest(), 'requested_url': url, 'final_url': url,
        'fetched_at': '2026-11-03T11:50:00+09:00'}
    card['snapshot_sha256'] = owner._sha(card)
    source = {'sources': [card], 'source_freeze_at': '2026-11-03T11:51:00+09:00',
              'prediction_cutoff': request['prediction_cutoff']}
    return request, source


def resign_card(source):
    card = source['sources'][0]
    card['snapshot_sha256'] = owner._sha({k: v for k, v in card.items() if k != 'snapshot_sha256'})


def test_exact_fnb_header_is_input_only_not_scope_activation():
    request, source = fixture()
    assert owner._card_heading(source, expected_race=request)['distance'] == 1500


def test_fnb_printed_clock_normalizes_hour_without_changing_post_time():
    request, source = fixture()
    request['scheduled_post_at'] = '2026-11-03T09:10:00+09:00'
    request['prediction_cutoff'] = source['prediction_cutoff'] = '2026-11-03T09:00:00+09:00'
    source['source_freeze_at'] = '2026-11-03T08:51:00+09:00'
    source['sources'][0]['fetched_at'] = '2026-11-03T08:50:00+09:00'
    raw = gzip.decompress(base64.b64decode(source['sources'][0]['raw_gzip_b64'])).replace(b'12:10', b'9:10')
    source['sources'][0].update(raw_gzip_b64=base64.b64encode(gzip.compress(raw)).decode(),
                               raw_sha256=hashlib.sha256(raw).hexdigest())
    resign_card(source)
    assert owner._card_heading(source, expected_race=request)['distance'] == 1500


@pytest.mark.parametrize('change', ['raw', 'snapshot', 'date', 'venue', 'race', 'url', 'late', 'cutoff', 'ineligible', 'post'])
def test_fnb_raw_url_printed_identity_and_asof_fail_closed(change):
    request, source = fixture()
    card = source['sources'][0]
    if change == 'raw': card['raw_sha256'] = '0' * 64; resign_card(source)
    elif change == 'snapshot': card['snapshot_sha256'] = '0' * 64
    elif change in {'date', 'venue', 'race'}:
        raw = gzip.decompress(base64.b64decode(card['raw_gzip_b64']))
        old, new = {'date': ('2026年11月3日', '2026年11月2日'),
                    'venue': ('船橋', '浦和'), 'race': ('第1競走', '第2競走')}[change]
        raw = raw.decode().replace(old, new).encode()
        card.update(raw_gzip_b64=base64.b64encode(gzip.compress(raw)).decode(), raw_sha256=hashlib.sha256(raw).hexdigest())
        resign_card(source)
    elif change == 'url': card['final_url'] = card['final_url'].replace('k_babaCode=19', 'k_babaCode=18'); resign_card(source)
    elif change == 'late': card['fetched_at'] = '2026-11-03T11:52:00+09:00'; resign_card(source)
    elif change == 'cutoff': source['prediction_cutoff'] = '2026-11-03T12:01:00+09:00'
    elif change == 'ineligible': card['post_cutoff_or_ineligible'] = True; resign_card(source)
    elif change == 'post': request['scheduled_post_at'] = '2026-11-03T11:55:00+09:00'
    with pytest.raises(owner.StaticOwnerError):
        owner._card_heading(source, expected_race=request)


def test_fnb_printed_mixed_class_keeps_both_labels():
    request, source = fixture()
    raw = gzip.decompress(base64.b64decode(source['sources'][0]['raw_gzip_b64']))
    raw = raw.decode().replace('C2一', '長月特別Ｂ２二Ｂ３一').encode()
    source['sources'][0].update(raw_gzip_b64=base64.b64encode(gzip.compress(raw)).decode(),
                               raw_sha256=hashlib.sha256(raw).hexdigest())
    resign_card(source)
    assert owner._card_heading(source, expected_race=request)['class'] == 'B2_B3'


def test_seed1_is_fixed_for_fnb_without_changing_kaw_default():
    request, _ = fixture()
    assert owner._owner_seed(request) == 1
    assert owner._owner_seed({**request, 'seed': 1}) == 1
    for value in (True, 2, '1'):
        with pytest.raises(owner.StaticOwnerError): owner._owner_seed({**request, 'seed': value})
    assert owner._owner_seed({**request, 'venue_id': 'KAW'}) == 2026110301


def test_fnb_exact_alias_and_latest_observation_are_separate_from_model_weights():
    row = {'race_card_fetched_at': '2026-10-01T10:00:00+09:00', 'starts': []}
    for venue, day, finish in [('船ナ橋', '26.09.01', 1), ('船橋ナ', '26.09.30', 3)]:
        row['starts'].append({'venue': venue, 'date': day, 'surface': 'DIRT',
                             'distance': 1500, 'finish': finish, 'field_size': 12})
    day = datetime.fromisoformat('2026-10-02T00:00:00+09:00')
    facts = owner._runner_facts(row, venue_name='船橋', distance=1500, race_day=day)
    assert facts['exact_races'] == 1 and facts['exact_wins'] == 0
    assert facts['recent_dirt_finish_share'] == 9 / 11
    assert facts['observed_runs'][0]['date'] == '2026-09-30'
    row['race_card_fetched_at'] = '2026-09-29T00:00:00+09:00'
    with pytest.raises(owner.StaticOwnerError, match='AFTER_SOURCE_OBSERVATION'):
        owner._runner_facts(row, venue_name='船橋', distance=1500, race_day=day)

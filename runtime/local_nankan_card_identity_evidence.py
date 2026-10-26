"""Private read-only identity evidence from already acquired NANKAN cards.

Observed links are identifiers, not permission to fetch their targets, NAR
license bridges, numerical evidence of jockey skill, or verified ACTIVE status.
No network or numerical calculation occurs in this module.
"""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
import hashlib
import re
from runtime.urw_nankan_reference_source import DOM, Node, decode, norm, reference_metadata, sha

ORIGIN = 'https://www.nankankeiba.com'
JST = timezone(timedelta(hours=9))
VENUES = {'URW': ('18', '浦和'), 'FNB': ('19', '船橋'),
          'OHI': ('20', '大井'), 'KAW': ('21', '川崎')}


def _reject(code):
    raise ValueError(code)


def _clock(value):
    try:
        d = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        if d.tzinfo is None:
            raise ValueError
        return d.astimezone(timezone.utc)
    except (ValueError, TypeError):
        _reject('CARD_IDENTITY_TIMESTAMP_UNKNOWN')


def _link(cell, family, digits, *, required):
    candidates = [a for a in cell.all('a')
                  if f'/{family}/' in a.attrs.get('href', '')]
    if not candidates and not required:
        return None
    if len(candidates) != 1:
        _reject('CARD_IDENTITY_LINK_NOT_UNIQUE')
    a = candidates[0]
    match = re.fullmatch(rf'/{family}/(\d{{{digits}}})\.do', a.attrs.get('href', ''))
    if not match or not a.text():
        _reject('CARD_IDENTITY_LINK_UNSUPPORTED')
    return {'provider_id': match[1], 'name_observed': a.text(),
            'official_url_observed_not_fetched': ORIGIN + a.attrs['href']}


def extract_card_identities(raw, receipt, race, frozen_runners, *, freeze_at):
    """Verify Raw/race/universe/time and expose exact same-provider links.

    ``frozen_runners`` is the preserved card parser's declared universe. A
    matching name alone cannot join a runner: horse number AND horse ID must
    agree first. Missing rider links remain unknown; contradictory ones fail.
    """
    rid = str(race.get('provider_race_id', ''))
    venue = VENUES.get(race.get('venue_id'))
    if (race.get('provider') != 'NANKAN_OFFICIAL' or not venue
            or not re.fullmatch(r'\d{16}', rid)
            or rid[:8] != str(race.get('race_date', '')).replace('-', '')
            or rid[8:10] != venue[0]
            or int(rid[-2:]) != race.get('race_no')):
        _reject('CARD_IDENTITY_RACE_CONTEXT')
    receipt = reference_metadata(receipt)
    expected_url = ORIGIN + '/uma_shosai/' + rid + '.do'
    if (receipt.get('url') != expected_url or receipt.get('http_status') != 200
            or receipt.get('provider') != 'NANKAN_OFFICIAL'
            or receipt.get('raw_sha256') != hashlib.sha256(raw).hexdigest()
            or (receipt.get('source_policy') or {}).get('usage_scope') !=
            'USER_PERSONAL_NONCOMMERCIAL_PRIVATE_ONLY_NOT_PUBLIC_REDISTRIBUTION'):
        _reject('CARD_IDENTITY_RAW_RECEIPT')
    fetched = _clock(receipt.get('fetched_at'))
    freeze = _clock(freeze_at)
    cutoff = _clock(race.get('prediction_cutoff'))
    scheduled = _clock(race.get('scheduled_post_at'))
    scheduled_jst = scheduled.astimezone(JST)
    if scheduled_jst.date().isoformat() != race['race_date'] or cutoff > scheduled:
        _reject('CARD_IDENTITY_SCHEDULE_CONTEXT')
    if not fetched <= freeze < cutoff:
        _reject('CARD_IDENTITY_POSTFREEZE_OR_POSTCUTOFF')
    dom = DOM(decode(raw)).root
    markers = [n.attrs.get('value') for n in dom.all('input')
               if n.attrs.get('id') in ('gamenKirikaeMenu_programId', '_cc_proId')]
    if not markers or set(markers) != {rid}:
        _reject('CARD_IDENTITY_BODY_RACE_ID')
    headers = dom.all('p', 'nk23_c-tab1__subtitle')
    y, m, d = map(int, race['race_date'].split('-'))
    if len(headers) != 1:
        _reject('CARD_IDENTITY_BODY_HEADER')
    header = headers[0].text()
    if (not re.match(rf'{race["race_no"]}R\b', header)
            or f'{y}年{m}月{d}日' not in header or venue[1] + '競馬' not in header
            or scheduled_jst.strftime('%H:%M') not in header
            or not re.search(rf'(?<![\d,])(?:{race["distance"]:,}|{race["distance"]})m\b', header)):
        _reject('CARD_IDENTITY_BODY_HEADER')
    tables = []
    for table in dom.all('table', 'nk23_c-table23__table'):
        rows = [r for r in table.all('tr') if any(
            '/uma_info/' in a.attrs.get('href', '') for a in r.all('a'))]
        if rows:
            tables.append(rows)
    if len(tables) != 1:
        _reject('CARD_IDENTITY_DECLARATION_TABLE_NOT_UNIQUE')
    expected = {}
    normalized_runner_ids = {}
    seen_runner_ids = set()
    for runner in frozen_runners:
        key = int(runner['horse_no'])
        if key in expected or not re.fullmatch(r'\d{10}', str(runner.get('provider_horse_id', ''))):
            _reject('CARD_IDENTITY_FROZEN_UNIVERSE')
        runner_id = runner.get('runner_id')
        if type(runner_id) not in (str, int) or not str(runner_id).strip():
            _reject('CARD_IDENTITY_FROZEN_RUNNER_ID')
        canonical_runner_id = str(runner_id).strip()
        if canonical_runner_id in seen_runner_ids:
            _reject('CARD_IDENTITY_FROZEN_RUNNER_ID_DUPLICATE')
        seen_runner_ids.add(canonical_runner_id)
        normalized_runner_ids[key] = canonical_runner_id
        expected[key] = runner
    if len({r['provider_horse_id'] for r in expected.values()}) != len(expected):
        _reject('CARD_IDENTITY_FROZEN_UNIVERSE')
    detail_tables = [t for t in dom.all('table', 'tb-shousai')
                     if t.attrs.get('id') != 'tb-sample'
                     and 'hidden' not in t.attrs.get('class', '').split()]
    if len(detail_tables) != 1:
        _reject('CARD_IDENTITY_DETAIL_TABLE_NOT_UNIQUE')
    detail = {}
    for row in detail_tables[0].all('tr'):
        number_cells = row.all('td', 'umaban')
        if not number_cells:
            continue
        if len(number_cells) != 1 or not re.fullmatch(r'[1-9]|1[0-6]', number_cells[0].text()):
            _reject('CARD_IDENTITY_DETAIL_ROW')
        no = int(number_cells[0].text())
        horse_ids = {re.fullmatch(r'/uma_info/(\d{10})\.do', a.attrs.get('href', ''))[1]
                     for a in row.all('a') if re.fullmatch(r'/uma_info/(\d{10})\.do', a.attrs.get('href', ''))}
        if no in detail or len(horse_ids) != 1:
            _reject('CARD_IDENTITY_DETAIL_ROW')
        detail[no] = {'horse_id': next(iter(horse_ids)),
                      'jockey': _link(row, 'kis_info', 6, required=False)}
    if set(detail) != set(expected):
        _reject('CARD_IDENTITY_DETAIL_UNIVERSE')
    result = []
    seen = set()
    frame_remaining = 0
    frame_cell = None
    for row in tables[0]:
        cells = [n for n in row.children if isinstance(n, Node) and n.tag == 'td']
        if len(cells) == 12:
            if frame_remaining or cells[0].attrs.get('rowspan', '1') not in ('1', '2'):
                _reject('CARD_IDENTITY_FRAME_ROWSPAN')
            frame_cell = cells[0]
            frame_remaining = int(frame_cell.attrs.get('rowspan', '1'))
        elif len(cells) == 11 and frame_remaining and frame_cell is not None:
            cells = [frame_cell] + cells
        else:
            _reject('CARD_IDENTITY_DECLARATION_ROW')
        if (not re.fullmatch(r'[1-8]', cells[0].text())
                or not re.fullmatch(r'[1-9]|1[0-6]', cells[1].text())):
            _reject('CARD_IDENTITY_DECLARATION_ROW')
        frame_remaining -= 1
        no = int(cells[1].text())
        horse = _link(cells[2], 'uma_info', 10, required=True)
        jockey = _link(cells[7], 'kis_info', 6, required=False)
        exp = expected.get(no)
        if (no in seen or exp is None or exp['provider_horse_id'] != horse['provider_id']
                or norm(exp['name']) != norm(horse['name_observed'])
                or exp.get('frame_no', int(cells[0].text())) != int(cells[0].text())):
            _reject('CARD_IDENTITY_RUNNER_UNIVERSE_MISMATCH')
        detailed = detail[no]
        if detailed['horse_id'] != horse['provider_id']:
            _reject('CARD_IDENTITY_DETAIL_HORSE_CONTRADICTION')
        dj = detailed['jockey']
        if (bool(jockey) != bool(dj) or jockey and
                (jockey['provider_id'] != dj['provider_id']
                 or norm(exp.get('current_jockey', '')) != norm(dj['name_observed']))):
            _reject('CARD_IDENTITY_CURRENT_RIDER_CONTRADICTION')
        seen.add(no)
        result.append({'provider': 'NANKAN_OFFICIAL', 'provider_race_id': rid,
            'horse_no': no, 'runner_id': normalized_runner_ids[no], 'horse': horse,
            'jockey': jockey, 'detail_jockey_label': dj['name_observed'] if dj else None,
            'main_detail_id_match': True, 'name_label_variation_is_not_identity_join': True,
            'jockey_identity_state': 'EXACT_PROVIDER_LINK_ID' if jockey else 'UNKNOWN_LINK_ABSENT',
            'nar_license_id': None, 'cross_provider_identity_verified': False,
            'active_verified': False, 'source_url': expected_url,
            'raw_sha256': receipt['raw_sha256'], 'fetched_at': receipt['fetched_at'],
            'numerical_consumer_enabled': False})
    if frame_remaining or seen != set(expected) or len(seen) != race.get('program_runner_count'):
        _reject('CARD_IDENTITY_RUNNER_UNIVERSE_MISMATCH')
    out = {'profile': 'LOCAL-NANKAN-CARD-IDENTITY-EVIDENCE-RESEARCH-v1',
        'classification': 'FROZEN_SOURCE_IDENTITY_AUDIT_NOT_NEW_PREDICTION',
        'race_id': rid, 'race_date': race['race_date'], 'race_no': race['race_no'],
        'source_raw_sha256': receipt['raw_sha256'], 'source_url': expected_url,
        'source_fetched_at': receipt['fetched_at'], 'original_freeze_at': freeze_at,
        'prediction_cutoff': race['prediction_cutoff'],
        'runner_count': len(result), 'exact_jockey_id_count': sum(r['jockey'] is not None for r in result),
        'independent_raw_source_count': 1, 'rows': result,
        'numerical_policy_changed': False, 'source_scope_expanded': False,
        'source_targets_fetched': 0, 'production_authority': False,
        'registered_oos_credit': 0, 'numerical_consumer_enabled': False}
    out['sha256'] = sha(out)
    return out

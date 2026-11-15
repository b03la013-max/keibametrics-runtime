"""Unsigned current Runner candidate from independent offered race/odds ZIPs.

This preserves ACTIVE_DECLARED when betting participation is unobserved. Zero,
blank or absent odds never prove inactivity. Positive individual win quotes
can corroborate the whole unexcluded field as of the two recorded snapshots;
no future no-change guarantee, SOURCE adoption, signature or licence follows.
The caller supplies any separately adopted freshness limits; no score or
selection parameter is introduced here.
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import csv
import hashlib
import io
import math
import re
import zipfile

from runtime.local_nar_csv_reference import inspect_zip, SCHEMAS, _dt
from runtime.local_nar_csv_download import DAILY_URL, DAILY_ODDS_URL

PROFILE = 'KM-FNB-NAR-CSV-CURRENT-UNIVERSE-CANDIDATE-v0.1-20261104'
STATUS = {'出走取消': 'CANCELLED', '競走除外': 'EXCLUDED'}


def _capture(raw, receipt, url, race_date):
    if (not isinstance(raw, bytes) or not 0 < len(raw) <= 4_000_000
            or receipt.get('provider') != 'NAR_OFFICIAL_CSV'
            or receipt.get('http_status') != 200 or receipt.get('source_url') != url
            or receipt.get('final_url') != url
            or receipt.get('raw_sha256') != hashlib.sha256(raw).hexdigest()
            or receipt.get('retrieval_method') != 'AUTHORIZED_HTTP_GET'):
        raise ValueError('CSV_CURRENT_ORIGINAL_CAPTURE_UNVERIFIED')
    capture_at = _dt(receipt['captured_at'])
    label = 'race' if url == DAILY_URL else 'odds'
    m = re.search(r'filename="?(\d{8})_(\d+)_' + label + r'\.zip"?', receipt.get('content_disposition', ''))
    if not m or m[1] != race_date.replace('-', ''):
        raise ValueError('CSV_CURRENT_ARCHIVE_DAY_OR_TIMESTAMP_UNVERIFIED')
    archive_at = datetime.fromtimestamp(int(m[2]), timezone.utc)
    if archive_at > capture_at:
        raise ValueError('CSV_CURRENT_ARCHIVE_TIME_AFTER_CAPTURE')
    return capture_at, archive_at


def _odds(raw, race_date, race_no):
    key = ('船橋', race_date.replace('-', ''), str(race_no))
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        members = archive.infolist()
        name = race_date.replace('-', '') + '_odds.csv'
        if (len(members) != 1 or members[0].filename != name
                or members[0].file_size > 16_000_000 or members[0].flag_bits & 1
                or archive.testzip() is not None):
            raise ValueError('CSV_CURRENT_ODDS_ARCHIVE_INVALID')
        text = archive.read(name).decode('utf-8-sig')
    reader = csv.DictReader(io.StringIO(text, newline=''))
    if tuple(reader.fieldnames or []) != SCHEMAS['odds']:
        raise ValueError('CSV_CURRENT_ODDS_HEADER_MISMATCH')
    wins = {}
    for number, row in enumerate(reader, 2):
        if None in row or any(v is None for v in row.values()):
            raise ValueError('CSV_CURRENT_ODDS_ROW_SHAPE_INVALID')
        if (row['競馬場'], row['競走年月日'], row['レース番号']) != key or row['賭式'] != '単勝':
            continue
        if not row['番号1'].isdigit() or int(row['番号1']) < 1 or row['番号2'] or row['番号3']:
            raise ValueError('CSV_CURRENT_INDIVIDUAL_WIN_IDENTITY_INVALID')
        rid = str(int(row['番号1']))
        if rid in wins:
            raise ValueError('CSV_CURRENT_WIN_ROW_DUPLICATE')
        price = None
        try:
            number_price = Decimal(row['オッズ'])
            if number_price.is_finite() and number_price > 0:
                price = str(number_price)
        except InvalidOperation:
            pass
        wins[rid] = {'quote': price, 'raw_quote': row['オッズ'],
                     'raw_popularity':row['人気'],'csv_row': number,
                     'state': 'POSITIVE_QUOTE_OBSERVED' if price else 'UNKNOWN'}
    return wins


def assess_current_universe(*, race_raw, race_receipt, request, freeze_at,
                            odds_raw=None, odds_receipt=None, freshness_limits=None):
    """Reparse originals, return honest status evidence, never adopt the Profile.

    ``freshness_limits`` is a pinned external source-quality decision, with
    max_fetch_age_seconds and max_archive_age_seconds, not a model setting.
    Absence of that decision retains observations and yields qualification0.
    Archive age is the documented filename UNIX timestamp, not a fabricated
    per-row update time and not reset by a later HTTP fetch.
    """
    if request.get('venue_id') != 'FNB':
        raise ValueError('CSV_CURRENT_FNB_REQUEST_REQUIRED')
    day, number = request['race_date'], request['race_no']
    freeze = _dt(freeze_at)
    captured, archive = _capture(race_raw, race_receipt, DAILY_URL, day)
    capture = {'provider': 'NAR_OFFICIAL_CSV', 'http_status': 200,
        'source_url': DAILY_URL, 'raw_sha256': race_receipt['raw_sha256'],
        'captured_at': race_receipt['captured_at'], 'retrieval_method': 'AUTHORIZED_HTTP_GET',
        'usage_qualification': {'record_sha256': race_receipt.get('usage_record_sha256'),
                                'not_formal_admission': True}}
    expected = {'venue_id': 'FNB', 'race_date': day, 'race_no': number}
    if request.get('scheduled_post_at'):
        expected['scheduled_post_at'] = request['scheduled_post_at']
    parsed = inspect_zip(race_raw, capture=capture, race=expected,
        encoding='utf-8-sig', header_mode='present', now=freeze)
    if parsed['target_outcome_fields_present']:
        raise ValueError('CSV_CURRENT_ACTUAL_RACE_RESULT_PRESENT')
    if not captured <= freeze < _dt(parsed['race_identity']['scheduled_post_at']):
        raise ValueError('CSV_CURRENT_CAPTURE_FREEZE_POST_ORDER_INVALID')
    if request.get('prediction_cutoff') and freeze >= _dt(request['prediction_cutoff']):
        raise ValueError('CSV_CURRENT_FREEZE_AFTER_CUTOFF')
    rows = {}
    for row in parsed['runners']:
        rid = str(row['runner_number'])
        fields = row['prestart_reference_fields']
        literal = row['outcome_fields_separated']['着差']
        rows[rid] = {'runner_id': rid, 'horse_no': row['runner_number'],
            'name': row['horse_name'], 'jockey': fields['騎手名'],
            'status': STATUS.get(literal, 'ACTIVE_DECLARED'),
            'status_basis': ('EXPLICIT_CSV_NOTICE_LITERAL' if literal in STATUS
                             else 'OFFICIAL_FULL_SNAPSHOT_LISTING_ONLY'),
            'notice_literal': literal if literal in STATUS else None,
            'current_rider_observed_not_change_event': True}
    wins = {}; snapshots = [{'kind': 'race', 'raw_sha256': race_receipt['raw_sha256'],
        'captured_at': captured.isoformat(), 'archive_filename_at': archive.isoformat()}]
    if (odds_raw is None) != (odds_receipt is None):
        raise ValueError('CSV_CURRENT_ODDS_RAW_AND_RECEIPT_BOTH_REQUIRED')
    if odds_raw is not None:
        odds_captured, odds_archive = _capture(odds_raw, odds_receipt, DAILY_ODDS_URL, day)
        if odds_captured > freeze:
            raise ValueError('CSV_CURRENT_ODDS_CAPTURE_AFTER_FREEZE')
        wins = _odds(odds_raw, day, number)
        snapshots.append({'kind': 'odds', 'raw_sha256': odds_receipt['raw_sha256'],
            'captured_at': odds_captured.isoformat(), 'archive_filename_at': odds_archive.isoformat()})
    limits_ok = (isinstance(freshness_limits, dict)
        and all(type(freshness_limits.get(k)) in (int, float)
                and math.isfinite(freshness_limits[k]) and freshness_limits[k] > 0
                for k in ('max_fetch_age_seconds', 'max_archive_age_seconds')))
    for snapshot in snapshots:
        snapshot['fetch_age_seconds'] = (freeze - _dt(snapshot['captured_at'])).total_seconds()
        snapshot['archive_age_seconds'] = (freeze - _dt(snapshot['archive_filename_at'])).total_seconds()
        snapshot['fresh_under_supplied_limits'] = bool(limits_ok
            and snapshot['fetch_age_seconds'] <= freshness_limits['max_fetch_age_seconds']
            and snapshot['archive_age_seconds'] <= freshness_limits['max_archive_age_seconds'])
    contradictions, temporal_disagreements = [], []
    same_snapshot = len(snapshots) == 2 and snapshots[0]['archive_filename_at'] == snapshots[1]['archive_filename_at']
    extra = set(wins) - set(rows)
    if extra:
        (contradictions if same_snapshot else temporal_disagreements).append(
            'OFFICIAL_WIN_NUMBER_NOT_IN_SAME_RACE_CARD:' + ','.join(sorted(extra)))
    for rid in set(wins) & set(rows):
        rows[rid]['independent_win_quote'] = wins[rid]
        if rows[rid]['status'] in {'CANCELLED', 'EXCLUDED'} and wins[rid]['quote']:
            (contradictions if same_snapshot else temporal_disagreements).append(
                'EXPLICIT_SCRATCH_WITH_POSITIVE_WIN_QUOTE:' + rid)
    unexcluded = {rid for rid, row in rows.items() if row['status'] == 'ACTIVE_DECLARED'}
    positive = {rid for rid, value in wins.items() if value['quote'] is not None}
    matched = bool(unexcluded and unexcluded <= positive and not contradictions and not temporal_disagreements)
    fresh = all(s['fresh_under_supplied_limits'] for s in snapshots)
    complete = matched and len(snapshots) == 2 and fresh
    if complete:
        for rid in unexcluded:
            rows[rid].update(status='ACTIVE', status_basis='POSITIVE_INDIVIDUAL_WIN_QUOTE_AND_FRESH_OFFICIAL_CARD')
    return {'profile': PROFILE, 'classification': 'UNADOPTED_PRIVATE_CURRENT_STATUS_CANDIDATE',
        'race_identity': parsed['race_identity'], 'freeze_at': freeze.isoformat(),
        'snapshots': snapshots, 'freshness_limits_supplied': freshness_limits,
        'rows': list(rows.values()), 'listed_count': len(rows),
        'positive_win_ids': sorted(positive), 'active_declared_ids': sorted(unexcluded),
        'observed_unexcluded_betting_set_matches': matched,
        'complete_current_universe_candidate': complete,
        'official_change_event_log_supplied': False,
        'latest_current_fields_observed': True,
        'true_observed_conflicts': contradictions,
        'temporal_reconciliation_required': temporal_disagreements,
        'no_future_change_guarantee': True, 'row_update_time_inferred': False,
        'source_admitted': False, 'profile_adopted': False, 'signature_verified': False,
        'provider_licence_granted': False, 'production_consumers_authorized': False}

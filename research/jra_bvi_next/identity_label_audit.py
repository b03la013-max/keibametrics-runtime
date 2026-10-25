"""Offline audit of retained, independently qualified navigation evidence.

No network, locator decoding, alias inference, permanent-ID promotion, or
Production write. The qualification is inherited from one retrieved CI artifact;
its OIDC claims are NOT represented as a fresh verification in this process.
"""
from __future__ import annotations

import argparse
import base64
from collections import Counter, defaultdict
from datetime import datetime
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

REPO = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(REPO / 'scripts'), str(REPO / 'runtime'),
                str(REPO / 'runtime/jra_source_runtime')]
from jra_pedigree_identity_recovery import (
    verify_recovery_bindings, stamp, sha_obj, profile, signature, official_link,
)
from source_acquisition import _decode
from jra_same_day_results import parse_result_detail
from jra_race_day_resolver import VENUES as OFFICIAL_VENUES

VENUES = {venue_id:name for venue_id,name in OFFICIAL_VENUES.values()}


def raw_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_qualification(recovery, qualification, root):
    """Bind retained CI outputs and recompute their stated eligible counts."""
    for item in (recovery, qualification):
        if item.get('sha256') != sha_obj({k:v for k,v in item.items() if k != 'sha256'}):
            raise ValueError('IDENTITY_AUDIT_REPORT_HASH')
    if (qualification['recovery_sha256'] != recovery['sha256']
            or qualification['target_cutoff'] != recovery['target_cutoff']
            or qualification.get('research_training_eligible') is not False
            or qualification.get('production_eligible') is not False
            or qualification.get('permanent_registry_ids_resolved') != 0):
        raise ValueError('IDENTITY_AUDIT_QUALIFICATION_SCOPE')
    verify_recovery_bindings(recovery, root)
    cutoff = stamp(recovery['target_cutoff'])
    files = qualification['file_verifications']
    for name, record in files.items():
        expected = ((recovery['corpus_files'].get(name) or {}).get('file_sha256')
                    or recovery['source_files'].get(name))
        path = (Path(root) / name).resolve()
        if not path.is_relative_to(Path(root).resolve()):
            raise ValueError('IDENTITY_AUDIT_PATH')
        if not expected or record['file_sha256'] != expected or raw_sha(path) != expected:
            raise ValueError('IDENTITY_AUDIT_ORIGINAL_CHANGED')
        times = [stamp(t) for check in record.get('checks') or [] if check.get('verified') is True
                 for t in check.get('verified_timestamps') or []]
        if record.get('qualified') is not bool(times and min(times) < cutoff):
            raise ValueError('IDENTITY_AUDIT_QUALIFICATION_CLOCK')
    qualified = []
    run_count = 0
    for row in recovery['resolved']:
        corpus_ok = files.get(row['corpus_file'], {}).get('qualified', False)
        source = recovery['raw_proofs'][row['proof']]['source_envelope']
        if corpus_ok and row['chronology_before_target'] and files.get(source, {}).get('qualified', False):
            qualified.append(row)
        for run in row['run_bindings']:
            source = recovery['raw_proofs'][run['proof']]['source_envelope']
            run_count += bool(corpus_ok and run['chronology_before_target']
                              and files.get(source, {}).get('qualified', False))
    expected_keys = {(x['corpus_file'], x['observation_index'], x['official_profile_token'])
                     for x in qualification['qualified']}
    actual_keys = {(x['corpus_file'], x['observation_index'], x['official_profile_token']) for x in qualified}
    if (expected_keys != actual_keys
            or len(qualified) != qualification['qualified_profile_locator_observations']
            or run_count != qualification['qualified_result_locator_runs']):
        raise ValueError('IDENTITY_AUDIT_QUALIFICATION_COUNT')
    return qualified, run_count


def surface(value):
    return {'ダート':'ダ', 'DIRT':'ダ', 'TURF':'芝'}.get(value, value)


def result_identity(artifact, race_no):
    """Use the already-bound SOURCE context, never decode an opaque CNAME."""
    context = artifact.get('source_race_context') or {}
    day, venue = context.get('race_date'), context.get('venue_id')
    if not day or venue not in VENUES or not isinstance(race_no, int) or not 1 <= race_no <= 12:
        raise ValueError('IDENTITY_AUDIT_RESULT_CONTEXT')
    expected = f"KM-JRA-{venue}-{day.replace('-', '')}-R{int(context.get('race_no') or 0):02d}"
    if artifact.get('race_id') != expected:
        raise ValueError('IDENTITY_AUDIT_RESULT_CONTEXT_BINDING')
    return f"KM-JRA-{venue}-{day.replace('-', '')}-R{race_no:02d}", day, VENUES[venue]


def verify_result_heading(soup, day, venue, race_no):
    headings = [h.get_text(' ',strip=True) for h in soup.select('h1')
                if h.get_text(' ',strip=True).startswith('レース結果')]
    if len(headings) != 1:
        raise ValueError('INDEPENDENT_RESULT_HEADING')
    text = headings[0]
    found_day = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日',text)
    found_race = re.search(r'(\d{1,2})レース\s*$',text)
    if (not found_day or not found_race or venue not in text
            or '-'.join(f'{int(x):02d}' if i else x for i,x in enumerate(found_day.groups())) != day
            or int(found_race[1]) != race_no):
        raise ValueError('INDEPENDENT_RESULT_HEADING_CONTEXT_MISMATCH')


def scan(root, recovery, qualification):
    root = Path(root)
    qualified, run_count = validate_qualification(recovery, qualification, root)
    files = qualification['file_verifications']
    envelopes = {}
    snapshots = {}
    def envelope(name):
        if name not in envelopes:
            envelopes[name] = json.loads((root / name).read_text())['artifact']
        return envelopes[name]
    def raw_profile(sid):
        if sid not in snapshots:
            ref = recovery['raw_proofs'][sid]
            art = envelope(ref['source_envelope'])
            snap = next(s for s in art['sources'] if s['snapshot_sha256'] == sid)
            raw = gzip.decompress(base64.b64decode(snap['raw_gzip_b64'], validate=True))
            decoded = _decode(raw, snap['content_type'])
            snapshots[sid] = (profile(snap), BeautifulSoup(decoded, 'html.parser'))
        return snapshots[sid]

    identities = defaultdict(set)
    profile_tokens = defaultdict(set)
    parents = {key: Counter() for key in ('sire', 'dam', 'damsire')}
    parent_token_counts = Counter()
    permanent_labels = []
    horse_runs = {}
    all_run_observations = 0
    qualified_run_observations = []
    corpus_cache = {}
    for row in qualified:
        if row['corpus_file'] not in corpus_cache:
            corpus_cache[row['corpus_file']] = json.loads((root/row['corpus_file']).read_text())
        horse = corpus_cache[row['corpus_file']]['horses'][row['observation_index']]
        identity = signature(horse)
        identities[horse['horse_name']].add(identity)
        profile_tokens[identity].add(row['official_profile_token'])
        for key in parents:
            parents[key][horse.get(key) or 'MISSING'] += 1
            parent_token_counts[key] += bool(row['parent_profile_tokens'][key])
        for sid in {row['proof'], *(x for x in row['parent_profile_proofs'].values() if x)}:
            parsed, soup = raw_profile(sid)
            for label in soup.select('dt, th'):
                text = label.get_text(' ', strip=True)
                if re.fullmatch(r'(?:血統登録番号|競走馬登録番号|登録番号|JRA馬ID|JRA Horse ID)', text, re.I):
                    permanent_labels.append({'snapshot_sha256':sid,'label':text})
        for bound in row['run_bindings']:
            source = recovery['raw_proofs'][bound['proof']]['source_envelope']
            if (not bound['chronology_before_target'] or not files.get(source, {}).get('qualified')):
                continue
            run = horse['runs'][bound['run_index']]
            key = (identity, run['date'], run['venue'], run['race_name'], surface(run['surface']),
                   run['distance_m'], run['finish'], run['field_size'])
            all_run_observations += 1
            qualified_run_observations.append({'key':key,'profile_token':row['official_profile_token'],
                'result_navigation_token':bound['official_result_navigation_token'], 'run':run,
                'available_at':max(stamp(row['original_observation_at']),
                                   stamp(recovery['raw_proofs'][bound['proof']]['fetched_at'])).isoformat()})
            horse_runs.setdefault(key, {'identity':identity,'run':run})

    # Extract a separate direct-result endpoint only from the already qualified
    # SOURCE files. No stored normalized result flag can replace original bytes.
    result_rows = defaultdict(list)
    result_holds = Counter()
    distinct_result_snapshots = set()
    result_evidence = []
    for name, check in sorted(files.items()):
        if not check.get('qualified') or not name.startswith('runtime/executions/'):
            continue
        art = envelope(name)
        by_snapshot = {s.get('snapshot_sha256'):s for s in art.get('sources', [])}
        same_day = art.get('jra_official_same_day_results') or {}
        for race in (same_day.get('races') or {}).values():
            sid = race.get('source_snapshot_sha256')
            snap = by_snapshot.get(sid)
            if sid in distinct_result_snapshots:
                continue
            try:
                if (not snap or snap.get('source_class') != 'OFFICIAL_JRA_SAME_DAY_RESULT'
                        or snap.get('official') is not True
                        or snap.get('authority') != 'JRA_OFFICIAL' or snap.get('http_status') != 200
                        or snap.get('raw_encoding') != 'gzip+base64'
                        or sid != sha_obj({k:v for k,v in snap.items() if k != 'snapshot_sha256'})
                        or stamp(snap['fetched_at']) > stamp(art['source_freeze_at'])
                        or stamp(snap['fetched_at']) >= stamp(recovery['target_cutoff'])):
                    raise ValueError('INDEPENDENT_RESULT_SNAPSHOT_UNQUALIFIED')
                for url in (snap['requested_url'],snap['final_url']):
                    parsed_url=urlsplit(url)
                    if (parsed_url.scheme!='https' or parsed_url.netloc!='www.jra.go.jp'
                            or parsed_url.path not in ('/JRADB/accessS.html','/JRADB/accessD.html')
                            or parsed_url.fragment):
                        raise ValueError('INDEPENDENT_RESULT_NON_OFFICIAL_ENDPOINT')
                raw = gzip.decompress(base64.b64decode(snap['raw_gzip_b64'], validate=True))
                if hashlib.sha256(raw).hexdigest() != snap['raw_sha256']:
                    raise ValueError('INDEPENDENT_RESULT_RAW_HASH')
                parsed = parse_result_detail(raw, snap['content_type'])
                race_id, day, venue = result_identity(art, race.get('race_no'))
                soup = BeautifulSoup(_decode(raw, snap['content_type']), 'html.parser')
                verify_result_heading(soup,day,venue,race['race_no'])
                labels = {s.get_text(' ',strip=True) for s in soup.select('.race_name')}
                if len(labels) != 1:
                    raise ValueError('INDEPENDENT_RESULT_RACE_NAME')
                race_name = labels.pop()
                environment = parsed['race_environment']
                field = len(parsed['runners']) + len(parsed.get('non_finishers', []))
                tokens_by_name = defaultdict(set)
                for tr in soup.select('tr'):
                    for link in tr.select('a[href]'):
                        try:
                            token = official_link(link['href'], 'U')
                        except ValueError:
                            continue
                        tokens_by_name[link.get_text(' ',strip=True)].add(token)
                for runner in parsed['runners']:
                    key = (day, venue, race_name, surface(environment.get('surface')),
                           environment.get('distance_m'), runner['horse_name'], runner['finish'], field)
                    result_rows[key].append({'race_id':race_id,'snapshot_sha256':sid,
                        'raw_sha256':snap['raw_sha256'],'file':name,'observed_at':snap['fetched_at'],
                        'horse_no':runner['horse_no'],
                        'horse_navigation_tokens':sorted(tokens_by_name[runner['horse_name']])})
                distinct_result_snapshots.add(sid)
                result_evidence.append({'race_id':race_id,'snapshot_sha256':sid,'runner_count':field,
                    'file':name,'observed_at':snap['fetched_at'],'raw_sha256':snap['raw_sha256']})
            except (ValueError, KeyError, TypeError) as exc:
                result_holds[str(exc)] += 1
    matched = []
    unmatched = Counter()
    for key, item in horse_runs.items():
        identity, day, venue, race_name, surf, distance, finish, field = key
        match_key = (day, venue, race_name, surf, distance, identity[0], finish, field)
        candidates = result_rows.get(match_key, [])
        race_ids = {r['race_id'] for r in candidates}
        if len(race_ids) != 1:
            unmatched['NO_UNIQUE_EXACT_DIRECT_RESULT_CONTEXT'] += 1
            continue
        observed_tokens = {t for r in candidates for t in r['horse_navigation_tokens']}
        exact_profile = bool(profile_tokens[identity] & observed_tokens)
        matched.append({'composite_identity':list(identity), 'run':item['run'],
            'official_race_id':next(iter(race_ids)), 'direct_result_evidence':candidates,
            'exact_profile_navigation_join':exact_profile,
            'label_disposition':'EXACT_DIRECT_RESULT_CONTEXT_AND_NAME_FINISH_MATCH_NOT_PERMANENT_HORSE_ID',
            'permanent_horse_id':None,'production_training_eligible':False})
    parent_unique = {}
    for key in parents:
        groups = defaultdict(set)
        for identities_for_name in identities.values():
            for identity in identities_for_name:
                index = {'sire':1,'dam':2,'damsire':3}[key]
                groups[identity[index]].add(identity)
        parent_unique[key] = [{'parent':p,'composite_offspring':len(v),
                               'independent_permanent_offspring':None} for p,v in sorted(groups.items())]
    out = {'profile':'KM-JRA-PEDIGREE-SCIENTIFIC-IDENTITY-LABEL-AUDIT-v1',
        'classification':'OFFLINE_AUDIT_OF_RETRIEVED_CI_QUALIFICATION / NO_FRESH_OIDC / NOT_FORWARD_OOS',
        'source_recovery_sha256':recovery['sha256'], 'source_qualification_sha256':qualification['sha256'],
        'inherited_qualification_cutoff':recovery['target_cutoff'],
        'file_hashes_rechecked':len(files),'offline_original_bindings_reverified':True,
        'qualified_profile_observations':len(qualified), 'qualified_result_navigation_observations':run_count,
        'profile_observations_used_for_relationships':len(qualified),
        'independent_composite_horses':sum(len(v) for v in identities.values()),
        'same_name_conflicting_pedigree_count':sum(len(v)>1 for v in identities.values()),
        'same_composite_multiple_navigation_count':sum(len(v)>1 for v in profile_tokens.values()),
        'parent_navigation_observation_counts':dict(parent_token_counts),
        'unique_bound_historical_runs':len(horse_runs),
        'run_observations_attached_to_qualified_profiles':all_run_observations,
        'duplicate_bound_history_observations_removed':all_run_observations-len(horse_runs),
        'explicit_permanent_id_label_candidates':permanent_labels,
        'qualified_raw_profile_snapshots_scanned':len(snapshots),
        'permanent_horse_ids':0,'permanent_parent_ids':0,
        'independently_observed_result_snapshots':len(distinct_result_snapshots),
        'independent_result_contexts':len({x['race_id'] for x in result_evidence}),
        'exact_direct_result_context_label_matches':len(matched),
        'exact_profile_navigation_and_result_label_matches':sum(x['exact_profile_navigation_join'] for x in matched),
        'unmatched_run_classification':dict(unmatched), 'independent_result_holds':dict(result_holds),
        'permanent_id_and_independent_race_training_eligible':0,
        'eligible_for_production_training':False,'production_effect':'NONE','oos_increment':0,
        'opponent_strength_status':'DIRECT_RESULT_FIELDS_OBSERVED_ONLY; NO_VALIDATED_PRE_EVENT_OPPONENT_ABILITY',
        'identity_limit':'Opaque CNAME tokens are not decoded or merged; exact name/context labels remain composite identities.',
        'parent_composite_offspring_distribution':parent_unique,
        'matched_direct_result_labels':matched,'independent_result_evidence':result_evidence,
        'code_sha256':raw_sha(__file__)}
    out['sha256'] = sha_obj(out)
    return out


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,default=REPO)
    p.add_argument('--recovery',type=Path,required=True)
    p.add_argument('--qualification',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    result=scan(a.root,json.loads(a.recovery.read_text()),json.loads(a.qualification.read_text()))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    if a.output.exists(): raise ValueError('IDENTITY_AUDIT_OUTPUT_IMMUTABLE')
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if not isinstance(v,(dict,list))},ensure_ascii=False))

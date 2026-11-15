"""One private research input document with honest child-provider lineage.

The document is an unsigned intermediate, not a provider HTTP response, SOURCE
receipt, Active proof or model adoption. Native IDs come exclusively from the
pinned independently reviewed official event/DOB bridge. Existing formulas and
the fixed prediction model are unchanged.
"""
from __future__ import annotations

import base64
from collections import Counter
from copy import deepcopy
from datetime import date, datetime, timezone
from decimal import Decimal, localcontext
import hashlib
import json
import os
from pathlib import Path

from runtime import local_base63_source_witness as witness
from runtime.local_fnb_csv_preliminary_numeric import materialize_preliminary, _independent_csv_field
from runtime.local_fnb_context_static_candidate import OBSERVATION_PROFILE, CLASSIFICATION as MODEL_CLASSIFICATION, CANON
from runtime.local_fnb_id_history_reference import build_id_history_index
from runtime.local_fnb_r8_arithmetic_29 import verify_29

PROFILE = 'KM-FNB-OFFICIAL-ID-LINKED-DERIVED-RESEARCH-INPUT-v1'
CLASSIFICATION = 'PRIVATE_UNSIGNED_DERIVED_REFERENCE_NOT_SOURCE_NOT_ACTIVE_NOT_PRESTART_NOT_OOS'
CURRENT_CSV_SHA = '52c1ff60f6ac9179a55ed31d0003792d288b2904078906d54874b5cba6803be6'
BRIDGE_SHA = 'be2eaf4b768a776b8cee9489d1eac9e0c89ab48fdc1604fd5218ffb1033a0003'
BRIDGE_REVIEW_SHA = '7795914986164a87d2135a77ba278ca7ffb7b38d9ab05d59b9abc36850f538b6'
OWNER_SHA = 'b80a057ea16a76384db667c407825ce5b415272825b338f15291582ce5b54008'
MODEL_SHA = '8fbee4eafada822ddb28185eb7233a96626e9ce93c8ff9a705fc3516faf9eed4'
MODEL_PROFILE_SHA = 'ba2e04aa9ca36f9adb2813d2376c81c15b857f15bebc320a408c5877c9240735'
NOT_BEFORE = '2026-11-03T15:54:46.876103+00:00'
_HISTORY_COMPONENTS = frozenset(('recent_finish','finish_margin','passing_position_content','class_level','opponent_strength','repeatability','same_venue','same_distance','similar_distance','course_geometry','turn_direction','going_fit','running_style_repro','position_acquisition','position_maintenance','third_corner_progression','leadership_stalk_acceptance','kickback_traffic_tolerance','going_adaptation','jockey_reproducibility','venue_recent','distance_record','position_acquisition_skill','progression_timing_skill','favorite_reliability','longshot_record','transfer_preparation','layoff_preparation','jockey_use_continuity','rotation_management','good_weight_range','interval','fatigue_rebound','official_recent_coverage','same_venue_distance_comparability','bodyweight_range_coverage','previous_class','recent_opponent_class','class_change_pressure','transfer_class','class_relative_time'))
IDENTITY_FIELDS = ('馬名','生年月日','父馬名','母馬名','母父馬名','性','齢')


def _sha(raw): return hashlib.sha256(raw).hexdigest()
def _encode(obj): return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def _hash(obj): return _sha(_encode(obj))
def _time(value):
    out=datetime.fromisoformat(str(value).replace('Z','+00:00'))
    if out.tzinfo is None: raise ValueError('ID_DOCUMENT_AWARE_TIME_REQUIRED')
    return out

def _original(raw):
    return {'sha256':_sha(raw),'bytes':len(raw),'base64':base64.b64encode(raw).decode()}

def _decode(original):
    raw=base64.b64decode(original['base64'],validate=True)
    if len(raw)!=original['bytes'] or _sha(raw)!=original['sha256']:
        raise ValueError('ID_DOCUMENT_CHILD_ORIGINAL_SHA_INVALID')
    return raw

def _pinned_json(raw,pin,label):
    if _sha(raw)!=pin: raise ValueError('ID_DOCUMENT_'+label+'_PIN_INVALID')
    return json.loads(raw)

def _current_original(raw,capture):
    if (_sha(raw)!=CURRENT_CSV_SHA or capture.get('raw_sha256')!=CURRENT_CSV_SHA
            or capture.get('captured_at')!='2026-11-03T15:06:41.192644+00:00'
            or capture.get('source_url')!='https://www.keiba.go.jp/KeibaWeb/DataDownload/RaceDataDownload?type=daily'):
        raise ValueError('ID_DOCUMENT_EXACT_NEW_CURRENT_CSV_ORIGINAL_REQUIRED')

def _resolve_current(parsed,bridge):
    identity=parsed['race_identity']
    if identity['race_date']!='2026-11-04' or identity['race_no']!=1 or identity.get('venue_id','FNB')!='FNB':
        raise ValueError('ID_DOCUMENT_ONLY_AUTHORIZED_NEW_FNB_20261104_R1')
    resolved={}
    for row in parsed['runners']:
        key=['船橋','20261104',1,row['runner_number']]
        matches=[x for x in bridge['resolved'] if x['current_event_key']==key]
        if len(matches)>1: raise ValueError('ID_DOCUMENT_CURRENT_NATIVE_ID_AMBIGUOUS')
        if not matches: continue
        joined=matches[0];facts=row['prestart_reference_fields']
        current={field:row['horse_name'] if field=='馬名' else facts[field] for field in IDENTITY_FIELDS}
        if current!=joined['current_identity_facts']:
            raise ValueError('ID_DOCUMENT_CURRENT_EXACT_OFFICIAL_FACT_CONFLICT')
        if joined.get('Active_verified') is not False or joined.get('Production_qualification_granted') is not False:
            raise ValueError('ID_DOCUMENT_BRIDGE_AUTHORITY_PROMOTION_FORBIDDEN')
        resolved[str(row['runner_number'])]=deepcopy(joined)
    return resolved

def _index(root,manifest,native_ids,asof,target,*,embedded=None,historical_raw=None,historical_capture=None):
    kwargs={'envelope_raw_by_sha':embedded} if embedded is not None else {}
    if historical_raw is not None:
        kwargs.update(historical_csv_raw=historical_raw,historical_csv_receipt=historical_capture)
    return build_id_history_index(root,manifest,native_ids,asof,target,**kwargs)

def _write_new(path,raw):
    from runtime.local_fnb_research_runtime import _private_root, ResearchHold
    path=Path(path);_private_root(path.parent)
    if path.is_symlink():raise ResearchHold('PRIVATE_STORE_SYMLINK_FORBIDDEN')
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as stream:
        stream.write(raw);stream.flush();os.fsync(stream.fileno())


def prepare_document(path,*,current_raw,capture,race,bridge_raw,bridge_review_raw,
                     historical_csv_raw,historical_csv_capture,owner_decision_raw,repo_root=None):
    """Save actual child originals first, then record actual document availability."""
    root=Path(repo_root or Path(__file__).resolve().parents[1]).resolve()
    bridge=_pinned_json(bridge_raw,BRIDGE_SHA,'OFFICIAL_BRIDGE')
    review=_pinned_json(bridge_review_raw,BRIDGE_REVIEW_SHA,'INDEPENDENT_REVIEW')
    owner=_pinned_json(owner_decision_raw,OWNER_SHA,'OWNER_DECISION')
    if review['report_file_sha256']!=BRIDGE_SHA or review['review_status']!='PASS_FACTUAL_OFFICIAL_RECORD_IDENTITY_BRIDGE_NOT_CURRENT_SOURCE_ADMISSION':
        raise ValueError('ID_DOCUMENT_INDEPENDENT_BRIDGE_REVIEW_REQUIRED')
    if _sha(historical_csv_raw)!=bridge['historical_original']['sha256']:
        raise ValueError('ID_DOCUMENT_HISTORICAL_CSV_PIN_INVALID')
    if owner.get('model_code_sha256')!=MODEL_SHA or owner.get('model_profile_sha256',owner.get('profile_sha256'))!=MODEL_PROFILE_SHA:
        # The exact original is pinned; preserve its actual nested schema below.
        if MODEL_SHA not in json.dumps(owner) or MODEL_PROFILE_SHA not in json.dumps(owner):
            raise ValueError('ID_DOCUMENT_FIXED_OWNER_MODEL_PINS_REQUIRED')
    now=datetime.now(timezone.utc)
    if now<=_time(NOT_BEFORE):raise ValueError('ID_DOCUMENT_BEFORE_NEW_IDENTITY_AVAILABLE')
    _current_original(current_raw,capture)
    if historical_csv_capture!=bridge['historical_original']['capture']:raise ValueError('ID_DOCUMENT_EXACT_HISTORICAL_CAPTURE_REQUIRED')
    baseline=materialize_preliminary(current_raw,capture=capture,race=race,repo_root=root,now=now)
    resolved=_resolve_current(baseline['parsed'],bridge)
    native_ids=sorted({x['observed_official_horse_id'] for x in resolved.values()})
    index=_index(root,bridge['archive_source_manifest'],native_ids,now.isoformat(),race['race_date'],
        historical_raw=historical_csv_raw,historical_capture=historical_csv_capture)
    selected=set(index['used_envelope_paths'])
    manifest=[m for m in bridge['archive_source_manifest'] if m['envelope_path'] in selected]
    originals={m['envelope_file_sha256']:_original(Path(m['envelope_path']).read_bytes()) for m in manifest}
    document={'profile':PROFILE,'classification':CLASSIFICATION,'race':deepcopy(race),
        'prepared_at':now.isoformat(),'identity_consumption_not_before':NOT_BEFORE,
        'current_csv_capture':deepcopy(capture),'historical_csv_capture':deepcopy(historical_csv_capture),
        'current_csv_original':_original(current_raw),'historical_csv_original':_original(historical_csv_raw),
        'official_identity_bridge_original':_original(bridge_raw),'independent_bridge_review_original':_original(bridge_review_raw),
        'reference_owner_decision_original':_original(owner_decision_raw),
        'archive_source_manifest':manifest,'archive_envelope_originals':originals,
        'archive_search_receipt':index['receipt'],
        'input_kind':'REAL_UNSIGNED_DERIVED_JSON_DOCUMENT_NOT_PROVIDER_HTTP_RAW',
        'formal_source_admitted':False,'active_universe_verified':False,'source_signature_issued':False,
        'new_numeric_policy':False,'retroactive_R12_enrichment':False,'actual_purchase':False}
    raw=_encode(document);_write_new(path,raw)
    availability={'profile':PROFILE,'document_sha256':_sha(raw),'document_bytes':len(raw),
        'available_at':datetime.now(timezone.utc).isoformat(),
        'availability_basis':'UTC_OBSERVED_AFTER_EXCLUSIVE_WRITE_FLUSH_FSYNC',
        'document_kind':'DERIVED_DOCUMENT_NOT_PROVIDER_HTTP_RAW','formal_source_receipt':False}
    _write_new(str(path)+'.availability.json',_encode(availability))
    return {'path':str(Path(path).resolve()),'sha256':_sha(raw),'availability':availability}


def load_document(path,*,repo_root=None,now=None):
    """Replay embedded originals; never accept caller-built numerical/observation JSON."""
    path=Path(path);raw=path.read_bytes();availability=json.loads(Path(str(path)+'.availability.json').read_bytes())
    if availability.get('document_sha256')!=_sha(raw) or availability.get('document_bytes')!=len(raw):
        raise ValueError('ID_DOCUMENT_AVAILABILITY_HASH_INVALID')
    result=materialize_document(raw,availability=availability,repo_root=repo_root,now=now)
    result['document_path']=str(path.resolve())
    return result


def materialize_document(document_raw,*,availability,repo_root=None,now=None):
    root=Path(repo_root or Path(__file__).resolve().parents[1]).resolve();doc=json.loads(document_raw)
    clock=now or datetime.now(timezone.utc);freeze=_time(availability['available_at'])
    if (doc.get('profile')!=PROFILE or doc.get('classification')!=CLASSIFICATION
        or doc.get('input_kind')!='REAL_UNSIGNED_DERIVED_JSON_DOCUMENT_NOT_PROVIDER_HTTP_RAW'
        or availability.get('document_sha256')!=_sha(document_raw)
        or availability.get('document_bytes')!=len(document_raw)
        or availability.get('document_kind')!='DERIVED_DOCUMENT_NOT_PROVIDER_HTTP_RAW'
        or availability.get('formal_source_receipt') is not False
        or any(doc.get(k) is not False for k in ('formal_source_admitted','active_universe_verified','source_signature_issued','new_numeric_policy','retroactive_R12_enrichment','actual_purchase'))
        or not _time(NOT_BEFORE)<_time(doc['prepared_at'])<=freeze<=clock):
        raise ValueError('ID_DOCUMENT_CLASSIFICATION_OR_ACTUAL_AVAILABILITY_INVALID')
    bridge_raw=_decode(doc['official_identity_bridge_original']);bridge=_pinned_json(bridge_raw,BRIDGE_SHA,'OFFICIAL_BRIDGE')
    review=_pinned_json(_decode(doc['independent_bridge_review_original']),BRIDGE_REVIEW_SHA,'INDEPENDENT_REVIEW')
    if review['report_file_sha256']!=BRIDGE_SHA:raise ValueError('ID_DOCUMENT_BRIDGE_REVIEW_MISMATCH')
    owner_raw=_decode(doc['reference_owner_decision_original']);owner=_pinned_json(owner_raw,OWNER_SHA,'OWNER_DECISION')
    current_raw=_decode(doc['current_csv_original']);historical_raw=_decode(doc['historical_csv_original'])
    if _sha(historical_raw)!=bridge['historical_original']['sha256']:raise ValueError('ID_DOCUMENT_HISTORICAL_CSV_PIN_INVALID')
    _current_original(current_raw,doc['current_csv_capture'])
    if doc['historical_csv_capture']!=bridge['historical_original']['capture']:raise ValueError('ID_DOCUMENT_EXACT_HISTORICAL_CAPTURE_REQUIRED')
    baseline=materialize_preliminary(current_raw,capture=doc['current_csv_capture'],race=doc['race'],repo_root=root,now=clock)
    resolved=_resolve_current(baseline['parsed'],bridge)
    native_ids=sorted({x['observed_official_horse_id'] for x in resolved.values()})
    # Only exact entries of the independently reviewed archive manifest may be supplied.
    original_manifest={m['envelope_file_sha256']:m for m in bridge['archive_source_manifest']}
    manifest=doc['archive_source_manifest']
    if not manifest or any(original_manifest.get(m['envelope_file_sha256'])!=m for m in manifest):
        raise ValueError('ID_DOCUMENT_ARCHIVE_MANIFEST_NOT_PINNED_BRIDGE_MEMBER')
    embedded={key:_decode(value) for key,value in doc['archive_envelope_originals'].items()}
    if set(embedded)!={m['envelope_file_sha256'] for m in manifest}:raise ValueError('ID_DOCUMENT_EMBEDDED_MANIFEST_SET_MISMATCH')
    index=_index(root,manifest,native_ids,doc['prepared_at'],doc['race']['race_date'],embedded=embedded,
        historical_raw=historical_raw,historical_capture=doc['historical_csv_capture'])
    request=deepcopy(baseline['request']);request['classification']=CLASSIFICATION
    request['race_id']='KM-LOCAL-FNB-20261104-R01-R13-OFFICIAL-ID-REV1'
    source=deepcopy(baseline['source']);source['classification']=CLASSIFICATION
    document_sha=_sha(document_raw);source['source_snapshot_sha256']=document_sha;source['source_freeze_at']=freeze.isoformat()
    source['derived_document_sha256']=document_sha;source['derived_document_kind']='DERIVED_DOCUMENT_NOT_PROVIDER_HTTP_RAW'
    current=deepcopy(baseline['raw_field']);context,independent=_independent_csv_field(current_raw,doc['current_csv_capture'],doc['race'],'utf-8-sig')
    joins={}
    for rid,join in resolved.items():
        entry=index['entries'][join['observed_official_horse_id']]
        if len(entry['starts'])!=len(entry['independent_history']):raise ValueError('ID_DOCUMENT_HISTORY_WITNESS_COUNT_CONFLICT')
        for a,b in zip(entry['starts'],entry['independent_history']):
            if date(2000+int(a['date'][:2]),int(a['date'][3:5]),int(a['date'][6:8]))!=b['date']:
                raise ValueError('ID_DOCUMENT_HISTORY_WITNESS_DATE_CONFLICT')
        current[rid]['starts']=deepcopy(entry['starts']);independent[rid]['history']=deepcopy(entry['independent_history'])
        # A factual observed ID bridge is not current SOURCE identity admission.
        current[rid]['horse_id']=None;current[rid]['archived_observed_official_horse_id']=entry['horse_id']
        current[rid]['history_identity_status']='INDEPENDENTLY_REVIEWED_OFFICIAL_EVENT_DOB_NATIVE_ID_BRIDGE_NOT_CURRENT_SOURCE'
        joins[rid]={'observed_native_id':entry['horse_id'],'bridge_sha256':BRIDGE_SHA,
            'current_permanent_horse_id':None,'actual_starts_consumed':len(entry['starts']),
            'current_official_csv_origin':baseline['raw_field'][rid]['field_provenance'],
            'bridge_witnesses':deepcopy(join['bridge_witnesses']),'history_provenance':deepcopy(entry['provenance']),
            'source_refs':sorted(set(entry['source_refs']+[BRIDGE_SHA,document_sha]))}
    from runtime.local_nar_evidence_candidate import compile_parsed_candidate_evidence
    from runtime.local_fullnumerical_candidate import materialize_candidate
    registry_path=root/'mapping/local_evidence_feature_rule_registry_v0.1_candidate_20260923.json'
    mapping_path=root/'mapping/local_full_numerical_mapping_v0.1_candidate_20260923.json'
    registry=json.loads(registry_path.read_bytes());mapping=json.loads(mapping_path.read_bytes())
    compiled=compile_parsed_candidate_evidence(source,request,current,registry_path)
    # Store provenance on every actual historical input, without inventing a current SOURCE grant.
    for runner in compiled['runners']:
        join=joins.get(str(runner['runner_id']))
        if not join or not join['actual_starts_consumed']:continue
        for name,feature in runner['evidence_features'].items():
            if name in _HISTORY_COMPONENTS and feature['missing'] is False:
                feature['evidence_refs']=sorted(set(feature['evidence_refs']+join['source_refs']))
                feature['history_identity_qualification']=current[str(runner['runner_id'])]['history_identity_status']
        runner['candidate_evidence_sha256']=_hash(runner['evidence_features'])
    numerical=materialize_candidate(compiled,registry_path,mapping_path)
    with localcontext() as ctx:
        ctx.prec=40
        rows,indices=witness.independently_score(independent,source,request,registry,context=context,
            management={'prior_result_count':0,'prior_race_numbers':[],'odds_source_present':False})
    actual={str(x['runner_id']):x for x in numerical['runners']};old={(x['runner_id'],x['component']):x for x in baseline['component_witness']}
    for row in rows:
        feature=actual[row['runner_id']]['evidence_features'][row['component']]
        row['comparison']='MATCH' if (abs(Decimal(str(feature['score']))-Decimal(str(row['witness_score'])))<=witness.EPSILON
            and feature['missing']==row['missing'] and abs(Decimal(str(feature['coverage']))-Decimal(str(row['coverage'])))<=witness.EPSILON
            and feature['rule_id']==row['rule_id']) else 'MISMATCH'
        row['baseline_missing']=old[(row['runner_id'],row['component'])]['missing']
        row['history_native_id']=joins.get(row['runner_id'],{}).get('observed_native_id')
        row['derived_document_sha256']=document_sha
    for row in indices:
        value=actual[row['runner_id']]['canonical_components'][row['index']]['value']
        row['comparison']='MATCH' if abs(Decimal(str(value))-Decimal(str(row['witness_value'])))<=witness.EPSILON else 'MISMATCH'
    arithmetic29=verify_29(numerical,registry,mapping)
    identity=baseline['parsed']['race_identity'];packet={'profile':OBSERVATION_PROFILE,'venue_canon':CANON,'classification':MODEL_CLASSIFICATION,
        'race_id':request['race_id'],'generated_at':datetime.now(timezone.utc).isoformat(),'source_freeze_at':freeze.isoformat(),
        'source_receipt_sha256':None,'source_snapshot_sha256':document_sha,'raw_card_sha256':document_sha,
        'raw_card_sha256_kind':'DERIVED_DOCUMENT_NOT_PROVIDER_HTTP_RAW',
        'raw_to_normalized_tables_equal':True,'table_equality_basis':'EXACT_EMBEDDED_ORIGINAL_REPLAY_TO_DERIVED_INPUT_DOCUMENT_AND_PACKET',
        'observation_transport_format':'UNSIGNED_IMMUTABLE_DERIVED_JSON_WITH_ORIGINAL_CHILD_HTTP_LINEAGE',
        'source_signature_verification':'NO_CURRENT_SOURCE_SIGNATURE_NOT_CLAIMED',
        'original_current_csv_http_raw_sha256':_sha(current_raw),'official_identity_bridge_sha256':BRIDGE_SHA,
        'prestart_generation':False,'header':{'distance':identity['distance_m'],'surface':identity['surface'],
            'direction':identity['turn'],'scheduled_post_at':identity['scheduled_post_at']},'runners':[],
        'computational_field_semantics':'CSV_LISTED_RUNNERS_NOT_OFFICIAL_ACTIVE_PROOF','formal_context_ready':False,
        'owner_scope_granted':False,'numerical_policy_changed':False,'forward_oos_credit':0}
    for rid,runner in current.items():
        entry=index['entries'].get(joins.get(rid,{}).get('observed_native_id'),{})
        observations=[]
        for original in entry.get('context_observations',[]):
            observations.append({**deepcopy(original),'same_distance':original['distance_m']==identity['distance_m'],
                'source_raw_sha256':document_sha,'source_raw_sha256_kind':'DERIVED_DOCUMENT_NOT_PROVIDER_HTTP_RAW',
                'source_fetched_at':freeze.isoformat(),'source_fetched_at_kind':'ACTUAL_DERIVED_DOCUMENT_AVAILABILITY_NOT_PROVIDER_FETCH',
                'original_provider_sources':deepcopy(entry['provenance']),
                'original_historical_start_rows':deepcopy([start for start in entry['starts'] if date(2000+int(start['date'][:2]),int(start['date'][3:5]),int(start['date'][6:8])).isoformat()==original['event_date'] and start['distance']==original['distance_m']]),
                'official_identity_bridge_sha256':BRIDGE_SHA,'original_current_csv_http_raw_sha256':_sha(current_raw)})
        packet['runners'].append({'runner_id':rid,'name':runner['name'],'historical_fnb_observations':observations,
            'historical_evidence_status':'ACTUAL_NATIVE_ID_LINKED_ARCHIVED_OBSERVATIONS' if observations else 'UNKNOWN',
            'observed_archived_native_id':joins.get(rid,{}).get('observed_native_id'),'current_permanent_id':None})
    packet['counts']={'active_runners':len(current),'historical_fnb_starts':sum(len(r['historical_fnb_observations']) for r in packet['runners']),
        'printed_position_sequences':sum(bool(o['printed_position_sequence']) for r in packet['runners'] for o in r['historical_fnb_observations'])}
    packet['sha256']=_hash(packet)
    receipt={'profile':PROFILE,'classification':CLASSIFICATION,'race_id':request['race_id'],'document_sha256':document_sha,
        'document_available_at':freeze.isoformat(),'original_current_csv_sha256':_sha(current_raw),'official_bridge_sha256':BRIDGE_SHA,
        'independent_bridge_review_sha256':BRIDGE_REVIEW_SHA,'reference_owner_decision_sha256':OWNER_SHA,
        'model_code_sha256':MODEL_SHA,'model_profile_sha256':MODEL_PROFILE_SHA,
        'owner_use_basis':'CURRENT_DIRECT_PRIVATE_RESEARCH_INSTRUCTION_WITH_PINNED_EXISTING_MODEL_USE_RECORD_NO_SOURCE_QUALIFICATION',
        'listed_runner_count':len(current),'history_identity_resolved_count':len(joins),
        'history_horses_with_eligible_starts':sum(bool(j['actual_starts_consumed']) for j in joins.values()),
        'actual_history_starts':sum(j['actual_starts_consumed'] for j in joins.values()),
        'context_observation_rows':packet['counts']['historical_fnb_starts'],
        'context_runners_with_position_evidence':sum(bool(r['historical_fnb_observations']) for r in packet['runners']),
        'component_records':len(rows),'component_matches':sum(r['comparison']=='MATCH' for r in rows),
        'missing_components':sum(r['missing'] for r in rows),'baseline_missing_components':baseline['receipt']['missing_components'],
        'new_nonmissing_components':sum(r['baseline_missing'] and not r['missing'] for r in rows),
        'base_index_records':len(indices),'base_index_matches':sum(r['comparison']=='MATCH' for r in indices),
        'evidence_quality_counts':dict(Counter(r['evidence_quality'] for r in rows)),'arithmetic29':arithmetic29,
        'archive_receipt':index['receipt'],'identity_joins':joins,'current_source_admitted':False,'active_verified':False,
        'qualified_prestart':False,'current_delivery_proven':False,'registered_OOS_increment':0,
        'previous_R12_outputs_modified':False,'numeric_policy_changed':False,'current_permanent_ID_granted':False,
        'actual_history_is_not_aggregate':True,'earlier_composite_hypotheses_consumed':False}
    receipt['sha256']=_hash(receipt);numerical['official_id_derived_reference']=receipt
    if receipt['component_matches']!=len(rows) or receipt['base_index_matches']!=len(indices) or arithmetic29.get('status')!='29_OF_29_RECORDED_FEATURE_ARITHMETIC_PASS':
        raise ValueError('ID_DOCUMENT_INDEPENDENT_ARITHMETIC_HOLD:'+json.dumps({'components':receipt['component_matches'],'bases':receipt['base_index_matches'],'arithmetic29':arithmetic29}))
    return {'document_raw':document_raw,'document_sha256':document_sha,'availability':deepcopy(availability),
        'raw':current_raw,'parsed':baseline['parsed'],'source':source,'request':request,'raw_field':current,'numerical':numerical,
        'receipt':receipt,'component_witness':rows,'base_index_witness':indices,'observation_packet':packet,
        'reference_owner_decision':{'decision_sha256':OWNER_SHA,'classification':'EXISTING_PRIVATE_MODEL_USE_RECORD_NOT_SOURCE_QUALIFICATION',
            'model_code_sha256':MODEL_SHA,'model_profile_sha256':MODEL_PROFILE_SHA},'owner_decision_bytes':owner_raw}

"""Format-honest CSV -> fixed FNB model -> canonical KRS/strict MEC.

The qualified entry retains the existing CSV Profile, rights, changes and
signature gates. The separate preliminary entry consumes already compiled
listed-runner evidence only; it never grants an official Active universe,
prestart prediction, SOURCE admission or Delivery credit. Neither entry
changes a score, model byte, KRS parameter or material-selection policy.
"""
from __future__ import annotations

import base64
import fcntl
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from runtime import local_fnb_research_runtime as common
from runtime.local_fnb_csv_source_admission import (
    consume_with_approved_profile, sha,
)
from runtime.local_fnb_context_static_candidate import (
    OBSERVATION_PROFILE, CLASSIFICATION as MODEL_CLASSIFICATION,
    CANON, build_context, predict,
)
from runtime.local_nar_csv_reference import inspect_zip

PROFILE = 'KM-FNB-CSV-FIXED-MODEL-RESEARCH-RUNTIME-v1-20261103'
PRELIMINARY = 'PRELIMINARY_LISTED_CSV_RESEARCH_NOT_ACTIVE_NOT_SOURCE_NOT_PRESTART_NOT_OOS'


def _clock():
    return datetime.now(timezone.utc)


def observation_packet(parsed, *, raw, generated_at, source_snapshot_sha256,
                       source_receipt_sha256=None, source_freeze_at=None):
    """Replay actual CSV tables; absent individual histories stay UNKNOWN.

    The pinned model calls the transport-neutral table-equality flag
    ``raw_to_normalized_tables_equal``. Here it means exact CSV table replay,
    explicitly identified by ``observation_transport_format``; no HTML card
    or signed SOURCE envelope is synthesized.
    """
    identity = parsed['race_identity']
    replay = inspect_zip(raw, capture=parsed['capture'], race=identity,
        encoding=parsed['encoding_caller_supplied_not_auto_detected'],
        header_mode=parsed['header_mode_caller_supplied_not_verified_by_manual'],
        now=generated_at)
    if replay != parsed or parsed['target_outcome_fields_present']:
        raise common.ResearchHold('CSV_OBSERVATION_RAW_REPLAY_OR_OUTCOME_MISMATCH')
    generated = common._stamp(generated_at)
    fetched = common._stamp(parsed['capture']['captured_at'])
    freeze = common._stamp(source_freeze_at) if source_freeze_at is not None else fetched
    if not fetched <= freeze <= generated:
        raise common.ResearchHold('CSV_OBSERVATION_GENERATION_BEFORE_CAPTURE')
    rows = parsed['runners']
    ids = [str(row['runner_number']) for row in rows]
    if len(ids) < 2 or len(set(ids)) != len(ids):
        raise common.ResearchHold('CSV_OBSERVATION_LISTED_FIELD_INVALID')
    packet = {'profile': OBSERVATION_PROFILE, 'venue_canon': CANON,
        'classification': MODEL_CLASSIFICATION,
        'race_id': 'KM-LOCAL-FNB-' + identity['race_date'].replace('-', '')
            + '-R' + str(identity['race_no']).zfill(2) + '-CSV-RESEARCH',
        'generated_at': generated.isoformat(), 'source_freeze_at': freeze.isoformat(),
        'source_receipt_sha256': source_receipt_sha256,
        'source_snapshot_sha256': source_snapshot_sha256,
        'raw_card_sha256': hashlib.sha256(raw).hexdigest(),
        'raw_to_normalized_tables_equal': True,
        'observation_transport_format': 'ORIGINAL_CSV_ZIP_NOT_HTML',
        'source_signature_verification': ('EXTERNAL_CSV_ADMISSION_VERIFIED'
            if source_receipt_sha256 else 'NOT_PRESENT_NOT_CLAIMED'),
        'prestart_generation': False,
        'header': {'distance': identity['distance_m'], 'surface': identity['surface'],
            'direction': identity['turn'], 'scheduled_post_at': identity['scheduled_post_at']},
        'runners': [{'runner_id': rid, 'name': row['horse_name'],
            'historical_fnb_observations': [], 'historical_evidence_status': 'UNKNOWN'}
            for rid, row in zip(ids, rows)],
        'counts': {'active_runners': len(rows), 'historical_fnb_starts': 0,
            'printed_position_sequences': 0},
        'computational_field_semantics': 'CSV_LISTED_RUNNERS_NOT_OFFICIAL_ACTIVE_PROOF',
        'missing_individual_history_is_not_aggregate_history': True,
        'formal_context_ready': False, 'owner_scope_granted': False,
        'role_or_rank_changed': False, 'numerical_policy_changed': False,
        'forward_oos_credit': 0}
    packet['sha256'] = sha(packet)
    return packet


def _bridge_aliases(numerical):
    """Map existing candidate schema names without changing numerical values."""
    out = deepcopy(numerical)
    for name in ('race_id', 'race_no', 'race_date'):
        value = out[name]
        if name in out['race'] and out['race'][name] != value:
            raise common.ResearchHold('CSV_CANDIDATE_BRIDGE_RACE_CONFLICT')
        out['race'][name] = value
    for target, original in (('numerical_current_state', 'candidate_current_state'),
                             ('numerical_environment', 'candidate_environment')):
        if target not in out:
            if original not in out:
                raise common.ResearchHold('CSV_CANDIDATE_BRIDGE_SCHEMA_MISSING')
            out[target] = deepcopy(out[original])
    return out


def _execute_locked(numerical, parsed, raw, request, *, private_root, engine, params,
             admission=None, owner_decision=None, owner_decision_bytes=None, source_freeze_at=None):
    # A qualified prestart wrapper must recheck the real process clock at each
    # phase. A preliminary wrapper always retains its non-prestart class.
    approved = admission is not None
    stamp = lambda: (common._prestart_clock(request,
        not_before=source_freeze_at or parsed['capture']['captured_at']) if approved else _clock())
    common._pinned(common.REPO/'runtime/local_fnb_context_static_candidate.py', common.MODEL_SHA)
    common._pinned(common.REPO/'profiles/local_fnb_context_static_candidate_v0.1_20261103.json', common.MODEL_PROFILE_SHA)
    common._pinned(engine, common.ENGINE_SHA)
    common._pinned(params, common.MAP_SHA)
    observed = stamp()
    code_paths = tuple(common.REPO/name for name in (
        'runtime/local_fnb_csv_research_runtime.py', 'runtime/local_fnb_semantic_closure.py',
        'runtime/local_krs_bridge_candidate.py', 'runtime/local_fnb_research_runtime.py',
        'runtime/local_fnb_csv_preliminary_numeric.py', 'runtime/local_nar_csv_reference.py',
        'runtime/local_fnb_csv_source_admission.py', 'runtime/local_base63_source_witness.py',
        'runtime/local_nar_evidence_candidate.py', 'runtime/local_fullnumerical_candidate.py',
        'mapping/local_evidence_feature_rule_registry_v0.1_candidate_20260923.json',
        'mapping/local_full_numerical_mapping_v0.1_candidate_20260923.json'))
    code_pins = {str(p.relative_to(common.REPO)): common.digest(p.read_bytes()) for p in code_paths}
    recipe = {'raw_sha256': common.digest(raw), 'parsed_sha256': sha(parsed),
        'numerical_sha256': common.digest(common.encoded(numerical)),
        'request_sha256': sha(request), 'admission': admission, 'code_pins': code_pins,
        'source_freeze_at':source_freeze_at or parsed['capture']['captured_at'],
        'model_code_sha256': common.MODEL_SHA, 'engine_sha256': common.ENGINE_SHA,
        'parameter_map_sha256': common.MAP_SHA,
        'owner_decision_sha256': (owner_decision or {}).get('decision_sha256')}
    folder = common._private_root(Path(private_root)/request['race_id']/sha(recipe))
    final = folder/'csv_research_execution_manifest.json'
    if final.exists():
        saved = common._verify_saved_manifest(final)
        if (saved.get('input_recipe') != recipe or saved.get('profile') != PROFILE
                or saved.get('race_id') != request['race_id']
                or saved.get('classification') != (common.PRESTART_CLASSIFICATION if approved else PRELIMINARY)
                or saved.get('official_active_universe_verified') is not approved
                or saved.get('prestart_computation_claim') is not approved
                or any(saved.get(k) is not False for k in ('computed_no_bet', 'formal_final',
                    'recipient_delivery_proven','actual_purchase'))
                or saved.get('registered_OOS_increment') != 0
                or saved.get('PFS') is not None
                or saved.get('KRS') != json.loads((folder/'krs/research_krs_receipt.json').read_bytes())
                or saved.get('original_strict_MEC') != json.loads((folder/'original_strict_mec.json').read_bytes())):
            raise common.ResearchHold('CSV_SAVED_RECIPE_MISMATCH')
        return {**saved, 'completion_reused': True, 'new_engine_executions_this_call': 0}
    # Lock/claim before an Engine call: a partial run is inspected, not silently
    # re-dispatched. Completion recovery uses only immutable saved originals.
    claim = folder/'execution_claim.json'
    if claim.exists():
        raise common.ResearchHold('CSV_PARTIAL_EXECUTION_REQUIRES_READBACK_NOT_REDISPATCH')
    common._immutable(claim, common.encoded({'recipe': recipe, 'observed_at': observed.isoformat()}))
    common._immutable(folder/'original.zip', raw)
    common._immutable(folder/'parsed_csv.json', common.encoded(parsed))
    common._immutable(folder/'race_request.json', common.encoded(request))
    common._immutable(folder/'numerical/numerical_materialization.json', common.encoded(numerical))
    if owner_decision_bytes is not None:
        common._immutable(folder/'owner_decision_original.json', owner_decision_bytes)
    from runtime.local_fnb_r13_private_numeric_document import render_full_numeric
    numeric_doc = deepcopy(numerical)
    numeric_doc.setdefault('required_indices', numerical['candidate_full_numerical_summary']['required_indices'])
    for row in numeric_doc['runners']:
        row.setdefault('numerical_missing_components', row.get('candidate_missing_components', []))
    document = render_full_numeric(numeric_doc, classification=PRELIMINARY if not approved
        else common.PRESTART_CLASSIFICATION, race_id=request['race_id'])
    common._immutable(folder/'numerical/all_horse_29_index_report.md', (document['body']+'\n').encode())
    packet = observation_packet(parsed, raw=raw, generated_at=stamp().isoformat(),
        source_snapshot_sha256=(numerical.get('candidate_current_state') or {})['source_snapshot_sha256'],
        source_receipt_sha256=(admission or {}).get('source_receipt_sha256'),
        source_freeze_at=source_freeze_at)
    packet['race_id'] = request['race_id']
    computational_ids = {str(row['runner_id']) for row in numerical['runners']}
    packet['runners'] = [row for row in packet['runners'] if row['runner_id'] in computational_ids]
    packet['counts']['active_runners'] = len(packet['runners'])
    packet['sha256'] = sha({k:v for k,v in packet.items() if k != 'sha256'})
    context = build_context(packet, generated_at=stamp().isoformat())
    upstream, bridge = common.build_upstream(_bridge_aliases(numerical),
        numerical_sha256=recipe['numerical_sha256'])
    prediction = predict(context, frozen_at=stamp().isoformat(), upstream_krs_input=upstream)
    for name, value in (('observations.json',packet),('context.json',context),
                         ('existing_hsv_bridge.json',upstream),('hsv_provenance.json',bridge),
                         ('research_prediction.json',prediction)):
        common._immutable(folder/name, common.encoded(value))
    stamp()
    krs = common.execute_krs(prediction['PRE_KRS_input'], engine=engine, params=params,
        destination=folder/'krs')
    common._immutable(folder/'krs/research_krs_receipt.json', common.encoded(krs))
    stamp()
    from runtime.local_fnb_semantic_closure import assess_semantics, execute_strict_mec
    semantics = assess_semantics(prediction, evaluated_at=stamp().isoformat())
    strict = execute_strict_mec(prediction, evaluated_at=stamp().isoformat())
    common._immutable(folder/'semantic_inventory.json', common.encoded(semantics))
    common._immutable(folder/'original_strict_mec.json', common.encoded(strict))
    body = common._render_private_body(folder, prediction, krs, strict, None,
        private_owner_decision=owner_decision, request=request,
        static_original_saved_at=prediction['freeze_at'])
    if not approved:
        prefix = ('# CSV掲載馬の予備研究・正式Active集合未検証\n\n'
            '公式SOURCE入場・正式署名・発走前完全予測・本人Deliveryの成功件数は0です。'
            'モデル内部のactive_runnersは計算に渡したCSV掲載馬であり、当日の確定出走集合ではありません。'
            'CSVにない個別過去走は作成せず、ContextはUNKNOWNを保持します。\n\n')
        body = prefix.encode()+body
    body_receipt = common._immutable(folder/'complete_csv_research_body.md', body)
    if code_pins != {str(p.relative_to(common.REPO)): common.digest(p.read_bytes()) for p in code_paths}:
        raise common.ResearchHold('CSV_RUNTIME_CODE_CHANGED_DURING_EXECUTION')
    completed = stamp()
    result = {'profile':PROFILE, 'classification':common.PRESTART_CLASSIFICATION if approved else PRELIMINARY,
        'race_id':request['race_id'], 'input_recipe':recipe, 'generated_at':completed.isoformat(),
        'listed_runners':[str(row['runner_number']) for row in parsed['runners']],
        'official_active_universe_verified':approved,
        'qualified_csv_source_admission':admission,
        'model_id':prediction['model_id'], 'model_code_sha256':common.MODEL_SHA,
        'index_cells':len(numerical['runners'])*29, 'KRS':krs, 'original_strict_MEC':strict,
        'computed_no_bet':False, 'complete_tickets':strict.get('tickets'),
        'prestart_computation_claim':approved, 'formal_final':False,
        'recipient_delivery_proven':False, 'registered_OOS_increment':0,
        'actual_purchase':False, 'complete_private_body':body_receipt,
        'output_directory':str(folder), 'PFS':None,
        'private_artifacts':[{'path':str(p.relative_to(folder)), 'sha256':common.digest(p.read_bytes())}
            for p in sorted(folder.rglob('*')) if p.is_file()]}
    if approved:
        result.update(prediction_cutoff=request['prediction_cutoff'],
            prestart_computation_completed_at=completed.isoformat())
    common._immutable(final, common.encoded(result))
    if approved:
        try:
            saved_at = stamp()
            common._immutable(folder/'prestart_finalization_receipt.json', common.encoded({
                'status':'PRIVATE_PRESTART_SAVE_READBACK_VERIFIED',
                'manifest_sha256':common.digest(final.read_bytes()),
                'prediction_cutoff':request['prediction_cutoff'],
                'save_readback_verified_at':saved_at.isoformat(),
                'recipient_delivery_proven':False}))
            stamp()
        except common.ResearchHold:
            common._immutable(folder/'prestart_finalization_failure.json',common.encoded({
                'status':'PRIVATE_PRESTART_FINALIZATION_FAILED_NOT_NO_BET',
                'observed_at':_clock().isoformat(),'prediction_cutoff':request['prediction_cutoff'],
                'prestart_delivery_proven':False}))
            raise
    else:
        stamp()
    return {**result, 'completion_reused':False,
        'new_engine_executions_this_call':int(krs['new_engine_execution'])}


def _execute(numerical, parsed, raw, request, **kwargs):
    root = common._private_root(Path(kwargs['private_root'])/request['race_id'])
    lock = root/'.csv_runtime_execution.lock'
    if lock.is_symlink():
        raise common.ResearchHold('PRIVATE_STORE_SYMLINK_FORBIDDEN')
    with lock.open('a') as handle:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return _execute_locked(numerical,parsed,raw,request,**kwargs)


def run_qualified(assessment, request, *, binding, source_receipt, private_root,
                  engine, params, owner_decision_path, owner_decision_sha256):
    """Existing trusted CSV gates remain prerequisites; never issue a signature."""
    admitted = consume_with_approved_profile(assessment, request, binding=binding,
        source_receipt=source_receipt, now=_clock())
    source = admitted['source_candidate']
    decision, decision_raw = common.verify_private_owner_decision(owner_decision_path,
        owner_decision_sha256, request=request, source=source)
    raw = base64.b64decode(source['sources'][0]['raw_b64'], validate=True)
    return _execute(admitted['numerical'], assessment['parsed_reference'], raw, request,
        private_root=private_root,engine=engine,params=params,
        admission=admitted['csv_private_profile_admission'],
        owner_decision=decision,owner_decision_bytes=decision_raw,
        source_freeze_at=source['source_freeze_at'])


def run_preliminary(numerical, parsed, raw, request, *, private_root, engine, params):
    """Explicit independent reference lane; no qualified-Source or Active claim.

    Caller must use the actual CSV preliminary compiler; its immutable source,
    raw-field and numerical witnesses are checked by that compiler. This entry
    independently replays the actual ZIP and binds all numerical inputs.
    """
    if (numerical.get('race_id') != request.get('race_id')
            or numerical.get('race_date') != parsed['race_identity']['race_date']
            or {str(r['runner_id']) for r in numerical['runners']}
               != {str(r['runner_number']) for r in parsed['runners']}):
        raise common.ResearchHold('CSV_PRELIMINARY_IDENTITY_MISMATCH')
    from runtime.local_fnb_csv_preliminary_numeric import materialize_preliminary
    replay = materialize_preliminary(raw, capture=parsed['capture'], race=parsed['race_identity'],
        encoding=parsed['encoding_caller_supplied_not_auto_detected'],
        header_mode=parsed['header_mode_caller_supplied_not_verified_by_manual'], now=_clock())
    if (replay['parsed'] != parsed or replay['numerical'] != numerical or replay['request'] != request
            or replay['receipt']['component_matches'] != replay['receipt']['component_records']
            or replay['receipt']['base_index_matches'] != replay['receipt']['base_index_records']
            or replay['receipt']['arithmetic29']['status'] != '29_OF_29_RECORDED_FEATURE_ARITHMETIC_PASS'):
        raise common.ResearchHold('CSV_PRELIMINARY_RECOMPUTATION_OR_WITNESS_MISMATCH')
    return _execute(numerical,parsed,raw,request,private_root=private_root,
        engine=engine,params=params)


def main(argv=None):
    """Explicit preliminary CLI; qualified entry is trusted private Python only."""
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('raw', 'capture', 'race', 'private-root', 'engine', 'params'):
        ap.add_argument('--'+name, required=True, type=Path)
    args = ap.parse_args(argv)
    from runtime.local_fnb_csv_preliminary_numeric import materialize_preliminary
    raw = args.raw.read_bytes()
    capture = json.loads(args.capture.read_bytes())
    race = json.loads(args.race.read_bytes())
    compiled = materialize_preliminary(raw,capture=capture,race=race,now=_clock())
    result = run_preliminary(compiled['numerical'],compiled['parsed'],raw,compiled['request'],
        private_root=args.private_root,engine=args.engine,params=args.params)
    keys = ('profile','classification','race_id','index_cells','completion_reused',
        'new_engine_executions_this_call','formal_final','recipient_delivery_proven',
        'prestart_computation_claim','output_directory')
    print(json.dumps({k:result[k] for k in keys},ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

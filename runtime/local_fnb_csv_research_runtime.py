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
DERIVED_REFERENCE = 'PRIVATE_UNSIGNED_DERIVED_REFERENCE_NOT_SOURCE_NOT_ACTIVE_NOT_PRESTART_NOT_OOS'


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


def _source_original(value, supplied_bytes, label):
    """Retain caller bytes exactly, or identify a serialized mapping honestly."""
    if not isinstance(value,dict):
        raise common.ResearchHold('CSV_QUALIFIED_SOURCE_ORIGINAL_MAPPING_REQUIRED')
    if supplied_bytes is None:
        raw = common.encoded(value)
        basis = 'CANONICAL_ENCODING_OF_SUPPLIED_MAPPING_NOT_TRANSPORT_BODY'
    else:
        if not isinstance(supplied_bytes,bytes):
            raise common.ResearchHold('CSV_QUALIFIED_SOURCE_ORIGINAL_BYTES_REQUIRED')
        try:
            decoded = json.loads(supplied_bytes)
        except (ValueError,UnicodeDecodeError) as error:
            raise common.ResearchHold('CSV_QUALIFIED_SOURCE_ORIGINAL_JSON_INVALID') from error
        if decoded != value:
            raise common.ResearchHold('CSV_QUALIFIED_SOURCE_ORIGINAL_MAPPING_BYTES_MISMATCH')
        raw = supplied_bytes
        basis = 'EXACT_SUPPLIED_JSON_BYTES'
    return {'raw':raw,'provenance':{'sha256':common.digest(raw),'bytes':len(raw),
        'representation':basis,'original_kind':label,
        'signature_or_source_qualification_issued_here':False}}


def _save_source_originals(folder, originals):
    """SOURCE originals share the immutable inventory/readback of every output."""
    metadata = {}
    for name in ('csv_source_assessment.json','csv_source_receipt_envelope.json'):
        original = originals.get(name) if isinstance(originals,dict) else None
        if (not isinstance(original,dict) or not isinstance(original.get('raw'),bytes)
                or original.get('provenance',{}).get('sha256') != common.digest(original['raw'])
                or original.get('provenance',{}).get('bytes') != len(original['raw'])):
            raise common.ResearchHold('CSV_QUALIFIED_SOURCE_ORIGINALS_REQUIRED_OR_CHANGED')
        saved = common._immutable(folder/name,original['raw'])
        metadata[name] = {**original['provenance'],'saved_sha256':saved['sha256']}
    common._immutable(folder/'qualified_source_originals_provenance.json',common.encoded(metadata))
    return metadata


def _qualified_identity(numerical, admission, originals):
    """Separate revalidation trace time from the same frozen execution inputs.

    All signed capture/raw/freeze/Active/rights/Profile facts remain in the
    identity. Only named wrapper trace fields and their aggregate assessment
    hash pointer are excluded; exact original bytes still enter the saved
    inventory and numerical provenance.
    """
    assessment = json.loads(originals['csv_source_assessment.json']['raw'])
    receipt = json.loads(originals['csv_source_receipt_envelope.json']['raw'])
    assessment_identity = deepcopy(assessment)
    for key in ('sha256','assessed_at','verified_at','actual_generated_at'):
        assessment_identity.pop(key,None)
    numeric_identity = deepcopy(numerical)
    consumer = numeric_identity.get('csv_research_consumer') or {}
    consumer.pop('actual_generated_at',None)
    consumer.pop('assessment_sha256',None)
    admission_identity = deepcopy(admission)
    for key in ('verified_at','assessed_at'):
        admission_identity.pop(key,None)
    return {'numerical_content_sha256':sha(numeric_identity),
        'assessment_content_sha256':sha(assessment_identity),
        'source_receipt_canonical_sha256':sha(receipt),
        'admission':admission_identity}


def _execute_locked(numerical, parsed, raw, request, *, private_root, engine, params,
             admission=None, owner_decision=None, owner_decision_bytes=None, source_freeze_at=None,
             qualified_source_originals=None,derived_document_path=None,derived_document_sha256=None,
             provider_reference=None, expected_engine_projection_sha256=None,
             require_reference_publication_cutoff=False):
    # A qualified prestart wrapper must recheck the real process clock at each
    # phase. A preliminary wrapper always retains its non-prestart class.
    approved = admission is not None
    if provider_reference is not None:
        if approved or derived_document_path is not None:
            raise common.ResearchHold('PROVIDER_REFERENCE_CANNOT_GRANT_SOURCE_ADMISSION')
        from runtime.local_fnb_rakuten_reference import materialize_reference
        replay=materialize_reference(raw,capture=provider_reference['capture'],race=provider_reference['race'],
            generated_at=provider_reference['generated_at'],
            active_runner_ids=provider_reference.get('active_runner_ids'))
        if any(replay[k] != v for k,v in (('numerical',numerical),('parsed',parsed),('request',request))):
            raise common.ResearchHold('PROVIDER_REFERENCE_ORIGINAL_REPLAY_MISMATCH')
    derived = None
    if derived_document_path is not None or derived_document_sha256 is not None:
        if approved or derived_document_path is None or derived_document_sha256 is None:
            raise common.ResearchHold('DERIVED_REFERENCE_NOT_QUALIFIED_SOURCE_AND_PIN_REQUIRED')
        common._pinned(derived_document_path,derived_document_sha256)
        from runtime.local_fnb_id_linked_race_reference import load_document
        derived = load_document(derived_document_path,now=_clock())
        if (derived['document_sha256'] != derived_document_sha256
                or derived['numerical'] != numerical or derived['parsed'] != parsed
                or derived['raw'] != raw or derived['request'] != request):
            raise common.ResearchHold('DERIVED_REFERENCE_REPLAY_INPUT_MISMATCH')
        source_freeze_at = derived['availability']['available_at']
    classification = (common.PRESTART_CLASSIFICATION if approved else
        'PRIVATE_PROVIDER_REFERENCE_NOT_QUALIFIED_SOURCE_NOT_ACTIVE_NOT_OOS' if provider_reference else
        DERIVED_REFERENCE if derived else PRELIMINARY)
    stamp = lambda: (common._prestart_clock(request,
        not_before=source_freeze_at or parsed['capture']['captured_at'])
        if approved or require_reference_publication_cutoff else _clock())
    common._pinned(common.REPO/'runtime/local_fnb_context_static_candidate.py', common.MODEL_SHA)
    common._pinned(common.REPO/'profiles/local_fnb_context_static_candidate_v0.1_20261103.json', common.MODEL_PROFILE_SHA)
    common._pinned(engine, common.ENGINE_SHA)
    common._pinned(params, common.MAP_SHA)
    observed = stamp()
    code_paths = tuple(common.REPO/name for name in (
        'runtime/local_fnb_csv_research_runtime.py', 'runtime/local_fnb_semantic_closure.py',
        'runtime/local_fnb_csv_postresult.py', 'runtime/capital_policy.py',
        'runtime/local_fnb_r13_private_numeric_document.py',
        'runtime/local_fnb_r17_method_constructor.py', 'runtime/jra_ticket_tree_renderer.py',
        'runtime/minimum_efficient_coverage.py',
        'profiles/family_user_capital_default_20261003_R1.json',
        'runtime/local_krs_bridge_candidate.py', 'runtime/local_fnb_research_runtime.py',
        'runtime/local_fnb_csv_preliminary_numeric.py', 'runtime/local_nar_csv_reference.py',
        'runtime/local_fnb_csv_source_admission.py', 'runtime/local_base63_source_witness.py',
        'runtime/local_nar_evidence_candidate.py', 'runtime/local_fullnumerical_candidate.py',
        'mapping/local_evidence_feature_rule_registry_v0.1_candidate_20260923.json',
        'mapping/local_full_numerical_mapping_v0.1_candidate_20260923.json'))
    code_pins = {str(p.relative_to(common.REPO)): common.digest(p.read_bytes()) for p in code_paths}
    if derived:
        extra_paths = ('runtime/local_fnb_id_linked_race_reference.py','runtime/local_fnb_id_history_reference.py')
        code_paths += tuple(common.REPO/name for name in extra_paths)
        code_pins.update({name:common.digest((common.REPO/name).read_bytes()) for name in extra_paths})
    if provider_reference:
        extra_paths=('runtime/local_fnb_rakuten_reference.py','runtime/local_fnb_multisource.py')
        code_paths+=tuple(common.REPO/name for name in extra_paths)
        code_pins.update({name:common.digest((common.REPO/name).read_bytes()) for name in extra_paths})
    numerical_original_sha256 = common.digest(common.encoded(numerical))
    recipe = {'raw_sha256': common.digest(raw), 'parsed_sha256': sha(parsed),
        'numerical_sha256':numerical_original_sha256,
        'request_sha256': sha(request), 'admission': admission, 'code_pins': code_pins,
        'source_freeze_at':source_freeze_at or parsed['capture']['captured_at'],
        'model_code_sha256': common.MODEL_SHA, 'engine_sha256': common.ENGINE_SHA,
        'parameter_map_sha256': common.MAP_SHA,
        'owner_decision_sha256': (owner_decision or {}).get('decision_sha256')}
    if expected_engine_projection_sha256 is not None:
        recipe['expected_engine_projection_sha256'] = expected_engine_projection_sha256
    if require_reference_publication_cutoff:
        recipe['require_reference_publication_cutoff'] = True
    if approved:
        if not isinstance(qualified_source_originals,dict):
            raise common.ResearchHold('CSV_QUALIFIED_SOURCE_ORIGINALS_REQUIRED_OR_CHANGED')
        identity = _qualified_identity(numerical,admission,qualified_source_originals)
        # Keep actual original hashes in the immutable manifest/inventory, not
        # as a reason to rerun identical KRS after a new verification timestamp.
        recipe.pop('numerical_sha256')
        recipe['admission'] = identity.pop('admission')
        recipe['qualified_input_identity'] = identity
    if derived:
        recipe.update(derived_document_sha256=derived_document_sha256,
            derived_availability=deepcopy(derived['availability']),
            reference_owner_decision=deepcopy(derived['reference_owner_decision']))
    if provider_reference:
        recipe['provider_reference_input']={k:deepcopy(v) for k,v in provider_reference.items()
            if k not in ('observation_packet','generated_at')}
        recipe['provider_reference_input'].get('private_owner_decision',{}).pop('verified_at',None)
    folder = common._private_root(Path(private_root)/request['race_id']/sha(recipe))
    final = folder/'csv_research_execution_manifest.json'
    if final.exists():
        saved = common._verify_saved_manifest(final)
        if (saved.get('input_recipe') != recipe or saved.get('profile') != PROFILE
                or saved.get('race_id') != request['race_id']
                or saved.get('classification') != classification
                or saved.get('official_active_universe_verified') is not approved
                or saved.get('prestart_computation_claim') is not approved
                or any(saved.get(k) is not False for k in ('formal_final',
                    'recipient_delivery_proven','actual_purchase'))
                or saved.get('registered_OOS_increment') != 0
                or saved.get('PFS') is not None
                or saved.get('KRS') != json.loads((folder/'krs/research_krs_receipt.json').read_bytes())
                or saved.get('original_strict_MEC') != json.loads((folder/'original_strict_mec.json').read_bytes())):
            raise common.ResearchHold('CSV_SAVED_RECIPE_MISMATCH')
        exports = saved.get('postresult_method_exports',{}).get('methods',{})
        expected_no_bet = len(exports)==3 and all(v.get('status')=='COMPUTED_NO_BET' for v in exports.values())
        if saved.get('computed_no_bet') is not expected_no_bet:
            raise common.ResearchHold('CSV_SAVED_METHOD_TERMINAL_MISMATCH')
        return {**saved, 'completion_reused': True, 'new_engine_executions_this_call': 0}
    # Lock/claim before an Engine call: a partial run is inspected, not silently
    # re-dispatched. Completion recovery uses only immutable saved originals.
    claim = folder/'execution_claim.json'
    if claim.exists():
        raise common.ResearchHold('CSV_PARTIAL_EXECUTION_REQUIRES_READBACK_NOT_REDISPATCH')
    common._immutable(claim, common.encoded({'recipe': recipe, 'observed_at': observed.isoformat()}))
    common._immutable(folder/('original_provider_card.html' if provider_reference else 'original.zip'), raw)
    common._immutable(folder/('parsed_provider_card.json' if provider_reference else 'parsed_csv.json'), common.encoded(parsed))
    if provider_reference:
        common._immutable(folder/'provider_reference_capture_and_scope.json',common.encoded(recipe['provider_reference_input']))
    if approved:
        _save_source_originals(folder,qualified_source_originals)
    if derived:
        common._immutable(folder/'derived_reference_document.json',derived['document_raw'])
        common._immutable(folder/'derived_reference_availability.json',common.encoded(derived['availability']))
        common._immutable(folder/'reference_owner_decision_original.json',derived['owner_decision_bytes'])
    common._immutable(folder/'race_request.json', common.encoded(request))
    common._immutable(folder/'numerical/numerical_materialization.json', common.encoded(numerical))
    if owner_decision_bytes is not None:
        common._immutable(folder/'owner_decision_original.json', owner_decision_bytes)
    from runtime.local_fnb_r13_private_numeric_document import render_full_numeric
    numeric_doc = deepcopy(numerical)
    numeric_doc.setdefault('required_indices', numerical['candidate_full_numerical_summary']['required_indices'])
    for row in numeric_doc['runners']:
        row.setdefault('numerical_missing_components', row.get('candidate_missing_components', []))
    numeric_render_options={'source_description':'楽天競馬の掲載原文（正式SOURCE未入場）'} if provider_reference else {}
    document = render_full_numeric(numeric_doc, classification=classification, race_id=request['race_id'],**numeric_render_options)
    common._immutable(folder/'numerical/all_horse_29_index_report.md', (document['body']+'\n').encode())
    packet = (deepcopy(provider_reference['observation_packet']) if provider_reference else
        deepcopy(derived['observation_packet']) if derived else observation_packet(parsed, raw=raw, generated_at=stamp().isoformat(),
        source_snapshot_sha256=(numerical.get('candidate_current_state') or {})['source_snapshot_sha256'],
        source_receipt_sha256=(admission or {}).get('source_receipt_sha256'),
        source_freeze_at=source_freeze_at))
    packet['race_id'] = request['race_id']
    computational_ids = {str(row['runner_id']) for row in numerical['runners']}
    packet['runners'] = [row for row in packet['runners'] if row['runner_id'] in computational_ids]
    packet['counts']['active_runners'] = len(packet['runners'])
    packet['sha256'] = sha({k:v for k,v in packet.items() if k != 'sha256'})
    context = build_context(packet, generated_at=stamp().isoformat())
    upstream, bridge = common.build_upstream(_bridge_aliases(numerical),
        numerical_sha256=numerical_original_sha256)
    prediction = predict(context, frozen_at=stamp().isoformat(), upstream_krs_input=upstream)
    for name, value in (('observations.json',packet),('context.json',context),
                         ('existing_hsv_bridge.json',upstream),('hsv_provenance.json',bridge),
                         ('research_prediction.json',prediction)):
        common._immutable(folder/name, common.encoded(value))
    stamp()
    if (expected_engine_projection_sha256 is not None
            and common.digest(common.encoded(common.engine_input_projection(prediction['PRE_KRS_input'])))
                != expected_engine_projection_sha256):
        raise common.ResearchHold('PINNED_ENGINE_INPUT_PROJECTION_MISMATCH_BEFORE_EXECUTION')
    krs = common.execute_krs(prediction['PRE_KRS_input'], engine=engine, params=params,
        destination=folder/'krs')
    common._immutable(folder/'krs/research_krs_receipt.json', common.encoded(krs))
    stamp()
    from runtime.local_fnb_semantic_closure import assess_semantics, execute_strict_mec
    semantics = assess_semantics(prediction, evaluated_at=stamp().isoformat())
    strict = execute_strict_mec(prediction, evaluated_at=stamp().isoformat())
    common._immutable(folder/'semantic_inventory.json', common.encoded(semantics))
    common._immutable(folder/'original_strict_mec.json', common.encoded(strict))
    if approved:
        from runtime.local_fnb_csv_postresult import export_strict_methods
        method_exports = export_strict_methods(folder=folder,request=request,prediction=prediction,
            strict=strict,krs=krs,clock=stamp,execution_recipe_sha256=sha(recipe))
        common._immutable(folder/'strict_method_capital_exports.json',common.encoded(method_exports))
    else:
        method_exports = {'status':'PRELIMINARY_NOT_ELIGIBLE_FOR_PRESTART_EXPORT','methods':{}}
    reference_active = provider_reference and provider_reference.get('active_runner_ids') is not None
    body = common._render_private_body(folder, prediction, krs, strict, None,
        private_owner_decision=owner_decision, request=request,
        static_original_saved_at=prediction['freeze_at'],
        computational_field_label='照合済みREFERENCE Active' if reference_active else
            '掲載馬' if provider_reference else 'Active')
    if not approved:
        prefix = (('# 代替Providerの私有研究・REFERENCE Active照合済み\n\n' if reference_active else
            '# 代替Provider掲載馬の私有研究・Active集合とSOURCE資格未検証\n\n' if provider_reference else
            '# CSV掲載馬の予備研究・正式Active集合未検証\n\n')
            +'公式SOURCE入場・正式署名・発走前完全予測・本人Deliveryの成功件数は0です。'
            +('モデル内部のactive_runnersには当日変更原本で照合したREFERENCEの集合を使用しました。'
              if reference_active else
              'モデル内部のactive_runnersは計算に渡した掲載馬であり、当日の確定出走集合ではありません。')
            +('個別過去走は派生文書内の実在原本とID接続を再解析して使用し、欠測部分はUNKNOWNを保持します。\n\n'
              if derived else 'Provider原文の同一馬行の個別過去走を再解析し、未観測のContextはUNKNOWNを保持します。\n\n'
              if provider_reference else 'CSVにない個別過去走は作成せず、ContextはUNKNOWNを保持します。\n\n'))
        body = prefix.encode()+body
        if provider_reference:
            body+=('\n## 代替Provider原本・時刻・Revision\n\n```json\n'+common.encoded({
                'classification':classification,'race_id':request['race_id'],
                'scheduled_post_at':request['scheduled_post_at'],'prediction_cutoff':request['prediction_cutoff'],
                'source_freeze_at':prediction['source_freeze_at'],'static_freeze_at':prediction['freeze_at'],
                'provider_capture':provider_reference['capture'],
                'private_owner_decision':provider_reference['private_owner_decision'],
                'active_verified':bool(reference_active),'qualified_source':False,
                'received_or_delivered_before_cutoff_proven':False}).decode()+'```\n').encode()
    elif method_exports['methods']:
        body += ('\n## 券種別の厳格MEC・Capital確定原本（独立代替案）\n\n'+
            '\n'.join('### '+method+'\n\n```json\n'+common.encoded(detail).decode().rstrip()+
                '\n```\n\n```text\n'+detail.get('canonical_tree','PAPER／選択券面なし')+'\n```\n'
                for method,detail in method_exports['methods'].items())).encode()
    body_receipt = common._immutable(folder/'complete_csv_research_body.md', body)
    if code_pins != {str(p.relative_to(common.REPO)): common.digest(p.read_bytes()) for p in code_paths}:
        raise common.ResearchHold('CSV_RUNTIME_CODE_CHANGED_DURING_EXECUTION')
    completed = stamp()
    terminals = method_exports['methods']
    selection_complete = len(terminals)==3 and all(v.get('status') in ('SELECTED_FROZEN','COMPUTED_NO_BET')
                                                  for v in terminals.values())
    computed_no_bet = selection_complete and all(v['status']=='COMPUTED_NO_BET' for v in terminals.values())
    result = {'profile':PROFILE, 'classification':classification,
        'race_id':request['race_id'], 'input_recipe':recipe, 'generated_at':completed.isoformat(),
        'listed_runners':[str(row['runner_number']) for row in parsed['runners']],
        'official_active_universe_verified':approved,
        'qualified_csv_source_admission':admission,
        'model_id':prediction['model_id'], 'model_code_sha256':common.MODEL_SHA,
        'numerical_original_sha256':numerical_original_sha256,
        'index_cells':len(numerical['runners'])*29, 'KRS':krs, 'original_strict_MEC':strict,
        'computed_no_bet':computed_no_bet,
        'complete_tickets':{method:detail['tickets'] for method,detail in terminals.items()} if selection_complete else None,
        'strict_mec_pre_capital_tickets':strict.get('tickets'),'selection_complete':selection_complete,
        'postresult_method_exports':method_exports,
        'prestart_computation_claim':approved, 'formal_final':False,
        'recipient_delivery_proven':False, 'registered_OOS_increment':0,
        'actual_purchase':False, 'complete_private_body':body_receipt,
        'output_directory':str(folder), 'PFS':None,
        'private_artifacts':[{'path':str(p.relative_to(folder)), 'sha256':common.digest(p.read_bytes())}
            for p in sorted(folder.rglob('*')) if p.is_file()]}
    if derived:
        result.update(derived_document_sha256=derived_document_sha256,
            reference_owner_decision=deepcopy(derived['reference_owner_decision']),
            source_freeze_at=source_freeze_at,derived_reference_is_not_source_qualification=True)
    if approved:
        result.update(prediction_cutoff=request['prediction_cutoff'],
            prestart_computation_completed_at=completed.isoformat(),
            qualified_source_originals={name:deepcopy(value['provenance'])
                for name,value in qualified_source_originals.items()})
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
                  engine, params, owner_decision_path, owner_decision_sha256,
                  assessment_original_bytes=None, source_receipt_original_bytes=None):
    """Existing trusted CSV gates remain prerequisites; never issue a signature."""
    admitted = consume_with_approved_profile(assessment, request, binding=binding,
        source_receipt=source_receipt, now=_clock())
    source = admitted['source_candidate']
    decision, decision_raw = common.verify_private_owner_decision(owner_decision_path,
        owner_decision_sha256, request=request, source=source)
    raw = base64.b64decode(source['sources'][0]['raw_b64'], validate=True)
    originals = {
        'csv_source_assessment.json':_source_original(assessment,assessment_original_bytes,'CSV_ASSESSMENT'),
        'csv_source_receipt_envelope.json':_source_original(source_receipt,source_receipt_original_bytes,
            'EXTERNAL_SOURCE_RECEIPT_AS_VERIFIED_BY_BOUND_GATE')}
    return _execute(admitted['numerical'], assessment['parsed_reference'], raw, request,
        private_root=private_root,engine=engine,params=params,
        admission=admitted['csv_private_profile_admission'],
        owner_decision=decision,owner_decision_bytes=decision_raw,
        source_freeze_at=source['source_freeze_at'],qualified_source_originals=originals)


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


def run_derived_document(path, pin, *, private_root,engine,params):
    """Explicit private derived-reference entry; never a SOURCE/Profile grant."""
    common._pinned(path,pin)
    from runtime.local_fnb_id_linked_race_reference import load_document
    loaded = load_document(path,now=_clock())
    return _execute(loaded['numerical'],loaded['parsed'],loaded['raw'],loaded['request'],
        private_root=private_root,engine=engine,params=params,
        derived_document_path=path,derived_document_sha256=pin)


def run_provider_reference(raw, *, capture,race,private_root,engine,params,
                           owner_decision_path,owner_decision_sha256,
                           expected_engine_projection_sha256=None,
                           require_reference_publication_cutoff=False,current_state_evidence=None):
    """Execute an actual alternative card through the existing fixed pipeline.

    Only the existing numerical rules and private Owner decision are used.
    Separately verified changes can constrain the REFERENCE Active set.
    """
    from runtime.local_fnb_rakuten_reference import (materialize_reference, parse_card,
        verify_reference_current_state)
    active_ids=None
    observed=_clock()
    if current_state_evidence is not None:
        state_envelope,original=current_state_evidence
        parsed=parse_card(raw,capture=capture,race=race,now=observed)
        state,active_ids,active_sha=verify_reference_current_state(
            parsed,state_envelope,original,request=race,now=observed)
    loaded=materialize_reference(raw,capture=capture,race=race,generated_at=observed,active_runner_ids=active_ids)
    owner,owner_bytes=common.verify_private_owner_decision(owner_decision_path,owner_decision_sha256,
        request=loaded['request'],source=loaded['source'],check_prestart=False)
    reference={'provider':'RAKUTEN_KEIBA','capture':deepcopy(capture),'race':deepcopy(race),
        'generated_at':loaded['generated_at'],'observation_packet':loaded['observation_packet'],
        'private_owner_decision':owner,'qualified_source':False,'active_verified':active_ids is not None}
    if active_ids is not None:
        reference.update(active_runner_ids=active_ids,active_universe_sha256=active_sha,
                         current_state_original_sha256=state['original_sha256'])
    return _execute(loaded['numerical'],loaded['parsed'],raw,loaded['request'],
        private_root=private_root,engine=engine,params=params,
        owner_decision_bytes=owner_bytes,source_freeze_at=loaded['parsed']['captured_at'],
        provider_reference=reference,expected_engine_projection_sha256=expected_engine_projection_sha256,
        require_reference_publication_cutoff=require_reference_publication_cutoff)


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

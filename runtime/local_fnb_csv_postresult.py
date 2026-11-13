"""Offered NAR CSV result adapter and same-original private settlement.

Parsing publishes no SOURCE signature or RESULT admission. Settlement requires
an existing verifier for the frozen ticket original and another for the actual
result/refund evidence. Missing predictions remain uncalculated, never NO-BET.
No acquisition, model changes, automatic promotion or messages occur here.
"""
from __future__ import annotations

import csv
from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import io
import json
from pathlib import Path
import re
import zipfile

from runtime.local_nar_csv_reference import SCHEMAS, inspect_zip, _dt
from runtime import local_fnb_research_runtime as private

PROFILE = 'KM-FNB-OFFERED-CSV-POSTRESULT-v1'
METHODS = {
    'EXACTA':('馬単',('組番1','組番2')),
    'TRIO':('３連複',('組番馬番1','組番馬番2','組番馬番3')),
    'TRIFECTA':('３連単',('組番馬番1','組番馬番2','組番馬番3')),
}
FROZEN_PROFILE = 'KM-FNB-PRIVATE-STRICT-METHOD-FROZEN-v1'


def sha(value):
    return hashlib.sha256(private.encoded(value)).hexdigest()


def _selection(method, values):
    count = 2 if method == 'EXACTA' else 3
    if (method not in METHODS or len(values) != count
            or any(not str(v).isdigit() or not 1 <= int(v) <= 20 for v in values)):
        raise ValueError('CSV_RESULT_SELECTION_INVALID')
    out = tuple(int(v) for v in values)
    if len(set(out)) != count:
        raise ValueError('CSV_RESULT_DUPLICATE_SELECTION_RUNNER')
    return tuple(sorted(out)) if method == 'TRIO' else out


def export_strict_methods(*, folder, request, prediction, strict, krs, clock,
                          execution_recipe_sha256):
    """Resolve existing Capital for strict selected leaves and freeze each alternative.

    Only the qualified runtime calls this seam. Unformed strict MEC returns a
    HOLD without files; PAPER decisions are retained but cannot be settled as a
    selected prestart method. No model proposals or UNKNOWN paths are adopted.
    """
    if (strict.get('status')!='CANONICAL_MEC_EXECUTED_NOT_FORMAL_QUALIFICATION'
            or strict.get('all_hold_causes') or strict.get('strict_mec_executed') is not True):
        return {'status':'STRICT_SELECTION_HOLD_NO_FROZEN_EXPORT','methods':{},'computed_no_bet':False}
    from runtime.minimum_efficient_coverage import validate_mec_plan
    from runtime.capital_policy import resolve_capital_policy
    from runtime.jra_ticket_tree_renderer import render_ticket_tree
    from runtime.local_fnb_r17_method_constructor import sha as method_sha
    plan = strict.get('canonical_mec_plan')
    if (not isinstance(plan,dict) or validate_mec_plan(plan).get('mec_verified') is not True
            or strict.get('tickets')!=plan.get('tickets')
            or strict.get('race_id')!=request['race_id']
            or prediction.get('race_id')!=request['race_id']
            or krs.get('run_count')!=5000 or krs.get('seed')!=1
            or krs.get('engine_sha256')!=private.ENGINE_SHA
            or krs.get('parameter_map_sha256')!=private.MAP_SHA):
        raise ValueError('CSV_FROZEN_STRICT_MEC_OR_CANONICAL_KRS_UNVERIFIED')
    folder = private._private_root(folder)
    originals = {}
    for name in ('original.zip','csv_source_assessment.json','csv_source_receipt_envelope.json',
                 'owner_decision_original.json','race_request.json','research_prediction.json',
                 'original_strict_mec.json','numerical/numerical_materialization.json',
                 'krs/research_krs_receipt.json','krs/execution_output.json'):
        path = folder/name
        if not path.is_file() or path.is_symlink():
            raise ValueError('CSV_FROZEN_QUALIFIED_INPUT_ORIGINAL_MISSING')
        data = path.read_bytes()
        originals[name] = {'path':str(path),'sha256':private.digest(data)}
    methods = {}
    for method in METHODS:
        selected = [deepcopy(t) for t in plan['tickets'] if t['bet_type']==method]
        required = sum(t['stake'] for t in selected)
        view = {**plan,'minimum_required_capital':required,'material_coverage_ratio':None,
            'sha256':method_sha({'race_id':request['race_id'],'owner':prediction['model_id'],
                                'method':method,'tickets':selected})}
        capital = resolve_capital_policy(strict['canonical_mec_request'],view)
        if type(capital.get('capital_limit')) is not int:
            raise ValueError('CSV_FROZEN_EXISTING_HARD_METHOD_BUDGET_REQUIRED')
        if capital.get('paper_only') is True:
            methods[method] = {'status':'PAPER_NOT_PRESTART_SELECTED','capital':capital}
            continue
        no_bet = not selected or capital.get('no_bet') is True
        tickets = [] if no_bet else selected
        reason = ('FROZEN_COMMON_MEC_HAS_NO_'+method+'_SELECTION' if not selected
                  else capital.get('reason')) if no_bet else None
        total = sum(t['stake'] for t in tickets)
        tree = render_ticket_tree({'final_ticket':{'tickets':tickets,'no_bet':no_bet},
                                  'capital_policy_decision':{'decision':'RECOMMENDATION_ONLY'}})['text']
        freeze = private._stamp(clock())
        if (not private._stamp(prediction['freeze_at']) <= freeze
                < private._stamp(request['prediction_cutoff']) < private._stamp(request['scheduled_post_at'])):
            raise ValueError('CSV_FROZEN_METHOD_AFTER_CUTOFF_OR_BEFORE_STATIC')
        frozen = {'profile':FROZEN_PROFILE,'classification':private.PRESTART_CLASSIFICATION,
            **{key:request[key] for key in ('race_id','venue_id','race_date','race_no',
                'prediction_cutoff','scheduled_post_at')},'method':method,'freeze_at':freeze.isoformat(),
            'owner_model_id':prediction['model_id'],'model_code_sha256':prediction['model_code_sha256'],
            'source_snapshot_sha256':prediction['source_snapshot_sha256'],
            'execution_recipe_sha256':execution_recipe_sha256,
            'parent_execution_manifest':str(folder/'csv_research_execution_manifest.json'),
            'originals':originals,'selection_complete':True,'computed_no_bet':no_bet,'no_bet_reason':reason,
            'canonical_mec_sha256':plan['sha256'],'capital_policy_decision':capital,
            'final_prediction_package':{'roles':deepcopy(prediction['roles'])},
            'final_ticket':{'tickets':tickets,'total_investment':total},
            'required_method_mec_capital':required,'capital_limit':capital['capital_limit'],
            'unused_capital':capital['capital_limit']-total,'canonical_tree':tree,
            'formal_final':False,'actual_purchase':False,'registered_OOS_increment':0}
        original = private._immutable(folder/'postresult'/f'{method}_frozen_ticket_original.json',private.encoded(frozen))
        if private._stamp(clock()) >= private._stamp(request['prediction_cutoff']):
            raise ValueError('CSV_FROZEN_METHOD_SAVE_AFTER_CUTOFF')
        methods[method] = {'status':'COMPUTED_NO_BET' if no_bet else 'SELECTED_FROZEN',
            'frozen_original':original,'capital':capital,'canonical_tree':tree,'tickets':tickets,
            'point_count':len(tickets),'total_investment':total,'unused_capital':frozen['unused_capital']}
    return {'status':'PRIVATE_STRICT_METHOD_CAPITAL_TERMINALS','methods':methods,
            'independent_alternatives_not_combined_purchase':True,'formal_final':False}


def verify_exported_frozen(*, original_bytes, sha256, candidate, now):
    """Re-read the completed qualified runtime and every frozen input original."""
    if private.digest(original_bytes)!=sha256:return False
    frozen = json.loads(original_bytes)
    if frozen.get('profile')!=FROZEN_PROFILE:return False
    parent = Path(frozen['parent_execution_manifest'])
    saved = private._verify_saved_manifest(parent)
    method = frozen['method']
    descriptor = saved.get('postresult_method_exports',{}).get('methods',{}).get(method,{}).get('frozen_original',{})
    if (saved.get('classification')!=private.PRESTART_CLASSIFICATION
            or saved.get('race_id')!=frozen['race_id'] or descriptor.get('sha256')!=sha256
            or saved.get('input_recipe',{}).get('model_code_sha256')!=frozen['model_code_sha256']
            or saved.get('qualified_csv_source_admission') is None
            or private._stamp(frozen['freeze_at'])>=private._stamp(saved['prediction_cutoff'])):
        return False
    if Path(descriptor['path']).read_bytes()!=original_bytes:return False
    root = parent.parent.resolve()
    for original in frozen['originals'].values():
        path = Path(original['path'])
        if root not in path.resolve().parents:return False
        private._pinned(path,original['sha256'])
    return True


def parse_result(raw, *, capture, race, now=None, encoding='utf-8-sig', header_mode='present'):
    now = now or datetime.now(timezone.utc)
    parsed = inspect_zip(raw,capture=capture,race=race,encoding=encoding,header_mode=header_mode,now=now)
    if _dt(capture['captured_at']) < _dt(parsed['race_identity']['scheduled_post_at']):
        raise ValueError('CSV_RESULT_CAPTURE_BEFORE_OFFICIAL_POST')
    key = ('船橋',race['race_date'].replace('-',''),str(race['race_no']))
    paybacks = []
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names = [name for name in archive.namelist() if name.endswith('_payback.csv')]
        if len(names) != 1:
            raise ValueError('CSV_RESULT_PAYBACK_TABLE_NOT_AVAILABLE')
        rows = csv.reader(io.StringIO(archive.read(names[0]).decode(encoding),newline=''),strict=True)
        if header_mode == 'present':next(rows)
        for number,row in enumerate(rows,2 if header_mode=='present' else 1):
            record = dict(zip(SCHEMAS['payback'],row))
            if (record['競馬場'],record['競走年月日'],record['レース番号']) == key:
                paybacks.append((number,record))
    groups, outcomes = {}, []
    for runner in parsed['runners']:
        finish = str(runner['outcome_fields_separated']['着順']).strip()
        no = runner['runner_number']
        outcomes.append({'runner_id':no,'finish_cell':finish,
            'field_provenance':runner['field_provenance']['着順']})
        if re.fullmatch('[1-9][0-9]*',finish):
            groups.setdefault(int(finish),[]).append(no)
    payouts = {method:{} for method in METHODS}
    payout_evidence = []
    for row_number,row in paybacks:
        for method,(prefix,parts) in METHODS.items():
            fields = [prefix+part for part in parts]+[prefix+'払戻金（円）']
            cells = [row[field].strip() for field in fields]
            if not any(cells):continue
            if not all(cells):raise ValueError('CSV_RESULT_PARTIAL_PUBLISHED_PAYOUT')
            selection = _selection(method,cells[:-1])
            amount = cells[-1]
            if not amount.isdigit() or int(amount) <= 0:
                raise ValueError('CSV_RESULT_PAYOUT_NOT_POSITIVE_INTEGER')
            label = '>'.join(map(str,selection))
            old = payouts[method].get(label)
            if old is not None and old != int(amount):
                raise ValueError('CSV_RESULT_CONFLICTING_PUBLISHED_PAYOUT')
            payouts[method][label] = int(amount)
            payout_evidence.append({'method':method,'selection':list(selection),
                'payout_per_100':int(amount),'table':names[0],'csv_row':row_number,
                'csv_columns':[SCHEMAS['payback'].index(field)+1 for field in fields],
                'zip_raw_sha256':capture['raw_sha256']})
    unique_top3 = [groups[rank][0] for rank in (1,2,3)] if all(len(groups.get(rank,[]))==1 for rank in (1,2,3)) else None
    result = {'profile':PROFILE,'classification':'OFFICIAL_CSV_RESULT_CANDIDATE_NOT_ADMITTED_NOT_SIGNED',
        'race_identity':parsed['race_identity'],'source_raw_sha256':capture['raw_sha256'],
        'capture':deepcopy(capture),'finish_groups':[
            {'finish':rank,'runners':sorted(numbers)} for rank,numbers in sorted(groups.items())],
        'runner_outcomes':outcomes,'unique_top3':unique_top3,
        'payouts_per_100':payouts,'payout_field_evidence':payout_evidence,
        'result_fields_present':bool(groups and payout_evidence),
        'official_result_admission_verified':False,'refund_completeness_verified':False,
        'frozen_prediction_joined':False,'PFS':None,'registered_OOS_increment':0,'actual_purchase':False}
    result['sha256'] = sha(result)
    return result


def settle_frozen(candidate, frozen_original, *, expected_sha256, verify_frozen,
                  verify_result, private_root, now=None):
    """Use actual pinned bytes plus independently supplied existing verifiers.

    The result verifier must confirm all payout lists and refund identities.
    That qualification is never inferred from an empty CSV cell or absence of
    cancellation text. The frozen verifier binds the exact original bytes to
    already selected, complete prestart tickets; it cannot supply new tickets.
    """
    now = now or datetime.now(timezone.utc)
    if (candidate.get('profile') != PROFILE or candidate.get('sha256') !=
            sha({k:v for k,v in candidate.items() if k!='sha256'})):
        raise ValueError('CSV_RESULT_CANDIDATE_HASH_MISMATCH')
    if frozen_original is None:
        return {'profile':PROFILE,'status':'UNCOMPUTED_NO_FROZEN_PREDICTION','PFS':None,
                'computed_no_bet':False,'registered_OOS_increment':0,'actual_purchase':False}
    if not callable(verify_frozen) or not callable(verify_result):
        raise ValueError('CSV_RESULT_EXISTING_INDEPENDENT_VERIFIERS_REQUIRED')
    path = Path(frozen_original).absolute()
    raw = private._pinned(path,expected_sha256)
    frozen = json.loads(raw)
    identity = candidate['race_identity']
    if (frozen.get('classification') != private.PRESTART_CLASSIFICATION
            or any(frozen.get(k) != identity[k] for k in ('venue_id','race_date','race_no'))
            or not private._stamp(frozen['freeze_at']) < private._stamp(frozen['prediction_cutoff'])
                < private._stamp(frozen['scheduled_post_at'])
            or private._stamp(frozen['scheduled_post_at']) != private._stamp(identity['scheduled_post_at'])
            or private._stamp(frozen['scheduled_post_at']) > private._stamp(now)):
        raise ValueError('CSV_RESULT_FROZEN_IDENTITY_OR_PRESTART_TIME_MISMATCH')
    if verify_frozen(original_bytes=raw,sha256=expected_sha256,candidate=deepcopy(candidate),now=now) is not True:
        raise ValueError('CSV_RESULT_FROZEN_ORIGINAL_NOT_VERIFIED')
    qualification = verify_result(candidate=deepcopy(candidate),frozen=deepcopy(frozen),now=now)
    if (not isinstance(qualification,dict) or qualification.get('result_sha256')!=candidate['sha256']
            or qualification.get('published_payouts_complete') is not True
            or qualification.get('refund_completeness_verified') is not True
            or not isinstance(qualification.get('refunded_runner_ids'),list)
            or any(type(v) is not int or not 1<=v<=20 for v in qualification['refunded_runner_ids'])
            or candidate.get('result_fields_present') is not True
            or not re.fullmatch('[a-f0-9]{64}',str(qualification.get('evidence_original_sha256')))):
        raise ValueError('CSV_RESULT_PAYOUT_OR_REFUND_QUALIFICATION_MISSING')
    tickets = frozen.get('final_ticket',{}).get('tickets')
    method = frozen.get('method')
    computed_no_bet = (tickets == [] and frozen.get('computed_no_bet') is True
        and frozen.get('final_ticket',{}).get('total_investment') == 0
        and isinstance(frozen.get('no_bet_reason'),str) and bool(frozen['no_bet_reason'].strip()))
    if (method not in METHODS or not isinstance(tickets,list) or not tickets and not computed_no_bet
            or frozen.get('selection_complete') is not True
            or any(ticket.get('bet_type') != method for ticket in tickets)):
        raise ValueError('CSV_RESULT_UNCOMPUTED_OR_INCOMPLETE_TICKETS_NOT_NO_BET')
    refunds = set(map(int,qualification['refunded_runner_ids']))
    # A cancelled runner may be absent from the result CSV. Only the separately
    # verified refund universe may extend its listed runners for settlement.
    runners = {row['runner_id'] for row in candidate['runner_outcomes']} | refunds
    result_rows, total, returned, refunded, seen = [],0,0,0,set()
    for ticket in tickets:
        method = ticket['bet_type']
        selection = _selection(method,ticket['selection'])
        if not set(selection) <= runners:
            raise ValueError('CSV_RESULT_FROZEN_RUNNER_NOT_IN_RESULT_UNIVERSE')
        stake = ticket['stake']
        if type(stake) is not int or stake<=0 or stake%100 or (method,selection) in seen:
            raise ValueError('CSV_RESULT_FROZEN_STAKE_OR_DUPLICATE_TICKET')
        seen.add((method,selection));total += stake
        refund = stake if refunds.intersection(selection) else 0
        payout = candidate['payouts_per_100'][method].get('>'.join(map(str,selection)),0)
        value = 0 if refund else payout*(stake//100)
        returned += value;refunded += refund
        result_rows.append({**ticket,'payout_per_100':payout,'return':value,'refund':refund})
    if frozen['final_ticket'].get('total_investment') != total:
        raise ValueError('CSV_RESULT_FROZEN_TOTAL_INVESTMENT_MISMATCH')
    effective = total-refunded
    settlement = {'status':('COMPLETE_PRIVATE_COMPUTED_NO_BET_RESULT_LINKED' if computed_no_bet
        else 'COMPLETE_PRIVATE_FROZEN_RESEARCH_SETTLEMENT'),
        'computed_no_bet':computed_no_bet,'method':method,'investment':total,
        'return':returned,'refund':refunded,'effective_investment':effective,
        'profit_loss':returned+refunded-total,
        'PFS':str(Decimal(returned)*100/Decimal(effective)) if effective else None,
        'ticket_results':result_rows,'frozen_original_sha256':expected_sha256,
        'result_candidate_sha256':candidate['sha256'],'qualification':qualification,
        'formal_result_signature_issued':False,'registered_OOS_increment':0,'actual_purchase':False}
    root = private._private_root(private_root)/sha(settlement)
    private._private_root(root)
    private._immutable(root/'frozen_ticket_original.json',raw)
    private._immutable(root/'result_candidate.json',private.encoded(candidate))
    receipt = private._immutable(root/'settlement.json',private.encoded(settlement))
    return {**settlement,'private_original':receipt}

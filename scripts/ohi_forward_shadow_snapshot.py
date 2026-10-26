"""Freeze outcome-free OHI diagnostics beside immutable private predictions.

No acquisition, model/Engine execution, ticket selection, result evaluation,
formal activation or OOS registration occurs here. A/B remain unimplemented.
"""
from __future__ import annotations
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'scripts'), str(ROOT/'runtime')]
from runtime import ohi_single_race_research as research
from ohi_readonly_portfolio_diagnostics import diagnose

SCHEMA = 'OHI-FORWARD-READONLY-SHADOW-CONTRACT-v1-20261027'
SNAPSHOT_SCHEMA = 'OHI-FORWARD-READONLY-SHADOW-SNAPSHOT-v1-20261027'
CODE_REF = 'd61f5c563238be2c812ef4bf912bd5b872b84fed'
SOURCE_PROFILE = 'OHI-NANKAN-PRIVATE-SINGLE-SCOPED-CHANGES-MARKET-v2-20261026'
OWNERS = ('BASELINE', 'OHI_FIXED_CANDIDATE')
CODE_PATHS = (
    'scripts/ohi_forward_shadow_snapshot.py',
    'scripts/ohi_readonly_portfolio_diagnostics.py',
    'runtime/ohi_single_race_research.py',
    'runtime/ohi_nankan_private_source_v2.py',
)
PREDICTION_PATHS = (
    'runtime/ohi_nankan_private_source.py', 'runtime/ohi_single_race_research.py',
    'runtime/urw_nankan_reference_source.py', 'runtime/urw_reference_source_policy.py',
    'runtime/local_fullnumerical_production.py', 'runtime/local_nar_evidence_candidate.py',
    'runtime/local_fullnumerical_candidate.py', 'runtime/local_krs_bridge_candidate.py',
    'runtime/local_race_key_shadow_owner.py', 'runtime/minimum_efficient_coverage.py',
    'runtime/capital_policy.py',
    'mapping/local_evidence_feature_rule_registry_v0.1_candidate_20260923.json',
    'mapping/local_full_numerical_mapping_v0.1_candidate_20260923.json',
    'profiles/ohi_single_race_nonproduction_20261026.json',
    'profiles/family_user_capital_default_20261003_R1.json',
    'runtime/ohi_nankan_private_source_v2.py',
    'profiles/ohi_single_race_source_v2_20261026.json',
)
CAPITAL_PATH = 'profiles/family_user_capital_default_20261003_R1.json'
CAPITAL_TRANSPORT_HASHES = [
    '7a4b0f960b72b5f60834ebc1e02de63fbb47aa40424c6214f347677ffe4ceaaa',
    'd8be84bf7bddc494519217ca062df28769a41874a3edf58d78415cf1ac847ad5',
]


def sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def stamp(value):
    clock = datetime.fromisoformat(value) if isinstance(value, str) else value
    if not isinstance(clock, datetime) or clock.tzinfo is None or clock.utcoffset() is None:
        raise ValueError('FORWARD_UTC_AWARE_TIME_REQUIRED')
    return clock.astimezone(timezone.utc)


def seal(value): return {**value, 'sha256':sha(value)}
def load(path): return json.loads(Path(path).read_text())


def definition():
    dependency_hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in PREDICTION_PATHS}
    if dependency_hashes[CAPITAL_PATH] not in CAPITAL_TRANSPORT_HASHES:
        raise ValueError('FORWARD_LOCAL_CAPITAL_TRANSPORT_UNKNOWN')
    # The two byte variants have already been independently verified as the
    # same JSON policy. Normalize only this path, before contract comparison.
    dependency_hashes[CAPITAL_PATH]=CAPITAL_TRANSPORT_HASHES[1]
    return {
        'schema': SCHEMA, 'venue_id':'OHI',
        'target_dates':['2026-10-27','2026-10-28','2026-10-29','2026-10-30'],
        'target_race_numbers':list(range(1,13)),
        'first_acceptance_priority':'R1',
        'fallback':'NEXT_OFFICIAL_ELIGIBLE_RACE_ONLY_WITH_EARLIER_INELIGIBILITY_RECORDED',
        'priority_enforcement':'EXISTING_CALLER_RESPONSIBILITY_NOT_ENFORCED_BY_SNAPSHOT',
        'prediction_code_ref':CODE_REF,
        'prediction_classification':research.CLASS, 'source_profile':SOURCE_PROFILE,
        'model_sha256':research.MODEL, 'engine_sha256':research.ENGINE,
        'parameters_sha256':research.PARAM, 'krs_runs_per_owner':5000, 'krs_seed':1,
        'owners':list(OWNERS), 'owner_cap_yen':10000, 'stake_unit_yen':100,
        'source_max_age_seconds':600, 'cutoff_basis':'EXISTING_POST_MINUS_300_SECONDS',
        'shadow_code_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in CODE_PATHS},
        'prediction_dependency_sha256':dependency_hashes,
        'allowed_dependency_transports':{CAPITAL_PATH:{
            'accepted_sha256':CAPITAL_TRANSPORT_HASHES,
            'basis':'PREVIOUSLY_VERIFIED_JSON_IDENTICAL_SINGLE_TRAILING_LF_TRANSPORT_ONLY',
            'other_path_compatibility':False}},
        'A':{'implemented':False,'classification':'INSUFFICIENT_EVIDENCE','method':'EVIDENCE_AUDIT_ONLY_NO_NEW_WINNER_MODEL'},
        'B':{'implemented':False,'classification':'INSUFFICIENT_EVIDENCE','method':'EVIDENCE_AUDIT_ONLY_NO_CAUSAL_LABEL'},
        'C':{'implemented':True,'method':'EXISTING_CONDITIONAL_MODEL_MASS_AUDIT',
             'purchase_consumption':False,'calibration':'UNPROVEN'},
        'D':{'implemented':True,'method':'ALL_EXISTING_MEC_AND_CONDITIONAL_MASS_PREFIXES',
             'chosen_prefix':None,'purchase_policy':False,'same_cap_not_equal_actual_spend':True},
        'outcome_input_allowed':False, 'registered_oos_credit':0,
        'production_authority':False, 'real_purchase':False, 'signed_final':False,
        'evaluation':{'result_before_snapshot':False,'missing_not_zero':True,
             'same_source_and_freeze_required':True,'owners_separate_accounts':True,
             'no_best_prefix_selection':True,'ordered_third_tie_not_applicable':True,
             'future_results_required_for_performance':True,
             'metrics':['WINNER_TOP1','W_CAPTURE','P2_CAPTURE','P3_CAPTURE',
                        'ORDERED_PAIR','PAIR_CONDITIONED_THIRD','TOP3_SET',
                        'CORRECT_TICKET_LOSS','FALSE_ADDED_TICKETS','SELECTED_TICKET_COUNT',
                        'NO_BET','PAPER_PFS','PROFIT_LOSS','HIT_BUT_LOSS','MAX_DRAWDOWN'],
             'equal_actual_spend_comparison':'ONLY_WHEN_FROZEN_PORTFOLIOS_ACTUALLY_HAVE_EQUAL_STAKE',
             'oct26_cohort_not_forward_credit':True},
    }


def make_contract(*, now=None):
    clock = stamp(now or datetime.now(timezone.utc))
    return seal({**definition(),'frozen_at':clock.isoformat(),
                 'contract_creation_transport_evidence':{
                     CAPITAL_PATH:hashlib.sha256((ROOT/CAPITAL_PATH).read_bytes()).hexdigest()},
                 'status':'PREREGISTERED_RESEARCH_EVALUATION_NOT_PREDICTION_NOT_REGISTERED_OOS'})


def verify_contract(contract, now):
    if contract.get('sha256') != sha({k:v for k,v in contract.items() if k!='sha256'}):
        raise ValueError('FORWARD_CONTRACT_SELF_HASH')
    expected = definition()
    if any(contract.get(k)!=v for k,v in expected.items()):
        raise ValueError('FORWARD_CONTRACT_DEFINITION_OR_CODE_CHANGED')
    transport=contract.get('contract_creation_transport_evidence')
    if (not isinstance(transport,dict) or set(transport)!={CAPITAL_PATH}
            or transport[CAPITAL_PATH] not in CAPITAL_TRANSPORT_HASHES):
        raise ValueError('FORWARD_CONTRACT_TRANSPORT_EVIDENCE')
    if stamp(contract['frozen_at']) > now:
        raise ValueError('FORWARD_CONTRACT_FUTURE_TIME')


def capture_snapshot(original_dir, contract, *, now=None, source_dir=None):
    """Read a genuine prestart original; outcome data are never accepted."""
    clock = stamp(now or datetime.now(timezone.utc))
    verify_contract(contract, clock)
    folder = research.private_root(original_dir)
    original, body = research.readback(folder)
    race = original['race'];cutoff = stamp(race['prediction_cutoff'])
    frozen = stamp(original['freeze_at'])
    if (race['venue_id']!='OHI' or race['race_date'] not in contract['target_dates']
            or type(race['race_no']) is not int or race['race_no'] not in contract['target_race_numbers']
            or not re.fullmatch(race['race_date'].replace('-','')+r'20\d{4}'+f"{race['race_no']:02d}",race['provider_race_id'])):
        raise ValueError('FORWARD_TARGET_RACE_SCOPE')
    if not stamp(contract['frozen_at']) < frozen <= clock < cutoff:
        raise ValueError('FORWARD_CONTRACT_FREEZE_CUTOFF_ORDER')
    if (original.get('classification')!=research.CLASS or original.get('production_authority') is not False
            or original.get('registered_oos_credit')!=0 or original.get('signed_final') is not False
            or original.get('actual_purchase') is not False or original.get('formal_source') is not False):
        raise ValueError('FORWARD_ORIGINAL_CLASSIFICATION_OR_AUTHORITY')
    observation = load(folder/'observation.json')
    if (observation.get('sha256')!=original['source_sha256']
            or observation.get('source_profile')!=SOURCE_PROFILE or observation.get('race')!=race):
        raise ValueError('FORWARD_SOURCE_BINDING')
    source = research.private_root(source_dir or folder.with_name(folder.name+'.source'))
    research.verify_observation(observation, source)
    # Reuse the operating checker, plus the injected boundary clock used by
    # independent tests. A caller cannot relax the actual operating check.
    source_clock = research.check_source_time(observation,'FORWARD_SHADOW_SNAPSHOT')
    times = [stamp(r['fetched_at']) for r in observation['receipts']]
    if not times or any(t>clock or (clock-t).total_seconds()>=600 for t in times):
        raise ValueError('FORWARD_SOURCE_AGE')
    manifest = load(folder/'execution-manifest.json')
    if (manifest.get('sha256')!=sha({k:v for k,v in manifest.items() if k!='sha256'})
            or manifest['sha256']!=original['execution_manifest_sha256']
            or manifest.get('source_sha256')!=original['source_sha256']
            or any(manifest.get(k)!=contract[k] for k in ('model_sha256','engine_sha256','parameters_sha256'))):
        raise ValueError('FORWARD_EXECUTION_ASSET_BINDING')
    dependencies=manifest.get('dependency_sha256')
    if not isinstance(dependencies,dict) or not dependencies or any(
            not isinstance(v,str) or not re.fullmatch('[a-f0-9]{64}',v) for v in dependencies.values()):
        raise ValueError('FORWARD_PREDICTION_CODE_SHAS_REQUIRED')
    expected=contract['prediction_dependency_sha256']
    if set(dependencies)!=set(expected):
        raise ValueError('FORWARD_PREDICTION_DEPENDENCY_KEYS_CHANGED')
    if any(value!=expected[p] and not (p==CAPITAL_PATH and value in CAPITAL_TRANSPORT_HASHES)
           for p,value in dependencies.items()):
        raise ValueError('FORWARD_PREDICTION_DEPENDENCY_CODE_CHANGED')
    n=original['numerical_summary']
    if (n['required_count']!=len(original['all_runners'])*29 or n['unresolved_count']!=0
            or n['terminalized_count']!=n['required_count']):
        raise ValueError('FORWARD_29_TERMINAL_REQUIRED')
    if set(original['owners'])!=set(OWNERS) or set(original['portfolios'])!=set(OWNERS):
        raise ValueError('FORWARD_OWNERS_REQUIRED')
    for owner in OWNERS:
        receipt=original['krs'][owner]['receipt']
        krs_input=load(folder/owner/'input.json')
        if (receipt.get('sha256')!=sha({k:v for k,v in receipt.items() if k!='sha256'})
                or any(receipt.get(k)!=v for k,v in
                    {'engine_sha256':research.ENGINE,'parameter_map_sha256':research.PARAM,
                     'runs':5000,'seed':1,'actual_engine_executed':True}.items())
                or receipt.get('output_sha256')!=sha(original['krs'][owner]['output'])):
            raise ValueError('FORWARD_KRS_RECEIPT_BINDING')
        if receipt.get('input_sha256')!=sha(krs_input):
            raise ValueError('FORWARD_KRS_INPUT_BINDING')
        p=original['portfolios'][owner]
        if p['capital']['capital_limit']!=10000 or any(type(t['stake']) is not int or t['stake']!=100 for t in p['tickets']):
            raise ValueError('FORWARD_CAP_OR_STAKE_CHANGED')
    diagnostic=diagnose(original,load(folder/'features.json'),None)
    selected={o:copy.deepcopy(original['portfolios'][o]['tickets']) for o in OWNERS}
    return seal({
        'schema':SNAPSHOT_SCHEMA,'classification':'PRESTART_READONLY_FORWARD_SHADOW_NOT_REGISTERED_OOS',
        'snapshot_at':clock.isoformat(),'contract_sha256':contract['sha256'],
        'contract_frozen_at':contract['frozen_at'],'race':copy.deepcopy(race),
        'original_prediction_sha256':original['sha256'],'original_freeze_at':original['freeze_at'],
        'original_source_sha256':original['source_sha256'],
        'execution_manifest_sha256':manifest['sha256'],'prediction_dependency_sha256':dependencies,
        'original_body_sha256':hashlib.sha256(body.encode()).hexdigest(),
        'source_time_check':source_clock,'diagnostic':diagnostic,
        'selected_frozen_tickets':selected,'selected_ticket_sha256':{o:sha(t) for o,t in selected.items()},
        'unchanged_role_columns':{o:copy.deepcopy(original['owners'][o].get('role_columns') or original['owners'][o]['roles']) for o in OWNERS},
        'outcome_received':False,'performance_evaluated':False,'registered_oos_credit':0,
        'production_authority':False,'actual_purchase':False,'signed_final':False,
        'private_remote_readback':False,'screen_display_verified':False,'owner_ack':False,
    })


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--freeze-contract',action='store_true');p.add_argument('--contract',required=True)
    p.add_argument('--original');p.add_argument('--source-dir');p.add_argument('--output')
    a=p.parse_args()
    contract_path=research.private_root(a.contract)
    if a.freeze_contract:
        if a.original or a.output or a.source_dir:p.error('contract freeze does not accept original/output/source')
        value=make_contract();research.write(contract_path,value)
    else:
        if not a.original or not a.output:p.error('snapshot requires original and new output')
        target=research.private_root(a.output)
        if target.exists():raise ValueError('FORWARD_SNAPSHOT_ALREADY_EXISTS')
        value=capture_snapshot(a.original,load(contract_path),source_dir=a.source_dir)
        research.write(target,value)
    print(json.dumps({'schema':value['schema'],'sha256':value['sha256'],
                      'performance_evaluated':False,'registered_oos_credit':0}))

if __name__=='__main__':main()

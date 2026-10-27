"""Execution diagnostics for existing JRA result lanes; never admission evidence."""
from __future__ import annotations

import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import urllib.error


def failure_row(race_id, exc, stage, **references):
    code = str(getattr(exc, 'error_code', None) or str(exc)).split(':', 1)[0][:300]
    detail = str(exc)[:1000]
    probe = (code + ' ' + detail).upper()
    if isinstance(exc, json.JSONDecodeError) or any(x in probe for x in ('HASH', 'SHA256', 'SIGNATURE', 'UNIVERSE', 'MISMATCH',
                                'IMMUTAB', 'CONFLICT', 'INTEGRITY', 'IDENTITY')):
        status = 'BLOCKED_RESULT_INTEGRITY'
    elif any(x in probe for x in ('CUTOFF', 'PROSPECTIVE', 'WITNESS', 'TIMEZONE', 'TEMPORAL')):
        status = 'BLOCKED_TEMPORAL'
    elif (isinstance(exc, (urllib.error.URLError, TimeoutError, ConnectionError)) or
          any(x in probe for x in ('SOURCE', 'CALENDAR', 'ENTRY_TOKEN', 'DAY_TOKEN',
                                  'RACE_TOKEN', 'ARCHIVE', 'NAVIGATION', 'HTTP', 'RESULT_DETAIL_TABLE'))):
        status = 'BLOCKED_SOURCE'
    else:
        status = 'FAILURE_INTERNAL'
    row = dict(references, race_id=race_id, status=status,
               first_failed_stage=getattr(exc, 'first_failed_stage', None) or stage,
               exception_class=type(exc).__name__, error_code=code, error=detail,
               persisted=False, recommendation_pfs=None,
               actual_purchase='UNVERIFIED', actual_purchase_pfs=None)
    for name in ('official_request', 'source_fault', 'diagnostic', 'official_navigation'):
        value = getattr(exc, name, None)
        if isinstance(value, (dict,list)):
            row[name] = _public_diagnostic(value)
    if isinstance(getattr(exc,'code',None),int) or getattr(exc,'official_request',None):
        sys.path.insert(0,str(Path(__file__).resolve().parent/'jra_source_runtime'))
        from jra_race_day_resolver import official_navigation_failure
        row['source_fault']=official_navigation_failure(exc,stage=row['first_failed_stage'])
    return row


def _public_diagnostic(value):
    if isinstance(value,list):return [_public_diagnostic(x) for x in value]
    if not isinstance(value,dict):return value
    result={}
    for key,item in value.items():
        if key.lower() in ('authorization','cookie','set-cookie','password','private_key','secret'):
            continue
        if key in ('headers','response_headers') and isinstance(item,dict):
            result[key]={k:v for k,v in item.items() if k.lower() in
                ('date','content-type','retry-after','server','location')}
        else:result[key]=_public_diagnostic(item)
    return result


def _category(row):
    status = str(row.get('status') or '')
    if status.startswith('BLOCKED:'):
        return failure_row(row.get('race_id'), ValueError(status),
                           row.get('first_failed_stage', 'PROCESS_RESULT'))['status']
    if status.startswith(('BLOCKED', 'FAILURE')):
        return status.split(':', 1)[0]
    if status.startswith('PENDING'):
        return 'PENDING_OFFICIAL_RESULT'
    if status=='NOT_RUN_BUDGET':
        return status
    if status in ('SETTLED', 'SETTLED_RECOMMENDATION'):
        return 'SETTLED'
    if status == 'RESULT_REQUEST_WRITTEN':
        return 'RESULT_REQUEST_WRITTEN'
    if status.startswith('ALREADY_'):
        return 'ALREADY_PROCESSED'
    return 'NOT_DUE_OR_NOT_ELIGIBLE'


def build_execution_health(lane, rows, *, observed_at=None):
    counts = {}
    for row in rows:
        category = _category(row)
        counts[category] = counts.get(category, 0) + 1
    blocked = sum(v for k, v in counts.items() if k.startswith(('BLOCKED', 'FAILURE')))
    if blocked:
        categories = [k for k in counts if k.startswith(('BLOCKED', 'FAILURE'))]
        health = ('PARTIAL_BLOCKED' if blocked != len(rows) else
                  categories[0] if len(categories) == 1 else 'PARTIAL_BLOCKED')
    elif counts.get('NOT_RUN_BUDGET'):
        health='NOT_RUN_BUDGET' if counts['NOT_RUN_BUDGET']==len(rows) else 'PARTIAL_BUDGET'
    elif counts.get('PENDING_OFFICIAL_RESULT'):
        health = 'PENDING_OFFICIAL_RESULT'
    elif counts.get('SETTLED'):
        health = 'SUCCESS_SETTLED'
    elif counts.get('RESULT_REQUEST_WRITTEN'):
        health = 'SUCCESS_RESULT_REQUESTS_WRITTEN'
    elif counts.get('ALREADY_PROCESSED'):
        health = 'SUCCESS_NO_NEW_SETTLEMENT'
    else:
        health = 'SUCCESS_NO_DUE_RACES'
    return {'lane': lane, 'generated_at': observed_at or datetime.now(timezone.utc).isoformat(),
            'execution_health': health, 'counts': counts,
            'material_failure_count': blocked, 'processed': rows,
            'signed_result_receipt_verified_by_health': False,
            'actual_purchase': 'UNVERIFIED', 'actual_purchase_pfs': None,
            'evidence_scope': 'EXECUTION_DIAGNOSTIC_NOT_RESULT_OR_OOS_ADMISSION'}


def health_exit_code(report):
    return 2 if report.get('material_failure_count', 0) else 0


def _semantic(report):
    report = copy.deepcopy(report)
    report.pop('generated_at', None)
    for row in report.get('processed', []):
        # Only observation metadata of failures is volatile. Signed/frozen,
        # effective-time and SHA bindings must remain material at every level.
        if not str(row.get('status', '')).startswith(('BLOCKED', 'FAILURE', 'PENDING')):
            continue
        for field in ('first_observed_at', 'last_observed_at', 'observed_at', 'status_updated_at'):
            row.pop(field, None)
        def observation(value):
            if isinstance(value,list):return [observation(x) for x in value]
            if not isinstance(value,dict):return value
            result={k:observation(v) for k,v in value.items() if k not in
                ('fetched_at','observed_at','attempt','first_observed_at','last_observed_at')}
            for name in ('headers','response_headers'):
                if isinstance(result.get(name),dict):
                    result[name]={k:v for k,v in result[name].items() if k.lower()!='date'}
            return result
        for field in ('source_fault', 'diagnostic', 'official_request','official_navigation'):
            diagnostic = row.get(field)
            if not isinstance(diagnostic, (dict,list)):
                continue
            row[field]=observation(diagnostic)
    return report


def write_execution_health(path, report):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        previous = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        previous = None
    if isinstance(previous, dict) and _semantic(previous) == _semantic(report):
        return previous
    # Reuse PR344's semantic-clock writer rather than inventing a second
    # persistence/commit mechanism. Only diagnostics are passed to this API.
    sys.path.insert(0, str(Path(__file__).resolve().parent / 'jra_source_runtime'))
    from jra_race_day_autopilot import _write_status_json
    return _write_status_json(path, report)


def aggregate_execution_health(files, exits, *, bvi_report=None, step_outcomes=None):
    """Finish existing lanes before reflecting their material failures in CI."""
    rows=[]
    for lane,path in files.items():
        try:
            report=json.loads(Path(path).read_text())
            items=report['processed']
            if not isinstance(items,list) or any(not isinstance(x,dict) for x in items):
                raise ValueError('EXECUTION_HEALTH_ROWS_INVALID')
            rows.extend(dict(x,lane=lane) for x in items)
            if exits.get(lane) not in ('0',0):
                if not any(_category(x).startswith(('BLOCKED','FAILURE')) for x in items):
                    raise RuntimeError('LANE_EXIT_WITHOUT_RECORDED_FAILURE:'+str(exits.get(lane)))
        except Exception as exc:
            rows.append(failure_row('LANE:'+lane,exc,'READ_LANE_EXECUTION_HEALTH',lane=lane))
    if bvi_report:
        try:
            if exits.get('bvi') not in ('0',0):
                raise RuntimeError('BVI_LANE_EXIT:'+str(exits.get('bvi')))
            bvi=json.loads(Path(bvi_report).read_text())
            failures=bvi['race_failures']
            if not isinstance(failures,list):raise ValueError('BVI_EXECUTION_FAILURES_INVALID')
            for failure in failures:
                rows.append(failure_row(failure['race_id'],ValueError(failure['reason']),
                    'BVI_ENV_SETTLEMENT',lane='BVI_ENV'))
            if not failures:
                rows.append({'race_id':'BVI_ENV','lane':'BVI_ENV',
                    'status':'PENDING_FORWARD_OOS' if not bvi.get('eligible_settled_races') else 'ALREADY_PROCESSED',
                    'eligible_settled_races':bvi.get('eligible_settled_races'),
                    'environment_candidate':bvi.get('environment_candidate'),
                    'new_oos_credit_from_execution_health':0,'persisted':False})
        except Exception as exc:
            row=failure_row('LANE:BVI_ENV',exc,'BVI_ENV_SETTLEMENT' if exits.get('bvi') not in ('0',0)
                else 'READ_BVI_EXECUTION_HEALTH',lane='BVI_ENV')
            row['upstream_stderr_ref']=str(Path(bvi_report).with_suffix('.stderr.txt'))
            rows.append(row)
    for step,outcome in (step_outcomes or {}).items():
        if outcome!='success':
            rows.append(failure_row('STEP:'+step,RuntimeError('WORKFLOW_STEP_'+outcome.upper()),
                'WORKFLOW_'+step.upper(),lane='WORKFLOW'))
    return build_execution_health('WORKFLOW_AGGREGATE',rows)


def main(argv=None):
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--health-file',action='append',default=[])
    parser.add_argument('--lane-exit',action='append',default=[])
    parser.add_argument('--step-outcome',action='append',default=[])
    parser.add_argument('--bvi-report')
    parser.add_argument('--output',required=True)
    args=parser.parse_args(argv)
    pairs=lambda values:dict(value.split('=',1) for value in values)
    report=aggregate_execution_health(pairs(args.health_file),pairs(args.lane_exit),
        bvi_report=args.bvi_report,step_outcomes=pairs(args.step_outcome))
    report=write_execution_health(args.output,report)
    print(json.dumps(report,ensure_ascii=False))
    return health_exit_code(report)


if __name__=='__main__':
    raise SystemExit(main())

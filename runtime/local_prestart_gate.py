"""LOCAL transport timing checks; prediction and purchase policies are untouched."""
from datetime import datetime, timedelta, timezone
from math import isfinite


class PrestartError(ValueError):
    pass


def _time(value, name):
    try:
        stamp = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except (ValueError, TypeError) as exc:
        raise PrestartError(name + '_INVALID') from exc
    if stamp.tzinfo is None:
        raise PrestartError(name + '_TZ_REQUIRED')
    return stamp.astimezone(timezone.utc)


def validate_window(request, *, now=None, phase='FORMAL'):
    if str(request.get('temporal_mode') or 'FORMAL-PRE-RACE').upper() != 'FORMAL-PRE-RACE':
        return None
    post = _time(request.get('scheduled_post_at'), 'SCHEDULED_POST_AT')
    cutoff = _time(request.get('prediction_cutoff'), 'PREDICTION_CUTOFF')
    if cutoff >= post:
        raise PrestartError('PREDICTION_CUTOFF_NOT_BEFORE_POST')
    raw_buffer = request.get('release_buffer_seconds', 120)
    try:
        buffer = float(raw_buffer)
    except (ValueError, TypeError) as exc:
        raise PrestartError('RELEASE_BUFFER_INVALID') from exc
    if isinstance(raw_buffer, bool) or not isfinite(buffer) or buffer <= 0:
        raise PrestartError('RELEASE_BUFFER_INVALID')
    deadline = (_time(request['release_deadline_at'], 'RELEASE_DEADLINE_AT')
                if request.get('release_deadline_at') else post - timedelta(seconds=buffer))
    if deadline >= post:
        raise PrestartError('RELEASE_DEADLINE_NOT_BEFORE_POST')
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        raise PrestartError('CURRENT_TIME_TZ_REQUIRED')
    end = min(cutoff, deadline) if phase == 'SOURCE' else deadline
    if current.astimezone(timezone.utc) >= end:
        raise PrestartError('DEADLINE_HOLD:' + phase + '_INCOMPLETE')
    return {'checked_at': current.isoformat(), 'scheduled_post_at': post.isoformat(),
            'prediction_cutoff': cutoff.isoformat(), 'release_deadline_at': deadline.isoformat(),
            'phase': phase, 'status': 'PASS'}

from __future__ import annotations

from typing import Any, Dict


def request_oos_policy(request: Dict[str, Any]) -> Dict[str, Any]:
    acceptance_only = bool(request.get("acceptance_only"))
    request_oos_enabled = request.get("oos_eligible") is not False
    if acceptance_only:
        allowed = False
        reason = "ACCEPTANCE_ONLY"
    elif not request_oos_enabled:
        allowed = False
        reason = "REQUEST_OOS_DISABLED"
    else:
        allowed = True
        reason = None
    return {
        "acceptance_only": acceptance_only,
        "request_oos_eligible": request_oos_enabled,
        "oos_allowed": allowed,
        "oos_exclusion_reason": reason,
    }

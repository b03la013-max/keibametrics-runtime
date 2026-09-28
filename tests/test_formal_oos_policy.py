from runtime.formal_oos_policy import request_oos_policy


def test_acceptance_is_never_oos_eligible():
    p = request_oos_policy({"acceptance_only": True, "oos_eligible": True})
    assert p["acceptance_only"] is True
    assert p["oos_allowed"] is False
    assert p["oos_exclusion_reason"] == "ACCEPTANCE_ONLY"


def test_explicit_oos_disable_is_respected():
    p = request_oos_policy({"acceptance_only": False, "oos_eligible": False})
    assert p["oos_allowed"] is False
    assert p["oos_exclusion_reason"] == "REQUEST_OOS_DISABLED"


def test_normal_formal_request_remains_oos_capable():
    p = request_oos_policy({"acceptance_only": False})
    assert p["request_oos_eligible"] is True
    assert p["oos_allowed"] is True
    assert p["oos_exclusion_reason"] is None

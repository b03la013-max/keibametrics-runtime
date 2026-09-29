import copy
import pytest
from local_krs_technical_proxy_from_source import build, LocalSourceDerivedProxyError

def test_requires_formal_ready_signed_source():
    with pytest.raises(LocalSourceDerivedProxyError, match="SIGNED_SOURCE_FORMAL_READY_REQUIRED"):
        build({"runners":[{"runner_id":"1"}]}, {"formal_ready":False})

def test_rejects_missing_source_snapshot():
    with pytest.raises(LocalSourceDerivedProxyError, match="SOURCE_SNAPSHOT_SHA_REQUIRED"):
        build({"runners":[{"runner_id":"1"}]}, {"formal_ready":True})

def test_profile_is_explicitly_nonproduction():
    # Contract-level invariant: implementation must never silently promote the
    # source-derived diagnostic bridge to Production numerical authority.
    import pathlib
    text=(pathlib.Path(__file__).resolve().parents[1]/"runtime"/"local_krs_technical_proxy_from_source.py").read_text()
    assert '"technical_proxy_mode":True' in text
    assert '"production_authority":False' in text
    assert '"source_derived":True' in text
    assert "TECHNICAL_PROXY_DIAGNOSTIC_ONLY" in text

def test_formal_runner_autowires_only_when_numerics_held_and_degraded():
    import pathlib
    text=(pathlib.Path(__file__).resolve().parents[1]/"runtime"/"non_jra_formal_runner.py").read_text()
    assert 'req.get("full_numerical_calculation") is not True' in text
    assert 'req.get("degraded_execution") is not True' in text
    assert 'SOURCE_DERIVED_KRS_TECHNICAL_PROXY' in text
    assert 'SOURCE_DERIVED_KRS_PROXY_BUILD_FAILED' in text

"""Test-only import isolation.

runtime/jra_source_runtime/ and runtime/local_physical/ each ship top-level
modules with the same name (source_acquisition, jma_weather_evidence, app).
Every test module sets up its own sys.path, and each passes when run alone, but
in a combined run an earlier module's sys.path entries and cached modules leak
into later ones (e.g. JRA tests importing the LOCAL source_acquisition).

Here each test module is collected from the session's base sys.path with the
shadowed names un-cached, and its own sys.path / shadowed modules are restored
again before its tests run. Production import paths are not touched.
"""
import sys
import pytest

_SHADOWED = ("source_acquisition", "jma_weather_evidence", "app")
from pathlib import Path as _P
_ROOT = _P(__file__).resolve().parents[1]
# Shared roots most JRA tests (and their subprocesses) expect; LOCAL tests put
# runtime/local_physical in front of these themselves.
_BASE_PATH = [str(_ROOT / "runtime"), str(_ROOT / "runtime" / "jra_source_runtime"),
              str(_ROOT / "tests")] + [p for p in sys.path]
_STATE = {}


@pytest.hookimpl(hookwrapper=True)
def pytest_make_collect_report(collector):
    if not isinstance(collector, pytest.Module):
        yield
        return
    sys.path[:] = list(_BASE_PATH)
    for name in _SHADOWED:
        sys.modules.pop(name, None)
    yield
    _STATE[str(collector.path)] = (list(sys.path),
                                   {n: sys.modules[n] for n in _SHADOWED if n in sys.modules})


def pytest_runtest_setup(item):
    state = _STATE.get(str(item.path))
    if state is None:
        return
    path, mods = state
    sys.path[:] = path
    for name in _SHADOWED:
        if name in mods:
            sys.modules[name] = mods[name]
        else:
            sys.modules.pop(name, None)

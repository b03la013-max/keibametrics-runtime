"""A frozen registration must verify in an isolated checkout and detect drift."""
import importlib.util
import json
from pathlib import Path
import shutil
import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('shadow_registration', ROOT / 'scripts/verify_jra_shadow_registration.py')
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)


def test_existing_registration_survives_checkout_move_and_rejects_changed_definition(tmp_path):
    original = (ROOT / mod.PLAN).read_bytes()
    plan = json.loads(original)
    for key in [mod.PLAN, *plan['definition_sha256']]:
        relative = key.removeprefix(mod.RECORDED_PREFIX)
        target = tmp_path / relative; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    result = mod.verify(tmp_path)
    assert result['definition_count'] == len(plan['definition_sha256'])
    assert result['registration_fingerprint'] == plan['policy_fingerprint']
    assert not result['activation_performed']
    assert (tmp_path / mod.PLAN).read_bytes() == original
    (tmp_path / 'runtime/jra_role_rescue_shadow.py').write_text('# drift\n')
    with pytest.raises(ValueError, match='FROZEN_DEFINITION_CHANGED'):
        mod.verify(tmp_path)
    assert (tmp_path / mod.PLAN).read_bytes() == original

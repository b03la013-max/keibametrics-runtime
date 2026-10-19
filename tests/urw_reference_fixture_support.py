"""Load the explicitly synthetic reference fixture factory for offline tests."""
import importlib.util
from pathlib import Path

path=Path(__file__).parent/'fixtures/urw_reference_synthetic/build.py'
spec=importlib.util.spec_from_file_location('km_urw_synthetic_fixture_factory',path)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
fixture_root=module.fixture_root

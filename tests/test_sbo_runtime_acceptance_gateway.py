"""Offline regression for the workflow preflight; never executes SOURCE/signing."""
import copy
import io
import json
import pathlib
import textwrap
import unittest
from unittest import mock

from runtime.execution_gateway import family_config, load_gateway

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / '.github/workflows/local-sbo-public-shadow-production-runtime-acceptance.yml'


def preflight(health, status=200):
    # Run the actual inline gate, stopping before the first mutating SOURCE call.
    text = WORKFLOW.read_text()
    code = textwrap.dedent(text.split("python - <<'PY'\n", 1)[1].split('\n          mc,m=call(', 1)[0])
    # A fresh stream is needed for each bounded polling attempt.
    def reply(*args, **kwargs):
        stream = io.BytesIO(json.dumps(health).encode())
        stream.status = status
        return stream
    with mock.patch('urllib.request.urlopen', side_effect=reply), mock.patch('time.sleep'):
        namespace = {}
        exec(compile(code, str(WORKFLOW), 'exec'), namespace)
        return namespace


class RuntimeAcceptanceGatewayTests(unittest.TestCase):
    def setUp(self):
        self.cfg = family_config('LOCAL', load_gateway())
        self.health = dict(self.cfg['active_bundle_sha256'])
        self.health.update(status='READY', runtime_revision=self.cfg['runtime_profile'],
            github_revision=self.cfg['runtime_git_revision'],
            engine_sha256=self.cfg['engine_sha256'],
            parameter_map_sha256=self.cfg['parameter_map_sha256'],
            receipt_signer_key_id=self.cfg['receipt_signer_key_id'],
            capabilities=self.cfg['required_capabilities'] + ['SOURCE_SBO_PUBLIC_SHADOW'],
            sbo_public_shadow_profile='KM-LOCAL-SBO-PUBLIC-SHADOW-EVIDENCE-v1.0-20260924')

    def test_current_canonical_runtime_is_accepted(self):
        result = preflight(self.health)
        self.assertEqual(result['BASE'], self.cfg['external_endpoint'].rstrip('/'))
        self.assertEqual(result['health'], self.health)

    def test_incompatible_runtime_remains_rejected(self):
        for field in ('runtime_revision', 'engine_sha256', 'parameter_map_sha256',
                      'receipt_signer_key_id', 'runtime_app_sha256', 'sbo_public_shadow_sha256', 'status',
                      'sbo_public_shadow_profile'):
            with self.subTest(field=field):
                invalid = copy.deepcopy(self.health)
                invalid[field] = 'INCOMPATIBLE'
                with self.assertRaises(AssertionError):
                    preflight(invalid)

    def test_capabilities_and_http_status_remain_required(self):
        for capability in ('SOURCE_ACQUIRE', 'SOURCE_SBO_PUBLIC_SHADOW'):
            with self.subTest(capability=capability):
                invalid = copy.deepcopy(self.health)
                invalid['capabilities'].remove(capability)
                with self.assertRaises(AssertionError):
                    preflight(invalid)
        with self.assertRaises(AssertionError):
            preflight(self.health, status=503)

    def test_sbo_capture_and_tamper_guards_are_retained(self):
        text = WORKFLOW.read_text()
        for guard in ('SOURCE_SBO_PUBLIC_SHADOW_HASH_MISMATCH', 'CAPTURED_NOT_OOS_ELIGIBLE',
                      'POST_START', 'ev["production_authority"] is False',
                      'ev["prediction_authority"] is False', 'tv["valid"] is False'):
            self.assertIn(guard, text)


if __name__ == '__main__':
    unittest.main()

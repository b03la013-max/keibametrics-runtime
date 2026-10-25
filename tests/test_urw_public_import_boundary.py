"""Unsigned public reference must not require archive-signature dependencies."""
import json
from pathlib import Path
import subprocess
import sys
import textwrap

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('mode', ['unsigned', 'archive'])
def test_public_import_is_crypto_free_but_archive_has_no_verification_fallback(tmp_path, mode):
    script = textwrap.dedent('''
        import importlib.abc,json,sys,urllib.request
        from pathlib import Path
        class NoCrypto(importlib.abc.MetaPathFinder):
            def find_spec(self,fullname,path=None,target=None):
                if fullname=='cryptography' or fullname.startswith('cryptography.'):
                    raise ModuleNotFoundError('CRYPTOGRAPHY_INTENTIONALLY_UNAVAILABLE',name=fullname)
        sys.meta_path.insert(0,NoCrypto())
        from scripts import urw_candidate_krs_replay as replay
        from runtime import urw_reference_source_policy as policy
        assert not any(name.startswith('cryptography') for name in sys.modules)
        if sys.argv[1]=='archive':
            sys.argv=['replay','--archives',sys.argv[2],'--evidence-audit-only',
                      '--output',str(Path(sys.argv[2])/'archive-output')]
            try:replay.main()
            except ModuleNotFoundError as error:
                assert error.name.startswith('cryptography')
                print(json.dumps({'mode':'archive','verification_dependency_required':True}))
            else:raise AssertionError('archive signature verification must not be skipped')
        else:
            tick=[0.0]
            policy.POLICY=policy.UrwReferenceSourcePolicy(Path(sys.argv[2])/'robots',
                clock=lambda:tick[0],sleep=lambda seconds:tick.__setitem__(0,tick[0]+seconds))
            class Response:
                status=200
                def __init__(self,url):
                    self.url=url
                    self.headers={'Content-Type':'text/plain' if url==policy.ROBOTS_URL else 'text/html; charset=UTF-8'}
                def __enter__(self):return self
                def __exit__(self,*args):pass
                def geturl(self):return self.url
                def read(self,count):
                    return (b'User-agent: *\\nAllow: /\\nCrawl-delay: 10\\n' if self.url==policy.ROBOTS_URL
                            else b'<table><tr><td>TEST_SYNTHETIC_ONLY</td></tr></table>')
            calls=[]
            class Opener:
                def open(self,request,timeout):
                    calls.append(request.full_url)
                    return Response(request.full_url)
            urllib.request.build_opener=lambda *handlers:Opener()
            from runtime.local_physical.nar_source_manifest import _race_card_source
            snapshot,errors=replay.fetch_public_urw_reference(_race_card_source('URW','18','2099/01/01',1))
            assert snapshot['http_status']==200 and calls[0]==policy.ROBOTS_URL and len(calls)==2
            assert not any(name.startswith('cryptography') for name in sys.modules)
            print(json.dumps({'mode':'unsigned','mock_fetch_succeeded_without_crypto':True}))
    ''')
    result = subprocess.run([sys.executable, '-c', script, mode, str(tmp_path)],
                            cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    expected = ({'mode': 'unsigned', 'mock_fetch_succeeded_without_crypto': True} if mode == 'unsigned'
                else {'mode': 'archive', 'verification_dependency_required': True})
    assert json.loads(result.stdout) == expected

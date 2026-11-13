"""Pinned existing Gateway client: response.read() -> private exact bytes -> audit.

No deploy, signer, model, alternate host, Provider bypass, or SOURCE admission.
Only the pinned configured Gateway's existing /source/acquire route is used.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import socket
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'runtime'))
from local_fnb_gateway_response_bytes import save_response_bytes, _preserve


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, 'GATEWAY_REDIRECT_FORBIDDEN', headers, fp)


def pinned(path, expected):
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError('GATEWAY_CLIENT_PINNED_INPUT_MISMATCH')
    return raw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('gateway-config', 'gateway-config-sha256', 'request', 'request-sha256',
                 'trust', 'trust-sha256', 'private-root', 'name'):
        parser.add_argument('--' + name, required=True)
    for name in ('response-bytes', 'response-bytes-sha256', 'capture-metadata', 'capture-metadata-sha256'):
        parser.add_argument('--' + name)
    args = parser.parse_args()
    try:
        config = json.loads(pinned(args.gateway_config, args.gateway_config_sha256))['families']['LOCAL']
        payload = pinned(args.request, args.request_sha256)
        race_id = json.loads(payload)['race_id']
        pinned(args.trust, args.trust_sha256)
        if args.response_bytes:
            if not all((args.response_bytes_sha256, args.capture_metadata, args.capture_metadata_sha256)):
                raise ValueError('GATEWAY_CLIENT_SAVED_BYTES_AND_PROVENANCE_PINS_REQUIRED')
            raw = pinned(args.response_bytes, args.response_bytes_sha256)
            metadata = json.loads(pinned(args.capture_metadata, args.capture_metadata_sha256))
            result = save_response_bytes(raw, private_root=args.private_root, name=args.name,
                metadata=metadata, trust_path=args.trust, trust_sha256=args.trust_sha256,
                expected_race_id=race_id)
            print(json.dumps(result, ensure_ascii=False))
            return 0 if result['receipt_status'] == 'SOURCE_FROZEN' else 2
        endpoint = config['external_endpoint'].rstrip('/') + '/source/acquire'
        parsed = urllib.parse.urlsplit(endpoint)
        if parsed.scheme != 'https' or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError('GATEWAY_CLIENT_PINNED_HTTPS_ORIGIN_REQUIRED')
        request = urllib.request.Request(endpoint, data=payload, method='POST',
                                         headers={'Content-Type': 'application/json', 'Accept': 'application/json'})
        opener = urllib.request.build_opener(NoRedirect())
        with opener.open(request, timeout=25) as response:
            raw = response.read(32 * 1024 * 1024 + 1)  # Never response.json()/JS serialization.
            if len(raw) > 32 * 1024 * 1024:
                raise ValueError('GATEWAY_CLIENT_RESPONSE_SIZE_LIMIT')
            metadata = {'capture_kind': 'ORIGINAL_HTTP_RESPONSE_BODY',
                'actor': 'PINNED_GATEWAY_PYTHON_URLLIB_RESPONSE_READ', 'url': endpoint,
                'http_status': response.status, 'content_type': response.headers.get('Content-Type'),
                'observed_at': datetime.now(timezone.utc).isoformat(),
                'request_sha256': args.request_sha256, 'redirects_allowed': False}
        result = save_response_bytes(raw, private_root=args.private_root, name=args.name,
            metadata=metadata, trust_path=args.trust, trust_sha256=args.trust_sha256,
            expected_race_id=race_id)
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result['receipt_status'] == 'SOURCE_FROZEN' else 2
    except Exception as error:
        reason = 'GATEWAY_CLIENT_TRANSPORT_OR_ENVELOPE_UNVERIFIED'
        underlying = getattr(error, 'reason', error)
        if isinstance(underlying, socket.gaierror):
            reason = 'GATEWAY_CLIENT_DNS_RESOLUTION_FAILED'
        elif isinstance(underlying, ssl.SSLError):
            reason = 'GATEWAY_CLIENT_TLS_FAILED'
        elif isinstance(error, urllib.error.HTTPError):
            reason = 'GATEWAY_CLIENT_HTTP_STATUS_' + str(error.code)
            _preserve(args.private_root, args.name + '.http_error_body', error.read())
        elif isinstance(error, ValueError) and str(error).startswith('GATEWAY_'):
            reason = str(error)
        print(json.dumps({'status': 'GATEWAY_CAPTURE_HOLD_NOT_NO_BET', 'reason': reason,
                          'exception_type': type(error).__name__, 'source_admitted': False}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

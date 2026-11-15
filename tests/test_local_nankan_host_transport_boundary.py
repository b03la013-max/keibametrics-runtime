"""Allow Nankan's official HTTPS origin without weakening SOURCE/robots gates."""
from __future__ import annotations

import time
from urllib.parse import urlsplit

import pytest

from runtime.local_physical import source_acquisition as source


def test_nankan_official_host_is_allowed_but_not_suffix_spoofed(monkeypatch):
    monkeypatch.delenv("KM_SOURCE_ALLOWED_HOSTS", raising=False)
    assert source._host_allowed("nankankeiba.com")
    assert source._host_allowed("www.nankankeiba.com")
    assert not source._host_allowed("nankankeiba.com.attacker.example")
    assert not source._host_allowed("evilnankankeiba.com")
    assert not source._host_allowed("nankankeiba.example")


def test_allowed_nankan_host_still_honors_robots_disallow(monkeypatch):
    monkeypatch.setattr(source, "validate_public_url", lambda url: urlsplit(url))
    origin = "https://www.nankankeiba.com"
    monkeypatch.setattr(source, "_ROBOTS_CACHE", {
        origin: {
            "rules": [("/uma_shosai/", False)],
            "robots_status": "POLICY_READ",
            "robots_sha256": "0" * 64,
            "delay": 0,
            "expires_at": time.monotonic() + 300,
            "next_request_at": 0,
        }
    })
    with pytest.raises(ValueError, match="SOURCE_POLICY_ROBOTS_DISALLOWED"):
        source._source_access_policy(
            origin + "/uma_shosai/2026110319080205.do", timeout=3,
        )

import sys
sys.path.insert(0, "runtime")
import jra_delivery as d

URL = "https://raw.githubusercontent.com/b03la013-max/keibametrics-runtime/" + "a" * 40 + "/runtime/final_artifacts/KM-JRA-TKY-20261121-R01.json"


def test_private_repo_reads_same_commit_through_authenticated_api(monkeypatch):
    seen = {}
    def fake(req, timeout=20):
        seen["url"] = getattr(req, "full_url", req)
        seen["auth"] = getattr(req, "headers", {}).get("Authorization")
        seen["accept"] = getattr(req, "headers", {}).get("Accept")
        return "ok"
    monkeypatch.setattr(d.urllib.request, "urlopen", fake)
    monkeypatch.setenv("GH_TOKEN", "t")
    assert d._canonical_open(URL) == "ok"
    assert seen["url"] == ("https://api.github.com/repos/b03la013-max/keibametrics-runtime/contents/"
                           "runtime/final_artifacts/KM-JRA-TKY-20261121-R01.json?ref=" + "a" * 40)
    assert seen["auth"] == "Bearer t" and seen["accept"] == "application/vnd.github.raw"


def test_without_token_keeps_raw_url(monkeypatch):
    seen = {}
    monkeypatch.setattr(d.urllib.request, "urlopen", lambda req, timeout=20: seen.setdefault("u", req))
    monkeypatch.delenv("GH_TOKEN", raising=False); monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    d._canonical_open(URL)
    assert seen["u"] == URL

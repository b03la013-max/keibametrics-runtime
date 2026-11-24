"""Live self-test of the GitHub OIDC token witness on a real GitHub-hosted runner.

Mints a witness for a throw-away file and verifies signature, digest binding, issuer,
repository identity and runner type against GitHub's live JWKS. The workflow/ref claims
are reported, not enforced, because a pull request runs on refs/pull/<n>/merge.
No Production artifact is touched.
"""
import json, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
import km_oidc_witness as W

with tempfile.TemporaryDirectory() as d:
    art = Path(d) / "selftest.json"; art.write_text(json.dumps({"selftest": True}))
    w = W.mint(art, Path(d) / "selftest.oidc_witness.json", "SELFTEST")
    c = W.verify_token(w, W._digest(art), jwks=W.live_jwks())
    assert c["repository"] == W.REPOSITORY and str(c["repository_id"]) == W.REPOSITORY_ID
    assert str(c["repository_owner_id"]) == W.OWNER_ID and c["runner_environment"] == "github-hosted"
    art.write_text("tampered")
    try:
        W.verify_token(w, W._digest(art), jwks=W.live_jwks()); raise SystemExit("TAMPER_NOT_DETECTED")
    except W.WitnessError:
        pass
    print(json.dumps({"status": "KM_OIDC_WITNESS_SELFTEST_PASS", "kid_published": True,
                      "workflow_ref": c.get("workflow_ref"), "ref": c.get("ref"), "iat": c.get("iat")}))

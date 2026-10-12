"""Read-only real Railway receipt regression. Never sends data or adds OOS."""
import base64
import hashlib
import json
from pathlib import Path
import sys
import tarfile
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / "runtime"))
from local_aki_columns import sha


def test_real_external_source_krs_final_result_and_paper_boundary():
    root = ROOT / "evidence/local_aki_columns_20261012"
    manifest = json.loads((root / "external_acceptance_manifest.json").read_text())
    archive_path = root / "kaw_r11_external_receipts.tar.gz"
    assert hashlib.sha256(archive_path.read_bytes()).hexdigest() == manifest["archive_sha256"]
    attestation = json.loads((root / "destination_verification.json").read_text())
    key = Ed25519PublicKey.from_public_bytes(base64.b64decode(attestation["health"]["receipt_public_key_b64"]))
    prefix = "external/KM-LOCAL-KAW-20261012-R11-LIVE-R1/39f06c07ee208cf9/"
    with tarfile.open(archive_path,"r:gz") as archive:
        def load(name): return json.load(archive.extractfile(prefix + name + ".json"))
        envelopes = {p:load(n) for p,n in (("PRE_KRS","pre_krs_receipt"),("KRS_RUN","krs_receipt"),
            ("FINAL","final_receipt"),("RESULT","replay_result_receipt"))}
        envelopes["SOURCE"] = json.loads((ROOT / manifest["canonical_source_path"]).read_text())
        assert envelopes["SOURCE"]["receipt_sha256"] == manifest["canonical_source_receipt_sha256"]
        for phase, e in envelopes.items():
            raw = json.dumps(e["receipt"],ensure_ascii=False,sort_keys=True,separators=(",", ":")).encode()
            key.verify(base64.b64decode(e["signature"]),raw)
            assert sha(e["artifact"]) == e["receipt"]["artifact_sha256"]
            assert hashlib.sha256(raw).hexdigest() == e["receipt_sha256"]
            assert e["receipt"]["phase"] == phase
            assert e["receipt"]["race_id"] == manifest["source_race_id"]
        run = envelopes["KRS_RUN"]["artifact"]
        assert run["actual_run_count"] == 20000
        assert run["input_sha256"] == envelopes["PRE_KRS"]["artifact"]["input_sha256"] == sha(load("krs_input"))
        final = envelopes["FINAL"]
        fpp = final["artifact"]["final_prediction_package"]
        columns = fpp["aki_selection"]["columns"]
        for rid, roles in fpp["roles"].items():
            assert roles == [c for c in ("W","P2","P3") if rid in columns[c]["selected"]]
        assert len(fpp["paper_tickets"]) == 10
        assert final["artifact"]["final_ticket"]["tickets"] == []
        assert final["artifact"]["capital_policy_decision"]["decision"] == "PAPER"
        result = envelopes["RESULT"]["artifact"]
        assert result["frozen_refs"]["final_receipt_sha256"] == final["receipt_sha256"]
        assert result["settlement"]["investment"] == 0
        assert result["settlement"]["pfs"] is None
        assert load("paper_settlement")["investment"] == 1000
        assert load("paper_settlement")["return"] == 0
        assert load("paper_reflection")["failure_localization"]["first_material_failure"] == "PREDICTION_ROLE_P2"
        assert load("paper_learning")["production_change_authorized"] is False
        assert manifest["unknown_future_oos_count"] == 0


def test_multi_venue_real_signed_variable_counts():
    root = ROOT / 'evidence/local_aki_columns_20261012'
    manifest = json.loads((root / 'multi_venue_manifest.json').read_text())
    path = root / 'multi_venue_external_receipts.tar.gz'
    assert hashlib.sha256(path.read_bytes()).hexdigest() == manifest['archive_sha256']
    attestation = json.loads((root / 'destination_verification.json').read_text())
    key = Ed25519PublicKey.from_public_bytes(base64.b64decode(attestation['health']['receipt_public_key_b64']))
    counts = []
    with tarfile.open(path, 'r:gz') as archive:
        for case in manifest['cases']:
            def load(name):
                raw = archive.extractfile(case['prefix'] + '/' + name + '.json').read()
                assert hashlib.sha256(raw).hexdigest() == case['files'][name + '.json']
                return json.loads(raw)
            envelopes = [load(n) for n in ('pre_krs_receipt','krs_receipt','final_receipt')]
            for e in envelopes:
                raw = json.dumps(e['receipt'],ensure_ascii=False,sort_keys=True,separators=(',', ':')).encode()
                key.verify(base64.b64decode(e['signature']),raw)
                assert sha(e['artifact']) == e['receipt']['artifact_sha256']
                assert hashlib.sha256(raw).hexdigest() == e['receipt_sha256']
                assert e['receipt']['race_id'] == case['acceptance']['race_id']
            assert envelopes[1]['artifact']['actual_run_count'] == 20000
            assert envelopes[1]['artifact']['input_sha256'] == envelopes[0]['artifact']['input_sha256'] == sha(load('krs_input'))
            final = envelopes[2]
            assert final['receipt_sha256'] == case['acceptance']['final_receipt_sha256']
            assert final['artifact']['final_prediction_package']['aki_selection'] == load('selection')
            counts.append(len(final['artifact']['final_prediction_package']['paper_tickets']))
            assert final['artifact']['final_ticket']['tickets'] == []
            assert final['artifact']['capital_policy_decision']['decision'] == 'PAPER'
    assert counts == [2,341,25]
    assert manifest['unique_actual_krs_runs'] == 60000
    assert manifest['unknown_future_oos_count'] == 0

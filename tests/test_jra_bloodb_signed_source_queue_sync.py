"""JRA signed formal intent -> Blood-B local queue, adversarial offline tests.

Exercises actual Ed25519 verification (not monkeypatched). Provider pages and
secrets are never accessed, and historical races never receive OOS credit.
"""
from __future__ import annotations
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
sys.path.insert(0,str(ROOT/"runtime"))
from jra_bloodb_signed_source_queue_sync import synchronize,collect_specs
from jra_bloodb_mac_collector import BloodBError
from jra_source_runtime.verify_source_envelope import sha_obj

RACE="KM-JRA-KYO-20261011-R09"
RUN=RACE+"-LIVE-R1"
CUTOFF="2026-10-11T14:00:00+09:00"
POST="2026-10-11T14:05:00+09:00"
NOW=datetime.fromisoformat("2026-10-10T10:00:00+09:00")
OFFICIAL=[
 {"runner_id":"1","horse_no":1,"horse_name":"血統テスト一号","status":"ACTIVE"},
 {"runner_id":"2","horse_no":2,"horse_name":"血統テスト二号","status":"ACTIVE"},
]

def fixture(root:Path,*,signed=True,cutoff=CUTOFF,source_race=RACE,
            future_date="2026-10-11",alter_source=False):
    fi=root/"runtime/jra_formal_intents"/(RUN+".json")
    fi.parent.mkdir(parents=True,exist_ok=True)
    intent={"family_id":"JRA","temporal_mode":"FORMAL-PRE-RACE",
       "race_id":RACE,"execution_id":RUN,"venue_id":"KYO",
       "race_date":future_date,"race_no":9,"prediction_cutoff":cutoff,
       "scheduled_post_at":POST,"acceptance_only":False}
    fi.write_text(json.dumps(intent),encoding="utf-8")
    src=root/"runtime/executions"/RUN/"SOURCE/runs"/"123"/"source_receipt_envelope.json"
    src.parent.mkdir(parents=True,exist_ok=True)
    art={"race_id":source_race,"family_id":"JRA",
        "prediction_cutoff":cutoff,"source_freeze_at":"2026-10-10T09:20:00+09:00",
        "source_race_context":{"race_date":"2026-10-11","venue_id":"KYO","race_no":9},
        "jra_official_race_card_detail":{"runners":OFFICIAL},
        "formal_ready":True, "errors":[]}
    private=Ed25519PrivateKey.generate()
    rec={"race_id":source_race,"family":"JRA","artifact_sha256":sha_obj(art)}
    canonical=json.dumps(rec,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
    envelope={"artifact":art,"receipt":rec,
       "receipt_sha256":hashlib.sha256(canonical).hexdigest(),
       "signature":base64.b64encode(private.sign(canonical)).decode(),
       "receipt_public_key_b64":base64.b64encode(
          private.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)).decode(),
       "signer_trust_class":"GITHUB_ACTIONS_EPHEMERAL_ED25519_PLUS_GITHUB_OIDC_ATTESTATION",
       "github_repository":"b03la013-max/keibametrics-runtime"}
    if alter_source:
        envelope["artifact"]["jra_official_race_card_detail"]["runners"][0]["horse_name"]="攻撃による改ざん"
    src.write_text(json.dumps(envelope),encoding="utf-8")
    return fi,src

class SignedSourceQueueTests(unittest.TestCase):
    def test_genuine_future_race_is_queued_only_after_signed_source_validation(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            fixture(root)
            queue=root/"secrets"/"queue.json"
            preview=synchronize(root,queue,now=NOW,dry_run=True)
            self.assertEqual(preview["signed_source_ready"],1)
            self.assertEqual(preview["new_items"],1)
            self.assertFalse(queue.exists())
            result=synchronize(root,queue,now=NOW)
            self.assertEqual(result["paid_page_fetches"],0)
            self.assertEqual(result["new_items"],1)
            record=json.loads(queue.read_text())
            self.assertEqual(len(record),1)
            self.assertEqual(record[0]["race_no"],9)
            self.assertEqual(record[0]["venue"],"京都")
            self.assertEqual(record[0]["race_id"],RACE)
            self.assertTrue(record[0]["signed_source_envelope_path"].endswith("source_receipt_envelope.json"))
            self.assertFalse(record[0]["production_authority"])
            self.assertEqual(queue.stat().st_mode & 0o077,0)
            again=synchronize(root,queue,now=NOW)
            self.assertEqual(again["new_items"],0)

    def test_tampered_source_or_wrong_race_cannot_enter_queue(self):
        for kwargs in ({"alter_source":True},
                       {"source_race":"KM-JRA-KYO-20261011-R08"}):
            with self.subTest(kwargs=kwargs),tempfile.TemporaryDirectory() as d:
                root=Path(d)
                fixture(root,**kwargs)
                queue=root/"secrets"/"queue.json"
                result=synchronize(root,queue,now=NOW)
                self.assertEqual(result["candidate_intents"],1)
                self.assertEqual(result["signed_source_ready"],0)
                self.assertEqual(result["missing_signed_source"],1)
                self.assertEqual(json.loads(queue.read_text()),[])

    def test_future_frozen_source_not_admitted_before_it_exists(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            fi,source=fixture(root)
            envelope=json.loads(source.read_text())
            envelope["artifact"]["source_freeze_at"]="2026-10-11T12:20:00+09:00"
            # Even if an attacker re-signs the new payload legitimately,
            # SOURCE cannot be admitted ahead of actual frozen-at time.
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
            from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
            private=Ed25519PrivateKey.generate()
            rec=envelope["receipt"]
            rec["artifact_sha256"]=sha_obj(envelope["artifact"])
            raw=json.dumps(rec,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
            envelope["receipt_sha256"]=hashlib.sha256(raw).hexdigest()
            envelope["signature"]=base64.b64encode(private.sign(raw)).decode()
            envelope["receipt_public_key_b64"]=base64.b64encode(
                private.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)).decode()
            source.write_text(json.dumps(envelope))
            report=synchronize(root,root/"queue.json",now=NOW,dry_run=True)
            self.assertEqual(report["signed_source_ready"],0)

    def test_historical_date_and_cutoff_mismatch_cannot_be_smuggled(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            intent,_=fixture(root)
            row=json.loads(intent.read_text())
            row["race_date"]="2026-10-10"
            intent.write_text(json.dumps(row))
            r=synchronize(root,root/"queue.json",now=NOW,dry_run=True)
            self.assertEqual(r["candidate_intents"],0)
            row["race_date"]="2026-10-11"
            row["execution_id"]="../secret/evade"
            intent.write_text(json.dumps(row))
            self.assertEqual(synchronize(root,root/"queue.json",now=NOW,dry_run=True)["candidate_intents"],0)

    def test_no_after_cutoff_replay_and_no_backdating(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            fixture(root)
            now=datetime.fromisoformat("2026-10-11T14:01:00+09:00")
            r=synchronize(root,root/"queue.json",now=now)
            self.assertEqual(r["signed_source_ready"],0)
            self.assertEqual(r["queue_items"],0)
            self.assertEqual(json.loads((root/"queue.json").read_text()),[])

    def test_existing_conflict_is_hard_block_and_no_modified_queue(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            fixture(root)
            q=root/"private"/"queue.json"
            synchronize(root,q,now=NOW)
            prior=q.read_bytes()
            data=json.loads(prior)
            data[0]["jra_signed_source_artifact_sha256"]="b"*64
            q.write_text(json.dumps(data))
            with self.assertRaisesRegex(BloodBError,"CONFLICT"):
                synchronize(root,q,now=NOW)
            self.assertEqual(q.read_text(),json.dumps(data))

if __name__=="__main__":
    unittest.main()

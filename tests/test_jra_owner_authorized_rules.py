"""Owner-authorized JRA official feature rules, pedigree corpus, parser repairs,
race-day resolver and owner-authorized (UNVALIDATED) Static activation."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import base64
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
sys.path.insert(0, str(ROOT / "runtime/jra_source_runtime"))
sys.path.insert(0, str(ROOT / "tests"))

from jra_owner_authorized_feature_rules import (
    RULES, RULE_AUTHORITY, owner_authorized_observations, decode_passing_positions, class_rank,
)
from jra_pedigree_corpus import build_corpus
from jra_race_card_detail import _parse_recent, decode_passing_positions as parser_decode
from jra_race_day_resolver import parse_day_rows, build_intent, venue_code
from jra_pedigree_harvest import parse_horse_pedigree
from jra_production_auto_handoff import (
    JRAProductionAutoHandoffError, require_independent_owner_activation,
)

REAL = "KM-JRA-TKY-20261010-R12-FULLPIPELINE-VALIDATION-LIVE-R1"
REGISTRY = json.loads((ROOT / "mapping/jra_evidence_feature_rule_registry_v1.2_20261010.json").read_text())


def real_artifact():
    runs = sorted((ROOT / "runtime/executions" / REAL / "SOURCE/runs").glob("*/source_receipt_envelope.json"))
    if not runs:
        raise unittest.SkipTest("stored SOURCE missing")
    return json.loads(runs[-1].read_text())["artifact"]


class TestPassingDecoder(unittest.TestCase):
    # Cases verified against official corner_list markup (949/951 exact on
    # 2026-10-11 cards; ambiguous strings return None instead of guessing).
    CASES = [("1515", 16, [15, 15]), ("119", 16, [11, 9]), ("13131415", 16, [13, 13, 14, 15]),
             ("7868", 14, [7, 8, 6, 8]), ("12", 16, [1, 2]), ("910", 16, [9, 10])]

    def test_decoder_both_copies_agree(self):
        for digits, n, want in self.CASES:
            self.assertEqual(decode_passing_positions(digits, n), want)
            self.assertEqual(parser_decode(digits, n), want)
        self.assertIsNone(decode_passing_positions("", 16))

    def test_parser_repairs(self):
        r = _parse_recent("2026年7月12日 小倉 阿蘇S OP 8着 11頭11番1番人気 川田 将雅 58.0kg 1700ダ "
                          "1:46.1 良 92 494kg 10 10 1 1 3F 38.6 レイナデアルシーラ(1.2)")
        self.assertEqual((r["going"], r["body_weight"], r["rating"]), ("良", 494, 92))
        self.assertEqual(r["passing_positions"], [10, 10, 1, 1])
        self.assertEqual(r["jockey"], "川田 将雅")
        self.assertEqual(r["passing_positions_parser"], "CORNER-LIST-SEPARATED-v2")
        old = _parse_recent("2026年10月3日 京都 1勝クラス 4着 16頭9番8番人気 富田 暁 58.0kg 1400ダ "
                            "1:24.0 良 516kg 1515 3F 36.4 パンサーズ(0.4)")
        self.assertEqual(old["passing_positions"], [15, 15])

    def test_class_rank(self):
        self.assertEqual(class_rank("3歳上1勝クラス"), 1)
        self.assertEqual(class_rank("米子城S OP"), 4)
        self.assertEqual(class_rank("サウジアラビアRC(GⅢ)"), 5)
        self.assertIsNone(class_rank("高瀬川S"))


class TestOwnerAuthorizedRules(unittest.TestCase):
    def test_real_source_features_are_labelled_registered_and_pre_race(self):
        art = real_artifact()
        out = owner_authorized_observations(art, REGISTRY, corpus=None)
        self.assertGreaterEqual(len(out), 2)
        seen = set()
        for rid, feats in out.items():
            for name, f in feats.items():
                seen.add(name)
                self.assertIn(f["rule_id"], REGISTRY["feature_rules"][name])
                self.assertEqual(f["rule_id"], RULES[name])
                self.assertEqual(f["rule_authority"], RULE_AUTHORITY)
                self.assertFalse(f["result_derived"])
                self.assertTrue(f["production_authority"])
                self.assertEqual(f["evidence_refs"][0], art["source_snapshot_sha256"])
                self.assertIn("UNVALIDATED", f["source_fact"])
        for must in ("recent_speed", "closing_quality", "position_quality", "rotation_fit",
                     "preparation_continuity", "same_day_track_fit", "market_mismatch"):
            self.assertIn(must, seen)

    def test_unregistered_rule_fails_closed(self):
        reg = deepcopy(REGISTRY)
        reg["feature_rules"]["recent_speed"] = ["SOMETHING-ELSE"]
        with self.assertRaisesRegex(ValueError, "NOT_REGISTERED"):
            owner_authorized_observations(real_artifact(), reg)

    def test_post_race_and_later_same_day_facts_are_ignored(self):
        art = real_artifact()
        base = owner_authorized_observations(art, REGISTRY)
        tampered = deepcopy(art)
        rid = next(iter(base))
        det = [x for x in tampered["jra_official_race_card_detail"]["runners"] if str(x["runner_id"]) == rid][0]
        det["recent_runs"].insert(0, {**det["recent_runs"][0], "date": "2026-10-10", "finish": 1, "margin": 0.0})
        hist = tampered["jra_official_horse_history"]["runners"][rid]["runs"]
        hist.insert(0, {**hist[0], "date": "2026-10-11", "finish": 1})
        races = tampered["jra_official_same_day_results"]["races"]
        later = deepcopy(next(iter(races.values())))
        later["race_no"] = 12
        races["12"] = later
        again = owner_authorized_observations(tampered, REGISTRY)
        self.assertEqual(base[rid], again[rid])

    def test_minimum_samples_never_filled(self):
        art = deepcopy(real_artifact())
        for x in art["jra_official_race_card_detail"]["runners"]:
            x["recent_runs"] = x["recent_runs"][:1]
            x["career_record"] = {"starts": 12}
        out = owner_authorized_observations(art, REGISTRY)
        for feats in out.values():
            self.assertNotIn("recent_speed", feats)
            self.assertNotIn("position_reproducibility", feats)
        art2 = deepcopy(real_artifact())
        art2["source_freeze_at"] = "2026-10-10T23:59:00+09:00"
        self.assertEqual(owner_authorized_observations(art2, REGISTRY), {})


class TestPedigreeCorpus(unittest.TestCase):
    def _signed_source(self, artifact, path):
        """An actual valid Ed25519 test receipt, never an unsigned JSON label."""
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
        from jra_source_runtime.verify_source_envelope import sha_obj
        private = Ed25519PrivateKey.generate()
        artifact = deepcopy(artifact)
        artifact["source_snapshot_sha256"] = sha_obj(artifact)
        receipt = {"race_id": artifact["race_id"], "family": "JRA",
                   "artifact_sha256": sha_obj(artifact)}
        canonical = json.dumps(receipt, ensure_ascii=False, sort_keys=True,
                               separators=(",", ":")).encode()
        env = {
            "artifact": artifact,
            "receipt": receipt,
            "receipt_sha256": hashlib.sha256(canonical).hexdigest(),
            "signature": base64.b64encode(private.sign(canonical)).decode(),
            "receipt_public_key_b64": base64.b64encode(
                private.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)).decode(),
            "signer_trust_class": "GITHUB_ACTIONS_EPHEMERAL_ED25519_PLUS_GITHUB_OIDC_ATTESTATION",
            "github_repository": "b03la013-max/keibametrics-runtime",
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(env))

    def _harvest(self, path, *, at, horses):
        profile = "KM-JRA-OFFICIAL-PEDIGREE-HARVEST-v1.0-20261010"
        data = {"profile": profile, "official": True, "source": "www.jra.go.jp",
                "race_date": "2026-10-01", "mode": "results",
                "harvested_at": at, "horse_token_count": len(horses),
                "horse_count": len(horses), "horses": horses, "errors": []}
        data["sha256"] = hashlib.sha256(json.dumps(
            data, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data))

    def test_point_in_time_and_harvest_cutoff(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "runtime/executions/X/SOURCE/runs/1/source_receipt_envelope.json"
            art = {"family_id": "JRA", "race_id": "R1",
                   "source_freeze_at": "2026-10-01T10:00:00+09:00",
                   "jra_official_race_card_detail": {"runners": [{
                       "runner_id": "1", "horse_name": "A", "sire": "S", "dam": "MA",
                       "damsire": "D",
                       "recent_runs": [
                           {"date": "2026-09-01", "finish": 1, "field_size": 10,
                            "surface": "芝", "venue": "東京", "distance_m": 1600},
                           {"date": "2026-10-05", "finish": 1, "field_size": 10,
                            "surface": "芝", "venue": "東京", "distance_m": 1600}]}]}}
            self._signed_source(art, src)
            later = root / "runtime/executions/Y/SOURCE/runs/1/source_receipt_envelope.json"
            art2 = deepcopy(art)
            art2.update(race_id="R2", source_freeze_at="2026-10-09T10:00:00+09:00")
            art2["jra_official_race_card_detail"]["runners"][0].update(
                horse_name="B", dam="MB")
            self._signed_source(art2, later)
            hv = root / "runtime/pedigree_corpus/h.json"
            self._harvest(hv, at="2026-10-08T00:00:00+09:00", horses=[
                {"horse_name": "C", "sire": "S", "dam": "MC",
                 "raw_sha256": "1"*64,
                 "runs": [{"date": "2026-09-02", "finish": 2, "field_size": 8}]},
            ])
            # Unsigned flag and hash alone are not provenance.
            early = build_corpus(root, prediction_cutoff="2026-10-03T12:00:00+09:00",
                                 race_date="2026-10-03",
                                 attestation_verifier=lambda p: True)
            self.assertEqual({h["horse_name"] for h in early["horses"].values()}, {"A"})
            self.assertEqual(early["run_count"], 1)
            late = build_corpus(root, prediction_cutoff="2026-10-10T12:00:00+09:00",
                                race_date="2026-10-10",
                                attestation_verifier=lambda p: True)
            self.assertEqual({h["horse_name"] for h in late["horses"].values()}, {"A","B","C"})
            self.assertEqual(late["horse_count"], 3)
            self.assertEqual(late["run_count"], 5)
            skipped = build_corpus(root, prediction_cutoff="2026-10-10T12:00:00+09:00",
                                   race_date="2026-10-10",
                                   attestation_verifier=lambda p: False)
            self.assertEqual({h["horse_name"] for h in skipped["horses"].values()}, {"A","B"})
            excluded = build_corpus(root, prediction_cutoff="2026-10-10T12:00:00+09:00",
                                    race_date="2026-10-10",exclude_race_id="R1",
                                    attestation_verifier=lambda p: False)
            self.assertEqual({h["horse_name"] for h in excluded["horses"].values()}, {"B"})

    def test_reject_tamper_and_name_collision(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "runtime/pedigree_corpus/h.json"
            horses = [{
                "horse_name":"同名馬", "sire":"S", "dam":"M1",
                "raw_sha256":"a"*64,
                "runs":[{"date":"2026-09-01","venue":"東京","surface":"芝",
                         "distance_m":1600,"finish":1,"field_size":10}]
            },{
                "horse_name":"同名馬", "sire":"S", "dam":"M2",
                "raw_sha256":"b"*64,
                "runs":[{"date":"2026-09-01","venue":"東京","surface":"芝",
                         "distance_m":1600,"finish":7,"field_size":10}]
            }]
            self._harvest(path,at="2026-10-01T00:00:00+09:00",horses=horses)
            ok = build_corpus(root,prediction_cutoff="2026-10-10T12:00:00+09:00",
                              race_date="2026-10-10",attestation_verifier=lambda p: True)
            self.assertEqual(ok["horse_count"], 2)
            self.assertEqual(ok["identity_collision_count"], 1)
            # Tampering with a published result after SHA creation fails.
            obj=json.loads(path.read_text())
            obj["horses"][0]["runs"][0]["finish"]=9
            path.write_text(json.dumps(obj))
            bad=build_corpus(root,prediction_cutoff="2026-10-10T12:00:00+09:00",
                             race_date="2026-10-10",attestation_verifier=lambda p: True)
            self.assertEqual(bad["horse_count"],0)
            self.assertEqual(bad["rejected_untrusted_inputs"],1)



class TestResolverAndHarvestParsers(unittest.TestCase):
    ROWS = ["レース番号 発走時刻 レース名",
            "9時50分 2歳未勝利[指定] ダート1,200m15頭 出馬表 未発表 未確定",
            "11時20分 障害3歳以上未勝利（混合） 芝→ダート2,910m9頭 出馬表",
            "15時30分 太秦ステークス 3歳以上オープン（国際）（特指） ダート1,800m14頭 出馬表"]

    def test_day_rows_and_intent(self):
        races = parse_day_rows(self.ROWS)
        self.assertEqual([r["race_no"] for r in races], [1, 2, 3])
        self.assertEqual(races[2]["distance_m"], 1800)
        it = build_intent(race_date="2026-10-11", venue="京都", race_no=3, meeting_key="0820260404", race=races[2])
        self.assertEqual(it["race_id"], "KM-JRA-KYO-20261011-R03")
        self.assertEqual(it["scheduled_post_at"], "2026-10-11T15:30:00+09:00")
        self.assertLess(it["prediction_cutoff"], it["external_dispatch_deadline_at"])
        with self.assertRaisesRegex(ValueError, "VENUE_MISMATCH"):
            build_intent(race_date="2026-10-11", venue="東京", race_no=3, meeting_key="0820260404", race=races[2])
        with self.assertRaises(ValueError):
            venue_code("大井")

    def test_horse_page_pedigree(self):
        page = ('<span class="opt">競走馬情報</span>ウルトラハート<span class="name_en">Ultra</span>'
                '<dt>父</dt>\n<dd><a href="#">ホッコータルマエ</a></dd>'
                '<dt>母</dt><dd><a href="#">プレイフォーユー</a><span class="sanku"><a href="#">産駒</a></span></dd>'
                '<dt>母の父</dt>\n <dd><a href="#">ハーツクライ</a></dd>')
        self.assertEqual(parse_horse_pedigree(page), {"horse_name": "ウルトラハート", "sire": "ホッコータルマエ",
                                                      "dam": "プレイフォーユー", "damsire": "ハーツクライ"})


class TestOwnerAuthorizedActivation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "runtime").mkdir()
        shutil.copy(ROOT / "runtime/jra_static_owner_executable.py", self.root / "runtime/")
        (self.root / "governance").mkdir()
        rec = {"decision": "AUTHORIZE_PRODUCTION_STATIC_OWNER_UNVALIDATED",
               "policy_profile": "JRA-STATIC-PREDICTION-OWNER-EXECUTABLE-CANDIDATE-20261010",
               "authorized_by": "TEST OWNER", "authorized_at": "2026-10-10T16:14:00+09:00"}
        p = self.root / "governance/rec.json"
        p.write_text(json.dumps(rec))
        self.activation = {
            "status": "OWNER_AUTHORIZED_UNVALIDATED",
            "profile": "JRA-STATIC-PREDICTION-OWNER-EXECUTABLE-CANDIDATE-20261010",
            "validation_status": "UNVALIDATED", "automatic_promotion": False,
            "forward_oos_eligible_races_at_authorization": 0,
            "market_baseline_superiority_proven": False,
            "policy_source_sha256": hashlib.sha256((ROOT / "runtime/jra_static_owner_executable.py").read_bytes()).hexdigest(),
            "owner_authorization_record": "governance/rec.json",
            "owner_authorization_record_sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        }

    def tearDown(self):
        self.tmp.cleanup()

    def auth(self, act):
        return {"family_scoped_authority": {"JRA": {"production_static_owner_activation": act}}}

    def test_truthful_owner_record_is_accepted_and_labelled(self):
        out = require_independent_owner_activation(self.auth(self.activation), root=self.root)
        self.assertEqual(out["validation_status"], "UNVALIDATED")
        intent, env, report, _ = __import__("test_jra_production_auto_handoff").fixture()
        from jra_production_auto_handoff import compile_production_auto_handoff
        req = compile_production_auto_handoff(intent, env, report, current_authority=self.auth(self.activation),
                                              frozen_at="2026-10-10T12:09:00+09:00", root=self.root)
        self.assertEqual(req["static_owner_activation_binding"]["validation_status"], "UNVALIDATED")
        self.assertIn("OWNER-AUTHORIZED-UNVALIDATED", req["static_prediction"]["status"])

    def test_fabricated_validation_or_tampered_record_rejected(self):
        for patch in ({"market_baseline_superiority_proven": True}, {"automatic_promotion": True},
                      {"validation_status": "VALIDATED"}, {"forward_oos_eligible_races_at_authorization": "30"},
                      {"policy_source_sha256": "0" * 64}, {"owner_authorization_record_sha256": "0" * 64},
                      {"owner_authorization_record": "governance/missing.json"}):
            with self.subTest(patch=patch):
                with self.assertRaises(JRAProductionAutoHandoffError):
                    require_independent_owner_activation(self.auth({**self.activation, **patch}), root=self.root)


if __name__ == "__main__":
    unittest.main()

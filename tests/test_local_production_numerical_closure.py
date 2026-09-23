import unittest
from runtime.local_evidence_to_base_production import materialize_request, WEIGHTS
from runtime.local_krs_input_builder_production import build as build_krs, HSV_KEYS, STATIC_KEYS, LocalKRSBridgeError

def fs(score=70):
    return {"score":score,"rule_id":"LOCAL-TEST-CANON-v1","evidence_refs":["E1"],"source_fact":"fixture","source_timestamp":"2026-09-22T12:00:00+09:00"}

class LocalProductionClosureTest(unittest.TestCase):
    def runner(self):
        feats={}
        for spec in WEIGHTS.values():
            for k in spec: feats[k]=fs()
        return {"runner_id":"1","name":"Fixture","evidence_features":feats}

    def base_request(self):
        return {
          "race_id":"LOCAL-SELFTEST-R1",
          "venue_formula_registry":{
            "registry_id":"LOCAL-SELFTEST-VENUE-RULES-v1",
            "allowed_rule_ids":{"EVI/CEV":["LOCAL-EVI-SELFTEST-v1"]}
          },
          "runners":[{
            **self.runner(),
            "canonical_external_indices":{
              "EVI/CEV":{"value":70,"rule_id":"LOCAL-EVI-SELFTEST-v1","evidence_refs":["EVI1"],"source_fact":"fixture evi","venue_formula_registry":"LOCAL-SELFTEST-VENUE-RULES-v1"}
            }
          }]
        }

    def test_exact_common_mapping(self):
        req=materialize_request(self.base_request(),["HPI-L","CFIg-L","RFIg-L","BVIg-L","JTI-L","CSI-L","BWI-L","DCR","NCI","EVI/CEV","TPI-L"])
        self.assertTrue(req["full_numerical_calculation"])
        self.assertEqual(req["numeric_coverage"]["unresolved_count"],0)
        cc=req["runners"][0]["canonical_components"]
        self.assertAlmostEqual(cc["HPI-L"]["value"],70)
        self.assertAlmostEqual(cc["TPI-L"]["value"],70)
        self.assertTrue(cc["HPI-L"]["rule_id"])
        self.assertTrue(cc["HPI-L"]["evidence_refs"])

    def test_unspecified_formula_terminalizes_without_fake_value(self):
        req=materialize_request(self.base_request(),["HPI-L","TPI-L","ZAI-WIN"])
        self.assertFalse(req["full_numerical_calculation"])
        self.assertTrue(req["full_terminalization"])
        self.assertEqual(req["numeric_coverage"]["unresolved_count"],0)
        self.assertEqual(req["numeric_coverage"]["ruled_hold_count"],1)
        z=req["runners"][0]["canonical_components"]["ZAI-WIN"]
        self.assertEqual(z["terminal_status"],"RULED-HOLD")
        self.assertNotIn("value",z)

    def test_explicit_degraded_base_hold_terminalizes_without_fake_scores(self):
        req={
          "race_id":"LOCAL-DEGRADED-R1",
          "allow_base_index_rule_hold":True,
          "runners":[{"runner_id":"1","name":"Real-race degraded fixture"}]
        }
        out=materialize_request(req,["HPI-L","CFIg-L"])
        self.assertTrue(out["full_terminalization"])
        self.assertFalse(out["full_numerical_calculation"])
        self.assertEqual(out["numeric_coverage"]["calculated_count"],0)
        self.assertEqual(out["numeric_coverage"]["ruled_hold_count"],2)
        self.assertEqual(out["numeric_coverage"]["unresolved_count"],0)

    def test_degraded_tpi_holds_when_base_dependencies_are_nonnumeric(self):
        req={
          "race_id":"LOCAL-DEGRADED-TPI-R1",
          "allow_base_index_rule_hold":True,
          "venue_formula_registry":{
            "registry_id":"LOCAL-DEGRADED-VENUE-RULES-v1",
            "allowed_rule_ids":{"EVI/CEV":[]},
            "default_terminals":{
              "EVI/CEV":{
                "terminal_status":"RULED-NEUTRAL","value":52,
                "rule_id":"LOCAL-EVI-NEUTRAL-TEST-v1",
                "evidence_refs":["EVI-MISSING"],"source_fact":"test neutral EVI"
              }
            }
          },
          "runners":[{"runner_id":"1","name":"Real-race degraded fixture"}]
        }
        out=materialize_request(req,["HPI-L","EVI/CEV","TPI-L"])
        self.assertTrue(out["full_terminalization"])
        self.assertFalse(out["full_numerical_calculation"])
        self.assertEqual(out["runners"][0]["canonical_components"]["TPI-L"]["terminal_status"],"RULED-HOLD")

    def test_local_krs_bridge_is_explicit_and_provenanced(self):
        r=self.runner()
        prov={k:{"rule_id":"LOCAL-HSV-SELFTEST-v1","evidence_refs":["K1"]} for k in HSV_KEYS+STATIC_KEYS}
        bridge={"bridge_id":"LOCAL-KRS-BRIDGE-SELFTEST-v1","family":"LOCAL",
          "technical_proxy_mode":True,
          "proxy_reason":"fixture explicitly exercises terminal-complete technical proxy transport",
          "runners":{"1":{
          "hsv":{k:60 for k in HSV_KEYS},"static":{k:60 for k in STATIC_KEYS},
          "provenance":prov,"uncertainty_scale":50
        }}}
        req={"race_id":"LOCAL-SELFTEST-R1","race":{"race_id":"LOCAL-SELFTEST-R1","venue":"OHI","surface":"dirt","distance":1200},"runners":[r],"local_krs_bridge":bridge}
        out=build_krs(req)
        self.assertEqual(len(out["krs_input_data"]["horses"][0]["hsv"]),30)
        self.assertEqual(len(out["krs_input_data"]["horses"][0]["static"]),11)
        self.assertTrue(out["local_krs_input_sha256"])

    def test_jra_or_missing_bridge_rejected(self):
        with self.assertRaises(LocalKRSBridgeError):
            build_krs({"race_id":"X","runners":[self.runner()],"local_krs_bridge":{"bridge_id":"BAD","family":"JRA","runners":{}}})

if __name__=="__main__":
    unittest.main()

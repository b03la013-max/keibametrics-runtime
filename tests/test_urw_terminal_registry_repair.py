import unittest
from runtime.local_evidence_to_base_production import materialize_request, WEIGHTS
from runtime.formal_request_validator import validate_canonical_index_components, FormalValidationError

def f(score=70):
    return {"score":score,"rule_id":"URW-TEST-EVIDENCE-v1","evidence_refs":["E1"],"source_fact":"fixture","source_timestamp":"2026-09-23T12:00:00+09:00"}

class URWTerminalRegistryRepairTest(unittest.TestCase):
    def base(self):
        feats={}
        for spec in WEIGHTS.values():
            for k in spec:
                feats[k]=f()
        return {
          "race_id":"URW-TERMINAL-TEST",
          "venue_formula_registry":{
            "registry_id":"URW-VENUE-FORMULA-TERMINAL-REGISTRY-v1.0-20260923",
            "allowed_rule_ids":{
              "EVI/CEV":["URW-v1.6-EVI-CEV-NEUTRAL-MISSING-v1"],
              "SRI-L":["URW-v1.6-SRI-L-RULED-HOLD-v1"]
            }
          },
          "runners":[{
            "runner_id":"1","name":"Fixture","evidence_features":feats,
            "canonical_external_indices":{
              "EVI/CEV":{
                "terminal_status":"RULED-NEUTRAL","transport_value":52,
                "rule_id":"URW-v1.6-EVI-CEV-NEUTRAL-MISSING-v1",
                "evidence_refs":["EVI-MISSING"],"source_fact":"missing EVI -> canon neutral with DCR consequence",
                "venue_formula_registry":"URW-VENUE-FORMULA-TERMINAL-REGISTRY-v1.0-20260923"
              },
              "SRI-L":{
                "terminal_status":"RULED-HOLD",
                "rule_id":"URW-v1.6-SRI-L-RULED-HOLD-v1",
                "evidence_refs":["SRI-SEMANTIC"],"source_fact":"semantic SRI resolved; numeric formula not registered",
                "venue_formula_registry":"URW-VENUE-FORMULA-TERMINAL-REGISTRY-v1.0-20260923"
              }
            }
          }]
        }

    def test_materializer_distinguishes_formal_and_transport(self):
        out=materialize_request(self.base(),["HPI-L","TPI-L","EVI/CEV","SRI-L"])
        self.assertTrue(out["full_terminal_resolution"])
        self.assertFalse(out["full_numerical_calculation"])
        sri=out["runners"][0]["canonical_components"]["SRI-L"]
        self.assertEqual(sri["terminal_status"],"RULED-HOLD")
        self.assertNotIn("value",sri)
        self.assertEqual(sri["terminal_status"],"RULED-HOLD")

    def test_validator_terminal_mode_accepts_hold(self):
        out=materialize_request(self.base(),["HPI-L","TPI-L","EVI/CEV","SRI-L"])
        cc=out["runners"][0]["canonical_components"]
        # Validator production manifest uses legacy names; build a complete fixture
        aliases=["HPI","SSI","CFI","RFI","BVI","JTI","CSI","TRI","BWI","GCI","PRI","KGI","VMI","DCR","TPI","ZAI_WIN","ZAI_PLACE","SRI","F3S","T3I"]
        sample=cc["HPI-L"]
        full={}
        for k in aliases:
            full[k]=dict(sample)
        full["SRI"]={
          "terminal_status":"RULED-HOLD",
          "rule_id":"URW-v1.6-SRI-L-RULED-HOLD-v1","mapping_version":"LOCAL-BASE-INDEX-MAPPING-REGISTRY-v1.0-20260922",
          "evidence_refs":["SRI-SEMANTIC"],"source_fact":"held"
        }
        req={"numeric_calculation_requirement":"FULL_TERMINAL_REQUIRED","runners":[{"runner_id":"1","canonical_components":full}]}
        meta=validate_canonical_index_components(req,["1"])
        self.assertEqual(meta["canonical_terminal_non_numeric_count"],1)
        req["numeric_calculation_requirement"]="FULL_REQUIRED"
        with self.assertRaises(FormalValidationError):
            validate_canonical_index_components(req,["1"])

if __name__=="__main__":
    unittest.main()

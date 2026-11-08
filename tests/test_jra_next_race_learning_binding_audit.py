import json
from pathlib import Path
import unittest

from runtime.jra_next_race_learning_binding_audit import (
    audit_learning_consumption, audit_official_observation_consumption,
)


class LearningBindingAuditTest(unittest.TestCase):
    def setUp(self):
        self.race = "KM-JRA-TKY-20261018-R02"
        self.state = {"state_id": "s1", "race_id": "KM-JRA-TKY-20261018-R01",
                      "effective_time": "2026-10-18T10:00:00+09:00",
                      "sha256": "abc"}
        self.kw = {"race_id": self.race,
                   "source_freeze": "2026-10-18T10:30:00+09:00",
                   "prediction_cutoff": "2026-10-18T10:50:00+09:00"}

    def test_saved_is_not_consumed(self):
        report = audit_learning_consumption(**self.kw, learning_states=[self.state])
        self.assertEqual(report["eligible_state_ids"], ["s1"])
        self.assertEqual(report["input_bound_state_ids"], [])
        self.assertEqual(report["status"], "NEXT_RACE_CONSUMPTION_UNVERIFIED")

    def test_binding_requires_matching_sha(self):
        report = audit_learning_consumption(**self.kw, learning_states=[self.state],
            prediction_input={"learning_state_bindings": [{"state_id": "s1", "state_sha256": "wrong"}]})
        self.assertEqual(report["input_bound_state_ids"], [])
        report = audit_learning_consumption(**self.kw, learning_states=[self.state],
            prediction_input={"learning_state_bindings": [{"state_id": "s1", "state_sha256": "abc"}]})
        self.assertEqual(report["input_bound_state_ids"], ["s1"])
        self.assertEqual(report["status"], "INPUT_BINDING_REFERENCE_OBSERVED_UNVERIFIED")

    def test_post_freeze_and_same_race_rejected(self):
        late = dict(self.state, effective_time="2026-10-18T10:31:00+09:00")
        same = dict(self.state, state_id="s2", race_id=self.race)
        report = audit_learning_consumption(**self.kw, learning_states=[late, same])
        self.assertEqual(len(report["rejected"]), 2)

    def test_missing_digest_is_not_eligible(self):
        state = dict(self.state)
        state.pop("sha256")
        report = audit_learning_consumption(**self.kw, learning_states=[state])
        self.assertEqual(report["eligible_state_ids"], [])
        self.assertEqual(report["rejected"][0]["reason"], "STATE_DIGEST_MISSING")

    def test_invalid_temporal_input_fails_closed(self):
        with self.assertRaises(ValueError):
            audit_learning_consumption(**dict(self.kw, source_freeze="2026-10-18T11:00:00+09:00"),
                                       learning_states=[])
        with self.assertRaises(ValueError):
            audit_learning_consumption(**dict(self.kw, source_freeze="2026-10-18T10:30:00"),
                                       learning_states=[])


if __name__ == "__main__":
    unittest.main()


def test_existing_official_observations_are_proven_separately_from_learning_state():
    import pytest

    root = Path(__file__).resolve().parents[1]
    for number, expected in ((1, (0, 0)), (6, (45, 44))):
        race = f"KM-JRA-FKS-20261108-R{number:02d}"
        final_path = root / "runtime/final_artifacts" / (race + ".json")
        original = final_path.read_bytes()
        final = json.loads(original)
        stage = final["final_prediction_package"]["execution_stage_manifest"]["SIGNED_SOURCE_RECEIPT_VERIFIED"]
        kwargs = {"source_freeze": stage["source_freeze_at"], "prediction_cutoff": final["prediction_cutoff"]}
        result = audit_official_observation_consumption(root, race, **kwargs)
        assert (result["signed_consumed_cell_count"], result["ablation_value_changed_count"]) == expected
        assert result["production_learning_state_use"] == "NOT_ESTABLISHED"
        assert not result["production_policy_changed"]
        assert final_path.read_bytes() == original
        with pytest.raises(ValueError, match="CALLER_CLOCK_MISMATCH"):
            audit_official_observation_consumption(root, race, **dict(kwargs, source_freeze=final["prediction_cutoff"]))

import unittest

from runtime.jra_next_race_learning_binding_audit import audit_learning_consumption


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

    def test_post_freeze_and_same_race_rejected(self):
        late = dict(self.state, effective_time="2026-10-18T10:31:00+09:00")
        same = dict(self.state, state_id="s2", race_id=self.race)
        report = audit_learning_consumption(**self.kw, learning_states=[late, same])
        self.assertEqual(len(report["rejected"]), 2)

    def test_invalid_temporal_input_fails_closed(self):
        with self.assertRaises(ValueError):
            audit_learning_consumption(**dict(self.kw, source_freeze="2026-10-18T11:00:00+09:00"),
                                       learning_states=[])
        with self.assertRaises(ValueError):
            audit_learning_consumption(**dict(self.kw, source_freeze="2026-10-18T10:30:00"),
                                       learning_states=[])


if __name__ == "__main__":
    unittest.main()

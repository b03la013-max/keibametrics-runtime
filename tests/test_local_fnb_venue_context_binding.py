"""Synthetic transport correctness only; no LIVE Context/model acceptance."""
import copy
import unittest

from runtime.local_fnb_venue_context_binding import (
    CANON, MODULE_FIELDS, RUNNER_MODULES, SCHEMA, FnbVenueContextError,
    bind_fnb_frozen_venue_context, canonical_sha256,
)


class FnbContextBindingTests(unittest.TestCase):
    def setUp(self):
        self.producer = {"model_id": "SYNTHETIC_CORRECTNESS_NOT_ADOPTED",
                         "version": "test", "code_sha256": "a" * 64,
                         "adoption_receipt_sha256": "b" * 64}
        self.policy = {"family_authority_basis": "CURRENT_TEST_AUTHORITY",
                       "fnb_venue_context_producer": self.producer}
        self.request = {"venue_id": "FNB", "race_id": "TEST-FNB-R01", "race_date": "2026-11-03",
                        "race_no": 1, "prediction_cutoff": "2026-11-03T12:00:00+09:00",
                        "scheduled_post_at": "2026-11-03T12:10:00+09:00"}
        self.source = {"source_freeze_at": "2026-11-03T11:50:00+09:00",
                       "source_snapshot_sha256": "c" * 64,
                       "source_race_context": {"venue_id": "FNB", "race_date": "2026-11-03", "race_no": 1},
                       "sources": [{"source_id": "official", "official": True,
                                    "cutoff_relation": "PRE_CUTOFF",
                                    "fetched_at": "2026-11-03T11:50:00+09:00"}]}
        self.envelope = {"receipt_sha256": "d" * 64, "artifact": self.source}
        self.context = {"schema": SCHEMA, "canon": CANON, "authority_id": "CURRENT_TEST_AUTHORITY",
                        "venue_id": "FNB", "race_id": "TEST-FNB-R01", "race_date": "2026-11-03",
                        "race_no": 1, "producer": copy.deepcopy(self.producer),
                        "source_receipt_sha256": "d" * 64, "source_snapshot_sha256": "c" * 64,
                        "active_runner_ids": ["1", "3"],
                        "frozen_at": "2026-11-03T11:51:00+09:00",
                        "temporal_status": "PRESTART_FROZEN_NO_RESULT", "modules": {},
                        "front_group_density": self.obs("MEDIUM")}
        for name, fields in MODULE_FIELDS.items():
            row = {field: self.obs({"min": 1, "max": 2} if name == "REACHABLE_POSITION_RANGE"
                                   else "specific test observation; no LIVE evidence") for field in fields}
            self.context["modules"][name] = ({rid: copy.deepcopy(row) for rid in ["1", "3"]}
                                                 if name in RUNNER_MODULES else row)
        for field in ["track_state", "same_day_state"]:
            self.context["modules"]["CURRENT_TRACK_STATE_CLASSIFY"][field] = {
                "status": "UNKNOWN", "value": None, "reason": "no verified same-day prior result"}
        self.rehash()

    def obs(self, value):
        return {"status": "OBSERVED", "value": value,
                "observed_at": "2026-11-03T11:50:00+09:00", "source_ids": ["official"]}

    def rehash(self):
        self.context["sha256"] = canonical_sha256({k: v for k, v in self.context.items() if k != "sha256"})
        self.request["venue_prediction_context"] = self.context

    def run_binding(self):
        return bind_fnb_frozen_venue_context(self.request, self.envelope, self.policy, ["1", "3"],
                                            static_freeze_at="2026-11-03T11:52:00+09:00")

    def assert_hold(self, expected):
        self.rehash()
        with self.assertRaisesRegex(FnbVenueContextError, expected):
            self.run_binding()

    def test_verbatim_content_and_range_preserved_without_mutation(self):
        before = copy.deepcopy(self.context)
        got = self.run_binding()
        self.assertEqual(before, got)
        self.assertEqual(before, self.context)
        self.assertIsNot(got, self.context)
        self.assertEqual(got["modules"]["REACHABLE_POSITION_RANGE"]["3"]["early"]["value"],
                         {"min": 1, "max": 2})

    def test_self_asserted_producer_does_not_create_policy_binding(self):
        self.policy.pop("fnb_venue_context_producer")
        self.assert_hold("PRODUCER_NOT_BOUND")

    def test_producer_sha_mismatch(self):
        self.context["producer"]["code_sha256"] = "e" * 64
        self.assert_hold("PRODUCER_BINDING_MISMATCH")

    def test_missing_authority_not_accepted_as_none_equals_none(self):
        self.policy.pop("family_authority_basis")
        self.context.pop("authority_id")
        self.assert_hold("AUTHORITY_MISMATCH")

    def test_other_race_or_venue_rejected(self):
        for key, value in [("race_no", 2), ("race_date", "2026-11-04"),
                           ("race_id", "OTHER"), ("venue_id", "KAW"), ("race_no", True)]:
            with self.subTest(key=key, value=value):
                original = self.context[key]
                self.context[key] = value
                self.assert_hold("RACE_IDENTITY_MISMATCH")
                self.context[key] = original

    def test_both_source_bindings_required(self):
        for key in ["source_receipt_sha256", "source_snapshot_sha256"]:
            original = self.context[key]
            self.context[key] = "f" * 64
            self.assert_hold("SOURCE_BINDING_MISMATCH")
            self.context[key] = original

    def test_cancelled_or_missing_runner_rejected_without_renumbering(self):
        for ids in [["1", "2"], ["1"], ["1", "3", "3"]]:
            self.context["active_runner_ids"] = ids
            self.assert_hold("ACTIVE_UNIVERSE_MISMATCH")

    def test_source_context_static_cutoff_order_enforced(self):
        for value in ["2026-11-03T11:49:00+09:00", "2026-11-03T11:53:00+09:00",
                      "2026-11-03T12:00:00+09:00"]:
            self.context["frozen_at"] = value
            self.assert_hold("TEMPORAL_BINDING_MISMATCH")

    def test_mechanism_name_list_cannot_substitute_for_results(self):
        self.context["modules"] = list(MODULE_FIELDS)
        self.assert_hold("REQUIRED_MODULES_MISMATCH")

    def test_omitted_or_extra_mechanism_rejected(self):
        self.context["modules"].pop("FPR_FNB")
        self.assert_hold("REQUIRED_MODULES_MISMATCH")

    def test_per_runner_mechanism_cannot_hide_runner(self):
        self.context["modules"]["FPR_FNB"].pop("3")
        self.assert_hold("RUNNER_MODULE_UNIVERSE_MISMATCH")

    def test_acquisition_does_not_substitute_for_maintenance(self):
        self.context["modules"]["FPR_FNB"]["1"].pop("maintenance")
        self.assert_hold("MODULE_FIELDS_MISMATCH")

    def test_empty_or_status_only_payload_rejected(self):
        for value in [None, {}, [], True, "", "PASS", "COMPLETE", {"status": "PASS"}]:
            self.context["modules"]["FPR_FNB"]["1"]["acquisition"]["value"] = value
            self.assert_hold("FULL_CONTENT_REQUIRED")

    def test_unknown_stays_null_and_is_not_weak(self):
        self.context["modules"]["FPR_FNB"]["1"]["maintenance"] = {
            "status": "UNKNOWN", "value": None, "reason": "no eligible maintenance observation"}
        self.rehash()
        self.assertEqual(self.run_binding()["modules"]["FPR_FNB"]["1"]["maintenance"]["value"], None)

    def test_unknown_with_score_is_rejected(self):
        self.context["modules"]["FPR_FNB"]["1"]["maintenance"] = {
            "status": "UNKNOWN", "value": 0, "reason": "no observation"}
        self.assert_hold("UNKNOWN_MUST_REMAIN_EXPLICIT_NULL")

    def test_all_unknown_carrier_not_context_ready(self):
        self.context["front_group_density"] = {"status": "UNKNOWN", "value": None, "reason": "not observed"}
        for module in self.context["modules"].values():
            rows = module.values() if all(isinstance(v, dict) and "status" not in v for v in module.values()) else [module]
            for row in rows:
                for key in row:
                    row[key] = {"status": "UNKNOWN", "value": None, "reason": "not observed"}
        self.assert_hold("EMPTY_EVIDENCE_CARRIER_FORBIDDEN")

    def test_unbound_source_id_rejected(self):
        self.context["modules"]["FPR_FNB"]["1"]["acquisition"]["source_ids"] = ["not-official"]
        self.assert_hold("SOURCE_REFERENCE_MISMATCH")

    def test_malformed_source_id_controlled_error(self):
        self.context["modules"]["FPR_FNB"]["1"]["acquisition"]["source_ids"] = [{}]
        self.assert_hold("SOURCE_REFERENCE_MISMATCH")

    def test_postfreeze_observation_rejected(self):
        self.context["modules"]["FPR_FNB"]["1"]["acquisition"]["observed_at"] = "2026-11-03T11:52:00+09:00"
        self.assert_hold("POSTFREEZE_OBSERVATION")

    def test_first_race_cannot_hide_current_bias_in_nested_carrier(self):
        self.context["modules"]["CURRENT_TRACK_STATE_CLASSIFY"]["same_day_state"] = self.obs("FRONT_BIAS_OBSERVED")
        self.assert_hold("SAME_DAY_BIAS_REQUIRES_VERIFIED_PRIOR_RESULT")

    def test_same_or_future_result_is_rejected_by_existing_temporal_guard(self):
        self.source["fnb_same_day_result_observations"] = [{
            "race_no": 1, "race_date": "2026-11-03", "venue_id": "FNB",
            "official_result_verified": True, "signed_result_receipt_verified": True,
            "first_observed_at": "2026-11-03T11:49:00+09:00"}]
        self.assert_hold("SAME_DAY_RESULT_NOT_PRIOR_RACE")

    def test_verified_prior_result_accepted_only_for_later_race(self):
        self.request["race_no"] = self.context["race_no"] = self.source["source_race_context"]["race_no"] = 2
        self.source["fnb_same_day_result_observations"] = [{
            "race_no": 1, "race_date": "2026-11-03", "venue_id": "FNB",
            "official_result_verified": True, "signed_result_receipt_verified": True,
            "first_observed_at": "2026-11-03T11:49:00+09:00"}]
        self.context["modules"]["CURRENT_TRACK_STATE_CLASSIFY"]["same_day_state"] = self.obs("PRIOR_RACE_CONTEXT_UNCALIBRATED")
        self.rehash()
        self.assertEqual(self.run_binding(), self.context)

    def test_prior_result_observed_after_source_freeze_rejected(self):
        self.request["race_no"] = self.context["race_no"] = self.source["source_race_context"]["race_no"] = 2
        self.source["fnb_same_day_result_observations"] = [{
            "race_no": 1, "race_date": "2026-11-03", "venue_id": "FNB",
            "official_result_verified": True, "signed_result_receipt_verified": True,
            "first_observed_at": "2026-11-03T11:52:00+09:00"}]
        self.assert_hold("RESULT_OBSERVED_AFTER_FROZEN")

    def test_actual_source_fetch_after_context_cannot_be_self_backdated(self):
        self.source["sources"][0]["fetched_at"] = "2026-11-03T11:52:00+09:00"
        self.assert_hold("REFERENCED_SOURCE_POST_SOURCE_FREEZE")

    def test_auxiliary_after_source_freeze_requires_new_immutable_source(self):
        # Even though 11:50:30 is before Context 11:51, it is outside the
        # immutable SOURCE 11:50 and cannot backfill that older Freeze.
        self.source["sources"][0]["fetched_at"] = "2026-11-03T11:50:30+09:00"
        self.assert_hold("REFERENCED_SOURCE_POST_SOURCE_FREEZE")

    def test_observation_time_cannot_be_after_the_source_fetch(self):
        self.context["modules"]["FPR_FNB"]["1"]["acquisition"]["observed_at"] = "2026-11-03T11:50:10+09:00"
        self.assert_hold("OBSERVATION_AFTER_REFERENCED_FETCH")

    def test_derivation_clock_separated_from_event_and_fetch_time(self):
        row = self.context["modules"]["FPR_FNB"]["1"]["acquisition"]
        row.update(status="DERIVED", derivation="explicit test-only computation", derived_at="2026-11-03T11:50:30+09:00")
        self.rehash()
        self.assertEqual(self.run_binding(), self.context)
        row["derived_at"] = "2026-11-03T11:49:00+09:00"
        self.assert_hold("DERIVATION_CLOCK_MISMATCH")

    def test_old_event_observed_before_later_fetch_is_not_future_leakage(self):
        self.context["modules"]["FPR_FNB"]["1"]["acquisition"]["observed_at"] = "2026-10-30T10:00:00+09:00"
        self.rehash()
        self.assertEqual(self.run_binding(), self.context)

    def test_explicit_source_ineligibility_cannot_be_dropped_in_context(self):
        self.source["sources"][0]["post_cutoff_or_ineligible"] = True
        self.assert_hold("REFERENCED_SOURCE_NOT_AVAILABLE_AT_FREEZE")

    def test_duplicate_source_ids_are_ambiguous(self):
        self.source["sources"].append(copy.deepcopy(self.source["sources"][0]))
        self.assert_hold("DUPLICATE_SOURCE_ID")

    def test_source_id_must_be_typed_nonempty_string(self):
        for value in [None, 1, True, "", " "]:
            self.source["sources"][0]["source_id"] = value
            self.assert_hold("TYPED_SOURCE_ID_REQUIRED")

    def test_explicit_stale_failed_or_noncurrent_snapshot_is_not_promoted(self):
        for key, value in [("stale", True), ("current", False), ("status", "FETCH_FAILED"),
                           ("http_status", 403), ("http_status", "200")]:
            self.source["sources"][0][key] = value
            self.assert_hold("REFERENCED_SOURCE_NOT_AVAILABLE_AT_FREEZE")
            self.source["sources"][0].pop(key)

    def test_grouped_position_cannot_be_collapsed_to_point(self):
        for value in [1.5, 1, {"min": 0, "max": 2}, {"min": 2, "max": 1}, {"min": True, "max": 2}]:
            self.context["modules"]["REACHABLE_POSITION_RANGE"]["1"]["early"]["value"] = value
            self.assert_hold("RANGE_MUST_REMAIN_RANGE")

    def test_derived_without_rule_rejected(self):
        self.context["modules"]["FPR_FNB"]["1"]["acquisition"]["status"] = "DERIVED"
        self.assert_hold("DERIVATION_REQUIRED")

    def test_postcutoff_label_rejected(self):
        self.context["temporal_status"] = "POSTCUTOFF_DIAGNOSTIC"
        self.assert_hold("PRESTART_STATUS_REQUIRED")

    def test_document_sha_tampering_rejected(self):
        self.context["modules"]["FPR_FNB"]["1"]["acquisition"]["value"] = "different evidence"
        with self.assertRaisesRegex(FnbVenueContextError, "DOCUMENT_SHA_MISMATCH"):
            self.run_binding()


if __name__ == "__main__":
    unittest.main()

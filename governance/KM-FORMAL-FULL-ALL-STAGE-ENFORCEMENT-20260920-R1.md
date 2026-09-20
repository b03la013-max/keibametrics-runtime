# KM-FORMAL-FULL-ALL-STAGE-ENFORCEMENT-20260920-R1

Status: ACTIVE / JRA-WIDE / CORRECTNESS-REPAIR / NON-PREDICTIVE / FAIL-CLOSED

## Purpose
Ensure that a JRA FORMAL-PRE-RACE run cannot claim FORMAL-FULL unless every mandatory pre-race execution stage is actually completed and externally evidenced. This repair does not change prediction formulas, venue rules, KRS physics, parameter-map calibration, ticket-selection policy, or capital policy.

## Mandatory rules

1. FORMAL-PRE-RACE always requires FULL numerical calculation.
   - index_provenance_ledger is mandatory.
   - numeric_calculation_requirement must resolve to FULL_REQUIRED.
   - calculated_count == required_count.
   - ruled_hold_count == 0.
   - not_applicable_count == 0.
   - unresolved_count == 0.
   - RULED-HOLD remains legal only for degraded / diagnostic operation, never FORMAL-FULL.

2. Temporal execution is fail-closed.
   - prediction_cutoff <= final_freeze_timestamp < scheduled_post_at.
   - external_dispatch_deadline_at < scheduled_post_at.
   - external dispatch must start before the dispatch deadline.
   - PRE_KRS/KRS must complete before FINAL submission.
   - FINAL receipt timestamp itself must be before scheduled_post_at.
   - A post-start receipt never upgrades a race to FORMAL-PRE-RACE.

3. Every mandatory pre-FINAL stage is recorded in execution_stage_manifest and bound into the signed FINAL payload.
   Mandatory stage evidence includes:
   - TEMPORAL_INPUT_VERIFIED
   - SOURCE_SNAPSHOT_VERIFIED
   - RUNNER_UNIVERSE_VERIFIED
   - INDEX_PROVENANCE_VERIFIED
   - STATIC_PREDICTION_VERIFIED
   - ROLE_REGISTRY_VERIFIED
   - PAIR_DISPOSITIONS_VERIFIED
   - THIRD_DISPOSITIONS_VERIFIED
   - BET_TYPE_DISPOSITIONS_VERIFIED
   - TICKET_CANONICAL_VERIFIED
   - CAPITAL_TOTAL_VERIFIED
   - FULL_NUMERICAL_CALCULATION_VERIFIED
   - PRE_KRS_VERIFIED
   - KRS_EXECUTION_VERIFIED
   - PRE_FINAL_TEMPORAL_VERIFIED
   - FINAL_VERIFIED

4. The runner emits execution_stage_manifest_sha256 and all_mandatory_pre_race_stages_verified.
   FORMAL-FULL requires every mandatory stage to be PASS.

## Acceptance proof

Implementation commit:
- eddf2a405d15a975723d057d321712cbcd1eab0e

Acceptance fixture:
- KM-ACCEPT-HSN-FULLSTAGE-20260920-T08

Acceptance GitHub Actions run:
- 35508594809
- conclusion: success

Observed acceptance facts:
- required_count: 60
- calculated_count: 60
- ruled_hold_count: 0
- unresolved_count: 0
- PRE_KRS receipt verified
- KRS requested_run_count: 5000
- KRS actual_run_count: 5000
- KRS receipt verified
- FINAL receipt verified
- execution_stage_manifest present
- all_mandatory_pre_race_stages_verified: true
- result: FULL_FORMAL_E2E_PASS

Receipt references from T08:
- PRE_KRS: 9c9bb53337df885a8e2bdcf7c1fd7021445ab4f5a3cf346893bce93a40e68018
- KRS: c6f531ec5749a0d3b39dab0a886cd6145a8ea74b69fe29c41d7d02b2469b31aa
- FINAL: a93270c8448a1c471ff7e215ae65de22926777a1c856c9ab9ca9caea06671fdd
- execution_stage_manifest_sha256: bd3610db7c1dfeea5ed355840da29bd4e1e7cb366ca585ea650603a50c4b85e7

## Result / settlement boundary
RESULT remains a post-race phase and is executed by the Formal Result Runner after an official result and settlement become available. RESULT PASS cannot retroactively repair a missing or late PRE_KRS/KRS/FINAL.

## Actual-ticket boundary
A complete KeibaMetrics recommendation pipeline is not the same as verified real-money purchase execution.
- FROZEN-RECOMMENDATION-PFS may be computed from frozen tickets.
- ACTUAL-PFS requires an independent Actual Ticket / purchase receipt.
- Until an authorized actual-purchase connector/receipt exists, FORMAL-FULL must not be represented as proof that wagers were actually purchased.

## Invariant
No silent bypass. If any required stage cannot be completed before the deadline, the system may preserve analysis and frozen prediction, but it must return EXECUTION-NOT-VERIFIED / FINAL-BLOCKED rather than FORMAL-FULL.

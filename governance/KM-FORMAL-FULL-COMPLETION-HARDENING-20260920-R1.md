# KM-FORMAL-FULL-COMPLETION-HARDENING-20260920-R1

Status: ACTIVE / CORRECTNESS-REPAIR / NON-PREDICTIVE / FAIL-CLOSED

## Purpose
Close the four execution gaps found in JRA Hanshin R11 Formal-Full review without changing prediction rules, numeric weights, KRS calibration, ticket policy, or capital policy.

## Mandatory Formal-Full conditions
A race may claim FORMAL-FULL only when all of the following are true before the applicable deadline:

1. BASE44_ORCHESTRATION_BOUND
   - A Base44 ExecutionSession is created first.
   - The request carries `orchestration_ref.authority=BASE44`, ExecutionSession ID, nonce, and created_at.
   - The same orchestration_ref is embedded in PRE_KRS and FINAL payloads so the signed external receipts cryptographically bind execution to that orchestration reference.

2. SOURCE_SNAPSHOT_SHA_VERIFIED
   - The canonical source_snapshot object is serialized as UTF-8 JSON with sort_keys=true and separators=(',',':').
   - SHA256 is recalculated by the formal validator.
   - Declared and recalculated hashes must match.
   - A declared-but-unrecomputed identifier is not sufficient.

3. FULL_NUMERICAL_CALCULATION_REQUIRED
   - For JRA Formal-Full, `numeric_calculation_requirement=FULL_REQUIRED`.
   - Every active runner must supply all 20 required canonical components:
     HPI, SSI, CFI, RFI, BVI, JTI, CSI, TRI, BWI, GCI, PRI, KGI, VMI,
     DCR, TPI, ZAI_WIN, ZAI_PLACE, SRI, F3S, T3I.
   - Each component requires finite 0-100 value, rule_id, mapping_version, non-empty evidence_refs, and source_fact.
   - Railway /calculate-jra-base must return calculated_count == required_count, ruled_hold_count == 0,
     not_applicable_count == 0, unresolved_count == 0.
   - RULED-HOLD may remain protocol-complete for degraded operation, but it cannot satisfy FORMAL-FULL.

4. ALL_BET_TYPES_DISPOSITION_VERIFIED
   - The request must declare available_bet_types.
   - Every available bet type must have exactly one disposition:
     PURCHASED / BUDGET-NONSELECTED / STRUCTURAL-INELIGIBLE /
     EVIDENCE-RANKED-LOWER / NOT-APPLICABLE / NO-BET.
   - Purchased bet types must exactly equal the bet types present in canonical tickets.
   - Available bet types and dispositions are embedded in FINAL signed payload.

5. SIGNED EXTERNAL EXECUTION
   - PRE_KRS signed receipt verified.
   - KRS run receipt verified; requested and actual run count checked.
   - FINAL signed receipt verified.
   - Engine SHA checked against declared canon.

## Temporal integrity
This repair is prospective. It does not rewrite frozen race artifacts.
HSN R11 2026-09-20 remains immutable as:
- pre-race external execution verified,
- index terminalization 320/320,
- actual numerical calculation 0/320,
- therefore not retrospectively upgraded to full numerical completion.

## Acceptance
Acceptance fixture: KM-ACCEPT-HSN-FULLPIPELINE-20260920-T05
- Base44 ExecutionSession created before request.
- Canonical Source Snapshot SHA recalculation passed.
- 16 runners x 20 indices = 320/320 CALCULATED.
- 0 RULED-HOLD / 0 NOT-APPLICABLE / 0 UNRESOLVED.
- 9 available bet types disposition-complete.
- PRE_KRS signed receipt verified.
- KRS 5000/5000 signed receipt verified.
- FINAL signed receipt verified.
- Railway external logs confirm the full call chain.

This is a correctness/operational repair only. It does not change any prediction formula, coefficient, KRS probability interpretation, or capital rule.

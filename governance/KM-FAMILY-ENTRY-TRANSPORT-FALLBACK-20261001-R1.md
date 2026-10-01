# KM-FAMILY-ENTRY-TRANSPORT-FALLBACK-20261001-R1

Status: ACTIVE / FAMILY-COMMON / C1 EXECUTION CORRECTNESS / NON-PREDICTIVE / NON-NUMERICAL / FAIL-CLOSED

## Purpose

Protect the Venue Chat -> Formal Orchestrator entry boundary. A failure to submit the primary Single-Entry intent before a GitHub commit is created must not silently degrade a Formal request into SOURCE-only, narrative-only, or unverified execution.

## Authorized sequence

1. Attempt the current Single-Entry path: `runtime/formal_intents/*.json`.
2. If and only if submission fails before GitHub commit creation, immediately retry the same semantic Formal payload through the existing compatibility path: `runtime/family_requests/*.json` with phase `FORMAL`.
3. Reuse the same explicit `execution_id` and the durable verified SOURCE checkpoint for that execution.
4. Verify the semantic payload hash before the legacy Formal runner may proceed.
5. Continue the existing authorized lifecycle through numerical terminalization, PRE_KRS, KRS, MEC, Capital, FINAL ticket freeze, and Signed FINAL.
6. If the fallback submission is also unavailable or rejected, fail closed as `ENTRY-TRANSPORT-BLOCKED`.

## Non-negotiable invariants

- No Prediction rule change.
- No numerical mapping or parameter change.
- No KRS physics change.
- No MEC-R3 or Capital policy change.
- No silent removal of Static, Role, Pair, Third, run_count, seed, or Capital fields to make transport succeed.
- No encoding, obfuscation, alternate credentials, or other attempt to bypass an external platform safety control.
- SOURCE-only success is not Formal completion.
- Narrative output is not a substitute for execution evidence.
- A retry may change transport metadata only; semantic payload must remain hash-identical.
- If the required semantic payload itself cannot be transported through an authorized connector, the correct terminal state is fail-closed, not a fabricated FINAL.

## Failure classification

`ENTRY_TRANSPORT` is distinct from Prediction, Runtime, KRS, Decision/Capital, and FINALIZATION failures. The first failed phase is the chat-to-execution submission boundary; the last successful stage must be recorded explicitly.

## Regression

`tests/test_entry_transport_fallback.py` requires:
- same execution ID,
- semantic hash preservation,
- rejection of semantic loss,
- rejection of safety-bypass flags,
- frozen Static requirement.

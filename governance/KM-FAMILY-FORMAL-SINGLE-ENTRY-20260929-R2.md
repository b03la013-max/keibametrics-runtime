# KM-FAMILY-FORMAL-SINGLE-ENTRY-20260929-R2

## Status

ACTIVE / FAMILY-COMMON EXECUTION-CORRECTNESS / LOCAL / CHECKPOINT-INTEGRITY / NON-PREDICTIVE / NON-NUMERICAL / FAIL-CLOSED

## Purpose

A Venue Chat should submit one Formal intent. Internally SOURCE and FORMAL remain independently signed phases, but the user or chat surface does not manually build a two-request handoff.

R2 closes the remaining integrity gaps discovered by real live mechanical acceptance:

1. SOURCE checkpoint reuse is allowed only when its immutable source basis matches.
2. Fresh FORMAL is automatically bound to the exact durable Signed SOURCE receipt, snapshot and SOURCE checkpoint manifest.
3. Immutable FORMAL reuse is allowed only when its semantic execution basis and durable SOURCE binding match.
4. Retry metadata may change without rerunning KRS; prediction/decision semantics may not.
5. Legacy FORMAL checkpoints that predate semantic-basis storage are never silently upgraded or rewritten.
6. Archived acceptance fixtures cannot claim FORMAL-PRE-RACE or OOS evidence.
7. Full lifecycle execution never means Strict Full Numerical authority when that authority is unavailable.

## Source checkpoint basis

For new SOURCE checkpoints the orchestrator stores `source_checkpoint_basis.json`.

The basis includes family, race identity, venue/date/race number, prediction cutoff and any explicit source-manifest hash. A changed basis requires a new Execution ID.

## Static-to-SOURCE binding

Before FORMAL, the orchestrator resolves the durable Signed SOURCE and writes its receipt SHA, snapshot SHA and checkpoint-manifest SHA into Static Prediction provenance. The FORMAL runner fails closed if the required binding is absent or mismatched.

## FORMAL semantic basis

For every new successful FORMAL checkpoint the orchestrator stores `formal_checkpoint_basis.json`.

The semantic hash includes execution-relevant prediction, role/pair/third, numerical terminalization inputs, KRS bridge, simulation seed/run count, Capital and ticket-construction inputs. Only retry/transport metadata are excluded.

If the basis differs, the old Signed FINAL is not returned and the caller must create a new Execution ID.

## Numerical truthfulness

LOCAL Production Numerical Authority remains NOT_READY because all 63 component score rules remain unbound.

The verified T02 mechanical acceptance therefore used:

- 348 required index cells;
- 348 terminalized;
- 0 CALCULATED;
- 348 RULED-HOLD;
- 0 unresolved;
- explicit TECHNICAL_PROXY_DIAGNOSTIC KRS input;
- KRS actual run count 5,000;
- Production MEC-R3 unchanged;
- Production Capital unchanged.

This verifies execution mechanics only. It is not unknown-future prediction evidence and does not promote any numerical model.

## Acceptance evidence

Fresh execution: GitHub Actions run 36488158808.

- SOURCE receipt: `373b23399df422c7b40bffcb661296e06b265f59d40ea6fc0aaba43a8254b75e`
- SOURCE snapshot: `cf525e7b406a2c49ae891b437dcad8432b656400ca82a91199de8680ad5fdfcf`
- SOURCE checkpoint manifest: `9432a2108ce2feb2eeb44060ae232353aa677c54d3a0d2a968731628811044d1`
- FORMAL checkpoint manifest: `2c1e398abbede62ff01d870b677d8058cc198507a0b5483da214970f55d67ac9`
- FORMAL semantic basis: `9d04f186a0ca9898ca0128d811547b08a3ba6a1cf7cd82ac999b4ebaf895e123`
- KRS receipt: `18bb92ab93b22260acd8f492b69fe6711b5bd82d3c97f00a793c2ed7a7dc387e`
- MEC-R3 SHA: `faeb30ee84c608ac11de5c59222ec118d7d94c7a12688ca5f2bcfaca3ddef4f7`
- Signed FINAL receipt: `f9228fa91022a634e68ec368dcc3dadc72a633128859505da1925102367d7f08`

Retry-only execution: GitHub Actions run 36488377428.

The semantic and SOURCE bases matched; the existing FORMAL run was returned as `ALREADY_COMPLETE / REUSED_IMMUTABLE`. KRS was not rerun.

## Freeze

This revision changes no predictive formula, numerical weight, Engine physics, parameter_map, MEC-R3, Capital policy or Venue prediction canon.

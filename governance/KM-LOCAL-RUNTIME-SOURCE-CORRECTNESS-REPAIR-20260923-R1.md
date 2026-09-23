# KM-LOCAL Runtime / Source Correctness Repair 2026-09-23 R1

## Status

ACTIVE / PRODUCTION-EXECUTION-CORRECTNESS / NON-NUMERICAL / BEHAVIOR-PRESERVING / FAIL-CLOSED

## Root cause

Urawa R8 exposed two independent execution defects:

1. NAR race-card declared horses and active betting runners were treated as one universe. A scratched horse could remain in the race-card table and therefore cause REQUEST vs OFFICIAL universe mismatch.
2. LOCAL Railway uses an image bootstrap that downloads runtime files from the commit in `KM_LOCAL_GITHUB_REV`. Updating GitHub main alone did not update the deployed runtime. Re-running immediately after a GitHub fix could therefore execute the old parser.

Neither defect is a prediction-model defect.

## Corrective architecture

### Runtime release integrity

- Canonical runtime revision is declared in the Family Runtime Contract.
- FORMAL Runner calls `/health` before Source Acquisition.
- It verifies:
  - runtime READY,
  - deployed GitHub revision equals canonical runtime release revision,
  - app_v15 hash,
  - legacy app hash,
  - source acquisition hash,
  - NAR source manifest hash,
  - NAR runner-universe parser hash.
- A stale request-local runtime revision fails with `REQUEST_RUNTIME_REVISION_STALE`.
- A deployed revision mismatch fails with `RUNTIME_REVISION_MISMATCH`.
- A file-hash mismatch fails with `RUNTIME_BUNDLE_HASH_MISMATCH`.
- Signed receipts carry GitHub revision and runtime bundle hashes.

### Declared versus Active Runner Universe

The source artifact preserves both:

- DECLARED: all horses officially listed on the race card, including scratches.
- ACTIVE: only current active betting/race runners.

A runner-status registry records status, reason, and evidence source. KRS and ticket construction use ACTIVE only.

The official active betting universe is required during FORMAL execution. Missing/ambiguous active-state evidence fails closed.

### Scratch / exclusion lineage

Race-card explicit cancellation markers and NAR official active betting data are reconciled. A scratched runner remains in DECLARED history but is removed from ACTIVE.

### Temporal integrity

FORMAL-PRE-RACE execution has a release deadline. When not supplied, it is derived as scheduled post time minus 120 seconds.

Deadline is rechecked:
- at execution start,
- after official Source/Race Identity,
- before PRE_KRS,
- after KRS,
- before FINAL,
- after FINAL.

Official NAR start time is compared with request scheduled post time. Material mismatch fails closed.

### Failure artifact persistence

Every completed stage writes an artifact immediately. Fail-closed runs preserve, when available:

- runtime preflight,
- deadline preflight,
- race identity preflight,
- signed SOURCE,
- declared/active runner-universe diagnostic,
- numerical authority preflight,
- numerical materialization summary,
- signed PRE_KRS,
- signed KRS,
- KRS utility,
- MEC plan and verification,
- capital decision,
- signed FINAL,
- failure diagnostic.

### Numerical authority

Current Evidence Feature Rule Registry is explicitly NON-NUMERICAL. It defines component sets and weights but not the raw-evidence-to-0..100 score rules for 63 required components.

Therefore:
- no freehand scores are permitted,
- Full Numerical Authority is NOT_READY,
- terminalized/degraded execution may continue,
- claiming FULL_NUMERICAL fails closed,
- no prediction weights or formulas are changed by this repair.

## Acceptance

- Regression: GitHub Actions 35837228499 — SUCCESS.
- Live runtime/hash + Urawa R8 scratch acceptance: 35836815875 — SUCCESS.
  - Declared runners: 12.
  - Active runners: 11.
  - #7 TRY AND ERROR: CANCELLED.
- Full post-start correctness replay: 35837306954 — SUCCESS.
  - KRS actual runs: 5,000.
  - Material coverage: 1.0.
  - Status: POST_START_REPLAY_E2E_PASS_NUMERICAL_DEGRADED.
- Negative full-numerical test: 35837370467 — expected FAIL_CLOSED.
- Negative stale-runtime test: 35837473643 — expected FAIL_CLOSED.
- Negative deadline test: 35837537866 — expected FAIL_CLOSED.

## Non-changes

This repair does not change:
- Production prediction weights,
- venue prediction formulas,
- KRS parameter map,
- W/P2/P3 policy,
- MEC semantics,
- capital policy,
- historical race freezes.

R8 remains prediction-complete/deadline-failed as originally frozen. Post-start acceptance does not retroactively promote it to FORMAL-PRE-RACE.

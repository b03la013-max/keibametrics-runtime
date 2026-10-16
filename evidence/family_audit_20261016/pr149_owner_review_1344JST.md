# PR #149 final audit and KAW R01 preflight — 2026-10-16

Observation window: approximately 13:31–13:44 JST, before the approved 14:00 JST scheduler window. This record supplements the existing family audit; it does not supersede authentic signed evidence or authorize a Production change.

**Decision: candidate correctness verified with the refund limitation below; Production merge HOLD.** Exact-HEAD Owner confirmation has not been attested. No independent Human Review is claimed. KAW R01 LIVE acceptance is PENDING because the approved execution window has not started.

## Owner review: four-file diff

Candidate: [PR #149](https://github.com/b03la013-max/keibametrics-runtime/pull/149), exact HEAD `57a0b4d21323a3c0b9015d6b575f228555a8f40d`, Draft/open. Diff: 4 files, 71 additions, 3 deletions.

| File | Effect to confirm |
|---|---|
| `.github/workflows/km-local-race-key-entry.yml` | Persist an acquired OFFICIAL_RESULT checkpoint even if RESULT has not yet been produced. Add derived ledgers only under the existing RESULT-directory condition. Use the existing bounded checkpoint publisher. |
| `runtime/aki_adaptive_oos_tracker.py` | Existing signed-settlement reconciliation requires finite, nonnegative int/float values, explicitly rejects bool/string/non-numeric values, and catches conversion overflow. Existing amount reconciliation remains. |
| `tests/test_aki_adaptive_oos_tracker.py` | Eight malformed signed-fixture cases cover both investment and return. |
| `tests/test_local_race_key_ingress.py` | Executes the actual persistence shell in temporary Git repositories for official-only, result-present and absent cases. No real publication. |

No dispatcher, SOURCE, Static, KRS, FINAL, Engine, parameter, Prediction, MEC or Capital implementation changed. No new validator was introduced. Historical signed FINAL/RESULT/Receipt and OOS ledger contents were not edited.

## Correctness evidence and limits

| Requirement | Finding |
|---|---|
| 1. Checkpoint before signed RESULT remains pending | PASS. OFFICIAL_RESULT is independently committed; absent RESULT remains WAITING_SIGNED_RESULT. Official request phase=RESULT denotes a future request, not a signed RESULT envelope. |
| 2. Do not confuse checkpoint with RESULT/Settlement | PASS. Existing manifest/hash/receipt/lineage verification and signed RESULT requirement remain. An isolated historical FORMAL+OFFICIAL_RESULT copy with RESULT omitted yielded zero eligible races, no errors and WAITING_SIGNED_RESULT. |
| 3. Reject invalid monetary values | PASS. Both monetary fields reject NaN, positive/negative Infinity, true/false, numeric strings, null, negative values, objects, arrays and an overflowing integer: 24 rejection probes, using the existing verifier. |
| 4. Accept valid payout/refund/zero amounts | Normal payout and zero-return acceptance PASS. Five matching nonnegative amount pairs pass, including (100,100) and (0,0). A full canonical losing-ticket fixture has investment 2,000 and return 0, and is OOS-eligible. **This does not establish end-to-end refund support:** existing refund/dead-heat cases intentionally stop with SPECIAL_OFFICIAL_OUTCOME_NEEDS_SETTLEMENT_SUPPORT; frozen-runner cancellation can stop earlier with OFFICIAL_RESULT_REFUND_REQUIRED. These guards are unchanged. |
| 5. Preserve signed history/OOS | PASS for this change and audit. Existing seven-race signed replay is part of the passing regression. No historical mutation or new OOS credit. |
| 6. Preserve KAW R01 pre-result path | PASS at diff/configuration level. Scheduler, authorization, resolve/entry jobs, SOURCE/Static/PRE_KRS/KRS/MEC/Capital/FINAL path are unchanged. Future LIVE success is not inferred from this. |

Existing exact-HEAD CI is 3/3 SUCCESS:
- [LOCAL Runtime Correctness Regression — 38847107954](https://github.com/b03la013-max/keibametrics-runtime/actions/runs/38847107954)
- [AKI Adaptive Purchase Shadow Acceptance — 38847107985](https://github.com/b03la013-max/keibametrics-runtime/actions/runs/38847107985)
- [LOCAL Race-Key Ingress Acceptance — 38847107934](https://github.com/b03la013-max/keibametrics-runtime/actions/runs/38847107934)

Local reuse of existing tests: **100 passed** in 2.47 seconds:
```
PYTHONPATH=runtime:. python -m pytest -q tests/test_aki_adaptive_oos_tracker.py tests/test_aki_adaptive_purchase_shadow.py tests/test_local_race_key_ingress.py tests/test_recovery_result_entry.py tests/test_execution_store.py tests/test_persist_local_checkpoints_scratch.py
```
Additional offline probes reused the existing implementation and fixtures; no validator or permanent test module was added. The workflow shell was also checked in four isolated repositories (official-only, result-only, both, neither), including a sentinel derived ledger: official-only never stages it. These counts overlap prior audit coverage and must not be added to that audit as unique coverage.

Integration inspected against main `6a1c7994cb7cb0ef3505e65d0a859e1460002416`: `git merge-tree --write-tree origin/main HEAD` returned zero conflicts and tree `506ac909295c76f3aefc48baea28633e2eee9df8`; `git diff --check` passed. Main-only movement since the candidate's base was the JRA daily status file. No branch ref or Production worktree was changed by this check. Any later merge requires a fresh head/base/CI check.

## Owner review: settlement stop conditions

Keep the existing HOLD/fail-closed behavior when:
- signed RESULT or required external receipt verification is missing;
- artifact/receipt hash, race identity, frozen FINAL binding or official-result authority disagrees;
- signed settlement is not COMPLETE with FROZEN-RECOMMENDATION authority, or either required monetary field is absent/invalid;
- a monetary value is not finite and nonnegative, or reconciled investment/return differ by more than the existing 0.001 tolerance;
- official payout is unresolved, special refund/dead-heat settlement lacks existing support, or frozen-ticket/temporal integrity fails.

Do not treat missing official payout as a legitimate zero return. Do not convert a pending checkpoint into COMPLETE, re-sign a historical result, or credit a new OOS observation merely to demonstrate this repair.

## Owner review: rollback and approval boundary

Rollback is a scoped revert of the four candidate files through the normal reviewed repository path. Preserve authentic OFFICIAL_RESULT checkpoints already acquired and all signed FINAL/RESULT/Receipt and OOS history. Do not delete evidence to simulate rollback. No Railway/Engine/parameter/signer redeploy is needed for this candidate.

GitHub review records remain empty; exact-HEAD Owner approval is NOT_ATTESTED. Existing owner-limited approval can cover only this exact four-file diff, the stop conditions above and this rollback. Prior PR #280/#284 approval does not approve PR #149. Repository branch settings do not supply missing human approval. No independent Human Review is inferred from AI audit or passing CI.

**Production merge remains HOLD.** A new execution risk near the live window requires deferral until KAW R01 completes. This report itself is neither approval nor merge authorization.

## KAW R01 production protection

- Activation enabled and unchanged: `KM_LOCAL_AUTONOMOUS_ENABLED=true`, read back from GitHub Actions variables UI.
- Approval: `profiles/local_autonomous_approvals/2026-10-16-KAW.json`; KAW R01 only, Phase B, max_dispatches=1.
- Plan SHA: `c316b452b4fba1bf40a334607469681442e56a1b4b7c80005955e48410ee60ba`.
- Existing scheduler: 14:00 / 14:05 / 14:10 JST, unchanged; no manual dispatch or new activation.
- Target: `KM-LOCAL-KAW-20261016-R01-LIVE-R1`; post 15:00 JST, prediction cutoff 14:58 JST.
- Current Authority: `KM-FAMILY-CURRENT-AUTHORITY-20261012-R51`.
- Existing dispatcher concurrency, claim-before-dispatch and no-resend-after-ambiguity behavior remain.
- Existing KAW source-only Static/29-index Owner authority and prediction-consumption gates remain unchanged.

Fresh existing Gateway assessment at **13:35:51 JST**: PASS, runtime READY, no mismatches/errors/missing capabilities/warnings.

| Component | Observed identity |
|---|---|
| Runtime deployment | `2f7ddb5d-6ebe-4de7-b3d5-c70833fd4460`, SUCCESS, online |
| Revision | `655530735f24cce78605dd1bd34843bdb2ea253d` |
| Bundle | `c6508062d02389fc32900a473a2eee83566a0f1132712033002dd79697d5d25a` |
| Wrapper | `ccb7af22beb13a1304715d967ceb32e48819f1b170bd1d53cd0ec87d6161974c` |
| Engine 1.1.0 | `9929df994aa7964173edef9af7e9a705628ce377babf22df3af4e280fc275421` |
| parameter 0.1-provisional | `d8c027ee5bcc8fd3d2c248e8059b341776be38910e833d7589f09ab817c161f5` |
| Signer | `KM-LOCAL-RUNTIME-ED25519-20260922` |

Railway usage limits were read back: Soft $5 / Hard $10 unchanged. No paid OpenAI API requests, purchases, new services, Production changes, deployments or activations were made. Only this evidence-only Draft branch is updated by this audit.

## LIVE acceptance: separate and still pending

No KAW R01 execution Receipt is claimed by this pre-window audit. Actual SOURCE, terminalized 29 indices (calculated vs neutral), Static, PRE_KRS, KRS, MEC, Capital, signed FINAL and user Delivery require read-back from this execution. Repository publication or a workflow summary alone is not user Delivery.

The existing bounded KAW 10/16 R01 delivery/result follow-up remains enabled and unchanged; no duplicate monitoring task was created. It is configured for 14:45 JST and three further hourly observations. Configuration is not proof a future run or Delivery will succeed.

If authenticated FINAL is available before 15:00, deliver its original Canonical ticket tree without reconstruction or selection changes. After post time, continue only through the existing official RESULT/Settlement/PFS/Learning path, preserving pending states and the frozen recommendation. Actual purchase remains unknown/none performed by this audit.

**At report time: PR adoption HOLD; KAW R01 LIVE PENDING. The priority remains pre-post signed FINAL and real user Delivery.**

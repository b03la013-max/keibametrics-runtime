# RESULT → Learning automatic recovery R3

Status: PARTIALLY IMPLEMENTED / NOT MERGE-READY / LIVE ACCEPTANCE PENDING.

Base: freshly verified main `c30d593c1183bcefde614cfe999b55ebcda937ef`.
Branch: `candidate/result-learning-resume-r3`. Carries the previous C1/R2 correction unchanged and adds executable downstream recovery. No main merge/deploy or Owner promotion.

## Fixed execution failure

Previously a signed RESULT followed by a Learning failure was preserved, but the next canonical call returned FORMAL_INCOMPLETE without a recovery route. A /verify transport failure immediately after /result could also lose the received envelope and allow another /result call.

Now the runner preserves a newly received RESULT before /verify, explicitly UNVERIFIED until verification succeeds. The orchestrator persists this noncompletion checkpoint with the exact original RESULT request digest. The same request automatically resumes the existing runner with that immutable envelope. The runner performs fresh external /verify, confirms race/phase/PASS, exact frozen FINAL receipt, official outcome/source/time/payouts, settlement investment/return and Frozen Recommendation PFS authority. It calls neither /result nor Prediction nor KRS on recovery. Expected settlement amounts are recomputed only to validate the stored financial binding; no new Production settlement or RESULT is issued.

After verification it runs the existing Reflection, research settlement, Learning and tracker terminal code. Research remains nonblocking for Production; Actual Purchase remains UNKNOWN without proof. Each attempt uses a new immutable recovery run identity derived from the parent checkpoint digest; previous runs and receipts remain intact. Completed duplicate requests return existing completion. Changed requests require the existing explicit correctness-revision rules.

The official-result watch automatically retries preserved RESULT transport failures within the existing gateway's max-attempt/backoff policy and its wait window. Correctness/signature/financial mismatch never becomes a transport retry. Durable watch beyond that workflow window is still unimplemented.

## Actual changed execution files

- `runtime/execution_store.py`: `verify_result_reuse`, frozen RESULT/FINAL/outcome/financial authority validation.
- `runtime/local_result_from_signed_final.py`: preserve unverified response before /verify; externally verify and reuse an existing RESULT; resume downstream without /result.
- `runtime/formal_execution_orchestrator.py`: automatic partial RESULT recovery, exact request basis, immutable recovery run publication and existing-policy transport continuation.
- `.github/workflows/km-local-execution-canary.yml`: actual network controls for safety-validated official NAR acquisition and fresh-process historical signed RESULT recovery in an isolated workspace. No API key, new signed RESULT, purchase or production tracker write.
- Tests: outcome/payout/FINAL/finance/authority/signature mutation rejection; verified and verification-pending checkpoint continuation; same-workflow transport recovery; actual external Runtime recovery control.

## Validation and its limits

Local selected suite: **253 passed, 2 skipped** (opt-in network tests). Real external /verify plus existing RESULT runner through Learning/tracker HOLD succeeded locally in a fresh isolated process before adding independent NAR acquisition to that same control: **1 PASS, 16.75 seconds**. The control prevents /result and all Prediction/KRS routes; original R8 signed RESULT is unchanged. It is a historical recovery control, not new future acceptance.

Local actual NAR fetch through the existing safety validator still fails DNS resolution. No proxy/DNS safety bypass is installed. The existing canary now runs actual R07 official acquisition and an R08 control that independently fetches official outcome/payouts, compares the original signed outcome, verifies the original FINAL/RESULT at the external Runtime, and executes downstream Learning in a fresh process. Remote results must be checked on this PR; they are not assumed PASS here.

All 183 protected Production/research files and nine Phase B.2 definition hashes are unchanged. No historical store, Production ledger, formula, physics, weights, policy, canon or Candidate definition was edited. No original OOS count is increased by the tests.

## Required final closure evidence

| Requirement | Current result |
| --- | --- |
| Owner Reality Audit / A-B-C | R2 exact R07/R08/R12 references retained; upstream generation remains unresolved |
| Real Production Owner / authority binding | Not registered; no authorized substitution |
| Prompt / schema / policy / model versions | Adapter enforcement retained; original complete Production generation prompt/model remains missing |
| Dedicated Project Service Account Secret | No key present. Current connector cannot select Service Account owner/permissions or securely transfer directly to actual Runtime Secret |
| Historical real API equivalence | Not run; no outcome-based fitting |
| One-trigger real pre-race Owner → KRS → FINAL | Blocked by Owner/credential dependencies; not replaced with synthetic success |
| Official result acquisition | Existing verified route wired; actual local DNS failure; actual remote test required |
| RESULT → Learning auto-resume | Implemented; external Runtime historical verification/recovery control executed, independent acquisition added to remote control |
| Stage completion / Numerical truthfulness | Existing gates retained and local regressions pass |
| Latency | 16.75-second downstream control observed; eight live pre-race stage latencies unmeasured |
| R09/R10/R11 / R07/R08/R12 | Existing refusal/immutable positive controls retained, local pass |
| Two-race stateful | Existing mechanical fresh-process isolation retained; real Owner two-race execution not run |
| Production Freeze | 183 protected files + nine Phase B.2 definitions unchanged |
| Remote CI | PR checks for this head are authoritative; no prior-head result substituted |
| Genuine unknown-future acceptance | Requires reviewed merge/deploy and actual one-trigger pre/post closure; pending |

Remaining work includes real Owner provenance and secure credentials, real outcome-blind equivalence/pre-race E2E, real two-race stateful test, factual SOURCE prewarm, cross-runtime concurrent deduplication and durable result watch beyond the workflow window. These prerequisites prohibit MERGE-READY or LIVE END-TO-END LIFECYCLE OPERATIONAL declarations.

Remote canary evidence: actual safety-validated official acquisition and the combined same-race R8 acquisition/signature/Learning recovery controls both PASS (2 tests, 2.02 seconds combined). All ten remote workflows PASS on the initially published R3 head. Final PR checks must be used for any subsequent head; the additional verification-pending preservation regression is retained. These controls do not prove real Prediction Owner equivalence or unknown-future completion.

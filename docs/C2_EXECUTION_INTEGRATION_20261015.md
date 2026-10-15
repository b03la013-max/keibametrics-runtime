# C2 execution integration / conflict resolution — 2026-10-15

Candidate only; OpenAI requests0, API budgetJPY0, no new paid resource, purchase, provider/key/cap change, main merge, deployment, Production Owner activation or new LIVE payload transfer.

## A–J disposition

| Deliverable | Status | Evidence and remaining boundary |
|---|---|---|
| A Main conflicts | COMPLETED locally / CANDIDATE pending remote CI | Integrate main389c2d53 into PR124 Candidate, retain Draft. Eight conflicts resolved; current main functionality wins in production execution/authority/result/worker files. Existing orchestrator functions AST-identical to main; production runner/workflow files byte-identical. No protected receipt/execution artifact changes. Per-file decisions in JSON evidence. |
| B Cross-Workflow budget | ZERO path VERIFIED; Positive Paid Path BLOCKED | Existing Runtime has no budget reservation capability and hosted checkouts have no common durable POSIX root. Existing Git retry/persistence is not an atomic pre-provider budget service. Do not pretend checkout-local ledgers share a budget. All real provider paths remain closed. Existing local ledger concurrency/crash/UNKNOWN tests retained; no new database/service. C2 offline Workflow concurrency serializes its own runs only; it is not a financial guarantee. |
| C Historical Resume | Workflow connection CANDIDATE / local VERIFIED | Existing C2 workflow now invokes existing resume-only CLI with digest-pinned repository artifact and independently pinned saved signer public anchor. No secrets, auth probes, generation, external /verify or paid fallback. Positive cached match uses unchanged output/freeze; default old real cohort legitimately HOLDs HISTORICAL_RESUME_BASIS_MISMATCH. Workflow success means a safe reuse/HOLD terminal, not real API/native schema acceptance. Actual GitHub workflow acceptance recorded on PR124 after push. |
| D Signature path | SIGNING-BLOCKED | Existing physical signer technically signs phase argument internally, but no C2 Shadow signing endpoint/capability or authorized scope is established. Existing final/formal endpoints require their own full lifecycle and cannot be used to manufacture a Shadow signature. Unsigned preparation and trust/receipt tamper checks retained. No key acquisition/generation/rotation or new Shadow signature. |
| E Schema | VERIFIED local / real API BLOCKED | Three saved real structural outputs contain free-text role and SELECTED/SUPPORTED pair states. Latest uses Common active states and native Pair/Third statuses plus full-universe/group rules. No semantic inference/migration, no original output overwrite. Matching request/config/schema required to resume; historical response is not latest-model generation. |
| F Production reliability | VERIFIED local; PR279 remains separate Candidate | Main Race matrix, SOURCE checkpoint, deadline guard, race-local runtime_out, separate RESULT workers, refund stop, Git checkpoint recovery, PFS/Learning preserved. Existing PR279 immutable FINAL/tree delivery regressions69PASS on its frozen checkout; no silent adoption/deployment of PR276/279. |
| G Zero paid request | VERIFIED within this work | No OpenAI request. Provider gate, concurrent zero-budget12 tasks/4 workers, duplicate reservations, forced crash17, UNKNOWN retention and 429 terminal tests retained. One LOCAL read-only GET /health verifies READY and saved public-key anchor match; no new race/Shadow payload sent. Historical/global actual billing remains UNKNOWN. |
| H GitHub | CANDIDATE / Draft | Candidate integrates latest observed main without merging into main. Final-head CI/Run/Artifact and conflict state recorded directly on PR124 after execution, not inferred from1359ef9b. |
| I Re-entry procedure | COMPLETED preparation / execution BLOCKED | Explicit authorization; reviewed shared durable store attached to every requester; provider-side usage/spend hard-cap check; pinned request/source/model/prompt/policy/schema/cutoff; token/request/race/retry ceilings; reserve and START before provider call; ambiguous completion held, no automatic rerun; legitimate Shadow signer. Current code still refuses positive paid reopening. |
| J External/owner blockers | BLOCKED / LIVE PENDING | Shared hosted store, provider cap attestation, authorized Shadow-signing scope, latest-native real response, promotion and genuine future acceptance unmet. No request to replenish this month. Owner action can wait; no paid test is required for this Candidate's offline work. |

## Conflict decisions and dependencies

1. Formal workflow: preserve main batch matrix, stable execution concurrency, RESULT separate from SOURCE/FORMAL and bounded persistence helper. Remove the old Candidate inline wait/staging-secret injection from this Production workflow. C2 uses its own existing workflow.
2. MEC acceptance: retain main's growing OOS rebuild versus immutable snapshot handling and COMPLETE_30 terminal; never edit OOS definitions/counters to clear CI.
3. Authority guard: retain current main CALCULATED_OR_RULED_NEUTRAL policy under existing explicit authority; no numerical formula or downstream prediction authorization change.
4. Orchestrator: preserve every existing main function, including deadline, phase exit status, race-local output and refund fail-closed. Inherited C2 helpers remain isolated; no automatic Candidate substitution into Production. The archived authority-pinned C1 helper remains a separately tested protocol, not an activated Owner.
5. Result/formal runners: main output isolation, persistence, signed result recovery and independent diagnostic retained.
6. Conflict tests: retain main's explicit frozen-Static requirement. Old Candidate tests assumed automatic Production Owner insertion; update them to assert no such fallback. Correct past-deadline fixture now also has a past cutoff. Legacy owner-protocol fixture pins R36 rather than mixing its v1.0 registry with R51; current numerical capability READY does not relabel its87 HOLD fixture cells as CALCULATED.

PR257's merged checkpoint/continuity work is inherited from main. PR276 and PR279 remain unmerged Drafts with their own changes; PR279 depends on276. This patch does not promote either branch or recreate its immutable FINAL/Delivery implementation. Its separate frozen regression is evidence for that component, not proof of its Production activation.

## Actual Workflow connection

`km-c2-staging-real-api-once.yml` is now named **C2 Candidate offline resume and zero-cost acceptance**. It is read-only, installs no service and receives no API secret. A reviewed commit SHA, artifact path and SHA bind the cache; saved trust-anchor SHA binds the public key. Ref/path are passed as argv/environment, not interpolated shell code. It checks SHADOW/non-production and authorization=false/monthly=race=retry=0 before resume. Missing artifact/hash mismatch is a failed job, not fallback. Contract/cache/schema HOLD is preserved as an explicit non-acceptance terminal; unexpected errors fail the job.

The default cache is PR279@5729e735's actual structural R07/R08/R12 comparison (SHA360e73c9...), anchor file SHAc76245e4.... The CLI validates SOURCE offline, then refuses current-schema/config mismatch. This is the correct zero-cost result, not a Prediction failure to hide. A workflow's green safety result cannot be called latest-native REAL API VERIFIED or SIGNED SHADOW VERIFIED.

The other existing manual staging workflow pins1033c818, before the zero-budget guard existed. Its Candidate job is explicitly disabled to prevent accidental use of that archived paid route. Historical workflow revisions cannot be rewritten: do not rerun old paid jobs. Main deployment/authority is untouched.

## Evidence and levels

Local combined C2/C1 Regression240PASS,2 explicit network SKIP; actual merged-main Runtime Correctness92PASS; additional Production reliability39PASS; PR279 frozen readback suite69PASS. Counts overlap and must not be summed into unique tests. No tests were added merely to inflate counts; stale contract fixtures were corrected to main's actual behavior. Workflow shell was executed locally and produced SAFE_HOLD / NOT_ACCEPTANCE, CLI exit2, no API fallback. Latest remote counts and required checks are separately recorded on PR124 after final HEAD exists.

LOCAL health2026-10-15T01:22:48Z: HTTP200 READY, physicalf0d23766, saved public anchor matches, no Shadow signer or budget endpoint advertised. `signed_receipt` being callable inside the physical process is not authorization to issue arbitrary new receipt phases. No Shadow signature was attempted.

CODE COMPLETE: Candidate conflict/zero-cost Resume integration only. CI VERIFIED: final-head Run required. EXTERNAL RUNTIME VERIFIED: health/public anchor only. REAL API VERIFIED: historical structural cohort only, not current schema. SIGNED SHADOW VERIFIED: NO. FORWARD OOS VERIFIED: no new record. PRODUCTION AUTHORIZED: C2 NO.

The attached KRS-Engine v1.6 Rev.3 temporal/freeze requirements remain inherited constraints; current Authority R51 and newer scoped Venue Canons are not downgraded to older attachments. Existing SOURCE/FINAL/RESULT, policy/model/prompt, Engine/parameter/MEC/Capital and existing failure history remain unchanged relative to current main, except already-existing Candidate files preserved for review.

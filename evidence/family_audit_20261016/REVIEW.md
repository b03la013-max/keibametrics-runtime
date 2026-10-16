# Family execution and frozen-evidence audit — 2026-10-16

This is an execution record, not a new governance contract or a Production promotion. Observation window ends approximately 13:10 JST, before the approved KAW R01 dispatch window. Machine-readable observations carry their own timestamps. No new LIVE race, signed prediction, Forward OOS credit, Production change, paid OpenAI API request, or purchase was made by this audit.

## Completed changes and verification

Two confirmed correctness defects were repaired in **existing Draft PR #149**, HEAD **57a0b4d21323a3c0b9015d6b575f228555a8f40d**. The original PR's prior settlement-schema change was already equivalent to main; its history and current main were preserved, rather than applying that change twice. The candidate is four paths, 71 additions and 3 deletions.

| Defect | Existing boundary repaired | Before / after evidence |
|---|---|---|
| NaN/Infinity could evade monetary reconciliation; booleans and numeric strings were coerced | `runtime/aki_adaptive_oos_tracker.py`: signed Production settlement reconciliation now requires finite, nonnegative JSON numbers, excluding booleans | Eight malformed signed-fixture cases failed before repair; regression passes after. No evidence is claimed that these malformed inputs occurred in a real race. |
| An acquired `OFFICIAL_RESULT` checkpoint was not committed when the worker stopped before creating `RESULT` | Existing persistence shell in `.github/workflows/km-local-race-key-entry.yml`: persist official evidence independently of signed RESULT, using the existing bounded checkpoint publisher | Real workflow shell executed in an offline temporary Git repository: official-only case failed before, passed after. Result-present and no-result cases also pass. This is not proof of the cause of every historical missing checkpoint. |

The remaining two paths are regression tests. No new workflow, registry, validator service, numerical formula, KRS parameter, MEC or Capital policy was introduced. Scheduler, dispatch authorization, concurrency, and retry limits are unchanged.

Verification files:

- `settlement_before.xml`: 8 failures reproduced.
- `checkpoint_before.xml`: 1 failure, 2 passes before repair.
- `combined_regression.xml`: 139 passes across ingress, dispatcher, recovery, execution-store and AKI paths.
- `persist_regression.xml`: existing bounded publisher, 2 passes.
- `existing_owner_regression.xml`: existing LOCAL shadow, KAW Owner and JRA Owner checks, 38 tests plus 6 subtests passed.
- Earlier 35-test settlement/related suites overlap the combined suite; do not add all counts into a fictitious unique total.
- Latest candidate CI: **3/3 SUCCESS**, runs **38847107954**, **38847107985**, **38847107934**. Detailed links and durations are in `repair_final_ci.json`.
- `minimal_correctness.patch` records the four-path patch. Existing signed artifacts and OOS ledgers were not edited.

Candidate status is **CANDIDATE / CI VERIFIED**, not owner-approved or Production-applied. The prior PR #280 approval is not authorization to merge this new candidate HEAD.

## Current Authority and deployment

Current Family Authority is **KM-FAMILY-CURRENT-AUTHORITY-20261012-R51**. Main observed at 12:54 JST was **16dc9de2add1949c33495e8f5222a3d7c5545a1b**. Since the audit checkout **1225349d64fdffdf87d6035db751d57be731e9dc**, the only changed path was the automated JRA race-day status for this date. The audited execution code was unchanged by that movement.

LOCAL production is a distinct deployment, **2f7ddb5d-6ebe-4de7-b3d5-c70833fd4460**, revision **655530735f24cce78605dd1bd34843bdb2ea253d**, at the existing `witnessstrictimage-production.up.railway.app` endpoint. Fresh Health and Gateway assessment passed:

| Component | SHA / identity |
|---|---|
| Executable bundle | `c6508062d02389fc32900a473a2eee83566a0f1132712033002dd79697d5d25a` |
| Wrapper | `ccb7af22beb13a1304715d967ceb32e48819f1b170bd1d53cd0ec87d6161974c` |
| KRS Engine | `9929df994aa7964173edef9af7e9a705628ce377babf22df3af4e280fc275421` |
| parameter_map | `d8c027ee5bcc8fd3d2c248e8059b341776be38910e833d7589f09ab817c161f5` |
| Signer | `KM-LOCAL-RUNTIME-ED25519-20260922` |

R8 and R10's original FINAL and RESULT receipts were independently submitted to existing `/verify`: four HTTP 200, valid/verified true. No new signing request was made. Main's newer dominant-loss-owner learning integration is not proof it is deployed: the wrapper deployment preserves earlier root modules, and the historical signed Learning lacks that newer field. The audit annotation does not rewrite signed Learning.

JRA's separate runtime returned READY with its own parameter map and signer. This does not resolve JRA Full20 source or Owner maturity. BAN remains physical-runtime-unverified. Uploaded historical rules were treated as historical references; they do not override R51 or activate a new scope.

## Formal entry and actual transport

The five fields `venue_id`, `race_date`, `race_no`, `scheduled_post_at`, `prediction_cutoff` belong to the existing **LOCAL Race-Key entry** workflow/intake. The intake validates identity, venue, dates and cutoff, derives a stable execution ID, and creates the SOURCE intent. Existing `local_race_entry.py` then uses the authorized KAW Owner and generated FORMAL intent.

The separate **formal single-entry** workflow accepts **`intent_path`**, or a main push to `runtime/formal_intents/*.json`. It does not directly expose the same five fields. No undocumented ChatGPT dispatch tool was called: new `workflow_dispatch` is not exposed by the current GitHub connector. Read/branch/PR capability does not establish Actions Dispatch capability.

| 2026-10-15 race | Actual evidence | Boundary / limit |
|---|---|---|
| KAW R06 / R07 | Existing PR #282 incident evidence; no original rejected tool response or new Actions run recovered | First reported boundary is before repository registration or Actions dispatch. Rejecting party, API, HTTP status, exact payload and cause remain UNKNOWN. |
| KAW R08 | Push run **38711152951**, main **3004adcd65e5961152f25048c16e06026de76ae9**, actor `b03la013-max`, started 18:11:50 JST; signed FINAL below | Proves the Race-Key push transport. Does not prove ChatGPT new-dispatch capability or resolve the R06/R07 rejection. |
| KAW R09 / R11 | User-reported failures; no canonical artifact or original refusal recovered in the inspected main cohort | UNKNOWN cause; absence in this checkout is not proof no archive exists. |
| KAW R10 | Push run **38720317619**, main **cb8f2d39db8aca9f48e6e0e376090a3d5aca71ab**, started 19:26:49 JST; FINAL 19:27:34 JST | Signed FINAL, RESULT and Learning exist; prediction lost. User Delivery evidence remains separate. |

No all-day execution-success percentage is inferred from incomplete archived evidence.

## KAW R08 closed loop and Delivery

Original FINAL receipt **fe87ea9c4e9b8b7d46d1ed455984b53581050d236ec33b525e84ae6f49144836**, signed **2026-10-15 18:12:40.178720 JST**, is intact. FINAL artifact SHA is **99b21dff54d1af93c9ea3bcdba729c49697e03f15af398b804aed4afc14cd56f**.

- 180 tickets, each 100 yen: Exacta 15, Trio 60, Trifecta 105; investment **18,000 yen**.
- Official result **8–2–1**, independently corroborated on the NAR official result page. Per-100-yen payouts: Exacta 15,210; Trio 55,460; Trifecta 234,180.
- Winning original tickets: Exacta 8→2 and Trio 1–2–8. Return **70,670 yen**, Frozen Recommendation PFS **392.61%**.
- Signed RESULT receipt **4150672bd8af17ba4e942516baa5cd6dc1e7d0785bbc77a6a7334fe73386bc54** and existing Reflection/Learning are preserved and verified. No duplicate settlement was created.
- First Material Failure: **EXACT_ORIENTATION**. Dominant realized PFS loss owner: **NONE_REALIZED_PFS_POSITIVE**, using the existing classifier as an audit annotation. A missed trifecta does not make the profitable whole portfolio a realized loss.
- KRS's most frequent pair **8→9** was 397/5,000 simulation occurrences; this is not calibrated win probability. The actual pair **8→2** was preserved in the formal tickets. No post-result pair replacement was made.
- Frozen Original AKI binding verifies, but its winner set 2/6 excludes 8: 15 tickets / 1,500 yen / zero return in read-only PAPER reconciliation. This is not an improvement or a new Forward OOS entry.
- **User Delivery time and independent Delivery receipt are UNPROVEN. Actual Purchase PFS is UNKNOWN.** Signed FINAL and repository publication do not establish user receipt before post time.

The original result Actions artifact was downloaded and hashed; it contains result/learning/receipts but no canonical raw official-result checkpoint. The dedicated official parser's fresh reacquisition failed with **OFFICIAL_RESULT_TRANSPORT_PENDING** / DNS transport failure in this work environment. Web-rendered official facts were not substituted for raw canonical acquisition. This blocks new OOS credit for the missing official-checkpoint cases; it does not invalidate an already verified signed settlement by assertion.

Existing GitHub Summary and canonical ticket artifacts provide read-back. No supported immediate ChatGPT Push connection was demonstrated. No additional notification infrastructure was created.

## Performance findings — distinct cohorts, no promotion

| Cohort | Production PFS | Alternative PFS | Interpretation |
|---|---:|---:|---|
| 17 KAW canonical FINAL+RESULT cases, 10/13–15 | **81.80%**: 237,800 invested / 194,530 returned | Not a matched AKI total here | 111 receipt verifications and 1,704 checkpoint file entries checked, zero integrity errors. Selected canonical subset, not every requested race. |
| Main Original AKI eligible 19 | **51.86%** | Original AKI **59.01%** | Fresh scan still waits for Forward OOS threshold; eight additional cases held. Stored held=[] aggregate is not current completeness evidence. |
| PR #276 recovered Original AKI 22 | **60.16%** | Original AKI **48.26%** | Previously recovered observations, not new OOS from this audit. The omitted three observations reverse the 19-race apparent advantage. |
| Existing same frozen 17-policy comparison | **53.55%** | Original 60.11%; Reference replay 114.52%; R1 selection replay 94.76%; R2 selection replay 77.45% | Different cohort from the KAW canonical 17 above. Replay is not genuine Forward; R1/R2 were not promoted. |

Canonical KAW 17 has 12 races with at least 100 tickets, 8 hit-but-loss races, 6 total losses, chronological maximum drawdown **63,540 yen**. Existing audit loss-owner classification assigns Capital 8, Prediction Role 6, and no realized portfolio loss 3. These are diagnostics, not causal proof of a replacement policy.

By bet type on that subset: Exacta **98.36%**, Trio **159.14%**, Trifecta **32.82%** PFS. That retrospective split cannot justify changing Production Capital. Existing MEC-R5's separate 30-case cohort has Production PFS 60.41%, 25/30 hits but 19/30 hit-but-loss; its candidates remain subject to review, not automatic best-replay selection.

Static capture in the KAW subset is Winner 11/17, P2 13/17, P3 17/17. Existing KRS classifications are 13 SUPPORTIVE, 3 UNIQUE-RESCUE and 1 MIXED, with five rescue signals across cases. These signals are not measured incremental PFS. JRA's existing 23/30 KRS ledger also remains incomplete; its 83 third proposals have zero recorded exact-third rescues. Do not equate simulation availability with utility.

`numerical_observability.json` measures all 29 indices with CALCULATED and RULED-NEUTRAL separated. Its winner/P2/P3 raw descending midrank fractions are descriptive only: no favorable-direction assumption, ablation, calibrated probabilities, EV or Kelly is claimed. LOCAL Numerical Authority's prediction-consumption gates remain unchanged. R08 has 406/406 terminalized cells, **350 calculated and 56 neutral**, not 406 calculated.

## Scope and dependency conclusions

| Area | Status | Remaining boundary |
|---|---|---|
| KAW formal Owner | VERIFIED existing implementation / authorized-unvalidated | Genuine repeated future execution and user Delivery acceptance still required. |
| Other LOCAL static generation | CANDIDATE already exists | Existing `local_race_key_shadow_owner.py` is connected to the nonproduction shadow path. It never fills formal FINAL input. No duplicate Owner was built or activated. |
| JRA | PENDING / scope-specific gaps | Separate runtime READY; Full20 source and Owner maturity not established by that health response. |
| C2 PR #124 | BLOCKED live provider | Existing evidence reports CREDIT_BALANCE_EXHAUSTED; historical resume CI does not demonstrate a working zero-cost live Owner. No API purchase/call attempted. |
| BAN | BLOCKED | Physical runtime unverified; LOCAL29/JRA Full20 cannot substitute its model. |
| PR #280 / #283 / #284 | VERIFIED merged | Dispatcher, CI and Gateway fixes are already main. No duplicate implementation or redeploy. |
| PR #276 / #279 | CANDIDATE, mixed dependencies | #279 bases on #276; parts already match main, other shadow/behavior changes remain. Do not merge either wholesale for these two narrow repairs. |
| PR #262–#265 | CANDIDATE / replay restrictions | Reference and R1/R2 comparison evidence preserved; no prediction or Capital promotion. |
| PR #149 | CANDIDATE, latest CI 3/3 | Owner review/explicit merge approval for HEAD 57a0b4d… is the first deployment gate for this audit's repairs. |
| PR #282 | Evidence only / Draft | This audit is added without changing Production files or prior evidence. |

Open PR inventory and candidate/main blob comparisons are saved separately. A zero check-record count (e.g. #262) is not a CI PASS. Historical-fixture jobs named “live” do not prove genuine Forward acceptance. SBO robots/502 failures remain separate from Race-Key registration, with no bypass.

## Current approved Phase B and remaining live acceptance

Existing `KM_LOCAL_AUTONOMOUS_ENABLED=true` was read back from GitHub UI. The only approved target is **2026-10-16 KAW R01**, post **15:00 JST**, cutoff **14:58 JST**, plan SHA **c316b452b4fba1bf40a334607469681442e56a1b4b7c80005955e48410ee60ba**. Existing cron is **14:00 / 14:05 / 14:10 JST**, max one Dispatch, concurrency one, preflight three, zero resend after ambiguous response. Nothing was changed or manually dispatched by this audit.

Fresh NAR card read-back at approximately 12:57 JST shows twelve listed runners, 15:00, sunny/good, with no current cancellation mark observed. A runner's historical cancellation is not today's cancellation. The official raw SOURCE and Active Runner match must still be reacquired by the authorized execution. These read-only observations do not create a new SOURCE checkpoint.

This report is completed **before** the scheduled window. Dispatch, FINAL, Delivery and this race's RESULT closed loop are therefore **PENDING**, not failed or successful. The existing bounded follow-up remains in place; no extra automation was created. Future races, other venues, JRA and BAN are not authorized by this Phase B plan.

## Production decision, rollback and costs

Production was left unchanged. The new fixes run in repository-side workflow/reconciliation code and do not require an Engine, parameter, signer or Railway wrapper deployment. After owner review of PR #149's exact HEAD, a permitted merge must still recheck current CI and main compatibility. No historical race should be re-signed or counted anew merely to demonstrate the repair.

Rollback for this candidate is a scoped revert of these four paths. Retain any authentic official checkpoints already persisted; never delete or rewrite signed artifacts, result history or OOS observations. Existing Runtime rollback remains available but was neither required nor executed for this candidate.

Existing Railway plan and workspace limits were read back and unchanged. Account-specific usage amounts are reported privately to the owner, not copied into this public repository. New CI job wall time across the two candidate revisions totals 201 seconds; this is not a dollar estimate. No unlimited retries, new service, billing-plan change, cap increase, paid OpenAI request or bet was made.

**Completion boundary:** audit, two minimal repairs, regression, current CI and evidence preservation are completed. All-Family autonomous operation, immediate user Delivery and improved long-run PFS are not established by this work. The first new Production gate is the exact-HEAD review/merge approval for PR #149; missing original refusal evidence and missing canonical official checkpoints remain explicit data limitations rather than invented diagnoses.

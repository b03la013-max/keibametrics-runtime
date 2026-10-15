# Family Race-Day Reliability — repair candidate, 2026-10-15

Status: CANDIDATE / PRODUCTION-FROZEN / LIVE-ACCEPTANCE-PENDING.

## Authority and dependency

Inspected main `2cf355f0f8e46f2e777b4d78d2ed2fcc4d8c7d6c`; Family R51, LOCAL R3, MEC-R3. This branch inherits PR276 `4e3c71fc1765027f45299cd2b406228f41d20ad8` and merges that main. It does not activate either candidate. PR257 is merged; PR124/265/276 remain Draft. Frozen physical Runtime revision and executable bundle, rather than Git SHA equality, remain the existing compatibility contract.

No Production weights, indices, Physics, parameter map, MEC, AKI, Capital, Venue Canon, existing FINAL/RESULT or OOS definitions are changed. No merge, deploy, activation, key change, billing change or purchase was performed.

## A/B/I — saved-record inventory and first failure (COMPLETED inventory; root-cause coverage PENDING)

`research/family_reliability_20261015/execution_inventory.json.gz` inventories 253 saved execution IDs and 55 auxiliary JRA no-bet/learning/status/race-key records. It retains research separately. LIVE-labeled saved IDs: LOCAL137, JRA94; these are **not unique races** (transport EXEC aliases and versioned retries remain visible). LOCAL has 96 SOURCE, 89 FORMAL, 56 RESULT phase pointers; JRA has 88 SOURCE pointers in this store. JRA FORMAL/RESULT count zero here does not establish absence in its separate lifecycle. No BAN record was found in this inventory. 22 research/other IDs are outside the LIVE-labeled summary.

The inventory verifies immutable store hashes through existing `resolve_phase`; it does not call every receipt a freshly verified signature. It records historical phase timestamps, attempt IDs, implementation SHA, stored errors and unknowns. Root-cause detail is established only where logs/receipts support it. Missing stages alone are **not a proven system failure**. Chat request acceptance, actual request time, recovery outcome and verified delivery denominators remain UNKNOWN. Do not quote these counts as Family race reliability percentages.

Recorded error occurrences include official result identity HOLD14, mandatory stage incomplete4, track-condition mismatch2, runner universe mismatch2, official result HTTP/authority HOLD2. These are occurrences, not unique failed races. Official-source HOLD is separate from software error; mismatches must remain fail-closed.

The existing `research/kaw_day_20261014/execution_audit.json` retains all12 scheduled Kawasaki races:5 FINAL/RESULT,3 SOURCE-only,4 without signed-execution evidence. It does not assume all12 have a provable chat request. Known incidents already repaired upstream are reused: R12 immutable push-event Race-Key extraction (38549826099 vs38555632204); R11 persisted FINAL despite later Git stash failure (38550326785); SOURCE-first/checkpoints/result-worker separation from PR257. These are not reimplemented here. Historical R7 missed its cutoff; historical R6 connector refusal has no proven lower-level cause. Unknown causes remain unconfirmed.

## C — Prediction Owner (BLOCKED/PENDING)

Existing Formal Single Entry supports LOCAL only. LOCAL's evidence-only Static profile is enabled for KAW but explicitly INITIAL-ACTIVATION-CANDIDATE / NOT-PERFORMANCE-VALIDATED / REQUIRES-LIVE-ACCEPTANCE. It consumes official prestart past-start evidence, not numerical candidate values. Other LOCAL venues need authorized frozen Static. JRA retains its separate owner/runner contracts. BAN physical runtime is unverified. None may silently borrow another Family's prediction authority.

PR124 C2 is a separate unmerged Shadow Owner. Its latest head is `1033c818bf2451ccb9496ae017c7aea0c35ad13e`. A real existing staging comparison job was rerun without starting Production: run36964996544, attempt3, job116154021402, code`643ba5bd15553d642e1041ffb552df303f6d71a0`, 2026-10-14T23:10:08Z–23:10:11Z. Configured staging secret presence was demonstrated, but provider preflight returned `OPENAI_API_TRANSPORT_OR_PROVIDER_HOLD`; no race comparison or two-race isolation acceptance followed. Production job was SKIPPED. Artifact11935261346, digest85a5cfe9847409e82377b0dbec3a970e98e0575e0139902f93278992954fa1f9.

The rerun uses the original workflow SHA, not PR124's newer diagnostic adapter. Therefore 429/quota/network/auth cannot be inferred from this old generic HOLD. Local credential presence is false. No key value was read. Next exact operation: workflow_dispatch existing C2 historical comparison on latest PR124 branch with `keibametrics-staging`; inspect its sanitized HTTP class, resolve any provider-side quota/project authorization through the owner, then repeat frozen evidence/schema/latency/signature/two-race isolation. This is not an approval to promote C2.

## D/E — minimal repairs (CANDIDATE; regression VERIFIED)

1. `local_race_entry.run`: an existing immutable FINAL is routed to the existing orchestrator before SOURCE acquisition, numerical materialization, Owner generation or deadline gating. Stored canonical intent is combined with the request; unchanged semantic/source binding is mandatory. Changed basis fails closed. Readback removes transport-only `analysis_only` rather than changing semantic identity. No new prediction or deadline extension occurs.
2. Existing failure classifier now recognizes missing authorized Static as `PREDICTION_OWNER_INPUT_REQUIRED`; its recovery hint waits for authorized frozen input instead of suggesting blind same-input retry or Owner promotion.
3. Existing terminal readback no longer trusts historical `receipt_verifications.FINAL` alone: canonical Gateway `/verify` must freshly validate the signed FINAL and race identity before tree rendering. Verification outage/failure cannot become signed/render PASS. Existing tree roundtrip/stake check remains authoritative. Output now includes the complete canonical prediction package, ticket, KRS reference and UNKNOWN actual purchase. Missing authority/grade metadata remains explicitly missing, never invented.

Before repair: the three new regression cases FAIL. After repair:136 relevant tests PASS. Existing execution store, orchestrator, transient transport, deadline fail-closed, source reuse, result recovery, ingress and tree regression suites were included. These tests are engineering evidence, not live reliability or prediction evidence.

Actual R12 after-cutoff entry readback returns `ALREADY_COMPLETE`, `readback_only=true`, `prediction_reexecution=false`. It did not call SOURCE/Static/KRS. Actual R11 and R12 terminal readbacks freshly verified FINAL and rendered all tickets even when Actions status was failure. Both remain `SIGNED_FINAL_RENDER_AVAILABLE_DELIVERY_UNPROVEN`.

## F — multi-race and recovery (existing implementation; new live acceptance PENDING)

PR257 race-scoped workers, SOURCE/RESULT separation and existing store locks are retained. Main's latest signed-RESULT downstream transport retry and canary persistence repairs are inherited, not duplicated. Checkpoint integrity, semantic identity and source identity are not relaxed. No new scheduler, universal discovery or fallback runtime is introduced. All-day queue/worker kill recovery and two simultaneous unknown-future races have not been demonstrated in this run.

## G — external acceptance (VERIFIED limited scope)

Railway deployment`acf63364-0235-42ea-b68d-fbe931fcf51f` is SUCCESS, created2026-10-14T06:12:53Z. This work made no infrastructure mutation. Canonical LOCAL Health/Gateway bundle assessment PASS (`gateway_canary.json`). Physical SHA`f0d23766b1d2e4cefc6194458b0e9141d5479cbc`, engine1.1.0 SHA9929df994aa7964173edef9af7e9a705628ce377babf22df3af4e280fc275421, parameter0.1-provisional SHAd8c027ee5bcc8fd3d2c248e8059b341776be38910e833d7589f09ab817c161f5. Main mismatch is recorded, not mislabeled as matching deployment.

Fresh `/verify` calls for the two historical races' SOURCE/PRE_KRS/KRS/FINAL/RESULT are saved separately. They verify retained receipt compatibility; no new KRS run or unknown-future prediction is claimed. C2 API preflight is independently HOLD. JRA/BAN full external lifecycle is not accepted by LOCAL health.

## H/J — Delivery and unknown-future acceptance (PENDING)

Canonical tree output and full package are available in the two readback files and delivery artifacts. Rendering now is not proof of chat receipt before historical post time. No authenticated user-delivery acknowledgment exists. No future formal race is counted. Missing approved Owner/required formal race cutoff must not be filled by candidate activation or an invented cutoff. 0 new genuine forward acceptances; no historical/synthetic record is added to Forward OOS.

Next authorized live acceptance must fix race identity/post/cutoff/authority/source and approved Owner before starting, retain one execution ID, freeze SOURCE/Static/PRE_KRS/KRS/MEC/Capital/FINAL, then prove an external delivery time before deadline. Later official RESULT/settlement/reflection/learning must close. Repeat for concurrent races and across each separately authorized Family. Failures and legitimate HOLD remain in the denominator. Use observed stage latency; do not invent margins or extend deadlines. Human acknowledgment and Owner activation are independent acceptance items.

## K/L — disposition

| Acceptance | Status |
|---|---|
| Correctness implementation / local regression | CANDIDATE / VERIFIED |
| LOCAL Gateway health and retained receipt verification | VERIFIED limited scope |
| C2 real API / two-race Owner isolation | BLOCKED / PENDING |
| Full Family one-trigger execution | PENDING |
| Prestart verified delivery | PENDING |
| Unknown-future lifecycle / all-day reliability | PENDING |
| Production activation | NOT REQUESTED; unchanged |

Draft PR and CI are reported in the PR body after remote execution. Production review must separately approve any merge/deploy/activation. No performance, user-delivery, or all-Family completion is claimed from CI/replay/readback.

Large canonical readback/inventory evidence is losslessly gzip-compressed (.json.gz); working materialized checkpoint copies are not duplicated in Git.

# Family P0: failure isolation, durable checkpoints and truthful Delivery

Status: DRAFT ONLY. Production Merge/Deploy/Activation and new LIVE dispatch remain HOLD. This is a continuation of PR #282, not another repair PR. Main audited: `02cd804b2e1e1fbc829f1a5a49e0ce7884b88698`; retained previous draft: `058d756aef4bf990e551dd9464cac4e45cc20d06`. PR #280 and #284 are already merged and reused.

## Seven operational answers

1. **Original refusals remain unattributed.** For 10/15 KAW6/7/9/11 and 10/16 KAW7/10, the observed earliest boundary is before canonical GitHub registration: no tracked Race-Key, Intent, checkpoint or matching Actions run was found in the audited main/day lists. Original tool name/input/error, GitHub HTTP response, original requested Authority and first-stop time are missing. `UNKNOWN` is preserved. A narrative saying “safety check” is not proof of the refusing component. The two later 10/16 failures cannot be conclusively assigned the same root cause.
2. **GitHub code has separately reproducible reliability defects.** A corrupt checkpoint aborted the whole dispatcher tick; raw LATEST observation did not reuse the canonical hash/identity validator; a claimed race without FINAL could remain in monitor status after cutoff. The workflow could also append an old canonical_tree after fresh FINAL verification failed. SOURCE and generated Intent were only pushed after later work, exposing verified progress to worker loss. These are corrected here, not presented as the cause of the historical connector refusals.
3. **Connector capabilities differ by product surface.** This Work/Codex surface exposes 89 GitHub operations including Git Data writes, but no dedicated new workflow/repository dispatch operation. Standard ChatGPT GitHub is documented as read-only. Work previously completed R1 registration using the existing authorized main-push entry. Neither that capability nor an Allow-all app setting proves what was exposed or allowed in the failed chats. The observed connector URL allowlist error in the prior audit is not an original race refusal or GitHub server HTTP denial. No alternate-route retry is performed here.
4. **Discovery works; all-race autonomous execution is not proven.** The official 10/16 plan recorded all 12 races at 08:59:08 JST, SHA `c316b452b4fba1bf40a334607469681442e56a1b4b7c80005955e48410ee60ba`. The dated activation authorizes R1 only, maximum one dispatch. R2–12 are NOT_AUTHORIZED_FOR_THIS_PHASE. A day plan is not registration of all formal Intents. Schedule run 38880716990 was created at 18:28:40 JST and read back the existing R1 result; no new dispatch was observed. Its original cron occurrence and lateness cause remain UNKNOWN. R1's prestart success came from push run 38855562125, not a proven 14:00/14:05/14:10 scheduled handoff.
5. **No delivery route currently has a proved time guarantee.** Existing canonical artifacts and the Actions job Summary are usable readback destinations. This candidate writes only this invocation's freshly verified prestart FINAL to Summary, with content SHA, write time and FINAL receipt/artifact SHAs. It explicitly does not claim user arrival. Standard chat immediate FINAL push has not been demonstrated. GitHub documents schedule delays/dropped runs; an hourly repair watch cannot guarantee prestart delivery. No new notification destination was added.
6. **Next proof requires a dated, approved future cohort.** Freeze the official identities and fixed denominator before execution, with independent cutoffs and current authority. For multiple unknown future KAW races, measure Discovery, Race-Key, Intent, SOURCE, Static, KRS, FINAL, prestart user Delivery and Result closed loop. Initial target is 100% for each stage over the whole approved cohort, zero duplicates/late FINAL, with every failure retained. At least two races are necessary but not sufficient to claim permanent reliability; continuity and recovery must be observed over further meetings. No future cohort is approved by this candidate.
7. **External/open constraints:** unavailable original refusal traces; missing dedicated dispatch on this surface; ordinary chat read-only access; no approved all-race future activation; no prestart arrival receipt; scheduler timing uncertainty. Existing Railway runtime is healthy. No evidence justifies a runtime deployment, signer/engine/parameter change or broader Authority change.

## Fixed retrospective denominator

The requested comparison is exactly nine races, not a representative future OOS sample. See `fixed_denominator_metrics.json` for every row, reference and UNKNOWN.

| Stage | Verified passes / fixed 9 | Other states |
|---|---:|---|
| Prestart official Discovery | 3/9 | Six prior-day discovery histories UNKNOWN; do not award retrospective discovery as prestart proof |
| Race-Key, Intent, SOURCE, Static, KRS, Signed FINAL | 3/9 each | Six not observed on audited main |
| Prestart user Delivery | 0 verified / 9 | Three UNKNOWN; six no FINAL. This is an evidence lower bound, not proof that nobody received a prediction |
| Signed RESULT + Settlement/PFS + Learning | 3/9 | Six not observed; actual purchases are UNKNOWN |

Controls: 10/15 R8 FINAL 18:12:40 JST, R10 FINAL 19:27:34 JST; 10/16 R1 FINAL 14:25:13 JST and RESULT 15:07:23 JST. All three retain the original signed artifacts and completed result records. R1 chat emission was observed around 14:32–14:33, but independently bound user arrival remains unconfirmed. Earlier fresh signature verifications are preserved at their original observation times, not relabeled as new LIVE execution.

## Candidate changes and stopping conditions

- `runtime/local_race_day_dispatcher.py`: reuse `execution_store.resolve_phase`; hold a corrupt race separately, preserve claim and first failure observation, allow unrelated authorized races to proceed, record expired FINAL deadline without redispatch.
- `runtime/local_race_entry.py`: optional existing strict Git persistence in the main Actions entry. Publish verified SOURCE before numerical/Static/FORMAL work and the frozen canonical Intent before FORMAL. Publication failure stops further work. No blind retry of an ambiguous external execution.
- `runtime/local_race_key_gate.py`: Summary comes from fresh verified return data, not a stale file; bind content/time to FINAL hashes, preserve original entry error fields, keep delivery unproven.
- Existing entry workflow: opt into those persistence points and preserve input/preflight/entry diagnostics even when the later formal gate fails. Existing schedule, activation checks, permissions, concurrency, resolve/result/local-day jobs are unchanged.
- Three existing test modules gain targeted regression coverage; existing 206-test acceptance command passes. The initial sparse-checkout fixture omission is documented separately from code failures. Before-patch evidence contains three behavioral failures and four absent-hook/API failures; it is not a replay of the original chat refusals.

Crash recovery is bounded: verified SOURCE and frozen Intent become durable before later stages. A process death during the publication itself or an ambiguous external FORMAL outcome still requires checkpoint reconciliation/authorized recovery. This PR does not claim arbitrary crash recovery, add another dispatcher, retry uncertain sends or fabricate delivery receipts.

## Owner review, release and rollback

Owner review is limited to the exact new executable diff, evidence, stop conditions and rollback. Existing owner-only governance is retained; no independent human review is claimed. This audit authorizes only Draft persistence and regression/CI. Production adoption requires explicit approval of the resulting exact HEAD. Existing changes already in PR #282 remain preserved and require their existing review; this candidate does not reapprove them.

No current date's expired approval is reusable for a new future race. Before activation, approve the official future plan SHA, race set, current authority, destination, maximum dispatch count, timing and cost scope. Do not remove a race from the denominator after failure.

Rollback: before merge, leave the Draft unapplied. After separately approved adoption, revert only the newly changed workflow/runtime blocks to the audited main versions using a reviewed revert; retain every newly written signed checkpoint, frozen Intent, failure and Delivery record. Never roll back by deleting receipts, resetting LATEST pointers or rewriting OOS. Publication failure holds further execution; uncertain dispatch remains non-retryable until reconciled.

## Protection and continuing observation

No protected profile, signer, engine, parameter, 29-index formula, Prediction Policy, KRS Physics, MEC-R3, Capital, Venue Canon, signed artifact, race-day approval, Race-Key or OOS record changed. Additional OpenAI paid API requests: 0; purchases: 0; production deployments: 0. Railway Soft $5/Hard $10 unchanged; this audit did not independently reread live billing settings, and retains the existing approval's limit-verification reference.

A single hourly Work fault-audit task is enabled, starting 20:45 JST. It checks existing authorized runs, saves new evidence, reproduces demonstrated code defects and updates the same Draft after regression/CI. It cannot register/dispatch races, merge, deploy, activate or expand scope. Only meaningful new findings notify this user. It is not a replacement dispatcher or a realtime delivery channel.

Primary platform references: https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt and https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule . These explain capability/timing limitations, not the unobserved historical refusal cause.

# LOCAL race-day Candidate acceptance — 2026-10-15

Implementation: existing LOCAL Race-Key workflow gains one disabled scheduled job;
no new workflow, execution registry, numerical formula or policy. The existing
19-field SOURCE intake, full Formal owner, per-race Actions concurrency, strict
checkpoint persistence, signed FINAL verifier/renderer and independent RESULT job
remain the execution path. JRA and BAN authority are unchanged.

`python -m runtime.local_race_day_dispatcher --venue KAW --date YYYY-MM-DD --cutoff-seconds 120`
reads official RaceList links and every individual card, binds date/venue/race/post,
records declared/observed active runners with the existing parser, and writes an
unsigned day plan. It does not send LIVE or create a freeze. No guessed race count.
The card's race navigation must corroborate the complete menu. SOURCE reacquires
current official runners/weather/weights; changes are handled by existing lifecycle.

Before activation, the owner must approve an actual future dated plan, its SHA,
all race numbers, Current Authority, KAW Owner scope, canonical Runtime destination,
data range, scheduled execution, and existing Runtime usage cost. Use the disabled
example only as a review template; it is NOT an approval. Store the approved record
at profiles/local_autonomous_approvals/YYYY-MM-DD-KAW.json after review. The matching
plan is runtime/local_race_day_plan/YYYY-MM-DD-KAW.json. No such enabled record or
repository variable was created by this work.

After separate Human Review, Required Checks inspection and explicit Production
merge/Runtime deployment approval, the owner can enable repository Actions variable
KM_LOCAL_AUTONOMOUS_ENABLED=true. The existing workflow's 5-minute cron then selects
only approved dated plans. Only this job gets actions:write; ordinary entry keeps
actions:read. Repository Actions must permit GITHUB_TOKEN workflow dispatch; verify
the first actual handoff rather than assuming owner admin equals App permission.
The cron covers 09:00–21:55 JST, so approval windows outside it must HOLD pending an
explicit schedule review. ChatGPT does not acquire a new dispatch capability.

Each due race publishes a canonical five-field key and durable claim BEFORE using
`gh workflow run km-local-race-key-entry.yml --ref main` with the existing five
inputs. GITHUB_TOKEN pushes do not trigger another workflow: explicit authorized
Actions dispatch is intentional. The driver does not wait for RESULT. Cutoff and
release deadline are checked before and after persistence. Existing race revisions,
Formal intents and keys prevent a second prediction. Runtime preflight retries are
bounded to three; dispatch timeouts/crashes after a claim never blindly resend.
Ambiguous runs require owner reconciliation against recorded claim, Actions title/
Run ID and existing checkpoints. SOURCE resume uses the existing approved recovery
path; this Candidate does not declare autonomous recovery proven.

Status retains remaining time, stored stage receipts, existing failure diagnostics/
resume hints, Actions run evidence, deadline alerts, and original FINAL read-back.
Canonical tree SHA, exact tickets/stakes/investment and freeze/read-back timestamps
are exposed by the existing gate. Chat receipt/time/content hash remain null until
actually observed. GitHub render availability is not delivery success.

Rollback: disable KM_LOCAL_AUTONOMOUS_ENABLED first; retain all claims/keys/receipts
and failures. Let or safely stop existing per-race jobs according to lifecycle; do
not delete a key to retry. Revert the reviewed Candidate code/workflow commit after
owner approval. If physical wrapper was deployed, use the existing PR280 release
rollback and compare bundle/signer/engine/parameter/anchor before any new execution.
No Production change has been made here.

LIVE acceptance remains PENDING: a future owner-approved day must demonstrate
ordinary/cancelled runners, concurrent races while RESULT waits, outage recovery,
checkpoint reuse, FINAL/read-back, actual timely Delivery and official Settlement/
Learning. Include every failure in denominators. Historical public discovery and
synthetic tests are never Forward OOS or a 100% uptime guarantee.

PR279 retains broad history; PR280 reuses its minimal correctness repairs and adds
this explicitly requested opt-in operational Candidate; PR282 remains incident
history. No prior failed race was changed to success. SBO robots HTTP502 is separate
and no restriction/check was bypassed. Detailed main protection API returned403
Resource not accessible by integration: owner must inspect Settings > Rules /
Branches and required statuses for the exact Candidate SHA. AI did not approve it.

# 2026-10-15 Production promotion gate

NOT MERGE-READY / NOT DEPLOY-READY / NOT ACTIVATED.

Reviewed previous Candidate 4ee59aa311ceb4cb374847a90d61ee8b180386da against main
1802622e5848aa1698514b80432f73c228160376. Local merge-tree had zero conflicts;
main was integrated into Candidate only. GitHub initially reported mergeable=false;
this was not reproduced as a content conflict. Original executions and intents
remain byte-identical to that main. PR279 remains the historical broad Candidate,
including inert SOURCE Behavior B; PR282 remains Draft evidence. Neither needs
to be merged before PR280.

## Findings repaired in the existing dispatcher

The previous approval validator required every discovered race, so Phase B could
not execute an approved subset. It also lacked explicit phased promotion and a
dispatch budget. Current Candidate selects only explicitly approved races,
requires Phase B one-race acceptance before Phase C limited multiple races, and
requires B/C acceptance references, human review and full-day activation for D.
Claims, including ambiguous outcomes, consume the finite dispatch budget across
ticks. Missing cost-control review reference fails closed. These references are
owner-maintained evidence, not AI approval or automatic verification of billing.

Phase A now uses the existing CLI to inspect duplicate keys, existing checkpoints,
cutoffs and observed runner sets without any LIVE approval, dispatch or verify POST.
Archived official-plan dry-run is explicitly historical, not fresh LIVE acceptance.

## Change classification

A correctness: existing SOURCE resume, immutable FINAL/read-back, official
cancellation reconciliation, Active membership boundaries, missing payout HOLD,
race isolation, deadline/claim persistence and ambiguous-response HOLD.

B behavior of operations: official day discovery, opt-in scheduled dispatch and
the phased/bounded approval handling. This is not merely a correctness-only
release; scheduling/egress/cost activation needs explicit owner approval.

C prediction behavior: no selection formula, 29-index calculation, prediction
weight, KRS Physics, MEC selection/Capital policy, Venue Canon or AKI promotion
change. MEC's existing Active membership rejection is an integrity boundary.
SOURCE acceptance-narrowing Behavior B in PR279 remains inert and excluded.

## Runtime and required owner actions

Existing deployment acf63364-0235-42ea-b68d-fbe931fcf51f remains SUCCESS and supports
rollback. Fresh health confirms f0d23766, bundle/engine/parameter/signer matching
current Gateway. Candidate repairs are NOT deployed. Six saved R08/R10 receipts
were reverified HTTP200/valid=true. No prediction or settlement was regenerated.

Human reviews: 0 at retrieval. Branch response protected=false and rulesets=[];
detailed protection endpoint returns403 Resource not accessible by integration.
Owner must inspect Settings > Rules and Settings > Branches and identify effective
required check names/apps. Integration cannot certify administration settings.

Railway24h telemetry: CPU mean0.0043053821, peak0.51395415; memory mean0.142533104GB,
peak0.209207296GB,1441 samples each. These are resource measurements, NOT a price.
Previous exact-head14 CI runs used547 aggregate job-seconds (9.1167min), not billed
minutes. Account plan, included credits, monetary charges and remaining budget
remain unavailable. Owner must provide current GitHub/Railway billing observations,
an explicit monetary ceiling and enforceable provider control/monitoring reference.
max_dispatches limits submissions only; it does not guarantee a monetary ceiling.
Do not activate while those conditions are unverified.

Current Static Owner is KAW-only. Discovery support for LOCAL venues does not
authorize their Static owners. No all-LOCAL/JRA/BAN scope expansion is permitted.
No dated enabled approval record or scheduler activation was created here.

## Deployment and rollback

Reuse docs/MINIMAL_CORRECTNESS_RELEASE_20261015.md and its existing start-command /
Gateway patches. The physical release is wrapper-only: preserve old Engine,
parameters, root MEC/Capital modules, signer and anchor; do not switch the whole
Runtime to latest main. Revalidate the pinned wrapper SHA before authorized deploy.
Merge approval, wrapper deploy/Gateway alignment approval, dated race egress and
cost approval, then scheduler activation are separate owner operations.

Rollback: disable autonomous entry first; retain claims and signed artifacts;
restore the reviewed old start command/Gateway patch or known deployment snapshot;
verify old fingerprint and saved receipts. Do not clear ambiguous claims or replay
past races. Existing cancellation defect returns after rollback: affected races HOLD.

## Acceptance disposition

A promotion review CANDIDATE; B required checks/human review BLOCKED;
C existing Runtime fingerprint VERIFIED (Candidate deployment PENDING);
D archived read-only dry-run VERIFIED, fresh-source status in separate log;
E limited LIVE BLOCKED; F multiple-race LIVE BLOCKED;
G canonical read-back CANDIDATE, independent prestart Delivery PENDING;
H R08/R10 stored closed loops VERIFIED historically, new autonomous loop PENDING;
I recovery regression CANDIDATE, genuine outage recovery PENDING;
J usage measurements VERIFIED, bill/cap BLOCKED;
K rollback package CANDIDATE, no deployment rollback executed;
L full-day Activation BLOCKED.

For live acceptance, record ALL approved targets in the denominator. Missing stage
or independent delivery evidence is UNKNOWN, never success or inferred zero.
Record registration/SOURCE/Static/KRS/FINAL/prestartDelivery/deadline/result/recovery
per execution plus first failure. Historical6–11 cohort remains2/6 FINAL and4/6
reported entry failures; original rejection owner/code remain UNKNOWN. R08/R10
Actual Purchase PFS UNKNOWN. These do not establish future autonomous reliability.

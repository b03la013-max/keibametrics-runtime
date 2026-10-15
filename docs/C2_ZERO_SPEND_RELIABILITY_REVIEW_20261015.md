# KeibaMetrics zero additional API spend review — 2026-10-15

Candidate only. No OpenAI requests, new external verification, LIVE payload dispatch, deployment, merge, purchase, or paid resource creation was performed in this revision. API budget is JPY 0. Production remains frozen; C2 remains SHADOW and unapproved.

## Evidence and status

| Deliverable | Status | Evidence / limitation |
|---|---|---|
| A Successful/latest diff | VERIFIED (offline) | Successful structural cohort 041fd9d / run 38658143289 versus ac932816. Latest schema adds Common active role states, native pair/third states, exact ranking/role cardinalities; earlier responses contain free-text/SELECTED states. All three saved responses fail latest schema. Prompt, pinned model and policy remain unchanged. Latest native schema was not real-API accepted. |
| B Duplicate spend audit | CANDIDATE / partially BLOCKED | Existing formal execution store reuses bound SHADOW checkpoints; added explicit race/execution/cutoff checks. Historical harness has no persistent resume and each race performs authentication plus generation. Workflow reruns could repeat both. Removed automatic push trigger; zero-budget guard blocks every real request. Paid cross-process reservation/resume is not implemented or accepted. |
| C Zero-spend protection | VERIFIED (offline), CANDIDATE | Existing adapter stops real calls with API-BILLING-HOLD before credentials/network. CLI stops before SOURCE external verification. JPY monthly/race limits and retries are zero. Positive config cannot silently reopen spending: returns BUDGET-HOLD because no enforced shared reservation ledger exists. |
| D Historical regression | VERIFIED (offline) | C2/orchestrator 102 PASS; PR279 selected formal, numerical, authority, ticket, capital, result and delivery/runtime regressions 96 PASS. Saved actual responses rejected correctly by latest schema; no new provider responses. No Forward OOS increment. |
| E Reliability repair | CANDIDATE | Preserve PR279 immutable FINAL readback, canonical ticket delivery, signature/identity validation and receipt persistence. Additional C2 cutoff/identity checkpoint binding prevents stale reuse. No new runtime failure claimed from replay. |
| F Other Owner availability | VERIFIED (repository audit), LIVE PENDING | Current main eb3105ef85091b6406f0c8e65a0543f1328d9ac4; R51. LOCAL KAW source-only initial Owner explicitly authorized 2026-10-14, unvalidated and no genuine future acceptance; not generic Family C2 authorization. JRA has separate scoped static-owner authorization, not proof of external autonomous availability. BAN has no accepted external physical endpoint. Never borrow Owner across Family/venue. |
| G Minimal paid reopening | PENDING / API-BILLING-HOLD | Procedure below; no execution authorized now. |
| H GitHub / CI | CANDIDATE | Existing Draft PR124 receives this repair; PR279 stays Draft at 5729e735, its prior 3/3 CI success is historical evidence. Local tests above are current offline checks, not real API verification. |
| I External conditions | BLOCKED / PENDING | Latest billing failure was credit_balance_exhausted. Signed C2 Shadow receipt, native real-API acceptance, Human Promotion Review, genuine future LIVE, multi-race external continuity and new settlement/learning remain unmet. |

## Spend-path findings

No internal retry loop exists in the current adapter: 429, schema errors, timeout, DNS and TLS terminate. Retrying GitHub runs is still capable of duplicating billed work in old revisions. This patch disables spending on the new Candidate revision; it cannot rewrite historical workflow revisions or guard unrelated applications. Do not rerun old paid jobs.

Formal checkpoints bind SOURCE receipt/universe, authority, configuration (model, prompt, policy), entrypoint and input contract. Explicit race/execution/cutoff comparison is added. Changed basis fails closed and must not reuse old results. Existing FINAL is read from its signed immutable canonical artifact on PR279; Owner regeneration must not replace it. Historical completed_comparisons retention is evidence preservation, not a working resume cache. Old free-text statuses are not translated into native purchasing/protection states.

Authentication probes are currently repeated per execute. Five comparison/isolation generations used five extra probes in the saved successful cohort. This report does not claim those costs were measured. Saved outputs predate usage capture; costs cannot be inferred from duration. Input projection excludes results but includes raw/normalized source evidence; token size has not been measured with the pinned model tokenizer. Required evidence is not removed merely to shrink requests.

## Minimal acceptance after explicit paid reopening approval

1. Review one immutable SOURCE/runner universe, cutoff, authority, config/model/project identity and exact request SHA locally. Validate native schema before network. Never use post-result data in prediction input.
2. Enforce a reviewed cross-process monthly/race reservation and request identity before enabling API. Define input-token cap, output cap (current 8000 is a ceiling, not an accepted minimum), hard request count, retry budget 0 initially, and concurrent-run exclusion. Exact input-token budget and expected cost range remain PENDING until official pinned-model pricing/token accounting is recorded. No invented fixed cost.
3. Use the existing authentication evidence when formally permitted; review removal of repeated per-race probes rather than silently changing authentication policy. Otherwise explicitly budget one no-race probe. Identity changes invalidate that evidence.
4. Resume only validated completed comparisons bound to identical normalized input, model, policy, schema, authority and cutoff; do not rerun them. Current historical harness lacks this facility, so paid acceptance remains held until it is reviewed.
5. Smallest native regression needs R07/R08/R12 once each (3 generations); fresh-process isolation may verify committed frozen outputs without new generation only if the acceptance contract permits. If it requires independent fresh responses, add exactly two generations. Do not call replay Forward OOS.
6. Stop on billing/quota/permission/schema mismatch, exceeded token/request budget, invalid signature, changed universe or cutoff. No automatic paid retry. An ambiguous transport completion must be reconciled before another request.
7. Preserve response ID, usage counters, request/output SHA, separate timing, freeze and signed Shadow receipt through an authorized signer. A hash manifest is not a signature. Native-schema success does not authorize Production.
8. Unknown future is separately approved Shadow/PAPER until Human Owner Promotion Review passes. New canonical runtime payload egress needs explicit approval. Only genuine pre-cutoff FINAL/Delivery followed by official RESULT/settlement/PFS/learning can establish LIVE acceptance.

## Retained external evidence

PR279 holds prior saved-envelope external verification (10/10) and frozen physical health evidence. They were not re-executed in this zero-spend work. Runtime latest physical health and genuinely future operation therefore remain PENDING; offline tests are not external runtime proof. All pre-existing receipts, failures, signed FINAL/RESULT and Forward OOS records are unchanged.

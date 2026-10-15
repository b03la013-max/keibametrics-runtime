# R06/R07 common registration investigation

Status: **BLOCKED — original refusal unavailable; automatic formal launch not restored/proven**.

main 887c07fe was refreshed and its tracked paths searched for both races. No same-race key, intent, checkpoint or FINAL was found. The queried Actions window 16:00 JST onward has no R06/R07 run. External durable-store absence has not been proven. Do not create a FINAL or call an alternative submitter to fill the gap.

R07 was reported blocked at 17:38:48 JST by a prior assistant message. Neither that message nor the retrieved R06 history includes the actual tool/API/payload/error or refusal authority. The original safety rejection is therefore **reported, not reproduced**. No original error code is invented.

## New concrete connection evidence

- Repository owner permission: admin. Repository viewer booleans include push/admin; these do not prove App Actions-write scope.
- Managed GitHub installation is selected-repositories. Installation response does not enumerate permission scopes.
- Current connector exposes reads, Git data writes and rerun-existing-job operations; no new workflow_dispatch/repository_dispatch tool was found.
- Read of workflow detail endpoint through generic Fetch was rejected by connector allowlist: HTTP400 / INVALID_ARGUMENT.
- Branch Protection GET reached GitHub and returned HTTP403 / FORBIDDEN / Resource not accessible by integration.

**These two diagnostic read errors are not R06/R07 original rejection codes.** They establish different connection boundaries. No safety setting, token, App scope or Production configuration was changed.

## Existing formal entry path

The existing workflow declares workflow_dispatch on main, with five scalar inputs: venue_id, race_date, race_no, scheduled_post_at, prediction_cutoff. An authorized owner can use native GitHub Actions → KM LOCAL Race-Key Single Entry → Run workflow. Use KAW; race_no without leading zero; official date and aware JST post/cutoff. Do not copy hypothetical test cutoffs. Current Authority and actual cutoff must be re-resolved for a separately authorized unknown future race. The workflow enforces cutoff and post-minus-120-second release deadline and then calls signed SOURCE, authority gate and existing Runtime. Capture run ID, terminal gate and verified FINAL; successful job alone is not proof of delivery.

This is an existing declared authorized owner path, not an assistant-tested dispatch or guarantee. If the Run workflow control is absent or returns an error, owner must preserve that exact error and inspect repository Actions policy/installation Actions permission. Do not weaken Runtime guards or bypass a connector refusal. No R06/R07 action was submitted in this investigation.

R05's actual push-triggered run 38700540987 persisted SOURCE/FORMAL records at 16:43 JST. This demonstrates the downstream entry worked for R05, not that R06/R07 were authorized or that direct dispatch was exercised.

## Repair, regression, Production

Main ingress tests re-run: 24 PASS. Existing PR280 candidate ingress tests re-run: 28 PASS. PR280 current queried CI: 13 of14 workflows succeeded; SBO acceptance failure remains. Actual R06/R07 replay is blocked by missing original request/rejection; the evidence is preserved as incidents, not promoted to passing regression cases.

PR280 code subject 9d38b8cc already fixes main's independent moving-HEAD/event-range risk. No duplicate or speculative code patch was added, and that repair is not asserted to fix this connection refusal. PR279 remains separate. Runtime measured at17:31 JST remains f0d23766, fingerprint PASS; no Production update occurred. No numerical formula, Policy, MEC, Capital or Signed Artifact changed.

Next race recurrence remains uncleared for ChatGPT-driven registration. Closing evidence is the original denied operation/error/payload (no secrets) and exact refusal actor, or an owner-native dispatch acceptance/error for an authorized future race. Do not claim root-cause repair from repository tests alone.

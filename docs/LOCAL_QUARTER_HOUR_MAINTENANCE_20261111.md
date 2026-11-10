# KeibaMetrics LOCAL | 15-minute guarded maintenance | 2026-11-11 JST

## Purpose
A separate GitHub Actions worker is scheduled at UTC minute 02/17/32/47 every hour (96 opportunities/day). This is a best-effort scheduled trigger. GitHub can delay or skip schedule starts, especially under load. The worker has a dedicated non-canceling concurrency group and a 12-minute timeout.

## What is actually implemented
- Read-only SHA256/presence verification of existing LOCAL Race-Key entry, dispatcher, gates, owner config, numerical manifest and evidence registry.
- Python syntax checking of four LOCAL runtime entry/gate modules.
- Explicit verification that the existing numerical mapping **declares 29 unique indices**. Declaration is not evidence of numerical calculation.
- Explicit reporting of owner-venue scope and four Consumer flags without changing them.
- Read-only GitHub API survey of up to 30 Race-Key Workflow runs, with 24-hour filtering and separate failure diagnostics. HTTP read retries are bounded at two; formal writes and ambiguous requests are never retried.
- Per-run observation JSON, GitHub job summary, short-lived artifact (7 days). No NAR Raw, Private Store data or credentials are uploaded.
- Fail-closed static validation. API access failure is UNKNOWN, not PASS.

## Not implemented / not claimed
This is **not** a 15-minute AI software engineer. It does not change code, open automatic PRs, re-run LIVE races, sign or verify SOURCE/FINAL, deliver to the user, provision infrastructure, deploy, merge, spend money or buy tickets. The script correctly reports repair_commits=0, live_dispatch=0, signed_receipts_verified=0. Actual unattended source/runtime repair will require isolated execution, trusted credentials, explicit deterministic repair recipes, conflict leases, budget controls and separately approved merge/deploy scopes.

## Authority, rollout and acceptance
- Existing Production, KAW-only owner scope, Current Authority R51 / LOCAL R16 and numerical policy are unchanged.
- No new model, numeric coefficients, S2, OOS registration or v2 enrollment.
- The existing hourly ChatGPT LOCAL maintenance automation is retained, not replaced or disabled.
- A schedule only runs from the repository default branch. This feature branch and draft PR **do not activate the schedule**. Merge requires separate explicit owner authorization after review, and any new billed usage requires approval.
- After merge: record three actual scheduled runs and compare scheduled_at/started_at/completed_at. No SLA can be declared from configuration alone. Investigate missed ticks rather than backdating proof.
- Genuine 15-minute autonomous code modifications should be introduced as a separately reviewed second phase with an external execution actor and private storage. Do not mislabel this monitoring guard as completed auto-remediation.

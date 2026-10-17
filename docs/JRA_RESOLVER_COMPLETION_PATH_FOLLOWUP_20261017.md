# PR303 post-merge Completion Handler correction

Owner approved PR303 HEAD `55650df9e1eec39bcdd08e850211a1206a29e1ac`.
Merge completed as `06dada57254a562ffb6030e9dca2b6886d86b911`.
The approved 17-file diff is exact, and executions/FINAL/RESULT/Learning/pedigree subtrees are byte-identical to the merge's first parent.

Post-merge read-only inspection found a defect in the newly added completion conditions:
GitHub REST `workflow_run.name` contains the dynamic run-name, not the fixed workflow name used by those conditions.
Actual Resolver Run 39000908421 has name `JRA intent 東京 2026-10-17 R8`;
actual failed Autopilot Run 38993239193 has name `JRA race-day autopilot 2026-10-17 loop`.
Both conditions in PR303 therefore evaluated false for the observed production identities.

This follow-up changes exactly two runtime condition expressions to use `workflow_run.path`:

- `.github/workflows/km-jra-race-intent-resolver.yml` for Resolver completion reconciliation.
- `.github/workflows/km-jra-race-day-autopilot.yml` for abnormal Autopilot recovery.

The existing trigger workflow list, main-branch requirement, failure/timeout predicates,
bounded retry count, race-day window, dispatch targets and concurrency are unchanged.
No resolver HTTP behavior, prediction values, BVI, AKI, KRS, MEC, Capital, signing or Source Authority changes.

Regression fixture contains the real API identity/path/conclusion fields of the two failed runs.
The test evaluates both job conditions against both real runs, verifies that only the matching job runs,
and verifies that non-main runs cannot trigger either recovery path.
The predecessor fails this regression; the corrected path conditions pass.

Main's pre-merge live-day worker Run 39005612401 was still executing SHA
`06015affc30aafae39591b283d294c761ea68fc7` when inspected.
The day index still displayed Tokyo R8 as DISPATCHED_RUNNING at 14:16:40 JST.
The correct expired failure checkpoint is merged; live index propagation is not yet proven.
Do not infer updated worker code, corrected live status or unknown-future Delivery from the merge alone.
No worker is cancelled/restarted and no new future activation is issued by this follow-up preparation.

Rollback: revert only this two-condition change if it misroutes completion events; retain signed artifacts,
incident history, PR303 HTTP/deadline repair and all Production prediction policy.
This follow-up has a distinct exact HEAD and requires separate Owner review/merge approval.
The PR303 approval is not reused as approval for a different HEAD.
Live Acceptance, Signed FINAL and pre-post user Delivery remain PENDING.

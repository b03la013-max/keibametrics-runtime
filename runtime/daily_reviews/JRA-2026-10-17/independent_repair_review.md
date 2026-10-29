# PR #305 independent repair re-review

Independent reviewer distinct from implementation agent. Reviewed dc6333f baseline plus current working-tree corrections (not yet committed at review time). This is technical agent review, not GitHub human approval, Owner approval, Deployment approval or Live Acceptance.

## Corrected findings

- CHECKPOINT_TOCTOU (P1): resolved at the Formal Runner caller by `runtime/jra_krs_request_checkpoint.py`. The original preregistered serializer/format remains byte-identical. New bounded interprocess flock spans staging, full pair conflict checks, no-replace publication, directory fsync and return. Existing partial pair can resume only if every existing byte matches. Neither output file is opened for overwrite. Lock lifetime is descriptor-bound, so process death releases it. New helper is Linux-specific, compatible with existing ubuntu-latest workflow.
- DECLARED_SCHEMA_BYPASS (P2): resolved by unconditional known revision/schema validation before legacy/declared contract branches. Unknown declarations still fail closed. Signature verification remains a separate mandatory workflow gate.
- STALE_LIVE_STATE: withdrawn. Actual merge-base PR diff107files does not touch the main-only two live paths; independent three-way merge preserves latest main state exactly.

## New independent verification

Written without calling implementation tests: `/tmp/km_reviewer_repaired_probe.py` exercised24 real multiprocess schedules:12 differing payloads yield one success/one conflict,12 identical payloads yield two matching successes; persisted bytes/metadata match every successful return. A separate process died with `os._exit(77)` immediately after first atomic publication; the next different payload was rejected without completing metadata, and the exact payload completed the original pair. Unknown runtime and unknown schema were separately rejected even under the supported explicit hash declaration. All probes PASS.

Re-ran independent cryptographic checks on23 original signed receipts with a separately written verifier: signatures, receipt hashes, normalized input hashes, canonical output SHA and structured output equivalence23/23 PASS. Archive562members retains exact original hashes. Existing Shadow registration14definition fingerprints remain unchanged and verified. No production numerical/policy or original signed artifact changes observed.

CI re-review: utility pull_request path triggers and pytest command now include the checkpoint sidecar and durable tests. Formal inline Python compiles. Existing push(main) path list remains narrower, so a future direct-main sidecar-only edit could skip this workflow; nonblocking for this PR, whose changed workflow/Formal paths trigger main CI. Symmetric path coverage is recommended maintenance. No new functional blocker found in repaired caller path. The frozen original helper remains unsafe for concurrent direct use by design; production caller must continue importing the durable wrapper, and direct frozen-helper calls are limited to isolated staging.

## Delivery and Learning scope

Actual Delivery cannot be completed truthfully by changing a flag: current route supports canonical publication/readback and GitHub summary, with no proven approved recipient adapter or ACK intake.23 available FINALs remain23available, not23received. Safe existing-record work can normalize audit fields (`delivery_channel`,FINAL SHA,attempt/publication/readback timestamps,ACK UNKNOWN/NOT VERIFIED,failure reason NO_APPROVED_NOTIFICATION_ADAPTER) from persisted evidence; must not invent a send attempt, completion, acknowledgment or retroactive timestamp. New external destination/sending/Activation is prohibited by this request, so actual receipt remains a concrete blocker requiring an Owner-approved existing destination/adapter and fresh recipient acknowledgment.

Learning helper only creates a SHADOW context receipt and explicitly says `prediction_application: NOT APPLIED`. Production caller has no learning digest binding/consumption authority established. A local/replay test can demonstrate context hash/temporal validation, but not next unknown-future Prediction consumption. Existing22Learning states,7late signed-evidence cases and0verifiedconsumption should stay distinct. Safe work is a stage checklist and immutable expected input lineage fields; no retroactive consumption claim and no new Production connection without scope approval. Both actual Delivery and Learning closed loop therefore remain PARTIAL.

## Startup / rollback / readiness

Saved diagnostic exit9 vs deployed uvicorn remains unresolved. Read-only Deployment diagnosis SUCCESS means current platform status, not proof diagnostic config will safely restart. commitHash null, source image tag without immutable digest/source linkage and unknown app-blob hash scope do not verify Git SHA. No speculative start command, redeploy, restart or rollback command should be executed or marked verified. Root user instruction says unsafe next Deploy possibility blocks MERGE-READY; therefore overall verdict remains **NOT MERGE-READY / operational startup provenance and required approvals pending**, even with resolved code findings.

Latest commit CI/exact code hashes should be captured after commit. Mechanical, historical, synthetic and process probes provide regression evidence only; no future race acceptance credit.

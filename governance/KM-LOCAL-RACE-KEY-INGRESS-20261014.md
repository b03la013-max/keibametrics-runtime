# KM LOCAL race-key ingress — candidate handoff (2026-10-14)

Status: NON-PRODUCTION / NO AUTOMATIC PROMOTION / NO SAFETY BYPASS.

## Incident and objective

On 2026-10-14, ChatGPT-to-GitHub create_file calls for KAW R03, R04
and R06 intermittently returned:

> このツールの呼び出しは、OpenAI の安全性チェックによってブロックされました。送信内容を再度確認してください。

The connector successfully created SOURCE files on R04 and R05 and
a full canonical Formal Intent on R04 and R05. GitHub write permission,
Railway external runtime and the repository were available.
Safety-check error detail was not exposed; do not assert a root cause
or treat this as a permission to bypass safety rules.

## New authorized ingress (after explicit review and merge)

The new workflow `.github/workflows/km-local-race-key-entry.yml` accepts
five scalar fields via GitHub Actions Run workflow or authenticated
`repository_dispatch` (event type `km_local_race_key`):

- venue_id (e.g. KAW)
- race_date (YYYY-MM-DD)
- race_no (1..12)
- scheduled_post_at (official post, ISO8601 with +09:00)
- prediction_cutoff (ISO8601 with +09:00)

Example authorized repository_dispatch POST through GitHub's official API
from the repository owner's own authenticated environment:

```json
{
  "event_type": "km_local_race_key",
  "client_payload": {
    "venue_id": "KAW",
    "race_date": "2026-10-15",
    "race_no": "4",
    "scheduled_post_at": "2026-10-15T16:15:00+09:00",
    "prediction_cutoff": "2026-10-15T16:10:00+09:00"
  }
}
```

These dates and times are illustrative, NOT verified future schedules
or dispatches. The operator must use the confirmed official race post.

The workflow only runs on main after authorized merge. It resolves the
current Family Authority from the repository, validates race identity and
prestart timing, checks the canonical external gateway, and invokes the
pre-existing LOCAL SOURCE-first owner. It persists signed SOURCE records
after verifying the receipt.

If a fully result-blind pre-frozen canonical Static for the same race
exists before cutoff, the existing LOCAL runner may execute the entire
Signed FINAL lifecycle; after verified FINAL a separate job continues
official RESULT -> Settlement -> Learning, preserving canonical receipts.

If no frozen Static exists, SOURCE and numerical diagnostic output are
retained, but the report explicitly declares
SOURCE_VERIFIED_STATIC_PENDING / FORMAL_FINAL_NOT_PROVEN.
No Production ranking or bets are invented from indices.

The workflow does NOT convert historical post-start entries into formal
pre-race predictions; does not promote shadow AKI, MEC, candidate numerical
authority; and does not alter R51, Venue canon or frozen Production.

## Remaining blocker

A race-key entry can launch signed SOURCE without writing per-race JSON
through the ChatGPT GitHub file connector, but full autonomous FORMAL
still requires an authorized, frozen Prediction Owner. The connected
chat-owned owner and canonical formal_intents remain unchanged.
This PR addresses intake transport, not an unimplemented prediction model.

## Verification and promotion

Tests: tests/test_local_race_key_ingress.py plus existing SOURCE and
Formal orchestration regression; GitHub CI in
`.github/workflows/km-local-race-key-acceptance.yml`.

Production merge requires review of exact workflow permissions,
preservation of Source/Final/Result receipt verification, timing,
GitHub token scope, OOS integrity and results of CI. Only actual
unknown-future live dispatches can establish operational end-to-end
acceptance. No retroactive KAW R06 completion.

## OpenAI Support — request ready for owner submission

Issue: Intermittent safety-blocking of authorized ChatGPT GitHub connector
file creation. The repo is b03la013-max/keibametrics-runtime.
Timeline (2026-10-14 JST): R03 initially blocked then SOURCE succeeded;
R04 first full SOURCE request blocked then simplified SOURCE succeeded;
R05 SOURCE+FULL succeeded; R06 two SOURCE attempts blocked.
The error is the Japanese tool error reproduced above.
The exact policy trigger was not disclosed. Request an investigation of
false-positive classification and a documented, authorized stable
integration path that retains all safety requirements, not exemption
from content policies. Do not attach credentials, tokens or private keys.

User submission: https://help.openai.com/ (chat bubble lower right).
This repository document is NOT a filed OpenAI Support case.

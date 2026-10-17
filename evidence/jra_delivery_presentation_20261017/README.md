# JRA completed presentation and delivery boundary repair

Verdict: **P0-RECOVERY-PARTIAL / future LIVE ACCEPTANCE PENDING**.

## Actual incident and responsibility boundaries

KYO 2026-10-17 R07 Formal [run 38998786014](https://github.com/b03la013-max/keibametrics-runtime/actions/runs/38998786014), job 117297098102, completed successfully. The actual steps for external execution, FINAL persistence, canonical tree preparation, publication readback and artifact upload all succeeded. FINAL receipt `325f88a709dbd6509d8f62498fba17d4d29880d15e828bae226ddf7baa4ec84c` verifies with the existing Ed25519 trust key. The historical availability receipt observed the exact FINAL/tree at 2026-10-17T03:28:59.873807Z, before 13:15 JST post.

| Boundary | Evidence and conclusion |
|---|---|
| External computation | Actual 200/200 numerical cells, signed KRS actual 5,000, FINAL PASS |
| Immutable persistence | FINAL semantic SHA `6011d0f01c93753240b7e9216add9b18b8a30aad40b092b71110faf117dc9fcd`; unchanged |
| Ticket rendering | Existing exact roundtrip renderer: 6 tickets, 600 yen |
| GitHub availability | Existing immutable availability receipt reports HTTP 200; availability is not destination receipt |
| Notification | Existing `jra_delivery.py` contains publication/readback, no notification sender; sent time null |
| Arrival / ACK | No destination receipt or user ACK; false/null must remain |
| ChatGPT answer interruption | User-reported. Host response/context/display logs are unavailable; exact host cause UNVERIFIED |
| Resume | Existing Single Entry checks FINAL before SOURCE, but rendered only a ticket tree, not a complete ranked answer. This repair adds the completed derivative and compact readback |

The proven application gap is missing durable completed presentation, separate from the unverified host interruption cause. GitHub code cannot promise host response continuation or receipt by a human. No available connected operation provides an external Runtime API to write this ChatGPT conversation. API Conversations objects are not evidence of such a ChatGPT host capability. No new delivery target, notification, paid API, credentials, activation or purchase is added.

## Implementation

- `runtime/jra_presentation.py`: derives a small Markdown answer, a 20-index-per-runner detail JSON and hash manifest from the existing signed FINAL. Binds race, execution, race-time Authority, policy code/fingerprint, FINAL/Receipt/SOURCE hashes and original generation time. Verifies PRE_KRS/KRS/FINAL signatures and signed mirror bindings. Exact existing tree is preferred; a renderer failure uses the unchanged signed per-ticket ledger. PAPER's reference MEC is separate from zero official tickets. A replay or unsigned AKI failure cannot become a Formal FINAL.
- `runtime/jra_delivery.py`: saves the derivative within the existing delivery directory, prints completed text, reads back all three presentation files at an exact published Git ref, and writes a separate presentation availability receipt. Existing FINAL/publication/availability files are not rewritten. Retry preserves saved bytes/timestamps; interrupted writes recover only with matching immutable contents.
- Existing Formal and Single Entry workflows: publish/archive the completed presentation, reuse saved presentation before SOURCE, and check expected race identity. A saved completed answer is checked against the immutable original and read without a live health dependency; this is reuse of creation-time verification, not a new READY/signature claim. An answer missing its saved presentation still requires the normal full verification path. No dispatch, timeout, scoring or purchase policy change.
- Existing continuity CI adds these regressions. No new workflow or new entry point is introduced.

The compact reader is:

```sh
PYTHONPATH=runtime python runtime/jra_presentation.py \
  --directory runtime/jra_delivery/KM-JRA-KYO-20261017-R07 \
  --expected-race-id KM-JRA-KYO-20261017-R07 \
  --expected-final-sha256 6011d0f01c93753240b7e9216add9b18b8a30aad40b092b71110faf117dc9fcd
```

It checks derivative content hashes/identity and does not claim a fresh signature verification. First creation verifies the full original. The Markdown is about 4 KB and details about 44 KB, compared with the original FINAL of 5.3 MB; full calculation traces remain addressable in the immutable original. Consumers should pin the Git commit when reading a manifest and its files together. No Venue Chat host configuration has been silently changed. The specifically named `KM-VENUE-CHAT-FORMAL-SETUP-20261017-R15` was not found in repository search or supplied local source files; requirements in the user's message were followed without inventing its missing text.

## Regression and empirical limits

`regression.xml`: 16 passing tests including the existing renderer suite. Before implementation the new completed-presentation contract failed collection because no such reader/builder existed; this is a missing capability, not a claim that the already successful KYO7 workflow failed. Tests cover exact actual KYO7 tickets/20 indices/three signatures, real KYO5 PAPER 0/0 versus reference 8/800, actual KYO3 status with `AKI_SELECTED_HEAD_WITHOUT_MATERIAL_PAIR`, actual KYO 10/12 R11 replay intent rejection, wrong Race/Authority/SHA, retry byte stability, partial-write recovery, renderer fault fallback and a health timeout after saved publication. Host connection interruption itself cannot be induced/observed through repository tests; compact resume is tested as its recovery mechanism.

`fixture_provenance.json` identifies pinned inputs; `actual_artifact_acceptance.json` records original FINAL hashes, exact ticket totals and derivative hashes. Saved health is explicitly a historical trust snapshot, not fresh READY evidence. The newly generated KYO7/KYO5 presentations were created AFTER post and are historical rendering acceptance only; neither FINAL is regenerated or re-signed. Receipt and GitHub availability existed before post; this new answer did not.

## Release, runtime and rollback

Latest source snapshot for this implementation: main `fbf7191252219a387408efa2d03baed8956c203f`; PR base is refreshed before branch creation. Profile directory resolution still selects R51 (latest effective Current Authority). Production Scope, Static/BVI/AKI/KRS/MEC/Capital sources and signing keys are untouched. All open PRs were checked; none contains this completed-presentation repair. PR297 remains an evidence-only open PR; PR298–301 incident fixes are inherited from main.

Railway read-only observations are in `runtime_observation.json`. KRS deployment `7c7eeb5e-3b5b-496a-b66f-82bd71897d53` and SOURCE deployment `c05f3e85-18ae-4147-821e-97f224c2258c` report SUCCESS and canRollback=true; neither exposes an application commitHash. Application Git SHA remains UNVERIFIED. Saved KRS startCommand exits 9 and is inconsistent with prior live READY/actual receipts; no restart/redeploy is performed. canRollback is a platform capability, not permission to invoke it.

This is JRA C1 presentation/execution correctness, not Family numerical promotion. Other families' owners/adapters/coefficients remain independent and unchanged. Non-numerical independence follows from the changed path set: render/publication and existing JRA workflows only; no prediction owner or numerical source is written. A release must respect existing Owner approval conditions; this PR does not create or claim human review/Owner release approval. Code rollback is a reviewed revert of these presentation/workflow changes while retaining all original signed artifacts and saved derivative history. Railway rollback/restart is not required for this code change and is not executed.

## Remaining acceptance conditions

1. Authorized exact-HEAD merge and main CI; never equate those with live delivery.
2. A next eligible unknown future race completes the existing approved path once; verify its own before-post FINAL and newly published presentation at the same Git ref. Do not replay an expired race or restart Production to obtain evidence.
3. Independently measure FINAL-to-render and FINAL-to-availability from actual timestamps. Notification, destination arrival and ACK stay UNKNOWN until a real approved channel supplies corresponding evidence. This repair supplies GitHub completed-answer retrieval; it does not invent ChatGPT automatic push or user-read evidence.
4. Continue existing official RESULT -> settlement -> signed RESULT -> reflection/learning. Rendering consumes original FINAL only; no result/payout is used as a prediction input. No absent FINAL/PFS is manufactured. New presentation acceptance does not itself prove a new closed-loop settlement.

Oct18 remains the fixed 36-race denominator. Pre-registration is not live execution; all future FINAL/Delivery/Settlement successes must be measured when those races run. No prediction accuracy, PFS improvement or 100% one-trigger delivery success is claimed.

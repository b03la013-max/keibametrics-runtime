# 2026-10-18 JRA 36R — measured review and unmerged repairs

Production remains R51, resolved from main d1b711d63c50d7f14e2d2ab2a96f2b3ec7e72b8f. 34 signed FINAL/RESULT pairs; 2 AKI_NO_BET without Production FINAL. All 36 registrations are represented. The 2 NO_BET official observations are reused from the existing separate Candidate official acquisition; they are not Candidate Prediction results relabelled as Production. Their canonical Production zero-bet Learning is missing.

## Concrete outcomes

- KRS diagnostic repair: capture actual request Roles in summary, compare P3 using the same SSR-T3 criterion as the proposal producer, and bind historical evaluation to frozen Production Roles/ranking. No Engine, threshold, Role selection or ticket-policy change.
- Learning producer: new states can carry actual UTC observation time and explicit FAMILY-CANDIDATE scope. Existing states and reviews are immutable; corrected official results require a new review revision, not silent rewriting.
- Research sidecar: Winner re-audit, Head-local P2, Pair-third, existing actionable KRS, learning-on/off and CORE/PROTECTION comparisons. Same positive-feature logic applies to all qualifying runners. Nonblocking calls in existing Formal and RESULT workflows freeze/persist/settle sidecars and maintain a distinct-race tracker.
- Existing formal paths continue unchanged if a Shadow fails; failure reasons are retained in summaries. No new workflow dispatcher, paid API, external notifier or automatic promotion.

## Artifacts (combined to avoid duplicate reports)

| Requested outcome | Existing placement / field |
|---|---|
| JRA_20261018_36R_FORMAL_REVIEW | JRA_20261018_36R_FORMAL_REVIEW.json.gz |
| PREDICTION_FAILURE_MATRIX | PREDICTION_FAILURE_MATRIX.csv + JSON races |
| STATIC_AKI_EVIDENCE_AUDIT | JSON races[].runner_audit / aki / model_market_disagreement |
| KRS_INCREMENTAL_UTILITY | JSON krs_role_comparison_totals / races[].krs_recomputed / shadow_comparison |
| VENUE_DAILY_REVIEW | JSON venues / venue_canon |
| CAPITAL_ROBUST_PFS | JSON summary / bet_type_pfs / tier_pfs / shadow_comparison |
| LEARNING_CONSUMPTION_PROOF | JSON learning + temporal regression tests; actual consumption remains zero verified |
| CORRECTNESS_REPAIR | runtime/jra_krs_measurement.py, runtime/post_result_learning.py, both existing workflows, tests/test_jra_role_learning_repair.py |
| FORWARD_OOS_SHADOW | runtime/jra_role_learning_shadow.py; proposed existing workflow connections |
| NEXT_RACE_READINESS | EXECUTION_CONTEXT.json, RUNTIME_READINESS.json, limitations below |

SIGNED_RESULT_VERIFICATION.json preserves the unchanged envelopes downloaded from 34 canonical Actions checkpoints and binds each to the canonical request hash. Signatures were checked locally using the live Runtime Ed25519 public key. All 34 frozen FINAL signatures and signed ticket payloads were independently verified with jra_delivery.verify_signed_final. No historical FINAL/RESULT/learning file was modified.

## Measured results

Frozen recommendation only: Tokyo 17,500/19,670 yen (112.40%); Kyoto 14,400/10,830 (75.2083%); Niigata 25,000/0 (0%). Total 56,900/30,500, PFS 53.6028%, loss 26,400. 31 positive-investment races, 3 zero-stake FINALs, 2 non-FINAL AKI_NO_BET. Actual purchases unknown.

Role denominators are 34 FINALs: W17, P2=13, P3=19, semantic ordered pair6, semantic exact3. A role capture is not necessarily a purchased correct ticket. Missing W is split into 8 role-migration and 9 discovery-or-role cases; the latter are not fully causally separated. Canon revision=NO at this stage, Promotion=HOLD for TKY/KYO/NGT. Venue mechanism measurements remain incomplete; course geometry grouping is not full canon implementation.

Largest return Tokyo11 accounts for 62.2951% of all returns. Removing it and its stake gives PFS21.2569%; top2 removed11.7202%, top3 removed6.5619%. Median race PFS0, maximum chronological drawdown35,300 yen, longest zero-return streak12. Ordering is official post then race ID, not verified actual purchase cash flow.

21 correct-outcome role-zone rescues and 2 potential nonconfirmations are diagnostic counts, not 21 winning tickets or 2 actual harms. 10 races have an actionable post-result UNIQUE-RESCUE label. Full proposal width611 includes false pair194 and false exact322. Research cost is explicitly included: actionable KRS arm requires120,700 yen vs baseline56,900. It is not automatically purchasable or proven superior. Every new arm was designed after this day; all 2026-10-18 comparisons are exploration/regression and earn zero forward OOS credit.

## Verification and independent review

Combined targeted regression: 62 tests + 9 subtests PASS, then added backdated-commit negative regression: role/learning suite9 tests +4 subtests PASS. Both workflow inline Python and YAML PASS, git diff --check PASS. Actual Tokyo11 and Kyoto2/4/10 positive controls preserve frozen baseline payout; Tokyo8 remains a negative control. Existing immutable signed tickets were not changed.

A separate review agent independently reproduced KRS false-rescue counts, Source/digest and proposal omissions, leakage cases, costs, and a backdated Git timestamp vulnerability. All blocking code findings were addressed. Independent review final code verdict PASS; external human review is not claimed. Reviewer ran22 tests+4 subtests and workflow syntax checks independently. Future measurement remains pending.

## First blockers / next allowed actions

1. Existing PR306 is extended; its new HEAD needs Owner approval before Merge. PR305 approved HEAD is untouched and remains subject to its existing real Railway isolated deploy/rollback condition. No provider-deploy retry or bypass was attempted. PR307 remains separate.
2. Git committer dates are mutable and cannot independently prove pre-result persistence. Sidecars can freeze/settle, but OOS eligibility stays false until server-side receipt time plus matching frozen artifact bytes are verified. The tracker does not auto-promote at60 races/3days/2venues.
3. Today34 Learning states have no effective_time; verified actual next-input consumption=0. New producer plus mechanical binding test is not historical live consumption proof. SAME-DAY and meeting-specific numerical adaptation are not activated.
4. The2 NO_BET outcomes lack canonical Production zero-bet Learning; no signed RESULT was fabricated for them. Static-only pre-KRS ticket counterfactual is not identifiable from an independent frozen ticket set and remains UNKNOWN.
5. No notification/recipient ACK records were found. Canonical publication/readback is separate from user receipt. No external send was made.

Production Merge HOLD; Shadow forward OOS BLOCKED pending Merge and independent server witness; model quality/Robust PFS improvement FORWARD OOS PENDING. Revert this PR's code/workflow additions to roll back; do not rewrite signed artifacts. Production Railway deployment remains7c7eeb5e-3b5b-496a-b66f-82bd71897d53; Runtime READY; deployed Git SHA unknown. No deploy/restart/stop was done.

CI caught LOCAL preregistration coupling to the shared KRS file. Its exact main bytes were restored. The JRA-only adapter contains the measurement repair; LOCAL code, metrics and frozen definition hashes are unchanged.


## PR306 merge and next-race continuation — 2026-10-18

Owner approved exact HEAD `5f9165b81cc7a1ddb341af7c44f219a63a6523e0`.
Merged as `408def14c7e32515ccefbad8af6ae39f41b70f26`; approved and merged trees are identical. PR CI 9/9 and merge/main CI 19/19 succeeded. Main subsequently observed at `b6ca787d10b1984f303aabaa73965c9046bdb4cd`. No signed historical artifact, Production coefficient, Engine, parameter map, Signer, AKI, MEC or Capital policy changed. Production Deployment `7c7eeb5e-3b5b-496a-b66f-82bd71897d53` remains SUCCESS/READY; deployed Git SHA remains UNVERIFIED. No Deployment/Restart/stop was performed. Rollback for merged code: revert PR306 code/workflow changes while preserving immutable artifacts. PR305 provider isolation gate remains unresolved and was not bypassed.

Unmerged continuation is consolidated into existing PR307. The existing Actions upload now contains the exact Shadow sidecar. RESULT checks fixed repository/main workflow/run attempt/head/code bytes, immutable archive digest and exact content, with server creation and update times no later than Cutoff. Git dates alone never confer OOS eligibility. New fields separately record losing added-ticket stake (False-positive Cost), added winning stake and return. These changes do not generate purchase instructions or promote a Candidate.

The existing zero-bet Workflow had five valid pending decisions but selected the oldest four; Kyoto R05 fell outside that batch. Selection now prioritizes the current meeting, and individual OIDC/decision-validation failures cannot block valid siblings. Regression executes the actual Workflow Python with official-network and attestation boundaries mocked, including the actual five pending terminal records. This is not proof of official capture: both Oct18 zero-bet canonical Learning records still await the existing OIDC Workflow's real execution. No unsigned observation was relabelled verified.

Focused regression: 53 tests + 32 subtests PASS. YAML and embedded Python compile, whitespace checks PASS. Separate technical reviewer independently passed 26 tests + 13 subtests, server-witness/NO-BET adversarial probes, and the combined Delivery wiring review; this is distinct from Owner authorization and from actual provider acceptance.

The 34 FINAL publication/readback records were audited; all 34 notification and recipient ACK states remain UNVERIFIED. No external message was sent. Actual next-race Learning consumption remains 0 verified; original 34 states are not backdated. New timestamped states can be bound only when actually available before the next Source freeze. True Forward OOS remains PENDING, not ACTIVE, until the unmerged code is approved and a future pre-cutoff artifact is independently verified. Prediction improvement is unproven.

Retrospective cost measurement, same 31 invested formal races (all arms designed after results; exploration only; not OOS or actual purchase):

| Arm | Added capital (yen) | Losing added-ticket stake (yen) | Added-ticket return (yen) |
|---|---:|---:|---:|
| Winner Re-Audit | 45,900 | 45,100 | 62,670 |
| Head-local P2 | 42,600 | 41,200 | 39,180 |
| Pair-conditioned Third | 11,500 | 11,100 | 3,190 |
| KRS Actionable | 60,700 | 59,400 | 94,700 |

Baseline is 56,900 yen / 30,500 yen return. Unequal-budget arms do not establish improvement; equal-budget/equal-ticket diagnostics and forward comparison remain separate. Full machine-readable observations are appended to existing EXECUTION_CONTEXT.json.

# AKI Capital closure repair, 2026-10-11

## Reproduced cause

Tokyo 11R (`KM-JRA-TKY-20261011-R11`) signed FINAL preserves the old Static Owner (`JRA-STATIC-PREDICTION-OWNER-EXECUTABLE-CANDIDATE-20261010`). Its actual ticket set is 132 EXACTA plus 1,452 TRIFECTA tickets. Each of 132 pairs has 11 purchased thirds. The old score-cluster selector created the purchased Cartesian universe before MEC; MEC faithfully closed those asserted material units. Capital used RECOMMENDATION_ONLY and no ceiling. All-stage PASS therefore did not establish sensible purchase width.

The race intent specified R48. Main now contains R49 and the existing Full20-derived AKI v2 width policy. Replaying the same frozen request with that existing policy yields 4 EXACTA + 16 TRIFECTA = 20 tickets / 2,000 yen. This is an unsigned post-freeze REFERENCE; this change does not rewrite the immutable FINAL, change settlement, or treat this replay as forward OOS.

## Actual changes

* Add `jra_aki_capital_preflight.py`. Bind the existing authorized owner's AKI width decision to frozen W/P2/P3 roles, purchased pairs/thirds, actual MEC tickets, legal stake increments, count and capital. Reject missing decisions, re-expansion, duplicate/invalid tickets and false official-v2.1 requirements. Persist the report in the Formal Runner's stage manifest and FINAL prediction package before capital and signing.
* Use the recorded Family 10,000-yen ceiling when the intent has no capital policy. Preserve an explicit owner override, including RECOMMENDATION_ONLY. The ceiling never selects runners, changes semantic coverage, or fills unused funds. Excess required capital goes to PAPER according to the existing Family default. Existing signed FINALs remain untouched.
* Implement an independent official-v2.1 component verification function. It consumes externally verified source-bound, registered W-AKI, P2-AKI, P3-AKI, ASI, RSI, external-change and solid-finish-correction components. It reproduces Central v2.3 article 36 exactly: `.30 W + .20 P2 + .20 P3 + .20 RSI + .10 external - correction`; ASI stays separate. Article 35's `.45 P2 + .55 P3` is compatibility display only. No numerical mapping, fallback scores, probability, EV, fixed ticket-count policy or clamp is invented.

## Formal v2.1 is still not complete

The attached Central v2.3 requires separate P2/P3 components, evidence-based column decisions and explicitly forbids AKI-total-only fixed ticket counts (articles 423, 440, 453). R49's `aki_capital_bridge_restoration` explicitly states `NOT_IMPLEMENTED_IN_CURRENT_20-INDEX MATERIALIZATION` and `EXPLICIT_GAP / NO_SYNTHETIC_AKI`.

The existing R49 owner uses a Full20-derived proxy labelled UNVALIDATED, pooled P-AKI, and old v1.1 fixed formation bands. Its coefficient formula is not official v2.1. It is not changed or promoted by this PR. The new official verification function is a reusable gate, not a completed official evidence-to-AKI calculator or a live v2.1 selector. Official rule IDs, term mappings, complete evidence and evidence-based reviewed column decisions still need a separately authorized implementation. Supplying a signed component package alone does not implement that selector. Explicitly requiring OFFICIAL_V2_1 while using the proxy blocks rather than silently downgrading.

A retained synthetic counterexample proves the existing proxy does not guarantee increasing valid point counts with more heads: a stable nine-runner case produces 10 tickets; a flat sixteen-runner case with shared column ranks produces 8, because heads overlap rows 2/3. This must not be hidden by claiming all stable/volatile cases are solved. Central's column-specific requirement is stronger than a single band table.

## Validation

45 focused tests plus 20 unittest subtests passed, covering official formula arithmetic, separate ASI, missing/forged component rejection, real 1,584-to-20 replay, immutable old input, budget/PAPER routing, no budget fill, width re-expansion rejection, existing Static/handoff/MEC mechanics and tree rendering. Full20 index values, rankings, KRS settings and engine are unchanged.

The workflow's embedded Python is syntax-checked. No live race execution, signing, Authority activation or empirical accuracy/PFS claim is made. This is a reviewable change on a repair branch; default budget behavior changes only when that branch is merged and deployed. The capital-policy acceptance script also passed.

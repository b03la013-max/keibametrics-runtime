# OHI 2026-10-06 Daily Review — R42 implementation

R42 inherits R41 and absorbs these changes into the existing owners, following DELETE → MERGE → ABSORB → SIMPLIFY → REPLACE → ADD. It creates no separate execution architecture. Production Prediction Weight, KRS physics/Engine, parameter_map, MEC-R3 selector, Production Capital Policy and OHI Venue Canon are unchanged.

## C1 correctness

Official dead heat is a normal result terminal. Competition ranks (1,1,3 etc.) generate all permitted winning selections; every official exacta, trio and trifecta selection/amount must be published and verified. Missing/contradictory ranks, winners, identity or raw digest still HOLD. No invented order within a tie. Existing unique-result callers retain flat payout compatibility; multiple winners use selection-indexed payouts and explicit winning selections.

The existing shared settlement owner now settles frozen tickets for Production and research consistently. Official excluded/scratched runner evidence refunds each affected ticket once, before payout matching. Refund is cash, never a hit. Gross PFS = (winnings + refunds)/original frozen stake. At-risk capital = original stake − refunds; refund-adjusted PFS = winnings/at-risk capital. All-refund denominator yields UNKNOWN. The RESULT API recomputes and validates the new financial evidence against the immutable signed FINAL, then signs both measurements. Partial payouts cannot become zero-return completed settlements.

MEC-R5 tracker resolves canonical execution FORMAL/OFFICIAL_RESULT/RESULT manifests, pre-result shadow, content digest, binding attestation, verified receipt evidence, race/source/chronology and signed FINAL/RESULT hashes. It recovers original arms without regeneration. Corrupt canonical evidence cannot fall through to legacy. Older execution protocols without this canonical evidence retain their verified legacy path. The eight OHI settled races are recaptured with original Frozen SHA; 2R without signed RESULT remains pending. Signed historical artifacts are never rewritten to inject new policies or refund facts.

Before FORMAL, signed SOURCE Active Runner Universe must equal the request runners; role/pair/third references must all be active. Require at least 180 seconds to the release deadline for FORMAL, in addition to the existing 120-second pre-post release buffer. Mismatch or inadequate margin holds before KRS/formal work. Source facts are not silently rewritten to fit a prediction.

## C2 absorbed diagnostic extension

R40 Pair Residual plus independent KRS actionable support yields PAIR-REVIEW, with no purchase authority. Hard exclusions win. Pair-local third terminals distinguish THIRD_SET_PROTECTION from THIRD_EXACT_MATERIAL: only explicit Pair-local material/purchase disposition with sufficient direct reason can enter the new selective exact arm; global P3/UNKNOWN is insufficient.

Three coverage measures are separate: prediction's semantic top-three set, a frozen exact ticket carrying any permutation of the set, and an actual unordered TRIO ticket carrying that set. Wrong permutation never implies unordered monetization.

Freeze market selection payout ranges with source/time/digest. Prices older than 300 seconds or after diagnostic freeze, missing prices, invalid ranges or bad digests yield UNKNOWN. Report capital-to-selection-payout mismatch; this is not probability, portfolio EV or a promise of profit. Economic review may suggest CORE-ONLY/PAPER/NO-BET in shadow only. Protection burden uses frozen MEC PROTECTION/TAIL stake divided by total stake; unclassified tiers remain UNKNOWN. Protection capital versus market payout range/ceiling is a measurement; no fixed burden threshold or automatic deletion is authorized.

UNKNOWN != WEAK and UNKNOWN != MUST PURCHASE. Preserve semantic alternatives independently from capital commitment.

The new protocol KM-LOCAL-DAILY-IMPROVEMENT-20261007-R1 starts on 2026-10-07 00:00 JST. Its arms are Production R3, Pair-local Selective Exact, Static×KRS Consensus Core 3 and Core 4. Consensus uses static top four intersected with uncalibrated KRS top-four role support, ordered by frozen static ranking. Core arms filter frozen set/pair/local-exact tickets only; insufficient consensus/tickets yields PAPER and no paired-cohort credit. No Production recommendation is changed.

Use a separate first-30 paired cohort with at least three race days. Every arm freezes inside the existing diagnostic digest bound into Signed FINAL; verified official Signed RESULT is required. 2026-10-06 and earlier are regression only for the new protocol. Existing R5/Common Exact/R41 selectors and cohorts are unchanged. Compare PFS, capital, return/profit, hits, hit-but-loss, drawdown, normalized exposure and single-race dependence. Human review and explicit promotion are required; automatic promotion is forbidden.

Existing Phase B forward definition pins retain exact historical protocol/hash pairs across these C1 settlement repairs. This is exact compatibility registration, never a wildcard for arm or numerical changes. All historical pre-result captures remain immutable and validate.

## Evidence limits

9R's supplied Daily Review exclusion reproduces refund 2,900 yen, at-risk capital 16,800 yen and refund-adjusted PFS 164.464286%. Its older canonical official snapshot contains only the top three and no exclusion row, so this corrected replay is regression evidence, not a rewritten signed official settlement. 2R supplied published winning payouts reproduce 1,880 yen; its official RESULT terminal must be acquired/signed by the normal live route after release of this code. No corrected historical result signature or new-cohort OOS is claimed by local acceptance.

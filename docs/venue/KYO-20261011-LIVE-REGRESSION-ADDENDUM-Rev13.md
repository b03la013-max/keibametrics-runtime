# 京都競馬攻略条項 v1.0-KYO-CANDIDATE｜2026-10-11 Live Regression追補 Rev.13

**Profile:** `KM-JRA-KYO-20261011-LIVE-REGRESSION-ADDENDUM-REV13-R1`  
**Status:** `VENUE LIVE REGRESSION / NON-PRODUCTION / NON-NUMERICAL / NO-CANON-CHANGE-REQUIRED / PROMOTION-HOLD`  
**Review date:** 2026-10-11  
**Venue:** JRA Kyoto (KYO)  
**Baseline Venue Candidate:** `京都競馬攻略条項 v1.0-KYO-CANDIDATE` (2026-10-03, user-supplied full text; SHA256 `31095157f6aa027d986e43963f3edea10edaf67341189660bbf3982ccc5d3cab`)  
**Previous Canon audit:** [2026-10-05 Rev.9](../../runtime/venue_audits/KM-JRA-KYO-20261005-REV9-CANON-AUDIT.json), verdict `NO CANON CHANGE REQUIRED`.  
**Review-time Family Authority:** [R50](../../profiles/KM_FAMILY_CURRENT_AUTHORITY_20261011_R50.json), effective **2026-10-11 16:58:10 JST**. All 2026-10-11 races must be judged with their own frozen race-time authority. **R50 AKI v2.1 is not retrospectively applied to earlier signed FINALs.**

> This document is an additive regression and learning observation, **not** a replacement Kyoto Canon, promotion, production scoring patch, or wagering mandate. Links point to frozen/runtime evidence in the same repository. Independently refetching JRA's live official result pages was **not** performed by this audit; GitHub result artifacts include official-source labels and hashes, whose provenance and external verification statuses remain separate.

## 1. Canon revision decision

| Gate | Decision |
|---|---|
| CANON REVISION REQUIRED | **NO** |
| KYOTO LIVE REGRESSION UPDATE | **YES** |
| NEW KYOTO NUMERICAL WEIGHT / FIXED STYLE BIAS | **NONE** |
| CURRENT VENUE CANDIDATE | **KEEP v1.0-KYO-CANDIDATE** |
| EXISTING PRODUCTION AUTHORITY / KRS / MEC / CAPITAL | **UNCHANGED** |
| PROMOTION | **HOLD / NO AUTO-PROMOTION** |
| NEXT UNKNOWN FROZEN OOS | **TEST NEXT (diagnostic comparisons only)** |

Reason: the three designated Kyoto results reveal material *discrimination*, *Third discovery*, and *capitalization* questions, but do **not** establish a replicated, specifically Kyoto-induced failure of the existing course mechanisms. Common engine conversion and capital problems must not be reimplemented in Venue Canon.

## 2. Complete 2026-10-11 Kyoto race-day execution snapshot (selection-bias guard)

Source: [race-day status](../../runtime/jra_race_day_status/2026-10-11.json). This is a **day-status coverage review**, not an independent all-race pace/geometry analysis.

| R | Runtime state | Frozen recommendation investment | Recorded recommendation return | PFS |
|---|---|---:|---:|---:|
| 1–5 | MISSED_WINDOW (5 races) | — | — | N/A |
| 6 | EVIDENCE_NO_BET | 0 | — | N/A |
| 7 | SETTLED_SIGNED_RESULT_LEARNED | ¥15,500 | ¥31,640 | 204.13% |
| 8 | EVIDENCE_NO_BET; separate Candidate lane | 0 | — | N/A |
| 9 | SETTLED_SIGNED_RESULT_LEARNED | ¥41,300 | ¥0 | 0.00% |
| 10 | SETTLED_SIGNED_RESULT_LEARNED | ¥64,400 | ¥3,370 | 5.23% |
| 11 | SETTLED_SIGNED_RESULT_LEARNED | ¥6,000 | ¥0 | 0.00% |
| 12 | SETTLED_SIGNED_RESULT_LEARNED | ¥52,000 | ¥42,300 | 81.35% |

**Five Production frozen recommendation settlements only:** ¥179,200 investment; ¥77,310 return; **−¥101,890** virtual result; **43.14% investment-weighted recommendation PFS**. No race in these five is recorded as actual purchased (`NOT_PURCHASED_RECOMMENDATION_ONLY`). Do not treat this as Actual PFS. Production no-bet races and missed-window races contribute to execution coverage but not to a fabricated zero-return betting denominator. Candidate R8 is excluded from Production totals. Race 9–11 predictions/individual failure causes were **not** independently decomposed in this addendum.

## 3. Race-specific observations and owner attribution

### KYO R07 — turf 1800m, 11 runners: prediction capture and KRS-Static disagreement

Frozen [Production result](../../runtime/results/KM-JRA-KYO-20261011-R07.json): result **9→2→10**, winning EXACTA **9→2** (¥6,890/¥100) and TRIFECTA **9→2→10** (¥24,750/¥100). 155×¥100 frozen recommendation, ¥31,640 return, **204.13%** recommendation PFS. The user-supplied earlier review reports Static ranks of 9=3rd, 2=2nd, 10=4th and KRS winner-appearance ranks of 9=1st, 2=2nd, 10=3rd. The result artifact independently substantiates the top-three and settlement; the exact KRS ranks here are retained as a **prior review observation**, not newly independently re-executed KRS.

- **What worked:** W/P2/P3 capture, ordered pair, exact third, paid ticket conversion.
- **What remains uncertain:** KRS winner-rank advantage over Static may be incidental; #9 was already in W, so **not** an attributable KRS unique rescue.
- **Venue question:** In **KYO-T1800-OUT**, do pre-cutoff hill restraint, downhill launch, 4C momentum and flat sustain observations explain Static/KRS rank disagreements consistently?
- **Owner:** Venue **diagnostic** for course-dependent explanation; Static-vs-KRS arbitration and ticket-width policy are **COMMON**.
- **Action:** KEEP course mechanism; pre-register disagreement evaluation; do not automatically substitute KRS head.

### KYO R08 — dirt 1800m, 16 runners: Candidate P3 discovery miss

Production state: [race-day status](../../runtime/jra_race_day_status/2026-10-11.json) **EVIDENCE_NO_BET / Full20 0/320**, no valid purchased Production ticket or Production PFS. Separate [frozen Candidate settlement](../../runtime/source_candidate_oos/KM-JRA-KYO-20261011-R08/settlement.json): **7→12→4**; Candidate ranks 7=6th, 12=3rd, 4=11th; W/P2 captured but P3 not captured. Candidate **30 exacta + 150 trifecta = 180 tickets**, ¥18,000 hypothetical stake, **¥23,520** exacta return, **130.67% Candidate frozen-recommendation PFS**; ¥18,000 exceeded the referenced ¥10,000 Candidate capital cap and is **not** an executable capital-compliant performance claim.

The separate [pre-start PAPER preview](../../runtime/source_candidate_oos/KM-JRA-KYO-20261011-R08/candidate_forecast_brief.json) contains **20 tickets / ¥2,000**, using only heads 2 and 15; it dropped winning head 7, and yielded **0% hypothetical PAPER PFS**. PAPER and Candidate full-MEC are separate portfolios. The exact 7→12→4 trifecta (¥486,670 per ¥100 in the stored result) was **not** in the 180-ticket Candidate set.

- **First material Candidate prediction failure:** global **P3 discovery/role omission** for #4, preceding any pair-local Third conversion. Its absence from 7→12→4 is a downstream consequence, **not** evidence that MEC dropped an existing correct Candidate P3.
- **Candidate KRS:** the prior review reported an `ADD_P3_SHADOW` / `AUDIT_ONLY` observation for #4; [stored utility attribution](../../runtime/source_candidate_oos/KM-JRA-KYO-20261011-R08/settlement.json) records **KRS P3 rank 11**, role-zone signal, **rescue_count=0**, **actionable_proposal_width=0**, and **no Production change**. **Audit attention ≠ actionable/verified unique rescue**; no hindsight P3 promotion.
- **Evidence quality:** #4's observed closing/position subfeatures warrant review, but the stored attribution also lists **42 missing source features**. They do not establish a calibrated P3 probability, and results must not be used to backfill pre-cutoff evidence.
- **Venue question:** In **KYO-D1800** worlds FRONT-SURVIVAL / STALK-CONTROL / EARLY-PROGRESSION / PACE-COLLAPSE, can pre-cutoff progression, pressure, closing quality and reproducible position evidence identify *limited* low-rank P3 re-audit cases?
- **Owner:** Venue **course-world diagnostic only**. P3 role promotion, KRS rescue adoption, head-local third, 20-ticket PAPER head loss, and capital policy are **COMMON**. Production index closure failure remains separate.
- **Action:** TEST NEXT in preregistered SHADOW; no global P3 cutoff relaxation.

### KYO R12 — turf 1600m, 16 runners: correct exact ticket but capital dilution

Frozen [Production result](../../runtime/results/KM-JRA-KYO-20261011-R12.json): result **3→1→4**; exacta ¥6,570/¥100, trifecta ¥35,730/¥100; 520×¥100 frozen recommendation, ¥42,300 return, **81.35%**, virtual loss **−¥9,700**. Prior review reports the 2nd/3rd finishers at static ranks 6 and 5, respectively, so a uniform top-four truncation would miss the correct exact ticket.

- **What worked:** W/P2/P3 and exact-order ticket coverage.
- **What did not:** conversion into an efficient capital footprint; 520 tickets for a portfolio that lost money. An R50 AKI reference of 16 tickets was PAPER/unsuitable for claiming preserved capture; the race-time FINAL predates R50 effective time.
- **Venue question:** Which **pre-cutoff** pace pressure, downhill control and speed-sustain clues can predict risk of early-pace exhaustion? The reported 600m sectional 33.5 sec is **post-race observation**, not itself a pre-race predictor.
- **Important missing check:** official **1600m INNER vs OUTER configuration is not proven by the reviewed intent fields**. Do **not** apply the outer-only geometry mechanically; Article 18 requires configuration resolution before Venue mechanism attribution.
- **Owner:** Venue pace/geometry **diagnostic** only; AKI W/P2/P3 column widths, ticket density, MEC and Capital are **COMMON**.
- **Action:** KEEP Article 18, preregister configuration-qualified pace stress diagnostic. Do not cut all W/P2/P3 at arbitrary fixed ranks.

## 4. Non-Kyoto negative controls: do not import general failure as local Canon

[Tokyo 11R result](../../runtime/results/KM-JRA-TKY-20261011-R11.json): exact top three **16→15→11**, but **1,584 tickets**, ¥158,400 frozen recommendation, ¥9,600 payout, **6.06% PFS**. This is a clear **COMMON semantic/materiality/capital over-expansion** example, not evidence for a Kyoto geometry factor.

[Tokyo 12R result](../../runtime/results/KM-JRA-TKY-20261011-R12.json): **10→8→1**, but winner #10 ranked 14th and outside the head candidates in the earlier review; **306 tickets** and ¥0 payout. Winner discovery upstream is the primary research issue. Ticket compression cannot create a winner that was never discovered. KRS SIM-XDI audit signal, if confirmed, remains uncalibrated/shadow.

Do not use the Tokyo cases as Kyoto-specific numeric training samples. Use them as **failure-taxonomy and COMMON-owner comparison controls** only.

## 5. Existing Kyoto Candidate articles and disposition

| Existing article | Regression relationship | Decision |
|---|---|---|
| Art. 18 — KYO-T1600-IN/OUT | KYO R12; inner/outer and pace qualification required | KEEP, no new bias |
| Art. 19 — KYO-T1800-OUT | KYO R07 Static/KRS disagreement | KEEP, diagnostic comparison |
| Art. 29 — KYO-D1800 | KYO R08 P3 omission under multiple pace worlds | KEEP, diagnostic comparison |
| Art. 41 — Kyoto Re-Promotion Trigger | Candidate re-audit only; no automatic role promotion | KEEP |
| Arts. 42–43 — Pre-race Manifest/Multi-World | Require observed geometry and prior world freeze | KEEP, enforce existing |
| Arts. 44–46 — Post-result prohibition/Learning | Distinguish observed result from predictive facts | KEEP, append these cases |
| Arts. 47–50 — Cause/Regression/Promotion | No unproven Kyoto cause code or numeric promotion | KEEP / HOLD |

This addendum **does not create a v1.1 Kyoto Canon**. The existing v1.0 full text remains authoritative only in its already designated NON-PRODUCTION candidate scope.

## 6. Preregistered next-unknown-Kyoto-OOS diagnostic matrix

All feature availability, race identity, equipment changes (if authorized), inner/outer, course rail, source time, index provenance and hypothesis arm must be **timestamped before start and committed/frozen**. Compare identical races/time cuts and retain losing examples. DO NOT backfill or use later odds or finishes.

| Diagnostic arm (all NON-PRODUCTION) | Pre-race condition | Primary outcome | Failure condition / cost |
|---|---|---|---|
| **A T1800 Static-vs-KRS** | KYO T1800 OUT; both ordered static and KRS head ranks frozen; pre-cutoff hill/downhill/position evidence present | Winner rank delta, W capture at same width, unique KRS improvement | KRS non-improvement, more false heads, wider purchase cost |
| **B D1800 P3-world re-audit** | KYO D1800; fixed candidate W→P2 pairs; pre-cutoff world, closing/position facts; uncalibrated KRS flags segregated | New **eligible** P3/exact captures and rescue density, measured against new P3 additions | Added P3s/false exacts/capital exceed incremental capture; NO change to Production |
| **C T1600 pace stress** | INNER/OUTER confirmed; pre-cutoff predicted pace + runner position/closing evidence | W/P2/P3 rank accuracy versus baseline, top3 and course-specific discrimination | No OOS gain, losses on positive controls or inner/outer leakage |
| **COMMON control: widths/capital** | Same frozen semantics, Production AKI version/effective time, shadow widths fixed in advance | Correct-ticket retention, ticket cost, capital efficiency, weighted and robust PFS | Head/Third capture discarded or portfolio gain depends on post-result selection |

No new constants, KRS adoption rules, conditional probabilities, arbitrary 30% boost, fixed ticket cap or market EV are enacted by this diagnostic specification. A legitimate numeric variant would require separate preregistration, owner authority and OOS promotion.

## 7. Required evidence ledger and measurement

For each new observation record:

`race_id, pre_start_at, race_time_authority, family, venue, surface, distance, inner_outer, rail, condition, source_sha, source_timestamp, signed_source_status, runner_universe_sha, feature_availability, numerical_closure, static_prediction_hash, krs_input/output/receipt_hash, static/KRS role ranks, AKI_version/effective_time, W/P2/P3, pair, third, semantic_universe, MEC, ticket/stake, frozen_final_sha, result_source_sha, settlement_status, actual_purchase_status, first_material_failure, dominant_pfs_loss_owner, candidate_arm, preregistered_at, oos_eligibility, learning_generated_at, learning_delivered_before_next_cutoff`.

Outcomes: winner/P2/P3 rank and capture **with widths**, pair/exact capture, KRS incremental utility (unique rescue vs shadow alert), false-added heads/thirds, ticket count, investment-weighted PFS by lane, capital cost per incremental true capture, hit-but-loss, largest-win-excluded PFS, top3-excluded PFS, drawdown and NO-BET rate. If data are absent mark `UNKNOWN`, not zero.

Formal improvement comparison requires preregistered, future frozen OOS plus explicit approval under Current Authority; no automatic promotion at 30 samples or any other count.

## 8. Common-owned action register (no new Kyoto runtime)

1. **JRA Prediction / P3:** evaluate true low-rank P3 discovery and head-local Third conversion as separate failures; source example KYO R08, shadow audit must show false positives and extra capital.
2. **KRS Utility:** Static-vs-KRS divergence (KYO R07), P3 shadow alert with 0 actionable rescue (KYO R08); require verified structured evidence and incremental comparison, not simulated rank-as-probability.
3. **JRA AKI / W/P2/P3 selection:** avoid fixed top-four truncation (KYO R12), prohibit retroactive R50 width; evaluate actual current policy only in new future races.
4. **MEC / Capital:** preserve semantic universe and distinguish real purchase from notional recommendation; Tokyo R11, Kyoto R10/R12 demonstrate hit-but-loss/over-expansion. Analyze weighted day PFS **43.14%** rather than cherry-picking KYO R07.
5. **Ticket renderer:** prior KYO R07 status recorded `ModuleNotFoundError: jra_ticket_tree_renderer` at generation time, **but the file and tests exist on current main**; independently test runtime import/packaging before treating this as still-unfixed or creating duplicate code.

These are OWNER HANDOFF observations. The addendum does **not** assert the Common owners have implemented or promoted any change.

## 9. Learning and promotion declaration

- **KEEP:** Kyoto v1.0 course geometry, existing T1800/T1600/D1800 distance separation, inner/outer separation, Multi-World, UNKNOWN protection, temporal freeze, source-bound observation.
- **TEST_NEXT:** pre-cutoff A/B/C diagnostic arms and COMMON width/capital comparisons. Store positive, negative and no-bet cases; include Kyoto's 2026-10-11 R1–R12 execution coverage.
- **REPAIR_NOW (COMMON only, if still reproducible):** renderer import environment; no Venue code duplication.
- **DO_NOT_CHANGE:** Kyoto numeric coefficients, permanent course biases, automatic KRS W/P3 promotion, current Production Static/KRS physics/MEC-R3/AKI/Capital, historical Frozen FINAL.
- **PROMOTION:** **HOLD**. No same-day result can claim future calibration.
- **FINAL VERDICT:** `NO CANON CHANGE REQUIRED / REGRESSION APPENDED / VENUE MECHANISM SHADOW VALIDATION ONLY / COMMON-OWNER HANDOFF`.

## 10. Immutable source references

- [2026-10-05 Kyoto venue audit](../../runtime/venue_audits/KM-JRA-KYO-20261005-REV9-CANON-AUDIT.json)
- [2026-10-11 JRA race-day status](../../runtime/jra_race_day_status/2026-10-11.json)
- [2026-10-11 Kyoto R07 Production result](../../runtime/results/KM-JRA-KYO-20261011-R07.json)
- [2026-10-11 Kyoto R08 Candidate frozen settlement](../../runtime/source_candidate_oos/KM-JRA-KYO-20261011-R08/settlement.json)
- [2026-10-11 Kyoto R08 Candidate learning](../../runtime/source_candidate_oos/KM-JRA-KYO-20261011-R08/learning.json)
- [2026-10-11 Kyoto R08 PAPER preview](../../runtime/source_candidate_oos/KM-JRA-KYO-20261011-R08/candidate_forecast_brief.json)
- [2026-10-11 Kyoto R09/R10/R11 Production results](../../runtime/results/)
- [2026-10-11 Kyoto R12 Production result](../../runtime/results/KM-JRA-KYO-20261011-R12.json)
- [2026-10-11 Tokyo R11/R12 COMMON controls](../../runtime/results/)
- [R50 authority snapshot](../../profiles/KM_FAMILY_CURRENT_AUTHORITY_20261011_R50.json)

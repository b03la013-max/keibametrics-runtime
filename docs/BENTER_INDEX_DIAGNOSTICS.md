# Benter Phase 0.6: corrected offline diagnostics

This is research CODE/CI only. #362 and #363 remain Draft/unmerged.
There is no Production policy, index weight, AKI, MEC, Capital, ticket or
autopilot/delivery/postresult/source execution change. No external odds fetch,
deploy, signing, OAuth, Gmail or purchase is performed.

## Correction of the Phase0.5 design

The old all-14-coefficient L2 penalized market beta. Its beta0.374986,
holdout increment -0.0889239663 and WF increment -0.0534915444 were values from
a defective design and must NOT be interpreted as the indices' effects.
The old asof and signed/Frozen inputs remain unchanged.

The corrected objective is mean race negative log likelihood plus
lambda/2 times the sum of squared INDEX coefficients only. Beta has no L2
penalty. A separate offset version fixes beta to the M estimate of the
current training sample. For nested validation, estimate that offset again
on each INNER training fold, not on all outer training dates.

Lambda grid is .0001, .001, .01, .1, 1, 10, 100, 1000. Inner expanding-date
validation selects lambda without outer holdout/future dates. The holdout
lambda curve is descriptive and never used for tuning. As lambda tends to
infinity, both free-beta and offset models approach M. Tests compare the
whole probability vectors, not just a rounded delta.

F-joint uses only 13 standardized indices (beta fixed0), with the same
historical lambda selection and L2. It contains market-derived VMI, so its
standalone rho2 is not evidence of market independence. An auxiliary
12-index F-joint excluding VMI is also reported. Compare holdout standalone
rho2 of ZAI_WIN, JTI, KGI and both F-joints without copying fitted weights to
Production. Sign stability uses1000 race-bootstrap refits conditional on the
historically selected lambda; the selection uncertainty is not fully covered.

## Tests and quality axes

Keep200 within-race shuffle runs as descriptive controls. This revision
chooses the permitted **resolution-limit labeling** route, not a new
bootstrap p-value method. The plus-one minimum p1/201 exceeds .05/13.
Holm's decision is RESOLUTION_INSUFFICIENT, not a definitive negative finding.

Delete the point-estimate priority ordering. Use a canonical-order table of
default/exact50/fallback/DCR/UNVALIDATED rates versus standalone rho2 instead.
Standalone means no explicit ln(m) covariate; it does not prove independence
from the market. The numeric-cell denominator is2349 x13, separate from
Required Component evidence denominators.

VMI is treated as MARKET_REPHRASING_CONTROL. Record observed component
features from each frozen VMI trace; compare them with the registered
manifest. The manifest may also name expert_support/external_index_support.
Do not silently equate those potential components with data actually consumed.
A value exactly50 alone is not proof of imputation; preserve lawful DCR.

## Current read-only recomputation

The existing178-race single-index M/F/C and resampling outputs may be reused
only with matching from/to/asof, seeds, repetitions, exact race membership and
verified SHA for every original input. Missing or changed inputs fail closed.
This does not reuse the defective joint model: free-beta, offset and F-joint
models are recalculated. The historical defective value is preserved and
explicitly annotated. New outputs use a new asof directory only.

Hosted PR CI may run this recomputation against stored repository inputs,
with socket connections disabled during analysis. It is not an external
data acquisition or a Production execution. SHA read-back and byte
determinism checks protect original data.

## Future manual update example — DO NOT EXECUTE NOW

For11/7-11/8 results, after the required stored inputs exist, from this branch:

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 runtime/analysis/benter_index_diagnostics.py --from 2026-10-11 --to 2026-11-08 --asof 2026-11-09 --out runtime/reports/benter_second_stage/2026-11-09-phase06

This single command runs corrected Phase0+0.5 together. Do not overwrite a past
asof directory. Do not supply a historical reuse cache for a different period.

After the cumulative cohort exceeds200 races, examine the lower bound of the
out-of-sample delta-rho2 interval, the expanding-date WF cumulative increment,
and beta's stability across train dates/bootstrap samples. Inspect free-beta
and offset results together, separate VMI from nonmarket controls, and retain
the500-race reassessment requirement. Do not tune weights or infer EV from
these preliminary measurements. Automatic scheduling remains a proposal only.

## Closing odds and backfill

Closing-odds acquisition is separate work: pure parser/format tests and a
manual-only, approval-gated workflow. It is not invoked by this CLI or CI.
Current0 closing-odds races must not be filled using the winner's payout or
a pre-race snapshot relabeled as final.

Original Phase0 calculator/output compatibility is verified by tests.
Generation time remains separate. Keep original SOURCE/FINAL/RESULT and past
asof files unchanged. Backfill is conditionally feasible only as a separate
replay cohort with provable historical raw bytes, versions, identities and
prices. It is not authentic pre-race freeze or Forward OOS.

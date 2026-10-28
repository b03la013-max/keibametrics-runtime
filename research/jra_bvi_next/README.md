# BVI next research: incremental hypothesis rejected

This is a separate, unpromoted statistical Candidate. The published incumbent
D (`5e7f3b31…`) and all five code files in its publication remain byte-identical.
No Production numerical formula, AKI, KRS, MEC, Capital, historical request or
signed artifact is changed. All evaluation is **post-capture research**, with
**zero Forward OOS** and no purchase authority.

## Measured conclusion

The current admitted-corpus projection has 38,290 deduplicated runs. Its old
surface-only eligibility gate admits 36,082 runs / 3,443 composite horses.
Explicit obstacle-name/surface classification removes 489 runs / 126 horses,
leaving 35,593 **research flat proxies**, not officially qualified training
labels. Permanent horse IDs and independently race-bound labels consumed by
this model are still unresolved.

On the fixed chronological partitions (train before 2026-08-01, validation
before 2026-09-01, test before 2026-10-24), training has 31,276 runs. Test has
2,771 runs / 2,252 composite horses:

| Arm | Test MSE | Test MAE |
| --- | ---: | ---: |
| Control only | 0.090924314 | 0.253946713 |
| General pedigree | 0.090216978 | 0.252143932 |
| Hierarchical residual ENV | 0.090452100 | 0.251311324 |
| ENV + calendar quarter | 0.090703281 | 0.251742946 |
| Permuted pedigree negative control | 0.091426183 | 0.252847317 |

ENV worsens MSE versus general pedigree, although MAE decreases slightly.
Calendar-quarter addition further worsens test MSE. The incremental hypothesis
is **REJECT_HISTORICAL_INCREMENT**, not promoted, retuned or advertised as
future improvement. The single permutation is a deterministic negative control,
not a significance test or p-value.

The same predefined settings on the older 37,445-run corpus also worsen test
MSE: general 0.090600883 -> ENV 0.090941934. The original historical model
`7dbed8a0…` (a different model from future incumbent D) reproduces every stored
Validation/Test MSE and MAE within 1e-12 by read-only replay.

## 2026-10-28 historical partition consistency audit (no refit)

The read-only `partition_integrity.py` cross-checks every stored arm's MSE/MAE
against the sample-weighted reported train-seen/train-unseen and venue/surface
partitions. It rejects forged aggregates, inconsistent sample sizes, claim
changes or an altered protocol SHA. The source report's raw SHA is carried into
an Actions artifact. This **reconciles stored aggregate arithmetic only**; it
cannot reverify independent horse IDs, underlying race labels or OIDC provenance.

The reported composite-horse train-disjoint subset has a different direction
from the overall test cohort. Exact historical comparisons are:

| Partition | Cohort | Runs | General MSE | ENV MSE | ENV−General MSE |
| --- | --- | ---: | ---: | ---: | ---: |
| Validation | All | 1,546 | 0.084643879 | 0.085200597 | +0.000556718 |
| Validation | Train-unseen composite horses | 254 | 0.105844896 | 0.106308435 | +0.000463539 |
| Test | All | 2,771 | 0.090216978 | 0.090452100 | +0.000235122 |
| Test | Train-unseen composite horses | 790 | 0.106238393 | 0.105878681 | −0.000359713 |
| Test | Train-seen composite horses | 1,981 | 0.083827822 | 0.084300157 | +0.000472335 |

The apparent test-subset benefit reverses on validation and is **not** a
prospectively pre-registered, independent-horse-ID or independent-race-label
result. Validation/test horse-set disjointness has not been established.
Training remains timestamp-split, not officially qualified; cross-race
opponent ability and calibrated cluster inference remain unavailable. Neither
subgroup selection nor MAE changes justify overturning the full-test
`REJECT_HISTORICAL_INCREMENT`. The existing control-only arm is an ablation;
the parent-permutation arm is one fixed-seed placebo, **not** two independent
randomized negative controls. Further negative controls are unexecuted.
Brier/logloss are intentionally NULL because this is a continuous rank target,
not verified binary calibrated probability forecasting. Prediction, KRS, ticket
and PFS increments remain unmeasured by this aggregate audit.

Reproduce without collecting or mutating SOURCE:

```bash
python -m pytest -q research/jra_bvi_next/test_partition_integrity.py
python research/jra_bvi_next/partition_integrity.py \
  --input research/jra_bvi_next/evidence/current_corpus_evaluation.json \
  --output /tmp/bvi_historical_partition_integrity.json
```

## Statistical structure and limits

The existing fixed CONTROL weighted-ridge implementation is reused read-only.
Individual prior form is recomputed **after** obstacle exclusion, using only
strictly earlier label dates. Parent general residual effects, sire×damsire,
then parent×surface/venue/distance/going residual effects receive fixed
normal-normal zero-residual shrinkage. This is ordered conditional partial
pooling, not a jointly fitted Bayesian multilevel posterior. Penalties are
predefined; no validation/test optimization is performed.

Every horse's total training weight is one; repeated runs do not increase
independent offspring count. General and environment coefficients, observed
support, effective horse weight, shrinkage and horse-cluster residual SE proxies
are stored independently in the compressed model artifact. None of these
composite counts is a permanent official offspring count. Unknown SE remains
unknown and cannot cause a role rescue. Bootstrap ranges in the evaluation JSON
are **dependency sensitivity ranges, not calibrated population confidence
intervals**. Shared race dependence remains unresolved without independent
race-bound labels. Class/field/prior individual form are controlled; opponent
strength is unavailable. Weather and meeting progression are not adopted.

The old 467-run/126-horse domain observation is retained. A compatible minimum
predicate reproduces that set; adding explicitly named jump stakes gives 487
runs on the old corpus. The 20 extra runs are Tokyo High Jump 10, Kyoto High
Jump 4, Pegasus JS 4 and Ushiwakamaru JS 2. They are separate definitions, not
a rewrite of the old observation. Source hashes and rows appear in the domain
audit. All 126 horses have flat histories too; their obstacle weight is not
126 independent horse equivalents.

## Connection audit

`connection_audit.py` reads the existing 30 formal 2026-10-25 requests / 400
runners and checks their archived SOURCE hashes. A pure +1 BVI scalar
counterfactual changes BVI/TPI/SRI/F3S/T3I for all 400 runners and changes
**zero ZAI_WIN/ZAI_PLACE cells**. It does not recompile a backdated FINAL or
claim all possible AKI/role effects are absent.

This scalar result does not mean all bloodline evidence has no effect on
Prediction. Existing shared pedigree features also feed GCI/KGI for established
horses, and HPI/CFI/GCI/KGI for low-career/newcomer profiles, which can feed ZAI.
The exact profile/feature weights are recorded in `shared_pedigree_paths.json`.
Those paths are structural evidence only; their incremental value effects are
not measured by the +1 scalar assay.

A separate, outcome-free P3 audit proposal requires at least four composite
offspring for general and environment effects, a finite positive conservative
environment lower proxy, and permits at most one additional P3 candidate.
It never removes a horse or promotes W/P2. In this known-day diagnostic it
produces **zero rescue proposals**. Archive result evaluation is qualified only
for 28 races; NGT11/NGT12 results are missing. Unknown outcomes are null and
are not counted as zero success/failure. PFS, actual ticket cost and KRS
unique rescue/harm remain null because no KRS/MEC/Capital/ticket execution is
performed. Any displayed 100-yen orientation bound is hypothetical, not a
recommendation or Capital result.

## Reproduction

The primary repository is a read-only data root. The two prior real CI
`environment_coverage.json` files identify the exact immutable source files.
`candidate.py --coverage` verifies their byte/content hashes and constructs a
compact forensic projection; it does **not** inject a substitute verifier into
Production or claim fresh OIDC. Compact datasets omit full provenance fields,
so their hash is not the incumbent's full `training_rows_sha256`.

```bash
python research/jra_bvi_next/candidate.py --repository /path/to/runtime-repo \
  --coverage /path/to/old/environment_coverage.json \
  --coverage /path/to/current/environment_coverage.json --output /scratch/data
python research/jra_bvi_next/candidate.py --repository /path/to/runtime-repo \
  --dataset /scratch/data/dataset_1.json --output /scratch/evaluation
python research/jra_bvi_next/connection_audit.py --repository /path/to/runtime-repo \
  --models /scratch/evaluation/candidate_models.json --output /scratch/new-connection
python -m pytest -q tests/test_jra_bvi_next_candidate.py
```

Large datasets, all coefficients and runner-level proposals stay in a separate
research artifact. This directory contains only code, tests, lightweight group
metrics, parameter/file hashes and read-only audits. No new collection, external
KRS, Dispatch, paid API, Merge or Deploy is part of this work.


## 2026-10-29 registered AKI role/Pair/Third scalar boundary (post-capture)

The offline-only \`role_chain_sensitivity.py\` reruns the unmodified R51
registered AKI decision logic on two in-memory copies of each of the 30
archived 2026-10-25 formal requests (400 runners). It verifies archived
SOURCE hashes, checks fixed-D raw SHA, and separately compares the saved
decision to the original replay. Its intervention is exactly +1 BVI scalar
capped at 100, **not** a simulated change to real pedigree features.

The first CI acceptance of this tool reproduced all 30 archived AKI role
decisions. The +1 intervention changed BVI/TPI/SRI/F3S/T3I in 400 runners,
ZAI_WIN/ZAI_PLACE in zero, and registered W/P2/P3 role memberships, Pair
decisions, Third decisions and ranking in **zero**. This is a measured
historical boundary outcome, not a universal proof that bloodline data
cannot change role selection. Registered policy may react at another
magnitude or at a different evidence gate.

The KRS-input extension measures the existing pure input bridge with the
same authorized in-memory role output. It **does not execute KRS** and must
never infer simulated W/P2/P3, MEC, ticket counts, same-budget Capital,
purchase cost, or PFS. All such outputs remain NULL. No result label is
consulted, no prospective Freeze or OOS credit is minted, and no input
request, formal FINAL, or Production formula is changed.

The research CI saves an explicit per-race and aggregate role-chain JSON
artifact. An incomplete archived re-evaluation or mismatched original
registered AKI replay now fails the research check instead of converting
a partial replay into success.

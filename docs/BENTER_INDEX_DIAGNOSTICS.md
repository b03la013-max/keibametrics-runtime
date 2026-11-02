# Benter Phase 0 / 0.5 offline measurement

This research CLI reads existing JRA FINAL, SOURCE, RESULT and Status artifacts.
It never imports into or invokes Production prediction, delivery or postresult.
There is no schedule, provider fetch, signing, authentication or purchase code.
The implementation is stacked on Draft PR #362. Both PRs remain unmerged.

## One manual command after each raceday

With Python 3.12, numpy 2.3.5 and scipy 1.17.0 installed, run from this branch:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 runtime/analysis/benter_index_diagnostics.py --from 2026-10-11 --to 2026-11-07 --asof 2026-11-08 --out runtime/reports/benter_second_stage/2026-11-08
```

Replace `--to`, `--asof` and the output directory on each update. The output
directory must not already exist, even if empty. The CLI runs Phase 0 and 0.5
together. It publishes a completed directory by rename after all calculations
and input SHA read-back checks. It produces:

- `summary.json`, `summary.md`, `ledger.csv`, `generation.json` from Phase 0;
- `index_diagnostics.json`, `index_diagnostics.md`, `index_ledger.csv` from 0.5;
- `ledger_final_odds.csv` only if explicitly final odds are already stored.

For the existing 2026-11-03 asof, preserve the original directory and use a new
qualified directory such as `2026-11-03-phase05`. No past asof is overwritten.
Runtime-dependent generation time lives only in `generation.json`. Pin input
SHA, code SHA, software versions, seeds and thread counts when reproducing bytes.

An automatic schedule is a proposal only and needs separate adoption. Do not
add this module to race-day autopilot, delivery or postresult.

## Frozen Phase 0 and the resolved Claude comparison

Owner clarified that Claude used a split at a raceday boundary and centered
ZAI without dividing by its within-race standard deviation. #362 uses the
specified post-time half split and within-race standardization. The difference
is therefore closed by the Owner's explanation; Claude's unpublished script
has not been independently executed here.

`benter_second_stage.py` and the old asof remain byte-identical. A new run's
`summary.json` is the unchanged Phase 0 result, including its historical
comparison annotation. The new `summary.md` replaces the obsolete unresolved
annotation, and `index_diagnostics.json.reference_resolution` is the explicit
correction record. A test compares its Phase 0 JSON with a standalone #362 run.

## Preregistered diagnostic choices

The audit denominator is runner x index cells (2349 x 13 in this cohort),
not the Required Component denominators of prior Base13 evidence audits.
Zero numeric cell omissions does not establish 100% observed evidence.

- Cohort: the same Phase 0-eligible races and active runners. No new missing
  value imputation. A genuinely missing Base13 value excludes its whole race
  from that index; the joint model requires all 13. Counts are explicit.
- Standardization: population SD within each race after non-starter removal;
  constant columns become zero. A value of exactly 50 is a diagnostic flag,
  not sufficient evidence of imputation. Explicit fallback/DCR and
  `UNVALIDATED` are counted separately. Their counts overlap, so they are not
  added. The displayed default rate is the union of exact-50 and fallback/DCR.
- A default-rate annotation of at least 25% means "reference" for this report;
  this is not a change to any Production threshold or missing-data rule.
- Per-index: same M/F/C fit, strict temporal half split, paired holdout race
  bootstrap 1000 plus train/holdout refit sensitivity, within-race shuffle200
  and expanding-date walk-forward as #362. Seeds remain 20261103.
- Holm: one-sided Monte Carlo p=(1+count(null >= observed))/(B+1), applied to
  all 13 hypotheses. With B=200 the minimum p is 1/201, greater than .05/13.
  Thus the requested run cannot resolve a Holm rejection, even for a very
  strong effect. Report that limitation, not "no information proven".
  Increasing the control to e.g. 1999 at the 500-race reassessment is a design
  proposal only; this run keeps the requested 200.
- Joint model: 13 standardized indices plus log market probability, L2 on
  **all 14 coefficients**, objective mean race NLL + lambda/2 * ||theta||².
  Candidate lambdas are .0001, .001, .01, .1, 1, 10, fixed before measurement.
  Select by summed validation log loss over inner expanding-date folds of
  outer training only. No future validation day or outer holdout is used.
  With no inner history, use the fixed default lambda=1. Date-WF selects
  again using only dates strictly before the target date. Grid ties prefer
  stronger regularization. No post-result tuning of the grid.
- Coefficient sign stability: 1000 race-bootstrap refits of the chronological
  training sample, holding its training-selected lambda fixed. Sign changes
  are relative to the original training coefficient. This is conditional on
  model selection and is not an adoption or causal confidence interval.
- Current weights: read the stored formula source as an AST, never import it.
  The supplied 11 weights sum to 1. BVI and VMI have direct weight0 in that
  `ZAI_WIN` expression. They may affect other Derived indices. Compare raw
  score weights and standardized diagnostic coefficients with their different
  units explicit; never copy the fitted coefficients to Production.
- Rank indices by held-out increment, show WF evidence/default rates beside
  them, and treat every ranking as exploratory until the fixed test is rerun
  after 500 eligible races. No new weight is implemented.

For the current 178-race measurement, BWI, JTI and CFI have the three highest
held-out point increments, but every one of their confidence intervals crosses
zero and every per-index expanding-date cumulative increment is negative.
Therefore the table is a diagnostic ranking, not a proven repair priority or
an adoption list. JTI's sample/evaluator binding, BWI's timestamp/range binding
and CFI/GCI's course/going evidence are reasonable correctness inspection
targets. Full-runner workout evidence for TRI/newcomer RFI remains a separate
evidence-quality task; a nonmissing index number does not establish that feed.

The joint model selected lambda1 from its inner historical folds and produced
a held-out increment of -0.088924. Its market coefficient was shrunk to0.375
because this preregistered L2 penalizes all14 coefficients. Stable signs alone
do not demonstrate market increment. An unpenalized-market nuisance coefficient
would be a different design, to consider separately at the 500-race review;
this run is not adjusted after observing the result.

## Odds timing and provider research (SPEC only)

The main snapshot, signing timestamp and frozen scheduled post remain those
of #362. Report race-level min/median/max minutes to post. Bands are <=10,
10< t <=30, 30< t <=60 and >60. The band-refitted M is an in-sample diagnostic;
also show each band's held-out M and ZAI increment under the same globally
trained Phase 0 coefficients. Do not interpret band differences as a causal
timing effect: race composition differs across bands.

Explicit final odds, when present, are a secondary cohort. Compare pre-sign
and final prices on paired races and the same original train/test membership.
Post-time observations alone are not proof that prices are final.

JRA says its odds/results pages expose final odds for completed races:
https://www.jra.go.jp/faq/pop02/1_1.html

The existing `jra_market_observation.py` reads race-card detail prices and has
no explicit final-price classification. Stored `official_result` inputs do
not supply a final-price series for the current cohort. The same JRA provider
can in principle supply the data, but capturing/classifying it and binding
Race ID, active universe, observation time and SHA needs a separate reader
change. No new provider or fetch is implemented in Phase0.5.

JRA-VAN DataLab documents realtime and 5-10 minute odds histories:
https://jra-van.jp/dlb/ddata.html

It is an alternative with separate licensing/environment/retention review,
not an adopted source. The availability of historical pre-sign snapshots for
each particular race must be proven, not inferred from current final odds.

## Arrival forecasts and backfill (SPEC only)

Count one raceday per calendar date across venues. The eight-day empirical
pace is a conditional extrapolation; venue mix, weather, legitimate NO-BET,
scope and runtime reliability can change it. Status enums are copied without
reclassification. Technical recovery is an upper-bound *future* scenario;
it never recreates an absent pre-race FINAL after the deadline.

Forecast calendar dates were checked visually against the official PDFs:

- https://www.jra.go.jp/keiba/program/2026/pdf/nittei.pdf
- https://www.jra.go.jp/keiba/program/2027/pdf/nittei.pdf
- https://www.jra.go.jp/news/202609/092805.html

The 2027 published calendar is subject to official approval and future
changes. The hardcoded offline calendar extends through March2027 and is not
a Discovery feed. Beyond that horizon, emit no invented arrival date.

Backfill is conditionally feasible as **a separate replay cohort** only when
pre-post raw bytes, versions, identities, cancellations, timestamps, evidence
corpus and odds were archived. Run outcome-blind feature replay with the
original rules/code. Later person stats, updated corpus or a current result
page cannot establish a past feature snapshot. Absent authentic pre-race
signature/freeze cannot be supplied retrospectively. Never add replay to the
178 original observations or genuine Forward OOS.

Engineering estimate if inputs are complete: 1-2 person-days for inventory
and temporal proof, 2-4 for offline replay adapter, 1-2 for independent review
and regression, total4-8. This is a planning estimate, not implementation or
a delivery commitment.

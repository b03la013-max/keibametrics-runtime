# JRA 2026-10-24 saved SOURCE / BVI / OOS audit

Baseline: `1e72d0d01bc41918fa5f460d49c85235f87a486b`. This is a retrospective correctness audit and an inspection of original provider archives. No historical SOURCE, FINAL, Freeze, model, numerical Policy or Production request was replaced. No Merge, Deploy, dispatch or external notification was performed.

## Correctness results

| Venue | Races | Runners / index cells | Printed frames recovered | Historical grade labels recovered | Existing class feature newly available | Incorrect workout gait repaired |
|---|---:|---:|---:|---:|---:|---:|
| Tokyo | 12 | 159 / 3,180 | 159 | 7 | 1 | 50 |
| Kyoto | 12 | 143 / 2,860 | 143 | 99 | 11 | 29 |
| Niigata | 12 | 165 / 3,300 | 165 | 12 | 1 | 14 |
| Total | 36 | 467 / 9,340 | 467 | 118 | 13 | 93 |

The frame/rider/detail-PDF implementation is reused from PR #330 HEAD `9347ad99a5cfbfff928b351b0304e6497a1dad59`, excluding its old Delivery/workflow stack. There were zero observed rider-label differences in this day's saved inputs. PDF supplements only fill missing frame/weight after exact horse-number/name matching; conflicts remain diagnostics.

Official historical race grades were present in image `alt` values and were discarded by plain text extraction. A parser used only by detailed cards and horse history now retains exact official grade/Listed labels. The general table parser and current race-context parser retain their prior behavior, so receipt-bound old context remains readable. Kyoto 11R horse 1 recovers 七夕賞 GⅢ / 都大路S Listed / 白富士S Listed / エリザベス杯 GⅠ; the existing registered class evaluator then has four observations without changing its weights.

All 33 saved formal KRS inputs had official SOURCE weather/going/class omitted by the sparse request race dictionary. The bridge now fills only missing metadata from the same hash-bound, timezone-aware pre-cutoff SOURCE. Explicit inputs take precedence. Absent/unverifiable context preserves the prior fallback. All 33 horse HSV arrays and seed/run-count dictionaries are unchanged in the diagnostic replay; KRS Physics was not run or changed.

The workout parser calculated the printed 脚色 column index but read `row[-3]`. Compact assessment tables have no 脚色 column, so this placed the horse name in gait for 93 horses. The existing column index is now used only when present. Assessment/rating and their numerical feature categories are unchanged. Tokyo 4R retains all 16 assessment observations while its course/lap-time inputs remain missing; no clock or workload is invented.

## Requested fixture diagnoses

| Fixture | Saved lineage finding | Classification |
|---|---|---|
| TKY 7R #5 | One exact-distance prior run; `same_distance_fit` requires at least two. The separate within-200m `distance_fit` has 11 observations but no Production index mapping. BVI 73, measured. | Existing rule / unused candidate feature; no automatic alias promotion |
| TKY 10R #7 | Four exact-distance runs reach CFI; eight surface observations reach CFI/GCI; two same-going observations are used. BVI 77.571429, measured. | Source and registered feature connection present |
| TKY 11R #13 | One prior run, one exact-distance/surface observation, zero same-going observations; registered observed-only minimums prevent class/distance/surface substitution. BVI 76.238095 is measured pedigree evidence. | Small sample / genuine condition-specific missingness |
| TKY 12R #8 | BVI 50 with no measured components, six unpublished pedigree features, DCR 0. Five exact-distance and two same-going observations are used elsewhere. | DCR-only BVI; no fabricated pedigree input |
| KYO 11R | Official image grades exist in the original raw bytes; 11 horses gain the existing class feature after parser-only correction. | Proven parser omission |
| NGT all 12R | All 165 runners / 3,300 stored index cells audited; runner universe unchanged. | Full saved-input coverage; Role/ticket failure matrix is the separate prediction audit |

## BVI and corpus

| Venue | MEASURED | MEASURED_PLUS_DCR | DCR_ONLY |
|---|---:|---:|---:|
| Tokyo | 144 | 8 | 7 |
| Kyoto | 128 | 6 | 9 |
| Niigata | 157 | 4 | 4 |
| Total | 429 | 18 | 20 |

These labels describe the existing index components, not independently validated pedigree-model utility. Per-runner source facts, component weights, reported offspring/run denominators and registered rule authority are retained in `lineage_audit.json`. The reported offspring count uses the existing name/sire/dam composite, so permanent-ID independence is unproven. B's separately identified BVI=50 sensitivity keeps DCR and provides the Role/ticket ablation; this audit does not claim a new model fit.

The current saved corpus has 66 hash-valid official-declared files, 2,717 horse observations, 26,498 run observations and 26,138 valid finish-label observations. All 2,717 lack accepted horse/sire/damsire permanent IDs; all 26,498 lack official race IDs. Surrogate grouping gives 23,743 horse-run groups and 2,395 repeated observations, with no contradictory labels/going in those groups. This grouping is diagnostic and is not certified independence. File hashes and official flags are not fresh OIDC attestation. Accepted permanent IDs recovered: 0; new corpus admissions by this work: 0; unaccepted 408 runs imported: false. Hierarchical Bayesian fitting remains blocked by identity/independent-label lineage.

Reusing the existing exact-token/original-raw identity-recovery implementation now resolves 705/2,717 official profile navigation observations and 5,508/26,498 official result navigation observations. The prior saved snapshot was 638/2,670 and 5,281/26,365; the denominators differ. Source envelope signatures and every referenced raw/corpus binding were reverified offline (205/207 envelopes verified; two held, nine raw chronology holds). Permanent horse/parent IDs remain zero; no name-only join, navigation-token equivalence class, new Corpus admission or model training was introduced. The full deterministic lookup is `navigation_recovery.json.gz`; its byte hashes, qualification limits and current/prior counts are in `navigation_recovery_summary.json`. Fresh OIDC qualification was not claimed.

## Independent archive and Learning evidence

Fresh authenticated GitHub reads retrieved metadata and exact ZIP bytes for all 33 original utility archives, plus the sidecar/rank code and model bytes at each original run HEAD. The existing `verify_actions_artifact` verifies the workflow, provider server receipt time, archive SHA and exact saved Shadow. All 33 pass. SOURCE, runner universe, cutoff, original FINAL, checkpoint, request, model and policy bindings are checked separately.

Strict preregistered Conditional Rank acceptance remains **0**: all 33 actual sidecar code SHAs differ from the day-plan's registered sidecar SHA. Rank code, model, model Policy and portfolio Policy pins match. The old runtime tracker claimed 13 eligible races; that recorded value is preserved separately. The plan was not rewritten to match later code. Minimum 60 distinct races / 3 days / 2 venues remains unchanged; no automatic promotion.

R51's SOURCE_CANDIDATE cohort requires a Signed Candidate FINAL. The separately registered ROLE/CONDITIONAL_RANK sidecar explicitly inherits verified Production SOURCE/KRS/FINAL and requires exact independent provider archive content; it does not claim a standalone Shadow signature. No unsigned object is relabeled a Signed Candidate FINAL, and these cohorts are not pooled.

Actual saved **Shadow** inputs contain accepted bindings for 24 targets, 139 binding occurrences and 10 distinct same-day source states. The utility archives alone prove existence before a target's SOURCE Freeze for 23 targets / 130 occurrences / all 10 source states. Nine first-use occurrences lack this earlier independent existence proof and remain separately identified. The original state bodies, SHA, effective time, source race, source-freeze boundary and composite prediction-input SHA are preserved. There is no backdated reconstruction.

The follow-up `learning_state_time_commitments.json` verifies the 13 original successful RESULT provider archives. Each saved `result_summary.json` commits to the unchanged State's canonical SHA, which includes its effective time, and to its source review SHA. The matching State/review bodies, original signed RESULT payload and Ed25519 receipt were verified offline with the previously recorded public key. The provider archive's SHA and server creation time commit these exact State contents before each target's SOURCE Freeze for **all 24 targets / 139 occurrences / 10 consumed states**. This adds the nine first-use proofs. The RESULT archive contains the State SHA commitment rather than the State body; the later saved target input contains the matching body. This indirect content commitment and the 130 earlier direct body-archive proofs remain separate columns. No failed-state body was recovered, no time field was rewritten and no deployment/process signer verification is inferred from the offline signature check.

Retrospective ON/OFF replay reproduces the original Shadow arms. LEARNING_ON changes tickets for 23 targets, adding 522 tickets / 52,200 virtual yen; this is an added-exposure diagnostic, not a matched-budget performance comparison. Production tickets change in 0 targets. The fixed rank model reads only Full20 and fixed coefficients: Learning changes no numerical rank input, score or order. Production numerical Learning consumption is 0. Fresh recovery-state live consumption is 0. The replay itself contributes 0 Forward OOS races.

Exclusions are kept distinct: 2,574 effective-time-unverified occurrences, 165 hash mismatches, 165 other-family occurrences and 1 effective time after the existing SOURCE boundary. They are not retroactively qualified. Original failed-run state bodies newly recovered from these 33 archives: 0; the ten present same-day bodies match already saved states.

## Validation and reproduction

`50 passed, 463 subtests passed` across the eight suites recorded in `regression.xml`. Sparse-checkout fixture references were local only; no request symlink, removed request, temporary file or original data mutation belongs to this change. All 33 saved FINAL file SHAs remained identical throughout the complete saved-input audit.

```sh
KM_LINEAGE_DATA_ROOT=/path/to/immutable/data PYTHONDONTWRITEBYTECODE=1 python -m pytest -q tests/test_jra_source_grade_context_retention.py tests/test_jra_source_observed_fact_retention.py tests/test_jra_horse_history.py tests/test_jra_production_fullnumerical_to_krs.py tests/test_jra_production_krs_contract.py tests/test_jra_observed_context.py tests/test_jra_official_fact_evaluator_production.py tests/test_jra_source_to_evidence_features.py
python scripts/jra_20261024_lineage_audit.py --data-root /path/to/immutable/data --output /tmp/lineage_audit.json
python scripts/jra_20261024_lineage_audit.py --data-root /path/to/immutable/data --provider-metadata evidence/jra_20261024_lineage/provider_metadata.json --provider-code /tmp/provider-run-code-cache.json --archive-root /tmp/exact-provider-zips --output /tmp/provider_archive_content.json
```

Provider metadata contains the original artifact IDs and run URLs. The provider-code cache is obtained with authenticated read-only GitHub contents reads at each recorded immutable HEAD. ZIP files are downloaded using the existing GitHub artifact endpoint and their provider digest, never from a newly generated replay. Owner approval and required integration checks remain necessary before applying the future parser/KRS fix to Production.

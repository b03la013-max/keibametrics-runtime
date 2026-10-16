# JRA BVI Phase 3: actual recovery, admission boundary, future measurement

Baseline main `877819fab8167fe38b42cee82634f9ddd698326c`, Current Authority R51.
The latest main and 25 open PRs were reviewed; Phase2's existing runtime fixes are
retained. No numerical, Static, KRS, AKI, MEC, Capital, Venue or promotion policy changes.

## Actual data recovered

Four sequential public official archive captures completed, respecting the observed
robots policy and existing collector at 1.2-second request spacing. No authenticated
subscriber collector was started. Actual selected race dates/conditions:

| Date | Venue | Condition | Profiles | History rows |
|---|---|---|---:|---:|
| 2022-05-01 | Tokyo | Dirt1600, 3yo maiden | 6 | 98 |
| 2023-05-07 | Kyoto | Dirt1800, 3yo maiden | 6 | 53 |
| 2024-09-08 | Chukyo | Turf3000, jump maiden | 6 | 203 |
| 2025-01-05 | Chukyo | Dirt1800, 3yo maiden | 6 | 73 |

Phase3 adds24 profile surrogates /427 history observations, without internal duplicates.
19 observations overlap the previously stored official corpus under the documented
horse-parent/date/venue/surface/distance/race-name surrogate;408 are absent from both
that corpus and Phase2 samples. This is a diagnostic dedup key, not an official ID.
Phase2+3 samples grow9/149 to33/576 profiles/history rows. Complete result races
recovered:0. These are sampled horse histories, never427 full races or full five-year coverage.
New run years:2019:5,2020:28,2021:32,2022:99,2023:104,2024:64,2025:70,2026:25.
The2022–2025 subset adds337 observations. Father/mother/damsire names exist24/24;
independent official IDs and publication timestamps remain unresolved.

History includes67 jump-named rows, some LOCAL runs, and2 unknown venue/surface rows.
Turf display does not establish flat-race eligibility. Keep these outside Production
until the existing discipline, identity, source admission and point-in-time rules apply.
Repeated starts are separate observations, not independent offspring. Source hashes,
actual2026 capture times, sire/damsire independent-sample counts and coverage dimensions
are in `data_recovery.json` and immutable research captures. Normalized class, race
number and national completeness are not inferred from race names.

The private checkpoint was rechecked. All16812 pending observed result links are
unique; year counts2021:754,2022:3456,2023:3456,2024:3456,2025:3468,2026:2222.
The2022–25 raw pages were never collected before the original worker stopped, rather
than lost after parsing/persistence. Provider data stays528 races/7059 rows. The
provider-to-official ID crosswalk is unresolved, so no pending links are falsely closed.
No private raw rows, member links or provider IDs are published here.

## Formal admission is still blocked

New captures remain under `research/`, outside the admitted corpus. Official origin,
hashes and `official:true` do not replace the original approved workflow's OIDC.
The existing verified-backfill workflow can reacquire bounded three-race windows,
attest its exact output and pass the unchanged admission gate. This environment has
no exposed manual workflow_dispatch method, local gh executable or local GitHub
token. No alternative signer, trigger, paid service or authority change was created.
The four exact existing date/start inputs are saved in `source_admission_blocker.json`.
An authorized run would reacquire its own output, not retroactively attest these bytes.
New formally admitted / consumed Production rows are therefore0. No historical
prediction is allowed to use these later-observed2026 captures as pre-race evidence.

## Real use and downstream sensitivity

Unchanged BVI consumption was actually replayed over23 archived canonical inputs,
313 runners:277 measured,14 measured+DCR,22 DCR-only. Measured contribution is291/313
(92.97%), not a forecast of October18 coverage or a new signature attestation.
The prior independently verified actual acceptance artifact12066173529 was re-read:
2 races/27 runners, six5000-trial candidate KRS executions with per-arm Static,
input/output/receipt/MEC/Ticket/Capital hashes. This remains POSTCAPTURE, not Forward OOS.

20 BVI values changed, one ranking changed, no A/B roles, tickets or investment changed.
The registered scalar BVI TPI weight is0.05 and discrete role selection can preserve
roles despite a ranking change. Shared pedigree features also feed other base indices;
this is not an identified BVI-only causal effect. The new recovery's predictive effect
is pending admission, not established by the older replay.

Seven old-policy results were separately read and their original RESULT Ed25519
signatures reverified against the existing trust anchor. Virtual investment9400,
return360, PFS3.83%, drawdown9040; all arms share that capital outcome. This is neither
Phase3 improvement nor actual purchases. Original pre-cutoff Git witness was accepted
by the existing settlement lane, not independently re-witnessed in this audit.
No post-result equal-ticket subsets are invented.

## October18 and completion limits

The actual fixed cohort remains36 races across3 venues. Phase2 status accidentally
reported3 by counting venue groups; this evidence records the erratum without changing
historical signed artifacts or the correct execution plan. Future coverage remains null.
Current-policy eligible Forward OOS remains0/30; Winner/P2/P3/Exact, bloodline Rescue/Harm,
equal-budget/equal-ticket and Robust PFS improvements remain INCONCLUSIVE.

Existing noon October17 and hourly October18 monitoring are updated in place, preserving
schedules and prior activation boundaries. Production execution stays first; only actual
pre-cutoff canonical-matched A/B/C artifacts count. No FINAL means no invented Production A.
Existing result verification, separate policy cohorts, frozen equal-budget/equal-ticket
protocols and Learning operate after official results; no future settlement is fabricated.

Actual recovery/inventory and selected temporal/lineage regressions passed42 tests.
No runtime code repair was necessary in this phase. The new script only reproduces the
offline recovery inventory. Local passing tests do not establish new CI, OIDC admission,
all-race success, predictive improvement or promotion. PR/CI and immutable head references
are reported separately after publication.

## Publication verification

PR295 data head `dceb0a08823116ec3b4a93a976fa7245f6e71e14` preserves17 files;
all17 uploaded Git blob identities match local bytes. GitHub reports0 check runs
and0 workflow runs for that head because the changed paths do not trigger existing
CI. This is NOT_TRIGGERED, not CI PASS; the existing runtime code and its prior
passing main checks are unchanged. The PR is cleanly mergeable. Merge receipt is
reported externally after this evidence commit; no self-referential SHA is invented.

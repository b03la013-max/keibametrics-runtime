# 2026-10-24 frozen capital comparison

This is post-result research. It grants no purchase, dispatch, deployment,
Production policy, or promotion authority. Forward OOS credit is **zero**.

The original 36-race day consists of 27 FORMAL FINAL allocations, six Signed
FINALs with PAPER/zero allocation, and three AKI_NO_BET terminals. The Production
recommendation totals below contain only the 27 allocated frozen FINALs. Actual
purchases are unverified, so these are virtual recommendation settlements.

| Venue | Frozen allocated stake | Official return | Official refund correction | Effective stake | Recommendation PFS |
|---|---:|---:|---:|---:|---:|
| Tokyo | 15,500 | 9,020 | 0 | 15,500 | 58.1935% |
| Kyoto, original signed settlement | 15,300 | 11,060 | 0 | 15,300 | 72.2876% |
| Kyoto, separate corrected research | 15,300 | 11,060 | 1,200 | 14,100 | 78.4397% |
| Niigata | 12,200 | 0 | 0 | 12,200 | 0% |

The original overall ratio is 20,080 / 43,000 = 46.6977%. The independent official
refund correction gives 20,080 / 41,800 = 48.0383%, loss 21,720 yen. Original
Signed FINAL/RESULT files were not changed or re-signed. The KYO7 correction uses
the independently parsed evidence owned by the P0 result repair; it does not add
a refund to payout. PAPER MEC candidate tickets are recorded separately, including
NGT2's hypothetical return of 24,590 yen, and never enter these totals.

`coverage.json` lists all 36 races with status, frozen FINAL recommendation,
Production recommendation allocation, frozen MEC hypothetical cost, and actual
purchase status. It also maps the seven C-owned Venue items to evidence and
remaining conditions. `summary.json` contains aggregate and per-race diagnostics.
`replay.json.gz` retains every selected research portfolio and settlement.
`frozen_auxiliary_inputs.json` records 33 unchanged original sidecars with content
hashes and Source/Cutoff/Universe/FINAL binding checks. This later input audit is
not an independent pre-race Freeze or an OOS qualification.

Portfolio construction accepts no result or payout. It uses the frozen Source,
runner features, KRS summaries, Role dispositions, and frozen sidecar proposals.
The default allocator preserves original **gross stake**, total points, exact
bet-type point counts, and each bet type's stake multiset. The explicitly labelled
BET_TYPE_ROUND_ROBIN arm preserves gross stake and total points while changing
the bet-type mix. Official cancellation refunds can differ with selected tickets,
so equal gross stake does not imply equal effective stake. Native additive
KRS/LEARNING_ON and structural abstention controls are a separate unmatched
exposure series.

Kyoto 10's frozen 2→8→4 is PROTECT and missing from the frozen TRIFECTA. The
result-blind PROTECTION_FIRST rule retains it within the original budget and type
counts. Across the day this rule returns 83.6190% PFS; it is a new research rule,
designed after results, and receives no OOS credit. Kyoto 11's 800 yen is entirely
head 11; Kyoto 12's 300 yen is entirely head 1 / pair 1→6. These concentrations and
the foregone return of a separate research abstention rule are recorded.

Niigata 11's frozen actionable proposals rescue W5 and pair 5→10. The native
KRS_ACTIONABLE arm adds 1,000 yen, returns 4,760 yen, and has 900 yen of losing
added stakes; the native LEARNING_ON arm adds 2,500 yen with the same return and
2,400 yen of losing added stakes. Niigata 12's native actionable arm adds 5,900
yen with zero return. Rescue, correct-ticket addition, profitability, and extra
cost are therefore separate metrics. Actionable proposals are not purchase
authorization.

The best observed same-exposure PFS is not a promotion result: the frozen-KRS
Role ranking research arm returns 101.4692%, falling to 64.6012% after excluding
its largest return. Only one observed date and 27 allocated races exist here;
R30/R100 and the required 60-race / three-date / two-Venue future test remain
pending. Opening bankroll is unavailable, so capital turnover is UNKNOWN.

Validation: 18 unit tests passed; all 660 race/arm portfolios passed gross-budget,
point-count, PAPER-zero, and applicable per-type stake checks; original input file
hashes were rechecked unchanged. The static-plus-KRS experiment averages
role-specific Static and frozen KRS ordinal ranks; it does not treat KRS
occurrence rates as calibrated probabilities or use EV/Kelly.

Reproduction from the integrated repository, with an independent correction
audit file and the corrected existing settlement function:

```bash
python -m pytest -q tests/test_jra_20261024_capital_comparison.py
python scripts/jra_20261024_capital_compare.py \
  --data-root /workspace/scratch/c3703925e24c/keibametrics-runtime \
  --prediction-root /workspace/scratch/c3703925e24c/km-prediction-49 \
  --settlement-code /workspace/scratch/c3703925e24c/km-p0-result-fix/runtime/jra_production_postresult.py \
  --correction-evidence /workspace/scratch/c3703925e24c/km-p0-result-fix/runtime/result_correction_audits/KM-JRA-KYO-20261024-R07.json \
  --output research/jra_20261024_capital/replay.json.gz
```

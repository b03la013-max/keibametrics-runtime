# 2026-10-24 JRA frozen-input prediction replay

Implemented eight separate research arms over all 36 races / 467 runners / 9,340 saved index cells. This is **post-result exploration, not Forward OOS**. Production, original Source/FINAL, numerical rules, role widths, KRS Physics, MEC, Capital and buying permissions are unchanged. No new Learning State is introduced into the historical inputs. Raw request file SHA and canonical payload SHA are stored separately; original archived Shadow prediction-input hashes and Learning bindings are retained as references, never as a witness for the new candidates.

`candidates.predict(request, final=None)` reads only the supplied frozen request and optional original KRS summary. Result and payout access is confined to `replay.py` evaluation. New factor arms use recorded `JRA_OFFICIAL` features; their frozen Static control retains the original registered-common inputs. Every distinct head gets head-local P2 and pair-conditioned Third rankings. Candidate tickets have priorities and no stakes; the separate Capital comparison preserves original exposure.

| Frozen Role capture, 33 FINAL races including PAPER | W | P2 | P3 |
|---|---:|---:|---:|
| Original Production selection | 15 | 18 | 18 |
| Static index control | 15 | 18 | 19 |
| Context history | 15 | 17 | 22 |
| Observed ability | 15 | 16 | 19 |
| Unique official features | 15 | 18 | 20 |
| Frozen Oct18 rank model | 15 | 16 | 22 |
| Frozen head-P2 interaction | 14 | 18 | 21 |
| Frozen KRS role scores | 13 | 18 | 20 |
| BVI neutral sensitivity | 15 | 18 | 19 |

The three AKI_NO_BET races have a separate diagnostic denominator in `summary.json`; their labels use saved official post-result observations and do not establish completed Production RESULT/Learning. Set capture is separated from top-one Ordered Pair/Exact. Harm, wrong additions and all successful controls remain in the denominator. Capital/PFS effects are reported in `research/jra_20261024_capital/summary.json` and must be considered before judging an arm.

The BVI ablation's correct comparison is the Static index control: W/P2/P3 capture difference is **0/0/0** over 36 races. Its mean actual P3 rank worsens by 0.0278. Its gain against original AKI roles is not a BVI gain. DCR remains unchanged, and BVI-to-KRS counterfactual Physics is unmeasured.

351 runners have 3,422 admissible prior runs. Missing/current-day/future histories are separated. All six newcomer races have registered workout assessments, but numeric final-1f/clock observations are 0. Load, paired work, response and start readiness remain UNKNOWN. Original PAPER and AKI terminals are preserved. The compact workout `gait` field matching horse names was referred to the Source audit.

Kyoto R6 (1200m) has four frozen same-day observations, none matching surface/distance/going; transferring 1800m evidence to 1200m is not validated. The saved KRS summary contains three strategy shares and five scenario names. No new scenario, result-selected tactic or Physics rerun was created; independent course-segment mechanisms and full world-specific outcome tables remain UNKNOWN.

Tokyo R3 and Kyoto R10 have correct Pair/Third dispositions `PROTECT`, with correct EXACTA/TRIO tickets but no correct TRIFECTA. Their matrix failure is `PROTECTED_EXACT_NOT_CONVERTED`, rather than a missing Pair/Third.

`coverage.json` maps the 22 Venue P1 and 11 Venue P2 items to actual work, evidence and remaining limits. `failure_matrix.json` covers all 36 races. `replay.json.gz` contains all-runner feature/history/role migration, original Source references and frozen KRS/input audits without duplicating the large raw artifacts. `summary.json` includes the existing 19-training/22-calibration model's held-out Oct24 log-loss/Brier/ECE; this does not accept calibration or enable EV/Kelly.

Reproduce from a checkout containing the original data, or pass its path explicitly:

```sh
python scripts/jra_20261024_prediction_replay.py --data-root /path/to/immutable-data-checkout
python -m pytest -q tests/test_jra_20261024_prediction_candidates.py
```

Validation: 19 new tests pass. Unchanged probability/head-P2 regression tests pass with the original fixture checkout: 21 tests and 63 subtests. Future qualification still requires independent pre-cutoff persistence/signature evidence, at least 60 distinct races, 3 dates and 2 venues. Every current replay has OOS credit 0 and no purchase/EV/promotion authority.

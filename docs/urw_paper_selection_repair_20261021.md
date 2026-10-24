# URW PR #329 continuation: correctness repair and forward handoff

Scope: LOCAL / URW / NON-PRODUCTION PAPER. Development on 2026-10-21 JST is
post-result development, not unseen validation. No S2, model refit, Production
change, purchase, deployment, signing or scope activation was performed.

## Findings and implementation

The inherited branch/PR head was exactly
`dd200187d1db9e44bc197597bf85d2093ed8578d`; its main base was
`f4da03cc950298457c2b5da617304b1233f1b9cb`. The original checkout was clean.
The exact pre-change code is preserved in Git and in the detached local worktree
`/workspace/keibametrics-pr329-baseline`.

| Finding | Evidence and action |
| --- | --- |
| Individually invalid conditional distributions could be accepted | A synthetic uniform three-runner input with P3 values 2 and 0 retained total joint mass 1 while inflating an EXACTA's mass from 1/6 to 1/3. Negative winner and P2 values could cancel in their product. `_joint` now validates every distribution's universe, finite 0..1 values and normalization. |
| Shared Coverage suppresses independently paying ticket types | The same ordered result can pay both EXACTA and TRIO. A synthetic concentrated example loses an eligible high-lift EXACTA after a TRIO covers the same atoms. This establishes a property of the existing objective, not an actual R3 loss attribution or an EV defect. Selection is unchanged; diagnostics record within-type marginal mass and cross-type suppression. |
| Protection-only participation is possible under S1 | It is explicitly recorded separately from Core-only, mixed and complete NO-BET. KRS-on/off selection changes, additional cost, winnings, refunds and NO-BET release are evaluated separately. Missing KRS top-list entries remain UNKNOWN. |
| Result availability changed reported participation | Summaries now count known outcome-blind planned Stakes, even if a result is missing. Unknown full-day returns, PFS, balances and drawdown remain unknown. Complete settlement must match the planned per-race Stakes. |
| Forward identity/restore checks were incomplete | Duplicate runner facts are refused; the day-plan validator is code-pinned; Policy SHA is checked; writes completing after cutoff are HOLD. v2 registration requires complete-ledger checkpoints before mutation or status reporting. Empty/suffix-truncated restoration is refused against the independently supplied expected file SHA. |
| Extracted originals were not compared to every ZIP member | Replay now verifies exact member paths, bytes/SHA, private permissions and the complete extracted tree before and after use. Traversal, symlinks, duplicate paths, unsupported members, extra/missing files and CRC corruption are refused. Outputs cannot overlap original inputs. |

The added trace covers all candidates, including losing and unselected ones.
Original-Stake finances and uniform 100-yen research-unit finances are separate.
P1 reports Role additions through candidate creation and S1 selection, while
checking that rankings and joint model values stay fixed. No effect is inferred
from Role count alone.

There is insufficient private-input evidence to choose one justified S2 change.
The minimum controls remain P0S0, P0S1, P0S1_NO_KRS and same-owner Top4 BOX;
the existing four-cell comparison and separate Utility accounting are retained.
B and C are never mixed or selected retrospectively race by race.

## Invariance and implementation evidence

- S1 Policy SHA remains
  `663c63f6931d49d5cbc994ee17cef8a3075d957216db18bf02590d82d5e3c34d`.
  The 1.10 Core/KRS thresholds, 25% marginal floor, 2,000/race,
  24,000/day, 500 Protection/race, 100-yen unit and 150,000 initial research cash
  are unchanged. The cap is not a spending target.
- The shared settler, original source/result parser, Owner predictor, old
  comparison script, MEC and Capital implementation are byte-identical to the
  inherited head. No old definition hash was rewritten.
- 240 authored valid-input differential cases matched the inherited selector's
  selected tickets/Stakes, tier spending, budgets, all old Coverage fields and
  NO-BET exactly. They cover runner counts 3..7, uniform/nearly uniform/concentrated
  inputs, budget 0/300/24,000, exclusions, KRS on/off and differing source Stakes.
  There were 178 NO-BET, 10 Protection-only and 52 Core-only cases. These counts
  are synthetic contract evidence, not race-day performance observations.
- The unchanged baseline passed 655 related CI tests and 39 selection/MEC/Capital
  tests: 694 distinct tests. The requested three-file 37-test run is a subset.
- The corrected selection/refund/archive/forward/MEC/Capital suite passed 92
  tests. Its new cases cover conditional corruption, overlapping payout events,
  multiple refunded horses and differing Stakes, duplicate prevention, missing
  results, private archive attacks, crash reservations and complete restoration.
- The final related 20-file CI suite passed 655 tests, with zero failures,
  errors or skips. Together with the 92-test research suite, 747 distinct tests
  passed on the corrected implementation. Compile, YAML, CLI and synthetic
  readback checks also passed.
- Independent review found two new accounting-helper defects (duplicate tickets
  lost during dictionary conversion and planned/settled Stake mismatch). Both
  were fixed with fail-closed checks and regression tests before final validation.
  The additional ledger-output contamination finding was fixed before any
  directory creation/write, with seven no-mutation regressions. Final independent
  review found no further concrete defect.

The cloud sandbox overlays protected `.git` directories under `/tmp` and
`/workspace`; private-storage tests must use a dedicated non-Git directory such
as `/var/tmp/keibametrics-tests`, with scoped write access/escalated execution.
No private-storage guard or test assertion was weakened. The workflow's existing
compile, YAML, CLI import and synthetic 12-race/131-runner readback checks are
also retained.

## Historical data: not reproduced

The R3 archive's filename, expected size/SHA and internal paths were supplied as
text, but the actual ZIP was not present in the available attachments or mounts.
Thus no real private `INPUT_ROOT` has been established; `/private/...` in the
runbook is an example, not a discovered location. The R3 figures in the directive
were not used as code constants or regenerated as substitute inputs. Actual R3
spending, return/refund, lost hits, Protection economics and B/C concentration
differences have **not** been recalculated. Neither the repaired conditional
validation nor the synthetic overlap example proves the cause of the real R3
losses. Verified valid inputs preserve S1 selections.

Required missing private inputs:

| Input | SHA / purpose |
| --- | --- |
| `URW_20261021_Repair_Result_R3.txt` | SHA not supplied; report/original cross-check. |
| `URW_20261021_Repair_Evidence_R3.zip` and `EVIDENCE-MANIFEST.json` | Expected ZIP size/SHA and member locations were supplied; file bytes are unavailable, so receipt/hash and every member remain unverified. The ZIP/tree checker does not pretend to validate an unavailable external MANIFEST. |
| Original PAPER: `frozen/Rxx/{comparison.freeze,source-observation,numerical}.json`, `paper/Rxx/{BASELINE,CANDIDATE}/downstream.audit.json` | Member SHA/bytes come from the original MANIFEST; required for the 24 unchanged B/C series and all four cells. |
| `immutable-inputs/equal_budget_prestart.json` and `immutable-inputs/utility-counterfactual-prestart.json` | Member SHA not yet readable; required for fair fixed and analytic same-spend accounting. |
| `evaluate_observed_oos.py` | Required pinned SHA `b92c10aba7e1b0dd4577c10a21a7c0e12cf84652778b022f5f3bad2db5b9370d`. |
| `frozen_ticket_attribution.py` | Required pinned SHA `dcaa001215dc691b790b1cbead7faf2d6b1cee664fd3982a5ab18648ce6b5e59`. |
| Saved official `Rxx.html.gz` / `Rxx.receipt.json` | SHA not supplied; verify saved Raw/Receipt before settlement, including 9R #2 refunds. Do not refetch or replace missing payouts with zero. |
| `closure/forward-final-registration.json` and complete `closure/forward-final-ledger/` | Registration identifier supplied as `27fb85e8d35e0f02bdecb5b29d9986ac57c10119609f9f4daf21c51c8198d762`; artifact and ledger unavailable, so not independently verified or rewritten. The old canonical path belongs to the prior environment and must not be rewritten for relocation. |

## Next unknown-future cohort

Actual new registration ID: **none**. Actual registered day Plans: **0**. Actual
race Freezes: **0**. Independent external saves/readbacks: **0**. Test fixtures
with future dates are labelled synthetic and do not count toward these totals.

At the initial check, the real clock was 2026-10-21 21:46 JST. The official NAR
program request received proxy HTTP 403. The repository's saved 2026-10-22
preparation record separately reports `SOURCE_POLICY_ROBOTS_DISALLOWED` for that
program path. The existing NANKAN client's robots-checked calendar request also
returned `SOURCE_POLICY_ROBOTS_UNKNOWN`. No restriction was bypassed. Thus the
next eligible whole-day schedule, current full-runner input, full KRS artifacts
and usable external private anchoring destination remain unverified/unavailable.
No new monitor was installed and the stopped old OOS worker was not restarted.

Use the complete command sequence in [the research runbook](urw_paper_selection_research.md).
It reuses `register`, `register-day`, `freeze` and `cohort-status`, with immutable
`checkpoint` export and `verify-restore` checks. Restore every ledger member at
its original canonical path, including reservations and failed attempts.
The latest checkpoint and its expected exact-file SHA must be retrieved from
the existing authorized private external store before resuming. Local hashes
cannot prove independent timing or detect simultaneous rollback of all local
copies. A new v2 registration is required; old registration/code are not silently
reused. A persisted orphan after a late or failed write is not an accepted Freeze:
the corresponding completion ledger governs its HOLD status.

The existing frozen/audits(BASELINE,CANDIDATE)/observation input contract remains.
Do not substitute simplified predictions for the full model/KRS path. Freeze
the whole-day Plan before its first cutoff. Save/retrieve source, model, code,
Policy, selected tickets and all Stakes before cutoff through the authorized
private external store. Minimum 60 races/five dates and existing fixed
date-cluster/noninferiority gates remain; neither reaching the minimum nor a
single profitable day implies performance acceptance.

Engineering contract tests, historical development results, forward performance
acceptance and Production authorization remain separate. This change grants no
forward performance pass or Production authority.

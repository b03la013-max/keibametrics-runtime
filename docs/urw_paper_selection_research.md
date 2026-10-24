# URW private selection experiment

This is an unapproved, unsigned PAPER policy experiment, outside the original
MEC portfolio. No Production entry, Owner scope, default capital policy,
simulation seed, signer or deployment is changed. Original artifacts are inputs,
never output paths. All outputs must be private, absolute, Git-free directories.

`runtime/urw_paper_selection.py` fixes research ceilings at 2,000 yen/race,
24,000 yen/day/configuration, with at most 500 yen/race for Protection and uniform
100-yen units. A ceiling is not a spending target. Conditional joint model mass
and joint KRS occurrences are uncalibrated support, not prices, probabilities,
EV or a user's betting budget. Unknown top-list entries are not zero support.

## Replay

Use `python scripts/urw_paper_selection_replay.py replay --help`. Inputs are the
unchanged original PAPER archive/extracted directory, its pre-fixed equal-budget
protocol, the separate Utility artifact, the original isolated analysis helper,
and saved official result Raw/receipt pairs. No HTTP is performed. Results are
read only after each race's outcome-blind research views have been saved.
Missing witnesses retain planned investment and the fixed denominator; full-day
return/PFS remain unknown until every race is settled. Refunds are separate from
winning returns. The original helper and its prior HOLD records are unchanged.
The private original ZIP and extracted tree must match member-for-member, with
directories 0700/files 0600, before and after Replay. Outputs must not overlap
any original input directory. This local ZIP/tree agreement does not stand in
for the independently supplied evidence MANIFEST or trusted archive digest.
The result-revision adapter separates explicit refunds and delegates live tickets
to the byte-unchanged preregistered shared settler. Its old definition hashes and
historical cohort are not rewritten to make CI pass.

P0S0 is the immutable original reference. P0S1 selects from that same universe.
P1 keeps model values/rankings fixed and tests limited, multi-evidence Role
hypotheses. P1S0 applies the same old S0 rule; P1S1 uses the identical S1 selector.
Every original candidate has a selected/nonselected reason. Lost semantic
coverage is reported; it is never relabelled 100% material coverage. Top4 BOX and
KRS-off are diagnostics, not retrospectively selected winners.

## Next unknown-future cohort

The corrected implementation requires a **new v2 registration**. Keep the old
registration and its exact code at `dd200187d1db9e44bc197597bf85d2093ed8578d`;
do not reseal or apply it to this code. The S1 Policy itself is unchanged.

1. `register --model-bundle /private/comparison.freeze.json --ledger /private/ledger --output /private/registration.json`
2. `checkpoint --registration /private/registration.json --output /private/checkpoint-initial.json`.
   Save the complete registration, ledger and checkpoint through the existing
   authorized external private store. Retrieve that checkpoint and retain its
   exact-file SHA from the independently saved copy. The CLI's local SHA output
   alone is not independent anchoring or freshness evidence.
3. Before the first cutoff, `register-day --registration /private/registration.json --day-plan /private/official_plan.json.gz --ledger-checkpoint /private/checkpoint-initial.json --expected-checkpoint-sha256 <trusted-file-sha>`.
   This reuses the existing `local_reference_day.verify_plan` whole-day contract.
4. Export a fresh `checkpoint` to a new immutable filename after registering the
   day. Save/retrieve it externally before the next ledger mutation. Repeat this
   after **every** attempt, including HOLD or interrupted reservations. Restore
   every member byte-for-byte at the original canonical ledger path and run
   `verify-restore --registration /private/registration.json --ledger-checkpoint /private/latest-checkpoint.json --expected-checkpoint-sha256 <trusted-file-sha>`.
   Empty or suffix-truncated ledgers cannot match that checkpoint. An old local
   checkpoint plus its old hash cannot independently prove freshness; the latest
   external readback is still a prerequisite when resuming.
5. The existing forward path produces the comparison, both original downstream
   audits and source observation. Package them as exactly
   `{"frozen": comparison, "audits": {"BASELINE": audit, "CANDIDATE": audit}, "observation": observation}`.
6. `freeze --registration /private/registration.json --ledger /private/ledger --input-bundle /private/bundle.json --output /private/new-race-revision --ledger-checkpoint /private/latest-checkpoint.json --expected-checkpoint-sha256 <trusted-file-sha>`
7. Export/save/retrieve the next checkpoint, then `cohort-status --registration /private/registration.json --output /private/new-status-revision.json --ledger-checkpoint /private/latest-checkpoint.json --expected-checkpoint-sha256 <trusted-file-sha>`.

The registered code/model/policy hashes and canonical ledger are mandatory.
The model output is reproduced with the existing conditioned predictor. The
clock cannot be supplied through the CLI. Past, inconsistent, duplicate and
result-bearing inputs are refused. A reservation event is saved before the
Freeze; an interrupted attempt cannot reset a budget or silently retry a race.
Uninvoked races remain visible against the registered whole-day plan. Restore
the complete original ledger when resuming; never replace it with an empty one.

Save/anchor each immutable registration/Freeze externally before its cutoff.
The local artifact explicitly says independent anchoring is pending; a self-hash
does not prove timely delivery or earn formal OOS credit. These commands do not
install a worker, create a monitor, send Venue messages or guarantee continued
execution. Invoke them from the existing approved non-Production forward path.

The development day is excluded from performance acceptance. Minimum 60 races,
five dates, original date-cluster bootstrap and noninferiority gates remain
unchanged. All comparisons retain failed/missing/NO-BET races. Separate losses,
lost hits, Protection cost, KRS harm, participation, unused capital and the Top4
diagnostic must be reviewed. No automatic performance pass or promotion exists.

Original Venue publications are never rewritten or substituted by these files.
Research trees carry a separate classification and reuse the existing renderer's
exact ticket/stake expansion check. No actual user-screen receipt is inferred
from that offline check.

## Correctness repair and diagnostics

The selector now rejects individually unnormalized, negative, nonfinite or
wrong-universe winner/P2/P3 distributions even if their joint products sum to
one. S1 thresholds, budget rules and the selected-ticket algorithm are retained.
Every candidate reports per-tier threshold, remaining budget, unknown KRS and
shared marginal-Coverage blockers; selected candidates also preserve their
decision-time trace. Core-only, Protection-only and complete NO-BET are distinct.
Shared ordered-scenario Coverage is not additive payout: an EXACTA and a TRIO
can both pay for the same result. No S2 or profitability claim follows from this
diagnostic; the private R3 inputs are needed before choosing a policy change.

Replay adds KRS-on/off additions/removals and separate winnings/refunds,
concentration by conditional context, P1 Role-to-candidate-to-selection flow,
and an outcome join for **all** candidates. Original-Stake and uniform research
unit finances are labelled separately. Missing results cannot lower known
participation: summaries use the outcome-blind planned stakes and retain unknown
full-day return/PFS until every result is resolved.

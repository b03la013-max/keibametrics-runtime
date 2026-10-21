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

P0S0 is the immutable original reference. P0S1 selects from that same universe.
P1 keeps model values/rankings fixed and tests limited, multi-evidence Role
hypotheses. P1S0 applies the same old S0 rule; P1S1 uses the identical S1 selector.
Every original candidate has a selected/nonselected reason. Lost semantic
coverage is reported; it is never relabelled 100% material coverage. Top4 BOX and
KRS-off are diagnostics, not retrospectively selected winners.

## Next unknown-future cohort

1. `register --model-bundle /private/comparison.freeze.json --ledger /private/ledger --output /private/registration.json`
2. Before the first cutoff, `register-day --registration /private/registration.json --day-plan /private/official_plan.json.gz`.
   This reuses the existing `local_reference_day.verify_plan` whole-day contract.
3. The existing forward path produces the comparison, both original downstream
   audits and source observation. Package them as exactly
   `{"frozen": comparison, "audits": {"BASELINE": audit, "CANDIDATE": audit}, "observation": observation}`.
4. `freeze --registration /private/registration.json --ledger /private/ledger --input-bundle /private/bundle.json --output /private/new-race-revision`
5. `cohort-status --registration /private/registration.json --output /private/new-status-revision.json`

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

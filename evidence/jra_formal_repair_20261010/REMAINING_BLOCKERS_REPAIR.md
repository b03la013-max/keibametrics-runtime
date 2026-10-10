# Remaining blocker repair

Current main remains 158be61; Current Authority R44.

Three additional acquisition defects were repaired: full-history records no longer discard independently matched official detail sectionals/margins/positions; workout acquisition failure no longer prevents independent speed acquisition; multi-row speed headers preserve row/column spans so the true five-run average is read and the second header cannot become a fictitious runner. Required workout failures remain errors.

The immutable Kyoto R09 registered speed snapshot contains only three real runner rows, with five-run averages 74,81,81; the earlier parser claimed a fourth runner named 2走前 and selected historical-run cells instead of the average. This is not a complete 16-runner speed source. No missing runner or index is imputed. Matching official history/detail uses date, venue, surface, distance, finish, field size and going; ambiguous or mismatched observations are omitted.

The existing registered closing-percentile rule is now applied to real matched prior sectionals with the same surface/distance/going, at least two observations per runner and four comparable peers. It is an observed sectional comparison, not a pace-adjusted speed figure or probability.

Local validation: 97 tests plus 77 subtests passed (dependency deprecation warnings only). Five real SOURCE replays remain historical diagnostics, zero OOS. Kyoto R09 remains 90/208 calculable base cells and 0/320 complete Full20; closing evidence alone does not satisfy SSI coverage.

Unresolved external/temporal requirements: complete independently acquired all-runner speed data; pedigree performance population evidence rather than sire identities; registered readiness evidence; 30 actual future Full20 pre-cutoff freezes, later official outcomes, market-baseline evaluation and independent authorization. No prior Candidate cohort, post-cutoff fetch, retrospective freeze or synthetic record may satisfy these requirements. The repair cannot truthfully turn future observations into already completed ones.

Changes remain in draft PR190, not deployed/main. No signatures, formal FINAL or purchase authority were fabricated.

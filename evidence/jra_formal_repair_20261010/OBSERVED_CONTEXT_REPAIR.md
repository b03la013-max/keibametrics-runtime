# JRA observed context and forward validation repair

Latest main: 158be61cba46358d3258ca728bd183cf70b4ca18. Current Authority: KM-FAMILY-CURRENT-AUTHORITY-20261008-R44.

The Kyoto R09 signed SOURCE calendar described a two-year-old turf 2000m race, but its immutable official detailed card described a three-year-old-and-up dirt 1400m race. The repair verifies the raw snapshot hash, official provenance, cutoff and race identity, and derives the observed context from that detailed card. Old signed envelopes are not rewritten. New SOURCE acquisitions bind observed context before signing and preserve calendar discrepancies.

Historical Kyoto R09 Production base coverage improves from 61 to 90 of 208 cells on current main; 118 remain blocked. Full20 remains zero of 320. Five real stored SOURCE envelopes pass local Ed25519/hash verification; independent OIDC verification is not claimed by this local audit. Kyoto R10 records were absent from the checked repository directories, so its actual runtime failure is not inferred from R09.

65 tests and 77 subtests passed. Four workflow YAML and shell syntax checks passed.

A separate immutable Static Owner forward OOS cohort uses only SOURCE_ONLY Full20 Production numerical inputs, actual pre-cutoff timestamps and git commit witnesses, current policy fingerprints, and subsequently observed official results. It does not import the old Candidate cohort, approve Production, prove market superiority automatically, or issue FINAL. It uses the existing scheduled result collector. Thirty actual future eligible races and independent review remain required; historical diagnostics contribute zero.

Remaining blockers: missing official evidence for complete Production indices (including SSI), independent Static Owner authorization, and unavailable Kyoto R10/R9 attachment evidence. No synthetic signature or post-race formal FINAL has been issued. The prior external KRS mechanical acceptance established execution connectivity, not this race's formal completion.

# LOCAL Current-State Lineage v1.1-CSL Rev.1
Profile: `KM-LOCAL-CSL-v1.1-REV.1-20260923`
Status: ACTIVE / PRODUCTION TEMPORAL LINEAGE / NON-NUMERICAL
Compiled artifact SHA256: `8d2d10511b2ffedacfeefaa1590b083ed0b8bb6921dfab019135db06dfa68077`

The lineage separates source_available_at, ingested_at, knowledge_cutoff, source_freeze_at, static_freeze_at and result_available_at. Same-day evidence may affect only races whose cutoff occurs after the evidence became available. Meeting-start transient state resets to UNKNOWN unless current authority says otherwise. State TTL classes are RACE-LOCAL, SAME-DAY, MEETING-LOCAL, VENUE-PERSISTENT-CANDIDATE and FAMILY-CANDIDATE. Material observations create a new revision; old state is SUPERSEDED. State, runner universe, KRS and FINAL hashes must remain lineage-consistent. Race_n results update Race_{n+1}, not Race_n.

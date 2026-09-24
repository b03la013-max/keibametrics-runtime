# LOCAL Input / Source Operations v1.7

Profile: `KM-LOCAL-INPUT-SOURCE-OPS-v1.7-20260924`  
Predecessor: `KM-LOCAL-INPUT-SOURCE-OPS-v1.6-20260924`  
Status: ACTIVE / LOCAL-WIDE / NON-NUMERICAL / SOURCE-ENRICHMENT-v3 / FAIL-CLOSED-CORE / OPTIONAL-SHADOW-ENRICHMENT / SBO-PUBLIC-SHADOW-RUNTIME-VERIFIED

## Current Source Route

```text
Race Metadata
→ Automatic NAR Official Manifest
→ NAR Race Card / Odds / Same-day Results
→ Raw Snapshot + cutoff validation
→ Official Runner Universe
→ NAR Horse / Rider / Trainer official profiles
→ Same-day position-bias SHADOW
→ Pedigree identity seed
→ JMA AMeDAS official weather SHADOW
→ Point-in-time population seed SHADOW
→ SBO public index/recommendation signal SHADOW
→ SOURCE Freeze
→ Signed SOURCE Receipt
→ Request Runner Universe Match
→ Numerical Materialization / Provenance
→ External PRE_KRS Universe Match
→ KRS
```

## Mandatory vs enrichment

Formal core remains fail-closed on the required NAR race-card/source lineage and Official Runner Universe.  
NAR auxiliary entity profiles, JMA weather and point-in-time population evidence are attempted automatically but remain evidence-layer SHADOW inputs unless a later OOS promotion explicitly changes Production authority.

JMA outage or an unavailable optional auxiliary profile does not silently fabricate a value. Missing optional enrichment is recorded as unavailable/unknown. A caller may explicitly request `require_jma_weather=true` or `require_auxiliary_profiles=true` for acceptance/testing.

## NAR Auxiliary Evidence

Profile: `KM-LOCAL-NAR-AUXILIARY-EVIDENCE-v1.0-20260924`

Captures from official NAR-linked pages:
- horse profile and pre-target-date history
- rider profile
- trainer profile
- same-day position bias derived from completed official same-day races
- pedigree identity seed

No result on or after the target race date may be injected into the target-race historical horse profile.

## JMA Weather

Profile: `KM-LOCAL-JMA-WEATHER-EVIDENCE-v1.0-20260924`

Official JMA AMeDAS station metadata selects a nearby observation station. Captured fields may include temperature, 10m/1h/3h/24h precipitation, wind speed/direction, humidity, sunshine and snow depth. JMA weather is context evidence; NAR remains authoritative for the official track-going declaration.

## Point-in-Time Population Seed

Profile: `KM-LOCAL-POINT-IN-TIME-POPULATION-LEDGER-v1.0-20260924`

The ledger joins current-field pedigree identities to pre-target-date NAR horse histories and creates descriptive sire/damsire cohorts by venue, distance bucket and going group.

Boundary: this is selection-biased current-field seed data, not a complete all-horse population and not Production BVI authority. Cohorts below the sample floor remain INSUFFICIENT.

## Universal-source boundary

The following do not currently have a verified universal NAR official automatic source:
- training
- trainer comments
- paddock evaluation

They may enter through user-supplied or separately verified venue-specific adapters, with separate source authority. No paid/private provider is scraped by default.

## Production boundary

This revision changes source collection and signed evidence persistence only. It does not change:
- Production numerical formulas or weights
- KRS Engine or parameter_map
- MEC/Capital authority
- probability/EV/Kelly authority

Current Production numeric suite remains `KM-LOCAL-RENDERED-INTEGRITY-20260827-R3` FROZEN.


## SBO Public Shadow Source

Profile: `KM-LOCAL-SBO-PUBLIC-SHADOW-EVIDENCE-v1.0-20260924`

Automatic LOCAL source acquisition now attempts one public SBO race page per target race when `include_sbo_shadow=true` (default).

Boundary:
- source class: `THIRD_PARTY_PUBLIC_SHADOW`
- authority: `SBO_PUBLIC_NON_OFFICIAL`
- official: false
- production_authority: false
- prediction_authority: false
- NAR official race facts always have higher authority
- SBO does not overwrite runner identity, scratch, going, post time, official odds or result facts
- no SBO value is mapped directly to Production HPI/TPI/W/P2/P3/KRS/EV/Kelly
- Production promotion requires separately preregistered Frozen Unknown OOS evidence

Captured normalized fields may include horse number/name, recent index, distance index, going index, average index/rank and the public recommendation groups.

Storage boundary: persist normalized extracted fields plus source URL, fetch time, raw SHA256 and byte count. Do not persist or redistribute the raw page body as the SBO sub-artifact.

Robots policy is checked before fetch. A disallow or indeterminate robots failure causes SBO capture to remain unavailable rather than bypassing site policy.

For OOS eligibility, SBO capture must be PRE_CUTOFF, PRE_START, and reconcile with the NAR Official Runner Universe. Archived/post-start capture may be used only for parser acceptance and never as future-prediction evidence.

Production runtime acceptance: GitHub Actions run `36015590690`; Railway deployment `511920b6-60c9-4afa-93e1-4d36948bab09`; SOURCE receipt `463b5259cc244394af7dcd4ea55a4bbaff546df0e0db47eb35ca073f9752c20e`; official/SBO runner count 9/9 MATCHED; tamper rejection PASS.

This source-enrichment revision changes no Production numerical formula, KRS parameter, MEC, Ticket or Capital rule.

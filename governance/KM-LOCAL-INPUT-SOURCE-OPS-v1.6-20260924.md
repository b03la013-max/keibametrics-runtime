# LOCAL Input / Source Operations v1.6

Profile: `KM-LOCAL-INPUT-SOURCE-OPS-v1.6-20260924`  
Predecessor: `KM-LOCAL-INPUT-SOURCE-OPS-v1.5-20260923`  
Status: ACTIVE / LOCAL-WIDE / NON-NUMERICAL / SOURCE-ENRICHMENT-v2 / FAIL-CLOSED-CORE / OPTIONAL-SHADOW-ENRICHMENT

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

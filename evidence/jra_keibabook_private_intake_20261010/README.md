# User-authorized Keibabook Smart Premium intake

Authenticated browser capture acquired Kyoto 2026-10-10 R9 (16 runners) and R10 (15 runners) from the user's existing Smart Premium subscription. No subscription purchase or credential export occurred. Raw subscriber HTML, comments and fact records remain in the local private outputs directory and are excluded from this repository.

Observed coverage: R9 47 historical speed values, 55 workout entries, 16 stable comments; R10 42 historical speed values, 53 workout entries, 15 stable comments. Twenty-eight observed sire/damsire links yielded 728 population rows covering surface, age, going and distance. Population aggregates were captured after cutoff and may contain today's outcomes; they are Replay diagnostics only. Counts are facts, not completed Production index cells.

The adapter validates immutable capture hashes, exact race URL paths, capture timestamps and official runner number/name correspondence across ability/workout/stable pages. Target-day or later performance history is rejected. Zero-start pedigree populations remain unknown. Kyoto R9 was matched to existing official SOURCE runner identities. R10 has cross-page consistency but lacks an independently verified JRA SOURCE in the current evidence set; no official identity validation is claimed for it.

A content hash is not a cryptographic signature. The adapter emits neither Signed SOURCE nor Signed FINAL, does not promote a provider or Candidate, and increments no prospective OOS count. Existing signed SOURCE objects remain unchanged. Provider/evaluator conformance and authentic prospective full SOURCE remain necessary before any Production use. Static Owner requires actual forward validation and independent approval; historic races cannot satisfy that requirement.

Validation: repair regression plus intake tests: 87 passed and 77 subtests passed. Whole-repository run: 560 passed, 117 subtests passed, 3 failed. Two failures arise from shared `app`/`source_acquisition` import-name collisions between JRA and LOCAL tests; one LOCAL test asserts an obsolete literal in the non-JRA runner. These are recorded separately from this adapter's passing regression suite.

Run privately:

```sh
python -m runtime.jra_keibabook_private_intake --manifest PRIVATE/manifest.json --official-runners PRIVATE/official-runners.json --race-date 2026-10-10 --book-race-id 202604000309 --prediction-cutoff ACTUAL_ISO_CUTOFF --output PRIVATE/intake.json
```

The official-runners JSON must contain authoritative runner_id/name records. Do not substitute Book-derived identities to claim JRA validation. Capture collection requires the user's authenticated supported browser; no cookie extraction or unauthenticated subscription bypass is provided.

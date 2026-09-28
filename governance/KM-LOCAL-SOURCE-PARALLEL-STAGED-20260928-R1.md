# LOCAL Source Parallel Acquisition Staged R1

Profile: `KM-LOCAL-SOURCE-PARALLEL-STAGED-20260928-R1`

This change is staged code only until the live Railway runtime is redeployed and verified.

It parallelizes independent external SOURCE fetches with a bounded worker pool while preserving the original manifest order before evidence merge and hash construction.

Unchanged invariants:

- source identity and duplicate checks happen before network fetch;
- authority priority merge is unchanged;
- equal-priority conflict handling is unchanged;
- required source failure remains fail-closed;
- cutoff/staleness checks remain unchanged;
- raw source snapshots remain retained and hashed;
- Signed SOURCE verification remains mandatory;
- no prediction, numerical, KRS, MEC, Capital, or Venue rule changes.

The active runtime bundle is explicitly frozen in `current_execution_gateway.json`. Candidate checkout files do not redefine live runtime authority. Activation requires a verified Railway deployment followed by an explicit Gateway/Current Authority transition.

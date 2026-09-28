# LOCAL Source Parallel Acquisition Staged R1

Profile: `KM-LOCAL-SOURCE-PARALLEL-STAGED-20260928-R1`

This artifact records the staged activation history. The candidate was promoted into the live LOCAL Runtime Rev.8 after Railway deployment and a passing Execution Gateway canary. It is no longer a pending staged candidate.

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


## Promotion closure

Promoted runtime: `KM-LOCAL-PHYSICAL-RUNTIME-v1.5-REV.8-20260928-RACE-DAY-SOURCE-PARALLEL`

Verified active source implementation SHA256:

`3311af0423ba6e8bdf5d427da7b4a9d36a76c20daa682f3ddc7523ee1545a2df`

Gateway canary evidence: GitHub Actions run `36430165650` / PASS.

This promotion changed SOURCE transport latency only. Production prediction numerics, KRS physics, MEC-R3, Capital Policy and Venue prediction rules remained unchanged.

# LOCAL KRS-Engine Ops v1.7 Rev.1
Profile: `KM-LOCAL-KRS-ENGINE-OPS-v1.7-REV.1-20260923`
Status: ACTIVE / PRODUCTION ENGINE OPS / NON-NUMERICAL / SIGNED-FULL-LIFECYCLE
Predecessor: v1.6 Rev.3
Compiled artifact SHA256: `de03f2bf714b8956ed583cc294f2686e1af49deafd19d56cd16d7716c4f85e41`

## Current execution owners
- GitHub: code/spec/mapping source of truth.
- Base44: formal orchestration, session/manifest/policy gate/receipt ledger.
- Railway: PRE_KRS, KRS, FINAL, FORMAL, RESULT and signed receipts.
- Venue: venue-specific prediction context only.
- MEC/Capital: common decision/execution layers after semantic freeze.

## Mandatory execution contract
1. Freeze prediction cutoff and source snapshot.
2. Resolve full runner universe and required-index manifest.
3. Separate terminalization from actual numerical calculation.
4. PRE_KRS must verify identity, revision, static freeze and numerical coverage.
5. Signed PRE_KRS/KRS/FINAL/RESULT receipts must be verified; self-declaration is not proof.
6. KRS execution records Engine/parameter attestation, run count, seed and hashes.
7. FINAL closes Prediction Package, MEC, Capital, Ticket Trace, canonical/rendered transport and temporal state.
8. RESULT closes Official Result, Frozen FINAL linkage, settlement-safe PFS, failure localization and learning state.
9. PENDING/UNKNOWN settlement must not become return=0.
10. Post-start processing is replay, not formal pre-race execution.
11. FCG-LOCAL v1.1.0 is compatibility/regression source only; it no longer owns FINAL authority.
12. KRS-LOCAL Runtime Package v1.2.0 is HISTORY-FROZEN / COMPATIBILITY. Current runtime is KM-LOCAL-PHYSICAL-RUNTIME-v1.4-20260923.
13. No numeric or predictive policy change.

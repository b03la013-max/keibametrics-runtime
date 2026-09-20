# JRA PRE_KRS Terminal Compatibility Adapter v0.1

Profile: `JRA-PREKRS-TERMINAL-COMPAT-v0.1-20260920`

Purpose: bridge the R2 semantic terminal states to the legacy PRE_KRS request schema without changing numerical meaning.

Authoritative semantic states remain:
- CALCULATED
- RULED-HOLD
- NOT-APPLICABLE

Legacy `quorumprobe /pre-krs` currently treats only request field `status=CALCULATED` as resolved. Therefore the adapter emits `status=CALCULATED` for all three permitted semantic terminal states **only as a transport gate token** and additionally sends `terminal_status`.

For RULED-HOLD / NOT-APPLICABLE:
- `formal_value = null`
- `transport_value/value = 50`
- `missing_flag = true`
- rule id / mapping version are preserved.
- 50 is not an ability score, probability, weakness score or market estimate.

Any UNRESOLVED / NOT_CALCULATED / MISSING_REQUIRED_INDEX / SPEC-MISSING remains non-CALCULATED and must fail PRE_KRS.

This is a NON-NUMERICAL compatibility repair. It does not modify KRS-Engine or parameter coefficients.

# LOCAL Automatic Static Shadow Owner / 2026-10-14

Status: **SHADOW / NON-PRODUCTION / UNVALIDATED / RESULT-BLIND / NO AUTO PROMOTION**.

## What now works without per-race manual ranking

The authorized Race-Key Single Entry (merged PR #267) takes a five-field
venue/date/race/post/cutoff request and executes signed SOURCE and full 29-index
terminal diagnostics on the GitHub runner. When no canonical result-blind
chat-owned Static exists and the current clock is strictly before cutoff,
`runtime/local_race_entry.py` now generates a separate
`entry-out/shadow_prediction.json` with
`runtime/local_race_key_shadow_owner.py`.

The output contains source receipt/snapshot IDs, all-runner rankings,
W/P2/P3 roles, a transparent provisional paper width, a paper EXACTA /
TRIFECTA ticket collection, 100-yen paper stakes, and frozen time.
The running workflow commits only the first prestart candidate for the
execution_id under `runtime/local_race_key_shadow/<execution_id>.json`.
A later retry does not rewrite the prior forecast.

## Hypothesis / limitations

- Uses only already-existing numerical names ZAI-WIN, ZAI-PLACE, T3I-L;
  the score sorting and winner separation bands 15 and 7 are a new,
  **untested ordinal hypothesis**. Never state this is a calibrated probability,
  Production mapping, ticket or approved AKI.
- Required all 29 fields must terminalize and numeric closure be strict.
  RULED-NEUTRAL remains expressly uncertain and must never become a
  negative ability finding.
- No pair-specific third empirical interaction is claimed; the provisional
  W/P2/P3 row combination is an OOS baseline, not a replacement of
  current Venue-specific Semantic / MEC / Capital.
- A formal Signed FINAL still requires the existing authorized chat-owned
  full Static, correct temporal freeze, and external KRS/FINAL receipts.
  The Shadow cannot fill or override that Static; no Production prediction,
  purchase authorization or authority manifest is changed.
- The shadow artifact is useful for **future** prospective OOS after the
  exact code fingerprint is frozen. Never use past results or silently adjust
  coefficients to make a historical race pass.

## Acceptance requirements

1. Candidate tests pass and unchanged LOCAL SOURCE / Formal regressions pass.
2. One unknown-future GitHub Race-Key dispatch completes signed SOURCE,
   exact 29-index diagnostic and immutable shadow before cutoff.
3. Signed external FINAL remains HOLD if approved Static is absent.
4. Compare prediction quality and paper PFS to the frozen Production baseline
   across predeclared forward OOS races; estimate missingness, calibration,
   exposure and downside risks independently.
5. Only explicit owner authorization + Current Authority promotion may
   permit Production numerical prediction consumption; this PR does NOT.

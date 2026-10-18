# URW Candidate KRS identity repair

Candidate v0.2's offline audit passed only `venue/distance/surface/course` to the
unchanged Engine. The Engine's native `prediction_id/date/race_no/racecourse`
were absent: six different races produced `SIM-0910953580` at seed1/runs5000.
The Engine also uses `prediction_id` in its per-draw seed namespace, so this is
an input lineage and reproducibility defect, not merely a display omission.

Candidate v0.3 carries the official-card-bound race date/number/post through the
Static freeze and supplies native race metadata and the URW canon ID. Invalid
calendar identity, boolean/noninteger/out-of-range race numbers fail closed.
No Engine, parameter map, numeric formula, Production Owner, KRS Physics, MEC,
Capital or signed historical artifact is changed. Fixing the seed namespace
necessarily changes offline simulation draws; no numerical effect is fitted.

## Actual offline diagnostic

`replay_report.json` retains all seven selected historical archives: six
complete and one HOLD (`URW_ACTIVE_UNIVERSE_MISMATCH`, Sep23R07). The original
signed SOURCE lacks a complete Active/Declared/Status registry; it is not
backfilled. Each completed race executes the actual pinned Engine5000 times
with seed1 and the unchanged LOCAL parameter map. All six output snapshots
carry the expected race identity and have distinct SIM IDs.

- Engine SHA256: `9929df994aa7964173edef9af7e9a705628ce377babf22df3af4e280fc275421`.
- Engine reference already exists in PR305 at HEAD
  `94f18659f89269e36e3cc91a73404567685b9dd7`, path
  `evidence/jra_day_review_20261017/independent_review_probes/recovered_runtime_reference/KRS-Engine_v1.1.0_PORTABLE.py`.
- LOCAL parameter SHA256:
  `d8c027ee5bcc8fd3d2c248e8059b341776be38910e833d7589f09ab817c161f5`.
- Original signed SOURCE envelopes are Ed25519-verified using the independently
  pinned LOCAL trust key, then the full29 materializer and existing URW adapter
  run without result labels. Original archive hashes and separate historical
  envelope verification are retained.
- `predictions_before_labels.json.gz` holds the actual-clock Candidate/PAPER
  inputs, Engine outputs and utility proposals before the separate label pass.
  It is retrospective research, has no prestart freeze, new signature or OOS
  credit. The compressed file is a derivative, not a new Signed artifact.

Static W/P2/P3 captures remain3/5/4 of six completed portfolios; the non-veto
KRS Shadow union also captures3/5/4. No actual-top3 rescue proposal is observed;
false pair/Exact proposals remain. The three Sep24 Winner misses persist.
PAPER semantic portfolios remain45,400JPY investment /33,420JPY return,
73.6123% descriptive historical PFS. The held race remains in the selected
denominator7, receives PFS N/A and is not assigned0%. Stored labels have mixed
provenance and were not freshly fetched from official RESULT in this run.

**Quality remains HOLD.** No genuine Forward OOS, calibrated scenario effect,
material Exact justification, Production numerical consumption authority or
URW Production Owner activation has been established. This repair does not
justify a formal prediction, a recommendation, a purchase or a LIVE send.

## Reproduce and verify

Download the seven original Actions archives to a local directory using the
run IDs and exact hashes in `scripts/urw_candidate_krs_replay.py`. Supply the
already-published pinned Engine reference; no Engine copy or new API is needed.

```sh
python scripts/urw_candidate_krs_replay.py --archives /path/to/archives \
  --engine /path/to/KRS-Engine_v1.1.0_PORTABLE.py \
  --baseline-outputs /path/to/anonymous-v02-engine-outputs \
  --output /path/to/new-output-directory
python -m pytest -q tests/test_urw_owner_candidate.py tests/test_local_south_kanto.py
```

The baseline outputs are the v0.2 offline5000/seed1 outputs with the same
unchanged Engine and parameter SHA. Their snapshots/evaluations are retained
in `replay_report.json`; no baseline artifact is rewritten by the v0.3 run.

Local focused regression79 PASS; existing KAW Owner regression20 PASS. The
full14-file acceptance command reached326 PASS and one missing historical
OHI fixture failure in the sparse workspace. It does not silently skip this
real-evidence test or claim327 PASS. Exact-HEAD GitHub full-checkout CI must
resolve that test before merge readiness is declared. `regression.xml` records
the actual local result, including the missing-fixture failure.

Rollback is an ordinary Owner-approved revert of this Candidate-only change.
It requires no Runtime deployment, key rotation, coefficient rollback or
historical artifact/ledger rewrite. No independent Human Review is claimed.

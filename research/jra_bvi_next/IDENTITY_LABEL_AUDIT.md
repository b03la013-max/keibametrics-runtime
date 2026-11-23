# JRA BVI scientific identity / direct-result audit

This is an offline research audit, not Production admission or Forward OOS.
It reuses GitHub artifact `12581734087` from Run `40150266311`, job
`121040164487`. Its retrieved ZIP SHA256 is
`3e74abc81353f40fb0d21cdc6d67253419b7842ac52a31657f51a69fe3d79bfc`.
No JRA fetch, new attestation, token decoding, alias merging, model update,
KRS, Dispatch, deployment, or paid service is used.

The inherited qualification is explicitly at **2026-10-24 09:00 JST**.
Its acquisition times must not be relabelled as evidence available at a
historical race date, and the later audit execution time is not a race freeze.
The auditor checks original file hashes and rebinds the retained identity/run
proofs through the existing verifier. It recomputes qualification clocks and
counts rather than trusting a stored PASS boolean.

Three distinct quantities remain separate:

1. Opaque official profile/result navigation observations.
2. Exact composite horse identities and exact direct-result context matches.
3. Independently established permanent registry IDs and training admission.

An official profile CNAME is not a permanent horse or ancestry ID. An opaque
result CNAME is not decoded into a canonical race ID. Direct result context
comes from the verified SOURCE race context and is checked again against the
original result page's date, venue, and race-number heading. Horse name,
race name, surface, distance, field size and finish must all match. Exact
profile-navigation matches are reported separately; a namesake is never
silently merged into an official registry identity.

`permanent_id_and_independent_race_training_eligible` stays zero while
permanent horse identity is unresolved. The observed separate result tables
can provide an additional falsifiable label check, but neither their presence
nor a hash match establishes pre-event opponent strength or causal bloodline
effects.

Run (using already downloaded exact inputs):

```sh
python research/jra_bvi_next/identity_label_audit.py \
  --root /path/to/keibametrics-runtime \
  --recovery /path/to/identity_recovery.json \
  --qualification /path/to/identity_recovery_oidc.json \
  --output /path/to/new_audit.json
python -m pytest -q research/jra_bvi_next/test_identity_label_audit.py
```

The output path must not already exist. Original source, corpus, qualification,
and fixed model files are never rewritten.

The retained actual audit `identity_label_audit_20261025.json` was generated
with implementation commit `c6a4f315`, whose source SHA is recorded inside the
report. A subsequent lookup-only change imports the existing canonical
ten-venue registry, including `KKR` for 小倉. All venues observed in this actual
audit have identical mappings in both versions; no result is relabelled.

`identity_label_times.py` derives a second report from these exact matched
labels, taking the latest required acquisition or independent verification
clock. The race's historical label date is never used as its acquisition time.

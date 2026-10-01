# Prediction Owner pre-race input firewall — R4

Verdict: PARTIALLY IMPLEMENTED / NOT MERGE-READY / LIVE ACCEPTANCE PENDING.

This is an actual Candidate request-path correction, not real Owner execution,
Production-equivalence, or full lifecycle acceptance. It continues the branch
created from main `c30d593c1183bcefde614cfe999b55ebcda937ef` and the C1/R2/R3 fixes.

## Executable changes

`runtime/openai_prediction_owner_candidate.py` no longer sends the complete
Current Authority manifest to the Responses API. An explicit normative field
projection excludes Acceptance evidence, dynamic trackers, LOCAL MEC research
PFS and unrelated family operational state. A missing authority effective time
or an authority effective after the Prediction cutoff holds before API execution.
The actual R08 cutoff rejects current R36; R35 is the historical input authority.

The signed SOURCE is retained unchanged and fully hash-bound in lineage. API
input contains its original receipt, receipt SHA, snapshot SHA, full-envelope
SHA and an explicitly unsigned factual artifact projection. It is never
misrepresented as a newly signed SOURCE. Third-party public shadow evidence
is excluded. Official runner universe, factual auxiliary/current-state evidence,
missingness and honest NOT_READY numerical status remain available. Earlier
official same-day races already present in the frozen pre-cutoff SOURCE remain
permitted current-state evidence; the target Race outcome remains forbidden.

Both projections are digest-bound. The input contract version is
`KM-OPENAI-OWNER-PRE-RACE-INPUT-v2`. `formal_execution_orchestrator.py` rejects
reuse of a Candidate checkpoint from an older input contract. It does not
alter or register a Production Prediction Owner. Candidate model behavior and
Production-equivalence remain unproven; the new input contract cannot be
silently declared equivalent to the previous Candidate input.

## Validation

- Owner/orchestration/lifecycle focused suite: 149 passed.
- Existing selected regression suite plus R4: 257 passed, 2 explicit network
  controls skipped locally. The prior real downstream network controls remain
  covered by remote canary; their latest-head result must be checked after push.
- Real immutable FNB R08 SOURCE + R35 authority are used directly in the input
  projection regression. No source, historical intent or signed artifact is edited.
- Tests retain the ten active runners, legal earlier R07 current-state evidence,
  receipt/snapshot/full-source references and NOT_READY. They exclude actual
  research/acceptance sections and reject cutoff-late R36.
- Synthetic transport tests verify exclusion before request dispatch. They are
  not real API Prediction, real pre-race KRS E2E, or unknown-future acceptance.
- All 183 protected files and nine Phase B.2 frozen definitions remain unchanged.

## Unresolved dependencies

No OpenAI API/Admin key or GitHub secret-administration token is available in
the execution environment. The available encrypted key connector cannot select
a Service Account owner or least-privilege scopes, and no approved direct secret
transfer into the actual Candidate runtime is callable. No key was created,
printed, stored in files/artifacts, hashed, or committed. User authorization is
already sufficient; the missing dependency is capability/credentials.

Library FNB v2.0 (300916 bytes; original manifest SHA
`6fac5a6344c2e6afa85352cdb80f8fb4922f5ef6bfdb4577f31eb06cb69267da`)
was located. It explicitly omits inherited articles 1–51. v1.4 also starts from
article 52. Their historical results/PFS are not an original Prediction-generation
prompt. Complete generating process/prompt/model provenance for R07/R08/R12 is
still missing; A/B/C remains unresolved, not guessed from Git authorship.

Therefore a faithful Production Owner cannot be registered on this evidence.
Real API equivalence, real pre-race E2E, real two-race isolation, all eight
pre-race stage latency measurements and genuine future acceptance are NOT RUN.
R3 downstream recovery success does not fill those gaps. Factual prewarm,
cross-runtime concurrent dedup and durable result watch beyond the current
workflow window remain incomplete. No main merge, deploy, promotion, purchase
or OOS count increment is performed. Human review/merge/deploy remains a
required later step before the requested unknown-future acceptance.

The inherited A–T C1 report, Owner Reality Audit, R2 report and R3 report retain
the complete required deliverable/evidence matrix. This supplement narrows the
R4 change and its limits; it does not upgrade any previous verdict.

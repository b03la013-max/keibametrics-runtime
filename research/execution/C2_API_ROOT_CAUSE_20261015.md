# C2 API root cause, 2026-10-15

Candidate only. Same pinned Project/model/Service Account and staging environment.
PR124 diagnostic baseline: 1033c818bf2451ccb9496ae017c7aea0c35ad13e.
Latest baseline recheck: run 37895628668, job 116161030222, 2026-10-14T23:31:02Z:
OPENAI_API_429_CREDIT_BALANCE_EXHAUSTED_HOLD. Artifact 11935769337.
Provider-side credit exhaustion is confirmed; this is not a transient network failure.
No blind retry, credential rotation, alternate model/provider, billing action or promotion.
Owner must replenish API billing credit for the configured Project's organization,
then check Project/model permission and limits and rerun this staging preflight.
ChatGPT subscription is not evidence that this API account has usable credit.
A successful pinned-model response is still required to prove authentication.
Secret presence and provisioning metadata passed the prior guard; no key read/display/hash.
R07/R08/R12 comparison, real two-race isolation and Signed Shadow receipt remain BLOCKED.

Minimal diagnostic repair: separate HTTP401/403 and wrapped DNS/TLS/Timeout by type.
Store wall-clock authentication/API/validation/freeze durations without provider bodies,
headers or exception messages. API duration includes provider generation; independent
provider generation duration stays null because the response supplies no such metric.
Failed preflight records only its stage and duration; later phases remain null.
Production, prompt, model, policy, mathematical formulas, Engine and OOS untouched.
Local focused regression: 101 PASS. Existing429 test needed a dummy credential fixture;
it previously stopped before reaching the mocked HTTP boundary in a clean environment.

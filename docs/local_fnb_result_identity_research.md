# Saved official result-row identity recovery

`runtime.local_historical_identity_observations.extract_result_row_identities`
accepts an existing NAR `RaceMarkTable` snapshot and a timezone-aware research
`as_of`. It verifies the original bytes, requested/final URL identity, and
printed date/venue/race header. It recovers horse, jockey and trainer IDs only
from the corresponding cell's official link. Both observed official result
layouts (with and without a corner column) are supported.

The return value is private, unadopted research observations. It does not
provide Provider permission, SOURCE admission, a comparison population, or
any numerical score. Future/source-at-cutoff data fail closed. A no-result
page has an explicit terminal. Non-numeric finish states remain non-numeric.

The raw record retains `trainer_id` as an official trainer-license identity.
LOCAL Articles14/17 use trainer/stable performance as the judgement unit; a
research caller may document an identity-preserving alias to its `stable_id`
field for that unit. This is not evidence of a separate stable organization,
and such an additional organization identifier is not a new eligibility gate.
Production source and evidence mappings are unchanged by this extractor.

Date-only result history is not an exact event timestamp. The extractor does
not invent `event_at`, parent IDs, a field-size denominator, or a normalized
class from the race name. A future research rule must independently establish
its source qualification, declared comparison frame and remaining inputs.

Actual rows and extraction receipts belong in private storage. Public tests
contain only synthetic correctness fixtures.

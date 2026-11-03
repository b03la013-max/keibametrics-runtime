# FNB multi-provider private frontend — v0.1, 2026-11-03

This is a research integration interface, not an enabled Provider or an adopted
numerical/Owner policy. Current Production SOURCE, Consumer, signer, Runtime,
URLs and deployment remain unchanged.

`runtime.local_fnb_multisource.acquire` requires a separately admitted private
`ProviderBinding`: exact observed URLs, actor, permission evidence, validity,
private retention/cloud scope, pinned transport identity, real fetch callback
and source-specific parser. No invented provider HTML/CSV parser is included.
The callback is the existing approved origin/rate/robots transport; it must
return original HTTPS GET response bytes and its policy receipt. Search
snippets and browser DOM do not satisfy this interface. Capture is checked
against a fresh post-fetch clock, not request-start time.

Field output preserves Provider authority, URL, original SHA, capture/effective
time, Race identity, missing values and a separate rule-consumer decision.
Permission to fetch is not permission to consume a numerical Rule. Without a
separate exact `consumer_verifier`, every parsed field stays Tier 3. Vendor
`external_*` indices always stay Tier 3 regardless of the permission record or
rule name. No packet emitted here claims signed official Admission, Active
verification, Owner authority or registered OOS.

`acquire_available` tries each distinct Provider/URL once. An unavailable
binding or failed policy is a visible HOLD and does not prevent a separately
qualified Provider from being checked. It does not choose another origin to
circumvent the failed origin, silently retry or infer permission from public
availability.

`import_user_reference` reads the exact uploaded JSON bytes under their expected
SHA and unchanged reference classification. In the supplied FNB2R material,
NANKAN's 14-digit `program` URL is a day program, not proof of Race 2. The
Rakuten zero-filled RACEID is an unresolved alias. Neither suffix is parsed into
an authoritative Race ID. The reference JSON's Race identity is retained only
as a reference claim; provider_raw_sha is null.

`reconcile` joins only the claimed Venue/date/Race, reports field conflicts and
per-runner reference/supplemental/missing coverage. It never majority-votes,
resolves a current official value, marks an Active universe verified, or merges
same-named horses into permanent identities. Actual Provider parsers and the
existing official admission/verifier must independently check header/date/
post/distance/surface/horse number and provider permanent IDs before use.

`r20_source_frontend` is a callable for the existing
`FNB_PRODUCERS.py -> get_producers()['source']` interface. It requires an actual
qualified official producer and its independent source-admission verifier.
Absent either, it raises `MULTISOURCE_FORMAL_PRODUCER_NOT_CONNECTED`. The
verifier must bind its PASS to the exact official source artifact SHA.
Supplemental receipts are stored separately and never rewrite the official
SOURCE, so existing R13/R20 raw reparse, prestart, Owner qualification, KRS and
model-independence gates remain in force. This module cannot make NANKAN,
Rakuten, SPAIA or reference data into a NAR card or issue a signature.

Activation requires the real per-provider permission/actor/transport/parser and
current Consumer records. No such records are generated or adopted by this
change. Rollback: stop calling this optional frontend; retain immutable private
receipts and existing R20 source binding. No resources, keys, original
predictions or Production policies need deletion or rewriting.

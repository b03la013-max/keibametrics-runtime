# Single-Race private FNB research Runtime

This entry persists the executed R3 research chain as reusable repository code.
It accepts any one explicitly identified FNB Race; it contains no archived Race
list, private data, absolute workspace paths, credential, signer, or deployment.
It is separate from the Formal and R20 two-Owner six-method paths.

Run the existing LOCAL entry with an explicit private descriptor:

```sh
python -m runtime.local_race_entry --research-intent /private/FNB_research_intent.json
```

The descriptor is JSON data, never executable code. Paths are resolved relative
to the descriptor directory, or can be absolute. Supply actual SHA256 values:

```json
{
  "profile": "KM-FNB-PRIVATE-RESEARCH-INTENT-v1",
  "source_path": "source_receipt_envelope.json",
  "source_sha256": "<actual original file SHA256>",
  "request_path": "race_intent.json",
  "request_sha256": "<actual original file SHA256>",
  "trust_path": "pinned_public_receipt_trust.json",
  "trust_sha256": "<actual trust file SHA256>",
  "private_root": "research_outputs",
  "krs_cache": "previous_execution",
  "krs_cache_receipt_sha256": "<actual context_receipt.json SHA256>"
}
```

The request is the existing complete LOCAL Race Intent. Its Race ID, date,
number, post, cutoff, Active universe and signed official Raw must agree.
The existing signed NAR HTML admission and original Raw replay are preserved.
The supplied trust file must contain the public Ed25519 key, signer key ID,
and the canonical Engine/LOCAL map hashes. Verifying a signature against this
explicitly supplied, pinned trust does **not** establish a Provider licence,
adopt the trust globally, or authorize a model/consumer.

The current signed-HTML research entry does not disguise a CSV as HTML. A CSV
research candidate has its own independent admission/qualification boundaries;
it must supply the required historical position evidence before this Context
model can run. Missing evidence remains a Terminal, not invented history.

The entry calls the existing R13 numerical materializer, SOURCE observation
compiler, HSV research bridge and fixed Context-Pareto model. It binds each
original and per-field bridge provenance to the current numerical output.
No coefficient, score, Static role width or KRS physics is copied or changed.
The fixed Context model remains unadopted.

The canonical Engine hash is
`9929df994aa7964173edef9af7e9a705628ce377babf22df3af4e280fc275421`;
the LOCAL map hash is
`d8c027ee5bcc8fd3d2c248e8059b341776be38910e833d7589f09ab817c161f5`.
For a new technical execution instead of cache reuse, remove the two cache
fields and supply `engine` and `params` paths. Their actual bytes must match
these pins. Every new invocation uses 5,000 runs and seed 1. The process has a
bounded timeout and remains a private research diagnostic.

For reuse, the original cache directory contains `context_input.json`,
`context_output.json` and `context_receipt.json`. The receipt itself is pinned
by the descriptor; input/output bytes, canonical versions, seed, run count,
Active universe and calibration status are checked. Every object consumed by
the pinned Engine (`race`, `environment`, `horses`, `simulation`) must be exactly
equal. RNG identity, Role metadata, horse ordering, uncertainty and numerical
arrays are not normalized away. Only external top-level tracing metadata can
differ. The original execution input/output/receipt bytes and their SHA values
are copied unchanged; the new requested input has its own separate SHA.
A cache hit performs **zero** new KRS executions and is never a new LIVE success.

The original strict Common MEC is always attempted and saved independently.
A HOLD stays a HOLD and is not changed into computed zero/NO-BET. An optional
new selection hypothesis must be selected explicitly in the descriptor:

```json
"paper_policy": "pair-local-known"
```

or the separately identified, stronger candidate:

```json
"paper_policy": "unknown-path-protection"
```

These are NEW unadopted research policies, not existing canon or Production
adoptions. Their selection coverage cannot remove the original strict HOLD,
resolve missing empirical evidence, create an independent B/C Owner, or claim
complete FINAL. Each generated method is an independent paper alternative.
The existing Common MEC, Capital policy and canonical tree renderer are reused.

The equivalent direct entry is:

```sh
python -m runtime.local_fnb_research_runtime --help
```

All results go outside git, under a Race ID and recipe hash. Source/request
bytes, source/run clocks, code pins, numerical values, Context, full Active
Role/Pair/Third inventory, KRS originals, strict MEC, optional separate paper
result and complete private Markdown are retained. Existing originals are
immutable. A completed recipe is reused only after its identity, input recipe,
no-authority/no-FINAL flags and every recorded artifact byte hash are checked.
It does not overwrite prior receipts after downstream binding.

The entry neither acquires Provider data nor signs, adopts, merges, deploys,
schedules, sends a message, registers OOS, settles a purchase, or buys a ticket.
Those independently authorized live operations require their actual actors.
Research arithmetic, cache reuse and private rendering do not satisfy them.

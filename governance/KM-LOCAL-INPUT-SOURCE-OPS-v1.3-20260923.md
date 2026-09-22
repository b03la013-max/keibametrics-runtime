# LOCAL Input / Source Operations v1.3

Profile: `KM-LOCAL-INPUT-SOURCE-OPS-v1.3-20260923`
Predecessor: `KM-LOCAL-INPUT-SOURCE-OPS-v1.2-20260923`
Status: ACTIVE / LOCAL-WIDE / NON-NUMERICAL / EXTERNAL-SOURCE-ACQUISITION / SIGNED-SOURCE-FREEZE / FAIL-CLOSED

## Priority

official race facts at cutoff
> Family Current Authority
> LOCAL common canon
> current Venue Canon
> verified race evidence
> auxiliary sources.

## Formal Source Route

```text
REQUIRED_SOURCE_MANIFEST
→ EXTERNAL_SOURCE_ACQUISITION
→ RAW_SOURCE_SNAPSHOT
→ SOURCE_VALIDATION
→ NORMALIZED_EVIDENCE
→ SOURCE_FREEZE
→ SIGNED_SOURCE_RECEIPT
```

Runtime: `KM-LOCAL-PHYSICAL-RUNTIME-v1.5-20260923-SOURCE-ACQUISITION`
Source Authority: `KM-FAMILY-EXTERNAL-SOURCE-ACQUISITION-20260923-R1`

## Required Invariants

- Raw source bodyと解析済みEvidenceを分離する。
- URL、authority、priority、official/unofficial、fetched_at、cutoff relation、current/stale、raw SHA256、snapshot SHA256を可能な範囲で保持する。
- Required SourceのPOST_CUTOFFをFORMAL-PRE-RACEへ遡及混入しない。
- 同Priority Conflictを推測で解消しない。
- Missing evidenceを精密値で補完しない。
- User-supplied sourceはSource Classとcutoff relationを失わない。
- Runtime outputをrace evidenceと混同しない。
- File/Runtime/Engineの存在を実行証明としない。
- Execution proof priorityは Verified Signed Receipt > Runtime Response > Internal Ledger > ChatGPT self-declaration。
- JRA/BAN numerical mapping/source adapterをLOCALへ無言流用しない。

## Security

HTTPS only、allowlisted host、redirect再検査、private/loopback address拒否、response size上限、timeout、content-type制限をProduction Source FetchのHard Gateとする。

## Acceptance

GitHub Actions unit run `35764984192` PASS。
Live runtime run `35765520464` PASS。
NAR official HTTPS Raw SnapshotからSOURCE Receiptを生成し、署名検証後、PRE_KRS→KRS 5,000→FINAL→FORMALまでE2E PASS済み。

SOURCE Receipt：`43519df9d65fb42cdba7a4f32200771a941a50444e6d6ec47da76de3b0aa7bed`
Source Snapshot：`d18c20f13be8f45fadbd5678f7584d697a2725f1bbc2fa239432c857f8f6805e`

実在Race全Lifecycle Acceptanceは別GateとしてPENDING。

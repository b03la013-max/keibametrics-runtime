# KeibaMetrics Family External Source Acquisition R1

制定日：2026-09-23  
Profile：`KM-FAMILY-EXTERNAL-SOURCE-ACQUISITION-20260923-R1`  
Status：ACTIVE / FAMILY-WIDE / PRODUCTION-EXECUTION-OVERLAY / NON-NUMERICAL / FAIL-CLOSED / SOURCE-PROVENANCE-HARDENING

## 0. 目的

本機構は予測モデルを変更しない。正式Predictionで使用する情報を、外部Executionにより取得・時刻固定・原文保存・正規化・衝突監査・署名し、Prediction入力のSource Provenanceを機械的に証明する。

最上位経路を次へ拡張する。

```text
CANON_RESOLVE
→ REQUIRED_SOURCE_MANIFEST
→ EXTERNAL_SOURCE_ACQUISITION
→ RAW_SOURCE_SNAPSHOT
→ SOURCE_VALIDATION
→ NORMALIZED_EVIDENCE
→ SOURCE_FREEZE
→ SIGNED_SOURCE_RECEIPT
→ FULL_RUNNER_UNIVERSE
→ EVIDENCE_FEATURE_LEDGER
→ NUMERICAL_MATERIALIZATION
→ STATIC_FREEZE
→ PRE_KRS
→ KRS
→ MEC
→ CAPITAL
→ FINAL
→ RESULT
→ PREQUENTIAL_LEARNING
```

## 1. Authority

- Source Acquisitionは競馬能力の評価権限を持たない。
- Raw Sourceを「強い／弱い」「プラス／マイナス」へ解釈しない。
- Venue固有の意味解釈はVenue Prediction Knowledgeへ返す。
- Evidence→Index変換は各Familyの現行Evidence Rule / Numerical Authorityが所有する。
- KRS、MEC、Capital、Ticket AuthorityをSource Acquisitionへ移さない。
- Production numeric formula、weight、KRS Engine、parameter_map、Probability / EV / Kelly authorityは変更しない。

## 2. Required Source Manifest

各Formal Raceは、収集開始前にRequired Source Manifestを持つ。

最低フィールド：

- race_id
- prediction_cutoff
- source_id
- source_class
- authority
- authority_priority
- official / unofficial
- required
- canonical URL
- extraction rule（必要時）
- freshness rule（必要時）

Required Source Manifestなしの任意Web探索をFormal Source Acquisitionとみなさない。

## 3. Source Classes

現行Registryを継承し、少なくとも次を対象とする。

- OFFICIAL_RACE_CARD
- SCRATCH_EXCLUSION_JOCKEY_CHANGE
- ODDS
- BODY_WEIGHT
- TRAINING
- TRAINER_COMMENTS
- EQUIPMENT_RIDER_CHANGES
- HISTORICAL_RACE_DATA
- SAME_VENUE_DISTANCE
- DIRECT_MATCHUP
- TRACK_CONDITION
- WEATHER
- SAME_DAY_RACE_EVIDENCE
- VENUE_SPECIFIC_SOURCE
- USER_SUPPLIED_RACE_DATA

外部取得不能・契約認証が必要なSourceは取得済みと偽装しない。

## 4. Raw Snapshot

取得したSourceは解析済み値だけを保存してはならない。可能な範囲で次を保存する。

- requested URL
- final URL
- HTTP status
- content type
- ETag
- Last-Modified
- fetched_at
- prediction cutoff relation
- raw byte count
- raw SHA256
- compressed raw body
- parser / extraction output
- snapshot SHA256

`Parsed Value != Raw Source` をInvariantとする。

## 5. Temporal Integrity

Prediction Cutoff後に取得したRequired SourceをFORMAL-PRE-RACEへ遡及混入しない。

状態：

- PRE_CUTOFF
- POST_CUTOFF
- UNKNOWN

Required SourceがPOST_CUTOFFならFail-Closedする。

## 6. Conflict Resolution

同一Evidence Fieldについて複数Sourceが競合する場合：

1. authority priorityを比較する。
2. 上位Authorityを採用する場合もConflictを保存する。
3. 同Priorityで値が異なる場合はUNRESOLVEDとし、Required EvidenceならFail-Closedする。
4. ChatGPTの推測で競合を埋めない。

## 7. Security Boundary

External Fetchは以下をHard Gateとする。

- HTTPS only
- explicit allowed host
- username/password embedded URL禁止
- DNS解決後のprivate / loopback / link-local / reserved address拒否
- redirect先も再検査
- response size上限
- content type制限
- timeout
- arbitrary Authorization header禁止
- Runtime secretをSourceへ転送しない

Source AcquisitionをSSRF又は汎用Proxyとして使用しない。

## 8. Signed SOURCE Receipt

SOURCE phaseを既存Signed Receipt lifecycleへ追加する。

```text
SOURCE
→ PRE_KRS
→ KRS_RUN
→ FINAL
→ RESULT
```

SOURCE Receiptは最低限：

- source profile
- race_id
- prediction_cutoff
- source_freeze_at
- required_source_manifest_sha256
- raw_source_bundle_sha256
- normalized_evidence_sha256
- source_snapshot_sha256
- missing_required_sources
- stale_sources
- post_cutoff_sources
- conflicts
- formal_ready

を保持する。

`ChatGPT Self Declaration != Source Execution Proof`

## 9. Formal Gate

LOCAL Physical Runtime v1.5以降は、Formal PRE_KRSの前にVerified SOURCE Receiptを要求する。

以下のいずれかでFail-Closedする。

- SOURCE_RECEIPT_REQUIRED
- SOURCE_RECEIPT_SIGNATURE_INVALID
- SOURCE_RECEIPT_PHASE_INVALID
- SOURCE_RECEIPT_NOT_FROZEN
- SOURCE_RECEIPT_RACE_ID_MISMATCH
- SOURCE_ARTIFACT_INVALID
- MISSING_REQUIRED_SOURCES
- REQUIRED_EXTRACTION_INCOMPLETE
- SOURCE_CONFLICT_UNRESOLVED
- SOURCE_POST_CUTOFF

## 10. Storage and Reproducibility

RuntimeはRaw Source bodyをgzip+base64でSource Artifactに保持し、raw SHA256とSnapshot SHA256で改変検知する。
永続Object Storeを将来追加しても、Receiptにはcontent hashを残し、保存先だけを信頼根拠にしない。

## 11. Initial Activation Scope

初期Production ActivationはLOCALから行う。

第一優先Source：

1. official race card / runner universe
2. scratch / exclusion / jockey change / track condition
3. body weight
4. official same-day result / passing order

次段階でodds、historical race data、direct matchup、training、trainer commentsを追加する。

JRA/BANへはFamily-specific Source Adapter / Authority / Acceptanceを確認してから展開し、LOCAL adapterを無断流用しない。

## 12. Acceptance

Production Activationには最低限：

- unit integrity tests PASS
- external HTTPS fetch PASS
- raw hash round-trip PASS
- SOURCE Receipt signature verify PASS
- POST_CUTOFF negative test PASS
- unresolved equal-priority conflict negative test PASS
- PRE_KRS source receipt hard gate PASS
- existing KRS / MEC / FINAL / RESULT regression non-breakage確認

を要求する。

## 13. Final Principle

目的は検索量を増やすことではない。

```text
Predictionに使用した事実を
いつ
どこから
何として取得し
どのRaw Sourceから
どのEvidenceへ変換し
発走前のどのCutoffでFreezeしたか
を外部実行で再現・証明する。
```

Source AcquisitionはPrediction Accuracyの前提条件を改善するExecution機構であり、Prediction Modelそのものではない。

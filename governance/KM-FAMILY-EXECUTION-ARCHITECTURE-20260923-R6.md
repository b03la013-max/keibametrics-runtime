# ケイバメトリクスFamily 実行Architecture正式統合改定 R6

制定日：2026-09-23
Profile：KM-FAMILY-EXECUTION-ARCHITECTURE-20260923-R6
Predecessor：KM-FAMILY-EXECUTION-ARCHITECTURE-20260921-R5
Status：ACTIVE / FAMILY-WIDE / PRODUCTION-EXECUTION-OVERLAY / NON-NUMERICAL / EXTERNAL-SOURCE-ACQUISITION / CLOSED-LOOP-HARDENING / FAIL-CLOSED

## 0. 中心命題

未知未来Predictionに用いる事実を、取得前のRequired Source Manifestから、Raw Source、Evidence、数値計算、KRS、Ticket、Capital、Result、Learningまで一貫したlineageで保持する。

本R6はPrediction Model、既存指数式、固定係数、KRS Engine、parameter_map、Probability / EV / Kelly Authorityを変更しない。

## 1. 正式順序

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
→ EVIDENCE_FEATURE_COMPILER
→ REQUIRED_INDEX_MANIFEST
→ ACTUAL_NUMERICAL_TERMINALIZATION
→ INDEX_PROVENANCE
→ STATIC_FREEZE
→ PRE_KRS
→ KRS
→ KRS_UTILITY_CAPTURE
→ FINAL_ROLE/PAIR/THIRD
→ PRECOMPRESSION_SEMANTIC_UNIVERSE
→ MEC-R3
→ CAPITAL_POLICY
→ TICKET_TRANSPORT_TRACE
→ FINAL_FREEZE
→ SIGNED_FINAL
→ SIGNED_RESULT
→ AUTO_POSTRESULT_REVIEW
→ LEARNING_STATE_N+1
→ KRS_OOS_R30_GATE
```

SOURCE ReceiptがRequiredなFamily/Routeでは、Verified SOURCE ReceiptなしにPRE_KRSへ進まない。

## 2. Source Authority

Source Acquisition Authority：
`KM-FAMILY-EXTERNAL-SOURCE-ACQUISITION-20260923-R1`

Source Acquisitionは事実の取得・保存・整合・時刻・Provenanceを所有するが、馬能力評価を所有しない。

```text
RAW SOURCE
!=
EVIDENCE INTERPRETATION
!=
INDEX
!=
PREDICTION
```

Venue固有意味解釈はVenue Canon、Evidence→IndexはFamily Numerical Authority、KRS/MEC/Capitalはそれぞれ既存Authorityへ返す。

## 3. Temporal / Fail-Closed

Required Sourceについて以下を区別する。

- PRE_CUTOFF
- POST_CUTOFF
- UNKNOWN
- STALE
- MISSING
- CONFLICT_UNRESOLVED

POST_CUTOFF、Required Missing、Required Extraction Incomplete、同Priority unresolved conflict、署名不正はFORMAL-PRE-RACEをFail-Closedする。

## 4. Execution Evidence Priority

`Verified Signed Receipt > External Runtime Response > Internal Ledger > ChatGPT Self Declaration`

File、規程、Engine、Runtimeの存在だけでExecution PASSを主張しない。

## 5. LOCAL Activation

LOCALは `KM-LOCAL-PHYSICAL-RUNTIME-v1.5-20260923-SOURCE-ACQUISITION` でSource AcquisitionをProduction Execution Overlayへ接続済み。

Acceptance：
- Unit run 35764984192: PASS
- Live Source-to-Formal run 35765520464: PASS
- NAR official HTTPS fetch: PASS
- Raw snapshot/hash round-trip: PASS
- Tamper detection: PASS
- POST_CUTOFF negative test: PASS
- Missing SOURCE Receipt PRE_KRS hard block: PASS
- KRS actual_run_count: 5000

これはSource Acquisition機構のProduction Acceptanceであり、実在Raceの発走前PredictionからRESULTまでの最初のReal-Race Empirical Acceptanceとは区別する。後者はPENDINGを維持する。

## 6. JRA / BAN Boundary

R6はFamily-wide Architectureだが、LOCALのSource Adapter/Authority/AcceptanceをJRA又はBANへ自動流用しない。
各FamilyでSource Authority、URL/Host policy、Parser、Cutoff、Runtime Receipt acceptanceを解決してからACTIVE化する。

## 7. 最終原則

情報を集めたと自己申告するのではなく、

`Required Source → Raw Snapshot → Hash → Normalized Evidence → Source Freeze → Signed Receipt`

を外部実行で証明してからPredictionへ進む。

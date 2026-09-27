# ケイバメトリクスFamily 実行Architecture正式統合改定 R7

制定日：2026-09-28  
Profile：KM-FAMILY-EXECUTION-ARCHITECTURE-20260928-R7  
Predecessor：KM-FAMILY-EXECUTION-ARCHITECTURE-20260923-R6  
Status：ACTIVE / FAMILY-WIDE / PRODUCTION-EXECUTION-OVERLAY / NON-NUMERICAL / SCOPE-OWNERSHIP-FIREWALL / SIGNED-FORMAL-LIFECYCLE / MATURITY-PROMOTION-GOVERNANCE / FAIL-CLOSED

## 0. 継承

R6のRequired Source→Raw Source→Evidence→Numerical→KRS→Ticket→Capital→Result→Learning lineage、Temporal Fail-Closed、Verified Receipt優先を全面継承する。

R7はPrediction Model、指数式、Weight、KRS Engine physics、parameter_map、MEC-R3、Capital Policy、Venue Production Canonを変更しない。

## 1. 新しい上位正本

- Scope Ownership：`KM-FAMILY-SCOPE-OWNERSHIP-CONTRACT-20260928-R1`
- Formal Lifecycle：`KM-FAMILY-FORMAL-LIFECYCLE-CONTRACT-20260928-R1`
- Cross-Family Maturity Promotion：`KM-FAMILY-CROSS-FAMILY-MATURITY-PROMOTION-20260928-R1`
- Runtime Guard：`runtime/family_authority_guard.py`

## 2. 正式順序

```text
CANON_RESOLVE
→ SCOPE_OWNERSHIP_RESOLVE
→ REQUIRED_SOURCE_MANIFEST
→ EXTERNAL_SOURCE_ACQUISITION
→ RAW_SOURCE_SNAPSHOT
→ SOURCE_VALIDATION
→ NORMALIZED_EVIDENCE
→ SOURCE_FREEZE
→ SIGNED_SOURCE_RECEIPT
→ FULL_RUNNER_UNIVERSE
→ EVIDENCE_FEATURE_LEDGER
→ REQUIRED_INDEX_MANIFEST
→ ACTUAL_NUMERICAL_MATERIALIZATION
→ INDEX_PROVENANCE
→ VENUE_PREDICTION_CONTEXT
→ STATIC_PREDICTION_FREEZE
→ PRE_KRS
→ KRS_EXECUTE
→ KRS_UTILITY_CAPTURE
→ FINAL_ROLE_PAIR_THIRD
→ PRECOMPRESSION_SEMANTIC_UNIVERSE
→ MEC
→ CAPITAL_POLICY
→ CANONICAL_TICKET
→ FINAL_FREEZE
→ SIGNED_FINAL
→ SIGNED_RESULT
→ SETTLEMENT
→ PREDICTION_UTILITY_MEASUREMENT
→ PFS_MEASUREMENT
→ FIRST_MATERIAL_FAILURE_LOCALIZATION
→ LEARNING_STATE_N_PLUS_1
→ OOS_PROMOTION_TRACKER_UPDATE
```

## 3. Scope Ownership Hard Gate

Formal execution前にAuthority Guardを実行する。

Guardは最低限、
- Current Authorityの最新解決
- Family IDの解決
- Scope Ownership profileの整合
- 他Family parameter/adapter/mapping流用
- Common reserved scopeのFamily/Venueによる再所有
- Candidate/ShadowのProduction numerical authority混入
- BAN physical runtime block
を検査する。

## 4. Venue/Common分離

Venueは「その競馬場で何が起こりやすいか」を所有する。Ticket、Capital、Runtime、Receipt、Settlement、PFS、Family-wide Learning transportを独自Production Authorityとして持たない。

旧Venue条項のCommon責務はCompatibility Source又はRegression Fixtureとして保持してよいがCurrent Authorityを重複させない。

## 5. Family Isolation

JRA、LOCAL、BANはSource Adapter、Evidence Rule Registry、Numerical Mapping、Numerical Materializer、KRS Input Adapter、parameter_mapを共有しない。

Schema/Interface/Receipt/Temporal/Measurement/Test HarnessはCommon化可能。

## 6. Formal-Full

TerminalizedとNumerically Calculatedを分離する。FULL_REQUIREDではRequired Index Cellが全てCALCULATEDでなければFORMAL-FULLを名乗らない。

Verified Signed Receipt > External Runtime Response > Immutable Ledger > Internal Log > Self Declaration。

## 7. Prediction Utility

R30のPrediction Utility Firstを継承する。Formal PASSはPrediction Successではない。KRS ExecutedはKRS Usefulではない。Candidate executableはProduction readyではない。

Result後はFirst Material FailureをOwnerへ返し、下流補正で上流欠陥を隠さない。

## 8. Promotion

Cross-Family成熟知見はPromotion Class C0～C3で審査する。C2/C3はFrozen Unknown OOSと明示Promotionが必須。自動昇格は禁止する。

## 9. 最終原則

**Family共通化は責務を一本化するために行い、数値・Source実装・Venue知識を均質化するためには行わない。**

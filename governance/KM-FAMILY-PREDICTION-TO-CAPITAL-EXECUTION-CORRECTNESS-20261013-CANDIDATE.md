# KM-FAMILY-PREDICTION-TO-CAPITAL-EXECUTION-CORRECTNESS-20261013-CANDIDATE

Status: CANDIDATE / NON-PRODUCTION / NO-AUTO-PROMOTION / PRODUCTION-FROZEN
基準日：2026-10-13。現行Family Authority R51、main7353e18a。新Authority/Revisionは制定しない。

## 統合差分と適用境界

既存のScope Ownership、Formal Lifecycle、MEC-R3、R43 Owner PFSを継承し、下記の実装伝播だけを候補化する。Core Principlesは変更しない。

- Family Commonの既存Conversion Diagnosticsへ明示opt-in Capital測定を接続。Head/Pair/Third/券種/tier Exposure、Material Pair非選択、第三世界、Core Density、UNKNOWN Roleを記録する。既存Materiality関数を再利用し、新Selector・資金配分関数・閾値を追加しない。全Material Pair購入は要求しない。Trioには順序Headを架空付与しない。
- 同一凍結AKI券面を測定するだけであり、予測Weight、KRS Physics、MEC-R3、Capital Policy、AKI列幅は保持する。Pair除外理由がない場合はNOT_RECORDED_PER_PAIR、市場価格がない場合はCore Recoverability HOLD。勝率・EV・Kellyはnull。
- 非有限値・boolはPFS/Promotionの数値証拠にしない。これは既存Gateの入力Correctness修復であり、Promotion閾値変更ではない。
- 歴史Regressionが変化するlive aggregateを参照して破綻しないよう、当時の正確なGit blobを凍結snapshotとして読ませる。Blob hash・行検証は維持。現行17戦台帳を7戦へ巻き戻さず、旧7戦Expected Outputを変更しない。
- PFS測定のVenue分類に既存LOCAL場KCH/KNZ/MIZ/HIMを補完。予測知識・Source Authorityを輸入する意味はない。
- SOURCE開始前Deadline失敗の保存修復はPR263に既存実装がある。共通修復であるが二重実装しない。PR257のSOURCE-first/Checkpoint/Receipt/Git conflictを継承。PR263受入・配備前に修復済み運用とは主張しない。

## Owner整合と非適用

Core：観測/推論/欠測、結果前Freeze、反証、No-Bet、未知未来検証は維持。
Family Common：Money/Receipt/Lifecycle/失敗分類/測定/審査のみ共通化。
Family-specific：LOCAL29指数/63Rules、JRAOwner、BANSource/Physics/指数はFamily固有。LOCAL AKI PR262をJRA/BANへ輸入しない。
Venue-specific：川崎900/1400/1600/2000mのStageとUNKNOWN条件変換はPR263の責務。
Current-State/Multi-World/Stage/Path/Semantic Graphは経験的仮説の地位を維持し、今回の損益から必須原理へ昇格しない。

## 実証範囲

元17戦の署名FINAL/RESULT34件は現行正本Runtime /verifyで全件valid。8戦・17戦の集計を既存trackerと独立Robustness測定で確認。実購入証跡なし、FROZEN-RECOMMENDATION/Shadow PAPERを分離。改定Armの真正Forward OOS0。
KAW13日8戦：Production55.79%、元AKI114.31%。17戦：Production53.55%、元AKI60.11%、AKI収支−7,100円。AKI最大DD9,200円、上位3払戻除外PFS18.86%。相対優位は絶対収益の証明でない。
Static-only購入Armが凍結されていないためStatic-only PFSはN/A。KRS支持/競合は既存Incremental Utilityを保持、別確率へ変換しない。価格不足、等予算/等点数、No-Bet比較、BAN/JRAの実レース受入はPENDING。

## 次回Unknown・Promotion

改定Armは測定専用。Code SHA、同SOURCE/Static/入力、生成時刻、凍結券面/Stake、Signed FINAL traceの診断hash、RESULT bindingを結果前に固定する。過去17戦へ新方式OOS creditを追加しない。
正式Prediction行動を変更するArmが必要なら、既存Selectorへの候補差分として別定義し結果前Freezeする。全6点等の固定Portfolioは作らない。
R43既存条件：30適格Forward以上、3日以上、Candidate PFS>100かつProduction超、raw/equal-budget DD悪化なし、equal-ticket利益悪化なし、Set保持、Hit-but-Loss悪化なし、最大1戦払戻比≤0.5、最大払戻戦除外利益>0、Integrity HOLD0、全必須値完備。満たしてもHuman Reviewへ進むだけで自動Promotionしない。Family固有Authorityと別の正式要件があれば最新正本優先。
結果前正式FINAL未成立はPFS N/A、Execution failureはNo-Betや予測Lossへ変換しない。Learningは既存KEEP/REPAIR_NOW/TEST_NEXT/SIMPLIFY_OR_REJECT等を使い、新Rule自動追加しない。

---
# 継承正本（以下の各原文は制定当時の履歴、Current Authorityを優先）


## 継承元 governance/KM-FAMILY-EXECUTION-ARCHITECTURE-20260928-R8.md

# ケイバメトリクスFamily 実行Architecture正式統合改定 R8

制定日：2026-09-28  
Profile：`KM-FAMILY-EXECUTION-ARCHITECTURE-20260928-R8`  
Predecessor：`KM-FAMILY-EXECUTION-ARCHITECTURE-20260928-R7`

## 0. 継承

R7のScope Ownership、Formal Lifecycle、Current Authority Guard、Family Isolation、Prediction Utility、Promotion Governanceを全面継承する。

**R8はFormal Stageを削除しない。**

R8が変更するのはWall-clock execution architectureのみである。

## 1. Race-Day Fast Path

`KM-FAMILY-RACE-DAY-FAST-PATH-20260928-R1` をProduction Execution Optimizationとして接続する。

初期対象はLOCAL、優先VenueはFNBとする。

```text
Full Formal Intelligence
+ Precompute
+ Exact Content Cache
+ Runner Parallelism
+ Delta Invalidation
+ Next-3 Prewarm
+ Fast Reflection
= Same Required Output / Shorter Wall Clock
```

## 2. Formal Lifecycle

R7のexecution_sequenceを完全維持する。

Precomputeされた値はFormal Stageそのものの完了を意味しない。Formal時点でCurrent Authority、Signed Source、Runner Universe、Current State、dependency SHA、implementation SHAを再確認した後にだけ再利用できる。

## 3. Cache

CacheはAuthorityではない。

`stage + exact dependency SHA256 + implementation SHA256 + profile` が一致する場合のみ利用できる。

不一致、破損、例外はすべてMISSとしてcanonical Full Pathへ戻す。

## 4. Parallelism

Runner単位等、依存関係が独立した純粋計算のみ並列化できる。

Temporal Stage、Signed Receipt verification、KRS handoff、MEC、Capital、FINALの依存順序は並列化を理由に逆転させない。

## 5. Prewarm

既に作成済みの同日未来requestについてn+1～n+3を先行計算できる。

未来requestを推測・捏造しない。

当日結果、取消、馬体重、Official Going等によりdependencyが変化した場合、該当cacheは自動失効する。

## 6. Reflection

Verified RESULT直後にFast Reflectionを生成する。

Fast ReflectionはPFS、W/P2/P3、Pair/Set/Exact、KRS分類、First Material Failure、Next Learning Stateを即時返す。

深いCandidate/OOS/Canon研究はCritical Path外へ送る。

## 7. SLO

- FINAL target：300秒
- Hard SLO：420秒
- Purchase reserve target：600秒
- Fast Reflection target：120秒

SLOは品質Gateより下位である。SLO達成のためにGateを省略してはならない。

## 8. Full/Fast Equivalence

同一入力についてFastとFullでPrediction/Selection/Execution behaviorが一致しなければFast PathをProduction利用しない。

Receipt timestamp、workflow id等の非行動差は同値性対象外とする。

## 9. Freeze

Prediction Model、指数式、Weight、KRS physics、parameter_map、MEC-R3、Capital Policy、FNB v2.1 Prediction Knowledgeは変更しない。


## 継承元 profiles/family_formal_lifecycle_contract_20260928_R1.json

{
  "profile_id": "KM-FAMILY-FORMAL-LIFECYCLE-CONTRACT-20260928-R1",
  "status": "ACTIVE / FAMILY-WIDE / FORMAL-PRE-RACE / FAIL-CLOSED / SIGNED-LIFECYCLE / NON-NUMERICAL",
  "effective_at": "2026-09-28T00:33:00+09:00",
  "predecessor": "KM-FAMILY-EXECUTION-ARCHITECTURE-20260923-R6 lifecycle semantics",
  "purpose": "Define the minimum complete Family-wide Formal lifecycle while leaving source adapters, numerical mappings and venue predictive knowledge to their owning scopes.",
  "temporal_invariant": "CANON_RESOLVE <= SCOPE_OWNERSHIP_RESOLVE <= RACE_IDENTITY_RESOLVE <= PREDICTION_CUTOFF_FREEZE; SOURCE_START <= SOURCE_FREEZE <= PREDICTION_CUTOFF_FREEZE <= STATIC_PREDICTION_FREEZE <= PRE_KRS < FINAL_FREEZE < SCHEDULED_POST; FINAL_BEFORE_POST_VERIFY requires SIGNED_FINAL timestamp < scheduled_post_at",
  "execution_evidence_priority": [
    "VERIFIED_SIGNED_RECEIPT",
    "EXTERNAL_RUNTIME_RESPONSE",
    "IMMUTABLE_LEDGER",
    "INTERNAL_LOG",
    "SELF_DECLARATION"
  ],
  "stages": [
    {
      "stage_id": "CANON_RESOLVE",
      "owner_class": "COMMON_FAMILY",
      "pre_race_required": true,
      "signed_receipt_required": false
    },
    {
      "stage_id": "SCOPE_OWNERSHIP_RESOLVE",
      "owner_class": "COMMON_FAMILY",
      "pre_race_required": true,
      "signed_receipt_required": false
    },
    {
      "stage_id": "RACE_IDENTITY_RESOLVE",
      "owner_class": "COMMON_FAMILY",
      "pre_race_required": true,
      "signed_receipt_required": false
    },
    {
      "stage_id": "PREDICTION_CUTOFF_FREEZE",
      "owner_class": "COMMON_FAMILY",
      "pre_race_required": true,
      "signed_receipt_required": false
    },
    {
      "stage_id": "REQUIRED_SOURCE_MANIFEST",
      "owner_class": "FAMILY_SPECIFIC",
      "pre_race_required": true,
      "signed_receipt_required": false
    },
    {
      "stage_id": "EXTERNAL_SOURCE_ACQUISITION",
      "owner_class": "FAMILY_SPECIFIC",
      "pre_race_required": true,
      "signed_receipt_required": false
    },
    {
      "stage_id": "RAW_SOURCE_SNAPSHOT",
      "owner_class": "FAMILY_SPECIFIC",
      "pre_race_required": true,
      "signed_receipt_required": false
    },
    {
      "stage_id": "SOURCE_VALIDATION",
      "owner_class": "FAMILY_SPECIFIC",
      "pre_race_required": true,
      "signed_receipt_required": false
    },
    {
      "stage_id": "NORMALIZED_EVIDENCE",
      "owner_class": "FAMILY_SPECIFIC",
      "pre_race_required": true,
      "signed_receipt_required": false
    },
    {
      "stage_id": "SOURCE_FREEZE",
      "owner_class": "FAMILY_SPECIFIC",
      "pre_race_required": true,
      "signed_receipt_required": false
    },
    {
      "stage_id": "SIGNED_SOURCE_RECEIPT",
      "owner_class": "COMMON_FAMILY",
      "pre_race_required": true,
      "signed_receipt_required": true
    },
    {
      "stage_id": "FULL_RUNNER_UNIVERSE",
      "owner_class": "COMMON_FAMILY",
      "pre_race_required": true,
      "signed_receipt_required": false
    },
    {
      "stage_id": "EVIDENCE_FEATURE_COMPILATION",
      "owner_class": "FAMILY_SPECIFIC",
      "pre_race_required": true,
      "signed_receipt_required": false
    },
    {
      "stage_id": "EVIDENCE_FEATURE_LEDGER",
      "owner_class": "FAMILY_SPECIFIC",
      "pre_race_required": true,
      "signed_receipt_required": false
    },
    {
      "stage_id": "REQUIRED_INDEX_MANIFEST",
      "owner_class": "COMMON_FAMILY",
      "pre_race_required": true,
      "signed_receipt_required": false
    },
    {
      "stage_id": "ACTUAL_NUMERICAL_MATERIALIZATION",
      "owner_class": "FAMILY_SPECIFIC",
      "pre_race_required": true,
      "signed_receipt_required": false
    },
    {
      "stage_id": "INDEX_PROVENANCE",
      "owner_class": "COMMON_FAMILY",
      "pre_race_required": true,
      "signed_receipt_required": false
    },
    {
      "stage_id": "VENUE_PREDICTION_CONTEXT",
      "owner_class": "VENUE_SPECIFIC",
      "pre_race_required": true,
      "signed_receipt_required": false
    },
    {
      "stage_id": "STATIC_PREDICTION_FREEZE",
      "owner_class": "FAMILY_SPECIFIC",
      "pre_race_required": true,
      "signed_receipt_required": false
    },
    {
      "stage_id": "PRE_KRS",
      "owner_class": "COMMON_FAMILY",
      "pre_race_required": true,
      "signed_receipt_required": true
    },
    {
      "stage_id": "KRS_EXECUTE",
      "owner_class": "COMMON_FAMILY",
      "pre_race_required": true,
      "signed_receipt_required": true
    },
    {
      "stage_id": "KRS_RECEIPT_VERIFY",
      "owner_class": "COMMON_FAMILY",
      "pre_race_required": true,
      "signed_receipt_required": true
    },
    {
      "stage_id": "KRS_UTILITY_CAPTURE",
      "owner_class": "COMMON_FAMILY",
      "pre_race_required": true,
      "signed_receipt_required": false
    },
    {
      "stage_id": "FINAL_ROLE_PAIR_THIRD",
      "owner_class": "COMMON_FAMILY",
      "pre_race_required": true,
      "signed_receipt_required": false
    },
    {
      "stage_id": "PRECOMPRESSION_SEMANTIC_UNIVERSE",
      "owner_class": "COMMON_FAMILY",
      "pre_race_required": true,
      "signed_receipt_required": false
    },
    {
      "stage_id": "MEC",
      "owner_class": "COMMON_FAMILY",
      "pre_race_required": true,
      "signed_receipt_required": false
    },
    {
      "stage_id": "TICKET_CONSTRUCTION",
      "owner_class": "COMMON_FAMILY",
      "pre_race_required": true,
      "signed_receipt_required": false
    },
    {
      "stage_id": "CAPITAL_POLICY",
      "owner_class": "COMMON_FAMILY",
      "pre_race_required": true,
      "signed_receipt_required": false
    },
    {
      "stage_id": "CANONICAL_TICKET",
      "owner_class": "COMMON_FAMILY",
      "pre_race_required": true,
      "signed_receipt_required": false
    },
    {
      "stage_id": "MANDATORY_STAGE_MANIFEST_VERIFY",
      "owner_class": "COMMON_FAMILY",
      "pre_race_required": true,
      "signed_receipt_required": false
    },
    {
      "stage_id": "FINAL_FREEZE",
      "owner_class": "COMMON_FAMILY",
      "pre_race_required": true,
      "signed_receipt_required": false
    },
    {
      "stage_id": "SIGNED_FINAL",
      "owner_class": "COMMON_FAMILY",
      "pre_race_required": true,
      "signed_receipt_required": true
    },
    {
      "stage_id": "FINAL_BEFORE_POST_VERIFY",
      "owner_class": "COMMON_FAMILY",
      "pre_race_required": true,
      "signed_receipt_required": true
    },
    {
      "stage_id": "SIGNED_RESULT",
      "owner_class": "COMMON_FAMILY",
      "pre_race_required": false,
      "signed_receipt_required": true
    },
    {
      "stage_id": "SETTLEMENT",
      "owner_class": "COMMON_FAMILY",
      "pre_race_required": false,
      "signed_receipt_required": false
    },
    {
      "stage_id": "PREDICTION_UTILITY_MEASUREMENT",
      "owner_class": "COMMON_FAMILY",
      "pre_race_required": false,
      "signed_receipt_required": false
    },
    {
      "stage_id": "PFS_MEASUREMENT",
      "owner_class": "COMMON_FAMILY",
      "pre_race_required": false,
      "signed_receipt_required": false
    },
    {
      "stage_id": "FIRST_MATERIAL_FAILURE_LOCALIZATION",
      "owner_class": "COMMON_FAMILY",
      "pre_race_required": false,
      "signed_receipt_required": false
    },
    {
      "stage_id": "LEARNING_STATE_N_PLUS_1",
      "owner_class": "COMMON_FAMILY",
      "pre_race_required": false,
      "signed_receipt_required": false
    },
    {
      "stage_id": "OOS_PROMOTION_TRACKER_UPDATE",
      "owner_class": "COMMON_FAMILY",
      "pre_race_required": false,
      "signed_receipt_required": false
    }
  ],
  "formal_full_conditions": {
    "runner_universe_complete": true,
    "required_index_manifest_terminalized": true,
    "full_required_numeric_mode": "ALL REQUIRED CELLS CALCULATED; HOLD/UNRESOLVED cannot claim FORMAL-FULL",
    "index_provenance_complete": true,
    "static_frozen_pre_result": true,
    "pre_krs_receipt_verified": true,
    "krs_actual_run_count_truthful": true,
    "semantic_universe_frozen_before_mec": true,
    "canonical_ticket_frozen_pre_result": true,
    "final_receipt_verified": true,
    "post_start_retroactive_promotion_forbidden": true,
    "krs_receipt_verified": true,
    "mandatory_stage_manifest_verified": true,
    "final_before_post_verified": true,
    "ticket_construction_complete": true,
    "race_identity_resolved": true,
    "prediction_cutoff_frozen": true
  },
  "hard_distinctions": [
    "TERMINALIZED != NUMERICALLY_CALCULATED",
    "KRS_EXECUTED != KRS_USEFUL",
    "FORMAL_PASS != PREDICTION_SUCCESS",
    "PREDICTION_SUCCESS != CAPITAL_SUCCESS",
    "CANDIDATE_EXECUTABLE != PRODUCTION_AUTHORIZED",
    "HISTORICAL_ACCEPTANCE != UNKNOWN_OOS"
  ],
  "result_learning": {
    "rule": "Race_n immutable FINAL + official Result -> review/settlement -> Learning State_n+1",
    "rewrite_race_n": false,
    "result_derived_pre_race_feature_forbidden": true
  },
  "production_freeze": {
    "predictive_numeric_change": "NONE",
    "krs_engine_physics_change": "NONE",
    "mec_r3_change": "NONE",
    "capital_policy_change": "NONE"
  }
}


## 継承元 profiles/family_scope_ownership_20260928_R1.json

{
  "profile_id": "KM-FAMILY-SCOPE-OWNERSHIP-CONTRACT-20260928-R1",
  "status": "ACTIVE / FAMILY-WIDE / PRODUCTION-AUTHORITY-BOUNDARY / NON-NUMERICAL / FAIL-CLOSED / NO-DUAL-PRODUCTION-OWNER",
  "effective_at": "2026-09-28T00:33:00+09:00",
  "predecessor": null,
  "purpose": "Define one authoritative owner class for each Production responsibility, preserve family/venue predictive specialization, and prevent duplicated or cross-family Production authority.",
  "families": [
    "JRA",
    "LOCAL",
    "BAN"
  ],
  "owner_classes": [
    "COMMON_FAMILY",
    "FAMILY_SPECIFIC",
    "VENUE_SPECIFIC",
    "CANDIDATE_SHADOW"
  ],
  "precedence": [
    "CURRENT_AUTHORITY_RESOLUTION",
    "COMMON_FAMILY_CONTRACT",
    "FAMILY_SPECIFIC_IMPLEMENTATION",
    "VENUE_SPECIFIC_PREDICTION_KNOWLEDGE",
    "CANDIDATE_SHADOW_NON_PRODUCTION"
  ],
  "scopes": {
    "CURRENT_AUTHORITY_RESOLUTION": {
      "owner": "COMMON_FAMILY",
      "production_authority": true,
      "portability": "FAMILY_WIDE"
    },
    "FORMAL_LIFECYCLE_CONTRACT": {
      "owner": "COMMON_FAMILY",
      "production_authority": true,
      "portability": "FAMILY_WIDE"
    },
    "RUNNER_UNIVERSE_PROTOCOL": {
      "owner": "COMMON_FAMILY",
      "production_authority": true,
      "portability": "FAMILY_WIDE_PROTOCOL"
    },
    "REQUIRED_INDEX_MANIFEST_PROTOCOL": {
      "owner": "COMMON_FAMILY",
      "production_authority": true,
      "portability": "FAMILY_WIDE_PROTOCOL"
    },
    "TEMPORAL_INTEGRITY": {
      "owner": "COMMON_FAMILY",
      "production_authority": true,
      "portability": "FAMILY_WIDE"
    },
    "RECEIPT_VERIFICATION": {
      "owner": "COMMON_FAMILY",
      "production_authority": true,
      "portability": "FAMILY_WIDE"
    },
    "KRS_EXECUTION_TRANSPORT": {
      "owner": "COMMON_FAMILY",
      "production_authority": true,
      "portability": "FAMILY_WIDE_PROTOCOL"
    },
    "PRECOMPRESSION_SEMANTIC_UNIVERSE": {
      "owner": "COMMON_FAMILY",
      "production_authority": true,
      "portability": "FAMILY_WIDE"
    },
    "MEC": {
      "owner": "COMMON_FAMILY",
      "production_authority": true,
      "portability": "FAMILY_WIDE"
    },
    "TICKET_CONSTRUCTION": {
      "owner": "COMMON_FAMILY",
      "production_authority": true,
      "portability": "FAMILY_WIDE"
    },
    "CAPITAL": {
      "owner": "COMMON_FAMILY",
      "production_authority": true,
      "portability": "FAMILY_WIDE"
    },
    "CANONICAL_TICKET_TRANSPORT": {
      "owner": "COMMON_FAMILY",
      "production_authority": true,
      "portability": "FAMILY_WIDE"
    },
    "SETTLEMENT": {
      "owner": "COMMON_FAMILY",
      "production_authority": true,
      "portability": "FAMILY_WIDE"
    },
    "PFS_MEASUREMENT": {
      "owner": "COMMON_FAMILY",
      "production_authority": true,
      "portability": "FAMILY_WIDE"
    },
    "FAILURE_LOCALIZATION": {
      "owner": "COMMON_FAMILY",
      "production_authority": true,
      "portability": "FAMILY_WIDE"
    },
    "PREQUENTIAL_LEARNING_TRANSPORT": {
      "owner": "COMMON_FAMILY",
      "production_authority": true,
      "portability": "FAMILY_WIDE"
    },
    "PROMOTION_GOVERNANCE": {
      "owner": "COMMON_FAMILY",
      "production_authority": true,
      "portability": "FAMILY_WIDE"
    },
    "SOURCE_ADAPTER": {
      "owner": "FAMILY_SPECIFIC",
      "production_authority": true,
      "portability": "FAMILY_ISOLATED"
    },
    "INFORMATION_SOURCE_REGISTRY": {
      "owner": "FAMILY_SPECIFIC",
      "production_authority": true,
      "portability": "FAMILY_ISOLATED"
    },
    "EVIDENCE_RULE_REGISTRY": {
      "owner": "FAMILY_SPECIFIC",
      "production_authority": true,
      "portability": "FAMILY_ISOLATED"
    },
    "NUMERICAL_MAPPING": {
      "owner": "FAMILY_SPECIFIC",
      "production_authority": true,
      "portability": "FAMILY_ISOLATED"
    },
    "NUMERICAL_MATERIALIZER": {
      "owner": "FAMILY_SPECIFIC",
      "production_authority": true,
      "portability": "FAMILY_ISOLATED"
    },
    "KRS_INPUT_ADAPTER": {
      "owner": "FAMILY_SPECIFIC",
      "production_authority": true,
      "portability": "FAMILY_ISOLATED"
    },
    "PARAMETER_MAP": {
      "owner": "FAMILY_SPECIFIC",
      "production_authority": true,
      "portability": "FAMILY_ISOLATED"
    },
    "FAMILY_PREDICTION_MODEL": {
      "owner": "FAMILY_SPECIFIC",
      "production_authority": true,
      "portability": "FAMILY_ISOLATED"
    },
    "COURSE_GEOMETRY": {
      "owner": "VENUE_SPECIFIC",
      "production_authority": true,
      "portability": "VENUE_ONLY"
    },
    "DISTANCE_INTERPRETATION": {
      "owner": "VENUE_SPECIFIC",
      "production_authority": true,
      "portability": "VENUE_ONLY"
    },
    "VENUE_TRACK_STATE": {
      "owner": "VENUE_SPECIFIC",
      "production_authority": true,
      "portability": "VENUE_ONLY"
    },
    "VENUE_POSITION_PROGRESS_FRICTION": {
      "owner": "VENUE_SPECIFIC",
      "production_authority": true,
      "portability": "VENUE_ONLY"
    },
    "VENUE_EVIDENCE_INTERPRETATION": {
      "owner": "VENUE_SPECIFIC",
      "production_authority": true,
      "portability": "VENUE_ONLY"
    },
    "VENUE_REGRESSION_FIXTURE": {
      "owner": "VENUE_SPECIFIC",
      "production_authority": true,
      "portability": "VENUE_ONLY"
    },
    "EXPERIMENTAL_NUMERICS": {
      "owner": "CANDIDATE_SHADOW",
      "production_authority": false,
      "portability": "NON_PRODUCTION"
    },
    "EXPERIMENTAL_PARAMETER_MAP": {
      "owner": "CANDIDATE_SHADOW",
      "production_authority": false,
      "portability": "NON_PRODUCTION"
    },
    "EXPERIMENTAL_KRS_UTILITY": {
      "owner": "CANDIDATE_SHADOW",
      "production_authority": false,
      "portability": "NON_PRODUCTION"
    },
    "EXPERIMENTAL_MEC": {
      "owner": "CANDIDATE_SHADOW",
      "production_authority": false,
      "portability": "NON_PRODUCTION"
    },
    "UNPROMOTED_VENUE_HYPOTHESIS": {
      "owner": "CANDIDATE_SHADOW",
      "production_authority": false,
      "portability": "NON_PRODUCTION"
    },
    "RACE_IDENTITY_PROTOCOL": {
      "owner": "COMMON_FAMILY",
      "production_authority": true,
      "portability": "FAMILY_WIDE"
    },
    "PREDICTION_CUTOFF_PROTOCOL": {
      "owner": "COMMON_FAMILY",
      "production_authority": true,
      "portability": "FAMILY_WIDE"
    },
    "EVIDENCE_FEATURE_PROTOCOL": {
      "owner": "COMMON_FAMILY",
      "production_authority": true,
      "portability": "FAMILY_WIDE_PROTOCOL"
    },
    "INDEX_PROVENANCE_PROTOCOL": {
      "owner": "COMMON_FAMILY",
      "production_authority": true,
      "portability": "FAMILY_WIDE_PROTOCOL"
    },
    "ACTUAL_NUMERICAL_CALCULATION_PROTOCOL": {
      "owner": "COMMON_FAMILY",
      "production_authority": true,
      "portability": "FAMILY_WIDE_PROTOCOL"
    },
    "STATIC_FREEZE_PROTOCOL": {
      "owner": "COMMON_FAMILY",
      "production_authority": true,
      "portability": "FAMILY_WIDE"
    },
    "KRS_RECEIPT_VERIFICATION": {
      "owner": "COMMON_FAMILY",
      "production_authority": true,
      "portability": "FAMILY_WIDE"
    },
    "ROLE_PAIR_THIRD_DECISION": {
      "owner": "COMMON_FAMILY",
      "production_authority": true,
      "portability": "FAMILY_WIDE"
    },
    "MANDATORY_STAGE_MANIFEST": {
      "owner": "COMMON_FAMILY",
      "production_authority": true,
      "portability": "FAMILY_WIDE"
    },
    "FINAL_FREEZE_PROTOCOL": {
      "owner": "COMMON_FAMILY",
      "production_authority": true,
      "portability": "FAMILY_WIDE"
    },
    "FINAL_BEFORE_POST_VERIFICATION": {
      "owner": "COMMON_FAMILY",
      "production_authority": true,
      "portability": "FAMILY_WIDE"
    },
    "EVIDENCE_FEATURE_COMPILER": {
      "owner": "FAMILY_SPECIFIC",
      "production_authority": true,
      "portability": "FAMILY_ISOLATED"
    },
    "INDEX_PROVENANCE_BUILDER": {
      "owner": "FAMILY_SPECIFIC",
      "production_authority": true,
      "portability": "FAMILY_ISOLATED"
    }
  },
  "common_reserved_scopes": [
    "CURRENT_AUTHORITY_RESOLUTION",
    "FORMAL_LIFECYCLE_CONTRACT",
    "RUNNER_UNIVERSE_PROTOCOL",
    "REQUIRED_INDEX_MANIFEST_PROTOCOL",
    "TEMPORAL_INTEGRITY",
    "RECEIPT_VERIFICATION",
    "KRS_EXECUTION_TRANSPORT",
    "PRECOMPRESSION_SEMANTIC_UNIVERSE",
    "MEC",
    "TICKET_CONSTRUCTION",
    "CAPITAL",
    "CANONICAL_TICKET_TRANSPORT",
    "SETTLEMENT",
    "PFS_MEASUREMENT",
    "FAILURE_LOCALIZATION",
    "PREQUENTIAL_LEARNING_TRANSPORT",
    "PROMOTION_GOVERNANCE",
    "RACE_IDENTITY_PROTOCOL",
    "PREDICTION_CUTOFF_PROTOCOL",
    "EVIDENCE_FEATURE_PROTOCOL",
    "INDEX_PROVENANCE_PROTOCOL",
    "ACTUAL_NUMERICAL_CALCULATION_PROTOCOL",
    "STATIC_FREEZE_PROTOCOL",
    "KRS_RECEIPT_VERIFICATION",
    "ROLE_PAIR_THIRD_DECISION",
    "MANDATORY_STAGE_MANIFEST",
    "FINAL_FREEZE_PROTOCOL",
    "FINAL_BEFORE_POST_VERIFICATION"
  ],
  "family_isolated_scopes": [
    "SOURCE_ADAPTER",
    "INFORMATION_SOURCE_REGISTRY",
    "EVIDENCE_RULE_REGISTRY",
    "NUMERICAL_MAPPING",
    "NUMERICAL_MATERIALIZER",
    "KRS_INPUT_ADAPTER",
    "PARAMETER_MAP",
    "FAMILY_PREDICTION_MODEL",
    "EVIDENCE_FEATURE_COMPILER",
    "INDEX_PROVENANCE_BUILDER"
  ],
  "venue_allowed_scopes": [
    "COURSE_GEOMETRY",
    "DISTANCE_INTERPRETATION",
    "VENUE_TRACK_STATE",
    "VENUE_POSITION_PROGRESS_FRICTION",
    "VENUE_EVIDENCE_INTERPRETATION",
    "VENUE_REGRESSION_FIXTURE"
  ],
  "cross_family_reuse": {
    "allowed": [
      "SCHEMA_SHAPE",
      "INTERFACE_CONTRACT",
      "RECEIPT_PROTOCOL",
      "TEMPORAL_PROTOCOL",
      "MEASUREMENT_DEFINITION",
      "FAILURE_CODE_PATTERN",
      "TEST_HARNESS_PATTERN"
    ],
    "prohibited": [
      "PARAMETER_MAP",
      "NUMERICAL_WEIGHTS",
      "FIXED_THRESHOLDS",
      "SOURCE_ADAPTER",
      "FAMILY_EVIDENCE_RULE_REGISTRY",
      "FAMILY_NUMERICAL_MAPPING",
      "KRS_INPUT_ADAPTER",
      "VENUE_FIXED_BONUS",
      "FAMILY_PREDICTION_COEFFICIENT"
    ],
    "rule": "Portable contract semantics may be promoted. Family/Venue numerical or source implementations may not be copied into another Family as Production authority."
  },
  "hard_rules": [
    "ONE_SCOPE_ONE_PRODUCTION_OWNER_CLASS",
    "COMMON_RESERVED_SCOPE_CANNOT_BE_RECLAIMED_BY_FAMILY_OR_VENUE",
    "FAMILY_ISOLATED_SCOPE_CANNOT_USE_ANOTHER_FAMILY_IMPLEMENTATION",
    "VENUE_CANON_CANNOT_OWN_COMMON_TICKET_CAPITAL_RUNTIME_MEASUREMENT",
    "CANDIDATE_SHADOW_HAS_NO_PRODUCTION_AUTHORITY",
    "HISTORICAL_COMPATIBILITY_SOURCE_DOES_NOT_CREATE_CURRENT_AUTHORITY"
  ],
  "production_freeze": {
    "predictive_numeric_change": "NONE",
    "krs_engine_physics_change": "NONE",
    "production_mec_change": "NONE",
    "capital_policy_change": "NONE",
    "venue_production_canon_change": "NONE"
  }
}


## 継承元 profiles/family_prediction_utility_contract_20260927_R1.json

{
  "profile_id": "KM-FAMILY-PREDICTION-UTILITY-CONTRACT-20260927-R1",
  "status": "ACTIVE / FAMILY-WIDE / PREDICTION-UTILITY-FIRST / MEASUREMENT-CONTRACT / NON-NUMERICAL / NO-AUTO-PROMOTION",
  "effective_at": "2026-09-27T18:00:00+09:00",
  "purpose": "Make unknown-future prediction utility the primary system objective while preserving Production numerical authority, immutable pre-result lineage, semantic continuity, executable conversion, capital discipline and robust long-run PFS measurement.",
  "system_objective_order": [
    "PREDICTION_UTILITY",
    "ORDER_ROLE_DISCRIMINATION",
    "KRS_INCREMENTAL_UTILITY",
    "SEMANTIC_PRESERVATION",
    "TICKET_CONVERSION_QUALITY",
    "CAPITAL_EFFICIENCY",
    "ROBUST_LONG_RUN_PFS",
    "EXECUTION_CONFORMANCE"
  ],
  "hard_distinctions": [
    "FORMAL_PASS != PREDICTION_SUCCESS",
    "PREDICTION_SUCCESS != CAPITAL_SUCCESS",
    "KRS_EXECUTED != KRS_USEFUL",
    "COVERAGE != DISCRIMINATION",
    "SOURCE_ACQUIRED != FEATURE_GENERATED",
    "FEATURE_GENERATED != PRODUCTION_AUTHORIZED",
    "CANDIDATE_EXECUTABLE != PRODUCTION_NUMERICAL_READY",
    "FROZEN_RECOMMENDATION_PFS != ACTUAL_PFS",
    "KNOWN_FIXTURE_IMPROVEMENT != UNKNOWN_OOS_IMPROVEMENT",
    "AUTHORITY_MANIFEST_SNAPSHOT != DYNAMIC_MEASUREMENT_STATE"
  ],
  "prediction_utility_chain": [
    "SOURCE",
    "SOURCE_FACT",
    "EVIDENCE_FEATURE",
    "BASE_INDEX_CONTRIBUTION",
    "BASE_DERIVED_INDEX",
    "STATIC_PREDICTION",
    "W_P2_P3_ROLE",
    "ORDERED_PAIR_THIRD",
    "KRS_INCREMENTAL_UTILITY",
    "PRE_COMPRESSION_SEMANTIC_UNIVERSE",
    "MEC",
    "TICKET",
    "CAPITAL",
    "PFS",
    "LEARNING_STATE_NEXT_RACE"
  ],
  "first_material_failure_owner_order": [
    "SOURCE_ACQUISITION",
    "SOURCE_TRUST_RECEIPT",
    "SOURCE_TO_FEATURE",
    "EVIDENCE_EVALUATOR",
    "NUMERICAL_MAPPING",
    "NUMERICAL_DISCRIMINATION",
    "STATIC_PREDICTION",
    "W_P2_P3",
    "ORDERED_PAIR",
    "PAIR_CONDITIONED_THIRD",
    "KRS",
    "SEMANTIC_COMPRESSION",
    "MEC",
    "TICKET_CONVERSION",
    "CAPITAL",
    "EXECUTION",
    "RESULT_LEARNING"
  ],
  "owner_routing_rules": {
    "SOURCE_ACQUISITION": "SOURCE / EXTERNAL EXECUTION / CORRECTNESS",
    "SOURCE_TO_FEATURE": "COMMON EVIDENCE / EVALUATOR",
    "NUMERICAL_MAPPING": "COMMON NUMERICAL",
    "STATIC_PREDICTION": "COMMON OR VENUE-SPECIFIC PREDICTION BY MECHANISM",
    "W_P2_P3": "COMMON PREDICTION / ORDER-ROLE unless a replicated venue mechanism is demonstrated",
    "ORDERED_PAIR": "COMMON ORDER / HEAD-LOCAL P2 unless venue-specific evidence is demonstrated",
    "PAIR_CONDITIONED_THIRD": "COMMON THIRD / PRE-COMPRESSION SEMANTICS unless venue-specific evidence is demonstrated",
    "KRS": "COMMON KRS",
    "SEMANTIC_COMPRESSION": "COMMON PRE-COMPRESSION SEMANTICS",
    "MEC": "COMMON MEC",
    "TICKET_CONVERSION": "COMMON TICKET CONSTRUCTION",
    "CAPITAL": "COMMON CAPITAL",
    "EXECUTION": "COMMON RUNTIME / RECEIPT / TEMPORAL INTEGRITY",
    "RESULT_LEARNING": "COMMON CLOSED LOOP",
    "VENUE_CANON": "Only pre-result-identifiable, venue-specific, reusable mechanisms with Frozen Unknown OOS support"
  },
  "required_trace_contract": {
    "source_feature_trace_schema": "KM-JRA-SOURCE-FEATURE-INDEX-TRACE-v1.0-20260927",
    "source_index_static_trace_schema": "KM-JRA-SOURCE-FEATURE-INDEX-STATIC-TRACE-v1.0-20260927",
    "source_feature_requirements": [
      "SOURCE_FACT_AVAILABILITY",
      "EVALUATOR_AVAILABILITY",
      "PRODUCTION_FEATURE_STATE",
      "MISSING_REASON",
      "RULE_ID",
      "CATEGORY",
      "EVIDENCE_REFS",
      "SOURCE_FACT",
      "TARGET_INDEX_BINDING"
    ],
    "index_requirements": [
      "FINAL_VALUE",
      "RULE_ID",
      "MAPPING_VERSION",
      "COVERAGE_WEIGHT",
      "COMPONENT_FEATURE",
      "COMPONENT_CATEGORY_SCORE",
      "WEIGHTED_CONTRIBUTION",
      "EVIDENCE_REFS",
      "SOURCE_FACT",
      "STATIC_RANK",
      "STATIC_ROLE"
    ],
    "missing_semantics": "MISSING != NEUTRAL != WEAK; no automatic neutral-50 synthesis"
  },
  "prediction_measurement": {
    "required": [
      "WINNER_RANK",
      "P2_RANK",
      "P3_RANK",
      "TOP3_MEAN_RANK",
      "W_CAPTURE_EFFICIENCY",
      "P2_CAPTURE_EFFICIENCY",
      "P3_CAPTURE_EFFICIENCY",
      "ORDERED_PAIR_CAPTURE",
      "ORDERED_EXACT_CAPTURE",
      "CANDIDATE_WIDTH",
      "MARKET_WINNER_RANK_GAIN",
      "MARKET_TOP3_MEAN_RANK_GAIN"
    ],
    "market_baseline": "Official pre-race popularity ranking when available; measurement only, never direct Production authority."
  },
  "krs_contract": {
    "role": "SECOND_OPINION_ENGINE",
    "production_authority": "SHADOW / NO DIRECT PRODUCTION CAPITAL AUTHORITY",
    "purpose": "Rescue material alternative futures omitted by frozen Static prediction without overwriting Static.",
    "required_post_result_metrics": [
      "UNIQUE_RESCUE",
      "UNIQUE_HARM",
      "WINNER_P2_P3_RANK_DELTA",
      "TOP3_MEAN_RANK_DELTA",
      "ROLE_RESCUE",
      "PAIR_RESCUE",
      "THIRD_RESCUE",
      "PROPOSAL_WIDTH",
      "RESCUE_DENSITY",
      "RESCUE_TO_TICKET_CONVERSION",
      "ADDED_CAPITAL_COST"
    ],
    "valid_no_change_states": [
      "LOW-DISCRIMINATION",
      "NO-MATERIAL-KRS-UPDATE"
    ],
    "auto_purchase": false,
    "auto_promotion": false
  },
  "mec_contract": {
    "production": "KM-FAMILY-MINIMUM-EFFICIENT-COVERAGE-20260921-R3",
    "production_objective": "Minimum capital subject to full pre-compression material semantic coverage.",
    "fixed_ticket_cap": null,
    "shadow": "KM-FAMILY-MEC-R4-SHADOW-CANDIDATE-20260922-R1",
    "shadow_arm_definitions_frozen": true,
    "shadow_arms": [
      "CORE_ONLY",
      "CORE_PROTECTION",
      "CPSS_ALL",
      "CPSS_TOP3",
      "CPSS_TOP4",
      "CPSS_TOP5",
      "CPSS_TOP6",
      "CPSS_TOP7",
      "CPSS_TOP8"
    ],
    "required_measurements": [
      "SEMANTIC_RETENTION",
      "CORE_RETENTION",
      "CORE_CAPITAL",
      "PROTECTION_CAPITAL",
      "TAIL_CAPITAL",
      "GENERIC_TAIL_CAPITAL_AVOIDED",
      "UNIQUE_TAIL_RESCUE",
      "FALSE_PROTECTION",
      "STAKE_DILUTION",
      "ROBUST_PFS",
      "DRAWDOWN",
      "LARGEST_WIN_DEPENDENCY"
    ],
    "production_rule_change": false
  },
  "pfs_contract": {
    "formula": "RETURN / INVESTMENT * 100",
    "separate_cohorts": [
      "PRODUCTION_FROZEN_RECOMMENDATION",
      "SOURCE_DERIVED_CANDIDATE_FROZEN_RECOMMENDATION",
      "SHADOW_COUNTERFACTUAL",
      "ACTUAL_PURCHASE"
    ],
    "actual_purchase_rule": "Actual PFS is NOT VERIFIED unless purchase evidence is verified.",
    "required_robustness": [
      "HEADLINE_PFS",
      "LARGEST_WIN_EXCLUDED_PFS",
      "TOP3_RETURNS_EXCLUDED_PFS",
      "MEDIAN_RACE_PFS",
      "HIT_BUT_LOSS",
      "MAX_DRAWDOWN",
      "MAX_LOSING_STREAK",
      "TIER_PFS",
      "BET_TYPE_PFS",
      "LARGEST_WIN_DEPENDENCY"
    ],
    "candidate_production_merge_forbidden": true
  },
  "learning_contract": {
    "rule": "Race_n Result -> Learning State_n+1",
    "immutable_pre_result_artifacts": true,
    "retroactive_prediction_rewrite_forbidden": true,
    "next_race_only": true,
    "venue_hypothesis_ttl_required": true,
    "delete_merge_simplify_replace_add_order": [
      "DELETE",
      "MERGE",
      "SIMPLIFY",
      "REPLACE",
      "ADD"
    ]
  },
  "promotion_contract": {
    "primary_evidence": "FROZEN_UNKNOWN_OOS",
    "known_fixture_role": "Correctness and mechanism verification only.",
    "race_count_threshold_not_sufficient": true,
    "explicit_promotion_declaration_required": true,
    "multi_axis_review": [
      "PREDICTION_RANK_AND_CAPTURE",
      "MARKET_BASELINE_GAIN",
      "KRS_RESCUE_HARM",
      "SEMANTIC_RETENTION",
      "TICKET_CONVERSION",
      "CAPITAL_DENSITY",
      "ROBUST_PFS",
      "EXECUTION_CONFORMANCE"
    ],
    "automatic_promotion": false
  },
  "production_freeze": {
    "numerical_change": "NONE",
    "prediction_behavior_change": "NONE",
    "unchanged": [
      "HPI_SSI_CFI_RFI_BVI_JTI_CSI_TRI_BWI_GCI_PRI_KGI_VMI_WEIGHTS",
      "DCR_TPI_ZAI_WIN_ZAI_PLACE_SRI_F3S_T3I_FORMULAS",
      "KRS_ENGINE_PHYSICS",
      "KRS_PARAMETER_MAP_PRODUCTION_AUTHORITY",
      "MEC_R3_PRODUCTION_RULE",
      "CAPITAL_POLICY",
      "FIXED_VENUE_BONUSES",
      "FIXED_TICKET_CAP",
      "AUTOMATIC_KRS_RESCUE_PURCHASE"
    ]
  },
  "dynamic_state_sources": {
    "source_candidate_oos": "runtime/source_candidate_oos_status.json",
    "krs_oos": "runtime/krs_oos_status.json",
    "mec_r4_oos": "runtime/mec_r4_oos_status.json",
    "pfs_grand_review": "runtime/pfs_grand_review/current.json",
    "hsn_venue_audit": "runtime/venue_audits/KM-JRA-HSN-20260927-REV7-CANON-AUDIT.json",
    "nky_venue_audit": "runtime/venue_audits/KM-JRA-NKY-20260927-REV7-CANON-AUDIT.json"
  },
  "enactment_snapshot": {
    "source_candidate_oos": "15/30",
    "krs_oos": "4/30",
    "mec_r4_oos": "3/30",
    "hsn_canon_revision_required": false,
    "nky_canon_revision_required": false
  },
  "production_effect": "NONE",
  "automatic_promotion": false
}


## 継承元 profiles/KM_FAMILY_MEC_PROFILE_20260921_R3.json

{
  "profile_id": "KM-FAMILY-MINIMUM-EFFICIENT-COVERAGE-20260921-R3",
  "predecessor": "KM-FAMILY-MINIMUM-EFFICIENT-COVERAGE-20260921-R2",
  "status": "ACTIVE",
  "authority": "FAMILY-WIDE-PRODUCTION-EXECUTION-OVERLAY",
  "numerical_effect": "NONE",
  "family_scope": [
    "JRA",
    "LOCAL",
    "BAN",
    "ALL_VENUES"
  ],
  "fixed_ticket_cap": null,
  "objective": "MINIMUM_REQUIRED_CAPITAL_FOR_100_PERCENT_PRECOMPRESSION_SEMANTIC_COVERAGE",
  "precompression_semantic_universe": true,
  "p3_tail_floor": {
    "applies_to": "GLOBAL_ACTIVE_P3 x MATERIAL_ORDERED_PAIR",
    "hard_exclusion_only_before_mec": true,
    "soft_exclusion_action": "TAIL_SET_PROTECTION",
    "preferred_bet_type": "TRIO",
    "exact_orientation_implied": false
  },
  "hard_exclusion_markers": [
    "STRUCTURAL",
    "NOT_APPLICABLE",
    "IMPOSSIBLE",
    "SCRATCH",
    "WITHDRAWN",
    "ROLE_INELIGIBLE",
    "UNIVERSE_MISMATCH",
    "FORMAL_OUT_OF_SCOPE"
  ],
  "soft_exclusion_examples": [
    "LOWER_PAIR_LOCAL_MATERIALITY",
    "BUDGET",
    "CAPITAL_LIMIT"
  ],
  "stop_buying": "NO_NEW_PRECOMPRESSION_MATERIAL_COVERAGE",
  "stop_compressing": "REMOVAL_BREAKS_PRECOMPRESSION_MATERIAL_COVERAGE",
  "no_legacy_width_fallback": true,
  "krs_shadow_capital_authority": false
}


## 継承元 governance/KM-FAMILY-MINIMUM-EFFICIENT-COVERAGE-20260921-R3.md

# ケイバメトリクスFamily Minimum Efficient Coverage Mandatory Overlay R3

制定日：2026-09-21
Profile：KM-FAMILY-MINIMUM-EFFICIENT-COVERAGE-20260921-R3
Predecessor：KM-FAMILY-MINIMUM-EFFICIENT-COVERAGE-20260921-R2
Status：ACTIVE / FAMILY-WIDE / PRODUCTION-EXECUTION-OVERLAY / NON-NUMERICAL / PRECOMPRESSION-SEMANTIC-COVERAGE / NO-FIXED-TICKET-CAP / FAIL-CLOSED

## 1. 中心修復
R2の「100% Material Coverage」を、Pair-local圧縮後のUniverseではなく、
Global W/P2/P3から始まるPre-Compression Semantic Universeに対して定義する。

## 2. P3 Tail Floor
Material Ordered Pair（PURCHASE又は非手続的PROTECT）に対し、Global P3 Active馬は、
hard structural exclusionがない限りMEC前に消してはならない。

Pair-local:
- PURCHASE -> CORE Exact Third
- PROTECT -> PROTECTION Set Third
- EXCLUDE + hard structural reason -> HARD EXCLUSION
- EXCLUDE + lower materiality/budget/soft reason -> TAIL Set Protection
- disposition missing -> synthesized TAIL Set Protection

TAILは原則TRIOで低資本保護し、Exact Orientationを自動主張しない。

## 3. Hard Exclusion
SCRATCH / WITHDRAWN / NOT_APPLICABLE / IMPOSSIBLE / ROLE_INELIGIBLE /
FORMAL_OUT_OF_SCOPE等の構造的理由のみMEC前の除外を許可する。

LOWER_PAIR_LOCAL_MATERIALITYはHard Exclusionではない。

## 4. 目的
min Capital subject to Pre-Compression Semantic Coverage = 100%.

R2の固定点数禁止、STOP BUYING、STOP COMPRESSING、Budget非削除原則を全面継承する。


## 継承元 governance/KM-FAMILY-OWNER-UTILITY-PFS-CONTINUOUS-IMPROVEMENT-20261007-R1.md

# KM-FAMILY-OWNER-UTILITY-PFS-CONTINUOUS-IMPROVEMENT-20261007-R1

- Status: ACTIVE / FAMILY-WIDE / GOVERNANCE-OVERLAY / NON-NUMERICAL / NON-PREDICTIVE / POSTRESULT-MEASUREMENT-ENFORCEMENT / NO-AUTO-PROMOTION
- Effective scope: JRA / LOCAL / BAN / all Venue entry points
- Production Prediction change: NONE
- Production Numerical change: NONE
- KRS physics / parameter_map change: NONE
- Production MEC / Capital policy change: NONE
- Venue Canon change: NONE
- Current Authority activation target: R43
- Predecessor authority: R40
- R41 / R42: existing open candidate lineages only; not inherited as Production by this overlay

## 0. 目的

KeibaMetricsの実用目的は、未知未来に対するPredictionを正しく行い、その情報をTicketとCapitalへ効率的に変換し、資本を持続させながらLong-run PFSを改善し続けることである。

PFS改善はOwner Utilityの中核であり、運用Capital、研究継続性、検証回数、外部AI/計算/開発環境への継続投資余力を支える。

ただしPFSは無制約最大化しない。

Long-run PFSは以下の制約下で改善する。

- pre-result integrity
- no result-fit
- unknown-future OOS generalization
- drawdown / capital sustainability
- prediction integrity
- semantic preservation
- execution correctness
- robustness / payout concentration
- opportunity cost
- human-reviewed promotion

## 1. No-Stagnation

Every Race Learns != Every Race Adds A Rule.

同時に、

Every Race Learns != Every Race Changes Nothing.

各Race / Day Reviewは、少なくとも次のどこかへLearningを送る。

- KEEP
- REPAIR_NOW
- TEST_NEXT
- SIMPLIFY_OR_REJECT
- PROMOTION_REVIEW
- DO_NOT_CHANGE

Productionを変更しない場合も、理由と次の反証可能なForward Testを残す。

## 2. 二軸Failure Localization

従来のFirst Material Failureを維持する。

加えて、PFS改善のためにDominant PFS Loss Ownerを独立評価する。

### First Material Failure
因果鎖で最初に壊れたLayer。

### Dominant PFS Loss Owner
最終的なCapital realizationを最も毀損したLayer。

候補Owner:

- SOURCE_EVIDENCE
- NUMERICAL
- PREDICTION_ROLE
- PAIR_EXACT_CONNECTION
- KRS
- SEMANTIC_MEC
- TICKET
- CAPITAL
- EXECUTION_RESULT
- NONE_REALIZED_PFS_POSITIVE
- UNKNOWN

First FailureとDominant PFS Loss Ownerは一致しなくてよい。

例:
Winner Roleで最初に失敗していても、広いProtection/Capital exposureが損失額を拡大した場合は、First Failure=PREDICTION_ROLE / Dominant PFS Loss Owner=CAPITALとなり得る。

自動Runtimeは証拠が不足する場合UNKNOWNを返し、原因を捏造しない。

## 3. SemanticとCapitalの分離

Family-wide原則:

- Semantic Universe != Purchased Universe
- UNKNOWN != WEAK
- UNKNOWN != MUST PURCHASE
- Budget Shortage != Semantic Compression
- Prediction confidence != mandatory capital exposure
- Set protection != automatic purchase
- KRS proposal != purchase authority

Semantic上必要な馬・Pair・Thirdを保存することと、その全てへCapitalを投入することを分離する。

## 4. PFS改善の主要Forward Tracks

既存Architectureへ吸収し、新規Architectureを乱造しない。

### A. Winner Role Migration
Lower-role retained / W absentの馬について、Venue Evidenceや独立KRS supportが重なる場合のみShadow W-REVIEW。

### B. Pair Residual
Active W × P2 CORE/PROTECTEDでMaterial Pairが欠落する場合、独立根拠が重なるPairのみPAIR-REVIEW。

### C. Pair-local Selective Exact
Material Pairに対してThirdの順序Materialityが独立して成立する場合のみExact-review。

### D. Race-conditional Capital Layer Selection
固定SET_ONLY / TOP-N / ConservativeへProductionを置換しない。
RaceごとにCORE / PAIR / EXACT / PROTECTIONのどのLayerへCapitalを置くべきかを結果前Shadowで比較する。

候補Evidence:
- core concentration
- winner uncertainty
- pair/exact reason sufficiency
- protection burden
- market-payout sufficiency
- KRS incremental support
- VERY_WIDE_REVIEW
- current-state uncertainty
- lower-role longshot mechanism

### E. KRS Incremental Utility
KRSを「実行したか」ではなく以下で測る。

- W Rescue
- Pair Rescue
- Third Rescue
- Unique Rescue
- False W Addition
- False Pair Addition
- False Exact Addition
- Rescue-to-Ticket Conversion
- Added Capital
- Net PFS contribution when measurement authority permits

KRS automatic promotionは禁止。

## 5. Owner Utility Scorecard

日次・cohort評価では、単一PFSのみでなく最低限以下を併記する。

- Frozen Recommendation PFS
- Actual Purchase PFS if verified
- Profit / Loss
- Drawdown
- Hit-but-Loss
- Capital Efficiency
- Prediction Utility
- Semantic Preservation
- Ticket Conversion
- Payout Concentration / Largest-win dependency
- Unknown-Future OOS count
- Candidate vs Production same-race comparison

Actual Purchase証明がなければActual PFSはUNKNOWN。

## 6. Learning Router

Post-result runtimeは各Raceについて:

1. First Material Failure
2. Dominant PFS Loss Owner
3. PFS status
4. Hit-but-Loss
5. Improvement Route

を出力する。

Production behavior changeは自動許可しない。

Correctness bugのみREPAIR_NOWへ送れる。

Prediction / KRS / MEC / Capital policy変更は原則TEST_NEXTへ送り、Forward OOSとHuman Review後にPROMOTION_REVIEWへ進める。

## 7. Promotion

Promotionは以下の順序を要求する。

Infrastructure / Measurement
→ Result-blind Shadow Freeze
→ Genuine Unknown-Future OOS
→ same-race Production comparison
→ robustness / drawdown / concentration check
→ Human Review
→ Explicit Authority Update

Automatic Promotionは禁止。

単Race、単日、Replay、Training、Synthetic AcceptanceはProduction promotion evidenceとして十分ではない。

## 8. Current Candidate境界

R41 / R42 / OHI v2.4等の既存Candidateは、それぞれのOOS / promotion contractを維持する。

本Overlayはそれらを自動的にProduction化しない。

R43はR40のProduction Prediction / Numerical / KRS / MEC-R3 / Capital / Venue Canonを維持したまま、Owner Utility / PFS Improvement / Post-result Learning GovernanceのみCurrent化する。

## 9. 最終原則

Production stabilityとcontinuous improvementを両立する。

- Productionは結果に合わせて毎Race変えない。
- Correctnessは止めずに直す。
- CandidateはProductionへ挑戦し続ける。
- Candidateが未知未来で再現的に優位ならPromotion Reviewへ送る。
- Evidenceが悪ければCandidateを捨てる。
- 同等なら簡素化する。

最終目標:

> 未知未来で、Prediction Integrityを守りながら、再現可能かつ資本持続可能なLong-run PFSを継続的に改善する。


## 継承元 profiles/family_maturity_promotion_20260928_R1.json

{
  "profile_id": "KM-FAMILY-CROSS-FAMILY-MATURITY-PROMOTION-20260928-R1",
  "status": "ACTIVE / FAMILY-WIDE / PROMOTION-GOVERNANCE / NON-NUMERICAL / NO-AUTO-PROMOTION / FAIL-CLOSED",
  "effective_at": "2026-09-28T00:33:00+09:00",
  "purpose": "Promote mature, family-independent contracts learned in one Family into Common authority without copying family-specific numerics, adapters, parameters or venue mechanisms.",
  "promotion_classes": {
    "C0_SCHEMA_INTERFACE": {
      "examples": [
        "schema",
        "interface",
        "receipt shape",
        "temporal ordering",
        "measurement definition"
      ],
      "behavioral_change": false,
      "minimum_evidence": [
        "cross-family semantic equivalence",
        "regression pass",
        "no authority collision"
      ],
      "unknown_oos_required": false
    },
    "C1_EXECUTION_CORRECTNESS": {
      "examples": [
        "fail-closed gate",
        "receipt verification",
        "runner-universe integrity",
        "provenance completeness"
      ],
      "behavioral_change": false,
      "minimum_evidence": [
        "owning-family acceptance",
        "second-family compatibility acceptance or proof of implementation independence",
        "negative tests"
      ],
      "unknown_oos_required": false
    },
    "C2_DECISION_POLICY": {
      "examples": [
        "MEC policy",
        "ticket selection",
        "capital routing",
        "KRS rescue policy"
      ],
      "behavioral_change": true,
      "minimum_evidence": [
        "pre-result freeze",
        "unknown OOS",
        "robust utility/PFS review",
        "explicit promotion declaration"
      ],
      "unknown_oos_required": true
    },
    "C3_NUMERICAL_MODEL": {
      "examples": [
        "weights",
        "thresholds",
        "parameter_map",
        "mapping coefficients",
        "venue fixed bonuses"
      ],
      "behavioral_change": true,
      "minimum_evidence": [
        "family-specific calibration",
        "family-specific unknown OOS",
        "anti-leakage review",
        "explicit promotion declaration"
      ],
      "unknown_oos_required": true,
      "cross_family_direct_promotion_forbidden": true
    }
  },
  "portable_to_common": [
    "CURRENT_AUTHORITY_RESOLUTION",
    "FORMAL_LIFECYCLE_CONTRACT",
    "RUNNER_UNIVERSE_PROTOCOL",
    "REQUIRED_INDEX_MANIFEST_PROTOCOL",
    "TEMPORAL_INTEGRITY",
    "RECEIPT_VERIFICATION",
    "PROVENANCE_CONTRACT",
    "PREDICTION_UTILITY_MEASUREMENT",
    "FAILURE_LOCALIZATION",
    "PREQUENTIAL_LEARNING_TRANSPORT",
    "PROMOTION_GOVERNANCE",
    "RACE_IDENTITY_PROTOCOL",
    "PREDICTION_CUTOFF_PROTOCOL",
    "EVIDENCE_FEATURE_PROTOCOL",
    "INDEX_PROVENANCE_PROTOCOL",
    "ACTUAL_NUMERICAL_CALCULATION_PROTOCOL",
    "STATIC_FREEZE_PROTOCOL",
    "KRS_RECEIPT_VERIFICATION",
    "ROLE_PAIR_THIRD_DECISION",
    "MANDATORY_STAGE_MANIFEST",
    "FINAL_FREEZE_PROTOCOL",
    "FINAL_BEFORE_POST_VERIFICATION"
  ],
  "remain_family_specific": [
    "SOURCE_ADAPTER",
    "INFORMATION_SOURCE_REGISTRY",
    "EVIDENCE_RULE_REGISTRY",
    "NUMERICAL_MAPPING",
    "NUMERICAL_MATERIALIZER",
    "KRS_INPUT_ADAPTER",
    "PARAMETER_MAP",
    "FAMILY_PREDICTION_MODEL",
    "EVIDENCE_FEATURE_COMPILER",
    "INDEX_PROVENANCE_BUILDER"
  ],
  "remain_venue_specific": [
    "COURSE_GEOMETRY",
    "DISTANCE_INTERPRETATION",
    "VENUE_TRACK_STATE",
    "VENUE_POSITION_PROGRESS_FRICTION",
    "VENUE_EVIDENCE_INTERPRETATION",
    "VENUE_REGRESSION_FIXTURE"
  ],
  "mandatory_review": [
    "PORTABILITY",
    "DUPLICATION",
    "AUTHORITY_COLLISION",
    "FAMILY_NUMERICAL_CONTAMINATION",
    "VENUE_KNOWLEDGE_ERASURE",
    "TEMPORAL_PURITY",
    "OOS_REQUIREMENT_CLASSIFICATION",
    "PRODUCTION_FREEZE_IMPACT",
    "ROLLBACK_PATH"
  ],
  "promotion_rule": "No item becomes Common Production merely because it worked in JRA, LOCAL, BAN, a single venue, a historical replay, or a correctness acceptance.",
  "automatic_promotion": false,
  "production_effect": "GOVERNANCE_ONLY / NO NUMERICAL CHANGE"
}

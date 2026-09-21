# ケイバメトリクスFamily 実行Architecture正式統合改定 R4

制定日：2026-09-21
Profile：KM-FAMILY-EXECUTION-ARCHITECTURE-20260921-R4
Predecessor：KM-FAMILY-EXECUTION-ARCHITECTURE-20260921-R3
Status：ACTIVE / FAMILY-WIDE / PRODUCTION-EXECUTION-OVERLAY / NON-NUMERICAL / FAIL-CLOSED / MEC-R2-MANDATORY

## 1. 継承
R3を全面継承し、Ticket/Capital段のAuthorityを
`KM-FAMILY-MINIMUM-EFFICIENT-COVERAGE-20260921-R2`
へ更新する。

## 2. Family正式パイプライン
CANON_RESOLVE
→ FULL_RUNNER_UNIVERSE
→ REQUIRED_INDEX_MANIFEST_BUILD
→ ALL_REQUIRED_INDEX_TERMINAL
→ STATIC_FREEZE
→ PRE_KRS
→ KRS
→ KRS_PREDICTION_UTILITY_CAPTURE
→ W/P2/P3
→ HEAD/PAIR/THIRD
→ MATERIAL_COVERAGE_UNIVERSE
→ MINIMUM_EFFICIENT_COVERAGE_R2
→ CAPITAL_COMPATIBILITY
→ FINAL_TICKET_FREEZE
→ FINAL_VERIFY
→ RESULT
→ REFLECTION/KMS

## 3. Ticket Width
固定点数上限は禁止する。
点数はMECの結果であり入力ではない。
診断帯はAuthorityを持たない。

## 4. Optimization Objective
100% Material Coverageを制約として、必要資本を最小化する。
追加Ticketが新しいMaterial Coverageを増やさない時にSTOP BUYING。
1点削除でCoverageが100%未満になる時にSTOP COMPRESSING。

## 5. Width Shape
Head / Pair / Thirdは別幅とし、原則 Head < Pair < Third。
Third uncertaintyはSet Protectionを優先し、Exact Orientationは独立根拠がある場合のみ追加する。

## 6. Budget
最低必要資本がCapital Policyに適合しない場合、Semantic Coverageを削らず
LIMITED / PAPER / NO-BETへ移行する。

## 7. Family Scope
JRA / LOCAL / BAN / ALL_VENUESへ強制継承。
JRAはRuntime強制済み。
LOCAL/BANはMEC対応Runtimeの外部実行証明がない限り旧固定幅へ戻らずFORMAL-FULLをFail-Closedする。

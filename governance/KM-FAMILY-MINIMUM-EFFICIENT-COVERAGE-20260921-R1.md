# ケイバメトリクスFamily Minimum Efficient Coverage 規格 R1

制定日：2026-09-21
Profile：KM-FAMILY-MINIMUM-EFFICIENT-COVERAGE-20260921-R1
Status：ACTIVE / FAMILY-WIDE / PRODUCTION-EXECUTION-OVERLAY / NON-NUMERICAL / NO-FIXED-TICKET-CAP / FAIL-CLOSED

## 1. 最上位命題
ケイバメトリクスの馬券設計目的は、最小点数でも最大点数でもない。
目的は、Static Prediction、Venue Prediction、Role、Ordered Pair、Pair-local Third、Multi-World、KRS等によって事前にMaterialと認定された未来構造を破壊せず、これを実行可能馬券へ変換するための最小資本Skeletonを求め、長期OOSでPFSを改善することである。

## 2. MEC定義
Minimum Efficient Coverage（MEC）を次で定義する。

> 必要なMaterial Coverageを100%保持する制約下で、購入資本を最小化するTicket集合。

点数は目的変数ではなく結果である。固定点数上限・固定点数帯を正式な購入Authorityとして使用しない。

## 3. 絶対禁止
以下を禁止する。
- 「12点まで」「20点まで」等を先に決めてSemantic Universeを削ること
- BUDGET-NONSELECTEDだけを理由にMaterial Pair/Third/Orientationを消すこと
- KRS/Multi-Worldで残ったMaterial構造を固定資本へ合わせてSemantic Excludeへ変換すること
- 同一Worldの重複購入をCoverage増加と数えること
- 点数を広げること自体を成功とみなすこと

## 4. 必須順序
Prediction
→ KRS
→ W/P2/P3
→ Ordered Pair
→ Pair-local Third
→ Material Coverage Universe
→ MEC
→ Capital Compile
→ FINAL

CapitalはSemantic Coverage完成後にのみ作用する。

## 5. Material Coverage
Production PredictionでPURCHASEまたはMaterial PROTECTとされた構造を対象とする。
最低限、
- Material Winner Head
- Material Ordered Pair
- Material Exact Third
- Pair-local Tail Protection
- Structural Orientation Protection
を扱う。

Correctness terminalization、schema closure、単なる形式補修はMaterial Coverageとして購入強制しない。

KRS ShadowはPromotion前はMEC Production資本へ直接入れず、Shadow比較として併記する。

## 6. 券種責務
Family/Venue固有の発売券種を尊重する。
JRA現RuntimeのMEC v1 transportでは、
- EXACTA：Ordered Pair Skeleton
- TRIO：Pair-local Tail Set Protection
- TRIFECTA：Material Exact Third
を基本責務とする。

他券種は独立Material Coverageを追加する場合のみ購入し、券種が違うだけの重複を禁止する。

## 7. Budget Rule
MEC Minimum Required Capitalが市場適合・利用者Capital Policyを超える場合、
Material Coverageを削るのではなく、
LIMITED / PAPER / NO-BET
へ移行する。

## 8. Stop Rules
STOP BUYING：
追加Ticketが新しいMaterial Coverageを一つも増やさない時。

STOP COMPRESSING：
Ticketを1点削除するとMaterial Coverageが100%未満になる時。

## 9. Width
固定上限は置かない。
点数帯は診断のみとしAuthorityを持たない。
- 1-8 CONCENTRATED
- 9-16 STANDARD
- 17-24 DIVERSE
- 25-36 HIGH_UNCERTAINTY
- 37+ VERY_WIDE_REVIEW

37点以上でもMaterial Coverageが必要なら許可する。
逆に8点でもMaterial Coverageが欠ければ不適合である。

## 10. 全Family継承
LOCAL / JRA / BAN / ALL_VENUESへ自動継承する。
VenueはPrediction Profileを担当し、Ticket幅・Capital Compressionの共通規則は本Profileへ返す。
Family固有Runtimeが未配備の場合、FORMAL-FULLを名乗らずFail-Closedする。

## 11. Measurement
各Formal Predictionで最低限、
- Material Coverage Ratio
- Minimum Required Capital
- Ticket Count
- Width Band
- Coverage Saturation Curve
- Redundant Ticket Count
- KRS Shadow non-capitalized delta
を保存する。

結果後はPFSだけでなく、Actual Winner/Pair/Top3/Exact Coverage、Tail Protection Efficiency、Redundant Capital Ratioを較正する。

## 12. 原則
最小資本とは「金額を可能な限り小さくする」ことではない。
必要な予測Coverageを完成させるために必要な最小資本である。

# ケイバメトリクスFamily Minimum Efficient Coverage Mandatory Overlay R2

制定日：2026-09-21
Profile：KM-FAMILY-MINIMUM-EFFICIENT-COVERAGE-20260921-R2
Predecessor：KM-FAMILY-MINIMUM-EFFICIENT-COVERAGE-20260921-R1
Status：ACTIVE / FAMILY-WIDE / PRODUCTION-EXECUTION-OVERLAY / NON-NUMERICAL / MANDATORY / NO-FIXED-TICKET-CAP / FAIL-CLOSED / NO-LEGACY-WIDTH-FALLBACK

## 1. 最上位命題
全ケイバメトリクス正式予想のTicket/Capital目的を次で固定する。

> Static Prediction、Venue Prediction、Multi-World、KRS、W/P2/P3、Ordered Pair、Pair-local Thirdが事前にMaterialと認定した未来構造を破壊せず、必要Coverageを100%保持する最小必要資本のTicket Portfolioを求める。

「最小点数」は目的ではない。
「広く買うこと」も目的ではない。
目的は Minimum Required Capital for Maximum Material Coverage である。

## 2. 全Family強制適用
本Overlayは次へ自動適用する。
- JRA：中山、東京、阪神、京都、中京、新潟、福島、小倉、札幌、函館
- LOCAL：大井、川崎、船橋、浦和、園田、姫路、名古屋、笠松、金沢、高知、佐賀、盛岡、水沢、門別その他地方平地
- BAN：帯広ばんえい
- 今後追加される全Venue

Venue個別規格はPrediction Profileを担当する。
Ticket Width / Capital Compressionの最上位Authorityは本Overlayへ返す。

## 3. 固定点数上限禁止
「12点まで」「20点まで」「三連単6点まで」等の固定点数上限を正式Authorityとして使用してはならない。

Ticket CountはMEC計算の出力であり、入力ではない。

診断帯のみ許可する。
- 1–8：CONCENTRATED
- 9–16：STANDARD
- 17–24：DIVERSE
- 25–36：HIGH_UNCERTAINTY
- 37+：VERY_WIDE_REVIEW

37点以上もMaterial Coverage上必要なら許可する。

## 4. 必須順序
Prediction
→ KRS
→ W/P2/P3
→ Ordered Pair
→ Pair-local Third
→ Material Coverage Universe
→ MEC Optimization
→ Capital Compatibility
→ Final Ticket Freeze

Capitalを理由にSemantic Universeを先に削ってはならない。

## 5. Stop Rules
STOP BUYING：
追加1Ticketが新しいMaterial Coverageを増やさない時。

STOP COMPRESSING：
1Ticket削除するとMaterial Coverage Ratioが100%未満になる時。

この二条件間の最小資本Portfolioを正式MECとする。

## 6. Width Direction
Head / Pair / Thirdの幅を同一に扱わない。

原則：
Head Width < Pair Width < Third Width

Third/Tailの不確実性は、馬単Headを無制限に増やすのではなく、TRIO等のSet Protectionを優先して低資本で保護する。
Exact Orientationに独立根拠がある場合のみTRIFECTAを追加する。

## 7. Marginal Coverage
各Ticketは最低1つの独立Material Coverageを追加しなければならない。

有効：
- NEW_WORLD
- NEW_HEAD_PATH
- NEW_PAIR
- NEW_THIRD
- NEW_ORIENTATION
- STRUCTURAL_PROTECTION

無効：
- REDUNDANT
- BET_TYPE_ONLY_DUPLICATION
- SAME_WORLD_DUPLICATION

無効Ticketは原則削除する。

## 8. Budget
MEC Minimum Required Capitalが利用者Capital PolicyまたはMarket Compatibilityを超える場合、
Material Coverageを削って点数を合わせてはならない。

LIMITED / PAPER / NO-BETへ移行する。

## 9. KRS
KRS Structured OutputはPrediction Utility Deltaとして保存する。
Production昇格前のKRS Shadow DeltaはMEC Production資本へ自動投入しない。
KRS RescueをCapital化するには、別途OOS Promotion Gateを通す。

## 10. Runtime Enforcement
JRA Formal RuntimeではMECを必須実行する。
LOCAL/BANでMEC対応Formal Runtimeの外部実行証明がない場合、旧固定幅方式へSilent Fallbackしてはならず、FORMAL-FULLをFail-Closedする。

## 11. Measurement
全Formal Predictionで保存する。
- Material Coverage Ratio
- Minimum Required Capital
- Ticket Count
- Width Band
- Coverage Saturation Curve
- Redundant Ticket Count
- Marginal Coverage per Ticket
- KRS Shadow non-capitalized delta
- Head / Pair / Third Width
- Capital by Bet Type

結果後は、
- Actual Winner Coverage
- Ordered Pair Coverage
- Top3 Set Coverage
- Exact Coverage
- Tail Protection Efficiency
- Redundant Capital Ratio
- PFS
を較正する。

## 12. No Legacy Fallback
本Overlay発効後の全正式予想で、旧固定点数・固定Capital幅を理由にMECを回避することを禁止する。

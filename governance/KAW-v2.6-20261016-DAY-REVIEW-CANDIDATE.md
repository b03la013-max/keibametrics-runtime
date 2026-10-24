# 川崎競馬攻略条項 v2.6-KAW｜20261016 Signed Forward Day Review（改定候補）

Status: CANDIDATE / NON-PRODUCTION / NON-NUMERICAL / NO-AUTO-PROMOTION / NO-BET-AUTHORITY / PRODUCTION-FROZEN  
作成基準日: 2026-10-16 JST  
現行場別Production正本: 川崎v2.4-KAW（継承全文SHA256: 7c295cb15a3444cd66c6a18a8fbc9cf60891049006c1b2938ff4df04691b8472）  
共通Authority: R51、LOCAL共通v4.13 Rev.1、MEC-R3、KRS Engine 1.1.0 / parameter_map v0.1-provisional。  
v2.5-KAW (PR #263): 未昇格Draft。v2.6はv2.5の施行や自動統合を意味しない。将来の競合調整を要する。

v2.4第0～371条と附則は元の意味を維持する。本改定の第372～383条は、その既存業務に対する非本番の監査粒度・将来検証方法を追加する。数値式・静的Owner・購入規則は現時点で変更しない。

## 第372条　改定目的
本日の課題は、実績順位由来のW/P2制約、KRS Proxy救済の相反する成績、三連複購入実在の偽陽性、広い購入構造のHit-But-Loss、新馬戦の馬番タイブレークである。「頭を増やす」「点数を減らす」の固定ルールを制定しない。

## 第373条　20261016正式Signed日次台帳
次の5戦は結果前Signed FINALと結果後Signed RESULTの存在を確認したRECOMMENDATION-ONLY精算。実購入は未確認。

| R | 結果 | 投資円 | 払戻円 | 損益円 | PFS | 第一原因 |
|---|---|---:|---:|---:|---:|---|
| 1 | 8→5→6 | 15,600 | 15,030 | -570 | 96.35% | CAPITAL_EFFICIENCY |
| 2 | 2→1→6 | 7,500 | 35,610 | +28,110 | 474.80% | NONE / TIEBREAK-QUALITY-WARNING |
| 6 | 12→1→11 | 15,600 | 0 | -15,600 | 0% | PREDICTION_ROLE_P2 |
| 9 | 5→7→6 | 13,200 | 0 | -13,200 | 0% | PREDICTION_ROLE_W |
| 12 | 10→5→8 | 14,400 | 0 | -14,400 | 0% | PREDICTION_ROLE_W |
| 合計 | 5戦 | 66,300 | 50,640 | -15,660 | 76.38% | — |

ユーザー提供の1・6・9・12の4戦のみの合計は58,800→15,030、-43,770円、25.56%。別母集団として表示する。
5戦のW捕捉3/5、P2捕捉3/5、P3捕捉5/5。全馬P3を予測識別力と解釈しない。的中券あり2/5、黒字1/5、PFS中央値0%。残る7戦は正式FINAL未確認として実行成功率の母集団へ残し、0円の負け券に換算しない。

## 第374条　Newcomer Non-Informative Tiebreak Gate
R02では全6頭が実走比較なしで同点となり、現行Static Ownerは末尾馬番で順位1,2,3,4,5,6を形成した。比較事実のない順位を能力評価と称しない。Candidate監査で EVIDENCE_DISCRIMINATIVE / PARTIAL / TIEBREAK_ONLY_NONINFORMATIVE / UNKNOWN を結果前に認証する。TIEBREAK_ONLY時の推奨購入はNO-BET/PAPERとの事前比較対象とし、Productionを無断変更しない。調教・能力試験・血統は正式Source/Temporal/権限を満たす実観測のみ採用する。

## 第375条　W/P2 Role Diversity Review
既存Ownerの上位3頭W・上位6頭P2というOrdinal固定幅は能力の較正結果ではない。R06の1=P2漏れ、R09の5=W・7=P2漏れ、R12の10=W漏れを事前Evidenceに基づく対照Fixtureとする。同距離実績がない＝弱い、としない。別距離/Class/位置取得/中盤/直線/馬体/休養をStage別の根拠に分解し、UNKNOWNとNegativeを分離する。結果後に当該RaceのRoleを修正しない。

## 第376条　KRS Proxy Rescue Control
R06で発走前KRSは12→1を290/5000回・P2追加Shadow、R09で実勝馬5をADD_W_SHADOW (SSR-W=0.238)、R12では実勝馬10を救済せず11に誤ったW追加Shadowを提示。救済成功・失敗の両Fixtureを保持する。未較正TECHNICAL_PROXY_DIAGNOSTICを勝率/EV/直接購入権限とみなさず、Frozen candidateでfalse additions・増額・正解券・PFSの純増比較を行う。

## 第377条　Role/Set/Exacta/Trio/Trifecta厳密な購入実在
次を別証拠として保持する。
- semantic_top3_set_present、winner_w、second_p2、third_p3
- purchased_exacta_direction、purchased_trifecta_exact_direction
- purchased_trio_unordered_set、alternate_orientation_present
- actual_purchase_verified、receipt_sha256、precutoff timestamp

R01は馬単8→5/三連単8→5→6を購入・三連複5-6-8非購入。R12は別方向三連単5→10→8あり、正方向10→5→8と三連複5-8-10なし。Legacyのtop3_set_ticket_coverage=trueを三連複購入と誤読しない。

## 第378条　Pair＋Trio→Exactの理由付きTerminal
v2.4第360/365条を継承。Pair A→B、Set{A,B,C}、Third Cの各候補はPURCHASED / STRUCTURAL-INELIGIBLE / EVIDENCE-RANKED-LOWER / BUDGET-NONSELECTED / UNRESOLVED-REVIEWに理由・来歴・時間を添えて終端する。全購入を強制しない。Head欠落と購入変換欠落は一次/二次原因を区別する。

## 第379条　Core-Hit Recoverability / Purpose Capital
v2.4第366条を実践し、購入前の当該券種別Market価格・Stake・Core/Independent/Protection/Peripheral・冗長性・予算・No-Betを監査する。価格欠測はPRICE_HOLD。結果後払戻で事前市場を代替しない。R01の「的中しても−570円」をNon-probability Sanity Fixtureとし、固定点数・固定倍率・事後的に削った正解券の操作を禁止する。

## 第380条　Execution / Prediction / Delivery 3-axis
SOURCE/PRE_KRS/KRS/FINALのSigned PASS、Staticの実根拠品質、Canonical券面、資金適合性、結果後PFS、受領者側Deliveryは別判定。prestart_delivery_pass=false / user_received_at=nullならSERVICE_COMPLETEと称さない。Race-Key未成立も実行母集団から削除しない。

## 第381条　Formal母集団と欠測
2026-10-16開催12R全体とSigned FINALを取得できたR01・R02・R06・R09・R12の5Rを別分母で保存する。未生成レースのPFSはN/Aであり0%ではない。結果の時計と知識Cutoffを保存し、RECONをFrozen OOSに混入しない。

## 第382条　未知未来評価の事前登録
同一Signed SOURCE、Full Runner Universe、Cutoffを用いて、Production Frozen baselineと次のPAPER/CANDIDATE Armを並走させる。
A現行Owner、B情報量不足でNO-BET、C W/P2根拠多様化、D条件付きKRS Rescue、E Core Capital効率、F券種交点Integrity。着順Role、購入券面、三連複Set、PFS、利益、最大ドローダウン、Hit-But-Loss、No-Bet機会費用、Deliveryを評価。未知未来30適格戦/3開催日を一次レビュー目安とするが、数に到達しただけで昇格させない。改善が再現しなければSIMPLIFY_OR_REJECT。

## 第383条　改定の効力・Freeze
本v2.6は非本番の正式な改定候補であり、川崎v2.4 Production、Family R51、数値式・KRS・AKI/MEC・Capital・予測Ownerの動作を変更しない。PR #263 v2.5未昇格候補と別物として識別する。結果後に同一レースのFrozen予測を書き換えない。昇格にはSigned Forward OOS比較、Regression、PR競合審査、明示Owner承認、Current Authority/Deployment更新が必要。
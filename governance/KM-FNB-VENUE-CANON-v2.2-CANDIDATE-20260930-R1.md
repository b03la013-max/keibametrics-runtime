# ケイバメトリクス地方版 船橋競馬攻略条項 v2.2-FNB-CANDIDATE
## 20260930 Day Regression / Venue Prediction Reachability / Class-Current-State Translation Shadow Candidate

- 制定日時：2026-09-30 21:40 JST
- Profile：`KM-LOCAL-FNB-v2.2-CANDIDATE-20260930-R1`
- Predecessor / Current Production：船橋競馬攻略条項 v2.1-FNB
- Status：CANDIDATE / SHADOW-ONLY / NON-PRODUCTION / NON-NUMERICAL / BEHAVIOR-CHANGING / PROMOTION-HOLD / FROZEN-UNKNOWN-OOS-REQUIRED
- Production Effect：NONE
- Numerical Change：NONE
- KRS Physics Change：NONE
- parameter_map Change：NONE
- Production MEC-R3 Change：NONE
- Capital Policy Change：NONE
- Current Production Canon：v2.1-FNB remains unchanged
- Current Authority Resolution：execution-time current successorを動的解決。本Candidate作成時参照は `KM-FAMILY-CURRENT-AUTHORITY-20260929-R35`

---

# 0. 法的位置付け

本v2.2-FNB-CANDIDATEは、2026-09-30船橋12R Day Regressionから得られたVenue-specific Prediction仮説だけを、次の未知Raceで反証可能なSHADOWとして整理する。

本CandidateはProduction v2.1-FNBを置換しない。2026-09-30の既知結果はTRAINING / REGRESSION evidenceであり、本CandidateのFrozen Unknown OOSとして数えない。

Day Regressionで最も大きかったExact ConversionおよびCapital Width問題はCommon / Family ownerであり、本Venue Canonへ取り込まない。

---

# 1. Day Regression要約

2026-09-30船橋12Rのユーザー提示Formal Review basisでは、Frozen Recommendation合計は投資65,200円、払戻35,300円、PFS 54.14%。

First Material Failure分類は、
- Prediction / Role：2戦
- Conversion：8戦
- Capital：2戦

であり、Venue Canonの全面再構築を支持しない。

特に4R・5R・7R・8R・9R・11R・12Rで反復した正解Exactの `SEMANTIC_ONLY / purchase_authority=false` はCommon Ticket/Conversion ownerへ返す。

3R・10R等で観測されたCapital Width過大もCommon MEC / Capital ownerへ返す。

---

# 2. v2.1から維持するProduction知識

v2.1-FNBの以下を全面維持する。

- FPR-FNB
- FSD-FNB
- LCC-FNB
- TVGCI-FNB
- Reachable Position Range
- Stage Cost Topology
- P2 Reachability Rescue
- Role Divergence Review
- Distance Capability Rescue
- Course-specific Leadership
- Same-day Current Track State
- UNKNOWN != WEAK
- Venue/Common ownership separation
- First Material Failure routing
- Race n immutable / learning applies to n+1

本Candidateを理由に固定補正、固定点、固定閾値、自動昇格、自動購入を追加しない。

---

# 3. Candidate A — FNB-2YO-LOWOBS-ALT-P2-REACHABILITY-R1

## Observation
2026-09-30 R1では、実2着馬がP3-Protectedまで存在した一方、P2へ届かずOrdered Pairを失った。

## Trigger
次を全て満たす場合にのみ発動する。
1. 2歳戦。
2. Current evidence上、低観測 / HIGH uncertaintyとして扱われている。
3. 対象馬がP3-Core / P3-Protectedに存在するがP2 Activeではない。
4. P2へ自動昇格させるだけのDirect Evidenceは不足している。

## Audit
既存P2 Reachability Rescue内で、以下のAlternative P2 Pathを明示再監査する。
- early leader collapse時のsurvival
- tracking / mid-packからのlow-cost progression
- winner separation後のplace scramble
- current-form persistence
- low-observationゆえのrole ceiling過小化

## Authority
SHADOW REVIEW ONLY。自動P2昇格、固定加点、購入義務を持たない。

## Primary metrics
P2 rank / P2 capture / candidate width / false-positive P2 / Ordered Pair reachability。

---

# 4. Candidate B — FNB-DISTANCE-RETURN-CLASS-CONTEXT-W-REACHABILITY-R1

## Observation
2026-09-30 R6では、船橋同距離実績・上級条件経験・適距離回帰を持つ勝ち馬がP3-Protected止まりとなりW Reachabilityを失った。

## Trigger
対象馬について、
- 船橋同距離または近接距離で明確な過去Positive Evidenceがある、
- 直近は別距離・別条件を使用している、
- 今回が過去Positive Evidenceへ近いdistance/class contextへ戻る、
- 近走着順だけで低Roleへ押し込まれている可能性がある、
場合。

## Audit
Distance Return、Class Context、Venue-Distance Proven Execution、Current Stateを分離し、P3-onlyで終了してよいかW/P2 Reachabilityを再監査する。

## Authority
自動W昇格なし。固定distance-return bonusなし。

## Primary metrics
Winner rank / W capture / Alternative Winner capture / false-positive W width。

---

# 5. Candidate C — FNB-LAYOFF-HISTORICAL-CEILING-DECAY-AUDIT-R1

## Observation
2026-09-30 R5では長期休養馬のHistorical CeilingをCurrent W/P2有効性へ強く移送した可能性が観測された。

## Trigger
- Historical venue/distance ceilingが高い、
- long layoff / current-state sparse / current evidence conflictのいずれかがある、
- W/P2評価の主要根拠がhistorical ceilingへ偏る、
場合。

## Audit
Historical CeilingとCurrent Stateを別表示し、Current execution evidenceが不足する場合にRole Ceilingを再監査する。

## Authority
固定減点、休養日数閾値、機械的降格を定義しない。

## Primary metrics
Winner/P2 rank delta / false-positive head rate / Positive Control destruction。

---

# 6. Candidate D — FNB-CLASS-EXPOSURE-RELIEF-TRANSLATION-AUDIT-R1

## Observation
2026-09-30 R7・R12等では、上級条件Exposureまたは高Class路線からの条件緩和を、近走着順だけでは十分に表現できない可能性が観測された。

## Trigger
- 上級条件 / 重賞級 / 強い相手関係へのExposureがある、
- 今回条件が相対的に緩和される、または同Venueで再現可能な条件へ戻る、
- recent finish positionだけでは能力文脈を失う可能性がある、
場合。

## Audit
Class Exposure、Class Relief、Venue compatibility、Current Stateを分離し、W/P2/P3 ceilingを再監査する。

## Authority
「上級戦経験=自動加点」を禁止する。

## Primary metrics
Winner/P2/P3 rank / top3 mean rank / false-positive width。

---

# 7. Commonへ返す項目

本Candidateは以下を所有しない。

## Exact Continuity
2026-09-30 Day Regressionで反復した、
`Material/Purchased Pair + Active P3 -> Exact SEMANTIC_ONLY`
はCommon Ticket Conversion owner。

Common Shadow：`KM-FAMILY-FNB-DAY-REGRESSION-COMMON-SHADOW-20260930-R1`

## KRS-actionable Exact
KRS Exact supportはFrozen Production Predictionを書き換えず、Common Conversion re-audit signalとしてのみ研究する。Venue Canonへ購入規則を追加しない。

## Concentration-aware Capital Width
Semantic Coverageを保持したままCapital Widthだけを適応化する仮説はCommon MEC / Capital owner。Venue CanonへTicket width、Stake、Budget、TAIL policyを追加しない。

---

# 8. Behavior分類

本CandidateはNON-NUMERICALだがBEHAVIOR-CHANGINGである。

理由：W/P2/P3 Reachability review結果を変え得るため。

したがって、
- Productionへ自動反映しない。
- Current v2.1とCandidate ON/OFFを同一Frozen Source basisで比較する。
- 既知2026-09-30 Raceの改善だけをPromotion Evidenceにしない。
- Frozen Unknown OOSを中心にKeep / Modify / Deleteを判断する。

---

# 9. OOS Validation Plan

次の未知船橋Raceから、Candidate適格Raceについて結果前に以下をFreezeする。

1. Production v2.1 Static。
2. Candidate OFF snapshot。
3. Candidate ON review result。
4. Candidateが変更したW/P2/P3 roleだけのdiff。
5. Candidate Count / Active Role Count。
6. Source basis / cutoff / timestamp。
7. Prediction result後のWinner/P2/P3 rank gain/harm。

主評価：
- Winner Rank
- P2 Rank
- P3 Rank
- Top3 Mean Rank
- W/P2/P3 Capture Efficiency
- Alternative Winner
- Ordered Pair reachability
- false-positive Candidate Width
- Positive Control destruction

経済評価はCommon Ticket/Capitalと分離する。

Automatic Promotionは禁止する。

---

# 10. Change Ledger

KEEP:
- v2.1 Production Prediction Knowledge全体
- P2 Reachability / Stage Cost / FPR-FSD-LCC
- Same-day Current Track State
- UNKNOWN semantics

ADD AS SHADOW ONLY:
- 2YO Low-observation Alternative P2 Reachability
- Distance Return × Class Context W Reachability
- Layoff Historical Ceiling Decay Audit
- Class Exposure / Relief Translation Audit

MOVE / KEEP IN COMMON:
- Exact Continuity
- KRS-actionable Exact Bridge
- MEC / TAIL
- Capital Width
- Ticket / Stake
- Runtime / Receipt / Settlement

DELETE:
- なし。単日結果だけを理由にProduction条項を削除しない。

---

# 11. Promotion Gate

Promotion条件はCurrent Family Maturity Contractに従う。

最低条件：
- preregistered pre-race activation
- result-blind freeze
- Frozen Unknown OOS
- Positive / Negative Control
- width inflation監査
- simpler baseline比較
- explicit human review

単一日・単一VenueのReplayだけでは昇格不可。

---

# 12. 最終判定

CANON REVISION REQUIRED：SHADOW-ONLY

NEW CANON：船橋競馬攻略条項 v2.2-FNB-CANDIDATE

ARCHITECTURE VERDICT：MINOR PREDICTION CANDIDATE / NO PRODUCTION RECONSTRUCTION

BEHAVIOR：BEHAVIOR-CHANGING

NUMERICAL CHANGE：NONE

PRODUCTION PROMOTION：NO / HOLD

CURRENT PRODUCTION：船橋競馬攻略条項 v2.1-FNB UNCHANGED

最終原則：

> 今日のPFS低下の大半をVenue Predictionへ転嫁しない。Venue固有Prediction failureだけをSHADOW化し、Common Conversion / Capital failureはCommonへ返す。

> Candidateは「昨日を説明する条項」ではなく、次の未知Raceで反証可能な最小仮説として運用する。

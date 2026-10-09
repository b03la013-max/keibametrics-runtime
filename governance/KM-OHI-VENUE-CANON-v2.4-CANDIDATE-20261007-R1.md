# ケイバメトリクス地方版 大井競馬攻略条項 v2.4-OHI-CANDIDATE
## 20261007 Day Regression / Ability-Readiness / Leadership-Cost / Winner-Migration / First-OHI Adaptation Refinement

- 制定日：2026-10-07
- Profile：`KM-LOCAL-OHI-v2.4-CANDIDATE-20261007-R1`
- Predecessor / Current Production：`大井競馬攻略条項 v2.3-OHI`
- Status：`CANDIDATE / SHADOW-ONLY / NON-PRODUCTION / NON-NUMERICAL / VENUE-PREDICTION-REFINEMENT / BEHAVIOR-CHANGING / PROMOTION-HOLD / FROZEN-UNKNOWN-OOS-REQUIRED`
- Production Effect：NONE
- Production Pointer Change：NONE
- Numerical Change：NONE
- KRS Physics / parameter_map Change：NONE
- Production MEC-R3 / Capital Policy Change：NONE
- Current Family Production at creation：`KM-FAMILY-CURRENT-AUTHORITY-20261005-R40`
- R42：Open PR / NON-PRODUCTION at creation

# 0. 法的位置付け

本Candidateは、2026-10-07大井12R Day Regressionから得た**大井固有Prediction仮説だけ**を、次の未知Raceで反証可能なShadowとして整理する。

Production v2.3-OHIを置換しない。2026-10-07の既知結果はTRAINING / REGRESSION evidenceであり、本CandidateのFrozen Unknown OOSには算入しない。

当日最大のPFS損失OwnerであったCapital、Protection Burden、Market-Payout Sufficiency、MEC Width、Ticket/StakeはFamily/Common ownerであり、本Venue Canonへ購入規則として取り込まない。

# 1. Day Regression要約

2026-10-07大井12RのFormal Review basis：

- Frozen Recommendation Investment：183,200円
- Return：111,440円
- Profit/Loss：-71,760円
- PFS：60.83%
- Hit Race：11/12
- Profitable Race：3/12
- Hit-but-Loss：8/12
- Winner W Capture：9/12
- P2 Capture：12/12
- P3 Capture：12/12
- Ordered Pair Ticket Capture：8/12
- Ordered Exact Ticket Capture：4/12

First Material Failureは主に、
- Winner Role：R3 / R6 / R10
- Pair / Exact Connection：R2 / R4 / R5 / R7 / R9
- Capital Efficiency：R1 / R11 / R12
へ分離された。

この分布はVenue Canonの全面再構築を支持しない。Prediction Discoveryは概ね機能し、Venue側の改善対象はWinner Conversion / Current Readiness / Leadership Cost等へ限定する。

# 2. v2.3-OHIから維持するもの

以下をKEEPする。

- Course / Distance / Surface interpretation
- Position Acquisition
- Leadership Acquisition / Survival
- Progression / Corner Reachability
- Current Reproducibility
- Distance / Class Translation
- Venue Current State / Same-day GCI
- W / P2 / P3 separation
- UNKNOWN != WEAK
- Wide Semantic Universe
- KRS Firewall / Static独立性
- Race n Immutable / Learning applies to n+1
- Venue/Common ownership separation

本Candidateを理由に固定点、固定Weight、固定閾値、自動W昇格、自動購入を追加しない。

# 3. Candidate A — OHI-ABILITY-READINESS-SEPARATION-R1

## 命題
`Ability Ceiling` と `Current Race Readiness` を明示分離する。

高い過去能力、JRA Ceiling、上級条件実績、直接距離実績は「能力上限」の根拠であり、今日の勝ち切り状態を自動的に意味しない。

逆に、Current Readiness不確実だけを理由にAbility Ceilingを消してはいけない。

## Review trigger
以下のいずれかが成立するときShadow再監査する。

- Historical / class / distance ceilingは高いがCurrent execution evidenceが薄い
- Layoff / transfer / first-OHI / class transition等によりCurrent Readinessが不確実
- W評価の主要根拠がHistorical Ceilingへ偏る
- Abilityは高いがStage-fit / Survival / Current Stateにconflictがある

## Action
Ability Ceiling、Current Readiness、Venue Adaptation、Stage-fitを別表示し、W一本化してよいかを再審査する。

## Authority
SHADOW REVIEW ONLY。固定減点、固定加点、自動降格・昇格なし。

# 4. Candidate B — OHI-ACQUISITION-LEADERSHIP-COST-STALKABILITY-R1

## 命題
大井、とくに1200m系で、
`Position Acquisition`
`Leadership Cost`
`Stalkability`
`Survival`
を同一視しない。

前へ行けることと、先頭を背負い続けて勝ち切れることは別能力である。

## Review trigger
- primary front candidateが複数存在する
- 対象馬に再現的Position Acquisitionがある
- leader固定 / contested frontの可能性がある
- stalk / trackingへ引ける余地がある
- lightweight / same-day GCI / pace pressure等がCurrent Costへ影響し得る

## Audit
以下を別々に記録する。
- acquisition probabilityではなくacquisition evidence
- leader-fixed risk
- stalkability evidence
- front congestion
- pressure exposure
- 4C reachability
- survival / final conversion

## Authority
「前有利」「逃げ有利」の固定加点は禁止。結果後の1戦から斤量閾値・脚質閾値を作らない。

# 5. Candidate C — OHI-VENUE-CONDITIONED-WINNER-ROLE-MIGRATION-R1

## 命題
下位Roleに保持されている馬がWから落ちている場合、大井固有EvidenceでW-REVIEW優先度を付ける。

## Base trigger
`LOWER_ROLE_RETAINED_W_ABSENT`

対象馬がP2/P3 CORE/PROTECTED等に存在し、W absentであること。

## Independent venue evidence
- Position Acquisition
- Current Form / Current Reproducibility
- lightweight / weight change context
- same-day GCI
- Leadership Cost / Stalkability
- Survival Failureの原因分解
- Front Congestion
- Class continuity / transition
- Distance translation
- first-OHI / transfer adaptation uncertainty

複数独立根拠が一致した馬だけW-REVIEW優先度を上げる。

## Authority
`W-REVIEW != W PROMOTION`

自動W昇格、購入義務、固定pointは禁止。

KRS独立支持がある場合はFamily側のIndependent Rescue評価へ接続できるが、Venue Canon単独でKRS proposalをProduction化しない。

# 6. Candidate D — OHI-TRANSFER-FIRST-OHI-ADAPTATION-UNCERTAINTY-R1

## 命題
Transfer / first-OHI horseについて、

`Ability Ceiling`
`Venue Adaptation`
`Current Race Readiness`

を分離する。

## Principle
- UNKNOWN != WEAK
- UNKNOWN != STRONG
- UNKNOWN != AUTO-ELIMINATION
- First OHI != automatic downgrade
- High external ceiling != automatic W core

## Action
外部路線能力を保持したまま、初大井・初内外回り・初距離帯でWinner Conversionの不確実性を別表示する。

固定「転入減点」は作らない。

# 7. Regression Fixtures

2026-10-07は既知結果なのでCandidate OOSに算入しない。

## R1 — Ability Ceiling / Winner Conversion
Prediction・Pair・Exactは成功し、Capitalで負けた。Venue側は能力評価を壊さず、Winner ConversionとVenue Adaptation不確実性の分離をPositive/Neutral fixtureとして保持。

## R6 — Independent Rescue Positive Control
Production W absentの⑥をStatic P2/P3 COREに保持。KRSはW → Pair → Thirdを結果前に一貫救済。
Venue側はLower-role retained horseのW-REVIEW条件を測り、KRS権限拡大はFamily側へ委ねる。

## R7 — Role Capture / Pair Connection Separation
W/P2/P3は捕捉したが6→8 PairがResidual止まり。
Venue側はP2 Protectedを保持したことをPositive Controlとし、Pair purchaseはCommon ownerへ返す。

## R10 — Static/KRS Common Blind Spot
③をP2/P3に保持したがWへ昇格できず、KRSもWinner Rescueできなかった。
軽斤量 × Acquisition × same-day GCI × Leadership Cost / Stalkability × Survival reasonのVenue再審査fixtureとする。

# 8. Common / Familyへ返すもの

本Candidateは以下を所有しない。

- Protection Burden Ratio
- Market-Payout Sufficiency
- Conservative Capital
- Core-only disposition
- SET_ONLY / SET_PAIR
- Exact TOP-N purchase width
- Protection Capital Ceiling
- Equal-Budget / Equal-Ticket normalization
- Ticket / Stake
- Production MEC-R3
- Production Capital Policy
- KRS Physics / parameter_map
- Pair Residual purchase authority
- Pair-local Selective Exact purchase authority

これらはFamily/Common Decision / Ticket / MEC / Capital ownerへ返す。

# 9. KRS境界

6RはPositive Controlだが、7R・8R等でFalse additionsも観測された。

従って、
- KRS Firewall：KEEP
- KRS Automatic W / Pair / Exact Promotion：禁止
- Venue CandidateがKRSをProduction Owner化：禁止

Candidate CのVenue EvidenceとKRS独立supportが重なった場合のみ、Family ShadowのIndependent Rescue Reviewへhandoff可能とする。

# 10. OOS Validation Plan

次の真正Unknown-Future大井Raceから、Candidate適格ケースについて結果前に以下をFreezeする。

1. Production v2.3 Static snapshot
2. Candidate OFF snapshot
3. Candidate ON review
4. W/P2/P3 diff
5. Candidate activation reason
6. source basis / cutoff / timestamp
7. Candidate width
8. result後rank gain / harm

Primary metrics：
- Winner Rank
- W Capture
- P2 / P3 Capture preservation
- Alternative Winner Capture
- False W Promotion
- Positive Control destruction
- Candidate Width
- Ability-Readiness conflict resolution
- Acquisition/Leadership/Stalkability classification accuracy

経済評価はCommon Ticket/Capitalと分離する。

Automatic Promotionは禁止。

# 11. Promotion Gate

最低条件：
- preregistered result-blind activation
- Frozen Unknown OOS
- Production v2.3 same-race comparison
- Positive / Negative Controls
- false-promotion監査
- width inflation監査
- multiple race days
- explicit human review

2026-10-07 racesはTraining / RegressionのみでPromotion Evidenceへ算入しない。

# 12. Change Ledger

KEEP：
- v2.3-OHI Production
- Wide Semantic Universe
- W/P2/P3 separation
- UNKNOWN protection
- KRS Firewall
- Current Venue State / Same-day GCI

ADD AS SHADOW ONLY：
- Ability Ceiling / Current Race Readiness Separation
- Acquisition / Leadership Cost / Stalkability Separation
- Venue-conditioned Winner Role Migration Review
- Transfer / First-OHI Adaptation Uncertainty Separation

KEEP IN COMMON：
- Pair / Exact purchase authority
- MEC
- Protection
- Capital
- Market-Payout Sufficiency
- Ticket / Stake
- KRS Authority

DELETE：
- なし

# 13. 最終判定

CANON REVISION：YES / CANDIDATE ONLY

NEW CANON：`大井競馬攻略条項 v2.4-OHI-CANDIDATE`

ARCHITECTURE：MINOR VENUE PREDICTION REFINEMENT / NO NEW ARCHITECTURE

NUMERICAL CHANGE：NONE

PRODUCTION PROMOTION：NO / HOLD

CURRENT PRODUCTION：`大井競馬攻略条項 v2.3-OHI` UNCHANGED

最終原則：

> Capitalで負けたRaceをVenue Predictionへ転嫁しない。大井固有のPrediction Failureだけを最小Shadow仮説として抽出する。

> v2.4は昨日を説明するRuleではなく、次の未知大井Raceで反証されるためのCandidateである。


## 14. 2026-10-09 大井 Day Regression Supplement（既知結果 / Venue固有 / 非OOS）

- Evidence：`research/ohi/KM-LOCAL-OHI-20261009-VENUE-REGRESSION-R1.json`
- 位置付け：`REGRESSION ONLY / KNOWN RESULT / NON-OOS / NON-PRODUCTION / NO RULE CHANGE`。
- 2026-10-07に凍結されたv2.4 Candidate本体の予測仮説、適用条件、数値式、Promotion Gateは一切変更しない。
- 2026-10-09開催の大井4R〜10R：正式推奨券7戦、投資265,100円、払戻148,730円、損益-116,370円、PFS56.10%、的中7/7、黒字1/7、Hit-but-Loss 6/7。実購入PFSではない。
- R3：発走前のFormal Intent／Signed FINAL／Canonical Ticketは確認されていないため、`POST_RESULT_DIAGNOSTIC / NO_FORMAL_PFS_AUTHORITY` としてのみ保持し、正式集計・未知未来OOSへ混入しない。

### Venue所有：既存仮説を再検査する回帰フィクスチャ
1. **R3**：2歳・初1600m・休養明け等の不確実性の下で、先行残存と後方進出／勝ち切りを分ける。結果後資料のみでW救済が予測可能だったと主張しない。
2. **R6・R7・R10**：Ability Ceiling／Current Readiness／Venue Adaptation／Acquisition／Leadership Cost／Stalkability／Final Conversionを再監査する。馬体重の大幅増、転入、休養を固定点に変換しない。
3. **R8**：Static上位3頭・三連単の正解を保持しつつ大幅赤字。Venue PredictionのPositive ControlとFamily CapitalのNegative Controlを同一事例で分離する。
4. **R9**：条件付きW（事前順位6位の⑪）が的中三連単へ変換されたPositive Control。未較正KRS SSR-Wが低いだけで独立Static Wを削除しない。
5. **R4・R5・R6**：Venue側のRunner/Role保持を理由に、Common所有のPair/Third/Exact購入権限を変更しない。

### Family/Commonに返す — Venue Canonへ混入禁止
- R5・R6：購入済みOrdered Pairに対し、3着候補のPair-local Thirdが全件PROTECTまたは購入ゼロ。独立理由・Ticket Conversionを検証するが全件Exact補完しない。
- R4・R7・R8・R9・R10：正解三連単を購入済みなのに対応する三連複集合を購入していないことがある。事前GAP_DETECTEDから経済的な追加価値まで測る。全件Trio追加はしない。
- R8・R10：Exact的中でも配当が購入総額に見合わない。Market-Payout Sufficiency／Selective Capital／NO-BETはCommon Shadowで測る。R9の高配当黒字機会を失う可能性も必ず測る。
- MEC-R5 TOP4の30戦PFS64.18%は同30戦Production60.41%を上回るが双方100%未満。AKIは別Cohortで、2026-10-09時点の7件`PRODUCTION_SIGNED_SETTLEMENT_CONFLICT`はCorrectness HOLD。いずれも自動昇格不可。

### 既存Candidateへの影響（凍結を尊重）
- KEEP：v2.4 Candidate R1の4つのVenue仮説・KRS Firewall・Positive/Negative Control。
- APPEND：歴史回帰Evidenceと反例、Family/CommonへのHandoffだけ。
- NO：新たな固定加減点、閾値、Prediction Weight、購入ルール、VenueからのPair購入、結果後のCandidate ON改竄。
- `2026-10-09 v2.4-CANDIDATE OOS incremental = 0`。Candidateの真の結果前ON/OFF Freezeが別途証明される場合に限り再審査可能。今後の未知未来については予めFreezeして比較する。

### 補注
この補遺はv2.4 Candidateを正式Productionへ昇格させない。実行基盤上のCurrent Productionは引き続きv2.3-OHIであり、R44 Family Authority・MEC-R3・数値式・KRSは不変。

# KeibaMetrics Family
## Astra Recovery / Delta Re-Baseline / Continuation Directive
### 2026-09-30 R1

- Recovery Profile: `KM-ASTRA-RECOVERY-DELTA-REBASELINE-20260930-R1`
- Canonical start point: current `main`
- Current main SHA at issuance: `cd350ad95a501ef37965b03417af63d348ab894c`
- Prior Astra branch: `audit/execution-recasting`
- Prior Astra PR: #111 `Consolidate SOURCE acquisition and immutable checkpoint resume`
- Prior Astra branch relation to current main at issuance: DIVERGED / 2 commits ahead / 56 commits behind
- Recovery rule: DO NOT continue the old Astra branch in place. Re-baseline from current main and selectively carry forward only still-valid prior work.
- Production effect of this Recovery Directive itself: NONE

---

# 0. 最上位目的

今回のRecoveryは、Astraの前回改修を捨てて最初から作り直すためのものではない。

同時に、前回の中断点を何も見直さずそのまま再開するためのものでもない。

目的は、

**前回Astraが実施したUnified Execution Recastingの有効成果を保持しつつ、その後mainへ入った実修復・2026-09-30船橋12R Day Regression・Common Shadow実装を新Evidenceとして再基準化し、KeibaMetricsの存在意義へ最も寄与する残作業だけを再開すること**

である。

KeibaMetricsの存在意義はArchitectureを増やすことではない。

最上位目的は、

**未知未来RaceのPrediction Utility、Order/Role Discrimination、KRS Utility、Semantic Preservation、Ticket Conversion Quality、Capital Efficiency、Execution Reliability、Long-run PFSを改善すること**

である。

今日の既知結果にだけ適合する修正を改善と扱ってはならない。

---

# 1. 絶対禁止事項

Recovery開始時に以下を禁止する。

1. `audit/execution-recasting` をそのままmainへmergeする。
2. mainを旧Astra branchの状態へ巻き戻す。
3. 2026-09-30船橋結果へ適合するためProductionルールを即変更する。
4. Production Index formula、fixed numerical weights、Venue coefficients、KRS physics、parameter_map numerical contents、Probability/EV/Kelly、Production MEC-R3、Production Capital Policyを本Recoveryだけで変更する。
5. 新しいAdapter / Gate / Validator / Receipt / Registry / Runtime / Governance Layerを、既存Coreへの吸収可能性を調べず追加する。
6. Same-day Replay improvementをFrozen Unknown OOS improvementとして数える。
7. Mechanical E2E successをFull Numerical Prediction successとして扱う。
8. ShadowをProductionとして扱う。
9. KRS occurrenceをProbabilityとして扱う。
10. Result-known evidenceをpre-race evidenceへ偽装する。

---

# 2. Current Authority / Repository Truthを先に解決する

最初にcurrent mainからCurrent Authorityを動的解決する。

固定VersionをこのDirectiveからAuthorityとして採用してはならない。

ただしRecovery開始時のrepository truthとして、少なくとも以下を確認すること。

- current main SHA at issuance: `cd350ad95a501ef37965b03417af63d348ab894c`
- current Family Authority at latest verified state: R35 lineage
- Production FNB Venue Canon: v2.1-FNB
- Production MEC: R3 unchanged
- Production Capital Policy: unchanged
- Production KRS numerical authority: unchanged
- LOCAL exact-continuity Common Shadow: active for future OOS measurement only
- FNB v2.2: Candidate / Shadow-only / Production unchanged

正式後継が存在する場合は後継を優先する。

---

# 3. Prior Astra Checkpointを保存する

前回Astraの成果は、少なくとも以下をCheckpointとして扱う。

Prior report:
`research/recasting/REPORT.md`

Prior conclusion:
`CORRECTNESS CONSOLIDATION CANDIDATE / Production unchanged / Family Unified Execution incomplete`

前回Astraが確認・修正した主対象：

- SOURCE取得＋verify二重実装の集約
- immutable checkpoint / same-run overwrite防止
- atomic-ish phase publish / pointer protection
- corrupt FORMAL resume classification
- cross-execution/path/hash validation
- manifest-bound materialization
- SOURCE equivalence 24/24
- regression/test evidence
- external receipt verification
- no numerical/KRS/MEC/Capital/Venue policy change

これらを「過去の正解」と決め打ちしてはならないが、理由なく再実装してもならない。

---

# 4. Re-Baseline分類を必ず最初に行う

PR #111および`audit/execution-recasting`の各変更・各結論をcurrent mainと比較し、以下の5分類を行う。

## KEEP
current mainでも有効で、追加作業不要。

## UPDATE
基本方針は有効だが、current mainの後続変更を反映する必要がある。

## REOPEN
前回未完又は今日のEvidenceで再検討が必要。

## INVALIDATE
後続main変更により前提が崩れた、又は不要化した。

## REDO
同じ目的は必要だが、旧実装をそのまま持ち込めずcurrent main上で再実装が必要。

このLedgerを作成する前にコード変更を開始してはならない。

特にPR #111はcurrent mainに対し、
**2 commits ahead / 56 commits behind**
で分岐している。

したがってPR #111を丸ごとmergeしてはならない。

---

# 5. 前回Astra後にmainへ入った重要Delta

Astraは以下を新しいRepository Truth / Delta Evidenceとして調査すること。

## A. Single Entry Lifecycle correctness consolidation

前回Astra作業後、main側では実Race failureを用いて以下のCorrectness修復が入っている。

- Frozen Staticの明示statusから重複freeze declarationをCanonicalize
- Signed Official SOURCEによる安全な軽微post-time reconciliation
- Frozen Staticからduplicate Final Prediction Package carrierをlosslessに導出
- Production Prediction ranking / rolesを変更しない
- large post-time drift / cutoff violationはFail-Closed維持

これらを旧Astra変更と競合・重複させない。

## B. R6 actual lifecycle regression

2026-09-29船橋R6の既存結果前Signed SOURCEを用いたPOST-START / NOT-OOS回帰で、

SOURCE checkpoint
→ FORMAL
→ PRE_KRS signed PASS
→ KRS actual 5,000
→ MEC-R3
→ Capital
→ Signed FINAL PASS

まで完走した。

これはMechanical EvidenceでありUnknown-Future Evidenceではない。

## C. Common Exact Continuity Forward Shadow

mainへmerge済み：

`KM-COMMON-EXACT-CONTINUITY-FORWARD-SHADOW-20260930-R1`

merge commit:
`7f5500fdb3c41a2e723df67ba12c649f18a2e513`

Tracker:
`KM-COMMON-EXACT-CONTINUITY-OOS-TRACKER-v1.0-20260930`

current state:
`0 / 30 eligible races`

Activation:
`2026-10-01T00:00:00+09:00`

Production effect:
`NONE`

Measurement arms:
- CONTINUITY_ALL
- KRS_TOP1
- KRS_TOP3
- KRS_TOP5

Signed FINALへshadow SHA / basis SHAをresult前bindingし、result後にForward OOS settlementする。

Automatic promotionは禁止。

## D. Concentration-aware Capital Width

現在は、

`SHADOW-HOLD / DIAGNOSTIC-FREEZE-ONLY / NOT-OOS-ARM`

である。

理由：
9/30結果から決定論的thresholdを後付けで作らないため。

Astraは結果に合わせたCapital thresholdを発明してはならない。

## E. FNB Venue Candidate

`KM-LOCAL-FNB-v2.2-CANDIDATE-20260930-R1`

Status:
`CANDIDATE / SHADOW-ONLY / NON-PRODUCTION / NON-NUMERICAL / BEHAVIOR-CHANGING / PROMOTION-HOLD`

Production FNB v2.1は変更なし。

Venue側仮説：
- 2YO low-observation Alternative P2 Reachability
- Distance Return × Class Context W Reachability
- Layoff Historical Ceiling vs Current State
- Class Exposure / Class Relief Translation

Exact Conversion / CapitalはVenue ownershipへ戻していない。

---

# 6. 2026-09-30 船橋Day RegressionをDelta Evidenceとして使う

Known-result Day Regression summary:

- races: 12
- Frozen Recommendation investment: 65,200 JPY
- return: 35,300 JPY
- PFS: 54.14%
- Actual Purchase PFS: NOT VERIFIED

First Material Failure counts:

- Prediction / Role: 2 races
- Conversion: 8 races
- Capital: 2 races

反復Exact Continuity Failure：

- R04
- R05
- R07
- R08
- R09
- R11
- R12

共通パターン：

Material/Purchased Ordered Pair
+ Active P3
+ correct exact present in Semantic Universe
→ SEMANTIC_ONLY
→ purchase_authority=false

Positive Control:
R10では正しいExactがCORE Materializedされ実際に的中。

KRS Strong Evidence:
R11ではKRSが実Exact 7→2→8をpre-result Top-1 occurrenceとして示したがProduction Ticketへ接続されなかった。

Capital contrast:
- あるRaceではTAILが利益を救済
- あるRaceではTAILが利益を破壊
- よって blanket TAIL deletionは不支持
- Semantic CoverageとCapital Widthを分離すべきEvidenceがある

重要：
この12Rは同一Venue・同一Dayの相関したknown-result cohortであり、
**7 Exact failures = 7 independent OOS cases**
とは扱わない。

---

# 7. 今日のEvidenceから何を変えてよいか

## Immediate Correctness
既存Contract矛盾、transport bug、identity bug、immutable violation等でPredictive policyを変えないものは、Evidenceが十分なら修正可。

## Candidate / Shadow
Behavior-changing policyはShadowへ送る。

## Production
Known-result dayだけでは変更禁止。

特に、

Exact Continuity
KRS-actionable Exact re-audit
Concentration-aware Capital Width
Venue Reachability hypotheses

はProduction即変更禁止。

---

# 8. Recovery後の優先順位

前回AstraのRemaining Risksと今日のDeltaを合わせ、次の順序で再開する。

## Priority 1 — End-to-End Lifecycle Ownership

以下を一件のRace lineageとして俯瞰する。

Request
→ Authority
→ SOURCE
→ Runner Universe
→ Evidence
→ Numerical
→ Prediction
→ Static Freeze
→ PRE_KRS
→ KRS
→ Semantic Universe
→ MEC
→ Capital
→ Ticket
→ Signed FINAL
→ RESULT
→ Settlement
→ Learning

前回Astraが未完とした、

- SOURCE→Prediction→Static Freeze handoff
- RESULT / Settlement / Learningの親統合

をREOPEN候補として評価する。

ただし統合のために新サービスを増やしてはならない。

## Priority 2 — Duplicate Semantic Carriers / Manual Handoffs

同一意味を複数Carrierへ再記述させる箇所を棚卸しする。

原則：

One Semantic Fact
→ One Canonical Authority
→ Derived Views

人間又はVenue Chatが同じ意味を二重入力する構造を削減する。

## Priority 3 — Common Exact Conversion Measurement

既にmainでForward Shadowが開始されている。

AstraはこのShadowを作り直さない。

必要なら観測性、binding、tracker completeness、settlement correctnessを改善するが、0/30 trackerの意味を変えない。

## Priority 4 — Capital Width Research

現在SHADOW-HOLD。

決定論的pre-race activation functionがEvidenceから正当化できるまでProduction/Forward OOS arm化しない。

## Priority 5 — Architecture Reduction

Workflow 160件、component inventory等を再評価する。

ただし「数を減らすこと」が目的ではない。

Quality維持又は向上が証明できる削減だけを行う。

---

# 9. Genuine Unknown-Future Acceptance

前回Astraの最大未完項目である。

Replay、synthetic future date、post-start executionを代用してはならない。

実在の未発走Raceについて、結果情報なしで、

Request
→ Fresh Official SOURCE
→ Prediction
→ Static Freeze
→ PRE_KRS
→ KRS
→ Semantic Universe
→ MEC
→ Capital
→ Signed FINAL

がdeadline前に閉じることを確認する。

その後、

Official RESULT
→ Settlement
→ Learning

まで同一lineageで閉じる。

Mechanical SuccessとPrediction SuccessとPFS Successは別評価する。

---

# 10. Numerical Authority

LOCAL numerical authorityがNOT_READYである場合、

TerminalizationをActual Calculationとして扱ってはならない。

AstraはExecution統合の都合で数値式を捏造してはならない。

Numerical closureは別Owner / separate candidateとして扱う。

---

# 11. Architecture Decision Rule

新Component追加前に必ず：

DELETE
→ MERGE
→ ABSORB INTO EXISTING CORE
→ SIMPLIFY
→ DEMOTE TO COMPATIBILITY
→ REPLACE
→ ADD

の順で検討する。

既存Single Entry Orchestratorが責務を安全に吸収できるなら、新Orchestratorを作らない。

既存Runtime endpointがStage Executorとして十分なら、新Runtimeを作らない。

Legacy endpointを削除できない場合はCanonical ParentとCompatibility Entryを明確に分離する。

---

# 12. Required Recovery Deliverables

AstraはRecovery開始後、以下を順に提出する。

## A. Delta Re-Baseline Ledger
PR #111 / prior Astra workを
KEEP / UPDATE / REOPEN / INVALIDATE / REDO
へ分類。

## B. Current E2E Map
current main基準。

## C. Remaining Seam Map
manual handoff / duplicate carrier / duplicate parent / compatibility path。

## D. Today's Evidence Impact Map
9/30 Day Regressionがどの既存仮説を
SUPPORT / CONTRADICT / NO-IMPACT
したか。

## E. Updated Consolidation Plan
新Architectureを増やす前に削除・吸収を優先。

## F. Actual Code Repair
必要なものだけ。

## G. Regression / Equivalence
Production Prediction / KRS / MEC / Capital非意図変更を検査。

## H. Unknown-Future Acceptance
実在未発走Race。

## I. Architecture Reduction Report
Before / After。

## J. Remaining Risk
未完を正直に残す。

---

# 13. Completion判定

以下を満たさない限り、
`FAMILY UNIFIED EXECUTION COMPLETE`
と宣言してはならない。

1. Current mainからのre-baseline完了。
2. PR #111旧変更の扱いが全件分類済み。
3. Canonical lifecycle parentが明確。
4. SOURCE→Prediction→Staticの責務が明確。
5. FINAL→RESULT→Settlement→Learningの責務が明確。
6. Duplicate carrier / manual handoffが合理的最小化。
7. Production behavior preservation tests PASS。
8. Existing Shadow/OOS trackersを破壊していない。
9. Genuine Unknown-Future pre-race acceptance PASS。
10. Post-result lifecycle closure PASS。
11. Numerical Authority不足を偽装していない。
12. No unintended Production MEC/Capital/KRS/Venue change。

---

# 14. Recoveryの最終原則

今回やるべきことは、

**Astraの前回作業を捨てて再出発することではない。**

また、

**古いAstra branchへ戻って続きを書くことでもない。**

current mainを新しいRealityとし、

**前回の有効成果を選択的に継承し、今日の実Race Evidenceで再評価し、KeibaMetricsの未知未来予測とPFS改善へ本当に必要な残作業だけを続行すること**

である。

今日の結果に合わせてArchitectureを作るな。

今日の結果から、
「次の未知未来で何を反証可能に測るべきか」
を学べ。

最終評価は、

Less Architecture
+ Less Duplication
+ Fewer Manual Handoffs
+ Same or Better Prediction Behavior
+ Same or Better Execution Integrity
+ Better Conversion Quality
+ Better Capital Efficiency
+ Strict Temporal Truthfulness
+ Genuine Unknown-Future Evidence

で行う。

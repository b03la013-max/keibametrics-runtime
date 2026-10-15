# ケイバメトリクスFamily Cross-Family Maturity Promotion正式統合 R1

制定日：2026-09-28  
Profile：KM-FAMILY-CROSS-FAMILY-MATURITY-PROMOTION-20260928-R1  
Status：ACTIVE / FAMILY-WIDE / PROMOTION-GOVERNANCE / NON-NUMERICAL / NO-AUTO-PROMOTION / FAIL-CLOSED

## 0. 最上位目的

Family共通化の目的はArchitectureを増やすことではない。JRA・LOCAL・BAN・Venueで成熟した知見のうち、未知未来Prediction Utility、変換品質、Capital効率、再現可能性をFamily全体で改善し得る**移植可能な契約**だけを共通化する。

「中央で成熟した」こと自体は昇格理由ではない。中央で成立した数値、Source Adapter、parameter_map、固定閾値、Venue機構を他Familyへコピーしてはならない。

## 1. Authorityの四層

1. COMMON_FAMILY：Current Authority、Formal Lifecycle、Runner Universe protocol、Required Index Manifest protocol、Temporal/Receipt、KRS transport、Semantic Universe、MEC、Ticket、Capital、Settlement、Measurement、Learning、Promotion。
2. FAMILY_SPECIFIC：JRA/LOCAL/BANごとのSource Adapter、Source Registry、Evidence Rule Registry、Numerical Mapping/Materializer、KRS Input Adapter、parameter_map、Family Prediction Model。
3. VENUE_SPECIFIC：Course Geometry、距離解釈、Track State、Position/Progression/Friction、Venue Evidence Interpretation、Venue Regression。
4. CANDIDATE_SHADOW：未昇格数値、実験parameter、実験KRS Utility、実験MEC、未証明Venue仮説。

一つのProduction責務に複数Ownerを置かない。

## 2. 中央からFamilyへ昇格してよいもの

- Authority Resolution
- Formal Full Lifecycle
- Full Runner Universeの完全性契約
- Required Index Manifestの完全性契約
- TerminalizationとActual Numerical Calculationの分離
- Evidence/Index Provenanceの追跡契約
- Source/Static/FinalのTemporal Freeze
- PRE_KRS/KRS/FINAL/RESULT Receipt検証
- Candidate/Shadow隔離
- Prediction UtilityとExecution Conformanceの分離
- First Material FailureのOwner Routing
- Prequential Learning
- OOS Promotion Governance
- Measurement定義・Failure Code・Test Harnessの共通Schema

これらは意味がFamilyを跨いでも変わらないため、Commonへ昇格可能である。

## 3. 直接移植禁止

次はFamily/Venue固有Authorityへ残す。

- JRA/LOCAL/BANのSource Adapter
- FamilyごとのEvidence Rule Registry
- Numerical Mapping、Weight、Threshold
- parameter_map
- KRS Input AdapterのFamily固有変換
- 固定Venue bonus
- Course/Distance/GCI固有知識
- 単一Venueでのみ反復したMechanism
- Candidate/Shadowの未昇格数値

Interfaceを共通化してもImplementationを混同しない。

## 4. Promotion Class

### C0 Schema / Interface
非行動変更。Cross-Family semantic equivalence、Regression、Authority collision absenceで昇格可能。

### C1 Execution Correctness
Fail-Closed、Receipt、Temporal、Universe、Provenance等。Owning Family acceptance、独立性確認又は第二Family互換Acceptance、negative testを要求する。数値Predictionを変えない限り未知OOSは必須ではない。

### C2 Decision Policy
MEC、Ticket、Capital、KRS rescue等。Pre-result Freeze、Unknown OOS、Robust Utility/PFS、明示Promotion Declarationが必須。

### C3 Numerical Model
Weight、Threshold、parameter、mapping coefficient等。Family固有較正、Family固有Unknown OOS、Leakage監査、明示Promotionが必須。他Familyへの直接Production昇格は禁止。

## 5. Duplicate Architecture Reduction

共通責務がVenue旧条項に残っている場合、削除せずCompatibility Source / Regression Fixtureへ降格できる。ただしCurrent Production Authorityを二重にしない。

新しいCommon規程を追加する前に、DELETE → MERGE → SIMPLIFY → REPLACE → ADDの順に検討する。

## 6. Formal Lifecycleとの接続

全FamilyのFORMAL-PRE-RACEは `KM-FAMILY-FORMAL-LIFECYCLE-CONTRACT-20260928-R1` に従う。Family/VenueはLifecycleの意味を上書きせず、自分が所有するStageのImplementationだけを提供する。

## 7. Production Freeze

本R1は以下を変更しない。

- 既存Production指数式・Weight
- KRS Engine physics
- Production parameter_map
- MEC-R3
- Capital Policy
- Venue Production Canon
- Candidate/ShadowのProduction status

## 8. 昇格の最終原則

**Commonへ上げるのは「中央のやり方」ではなく「Familyを跨いでも同じ意味を持つ契約」である。**
数値・Source実装・Venue因果はOwnerへ残し、未知未来に影響するPolicy変更はFrozen OOSなしに昇格させない。


## 9. 個人開発の限定Executionリリース承認方式（Owner採用指示記録・配置承認待ち）

この追記は、Owner本人が本追記のSHAと対象コードSHAを指定して採用を明示するまで効力を持たない。GitHubへの保存、AIによる監査、CI成功、Ownerが単独開発者であるという事実だけでは採用としない。従来の個別リリース条件を維持する。

### 9.1 適用範囲と承認主体

C0/C1の非予測・非数値Correctness修復について、既存第4節の証拠条件をすべて満たす場合、Owner本人による実際の差分・リスク確認と明示リリース承認を人間の承認方式として選択できる。この方式は独立Human Reviewではない。C1のproof of implementation independenceは人間の独立性とは別の条件であり、削除しない。既存GitHub保護・Required Checks・上位規程の独立承認要求があれば、この方式で上書きしない。

PRにDiscovery/Scheduling/Activationが含まれる場合、それをC1として一括承認しない。対象日・Venue・Race・送信先・Payload・時刻・費用制御・回数制御の運用変更として別途明示承認する。今回の対象はPR280 exact HEAD 655530735f24cce78605dd1bd34843bdb2ea253d、LOCAL KAW Phase B 1Raceのみ。Family全体への一般Activation権限は与えない。

### 9.2 必須証拠

- 全変更パスのCorrectness/運用Scheduling/予測Behavior/Security/Cost分類。分類不明・予測Behavior混入はHOLD。
- 対象exact HEAD、最新main、差分、必要な全CI、既存回帰、失敗前後の証拠。新HEADではCIと審査を再確認。
- Owning Family acceptance、第二Family互換性又は実装独立性の証明、negative tests、Authority collision absence。
- Production Engine/parameter_map/Signer/Trust Anchor/MEC/Capital/数値式/Venue Canonの不変SHAと実Runtime Fingerprint。
- 配置対象、既知の旧Deployment/startCommand/Gateway、受付停止条件、Rollback手順と復旧後検証。
- 共有Workspaceの既存費用上限の実効確認。Dispatch回数は金額上限の代替にしない。追加OpenAI API有料要求0、上限引上げ・新課金・購入なし。
- Owner本人の承認記録（チャット原文又は本人のGitHub操作）を改変せず参照し、AIがOwner/Reviewerとして承認を作成しない。

### 9.3 段階別の明示承認

1. 本方式の採用：Ownerは従来のPR280独立Human Review必須条件を、この限定Owner承認方式に変更することを明示する。対象追記SHA、対象コードSHA、例外範囲、残存リスクを記録する。
2. Merge：Owner本人が差分・証拠・リスクを確認し、exact HEADのMergeを明示承認する。以前の条件付き指示は新方式採用の証拠には流用しない。
3. Deploy：既存Runtimeへのwrapper限定配置とGateway整合を別の承認項目として記録する。Merge成功だけでは配備を許可しない。
4. Activation：限定Race/時刻/送信先/Payload/既存費用上限/最大回数を別の承認項目として記録する。既存Dispatcherのdated approvalと環境ゲートを用い、新Registry/Validator/Workflowを追加しない。

同一Ownerメッセージで複数項目を明示承認できるが、承認範囲は区別して記録する。コード・対象日・Race・上限・配備範囲の変更時は、該当承認を再確認する。AIのコード監査は補助証拠としてのみ記録し、独立レビュー欄はNOT_PERFORMEDのままとする。

### 9.4 除外と停止

C2 Decision Policy/C3 Numerical Model、予測数値・KRS Physics・MEC・Capital変更、Numericalの新たな予測消費、AKI等Shadow昇格、他Venue/JRA/BAN/Phase C/Dへの拡張は対象外。既存OOS/Human Review/明示Authority更新条件を維持する。

独立レビューが上位条件として必要な変更は、Ownerが選任する外部人間の正規レビュー、又はその上位条件自体の正式改定が成立するまでHOLD。無限Retry、曖昧応答後再送、時刻遡及FINAL、既存Artifact/OOS改変は禁止。

配置後はHealth/Gateway/Canary/既存Receipt Verify/既存FINAL Read-backを実測し、どれか不成立なら受付HOLD・既知配置へRollbackする。真正未来FINAL・Delivery・結果Closed Loopは別々に検証し、CI又は過去ReplayをLIVE完了としない。

### 9.5 PR280への採用指示記録（2026-10-15 23:27 JST）

Ownerは本チャットの「PR #280 個人開発限定承認方式の正式採用・Production導入依頼」で、PR282 commit 7b92b83eに保存した方式の正式化を指示した。対象コードは655530735f24cce78605dd1bd34843bdb2ea253d、参照patch SHAは92b407588feecc1c7365d9d43b0d2fe828833e8fcfe5982ab7a86e5eb7601db0。このOwner指示を方式採用・正本反映の根拠として記録し、独立Human Reviewerの探索を必要工程にしない。

ただし同指示は「Owner本人による差分・リスク確認が必要な場合、その確認をWork自身が代行したと偽装してはいけません」と明記している。Owner本人が差分・リスクを確認済みという申告はまだ得られていない。従って9.3の対象コードへのOwner本人の実レビュー・リリース承認条件は未充足であり、PR280 Merge、wrapper Deploy、Phase B ActivationはHOLD。方式採用記録とコードのリリース承認を混同しない。

本追記はPR282上の正本反映差分であり、main未反映。既存Current Authority pointer/Profile/Dispatcherの実行ゲートを変更せず、Production効力・成功を自動付与しない。

### 9.6 Owner本人確認と実Merge記録（2026-10-15 23:42 JST）

Owner本人は対象HEADの実質差分を確認済みと明言しMergeを承認した。第9.5節のOwner本人確認HOLDはこの時点で解消した。独立Human Reviewを実施したという意味ではない。HEAD655530735f24cce78605dd1bd34843bdb2ea253dに対しCI14/14を再照合し、Merge552700f26a4b1b8c321a8b5b2321a1c87df41237を実行した（2026-10-15T14:42:53Z）。

その後wrapper-only startCommand1件をRailway既存productionへステージしたが、accept-deployが「Cancelled — the user did not approve this action. No changes were made.」を返した。Deploy/Activationは未実行、稼働中Runtime/Gatewayは旧まま。別経路での適用を試みない。mainへの本Governance追記は未実施で、Owner承認原文と実操作記録をPR282に保存する。

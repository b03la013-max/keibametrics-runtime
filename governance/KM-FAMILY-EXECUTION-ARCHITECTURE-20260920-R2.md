# ケイバメトリクスFamily 実行Architecture正式統合改定 R2

制定日：2026-09-20
制定主体：ケイバメトリクス第五司令部
Profile：KM-FAMILY-EXECUTION-ARCHITECTURE-20260920-R2
Predecessor：KM-FAMILY-MANDATORY-FULL-EXECUTION-20260920-R1
Status：ACTIVE / FAMILY-WIDE / PRODUCTION-EXECUTION-OVERLAY / NON-NUMERICAL / FAIL-CLOSED / EXTERNAL-RECEIPT-REQUIRED

## 1. 改定目的
本R2はR1の完全指数・External KRS・Prediction-to-Ticket強制実行契約を、実在するGitHub／Railway／Base44／Scriptableへ正式接続する実装統合改定である。既存指数式、KRS-Engine v1.1.0、parameter_map、Venue固有予測理論、Production/Candidate/Shadow境界を数値変更しない。

## 2. 四系統の正式責務
### GitHub
Code / Specification Source of Truth。正式Runtimeコード、実行Profile、Schema、Validator、規程、SHAを永続管理する。現行Canonical repositoryは `b03la013-max/keibametrics-runtime` とする。GitHub revisionが特定不能な実装はProduction昇格証拠として不十分とする。

### Railway
Sole Formal Calculation & Execution Runtime Authority。現行実行先は Railway project `kmjrawitnessv061` / production、service `quorumprobe`、public domain `quorumprobe-production.up.railway.app`。PRE_KRS、KRS、FINAL、RESULT、VERIFYを担う。基礎指数・KRS・Ticket/FINALの正式実行証拠はRailway外部Receiptで確認する。

### Base44
Formal Execution Orchestrator / Console / Receipt Gate。App `KeibaMetrics Console` (`6aabb8079803485e24ee0259`) はRailwayを順番通り駆動し、Required Index Manifest、Gate、Ticket Decision、Execution Session、Receiptを保存・表示する。Base44内の独自指数式でRailway計算を代替しない。

### Scriptable
Optional Input Acquisition / Structuring Adapter。iPhone上のコピー情報等を構造化して入力へ渡す補助層。KRS、FINAL、指数Authorityを持たない。Scriptableを使わない公式・手入力経路も許容するが、Base44→Railway正式実行路は迂回不可。

## 3. Family共通正式パイプライン
CANON_RESOLVE
→ FULL_RUNNER_UNIVERSE
→ REQUIRED_INDEX_MANIFEST_BUILD
→ ALL_REQUIRED_INDEX_TERMINAL
→ STATIC_FREEZE
→ BASE44_ORCHESTRATION
→ RAILWAY_PRE_KRS
→ PRE_KRS_RECEIPT_VERIFY
→ RAILWAY_KRS_EXECUTE
→ KRS_RECEIPT_VERIFY
→ W/P2/P3_FINAL_PREDICTION
→ HEAD/PAIR/THIRD/TRIO/EXACT_CLOSURE
→ TICKET_CONSTRUCTION
→ CAPITAL_COMPILE
→ CANONICAL_RENDERED_RECONCILIATION
→ RAILWAY_FINAL
→ FINAL_RECEIPT_VERIFY
→ USER_VISIBLE_FORMAL_OUTPUT
→ RESULT
→ RESULT_RECEIPT_VERIFY
→ REFLECTION/KMS

この順序を逆転、短絡、省略してはならない。

## 4. Required Index Hard Gate
全Runner×全Required Indexについて次のTerminal statusのみ許可する。
- CALCULATED
- RULED-NEUTRAL
- RULED-HOLD
- NOT-APPLICABLE

次を一件でも含む場合はINDEX-BLOCKEDとしてPRE_KRS禁止。
- UNRESOLVED
- NOT_CALCULATED
- MISSING_REQUIRED_INDEX
- SPEC-MISSING
- RUNNER-MISSING

欠損を推測値で埋めてTerminal化してはならない。各Family/Venue Production正本の欠損処理に従う。

## 5. Family Index Profile
地方平地、JRA中央、ばんえいは別Manifestを使用し、Family間で数式を流用しない。Venue固有Required moduleをManifestへ追加する。Required Setの具体はR1および各Family現行Production正本に従う。

## 6. PRE_KRS Gate
PRE_KRS PASSには最低限、Canon Resolution、Full Runner Universe、Required Index Manifest terminalization、Static Snapshot、source/profile revision lineageが必要。PRE_KRS Receiptは同一race_id/snapshot_idに紐づき、署名・hash検証可能でなければKRSへ進めない。

## 7. KRS Gate
KRSはPRE_KRS VERIFIED-PASS後のみ起動する。通常戦SIM-STD 5,000、高不確実性戦SIM-HIGH 20,000を現行規程に従って使用する。actual_run_count、requested_run_count、seed、engine_version、engine_sha256、parameter_map_version/hash、input/output hashをReceiptへ保存する。未較正Supportを勝率・EVと呼ばない。

## 8. Prediction-to-Ticket Gate
KRS後、StaticとKRSの責任分界を維持してW/P2/P3を確定し、Head、Ordered Pair、Pair-local Third、Trio、Exactを閉包する。全発売券種を候補生成対象にできるが、全券種購入を強制しない。Ticket DecisionはPURCHASED / BUDGET-NONSELECTED / STRUCTURAL-INELIGIBLE / EVIDENCE-RANKED-LOWER / NOT-APPLICABLE / NO-BET等を理由付きで保存する。

## 9. FINAL Gate
FINAL PASSにはKRS実行Receipt、Final Prediction Package、Ticket Construction、Capital、Canonical/Rendered reconciliation、Final Freeze timestampが必要。いずれか欠損ならFINAL-BLOCKED。FINAL Receiptは署名/hash Verify済みでなければFORMAL-FULL-EXTERNALと表示しない。

## 10. GitHub／Railway整合
GitHubを仕様・コード正本、Railwayを実行Authorityとし、Runtime revisionは可能な限りGit commit/release/profile hashへ接続する。現Railway serviceが環境変数blob起動である間は、runtime blob SHAとGitHub canonical revisionの対応表を保存し、対応不能ならSOURCE-LINEAGE-PARTIALと表示する。

## 11. Base44実装必須Entity
FamilyExecutionPolicy / RequiredIndexManifest / RequiredIndexItem / ExecutionPolicyGate / TicketDecision / SourceRevision / ExecutionRun / ExecutionReceipt / ExecutionSession / ExecutionArtifact / ExecutionAuditを正式保存系とする。

## 12. Fail-Closed
Base44障害、Railway障害、Receipt検証不能、Required index未完、KRS未実行、Ticket未完、FINAL未検証時は分析自体を禁止しない。ただしFORMAL-FULL、KRS-EXECUTED、FINAL-PASS、正式買い目を名乗らない。表示はANALYSIS-ONLY / EXECUTION-NOT-PROVEN / FINAL-BLOCKED等とする。

## 13. Venue継承
全Venueは本R2を共通Execution Overlayとして自動継承する。Venue正本へ同一条項を重複増築しない。VenueはPrediction Profileに専念し、実行・Ticket/Capital/Receipt責務はFamily共通層へ返す。

## 14. 受入試験
Production受入は少なくとも1つの新規レースで、全指数Terminal→PRE_KRS VERIFIED→KRS actual_run_count成立→Prediction→全券種Decision→FINAL VERIFIEDをEnd-to-Endで完走して証明する。過去結果や手作業Receiptを受入証明へ代用しない。

## 15. 現行Infrastructure登録
- Base44 app: 6aabb8079803485e24ee0259 / KeibaMetrics Console
- Railway project: b83c61e2-1555-4944-8f3f-68f269931185 / kmjrawitnessv061
- Railway environment: 8af4a037-975f-4c15-8005-7bcde494022b / production
- Railway service: 3075b11b-a996-4d81-a76b-2df66f2561a0 / quorumprobe
- Runtime domain: quorumprobe-production.up.railway.app
- GitHub canonical repo: b03la013-max/keibametrics-runtime
- R1 Constitution SHA256: 39ef46abb09c65bdfa9c7f6464a9b02094436ac6645c2199f86adbf13e5baf26

## 16. 最終原則
予測を出すことより、正本どおり完全に実行したことを証明することを先にする。ただしFormal Integrity自体を目的化せず、完全計算→KRS→予測→買い目という本来の予測効用を確実に実行するためのFail-Closedである。

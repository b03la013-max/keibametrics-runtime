# JRA P0 continuation: RESULT publication and October18 preparation

2026-10-17昼JST。修復前の新潟5R RESULT Run38999590505は署名検証/Review/Learning計算を通過後、main同時更新によるpush拒否で終了した。署名失敗やPFS0ではない。実ログと元hashの照合は `result_recovery.json`。

既存保存ヘルパーを5回上限で再利用し、JRA RESULTモードだけ4種類の派生集計を再構築する。LOCAL既定の対象集合は変えない。per-race記録/署名データの競合は停止し、force pushしない。検証済み原request/envelopeはReview前に保存し、失敗時もArtifactへ保持する。新入口/新署名器/Deploy/数値Policyなし。

元RESULT requestと署名FINALからReview/Learning/KRS OOS/Fast Reflection/MEC Shadow精算を再計算し、元Workflowの5つのhashすべてと一致した。未保存のraw RESULT envelopeは復元していない。再署名せず、独立署名再検証済み・完全Closed Loopとは扱わない。PAPER0円、PFS=null、購入UNVERIFIED。集計は後続既存処理で再構築する。

固定36件は全登録hash/plan/cohort一致、予定450頭/9000セル、当日の実セル0。公式ページを再確認し、今回の再取得では35Race433頭の番号/馬名と発走時刻が一致。京都11Rはこの取得経路でアクセス不可、直前の公式17頭観測を維持するが今回の再取得成功には含めない。出所/取得時刻/表示excerpt hashは `official_recheck_36.json`。これはraw HTTP HTMLのhashや当日のSigned SOURCEではない。jockey判定がnullなら未確認であり変更・取消と断定しない。取消/除外を推測しない。

東京7Rの原FINALはPRE_KRS/KRS/FINAL Ed25519・署名payload・immutable hashを固定公開鍵で独立再検証。11頭のBVIは既存式のweight/category/coverageから再計算一致、Static実行proofと同一署名FINALへの結合を確認。DCR_ONLY0、実測11。KRS5000、Full20 220/220、19点1900円。正式券面はRecommendationであり実購入ではない。GitHub公開12:37:28 JSTは人の受領ACKと別。

既存PR286/287/288/289/290/291/293/295/296/298/299/300はMerge済み。PR297は未Mergeの観測証拠として読む。最新AuthorityはR51 effective2026-10-12T05:05:14.161540Z、Static/AKIはOwner承認・UNVALIDATED。新408走は研究隔離、旧7件と現行Forward OOS0/30を混ぜない。数値/BVI/AKI/MEC/Capital/parameter_map/Signer変更なし。

Railwayの既存KRS/Calculatorは同一SUCCESS Deployment、stagedなし。app Git SHAは公開metadataで未証明。保存startCommand/liveの不整合は残り、再起動/Deployしない。今回の直接health再取得は環境/取得経路エラーで失敗したため、過去READYを現在healthの実測として再掲しない。新潟8Rは修復後Workerから自律受付・FINAL状態まで進んでいる。

Oct18は全36件のIntent/Signed SOURCE/Full20/Static/AKI/PRE_KRS/KRS/MEC/Capital/FINAL/Delivery/RESULT/Settlement/Learningが未実行。事前登録36/36を本番成功に数えない。LIVE ACCEPTANCE PENDING、Delivery人のACK未証明、Deployment SHA未証明。総合P0-RECOVERY-PARTIAL。

ローカルの実Git競合・原bytes維持・別Race併存・同Race競合HOLD・上限試験と既存scratch互換性7件PASS。修復前2FAIL/3PASS。完全repoのCIは正確な最新HEADで確認する。Rollbackは本PRコード/Workflow差分のみrevertし、真正なSOURCE/FINAL/RESULT/回復したper-race記録は削除・書換えしない。

# JRA 2026-10-18 P0 execution readiness and correctness

対象は東京・京都・新潟の公式36レース。公式Discoveryと各レースの事前受付を保存した。これは実SOURCE、Static、KRS、FINALの完了記録ではない。宣言頭数の予定総数450、Full20予定9,000セル、実計算0セル。Active Runner Universeは当日の新鮮な署名SOURCEで確定する。

## Current authority and actual runtime

調査基点mainは7206b76a82343b28334adcbc4dcecf7beff51a63。PR282は承認された8c0f1ad9…からMerge済み。修復を重複実装せず、mainの厳密な永続化ヘルパーを再利用する。最新effective manifestを実際に再解決してR51を確認。JRA Static/AKIはOWNER_AUTHORIZED/UNVALIDATED。新馬は既存R51 PAPER権限を維持する。

Calculatorと外部KRSの実healthはHTTP200/READY。Engine/parameter_map/signerはruntime_health.jsonを参照。RailwayのDeployment IDは取得できたが、配置されたコードのgit SHAは公開されたread-only情報では確定できない。Workflow SHAとの一致を装わない。quorumprobeの保存startCommandと稼働中healthに不整合があるため、再起動・redeployは行っていない。起動設定修正は、実Deploymentの設定スナップショット確認後に扱う。

全Open PRのメタデータをopen_pr_inventory.jsonに保存。LOCAL研究PR262/265/276、別研究285等をJRA ProductionへMergeしない。PR279等の未Merge候補がCurrent Authorityになったとは扱わない。追加添付Central Rev.2も自身がCANDIDATE/Production Authorityなしと明記しており、JRA正式規程の上書きには使わない。

## Implemented behavior

- 事前受付は独立ディレクトリ。Race ID/Execution ID/20指数Manifest/Owner/予定時刻/固定cohortを結合し、ライブIntentやSOURCEを早期生成しない。cohortとplanと各登録をhash結合する。
- 自律DispatcherはAPI送信前にclaimをmainへ永続化する。応答不明時は記録を残して重複送信を停止し、他Raceを継続する。曖昧なclaimの再送には実Run/Intentとの照合が必要であり、根拠なく消去しない。
- 既存push start requestのrace_date/modeを読み、当日以外の起動を拒否する。新規受付transportは作らない。
- 公式発走時刻の変更は新しい公式day rowを採用し、元の事前受付時刻と照合記録を残す。固定分母は変更しない。
- SOURCEのPDF掲載集合と取消後Active集合を分離。PDFと公式詳細の全掲載馬identityが一致した後、公式取消・除外のみを除く。説明できない馬名・番号差異は拒否する。
- 前Raceの結果処理を既存独立Post-Result Workflowへ委譲し、予測Workerで結果取得・精算を待たない。個別の破損checkpointは他Raceを止めない。
- Single Entryは最初にmainの既存Signed FINALを検証して読み戻す。既存FINALがあればSOURCE/Static/KRS/FINALを再生成しない。
- Signed FINALのEd25519署名だけでなく、署名された買い目payloadと表示券面の一致を検証する。GitHubへ保存後、特定commitのFINALとtreeをHTTP読み戻しし、公開時刻の証拠を保存する。
- FINAL保存と公開処理を分離。公開で失敗しても正式署名証拠を残し、canonical summaryを常時uploadする。呼出側は計算の成立とWorkflow全体の終了状態を別々に記録する。
- 精算はboolean/文字列/非有限数/負の払戻を暗黙int変換しない。正常な0円は受理する。既存の同着・返還を単一配当で表現できない経路は引き続きHOLDし、0円の不的中に偽装しない。これら特殊精算の自動完走は本変更では未完成。

## Actual observations and completion boundary

過去2026-10-12の成功FINAL14件でDispatch記録→署名は455.4～781.7秒。成功例に偏った観測であり、全Raceの所要時間保証ではない。既存55～30分前の窓を維持する。地方の42.9～57.8秒をJRA保証に流用しない。

歴史FINAL24件を検査し、現形式23件で署名とticket payload bindingを確認。旧阪神9/21R10はimmutable hashがない旧形式なので拒否した。旧履歴を修正・再署名していない。

3場の公式出馬表PDFは調査時点でHTTP403。未公開・アクセス制御等の理由はUNKNOWN。追加の迂回取得や架空Runner補完は行わない。当日SOURCEで再取得・検証する。公式card自体は36Raceを確認済み。

Canonical GitHub公開とユーザー到達は別工程。availability receiptはHTTP読み戻しの証拠であり、ユーザー既読・ChatGPT即時Pushを証明しない。ChatGPTへ全Raceを即時Pushする接続は確認できていない。user_delivery_verifiedは証拠がない限りfalseとする。実購入はUNVERIFIED。発走後の新規FINALを事前予測としない。

予測式、Venue係数、AKI閾値、MEC/Capital、KRS parameter_mapは変更しない。新しい予測選択Policy、疑似EV/Kelly、未知未来の収益改善を宣言しない。Static単独/KRS増分、Winner migration、Head-local P2、Pair-conditioned Third、Equal-Budget/Equal-Ticket、Drawdown、NO-BET機会損失は既存Frozen Evidence/Forward OOSと分離して比較する。

## Verification and operation

regression.xmlには受付、送信不明、個別障害分離、時刻変更、取消・除外、公開と到達の分離、署名payload改ざん、精算数値、既存AKI/Single Entry/Checkpoint回帰の実行結果を保存。CI成功はProduction成功率ではない。

既存経路: race-dayの `runtime/jra_autopilot_start_requests/*.json` push → bounded Autopilot → official intent resolver → Formal Single Entry → Signed SOURCE/Full20/Static → canonical Formal/KRS/AKI/MEC/Capital/FINAL → canonical publication → 独立RESULT/Settlement/Learning。Schedulerは予備。ChatGPT側の時限確認も起動遅延・通知遅延の可能性があり、リアルタイム到達保証の代替とはしない。

当日、固定cohort 36を分母に受付・外部KRS・FINAL公開・ユーザー到達・Learningを別々に集計する。正式FINALなしの推奨PFSはN/A。結果後データを事前予測に戻さない。最後のレースは16:30 JST予定。実結果と署名RESULT/Learningの成立を結果後監査で確認する。

## Risk and rollback

API応答不明のclaimは取りこぼし防止と二重実行防止のためHOLDする。根拠となるWorkflow Runが見つからなければ、実HTTP/CLI応答を調べたうえで限定再受付が必要になる。P0修復後もGitHub/公式SOURCE/Runtimeの障害による失敗をゼロと保証しない。

Rollbackは本PRのコードとWorkflow変更を限定revertする。既存・新規を問わず真正なSOURCE/FINAL/RESULT/登録証拠を削除・書換えしない。Runtime redeployは不要・未実施。追加OpenAI API要求0、購入0。既存Actionsの稼働は従来の時間窓内に限定する。

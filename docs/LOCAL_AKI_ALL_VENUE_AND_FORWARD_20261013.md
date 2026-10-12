# 全14場の実データ接続と未知未来PAPER起動

2026-10-13 JST。最新main d00238d6、Current Authority R51、LOCAL29指数/63 component rules、KRS20,000回、正本Runtime/Ed25519署名を使用。BAN・実購入・自動本番昇格を除外。

## 実行済みの範囲

全14平地場について、実公式資料→Signed SOURCE→全必要29指数/Provenance→列選定→PRE_KRS→外部KRS→Pair/Third→MEC→Capital=PAPER→Signed FINALまで、既存正式入口の明示的な研究経路を実行した。点数はレースの観測情報と列選定に従い変化する。全部を発走前予測や性能検証済みとは扱わない。

|分類|レース数|実証したこと|性能評価への扱い|
|---|---:|---|---|
|既存凍結SOURCEのReplay|4|川崎・大井2例・船橋の外部接続/公式RESULT/研究精算|過去研究のみ。OOS0|
|今回の事前登録済み発走前PAPER|5|門別・盛岡・川崎・金沢・名古屋のSOURCE/29指数/KRS/FINALを発走前凍結|結果未観測。現時点の評価済み未来OOS0|
|今回取得した過去ページの技術Replay|7|浦和・園田・姫路・笠松・高知・佐賀・水沢の実入力接続|SOURCEは結果後取得。補助資料のlookaheadリスクあり。PFS検証/未来OOSへ加算禁止|

成功署名KRSの確定実回数は16ケース×20,000=320,000回。浦和で失敗した追加1試行の実回数は不明であり、この320,000へ20,000回として加算していない。キャッシュ復元は追加実行ではない。

## 2026-10-13の未知未来PAPER凍結

5場の各1Rを事前登録し、全5件・全HOLDを保存する設計。結果を見て成功例を選んでいない。Source cutoffは02:00 JST。深夜の早期資料であり、馬体重・馬場等が未観測の項目はRule-bound neutralとmissingnessを保持する。neutralは能力・軸信頼の肯定証拠ではない。実購入は0。

|場/R|頭数|発走JST|PAPER点数|実行ID|
|---|---:|---|---:|---|
|門別1R|7|14:30|30|LOCAL-AKI-FORWARD-8138e5c1315da5d9|
|盛岡1R|10|11:50|45|LOCAL-AKI-FORWARD-a9ef31abe915fa22|
|川崎1R|12|15:00|119|LOCAL-AKI-FORWARD-712dde8283415599|
|金沢1R|11|12:55|13|LOCAL-AKI-FORWARD-3df58be5fe6bf4d7|
|名古屋1R|11|12:10|10|LOCAL-AKI-FORWARD-8086e070bbabf0d5|

計51頭×29=1,479値。CALCULATED1,197、RULED-NEUTRAL282、未解決0。全馬・全指数・全Provenanceを保存。全ケースでSOURCE/FINAL署名、原文hash、原文の日付場R、PRE_KRS/KRS入力hash、20,000実回数、凍結plan hash、SOURCE登録順序、発走前署名時刻を独立検証。列選定はSOURCEから再計算した。

署名資料: forward_pilot_20261013_receipts.tar.gz / forward_pilot_20261013_manifest.json。登録時点のコードはforward_R2_frozen_implementation.tar.gzとファイルhashを保存。完全なPAPER券面ツリーはLOCAL_AKI_FORWARD_FROZEN_TREES_20261013.md。

## 追加7場の技術Replay

|場|公式ページの対象日/R|点数|実行ID|
|---|---|---:|---|
|浦和|2026-09-23/1R|22|LOCAL-AKI-REPLAY-1cab0cf7020fcc20|
|園田|2026-10-09/1R|16|LOCAL-AKI-REPLAY-c8cba3ef9a0fcbf7|
|姫路|2026-02-26/1R|19|LOCAL-AKI-REPLAY-a33478621ddd4b65|
|笠松|2026-10-09/1R|11|LOCAL-AKI-REPLAY-96bafa0b2aeb3cf5|
|高知|2026-10-11/1R|46|LOCAL-AKI-REPLAY-fffb468bf3f74cf4|
|佐賀|2026-10-12/1R|98|LOCAL-AKI-REPLAY-318a1f9d840c38d5|
|水沢|2026-09-27/1R|104|LOCAL-AKI-REPLAY-d0c886f71947b9cb|

これは対象レースの発走前に保存されたSOURCEではない。取得時刻・公式原文・全Runner・指数・署名は真正だが、補助profileは結果後の情報を含み得る。予測性能を評価する資料ではなく、頭数/距離/場/クラスが異なる実入力でのコード・Transport検証である。39レースの過去比較にも加算していない。

資料: post_event_seven_venue_receipts.tar.gz / post_event_seven_venue_manifest.json。失敗試行も保存し、成功資料だけの抽出を防ぐ。

## 浦和のSIGKILLと再開

初回署名KRSはstatus FAIL、returncode -9、actual_run_countなし。HTTP200を成功と解釈していない。初回SOURCE・PRE_KRS・入力・FAIL Receipt・入口FailClosedを保存。並列バッチ終了後、同じSOURCE/選定/KRS入力/seed/必要20,000回で別attemptを単独実行し、署名KRS EXECUTEDと署名FINALを得た。
Railwayの読み取り診断でmemory limit約1GB、60秒サンプル最大0.6572GBを確認。OOMを断定できるログはなく、原因は未確定。リソース増量・契約変更を行わない。技術ReplayのSOURCE取得は並列、外部エンジンへのバッチ投入は一件ずつとした。Runtime全体の別callerとの競合まで解消した証明ではない。

## チャット終了後の結果処理

短時間Worker tools/local_aki_forward_result_worker.py は凍結済み資料のみを処理。未発走はWAITING_OFFICIAL_RESULT。公式結果が未確定/入力競合/署名不一致ならWAITING又はHOLDを保存。SOURCE→29指数/列を再計算し、PRE_KRS/KRS/FINAL系譜を確認して既存正本RuntimeへRESULTを渡す。予測変更・新KRS・購入はしない。
2026-10-13 12:00 JSTから毎時、最大12回の自動処理を作成済み。全5件が完了したら終了する。通常待機では通知せず、全件完了又は重大な入力/署名問題を報告する。予測archiveは更新せず、結果checkpointを別に保存する。workflowも用意したが、このチャットからGitHub workflow dispatchを実起動したとは主張しない。自動処理は保存済みコードを復元してWorkerを実行する。
既存のゼロ資金RESULT handlerはREPLAYラベルを継承する。独立future_evaluation classifierは署名FINAL内FORWARD_PAPER・事前登録・発走前Freezeと実結果観測から分類し、この継承ラベルを本番利用許可へ読み替えない。future OOSの件数は実結果観測後だけ計上し、実購入PFSはnull。同SOURCEのProduction比較が未成立であり、5件だけで優位性・昇格を判定しない。

## 全体の完成条件

全場の実データTransport確認は完了したが、全14場での発走前予測性能、場別予測則の較正、SOURCE鮮度/直前再予測、本番の全日程Worker・Git競合・独立予備起動、R51のgenuine unknown-future OOS + human reviewは未完了。現在の研究実行が稼働したことを、Production完成・性能実証済み・購入許可へ拡張しない。

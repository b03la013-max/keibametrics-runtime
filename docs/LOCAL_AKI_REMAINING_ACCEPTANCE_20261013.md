# LOCAL AKI残項目の追加処理（2026-10-13 JST）

完了判定は限定する。船橋公式結果の処理、整数単位の同予算・同点数研究比較、全14場の外部manifest接続確認、研究経路の二重起動防止・保存済み署名成果物からの復元を実施した。全場の実レース完走、場別の予測則較正、未知未来性能、本番適用、全日程Worker・Git競合の本番解消は完成と判定しない。

## 船橋R6の結果待機を解消

実行ID LOCAL-AKI-REPLAY-6760be6385435c03、FINAL dd083b766f0983b2877ee3405cdb054436df0c0fd00ff2d51909f457ab893c84。
手元の公式取得はDNS待機だったが、既存の正本外部Runtimeの /source/acquire で公式NAR成績原文を取得。RESULT専用の時刻軸とし、SOURCEのEd25519署名・原文hash・日付場R・全出走馬範囲・確定着順・払戻組合せを既存parserで検証した。これを予測用発走前SOURCEに利用していない。
公式上位は7→12→8、馬単370円、三連複8,890円、三連単13,600円。元の署名FINALは上書きせず、署名RESULT c373859f74f0182972b335a7c0985519e4a6ecd4ebacc70872d30373e7e5196e を得た。PAPER25点・2,500円、払戻0円、最初の失敗箇所PREDICTION_ROLE_P2。実購入0円/PFS null、OOS0。
既存formal_execution_orchestrator --aki-paper-replay --replay-official-result-source経路からRESULT/Reflection/Learningまで再開し、fnb_r06_single_entry_report.jsonへ保存。署名成果物はfnb_r06_postresult_receipts.tar.gzとmanifestへ保存。追加KRS回数0、累計の独立実行は4レース80,000回のまま。

## 同予算・同点数比較を実施

39の同一SOURCE・結果レースについて、元FINALとRESULTの署名・hash・結果系譜も再検証した。固定namespace LOCAL-AKI-MATCHED-REPLAY-20261013-R1 とrace identity/ticket keyだけで並べ、結果・オッズ・払戻による選別は行わない。予測候補と本番券面は変更しない。研究用ポートフォリオは100円単位で実際に点数・金額が一致する。

|研究方式|候補回収率|既存回収率|各方式の総投資|
|---|---:|---:|---:|
|元券面（各100円）|44.95%|46.45%|候補274,300円/既存939,600円|
|同予算・全候補維持|57.18%|46.33%|両者942,000円|
|同予算・同点数の固定hash比較|44.34%|32.83%|両者271,900円・2,719点|

全候補維持方式は、各レースの両券面の最大点数×100円を共通予算とし、全点へ100円以上を配分する。余りの100円は結果を使わない固定順へ配る。これは新Capital推奨ではない。
同点数方式は両者の最小点数を比較点数とする固定hash部分集合。候補を機械削減する予測規則ではなく、幅の違う元券面を比較する研究上の反実仮想である。比較結果はこの一つの固定研究手法に依存し、既存方式一般に対する優位性を証明しない。
全候補維持方式から払戻上位3レースを除くと候補23.81%、既存39.07%。候補の最大drawdown546,450円は既存505,560円より大きい。点数を絞った方式でも上位3レース除外後は候補16.54%、既存16.59%。頑健な性能改善とは判定しない。
券種別、場別、頭数別、クラス別、距離別、時系列前後、的中赤字、損失上位5戦集中、連敗・drawdown、全比較券面と精算をmatched_comparison.json.gzに保存。全件Replay/OOS0。規則を高配当に合わせて最適化していない。

## 全14場の接続と実証不足を分離

正本Runtime /source/manifest/local のAPIを14場とも実呼出しし、場コードと生成manifestを確認した。保存先venue_manifest_transport。競走の存在確認・SOURCE取得・発走前Freeze・全29指数・KRS・FINAL実証とは別で、source_acquired/prestart_source_acceptance/race_existence_verifiedはfalse。
実署名SOURCEによるAKI→FINALは大井・船橋・川崎3場4レース。再構成可能な重複除去済みPAPER SOURCEは大井46、船橋10、川崎2。残りの浦和・園田・姫路・名古屋・笠松・金沢・高知・佐賀・盛岡・水沢・門別には、この監査で適格な保存済み発走前SOURCEがない。場別較正も未実証。これらへ大井等の出走馬を差し替えて全場検証済みにすることはしない。
追加の全文検索から園田2026-08-28 R2のRECON terminal precheckを2,078行すべて読んだ。Head/Pair/Third閉包記録はあるがSigned SOURCE・全29指数Provenance・公式結果系譜がなく、適格Replayへ加算しない。PURCHASEDという内部ラベルを実購入証明にしない。除外記録sonoda_historical_exclusion.json。
添付の旧地方版v4.12、旧船橋v1.8、旧KRS v1.6等は継承資料。発効中R51の地方v4.13、船橋v2.1、KRS v1.7等をこれらで巻き戻していない。

## 二重起動・復元・待機

研究実行はrace/SOURCE単位の非待機ファイルロック。独立レースは別lockを使用する。同一workerが動作中ならEXTERNAL_EXECUTION_WAITとし、入口はLOCAL_AKI_WAITING_EXTERNALを保存する。
KRS送信前にdispatch checkpointを保存し、応答receiptが保存されないまま終了した場合はEXTERNAL_KRS_INDETERMINATE。自動再送で実行回数を増やさない。Runtime側の実行状態照会がないため、この不確定状態を自動回復完了と主張しない。
保存は一時ファイルからatomic replace。同一入力の保存済み成果物は、コミット済み圧縮archiveとファイル別hashを検証して復元し、SOURCEから全29指数・列選定を再計算し、PRE_KRS/KRS/FINAL署名とhashを再検証する。空の作業領域への復元でネットワーク呼出しが起きない回帰も確認した。Git保存はexpected SHA付きref更新で競合上書きを防止する。全日程・独立予備起動・本番WorkerのGit競合解消を実証したという意味ではない。

## 未知未来・本番境界

profiles/local_aki_prospective_evaluation_20261013_R1.jsonへ規則/コードhash、連続全レース・HOLDの収集、時系列分離、比較方式、30 eligible future racesの審査契機、全14場の実証要件、撤回・簡素化の条件を事前登録。30戦は自動昇格閾値ではない。未観測の将来結果はまだ0件。
発効中R51 numerical_consumption_boundaryは、Prediction/KRS/Ticket/Capitalの利用に "SEPARATE GENUINE UNKNOWN-FUTURE OOS + HUMAN REVIEW" を要求している。研究実装・外部Replayの許可でこの証拠を満たしたことにはできない。過去を未知未来へ加算せず、Current AuthorityやProduction suiteを自動昇格させない。
現時点で全地方版完成を宣言できない直接の理由は、11場の適格発走前SOURCE不足、場別則の実装・較正不足、未知未来OOS未観測、本番審査未成立である。これらはコード成功数やmanifest成功数で代替できない。

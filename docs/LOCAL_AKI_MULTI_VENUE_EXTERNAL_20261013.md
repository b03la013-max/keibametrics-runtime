# LOCAL AKI外部検証追加記録（2026-10-13 JST）

Current AuthorityはR51。LOCAL 29指数・63 component rulesを使用し、中央係数は転用していない。数値計算の利用権限とPrediction/KRS/Ticket/Capitalの本番利用権限は別であり、後者は未発効。新規則は未較正のREPLAY/PAPER companion。BAN・実購入・未知未来OOSを含まない。本番完成とは判定しない。

## 実外部実行

同一の正本Runtimeで各20,000回のKRSとEd25519署名FINALを検証した。川崎を含む4独立レース・3場・80,000回。署名済み結果の再開は新規KRS回数に加算しない。

|レース|頭数|PAPER点数|外部実行ID|PAPER投資/払戻|
|---|---:|---:|---|---|
|川崎2026-10-12 R11|9|10|LOCAL-AKI-REPLAY-39f06c07ee208cf9|1,000/0円|
|大井2026-10-07 R4|6|2|LOCAL-AKI-REPLAY-7a4c90234425aee6|200/290円|
|大井2026-10-08 R7|14|341|LOCAL-AKI-REPLAY-9dbe515c86f1f557|34,100/3,560円|
|船橋2026-10-02 R6|12|25|LOCAL-AKI-REPLAY-6760be6385435c03|2,500/未精算|

全件Capital=PAPER、実購入券面は空、実購入額0。実購入回収率はnull。結果既知のReplayでありOOS=0。船橋は正本の公式結果取得経路がOFFICIAL_RESULT_TRANSPORT_PENDINGとなったため、公式RESULT/Settlement/Learning完成扱いにしない。

大井R4ではW/P2が3・1、P3が1・3。順位・AKIに基づく幅が2頭に留まり、異なる3頭がないため三連系は生成されない。大井R7では列ごとの追加候補から341点となった。予算による候補削減はしない。341点は最適性の実証ではなく、券面過大・赤字の評価対象。船橋W/P2は7・2・4、P3は4・10・11・12・7・1・2・9・8で、PairとThirdの関係をMECへ渡し25点。

## 正式成果物の券面ツリー（大井R4・全2点）

- PAPER
  - 馬単 EXACTA（各100円、計200円）
    - 1着 1
      - 2着 3
    - 1着 3
      - 2着 1

これは署名FINAL内final_prediction_package.paper_ticketsから抽出した研究券面。final_ticket.ticketsは空。

## 入口・保存・回帰

既存runtime/formal_execution_orchestrator.pyに明示的な--aki-paper-replay経路を接続。正本配下の凍結SOURCE、LOCAL限定、Current Authorityを確認し、既存外部Runtimeへ渡す。通常の本番経路は昇格しない。再開時はSOURCE/PRE_KRS/KRS/FINAL署名、入力hash、SOURCE由来29指数と列選定を再検証してキャッシュを利用する。大井R4の既存入口再開証拠はevidence/local_aki_columns_20261012/ohi_r04_single_entry_report.json。

追加3レースの全29指数・KRS入力・署名・券面・受領記録はmulti_venue_external_receipts.tar.gz、ファイル別hashと実行IDはmulti_venue_manifest.json。川崎の独立証拠は既存kaw_r11_external_receipts.tar.gzを保持。実署名回帰と選定/入口の64テストが通過。署名正本のFINALは変更しない。

## 過去監査・未完成範囲

114 execution IDs/93識別レース、79 FORMAL試行。60 PAPER再構成、19 HOLD、35 FORMAL欠落。39重複除去済み精算レースで候補回収率44.9471%、既存46.4496%。改善は未実証。予算・点数を揃えた比較、損失集中・連敗、十分な時系列評価は未完了。少数高配当への係数最適化は行っていない。

実凍結SOURCEが確認できる場は大井・船橋・川崎。浦和はsmoke等があり全工程適格実例には加算しない。残りの平地場にも共通ルーティングはあるが、全場の適格SOURCEによる実外部完走と場別較正を実証したとはいえない。Libraryは2395件のmetadataを総点検したが全本文を読んだとはいえない。全場完成を宣言するには適格な発走前SOURCEと場別登録の検証が必要。

軸不安、空列、欠測、取消・入力競合の回帰は選定テストで扱う。外部長時間Workerの独立枠・Git競合・全日程起動を本番で解消した証拠は不足している。新規則の実装許可、研究実行、未知未来性能、本番利用、購入権限は分離して保持する。

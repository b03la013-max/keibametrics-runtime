# ケイバメトリクス地方版 オートパイロット 2026-11-15

楽天競馬の公開出馬表（robots.txt許可範囲・61秒間隔）から v4.3 PAPER を自動計算し、公式29指数の算術をシャドー実行。未較正・購入なし・正式Productionではない。

## 全日Completion Gate

| 指標 | 実績 |
|---|---|
| 開催場Discovery | 4場（水沢・金沢・高知・佐賀） |
| Race Discovery | 44R |
| 発走前予測完成 | 3/44（7%） |
| 発走前GitHub push検証（実バイト照合） | 0/44（0%） |
| 本人Delivery／到達／ACK | 未接続（GitHub保存は本人受領の証拠ではない） |
| 朝版または発走前版あり | 3/44（7%） |
| 未作成（MISSED_DEADLINE） | 0R |
| 失敗・保留 | 0R |
| 最初の失敗 | なし |
| 初回起動 / Plan完成 / 初予想 / 全Race初版完成 | 21:00:22 / 21:05:24 / 21:05:24 / 未達 |
| 最早発走 | 11:45 |
| Provider要求 | 7回・待機422秒 |

## 公式29指数シャドー（候補算術 materialize_candidate・正式Consumerではない）

予想3Rのうち実行3R／27頭×29＝783セル（期待値 783）：CALCULATED 588・RULED-NEUTRAL 195・RULED-HOLD 0・NOT-APPLICABLE 0・UNRESOLVED 0。正式経路と同じセル検査：通過 783／。KRS実試行 0（外部Engine未呼出）。

## PAPERエンジン vs 公式29指数シャドー（同一出馬表）

比較3R：◎一致 2/3・順位相関（Spearman平均）0.67。シャドーは消費権限なし（Prediction/KRS/Ticket/Capital=false）。

## 水沢

| R | 発走（変更） | 状態 | 版 | 取得 | 保存 | 本命 | 買い目 | 結果 |
|---|---|---|---|---|---|---|---|---|
| [1R](MIZ_01.md) | 11:45 | PREDICTION_COMPLETE | 朝版 | 21:02 | 21:05 | ◎1 ラブドラゴン | ワイド 1-2<br>三連複 2-3-4 / 1-2-3 / 1-2-4 / 1-2-5 / 1-3-4 |  |
| [2R](MIZ_02.md) | 12:20 | PREDICTION_COMPLETE | 朝版 | 21:06 | 21:06 | ◎3 ツクバアヴァロン | ワイド 3-7 / 3-4<br>三連複 2-3-7 / 3-7-9 / 3-4-7 / 2-3-9 / 2-3-4 |  |
| [3R](MIZ_03.md) | 12:55 | PREDICTION_COMPLETE | 朝版 | 21:07 | 21:07 | ◎7 ロジタイガー | ワイド 7-6 / 7-10<br>三連複 5-6-7 / 6-7-8 / 6-7-10 / 5-7-8 / 5-7-10 |  |
| 4R | 13:35 | DISCOVERED |  |  |  |  |  |  |
| 5R | 14:10 | DISCOVERED |  |  |  |  |  |  |
| 6R | 14:45 | DISCOVERED |  |  |  |  |  |  |
| 7R | 15:20 | DISCOVERED |  |  |  |  |  |  |
| 8R | 15:50 | DISCOVERED |  |  |  |  |  |  |
| 9R | 16:25 | DISCOVERED |  |  |  |  |  |  |
| 10R | 16:55 | DISCOVERED |  |  |  |  |  |  |
| 11R | 17:30 | DISCOVERED |  |  |  |  |  |  |
| 12R | 18:05 | DISCOVERED |  |  |  |  |  |  |

## 金沢

| R | 発走（変更） | 状態 | 版 | 取得 | 保存 | 本命 | 買い目 | 結果 |
|---|---|---|---|---|---|---|---|---|
| 1R | 13:15 | DISCOVERED |  |  |  |  |  |  |
| 2R | 13:55 | DISCOVERED |  |  |  |  |  |  |
| 3R | 14:30 | DISCOVERED |  |  |  |  |  |  |
| 4R | 15:05 | DISCOVERED |  |  |  |  |  |  |
| 5R | 16:30 | DISCOVERED |  |  |  |  |  |  |
| 6R | 17:05 | DISCOVERED |  |  |  |  |  |  |
| 7R | 17:40 | DISCOVERED |  |  |  |  |  |  |
| 8R | 18:15 | DISCOVERED |  |  |  |  |  |  |
| 9R | 18:55 | DISCOVERED |  |  |  |  |  |  |

## 高知

| R | 発走（変更） | 状態 | 版 | 取得 | 保存 | 本命 | 買い目 | 結果 |
|---|---|---|---|---|---|---|---|---|
| 1R | 14:55 | DISCOVERED |  |  |  |  |  |  |
| 2R | 15:30 | DISCOVERED |  |  |  |  |  |  |
| 3R | 16:00 | DISCOVERED |  |  |  |  |  |  |
| 4R | 16:35 | DISCOVERED |  |  |  |  |  |  |
| 5R | 17:05 | DISCOVERED |  |  |  |  |  |  |
| 6R | 17:35 | DISCOVERED |  |  |  |  |  |  |
| 7R | 18:10 | DISCOVERED |  |  |  |  |  |  |
| 8R | 18:40 | DISCOVERED |  |  |  |  |  |  |
| 9R | 19:15 | DISCOVERED |  |  |  |  |  |  |
| 10R | 19:45 | DISCOVERED |  |  |  |  |  |  |
| 11R | 20:20 | DISCOVERED |  |  |  |  |  |  |
| 12R | 20:50 | DISCOVERED |  |  |  |  |  |  |

## 佐賀

| R | 発走（変更） | 状態 | 版 | 取得 | 保存 | 本命 | 買い目 | 結果 |
|---|---|---|---|---|---|---|---|---|
| 1R | 15:15 | DISCOVERED |  |  |  |  |  |  |
| 2R | 15:50 | DISCOVERED |  |  |  |  |  |  |
| 3R | 16:20 | DISCOVERED |  |  |  |  |  |  |
| 4R | 16:50 | DISCOVERED |  |  |  |  |  |  |
| 5R | 17:25 | DISCOVERED |  |  |  |  |  |  |
| 6R | 18:00 | DISCOVERED |  |  |  |  |  |  |
| 7R | 18:35 | DISCOVERED |  |  |  |  |  |  |
| 8R | 19:05 | DISCOVERED |  |  |  |  |  |  |
| 9R | 19:35 | DISCOVERED |  |  |  |  |  |  |
| 10R | 20:10 | DISCOVERED |  |  |  |  |  |  |
| 11R | 20:40 | DISCOVERED |  |  |  |  |  |  |


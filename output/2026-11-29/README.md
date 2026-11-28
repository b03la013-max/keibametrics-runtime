# ケイバメトリクス地方版 オートパイロット 2026-11-29

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
| 初回起動 / Plan完成 / 初予想 / 全Race初版完成 | 21:00:47 / 21:05:46 / 21:05:47 / 未達 |
| 最早発走 | 11:35 |
| Provider要求 | 7回・待機416秒 |

## 公式29指数シャドー（候補算術 materialize_candidate・正式Consumerではない）

予想3Rのうち実行3R／33頭×29＝957セル（期待値 957）：CALCULATED 778・RULED-NEUTRAL 179・RULED-HOLD 0・NOT-APPLICABLE 0・UNRESOLVED 0。正式経路と同じセル検査：通過 957／。KRS実試行 0（外部Engine未呼出）。

## PAPERエンジン vs 公式29指数シャドー（同一出馬表）

比較3R：◎一致 0/3・順位相関（Spearman平均）0.79。シャドーは消費権限なし（Prediction/KRS/Ticket/Capital=false）。

## 水沢

| R | 発走（変更） | 状態 | 版 | 取得 | 保存 | 本命 | 買い目 | 結果 |
|---|---|---|---|---|---|---|---|---|
| [1R](MIZ_01.md) | 11:35 | PREDICTION_COMPLETE | 朝版 | 21:02 | 21:05 | ◎5 スピードブラッシュ | ワイド 5-6 / 5-8<br>三連複 5-6-11 / 5-6-10 / 5-6-8 / 5-10-11 / 5-8-11 |  |
| [2R](MIZ_02.md) | 12:10 | PREDICTION_COMPLETE | 朝版 | 21:06 | 21:06 | ◎8 ホウオウデンファレ | ワイド 8-7 / 8-2<br>三連複 6-7-8 / 7-8-9 / 4-7-8 / 7-8-10 / 2-7-8 |  |
| [3R](MIZ_03.md) | 12:50 | PREDICTION_COMPLETE | 朝版 | 21:07 | 21:07 | ◎9 ブランマジョリティ | ワイド 9-1 / 9-8<br>三連複 1-9-10 / 1-4-9 / 1-8-9 / 4-9-10 / 8-9-10 |  |
| 4R | 13:25 | DISCOVERED |  |  |  |  |  |  |
| 5R | 14:00 | DISCOVERED |  |  |  |  |  |  |
| 6R | 14:35 | DISCOVERED |  |  |  |  |  |  |
| 7R | 15:10 | DISCOVERED |  |  |  |  |  |  |
| 8R | 15:50 | DISCOVERED |  |  |  |  |  |  |
| 9R | 16:25 | DISCOVERED |  |  |  |  |  |  |
| 10R | 16:55 | DISCOVERED |  |  |  |  |  |  |
| 11R | 17:30 | DISCOVERED |  |  |  |  |  |  |
| 12R | 18:05 | DISCOVERED |  |  |  |  |  |  |

## 金沢

| R | 発走（変更） | 状態 | 版 | 取得 | 保存 | 本命 | 買い目 | 結果 |
|---|---|---|---|---|---|---|---|---|
| 1R | 13:20 | DISCOVERED |  |  |  |  |  |  |
| 2R | 13:55 | DISCOVERED |  |  |  |  |  |  |
| 3R | 14:30 | DISCOVERED |  |  |  |  |  |  |
| 4R | 15:05 | DISCOVERED |  |  |  |  |  |  |
| 5R | 16:05 | DISCOVERED |  |  |  |  |  |  |
| 6R | 16:40 | DISCOVERED |  |  |  |  |  |  |
| 7R | 17:15 | DISCOVERED |  |  |  |  |  |  |
| 8R | 17:55 | DISCOVERED |  |  |  |  |  |  |
| 9R | 18:30 | DISCOVERED |  |  |  |  |  |  |

## 高知

| R | 発走（変更） | 状態 | 版 | 取得 | 保存 | 本命 | 買い目 | 結果 |
|---|---|---|---|---|---|---|---|---|
| 1R | 14:55 | DISCOVERED |  |  |  |  |  |  |
| 2R | 15:30 | DISCOVERED |  |  |  |  |  |  |
| 3R | 16:10 | DISCOVERED |  |  |  |  |  |  |
| 4R | 16:45 | DISCOVERED |  |  |  |  |  |  |
| 5R | 17:20 | DISCOVERED |  |  |  |  |  |  |
| 6R | 17:50 | DISCOVERED |  |  |  |  |  |  |
| 7R | 18:20 | DISCOVERED |  |  |  |  |  |  |
| 8R | 18:50 | DISCOVERED |  |  |  |  |  |  |
| 9R | 19:20 | DISCOVERED |  |  |  |  |  |  |
| 10R | 19:50 | DISCOVERED |  |  |  |  |  |  |
| 11R | 20:20 | DISCOVERED |  |  |  |  |  |  |
| 12R | 20:50 | DISCOVERED |  |  |  |  |  |  |

## 佐賀

| R | 発走（変更） | 状態 | 版 | 取得 | 保存 | 本命 | 買い目 | 結果 |
|---|---|---|---|---|---|---|---|---|
| 1R | 15:15 | DISCOVERED |  |  |  |  |  |  |
| 2R | 15:50 | DISCOVERED |  |  |  |  |  |  |
| 3R | 16:30 | DISCOVERED |  |  |  |  |  |  |
| 4R | 17:05 | DISCOVERED |  |  |  |  |  |  |
| 5R | 17:40 | DISCOVERED |  |  |  |  |  |  |
| 6R | 18:10 | DISCOVERED |  |  |  |  |  |  |
| 7R | 18:40 | DISCOVERED |  |  |  |  |  |  |
| 8R | 19:10 | DISCOVERED |  |  |  |  |  |  |
| 9R | 19:40 | DISCOVERED |  |  |  |  |  |  |
| 10R | 20:10 | DISCOVERED |  |  |  |  |  |  |
| 11R | 20:40 | DISCOVERED |  |  |  |  |  |  |


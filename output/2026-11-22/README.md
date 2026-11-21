# ケイバメトリクス地方版 オートパイロット 2026-11-22

楽天競馬の公開出馬表（robots.txt許可範囲・61秒間隔）から v4.3 PAPER を自動計算し、公式29指数の算術をシャドー実行。未較正・購入なし・正式Productionではない。

## 全日Completion Gate

| 指標 | 実績 |
|---|---|
| 開催場Discovery | 3場（水沢・高知・佐賀） |
| Race Discovery | 34R |
| 発走前予測完成 | 4/34（12%） |
| 発走前GitHub push検証（実バイト照合） | 0/34（0%） |
| 本人Delivery／到達／ACK | 未接続（GitHub保存は本人受領の証拠ではない） |
| 朝版または発走前版あり | 4/34（12%） |
| 未作成（MISSED_DEADLINE） | 0R |
| 失敗・保留 | 0R |
| 最初の失敗 | なし |
| 初回起動 / Plan完成 / 初予想 / 全Race初版完成 | 21:02:05 / 21:06:03 / 21:06:03 / 未達 |
| 最早発走 | 12:00 |
| Provider要求 | 7回・待機371秒 |

## 公式29指数シャドー（候補算術 materialize_candidate・正式Consumerではない）

予想4Rのうち実行4R／44頭×29＝1276セル（期待値 1276）：CALCULATED 1039・RULED-NEUTRAL 237・RULED-HOLD 0・NOT-APPLICABLE 0・UNRESOLVED 0。正式経路と同じセル検査：通過 1276／。KRS実試行 0（外部Engine未呼出）。

## PAPERエンジン vs 公式29指数シャドー（同一出馬表）

比較4R：◎一致 2/4・順位相関（Spearman平均）0.82。シャドーは消費権限なし（Prediction/KRS/Ticket/Capital=false）。

## 水沢

| R | 発走（変更） | 状態 | 版 | 取得 | 保存 | 本命 | 買い目 | 結果 |
|---|---|---|---|---|---|---|---|---|
| [1R](MIZ_01.md) | 12:00 | PREDICTION_COMPLETE | 朝版 | 21:04 | 21:06 | ◎2 デディカス | 馬単 2→1,11,8<br>三連単 2→1,11→1,11,8,5,10 |  |
| [2R](MIZ_02.md) | 12:35 | PREDICTION_COMPLETE | 朝版 | 21:07 | 21:07 | ◎3 ツクバアヴァロン | ワイド 3-7 / 3-10<br>三連複 1-3-7 / 3-4-7 / 3-7-8 / 3-7-9 / 3-7-10 |  |
| [3R](MIZ_03.md) | 13:10 | PREDICTION_COMPLETE | 朝版 | 21:08 | 21:08 | ◎3 メイショウオタモイ | 馬単 3→4,9,8<br>三連単 3→4,9→4,9,8,6,10 |  |
| [4R](MIZ_04.md) | 13:45 | PREDICTION_COMPLETE | 朝版 | 21:09 | 21:09 | ◎8 ブライティアロード | 馬単 8→3,7,9<br>三連単 8→3,7→3,7,9,2,10 |  |
| 5R | 14:15 | DISCOVERED |  |  |  |  |  |  |
| 6R | 14:50 | DISCOVERED |  |  |  |  |  |  |
| 7R | 15:25 | DISCOVERED |  |  |  |  |  |  |
| 8R | 16:05 | DISCOVERED |  |  |  |  |  |  |
| 9R | 16:40 | DISCOVERED |  |  |  |  |  |  |
| 10R | 17:15 | DISCOVERED |  |  |  |  |  |  |
| 11R | 17:50 | DISCOVERED |  |  |  |  |  |  |
| 12R | 18:20 | DISCOVERED |  |  |  |  |  |  |

## 高知

| R | 発走（変更） | 状態 | 版 | 取得 | 保存 | 本命 | 買い目 | 結果 |
|---|---|---|---|---|---|---|---|---|
| 1R | 15:30 | DISCOVERED |  |  |  |  |  |  |
| 2R | 16:00 | DISCOVERED |  |  |  |  |  |  |
| 3R | 16:35 | DISCOVERED |  |  |  |  |  |  |
| 4R | 17:10 | DISCOVERED |  |  |  |  |  |  |
| 5R | 17:45 | DISCOVERED |  |  |  |  |  |  |
| 6R | 18:15 | DISCOVERED |  |  |  |  |  |  |
| 7R | 18:45 | DISCOVERED |  |  |  |  |  |  |
| 8R | 19:15 | DISCOVERED |  |  |  |  |  |  |
| 9R | 19:45 | DISCOVERED |  |  |  |  |  |  |
| 10R | 20:20 | DISCOVERED |  |  |  |  |  |  |
| 11R | 20:50 | DISCOVERED |  |  |  |  |  |  |

## 佐賀

| R | 発走（変更） | 状態 | 版 | 取得 | 保存 | 本命 | 買い目 | 結果 |
|---|---|---|---|---|---|---|---|---|
| 1R | 15:15 | DISCOVERED |  |  |  |  |  |  |
| 2R | 15:50 | DISCOVERED |  |  |  |  |  |  |
| 3R | 16:25 | DISCOVERED |  |  |  |  |  |  |
| 4R | 17:00 | DISCOVERED |  |  |  |  |  |  |
| 5R | 17:35 | DISCOVERED |  |  |  |  |  |  |
| 6R | 18:05 | DISCOVERED |  |  |  |  |  |  |
| 7R | 18:35 | DISCOVERED |  |  |  |  |  |  |
| 8R | 19:10 | DISCOVERED |  |  |  |  |  |  |
| 9R | 19:40 | DISCOVERED |  |  |  |  |  |  |
| 10R | 20:10 | DISCOVERED |  |  |  |  |  |  |
| 11R | 20:40 | DISCOVERED |  |  |  |  |  |  |


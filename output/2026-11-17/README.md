# ケイバメトリクス地方版 オートパイロット 2026-11-17

楽天競馬の公開出馬表（robots.txt許可範囲・61秒間隔）から v4.3 PAPER を自動計算し、公式29指数の算術をシャドー実行。未較正・購入なし・正式Productionではない。

## 全日Completion Gate

| 指標 | 実績 |
|---|---|
| 開催場Discovery | 3場（水沢・大井・金沢） |
| Race Discovery | 36R |
| 発走前予測完成 | 5/36（14%） |
| 発走前GitHub push検証（実バイト照合） | 0/36（0%） |
| 本人Delivery／到達／ACK | 未接続（GitHub保存は本人受領の証拠ではない） |
| 朝版または発走前版あり | 5/36（14%） |
| 未作成（MISSED_DEADLINE） | 0R |
| 失敗・保留 | 0R |
| 最初の失敗 | なし |
| 初回起動 / Plan完成 / 初予想 / 全Race初版完成 | 21:08:03 / 21:11:06 / 21:11:07 / 未達 |
| 最早発走 | 11:35 |
| Provider要求 | 8回・待機422秒 |

## 公式29指数シャドー（候補算術 materialize_candidate・正式Consumerではない）

予想5Rのうち実行5R／58頭×29＝1682セル（期待値 1682）：CALCULATED 1371・RULED-NEUTRAL 311・RULED-HOLD 0・NOT-APPLICABLE 0・UNRESOLVED 0。正式経路と同じセル検査：通過 1682／。KRS実試行 0（外部Engine未呼出）。

## PAPERエンジン vs 公式29指数シャドー（同一出馬表）

比較5R：◎一致 2/5・順位相関（Spearman平均）0.85。シャドーは消費権限なし（Prediction/KRS/Ticket/Capital=false）。

## 水沢

| R | 発走（変更） | 状態 | 版 | 取得 | 保存 | 本命 | 買い目 | 結果 |
|---|---|---|---|---|---|---|---|---|
| [1R](MIZ_01.md) | 11:35 | PREDICTION_COMPLETE | 朝版 | 21:09 | 21:11 | ◎2 フィレルレーヴ | ワイド 2-4 / 2-6<br>三連複 2-4-5 / 2-4-10 / 1-2-4 / 2-4-8 / 2-4-6 |  |
| [2R](MIZ_02.md) | 12:10 | PREDICTION_COMPLETE | 朝版 | 21:12 | 21:12 | ◎10 ブレイロックホール | ワイド 10-12 / 10-7<br>三連複 1-10-12 / 8-10-12 / 7-10-12 / 1-8-10 / 1-7-10 |  |
| [3R](MIZ_03.md) | 12:45 | PREDICTION_COMPLETE | 朝版 | 21:13 | 21:13 | ◎10 シャンペトルブーケ | ワイド 10-3 / 10-4<br>三連複 3-9-10 / 2-3-10 / 3-5-10 / 1-3-10 / 3-4-10 |  |
| [4R](MIZ_04.md) | 13:20 | PREDICTION_COMPLETE | 朝版 | 21:14 | 21:14 | ◎6 パノラマステージ | 馬単 6→2,4,10<br>三連単 6→2,4→2,4,10,11,3 |  |
| [5R](MIZ_05.md) | 13:55 | PREDICTION_COMPLETE | 朝版 | 21:15 | 21:15 | ◎2 イズミル | ワイド 2-9 / 2-8<br>三連複 2-4-9 / 2-6-9 / 2-8-9 / 2-4-6 / 2-4-8 |  |
| 6R | 14:35 | DISCOVERED |  |  |  |  |  |  |
| 7R | 15:10 | DISCOVERED |  |  |  |  |  |  |
| 8R | 15:45 | DISCOVERED |  |  |  |  |  |  |
| 9R | 16:20 | DISCOVERED |  |  |  |  |  |  |
| 10R | 16:55 | DISCOVERED |  |  |  |  |  |  |
| 11R | 17:30 | DISCOVERED |  |  |  |  |  |  |
| 12R | 18:05 | DISCOVERED |  |  |  |  |  |  |

## 大井

| R | 発走（変更） | 状態 | 版 | 取得 | 保存 | 本命 | 買い目 | 結果 |
|---|---|---|---|---|---|---|---|---|
| 1R | 14:30 | DISCOVERED |  |  |  |  |  |  |
| 2R | 15:02 | DISCOVERED |  |  |  |  |  |  |
| 3R | 15:35 | DISCOVERED |  |  |  |  |  |  |
| 4R | 16:07 | DISCOVERED |  |  |  |  |  |  |
| 5R | 16:40 | DISCOVERED |  |  |  |  |  |  |
| 6R | 17:12 | DISCOVERED |  |  |  |  |  |  |
| 7R | 17:45 | DISCOVERED |  |  |  |  |  |  |
| 8R | 18:20 | DISCOVERED |  |  |  |  |  |  |
| 9R | 18:55 | DISCOVERED |  |  |  |  |  |  |
| 10R | 19:30 | DISCOVERED |  |  |  |  |  |  |
| 11R | 20:10 | DISCOVERED |  |  |  |  |  |  |
| 12R | 20:50 | DISCOVERED |  |  |  |  |  |  |

## 金沢

| R | 発走（変更） | 状態 | 版 | 取得 | 保存 | 本命 | 買い目 | 結果 |
|---|---|---|---|---|---|---|---|---|
| 1R | 14:10 | DISCOVERED |  |  |  |  |  |  |
| 2R | 14:45 | DISCOVERED |  |  |  |  |  |  |
| 3R | 15:20 | DISCOVERED |  |  |  |  |  |  |
| 4R | 15:55 | DISCOVERED |  |  |  |  |  |  |
| 5R | 16:30 | DISCOVERED |  |  |  |  |  |  |
| 6R | 17:05 | DISCOVERED |  |  |  |  |  |  |
| 7R | 17:40 | DISCOVERED |  |  |  |  |  |  |
| 8R | 18:15 | DISCOVERED |  |  |  |  |  |  |
| 9R | 18:50 | DISCOVERED |  |  |  |  |  |  |
| 10R | 19:25 | DISCOVERED |  |  |  |  |  |  |
| 11R | 20:00 | DISCOVERED |  |  |  |  |  |  |
| 12R | 20:40 | DISCOVERED |  |  |  |  |  |  |


# ケイバメトリクス地方版 オートパイロット 2026-11-26

楽天競馬の公開出馬表（robots.txt許可範囲・61秒間隔）から v4.3 PAPER を自動計算し、公式29指数の算術をシャドー実行。未較正・購入なし・正式Productionではない。

## 全日Completion Gate

| 指標 | 実績 |
|---|---|
| 開催場Discovery | 4場（浦和・金沢・名古屋・園田） |
| Race Discovery | 48R |
| 発走前予測完成 | 4/48（8%） |
| 発走前GitHub push検証（実バイト照合） | 0/48（0%） |
| 本人Delivery／到達／ACK | 未接続（GitHub保存は本人受領の証拠ではない） |
| 朝版または発走前版あり | 4/48（8%） |
| 未作成（MISSED_DEADLINE） | 0R |
| 失敗・保留 | 0R |
| 最初の失敗 | なし |
| 初回起動 / Plan完成 / 初予想 / 全Race初版完成 | 21:00:04 / 21:04:09 / 21:04:09 / 未達 |
| 最早発走 | 10:40 |
| Provider要求 | 8回・待機422秒 |

## 公式29指数シャドー（候補算術 materialize_candidate・正式Consumerではない）

予想4Rのうち実行4R／43頭×29＝1247セル（期待値 1247）：CALCULATED 1016・RULED-NEUTRAL 231・RULED-HOLD 0・NOT-APPLICABLE 0・UNRESOLVED 0。正式経路と同じセル検査：通過 1247／。KRS実試行 0（外部Engine未呼出）。

## PAPERエンジン vs 公式29指数シャドー（同一出馬表）

比較4R：◎一致 1/4・順位相関（Spearman平均）0.80。シャドーは消費権限なし（Prediction/KRS/Ticket/Capital=false）。

## 浦和

| R | 発走（変更） | 状態 | 版 | 取得 | 保存 | 本命 | 買い目 | 結果 |
|---|---|---|---|---|---|---|---|---|
| 1R | 12:20 | DISCOVERED |  |  |  |  |  |  |
| 2R | 12:50 | DISCOVERED |  |  |  |  |  |  |
| 3R | 13:20 | DISCOVERED |  |  |  |  |  |  |
| 4R | 13:50 | DISCOVERED |  |  |  |  |  |  |
| 5R | 14:20 | DISCOVERED |  |  |  |  |  |  |
| 6R | 14:50 | DISCOVERED |  |  |  |  |  |  |
| 7R | 15:25 | DISCOVERED |  |  |  |  |  |  |
| 8R | 16:00 | DISCOVERED |  |  |  |  |  |  |
| 9R | 16:35 | DISCOVERED |  |  |  |  |  |  |
| 10R | 17:10 | DISCOVERED |  |  |  |  |  |  |
| 11R | 17:45 | DISCOVERED |  |  |  |  |  |  |
| 12R | 18:20 | DISCOVERED |  |  |  |  |  |  |

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
| 12R | 20:35 | DISCOVERED |  |  |  |  |  |  |

## 名古屋

| R | 発走（変更） | 状態 | 版 | 取得 | 保存 | 本命 | 買い目 | 結果 |
|---|---|---|---|---|---|---|---|---|
| 1R | 14:40 | DISCOVERED |  |  |  |  |  |  |
| 2R | 15:15 | DISCOVERED |  |  |  |  |  |  |
| 3R | 15:50 | DISCOVERED |  |  |  |  |  |  |
| 4R | 16:25 | DISCOVERED |  |  |  |  |  |  |
| 5R | 17:00 | DISCOVERED |  |  |  |  |  |  |
| 6R | 17:30 | DISCOVERED |  |  |  |  |  |  |
| 7R | 18:05 | DISCOVERED |  |  |  |  |  |  |
| 8R | 18:35 | DISCOVERED |  |  |  |  |  |  |
| 9R | 19:05 | DISCOVERED |  |  |  |  |  |  |
| 10R | 19:40 | DISCOVERED |  |  |  |  |  |  |
| 11R | 20:15 | DISCOVERED |  |  |  |  |  |  |
| 12R | 20:50 | DISCOVERED |  |  |  |  |  |  |

## 園田

| R | 発走（変更） | 状態 | 版 | 取得 | 保存 | 本命 | 買い目 | 結果 |
|---|---|---|---|---|---|---|---|---|
| [1R](SON_01.md) | 10:40 | PREDICTION_COMPLETE | 朝版 | 21:04 | 21:04 | ◎8 キングズテイル | ワイド 8-1 / 8-9<br>三連複 1-5-8 / 1-7-8 / 1-8-9 / 5-7-8 / 5-8-9 |  |
| [2R](SON_02.md) | 11:10 | PREDICTION_COMPLETE | 朝版 | 21:05 | 21:05 | ◎5 アスクサステナブル | ワイド 5-3 / 5-2<br>三連複 1-3-5 / 3-5-7 / 3-5-8 / 3-5-6 / 2-3-5 |  |
| [3R](SON_03.md) | 11:40 | PREDICTION_COMPLETE | 朝版 | 21:06 | 21:06 | ◎10 オセアビシャイン | ワイド 10-4 / 10-8<br>三連複 1-4-10 / 2-4-10 / 3-4-10 / 4-6-10 / 4-8-10 |  |
| [4R](SON_04.md) | 12:10 | PREDICTION_COMPLETE | 朝版 | 21:07 | 21:07 | ◎11 マメーアップル | ワイド 11-12 / 11-4<br>三連複 9-11-12 / 3-11-12 / 4-11-12 / 3-9-11 / 4-9-11 |  |
| 5R | 12:45 | DISCOVERED |  |  |  |  |  |  |
| 6R | 13:20 | DISCOVERED |  |  |  |  |  |  |
| 7R | 13:55 | DISCOVERED |  |  |  |  |  |  |
| 8R | 14:30 | DISCOVERED |  |  |  |  |  |  |
| 9R | 15:05 | DISCOVERED |  |  |  |  |  |  |
| 10R | 15:40 | DISCOVERED |  |  |  |  |  |  |
| 11R | 16:15 | DISCOVERED |  |  |  |  |  |  |
| 12R | 16:45 | DISCOVERED |  |  |  |  |  |  |


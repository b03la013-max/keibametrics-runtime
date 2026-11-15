# ケイバメトリクス地方版 オートパイロット 2026-11-16

楽天競馬の公開出馬表（robots.txt許可範囲・61秒間隔）から v4.3 PAPER を自動計算し、公式29指数の算術をシャドー実行。未較正・購入なし・正式Productionではない。

## 全日Completion Gate

| 指標 | 実績 |
|---|---|
| 開催場Discovery | 3場（水沢・大井・金沢） |
| Race Discovery | 36R |
| 発走前予測完成 | 6/36（17%） |
| 発走前GitHub push検証（実バイト照合） | 0/36（0%） |
| 本人Delivery／到達／ACK | 未接続（GitHub保存は本人受領の証拠ではない） |
| 朝版または発走前版あり | 6/36（17%） |
| 未作成（MISSED_DEADLINE） | 0R |
| 失敗・保留 | 0R |
| 最初の失敗 | なし |
| 初回起動 / Plan完成 / 初予想 / 全Race初版完成 | 21:06:16 / 21:09:19 / 21:09:31 / 未達 |
| 最早発走 | 11:45 |
| Provider要求 | 8回・待機401秒 |

## 公式29指数シャドー（候補算術 materialize_candidate・正式Consumerではない）

予想6Rのうち実行6R／60頭×29＝1740セル（期待値 1740）：CALCULATED 1422・RULED-NEUTRAL 318・RULED-HOLD 0・NOT-APPLICABLE 0・UNRESOLVED 0。正式経路と同じセル検査：通過 1740／。KRS実試行 0（外部Engine未呼出）。

## PAPERエンジン vs 公式29指数シャドー（同一出馬表）

比較6R：◎一致 2/6・順位相関（Spearman平均）0.69。シャドーは消費権限なし（Prediction/KRS/Ticket/Capital=false）。

## 水沢

| R | 発走（変更） | 状態 | 版 | 取得 | 保存 | 本命 | 買い目 | 結果 |
|---|---|---|---|---|---|---|---|---|
| [1R](MIZ_01.md) | 11:45 | PREDICTION_COMPLETE | 朝版 | 21:07 | 21:09 | ◎6 イヌボウノシオカゼ | ワイド 6-9 / 6-5<br>三連複 6-8-9 / 6-7-9 / 5-6-9 / 6-7-8 / 5-6-8 |  |
| [2R](MIZ_02.md) | 12:20 | PREDICTION_COMPLETE | 朝版 | 21:10 | 21:10 | ◎2 ゴールドサイカ | ワイド 2-7 / 2-4<br>三連複 2-6-7 / 2-5-7 / 2-4-7 / 2-5-6 / 2-4-6 |  |
| [3R](MIZ_03.md) | 12:55 | PREDICTION_COMPLETE | 朝版 | 21:12 | 21:12 | ◎6 ロールスワン | ワイド 6-11 / 6-7<br>三連複 5-6-11 / 2-6-11 / 6-7-11 / 2-5-6 / 5-6-7 |  |
| 4R | 13:30 | DISCOVERED |  |  |  |  |  |  |
| 5R | 14:05 | DISCOVERED |  |  |  |  |  |  |
| 6R | 14:40 | DISCOVERED |  |  |  |  |  |  |
| 7R | 15:15 | DISCOVERED |  |  |  |  |  |  |
| 8R | 15:50 | DISCOVERED |  |  |  |  |  |  |
| 9R | 16:25 | DISCOVERED |  |  |  |  |  |  |
| 10R | 17:00 | DISCOVERED |  |  |  |  |  |  |
| 11R | 17:35 | DISCOVERED |  |  |  |  |  |  |
| 12R | 18:10 | DISCOVERED |  |  |  |  |  |  |

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
| [1R](KNZ_01.md) | 12:15 | PREDICTION_COMPLETE | 朝版 | 21:09 | 21:09 | ◎2 ライツェントライゼ | ワイド 2-1 / 2-10<br>三連複 1-2-4 / 1-2-6 / 1-2-10 / 2-4-6 / 2-4-10 |  |
| [2R](KNZ_02.md) | 12:50 | PREDICTION_COMPLETE | 朝版 | 21:11 | 21:11 | ◎8 カキエモン | ワイド 8-1 / 8-5<br>三連複 1-4-6 / 1-4-8 / 1-6-8 / 1-8-9 / 1-7-8 |  |
| [3R](KNZ_03.md) | 13:25 | PREDICTION_COMPLETE | 朝版 | 21:13 | 21:13 | ◎3 ドリーマーズ | 馬単 3→1,7,2<br>三連単 3→1,7→1,7,2,8,4 |  |
| 4R | 14:00 | DISCOVERED |  |  |  |  |  |  |
| 5R | 14:35 | DISCOVERED |  |  |  |  |  |  |
| 6R | 15:10 | DISCOVERED |  |  |  |  |  |  |
| 7R | 15:45 | DISCOVERED |  |  |  |  |  |  |
| 8R | 16:20 | DISCOVERED |  |  |  |  |  |  |
| 9R | 16:55 | DISCOVERED |  |  |  |  |  |  |
| 10R | 17:30 | DISCOVERED |  |  |  |  |  |  |
| 11R | 18:05 | DISCOVERED |  |  |  |  |  |  |
| 12R | 18:45 | DISCOVERED |  |  |  |  |  |  |


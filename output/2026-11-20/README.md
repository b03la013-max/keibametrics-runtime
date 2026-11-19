# ケイバメトリクス地方版 オートパイロット 2026-11-20

楽天競馬の公開出馬表（robots.txt許可範囲・61秒間隔）から v4.3 PAPER を自動計算し、公式29指数の算術をシャドー実行。未較正・購入なし・正式Productionではない。

## 全日Completion Gate

| 指標 | 実績 |
|---|---|
| 開催場Discovery | 3場（大井・笠松・園田） |
| Race Discovery | 36R |
| 発走前予測完成 | 6/36（17%） |
| 発走前GitHub push検証（実バイト照合） | 0/36（0%） |
| 本人Delivery／到達／ACK | 未接続（GitHub保存は本人受領の証拠ではない） |
| 朝版または発走前版あり | 6/36（17%） |
| 未作成（MISSED_DEADLINE） | 0R |
| 失敗・保留 | 0R |
| 最初の失敗 | なし |
| 初回起動 / Plan完成 / 初予想 / 全Race初版完成 | 21:01:26 / 21:04:29 / 21:04:31 / 未達 |
| 最早発走 | 10:25 |
| Provider要求 | 8回・待機412秒 |

## 公式29指数シャドー（候補算術 materialize_candidate・正式Consumerではない）

予想6Rのうち実行6R／49頭×29＝1421セル（期待値 1421）：CALCULATED 1102・RULED-NEUTRAL 319・RULED-HOLD 0・NOT-APPLICABLE 0・UNRESOLVED 0。正式経路と同じセル検査：通過 1421／。KRS実試行 0（外部Engine未呼出）。

## PAPERエンジン vs 公式29指数シャドー（同一出馬表）

比較6R：◎一致 4/6・順位相関（Spearman平均）0.86。シャドーは消費権限なし（Prediction/KRS/Ticket/Capital=false）。

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

## 笠松

| R | 発走（変更） | 状態 | 版 | 取得 | 保存 | 本命 | 買い目 | 結果 |
|---|---|---|---|---|---|---|---|---|
| [1R](KSM_01.md) | 10:25 | PREDICTION_COMPLETE | 朝版 | 21:03 | 21:04 | ◎7 キナコチャン | ワイド 7-6 / 7-1<br>三連複 2-6-7 / 4-6-7 / 1-6-7 / 2-4-7 / 1-2-7 |  |
| [2R](KSM_02.md) | 10:55 | PREDICTION_COMPLETE | 朝版 | 21:05 | 21:05 | ◎2 ヒャクレツケン | 馬単 2→9,1,6<br>三連単 2→9,1→9,1,6,4,7 |  |
| [3R](KSM_03.md) | 11:25 | PREDICTION_COMPLETE | 朝版 | 21:07 | 21:07 | ◎2 ヴィペチカ | ワイド 2-7 / 2-1<br>三連複 2-7-8 / 2-6-7 / 1-2-7 / 2-6-8 / 1-2-8 |  |
| 4R | 11:55 | DISCOVERED |  |  |  |  |  |  |
| 5R | 12:25 | DISCOVERED |  |  |  |  |  |  |
| 6R | 12:55 | DISCOVERED |  |  |  |  |  |  |
| 7R | 13:30 | DISCOVERED |  |  |  |  |  |  |
| 8R | 14:00 | DISCOVERED |  |  |  |  |  |  |
| 9R | 14:35 | DISCOVERED |  |  |  |  |  |  |
| 10R | 15:10 | DISCOVERED |  |  |  |  |  |  |
| 11R | 15:45 | DISCOVERED |  |  |  |  |  |  |
| 12R | 16:15 | DISCOVERED |  |  |  |  |  |  |

## 園田

| R | 発走（変更） | 状態 | 版 | 取得 | 保存 | 本命 | 買い目 | 結果 |
|---|---|---|---|---|---|---|---|---|
| [1R](SON_01.md) | 10:40 | PREDICTION_COMPLETE | 朝版 | 21:04 | 21:04 | ◎5 ニネンエフグミ | 馬単 5→9,4,7<br>三連単 5→9,4→9,4,7,3,6 |  |
| [2R](SON_02.md) | 11:10 | PREDICTION_COMPLETE | 朝版 | 21:06 | 21:06 | ◎1 スマイルブロック | ワイド 1-3 / 1-6<br>三連複 2-3-5 / 1-3-5 / 1-2-3 / 1-3-6 / 1-2-5 |  |
| [3R](SON_03.md) | 11:40 | PREDICTION_COMPLETE | 朝版 | 21:08 | 21:08 | ◎7 ロミヒ | ワイド 7-1 / 7-4<br>三連複 1-5-7 / 1-7-8 / 1-4-7 / 5-7-8 / 4-5-7 |  |
| 4R | 12:10 | DISCOVERED |  |  |  |  |  |  |
| 5R | 12:40 | DISCOVERED |  |  |  |  |  |  |
| 6R | 13:10 | DISCOVERED |  |  |  |  |  |  |
| 7R | 13:40 | DISCOVERED |  |  |  |  |  |  |
| 8R | 14:10 | DISCOVERED |  |  |  |  |  |  |
| 9R | 14:45 | DISCOVERED |  |  |  |  |  |  |
| 10R | 15:20 | DISCOVERED |  |  |  |  |  |  |
| 11R | 15:55 | DISCOVERED |  |  |  |  |  |  |
| 12R | 16:30 | DISCOVERED |  |  |  |  |  |  |


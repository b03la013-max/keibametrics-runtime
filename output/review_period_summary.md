# 地方版 週次 2026-W47（自動・推薦試算・実購入なし）

- 反省済みRace 237／PAPER PFS 60.2%／正式推薦 PFS 94.8%
- 第一失敗：{'NONE': 34, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 54, 'PREDICTION_ROLE_W': 75, 'PREDICTION_ROLE_P2': 37, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 24 | 104.2 | 44.2 | {'NONE': 4, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 36 | 56.2 | 36.0 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 5, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 7, 'EXACT_ORIENTATION': 1} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 22 | 63.0 | 36.9 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 6, 'PREDICTION_ROLE_W': 5, 'CAPITAL_EFFICIENCY': 6, 'NONE': 2} |
| SON | 36 | 23.6 | 56.9 | {'PREDICTION_ROLE_W': 16, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_P2': 6, 'NONE': 4} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 237 | 33.8% | 69.2% | 33.8% | 16.5% | 13.9% | 11.0% | 23.6% | 1.56 |
| 正式推薦 | 199 | 33.2% | 62.3% | 62.3% | 71.9% | 100.0% | 62.3% | 30.2% | 1.4 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中35.7%（無作為9.7%、差+26.0）／P2 平均1.0頭 的中17.1%（無作為9.7%、差+7.4）／P3 平均1.0頭 的中14.0%（無作為9.7%、差+4.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中67.2%（無作為28.9%、差+38.3）／P2 平均6.0頭 的中71.3%（無作為57.9%、差+13.5）／P3 平均10.67頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.63/40（選択性補正込み）・能力順位 14.04/20（57R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.01/40（選択性補正込み）・能力順位 13.74/20（50R平均）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 99 | 473,930 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 67 | 250,260 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 46 | 234,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 237 | 932,560 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 4 | 22,410 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 週次 2026-W48（自動・推薦試算・実購入なし）

- 反省済みRace 196／PAPER PFS 62.1%／正式推薦 PFS 43.1%
- 第一失敗：{'PREDICTION_ROLE_P2': 34, 'CAPITAL_EFFICIENCY': 71, 'PREDICTION_ROLE_W': 75, 'NONE': 16}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 22 | 51.6 | 73.2 | {'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 12, 'PREDICTION_ROLE_W': 5, 'NONE': 2} |
| KOC | 3 | 26.7 | 152.9 | {'PREDICTION_ROLE_P2': 1, 'CAPITAL_EFFICIENCY': 1, 'NONE': 1} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 48 | 51.9 | 46.3 | {'PREDICTION_ROLE_W': 20, 'CAPITAL_EFFICIENCY': 14, 'NONE': 6, 'PREDICTION_ROLE_P2': 8} |
| SAG | 15 | 27.2 | 14.3 | {'PREDICTION_ROLE_W': 4, 'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_P2': 5} |
| SON | 36 | 102.8 | 37.8 | {'PREDICTION_ROLE_W': 18, 'NONE': 1, 'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 14} |
| URW | 48 | 65.7 | 35.5 | {'CAPITAL_EFFICIENCY': 16, 'PREDICTION_ROLE_W': 20, 'NONE': 4, 'PREDICTION_ROLE_P2': 8} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 196 | 32.7% | 65.3% | 32.7% | 13.8% | 14.3% | 6.6% | 24.0% | 1.54 |
| 正式推薦 | 196 | 33.2% | 61.7% | 61.7% | 75.0% | 100.0% | 66.8% | 41.3% | 1.49 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中32.7%（無作為9.4%、差+23.3）／P2 平均1.0頭 的中13.8%（無作為9.4%、差+4.4）／P3 平均1.0頭 的中14.3%（無作為9.4%、差+4.9）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中61.7%（無作為28.1%、差+33.7）／P2 平均6.0頭 的中75.0%（無作為56.2%、差+18.8）／P3 平均10.92頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.73/40（選択性補正込み）・能力順位 14.06/20（196R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.37/40（選択性補正込み）・能力順位 13.61/20（196R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 9,000円（5.8%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）48R・着順まで的中 2R／的中 73R のうち的中赤字 37R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 51.2%（同じ196Rの実績 62.1%）／券種別 EXACTA 67点 PFS 37.0%／TRIFECTA 120点 PFS 13.3%／TRIO 1010点 PFS 55.4%／WIDE 340点 PFS 104.4%／WIN 11点 PFS 46.4%／荒れ度（発走前・1番人気オッズ）MID 101R PFS 73.3% 的中赤字 13/36／OPEN 7R PFS 49.8% 的中赤字 0/2／SOLID 85R PFS 47.5% 的中赤字 23/33／UNKNOWN 3R PFS 152.7% 的中赤字 1/2／市場ミラーとの差 193R：実績 60.3% − ミラー 54.9% = Δ 5.4pt（95%区間 -18.9〜30.8、最高1R除き 0.1pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 351,200円（29.9%）／保護層の資金比率 0.0（196R）／組だけ的中（三連単は外れ）55R・着順まで的中 40R／的中 109R のうち的中赤字 90R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 47.0%（同じ196Rの実績 43.1%）／券種別 EXACTA 3048点 PFS 48.2%／TRIFECTA 5652点 PFS 32.3%／TRIO 3060点 PFS 57.8%／荒れ度（発走前・1番人気オッズ）MID 101R PFS 50.6% 的中赤字 44/55／OPEN 7R PFS 15.6% 的中赤字 2/2／SOLID 85R PFS 37.1% 的中赤字 41/49／UNKNOWN 3R PFS 21.7% 的中赤字 3/3／市場ミラーとの差 193R：実績 43.4% − ミラー 68.6% = Δ -25.2pt（95%区間 -50.4〜-2.2、最高1R除き -29.5pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、91R×3券種）：購入 28／予算で削除 0／予想で除外 80／未生成・券種なし 165／役割馬の行き先 {'PURCHASED': 273}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、91R×3券種）：購入 99／予算で削除 30／予想で除外 83／未生成・券種なし 61／役割馬の行き先 {'PURCHASED': 684, 'BUDGET_COMPRESSED': 323}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 35R／W外 56R、2着が P2 役割 6R）：STATIC 6/35（平均3.71位）／STYLE_COND 9/35（平均3.6位） 救済3・喪失0／MARKET_COND 7/33（平均3.03位） 救済5・喪失3
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 60R／W外 31R、2着が P2 役割 45R）：STATIC 47/60（平均4.1位）／STYLE_COND 48/60（平均3.98位） 救済1・喪失0／MARKET_COND 54/58（平均2.95位） 救済10・喪失1

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 90 | 328,530 | RECURRING |
| P1:ROLE_W_MISS | P1 | 75 | 392,370 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 34 | 204,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 196 | 850,530 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 433／PAPER PFS 61.0%／正式推薦 PFS 69.5%
- 第一失敗：{'NONE': 50, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 125, 'PREDICTION_ROLE_W': 150, 'PREDICTION_ROLE_P2': 71, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 46 | 78.5 | 62.5 | {'NONE': 6, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 17, 'PREDICTION_ROLE_W': 9, 'PREDICTION_ROLE_P2': 5, 'EXACT_ORIENTATION': 1} |
| KOC | 26 | 56.6 | 48.9 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 3, 'NONE': 3, 'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 48 | 51.9 | 46.3 | {'PREDICTION_ROLE_W': 20, 'CAPITAL_EFFICIENCY': 14, 'NONE': 6, 'PREDICTION_ROLE_P2': 8} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 37 | 48.0 | 26.9 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 11, 'PREDICTION_ROLE_W': 9, 'CAPITAL_EFFICIENCY': 12, 'NONE': 2} |
| SON | 72 | 62.3 | 47.3 | {'PREDICTION_ROLE_W': 34, 'CAPITAL_EFFICIENCY': 24, 'PREDICTION_ROLE_P2': 9, 'NONE': 5} |
| URW | 48 | 65.7 | 35.5 | {'CAPITAL_EFFICIENCY': 16, 'PREDICTION_ROLE_W': 20, 'NONE': 4, 'PREDICTION_ROLE_P2': 8} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 433 | 33.3% | 67.4% | 33.3% | 15.2% | 14.1% | 9.0% | 23.8% | 1.55 |
| 正式推薦 | 395 | 33.2% | 62.0% | 62.0% | 73.4% | 100.0% | 64.6% | 35.7% | 1.45 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中33.8%（無作為9.5%、差+24.4）／P2 平均1.0頭 的中15.1%（無作為9.5%、差+5.6）／P3 平均1.0頭 的中14.2%（無作為9.5%、差+4.7）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.8%（無作為28.4%、差+35.4）／P2 平均6.0頭 的中73.6%（無作為56.8%、差+16.8）／P3 平均10.82頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.93/40（選択性補正込み）・能力順位 14.05/20（253R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.5/40（選択性補正込み）・能力順位 13.63/20（246R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 9,000円（5.8%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）48R・着順まで的中 2R／的中 73R のうち的中赤字 37R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 51.2%（同じ196Rの実績 62.1%）／券種別 EXACTA 67点 PFS 37.0%／TRIFECTA 120点 PFS 13.3%／TRIO 1010点 PFS 55.4%／WIDE 340点 PFS 104.4%／WIN 11点 PFS 46.4%／荒れ度（発走前・1番人気オッズ）MID 101R PFS 73.3% 的中赤字 13/36／OPEN 7R PFS 49.8% 的中赤字 0/2／SOLID 85R PFS 47.5% 的中赤字 23/33／UNKNOWN 3R PFS 152.7% 的中赤字 1/2／市場ミラーとの差 193R：実績 60.3% − ミラー 54.9% = Δ 5.4pt（95%区間 -18.9〜30.8、最高1R除き 0.1pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 351,200円（29.9%）／保護層の資金比率 0.0（196R）／組だけ的中（三連単は外れ）55R・着順まで的中 40R／的中 109R のうち的中赤字 90R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 47.0%（同じ196Rの実績 43.1%）／券種別 EXACTA 3048点 PFS 48.2%／TRIFECTA 5652点 PFS 32.3%／TRIO 3060点 PFS 57.8%／荒れ度（発走前・1番人気オッズ）MID 101R PFS 50.6% 的中赤字 44/55／OPEN 7R PFS 15.6% 的中赤字 2/2／SOLID 85R PFS 37.1% 的中赤字 41/49／UNKNOWN 3R PFS 21.7% 的中赤字 3/3／市場ミラーとの差 193R：実績 43.4% − ミラー 68.6% = Δ -25.2pt（95%区間 -50.4〜-2.2、最高1R除き -29.5pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、91R×3券種）：購入 28／予算で削除 0／予想で除外 80／未生成・券種なし 165／役割馬の行き先 {'PURCHASED': 273}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、91R×3券種）：購入 99／予算で削除 30／予想で除外 83／未生成・券種なし 61／役割馬の行き先 {'PURCHASED': 684, 'BUDGET_COMPRESSED': 323}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 35R／W外 56R、2着が P2 役割 6R）：STATIC 6/35（平均3.71位）／STYLE_COND 9/35（平均3.6位） 救済3・喪失0／MARKET_COND 7/33（平均3.03位） 救済5・喪失3
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 60R／W外 31R、2着が P2 役割 45R）：STATIC 47/60（平均4.1位）／STYLE_COND 48/60（平均3.98位） 救済1・喪失0／MARKET_COND 54/58（平均2.95位） 救済10・喪失1

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 174 | 866,300 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 157 | 578,790 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 80 | 438,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 433 | 1,783,090 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

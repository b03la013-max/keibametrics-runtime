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

- 反省済みRace 40／PAPER PFS 34.2%／正式推薦 PFS 33.8%
- 第一失敗：{'PREDICTION_ROLE_P2': 10, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 14, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 10 | 20.2 | 94.3 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 1} |
| MIZ | 16 | 49.8 | 11.4 | {'PREDICTION_ROLE_W': 6, 'PREDICTION_ROLE_P2': 5, 'CAPITAL_EFFICIENCY': 5} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| URW | 3 | 31.4 | 15.6 | {'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 1} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 40 | 37.5% | 72.5% | 37.5% | 12.5% | 12.5% | 7.5% | 22.5% | 1.52 |
| 正式推薦 | 40 | 35.0% | 65.0% | 65.0% | 72.5% | 100.0% | 65.0% | 40.0% | 1.57 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中37.5%（無作為10.3%、差+27.2）／P2 平均1.0頭 的中12.5%（無作為10.3%、差+2.2）／P3 平均1.0頭 的中12.5%（無作為10.3%、差+2.2）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中65.0%（無作為31.0%、差+34.0）／P2 平均6.0頭 的中72.5%（無作為61.9%、差+10.6）／P3 平均9.85頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.15/40（選択性補正込み）・能力順位 13.88/20（40R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.54/40（選択性補正込み）・能力順位 13.23/20（40R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（7.5%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）10R・着順まで的中 0R／的中 12R のうち的中赤字 6R／損益分岐の倍率 平均 8.1倍／同じ点数を無作為に選んだ場合の期待PFS 42.2%（同じ40Rの実績 34.2%）／券種別 EXACTA 16点 PFS 0.0%／TRIFECTA 32点 PFS 0.0%／TRIO 204点 PFS 33.2%／WIDE 68点 PFS 62.2%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 14R PFS 43.8% 的中赤字 2/4／OPEN 3R PFS 114.8% 的中赤字 0/2／SOLID 23R PFS 19.9% 的中赤字 4/6／市場ミラーとの差 40R：実績 34.2% − ミラー 62.1% = Δ -27.9pt（95%区間 -67.7〜9.3、最高1R除き -35.2pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 90,800円（37.8%）／保護層の資金比率 0.0（40R）／組だけ的中（三連単は外れ）13R・着順まで的中 6R／的中 19R のうち的中赤字 18R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 37.3%（同じ40Rの実績 33.8%）／券種別 EXACTA 600点 PFS 28.6%／TRIFECTA 1000点 PFS 11.3%／TRIO 800点 PFS 65.8%／荒れ度（発走前・1番人気オッズ）MID 14R PFS 73.3% 的中赤字 6/7／OPEN 3R PFS 8.4% 的中赤字 1/1／SOLID 23R PFS 13.1% 的中赤字 11/11／市場ミラーとの差 40R：実績 33.8% − ミラー 74.1% = Δ -40.2pt（95%区間 -114.2〜26.0、最高1R除き -61.7pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 18 | 74,640 | RECURRING |
| P1:ROLE_W_MISS | P1 | 14 | 81,280 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 10 | 60,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 40 | 200,640 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 1 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 277／PAPER PFS 56.4%／正式推薦 PFS 84.8%
- 第一失敗：{'NONE': 35, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 69, 'PREDICTION_ROLE_W': 89, 'PREDICTION_ROLE_P2': 47, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 34 | 79.4 | 66.2 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 52 | 54.2 | 26.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 5, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 12, 'PREDICTION_ROLE_W': 11, 'PREDICTION_ROLE_P2': 12, 'EXACT_ORIENTATION': 1} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 36 | 23.6 | 56.9 | {'PREDICTION_ROLE_W': 16, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_P2': 6, 'NONE': 4} |
| URW | 3 | 31.4 | 15.6 | {'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 1} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 277 | 34.3% | 69.7% | 34.3% | 15.9% | 13.7% | 10.5% | 23.5% | 1.56 |
| 正式推薦 | 239 | 33.5% | 62.8% | 62.8% | 72.0% | 100.0% | 62.8% | 31.8% | 1.43 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中36.1%（無作為9.8%、差+26.3）／P2 平均1.0頭 的中16.0%（無作為9.8%、差+6.1）／P3 平均1.0頭 的中13.6%（無作為9.8%、差+3.8）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中66.7%（無作為29.4%、差+37.2）／P2 平均6.0頭 的中71.6%（無作為58.9%、差+12.7）／P3 平均10.47頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.43/40（選択性補正込み）・能力順位 13.97/20（97R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.36/40（選択性補正込み）・能力順位 13.51/20（90R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（7.5%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）10R・着順まで的中 0R／的中 12R のうち的中赤字 6R／損益分岐の倍率 平均 8.1倍／同じ点数を無作為に選んだ場合の期待PFS 42.2%（同じ40Rの実績 34.2%）／券種別 EXACTA 16点 PFS 0.0%／TRIFECTA 32点 PFS 0.0%／TRIO 204点 PFS 33.2%／WIDE 68点 PFS 62.2%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 14R PFS 43.8% 的中赤字 2/4／OPEN 3R PFS 114.8% 的中赤字 0/2／SOLID 23R PFS 19.9% 的中赤字 4/6／市場ミラーとの差 40R：実績 34.2% − ミラー 62.1% = Δ -27.9pt（95%区間 -67.7〜9.3、最高1R除き -35.2pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 90,800円（37.8%）／保護層の資金比率 0.0（40R）／組だけ的中（三連単は外れ）13R・着順まで的中 6R／的中 19R のうち的中赤字 18R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 37.3%（同じ40Rの実績 33.8%）／券種別 EXACTA 600点 PFS 28.6%／TRIFECTA 1000点 PFS 11.3%／TRIO 800点 PFS 65.8%／荒れ度（発走前・1番人気オッズ）MID 14R PFS 73.3% 的中赤字 6/7／OPEN 3R PFS 8.4% 的中赤字 1/1／SOLID 23R PFS 13.1% 的中赤字 11/11／市場ミラーとの差 40R：実績 33.8% − ミラー 74.1% = Δ -40.2pt（95%区間 -114.2〜26.0、最高1R除き -61.7pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 113 | 555,210 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 85 | 324,900 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 56 | 294,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 277 | 1,133,200 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 5 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

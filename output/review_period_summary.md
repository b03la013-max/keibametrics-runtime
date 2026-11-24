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

- 反省済みRace 43／PAPER PFS 46.2%／正式推薦 PFS 38.1%
- 第一失敗：{'PREDICTION_ROLE_P2': 11, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 15, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 10 | 20.2 | 94.3 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 1} |
| MIZ | 17 | 47.3 | 10.8 | {'PREDICTION_ROLE_W': 6, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 5} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| URW | 5 | 157.1 | 66.3 | {'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 2, 'NONE': 1} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 43 | 39.5% | 74.4% | 39.5% | 11.6% | 14.0% | 7.0% | 23.3% | 1.51 |
| 正式推薦 | 43 | 32.6% | 65.1% | 65.1% | 72.1% | 100.0% | 65.1% | 41.9% | 1.53 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中39.5%（無作為10.4%、差+29.1）／P2 平均1.0頭 的中11.6%（無作為10.4%、差+1.2）／P3 平均1.0頭 的中14.0%（無作為10.4%、差+3.5）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中65.1%（無作為31.3%、差+33.8）／P2 平均6.0頭 的中72.1%（無作為62.6%、差+9.5）／P3 平均9.79頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.35/40（選択性補正込み）・能力順位 13.77/20（43R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.35/40（選択性補正込み）・能力順位 13.02/20（43R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（7.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）11R・着順まで的中 0R／的中 13R のうち的中赤字 6R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 47.6%（同じ43Rの実績 46.2%）／券種別 EXACTA 16点 PFS 0.0%／TRIFECTA 32点 PFS 0.0%／TRIO 219点 PFS 51.1%／WIDE 74点 PFS 62.8%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 14R PFS 43.8% 的中赤字 2/4／OPEN 3R PFS 114.8% 的中赤字 0/2／SOLID 26R PFS 40.1% 的中赤字 4/7／市場ミラーとの差 43R：実績 46.2% − ミラー 58.3% = Δ -12.1pt（95%区間 -54.7〜36.5、最高1R除き -26.7pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 97,800円（37.9%）／保護層の資金比率 0.0（43R）／組だけ的中（三連単は外れ）15R・着順まで的中 6R／的中 21R のうち的中赤字 18R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 41.2%（同じ43Rの実績 38.1%）／券種別 EXACTA 645点 PFS 33.2%／TRIFECTA 1075点 PFS 10.5%／TRIO 860点 PFS 76.1%／荒れ度（発走前・1番人気オッズ）MID 14R PFS 73.3% 的中赤字 6/7／OPEN 3R PFS 8.4% 的中赤字 1/1／SOLID 26R PFS 22.5% 的中赤字 11/13／市場ミラーとの差 43R：実績 38.1% − ミラー 94.6% = Δ -56.5pt（95%区間 -129.2〜9.7、最高1R除き -76.8pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 18 | 74,640 | RECURRING |
| P1:ROLE_W_MISS | P1 | 15 | 81,280 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 11 | 66,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 43 | 206,640 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 280／PAPER PFS 58.0%／正式推薦 PFS 85.0%
- 第一失敗：{'NONE': 36, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 69, 'PREDICTION_ROLE_W': 90, 'PREDICTION_ROLE_P2': 48, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 34 | 79.4 | 66.2 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 53 | 53.3 | 25.6 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 5, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 12, 'PREDICTION_ROLE_W': 11, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 36 | 23.6 | 56.9 | {'PREDICTION_ROLE_W': 16, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_P2': 6, 'NONE': 4} |
| URW | 5 | 157.1 | 66.3 | {'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 2, 'NONE': 1} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 280 | 34.6% | 70.0% | 34.6% | 15.7% | 13.9% | 10.4% | 23.6% | 1.55 |
| 正式推薦 | 242 | 33.1% | 62.8% | 62.8% | 71.9% | 100.0% | 62.8% | 32.2% | 1.43 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中36.6%（無作為9.9%、差+26.8）／P2 平均1.0頭 的中15.7%（無作為9.9%、差+5.8）／P3 平均1.0頭 的中14.0%（無作為9.9%、差+4.1）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中66.7%（無作為29.5%、差+37.1）／P2 平均6.0頭 的中71.5%（無作為59.1%、差+12.4）／P3 平均10.44頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.51/40（選択性補正込み）・能力順位 13.92/20（100R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.25/40（選択性補正込み）・能力順位 13.41/20（93R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（7.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）11R・着順まで的中 0R／的中 13R のうち的中赤字 6R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 47.6%（同じ43Rの実績 46.2%）／券種別 EXACTA 16点 PFS 0.0%／TRIFECTA 32点 PFS 0.0%／TRIO 219点 PFS 51.1%／WIDE 74点 PFS 62.8%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 14R PFS 43.8% 的中赤字 2/4／OPEN 3R PFS 114.8% 的中赤字 0/2／SOLID 26R PFS 40.1% 的中赤字 4/7／市場ミラーとの差 43R：実績 46.2% − ミラー 58.3% = Δ -12.1pt（95%区間 -54.7〜36.5、最高1R除き -26.7pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 97,800円（37.9%）／保護層の資金比率 0.0（43R）／組だけ的中（三連単は外れ）15R・着順まで的中 6R／的中 21R のうち的中赤字 18R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 41.2%（同じ43Rの実績 38.1%）／券種別 EXACTA 645点 PFS 33.2%／TRIFECTA 1075点 PFS 10.5%／TRIO 860点 PFS 76.1%／荒れ度（発走前・1番人気オッズ）MID 14R PFS 73.3% 的中赤字 6/7／OPEN 3R PFS 8.4% 的中赤字 1/1／SOLID 26R PFS 22.5% 的中赤字 11/13／市場ミラーとの差 43R：実績 38.1% − ミラー 94.6% = Δ -56.5pt（95%区間 -129.2〜9.7、最高1R除き -76.8pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 114 | 555,210 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 85 | 324,900 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 57 | 300,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 280 | 1,139,200 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

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

- 反省済みRace 32／PAPER PFS 40.3%／正式推薦 PFS 39.3%
- 第一失敗：{'PREDICTION_ROLE_P2': 8, 'CAPITAL_EFFICIENCY': 11, 'PREDICTION_ROLE_W': 12, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 10 | 20.2 | 94.3 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 1} |
| MIZ | 12 | 69.0 | 11.2 | {'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 4, 'CAPITAL_EFFICIENCY': 3} |
| SAG | 10 | 26.1 | 17.9 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 2} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 32 | 34.4% | 68.8% | 34.4% | 15.6% | 15.6% | 9.4% | 25.0% | 1.53 |
| 正式推薦 | 32 | 31.2% | 62.5% | 62.5% | 71.9% | 100.0% | 62.5% | 43.8% | 1.59 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中34.4%（無作為10.3%、差+24.0）／P2 平均1.0頭 的中15.6%（無作為10.3%、差+5.3）／P3 平均1.0頭 的中15.6%（無作為10.3%、差+5.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中62.5%（無作為31.0%、差+31.5）／P2 平均6.0頭 的中71.9%（無作為62.0%、差+9.8）／P3 平均9.81頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.31/40（選択性補正込み）・能力順位 13.76/20（32R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.35/40（選択性補正込み）・能力順位 13.26/20（32R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,800円（7.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）8R・着順まで的中 0R／的中 10R のうち的中赤字 4R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 46.8%（同じ32Rの実績 40.3%）／券種別 EXACTA 13点 PFS 0.0%／TRIFECTA 24点 PFS 0.0%／TRIO 164点 PFS 39.2%／WIDE 54点 PFS 72.6%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 13R PFS 47.0% 的中赤字 2/4／OPEN 3R PFS 114.8% 的中赤字 0/2／SOLID 16R PFS 23.5% 的中赤字 2/4／市場ミラーとの差 32R：実績 40.3% − ミラー 71.7% = Δ -31.4pt（95%区間 -78.9〜13.9、最高1R除き -40.8pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 72,900円（38.0%）／保護層の資金比率 0.0（32R）／組だけ的中（三連単は外れ）12R・着順まで的中 5R／的中 15R のうち的中赤字 14R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 41.1%（同じ32Rの実績 39.3%）／券種別 EXACTA 480点 PFS 28.0%／TRIFECTA 800点 PFS 12.6%／TRIO 640点 PFS 81.1%／荒れ度（発走前・1番人気オッズ）MID 13R PFS 78.9% 的中赤字 6/7／OPEN 3R PFS 8.4% 的中赤字 1/1／SOLID 16R PFS 12.9% 的中赤字 7/7／市場ミラーとの差 32R：実績 39.3% − ミラー 81.7% = Δ -42.4pt（95%区間 -136.1〜38.6、最高1R除き -69.5pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 14 | 56,310 | RECURRING |
| P1:ROLE_W_MISS | P1 | 12 | 69,280 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 8 | 48,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 32 | 158,310 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 269／PAPER PFS 57.8%／正式推薦 PFS 87.3%
- 第一失敗：{'NONE': 35, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 65, 'PREDICTION_ROLE_W': 87, 'PREDICTION_ROLE_P2': 45, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 34 | 79.4 | 66.2 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 48 | 59.4 | 27.8 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 5, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_W': 10, 'PREDICTION_ROLE_P2': 11, 'EXACT_ORIENTATION': 1} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 32 | 51.3 | 30.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 36 | 23.6 | 56.9 | {'PREDICTION_ROLE_W': 16, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_P2': 6, 'NONE': 4} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 269 | 33.8% | 69.1% | 33.8% | 16.4% | 14.1% | 10.8% | 23.8% | 1.56 |
| 正式推薦 | 231 | 32.9% | 62.3% | 62.3% | 71.9% | 100.0% | 62.3% | 32.0% | 1.43 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中35.4%（無作為9.8%、差+25.6）／P2 平均1.0頭 的中16.8%（無作為9.8%、差+7.0）／P3 平均1.0頭 的中14.3%（無作為9.8%、差+4.5）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中66.2%（無作為29.4%、差+36.9）／P2 平均6.0頭 的中71.4%（無作為58.7%、差+12.7）／P3 平均10.49頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.52/40（選択性補正込み）・能力順位 13.94/20（89R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.37/40（選択性補正込み）・能力順位 13.55/20（82R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,800円（7.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）8R・着順まで的中 0R／的中 10R のうち的中赤字 4R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 46.8%（同じ32Rの実績 40.3%）／券種別 EXACTA 13点 PFS 0.0%／TRIFECTA 24点 PFS 0.0%／TRIO 164点 PFS 39.2%／WIDE 54点 PFS 72.6%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 13R PFS 47.0% 的中赤字 2/4／OPEN 3R PFS 114.8% 的中赤字 0/2／SOLID 16R PFS 23.5% 的中赤字 2/4／市場ミラーとの差 32R：実績 40.3% − ミラー 71.7% = Δ -31.4pt（95%区間 -78.9〜13.9、最高1R除き -40.8pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 72,900円（38.0%）／保護層の資金比率 0.0（32R）／組だけ的中（三連単は外れ）12R・着順まで的中 5R／的中 15R のうち的中赤字 14R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 41.1%（同じ32Rの実績 39.3%）／券種別 EXACTA 480点 PFS 28.0%／TRIFECTA 800点 PFS 12.6%／TRIO 640点 PFS 81.1%／荒れ度（発走前・1番人気オッズ）MID 13R PFS 78.9% 的中赤字 6/7／OPEN 3R PFS 8.4% 的中赤字 1/1／SOLID 16R PFS 12.9% 的中赤字 7/7／市場ミラーとの差 32R：実績 39.3% − ミラー 81.7% = Δ -42.4pt（95%区間 -136.1〜38.6、最高1R除き -69.5pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 111 | 543,210 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 81 | 306,570 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 54 | 282,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 269 | 1,090,870 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 4 | 22,410 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

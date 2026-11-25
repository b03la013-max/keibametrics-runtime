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

- 反省済みRace 72／PAPER PFS 46.4%／正式推薦 PFS 45.3%
- 第一失敗：{'PREDICTION_ROLE_P2': 15, 'CAPITAL_EFFICIENCY': 22, 'PREDICTION_ROLE_W': 28, 'NONE': 7}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 10 | 20.2 | 94.3 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 1} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 12 | 42.2 | 46.2 | {'PREDICTION_ROLE_W': 6, 'CAPITAL_EFFICIENCY': 3, 'NONE': 2, 'PREDICTION_ROLE_P2': 1} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 3 | 4.9 | 12.9 | {'PREDICTION_ROLE_W': 3} |
| URW | 12 | 116.2 | 56.3 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 2, 'PREDICTION_ROLE_P2': 3} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 72 | 31.9% | 66.7% | 31.9% | 9.7% | 9.7% | 6.9% | 23.6% | 1.5 |
| 正式推薦 | 72 | 34.7% | 61.1% | 61.1% | 75.0% | 100.0% | 61.1% | 44.4% | 1.56 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中31.9%（無作為9.8%、差+22.1）／P2 平均1.0頭 的中9.7%（無作為9.8%、差-0.1）／P3 平均1.0頭 的中9.7%（無作為9.8%、差-0.1）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中61.1%（無作為29.4%、差+31.7）／P2 平均6.0頭 的中75.0%（無作為58.8%、差+16.2）／P3 平均10.43頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.89/40（選択性補正込み）・能力順位 13.93/20（72R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.83/40（選択性補正込み）・能力順位 13.45/20（72R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 4,200円（7.3%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）18R・着順まで的中 1R／的中 24R のうち的中赤字 12R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 40.0%（同じ72Rの実績 46.4%）／券種別 EXACTA 27点 PFS 10.0%／TRIFECTA 56点 PFS 10.5%／TRIO 368点 PFS 48.7%／WIDE 124点 PFS 63.1%／WIN 3点 PFS 63.3%／荒れ度（発走前・1番人気オッズ）MID 34R PFS 55.7% 的中赤字 6/13／OPEN 4R PFS 82.5% 的中赤字 0/2／SOLID 33R PFS 36.4% 的中赤字 6/9／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 71R：実績 47.7% − ミラー 45.9% = Δ 1.8pt（95%区間 -28.2〜32.1、最高1R除き -6.9pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 163,600円（37.9%）／保護層の資金比率 0.0（72R）／組だけ的中（三連単は外れ）24R・着順まで的中 12R／的中 38R のうち的中赤字 30R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 35.3%（同じ72Rの実績 45.3%）／券種別 EXACTA 1080点 PFS 52.1%／TRIFECTA 1800点 PFS 28.2%／TRIO 1440点 PFS 61.5%／荒れ度（発走前・1番人気オッズ）MID 34R PFS 64.4% 的中赤字 12/17／OPEN 4R PFS 27.3% 的中赤字 2/2／SOLID 33R PFS 28.4% 的中赤字 15/18／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 71R：実績 45.6% − ミラー 98.0% = Δ -52.4pt（95%区間 -106.7〜-2.6、最高1R除き -64.5pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 30 | 115,620 | RECURRING |
| P1:ROLE_W_MISS | P1 | 28 | 148,200 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 15 | 90,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 72 | 319,620 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 309／PAPER PFS 57.0%／正式推薦 PFS 81.9%
- 第一失敗：{'NONE': 41, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 76, 'PREDICTION_ROLE_W': 103, 'PREDICTION_ROLE_P2': 52, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 34 | 79.4 | 66.2 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 12 | 42.2 | 46.2 | {'PREDICTION_ROLE_W': 6, 'CAPITAL_EFFICIENCY': 3, 'NONE': 2, 'PREDICTION_ROLE_P2': 1} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 39 | 21.6 | 53.5 | {'PREDICTION_ROLE_W': 19, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_P2': 6, 'NONE': 4} |
| URW | 12 | 116.2 | 56.3 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 2, 'PREDICTION_ROLE_P2': 3} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 309 | 33.3% | 68.6% | 33.3% | 14.9% | 12.9% | 10.0% | 23.6% | 1.55 |
| 正式推薦 | 271 | 33.6% | 62.0% | 62.0% | 72.7% | 100.0% | 62.0% | 33.9% | 1.44 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中34.3%（無作為9.7%、差+24.6）／P2 平均1.0頭 的中14.4%（無作為9.7%、差+4.7）／P3 平均1.0頭 的中12.4%（無作為9.7%、差+2.7）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中64.9%（無作為29.1%、差+35.8）／P2 平均6.0頭 的中72.7%（無作為58.2%、差+14.5）／P3 平均10.58頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.66/40（選択性補正込み）・能力順位 13.97/20（129R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.32/40（選択性補正込み）・能力順位 13.57/20（122R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 4,200円（7.3%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）18R・着順まで的中 1R／的中 24R のうち的中赤字 12R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 40.0%（同じ72Rの実績 46.4%）／券種別 EXACTA 27点 PFS 10.0%／TRIFECTA 56点 PFS 10.5%／TRIO 368点 PFS 48.7%／WIDE 124点 PFS 63.1%／WIN 3点 PFS 63.3%／荒れ度（発走前・1番人気オッズ）MID 34R PFS 55.7% 的中赤字 6/13／OPEN 4R PFS 82.5% 的中赤字 0/2／SOLID 33R PFS 36.4% 的中赤字 6/9／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 71R：実績 47.7% − ミラー 45.9% = Δ 1.8pt（95%区間 -28.2〜32.1、最高1R除き -6.9pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 163,600円（37.9%）／保護層の資金比率 0.0（72R）／組だけ的中（三連単は外れ）24R・着順まで的中 12R／的中 38R のうち的中赤字 30R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 35.3%（同じ72Rの実績 45.3%）／券種別 EXACTA 1080点 PFS 52.1%／TRIFECTA 1800点 PFS 28.2%／TRIO 1440点 PFS 61.5%／荒れ度（発走前・1番人気オッズ）MID 34R PFS 64.4% 的中赤字 12/17／OPEN 4R PFS 27.3% 的中赤字 2/2／SOLID 33R PFS 28.4% 的中赤字 15/18／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 71R：実績 45.6% − ミラー 98.0% = Δ -52.4pt（95%区間 -106.7〜-2.6、最高1R除き -64.5pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 127 | 622,130 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 97 | 365,880 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 61 | 324,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 309 | 1,252,180 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

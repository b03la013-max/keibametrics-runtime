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

- 反省済みRace 23／PAPER PFS 44.6%／正式推薦 PFS 12.2%
- 第一失敗：{'PREDICTION_ROLE_P2': 7, 'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 10}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 7 | 27.3 | 8.7 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 3} |
| MIZ | 11 | 82.8 | 11.6 | {'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 4, 'CAPITAL_EFFICIENCY': 2} |
| SAG | 5 | 0.0 | 18.4 | {'PREDICTION_ROLE_W': 2, 'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_P2': 1} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 23 | 34.8% | 69.6% | 34.8% | 4.3% | 21.7% | 8.7% | 26.1% | 1.52 |
| 正式推薦 | 23 | 39.1% | 56.5% | 56.5% | 65.2% | 100.0% | 56.5% | 30.4% | 1.43 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中34.8%（無作為10.4%、差+24.3）／P2 平均1.0頭 的中4.3%（無作為10.4%、差-6.1）／P3 平均1.0頭 的中21.7%（無作為10.4%、差+11.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中56.5%（無作為31.3%、差+25.2）／P2 平均6.0頭 的中65.2%（無作為62.6%、差+2.6）／P3 平均9.74頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.26/40（選択性補正込み）・能力順位 13.44/20（23R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.93/40（選択性補正込み）・能力順位 12.77/20（23R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,200円（6.5%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）6R・着順まで的中 0R／的中 8R のうち的中赤字 3R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 54.9%（同じ23Rの実績 44.6%）／券種別 EXACTA 10点 PFS 0.0%／TRIFECTA 16点 PFS 0.0%／TRIO 119点 PFS 39.9%／WIDE 38点 PFS 92.4%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 6R PFS 51.8% 的中赤字 1/2／OPEN 3R PFS 114.8% 的中赤字 0/2／SOLID 14R PFS 28.1% 的中赤字 2/4／市場ミラーとの差 23R：実績 44.6% − ミラー 69.0% = Δ -24.3pt（95%区間 -87.4〜31.3、最高1R除き -37.2pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 52,500円（38.0%）／保護層の資金比率 0.0（23R）／組だけ的中（三連単は外れ）7R・着順まで的中 3R／的中 8R のうち的中赤字 8R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 49.0%（同じ23Rの実績 12.2%）／券種別 EXACTA 345点 PFS 10.2%／TRIFECTA 575点 PFS 10.8%／TRIO 460点 PFS 15.4%／荒れ度（発走前・1番人気オッズ）MID 6R PFS 21.1% 的中赤字 2/2／OPEN 3R PFS 8.4% 的中赤字 1/1／SOLID 14R PFS 9.2% 的中赤字 5/5／市場ミラーとの差 23R：実績 12.2% − ミラー 96.4% = Δ -84.2pt（95%区間 -189.5〜-18.1、最高1R除き -90.1pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 10 | 58,250 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 8 | 31,200 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 7 | 42,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 23 | 121,200 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 260／PAPER PFS 58.8%／正式推薦 PFS 86.5%
- 第一失敗：{'NONE': 34, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 60, 'PREDICTION_ROLE_W': 85, 'PREDICTION_ROLE_P2': 44, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 31 | 86.0 | 31.6 | {'NONE': 4, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 7, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 47 | 61.9 | 28.4 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 5, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 9, 'PREDICTION_ROLE_W': 10, 'PREDICTION_ROLE_P2': 11, 'EXACT_ORIENTATION': 1} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 27 | 50.0 | 33.0 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 7, 'PREDICTION_ROLE_W': 7, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| SON | 36 | 23.6 | 56.9 | {'PREDICTION_ROLE_W': 16, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_P2': 6, 'NONE': 4} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 260 | 33.8% | 69.2% | 33.8% | 15.4% | 14.6% | 10.8% | 23.8% | 1.56 |
| 正式推薦 | 222 | 33.8% | 61.7% | 61.7% | 71.2% | 100.0% | 61.7% | 30.2% | 1.41 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中35.5%（無作為9.8%、差+25.7）／P2 平均1.0頭 的中15.1%（無作為9.8%、差+5.3）／P3 平均1.0頭 的中15.1%（無作為9.8%、差+5.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中65.5%（無作為29.3%、差+36.2）／P2 平均6.0頭 的中70.3%（無作為58.6%、差+11.7）／P3 平均10.52頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.53/40（選択性補正込み）・能力順位 13.86/20（80R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.04/40（選択性補正込み）・能力順位 13.43/20（73R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,200円（6.5%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）6R・着順まで的中 0R／的中 8R のうち的中赤字 3R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 54.9%（同じ23Rの実績 44.6%）／券種別 EXACTA 10点 PFS 0.0%／TRIFECTA 16点 PFS 0.0%／TRIO 119点 PFS 39.9%／WIDE 38点 PFS 92.4%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 6R PFS 51.8% 的中赤字 1/2／OPEN 3R PFS 114.8% 的中赤字 0/2／SOLID 14R PFS 28.1% 的中赤字 2/4／市場ミラーとの差 23R：実績 44.6% − ミラー 69.0% = Δ -24.3pt（95%区間 -87.4〜31.3、最高1R除き -37.2pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 52,500円（38.0%）／保護層の資金比率 0.0（23R）／組だけ的中（三連単は外れ）7R・着順まで的中 3R／的中 8R のうち的中赤字 8R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 49.0%（同じ23Rの実績 12.2%）／券種別 EXACTA 345点 PFS 10.2%／TRIFECTA 575点 PFS 10.8%／TRIO 460点 PFS 15.4%／荒れ度（発走前・1番人気オッズ）MID 6R PFS 21.1% 的中赤字 2/2／OPEN 3R PFS 8.4% 的中赤字 1/1／SOLID 14R PFS 9.2% 的中赤字 5/5／市場ミラーとの差 23R：実績 12.2% − ミラー 96.4% = Δ -84.2pt（95%区間 -189.5〜-18.1、最高1R除き -90.1pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 109 | 532,180 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 75 | 281,460 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 53 | 276,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 260 | 1,053,760 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 4 | 22,410 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

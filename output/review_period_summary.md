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

- 反省済みRace 92／PAPER PFS 50.1%／正式推薦 PFS 44.8%
- 第一失敗：{'PREDICTION_ROLE_P2': 16, 'CAPITAL_EFFICIENCY': 31, 'PREDICTION_ROLE_W': 37, 'NONE': 8}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 10 | 20.2 | 94.3 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 1} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 16 | 41.2 | 45.7 | {'PREDICTION_ROLE_W': 7, 'CAPITAL_EFFICIENCY': 6, 'NONE': 2, 'PREDICTION_ROLE_P2': 1} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 11 | 43.8 | 56.1 | {'PREDICTION_ROLE_W': 8, 'NONE': 1, 'PREDICTION_ROLE_P2': 1, 'CAPITAL_EFFICIENCY': 1} |
| URW | 20 | 99.2 | 39.0 | {'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 7, 'NONE': 2, 'PREDICTION_ROLE_P2': 3} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 92 | 28.3% | 66.3% | 28.3% | 13.0% | 9.8% | 7.6% | 23.9% | 1.49 |
| 正式推薦 | 92 | 31.5% | 59.8% | 59.8% | 77.2% | 100.0% | 59.8% | 43.5% | 1.47 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中28.3%（無作為9.6%、差+18.6）／P2 平均1.0頭 的中13.0%（無作為9.6%、差+3.4）／P3 平均1.0頭 的中9.8%（無作為9.6%、差+0.2）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中59.8%（無作為28.9%、差+30.9）／P2 平均6.0頭 的中77.2%（無作為57.8%、差+19.4）／P3 平均10.63頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.72/40（選択性補正込み）・能力順位 13.73/20（92R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.85/40（選択性補正込み）・能力順位 13.3/20（92R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 5,400円（7.3%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）23R・着順まで的中 1R／的中 31R のうち的中赤字 16R／損益分岐の倍率 平均 8.1倍／同じ点数を無作為に選んだ場合の期待PFS 50.7%（同じ92Rの実績 50.1%）／券種別 EXACTA 37点 PFS 7.3%／TRIFECTA 72点 PFS 8.2%／TRIO 472点 PFS 54.8%／WIDE 156点 PFS 64.6%／WIN 5点 PFS 70.0%／荒れ度（発走前・1番人気オッズ）MID 46R PFS 55.0% 的中赤字 8/16／OPEN 5R PFS 67.7% 的中赤字 0/2／SOLID 40R PFS 45.5% 的中赤字 8/13／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 91R：実績 51.2% − ミラー 44.4% = Δ 6.7pt（95%区間 -19.8〜34.8、最高1R除き 0.0pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 210,100円（38.1%）／保護層の資金比率 0.0（92R）／組だけ的中（三連単は外れ）30R・着順まで的中 14R／的中 51R のうち的中赤字 42R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 46.8%（同じ92Rの実績 44.8%）／券種別 EXACTA 1380点 PFS 54.1%／TRIFECTA 2300点 PFS 24.0%／TRIO 1840点 PFS 63.8%／荒れ度（発走前・1番人気オッズ）MID 46R PFS 54.5% 的中赤字 19/24／OPEN 5R PFS 21.9% 的中赤字 2/2／SOLID 40R PFS 37.0% 的中赤字 20/24／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 91R：実績 45.0% − ミラー 85.3% = Δ -40.3pt（95%区間 -84.3〜1.7、最高1R除き -49.6pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 42 | 158,410 | RECURRING |
| P1:ROLE_W_MISS | P1 | 37 | 193,380 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 16 | 96,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 92 | 404,410 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 329／PAPER PFS 57.3%／正式推薦 PFS 79.3%
- 第一失敗：{'NONE': 42, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 85, 'PREDICTION_ROLE_W': 112, 'PREDICTION_ROLE_P2': 53, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 34 | 79.4 | 66.2 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 16 | 41.2 | 45.7 | {'PREDICTION_ROLE_W': 7, 'CAPITAL_EFFICIENCY': 6, 'NONE': 2, 'PREDICTION_ROLE_P2': 1} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 47 | 29.0 | 56.7 | {'PREDICTION_ROLE_W': 24, 'CAPITAL_EFFICIENCY': 11, 'PREDICTION_ROLE_P2': 7, 'NONE': 5} |
| URW | 20 | 99.2 | 39.0 | {'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 7, 'NONE': 2, 'PREDICTION_ROLE_P2': 3} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 329 | 32.2% | 68.4% | 32.2% | 15.5% | 12.8% | 10.0% | 23.7% | 1.54 |
| 正式推薦 | 291 | 32.6% | 61.5% | 61.5% | 73.5% | 100.0% | 61.5% | 34.4% | 1.42 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中32.6%（無作為9.7%、差+22.9）／P2 平均1.0頭 的中15.4%（無作為9.7%、差+5.7）／P3 平均1.0頭 的中12.2%（無作為9.7%、差+2.6）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中64.0%（無作為28.9%、差+35.1）／P2 平均6.0頭 的中73.8%（無作為57.8%、差+16.0）／P3 平均10.65頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.45/40（選択性補正込み）・能力順位 13.85/20（149R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.26/40（選択性補正込み）・能力順位 13.45/20（142R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 5,400円（7.3%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）23R・着順まで的中 1R／的中 31R のうち的中赤字 16R／損益分岐の倍率 平均 8.1倍／同じ点数を無作為に選んだ場合の期待PFS 50.7%（同じ92Rの実績 50.1%）／券種別 EXACTA 37点 PFS 7.3%／TRIFECTA 72点 PFS 8.2%／TRIO 472点 PFS 54.8%／WIDE 156点 PFS 64.6%／WIN 5点 PFS 70.0%／荒れ度（発走前・1番人気オッズ）MID 46R PFS 55.0% 的中赤字 8/16／OPEN 5R PFS 67.7% 的中赤字 0/2／SOLID 40R PFS 45.5% 的中赤字 8/13／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 91R：実績 51.2% − ミラー 44.4% = Δ 6.7pt（95%区間 -19.8〜34.8、最高1R除き 0.0pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 210,100円（38.1%）／保護層の資金比率 0.0（92R）／組だけ的中（三連単は外れ）30R・着順まで的中 14R／的中 51R のうち的中赤字 42R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 46.8%（同じ92Rの実績 44.8%）／券種別 EXACTA 1380点 PFS 54.1%／TRIFECTA 2300点 PFS 24.0%／TRIO 1840点 PFS 63.8%／荒れ度（発走前・1番人気オッズ）MID 46R PFS 54.5% 的中赤字 19/24／OPEN 5R PFS 21.9% 的中赤字 2/2／SOLID 40R PFS 37.0% 的中赤字 20/24／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 91R：実績 45.0% − ミラー 85.3% = Δ -40.3pt（95%区間 -84.3〜1.7、最高1R除き -49.6pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 136 | 667,310 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 109 | 408,670 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 62 | 330,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 329 | 1,336,970 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

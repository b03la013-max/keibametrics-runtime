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

- 反省済みRace 89／PAPER PFS 48.0%／正式推薦 PFS 44.4%
- 第一失敗：{'PREDICTION_ROLE_P2': 16, 'CAPITAL_EFFICIENCY': 29, 'PREDICTION_ROLE_W': 36, 'NONE': 8}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 10 | 20.2 | 94.3 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 1} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 15 | 43.9 | 42.3 | {'PREDICTION_ROLE_W': 7, 'CAPITAL_EFFICIENCY': 5, 'NONE': 2, 'PREDICTION_ROLE_P2': 1} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 10 | 22.8 | 54.2 | {'PREDICTION_ROLE_W': 8, 'NONE': 1, 'PREDICTION_ROLE_P2': 1} |
| URW | 19 | 105.8 | 41.1 | {'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 6, 'NONE': 2, 'PREDICTION_ROLE_P2': 3} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 89 | 29.2% | 66.3% | 29.2% | 13.5% | 10.1% | 7.9% | 23.6% | 1.49 |
| 正式推薦 | 89 | 32.6% | 59.6% | 59.6% | 77.5% | 100.0% | 59.6% | 42.7% | 1.47 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中29.2%（無作為9.7%、差+19.6）／P2 平均1.0頭 的中13.5%（無作為9.7%、差+3.8）／P3 平均1.0頭 的中10.1%（無作為9.7%、差+0.5）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中59.6%（無作為29.0%、差+30.6）／P2 平均6.0頭 的中77.5%（無作為58.0%、差+19.6）／P3 平均10.6頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.87/40（選択性補正込み）・能力順位 13.77/20（89R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.82/40（選択性補正込み）・能力順位 13.28/20（89R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 5,400円（7.5%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）22R・着順まで的中 1R／的中 30R のうち的中赤字 16R／損益分岐の倍率 平均 8.1倍／同じ点数を無作為に選んだ場合の期待PFS 50.7%（同じ89Rの実績 48.0%）／券種別 EXACTA 37点 PFS 7.3%／TRIFECTA 72点 PFS 8.2%／TRIO 455点 PFS 53.4%／WIDE 150点 PFS 60.2%／WIN 5点 PFS 70.0%／荒れ度（発走前・1番人気オッズ）MID 44R PFS 57.7% 的中赤字 8/16／OPEN 5R PFS 67.7% 的中赤字 0/2／SOLID 39R PFS 38.7% 的中赤字 8/12／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 88R：実績 49.1% − ミラー 44.2% = Δ 4.9pt（95%区間 -21.5〜32.2、最高1R除き -2.0pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 203,100円（38.0%）／保護層の資金比率 0.0（89R）／組だけ的中（三連単は外れ）29R・着順まで的中 13R／的中 49R のうち的中赤字 40R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 46.3%（同じ89Rの実績 44.4%）／券種別 EXACTA 1335点 PFS 52.9%／TRIFECTA 2225点 PFS 23.1%／TRIO 1780点 PFS 64.5%／荒れ度（発走前・1番人気オッズ）MID 44R PFS 54.8% 的中赤字 18/23／OPEN 5R PFS 21.9% 的中赤字 2/2／SOLID 39R PFS 36.0% 的中赤字 19/23／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 88R：実績 44.6% − ミラー 87.1% = Δ -42.5pt（95%区間 -88.6〜0.6、最高1R除き -52.1pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 40 | 156,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 36 | 187,380 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 16 | 96,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 89 | 396,780 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 326／PAPER PFS 56.9%／正式推薦 PFS 79.6%
- 第一失敗：{'NONE': 42, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 83, 'PREDICTION_ROLE_W': 111, 'PREDICTION_ROLE_P2': 53, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 34 | 79.4 | 66.2 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 15 | 43.9 | 42.3 | {'PREDICTION_ROLE_W': 7, 'CAPITAL_EFFICIENCY': 5, 'NONE': 2, 'PREDICTION_ROLE_P2': 1} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 46 | 23.4 | 56.3 | {'PREDICTION_ROLE_W': 24, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_P2': 7, 'NONE': 5} |
| URW | 19 | 105.8 | 41.1 | {'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 6, 'NONE': 2, 'PREDICTION_ROLE_P2': 3} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 326 | 32.5% | 68.4% | 32.5% | 15.6% | 12.9% | 10.1% | 23.6% | 1.54 |
| 正式推薦 | 288 | 33.0% | 61.5% | 61.5% | 73.6% | 100.0% | 61.5% | 34.0% | 1.42 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中33.0%（無作為9.7%、差+23.3）／P2 平均1.0頭 的中15.6%（無作為9.7%、差+5.9）／P3 平均1.0頭 的中12.4%（無作為9.7%、差+2.7）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中64.0%（無作為28.9%、差+35.0）／P2 平均6.0頭 的中73.9%（無作為57.9%、差+16.0）／P3 平均10.64頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.55/40（選択性補正込み）・能力順位 13.87/20（146R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.25/40（選択性補正込み）・能力順位 13.45/20（139R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 5,400円（7.5%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）22R・着順まで的中 1R／的中 30R のうち的中赤字 16R／損益分岐の倍率 平均 8.1倍／同じ点数を無作為に選んだ場合の期待PFS 50.7%（同じ89Rの実績 48.0%）／券種別 EXACTA 37点 PFS 7.3%／TRIFECTA 72点 PFS 8.2%／TRIO 455点 PFS 53.4%／WIDE 150点 PFS 60.2%／WIN 5点 PFS 70.0%／荒れ度（発走前・1番人気オッズ）MID 44R PFS 57.7% 的中赤字 8/16／OPEN 5R PFS 67.7% 的中赤字 0/2／SOLID 39R PFS 38.7% 的中赤字 8/12／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 88R：実績 49.1% − ミラー 44.2% = Δ 4.9pt（95%区間 -21.5〜32.2、最高1R除き -2.0pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 203,100円（38.0%）／保護層の資金比率 0.0（89R）／組だけ的中（三連単は外れ）29R・着順まで的中 13R／的中 49R のうち的中赤字 40R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 46.3%（同じ89Rの実績 44.4%）／券種別 EXACTA 1335点 PFS 52.9%／TRIFECTA 2225点 PFS 23.1%／TRIO 1780点 PFS 64.5%／荒れ度（発走前・1番人気オッズ）MID 44R PFS 54.8% 的中赤字 18/23／OPEN 5R PFS 21.9% 的中赤字 2/2／SOLID 39R PFS 36.0% 的中赤字 19/23／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 88R：実績 44.6% − ミラー 87.1% = Δ -42.5pt（95%区間 -88.6〜0.6、最高1R除き -52.1pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 135 | 661,310 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 107 | 407,040 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 62 | 330,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 326 | 1,329,340 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

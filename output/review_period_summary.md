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

- 反省済みRace 65／PAPER PFS 49.6%／正式推薦 PFS 46.8%
- 第一失敗：{'PREDICTION_ROLE_P2': 14, 'CAPITAL_EFFICIENCY': 21, 'PREDICTION_ROLE_W': 24, 'NONE': 6}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 10 | 20.2 | 94.3 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 1} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 8 | 40.9 | 46.7 | {'PREDICTION_ROLE_W': 5, 'CAPITAL_EFFICIENCY': 2, 'NONE': 1} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| URW | 12 | 116.2 | 56.3 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 2, 'PREDICTION_ROLE_P2': 3} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 65 | 33.8% | 67.7% | 33.8% | 9.2% | 10.8% | 7.7% | 24.6% | 1.49 |
| 正式推薦 | 65 | 36.9% | 63.1% | 63.1% | 73.8% | 100.0% | 63.1% | 44.6% | 1.54 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中33.8%（無作為9.9%、差+23.9）／P2 平均1.0頭 的中9.2%（無作為9.9%、差-0.7）／P3 平均1.0頭 的中10.8%（無作為9.9%、差+0.9）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.1%（無作為29.7%、差+33.4）／P2 平均6.0頭 的中73.8%（無作為59.4%、差+14.4）／P3 平均10.34頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.2/40（選択性補正込み）・能力順位 13.86/20（65R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.87/40（選択性補正込み）・能力順位 13.44/20（65R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 3,000円（5.9%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）16R・着順まで的中 1R／的中 22R のうち的中赤字 11R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 39.1%（同じ65Rの実績 49.6%）／券種別 EXACTA 21点 PFS 12.9%／TRIFECTA 40点 PFS 14.8%／TRIO 333点 PFS 50.8%／WIDE 114点 PFS 64.7%／WIN 3点 PFS 63.3%／荒れ度（発走前・1番人気オッズ）MID 31R PFS 57.5% 的中赤字 6/12／OPEN 4R PFS 82.5% 的中赤字 0/2／SOLID 30R PFS 38.6% 的中赤字 5/8／市場ミラーとの差 65R：実績 49.6% − ミラー 46.0% = Δ 3.6pt（95%区間 -28.4〜39.0、最高1R除き -5.9pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 147,500円（37.8%）／保護層の資金比率 0.0（65R）／組だけ的中（三連単は外れ）21R・着順まで的中 11R／的中 34R のうち的中赤字 27R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 35.9%（同じ65Rの実績 46.8%）／券種別 EXACTA 975点 PFS 54.3%／TRIFECTA 1625点 PFS 27.7%／TRIO 1300点 PFS 65.0%／荒れ度（発走前・1番人気オッズ）MID 31R PFS 64.8% 的中赤字 11/15／OPEN 4R PFS 27.3% 的中赤字 2/2／SOLID 30R PFS 30.8% 的中赤字 14/17／市場ミラーとの差 65R：実績 46.8% − ミラー 101.2% = Δ -54.4pt（95%区間 -111.8〜3.6、最高1R除き -67.7pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 27 | 102,630 | RECURRING |
| P1:ROLE_W_MISS | P1 | 24 | 126,520 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 14 | 84,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 65 | 288,630 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 302／PAPER PFS 57.9%／正式推薦 PFS 83.3%
- 第一失敗：{'NONE': 40, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 75, 'PREDICTION_ROLE_W': 99, 'PREDICTION_ROLE_P2': 51, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 34 | 79.4 | 66.2 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 8 | 40.9 | 46.7 | {'PREDICTION_ROLE_W': 5, 'CAPITAL_EFFICIENCY': 2, 'NONE': 1} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 36 | 23.6 | 56.9 | {'PREDICTION_ROLE_W': 16, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_P2': 6, 'NONE': 4} |
| URW | 12 | 116.2 | 56.3 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 2, 'PREDICTION_ROLE_P2': 3} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 302 | 33.8% | 68.9% | 33.8% | 14.9% | 13.2% | 10.3% | 23.8% | 1.55 |
| 正式推薦 | 264 | 34.1% | 62.5% | 62.5% | 72.3% | 100.0% | 62.5% | 33.7% | 1.44 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中35.1%（無作為9.8%、差+25.3）／P2 平均1.0頭 的中14.4%（無作為9.8%、差+4.7）／P3 平均1.0頭 的中12.9%（無作為9.8%、差+3.1）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中65.8%（無作為29.2%、差+36.6）／P2 平均6.0頭 的中72.2%（無作為58.4%、差+13.8）／P3 平均10.56頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.87/40（選択性補正込み）・能力順位 13.94/20（122R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.37/40（選択性補正込み）・能力順位 13.57/20（115R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 3,000円（5.9%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）16R・着順まで的中 1R／的中 22R のうち的中赤字 11R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 39.1%（同じ65Rの実績 49.6%）／券種別 EXACTA 21点 PFS 12.9%／TRIFECTA 40点 PFS 14.8%／TRIO 333点 PFS 50.8%／WIDE 114点 PFS 64.7%／WIN 3点 PFS 63.3%／荒れ度（発走前・1番人気オッズ）MID 31R PFS 57.5% 的中赤字 6/12／OPEN 4R PFS 82.5% 的中赤字 0/2／SOLID 30R PFS 38.6% 的中赤字 5/8／市場ミラーとの差 65R：実績 49.6% − ミラー 46.0% = Δ 3.6pt（95%区間 -28.4〜39.0、最高1R除き -5.9pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 147,500円（37.8%）／保護層の資金比率 0.0（65R）／組だけ的中（三連単は外れ）21R・着順まで的中 11R／的中 34R のうち的中赤字 27R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 35.9%（同じ65Rの実績 46.8%）／券種別 EXACTA 975点 PFS 54.3%／TRIFECTA 1625点 PFS 27.7%／TRIO 1300点 PFS 65.0%／荒れ度（発走前・1番人気オッズ）MID 31R PFS 64.8% 的中赤字 11/15／OPEN 4R PFS 27.3% 的中赤字 2/2／SOLID 30R PFS 30.8% 的中赤字 14/17／市場ミラーとの差 65R：実績 46.8% − ミラー 101.2% = Δ -54.4pt（95%区間 -111.8〜3.6、最高1R除き -67.7pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 123 | 600,450 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 94 | 352,890 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 60 | 318,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 302 | 1,221,190 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

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

- 反省済みRace 105／PAPER PFS 48.3%／正式推薦 PFS 41.6%
- 第一失敗：{'PREDICTION_ROLE_P2': 19, 'CAPITAL_EFFICIENCY': 33, 'PREDICTION_ROLE_W': 44, 'NONE': 9}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 10 | 20.2 | 94.3 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 1} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 24 | 29.8 | 35.4 | {'PREDICTION_ROLE_W': 10, 'CAPITAL_EFFICIENCY': 7, 'NONE': 3, 'PREDICTION_ROLE_P2': 4} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 12 | 63.2 | 60.5 | {'PREDICTION_ROLE_W': 9, 'NONE': 1, 'PREDICTION_ROLE_P2': 1, 'CAPITAL_EFFICIENCY': 1} |
| URW | 24 | 83.3 | 33.2 | {'CAPITAL_EFFICIENCY': 9, 'PREDICTION_ROLE_W': 10, 'NONE': 2, 'PREDICTION_ROLE_P2': 3} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 105 | 27.6% | 62.9% | 27.6% | 11.4% | 8.6% | 6.7% | 21.0% | 1.46 |
| 正式推薦 | 105 | 29.5% | 58.1% | 58.1% | 73.3% | 100.0% | 58.1% | 41.0% | 1.46 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中27.6%（無作為9.5%、差+18.1）／P2 平均1.0頭 的中11.4%（無作為9.5%、差+1.9）／P3 平均1.0頭 的中8.6%（無作為9.5%、差-0.9）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中58.1%（無作為28.5%、差+29.6）／P2 平均6.0頭 的中73.3%（無作為56.9%、差+16.4）／P3 平均10.79頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.26/40（選択性補正込み）・能力順位 13.58/20（105R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.59/40（選択性補正込み）・能力順位 13.16/20（105R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 5,400円（6.5%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）23R・着順まで的中 1R／的中 34R のうち的中赤字 18R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 56.8%（同じ105Rの実績 48.3%）／券種別 EXACTA 39点 PFS 6.9%／TRIFECTA 72点 PFS 8.2%／TRIO 539点 PFS 48.0%／WIDE 180点 PFS 73.8%／WIN 6点 PFS 58.3%／荒れ度（発走前・1番人気オッズ）MID 52R PFS 56.9% 的中赤字 10/19／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 46R PFS 40.5% 的中赤字 8/13／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 104R：実績 49.2% − ミラー 45.0% = Δ 4.2pt（95%区間 -20.9〜30.3、最高1R除き -1.7pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 240,400円（38.2%）／保護層の資金比率 0.0（105R）／組だけ的中（三連単は外れ）33R・着順まで的中 15R／的中 55R のうち的中赤字 44R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 53.4%（同じ105Rの実績 41.6%）／券種別 EXACTA 1575点 PFS 49.7%／TRIFECTA 2625点 PFS 22.5%／TRIO 2100点 PFS 59.4%／荒れ度（発走前・1番人気オッズ）MID 52R PFS 50.3% 的中赤字 19/25／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 46R PFS 35.1% 的中赤字 22/27／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 104R：実績 41.7% − ミラー 80.1% = Δ -38.3pt（95%区間 -77.7〜-3.1、最高1R除き -46.4pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 44 | 229,380 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 44 | 168,500 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 19 | 114,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 105 | 468,500 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 342／PAPER PFS 56.6%／正式推薦 PFS 76.8%
- 第一失敗：{'NONE': 43, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 87, 'PREDICTION_ROLE_W': 119, 'PREDICTION_ROLE_P2': 56, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 34 | 79.4 | 66.2 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 24 | 29.8 | 35.4 | {'PREDICTION_ROLE_W': 10, 'CAPITAL_EFFICIENCY': 7, 'NONE': 3, 'PREDICTION_ROLE_P2': 4} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 48 | 34.8 | 57.8 | {'PREDICTION_ROLE_W': 25, 'CAPITAL_EFFICIENCY': 11, 'PREDICTION_ROLE_P2': 7, 'NONE': 5} |
| URW | 24 | 83.3 | 33.2 | {'CAPITAL_EFFICIENCY': 9, 'PREDICTION_ROLE_W': 10, 'NONE': 2, 'PREDICTION_ROLE_P2': 3} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 342 | 31.9% | 67.3% | 31.9% | 14.9% | 12.3% | 9.6% | 22.8% | 1.53 |
| 正式推薦 | 304 | 31.9% | 60.9% | 60.9% | 72.4% | 100.0% | 60.9% | 33.9% | 1.42 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中32.1%（無作為9.6%、差+22.5）／P2 平均1.0頭 的中14.5%（無作為9.6%、差+4.9）／P3 平均1.0頭 的中11.5%（無作為9.6%、差+1.9）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.0%（無作為28.7%、差+34.3）／P2 平均6.0頭 的中72.2%（無作為57.4%、差+14.8）／P3 平均10.73頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.09/40（選択性補正込み）・能力順位 13.74/20（162R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.05/40（選択性補正込み）・能力順位 13.35/20（155R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 5,400円（6.5%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）23R・着順まで的中 1R／的中 34R のうち的中赤字 18R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 56.8%（同じ105Rの実績 48.3%）／券種別 EXACTA 39点 PFS 6.9%／TRIFECTA 72点 PFS 8.2%／TRIO 539点 PFS 48.0%／WIDE 180点 PFS 73.8%／WIN 6点 PFS 58.3%／荒れ度（発走前・1番人気オッズ）MID 52R PFS 56.9% 的中赤字 10/19／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 46R PFS 40.5% 的中赤字 8/13／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 104R：実績 49.2% − ミラー 45.0% = Δ 4.2pt（95%区間 -20.9〜30.3、最高1R除き -1.7pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 240,400円（38.2%）／保護層の資金比率 0.0（105R）／組だけ的中（三連単は外れ）33R・着順まで的中 15R／的中 55R のうち的中赤字 44R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 53.4%（同じ105Rの実績 41.6%）／券種別 EXACTA 1575点 PFS 49.7%／TRIFECTA 2625点 PFS 22.5%／TRIO 2100点 PFS 59.4%／荒れ度（発走前・1番人気オッズ）MID 52R PFS 50.3% 的中赤字 19/25／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 46R PFS 35.1% 的中赤字 22/27／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 104R：実績 41.7% − ミラー 80.1% = Δ -38.3pt（95%区間 -77.7〜-3.1、最高1R除き -46.4pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 143 | 703,310 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 111 | 418,760 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 65 | 348,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 342 | 1,401,060 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

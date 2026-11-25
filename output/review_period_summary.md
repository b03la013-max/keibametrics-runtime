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

- 反省済みRace 83／PAPER PFS 44.6%／正式推薦 PFS 47.1%
- 第一失敗：{'PREDICTION_ROLE_P2': 16, 'CAPITAL_EFFICIENCY': 27, 'PREDICTION_ROLE_W': 32, 'NONE': 8}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 10 | 20.2 | 94.3 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 1} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 13 | 44.5 | 45.8 | {'PREDICTION_ROLE_W': 6, 'CAPITAL_EFFICIENCY': 4, 'NONE': 2, 'PREDICTION_ROLE_P2': 1} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 8 | 26.4 | 67.8 | {'PREDICTION_ROLE_W': 6, 'NONE': 1, 'PREDICTION_ROLE_P2': 1} |
| URW | 17 | 87.0 | 45.6 | {'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 5, 'NONE': 2, 'PREDICTION_ROLE_P2': 3} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 83 | 30.1% | 67.5% | 30.1% | 14.5% | 8.4% | 7.2% | 22.9% | 1.51 |
| 正式推薦 | 83 | 33.7% | 61.4% | 61.4% | 77.1% | 100.0% | 61.4% | 43.4% | 1.52 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中30.1%（無作為9.8%、差+20.4）／P2 平均1.0頭 的中14.5%（無作為9.8%、差+4.7）／P3 平均1.0頭 的中8.4%（無作為9.8%、差-1.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中61.4%（無作為29.3%、差+32.2）／P2 平均6.0頭 的中77.1%（無作為58.5%、差+18.6）／P3 平均10.49頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.93/40（選択性補正込み）・能力順位 13.76/20（83R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.93/40（選択性補正込み）・能力順位 13.34/20（83R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 5,400円（8.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）20R・着順まで的中 1R／的中 27R のうち的中赤字 14R／損益分岐の倍率 平均 8.1倍／同じ点数を無作為に選んだ場合の期待PFS 50.9%（同じ83Rの実績 44.6%）／券種別 EXACTA 33点 PFS 8.2%／TRIFECTA 72点 PFS 8.2%／TRIO 425点 PFS 48.4%／WIDE 142点 PFS 59.7%／WIN 3点 PFS 63.3%／荒れ度（発走前・1番人気オッズ）MID 41R PFS 49.7% 的中赤字 8/15／OPEN 4R PFS 82.5% 的中赤字 0/2／SOLID 37R PFS 38.3% 的中赤字 6/10／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 82R：実績 45.7% − ミラー 44.0% = Δ 1.7pt（95%区間 -23.3〜29.0、最高1R除き -5.7pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 189,000円（38.0%）／保護層の資金比率 0.0（83R）／組だけ的中（三連単は外れ）28R・着順まで的中 12R／的中 46R のうち的中赤字 37R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 46.5%（同じ83Rの実績 47.1%）／券種別 EXACTA 1245点 PFS 56.4%／TRIFECTA 2075点 PFS 24.5%／TRIO 1660点 PFS 68.3%／荒れ度（発走前・1番人気オッズ）MID 41R PFS 58.4% 的中赤字 17/22／OPEN 4R PFS 27.3% 的中赤字 2/2／SOLID 37R PFS 37.3% 的中赤字 17/21／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 82R：実績 47.3% − ミラー 91.2% = Δ -43.9pt（95%区間 -91.7〜0.5、最高1R除き -54.3pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 37 | 141,340 | RECURRING |
| P1:ROLE_W_MISS | P1 | 32 | 164,430 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 16 | 96,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 83 | 363,340 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 320／PAPER PFS 56.1%／正式推薦 PFS 81.1%
- 第一失敗：{'NONE': 42, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 81, 'PREDICTION_ROLE_W': 107, 'PREDICTION_ROLE_P2': 53, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 34 | 79.4 | 66.2 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 13 | 44.5 | 45.8 | {'PREDICTION_ROLE_W': 6, 'CAPITAL_EFFICIENCY': 4, 'NONE': 2, 'PREDICTION_ROLE_P2': 1} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 44 | 24.3 | 58.9 | {'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_P2': 7, 'NONE': 5} |
| URW | 17 | 87.0 | 45.6 | {'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 5, 'NONE': 2, 'PREDICTION_ROLE_P2': 3} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 320 | 32.8% | 68.8% | 32.8% | 15.9% | 12.5% | 10.0% | 23.4% | 1.55 |
| 正式推薦 | 282 | 33.3% | 62.1% | 62.1% | 73.4% | 100.0% | 62.1% | 34.0% | 1.44 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中33.5%（無作為9.7%、差+23.8）／P2 平均1.0頭 的中16.0%（無作為9.7%、差+6.3）／P3 平均1.0頭 的中11.8%（無作為9.7%、差+2.1）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中64.9%（無作為29.1%、差+35.8）／P2 平均6.0頭 的中73.7%（無作為58.1%、差+15.5）／P3 平均10.6頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.62/40（選択性補正込み）・能力順位 13.87/20（140R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.34/40（選択性補正込み）・能力順位 13.49/20（133R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 5,400円（8.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）20R・着順まで的中 1R／的中 27R のうち的中赤字 14R／損益分岐の倍率 平均 8.1倍／同じ点数を無作為に選んだ場合の期待PFS 50.9%（同じ83Rの実績 44.6%）／券種別 EXACTA 33点 PFS 8.2%／TRIFECTA 72点 PFS 8.2%／TRIO 425点 PFS 48.4%／WIDE 142点 PFS 59.7%／WIN 3点 PFS 63.3%／荒れ度（発走前・1番人気オッズ）MID 41R PFS 49.7% 的中赤字 8/15／OPEN 4R PFS 82.5% 的中赤字 0/2／SOLID 37R PFS 38.3% 的中赤字 6/10／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 82R：実績 45.7% − ミラー 44.0% = Δ 1.7pt（95%区間 -23.3〜29.0、最高1R除き -5.7pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 189,000円（38.0%）／保護層の資金比率 0.0（83R）／組だけ的中（三連単は外れ）28R・着順まで的中 12R／的中 46R のうち的中赤字 37R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 46.5%（同じ83Rの実績 47.1%）／券種別 EXACTA 1245点 PFS 56.4%／TRIFECTA 2075点 PFS 24.5%／TRIO 1660点 PFS 68.3%／荒れ度（発走前・1番人気オッズ）MID 41R PFS 58.4% 的中赤字 17/22／OPEN 4R PFS 27.3% 的中赤字 2/2／SOLID 37R PFS 37.3% 的中赤字 17/21／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 82R：実績 47.3% − ミラー 91.2% = Δ -43.9pt（95%区間 -91.7〜0.5、最高1R除き -54.3pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 131 | 638,360 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 104 | 391,600 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 62 | 330,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 320 | 1,295,900 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

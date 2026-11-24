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

- 反省済みRace 44／PAPER PFS 45.3%／正式推薦 PFS 37.2%
- 第一失敗：{'PREDICTION_ROLE_P2': 11, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 16, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 10 | 20.2 | 94.3 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 1} |
| MIZ | 17 | 47.3 | 10.8 | {'PREDICTION_ROLE_W': 6, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 5} |
| NGY | 1 | 0.0 | 0.0 | {'PREDICTION_ROLE_W': 1} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| URW | 5 | 157.1 | 66.3 | {'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 2, 'NONE': 1} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 44 | 38.6% | 72.7% | 38.6% | 11.4% | 13.6% | 6.8% | 22.7% | 1.5 |
| 正式推薦 | 44 | 31.8% | 63.6% | 63.6% | 72.7% | 100.0% | 63.6% | 40.9% | 1.52 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中38.6%（無作為10.4%、差+28.2）／P2 平均1.0頭 的中11.4%（無作為10.4%、差+1.0）／P3 平均1.0頭 的中13.6%（無作為10.4%、差+3.2）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.6%（無作為31.2%、差+32.4）／P2 平均6.0頭 的中72.7%（無作為62.4%、差+10.3）／P3 平均9.82頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.09/40（選択性補正込み）・能力順位 13.74/20（44R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.24/40（選択性補正込み）・能力順位 12.98/20（44R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（6.9%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）11R・着順まで的中 0R／的中 13R のうち的中赤字 6R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 47.3%（同じ44Rの実績 45.3%）／券種別 EXACTA 16点 PFS 0.0%／TRIFECTA 32点 PFS 0.0%／TRIO 224点 PFS 50.0%／WIDE 76点 PFS 61.2%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 15R PFS 40.9% 的中赤字 2/4／OPEN 3R PFS 114.8% 的中赤字 0/2／SOLID 26R PFS 40.1% 的中赤字 4/7／市場ミラーとの差 44R：実績 45.3% − ミラー 57.1% = Δ -11.8pt（95%区間 -56.3〜32.0、最高1R除き -26.2pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 99,900円（37.8%）／保護層の資金比率 0.0（44R）／組だけ的中（三連単は外れ）15R・着順まで的中 6R／的中 21R のうち的中赤字 18R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 40.7%（同じ44Rの実績 37.2%）／券種別 EXACTA 660点 PFS 32.4%／TRIFECTA 1100点 PFS 10.3%／TRIO 880点 PFS 74.4%／荒れ度（発走前・1番人気オッズ）MID 15R PFS 68.4% 的中赤字 6/7／OPEN 3R PFS 8.4% 的中赤字 1/1／SOLID 26R PFS 22.5% 的中赤字 11/13／市場ミラーとの差 44R：実績 37.2% − ミラー 93.7% = Δ -56.5pt（95%区間 -128.2〜7.9、最高1R除き -76.4pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 18 | 74,640 | RECURRING |
| P1:ROLE_W_MISS | P1 | 16 | 87,280 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 11 | 66,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 44 | 212,640 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 281／PAPER PFS 57.9%／正式推薦 PFS 84.6%
- 第一失敗：{'NONE': 36, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 69, 'PREDICTION_ROLE_W': 91, 'PREDICTION_ROLE_P2': 48, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 34 | 79.4 | 66.2 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 53 | 53.3 | 25.6 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 5, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 12, 'PREDICTION_ROLE_W': 11, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 1 | 0.0 | 0.0 | {'PREDICTION_ROLE_W': 1} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 36 | 23.6 | 56.9 | {'PREDICTION_ROLE_W': 16, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_P2': 6, 'NONE': 4} |
| URW | 5 | 157.1 | 66.3 | {'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 2, 'NONE': 1} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 281 | 34.5% | 69.8% | 34.5% | 15.7% | 13.9% | 10.3% | 23.5% | 1.55 |
| 正式推薦 | 243 | 32.9% | 62.6% | 62.6% | 72.0% | 100.0% | 62.6% | 32.1% | 1.42 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中36.4%（無作為9.9%、差+26.5）／P2 平均1.0頭 的中15.6%（無作為9.9%、差+5.7）／P3 平均1.0頭 的中13.9%（無作為9.9%、差+4.0）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中66.3%（無作為29.5%、差+36.7）／P2 平均6.0頭 的中71.7%（無作為59.1%、差+12.6）／P3 平均10.45頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.4/40（選択性補正込み）・能力順位 13.9/20（101R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.18/40（選択性補正込み）・能力順位 13.38/20（94R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（6.9%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）11R・着順まで的中 0R／的中 13R のうち的中赤字 6R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 47.3%（同じ44Rの実績 45.3%）／券種別 EXACTA 16点 PFS 0.0%／TRIFECTA 32点 PFS 0.0%／TRIO 224点 PFS 50.0%／WIDE 76点 PFS 61.2%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 15R PFS 40.9% 的中赤字 2/4／OPEN 3R PFS 114.8% 的中赤字 0/2／SOLID 26R PFS 40.1% 的中赤字 4/7／市場ミラーとの差 44R：実績 45.3% − ミラー 57.1% = Δ -11.8pt（95%区間 -56.3〜32.0、最高1R除き -26.2pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 99,900円（37.8%）／保護層の資金比率 0.0（44R）／組だけ的中（三連単は外れ）15R・着順まで的中 6R／的中 21R のうち的中赤字 18R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 40.7%（同じ44Rの実績 37.2%）／券種別 EXACTA 660点 PFS 32.4%／TRIFECTA 1100点 PFS 10.3%／TRIO 880点 PFS 74.4%／荒れ度（発走前・1番人気オッズ）MID 15R PFS 68.4% 的中赤字 6/7／OPEN 3R PFS 8.4% 的中赤字 1/1／SOLID 26R PFS 22.5% 的中赤字 11/13／市場ミラーとの差 44R：実績 37.2% − ミラー 93.7% = Δ -56.5pt（95%区間 -128.2〜7.9、最高1R除き -76.4pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 115 | 561,210 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 85 | 324,900 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 57 | 300,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 281 | 1,145,200 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

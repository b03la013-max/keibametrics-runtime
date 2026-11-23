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

- 反省済みRace 11／PAPER PFS 61.2%／正式推薦 PFS 11.0%
- 第一失敗：{'PREDICTION_ROLE_P2': 5, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 3}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 4 | 44.3 | 5.6 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 1, 'PREDICTION_ROLE_W': 1} |
| MIZ | 7 | 73.9 | 14.0 | {'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 2} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 11 | 54.5% | 81.8% | 54.5% | 9.1% | 18.2% | 9.1% | 27.3% | 1.45 |
| 正式推薦 | 11 | 54.5% | 72.7% | 72.7% | 45.5% | 100.0% | 72.7% | 27.3% | 1.36 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中54.5%（無作為10.5%、差+44.1）／P2 平均1.0頭 的中9.1%（無作為10.5%、差-1.4）／P3 平均1.0頭 的中18.2%（無作為10.5%、差+7.7）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中72.7%（無作為31.4%、差+41.3）／P2 平均6.0頭 的中45.5%（無作為62.9%、差-17.4）／P3 平均9.64頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.91/40（選択性補正込み）・能力順位 13.87/20（11R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.62/40（選択性補正込み）・能力順位 12.72/20（11R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（7.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）3R・着順まで的中 0R／的中 5R のうち的中赤字 2R／損益分岐の倍率 平均 7.8倍／同じ点数を無作為に選んだ場合の期待PFS 37.7%（同じ11Rの実績 61.2%）／券種別 EXACTA 3点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 55点 PFS 42.4%／WIDE 20点 PFS 146.5%／荒れ度（発走前・1番人気オッズ）MID 3R PFS 111.0% 的中赤字 1/2／SOLID 8R PFS 45.1% 的中赤字 1/3／市場ミラーとの差 11R：実績 61.2% − ミラー 95.6% = Δ -34.4pt（95%区間 -156.2〜70.4、最高1R除き -64.3pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 25,100円（38.0%）／保護層の資金比率 0.0（11R）／組だけ的中（三連単は外れ）3R・着順まで的中 2R／的中 3R のうち的中赤字 3R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 29.0%（同じ11Rの実績 11.0%）／券種別 EXACTA 165点 PFS 7.9%／TRIFECTA 275点 PFS 12.9%／TRIO 220点 PFS 10.8%／荒れ度（発走前・1番人気オッズ）MID 3R PFS 17.9% 的中赤字 1/1／SOLID 8R PFS 8.4% 的中赤字 2/2／市場ミラーとの差 11R：実績 11.0% − ミラー 155.2% = Δ -144.2pt（95%区間 -349.6〜-10.1、最高1R除き -158.7pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | 5 | 30,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 3 | 18,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 3 | 10,770 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 11 | 58,770 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 248／PAPER PFS 60.2%／正式推薦 PFS 90.5%
- 第一失敗：{'NONE': 34, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 57, 'PREDICTION_ROLE_W': 78, 'PREDICTION_ROLE_P2': 42, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 28 | 94.6 | 35.0 | {'NONE': 4, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 43 | 58.7 | 31.1 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 5, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 9, 'PREDICTION_ROLE_W': 7, 'PREDICTION_ROLE_P2': 10, 'EXACT_ORIENTATION': 1} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 22 | 63.0 | 36.9 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 6, 'PREDICTION_ROLE_W': 5, 'CAPITAL_EFFICIENCY': 6, 'NONE': 2} |
| SON | 36 | 23.6 | 56.9 | {'PREDICTION_ROLE_W': 16, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_P2': 6, 'NONE': 4} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 248 | 34.7% | 69.8% | 34.7% | 16.1% | 14.1% | 10.9% | 23.8% | 1.56 |
| 正式推薦 | 210 | 34.3% | 62.9% | 62.9% | 70.5% | 100.0% | 62.9% | 30.0% | 1.4 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中37.1%（無作為9.8%、差+27.4）／P2 平均1.0頭 的中16.4%（無作為9.8%、差+6.7）／P3 平均1.0頭 的中14.3%（無作為9.8%、差+4.5）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中67.7%（無作為29.1%、差+38.5）／P2 平均6.0頭 的中69.2%（無作為58.3%、差+10.9）／P3 平均10.59頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.84/40（選択性補正込み）・能力順位 14.01/20（68R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.58/40（選択性補正込み）・能力順位 13.55/20（61R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（7.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）3R・着順まで的中 0R／的中 5R のうち的中赤字 2R／損益分岐の倍率 平均 7.8倍／同じ点数を無作為に選んだ場合の期待PFS 37.7%（同じ11Rの実績 61.2%）／券種別 EXACTA 3点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 55点 PFS 42.4%／WIDE 20点 PFS 146.5%／荒れ度（発走前・1番人気オッズ）MID 3R PFS 111.0% 的中赤字 1/2／SOLID 8R PFS 45.1% 的中赤字 1/3／市場ミラーとの差 11R：実績 61.2% − ミラー 95.6% = Δ -34.4pt（95%区間 -156.2〜70.4、最高1R除き -64.3pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 25,100円（38.0%）／保護層の資金比率 0.0（11R）／組だけ的中（三連単は外れ）3R・着順まで的中 2R／的中 3R のうち的中赤字 3R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 29.0%（同じ11Rの実績 11.0%）／券種別 EXACTA 165点 PFS 7.9%／TRIFECTA 275点 PFS 12.9%／TRIO 220点 PFS 10.8%／荒れ度（発走前・1番人気オッズ）MID 3R PFS 17.9% 的中赤字 1/1／SOLID 8R PFS 8.4% 的中赤字 2/2／市場ミラーとの差 11R：実績 11.0% − ミラー 155.2% = Δ -144.2pt（95%区間 -349.6〜-10.1、最高1R除き -158.7pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 102 | 491,930 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 70 | 261,030 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 51 | 264,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 248 | 991,330 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 4 | 22,410 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

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

- 反省済みRace 56／PAPER PFS 51.0%／正式推薦 PFS 43.1%
- 第一失敗：{'PREDICTION_ROLE_P2': 13, 'CAPITAL_EFFICIENCY': 19, 'PREDICTION_ROLE_W': 20, 'NONE': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 10 | 20.2 | 94.3 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 1} |
| MIZ | 21 | 47.9 | 22.9 | {'PREDICTION_ROLE_W': 7, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 7, 'NONE': 1} |
| NGY | 5 | 48.4 | 27.0 | {'PREDICTION_ROLE_W': 4, 'CAPITAL_EFFICIENCY': 1} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| URW | 9 | 134.9 | 75.1 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 2, 'NONE': 2, 'PREDICTION_ROLE_P2': 2} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 56 | 33.9% | 69.6% | 33.9% | 8.9% | 12.5% | 5.4% | 25.0% | 1.5 |
| 正式推薦 | 56 | 35.7% | 64.3% | 64.3% | 75.0% | 100.0% | 64.3% | 46.4% | 1.54 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中33.9%（無作為10.1%、差+23.8）／P2 平均1.0頭 的中8.9%（無作為10.1%、差-1.2）／P3 平均1.0頭 的中12.5%（無作為10.1%、差+2.4）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中64.3%（無作為30.4%、差+33.9）／P2 平均6.0頭 的中75.0%（無作為60.8%、差+14.2）／P3 平均10.09頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.38/40（選択性補正込み）・能力順位 13.85/20（56R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.89/40（選択性補正込み）・能力順位 13.35/20（56R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（5.5%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）15R・着順まで的中 0R／的中 18R のうち的中赤字 8R／損益分岐の倍率 平均 7.8倍／同じ点数を無作為に選んだ場合の期待PFS 41.5%（同じ56Rの実績 51.0%）／券種別 EXACTA 16点 PFS 0.0%／TRIFECTA 32点 PFS 0.0%／TRIO 288点 PFS 56.5%／WIDE 100点 PFS 60.6%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 24R PFS 63.0% 的中赤字 4/9／OPEN 4R PFS 82.5% 的中赤字 0/2／SOLID 28R PFS 37.7% 的中赤字 4/7／市場ミラーとの差 56R：実績 51.0% − ミラー 48.4% = Δ 2.6pt（95%区間 -35.3〜45.7、最高1R除き -8.6pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 127,200円（37.9%）／保護層の資金比率 0.0（56R）／組だけ的中（三連単は外れ）20R・着順まで的中 9R／的中 30R のうち的中赤字 25R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 37.9%（同じ56Rの実績 43.1%）／券種別 EXACTA 840点 PFS 43.2%／TRIFECTA 1400点 PFS 20.0%／TRIO 1120点 PFS 71.8%／荒れ度（発走前・1番人気オッズ）MID 24R PFS 67.0% 的中赤字 10/13／OPEN 4R PFS 27.3% 的中赤字 2/2／SOLID 28R PFS 24.9% 的中赤字 13/15／市場ミラーとの差 56R：実績 43.1% − ミラー 106.0% = Δ -62.9pt（95%区間 -129.9〜-1.7、最高1R除き -78.5pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 25 | 93,570 | RECURRING |
| P1:ROLE_W_MISS | P1 | 20 | 102,520 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 13 | 78,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 56 | 249,570 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 293／PAPER PFS 58.5%／正式推薦 PFS 83.7%
- 第一失敗：{'NONE': 38, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 73, 'PREDICTION_ROLE_W': 95, 'PREDICTION_ROLE_P2': 50, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 34 | 79.4 | 66.2 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 57 | 53.2 | 29.9 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 6, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 14, 'PREDICTION_ROLE_W': 12, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 5 | 48.4 | 27.0 | {'PREDICTION_ROLE_W': 4, 'CAPITAL_EFFICIENCY': 1} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 36 | 23.6 | 56.9 | {'PREDICTION_ROLE_W': 16, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_P2': 6, 'NONE': 4} |
| URW | 9 | 134.9 | 75.1 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 2, 'NONE': 2, 'PREDICTION_ROLE_P2': 2} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 293 | 33.8% | 69.3% | 33.8% | 15.0% | 13.7% | 9.9% | 23.9% | 1.55 |
| 正式推薦 | 255 | 33.7% | 62.7% | 62.7% | 72.5% | 100.0% | 62.7% | 33.7% | 1.43 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中35.1%（無作為9.8%、差+25.3）／P2 平均1.0頭 的中14.6%（無作為9.8%、差+4.8）／P3 平均1.0頭 的中13.5%（無作為9.8%、差+3.7）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中66.3%（無作為29.4%、差+36.9）／P2 平均6.0頭 的中72.5%（無作為58.8%、差+13.7）／P3 平均10.49頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.01/40（選択性補正込み）・能力順位 13.94/20（113R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.42/40（選択性補正込み）・能力順位 13.53/20（106R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（5.5%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）15R・着順まで的中 0R／的中 18R のうち的中赤字 8R／損益分岐の倍率 平均 7.8倍／同じ点数を無作為に選んだ場合の期待PFS 41.5%（同じ56Rの実績 51.0%）／券種別 EXACTA 16点 PFS 0.0%／TRIFECTA 32点 PFS 0.0%／TRIO 288点 PFS 56.5%／WIDE 100点 PFS 60.6%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 24R PFS 63.0% 的中赤字 4/9／OPEN 4R PFS 82.5% 的中赤字 0/2／SOLID 28R PFS 37.7% 的中赤字 4/7／市場ミラーとの差 56R：実績 51.0% − ミラー 48.4% = Δ 2.6pt（95%区間 -35.3〜45.7、最高1R除き -8.6pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 127,200円（37.9%）／保護層の資金比率 0.0（56R）／組だけ的中（三連単は外れ）20R・着順まで的中 9R／的中 30R のうち的中赤字 25R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 37.9%（同じ56Rの実績 43.1%）／券種別 EXACTA 840点 PFS 43.2%／TRIFECTA 1400点 PFS 20.0%／TRIO 1120点 PFS 71.8%／荒れ度（発走前・1番人気オッズ）MID 24R PFS 67.0% 的中赤字 10/13／OPEN 4R PFS 27.3% 的中赤字 2/2／SOLID 28R PFS 24.9% 的中赤字 13/15／市場ミラーとの差 56R：実績 43.1% − ミラー 106.0% = Δ -62.9pt（95%区間 -129.9〜-1.7、最高1R除き -78.5pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 119 | 576,450 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 92 | 343,830 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 59 | 312,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 293 | 1,182,130 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

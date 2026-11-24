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

- 反省済みRace 47／PAPER PFS 44.3%／正式推薦 PFS 38.2%
- 第一失敗：{'PREDICTION_ROLE_P2': 11, 'CAPITAL_EFFICIENCY': 17, 'PREDICTION_ROLE_W': 17, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 10 | 20.2 | 94.3 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 1} |
| MIZ | 18 | 45.0 | 14.1 | {'PREDICTION_ROLE_W': 6, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 6} |
| NGY | 2 | 0.0 | 0.0 | {'PREDICTION_ROLE_W': 2} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| URW | 6 | 145.0 | 70.0 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 2, 'NONE': 1} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 47 | 38.3% | 72.3% | 38.3% | 10.6% | 12.8% | 6.4% | 23.4% | 1.47 |
| 正式推薦 | 47 | 34.0% | 63.8% | 63.8% | 74.5% | 100.0% | 63.8% | 42.6% | 1.53 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中38.3%（無作為10.3%、差+28.0）／P2 平均1.0頭 的中10.6%（無作為10.3%、差+0.3）／P3 平均1.0頭 的中12.8%（無作為10.3%、差+2.5）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.8%（無作為30.9%、差+32.9）／P2 平均6.0頭 的中74.5%（無作為61.8%、差+12.7）／P3 平均9.94頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.77/40（選択性補正込み）・能力順位 13.73/20（47R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.45/40（選択性補正込み）・能力順位 13.02/20（47R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（6.5%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）12R・着順まで的中 0R／的中 14R のうち的中赤字 7R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 45.6%（同じ47Rの実績 44.3%）／券種別 EXACTA 16点 PFS 0.0%／TRIFECTA 32点 PFS 0.0%／TRIO 239点 PFS 48.7%／WIDE 82点 PFS 58.4%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 17R PFS 41.1% 的中赤字 3/5／OPEN 3R PFS 114.8% 的中赤字 0/2／SOLID 27R PFS 38.9% 的中赤字 4/7／市場ミラーとの差 47R：実績 44.3% − ミラー 54.3% = Δ -9.9pt（95%区間 -51.1〜32.1、最高1R除き -23.4pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 106,400円（37.7%）／保護層の資金比率 0.0（47R）／組だけ的中（三連単は外れ）15R・着順まで的中 8R／的中 23R のうち的中赤字 20R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 38.8%（同じ47Rの実績 38.2%）／券種別 EXACTA 705点 PFS 34.2%／TRIFECTA 1175点 PFS 14.6%／TRIO 940点 PFS 70.8%／荒れ度（発走前・1番人気オッズ）MID 17R PFS 65.6% 的中赤字 7/8／OPEN 3R PFS 8.4% 的中赤字 1/1／SOLID 27R PFS 24.3% 的中赤字 12/14／市場ミラーとの差 47R：実績 38.2% − ミラー 102.7% = Δ -64.4pt（95%区間 -140.1〜3.4、最高1R除き -83.2pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 20 | 77,030 | RECURRING |
| P1:ROLE_W_MISS | P1 | 17 | 93,280 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 11 | 66,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 47 | 221,030 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 284／PAPER PFS 57.6%／正式推薦 PFS 84.3%
- 第一失敗：{'NONE': 36, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 71, 'PREDICTION_ROLE_W': 92, 'PREDICTION_ROLE_P2': 48, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 34 | 79.4 | 66.2 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 54 | 52.5 | 26.7 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 5, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 13, 'PREDICTION_ROLE_W': 11, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 2 | 0.0 | 0.0 | {'PREDICTION_ROLE_W': 2} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 36 | 23.6 | 56.9 | {'PREDICTION_ROLE_W': 16, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_P2': 6, 'NONE': 4} |
| URW | 6 | 145.0 | 70.0 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 2, 'NONE': 1} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 284 | 34.5% | 69.7% | 34.5% | 15.5% | 13.7% | 10.2% | 23.6% | 1.55 |
| 正式推薦 | 246 | 33.3% | 62.6% | 62.6% | 72.4% | 100.0% | 62.6% | 32.5% | 1.43 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中36.4%（無作為9.9%、差+26.5）／P2 平均1.0頭 的中15.3%（無作為9.9%、差+5.5）／P3 平均1.0頭 的中13.6%（無作為9.9%、差+3.8）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中66.3%（無作為29.5%、差+36.8）／P2 平均6.0頭 的中72.2%（無作為58.9%、差+13.2）／P3 平均10.47頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.24/40（選択性補正込み）・能力順位 13.9/20（104R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.26/40（選択性補正込み）・能力順位 13.39/20（97R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（6.5%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）12R・着順まで的中 0R／的中 14R のうち的中赤字 7R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 45.6%（同じ47Rの実績 44.3%）／券種別 EXACTA 16点 PFS 0.0%／TRIFECTA 32点 PFS 0.0%／TRIO 239点 PFS 48.7%／WIDE 82点 PFS 58.4%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 17R PFS 41.1% 的中赤字 3/5／OPEN 3R PFS 114.8% 的中赤字 0/2／SOLID 27R PFS 38.9% 的中赤字 4/7／市場ミラーとの差 47R：実績 44.3% − ミラー 54.3% = Δ -9.9pt（95%区間 -51.1〜32.1、最高1R除き -23.4pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 106,400円（37.7%）／保護層の資金比率 0.0（47R）／組だけ的中（三連単は外れ）15R・着順まで的中 8R／的中 23R のうち的中赤字 20R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 38.8%（同じ47Rの実績 38.2%）／券種別 EXACTA 705点 PFS 34.2%／TRIFECTA 1175点 PFS 14.6%／TRIO 940点 PFS 70.8%／荒れ度（発走前・1番人気オッズ）MID 17R PFS 65.6% 的中赤字 7/8／OPEN 3R PFS 8.4% 的中赤字 1/1／SOLID 27R PFS 24.3% 的中赤字 12/14／市場ミラーとの差 47R：実績 38.2% − ミラー 102.7% = Δ -64.4pt（95%区間 -140.1〜3.4、最高1R除き -83.2pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 116 | 567,210 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 87 | 327,290 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 57 | 300,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 284 | 1,153,590 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

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

- 反省済みRace 54／PAPER PFS 47.0%／正式推薦 PFS 39.4%
- 第一失敗：{'PREDICTION_ROLE_P2': 13, 'CAPITAL_EFFICIENCY': 18, 'PREDICTION_ROLE_W': 20, 'NONE': 3}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 10 | 20.2 | 94.3 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 1} |
| MIZ | 21 | 47.9 | 22.9 | {'PREDICTION_ROLE_W': 7, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 7, 'NONE': 1} |
| NGY | 4 | 59.7 | 26.4 | {'PREDICTION_ROLE_W': 4} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| URW | 8 | 109.8 | 52.5 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 2, 'NONE': 1, 'PREDICTION_ROLE_P2': 2} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 54 | 33.3% | 68.5% | 33.3% | 9.3% | 13.0% | 5.6% | 24.1% | 1.5 |
| 正式推薦 | 54 | 35.2% | 63.0% | 63.0% | 74.1% | 100.0% | 63.0% | 46.3% | 1.54 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中33.3%（無作為10.2%、差+23.2）／P2 平均1.0頭 的中9.3%（無作為10.2%、差-0.9）／P3 平均1.0頭 的中13.0%（無作為10.2%、差+2.8）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.0%（無作為30.5%、差+32.5）／P2 平均6.0頭 的中74.1%（無作為60.9%、差+13.2）／P3 平均10.07頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.37/40（選択性補正込み）・能力順位 13.79/20（54R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.69/40（選択性補正込み）・能力順位 13.27/20（54R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（5.7%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）14R・着順まで的中 0R／的中 17R のうち的中赤字 8R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 42.3%（同じ54Rの実績 47.0%）／券種別 EXACTA 16点 PFS 0.0%／TRIFECTA 32点 PFS 0.0%／TRIO 278点 PFS 50.6%／WIDE 96点 PFS 61.0%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 22R PFS 53.5% 的中赤字 4/8／OPEN 4R PFS 82.5% 的中赤字 0/2／SOLID 28R PFS 37.7% 的中赤字 4/7／市場ミラーとの差 54R：実績 47.0% − ミラー 49.2% = Δ -2.2pt（95%区間 -40.7〜38.2、最高1R除き -13.9pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 122,500円（37.8%）／保護層の資金比率 0.0（54R）／組だけ的中（三連単は外れ）20R・着順まで的中 8R／的中 28R のうち的中赤字 24R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 38.8%（同じ54Rの実績 39.4%）／券種別 EXACTA 810点 PFS 39.9%／TRIFECTA 1350点 PFS 12.7%／TRIO 1080点 PFS 72.5%／荒れ度（発走前・1番人気オッズ）MID 22R PFS 60.1% 的中赤字 9/11／OPEN 4R PFS 27.3% 的中赤字 2/2／SOLID 28R PFS 24.9% 的中赤字 13/15／市場ミラーとの差 54R：実績 39.4% − ミラー 109.0% = Δ -69.6pt（95%区間 -137.9〜-5.7、最高1R除き -85.9pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 24 | 89,320 | RECURRING |
| P1:ROLE_W_MISS | P1 | 20 | 102,520 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 13 | 78,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 54 | 245,320 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 291／PAPER PFS 57.8%／正式推薦 PFS 83.3%
- 第一失敗：{'NONE': 37, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 72, 'PREDICTION_ROLE_W': 95, 'PREDICTION_ROLE_P2': 50, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 34 | 79.4 | 66.2 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 57 | 53.2 | 29.9 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 6, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 14, 'PREDICTION_ROLE_W': 12, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 4 | 59.7 | 26.4 | {'PREDICTION_ROLE_W': 4} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 36 | 23.6 | 56.9 | {'PREDICTION_ROLE_W': 16, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_P2': 6, 'NONE': 4} |
| URW | 8 | 109.8 | 52.5 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 2, 'NONE': 1, 'PREDICTION_ROLE_P2': 2} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 291 | 33.7% | 69.1% | 33.7% | 15.1% | 13.7% | 10.0% | 23.7% | 1.55 |
| 正式推薦 | 253 | 33.6% | 62.5% | 62.5% | 72.3% | 100.0% | 62.5% | 33.6% | 1.43 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中35.0%（無作為9.8%、差+25.1）／P2 平均1.0頭 的中14.8%（無作為9.8%、差+4.9）／P3 平均1.0頭 的中13.7%（無作為9.8%、差+3.8）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中65.9%（無作為29.4%、差+36.5）／P2 平均6.0頭 的中72.2%（無作為58.8%、差+13.4）／P3 平均10.49頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.02/40（選択性補正込み）・能力順位 13.92/20（111R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.33/40（選択性補正込み）・能力順位 13.49/20（104R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（5.7%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）14R・着順まで的中 0R／的中 17R のうち的中赤字 8R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 42.3%（同じ54Rの実績 47.0%）／券種別 EXACTA 16点 PFS 0.0%／TRIFECTA 32点 PFS 0.0%／TRIO 278点 PFS 50.6%／WIDE 96点 PFS 61.0%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 22R PFS 53.5% 的中赤字 4/8／OPEN 4R PFS 82.5% 的中赤字 0/2／SOLID 28R PFS 37.7% 的中赤字 4/7／市場ミラーとの差 54R：実績 47.0% − ミラー 49.2% = Δ -2.2pt（95%区間 -40.7〜38.2、最高1R除き -13.9pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 122,500円（37.8%）／保護層の資金比率 0.0（54R）／組だけ的中（三連単は外れ）20R・着順まで的中 8R／的中 28R のうち的中赤字 24R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 38.8%（同じ54Rの実績 39.4%）／券種別 EXACTA 810点 PFS 39.9%／TRIFECTA 1350点 PFS 12.7%／TRIO 1080点 PFS 72.5%／荒れ度（発走前・1番人気オッズ）MID 22R PFS 60.1% 的中赤字 9/11／OPEN 4R PFS 27.3% 的中赤字 2/2／SOLID 28R PFS 24.9% 的中赤字 13/15／市場ミラーとの差 54R：実績 39.4% − ミラー 109.0% = Δ -69.6pt（95%区間 -137.9〜-5.7、最高1R除き -85.9pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 119 | 576,450 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 91 | 339,580 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 59 | 312,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 291 | 1,177,880 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

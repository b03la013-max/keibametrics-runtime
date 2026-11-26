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

- 反省済みRace 148／PAPER PFS 67.6%／正式推薦 PFS 40.9%
- 第一失敗：{'PREDICTION_ROLE_P2': 25, 'CAPITAL_EFFICIENCY': 56, 'PREDICTION_ROLE_W': 56, 'NONE': 11}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 20 | 59.0 | 64.9 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 12, 'PREDICTION_ROLE_W': 5, 'NONE': 1} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 33 | 71.6 | 44.9 | {'PREDICTION_ROLE_W': 12, 'CAPITAL_EFFICIENCY': 10, 'NONE': 5, 'PREDICTION_ROLE_P2': 6} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 24 | 105.1 | 47.9 | {'PREDICTION_ROLE_W': 14, 'NONE': 1, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 7} |
| URW | 36 | 68.6 | 29.8 | {'CAPITAL_EFFICIENCY': 14, 'PREDICTION_ROLE_W': 14, 'NONE': 2, 'PREDICTION_ROLE_P2': 6} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 148 | 30.4% | 64.9% | 30.4% | 11.5% | 11.5% | 7.4% | 25.0% | 1.51 |
| 正式推薦 | 148 | 29.7% | 62.2% | 62.2% | 74.3% | 100.0% | 62.2% | 44.6% | 1.48 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中30.4%（無作為9.4%、差+21.0）／P2 平均1.0頭 的中11.5%（無作為9.4%、差+2.0）／P3 平均1.0頭 的中11.5%（無作為9.4%、差+2.0）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中62.2%（無作為28.3%、差+33.8）／P2 平均6.0頭 的中74.3%（無作為56.7%、差+17.7）／P3 平均10.84頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.1/40（選択性補正込み）・能力順位 13.84/20（148R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.18/40（選択性補正込み）・能力順位 13.4/20（148R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 7,800円（6.6%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）38R・着順まで的中 2R／的中 55R のうち的中赤字 26R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 54.3%（同じ148Rの実績 67.6%）／券種別 EXACTA 57点 PFS 20.5%／TRIFECTA 104点 PFS 15.4%／TRIO 762点 PFS 64.5%／WIDE 252点 PFS 109.6%／WIN 9点 PFS 56.7%／荒れ度（発走前・1番人気オッズ）MID 77R PFS 75.7% 的中赤字 12/28／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 63R PFS 55.5% 的中赤字 14/24／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 146R：実績 65.5% − ミラー 44.7% = Δ 20.8pt（95%区間 -5.1〜49.3、最高1R除き 14.0pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 339,900円（38.3%）／保護層の資金比率 0.0（148R）／組だけ的中（三連単は外れ）46R・着順まで的中 25R／的中 83R のうち的中赤字 70R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 51.0%（同じ148Rの実績 40.9%）／券種別 EXACTA 2220点 PFS 50.0%／TRIFECTA 3700点 PFS 22.6%／TRIO 2960点 PFS 57.0%／荒れ度（発走前・1番人気オッズ）MID 77R PFS 48.9% 的中赤字 34/42／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 63R PFS 33.9% 的中赤字 32/37／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 146R：実績 41.2% − ミラー 69.8% = Δ -28.7pt（95%区間 -56.9〜-1.2、最高1R除き -34.4pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、43R×3券種）：購入 17／予算で削除 0／予想で除外 37／未生成・券種なし 75／役割馬の行き先 {'PURCHASED': 129}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、43R×3券種）：購入 57／予算で削除 17／予想で除外 36／未生成・券種なし 19／役割馬の行き先 {'PURCHASED': 316, 'BUDGET_COMPRESSED': 155}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 16R／W外 27R、2着が P2 役割 2R）：STATIC 2/16（平均4.0位）／STYLE_COND 4/16（平均3.75位） 救済2・喪失0／MARKET_COND 4/15（平均3.07位） 救済3・喪失1
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 31R／W外 12R、2着が P2 役割 25R）：STATIC 26/31（平均3.87位）／STYLE_COND 26/31（平均3.74位） 救済0・喪失0／MARKET_COND 28/30（平均2.8位） 救済3・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 70 | 247,890 | RECURRING |
| P1:ROLE_W_MISS | P1 | 56 | 294,370 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 25 | 150,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 148 | 637,890 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 385／PAPER PFS 63.0%／正式推薦 PFS 72.2%
- 第一失敗：{'NONE': 45, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 110, 'PREDICTION_ROLE_W': 131, 'PREDICTION_ROLE_P2': 62, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 44 | 83.5 | 56.8 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 17, 'PREDICTION_ROLE_W': 9, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 33 | 71.6 | 44.9 | {'PREDICTION_ROLE_W': 12, 'CAPITAL_EFFICIENCY': 10, 'NONE': 5, 'PREDICTION_ROLE_P2': 6} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 60 | 57.0 | 53.3 | {'PREDICTION_ROLE_W': 30, 'CAPITAL_EFFICIENCY': 17, 'PREDICTION_ROLE_P2': 8, 'NONE': 5} |
| URW | 36 | 68.6 | 29.8 | {'CAPITAL_EFFICIENCY': 14, 'PREDICTION_ROLE_W': 14, 'NONE': 2, 'PREDICTION_ROLE_P2': 6} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 385 | 32.5% | 67.5% | 32.5% | 14.5% | 13.0% | 9.6% | 24.2% | 1.54 |
| 正式推薦 | 347 | 31.7% | 62.2% | 62.2% | 72.9% | 100.0% | 62.2% | 36.3% | 1.44 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中32.9%（無作為9.6%、差+23.3）／P2 平均1.0頭 的中14.1%（無作為9.6%、差+4.5）／P3 平均1.0頭 的中12.6%（無作為9.6%、差+3.1）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中64.4%（無作為28.6%、差+35.8）／P2 平均6.0頭 的中73.0%（無作為57.2%、差+15.8）／P3 平均10.76頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.53/40（選択性補正込み）・能力順位 13.89/20（205R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.39/40（選択性補正込み）・能力順位 13.49/20（198R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 7,800円（6.6%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）38R・着順まで的中 2R／的中 55R のうち的中赤字 26R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 54.3%（同じ148Rの実績 67.6%）／券種別 EXACTA 57点 PFS 20.5%／TRIFECTA 104点 PFS 15.4%／TRIO 762点 PFS 64.5%／WIDE 252点 PFS 109.6%／WIN 9点 PFS 56.7%／荒れ度（発走前・1番人気オッズ）MID 77R PFS 75.7% 的中赤字 12/28／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 63R PFS 55.5% 的中赤字 14/24／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 146R：実績 65.5% − ミラー 44.7% = Δ 20.8pt（95%区間 -5.1〜49.3、最高1R除き 14.0pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 339,900円（38.3%）／保護層の資金比率 0.0（148R）／組だけ的中（三連単は外れ）46R・着順まで的中 25R／的中 83R のうち的中赤字 70R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 51.0%（同じ148Rの実績 40.9%）／券種別 EXACTA 2220点 PFS 50.0%／TRIFECTA 3700点 PFS 22.6%／TRIO 2960点 PFS 57.0%／荒れ度（発走前・1番人気オッズ）MID 77R PFS 48.9% 的中赤字 34/42／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 63R PFS 33.9% 的中赤字 32/37／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 146R：実績 41.2% − ミラー 69.8% = Δ -28.7pt（95%区間 -56.9〜-1.2、最高1R除き -34.4pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、43R×3券種）：購入 17／予算で削除 0／予想で除外 37／未生成・券種なし 75／役割馬の行き先 {'PURCHASED': 129}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、43R×3券種）：購入 57／予算で削除 17／予想で除外 36／未生成・券種なし 19／役割馬の行き先 {'PURCHASED': 316, 'BUDGET_COMPRESSED': 155}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 16R／W外 27R、2着が P2 役割 2R）：STATIC 2/16（平均4.0位）／STYLE_COND 4/16（平均3.75位） 救済2・喪失0／MARKET_COND 4/15（平均3.07位） 救済3・喪失1
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 31R／W外 12R、2着が P2 役割 25R）：STATIC 26/31（平均3.87位）／STYLE_COND 26/31（平均3.74位） 救済0・喪失0／MARKET_COND 28/30（平均2.8位） 救済3・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 155 | 768,300 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 137 | 498,150 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 71 | 384,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 385 | 1,570,450 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

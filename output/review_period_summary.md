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

- 反省済みRace 144／PAPER PFS 68.5%／正式推薦 PFS 40.6%
- 第一失敗：{'PREDICTION_ROLE_P2': 25, 'CAPITAL_EFFICIENCY': 52, 'PREDICTION_ROLE_W': 56, 'NONE': 11}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 18 | 58.2 | 67.8 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_W': 5, 'NONE': 1} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 31 | 75.7 | 43.6 | {'PREDICTION_ROLE_W': 12, 'CAPITAL_EFFICIENCY': 8, 'NONE': 5, 'PREDICTION_ROLE_P2': 6} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 24 | 105.1 | 47.9 | {'PREDICTION_ROLE_W': 14, 'NONE': 1, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 7} |
| URW | 36 | 68.6 | 29.8 | {'CAPITAL_EFFICIENCY': 14, 'PREDICTION_ROLE_W': 14, 'NONE': 2, 'PREDICTION_ROLE_P2': 6} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 144 | 29.2% | 63.9% | 29.2% | 11.1% | 11.8% | 6.2% | 25.0% | 1.51 |
| 正式推薦 | 144 | 29.2% | 61.1% | 61.1% | 73.6% | 100.0% | 61.1% | 43.8% | 1.48 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中29.2%（無作為9.4%、差+19.7）／P2 平均1.0頭 的中11.1%（無作為9.4%、差+1.7）／P3 平均1.0頭 的中11.8%（無作為9.4%、差+2.4）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中61.1%（無作為28.3%、差+32.8）／P2 平均6.0頭 的中73.6%（無作為56.6%、差+17.0）／P3 平均10.85頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.94/40（選択性補正込み）・能力順位 13.8/20（144R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.05/40（選択性補正込み）・能力順位 13.37/20（144R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 7,200円（6.3%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）38R・着順まで的中 1R／的中 53R のうち的中赤字 24R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 55.8%（同じ144Rの実績 68.5%）／券種別 EXACTA 52点 PFS 13.8%／TRIFECTA 96点 PFS 6.1%／TRIO 742点 PFS 66.3%／WIDE 248点 PFS 111.4%／WIN 8点 PFS 43.8%／荒れ度（発走前・1番人気オッズ）MID 74R PFS 78.4% 的中赤字 11/27／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 62R PFS 54.4% 的中赤字 13/23／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 142R：実績 66.3% − ミラー 41.9% = Δ 24.4pt（95%区間 -2.0〜53.9、最高1R除き 17.3pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 330,800円（38.3%）／保護層の資金比率 0.0（144R）／組だけ的中（三連単は外れ）45R・着順まで的中 23R／的中 79R のうち的中赤字 66R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 52.1%（同じ144Rの実績 40.6%）／券種別 EXACTA 2160点 PFS 48.1%／TRIFECTA 3600点 PFS 22.3%／TRIO 2880点 PFS 57.8%／荒れ度（発走前・1番人気オッズ）MID 74R PFS 48.5% 的中赤字 31/39／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 62R PFS 34.0% 的中赤字 31/36／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 142R：実績 40.9% − ミラー 69.9% = Δ -29.0pt（95%区間 -58.1〜-2.6、最高1R除き -34.9pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、39R×3券種）：購入 15／予算で削除 0／予想で除外 32／未生成・券種なし 70／役割馬の行き先 {'PURCHASED': 117}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、39R×3券種）：購入 48／予算で削除 15／予想で除外 36／未生成・券種なし 18／役割馬の行き先 {'PURCHASED': 286, 'BUDGET_COMPRESSED': 144}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 13R／W外 26R、2着が P2 役割 1R）：STATIC 1/13（平均4.23位）／STYLE_COND 3/13（平均4.0位） 救済2・喪失0／MARKET_COND 3/12（平均3.33位） 救済2・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 27R／W外 12R、2着が P2 役割 21R）：STATIC 22/27（平均3.78位）／STYLE_COND 22/27（平均3.63位） 救済0・喪失0／MARKET_COND 24/26（平均2.92位） 救済3・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 66 | 236,300 | RECURRING |
| P1:ROLE_W_MISS | P1 | 56 | 294,370 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 25 | 150,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 144 | 626,300 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 381／PAPER PFS 63.3%／正式推薦 PFS 72.5%
- 第一失敗：{'NONE': 45, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 106, 'PREDICTION_ROLE_W': 131, 'PREDICTION_ROLE_P2': 62, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 42 | 84.9 | 57.9 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 9, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 31 | 75.7 | 43.6 | {'PREDICTION_ROLE_W': 12, 'CAPITAL_EFFICIENCY': 8, 'NONE': 5, 'PREDICTION_ROLE_P2': 6} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 60 | 57.0 | 53.3 | {'PREDICTION_ROLE_W': 30, 'CAPITAL_EFFICIENCY': 17, 'PREDICTION_ROLE_P2': 8, 'NONE': 5} |
| URW | 36 | 68.6 | 29.8 | {'CAPITAL_EFFICIENCY': 14, 'PREDICTION_ROLE_W': 14, 'NONE': 2, 'PREDICTION_ROLE_P2': 6} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 381 | 32.0% | 67.2% | 32.0% | 14.4% | 13.1% | 9.2% | 24.1% | 1.54 |
| 正式推薦 | 343 | 31.5% | 61.8% | 61.8% | 72.6% | 100.0% | 61.8% | 35.9% | 1.43 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中32.2%（無作為9.6%、差+22.7）／P2 平均1.0頭 的中13.9%（無作為9.6%、差+4.4）／P3 平均1.0頭 的中12.8%（無作為9.6%、差+3.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.9%（無作為28.6%、差+35.3）／P2 平均6.0頭 的中72.6%（無作為57.2%、差+15.4）／P3 平均10.77頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.42/40（選択性補正込み）・能力順位 13.87/20（201R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.3/40（選択性補正込み）・能力順位 13.46/20（194R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 7,200円（6.3%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）38R・着順まで的中 1R／的中 53R のうち的中赤字 24R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 55.8%（同じ144Rの実績 68.5%）／券種別 EXACTA 52点 PFS 13.8%／TRIFECTA 96点 PFS 6.1%／TRIO 742点 PFS 66.3%／WIDE 248点 PFS 111.4%／WIN 8点 PFS 43.8%／荒れ度（発走前・1番人気オッズ）MID 74R PFS 78.4% 的中赤字 11/27／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 62R PFS 54.4% 的中赤字 13/23／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 142R：実績 66.3% − ミラー 41.9% = Δ 24.4pt（95%区間 -2.0〜53.9、最高1R除き 17.3pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 330,800円（38.3%）／保護層の資金比率 0.0（144R）／組だけ的中（三連単は外れ）45R・着順まで的中 23R／的中 79R のうち的中赤字 66R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 52.1%（同じ144Rの実績 40.6%）／券種別 EXACTA 2160点 PFS 48.1%／TRIFECTA 3600点 PFS 22.3%／TRIO 2880点 PFS 57.8%／荒れ度（発走前・1番人気オッズ）MID 74R PFS 48.5% 的中赤字 31/39／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 62R PFS 34.0% 的中赤字 31/36／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 142R：実績 40.9% − ミラー 69.9% = Δ -29.0pt（95%区間 -58.1〜-2.6、最高1R除き -34.9pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、39R×3券種）：購入 15／予算で削除 0／予想で除外 32／未生成・券種なし 70／役割馬の行き先 {'PURCHASED': 117}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、39R×3券種）：購入 48／予算で削除 15／予想で除外 36／未生成・券種なし 18／役割馬の行き先 {'PURCHASED': 286, 'BUDGET_COMPRESSED': 144}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 13R／W外 26R、2着が P2 役割 1R）：STATIC 1/13（平均4.23位）／STYLE_COND 3/13（平均4.0位） 救済2・喪失0／MARKET_COND 3/12（平均3.33位） 救済2・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 27R／W外 12R、2着が P2 役割 21R）：STATIC 22/27（平均3.78位）／STYLE_COND 22/27（平均3.63位） 救済0・喪失0／MARKET_COND 24/26（平均2.92位） 救済3・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 155 | 768,300 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 133 | 486,560 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 71 | 384,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 381 | 1,558,860 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

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

- 反省済みRace 151／PAPER PFS 66.0%／正式推薦 PFS 43.3%
- 第一失敗：{'PREDICTION_ROLE_P2': 25, 'CAPITAL_EFFICIENCY': 56, 'PREDICTION_ROLE_W': 57, 'NONE': 13}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 21 | 53.7 | 76.7 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 12, 'PREDICTION_ROLE_W': 5, 'NONE': 2} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 35 | 67.6 | 47.1 | {'PREDICTION_ROLE_W': 13, 'CAPITAL_EFFICIENCY': 10, 'NONE': 6, 'PREDICTION_ROLE_P2': 6} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 24 | 105.1 | 47.9 | {'PREDICTION_ROLE_W': 14, 'NONE': 1, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 7} |
| URW | 36 | 68.6 | 29.8 | {'CAPITAL_EFFICIENCY': 14, 'PREDICTION_ROLE_W': 14, 'NONE': 2, 'PREDICTION_ROLE_P2': 6} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 151 | 30.5% | 64.2% | 30.5% | 11.9% | 11.9% | 7.9% | 24.5% | 1.5 |
| 正式推薦 | 151 | 30.5% | 62.3% | 62.3% | 74.8% | 100.0% | 62.3% | 45.0% | 1.48 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中30.5%（無作為9.4%、差+21.0）／P2 平均1.0頭 的中11.9%（無作為9.4%、差+2.5）／P3 平均1.0頭 的中11.9%（無作為9.4%、差+2.5）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中62.3%（無作為28.3%、差+33.9）／P2 平均6.0頭 的中74.8%（無作為56.7%、差+18.2）／P3 平均10.83頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.14/40（選択性補正込み）・能力順位 13.84/20（151R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.23/40（選択性補正込み）・能力順位 13.43/20（151R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 8,400円（6.9%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）38R・着順まで的中 2R／的中 55R のうち的中赤字 26R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 53.7%（同じ151Rの実績 66.0%）／券種別 EXACTA 60点 PFS 19.5%／TRIFECTA 112点 PFS 14.3%／TRIO 777点 PFS 63.3%／WIDE 256点 PFS 107.9%／WIN 9点 PFS 56.7%／荒れ度（発走前・1番人気オッズ）MID 78R PFS 74.7% 的中赤字 12/28／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 65R PFS 53.3% 的中赤字 14/24／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 149R：実績 63.8% − ミラー 44.9% = Δ 19.0pt（95%区間 -5.6〜47.4、最高1R除き 12.3pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 346,700円（38.3%）／保護層の資金比率 0.0（151R）／組だけ的中（三連単は外れ）46R・着順まで的中 27R／的中 85R のうち的中赤字 70R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 50.4%（同じ151Rの実績 43.3%）／券種別 EXACTA 2265点 PFS 50.1%／TRIFECTA 3775点 PFS 26.9%／TRIO 3020点 PFS 58.5%／荒れ度（発走前・1番人気オッズ）MID 78R PFS 48.3% 的中赤字 34/42／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 65R PFS 40.3% 的中赤字 32/39／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 149R：実績 43.6% − ミラー 72.6% = Δ -29.1pt（95%区間 -57.5〜-1.4、最高1R除き -34.7pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、46R×3券種）：購入 17／予算で削除 0／予想で除外 42／未生成・券種なし 79／役割馬の行き先 {'PURCHASED': 138}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、46R×3券種）：購入 63／予算で削除 17／予想で除外 38／未生成・券種なし 20／役割馬の行き先 {'PURCHASED': 338, 'BUDGET_COMPRESSED': 165}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 17R／W外 29R、2着が P2 役割 2R）：STATIC 2/17（平均4.0位）／STYLE_COND 4/17（平均3.76位） 救済2・喪失0／MARKET_COND 4/16（平均3.0位） 救済3・喪失1
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 33R／W外 13R、2着が P2 役割 27R）：STATIC 28/33（平均3.88位）／STYLE_COND 28/33（平均3.73位） 救済0・喪失0／MARKET_COND 30/32（平均2.88位） 救済3・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 70 | 247,890 | RECURRING |
| P1:ROLE_W_MISS | P1 | 57 | 300,370 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 25 | 150,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 151 | 643,890 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 388／PAPER PFS 62.4%／正式推薦 PFS 73.0%
- 第一失敗：{'NONE': 47, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 110, 'PREDICTION_ROLE_W': 132, 'PREDICTION_ROLE_P2': 62, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 45 | 79.9 | 64.4 | {'NONE': 6, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 17, 'PREDICTION_ROLE_W': 9, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 35 | 67.6 | 47.1 | {'PREDICTION_ROLE_W': 13, 'CAPITAL_EFFICIENCY': 10, 'NONE': 6, 'PREDICTION_ROLE_P2': 6} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 60 | 57.0 | 53.3 | {'PREDICTION_ROLE_W': 30, 'CAPITAL_EFFICIENCY': 17, 'PREDICTION_ROLE_P2': 8, 'NONE': 5} |
| URW | 36 | 68.6 | 29.8 | {'CAPITAL_EFFICIENCY': 14, 'PREDICTION_ROLE_W': 14, 'NONE': 2, 'PREDICTION_ROLE_P2': 6} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 388 | 32.5% | 67.3% | 32.5% | 14.7% | 13.1% | 9.8% | 24.0% | 1.54 |
| 正式推薦 | 350 | 32.0% | 62.3% | 62.3% | 73.1% | 100.0% | 62.3% | 36.6% | 1.43 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中32.9%（無作為9.6%、差+23.3）／P2 平均1.0頭 的中14.3%（無作為9.6%、差+4.7）／P3 平均1.0頭 的中12.9%（無作為9.6%、差+3.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中64.5%（無作為28.6%、差+35.9）／P2 平均6.0頭 的中73.3%（無作為57.2%、差+16.1）／P3 平均10.76頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.55/40（選択性補正込み）・能力順位 13.89/20（208R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.42/40（選択性補正込み）・能力順位 13.5/20（201R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 8,400円（6.9%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）38R・着順まで的中 2R／的中 55R のうち的中赤字 26R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 53.7%（同じ151Rの実績 66.0%）／券種別 EXACTA 60点 PFS 19.5%／TRIFECTA 112点 PFS 14.3%／TRIO 777点 PFS 63.3%／WIDE 256点 PFS 107.9%／WIN 9点 PFS 56.7%／荒れ度（発走前・1番人気オッズ）MID 78R PFS 74.7% 的中赤字 12/28／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 65R PFS 53.3% 的中赤字 14/24／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 149R：実績 63.8% − ミラー 44.9% = Δ 19.0pt（95%区間 -5.6〜47.4、最高1R除き 12.3pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 346,700円（38.3%）／保護層の資金比率 0.0（151R）／組だけ的中（三連単は外れ）46R・着順まで的中 27R／的中 85R のうち的中赤字 70R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 50.4%（同じ151Rの実績 43.3%）／券種別 EXACTA 2265点 PFS 50.1%／TRIFECTA 3775点 PFS 26.9%／TRIO 3020点 PFS 58.5%／荒れ度（発走前・1番人気オッズ）MID 78R PFS 48.3% 的中赤字 34/42／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 65R PFS 40.3% 的中赤字 32/39／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 149R：実績 43.6% − ミラー 72.6% = Δ -29.1pt（95%区間 -57.5〜-1.4、最高1R除き -34.7pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、46R×3券種）：購入 17／予算で削除 0／予想で除外 42／未生成・券種なし 79／役割馬の行き先 {'PURCHASED': 138}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、46R×3券種）：購入 63／予算で削除 17／予想で除外 38／未生成・券種なし 20／役割馬の行き先 {'PURCHASED': 338, 'BUDGET_COMPRESSED': 165}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 17R／W外 29R、2着が P2 役割 2R）：STATIC 2/17（平均4.0位）／STYLE_COND 4/17（平均3.76位） 救済2・喪失0／MARKET_COND 4/16（平均3.0位） 救済3・喪失1
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 33R／W外 13R、2着が P2 役割 27R）：STATIC 28/33（平均3.88位）／STYLE_COND 28/33（平均3.73位） 救済0・喪失0／MARKET_COND 30/32（平均2.88位） 救済3・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 156 | 774,300 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 137 | 498,150 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 71 | 384,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 388 | 1,576,450 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

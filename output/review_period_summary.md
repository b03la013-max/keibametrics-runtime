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

- 反省済みRace 135／PAPER PFS 64.9%／正式推薦 PFS 41.4%
- 第一失敗：{'PREDICTION_ROLE_P2': 24, 'CAPITAL_EFFICIENCY': 47, 'PREDICTION_ROLE_W': 53, 'NONE': 11}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 15 | 24.2 | 74.0 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 5, 'NONE': 1} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 28 | 68.8 | 44.9 | {'PREDICTION_ROLE_W': 11, 'CAPITAL_EFFICIENCY': 7, 'NONE': 5, 'PREDICTION_ROLE_P2': 5} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 24 | 105.1 | 47.9 | {'PREDICTION_ROLE_W': 14, 'NONE': 1, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 7} |
| URW | 33 | 74.1 | 30.9 | {'CAPITAL_EFFICIENCY': 13, 'PREDICTION_ROLE_W': 12, 'NONE': 2, 'PREDICTION_ROLE_P2': 6} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 135 | 29.6% | 65.2% | 29.6% | 11.1% | 10.4% | 6.7% | 24.4% | 1.5 |
| 正式推薦 | 135 | 30.4% | 60.7% | 60.7% | 73.3% | 100.0% | 60.7% | 43.0% | 1.48 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中29.6%（無作為9.4%、差+20.2）／P2 平均1.0頭 的中11.1%（無作為9.4%、差+1.7）／P3 平均1.0頭 的中10.4%（無作為9.4%、差+0.9）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中60.7%（無作為28.3%、差+32.4）／P2 平均6.0頭 的中73.3%（無作為56.6%、差+16.7）／P3 平均10.84頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.81/40（選択性補正込み）・能力順位 13.81/20（135R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.99/40（選択性補正込み）・能力順位 13.35/20（135R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 7,200円（6.6%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）35R・着順まで的中 1R／的中 48R のうち的中赤字 23R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 51.5%（同じ135Rの実績 64.9%）／券種別 EXACTA 52点 PFS 13.8%／TRIFECTA 96点 PFS 6.1%／TRIO 697点 PFS 67.6%／WIDE 230点 PFS 93.3%／WIN 8点 PFS 43.8%／荒れ度（発走前・1番人気オッズ）MID 68R PFS 73.0% 的中赤字 11/24／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 59R PFS 52.4% 的中赤字 12/21／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 133R：実績 62.5% − ミラー 44.1% = Δ 18.4pt（95%区間 -7.4〜48.1、最高1R除き 10.8pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 309,700円（38.2%）／保護層の資金比率 0.0（135R）／組だけ的中（三連単は外れ）42R・着順まで的中 21R／的中 73R のうち的中赤字 60R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 47.4%（同じ135Rの実績 41.4%）／券種別 EXACTA 2025点 PFS 48.3%／TRIFECTA 3375点 PFS 22.3%／TRIO 2700点 PFS 60.0%／荒れ度（発走前・1番人気オッズ）MID 68R PFS 49.4% 的中赤字 26/34／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 59R PFS 35.3% 的中赤字 30/35／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 133R：実績 41.7% − ミラー 72.3% = Δ -30.6pt（95%区間 -61.4〜-1.3、最高1R除き -36.8pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、30R×3券種）：購入 12／予算で削除 0／予想で除外 26／未生成・券種なし 52／役割馬の行き先 {'PURCHASED': 90}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、30R×3券種）：購入 36／予算で削除 12／予想で除外 28／未生成・券種なし 14／役割馬の行き先 {'PURCHASED': 221, 'BUDGET_COMPRESSED': 109}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 11R／W外 19R、2着が P2 役割 0R）：STATIC 0/11（平均4.36位）／STYLE_COND 2/11（平均4.09位） 救済2・喪失0／MARKET_COND 2/10（平均3.6位） 救済2・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 21R／W外 9R、2着が P2 役割 16R）：STATIC 16/21（平均3.9位）／STYLE_COND 16/21（平均3.71位） 救済0・喪失0／MARKET_COND 18/20（平均2.9位） 救済3・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 60 | 215,690 | RECURRING |
| P1:ROLE_W_MISS | P1 | 53 | 277,890 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 24 | 144,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 135 | 587,690 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 372／PAPER PFS 61.9%／正式推薦 PFS 73.6%
- 第一失敗：{'NONE': 45, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 101, 'PREDICTION_ROLE_W': 128, 'PREDICTION_ROLE_P2': 61, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 39 | 73.8 | 60.3 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 12, 'PREDICTION_ROLE_W': 9, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 28 | 68.8 | 44.9 | {'PREDICTION_ROLE_W': 11, 'CAPITAL_EFFICIENCY': 7, 'NONE': 5, 'PREDICTION_ROLE_P2': 5} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 60 | 57.0 | 53.3 | {'PREDICTION_ROLE_W': 30, 'CAPITAL_EFFICIENCY': 17, 'PREDICTION_ROLE_P2': 8, 'NONE': 5} |
| URW | 33 | 74.1 | 30.9 | {'CAPITAL_EFFICIENCY': 13, 'PREDICTION_ROLE_W': 12, 'NONE': 2, 'PREDICTION_ROLE_P2': 6} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 372 | 32.3% | 67.7% | 32.3% | 14.5% | 12.6% | 9.4% | 23.9% | 1.54 |
| 正式推薦 | 334 | 32.0% | 61.7% | 61.7% | 72.5% | 100.0% | 61.7% | 35.3% | 1.43 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中32.6%（無作為9.6%、差+23.0）／P2 平均1.0頭 的中14.0%（無作為9.6%、差+4.5）／P3 平均1.0頭 的中12.1%（無作為9.6%、差+2.6）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.8%（無作為28.6%、差+35.2）／P2 平均6.0頭 的中72.4%（無作為57.2%、差+15.2）／P3 平均10.76頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.35/40（選択性補正込み）・能力順位 13.88/20（192R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.27/40（選択性補正込み）・能力順位 13.46/20（185R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 7,200円（6.6%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）35R・着順まで的中 1R／的中 48R のうち的中赤字 23R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 51.5%（同じ135Rの実績 64.9%）／券種別 EXACTA 52点 PFS 13.8%／TRIFECTA 96点 PFS 6.1%／TRIO 697点 PFS 67.6%／WIDE 230点 PFS 93.3%／WIN 8点 PFS 43.8%／荒れ度（発走前・1番人気オッズ）MID 68R PFS 73.0% 的中赤字 11/24／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 59R PFS 52.4% 的中赤字 12/21／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 133R：実績 62.5% − ミラー 44.1% = Δ 18.4pt（95%区間 -7.4〜48.1、最高1R除き 10.8pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 309,700円（38.2%）／保護層の資金比率 0.0（135R）／組だけ的中（三連単は外れ）42R・着順まで的中 21R／的中 73R のうち的中赤字 60R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 47.4%（同じ135Rの実績 41.4%）／券種別 EXACTA 2025点 PFS 48.3%／TRIFECTA 3375点 PFS 22.3%／TRIO 2700点 PFS 60.0%／荒れ度（発走前・1番人気オッズ）MID 68R PFS 49.4% 的中赤字 26/34／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 59R PFS 35.3% 的中赤字 30/35／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 133R：実績 41.7% − ミラー 72.3% = Δ -30.6pt（95%区間 -61.4〜-1.3、最高1R除き -36.8pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、30R×3券種）：購入 12／予算で削除 0／予想で除外 26／未生成・券種なし 52／役割馬の行き先 {'PURCHASED': 90}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、30R×3券種）：購入 36／予算で削除 12／予想で除外 28／未生成・券種なし 14／役割馬の行き先 {'PURCHASED': 221, 'BUDGET_COMPRESSED': 109}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 11R／W外 19R、2着が P2 役割 0R）：STATIC 0/11（平均4.36位）／STYLE_COND 2/11（平均4.09位） 救済2・喪失0／MARKET_COND 2/10（平均3.6位） 救済2・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 21R／W外 9R、2着が P2 役割 16R）：STATIC 16/21（平均3.9位）／STYLE_COND 16/21（平均3.71位） 救済0・喪失0／MARKET_COND 18/20（平均2.9位） 救済3・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 152 | 751,820 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 127 | 465,950 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 70 | 378,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 372 | 1,520,250 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

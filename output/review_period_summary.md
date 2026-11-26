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

- 反省済みRace 131／PAPER PFS 59.5%／正式推薦 PFS 40.2%
- 第一失敗：{'PREDICTION_ROLE_P2': 23, 'CAPITAL_EFFICIENCY': 46, 'PREDICTION_ROLE_W': 52, 'NONE': 10}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 14 | 25.7 | 75.1 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 5, 'NONE': 1} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 27 | 29.4 | 38.1 | {'PREDICTION_ROLE_W': 11, 'CAPITAL_EFFICIENCY': 7, 'NONE': 4, 'PREDICTION_ROLE_P2': 5} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 23 | 108.6 | 48.3 | {'PREDICTION_ROLE_W': 13, 'NONE': 1, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 7} |
| URW | 32 | 79.0 | 31.9 | {'CAPITAL_EFFICIENCY': 13, 'PREDICTION_ROLE_W': 12, 'NONE': 2, 'PREDICTION_ROLE_P2': 5} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 131 | 29.8% | 64.9% | 29.8% | 11.5% | 10.7% | 6.1% | 24.4% | 1.5 |
| 正式推薦 | 131 | 29.8% | 60.3% | 60.3% | 73.3% | 100.0% | 60.3% | 42.0% | 1.47 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中29.8%（無作為9.4%、差+20.3）／P2 平均1.0頭 的中11.5%（無作為9.4%、差+2.0）／P3 平均1.0頭 的中10.7%（無作為9.4%、差+1.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中60.3%（無作為28.3%、差+32.0）／P2 平均6.0頭 的中73.3%（無作為56.6%、差+16.7）／P3 平均10.83頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.85/40（選択性補正込み）・能力順位 13.78/20（131R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.93/40（選択性補正込み）・能力順位 13.31/20（131R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 6,600円（6.3%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）34R・着順まで的中 1R／的中 47R のうち的中赤字 23R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 52.7%（同じ131Rの実績 59.5%）／券種別 EXACTA 49点 PFS 14.7%／TRIFECTA 88点 PFS 6.7%／TRIO 677点 PFS 58.6%／WIDE 224点 PFS 93.1%／WIN 8点 PFS 43.8%／荒れ度（発走前・1番人気オッズ）MID 65R PFS 59.5% 的中赤字 11/23／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 58R PFS 54.2% 的中赤字 12/21／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 129R：実績 56.9% − ミラー 45.4% = Δ 11.4pt（95%区間 -12.5〜37.4、最高1R除き 6.3pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 300,900円（38.3%）／保護層の資金比率 0.0（131R）／組だけ的中（三連単は外れ）40R・着順まで的中 20R／的中 70R のうち的中赤字 58R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 48.3%（同じ131Rの実績 40.2%）／券種別 EXACTA 1965点 PFS 46.4%／TRIFECTA 3275点 PFS 22.1%／TRIO 2620点 PFS 58.1%／荒れ度（発走前・1番人気オッズ）MID 65R PFS 46.6% 的中赤字 24/31／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 58R PFS 35.9% 的中赤字 30/35／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 129R：実績 40.5% − ミラー 71.4% = Δ -31.0pt（95%区間 -65.2〜-1.7、最高1R除き -37.4pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、26R×3券種）：購入 11／予算で削除 0／予想で除外 21／未生成・券種なし 46／役割馬の行き先 {'PURCHASED': 78}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、26R×3券種）：購入 31／予算で削除 10／予想で除外 24／未生成・券種なし 13／役割馬の行き先 {'PURCHASED': 190, 'BUDGET_COMPRESSED': 96}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 10R／W外 16R、2着が P2 役割 0R）：STATIC 0/10（平均4.1位）／STYLE_COND 2/10（平均3.8位） 救済2・喪失0／MARKET_COND 1/9（平均3.89位） 救済1・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 18R／W外 8R、2着が P2 役割 14R）：STATIC 14/18（平均3.89位）／STYLE_COND 14/18（平均3.67位） 救済0・喪失0／MARKET_COND 15/17（平均2.94位） 救済2・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 58 | 209,610 | RECURRING |
| P1:ROLE_W_MISS | P1 | 52 | 274,240 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 23 | 138,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 131 | 575,610 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 368／PAPER PFS 59.9%／正式推薦 PFS 73.5%
- 第一失敗：{'NONE': 44, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 100, 'PREDICTION_ROLE_W': 127, 'PREDICTION_ROLE_P2': 60, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 38 | 75.5 | 60.3 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 11, 'PREDICTION_ROLE_W': 9, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 27 | 29.4 | 38.1 | {'PREDICTION_ROLE_W': 11, 'CAPITAL_EFFICIENCY': 7, 'NONE': 4, 'PREDICTION_ROLE_P2': 5} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 59 | 57.7 | 53.5 | {'PREDICTION_ROLE_W': 29, 'CAPITAL_EFFICIENCY': 17, 'PREDICTION_ROLE_P2': 8, 'NONE': 5} |
| URW | 32 | 79.0 | 31.9 | {'CAPITAL_EFFICIENCY': 13, 'PREDICTION_ROLE_W': 12, 'NONE': 2, 'PREDICTION_ROLE_P2': 5} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 368 | 32.3% | 67.7% | 32.3% | 14.7% | 12.8% | 9.2% | 23.9% | 1.54 |
| 正式推薦 | 330 | 31.8% | 61.5% | 61.5% | 72.4% | 100.0% | 61.5% | 34.8% | 1.43 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中32.7%（無作為9.6%、差+23.1）／P2 平均1.0頭 的中14.2%（無作為9.6%、差+4.7）／P3 平均1.0頭 的中12.3%（無作為9.6%、差+2.7）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.6%（無作為28.6%、差+35.0）／P2 平均6.0頭 的中72.3%（無作為57.2%、差+15.1）／P3 平均10.75頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.39/40（選択性補正込み）・能力順位 13.86/20（188R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.23/40（選択性補正込み）・能力順位 13.43/20（181R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 6,600円（6.3%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）34R・着順まで的中 1R／的中 47R のうち的中赤字 23R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 52.7%（同じ131Rの実績 59.5%）／券種別 EXACTA 49点 PFS 14.7%／TRIFECTA 88点 PFS 6.7%／TRIO 677点 PFS 58.6%／WIDE 224点 PFS 93.1%／WIN 8点 PFS 43.8%／荒れ度（発走前・1番人気オッズ）MID 65R PFS 59.5% 的中赤字 11/23／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 58R PFS 54.2% 的中赤字 12/21／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 129R：実績 56.9% − ミラー 45.4% = Δ 11.4pt（95%区間 -12.5〜37.4、最高1R除き 6.3pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 300,900円（38.3%）／保護層の資金比率 0.0（131R）／組だけ的中（三連単は外れ）40R・着順まで的中 20R／的中 70R のうち的中赤字 58R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 48.3%（同じ131Rの実績 40.2%）／券種別 EXACTA 1965点 PFS 46.4%／TRIFECTA 3275点 PFS 22.1%／TRIO 2620点 PFS 58.1%／荒れ度（発走前・1番人気オッズ）MID 65R PFS 46.6% 的中赤字 24/31／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 58R PFS 35.9% 的中赤字 30/35／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 129R：実績 40.5% − ミラー 71.4% = Δ -31.0pt（95%区間 -65.2〜-1.7、最高1R除き -37.4pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、26R×3券種）：購入 11／予算で削除 0／予想で除外 21／未生成・券種なし 46／役割馬の行き先 {'PURCHASED': 78}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、26R×3券種）：購入 31／予算で削除 10／予想で除外 24／未生成・券種なし 13／役割馬の行き先 {'PURCHASED': 190, 'BUDGET_COMPRESSED': 96}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 10R／W外 16R、2着が P2 役割 0R）：STATIC 0/10（平均4.1位）／STYLE_COND 2/10（平均3.8位） 救済2・喪失0／MARKET_COND 1/9（平均3.89位） 救済1・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 18R／W外 8R、2着が P2 役割 14R）：STATIC 14/18（平均3.89位）／STYLE_COND 14/18（平均3.67位） 救済0・喪失0／MARKET_COND 15/17（平均2.94位） 救済2・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 151 | 748,170 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 125 | 459,870 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 69 | 372,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 368 | 1,508,170 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

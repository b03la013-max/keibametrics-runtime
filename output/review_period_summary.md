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

- 反省済みRace 124／PAPER PFS 56.4%／正式推薦 PFS 40.0%
- 第一失敗：{'PREDICTION_ROLE_P2': 22, 'CAPITAL_EFFICIENCY': 44, 'PREDICTION_ROLE_W': 49, 'NONE': 9}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 12 | 18.9 | 81.4 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 5, 'NONE': 1} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 26 | 30.5 | 32.7 | {'PREDICTION_ROLE_W': 11, 'CAPITAL_EFFICIENCY': 7, 'NONE': 3, 'PREDICTION_ROLE_P2': 5} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 21 | 99.9 | 50.4 | {'PREDICTION_ROLE_W': 11, 'NONE': 1, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 7} |
| URW | 30 | 77.8 | 34.0 | {'CAPITAL_EFFICIENCY': 13, 'PREDICTION_ROLE_W': 11, 'NONE': 2, 'PREDICTION_ROLE_P2': 4} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 124 | 29.8% | 64.5% | 29.8% | 10.5% | 10.5% | 5.6% | 22.6% | 1.48 |
| 正式推薦 | 124 | 29.8% | 60.5% | 60.5% | 73.4% | 100.0% | 60.5% | 41.1% | 1.47 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中29.8%（無作為9.4%、差+20.4）／P2 平均1.0頭 的中10.5%（無作為9.4%、差+1.1）／P3 平均1.0頭 的中10.5%（無作為9.4%、差+1.1）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中60.5%（無作為28.3%、差+32.2）／P2 平均6.0頭 的中73.4%（無作為56.5%、差+16.9）／P3 平均10.85頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.76/40（選択性補正込み）・能力順位 13.69/20（124R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.95/40（選択性補正込み）・能力順位 13.3/20（124R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 6,000円（6.1%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）30R・着順まで的中 1R／的中 42R のうち的中赤字 20R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 54.2%（同じ124Rの実績 56.4%）／券種別 EXACTA 46点 PFS 5.9%／TRIFECTA 80点 PFS 7.4%／TRIO 638点 PFS 53.7%／WIDE 212点 PFS 94.6%／WIN 8点 PFS 43.8%／荒れ度（発走前・1番人気オッズ）MID 61R PFS 51.1% 的中赤字 10/20／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 55R PFS 55.6% 的中赤字 10/19／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 122R：実績 53.6% − ミラー 43.1% = Δ 10.4pt（95%区間 -12.1〜36.6、最高1R除き 5.0pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 284,700円（38.3%）／保護層の資金比率 0.0（124R）／組だけ的中（三連単は外れ）37R・着順まで的中 19R／的中 66R のうち的中赤字 55R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 49.5%（同じ124Rの実績 40.0%）／券種別 EXACTA 1860点 PFS 47.3%／TRIFECTA 3100点 PFS 22.7%／TRIO 2480点 PFS 56.1%／荒れ度（発走前・1番人気オッズ）MID 61R PFS 45.0% 的中赤字 22/28／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 55R PFS 37.5% 的中赤字 29/34／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 122R：実績 40.3% − ミラー 73.3% = Δ -33.0pt（95%区間 -66.1〜-1.4、最高1R除き -39.8pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、19R×3券種）：購入 6／予算で削除 0／予想で除外 17／未生成・券種なし 34／役割馬の行き先 {'PURCHASED': 57}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、19R×3券種）：購入 23／予算で削除 8／予想で除外 16／未生成・券種なし 10／役割馬の行き先 {'PURCHASED': 139, 'BUDGET_COMPRESSED': 73}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 8R／W外 11R、2着が P2 役割 0R）：STATIC 0/8（平均4.5位）／STYLE_COND 1/8（平均4.25位） 救済1・喪失0／MARKET_COND 0/7（平均4.14位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 14R／W外 5R、2着が P2 役割 11R）：STATIC 11/14（平均3.71位）／STYLE_COND 11/14（平均3.57位） 救済0・喪失0／MARKET_COND 11/13（平均2.92位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 55 | 199,180 | RECURRING |
| P1:ROLE_W_MISS | P1 | 49 | 259,380 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 22 | 132,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 124 | 547,180 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 361／PAPER PFS 58.9%／正式推薦 PFS 74.2%
- 第一失敗：{'NONE': 43, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 98, 'PREDICTION_ROLE_W': 124, 'PREDICTION_ROLE_P2': 59, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 36 | 75.7 | 62.2 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 9, 'PREDICTION_ROLE_W': 9, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 26 | 30.5 | 32.7 | {'PREDICTION_ROLE_W': 11, 'CAPITAL_EFFICIENCY': 7, 'NONE': 3, 'PREDICTION_ROLE_P2': 5} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 57 | 52.8 | 54.5 | {'PREDICTION_ROLE_W': 27, 'CAPITAL_EFFICIENCY': 17, 'PREDICTION_ROLE_P2': 8, 'NONE': 5} |
| URW | 30 | 77.8 | 34.0 | {'CAPITAL_EFFICIENCY': 13, 'PREDICTION_ROLE_W': 11, 'NONE': 2, 'PREDICTION_ROLE_P2': 4} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 361 | 32.4% | 67.6% | 32.4% | 14.4% | 12.7% | 9.1% | 23.3% | 1.53 |
| 正式推薦 | 323 | 31.9% | 61.6% | 61.6% | 72.4% | 100.0% | 61.6% | 34.4% | 1.43 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中32.8%（無作為9.6%、差+23.2）／P2 平均1.0頭 的中13.8%（無作為9.6%、差+4.3）／P3 平均1.0頭 的中12.3%（無作為9.6%、差+2.7）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.8%（無作為28.6%、差+35.2）／P2 平均6.0頭 的中72.4%（無作為57.2%、差+15.2）／P3 平均10.76頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.35/40（選択性補正込み）・能力順位 13.8/20（181R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.26/40（選択性補正込み）・能力順位 13.43/20（174R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 6,000円（6.1%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）30R・着順まで的中 1R／的中 42R のうち的中赤字 20R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 54.2%（同じ124Rの実績 56.4%）／券種別 EXACTA 46点 PFS 5.9%／TRIFECTA 80点 PFS 7.4%／TRIO 638点 PFS 53.7%／WIDE 212点 PFS 94.6%／WIN 8点 PFS 43.8%／荒れ度（発走前・1番人気オッズ）MID 61R PFS 51.1% 的中赤字 10/20／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 55R PFS 55.6% 的中赤字 10/19／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 122R：実績 53.6% − ミラー 43.1% = Δ 10.4pt（95%区間 -12.1〜36.6、最高1R除き 5.0pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 284,700円（38.3%）／保護層の資金比率 0.0（124R）／組だけ的中（三連単は外れ）37R・着順まで的中 19R／的中 66R のうち的中赤字 55R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 49.5%（同じ124Rの実績 40.0%）／券種別 EXACTA 1860点 PFS 47.3%／TRIFECTA 3100点 PFS 22.7%／TRIO 2480点 PFS 56.1%／荒れ度（発走前・1番人気オッズ）MID 61R PFS 45.0% 的中赤字 22/28／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 55R PFS 37.5% 的中赤字 29/34／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 122R：実績 40.3% − ミラー 73.3% = Δ -33.0pt（95%区間 -66.1〜-1.4、最高1R除き -39.8pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、19R×3券種）：購入 6／予算で削除 0／予想で除外 17／未生成・券種なし 34／役割馬の行き先 {'PURCHASED': 57}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、19R×3券種）：購入 23／予算で削除 8／予想で除外 16／未生成・券種なし 10／役割馬の行き先 {'PURCHASED': 139, 'BUDGET_COMPRESSED': 73}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 8R／W外 11R、2着が P2 役割 0R）：STATIC 0/8（平均4.5位）／STYLE_COND 1/8（平均4.25位） 救済1・喪失0／MARKET_COND 0/7（平均4.14位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 14R／W外 5R、2着が P2 役割 11R）：STATIC 11/14（平均3.71位）／STYLE_COND 11/14（平均3.57位） 救済0・喪失0／MARKET_COND 11/13（平均2.92位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 148 | 733,310 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 122 | 449,440 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 68 | 366,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 361 | 1,479,740 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

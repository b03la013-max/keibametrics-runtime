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

- 反省済みRace 129／PAPER PFS 60.4%／正式推薦 PFS 40.8%
- 第一失敗：{'PREDICTION_ROLE_P2': 22, 'CAPITAL_EFFICIENCY': 46, 'PREDICTION_ROLE_W': 51, 'NONE': 10}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 14 | 25.7 | 75.1 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 5, 'NONE': 1} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 27 | 29.4 | 38.1 | {'PREDICTION_ROLE_W': 11, 'CAPITAL_EFFICIENCY': 7, 'NONE': 4, 'PREDICTION_ROLE_P2': 5} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 22 | 112.3 | 50.5 | {'PREDICTION_ROLE_W': 12, 'NONE': 1, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 7} |
| URW | 31 | 82.5 | 32.9 | {'CAPITAL_EFFICIENCY': 13, 'PREDICTION_ROLE_W': 12, 'NONE': 2, 'PREDICTION_ROLE_P2': 4} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 129 | 29.5% | 64.3% | 29.5% | 11.6% | 10.9% | 5.4% | 24.8% | 1.5 |
| 正式推薦 | 129 | 29.5% | 60.5% | 60.5% | 74.4% | 100.0% | 60.5% | 42.6% | 1.49 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中29.5%（無作為9.4%、差+20.0）／P2 平均1.0頭 的中11.6%（無作為9.4%、差+2.2）／P3 平均1.0頭 的中10.9%（無作為9.4%、差+1.4）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中60.5%（無作為28.3%、差+32.1）／P2 平均6.0頭 的中74.4%（無作為56.7%、差+17.8）／P3 平均10.82頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.86/40（選択性補正込み）・能力順位 13.78/20（129R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.01/40（選択性補正込み）・能力順位 13.35/20（129R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 6,000円（5.9%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）34R・着順まで的中 1R／的中 46R のうち的中赤字 22R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 53.1%（同じ129Rの実績 60.4%）／券種別 EXACTA 46点 PFS 5.9%／TRIFECTA 80点 PFS 7.4%／TRIO 667点 PFS 59.5%／WIDE 222点 PFS 94.0%／WIN 8点 PFS 43.8%／荒れ度（発走前・1番人気オッズ）MID 65R PFS 59.5% 的中赤字 11/23／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 56R PFS 55.9% 的中赤字 11/20／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 127R：実績 57.7% − ミラー 42.7% = Δ 15.0pt（95%区間 -8.7〜40.7、最高1R除き 9.8pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 296,400円（38.3%）／保護層の資金比率 0.0（129R）／組だけ的中（三連単は外れ）40R・着順まで的中 20R／的中 70R のうち的中赤字 58R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 48.7%（同じ129Rの実績 40.8%）／券種別 EXACTA 1935点 PFS 47.1%／TRIFECTA 3225点 PFS 22.4%／TRIO 2580点 PFS 59.0%／荒れ度（発走前・1番人気オッズ）MID 65R PFS 46.6% 的中赤字 24/31／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 56R PFS 37.2% 的中赤字 30/35／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 127R：実績 41.1% − ミラー 72.0% = Δ -30.9pt（95%区間 -64.5〜-0.7、最高1R除き -37.4pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、24R×3券種）：購入 10／予算で削除 0／予想で除外 18／未生成・券種なし 44／役割馬の行き先 {'PURCHASED': 72}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、24R×3券種）：購入 31／予算で削除 10／予想で除外 20／未生成・券種なし 11／役割馬の行き先 {'PURCHASED': 175, 'BUDGET_COMPRESSED': 88}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 9R／W外 15R、2着が P2 役割 0R）：STATIC 0/9（平均4.33位）／STYLE_COND 1/9（平均4.11位） 救済1・喪失0／MARKET_COND 0/8（平均4.25位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 17R／W外 7R、2着が P2 役割 14R）：STATIC 14/17（平均3.71位）／STYLE_COND 14/17（平均3.47位） 救済0・喪失0／MARKET_COND 14/16（平均3.06位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 58 | 209,610 | RECURRING |
| P1:ROLE_W_MISS | P1 | 51 | 268,240 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 22 | 132,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 129 | 563,610 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 366／PAPER PFS 60.2%／正式推薦 PFS 74.0%
- 第一失敗：{'NONE': 44, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 100, 'PREDICTION_ROLE_W': 126, 'PREDICTION_ROLE_P2': 59, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 38 | 75.5 | 60.3 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 11, 'PREDICTION_ROLE_W': 9, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 27 | 29.4 | 38.1 | {'PREDICTION_ROLE_W': 11, 'CAPITAL_EFFICIENCY': 7, 'NONE': 4, 'PREDICTION_ROLE_P2': 5} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 58 | 58.5 | 54.4 | {'PREDICTION_ROLE_W': 28, 'CAPITAL_EFFICIENCY': 17, 'PREDICTION_ROLE_P2': 8, 'NONE': 5} |
| URW | 31 | 82.5 | 32.9 | {'CAPITAL_EFFICIENCY': 13, 'PREDICTION_ROLE_W': 12, 'NONE': 2, 'PREDICTION_ROLE_P2': 4} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 366 | 32.2% | 67.5% | 32.2% | 14.8% | 12.8% | 9.0% | 24.0% | 1.54 |
| 正式推薦 | 328 | 31.7% | 61.6% | 61.6% | 72.9% | 100.0% | 61.6% | 35.1% | 1.44 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中32.6%（無作為9.6%、差+23.0）／P2 平均1.0頭 的中14.3%（無作為9.6%、差+4.8）／P3 平均1.0頭 的中12.4%（無作為9.6%、差+2.8）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.7%（無作為28.6%、差+35.1）／P2 平均6.0頭 的中72.9%（無作為57.2%、差+15.7）／P3 平均10.75頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.4/40（選択性補正込み）・能力順位 13.86/20（186R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.29/40（選択性補正込み）・能力順位 13.46/20（179R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 6,000円（5.9%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）34R・着順まで的中 1R／的中 46R のうち的中赤字 22R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 53.1%（同じ129Rの実績 60.4%）／券種別 EXACTA 46点 PFS 5.9%／TRIFECTA 80点 PFS 7.4%／TRIO 667点 PFS 59.5%／WIDE 222点 PFS 94.0%／WIN 8点 PFS 43.8%／荒れ度（発走前・1番人気オッズ）MID 65R PFS 59.5% 的中赤字 11/23／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 56R PFS 55.9% 的中赤字 11/20／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 127R：実績 57.7% − ミラー 42.7% = Δ 15.0pt（95%区間 -8.7〜40.7、最高1R除き 9.8pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 296,400円（38.3%）／保護層の資金比率 0.0（129R）／組だけ的中（三連単は外れ）40R・着順まで的中 20R／的中 70R のうち的中赤字 58R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 48.7%（同じ129Rの実績 40.8%）／券種別 EXACTA 1935点 PFS 47.1%／TRIFECTA 3225点 PFS 22.4%／TRIO 2580点 PFS 59.0%／荒れ度（発走前・1番人気オッズ）MID 65R PFS 46.6% 的中赤字 24/31／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 56R PFS 37.2% 的中赤字 30/35／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 127R：実績 41.1% − ミラー 72.0% = Δ -30.9pt（95%区間 -64.5〜-0.7、最高1R除き -37.4pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、24R×3券種）：購入 10／予算で削除 0／予想で除外 18／未生成・券種なし 44／役割馬の行き先 {'PURCHASED': 72}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、24R×3券種）：購入 31／予算で削除 10／予想で除外 20／未生成・券種なし 11／役割馬の行き先 {'PURCHASED': 175, 'BUDGET_COMPRESSED': 88}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 9R／W外 15R、2着が P2 役割 0R）：STATIC 0/9（平均4.33位）／STYLE_COND 1/9（平均4.11位） 救済1・喪失0／MARKET_COND 0/8（平均4.25位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 17R／W外 7R、2着が P2 役割 14R）：STATIC 14/17（平均3.71位）／STYLE_COND 14/17（平均3.47位） 救済0・喪失0／MARKET_COND 14/16（平均3.06位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 150 | 742,170 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 125 | 459,870 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 68 | 366,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 366 | 1,496,170 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

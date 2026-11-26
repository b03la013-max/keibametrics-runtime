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

- 反省済みRace 128／PAPER PFS 60.3%／正式推薦 PFS 40.7%
- 第一失敗：{'PREDICTION_ROLE_P2': 22, 'CAPITAL_EFFICIENCY': 45, 'PREDICTION_ROLE_W': 51, 'NONE': 10}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 13 | 22.5 | 76.6 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 5, 'NONE': 1} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 27 | 29.4 | 38.1 | {'PREDICTION_ROLE_W': 11, 'CAPITAL_EFFICIENCY': 7, 'NONE': 4, 'PREDICTION_ROLE_P2': 5} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 22 | 112.3 | 50.5 | {'PREDICTION_ROLE_W': 12, 'NONE': 1, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 7} |
| URW | 31 | 82.5 | 32.9 | {'CAPITAL_EFFICIENCY': 13, 'PREDICTION_ROLE_W': 12, 'NONE': 2, 'PREDICTION_ROLE_P2': 4} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 128 | 29.7% | 64.1% | 29.7% | 11.7% | 10.9% | 5.5% | 24.2% | 1.48 |
| 正式推薦 | 128 | 29.7% | 60.2% | 60.2% | 74.2% | 100.0% | 60.2% | 42.2% | 1.48 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中29.7%（無作為9.4%、差+20.3）／P2 平均1.0頭 的中11.7%（無作為9.4%、差+2.3）／P3 平均1.0頭 的中10.9%（無作為9.4%、差+1.5）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中60.2%（無作為28.3%、差+31.9）／P2 平均6.0頭 的中74.2%（無作為56.6%、差+17.6）／P3 平均10.84頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.84/40（選択性補正込み）・能力順位 13.75/20（128R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.98/40（選択性補正込み）・能力順位 13.34/20（128R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 6,000円（5.9%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）33R・着順まで的中 1R／的中 45R のうち的中赤字 21R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 53.4%（同じ128Rの実績 60.3%）／券種別 EXACTA 46点 PFS 5.9%／TRIFECTA 80点 PFS 7.4%／TRIO 662点 PFS 59.4%／WIDE 220点 PFS 94.0%／WIN 8点 PFS 43.8%／荒れ度（発走前・1番人気オッズ）MID 64R PFS 59.4% 的中赤字 10/22／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 56R PFS 55.9% 的中赤字 11/20／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 126R：実績 57.6% − ミラー 42.5% = Δ 15.1pt（95%区間 -9.2〜40.9、最高1R除き 9.9pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 294,000円（38.3%）／保護層の資金比率 0.0（128R）／組だけ的中（三連単は外れ）40R・着順まで的中 19R／的中 69R のうち的中赤字 57R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 49.1%（同じ128Rの実績 40.7%）／券種別 EXACTA 1920点 PFS 47.0%／TRIFECTA 3200点 PFS 22.0%／TRIO 2560点 PFS 59.3%／荒れ度（発走前・1番人気オッズ）MID 64R PFS 46.5% 的中赤字 23/30／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 56R PFS 37.2% 的中赤字 30/35／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 126R：実績 41.0% − ミラー 72.1% = Δ -31.1pt（95%区間 -65.1〜-0.2、最高1R除き -37.7pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、23R×3券種）：購入 9／予算で削除 0／予想で除外 18／未生成・券種なし 42／役割馬の行き先 {'PURCHASED': 69}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、23R×3券種）：購入 28／予算で削除 10／予想で除外 20／未生成・券種なし 11／役割馬の行き先 {'PURCHASED': 168, 'BUDGET_COMPRESSED': 86}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 9R／W外 14R、2着が P2 役割 0R）：STATIC 0/9（平均4.33位）／STYLE_COND 1/9（平均4.11位） 救済1・喪失0／MARKET_COND 0/8（平均4.25位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 16R／W外 7R、2着が P2 役割 13R）：STATIC 13/16（平均3.62位）／STYLE_COND 13/16（平均3.44位） 救済0・喪失0／MARKET_COND 13/15（平均3.13位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 57 | 206,940 | RECURRING |
| P1:ROLE_W_MISS | P1 | 51 | 268,240 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 22 | 132,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 128 | 560,940 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 365／PAPER PFS 60.2%／正式推薦 PFS 74.0%
- 第一失敗：{'NONE': 44, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 99, 'PREDICTION_ROLE_W': 126, 'PREDICTION_ROLE_P2': 59, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 37 | 75.6 | 60.5 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_W': 9, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
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
| PAPER | 365 | 32.3% | 67.4% | 32.3% | 14.8% | 12.9% | 9.0% | 23.8% | 1.53 |
| 正式推薦 | 327 | 31.8% | 61.5% | 61.5% | 72.8% | 100.0% | 61.5% | 34.9% | 1.43 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中32.7%（無作為9.6%、差+23.1）／P2 平均1.0頭 的中14.4%（無作為9.6%、差+4.8）／P3 平均1.0頭 的中12.5%（無作為9.6%、差+2.9）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.6%（無作為28.6%、差+35.0）／P2 平均6.0頭 的中72.8%（無作為57.2%、差+15.6）／P3 平均10.76頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.39/40（選択性補正込み）・能力順位 13.84/20（185R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.27/40（選択性補正込み）・能力順位 13.45/20（178R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 6,000円（5.9%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）33R・着順まで的中 1R／的中 45R のうち的中赤字 21R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 53.4%（同じ128Rの実績 60.3%）／券種別 EXACTA 46点 PFS 5.9%／TRIFECTA 80点 PFS 7.4%／TRIO 662点 PFS 59.4%／WIDE 220点 PFS 94.0%／WIN 8点 PFS 43.8%／荒れ度（発走前・1番人気オッズ）MID 64R PFS 59.4% 的中赤字 10/22／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 56R PFS 55.9% 的中赤字 11/20／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 126R：実績 57.6% − ミラー 42.5% = Δ 15.1pt（95%区間 -9.2〜40.9、最高1R除き 9.9pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 294,000円（38.3%）／保護層の資金比率 0.0（128R）／組だけ的中（三連単は外れ）40R・着順まで的中 19R／的中 69R のうち的中赤字 57R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 49.1%（同じ128Rの実績 40.7%）／券種別 EXACTA 1920点 PFS 47.0%／TRIFECTA 3200点 PFS 22.0%／TRIO 2560点 PFS 59.3%／荒れ度（発走前・1番人気オッズ）MID 64R PFS 46.5% 的中赤字 23/30／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 56R PFS 37.2% 的中赤字 30/35／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 126R：実績 41.0% − ミラー 72.1% = Δ -31.1pt（95%区間 -65.1〜-0.2、最高1R除き -37.7pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、23R×3券種）：購入 9／予算で削除 0／予想で除外 18／未生成・券種なし 42／役割馬の行き先 {'PURCHASED': 69}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、23R×3券種）：購入 28／予算で削除 10／予想で除外 20／未生成・券種なし 11／役割馬の行き先 {'PURCHASED': 168, 'BUDGET_COMPRESSED': 86}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 9R／W外 14R、2着が P2 役割 0R）：STATIC 0/9（平均4.33位）／STYLE_COND 1/9（平均4.11位） 救済1・喪失0／MARKET_COND 0/8（平均4.25位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 16R／W外 7R、2着が P2 役割 13R）：STATIC 13/16（平均3.62位）／STYLE_COND 13/16（平均3.44位） 救済0・喪失0／MARKET_COND 13/15（平均3.13位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 150 | 742,170 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 124 | 457,200 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 68 | 366,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 365 | 1,493,500 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

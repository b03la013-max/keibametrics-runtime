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

- 反省済みRace 206／PAPER PFS 60.1%／正式推薦 PFS 45.8%
- 第一失敗：{'PREDICTION_ROLE_P2': 36, 'CAPITAL_EFFICIENCY': 72, 'PREDICTION_ROLE_W': 80, 'NONE': 18}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 22 | 51.6 | 73.2 | {'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 12, 'PREDICTION_ROLE_W': 5, 'NONE': 2} |
| KOC | 8 | 31.2 | 171.2 | {'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 1, 'NONE': 3, 'PREDICTION_ROLE_W': 1} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 48 | 51.9 | 46.3 | {'PREDICTION_ROLE_W': 20, 'CAPITAL_EFFICIENCY': 14, 'NONE': 6, 'PREDICTION_ROLE_P2': 8} |
| SAG | 20 | 23.5 | 14.8 | {'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_P2': 5} |
| SON | 36 | 102.8 | 37.8 | {'PREDICTION_ROLE_W': 18, 'NONE': 1, 'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 14} |
| URW | 48 | 65.7 | 35.5 | {'CAPITAL_EFFICIENCY': 16, 'PREDICTION_ROLE_W': 20, 'NONE': 4, 'PREDICTION_ROLE_P2': 8} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 206 | 32.5% | 65.5% | 32.5% | 13.1% | 14.6% | 6.8% | 23.8% | 1.54 |
| 正式推薦 | 206 | 32.5% | 61.2% | 61.2% | 74.8% | 100.0% | 67.5% | 40.8% | 1.49 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中32.5%（無作為9.4%、差+23.1）／P2 平均1.0頭 的中13.1%（無作為9.4%、差+3.7）／P3 平均1.0頭 的中14.6%（無作為9.4%、差+5.1）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中61.2%（無作為28.2%、差+32.9）／P2 平均6.0頭 的中74.8%（無作為56.5%、差+18.3）／P3 平均10.86頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.7/40（選択性補正込み）・能力順位 14.06/20（206R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.29/40（選択性補正込み）・能力順位 13.62/20（206R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 9,600円（5.9%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）50R・着順まで的中 2R／的中 76R のうち的中赤字 39R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 50.8%（同じ206Rの実績 60.1%）／券種別 EXACTA 74点 PFS 33.5%／TRIFECTA 128点 PFS 12.5%／TRIO 1062点 PFS 54.0%／WIDE 354点 PFS 102.1%／WIN 13点 PFS 39.2%／荒れ度（発走前・1番人気オッズ）MID 105R PFS 70.7% 的中赤字 14/37／OPEN 8R PFS 64.7% 的中赤字 0/3／SOLID 90R PFS 45.2% 的中赤字 24/34／UNKNOWN 3R PFS 152.7% 的中赤字 1/2／市場ミラーとの差 203R：実績 58.4% − ミラー 53.5% = Δ 4.9pt（95%区間 -18.7〜28.5、最高1R除き -0.2pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 351,200円（28.4%）／保護層の資金比率 0.0（206R）／組だけ的中（三連単は外れ）59R・着順まで的中 43R／的中 114R のうち的中赤字 93R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 46.9%（同じ206Rの実績 45.8%）／券種別 EXACTA 3222点 PFS 49.8%／TRIFECTA 6078点 PFS 37.6%／TRIO 3060点 PFS 57.8%／荒れ度（発走前・1番人気オッズ）MID 105R PFS 55.4% 的中赤字 44/56／OPEN 8R PFS 39.4% 的中赤字 2/3／SOLID 90R PFS 35.9% 的中赤字 44/52／UNKNOWN 3R PFS 21.7% 的中赤字 3/3／市場ミラーとの差 203R：実績 46.1% − ミラー 67.3% = Δ -21.2pt（95%区間 -45.7〜1.5、最高1R除き -25.2pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、101R×3券種）：購入 30／予算で削除 0／予想で除外 92／未生成・券種なし 181／役割馬の行き先 {'PURCHASED': 303}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、101R×3券種）：購入 106／予算で削除 32／予想で除外 95／未生成・券種なし 70／役割馬の行き先 {'PURCHASED': 758, 'BUDGET_COMPRESSED': 346}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 38R／W外 63R、2着が P2 役割 6R）：STATIC 6/38（平均3.74位）／STYLE_COND 9/38（平均3.61位） 救済3・喪失0／MARKET_COND 8/36（平均2.97位） 救済6・喪失3
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 65R／W外 36R、2着が P2 役割 48R）：STATIC 51/65（平均4.14位）／STYLE_COND 52/65（平均4.03位） 救済1・喪失0／MARKET_COND 59/63（平均2.95位） 救済11・喪失1

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 93 | 341,650 | RECURRING |
| P1:ROLE_W_MISS | P1 | 80 | 418,200 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 36 | 216,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 206 | 893,650 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 443／PAPER PFS 60.1%／正式推薦 PFS 70.3%
- 第一失敗：{'NONE': 52, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 126, 'PREDICTION_ROLE_W': 155, 'PREDICTION_ROLE_P2': 73, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 46 | 78.5 | 62.5 | {'NONE': 6, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 17, 'PREDICTION_ROLE_W': 9, 'PREDICTION_ROLE_P2': 5, 'EXACT_ORIENTATION': 1} |
| KOC | 31 | 52.1 | 73.6 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 5, 'NONE': 5, 'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 9} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 48 | 51.9 | 46.3 | {'PREDICTION_ROLE_W': 20, 'CAPITAL_EFFICIENCY': 14, 'NONE': 6, 'PREDICTION_ROLE_P2': 8} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 42 | 43.8 | 25.6 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 11, 'PREDICTION_ROLE_W': 13, 'CAPITAL_EFFICIENCY': 13, 'NONE': 2} |
| SON | 72 | 62.3 | 47.3 | {'PREDICTION_ROLE_W': 34, 'CAPITAL_EFFICIENCY': 24, 'PREDICTION_ROLE_P2': 9, 'NONE': 5} |
| URW | 48 | 65.7 | 35.5 | {'CAPITAL_EFFICIENCY': 16, 'PREDICTION_ROLE_W': 20, 'NONE': 4, 'PREDICTION_ROLE_P2': 8} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 443 | 33.2% | 67.5% | 33.2% | 14.9% | 14.2% | 9.0% | 23.7% | 1.55 |
| 正式推薦 | 405 | 32.8% | 61.7% | 61.7% | 73.3% | 100.0% | 64.9% | 35.6% | 1.45 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中33.7%（無作為9.5%、差+24.2）／P2 平均1.0頭 的中14.6%（無作為9.5%、差+5.1）／P3 平均1.0頭 的中14.3%（無作為9.5%、差+4.8）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.4%（無作為28.5%、差+34.9）／P2 平均6.0頭 的中73.5%（無作為57.0%、差+16.5）／P3 平均10.79頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.9/40（選択性補正込み）・能力順位 14.05/20（263R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.43/40（選択性補正込み）・能力順位 13.64/20（256R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 9,600円（5.9%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）50R・着順まで的中 2R／的中 76R のうち的中赤字 39R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 50.8%（同じ206Rの実績 60.1%）／券種別 EXACTA 74点 PFS 33.5%／TRIFECTA 128点 PFS 12.5%／TRIO 1062点 PFS 54.0%／WIDE 354点 PFS 102.1%／WIN 13点 PFS 39.2%／荒れ度（発走前・1番人気オッズ）MID 105R PFS 70.7% 的中赤字 14/37／OPEN 8R PFS 64.7% 的中赤字 0/3／SOLID 90R PFS 45.2% 的中赤字 24/34／UNKNOWN 3R PFS 152.7% 的中赤字 1/2／市場ミラーとの差 203R：実績 58.4% − ミラー 53.5% = Δ 4.9pt（95%区間 -18.7〜28.5、最高1R除き -0.2pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 351,200円（28.4%）／保護層の資金比率 0.0（206R）／組だけ的中（三連単は外れ）59R・着順まで的中 43R／的中 114R のうち的中赤字 93R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 46.9%（同じ206Rの実績 45.8%）／券種別 EXACTA 3222点 PFS 49.8%／TRIFECTA 6078点 PFS 37.6%／TRIO 3060点 PFS 57.8%／荒れ度（発走前・1番人気オッズ）MID 105R PFS 55.4% 的中赤字 44/56／OPEN 8R PFS 39.4% 的中赤字 2/3／SOLID 90R PFS 35.9% 的中赤字 44/52／UNKNOWN 3R PFS 21.7% 的中赤字 3/3／市場ミラーとの差 203R：実績 46.1% − ミラー 67.3% = Δ -21.2pt（95%区間 -45.7〜1.5、最高1R除き -25.2pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、101R×3券種）：購入 30／予算で削除 0／予想で除外 92／未生成・券種なし 181／役割馬の行き先 {'PURCHASED': 303}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、101R×3券種）：購入 106／予算で削除 32／予想で除外 95／未生成・券種なし 70／役割馬の行き先 {'PURCHASED': 758, 'BUDGET_COMPRESSED': 346}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 38R／W外 63R、2着が P2 役割 6R）：STATIC 6/38（平均3.74位）／STYLE_COND 9/38（平均3.61位） 救済3・喪失0／MARKET_COND 8/36（平均2.97位） 救済6・喪失3
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 65R／W外 36R、2着が P2 役割 48R）：STATIC 51/65（平均4.14位）／STYLE_COND 52/65（平均4.03位） 救済1・喪失0／MARKET_COND 59/63（平均2.95位） 救済11・喪失1

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 179 | 892,130 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 160 | 591,910 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 82 | 450,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 443 | 1,826,210 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

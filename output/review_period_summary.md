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

- 反省済みRace 167／PAPER PFS 63.5%／正式推薦 PFS 42.0%
- 第一失敗：{'PREDICTION_ROLE_P2': 26, 'CAPITAL_EFFICIENCY': 62, 'PREDICTION_ROLE_W': 66, 'NONE': 13}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 22 | 51.6 | 73.2 | {'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 12, 'PREDICTION_ROLE_W': 5, 'NONE': 2} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 37 | 64.0 | 52.7 | {'PREDICTION_ROLE_W': 15, 'CAPITAL_EFFICIENCY': 10, 'NONE': 6, 'PREDICTION_ROLE_P2': 6} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 32 | 98.6 | 40.9 | {'PREDICTION_ROLE_W': 16, 'NONE': 1, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 13} |
| URW | 41 | 61.0 | 26.9 | {'CAPITAL_EFFICIENCY': 14, 'PREDICTION_ROLE_W': 19, 'NONE': 2, 'PREDICTION_ROLE_P2': 6} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 167 | 30.5% | 63.5% | 30.5% | 15.0% | 13.8% | 7.2% | 25.1% | 1.51 |
| 正式推薦 | 167 | 31.1% | 60.5% | 60.5% | 76.6% | 100.0% | 63.5% | 43.1% | 1.48 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中30.5%（無作為9.5%、差+21.1）／P2 平均1.0頭 的中15.0%（無作為9.5%、差+5.5）／P3 平均1.0頭 的中13.8%（無作為9.5%、差+4.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中60.5%（無作為28.4%、差+32.1）／P2 平均6.0頭 的中76.6%（無作為56.8%、差+19.8）／P3 平均10.81頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.51/40（選択性補正込み）・能力順位 13.9/20（167R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.2/40（選択性補正込み）・能力順位 13.5/20（167R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 8,400円（6.3%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）43R・着順まで的中 2R／的中 60R のうち的中赤字 30R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 53.8%（同じ167Rの実績 63.5%）／券種別 EXACTA 60点 PFS 19.5%／TRIFECTA 112点 PFS 14.3%／TRIO 857点 PFS 61.4%／WIDE 288点 PFS 98.0%／WIN 9点 PFS 56.7%／荒れ度（発走前・1番人気オッズ）MID 86R PFS 72.2% 的中赤字 13/30／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 72R PFS 50.6% 的中赤字 16/26／UNKNOWN 3R PFS 152.7% 的中赤字 1/2／市場ミラーとの差 164R：実績 61.4% − ミラー 43.9% = Δ 17.5pt（95%区間 -4.7〜42.7、最高1R除き 11.3pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 351,200円（35.0%）／保護層の資金比率 0.0（167R）／組だけ的中（三連単は外れ）52R・着順まで的中 31R／的中 94R のうち的中赤字 78R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 49.0%（同じ167Rの実績 42.0%）／券種別 EXACTA 2541点 PFS 48.5%／TRIFECTA 4419点 PFS 27.4%／TRIO 3060点 PFS 57.8%／荒れ度（発走前・1番人気オッズ）MID 86R PFS 45.6% 的中赤字 39/47／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 72R PFS 40.7% 的中赤字 34/42／UNKNOWN 3R PFS 21.7% 的中赤字 3/3／市場ミラーとの差 164R：実績 42.4% − ミラー 70.1% = Δ -27.7pt（95%区間 -55.5〜-0.7、最高1R除き -32.7pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、62R×3券種）：購入 22／予算で削除 0／予想で除外 53／未生成・券種なし 111／役割馬の行き先 {'PURCHASED': 186}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、62R×3券種）：購入 75／予算で削除 22／予想で除外 54／未生成・券種なし 35／役割馬の行き先 {'PURCHASED': 456, 'BUDGET_COMPRESSED': 216}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 22R／W外 40R、2着が P2 役割 5R）：STATIC 5/22（平均3.64位）／STYLE_COND 7/22（平均3.45位） 救済2・喪失0／MARKET_COND 5/20（平均3.0位） 救済3・喪失2
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 40R／W外 22R、2着が P2 役割 33R）：STATIC 34/40（平均3.77位）／STYLE_COND 34/40（平均3.6位） 救済0・喪失0／MARKET_COND 36/38（平均2.82位） 救済4・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 78 | 284,490 | RECURRING |
| P1:ROLE_W_MISS | P1 | 66 | 343,870 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 26 | 156,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 167 | 722,490 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 404／PAPER PFS 61.5%／正式推薦 PFS 71.1%
- 第一失敗：{'NONE': 47, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 116, 'PREDICTION_ROLE_W': 141, 'PREDICTION_ROLE_P2': 63, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 46 | 78.5 | 62.5 | {'NONE': 6, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 17, 'PREDICTION_ROLE_W': 9, 'PREDICTION_ROLE_P2': 5, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 37 | 64.0 | 52.7 | {'PREDICTION_ROLE_W': 15, 'CAPITAL_EFFICIENCY': 10, 'NONE': 6, 'PREDICTION_ROLE_P2': 6} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 68 | 58.5 | 49.4 | {'PREDICTION_ROLE_W': 32, 'CAPITAL_EFFICIENCY': 23, 'PREDICTION_ROLE_P2': 8, 'NONE': 5} |
| URW | 41 | 61.0 | 26.9 | {'CAPITAL_EFFICIENCY': 14, 'PREDICTION_ROLE_W': 19, 'NONE': 2, 'PREDICTION_ROLE_P2': 6} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 404 | 32.4% | 66.8% | 32.4% | 15.8% | 13.9% | 9.4% | 24.3% | 1.54 |
| 正式推薦 | 366 | 32.2% | 61.5% | 61.5% | 74.0% | 100.0% | 62.8% | 36.1% | 1.44 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中32.8%（無作為9.6%、差+23.2）／P2 平均1.0頭 的中15.9%（無作為9.6%、差+6.3）／P3 平均1.0頭 的中13.9%（無作為9.6%、差+4.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.3%（無作為28.6%、差+34.7）／P2 平均6.0頭 的中74.4%（無作為57.3%、差+17.1）／P3 平均10.75頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.8/40（選択性補正込み）・能力順位 13.93/20（224R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.38/40（選択性補正込み）・能力順位 13.56/20（217R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 8,400円（6.3%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）43R・着順まで的中 2R／的中 60R のうち的中赤字 30R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 53.8%（同じ167Rの実績 63.5%）／券種別 EXACTA 60点 PFS 19.5%／TRIFECTA 112点 PFS 14.3%／TRIO 857点 PFS 61.4%／WIDE 288点 PFS 98.0%／WIN 9点 PFS 56.7%／荒れ度（発走前・1番人気オッズ）MID 86R PFS 72.2% 的中赤字 13/30／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 72R PFS 50.6% 的中赤字 16/26／UNKNOWN 3R PFS 152.7% 的中赤字 1/2／市場ミラーとの差 164R：実績 61.4% − ミラー 43.9% = Δ 17.5pt（95%区間 -4.7〜42.7、最高1R除き 11.3pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 351,200円（35.0%）／保護層の資金比率 0.0（167R）／組だけ的中（三連単は外れ）52R・着順まで的中 31R／的中 94R のうち的中赤字 78R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 49.0%（同じ167Rの実績 42.0%）／券種別 EXACTA 2541点 PFS 48.5%／TRIFECTA 4419点 PFS 27.4%／TRIO 3060点 PFS 57.8%／荒れ度（発走前・1番人気オッズ）MID 86R PFS 45.6% 的中赤字 39/47／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 72R PFS 40.7% 的中赤字 34/42／UNKNOWN 3R PFS 21.7% 的中赤字 3/3／市場ミラーとの差 164R：実績 42.4% − ミラー 70.1% = Δ -27.7pt（95%区間 -55.5〜-0.7、最高1R除き -32.7pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、62R×3券種）：購入 22／予算で削除 0／予想で除外 53／未生成・券種なし 111／役割馬の行き先 {'PURCHASED': 186}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、62R×3券種）：購入 75／予算で削除 22／予想で除外 54／未生成・券種なし 35／役割馬の行き先 {'PURCHASED': 456, 'BUDGET_COMPRESSED': 216}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 22R／W外 40R、2着が P2 役割 5R）：STATIC 5/22（平均3.64位）／STYLE_COND 7/22（平均3.45位） 救済2・喪失0／MARKET_COND 5/20（平均3.0位） 救済3・喪失2
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 40R／W外 22R、2着が P2 役割 33R）：STATIC 34/40（平均3.77位）／STYLE_COND 34/40（平均3.6位） 救済0・喪失0／MARKET_COND 36/38（平均2.82位） 救済4・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 165 | 817,800 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 145 | 534,750 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 72 | 390,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 404 | 1,655,050 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

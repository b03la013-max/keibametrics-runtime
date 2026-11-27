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

- 反省済みRace 170／PAPER PFS 62.5%／正式推薦 PFS 43.5%
- 第一失敗：{'PREDICTION_ROLE_P2': 27, 'CAPITAL_EFFICIENCY': 62, 'PREDICTION_ROLE_W': 67, 'NONE': 14}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 22 | 51.6 | 73.2 | {'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 12, 'PREDICTION_ROLE_W': 5, 'NONE': 2} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 38 | 62.3 | 51.3 | {'PREDICTION_ROLE_W': 16, 'CAPITAL_EFFICIENCY': 10, 'NONE': 6, 'PREDICTION_ROLE_P2': 6} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 33 | 96.2 | 39.7 | {'PREDICTION_ROLE_W': 16, 'NONE': 1, 'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 13} |
| URW | 42 | 59.7 | 35.3 | {'CAPITAL_EFFICIENCY': 14, 'PREDICTION_ROLE_W': 19, 'NONE': 3, 'PREDICTION_ROLE_P2': 6} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 170 | 30.6% | 63.5% | 30.6% | 14.7% | 13.5% | 7.1% | 24.7% | 1.51 |
| 正式推薦 | 170 | 31.2% | 60.6% | 60.6% | 76.5% | 100.0% | 64.1% | 42.9% | 1.47 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中30.6%（無作為9.5%、差+21.1）／P2 平均1.0頭 的中14.7%（無作為9.5%、差+5.2）／P3 平均1.0頭 的中13.5%（無作為9.5%、差+4.1）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中60.6%（無作為28.4%、差+32.2）／P2 平均6.0頭 的中76.5%（無作為56.8%、差+19.7）／P3 平均10.82頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.44/40（選択性補正込み）・能力順位 13.9/20（170R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.2/40（選択性補正込み）・能力順位 13.48/20（170R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 8,400円（6.2%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）43R・着順まで的中 2R／的中 60R のうち的中赤字 30R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 53.2%（同じ170Rの実績 62.5%）／券種別 EXACTA 60点 PFS 19.5%／TRIFECTA 112点 PFS 14.3%／TRIO 872点 PFS 60.4%／WIDE 294点 PFS 96.0%／WIN 9点 PFS 56.7%／荒れ度（発走前・1番人気オッズ）MID 88R PFS 70.7% 的中赤字 13/30／OPEN 7R PFS 49.8% 的中赤字 0/2／SOLID 72R PFS 50.6% 的中赤字 16/26／UNKNOWN 3R PFS 152.7% 的中赤字 1/2／市場ミラーとの差 167R：実績 60.4% − ミラー 45.0% = Δ 15.4pt（95%区間 -7.6〜40.4、最高1R除き 9.4pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 351,200円（34.4%）／保護層の資金比率 0.0（170R）／組だけ的中（三連単は外れ）52R・着順まで的中 32R／的中 95R のうち的中赤字 78R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 48.5%（同じ170Rの実績 43.5%）／券種別 EXACTA 2604点 PFS 49.6%／TRIFECTA 4536点 PFS 30.5%／TRIO 3060点 PFS 57.8%／荒れ度（発走前・1番人気オッズ）MID 88R PFS 48.8% 的中赤字 39/48／OPEN 7R PFS 15.6% 的中赤字 2/2／SOLID 72R PFS 40.7% 的中赤字 34/42／UNKNOWN 3R PFS 21.7% 的中赤字 3/3／市場ミラーとの差 167R：実績 43.9% − ミラー 69.1% = Δ -25.1pt（95%区間 -53.4〜-0.9、最高1R除き -30.1pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、65R×3券種）：購入 22／予算で削除 0／予想で除外 56／未生成・券種なし 117／役割馬の行き先 {'PURCHASED': 195}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、65R×3券種）：購入 77／予算で削除 22／予想で除外 58／未生成・券種なし 38／役割馬の行き先 {'PURCHASED': 482, 'BUDGET_COMPRESSED': 224}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 23R／W外 42R、2着が P2 役割 5R）：STATIC 5/23（平均3.57位）／STYLE_COND 8/23（平均3.35位） 救済3・喪失0／MARKET_COND 6/21（平均2.9位） 救済4・喪失2
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 42R／W外 23R、2着が P2 役割 34R）：STATIC 35/42（平均3.81位）／STYLE_COND 35/42（平均3.64位） 救済0・喪失0／MARKET_COND 38/40（平均2.83位） 救済5・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 78 | 284,490 | RECURRING |
| P1:ROLE_W_MISS | P1 | 67 | 349,870 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 27 | 162,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 170 | 734,490 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 407／PAPER PFS 61.1%／正式推薦 PFS 71.6%
- 第一失敗：{'NONE': 48, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 116, 'PREDICTION_ROLE_W': 142, 'PREDICTION_ROLE_P2': 64, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 46 | 78.5 | 62.5 | {'NONE': 6, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 17, 'PREDICTION_ROLE_W': 9, 'PREDICTION_ROLE_P2': 5, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 38 | 62.3 | 51.3 | {'PREDICTION_ROLE_W': 16, 'CAPITAL_EFFICIENCY': 10, 'NONE': 6, 'PREDICTION_ROLE_P2': 6} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 69 | 57.8 | 48.7 | {'PREDICTION_ROLE_W': 32, 'CAPITAL_EFFICIENCY': 23, 'PREDICTION_ROLE_P2': 9, 'NONE': 5} |
| URW | 42 | 59.7 | 35.3 | {'CAPITAL_EFFICIENCY': 14, 'PREDICTION_ROLE_W': 19, 'NONE': 3, 'PREDICTION_ROLE_P2': 6} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 407 | 32.4% | 66.8% | 32.4% | 15.7% | 13.8% | 9.3% | 24.1% | 1.54 |
| 正式推薦 | 369 | 32.2% | 61.5% | 61.5% | 74.0% | 100.0% | 63.1% | 36.0% | 1.43 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中32.8%（無作為9.6%、差+23.2）／P2 平均1.0頭 的中15.7%（無作為9.6%、差+6.2）／P3 平均1.0頭 的中13.7%（無作為9.6%、差+4.2）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.4%（無作為28.6%、差+34.7）／P2 平均6.0頭 的中74.3%（無作為57.2%、差+17.1）／P3 平均10.76頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.74/40（選択性補正込み）・能力順位 13.94/20（227R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.38/40（選択性補正込み）・能力順位 13.54/20（220R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 8,400円（6.2%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）43R・着順まで的中 2R／的中 60R のうち的中赤字 30R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 53.2%（同じ170Rの実績 62.5%）／券種別 EXACTA 60点 PFS 19.5%／TRIFECTA 112点 PFS 14.3%／TRIO 872点 PFS 60.4%／WIDE 294点 PFS 96.0%／WIN 9点 PFS 56.7%／荒れ度（発走前・1番人気オッズ）MID 88R PFS 70.7% 的中赤字 13/30／OPEN 7R PFS 49.8% 的中赤字 0/2／SOLID 72R PFS 50.6% 的中赤字 16/26／UNKNOWN 3R PFS 152.7% 的中赤字 1/2／市場ミラーとの差 167R：実績 60.4% − ミラー 45.0% = Δ 15.4pt（95%区間 -7.6〜40.4、最高1R除き 9.4pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 351,200円（34.4%）／保護層の資金比率 0.0（170R）／組だけ的中（三連単は外れ）52R・着順まで的中 32R／的中 95R のうち的中赤字 78R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 48.5%（同じ170Rの実績 43.5%）／券種別 EXACTA 2604点 PFS 49.6%／TRIFECTA 4536点 PFS 30.5%／TRIO 3060点 PFS 57.8%／荒れ度（発走前・1番人気オッズ）MID 88R PFS 48.8% 的中赤字 39/48／OPEN 7R PFS 15.6% 的中赤字 2/2／SOLID 72R PFS 40.7% 的中赤字 34/42／UNKNOWN 3R PFS 21.7% 的中赤字 3/3／市場ミラーとの差 167R：実績 43.9% − ミラー 69.1% = Δ -25.1pt（95%区間 -53.4〜-0.9、最高1R除き -30.1pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、65R×3券種）：購入 22／予算で削除 0／予想で除外 56／未生成・券種なし 117／役割馬の行き先 {'PURCHASED': 195}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、65R×3券種）：購入 77／予算で削除 22／予想で除外 58／未生成・券種なし 38／役割馬の行き先 {'PURCHASED': 482, 'BUDGET_COMPRESSED': 224}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 23R／W外 42R、2着が P2 役割 5R）：STATIC 5/23（平均3.57位）／STYLE_COND 8/23（平均3.35位） 救済3・喪失0／MARKET_COND 6/21（平均2.9位） 救済4・喪失2
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 42R／W外 23R、2着が P2 役割 34R）：STATIC 35/42（平均3.81位）／STYLE_COND 35/42（平均3.64位） 救済0・喪失0／MARKET_COND 38/40（平均2.83位） 救済5・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 166 | 823,800 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 145 | 534,750 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 73 | 396,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 407 | 1,667,050 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

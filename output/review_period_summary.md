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

- 反省済みRace 173／PAPER PFS 64.3%／正式推薦 PFS 43.1%
- 第一失敗：{'PREDICTION_ROLE_P2': 28, 'CAPITAL_EFFICIENCY': 63, 'PREDICTION_ROLE_W': 68, 'NONE': 14}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 22 | 51.6 | 73.2 | {'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 12, 'PREDICTION_ROLE_W': 5, 'NONE': 2} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 39 | 61.1 | 50.0 | {'PREDICTION_ROLE_W': 16, 'CAPITAL_EFFICIENCY': 10, 'NONE': 6, 'PREDICTION_ROLE_P2': 7} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 34 | 103.8 | 38.5 | {'PREDICTION_ROLE_W': 17, 'NONE': 1, 'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 13} |
| URW | 43 | 60.7 | 35.7 | {'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 19, 'NONE': 3, 'PREDICTION_ROLE_P2': 6} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 173 | 31.2% | 63.6% | 31.2% | 14.5% | 13.3% | 6.9% | 24.9% | 1.52 |
| 正式推薦 | 173 | 31.2% | 60.7% | 60.7% | 76.3% | 100.0% | 64.2% | 42.8% | 1.47 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中31.2%（無作為9.4%、差+21.8）／P2 平均1.0頭 的中14.5%（無作為9.4%、差+5.0）／P3 平均1.0頭 的中13.3%（無作為9.4%、差+3.9）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中60.7%（無作為28.3%、差+32.4）／P2 平均6.0頭 的中76.3%（無作為56.7%、差+19.6）／P3 平均10.83頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.52/40（選択性補正込み）・能力順位 13.93/20（173R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.23/40（選択性補正込み）・能力順位 13.5/20（173R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 8,400円（6.1%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）44R・着順まで的中 2R／的中 63R のうち的中赤字 31R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 53.4%（同じ173Rの実績 64.3%）／券種別 EXACTA 60点 PFS 19.5%／TRIFECTA 112点 PFS 14.3%／TRIO 887点 PFS 60.0%／WIDE 300点 PFS 104.6%／WIN 9点 PFS 56.7%／荒れ度（発走前・1番人気オッズ）MID 90R PFS 74.7% 的中赤字 13/32／OPEN 7R PFS 49.8% 的中赤字 0/2／SOLID 73R PFS 50.2% 的中赤字 17/27／UNKNOWN 3R PFS 152.7% 的中赤字 1/2／市場ミラーとの差 170R：実績 62.3% − ミラー 45.2% = Δ 17.1pt（95%区間 -6.8〜42.2、最高1R除き 11.1pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 351,200円（33.8%）／保護層の資金比率 0.0（173R）／組だけ的中（三連単は外れ）52R・着順まで的中 33R／的中 96R のうち的中赤字 79R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 48.3%（同じ173Rの実績 43.1%）／券種別 EXACTA 2652点 PFS 49.0%／TRIFECTA 4668点 PFS 30.1%／TRIO 3060点 PFS 57.8%／荒れ度（発走前・1番人気オッズ）MID 90R PFS 48.3% 的中赤字 40/49／OPEN 7R PFS 15.6% 的中赤字 2/2／SOLID 73R PFS 40.1% 的中赤字 34/42／UNKNOWN 3R PFS 21.7% 的中赤字 3/3／市場ミラーとの差 170R：実績 43.5% − ミラー 68.8% = Δ -25.3pt（95%区間 -53.3〜-0.2、最高1R除き -30.2pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、68R×3券種）：購入 23／予算で削除 0／予想で除外 58／未生成・券種なし 123／役割馬の行き先 {'PURCHASED': 204}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、68R×3券種）：購入 79／予算で削除 22／予想で除外 62／未生成・券種なし 41／役割馬の行き先 {'PURCHASED': 504, 'BUDGET_COMPRESSED': 237}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 25R／W外 43R、2着が P2 役割 5R）：STATIC 5/25（平均3.56位）／STYLE_COND 8/25（平均3.4位） 救済3・喪失0／MARKET_COND 6/23（平均2.87位） 救済4・喪失2
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 44R／W外 24R、2着が P2 役割 35R）：STATIC 36/44（平均3.91位）／STYLE_COND 36/44（平均3.75位） 救済0・喪失0／MARKET_COND 40/42（平均2.81位） 救済6・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 79 | 287,220 | RECURRING |
| P1:ROLE_W_MISS | P1 | 68 | 355,870 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 28 | 168,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 173 | 749,220 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 410／PAPER PFS 61.9%／正式推薦 PFS 71.2%
- 第一失敗：{'NONE': 48, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 117, 'PREDICTION_ROLE_W': 143, 'PREDICTION_ROLE_P2': 65, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 46 | 78.5 | 62.5 | {'NONE': 6, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 17, 'PREDICTION_ROLE_W': 9, 'PREDICTION_ROLE_P2': 5, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 39 | 61.1 | 50.0 | {'PREDICTION_ROLE_W': 16, 'CAPITAL_EFFICIENCY': 10, 'NONE': 6, 'PREDICTION_ROLE_P2': 7} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 70 | 61.9 | 48.0 | {'PREDICTION_ROLE_W': 33, 'CAPITAL_EFFICIENCY': 23, 'PREDICTION_ROLE_P2': 9, 'NONE': 5} |
| URW | 43 | 60.7 | 35.7 | {'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 19, 'NONE': 3, 'PREDICTION_ROLE_P2': 6} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 410 | 32.7% | 66.8% | 32.7% | 15.6% | 13.7% | 9.3% | 24.1% | 1.54 |
| 正式推薦 | 372 | 32.3% | 61.6% | 61.6% | 73.9% | 100.0% | 63.2% | 36.0% | 1.44 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中33.1%（無作為9.5%、差+23.6）／P2 平均1.0頭 的中15.6%（無作為9.5%、差+6.0）／P3 平均1.0頭 的中13.6%（無作為9.5%、差+4.0）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.4%（無作為28.6%、差+34.8）／P2 平均6.0頭 的中74.2%（無作為57.2%、差+17.1）／P3 平均10.77頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.8/40（選択性補正込み）・能力順位 13.96/20（230R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.4/40（選択性補正込み）・能力順位 13.55/20（223R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 8,400円（6.1%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）44R・着順まで的中 2R／的中 63R のうち的中赤字 31R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 53.4%（同じ173Rの実績 64.3%）／券種別 EXACTA 60点 PFS 19.5%／TRIFECTA 112点 PFS 14.3%／TRIO 887点 PFS 60.0%／WIDE 300点 PFS 104.6%／WIN 9点 PFS 56.7%／荒れ度（発走前・1番人気オッズ）MID 90R PFS 74.7% 的中赤字 13/32／OPEN 7R PFS 49.8% 的中赤字 0/2／SOLID 73R PFS 50.2% 的中赤字 17/27／UNKNOWN 3R PFS 152.7% 的中赤字 1/2／市場ミラーとの差 170R：実績 62.3% − ミラー 45.2% = Δ 17.1pt（95%区間 -6.8〜42.2、最高1R除き 11.1pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 351,200円（33.8%）／保護層の資金比率 0.0（173R）／組だけ的中（三連単は外れ）52R・着順まで的中 33R／的中 96R のうち的中赤字 79R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 48.3%（同じ173Rの実績 43.1%）／券種別 EXACTA 2652点 PFS 49.0%／TRIFECTA 4668点 PFS 30.1%／TRIO 3060点 PFS 57.8%／荒れ度（発走前・1番人気オッズ）MID 90R PFS 48.3% 的中赤字 40/49／OPEN 7R PFS 15.6% 的中赤字 2/2／SOLID 73R PFS 40.1% 的中赤字 34/42／UNKNOWN 3R PFS 21.7% 的中赤字 3/3／市場ミラーとの差 170R：実績 43.5% − ミラー 68.8% = Δ -25.3pt（95%区間 -53.3〜-0.2、最高1R除き -30.2pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、68R×3券種）：購入 23／予算で削除 0／予想で除外 58／未生成・券種なし 123／役割馬の行き先 {'PURCHASED': 204}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、68R×3券種）：購入 79／予算で削除 22／予想で除外 62／未生成・券種なし 41／役割馬の行き先 {'PURCHASED': 504, 'BUDGET_COMPRESSED': 237}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 25R／W外 43R、2着が P2 役割 5R）：STATIC 5/25（平均3.56位）／STYLE_COND 8/25（平均3.4位） 救済3・喪失0／MARKET_COND 6/23（平均2.87位） 救済4・喪失2
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 44R／W外 24R、2着が P2 役割 35R）：STATIC 36/44（平均3.91位）／STYLE_COND 36/44（平均3.75位） 救済0・喪失0／MARKET_COND 40/42（平均2.81位） 救済6・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 167 | 829,800 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 146 | 537,480 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 74 | 402,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 410 | 1,681,780 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

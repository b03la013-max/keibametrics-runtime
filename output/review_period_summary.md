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

- 反省済みRace 139／PAPER PFS 64.8%／正式推薦 PFS 41.2%
- 第一失敗：{'PREDICTION_ROLE_P2': 25, 'CAPITAL_EFFICIENCY': 49, 'PREDICTION_ROLE_W': 54, 'NONE': 11}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 16 | 26.6 | 70.9 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 5, 'NONE': 1} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 30 | 70.4 | 45.1 | {'PREDICTION_ROLE_W': 11, 'CAPITAL_EFFICIENCY': 8, 'NONE': 5, 'PREDICTION_ROLE_P2': 6} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 24 | 105.1 | 47.9 | {'PREDICTION_ROLE_W': 14, 'NONE': 1, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 7} |
| URW | 34 | 72.2 | 30.7 | {'CAPITAL_EFFICIENCY': 13, 'PREDICTION_ROLE_W': 13, 'NONE': 2, 'PREDICTION_ROLE_P2': 6} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 139 | 28.8% | 64.7% | 28.8% | 10.8% | 11.5% | 6.5% | 25.2% | 1.51 |
| 正式推薦 | 139 | 30.2% | 61.2% | 61.2% | 73.4% | 100.0% | 61.2% | 43.9% | 1.49 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中28.8%（無作為9.4%、差+19.4）／P2 平均1.0頭 的中10.8%（無作為9.4%、差+1.4）／P3 平均1.0頭 的中11.5%（無作為9.4%、差+2.1）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中61.2%（無作為28.2%、差+32.9）／P2 平均6.0頭 的中73.4%（無作為56.5%、差+16.9）／P3 平均10.86頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.88/40（選択性補正込み）・能力順位 13.85/20（139R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.1/40（選択性補正込み）・能力順位 13.42/20（139R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 7,200円（6.5%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）37R・着順まで的中 1R／的中 50R のうち的中赤字 24R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 50.8%（同じ139Rの実績 64.8%）／券種別 EXACTA 52点 PFS 13.8%／TRIFECTA 96点 PFS 6.1%／TRIO 717点 PFS 67.7%／WIDE 238点 PFS 91.8%／WIN 8点 PFS 43.8%／荒れ度（発走前・1番人気オッズ）MID 71R PFS 72.5% 的中赤字 11/25／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 60R PFS 52.7% 的中赤字 13/22／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 137R：実績 62.5% − ミラー 43.1% = Δ 19.4pt（95%区間 -6.2〜49.6、最高1R除き 12.1pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 318,900円（38.2%）／保護層の資金比率 0.0（139R）／組だけ的中（三連単は外れ）44R・着順まで的中 22R／的中 76R のうち的中赤字 63R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 46.4%（同じ139Rの実績 41.2%）／券種別 EXACTA 2085点 PFS 48.0%／TRIFECTA 3475点 PFS 22.7%／TRIO 2780点 PFS 59.3%／荒れ度（発走前・1番人気オッズ）MID 71R PFS 49.0% 的中赤字 28/36／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 60R PFS 35.1% 的中赤字 31/36／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 137R：実績 41.5% − ミラー 71.2% = Δ -29.6pt（95%区間 -60.7〜-0.5、最高1R除き -35.7pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、34R×3券種）：購入 14／予算で削除 0／予想で除外 28／未生成・券種なし 60／役割馬の行き先 {'PURCHASED': 102}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、34R×3券種）：購入 42／予算で削除 13／予想で除外 32／未生成・券種なし 15／役割馬の行き先 {'PURCHASED': 251, 'BUDGET_COMPRESSED': 125}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 11R／W外 23R、2着が P2 役割 0R）：STATIC 0/11（平均4.36位）／STYLE_COND 2/11（平均4.09位） 救済2・喪失0／MARKET_COND 2/10（平均3.6位） 救済2・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 24R／W外 10R、2着が P2 役割 18R）：STATIC 19/24（平均3.92位）／STYLE_COND 19/24（平均3.79位） 救済0・喪失0／MARKET_COND 21/23（平均3.04位） 救済3・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 63 | 225,040 | RECURRING |
| P1:ROLE_W_MISS | P1 | 54 | 282,370 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 25 | 150,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 139 | 603,040 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 376／PAPER PFS 61.9%／正式推薦 PFS 73.2%
- 第一失敗：{'NONE': 45, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 103, 'PREDICTION_ROLE_W': 129, 'PREDICTION_ROLE_P2': 62, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 40 | 73.7 | 59.0 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 13, 'PREDICTION_ROLE_W': 9, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 30 | 70.4 | 45.1 | {'PREDICTION_ROLE_W': 11, 'CAPITAL_EFFICIENCY': 8, 'NONE': 5, 'PREDICTION_ROLE_P2': 6} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 60 | 57.0 | 53.3 | {'PREDICTION_ROLE_W': 30, 'CAPITAL_EFFICIENCY': 17, 'PREDICTION_ROLE_P2': 8, 'NONE': 5} |
| URW | 34 | 72.2 | 30.7 | {'CAPITAL_EFFICIENCY': 13, 'PREDICTION_ROLE_W': 13, 'NONE': 2, 'PREDICTION_ROLE_P2': 6} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 376 | 31.9% | 67.6% | 31.9% | 14.4% | 13.0% | 9.3% | 24.2% | 1.54 |
| 正式推薦 | 338 | 32.0% | 61.8% | 61.8% | 72.5% | 100.0% | 61.8% | 35.8% | 1.44 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中32.1%（無作為9.5%、差+22.5）／P2 平均1.0頭 的中13.8%（無作為9.5%、差+4.3）／P3 平均1.0頭 的中12.7%（無作為9.5%、差+3.1）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中64.0%（無作為28.6%、差+35.4）／P2 平均6.0頭 的中72.4%（無作為57.1%、差+15.3）／P3 平均10.77頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.39/40（選択性補正込み）・能力順位 13.91/20（196R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.34/40（選択性補正込み）・能力順位 13.51/20（189R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 7,200円（6.5%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）37R・着順まで的中 1R／的中 50R のうち的中赤字 24R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 50.8%（同じ139Rの実績 64.8%）／券種別 EXACTA 52点 PFS 13.8%／TRIFECTA 96点 PFS 6.1%／TRIO 717点 PFS 67.7%／WIDE 238点 PFS 91.8%／WIN 8点 PFS 43.8%／荒れ度（発走前・1番人気オッズ）MID 71R PFS 72.5% 的中赤字 11/25／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 60R PFS 52.7% 的中赤字 13/22／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 137R：実績 62.5% − ミラー 43.1% = Δ 19.4pt（95%区間 -6.2〜49.6、最高1R除き 12.1pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 318,900円（38.2%）／保護層の資金比率 0.0（139R）／組だけ的中（三連単は外れ）44R・着順まで的中 22R／的中 76R のうち的中赤字 63R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 46.4%（同じ139Rの実績 41.2%）／券種別 EXACTA 2085点 PFS 48.0%／TRIFECTA 3475点 PFS 22.7%／TRIO 2780点 PFS 59.3%／荒れ度（発走前・1番人気オッズ）MID 71R PFS 49.0% 的中赤字 28/36／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 60R PFS 35.1% 的中赤字 31/36／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 137R：実績 41.5% − ミラー 71.2% = Δ -29.6pt（95%区間 -60.7〜-0.5、最高1R除き -35.7pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、34R×3券種）：購入 14／予算で削除 0／予想で除外 28／未生成・券種なし 60／役割馬の行き先 {'PURCHASED': 102}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、34R×3券種）：購入 42／予算で削除 13／予想で除外 32／未生成・券種なし 15／役割馬の行き先 {'PURCHASED': 251, 'BUDGET_COMPRESSED': 125}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 11R／W外 23R、2着が P2 役割 0R）：STATIC 0/11（平均4.36位）／STYLE_COND 2/11（平均4.09位） 救済2・喪失0／MARKET_COND 2/10（平均3.6位） 救済2・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 24R／W外 10R、2着が P2 役割 18R）：STATIC 19/24（平均3.92位）／STYLE_COND 19/24（平均3.79位） 救済0・喪失0／MARKET_COND 21/23（平均3.04位） 救済3・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 153 | 756,300 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 130 | 475,300 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 71 | 384,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 376 | 1,535,600 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

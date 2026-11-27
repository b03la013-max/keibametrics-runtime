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

- 反省済みRace 179／PAPER PFS 64.1%／正式推薦 PFS 43.4%
- 第一失敗：{'PREDICTION_ROLE_P2': 28, 'CAPITAL_EFFICIENCY': 67, 'PREDICTION_ROLE_W': 69, 'NONE': 15}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 22 | 51.6 | 73.2 | {'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 12, 'PREDICTION_ROLE_W': 5, 'NONE': 2} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 41 | 58.6 | 49.8 | {'PREDICTION_ROLE_W': 16, 'CAPITAL_EFFICIENCY': 12, 'NONE': 6, 'PREDICTION_ROLE_P2': 7} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 36 | 102.8 | 37.8 | {'PREDICTION_ROLE_W': 18, 'NONE': 1, 'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 14} |
| URW | 45 | 61.7 | 37.8 | {'CAPITAL_EFFICIENCY': 16, 'PREDICTION_ROLE_W': 19, 'NONE': 4, 'PREDICTION_ROLE_P2': 6} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 179 | 32.4% | 64.8% | 32.4% | 14.5% | 13.4% | 6.7% | 25.1% | 1.54 |
| 正式推薦 | 179 | 31.8% | 61.5% | 61.5% | 77.1% | 100.0% | 64.8% | 43.0% | 1.49 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中32.4%（無作為9.4%、差+23.0）／P2 平均1.0頭 的中14.5%（無作為9.4%、差+5.1）／P3 平均1.0頭 的中13.4%（無作為9.4%、差+4.0）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中61.5%（無作為28.2%、差+33.2）／P2 平均6.0頭 的中77.1%（無作為56.4%、差+20.7）／P3 平均10.87頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.75/40（選択性補正込み）・能力順位 14.01/20（179R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.42/40（選択性補正込み）・能力順位 13.59/20（179R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 8,400円（6.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）46R・着順まで的中 2R／的中 66R のうち的中赤字 32R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 52.2%（同じ179Rの実績 64.1%）／券種別 EXACTA 60点 PFS 19.5%／TRIFECTA 112点 PFS 14.3%／TRIO 917点 PFS 60.4%／WIDE 312点 PFS 101.6%／WIN 9点 PFS 56.7%／荒れ度（発走前・1番人気オッズ）MID 94R PFS 75.0% 的中赤字 13/34／OPEN 7R PFS 49.8% 的中赤字 0/2／SOLID 75R PFS 49.3% 的中赤字 18/28／UNKNOWN 3R PFS 152.7% 的中赤字 1/2／市場ミラーとの差 176R：実績 62.2% − ミラー 44.4% = Δ 17.8pt（95%区間 -4.9〜42.7、最高1R除き 12.0pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 351,200円（32.7%）／保護層の資金比率 0.0（179R）／組だけ的中（三連単は外れ）53R・着順まで的中 36R／的中 101R のうち的中赤字 83R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 46.9%（同じ179Rの実績 43.4%）／券種別 EXACTA 2754点 PFS 49.5%／TRIFECTA 4926点 PFS 31.1%／TRIO 3060点 PFS 57.8%／荒れ度（発走前・1番人気オッズ）MID 94R PFS 48.6% 的中赤字 42/52／OPEN 7R PFS 15.6% 的中赤字 2/2／SOLID 75R PFS 40.3% 的中赤字 36/44／UNKNOWN 3R PFS 21.7% 的中赤字 3/3／市場ミラーとの差 176R：実績 43.8% − ミラー 67.9% = Δ -24.1pt（95%区間 -49.8〜1.0、最高1R除き -28.8pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、74R×3券種）：購入 25／予算で削除 0／予想で除外 62／未生成・券種なし 135／役割馬の行き先 {'PURCHASED': 222}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、74R×3券種）：購入 87／予算で削除 24／予想で除外 64／未生成・券種なし 47／役割馬の行き先 {'PURCHASED': 551, 'BUDGET_COMPRESSED': 262}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 29R／W外 45R、2着が P2 役割 6R）：STATIC 6/29（平均3.48位）／STYLE_COND 9/29（平均3.31位） 救済3・喪失0／MARKET_COND 7/27（平均2.81位） 救済5・喪失3
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 49R／W外 25R、2着が P2 役割 40R）：STATIC 41/49（平均3.71位）／STYLE_COND 41/49（平均3.57位） 救済0・喪失0／MARKET_COND 45/47（平均2.83位） 救済6・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 83 | 301,210 | RECURRING |
| P1:ROLE_W_MISS | P1 | 69 | 361,870 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 28 | 168,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 179 | 769,210 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 416／PAPER PFS 61.8%／正式推薦 PFS 70.9%
- 第一失敗：{'NONE': 49, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 121, 'PREDICTION_ROLE_W': 144, 'PREDICTION_ROLE_P2': 65, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 46 | 78.5 | 62.5 | {'NONE': 6, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 17, 'PREDICTION_ROLE_W': 9, 'PREDICTION_ROLE_P2': 5, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 41 | 58.6 | 49.8 | {'PREDICTION_ROLE_W': 16, 'CAPITAL_EFFICIENCY': 12, 'NONE': 6, 'PREDICTION_ROLE_P2': 7} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 72 | 62.3 | 47.3 | {'PREDICTION_ROLE_W': 34, 'CAPITAL_EFFICIENCY': 24, 'PREDICTION_ROLE_P2': 9, 'NONE': 5} |
| URW | 45 | 61.7 | 37.8 | {'CAPITAL_EFFICIENCY': 16, 'PREDICTION_ROLE_W': 19, 'NONE': 4, 'PREDICTION_ROLE_P2': 6} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 416 | 33.2% | 67.3% | 33.2% | 15.6% | 13.7% | 9.1% | 24.3% | 1.55 |
| 正式推薦 | 378 | 32.5% | 61.9% | 61.9% | 74.3% | 100.0% | 63.5% | 36.2% | 1.44 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中33.8%（無作為9.5%、差+24.2）／P2 平均1.0頭 的中15.6%（無作為9.5%、差+6.1）／P3 平均1.0頭 的中13.6%（無作為9.5%、差+4.1）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.8%（無作為28.5%、差+35.3）／P2 平均6.0頭 的中74.8%（無作為57.0%、差+17.7）／P3 平均10.79頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.96/40（選択性補正込み）・能力順位 14.02/20（236R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.55/40（選択性補正込み）・能力順位 13.62/20（229R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 8,400円（6.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）46R・着順まで的中 2R／的中 66R のうち的中赤字 32R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 52.2%（同じ179Rの実績 64.1%）／券種別 EXACTA 60点 PFS 19.5%／TRIFECTA 112点 PFS 14.3%／TRIO 917点 PFS 60.4%／WIDE 312点 PFS 101.6%／WIN 9点 PFS 56.7%／荒れ度（発走前・1番人気オッズ）MID 94R PFS 75.0% 的中赤字 13/34／OPEN 7R PFS 49.8% 的中赤字 0/2／SOLID 75R PFS 49.3% 的中赤字 18/28／UNKNOWN 3R PFS 152.7% 的中赤字 1/2／市場ミラーとの差 176R：実績 62.2% − ミラー 44.4% = Δ 17.8pt（95%区間 -4.9〜42.7、最高1R除き 12.0pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 351,200円（32.7%）／保護層の資金比率 0.0（179R）／組だけ的中（三連単は外れ）53R・着順まで的中 36R／的中 101R のうち的中赤字 83R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 46.9%（同じ179Rの実績 43.4%）／券種別 EXACTA 2754点 PFS 49.5%／TRIFECTA 4926点 PFS 31.1%／TRIO 3060点 PFS 57.8%／荒れ度（発走前・1番人気オッズ）MID 94R PFS 48.6% 的中赤字 42/52／OPEN 7R PFS 15.6% 的中赤字 2/2／SOLID 75R PFS 40.3% 的中赤字 36/44／UNKNOWN 3R PFS 21.7% 的中赤字 3/3／市場ミラーとの差 176R：実績 43.8% − ミラー 67.9% = Δ -24.1pt（95%区間 -49.8〜1.0、最高1R除き -28.8pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、74R×3券種）：購入 25／予算で削除 0／予想で除外 62／未生成・券種なし 135／役割馬の行き先 {'PURCHASED': 222}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、74R×3券種）：購入 87／予算で削除 24／予想で除外 64／未生成・券種なし 47／役割馬の行き先 {'PURCHASED': 551, 'BUDGET_COMPRESSED': 262}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 29R／W外 45R、2着が P2 役割 6R）：STATIC 6/29（平均3.48位）／STYLE_COND 9/29（平均3.31位） 救済3・喪失0／MARKET_COND 7/27（平均2.81位） 救済5・喪失3
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 49R／W外 25R、2着が P2 役割 40R）：STATIC 41/49（平均3.71位）／STYLE_COND 41/49（平均3.57位） 救済0・喪失0／MARKET_COND 45/47（平均2.83位） 救済6・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 168 | 835,800 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 150 | 551,470 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 74 | 402,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 416 | 1,701,770 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

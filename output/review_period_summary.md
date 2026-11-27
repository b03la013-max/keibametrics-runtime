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

- 反省済みRace 159／PAPER PFS 64.6%／正式推薦 PFS 41.9%
- 第一失敗：{'PREDICTION_ROLE_P2': 26, 'CAPITAL_EFFICIENCY': 60, 'PREDICTION_ROLE_W': 60, 'NONE': 13}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 22 | 51.6 | 73.2 | {'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 12, 'PREDICTION_ROLE_W': 5, 'NONE': 2} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 36 | 65.7 | 45.8 | {'PREDICTION_ROLE_W': 14, 'CAPITAL_EFFICIENCY': 10, 'NONE': 6, 'PREDICTION_ROLE_P2': 6} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 29 | 98.5 | 44.1 | {'PREDICTION_ROLE_W': 15, 'NONE': 1, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 11} |
| URW | 37 | 67.0 | 29.0 | {'CAPITAL_EFFICIENCY': 14, 'PREDICTION_ROLE_W': 15, 'NONE': 2, 'PREDICTION_ROLE_P2': 6} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 159 | 31.4% | 64.8% | 31.4% | 13.8% | 13.2% | 7.5% | 25.8% | 1.53 |
| 正式推薦 | 159 | 31.4% | 62.3% | 62.3% | 75.5% | 100.0% | 63.5% | 44.0% | 1.48 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中31.4%（無作為9.5%、差+22.0）／P2 平均1.0頭 的中13.8%（無作為9.5%、差+4.4）／P3 平均1.0頭 的中13.2%（無作為9.5%、差+3.7）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中62.3%（無作為28.4%、差+33.9）／P2 平均6.0頭 的中75.5%（無作為56.8%、差+18.7）／P3 平均10.81頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.6/40（選択性補正込み）・能力順位 13.92/20（159R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.26/40（選択性補正込み）・能力順位 13.46/20（159R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 8,400円（6.6%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）42R・着順まで的中 2R／的中 59R のうち的中赤字 30R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 55.1%（同じ159Rの実績 64.6%）／券種別 EXACTA 60点 PFS 19.5%／TRIFECTA 112点 PFS 14.3%／TRIO 817点 PFS 62.2%／WIDE 272点 PFS 102.9%／WIN 9点 PFS 56.7%／荒れ度（発走前・1番人気オッズ）MID 82R PFS 72.1% 的中赤字 13/29／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 68R PFS 53.0% 的中赤字 16/26／UNKNOWN 3R PFS 152.7% 的中赤字 1/2／市場ミラーとの差 156R：実績 62.5% − ミラー 45.2% = Δ 17.3pt（95%区間 -6.7〜43.4、最高1R除き 10.9pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 351,200円（36.8%）／保護層の資金比率 0.0（159R）／組だけ的中（三連単は外れ）49R・着順まで的中 29R／的中 90R のうち的中赤字 75R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 50.6%（同じ159Rの実績 41.9%）／券種別 EXACTA 2400点 PFS 49.3%／TRIFECTA 4080点 PFS 25.7%／TRIO 3060点 PFS 57.8%／荒れ度（発走前・1番人気オッズ）MID 82R PFS 47.1% 的中赤字 36/44／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 68R PFS 38.7% 的中赤字 34/41／UNKNOWN 3R PFS 21.7% 的中赤字 3/3／市場ミラーとの差 156R：実績 42.3% − ミラー 71.8% = Δ -29.6pt（95%区間 -58.0〜-3.0、最高1R除き -34.9pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、54R×3券種）：購入 21／予算で削除 0／予想で除外 46／未生成・券種なし 95／役割馬の行き先 {'PURCHASED': 162}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、54R×3券種）：購入 70／予算で削除 20／予想で除外 45／未生成・券種なし 27／役割馬の行き先 {'PURCHASED': 399, 'BUDGET_COMPRESSED': 187}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 21R／W外 33R、2着が P2 役割 4R）：STATIC 4/21（平均3.76位）／STYLE_COND 6/21（平均3.57位） 救済2・喪失0／MARKET_COND 5/19（平均3.05位） 救済3・喪失1
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 38R／W外 16R、2着が P2 役割 31R）：STATIC 32/38（平均3.82位）／STYLE_COND 32/38（平均3.68位） 救済0・喪失0／MARKET_COND 34/36（平均2.86位） 救済4・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 75 | 270,060 | RECURRING |
| P1:ROLE_W_MISS | P1 | 60 | 315,650 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 26 | 156,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 159 | 684,060 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 396／PAPER PFS 61.9%／正式推薦 PFS 71.7%
- 第一失敗：{'NONE': 47, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 114, 'PREDICTION_ROLE_W': 135, 'PREDICTION_ROLE_P2': 63, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 46 | 78.5 | 62.5 | {'NONE': 6, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 17, 'PREDICTION_ROLE_W': 9, 'PREDICTION_ROLE_P2': 5, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 36 | 65.7 | 45.8 | {'PREDICTION_ROLE_W': 14, 'CAPITAL_EFFICIENCY': 10, 'NONE': 6, 'PREDICTION_ROLE_P2': 6} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 65 | 56.9 | 51.2 | {'PREDICTION_ROLE_W': 31, 'CAPITAL_EFFICIENCY': 21, 'PREDICTION_ROLE_P2': 8, 'NONE': 5} |
| URW | 37 | 67.0 | 29.0 | {'CAPITAL_EFFICIENCY': 14, 'PREDICTION_ROLE_W': 15, 'NONE': 2, 'PREDICTION_ROLE_P2': 6} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 396 | 32.8% | 67.4% | 32.8% | 15.4% | 13.6% | 9.6% | 24.5% | 1.55 |
| 正式推薦 | 358 | 32.4% | 62.3% | 62.3% | 73.5% | 100.0% | 62.8% | 36.3% | 1.44 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中33.3%（無作為9.6%、差+23.8）／P2 平均1.0頭 的中15.3%（無作為9.6%、差+5.7）／P3 平均1.0頭 的中13.5%（無作為9.6%、差+4.0）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中64.4%（無作為28.6%、差+35.8）／P2 平均6.0頭 的中73.7%（無作為57.2%、差+16.4）／P3 平均10.75頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.87/40（選択性補正込み）・能力順位 13.95/20（216R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.44/40（選択性補正込み）・能力順位 13.52/20（209R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 8,400円（6.6%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）42R・着順まで的中 2R／的中 59R のうち的中赤字 30R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 55.1%（同じ159Rの実績 64.6%）／券種別 EXACTA 60点 PFS 19.5%／TRIFECTA 112点 PFS 14.3%／TRIO 817点 PFS 62.2%／WIDE 272点 PFS 102.9%／WIN 9点 PFS 56.7%／荒れ度（発走前・1番人気オッズ）MID 82R PFS 72.1% 的中赤字 13/29／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 68R PFS 53.0% 的中赤字 16/26／UNKNOWN 3R PFS 152.7% 的中赤字 1/2／市場ミラーとの差 156R：実績 62.5% − ミラー 45.2% = Δ 17.3pt（95%区間 -6.7〜43.4、最高1R除き 10.9pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 351,200円（36.8%）／保護層の資金比率 0.0（159R）／組だけ的中（三連単は外れ）49R・着順まで的中 29R／的中 90R のうち的中赤字 75R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 50.6%（同じ159Rの実績 41.9%）／券種別 EXACTA 2400点 PFS 49.3%／TRIFECTA 4080点 PFS 25.7%／TRIO 3060点 PFS 57.8%／荒れ度（発走前・1番人気オッズ）MID 82R PFS 47.1% 的中赤字 36/44／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 68R PFS 38.7% 的中赤字 34/41／UNKNOWN 3R PFS 21.7% 的中赤字 3/3／市場ミラーとの差 156R：実績 42.3% − ミラー 71.8% = Δ -29.6pt（95%区間 -58.0〜-3.0、最高1R除き -34.9pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、54R×3券種）：購入 21／予算で削除 0／予想で除外 46／未生成・券種なし 95／役割馬の行き先 {'PURCHASED': 162}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、54R×3券種）：購入 70／予算で削除 20／予想で除外 45／未生成・券種なし 27／役割馬の行き先 {'PURCHASED': 399, 'BUDGET_COMPRESSED': 187}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 21R／W外 33R、2着が P2 役割 4R）：STATIC 4/21（平均3.76位）／STYLE_COND 6/21（平均3.57位） 救済2・喪失0／MARKET_COND 5/19（平均3.05位） 救済3・喪失1
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 38R／W外 16R、2着が P2 役割 31R）：STATIC 32/38（平均3.82位）／STYLE_COND 32/38（平均3.68位） 救済0・喪失0／MARKET_COND 34/36（平均2.86位） 救済4・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 159 | 789,580 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 142 | 520,320 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 72 | 390,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 396 | 1,616,620 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

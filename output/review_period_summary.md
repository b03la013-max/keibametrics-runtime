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

- 反省済みRace 160／PAPER PFS 64.3%／正式推薦 PFS 41.8%
- 第一失敗：{'PREDICTION_ROLE_P2': 26, 'CAPITAL_EFFICIENCY': 60, 'PREDICTION_ROLE_W': 61, 'NONE': 13}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 22 | 51.6 | 73.2 | {'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 12, 'PREDICTION_ROLE_W': 5, 'NONE': 2} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 36 | 65.7 | 45.8 | {'PREDICTION_ROLE_W': 14, 'CAPITAL_EFFICIENCY': 10, 'NONE': 6, 'PREDICTION_ROLE_P2': 6} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 29 | 98.5 | 44.1 | {'PREDICTION_ROLE_W': 15, 'NONE': 1, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 11} |
| URW | 38 | 65.4 | 29.0 | {'CAPITAL_EFFICIENCY': 14, 'PREDICTION_ROLE_W': 16, 'NONE': 2, 'PREDICTION_ROLE_P2': 6} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 160 | 31.2% | 64.4% | 31.2% | 13.8% | 13.8% | 7.5% | 25.6% | 1.52 |
| 正式推薦 | 160 | 31.2% | 61.9% | 61.9% | 75.6% | 100.0% | 63.8% | 44.4% | 1.48 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中31.2%（無作為9.5%、差+21.8）／P2 平均1.0頭 的中13.8%（無作為9.5%、差+4.3）／P3 平均1.0頭 的中13.8%（無作為9.5%、差+4.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中61.9%（無作為28.4%、差+33.5）／P2 平均6.0頭 的中75.6%（無作為56.8%、差+18.8）／P3 平均10.81頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.58/40（選択性補正込み）・能力順位 13.91/20（160R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.24/40（選択性補正込み）・能力順位 13.46/20（160R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 8,400円（6.6%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）42R・着順まで的中 2R／的中 59R のうち的中赤字 30R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 54.9%（同じ160Rの実績 64.3%）／券種別 EXACTA 60点 PFS 19.5%／TRIFECTA 112点 PFS 14.3%／TRIO 822点 PFS 61.8%／WIDE 274点 PFS 102.2%／WIN 9点 PFS 56.7%／荒れ度（発走前・1番人気オッズ）MID 83R PFS 71.3% 的中赤字 13/29／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 68R PFS 53.0% 的中赤字 16/26／UNKNOWN 3R PFS 152.7% 的中赤字 1/2／市場ミラーとの差 157R：実績 62.1% − ミラー 45.4% = Δ 16.8pt（95%区間 -8.4〜43.6、最高1R除き 10.4pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 351,200円（36.6%）／保護層の資金比率 0.0（160R）／組だけ的中（三連単は外れ）49R・着順まで的中 30R／的中 91R のうち的中赤字 76R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 50.3%（同じ160Rの実績 41.8%）／券種別 EXACTA 2421点 PFS 48.8%／TRIFECTA 4119点 PFS 25.9%／TRIO 3060点 PFS 57.8%／荒れ度（発走前・1番人気オッズ）MID 83R PFS 46.8% 的中赤字 37/45／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 68R PFS 38.7% 的中赤字 34/41／UNKNOWN 3R PFS 21.7% 的中赤字 3/3／市場ミラーとの差 157R：実績 42.2% − ミラー 71.4% = Δ -29.2pt（95%区間 -58.6〜-2.4、最高1R除き -34.5pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、55R×3券種）：購入 21／予算で削除 0／予想で除外 47／未生成・券種なし 97／役割馬の行き先 {'PURCHASED': 165}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、55R×3券種）：購入 71／予算で削除 20／予想で除外 46／未生成・券種なし 28／役割馬の行き先 {'PURCHASED': 407, 'BUDGET_COMPRESSED': 189}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 21R／W外 34R、2着が P2 役割 4R）：STATIC 4/21（平均3.76位）／STYLE_COND 6/21（平均3.57位） 救済2・喪失0／MARKET_COND 5/19（平均3.05位） 救済3・喪失1
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 38R／W外 17R、2着が P2 役割 31R）：STATIC 32/38（平均3.82位）／STYLE_COND 32/38（平均3.68位） 救済0・喪失0／MARKET_COND 34/36（平均2.86位） 救済4・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 76 | 274,280 | RECURRING |
| P1:ROLE_W_MISS | P1 | 61 | 319,870 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 26 | 156,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 160 | 688,280 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 397／PAPER PFS 61.8%／正式推薦 PFS 71.6%
- 第一失敗：{'NONE': 47, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 114, 'PREDICTION_ROLE_W': 136, 'PREDICTION_ROLE_P2': 63, 'EXACT_ORIENTATION': 4}

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
| URW | 38 | 65.4 | 29.0 | {'CAPITAL_EFFICIENCY': 14, 'PREDICTION_ROLE_W': 16, 'NONE': 2, 'PREDICTION_ROLE_P2': 6} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 397 | 32.7% | 67.3% | 32.7% | 15.4% | 13.9% | 9.6% | 24.4% | 1.55 |
| 正式推薦 | 359 | 32.3% | 62.1% | 62.1% | 73.5% | 100.0% | 63.0% | 36.5% | 1.43 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中33.2%（無作為9.6%、差+23.7）／P2 平均1.0頭 的中15.2%（無作為9.6%、差+5.7）／P3 平均1.0頭 的中13.8%（無作為9.6%、差+4.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中64.2%（無作為28.6%、差+35.6）／P2 平均6.0頭 的中73.8%（無作為57.2%、差+16.5）／P3 平均10.75頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.86/40（選択性補正込み）・能力順位 13.95/20（217R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.42/40（選択性補正込み）・能力順位 13.52/20（210R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 8,400円（6.6%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）42R・着順まで的中 2R／的中 59R のうち的中赤字 30R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 54.9%（同じ160Rの実績 64.3%）／券種別 EXACTA 60点 PFS 19.5%／TRIFECTA 112点 PFS 14.3%／TRIO 822点 PFS 61.8%／WIDE 274点 PFS 102.2%／WIN 9点 PFS 56.7%／荒れ度（発走前・1番人気オッズ）MID 83R PFS 71.3% 的中赤字 13/29／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 68R PFS 53.0% 的中赤字 16/26／UNKNOWN 3R PFS 152.7% 的中赤字 1/2／市場ミラーとの差 157R：実績 62.1% − ミラー 45.4% = Δ 16.8pt（95%区間 -8.4〜43.6、最高1R除き 10.4pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 351,200円（36.6%）／保護層の資金比率 0.0（160R）／組だけ的中（三連単は外れ）49R・着順まで的中 30R／的中 91R のうち的中赤字 76R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 50.3%（同じ160Rの実績 41.8%）／券種別 EXACTA 2421点 PFS 48.8%／TRIFECTA 4119点 PFS 25.9%／TRIO 3060点 PFS 57.8%／荒れ度（発走前・1番人気オッズ）MID 83R PFS 46.8% 的中赤字 37/45／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 68R PFS 38.7% 的中赤字 34/41／UNKNOWN 3R PFS 21.7% 的中赤字 3/3／市場ミラーとの差 157R：実績 42.2% − ミラー 71.4% = Δ -29.2pt（95%区間 -58.6〜-2.4、最高1R除き -34.5pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、55R×3券種）：購入 21／予算で削除 0／予想で除外 47／未生成・券種なし 97／役割馬の行き先 {'PURCHASED': 165}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、55R×3券種）：購入 71／予算で削除 20／予想で除外 46／未生成・券種なし 28／役割馬の行き先 {'PURCHASED': 407, 'BUDGET_COMPRESSED': 189}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 21R／W外 34R、2着が P2 役割 4R）：STATIC 4/21（平均3.76位）／STYLE_COND 6/21（平均3.57位） 救済2・喪失0／MARKET_COND 5/19（平均3.05位） 救済3・喪失1
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 38R／W外 17R、2着が P2 役割 31R）：STATIC 32/38（平均3.82位）／STYLE_COND 32/38（平均3.68位） 救済0・喪失0／MARKET_COND 34/36（平均2.86位） 救済4・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 160 | 793,800 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 143 | 524,540 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 72 | 390,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 397 | 1,620,840 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

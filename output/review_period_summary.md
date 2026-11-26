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

- 反省済みRace 123／PAPER PFS 56.8%／正式推薦 PFS 40.3%
- 第一失敗：{'PREDICTION_ROLE_P2': 21, 'CAPITAL_EFFICIENCY': 44, 'PREDICTION_ROLE_W': 49, 'NONE': 9}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 12 | 18.9 | 81.4 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 5, 'NONE': 1} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 25 | 31.7 | 34.0 | {'PREDICTION_ROLE_W': 11, 'CAPITAL_EFFICIENCY': 7, 'NONE': 3, 'PREDICTION_ROLE_P2': 4} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 21 | 99.9 | 50.4 | {'PREDICTION_ROLE_W': 11, 'NONE': 1, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 7} |
| URW | 30 | 77.8 | 34.0 | {'CAPITAL_EFFICIENCY': 13, 'PREDICTION_ROLE_W': 11, 'NONE': 2, 'PREDICTION_ROLE_P2': 4} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 123 | 30.1% | 65.0% | 30.1% | 10.6% | 10.6% | 5.7% | 22.8% | 1.49 |
| 正式推薦 | 123 | 30.1% | 60.2% | 60.2% | 74.0% | 100.0% | 60.2% | 41.5% | 1.46 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中30.1%（無作為9.4%、差+20.7）／P2 平均1.0頭 的中10.6%（無作為9.4%、差+1.1）／P3 平均1.0頭 的中10.6%（無作為9.4%、差+1.1）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中60.2%（無作為28.3%、差+31.9）／P2 平均6.0頭 的中74.0%（無作為56.6%、差+17.4）／P3 平均10.84頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.86/40（選択性補正込み）・能力順位 13.75/20（123R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.94/40（選択性補正込み）・能力順位 13.29/20（123R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 6,000円（6.1%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）30R・着順まで的中 1R／的中 42R のうち的中赤字 20R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 54.3%（同じ123Rの実績 56.8%）／券種別 EXACTA 46点 PFS 5.9%／TRIFECTA 80点 PFS 7.4%／TRIO 633点 PFS 54.1%／WIDE 210点 PFS 95.5%／WIN 8点 PFS 43.8%／荒れ度（発走前・1番人気オッズ）MID 60R PFS 51.9% 的中赤字 10/20／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 55R PFS 55.6% 的中赤字 10/19／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 121R：実績 54.0% − ミラー 43.4% = Δ 10.5pt（95%区間 -13.5〜38.0、最高1R除き 5.0pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 282,300円（38.3%）／保護層の資金比率 0.0（123R）／組だけ的中（三連単は外れ）37R・着順まで的中 19R／的中 66R のうち的中赤字 55R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 49.6%（同じ123Rの実績 40.3%）／券種別 EXACTA 1845点 PFS 47.7%／TRIFECTA 3075点 PFS 22.8%／TRIO 2460点 PFS 56.6%／荒れ度（発走前・1番人気オッズ）MID 60R PFS 45.7% 的中赤字 22/28／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 55R PFS 37.5% 的中赤字 29/34／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 121R：実績 40.6% − ミラー 73.9% = Δ -33.2pt（95%区間 -66.2〜-1.6、最高1R除き -40.1pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、18R×3券種）：購入 6／予算で削除 0／予想で除外 16／未生成・券種なし 32／役割馬の行き先 {'PURCHASED': 54}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、18R×3券種）：購入 23／予算で削除 8／予想で除外 14／未生成・券種なし 9／役割馬の行き先 {'PURCHASED': 132, 'BUDGET_COMPRESSED': 68}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 8R／W外 10R、2着が P2 役割 0R）：STATIC 0/8（平均4.5位）／STYLE_COND 1/8（平均4.25位） 救済1・喪失0／MARKET_COND 0/7（平均4.14位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 13R／W外 5R、2着が P2 役割 11R）：STATIC 11/13（平均3.46位）／STYLE_COND 11/13（平均3.23位） 救済0・喪失0／MARKET_COND 11/12（平均2.58位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 55 | 199,180 | RECURRING |
| P1:ROLE_W_MISS | P1 | 49 | 259,380 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 21 | 126,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 123 | 541,180 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 360／PAPER PFS 59.0%／正式推薦 PFS 74.4%
- 第一失敗：{'NONE': 43, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 98, 'PREDICTION_ROLE_W': 124, 'PREDICTION_ROLE_P2': 58, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 36 | 75.7 | 62.2 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 9, 'PREDICTION_ROLE_W': 9, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 25 | 31.7 | 34.0 | {'PREDICTION_ROLE_W': 11, 'CAPITAL_EFFICIENCY': 7, 'NONE': 3, 'PREDICTION_ROLE_P2': 4} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 57 | 52.8 | 54.5 | {'PREDICTION_ROLE_W': 27, 'CAPITAL_EFFICIENCY': 17, 'PREDICTION_ROLE_P2': 8, 'NONE': 5} |
| URW | 30 | 77.8 | 34.0 | {'CAPITAL_EFFICIENCY': 13, 'PREDICTION_ROLE_W': 11, 'NONE': 2, 'PREDICTION_ROLE_P2': 4} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 360 | 32.5% | 67.8% | 32.5% | 14.4% | 12.8% | 9.2% | 23.3% | 1.54 |
| 正式推薦 | 322 | 32.0% | 61.5% | 61.5% | 72.7% | 100.0% | 61.5% | 34.5% | 1.43 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中32.9%（無作為9.6%、差+23.4）／P2 平均1.0頭 的中13.9%（無作為9.6%、差+4.3）／P3 平均1.0頭 的中12.3%（無作為9.6%、差+2.7）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.7%（無作為28.6%、差+35.1）／P2 平均6.0頭 的中72.7%（無作為57.2%、差+15.4）／P3 平均10.76頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.42/40（選択性補正込み）・能力順位 13.84/20（180R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.25/40（選択性補正込み）・能力順位 13.42/20（173R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 6,000円（6.1%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）30R・着順まで的中 1R／的中 42R のうち的中赤字 20R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 54.3%（同じ123Rの実績 56.8%）／券種別 EXACTA 46点 PFS 5.9%／TRIFECTA 80点 PFS 7.4%／TRIO 633点 PFS 54.1%／WIDE 210点 PFS 95.5%／WIN 8点 PFS 43.8%／荒れ度（発走前・1番人気オッズ）MID 60R PFS 51.9% 的中赤字 10/20／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 55R PFS 55.6% 的中赤字 10/19／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 121R：実績 54.0% − ミラー 43.4% = Δ 10.5pt（95%区間 -13.5〜38.0、最高1R除き 5.0pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 282,300円（38.3%）／保護層の資金比率 0.0（123R）／組だけ的中（三連単は外れ）37R・着順まで的中 19R／的中 66R のうち的中赤字 55R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 49.6%（同じ123Rの実績 40.3%）／券種別 EXACTA 1845点 PFS 47.7%／TRIFECTA 3075点 PFS 22.8%／TRIO 2460点 PFS 56.6%／荒れ度（発走前・1番人気オッズ）MID 60R PFS 45.7% 的中赤字 22/28／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 55R PFS 37.5% 的中赤字 29/34／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 121R：実績 40.6% − ミラー 73.9% = Δ -33.2pt（95%区間 -66.2〜-1.6、最高1R除き -40.1pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、18R×3券種）：購入 6／予算で削除 0／予想で除外 16／未生成・券種なし 32／役割馬の行き先 {'PURCHASED': 54}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、18R×3券種）：購入 23／予算で削除 8／予想で除外 14／未生成・券種なし 9／役割馬の行き先 {'PURCHASED': 132, 'BUDGET_COMPRESSED': 68}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 8R／W外 10R、2着が P2 役割 0R）：STATIC 0/8（平均4.5位）／STYLE_COND 1/8（平均4.25位） 救済1・喪失0／MARKET_COND 0/7（平均4.14位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 13R／W外 5R、2着が P2 役割 11R）：STATIC 11/13（平均3.46位）／STYLE_COND 11/13（平均3.23位） 救済0・喪失0／MARKET_COND 11/12（平均2.58位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 148 | 733,310 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 122 | 449,440 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 67 | 360,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 360 | 1,473,740 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

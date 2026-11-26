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

- 反省済みRace 111／PAPER PFS 57.9%／正式推薦 PFS 40.5%
- 第一失敗：{'PREDICTION_ROLE_P2': 21, 'CAPITAL_EFFICIENCY': 36, 'PREDICTION_ROLE_W': 45, 'NONE': 9}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 10 | 20.2 | 94.3 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 1} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 24 | 29.8 | 35.4 | {'PREDICTION_ROLE_W': 10, 'CAPITAL_EFFICIENCY': 7, 'NONE': 3, 'PREDICTION_ROLE_P2': 4} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 17 | 115.2 | 50.5 | {'PREDICTION_ROLE_W': 10, 'NONE': 1, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 4} |
| URW | 25 | 80.1 | 31.9 | {'CAPITAL_EFFICIENCY': 9, 'PREDICTION_ROLE_W': 10, 'NONE': 2, 'PREDICTION_ROLE_P2': 4} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 111 | 30.6% | 64.9% | 30.6% | 10.8% | 9.0% | 6.3% | 21.6% | 1.47 |
| 正式推薦 | 111 | 29.7% | 59.5% | 59.5% | 72.1% | 100.0% | 59.5% | 40.5% | 1.45 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中30.6%（無作為9.5%、差+21.2）／P2 平均1.0頭 的中10.8%（無作為9.5%、差+1.4）／P3 平均1.0頭 的中9.0%（無作為9.5%、差-0.4）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中59.5%（無作為28.4%、差+31.1）／P2 平均6.0頭 的中72.1%（無作為56.8%、差+15.3）／P3 平均10.81頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.63/40（選択性補正込み）・能力順位 13.68/20（111R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.72/40（選択性補正込み）・能力順位 13.19/20（111R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 5,400円（6.2%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）25R・着順まで的中 1R／的中 37R のうち的中赤字 18R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 57.3%（同じ111Rの実績 57.9%）／券種別 EXACTA 39点 PFS 6.9%／TRIFECTA 72点 PFS 8.2%／TRIO 569点 PFS 55.3%／WIDE 192点 PFS 94.7%／WIN 6点 PFS 58.3%／荒れ度（発走前・1番人気オッズ）MID 56R PFS 55.9% 的中赤字 10/20／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 47R PFS 53.3% 的中赤字 8/14／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 109R：実績 54.8% − ミラー 43.4% = Δ 11.4pt（95%区間 -15.6〜39.8、最高1R除き 5.2pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 254,600円（38.2%）／保護層の資金比率 0.0（111R）／組だけ的中（三連単は外れ）35R・着順まで的中 15R／的中 58R のうち的中赤字 47R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 52.0%（同じ111Rの実績 40.5%）／券種別 EXACTA 1665点 PFS 48.4%／TRIFECTA 2775点 PFS 21.2%／TRIO 2220点 PFS 58.8%／荒れ度（発走前・1番人気オッズ）MID 56R PFS 47.2% 的中赤字 20/26／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 47R PFS 36.4% 的中赤字 23/28／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 109R：実績 40.9% − ミラー 77.1% = Δ -36.2pt（95%区間 -72.0〜-0.8、最高1R除き -43.9pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、6R×3券種）：購入 2／予算で削除 0／予想で除外 4／未生成・券種なし 12／役割馬の行き先 {'PURCHASED': 18}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、6R×3券種）：購入 5／予算で削除 4／予想で除外 6／未生成・券種なし 3／役割馬の行き先 {'PURCHASED': 43, 'BUDGET_COMPRESSED': 24}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 5R／W外 1R、2着が P2 役割 0R）：STATIC 0/5（平均4.6位）／STYLE_COND 1/5（平均4.2位） 救済1・喪失0／MARKET_COND 0/4（平均5.0位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 5R／W外 1R、2着が P2 役割 3R）：STATIC 3/5（平均5.4位）／STYLE_COND 3/5（平均5.0位） 救済0・喪失0／MARKET_COND 3/4（平均4.0位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 47 | 178,510 | RECURRING |
| P1:ROLE_W_MISS | P1 | 45 | 235,380 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 21 | 126,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 111 | 496,510 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 348／PAPER PFS 59.5%／正式推薦 PFS 75.8%
- 第一失敗：{'NONE': 43, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 90, 'PREDICTION_ROLE_W': 120, 'PREDICTION_ROLE_P2': 58, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 34 | 79.4 | 66.2 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 24 | 29.8 | 35.4 | {'PREDICTION_ROLE_W': 10, 'CAPITAL_EFFICIENCY': 7, 'NONE': 3, 'PREDICTION_ROLE_P2': 4} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 53 | 54.3 | 54.8 | {'PREDICTION_ROLE_W': 26, 'CAPITAL_EFFICIENCY': 14, 'PREDICTION_ROLE_P2': 8, 'NONE': 5} |
| URW | 25 | 80.1 | 31.9 | {'CAPITAL_EFFICIENCY': 9, 'PREDICTION_ROLE_W': 10, 'NONE': 2, 'PREDICTION_ROLE_P2': 4} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 348 | 32.8% | 67.8% | 32.8% | 14.7% | 12.4% | 9.5% | 23.0% | 1.53 |
| 正式推薦 | 310 | 31.9% | 61.3% | 61.3% | 71.9% | 100.0% | 61.3% | 33.9% | 1.42 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中33.3%（無作為9.6%、差+23.7）／P2 平均1.0頭 的中14.2%（無作為9.6%、差+4.6）／P3 平均1.0頭 的中11.7%（無作為9.6%、差+2.1）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.5%（無作為28.7%、差+34.9）／P2 平均6.0頭 的中71.7%（無作為57.3%、差+14.3）／P3 平均10.74頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.31/40（選択性補正込み）・能力順位 13.8/20（168R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.12/40（選択性補正込み）・能力順位 13.36/20（161R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 5,400円（6.2%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）25R・着順まで的中 1R／的中 37R のうち的中赤字 18R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 57.3%（同じ111Rの実績 57.9%）／券種別 EXACTA 39点 PFS 6.9%／TRIFECTA 72点 PFS 8.2%／TRIO 569点 PFS 55.3%／WIDE 192点 PFS 94.7%／WIN 6点 PFS 58.3%／荒れ度（発走前・1番人気オッズ）MID 56R PFS 55.9% 的中赤字 10/20／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 47R PFS 53.3% 的中赤字 8/14／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 109R：実績 54.8% − ミラー 43.4% = Δ 11.4pt（95%区間 -15.6〜39.8、最高1R除き 5.2pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 254,600円（38.2%）／保護層の資金比率 0.0（111R）／組だけ的中（三連単は外れ）35R・着順まで的中 15R／的中 58R のうち的中赤字 47R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 52.0%（同じ111Rの実績 40.5%）／券種別 EXACTA 1665点 PFS 48.4%／TRIFECTA 2775点 PFS 21.2%／TRIO 2220点 PFS 58.8%／荒れ度（発走前・1番人気オッズ）MID 56R PFS 47.2% 的中赤字 20/26／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 47R PFS 36.4% 的中赤字 23/28／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 109R：実績 40.9% − ミラー 77.1% = Δ -36.2pt（95%区間 -72.0〜-0.8、最高1R除き -43.9pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、6R×3券種）：購入 2／予算で削除 0／予想で除外 4／未生成・券種なし 12／役割馬の行き先 {'PURCHASED': 18}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、6R×3券種）：購入 5／予算で削除 4／予想で除外 6／未生成・券種なし 3／役割馬の行き先 {'PURCHASED': 43, 'BUDGET_COMPRESSED': 24}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 5R／W外 1R、2着が P2 役割 0R）：STATIC 0/5（平均4.6位）／STYLE_COND 1/5（平均4.2位） 救済1・喪失0／MARKET_COND 0/4（平均5.0位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 5R／W外 1R、2着が P2 役割 3R）：STATIC 3/5（平均5.4位）／STYLE_COND 3/5（平均5.0位） 救済0・喪失0／MARKET_COND 3/4（平均4.0位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 144 | 709,310 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 114 | 428,770 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 67 | 360,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 348 | 1,429,070 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

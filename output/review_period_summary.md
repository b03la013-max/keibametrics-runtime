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

- 反省済みRace 110／PAPER PFS 58.4%／正式推薦 PFS 40.9%
- 第一失敗：{'PREDICTION_ROLE_P2': 20, 'CAPITAL_EFFICIENCY': 36, 'PREDICTION_ROLE_W': 45, 'NONE': 9}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 10 | 20.2 | 94.3 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 1} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 24 | 29.8 | 35.4 | {'PREDICTION_ROLE_W': 10, 'CAPITAL_EFFICIENCY': 7, 'NONE': 3, 'PREDICTION_ROLE_P2': 4} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 16 | 120.5 | 53.7 | {'PREDICTION_ROLE_W': 10, 'NONE': 1, 'PREDICTION_ROLE_P2': 1, 'CAPITAL_EFFICIENCY': 4} |
| URW | 25 | 80.1 | 31.9 | {'CAPITAL_EFFICIENCY': 9, 'PREDICTION_ROLE_W': 10, 'NONE': 2, 'PREDICTION_ROLE_P2': 4} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 110 | 30.0% | 64.5% | 30.0% | 10.9% | 9.1% | 6.4% | 21.8% | 1.46 |
| 正式推薦 | 110 | 30.0% | 59.1% | 59.1% | 72.7% | 100.0% | 59.1% | 40.9% | 1.45 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中30.0%（無作為9.5%、差+20.5）／P2 平均1.0頭 的中10.9%（無作為9.5%、差+1.4）／P3 平均1.0頭 的中9.1%（無作為9.5%、差-0.4）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中59.1%（無作為28.4%、差+30.7）／P2 平均6.0頭 的中72.7%（無作為56.8%、差+15.9）／P3 平均10.8頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.55/40（選択性補正込み）・能力順位 13.65/20（110R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.7/40（選択性補正込み）・能力順位 13.2/20（110R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 5,400円（6.2%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）25R・着順まで的中 1R／的中 37R のうち的中赤字 18R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 57.4%（同じ110Rの実績 58.4%）／券種別 EXACTA 39点 PFS 6.9%／TRIFECTA 72点 PFS 8.2%／TRIO 564点 PFS 55.8%／WIDE 190点 PFS 95.7%／WIN 6点 PFS 58.3%／荒れ度（発走前・1番人気オッズ）MID 55R PFS 56.9% 的中赤字 10/20／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 47R PFS 53.3% 的中赤字 8/14／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 108R：実績 55.2% − ミラー 43.8% = Δ 11.5pt（95%区間 -14.7〜39.5、最高1R除き 5.2pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 252,400円（38.2%）／保護層の資金比率 0.0（110R）／組だけ的中（三連単は外れ）35R・着順まで的中 15R／的中 58R のうち的中赤字 47R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 52.1%（同じ110Rの実績 40.9%）／券種別 EXACTA 1650点 PFS 48.9%／TRIFECTA 2750点 PFS 21.4%／TRIO 2200点 PFS 59.3%／荒れ度（発走前・1番人気オッズ）MID 55R PFS 48.0% 的中赤字 20/26／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 47R PFS 36.4% 的中赤字 23/28／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 108R：実績 41.3% − ミラー 77.8% = Δ -36.5pt（95%区間 -75.2〜-0.5、最高1R除き -44.3pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、5R×3券種）：購入 2／予算で削除 0／予想で除外 3／未生成・券種なし 10／役割馬の行き先 {'PURCHASED': 15}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、5R×3券種）：購入 5／予算で削除 4／予想で除外 4／未生成・券種なし 2／役割馬の行き先 {'PURCHASED': 35, 'BUDGET_COMPRESSED': 20}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 4R／W外 1R、2着が P2 役割 0R）：STATIC 0/4（平均5.25位）／STYLE_COND 0/4（平均5.0位） 救済0・喪失0／MARKET_COND 0/3（平均4.33位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 4R／W外 1R、2着が P2 役割 3R）：STATIC 3/4（平均4.75位）／STYLE_COND 3/4（平均4.5位） 救済0・喪失0／MARKET_COND 3/3（平均3.0位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 47 | 178,510 | RECURRING |
| P1:ROLE_W_MISS | P1 | 45 | 235,380 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 20 | 120,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 110 | 490,510 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 347／PAPER PFS 59.6%／正式推薦 PFS 76.0%
- 第一失敗：{'NONE': 43, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 90, 'PREDICTION_ROLE_W': 120, 'PREDICTION_ROLE_P2': 57, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 34 | 79.4 | 66.2 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 24 | 29.8 | 35.4 | {'PREDICTION_ROLE_W': 10, 'CAPITAL_EFFICIENCY': 7, 'NONE': 3, 'PREDICTION_ROLE_P2': 4} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 52 | 55.1 | 55.9 | {'PREDICTION_ROLE_W': 26, 'CAPITAL_EFFICIENCY': 14, 'PREDICTION_ROLE_P2': 7, 'NONE': 5} |
| URW | 25 | 80.1 | 31.9 | {'CAPITAL_EFFICIENCY': 9, 'PREDICTION_ROLE_W': 10, 'NONE': 2, 'PREDICTION_ROLE_P2': 4} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 347 | 32.6% | 67.7% | 32.6% | 14.7% | 12.4% | 9.5% | 23.1% | 1.53 |
| 正式推薦 | 309 | 32.0% | 61.2% | 61.2% | 72.2% | 100.0% | 61.2% | 34.0% | 1.42 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中33.1%（無作為9.6%、差+23.5）／P2 平均1.0頭 的中14.2%（無作為9.6%、差+4.6）／P3 平均1.0頭 的中11.7%（無作為9.6%、差+2.1）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.4%（無作為28.7%、差+34.7）／P2 平均6.0頭 的中72.0%（無作為57.4%、差+14.6）／P3 平均10.73頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.26/40（選択性補正込み）・能力順位 13.78/20（167R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.11/40（選択性補正込み）・能力順位 13.36/20（160R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 5,400円（6.2%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）25R・着順まで的中 1R／的中 37R のうち的中赤字 18R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 57.4%（同じ110Rの実績 58.4%）／券種別 EXACTA 39点 PFS 6.9%／TRIFECTA 72点 PFS 8.2%／TRIO 564点 PFS 55.8%／WIDE 190点 PFS 95.7%／WIN 6点 PFS 58.3%／荒れ度（発走前・1番人気オッズ）MID 55R PFS 56.9% 的中赤字 10/20／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 47R PFS 53.3% 的中赤字 8/14／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 108R：実績 55.2% − ミラー 43.8% = Δ 11.5pt（95%区間 -14.7〜39.5、最高1R除き 5.2pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 252,400円（38.2%）／保護層の資金比率 0.0（110R）／組だけ的中（三連単は外れ）35R・着順まで的中 15R／的中 58R のうち的中赤字 47R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 52.1%（同じ110Rの実績 40.9%）／券種別 EXACTA 1650点 PFS 48.9%／TRIFECTA 2750点 PFS 21.4%／TRIO 2200点 PFS 59.3%／荒れ度（発走前・1番人気オッズ）MID 55R PFS 48.0% 的中赤字 20/26／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 47R PFS 36.4% 的中赤字 23/28／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 108R：実績 41.3% − ミラー 77.8% = Δ -36.5pt（95%区間 -75.2〜-0.5、最高1R除き -44.3pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、5R×3券種）：購入 2／予算で削除 0／予想で除外 3／未生成・券種なし 10／役割馬の行き先 {'PURCHASED': 15}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、5R×3券種）：購入 5／予算で削除 4／予想で除外 4／未生成・券種なし 2／役割馬の行き先 {'PURCHASED': 35, 'BUDGET_COMPRESSED': 20}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 4R／W外 1R、2着が P2 役割 0R）：STATIC 0/4（平均5.25位）／STYLE_COND 0/4（平均5.0位） 救済0・喪失0／MARKET_COND 0/3（平均4.33位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 4R／W外 1R、2着が P2 役割 3R）：STATIC 3/4（平均4.75位）／STYLE_COND 3/4（平均4.5位） 救済0・喪失0／MARKET_COND 3/3（平均3.0位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 144 | 709,310 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 114 | 428,770 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 66 | 354,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 347 | 1,423,070 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

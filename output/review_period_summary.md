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

- 反省済みRace 119／PAPER PFS 54.6%／正式推薦 PFS 39.9%
- 第一失敗：{'PREDICTION_ROLE_P2': 21, 'CAPITAL_EFFICIENCY': 41, 'PREDICTION_ROLE_W': 48, 'NONE': 9}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 11 | 18.4 | 85.8 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 5, 'NONE': 1} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 24 | 29.8 | 35.4 | {'PREDICTION_ROLE_W': 10, 'CAPITAL_EFFICIENCY': 7, 'NONE': 3, 'PREDICTION_ROLE_P2': 4} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 20 | 97.0 | 49.0 | {'PREDICTION_ROLE_W': 11, 'NONE': 1, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 6} |
| URW | 29 | 72.2 | 31.8 | {'CAPITAL_EFFICIENCY': 12, 'PREDICTION_ROLE_W': 11, 'NONE': 2, 'PREDICTION_ROLE_P2': 4} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 119 | 29.4% | 64.7% | 29.4% | 10.9% | 9.2% | 5.9% | 21.0% | 1.47 |
| 正式推薦 | 119 | 29.4% | 59.7% | 59.7% | 73.1% | 100.0% | 59.7% | 40.3% | 1.45 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中29.4%（無作為9.4%、差+20.0）／P2 平均1.0頭 的中10.9%（無作為9.4%、差+1.5）／P3 平均1.0頭 的中9.2%（無作為9.4%、差-0.2）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中59.7%（無作為28.3%、差+31.4）／P2 平均6.0頭 的中73.1%（無作為56.5%、差+16.6）／P3 平均10.85頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.63/40（選択性補正込み）・能力順位 13.66/20（119R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.83/40（選択性補正込み）・能力順位 13.23/20（119R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 6,000円（6.3%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）27R・着順まで的中 1R／的中 38R のうち的中赤字 18R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 55.3%（同じ119Rの実績 54.6%）／券種別 EXACTA 44点 PFS 6.1%／TRIFECTA 80点 PFS 7.4%／TRIO 613点 PFS 52.6%／WIDE 204点 PFS 89.8%／WIN 7点 PFS 50.0%／荒れ度（発走前・1番人気オッズ）MID 60R PFS 51.9% 的中赤字 10/20／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 51R PFS 50.6% 的中赤字 8/15／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 117R：実績 51.6% − ミラー 42.8% = Δ 8.8pt（95%区間 -16.2〜35.2、最高1R除き 3.1pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 272,900円（38.2%）／保護層の資金比率 0.0（119R）／組だけ的中（三連単は外れ）36R・着順まで的中 17R／的中 63R のうち的中赤字 52R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 51.0%（同じ119Rの実績 39.9%）／券種別 EXACTA 1785点 PFS 48.1%／TRIFECTA 2975点 PFS 22.3%／TRIO 2380点 PFS 55.7%／荒れ度（発走前・1番人気オッズ）MID 60R PFS 45.7% 的中赤字 22/28／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 51R PFS 36.3% 的中赤字 26/31／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 117R：実績 40.2% − ミラー 75.5% = Δ -35.2pt（95%区間 -69.2〜-2.0、最高1R除き -42.4pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、14R×3券種）：購入 3／予算で削除 0／予想で除外 14／未生成・券種なし 25／役割馬の行き先 {'PURCHASED': 42}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、14R×3券種）：購入 15／予算で削除 7／予想で除外 12／未生成・券種なし 8／役割馬の行き先 {'PURCHASED': 103, 'BUDGET_COMPRESSED': 55}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 6R／W外 8R、2着が P2 役割 0R）：STATIC 0/6（平均5.17位）／STYLE_COND 1/6（平均4.67位） 救済1・喪失0／MARKET_COND 0/5（平均4.4位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 10R／W外 4R、2着が P2 役割 8R）：STATIC 8/10（平均3.9位）／STYLE_COND 8/10（平均3.6位） 救済0・喪失0／MARKET_COND 8/9（平均2.44位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 52 | 193,840 | RECURRING |
| P1:ROLE_W_MISS | P1 | 48 | 253,380 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 21 | 126,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 119 | 529,840 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 356／PAPER PFS 58.3%／正式推薦 PFS 74.6%
- 第一失敗：{'NONE': 43, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 95, 'PREDICTION_ROLE_W': 123, 'PREDICTION_ROLE_P2': 58, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 35 | 77.1 | 63.4 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 9, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 24 | 29.8 | 35.4 | {'PREDICTION_ROLE_W': 10, 'CAPITAL_EFFICIENCY': 7, 'NONE': 3, 'PREDICTION_ROLE_P2': 4} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 56 | 51.1 | 54.1 | {'PREDICTION_ROLE_W': 27, 'CAPITAL_EFFICIENCY': 16, 'PREDICTION_ROLE_P2': 8, 'NONE': 5} |
| URW | 29 | 72.2 | 31.8 | {'CAPITAL_EFFICIENCY': 12, 'PREDICTION_ROLE_W': 11, 'NONE': 2, 'PREDICTION_ROLE_P2': 4} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 356 | 32.3% | 67.7% | 32.3% | 14.6% | 12.4% | 9.3% | 22.8% | 1.53 |
| 正式推薦 | 318 | 31.8% | 61.3% | 61.3% | 72.3% | 100.0% | 61.3% | 34.0% | 1.42 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中32.7%（無作為9.6%、差+23.1）／P2 平均1.0頭 的中14.1%（無作為9.6%、差+4.6）／P3 平均1.0頭 的中11.7%（無作為9.6%、差+2.1）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.5%（無作為28.6%、差+34.9）／P2 平均6.0頭 的中72.2%（無作為57.2%、差+15.0）／P3 平均10.76頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.28/40（選択性補正込み）・能力順位 13.78/20（176R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.18/40（選択性補正込み）・能力順位 13.38/20（169R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 6,000円（6.3%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）27R・着順まで的中 1R／的中 38R のうち的中赤字 18R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 55.3%（同じ119Rの実績 54.6%）／券種別 EXACTA 44点 PFS 6.1%／TRIFECTA 80点 PFS 7.4%／TRIO 613点 PFS 52.6%／WIDE 204点 PFS 89.8%／WIN 7点 PFS 50.0%／荒れ度（発走前・1番人気オッズ）MID 60R PFS 51.9% 的中赤字 10/20／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 51R PFS 50.6% 的中赤字 8/15／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 117R：実績 51.6% − ミラー 42.8% = Δ 8.8pt（95%区間 -16.2〜35.2、最高1R除き 3.1pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 272,900円（38.2%）／保護層の資金比率 0.0（119R）／組だけ的中（三連単は外れ）36R・着順まで的中 17R／的中 63R のうち的中赤字 52R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 51.0%（同じ119Rの実績 39.9%）／券種別 EXACTA 1785点 PFS 48.1%／TRIFECTA 2975点 PFS 22.3%／TRIO 2380点 PFS 55.7%／荒れ度（発走前・1番人気オッズ）MID 60R PFS 45.7% 的中赤字 22/28／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 51R PFS 36.3% 的中赤字 26/31／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 117R：実績 40.2% − ミラー 75.5% = Δ -35.2pt（95%区間 -69.2〜-2.0、最高1R除き -42.4pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、14R×3券種）：購入 3／予算で削除 0／予想で除外 14／未生成・券種なし 25／役割馬の行き先 {'PURCHASED': 42}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、14R×3券種）：購入 15／予算で削除 7／予想で除外 12／未生成・券種なし 8／役割馬の行き先 {'PURCHASED': 103, 'BUDGET_COMPRESSED': 55}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 6R／W外 8R、2着が P2 役割 0R）：STATIC 0/6（平均5.17位）／STYLE_COND 1/6（平均4.67位） 救済1・喪失0／MARKET_COND 0/5（平均4.4位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 10R／W外 4R、2着が P2 役割 8R）：STATIC 8/10（平均3.9位）／STYLE_COND 8/10（平均3.6位） 救済0・喪失0／MARKET_COND 8/9（平均2.44位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 147 | 727,310 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 119 | 444,100 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 67 | 360,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 356 | 1,462,400 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

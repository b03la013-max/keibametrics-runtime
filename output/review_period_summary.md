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

- 反省済みRace 115／PAPER PFS 56.5%／正式推薦 PFS 40.1%
- 第一失敗：{'PREDICTION_ROLE_P2': 21, 'CAPITAL_EFFICIENCY': 39, 'PREDICTION_ROLE_W': 46, 'NONE': 9}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 10 | 20.2 | 94.3 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 1} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 24 | 29.8 | 35.4 | {'PREDICTION_ROLE_W': 10, 'CAPITAL_EFFICIENCY': 7, 'NONE': 3, 'PREDICTION_ROLE_P2': 4} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 18 | 104.7 | 52.4 | {'PREDICTION_ROLE_W': 10, 'NONE': 1, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 5} |
| URW | 28 | 75.4 | 29.6 | {'CAPITAL_EFFICIENCY': 11, 'PREDICTION_ROLE_W': 11, 'NONE': 2, 'PREDICTION_ROLE_P2': 4} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 115 | 30.4% | 66.1% | 30.4% | 10.4% | 9.6% | 6.1% | 21.7% | 1.49 |
| 正式推薦 | 115 | 30.4% | 60.0% | 60.0% | 73.0% | 100.0% | 60.0% | 40.9% | 1.46 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中30.4%（無作為9.4%、差+21.0）／P2 平均1.0頭 的中10.4%（無作為9.4%、差+1.0）／P3 平均1.0頭 的中9.6%（無作為9.4%、差+0.1）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中60.0%（無作為28.3%、差+31.7）／P2 平均6.0頭 的中73.0%（無作為56.5%、差+16.5）／P3 平均10.85頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.78/40（選択性補正込み）・能力順位 13.74/20（115R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.88/40（選択性補正込み）・能力順位 13.28/20（115R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 6,000円（6.5%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）27R・着順まで的中 1R／的中 38R のうち的中赤字 18R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 55.9%（同じ115Rの実績 56.5%）／券種別 EXACTA 42点 PFS 6.4%／TRIFECTA 80点 PFS 7.4%／TRIO 591点 PFS 54.6%／WIDE 198点 PFS 92.5%／WIN 6点 PFS 58.3%／荒れ度（発走前・1番人気オッズ）MID 58R PFS 53.9% 的中赤字 10/20／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 49R PFS 52.5% 的中赤字 8/15／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 113R：実績 53.4% − ミラー 42.5% = Δ 10.9pt（95%区間 -13.9〜37.4、最高1R除き 5.0pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 263,700円（38.2%）／保護層の資金比率 0.0（115R）／組だけ的中（三連単は外れ）36R・着順まで的中 16R／的中 61R のうち的中赤字 50R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 50.9%（同じ115Rの実績 40.1%）／券種別 EXACTA 1725点 PFS 48.0%／TRIFECTA 2875点 PFS 21.8%／TRIO 2300点 PFS 57.2%／荒れ度（発走前・1番人気オッズ）MID 58R PFS 45.7% 的中赤字 21/27／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 49R PFS 37.0% 的中赤字 25/30／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 113R：実績 40.5% − ミラー 76.0% = Δ -35.5pt（95%区間 -69.9〜-2.0、最高1R除き -43.0pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、10R×3券種）：購入 3／予算で削除 0／予想で除外 9／未生成・券種なし 18／役割馬の行き先 {'PURCHASED': 30}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、10R×3券種）：購入 11／予算で削除 6／予想で除外 8／未生成・券種なし 5／役割馬の行き先 {'PURCHASED': 73, 'BUDGET_COMPRESSED': 42}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 6R／W外 4R、2着が P2 役割 0R）：STATIC 0/6（平均5.17位）／STYLE_COND 1/6（平均4.67位） 救済1・喪失0／MARKET_COND 0/5（平均4.4位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 8R／W外 2R、2着が P2 役割 6R）：STATIC 6/8（平均4.12位）／STYLE_COND 6/8（平均3.75位） 救済0・喪失0／MARKET_COND 6/7（平均2.86位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 50 | 189,540 | RECURRING |
| P1:ROLE_W_MISS | P1 | 46 | 241,380 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 21 | 126,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 115 | 513,540 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 352／PAPER PFS 59.0%／正式推薦 PFS 75.2%
- 第一失敗：{'NONE': 43, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 93, 'PREDICTION_ROLE_W': 121, 'PREDICTION_ROLE_P2': 58, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 34 | 79.4 | 66.2 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 24 | 29.8 | 35.4 | {'PREDICTION_ROLE_W': 10, 'CAPITAL_EFFICIENCY': 7, 'NONE': 3, 'PREDICTION_ROLE_P2': 4} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 54 | 52.5 | 55.4 | {'PREDICTION_ROLE_W': 26, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_P2': 8, 'NONE': 5} |
| URW | 28 | 75.4 | 29.6 | {'CAPITAL_EFFICIENCY': 11, 'PREDICTION_ROLE_W': 11, 'NONE': 2, 'PREDICTION_ROLE_P2': 4} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 352 | 32.7% | 68.2% | 32.7% | 14.5% | 12.5% | 9.4% | 23.0% | 1.54 |
| 正式推薦 | 314 | 32.2% | 61.5% | 61.5% | 72.3% | 100.0% | 61.5% | 34.1% | 1.42 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中33.2%（無作為9.6%、差+23.6）／P2 平均1.0頭 的中13.9%（無作為9.6%、差+4.4）／P3 平均1.0頭 的中11.9%（無作為9.6%、差+2.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.7%（無作為28.6%、差+35.1）／P2 平均6.0頭 的中72.2%（無作為57.2%、差+14.9）／P3 平均10.76頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.4/40（選択性補正込み）・能力順位 13.84/20（172R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.23/40（選択性補正込み）・能力順位 13.42/20（165R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 6,000円（6.5%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）27R・着順まで的中 1R／的中 38R のうち的中赤字 18R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 55.9%（同じ115Rの実績 56.5%）／券種別 EXACTA 42点 PFS 6.4%／TRIFECTA 80点 PFS 7.4%／TRIO 591点 PFS 54.6%／WIDE 198点 PFS 92.5%／WIN 6点 PFS 58.3%／荒れ度（発走前・1番人気オッズ）MID 58R PFS 53.9% 的中赤字 10/20／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 49R PFS 52.5% 的中赤字 8/15／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 113R：実績 53.4% − ミラー 42.5% = Δ 10.9pt（95%区間 -13.9〜37.4、最高1R除き 5.0pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 263,700円（38.2%）／保護層の資金比率 0.0（115R）／組だけ的中（三連単は外れ）36R・着順まで的中 16R／的中 61R のうち的中赤字 50R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 50.9%（同じ115Rの実績 40.1%）／券種別 EXACTA 1725点 PFS 48.0%／TRIFECTA 2875点 PFS 21.8%／TRIO 2300点 PFS 57.2%／荒れ度（発走前・1番人気オッズ）MID 58R PFS 45.7% 的中赤字 21/27／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 49R PFS 37.0% 的中赤字 25/30／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 113R：実績 40.5% − ミラー 76.0% = Δ -35.5pt（95%区間 -69.9〜-2.0、最高1R除き -43.0pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、10R×3券種）：購入 3／予算で削除 0／予想で除外 9／未生成・券種なし 18／役割馬の行き先 {'PURCHASED': 30}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、10R×3券種）：購入 11／予算で削除 6／予想で除外 8／未生成・券種なし 5／役割馬の行き先 {'PURCHASED': 73, 'BUDGET_COMPRESSED': 42}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 6R／W外 4R、2着が P2 役割 0R）：STATIC 0/6（平均5.17位）／STYLE_COND 1/6（平均4.67位） 救済1・喪失0／MARKET_COND 0/5（平均4.4位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 8R／W外 2R、2着が P2 役割 6R）：STATIC 6/8（平均4.12位）／STYLE_COND 6/8（平均3.75位） 救済0・喪失0／MARKET_COND 6/7（平均2.86位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 145 | 715,310 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 117 | 439,800 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 67 | 360,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 352 | 1,446,100 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

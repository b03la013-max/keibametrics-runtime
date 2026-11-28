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

- 反省済みRace 192／PAPER PFS 62.4%／正式推薦 PFS 41.5%
- 第一失敗：{'PREDICTION_ROLE_P2': 33, 'CAPITAL_EFFICIENCY': 69, 'PREDICTION_ROLE_W': 75, 'NONE': 15}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 22 | 51.6 | 73.2 | {'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 12, 'PREDICTION_ROLE_W': 5, 'NONE': 2} |
| KOC | 1 | 17.1 | 0.0 | {'PREDICTION_ROLE_P2': 1} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 48 | 51.9 | 46.3 | {'PREDICTION_ROLE_W': 20, 'CAPITAL_EFFICIENCY': 14, 'NONE': 6, 'PREDICTION_ROLE_P2': 8} |
| SAG | 13 | 20.5 | 14.8 | {'PREDICTION_ROLE_W': 4, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 4} |
| SON | 36 | 102.8 | 37.8 | {'PREDICTION_ROLE_W': 18, 'NONE': 1, 'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 14} |
| URW | 48 | 65.7 | 35.5 | {'CAPITAL_EFFICIENCY': 16, 'PREDICTION_ROLE_W': 20, 'NONE': 4, 'PREDICTION_ROLE_P2': 8} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 192 | 32.3% | 64.6% | 32.3% | 14.1% | 14.1% | 6.2% | 24.0% | 1.53 |
| 正式推薦 | 192 | 31.8% | 60.9% | 60.9% | 75.0% | 100.0% | 66.1% | 41.7% | 1.49 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中32.3%（無作為9.4%、差+22.9）／P2 平均1.0頭 的中14.1%（無作為9.4%、差+4.7）／P3 平均1.0頭 的中14.1%（無作為9.4%、差+4.7）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中60.9%（無作為28.1%、差+32.9）／P2 平均6.0頭 的中75.0%（無作為56.1%、差+18.9）／P3 平均10.93頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.68/40（選択性補正込み）・能力順位 14.04/20（192R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.29/40（選択性補正込み）・能力順位 13.58/20（192R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 8,400円（5.6%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）47R・着順まで的中 2R／的中 71R のうち的中赤字 35R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 51.8%（同じ192Rの実績 62.4%）／券種別 EXACTA 64点 PFS 18.3%／TRIFECTA 112点 PFS 14.3%／TRIO 990点 PFS 56.3%／WIDE 334点 PFS 105.8%／WIN 11点 PFS 46.4%／荒れ度（発走前・1番人気オッズ）MID 100R PFS 74.0% 的中赤字 13/36／OPEN 7R PFS 49.8% 的中赤字 0/2／SOLID 82R PFS 47.0% 的中赤字 21/31／UNKNOWN 3R PFS 152.7% 的中赤字 1/2／市場ミラーとの差 189R：実績 60.6% − ミラー 56.3% = Δ 4.3pt（95%区間 -19.6〜30.2、最高1R除き -1.1pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 351,200円（30.5%）／保護層の資金比率 0.0（192R）／組だけ的中（三連単は外れ）54R・着順まで的中 39R／的中 106R のうち的中赤字 88R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 47.6%（同じ192Rの実績 41.5%）／券種別 EXACTA 2973点 PFS 47.5%／TRIFECTA 5487点 PFS 29.1%／TRIO 3060点 PFS 57.8%／荒れ度（発走前・1番人気オッズ）MID 100R PFS 46.8% 的中赤字 44/54／OPEN 7R PFS 15.6% 的中赤字 2/2／SOLID 82R PFS 37.8% 的中赤字 39/47／UNKNOWN 3R PFS 21.7% 的中赤字 3/3／市場ミラーとの差 189R：実績 41.8% − ミラー 69.7% = Δ -27.9pt（95%区間 -52.3〜-5.6、最高1R除き -32.3pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、87R×3券種）：購入 26／予算で削除 0／予想で除外 76／未生成・券種なし 159／役割馬の行き先 {'PURCHASED': 261}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、87R×3券種）：購入 95／予算で削除 27／予想で除外 81／未生成・券種なし 58／役割馬の行き先 {'PURCHASED': 655, 'BUDGET_COMPRESSED': 310}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 33R／W外 54R、2着が P2 役割 6R）：STATIC 6/33（平均3.73位）／STYLE_COND 9/33（平均3.58位） 救済3・喪失0／MARKET_COND 7/31（平均2.9位） 救済5・喪失3
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 56R／W外 31R、2着が P2 役割 42R）：STATIC 44/56（平均4.07位）／STYLE_COND 45/56（平均3.95位） 救済1・喪失0／MARKET_COND 51/54（平均2.89位） 救済9・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 88 | 319,670 | RECURRING |
| P1:ROLE_W_MISS | P1 | 75 | 392,370 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 33 | 198,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 192 | 835,670 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 429／PAPER PFS 61.2%／正式推薦 PFS 69.0%
- 第一失敗：{'NONE': 49, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 123, 'PREDICTION_ROLE_W': 150, 'PREDICTION_ROLE_P2': 70, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 46 | 78.5 | 62.5 | {'NONE': 6, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 17, 'PREDICTION_ROLE_W': 9, 'PREDICTION_ROLE_P2': 5, 'EXACT_ORIENTATION': 1} |
| KOC | 24 | 58.7 | 30.9 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 3, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 48 | 51.9 | 46.3 | {'PREDICTION_ROLE_W': 20, 'CAPITAL_EFFICIENCY': 14, 'NONE': 6, 'PREDICTION_ROLE_P2': 8} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 35 | 47.2 | 27.9 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 10, 'PREDICTION_ROLE_W': 9, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 72 | 62.3 | 47.3 | {'PREDICTION_ROLE_W': 34, 'CAPITAL_EFFICIENCY': 24, 'PREDICTION_ROLE_P2': 9, 'NONE': 5} |
| URW | 48 | 65.7 | 35.5 | {'CAPITAL_EFFICIENCY': 16, 'PREDICTION_ROLE_W': 20, 'NONE': 4, 'PREDICTION_ROLE_P2': 8} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 429 | 33.1% | 67.1% | 33.1% | 15.4% | 14.0% | 8.9% | 23.8% | 1.55 |
| 正式推薦 | 391 | 32.5% | 61.6% | 61.6% | 73.4% | 100.0% | 64.2% | 35.8% | 1.45 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中33.6%（無作為9.5%、差+24.2）／P2 平均1.0頭 的中15.3%（無作為9.5%、差+5.8）／P3 平均1.0頭 的中14.0%（無作為9.5%、差+4.5）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.4%（無作為28.4%、差+35.0）／P2 平均6.0頭 的中73.6%（無作為56.8%、差+16.8）／P3 平均10.83頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.9/40（選択性補正込み）・能力順位 14.04/20（249R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.44/40（選択性補正込み）・能力順位 13.61/20（242R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 8,400円（5.6%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）47R・着順まで的中 2R／的中 71R のうち的中赤字 35R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 51.8%（同じ192Rの実績 62.4%）／券種別 EXACTA 64点 PFS 18.3%／TRIFECTA 112点 PFS 14.3%／TRIO 990点 PFS 56.3%／WIDE 334点 PFS 105.8%／WIN 11点 PFS 46.4%／荒れ度（発走前・1番人気オッズ）MID 100R PFS 74.0% 的中赤字 13/36／OPEN 7R PFS 49.8% 的中赤字 0/2／SOLID 82R PFS 47.0% 的中赤字 21/31／UNKNOWN 3R PFS 152.7% 的中赤字 1/2／市場ミラーとの差 189R：実績 60.6% − ミラー 56.3% = Δ 4.3pt（95%区間 -19.6〜30.2、最高1R除き -1.1pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 351,200円（30.5%）／保護層の資金比率 0.0（192R）／組だけ的中（三連単は外れ）54R・着順まで的中 39R／的中 106R のうち的中赤字 88R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 47.6%（同じ192Rの実績 41.5%）／券種別 EXACTA 2973点 PFS 47.5%／TRIFECTA 5487点 PFS 29.1%／TRIO 3060点 PFS 57.8%／荒れ度（発走前・1番人気オッズ）MID 100R PFS 46.8% 的中赤字 44/54／OPEN 7R PFS 15.6% 的中赤字 2/2／SOLID 82R PFS 37.8% 的中赤字 39/47／UNKNOWN 3R PFS 21.7% 的中赤字 3/3／市場ミラーとの差 189R：実績 41.8% − ミラー 69.7% = Δ -27.9pt（95%区間 -52.3〜-5.6、最高1R除き -32.3pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、87R×3券種）：購入 26／予算で削除 0／予想で除外 76／未生成・券種なし 159／役割馬の行き先 {'PURCHASED': 261}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、87R×3券種）：購入 95／予算で削除 27／予想で除外 81／未生成・券種なし 58／役割馬の行き先 {'PURCHASED': 655, 'BUDGET_COMPRESSED': 310}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 33R／W外 54R、2着が P2 役割 6R）：STATIC 6/33（平均3.73位）／STYLE_COND 9/33（平均3.58位） 救済3・喪失0／MARKET_COND 7/31（平均2.9位） 救済5・喪失3
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 56R／W外 31R、2着が P2 役割 42R）：STATIC 44/56（平均4.07位）／STYLE_COND 45/56（平均3.95位） 救済1・喪失0／MARKET_COND 51/54（平均2.89位） 救済9・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 174 | 866,300 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 155 | 569,930 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 79 | 432,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 429 | 1,768,230 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

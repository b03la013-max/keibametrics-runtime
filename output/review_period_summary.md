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

- 反省済みRace 188／PAPER PFS 63.7%／正式推薦 PFS 42.3%
- 第一失敗：{'PREDICTION_ROLE_P2': 31, 'CAPITAL_EFFICIENCY': 69, 'PREDICTION_ROLE_W': 73, 'NONE': 15}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 22 | 51.6 | 73.2 | {'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 12, 'PREDICTION_ROLE_W': 5, 'NONE': 2} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 47 | 53.2 | 47.3 | {'PREDICTION_ROLE_W': 19, 'CAPITAL_EFFICIENCY': 14, 'NONE': 6, 'PREDICTION_ROLE_P2': 8} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 36 | 102.8 | 37.8 | {'PREDICTION_ROLE_W': 18, 'NONE': 1, 'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 14} |
| URW | 48 | 65.7 | 35.5 | {'CAPITAL_EFFICIENCY': 16, 'PREDICTION_ROLE_W': 20, 'NONE': 4, 'PREDICTION_ROLE_P2': 8} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 188 | 31.9% | 64.9% | 31.9% | 14.4% | 13.8% | 6.4% | 24.5% | 1.54 |
| 正式推薦 | 188 | 31.9% | 61.2% | 61.2% | 76.1% | 100.0% | 65.4% | 42.0% | 1.48 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中31.9%（無作為9.3%、差+22.6）／P2 平均1.0頭 的中14.4%（無作為9.3%、差+5.0）／P3 平均1.0頭 的中13.8%（無作為9.3%、差+4.5）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中61.2%（無作為28.0%、差+33.1）／P2 平均6.0頭 的中76.1%（無作為56.1%、差+20.0）／P3 平均10.94頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.68/40（選択性補正込み）・能力順位 14.05/20（188R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.39/40（選択性補正込み）・能力順位 13.6/20（188R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 8,400円（5.7%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）47R・着順まで的中 2R／的中 70R のうち的中赤字 34R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 52.5%（同じ188Rの実績 63.7%）／券種別 EXACTA 62点 PFS 18.9%／TRIFECTA 112点 PFS 14.3%／TRIO 968点 PFS 57.6%／WIDE 328点 PFS 107.4%／WIN 10点 PFS 51.0%／荒れ度（発走前・1番人気オッズ）MID 99R PFS 74.9% 的中赤字 13/36／OPEN 7R PFS 49.8% 的中赤字 0/2／SOLID 79R PFS 48.4% 的中赤字 20/30／UNKNOWN 3R PFS 152.7% 的中赤字 1/2／市場ミラーとの差 185R：実績 61.8% − ミラー 52.0% = Δ 9.8pt（95%区間 -15.0〜36.1、最高1R除き 4.3pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 351,200円（31.1%）／保護層の資金比率 0.0（188R）／組だけ的中（三連単は外れ）54R・着順まで的中 38R／的中 105R のうち的中赤字 87R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 48.4%（同じ188Rの実績 42.3%）／券種別 EXACTA 2907点 PFS 48.6%／TRIFECTA 5313点 PFS 29.9%／TRIO 3060点 PFS 57.8%／荒れ度（発走前・1番人気オッズ）MID 99R PFS 47.3% 的中赤字 44/54／OPEN 7R PFS 15.6% 的中赤字 2/2／SOLID 79R PFS 39.1% 的中赤字 38/46／UNKNOWN 3R PFS 21.7% 的中赤字 3/3／市場ミラーとの差 185R：実績 42.6% − ミラー 67.4% = Δ -24.8pt（95%区間 -48.7〜-1.4、最高1R除き -29.2pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、83R×3券種）：購入 26／予算で削除 0／予想で除外 71／未生成・券種なし 152／役割馬の行き先 {'PURCHASED': 249}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、83R×3券種）：購入 93／予算で削除 27／予想で除外 75／未生成・券種なし 54／役割馬の行き先 {'PURCHASED': 622, 'BUDGET_COMPRESSED': 301}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 31R／W外 52R、2着が P2 役割 6R）：STATIC 6/31（平均3.58位）／STYLE_COND 9/31（平均3.39位） 救済3・喪失0／MARKET_COND 7/29（平均2.9位） 救済5・喪失3
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 54R／W外 29R、2着が P2 役割 42R）：STATIC 43/54（平均3.98位）／STYLE_COND 44/54（平均3.83位） 救済1・喪失0／MARKET_COND 49/52（平均2.88位） 救済8・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 87 | 314,490 | RECURRING |
| P1:ROLE_W_MISS | P1 | 73 | 381,190 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 31 | 186,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 188 | 812,490 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 425／PAPER PFS 61.7%／正式推薦 PFS 69.7%
- 第一失敗：{'NONE': 49, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 123, 'PREDICTION_ROLE_W': 148, 'PREDICTION_ROLE_P2': 68, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 46 | 78.5 | 62.5 | {'NONE': 6, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 17, 'PREDICTION_ROLE_W': 9, 'PREDICTION_ROLE_P2': 5, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 47 | 53.2 | 47.3 | {'PREDICTION_ROLE_W': 19, 'CAPITAL_EFFICIENCY': 14, 'NONE': 6, 'PREDICTION_ROLE_P2': 8} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 72 | 62.3 | 47.3 | {'PREDICTION_ROLE_W': 34, 'CAPITAL_EFFICIENCY': 24, 'PREDICTION_ROLE_P2': 9, 'NONE': 5} |
| URW | 48 | 65.7 | 35.5 | {'CAPITAL_EFFICIENCY': 16, 'PREDICTION_ROLE_W': 20, 'NONE': 4, 'PREDICTION_ROLE_P2': 8} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 425 | 32.9% | 67.3% | 32.9% | 15.5% | 13.9% | 8.9% | 24.0% | 1.55 |
| 正式推薦 | 387 | 32.6% | 61.8% | 61.8% | 73.9% | 100.0% | 63.8% | 35.9% | 1.44 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中33.4%（無作為9.5%、差+24.0）／P2 平均1.0頭 的中15.5%（無作為9.5%、差+6.0）／P3 平均1.0頭 的中13.9%（無作為9.5%、差+4.4）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.5%（無作為28.4%、差+35.2）／P2 平均6.0頭 的中74.2%（無作為56.8%、差+17.4）／P3 平均10.83頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.9/40（選択性補正込み）・能力順位 14.04/20（245R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.52/40（選択性補正込み）・能力順位 13.63/20（238R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 8,400円（5.7%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）47R・着順まで的中 2R／的中 70R のうち的中赤字 34R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 52.5%（同じ188Rの実績 63.7%）／券種別 EXACTA 62点 PFS 18.9%／TRIFECTA 112点 PFS 14.3%／TRIO 968点 PFS 57.6%／WIDE 328点 PFS 107.4%／WIN 10点 PFS 51.0%／荒れ度（発走前・1番人気オッズ）MID 99R PFS 74.9% 的中赤字 13/36／OPEN 7R PFS 49.8% 的中赤字 0/2／SOLID 79R PFS 48.4% 的中赤字 20/30／UNKNOWN 3R PFS 152.7% 的中赤字 1/2／市場ミラーとの差 185R：実績 61.8% − ミラー 52.0% = Δ 9.8pt（95%区間 -15.0〜36.1、最高1R除き 4.3pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 351,200円（31.1%）／保護層の資金比率 0.0（188R）／組だけ的中（三連単は外れ）54R・着順まで的中 38R／的中 105R のうち的中赤字 87R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 48.4%（同じ188Rの実績 42.3%）／券種別 EXACTA 2907点 PFS 48.6%／TRIFECTA 5313点 PFS 29.9%／TRIO 3060点 PFS 57.8%／荒れ度（発走前・1番人気オッズ）MID 99R PFS 47.3% 的中赤字 44/54／OPEN 7R PFS 15.6% 的中赤字 2/2／SOLID 79R PFS 39.1% 的中赤字 38/46／UNKNOWN 3R PFS 21.7% 的中赤字 3/3／市場ミラーとの差 185R：実績 42.6% − ミラー 67.4% = Δ -24.8pt（95%区間 -48.7〜-1.4、最高1R除き -29.2pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、83R×3券種）：購入 26／予算で削除 0／予想で除外 71／未生成・券種なし 152／役割馬の行き先 {'PURCHASED': 249}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、83R×3券種）：購入 93／予算で削除 27／予想で除外 75／未生成・券種なし 54／役割馬の行き先 {'PURCHASED': 622, 'BUDGET_COMPRESSED': 301}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 31R／W外 52R、2着が P2 役割 6R）：STATIC 6/31（平均3.58位）／STYLE_COND 9/31（平均3.39位） 救済3・喪失0／MARKET_COND 7/29（平均2.9位） 救済5・喪失3
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 54R／W外 29R、2着が P2 役割 42R）：STATIC 43/54（平均3.98位）／STYLE_COND 44/54（平均3.83位） 救済1・喪失0／MARKET_COND 49/52（平均2.88位） 救済8・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 172 | 855,120 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 154 | 564,750 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 77 | 420,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 425 | 1,745,050 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

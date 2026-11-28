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

- 反省済みRace 213／PAPER PFS 59.0%／正式推薦 PFS 54.2%
- 第一失敗：{'PREDICTION_ROLE_P2': 37, 'CAPITAL_EFFICIENCY': 72, 'PREDICTION_ROLE_W': 84, 'NONE': 20}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 22 | 51.6 | 73.2 | {'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 12, 'PREDICTION_ROLE_W': 5, 'NONE': 2} |
| KOC | 12 | 21.0 | 280.0 | {'PREDICTION_ROLE_P2': 4, 'CAPITAL_EFFICIENCY': 1, 'NONE': 4, 'PREDICTION_ROLE_W': 3} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 48 | 51.9 | 46.3 | {'PREDICTION_ROLE_W': 20, 'CAPITAL_EFFICIENCY': 14, 'NONE': 6, 'PREDICTION_ROLE_P2': 8} |
| SAG | 23 | 27.8 | 17.9 | {'PREDICTION_ROLE_W': 10, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_P2': 5, 'NONE': 1} |
| SON | 36 | 102.8 | 37.8 | {'PREDICTION_ROLE_W': 18, 'NONE': 1, 'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 14} |
| URW | 48 | 65.7 | 35.5 | {'CAPITAL_EFFICIENCY': 16, 'PREDICTION_ROLE_W': 20, 'NONE': 4, 'PREDICTION_ROLE_P2': 8} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 213 | 32.4% | 64.8% | 32.4% | 12.7% | 14.6% | 6.6% | 23.5% | 1.53 |
| 正式推薦 | 213 | 32.4% | 60.6% | 60.6% | 75.1% | 100.0% | 68.1% | 40.4% | 1.48 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中32.4%（無作為9.4%、差+23.0）／P2 平均1.0頭 的中12.7%（無作為9.4%、差+3.3）／P3 平均1.0頭 的中14.6%（無作為9.4%、差+5.2）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中60.6%（無作為28.2%、差+32.4）／P2 平均6.0頭 的中75.1%（無作為56.4%、差+18.7）／P3 平均10.88頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.56/40（選択性補正込み）・能力順位 14.0/20（213R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.26/40（選択性補正込み）・能力順位 13.6/20（213R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 9,600円（5.7%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）51R・着順まで的中 2R／的中 77R のうち的中赤字 39R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 50.7%（同じ213Rの実績 59.0%）／券種別 EXACTA 74点 PFS 33.5%／TRIFECTA 128点 PFS 12.5%／TRIO 1101点 PFS 53.2%／WIDE 368点 PFS 98.2%／WIN 13点 PFS 39.2%／荒れ度（発走前・1番人気オッズ）MID 109R PFS 69.7% 的中赤字 14/38／OPEN 9R PFS 56.2% 的中赤字 0/3／SOLID 92R PFS 44.4% 的中赤字 24/34／UNKNOWN 3R PFS 152.7% 的中赤字 1/2／市場ミラーとの差 210R：実績 57.3% − ミラー 55.6% = Δ 1.6pt（95%区間 -20.6〜26.3、最高1R除き -3.2pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 351,200円（27.5%）／保護層の資金比率 0.0（213R）／組だけ的中（三連単は外れ）61R・着順まで的中 45R／的中 117R のうち的中赤字 94R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 46.5%（同じ213Rの実績 54.2%）／券種別 EXACTA 3354点 PFS 50.2%／TRIFECTA 6366点 PFS 54.6%／TRIO 3060点 PFS 57.8%／荒れ度（発走前・1番人気オッズ）MID 109R PFS 54.4% 的中赤字 45/58／OPEN 9R PFS 35.0% 的中赤字 2/3／SOLID 92R PFS 56.8% 的中赤字 44/53／UNKNOWN 3R PFS 21.7% 的中赤字 3/3／市場ミラーとの差 210R：実績 54.6% − ミラー 68.6% = Δ -13.9pt（95%区間 -42.3〜17.1、最高1R除き -23.5pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、108R×3券種）：購入 31／予算で削除 0／予想で除外 98／未生成・券種なし 195／役割馬の行き先 {'PURCHASED': 324}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、108R×3券種）：購入 111／予算で削除 33／予想で除外 104／未生成・券種なし 76／役割馬の行き先 {'PURCHASED': 811, 'BUDGET_COMPRESSED': 374}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 40R／W外 68R、2着が P2 役割 6R）：STATIC 6/40（平均3.65位）／STYLE_COND 10/40（平均3.5位） 救済4・喪失0／MARKET_COND 8/38（平均3.03位） 救済6・喪失3
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 68R／W外 40R、2着が P2 役割 50R）：STATIC 53/68（平均4.16位）／STYLE_COND 54/68（平均4.06位） 救済1・喪失0／MARKET_COND 62/66（平均2.98位） 救済12・喪失1

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 94 | 347,090 | RECURRING |
| P1:ROLE_W_MISS | P1 | 84 | 441,640 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 37 | 222,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 213 | 923,090 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 450／PAPER PFS 59.6%／正式推薦 PFS 74.1%
- 第一失敗：{'NONE': 54, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 126, 'PREDICTION_ROLE_W': 159, 'PREDICTION_ROLE_P2': 74, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 46 | 78.5 | 62.5 | {'NONE': 6, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 17, 'PREDICTION_ROLE_W': 9, 'PREDICTION_ROLE_P2': 5, 'EXACT_ORIENTATION': 1} |
| KOC | 35 | 45.8 | 128.3 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 6, 'NONE': 6, 'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 11} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 48 | 51.9 | 46.3 | {'PREDICTION_ROLE_W': 20, 'CAPITAL_EFFICIENCY': 14, 'NONE': 6, 'PREDICTION_ROLE_P2': 8} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 45 | 44.9 | 26.5 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 11, 'PREDICTION_ROLE_W': 15, 'CAPITAL_EFFICIENCY': 13, 'NONE': 3} |
| SON | 72 | 62.3 | 47.3 | {'PREDICTION_ROLE_W': 34, 'CAPITAL_EFFICIENCY': 24, 'PREDICTION_ROLE_P2': 9, 'NONE': 5} |
| URW | 48 | 65.7 | 35.5 | {'CAPITAL_EFFICIENCY': 16, 'PREDICTION_ROLE_W': 20, 'NONE': 4, 'PREDICTION_ROLE_P2': 8} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 450 | 33.1% | 67.1% | 33.1% | 14.7% | 14.2% | 8.9% | 23.6% | 1.55 |
| 正式推薦 | 412 | 32.8% | 61.4% | 61.4% | 73.5% | 100.0% | 65.3% | 35.4% | 1.44 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中33.6%（無作為9.5%、差+24.1）／P2 平均1.0頭 的中14.3%（無作為9.5%、差+4.8）／P3 平均1.0頭 的中14.3%（無作為9.5%、差+4.8）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.0%（無作為28.5%、差+34.5）／P2 平均6.0頭 的中73.7%（無作為56.9%、差+16.8）／P3 平均10.81頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.79/40（選択性補正込み）・能力順位 14.0/20（270R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.4/40（選択性補正込み）・能力順位 13.63/20（263R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 9,600円（5.7%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）51R・着順まで的中 2R／的中 77R のうち的中赤字 39R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 50.7%（同じ213Rの実績 59.0%）／券種別 EXACTA 74点 PFS 33.5%／TRIFECTA 128点 PFS 12.5%／TRIO 1101点 PFS 53.2%／WIDE 368点 PFS 98.2%／WIN 13点 PFS 39.2%／荒れ度（発走前・1番人気オッズ）MID 109R PFS 69.7% 的中赤字 14/38／OPEN 9R PFS 56.2% 的中赤字 0/3／SOLID 92R PFS 44.4% 的中赤字 24/34／UNKNOWN 3R PFS 152.7% 的中赤字 1/2／市場ミラーとの差 210R：実績 57.3% − ミラー 55.6% = Δ 1.6pt（95%区間 -20.6〜26.3、最高1R除き -3.2pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 351,200円（27.5%）／保護層の資金比率 0.0（213R）／組だけ的中（三連単は外れ）61R・着順まで的中 45R／的中 117R のうち的中赤字 94R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 46.5%（同じ213Rの実績 54.2%）／券種別 EXACTA 3354点 PFS 50.2%／TRIFECTA 6366点 PFS 54.6%／TRIO 3060点 PFS 57.8%／荒れ度（発走前・1番人気オッズ）MID 109R PFS 54.4% 的中赤字 45/58／OPEN 9R PFS 35.0% 的中赤字 2/3／SOLID 92R PFS 56.8% 的中赤字 44/53／UNKNOWN 3R PFS 21.7% 的中赤字 3/3／市場ミラーとの差 210R：実績 54.6% − ミラー 68.6% = Δ -13.9pt（95%区間 -42.3〜17.1、最高1R除き -23.5pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、108R×3券種）：購入 31／予算で削除 0／予想で除外 98／未生成・券種なし 195／役割馬の行き先 {'PURCHASED': 324}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、108R×3券種）：購入 111／予算で削除 33／予想で除外 104／未生成・券種なし 76／役割馬の行き先 {'PURCHASED': 811, 'BUDGET_COMPRESSED': 374}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 40R／W外 68R、2着が P2 役割 6R）：STATIC 6/40（平均3.65位）／STYLE_COND 10/40（平均3.5位） 救済4・喪失0／MARKET_COND 8/38（平均3.03位） 救済6・喪失3
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 68R／W外 40R、2着が P2 役割 50R）：STATIC 53/68（平均4.16位）／STYLE_COND 54/68（平均4.06位） 救済1・喪失0／MARKET_COND 62/66（平均2.98位） 救済12・喪失1

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 183 | 915,570 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 161 | 597,350 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 83 | 456,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 450 | 1,855,650 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

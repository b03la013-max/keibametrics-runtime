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

- 反省済みRace 176／PAPER PFS 64.2%／正式推薦 PFS 43.8%
- 第一失敗：{'PREDICTION_ROLE_P2': 28, 'CAPITAL_EFFICIENCY': 65, 'PREDICTION_ROLE_W': 68, 'NONE': 15}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 22 | 51.6 | 73.2 | {'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 12, 'PREDICTION_ROLE_W': 5, 'NONE': 2} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 40 | 60.0 | 50.3 | {'PREDICTION_ROLE_W': 16, 'CAPITAL_EFFICIENCY': 11, 'NONE': 6, 'PREDICTION_ROLE_P2': 7} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 35 | 101.3 | 38.9 | {'PREDICTION_ROLE_W': 17, 'NONE': 1, 'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 14} |
| URW | 44 | 63.0 | 38.2 | {'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 19, 'NONE': 4, 'PREDICTION_ROLE_P2': 6} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 176 | 32.4% | 64.2% | 32.4% | 14.8% | 13.6% | 6.8% | 25.0% | 1.53 |
| 正式推薦 | 176 | 32.4% | 61.4% | 61.4% | 76.7% | 100.0% | 64.8% | 43.8% | 1.49 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中32.4%（無作為9.4%、差+23.0）／P2 平均1.0頭 的中14.8%（無作為9.4%、差+5.3）／P3 平均1.0頭 的中13.6%（無作為9.4%、差+4.2）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中61.4%（無作為28.3%、差+33.1）／P2 平均6.0頭 的中76.7%（無作為56.5%、差+20.2）／P3 平均10.85頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.73/40（選択性補正込み）・能力順位 13.98/20（176R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.37/40（選択性補正込み）・能力順位 13.58/20（176R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 8,400円（6.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）45R・着順まで的中 2R／的中 65R のうち的中赤字 32R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 52.7%（同じ176Rの実績 64.2%）／券種別 EXACTA 60点 PFS 19.5%／TRIFECTA 112点 PFS 14.3%／TRIO 902点 PFS 60.4%／WIDE 306点 PFS 103.0%／WIN 9点 PFS 56.7%／荒れ度（発走前・1番人気オッズ）MID 92R PFS 74.9% 的中赤字 13/33／OPEN 7R PFS 49.8% 的中赤字 0/2／SOLID 74R PFS 49.8% 的中赤字 18/28／UNKNOWN 3R PFS 152.7% 的中赤字 1/2／市場ミラーとの差 173R：実績 62.3% − ミラー 44.9% = Δ 17.4pt（95%区間 -5.6〜42.1、最高1R除き 11.5pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 351,200円（33.3%）／保護層の資金比率 0.0（176R）／組だけ的中（三連単は外れ）52R・着順まで的中 36R／的中 99R のうち的中赤字 81R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 47.5%（同じ176Rの実績 43.8%）／券種別 EXACTA 2703点 PFS 49.2%／TRIFECTA 4797点 PFS 31.9%／TRIO 3060点 PFS 57.8%／荒れ度（発走前・1番人気オッズ）MID 92R PFS 49.4% 的中赤字 41/51／OPEN 7R PFS 15.6% 的中赤字 2/2／SOLID 74R PFS 40.4% 的中赤字 35/43／UNKNOWN 3R PFS 21.7% 的中赤字 3/3／市場ミラーとの差 173R：実績 44.2% − ミラー 68.1% = Δ -23.9pt（95%区間 -51.5〜0.2、最高1R除き -28.7pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、71R×3券種）：購入 24／予算で削除 0／予想で除外 60／未生成・券種なし 129／役割馬の行き先 {'PURCHASED': 213}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、71R×3券種）：購入 85／予算で削除 22／予想で除外 62／未生成・券種なし 44／役割馬の行き先 {'PURCHASED': 529, 'BUDGET_COMPRESSED': 248}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 28R／W外 43R、2着が P2 役割 6R）：STATIC 6/28（平均3.43位）／STYLE_COND 9/28（平均3.25位） 救済3・喪失0／MARKET_COND 6/26（平均2.88位） 救済4・喪失3
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 47R／W外 24R、2着が P2 役割 38R）：STATIC 39/47（平均3.77位）／STYLE_COND 39/47（平均3.62位） 救済0・喪失0／MARKET_COND 43/45（平均2.82位） 救済6・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 81 | 292,430 | RECURRING |
| P1:ROLE_W_MISS | P1 | 68 | 355,870 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 28 | 168,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 176 | 754,430 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 413／PAPER PFS 61.9%／正式推薦 PFS 71.3%
- 第一失敗：{'NONE': 49, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 119, 'PREDICTION_ROLE_W': 143, 'PREDICTION_ROLE_P2': 65, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 46 | 78.5 | 62.5 | {'NONE': 6, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 17, 'PREDICTION_ROLE_W': 9, 'PREDICTION_ROLE_P2': 5, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 40 | 60.0 | 50.3 | {'PREDICTION_ROLE_W': 16, 'CAPITAL_EFFICIENCY': 11, 'NONE': 6, 'PREDICTION_ROLE_P2': 7} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 71 | 61.2 | 48.0 | {'PREDICTION_ROLE_W': 33, 'CAPITAL_EFFICIENCY': 24, 'PREDICTION_ROLE_P2': 9, 'NONE': 5} |
| URW | 44 | 63.0 | 38.2 | {'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 19, 'NONE': 4, 'PREDICTION_ROLE_P2': 6} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 413 | 33.2% | 67.1% | 33.2% | 15.7% | 13.8% | 9.2% | 24.2% | 1.55 |
| 正式推薦 | 375 | 32.8% | 61.9% | 61.9% | 74.1% | 100.0% | 63.5% | 36.5% | 1.44 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中33.8%（無作為9.5%、差+24.2）／P2 平均1.0頭 的中15.7%（無作為9.5%、差+6.2）／P3 平均1.0頭 的中13.8%（無作為9.5%、差+4.2）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.8%（無作為28.5%、差+35.2）／P2 平均6.0頭 的中74.5%（無作為57.1%、差+17.4）／P3 平均10.78頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.95/40（選択性補正込み）・能力順位 14.0/20（233R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.51/40（選択性補正込み）・能力順位 13.61/20（226R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 8,400円（6.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）45R・着順まで的中 2R／的中 65R のうち的中赤字 32R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 52.7%（同じ176Rの実績 64.2%）／券種別 EXACTA 60点 PFS 19.5%／TRIFECTA 112点 PFS 14.3%／TRIO 902点 PFS 60.4%／WIDE 306点 PFS 103.0%／WIN 9点 PFS 56.7%／荒れ度（発走前・1番人気オッズ）MID 92R PFS 74.9% 的中赤字 13/33／OPEN 7R PFS 49.8% 的中赤字 0/2／SOLID 74R PFS 49.8% 的中赤字 18/28／UNKNOWN 3R PFS 152.7% 的中赤字 1/2／市場ミラーとの差 173R：実績 62.3% − ミラー 44.9% = Δ 17.4pt（95%区間 -5.6〜42.1、最高1R除き 11.5pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 351,200円（33.3%）／保護層の資金比率 0.0（176R）／組だけ的中（三連単は外れ）52R・着順まで的中 36R／的中 99R のうち的中赤字 81R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 47.5%（同じ176Rの実績 43.8%）／券種別 EXACTA 2703点 PFS 49.2%／TRIFECTA 4797点 PFS 31.9%／TRIO 3060点 PFS 57.8%／荒れ度（発走前・1番人気オッズ）MID 92R PFS 49.4% 的中赤字 41/51／OPEN 7R PFS 15.6% 的中赤字 2/2／SOLID 74R PFS 40.4% 的中赤字 35/43／UNKNOWN 3R PFS 21.7% 的中赤字 3/3／市場ミラーとの差 173R：実績 44.2% − ミラー 68.1% = Δ -23.9pt（95%区間 -51.5〜0.2、最高1R除き -28.7pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、71R×3券種）：購入 24／予算で削除 0／予想で除外 60／未生成・券種なし 129／役割馬の行き先 {'PURCHASED': 213}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、71R×3券種）：購入 85／予算で削除 22／予想で除外 62／未生成・券種なし 44／役割馬の行き先 {'PURCHASED': 529, 'BUDGET_COMPRESSED': 248}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 28R／W外 43R、2着が P2 役割 6R）：STATIC 6/28（平均3.43位）／STYLE_COND 9/28（平均3.25位） 救済3・喪失0／MARKET_COND 6/26（平均2.88位） 救済4・喪失3
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 47R／W外 24R、2着が P2 役割 38R）：STATIC 39/47（平均3.77位）／STYLE_COND 39/47（平均3.62位） 救済0・喪失0／MARKET_COND 43/45（平均2.82位） 救済6・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 167 | 829,800 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 148 | 542,690 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 74 | 402,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 413 | 1,686,990 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

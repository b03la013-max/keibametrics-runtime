# 地方版 2026-11-26 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 13／PAPER PFS 108.8%／正式推薦 PFS 26.2%
- 第一失敗：{'PREDICTION_ROLE_W': 4, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_P2': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 1 | 0.0 | 0.0 | {'PREDICTION_ROLE_W': 1} |
| SON | 7 | 181.6 | 31.0 | {'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 1} |
| URW | 5 | 22.8 | 24.6 | {'PREDICTION_ROLE_P2': 1, 'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 3} |

## 日次自律監査

1. 配送：管理 48R／PAPER発走前送信 21／正式試行 21・発走前送信 21／本人確認 0
2. 計算完走：Full29 21／Signed FINAL 21／KRS5000 21／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 108.8%／正式推薦 26.2%／実購入なし
5. Learning：RESULT署名検証 13／学習状態保存 13／前Raceの学習状態を結合した正式Race 21（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '266/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 13 | 46.2% | 84.6% | 46.2% | 0.0% | 15.4% | 0.0% | 23.1% | 1.62 |
| 正式推薦 | 13 | 30.8% | 69.2% | 69.2% | 69.2% | 100.0% | 69.2% | 38.5% | 1.38 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中46.2%（無作為8.9%、差+37.3）／P2 平均1.0頭 的中0.0%（無作為8.9%、差-8.9）／P3 平均1.0頭 的中15.4%（無作為8.9%、差+6.5）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中69.2%（無作為26.6%、差+42.6）／P2 平均6.0頭 的中69.2%（無作為53.3%、差+16.0）／P3 平均11.38頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.62/40（選択性補正込み）・能力順位 14.58/20（13R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.53/40（選択性補正込み）・能力順位 13.69/20（13R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（5.7%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）4R・着順まで的中 0R／的中 4R のうち的中赤字 0R／損益分岐の倍率 平均 8.1倍／同じ点数を無作為に選んだ場合の期待PFS 43.8%（同じ13Rの実績 108.8%）／券種別 EXACTA 5点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 69点 PFS 92.6%／WIDE 22点 PFS 228.6%／WIN 1点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 8R PFS 19.8% 的中赤字 0/1／SOLID 4R PFS 162.9% 的中赤字 0/2／UNKNOWN 1R PFS 577.1% 的中赤字 0/1／市場ミラーとの差 12R：実績 75.3% − ミラー 27.6% = Δ 47.8pt（95%区間 -31.0〜184.9、最高1R除き -6.8pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 30,200円（38.7%）／保護層の資金比率 0.0（13R）／組だけ的中（三連単は外れ）3R・着順まで的中 2R／的中 7R のうち的中赤字 7R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 32.8%（同じ13Rの実績 26.2%）／券種別 EXACTA 195点 PFS 27.5%／TRIFECTA 325点 PFS 22.7%／TRIO 260点 PFS 29.6%／荒れ度（発走前・1番人気オッズ）MID 8R PFS 15.9% 的中赤字 3/3／SOLID 4R PFS 50.0% 的中赤字 3/3／UNKNOWN 1R PFS 13.3% 的中赤字 1/1／市場ミラーとの差 12R：実績 27.2% − ミラー 31.1% = Δ -3.9pt（95%区間 -28.6〜21.1、最高1R除き -11.3pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、13R×3券種）：購入 3／予算で削除 0／予想で除外 13／未生成・券種なし 23／役割馬の行き先 {'PURCHASED': 39}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、13R×3券種）：購入 14／予算で削除 6／予想で除外 12／未生成・券種なし 7／役割馬の行き先 {'PURCHASED': 95, 'BUDGET_COMPRESSED': 53}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 6R／W外 7R、2着が P2 役割 0R）：STATIC 0/6（平均5.17位）／STYLE_COND 1/6（平均4.67位） 救済1・喪失0／MARKET_COND 0/5（平均4.4位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 9R／W外 4R、2着が P2 役割 7R）：STATIC 7/9（平均4.22位）／STYLE_COND 7/9（平均3.89位） 救済0・喪失0／MARKET_COND 7/8（平均2.62位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 7 | 21,580 | RECURRING |
| P1:ROLE_W_MISS | P1 | 4 | 24,000 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 13 | 57,580 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

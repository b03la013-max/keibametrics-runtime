# 地方版 2026-11-27 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 15／PAPER PFS 39.0%／正式推薦 PFS 57.9%
- 第一失敗：{'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 6, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| NGY | 1 | 0.0 | 300.0 | {'PREDICTION_ROLE_W': 1} |
| SON | 8 | 73.0 | 20.0 | {'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 2} |
| URW | 6 | 0.0 | 68.0 | {'PREDICTION_ROLE_W': 5, 'NONE': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 20／正式試行 20・発走前送信 20／本人確認 0
2. 計算完走：Full29 20／Signed FINAL 20／KRS5000 20／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 39.0%／正式推薦 57.9%／実購入なし
5. Learning：RESULT署名検証 15／学習状態保存 15／前Raceの学習状態を結合した正式Race 20（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '300R到達', 'C14-FORMAL-P2BOX20-ONLY': '300R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '300R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '295/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 15 | 26.7% | 60.0% | 26.7% | 40.0% | 26.7% | 0.0% | 33.3% | 1.67 |
| 正式推薦 | 15 | 40.0% | 46.7% | 46.7% | 100.0% | 100.0% | 80.0% | 33.3% | 1.6 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中26.7%（無作為9.7%、差+17.0）／P2 平均1.0頭 的中40.0%（無作為9.7%、差+30.3）／P3 平均1.0頭 的中26.7%（無作為9.7%、差+17.0）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中46.7%（無作為29.1%、差+17.6）／P2 平均6.0頭 的中100.0%（無作為58.2%、差+41.8）／P3 平均10.6頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.93/40（選択性補正込み）・能力順位 14.66/20（15R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.0/40（選択性補正込み）・能力順位 15.04/20（15R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）5R・着順まで的中 0R／的中 5R のうち的中赤字 4R／損益分岐の倍率 平均 7.0倍／同じ点数を無作為に選んだ場合の期待PFS 51.2%（同じ15Rの実績 39.0%）／券種別 TRIO 75点 PFS 46.4%／WIDE 30点 PFS 20.3%／荒れ度（発走前・1番人気オッズ）MID 8R PFS 46.4% 的中赤字 1/2／SOLID 6R PFS 22.6% 的中赤字 2/2／UNKNOWN 1R PFS 77.1% 的中赤字 1/1／市場ミラーとの差 14R：実績 36.2% − ミラー 18.8% = Δ 17.4pt（95%区間 -17.8〜66.0、最高1R除き -4.4pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 0.0（15R）／組だけ的中（三連単は外れ）6R・着順まで的中 5R／的中 10R のうち的中赤字 8R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 33.6%（同じ15Rの実績 57.9%）／券種別 EXACTA 267点 PFS 58.5%／TRIFECTA 633点 PFS 57.6%／荒れ度（発走前・1番人気オッズ）MID 8R PFS 66.3% 的中赤字 5/6／SOLID 6R PFS 52.1% 的中赤字 2/3／UNKNOWN 1R PFS 25.5% 的中赤字 1/1／市場ミラーとの差 14R：実績 60.2% − ミラー 34.7% = Δ 25.5pt（95%区間 -34.5〜98.7、最高1R除き -1.7pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、15R×3券種）：購入 5／予算で削除 0／予想で除外 10／未生成・券種なし 30／役割馬の行き先 {'PURCHASED': 45}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、15R×3券種）：購入 14／予算で削除 4／予想で除外 12／未生成・券種なし 15／役割馬の行き先 {'BUDGET_COMPRESSED': 48, 'PURCHASED': 111}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 4R／W外 11R、2着が P2 役割 3R）：STATIC 3/4（平均1.25位）／STYLE_COND 3/4（平均1.25位） 救済0・喪失0／MARKET_COND 1/3（平均2.33位） 救済0・喪失1
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 7R／W外 8R、2着が P2 役割 7R）：STATIC 7/7（平均2.14位）／STYLE_COND 7/7（平均1.86位） 救済0・喪失0／MARKET_COND 6/6（平均2.5位） 救済0・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 8 | 37,500 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 8 | 36,600 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 15 | 66,600 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

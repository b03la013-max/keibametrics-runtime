# 地方版 2026-11-26 日次総括（自動・推薦試算・実購入なし）

- 反省済みRace 48／PAPER PFS 101.4%／正式推薦 PFS 45.1%
- 第一失敗：{'PREDICTION_ROLE_W': 14, 'CAPITAL_EFFICIENCY': 23, 'NONE': 4, 'PREDICTION_ROLE_P2': 7}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 12 | 76.1 | 55.5 | {'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 9, 'NONE': 1, 'PREDICTION_ROLE_P2': 1} |
| NGY | 12 | 138.0 | 66.6 | {'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'NONE': 3, 'CAPITAL_EFFICIENCY': 3} |
| SON | 12 | 160.3 | 35.4 | {'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 1} |
| URW | 12 | 45.0 | 22.9 | {'PREDICTION_ROLE_P2': 3, 'PREDICTION_ROLE_W': 4, 'CAPITAL_EFFICIENCY': 5} |

## 日次自律監査

1. 配送：管理 48R／PAPER発走前送信 48／正式試行 48・発走前送信 48／本人確認 0
2. 計算完走：Full29 48／Signed FINAL 48／KRS5000 48／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 101.4%／正式推薦 45.1%／実購入なし
5. Learning：RESULT署名検証 48／学習状態保存 48／前Raceの学習状態を結合した正式Race 48（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '266/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 48 | 37.5% | 66.7% | 37.5% | 14.6% | 20.8% | 10.4% | 31.2% | 1.6 |
| 正式推薦 | 48 | 33.3% | 70.8% | 70.8% | 77.1% | 100.0% | 70.8% | 52.1% | 1.5 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中37.5%（無作為9.3%、差+28.2）／P2 平均1.0頭 的中14.6%（無作為9.3%、差+5.2）／P3 平均1.0頭 的中20.8%（無作為9.3%、差+11.5）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中70.8%（無作為28.0%、差+42.8）／P2 平均6.0頭 的中77.1%（無作為56.1%、差+21.0）／P3 平均10.94頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.35/40（選択性補正込み）・能力順位 14.41/20（48R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.44/40（選択性補正込み）・能力順位 13.87/20（48R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 3,000円（7.7%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）15R・着順まで的中 1R／的中 21R のうち的中赤字 8R／損益分岐の倍率 平均 8.2倍／同じ点数を無作為に選んだ場合の期待PFS 47.6%（同じ48Rの実績 101.4%）／券種別 EXACTA 21点 PFS 42.9%／TRIFECTA 40点 PFS 25.2%／TRIO 248点 PFS 94.1%／WIDE 80点 PFS 179.1%／WIN 3点 PFS 53.3%／荒れ度（発走前・1番人気オッズ）MID 27R PFS 107.0% 的中赤字 2/9／SOLID 20R PFS 77.6% 的中赤字 6/11／UNKNOWN 1R PFS 577.1% 的中赤字 0/1／市場ミラーとの差 47R：実績 92.7% − ミラー 47.1% = Δ 45.6pt（95%区間 -10.3〜114.3、最高1R除き 25.1pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 110,800円（38.5%）／保護層の資金比率 0.0（48R）／組だけ的中（三連単は外れ）13R・着順まで的中 12R／的中 30R のうち的中赤字 26R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 43.7%（同じ48Rの実績 45.1%）／券種別 EXACTA 720点 PFS 49.0%／TRIFECTA 1200点 PFS 35.6%／TRIO 960点 PFS 54.1%／荒れ度（発走前・1番人気オッズ）MID 27R PFS 42.6% 的中赤字 15/17／SOLID 20R PFS 50.1% 的中赤字 10/12／UNKNOWN 1R PFS 13.3% 的中赤字 1/1／市場ミラーとの差 47R：実績 45.8% − ミラー 57.1% = Δ -11.4pt（95%区間 -46.2〜19.0、最高1R除き -18.1pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、48R×3券種）：購入 17／予算で削除 0／予想で除外 44／未生成・券種なし 83／役割馬の行き先 {'PURCHASED': 144}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、48R×3券種）：購入 63／予算で削除 18／予想で除外 42／未生成・券種なし 21／役割馬の行き先 {'PURCHASED': 353, 'BUDGET_COMPRESSED': 172}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 18R／W外 30R、2着が P2 役割 2R）：STATIC 2/18（平均4.17位）／STYLE_COND 4/18（平均3.94位） 救済2・喪失0／MARKET_COND 4/17（平均3.12位） 救済3・喪失1
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 34R／W外 14R、2着が P2 役割 27R）：STATIC 28/34（平均4.03位）／STYLE_COND 28/34（平均3.88位） 救済0・喪失0／MARKET_COND 31/33（平均2.94位） 救済4・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 26 | 79,390 | RECURRING |
| P1:ROLE_W_MISS | P1 | 14 | 76,990 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 7 | 42,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 48 | 187,390 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 2026-11-27 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 26／PAPER PFS 56.6%／正式推薦 PFS 47.5%
- 第一失敗：{'PREDICTION_ROLE_W': 11, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| NGY | 5 | 6.6 | 78.8 | {'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 1, 'CAPITAL_EFFICIENCY': 2} |
| SON | 12 | 96.7 | 17.6 | {'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 1} |
| URW | 9 | 31.0 | 69.9 | {'PREDICTION_ROLE_W': 5, 'NONE': 2, 'CAPITAL_EFFICIENCY': 2} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 30／正式試行 30・発走前送信 30／本人確認 0
2. 計算完走：Full29 30／Signed FINAL 30／KRS5000 30／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 56.6%／正式推薦 47.5%／実購入なし
5. Learning：RESULT署名検証 26／学習状態保存 26／前Raceの学習状態を結合した正式Race 30（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '300R到達', 'C14-FORMAL-P2BOX20-ONLY': '300R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '300R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '300R到達', 'C17-P2-ZAI-PLACE': '300R到達', 'C18-W-PLUS-FAVORITE': '300R到達', 'C19-W-PLUS-TOP2-POP': '300R到達', 'C20-P2-PLUS-TOP3-POP': '300R到達', 'C21-BVI-L-R2-TERTILE': '295/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 26 | 42.3% | 69.2% | 42.3% | 26.9% | 19.2% | 0.0% | 30.8% | 1.73 |
| 正式推薦 | 26 | 38.5% | 57.7% | 57.7% | 92.3% | 100.0% | 80.8% | 34.6% | 1.58 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中42.3%（無作為9.2%、差+33.1）／P2 平均1.0頭 的中26.9%（無作為9.2%、差+17.7）／P3 平均1.0頭 的中19.2%（無作為9.2%、差+10.0）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中57.7%（無作為27.6%、差+30.1）／P2 平均6.0頭 的中92.3%（無作為55.3%、差+37.0）／P3 平均11.08頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.81/40（選択性補正込み）・能力順位 15.04/20（26R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.87/40（選択性補正込み）・能力順位 14.81/20（26R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）8R・着順まで的中 0R／的中 11R のうち的中赤字 6R／損益分岐の倍率 平均 7.0倍／同じ点数を無作為に選んだ場合の期待PFS 41.0%（同じ26Rの実績 56.6%）／券種別 TRIO 130点 PFS 47.8%／WIDE 52点 PFS 78.7%／荒れ度（発走前・1番人気オッズ）MID 15R PFS 81.7% 的中赤字 1/6／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 9R PFS 18.7% 的中赤字 4/4／UNKNOWN 1R PFS 77.1% 的中赤字 1/1／市場ミラーとの差 25R：実績 55.8% − ミラー 35.0% = Δ 20.7pt（95%区間 -23.8〜71.8、最高1R除き 4.5pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 0.0（26R）／組だけ的中（三連単は外れ）7R・着順まで的中 9R／的中 16R のうち的中赤字 13R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 26.5%（同じ26Rの実績 47.5%）／券種別 EXACTA 459点 PFS 49.6%／TRIFECTA 1101点 PFS 46.6%／荒れ度（発走前・1番人気オッズ）MID 15R PFS 53.5% 的中赤字 8/10／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 9R PFS 45.2% 的中赤字 4/5／UNKNOWN 1R PFS 25.5% 的中赤字 1/1／市場ミラーとの差 25R：実績 48.4% − ミラー 37.4% = Δ 10.9pt（95%区間 -27.9〜56.9、最高1R除き -4.4pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、26R×3券種）：購入 8／予算で削除 0／予想で除外 18／未生成・券種なし 52／役割馬の行き先 {'PURCHASED': 78}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、26R×3券種）：購入 24／予算で削除 6／予想で除外 22／未生成・券種なし 26／役割馬の行き先 {'BUDGET_COMPRESSED': 90, 'PURCHASED': 198}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 11R／W外 15R、2着が P2 役割 4R）：STATIC 4/11（平均2.36位）／STYLE_COND 5/11（平均2.27位） 救済1・喪失0／MARKET_COND 3/10（平均2.3位） 救済2・喪失2
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 15R／W外 11R、2着が P2 役割 13R）：STATIC 13/15（平均3.0位）／STYLE_COND 13/15（平均2.87位） 救済0・喪失0／MARKET_COND 14/14（平均2.57位） 救済2・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 13 | 53,320 | RECURRING |
| P1:ROLE_W_MISS | P1 | 11 | 55,500 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 26 | 113,320 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

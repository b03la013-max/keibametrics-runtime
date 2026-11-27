# 地方版 2026-11-27 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 14／PAPER PFS 41.7%／正式推薦 PFS 35.0%
- 第一失敗：{'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 6}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| NGY | 1 | 0.0 | 300.0 | {'PREDICTION_ROLE_W': 1} |
| SON | 8 | 73.0 | 20.0 | {'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 2} |
| URW | 5 | 0.0 | 5.9 | {'PREDICTION_ROLE_W': 5} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 19／正式試行 19・発走前送信 19／本人確認 0
2. 計算完走：Full29 19／Signed FINAL 19／KRS5000 19／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 41.7%／正式推薦 35.0%／実購入なし
5. Learning：RESULT署名検証 14／学習状態保存 14／前Raceの学習状態を結合した正式Race 19（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '300R到達', 'C14-FORMAL-P2BOX20-ONLY': '300R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '300R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '295/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 14 | 28.6% | 57.1% | 28.6% | 42.9% | 28.6% | 0.0% | 35.7% | 1.64 |
| 正式推薦 | 14 | 35.7% | 42.9% | 42.9% | 100.0% | 100.0% | 78.6% | 28.6% | 1.57 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中28.6%（無作為9.8%、差+18.8）／P2 平均1.0頭 的中42.9%（無作為9.8%、差+33.1）／P3 平均1.0頭 的中28.6%（無作為9.8%、差+18.8）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中42.9%（無作為29.4%、差+13.5）／P2 平均6.0頭 的中100.0%（無作為58.8%、差+41.2）／P3 平均10.5頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.64/40（選択性補正込み）・能力順位 14.51/20（14R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.46/40（選択性補正込み）・能力順位 14.82/20（14R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）5R・着順まで的中 0R／的中 5R のうち的中赤字 4R／損益分岐の倍率 平均 7.0倍／同じ点数を無作為に選んだ場合の期待PFS 54.0%（同じ14Rの実績 41.7%）／券種別 TRIO 70点 PFS 49.7%／WIDE 28点 PFS 21.8%／荒れ度（発走前・1番人気オッズ）MID 7R PFS 53.1% 的中赤字 1/2／SOLID 6R PFS 22.6% 的中赤字 2/2／UNKNOWN 1R PFS 77.1% 的中赤字 1/1／市場ミラーとの差 13R：実績 39.0% − ミラー 20.2% = Δ 18.8pt（95%区間 -18.1〜71.1、最高1R除き -4.8pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 0.0（14R）／組だけ的中（三連単は外れ）6R・着順まで的中 4R／的中 9R のうち的中赤字 8R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 34.3%（同じ14Rの実績 35.0%）／券種別 EXACTA 246点 PFS 39.8%／TRIFECTA 594点 PFS 33.0%／荒れ度（発走前・1番人気オッズ）MID 7R PFS 21.7% 的中赤字 5/5／SOLID 6R PFS 52.1% 的中赤字 2/3／UNKNOWN 1R PFS 25.5% 的中赤字 1/1／市場ミラーとの差 13R：実績 35.7% − ミラー 37.4% = Δ -1.7pt（95%区間 -45.2〜52.5、最高1R除き -22.2pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、14R×3券種）：購入 5／予算で削除 0／予想で除外 9／未生成・券種なし 28／役割馬の行き先 {'PURCHASED': 42}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、14R×3券種）：購入 12／予算で削除 4／予想で除外 12／未生成・券種なし 14／役割馬の行き先 {'BUDGET_COMPRESSED': 44, 'PURCHASED': 103}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 4R／W外 10R、2着が P2 役割 3R）：STATIC 3/4（平均1.25位）／STYLE_COND 3/4（平均1.25位） 救済0・喪失0／MARKET_COND 1/3（平均2.33位） 救済0・喪失1
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 6R／W外 8R、2着が P2 役割 6R）：STATIC 6/6（平均2.33位）／STYLE_COND 6/6（平均2.0位） 救済0・喪失0／MARKET_COND 5/5（平均2.0位） 救済0・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 8 | 37,500 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 8 | 36,600 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 14 | 66,600 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

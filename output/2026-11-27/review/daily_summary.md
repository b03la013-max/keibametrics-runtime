# 地方版 2026-11-27 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 32／PAPER PFS 57.8%／正式推薦 PFS 43.1%
- 第一失敗：{'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 4, 'CAPITAL_EFFICIENCY': 13, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| NGY | 8 | 4.0 | 67.4 | {'PREDICTION_ROLE_W': 3, 'PREDICTION_ROLE_P2': 1, 'CAPITAL_EFFICIENCY': 4} |
| SON | 12 | 96.7 | 17.6 | {'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 1} |
| URW | 12 | 56.2 | 52.4 | {'PREDICTION_ROLE_W': 6, 'NONE': 2, 'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_P2': 2} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 34／正式試行 34・発走前送信 34／本人確認 0
2. 計算完走：Full29 34／Signed FINAL 34／KRS5000 34／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 57.8%／正式推薦 43.1%／実購入なし
5. Learning：RESULT署名検証 32／学習状態保存 32／前Raceの学習状態を結合した正式Race 34（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '300R到達', 'C14-FORMAL-P2BOX20-ONLY': '300R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '300R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '300R到達', 'C17-P2-ZAI-PLACE': '300R到達', 'C18-W-PLUS-FAVORITE': '300R到達', 'C19-W-PLUS-TOP2-POP': '300R到達', 'C20-P2-PLUS-TOP3-POP': '300R到達', 'C21-BVI-L-R2-TERTILE': '295/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 32 | 40.6% | 68.8% | 40.6% | 25.0% | 21.9% | 0.0% | 25.0% | 1.72 |
| 正式推薦 | 32 | 37.5% | 59.4% | 59.4% | 84.4% | 100.0% | 81.2% | 34.4% | 1.56 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中40.6%（無作為9.0%、差+31.6）／P2 平均1.0頭 的中25.0%（無作為9.0%、差+16.0）／P3 平均1.0頭 的中21.9%（無作為9.0%、差+12.9）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中59.4%（無作為27.0%、差+32.3）／P2 平均6.0頭 的中84.4%（無作為54.1%、差+30.3）／P3 平均11.31頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.31/40（選択性補正込み）・能力順位 14.97/20（32R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.82/40（選択性補正込み）・能力順位 14.83/20（32R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）8R・着順まで的中 0R／的中 13R のうち的中赤字 6R／損益分岐の倍率 平均 7.2倍／同じ点数を無作為に選んだ場合の期待PFS 40.2%（同じ32Rの実績 57.8%）／券種別 TRIO 166点 PFS 37.4%／WIDE 64点 PFS 110.8%／荒れ度（発走前・1番人気オッズ）MID 20R PFS 79.3% 的中赤字 1/8／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 10R PFS 16.9% 的中赤字 4/4／UNKNOWN 1R PFS 77.1% 的中赤字 1/1／市場ミラーとの差 31R：実績 57.2% − ミラー 87.2% = Δ -30.0pt（95%区間 -113.2〜40.4、最高1R除き -44.3pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 0.0（32R）／組だけ的中（三連単は外れ）7R・着順まで的中 11R／的中 19R のうち的中赤字 16R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 28.0%（同じ32Rの実績 43.1%）／券種別 EXACTA 561点 PFS 45.7%／TRIFECTA 1359点 PFS 42.0%／荒れ度（発走前・1番人気オッズ）MID 20R PFS 45.9% 的中赤字 10/12／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 10R PFS 43.7% 的中赤字 5/6／UNKNOWN 1R PFS 25.5% 的中赤字 1/1／市場ミラーとの差 31R：実績 43.7% − ミラー 40.4% = Δ 3.3pt（95%区間 -29.3〜44.2、最高1R除き -9.3pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、32R×3券種）：購入 8／予算で削除 0／予想で除外 24／未生成・券種なし 64／役割馬の行き先 {'PURCHASED': 96}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、32R×3券種）：購入 29／予算で削除 8／予想で除外 28／未生成・券種なし 31／役割馬の行き先 {'BUDGET_COMPRESSED': 118, 'PURCHASED': 244}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 13R／W外 19R、2着が P2 役割 4R）：STATIC 4/13（平均2.77位）／STYLE_COND 5/13（平均2.62位） 救済1・喪失0／MARKET_COND 3/12（平均2.58位） 救済2・喪失2
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 19R／W外 13R、2着が P2 役割 15R）：STATIC 15/19（平均3.53位）／STYLE_COND 16/19（平均3.37位） 救済1・喪失0／MARKET_COND 17/18（平均2.89位） 救済3・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 16 | 62,610 | RECURRING |
| P1:ROLE_W_MISS | P1 | 13 | 64,830 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 4 | 24,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 32 | 140,610 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

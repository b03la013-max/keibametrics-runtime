# 地方版 2026-11-27 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 11／PAPER PFS 25.7%／正式推薦 PFS 16.4%
- 第一失敗：{'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 6}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| SON | 7 | 40.4 | 21.5 | {'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 2} |
| URW | 4 | 0.0 | 7.4 | {'PREDICTION_ROLE_W': 4} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 16／正式試行 16・発走前送信 16／本人確認 0
2. 計算完走：Full29 16／Signed FINAL 16／KRS5000 16／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 25.7%／正式推薦 16.4%／実購入なし
5. Learning：RESULT署名検証 11／学習状態保存 11／前Raceの学習状態を結合した正式Race 16（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '300R到達', 'C14-FORMAL-P2BOX20-ONLY': '300R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '300R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '295/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 11 | 27.3% | 54.5% | 27.3% | 45.5% | 36.4% | 0.0% | 36.4% | 1.73 |
| 正式推薦 | 11 | 36.4% | 45.5% | 45.5% | 100.0% | 100.0% | 81.8% | 27.3% | 1.55 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中27.3%（無作為9.6%、差+17.7）／P2 平均1.0頭 的中45.5%（無作為9.6%、差+35.9）／P3 平均1.0頭 的中36.4%（無作為9.6%、差+26.8）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中45.5%（無作為28.7%、差+16.7）／P2 平均6.0頭 的中100.0%（無作為57.5%、差+42.5）／P3 平均10.64頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 17.73/40（選択性補正込み）・能力順位 14.95/20（11R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.46/40（選択性補正込み）・能力順位 15.19/20（11R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）4R・着順まで的中 0R／的中 4R のうち的中赤字 4R／損益分岐の倍率 平均 7.0倍／同じ点数を無作為に選んだ場合の期待PFS 58.4%（同じ11Rの実績 25.7%）／券種別 TRIO 55点 PFS 29.1%／WIDE 22点 PFS 17.3%／荒れ度（発走前・1番人気オッズ）MID 6R PFS 11.7% 的中赤字 1/1／SOLID 4R PFS 33.9% 的中赤字 2/2／UNKNOWN 1R PFS 77.1% 的中赤字 1/1／市場ミラーとの差 10R：実績 20.6% − ミラー 26.3% = Δ -5.7pt（95%区間 -27.9〜15.4、最高1R除き -6.3pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 0.0（11R）／組だけ的中（三連単は外れ）5R・着順まで的中 3R／的中 7R のうち的中赤字 7R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 36.9%（同じ11Rの実績 16.4%）／券種別 EXACTA 192点 PFS 30.8%／TRIFECTA 468点 PFS 10.5%／荒れ度（発走前・1番人気オッズ）MID 6R PFS 23.8% 的中赤字 4/4／SOLID 4R PFS 3.1% 的中赤字 2/2／UNKNOWN 1R PFS 25.5% 的中赤字 1/1／市場ミラーとの差 10R：実績 15.5% − ミラー 42.2% = Δ -26.7pt（95%区間 -65.7〜1.1、最高1R除き -29.7pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、11R×3券種）：購入 4／予算で削除 0／予想で除外 7／未生成・券種なし 22／役割馬の行き先 {'PURCHASED': 33}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、11R×3券種）：購入 9／予算で削除 3／予想で除外 10／未生成・券種なし 11／役割馬の行き先 {'PURCHASED': 82, 'BUDGET_COMPRESSED': 35}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 3R／W外 8R、2着が P2 役割 2R）：STATIC 2/3（平均1.33位）／STYLE_COND 2/3（平均1.33位） 救済0・喪失0／MARKET_COND 1/2（平均2.5位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 5R／W外 6R、2着が P2 役割 5R）：STATIC 5/5（平均2.0位）／STYLE_COND 5/5（平均1.8位） 救済0・喪失0／MARKET_COND 4/4（平均2.0位） 救済0・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 7 | 31,180 | RECURRING |
| P1:ROLE_W_MISS | P1 | 6 | 31,500 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 11 | 55,180 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 2026-11-27 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 13／PAPER PFS 44.9%／正式推薦 PFS 14.6%
- 第一失敗：{'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 7}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| SON | 8 | 73.0 | 20.0 | {'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 2} |
| URW | 5 | 0.0 | 5.9 | {'PREDICTION_ROLE_W': 5} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 19／正式試行 19・発走前送信 19／本人確認 0
2. 計算完走：Full29 19／Signed FINAL 19／KRS5000 19／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 44.9%／正式推薦 14.6%／実購入なし
5. Learning：RESULT署名検証 13／学習状態保存 13／前Raceの学習状態を結合した正式Race 19（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '300R到達', 'C14-FORMAL-P2BOX20-ONLY': '300R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '300R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '295/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 13 | 30.8% | 53.8% | 30.8% | 46.2% | 30.8% | 0.0% | 38.5% | 1.62 |
| 正式推薦 | 13 | 38.5% | 46.2% | 46.2% | 100.0% | 100.0% | 76.9% | 23.1% | 1.54 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中30.8%（無作為9.8%、差+20.9）／P2 平均1.0頭 的中46.2%（無作為9.8%、差+36.3）／P3 平均1.0頭 的中30.8%（無作為9.8%、差+20.9）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中46.2%（無作為29.5%、差+16.6）／P2 平均6.0頭 的中100.0%（無作為59.1%、差+40.9）／P3 平均10.46頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 17.23/40（選択性補正込み）・能力順位 14.5/20（13R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.62/40（選択性補正込み）・能力順位 14.76/20（13R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）5R・着順まで的中 0R／的中 5R のうち的中赤字 4R／損益分岐の倍率 平均 7.0倍／同じ点数を無作為に選んだ場合の期待PFS 56.4%（同じ13Rの実績 44.9%）／券種別 TRIO 65点 PFS 53.5%／WIDE 26点 PFS 23.5%／荒れ度（発走前・1番人気オッズ）MID 7R PFS 53.1% 的中赤字 1/2／SOLID 5R PFS 27.1% 的中赤字 2/2／UNKNOWN 1R PFS 77.1% 的中赤字 1/1／市場ミラーとの差 12R：実績 42.3% − ミラー 21.9% = Δ 20.4pt（95%区間 -19.3〜77.0、最高1R除き -5.2pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 0.0（13R）／組だけ的中（三連単は外れ）6R・着順まで的中 3R／的中 8R のうち的中赤字 8R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 35.4%（同じ13Rの実績 14.6%）／券種別 EXACTA 225点 PFS 28.9%／TRIFECTA 555点 PFS 8.8%／荒れ度（発走前・1番人気オッズ）MID 7R PFS 21.7% 的中赤字 5/5／SOLID 5R PFS 2.5% 的中赤字 2/2／UNKNOWN 1R PFS 25.5% 的中赤字 1/1／市場ミラーとの差 12R：実績 13.7% − ミラー 36.0% = Δ -22.2pt（95%区間 -54.2〜1.7、最高1R除き -24.3pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、13R×3券種）：購入 5／予算で削除 0／予想で除外 8／未生成・券種なし 26／役割馬の行き先 {'PURCHASED': 39}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、13R×3券種）：購入 10／予算で削除 4／予想で除外 12／未生成・券種なし 13／役割馬の行き先 {'PURCHASED': 96, 'BUDGET_COMPRESSED': 40}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 4R／W外 9R、2着が P2 役割 3R）：STATIC 3/4（平均1.25位）／STYLE_COND 3/4（平均1.25位） 救済0・喪失0／MARKET_COND 1/3（平均2.33位） 救済0・喪失1
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 6R／W外 7R、2着が P2 役割 6R）：STATIC 6/6（平均2.33位）／STYLE_COND 6/6（平均2.0位） 救済0・喪失0／MARKET_COND 5/5（平均2.0位） 救済0・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 8 | 36,600 | RECURRING |
| P1:ROLE_W_MISS | P1 | 7 | 37,500 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 13 | 66,600 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

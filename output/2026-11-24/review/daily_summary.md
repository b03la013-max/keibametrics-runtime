# 地方版 2026-11-24 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 17／PAPER PFS 61.6%／正式推薦 PFS 41.0%
- 第一失敗：{'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 6, 'PREDICTION_ROLE_P2': 3, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| MIZ | 7 | 0.0 | 36.6 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 1} |
| NGY | 3 | 85.2 | 7.2 | {'PREDICTION_ROLE_W': 3} |
| URW | 7 | 124.3 | 60.0 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 2, 'NONE': 1, 'PREDICTION_ROLE_P2': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 22／正式試行 22・発走前送信 22／本人確認 0
2. 計算完走：Full29 22／Signed FINAL 22／KRS5000 22／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 61.6%／正式推薦 41.0%／実購入なし
5. Learning：RESULT署名検証 17／学習状態保存 17／前Raceの学習状態を結合した正式Race 22（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '211/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 17 | 35.3% | 64.7% | 35.3% | 0.0% | 5.9% | 0.0% | 23.5% | 1.41 |
| 正式推薦 | 17 | 35.3% | 64.7% | 64.7% | 82.4% | 100.0% | 64.7% | 47.1% | 1.47 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中35.3%（無作為10.2%、差+25.1）／P2 平均1.0頭 的中0.0%（無作為10.2%、差-10.2）／P3 平均1.0頭 的中5.9%（無作為10.2%、差-4.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中64.7%（無作為30.6%、差+34.1）／P2 平均6.0頭 的中82.4%（無作為61.3%、差+21.1）／P3 平均10.12頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 11.82/40（選択性補正込み）・能力順位 13.78/20（17R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.87/40（選択性補正込み）・能力順位 12.81/20（17R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（4.7%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）5R・着順まで的中 0R／的中 5R のうち的中赤字 3R／損益分岐の倍率 平均 7.5倍／同じ点数を無作為に選んだ場合の期待PFS 39.4%（同じ17Rの実績 61.6%）／券種別 EXACTA 3点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 85点 PFS 76.6%／WIDE 32点 PFS 42.8%／荒れ度（発走前・1番人気オッズ）MID 6R PFS 56.7% 的中赤字 1/2／SOLID 11R PFS 64.0% 的中赤字 2/3／市場ミラーとの差 17R：実績 61.6% − ミラー 17.4% = Δ 44.1pt（95%区間 -14.6〜134.2、最高1R除き 6.7pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 38,300円（37.5%）／保護層の資金比率 0.0（17R）／組だけ的中（三連単は外れ）5R・着順まで的中 3R／的中 10R のうち的中赤字 7R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 32.0%（同じ17Rの実績 41.0%）／券種別 EXACTA 255点 PFS 66.9%／TRIFECTA 425点 PFS 16.7%／TRIO 340点 PFS 52.2%／荒れ度（発走前・1番人気オッズ）MID 6R PFS 41.2% 的中赤字 2/3／SOLID 11R PFS 41.0% 的中赤字 5/7／市場ミラーとの差 17R：実績 41.0% − ミラー 132.6% = Δ -91.6pt（95%区間 -208.1〜1.9、最高1R除き -77.5pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 7 | 25,430 | RECURRING |
| P1:ROLE_W_MISS | P1 | 6 | 28,710 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 17 | 67,430 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

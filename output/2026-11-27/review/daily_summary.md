# 地方版 2026-11-27 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 22／PAPER PFS 58.6%／正式推薦 PFS 50.9%
- 第一失敗：{'PREDICTION_ROLE_W': 10, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| NGY | 3 | 5.2 | 100.0 | {'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 1} |
| SON | 11 | 90.5 | 19.2 | {'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 3, 'PREDICTION_ROLE_P2': 1} |
| URW | 8 | 34.8 | 75.9 | {'PREDICTION_ROLE_W': 5, 'NONE': 2, 'CAPITAL_EFFICIENCY': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 27／正式試行 27・発走前送信 27／本人確認 0
2. 計算完走：Full29 27／Signed FINAL 27／KRS5000 27／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 58.6%／正式推薦 50.9%／実購入なし
5. Learning：RESULT署名検証 22／学習状態保存 22／前Raceの学習状態を結合した正式Race 27（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '300R到達', 'C14-FORMAL-P2BOX20-ONLY': '300R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '300R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '295/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 22 | 40.9% | 63.6% | 40.9% | 27.3% | 22.7% | 0.0% | 31.8% | 1.68 |
| 正式推薦 | 22 | 40.9% | 54.5% | 54.5% | 90.9% | 100.0% | 81.8% | 36.4% | 1.59 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中40.9%（無作為9.4%、差+31.5）／P2 平均1.0頭 的中27.3%（無作為9.4%、差+17.9）／P3 平均1.0頭 的中22.7%（無作為9.4%、差+13.4）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中54.5%（無作為28.1%、差+26.4）／P2 平均6.0頭 的中90.9%（無作為56.2%、差+34.7）／P3 平均10.91頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.5/40（選択性補正込み）・能力順位 14.85/20（22R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.36/40（選択性補正込み）・能力順位 14.75/20（22R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）7R・着順まで的中 0R／的中 9R のうち的中赤字 5R／損益分岐の倍率 平均 7.0倍／同じ点数を無作為に選んだ場合の期待PFS 45.6%（同じ22Rの実績 58.6%）／券種別 TRIO 110点 PFS 47.8%／WIDE 44点 PFS 85.7%／荒れ度（発走前・1番人気オッズ）MID 13R PFS 81.6% 的中赤字 1/5／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 7R PFS 21.6% 的中赤字 3/3／UNKNOWN 1R PFS 77.1% 的中赤字 1/1／市場ミラーとの差 21R：実績 57.8% − ミラー 40.3% = Δ 17.5pt（95%区間 -33.1〜76.9、最高1R除き -2.2pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 0.0（22R）／組だけ的中（三連単は外れ）6R・着順まで的中 8R／的中 13R のうち的中赤字 10R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 29.9%（同じ22Rの実績 50.9%）／券種別 EXACTA 390点 PFS 49.5%／TRIFECTA 930点 PFS 51.4%／荒れ度（発走前・1番人気オッズ）MID 13R PFS 60.1% 的中赤字 7/9／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 7R PFS 44.6% 的中赤字 2/3／UNKNOWN 1R PFS 25.5% 的中赤字 1/1／市場ミラーとの差 21R：実績 52.1% − ミラー 36.5% = Δ 15.5pt（95%区間 -28.0〜69.9、最高1R除き -2.6pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、22R×3券種）：購入 7／予算で削除 0／予想で除外 15／未生成・券種なし 44／役割馬の行き先 {'PURCHASED': 66}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、22R×3券種）：購入 20／予算で削除 4／予想で除外 20／未生成・券種なし 22／役割馬の行き先 {'BUDGET_COMPRESSED': 72, 'PURCHASED': 168}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 9R／W外 13R、2着が P2 役割 3R）：STATIC 3/9（平均2.22位）／STYLE_COND 4/9（平均2.11位） 救済1・喪失0／MARKET_COND 2/8（平均2.5位） 救済1・喪失1
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 12R／W外 10R、2着が P2 役割 10R）：STATIC 10/12（平均3.25位）／STYLE_COND 10/12（平均3.08位） 救済0・喪失0／MARKET_COND 11/11（平均2.55位） 救済2・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 10 | 49,500 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 10 | 42,260 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 22 | 96,260 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

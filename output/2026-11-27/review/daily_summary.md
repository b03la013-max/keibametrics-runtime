# 地方版 2026-11-27 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 27／PAPER PFS 65.0%／正式推薦 PFS 45.7%
- 第一失敗：{'PREDICTION_ROLE_W': 11, 'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| NGY | 5 | 6.6 | 78.8 | {'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 1, 'CAPITAL_EFFICIENCY': 2} |
| SON | 12 | 96.7 | 17.6 | {'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 1} |
| URW | 10 | 56.4 | 62.9 | {'PREDICTION_ROLE_W': 5, 'NONE': 2, 'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_P2': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 30／正式試行 30・発走前送信 30／本人確認 0
2. 計算完走：Full29 30／Signed FINAL 30／KRS5000 30／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 65.0%／正式推薦 45.7%／実購入なし
5. Learning：RESULT署名検証 27／学習状態保存 27／前Raceの学習状態を結合した正式Race 30（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '300R到達', 'C14-FORMAL-P2BOX20-ONLY': '300R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '300R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '300R到達', 'C17-P2-ZAI-PLACE': '300R到達', 'C18-W-PLUS-FAVORITE': '300R到達', 'C19-W-PLUS-TOP2-POP': '300R到達', 'C20-P2-PLUS-TOP3-POP': '300R到達', 'C21-BVI-L-R2-TERTILE': '295/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 27 | 44.4% | 70.4% | 44.4% | 25.9% | 22.2% | 0.0% | 29.6% | 1.74 |
| 正式推薦 | 27 | 37.0% | 59.3% | 59.3% | 88.9% | 100.0% | 81.5% | 33.3% | 1.56 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中44.4%（無作為9.2%、差+35.3）／P2 平均1.0頭 的中25.9%（無作為9.2%、差+16.7）／P3 平均1.0頭 的中22.2%（無作為9.2%、差+13.0）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中59.3%（無作為27.5%、差+31.7）／P2 平均6.0頭 的中88.9%（無作為55.1%、差+33.8）／P3 平均11.11頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 17.19/40（選択性補正込み）・能力順位 15.06/20（27R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.85/40（選択性補正込み）・能力順位 14.78/20（27R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）8R・着順まで的中 0R／的中 12R のうち的中赤字 6R／損益分岐の倍率 平均 7.1倍／同じ点数を無作為に選んだ場合の期待PFS 40.6%（同じ27Rの実績 65.0%）／券種別 TRIO 137点 PFS 45.3%／WIDE 54点 PFS 114.8%／荒れ度（発走前・1番人気オッズ）MID 16R PFS 93.8% 的中赤字 1/7／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 9R PFS 18.7% 的中赤字 4/4／UNKNOWN 1R PFS 77.1% 的中赤字 1/1／市場ミラーとの差 26R：実績 64.5% − ミラー 61.9% = Δ 2.6pt（95%区間 -52.9〜60.1、最高1R除き -13.6pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 0.0（27R）／組だけ的中（三連単は外れ）7R・着順まで的中 9R／的中 16R のうち的中赤字 13R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 27.3%（同じ27Rの実績 45.7%）／券種別 EXACTA 480点 PFS 47.4%／TRIFECTA 1140点 PFS 45.0%／荒れ度（発走前・1番人気オッズ）MID 16R PFS 50.2% 的中赤字 8/10／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 9R PFS 45.2% 的中赤字 4/5／UNKNOWN 1R PFS 25.5% 的中赤字 1/1／市場ミラーとの差 26R：実績 46.5% − ミラー 42.6% = Δ 3.9pt（95%区間 -34.8〜48.8、最高1R除き -11.1pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、27R×3券種）：購入 8／予算で削除 0／予想で除外 19／未生成・券種なし 54／役割馬の行き先 {'PURCHASED': 81}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、27R×3券種）：購入 24／予算で削除 6／予想で除外 24／未生成・券種なし 27／役割馬の行き先 {'BUDGET_COMPRESSED': 94, 'PURCHASED': 206}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 12R／W外 15R、2着が P2 役割 4R）：STATIC 4/12（平均2.67位）／STYLE_COND 5/12（平均2.5位） 救済1・喪失0／MARKET_COND 3/11（平均2.36位） 救済2・喪失2
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 16R／W外 11R、2着が P2 役割 13R）：STATIC 13/16（平均3.25位）／STYLE_COND 14/16（平均3.06位） 救済1・喪失0／MARKET_COND 15/15（平均2.6位） 救済3・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 13 | 53,320 | RECURRING |
| P1:ROLE_W_MISS | P1 | 11 | 55,500 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 27 | 119,320 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

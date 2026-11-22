# 中央版 指数の根拠台帳（2026-11-22）

本番の式・重み・券面は変更していない。根拠の段階：INITIAL_DESIGN＝初期値・要較正／KNOWN_RESULT_FIT＝過去データで合わせた／WALK_FORWARD＝時間順に分けて検証／FORWARD_OOS＝発走前凍結で比較済み。

## 基礎13指数

| 指数 | 中身 | 段階 | 観測重み 11/21 | 11/22 | 上位3頭平均順位（207R） |
|---|---|---|---|---|---|
| HPI | 能力（近走・クラス・相手） | INITIAL_DESIGN | 93% | 85% | 5.246 |
| SSI | スピード | INITIAL_DESIGN | 90% | 84% | 5.372 |
| CFI | コース・距離適性 | INITIAL_DESIGN | 70% | 68% | 5.929 |
| RFI | ローテ・状態 | INITIAL_DESIGN | 76% | 65% | 6.151 |
| BVI | 血統 | INITIAL_DESIGN | 95% | 94% | 6.641 |
| JTI | 騎手・調教師 | INITIAL_DESIGN | 53% | 53% | 5.156 |
| CSI | 厩舎の意図・仕上がり | INITIAL_DESIGN | 69% | 64% | 5.491 |
| TRI | 調教 | INITIAL_DESIGN | 65% | 65% | 5.976 |
| BWI | 馬体重・馬体・馬具 | INITIAL_DESIGN | 74% | 60% | 6.895 |
| GCI | 馬場・当日傾向 | INITIAL_DESIGN | 64% | 63% | 6.32 |
| PRI | 位置取り・展開 | INITIAL_DESIGN | 76% | 68% | 6.245 |
| KGI | 格・隠れた実力 | INITIAL_DESIGN | 90% | 88% | 5.291 |
| VMI | 市場・外部評価 | INITIAL_DESIGN | 82% | 71% | 4.586 |

## 派生7指数

| 指数 | 式 | 段階 | 上位3頭平均順位 |
|---|---|---|---|
| DCR | データの信頼度（6項目の点数） | INITIAL_DESIGN | 5.76 |
| TPI | 総合力：HPI.15 SSI.14 CFI.10 RFI.10 BVI.05 JTI.06 CSI.05 TRI.07 BWI.06 GCI.08 PRI.08 KGI.06、弱点減点 0.40×max(0,60−最弱)+0.20×max(0,65−2番目)、DCR係数で50へ縮める | INITIAL_DESIGN | 5.093 |
| ZAI_WIN | 勝ち指数。v1.0：HPI.20 SSI.17 CFI.10 RFI.08 JTI.05 CSI.05 TRI.05 BWI.05 GCI.08 PRI.12 KGI.05。v1.1（11/15〜）：v1.0×0.80＋BVI.15＋VMI.05。本番の順位はこれ | INITIAL_DESIGN（v1.1 は Owner 判断 11/14）＋FORWARD_OOS 進行中（ZAI-V11-VS-V10、11/21〜） | 5.081 |
| ZAI_PLACE | 複勝指数（同型、重み違い） | INITIAL_DESIGN | 5.082 |
| SRI | 安定度：ZAI_PLACE.45 TPI.25 RFI.10 PRI.08 KGI.07 BWI.05 | INITIAL_DESIGN | 5.176 |
| F3S | 最終3着内：ZAI_WIN.30 ZAI_PLACE.25 TPI.25 SRI.15 シナリオ.05 | INITIAL_DESIGN | 5.093 |
| T3I | 3着候補：ZAI_PLACE.35 TPI.20 RFI.15 PRI.10 GCI.08 CFI.07 VMI.05 | INITIAL_DESIGN | 5.166 |

## 変換と欠測

- 変換：特徴ごとに帯域（9段階）を付け、共通の点数表で数値化（INITIAL_DESIGN）。train 10/11-11/09 3,158頭：帯域が上がるほど3着内率が上がる（VERY_WEAK 6.5% → EXCEPTIONAL 35.6%、単調）。ただし market_mismatch（相関 -0.146）・opponent_strength（-0.048）・weight_load_fit（-0.007）は向きが逆か無関係
- 欠測：取れなかった特徴は除いて残りの重みで再正規化。指数ごとの最低被覆率（プロファイル別）を下回ると 50+(raw-50)×被覆率 に縮める（第3条 DCR）。京都11R（2026-11-22）で、情報不足が能力の減点として働いた例あり → 挑戦者 C2_UNCERT（PR #456）

## どこが一番弱いか

- data：index_analysis（207R・結果既知）、特徴の相関（train 3,158頭）、11/10以降97Rのリプレイ（参考値）
- 1_conversion：帯域→点数は全体として単調。逆向き・無関係の特徴が3つ（market_mismatch -0.146 が最大）
- 2_index_formula：基礎指数の上位3頭平均順位は JTI 5.16〜BWI 6.90。BVI 6.64（v1.1で重み.15）・GCI 6.32・PRI 6.24・RFI 6.15 が弱い
- 3_composite：ZAI_WIN 5.08 に対し VMI 単独 4.59、特徴では market_rank の相関 .378 が最大。合成が市場の情報を十分使えていない（約0.5順位の差）
- 4_role：本番の順位で勝ち馬が3位以内は約50%だが回収率は約31%。役割の挑戦者（P3_MARKET_TOP5 等、結果既知の参考値）で改善が大きい
- verdict：数字で一番弱いのは③合成（市場情報の使い方）と④役割。①変換は全体として機能しているが、向きの逆な特徴がある

## 今回登録した変換の挑戦者（記録のみ）

| 案 | 内容 | 11/10以降97R（参考値）上位3頭平均順位 | 上位5頭に入った3着内馬 |
|---|---|---|---|
| 本番 | — | 5.237 | 59.8% |
| CV1_SIGN_FIX | 逆向き3特徴を未観測扱い | 5.244 | 59.1% |
| CV2_ISO_SCALE | 共通点数表を引き直し | 5.289 | 59.1% |

どちらも参考値では本番を上回っていない。11/23 から発走前凍結で比べる。確率を出さないため Brier/LogLoss は対象外。

## 試したが登録しなかった案

- CV1 閾値 0.02（9特徴を除外）：同時評価の上限（段ごと最大2）のため。閾値0の版を代表に登録
- 特徴別の点数表（57特徴×9帯域）：自由度が大きく過学習の恐れ。共通表の再較正（CV2）を先に評価
- 市場重みを上げた ZAI：③合成段の案のため今回は対象外（jra_index_research の ZAI 枠と 11/27 の改善の仕組みで扱う）

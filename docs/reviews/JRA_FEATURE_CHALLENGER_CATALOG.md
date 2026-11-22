# 中央版 挑戦者特徴の一覧（収集資料・Drive精読 → 指数）

2026-11-22 時点。本番の重み・券面は変更しない（記録のみ）。11/22 の 312頭で本番の観測率が 0% だった特徴は12個。

## 接続済み（11/23 から発走前に凍結）
| 特徴 | 指数 | 収集元 | 挑戦者 |
|---|---|---|---|
| workout_load / workout_partner_level / workout_consistency | TRI・RFI・KGI | 競馬ブック調教（強弱・併せ・矢印） | CH_KB4 |
| stable_readiness | CSI・HPI・RFI | 競馬ブック攻め解説＋厩舎の話 | CH_KB4 |
| expert_support | VMI | TSL 推奨（軸・本線・次点・おさえ） | CH_EXPERT |
| body_condition_comment | BWI | 競馬ブック パドック評価 | CH_PADDOCK |
| equipment_effect | BWI | JRA公式 馬具申告（ブリンカー） | CH_EQUIP |
| （外国馬の分類・情報不足の扱い） | 全13 | JRA公式の過去成績 | C1_FOREIGN / C2_UNCERT（jra_info_gap_challenger） |

## まだ接続していない収集資料（予定）
| 資料 | 使い道 | 予定 |
|---|---|---|
| BB 深掘り（当日/前日/前週・コース・傾向・詳細・亀谷Point・コラム・ドル箱） | track_bias_fit・same_day_track_fit・sire 規則（D6） | 生データの帯域化ルールが要る。Drive J2（12/10）と統合 |
| TSL 得票率・異常/断層/拮抗・波乱度 | VMI 市場変化・荒れ易さ（STC） | J1/J2（12/03・12/10） |
| 競馬ブック 能力表・ポイント・対戦成績・TM直前情報 | forward_speed_comment（PRI・SSI）・opponent_strength | J2（12/10） |
| JRA 馬場情報（クッション値・含水率）・変更情報 | GCI・BVI ENV（q523） | J2（12/10） |
| JRA G1 プレレーティング | 能力水準（外国馬を含む） | 記録のみ（runtime/jra_prerating） |
| jockey_venue_fit・jockey_style_fit・trainer_jockey_fit | JTI | 騎手の場別・脚質別成績が必要 → E1 過去成績（11/25 着手）待ち |
| equipment_effect（初ブリンカー） | BWI | 前走の装着履歴が要る（今はブリンカー着用のみ） |
| weather_fit | GCI | 気象＋過去成績（E1 待ち） |

## Drive 精読の知見
中央版の Drive 精読（別タスク）の接続一覧は private repo の drive_reading/jra_connect.md（J1 役割・券面 12/03、J2 指数 12/10、J3 場別条項）。J2 の指数系の案は、この特徴型の挑戦者枠（runtime/analysis/jra_feature_challenger.py）に足していく。場別攻略条項（中京・札幌・函館・新潟・阪神・中山）は同じ場のレースにだけ適用する。

## A4（黙って失敗する計算の検出）
読み込み失敗・不明な場コード・発走時刻なし・本番再計算の不一致・発走前の取得に結果の注記（「(2着)」等）が混じる、をすべて ERROR として数え、凍結ファイルと監視の出力に「A4 ERROR n」を出す。

## 観測重みの表（毎開催日）
runtime/jra_feature_challenger/coverage_<date>.md。11/22（22R）：TRI 65%→98%、CSI 64%→94%、RFI 65%→87%、VMI 71%→84%、KGI 88%→98%、HPI 85%→89%、BWI 60%→62%。GCI 63%・CFI 69%・JTI 53%・PRI 69% は未接続のまま（E1 過去成績・BB 当日・JRA 馬場情報の接続待ち）。

## 有料情報の扱い
TSL 推奨・競馬ブック パドックの帯域は private repo にのみ保存（1対1で元の印を推定できる形を公開に出さない）。公開側は順位と件数のみ。

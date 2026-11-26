# KCP-JRA 現状監査と CAL-05 基準値（2026-11-26）

ChatGPT「KCP v1.0 三系統同時較正計画」の中央版担当分。Owner 承認 2026-11-26（KCP-C2 の記録登録）。本番影響なし。

## P0-01 現行KRSの棚卸し（中央版）
| 項目 | 現状 |
|---|---|
| Engine | KRS-Engine v1.1.0（SHA 9929df99…、外部実行、`runtime/jra_candidate_krs_plan.py` で照合） |
| parameter_map | 0.1-provisional（SHA 75cc9d0e…、**PROVISIONAL_UNCALIBRATED**）。地方版の 0.1-provisional（d8c027ee…）とは別物 |
| World | high_friction / leader_failure / leader_success / low_friction / natural の5つ |
| 出力 | 全馬の SSR-W・SSR-P2・SSR-P3・SSR-T3・LSR・Z4R・positions。署名済み FINAL に凍結 |
| 既存の評価 | `krs_oos_promotion_gate.py`（335R、役割提案の的中率 9.7%、自動昇格なし） |
| 使い方 | 影の計測のみ。Role・MEC・資金には使っていない |

## P0-02 データ
署名済み FINAL ＋ 公式結果がそろう 355R（2026-10-11〜11-23）。全レース同じ engine と parameter_map。
通過順・上がり・人気の過去データは公式結果の夜間収集（PR #496、入口の不具合を #502 で修正）で集め始める。

## CAL-05 現行誤差（勝率 SSR-W）
| | Brier | Log Loss/R | ECE |
|---|---|---|---|
| 現行 KRS（B1） | 0.0678 | 2.752 | 0.034 |
| 全頭同率（参照） | 0.0670 | 2.599 | 0 |

KRS が 50〜60% と出した馬の実際の勝率は 19%（31頭）、40〜50% は 25%（71頭）。**自信過剰で、確率としては全頭同率より悪い**。並び（勝ち馬の平均順位 4.92）は Static（4.83）とほぼ同じ。SSR-T3 も同じ方向（0.9 以上と出した馬の実際の3着内率は 64%）。

## KCP-C2（温度補正）
開催日 10/11〜11/07（209R）で T を決め（T=2.65）、11/08 以降の 146R に当てた結果：

| | Brier | Log Loss/R | ECE |
|---|---|---|---|
| B1 | 0.0654 | 2.923 | 0.034 |
| C2 | 0.0621 | **2.488** | **0.005** |
| 全頭同率 | 0.0643 | 2.651 | 0 |

対の差（C2−B1）−0.435、95%区間 [−0.656, −0.214]。補正後は全頭同率より良くなる。順位は変わらない（単調変換）ので Role・券面には影響しない。
11/28 以降の FINAL で前向きに記録（`profiles/KM_JRA_FORWARD_OOS_PREREG_20261128_KCP_C2.json`）。

## 次（未着手・要件）
- CAL-02（内部係数）：engine は外部実行。係数を変えた再実行には engine の研究用呼び出しと計算量の見積もりが必要。
- CAL-03（Stage）：通過順の実測が要る。夜間収集が動けば positions と照合できる。
- CAL-06（意思決定価値）：B0（Static のみ）と B1 の比較は `krs_oos_promotion_gate` が既に一部実施。同予算比較は未。

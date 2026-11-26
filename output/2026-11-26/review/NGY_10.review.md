# 2026-11-26 NGY_10 詳細反省（自動・実購入なし）

- 公式着順：5-4-6-3-2（上位3頭 [5, 4, 6]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 6／2着 2／3着 3；W False・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "NGY_10.r2", "ticket_sha256": "28f1a757afb8f49a713ac1a671d466b72697f406241ac918d5ec8ff4c9a6a7af", "frozen_at": "2026-11-26T18:55:06.366418+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 6／3着 2；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 10110／損益 4110／PFS 168.5%
- 参照：{"final_receipt_sha256": "e80f8dc9bb326e2fe5763f0e8c26176720159d73cdcd6e97178baba5b989900b", "result_receipt_sha256": "f1a5009ad7fe303621277b2c927850b4f7e03c8ff68a9a7c74f2acfa898ccc7e", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "ebdece45745ee73e68030b1a3401addcf0eff44bd3b860e63f865d06fe5973d4", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 8150, "pfs": 56.6}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T10:32:20.009633+00:00", "source_receipt_sha256": "7a59cd4124a317b2c1bce3c9d20fdb561319ee44c6b707a5c813c1cc06ae51d2", "signed_final_at": "2026-11-26T10:32:33.356054+00:00", "delivered_ticket_sha256": "2062ec74131725fb4c5fa9bf37f711bbe3e85d685acf52ddbdc564c130d41819", "settled_ticket_sha256": "e80f8dc9bb326e2fe5763f0e8c26176720159d73cdcd6e97178baba5b989900b"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 2, "HPI-L": 1}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 6, "third_pre_rank": 2, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [5, 4, 6], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P3_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | OK | {"pfs": 168.5, "profit_loss": 4110, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `571e19ce3a8da2f5`／Learning State `145d1b9df81a`</sub>

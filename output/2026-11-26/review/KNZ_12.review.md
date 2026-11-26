# 2026-11-26 KNZ_12 詳細反省（自動・実購入なし）

- 公式着順：5-1-6-10-8（上位3頭 [5, 1, 6]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 1／2着 8／3着 3；W True・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "KNZ_12.r2", "ticket_sha256": "2c397e4d0833558f75a1d5293a70ab1eb3becdd23aed6c5e1e7b5c780d365621", "frozen_at": "2026-11-26T19:50:12.954473+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 10／3着 2；W True・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "35e24a4deaa54eb418458953f23ec302c70d1aefed15721d549232036d485039", "result_receipt_sha256": "215e9b6e47fceb92a4217c830adab8dc7fbbdd0f049c6729ddd52bd6651880c1", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "c5ccabd9fd4ba939f83ec17103e537bf99efd01e18ae48830e9e50a838a5ff27", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 1160, "pfs": 8.8}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T11:26:22.066676+00:00", "source_receipt_sha256": "195775cec6f7cc86bab00424d39da8b658b854db0eb36b926badb1dae036b781", "signed_final_at": "2026-11-26T11:26:34.252419+00:00", "delivered_ticket_sha256": "03ee3dc3cd54c8001046a22146eb12c130545b6b73530855437dab724b03ea44", "settled_ticket_sha256": "35e24a4deaa54eb418458953f23ec302c70d1aefed15721d549232036d485039"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 2, "T3I-L": 3, "HPI-L": 3}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 1, "second_pre_rank": 10, "third_pre_rank": 2, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [5, 1, 6], "rescues": [], "supports": ["P3_ROLE_CONFIRMED"], "misses": [" |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 10} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `19f0163e3595e8d4`／Learning State `aead6afae5eb`</sub>

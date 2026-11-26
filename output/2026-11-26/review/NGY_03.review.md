# 2026-11-26 NGY_03 詳細反省（自動・実購入なし）

- 公式着順：9-7-12-10-5（上位3頭 [9, 7, 12]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 3／2着 4／3着 7；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "NGY_03.r2", "ticket_sha256": "77b11b117dbd2331191edc5cdc4a25561574324499e44c5d080f5a6b4182490b", "frozen_at": "2026-11-26T15:05:04.169618+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 3／3着 6；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 10760／損益 4760／PFS 179.3%
- 参照：{"final_receipt_sha256": "ab6d7e8e40e6264a81491153c8b817c9f9444dd54ad440b1c91515b77d752c85", "result_receipt_sha256": "737d8b35f0a0f0010abe239749964cd4733522abe29f26f4e169baaf2f326b4f", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "a12be57eb492548447a683b4a402a6ee43387b7683ef22ae09a1a6ccbf362624", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 18660, "pfs": 119.6}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T06:42:14.462126+00:00", "source_receipt_sha256": "dc5f3e5afcfd23313e2f8d8cc213bc9d26ce08e28eb6a343ed118a4de94360a7", "signed_final_at": "2026-11-26T06:42:28.396950+00:00", "delivered_ticket_sha256": "c604d987e65b66f3c4a91124c84745e681a13a28ba8839e65ae37ee09e0616ba", "settled_ticket_sha256": "ab6d7e8e40e6264a81491153c8b817c9f9444dd54ad440b1c91515b77d752c85"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 2, "T3I-L": 1, "HPI-L": 2}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 3, "third_pre_rank": 6, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [9, 7, 12], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | OK | {"pfs": 179.3, "profit_loss": 4760, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `d4bdba400ace21ff`／Learning State `8e0ba40e3dc1`</sub>

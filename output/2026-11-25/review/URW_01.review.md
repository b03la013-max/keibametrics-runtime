# 2026-11-25 URW_01 詳細反省（自動・実購入なし）

- 公式着順：9-3-11-5-8（上位3頭 [9, 3, 11]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 2／2着 9／3着 7；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "URW_01.r2", "ticket_sha256": "8d311de0f6239bbcffea98a1bb750a983338bf9519bbd50e012d7b0c28b6e4d7", "frozen_at": "2026-11-25T11:35:08.556225+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 5／3着 10；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 1760／損益 -4240／PFS 29.3%
- 参照：{"final_receipt_sha256": "515a19223c4f45ab64345b2e6fc3e920ca6935a70f5f907543c877d9e9036b8b", "result_receipt_sha256": "542dfe18c03a3de34539373b7c704cdf1dba329d989e5cac4d812df95fd80a47", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "5003aecdc2b6b501d490141896d1b80ad9597f760af4a774a079d9e9e9c22eeb", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 28360, "pfs": 181.8}, "effective_revision": "REVISION_2", "source_at": "2026-11-25T03:11:08.794306+00:00", "source_receipt_sha256": "6a75c5c9cb6e85ec65812ff711908d2f4cec1c08ea082a0ab4a805bfa401468c", "signed_final_at": "2026-11-25T03:11:21.237831+00:00", "delivered_ticket_sha256": "4a5c1933cea241ec902722819597d78fa8524f4eda9d6e2adc585c82840a8a60", "settled_ticket_sha256": "515a19223c4f45ab64345b2e6fc3e920ca6935a70f5f907543c877d9e9036b8b"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 2, "SRI-L": 1, "T3I-L": 2, "HPI-L": 1}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 5, "third_pre_rank": 10, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [9, 3, 11], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 29.3, "profit_loss": -4240, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 29.3, "tickets": 60, "payout": 1760} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `ef127aa4f5b3223e`／Learning State `7a72b118659c`</sub>

# 2026-11-26 KNZ_07 詳細反省（自動・実購入なし）

- 公式着順：4-6-7-9-3（上位3頭 [4, 6, 7]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 1／2着 2／3着 3；W True・P2 True・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 820／損益 120／PFS 117.1%
- 参照：{"revision": "KNZ_07.r2", "ticket_sha256": "bfbd8d31f711addb0e27855210c82433e733e5795779ed4ac6f7f3baa062cf07", "frozen_at": "2026-11-26T16:55:08.986823+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 3／3着 4；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 2330／損益 -3670／PFS 38.8%
- 参照：{"final_receipt_sha256": "57d39aa4e9d6c4233a52de9f552cb334b8acb51df9e0c42323b59bb44fa91e72", "result_receipt_sha256": "7867a308d7ece1a84d3f6a6239e5b9d919ed5785d541d215487d734d96e71a31", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "0f117e60abf2f12a1ddfd1a8f42855aeba37dfc4c6a487da2634f971cbfb92c8", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 1680, "pfs": 14.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-26T07:58:11.103911+00:00", "source_receipt_sha256": "551fdda9dc906a03240c31e2be60380c1291da3a6b81309eac18cd8092b2799f", "signed_final_at": "2026-11-26T07:58:21.754535+00:00", "delivered_ticket_sha256": "d5ffcefb2c54dee37e57cfe99c7dd9ccea096e038d59fa08b39d36f9e26c1bb1", "settled_ticket_sha256": "57d39aa4e9d6c4233a52de9f552cb334b8acb51df9e0c42323b59bb44fa91e72"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 1, "SRI-L": 2, "T3I-L": 3, "HPI-L": 5}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 3, "third_pre_rank": 4, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [4, 6, 7], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONF |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 38.8, "profit_loss": -3670, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 38.8, "tickets": 60, "payout": 2330} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `aef7543e0078d346`／Learning State `dd1760441ec1`</sub>

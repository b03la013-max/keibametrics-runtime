# 2026-11-26 URW_12 詳細反省（自動・実購入なし）

- 公式着順：7-3-10-2-4（上位3頭 [7, 3, 10]）
- 距離帯：MIDDLE(1701-2100)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 4／2着 1／3着 8；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "URW_12.r2", "ticket_sha256": "23a0351ac6fa53c0858cd5e70b303b620d03204507072890f98264e587f1693e", "frozen_at": "2026-11-26T17:35:11.571359+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 1／3着 3；W True・P2 True・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 1670／損益 -4330／PFS 27.8%
- 参照：{"final_receipt_sha256": "f127d4d4201e31e2b50e13c86c5462e10d09879b9e26c9d00c6dceefccd35fdc", "result_receipt_sha256": "a672d41d7eb84c74c485860a5f679d3547e350ac14c6825fb9d16c5ecfe7601a", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "04559fef691d8b8777dbd881b45ca04fac10a6ef9d3553f549123a0ee4c1b30b", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 4600, "pfs": 29.5}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T09:10:17.893194+00:00", "source_receipt_sha256": "3dc14908d44749d7893b578ec5f2fa19651fb8d2546f976e96b80911e697e057", "signed_final_at": "2026-11-26T09:10:30.662543+00:00", "delivered_ticket_sha256": "1643611cbf904040a067fa0e79862c9c2123e422dd64350d03e9a1eae2ba4bb9", "settled_ticket_sha256": "f127d4d4201e31e2b50e13c86c5462e10d09879b9e26c9d00c6dceefccd35fdc"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 2, "T3I-L": 3, "HPI-L": 2}, "ruled_neutral_share": 0.006} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 1, "third_pre_rank": 3, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [7, 3, 10], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 27.8, "profit_loss": -4330, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 27.8, "tickets": 60, "payout": 1670} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `bb6db71374553464`／Learning State `c2a5119965f5`</sub>

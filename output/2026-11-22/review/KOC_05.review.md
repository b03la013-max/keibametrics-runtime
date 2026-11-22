# 2026-11-22 KOC_05 詳細反省（自動・実購入なし）

- 公式着順：8-11-2-3-4（上位3頭 [8, 11, 2]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 2／2着 5／3着 3；W False・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "KOC_05.r2", "ticket_sha256": "9ae8cae9bdee1d38f36b84edfb1f8c0091f877a68c437df26acc621b2fff87e5", "frozen_at": "2026-11-22T17:00:09.967206+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 4／3着 2；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 3970／損益 -2030／PFS 66.2%
- 参照：{"final_receipt_sha256": "8e0151f320b7b4bb9dec1beb3db7c0af75fb729a46049d23322843da7d8b248b", "result_receipt_sha256": "e3cdd756ca3cf964352c800715af132e1124f12d8abcd1115e909f6aa5047aaa", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "cce44676aa3b227b3d861ee1ac0fe841271546598baa00480aadca9439e6d66e", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 7370, "pfs": 47.2}, "effective_revision": "REVISION_2", "source_at": "2026-11-22T08:36:18.506666+00:00", "source_receipt_sha256": "54579a8f48ba1e6b0d7790b4e85c5fc339260d3944f18d2a8c6343b89bfeadd9", "signed_final_at": "2026-11-22T08:36:30.843385+00:00", "delivered_ticket_sha256": "77d86802c527febec7672f9efe7c53007e24ba76c8deac1538754e0543c601de", "settled_ticket_sha256": "8e0151f320b7b4bb9dec1beb3db7c0af75fb729a46049d23322843da7d8b248b"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 2, "T3I-L": 4, "HPI-L": 2}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 3, "second_pre_rank": 4, "third_pre_rank": 2, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [8, 11, 2], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 66.2, "profit_loss": -2030, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 66.2, "tickets": 60, "payout": 3970} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `dafcb1bcbdc0f0c1`／Learning State `7665d22d8664`</sub>

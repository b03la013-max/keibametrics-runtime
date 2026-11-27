# 2026-11-27 NGY_05 詳細反省（自動・実購入なし）

- 公式着順：2-10-5-9-1（上位3頭 [2, 10, 5]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 1／2着 6／3着 11；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "NGY_05.r2", "ticket_sha256": "5f729bc8fc6338fbdaa09b54e66872b1ae40cc06afb33686091b62112e975a92", "frozen_at": "2026-11-27T16:15:04.434253+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 1／3着 12；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 1930／損益 -4070／PFS 32.2%
- 参照：{"final_receipt_sha256": "23f1d99386c51bc7757d0d6e3b621095874d28991b96313919c7590617bb6d6c", "result_receipt_sha256": "eb48da45946ef1cb87e49e38bf4882a457358fcaeeeaeb4e7913b11785a7328c", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "11c403014325451dcd99986558dcb899c5194fc38766578f9baac6e44faeaec0", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 2890, "pfs": 18.5}, "effective_revision": "REVISION_1", "source_at": "2026-11-27T07:18:06.540737+00:00", "source_receipt_sha256": "d840118d499ff00c2f2751f8fd98e526baad3fdf0bbf5abc3a56cad65dd14c99", "signed_final_at": "2026-11-27T07:18:18.926771+00:00", "delivered_ticket_sha256": "d39b2f1796e1ed1009355ca68b53758d807bb62944c69f198ef674907aaca1da", "settled_ticket_sha256": "23f1d99386c51bc7757d0d6e3b621095874d28991b96313919c7590617bb6d6c"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 3, "SRI-L": 2, "T3I-L": 7, "HPI-L": 6}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 3, "second_pre_rank": 1, "third_pre_rank": 12, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [2, 10, 5], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 32.2, "profit_loss": -4070, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 32.2, "tickets": 60, "payout": 1930} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `1f2bc64750385ecc`／Learning State `8eb37a7603d3`</sub>

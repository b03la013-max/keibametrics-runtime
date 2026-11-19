# 2026-11-19 KSM_04 詳細反省（自動・実購入なし）

- 公式着順：10-6-5-1-4（上位3頭 [10, 6, 5]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 8／2着 7／3着 9；W False・P2 False・P3 False
- Top3捕捉 0／Top4捕捉 0；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "KSM_04.r2", "ticket_sha256": "ef0d7c42f932a9b9d7595af99f7aa4e779b110647c63ceceac8fb3b8e10cb534", "frozen_at": "2026-11-19T11:10:13.185203+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 4／3着 1；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 586840／損益 580840／PFS 9780.7%
- 参照：{"final_receipt_sha256": "d3ca48548f71b6c448a4de910e9ca820bc3a6c6b0c06901f62f2f97b063a6ce8", "result_receipt_sha256": "d52ea991375eb83b4e3e1e42121ab23ffc31c69ee939997ed9e7c9953242a2b0", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "e3b63ffa45d15fff6be22032e769efb3000c248c56cb5765376017a8186f061e", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 586840, "pfs": 4445.8}, "effective_revision": "REVISION_2", "source_at": null, "signed_final_at": "2026-11-19T02:45:14.082027+00:00", "delivered_ticket_sha256": "575c1869d995387cff9111698e3060fa254b4d90414e021b76845b5da2731941", "settled_ticket_sha256": "d3ca48548f71b6c448a4de910e9ca820bc3a6c6b0c06901f62f2f97b063a6ce8"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 5, "TPI-L": 6, "SRI-L": 4, "T3I-L": 3, "HPI-L": 3}, "ruled_neutral_share": 0.117} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 4, "third_pre_rank": 1, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [10, 6, 5], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CON |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | OK | {"pfs": 9780.7, "profit_loss": 580840, "hit_but_loss": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `a1477b90c1da8eee`／Learning State `10c6ba4ec9d6`</sub>

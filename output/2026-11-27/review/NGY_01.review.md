# 2026-11-27 NGY_01 詳細反省（自動・実購入なし）

- 公式着順：4-11-12-9-5（上位3頭 [4, 11, 12]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 3／2着 1／3着 8；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "NGY_01.r2", "ticket_sha256": "91e61ba09ef2662a53dad351cfd11a78fd3df049eaa390a2376d8939da9aa537", "frozen_at": "2026-11-27T13:55:05.731052+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 4／2着 3／3着 2；W False・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 18000／損益 12000／PFS 300.0%
- 参照：{"final_receipt_sha256": "837510f0da570baa22730af2ce9f250ac8c5e0a2fa1922688c0418e9565a37c8", "result_receipt_sha256": "7784ac9501a9cd0b3b279a945e0d312a95c51eeb92930d6168329d925a2aaeed", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "c343286c77527d478a743d23ada469a1db2ebfaca65cbe9b1163aa8ac6508351", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-27T05:32:19.745204+00:00", "source_receipt_sha256": "548d2750bb257c9a173fc0071c62dded61ac9e85c3d31fa907dacf70a50e4353", "signed_final_at": "2026-11-27T05:32:31.955646+00:00", "delivered_ticket_sha256": "eb0589ce4c540e50c3fdab2f28b80f02e0c76768140e2e70f7aceede68f98044", "settled_ticket_sha256": "837510f0da570baa22730af2ce9f250ac8c5e0a2fa1922688c0418e9565a37c8"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 2, "T3I-L": 1, "HPI-L": 1}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 4, "second_pre_rank": 3, "third_pre_rank": 2, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [4, 11, 12], "rescues": ["WINNER_ROLE_RESCUE", "ORDERED_PAIR_RESCUE", "PA |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_cov |
| CAPITAL | OK | {"pfs": 300.0, "profit_loss": 12000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 4, "alternative_signals_that_had_winner_top": ["F3S-L ranked the winner #1", "TPI-L ranked the winne | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `eb13196ceb995212`／Learning State `515d18739a3f`</sub>

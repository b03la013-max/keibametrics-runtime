# 2026-11-22 MIZ_11 詳細反省（自動・実購入なし）

- 公式着順：9-8-2-4-3（上位3頭 [9, 8, 2]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 2／2着 9／3着 7；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "MIZ_11.r2", "ticket_sha256": "dc2596277696b2b1da21898b181a21f2672b376d0953191ef9335717fb89150a", "frozen_at": "2026-11-22T17:05:26.952210+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 8／3着 5；W True・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "9666694caee399f74336a9788b4dc82b14a048fe371a317869bf7e9a310d11a1", "result_receipt_sha256": "8976b5a99ea3a86e22fc4a2001d4becf17dfc252d1efe7882f6b1f9349ca4e12", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "f53500e9265783356d5f7712eb870915d1761229724f325f707c03b418dfb0c4", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-22T08:41:20.306509+00:00", "source_receipt_sha256": "1a33504bab6bd9da85a6b646da2a78cbd48d322cbdea9fa88a21e45a196372ca", "signed_final_at": "2026-11-22T08:41:32.158354+00:00", "delivered_ticket_sha256": "aa0cecf47686d3e94d461dc4cb68ccb250b1ea4108d2e8ee1e1e2849bd28fdac", "settled_ticket_sha256": "9666694caee399f74336a9788b4dc82b14a048fe371a317869bf7e9a310d11a1"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 2, "HPI-L": 1}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 1, "second_pre_rank": 8, "third_pre_rank": 5, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [9, 8, 2], "rescues": ["P2_ROLE_RESCUE", "ORDERED_PAIR_RESCUE", "PAIR_THI |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 8} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `cfc2bcc5d5b775ec`／Learning State `078b0ba4d014`</sub>

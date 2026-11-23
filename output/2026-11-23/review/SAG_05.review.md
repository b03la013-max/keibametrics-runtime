# 2026-11-23 SAG_05 詳細反省（自動・実購入なし）

- 公式着順：8-9-10-6-12（上位3頭 [8, 9, 10]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 1／2着 10／3着 2；W True・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 False；Pair条件付き3着 None
- 投資 1600／返還 0／払戻 0／損益 -1600／PFS 0.0%
- 参照：{"revision": "SAG_05.r2", "ticket_sha256": "52c3f2328f2e60e857f78cf79088207eb0dc3abcbc69224be0950db301ae3840", "frozen_at": "2026-11-23T16:50:07.527794+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 9／3着 4；W True・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "756679e5c0a48b0a0b2dbd0237024ab13082139dfb6f3940d16de3f14b563775", "result_receipt_sha256": "de2a3a882552f6ea3991f8f400068164599f784ddb6b2e1361d45da2a63621bd", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "ef0d1ac0b639442bb1587ce3b73df2ea248baccc65d165b7f248f7b2c8edb2de", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-23T07:53:35.991097+00:00", "source_receipt_sha256": "f952f6321b5f0dd7ae94edeee22335245d4b49d601cf1b7ed53f35daf2595b00", "signed_final_at": "2026-11-23T07:53:52.433552+00:00", "delivered_ticket_sha256": "62307a77d7585db170660ae10e2ab05dfc2560cacde4e593378aca2dd3b2491b", "settled_ticket_sha256": "756679e5c0a48b0a0b2dbd0237024ab13082139dfb6f3940d16de3f14b563775"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 3, "HPI-L": 1}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 1, "second_pre_rank": 9, "third_pre_rank": 4, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [8, 9, 10], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P3_ROLE |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 9} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `8e3f36eef706f494`／Learning State `799a8675995a`</sub>

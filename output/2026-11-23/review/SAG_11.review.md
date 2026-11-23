# 2026-11-23 SAG_11 詳細反省（自動・実購入なし）

- 公式着順：1-4-6-3-9（上位3頭 [1, 4, 6]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 1／2着 12／3着 5；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "SAG_11.r2", "ticket_sha256": "73fcb3c125374841f52be661a64943e2667b34e23c0931d86851180b66e117d0", "frozen_at": "2026-11-23T20:05:07.226926+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 9／3着 4；W True・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "c09191281147c5770a0dbaca40d8a86a5210c14a39c2a644cfbf2f7236aa42c0", "result_receipt_sha256": "f449ba868c94bc0bf9a3711b6dc7ec88553231d4995e515e003406ce1e44a6f8", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "a2b7ea3063a8ca786b2ce8c0fb5a9ce64692b68dee20a9280379f49340766b25", "signed_final_ticket_count": 180, "signed_final_total_investment": 18000, "signed_final_settlement": {"invest": 18000, "refund": 0, "effective_invest": 18000, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-23T11:41:12.273795+00:00", "source_receipt_sha256": "0fb08fd8eec0bf5ecf0abed94b374b1a0c4af54613a6badcbe2fafa8eb663f19", "signed_final_at": "2026-11-23T11:41:30.927977+00:00", "delivered_ticket_sha256": "e1f6c39f6e9ae49e4d62f3de16dfef7b6746b203123c0fdce218ca9d50ed84a9", "settled_ticket_sha256": "c09191281147c5770a0dbaca40d8a86a5210c14a39c2a644cfbf2f7236aa42c0"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 4, "HPI-L": 1}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 1, "second_pre_rank": 9, "third_pre_rank": 4, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [1, 4, 6], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P3_ROLE_ |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 9} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `d86b63d023475092`／Learning State `028703a3fab9`</sub>

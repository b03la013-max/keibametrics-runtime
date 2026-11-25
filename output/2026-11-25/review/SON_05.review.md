# 2026-11-25 SON_05 詳細反省（自動・実購入なし）

- 公式着順：3-2-6-8-5（上位3頭 [3, 2, 6]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 3／2着 2／3着 6；W False・P2 True・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 900／返還 0／払戻 0／損益 -900／PFS 0.0%
- 参照：{"revision": "SON_05.r2", "ticket_sha256": "77e22505005da91cefae280df4521778ba685f4c234746f273a495c4d6045a01", "frozen_at": "2026-11-25T12:00:06.574833+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 4／2着 6／3着 3；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 5480／損益 -520／PFS 91.3%
- 参照：{"final_receipt_sha256": "d21f70a1729c7128f875f443cac1da086db439f86e17c363627dda075522f577", "result_receipt_sha256": "6ac6d8e0f4cb5755bd76c22df9f301379060f1edfd147f324918e0f91b5e352a", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "3fffd9590e24eb3de7ac5ace5ad939942b6146bad115093906b2498d651c3555", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-25T03:38:09.666645+00:00", "source_receipt_sha256": "5f3fd078dc4753e97ca829a9a74f0f54cb34b966c871aa064f4415166d0cbcd0", "signed_final_at": "2026-11-25T03:38:22.075768+00:00", "delivered_ticket_sha256": "2c34e42f23cbedcfb3b9d79915e51a13caeefc1e224270de579913c326e91468", "settled_ticket_sha256": "d21f70a1729c7128f875f443cac1da086db439f86e17c363627dda075522f577"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 5, "TPI-L": 4, "SRI-L": 5, "T3I-L": 6, "HPI-L": 4}, "ruled_neutral_share": 0.003} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補5頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 4, "second_pre_rank": 6, "third_pre_rank": 3, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [3, 2, 6], "rescues": [], "supports": ["P3_ROLE_CONFIRMED"], "misses": [" |
| TICKET | OK | {"head_local_p2": null, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cov |
| CAPITAL | ISSUE | {"pfs": 91.3, "profit_loss": -520, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 4, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P1:HIT_BUT_LOSS | P1 | {"pfs": 91.3, "tickets": 60, "payout": 5480} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `087b89f1c7bbe611`／Learning State `8628435190c3`</sub>

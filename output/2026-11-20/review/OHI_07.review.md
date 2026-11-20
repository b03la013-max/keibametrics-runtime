# 2026-11-20 OHI_07 詳細反省（自動・実購入なし）

- 公式着順：4-8-3-2-5（上位3頭 [4, 8, 3]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 2／2着 1／3着 6；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 2250／損益 1550／PFS 321.4%
- 参照：{"revision": "OHI_07.r2", "ticket_sha256": "f583ee5d28f3951ccd47fce50dc7b49e4d7868df67cd14a8d2e9e6c37d62b17b", "frozen_at": "2026-11-20T17:01:24.345911+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 2／3着 4；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 15630／損益 9630／PFS 260.5%
- 参照：{"final_receipt_sha256": "7360e0f191c966bca58c960086a00f2483af078a93881203760be5c68dbb1ccc", "result_receipt_sha256": "3a26917ea8c0e7285a1c79f6589934a251cba9d2582bac0265d88bc6b44a8486", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "963f69ed5aa7da409e8f69d92fc56cb8b43ebdfc82956e7e9f3510b86389b7fd", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 15630, "pfs": 130.2}, "effective_revision": "REVISION_2", "source_at": "2026-11-20T08:37:48.571293+00:00", "source_receipt_sha256": "e7de84fb4b0f299571b2ea16714d0f701decca9b7f0f5d3d20ff99b0e614828e", "signed_final_at": "2026-11-20T08:37:56.276182+00:00", "delivered_ticket_sha256": "3dc4ea28a8b760e0476adee93f1e6d646b205525fd7456692f14991282722b92", "settled_ticket_sha256": "7360e0f191c966bca58c960086a00f2483af078a93881203760be5c68dbb1ccc"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 1, "T3I-L": 2, "HPI-L": 2}, "ruled_neutral_share": 0.107} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補5頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 2, "third_pre_rank": 4, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [4, 8, 3], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_CONFIRMED",  |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_cov |
| CAPITAL | OK | {"pfs": 260.5, "profit_loss": 9630, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `b28a3b8a0460fe17`／Learning State `341130f58bbf`</sub>

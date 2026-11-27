# 2026-11-27 URW_04 詳細反省（自動・実購入なし）

- 公式着順：11-13-10-2-7（上位3頭 [11, 13, 10]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 8／2着 2／3着 4；W False・P2 True・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "URW_04.r2", "ticket_sha256": "84ebeabdb6d289dc3295660d98b0bf44c7f2cf9bc4f13410a79cb6888db0999b", "frozen_at": "2026-11-27T13:05:06.311682+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 4／2着 2／3着 3；W False・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "bad8c1f978d3b5897ab7ab52d77b353d773dd2fdf47577cf2c21b5c7e2784632", "result_receipt_sha256": "5efcfd8c8caedbc1e31571b158a40f638af79c8542befd458c30fe0ab8873657", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "ec7d7184091866d46a090e884b5d58719bb702185c3cc6ca0dbdab4f7a2d2ea5", "signed_final_ticket_count": 168, "signed_final_total_investment": 16800, "signed_final_settlement": {"invest": 16800, "refund": 0, "effective_invest": 16800, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-27T04:07:31.988782+00:00", "source_receipt_sha256": "ff805e2fdea8e57461e360cf143cd510cfb6b28ca3d744ac85c3afbe76ebf0b2", "signed_final_at": "2026-11-27T04:07:45.274721+00:00", "delivered_ticket_sha256": "e44963198afe72a6e72b9bc9b91e53bda2309887f2c1e70c3aae8deed6e47863", "settled_ticket_sha256": "bad8c1f978d3b5897ab7ab52d77b353d773dd2fdf47577cf2c21b5c7e2784632"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 5, "TPI-L": 5, "SRI-L": 5, "T3I-L": 2, "HPI-L": 8}, "ruled_neutral_share": 0.003} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 4, "second_pre_rank": 2, "third_pre_rank": 3, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [11, 13, 10], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_C |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 4, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `7b4c65ed5606362a`／Learning State `7b0d0559fb6a`</sub>

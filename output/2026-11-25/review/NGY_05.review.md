# 2026-11-25 NGY_05 詳細反省（自動・実購入なし）

- 公式着順：4-11-12-9-1（上位3頭 [4, 11, 12]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 1／2着 9／3着 2；W True・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 190／損益 -510／PFS 27.1%
- 参照：{"revision": "NGY_05.r2", "ticket_sha256": "545b899bd8ae63971a7b4983602193534162afa15f6fd2c6ca2af832bb987116", "frozen_at": "2026-11-25T16:15:02.619932+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 8／3着 1；W True・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "7c7200dd5dc4a4dcd79ec062e9abd14be61eedcc29225646783c28fbac086ea0", "result_receipt_sha256": "2e65aa9acfef4bd0ec3be6bfeab58112faff07cd1da08b25f4ca9d132ebe840e", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "51466af4f86d44c9088b508c666746f5f8d3a8f72927fb12f48d3669a1ded44c", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-25T07:50:03.975810+00:00", "source_receipt_sha256": "f89da37fa02bb52db4b8b6bf7fbc645f50e896a25de3014b4e1c970b1fb8772b", "signed_final_at": "2026-11-25T07:50:16.217169+00:00", "delivered_ticket_sha256": "3a8f4569ccade7bd3b9d5612ce2944f54abb4c49a14f898bbec9231f34ed3914", "settled_ticket_sha256": "7c7200dd5dc4a4dcd79ec062e9abd14be61eedcc29225646783c28fbac086ea0"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 3, "SRI-L": 3, "T3I-L": 10, "HPI-L": 3}, "ruled_neutral_share": 0.072} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 2, "second_pre_rank": 8, "third_pre_rank": 1, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [4, 11, 12], "rescues": ["P2_ROLE_RESCUE", "ORDERED_PAIR_RESCUE", "PAIR_T |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 8} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `0b5f63bab6926e16`／Learning State `a9e17ec32935`</sub>

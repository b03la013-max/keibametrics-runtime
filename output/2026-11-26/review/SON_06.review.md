# 2026-11-26 SON_06 詳細反省（自動・実購入なし）

- 公式着順：1-10-9-3-4（上位3頭 [1, 10, 9]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 2／2着 1／3着 5；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 1600／返還 0／払戻 0／損益 -1600／PFS 0.0%
- 参照：{"revision": "SON_06.r2", "ticket_sha256": "480617ea684c91193e1deaf91354b077ef7e685ec0d2bca6f6f990552f4d1e2d", "frozen_at": "2026-11-26T12:35:05.837904+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 2／3着 3；W True・P2 True・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 5040／損益 -960／PFS 84.0%
- 参照：{"final_receipt_sha256": "36176bf22c562bc225d3fdb6da13b680679a3942f446e1a3b52936026e70c3f1", "result_receipt_sha256": "a79bd84dd31d03165503dbd22dc20ef7c0e2c0c447292363ec2710e13fb65c01", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "bfd725d5b96b3ad1dcc5e6c4e7ce553b1da488106bb298eb72820b512bd07f78", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 4720, "pfs": 30.3}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T04:11:13.142336+00:00", "source_receipt_sha256": "a20c2f9fcb2695b50cadfd80b96faef41126eadafa3408384762e5e5b1aaae3d", "signed_final_at": "2026-11-26T04:11:27.266383+00:00", "delivered_ticket_sha256": "79d6c8dbaca4b18e749048afdeefa1fdb3dfd024cb0f173fa25a1b86cb93ad46", "settled_ticket_sha256": "36176bf22c562bc225d3fdb6da13b680679a3942f446e1a3b52936026e70c3f1"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 1, "HPI-L": 1}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 2, "third_pre_rank": 3, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [1, 10, 9], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 84.0, "profit_loss": -960, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 84.0, "tickets": 60, "payout": 5040} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `943b49e00c625514`／Learning State `9269117c34c8`</sub>

# 2026-11-22 MIZ_05 詳細反省（自動・実購入なし）

- 公式着順：8-7-6-1-4（上位3頭 [8, 7, 6]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 3／2着 2／3着 4；W False・P2 True・P3 False
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "MIZ_05.r2", "ticket_sha256": "b156d791d0679eafab9712402cad3e5a63b6e29ecbf58ecad499590369135ae6", "frozen_at": "2026-11-22T13:30:05.410736+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 1／3着 4；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 2430／損益 -3570／PFS 40.5%
- 参照：{"final_receipt_sha256": "2be8eb21db57c206d47da8599bb8667bcb2a262929333fd906219b2172a7e555", "result_receipt_sha256": "7aa34c1f22d6659b71e5dfd0fa50e459e2cd6b4422e5384ef753c7350b71ff67", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "a4fc0951454aa9f8674ca185c737f4c51a26bcc9d74c88831a8e6c0d94aa240a", "signed_final_ticket_count": 105, "signed_final_total_investment": 10500, "signed_final_settlement": {"invest": 10500, "refund": 0, "effective_invest": 10500, "payout": 4820, "pfs": 45.9}, "effective_revision": "REVISION_2", "source_at": "2026-11-22T05:07:03.622366+00:00", "source_receipt_sha256": "d784cb478d0f3d8167b9709c00ab3d46d50854a209f03f7d2570d71da6665f25", "signed_final_at": "2026-11-22T05:07:14.378576+00:00", "delivered_ticket_sha256": "2506d2b6dee2ed747e3d041c214138713feaae675a109e76da552cec4a00de2d", "settled_ticket_sha256": "2be8eb21db57c206d47da8599bb8667bcb2a262929333fd906219b2172a7e555"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 3, "SRI-L": 2, "T3I-L": 4, "HPI-L": 3}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 3, "second_pre_rank": 1, "third_pre_rank": 4, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [8, 7, 6], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONFIRMED", "ORD |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 40.5, "profit_loss": -3570, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 40.5, "tickets": 60, "payout": 2430} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `65c2e38290a29bff`／Learning State `c340dc783b06`</sub>

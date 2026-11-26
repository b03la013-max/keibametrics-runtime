# 2026-11-26 SON_09 詳細反省（自動・実購入なし）

- 公式着順：3-4-10-7-8（上位3頭 [3, 4, 10]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 1／2着 3／3着 4；W True・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 1260／損益 560／PFS 180.0%
- 参照：{"revision": "SON_09.r2", "ticket_sha256": "84f0427ae920ec7b5a08d4ddbc656ff59704dbccc0cdac8727dbf06aaac6257f", "frozen_at": "2026-11-26T14:20:04.519960+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 2／3着 4；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 4700／損益 -1300／PFS 78.3%
- 参照：{"final_receipt_sha256": "d99d4d6cee76687887e4ef394f81bb3d81899796fa6105c4599107de665a9b15", "result_receipt_sha256": "0e15fed3dbae1d7121283c2c0074e1bd18739374c3e5c9ec62d28d754f1d4108", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "9ee3208db322c687cbde30b7bf8d0998e78b895f775de927e849a524d0f9be07", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 3440, "pfs": 23.9}, "effective_revision": "REVISION_1", "source_at": "2026-11-26T05:23:07.327748+00:00", "source_receipt_sha256": "68802b497f18e0db93706f9df452bcdd4b3dab1dd526a984acab385c7074034a", "signed_final_at": "2026-11-26T05:23:19.318270+00:00", "delivered_ticket_sha256": "573b771138497b81ac6169b71f9173fcd78dcc59f88515421571bb7233b7bdb8", "settled_ticket_sha256": "d99d4d6cee76687887e4ef394f81bb3d81899796fa6105c4599107de665a9b15"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 1, "HPI-L": 4}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 2, "third_pre_rank": 4, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [3, 4, 10], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_CONFIRMED", |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 78.3, "profit_loss": -1300, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 78.3, "tickets": 60, "payout": 4700} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `cb9b8eb8a21692dd`／Learning State `381bc694daa5`</sub>

# 2026-11-20 SON_01 詳細反省（自動・実購入なし）

- 公式着順：5-3-2-6-7（上位3頭 [5, 3, 2]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 1／2着 6／3着 8；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 False；Pair条件付き3着 None
- 投資 1600／返還 0／払戻 0／損益 -1600／PFS 0.0%
- 参照：{"revision": "SON_01.r2", "ticket_sha256": "025c233cecff11a03225f345b9d2c6ef7f110a2242e4dded625f535ab47bbc46", "frozen_at": "2026-11-20T09:56:31.052742+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 4／3着 7；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 760／損益 -5240／PFS 12.7%
- 参照：{"final_receipt_sha256": "c6dc96d85190a1f79c3cd74722de3a49de9726a1fd023679a05b760327eb074f", "result_receipt_sha256": "6d2a2df67a8b6e4fa067c8784c076216ada32d6c51dc95043bb03b667ee5d612", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "ba1880944065ed23c74d51e256b1b6de8c068676790bceaae7cfc7ebeb8fd59a", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 35430, "pfs": 268.4}, "effective_revision": "REVISION_2", "source_at": "2026-11-20T01:31:28.343950+00:00", "source_receipt_sha256": "4ae9bf6da651cf0fdca0fb401096779e4e737548112ffb544c20b683fa4706df", "signed_final_at": "2026-11-20T01:31:38.104094+00:00", "delivered_ticket_sha256": "cbd45903fbab010b9216a6a7f1372bfc1970ccc1b3954b5c6e359b1fe4144abe", "settled_ticket_sha256": "c6dc96d85190a1f79c3cd74722de3a49de9726a1fd023679a05b760327eb074f"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 5, "HPI-L": 1}, "ruled_neutral_share": 0.107} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 4, "third_pre_rank": 7, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [5, 3, 2], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_CONFIRMED",  |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 12.7, "profit_loss": -5240, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 12.7, "tickets": 60, "payout": 760} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `1243620bf98b30aa`／Learning State `ec33c8cbdc1d`</sub>

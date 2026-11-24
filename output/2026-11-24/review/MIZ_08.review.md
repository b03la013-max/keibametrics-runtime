# 2026-11-24 MIZ_08 詳細反省（自動・実購入なし）

- 公式着順：5-8-9-10-7（上位3頭 [5, 8, 9]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 2／2着 1／3着 5；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 1420／損益 720／PFS 202.9%
- 参照：{"revision": "MIZ_08.r2", "ticket_sha256": "c759945c6ca449ddaa787f5efff6f001d0eff88ab67e5080d88990d86b1f84e7", "frozen_at": "2026-11-24T15:00:50.393590+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 5／3着 2；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 2950／損益 -3050／PFS 49.2%
- 参照：{"final_receipt_sha256": "4ee787d31cf09bac5e37e35f40a461647abe9d749234c025b338460ad0cd7de4", "result_receipt_sha256": "473a09ed340f9eb38e67820c8725d2c7bc443c586ad5130b0ee18a93ea352fb7", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "a378352e773b201f9f84057fc8fed5e830c6224c9ff93db77033b8e49f3eed27", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 10430, "pfs": 79.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-24T06:37:35.176119+00:00", "source_receipt_sha256": "d3f5e1a19480368c4930851457456cf7dc9379d6c6f1fc0e6680b77e235da7eb", "signed_final_at": "2026-11-24T06:37:48.508880+00:00", "delivered_ticket_sha256": "123a4286c6a5b542113d454935510a59948e605ea9118ad622680f286bd6ceb5", "settled_ticket_sha256": "4ee787d31cf09bac5e37e35f40a461647abe9d749234c025b338460ad0cd7de4"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 3, "SRI-L": 1, "T3I-L": 4, "HPI-L": 2}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（エナジーイッセイ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 5, "third_pre_rank": 2, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [5, 8, 9], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 49.2, "profit_loss": -3050, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 49.2, "tickets": 60, "payout": 2950} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `1a8535deb955dcc7`／Learning State `6fbf1d455120`</sub>

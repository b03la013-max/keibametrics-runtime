# 2026-11-19 SON_12 詳細反省（自動・実購入なし）

- 公式着順：8-10-3-1-5（上位3頭 [8, 10, 3]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 1／2着 6／3着 4；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 False；Pair条件付き3着 None
- 投資 800／返還 0／払戻 340／損益 -460／PFS 42.5%
- 参照：{"revision": "SON_12.r2", "ticket_sha256": "e80847364431ebe2cd6343a1c4a2e00b72c146c042b268170a99e6c3b181e8e5", "frozen_at": "2026-11-19T15:46:18.540324+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 1／3着 8；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 2440／損益 -3560／PFS 40.7%
- 参照：{"final_receipt_sha256": "18f13ca0bee1640b9f3b073a40d11d272b872614b61f05deefc4280c213b2337", "result_receipt_sha256": "87257cc458e5712efe0c6c1f6481838e9fffedc5251107764553d13ef3af6a27", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "e1fb3f4505afa137622197a8a709a590f08971966acbb4aea24a02443ab00152", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 6610, "pfs": 42.4}, "effective_revision": "REVISION_2", "source_at": null, "signed_final_at": "2026-11-19T07:21:20.609589+00:00", "delivered_ticket_sha256": "9ded32df1f1edb6881ff5c3679ac6ab533d74f794cc6554c639342fa393dfec4", "settled_ticket_sha256": "18f13ca0bee1640b9f3b073a40d11d272b872614b61f05deefc4280c213b2337"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 4, "TPI-L": 3, "SRI-L": 4, "T3I-L": 7, "HPI-L": 3}, "ruled_neutral_share": 0.121} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 1, "third_pre_rank": 8, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [8, 10, 3], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_co |
| CAPITAL | ISSUE | {"pfs": 40.7, "profit_loss": -3560, "hit_but_loss": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 40.7, "tickets": 60, "payout": 2440} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `3e1e230d138c9265`／Learning State `63ed251cad53`</sub>

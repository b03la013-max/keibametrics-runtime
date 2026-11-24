# 2026-11-24 URW_05 詳細反省（自動・実購入なし）

- 公式着順：4-3-6-1-10（上位3頭 [4, 3, 6]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 2／2着 7／3着 5；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "URW_05.r2", "ticket_sha256": "389fc1ed75e189881739ee12dcfa5e0456c218a9b8479897cb68f1147af97f8f", "frozen_at": "2026-11-24T13:35:46.407446+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 5／2着 6／3着 3；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 8430／損益 2430／PFS 140.5%
- 参照：{"final_receipt_sha256": "b2a82e816250851236c2cc47f72b79da92ed93cf24b8d31ae249b27f4341c71d", "result_receipt_sha256": "c511d24b9ee275826989e9534e6a15ae1af9d843105a985ddc57b7edc96b16e7", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "e77abf951cde71c19ef8cada3da7090fad1d051ac61f4a5fbf39d918cde7138c", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-24T05:11:26.250493+00:00", "source_receipt_sha256": "dbc462e78afec2e8d942e5a9afec66cbe2674ec66d093a337ba5453ad3a041ba", "signed_final_at": "2026-11-24T05:11:41.349978+00:00", "delivered_ticket_sha256": "620b099e72175d7c38956d7d7ede95ccb92a9cad55d5a54defec970cbc80c911", "settled_ticket_sha256": "b2a82e816250851236c2cc47f72b79da92ed93cf24b8d31ae249b27f4341c71d"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 5, "TPI-L": 5, "SRI-L": 5, "T3I-L": 6, "HPI-L": 5}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補6頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 5, "second_pre_rank": 6, "third_pre_rank": 3, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [4, 3, 6], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONF |
| TICKET | OK | {"head_local_p2": null, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cov |
| CAPITAL | OK | {"pfs": 140.5, "profit_loss": 2430, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 5, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `78fcdb79dfbaa963`／Learning State `e1504539e310`</sub>

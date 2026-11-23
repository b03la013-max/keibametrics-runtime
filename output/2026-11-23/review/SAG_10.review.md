# 2026-11-23 SAG_10 詳細反省（自動・実購入なし）

- 公式着順：4-2-7-9-8（上位3頭 [4, 2, 7]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 3／2着 2／3着 5；W False・P2 True・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "SAG_10.r2", "ticket_sha256": "3233aaf437481de9753f40ffcf2f405587679a7089642e6e701ea26acccce0c3", "frozen_at": "2026-11-23T19:35:16.577390+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 10／2着 2／3着 1；W False・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "ef0f67d5e3037a52353ced4044c8da5b317205ce584ad2c273fe936007e5b2b6", "result_receipt_sha256": "9983458a97eccdf64631b2917db76f51ab9b5f531c7f671457c268c09232d305", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "b6345bbefc21b9bd41af2431a7217c54eee440bce602b0527e690036e007f51c", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 690, "pfs": 5.2}, "effective_revision": "REVISION_1", "source_at": "2026-11-23T10:39:48.769341+00:00", "source_receipt_sha256": "699e7b92bf7ff971c2dd89d3a3152beb407fa79753b1d382daf9b5b8f6a333de", "signed_final_at": "2026-11-23T10:40:02.820786+00:00", "delivered_ticket_sha256": "763e8f5289ecde2d209065b7f85338d1fa15bcc2818c4b922ebc87c7cf17e0ec", "settled_ticket_sha256": "ef0f67d5e3037a52353ced4044c8da5b317205ce584ad2c273fe936007e5b2b6"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 8, "TPI-L": 8, "SRI-L": 8, "T3I-L": 10, "HPI-L": 7}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（ラブミーテキーラ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 10, "second_pre_rank": 2, "third_pre_rank": 1, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [4, 2, 7], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONF |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 10, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `f740c656713864f1`／Learning State `f184754eaff6`</sub>

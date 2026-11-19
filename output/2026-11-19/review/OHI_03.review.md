# 2026-11-19 OHI_03 詳細反省（自動・実購入なし）

- 公式着順：1-3-7-5-6（上位3頭 [1, 3, 7]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 1／2着 4／3着 10；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 900／返還 0／払戻 0／損益 -900／PFS 0.0%
- 参照：{"revision": "OHI_03.r2", "ticket_sha256": "2cb93ade1ebc1fd0cf8b559e5b3099fc43dade99135229bc73f11b7bf6f5906a", "frozen_at": "2026-11-19T14:50:11.588023+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 3／3着 8；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 4310／損益 -1690／PFS 71.8%
- 参照：{"final_receipt_sha256": "f3a6f58658f339b06cd6a5d77de1c2a07ee2dcd72ec1f55bc7f641dc0b3e5edb", "result_receipt_sha256": "e5987c0245b54ae7f611c039f7b0b672ba55a07945a61552aee4d13fed1af769", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "83f3ce766e107ff2909d0d17b1f96262f36cf480de8f9bea57f61adbf7bf2294", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 35170, "pfs": 244.2}, "effective_revision": "REVISION_2", "source_at": null, "signed_final_at": "2026-11-19T06:25:37.354435+00:00", "delivered_ticket_sha256": "70a63929811d2b4d2e930e122439e8839fca752ce274bb5004ce009c6890a0f4", "settled_ticket_sha256": "f3a6f58658f339b06cd6a5d77de1c2a07ee2dcd72ec1f55bc7f641dc0b3e5edb"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 3, "SRI-L": 1, "T3I-L": 5, "HPI-L": 5}, "ruled_neutral_share": 0.129} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 3, "third_pre_rank": 8, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [1, 3, 7], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONF |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_co |
| CAPITAL | ISSUE | {"pfs": 71.8, "profit_loss": -1690, "hit_but_loss": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 71.8, "tickets": 60, "payout": 4310} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `63130c9f37330ec3`／Learning State `2cbbb7c426c3`</sub>

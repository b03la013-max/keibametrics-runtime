# 2026-11-24 MIZ_07 詳細反省（自動・実購入なし）

- 公式着順：5-7-6-3-10（上位3頭 [5, 7, 6]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 6／2着 3／3着 2；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "MIZ_07.r2", "ticket_sha256": "08556fe3a07a5b71be2205eac686390aa2b8e228a752d80b43ac55769377183b", "frozen_at": "2026-11-24T14:26:20.402668+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 2／3着 5；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 8210／損益 2210／PFS 136.8%
- 参照：{"final_receipt_sha256": "0876b7d96904aadcffce20694b4854764a95999c5c744b92e9ca32c177895533", "result_receipt_sha256": "1798a4daa1d66d90e92def15aeccd75346c09ef2e7d3a266a2a2f6b0041eef71", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "361f09d5260a95ed0671b898116d7c66be0a103672cd158507e13282a0f3be93", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 23700, "pfs": 197.5}, "effective_revision": "REVISION_2", "source_at": "2026-11-24T06:02:51.403451+00:00", "source_receipt_sha256": "0f4eceab4ab1bfa4f9b2681b6b9fdc6ae0186210c219609fc1bf71b869909968", "signed_final_at": "2026-11-24T06:03:04.509427+00:00", "delivered_ticket_sha256": "373e676a060dd884970b6f731a68b958a19d7697b257b5a146a1f4bb9be688ba", "settled_ticket_sha256": "0876b7d96904aadcffce20694b4854764a95999c5c744b92e9ca32c177895533"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 5, "TPI-L": 5, "SRI-L": 4, "T3I-L": 5, "HPI-L": 6}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（エムティリラ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 3, "second_pre_rank": 2, "third_pre_rank": 5, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [5, 7, 6], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONF |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | OK | {"pfs": 136.8, "profit_loss": 2210, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `58064f2998277c3a`／Learning State `f8e0792d067b`</sub>
